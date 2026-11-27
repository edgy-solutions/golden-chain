"""B2, B3 (LOCK_report29): the plumb-line form tests derive their counts from the loci file they read."""
import shutil

import test_console_specs as tcs

LOCI_ADDED = '''
# Born test: a Locus the form tests have never heard of.
<locus/zz-derived-check> a gc:Locus ;
    rdfs:label "Derived-count check"@en ;
    skos:notation "33z" ;
    gc:underHeading <heading/worship> ;
    gc:question "Does a new Locus need a test amended?"@en .

<position/zz-derived-check/first> a gc:Position ;
    rdfs:label "First position on the check Locus."@en ;
    gc:answers <locus/zz-derived-check> ;
    gc:status <vocab/status/proposed> ;
    gc:proposedBy <agent/build-agent> .

<position/zz-derived-check/second> a gc:Position ;
    rdfs:label "Second position on the check Locus."@en ;
    gc:answers <locus/zz-derived-check> ;
    gc:status <vocab/status/proposed> ;
    gc:proposedBy <agent/build-agent> .
'''


def test_derived_values_on_the_real_loci_file():
    loci, npos = tcs.derived(tcs.LOCI)
    assert (npos, len(loci)) == (25, 12)
    assert (npos - 2, npos - 1, len(loci) - 1) == (23, 24, 11)  # Holdings and holds; silence Holdings; tiers


def born_loci(tmp_path):
    p = tmp_path / "loci.ttl"
    shutil.copy(tcs.LOCI, p)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(LOCI_ADDED)
    assert tcs.derived(p)[1:] == (27,) and len(tcs.derived(p)[0]) == 13
    return p


def test_born_spec_matches_form(tmp_path):
    tcs.check_spec_matches_form(born_loci(tmp_path))


def test_born_ttl_writer(tmp_path, monkeypatch):
    p = born_loci(tmp_path)
    (tmp_path / "w").mkdir()
    tcs.check_ttl_writer(tcs.plumb_for(tmp_path / "w", monkeypatch, p), p)


def test_born_null_modality_is_silence(tmp_path, monkeypatch):
    p = born_loci(tmp_path)
    (tmp_path / "s").mkdir()
    tcs.check_null_modality_is_silence(tcs.plumb_for(tmp_path / "s", monkeypatch, p), p)
