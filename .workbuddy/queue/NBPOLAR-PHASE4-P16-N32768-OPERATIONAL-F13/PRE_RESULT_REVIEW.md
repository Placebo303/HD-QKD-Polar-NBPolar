# Pre-RESULT review — NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13 (Tier-Y, independent)

Reviewer: fresh independent reviewer-go (did not write code, freeze plan, or run gate).
Read-only except this file. Gate NOT rerun (reads 1/1 + attempts 1/1 spent).
NPZ NOT reopened (metadata `stat` only). No Model-F/HOLD/raw/real/EVAL access;
no P12–P15/old-root writes; no commit/push. HEAD unchanged.

## Verdict: PASS_WITH_COMMENTS

All 13 integrity gates recomputed TRUE from records, both scientific gates
recomputed TRUE from an independent 62/64 recount + own Wilson implementation,
label `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` uniquely correct per
frozen rule. Comments (non-blocking): (a) classification sits EXACTLY on the
recovery threshold with ZERO-count margin — one fewer exact flips to
NOT_CONFIRMED (see §3); (b) `k_total_raw` repr dust vs literal recomputation
(both floor 6811, immaterial); (c) `wall_s` vs `resources.wall_s` per-block
sums differ by 18 ms total (immaterial). No blocking issue. No scope creep.

---

## 1. Root inventory + scalar-only audit (recomputed)

Commands:

```bash
ls -1 .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/
ls -l .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/
# jsonl keys + scalar check via pinned interpreter (see §2 commands)
```

Raw numbers:

- Files: exactly 5 — `aggregate_summary.json`, `construction_and_allocation.json`,
  `frozen_plan.json`, `per_block_outcomes.jsonl`, `report.md`. No extras,
  sidecars, or stub markers (`RUNNING`/pending strings absent; final
  `outcome_label` is CANDIDATE, `integrity_all_pass` true in artifact).
- `per_block_outcomes.jsonl`: 64 rows. Every row carries the same 25 frozen
  keys: `block_index, error, exact, k1, k2, key_dependent_bits, l1_decode_failed,`
  `l1_error_type, l1_executed, l1_provenance, l2_decode_failed, l2_error_type,`
  `l2_invoked, l2_provenance, l2_skipped_by_l1_failure, label_match, nonfinite,`
  `outcome, public_control_bits, resources, stream_seed, tag_invoked, tag_pass,`
  `truth_leak_violation, wall_s`. `resources` holds only
  `{rss_bytes_hwm, vm_peak_kb, vm_size_kb, wall_s}` scalars.
- Scalar-only: all row values + resource sub-values are None/bool/int/float/str;
  zero non-scalar values observed. Banned-substring scan over jsonl keys:
  `counts/sampled/truth/decoded/label_hat/label_true/key/metric_plane/metric/`
  `tag_seed/seed_bits/rng_state/high_true/low_true/alice/bob_symbol` — all absent.
- Aggregate/construction/frozen_plan banned walk: no `count_table`,
  `sampled/truth_vector/decoded_label/decoded_key/metric_plane/tag_seed/seed_bits/`
  `rng_state` keys. Only hit is `tag_seed_domain` template string
  `nbpolar-p16-operational-f13-seed:<master>:<n>:<block_index>` (public domain,
  not raw seed). `l1_order/l2_order` (32768 ints each) + pooled means are the
  only large arrays; both are public orders/risks per packet P16-05. No counts,
  sampled/truth vectors, decoded labels/keys, metric planes, raw tag seeds.
- Aggregate top keys (42): analysis/mode/repository/n/q/source/input_mode/counts_path,
  chunk_rows/tag_bits/target_f/train/dev seeds+totals+bps, entropy, construction,
  outcome_counts/exact_count/exact_fraction/recovery/wilson_boundary_check,
  disclosure, attempt_read_accounting, integrity/integrity_all_pass/
  failing_integrity_gates/outcome_label, sc_calls/genie_calls/planned_*,
  provenance_violations, wall_s/rss_bytes_peak/resource_stop_*.

## 2. Outcome recount — INDEPENDENT (classification-deciding)

Command (pinned `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`):

```python
rows=[json.loads(l) for l in Path(".../per_block_outcomes.jsonl").read_text().splitlines()]
Counter(r["outcome"] for r in rows)
# per-stream totals, non-exact identities, l1/l2/tag/label/truth sums,
# bucket-consistency loop (exact ⟺ tag True+label True; verify_failed ⟺ both False)
```

