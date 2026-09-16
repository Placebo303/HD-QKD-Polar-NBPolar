# Pre-EXECUTE review — NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING

Independent reviewer (did not write the code). Read-only except this file.
NPZ content never opened (stat only). Gate command never run.

## Verdict: PASS

The frozen Tier-Y packet may proceed to its single authorized execution with
the frozen P15-06 command. No blocking issue found. Four non-blocking
observations are recorded at the end (no pre-execution repair; the point is
frozen).

---

## 1. STATUS exactness — PASS

`STATUS.yaml` re-read at review time (unchanged):

- `execution_authorized: true`
- `artifact_reads_allowed: 1`, `artifact_reads_used: 0`
- `attempts_allowed: 1`, `attempts_used: 0`
- `result: null`
- `pre_execute_review: pending`, `pre_result_review: pending`
- `state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`,
  `next_gate: INDEPENDENT_PRE_EXECUTE`

Matches the P15_FREEZE.md declaration exactly. No consumption has occurred.

## 2. OpenSpec P15 delta consistency — PASS

- Delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p15/spec.md`
  (166 lines) + P15 task section in `tasks.md` (lines 686-760).
- Cells/construction/statistic/gates/labels/scope all match TASK_PACKET.md:
  N=32768/65536, TRAIN 2026091960..63 / DEV 2026091970..73 per N=32768 and
  TRAIN 2026091980..83 / DEV 2026091990..93 per N=65536, 4 blocks/stream,
  16+16 blocks per N, 128 planned genie calls, oracle-conditioned
  L1/L2 true-prefix genie only, pooled `(e,h,index)` worst-first orders,
  `K_total=floor((1.3*N*(H1+H2)-64)/5)` (6811/13636), lexicographic
  `(residual,K1,K2)` split, per-N 16-scalar DEV residuals with
  `mean + 1.753050356*std/sqrt(16)` (df=15), any-UCB<=0.01 CANDIDATE +
  smallest N / else NOT_CONFIRMED / else BLOCKED, five-file checkpointed
  root, 2 GiB + 2100 s budgets.
- Proxy-not-FER wording present in spec (lines 88-90, 114-115, 152-160);
  no-BEC-arm explicit (spec line 68: "No decision arm, no tag and no
  Toeplitz master SHALL exist in this gate").
- All nine P15 boxes unchecked: `grep -c -- "- \[x\] P15" tasks.md` → `0`.
  P15-1..P15-9 are all `- [ ]`.
- Docs authorize no production behavior: spec.md line 16-17 ("This document
  authorizes no production behavior."), tasks P15-1 ("no production behavior
  is authorized by this doc"), P15_FREEZE.md line 148 ("This document
  authorizes nothing").

## 3. Reuse proof (no accepted-module changes from this wave) — PASS

- `git status --porcelain` shows the worktree carries many pre-existing
  modifications/untracked files from prior waves (P3..P14 implementation
  material, all uncommitted under HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e`).
  Per AGENTS.md §10.1-11 the dirty tree is reviewed by scope, not by blanket diff.
- P15-attribution grep over every tracked-file diff touching shared modules
  returns zero P15 tokens:
  `git diff -- .../__init__.py | grep -c "mid_n\|P15\|196\|197\|198\|199"` → `0`;
  same grep over `sc.py empirical_channel.py empirical_oracle.py
  empirical_diagnostic.py` diffs → `0`.
- `prior.py`: tracked, unmodified (no status entry). `target_construction.py`,
  `target_n_scaling.py`, `empirical_genie_scaling.py` (P13),
  `empirical_genie_learning_curve.py` (P14): untracked-new files from prior
  waves; repo grep for `202609196/197/198/199`, `mid_n`, `P15` over them
  returns only P12's own `FROZEN_N_VALUES` line in `target_n_scaling.py`
  (its own gate, lines 42/131/248) — no P15 token in any accepted module.
