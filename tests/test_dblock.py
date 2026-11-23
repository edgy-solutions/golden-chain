"""Born tests for ADR-0001 amendment 1 (AY1, AY2): the shared-database guard."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from goldenchain import dblock

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "fuseki" / "databases" / "gc"
TRIG = ROOT / "fuseki" / "run" / "gc.trig"

_CHILD = (
    "import sys\n"
    "from goldenchain import dblock\n"
    "try:\n"
    "    cm = dblock.hold('child', sys.argv[1]); cm.__enter__()\n"
    "except dblock.DatabaseBusy:\n"
    "    sys.exit(3)\n"
    "if len(sys.argv) > 2:\n"
    "    print('held', flush=True); sys.stdin.readline()\n"
)


def _env(**extra):
    return {**os.environ, "PYTHONPATH": str(ROOT), **extra}


def _run(lock, timeout=60):
    return subprocess.run([sys.executable, "-c", _CHILD, str(lock)], cwd=ROOT, env=_env(),
                          capture_output=True, text=True, timeout=timeout).returncode


def _snap():
    db = {}
    if DB.exists():
        for f in sorted(DB.rglob("*")):
            st = f.stat()
            db[f.relative_to(DB).as_posix()] = (st.st_size, st.st_mtime_ns)
    else:
        db = None
    trig = TRIG.stat() if TRIG.exists() else None
    return db, trig and (trig.st_size, trig.st_mtime_ns)


def test_ay1_busy_ingest_refused_and_database_untouched(tmp_path):
    data = tmp_path / "data"
    shutil.copytree(ROOT / "data", data)
    before = _snap()
    p = subprocess.run([sys.executable, "-m", "goldenchain.ingest"], cwd=ROOT,
                       env=_env(GOLDEN_CHAIN_DATA=str(data)), capture_output=True, text=True, timeout=300)
    assert p.returncode == 1
    assert "DatabaseBusy" in p.stderr
    assert _snap() == before


def test_ay2_nested_hold_and_release_on_outermost_exit(tmp_path):
    lock = tmp_path / "gc.lock"
    with dblock.hold("outer", lock):
        with dblock.hold("inner", lock):
            assert _run(lock) == 3
        assert _run(lock) == 3  # still held after inner exit
    assert _run(lock) == 0


def test_ay2_killed_holder_does_not_block(tmp_path):
    lock = tmp_path / "gc.lock"
    proc = subprocess.Popen([sys.executable, "-c", _CHILD, str(lock), "wait"], cwd=ROOT, env=_env(),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        assert proc.stdout.readline().strip() == "held"
        assert _run(lock) == 3
        proc.kill()
        proc.wait(timeout=30)
    finally:
        proc.kill()
        proc.wait(timeout=30)
        proc.stdin.close()
        proc.stdout.close()
    assert _run(lock) == 0
