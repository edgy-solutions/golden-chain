"""The frozen fixture is byte-identical to data/ at 8ac7e41 (LOCK_frozen_fixture_eight)."""

import subprocess
from pathlib import Path

from gcfix import FROZEN_8AC7E41

REPO = Path(__file__).resolve().parent.parent


def test_frozen_fixture_matches_8ac7e41():
    names = subprocess.check_output(
        ["git", "ls-tree", "--name-only", "8ac7e41", "data/"], cwd=REPO, text=True).split()
    expected = {Path(n).name for n in names if n.endswith(".ttl")}
    found = {p.name for p in FROZEN_8AC7E41.glob("*.ttl")}
    assert found == expected
    for name in sorted(found):
        original = subprocess.check_output(["git", "show", "8ac7e41:data/" + name], cwd=REPO)
        assert (FROZEN_8AC7E41 / name).read_bytes() == original, name
