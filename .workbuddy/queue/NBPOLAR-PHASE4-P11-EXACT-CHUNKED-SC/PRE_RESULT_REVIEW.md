# Pre-RESULT review — NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC (independent, read-only)

Reviewer: independent reviewer-go (did not write the code, freeze the plan, or run the gate).
Scope: Tier-Y packet `NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC`, Wave-C single execution only.
Constraint observed: gate NEVER rerun (attempt 1/1 consumed by the operator run; no
`sc_chunked_gate` invocation); no artifact/evidence/raw/held-out/real/EVAL/tag/protocol
access; no old-root writes; no commit/push. Evidence is the four frozen files under
`exact_chunked_sc_gate/` plus read-only inspection of `sc.py` / `sc_chunked_gate.py`.
This file is the SOLE write of this review.

## Verdict: PASS_WITH_COMMENTS

All persisted numbers recompute exactly from the records (see §§1–6); bounded wording
satisfies P11-04/P11-05/P11-07 (§7); focused + full suites green with the pinned
interpreter and fresh basetemps (§8); scope clean (§8). Two non-blocking comments
(§9: carried-over consumption-point label; stale `STATUS.yaml` lifecycle fields) require
no rework and do not affect the evidence. Recommendation: main thread may accept the
`EXACT_CHUNKED_SC_CANDIDATE` label (acceptance itself remains main-thread business).

---

## 1. Root: exactly four frozen files, scalar-only — PASS

Command:

```bash
ls -1 .workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/
ls -1 .../exact_chunked_sc_gate/ | wc -l
```

Raw evidence:

```text
equivalence_records.json
frozen_plan.json
report.md
scaling_record.json
4
```

Top-level keys and sizes (recomputed, not copied):

```text
frozen_plan.json: [attempt_accounting, budgets, command, environment, gates, label, packet, parameters], 2152 bytes
equivalence_records.json: [full_sc, paired_n65536, primitive_cells, primitive_totals, validation_contract, validation_totals], 23808 bytes
scaling_record.json: [rss_final, scaling_record, wall_total_s], 580 bytes
report.md: 95 lines (read in full, §§3–7 below)
```

Scalar-only audit (walked every JSON leaf; non-scalar/suspect leaves found):

```text
frozen_plan.json: 0
equivalence_records.json: 0
scaling_record.json: 0
```

