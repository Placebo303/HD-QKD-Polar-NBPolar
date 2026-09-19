# P20R Pre-RESULT review (2026-09-19, independent reviewer-go — PASS)

Scope: five-file evidence root `l2_order_position_1p5m/` (frozen_plan.json, input_and_predecessor_identity.json, per_block_arm_outcomes.jsonl — 4 records, aggregate_summary.json, report.md) vs OPERATOR_RETURN.md claims. No re-execution, no protected-source opens beyond the evidence root, no `git show HEAD:` blobs for evidence paths.

1. Plan-threshold fidelity PASS — outcome label `TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE` in aggregate+report; FER/recovery/superiority/Wilson only as negated disclaimers.
2. Leakage decomposition PASS — recomputed 2*35164+2*33509=137346 and 4*327743=1310972 match per-record actuals; caps Δ0; recount_mismatch 0.
3. `undetected` isolation PASS — undetected 0, nonfinite 0, 4/4 verify_failed, nothing merged; claim_scope states undetected never success.
4. Per-source breakdown PASS — A/C digest a9f18a9f vs B/D c7853286 arm-separated; C/D deployable false, oracle_control true, excluded from operational aggregates.
5. Disclosure accounting PASS — per-record key/public/tag fields; tag_invoked 4/4, tag_pass 0/4 consistent; recount_mismatch 0.
6. Nine-scalar + IR-1..IR-5 PASS — nine scalars 4/4; IR-1 65 edges/64+64, IR-2 rank pct, IR-3 exactly 1.0x/2.0x mean-exact, IR-4 top-16 ranks 1-16, IR-5 4096 truncated true len 32768; no H2 verdict strings.
7. Truth-isolation PASS — truth_isolation gate true, truth_leak_violation false 4/4; IR recording-only boundary per packet.
8. One-shot semantics PASS — attempts 1/1 reopen false retries 0; counts 0/0, DEV 1/1, VAL-DEV/HOLD/1M/2M 0; five-file root exact; pie_grid.csv mtime 19:36 predates 23:22 run, zero content diff; untracked queue dir, no commit/push.
9. Honest-scope verbatim PASS — §0 sentence byte-verbatim (python substring match) in OPERATOR_RETURN.md §9.
10. Return-vs-artifacts PASS — per-arm 0/1, tables 0/0/0/1, set-delta K2 6689/int 1213/5476/5476/delta 0, IR-2 medians A 0.99966/B 0.32919/all 0.66442, 34/34 gates, wall 44.368862 s/RSS 546258944 B recomputed exact.
11. First-error sanity PASS — A 133 L2 in-prefix-U-out vs B 0 L2 out-of-prefix; C 133/D 0 mirror; orders frozen pre-execution, no post-hoc selection.

Non-blocking: wall/RSS rounding only; outcome label lives in aggregate+report per §9 design; pie_grid.csv stat-dirty pre-existing unrelated.