Raw numbers (mine, not copied):

- n=64. Tallies: exact 62, undetected 0, verify_failed 2, decode_failed 0,
  nonfinite 0, resource_abort 0. Sum 62+0+2+0+0+0=64. `outcome` values observed:
  only `exact`, `verify_failed`.
- The two non-exact rows are EXACTLY:
  - stream 2026092015, block_index 5, outcome `verify_failed`, tag_pass False,
    label_match False, exact False, l1_executed True, l2_invoked True,
    nonfinite False, error None, l1_decode_failed False, l2_decode_failed False,
    truth_leak_violation False, k1 319/k2 6492, key bits 34119, public 327743,
    tag_invoked True;
  - stream 2026092017, block_index 3, outcome `verify_failed`, identical flags
    (tag False, label False, exact False, l1 True, l2 True, no error).
- Per-stream completeness (8 DEV streams × 8 blocks, indices 0..7 each):
  2026092010 8/8 exact; 2011 8/8; 2012 8/8; 2013 8/8; 2014 8/8;
  2015 7/8 (one verify_failed at block 5); 2016 8/8; 2017 7/8 (block 3).
  Seven streams 8/8 exact; the two failures are isolated singletons in distinct
  streams. No stream missing/duplicated; block indices sorted 0..7 per stream.
- Bucket exclusivity + consistency: `consistency_bad=[]`. Every `exact` row has
  tag_pass True + label_match True + exact True; every `verify_failed` row has
  tag False + label False + exact False. No `undetected` (which would be
  tag True + label False) present. `error` is None on all 64 rows.
- Sums: l1_executed 64, l2_invoked 64, l1_decode_failed 0, l2_decode_failed 0,
  l2_skipped_by_l1_failure 0, tag_invoked 64 (pass 62 / False 2),
  label_match True 62 / False 2, truth_leak_violation 0, nonfinite True 0.
  Uniform (K1,K2,key,public) set: single tuple (319, 6492, 34119, 327743).

## 3. Wilson + scientific gates (own implementation)

Command:

```python
import math
z=1.6448536269514722
def wilson_lb(k,n,z=z):
    p=k/n; d=1+z*z/n; c=p+z*z/(2*n)
    m=z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return (c-m)/d
```

Raw numbers:

- 62/64 fraction = 0.96875.
- My Wilson one-sided 95% LB (z=1.6448536269514722): 62/64 → 0.9098711859061207.
  Persisted `recovery.wilson_lower_bound` = 0.9098711859061207 — exact match.
  Persisted `wilson_boundary_check.lb_62_of_64` = 0.9098711859061207 — match.
  Rounded boundary 0.9098711859 — match.
- My 61/64 LB → 0.8883797143731994. Persisted `lb_61_of_64` =
  0.8883797143731994 — exact match. Rounded 0.8883797144 — match.
- Gates: exact≥62/64 TRUE (62≥62, count margin 62−62=0); Wilson LB≥0.90 TRUE
  (0.9098711859061207≥0.90, margin +0.009871185906120683 ≈ +0.0099).
- ZERO-MARGIN STATEMENT (blunt, neutral): the run sits EXACTLY on the recovery
  threshold. ONE fewer exact (61/64 → fraction 0.953125, LB 0.8883797143731994)
  would make exact-gate FALSE and Wilson-gate FALSE, flipping the frozen-rule
  classification from CANDIDATE to NOT_CONFIRMED. The 62/64 outcome is a pass
  with no count buffer; it must not be described as clearance above threshold.
- `recovery` persisted: exact_count 62, total 64, exact_at_least_62 TRUE,
  wilson_lower_bound_at_least_0p90 TRUE, pass TRUE, wilson_z 1.6448536269514722,
  wilson_min 0.9, boundaries 0.9098711859/0.8883797144 — all consistent with
  my recomputation.

## 4. Preconditions / consumption / construction (recomputed)

Commands: parsed `aggregate_summary.json:entropy/attempt_read_accounting/
construction`, `frozen_plan.json:artifact_read_accounting`, `stat` on NPZ
(metadata only), K/f arithmetic with `math.floor` (no repo code).

Raw numbers:

- H1 observed 0.024280546818678802 vs literal 0.02428054681872374,
  diff 4.4939746368655165e-14 ≤1e-12 TRUE.
- H2 observed 0.7767572780789994 vs literal 0.7767572780789994, diff 0.0 TRUE.
- Total observed 0.8010378248976782 vs literal 0.8010378248977232,
  diff 4.5075054799781356e-14 ≤1e-12 TRUE.
