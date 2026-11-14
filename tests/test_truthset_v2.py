"""Truth-set v2 draw: page- and slant-stratified, deterministic, no text (ruling on report 13, item 17)."""

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import truthset_v2 as T  # noqa: E402
from column_rule import Fail  # noqa: E402


def rows(page, n_sl, n_up, n_edge, n_small=0):
    out = []
    for kind, n in (("s", n_sl), ("u", n_up), ("e", n_edge), ("m", n_small)):
        for i in range(n):
            out.append({"key": f"{page}/left/1.1.{kind}.{i}", "page": page, "region": "left",
                        "slant": None if kind in "em" else (0.2 if kind == "s" else 0.0),
                        "abstain": {"e": "edge", "m": "small"}.get(kind),
                        "slanted": None if kind in "em" else kind == "s"})
    return out


def boxes(rs):
    return {r["key"]: [0, 0, 10, 10] for r in rs}


def test_strata_per_page_and_short_strata():
    rs = rows(1, 9, 9, 9, 3) + rows(2, 0, 9, 1)
    out = T.draw(rs, boxes(rs))
    by = {(r["page"], r["stratum"]): 0 for r in out}
    for r in out:
        by[(r["page"], r["stratum"])] += 1
    assert by == {(1, "slanted"): 4, (1, "upright"): 4, (1, "edge"): 2, (2, "upright"): 4, (2, "edge"): 1}
    assert all(r["signed_italic"] is None and "text" not in r for r in out)


def test_order_is_by_salted_hash_and_input_order_free():
    rs = rows(1, 9, 9, 9)
    a = T.draw(rs, boxes(rs))
    sh = rs[:]
    random.Random(3).shuffle(sh)
    assert T.draw(sh, boxes(rs)) == a
    assert T.digest(T.draw(sh, boxes(rs))) == T.digest(a)
    sl = sorted((r for r in rs if r["slanted"]), key=lambda r: T.order_key(r["key"]))[:4]
    assert [r["key"] for r in a if r["stratum"] == "slanted"] == [r["key"] for r in sl]


def test_fail_loud():
    rs = rows(1, 1, 1, 0)
    with pytest.raises(Fail):
        T.draw(rs, {})
    bad = rows(1, 1, 0, 0)
    bad[0]["slanted"] = None
    with pytest.raises(Fail):
        T.draw(bad, boxes(bad))
