"""CCEL realignment of the OCR column words: hyphens joined, per page, block-move tolerant (O-3).

Usage: python tools/ccel_align.py <ocr-run-dir> <ccel-practical.txt> <out-dir>

Flags per OCR column word: agree / moved / differ / unaligned (None when empty after normalisation).
Pass A: a global in-order alignment fixes a CCEL window per page; each page is aligned in order inside
its window. Pass B: runs of non-agree words are matched against the whole chapter; matching blocks
mark the words "moved". Line-end hyphens are joined (across column and page ends too).
Outputs hold keys and flags only (no text) but describe the corpus: local only, never commit.
Prediction: ~/.golden-chain/o3-ccel-realign-predictions-locked.txt
"""

import argparse
import datetime
import difflib
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

MOVE_RUN = 8
MOVE_BLOCK = 6
PAD = 200
PCT = (5, 95)
MIN_ANCHORS = 20
PREDICTION = "~/.golden-chain/o3-ccel-realign-predictions-locked.txt"
FLAGS = ("agree", "moved", "differ", "unaligned")


def cmp_norm(t):
    return re.sub(r"[^0-9a-z]", "", t.lower())


def hyphen_join(tokens, line_end):
    joined, owner = [], []
    i, n = 0, len(tokens)
    while i < n:
        t = tokens[i]
        if line_end[i] and i + 1 < n and len(t) >= 2 and t.endswith("-") and t[-2].isalpha():
            joined.append(t[:-1] + tokens[i + 1])
            owner += [len(joined) - 1, len(joined) - 1]
            i += 2
        else:
            joined.append(t)
            owner.append(len(joined) - 1)
            i += 1
    return joined, owner


def align_in_order(a, b):
    """(flag, j) per a-token; j is the CCEL index for agree, else None."""
    kind = {"equal": "agree", "replace": "differ", "delete": "unaligned"}
    out = []
    for tag, i1, i2, j1, _j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag in kind:
            for k in range(i1, i2):
                out.append(("agree", j1 + (k - i1)) if tag == "equal" else (kind[tag], None))
    return out


def page_windows(pages_tokens, b):
    """pages_tokens: ordered list of (page, tokens). Returns {page: (lo, hi)}."""
    allt = [t for _p, toks in pages_tokens for t in toks]
    res = align_in_order(allt, b) if allt and b else []
    win, pos = {}, 0
    for p, toks in pages_tokens:
        js = [j for f, j in res[pos:pos + len(toks)] if f == "agree"]
        pos += len(toks)
        if len(js) >= MIN_ANCHORS:
            lo = max(0, math.floor(np.percentile(js, PCT[0])) - PAD)
            hi = min(len(b), math.ceil(np.percentile(js, PCT[1])) + PAD + 1)
            win[p] = (lo, hi)
        else:
            win[p] = None
    order = [p for p, _t in pages_tokens]
    prev_hi = None
    for k, p in enumerate(order):
        if win[p] is None:
            lo = 0 if prev_hi is None else max(0, prev_hi - PAD)
            nxt = next((win[q][0] for q in order[k + 1:] if win[q] is not None), None)
            hi = len(b) if nxt is None else min(len(b), nxt + PAD)
            win[p] = (lo, hi)
        prev_hi = win[p][1]
    return win


def moved_blocks(a, flags, b):
    """Marks matching blocks "moved" in flags (in place); returns [{"a_start", "a_len", "b_start"}]."""
    out = []
    n, i = len(a), 0
    while i < n:
        if flags[i] == "agree":
            i += 1
            continue
        j = i
        while j < n and flags[j] != "agree":
            j += 1
        if j - i >= MOVE_RUN:
            sm = difflib.SequenceMatcher(None, a[i:j], b, autojunk=False)
            for m in sm.get_matching_blocks():
                if m.size >= MOVE_BLOCK:
                    for k in range(i + m.a, i + m.a + m.size):
                        flags[k] = "moved"
                    out.append({"a_start": i + m.a, "a_len": m.size, "b_start": m.b})
        i = j
    return out