Persisted shapes are scalars only: equality booleans, mismatch counts,
`max_finite_abs_err` magnitudes, support counts, exception type+message strings,
walls, RSS dicts, accounting, gates. No input vectors, decisions, metrics, decoded
keys, raw arrays, or artifacts. (`report.md` matches the terms "input vectors /
decisions / metrics / decoded keys / raw arrays" only inside its exclusion sentence
"Outputs persist no input vectors, decisions, metrics, decoded keys, raw arrays or
artifacts: only parameters, environment, …", which is the required P11-05 statement.)

Partial-evidence fallback NOT taken: `paired_n65536` and `scaling_record` are both
present (non-`None`), i.e. the exit-0 full-evidence path (§6). PASS.

## 2. Frozen identity: seed/env/params/command/attempts — PASS

Command:

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c "[dump fp parameters/command/env/accounting/budgets/label]"
diff <(sed -n '116p' .../TASK_PACKET.md) <(sed -n '47p' .../P11_FREEZE.md)  # -> BYTE_IDENTICAL
```

Raw recomputed values from `frozen_plan.json`:

```text
seed: 2026091800 (== 2026091800: True)
chunk_rows: 512 (== 512: True)
primitive_rows: [1, 31, 32, 33, 127, 128, 129, 511, 512, 513, 2048]
primitive_kinds: [moderate_m20, wide_m160, neginf_support]
full_sc_N: [64, 256], paired_N: 65536, large_N: 262144
arm_order_paired: direct_before_chunked
rng_stream_order: primitives(rows asc x kinds)->V0(fixed)->N64 controls->N256 controls->N65536 block->N262144 block; C4 search draws data-dependent in count, stream-ordered
command tokens: --seed 2026091800 True; --chunk-rows 512 True; out-dir exact_chunked_sc_gate True; timeout 600 True; ulimit -v 2097152 True
environment: interpreter /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python; python 3.12.3; numpy 2.5.3; Linux WSL2 x86_64, cpu 8
attempts: allowed 1 / consumed_before 0 / consumed_by_this_run 1
artifact_reads: authorized 0 / consumed 0
budgets: timeout_s 600; vsz_kb 2097152; rss_hard_limit_bytes 1610612736; planning_wall_s_report_only 120.0; planning_rss_bytes_report_only 1073741824
label: EXACT_CHUNKED_SC_CANDIDATE
```

- Seed `2026091800`, chunk-rows `512`, params, env, and budgets match P11-04/P11-06
  and `P11_FREEZE.md` §2/§6.
- `TASK_PACKET.md:116` vs `P11_FREEZE.md:47` command lines: `diff` → `BYTE_IDENTICAL`;
  the persisted `frozen_plan.command` carries the same cwd/interpreter/module/args/root
  (the `&&`-joined semantic equivalent ratified at Pre-EXECUTE §8).
- Attempt accounting: 1 allowed / 0 before / 1 consumed by this run; 0 artifact reads
  authorized/consumed. Consistent with the one-shot rule (consumption point wording,
  see non-blocking comment §9-C1, does not change the 1/1 count).
- No artifact access possible (runner's only `open()` is `/proc/self/status` for RSS;
  no `np.load`/`stat`/`read` of any data path — verified by grep, §8). PASS.

## 3. Semantic matrix: 33 primitives + 16 V0 + 18 full-SC — PASS

### 3a. Primitive cells (33 = 11 rows × 3 kinds)

```text
n_cells: 33
n_exact_equal True: 33
n_support_equal True: 33
n_max_finite_abs_err == 0.0: 33
n_support_mismatch_rows == 0: 33
distinct rows: [1, 31, 32, 33, 127, 128, 129, 511, 512, 513, 2048] (matches frozen list)
distinct kinds: [moderate_m20, neginf_support, wide_m160] (matches frozen list)
persisted primitive_totals: {cells: 33, all_exact: True}
recomputed all-exact (exact AND support AND err==0.0 AND mismatch==0 over all 33): True
```

Every cell line in `report.md` (33 lines, §§11–43) shows
`exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0`. PASS.

### 3b. V0 invalid-input cases (16)

```text
n_cases: 16; n_parity True: 16; n_both_raised: 16; n_type+message_equal: 16
recomputed all_parity (parity AND both raised AND type+message equal, all 16): True
persisted validation_totals: {cases: 16, all_parity: True}
```

Type+message parity per case (baseline == chunked, recomputed):

```text
nan_entry                  | ValueError | metric contract: logp_x must not contain NaN
posinf_entry               | ValueError | metric contract: logp_x must not contain positive infinity
all_neginf_row             | ValueError | metric contract: every logp_x row needs finite support
width_mismatch             | ValueError | field/shape contract: logp_x width 33 != field q 32
non_power_of_two_N         | ValueError | field/shape contract: block length N=48 is not a positive power of two
rank1_input                | ValueError | metric contract: logp_x must have shape (N, q), got shape (32,)
boolean_input              | TypeError  | metric contract: logp_x must hold float log-scores, got boolean input
positions_out_of_range     | ValueError | known-coordinate contract: positions must lie in 0..7
positions_repeat           | ValueError | known-coordinate contract: positions must not repeat
positions_values_length    | ValueError | known-coordinate contract: positions and values lengths differ
positions_none_values_given| ValueError | known-coordinate contract: positions and values must be given together
positions_given_values_none| ValueError | known-coordinate contract: positions and values must be given together
float_positions            | TypeError  | known-coordinate contract: positions must hold integers
boolean_positions          | TypeError  | known-coordinate contract: positions must hold integers, got boolean input
value_out_of_range         | ValueError | known-coordinate contract: known_values symbols must lie in 0..31
negative_position          | ValueError | known-coordinate contract: positions must lie in 0..7
```

PASS.

### 3c. Full-SC controls (9 per N × 2 N = 18)

Recomputed per control (status/u_hat/x_hat/metrics/scores/mask/provenance fields):

```text
N=64 F1_moderate:                        parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=64 F2_wide:                            parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=64 F3_neginf_jmod5_evenoff:            parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=64 K4_known25pct_positive_support:     parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=64 C3_x11_pattern_positive_support:    parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=64 C4_impossible_disclosed_value:      parity True, ImpossibleDisclosedValueError, t=0, k=16, attempts=1,
                                         message "impossible disclosed value: U[3]=2 has exact-zero support" (direct == chunked)
N=64 T5_exact_tie / T5_ramp / T5_near_tie: parity True each, status ok, u_mm 0, merr 0.0
N=64 n_parity_true: 9/9
N=256 F1_moderate:                       parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=256 F2_wide:                           parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=256 F3_neginf_jmod5_evenoff:           parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=256 K4_known25pct_positive_support:    parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=256 C3_x11_pattern_positive_support:   parity True, status ok, u_mm 0, x_mm 0, merr 0.0, serr 0.0, prov True
N=256 C4_impossible_disclosed_value:     parity True, ImpossibleDisclosedValueError, t=0, k=16, attempts=1,
                                         message "impossible disclosed value: U[3]=12 has exact-zero support" (direct == chunked)
N=256 T5_exact_tie / T5_ramp / T5_near_tie: parity True each, status ok, u_mm 0, merr 0.0
N=256 n_parity_true: 9/9
```

- C3-pattern, C4-impossible (disclosed coordinates/values `U[3]=2` at N=64 and
  `U[3]=12` at N=256 recorded above), and T5 ties (exact/ramp/near-tie all parity)
  verified element-by-element.
- Default-512 vs `None` pairing: the frozen params fix `chunk_rows: 512`, the runner
  enforces `chunk-rows == 512` before any decode, the persisted arm order is
  `direct_before_chunked`, and every comparison record pairs the direct (`None`) arm
  against the default-512 arm with zero mismatches. PASS.

## 4. N=65536 paired direct-first exact parity — PASS

```text
arm_order: direct_before_chunked (== frozen P11-04 step-2 order)
N: 65536
status_equal True, status ok
u_hat_exact True, u_hat_mismatches 0; x_hat_exact True, x_hat_mismatches 0
metrics_exact True, max_finite_metric_abs_err 0.0, metrics_support_equal True, metrics_argmax_mismatches 0
scores_exact True, max_finite_score_abs_err 0.0
known_mask_exact True, known_count_equal True, provenance_equal True
parity True
recomputed paired-exact (all of the above AND parity): True
walls (report-only): direct 15.683720048000396 s, chunked 14.584007425000891 s
  -> report.md rounds to direct=15.684 chunked=14.584: True
rss_after: {ru_maxrss 710504448, VmHWM 710504448, peak 710504448}
```

Wording check: `report.md` step-2 line presents the two walls bare
(`wall_s direct=15.684 chunked=14.584; rss_peak_bytes=710504448`) with no
throughput/speedup/superiority claim anywhere in the file (the only "throughput"
sentence is the explicit denial quoted in §7). PASS.

## 5. N=262144 completion + RSS — PASS (comparisons recomputed myself)

```text
status: ok; finite_outputs: True
wall_s raw: 66.08841076899989 -> report.md 66.088: True
rss peak raw: 710504448 -> report.md 710504448: True
recomputed completion (status == ok AND finite_outputs is True): True
66.08841076899989 <= 120.0 (planning, report-only): True
710504448 < 1610612736 (hard gate): True (margin 900108288 bytes)
710504448 < 1073741824 (planning, report-only): True (margin 363237376 bytes)
hard limit stored in frozen_plan.budgets.rss_hard_limit_bytes: 1610612736
recomputed rss gate (peak < hard limit): True
wall_total_s raw: 97.95551134699963 -> report.md 97.956: True
rss_final: {ru_maxrss 710504448, VmHWM 710504448, peak 710504448}
```

`report.md` step-3 line keeps both planning targets explicitly report-only:
`wall_s=66.088 (planning target <=120.0 s report-only) rss_peak_bytes=710504448
(hard limit 1610612736; planning target 1073741824 report-only)`. PASS.

## 6. Gates/labels — PASS (all four recomputed, not copied)

Recomputation rules (from TASK_PACKET P11-04/P11-05 and the freeze):

- `semantic_parity` = 33 primitives all-exact (§3a) AND 16 V0 type+message parity (§3b)
  AND 18 full-SC parity (§3c).
- `paired_n65536_exact` = §4 full comparison parity with `direct_before_chunked`.
- `large_n262144_completion` = status `ok` AND finite outputs.
- `large_n262144_rss` = peak RSS < `budgets.rss_hard_limit_bytes` (1610612736).

Gate table:

```text
gate                        recomputed    persisted    match
semantic_parity             True          True         True
paired_n65536_exact         True          True         True
large_n262144_completion    True          True         True
large_n262144_rss           True          True         True
all four recomputed True: True
derived label: EXACT_CHUNKED_SC_CANDIDATE (all-true rule)
persisted label: EXACT_CHUNKED_SC_CANDIDATE
partial-evidence fallback taken: False (both records present; exit-0 path)
```

Label derivation verified: all-true → `EXACT_CHUNKED_SC_CANDIDATE`; no
`BLOCKED(<gate>)` path present in any record. PASS.

## 7. Bounded wording — PASS (report.md read in full, 95 lines)

Required elements, all present verbatim or in substance:

- Synthetic injected-data engineering gate only: report header gives seed/float64/
  GF(32)/chunk-rows; bounded paragraph scopes the claim to "the default-512
  allocation path is bitwise-equivalent to the accepted unchunked reference
  everywhere in the frozen matrix and completes the single N=262144 block within
  the frozen resource envelope". Present.
- Not FER/efficiency/key-rate/scaling/qualification/promotion: "This is not
  target-channel FER, efficiency, key-rate, scaling, qualification or promotion
  evidence; a candidate remains pending main-thread acceptance." Present.
- No throughput claim: "no throughput superiority claim is allowed" (explicit
  denial; the file's only "throughput" hit). No speedup/faster-than language
  anywhere. Step-2 walls are bare numbers with no comparative claim. Present.
- Single-draw variance disclaimer: "One draw cannot discriminate timing variance …
  and the 120 s / 1 GiB values are report-only." Present.
- 120 s / 1 GiB report-only: marked report-only in step-3 line, gates section
  (absent from hard gates), and `scaling_record.planning_targets_report_only`.
  Present.

Full bounded paragraph (report.md:94):

```text
A candidate means the default-512 allocation path is bitwise-equivalent to the accepted unchunked reference everywhere in the frozen matrix and completes the single N=262144 block within the frozen resource envelope. One draw cannot discriminate timing variance: no throughput superiority claim is allowed, and the 120 s / 1 GiB values are report-only. This is not target-channel FER, efficiency, key-rate, scaling, qualification or promotion evidence; a candidate remains pending main-thread acceptance.
```

PASS.

## 8. Tests/scope — PASS

### 8a. Re-run with pinned interpreter + fresh basetemps (`-q -p no:cacheprovider`)

Commands (gate command NOT invoked):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_sc_chunked.py -q -p no:cacheprovider --basetemp=/tmp/p11-preresult-chunked-basetemp
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest [all 18 test_nbpolar_*.py] -q -p no:cacheprovider --basetemp=/tmp/p11-preresult-full262-basetemp
```

Raw evidence:

```text
focused: 10 passed in 5.80s (exit 0)
full NB-Polar: 262 passed in 119.76s (exit 0) = 252 predecessor + 10 new
reviewer env at rerun: Python 3.12.3 / NumPy 2.5.3 (matches frozen_plan environment)
```

Expectation from the packet (10 + 262) met exactly. PASS.

### 8b. Implementation scope

- `git diff -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py`: only
  `_minus_block` (32 insertions, 4 deletions): keyword-only `chunk_rows=512` default,
  `None` golden path with the literal accepted expression, bool/non-`Integral` →
  `TypeError` / nonpositive → `ValueError` before allocation, contiguous slices in
  original order with per-slice `first_slice[:, index] + second_slice[:, None, :]` +
  `logaddexp.reduce(axis=2)` and a single full-matrix `_normalize_rows`. Allocation-only.
- `sc_decode` public signature unchanged at runtime:
  `(logp_x, *, field, alpha=2, known_positions=None, known_values=None)` — no `chunk`
  parameter; sole production call site passes no new argument.
- Forbidden-token grep on `sc.py` + `sc_chunked_gate.py`: only prose hits
  (`"environment"` in the env dict/report string). No FWHT/clipping/caching/reorder/
  dynamic-range/approx/env-config logic.
- Runner audit (read-only grep): `--seed`/`--chunk-rows`/`--out-dir` all
  `required=True` (no defaults); absent-root `FileExistsError` + frozen seed/chunk
  `ValueError`s precede RNG/first decode; `FROZEN_SEED = 2026091800`,
  `FROZEN_CHUNK_ROWS = 512`; `direct_before_chunked` persisted; `FOUR_FILES` exact-set
  post-write guard; only `open()` is `/proc/self/status` for RSS.
- Other `M`/`??` worktree entries (`__init__.py`, `empirical_*`, P3/P4–P10/X-probe
  queues, docs, `tasks.md` accumulation) are the pre-existing dirty worktree declared
  in `PRE_EXECUTE_REVIEW.md` §9 and `P11_IMPLEMENTATION_NOTES.md`; the P7/P8/X
  modules (`target_construction`, `target_rate`, `two_layer*`, `adaptive*`,
  `penalty*`, `incremental*`, `protocol`) are untracked pre-existing files, none
  modified by P11. P11's own set (`sc.py` delta, `sc_chunked_gate.py`,
  `test_nbpolar_sc_chunked.py`, `specs/nbpolar-phase4-p11/`, this queue dir,
  `tasks.md` P11 section) matches the declared packet scope. No `results/` /
  `workspace/probes/` / `outputs_comparison/` writes from gate or review
  (`git status --porcelain` on those roots: empty).