- The runner only CALLS accepted semantics (empirical_genie_mid_n.py lines
  104-126): `load_v25_channel_counts` (loader), `make_gf32`,
  `disclosure_order_from_stats` + `spearman_rank_corr` (construction),
  `sample_full_block` (empirical_channel), `block_genie_risks` /
  `residual_for_orders` / `select_empirical_split` (P13, identity asserted by
  test, see §8), `Provenance/build_p1_metrics/gather_p2_metrics/
  probs_to_symbol_metric` (prior), `ImpossibleDisclosedValueError` (sc),
  `PRECONDITION_ORDER/TargetPopulationContractError/target_preconditions`
  (P7), `budget_k_total` (P12/P13 f-budget only — `allocate_layer_ks` NOT
  imported), `polar_transform`. Chunked SC is used only via the P13 genie
  path plus the `_minus_block` default-512/keyword-only contract check
  (lines 381-397); `sc_decode` is introspected, never called
  (test asserts `sc_decode(` absent and `hasattr(emn,'sc_decode')` False).

## 4. Frozen budget/construction — PASS (recomputed independently)

K_total recomputed by the reviewer with the pinned interpreter
(`H=0.8010378248977232`):

- N=32768: raw `(1.3*32768*H-64)/5` = `6811.785936024635` → floor **6811**;
  leakage `5*6811+64=34119 <= 34122.929680123176` ✓
- N=65536: raw = `13636.37187204927` → floor **13636**;
  leakage `5*13636+64=68244 <= 68245.85936024635` ✓
- Matches operator-reported raws (6811.7859… / 13636.3718…) and the
  `test_frozen_k_totals_pinned` pins under both float64 spellings of H1+H2
  (`0.02428054681872374+0.7767572780789994 = 0.8010378248977231`, 1-ulp from
  the literal — both give the same floors; fractional margins .786/.372 are
  far from any integer boundary; entropy noise 1e-12 shifts raw by <2e-8).
- Clipping `[0,2N]`: `budget_k_total` (target_n_scaling.py:421-429)
  `max(0, min(2N, floor(...)))` ✓. Full-budget-use: `select_empirical_split`
  (empirical_genie_scaling.py:461-497) enumerates `K1 in
  [max(0,K-N), min(N,K)]` with `K2=K-K1`, key `(residual,K1,K2)` —
  lexicographic rule exactly as specified ✓. Leakage inequality enforced at
  runtime (empirical_genie_mid_n.py:958-965) and in replay (1392) ✓.
- Per-N freeze-before-DEV in code order: the `for n_pos, n in
  enumerate(n_list)` loop (line 954) slices per-N seeds (956-957), runs 16
  TRAIN (972-1021), freezes orders/allocation/TRAIN residual + freeze-SHA
  (1023-1099), then runs 16 DEV against the local frozen `emp` dict
  (1101-1180). DEV of N=32768 cannot leak into N=65536 construction
  (pooled accs are per-cell locals; DEV only reads `emp`) and vice versa.
  Stability Spearman is marked `diagnostic_only` and excluded from the freeze
  SHA (1069-1078) and from every gate ✓.
- P7 empirical orders never imported: only `PRECONDITION_ORDER`,
  `TargetPopulationContractError`, `target_preconditions` come from
  `target_construction` (lines 120-124) ✓.

## 5. Refusal/consumption/checkpoint ordering — PASS

Code order in `run_empirical_genie_mid_n` (lines 717-872):

1. absent-root refusal (719-720) → floor/source/target-f refusals (721-728)
   → chunk contract (729) → N-values `!= [32768,65536]` (730-735) →
   bps `!= 4/4` + N-to-seed grouping (4/N, distinct, disjoint, 736-764) —
   ALL before any artifact access, zero genie calls, root untouched
   (test asserts roots a..g never created).
2. Five files created as stubs (776-793) BEFORE the content open.
3. NPZ branch (796-809): `is_file` → stat size `== 25166822` → single
   `load_v25_channel_counts` open; reopen guard (797-798) refuses a second
   NPZ-mode call process-wide (`_NPZ_CONTENT_OPENED`, line 286, never cleared).
4. Preconditions via `target_preconditions` (861-872) after open but before
   ANY genie call — zero-genie probe covered by
   `test_precondition_failure_zero_genie_and_blocked_stubs` (genie counter 0,
   BLOCKED stubs written in place, never a fresh root).
5. Consumption read 1/1 + attempt 1/1 recorded at first open in `accounting`
   (813-831); injected test mode records 0/0 with exact-accounting gates
   still holding (test asserts).
6. Per-block checkpoint of the same five files after every completed block
   (1160-1177: jsonl append + `_integrity_gates_partial` + `checkpoint`);
   no sidecars (smoke re-confirmed exactly the five names).
