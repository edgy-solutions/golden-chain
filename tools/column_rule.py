"""Measure the printed inter-column rule and gutter on Gill BSB/Tegg pages.

A measurement on pixels, not an OCR step: it reads only the page's single
embedded 1-bit image, never a text layer. Method (fixed on p. 183, outside
the measured set, before the run):

1. Native bitmap of the page's one image object; ink = value > 127
   (this scan decodes paper as 0). Fail loud on any other page structure,
   on ink in the 50-px border, or on an implausible ink fraction.
2. Slabs of R = 400 rows; search band x in [0.35 W, 0.65 W].
3. Per slab, per column, the ink fraction f. Rule threshold T is the
   mode-midpoint of the page's histogram of nonzero f (20 bins): the
   midpoint between the low (text) mode and the high mode. A page with no
   high mode separated by a valley is unimodal: no rule detected.
4. Rule columns: f >= T. Clusters of rule columns (merged across <= 1 px)
   give the rule count per slab: 1 single, 2 double.
5. Gutter per two-column slab: the zero-ink run left of the rule, the rule
   width (contiguous nonzero columns round the cluster), the zero-ink run
   right of it; without a rule, the longest zero-ink run in the band.
6. Coverage = rule-bearing slabs / two-column slabs. A page carries a rule
   iff coverage >= 0.5 (a column rule runs the text height; less is a
   fragment). Any page under 0.9 is flagged for a human look.

Usage: python -I tools/column_rule.py <pdf> <first> <last> <out_dir>
(printed page numbers; PDF page = printed + 53). Needs numpy, pypdfium2.
"""
import datetime
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

import numpy as np
import pypdfium2 as pdfium
import pypdfium2.raw as raw

OFFSET = 53
R = 400
BAND = (0.35, 0.65)
LEFT_TEXT = (0.15, 0.45)
RIGHT_TEXT = (0.55, 0.85)
BINS = 20
DPI = 850
PT = 72 / DPI


class Fail(Exception):
    pass


def bitmap(pdf, printed):
    pg = pdf[printed + OFFSET - 1]
    objs = list(pg.get_objects())
    imgs = [o for o in objs if o.type == raw.FPDF_PAGEOBJ_IMAGE]
    if len(objs) != 1 or len(imgs) != 1:
        raise Fail(f"p.{printed}: expected one image object, got {len(objs)} objects")
    m = imgs[0].get_metadata()
    if (m.width, m.height, m.bits_per_pixel) != (5100, 7650, 1):
        raise Fail(f"p.{printed}: image {m.width}x{m.height} {m.bits_per_pixel}bpp")
    ink = np.asarray(imgs[0].get_bitmap(render=False).to_pil().convert("L")) > 127
    border = np.concatenate([ink[:50].ravel(), ink[-50:].ravel(),
                             ink[:, :50].ravel(), ink[:, -50:].ravel()]).mean()
    if border > 0.001 or not 0.02 < ink.mean() < 0.4:
        raise Fail(f"p.{printed}: polarity/crop check: border {border:.4f}, ink {ink.mean():.4f}")
    return ink


