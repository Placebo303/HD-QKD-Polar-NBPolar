# P20T Pre-RESULT review (2026-09-20, independent reviewer-go — PASS)

Scope: 15-file evidence root `n8192_persistence_probe_2m/` (frozen_plan.json, input_and_predecessor_identity.json, per_block_arm_outcomes.jsonl — 3 records, aggregate_summary.json, report.md, ir5_full_manifest.json + nine IR-5 .bin) vs OPERATOR_RETURN.md claims. No re-execution, no protected-source opens beyond the evidence root, no `git show HEAD:` blobs for evidence paths.

1. Plan-threshold fidelity PASS — outcome label `TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE`; FER/recovery/Wilson/superiority/scaling only as negated disclaimers; `transition_cells_computed: false`.
2. Q-G1/Q-G2 geometry PASS — every record carries fail coord/layer/hazard/rank/domain/nbhd/floor + IR-1/IR-2/IR-3/IR-4; asked-not-decided, no votes, no recovery-rate reading.
3. Leakage decomposition PASS — recomputed 8864+8864+8444=26172 and 81983×3=245949 match per-record actuals; A/B Δ0; `recount_mismatch: 0`.
4. `undetected` isolation PASS — `undetected_count: 0`, `nonfinite_count: 0`, all `verify_failed`; gates `undetected_zero`/`nonfinite_zero`/`truth_isolation` true; never merged into success.
5. Per-source breakdown PASS — A `66aefea8…` / B `355a32d3…` / O `66aefea8…`; O `deployable:false`, excluded from operational aggregates.
6. Recorders PASS — nine scalars arm-specific + IR-1 65-edge + IR-2 rank + IR-3 exactly 1.0×/2.0× + IR-4 top-16 + IR-5 uncapped 8192 f32le + 2×8192 u8 with `ir5full-v1` manifest SHA-match; recording-only, truth isolation true.
7. One-shot semantics PASS — attempts 1/1, DEV 1/1, counts 0/0, 1M/1.5M/2M-non-DEV 0, sampling 0, SC 5/5, tags 3/3; no overwrite `results/`/`outputs_comparison/`; no commit/push.
8. Honest-scope verbatim PASS — §7 repeats §0 (line-breaks only); `cross_n_inference:false`, `within_n_only:true`; no cross-N, no H2.
9. Return-vs-artifacts PASS — A193/B3/O193, IR-2 0.4001/0.0500, IR-4 4/3/4 with byte-identical coords, recount 26172/245949, 31/31 gates, wall 8.36 s / RSS ~350 MiB all match.
10. N=8192 derivation integrity PASS — digests `b16f5216`/`d77466ec`/`66aefea8`/`355a32d3` replay-exact; K 1760/84/1676 + budget literal; set-delta 963/963 ∩713 Δ0; no N=32768 literal carried.

Non-blocking: per-record JSONL carries no explicit `undetected` key (isolation via aggregate count + gate); `32768` byte-size text collides with N=32768 (benign; annotate bytes as 8192×4 in future manifests); record-wall sum vs total wall is unremarked overhead, no ceiling impact.
