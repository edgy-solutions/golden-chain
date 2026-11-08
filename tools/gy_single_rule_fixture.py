"""Synthetic single-column-rule page, offered to goat-yard's A2.

It has the shape of goat-yard's test_verse_regions._cs_page: a two-column page
with one vertical column rule between the columns and footnote rules
[None, None]. Numpy only; nothing is imported from goat-yard.

Every default comes from Golden Chain's measured run at scale 6.947 (BSB Gill
1766 Body, pp. 896-915, substrate-v1,
~/.golden-chain/gy-locate-column-rule-v1-scale6.947-2026-11-01/), from numbers,
not from images. Measured values used:
- frame 3002 x 4502; y_end 4202; 12 strips from 700;
- rule run of columns >= 0.59: 3/5/7 px (min/median/max); peak fraction 1.0;
- white flank from rule edge to type: median 36 (left) / 37 (right);
- type column fraction p50 0.163, p95 0.333, p99 0.417, p99.9 0.520;
- track c0 median 1500.8; line height 55, pitch 67.
"""

import numpy as np

W, H = 3002, 4502  # measured frame
LINE_H, PITCH = 55, 67  # measured line height (matched to goat-yard) and pitch
Y0 = 760  # first type line, below the 640 body top and RULE_TOP
Y_END = H - 300  # rules [None, None] -> 4202, measured on every page
RULE_TOP = 700  # strips start at 700, measured
STROKE_W, STROKE_STEP = 5, 9  # type strokes giving column fractions 0.33/0.48
XH_TOP, XH_BOT = 20, 42  # x-height stroke rows within a line (22 rows)
ASC_TOP = 10  # ascender rows 10..42 (32 rows); every third stroke is one
# Strokes are set in words joined by a baseline hairline, so a band's column projection is
# word-wide runs, as real type is. Lone 5-px strokes are runs <= goat-yard's RULE_RUN_MAX_W (8)
# and are erased as rule near the gutter (v1 of this fixture; lock v2).
WORD_STROKES, WORD_SPACE = 5, 9
WORD_W = WORD_STROKES * STROKE_STEP - (STROKE_STEP - STROKE_W)  # 41
WORD_PITCH = WORD_W + WORD_SPACE  # 50
HAIR = XH_BOT - 1  # hairline row joining a word's strokes


def _set_line(ink, y, edge, side):
    """Set one line's words outward from edge (left: ending at edge; right: starting at it).
    Returns the far end: the first inked column (left) or the exclusive end (right)."""
    far, i, k = edge, 0, 0
    while True:
        d = k * WORD_PITCH
        lo, hi = (edge - d - WORD_W, edge - d) if side == "left" else (edge + d, edge + d + WORD_W)
        if lo < 100 or hi > W - 100:
            return far
        ink[y + HAIR, lo:hi] = True
        for j in range(WORD_STROKES):
            x = hi - STROKE_W - j * STROKE_STEP if side == "left" else lo + j * STROKE_STEP
            top = ASC_TOP if i % 3 == 2 else XH_TOP
            ink[y + top:y + XH_BOT, x:x + STROKE_W] = True
            i += 1
        far, k = (lo if side == "left" else hi), k + 1


def centre(c0, slope, y):
    return c0 + slope * y


def single_rule_page(c0=1500.8, slope=-0.0012, xdiv=1471, rule_w=5, flank=36,
                     missing_strips=(), duty=None):
    ink = np.zeros((H, W), dtype=bool)
    starts = {}
    for y in range(RULE_TOP, Y_END):
        a = int(round(centre(c0, slope, y) - rule_w / 2))
        starts[y] = a
        if (y - 700) // 300 in missing_strips:
            continue
        if duty is not None and (y % 10) >= round(duty * 10):
            continue
        ink[y, a:a + rule_w] = True
    texts = {}
    y = Y0
    while y + LINE_H <= Y_END - 20:
        edges = [starts[y], starts[y + LINE_H - 1]]
        rule_lo, rule_hi = min(edges), max(edges) + rule_w
        l_end, r_start = rule_lo - flank, rule_hi + flank
        l_start = _set_line(ink, y, l_end, "left")
        r_end = _set_line(ink, y, r_start, "right")
        texts[("left", y)] = (l_start, l_end)
        texts[("right", y)] = (r_start, r_end)
        y += PITCH
    geom = {"file_page": 1, "mode": "two_column", "xdiv": xdiv, "page": [W, H],
            "rules": [None, None],
            "body_regions": [{"col": "left", "box": [0, 640, xdiv, Y_END]},
                             {"col": "right", "box": [xdiv, 640, W, Y_END]}]}
    return ink, geom, texts


def column_fractions(ink, y0, y1, lo, hi):
    return ink[y0:y1, lo:hi].mean(axis=0)
