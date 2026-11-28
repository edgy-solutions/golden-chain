# Findings: item 6, the second typeface (2026-11-27)

- **From:** the build agent, 2026-11-27.
- **Lock:** [LOCK_item6_second_typeface_2026-11-27.md](LOCK_item6_second_typeface_2026-11-27.md) (`65942f5`), committed before any request.
- **Result: the fetch is refused, so the item stops.** No other route was tried, as the order and the lock require.

## What was requested

Two requests in all, on 2026-11-27, with a generic client name and no personal detail:

1. `https://goatyardarchive.org/robots.txt`: HTTP 200.
2. `https://goatyardarchive.org/scans`: HTTP 200. It is the shell page (958 bytes) of a script-driven site. It holds no listing, so the listing would have needed the site's own API.

No scan file was requested, and none is held. No image was viewed.

## Why it is a refusal

- The `User-agent: *` group allows `/`. It carries `Content-Signal: search=yes,ai-train=no,use=reference`.
- The same file **disallows `/` for Anthropic's agents by name**: `ClaudeBot`, `anthropic-ai` and `Claude-Web`. It does the same for about thirty other AI crawlers.
- The build agent is an Anthropic model. Fetching under a generic client name, when the site has refused Anthropic's agents by name, would be working around a refusal. So it is recorded as one.
- The robots file was fetched first, but only its opening lines were read before the shell page was requested. The per-agent groups were read in full after that second request. The second request is recorded here, and nothing in it is used.

## The lock, scored (never edited)

| # | Result |
|---|---|
| E1 | **Missed.** The site refuses Anthropic's agents by name. |
| E2-E7 | Not measured. No page was fetched. |
| E8 | Not measured. No tool was written for this item (`tools/gy_ocr_scans.py` does not exist). |

## What waits

- **On Chris or the architect:** the scans could still be measured another way:
  - Chris downloads the twenty FILE pages (chosen by the lock's rule) and places them in a local folder; or
  - the site's operator grants access in writing.

  Either is for Chris and the architect to decide. The build agent does not ask the site for it.
- The local probe folder `~/.golden-chain/item6-scans/probe/` holds only `robots.txt` and the shell page. It is never committed.
