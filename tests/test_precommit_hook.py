import shutil
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / ".githooks" / "pre-commit"


def run(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    run(tmp_path, "init", "-q")
    run(tmp_path, "config", "user.name", "T")
    run(tmp_path, "config", "user.email", "t@example.com")
    run(tmp_path, "config", "commit.gpgsign", "false")
    hooks = tmp_path / ".githooks"
    hooks.mkdir()
    shutil.copy(HOOK, hooks / "pre-commit")
    run(tmp_path, "update-index", "--chmod=+x", "--add", ".githooks/pre-commit")
    run(tmp_path, "config", "core.hooksPath", ".githooks")
    return tmp_path


def commit(repo, names):
    for n in names:
        p = repo / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x\n")
        assert run(repo, "add", "--", n).returncode == 0
    return run(repo, "commit", "-m", "t").returncode


@pytest.mark.parametrize("names", [
    ["x.pdf"],
    ["docs/A.PDF"],
    ["data/x.csv"],
    ["data/sub/x"],
    ["my file.pdf"],
])
def test_refused(repo, names):
    assert commit(repo, names) != 0


@pytest.mark.parametrize("names", [
    ["data/x.ttl", "data/x.md", "data/x.py"],
    ["docs/note.md"],
])
def test_accepted(repo, names):
    assert commit(repo, names) == 0
