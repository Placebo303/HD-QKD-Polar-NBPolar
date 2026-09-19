# P20N Pre-RESULT review (independent; before acceptance/publication)

- Reviewer: `reviewer-go` (independent subagent), session `ses_f47de58a6ffeXDdb5E69vrIfzx`, 2026-09-19.
- Scope (`AGENTS.md` §10.3): plan pins/thresholds, per-arm recount, `undetected`
  isolation, instrumentation semantics, accounting/decomposition, disclosure
  recount, non-access, anti-drift, operator-return claims — against the actual
  Stage-B artifacts.
- Verdict: **PASS (PR1–PR7; three non-blocking caveats)**. The Stage-B result
  `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE` may be
  published/accepted as descriptive evidence. (The reviewer accepts nothing.)

## Verdicts (abridged evidence)

| ID | Verdict | Key evidence |
|---|---|---|
| PR1 inventory/freeze identity | PASS | Exactly 5 files (mtimes inside the run window); alt sha `6f4a4f76…2333e78` == freeze/plan/identity pins; prior `372dcc1c…`, order `a9f18a9f…`, K `331/6689/7020`, HOLD `2213..2724` + remainder `2725..2766`, master 2026092300, caps 35164/35164/33509/33509 + 327743; all three input stats before==after. |
| PR2 per-record recount | PASS | 16 unique (arm,block) records; outcomes 2 exact / 14 verify_failed; A 0/4 (@111/76/3/81), B 1/4 (b3 exact; @1009/20/5823), C 0/4 (same as A), D 1/4 (b3 exact); `b_restored_count 1`, `d_restored_count 1`, `b_maintain_count 0`; 14/14 failures L2-layer; tag passes exactly on the 2 exact records; both exact records independently verified (label match, tag pass, key bits 35164 / 33509; public 327743); `undetected` 0 by taxonomy + aggregate (`undetected_count 0`). |
| PR3 instrumentation semantics | PASS (definition artifact, no anomaly) | Field definitions cited (`:1321-1328`, `:1387-1390`, `:1404-1418`); `l2_fail_in_prefix` true on **12/14**, false on 2/14 (B-b2/D-b2 @5823, one shared event); nbhd floor frac `0.0` on all 14; prefix floor frac 0.0001495–0.0013455; alt prefix-hazard means 0.8925–0.9035 vs incumbent 0.7954–0.8556. Adjudication: the field tests an **X-domain** error index for membership in the **U-domain** disclosure set (disclosure pins U; hats are X; code: `operational_f13.py:777-833`, `sc.py:239-262`, `l1_order_1p5m.py:1406-1410`) — a frozen-definition artifact, not a pinning violation. |
| PR4 accounting | PASS | Key `549384 = 8*35164 + 8*33509`; public `5243888 = 16*327743`; SC 24; tags 16; Stage-B sampling 0; recount 0; `integrity_all_pass: true`, `failing_integrity_gates: []` (28 gate keys, all true — the operator's "26/26" is a count slip only, caveat C1). |
| PR5 reads/non-access | PASS | counts 0/0; HOLD 1/1 SPENT (no reopen/retry); attempts 1/1; VAL-remainder 0; 1M refused; 2M never opened/statted/listed; opened==registered (3 paths); `input_stat_unchanged`. |
| PR6 anti-drift | PASS | Single execution (retries 0); frozen mtimes predate the run; pins unedited post-run; no K/order/construction change; writes confined to packet dir + out-dir; no commit; descriptive-only language; honest-scope verbatim. |
| PR7 operator-return claims | PASS | Command byte-identical to `FROZEN_COMMAND`/freeze §5; start/end 05:20:01Z→05:22:45Z, exit 0, wall 164.37 s, RSS 631.2 MB (above the ≲600 MB expectation, below the 2 GiB cap; resource gates PASS); five-file inventory and tables match the jsonl recount. |

## Caveats (non-blocking)

- C1: gate count wording — the summary has 28 gate keys (all true), not 26; count only.
- C2: per-record `undetected` is outcome-valued (no per-record boolean key by schema);
  isolation holds via taxonomy + aggregate `undetected_count 0`.
- C3: state the in-prefix pattern as 12/14 true + 2/14 false (one shared b2 event), not 13/14.

No files were edited by this review; no commit/push; not a self-acceptance.
