# P13 freeze — target empirical-genie f=1.3 scaling gate (Wave-A implementation freeze)

Packet: `NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING` (Tier-Y).
Predecessors verified: P9 `TARGET_EMPIRICAL_LOWER_RATE_POINT_ACCEPTED`,
P11 `EXACT_CHUNKED_SC_ACCEPTED`, P12 `BLOCKED(resource_limits_met_and_no_abort)`,
X13R1 `COMPLETE_DESCRIPTIVE_ONLY`. This document freezes the
implementation, tests, command, budgets, output schema, target absence
and attempt point for the Wave-C gate execution. It authorizes nothing;
an independent reviewer-go Pre-EXECUTE PASS is required before the
single NPZ content open. The gate has NOT been run in this wave
(artifact reads used: 0, attempts used: 0; the V25 `channel_counts.npz`
was never content-opened — stat size only, §8).

## 1. Mission and frozen execution matrix (P13-01/P13-02)

Determine, before any P12 retry, whether the V25 1M TRAIN target model
reaches the planning budget `f<=1.3` at N=4096, 8192 or 16384 when
construction and rate allocation are learned from empirical genie risks
rather than a same-entropy BEC surrogate. Model-sampled
construction/rate development gate only: not operational FER and not
real-data qualification.

| N | TRAIN streams (×2 blocks = 8) | DEV streams (×8 blocks = 32) |
|---:|---|---|
| 4096 | 2026091860, 2026091861, 2026091862, 2026091863 | 2026091870, 2026091871, 2026091872, 2026091873 |
| 8192 | 2026091880, 2026091881, 2026091882, 2026091883 | 2026091890, 2026091891, 2026091892, 2026091893 |
| 16384 | 2026091900, 2026091901, 2026091902, 2026091903 | 2026091910, 2026091911, 2026091912, 2026091913 |

Exactly 120 blocks (24 TRAIN + 96 DEV). Each stream restarts its RNG
(`np.random.default_rng(stream seed)`, blocks sequential, no global
RNG). Per block: `B ~ p_b` then `A ~ P_floor(A|B)` sampled once
(`A = 32*U1 + U2`); L1 genie conditionals with the true U1 prefix; L2
genie conditionals with the true U1+U2 prefix (L2 metrics
`ORACLE_CONDITIONED` on the true high symbols). Every genie call runs
through the accepted `genie_conditionals` (whose `sc_decode` production
default is exactly `chunk_rows=512`, verified by contract check, never
changed). No tag or Toeplitz master exists in this gate.

## 2. Frozen f budget, empirical construction and allocation (P13-02/P13-03)

- Budget: `K_total = floor((1.3*N*(H1+H2)-64)/5)` with
  `H1 = 0.02428054681872374`, `H2 = 0.7767572780789994`
  (`H1+H2 = 0.8010378248977231` in float64; the `EXPECTED_TOTAL` literal
  `0.8010378248977232` differs by one ulp and every frozen floor is far
  from an integer boundary under either value, verified §8), clipped to
  `[0, 2N]`, entire budget used. Computed from the literals alone (no
  NPZ opened; reproduced by `test_frozen_k_total_pinned`):

  | N | 1.3·N·H | (1.3·N·H−64)/5 | K_total |
  |---:|---|---|---:|
  | 4096 | 4265.366210015396 | 840.2732420030792 | 840 |
  | 8192 | 8530.732420030791 | 1693.3464840061583 | 1693 |
  | 16384 | 17061.464840061585 | 3399.492968012317 | 3399 |

- Construction: per TRAIN block accumulate `h_i = -log2 p_i[U_i]` and
  `e_i = 1 - max p_i` from the genie rows; pool means per layer; persist
  only the pooled coordinate risks, never per-block metric/risk planes.
  Worst-first orders by the accepted `(e, h, index)` semantics
  (`disclosure_order_from_stats`). Every feasible integer `(K1, K2)`
  with `K1+K2 = K_total` enumerated; lexicographic minimum of `(TRAIN
  residual e sum, K1, K2)`. Orders, allocation and TRAIN residual frozen
  before the first DEV block (freeze SHA-256 over N/K/orders/pooled
  risks, re-verified post-DEV).
- DEV: per block the scalar residual `R` for the frozen split, plus the
  report-only residual under the P12 same-entropy BEC orders and their
  deterministic same-budget allocation (accepted `allocate_layer_ks`)
  computed from the SAME DEV genie rows with no extra SC calls. DEV is
  never selected or tuned from. Frozen report-only BEC splits from the
  literals alone: N=4096 → (37, 803), residual 3.363831923437399;
  N=8192 → (80, 1613), residual 2.264840263288221; N=16384 → (166,
  3233), residual 1.2717801865443192 (reproduced by
  `test_frozen_bec_report_only_splits_pinned`).
- Per N: the 32 DEV `R` values, mean, sample standard deviation, range
  and one-sided 95% Student-t UCB `mean + 1.695518782*std/sqrt(32)`
  (df=31). The residual is a genie union-bound construction proxy; it
  is not operational FER.

## 3. Exact verbatim frozen command (P13-07)

