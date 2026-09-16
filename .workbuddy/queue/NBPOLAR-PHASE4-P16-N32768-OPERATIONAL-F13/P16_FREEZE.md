# P16 freeze — N=32768 empirical-construction operational f=1.3 gate (Wave-A implementation)

Packet: `NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13` (`TASK_PACKET.md`, 120 lines, frozen).
Predecessors: P15 `ACCEPTED_VALID_NEGATIVE`, P9 `ACCEPTED`, P11 `EXACT_CHUNKED_SC_ACCEPTED`.
Wave-A scope ONLY: OpenSpec delta + implementation + tests + this freeze.
This document authorizes nothing. No box in `tasks.md` is checked by the implementing session.

## 1. Mission

P15's genie UCB is conservative and is not an operational outcome. P16
measures actual two-layer hard-candidate SC recovery at the accepted
target model, N=32768 and planning `f<=1.3`, using empirical
construction frozen before DEV, a fresh operational DEV set (64 blocks)
and one 64-bit Toeplitz verification per DEV block. No second arm, no
retry arm.

## 2. Frozen matrix

| item | frozen value |
|---|---|
| N | 32768 |
| field | GF32, primitive polynomial 37, alpha 2, natural order |
| source / floor / target f | `1M` / `1e-15` / `1.3` |
| chunk_rows | 512 (production default contract-checked) |
| tag-bits | 64 |
| TRAIN | streams 2026092000..2003 x 4 blocks = 16 (true-prefix L1 + true-high-conditioned L2 genie rows, exactly P13) |
| DEV | streams 2026092010..2017 x 8 blocks = 64, each stream restarts RNG, sample once |
| K_total | 6811 (see arithmetic below) |
| tag master | DEV stream seed + 10000, domain `nbpolar-p16-operational-f13-seed:<master>:<n>:<block>` |
| public control | `10*32768+63 = 327743` bits per invoked tag |
| outcomes | exact / undetected / verify_failed / decode_failed / nonfinite / resource_abort (undetected never success; nonfinite outranks decode_failed) |

K_total arithmetic (computed from the ratified literals, recorded here):
`H = H1+H2 = 0.02428054681872374+0.7767572780789994 = 0.8010378248977231`
(float64 sum; the `EXPECTED_TOTAL` literal `0.8010378248977232` differs by 1 ulp).
`(1.3*32768*H-64)/5 = 6811.785936024634` (both H spellings) →
`floor = 6811`, far from any integer boundary. Leakage `5*6811+64 = 34119`
against budget `1.3*32768*H = 34122.92968012317`; `f = 1.2998502888172847 <= 1.3`.

## 3. Frozen command (verbatim, P16-06)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 2100 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13 --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n 32768 --train-seeds 2026092000 2026092001 2026092002 2026092003 --train-blocks-per-stream 4 --dev-seeds 2026092010 2026092011 2026092012 2026092013 2026092014 2026092015 2026092016 2026092017 --dev-blocks-per-stream 8 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate
```

All twelve flags required; no production default. Budgets: 2100 s external
timeout, 2 GiB virtual limit (`ulimit -v 2097152`), 2 GiB RSS cap,
single-thread BLAS/OpenMP + `MALLOC_ARENA_MAX=2`.

## 4. Output root and five-file schema (absent until authorized execution)

Root `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/`
is ABSENT (verified §8). Exactly five files, created as stubs BEFORE the
content open, checkpointed after the construction freeze and after every
completed TRAIN/DEV block (same files, no sidecars):
`frozen_plan.json`, `construction_and_allocation.json`,
`per_block_outcomes.jsonl` (64 DEV records at completion),
`aggregate_summary.json`, `report.md`.
Public orders/pooled risks + scalar outcomes only: never counts, sampled
symbols, truth vectors, decoded labels/keys, metric planes, tag seeds or
RNG state (banned-key walk in focused tests). Per record: wall, RSS HWM,
Linux VmPeak/VmSize.

## 5. Gates and labels

Integrity (frozen order): target_population_contract;
construction_frozen_before_dev; train_dev_coverage_complete;
streams_disjoint_frozen; orders_valid_k_replay_f_within_budget;
buckets_disjoint_exhaustive; truth_isolation; undetected_zero;
nonfinite_zero; no_unregistered_calls (32 genie; SC attempts recomputed
from records); disclosure_recount_exact; attempt_read_accounting_exact;
resource_limits_met_and_no_abort.
Scientific: exact `>= 62/64` AND one-sided 95% Wilson LB `>= 0.90`.
Frozen boundary values (verified in code before DEV and in tests):
62/64 → `0.9098711859` (pass), 61/64 → `0.8883797144` (fail).
Labels: `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` /
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_NOT_CONFIRMED` /
`BLOCKED(<earliest gate>)`.

