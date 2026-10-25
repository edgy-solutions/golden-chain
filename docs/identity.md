# Identity: the golden-chain namespace

| Item | Value |
|---|---|
| Namespace (IRI base) | `https://w3id.org/golden-chain/` |
| Redirect target | `https://golden-chain.org/id/$1` (path preserved) |
| Redirect type | HTTP 302, single catch-all `RewriteRule ^(.*)$` |
| Registry | [perma-id/w3id.org](https://github.com/perma-id/w3id.org) |
| Pull request | [perma-id/w3id.org#6977](https://github.com/perma-id/w3id.org/pull/6977), "golden-chain: add project redirect" |
| PR head | `edgy-solutions/w3id.org`, branch `add-golden-chain` |
| Files in PR | `ids/golden-chain/.htaccess`, `ids/golden-chain/README.md` |
| Status | **Awaiting merge.** Open, mergeable, no reviews or comments (checked 2026-10-25) |
| Front door | `https://golden-chain.org` (registered, not yet served) |

## Content of the submitted redirect (as filed; not edited here)

```apache
RewriteEngine on
RewriteRule ^(.*)$ https://golden-chain.org/id/$1 [R=302,L]
```

## Working rules

- Every IRI in the ontology and data is minted under the base above,
  using the patterns in [ADR-0002](adr/0002-identity.md).
- Mint as if the redirect were live. During phases 0–1 the redirect is
  pending and the site is not served, so IRIs do not resolve. That is
  expected and is not a defect; no test may depend on dereferencing.
- This repo never edits the w3id fork. Changes to the redirect (e.g. content
  negotiation for `text/turtle` once the site serves RDF) are a separate
  PR against perma-id/w3id.org, raised by the maintainer.

## Notes for later

- The redirect has no content negotiation. When golden-chain.org serves
  both HTML and Turtle at `/id/…`, negotiation can happen at the site; the
  w3id rule need not change.
- `302` is the w3id-recommended choice and keeps the target movable.
