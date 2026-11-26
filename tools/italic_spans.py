"""Italic spans paired with Scripture references (LOCK_italic_spans_2026-11-22, item 7).

Usage: python tools/italic_spans.py <ocr-run-dir> <slant-run-dir> <out-dir>

Definitions in brief (the lock has them in full):
- Words: left and right regions only, in reading order (page, region, block, par, line, word).
  slanted / upright / abstain (row has abstain) / unmeasured (no slant row).
- Span: maximal run of words in one page and region where every measured word is slanted;
  unmeasured words between slanted words are bridges; leading/trailing unmeasured are trimmed;
  an upright or abstained word ends it. Edge = touches the region's first or last word.
- Reference: optional prefix (1, 2, i, ii), a book token (BOOKS, optional "."), a roman chapter
  and a digit token. Continuation: roman + digit with no book, starting within 6 words after a
  previous reference's end (start index - end index <= 6). "ver." forms are counted apart,
  never references.
- Pairing: a span takes the first reference that starts after its last word, in the same page and
  region, with at most 8 words between them, before the next span starts; one span per reference.
- A row with slanted None and no abstain is treated as abstained.

Outputs hold no word text; local only, never commit.
"""

import datetime
import hashlib
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import REPO, Fail, git_state  # noqa: E402

WINDOW = 8
CONTINUATION = 6
REGIONS = {"left": 0, "right": 1}
BOOKS = ("Gen Exod Lev Numb Num Deut Josh Judg Ruth Sam Kings Chron Ezra Neh Esth Job Psal Ps Prov "
         "Eccl Eccles Cant Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech "
         "Mal Matt Mark Luke John Acts Rom Cor Gal Eph Phil Col Thess Tim Tit Titus Philem Heb "
         "James Jam Pet Jude Rev").split()
BOOK_RE = re.compile(r"^(?:" + "|".join(BOOKS) + r")\.?$")
PREFIX_RE = re.compile(r"^(?:1|2|i|ii)\.?$")
ROMAN_RE = re.compile(r"^[ivxlc]+[.,;]?$")
DIGIT_RE = re.compile(r"^\d")
VER_RE = re.compile(r"^ver\.?$")
GC = "https://w3id.org/golden-chain/ontology#"
TTL = REPO / "data" / "gill-body-of-divinity.ttl"


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(ocr_dir, slant_dir):
    ocr_p, slant_p = Path(ocr_dir) / "ocr.json", Path(slant_dir) / "slant.json"
    for p in (ocr_p, slant_p):
        if not p.is_file():
            raise Fail(f"missing {p}")
    slant = json.loads(slant_p.read_text(encoding="utf-8"))
    want = slant.get("input", {}).get("ocr_json_sha256")
    got = sha256_file(ocr_p)
    if want != got:
        raise Fail("slant.json input.ocr_json_sha256 does not match sha256 of ocr.json")
    ocr = json.loads(ocr_p.read_text(encoding="utf-8"))
    return ocr, slant, got, sha256_file(slant_p)


def classify(row):
    if row is None:
        return "unmeasured"
    if row.get("abstain") is not None:
        return "abstain"
    if row.get("slanted") is True:
        return "slanted"
    if row.get("slanted") is False:
        return "upright"
    return "abstain"


def region_lists(ocr, slant):
    rows = {r["key"]: r for r in slant["rows"]}
    groups = {}
    for w in ocr["words"]:
        if w.get("region") in REGIONS:
            groups.setdefault((w["page"], w["region"]), []).append(w)
    out = []
    for (page, region), ws in sorted(groups.items(), key=lambda kv: (kv[0][0], REGIONS[kv[0][1]])):
        ws.sort(key=lambda w: (w["block"], w["par"], w["line"], w["word"]))
        out.append((page, region, ws, [classify(rows.get(w["key"])) for w in ws]))
    return out


def find_spans(states):
    """[(first, last)] index pairs, trimmed, over one region's states."""
    spans, i, n = [], 0, len(states)
    while i < n:
        if states[i] != "slanted":
            i += 1
            continue
        j = i
        k = i + 1
        while k < n and states[k] in ("slanted", "unmeasured"):
            if states[k] == "slanted":
                j = k
            k += 1
        spans.append((i, j))
        i = k
    return spans


def find_refs(texts):
    """[(start, end, kind)] over one region's word texts."""
    refs, i, n, last_end = [], 0, len(texts), None
    while i < n:
        t = texts[i]
        if BOOK_RE.match(t) and i + 2 < n and ROMAN_RE.match(texts[i + 1]) and DIGIT_RE.match(texts[i + 2]):
            start = i - 1 if i > 0 and PREFIX_RE.match(texts[i - 1]) else i
            if refs and start <= refs[-1][1]:
                start = i
            refs.append((start, i + 2, "book"))
            last_end, i = i + 2, i + 3
        elif (ROMAN_RE.match(t) and i + 1 < n and DIGIT_RE.match(texts[i + 1])
              and last_end is not None and i - last_end <= CONTINUATION):
            refs.append((i, i + 1, "continuation"))
            last_end, i = i + 1, i + 2
        else:
            i += 1
    return refs


