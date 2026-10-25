"""Canonical passage IRIs (ADR-0002, "Passage scheme")."""

import re
from dataclasses import dataclass

from goldenchain.versification import BOOKS, V11N, last_verse, verse_ordinal

BASE = "https://w3id.org/golden-chain/"

_B = "(?:" + "|".join(BOOKS) + ")"
_V = r"[1-9][0-9]*"
_VERSE = rf"{_B}\.{_V}\.{_V}"
IRI_PATTERN = (
    "^" + re.escape(BASE + "passage/" + V11N + "/")
    + f"{_VERSE}(?:-{_VERSE})?$"
)

_REF = re.compile(rf"^({_B})\.({_V})(?:\.({_V}))?$")


@dataclass(frozen=True)
class Passage:
    v11n: str
    book: str
    osis: str
    start_ordinal: int
    end_ordinal: int


def _check(v11n: str) -> None:
    if v11n != V11N:
        raise ValueError(f"unsupported v11n: {v11n!r}")


def _point(text: str, end: bool) -> tuple[str, int, int]:
    """Parse Book.C or Book.C.V; a bare chapter means its first/last verse."""
    m = _REF.match(text)
    if not m:
        raise ValueError(f"malformed reference: {text!r}")
    book, c = m.group(1), int(m.group(2))
    if m.group(3) is not None:
        v = int(m.group(3))
    else:
        v = last_verse(book, c) if end else 1
    verse_ordinal(book, c, v)  # validates chapter and verse
    return book, c, v


def _osis(ref: str, v11n: str) -> tuple[str, str, int, int]:
    _check(v11n)
    start_s, sep, end_s = ref.partition("-")
    b1, c1, v1 = _point(start_s, False)
    if sep:
        b2, c2, v2 = _point(end_s, True)
    else:
        b2, c2, v2 = _point(start_s, True)
        if _REF.match(start_s).group(3) is not None:  # type: ignore[union-attr]
            b2, c2, v2 = b1, c1, v1
    if b1 != b2:
        raise ValueError(f"cross-book range: {ref!r}")
    o1, o2 = verse_ordinal(b1, c1, v1), verse_ordinal(b2, c2, v2)
    if o1 > o2:
        raise ValueError(f"reversed range: {ref!r}")
    first = f"{b1}.{c1}.{v1}"
    osis = first if o1 == o2 else f"{first}-{b2}.{c2}.{v2}"
    return b1, osis, o1, o2


def canonical(ref: str, v11n: str = V11N) -> str:
    """Canonical passage IRI for an OSIS reference."""
    return BASE + "passage/" + v11n + "/" + _osis(ref, v11n)[1]


def parse(iri_or_ref: str) -> Passage:
    """Parse a canonical IRI or an OSIS reference."""
    text = iri_or_ref
    prefix = BASE + "passage/"
    v11n = V11N
    if text.startswith(prefix):
        v11n, _, text = text[len(prefix):].partition("/")
        book, osis, o1, o2 = _osis(text, v11n)
        if osis != text:
            raise ValueError(f"non-canonical IRI: {iri_or_ref!r}")
    else:
        book, osis, o1, o2 = _osis(text, v11n)
    return Passage(v11n, book, osis, o1, o2)
