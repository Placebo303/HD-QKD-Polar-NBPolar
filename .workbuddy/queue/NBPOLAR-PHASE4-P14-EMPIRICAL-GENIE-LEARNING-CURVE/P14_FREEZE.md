# P14 FREEZE — empirical-genie construction learning curve (implementation)

Packet: `NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE` (Tier-Y).
Predecessor: `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED_ACCEPTED` (P13).
Scope of this document: Wave-A implementation freeze (OpenSpec delta +
thin runner + focused tests). The gate has NOT been executed. This
document authorizes nothing; execution requires explicit user
authorization plus an independent reviewer-go Pre-EXECUTE PASS.

## 1. Mission

At P13's N=16384 point, determine whether failure to reach the f=1.3
residual target (P13 DEV UCB 0.2524893538319819 at N=16384, far above
0.01) was materially caused by constructing from only eight TRAIN
blocks. Build nested 8/16/32/64/128-block constructions from one
128-block TRAIN sequence and evaluate all five on the same independent
32 DEV blocks. Model-sampled genie construction diagnostic only — not
operational FER, not real-data qualification.

## 2. Frozen matrix

- N = 16384 (only; any other N is refused before the content open).
- GF(32), primitive polynomial 37, alpha 2, natural order; chunk_rows = 512.
- Target f = 1.3; floor = 1e-15; source = 1M.
- TRAIN streams `2026091930..2026091937` x 16 blocks each = 128 blocks,
  stream-major order (seed ascending, then block index ascending; one
  RNG per stream restarted per stream).
- DEV streams `2026091940..2026091943` x 8 blocks each = 32 blocks.
- Nested prefixes B = 8, 16, 32, 64, 128 from the one TRAIN sequence.
- Each TRAIN block decoded ONCE per layer; running risk sums serve every
  applicable prefix (no repeated calls). Each DEV block decoded ONCE per
  layer; its genie rows score ALL FIVE frozen constructions.
- Planned genie calls = 2 x (128 + 32) = 320 (asserted in code).
- Sampling, L1 true-prefix genie and oracle-conditioned L2 genie are
  exactly P13 (shared helpers, not reimplemented).

## 3. K_total = 3399 verification

`K_total = floor((1.3*N*(H1+H2)-64)/5)` with the ratified literals:

| H spelling | H | raw = (1.3*16384*H-64)/5 | floor |
|---|---|---|---|
| H1+H2 | 0.8010378248977231 | 3399.492968012317 | 3399 |
| EXPECTED_TOTAL | 0.8010378248977232 | 3399.4929680123178 | 3399 |

`budget_k_total(16384, H, 1.3) == 3399` under both spellings (far from
any integer boundary); leakage `5*3399+64 = 17059 <= 1.3*16384*H`.
Same value as P13's accepted N=16384 cell. Pinned by
`test_frozen_k_total_pinned_3399`.

## 4. Five prefixes

For each B in (8, 16, 32, 64, 128): pool TRAIN means from the running
sums over the first B blocks, worst-first `(e,h,index)` orders per
layer, exhaustive `(K1,K2)` lexicographic `(TRAIN residual, K1, K2)`
selection with K_total = 3399, freeze `{k1, k2, residual, orders,
pooled means, freeze_sha256}` before the first DEV call. Other prefixes
diagnose learning only; only B=128 decides.

