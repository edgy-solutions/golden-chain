# Report 33: the two-day order, Day 2 (items 4-7), with items 8 and 9 of the ruling on report 32

- **From:** the build agent, 2026-11-27. Branch `phase-0`, pushed.
- **On:**
  - [RULING_report_31.md](RULING_report_31.md), the two-day order, Day 2;
  - [RULING_report_32.md](RULING_report_32.md), applied (its "Applied" table lists each commit).
- **Each item was locked before its work.** Misses are recorded, not edited.
- **Nothing is minted.** No `data/` file changed, and no existing test changed. No hold/ branch was needed.
- **One fetch was refused (item 6).** It was recorded, and the item stopped.
- **No image was viewed for items 4-9.** Gill pp. 897-912 were not opened by any tool. Subagents were used only to write code from a spec.

## One list: what waits on Chris, and on the architect

**On Chris (sign from the pixels; each page is local, under `~/.golden-chain/console/`):**

1. **Sitting 2:** `plumb-line-followup/console_plumb-line-followup_e38d95cac2ff7bb3.html`.
   - It was rebuilt under the ruling on report 32, and supersedes `18a4a13dfeffb6e9`.
2. **Statements and inclusion:** `statements/console_statements_f3f1af17d9075ba5.html`.
3. **LBC 1677:** `console_lbc-1677_0a73bb5afa616446.html`.
   - LBC 28.2 (a C-d read) waits on it.
4. **Gill's italic:** `italic-spans/console_italic-spans_9b19159be3098c64.html`.
   - Part 2 of the argument-unit page pass (Gill *Body* pp. 897-912) waits on it.
5. **Item 6, if wanted:** download by hand the twenty FILE pages that item 6's lock chose, into a local folder. Or decide with the architect to leave them. The build agent does not ask the site again.

**On the architect:**

- **Item 4** ([FINDINGS_item4_gill_book2_2026-11-27.md](FINDINGS_item4_gill_book2_2026-11-27.md)):
  - The lock named the wrong frame for the column rule. Score K1 and K2 as a lock error, with the 6.947 results standing, or re-lock?
  - K2's 51 px median (inside the band, below the prediction).
  - The 7 thin runs near the rule (a viewing pass, or a margin-rule change?).
  - Re-read the 7 skipped pages at the 6.947 frame?
  - The narrow-glyph baseline, 823 runs and 9 px against report 13's 872 and 10 px.
- **Item 5** ([FINDINGS_item5_footnote_rule_2026-11-27.md](FINDINGS_item5_footnote_rule_2026-11-27.md)):
  - Choose among the three proposed rules (line pitch, the white-gap boundary, a 0.90 cut-off), each under a new lock.
  - The footnote type is 0.84 of the body.
- **Item 6** ([FINDINGS_item6_second_typeface_2026-11-27.md](FINDINGS_item6_second_typeface_2026-11-27.md)): the scans, by Chris's hand or not at all.
- **Item 7** ([FINDINGS_item7_weigh_body_pages_2026-11-27.md](FINDINGS_item7_weigh_body_pages_2026-11-27.md)):
  - ADR-0008 Revision 1's five open points: the groups' reading; "no locus covered"; whether the ruled wordings count as signed records; officers scope; comparison views.
  - Should `build()` make the new pages by default? That would amend two existing tests, on a hold/ branch.
- **Item 8** (`79f3aae`):
  - ADR-0011's open points, first among them that **the repository is public**;
  - ADR-0012's open points, first among them whether Neo4j is needed.
- **Item 9** ([RECUT_list_outside_gill_897_912_2026-11-27.md](RECUT_list_outside_gill_897_912_2026-11-27.md)), Q-A-2:
  - Apply the 7 → 21 re-cut now, or with part 2?
  - The deprecation form.
  - F6 on `gill-body/doctrinal/4/5/003` travels unresolved.
- **From the ruling on report 32:**
  - the G-P5 label source (Fuller);
  - the two Gill leads on duty-faith;
  - WCF 27.4 and Scots XXII on C-d, to be entered or not;
  - whether "the covenant chapters" (II.7-II.15 by title) is the right scope for item 4.

## What Day 2 did

| Item | Lock | Work | Findings | The lock, scored |
|---|---|---|---|---|
| 4. Gill Book II by machine (90 pages) | `bd7eb6d` | `5142b73` (2 tools, 29 tests) | `06dccdd` | 8 hit (K4-K11); 3 missed (K1-K3) |
| 5. Footnote rule (baptism chapter) | `895affc` | `4e2b541`, fixed `9d6dae3` | `40a57ec` | 3 hit (N1, N6, N7); 4 missed (N2-N5). Agrees with the p. 914 note; disagrees with p. 913. |
| 6. The second typeface | `65942f5` | none | `be1f780` | Refused by robots.txt; E1 missed, E2-E8 not measured |
| 7. Weigh and Body pages (local) | `7a33551` | `e9fb45a` (20 tests; ADR-0008 R1 proposed) | this commit | 7 hit (WX1-WX7); suite 993 passed, 1 skipped |
| 8. ADR-0011 and ADR-0012 | none (drafts) | `79f3aae` | none | Proposed, not built |
| 9. The re-cut list outside pp. 897-912 | `e4b7d47` | none | `785e8f2` | 6 hit (R1-R6) |

**In brief:**

- **Item 4:**
  - OCR reads 955.8 words a page on Doctrinal and 911.3 on Practical.
  - The fail shares for words that do not crop cleanly are slanted 9.07 % / 10.04 % and upright 6.04 % / 6.46 %, close to the baptism chapter's.
  - No text entered the repo. Nothing was drawn.
- **Item 5:** footnote type measured by word-box height is 0.84 of the body, just under the 0.85 cut-off. So the rule finds a zone in only 5 of 40 columns.
- **Item 7:**
  - The groups are what the lock predicted: Gill and LBC 1689 could join; the Small Catechism could join with one stated difference (baptism-efficacy, a break); Book of Concord has no locus covered.
  - Apology, Augsburg and WCF are listed apart with their derivation and the unsigned-statement line.
  - All 172 existing pages are byte-identical.
- **Item 9:** 7 Arguments become 21. Every number, cite and Passage checks against the data. The 35 Batch C Arguments were cut on the unit when minted, and none is a candidate.

## Not done, and why

- **Item 6:** the site refuses Anthropic's agents in robots.txt, so it was not worked around.
- **Not read:**
  - Gill pp. 897-912: the order forbids it.
  - The open sittings' pages.
- **Not drawn:**
  - nothing for signing, as item 4 says;
  - no changed footnote rule was measured, because item 5's lock requires a new lock first.