def align(pages, ccel_lines):
    # CCEL side
    ct, ce = [], []
    for line in ccel_lines:
        toks = line.split()
        ct += toks
        ce += [False] * (len(toks) - 1) + [True] if toks else []
    cj, _ = hyphen_join(ct, ce)
    b = [n for n in (cmp_norm(t) for t in cj) if n]
    # OCR side, joined across the whole column sequence
    seq = [(p, k, t, le) for p, ws in pages for (k, t, le) in ws]
    joined, owner = hyphen_join([s[2] for s in seq], [s[3] for s in seq])
    first, last, jpage = {}, {}, {}
    for i, o in enumerate(owner):
        first.setdefault(o, i)
        last[o] = i
        jpage.setdefault(o, seq[i][0])
    norm = [cmp_norm(t) for t in joined]
    jflag = [None] * len(joined)
    page_order = [p for p, _ws in pages]
    pidx = {p: [] for p in page_order}
    for o in range(len(joined)):
        if norm[o]:
            pidx[jpage[o]].append(o)
    ptoks = [(p, [norm[o] for o in pidx[p]]) for p in page_order]
    win = page_windows(ptoks, b)
    mblocks = []
    for p, toks in ptoks:
        lo, hi = win[p]
        if toks and hi > lo:
            fl = [f for f, _j in align_in_order(toks, [x for x in b[lo:hi]])]
        else:
            fl = ["unaligned"] * len(toks)
        for blk in moved_blocks(toks, fl, b):
            idx = pidx[p][blk["a_start"]:blk["a_start"] + blk["a_len"]]
            mblocks.append({"page": p, "first_key": seq[first[idx[0]]][1],
                            "last_key": seq[last[idx[-1]]][1],
                            "n_words": last[idx[-1]] - first[idx[0]] + 1,
                            "ccel_token_start": blk["b_start"], "ccel_token_len": blk["a_len"]})
        for o, f in zip(pidx[p], fl):
            jflag[o] = f
    flags = [jflag[o] for o in owner]
    per_page = {}
    for p in page_order:
        fs = [f for (pp, _k, _t, _l), f in zip(seq, flags) if pp == p]
        per_page[str(p)] = {"column_words": len(fs), **{k: fs.count(k) for k in FLAGS},
                            "none": fs.count(None), "window": list(win[p])}
    pairs = [o for o in set(owner) if last[o] != first[o]]
    report = {
        "pages": per_page, "moved_blocks": mblocks,
        "hyphen_pairs": len(pairs),
        "hyphen_pairs_agree_or_moved": sum(1 for o in pairs if jflag[o] in ("agree", "moved")),
        "totals": {"column_words": len(flags), **{k: flags.count(k) for k in FLAGS},
                   "none": flags.count(None)},
    }
    return flags, report


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(run_dir, ccel_path, out, ccel_sha=None, ccel_lines_range=None):
    import gy_ocr_baptism as O
    ccel_sha = ccel_sha or O.CCEL_SHA
    rng = ccel_lines_range or O.CCEL_LINES
    git_start = git_state(REPO)
    run_dir, out = Path(run_dir), Path(out)
    ocr_path = run_dir / "ocr.json"
    for f in (ocr_path, Path(ccel_path)):
        if not f.is_file():
            raise Fail(f"missing file: {f}")
    if sha256_file(ccel_path) != ccel_sha:
        raise Fail("CCEL file sha256 differs")
    ocr_sha = sha256_file(ocr_path)
    allw = json.loads(ocr_path.read_text(encoding="utf-8"))["words"]

    def ident(w):
        return (w["page"], w["region"], w["block"], w["par"], w["line"])

    rank = {"left": 0, "right": 1}
    col, by_page = [], {}
    for i, w in enumerate(allw):
        if w["region"] not in rank:
            continue
        le = i + 1 >= len(allw) or ident(allw[i + 1]) != ident(w)
        col.append(w)
        by_page.setdefault(w["page"], []).append((rank[w["region"]], i, w["key"], w["text"], le))
    pages = [(p, [(k, t, le) for _r, _i, k, t, le in sorted(by_page[p])]) for p in sorted(by_page)]
    lines = Path(ccel_path).read_text(encoding="utf-8", errors="replace").splitlines()
    flags, report = align(pages, lines[rng[0] - 1:rng[1]])
    order = [k for _p, ws in pages for k, _t, _l in ws]
    fmap = dict(zip(order, flags))
    cmp = {}
    for p, _ws in pages:
        n = sum(1 for w in col if w["page"] == p)
        old = sum(1 for w in col if w["page"] == p and w.get("ccel") == "agree")
        r = report["pages"][str(p)]
        cmp[str(p)] = {"column_words": n, "run1_agree_frac": round(old / n, 4) if n else None,
                       "run2_agree_or_moved_frac": round((r["agree"] + r["moved"]) / n, 4) if n else None}
    params = {"MOVE_RUN": MOVE_RUN, "MOVE_BLOCK": MOVE_BLOCK, "PAD": PAD, "PCT": list(PCT),
              "MIN_ANCHORS": MIN_ANCHORS}
    out.mkdir(parents=True, exist_ok=True)
    (out / "align.json").write_text(json.dumps(
        {"flags": fmap, "report": report, "run1_vs_run2": cmp, "params": params,
         "input": {"ocr_json_sha256": ocr_sha, "ccel_sha256": ccel_sha, "ccel_lines": list(rng)}},
        indent=1, sort_keys=True), encoding="utf-8")
    git_end = git_state(REPO)
    header = {"run": "ccel-align",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__), "golden_chain_git_start": git_start,
              "golden_chain_git_end": git_end, "clean_run": clean_run(git_start, git_end),
              "prediction": PREDICTION}
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8")
    (out / "README.txt").write_text(
        "LOCAL ONLY. align.json holds keys and flags only, but it describes corpus text. Never commit it.\n",
        encoding="utf-8")
    print(json.dumps(report["totals"]))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("run_dir")
    ap.add_argument("ccel")
    ap.add_argument("out")
    a = ap.parse_args()
    try:
        sys.exit(main(a.run_dir, a.ccel, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
