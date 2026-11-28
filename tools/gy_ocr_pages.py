"""OCR of arbitrary page ranges of the Gill PDF on goat-yard substrate-v1 (lock item 4, Gill Book II)

Usage: python tools/gy_ocr_pages.py <gill.pdf> <ranges> <out-dir> [--workers N]
       ranges: comma-separated, each "a-b" or a single page "a", e.g. 201-209,214-250. Pages above 895 are refused.

The page-range variant of tools/gy_ocr_baptism.py: same page flow, same region cut, same two Tesseract reads
(stock LSTM text, legacy italic flag), same word fields. No CCEL alignment (every word has "ccel": None), no
candidates, nothing drawn. A page whose split is not ok is recorded in split_failed and skipped.
Lock: docs/handoff/LOCK_item4_gill_book2_2026-11-27.md
Outputs hold corpus text: local only, never commit.
"""

import argparse
import datetime
import json
import math
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import OFFSET, REPO, Fail, bitmap, clean_run, git_state  # noqa: E402
import gy_locate_column_rule as G  # noqa: E402
from gy_ocr_baptism import (  # noqa: E402
    DPI, IOU_MIN, LEGACY_DIR, LEGACY_SHA, PSM, REGIONS, TESSERACT,
    match, parse_hocr, parse_tsv, regions, run_legacy, run_lstm, sha256_file)

MAX_PAGE = 895
LOCK = "docs/handoff/LOCK_item4_gill_book2_2026-11-27.md"


def parse_ranges(s):
    """Pure. "201-209,214" -> sorted unique ints. Fail on empty, malformed, a>b, page < 1 or page > 895."""
    if s is None or not str(s).strip():
        raise Fail("empty page ranges")
    pages = set()
    for part in str(s).split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", part)
        if not m:
            raise Fail(f"malformed range: {part!r}")
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) is not None else a
        if a > b:
            raise Fail(f"range {part!r} has first > last")
        if a < 1:
            raise Fail(f"page {a} < 1")
        if b > MAX_PAGE:
            raise Fail(f"page {b} > {MAX_PAGE}: pages above {MAX_PAGE} are never processed")
        pages.update(range(a, b + 1))
    return sorted(pages)


def check_models():
    if not Path(TESSERACT).is_file():
        raise Fail(f"tesseract not found at {TESSERACT}")
    legacy = LEGACY_DIR / "eng.traineddata"
    if not legacy.is_file():
        raise Fail(f"legacy model missing: {legacy}")
    if sha256_file(legacy) != LEGACY_SHA:
        raise Fail("legacy model sha256 differs")
    stock = Path(TESSERACT).parent / "tessdata" / "eng.traineddata"
    if not stock.is_file():
        raise Fail(f"stock eng.traineddata missing: {stock}")
    return legacy, stock


def run_pages(pages, split_one, ocr_region, workers=6):
    """Core, testable with fakes.
    split_one(p) -> None (no record) | {"status", "reason", "rec", "regions": [{"name","x_off","y_off","image"}]}
    ocr_region(p, region) -> (lstm_words, legacy_words) as parse_tsv / parse_hocr return them.
    -> (splits, split_failed, words). Fails only if every page failed."""
    splits, failed, meta, jobs = {}, {}, {}, []
    for p in pages:
        s = split_one(p)
        if s is None:
            failed[str(p)] = {"status": "no_record", "reason": None}
            continue
        if s.get("status") != "ok":
            failed[str(p)] = {"status": s.get("status"), "reason": s.get("reason")}
            continue
        splits[str(p)] = s["rec"]
        for r in s["regions"]:
            meta[(p, r["name"])] = r
            jobs.append((p, r))
    if not splits:
        raise Fail("every page failed to split")

    def work(job):
        p, r = job
        a, b = ocr_region(p, r)
        return p, r["name"], a, b

    with ThreadPoolExecutor(workers) as ex:
        results = {(p, n): (a, b) for p, n, a, b in ex.map(work, jobs)}
    words = []
    for p in sorted(int(k) for k in splits):
        for name in REGIONS:
            if (p, name) not in results:
                continue
            r = meta[(p, name)]
            lw, hw = results[(p, name)]
            for w in match(lw, hw):
                dx, dy = r["x_off"], r["y_off"]
                b = w["bbox"]
                words.append({"key": f"{p}/{name}/{w['block']}.{w['par']}.{w['line']}.{w['word']}",
                              "page": p, "region": name, "block": w["block"], "par": w["par"],
                              "line": w["line"], "word": w["word"], "text": w["text"], "conf": w["conf"],
                              "bbox": [b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy],
                              "italic": w["italic"], "legacy_iou": w["legacy_iou"],
                              "legacy_text": w["legacy_text"], "ccel": None})
    return splits, failed, words


