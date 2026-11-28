# The re-cut list for every Argument outside Gill pp. 897-912 (2026-11-27), ready for ruling

- **From:** the build agent, 2026-11-27, on the ruling on report 32, item 9.
- **Lock:** [LOCK_item9_recut_list_2026-11-27.md](LOCK_item9_recut_list_2026-11-27.md) (`e4b7d47`), committed before the check.
- **Rests on:** [AUDIT_argument_unit_2026-11-26.md](AUDIT_argument_unit_2026-11-26.md), page pass part 1 (lock `a08a324`). The units as printed are the ones part 1 read from the page images. **No page was viewed for this list.** It checks part 1's proposals against the data by machine.
- **Nothing is changed.** No file under `data/` or `tests/` changes. The list is unapplied until it is ruled (ruling on report 30, Q-A-2: "Re-cut, but once").

## Which Arguments it covers

The data at `e4b7d47` holds 115 Arguments.

| Group | Arguments | Where it stands |
|---|---|---|
| Audited, outside Gill pp. 897-912 | 63 | Part 1 viewed all 63: **56 same cut, 7 would split into 21 units**, 0 merge, 0 widen. |
| Audited, Gill *Body* Practical III.1 001-017 (pp. 897-912) | 17 | Out of scope here. Waiting for part 2, which waits on the italic-spans sitting `9b19159be3098c64`. |
| Minted by Batch C on the quotation unit (`f639051`, LOCK_batchC_unit U1-U10) | 35 | Not audited, because they were cut on the unit when minted. They are 23 Heidelberg (Harbaugh), 8 Belgic and 4 Gill *Body* Practical III.1 (022-025, "Sixthly, 1."-"Sixthly, 4.", `gc:secondaryLocator` "BSB 2019 p. 914"). All 35 are outside pp. 897-912, and none is a re-cut candidate. |

So outside pp. 897-912 the list is complete: the 7 below, and no others.

## The list

The rules for each re-cut, as in the audit:
- Each old IRI is deprecated with `dcterms:isReplacedBy` (one triple per new unit) and is never reused.
- Each new Argument keeps the old one's `gc:supports`, source and `gc:locator`.
- Each new Argument cites only its unit's Passages.

