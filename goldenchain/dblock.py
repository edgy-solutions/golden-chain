"""Shared-database guard (ADR-0001 amendment 1).

One TDB2 store is shared by ingest, the Fuseki server and the test suite. hold() takes a
non-blocking exclusive OS lock on fuseki/run/gc.lock; the OS drops it when the process dies.
Re-entrant within one process. A sidecar gc.lock.holder names the holder (pid, purpose, UTC start).
Does not import goldenchain.ingest (ingest imports this).
"""

import os
import sys
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

LOCK = Path(__file__).resolve().parent.parent / "fuseki" / "run" / "gc.lock"

if sys.platform == "win32":
    import msvcrt

    def _lock(fh):
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock(fh):
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _lock(fh):
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock(fh):
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


class DatabaseBusy(RuntimeError):
    pass


_mu = threading.Lock()
_held: dict[str, list] = {}  # key -> [handle, depth]


def _sidecar(path: Path) -> Path:
    return path.with_name(path.name + ".holder")


def _holder_text(path: Path) -> str:
    try:
        return _sidecar(path).read_text(encoding="utf-8").strip()
    except OSError:
        return "holder unknown"


@contextmanager
def hold(purpose: str, path=LOCK):
    path = Path(path)
    key = str(path.resolve())
    with _mu:
        entry = _held.get(key)
        if entry is not None:
            entry[1] += 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            fh = open(path, "a+b")
            try:
                fh.seek(0, os.SEEK_END)
                if fh.tell() == 0:
                    fh.write(b"\0")
                    fh.flush()
                _lock(fh)
            except OSError:
                fh.close()
                raise DatabaseBusy(
                    f"the shared database (fuseki/databases/gc) is in use: {_holder_text(path)} [lock {path}]"
                ) from None
            try:
                _sidecar(path).write_text(
                    f"pid={os.getpid()} purpose={purpose} "
                    f"started={datetime.now(timezone.utc).isoformat(timespec='seconds')}\n",
                    encoding="utf-8",
                )
            except OSError:
                pass
            _held[key] = [fh, 1]
    try:
        yield
    finally:
        with _mu:
            entry = _held[key]
            entry[1] -= 1
            if entry[1] == 0:
                del _held[key]
                try:
                    _sidecar(path).unlink()
                except OSError:
                    pass
                try:
                    _unlock(entry[0])
                finally:
                    entry[0].close()
