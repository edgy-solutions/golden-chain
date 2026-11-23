"""Born tests for the statements console kind (LOCK_statements_console T1-T4)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "console"))
sys.path.insert(0, str(ROOT / "tools" / "console" / "specs"))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import ingest  # noqa: E402
import statements as st  # noqa: E402
import test_console as tc  # noqa: E402
from build import Fail  # noqa: E402

CONTENT = ROOT / "docs" / "consoles" / "statements-1.json"
DATA = ROOT / "data"


@pytest.fixture
def images(tmp_path):
    d = tmp_path / "imgs"
    d.mkdir()
    for n, im in enumerate(json.loads(CONTENT.read_text(encoding="utf-8"))["images"]):
        tc.png(d / im["file"], 8, 4, shade=50 + n)
    return d


def content_with(tmp_path, mutate):
    c = json.loads(CONTENT.read_text(encoding="utf-8"))
    mutate(c)
    p = tmp_path / "content.json"
    p.write_text(json.dumps(c), encoding="utf-8")
    return p


def src(c, rel):
    return next(s for s in c["inclusion"]["sources"] if s["source"] == rel)


def test_statements_spec_on_the_real_content(images):
    spec = st.make_spec(CONTENT, DATA, images)
    secs = spec["sections"]
    assert spec["kind"] == "statements" and len(secs) == 3
    assert [len(s["rows"]) for s in secs] == [1, 1, 14]
    rows = [r for s in secs for r in s["rows"]]
    assert len(rows) == 16 and sum(len(r["fields"]) for r in rows) == 31
    assert len(spec["images"]) == 4
    for s in secs[:2]:
        f = s["rows"][0]["fields"]
        assert len(f) == 1 and f[0]["kind"] == "text" and "proposed" not in f[0]
    inc = secs[2]["rows"]
    prop = {r["id"]: r["fields"][0]["proposed"] for r in inc}
    assert sum(v == "include" for v in prop.values()) == 13
    assert [k for k, v in prop.items() if v == "not now"] == ["bsb-gill-1984"]
    gs = next(r for r in inc if r["id"] == "gospel-standard-1875")
    assert [f["id"] for f in gs["fields"]] == ["include", "reason", "witness-check"]
    assert len(gs["image_ids"]) == 4
    build.check_spec(spec)


@pytest.mark.parametrize("name,mutate", [
    ("unknown source", lambda c: src(c, "source/wcf").update(source="source/nope")),
    ("new but in data", lambda c: src(c, "source/wcf").update(new=True, label="x")),
    ("proposed on a statement", lambda c: c["statements"][0].update(proposed="x")),
    ("plumb-line listed", lambda c: c["inclusion"]["sources"].append(
        {**src(c, "source/wcf"), "source": "source/plumb-line"})),
    ("duplicate", lambda c: c["inclusion"]["sources"].append(dict(src(c, "source/wcf")))),
    ("proposed not in options", lambda c: src(c, "source/wcf").update(proposed="maybe")),
])
def test_statements_refusals(tmp_path, images, name, mutate):
    with pytest.raises(Fail):
        st.make_spec(content_with(tmp_path, mutate), DATA, images)


def test_statements_is_a_kind_and_writes_one_handoff_record():
    assert "statements" in build.KINDS and "statements" in ingest.KINDS
    b = "ab" * 32
    signed = {"kind": "statements", "build_hash": b, "export_sha256": "cd" * 32, "manifest_sha256": "ef" * 32,
              "signer": "Chris", "provisional": False, "signature": {"name": "Chris", "date": "2026-11-22"}, "rows": []}
    out = ingest.instance_output(signed, {"sections": [], "images": [], "title": "t"}, None)
    assert len(out) == 1
    path = Path(out[0][0])
    assert path.parent == ingest.HANDOFF and path.name == f"SIGNED_statements_{b[:16]}.md"


def test_statements_spec_builds(tmp_path, images, monkeypatch):
    spec = st.make_spec(CONTENT, DATA, images)
    p = tmp_path / "spec.json"
    build.write_spec(p, spec)
    monkeypatch.setattr(build, "git_state", lambda r: dict(tc.CLEAN))
    made = build.build(p, tmp_path / "out")
    assert made["manifest"].is_file()
