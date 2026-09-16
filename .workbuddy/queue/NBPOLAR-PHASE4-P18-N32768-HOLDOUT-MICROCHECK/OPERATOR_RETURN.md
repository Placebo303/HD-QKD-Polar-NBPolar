# Operator return — Phase 4-P18 N=32768 1M-HOLD operational microcheck

- Task: `NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK` (Tier Y, single attempt)
- Operator: OpenCode implementation session, operator only (no acceptance)
- Date: 2026-09-16 (WSL); HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e`; branch `codex/nbpolar-phase0`
- Result label: `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE`
- State: `..._COMPLETE_PENDING_MAIN_THREAD_ACCEPTANCE`; this return is not an acceptance

## 1. Mission

Run the accepted P16/P17 operational point exactly once on the only three
complete, non-overlapping N=32768 blocks available in the V25 1M HOLD split
(frames 1600..1983): a real-input microcheck of loading, ordering, fixed-TRAIN
prior use, decoder behavior and accounting. It is not a FER gate and has no
recovery threshold.

## 2. Implementation and tests

- New runner: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_microcheck.py` (thin P18 wiring; accepted P16 `run_operational_block`/outcome/record/recount helpers and the P17 `verify_predecessor_construction` reused by import, unchanged).
- New focused tests: `comparison_bench/tests/test_nbpolar_holdout_microcheck.py`.
- New OpenSpec P18 delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p18/spec.md`; `tasks.md` P18 section appended, no box checked.
- Focused suite: 26 passed. Full NB-Polar suite (`test_nbpolar_*.py`, 25 files): 409 passed (383 + 26). Both re-run green in the resuming sessions with the pinned interpreter and fresh `/tmp` basetemps.
- Zero protected opens during tests: an independent `builtins.open`/`os.open` audit plugin reported `protected_open_hits: []` for both the focused and full runs (guard sanity-checked to fire on both protected basenames); the runner tests replace both loaders with asserting stubs.
- No change to decoder, prior, construction, disclosure, tag, packing or outcome semantics. No commit, no push.

## 3. Pre-run checks (before the single execution)

- Independent `reviewer-go` Pre-EXECUTE review: **PASS** (frozen command byte-equal to `holdout_microcheck.FROZEN_COMMAND`; predecessor/manifest identities and protected-input stat values re-verified; rulings R8 invented flags and R9 unreachable post-open branch ratified; mirror-path convention noted).
- Output root `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/` absent before execution; reads/attempts 0/1 each at that time.
- Neither protected input content-opened by either review (stat/JSON only).

## 4. Frozen command and run outcome

Verbatim frozen command (four lines, as executed):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_microcheck --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --hold-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --hold-frames 1600 1999 --block-frames 128 --remainder-frames 1984 1999 --tag-master 2026092050 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck
```

- Exit code 0; stderr empty.
- In-run `wall_s` 37.274417 s (≤ 600 s); outer wrapper ≈ 55.9 s.
- One execution only; no rerun, repair, retune, seed/parameter change or cleanup.

## 5. Identity, manifest and preconditions

- Predecessor P16 digest match true: recomputed = stored = flag = `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`; N=32768, K1=319, K2=6492, K_total=6811, leakage=34119, f=1.2998502888172847 ≤ 1.3.
- Split manifest `nbldpc_v25_split_manifest_v1`: 1M `type2_1M_20260121_184040` HOLD = 400 frames / 102400 pairs (required 400/102400); TRAIN 1200/307200, VAL 400/102400.
- Preconditions 7/7 true: H1 0.024280546818678802 (literal 0.02428054681872374, diff 4.494e-14), H2 0.7767572780789994 (diff 0.0), total 0.8010378248976782 (literal 0.8010378248977232, diff 4.508e-14), floor entropy change 5.1600945738528026e-11 ≤ 1e-9, column dev 1.1357581541915351e-13 ≤ 1e-12, `p_b_sum` 1.0, no zero Bob column.

## 6. Consumption

- Attempts allowed 1 / consumed 1; consumption point = first protected content open (`load_v25_channel_counts`).
- NPZ content opens 1/1; HOLD parquet content opens 1/1; `retries` 0, `reopen_attempted` false, `retry_after_open` false.
- Input stats before == after and unchanged: NPZ 25,166,822 B / mtime_ns 1787074449691122000; parquet 1,354,289 B / mtime_ns 1789155517259296100. No reopen.

## 7. Per-block outcomes (descriptive; no threshold)

| block | frames | raw SER | L1 NLL bits | L2 NLL bits | total NLL bits | outcome | L1 correct | tag | key-dep bits | public bits | CE ratio | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1600..1727 | 0.240936279296875 | 773.8421894692976 | 26815.50805586987 | 27589.350245339167 | verify_failed | true | false | 34119 | 327743 | 1.2366728355903898 | 11.856873 |
| 1 | 1728..1855 | 0.23980712890625 | 868.6436203445395 | 27015.516878425602 | 27884.160498770143 | verify_failed | false | false | 34119 | 327743 | 1.2235978917674373 | 11.882077 |
| 2 | 1856..1983 | 0.240264892578125 | 806.8510674338244 | 26881.237733518323 | 27688.088800952148 | verify_failed | false | false | 34119 | 327743 | 1.232262733815947 | 11.76401 |