Byte-equivalence with this file is a Pre-EXECUTE check:

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_scaling --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values 4096 8192 16384 --train-seeds 2026091860 2026091861 2026091862 2026091863 2026091880 2026091881 2026091882 2026091883 2026091900 2026091901 2026091902 2026091903 --dev-seeds 2026091870 2026091871 2026091872 2026091873 2026091890 2026091891 2026091892 2026091893 2026091910 2026091911 2026091912 2026091913 --train-blocks-per-stream 2 --dev-blocks-per-stream 8 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate
```

Every flag is required; there is no production default. N-to-seed
grouping is enforced (12 TRAIN + 12 DEV seeds in N order, four streams
per N). Pinned interpreter
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (Pre-EXECUTE
reconfirms). Budgets: 2 GiB virtual (`ulimit -v 2097152`) and 2 GiB RSS,
1800 s external timeout and 1800 s internal wall guard, single-thread
allocator environment per the export line.

## 4. Absent root and five-file schema with checkpointing (P13-05)

Root
`.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/`
is ABSENT at freeze time (verified §8) and must remain absent until the
authorized execution. All five files are created as stubs BEFORE the
content open, then the SAME five files are checkpointed after every
completed block/N; no sidecars: `frozen_plan.json`,
`construction_and_allocations.json`, `per_block_genie_residuals.jsonl`,
`aggregate_summary.json`, `report.md`. Public orders and scalar block
statistics only: never counts, sampled symbols, truth vectors, decoder
outputs, metric planes or RNG state. Per cell: wall, RSS HWM, Linux
`VmPeak` and `VmSize` (from `/proc/self/status`).

## 5. Gates, labels, UCB rule (P13-04)

Integrity gates in frozen order: `target_population_contract`,
`three_n_cells_complete`, `streams_disjoint_frozen`,
`orders_valid_frozen_before_dev`, `budget_allocation_reproduced`,
`risks_finite`, `zero_genie_exceptions`, `truth_isolation`,
`no_unregistered_calls`, `checkpoint_accounting_consistent`,
`attempt_read_accounting_exact`, `resource_limits_met_and_no_abort`.
Scientific classification uses only the empirical arm:
`TARGET_EMPIRICAL_GENIE_F13_SCALING_CANDIDATE` if at least one
registered N has frozen DEV residual UCB `<= 0.01` (smallest such N
recorded); `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` if
integrity passes but none meets it; otherwise `BLOCKED(<earliest>)`.
No FER/real-channel/minimum-N language beyond the frozen proxy wording;
BEC and empirical-minus-BEC are report-only.

## 6. Consumption point, refusal ordering, no-rerun rule

Artifact read 1/1 and scientific attempt 1/1 are consumed together at
the first NPZ content open (`load_v25_channel_counts`); a module-level
reopen guard refuses any second NPZ-mode call. Refusals (absent root,
CLI parse, chunk contract, seed grouping, missing file, size mismatch)
happen BEFORE the open with zero genie calls. Any post-open failure
(precondition mismatch, budget violation, exception, resource stop) is
`BLOCKED(<earliest gate>)` with consumption already spent: best-effort
BLOCKED stubs (the files already exist), then fail closed. After
content open: no repair, rerun, seed/order/allocation/threshold change
or tuning. On MemoryError/resource failure: preserve checkpoints,
finalize BLOCKED if possible, never rerun. No commit/push.

## 7. Forbidden paths

No Model-F/HOLD/raw/real/EVAL artifact access; no official prior seeds
(all P7–P12 streams plus probe seeds) and no N outside 4096/8192/16384;
no FWHT/APP/SCL; no operational decoder, tag, Toeplitz master,
disclosed values or production benchmark; no old-root modification
(`results/`, `comparison_bench/outputs_comparison/`, prior queue
roots); no other source-file change beyond the allowed manifest;
no commit/push. The residual is a proxy, not FER: no
FER/efficiency/key-rate/qualification/promotion claim either way.

## 8. Freeze-time verification evidence (this wave)

- Target root absent: `ls` of the P13 queue dir shows only
  `AUTHORIZATION_PROMPT.md`, `PROMPT.md`, `STATUS.yaml`,
  `TASK_PACKET.md` (plus, after this wave, `P13_FREEZE.md`,
  `P13_IMPLEMENTATION_NOTES.md`) — no `empirical_genie_scaling_gate/`.
- NPZ stat size only: `25166822` bytes (matches `EXPECTED_NPZ_BYTES`);
  content never opened (reads used 0, attempts used 0).
- Frozen-seed freshness: repo grep for each P13 stream seed shows hits
  only in P13 code/docs/tests/freeze (see review item R1 for the
  2026091900..1903 test-local overlap note); all P13 seeds disjoint
  from every official prior stream (P7 1650–1664, P8/P9 grids, P11
  gate, P12 1820–1825, probe seeds).
- K_total floors verified under both float64 spellings of H1+H2
  (table §2; all far from integer boundaries: fractional parts
  0.27/0.35/0.49).
- Focused suite: 20/20 pass; NB-Polar suite 305/305 green (285 accepted
  + 20 new); full `comparison_bench/tests` triaged (2117 passed, 468
  failed, 21 skipped, 22 pre-existing collection errors — all failures
  outside `test_nbpolar_*`, environmental/pre-existing, none touching
  this wave's files; see implementation notes R2).
- HEAD unchanged except the allowed manifest; no commit (see
  implementation notes for the pre-existing dirty state, untouched by
  this wave).
