"""Born test for the statements console's second content file (LOCK_statements2_2026-11-26 S1, S2)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "console"))
sys.path.insert(0, str(ROOT / "tools" / "console" / "specs"))
sys.path.insert(0, str(ROOT / "tools"))
import statements as st  # noqa: E402
import test_console as tc  # noqa: E402

ONE = ROOT / "docs" / "consoles" / "statements-1.json"
TWO = ROOT / "docs" / "consoles" / "statements-2.json"
LABEL = ("If included, it is labelled: short extracts only; written confirmation to be sought before launch "
         "(architect, ruling on report 28).")


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def test_s1_differs_only_on_the_bsb_row_and_the_harbaugh_row():
    one, two = load(ONE), load(TWO)
    rows1, rows2 = one["inclusion"]["sources"], two["inclusion"]["sources"]
    added = [r for r in rows2 if r["source"] == "source/heidelberg-harbaugh"]
    assert len(added) == 1 and added[0]["proposed"] == "include" and "new" not in added[0]
    order = [r["source"] for r in rows2]
    assert order.index("source/heidelberg-harbaugh") == order.index("source/belgic-confession") + 1
    rest = [r for r in rows2 if r["source"] != "source/heidelberg-harbaugh"]
    assert [r["source"] for r in rest] == [r["source"] for r in rows1]
    for a, b in zip(rows1, rest):
        if a["source"] != "source/bsb-gill-1984":
            assert a == b
            continue
        assert a["proposed"] == "not now" and b["proposed"] == "include"
        assert b["status"] == a["status"] + " " + LABEL
        assert {k: v for k, v in a.items() if k not in ("proposed", "status")} == \
               {k: v for k, v in b.items() if k not in ("proposed", "status")}
    strip = lambda d: {k: ({kk: vv for kk, vv in v.items() if kk != "sources"} if k == "inclusion" else v)
                       for k, v in d.items()}
    assert strip(one) == strip(two)


def test_s2_the_builder_accepts_it_on_the_real_data(tmp_path):
    d = tmp_path / "imgs"
    d.mkdir()
    for n, im in enumerate(load(TWO)["images"]):
        tc.png(d / im["file"], 8, 4, shade=50 + n)
    spec = st.make_spec(str(TWO), str(ROOT / "data"), str(d))
    rows = [r for s in spec["sections"] for r in s["rows"]]
    assert any("heidelberg-harbaugh" in json.dumps(r) for r in rows)