def mode_midpoint(f):
    h, edges = np.histogram(f[f > 0], bins=BINS, range=(0, 1))
    centers = (edges[:-1] + edges[1:]) / 2
    lo = int(np.argmax(h[: BINS // 2]))
    # The high mode is a local maximum, not the upper half's argmax: the text
    # tail can outweigh the rule bin at the half's edge (run 1, pp. 897/898/902).
    peaks = [i for i in range(BINS // 2, BINS)
             if h[i] > h[i - 1] and (i == BINS - 1 or h[i] >= h[i + 1])]
    if not peaks:
        return None, h.tolist()
    hi = max(peaks, key=lambda i: h[i])
    valley = int(h[lo:hi + 1].min())
    bimodal = h[hi] > valley and h[lo] > valley
    return (float((centers[lo] + centers[hi]) / 2) if bimodal else None), h.tolist()


def runs(mask):
    """(start, end) of True runs, end exclusive."""
    d = np.diff(np.concatenate([[0], mask.astype(int), [0]]))
    return list(zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]))


def zero_run(v, start, step):
    """Length of the zero-ink run from start in direction step; None if it hits the band edge."""
    i, n = start, 0
    while 0 <= i < len(v) and v[i] == 0:
        i += step
        n += 1
    return n if 0 <= i < len(v) else None


def measure(ink):
    H, W = ink.shape
    x0, x1 = int(BAND[0] * W), int(BAND[1] * W)
    slabs = [ink[y:y + R] for y in range(0, H - R + 1, R)]
    f = np.array([s[:, x0:x1].sum(0) / R for s in slabs])
    T, hist = mode_midpoint(f)
    rows = []
    for i, s in enumerate(slabs):
        two_col = (s[:, int(LEFT_TEXT[0] * W):int(LEFT_TEXT[1] * W)].any()
                   and s[:, int(RIGHT_TEXT[0] * W):int(RIGHT_TEXT[1] * W)].any())
        if not two_col:
            continue
        v = s[:, x0:x1].sum(0)
        row = {"slab": i, "y": i * R}
        clusters = []
        if T is not None:
            for a, b in runs(f[i] >= T):
                if clusters and a - clusters[-1][1] <= 1:
                    clusters[-1] = (clusters[-1][0], b)
                else:
                    clusters.append((a, b))
        # Each cluster grows to its contiguous nonzero block; the rule is the
        # block with the most white on both sides (text stems have little).
        cands = []
        for ca, cb in clusters:
            a, b = ca, cb
            while a > 0 and v[a - 1] > 0:
                a -= 1
            while b < len(v) and v[b] > 0:
                b += 1
            lw, rw = zero_run(v, a - 1, -1), zero_run(v, b, 1)
            if lw and rw and (a, b) not in [c[:2] for c in cands]:
                cands.append((a, b, lw, rw))
        if cands:
            a, b, lw, rw = max(cands, key=lambda c: min(c[2], c[3]))
            n = 1
            # Double rule: a second isolated candidate across a gap narrower
            # than its own outer white.
            for c in cands:
                if c[1] + c[3] == a and c[2] > c[3]:
                    a, lw, n = c[0], c[2], 2
                elif c[0] - c[2] == b and c[3] > c[2]:
                    b, rw, n = c[1], c[3], 2
            row.update(rule=n, rule_x=int(x0 + a), rule_w=int(b - a), left_white=lw,
                       right_white=rw, gutter=int(lw + (b - a) + rw))
        else:
            zr = [(b - a, a) for a, b in runs(v == 0)]
            interior = [(n, a) for n, a in zr if a > 0 and a + n < len(v)]
            row.update(rule=0, gutter=int(max(interior)[0]) if interior else None)
        rows.append(row)
    # The outermost two-column slabs straddle the running head and the
    # block's last line; coverage is over the slabs between them.
    inner = rows[1:-1]
    ruled = [r for r in inner if r["rule"]]
    cov = len(ruled) / len(inner) if inner else 0.0
    return {
        "threshold": T, "hist": hist, "two_col_slabs": len(rows), "inner_slabs": len(inner),
        "rule_slabs": len(ruled), "coverage": round(cov, 3),
        "rule_present": T is not None and cov >= 0.5, "flag": T is None or cov < 0.9,
        "rule_kind": sorted({r["rule"] for r in ruled}),
        "rule_w_px": [r["rule_w"] for r in ruled],
        "gutter_px": [r["gutter"] for r in ruled],
        "gutter_norule_px": [r["gutter"] for r in inner if not r["rule"] and r["gutter"] is not None],
        "slabs": rows,
    }


def main(pdf_path, first, last, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(pdf_path)
    header = {
        "run": "gill-column-rule",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "pdf_sha256": hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest(),
        "pages_printed": [first, last], "pdf_offset": OFFSET,
        "params": {"R": R, "band": BAND, "left_text": LEFT_TEXT, "right_text": RIGHT_TEXT,
                   "bins": BINS, "dpi": DPI},
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                     "pypdfium2": importlib.metadata.version("pypdfium2")},
    }
    pages = {}
    for p in range(first, last + 1):
        pages[p] = measure(bitmap(pdf, p))
    (out / "column_rule.json").write_text(json.dumps({"header": header, "pages": pages}, indent=1, default=str))
    for p, r in pages.items():
        g = r["gutter_px"]
        print(p, "present" if r["rule_present"] else "ABSENT", "flag" if r["flag"] else "",
              "T", None if r["threshold"] is None else round(r["threshold"], 3),
              "cov", r["coverage"], f"{r['rule_slabs']}/{r['two_col_slabs']}", "kind", r["rule_kind"],
              "rule_w med", int(np.median(r["rule_w_px"])) if r["rule_w_px"] else None,
              "gutter med/min/max", (int(np.median(g)), min(g), max(g)) if g else None)


if __name__ == "__main__":
    try:
        main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    except Fail as e:
        sys.exit(f"FAIL: {e}")
