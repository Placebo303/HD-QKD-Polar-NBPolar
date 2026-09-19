# P20G Stage-B OPERATOR_RETURN — NBPOLAR-PHASE4-P20G-1P5M-183806 (single attempt, BLOCKED)

- Packet: `NBPOLAR-PHASE4-P20G-1P5M-183806` (Tier-Y). Operator: Stage-B executor, no acceptance authority.
- Preconditions for execution (all verified before the run): branch `codex/nbpolar-phase0` HEAD
  `faac0411` (matches PRE_EXECUTE_REVIEW); STATUS `protected_data_read_authorized: true`,
  `decoder_execution_authorized: true`, `attempts 0/1`; output root `independent_session/` ABSENT
  (stat `No such file or directory`); frozen quad ΔK2=+1024 / 1.5M TRAIN 0..383 + remainder
  384..1659 / caps 34119+39239+32524 key + 327743 public / budget 600 s + 2 GiB + single thread;
  module `FROZEN_COMMAND` printed pre-run with `CONSISTENCY_TRUE= True` against FREEZE §10.
- This return claims nothing beyond what the artifacts show. No FER, no promotion, no efficiency
  language. B2 never operational (never executed). `undetected` does not occur (zero tags).

## 1. Executed command (verbatim FREEZE §10, one shot, no repeat)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && ulimit -v 2097152 && timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_independent_session --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 0 383 --block-frames 128 --remainder-frames 384 1659 --tag-master 2026092210 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/independent_session
```

- Start/end: 2026-09-18 22:22:32 +0800 (all five root files stamped this second; fast fail-closed
  refusal, far inside the 600 s / 2 GiB / single-thread envelope; no resource abort, P20A path
  not triggered).
- Exit: non-zero BLOCKED refusal. Exact process output (single line, quoted verbatim):
  `nbpolar phase4-p20g plus1024 independent session refused: BLOCKED(target_population_contract): failing preconditions: h1_matches_literal,h2_matches_literal,total_matches_literal`
  (numeric exit code was not surfaced by the execution bridge; no rerun was performed to recover
  it — one-shot rule).

## 2. Evidence root (exactly five files, preserved RUNNING stubs)

`.workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/independent_session/`:

| file | state |
|---|---|
| `frozen_plan.json` | complete pre-open doc (arms B0 34119 / B1 39239 / B2 32524 + 327743 public; blocks 0..127/128..255/256..383; remainder 384..1659; dev_source verified true) |
| `input_and_predecessor_identity.json` | complete pre-open doc (construction digest match true; split manifest 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824; dev/block pins verified true) |
| `per_block_arm_outcomes.jsonl` | empty, 0 records (expected 9) |
| `aggregate_summary.json` | `{"status": "RUNNING"}` |
| `report.md` | `# P20G plus1024 independent session (RUNNING)` |

Gate statistics (frozen 20-gate order, read from artifacts + refusal line):

- PASS before any content open: `predecessor_construction_identity` (digest match true),
  `dev_split_manifest_identity` (counts exact), `dev_block_range_identity` double gate —
  cross-file source-tag+digest pin first (1.5M path + 1869178 B pin verified true; 1M pool and
  reserved 2M refusal strings armed) then intra-file DEV-vs-VAL/HOLD disjointness (VAL first).
- FAIL: `target_population_contract` — the loaded `--source 1p5M` counts array
  (shape (1024,1024), floor 1e-15) mismatches all three carried-over literals
  (H1 0.02428054681872374 / H2 0.7767572780789994 / TOTAL 0.8010378248977232, from
  `operational_f13.EXPECTED_H1/H2/TOTAL`, i.e. the 1M-derived target point): failing
  `h1_matches_literal,h2_matches_literal,total_matches_literal`.
- Not evaluated (run stopped before any SC call, fail-closed): the remaining 16 gates,
  including `dev_population_exact`, `blocks_exact_with_declared_remainder`, `nine_records_exact`,
  `sc_calls_exact`, `tags_exact`, disclosure recount, one-open accounting, resource gate.

## 3. Per-arm outcomes and endpoints (descriptive; zero records)

| arm | disclosed (K1/K2/key bits) | SC+tag invoked | exact | verify_failed | undetected | endpoints (l1/hard-L2/oracle-L2/pair) |
|---|---|---|---|---|---|---|
| B0_sc_base (operational) | 319/6492/34119 | 0 | — (not run) | — | 0 | — (not run) |
| B1_L2plus (operational) | 319/7516/39239, ΔK2=+1024, +5120 bits vs base | 0 | — (not run) | — | 0 | — (not run) |
| B2_true_l1_diagnostic (oracle) | 0/6492/32524 | 0 | — (not run) | — | 0 | — (not run; never operational regardless) |