- Floored total 0.8010378249492791; floor change 5.1600945738528026e-11 ≤1e-9 TRUE.
- Column deviation 1.1357581541915351e-13; p_b sum 1.0. All 7 checks recorded
  true: no_zero_bob_column, p_b_normalized, conditional_columns_normalized,
  h1/h2/total_matches_literal, floor_entropy_change_at_most_1e-9. Ratified
  semantics (literals within 1e-12, floor guard ≤1e-9) verified from records;
  NPZ content not reopened to re-derive (forbidden).
- Consumption: reads 1/1 (consumed_before 0, by_run 1, allowed 1), attempts 1/1
  (before 0, by_run 1, allowed 1), open_count 1, reopen_attempted False,
  retries 0, retry_after_open False, stat_size_checked True,
  observed_npz_bytes 25166822 = expected_npz_bytes 25166822. Frozen-plan
  accounting mirrors 1/1, 1/1, no reopen. Consumption at first open spent.
- NPZ stat (metadata only, no open): size 25166822 bytes, mtime 2026-08-19
  01:34:09 — matches `expected_npz_bytes` 25166822, unchanged.
- Calls: TRAIN genie 32/32 (16 blocks × 2 layers = PLANNED_GENIE_CALLS 32),
  DEV SC 128/128 (64 blocks × 2 layers = PLANNED_SC_CALLS_MAX 128),
  provenance_violations 0. Expected SC recomputed as
  Σ(1+l2_invoked over non-abort error-free)=128 — matches persisted 128.
- K_total: persisted 6811 (raw 6811.785936024251), K1 319 + K2 6492 = 6811 TRUE.
  My literal recomputation: H=0.8010378248977231 → raw 6811.785936024634 →
  floor 6811; EXPECTED_TOTAL spelling → 6811.785936024635 → 6811. Both agree on
  6811, far from integer boundary (0.786). Repr dust: persisted raw ends
  …024251 vs my …024634/…024635 (Δ≈3.8e-10, float-path dust; non-blocking —
  floor, K split, digest, f-gate all unaffected).
- Leakage 5*6811+64=34119; budget 1.3*32768*H=34122.92968012317; persisted
  f 1.2998502888173578 vs my (5*6811+64)/(N*H)=1.2998502888172847 (Δ≈7e-14).
  f≤1.3 TRUE with margin ≈0.00015 (≈3.9 bits of 34122 budget).
- Freeze-before-DEV: `construction_and_allocation.json:frozen_before_first_dev`
  True; digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b
  identical in construction file and aggregate; my SHA-256 recomputation over
  {n,k_total,k1,k2,l1_order,l2_order,pooled_e1/h1/e2/h2_mean} matches exactly.
  TRAIN 16 blocks (used_l1 16, used_l2 16, impossible 0, residual
  5.87097048643237e-07).

## 5. Disclosure / accounting (independent literal recount)

Commands: per-row sums + literal products (no booleans copied).

Raw numbers:

- Per-block literal: 5*(319+6492)+64 = 5*6811+64 = 34119 TRUE (uniform across
  all 64 rows).
- Totals: key 64×34119=2183616 — matches row-sum 2183616 and persisted
  key_dependent_bits 2183616. Public 64×327743=20975552 — matches row-sum
  20975552 and persisted public_control_bits 20975552. Tags: row tag_invoked
  sum 64 = persisted tag_invocations 64 = recount tag_invocations 64.
- Recount: event_types {l1_disclosure 64, l2_disclosure 64, verification_tag 64},
  key 2183616, public 20975552, tags 64; mismatches [] (length 0).
  Mismatch count 0 recomputed (empty list observed, not copied).
- Public per-tag: 10*32768+63 = 327743 verified; every row public_control_bits
  327743.

## 6. Truth boundary (code audit + record evidence)

- `operational_f13.py` flow audited: sampling via `sample_full_block` (TRAIN
  :1667, DEV :1787, one sample per block); disclosed slices only
  `u1_arr[l1_positions]` (:767) and `u2_arr[l2_positions]` (:807); L1 SC
  (:784-786), L2 metrics `gather_p2_metrics(bob_arr, high_hat, ...)` (:805)
  from Bob + hard L1 candidate only (true high never enters); restarted L2 SC
  (:812-814); `label_hat=32*high_hat+low_hat` (:816); scoring
  `array_equal(label_hat, labels_arr)` (:818) + Toeplitz tag pair (:819-821);
  single classify (:829-835); sentinel (:843-852) with
  `_truth_isolation_sentinel` (:637-645) proving protected
  `[op_p1_metric.logp, u1_disclosed, u2_disclosed]` unchanged under truth
  mutation. Truth copies made at :755-759; provenance PRIOR_ONLY (:766) /
  CANDIDATE_CONDITIONED (:806).
