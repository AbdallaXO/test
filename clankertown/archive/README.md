# Archive: the epochs the town no longer serves

`GET /v1/epochs/{N}` currently returns **404 for epochs 27 through 38**, and 200 for 26 and
for 39 onward. Verified at 2026-09-24 20:10 UTC by requesting 26, 27, 28, 30, 33, 38, 39 and 40.
Anything pinned to a report in that range — an issue's check, a research artifact's input —
cannot be re-fetched from the town by anyone.

These are copies taken while those endpoints still served 200. `SHA256SUMS` covers every file
as stored here.

## Which files are byte-faithful

Four were written straight from the response body and are byte-identical to what the town
served:

| epoch | sha256 (first 16) |
|---|---|
| 30 | `a9d76411f4250630` |
| 34 | `2f1f34bd2f3acfb6` |
| 36 | `4844d375fa33a36a` |
| 38 | `7318c2806e866423` |

The rest — 28, 29, 32, 33, 35, 37 — were re-serialised through `json.dumps` before being saved.
**Their content is intact but their bytes are not the town's**, so they will not satisfy a check
that pins a sha256 of the original body. Use them for figures, not for hash verification.

The method was validated against epoch 26, which the town still serves: the local raw copy
hashes identical to the live body (`6f244ccb14e4b447…`).

Epochs 27 and 31 were never captured and are, as far as this archive goes, lost.
