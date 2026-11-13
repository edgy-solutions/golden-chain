# To goat-yard (A2): a single-rule fixture, offered (2026-11-08)

From: the Golden Chain build agent, sent by Chris. Prepared on the Golden Chain architect's ruling (report 5, Q4; ordered on report 10).

**What it is.** A synthetic two-column page in the shape of `test_verse_regions._cs_page`, but with one printed column rule where `_cs_page` has the double rule. Golden Chain's 20 pages (BSB/Tegg Gill, printed 896–915) carry a single rule. The fixture is `tools/gy_single_rule_fixture.py` in the Golden Chain repo, numpy only, with no goat-yard import. Its cases are in `tests/test_gy_single_rule_fixture.py`. Nothing from the substrate is copied. Take it, adapt it or leave it: goat-yard decides.

**Where the numbers come from.** Every default is measured from our `locate_column_rule` run at scale 6.947 on substrate-v1 (rules [None, None]; 12 strips; line height matched to 55). The measurements are numbers from the run's stored strip fractions, not readings of images:
- the frame is 3002 × 4502;
- the run of rule columns at or above 0.59 is 3/5/7 px wide (min/median/max), with a peak fraction of 1.0;
- the white flank between rule and type is 36/37 px;
- the type column fraction is p50 0.163 and p99.9 0.520, and 13 of 138,240 strip columns reach 0.59;
- c0 is 1500.8, and the slopes run from −0.0056 to +0.0021.

Defaults: c0 1500.8, slope −0.0012, rule 5 px, flank 36, line height 55, pitch 67.

**What it checks, at substrate-v1** (all hold):

| Case | Result |
|---|---|
| Rule 3 / 5 / 7 px | ok; n_rule 12/12; half_w 1.5 / 2.5 / 3.5; c0 1500.9; slope −0.001236; max_resid 0.4 |
| Bands, `analyze_page_s1` | col_split ok; no full-width bands; all 51 left bands end at the drawn type end (exclusive); all 51 right bands start at the drawn type start |
| Rule missing from 5 of 12 strips | ok, n_rule 7 (our p. 896 case) |
| Rule missing from 7 of 12 strips | abstained, `no_rule`, n_rule 5 |
| Dashed rule, duty 0.4 | abstained, `no_rule`, n_rule 0 |
| Dashed rule, duty 0.7 | ok, n_rule 12, half_w 2.5 |

**One observation, no request.** Our first draft drew type as separate 5 px strokes. With that type, every left band's `right_ink_x` fell about 81 px short. The cause is in `_make_band`: inside the ±120 px gutter window, every ink run of `RULE_RUN_MAX_W` (8) px or less is treated as rule. The miss was in our fixture, because real type projects to word-wide runs, so we joined the strokes into words. The same rule would also erase a real lone narrow glyph (a lone "I", or a numeral "1") that ends a line within 120 px of the gutter, so the band would end at the word before it. We have since measured it on BSB Gill pp. 896-915 (native 5100 x 7650 frame; substrate-v1 consumed unchanged; our tools/gy_narrow_glyph.py, prediction locked first). Of 1095 left-column S1 bands, 872 end in text inside the window, and none of those line-final text runs is 8 px or narrower; the narrowest is 10 px. Every run of 8 px or less at a line end there is the printed rule's own uneven edge or a speck, which the rule is meant to erase. On these pages, then, it clips no text. The margin is small (10 px against 8), so a lighter impression or a smaller face could cross it. We are not asking for a change.
