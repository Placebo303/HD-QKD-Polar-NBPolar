# P20O Pre-RESULT review (independent; before acceptance/publication)

- Reviewer: `reviewer-go` (independent subagent), session `ses_f46d1de2dffeuf2NvfKKrLeJ9W`, 2026-09-19.
- Scope (`AGENTS.md` §10.3): plan pins/thresholds, per-arm recount, `undetected`
  isolation, instrumentation semantics, accounting/decomposition, disclosure recount,
  non-access, anti-drift, operator-return claims — against the actual Stage-B artifacts.
- Verdict: **PASS (PR1–PR7 all PASS)** — the Stage-B result may be published/accepted as
  descriptive evidence. (The reviewer accepts nothing.)

Read-accounting honored: no open/stat/listing of protected content; verification from
packet artifacts + code only.

## Verdicts (abridged evidence)

| ID | Verdict | Key evidence |
|---|---|---|
| PR1 inventory/freeze identity | PASS | Five files (20 records); pins match the freeze (prior canonical `b16f5216…`, alt `98e25495…`, order `b2255449…`, K `334/6746/7080`, budget literal 7080, VAL DEV `2187..2826` + remainder `2827..2915`, master 2026092310, caps `35464/35464/33794/33794` + 327743, totals `692580/6554860`, `hazard_fields` 9 with U-domain PRESENT); identity json: all digests verified, recomputed H within 2e-16 (≤1e-12), `p1`-equality 0.0, stats unchanged. |
| PR2 per-record recount | PASS | 20 unique (block,arm) records; **A 0/5, B 2/5 (b1 `2315..2442`, b2 `2443..2570`), C 0/5, D 3/5 (b1, b2, b4 `2699..2826`)**; exact 5 / verify_failed 15; `b_restored 2` (b1,b2), `b_maintained 0`, `d_restored 3`, `d_maintained 0`; A→B `0/0/2/3`; first-error layers per operator (b0 L1/L1/L2/L2 @6834/6834/78/121; b1 L2@45; b2 L2@153; b3 L2×4; b4 L1/L1/L2 @14296/14296/274); tag/label passes exactly on the 5 exact records; key bits 35464/33794, public 327743; `undetected` 0 isolated; nonfinite/decode_failed/resource_abort 0; truth-leak false ×20. |
| PR3 instrumentation (nine scalars) | PASS — P20N ambiguity closed | 11 L2-fail records: X-prefix true ×11, **U-domain false ×11**; the 9 other records have fail-conditional scalars null, prefix scalars present; `hazard_instrumentation_complete: true`. Code path verified (`polar_transform(low_hat)` vs `view['u2']` prefix membership; same K2 mask). Conclusion: the first errors sit at naturally-indexed positions whose U-domain rank ≥ K2 → genuine undisclosed-region SC errors, **not** disclosure-pinning violations. Recording-only post-decode; sentinel green. |
| PR4 integrity gates | PASS | `integrity_all_pass: true`, `failing_integrity_gates: []`, **29 gate keys** (operator return says "28/28" — count slip only); spot-verified identity/exclusion/isolation/recount/resource gates from raw records. |
| PR5 accounting | PASS | key `692580 = 10*35464 + 10*33794` (per-record actuals; the main thread's delegation-text parenthetical `8*…+8*…` appears in NO artifact — erratum only); public `6554860 = 20*327743`; SC 30/30; tags 20/20; sampling 0; recount 0. |
| PR6 reads/non-access | PASS | counts 1/1 unchanged (no second open); VAL-DEV 1/1 SPENT; attempts 1/1 SPENT; remainder 0; HOLD 0; 1M/1.5M 0; opened==registered (3 paths); no reopen/retry; stats before==after. |
| PR7 anti-drift + claims | PASS | Single execution (10:12:10Z→10:15:45Z, exit 0, wall 215 s external / 208.56 s runner, RSS ≤ 651 MiB); pasted command byte-identical to `FROZEN_COMMAND`/freeze §8; pins unedited post-run; writes confined; no commit; label + report language descriptive-only; honest scope verbatim. |

## Caveats (non-blocking)

- Gate-count wording: 29 keys (all true), not 28.
- `undetected` per-record key absent by schema; isolation holds via outcome vocabulary +
  `undetected_zero: true`.
- Recomputed H last-bit diff ~2e-16 (within frozen 1e-12).
- b4-B `hard_l2_exact: true` under `verify_failed` (L1 failed) — correct endpoint
  separation, not an anomaly.
- Main-thread delegation parenthetical erratum (`8+8`) — no artifact carries it.

No files were edited by this review; no commit/push; not a self-acceptance.