7. `MemoryError` over the full post-open pipeline (1263-1284) preserves
   partial evidence (jsonl + construction checkpoints already on disk) and
   finalizes BLOCKED if possible; `EmpiricalGenieMidNResourceError`
   propagates without rewrite (see non-blocking observation 2). Post-open:
   no repair/rerun/N-seed-order-allocation-threshold change or tuning
   anywhere in the code paths ✓.

## 6. Matrix/statistic — PASS

- Cells exact: `FROZEN_N_VALUES=(32768,65536)`; TRAIN
  `(1960..63,1980..83)`, DEV `(1970..73,1990..93)` (lines 141-149);
  16+16 blocks per N (`FROZEN_TRAIN/DEV_BLOCKS_PER_N=16`); per-stream
  `np.random.default_rng(seed)` restart per stream (973, 1103) ✓.
- Oracle-genie exactly P13: shared-identity test
  (`test_p13_helpers_shared_not_reimplemented`) asserts `is` identity for
  all three helpers; L1 `PRIOR_ONLY` / L2 `ORACLE_CONDITIONED` provenance
  with violation counting on both TRAIN and DEV paths (991-998, 1122-1129);
  `truth_isolation` gate requires zero violations ✓.
- NO BEC/tag/Toeplitz anywhere functional: code-identifier grep
  (`allocate_layer_ks|analytic_order|bec_report_only|r_bec|toeplitz|fwht|
  scl_decode|app_|tag_sign|model_f|holdout|raw_frame|real_frame|EVAL`)
  matches only module-docstring/prose lines (40, 82-83, 221-223); the test's
  functional-token scan (`toeplitz_tag,TAG_BITS,seed_bits_for,load_v31,
  parquet,TTBin,fwht,sc_decode(,HOLD_,EVAL_,analytic_order,
  allocate_layer_ks,bec_report_only,r_bec,bec_r,BEC_RULE`) passes ✓.
- `chunk_rows=512` plumbed: CLI requires `--chunk-rows`, contract-checked
  against `_minus_block` default (381-397); P13 genie path runs chunked SC ✓.
- Pooled-risks-only persistence: construction holds orders + pooled means +
  scalars; banned-key walk over all three JSON artifacts + every jsonl record
  (`bob,high,low,u1_true,u2_true,a_full,counts,logp,…,p_b,f_full,r_bec,bec`)
  passes ✓. Per-block jsonl records carry exactly
  `{n,stream_seed,block_index,r_empirical,error,resources}` with
  `{wall_s,rss_bytes_hwm,vm_peak_kb,vm_size_kb}` per record ✓.
- `(e,h,index)` worst-first via accepted `select_empirical_split` /
  `disclosure_order_from_stats` ✓; DEV residuals are pure
  (`dev_block_residual`, zero-genie test with boom fake) ✓.
- DEV statistic: 16 scalar residuals per N; `student_t_ucb_95` applies factor
  `1.753050356` ONLY at `count==16`, else `ucb=None` (lines 466-468);
  reviewer independently integrated the t-CDF (Simpson, pure `math`) to
  `t(0.95,df=15)=1.7530503557` — literal differs by 3e-11 (rounding) ✓;
  `t(0.95,df=31)=1.6955187825` confirmed different, and `1.695518782` is
  textually absent from the runner (test asserts) ✓.
- Order-stability/allocation/resources diagnostics-only ✓ (SHA exclusion,
  `diagnostic_only: True`, gates never read them).
- Classification (1219-1226): integrity-all-true + any UCB≤0.01 →
  `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_CANDIDATE` + smallest N; pass
  without qualifier → `..._NOT_CONFIRMED`; else `BLOCKED(<earliest>)` in
  `INTEGRITY_GATE_ORDER` ✓, with proxy-only wording (`RESIDUAL_SCOPE`,
  `CLAIM_SCOPE`; `undetected` correctly noted meaningless, line 281) ✓.
- Truth isolation + no DEV-based tuning possible: DEV loop is read-only over
  the frozen `emp` dict; replay gate re-derives orders/split from pooled
  TRAIN risks only ✓.

## 7. OPERATOR-FLAGGED ITEM — wall/RSS adjudication — PASS (ratified with numbers)

Ground truth (accepted, same code path / env / machine class):

