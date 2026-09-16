# Pre-EXECUTE review — NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE (independent)

Reviewer: independent reviewer-go (did not write the code). Read-only review;
the only file written by this review is this document. The V25
`channel_counts.npz` content was NEVER opened (stat-only: 25166822 bytes).
The real gate command was NEVER run. No Model-F/HOLD/raw/real/EVAL/tag/FWHT/
APP/SCL access; no P13/old-root writes; no commit/push.

**Verdict: PASS** — Wave-C (single authorized gate execution) may proceed.
No blocking issue found. Three non-blocking observations (§11) require no
pre-execution repair; one (RSS-counter artifact) carries a Wave-C/Pre-RESULT
reading instruction.

## 1. STATUS exactness — PASS

Command:

```bash
cat .workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/STATUS.yaml
```

Raw evidence (read 2026-09-15, verbatim):

```yaml
task_id: NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE
state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE
tier: Y
predecessor: TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED_ACCEPTED
execution_authorized: true
artifact_reads_allowed: 1
artifact_reads_used: 0
attempts_allowed: 1
attempts_used: 0
result: null
pre_execute_review: pending
pre_result_review: pending
next_gate: INDEPENDENT_PRE_EXECUTE
```

`execution_authorized: true`; reads 0/1, attempts 0/1; `result: null`;
both reviews `pending`; state/next-gate exactly as declared. PASS.

## 2. OpenSpec P14 delta consistency — PASS