Each block: frame_count 128 (× 256 pairs = 32768 symbols), one L1 + one candidate-conditioned L2 SC, one 64-bit tag, `l1_provenance` PRIOR_ONLY, `l2_provenance` CANDIDATE_CONDITIONED, `truth_leak_violation` false, `error` null.

Aggregate: L1 2449.3368772476615 bits, L2 80712.26266781379 bits, total 83161.59954506146 bits; sample CE-normalized disclosure ratio 1.230820481567787 (descriptive only, NOT qualification efficiency); key-dependent bits 102357 (34119 × 3); public-control bits 983229 (327743 × 3); tag invocations 3; SC calls 6; outcome counts exact 0 / undetected 0 / verify_failed 3 / decode_failed 0 / nonfinite 0 / resource_abort 0.

Transcript recount: `l1_disclosure` 3, `l2_disclosure` 3, `verification_tag` 3; `mismatches` [].

Unused remainder: frames 1984..1999, 16 frames / 4096 symbols, `used: false`.

## 8. Resources

| item | value | budget |
|---|---|---|
| in-run wall_s | 37.274417 | ≤ 600 s |
| external timeout | not fired | 600 s |
| peak RSS | 520798208 B | ≤ 2147483648 B (2 GiB) |
| `ulimit -v` virtual | 2097152 KiB | 2097152 KiB |
| per-block VmPeak (kB) | 1747608 / 1765524 / 1765524 | ≤ 2097152 |
| per-block VmSize (kB) | 1583760 / 1601680 / 1583760 | — |
| per-block RSS HWM (B) | 503291904 / 520798208 / 520798208 | — |
| resource stop | false (reason null) | — |
| threads/env | `OPENBLAS/OMP/MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2` | as frozen |

## 9. Integrity gates (17/17 true)

| gate | result |
|---|---|
| predecessor_construction_identity | true |
| hold_split_manifest_identity | true |
| target_population_contract | true |
| hold_population_exact | true |
| blocks_exact_with_declared_remainder | true |
| orders_valid_k_replay_f_within_budget | true |
| sc_calls_exact | true |
| tags_exact | true |
| buckets_disjoint_exhaustive | true |
| truth_isolation | true |
| undetected_zero | true |
| nonfinite_zero | true |
| disclosure_recount_exact | true |
| one_open_per_protected_input | true |
| input_stat_unchanged | true |
| no_unregistered_access | true |
| resource_limits_met_and_no_abort | true |

`failing_integrity_gates` []; `integrity_all_pass` true; `provenance_violations` 0.

## 10. Label derivation

All 17 integrity gates true → `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE`,
regardless of the 0/3 exact outcomes. The label path consumes only the
integrity gates dict; `decision.recovery_threshold` is `null`; there is no
exact-count, Wilson, FER, winner, promotion or recovery threshold anywhere in
this gate. The 0/3 exact outcomes (`verify_failed` × 3, `undetected` 0) are
descriptive real-input observations, **not** a gate and not a pass/fail
threshold; `BLOCKED(<earliest gate>)` was not taken and recovery was never
reinterpreted as an integrity gate. `undetected` is never success.

## 11. Reviews

- Independent Pre-EXECUTE review: **PASS** (`PRE_EXECUTE_REVIEW.md`).
- Independent Pre-RESULT review: **PASS_WITH_COMMENTS** (`PRE_RESULT_REVIEW.md`); zero blocking issues; all 17 gates, the P16 identity,
  preconditions, per-block and aggregate arithmetic, accounting/recount,
  consumption/input stats, resources and bounded wording independently
  recomputed. Comments are non-blocking process notes only.
- Pre-RESULT resumption note: the first Pre-RESULT reviewer attempt
  (`reviewer-go-backup`, session `ses_f59cc2717ffeJejCxUJCt4vp5Y`) was
  manually terminated mid-run (its full-suite run interrupted). The review was
  completed as a resumption from that attempt's saved transcript; the resuming
  session independently re-verified every load-bearing number and re-ran both
  suites fresh (26 focused / 409 full, both zero protected opens) before
  writing the review file. The gate itself was not rerun; output-root mtimes
  are unchanged and no repo file was written after 01:52:10 except the review.

## 12. Bounded scope

Real-input operational microcheck of the frozen V25 1M HOLD split at N=32768
only (three registered chronological blocks, frames 1600..1983), at the fixed
P16 construction and fixed floor-1e-15 TRAIN prior. Descriptive
loading/ordering/prior/decoder/accounting evidence only: not real-frame FER,
reconciliation efficiency, leakage, key rate, scaling superiority,
qualification or promotion. The CE-normalized disclosure ratio is a sample
descriptive ratio and is NOT qualification efficiency. The unused remainder
(frames 1984..1999) was never used. No pooling with TRAIN/VAL/P16/P17.

## 13. Unrun stages, no-commit statement

- Unrun stages: none remaining in the packet except main-thread acceptance
  (owner: main thread). No box in `tasks.md` is checked by the operator.
- No code, artifact, old-root or protected-input change beyond the declared
  P18 wave; neither protected input was reopened.
- No commit and no push.

**This return is not an acceptance, not a qualification and not a FER result.
Main-thread acceptance remains separate.**