| Old Argument | Supports | Locator | New (proposed) | Unit as printed | Cites | Page |
|---|---|---|---|---|---|---|
| `coxe-covenants/5/8/001` | `circumcision-covenant/not-an-administration-of-grace` | V §8 | `coxe-covenants/5/8/002` | "Gen. 17. 4, 5." | Gen.17.4-Gen.17.5 | 105 |
| | | | `coxe-covenants/5/8/003` | "Rom. 4. 17." | Rom.4.17 | 106 |
| | | | `coxe-covenants/5/8/004` | "Rom. 4." | Rom.4.1-Rom.4.25 | 106 |
| | | | `coxe-covenants/5/8/005` | marginal note "Read diligently Gal. 3." | Gal.3.1-Gal.3.29 | 106 |
| | | | `coxe-covenants/5/8/006` | "Rom. 4. 11." | Rom.4.11 | 107 |
| | | | `coxe-covenants/5/8/007` | "Gen. 17." | Gen.17.1-Gen.17.27 | 109 |
| `gill-body/doctrinal/2/15/003` | `covenant-of-grace/eternal-with-christ` | 1. | `gill-body/doctrinal/2/15/004` | "Psalm lxxxix. 2, 3, 28. and ciii. 17." | Ps.89.2-Ps.89.3, Ps.89.28, Ps.103.17 | 247 |
| | | | `gill-body/doctrinal/2/15/005` | "John xvii. 23, 24." | John.17.23-John.17.24 | 247 |
| | | | `gill-body/doctrinal/2/15/006` | "Eph. i. 4." | Eph.1.4 | 247 |
| | | | `gill-body/doctrinal/2/15/007` | "Prov. viii. 23. Mic. v. 2." | Prov.8.23, Mic.5.2 | 247 |
| `gill-body/doctrinal/4/5/001` | `covenant-administrations/one-covenant-two-administrations` | First, 1. | `gill-body/doctrinal/4/5/002` | "Heb. ix. 10." | Heb.9.10 | 361 |
| | | | `gill-body/doctrinal/4/5/003` | "Gal. iii. 1, 2, 3, 4. and iii. 24, 25." | Gal.3.24-Gal.3.25, and the two `gc:citesCandidate` (Gal.3.1-Gal.3.4, Gal.4.1-Gal.4.4) carried over unresolved (F6) | 361 |
| `gill-divine-right/4/001` | `circumcision-covenant/not-an-administration-of-grace` | First, 1. | `gill-divine-right/4/006` | "Acts vii. 8." | Acts.7.8 | 45 |
| | | | `gill-divine-right/4/007` | "Gal. v. 2, 3, 4." | Gal.5.2-Gal.5.4 | 45 |
| `gill-divine-right/4/003` | `circumcision-covenant/not-an-administration-of-grace` | First, 3. | `gill-divine-right/4/008` | "Gen. xvii. 14." | Gen.17.14 | 46 |
| | | | `gill-divine-right/4/009` | "Ps. lxxxix. 34." | Ps.89.34 | 46 |
| `gill-divine-right/4/004` | `circumcision-covenant/not-an-administration-of-grace` | First, 4. | `gill-divine-right/4/010` | "Gen. xvii. 6, 8." | Gen.17.6, Gen.17.8 | 46 |
| | | | `gill-divine-right/4/011` | "ver. 5." | Gen.17.5 | 46 |
| `graves-old-landmarkism/10/001` | `baptism-validity/church-of-our-order` | Ch. X | `graves-old-landmarkism/10/002` | "(Matt. 16: 18)" | Matt.16.18 | 124 |
| | | | `graves-old-landmarkism/10/003` | "(Heb. 12: 28)" | Heb.12.28 | 124 |
| | | | `graves-old-landmarkism/10/004` | "Daniel (2: 44)" | Dan.2.44 | 124 |

That is **7 old Arguments becoming 21**. The total would go from 115 to 129 live Arguments, plus 7 deprecated.

## The lock, scored (never edited)

| # | Result | |
|---|---|---|
| R1 | 7 old become 21 new; the other 56 audited Arguments outside pp. 897-912 are unchanged. (The 35 Batch C Arguments, minted on the unit after the audit, are listed above. The lock did not mention them.) | **Hit** |
| R2 | None of the 21 IRIs is in use. | **Hit** |
| R3 | Each division's numbers follow its highest existing Argument with no gap: `coxe-covenants/5/8` 001 → 002-007; `gill-body/doctrinal/2/15` 003 → 004-007; `gill-body/doctrinal/4/5` 001 → 002-003; `gill-divine-right/4` 005 → 006-011; `graves-old-landmarkism/10` 001 → 002-004. | **Hit** |
| R4 | Each unit cites a subset of its old Argument's `gc:cites`, and each split's units cover all of them. | **Hit** |
| R5 | Every cited Passage exists. | **Hit** |
| R6 | No file under `data/` or `tests/` changed. | **Hit** |

## For the ruling

1. **Apply these 7 now, or with part 2?** The ruling on report 30 says "re-cut, but once, after the page pass is complete". Part 2 (pp. 897-912) waits on a sitting. These 7 are in other divisions, so their numbers are final whatever part 2 finds. Applying them now would be one locked change, with tests born with it. Waiting keeps the re-cut to one act.
2. **The deprecation form.** `dcterms:isReplacedBy` from the old Argument to each new one, and the old one kept with its triples. Or should the old one also lose its `gc:cites`, so that a passage page lists each quotation once?
3. **F6 on 4/5/003.** The two candidate readings of "Gal. iii. 1, 2, 3, 4." travel with the unit unresolved. This is not a unit question.
