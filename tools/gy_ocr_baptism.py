"""OCR of the baptism chapter (BSB pp. 896-915) on goat-yard substrate-v1 (overnight order, item 6)

Usage: python tools/gy_ocr_baptism.py <gill.pdf> <first> <last> <ccel-practical.txt> <out-dir> [--workers N]

Per page: the native embedded image as grey (ink 0, paper 255), goat-yard's process_page / page_ink /
locate_column_rule (consumed unchanged through tools/gy_locate_column_rule.goatyard(); nothing is copied;
ink_box is not used). The page is cut into head, left, right and foot regions around the located rule
(left/right with the rule side whitened along the slanted edge). Each region is read twice by Tesseract:
stock LSTM (text, TSV) and the legacy 4.1.0 engine (italic flag, hOCR with font info); words are matched
by bbox IoU. Column words get an agree/differ/unaligned flag against the CCEL text (flag only; the CCEL
text is never stored). 100 flagged-italic and 100 unflagged words are drawn by sha256(key) as the
candidate truth set (rows unsigned).
Prediction: ~/.golden-chain/item6-ocr-baptism-predictions-locked.txt
Outputs hold corpus text: local only, never commit.
"""

import argparse
import datetime
import difflib
import hashlib
import html
import json
import math
import os
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

TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
LEGACY_DIR = Path.home() / ".golden-chain" / "tessdata-4.1.0"
LEGACY_SHA = "daa0c97d651c19fba3b25e81317cd697e9908c8208090c94c3905381c23fc047"
CCEL_SHA = "81697d63c76ee781ebee84e722260f3286d294cb7a5780953ba92568df82d649"
CCEL_LINES = (16170, 17760)
CCEL_URL = "https://www.ccel.org/ccel/g/gill/practical/cache/practical.txt"
DPI = 850
PSM = 4
N_CANDIDATES = 100
IOU_MIN = 0.5
TIMEOUT = 900
PREDICTION = "~/.golden-chain/item6-ocr-baptism-predictions-locked.txt"
REGIONS = ("head", "left", "right", "foot")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def regions(grey, split, strip_px, left_edge, right_edge):
    """Pure. head / foot above and below the rule strips; left / right with the rule side whitened."""
    H, W = grey.shape
    mids = [t["y_mid"] for t in split["strips"]]
    ytop = max(0, int(math.floor(min(mids) - strip_px / 2)))
    ybot = min(H, int(math.ceil(max(mids) + strip_px / 2)))
    out = []

    def add(name, x_off, y_off, img):
        if img.shape[0] == 0 or img.shape[1] == 0 or not (img < 128).any():
            return
        out.append({"name": name, "x_off": x_off, "y_off": y_off, "image": img})

    add("head", 0, 0, grey[0:ytop, :].copy())
    ys = range(ytop, ybot)
    les = [left_edge(split, y) for y in ys]
    res = [right_edge(split, y) for y in ys]
    if les:
        xe = min(W, int(math.ceil(max(les))) + 1)
        img = grey[ytop:ybot, 0:xe].copy()
        for i, le in enumerate(les):
            img[i, np.arange(xe) >= le] = 255
        add("left", 0, ytop, img)
        xs = max(0, int(math.floor(min(res))))
        img = grey[ytop:ybot, xs:W].copy()
        xx = np.arange(xs, W)
        for i, re_ in enumerate(res):
            img[i, xx <= re_] = 255
        add("right", xs, ytop, img)
    add("foot", 0, ybot, grey[ybot:, :].copy())
    order = {n: i for i, n in enumerate(REGIONS)}
    out.sort(key=lambda r: order[r["name"]])
    return out