## 6. Consumption, refusal ordering, no-rerun

Artifact read 1/1 + scientific attempt 1/1 are consumed together at the
first NPZ content open (`load_v25_channel_counts`); a module-level
reopen guard refuses any second NPZ-mode call. Refusal order: existing
root → CLI parse → floor/source/target-f/chunk/tag/N/seed-grouping
checks (zero calls, zero opens) → stub creation → stat size check →
content open → preconditions (zero genie/SC on failure) → TRAIN/DEV.
Any post-open failure is BLOCKED with consumption spent. After content
open: no repair, rerun, N/seed/order/allocation/threshold/tag change or
tuning. Wall/RSS breach during TRAIN raises fail-closed; during DEV the
gate abort-fills remaining blocks and completes as BLOCKED. MemoryError
anywhere post-open preserves checkpoints, finalizes BLOCKED if
possible, and never reruns.

## 7. Forbidden paths (none implemented, none accessed)

No Model-F/HOLD/raw/real/EVAL access; no official prior-seed use; no
second or retry arm; no surrogate-order construction; no
transform/belief/list decoder; no FWHT/APP/SCL paths touched; no
P12-P15 code/evidence or old-root modification; no `results/` or
`comparison_bench/outputs_comparison/` writes; no commit/push.

## 8. Wave-A evidence (implementation only; gate NOT run)

- Output root absent: queue dir holds only `TASK_PACKET.md`,
  `STATUS.yaml`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md` (+ these two new
  freeze files); no `operational_f13_gate/`.
- NPZ never opened: stat-only size `25166822` bytes (expected value);
  module flag `_NPZ_CONTENT_OPENED` is False; reads/attempts used 0.
- Frozen seeds fresh: `2026092000..2003` / `2026092010..2017` appear only
  in the P16 packet docs, `operational_f13.py`, its focused test
  (constants read, never executed) and this freeze. They are disjoint
  from all P7-P15 official streams and all probe/test seeds. One
  cross-track coincidence, packet value retained verbatim: `2026092001`
  is also the v22 DE gate's density-evolution default sampler seed
  (different track, DE computation, not a Phase-4 stream) — flagged for
  independent Pre-EXECUTE review (see review items).
- Focused tests: 23/23 green (injected only, fresh test seeds
  2026091753..1759 + 2026091761..1765, temp roots, pinned interpreter).
- Full NB-Polar suite: 358/358 green (335 predecessors + 23 new),
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q
  -p no:cacheprovider`, fresh basetemps.
- HEAD unchanged by this wave; no commit/push (dirty worktree lines are
  pre-existing, out of scope, untouched).

## 9. Review items for independent Pre-EXECUTE

1. Six-bucket outcome extension: `nonfinite` as its own bucket above
   `decode_failed` (packet P16-02/P16-04) vs the P7/P8/P12 flag
   convention — classifier, record consistency and gate semantics.
2. TRAIN-phase per-block checkpointing (mirrors DEV checkpoint shape;
   TRAIN contributes progress counters only, no records).
3. DEV budget-breach abort-fill vs TRAIN-breach raise split (both
   preserve checkpoints; labels carry the earliest failing gate).
4. `2026092001` coincidence with the v22 DE default seed (§8).
5. `check_wilson_boundary` placement post-open (zero artifact
   interaction; fail-closed on helper drift).

## 10. Boundary

Operational-but-model-sampled: all frames are drawn from the frozen V25
TRAIN target population inside the runner. NOT real-data, NOT
qualification, NOT promotion evidence. Pre-EXECUTE PASS is mandatory
before the single attempt; Pre-RESULT recomputation before any label.
