# Ruling: the BSB foreword's status, quotation, and the testimony (filed verbatim)

- **From:** the architect, relayed by Chris, 2026-11-22.
- **On:** the BSB 1984 foreword to Gill's *Body of Divinity*, as described on the sitting-1 follow-up console (`eb961ddb1e582ed6`, row `validity-3-testimony`) and in [PROPOSAL_validity_bsb_foreword.md](PROPOSAL_validity_bsb_foreword.md).

```
BSB foreword: the console's "not public domain" is too strong.
Record its status as "published 1984; no copyright notice per
Chris; publisher's stated position that its books are freely
distributable; written confirmation to be sought before public
launch". Short verbatim quotation of the numbered propositions is
permitted: quote propositions 3 and 7 for validity, and conclusion
1(a) on Gill's Practical III.1, each with its page, in place of any
paraphrase. Also record: the earlier "testimony" on the foreword
ruling mixed Chris's words with the architect's. Chris's own words
are those he signs on row validity-3-testimony; the Spilsbury and
succession details were the architect's and are not testimony.
```

## Applied

Worked 2026-11-22 by the build agent.

- **Status recorded as ruled** in:
  - `data/bsb-gill-1984.ttl`: the file comment and the work's `dcterms:bibliographicCitation`. No quotation is stored in data (`test_bsb_not_quoted` stands). Weigh byte-identical (`71c14a5d187d` / `c8fe9e910b5a`); validation 0 violations, 3 warnings; `tests/test_step3_batch_b.py` 22 passed.
  - [../sources/lee-bsb.md](../sources/lee-bsb.md) (item 5) and [../sources/gill-body-of-divinity.md](../sources/gill-body-of-divinity.md) ("What enters the repo").
  - [PROPOSAL_validity_bsb_foreword.md](PROPOSAL_validity_bsb_foreword.md): a "Corrections recorded" section appended; the record itself is not rewritten.
- **Quotations,** transcribed by the build agent from the page images of the BSB PDF in the private corpus (pp. vii, viii, xiii = PDF 8, 9, 14):
  - Proposition 3 (p. vii): "Scriptural baptism is absolutely necessary to church constitution, organization and existence, so much so, that where there is no Scriptural baptism there is no Scriptural church. No baptism, no church."
  - Proposition 7 (p. viii): "Only churches of New Testament origin and New Testament order can give Scriptural baptism. Therefore, any religious society that preaches a false gospel cannot give Scriptural baptism."
  - Conclusion 1(a) (p. xiii): quoted in full in [REPORT_phase1_25.md](REPORT_phase1_25.md), in place of its paraphrase there.
- **The testimony correction** is recorded in the proposal file and in the handoff's 2026-11-08 entry. Past reports (11–13) are records and are not edited.
- **Not done: the console.** `eb961ddb1e582ed6`, row `validity-3-testimony`, still reads "Nothing from the foreword is quoted here (not public domain)" and offers the mixed string as "Your words as recorded", with "my recorded words stand" as an answer. Fixing it means a rebuild, with a new console id. The 23a dispatch said not to rebuild `eb961ddb`. So the rebuild waits on Chris. The proposed row, if rebuilt:
  - context: propositions 3 and 7 with pages; the status as ruled; "An earlier record mixed your words with the architect's. Only what you write here is your testimony.";
  - answer: free text in Chris's own words, with no proposed wording.
- **A question for the architect.** The source division in data is "pp. vii–viii, propositions 1 and 7" (ruling B-Q4). This ruling names propositions **3** and 7 for validity. Proposition 1 is the one with "true New Testament Church of gospel order". Should the division's label stay as 1 and 7, or become 1, 3 and 7? Not changed.

### Corrected by the ruling on report 26 ([RULING_report_26.md](RULING_report_26.md), ruling 2)

- **The architect:** "your label is right and my ruling misnamed it." Propositions **1 and 7** are the source for validity (3). Proposition 3 ("no baptism, no church") is quoted where the recursion and the church-Locus dependency are recorded, not as the source for (3). Recorded against the architect.
- **So the question above is answered:** the source division stays "pp. vii–viii, propositions 1 and 7". Data is unchanged.
- **Applied:** [../sources/lee-bsb.md](../sources/lee-bsb.md) item 5 now quotes Proposition 1 (p. vii): "Any religious assembly that preaches a false gospel and/or practices a false baptism cannot be recognized as a true New Testament Church of gospel order. All such assemblies who fundamentally, characteristically and permanently preach a false gospel come under the indictment of Gal. 1:6-9." and proposition 7 for validity. Proposition 3 is kept there for the recursion only, and quoted in [PROPOSAL_validity_bsb_foreword.md](PROPOSAL_validity_bsb_foreword.md), "Corrections recorded". [REPORT_phase1_25.md](REPORT_phase1_25.md) carries a correction note after its "for comparison" block. The lists above are left as worked.
- **The console:** `eb961ddb` was signed and is not rebuilt (ruling 1). Its testimony row is recorded as a console defect in [AUDIT_plumb_line_followup_eb961ddb1e582ed6.md](AUDIT_plumb_line_followup_eb961ddb1e582ed6.md).
