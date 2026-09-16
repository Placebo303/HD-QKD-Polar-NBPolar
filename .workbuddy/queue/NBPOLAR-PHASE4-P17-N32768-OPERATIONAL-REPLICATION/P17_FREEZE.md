# P17 freeze — N=32768 operational replication of the P16 f=1.3 gate (Wave-A implementation)

Packet: `NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION` (`TASK_PACKET.md`, 107 lines, frozen).
Predecessor: P16 `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE_ACCEPTED_ZERO_MARGIN`
(main-thread acceptance `ACCEPTED_DEVELOPMENT_SIGNAL_ZERO_COUNT_MARGIN`).
Wave-A scope ONLY: OpenSpec delta + implementation + tests + this freeze.
This document authorizes nothing. No box in `tasks.md` is checked by the implementing session.

## 1. Mission

P16 closed at 62/64 exact with Wilson LB 0.9098711859: a candidate with
zero count margin. P17 resolves that margin with an independent
128-block replication at exactly the same target model, N, construction,
disclosure and protocol. No retraining, no retuning, no pooling of P16
observations into the decision.

## 2. Predecessor identity record (verified before any attempt)

P16 accepted file:
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
(read structure/digest only; P16 immutable, never modified):

| item | verified value |
|---|---|
| protocol | `nbpolar-p16-operational-f13-gate`, frozen before DEV |
| N / K_total / K1 / K2 | 32768 / 6811 / 319 / 6492 |
| L1/L2 orders | valid permutations of length 32768 |
| canonical digest (recomputed here) | `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` |
| stored digest | identical (match) |
| K replay | `floor((1.3*32768*H-64)/5) = 6811`, `319+6492 = 6811` |
| leakage / f | `5*6811+64 = 34119`, `f <= 1.3` from the ratified literals |

Any mismatch stops before any attempt and consumes nothing (refusal
ordering §6). P16 TRAIN streams `2026092000..2003` and DEV streams
`2026092010..2017` are all avoided by the P17 matrix.

## 3. Frozen matrix

