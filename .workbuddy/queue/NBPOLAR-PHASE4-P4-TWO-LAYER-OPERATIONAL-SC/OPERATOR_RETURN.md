# Operator return — NB-Polar Phase 4-P4 two-layer operational SC

Packet: `NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC`
Return label: **`TWO_LAYER_OPERATIONAL_SC_CANDIDATE`** (candidate only; acceptance is the main thread's decision)
Date: 2026-09-13. HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged; no commit, no push).
Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3).

This is a candidate-labelled factual return. It is **not** an acceptance. It
makes no real-data FER, leakage-efficiency, key-rate, qualification, promotion
or `f<=1.3` claim. No OpenSpec box is checked here.

## 1. Mission

Close the Phase-4 dependency omitted before the protocol phases: implement the
smallest scientifically valid two-stage SC closed loop and execute one paired
oracle-L2 vs candidate-L2 synthetic **interface** gate on injected tables. The
gate measures causal wiring, provenance, truth isolation, taxonomy, accounting
and transcript integrity — not a performance delta.

## 2. Two-stage causal path implemented

One module, no benchmark adapter (documented decision in
`P4_IMPLEMENTATION_NOTES.md` §2.1; the accepted `IRMethod`/`FrameBatch`
single-layer contract has low half constant zero and cannot carry the paired
oracle arm without a frozen-schema change).

- One shared L1 stage per block: Bob-only `build_p1_metrics(B, p1_table)` →
  `probs_to_symbol_metric` (`PRIOR_ONLY`) → one `sc_decode`
  (`known_positions=D1`, `known_values=U1[D1]`); `high_hat = sc1.x_hat`
  (source-domain hard candidate, a fresh copy).
- Operational arm (causal, strict): Bob + candidate
  `gather_p2_metrics(B, high_hat, p2_table)` → `probs_to_symbol_metric`
  (`CANDIDATE_CONDITIONED`) → one **fresh** `sc_decode`
  (`known_positions=D2`, `known_values=U2[D2]`) → `label_hat = low_hat + 32*high_hat`
  → exactly one final 64-bit Toeplitz tag.
- Oracle arm (strictly isolated diagnostic, same block and disclosures):
  `gather_p2_metrics(B, high_true, p2_table)` → `ORACLE_CONDITIONED` → one
  fresh `sc_decode` with the same `D2/U2[D2]` → `label_oracle = low_hat_oracle +
  32*high_true` → exactly one final tag. Runs for every executed block,
  including blocks whose operational L1 failed.
- No state/APP/belief/partial-sum transfer: each L2 is a fresh `sc_decode` on a
  metric gathered from scratch (Pre-EXECUTE spy: exactly 3 decodes per block, no
  shared `logp` memory). `APP` is a comment/plan token only in the module.
- Core `comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer.py`;
  focused tests `comparison_bench/tests/test_nbpolar_two_layer.py` (12 tests,
  P4-A01..A09 + failure taxonomy + A11 + forbidden-marker/import-time checks).

## 3. Frozen gate identity

| item | value |
|---|---|
| point | q=32 GF32 poly 37 / alpha 2 / natural order; N=256; epsilon1=0.05, epsilon2=0.20; K1=45, K2=110 |
| disclosure sets | `D1 = sorted(analytic_order(0.05,256)[:45])`, `D2 = sorted(analytic_order(0.20,256)[:110])`; published actual GF32 `U1[D1]`/`U2[D2]` values |
| model | explicit injected `[Alice,Bob]` `(1024,1024)` table `f[a,b]=Ph(b_h\|a_h)*Pl(b_l\|a_l)` with `L(y\|x)=eps/32+(1-eps)[y==x]`; `A=32*high+low`, `high/low` iid uniform GF32; independent layer-erasure observation; column-sum deviation 9.55e-15 <= 1e-12 |
| blocks | 96 paired synthetic blocks |
| run seed | 2026091360 (consumed at the first gate SC call: block 0 operational L1) |
| public Toeplitz master | 2026091361 (public control; per-arm/per-block SHA-256 counter-stream, 2623 bits per tag invocation, never persisted raw) |
| output root | `.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/` (absent at freeze; refused if present) |
| budgets | internal total wall 3600 s; external `timeout 3600`; `ulimit -v 2097152` (2 GiB); `rss_bytes_max=2147483648` |

