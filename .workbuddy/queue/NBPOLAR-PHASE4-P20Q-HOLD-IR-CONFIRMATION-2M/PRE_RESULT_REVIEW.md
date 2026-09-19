# P20Q Pre-RESULT review (2026-09-19, independent reviewer-go — PASS)

Scope: five-file evidence root `l2_alt_hold_ir_2m/` (frozen_plan.json, input_and_predecessor_identity.json, per_block_arm_outcomes.jsonl — 20 records, aggregate_summary.json, report.md) vs OPERATOR_RETURN.md claims. No re-execution, no protected-source opens beyond the evidence root, no `git show HEAD:` blobs for evidence paths.

1. Plan-threshold fidelity PASS — label `TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE` exact; descriptive counts only + explicit no-recovery/FER/superiority/qualification disclaimers.
2. Leakage decomposition PASS — per-record A/B 35464, C/D 33794, public 327743 recomputed; totals 692580/6554860 exact, Δ0 on all 20, recount mismatch 0.
3. `undetected` isolation PASS — outcomes exact (8) / verify_failed (12) only; undetected 0 / nonfinite 0 as separate counters, never merged into success.
4. Per-source breakdown PASS — 4 arms × 5 records separated; operational aggregate excludes oracle; C/D deployable=false, diagnostic-only.
5. Disclosure accounting PASS — per-record key/public/tag on all 20; tags 20/20, tag_pass 8/20 with tag_pass==exact on every record.
6. Nine-scalar + IR-1..IR-5 PASS — nine scalars 0 missing with frozen nullability; IR-1 65/64/64 mass 32768, IR-2 12 vals/8 nulls, IR-3 lo==prefix-mean hi==2xlo, IR-4 16 ranks 1..16, IR-5 4096+4096 truncated, all on 20/20; H2 quantities suppliable; no H2 verdict in artifacts.
7. Truth-isolation PASS — truth_isolation gate true, truth_leak_violation false 20/20; oracle_truth_use True only on 10 oracle records.
8. One-shot semantics PASS — attempts 1/1, counts 0/0, HOLD-DEV 1/1, VAL 0, reopen false/retries 0, sampling 0+0; five-file root only; no commit/push.
9. Honest-scope statement PASS — OPERATOR_RETURN §11 whitespace-normalized-identical to packet §0.
10. Return-vs-artifacts PASS — per-arm counts, A→B/C→D {0,0,4,1}, recount totals, 30-gate set-equal/all-true, wall/RSS/SC/tags/IR-2 medians recomputed exact.

Non-blocking: D-exact pair_exact=None is expected oracle separation; STATUS `state` string cosmetic lag (fixed at acceptance); per-record wall_s slices vs aggregate wall_s are different scopes (peak RSS 650346496 B ≈ 620 MiB consistent).
