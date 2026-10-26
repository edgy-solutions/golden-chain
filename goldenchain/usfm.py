"""Read chapter and verse counts from a USFM Bible (eBible.org layout).

Counts only; no text is kept. Used to cross-check goldenchain.versification
against an independent witness. Gaps, duplicates and non-monotonic
numbering raise UsfmError rather than being repaired.
"""

import re
from pathlib import Path

from goldenchain.versification import BOOKS

_CODES = (
    "GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB "
    "PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP "
    "HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI "
    "2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"
).split()
assert len(_CODES) == len(BOOKS) == 66
USFM_TO_OSIS: dict[str, str] = dict(zip(_CODES, BOOKS))

_TOKEN = re.compile(r"\\(id|c|v)[ \t]+(\S+)")


class UsfmError(ValueError):
    pass


def parse_book(text: str) -> tuple[str, tuple[int, ...], list[tuple[int, str]]]:
    """Return (osis_book, verses_per_chapter, bridges) for one USFM file.

    bridges is a list of (chapter, "a-b") for each verse range seen.
    """
    book = None
    chapters: list[int] = []  # highest verse per chapter
    bridges: list[tuple[int, str]] = []
    for kind, arg in _TOKEN.findall(text):
        if kind == "id":
            if book is not None:
                raise UsfmError(f"second \\id {arg} after {book}")
            if arg not in USFM_TO_OSIS:
                raise UsfmError(f"unknown \\id {arg}")
            book = USFM_TO_OSIS[arg]
        elif kind == "c":
            if not arg.isdigit() or int(arg) != len(chapters) + 1:
                raise UsfmError(f"{book}: chapter {arg} after {len(chapters)}")
            chapters.append(0)
        else:
            if not chapters:
                raise UsfmError(f"{book}: verse {arg} before any chapter")
            m = re.fullmatch(r"(\d+)(?:-(\d+))?", arg)
            if not m:
                raise UsfmError(f"{book} {len(chapters)}: bad verse {arg!r}")
            lo = int(m.group(1))
            hi = int(m.group(2) or lo)
            if lo != chapters[-1] + 1 or hi < lo:
                raise UsfmError(
                    f"{book} {len(chapters)}: verse {arg} after {chapters[-1]}"
                )
            if hi != lo:
                bridges.append((len(chapters), arg))
            chapters[-1] = hi
    if book is None:
        raise UsfmError("no \\id")
    if not chapters or 0 in chapters:
        raise UsfmError(f"{book}: no chapters or an empty chapter")
    return book, tuple(chapters), bridges


def read_all(usfm_dir) -> tuple[dict[str, tuple[int, ...]], list[tuple[str, int, str]]]:
    """Parse every *.usfm file; return (counts, bridges)."""
    counts: dict[str, tuple[int, ...]] = {}
    bridges: list[tuple[str, int, str]] = []
    for path in sorted(Path(usfm_dir).glob("*.usfm")):
        book, ch, br = parse_book(path.read_text(encoding="utf-8-sig"))
        if book in counts:
            raise UsfmError(f"duplicate book {book} ({path.name})")
        counts[book] = ch
        bridges += [(book, c, v) for c, v in br]
    return counts, bridges


def read_counts(usfm_dir) -> dict[str, tuple[int, ...]]:
    """Verses per chapter by OSIS book id, in BOOKS order where present."""
    counts, _ = read_all(usfm_dir)
    return {b: counts[b] for b in BOOKS if b in counts}


def diff_counts(a: dict, b: dict) -> list[tuple]:
    """Differences between two {book: verses-per-chapter} maps.

    ("missing", book, "a"|"b")            book absent from that side
    ("chapters", book, len_a, len_b)      chapter-count mismatch
    ("verses", book, chapter, va, vb)     verse-count mismatch (1-based chapter)
    """
    out: list[tuple] = []
    for book in [*a, *(k for k in b if k not in a)]:
        if book not in b:
            out.append(("missing", book, "b"))
        elif book not in a:
            out.append(("missing", book, "a"))
        elif len(a[book]) != len(b[book]):
            out.append(("chapters", book, len(a[book]), len(b[book])))
        else:
            for i, (x, y) in enumerate(zip(a[book], b[book]), 1):
                if x != y:
                    out.append(("verses", book, i, x, y))
    return out