| item | frozen value |
|---|---|
| N | 32768 |
| field | GF32, primitive polynomial 37, alpha 2, natural order |
| source / floor / planning f | `1M` / `1e-15` / `1.3` |
| chunk_rows | 512 (production default contract-checked) |
| tag-bits | 64 |
| K1 / K2 / K_total | 319 / 6492 / 6811 (verified file, never recomputed) |
| DEV | streams 2026092030..2037 x 16 blocks = 128, each stream restarts RNG, sample once |
| tag master | DEV stream seed + 10000, domain `nbpolar-p17-operational-replication-seed:<master>:<n>:<block>` (prefix differs from P16's) |
| key-dependent disclosure | `5*(319+6492)+64 = 34119` bits per fully invoked block |
| public control | `10*32768+63 = 327743` bits per invoked tag |
| outcomes | exact / undetected / verify_failed / decode_failed / nonfinite / resource_abort (undetected never success; nonfinite outranks decode_failed) |

## 4. Frozen command (verbatim, P17-05)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2400 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13_replication --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-seeds 2026092030 2026092031 2026092032 2026092033 2026092034 2026092035 2026092036 2026092037 --dev-blocks-per-stream 16 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate
```

All thirteen flags required; no production default. Budgets: 2400 s
external timeout, 2 GiB virtual limit (`ulimit -v 2097152`), 2 GiB RSS
cap, single-thread BLAS/OpenMP + `MALLOC_ARENA_MAX=2`.

## 5. Output root and five-file schema (absent until authorized execution)

Root `.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate/`
is ABSENT (verified §8). Exactly five files, created as stubs BEFORE the
content open, checkpointed after every completed DEV block (same files,
no sidecars): `frozen_plan.json`,
`predecessor_construction_identity.json` (identity scalars + order
heads; full orders stay in the immutable P16 file),
`per_block_outcomes.jsonl` (128 records at completion),
`aggregate_summary.json`, `report.md`.
Predecessor identity/scalars + per-block scalar outcomes only: never
counts, sampled symbols, truth vectors, decoded labels/keys, metric
planes, tag seeds or RNG state (banned-key walk in focused tests). Per
record: wall, RSS HWM, Linux VmPeak/VmSize.

## 6. Gates, labels, consumption and no-rerun rule

Integrity (frozen order): predecessor_construction_identity;
target_population_contract; construction_frozen_before_dev;
dev_coverage_complete (128/128 + exact stream grouping);
streams_disjoint_frozen; orders_valid_k_replay_f_within_budget;
buckets_disjoint_exhaustive; truth_isolation; undetected_zero;
nonfinite_zero; no_unregistered_calls (SC attempts recomputed from
records; the only counter is `sc` — no second counter exists);
disclosure_recount_exact; attempt_read_accounting_exact;
resource_limits_met_and_no_abort.
Scientific (P17's 128 blocks only): exact `>= 121/128` AND one-sided
95% Wilson LB `>= 0.90`. Frozen boundary values (verified in code before
DEV and in tests): 121/128 → `0.9021084760` (pass), 120/128 →
`0.8924595822` (fail). The recovery total is pinned to 128, so P16's
62/64 is structurally excluded from every gate input; it appears in
`report.md` discussion only with an explicit never-pooled statement.
Labels: `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE` /
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_NOT_CONFIRMED` /
`BLOCKED(<earliest gate>)`.

Consumption: artifact read 1/1 + scientific attempt 1/1 together at the
first NPZ content open; module-level reopen guard; post-open failure is
BLOCKED with consumption spent. Refusal ordering (all before the open,
consuming nothing): absent root → CLI parse → digest-flag pin →
predecessor identity → contracts/grouping. After content open: no
repair, rerun, seed/N/K/floor/order/threshold/tag change or tuning.

## 7. Forbidden paths and scope boundary

Forbidden in this gate: Model-F/HOLD/raw/real/EVAL access, other N,
any construction path, BEC arm, adaptive retry, FWHT/APP/SCL decoders,
second tag, oracle/comparator/rescue paths, P12-P16 code modification,
old-root modification, official prior-seed reuse, `results/` or
`comparison_bench/outputs_comparison/` writes, commit/push. The runner
holds zero TRAIN/genie tokens by construction (focused test). Scope is
operational-but-model-sampled: blocks are sampled from the frozen V25
1M target population, not real frames; planning `f` is not
real-channel efficiency; undetected is never success.

## 8. Wave-A verification evidence (implementation time)

- Output root absent: queue dir holds only `TASK_PACKET.md`,
  `STATUS.yaml`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`,
  `P17_FREEZE.md`, `P17_IMPLEMENTATION_NOTES.md`.
- NPZ stat metadata only: `channel_counts.npz` = 25166822 bytes
  (expected); content never opened (reads/attempts used 0).
- Predecessor digest recomputed in this session: `055c90...c3faea1b`,
  equal to the stored freeze digest and the frozen flag.
- P16 root untouched (read-only stat): five files,
  `construction_and_allocation.json` 2581862 B,
  `aggregate_summary.json` 2586645 B, `frozen_plan.json` 6991 B,
  `per_block_outcomes.jsonl` 42760 B, `report.md` 2529 B.
- Frozen seeds fresh: `2026092030..2037` appear in no `.py` outside
  P17 code/tests; disjoint from P16's twelve streams and all listed
  priors/probes (repo grep + focused test).
- Focused suite: `test_nbpolar_operational_f13_replication.py`, 25/25
  green (fresh /tmp basetemp, pinned interpreter, `-p
  no:cacheprovider`).
- Full NB-Polar suite: 383 tests green (same settings);
  baseline before this wave 358, all green.
- HEAD unchanged at `ab173f2a`; no commit (worktree carries only
  pre-existing unrelated modifications plus this wave's untracked
  additions).