def run_tesseract(png, base, extra, tessdata_dir=None, tesseract=TESSERACT):
    cmd = [str(tesseract), str(png), str(base)]
    if tessdata_dir:
        cmd += ["--tessdata-dir", str(tessdata_dir)]
    cmd += extra
    env = dict(os.environ, OMP_THREAD_LIMIT="1")
    try:
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=TIMEOUT)
    except (subprocess.TimeoutExpired, OSError) as e:
        raise Fail(f"tesseract failed on {png}: {e}")
    if r.returncode != 0:
        raise Fail(f"tesseract exit {r.returncode} on {png}: {r.stderr[-300:]}")


def run_lstm(png, base, tesseract=TESSERACT):
    run_tesseract(png, base, ["--oem", "1", "--psm", str(PSM), "--dpi", str(DPI),
                              "-c", "tessedit_create_tsv=1"], tesseract=tesseract)
    return Path(str(base) + ".tsv")


def run_legacy(png, base, tesseract=TESSERACT, tessdata_dir=LEGACY_DIR):
    run_tesseract(png, base, ["--oem", "0", "--psm", str(PSM), "--dpi", str(DPI),
                              "-c", "tessedit_create_hocr=1", "-c", "hocr_font_info=1"],
                  tessdata_dir=tessdata_dir, tesseract=tesseract)
    return Path(str(base) + ".hocr")


def parse_tsv(text):
    words = []
    for line in text.splitlines()[1:]:
        c = line.split("\t")
        if len(c) < 12 or c[0] != "5":
            continue
        t = "\t".join(c[11:]).strip()
        if not t:
            continue
        l, tp, w, h = (int(c[6]), int(c[7]), int(c[8]), int(c[9]))
        words.append({"block": int(c[2]), "par": int(c[3]), "line": int(c[4]), "word": int(c[5]),
                      "conf": float(c[10]), "text": t, "bbox": [l, tp, l + w, tp + h]})
    return words


_WORD = re.compile(r"<span\b([^>]*\bclass=['\"]ocrx_word['\"][^>]*)>(.*?)</span>", re.S)
_TITLE = re.compile(r"\btitle=(['\"])(.*?)\1", re.S)
_BBOX = re.compile(r"\bbbox\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)")
_XFONT = re.compile(r"\bx_font\s+([^;]*)")


def parse_hocr(text):
    words = []
    for m in _WORD.finditer(text):
        tm = _TITLE.search(m.group(1))
        bm = _BBOX.search(tm.group(2)) if tm else None
        if not bm:
            continue
        inner = m.group(2)
        t = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        if not t:
            continue
        fm = _XFONT.search(tm.group(2))
        italic = bool(re.search(r"<em\b", inner)) or bool(fm and "Italic" in fm.group(1))
        words.append({"text": t, "bbox": [int(g) for g in bm.groups()], "italic": italic})
    return words


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def match(lstm_words, legacy_words):
    out = []
    for w in lstm_words:
        best, bi = None, 0.0
        for lw in legacy_words:
            v = iou(w["bbox"], lw["bbox"])
            if v > bi:
                best, bi = lw, v
        r = dict(w)
        if best is not None and bi >= IOU_MIN:
            r.update(italic=best["italic"], legacy_iou=round(bi, 4), legacy_text=best["text"])
        else:
            r.update(italic=None, legacy_iou=round(bi, 4) if best is not None else None, legacy_text=None)
        out.append(r)
    return out


def norm(s):
    return re.sub(r"^[^0-9A-Za-z]+|[^0-9A-Za-z]+$", "", s.lower())


def ccel_flags(ocr_tokens, ccel_tokens):
    """agree / differ / unaligned per OCR token; None for tokens empty after norm."""
    idx = [i for i, t in enumerate(ocr_tokens) if norm(t)]
    a = [norm(ocr_tokens[i]) for i in idx]
    b = [n for n in (norm(t) for t in ccel_tokens) if n]
    flags = [None] * len(ocr_tokens)
    kind = {"equal": "agree", "replace": "differ", "delete": "unaligned"}
    for tag, i1, i2, _j1, _j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag in kind:
            for k in range(i1, i2):
                flags[idx[k]] = kind[tag]
    return flags


