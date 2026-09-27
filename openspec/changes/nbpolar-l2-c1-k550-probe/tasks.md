# Tasks: `nbpolar-l2-c1-k550-probe`

- [x] C1-P1 — Record the exact single-factor C1 delta and all no-claim, no-data, no-rerun, and no-auto-continuation boundaries in OpenSpec.
- [x] C1-P2 — Freeze the three-line `prereg.md` with exact command and every main-thread parameter.
- [x] C1-P3 — Prepare a runnable `run.py` mechanically derived from the k550 predecessor; change only the C1 construction, identifiers, seeds, output/cache paths, and probe-id text, and remove C3-only e2/h2 accounting. Do not invoke `main()` or create `results.json`.
- [x] C1-P4 — Prepare the packet, operator prompt, authorization record, and status. Record the user's broad authorization while leaving execution pending main-thread freeze review.
- [x] C1-P5 — Run T0 syntax/import/structural/tiny-order checks only. No design MC, decoder, or smoke execution. T0 import created an empty scoped `.numba_cache` directory; this side effect is recorded in STATUS, with no result file.

## Execution is outside this change

Execution requires a separate main-thread freeze review of this complete packet, the exact prereg command, target-output absence, and write scope. This change does not auto-start the probe or authorize a successor route.