def summarize(pages, splits, failed, words):
    col = [w for w in words if w["region"] in ("left", "right")]
    matched = sum(1 for w in words if w["italic"] is not None)
    ital = sum(1 for w in words if w["italic"] is True)
    return {
        "pages": len(pages), "split_ok": len(splits), "split_failed": len(failed), "words_total": len(words),
        "words_by_region": {n: sum(1 for w in words if w["region"] == n) for n in REGIONS},
        "column_words": len(col),
        "words_per_page": round(len(words) / len(splits), 1) if splits else None,
        "legacy_matched": matched, "match_frac": round(matched / len(words), 4) if words else None,
        "italic_true": ital, "italic_rate": round(ital / matched, 4) if matched else None,
    }


def main(pdf_path, ranges, out, workers=6):
    import pypdfium2 as pdfium

    pages = parse_ranges(ranges)
    git_start = git_state(REPO)
    legacy, stock = check_models()
    root, BPG, VR = G.goatyard()
    out = Path(out)
    for d in ("pages", "regions", "raw"):
        (out / d).mkdir(parents=True, exist_ok=True)
    config = BPG.build_config(BPG.DEFAULT_UPSCALE, BPG.DEFAULT_FULL_WIDTH_DEPTH,
                              BPG.compute_module_sha256(root / "pipeline" / "scripts" / "cv_footnote_presplit.py"),
                              BPG.get_git_head(root), BPG.get_git_dirty(root))
    pdf = pdfium.PdfDocument(pdf_path)

    def split_one(p):
        grey = np.where(bitmap(pdf, p), 0, 255).astype(np.uint8)
        path = out / "pages" / f"p{p}.png"
        Image.fromarray(grey, mode="L").save(path)
        record, missing = BPG.process_page("bsb-gill", p + OFFSET, path, path.name, "measure", config)
        if missing or record is None:
            return None
        ink = VR.page_ink(np.asarray(Image.open(path).convert("L")))
        split = VR.locate_column_rule(ink, record)
        if split["status"] != "ok":
            return {"status": split["status"], "reason": split.get("reason")}
        mids = [t["y_mid"] for t in split["strips"]]
        rec = {k: v for k, v in split.items() if k != "strips"}
        rec["ytop"] = int(math.floor(min(mids) - VR.RULE_STRIP_PX / 2))
        rec["ybot"] = int(math.ceil(max(mids) + VR.RULE_STRIP_PX / 2))
        return {"status": "ok", "rec": rec,
                "regions": regions(grey, split, VR.RULE_STRIP_PX, VR.left_edge, VR.right_edge)}

    def ocr_region(p, r):
        png = out / "regions" / f"p{p}-{r['name']}.png"
        Image.fromarray(r["image"], mode="L").save(png)
        base = out / "raw" / f"p{p}-{r['name']}"
        t = run_lstm(png, str(base) + ".lstm")
        h = run_legacy(png, str(base) + ".legacy")
        return parse_tsv(t.read_text(encoding="utf-8")), parse_hocr(h.read_text(encoding="utf-8"))

    splits, failed, words = run_pages(pages, split_one, ocr_region, workers)
    summary = summarize(pages, splits, failed, words)
    git_end = git_state(REPO)
    tv = subprocess.run([TESSERACT, "--version"], capture_output=True, text=True)
    header = {"run": "gy-ocr-pages",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__), "pdf_sha256": sha256_file(pdf_path),
              "pages_printed": pages, "ranges": ranges, "pdf_offset": OFFSET,
              "goatyard": {"tag": G.TAG, "commit": G.PINNED},
              "tesseract_version": ((tv.stdout or tv.stderr).splitlines() or [""])[0],
              "lstm_model": {"path": str(stock), "sha256": sha256_file(stock)},
              "legacy_model": {"path": str(legacy), "sha256": LEGACY_SHA},
              "params": {"dpi": DPI, "psm": PSM, "oem_text": 1, "oem_italic": 0, "iou": IOU_MIN,
                         "workers": workers},
              "splits": splits, "split_failed": failed, "lock": LOCK,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    (out / "ocr.json").write_text(json.dumps({"header": header, "summary": summary, "words": words},
                                             indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "README.txt").write_text(
        "LOCAL ONLY. This directory holds corpus text (OCR of the book) and page images. Never commit it.\n"
        "Nothing is drawn here: no candidates, no sample, no CCEL comparison.\n", encoding="utf-8")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("pdf")
    ap.add_argument("ranges")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    try:
        sys.exit(main(a.pdf, a.ranges, a.out, a.workers))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