def candidates(words, n):
    elig = [w for w in words if w.get("italic") is not None and norm(w["text"])]
    rows = []
    for stratum, flag in (("flagged", True), ("unflagged", False)):
        pool = sorted((w for w in elig if w["italic"] is flag),
                      key=lambda w: hashlib.sha256(w["key"].encode("utf-8")).hexdigest())
        if len(pool) < n:
            raise Fail(f"stratum {stratum} has {len(pool)} eligible words, need {n}")
        for w in pool[:n]:
            rows.append({"key": w["key"], "page": w["page"], "region": w["region"], "bbox": w["bbox"],
                         "text": w["text"], "italic_flag": w["italic"], "ccel": w["ccel"],
                         "stratum": stratum, "signed_italic": None})
    return rows


def check_inputs(ccel_path):
    if not Path(TESSERACT).is_file():
        raise Fail(f"tesseract not found at {TESSERACT}")
    legacy = LEGACY_DIR / "eng.traineddata"
    if not legacy.is_file():
        raise Fail(f"legacy model missing: {legacy}")
    if sha256_file(legacy) != LEGACY_SHA:
        raise Fail("legacy model sha256 differs")
    if not Path(ccel_path).is_file():
        raise Fail(f"CCEL file missing: {ccel_path}")
    if sha256_file(ccel_path) != CCEL_SHA:
        raise Fail("CCEL file sha256 differs")
    stock = Path(TESSERACT).parent / "tessdata" / "eng.traineddata"
    if not stock.is_file():
        raise Fail(f"stock eng.traineddata missing: {stock}")
    return legacy, stock