- HEAD unchanged: `ab173f2a5e17336383a897b941080b731ba3dd9e` before and after all
  checks; `git log --oneline -1` shows no new commit. No commit/push. PASS.

## 9. Findings

- Blocking: none.
- Non-blocking C1 (carried over from Pre-EXECUTE NOTE 4N1): `frozen_plan.json`
  `attempt_accounting.consumption_point` repeats the freeze label "first formal
  sc_decode call (step-1 N=64 F1_moderate direct arm)" while the runner's first
  `sc_decode` in code order is the V0 `nan_entry` direct arm. Ratified meaning is
  unchanged (ANY `sc_decode` in the frozen run consumes the attempt; 1/1 recorded).
  Optional future reword; NOT a reason to touch evidence.
- Non-blocking C2: `STATUS.yaml` still shows pre-execution lifecycle values
  (`attempts_used: 0`, `independent_pre_execute/result: pending`,
  `state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`). Lifecycle sync is main-thread
  business; the authoritative attempt record for this gate is `frozen_plan.json`
  (1/1) plus this review. No evidence impact.

## Closure statements

- The frozen gate was NOT rerun by this review (no `sc_chunked_gate` execution; only
  focused/full pytest with fresh test seeds and temp roots, plus read-only
  inspection and JSON recomputation).
- Attempt remains 1/1 consumed by the single Wave-C operator run, per
  `frozen_plan.json` (`attempts_allowed 1 / consumed_before 0 / consumed_by_this_run 1`);
  no further run is authorized by this review.
- No artifact/evidence/raw/held-out/real/EVAL/tag/protocol path was opened; no
  old-root or production output was written; no commit/push was performed; HEAD
  `ab173f2a5e17336383a897b941080b731ba3dd9e` unchanged.
- Gate root contains exactly the four frozen files; no extras were added by this review.
- This file (`.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/PRE_RESULT_REVIEW.md`)
  is the SOLE write of this review.