Exact frozen command (executed once, exit 0):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer --n 256 --epsilon1 0.05 --epsilon2 0.20 --k1 45 --k2 110 --blocks 96 --seed 2026091360 --toeplitz-master 2026091361 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate
```

## 4. Run results

- Single gate execution, **exit 0**; all 13 hard gates true; candidate label
  `TWO_LAYER_OPERATIONAL_SC_CANDIDATE`.
- Paired coverage **96/96** both arms; **both** operational and oracle L2 invoked
  96/96; L1 executed 96/96 per arm; no skips, no decode failures, no resource
  abort.
- Provenance: operational L1 `PRIOR_ONLY` 96; operational L2
  `CANDIDATE_CONDITIONED` 96; oracle L2 `ORACLE_CONDITIONED` 96; oracle L1
  `None` 96 (shared block stage).
- Operational outcomes: exact **26**, verify_failed **70**, undetected 0,
  decode_failed 0, resource_abort 0 (sum 96).
- Oracle outcomes: exact **44**, verify_failed **52**, undetected 0,
  decode_failed 0, resource_abort 0 (sum 96).
- `undetected`/`decode_failed`/`resource_abort` all 0 and never folded into
  `exact`; truth-leak 0; nonfinite 0; `decode_error_types` empty.
- Report-only (no threshold): operational exact 26 vs oracle exact 44;
  `oracle_candidate_divergence_count = 34` of 96 defined.
- Resource: artifact wall **10.154709 s**; peak RSS **144609280 B** (137.9 MiB);
  `resource_stop_fired = false`.
- Tests: 12 new focused + 180 predecessor = **192 passed** across 13
  `test_nbpolar_*.py` files.
- Attempt 1/1 consumed; no rerun, no seed change, no tuning.

## 5. Hard-gate table (13/13 true)

| # | gate | result |
|---|---|---|
| 1 | paired_coverage_complete | True |
| 2 | both_arms_l2_invoked_for_l1_candidates | True |
| 3 | p1_provenance_prior_only | True |
| 4 | candidate_provenance_candidate_conditioned | True |
| 5 | oracle_provenance_oracle_conditioned | True |
| 6 | operational_truth_leak_zero | True |
| 7 | undetected_zero | True |
| 8 | nonfinite_zero | True |
| 9 | resource_abort_zero | True |
| 10 | outcome_buckets_disjoint_exhaustive | True |
| 11 | disclosures_exact | True |
| 12 | transcript_recount_mismatch_zero | True |
| 13 | pre_run_injected_wrong_l1_propagation_passed | True |

Pre-run injected wrong-L1 propagation check (decoder-free, consumes no attempt):
`decoder_calls=0`, `metric_divergent=true`, `label_divergent=true`,
`metric_max_abs_diff=0.6`, `passed=true`.

## 6. Per-layer sub-buckets and provenance

Per arm per block, disjoint and exhaustive over executed blocks:
`l1_executed` / `l1_decode_failed`, `l2_invoked` / `l2_skipped_by_l1_failure` /
`l2_decode_failed`, and `tag_invoked` (at most one per arm per block). Frozen
run: for both arms `l1_executed=96`, `l1_decode_failed=0`, `l2_invoked=96`,
`l2_skipped=0`, `l2_decode_failed=0`, `tag_invoked=96`. Every L1-candidate block
invoked both L2 arms (96/96 pairs). Record clarity (Pre-EXECUTE NB-6): for the
oracle arm `l1_executed=True`/`l1_decode_failed=False` denote the shared block
L1 stage / true-L1 availability, not an oracle-arm L1 SC call.

## 7. Accounting and recount

- Per executed arm per block: L1 disclosure `5*K1=225`, L2 disclosure `5*K2=550`,
  tag `64`; a fully invoked arm totals `5*(K1+K2)+64 = 839`.
- Key-dependent total **161088** = 96 x 839 per arm (operational 80544, oracle
  80544).
- Public control **503616** = 192 tags x 2623 bits (operational 251808, oracle
  251808); counted separately from key-dependent bits.
- Transcript: **576** events = `l1_disclosure` 192 + `l2_disclosure` 192 +
  `verification_tag` 192.
- Independent literal recount equals the incremental totals per arm and in
  total; `mismatch_count = 0`, `mismatches = []`.

## 8. Frozen-model consequence and ULP divergence definition

The frozen independent-layer model makes the table-derived `P2` numerically
independent of the L1 high symbol: Pre-EXECUTE independently measured
`max_b |P2[u1=0,b,:] - P2[u1=1,b,:]| = 7.771561172376096e-16`, pure float64
rounding. A wrong L1 candidate therefore changes the operational `P2_hat` only
at rounding scale, so the paired gate validates wiring / provenance / isolation
/ accounting plus **label-level** propagation (a wrong L1 flips the five high
bits of `label = low_hat + 32*high_hat`), **not** metric-level L1→L2
dependence.

`oracle_candidate_divergence` is defined in `two_layer.py`
(`_candidate_divergence(p2_hat, p2_true) = not np.array_equal(p2_hat, p2_true)`,
applied per block comparing the `(32,1024)` float64 candidate- and
oracle-conditioned P2 arrays). Its value 34/96 = 34 blocks where those rounding
differences happened to change at least one array bit. It is report-only, has no
threshold, and is not read by `hard_gates` or `candidate`; it is **not** a
semantic metric-level dependence and not a performance result. The hand-injected
layer-dependent check (`max abs diff 0.6`) and the focused tests prove real
divergence is detected where the model has layer dependence.

## 9. Attempt and seed accounting

- `attempts_allowed: 1`; `attempts_used: 1`. The single attempt is consumed at
  the first gate SC call (block 0 operational L1); `frozen_plan.json`
  `attempts_consumed = 1` and `aggregate_summary.json`
  `attempts_consumed_by_this_run = 1`.
- Run seed **2026091360** consumed; Toeplitz master **2026091361** is public
  control (never persisted raw). Both are absent from the 27-entry refused set
  of previously consumed official seeds.
- Seed-overlap adjudication: `2026091360`/`2026091361` were used only as P6-R1
  **test-local** seeds (`test_nbpolar_incremental_r1.py`; `R1_FREEZE.md` §6).
  They are not consumed official result streams; the P4 Toeplitz namespace
  `nbpolar-p4-toeplitz-seed` is distinct from the P6 prefix, so no tag stream can
  collide, and no accepted evidence artifact depends on them. Pre-EXECUTE
  adjudicated the overlap acceptable.
- No rerun, no seed change, no parameter/K/table/threshold tuning, no partial
  credit.

## 10. Independent review verdicts

- **Pre-EXECUTE: PASS** (`PRE_EXECUTE_REVIEW.md`). Frozen identity byte-faithful
  to packet and delta spec; both operator-flagged items adjudicated acceptable
  with recorded consequences: (a) frozen-model P2 layer-independence — no hard
  gate invalidated, divergence/exact are report-only and must be described as a
  label-level propagation / float-noise signal, not metric-level dependence;
  (b) P6-R1 test-local seed overlap — acceptable, no evidence entanglement.
  Non-blocking findings NB-1..NB-7 (docs consistency, non-consuming test seed
  literals, claim wording, WSL2 RSS, docs update, oracle-arm `l1_executed`
  semantics, budget symmetry) recorded.
- **Pre-RESULT: PASS_WITH_COMMENTS** (`PRE_RESULT_REVIEW.md`). All 13 hard
  gates, coverage/outcome/provenance/accounting numbers and the report-only
  metrics independently recomputed exactly as persisted; no blocking issue. The
  comments are reporting/housekeeping only (STATUS lag — now updated; transcript
  events not persisted; oracle-arm `l1_executed` semantics; test-file count
  wording).

## 11. Output files

Output root `two_layer_operational_sc_gate/` (read-only, exactly 5 files,
single generation):

| file | size |
|---|---|
| `frozen_plan.json` | 5349 B |
| `per_block_two_layer_outcomes.json` | 141468 B |
| `transcript_accounting.json` | 1226 B |
| `aggregate_summary.json` | 3899 B |
| `report.md` | 1938 B |

All persisted records are scalar-only; no symbols, labels, disclosed values,
decoded keys or raw seed bits are persisted.

## 12. Scope and bounded-scope statement

Synthetic injected-table interface and cross-layer-propagation development
signal only. This is **not** real-data FER, leakage efficiency, key rate,
qualification, promotion or `f<=1.3` evidence; no performance claim is derived
from the report-only `exact` or divergence numbers. No Model-F/artifact/parquet/
TTBin/real data; no empirical construction; no N>256; no FWHT/scalable decoder;
no APP/soft L1 belief; no SCL/Phase 7. No old evidence root was opened, parsed
or modified; no `results/` or `comparison_bench/outputs_comparison/` write; no
sibling-checkout write.

## 13. Stage status

- Unrun stages: **none within this packet**. The only remaining stage is
  **main-thread acceptance** (`next_gate: MAIN_THREAD_ACCEPTANCE`).
- No commit, no push.