- Operational metrics truth-free: only disclosed values, tag construction, and
  scoring touch truth; no undisclosed metric/decision/candidate uses truth.
- Record evidence: all 64 rows truth_leak_violation False (sum 0 recomputed);
  provenance_violations 0; the two verify_failed blocks both show label_match
  False (tag False + label False) — scoring observed the mismatch without
  leaking truth into decisions (no undetected, no rescue).
- Call sites: exactly one `sc_decode` (:623 via `_decode_layer`), one
  TRAIN-only `block_genie_risks` (:1685), two `sample_full_block` (TRAIN/DEV).
  No second/oracle/rescue/adaptive/retry arm in logic.

## 7. Resources (recomputed, authoritative sources stated)

Commands: row wall/RSS/VmPeak/VmSize ranges + sums vs `aggregate_summary.json:
wall_s/rss_bytes_peak`.

Raw numbers:

- Total wall persisted 1183.61887 s ≤2100 s TRUE; margin 916.38113 s (≈43.6%).
  Within 2100-s envelope with large buffer. (Exit 0 + empty stderr per packet
  context; verified via completed CANDIDATE summary, not by rerun.)
- Per-block `resources.wall_s` range 11.794088–13.15363 s, sum 790.799327 s
  (matches context). Per-block `wall_s` range 11.793906–13.153319 s, sum
  790.781564 s (Δ 0.017763 s total, <0.3 ms/block capture dust — immaterial).
  Overhead = 1183.61887−790.799327 ≈ 392.82 s (TRAIN 16 blocks + freeze/
  finalize/checkpoint JSON).
- RSS peak persisted 545861632 B (≈520.6 MiB) ≤2147483648 B TRUE;
  margin 1601622016 B (≈1.49 GiB). Per-block RSS HWM range
  543035392–545861632 B; peak equals max HWM (no hidden growth).
- VmPeak (authoritative virtual) range 761360–763408 kB (max 781729792 B);
  VmSize range 597516–599564 kB (max 613953536 B); both <2 GiB TRUE with
  >1.3 GiB margin. `ulimit -v 2097152` KiB (=2 GiB) held.
- ru_maxrss note: per-block RSS HWM and aggregate peak are the Linux
  ru_maxrss-family resident figures; VmPeak/VmSize are the authoritative
  virtual-memory envelope on this run (both held). No phantom exceedance:
  resident peak ≈0.51 GiB, virtual peak ≈0.73 GiB, both well under 2 GiB.
- Aborts 0, resource_stop_fired False, reason None. No resource_abort rows.
  No MemoryError path taken.

## 8. Bounded wording (report.md read fully, 64 lines)

- `report.md` + aggregate `claim_scope` state ONLY: "frozen V25 TRAIN
  target-population empirical-construction operational development signal at
  N=32768 only, sampled from the model; not held-out or real frame FER,
  efficiency, key rate, scaling superiority, qualification or promotion;
  planning f is not real-channel efficiency; undetected is never success."
- No BEC arm present: string `bec` absent from all five gate artifacts;
  runner docstring states single operational arm, no second/retry arm.
- No success language beyond the frozen label: outcome table lists exact 62 /
  undetected 0 / verify_failed 2 / decode_failed 0 / nonfinite 0 /
  resource_abort 0, fraction 0.96875, Wilson LB 0.9098711859061207 with both
  boundaries quoted (0.9098711859 / 0.8883797144). Label is exactly
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` — the frozen candidate
  token, not a qualification/promotion claim.
- Threshold-sit neutrality: report quotes both boundaries; this review states
  bluntly the zero-count margin (§3). The 62/64 sit is reported as an exact
  threshold meet, not as headroom.

## 9. Tests / scope (rerun, not copied)

Commands (pinned interpreter, fresh basetemps, `-q -p no:cacheprovider`):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_operational_f13.py -q -p no:cacheprovider \
  --basetemp=/tmp/p16-preresult-focused
# → 23 passed in 456.86s

/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider \
  --basetemp=/tmp/p16-preresult-full
# → 358 passed in 1218.24s
```