def pair(spans, refs):
    """paired ref index (or None) per span; one span per reference."""
    claimed, out = set(), []
    for si, (_first, last) in enumerate(spans):
        nxt = spans[si + 1][0] if si + 1 < len(spans) else None
        hit = None
        for ri, (rs, _re, _k) in enumerate(refs):
            if ri in claimed or rs <= last or rs - last - 1 > WINDOW:
                continue
            if nxt is not None and rs >= nxt:
                continue
            hit = ri
            break
        if hit is not None:
            claimed.add(hit)
        out.append(hit)
    return out


@lru_cache(maxsize=1)
def hand_minted():
    from rdflib import Graph, URIRef
    g = Graph()
    g.parse(TTL, format="turtle")
    cites, pages, loc = URIRef(GC + "cites"), URIRef(GC + "pages"), URIRef(GC + "locator")
    out = {}
    for arg in set(g.subjects(cites, None)):
        if "/practical/3/1/" not in str(arg):
            continue
        pg = str(next(g.objects(arg, pages))).split("-")[0].strip()
        # a printed reference counts once, however many Positions its Arguments support (Batch C adds a
        # second Argument on Sixthly 1-4 for baptism-instrumentality)
        locator = str(next(g.objects(arg, loc), ""))
        out.setdefault(pg, set()).update((locator, str(c)) for c in g.objects(arg, cites))
    return {pg: len(v) for pg, v in sorted(out.items())}


def build(ocr, slant):
    spans_out, refs_out = [], []
    by_page = {}
    for page, region, ws, states in region_lists(ocr, slant):
        keys = [w["key"] for w in ws]
        texts = [w.get("text") or "" for w in ws]
        pg = by_page.setdefault(str(page), dict(measured=0, slanted=0, spans=0, paired=0, unpaired=0,
                                                refs=0, ver_forms=0, edge_spans=0))
        pg["measured"] += sum(1 for s in states if s in ("slanted", "upright"))
        pg["slanted"] += states.count("slanted")
        pg["ver_forms"] += sum(1 for t in texts if VER_RE.match(t))
        spans, refs = find_spans(states), find_refs(texts)
        pg["refs"] += len(refs)
        paired = pair(spans, refs)
        for (first, last), p in zip(spans, paired):
            edge = first == 0 or last == len(ws) - 1
            seg = states[first:last + 1]
            spans_out.append({"page": page, "region": region, "first_key": keys[first],
                              "last_key": keys[last], "n_words": last - first + 1,
                              "n_slanted": seg.count("slanted"), "n_bridged": seg.count("unmeasured"),
                              "edge": edge, "paired_ref_key": keys[refs[p][0]] if p is not None else None})
            pg["spans"] += 1
            pg["edge_spans"] += edge
            pg["paired" if p is not None else "unpaired"] += 1
        for rs, _e, kind in refs:
            refs_out.append({"page": page, "region": region, "key": keys[rs], "kind": kind})
    totals = {k: sum(v[k] for v in by_page.values()) for k in
              ("measured", "slanted", "spans", "paired", "unpaired", "refs", "ver_forms", "edge_spans")}
    return spans_out, refs_out, by_page, totals


def dump(obj):
    return json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False)


def main(ocr_dir, slant_dir, out_dir):
    out = Path(out_dir)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise Fail(f"out-dir exists and is not empty: {out}")
    ocr, slant, ocr_sha, slant_sha = load(ocr_dir, slant_dir)
    spans, refs, by_page, totals = build(ocr, slant)
    inp = {"ocr_json_sha256": ocr_sha, "slant_json_sha256": slant_sha}
    params = {"window": WINDOW, "continuation": CONTINUATION, "books": BOOKS}
    summary = {"by_page": by_page, "totals": totals, "hand_minted": hand_minted()}
    out.mkdir(parents=True, exist_ok=True)
    (out / "spans.json").write_text(dump({"input": inp, "params": params, "spans": spans, "refs": refs}),
                                    encoding="utf-8", newline="\n")
    (out / "summary.json").write_text(dump(summary), encoding="utf-8", newline="\n")
    header = {"run": "italic-spans",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "input": inp, "params": params, "git_state": git_state(REPO)}
    (out / "run_header.json").write_text(dump(header), encoding="utf-8", newline="\n")
    print(dump(totals))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    try:
        main(*sys.argv[1:])
    except Fail as e:
        sys.exit(f"FAIL: {e}")
