"""Shared test guard: no test may write the real plumb-line records (ADR-0006 R1).

An ingest with write=True and no ttl_out merges into plumb_merge.RECORDS and data/plumb-line.ttl.
Here RECORDS points at an empty tmp dir for every test, so such a call fails loud on the guard
(the real TTL is present and the records dir is empty) instead of writing a record. A test that
needs the real records names the path itself (REAL_RECORDS).
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REAL_RECORDS = ROOT / "docs" / "sittings" / "plumb-line"


@pytest.fixture(scope="session", autouse=True)
def _hold_shared_database():
    """ADR-0001 amendment 1: the session holds the shared database, so no other process can open it."""
    from goldenchain import dblock
    with dblock.hold("pytest session"):
        yield


@pytest.fixture(autouse=True)
def _no_real_plumb_records(tmp_path_factory, monkeypatch):
    for d in (ROOT / "tools", ROOT / "tools" / "console"):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    import plumb_merge
    assert plumb_merge.RECORDS == REAL_RECORDS
    monkeypatch.setattr(plumb_merge, "RECORDS", tmp_path_factory.mktemp("no-real-records"))