## 5. Exact verbatim command (frozen P14-06; NOT run in this wave)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_learning_curve --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n 16384 --train-seeds 2026091930 2026091931 2026091932 2026091933 2026091934 2026091935 2026091936 2026091937 --train-blocks-per-stream 16 --prefix-blocks 8 16 32 64 128 --dev-seeds 2026091940 2026091941 2026091942 2026091943 --dev-blocks-per-stream 8 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate
```

All twelve flags required; no production default. Any deviation in
`--n` (must be 16384), `--prefix-blocks` (must be `8 16 32 64 128`),
`--train-blocks-per-stream` (16), `--dev-blocks-per-stream` (8),
`--chunk-rows` (512), seed counts/shape (eight TRAIN + four DEV,
distinct within, disjoint across) or CLI parse is refused BEFORE the
NPZ content open with zero genie calls and no output root created.

## 6. Absent root, five-file schema, per-block checkpointing

Target root (ABSENT at freeze time; verified 2026-09-15, queue dir holds
only the four frozen packet files):
`.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/`

Exactly five files, created as stubs BEFORE the content open and
checkpointed (same files rewritten) after EVERY TRAIN and DEV block
(160 checkpoints, no sidecars):

1. `frozen_plan.json` — protocol, matrix, literals, K_total from
   literals (3399), gate order, decision rule, budgets, frozen command.
2. `learning_curve_constructions.json` — n, k_total,
   `frozen_before_first_dev`, per-prefix `{b, train_blocks_used, k1,
   k2, train_residual, leakage_bits, f, l1_order, l2_order,
   pooled_e1/h1/e2/h2_mean, freeze_sha256}`.
3. `per_block_genie_residuals.jsonl` — 32 lines, one per DEV block:
   `{n, stream_seed, block_index, r_8, r_16, r_32, r_64, r_128, error}`.
4. `aggregate_summary.json` — entropy, constructions digest, per-prefix
   DEV stats, paired `R_B-R_8` + adjacent-step stats, report-only
   diagnostics, 13 integrity booleans, outcome label, resources,
   attempt/read accounting.
5. `report.md` — human-readable rendering of the same facts.

Pooled risks/public orders + scalar block stats only. Never persisted:
counts, sampled symbols, truth vectors, decoder outputs, metric planes,
RNG state. Per run: wall, RSS HWM, Linux VmPeak/VmSize.

## 7. Gates and labels

13 integrity gates (persisted booleans, all required):
`target_population_contract`, `one_n_cell_complete` (128 TRAIN used both
layers + 32 DEV records, zero errors), `nested_prefixes_exact` (exact
8/16/32/64/128 set with train_blocks_used == B),
`streams_disjoint_frozen` (exact frozen seed tuples + disjoint),
`orders_valid_frozen_before_dev` (five permutations + freeze-SHA replay),
`budget_allocation_reproduced` (K_total == 3399 from literals + per-prefix
split replay within 1e-9), `risks_finite`, `zero_genie_exceptions`,
`truth_isolation` (L1 PRIOR_ONLY / L2 ORACLE_CONDITIONED, zero
violations), `no_unregistered_calls` (exactly 320 at final, <= during),
`checkpoint_accounting_consistent` (five files + JSONL lines ==
records), `attempt_read_accounting_exact`, `resource_limits_met_and_no_abort`.

Classification (code implements, main thread adjudicates):
- B=128 DEV UCB <= 0.01 →
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_CANDIDATE`
- integrity pass but UCB > 0.01 →
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED`
- earliest integrity/resource failure → `BLOCKED(<gate>)`
  (t-UCB factor 1.695518782, df=31, one-sided 95%).

## 8. Consumption point and refusal ordering

Artifact read 1/1 + scientific attempt 1/1 are consumed TOGETHER at the
first NPZ content open (`load_v25_channel_counts`); module-level reopen
guard refuses a second NPZ-mode call. Refusals BEFORE the open (zero
consumption, zero genie calls, no root): existing root, CLI parse,
chunk/n/prefix/bps/seed-shape contract. Post-open failure (including
precondition mismatch with zero genie calls): BLOCKED with consumption
spent, best-effort BLOCKED stubs, never a fresh root, never a rerun.
MemoryError around the FULL post-open pipeline: checkpoints preserved,
BLOCKED summary finalized if possible, resource error raised, never
rerun. Post-open: no repair, rerun, seed/prefix/order/allocation/
threshold change or tuning.

## 9. No-rerun rule and budgets

One attempt only. After content open: no rerun or retry for semantic
(prompt/contract/integrity) or resource failure. Budgets: 2 GiB virtual
(`ulimit -v 2097152`), 1800 s external timeout, single-thread
BLAS/OpenMP + `MALLOC_ARENA_MAX=2`. Projection from accepted P13
evidence (its N=16384 cell: 40 blocks in 291.8 s, i.e. ~7.3 s/block):
160 blocks x ~7.3 s ~= 1170 s — inside 1800 s but with less headroom
than P13 (28% -> ~65% of budget). Pre-EXECUTE owns the adequacy verdict;
an overrun BLOCKEDs with evidence preserved (per-block checkpoints).

## 10. P13-reference-only statement

P13's B=8 construction is a historical reference ONLY. P14's TRAIN/DEV
streams (1930..1943) are disjoint from all P13 streams (1860..1913);
P13's different-seed blocks are never merged into P14 statistics and
equality with any P13 value is never required by any gate.

## 11. Forbidden paths (this wave touched none)

Model-F/HOLD artifact, raw/held-out/real frames, EVAL, tag/Toeplitz
(any), FWHT/APP/SCL, operational decode, other N, official prior seeds,
P13 code/evidence, old evidence roots, `results/`,
`comparison_bench/outputs_comparison/`, commit/push. The runner module
contains no functional reference to any of these (pinned by
`test_no_production_raw_hold_access_rule`). The NPZ was stat-only
(25166822 bytes, metadata, never opened): reads 0/1, attempts 0/1.

## 12. Proxy boundary

Every residual `R_B` is a genie union-bound construction proxy: sums of
undisclosed-coordinate genie error risks. It is NOT operational FER,
NOT a real-channel result, and NOT proof of any minimum N or TRAIN
size. No FER/efficiency/key-rate/qualification/promotion claim is
authorized by any P14 artifact.

## 13. Freeze verification evidence (2026-09-15, this wave)

- Gate root absent: queue dir lists only `AUTHORIZATION_PROMPT.md`,
  `PROMPT.md`, `STATUS.yaml`, `TASK_PACKET.md`.
- NPZ stat-only: 25166822 bytes (expected 25166822); content never
  opened (module `_NPZ_CONTENT_OPENED` False in all tests; STATUS
  reads/attempts used 0).
- Frozen-seed freshness: repo-wide grep for `202609193[0-7]` /
  `202609194[0-3]` hits ONLY the frozen P14 packet files
  (`AUTHORIZATION_PROMPT.md`, `TASK_PACKET.md`) plus Wave-A additions
  (runner, focused tests as pinned constants, this spec delta).
  Disjoint from all P7-P13/probe/test seeds (full-seed census in
  implementation notes).
- Focused suite: 15/15 pass. Full NB-Polar suite: 320/320 pass
  (305 pre-existing + 15 new), pinned interpreter
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q
  -p no:cacheprovider`, fresh /tmp basetemps.