- `b1_restored_count` analogue: not computable (no block executed; denominator 0 by construction).
- No exact count of any kind is reported because no block ran; per §7 any count would be COMPLETE
  only with integrity holding — integrity did not hold, so the label is BLOCKED, not COMPLETE.

## 4. Accounting identities (planned vs actual)

- Planned (frozen): SC 15 (3 blocks × (2+2+1)), tags 9, records 9; key 317646
  (3×34119 + 3×39239 + 3×32524; operational 220074 + oracle 97572); public 2949687 (9×327743);
  B1 key delta vs base +5120.
- Actual: SC 0/15, tags 0/9, records 0/9; key-dependent bits disclosed 0; public/tag bits 0.
  Independent recount: zero transcript events, mismatch 0 — vacuously consistent; the BLOCKED
  verdict comes from the earlier `target_population_contract` gate, not from accounting.
- Resource envelope: wall ≪ 600 s, no RSS pressure (fast pre-SC refusal), single-thread env
  (`OPENBLAS/OMP/MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2`, `ulimit -v 2097152`) as frozen.

## 5. Consumption counts (one-shot semantics honored)

- `attempts_used`: 0 → 1 (1/1 SPENT). Consumption point reached: first protected content open
  (`load_v25_channel_counts` on the NPZ; code sets `counts_content_opens=1`,
  `attempts_consumed_by_this_run=1` before the precondition check).
- NPZ content opens: 1 (the shared `channel_counts.npz`, `1p5M` array selected; shape check passed).
- 1.5M DEV parquet content opens: **0 — the DEV file was NEVER content-opened**. Only the
  stat-size pre-check ran; the run BLOCKED before `load_pairs_table`. No DEV row, frame, or
  symbol was read; remainder 384..1659 never decoded (never even listed from content).
- STATUS mapping: `train_artifact_reads_used` 0 → 1 (NPZ open); `hold_data_reads_used` stays 0.
- No reopen, no rerun, no tuning, no refit, no second factor, no SCL. Any further execution
  under this packet is forbidden (attempts 1/1 exhausted).

## 6. 2M pristine confirmation (procedural; the file was never statted per packet §4)

- The executed argv contains no 2M path; the only 2M string in scope is the runner's refusal
  literal (`REFUSED_2M_DEV_PAIRS_PATH`), which is a never-touched string constant.
- This operator issued zero open/stat/read/listing commands against
  `type2_2M_20260121_183657` in any form (Stage A likewise: refusal-literal only).
- Pristine status is therefore preserved by non-access; it was NOT verified by stat (stat would
  itself violate the packet), only by the absence of any accessing command in this session.

## 7. Stages not run

- Pre-RESULT review: NOT_RUN. Main-thread acceptance: PENDING (this operator does not accept).
- No decoder SC/tag execution, no DEV decode, no remainder/VAL/HOLD selection, no commit/push,
  no writes under `results/` or `comparison_bench/outputs_comparison/` (scoped cleanliness check:
  `src/`, `experiments/`, `tools/`, `results/` zero diff; the single
  `comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv` modification
  predates this run by ~11 h — pre-existing unrelated dirt, untouched by Stage B).

## 8. Blocker (first and only; execution stops here)

- Failing command: the §1 Stage-B command (verbatim, first and only attempt).
- Exact error: `BLOCKED(target_population_contract): failing preconditions: h1_matches_literal,h2_matches_literal,total_matches_literal`
  (mechanism, read-only code inspection, no rerun: `run()` opens the NPZ, selects
  `loaded["1p5M"]`, and checks it against the frozen 1M-derived `EXPECTED_H1/H2/TOTAL`
  literals via `target_preconditions`; all three fail, so it raises before the DEV parquet
  open — the double gate and construction/manifest pins all passed first).
- Attempted remedies: none beyond read-only artifact/code inspection. A rerun of any kind
  (identical or otherwise) is forbidden by the packet one-shot rule (attempts 1/1 spent), and
  any precondition/threshold/prior change would be tuning, likewise forbidden.
- ONE decision needed from the main thread: accept `BLOCKED(target_population_contract)` as
  the terminal Stage-B outcome of this packet (route to Pre-RESULT review on the BLOCKED
  artifacts, then planner owns the next-round design — e.g. whether a future packet re-freezes
  the target-population contract for per-session channel statistics), OR rule otherwise; no
  further operator action is authorized under this packet either way.