- Focused P16: 23/23 pass (expected 23). Full NB-Polar suite: 358/358 pass
  (expected 358; 23 files). Tests inject `counts=`, never open the NPZ, never
  execute frozen streams as production (constant-reads only).
- `git status --porcelain`: only the declared P16 set (untracked module
  `operational_f13.py`, focused test, P16 spec dir, tasks.md P16 section,
  queue `NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/` incl. five-file
  `operational_f13_gate/`) plus pre-existing out-of-scope dirt (P3-tracked
  edits, sibling phase queues) untouched by this review. Accepted modules /
  P12–P15 / X-roots show no new P16-driven writes (P16 strings only in
  tasks.md per Pre-EXECUTE §3, still holding).
- HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` unchanged; no commit/push;
  no rerun of the frozen gate; no output-root writes outside the five files.
- STATUS.yaml on disk still shows pre-execution values (reads/attempts 0/0)
  while the gate artifacts record the spent 1/1 — the spent state lives in
  the artifacts (`attempt_read_accounting`), which is the authoritative
  consumption record post-open; no second open was performed by this review.

## Gate table (recomputed vs persisted — all recomputed TRUE)

| gate | recomputed | persisted | evidence |
|---|---|---|---|
| target_population_contract | TRUE | TRUE | H1 Δ4.49e-14, H2 0, total Δ4.51e-14 (tol 1e-12); floor Δ5.16e-11 (≤1e-9); col 1.14e-13; p_b 1.0; 7/7 checks |
| construction_frozen_before_dev | TRUE | TRUE | frozen_before_first_dev True; train 16/16/0; digest match |
| train_dev_coverage_complete | TRUE | TRUE | TRAIN 16, DEV 64/64; N/seeds/bps match frozen plan |
| streams_disjoint_frozen | TRUE | TRUE | TRAIN∩DEV ∅; intra-list unique; frozen order match |
| orders_valid_k_replay_f_within_budget | TRUE | TRUE | both perms of 0..32767; K1+K2=6811; digest recomputed match; f 1.29985≤1.3 |
| buckets_disjoint_exhaustive | TRUE | TRUE | 62+0+2+0+0+0=64; consistency_bad [] |
| truth_isolation | TRUE | TRUE | 64× leak False; prov 0; sentinel+provenance audit; verify_failed label False |
| undetected_zero | TRUE | TRUE | 0/64 |
| nonfinite_zero | TRUE | TRUE | outcome 0 + flag 0 |
| no_unregistered_calls | TRUE | TRUE | genie 32/32; SC 128=Σ(1+l2); error-free |
| disclosure_recount_exact | TRUE | TRUE | 2183616=64×34119; 20975552=64×327743; 64 tags; mismatches [] |
| attempt_read_accounting_exact | TRUE | TRUE | 1/1, 1/1, opens 1, no reopen, stat 25166822 |
| resource_limits_met_and_no_abort | TRUE | TRUE | wall 1183.6<2100; RSS 545M<2GiB; VmPeak 763408kB<2GiB; 0 aborts |
| failing list | [] (len 0) | [] | — |
| scientific exact≥62/64 | TRUE | TRUE | 62≥62, margin 0 counts |
| scientific Wilson≥0.90 | TRUE | TRUE | 0.9098711859061207≥0.90, margin +0.00987 |
| label | CANDIDATE | CANDIDATE | integrity all TRUE + recovery TRUE → CANDIDATE uniquely |

Classification derivation: all-integrity-TRUE ∧ recovery-TRUE ⇒
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` per frozen
`select_label` rule. NOT_CONFIRMED would require integrity-TRUE ∧
recovery-FALSE; BLOCKED would require earliest integrity FALSE. Neither
applies. CANDIDATE is uniquely correct — with the blunt zero-margin caveat
that 61/64 (LB 0.8883797143731994) would have yielded NOT_CONFIRMED.

## Closure statements

- NPZ content NOT reopened by this review (stat size 25166822 only; mtime
  2026-08-19 unchanged).
- Frozen gate NOT rerun (single 1/1 read + 1/1 attempt remain spent per
  artifacts; opens 1, reopen False).
- No Model-F/HOLD/raw/real/EVAL access; no P12–P15/old-root writes; no
  commit/push; HEAD `ab173f2a` unchanged.
- Only file written by this review: this `PRE_RESULT_REVIEW.md`.
- Recommendation: accept CANDIDATE as the frozen-rule operational development
  signal at N=32768/f≤1.3 with the zero-margin fragility recorded; no
  reclassification, no rerun, no tuning.