- HEAD `ab173f2a` unchanged by this wave; no commit/push (worktree was
  already dirty before this wave from prior phases; Wave-A touched only
  the files listed in §14).
- STATUS.yaml: `execution_authorized: true`, reads/attempts used 0,
  result null, reviews pending, state
  `IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`, next gate
  `INDEPENDENT_PRE_EXECUTE`.

## 14. Wave-A changed files (deltas only; boxes unchecked)

1. `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p14/spec.md`
   (new P14 delta; no production behavior authorized by docs).
2. `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (P14 section
   appended only; all boxes UNCHECKED — Wave-A never checks its own boxes).
3. `comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_learning_curve.py`
   (new thin runner; no other source file touched, no export change needed).
4. `comparison_bench/tests/test_nbpolar_empirical_genie_learning_curve.py`
   (new focused tests, 15 tests).
5. `.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/P14_FREEZE.md`
   (this file) + `P14_IMPLEMENTATION_NOTES.md` (new).
6. `.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/STATUS.yaml`
   (updated authorization/state/accounting fields only).

## 15. Review items flagged for independent Pre-EXECUTE

1. Budget headroom (§9): ~1170 s projected vs 1800 s limit; confirm.
2. Exact frozen command/flag grouping (§5) and absent root re-check at
   execution time (root must still be absent).
3. K_total=3399 from literals (§3) vs run-time recomputation from
   measured H (floor stable; 1e-12 literal tolerance cannot flip it —
   raw is 0.007 from the next integer).
4. Implementation errata found and fixed by tests during Wave-A (see
   implementation notes §4): string-sorted prefix-key comparisons
   (would have failed three gates permanently); run-K vs literal-K gate
   conjunct (would have failed only on injected data, never the frozen
   run); test-side tmpdir/indentation and RNG-logging issues (no
   production impact).