- P13 OPERATOR_RETURN §9 (chunk_rows=512, single-thread, 40 blocks/cell =
  8 TRAIN + 32 DEV): N=4096: 65.04243 s; N=8192: 139.731162 s;
  N=16384: 291.806806 s → per-block 1.626 / 3.493 / **7.295 s**
  (ratios 2.148, 2.089 per doubling ≈ N·logN theory 2.167/2.154, slightly sub).
- P14 OPERATOR_RETURN (160 blocks @N=16384, same chunking/env):
  wall 1110.16709 s → **6.94 s/block**; VmPeak 508308 kB; RSS HWM 283 MB.
- Reviewer smoke TODAY, same pinned interpreter + frozen env vars, REAL genie
  path, injected tables (Part B, `/tmp/p15_smoke.py`): per-block
  4096: 1.447 s; 8192: 3.086 s (×2.133); 16384: 6.458 s (×2.093);
  32768: 13.685 s (×2.119); 65536: 28.775 s (×2.103). Exponent confirmed;
  absolute baseline within 12% of P13 (injected-table sparsity; P13 numbers
  additionally include per-block checkpoint I/O, hence used as the
  conservative projector). Table density cannot change cost (all hot shapes
  are fixed `(N,32)`; sampling/gathers/SC are value-independent; P13/P14 had
  zero `ImpossibleDisclosedValueError`s).

Projection (primary: P13 checkpoint-inclusive baseline × smoke ratios):

- N=32768: 7.295 × 2.119 = 15.46 s/block × 32 blocks = **494.6 s**
- N=65536: 15.46 × 2.103 = 32.51 s/block × 32 blocks = **1040.4 s**
- Gate total ≈ **1535 s** (precondition/load/finalize ≈ 0 per P13 cells≈total).
- Conservative (P13 max ratio 2.148 twice): 32×(15.67+33.66) = **1578.5 s**.
- +10% machine-variance headroom on conservative: **1736 s**.
- Cap 2100 s → margin ratio **1.33-1.37×**, headroom ≥ 360 s in the worst
  arithmetic above. The in-run wall guard and external `timeout 2100` coincide,
  so a breach fails closed as resource BLOCKED, never silently.

RSS/VmPeak projection:

- Smoke VmPeak: 549 MB through N=32768 (incl. full runner fake pass at frozen
  N, Part A wall 67.75 s — reproduces the operator's ~75 s note), **653 MB**
  at N=65536 real path. P13 VmPeak slope (+55 MB for the 8192→16384 doubling)
  extrapolates to ≈855 MB. Metric planes are `(65536,32)` float64 = 16.8 MiB
  each; P11 chunking caps the `(rows,32,32)` gather at chunk_rows=512
  (4 MiB/slice — the unchunked 536 MiB temporary cannot occur; contract
  check enforces it). Limit 2 GiB → margin **≥2.4×** (measured) / 3.1× (smoke).

RATIFIED: wall fits with explicit ~1.35× margin (thinner than P14's 1.54×
envelope — recorded as non-blocking observation 1); memory fits with ≥2.4×
margin. No cap/budget change is permitted (frozen); no change is needed.

## 8. Tests — PASS (re-run by reviewer, pinned interpreter, fresh basetemps)

- Focused:
  `TMPDIR=/tmp/p15-preexec-tmp /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python
  -m pytest comparison_bench/tests/test_nbpolar_empirical_genie_mid_n.py -q
  -p no:cacheprovider --basetemp=/tmp/p15-preexec-base/focused`
  → **15 passed** in 208.29 s. Raw evidence reproduced.
- Full NB-Polar suite:
  `... pytest comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider
  --basetemp=/tmp/p15-preexec-base3/full` → **335 passed** in 748.73 s
  (320 prior + 15 P15; operator reported 335 in 709.88 s — same count).
- Coverage vs P15-05 list, verified present: frozen K pins (both H spellings
  + leakage inequality), matrix constants + per-N/across-N separation,
  P13-helper identity (+ df=31 helper explicitly NOT shared), both-N grouping
  + 7 mis-grouping refusals with absent roots, order/allocation replay with
  closed-form pooled means, DEV residual formula + df=15 stats, df=15 literal
  + df=31 absence, residual purity (zero-genie), checkpoint refusal
  (sentinel untouched), partial-failure preservation (BLOCKED, 128 calls,
  32 rows), injected accounting + reopen guard, precondition BLOCKED stubs
  (zero genie), MemoryError classification, CLI-parse refusal (subprocess,
  exit 2), forbidden-access token scan.
- Tests never open the NPZ (only string `/nonexistent/channel_counts.npz`
  with the guard pre-set + loader patched to raise), never use frozen streams
  1960..93 as inputs (own seeds 2026091770..1785; disjointness asserted
  against frozen + across lists), never invoke production paths
  (forbidden-loader/genie patches; `emn._NPZ_CONTENT_OPENED is False`
  asserted).
- 1e-9 tolerance adjudication: operator's in-wave finding is benign
  summation-order noise — runner numpy mean vs test `math.fsum` differ
  ~1.8e-12 absolute at residual scale ~1e4 (relative ~2e-16). It does NOT
  affect gate correctness (no gate compares cross-implementation means except
  the replay check, which already allows 1e-9 at line 1389). **Implication
  for Pre-RESULT (binding):** independent recomputation of mean/std/UCB and
  TRAIN-residual replay MUST use absolute tolerance ≥1e-9 (not exact equality,
  not tight relative); min/max and orders/allocations stay exact.

## 9. Bounded smoke — PASS

`/tmp/p15_smoke.py` (injected 1024×1024 tables, temp roots, single-thread
frozen env; NPZ never touched, `_NPZ_CONTENT_OPENED False` at end):

- Part A (runner + FakeGenie/fake_sample seams at frozen N): exactly the five
  files, pre-open stubs then per-block checkpoints; wall 67.75 s;
  VmPeak 549716 kB; outcome `BLOCKED(two_n_cells_complete)` (correct for
  non-frozen test seeds — shape gate); 128 genie calls / 32 jsonl rows;
  per-record + per-cell resources present.
- Part B (real genie path timing): see §7 table. Grounds the wall projection.

## 10. Scope/premises — PASS

- `git status --porcelain` Wave-A set for P15: untracked
  `comparison_bench/src/.../empirical_genie_mid_n.py`,
  `comparison_bench/tests/test_nbpolar_empirical_genie_mid_n.py`,
  `.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/`,
  `openspec/.../specs/nbpolar-phase4-p15/`, plus the P15 section of the
  shared `tasks.md`. No accepted-module / P12-P14 / old-root / `results/` /
  `outputs_comparison/` writes attributable to this wave (§3). No commit
  made. HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` unchanged (matches
  freeze record).
- Frozen seeds 1960..93 fresh: repo-wide grep hits ONLY the four P15 files
  (runner, test-docstring/constants, spec, tasks) + the packet docs —
  disjoint from all priors by construction ✓.
- Queue dir holds only the six packet files; gate root
  `empirical_genie_mid_n_gate/` ABSENT ✓. NPZ stat-only `25166822` ✓
  (re-stated at review time; content never opened). STATUS reads/attempts
  still 0/1, result null ✓.

---

## Wave-C exit-code / label reading rule (verified in code)

- `main()` (lines 1508-1541): run completes → prints JSON summary → **exit 0**.
  **Exit 0 ⟺ completed label persisted: read `outcome_label`** from
  `aggregate_summary.json` (CANDIDATE / NOT_CONFIRMED / BLOCKED).
- `except (ValueError, FileExistsError, OSError) → return 2`: covers pre-open
  refusals (absent root, CLI parse — argparse itself exits 2, chunk contract,
  N/bps/seed-grouping, size mismatch, reopen guard) AND post-open contract
  BLOCKEDs (`TargetPopulationContractError` subclasses `ValueError`,
  target_construction.py:340). Disambiguate by root/stubs per P14 precedent:
  **exit 2 + root absent (or only pre-existing content) = pre-open refusal,
  consumption NOT spent** — except the reopen-guard path, which fires after
  stub creation; **exit 2 + five stub files + BLOCKED aggregate = post-open
  contract BLOCKED, consumption spent**.
- Any other non-zero (uncaught `EmpiricalGenieMidNResourceError` from
  wall/RSS stops, `MemoryError` escape, unexpected exception + traceback) =
  post-open resource/unexpected failure: evidence is whatever checkpoints
  exist (RUNNING summary + jsonl + construction), consumption spent,
  **never rerun** (single attempt already consumed at first open).

## Complete frozen record

- K: N=32768 → 6811 (raw 6811.785936024635); N=65536 → 13636 (raw
  13636.37187204927); `floor((1.3*N*0.8010378248977232-64)/5)`;
  leakage 34119 / 68244 bits; H1=0.02428054681872374, H2=0.7767572780789994.
- Seeds: TRAIN 2026091960..63 + 2026091980..83; DEV 2026091970..73 +
  2026091990..93; 4 blocks/stream; per-stream RNG restart; 16+16 per N;
  128 planned genie calls; GF(32)/poly-37/alpha-2; chunk_rows=512; f=1.3.
- Command: byte-identical across TASK_PACKET P15-06, P15_FREEZE.md, and
  runner `FROZEN_COMMAND` (verified programmatically: packet==runner,
  freeze==runner, packet==freeze → True). Root:
  `.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate/`
  (absent). Budgets: `ulimit -v 2097152`, `timeout 2100`, single-thread
  BLAS/OpenMP, `MALLOC_ARENA_MAX=2`. Schema: exactly five files, stubs
  pre-open, checkpoint per block, scalar-only. Gates: 12 in
  `INTEGRITY_GATE_ORDER` (target_population_contract,
  two_n_cells_complete, streams_disjoint_frozen,
  orders_valid_frozen_before_dev, budget_allocation_reproduced, risks_finite,
  zero_genie_exceptions, truth_isolation, no_unregistered_calls,
  checkpoint_accounting_consistent, attempt_read_accounting_exact,
  resource_limits_met_and_no_abort). Labels: CANDIDATE / NOT_CONFIRMED /
  `BLOCKED(<earliest>)`; df=15 factor 1.753050356; any-UCB ≤ 0.01 + smallest N.

## Findings

Blocking issues: none.

Non-blocking suggestions (no pre-execution repair; frozen point untouched):

1. Wall margin (~1.35×) is thinner than P14's 1.54× envelope. Projection is
   grounded twice (accepted P13/P14 cells + today's same-machine real-path
   smoke), and breach fails closed via coincident wall guard + external
   timeout — but a >33% machine slowdown vs projection would cost the single
   attempt. Accepted residual risk; operator should run on a quiet machine.
2. Wall/RSS resource stops re-raise `EmpiricalGenieMidNResourceError` without
   rewriting `aggregate_summary.json` to BLOCKED (the MemoryError path does
   finalize). Last RUNNING checkpoint + jsonl + construction still preserve
   evidence; per the Wave-C rule the operator/Pre-RESULT must read exit≠0 +
   RUNNING summary as resource BLOCKED, never rerun. Pre-RESULT should assert
   this mapping explicitly.
3. Pre-RESULT must use absolute tolerance ≥1e-9 for mean/std/UCB/TRAIN-residual
   recomputation (summation-order noise ~1e-12 absolute at residual scale
   ~1e4); exact-equality or tight-relative checks would false-fail. Min/max,
   orders, (K1,K2), call counts, freeze-SHA stay exact.
4. `test_v72p2d7_*` collection errors (22) are pre-existing dirty-tree
   cleanliness assertions, unrelated to P15; the acceptance suite is exactly
   `test_nbpolar_*.py` (335 green). No action in this packet.

## Checklist

- [x] Matches OpenSpec spec (P15 delta §§ requirements ↔ TASK_PACKET ↔ runner)
- [x] Tests pass (15 focused + 335 NB-Polar, pinned interpreter, fresh basetemps)
- [x] No scope creep (P15 footprint only; accepted modules untouched; no
      BEC/tag/Toeplitz/operational/FER apparatus)
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? —
      No: no new failure mode or durable decision surfaced. The 1e-9
      summation-noise note and the resource-stop mapping note are recorded
      above for Pre-RESULT; batch any ledger updates at the milestone per
      AGENTS.md §10.4.

## Closure statements

- The V25 `channel_counts.npz` was NEVER opened by this review (metadata
  `stat` size 25166822 bytes only, same as frozen expectation).
- The real gate command was NEVER run by this review (all execution used
  injected tables/arrays, test seeds 2026091770..1785, and temp roots).
- No Model-F/HOLD/raw/real/EVAL/tag/FWHT/APP/SCL path was accessed; no
  P12/P13/P14/old-root write; no commit/push.
- `STATUS.yaml` reads/attempts still 0/1, result null; gate root still absent.
- Next gate: authorized single execution (Wave-C), then independent Pre-RESULT.