- Delta `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p14/spec.md`
  (166 lines) matches TASK_PACKET P14-01..P14-06: frozen V25 1M input + P7
  floor/support rule + entropy literals (H1 0.02428054681872374, H2
  0.7767572780789994, total 0.8010378248977232, tol 1e-12/1e-9); frozen
  matrix N=16384, TRAIN 1930..37x16, DEV 1940..43x8, nested prefixes
  8/16/32/64/128, 320 planned calls; construction (pooled means,
  worst-first `(e,h,index)`, K_total=3399, exhaustive lexicographic
  `(TRAIN residual,K1,K2)`, freeze-before-DEV); DEV scalar residuals +
  mean/std/range + one-sided t-UCB `mean+1.695518782*std/sqrt(32)` + paired
  `R_B-R_8` + adjacent diffs; B=128-only 0.01 decision rule with the two
  exact labels; 13 integrity gates; five-file schema + per-block
  checkpointing; budgets (1800 s, 2 GiB, single-thread, ARENA_MAX=2);
  proxy-not-FER scope ("not operational FER", "not ... proof of any minimum
  N or TRAIN size"); P13-B=8 historical-reference-only ("SHALL NOT be
  merged", "equality SHALL NOT be required"); "This document authorizes no
  production behavior." (spec.md:17).
- P14 tasks section (`tasks.md` lines ~610-684): all nine boxes UNCHECKED —
  `P14-1..P14-9` every line `- [ ]`, zero `[x]/[X]` in lines 605-690
  (verified by `awk 'NR>=605 && NR<=690 && (/\[x\]/ || /\[X\]/)'` → empty).
  Checked boxes elsewhere in tasks.md (P11 etc.) belong to prior accepted
  phases, not this wave.
- No production behavior is authorized by docs (spec.md:17; tasks P14-1 text;
  P14_FREEZE.md §8 "This document authorizes nothing"). PASS.

## 3. Reuse proof (accepted modules untouched by this wave) — PASS

- `git status --porcelain` + `git diff`: tracked modification to
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py` is the
  ACCEPTED P11 allocation-only chunking (`chunk_rows` keyword-only,
  default 512; diff hunk at sc.py:176-204; file mtime Sep 14, predates
  Wave-A Sep 15). It is the reuse target, not a Wave-A edit.
- Wave-A files are all NEW (untracked `??`): `.../nbpolar-phase4-p14/`
  spec dir, `empirical_genie_learning_curve.py` (mtime Sep 15 02:23),
  `test_nbpolar_empirical_genie_learning_curve.py`, queue dir
  `NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/` (FREEZE/NOTES/this
  review; STATUS.yaml lives inside the new dir). `tasks.md` tracked diff
  appends the P14 section only (P14-1..P14-9, unchecked).
- `empirical_genie_scaling.py` (accepted P13, mtime Sep 14 23:17, predates
  wave), `prior.py`, loader (`v35_algorithm_development`), P13 evidence
  root, old roots: no Wave-A modification (mtimes pre-wave; no entries in
  `git diff`; P13 gate dir untouched — only READ for timing evidence §7).
- The runner only CALLS accepted semantics: imports are
  `load_v25_channel_counts`, `make_gf32`, `spearman_rank_corr/topk_overlap`,
  `sample_full_block`, P13 `block_genie_risks/residual_for_orders/
  select_empirical_split/student_t_ucb_95` (identity-pinned by passing test
  `test_p13_helpers_shared_not_reimplemented`, runner:108-113), `Provenance/
  build_p1_metrics/gather_p2_metrics/probs_to_symbol_metric`,
  `ImpossibleDisclosedValueError`, `PRECONDITION_ORDER/
  TargetPopulationContractError/target_preconditions`, `budget_k_total`,
  `polar_transform` (runner:104-127). No reimplementation. PASS.

## 4. Frozen budget/construction — PASS (independently recomputed)

Command:

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c \
  "import math; H=0.8010378248977232; raw=(1.3*16384*H-64)/5; \
   print(repr(raw), math.floor(raw), 5*math.floor(raw)+64, repr(1.3*16384*H))"
```

Raw evidence: `raw = 3399.4929680123178`, `floor = 3399`, `leakage = 17059`,
`budget = 17061.464840061588` (slack 2.46 bits; 0.507 from the next integer
— floor stable under either float64 spelling; alt spelling
`3399.492968012317` → 3399). Matches `budget_k_total` pin in the passing
focused test and runner:961 + `_stub_plan` literal-K (runner:627-628).

- Per-prefix `(K1,K2)` lexicographic rule: `select_empirical_split`
  (P13 accepted, scaling.py:461-497) enumerates all feasible K1 and keeps
  `min(residual,K1,K2)` (scaling.py:483-488); invoked per prefix from
  running sums at the moment `used == B` (runner:1133-1143). Order of
  enumeration cannot matter (explicit tuple comparison, not first-best).
- Freeze-before-first-DEV: structural — TRAIN loop (runner:1091-1146)
  completes fully before `frozen_arms` snapshot (runner:1154-1162) and the
  DEV loop (runner:1165+); missing-prefix guard raises
  `BLOCKED(nested_prefixes_exact)` before any DEV genie call
  (runner:1149-1153).
- Nested prefixes from ONE stream-major TRAIN sequence: single pass over
  `train_list` × `range(train_bps)` with per-stream `default_rng(seed)`
  restart (runner:1091-1093); prefixes are running-sum snapshots, no block
  revisited (runner:1090-1143).
- No-repeated-decodes: exactly one `block_genie_risks` call per TRAIN block
  (runner:1118) and one per DEV block (runner:1192); `residual_for_orders`
  is pure (scaling.py:447-458, "no SC call, no RNG, no I/O" — no `calls`
  increment). `block_genie_risks` = exactly 2 registered calls via the
  `genie_layer_risks` choke point (scaling.py:531-553). Planned
  `2*(128+32) = 320` (runner:154); final gate requires `== 320`
  (runner:1487); smoke measured 160 block-calls / 320 calls (§9). PASS.

## 5. Refusal/consumption/checkpoint ordering — PASS

- Pre-open refusals, in code order (runner:791-844, ALL before `mkdir` at
  854 and stubs at 857-872): existing root (`FileExistsError`, 792-793);
  floor/source/target-f/chunk/n/prefix/seed-count/disjointness/bps
  (`ValueError`, 794-841). CLI-parse refusal exits 2 without entering
  `run_*` (runner:1578-1597). Probed: wrong `--n 8192` with the REAL
  frozen counts path → `exit=2`, `ROOT_ABSENT`, message
  `frozen point requires n=16384, got 8192` (§9). Existing-root probe is
  test-pinned (sentinel untouched, test `test_checkpoint_resume_refusal_`).
- Five files created BEFORE content open (runner:853-872), checkpointed per
  block thereafter: TRAIN (runner:1144-1146) and DEV (JSONL append
  runner:1219 + checkpoint runner:1223-1225); writes target ONLY the five
  names under `out_path` (verified all write call sites, runner:432-437,
  857-872, 979-990, 1219, 1311-1336, 1497-read); no sidecars.
  (`frozen_plan.json` is immutable plan content — written once at stub
  time; per-block checkpoint rewrites the four live files. No violation.)
- Preconditions AFTER open but BEFORE any genie call: `target_preconditions`
  (runner:940) precedes first genie call (runner:1118); zero-genie probe
  test-pinned (`test_precondition_failure_zero_genie_and_blocked_stubs`:
  `seen == {"genie": 0}`, BLOCKED stubs written).
- Consumption at first open with reopen guard: `load_v25_channel_counts`
  single call (runner:887), `_NPZ_CONTENT_OPENED` set once (888), guard
  refuses second NPZ-mode call (876-877); accounting records 1/1 + 1/1
  (892-910).
- MemoryError path preserves checkpoints + finalizes BLOCKED if possible
  (runner:1320-1341; DEV re-raise runner:1208-1209); test-pinned.
- Post-open: no repair/rerun/retuning paths exist (single straight-line
  pass; no retry/reopen flags ever set true). PASS.

## 6. Matrix/evaluation semantics — PASS

- N=16384 only (runner:803-805 refuse otherwise); TRAIN 8 streams × 16 =
  128, DEV 4 × 8 = 32 (runner:814-841 shape gates); per-stream RNG restart
  (runner:1092, 1166); CLI order pinned to ascending frozen tuples by the
  `streams_disjoint_frozen` final gate (runner:1367-1370, 1396-1401).
- Oracle-genie exactly P13: L1 true-U1-prefix via `build_p1_metrics` +
  `PRIOR_ONLY` (runner:1105-1110), L2 oracle-conditioned on true high
  symbols via `gather_p2_metrics(..., high...)` + `ORACLE_CONDITIONED`
  (runner:1111-1116), both layers through P13 `block_genie_risks`;
  provenance violations counted and gated (`truth_isolation`,
  runner:1485). Same shape in DEV (runner:1180-1195).
- NO tag/Toeplitz: `grep -n "toeplitz_tag|TAG_BITS|seed_bits_for|load_v31|
  parquet|TTBin|ttbin|fwht|sc_decode(|HOLD_|EVAL_|analytic_order|
  allocate_layer_ks"` on the runner → zero hits (only prose "No tag or
  Toeplitz"); test-pinned (`test_no_production_raw_hold_access_rule`,
  passing). No BEC arm by design (`analytic_order`/`allocate_layer_ks`
  absent).
- `chunk_rows=512` enforced pre-open (runner:802 + `_check_chunk_contract`
  runner:374-390: sc `_minus_block` default must be exactly 512,
  keyword-only, `sc_decode` exposes no chunk arg); flows through the
  accepted P13-helper default — helpers are called, never changed (§3).
- Pooled-risks-only persistence: `_freeze_construction` stores pooled means
  + public orders + scalars + SHA (runner:487-515); DEV records store
  scalars + `(seed, block_index)` (runner:1196-1207); counts/symbols/truth/
  decoder outputs/metric planes/RNG state never persisted.
- `(e,h,index)` worst-first via accepted `select_empirical_split` (§4).
- DEV stats: 32-value mean/sample-std (ddof=1)/range + one-sided t-UCB via
  P13 `student_t_ucb_95` (factor `T_FACTOR_DF31_95 = 1.695518782`,
  scaling.py:171; UCB emitted ONLY when count == 32, scaling.py:518-520);
  paired `R_B-R_8` (runner:1236-1241) and adjacent diffs (1242-1249)
  through the same helper (`paired_diff_stats` alias, runner:476-484);
  non-32 → `ucb None` (partial checkpoints only).
- Report-only Spearman/top-K (at frozen B=128 depths)/allocation-movement/
  improved-tied-regressed (runner:518-578); no selection path from DEV
  (constructions never written in DEV loop).
- P13 B=8 reference-only, mechanically enforced: no P13-evidence import,
  path, or value appears in the runner (only docstring prose); no gate
  compares against any P13 block or value (all gates recompute from run
  artifacts + literals). PASS.

## 7. OPERATOR-FLAGGED ITEM — wall/RSS adjudication: PASS (envelope adequate)

Projection arithmetic (all numbers from accepted/measured artifacts):

- Accepted P13 evidence (READ-ONLY,
  `.../P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/
  aggregate_summary.json`, outcome `..._NOT_CONFIRMED`):
  per-N `16384` resources = `{wall_s: 291.806806, rss_bytes_hwm: 301961216,
  vm_peak_kb: 525660, vm_size_kb: 486108}` for 8 TRAIN + 32 DEV = 40 blocks
  at N=16384 through the IDENTICAL helpers P14 reuses → **7.295 s/block**.
- P14 frozen workload: 128 TRAIN + 32 DEV = 160 blocks at the same N=16384
  through the same kernels → `160 × 7.295 = 1167.2 s ≈ 1170 s` projected.
- P14-only extras (running-sum accumulation, five one-time exhaustive
  splits over 3400 candidates, five-way pure scoring, 160 checkpoints of
  full-N=16384-vector files) are bounded by this review's injected smoke
  (§9): full 160-block shape with every P14 mechanism REAL except
  sampling+SC faked → **75-77 s**. Conservative total ≈ 1167 + 77 ≈
  **1245 s vs the 1800 s cap → ≥ 550 s (≥ 30%) margin**. Even a 40%
  machine-variance overrun (≈1640 s) stays inside.
- RSS/Vm (authoritative counters): P13 VmPeak 513 MB vs 2 GiB `ulimit`
  (4× margin); smoke VmHWM 237 MB for the full-shape checkpointing load;
  P14 adds ≈3 MB pooled/construction state. VmSize-gated `ulimit -v
  2097152` is kernel-enforced on TRUE usage → safe.
- An overrun cannot corrupt science: per-block checkpoints + fail-safe
  `BLOCKED(resource_limits_met_and_no_abort)` with evidence preserved.
- CAVEAT (non-blocking, see §11.1): the runner's `rss_bytes`
  (`ru_maxrss`-based) over-reads on this box (fresh-process proof:
  `ru_maxrss = 1725116 KB` vs true `VmHWM = 24 MB`). It cannot fail the
  gate from the stuck value (1.68 GB < 2 GiB) nor from true values
  (≈0.5 GB per P13 precedent); Pre-RESULT shall judge resources by
  VmPeak/VmSize + wall, not `rss_bytes_peak`.

Envelope adequate with margin. No wall/RSS ground for FAIL.

## 8. Tests — PASS (independently re-run, pinned interpreter, fresh basetemps)

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_empirical_genie_learning_curve.py \
  -q -p no:cacheprovider --basetemp=/tmp/p14-preexec-focused   # → 15 passed in 376.69s
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_*.py \
  -q -p no:cacheprovider --basetemp=/tmp/p14-preexec-full      # → 320 passed in 503.12s
```

- Focused 15/15 covers the full P14-4 list: K pin (both H spellings),
  matrix constants, P13-helper identity, nested accumulation + exact
  320-call budget + stream-major order, per-prefix order/K replay, five-way
  DEV scoring from one decode, paired/adjacent UCB recompute + report-only
  recompute, helper edges, six refusal probes (seed-shape/disjoint/n/
  prefixes/chunk/bps + CLI-parse exit 2), checkpoint-resume refusal,
  injected zero-read/attempt accounting + `_NPZ_CONTENT_OPENED is False`,
  precondition zero-genie BLOCKED stubs, MemoryError classification,
  forbidden-token scan.
- Full NB-Polar suite 320/320 (305 pre-existing + 15 new) — no regressions.
- Tests never open the NPZ (injected `counts=` path only; loader patched to
  forbid in refusal tests; CLI probe passes `--counts x` and expects parse
  failure), never use frozen streams 1930..43 (own seeds 1741..1752,
  disjointness asserted in-test), never invoke production paths
  (sample+genie seams faked; `forbidden_loader/forbidden_genie` guards).
  PASS.

## 9. Bounded smoke (injected only, temp root) — PASS

- Probe A (pre-open CLI refusal, REAL frozen counts path, never opened):
  `--n 8192` → `exit=2`, `ROOT_ABSENT`
  (`rm -rf /tmp/p14-smoke-refuse && ... -m ...empirical_genie_learning_curve
  --counts <frozen.npz> --source 1M ... --n 8192 ... --out-dir
  /tmp/p14-smoke-refuse`; stderr `frozen point requires n=16384, got 8192`).
- Probe B (full-shape injected run, fresh smoke seeds TRAIN 2026091781..88
  / DEV 2026091791..94 — repo-grep-confirmed fresh, disjoint from all
  priors — tiny injected 1024×1024 table, faked sample+genie seams,
  `/tmp` root): five files created
  (`frozen_plan.json`, `learning_curve_constructions.json`,
  `per_block_genie_residuals.jsonl`, `aggregate_summary.json`, `report.md`);
  160 block-calls / 320 genie calls; 32 JSONL lines; 13 gates recorded;
  outcome `BLOCKED(streams_disjoint_frozen)` (expected on non-frozen
  seeds; mechanical gates green); wall 75-77 s; VmHWM 237 MB;
  `_NPZ_CONTENT_OPENED False`. Grounds the §7 overhead term. PASS.

## 10. Scope/premises — PASS

- `git status --porcelain`: Wave-A set = new P14 spec dir + new runner +
  new focused test + new queue dir (FREEZE/NOTES/this review) + P14 section
  appended to `tasks.md`. No accepted-module, P13-evidence, or old-root
  writes (P13 gate dir read-only for §7 timings). Other dirty entries are
  pre-existing prior-phase work (worktree was already dirty; HEAD
  `ab173f2a` unchanged — `git log --oneline -1` → `ab173f2a`; no commit
  by this review).
- Frozen-seed freshness: repo-wide grep for `202609193[0-7]`/`202609194[0-3]`
  hits ONLY the frozen packet files + Wave-A additions (runner constants,
  test pins, spec delta); disjoint from all P7-P13/probe/test seeds
  (P13: 1860..1913; tests: 1741..1752; smoke: 1781..1794).
- Gate root `.../empirical_genie_learning_curve_gate/` ABSENT (verified
  `ls` + `test -e` → `ROOT_ABSENT`).
- NPZ stat-only `25166822` bytes (matches `EXPECTED_NPZ_BYTES`); content
  never opened in any review process (injected paths only; module flag
  `False` in every test/smoke; STATUS reads/attempts still 0/0/null).
  PASS.

## Frozen record (for Wave-C execution)

- K_total = 3399: `floor((1.3×16384×0.8010378248977232−64)/5)`,
  raw `3399.4929680123178`; leakage `5×3399+64 = 17059 ≤ 17061.46484…`.
- Prefixes B = 8/16/32/64/128, nested, one stream-major TRAIN sequence.
- Seeds: TRAIN `2026091930..2026091937` × 16 = 128; DEV `2026091940..41`
  × 8 = 32. RNG restarted per stream. N = 16384, GF(32)/poly-37/alpha-2,
  `chunk_rows = 512`, f = 1.3, floor = 1e-15, source = 1M.
- Planned genie calls = 320 (each TRAIN/DEV block decoded once per layer;
  five-way DEV scoring from the one decode).
- Command (exact, all flags required):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_learning_curve --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n 16384 --train-seeds 2026091930 2026091931 2026091932 2026091933 2026091934 2026091935 2026091936 2026091937 --train-blocks-per-stream 16 --prefix-blocks 8 16 32 64 128 --dev-seeds 2026091940 2026091941 2026091942 2026091943 --dev-blocks-per-stream 8 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate
```

- Root (must be absent at start):
  `.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/`
  with exactly five files (`frozen_plan.json`,
  `learning_curve_constructions.json`, `per_block_genie_residuals.jsonl`,
  `aggregate_summary.json`, `report.md`), stub-created pre-open,
  checkpointed per block, no sidecars.
- Budgets: 1800 s external timeout + internal cap, 2 GiB virtual
  (`ulimit -v 2097152`), single-thread BLAS/OpenMP, `MALLOC_ARENA_MAX=2`.
- Gates (13, frozen order): `target_population_contract`,
  `one_n_cell_complete`, `nested_prefixes_exact`, `streams_disjoint_frozen`,
  `orders_valid_frozen_before_dev`, `budget_allocation_reproduced`,
  `risks_finite`, `zero_genie_exceptions`, `truth_isolation`,
  `no_unregistered_calls`, `checkpoint_accounting_consistent`,
  `attempt_read_accounting_exact`, `resource_limits_met_and_no_abort`.
- Labels: B=128 DEV UCB (`mean + 1.695518782·std/√32`, df=31) ≤ 0.01 →
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_CANDIDATE`; integrity-pass
  but UCB > 0.01 → `..._NOT_CONFIRMED`; else `BLOCKED(<earliest gate>)`.

## Wave-C exit-code / label reading rule (corrected — read with stubs, not code alone)

`TargetPopulationContractError` subclasses `ValueError`, so (exactly as in
accepted P13) exit 2 covers BOTH pre-open refusals AND post-open contract
BLOCKEDs. Disambiguate by the root, never by exit code alone:

- `exit 0` ⟺ `run_*` completed and the five files are finalized → read
  `outcome_label` from `aggregate_summary.json`
  (`..._CANDIDATE` / `..._NOT_CONFIRMED` / `BLOCKED(<earliest>)`).
- `exit 2` + root ABSENT (or present-but-untouched, sentinel intact) =
  pre-open refusal (root-exists/CLI-parse/contract-shape); zero genie
  calls, NOTHING consumed — verify `_NPZ_CONTENT_OPENED` never set and
  STATUS still 0/0 before any retry-decision (retry needs a delta re-freeze
  per no-rerun; pre-open refusal is not an attempt).
- `exit 2` + root PRESENT with `aggregate_summary.json` carrying
  `BLOCKED(target_population_contract)` = POST-open contract failure;
  consumption SPENT (read 1/1 + attempt 1/1), zero genie calls — never
  rerun, never a fresh root.
- Other non-zero (1, traceback) = post-open resource/unexpected failure
  (`EmpiricalGenieLearningCurveResourceError`, MemoryError conversion, or
  unforeseen); checkpoints preserved — never rerun.
- Post-open, regardless of code: no repair, rerun, seed/prefix/order/
  allocation/threshold change, or tuning.

## 11. Findings (all non-blocking; smallest in-scope repairs — none required pre-execute)

1. (/platform, non-blocking) `rss_bytes` over-reads on this box:
   `_peak_rss_bytes()` (`ru_maxrss×1024`, runner:393-396) returns a stuck
   1725116 KB (1.68 GB) even for a fresh interpreter (true VmHWM 24 MB;
   smoke true VmHWM 237 MB). Verdict impact: none — stuck 1.68 GB < 2 GiB
   passes; if the counter unsticks it reads true values (≈0.3-0.5 GB per
   P13 precedent, `301961216` B) which also pass; worst case is a fail-safe
   `BLOCKED(resource…)`, never wrong science. Wave-C/Pre-RESULT
   instruction: judge resources by `VmPeak`/`VmSize` + wall; treat
   `rss_bytes_peak ≫ VmPeak` as this documented artifact. No code change
   (identical P13-accepted pattern; AGENTS.md §5.7 — no defensive
   re-engineering for a fail-safe cosmetic counter).
2. (inherited, non-blocking) Exit-2 overlap described in the reading rule
   above (runner:1595-1597 catches `ValueError` incl. the contract error,
   target_construction.py:340). Identical to accepted P13 (scaling.py:1588-
   1590). Disambiguation via stubs is specified; no change.
3. (cosmetic, non-blocking) `frozen_plan.json` is stub-written once, not
   rewritten per checkpoint (runner:978-990); content is immutable plan
   data and the accounting gate requires existence, not rewrite. No change.
4. (robustness note, non-blocking) A non-`ImpossibleDisclosedValueError`,
   non-contract, non-MemoryError exception inside the TRAIN loop would
   propagate without BLOCKED-stub finalization (only the contract/MemoryError
   handlers finalize; DEV blocks are individually caught at runner:1210-
   1217). Checkpoints are still preserved per block. No frozen-data path
   triggers this (accepted helpers + passing suite); no change.

## 12. Checklist

- [x] Matches OpenSpec spec (P14 delta §§ Requirement × 5 + bounded-claim;
      all P14 task boxes unchecked; docs authorize nothing)
- [x] Tests pass (focused 15/15; full NB-Polar 320/320; pinned interpreter;
      fresh basetemps; coverage matches P14-4; no NPZ/frozen-stream/
      production-path use in tests)
- [x] No scope creep (Wave-A set only; accepted modules called-not-changed;
      no tag/Toeplitz/BEC/FER/qualification surface; no P13/old-root writes)
- [x] docs/decision-log.md or docs/troubleshooting.md needs update? NO —
  Wave-A touched neither; the RSS-counter artifact (§11.1) is review
  evidence for Pre-RESULT, not a reusable failure mode of the repo
  (single-box WSL2 quirk with a fail-safe gate). If the main thread wants
  it logged, that is a milestone-batched docs action, not a pre-execute
  gate.

## Closure statements

- The V25 `channel_counts.npz` content was NOT opened by this review
  (metadata stat `25166822` bytes only); the real gate command was NOT run.
- Artifact reads/attempts are still 0/1 + 0/1 (`result: null`, reviews
  still `pending` — this PASS is recorded only in this file; STATUS.yaml
  itself is untouched by the reviewer).
- The gate root is still absent.
- HEAD is unchanged (`ab173f2a`); no commit/push by this review.
- Recommendation: main thread records Pre-EXECUTE PASS, then Wave-C single
  authorized execution with the exact frozen command above.