def main(pdf_path, first, last, ccel_path, out, workers=6):
    import pypdfium2 as pdfium

    git_start = git_state(REPO)
    legacy, stock = check_inputs(ccel_path)
    root, BPG, VR = G.goatyard()
    out = Path(out)
    for d in ("pages", "regions", "raw"):
        (out / d).mkdir(parents=True, exist_ok=True)
    config = BPG.build_config(BPG.DEFAULT_UPSCALE, BPG.DEFAULT_FULL_WIDTH_DEPTH,
                              BPG.compute_module_sha256(root / "pipeline" / "scripts" / "cv_footnote_presplit.py"),
                              BPG.get_git_head(root), BPG.get_git_dirty(root))
    pdf = pdfium.PdfDocument(pdf_path)
    jobs, splits, meta = [], {}, {}
    for p in range(first, last + 1):
        grey = np.where(bitmap(pdf, p), 0, 255).astype(np.uint8)
        path = out / "pages" / f"p{p}.png"
        Image.fromarray(grey, mode="L").save(path)
        record, missing = BPG.process_page("bsb-gill", p + OFFSET, path, path.name, "measure", config)
        if missing or record is None:
            raise Fail(f"p.{p}: image not written")
        ink = VR.page_ink(np.asarray(Image.open(path).convert("L")))
        split = VR.locate_column_rule(ink, record)
        if split["status"] != "ok":
            raise Fail(f"p.{p}: split {split['status']}")
        regs = regions(grey, split, VR.RULE_STRIP_PX, VR.left_edge, VR.right_edge)
        mids = [t["y_mid"] for t in split["strips"]]
        rec = {k: v for k, v in split.items() if k != "strips"}
        rec["ytop"] = int(math.floor(min(mids) - VR.RULE_STRIP_PX / 2))
        rec["ybot"] = int(math.ceil(max(mids) + VR.RULE_STRIP_PX / 2))
        splits[str(p)] = rec
        for r in regs:
            png = out / "regions" / f"p{p}-{r['name']}.png"
            Image.fromarray(r["image"], mode="L").save(png)
            base = out / "raw" / f"p{p}-{r['name']}"
            meta[(p, r["name"])] = r
            jobs.append((p, r["name"], png, base))

    def work(job):
        p, name, png, base = job
        t = run_lstm(png, str(base) + ".lstm")
        h = run_legacy(png, str(base) + ".legacy")
        return p, name, parse_tsv(t.read_text(encoding="utf-8")), parse_hocr(h.read_text(encoding="utf-8"))

    with ThreadPoolExecutor(workers) as ex:
        results = {(p, n): (a, b) for p, n, a, b in ex.map(work, jobs)}

    words = []
    for p in range(first, last + 1):
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
    lines = Path(ccel_path).read_text(encoding="utf-8", errors="replace").splitlines()
    ccel_tokens = " ".join(lines[CCEL_LINES[0] - 1:CCEL_LINES[1]]).split()
    col = [w for w in words if w["region"] in ("left", "right")]
    for w, f in zip(col, ccel_flags([w["text"] for w in col], ccel_tokens)):
        w["ccel"] = f
    cand = candidates(words, N_CANDIDATES)

    cc = {k: sum(1 for w in col if w["ccel"] == k) for k in ("agree", "differ", "unaligned")}
    cc["none"] = sum(1 for w in col if w["ccel"] is None)
    fl = [w for w in col if w["italic"] is True and w["ccel"] is not None]
    matched = sum(1 for w in words if w["italic"] is not None)
    ital = sum(1 for w in words if w["italic"] is True)
    summary = {
        "pages": last - first + 1, "split_ok": len(splits), "words_total": len(words),
        "words_by_region": {n: sum(1 for w in words if w["region"] == n) for n in REGIONS},
        "column_words": len(col),
        "ccel_agree": cc["agree"], "ccel_differ": cc["differ"], "ccel_unaligned": cc["unaligned"],
        "ccel_none": cc["none"],
        "agree_frac": round(sum(1 for w in fl if w["ccel"] == "agree") / len(fl), 4) if fl else None,
        "legacy_matched": matched, "match_frac": round(matched / len(words), 4) if words else None,
        "italic_true": ital, "italic_rate": round(ital / matched, 4) if matched else None,
        "candidates_flagged": sum(1 for r in cand if r["stratum"] == "flagged"),
        "candidates_unflagged": sum(1 for r in cand if r["stratum"] == "unflagged"),
    }
    git_end = git_state(REPO)
    tv = subprocess.run([TESSERACT, "--version"], capture_output=True, text=True)
    header = {"run": "gy-ocr-baptism",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__), "pdf_sha256": sha256_file(pdf_path),
              "pages_printed": [first, last], "pdf_offset": OFFSET,
              "goatyard": {"tag": G.TAG, "commit": G.PINNED},
              "tesseract_version": ((tv.stdout or tv.stderr).splitlines() or [""])[0],
              "lstm_model": {"path": str(stock), "sha256": sha256_file(stock)},
              "legacy_model": {"path": str(legacy), "sha256": LEGACY_SHA},
              "ccel": {"url": CCEL_URL, "sha256": CCEL_SHA, "lines": list(CCEL_LINES)},
              "params": {"dpi": DPI, "psm": PSM, "oem_text": 1, "oem_italic": 0, "iou": IOU_MIN,
                         "workers": workers},
              "splits": splits, "prediction": PREDICTION,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    (out / "ocr.json").write_text(json.dumps({"header": header, "summary": summary, "words": words},
                                             indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "candidates.json").write_text(json.dumps({"header": header, "n": 2 * N_CANDIDATES, "rows": cand},
                                                    indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "README.txt").write_text(
        "LOCAL ONLY. This directory holds corpus text (OCR of the book) and page images. Never commit it.\n"
        "candidates.json is the truth-set candidate list: every signed_italic is null (unsigned) until signed.\n",
        encoding="utf-8")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("pdf")
    ap.add_argument("first", type=int)
    ap.add_argument("last", type=int)
    ap.add_argument("ccel")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    try:
        sys.exit(main(a.pdf, a.first, a.last, a.ccel, a.out, a.workers))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
