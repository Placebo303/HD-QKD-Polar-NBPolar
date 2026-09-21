# Decision Log

Durable decisions and rejected alternatives for the HD-QKD_Polar_Comparison-nbpolar project.

---

## Template

```
### YYYY-MM-DD: <Title>

**Decision**: <What was decided>

**Context**: <Why this was needed>

**Alternatives considered**:
- Alternative A: <Why rejected>
- Alternative B: <Why rejected>

**Consequences**: <What this means going forward>
```

---

## Decisions

## 2026-09-19 NB-Polar Phase 4 P20Q HOLD IR confirmation accepted (descriptive; B 4/5 restoration, IR-1..IR-5 complete)

**Decision**: Record the single P20Q Tier-Y execution as `TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`, accepted descriptive only. The accepted IR-1..IR-5 payload tables + nine carried scalars are the pre-registered inputs for main-thread H2a–H2e analysis AFTER this acceptance; the follow-on efficiency/disclosure-minimality vs next-upstream-factor branch decision comes after that analysis. Nothing auto-triggers.

**Context**: Reuse-only α1-confirmation packet `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/` (`MAIN_THREAD_ACCEPTANCE.md` / `PRE_EXECUTE_REVIEW.md` / `OPERATOR_RETURN.md` on disk; Pre-RESULT PASS session `ses_f463b6cdaffeISG0o1eh7nP79u` in `STATUS.yaml`; acceptance commit `d5c0afb`). First use of 2M HOLD DEV 2916..3555 (5 × 128, remainder 3556..3644 declared never-decoded), K1/K2 334/6746, tag master 2026092330, single authorized attempt (exit 0, HOLD-DEV 1/1, counts 0/0, SC 30/30, tags 20/20, wall 198.39 s / RSS ~620 MiB). Outcomes: A 0/5, B 4/5 (`b_restored` 4, `b_maintained` 0 vacuous), C 0/5, D 4/5 (`d_restored` 4 diagnostic); 12 L2-fail records all natural-in-prefix but U-domain-out (P20N/P20O pattern continuity on a third segment); `undetected` 0; integrity 30/30; key 692580 / public 6554860 / recount 0; zero B−A / D−C disclosure delta. Chain P20N B 1/4 → P20O B 2/5 → P20Q B 4/5, all descriptive. One-packet evidence-size exception: 2.25 MB `per_block_arm_outcomes.jsonl` committed as frozen evidence.

**Alternatives considered**:
- Treat B 4/5 (or the P20N→P20O→P20Q chain) as reliability/FER/recovery evidence: rejected — descriptive only by freeze; three construction events across three segments do not license a reliability claim.
- Render an H2a–H2e verdict in this packet: rejected by design — H2 analysis is main-thread work on the accepted payload after acceptance, never an in-packet verdict.
- Adopt a standing pre-freeze evidence-size rule now: deferred — the 2.25 MB commit is a one-packet exception; a standing rule needs an explicit main-thread decision.
- Treat the absent `b_maintained` (strict-sense maintain 0) as evidence against the construction: rejected — A is never exact anywhere, so maintain is vacuous; restoration 4/5 at zero disclosure delta is the planning input.

**Consequences**: No rerun/retuning of P20Q; P19 roots untouched; no push. 2M HOLD DEV 2916..3555 CONSUMED; HOLD remainder 3556..3644 and 1.5M VAL remainder 2044..2212 stay never-decoded.

## 2026-09-19 X10 H2 scalar adjudication probe disposition (H2a refuted; local-spike reading; IR-1..IR-5; P20Q frozen next)

**Decision**: Record the Tier-X probe `workspace/probes/nbpolar_x10_h2_scalar_adjudication/` (packet `.workbuddy/queue/NBPOLAR-X10-H2-SCALAR-ADJUDICATION/`, reviewed PASS, decoder-free, zero protected opens) as: H2a **REFUTED**, H2b **SUPPORTED**, H2c **SUPPORTED**, H2d flat, H2e static-geometry **NOT-DECIDABLE** → bounded recording-only instrumentation requirements IR-1..IR-5. Freeze `NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M` (reuse-only α1 confirmation on 2M HOLD 2916..3555, 5 blocks, IR-1..IR-5 PRESENT, zero new counts read) as the next planning input; nothing auto-triggers — Stage-A authorization paste still required.

**Context**: H2a: 4/4 evaluable blocks show the exact arm's prefix-hazard mean HIGHER than the failing arm's (P20N b3 +0.0971; P20O b1 +0.0304, b2 +0.0431, b4 +0.0684 bits). H2b: fail-site hazard / prefix-mean median ratio 2.246 over n=25 L2 fails, per-arm medians >1.1. H2c: 23/25 fails in X-prefix; P20O 11/11 additionally out-of-U. H2d: mean |Δfloor| 0.0030 (flat). H2e undecidable from static geometry alone. Descriptive reading: failures are driven by LOCAL relative hazard spikes, not average metric quality; α=1 smoothing flattens those spikes even while raising the mean — this explains "alt CE/hazard higher yet restores blocks". IR-1 64-bin log hazard histograms {prefix,outside} ~1KB/rec; IR-2 first-error hazard-rank percentile (1 float); IR-3 above-threshold prefix counts at 1.0×/2.0× record prefix-mean; IR-4 top-16 hazardous positions w/ ranks; IR-5 capped 4096×2 float32 series + truncation flag (escalation). H2 is one instrumented run from resolution.

**Alternatives considered**:
- Treat the H2b/H2c support as a mechanism verdict or auto-trigger P20Q: rejected — descriptive only, static scalars; P20Q needs explicit Stage-A authorization.
- Retain H2a (average-metric-quality) as live: rejected — refuted 4/4 in the evaluable direction.
- Decide H2e from static geometry or demand the full per-position series now: rejected — NOT-DECIDABLE on current scalars; IR-5 is capped/escalation-only.

**Consequences**: No FER/reliability/qualification claim; no rerun/retuning; P19 roots untouched; no commit/push.

## 2026-09-19 NB-Polar Phase 4 P20O 2M maintain-confirmation accepted (descriptive; restoration replicated cross-session; U-domain closure)

**Decision**: Record the single P20O Tier-Y execution as `TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE`, accepted descriptive only. Combined with P20N, the frozen alt-L2 construction now shows B 3/9 vs control A 0/9 restoration events across two sessions, with zero maintain events. The next single factor is main-thread planning input; nothing auto-triggers.

**Context**: Maintain-confirmation packet `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/` (`PRE_EXECUTE_REVIEW.md` / `PRE_RESULT_REVIEW.md` / `MAIN_THREAD_ACCEPTANCE.md` on disk). Factor: maintain-confirmation of `ALT-L2-LAPLACE-α1` on the FIRST use of the reserved 2M independent session, with per-session Stage-A derivation (2M raw prior canonical digest `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`; orders sha `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; alt table sha `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`; session H1/H2/H 0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477; K_total 7080, K1/K2 334/6746; D2 FEASIBLE margin 4791.09652735766). Stage B one-shot on 2M VAL 2187..2826 (5 blocks): A 0/5, **B 2/5 (b1 `2315..2442`, b2 `2443..2570` exact)**, C 0/5, **D 3/5 (b1, b2, b4 `2699..2826` exact)**; `b_restored_count` 2, `b_maintained` 0, `d_restored` 3, `d_maintained` 0; integrity 29/29 gate keys; key 692580 = 10*35464 + 10*33794; public 6554860; SC 30; tags 20; `undetected` 0; counts 1/1 + 2M VAL-DEV 1/1 + attempts 1/1 SPENT; 2M remainder 2827..2915 and HOLD 2916..3644 untouched. Descriptive reading: restoration replicated on an independent session (P20N 1.5M HOLD B 1/4 vs A 0/4 → combined B 3/9 vs A 0/9); oracle gap persists (D 3/5 > B 2/5); L1 is not universal on 2M (b0/b4 operational first errors L1 @6834/14296); alt metric has higher average CE/prefix-hazard yet restores blocks → mechanism likely order/metric-side (H2 open). Instrumentation: the ninth U-domain scalar (`l2_fail_in_prefix_u_domain`) definitively closed the P20N domain-mixed reading — all 11 L2 failures are natural-index-in-X-prefix but U-domain-out (genuine undisclosed-region SC errors, no pinning violation); instrumentation remains 9 scalars per record, NOT a per-position hazard series.

**Alternatives considered**:
- Treat the cross-session B 3/9 vs A 0/9 as reliability/FER/recovery evidence or auto-trigger the next factor: rejected — descriptive only, 9 blocks, no FER design; next gate is main-thread planning (candidates: H2 adjudication from the 9 scalars; per-position instrumentation enhancement; L2 construction-family expansion with X02/X03/X03b materials; L1-side 2M robustness).
- Read D 3/5 > B 2/5 as a verdict against the alt-L2 construction: rejected — the oracle gap confounds true-L1 vs hard-L1; H2 adjudication is a planning candidate, not a conclusion.
- Treat the `l2_fail_in_prefix` domain-mixed reading as still open: rejected — the ninth U-domain scalar closed it definitively (11/11 U-domain-out).
- Remove the λ code paths now or claim f=1.3 margin: rejected/deferred — non-blocking debt (`per_session_calibration.py` retains the λ program; `empirical_diagnostic.py` still references `LAMBDA_STAR`; disposition unchanged: raw+floor only for target-channel priors); f=1.3 still has no demonstrated margin.

**Consequences**: No rerun/retuning of P20O; P19 roots untouched; no commit/push. 1M-HOLD thread stays open; the worktree's ~89 uncommitted changes belong to the separately-made milestone commit.

## 2026-09-19 NB-Polar Phase 4 P20N alt-L2 construction HOLD accepted (descriptive; first operational restoration; maintain-confirmation branch armed)

**Decision**: Record the single P20N Tier-Y execution as `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE`, accepted descriptive only. The b3 restoration event activates the deferred `b_restoration_branch_maintain_confirmation_round` as the next planning input; nothing auto-triggers.

**Context**: Single-factor L2-construction packet `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/` (`PRE_EXECUTE_REVIEW.md` / `PRE_RESULT_REVIEW.md` / `MAIN_THREAD_ACCEPTANCE.md` on disk). Factor: one preregistered alternative L2 construction `ALT-L2-LAPLACE-α1`, `f_alt=(counts_ab+1)/(n_b+1024)` (α=1; L1 path/K/order unchanged), `alt_l2_tables_1p5m.npz` sha256 `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`; D2 feasibility FEASIBLE (ce_alt 0.9027311772313849 vs incumbent 0.8003665547439149; alt ideal length 29580.70 ≤ 33509). Stage B one-shot on HOLD 2213..2724 (first HOLD use), 4 blocks, fixed disclosure K1=331/K2=6689, tag master 2026092300: A control-L2 0/4 (L2 fails @111/76/3/81); B alt-L2 operational 1/4 (block 3 `2597..2724` EXACT; fails @1009/20/5823); C control-oracle 0/4; D alt-oracle 1/4 (b3 exact). `b_restored_count` 1, `d_restored_count` 1, `b_maintain_count` 0; all 14 failures L2-layer; L1 exact on all 8 operational records; `undetected` 0 isolated; integrity 28/28; key 549384 / public 5243888 / SC 24 / tags 16 / recount 0. Consumption: counts 0/0, HOLD 1/1 SPENT, attempts 1/1 SPENT, VAL-remainder 0, 2M pristine. Descriptive reading only: first operational exact block on the 1.5M session, out-of-sample, at fixed disclosure, restored under both hard-L1 (B) and true-L1 (D) → gain is L2-metric-side; alt metric has higher average prefix hazard (0.8925–0.9035 vs 0.7954–0.8556) yet decoded one block exactly; neighbourhood floor fraction 0.0 on every failing record → floors exonerated in-run (support for "incumbent spikiness, not average length, drives out-of-sample L2 failures"). Instrumentation note: X09-R1 `l2_fail_in_prefix` true on 12/14 failures, false on the shared B-b2/D-b2 event @5823 — a frozen-definition domain artifact (X-domain index vs U-domain set), not a pinning violation; U-domain cross-check needs unpersisted arrays (successor item).

**Alternatives considered**:
- Treat the b3 restoration as reliability/recovery/FER evidence or auto-trigger the maintain round: rejected — descriptive only, one block; the branch is armed, not triggered.
- Run the maintain confirmation on VAL remainder 2044..2212 vs reserved 2M first-use now: deferred to main-thread planning — VAL remainder is one block + 41-frame stub; 2M is an independent session needing per-session raw calibration + new freeze/tags.
- Treat the `l2_fail_in_prefix=false` event as a pinning violation: rejected — frozen-definition domain artifact, documented as successor instrumentation.

**Consequences**: No rerun/retuning of P20N; P19 roots untouched; no commit/push. 1M-HOLD thread stays open; 2M stays reserved.

## 2026-09-19 NB-Polar Phase 4 X08 prior disposition + P20L supersession + P20M raw-prior VAL accepted (descriptive; L2 bottleneck live)

**Decision**: (a) The λ concentration program must not be used to build the target-channel prior for new sessions — raw-count MLE + 1e-15 floor is the canonical rule, λ survives only as a control arm. (b) `NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M` is SUPERSEDED by P20M with zero consumption. (c) Record the single P20M Tier-Y execution as `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE`, accepted descriptive only; the live planning consequence is that L2 is now the bottleneck factor (L2-side single factor / P20D candidate as next planning input; nothing auto-triggered).

**Context**: X08 Tier-X probe (`workspace/probes/nbpolar_x08_per_session_prior_entropy_audit/results.json`; packet `.workbuddy/queue/NBPOLAR-X08-PER-SESSION-PRIOR-ENTROPY-AUDIT/`, focused review PASS) on 1.5M TRAIN counts: λ=137.3823795883264 gives H1 2.006647056368773 / H2 1.9017235959286112 / TOTAL 3.908370652297384 (K_total 33285, N·H1 65754) vs raw+floor H1 0.025199496923753 / H2 0.800366554749543 / TOTAL 0.825566051673296 (K_total 7020, N·H1 826); floor hits 1,046,140/1,048,576; zero columns 0. P20M Stage A derived `raw_prior_1p5m.npz` (digest `372dcc1c…cf7d46ac`) under the raw rule and `raw_prior_orders_1p5m.json` (sha `a9f18a9f…1da11bc638`), K_total 7020 split K1=331/K2=6689 via accepted `select_empirical_split` (16 synthetic TRAIN blocks, seeds 2026092291..2026092294); 19 focused tests green; `PRE_EXECUTE_REVIEW.md` PASS and `PRE_RESULT_REVIEW.md` PASS + `MAIN_THREAD_ACCEPTANCE.md` on disk. Stage B one-shot (exit 0, wall 104.85 s, RSS ~531 MB) on VAL 1660..2043 (first genuinely out-of-sample 1.5M segment), tag master 2026092280: G0 (λ control 319/6492) 0/3, L1 first errors 24/5/17; G1 (raw 331/6689) 0/3 with L1 breakthrough — first errors L2/26 (l1_exact TRUE), L1/848, L2/31 (l1_exact TRUE), `g1_restored_count` 0; G2 (true-L1 oracle K2 6689) 0/3, L2 first errors 26/3646/31, `oracle_l2_exact` false. Accounting: 25/25 gates, `undetected` 0 isolated, key 308376 / public 2949687 / tags 9 / SC 15 / sampling 0, counts 0/0, DEV 1/1 + attempts 1/1 spent, HOLD 0/1, 2M pristine. P20L never ran Stage B (counts 0/0, DEV 0/1, HOLD 0/1, attempts 0/1); its VAL DEV segment 1660..2043 was released and its STATUS.yaml corrected by the main thread. This is the FIRST genuine out-of-sample L2 evidence (prior TRAIN-segment oracle arms 3/3 exact; now 0/3 on VAL under true L1); both §16 L2-implication triggers fired.

**Alternatives considered**:
- Use the λ prior for new-session target channels: rejected — X08 evidence + X07 disposition; λ is control-arm only.
- Keep P20L alive alongside P20M: rejected — user decision 2026-09-19; P20L superseded with zero consumption.
- Treat P20M as FER/recovery/qualification evidence or auto-trigger P20D: rejected — descriptive only, no restoration evidence; L2-side work is planning input, not an automatic trigger; 2M stays reserved for independent-session confirmation and the 1M-HOLD thread stays open.

**Consequences**: Raw+floor is the canonical prior rule; no rerun/retuning of P20M; P19 roots untouched; no commit/push. Next gate is main-thread planning of an L2-side single factor.

## 2026-09-16 NB-Polar Phase 4-P19 N=32768 1M-HOLD layer/backoff diagnostic COMPLETE (single run, 15/15 verify_failed descriptive)

**Decision**: Record the single P19 Tier-Y execution (exit 0, stderr empty,
in-run wall 186.421779 s within 600 s; outer ≈206.7 s) as
`TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`. Main-thread
acceptance is pending; this entry is not an acceptance and not blocked. No
route recommendation is made.

**Context**: Descriptive five-arm real-input layer/backoff diagnostic on the
exact three accepted P18 HOLD blocks (frames 1600..1727 / 1728..1855 /
1856..1983 of the V25 1M `pairs.parquet`), reusing the accepted P16
construction (K1 319/K2 6492, digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), fixed
floor-1e-15 TRAIN prior and P18 slicing (remainder 1984..1999 unused). Arms:
base(319,6492), l1_plus(447,6492), l2_plus(319,7004), both_plus(447,7004) and a
provenance-isolated true-L1 oracle control(0,6492); fixed +128 L1 / +512 L2
increments, `chunk_rows=512`, public tag master 2026092060. All 20 integrity
gates true, `failing_integrity_gates` empty, `provenance_violations` 0; 15/15
records, 27/27 SC calls, 15/15 tags. All 15 records returned `verify_failed`
(exact 0, undetected 0, decode_failed 0, nonfinite 0, resource_abort 0);
paired-vs-base for every extra-disclosure arm was
`verify_failed->verify_failed` ×3, `first_operational_recovery_arm` null and
`ordered_exact_counts_non_monotone` false (reported neutrally). Per-arm
aggregate CE-normalized disclosure ratios (descriptive only, explicitly NOT
qualification efficiency): base 1.230820481567787, l1_plus 1.2539080605766497,
l2_plus 1.3231707976032374, both_plus 1.3462583766121001; oracle control
1.1732819057566373 (excluded from operational aggregates, deployable false).
Recount key-dependent 526200 (operational 428628 + isolated control 97572) /
public 4916145, mismatch 0; reads 1/1 + 1/1 and attempt 1/1 consumed at the
first protected content open; input sizes/mtimes unchanged; no reopen/rerun.
Peak RSS 615960576 B ≤ 2 GiB. **There is no exact-count, FER, winner,
monotonicity, superiority or recovery threshold in this gate**: 15/15
`verify_failed` is a descriptive real-input observation and is neither a gate
nor a pass/fail result, and `undetected` is never success (it was 0). Note: an
earlier operator transcription of the `l2_plus` ratio said 1.339389; the
artifact value 1.3231707976032374 is authoritative. Independent Pre-EXECUTE
PASS_WITH_COMMENTS and Pre-RESULT PASS_WITH_COMMENTS (all numbers recomputed
from the worktree artifacts).

**Provenance anomaly (external, non-blocking)**: while the run was executing, a
concurrent **external** commit not made by this packet's operators advanced HEAD
`ab173f2a` → `faac0411684819f5a9055cd71fc1b4bae6955287`
(`2026-09-16 21:14:28 +0800`, "docs: consolidate NB-Polar research state and
Astra pack") and captured a **mid-run 11/15 snapshot** of the five P19 artifacts
(`RUNNING(record 11/15)`, `integrity_all_pass false`) via an add-before-commit
race ~33 s after the run's final write. This is a provenance anomaly, not a
scientific failure, and there is no rerun. The finalized 15/15 files are in the
worktree (four ` M` versus that commit; `frozen_plan.json` byte-identical).
**Rule for acceptance and future readers: the worktree files are authoritative;
never read `git show HEAD:<path>` for the four modified paths, and never
`git restore`/`checkout`/`stash` them.** If a commit is eventually authorized,
`git add` the four finalized files after acceptance and cite the worktree
hashes; do not describe `faac0411`'s blobs as the P19 result.

**Alternatives considered**:
- Rerun/tune seeds, N, K, arms, floor, orders, blocks or thresholds: rejected —
  forbidden by the freeze; reads 1/1 + 1/1 and attempt 1/1 are consumed.
- Treat the 15/15 `verify_failed` outcome as a failure, a winner or blocked:
  rejected — the gate has no recovery/FER/winner/monotonicity/superiority
  threshold by design and every integrity gate passes; the label is COMPLETE
  independent of the recovery pattern.
- Promote to real-frame FER, reconciliation efficiency, leakage, key rate,
  scaling, qualification or promotion evidence: rejected — scope is a
  descriptive five-arm diagnostic at N=32768 only, the CE ratio is explicitly
  not qualification efficiency, and the true-L1 arm is an oracle control.
- Reconcile the external commit by restoring/checking out the five paths:
  rejected — that would overwrite the finalized artifacts with the superseded
  11/15 snapshot and destroy the evidence.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
neither protected input modified or reopened; no commit/push by this packet's
operators. Next gate is main-thread acceptance, which must accept from the
worktree files only.

## 2026-09-16 NB-Polar Phase 4-P18 N=32768 1M-HOLD microcheck COMPLETE (single run, 0/3 exact descriptive)

**Decision**: Record the single P18 Tier-Y execution (exit 0, stderr empty,
in-run wall 37.274417 s within 600 s; outer ≈55.9 s) as
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE`. Main-thread
acceptance is pending; this entry is not an acceptance and not blocked. No
route recommendation is made.

**Context**: Real-input operational microcheck of the frozen V25 1M HOLD split
at N=32768, reusing the accepted P16/P17 construction (K1 319/K2 6492, digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), fixed
floor-1e-15 TRAIN prior and operational block path. Split manifest verified
400 HOLD frames / 102400 HOLD pairs before any open; three registered
chronological blocks 1600..1727 / 1728..1855 / 1856..1983 with remainder
1984..1999 (16 frames / 4096 symbols) recorded unused. All 17 integrity gates
true, `failing_integrity_gates` empty, `provenance_violations` 0. Per-block
outcomes were `verify_failed` × 3 (exact 0, undetected 0, decode_failed 0,
nonfinite 0, resource_abort 0); aggregate total NLL 83161.59954506146 bits,
key-dependent 102357 / public-control 983229 / tags 3, recount mismatch 0,
sample CE-normalized disclosure ratio 1.230820481567787 (descriptive only).
Preconditions 7/7 true; reads 1/1 + 1/1 and attempt 1/1 consumed at the first
protected content open; input sizes/mtimes unchanged; no reopen/rerun. Peak RSS
520798208 B ≤ 2 GiB. **There is no exact-count, Wilson, FER, winner, promotion
or recovery threshold in this gate**: the 0/3 exact outcomes are descriptive
real-input observations and are neither a gate nor a pass/fail result, and
`undetected` is never success. Independent Pre-EXECUTE PASS and Pre-RESULT
PASS_WITH_COMMENTS; the Pre-RESULT review was completed as a resumption from an
interrupted prior reviewer attempt's saved transcript (the interrupted suites
were re-run fresh — 26 focused / 409 full, zero protected opens — and every
load-bearing number independently recomputed; the gate itself was not rerun).
Evidence: packet `OPERATOR_RETURN.md` + `holdout_microcheck/` (five files);
`.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/`.

**Alternatives considered**:
- Rerun/tune seeds, N, K, floor, orders, blocks or thresholds: rejected —
  forbidden by the freeze; read 1/1 + read 1/1 + attempt 1/1 are consumed.
- Treat the 0/3 exact outcome as a failure or as blocked: rejected — the gate
  has no recovery/FER threshold by design and every integrity gate passes; the
  label is COMPLETE independent of the exact count.
- Promote to real-frame FER, reconciliation efficiency, leakage, key rate,
  scaling, qualification or promotion evidence: rejected — scope is a
  real-input operational microcheck at N=32768 only, and the CE ratio is
  explicitly not qualification efficiency.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
neither protected input modified; no commit/push. Next gate is main-thread
acceptance.

## 2026-09-15 NB-Polar Phase 4-P17 N=32768 operational replication CANDIDATE returned (single run, count margin 2)

**Decision**: Record the single P17 Tier-Y gate execution (exit 0, stderr
empty, wall 2031.385216 s within 2400 s) as candidate
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE`. Main-thread
acceptance is pending; this entry is not an acceptance and not blocked.
No route recommendation is made.

**Context**: Independent 128-block replication of P16 at the exact same target
model, N=32768, construction (K1 319/K2 6492, verified digest
055c90…c3faea1b), disclosure (34119 key / 327743 public bits per block) and
protocol; fresh DEV streams 2026092030..2037 × 16. DEV exact 123/128 with
Wilson one-sided 95% LB 0.921934049951655 ≥ 0.90 — count margin exactly 2
over 121 (LB margin +0.0219), resolving P16's zero margin. Per-stream
15/1, 15/1, 16/0, 15/1, 15/1, 15/1, 16/0, 16/0 (block_index 0–15 each).
Integrity 14/14 true, failing list empty; undetected 0; preconditions 7/7
true; reads/attempts 1/1 spent at the first NPZ content open; 256 operational
SC calls, 0 TRAIN/genie calls; no reopen/rerun. P16's 62/64 + 0.9098711859
are report-only (`pooled_into_decision: false`); decision inputs are exactly
the 128 P17 blocks. Independent Pre-EXECUTE PASS and Pre-RESULT
PASS_WITH_COMMENTS (independent 123/128 recount + Wilson recomputation
confirm CANDIDATE; item-8 resolved — per-record VmPeak/VmSize present in all
128 records, aggregate carries wall+RSS by schema design). Evidence: packet
`OPERATOR_RETURN.md` + `operational_replication_gate/` (five files);
`.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/`.

**Alternatives considered**:
- Rerun/tune seeds, N, K, floor, orders or thresholds: rejected —
  forbidden by the freeze; read 1/1 + attempt 1/1 are consumed.
- Treat as NOT_CONFIRMED or blocked: rejected — both recovery gates pass
  and all integrity gates pass; CANDIDATE is uniquely correct (with the
  plainly stated count-margin-2 caveat above).
- Promote to real-data FER/qualification/efficiency/key-rate/scaling
  evidence: rejected — scope is a model-sampled replication outcome at
  N=32768/f≤1.3 only.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. Next gate is main-thread acceptance.

## 2026-09-15 NB-Polar Phase 4-P16 N=32768 operational f=1.3 CANDIDATE returned (single run, exact-threshold meet)

**Decision**: Record the single P16 Tier-Y gate execution (exit 0, stderr
empty, wall 1183.61887 s within 2100 s) as candidate
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE`. Main-thread
acceptance is pending; this entry is not an acceptance and not blocked.
No route recommendation is made.

**Context**: Empirical construction at N=32768 (K_total 6811; K1 319/K2
6492; TRAIN residual 5.87097048643237e-07; leakage 34119; f
1.2998502888173578 ≤ 1.3) frozen before DEV; 16 TRAIN + 64 independent
operational DEV blocks (TRAIN genie 32 + DEV SC 128 calls). DEV exact
62/64 with Wilson one-sided 95% LB 0.9098711859061207 ≥ 0.90 — exactly at
threshold with ZERO-count margin (61/64 → 0.8883797143731994 would flip
to NOT_CONFIRMED). Integrity 13/13 true, failing list empty; undetected
0; preconditions 7/7 true; reads/attempts 1/1 spent at the first NPZ
content open; no reopen/rerun. Independent Pre-EXECUTE PASS and
Pre-RESULT PASS_WITH_COMMENTS (independent 62/64 recount + Wilson
recomputation confirm CANDIDATE). Evidence: packet `OPERATOR_RETURN.md`
+ `operational_f13_gate/` (five files);
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/`.

**Alternatives considered**:
- Rerun/tune seeds, N, K, floor, orders or thresholds: rejected —
  forbidden by the freeze; read 1/1 + attempt 1/1 are consumed.
- Treat as NOT_CONFIRMED or blocked: rejected — both recovery gates pass
  and all integrity gates pass; CANDIDATE is uniquely correct (with the
  blunt zero-margin caveat above).
- Promote to real-data FER/qualification/efficiency/key-rate/scaling
  evidence: rejected — scope is a model-sampled operational outcome at
  N=32768/f≤1.3 only.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. Next gate is main-thread acceptance.

## 2026-09-15 NB-Polar Phase 4-P15 empirical-genie mid-N scaling NOT_CONFIRMED (single run, negative)

**Decision**: Record the single P15 Tier-Y gate execution (exit 0, stderr
empty, wall 1620.511243 s) as valid scientific negative
`TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED`. Main-thread
acceptance is pending; this entry is not an acceptance, not a candidate, and
not blocked. No route recommendation is made.

**Context**: P13/P14 curve extended to N=32768/65536 under empirical
construction and f=1.3 allocation (K_total 6811/13636; splits
(314,6497)/(607,13029); TRAIN residuals 1.1128237904570182e-06/
1.1015630768662632e-10). Each N has 16 TRAIN + 16 independent DEV blocks;
orders frozen before each N's first DEV. DEV UCBs 0.035899663088366535 /
0.07612810621111707 — both >0.01, so `candidate_ns` [],
`smallest_candidate_n` null. Integrity 12/12 true, failing list empty;
preconditions 7/7 true; genie_calls 128/128; reads/attempts 1/1 spent at
the first NPZ content open; no reopen/rerun. Independent Pre-EXECUTE PASS
and Pre-RESULT PASS (numbers bit-exact; two non-blocking notes). Evidence:
packet `OPERATOR_RETURN.md` + `empirical_genie_mid_n_gate/` (five files);
`.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/`.

**Alternatives considered**:
- Rerun/tune seeds, N, K, floor, orders or thresholds: rejected —
  forbidden by the freeze; read 1/1 + attempt 1/1 are consumed.
- Treat as candidate or blocked: rejected — integrity passes (not blocked)
  but neither UCB ≤0.01 (not a candidate); NOT_CONFIRMED is uniquely correct.
- Promote to FER/real-channel/minimum-N/efficiency/key-rate/qualification
  evidence: rejected — scope is genie union-bound proxy only.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. Next gate is main-thread acceptance.

## 2026-09-15 NB-Polar Phase 4-P14 empirical-genie learning curve NOT_CONFIRMED (single run, negative)

**Decision**: Record the single P14 Tier-Y gate execution (exit 0, stderr
empty, wall 1110.16709 s) as valid scientific negative
`TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED`. Main-thread
acceptance is pending; this entry is not an acceptance, not a candidate, and
not blocked. No route recommendation is made — the more-TRAIN /
regularization / larger-N choice belongs to the main thread.

**Context**: At P13's N=16384 point, nested B=8/16/32/64/128 constructions from
one 128-block TRAIN sequence (streams 2026091930..37 x16), all evaluated on one
independent 32-block DEV set (streams 2026091940..43 x8), orders frozen before
first DEV, K_total=3399 (leakage 17059, f=1.2998121912679332). Per-prefix DEV
UCBs 0.17251343416734777 / 0.18789978997914214 / 0.15868335611416776 /
0.13913227660764454 / 0.2011332146072146 — all >0.01, so only the B=128 rule
applies and it fails. The curve is flat: B=128 (mean 0.1419810706809162) is not
better than B=8 (mean 0.1175773969604019); paired R_128−R_8 mean
+0.024403673720514288. Integrity 13/13 true, failing list empty; preconditions
7/7 true; genie_calls 320/320; reads/attempts 1/1 spent at the first NPZ
content open; no reopen/rerun. Independent Pre-EXECUTE PASS and Pre-RESULT
PASS_WITH_COMMENTS (non-blocking only, numbers verified). Evidence: packet
`OPERATOR_RETURN.md` + `empirical_genie_learning_curve_gate/` (five files);
`.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/`.

**Alternatives considered**:
- Rerun/tune seeds, prefixes, N, K, floor, orders or thresholds: rejected —
  forbidden by the freeze; read 1/1 + attempt 1/1 are consumed.
- Treat as candidate or blocked: rejected — integrity passes (not blocked)
  but B=128 UCB >0.01 (not a candidate); NOT_CONFIRMED is uniquely correct.
- Promote to FER/real-channel/minimum-N/efficiency/key-rate/qualification
  evidence: rejected — scope is genie union-bound proxy only.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. Next gate is main-thread acceptance.

## 2026-09-14 NB-Polar Phase 4-P13 empirical-genie f=1.3 scaling NOT_CONFIRMED (single run, negative)

**Decision**: Record the single P13 Tier-Y gate execution (exit 0, stderr
empty, total wall 496.580679 s) as valid scientific negative
`TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED`. Main-thread acceptance
is pending; this entry is not an acceptance, not a candidate, and not
blocked.

**Context**: Pre-P12-retry empirical-genie check at N=4096/8192/16384 under
empirical construction and f=1.3 allocation (K_total 840/1693/3399; splits
(38,802)/(78,1615)/(152,3247); TRAIN residuals
0.10927696273202786/0.005622605905980432/9.123285118244062e-05). TRAIN
8+8+8 blocks, DEV 32×3=96, orders frozen before first DEV. DEV empirical
UCBs 0.9522855359820204/0.4859431994053538/0.2524893538319819 — all >0.01,
so no registered N meets the frozen rule; `candidate_ns` [],
`smallest_candidate_n` null. Integrity 12/12 true, failing list empty;
preconditions 7/7 true; genie_calls 240/240; reads/attempts 1/1 spent at
the first NPZ content open; no reopen/retry/rerun. BEC means/UCBs
report-only, transcribed without interpretation. Independent Pre-EXECUTE
PASS and Pre-RESULT PASS_WITH_COMMENTS (non-blocking only, numbers
verified). Evidence: packet `OPERATOR_RETURN.md` +
`empirical_genie_scaling_gate/` (five files);
`.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/`.

**User-stated interpretive guards** (main-thread bounds, recorded verbatim,
not extended here): (1) ε_eff≈0.115 is currently only a scenario hypothesis
back-inferred from small-N behavior, not established; (2) higher HOLD
entropy means the fixed TRAIN disclosure is only ≈f=1.23 relative to HOLD
(less redundancy) — not numerically f≈1.37.

**Alternatives considered**:
- Rerun/tune seeds, N, K, floor, orders or thresholds: rejected —
  forbidden by the freeze; read 1/1 + attempt 1/1 are consumed.
- Treat as candidate or blocked: rejected — integrity passes (not blocked)
  but no N meets UCB≤0.01 (not a candidate); NOT_CONFIRMED is uniquely
  correct.
- Promote to FER/real-channel/minimum-N/efficiency/key-rate/qualification
  evidence: rejected — scope is genie union-bound proxy only.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. Next gate is main-thread acceptance.

## 2026-09-14 NB-Polar Phase 4-P12 target f=1.3 N-scaling profile TERMINAL BLOCKED (resource abort, single run)

**Decision**: Close packet `NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE`
as terminal `BLOCKED(resource_limits_met_and_no_abort)`. The single
authorized Tier-Y run executed once 20:53:45→21:12:37 (exit 1, stdout empty)
and resource-aborted on the N=262144 arm: uncaught `_ArrayMemoryError`
(64.0 MiB `(262144, 32)` float64 at `prior.py:255` via
`target_n_scaling.py:774` L2 candidate metric, outside both SC try-guards;
`MemoryError` outside the runner's caught
`(ValueError, FileExistsError, OSError)`). No output root created (end-only
writes), no label persisted, ~124 smaller-N blocks of in-memory progress
lost. Read 1/1 + attempt 1/1 spent at the first NPZ content open; no
reopen/rerun/repair/tuning. Independent Pre-EXECUTE PASS and Pre-RESULT
CONFIRMED_SINGLE_RESOURCE_ABORT. Evidence: packet `OPERATOR_RETURN.md`
(verbatim stderr) + `PRE_RESULT_REVIEW.md`; `STATUS.yaml` 1/1 spent.

**Alternatives considered**:
- Rerun/repair/retry with changed guards or checkpointing: rejected —
  forbidden by the freeze; attempt 1/1 is consumed and the packet is
  terminal.
- Treat the abort as a semantic or precondition finding: rejected — the
  traceback proves deep execution past preconditions/allocation into the
  N=262144 arm; the allocator refused, not a value/contract check.
- Promote partial in-memory progress to evidence: rejected — nothing was
  persisted; no artifacts exist.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. A successor packet, if any, requires NEW authorization.

## 2026-09-14 NB-Polar Phase 4-P11 exact chunked SC candidate returned (acceptance pending)

**Decision**: Record the single P11 Tier-Y gate execution (exit 0,
wall_total 97.955511 s) as candidate `EXACT_CHUNKED_SC_CANDIDATE`.
Main-thread acceptance is pending; this entry is not an acceptance.

**Context**: Allocation-only `_minus_block` promotion (keyword-only
`chunk_rows=512` default; `None` golden comparator; validation before
allocation; `sc_decode` signature unchanged). Gate seed 2026091800, float64,
GF32 poly 37 alpha 2. Semantic parity: 33 primitive cells all exact (11 rows
× 3 kinds, err 0.0, support parity); 16 V0 invalid-input cases all exception
type+message parity; N=64 + N=256 full-SC 9+9 cases all parity (incl. C4
N=64 U[3]=2 / N=256 U[3]=12 `ImpossibleDisclosedValueError` parity).
Paired N=65536 direct-first exact (u/x 0 mismatches, metrics/scores err 0.0;
walls 15.684/14.584 report-only). N=262144 status ok, finite True, wall
66.088411 s (report-only ≤120 met), RSS 710504448 < 1610612736 hard gate met
(margin 900108288; 1 GiB report-only met). Gates semantic_parity /
paired_n65536_exact / large_n262144_completion / large_n262144_rss all True.
Attempt 1/1 at first formal `sc_decode`, 0 artifact reads; no rerun/tuning.
Independent Pre-EXECUTE PASS (partial-evidence fallback ratified) and
Pre-RESULT PASS_WITH_COMMENTS (non-blocking only). Evidence:
`OPERATOR_RETURN.md` and `exact_chunked_sc_gate/` (four files: frozen_plan
2152 / equivalence_records 23808 / scaling_record 580 / report 8018 B) in
`.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/`.

**Alternatives considered**:
- Rerun/tune seed, chunk size, thresholds: rejected — forbidden by the
  freeze; attempt 1/1 is consumed.
- Treat N=65536 walls as a throughput claim: rejected — report-only; one
  draw cannot discriminate timing variance.
- Promote to FER/efficiency/key-rate/qualification evidence: rejected —
  scope is synthetic injected-data engineering gate only.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. Next gate is main-thread acceptance.

## 2026-09-14 NB-Polar Phase 4-P9 lower-rate boundary-resolution candidate returned (acceptance pending)

**Decision**: Record the single P9 Tier-Y gate execution (artifact wall
720.522313 s) as candidate `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE`.
Main-thread acceptance is pending; this entry is not an acceptance.

**Context**: The P8 grid left-censored the boundary below the (8,80) anchor.
P9 ran a SCREEN over the exact 8x7 grid (K1=[0,2,4,6,8,12,24,45] x
K2=[0,20,40,50,60,70,80] = 56 points, incl. (0,0) and the (8,80) anchor) on
seeds 2026091710..1712 x64 (192), reusing the accepted P7 orders
(sha 8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104)
with the 1e-15 floor. Exactly 10 points were eligible; (0,0) gave exact 0/192
(tag-only, zero undetected). Deterministic selection picked (k1=6,k2=70), key
(76,6,70). CONFIRM on disjoint seeds 2026091720..1724 x128 (640) at the
selected point only gave empirical 624/640 vs BEC control 520/640
(report-only), cells 520/104/0/16, Wilson LB 0.9626753340557015 (>=0.95,
>=618/640 met). Disclosure 5*(K1+K2)+64 per fully invoked point (selected 444
vs P8 anchor 504, report-only); totals key 4392768 / public 31559936 / tags
12032 with recount mismatch 0; planning-only f 2.165159928897918; RSS
318406656 B. Reads/attempts 1/1 consumed at the first NPZ content open; no
reopen/rerun/tuning. Independent Pre-EXECUTE PASS and Pre-RESULT PASS (zero
comments). Evidence: `OPERATOR_RETURN.md` and `lower_rate_screen_confirm/`
(five files) in
`.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/`.

**Execution incident**: The first Wave-C delegation executed the frozen command
and flushed the root at 15:29:50 but result delivery failed on an
infrastructure certificate error; the retry found the root present and STOPPED
without running anything (BLOCKED(prior-output-exists), nothing consumed);
read-only inspection verified single-flush provenance (0.3 s window, P9-only
identifiers, 56x192+640x2 shapes, frozen command verbatim). STATUS counters
aligned to 1/1; no rerun occurred. The incident changes no scientific fact.

**Alternatives considered**:
- Rerun/tune seeds, grid, floor or thresholds: rejected — forbidden by the
  freeze; read 1/1 + attempt 1/1 are consumed.
- Treat the BEC gap (104 empirical-only cells) or the anchor disclosure delta
  as a superiority claim: rejected — both are report-only.
- Interpolate between grid points or claim a global minimum rate: rejected —
  scope is the frozen grid plus one confirmed point.
- Promote to qualification/efficiency/key-rate evidence: rejected — scope is
  synthetic N=256 V25-1M-TRAIN model-sampled development signal only.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. Next gate is main-thread acceptance.

## 2026-09-14 NB-Polar Phase 4-P8 target-rate SCREEN→CONFIRM candidate returned (acceptance pending)

**Decision**: Record the single P8 Tier-Y gate execution (exit 0) as candidate
`TARGET_EMPIRICAL_RATE_POINT_CANDIDATE`. Main-thread acceptance is pending;
this entry is not an acceptance.

**Context**: Over the exact 35-grid (K1=[8,10,12,16,24,32,45] x
K2=[80,94,110,125,140]) with shared-block sampling on SCREEN seeds
2026091680..1682 x64 (192), all 35 points were eligible (Wilson LB>=0.95
each). Deterministic selection picked (k1=8,k2=80). CONFIRM on disjoint
seeds 2026091690..1694 x128 (640) gave empirical 638 exact / 2
verify_failed vs BEC control 621/19 (report-only), paired cells
621/17/0/2, Wilson LB 0.9906013676984646 (>=0.95, >=618/640 met).
Disclosure 5*(K1+K2)+64 per fully invoked point (selected 504), totals
key 5470080 / public 20984000 / tags 8000, recount mismatch 0.
Reads/attempts 1/1 consumed at the first NPZ content open; no
reopen/retry/rerun/tuning. Independent Pre-EXECUTE PASS (seed-coincidence
ratified FRESH) and Pre-RESULT PASS_WITH_COMMENTS (non-blocking only).
Evidence: `OPERATOR_RETURN.md` and
`rate_screen_confirm/` (five files) in
`.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/`.

**Alternatives considered**:
- Rerun/tune seeds, grid, floor or thresholds: rejected — forbidden by the
  freeze; read 1/1 + attempt 1/1 are consumed.
- Treat the BEC gap (17 empirical-only cells) as a superiority claim:
  rejected — BEC is report-only; empirical was not required to beat BEC.
- Promote to qualification/efficiency/key-rate evidence: rejected — scope is
  synthetic N=256 V25-1M-TRAIN model-sampled development signal only.

**Consequences**: No OpenSpec box checked; no code/artifact/old-root change;
no commit/push. Next gate is main-thread acceptance.

## 2026-09-13 NB-Polar Phase 6 fixed-incremental paired gate blocked on recovery

**Decision**: Record the Phase 6 fixed-incremental paired 300-block development
gate as `BLOCKED(incremental_exact_ge_285)`. The negative result is final for
this packet: no rerun, no seed change, no threshold or K tuning. Main-thread
disposition is pending.

**Context**: One frozen paired attempt (exit 0) ran the incremental arm
(K=(29,33,37,41,45)) and an in-run static K=45 comparator on the same 300
synthetic blocks (300/300 paired_match). Incremental saved 28.2% key-dependent
disclosure (207.293333 vs 288.573333 avg bits; integer rule 6218800 <= 8224340)
and passed 16 of 18 gates, but failed the recovery gates: incremental exact
271 < 285 and Wilson one-sided 95% LB 0.8715597837542944 < 0.90; the paired
static arm was 298/300 exact. The 29 incremental `decode_failed` (and 2 static)
were all `ImpossibleDisclosedValueError` at invoked level 0.

**Mechanism**: On the q-ary erasure channel a wrong early SC decision can make a
later true disclosed value have exact-zero support, raising the accepted
`sc.py` `ImpossibleDisclosedValueError`; the frozen fail-closed rule then
terminates the block at that level. Independent Pre-RESULT review classified
this as valid scheduled science, not an implementation defect, and confirmed
the evidence is self-consistent.

**Alternatives considered**:
- Rerun/tune K, seeds or thresholds to clear the gates: rejected — forbidden by
  the freeze; attempt 1/1 is consumed and the run seed is spent.
- Report a candidate from the passing disclosure gate alone: rejected — the
  candidate label requires all 18 gates, including recovery.

**Consequences**: Pre-EXECUTE PASS and Pre-RESULT PASS_WITH_COMMENTS are
recorded; `STATUS.yaml` is `attempts_used: 1`, `next_gate:
MAIN_THREAD_DISPOSITION`. A successor (level-advance reject semantics, a
different frozen K/early-safety level) or closing the route is a main-thread
design decision. No commit or push; no qualification or promotion claim.

## 2026-09-11 NB-Polar Phase 3 blocked; one-shot EVAL retained as diagnostic

**Decision**: Record Phase 3 as `BLOCKED(PHASE3_GATE_INVALID)`. Retain the sole
EVAL as diagnostic, do not rerun it, do not relax its gate, and do not enter
Phase 4.

**Context**: The implementation tests report 45/45 pass, but the first frozen
construction gate fails: full-vector Spearman is 0.7665 below 0.90. The later
e>0 subset value 0.9959 cannot replace the preregistered population. The
required independent reviewer-go was unavailable and an operator self-check
incorrectly authorized EVAL. The reconstructed invocation also omits the
literal full 256-coordinate permutation. The resulting one-shot EVAL is
preserved: 299/300 exact, 300/300 initial-error, one impossible disclosure at
block 104.

**Consequences**: The result suggests a small residual failure probability at
q=32, N=256, epsilon=0.05, K=45, but does not prove N/K is the unique cause.
Any Phase 3-R1 construction/gate revision requires a fresh packet and explicit
authorization; EVAL seed 2026091203 remains consumed and may not be rerun.

## 2026-09-11 NB-Polar Phase 2 reference SC and oracle accepted

**Decision**: Accept the Phase 2 log-domain q-ary SC, explicit partial-sum
recursion, known-coordinate semantics, and independent exhaustive oracle as
`IMPLEMENTATION_ACCEPTED`.

**Context**: reviewer-go independently reported 33/33 tests passing. Across
221 production/oracle comparisons, maximum probability error was 3.331e-16,
maximum finite log error 1.776e-15, with zero support mismatches. Noiseless
loopback was 831/831 exact. The main-thread review closed five comments without
rerunning the trusted suite; the only correction was a report count from “all
32 betas” to four representative betas.

**Consequences**: Phase 3 synthetic construction may be planned separately.
This acceptance makes no construction, FER, Model-F, real-data, protocol,
benchmark, qualification, or promotion claim.

## 2026-09-11 NB-Polar Phase 1 transform implementation accepted

**Decision**: Accept the Phase 1 GF4/GF32 adapter, natural-order transform,
dense reference, and source-coordinate selection as
`IMPLEMENTATION_ACCEPTED`. The independent pytest run collected and passed
17/17 tests.

**Context**: The execution-session candidate passed its plain-Python runner.
The main thread additionally located pytest 9.0.3 in the installed Miniforge
environment and reran the exact focused file: 17 passed in 2.06 seconds. Fast
and dense paths are independent, natural order has explicit anti-bit-reversal
cases, and frozen directories plus forbidden dependencies remain clean.

**Consequences**: Phase 2 may receive a separate SC/oracle implementation
packet. `N=1` without a dedicated test and acceptance of `alpha=0` are recorded
Phase 1 limitations; the operative MVP remains fixed to primitive `alpha=2`.
No decoder, Model-F, real-data, performance, result, or promotion claim follows.

## 2026-09-11 venv-only docs fix + fence fix

**Decision**: 冻结 venv-only Python 入口（`.venv/bin/python -m ...`），不改代码。

**Context**: 裸 `python`/`python3` 缺 numpy/pytest 导致误报，需统一文档与示例。

**Alternatives considered**:
- 裸 python：已否决（系统 python 缺依赖）。

**Consequences**: 示例统一 venv 前缀；§7 旧裸示例另开 follow-up。

## 2026-09-11 NB-Polar Phase 0 document freeze accepted

**Decision**: Accept `openspec/changes/nbpolar-phase0-freeze/` as
`FREEZE_ACCEPT`. Phase 1 packet preparation is unlocked. The acceptance covers
only document and pure-array alignment; implementation, decoder, Model-F,
real-data, result, qualification, and promotion flags remain false.

**Context**: A first review returned four blockers. After correction, the
execution-session review returned `PASS with comments`; the main thread
rechecked the current files, the D4R2 formula and result lines, three synthetic
array checks, scoped path hits, and the isolation ban list. The durable verdict
is `docs/research_cycles/NBPOLAR-PHASE0/FREEZE_REVIEW_VERDICT.md`.

**Consequences**: Canonical docs now state the two-reference Phase 0 basis,
relative path discipline, absolute tolerance semantics, and natural-log versus
bit units. Phase 1 work must use a separate bounded packet and cannot open
Phase 2 or any claim-bearing run.

## 2026-09-11 NB-Polar independent worktree initialized

**Decision**: This checkout is the sole NB-Polar planning and future
implementation location. Its canonical documents are docs/nbpolar/ and
OpenSpec change formal-ir-nbpolar-mvp. The inherited Comparison, Cascade,
and Release checkouts remain separate reference projects.

**Context**: The prior live APP-transfer draft coupled a proposed Polar
upper layer to the unresolved NB-LDPC lower layer. The new plan separates
GF arithmetic, symbol metrics, transform, construction, decoder, prior,
protocol, and validation so a failure is attributable to one layer.

**Frozen candidate**: GF32 polynomial basis, primitive polynomial 37,
alpha=2 kernel F_alpha=[[1,0],[alpha,1]], natural index order, normalized
float64 log-probabilities, source SC, static full-symbol disclosure, and one
final universal tag. Model-F and Release assets enter only through explicit
adapters. CRC, puncturing, shortening, SCL, and real-data execution are
later gates.

**Status**: PLAN_CANDIDATE / IMPLEMENTATION_NOT_AUTHORIZED /
EXECUTE_NOT_AUTHORIZED. No decoder, result root, benchmark, leakage,
security, qualification, promotion, or push is implied by this entry.
### 2026-08-24: Use GitHub as the ChatGPT/OpenCode research exchange surface

**Decision**: Use repository-native, copy-pasteable handoffs rather than MCP.
ChatGPT owns planning and read-only scientific review; OpenCode implements a
frozen packet; the user/main reviewer owns acceptance and formal-execution
authorization. `docs/research-cycle-sop.md` is the workflow authority.

**Context**: Chat histories are not durable or shared, and high-capability
execution models can confidently invent missing requirements or overstate
results. Each side therefore receives an exact repository/branch/SHA and a
fixed entrypoint, then returns a stable schema that is copied back into Git.

**Data decision**: Each research milestone includes compact machine-readable
data when practical. Large, binary, raw, private, or replaceable artifacts may
remain outside Git only when the commit includes a result summary with data
identity, seeds, commands, metrics, omissions, claim limits, and reproduction
or retrieval instructions.

**Publishing boundary**: Normal non-force pushes only. An incompatible remote
Polar/crosstalk line is not merged into the formal-IR research history; use a
separate formal-IR branch.

**Consequences**: Agent completion is not acceptance, a test pass is not
scientific success, and development evidence is not qualification. The SOP
must remain lighter than the algorithm work it supports.

### 2026-08-24: Preserve V36 as an exploratory residual signal, not an accepted candidate

**Decision**: Retain V36 code and compact run data, but label A1 DE selection
unaccepted, A2 structural gate failed, and A3 development-only exploratory.
The overall terminal remains `NO_FINITE_GRAPH_ADVANCE`.

**Evidence**: The paired finite data show mean residual 174.80 -> 157.07 and
10/15 improved blocks, but 0/15 exact recovery. All source median gates miss
15%; two blocks worsen by more than 10 errors. The realized graphs contain
thousands of 4-cycles and degree-2 cycle ranks 779--801 despite a frozen zero
cycle requirement. DE confirmation did not compare each source to a baseline
under identical confirmation settings or enforce the required 10% threshold.

**Consequences**: V36 supports a bounded hypothesis that low-average-degree
irregular graphs deserve a corrected finite-aware test. It does not prove
empirical-P DE superiority, trapping-set causality, general FER improvement,
or the necessity of MET.

### 2026-08-24: Close V34 as an ER1-accepted bounded finite-control failure

**Decision**: Accept the single authorized V34 official run as
`matched_empirical_finite_control_fail` and prohibit V34 rerun or tuning.

**Evidence**: Accounting-corrected HEAD `c8cc1fbe` passed independent IR1 and
the complete 45-test fake suite. The authorized 60-block matrix completed with
no fatal record. All three sources had 0/20 exact/syndrome/tag successes, while
mean L2 errors fell by about 31--32%. Strict absolute-path verification was
consistent and independent ER1 accepted all recomputed initial/final counts,
runtime fields, ordinals, authorization, and terminal. No run_02 exists.

**Interpretation**: Matching the empirical generator and posterior removes the
V32 B1 attribution defect, but does not make this one V31 QC finite realization
and V28R decoder succeed at oracle L1 and max_iter=30. Partial error reduction
shows useful posterior/decoder motion; 37 converged-no-syndrome and 23 max-iter
blocks point to finite-graph/iterative dynamics without uniquely identifying
the cause.

**Consequences**: Close current-packet tuning. Use existing residuals to guide
one empirical-P-informed protograph/MET candidate and one rate-adaptive or
incremental-syndrome mother-code design. Any higher-iteration check or new
finite run is a separate successor, not a V34 retry.

### 2026-08-24: High-performance correction algorithms are the strict first principle

**Decision**: Make discovery, implementation, and experimental validation of
high-performance IR/error-correction algorithms the project's strict first
principle. Benchmark, evidence, lifecycle, and review work are supporting
means, not the research output.

**Priority metrics**: correction success/FER, leakage and reconciliation
efficiency, throughput/runtime, memory/resource cost, and accepted-frame net
secret-key yield.

**Blocking rule**: Engineering, audit, or verifier findings block algorithm
work only when they can concretely cause wrong numerics/scientific attribution,
irreproducibility, unauthorized expensive execution, or destructive overwrite.
All other engineering improvements are non-blocking or deferred.

**Consequences**: Do not turn algorithm development into package-hardening or
adversarial-verifier work. Use the smallest scientifically valid implementation
and validation, measure the method, then allocate effort to the next
highest-information correction algorithm.

### 2026-08-24: Freeze V34 and stop after the P3 implementation candidate

**Decision**: Accept the revised V34 specification freeze, implement only the
minimal fake/test-isolated candidate, and stop at
`IMPLEMENTATION_CANDIDATE / EXECUTE_NOT_AUTHORIZED` for Ox Alpha evidence work
and independent Codex IR1.

**Evidence**: Initial FR1 rejected ambiguous RNG, threshold, decoder-matrix,
failure and protected-root semantics. Revised FR1 returned ACCEPT; independent
science review accepted the carried-forward >=19/20 mechanical discriminator,
bounded-sample claim, max_iter=30 comparability binding and literal NumPy 2.4.0
reference vector. The P3 candidate passes compile, selfcheck, real-input
read-only prepare and 13 focused fake tests; official V34 `run_01` is absent.

**Alternatives considered**:
- Change the gate to 20/20: rejected because it would change the decision rule
  together with the generator and spoil the V32/V34 single-channel-law contrast.
- Raise max_iter to 200 now: rejected because it changes a second variable;
  decoder-iteration adequacy is a separate possible successor.
- Treat 19/20 as FER evidence: rejected; 20 blocks/source are only a bounded
  diagnostic conditional on this packet and decoder configuration.
- Let Ox Alpha execute the real decoder or self-accept: rejected; it is an
  implementation/evidence operator, while Codex retains IR1 and execution gates.

**Consequences**: Ox Alpha may complete the frozen P4 fake T2/T3 evidence
packet. No production decoder, official root, EXECUTE_AUTH, ER1, qualification,
promotion or successor is authorized. See
`docs/v34-p3-implementation-candidate-and-ox-alpha-handoff-20260824.md`.

### 2026-08-24: V33 exact-rate empirical-P ensemble gate passed

**Decision**: Accept the single authorized V33 `run_01` as
`PASS / pass_rate_aligned_empirical_de` after independent ER1, while retaining
an ensemble-only claim boundary.

**Evidence**: 30/30 registered calls PASS; all six source×layer cells PASS
5/5 at the V31 exact rates. Strict replay returned `consistent`,
`problems=[]`, `records_checked=30`; independent ER1 returned ACCEPT. L1 used
23–25 iterations and L2 37–44. No decoder, finite-control, rerun, tuning, or
successor ran.

**Alternatives considered**:
- Treat V31/V32 as proof the whole NB-LDPC route failed: rejected because V32
  used mismatched generator/posterior laws and V33 now passes at the actual
  empirical-P ensemble operating point.
- Infer finite-code success from V33: rejected because DE does not test the
  fixed QC graph, decoder, FER, or finite-length conversion.
- Start a matched control automatically: rejected; it requires a new frozen
  OpenSpec and explicit authorization.

**Consequences**: The exact-rate ensemble veto is removed. The next proposed
scientific gate is one corrected matched empirical-P finite-control that keeps
the V31 QC packet/decoder fixed and changes only generator/posterior matching.
V33 must not be rerun, tuned, or promoted to qualification evidence.
The diagnostic change is archived without merging its delta spec into the
canonical method specs; no successor is authorized.

### 2026-08-21: V31 deterministic finite-graph redesign gate closed with `finite_graph_fail`

**Decision**: Execute and archive the V31 gate as `finite_graph_fail`.

**Context**: V30R failed at the finite graph/decoder conversion layer. V31
tested the successor hypotheses (m1=16, projective-capacity-aware PEG,
deterministic QC control, n=1024/2048) with no search/seed/probity changes.

**Evidence**:
- M1 DE confirmation PASS 60/60 (30/30 per n, m1=16).
- M2: PEG-capacity-aware rejected at both n (L2 GF32 rank-deficient:
  m=200->199, m=414->413); QC-cyclic-projective constructed OK (occupancy<=31).
- M3: n=1024 full window 300/300 exact/tag=0, L2 always `converged_no_syndrome`
  -> exact/tag FER=1.0; n=2048 bounded 1M prefix (14 blocks) repeats the failure.
- Read-only verifier ok=true, problems=[]; terminal finite_graph_fail.

**Alternatives considered**:
- Re-run/tune V30R balanced packets: prohibited by the frozen objective.
- Random matrix-library search / seed adjustment: prohibited.
- Continue the unbounded n=2048 full window: infeasible (non-converging L2
  decodes took tens of minutes to hours per block); closed on a bounded 1M
  prefix per the pre-registered design contingency.

**Consequences**: V31 closes this finite-graph conversion route as negative at
both tested block lengths and both deterministic families. A successor requires
a new user authorization and new OpenSpec change; the primary diagnostics are
L2 syndrome non-convergence on the empirical channel and PEG L2 rank
deficiency at these sizes. No push, qualification, or promotion occurred.


### 2026-08-20: V30R finite-graph gate closed with `finite_graph_fail`

**Decision**: Close and archive V30R after the canonical `run_01` execution
and independent read-only verification. The verifier returned `ok=true`,
`problems=[]`, and recomputed the persisted terminal `finite_graph_fail`.

**Evidence**: M0 reproduced `15/69/303/922/1107`. M1 persisted all 72 screen
calls and 60 confirmation calls; screen-eligible `m1=9,12,16` were ranked,
`m1_9` and `m1_12` were selected, and both completed 30/30 confirmation. M2
retained valid balanced packets for `m1=9,12`; both PEG packets were
deterministically rejected because no projectively unique ratio survived for
support `(0,1)`. M3 screened both valid packets on source 1M blocks `0..5`,
with `0/6` exact/tag-verified and `0` false accepts for each, making the
frozen `15/20` screen threshold impossible. The stage stopped before other
sources and before confirmation. M1/M3 meters were 74.828 s and 719.876 s.

**Scientific boundary**: This is negative only for the tested `n=1024`, F03,
fixed-allocation, balanced/PEG-family finite conversion under the V28 decoder.
It does not negate V25's empirical channel, V26's channel-informed DE, or all
NBLDPC designs. It makes no FER qualification, fresh qualification, promotion,
integration, or public-residual claim.

**Consequences**: V30R evidence and failure are archived. Same-packet expansion,
rerun, decoder tuning, random matrix/degree search, V29 holdout reuse, and
automatic fallback are prohibited. A future finite-graph redesign requires a
new user-authorized OpenSpec; recorded hypotheses are `m1=16`,
projective-capacity-aware PEG, L2 girth/expander/QC/SC constraints, and
`n=2048/4096`. No push was performed.

### 2026-08-20: V30R P103 freeze review ACCEPTED

**Decision**: The independent third P103 freeze review ACCEPTED the V30R
projective-safe finite-graph gate on 2026-08-20. The four-document packet is
now `FROZEN_P103_ACCEPTED`; its frozen implementation and pre-registered V30R
execution are authorized.

**Boundary**: This records authorization, not execution. No V30R code,
finite-code construction, DE, decoder call, or scientific output has started
as of this entry. Fresh qualification, promotion, archive, commit, and push
remain separate actions and are not implied by P103.

**Consequence**: The next operator may implement the exact frozen packet and
then execute its registered gate, preserving the no-rerun/no-tuning and
evidence-boundary rules in the V30R four-set. The active state is not pending
review, and P102 remains historical/superseded.

### 2026-08-20: V27R freeze review ACCEPT (P102) — in-conversation independent review

**Decision**: The V27R OpenSpec (source-adaptive finite-leakage-margin) received an
independent freeze review run ON THE MAIN THREAD directly in this conversation (per
user authorization; subagent not required). Verdict: ACCEPT. The main thread recorded
P102 ACCEPT, unblocking Phase B.

**Context**: subagent infrastructure was persistently unavailable (rounds 1-4). The user
explicitly authorized running the independent review in-conversation and updating the
goal wording accordingly (goal revision 3-4: reviews by main thread in this conversation,
not gated on subagent availability).

**Independent review findings (recomputed independently):**
- H from channel_counts.npz (F03): 1M 0.024280547/0.776757278; 1p5M 0.025199497/0.800366555;
  2M 0.025662049/0.806900673. Matches frozen docs.
- m_total source-adaptive: 1M 200/413/840/1693; 1p5M 206/426/866/1745; 2M 208/430/873/1760
  for block_len 1024/2048/4096/8192. MATCH.
- m1_ep=round(m_total*H1/H_total): 1M 6/13/25/51; 1p5M 6/13/26/53; 2M 6/13/27/54. MATCH.
- Realized f<1.3 all 12 cells (1.29409-1.29974). All 5 candidates per cell legal
  (m1,m2 in [0,m_total], <n). Rates R1~0.993-0.994, R2~0.79-0.81.
- All 14 required spec items captured (proposal/design/tasks/spec); terminal states only
  the 4 allowed; no fixed_ensemble_margin_fail; prohibitions present; no overclaim
  (V27 is asymptotic DE only). Item-by-item check passed.

**Consequences**: V27R FREEZE ACCEPTED; P102 ACCEPT recorded by main thread (goal owns
ACCEPT). Phase B may now proceed: minimal budget planner + V26 MC-DE adapter wrapper,
T0/T1, screen/confirmation, readonly verifier, local commit + archive, no push.

### 2026-08-20: V27R freeze-review gate still blocked by subagent infrastructure (round 2)

**Decision**: Keep V27R OpenSpec in PENDING_FREEZE_REVIEW. P102 ACCEPT is NOT recorded and
Phase B is NOT started because the required independent Luna freeze review still cannot be
delivered: the subagent infrastructure failed every attempt this round (foreground subagent
x1, background subagent x3, muse_spark x1), and earlier-round attempts also failed. The main
thread has independently re-verified the full arithmetic and evidence (P001/P002 closed) and
produced a freeze-review packet (tmp_v27r/v27r_freeze_review_packet.md), but that does NOT
substitute for the independent review.

**Context**: Phase A gate (item 13/14) requires an independent Luna freeze review before
acceptance. This is a process/infrastructure blocker, not a scientific result.

**Alternatives considered**:
- Record P102 ACCEPT on the main thread's own verification: rejected — the goal mandates an
  independent Luna review; fabricating acceptance would violate the strict gate.
- Start Phase B implementation anyway: rejected — violates "freeze review ACCEPT 前不实现".

**Consequences**: V27R docs and evidence are ready; only the independent review is pending on
infrastructure. When subagent infra is available again, a fresh Luna freeze review must run;
on ACCEPT, record P102 and proceed to Phase B. Goal remains active.

### 2026-08-19: V27R OpenSpec revision — source-adaptive finite-leakage-margin budget

**Decision**: Revise V27 OpenSpec from a single worst-source budget to a **source-adaptive**
budget: each source (1M/1p5M/2M) uses its own full-precision H1/H2 and
`m_total = floor((1.3*block_len*H_source - 64)/5)`. Frozen table (block_len
1024/2048/4096/8192 -> m_total): 1M 200/413/840/1693, 1p5M 206/426/866/1745,
2M 208/430/873/1760 (arithmetic re-verified). m1_ep = round(m_total*H1/H_total) (Python
round, round-half-to-even, frozen explicit rule); candidates m1_ep+offset for offset in
{-2,-1,0,+1,+2}; all five eligible. V27 is asymptotic true-predecessor-conditioned
multistage DE (L2 conditioned on correct L1; no finite-code error propagation); the
single 64-bit tag counts only in total block leakage, not between layers. Terminal states
only pass_finite_budget_ready / de_pass_no_finite_headroom / implementation_blocked /
resource_blocked. 24h global completed-call cumulative resource gate; checkpoint bound
to frozen config; V26 archived reference only (no rerun).

**Context**: V26 proved asymptotic A02 (F03 GF32+GF32) DE converges 30/30 at f=1.3. The
finite-leakage-margin gate must answer whether, at finite block length + integer code
rate + 64-bit tag cost, the fixed ensemble retains positive convergence headroom per
source. A single worst-source budget under-allocates 1M/1p5M.

**Alternatives considered**:
- Worst-source single budget (previous draft): rejected — under-allocates 1M/1p5M
  headroom; replaced by source-adaptive.
- m1/m2 search: rejected — only entropy-proportional split plus +/-2 window is tested;
  no degree/m1/m2 search.

**Consequences**: V27R docs written to openspec/changes/formal-nonbinary-ldpc-v27-.../
(proposal/design/tasks/spec). STILL PENDING_FREEZE_REVIEW: the independent Luna freeze
review could not be delivered this session because the subagent infrastructure failed
repeatedly (foreground and background subagent/muse_spark all failed; background agents
stuck in "ready" with no result). P102 ACCEPT was NOT recorded and Phase B was NOT
started, per the strict gate. The freeze review must be completed (Luna worker) and
accepted before any V27 implementation/execution.


### 2025-06-01: Non-invasive comparison layer architecture

**Decision**: The comparison benchmark is built as an outer wrapper (`comparison_bench/`) that reads the original Polar pipeline outputs without modifying them. The original `src/`, `experiments/`, and `tools/` directories are frozen baselines.

**Context**: We needed to compare multiple IR methods without risking regressions in the proven Polar pipeline.

**Alternatives considered**:
- Fork the repo and modify in-place: rejected because it would create maintenance burden and risk breaking the original workflow.
- Build a separate, fully independent project: rejected because we need to directly import/read Polar results.

**Consequences**: 
- `comparison_bench/` is the only mutable area for new IR comparison work.
- The `polar_existing` bridge in `comparison_bench/src/comparison_bench/io/polar_existing_bridge.py` is the sole interface for reading original Polar outputs.

---

### 2025-06-15: OpenSpec workflow initialization

**Decision**: Adopt OpenSpec as the change management workflow for all substantial feature work.

**Context**: Multi-agent workflow requires clear proposal → design → tasks → implement → review → archive pipeline.

**Alternatives considered**:
- GitHub Issues only: rejected because no structured design/spec/task linkage.
- Ad-hoc task lists: rejected because no durable record of decisions and spec changes.

**Consequences**:
- All substantial changes must go through `openspec/` workflow.
- `AGENTS.md` is authoritative for agent rules.
- `docs/decision-log.md` (this file) records durable decisions.

---

### 2026-06-15: Real IR success before final method selection

**Decision**: Prioritize verified real information reconciliation success on high-dimensional arrival-time QKD frames before final error-correction method selection or efficiency comparison.

**Context**: The existing Polar line has produced results, while most non-Polar comparison methods still need stable real-data verification success. Comparing `beta_eff_empirical`, leakage, or runtime before methods actually reconcile real frames risks optimizing a metric artifact instead of solving the IR problem.

**Alternatives considered**:
- Immediate final method selection: rejected because non-Polar methods have not yet established enough verified real-data success.
- Continue broad parameter sweeps first: rejected because broad sweeps are less useful until success/failure criteria and representative real-frame validation are explicit.
- Treat synthetic success as sufficient: rejected because the first-principles target is real high-dimensional arrival-time QKD reconciliation.

**Consequences**:
- The next active OpenSpec change is `real-ir-success-first`.
- Cascade-lite is treated as the first non-Polar real-success candidate, with simplified-Cascade caveats.
- Layered LDPC is treated as an executable failure-diagnosis target before being considered a final candidate.
- qLDPC remains a reference-grade q-ary feasibility direction until stronger evidence exists.
- Final method selection is deferred until verified real-data success and leakage accounting are established.

---

### 2026-07-25: Reconciled evidence is not final method-selection proof

**Decision**: Retain Cascade-lite as the preferred executable non-Polar
candidate and Layered LDPC as the control baseline, but defer final selection
until a new, pre-registered frame-identical confirmation change is completed.

**Context**: The Phase 0 reconciliation verified real-success, optimization,
expanded-evidence, and group-meeting artifacts. It also found material limits:
historical Polar is not frame-identical, low-dimensional group-meeting points
usually have only four frames, and historical changes do not all meet their
written acceptance criteria.

**Alternatives considered**:
- Archive historical changes solely because reports and manifests exist:
  rejected because the acceptance gaps are explicit and measurable.
- Declare Cascade-lite the final production method now: rejected because the
  evidence is bounded and accounting/Polar comparability are incomplete.

**Consequences**:
- No historical IR OpenSpec change is archived in this reconciliation pass.
- The next substantive work is a `final-ir-method-selection` OpenSpec change
  with fixed candidates, compatible leakage reporting, separate tuning and
  confirmation frames, and a stated stopping rule.

---

### 2026-07-25: Bounded final-IR confirmation yields no final winner

**Decision**: Record `no_decision` for the locked medium-SER confirmation; do
not promote Cascade-lite to a final winner from this run.

**Context**: The read-only Phase 4 audit at
`comparison_bench/outputs_comparison/final_ir_method_selection/20260725_v4_audit/`
verified the same 60 unique locked confirmation keys for both candidates, all
attempted statuses, summary denominators, corrected-grid frozen configurations,
and recorded lock hashes. Cascade had 60/60 independently verified successes
and Layered LDPC 59/60; the exact pre-registered two-sided McNemar/binomial
p-value for the one discordant pair is 1.0 at alpha 0.05.

The prior v3 audit is superseded by its additive notice because a generic
decision-helper branch did not represent an LDPC winner or insufficient
evidence. That repair does not change this run's p=1.0 `no_decision` outcome.

**Alternatives considered**:
- Declare Cascade the winner on raw success count: rejected because the
  pre-registered paired test is not significant.
- Rank methods by reported leakage: rejected because the disclosure
  decompositions are method-specific and intentionally non-comparable.

**Consequences**:
- The evidence supports only real d=1024, 64-symbol frames with dataset raw
  SER in [0.20, 0.30); it makes no broader, Polar, qLDPC, or Route A proof claim.
- The non-numerical Route A compatibility gate is `fail`: the Phase-3 schema
  lacks the documented universal-hash protocol, leakage, and correctness-bound
  fields. No Route A numerical rerun was performed.

---

### 2026-07-25: Final-selection evidence is revalidated read-only

**Decision**: Keep the locked v1 data split, authoritative v2 run, and v4
audit immutable; use only read-only verification for their revalidation.

**Context**: Phase 5 hardened the comparison-layer workflow without changing
the frozen baseline or existing evidence. The v1 lock verification and v4
audit verification passed; the latter still reports `no_decision` with p=1.0
and a failing non-numerical Route A compatibility gate.

**Consequences**:
- Future Phase-3 runs require an explicit new additive output directory and
  persist `pre_run_plan.json` before tuning.
- The runbook at `comparison_bench/docs/final_ir_method_selection_runbook.md`
  is the operational entry point for lock, bounded run, and audit commands.
- The result remains bounded to its locked domain; no winner, cross-method
  leakage rank, Polar/qLDPC comparison, Route A numerical result, or proof
  completion is implied.
---

### 2026-07-25: Formal Cascade/LDPC Must Precede Three-Method Ranking

## Decision

Create OpenSpec `implement-formal-cascade-and-ldpc` before attempting a
frame-identical Cascade/LDPC/Polar comparison. It introduces additive
`cascade_formal_v1` and `ldpc_formal_v1` under an offline, already-authenticated
public-channel model, with Alice reference/Bob correction, universal2 Toeplitz
verification, explicit disclosure accounting, and independent qualification.

## Rationale

The existing `cascade_lite` and `layered_ldpc_lite` are executable baselines,
not sufficiently protocol-faithful formal competitors. A three-way comparison
before formalizing them would compare Polar to simplified implementations.

## Consequences

- Lite identities and historical evidence remain unchanged.
- No Polar adapter, formal winner, network/authentication cost, finite-key or
  Route-A numerical claim belongs to this change.
- A later OpenSpec may enable frame-identical three-method comparison only
  after separately qualified formal candidates exist.
- The active spec freezes exact Toeplitz seed/index/transcript semantics,
  Cascade FIFO look-back, deterministic HGF2V1 LDPC codebooks, calibration-only
  rate selection, pinned `ldpc==2.4.1`, additive artifact/status provenance,
  and predeclared synthetic and fresh real-frame promotion gates.
- One or both methods may be archived as `non_promoted`. Only promoted formal
  methods may enter a future Polar comparison; a non-promoted method requires
  a new improvement change and cannot be replaced by its lite predecessor.
- Pinned `ldpc==2.4.1` constructor behavior overrides its docstring: although
  the documentation advertises `random_serial_schedule`, the constructor
  rejects it. Formal kwargs omit it and require serial schedule, explicit
  `[0..63]` order, and one OMP thread. Preflight must prove exact kwargs
  acceptance with a no-decode 1-by-64 constructor probe and fail closed
  otherwise.

---

### 2026-07-25: Synthetic v2 is diagnostic and does not promote a method

**Decision**: Exclude synthetic v1 and v2 from promotion and reopen Phase 5 for
a fresh, contract-compliant v3. No formal method is promoted by these runs.

**Context**: v1 made zero frame calls. v2 listed the pre-registered Alice seed
`2026072501` and frame-order seed `2026072531` but did not use them; it
generated batches using undeclared Alice seeds `2026072502..2505`. Therefore
its outcomes and prior verifier pass do not prove pre-registered generation.

**Consequences**: v2 receives an additive invalid notice and remains diagnostic.
Fresh v3 must bind exact RNG calls/order, qualification-only shared verification
seeds, original transcript bytes, deterministic runner preflight, complete
provenance, exception finalization, and strict verification. Phase 6 and Polar
comparison remain unauthorized.

---

### 2026-07-25: Formal synthetic v3 promotes Cascade only

**Decision**: Record the immutable v3 synthetic qualification as promotion for
`cascade_formal_v1` and non-promotion for `ldpc_formal_v1`.

**Context**: The additive v3 package completed once and its strict read-only
verifier accepted all six artifacts and 128 outcomes. Cascade achieved 32/32
`verified_success` in each p=.01 and p=.02 stratum. LDPC achieved 29/32 and
14/32, below the 31/32 promotion threshold; all remaining outcomes were
retained `verify_failed`, with zero unclassified/internal/provenance/accounting
failures.

**Consequences**: Do not retune this LDPC evidence or replace it with a lite
method. Phase 6 locked real qualification remains required; no Polar adapter
or three-method ranking is authorized by the synthetic result.

---

### 2026-07-25: Bounded formal real qualification promotes Cascade only

**Decision**: Promote `cascade_formal_v1` for the locked real confirmation
domain only: `d=1024`, 64 symbols, bw120, frame SER `[0.20,0.30)`. Do not
infer general Cascade performance or a Cascade-versus-Polar winner.

**Context**: The unique real v2 package passed its strict read-only verifier.
All 60 requested confirmation frames were attempted, denominator-included,
verification-invoked, and `verified_success`, with verification union bound
`3.2526065174565133e-18` and zero unclassified/internal/provenance/accounting
failures. Its exact preflight passed 29 tests with exit 0. The invalid real v1
lock remained unexecuted and byte-preserved apart from its additive invalid
notice. Synthetic v3 separately promotes Cascade at 32/32 in both strata but
leaves LDPC non-promoted at 29/32 and 14/32; LDPC was not run on real data.

**Alternatives considered**:
- Generalize the 60-frame result to other dimensions, frame lengths, bandwidth
  groups, or SER regions: rejected because those domains were not qualified.
- Treat this as a Polar comparison or winner claim: rejected because Polar was
  not run frame-identically in this change.
- Substitute `layered_ldpc_lite` or retune formal LDPC on confirmation:
  rejected because the formal LDPC promotion gate failed and confirmation is
  locked evidence, not tuning data.

**Consequences**:
- The active formal-method change is technically ready for archive review, but
  is not archived until memory triage and the actual archive action complete.
- A new LDPC-improvement OpenSpec change must earn fresh synthetic and real
  promotion before any frame-identical Polar/Cascade/LDPC comparison.
- No general performance, Polar winner, cross-domain, or lite-equivalence claim
  follows from this bounded promotion.

---

### 2026-07-26: Formal LDPC v2 remains non-promoted after frozen qualification

**Decision**: Record `ldpc_formal_v2` as `non_promoted`; do not authorize a
real-data lock/run or a frame-identical Cascade/LDPC/Polar comparison.

**Context**: The active `improve-formal-ldpc-v2` change froze nine policies
(rate margins 0/1/2 crossed with `OSD_0/0`, `OSD_CS/1`, `OSD_CS/2`) and a
nested n=64 codebook with selected 32/40/48/56 prefixes. The prior v1
integration root is invalid because its v1 codebook verifier classified all
576 policy outcomes plus 64 associated outcomes as `unsupported_domain`; its
seven artifacts remain immutable with an additive invalid notice. A fresh v2
plan (SHA256 `c0770b5b1c80c277448ca832b01a5dd6d8413df78870fa040c6546d0098ede18`)
had zero old/new CSPRNG overlap and passed strict verification. Development
selected margin 2 with `OSD_0/0` (26/64, 33/64, 56/64 for margins 0, 1, 2,
identical across OSD variants). Confirmation was 28/32 at p=.01 and 29/32 at
p=.02, with seven `verify_failed`, verification invoked on all 64 outcomes,
and zero unclassified/internal/provenance/accounting failures.

**Alternatives considered**:
- Continue tuning against the confirmation outcomes: rejected because the
  confirmation set is frozen evidence, not development data.
- Treat structural codebook screening as qualification: rejected because it is
  only a structural proxy, not verified decoding evidence.
- Proceed to real qualification or three-method comparison: rejected because
  the synthetic promotion gate was not met.

**Consequences**:
- The short- and medium-term engineering tasks are complete with reproducible
  evidence, but LDPC remains below promotion.
- Archive the completed engineering change as explicit non-promotion evidence;
  archiving does not authorize real LDPC qualification or comparison.
- Terra low acted only as the frozen-task implementer/test operator; the main
  thread retained planning and acceptance.

---

### 2026-07-29: Standardize the project-wide agent delivery workflow

**Decision**: Adopt `AGENTS.md` §10.1 as the global default and
`AGENT_HANDOFF.md` as the operator checklist for substantial delegated work.

**Context**: Formal qualification work repeatedly discovered acceptance
requirements late, returned partial subagent status as completion, reran broad
tests after small edits, hit Windows temp ACL failures, and accidentally
entered production decoder paths from tests.

**Consequences**:
- Freeze stable acceptance IDs and feasibility checks before delegation.
- Reuse the nearest accepted predecessor through an explicit delta list.
- Use T0--T3 staged verification and explicit fake runners in test-only paths.
- Use additive Windows workspace roots, process ownership, scoped dirty-tree
  review, and compact delta-only handoffs.
- Preserve all scientific gates, immutable failures, no-rerun/no-tuning rules,
  and main-thread production authorization.

---

### 2026-07-26: Advance binary and nonbinary LDPC as independent parallel lanes

**Decision**: Continue binary LDPC and nonbinary LDPC in parallel, with
separate formal method identities, OpenSpec changes, codebooks, evidence
chains, disclosure accounting, and promotion decisions.

**Context**: `ldpc_formal_v2` is reproducible but non-promoted at 28/32 and
29/32. Its n=64 result points toward longer frames, stronger code families,
incremental redundancy, and bit-plane soft information. The existing
`qldpc_reference` path uses reference-grade matrix construction and hard
syndrome decoding and does not satisfy the formal backend, codebook,
verification, or leakage contracts required of a production-oriented
nonbinary method.

**Alternatives considered**:
- Improve only binary LDPC: rejected because nonbinary symbol-domain coding is
  a scientifically distinct candidate worth evaluating.
- Treat `qldpc_reference` as the formal nonbinary method: rejected because that
  would overstate its implementation and evidence.
- Use one shared qualification pipeline and promotion result: rejected because
  field arithmetic, codebooks, decoder semantics, and leakage decompositions
  differ materially.

**Consequences**:
- Binary and nonbinary work may proceed concurrently through their engineering
  and synthetic-qualification stages.
- The provisional new nonbinary identity is `nbldpc_formal_v1`; the existing
  `qldpc_reference` identity and status remain unchanged.
- Neither lane may reuse existing confirmation evidence for tuning or borrow
  the other lane's promotion.
- A later fair comparison requires independent promotion and frame-identical
  inputs, with disclosure normalized to bits while preserving method-specific
  decomposition.

---

### 2026-07-26: Accept binary long-frame candidate-codebook foundation only

**Decision**: Accept Phase 1 of `binary-ldpc-long-frame-and-ir-v3` as an
offline, candidate-only engineering foundation. Do not select a code family,
wire a decoder, or infer FER or promotion.

**Context**: The additive implementation supports n=256/512/1024, ten planes,
four deterministic candidates, and four nested redundancy prefixes. Canonical
HGF2V3 bytes and a complete 120-candidate manifest bind construction and
structural diagnostics. Main-thread verification passed the focused 4-test
suite, the v2 regression, compilation, and frozen-directory checks.

**Consequences**:
- `ldpc_formal_v2` and its non-promotion evidence remain unchanged.
- Rank, weight, 4-cycle, and `column_pair_extrinsic_degree_v1` values are
  structural proxies, not decoder evidence.
- The next work package must freeze sacrificed-development FER evaluation and
  candidate-selection rules before it reads any development frames.
- Confirmation and real data remain unauthorized.

---

### 2026-07-26: Accept the long-frame development evaluator, not FER evidence

**Decision**: Accept the Phase 2 sacrificed-development evaluator and exact
candidate-selection contract. Do not claim that any candidate or length has
demonstrated FER improvement.

**Context**: The in-memory kernel freezes deterministic p=.01/.02 development
data, pinned BP+OSD-0 parameters, four nested syndrome prefixes, retained
failure statuses, incremental disclosure, and a runtime-independent
lexicographic selection tuple. Main-thread tests independently reconstructed
seed/hash preimages and exercised valid and malformed selection grids.

**Consequences**:
- The evaluator is ready for a separately frozen pinned-backend pilot.
- Injected-decoder tests are contract evidence, not LDPC performance evidence.
- No full development sweep, confirmation, real-data run, candidate
  qualification, or promotion is authorized by Phase 2.

---

### 2026-07-26: Backend pilot clears feasibility, not performance

**Decision**: Use the successful single-slice pinned-backend pilot to proceed
with planning a full sacrificed-development sweep. Do not treat the pilot as
candidate-selection or FER qualification evidence.

**Context**: The one authorized n=256/plane0/candidate0/p=.01 run completed
16/16 exact successes using `ldpc==2.4.1`, mostly at p050, in 0.323 seconds
process time and 1.0 second external wall. It wrote no files.

**Consequences**:
- Backend/API feasibility is no longer the immediate blocker for n=256.
- n=512/1024, other planes/candidates, comparative FER, artifact finalization,
  and verifier cost remain unmeasured.
- A full development sweep requires a new frozen runner/artifact/verifier
  contract before execution.

---

### 2026-07-26: Accept full-development tooling before running the sweep

**Decision**: Accept the Phase 3B runner/verifier implementation and its
test-only evidence. Keep production plan creation and execution as separate
review gates.

**Context**: The tool freezes 3840 ordered outcomes, 30 selections, six
canonical artifacts, a complete hash DAG, failure finalization, no-overwrite,
and strict production/test isolation. Tests cover valid and failed packages
plus semantic tampering after downstream hashes are recomputed.

**Consequences**:
- Tooling is ready to prepare one fresh production plan.
- No candidate FER or selection exists until the production sweep completes
  and the read-only verifier accepts its package.
- Verifier acceptance will still mean artifact integrity and deterministic
  selection reconstruction, not decoder reexecution or promotion.

---

### 2026-07-26: Full per-plane development succeeds but exposes a stopping oracle

**Decision**: Retain the verified 3840-row development package and its
candidate selections, but do not use its per-plane terminal leakage or
100%-success result as formal qualification evidence.

**Context**: Every candidate/length/plane/stratum outcome was an exact
development success. The strict verifier accepted the package and reconstructed
all 30 selections without rerunning decoding. However, the development
evaluator stops each plane by comparing corrected bits directly with Alice.
Bob does not possess that truth oracle in a deployed protocol.

**Consequences**:
- The code-family/backend lane is promising enough to continue.
- Per-plane terminal rounds must be lifted into ten-plane frame-level rounds.
- A formal design should disclose one frame-wide Toeplitz tag and let the
  slowest plane determine each global incremental-redundancy stop.
- Qualification and promotion remain unauthorized until frame-level
  development leakage and stopping semantics are frozen and tested.

---

### 2026-07-26: Select n=256 from frame-level sacrificed development

**Decision**: Freeze n=256 as the next binary LDPC formal-development length.
Do not qualify it until actual frame-wide Toeplitz stopping and formal
transcript/status accounting are implemented.

**Context**: Ten-plane aggregation retained 16/16 successes in both strata for
all three lengths. With one modeled 64-bit tag and slowest-plane global
rounds, n256 had the lowest worst-stratum and overall disclosure fractions:
.68125 and .62265625. The exact selection tuple was
`[-16,-32,.68125,.62265625,256]`.

**Consequences**:
- Candidate IDs selected per n256 plane remain frozen from Phase 3C.
- Formal v3 should use n=256, q=1024, ten planes, and the four global nested
  prefixes.
- Actual Toeplitz tag execution, transcript disclosure, caps and status
  semantics must be implemented before fresh confirmation is planned.
- No promotion follows from sacrificed development.

---

### 2026-07-26: Accept executable binary LDPC v3 before qualification

**Decision**: Accept `ldpc_formal_v3` as the binary lane's formal method
implementation for q=1024/n=256, while withholding qualification and
promotion.

**Context**: The method executes ten frozen Gray bit planes in synchronous
nested-syndrome rounds and uses one locked frame-wide Toeplitz tag only for
global stopping. Tests cover later-round correction and a full-prefix
nullspace error that remains syndrome-consistent through four rounds and ends
`verify_failed`.

**Consequences**:
- Alice truth and verification-tag feedback are not decoder inputs.
- Transcript validation binds round, terminal prefix, incremental syndrome,
  tag, seed, epsilon, backend, calibration and candidate selection.
- Phase 6 must pre-register fresh confirmation, calibration binding, package
  DAG/verifier, gate and stop rules before execution.
- Engineering acceptance does not make the method comparison-eligible.

---

### 2026-07-26: Stop binary LDPC v3 after failed Phase 6 synthetic gate

**Decision**: Retain the strictly verified Phase 6B package as non-promoted
and do not create or execute the real Phase 6C lane.

**Context**: The TTBIN-derived calibration exposed strongly unequal Gray-plane
BER, reaching about .123 on plane 9. Fresh confirmation produced only 3/32
verified successes in the calibrated stratum and 1/32 under 1.25x stress,
against independent 31/32 gates. The remaining 60 frames were classified
`verify_failed`; integrity and accounting failures were zero.

**Consequences**:
- This is an algorithmic/code-channel mismatch, not a packaging/verifier
  failure.
- Real confirmation remains sealed by the synthetic hard gate.
- No confirmation tuning, rerun, real-data execution, or comparison claim is
  allowed.
- A successor requires a new decoder/code-design proposal and fresh synthetic
  confirmation.

---

### 2026-07-26: Pin the nonbinary N0 field contract before decoder selection

**Decision**: Implement the first `nbldpc_formal_v1` slice as a deterministic
internal polynomial-basis GF(2^m) contract for powers-of-two q through 1024,
with canonical field IDs and a read-only fail-closed preflight. Keep
`qldpc_reference` unchanged.

**Context**: The formal nonbinary lane needs an exact field representation and
q=1024 support before a soft-decoder backend or codebook can be evaluated.
The existing reference fallback stops at q=256 and its greedy hard decoder is
not a promotion candidate.

**Alternatives considered**:
- Relabel `qldpc_reference`: rejected because its implementation and evidence
  remain reference-grade.
- Install a large decoder/GF dependency immediately: deferred until a bounded
  N1/N2 contract identifies the smallest backend that satisfies the frozen
  interface.

**Consequences**:
- N0 establishes field-backend feasibility only. It does not establish
  decoder feasibility, qualification, promotion, or performance.
- Unsupported q, non-integral field inputs, field-ID mismatch, and arithmetic
  inconsistency fail closed without backend or lower-q fallback.
- N1 must define deterministic GF(q) codebooks, GF(q) rank, canonical bytes,
  and manifest hashes. N2 must separately freeze soft decoding and formal
  disclosure/Toeplitz accounting before experiments.

---

### 2026-07-26: Freeze the nonbinary N1 structural codebook family

**Decision**: Use a pure in-memory n=64 nonbinary family with one deterministic
32x64 mother matrix and exact 16/24/32 ordered prefixes. Verify rank over the
pinned GF(q), and identify every codebook and ordered family manifest through
canonical `NBLDPC1` bytes and SHA256.

**Context**: The formal lane needs immutable, rate-compatible codebook
identities before any soft decoder can be evaluated. Random reference matrices
and GF(2)/real rank would not provide that evidence.

**Alternatives considered**:
- Random sparse matrices: rejected because their topology and identity would
  not be a stable formal contract.
- PEG search or an external code-design dependency: deferred because the
  deterministic cyclic/protograph-style plus identity construction satisfies
  the bounded N1 structural contract without adding dependency or search
  nondeterminism.

**Consequences**:
- N1 has reproducible GF(q) ranks, prefix relations, canonical bytes, golden
  hashes, and fail-closed tamper verification for q through 1024.
- Structural rank/hash evidence is not decoder feasibility, distance/FER
  performance, qualification, promotion, or comparison evidence.
- N2 must freeze soft decoding and exact public-disclosure/Toeplitz accounting
  before decoder implementation, dependency selection, or experiments.

---

### 2026-07-26: Accept bounded nonbinary FFT-QSPA feasibility only

**Decision**: Use a pure full-message probability-domain FFT-QSPA as the first
bounded `nbldpc_formal_v1` decoder-feasibility implementation. Keep EMS and
min-sum as separately pre-registered alternatives rather than inventing an
unreviewed truncation/tail rule.

**Context**: The q=2^m additive group permits q log(q) Walsh-Hadamard check
convolution, while the pinned N1 matrices require exact nonzero GF(q)
coefficient permutations. The decoder must implement syndrome/coset semantics
without reading Alice truth, and q=1024 must fail closed under explicit
resource bounds.

**Consequences**:
- q=4 coefficient/coset messages agree with brute-force convolution, and a
  bounded q=1024 no-error case executes within the declared memory cap.
- Syndrome consistency remains distinct from locked Toeplitz verification;
  syndrome, tag, and public-control disclosure are separately accounted.
- These are unit-level engineering feasibility results, not general
  correction, FER/performance, calibration, qualification, promotion,
  real-data, production, or comparison evidence.
- N3 may not execute until development/confirmation isolation, claim domain,
  global policy, metrics/gates, resources/stops, artifacts/statuses,
  invalid-run handling, and strict verification are pre-registered.
### 2026-07-26: Nonbinary N3 is non-promoted and strict-verification-unverifiable

**Decision**: Retain the sole `nbldpc_formal_v1` N3 package unchanged as
non-promoted. Do not tune confirmation, rerun, or authorize N4 real-data work.

**Context**: The frozen q=1024 synthetic run selected margin 7, scale 1.0,
max_iter 10 and 32 checks. It achieved 18/32 verified successes at p=.20 and
5/32 at p=.30, below the independent 31/32 gates. The official strict CLI
verifier then failed only because live whole-worktree `git_status_sha256`
drifted post-execution. Source/CLI/contract hashes, commit, Python and NumPy
matched; a diagnostic `_test_only=True` replay checked artifacts/DAG/gates but
does not qualify as official verification.

**Consequences**: The seven artifacts at
`comparison_bench/outputs_comparison/formal_ir_methods/20260726_v1_nbldpc_synthetic`
remain immutable. No promotion, N4, real-data claim, performance comparison,
or confirmation retuning follows.

---

### 2026-07-26: Stop nonbinary LDPC v2 before confirmation

**Decision**: Retain the sole strictly verified `nbldpc_formal_v2` package as
`non_promoted_development`; do not generate confirmation or authorize N4.

**Context**: The selected QC48 tempered+damped policy used margin 8,
max_iter 10, and 32/40 checks for p=.20/.30. Fresh sacrificed development
achieved 0/24 and 5/24 verified successes, below the frozen 22/24 floor in
both strata. The sole execution and full deterministic replay both exited
successfully; scoped provenance passed.

**Consequences**:
- This is development non-readiness, not confirmation failure or FER.
- No confirmation rows/events were generated or executed.
- No rerun, tuning, N4 sidecar adapter, `.ttbin` processing, real-data claim,
  or comparison claim is authorized.

---

### 2026-07-27: Stop binary LDPC v4 at the production development gate

**Decision**: Retain the sole strictly verified
`20260727_v1_binary_ldpc_v4_development` package unchanged and stop before
fresh synthetic preparation. Do not create real qualification evidence,
retune, or rerun this package.

**Context**: The frozen plan executed all 40,960 candidate-plane outcomes and
the read-only verifier reconstructed source, channel, codebooks, selection,
accounting, and readiness without decoder reexecution. Nominal and stress each
had 0/512 frame successes and 5,120 forbidden
`development_decoder_error` plane outcomes, so neither met 495/512.

A subsequent no-decode constructor diagnostic identified a backend-boundary
implementation defect: `ldpc==2.4.1` rejects the NumPy `error_channel` passed
by `ldpc_v4_development.py` and requires a Python list. The formal v4 method
already performs that conversion. Consequently this package is not FER
evidence and cannot support a scientific rejection of the code family.

**Consequences**:
- No production v4 synthetic or real directory, data lock, execution, or
  qualification result exists.
- The immutable package and scoped source hashes remain the audit record.
- Fair Cascade/LDPC/Polar comparison remains blocked.
- Any continuation requires a new main-thread OpenSpec implementation
  correction with a production-constructor regression and newly versioned
  evidence. It must not be represented as a retry or parameter tuning of v4.

---

### 2026-07-27: Accept the versioned v4 backend correction at development

**Decision**: Accept
`20260727_v2_binary_ldpc_v4_development` as strictly verified,
development-ready evidence. Preserve both the failed v1 package and corrected
v2 package unchanged. Do not treat development readiness as qualification.

**Context**: The correction changed only the pinned decoder constructor
boundary from a NumPy float64 array to an equivalent Python list. All matrices,
channel probabilities, deterministic frames, decoder parameters, selection,
accounting, and the 495/512 gates were unchanged. The package achieved 510/512
nominal and 511/512 stress with zero forbidden failures. The read-only verifier
reconstructed predecessor, source, model, codebooks, selection, accounting,
and gates without decoder reexecution.

**Consequences**:
- The confirmed constructor defect is resolved for the versioned development
  path.
- Binary v4 is eligible for a separately reviewed fresh synthetic prepare.
- No synthetic promotion, real-data readiness, FER claim, or fair
  Cascade/LDPC/Polar comparison follows from this decision.
- Do not rerun or tune the immutable development package.

---

### 2026-07-28: Promote corrected binary v4 synthetic; wait for real capacity

**Decision**: Accept the strictly verified corrected-v2 synthetic package as
promoted. Do not prepare real qualification until the registered 128-frame
capacity exists independently in all three real strata.

**Context**: The fresh package achieved 127/128 nominal and 126/128 stress
with zero forbidden failures. Its eight CSPRNG roots and 256 Toeplitz seeds
are unique and disjoint from v3 and development. Read-only verification
reconstructed the full prerequisite/source/method/transcript/outcome/gate DAG
without decoder reexecution.

The current source has 117 complete frames in each of bw120, bw180, and bw200.
The frozen exclusion of 32 v3-reserved identities leaves 85 eligible, a
43-frame deficit against 128.

**Consequences**:
- Binary v4 has passed its independent synthetic qualification.
- Do not reuse v3-reserved real frames or lower the 128/126 gate to fit the
  current capture.
- Obtain traceable same-domain data, preferably at least 64 new complete
  frames per stratum, freeze an extended source manifest, and only then create
  one real lock/plan.
- No real `.ttbin` promotion or Cascade/LDPC/Polar comparison claim exists yet.

---

### 2026-07-28: Accept the v4 real-source intake layer

**Decision**: Accept the frozen source-extension builder, candidate pool, real
lock binding, and read-only reconstruction. Continue to block production real
prepare until a genuinely distinct same-domain acquisition is supplied.

**Context**: The only additional local 20 dB directory has byte-identical
main/chunk `.ttbin` hashes and is therefore a copy, not independent capacity.
The new intake rejects duplicate raw pairs and duplicate 256-symbol payloads,
binds all three q=1024 sidecars and their provenance, ignores rather than pads
natural incomplete tails, and deterministically reconstructs selection without
decoding.

Main-thread acceptance passed 3 source, 5 real, 7 bridge/source, and 25
backend/development/formal-real tests. The first broad regression used a
repository-internal temporary root and retained 8 environment failures; the
same suite passed 25/25 using its required external temp root.

**Consequences**:
- New data can be validated and frozen without modifying the historical v3
  bridge or inspecting real qualification outcomes.
- A copied or re-materialized registered capture supplies zero new capacity.
- Real prepare must bind a reviewed source-extension manifest and remains
  forbidden until all strata have at least 128 eligible frames.
- The next external input is a distinct 20 dB `.ttbin` main/chunk pair with
  traceable bw120/bw180/bw200 sidecars; prefer at least 64 complete frames per
  stratum.

---

### 2026-07-29: Retain the non-promoted 16 dB transfer and pre-register 10 dB

**Decision**: Retain the sole verified 16 dB transfer package as immutable
non-promoted evidence. Do not tune or rerun it. Pre-register one
unchanged-method transfer qualification on the independent 10 dB Type-II
capture.

**Context**: The 16 dB package completed all 384 denominators. bw120 achieved
125/128 against the frozen 126/128 floor; bw180 and bw200 achieved 128/128;
all forbidden counts were zero. Strict verification succeeded without decoder
reexecution or file changes. The 10 dB capture has 1108, 1111, and 1112
complete frames in the same q=1024 bw120/bw180/bw200 processing layers.

**Consequences**:
- The 16 dB and original 20 dB domains remain unpromoted.
- No v4 parameter, matrix, channel, decoder, leakage, cap, or gate changes are
  authorized for the 10 dB transfer.
- The 10 dB package must bind both the promoted synthetic prerequisite and the
  exact non-promoted 16 dB predecessor.
- A promoted result would establish only registered 10 dB transfer, not a
  general real-data or multi-loss claim.

---

### 2026-07-29: Reject 10 dB v1 at prepare review

**Decision**: Do not execute the v1 10 dB plan. Preserve its two files as
immutable `invalid_pre_execute` evidence and permit only a versioned v2
self-exclusion correction.

**Context**: v1 prepare completed without decoding, but strict post-write
validation rediscovered the current plan among prior real plans and therefore
collided with its own roots. This was detected at the required main-thread
review gate before execute.

**Consequences**:
- No 10 dB result has been observed and v1 is not qualification evidence.
- v1 must not be overwritten, deleted, or executed.
- v2 may exclude only its exact current plan SHA during validation.
- v2 must bind v1 and forbid all v1 roots and seeds; all scientific semantics
  remain unchanged.

---

### 2026-07-29: Retain 10 dB v2 non-promotion; develop v5 IR

**Decision**: Retain the strictly verified 10 dB v2 package as non-promoted.
Do not rerun v4 on 10 dB or move through easier losses until a pass appears.
Develop binary LDPC v5 using a pre-locked unused-frame development and
confirmation split.

**Context**: v2 achieved 125/128 at bw120, 127/128 at bw180, and 128/128 at
bw200, with zero forbidden failures. The misses were final Toeplitz
mismatches after complete fixed v4 syndrome decoding. The same fixed policy
also missed 16 dB by one frame, so rate/decoder robustness is the repeated
limitation.

**Consequences**:
- Reserve 512 unused development and 128 sealed confirmation frames per 10 dB
  layer before any v5 decoding.
- Screen only the pre-registered control, stronger OSD, and incremental
  syndrome policies.
- Count all added syndrome/tag disclosure and feedback; a pass with excessive
  leakage remains visible rather than being called free improvement.
- Require a fresh synthetic confirmation before the sealed real attempt.

---

### 2026-07-30: Retain nonbinary LDPC v3 synthetic non-promotion

**Decision**: Retain the sole strictly verified v3 covered-layered synthetic
package as immutable non-promotion evidence. Do not rerun, tune confirmation,
or begin N4/sidecar/`.ttbin` work.

**Context**: The selected layered-l075 margin-8 policy passed development
readiness at 23/24 for p=.20 and 24/24 for p=.30. Its sealed confirmation then
achieved 32/32 and 30/32 with zero prohibited failures. The frozen promotion
floor was 31/32 in each stratum, so p=.30 missed by one frame. The sole strict
read-only replay returned `verified=True`, `run_status=completed`, and
`promoted=False`.

**Consequences**:
- The new codebook and decoder route is implemented and qualified as a
  reproducible synthetic experiment, but is not promoted.
- Confirmation failures remain retained; no post-result parameter search or
  rerun is authorized.
- N4 and real `.ttbin` ingestion remain blocked by the synthetic promotion
  gate and require a new approved OpenSpec change even after promotion.

---

### 2026-07-31: Retain nonbinary LDPC v4 IR synthetic non-promotion

**Decision**: Retain the sole strictly verified v4 incremental-redundancy
package as immutable non-promotion evidence. Stop at A3; do not rerun, tune,
or begin N4/sidecar/`.ttbin` work.

**Context**: Development selected the warm 40→48/32→40 IR policy at 64/64 for
p=.20 and 63/64 for p=.30. Sealed confirmation achieved 128/128 at p=.20 and
120/128 at p=.30. All eight misses were `decode_failed`; there were zero
prohibited failures. The pre-registered gate was exactly 128/128 per stratum.
The sole verifier returned `verified=True`, `run_status=completed`, and
`promoted=False`.

**Consequences**:
- Preserve the complete eight-artifact package without overwrite or rerun.
- One extra eight-symbol syndrome prefix materially improved v3 but did not
  eliminate the p=.30 tail under the frozen decoder and codebook.
- A successor may investigate a stronger pre-registered rate-compatible
  family, additional extension stage, or decoder/codebook redesign only on
  fresh synthetic development data.
- Existing v4 confirmation failures are diagnostic evidence, not tuning data.
  Real-data eligibility remains blocked.

---

### 2026-08-01: Retain nonbinary LDPC v5a Route A synthetic non-promotion

**Decision**: Retain the sole completed v5a multistage-IR package at
`comparison_bench/outputs_comparison/formal_ir_methods/20260731_v5a_nbldpc_multistage_synthetic`
as immutable non-promotion evidence. Do not rerun, tune confirmation, or begin
N4/sidecar/`.ttbin` work. Continue to Route B (task 5.1) as pre-registered.

**Context**: The frozen plan (development seeds 202607720000/730000,
confirmation 202607740000/750000, 128 frames per stratum, caps checks<=56 /
row weight<=8 / stage iterations<=12 / workers 1, probe 202607719999) executed
once: all 512 outcomes completed (`run_status=completed`, `outcome_count=512`).
Readiness passed (both strata >= 63/64) and confirmation material was
atomically materialized and executed. Promotion gates: p=.20 stratum 128/128,
p=.30 stratum 127/128 (one `decode_failed` tail miss), so `promoted=false`
against the frozen 128/128 floor in both strata. Zero prohibited failures.

The pre-registered strict read-only replay was attempted once and could not
run: between plan creation (git HEAD `71bda20d`) and the replay attempt, an
external session committed two unrelated changes (HEAD `3a5d96a`, binary LDPC
v1 sacrificed-development package and a Phase-2 verifier conformity fix;
neither touched any v5a source file). The frozen `_validate_plan` provenance
check therefore rejects the current HEAD. Source/CLI/contract hashes all
still match; only the `git_commit` provenance field drifted. This is an
external interference event, not a package defect; per at-most-once semantics
the strict replay is not rerun.

**Alternatives considered**:
- Reset HEAD to the plan-frozen commit and replay: rejected because it would
  discard another session's committed work.
- Re-run the strict verifier in a temporary worktree: rejected because
  untracked v5a sources and the official output path do not exist there; a
  mirrored environment would not verify the real package.
- Treat the blocked replay as package verification: rejected; the package
  remains "completed but replay-blocked" until a future window with matching
  HEAD re-enables the at-most-once strict replay.

**Consequences**:
- The eight-artifact package is immutable; no rerun or confirmation tuning is
  authorized (no-rerun/no-tuning rules intact).
- Route B (`20260731_v5b_nbldpc_mother_synthetic`, roots 202607760000-
  202607790000) is next; Route A evidence does not establish codebook/decoder
  failure, only failure of the 128/128 promotion floor in the p=.30 tail.
- s6* shift-difference intersection deviation (task 1.3 UNSAT contingency:
  `mask_a ∩ mask6` replaced the full 6-element mask condition; recorded in
  codebook docstring and v5a acceptance evidence) is registered here as a
  formal deviation of the frozen design, not a gate or leakage change.
- Any later strict replay must happen only when the repository HEAD matches
  the plan-frozen commit, and remains an at-most-once action.

---

### 2026-08-01: Retain nonbinary LDPC v5b Route B synthetic non-promotion

**Decision**: Retain the sole completed v5b mother-redesign package at
`comparison_bench/outputs_comparison/formal_ir_methods/20260731_v5b_nbldpc_mother_synthetic`
as immutable non-promotion evidence. Do not rerun or tune. Continue to Route C
(task 6.1) as pre-registered.

**Context**: NBLDPC5B (7 frozen 8-row block templates, disjoint-shift-
difference shift enumeration, salt 0, K=8 proxy candidates with w2=w3=0 —
zero weight-2/weight-3 syndrome collisions over the 56-row mother) ran once:
all 512 outcomes completed (`run_status=completed`, `outcome_count=512`).
Readiness passed in both strata; confirmation material was materialized and
executed. Promotion gates: p=.20 128/128, p=.30 127/128 (one tail miss), so
`promoted=false` against the frozen 128/128 floor. Zero prohibited failures.

The pre-registered strict read-only replay was attempted once and could not
run: between plan creation (git HEAD `3a5d96a`) and the replay attempt an
external session committed an unrelated `ldpc_v5_development` speedup (HEAD
`4dd6b7e`); the frozen `_validate_plan` provenance check therefore rejects
the current HEAD. Source/CLI/contract hashes all still match; only the
`git_commit` provenance field drifted — the same external-interference
pattern already recorded for v5a.

**Alternatives considered**:
- Reset HEAD or drop the external commit: rejected — would discard another
  session's committed work.
- Verify in a temporary worktree: rejected — untracked v5b sources and the
  official output path do not exist there.
- Treat the blocked replay as verification: rejected; the package remains
  "completed but replay-blocked" until a matching-HEAD window re-enables the
  at-most-once strict replay.

**Consequences**:
- The eight-artifact package is immutable; no rerun or confirmation tuning is
  authorized.
- Route C (`20260731_v5c_nbldpc_decoder_synthetic`, roots 202607800000-
  202607830000) is next; codebook identity is fixed to NBLDPC5B (Route B ran
  and is non-promoted).
- A zero-short-weight-codeword mother did not close the p=.30 tail either;
  the remaining lever is the decoder family (damping-schedule FFT-QSPA vs
  truncated EMS), not further codebook search.
- Any later strict replay must happen only when the repository HEAD matches
  the plan-frozen commit, and remains an at-most-once action.

---

### 2026-08-01: Phase 2 speedup refactor and single re-execute approval

**Decision**: Accept the performance refactor of the Phase 2 execute/verify
path (commit `4dd6b7e`) with two formal deviations from the frozen
`phase2-task-packet.md` contract, and approve one fresh prepare/execute/verify
cycle to replace the invalidated official package. The new package
(`20260731_v1_binary_ldpc_v5_development`, plan_sha256
`287d17e825f5bc2a230de7e3b27a77fb99587a91c6057780b5d91d7df7f427d3`) is the
single executed package; the first attempt wrote zero artifacts
(`ValueError: plan frozen equality` — plan binds frozen source hashes and the
source changed under it) and the stale directory was deleted.

**Deviations (semantic-preserving, approved by main thread before re-execute)**:
1. Per-frame loader: `_execute` validates the partition lock once and builds
   rows from `lock["role_rows"]`; per-frame symbols now come from
   `_production_arrays_for_frame` (role membership check + cached
   `build_source_lock()`), replacing per-frame `development_arrays_for_frame`.
2. Verifier: source lock is built once per run instead of per frame; the
   full partition-lock rebuild is skipped for test-injected packages.

**Context**: The unmodified contract cost ~100 s per frame (partition-lock
validation inside the per-frame development loader) and ~0.086 s per frame in
the verifier — an estimated ~130 h wall clock for 4608 frames. The refactor
cut the test suite from 484 s to 97 s (29 passed, 1 skipped), and the official
execute completed in ~4.5 min with per-512-frame progress logs.

**Alternatives considered**:
- Keep the frozen contract and wait ~130 h: rejected as operationally
  unacceptable; speedup is behavior-neutral (verified by
  `test_production_array_loader_matches_locked_source` plus 29-test suite).
- Amend the plan in place: rejected; plans are immutable by design, the only
  legal path is one fresh prepare/execute/verify cycle.

**Consequences**:
- Official package verified once: EXIT=0,
  `{"decoder_reexecution":false,"outcomes":4608,"ready_for_synthetic_prepare":true,"run_status":"completed","selected_candidate_id":"V5-C2","status":"verified"}`.
- V5-C0/C1 are intentionally inactive control candidates (`active=False` in
  `ldpc_v5.py`); their 512x3 `backend_unavailable` rows are expected, not a
  defect.
- The speedup pattern (lock validated once, cached source lock, progress
  logs) is now the normal Phase 3/4 execute/verify path.

---

### 2026-08-01: V5-C2 real-data success promoted — success conditions and robustness boundary

**Decision**: Promote `V5-C2` (round-0 OSD_0/50-iter with H1, strong
OSD_CS/OSD-2/100-iter H1+H2 fallback, 64-bit Toeplitz verification) as the
main flow for binary LDPC v5 incremental redundancy, and proceed to Phase 3
(fresh synthetic confirmation). The promotion is based on verified real-data
success plus a pre-registered robustness argument.

**Context**: The official package verified 1536/1536 V5-C2 frames
(512/512 in bw120, bw180, bw200; fallback invoked 0/1536; SER quantiles
[0.0352, 0.0742, 0.0898, 0.1133, 0.1328, 0.1602, 0.2148]; runtime ~0.133 s;
h1 584 bits/frame). Robustness validation (`workspace/ldpc_v5_robustness/`):
- E1 seed/root independence: 768/768 verified with a fresh root set.
- E3 model-consistent boundary: 768/768 verified at the model's nominal SER
  0.2430 (adjacent +/-1 injected at the frozen calibration probabilities
  plus_one 3865/16384, minus_one 116/16384) — the decoder prior
  (`v5_plane_error_channel` hardcodes `adjacent_nominal`) exactly matches the
  injected distribution there.
- E2 out-of-distribution control: 0/1152 with uniform random symbol
  replacement (structure mismatch vs the +/-1 model) — expected and
  diagnostic, proving the error_channel prior is load-bearing.

**Success-condition analysis**: `plane_error_channel` is Bob-conditioned
(per-position error probability from the frozen calibration table only; it
never sees Alice). Correct decoding therefore requires the real noise to be
adjacent-bin +/-1 errors at rates at or below the frozen nominal table
(SER 0.243). Real frames satisfy this (max SER 0.215 < 0.243), so round-0
corrects everything and the strong fallback never fires. Failure is only
possible under out-of-distribution noise.

**Alternatives considered**:
- Keep C0/C1 as live candidates: rejected; they are intentionally inactive
  controls, not competing decoders.
- Require synthetic confirmation before promotion: deferred; the official
  package itself already gates `ready_for_synthetic_prepare=true`, and Phase 3
  remains the next mandatory gate before sealed real qualification.

**Consequences**:
- V5-C2 is the main v5 flow; Phase 3 synthetic package must still meet
  126/128 nominal and stress with zero forbidden failures before Phase 4.
- The robustness harness (`run_robustness.py`) is retained as reusable
  evidence infrastructure; results in
  `workspace/ldpc_v5_robustness/results.json` (E1/E2) and `results_e1e2.json`
  plus E3 in `results.json`.
- Any future SER-beyond-model evidence must be generated model-consistently
  (adjacent +/-1 at known probabilities); uniform-noise injections are
  recorded as OOD controls, not capability boundaries.

---

### 2026-08-01: Retain nonbinary LDPC v5c Route C synthetic non-promotion

**Decision**: Retain the sole completed v5c decoder-family package at
`comparison_bench/outputs_comparison/formal_ir_methods/20260731_v5c_nbldpc_decoder_synthetic`
as immutable non-promotion evidence. Do not rerun or tune confirmation.
Continue to Route D (task 7.1) as pre-registered.

**Context**: The frozen plan (NBLDPC5B codebook identity fixed at plan freeze
because Route B ran and is non-promoted; dual policies `nbldpc_v5c_sched`
damped FFT-QSPA lambda 0.5/0.75/0.9 per 4-iteration quartile and
`nbldpc_v5c_ems` LLR min-sum nm=64 alpha=0.8; roots 202607800000-
202607830000; 128 frames, 640 development Toeplitz seeds) executed once with
`run_status=completed`. Readiness passed (both strata >= 63/64) and
confirmation material was atomically materialized and executed. Promotion
gates: p=.20 stratum 128/128, p=.30 stratum 127/128 (one retained tail
miss), so `promoted=false` against the frozen 128/128 floor in both strata.
Prohibited failures were zero.

The pre-registered strict read-only replay completed once and returned
`{'verified': True, 'run_status': 'completed', 'promoted': False}`; the
repository worktree status was unchanged by the replay.

**Alternatives considered**:
- Promote on 127/128 in the p=.30 tail: rejected; the frozen floor is 128/128
  in both strata and no-rerun/no-tuning rules remain intact.
- Tune the decoder policies against confirmation outcomes: rejected;
  confirmation is frozen evidence, not tuning data.
- Treat the result as codebook or decoder failure: rejected; it is failure of
  the promotion floor in the p=.30 tail only, the same pattern as v5a and v5b.

**Consequences**:
- The eight-artifact package is immutable; no rerun or confirmation tuning is
  authorized (no-rerun/no-tuning rules intact).
- Route D (`20260731_v5d_nbldpc_post_synthetic`, roots 202607840000-
  202607870000) is next; the pre-registered list-stage + ADMM post stage is
  the remaining lever after codebook redesign (v5b) and decoder-family change
  (v5c) both left the p=.30 tail open.
- The replay succeeded in this window; the strict replay remains an
  at-most-once action.

---

### 2026-08-02: Retain nonbinary LDPC v5d Route D synthetic non-promotion; v5 change terminates

**Decision**: Retain the sole completed v5d post-processing package at
`comparison_bench/outputs_comparison/formal_ir_methods/20260731_v5d_nbldpc_post_synthetic`
as immutable non-promotion evidence. Do not rerun or tune. Per the frozen
rule (task 7.4), with all four routes non-promoted the v5 multistage change
terminates with four immutable non-promoted packages; N4, sidecars,
`.ttbin`, real-data, and comparison claims remain locked.

**Context**: The frozen plan (run ID `20260731_v5d_nbldpc_post_synthetic`,
NBLDPC5B codebook via v5c delegation, dual policies
`nbldpc_v5d_sched_post`/`nbldpc_v5d_ems_post`, roots 202607840000-
202607870000, 128 frames, 640 development Toeplitz seeds, caps and gates
unchanged from the shared v5 contract) executed once with
`run_status=completed` and readiness true; confirmation material was
atomically materialized and executed. Promotion gates: p=.20 128/128,
p=.30 127/128 (one retained confirmation-frame `decode_failed`),
prohibited failures zero, so `promoted=false`. The pre-registered strict
read-only replay completed once and returned
`{'verified': True, 'run_status': 'completed', 'promoted': False}` with an
unchanged worktree.

Implementation corrections were approved and recorded during D1/D2
(module docstring + Verification Notes): the frozen x-update prior-term
sign was wrong (`+ prior/RHO`; correct proximal is `x = z - lambda -
prior/rho`) — a q=4 brute-force experiment showed codeword recovery jump
from ~0% to 87-100% after the fix; and the frozen z-update alternating
projection onto `{per-variable simplex AND output-sum = e_s}` is a strict
subset of the GF(q) check polytope and could not recover codewords — it
was replaced by the per-bit parity-relaxation projection (bitwise-XOR
linearization), which reached 100% exact recovery in the same experiment
(clean and noisy beliefs). A procedural deviation was also recorded: the
7.3 plan was created before the D1/D2 acceptance evidence file; it was
closed read-only at the same HEAD with the plan unchanged.

**Alternatives considered**:
- Promote on 127/128 in the p=.30 tail: rejected; the frozen floor is
  128/128 in both strata and no-rerun/no-tuning rules remain intact.
- Continue Route D tuning (larger list, more ADMM iterations): rejected;
  the list and ADMM bounds are frozen and confirmation is sealed evidence.
- Extend the change with a fifth route: rejected; the pre-registered
  stop rule terminates at four non-promoted routes.

**Consequences**:
- The eight-artifact package is immutable; no rerun or confirmation tuning
  is authorized.
- The v5 multistage change terminates: Routes A, B, C, D are all
  non-promoted with the same p=.30 tail pattern (127/128). Neither codebook
  redesign (B), decoder-family change (C), nor list/ADMM post-processing
  (D) closed the p=.30 tail at the 128/128 floor.
- N4, sidecar access, `.ttbin` processing, real-data qualification, and any
  comparison claim remain locked; a successor requires a new OpenSpec
  change with fresh development and confirmation data.
- The strict replay remains an at-most-once action; any later replay
  requires a matching-HEAD window.

---

### 2026-08-02: Nonbinary v7 R1A canary non-promotion → R1B

**Decision**: R1A (GF(1024) n=256 (2,3) mother, m=170, flooding FFT-QSPA
primary, max_iter 100) sacrificed canary achieved 0/4 verified success in
both strata (8/8 decode_failed at 100 iterations, zero forbidden statuses);
the pre-registered ladder gate fires failed_canary; R1A package frozen
immutably at the workspace canary dir; no rerun/tuning; R1B (one
multiplicative repetition, rate 1/6) is the authorized next route;
development-ready definition (>=15/16 per stratum, zero forbidden, strict
replay, disclosure <=8.75 bits/symbol excluding tag, median <=120 s/frame)
unchanged.

---

### 2026-08-02: Nonbinary v7 R1B canary non-promotion → R2

**Decision**: R1B (one multiplicative repetition of the (2,3) R1A mother,
rate 1/6 nominal, identity nbldpc_formal_v7_r1b_mr1) sacrificed canary
achieved p=.20 3/4 and p=.30 0/4 verified success (5 decode_failed at 100
iterations, zero forbidden statuses); multiplicative repetition improved
p=.20 (vs R1A 0/4) but did not close the p=.30 tail; the pre-registered
ladder gate fires failed_canary (any stratum 0/4); R1B package frozen
immutably; no rerun/tuning; R2 (QSC density-evolution ensemble) is the
authorized next route with its scientific identity requirement (DE must be
independently validated or the route stops implementation_blocked).

---

### 2026-08-02: Nonbinary v7 R2 canary non-promotion → R3

**Decision**: R2 (QSC density-evolution ensemble, identity
nbldpc_formal_v7_r2_qsc_de, DE validated against published BSC/BEC vectors,
per-stratum n=1024 codebooks with 321/458 checks) sacrificed canary achieved
0/4 verified success in both strata (8/8 decode_failed at 100 iterations,
zero forbidden statuses, execute ~21.9 min); the pre-registered ladder gate
fires failed_canary; R2 package frozen immutably at the workspace canary
dir; no rerun/tuning; R3 (GF(32)xGF(32) nonbinary multilevel, EMS nm=32
primary) is the final authorized route; if R3 also fails, the ladder closes
with a non-ready report (V7-40..42).

### 2026-08-02: Nonbinary v7 R3 engineering interrupted — resume state frozen

**Decision**: R3 engineering (identity nbldpc_formal_v7_r3_gf32x2,
reversible 10-bit → high/low 5-bit split, two GF(32) n=1024 codes,
layer-0-first, EMS nm=32 primary, max_iter 100) is PARTIAL on disk:
`formal_ir/nonbinary_v7_r3_codebook.py`, `nonbinary_v7_r3_long.py`, R3
CANARY/DEVELOPMENT configs in `nonbinary_v7_development.py`
(CANARY_R3/DEVELOPMENT_R3), and `tests/test_nonbinary_v7_r3_codebook.py`
exist; missing `tests/test_nonbinary_v7_r3_long.py`, additive harness tests,
T0-T3 runs, and `evidence/v7_r3_engineering_acceptance.json`. The Task tool
intermittently returned empty results or cancelled sessions (memory triage,
coder-fast runs, reviewer-go returns); every completed stage was verified on
disk before acceptance and fresh-session retries succeeded for R1A/R1B/R2.
No R3 plan/execution/official output exists; resume from the frozen partial
inventory (handoff: AGENT_HANDOFF.md current-state section; memory:
AGENT_PROJECT_MEMORY.md §35), then run the R3 canary gate and ladder
closeout (V7-40..42).

---

### 2026-08-04: Nonbinary v7 R3 canary non-promotion — ladder exhausted, closeout

**Decision**: R3 (identity nbldpc_formal_v7_r3_gf32x2, GF(32)xGF(32) two-layer
EMS nm=32 exact min-sum, reversible 10-bit split, layer-0-first conditional
layer-1 priors, m0=m1=404/558, disclosure 4040/5580 bits excluding tag,
3.945/5.449 bits/symbol) engineering was accepted (T0 19/T1 105/T2 33/T3 179,
10/10 independent review PASS); its sacrificed 4+4 canary was staged and
reviewed READY-FOR-SINGLE-EXECUTION, a minimal canary-only authorization edit
was applied, and the canary executed exactly once (exit 0, 668.8 s) and
strict-replayed exactly once (exit 0, 663.4 s) with per-stratum verified
success {0.20: 0, 0.30: 0} (8/8 decode_failed at max_iter=100, layer-0 failed
on every frame, zero forbidden statuses, verification never invoked). The
pre-registered canary gate fires -> failed_canary; R3 package frozen
immutably; no rerun/tuning/confirmation/real data; no official root created.
With R1A, R1B, R2, and R3 all `failed_canary`, no route reached
development-ready: **ladder_exhausted** (report
evidence/v7_ladder_report.md, V7-40 complete). No fourth route is invented;
any successor requires a NEW OpenSpec change with fresh development and
confirmation data, new roots, and its code/rate/decoder change frozen before
new development data; current confirmation rows are not tuning data.
Qualification/promotion/comparison claims remain unauthorized (V7-41/42
pending).

---

### 2026-08-04: Nonbinary V8 starts with reference reproduction, not another canary

**Decision**: Open change
`formal-nonbinary-ldpc-v8-reference-reproduction`. Preserve V7 evidence and
its `ladder_exhausted` result, while narrowing its scientific interpretation:
V7 T0-T3 engineering passed; its route canaries failed. R1B is retained only
as an algorithmic diagnostic because it synthesizes an additional independent
Alice-derived observation outside the project's single-Bob-observation IR
contract. R2's 0/8 applies to its scalar two-level DE surrogate, not to the
paper's full-vector q-ary density evolution. V8 shall implement error-domain
syndrome equivalence, an independent probability-domain oracle, full-vector
QSC MC-DE with edge-perspective degrees and channel terms, and one precisely
sourced published q-ary reproduction. V8 is engineering/reference-only: no
canary, development, confirmation, real/N4/comparison execution or official
output. A separate V9 may be proposed only after V8 acceptance.

---

### 2026-08-04: Nonbinary V8 reference reproduction complete and independently accepted

**Decision**: Accept `formal-nonbinary-ldpc-v8-reference-reproduction` as
implemented and INDEPENDENTLY REVIEWED ACCEPTED (reviewer-go, read-only,
2026-08-04, HEAD `a9c3c5d8696ad9fa967e2d5d8b9905c5a55c8344`). V8-A01..V8-A11
pass; V8-A12 is satisfied by the independent review (the operator did not
self-accept). V8 is engineering/reference-only: it authorizes no FER,
readiness, qualification, promotion, or comparison claim; only a separate V9
proposal follows.

**Context**:
- Additive files only (3 modules + 3 tests + 7 evidence files under
  `openspec/changes/formal-nonbinary-ldpc-v8-reference-reproduction/evidence/`):
  `nonbinary_v8_error_domain.py` (error-domain contract d = H*(x+y),
  reconstruction x_hat = y + e_hat, pure field-tables-only helpers);
  `nonbinary_v8_reference.py` (independent direct probability-domain oracle:
  pairwise XOR convolution + sparse support enumeration + brute-force tiny-code
  coset/MAP, imports only GF2mField, import-boundary test enforced);
  `nonbinary_v8_mcde.py` (full-vector QSC Monte-Carlo density evolution:
  length-q messages, edge-perspective degree distributions with tested
  node/edge conversion, exact sampled degrees, fresh channel message at every
  variable update, direct convolution without FWHT, base-q mean entropy
  convergence, seeded deterministic, fail-closed; golden regressions detect
  old R2 missing-channel and fixed-`dv_max` behavior).
- Tiers (`pytest -q -p no:cacheprovider`, fresh
  `workspace/nbldpc_v8_reference_9c3f51e2a74b48d9b6c0a5f8e1d23a4b` root):
  T0 11/0, T1 31/0, T2 3/0 (read-only reproduction-trace + source-manifest +
  no-production-runner verification), T3 179/0 (frozen 16-file
  v5+v6+v7-R1A/R1B/R2 regression subset, exact frozen file list). The reviewer
  re-ran T0/T1/T2: identical.
- Published reproduction (single frozen run, no rerun/tuning): Muller et al.,
  "Efficient Information Reconciliation for High-Dimensional Quantum Key
  Distribution", Quantum Inf Process 23, 195 (2024), arXiv:2307.02225v2,
  Section 3.1 Table 1 row "0.75": q=4, rate 0.75, DET 0.069, EEff 1.053,
  edge-view lambda with coefficients
  `0.107x+0.245x^3+0.192x^6+0.034x^9+0.207x^18+0.161x^25+0.049x^27`
  (paper Eq. 13: exponents are degree-1, so DE degrees {2,4,7,10,19,26,28});
  concentrated two-point check distribution inferred from the fixed rate:
  dc_mean = 1/((1-R)*sum(lambda_d/d)) = 24.3285893 -> {24,25} (documented
  inference; provenance record `evidence/v8_literature_provenance.json`;
  verbatim extract `evidence/v8_muller2024_table1_extract.txt` SHA256
  `d343f0204e87994e64efd32531bc12490fb4e7125cd90b52cfaf2397279b57bd`). Frozen
  params: seed 2026080418, 20000 nodes, max 200 iterations, entropy
  convergence < 0.01 base-q for 20 consecutive iterations, binary search p in
  [0.01, 0.12] step 0.0025, frozen tolerance 0.015. Result:
  threshold_proxy 0.062421875, delta vs 0.069 = 0.006578 <= 0.015 -> PASS;
  full probe trace in `evidence/v8_reproduction_trace.json`.
- Output policy: no V8 directory under
  `comparison_bench/outputs_comparison/formal_ir_methods/`; no
  canary/development/confirmation/real-data/N4/comparison execution; frozen
  `src/`/`experiments/`/`tools/`/`results/` and all V1-V7 files unchanged
  (git status/diff empty); nothing staged.
- Evidence: `evidence/v8_engineering_acceptance.json` (schema
  v8_engineering_v1; source manifest with SHA256 of the 6 additive files;
  pre-test manifest `evidence/v8_source_manifest.json` re-verified read-only;
  one recorded manifest delta for a test-file assertion addition, all tiers
  re-verified); `evidence/v8_v7_interpretation_audit.md` (R1B =
  out-of-contract extra-observation diagnostic; R2 = unvalidated scalar-DE
  surrogate result; V7 T0-T3 engineering PASS distinct from canary failures);
  `evidence/v8_v9_recommendation.md` (V9 lead: paper-faithful syndrome
  reconciliation with a reproduced ensemble and blind puncturing/shortening,
  fresh roots, separate OpenSpec change; NOT implemented).

**Consequences**:
- V8 is closed; nothing remains for V8 except a future separate V9 proposal.
- No FER, readiness, qualification, promotion, or comparison claim is made
  from V8.

---

### 2026-08-04: Nonbinary V8-60 audit-correction close-out

**Decision**: Record V8-60 as a **non-tuning formula correction** discovered by
an independent audit of the accepted V8 candidate: (a) `concentrated_check_distribution`
previously matched the two-point MEAN check degree (`w_lo = dc_hi - dc_mean`),
which only approximates the edge-perspective rate condition
`sum_j rho_j/j = (1-R)*sum_i lambda_i/i` (relative error ~1e-4); corrected to
solve it exactly for adjacent check degrees `{floor(dc), ceil(dc)}` with
`w_lo = (target - 1/d_hi)/(1/d_lo - 1/d_hi)`, `w_hi = 1 - w_lo`,
`target = (1-R)*integral_lambda`, `dc = 1/target` (integer `dc` degenerates to
the regular degree); new public helper
`reconstructed_rate(lambda_edge, rho_edge) = 1 - (sum rho_j/j)/(sum lambda_i/i)`;
tests assert `|reconstructed_rate - rate| <= 1e-12` (5 configs). (b) The
`REPRODUCTION_CITATION` first author was corrected from the wrong given name
"Rasmus T. Müller" to "Ronny Müller" (full arXiv:2307.02225v2 author list).
(c) The frozen tolerance justification `0.005+0.003+0.0025=0.015` was
arithmetically invalid; replaced by `0.0005` (3-decimal published rounding) +
`0.00125` (p_tol/2) + `0.005` (our MC-DE finite-sample error at 100000 nodes)
+ `0.005` (paper MC-DE error at its 100000 nodes) = `0.01175 <= 0.012`; frozen
tolerance 0.012.

**Context**:
- Corrective reference run (exactly once, parameters frozen BEFORE the run):
  q=4, R=0.75, Muller et al. 2024 Table 1 row 0.75 (DET published 0.069),
  concentrated rho `{24: 0.6623423944, 25: 0.3376576056}` (dc_mean 24.3285893
  unchanged), n_samples 100000 and max_iter 150 (the paper's own MC-DE budget),
  seed 2026080418, p in [0.01,0.12] step 0.0025, entropy < 0.01 base-q for 20
  consecutive iterations. Result: threshold_proxy 0.062421875, delta
  0.006578125 <= 0.012 -> PASS; full probe trace in
  `evidence/v8_reproduction_trace_corrected.json`. No rerun, no tuning.
- History preservation: `evidence/v8_reproduction_trace.json` preserved
  byte-identical (SHA256
  `dd5678fd2d77b67dd7f3fc7ee221a49b0d33eab37ab5d226d96e6d243b071de3`) and
  marked as the pre-correction approximate trace via
  `evidence/v8_reproduction_trace_precorrection_annotation.json`;
  `evidence/v8_engineering_acceptance.json` NOT rewritten (its A12=blocked
  status is explicitly resolved by the new
  `evidence/v8_acceptance_closeout_addendum.json`, main-thread V8-60.10);
  `v8_literature_provenance.json`, `v8_muller2024_table1_extract.txt`,
  `v8_v7_interpretation_audit.md`, `v8_v9_recommendation.md` unchanged.
- Golden regressions: q=4 golden re-recorded under the corrected rho
  `{4: 1/6, 5: 5/6}` (same seed/config; recording not tuning);
  omitted-channel and fixed_max tamper modes still differ (old-R2 detection
  preserved); q=8 golden byte-identical (regular `{6:1.0}`).
- Tiers (V8-60.8 scope, no T3): compile exit 0; T0 17 passed / 0 failed;
  T1 32 passed / 0 failed; T2 4 passed / 0 failed (reproduction-trace +
  source-manifest + no-production-runner + precorrection-preservation, all
  read-only). Independent reviewer-go re-ran T1 32/0 and T2 4/0: identical.
- Independent review (V8-60.9): reviewer-go ACCEPTED the corrected candidate;
  `evidence/v8_independent_review_acceptance.json` written (review scope,
  re-run commands/results, source hashes, V8-A01..A12 conclusions; A12
  resolved pass by this review). Blocking findings: none. Non-blocking:
  `v8_v9_recommendation.md` cites pre-correction run numbers (direction
  unaffected; corrected numbers supersede); cosmetic duplicated REPO_ROOT
  line; pre-existing package `__init__` binding (test scopes correctly).
- Evidence inventory (new in V8-60): `v8_reproduction_trace_corrected.json`,
  `v8_reproduction_trace_precorrection_annotation.json`,
  `v8_60_correction_evidence.json` (formula/constants old->new, tolerance
  arithmetic, source-hash old->new; only `nonbinary_v8_mcde.py` and
  `test_nonbinary_v8_mcde.py` changed: new hashes
  `2c84a5ee76d09f4d6cea537289ff82d88ab19abd31d1a41951a7d24acdd66543` /
  `a508a4228ee06114424db2242b4db784bfa1b9cabcbae54f4cd7172ed988a81f`),
  `v8_independent_review_acceptance.json`, `v8_acceptance_closeout_addendum.json`;
  `v8_source_manifest.json` regenerated with a `v8_60_delta` field (old hashes
  remain in the original acceptance).

**Consequences**:
- V8-60.9 and V8-60.10 are complete; V8-60.11 remains open until the memory
  agent writes AGENT_PROJECT_MEMORY.md section 39.
- The corrected formula, citation, and tolerance supersede the pre-correction
  records; the original evidence remains byte-identical.
- V8 remains engineering/reference-only; no V9 implementation, no
  canary/development/confirmation/real-data/N4, no official output, no
  staging/committing/pushing; only a separate future V9 OpenSpec proposal is
  authorized.
- Nothing remains for V8; the pre-correction evidence stays byte-identical and
  the corrected numbers supersede it.

---

### 2026-08-04: Authorize gated V9 GF(1024) ensemble-to-long-block route

**Decision**: Create OpenSpec change
`formal-nonbinary-ldpc-v9-gf1024-long-ir` and authorize its frozen state
machine V9A -> V9B -> V9C. V9A first validates scalable full-vector GF(1024)
MC-DE and separate p=.20/.30 robust f=1.15 and target f=1.08 ensembles. Robust
multi-seed thresholds must reach .22/.32 before a finite codebook exists.
Passing stages may advance autonomously to n=4096, n=16384, and n=32768
synthetic canary/development; any failed gate freezes evidence and stops.

V8 q=4 validates method/audit machinery only, not GF(1024) threshold or FER.
V9C stops after the n=32768 16+16 development decision. Qualification,
confirmation, real/N4, promotion, and formal comparison remain unauthorized.
Full formulas, resource gates, lifecycle rules, and acceptance IDs V9-A01..
V9-A16 are frozen in the new change and `docs/nonbinary-ldpc-v9-plan.md`.

**Specification correction after independent freeze review**: V9A robust
candidates use conservative .22/.32 gates; target uses .215/.32 (.215 remains
below the p=.20 f=1.08 capacity threshold ~.21827). All four searches
plus multi-seed validation form one reviewed, once-executed, once-replayed
package. n=4096/16384/32768 bind 4/16/32 disjoint constituents respectively;
all finite matrices require `rank(H)=m`. n=32768 canary uses hard 24h timeout
and median <=16h. V9C uses fixed rates only: `m=ceil(f*H_q(p)*n)`, syndrome
`L_recon=10*m`, separate 64-bit tag, `L_total=10*m+64`, with no other
reconciliation payload. Blind adaptation is prohibited in V9 and deferred to
V10.

### 2026-08-04: V9A ensemble gate fails — frozen STOP before codebooks

**Decision**: V9A stops at the ensemble gate. No finite codebook, decoder,
canary, development run, qualification, real/N4 data, promotion, or formal
comparison will be produced under `formal-nonbinary-ldpc-v9-gf1024-long-ir`.

**Context**: V9A executed exactly once under the v2 budget protocol (pid 5084,
3968.5 s, peak RSS 428.3 MiB) and was strict-replayed exactly once (pid 29340,
4838.5 s, peak RSS 451.5 MiB). Scientific outputs are deterministic and
byte-identical between execute and replay; only `run_meta.json` differs in
provenance fields. All four searches (S1 robust p=.20 f=1.15 gate .22; S2
target p=.20 f=1.08 gate .215; S3 robust p=.30 f=1.15 gate .32; S4 target
p=.30 f=1.08 gate .32) recorded zero eligible candidates: every one of the
32 candidate screens at the gate p failed to converge in 150 iterations (final
entropy 0.66-0.93, final error 0.08-0.31). The conservative threshold is
undefined for every gate.

Capacity context (informational only): S1 p*=0.2345, S2 p*=0.2183, S3
p*=0.3527, S4 p*=0.3279. The gates sit below capacity, but the frozen
8-candidate population of 3-term lambda mixtures with harmonic-exact
concentrated rho did not approach it.

**Alternatives considered**:
- Tune the candidate population or expand the search budget: rejected because
  the plan was frozen before any result and a failed execute is immutable.
- Lower the robust gate to match the observed proxies (~0.19-0.20 for S1):
  rejected because that would redefine the frozen gate after seeing the result.
- Advance to V9B anyway with the best non-eligible candidate: rejected because
  the plan requires an eligible/searched winner with a conservative threshold
  before any finite codebook exists.

**Consequences**:
- Evidence is frozen under
  `openspec/changes/formal-nonbinary-ldpc-v9-gf1024-long-ir/evidence/`.
- The replay script's missing guard on the shared
  `evidence/v9a_execute_results.json` path caused an overwrite; the original
  execute version was restored from `v2_execute/evidence_v9a_execute_results.json`.
- V9B/V9C are unreachable. A successor nonbinary LDPC lane would require a new
  OpenSpec change with fresh roots, a different ensemble family, and new
  development/confirmation data.

### 2026-08-05: V9A acceptance and archive complete

**Decision**: The V9A package passed independent review and the change
`formal-nonbinary-ldpc-v9-gf1024-long-ir` was archived (STOP at the ensemble
gate).

**Context**: reviewer-go accepted the V9A evidence package read-only (all
checklist items pass, no blocking issues). Independent SHA256 verification
confirmed 9/11 execute/replay files byte-identical; the 2 differing files
(`evidence_v9a_execute_results.json`, `run_meta.json`) differ only in
provenance fields (pid/start/end/elapsed/peak_rss/command). The official
execute evidence hash matches the v2_execute copy
(`540295123a8a19f3f335f727339df14f4c1106fc01cccab46ecb644dd1eedb8c`).
Acceptance record: `evidence/v9a_independent_review_acceptance.json`.

The generic openspec archive CLI rejected the change (its `verifyChange`
requires numeric `- [ ] 1.1` task IDs and all tasks checked; this project uses
custom `- [x] **V9-XX.Y**` task IDs and V9-30..V9-70 are legitimately
unchecked as unreachable after the frozen STOP). The archive was therefore
performed as the CLI's underlying operation — a dated directory move — exactly
as prior project archives were done.

**Alternatives considered**:
- Rewrite tasks.md to the CLI's numeric format and check all boxes: rejected
  because it would falsify the record (V9B/V9C tasks were never done).
- Run the CLI anyway: rejected because `verifyChange` hard-fails on the
  custom task format and on any pending task.

**Consequences**:
- Change moved to
  `openspec/changes/archive/2026-08-05-formal-nonbinary-ldpc-v9-gf1024-long-ir/`
  (all 6 artifacts: proposal, design, tasks, specs, packet, evidence).
- Delta spec NOT synced into `openspec/specs/` (per user choice: the
  unattained V9B/V9C requirements must not become canonical spec).
- No V9B/V9C artifacts exist; no scientific command was executed during
  close-out or archive.
- Successor nonbinary LDPC work requires a new OpenSpec change with fresh
  roots, a different ensemble family, and new development/confirmation data.

---

### 2026-08-06: Nonbinary V10 fails at the ensemble gate — failed_ensemble, V11 successor

**Decision**: Terminate `formal-nonbinary-ldpc-v10-de-peg-fftqspa` with final
state `failed_ensemble` (`evidence/v10_gate_decision.json`, schema
`v10_gate_decision_v1`). V10A GF(1024) four-search density-evolution ensemble
gate failed (hard stop V10-S02); V10-30 (PEG), V10-40 (FFT-QSPA), V10-50
(canary), and V10-60 (development) are all HALTED. There is no "closest to
gate" candidate, no rerun, and no tuning. The successor is a brand-new V11
NB-SC-LDPC OpenSpec change (fresh everything: new change, new roots, new
development/confirmation data).

**Context**:
- V10-0 q=4 reference-recovery gate PASS: conservative threshold 0.06414,
  |δ| = |0.06414 − 0.069| = 0.00486 ≤ 0.012; main-thread accepted
  2026-08-05.
- V10A searches: S1 (p=.20, f=1.15) conservative 0.2153 < 0.22 FAIL; S2
  (p=.20, f=1.08) conservative 0.1984 < 0.215 FAIL; S3 (p=.30, f=1.15)
  conservative 0.3166 < 0.32 FAIL; S4 (p=.30, f=1.08) no eligible candidate
  FAIL. Triggered hard stop V10-S02.
- Execution record: V10A executed once (~10470 s, peak RSS 335 MB < 3 GiB);
  the first replay attempt was interrupted (PID 21032 died after S1 only);
  per precedent, the replay was rerun in `replay_attempt2/` and completed
  (04:36–07:07Z, RSS 339 MB). Direct byte comparison PASS across 129 files:
  scientific files byte-identical; only provenance normalization differs
  (plan_binding digest key and run_complete role/stage).
- 2026-08-06 protocol amendment (main-thread directive): per AGENTS.md §5.7,
  defensive SHA-256/checksum/integrity-manifest mechanisms were removed
  (plan-bound digest, manifest self/source hash, per-file compare sha256,
  etc.); replacements are git baseline checks, direct byte comparison,
  structured field validation, and semantic recomputation. `v10_seed` is
  retained as a deterministic RNG derivation primitive (DE population
  initialization and mutation RNG streams depend on it; completed results
  depend on its byte reproduction). Amendment record:
  `evidence/v10_protocol_amendment_no_hash_v1.json`.
- Evidence files (change `evidence/`): `v10a_execute_results.json`,
  `v10a_replay_evidence.json`, `v10a_gate_decision.json`,
  `v10_gate_decision.json`, `v10_t3_regression.json` (git baseline PASS,
  frozen directories zero change), `v10_protocol_amendment_no_hash_v1.json`.
- Tests: full V10 suite 89 passed (common 23 / de 24 / gate 13 / peg 12 /
  fftqspa 17).
- Frozen baseline: git HEAD
  `a9c3c5d8696ad9fa967e2d5d8b9905c5a55c8344`; `src/`, `experiments/`,
  `tools/`, `results/` zero change; no new output under
  `comparison_bench/outputs_comparison/formal_ir_methods/`; the 12 tracked
  modifications are pre-existing dirty-worktree entries of other workflows.
- V10-30.DESIGN task (PEG no-hash design note) remains unchecked and is left
  for future V11 inheritance.

**Alternatives considered**:
- Report a "closest to gate" candidate: rejected — the gates are
  pre-registered absolute thresholds; no candidate reached them, and naming a
  closest value would imply partial success or tunability.
- Rerun or tune (expand search budget, adjust population): rejected — the
  failed execution is immutable and no-rerun/no-tuning rules remain intact.
- Advance to V10-30 with the best non-eligible candidate: rejected — the
  hard stop V10-S02 requires all gates to pass before any finite codebook.

**Consequences**:
- V10 terminates at `failed_ensemble`; no codebook, decoder, canary,
  development, qualification, real-data, promotion, or comparison output was
  produced under this change.
- The successor is a new V11 NB-SC-LDPC OpenSpec change with fresh roots,
  fresh development/confirmation data, and its code/rate/decoder change
  frozen before new data; starting V11 is a user decision.
- `v10_seed` remains a deterministic RNG primitive; the other defensive hash
  mechanisms were removed per the 2026-08-06 amendment and must not be
  re-added to new evidence without a new decision.
- V10-30.DESIGN (PEG no-hash design note) is inherited by V11, unchecked.
- S4 delta correction (2026-08-06): `evidence/v10_s4_delta_correction.json`
  (schema `v10_s4_delta_correction_v1`) records that the S4 `delta` field in
  `evidence/v10a_gate_decision.json` was a boolean false from the
  build_evidence short-circuit bug; correct semantics is null. The evidence
  file was not overwritten; the script expression was fixed for future reuse.
  The S4 FAIL verdict and the `failed_ensemble` conclusion are unaffected.
- Independent final review (2026-08-06): reviewer-go ACCEPT recorded in
  `evidence/v10_independent_review_acceptance.json` (schema
  `v10_independent_review_acceptance_v1`; 89 tests pass, covering the S4
  correction record).

---

### 2026-08-06: Freeze V11 as a spatially coupled DE-only successor

**Decision**: Create `formal-nonbinary-ldpc-v11-sc-de-gate` as a plan-only
OpenSpec change. V11 first reproduces published q=4/q=16 QSC coupled and
uncoupled SMP thresholds, then validates a separate full-vector coupled MC-DE,
and finally tests the frozen V10 robust S1/S3 ensembles under equal effective
rate. The only formal geometries are G1 `(w=1,L=32,W=8)`, G2
`(w=2,L=32,W=16)`, and G3 `(w=2,L=32,W=32)`.

**Rationale**: The direct QSC literature supports a spatial-coupling gain but
uses simplified symbol-message passing; BEC/AWGN threshold-saturation results
do not by themselves validate GF(1024) HD-QKD full-vector behavior. A dual
reference gate prevents those claims from being conflated. Equal-rate
termination compensation and paired uncoupled controls isolate coupling from
extra leakage.

**Consequences**:
- Passing requires conservative S1/S3 thresholds of .22/.32 and at least .002
  paired gain in both strata.
- Reference mismatch, resource excess, or no passing geometry stops as
  `failed_reference`, `resource_blocked`, or `failed_coupling` respectively.
- V11 stops at `ready_for_finite_length`; it cannot construct a finite code,
  run FFT-QSPA/canary/real data, or make qualification/promotion claims.
- V11-P04 independent freeze review is required before implementation or any
  scientific execution.

---

### 2026-08-12: Binary LDPC v5 sealed real qualification promoted on real 10 dB ttbin

**Decision**: Accept the sealed real qualification of binary LDPC v5 on the
independent 10 dB Type-II capture: 384/384 verified successes (bw120, bw180,
and bw200 each 128/128) with zero forbidden failures and `promoted=true`.
This is the first real-data promotion for binary LDPC.

**Context**: The full pre-registered chain completed, each stage exactly once
with read-only verification: 20260731 partition lock → 20260731 v5
development (V5-C2, 1536/1536) → 20260801 v5 synthetic (256/256, promoted) →
20260801_v2 real (384/384, promoted). The official ten-file package is
`comparison_bench/outputs_comparison/formal_ir_methods/20260801_v2_binary_ldpc_v5_real/`
(run_id `binary_ldpc_v5_real_qualification_v1`, plan_sha256
`a79cd16f19b968364a4c46fb4887f933eeb472e45c19d098a938ae5dc58ad01b`, report
sha256 `18b5566ed636a79473ff7290cb55d90d4ab20a170895b53f786ea2455ad953d5`).
Report fields: `promoted=true`, `run_status=completed`,
`decoder_reexecution=false`. Execute took ~5m12s and read-only verify ~4m29s,
run in a detached background process on 2026-08-12.

The CSV role uses the frozen encoder's allowed `real` value: the contract's
literal `real_confirmation` is rejected by the encoder, the same precedent as
Phase 3. During implementation, three latent bugs masked by test mocks were
found and fixed (synthetic_dir directory semantics, generator empty-dict
check, missing root_id); the fixes are semantic-preserving and do not change
the scientific result.

**Alternatives considered**:
- None: the qualification is pre-registered and gated; alternatives would
  apply only on a failed gate, which did not occur.

**Consequences**:
- The promotion is limited to the 10 dB Type-II, q=1024, Gray, 256-symbol,
  bw120/bw180/bw200 domain with the V5-C2 strategy. It does not extend to v4,
  the 16 dB/20 dB captures, other acquisitions, nonbinary LDPC, or any
  Cascade/Polar comparison claim.
- v4's two real transfers (16 dB 125/128 and 10 dB v2 125/128, both below the
  126/128 gate) remain retained non-promoted failure evidence; v5 is the
  first all-green real 10 dB Type-II promotion.
- Comparison eligibility is updated: binary LDPC v5 may participate in
  comparison within the promoted 10 dB domain; all other domains and methods
  keep their prior status. Binary/nonbinary parallel status: binary v5
  promoted; the nonbinary lane is unchanged.
- A rate-adaptive successor requires a separate new OpenSpec change.

---

### 2026-08-11: V11 spatial-coupling hypothesis rejected — `failed_coupling`

**Decision**: Terminate `formal-nonbinary-ldpc-v11-sc-de-gate` with final
state `failed_coupling` (`evidence/decision/final_gate_decision.json`, schema
`v11_final_gate_decision_v1`). The V11 spatial-coupling hypothesis is
rejected: none of G1/G2/G3 reached the frozen dual gates (S1 ≥ .22 and S3 ≥
.32), and every paired conservative gain is negative. V11 ends honestly at
`failed_coupling`; no silent promotion is made.

**Context**: Under the frozen V10 S1/S3 lambda distributions and the frozen
G1 `(w=1,L=32,W=8)`, G2 `(w=2,L=32,W=16)`, G3 `(w=2,L=32,W=32)` geometries,
the coupled conservative thresholds were S1 G1 .2100 / G2 .2025 / G3 .2019
(all < .22) and S3 G1 .3125 / G2 .3000 / G3 .3000 (all < .32); paired gains
were all negative (S1 -0.0075 / -0.0144 / -0.0156 and S3 -0.0137 / -0.0256 /
-0.0206). The scientific matrix executed 60/60 runs once (2026-08-08,
execution root `workspace/nbldpc_v11_execute_002d51de/`); the strict replay
was 60/60 byte-identical on science fields from a fresh workspace
(`workspace/nbldpc_v11_replay_8e63bf62/`). Independent final acceptance
(reviewer-go V11-50.3) recomputed 12 conservative aggregates + 6 paired gains
+ 3 gate verdicts, all consistent (16/16 A01-A16 PASS).

**Alternatives considered**:
- Silent promotion or describing a "closest to gate" geometry: rejected —
  the gates are pre-registered absolute thresholds and no silent promotion of
  failures is allowed (design.md §6, A15).
- Retune parameters/ensembles and rerun: rejected — the failed execution is
  immutable and no-rerun/no-tuning rules remain intact.
- Shrink the matrix (drop a geometry/stratum or relax the gates after seeing
  the result): rejected — it would redefine the frozen plan after the result.

**Consequences**:
- V11 stops at `failed_coupling`; the provisional `failed_reference` in the
  execution-root summary was a checks-pending placeholder and is superseded by
  the final decision file.
- No finite code, decoder, canary, development, qualification, promotion, or
  comparison output was produced under this change.
- Finite-length/lifting, windowed FFT-QSPA, decoder, canary, real-data,
  qualification, and promotion work all require a new OpenSpec change with
  fresh roots and fresh development/confirmation data (design.md §6/§8).
- Resource budget (15.83 h < 24 h, peak RSS 2.82 GiB < 3 GiB) and rate
  contract passed; the failure is purely scientific (no threshold gain from
  spatial coupling under the frozen distributions and geometries).

---

### 2026-08-13: V12 nonbinary LDPC real micro-feasibility: source_partition_blocked

**Decision**: V12 terminated with terminal state `source_partition_blocked`. The
four-frame bw200 micro-feasibility canary cannot be executed because the
reconstructed traceable 10 dB pool (2304 rows, 768 per stratum) is 100%
covered by historical frame/payload identities from the V4 10 dB/16 dB
transfer locks (20260729_v1/v2) and V5 development/partition role locks
(20260731_v1): 2848 excluded frame + 2688 excluded payload identities, zero
eligible bw200 rows. Implementation (V12-I01..I05) and engineering acceptance
(V12-T0..T2, 41/41 tests) completed; prepare lane (RP01-RP03) produced the
official package
`comparison_bench/outputs_comparison/formal_ir_methods/20260813_v2_nonbinary_v12_real_micro/`
(v1 intermediate package deleted by explicit user decision). No successor,
rerun, tuning, replacement, or promotion is automatically authorized.

**Context**: V12 asked whether the frozen finite GF(1024) R1 baseline
(unchanged V7 R1A matrix, p=.20 prior, full 170-row syndrome) can produce an
independently verified exact correction on four fresh compatible real frames;
the partition-freeze step found zero collision-free rows in the existing pool.

**Alternatives considered**:
- Reuse historical frames: rejected — cross-history frame/payload exclusion is
  frozen in V12-P05 and design §4.
- Relax the exclusion inventory: rejected — the identities are genuinely
  shared with prior V4/V5 real packages; relaxing would break freshness.
- Fresh acquisition now: deferred — out of V12 scope; requires new capture and
  a new OpenSpec change.

**Consequences**: V12 stands as a documentation + engineering deliverable with
terminal state `source_partition_blocked`; no finite decoder correction was
established for the existing pool; any future canary requires a fresh
acquisition and a new OpenSpec change. Claim boundary: V12 never establishes
success probability, FER, threshold, qualification, or promotion.

---

### 2026-08-14: 先用现有数据诊断非二元 LDPC，不以重新采集为前置

**Decision**: 用户决定先使用现有 10 dB Type-II、q=1024、Gray、256-symbol
数据做非二元 LDPC 的 retrospective diagnostic/development 规划，不把
重新采集设为 V13 的前置条件。V13 change
`formal-nonbinary-ldpc-v13-existing-data-diagnostics` 仅处于
`PLAN DRAFTED / EXECUTION NOT AUTHORIZED`；本轮只请求独立只读 freeze
review，不请求 decoder 或真实数据执行。

**Context**: V12 的 `source_partition_blocked` 是 freshness/identity
partition 失败：已有 10 dB 池中的 768 个 bw200 行均已被 V4/V5 历史
frame/payload identities 覆盖，而不是数据量为零。现有行可用于 channel
统计、接口/数值诊断和事后 exact-correction 检查，但不能被称为 fresh
canary、confirmation、qualification 或 promotion evidence。

**Frozen boundary**: V7 R1A、V10 `failed_ensemble`、V11
`failed_coupling`、V12 `source_partition_blocked` 的含义不改写；binary
V5 同域 384/384 仅作 frame-difficulty/control 参照，不复制其 leakage、
prior 或模型。Alice truth 仅可进入离线 aggregate 与事后 exact check；
公共 telemetry 不保存 raw arrays 或逐位置 error mask。bw200 是 primary，
bw120/bw180 只能在 bw200 根因结论之后做预注册 cross-stratum check。

**Artifact naming**: future diagnostics use the six-file additive package;
`diagnostic_outcomes.csv` contains baseline, candidate-development, and
retrospective-audit rows with explicit `phase` and `method` fields. The
diagnostic CSV name is frozen to `diagnostic_outcomes.csv`.

**Consequences**: P01--P07 只在文档中 drafted，P08 独立 freeze review
尚未完成；所有 D/R/I/E/A/C 均未授权。即使未来诊断全绿，最高状态也
只是 `ready_for_fresh_confirmation`。fresh acquisition、正式
qualification 或 promotion 必须另开 OpenSpec change 并由用户决定；V12
仍保持 `source_partition_blocked`，不重开 X01/X02。

---

### 2026-08-14: V13-D04 baseline probe — 主线程授权、实现并执行一次

**Decision**: 主线程授权执行 V13-D04（unchanged V7 R1A `p=.20` baseline
probe，32 个预注册 bw200 development frames，恰好一次，禁止重试/替换/调
参）。D04 通道实现于 `comparison_bench/`：`run_d04` core lane（含 D04
限定的 manifest authorization、冻结失败包处理）、CLI `d04` action、
只读 verify 扩展、D04-lane 工程测试（DT3，27/27 全绿）。生产执行一次，
run_id `v13_d04_20260814`，六文件包位于
`comparison_bench/outputs_comparison/nonbinary_diagnostics/v13_d04_20260814/`，
严格只读 verify PASS（32 outcome rows、32 telemetry records、ledger ready）。

**Context**: P08 freeze review 已 ACCEPT；DT0-DT2 21/21 通过。D04 结果：
8/32 `syndrome_consistent` + `exact_correct`（全部在第 1 次迭代收敛）、
24/32 `decode_failed` 到 100 次迭代上限、零 `decoder_error`、零
exact_mismatch、零 non-finite/normalisation/underflow 事件。telemetry
观测（经验诊断，非结论）：decode_failed 帧末态后验高度集中（mean
posterior max 0.986、entropy 0.103 bits）但平均 3.79 个 unsatisfied
checks，11/32 帧有振荡迹象。hook 等价性在全部 32 帧保持
（hook_equivalence=ok），V7 R1A 冻结源码字节未改。

**Alternatives considered**: D04 之前是 CLI 硬停止（exit 2）；实现即唯一
路径。输出根写入在沙箱下被拒一次，以 danger-full-access 重试同一命令
成功（用户批准）。

**Consequences**: D04 包 run_state=`plan_only`、`d05_emitted=false`，不产
生任何 diagnosis_class/run_state 结论。D05（根因报告 + 独立复核）仍未
授权、未实现；R/I/E/A/C 全部锁死。8/32 不得被表述为 promotion、
qualification 或 fresh correction。下一授权点是主线程决定是否授权 D05。

---

### 2026-08-14: V13 D01 run 统计 bug 修正 + D04 数据的信道结构观测

**Decision**: 修正 `nonbinary_v13_diagnostics._frame_channel_stats` 的 run
计数 bug（条件表达式在 run-end 检查前把 `run` 清零，导致 D01 记录
`run_count=8` 的伪影）；D01 六文件包保持不可变证据不重写。修正后的同一
128 个 bw200 characterization 帧聚合值记入本条目作为可信参考。

**Corrected aggregates** (read-only recompute, same frames): 2525 个错误符
号；2340 个 run（每帧均值 18.3）；run 长度直方图 {1: 2169, 2: 157, 3: 14}
（最大长度 3）；185 个相邻错误对（7.3% 的错误有相邻错误）——错误是孤立
的单符号扰动，不是突发。**99.3%（2508/2525）的非零 Alice-Bob 差分落在
[0,128)**，与位面失配的 MSB→LSB 单调结构（3.1e-5 → 3.75e-2）一致，并与
binary V5 同域已知的相邻 ±1 符号扰动结构（troubleshooting 中
`plane_error_channel` 的 adjacent_nominal）互证。这些是 D01 邻近的经验观
测，不构成 D05 结论。

**Context**: 主线程层面的 D04 数据预分析（非 D05）：基线双峰行为（8/32
在第 1 次迭代 exact-correct、24/32 迭代上限 decode_failed）、失败帧高置
信错字（posterior max 0.986、entropy 0.103、均值 3.79 unsatisfied
checks、11/32 振荡）与"QSC p=.20 均匀先验严重失配于小差分集中信道"的假
说一致（校准失配 0.1229；模型熵 2.722 vs 经验条件熵 0.547 bits/symbol；
R1A 泄漏 6.64 bits/symbol ≈ 12× 经验下界）。候选排序与文献对照详见本轮
分析答复；正式 diagnosis_class 只能由 D05 发射。

**Consequences**: run 统计 bug 修正只影响未来运行；修正后的聚合值用于
后续文档引用（替代 CURRENT_TASK 中旧 8-run 表述）。信道结构观测不自动
授权 R1 候选——R 阶段仍需 D05 + OpenSpec amendment + 主线程批准。

---

### 2026-08-14: V13-D05 根因报告 — code / diagnosis_complete（含一次无效发射修正）

**Decision**: 主线程按推荐步骤授权 D05 发射。离线 girth 分析显示冻结 V7
R1A 图**结构性退化**：170 个校验节点分成 85 个互不相连的 2-校验组件
（每个组件 3-4 个全 degree-2 变量），check 图 girth=2、Tanner girth=4、
逐组件最小距离 d_min=3。对 32 个 D04 development 帧的结构天花板分析：
structural_failure_fraction=0.75 == 观测失败率 0.75，且**帧级完美对应**
（24/24 失败帧都含 ≥2 错误组件；8/8 exact-correct 帧都不含）。D05 发射
`diagnosis_class=code`、`run_state=diagnosis_complete`、后继 **R3
code-only**；QSC p=.20 先验失配（校准失配 0.1229、|熵差| 2.17 bits）作为
已记录的 co-factor（其不解释观测失败——结构单独解释 100% 失败）。

**Correction**: 首次发射 `v13_d05_20260814` 因决策机制缺陷被判
inconclusive（ceiling 文档缺 observed 分数→默认 1.0；entropy gap 为负而
阈值用了带符号值），按 V8-60 先例：保留原包不可变 + 同级
`v13_d05_20260814_invalid_execution_notice.json` 记录 + 修正后以新 run id
`v13_d05_20260814_corrected` 加法重发一次（决策函数为纯函数，证据字段原
样保留）。严格只读 verifier PASS。

**Context**: 该结论与 V7 合成 canary 0/4+0/4（SER 0.20 ≈ 51 错误/帧 → 每
组件多错）以及 V6/V7 全线 0/N 历史一致；并解释 D04 双峰行为（iter-1 成
功/100 迭代失败）——4-cycle 消息传递的振荡是症状而非独立类别。

**Consequences**: R 阶段仅解锁 **R3 code-only**（prior 与 decoder 接口不
变，只改一个明确的 finite graph/rate 属性：把退化的 85 组件图换成同
n/m/rate/度数、连通、girth≥8 的图）。R1/R2 锁死。R3 候选需 OpenSpec
amendment + 独立复核后方可冻结；E01 门（≥1/64）与 A01 门（≥120/128）不
变。D05 独立只读复核（reviewer-go）为下一科学门。最高状态仍为
`ready_for_fresh_confirmation`，禁止 promoted/qualified/
observed_fresh_correction。

---

### 2026-08-14: V13-D05 独立复核 ACCEPT + R3 候选冻结（amendment）

**Decision**: reviewer-go 独立只读复核（2026-08-14）对修正版 D05 包
`v13_d05_20260814_corrected` 出具 **ACCEPT，零 blocker**：五任务全过
（六文件包 + verifier PASS；图普查 85 组件/girth4/d_min3 独立重算一致；
结构天花板 0.75==0.75、完美对应 24/24+8/8、对抗性逐帧 0 失配；决策表符
合性判断——`mixed` 不成立，因为帧级完美对应是决定性分离：每个失败帧结
构上不可纠（≥2 错误在 d_min=3 组件），每个结构干净帧在（失配的）先验
下也成功，先验解释 0/32 结果；边界扫描干净；无效发射处理正确）。四个
非阻塞警告记录在案（共存分辨率 operationalization、rationale 措辞、
D05 重算聚合的可复现性依赖、real_decode_authorized 语义）。

**R3 amendment (frozen by this entry)**: 唯一候选 = **一个** finite
graph/rate 属性变更——把冻结 R1A 退化图（85 个不相连 2-校验组件，Tanner
girth 4，组件 d_min 3）替换为**连通简单 check 图**（170 校验节点、256
变量边、变量全 degree 2、校验度 168×3+2×4、无平行边、check 图 girth≥4
即 Tanner girth≥8）。构造：确定性种子化随机配对，冻结种子 = 20260818
（>=20260814 中第一个通过 简单/连通/check-girth≥4 门的种子；原型验证
通过）。**不变**：prior（QSC p=.20）、decoder 接口（flooding FFT-QSPA，
与 D03 证明等价的镜像循环）、校验数 170、n=256、rate、max_iter=100、
syndrome/tag 语义、Alice 边界、六文件包契约。新身份
`nbldpc_v13_r3_code_v1`（canonical manifest 含构造种子与 girth 证书）。

**E01 预注册（冻结）**: 64 个 bw200 development 帧 = 按 (frame_id,
frame_identity) 排序的 development 行，跳过前 32（D04），取接下来 64：
[77,78,88,89,92,98,100,102,104,105,106,108,111,113,115,116,117,118,119,
121,123,124,125,127,128,129,134,138,139,140,142,144,145,148,151,153,159,
160,161,163,165,166,168,170,171,172,173,175,177,179,181,184,187,190,193,
194,196,198,208,212,215,216,217,221]。与 D04 的 32 帧及 128 个 audit 帧
互斥。E01 = baseline（unchanged R1A）与 candidate 各执行一次；门：
candidate ≥1/64 independently exact-corrected + syndrome consistency +
post-decode exact check + 零 forbidden/internal/accounting failures；
0/64 → `failed_existing_data_feasibility` 冻结路线。E01 通过 → E02 冻结
候选（禁止继续调参/替换）。A01（候选在 128 个 frame-identical audit 帧
上各一次；≥120/128、零 forbidden、median ≤120 s/frame、disclosure ≤8.75
bits/symbol——170×10/256=6.64 结构性通过）→ A02（bw120/bw180 预注册只读
跨层检查）→ C01。

**Consequences**: R3 候选实现（`comparison_bench/` 内新模块 + E01 通道 +
IT0-IT3 测试）现在开始；E01 前必须 IT0-IT3 全过。所有失败保留；禁止
重试/调参/替换/同义重跑 V7/V10/V11 路线。

---

### 2026-08-14: V13-E01 门通过（candidate 64/64）+ A01 开始

**Decision**: E01 development screen 生产执行一次（run_id
`v13_e01_20260814`，64 个预注册 bw200 development 帧）：R3 候选
`nbldpc_v13_r3_code_v1`（QSC p=.20、flooding、连通 girth-8 图）**64/64
exact_correct**，unchanged V7 R1A 基线 13/64，零 forbidden/internal/
accounting 失败，全部行 syndrome consistency + post-decode exact equality，
严格只读 verifier PASS。E01 门（≥1/64）**通过**；E02 无操作——候选在 R3
amendment 中已预冻结，无调参/替换。这与此前 D05 `code` 诊断完全一致：
把退化的 85 组件图换成同契约的连通图后，在相同先验/解码器下可解码性
剧变。

**A01 预注册（本条目固化）**: candidate-only（baseline 不在 audit 帧上
运行——预先决定）；128 个 frame-identical V5 confirmation 帧
（partition ranks 0..127，bw200，与 D04/E01 development 帧互斥）；门
≥120/128 exact + 零 forbidden + median ≤120 s/frame + disclosure ≤8.75
bits/symbol（170×10/256=6.640625 结构性满足）。通过 → 仅
`ready_for_fresh_confirmation`；未过 → `retrospective_non_ready`。

**Consequences**: A01 生产运行（`v13_a01_20260814`）已启动；其后是 A02
（bw200 通过后预注册只读 bw120/bw180 跨层检查，不提升状态）与 C01
（独立验收 + 记忆 triage + 用户决定 fresh acquisition）。64/64 与任何
后续结果均不构成 promotion/qualification/fresh correction。

---

### 2026-08-14: V13-A01 通过（128/128）→ ready_for_fresh_confirmation；A02 通过

**Decision**: A01 retrospective audit 生产执行一次（run_id
`v13_a01_20260814`，128 个 frame-identical V5 confirmation 帧，candidate
once）：R3 候选 **128/128 exact_correct**（raw SER 0.039–0.113），零
forbidden，median 0.90 s/frame（门 ≤120），disclosure 6.640625（门
≤8.75）。全部 readiness 门通过 → **run_state=`ready_for_fresh_confirmation`**
（V13 冻结计划允许的最高声明状态）。严格只读 verifier PASS。

A02 cross-stratum check 生产执行一次（run_id `v13_a02_20260814`）：
bw120 128/128、bw180 128/128 exact_correct，readiness gate 均满足；
`no_state_promotion=true`（只读检查，不改变 bw200 状态）；verifier PASS。

**Context**: E01（64/64）+ A01（128/128）+ A02（256/256）在同一冻结候选
（连通 girth-8 图 + QSC p=.20 先验 + flooding FFT-QSPA）上的全绿结果与
D05 `code` 诊断闭环：图的连通性/girth 是此前 24/32 失败的根因，替换后
在相同先验/解码器下全部精确纠错。补充观测：candidate 帧耗时 median
~0.9–1.0 s（远低于 120 s 门）；全部帧 syndrome_consistent + post-decode
exact equality。

**Consequences**: V13 的 existing-data 诊断路线达到终态
`ready_for_fresh_confirmation`。**不构成** promotion/qualification/fresh
correction（身份仍为历史复用）。下一步由用户决定：是否另开 OpenSpec
change 做 fresh acquisition（新帧身份）以把该候选提升为 fresh canary/
confirmation/qualification。C01（独立验收 + 记忆 triage）进行中。

---

### 2026-08-14: V13-C01 独立验收 ACCEPT — V13 规划完成

**Decision**: reviewer-go 独立只读验收（2026-08-14）出具 **ACCEPT，零
blocker**：六项任务全过——(1) 五个生产包（D04/D05_corrected/E01/A01/A02）
只读 verifier 全 PASS 且 run_state 与声明集一致；(2) 冻结门全部满足
（E01 candidate 64/64≥1/64、A01 128/128≥120 + median 0.904s≤120 +
disclosure 6.640625≤8.75 + gate_passed==run_state、A02 两层 128/128 +
no_state_promotion）；(3) 预注册纪律（D04=排序前 32、E01=次 64、A01=128
audit，互斥且与 decision-log 冻结清单精确一致）；(4) 声明边界（无
promoted/qualified/observed_fresh_correction、无 raw 数据持久化、纯加法
提交零删除）；(5) 执行授权（outcome 行数精确匹配授权解码集：32/128/128/
256）；(6) 科学一致性（`ready_for_fresh_confirmation` 为 V13 最高状态、
R3 候选独立重算一致：seed 20260818、连通、Tanner girth 8、rank 170）。
三个非阻塞警告记录在案（首版 D05 包的 run_state 标注、D01 bursts_runs
已知 bug 与 D05 修正聚合、A02 跨层 frame_id 复用——身份以
(stratum, frame_id, frame_identity) 三元组为准）。

**Consequences**: V13 冻结规划**全部完成**：P→D→R→I→E→A→C 每阶段按
纪律执行，终态 `ready_for_fresh_confirmation`，七个生产包 + 无效发射
notice 全部保留并提交。记忆 triage 完成（AGENT_PROJECT_MEMORY §47）。
待用户决定的独立事项：① 是否另开 OpenSpec change 做 fresh acquisition
（新帧身份 + prepare/review/execute/verify 链）以推进
confirmation/qualification/promotion；② V12 change 的 archive 决定
（独立 housekeeping）。两者都不由 V13 自动触发。`

---

### 2026-08-14: V14 效率可行性门——计划冻结（freeze review ACCEPT）+ 实现 + 门执行启动

**Decision**: 按调研路线（docs/nonbinary-ldpc-efficiency-roadmap-survey.md）
立项 V14 效率可行性门：在构造任何高码率码之前，用 DE 判定"结构化信道
（V13 characterization 帧经验差分分布）上是否存在 rate≥0.90、f≤1.3 的
非二元 LDPC 系综"。冻结内容：信道模型（λ=1e-3 光滑化、cross-fit 只用
characterization 帧；H(w')=0.5677 bits/symbol）；候选集 3 个 λ
（{2:.25,3:.30,4:.45}/{2:.20,3:.25,5:.55}/{3:.3,4:.7}）× m∈{15,16,17,18}
共 12 点评估（不做 profile 搜索——V11 教训 66.7h）；Stage 0 QSC 回归
（q=4 R=0.75 发表门限 0.069±0.012）；Stage 1 折叠小 q 结构化验证
（φ_m(d)=d mod 2^m）；Stage 2 q=1024 点评估（n_samples=1e4、max_iter
150、熵≤0.01 连续 20 迭代）；预算 3 GiB RSS / 24 h wall / execute-once
+ 严格字节回放；预注册降级链（Li-Fair-Krzymień GA → Cohen 位面分解 →
resource_blocked）。判定规则先冻结：PASS iff Stage 0 通过且存在收敛点
且 f≤1.3；FAIL → 路线冻结为"仅 fresh 确认 V13 R3 现状"。

**Process**: DE 机制由调研子代理定稿（V9 run_mcde 信道块 ~10 行改动
即支持任意 w；q=1024 单点 ~1.18s/500×30 可行、profile 搜索不可行）；
freeze review 首轮 BLOCKERS（spec 候选集与 design 矛盾、Stage 0 锚点
漂移）修复后复评 ACCEPT（三个非阻塞词汇警告已并入）；实现由
opencode-go/deepseek-v4-flash 子代理落实（nonbinary_v14_channel.py、
nonbinary_v14_mcde.py——numba 本地核拷贝 + QSC 模式与 V9 等价 1e-12、
cli/run_v14_gate.py），独立 verifier ACCEPT；测试 13/13 + v13 回归
49/49 = 62/62（gate 修复后 64/64）；V8/V9/V11/V13 源码零改动。

**Correction**: 首启失败——gate 动作对 evidence 目录整体 fail-closed，
而模型文件（model 动作产物、已提交）先存在；修复为按文件 fail-closed
（模型文件属同一冻结证据集，gate 只读校验之；gate 自身 6 个输出文件
任一存在即拒绝，execute-once 不变）。

**Consequences**: 生产门（Stage 0/1/2）已启动（execute-once）。门结果
决定 V15：PASS → V15 高码率候选立项（合成资格 + fresh 实数据需用户
决定采集）；FAIL → 路线冻结声明。门证据落 change 的 evidence/ 目录
（加法、fail-closed）。

---

### 2026-08-15: V14 效率可行性门——gate_state=FAIL，效率路线冻结声明

**Decision**: V14 门生产执行一次（evidence 提交 1cdc63b6），E02 独立
gate review **ACCEPT**：Stage 0 机制回归 PASS（proxy 0.060 vs 发表
0.069，|δ|=0.009≤0.012）；Stage 1 折叠验证全绿；Stage 2 的 12 个冻结
点（3 λ × m∈{15,16,17,18}，q=1024 结构化信道）**全部非收敛**——150
迭代后平均 base-q 熵停在 0.288–0.357（收敛阈 0.01 的 29–36 倍，非
边际失败）；f 值 1.032–1.239 全部满足 f≤1.3，但收敛是绑定判据 →
**gate_state=fail**。预算：wall 87 min ≤ 24 h、peak RSS 577 MiB ≤
3 GiB；严格回放在途。机制经 T2 等价测试（与 V9 1e-12）与 Stage 0
文献回归双重背书，FAIL 不是机制伪影。

**科学解读（规划层，非新结论）**: 四个码率点（R=0.9414–0.9297）全部
低于该信道容量（C≈0.9432 base-q），故非信息论不可能；而是**普通不
规则系综（含 degree-2 的 λ、dc≈51 集中 ρ）在该极端码率上的 BP 阈值
距容量存在结构性缺口**。这与历史一致：V10/V11 在 QSC 上 .22/.32 门
失败是同类"普通系综的 BP 阈限"现象。V13 R3（f≈12.1）仍是唯一经
验证的正确器；fresh-confirmation-only 路线不受影响。

**Consequences（冻结纪律的终态）**: V15（高码率候选）与 V16（部署
适配）**不立项**——其提案/设计骨架保留为"门未过、不立项"状态。V14
禁"最接近"续行与换候选重跑；效率路线的下一步只能由用户决定另开
新 change，候选方向（均需新 DE 门先行）：① 非二元 SC-LDPC（阈值饱和
文献：Zhang 2016；V11 在 QSC 门失败但本结构化信道上耦合增益未测）；
② Cohen 2019 位面分解（与本数据 MSB→LSB 单调失配同构）；③ 多边/
高维 λ 族。V12 archive 与 fresh acquisition 决定仍待用户。

---

### 2026-08-15: 更新目标 P0 收口完成 + P1（fresh acquisition）/ P2（V17 位面门）立项

**Decision（用户更新目标）**: P0 状态收口（纯 housekeeping、无科学
执行）→ P1（立即优先：V13 R3 fresh acquisition）→ P2（独立效率研究：
位面/边标签 DE 门先行）。

**P0 执行（2026-08-15，提交 fb6e579d）**:
- V12 正式归档 →
  `openspec/changes/archive/2026-08-15-formal-nonbinary-ldpc-v12-real-micro-feasibility/`
  （保留 `source_partition_blocked`、X01/X02 未执行、v2 prepare 包；
  归档≠成功、不重开执行；delta spec 未合并——V9/V10 先例）。
- V15/V16 归档为 aborted drafts（未立项/前置门失败；delta spec 未合并；
  aborted_notice.md 记录重启边界：需新 DE 门 PASS）。
- 陈旧文档修复：CURRENT_TASK.md（V14 段降级为历史）、V14 tasks.md
  （头部状态、测试数字、回放完成）、V13 tasks.md（C01 COMPLETE、
  IT0-IT3 49/49）、AGENT_HANDOFF.md（Current State 重写）、记忆
  §47/§48 修订 + §50 新增。
- V14 测试数字统一（原始记录 = decision-log 2026-08-14）：修复前
  13+49=62/62 → 修复后 15+49=**64/64**。
- 本地领先 `origin/main` 28 个提交（收口后 29）；**push 待用户单独
  授权**。

**P1 立项（提交 240e3a2e）**: 新 change
`formal-nonbinary-ldpc-v13-r3-fresh-acquisition`——冻结：新帧/载荷
身份（排除 V4/V5/V12/V13 全部历史锁）、acquisition/window/stratum
（bw200 主）、三角色隔离、R3 码本/先验/迭代上限不变、漂移与无
eligible frame 停止规则、失败原样保留；流程冻结→prepare→review→
单次 execute→只读 verify→fresh-confirmed/frozen failure。数据事实：
2026-08-15 检查 `D:\Data` 无 fresh 帧数据源（最新 2026-07-28 JSI，
非帧数据）→ prepare 预计产出 zero-eligible（合法冻结结果，V12 先例）；
用户提供新数据后 prepare 可确定性重跑（非失败重跑）。

**P2 立项（提交 240e3a2e）**: 新 change
`formal-nonbinary-ldpc-v17-multibit-structured-de-gate`——纯可行性门：
Stage 0 Cohen/多位机制复现 → Stage 1 MSB→LSB 单调失配映射为冻结
多位信道模型（schema v1）→ Stage 2 预注册 3–5 个边标签/位面候选点
评估（复用/扩展 V14 structured 分支）→ 冻结收敛（熵≤0.01×20 迭代）/
f≤1.3/预算（3 GiB/24h）/execute-once+回放 → 一次执行。PASS → 另开
有限码 candidate change；FAIL → 冻结、不启动 V15/V16、不扩大搜索。
排名冻结：①位面/边标签（直接对应当前数据位面不均匀性）；②SC-LDPC
（QSC 负耦合、结构化未否定）；③多边/高维 λ。

**Process**: P0 由主线程完成并本地提交；P1/P2 规划文档由主线程起草，
两个独立 freeze review（opencode-go/deepseek-v4-flash 子代理，只读）
在途；ACCEPT 前禁止 prepare/实现/执行。V13/V14 源码零改动。

**Consequences**: 两个新 change 的 tasks P07 均为独立 freeze review；
review 结果决定是否进入 PREP/实现阶段。push（30 个本地领先提交）
仍待用户单独授权。

---

### 2026-08-16: V17 多位结构化 DE 门——gate_state=mechanism_unverified（FAIL 类），位面/边标签效率路线冻结

**Decision**: V17 生产 gate 执行一次（wall 7026.6 s，peak RSS 541 MB
≤ 3 GiB/24h 预算），strict replay 5/5 字节一致，E02 独立 gate review
**ACCEPT（零 blockers）**。终态 **`mechanism_unverified`**（FAIL 类）：
- **Stage 0 锚点 A（q=4 退化 p1=p2 内部一致性）失败**：
  bit-plane 分解 DE 阈值 0.0525 vs 符号级 QSC DE 阈值 0.0600，
  Δ=0.0075 > 容差 0.005 → `mechanism_verified=false`。方向性成立：
  位面分解在 p=0.055 起 joint 未收敛（熵跃升 0.95），符号级至
  p=0.060 仍收敛（0.0625 才翻转）——同一系综/seed/n_samples=1e5/
  max_iter=150 下位面分解阈值严格低于符号级阈值，Cohen 式
  位面分解机制未在冻结判据内复现。
- **Stage 0 锚点 B（文献交叉）通过**：computed 0.0600 vs published
  0.069，|δ|=0.009 ≤ 0.012（V14 冻结常量逐字一致）。
- **Stage 1 模型构建成功**：V13 D01 只读聚合 → 10 个 MSB-first
  位面误码率（3.05e-5→3.75e-2），product-of-marginals 联合近似
  （显式声明保守假设），熵 0.549955 bits/symbol。
- **Stage 2 诊断（diagnostic_only）**：3 候选（bitplane/edgelabel/
  planeweight）× m∈{15,16,17,18} 全 12 点 **全部未收敛**，
  f_achieved∈[1.065,1.279] 均 < f_limit 1.3 但收敛为绑定判据；
  无 pass_point、无 closest/rerun/调参痕迹。

**科学解读（规划层，非新结论）**: 门冻结发生在机制层而非系综层——
Cohen 2019 多位位面分解机制未通过内部一致性锚点，故 Stage 2 的
12 个诊断点不构成效率结论（仅记录，不引用为证据）。这与 V14
（普通不规则系综在 rate 0.93–0.94 无 BP 收敛点）共同说明：位面/
边标签路线在该冻结判据下不可验证，不进入有限码。

**Consequences（冻结纪律的终态）**: 位面/边标签效率路线按 V17 纪律
**冻结**；不启动 V15/V16、不扩大搜索、无"最接近"续行、无 rerun/
调参。效率路线的下一步只能由用户决定另开新 change（候选方向：
② SC-LDPC——QSC 下负耦合、结构化信道下未否定，仍排第二；
③ 多边/高维 λ 族，排第三；或用户指定的其他方向）。本门无 FER/
资格/效率实测结论；P1（V13 R3 fresh acquisition）独立推进不受
影响，仍阻塞于 fresh 数据（用户提供后重新 prepare 即可）。
证据：change `evidence/` 6 文件（5 科学 + replay 记账）。


### 2026-08-16: V13-R3 fresh 数据准入——2026-01-21 三源判定为 data_intake_rejected

**Decision**: 用户提供的三个 `2026-01-21` Type2 ttbin 源不能作为 V13 R3
fresh-confirmation 数据源。新增 D0 准入证据包
`comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_intake_20260816/intake_decision.json`，
判定 `data_intake_rejected_for_fresh_confirmation`。不进入 P1 prepare/execute/verify。

**Context**: frozen design §1 要求 fresh 数据晚于 V13 历史且为可核验 10 dB
Type-II 帧数据。三个源时间戳为 2026-01-21、损耗元数据缺失；且 folder1 已有
D2 烟测 `raw_ser=0.254663`，远超 V13 D01 参考 0.0771，已触发漂移门。

**Alternatives considered**:
- 按原“v16”规划继续 prepare/execute：拒绝，因数据不 fresh 且烟测已漂移。
- 降级为 legacy drift audit：可另开新 change，但不得使用 fresh-confirmed/
  promotion/qualification 声明。

**Consequences**: P1 保持 `no_eligible_frames` 阻塞态；D1–D5 仅在诊断标签下
可后续执行；真正 fresh 数据到达后重新进入 D1–D5→P1。push 仍待用户单独授权。

### 2026-08-16: V13-R3 fresh 数据准入——D1–D5 诊断执行完成，D5 drift_exceeded

**Decision**: shell 可用后按修正参数执行 D1–D5 诊断，完成三源 sidecar/pairs/manifest 与全量漂移预检。D5 三源全部 `drift_exceeded`，按冻结停止规则自动停止，不进入 P/E/V。

**Context**: D0 已判定 `2026-01-21` 三源 `data_intake_rejected_for_fresh_confirmation`；D1–D5 作为只读诊断仍按修正参数执行，以固定证据并确认漂移幅度。

**Evidence**:
- D1: `workspace/v13r3fresh_20260816/d1_baseline.json`
- D2/D3 sidecars: `workspace/v13r3fresh_20260816/sidecars/<source_tag>/`（`map_sanity.verdict=FAIL`，raw SER ≈0.240–0.256）
- D4 pairs: `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/<source_tag>/pairs.parquet` + `build_manifest.json`
- D5: `workspace/v13r3fresh_20260816/precheck_report.json`，三源 `precheck_state=drift_exceeded`，fail reason 均为 `raw_ser_mean_deviation_exceeded`

**Consequences**: P1 仍保持 `no_eligible_frames` 冻结终态；P/E/V 不进入。真正 fresh 数据到达后重新进入 D1–D5→P1；若用户坚持使用 2026-01-21 数据，另开 legacy drift audit change。push 仍待用户单独授权。

### 2026-08-16: V13-R3 legacy drift audit——用户决定使用 2026-01-21 三源；192 帧 188 exact_correct / 4 decode_failed

**Decision**: 用户明确表示这些是之前采集的数据、纠错算法对具体数据源要求没那么高，要求使用三份 `2026-01-21` Type2 数据继续。按冻结规则不以 fresh-confirmation 进入 P/E/V，另开 change `formal-nonbinary-ldpc-v13-r3-legacy-drift-audit`，claim boundary 仅限 `legacy_drift_audit`。

**Execution（一次）**: 新增最小 execute/verify 工具（8 测试通过）。三源各取前 64 个完整帧（frame_id 0..63，共 192 帧），不变 R3 候选 `nbldpc_v13_r3_code_v1`（p=.20、flooding FFT-QSPA、max_iter=100）每帧解码一次，失败原样保留。

**Result**: 188/192 `exact_correct`；4 帧 `decode_failed`（`iteration_limit`：type2_1M frame 15/20、type2_2M frame 52/56），raw SER 0.230–0.297。三源 raw SER 均值约 0.243–0.255（V13 D01 参考 0.0771）。只读 verify OK。证据包：
`comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3_legacy_drift_audit_20260816/`。

**Consequences**: 本结果仅证明 R3 候选在已知漂移 legacy 数据上 188/192 精确纠错，不构成 fresh-confirmed / promotion / qualification；P1 `no_eligible_frames` 冻结终态不变；P2 V17 `mechanism_unverified` 不变。push 仍待用户单独授权。

### 2026-08-16: V13-R3 legacy drift audit——全量 8412 帧完成，8284 exact_correct / 128 decode_failed

**Decision**: 用户要求继续使用三份 `2026-01-21` legacy 数据；在 192 帧审计后进一步执行全量 8412 帧审计。采用 8 chunk 并行（`--all-frames --chunks 8`），每个 chunk 独立 additive 包，claim boundary 仍仅 `legacy_drift_audit`。

**Result**: 8/8 chunk verify OK；合并全量结果：
- 总帧数：8412
- exact_correct：**8284**
- decode_failed：**128**（均为 iteration_limit）
- exact_mismatch：0
- 分源：1p5M 2729/2767，1M 1970/2000，2M 3585/3645
- raw SER 均值：0.240–0.256（V13 D01 参考 0.0771）

**Evidence**: 合并包 `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3_legacy_drift_audit_full_20260816/` + 8 个 chunk 包。

**Consequences**: 仍不构成 fresh-confirmed / promotion / qualification；P1 `no_eligible_frames` 与 P2 V17 `mechanism_unverified` 均不变。push 待用户单独授权。

### 2026-08-16: V20 scientific reclassification and V21 Bob-only plan

**Decision**: 接受外部审查结论，V20 的 `31/64`、`40/96` 不得标为可执行 FER：
- `31/64` = oracle-aided best-of cascade upper bound；
- `40/96` = top-4 oracle list coverage；
- standalone bounded4 `30/64` = unverified Bob-only estimate；
- V01 = counting-only verifier。
V20 状态改为 `CONCLUDED_PENDING_SCIENTIFIC_CORRECTION_AND_ARCHIVE`，语义修正后
再归档。新建 V21 plan：`docs/nbldpc-v21-bob-only-plan-20260816.md`，只验证
Bob-only 策略 S0/S1/S2，Alice 仅出现在最终指标阶段；停止门 FER≥0.45 则冻结
短块 OSD/top-K 路线，转 V22 结构化构造。

**Context**: V20 cascade 用 `np.array_equal(x_hat, alice)` 决定是否调用
bounded4 以及从 top-K 中选谁；Bob 无法知道 syndrome-consistent 候选是否是
exact mismatch，因此该策略不可执行。n64 最多只剩 5 bits 公开预算，n80 只剩
7 bits，16/32-bit 验证标签会使 f 升到 1.50–2.05，top-K+public hash 不能直接
立项。

**Alternatives considered**:
- 继续扩样 n80 top-K：拒绝，因 oracle coverage 与可执行 FER 混同；
- 直接进入 fresh qualification：拒绝，必须先完成 Bob-only 重分类与验证；
- 直接归档不修语义：拒绝，因会固化错误 FER 标签。

**Consequences**: V20 保持 active 直到 Phase 0 addendum 完成并真正移动到
archive；下一阶段执行 V21 Bob-only 验证；push 仍待用户单独授权。

### 2026-08-16: V21 Bob-only stop gate triggered

**Decision**: V21 Bob-only validation on 64 fresh n=64 frames:
- S0 BP-only: 24/64, FER=0.625
- S1 bounded4-only: 28/64, FER=0.5625
- S2 BP-first-fallback-bounded4: 28/64, FER=0.5625
All >= 0.45, so stop gate is triggered. Short-block OSD/top-K branch is frozen as
`scientific_not_ready`. V20 moved to archive; V22 structured construction drafted.

**Context**: This confirms the external review: Bob-only executable FER is around
0.56-0.63, not the oracle upper bounds 0.5156/0.5.

**Consequences**: No fresh qualification; next phase is V22 DE-gated MET/protograph
or SC-LDPC construction. push still user-gated.

### 2026-08-16: V22 structured DE declared not-ready for target f

**Decision**: V22 structured DE gate at q=1024, rate=0.9375 does not converge
with current SC-LDPC/plain tools even at n_samples=200, max_iter=30,
degree_max=512. V22 is frozen as `scientific_not_ready` pending a MET/protograph
multi-edge DE implementation. No finite-code construction is started.

**Context**: plain structured DE ceiling confirmed; SC-LDPC V10 winners only pass
at low QSC p=0.05, not target rate. degree cap unblocked by V22b but candidates
still non-converged.

**Consequences**: no finite construction, no fresh qualification. Next candidate
is a MET/protograph DE (V23) or acceptance of current not-ready state.

### 2026-08-16: V23 DE not reachable with current ensembles

**Decision**: q=1024, rate=0.9375 structured-channel DE does not converge with
plain irregular, SC-LDPC, regular protograph, or simple irregular protograph
ensembles (entropy floor ~0.19-0.34, tolerance 0.01). V23 status set to
`DE_NOT_REACHABLE`. Further progress requires full DE optimization
(Müller-style) or a different channel decomposition; no finite-code construction
is started.

**Consequences**: f<=1.3 structured high-rate reconciliation is not demonstrated
with current tooling; record as scientific limitation. push still user-gated.

### 2026-08-16: NBLDPC structured high-rate route end (awaiting user direction)

**Decision**: After V19→V23 diagnostics, q=1024 structured f<=1.3 is not
reachable with current ensembles (DE non-convergent; Bob-only FER>=0.45 for
short blocks). No further automatic step is justified without a user decision
among: (a) full structured DE optimization, (b) adjusted target (higher f /
smaller q / channel decomposition), (c) MET multi-edge implementation, or
(d) accept current not-ready state and archive.

**Consequences**: Objective stays active as a blocker; push remains user-gated.

### 2026-08-17: Correct NBLDPC route-wide conclusion and plan bounded V24 successor

**Decision**: Supersede `NBLDPC_ROUTE_BLOCKED` and any route-wide “unreachable”
or “MET failed” wording with `NBLDPC_CURRENT_SINGLE_EDGE_TOOLING_BLOCKED`.
V21 concluded its observed stop gate but lacks pre-freeze and runtime
Alice-injection/V01 verification. V22 is negative only for tested candidates
under the current kernel. V23 reduced base matrices to aggregate single-edge
`lambda/rho` and called V22b; it did not implement topology-preserving
protograph DE or MET DE. Its raw scan contains three matrices, while additional
consolidated points lack independent raw/verify packages.

**Context**: The 2026-08-16 closeout wording overreached the actual evidence and
collapsed engineering tests, scientific verification, candidate coverage, and
unimplemented MET into one route-wide conclusion.

**Consequences**:
- V21, V22, and V23 are respectively
  `CONCLUDED_STOP_GATE_TRIGGERED_PENDING_ARCHIVE`,
  `CONCLUDED_CURRENT_KERNEL_NEGATIVE_PENDING_ARCHIVE`, and
  `CONCLUDED_SINGLE_EDGE_DIAGNOSTIC_PENDING_ARCHIVE`.
- This round performs documentation/planning only; no code, DE/FER execution,
  scientific output, archive movement, or push.
- Actual archive order is V21 -> V22 -> V23 only after independent read-only
  closeout ACCEPT and explicit user authorization.
- V24 is frozen pending P07 user authorization for bounded q=1024 V17
  structured single-edge optimization.
  DE PASS precedes any finite-code proposal. True MET is untested and can only
  become a separate user-authorized change after V24 FAIL.

**Freeze-review addendum**: V24 P06 independent read-only review returned
ACCEPT on 2026-08-17 after the frozen V8-trace reuse, deterministic indexed
generator, ranking/error semantics, and resource-stop contract were made
unambiguous. P01–P06 are complete. P07 user authorization remains required
before implementation or scientific execution.

---

## 2026-08-18 — V24 archived predecessor + engineering + gate launch

**Context**: The current objective granted P07 (implement + scientific
execution) and asked to formally archive V21->V22->V23 first.

**Decisions**:
- V21/V22/V23 archives moved:
  `openspec/changes/archive/2026-08-18-*` with archive notes. Archive direction
  V21 -> V22 -> V23 preserved.
- V24 engineering (I01-I11) implemented and all 21 focused tests pass
  (T0/T1/T2/T3). No frozen predecessor source modified.
- Pre-registered M0-M2 scientific gate launched in background with a 24 h
  completed-DE-call resource ceiling; M0 mechanism gate passed.

**Observed**:
- Proposal sparsity: 135 unique valid in-band candidates across the 8192
  attempt ceiling.
- Screen DE calls non-converged (final base-q entropy ~0.3), consistent with
  the V22/V23 single-edge negative diagnostics.
- Evidence root:
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v24_20260818/run_20260818T135145_prod/`.

**Pending**: gate completion (~7 h) and independent verifier; terminal state
(pass/fail/resource_blocked) recorded in M3. No finite code/FER/qualification/
promotion before a DE PASS, and no push.

---

## 2026-08-18 — V24 M0-M2 gate result: FAIL (bounded single-edge route closed)

**Gate**: pre-registered V24 M0-M2 scientific gate completed in background
(314 DE calls, 4.87 h accumulated completed-DE-call time, well under the 24 h
ceiling; 0 errors; 0 converged).

**Result**:
- M0 mechanism/accounting gate: PASS.
- 135 unique valid candidates found in 8192 attempts (search band
  R in [0.9375, 0.94140625]).
- Screen (270 calls): 0/135 converged; entropy floor ~0.20-0.32.
- Refine (24 calls): 0/8 converged; entropy ~0.29-0.30.
- Holdout (20 calls, 4 pre-declared finalists x 5 seeds): 0 finalists converged
  on all five seeds (final base-q entropy ~0.29-0.30).
- Terminal state: **`fail`** = `single_edge_bounded_optimization_failed`.

**Interpretation**: The bounded single-edge `lambda/rho` optimization over the
frozen V17 q=1024 structured channel at target f<=1.3 found no DE-convergent
candidate. This is an asymptotic ensemble result only (VA09/VA10): no
finite-code, FER, qualification, promotion, or MET claim is made.

**Successor rule**: true MET/multi-edge DE is only a new user-authorized
change candidate; adjusting q / channel decomposition / f target is a separate
user decision. No automatic fallback runs. No push was performed.

**Evidence**: `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v24_20260818/run_20260818T135145_prod/`
(read-only verifier: ok=True, recomputed terminal fail).

---

## 2026-08-18 — V25 M0-M4 complete: pass_ready_for_de_change

**Context**: main-thread freeze decision accepted the +-1 empirical regularity as a
source/delay-conditioned channel (not alignment blocker); P102 ACCEPT; M0-M4 authorized.

**Result**:
- Empirical timestamp channel: H(A|B) ~ 0.80 bits; errors ~ {-1,0,+1} adjacent bins;
  direction flips with delay_used_ps sign (-50 -> +1, +50 -> -1), stable over time.
- M1: empirical delta conditional models (C03/C04/C05) beat QSC (3.20-3.35) and V17
  independent-plane product (3.32-3.50) on every source's holdout (NLL 0.81-0.83).
- M3: chain-rule closure error <= 5e-9 across F01-F05 x {natural, Gray}.
- M4: high-field candidate F01/GF512(+GF2), mid-field control F03/GF32(+GF32) for V26;
  terminal state = pass_ready_for_de_change.
- Evidence root: comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/
- Read-only verifier ok=true.

**Successor**: V26 small-scale channel-informed DE is a NEW change requiring explicit user
authorization; V25 PASS only proposes V26 and does not auto-start it. No finite code / FER /
MET / fresh qualification / public residual / Alice-oracle; no push.

## 2026-08-19 — V26 channel-informed multilevel DE gate: RUN_COMPLETE pass_target_f13 (+ closeout fixes)

**Context**: V25 (pass_ready_for_de_change) proposed two preselected exploration points —
high-field F01 GF512+GF2 (A01) and mid-field F03 GF32+GF32 (A02). V26 ran a small-scale
channel-informed multilevel MC-DE gate on them at f in {1.3,1.6,2.0}.

**Result**:
- M0 adapter semantic gate + M1 mechanism tests all pass; A02 f=1.3 converges on all
  2 layer x 3 source x 5 confirm-seed (30/30), final mean entropy 0.00000 bits/symbol.
  A01 f=1.3 fails on the GF2 residual layer, passes at f=1.6. Terminal = pass_target_f13.
- Independent read-only verifier recomputes 72 screen + 60 confirmation + A02@f=1.3 30/30
  + rate/rho/seed/entropy/terminal; run_01 and run_02 both 0 mismatch, ok=true.
- Fixed definitions: f_i = leak_i / H_i with leak_i = (1 - R_i) log2(q_i) and
  R_i = 1 - f_i H_i / log2(q_i) throughout proposal/design/spec/report/code/v27 planning.
- Corrected weak M1 references: iteration-0 test now genuinely enters the MC-DE first round
  (record_channel_entropy); GF2 BSC reference now clearly decides pass/fail (noiseless must
  converge; feasible-rate must converge; at-capacity must fail) instead of "both non-converge
  = agree".
- Implemented the declared 24h completed-call resource gate (RESOURCE_LIMIT_SECONDS) in
  run_screen/run_confirmation + resource_blocked terminal state; not triggered in V26.
- Added explicit source<->delay metadata (SOURCE_METADATA: 1M/1p5M/2M -> delay_used_ps
  -50/+50/+50, n_pairs 512000/708352/933120) into ChannelAdapter, M0 detail, RUN_MANIFEST.
- Run roles: run_02 = canonical, run_01 = deterministic_repeat (RUN_MANIFEST/README).

**Consequences**:
- pass_target_f13 only authorizes proposing A02 (F03 GF32+GF32) finite-code/construction
  change; still no FER/qualification/promotion/MET claim.
- V27 is a NEW change (finite-leakage-margin DE gate) to be written as OpenSpec and returned
  to main-thread freeze review; it is NOT auto-executed here.
- V26 archived locally; no push.

---

## 2026-08-19 — V27 scope freeze (OpenSpec only, no execution)

**Decision**: Create V27 as a *finite-leakage-margin* DE gate OpenSpec, four-part
(proposal/design/tasks/spec delta), frozen parameters: architecture fixed to F03 GF32+GF32;
source/delay-conditioned empirical posterior; Bob-full sequential decoding semantics;
lambda={2:1}; forbid degree search/MET/finite FER; n in {1024,2048,4096,8192}; 64-bit public
verification tag counted in total leakage; integer m_total per n with total f <= 1.3;
test only entropy-proportional m1/m2 and m1+/-1/m1+/-2; screen seeds 27001-27002,
confirmation seeds 27101-27105; terminal states pass_finite_budget_ready /
de_pass_no_finite_headroom / fixed_ensemble_margin_fail. After writing the four parts, return
to the main thread for freeze review; do NOT execute V27.


---

## 2026-08-20 — V27 finite-leakage-margin gate PASS (pass_finite_budget_ready)

**Decision**: V27 executed once (additive run root; V26 MC-DE kernel reused via thin wrapper,
not copied/rewritten) and reached terminal `pass_finite_budget_ready` with passing_block_len=1024;
all four block_lens (1024/2048/4096/8192) confirmed all three sources (1M/1p5M/2M) at the m1_ep
offset-0 candidate.

**Context**: Phase B required minimal budget planner + V26 MC-DE adapter wrapper, T0/T1,
independent candidate-delivery review, one-shot screen+ranked-confirmation, read-only verifier,
evidence preservation, local commit (no push). Independent review run in-conversation (subagent
infrastructure unavailable; user authorized in-conversation review, not gated on subagent).

**Alternatives considered**:
- Reuse V26 DE gate kernel directly: rejected — V27 needs source-adaptive budget + 5-candidate
  ranking + four terminal states; V26 kernel reused only via thin wrapper.
- Simulate finite-code error propagation: rejected — V27 is asymptotic true-predecessor-
  conditioned multistage DE; 64-bit tag only in total block leakage.

**Consequences**:
- `pass_finite_budget_ready` authorizes entering Phase C (V28 GF32xGF32 finite-code engineering)
  and Phase D (V29 retrospective finite-code gate). Stop before fresh qualification.
- Critical bug found/fixed during candidate-delivery review: `run_v27_gate` collapsed 5
  candidates per (source,block_len) to 1 via `candidates[(bl,src)]=cand`; fixed to 3-tuple key
  `(block_len, source, m1)`. Manifest `frozen_config_sha_binding` misclaim removed (no SHA was
  computed). Read-only verifier ok=true (recomputed terminal == persisted).
- Evidence: comparison_bench/outputs_comparison/nonbinary_diagnostics/
  nbldpc_v27r_finite_leakage_margin/run_01/ (frozen_config, screen/confirm checkpoints+results,
  ranking, gate, RUN_MANIFEST, EXECUTION_WALLCLOCK_S=322.9s). No push.


---

## 2026-08-20 — V28 OpenSpec frozen + freeze review ACCEPT (Phase C)

**Decision**: Freeze the V28 GF32xGF32 finite-code engineering OpenSpec and ACCEPT its
independent freeze review (in-conversation; subagent unavailable). V28 reuses existing
`GF2mField.create(32)` (pinned poly 0b100101), `nonbinary_codebook` three-shift-cyclic GF(32)
mother-matrix construction + `gf_rank`, and `nonbinary_qspa.decode_nonbinary_fft_qspa`
(GF(32) FFT-QSPA). No new field/decoder science.

**Context**: V27 reached `pass_finite_budget_ready` at block_len=1024; V28 must materialize
that split `(m1=6, m2 in {194,200,202}, R1, R2)` as real GF(32) parity-check matrices + a
Bob-only sequential decoder so V29 can run the retrospective finite-code gate on frozen V25
holdout.

**Alternatives considered**:
- New GF(32) field/decoder: rejected — pinned `GF2mField` and FFT-QSPA already exist and are
  verified; V28 is engineering, not new science.
- Re-run DE to re-pick parameters: rejected — V27 already fixed the split; V28 must not
  re-optimize (forbidden re-tuning).

**Consequences**:
- Leakage = m_total*5 + 64 bits; f = leak/(n*H_source) < 1.3 for all three sources
  (1.29715 / 1.29409 / 1.29495), consistent with V27.
- Terminal state only `engineering_ready_for_retrospective_gate`; no FER/qualification/
  promotion in V28. V29 follows on frozen holdout. No push.


---

## 2026-08-20 — V28 implementation complete + acceptance ACCEPT (Phase C)

**Decision**: Implement V28 GF32xGF32 finite-code engineering and ACCEPT its independent
main-thread acceptance review. V28 reuses `GF2mField.create(32)`, the `nonbinary_codebook`
three-shift-cyclic GF(32) mother-matrix construction + `gf_rank`, and `nonbinary_v10_fftqspa.
decode_error_domain` (GF(32) FFT-QSPA, Bob-only). No new field/decoder science.

**Context**: V27 selected (block_len=1024, m1=6 shared, m2 in {194,200,202}). V28 materializes
that split as real GF(32) parity-check matrices + two-layer sequential decode so V29 can run
the retrospective finite-code gate on frozen V25 holdout.

**Alternatives considered**:
- Use `decode_nonbinary_fft_qspa`: rejected — it internally enforces the N1 n=64 family and
  rejects V28's n=1024 matrices; the lower-level `decode_error_domain` is the correct reuse.
- New GF(32) decoder: rejected — the pinned FFT-QSPA already exists and is verified.

**Consequences**:
- Structural + noiseless decode verified (both layers, all 3 sources recover x exactly);
  controlled-error is fail-closed (never a false success). 11 T0/T1 tests pass.
- Honest finding: the V27 split is a sparse high-rate code; under uniform QSC prior, iterative
  error correction is limited (decoder reports `converged_no_syndrome`). The limiter is the
  split, not the decoder (proven on m=32/n=64 proper code). V29 measures real FER.
- Terminal state only `engineering_ready_for_retrospective_gate`; no FER/qualification/promotion.
  Evidence: `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v28_gf32_finite_code/
  run_01/` (v28_config, v28_evidence, gate, RUN_MANIFEST, verify). Local commit, no push.

## 2026-08-20 — V29 finite-gate FAIL; V30 projective-safe successor drafted

**Decision**: Close V29 with canonical run_02 as a user-authorized
irreversible-threshold failure. It contains 9 persisted 1M blocks, exact/tag
count 1, 8 failures, and maximum possible 92/100<95. The terminal is
`v29_finite_gate_fail`; `readonly_verify.json` is `ok=true` and the FER is
observed-prefix-only. Retain run_01 as superseded 0-call
`implementation_blocked`; do not rerun or tune V29.

**Context**: The V28R finite graph audit found 15 L1 support groups, maximum
group multiplicity 69, 303 duplicate projective classes, 922 columns in
duplicate classes, and 1107 guaranteed proportional-column/weight-2 pairs.
Thus this particular finite matrix has `d_min<=2`.

**Decision boundary**: This is a V28R finite matrix-construction defect, not a
closure of the channel-informed GF32×GF32 route. The original V28 ACCEPT is
superseded by V28R engineering evidence and does not claim FER.

**Historical pre-P103 state**: The original V30
`formal-nonbinary-ldpc-v30-projective-safe-finite-graph-gate`
`FROZEN_P102_ACCEPTED` state was superseded by V30R
`DRAFT_PENDING_P103_FREEZE_REVIEW`; implementation/execution was blocked at
that time, and no DE, matrix construction, validation block, or decoder call
had started. The later P103 ACCEPT entry at the top records the current
`FROZEN_P103_ACCEPTED` state and authorization boundary. V31 fresh
time-separated qualification follows only after V30 PASS; V32 integration
follows V31.

## 2026-08-20 — V30R bounded cycle-cancellation revision (historical pre-P103 state)

**Decision**: Supersede the original V30 `P102 ACCEPTED` packet with a V30R
revision before implementation or execution. At the time of this entry, the
state was `DRAFT_PENDING_P103_FREEZE_REVIEW` and P103 was the only release
gate; the later P103 ACCEPT entry records the current state.

**Frozen packet semantics**:
- Each selected allocation may produce at most one
  `balanced-projective` packet and one `PEG-projective-cycle-cancelled` packet;
  with at most two selected allocations, the global packet cap is four.
- M1 marks a failed allocation ineligible only after all 12 registered calls
  are persisted. Only a global terminal may interrupt the registered calls.
- M3 screens fixed blocks `0..19` for every registered packet. A screen failure
  removes only that packet. After the complete screen, only the single
  top-ranked eligible packet runs fixed confirmation blocks `20..69`; its
  failure is global `finite_graph_fail` and no fallback packet runs.

**Bounded graph/label rule**:
- A duplicate projective key/proportional column is the 4-cycle FRC failure and
  must be zero. Ordinary 4-cycles are allowed and only counted for topology or
  ranking.
- For each column, reject duplicate-key labels first; among remaining fixed
  `nonzero_cycle` candidates, compute exact newly closed degenerate Tanner-6
  cycles and choose minimal `(degenerate_6_new, ratio_index)`. Nonzero counts
  are allowed and retained as aggregate evidence.
- Tanner-8 is topology/girth diagnostics only. No all-4/6/8 FRC catalog,
  random label search, or candidate rejection list is required. Standard
  variable-side ACE is not used because `d_v=2`.

**Consequences**: V30R retains the V25/V26 channel and V27/V29 leakage/data
boundaries, but narrows cycle cancellation to an executable,
literature-aligned bounded rule. No code, DE, finite decoding, scientific
output, archive, commit, or push is authorized before P103 ACCEPT.

**V30R input binding**: V25 authority is
`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/data_inventory.json`
plus
`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`;
V26 canonical is
`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v26_20260818/run_02/`
(manifest/M0/verify); V28R canonical is
`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v28_gf32_finite_code/run_02_v28r/`
(config/evidence/manifest/verify).
The source IDs/delays are `type2_1M_20260121_184040/-50 ps/1M`,
`type2_1p5M_20260121_183806/+50 ps/1p5M`, and
`type2_2M_20260121_183657/+50 ps/2M`, with matching
`v13r3fresh_pairs_20260816/<source_id>/pairs.parquet` paths. The field is
`GF2mField.create(32)` with `0b100101`, V28R field_id
`c3a3660aa3cfbf788568cf366ee5de345ddc6be0372154a702c9e244a53bc6cf`, and
zero-based `ratio_index`.

**V30R deterministic graph binding**: balanced uses columns in order and
lexicographic supports minimizing
`(occupancy_after,max_check_degree_after,sumsq_after,a,b)`. PEG uses the prior
support check-multigraph edge distance `d_check(a,b)`, defines Tanner path
length `d(a,b)=2*d_check(a,b)`, and minimizes
`(component_flag,distance_cost,max_check_degree_after,sumsq_after,a,b)` with
local Tanner score `d+2`; projective uniqueness is label-stage-only. Tanner-6
counts contain only the current column and use the canonical tuple
`min((j,a,k1,c,k2,b),(j,b,k2,c,k1,a))`; L1 and each L2 source use independent
state. M1 is 72 screen plus at most 60 confirmation calls, with complete 30-call
confirmation for each selected allocation and allocation-local failure.

---

### 2026-08-21: V31 deterministic finite-graph redesign — ARCHIVED_PARTIAL closeout audit addendum (Change A, A10)

**Decision**: Close V31 as `ARCHIVED_PARTIAL` via additive closeout audit addendum `docs/nbldpc-v31-closeout-audit-addendum-20260821.md`. The authoritative evidence is additive `run_02` (`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v31_20260820/run_02/`); `run_01` (`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v31_20260820/run_01/`) is preserved byte-identical but superseded for all lifecycle and interpretation claims. No V31 rerun, reseeding, or graph tuning is performed.

**Context — why ARCHIVED_PARTIAL**: V31 executed n=1024 complete (300/300 blocks: 100 per source 1M/1p5M/2M) and reached `finite_graph_fail` (exact 0/300, tag 0/300, syndrome 0.00, L2 always `converged_no_syndrome`, zero false accepts). n=2048 executed only 14 blocks from 1M (1p5M/2M not executed). Therefore:

```
V31: ARCHIVED_PARTIAL
n=1024: 300/300, finite_graph_fail
n=2048: 14 blocks from 1M only
original both-n execution: incomplete
global PASS under original contract: impossible
bounded-prefix contingency: post hoc
```

A global PASS under the original both-n (n=1024 + n=2048) contract was impossible once the complete n=1024 failure was observed.

**Post-hoc submission timing**: The original submission closed on a `finite_graph_fail` terminal without distinguishing the bounded-prefix nature. The independent audit on 2026-08-21 identified that the 1M 14-block n=2048 prefix was not a pre-registered design contingency but a closeout-time bounded-prefix contingency added post hoc to document the consistent `converged_no_syndrome` mode. The correction is additive and is recorded in the new addendum and in `run_02` verifier v2 evidence; `run_01` is superseded precisely because it omitted the persisted PEG evidence limitation.

**Why n=1024 negative retained**: The 300-block n=1024 result is a complete, verifier-recomputed (`ok=true`, `problems=[]`, 13015 s wall) bounded negative for the tested deterministic `QC-cyclic-projective` family (full-rank, occupancy 9 at n=1024 / 18 at n=2048, zero duplicate/proportional keys) at fixed `m1=16` on the F03 GF32+GF32 V25 channel (field_id `c3a3660aa3cfbf788568cf366ee5de345ddc6be0372154a702c9e244a53bc6cf`, `HEAD c8d2acab`). L2 progress without convergence is real; the failure is isolated to the finite graph/decoder conversion layer and does not negate V25/V26/V27 or the entire GF32+GF32 route.

**Why no V31 rerun**: V31 is an immutable executed gate (M1 60/60 PASS, M2 PEG rank-deficient hard reject, M3 QC 0/300). Rerunning with the same deterministic constructions would reproduce the same rank deficiency and syndrome non-convergence; any tuning would violate the no-rerun/no-tuning discipline for a completed gate. The addendum therefore corrects only the closeout wording and lifecycle, not the science.

**Why V32 finite-DE bridge instead of graph/seed tuning**: Graph-local tuning (degree/PEG label/seed search) would re-search the same finite conversion layer that V31 isolated as failing, without testing whether the empirical channel itself supports a finite leakage budget at these lengths. V32 (`formal-nonbinary-ldpc-v32-finite-de-bridge`) is pre-registered to test the upstream hypothesis first: whether a channel-informed finite-DE bridge at n=1024 can recover a feasible split before any new finite graph is constructed. If that bridge fails, graph tuning is moot; if it passes, a new graph change can be built on a validated budget. This ordering preserves the V25/V26 channel scope and avoids speculative finite-graph search.

**What is corrected (4 rows)**: `fully executed -> partially executed`; `pre-registered bounded contingency -> post-hoc closeout contingency`; `complete finite-graph gate -> n=1024 complete plus n=2048 prefix`; `verifier proves all evidence -> verifier proves persisted evidence with PEG replay limitation`.

**Verifier v2 evidence (authoritative run_02, run_01 superseded)**: `run_02` block coverage n=1024 300/300 + n=2048 14×1M; exact 0/300, tag 0/300, false_accept 0; syndrome 0.00 (`converged_no_syndrome`); runtime 13015 s; QC matrix full-rank occupancy 9/18; input/code binding field_id `c3a3660aa3cfbf788568cf366ee5de345ddc6be0372154a702c9e244a53bc6cf`, `H` from V25 `data_inventory.json`/`split_manifest.json`, `m1=16`, `HEAD c8d2acab`; PEG limitation exact text `verifier proves persisted evidence with PEG replay limitation` (PEG rank-deficient, no M3 blocks, verifier attests only persisted rejection audit); strict replay/tamper `ok=true`, `recomputed_terminal=finite_graph_fail`, zero mismatches. run_01 is preserved but superseded because it omitted the persisted PEG evidence limitation.

**Consequences**: V31 remains `finite_graph_fail` but as `ARCHIVED_PARTIAL` (n=1024 complete plus n=2048 prefix, post-hoc contingency). The prior report `docs/nbldpc-v31-deterministic-finite-graph-redesign-report-20260820.md` is preserved, not rewritten. No qualification, promotion, V32 result, or complete n=2048 completion is implied. A successor V32 finite-DE bridge requires a new user-authorized OpenSpec change with fresh roots; any finite-code successor after that also requires a new change. Evidence roots `run_02` (authoritative) and `run_01` (superseded) remain immutable; no push was performed.

---

### 2026-08-23: V32 finite-DE bridge + operating-point audit correction — durable closeout (ACCEPTED)

**Decision**: Close the V32 arc with four accepted artifacts. (1) The V32 finite-DE bridge raw record (`nbldpc_v32_finite_de_bridge/run_01`, B0 6/6; B1–B4 0/60; B5 read-only import; exact-once, no resume) is retained byte-identical as valid evidence, but its persisted terminal `finite_graph_decoder_mismatch` is NOT accepted as a scientific attribution. (2) Main review verdict `EVIDENCE_VALID_BUT_ATTRIBUTION_INCONCLUSIVE` stands (`docs/nbldpc-v32-main-review-verdict-20260822.md`). (3) The first operating-point audit (`formal-nonbinary-ldpc-v32-operating-point-consistency-audit`, commits 60117174→dda3503e out of order) is annotated `post_hoc_exploratory_only / not_formal_pre_registered_gate / numerical_outputs_retained / scientific_terminal_superseded_pending_correction`; its numbers are retained, its attribution superseded. (4) The correction change `formal-nonbinary-ldpc-v32-operating-point-audit-correction` (freeze 59ba0236, impl 0765d893, evidence 29a5dafe, verifier-fix 3110cb0e) is ACCEPTED with candidate terminal `audit_corrected_rate_aligned_de_required` and archived.

**Reason**: Arm B1 was not a matched empirical-joint control. Its generator law Q_B1 (Alice uniform + Bernoulli(raw_ser) + uniform nonzero delta mod 1024) differs from the V25 empirical posterior law P(A,B)=N_ab/total and places positive mass on zero-support cells (analytic q_mass_on_p_zero_cells ≈ 0.239468/0.254127/0.255348 per source), making full E_Q[-log2 P] infinite. B1's active divergence therefore cannot attribute anything to the fixed QC graph or the V28R decoder. Corrected semantics (independently recomputed, R2 bit-exact): B2 `l2_errors_final=1024` is a not-run sentinel; B3/B4 improve-but-no-syndrome (~250→~179 mean L2 errors), never "divergent". Dual-law feasibility: the empirical-P budget is nominally feasible only (pure-syndrome gaps +180–187 bits; verbatim +244–251 bits; no finite-length/DE/fixed-graph/decoder claim); the original Q_B1 law is information-theoretically infeasible at the current allocation (H_Q(B|A) ≈ 3.1921/3.3626/3.3773 bits/symbol ⇒ required ≈ 3269–3458 bits vs pure syndrome 1000–1040 bits).

**Verifier semantic guards (fix 3110cb0e, ACCEPT)**: `full_expected_nll="infinity"` iff q_mass_on_p_zero_cells>0, otherwise the JSON-safe finite analytic value; minimal explicit run-root guardrail (protected old roots/subpaths, repo/results/diagnostics roots rejected; frozen v2 root or fake-runner workspace roots allowed); verify_manifest field-level guards (schema/lifecycle/flags/implementation identity/output list/frozen-block equality) with execution-time binding (never compared against current HEAD/CLI).

**Consequences**: Do not attribute B1 divergence to the fixed QC graph or V28R decoder; do not cite `finite_graph_decoder_mismatch` as an accepted root cause anywhere. The next authorized question is exactly: under the V25 empirical joint P(A,B), F03/A02 allocation, and V31 actual layer rates (L1 0.984375 ×3 sources; L2 0.8203125/0.814453125/0.8125), does the corresponding ensemble DE converge for all three sources and both layers? A candidate change (`formal-nonbinary-ldpc-v33-rate-aligned-empirical-channel-de-diagnostic`) exists as `DRAFT_PENDING_FREEZE_REVIEW` only; DE execution requires a frozen OpenSpec plus explicit authorization. Fixed-graph/decoder/NB-Polar successor selection remains undecided. No qualification, promotion, push, or sibling-checkout access occurred; all old evidence roots remain byte-identical.

---

### 2026-09-04: 双 PRIVATE 仓 remote 解耦采用 A 方案并冻结审计链

**Decision**: 采用 A 方案：原仓改名成为 Release 仓，新建 Comparison 仓。白名单加 4 项残留 B1 扩展放行（短标识 1b7055c / df01f068 / 7d9a77f / 6a58adb，日期与保护态见审计链），两处待推 push 保持未推。PR#1 已 MERGED（be62938，2026-09-04）。历史内容不迁移验收。已批准的脏态书面豁免归档，保持不动。

**Context**: 两仓分离前需冻结可审计的 remote 与分支终态，避免交叉可见与未授权迁移；残留项与待推项按白名单逐项审计放行。

**Alternatives considered**:
- 全量迁移历史内容：拒绝，不迁移验收。

**Consequences**: 两仓各自 origin 指向自家新址，legacy-origin 只读保留旧 URL；互不可见列为发布前必检；审计链唯一源为 `openspec/changes/repo-remote-decoupling` 三件套；后续引用以审计链为准，不记录临时盘点数字。

---

### 2026-09-05: V72P2D5 GF32 rate-mother plan frozen, no implementation or execution

**Decision**: Freeze `formal-ir-v72p2d5-gf32-rate-mother-plan` as `PLAN_CANDIDATE / EXECUTE_NOT_AUTHORIZED` (commit `c3499522`, 5 docs +540 lines, zero production `.py` change). Select V31 QC-cyclic-projective `build_layer` (`nonbinary_v31.py:624`) as the sole baseline with per-layer single `M_max=1000` build + `H[:k]` prefix disclosure; keep Lane-C as backup; veto V36/V35. Freeze the prior contract (`P1=sum_u2 P_F`, `P2=P_F/P1`, production `q@P`, oracle-L2 diagnostic-only, `lambda*=137.3823795883264` as sole adapter delta, floor dual-track `1e-300/1e-15`), the `rows=ceil(N*CE*f/5)` table (n=1024: `f=1.0 782/686 tot1468`, `1.05 821/720`, `1.1 860/755`, `1.2 938/823`), and the G0/G1/G2 gates with G2 n=256 as the sole life-death experiment (PASS = `f=1.2` end-to-end >=90% + monotonic + oracle>=APP; FAIL `<50%` route-dead / `50-90%` budget-insufficient both abandon n=1024 real).

**Context**: D4R2 selected model F (`d=1024, U=[5,5], GF32, N=1024`; `CE_L1=3.814742 / CE_L2_oracle=3.347605 / CE_joint=7.162347`) and proved `MODEL_BUDGET_MISMATCH` for the old 216 rows (gap 6254 bits / 1251 rows / 6.79x). D5 answers 6 frozen questions (prior/budget/constructor/mother/synthetic-gate/kill-experiment) without writing code, running any decoder, reading VAL, or creating `run_01`.

**Alternatives considered**:
- V36 incremental (+32 rows, row-weight 10-14) / V35 (192->224 hardcoded): rejected — too dense / hardcoded for 700-1000-row regime.
- V28 small-m constructors / V54 PEG-like incremental without audit: rejected as baseline — unverified at large m / missing rank audit; V28 kept as small-matrix reference, Lane-C as backup only.
- Old 216-row real experiment: prohibited — `MODEL_BUDGET_MISMATCH` ban stands.

**Consequences**: No apply before D5-T8 independent Plan Review ACCEPT (incl OQ1 per-layer `M_max` interpretation / OQ2 90% line decision); any decoder/VAL/n=1024 real execution still needs an independent `EXECUTE_AUTH`. Frozen thresholds/row table must not be relaxed in apply; implementation ambiguity stops to planner/OpenSpec revision on a new SHA.

---

### 2026-09-05: V72P2D5-R1 plan revision PASS, no code no execution

**Decision**: Revise `formal-ir-v72p2d5-gf32-rate-mother-plan` per review (commit `836e151c`, exactly 5 D5 plan files, zero production `.py` change, no `run_01`, Review PASS, `HEAD == origin` ahead 0). Durable deltas: `M_max=1000` is D5 synthetic cap only (not production sufficiency); OQ2 four-state `QUALIFIED/INCONCLUSIVE/CURRENT_CONFIGURATION_FAILED/BLOCKED`, `ROUTE_DEAD` deleted; probability axis `(Alice,Bob)` `axis0` summation; per-prefix 13-item structural gate + minimum 5-item PASS; M0 two-stage natural prefix (non-hypothesis) + deterministic row ordering without decoder; seeds frozen L1 `2026090501` / L2 `2026090502` / G0 `510..517` / G1 `600..699` / G2 `1000..1199`, search banned; oracle non-hard-gate diagnostic-only `ORACLE_APP_NONMONOTONIC_DIAGNOSTIC`; P0 preflight n=64 2 blocks, G1 `<=900s` / G2 `<=3600s` / single-call 120s / RSS `<2GiB`, calls G1 `APP100x2+oracle20x2` / G2 `APP200x3+oracle40x3`; metric `exact_failure_fraction` not FER; lifecycle three-false, no single authorization across G0/G1/G2.

**Context**: R1 answers review OQ1/OQ2 without execution; residual is `M AGENT_PROJECT_MEMORY.md` + `M docs/decision-log.md` + untracked baseline, uncommitted by design.

**Alternatives considered**:
- 90% death-line / `ROUTE_DEAD`: rejected — replaced by four-state verdicts.
- `M_max=1000` as production sufficiency: rejected — synthetic cap only.
- Oracle as hard gate / FER metric: rejected — diagnostic-only / `exact_failure_fraction`.

**Consequences**: Apply still gated by D5-T8 independent Plan Review ACCEPT + independent `EXECUTE_AUTH`; frozen seeds/budgets/call-counts/metric must not be relaxed in apply.

---

### 2026-09-05: coder-fast completion must chain reviewer-go (one-time exception R1 836e151c)

**Decision**: Every coder-fast COMPLETE must be followed by an independent read-only reviewer-go review. Plan-only or zero-production-code is not a skip reason. Any skip requires explicit user approval and dual recording in `AGENT_PROJECT_MEMORY.md` + `docs/decision-log.md`.

**Context**: V72P2D5 R1 push (commit `836e151c`) was pushed without post-commit reviewer review under explicit user approval on 2026-09-05. Read-only check confirms neither `docs/research-cycle-sop.md` (only generic "independent review" in §6 step 7 / §10 Pre-RESULT, zero coder-fast/reviewer-go mentions) nor `AGENTS.md` (only §6 line 180 `/implement-change` pipeline description, no mandatory chaining clause) states the explicit rule.

**Alternatives considered**:
- Directly patch SOP/AGENTS.md now: rejected — workflow-rule changes must go through an OpenSpec change; this entry only persists the rule and proposes wording.

**Consequences**: Schedule reviewer-go after every coder-fast COMPLETE (pre-push or post-commit make-up). Future skips without user approval are violations, not precedents. Proposed SOP patch (via OpenSpec): add mandatory "coder-fast → reviewer-go 必接" clause to `docs/research-cycle-sop.md` §6/§10 and mirror in `AGENTS.md` §3/§10.
## 2026-09-06 — Git identity removed from the default execution gate

- Decision: for this single-user local research repository, commit IDs are
  provenance and recovery aids, not execution capabilities.
- Default Pre-EXECUTE now checks intended branch, scoped file cleanliness,
  frozen scientific inputs/thresholds/command, focused tests, explicit user
  authorization, and output non-overwrite state.
- Rejected default: `HEAD == origin == implementation SHA`, stale-SHA grep,
  self-referential acceptance commits, checksums, and generic watchdog systems.
- Exact revision locking remains available only for a named concrete
  multi-writer, destructive, release, or evidence-integrity risk.
- Scientific review, failure retention, additive outputs, leakage/undetected
  semantics, and independent Pre-RESULT review are unchanged.
- Independent review is milestone-based, not required after every docs-only
  commit or tiny unchanged-scope fix. Existing packets inherit this decision;
  Git-identity clauses are non-binding absent a stated concrete risk.

---

### 2026-09-06: Main-plan roadmap shifted version-number → deliverable (docs only, no new decision)

**Decision**: Record `openspec/project.md` § Roadmap as the durable main-plan
roadmap (D1–D6 plus nearest milestone). No behavior, architecture, prompt,
tool-semantic, or workflow rule is changed by this entry; no new OpenSpec
change is opened for the project.md edit itself.

**Context**: A 2026-09-06 read-only review (no code change, no decoder run,
no CAL/VAL/raw read) found NB-LDPC kernels, layered decoding, and historical
results reusable, but two different-natured gaps remaining: rate/finite-length
validation in the new domain, and the full input→scan→report chain. The
roadmap therefore organizes by six deliverables (D1 D5 input-to-result loop;
D2 new-domain single-point NB-IR; D3 honest `reconciled_net` report interface;
D4 fixed-`d` `tau` scan then `d`×`tau`; D5 parallel security qualification;
D6 best-point plus holdout) instead of version numbers.

**Nearest milestone**: one real ttbin session at fixed dimension producing a
`tau` scan table backed by real NB-LDPC decoding; security-measurement
interface advanced in parallel, dimension widened after.

**Consequences**: Frozen order STRUCTURE → G0 → P0 → G1 → G2 and all V72
scopes/thresholds unchanged; P0/G1/G2 remain unexecuted. Future work cites
`openspec/project.md` for roadmap placement; this entry adds no freeze,
authorization, or scientific verdict.

---

### 2026-09-07: V72P2D5 unauthorized G1 output disposed VOID_RETAINED_IN_PLACE (docs only)

**Decision**: Dispose `workspace/v72p2d5_g1/20260906_r1/` (4 files,
`decoder_calls=440`) as `VOID_RETAINED_IN_PLACE`. Retained unmodified as
forensic evidence of a test-isolation defect; permanently barred from citation
as a G1 result, a performance measurement, or evidence about the NB-LDPC
method. No delete, no move, no rename, no rerun, no authorization change.

**Context**: `MODEL_F_INPUT_PRE_RESULT_REVIEW_R1.md` returned
`PRE_RESULT_REVIEW_FAIL` on the single blocker PR16 — the G1 formal root existed
while `g1_execution_authorized=false` and `next_gate=P0_PACKET_REVIEW`. Cause is
incident I09 (tests called `run_g1_synthetic(authorized=True)` without fake
decoder / injected arrays / tmp `out_dir`, so once the Model-F artifact existed
the production decoder bound and the default writer hit the formal root).
Model-F artifact content itself passed PR01-PR15 and PR17-PR23. The isolation
repair is complete and evidenced (165 collected / 165 passed).

**Alternatives considered**:
- Delete the four files: rejected — irreversible, breaks the evidence chain.
- Move to a quarantine directory: rejected — violates incident I08
  (no move/rename/copy).

**Consequences**: All `*_execution_authorized` stay false; `next_gate` stays
`P0_PACKET_REVIEW`; no P0 authorization. PR16 is addressed by record only —
clearance requires an independent Pre-RESULT re-review. A future authorized G1
run must use a new output root and must not reuse or compare against this one.

---

### 2026-09-07: V72P2D5 Model-F input result ACCEPTED (docs only, no authorization)

**Decision**: Accept the canonical Model-F CAL-TRAIN input at
`workspace/v72p2d5_model_f_input/20260907_r1/` as the P0/G1/G2 prior input.
Record acceptance at the cycle level; the artifact's own `status` stays
`MODEL_F_INPUT_CANDIDATE` because rewriting a file inside a protected
immutable root is forbidden and the loader accepts both values.

**Context**: Implementation accepted; Pre-EXECUTE R2 PASS after the PX11 path
fix; exactly one authorized `prepare` plus one `verify` executed 2026-09-07
(authorization consumed); Pre-RESULT R1 FAILed on the single blocker PR16;
the unauthorized G1 root was dispositioned `VOID_RETAINED_IN_PLACE`; the
independent Pre-RESULT R2 returned PASS with C01-C11 all PASS and `195 passed`.

**Material caveat**: PR16 was cleared BY RECORD, not by condition. R1's PR16
was the formal check "formal roots absent"; that condition is still not met —
`workspace/v72p2d5_g1/20260906_r1/` exists. R2 reinterpreted PR16 by its
intent (unauthorized numbers must not enter the result chain) and judged that
intent closed by the disposition. Deletion and quarantine-move were both
explicitly rejected by the user.

**Alternatives considered**:
- Flip the artifact `status` to `ACCEPTED`: rejected — would require rewriting
  inside a protected immutable root.
- Hold acceptance until PR16 is physically cleared: rejected — that would
  require reversing an explicit user decision and adds no scientific
  protection to the Model-F claim.

**Consequences**: All nine `*_execution_authorized` stay `false`;
`scientific_promotion` stays `false`; `next_gate` stays `P0_PACKET_REVIEW`.
P0 is not authorized. Residual risks carried into the P0 packet: `R-R1`
production-side bare-authorized defaults unchanged, recurrence guard is
test-side only, so future P0/G1/G2 packets must re-verify isolation before any
authorization; `R-R2` `M24`/`P12` no longer assert global formal-root absence,
so an unexpected new formal output relies on per-test snapshot comparison
rather than a global gate.

---

### 2026-09-07: V72P2D5 P0 cost preflight ACCEPTED as cost measurement only (docs only, no authorization)

**Decision**: Accept the second authorized P0 invocation at
`workspace/v72p2d5_p0_cost/20260906_r1/` as `P0_RESULT_ACCEPTED` with scope
`COST_MEASUREMENT_ONLY`, recorded in
`docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/P0_RESULT_ACCEPTANCE_R1.md`.
Acceptance of a cost measurement is not scientific promotion and grants no G1
authorization.

**Context**: Measured scalars transcribed verbatim from `results.json`:
phase `p0-cost`; block_length 64; f_list 1.0, 1.2; frozen_rows f=1.0 -> m1 49 /
m2 43 and f=1.2 -> m1 59 / m2 52; seeds 2026090510, 2026090511; decoder_calls
12; records 1.0 app 1.8862763999495655 / 360 / null, 1.0 oracle
1.04731999989599 / 180 / null, 1.2 app 3.459295800072141 / 360 / null, 1.2
oracle 1.671841400093399 / 180 / null; projected_g1_s 161.8241519993171;
projected_g2_s 485.47245599795133; projection_blocked false; passed true; run
wall (operator) 8.6278899 s, exit 0, stdout and stderr empty; decode-attributed
total 8.064733600011096 s against the 1440 s cap, no `RESOURCE_OVERRUN`.
Four-review chain landed by this packet: `P0_PRE_EXECUTE_REVIEW_R1.md`
`PRE_EXECUTE_REVIEW_PASS` with five open questions decided;
`LOADER_FIX_REVIEW_R1.md` `LOADER_FIX_REVIEW_PASS` for the Model-F consumer
path fix (`299416ae`); `P0_PRE_RESULT_REVIEW_R1.md` `P0_PRE_RESULT_REVIEW_PASS`
with limitations; `GUARD_REWORK_REVIEW_R1.md` `GUARD_REWORK_REVIEW_PASS` with
L1-L4. Authorization history: two P0 authorizations were issued; the first
(2026-09-07, `a71188fb`/`3ecaebb6`) was consumed with no run because the phase
refused in 0.376 s on a false missing-input message caused by the consumer
path defect; the second (`f1cdf970`/`b4696273`) produced this result; both are
consumed and neither is reusable.

**Alternatives considered**:
- Accept P0 as a correctness or qualification result: rejected — P0 records
  cost only; it grades nothing, and establishes no `exact_failure_fraction`,
  no FER, no leakage, no key rate, no net rate, and no qualification of
  NB-LDPC, the dv3 mother, the rate points, or Model-F.
- Treat `projected_g2_s` or `projection_blocked: false` as G2 permission:
  rejected — the projections are `per_call x {240, 720}` with no width or
  row-count scaling, so they grant G2 nothing.
- Create a G1 authorization in this packet: rejected — G1 stays unauthorized
  and unfrozen; freezing, review, and authorization belong to later packets.

**Consequences**: P0 establishes no correctness, no `exact_failure_fraction`,
no FER, no leakage, no key rate, no net rate, and no qualification; no
statement that G1 or G2 will pass, complete, or fit their budgets; no
authorization for anything. Seven limitations carried into the G1 packet, each
tagged `MUST_CARRY_INTO_G1_PACKET`: L1 (depth, top-level-only snapshot),
L2 (T1_23 narrowness), L3 (T1_22 live-fire by logic reading, not live red),
L4 (guard-rework `STATUS=63` superseded by 1969 porcelain lines / 1887
modified paths / `numstat` content changes 0), L-RSS (`rss_bytes` null on
Windows, 2 GiB reference unchecked), L-SCALE (projections carry no width or
row-count scaling; `projected_g2_s` and `projection_blocked: false` grant G2
nothing; `projected_g1_s` is a same-width call-count indication only), L-ITER
(all 12 decodes ran the full `MAX_ITER = 90`, a saturated upper bound; G1 must
budget at the cap and record exact/syndrome outcomes). All nine
`*_execution_authorized` stay `false`; `scientific_promotion` stays `false`;
`next_gate` moves `P0_PACKET_REVIEW -> G1_PACKET_REVIEW`; no authorization was
created. Next: freeze the G1 execution packet carrying every limitation, then
an independent Pre-EXECUTE review, then a separate explicit G1 authorization;
these may not be merged or reordered.

---

### 2026-09-07: V72P2D5 G1 readiness implementation-only acceptance and Pre-EXECUTE packet freeze (docs only, no authorization)

**Decision**: Accept the G1 readiness implementation at `cf61ee63` (predecessor `614aab9e`, spec/review `d47e7da1`) as implementation readiness only, recorded in `G1_IMPLEMENTATION_ACCEPTANCE_R1.md`; freeze `G1_PRE_EXECUTE_PACKET_R1.md` as `G1_PRE_EXECUTE_PACKET_FROZEN / EXECUTE_NOT_AUTHORIZED`; move `next_gate` to `INDEPENDENT_G1_PRE_EXECUTE_REVIEW`.

**Context**: Review chain — packet review PASS, readiness code review PASS (`G1_READINESS_CODE_REVIEW_PASS`), scope addendum PASS (`G1_CODE_REVIEW_SCOPE_ADDENDUM_PASS`, exact frozen three pytest files, `219 passed`), live Windows RSS positive. Accepted functionality: new root `workspace/v72p2d5_g1/20260907_r2`, Windows RSS ABI with 200-sample peak semantics, aggregate exact/syndrome/iteration/RSS fields, prospective signal, outcome precedence (seven labels, `passed` iff `G1_TREND_PASS`), fail-loud writers, no-subdirectory guard, test-only reachability/isolation. Scope is implementation readiness only; no decoder/G1 result, FER, leakage, key rate, qualification, or G2 claim. Real external-file Model-F sentinel and watchdog semantics stay mandatory in Pre-EXECUTE; acceptance grants no authorization. Disclosed boundaries carried: process-vs-entrypoint wall (operator outer wall controls 900 s classification); `app_iterations_max<=180` asserted not clamped; exception/timeout/refusal are operator-side labels; G1 is synthetic trend only.

**Consequences**: G1 remains unauthorized and unexecuted; G2 remains unauthorized. Frozen signal/outcomes/resources and the exact single-attempt command live in the packet. Next is the independent Pre-EXECUTE review (reviewer may not flip authorization or run G1), then a separate explicit user authorization. All nine authorizations stay false; promotion stays false.

---

### 2026-09-07: V72P2D5 G1 result acceptance — synthetic completed-no-signal failure (no pass, no rerun, bounded attribution only)

**Decision**: Accept the sole frozen G1 attempt in `workspace/v72p2d5_g1/20260907_r2` as `G1_RESULT_ACCEPTED` with scope `SYNTHETIC_COMPLETED_NO_SIGNAL_FAIL`, outcome `G1_COMPLETED_NO_SIGNAL_FAIL`, `passed: false`, recorded in `docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/G1_RESULT_ACCEPTANCE_R1.md`.

**Context**: Evidence chain `cf61ee63 → 6494b623 → f4d577fb → 58c68961`; dual review (Pre-EXECUTE PASS + Pre-RESULT `G1_PRE_RESULT_REVIEW_PASS`, R01–R09 all PASS on internal coherence). Literals, identical across all four files: both f APP exact `0/100` (rate `0.0`, failure `1.0`), APP syndrome-ok `0`, oracle exact/syndrome `0`, `app_iterations_max 180` (cap `2×90`), APP iterations `18000 = 100×180`, oracle `1800 = 20×90`, `decoder_calls 440 = 400 + 40`, crashes/nonfinite `0`, wall `238.86517630005255 s <= 900` (operator outer `239.110 s`), RSS `115142656 < 2147483648`. Resource gates pass; signal FALSE (top APP exact `0`), so the terminal is a no-signal failure with `passed=false`. Exact/syndrome/oracle stay isolated; stored zeros are literal, never relabeled as FER, undetected success, correctness, or data quality. The single authorized attempt is consumed; no retry/resume/second attempt.

**Consequences**: Not trend pass, qualification, G2 readiness, method success, rerun permission, or reinterpretation of the formal record. All nine `*_execution_authorized` stay `false`; `scientific_promotion` stays `false`; G2 remains absent. `next_gate` moves `INDEPENDENT_G1_PRE_EXECUTE_REVIEW -> G1_NO_SIGNAL_ATTRIBUTION_IN_PROGRESS`. Next is bounded failure attribution only under the D5 packet: no formal CLI phase, no formal-root write, no VOID-interior read, no G2, no real data.


---

### 2026-09-07: V72P2D5 G1 no-signal attribution (FINITE_LENGTH_DISCLOSURE_INSUFFICIENT, no code change, route decision)

**Decision**: Attribute the accepted G1 dual-zero to `FINITE_LENGTH_DISCLOSURE_INSUFFICIENT` as the sole primary bucket, recorded in `docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/G1_NO_SIGNAL_ATTRIBUTION_R1.md`; make no code change and return `G1_ATTRIBUTION_ROUTE_DECISION` for one next square-disclosure oracle probe (approve / reject / redirect).

**Context**: 29 development decoder calls (of 300; ~12.9 s wall; peak RSS 113790976 B): accepted Model-F actual CE is L1/L2 ~= 5.0/5.0 bits (uniform priors, I(A;B) ~= 0; counts mean cell 0.25 vs lambda* 137.38) vs frozen sizing constants 3.81/3.35, so frozen rows 49/43 and 59/52 sit below the Slepian-Wolf need 64/64 (f=1.0) and 77/77 (f=1.2). Paired controls on identical samples: APP 0/4 and oracle 0/4 with saturation (formal signature reproduced); full-disclosure H2[:52] control 0/4; doubled cap (180) still fails; decoy-prior probes converge exact=1 on all four frozen prefixes (decoder/graph healthy with signal); GF32 tables/syndrome/rank cross-match exactly. Decoder/APP-propagation/iteration/prefix hypotheses rejected as primary (prefix audit failures carried secondary).

**Consequences**: No OpenSpec/code diff (no implementation defect; frozen constants untouched; formal result unchanged). `next_gate` moves `G1_NO_SIGNAL_ATTRIBUTION_IN_PROGRESS -> G1_ATTRIBUTION_ROUTE_DECISION`. No G1 rerun, no G2, no real data; all nine authorizations stay false; promotion stays false.

## 2026-09-08 V72P2D5 G1 wide attribution R2 (lambda-contract defect + candidate)

**Decision**: Supersede R1's `FINITE_LENGTH_DISCLOSURE_INSUFFICIENT` as primary with `LAMBDA_APPLICATION_CONTRACT_DEFECT` (R1 bucket carried as downstream secondary); add review-ready nonformal candidate `build_f_model_concentration` + `prepare_model_f_prior_candidate` (additive only) under OpenSpec `v72p2d5-g1-information-recovery-r2`; move `next_gate` to `INDEPENDENT_G1_INFORMATION_RECOVERY_R2_REVIEW`.

**Context**: 53 development decoder calls (~51 s wall; peak RSS 240963584 B; CAL-only, no VAL): frozen `lambda*=137.38` was selected as total per-column concentration (D4R2 `build_f`) but the accepted consumer applies it per cell (140,680 added/column vs 256 observed, 99.82% prior, MI 0.0004 bits vs 2.48 backoff). Same-counts backoff returns to the D4 family (joint 7.51 vs 7.16; held-out C1 7.162347 reproduces D4R2 exactly). Square probe (rank-64 mother, seed 2026090801): C0 oracle 0/4, C1 oracle-L2 4/4; C1 L2 at H2[:52] 2/4; C1 L1 fails at every disclosure including square (mass 0.096 below BP threshold, binding constraint). C2 held-out catastrophic (504.7); C3 dominated (7.34).

**Consequences**: Frozen functions/constants/seeds/thresholds/authorizations/accepted artifacts unchanged; production phases keep the frozen path. One pre-existing suite failure noted (`test_G1R01...` asserts absence of the accepted G1 root; stale since Sept-7 acceptance; untouched). No formal rerun, no G2, no push.

## 2026-09-08 V72P2D5 G1 R2 acceptance (additive backoff-prior candidate, no formal change)

**Decision**: Accept the independently reviewed R2 candidate (`G1_INFORMATION_RECOVERY_R2_REVIEW_PASS`) as `G1_INFORMATION_RECOVERY_R2_ACCEPTED` with scope `ADDITIVE_NONFORMAL_BACKOFF_PRIOR_CANDIDATE`, terminal class `LAMBDA_APPLICATION_CONTRACT_DEFECT`, `formal_g1_result_changed: false`, `production_wiring_changed: false`, recorded in `docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/G1_INFORMATION_RECOVERY_R2_ACCEPTANCE_R1.md`.

**Context**: Chain `88053563→a93106f5→21576add→1d4fa912`; like-for-like same-counts `10.0 → 7.51` (MI `0.0004 → 2.48` bits, truth mass `0.031 → 0.254`); three-call square confirmation (old 0/4 vs candidate oracle-L2 4/4); C1 L1 mass `0.096` fails everywhere including square (binding L1 question); C1 L2 recovers only at 52–64 rows (near-zero rate, not an operating point).

**Consequences**: Accepted Model-F/G1 artifacts, thresholds, seeds, authorizations unchanged; production keeps the frozen path. `next_gate` moves `INDEPENDENT_G1_INFORMATION_RECOVERY_R2_REVIEW -> G1_L1_ESTIMATOR_DISCRIMINATOR_IN_PROGRESS`. No G1 rerun, no G2, no qualification/promotion, no push.

## 2026-09-08 V72P2D5 G1 L1 discriminator (BP-threshold terminal, route-stop)

**Decision**: Close the L1 discriminator with terminal class `L1_BP_THRESHOLD_NOT_RECOVERABLE_AT_N64`, recorded in `docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/G1_L1_ESTIMATOR_DISCRIMINATOR_R1.md`; set `next_gate` to `D5_ROUTE_STOP_REVIEW`.

**Context**: Prereg `f0e4a1c` before any score/call. CAL-only held-out L1 NLL selects E2 (`kap*≈62.10`, unanimous; mean 3.7717 vs E1/E3 3.8147); E1≡E3 bit-identical (backoff linearity under marginalization). Paired decoder (75 calls, 0 nonfinite, flags agree): n64 0/24 incl. square; n128/n256 nonzero-rate 0/4 everywhere; square-only partials 1/4, 2/4. Truth mass ~0.10–0.15 vs ~0.28 needed. No code justified; production untouched; four-file suite 259 passed.

**Consequences**: Stop n64 two-layer L1 recovery and block scaling; no G2; any successor is a new decoder/matrix change, not estimator work. Formal G1 negative result unchanged; all authorizations false; no push.

## 2026-09-08 V72P2D5 D5 route-stop acceptance (current-path stop, decomposition successor)

**Decision**: Accept `D5_ROUTE_STOP_REVIEW_PASS` as `D5_ROUTE_STOP_ACCEPTANCE_R1.md`: terminal `D5_CURRENT_TWO_LAYER_RATE_MOTHER_BP_PATH_STOPPED`, reason `ACCEPTED_G1_NO_SIGNAL_PLUS_CAL_ONLY_L1_DISCRIMINATOR_NO_USEFUL_RECOVERY`, scope exactly the current fixed high-five/low-five two-layer rate-mother/BP path.

**Context**: Independently reviewed chain R2 acceptance `247f8adc` → prereg `f0e4a1cf` → evidence/gate `d6fabf09`; review `D5_ROUTE_STOP_REVIEW_R1.md` landed unchanged (S01–S11 PASS, S12 advisory).

**Consequences**: GF32/NB-LDPC stays open; formal G1 stays accepted completed-no-signal (not rewritten); G2 unauthorized and absent; successor is the reversible 5+5 bit-partition decomposition discriminator (252 ordered partitions, CAL-only, bounded paired development decoder). `next_gate` moves `D5_ROUTE_STOP_REVIEW -> D5_DECOMPOSITION_SUCCESSOR_PREREG`. No push.

## 2026-09-08 V72P2D5 decomposition successor R1 (no N64 recovery, graph/mother route next)

**Decision**: Close the reversible-partition discriminator with terminal `DECOMPOSITION_NO_N64_RECOVERY`, recorded in `docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/D5_DECOMPOSITION_SUCCESSOR_R1.md`; no code/OpenSpec implementation (§4.6 not-strong branch).

**Context**: Prereg `e4d3af7` before scores/calls. 252 partitions CAL-only (chain err ≤ 8.88e-16; joint 7.162347 invariant; control reproduces c1 E1 3.814742); rank-1 IS the current mapping `(5,6,7,8,9)` m=(59,52). 192/600 dev calls (100.8 s, peak RSS 124219392 B, 0 crash/nonfinite/disagreement): APP exact 0/8 everywhere incl. square; oracle-L2 6/8 non-square + 8/8 square on rank-1 only (diagnostic). Evidence `workspace/d5_decomposition_successor_r1_c765e3010674/`; four-file suite 259 passed.

**Consequences**: Decomposition family exhausted without APP signal; next route `D5_GRAPH_MOTHER_SUCCESSOR_PROPOSAL` by main-thread proposal (not authorized). Formal G1/Model-F/roots unchanged; all authorizations false; no push.

## 2026-09-09 V72P2D6 R1c-A3 post-run verifier rework (blocked run, topology claim forbidden)

**Decision**: Accept `D6_R1C_A3_PRE_RESULT_REVIEW_PASS_BLOCKED_RUN`: the R1c-A2 root solidifies as an implementation/structure-blocked development attempt with recomputed terminal `D6_GRAPH_STRUCTURE_INVARIANT_BLOCKED`; stored `D6_GRAPH_TOPOLOGY_NO_USEFUL_RECOVERY` is preserved but unsupported and must not be cited.

**Context**: A2 verifier FAILs repaired via OpenSpec amendment (identity key +`n`; stage-separated canary/scaling-per-width/confirmation recompute; crash precedence with degree→invariant class; EMPTY confirmation label; stored+recomputed reported fail-closed). Forensics (read-only, zero decoder): 184 rows reconcile 104/40/40/0; 64 attempted degree crashes from degree-1 check rows in frozen T3/M1 graphs (integer proof + structure-only rebuild with negative controls; transport/precondition excluded). Corrected `--verify` once on the immutable root: exit 0, 15/15 PASS + agreement False. Focused 42/42; seven-file non-perf 323/323; v38 skipped (recorded).

**Consequences**: `next_gate` → `D6_GRAPH_MOTHER_R1C_A3_BLOCKED_AWAITING_MAIN_THREAD_ROUTE` (successor needs new OpenSpec + fresh authorization; nothing granted here). Exposed audit gap: structural eligibility gates `zero_rows` but never minimum check degree — candidate rule for any successor proposal. All authorizations false; G2 absent; no push.

## 2026-09-09 V72P2D6 R1c-A4 structure performance (READY, no run authorized)

**Decision**: Accept `D6_R1C_A4_PERFORMANCE_REVIEW_PASS`: scaling structure wall 10897.7 s → 2.5 s (≈4280×, pruned T2 + two-build replay, bit-identical science for dispatched arms); n64 outputs exactly equal at 21.0 s (was 42.2 s); RSS ≈ 90 MB; zero decoder calls. Final state `READY_FOR_FUTURE_D6_PRE_EXECUTE_REVIEW` (structure path only).

**Context**: Profile-first (T2 ≥99.9% of scaling pools); three frozen optimizations (pruning, ≤2 constructions, overflow passthrough; T2 semantics untouched); equivalence proven against committed A2 evidence (n64 all-arms + T1/M1 at n128/n256 exact); fresh-root benchmark cold+warm after-side, cold before-side; before-warm-n256 disclosed unmeasured with seconds-level bound (zero gate impact at 1000×+ margin). Focused 51/51; seven-file non-perf 332/332.

**Consequences**: Any future D6 execution still needs its own OpenSpec + Pre-EXECUTE + explicit authorization — nothing granted. T2 semantics at n64 unchanged. All authorizations false; G2 absent; no push.

## 2026-09-10 V72P2D6 R1c-A5 validity closure, repair infeasibility, R1d readiness (eligible-only branch)

**Decision**: Accept `D6_R1C_A5_REVIEW_PASS_ELIGIBLE_ONLY_BRANCH` (implementation + validity reviews): the I1 check-degree invariant defect is proven and gated; admissible repair is structurally infeasible as frozen; the R1d package is recorded `NOT_AUTHORIZED`.

**Context**: Independent 144-cell matrix (own implementation; 132/132 main-thread cross-check, 51/51 recompute, replay all True): T3/T4/M1 carry degree-1 check rows at f1.2+square everywhere (M1 exactly at the zone-counting bound); T2 rank-deficient at every square (63/62, 123/122, 246/240); B0/B1 bounds recorded unmodified. Frozen eligible + A2 selection {B0,B1,T1,T3,M1} reproduced exactly. I1 landed (eligible-AND, dispatch guard, verify INFO/PASS-FAIL) with fake-only tests; builders byte-identical; historical root verify exit 0, 15/15 PASS, agreement False, mtimes intact. Repair study: 0/10 preregistered sandbox rules admissible (R3 fails everywhere; three identity non-repairs) with per-family infeasibility proofs + a 3-option `REQUIRES_MAIN_THREAD_RULING` menu, nothing landed. Focused 56/56; seven-file non-perf 90/90 (membership reconstructed and named).

**Consequences**: `next_gate` → `D6_GRAPH_MOTHER_R1C_A5_TRACK_A_COMPLETE_TRACK_B_PENDING`. R1d viable without a ruling only on the eligible-only {B0,B1,T1} branch — itself unauthorized here. All authorizations false; G2 absent; no push.

## 2026-09-10 V72P2D6 R1c-A6 exact-equivalent T2 acceleration (PASS, no NOT_MET)

**Decision**: Accept `D6_R1C_A6_REVIEW_PASS`: staged/vectorized/integer-encoded T2 (`_build_T2_support_fast`, reference intact, key/order frozen, no float) proven exactly equal at all seven gates; all performance targets met with ≥10x factors; A4 gains not regressed.

**Context**: Equivalence — T2 n64 live-vs-reference, n128/n256 vs replay-verified committed fixtures, per-variable traces, committed n64 rows byte-identical, eligible/selection unchanged, replay + seq==par, A4 guards green, sandbox-T2 gate vacuous (no sandbox T2 exists). Benchmark (fresh roots, cold+warm, A4 protocol): T2/layer n64 1.2 s (≤5, 34.5x), n128 26.6 s (≤90, 24.7x), n256 516.1/479.7 s (≤600, 19.9x); n64 all-8 1.5 s (≤8); fb-only 0.6/1.3 s vs A4 2.5/2.7 s; RSS ≈ 93 MB; zero decoder calls; no retry. Slow-task inventory measured (v38 T0 2.0 s, T1 812/810 s, orchestration 345/344 s, lane-A ≈40 s, helpers ≤46 ms; V30R 74.8/719.9 s cited, decoder-bound, not re-runnable). Focused 61/61 + slow n256 cell; seven-file non-perf 95/95.

**Consequences**: `next_gate` → `D6_GRAPH_MOTHER_R1C_A5A6_COMPLETE_AWAITING_MAIN_THREAD_RULING`. T2-at-n256 no longer breaches the chunk block on structure cost. Any future D6 execution still needs its own OpenSpec + Pre-EXECUTE + explicit authorization — nothing granted. All authorizations false; G2 absent; no push.

## 2026-09-10 V72P2D6 R1d Option C freeze (eligible-only {B0,B1,T1}, Pre-EXECUTE pending)

**Decision**: Main-thread ruling Option C accepted and frozen: no SC/M knob lift (A rejected: R2 degree-profile lift + selection re-freeze; B rejected: M-over-B identity weakening + re-freeze; both reopen repair research); SC/accumulator structurally inadmissible as frozen; R1d = {B0,B1,T1} with T2 rank-bound recorded only; no A2 call/root reuse; schema `r1d-v2` approved for new roots (historical A2 immutable, old schema).

**Context**: 22 distinct R1d structure cells (26 role-cells; 4 T1-n64 cells shared by canary+confirmation) proven ⊆ A5 valid subset (CSV read, zero decoder, 22/22 frozen+I1 pass, 0 conflicts; worst-case 552 ≤ 2500 calls). New OpenSpec change `v72p2d6-gf32-graph-mother-r1d-option-c` + `D6_GRAPH_MOTHER_OPTION_C_ACCEPTANCE_R1.md` + `D6_GRAPH_MOTHER_R1D_EXECUTION_PACKET_R1.md` (exact `--r1d` command, budgets, stop rules, no-reuse, claim ceiling). R1d NOT authorized, NOT executed; no R1d root exists.

**Consequences**: `next_gate` → `D6_GRAPH_MOTHER_R1D_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. Eligible-only `--r1d` implementation + focused tests + independent reviews next. All authorizations false; G2 absent; no push.

## 2026-09-10 V72P2D6 R1d Option C implementation + Pre-EXECUTE (PASS, awaiting explicit authorization)

**Decision**: Accept `D6_R1D_PRE_EXECUTE_REVIEW_PASS_AWAITING_EXPLICIT_AUTHORIZATION` (implementation review `D6_R1D_IMPLEMENTATION_REVIEW_PASS` first, zero rework rounds; this review grants no authorization).

**Context**: Eligible-only dispatch layer landed (mother module pure-append: `R1D_ARMS`, 22-cell `R1D_VALID_SUBSET`, arm/subset/live-I1 guard, T1-only fallback, schema-`r1d-v2` writer for new roots, 4-root named refusal; `--r1d` runner mode default-off with frozen default call shapes intact per the A4 pin). 13 focused R1d tests (all 12 packet properties + `--dry-structure` behavioral run) + full D6 file + seven-file non-perf suite: 356/356 green in a fresh task-owned basetemp. Perf-v38 skipped (scoped deps outside the v38 orchestration path; v38 file has zero v72p2d6 references). Independent subset re-derivation 22 == 22, 0 matrix-invalid, live spot-check pass. No R1d root exists; historical A2 header still old-schema, path git-clean; zero decoder calls throughout.

**Consequences**: R1d stays NOT authorized, NOT executed (`next_gate` unchanged: `D6_GRAPH_MOTHER_R1D_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`). Execution needs a separate explicit main-thread grant; mandatory Pre-RESULT review before any solidification. All authorizations false; G2 absent; no push.

## 2026-09-10 D7-A GF32 decoder ground-truth certification PASS (no production change)

**Decision**: Record D7_A_DECODER_CERTIFICATION_PASS. Historical row-layered FFT-QSPA kernel matches the independent oracle (tables exact; check-update worst 3.3e-16; tree posterior worst 6.7e-16; loopy per-sweep worst 7.2e-13; L1->L2 soft-APP bridge verified, final_beliefs log-domain, no double-softmax); all within tol 1e-10 with zero production diff and no trace hook.

**Context**: New oracle comparison_bench/src/comparison_bench/formal_ir/v72p2d7_gf32_decoder_certification.py + 14 tests (14/14); related v35/D5 files 204/204 combined; D6/field files 88 pass + 1 pre-existing unrelated CRLF-churn hash-pin failure (qldpc_reference.py, untouched). Tiny synthetic in-memory calls only; R1d still paused, G2 absent, all auth keys false, no push.

**Consequences**: next route D7_B_EASY_REGIME_PACKET_FREEZE readiness only (design, no execution). D7-B/C/D execution, R1d, G1, G2 all unauthorized. Evidence: docs/research_cycles/V72P2D7-GF32-DECODER-CERTIFICATION/ (PREREG/REPORT/REVIEW).

## 2026-09-10 D7-B easy-regime freeze, harness + independent Pre-EXECUTE (PASS, awaiting explicit authorization)

**Decision**: Accept `D7_B_PRE_EXECUTE_REVIEW_PASS_AWAITING_EXPLICIT_AUTHORIZATION` (implementation review `D7_B_IMPLEMENTATION_REVIEW_PASS` first, zero rework; neither grants authorization nor runs D7-B).

**Context**: R1+A1 frozen: 64 cells (4 tiers x 4 priors x seeds 2026091200..03), caps [1,2,4,8,16,32,90], 420-call global stop, 120/1500/1800(+30)s, <2GiB. TREE_6 is the literal A1 topology (rows [3,3,2], c0=[0,1,2]/[1,7,13], c1=[2,3,4]/[29,1,7], c2=[4,5]/[13,29]; V=9/E=8, var degs [1,1,2,1,2,1], rank 3); superseded R1 [2,3,2]/7-edge tuple impossible (7<8) and rejected by regression test, never dispatched. Tree-exact is dual message-passing vs 1024-projection cross-check (never 32^6, never production/FFT). Harness `formal_ir/v72p2d7_gf32_easy_regime.py` + 19 tests + gated runner; D7-A oracle reused, v35/D5 read-only. Qualification: py_compile clean; D7-B 19/19; D7-A 14/14; v35 25/25; field milestone 13/14 with the same pre-existing CRLF hash-pin failure (isolated). Live env: RSS 85139456 int; timeout.exe present, 3s rehearsal exit 124; out-of-repo reachability with repo-off-sys.path, sentinel, empty tempdir, zero scientific calls; fresh UUID target absent; unauthorized run refuses with no root. Tiny production contacts only (n=3 single-check k<=2 proxy check); `_EXECUTION_CONSUMED` false; no D7-B root.

**Consequences**: D7-B NOT authorized, NOT executed (`next_gate`: `D7_B_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`). Execution needs a separate verbatim user grant for one UUID; mandatory Pre-RESULT review before any result. R1d stays paused; G1/G2 unauthorized; no push.

## 2026-09-10 D7-B WSL launch rework + renewed Pre-EXECUTE (PASS, awaiting fresh explicit authorization)

**Decision**: Accept `D7_B_WSL_LAUNCH_REWORK_REVIEW_PASS` (zero repair cycles) then `D7_B_PRE_EXECUTE_REVIEW_PASS_WSL_R2_AWAITING_FRESH_AUTHORIZATION` (grants nothing, generates no UUID). Spent UUID `0f1ad3ec-f9e0-463f-a7dd-d9880ff7230c` stays exhausted; disposition `D7_B_PRE_EXECUTION_LAUNCH_BINDING_BLOCKED` retained as a launch defect with no terminal/count/result inferred.

**Context**: Zero-decoder probe proved the 5-step package-context cause (file-location load, package absent, top-level v35 fallback, relative import without parent). Repair is runner-local only (+4 lines: `<repo>/comparison_bench/src` from resolved `__file__`, insert-if-absent before core load); core/v35/D5/D7-A/field byte-unchanged; fallbacks still `except ModuleNotFoundError`-only. L01–L12 green (miniature original-failure capture; help/dry-run both cwds; 64 cells; src-only insertion; exact package v35 bind never called; fake-shadow refusal; unauthorized exit 3 pre-bind; 19+14 suites green; frozen contract; roots/auth unchanged). Full D7-B 31/31, D7-A 14/14, v35 milestone 25/25. WSL identity: venv python 3.12.3, NumPy 2.4.4, kernel 6.18.33.2-WSL2, GNU timeout 9.4, RSS 9416704, 3 s rehearsal exit 124; external binding probe reached the exact v35 callable with zero call/zero root. WSL-A1 addendum freezes shell-spelling-only command shape; no new UUID.

**Consequences**: Documented gate `D7_B_WSL_READY_AWAITING_FRESH_EXPLICIT_AUTHORIZATION` (docs only; `cycle_state.yaml` untouched, all keys factually unchanged). Any future run needs a fresh explicit user authorization naming one new UUID. R1d stays paused; G1/G2 unauthorized; no push.

## 2026-09-10 D7-B WSL R2 scoped result acceptance (RESOURCE_OVERRUN retained, hard-decision limits disclosed)

**Decision**: Accept the WSL R2 root (`c605d1e6-8577-4c52-a865-12500fc8c964`) as authentic, immutable and contract-faithful with the stored terminal `D7_B_RESOURCE_OVERRUN` retained. Accepted scope is exactly `HARD_DECISION_EASY_REGION_OBSERVED_WITH_RESOURCE_AND_SOFT_BELIEF_LIMITATIONS`: 64/64 exact+syndrome hard decisions at cap 1; 49 iteration-0 + 15 iteration-1; posterior tolerance failed (SINGLE max ~0.500, TREE max ~0.400 vs 1e-10) while MAP agreement passed; RSS null is telemetry unknown (WSL venv lacks psutil) with no measured breach and no `<2GiB` PASS claimed. `CONFIRMED`/`PARTIAL`, FER/leakage/key-rate/CAL-recovery/qualification/R1d/G2-permission/broad NB-LDPC conclusions are all refused.

**Context**: `D7_B_RESULT_ACCEPTANCE_R2.md` states packet §3's twelve points without reinterpretation; pre-result review `D7_B_PRE_RESULT_REVIEW_PASS_R2`; root read twice with identical names/sizes/mtimes (111/44743/1008/80/449); zero decoder calls, zero root/production edits, no VOID reads.

**Consequences**: `next_gate` → `D7_B_EARLY_EXIT_SOFT_BELIEF_AUDIT` (zero-decoder soft-belief audit R1 next). All authorizations stay false; R1d/G1/G2 unauthorized; no push.

## 2026-09-10 D7-B early-exit soft-belief audit classification + independent review PASS (next route interface correction)

**Decision**: Classify the early-exit soft-belief evidence as `D7_B_MIXED_METRIC_AND_INTERFACE_DEFECT` (primary) + `D7_B_RSS_TELEMETRY_DEPENDENCY_GAP` (secondary); independent review `D7_B_EARLY_EXIT_SOFT_BELIEF_AUDIT_REVIEW_PASS`.

**Context**: `D7_B_EARLY_EXIT_SOFT_BELIEF_AUDIT_R1.md` (E01–E12, zero decoder calls) with one review-§4 transcription correction (E06: 25 tractable it0 rows + 4 TREE PAIR it1 rows at 0.00689, total failures 29 unchanged; E05 stratification already correct); review `D7_B_EARLY_EXIT_SOFT_BELIEF_AUDIT_REVIEW_R1.md` re-verified 49/15 partition, v35 it0 return path, all consumers, and I1/I2/I3 split; R2 root five files unchanged; terminal stays `D7_B_RESOURCE_OVERRUN`.

**Consequences**: `next_gate` → `D7_B_LAYER_INTERFACE_CORRECTION_PROPOSAL` (before D7-C) per §8 mixed/interface mapping. All authorizations stay false; R1d/D7-C/D/G1/G2 unauthorized; no push.

## 2026-09-11 D7-B layer-interface proposal PASS + D7-C bidirectional-oracle freeze/implementation/Pre-EXECUTE (no execution)

**Decision**: Accept `D7_B_LAYER_INTERFACE_CORRECTION_PROPOSAL_PASS_D7_C_NONBLOCKING` (OpenSpec `v72p2d7-layer-interface-belief-provenance` + `D7_B_LAYER_INTERFACE_CORRECTION_PROPOSAL_R1.md`, commit `86f6baf6`): preferred alternative A exposes a `belief_provenance` enum `PRIOR_ONLY`/`CHECK_UPDATED`/`WARM_START_UNSPECIFIED` and makes cross-layer APP consumers fail closed unless `CHECK_UPDATED`; interface implementation is mandatory before any sequential/alternating/joint cross-layer APP route but not before D7-C; no historical result is reinterpreted; no v35 stopping change. Accept the D7-C R1+A1 freeze and its reviews (`D7_C_IMPLEMENTATION_REVIEW_PASS`, 0 rework / 20 tests; `D7_C_PRE_EXECUTE_REVIEW_PASS_AWAITING_EXPLICIT_AUTHORIZATION`).

**Context**: D7-B documented next route `D7_C_BIDIRECTIONAL_ORACLE_PACKET_FREEZE_INTERFACE_REWORK_DEFERRED`; consumer inventory 22 production/interface `final_beliefs` entries + V64 runner extension, sibling `nonbinary_v10_fftqspa.py` excluded. D7-C commits `0c304875` / `391fc6b0` / `ca00b234` plus a separately committed Pre-EXECUTE review (SHA not recorded here). Accepted H03 estimator `d5.prepare_model_f_prior_candidate` / `build_f_model_concentration` (`LAMBDA_STAR=137.3823795883264`, per-Bob-column total concentration); `prepare_model_f_prior` / `build_f_model` rejected (`LAMBDA_APPLICATION_CONTRACT_DEFECT`, per-cell pseudocount). Frozen matrix: n=64, seeds `2026091300..2026091315`, f `[1.0,1.2]`, L1 rows 49/59, L2 rows 43/52, D5-native mothers 49/2026090501 + 43/2026090502, 128 calls, budgets 120/1500/1800+30 s / <2 GiB, six scalar files, four direct `J` priors, no cross-layer belief flow.

**Consequences**: D7-C NOT authorized and NOT executed; all authorization false, no UUID, no `workspace/d7_c_bidirectional_oracle_*` root; D7-B R2 root `c605d1e6-8577-4c52-a865-12500fc8c964` immutable; R1d paused; G1/G2 unauthorized. `next_gate` `D7_C_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`; parallel state `LAYER_INTERFACE_IMPLEMENTATION_DEFERRED_BEFORE_CROSS_LAYER_APP`. Mandatory Pre-RESULT review before any result publication; no push.

## 2026-09-11 D7-C result acceptance (bounded bidirectional-dependence diagnostic; route to D7-D schedule discriminator)

**Decision**: Accept the immutable D7-C run and independent review as `D7_C_RESULT_ACCEPTED_BIDIRECTIONAL_DEPENDENCE_DIAGNOSTIC` per main-thread adjudication §0 of `D7_C_ACCEPT_D7_D_SCHEDULE_FREEZE_IMPLEMENT_PRE_EXECUTE_R1_TASK_PACKET.md`, recorded without reinterpretation in `D7_C_RESULT_ACCEPTANCE_R1.md`. Accepted scope: 128/128 frozen single-layer calls completed, finite and internally coherent; exact and syndrome agreed on all calls, 43/128 exact; f=1.0 L1 marginal/oracle `0/16 -> 10/16`, L2 `0/16 -> 1/16`; f=1.2 L1 `3/16 -> 16/16`, L2 `0/16 -> 13/16`; f=1.2 has `STRONG_ORACLE_LIFT` in both layers; run terminal `D7_C_BIDIRECTIONAL_DEPENDENCE` accepted as a bounded mechanism-classification result; no crash/nonfinite/resource/watchdog issue, RSS known and below 2 GiB; D7-C did not consume cross-layer returned beliefs and is not affected by the deferred D7-B APP-interface implementation. Route the next mainline stage to D7-D (isolate schedule only; do not implement alternating/joint BP).

**Context**: Scientific interpretation ceiling held verbatim — accepted that true other-layer symbols materially improve recovery under the frozen priors, matrices, decoder, disclosures, n=64 and 16 paired blocks; NOT accepted that an implementable alternating/joint decoder can generate that information, bootstrap from marginal priors, achieve FER, improve leakage/key rate, qualify the code, or generalize beyond this matrix; f=1.0 L2 remains effectively unrecovered even with oracle (1/16). Immutable evidence: sole UUID/root `94c0ea15-a786-4cb8-a991-6fec521cccae` (six files, zero subdirs, 282/23599/2709/1130/362/728 B), lifecycle authorize `b07b5441` → one invocation → revoke `d3bd3c8b` → result `b4ba2896`, independent Pre-RESULT `D7_C_PRE_RESULT_REVIEW_PASS_R1`, verifier `VERIFY_OK {'ok': True, 'problems': [], 'records': 128, 'terminal': 'D7_C_BIDIRECTIONAL_DEPENDENCE'}`. Four 2×2 paired counts (oracle_only/marginal_only/both/neither per stratum): f=1.0 L1 `10/0/0/6`, f=1.0 L2 `1/0/0/15`, f=1.2 L1 `13/0/3/0`, f=1.2 L2 `13/0/0/3` (each sums to 16; no `marginal_only` pair anywhere). Resources: outer wall `33.743` s, stored wall `32.631` s, max call `0.439` s, RSS `105172992` B, exit 0, timeout-124 false.

**Consequences**: `next_gate` → `D7_D_SCHEDULE_DISCRIMINATOR_PACKET_FREEZE`. D7-D is a readiness stage only — no D7-D root/UUID, no alternating/joint bootstrap, no FER/leakage/key-rate/CAL/qualification/promotion claim, and layer-interface implementation remains deferred and mandatory before any cross-layer APP route. All authorizations stay false; R1d/G1/G2 unauthorized; D7-C and D7-B roots immutable; no push.

## 2026-09-11 D7-D schedule-discriminator freeze/implementation/certification acceptance (readiness only, awaiting explicit authorization)

**Decision**: Accept the D7-D schedule-discriminator freeze, implementation, and flooding certification as READINESS ONLY, recorded with `D7_D_IMPLEMENTATION_REVIEW_PASS` and `D7_D_PRE_EXECUTE_REVIEW_PASS_AWAITING_EXPLICIT_AUTHORIZATION` (commit `727bca7a`; pre-execute review doc uncommitted at review time). Neither review verdict grants authorization, generates a UUID, or runs anything.

**Context**: OpenSpec `v72p2d7-gf32-schedule-discriminator` + prereg/execution packet committed `3a05899`; discriminator module `v72p2d7_gf32_schedule_discriminator.py` + tests + runner `scripts/v72p2d7_gf32_schedule_discriminator.py` + flooding certification doc committed `43f07186`. Frozen matrix: 128 D7-C identities × schedules `[ROW_LAYERED, FLOODING]` = 256 calls, `call_idx` `2k-1`/`2k`, identical non-schedule inputs within each pair. Certification/reviews: F01–F08 flooding certification all PASS; S01–S22 all PASS (30-test suite). Regression scope: D7-A 14 / D5 165 / v35 25 green; D7-B scoped 29 green; D7-C raw 19 passed with the stale pre-execution `test_c19` invariant non-blocking (S20 scoped deselection; refresh as a separate scoped change). Environment unchanged (Python 3.12.3 / NumPy 2.4.4 / GNU timeout 9.4; venv-on-PATH adapter carry-forward).

**Consequences**: `next_gate` → `D7_D_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. All authorizations false; no D7-D root/UUID; the 256 scientific calls remain unauthorized; layer-interface implementation still deferred and mandatory before any cross-layer APP route; R1d/G1/G2 unauthorized; no push. No FER/leakage/key-rate/qualification/promotion implications.

## 2026-09-11 D7-D bounded result acceptance (schedule effect inconclusive; route to BP provenance Alternative A)

**Decision**: Accept the reviewed D7-D run (UUID `64660d16-397d-4ef3-8454-3066d27c12c7`) as `D7_D_RESULT_ACCEPTED_SCHEDULE_EFFECT_INCONCLUSIVE` per §0 of `D7_D_ACCEPT_BP_INTERFACE_READINESS_R1_TASK_PACKET.md`, recorded without reinterpretation in `D7_D_RESULT_ACCEPTANCE_R1.md` (Phase-A A01 independent recomputation: 0 discrepancies). Accepted facts: 256/256 paired calls completed; row-layered exact `43/128`, flooding exact `40/128`, layered-only `3`, flooding-only `0`, both `40`, neither `85`; no crash/nonfinite/watchdog; stored terminal `D7_D_SCHEDULE_EFFECT_INCONCLUSIVE`; independent Pre-RESULT `D7_D_PRE_RESULT_REVIEW_PASS_R1`; budgets passed. The three layered-only identities are 26 (1.0/2026091306/L1_ORACLE_U2), 46 (1.0/2026091311/L1_ORACLE_U2) and 101 (1.2/2026091309/L1_MARGINAL).

**Context**: The frozen matrix establishes no preregistered flooding or layered advantage; `43 vs 40` and the three layered-only pairs are reported, not promoted into a schedule-superiority claim; schedule choice is not supported as the dominant explanation of the current failures. D7-C's accepted bidirectional oracle dependence remains the stronger route evidence but does not prove that alternating/joint BP can bootstrap. No FER, leakage, key rate, qualification, promotion, general schedule equivalence or general NB-LDPC conclusion. Eight strata labels (no advantage stratum): `EXACT_TIE_LOW, MIXED_SCHEDULE_EFFECT, EXACT_TIE_LOW, EXACT_TIE_LOW, EXACT_TIE_LOW, EXACT_TIE_HIGH, EXACT_TIE_LOW, EXACT_TIE_HIGH`. Immutable root: seven files 3164/57659/17690/1777/1546/455/290 B, whole-file read twice identical; lifecycle authorize `7a3f0d92` → one invocation → revoke `eba385bb` → result `63a69f57`; verifier `VERIFY_OK {'ok': True, 'problems': [], 'records': 256, 'terminal': 'D7_D_SCHEDULE_EFFECT_INCONCLUSIVE'}`; outer wall 67.178 s, stored wall 65.945 s, max call 0.436 s, RSS 105304064 B. R1d becomes `PAUSED_OPTIONAL_LOCAL_CONFIRMATION_NOT_MAINLINE_GATE`; G1/G2 unauthorized; old D5/D6 checkboxes are historical accounting, not gates to dimension generalization.

**Consequences**: `D7_D_SCHEDULE_EFFECT_INCONCLUSIVE` has no frozen automatic successor; this ruling selects Alternative A (explicit belief provenance plus fail-closed cross-layer consumers) as the next mainline action. `next_gate` → `BP_INTERFACE_PROVENANCE_IMPLEMENTATION`. No forced sweep (Alternative B), warm-start mechanism, alternating/joint decoder or scientific decoder run is authorized. Dimension/bw expansion waits for a working provenance-safe fixed-dimension mechanism and, for more than two layers, a separate mathematical/leakage contract. All authorizations stay false; D7-D/D7-C/D7-B roots immutable; no D7-E work; no push.
## 2026-09-11 — Authorize NB-Polar Phase 3-R1 construction recovery

The user authorized the new heavy autonomous execution packet at
`.workbuddy/queue/NBPOLAR-PHASE3-R1-CONSTRUCTION-RECOVERY/`. The operator may
implement and iterate on TRAIN/DEV, then perform one fresh synthetic EVAL only
after a real independent reviewer-go PASS on the final frozen contract. The
procedure-invalid predecessor remains diagnostic only; seed 2026091203 is not
rerun or reused. Phase 4, Model-F, real data, promotion, commit, and push remain
closed.
## 2026-09-11 — Accept Phase 3-R1 as a bounded synthetic diagnostic

After independent Pre-RESULT review, accept the single fresh O3 analytic
synthetic EVAL at q32/N256, erasure eps=0.05, K45, seed 2026091213. It achieved
299/300 exact with one impossible failure at block 219, 300/300 initial-error,
and zero other/NaN failures. The result is `EVAL_ACCEPTED_DIAGNOSTIC`; it does
not open Phase 4 or support unique-cause, general-performance, Model-F,
real-data, leakage, key-rate, qualification, or promotion claims. The seed and
output root are frozen against rerun or overwrite.
## 2026-09-11 — Accept Phase 4-P0 prior contract; split P1 before CAL

Accept `formal-ir-nbpolar-phase4-p0` after independent reviewer-go PASS WITH
COMMENTS. The accepted contract uses per-Bob-column concentration smoothing,
explicit `[Alice,Bob]` axes and 5+5 integer-label packing, dense SymbolMetric,
six pure helpers, separated evidence streams and V-P0-01..12. To preserve
failure attribution, Phase 4-P1 covers only the pure adapter and synthetic
V-P0-01..07; CAL/DEV and decoder diagnostics move to a later separately
authorized packet. No implementation or data execution is authorized here.
## 2026-09-11 — Scope P3-T1-09 instead of hiding the Phase 4 prior export

P3-T1-09 accidentally applied its `.prior` text ban to package `__init__.py`,
while accepted Phase 4-P0 design §7 required that public export. Choose option
(a): retain the `.prior` ban on `synthetic.py` and `construction.py`; retain all
legacy/protocol/result bans on the original three-file set; permit the explicit
Phase 4 API export from `__init__.py`. Reject import-spelling evasion and API
relocation. After the change, the combined Phase 1-4-P1 suite passed 66/66 and
independent focused review passed with comments. P1 advances only to
`IMPLEMENTATION_CANDIDATE`; CAL/decoder/P2 remain closed.
## 2026-09-11 — Accept Phase 4-P1 synthetic prior adapter

Independent reviewer-go returned ACCEPT on the P1 candidate after option (a)
resolved the P3 sentinel conflict. Promote P1 to
`IMPLEMENTATION_ACCEPTED_SYNTHETIC_ONLY` on the paired 66/66 full focused and
independent 11/11 decoder-free evidence. Acceptance covers the pure dense prior
adapter and synthetic V-P0-01..07 only. It does not cover CAL, Model-F, SC with
empirical priors, DEV/EVAL, FER, leakage, key rate, qualification or promotion.
P2 remains all-false and requires separate authorization.
## 2026-09-11 — Require copyable authorization text and isolate P2 before SC

Every WorkBuddy task now carries TASK_PACKET, PROMPT, AUTHORIZATION_PROMPT and
STATUS. At each authorization gate the main thread must paste the full grant in
chat and continue through adjudication and next-packet preparation. Phase 4-P2
is narrowed to one read-only validation of the accepted sibling CAL count
artifact against the P1 prior adapter. Empirical-prior SC decoding moves to P3
so artifact/schema/formula failures cannot be confused with decoder failures.
## 2026-09-11 — Retain P2 attempt 1 BLOCKED; route to Bob-axis recovery

P2's sole content attempt passed the accepted artifact loader and failed in a
new diagnostic expression `f3[u1,:,nz]`, producing `(32,1024)` against Bob
weights `(1024,1)`. Classify this as `BLOCKED(P2_DIAG_INDEX_ERROR)`, not an
artifact, prior-formula or decoder result. Preserve attempt 1/1 and absent
target. P2-R1 must use `f3[u1,nz_b,:]`, asymmetric shape tests and an
independent loop oracle before a newly authorized single attempt. P3 closed.
## 2026-09-12 — Accept P2-R1 CAL prior validation; keep SC separate

Accept the reviewed P2-R1 result only as validation of the accepted CAL count
artifact through the P1/P2 prior-table formulas, axes, support and entropy
chain. Evidence: 88 tests, one consumed R1 read, formula error 0,
normalization/oracle errors below 3e-14/7e-15 and chain discrepancy 8.88e-16.
H1/H2/chain and CE are CAL-resubstitution descriptions, not held-out
performance. Prepare P3 as a separate model-sampled P1-prior-to-SC interface
qualification; no real data, reconciliation or performance claim.

## 2026-09-13 — Accept Phase 4-P3 interface candidate; freeze static protocol

Accept the independently reviewed P3 result as
`EMPIRICAL_PRIOR_SC_INTERFACE_ACCEPTED`: the accepted CAL-derived P1 metric is
numerically consistent with q-ary SC and an independent tiny exhaustive oracle
under model-sampled data. The sole artifact attempt and seed 2026091316 are
consumed; the five-file root is immutable. The 48/328 exact count is not a FER,
construction, disclosure-pattern or performance result.

Freeze `formal-ir-nbpolar-phase5-static-protocol` and the paired WorkBuddy
packet as all-false. Phase 5 starts with one static synthetic protocol, actual
GF32 disclosed values, full-label reconstruction, one final Toeplitz tag and
independent disclosure recount. No Phase 5 action is authorized by this
decision.

## 2026-09-13 — Ratify P3 Stage B B5 attribution precedence; stale MVP freeze superseded; P3 candidate returned

**Decision**: Ratify the implemented B5 earliest-layer attribution precedence as
the frozen classifier rule: `artifact_adapter_support` > `normalization` >
`disclosure_contradiction` > `SC_numeric` > `unattributed` >
`expected_under_disclosure` > `SC_decision`. This resolves Pre-EXECUTE review
F-1, whose NEEDS_CHANGES finding was that freeze-v2 §4's precedence text was the
reverse of `classify_stageb_failure` for the last three categories; the repair
was docs/comments-only and re-reviewed to PASS (R1), with no frozen value
changed.

**Context**: The stale draft
`openspec/changes/formal-ir-nbpolar-mvp/P3_STAGEB_FREEZE.md` is superseded by the
queue `P3_STAGEB_FREEZE.md` v2/Rev 2a: the stale draft's `--case`/`--mask`
runner never existed, its target-output layout conflicted with TASK_PACKET
§Output, and its `MASTER_SEED 20260911` is an earlier official (oracle) seed,
not the Stage B diagnostic seed 2026091316. The single authorized Stage B
artifact-content attempt was consumed (1/1) and returned
`EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE` with independent Pre-EXECUTE PASS (R1)
and Pre-RESULT PASS_WITH_COMMENTS; evidence root
`.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/`.

**Consequences**: Acceptance is NOT granted by this entry; it remains owned by
the main thread. The candidate is an interface-consistency label only — not FER,
reconciliation, leakage, key-rate, construction-K or real-data evidence. No
Phase 5 authorization, no promotion, no commit/push.

## 2026-09-13 — P5 static protocol returned as candidate (not accepted); R1/R2 rulings

**Decision**: Ratify the two Phase 5 static-protocol rulings recorded in
`P5_FREEZE.md` Rev 1 §0 and implemented in `protocol.py`:

- **R1 (disclosure orientation)** — the static DISCLOSED set is
  `construction.analytic_order(0.05, 256)[:45]`, the 45 *highest-risk*
  coordinates; SC reconstructs the remaining 211. This supersedes the
  `TASK_PACKET.md` phrase "information set … disclose its complement" and the
  corresponding `design.md` sentence. It matches `docs/nbpolar/ARCHITECTURE.md`
  ("Alice sends the actual values `U[D]`") and the accepted Phase 3 point
  `evaluate_blocks(..., k=45)`.
- **R2 (label domain)** — the physical label vector is the 10-bit single-layer
  embedding `label_j = 32 * x_hat_j` with low half constant zero; the
  verification message domain is `10*N = 2560` bits and the per-block Toeplitz
  seed is `2560 + 63 = 2623` public-control bits.

**Context**: The Phase 5 packet (`NBPOLAR-PHASE5-STATIC-PROTOCOL`) implemented a
static synthetic reconciliation protocol and executed its single preregistered
300-block development gate (exit 0) under run seed 2026091317 and public Toeplitz
master seed 2026091318. Result: 300/300 exact, `undetected` 0, recount mismatch
0, 11/11 hard gates true, one-sided 95% Wilson lower bound 0.9910621278248719
(threshold 0.90), average key-dependent disclosure 289.0 bits/block
(< `10*N` = 2560). Evidence root
`.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate/`.
Independent Pre-EXECUTE review PASS and Pre-RESULT review PASS_WITH_COMMENTS;
mandatory closeout item R-1 (`STATUS.yaml attempts_used 0 → 1`) completed.

**Consequences**: The operator returned the candidate label
`STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE`; **acceptance is NOT granted by this
entry** and remains owned by the main thread. The single attempt 1/1 is consumed
and the five-file root is frozen — no rerun, no retuning, no seed change. The
candidate is a synthetic development signal only: not real-data FER, leakage
efficiency, reconciliation, key rate, qualification or promotion. No Phase 6
authorization, no commit/push.

## 2026-09-13 — Accept Phase 5 static synthetic protocol development gate

Accept the independently reviewed candidate as
`STATIC_PROTOCOL_DEVELOPMENT_ACCEPTED`. At the frozen
GF32/N256/epsilon0.05/K45 point, the sole 300-block attempt produced 300 exact
outcomes, zero undetected or other terminal failures, Wilson one-sided 95%
lower bound 0.9910621278248719, and independently recounted 289 key-dependent
plus 2623 public-control bits per block. The physical label is `32*x_hat`; the
Toeplitz message domain is 2560 bits.

This is a synthetic static-protocol development signal, not real-data FER,
leakage efficiency, key rate, qualification, promotion or adaptation evidence.
Attempt 1/1 and seed 2026091317 are consumed and the five-file root is
immutable. Phase 6 remains false; its next action is contract freeze, not
execution.

## 2026-09-13 — Freeze Phase 6 fixed incremental successor

Freeze a single successor schedule `K=(29,33,37,41,45)` on the accepted
GF32/N256/erasure0.05 point. A tag match accepts the current level; mismatch
may only discard it and enter the immediately next frozen level with a
restart-from-scratch SC call. The tag cannot rank candidates, carry decoder
state, skip levels or change decoder parameters. Each coordinate is disclosed
once and every tag/public seed/control invocation is counted.

The paired 300-block development criterion requires zero undetected, at least
285 exact, Wilson lower bound at least 0.90, and at least 5% lower average
key-dependent disclosure than an in-run static K45 arm on identical blocks.
OpenSpec and WorkBuddy four-file packet are prepared all-false; no Phase 6
action or execution is authorized by this freeze.

## 2026-09-13 — Accept Phase 6 strict-stop negative; choose decode-reject advancement

Accept the sole paired strict-stop result as
`FIXED_INCREMENTAL_NEGATIVE_ACCEPTED`: incremental 271/300 and Wilson 0.87156
fail the frozen recovery gates despite 28.17% lower average disclosure. All 29
incremental failures are level-0 `ImpossibleDisclosedValueError`; independent
review classifies this as valid scheduler science, not an SC defect. Attempt
1/1 and seed 2026091340 are consumed; the five-file root is immutable.

Choose successor option (a). At K<45 an impossible-disclosure decode creates no
candidate/tag, counts one public feedback request, advances one fixed level and
restarts SC. At K45 it remains terminal decode-failed. K, construction, SC,
thresholds and old evidence do not change. P6-R1 OpenSpec and four-file packet
are frozen all-false awaiting explicit authorization.

## 2026-09-13 — Phase 6-R1 decode-reject advancement returns candidate (not accepted)

**Decision**: Return the Phase 6-R1 decode-reject-advance result as the candidate
`DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE`. This is a candidate, not an
acceptance; no task box is checked and acceptance remains a main-thread decision.
No tuning, seed change, threshold change or rerun.

**Context**: One frozen three-arm paired 300-block development gate executed once
(exit 0) with static K=45, strict-stop and R1 arms on identical blocks
(300/300 paired_match). Static: 298/300 exact, avg 288.573333 key-dependent
bits/block. Strict-stop: 280/300 exact, 20 `ImpossibleDisclosedValueError`
failures, avg 214.253333. R1: 298/300 exact, 2 failures, avg 220.506667 —
23.59% below static (integer rule 6615200 <= 8224340), Wilson one-sided 95% LB
0.9800565738801275, 32 rejections over 20 blocks (histogram `{0:20,1:7,2:3,3:2}`).
R1 vs strict-stop rescue identities: rescued 18 / persisted 282 / regressed 0 /
other 0. All 18 frozen gates true; transcript mismatch 0/0/0; truth leak 0;
nonfinite 0; union bound 5.1228552649940085e-17 over 945 tag invocations.

**The unique semantic delta**: the only change from the accepted Phase 6 schedule
is that a non-final (K<45) impossible-disclosure rejection is treated as
reject-and-continue — no candidate/tag at that level, exactly one public feedback
request, next fixed increment disclosed, and SC restarted from the original
metric with no carried state. At the terminal K=45 level the same error remains
fail-closed `decode_failed`, as do all other exceptions and nonfinite marginals.
An intermediate rejection is never a success or a final outcome bucket.

**Alternatives considered**:
- Tune K/thresholds or rerun to improve the numbers: rejected — forbidden by the
  freeze; attempt 1/1 and run seed 2026091350 are consumed.
- Gating on the rescue identities: rejected — they are reported, not thresholded,
  matching the freeze (§9).

**Consequences**: Independent Pre-EXECUTE PASS and Pre-RESULT PASS are recorded;
`attempts_used: 1`; `next_gate: MAIN_THREAD_ACCEPTANCE`. Evidence root
`.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/`
(five scalar-only files). The result is a synthetic paired development signal
only — not real-data FER, leakage efficiency, key rate, qualification or
promotion evidence. No commit or push.

## 2026-09-13 — Accept Phase 6-R1; pause Phase 7 for two-layer rate feasibility

Accept the sole R1 three-arm result as
`DECODE_REJECT_ADVANCE_DEVELOPMENT_ACCEPTED` within its frozen single-layer BEC
synthetic scope. The 18/18 gates, 298/300 recovery, 23.59% disclosure saving,
zero undetected/regressed outcomes and independent Pre-RESULT PASS support the
protocol-semantic acceptance. Attempt 1/1 and seed 2026091350 remain consumed.

Do not interpret the acceptance as reconciliation efficiency or two-layer
evidence. Phase 5/6 used `label=32*x_hat` with a constant-zero low half, while
the roadmap's oracle-L2 and candidate-conditioned operational L2 paths have not
been exercised by those gates. The planning documents also lacked a numerical
NB-Polar `f<=1.3` gate.

Pause Phase 7/SCL. Freeze successor
`formal-ir-nbpolar-phase6-r2-two-layer-rate-feasibility`: a decoder-free,
full-precision, per-source BEC-surrogate sensitivity across N=2^8..2^18,
explicit two-layer FER-budget allocations, tag-inclusive leakage and f. A
scratch recomputation reproduced the single-layer N256/epsilon0.05 K43
calibration and placed the f≈1.3 crossing near 2^17–2^18, but this is only a
planning estimate. The successor must independently reproduce it and must not
claim that BEC is a rigorous empirical-channel lower bound.

## 2026-09-13 — Phase 6-R2 two-layer rate-feasibility candidate returned (pending main-thread acceptance)

Decoder-free two-layer BEC surrogate feasibility study returned candidate
`TWO_LAYER_RATE_FEASIBILITY_CANDIDATE` from
`.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/`
(`two_layer_rate_sensitivity.json`, `R2_REPORT.md`, `OPERATOR_RETURN.md`).
Inputs are the frozen per-source TRAIN `nll_u1`/`nll_u2` entropies from
`docs/v49_distribution_tables/v49_train_val_hold_nll.csv` (1M
0.024280547/0.776757278; 1p5M 0.025199497/0.800366555; 2M
0.025662049/0.806900673), mapped `epsilon_l=H_l/5`.

K43 calibration (N=256, epsilon=0.05, budget 1e-2) reproduced: residual
`sum(z[43:])=0.0080281681532746`, K=42 residual `0.010563784528611946` (>1e-2).
All 66 rows (N=2^8..2^18 x 3 sources x 2 allocations) are complete and finite.
First `f<=1.3` crossing is 2^18 on all six axes; log2-linear interpolation
places the exact crossing at 2^17.20-2^17.36, matching the earlier scratch
"near 2^17-2^18" estimate. `f=leakage_bits/nH` with
`leakage_bits=5*(K1+K2)+64` (one 64-bit tag) and `nH=N*(H1+H2)`; tag-free
`f_no_tag` reported alongside, `f > f_no_tag` in every row.

L2 audit gap: code and docs confirm oracle-L2 (true-L1-conditioned) and
operational candidate-L2 SC have never executed; only the single-layer L1
high-plane path (`label=32*x_hat`, low half constant zero) has ever entered SC.
Successor prerequisites (decision output only, nothing implemented): L2 prior
extraction per the P0 contract (P2_true/P2_hat) with two-stage restart SC; a
paired two-layer development gate under the same accounting discipline; and
empirical construction plus a scalable decoder (e.g. FWHT) for N>=2^17.

These BEC figures are a surrogate planning estimate only, not real-channel
performance, not a rigorous lower bound, and not decoder evidence. No SC call,
no artifact/parquet/TTBin read, no sampling, no attempt/seed consumed
(`attempts_allowed/used` 0/0), old evidence roots untouched, no commit/push.
Independent result review is PASS_WITH_COMMENTS (66/66 rows recomputed with
zero difference); acceptance remains a main-thread decision.

## 2026-09-13 — Accept Phase 6-R2; restore operational L2 before scaling

Accept `TWO_LAYER_RATE_FEASIBILITY_CANDIDATE` as
`TWO_LAYER_RATE_FEASIBILITY_ACCEPTED`. Independent recomputation matched all
66 rows, K43 calibration, leakage/f arithmetic and the six first-grid crossings
at N=2^18. The L2 call-site audit is also accepted: neither oracle-L2 nor
candidate-conditioned L2 has entered SC execution.

Scope remains a BEC-surrogate planning estimate only. The 2^17.20–2^17.36
interpolation is not a measured sufficient N, a rigorous lower bound, decoder
FER, achieved reconciliation efficiency or empirical-channel evidence.

Do not jump directly to N=2^18 optimization or SCL. Restore the omitted Phase-4
dependency first with `formal-ir-nbpolar-phase4-p4-two-layer-operational-sc`:
an injected-table, bounded N<=256 causal path from L1 SC hard candidate through
P2_hat and fresh L2 SC, paired against an isolated P2_true oracle arm. This
successor measures wiring and cross-layer propagation only; empirical
construction and scalable/FWHT decoding remain separate later changes.

## 2026-09-13 — Phase 4-P4 two-layer operational SC interface candidate returned (pending main-thread acceptance)

**Decision**: Record the single authorized Phase 4-P4 two-layer operational SC
paired synthetic interface gate (exit 0) as candidate
`TWO_LAYER_OPERATIONAL_SC_CANDIDATE`, pending main-thread acceptance. This is a
candidate, not an acceptance, and makes no real-data FER, leakage-efficiency,
key-rate, qualification, promotion or `f<=1.3` claim.

**Context**: The gate executed once on the frozen point via
`.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/` (Q32/N=256,
epsilon1=0.05/epsilon2=0.20, K1=45/K2=110, 96 paired blocks, run seed
2026091360, public Toeplitz master 2026091361, output root
`two_layer_operational_sc_gate/`). It implements Bob-only P1 -> L1 SC hard
candidate -> candidate-conditioned P2_hat -> fresh L2 SC -> `low_hat+32*high_hat`
-> one final 64-bit tag, paired against a strictly isolated true-L1 oracle arm.

**Result**: 96/96 paired coverage; both arms' L2 invoked 96/96;
PRIOR_ONLY 96 / CANDIDATE_CONDITIONED 96 / ORACLE_CONDITIONED 96; 13/13 hard
gates true; truth-leak 0; nonfinite 0; undetected/decode_failed/resource_abort
all 0; operational exact 26/96 vs oracle exact 44/96 (report-only, no
threshold); accounting exact per fully invoked arm 839 bits (225+550+64),
key-dependent total 161088, public control 503616 (192 tags x 2623), 576
transcript events, recount mismatch 0; wall 10.154709 s; peak RSS 144609280 B;
192 tests (12 new + 180 predecessor) pass. Attempt 1/1 and run seed 2026091360
are consumed; master 2026091361 is public control.

**Frozen-model consequence**: the independent-layer injected model makes the
table-derived P2 numerically independent of the L1 high symbol
(`max |P2[u1=0]-P2[u1=1]| = 7.771561172376096e-16`, pure float64 rounding), so
the paired comparison is degenerate at the metric level. The report-only
`oracle_candidate_divergence` count 34/96 = `not np.array_equal(P2_hat,
P2_true)` (`two_layer.py` `_candidate_divergence`), i.e. ULP-level bitwise
inequality between the candidate- and oracle-conditioned arrays, not a semantic
metric-level L1->L2 dependence. The gate's value is therefore causal
wiring/provenance/isolation/accounting discipline plus label-level propagation
(the five high bits of the label), not a performance delta.

**Seed-overlap adjudication**: `2026091360`/`2026091361` were used only as P6-R1
**test-local** seeds (not consumed official streams); the distinct
`nbpolar-p4-toeplitz-seed` namespace prevents tag-stream collision and no
accepted evidence depends on them. Pre-EXECUTE adjudicated the overlap
acceptable.

**Alternatives considered**:
- Rerun or tune seeds/table/K/thresholds after the run: rejected — forbidden by
  the freeze; attempt 1/1 is consumed and no tuning or rerun occurred.
- Report a metric-level L1->L2 dependence: rejected — the frozen model is
  layer-independent and the divergence flag is ULP-level and report-only.

**Consequences**: Independent Pre-EXECUTE PASS and Pre-RESULT PASS_WITH_COMMENTS
are recorded (`next_gate: MAIN_THREAD_ACCEPTANCE`). No commit or push; no
qualification or promotion. Empirical construction, scalable/FWHT decoding,
real-data FER and Phase 7 remain separate, later, separately authorized changes.

## 2026-09-13 — Accept P4 interface; propose explicit probe tier

Accept P4 as `TWO_LAYER_OPERATIONAL_SC_INTERFACE_ACCEPTED`: all 13 wiring,
provenance, isolation and accounting gates passed. Do not promote operational
26/96, oracle 44/96 or divergence 34/96: the independent-layer model makes P2
vary across L1 only at 7.77e-16 rounding scale.

Propose Tier X non-claim probes while retaining Tier Y one-shot decisions.
Tier-X results may calibrate a future gate but cannot strengthen old evidence.
Freeze `NBPOLAR-X01-PROBE-TIER-BOOTSTRAP` all-false; neither the workflow change
nor its four five-seed probe families are active before explicit authorization.

## 2026-09-13 — Activate two-tier workflow; route X01 to X02, not Gate A

The Tier-X/Tier-Y and delta-successor rules are implemented in AGENTS.md §10.4
and apply project-wide. X01 is closed as a reviewed non-claim probe. Its five
seeds show low P5/R1 dispersion and materially larger P4 dispersion, but do not
upgrade prior accepted evidence.

Reject an additional R1-vs-static Tier-Y Gate A as low information: the route
already has a frozen gate and the probe resolves its dispersion. Defer P4 Gate
B because the current dependent model's oracle arm is only about 42/96 exact.
Next is the compact X02 Tier-X search over frozen dependence profiles and K1/K2
to identify an informative high-oracle operating point without a pass verdict.

## 2026-09-13 — X02 selects the hard-conditioning penalty discriminator

X02 is a reviewed Tier-X probe, not accepted scientific evidence. Its frozen
grid identifies strong/K1=45/K2=140 as the lowest-disclosure strong point with
oracle 96/96 and operational 47/96 across the three probe streams. Preserve the
execution-body provenance correction in the successor rather than treating the
logged pre-fix body as byte-faithful.

Freeze Phase 4-P5 as a negative mechanism discriminator with 384 new paired
blocks. Use four paired cells; do not apply Clopper-Pearson to a difference of
marginal rates. Confirmation requires oracle>=365/384, operational-only=0 and
the one-sided exact lower bound for the oracle-only event above 0.30. This can
stop direct scaling of hard conditioning, but cannot establish real performance.

## 2026-09-13 — Phase 4-P5 hard-L1 conditioning penalty returned as candidate (not accepted)

**Decision**: Record the Phase 4-P5 gate result as a candidate only. At the frozen
strong dependent-L2 point (GF32, N=256, epsilon1=0.05,
`epsilon2(u1)=0.02+0.36*u1/31`, K1=45, K2=140), the single 384-pair paired gate
(exit 0) shows a material hard-L1 conditioning penalty: oracle exact 377/384 vs
operational exact 233/384, operational-only 0, `neither` 7, `oracle_only` X=144,
and the one-sided 95% exact lower bound `L=0.3338842736427746 > 0.30`. All ten
integrity gates pass. Persisted label `HARD_L1_CONDITIONING_PENALTY_CANDIDATE`.
Main-thread acceptance is pending and is not claimed here.

**Context**: The discriminator was frozen as oracle exact >=365/384,
operational-only == 0, and `L > 0.30`, with no binomial interval on the marginal
rate difference. Per-stream cells: 83/43/0/2, 72/55/0/1, 78/46/0/4. The first X
with `L > 0.30` is 131; X=144 is well inside the pass region. Independent
Pre-EXECUTE R0 returned `NEEDS_CHANGES` on a docs-only Blocking Issue B-1 (the
freeze/notes enumerated the public masters as `seed+1000` while the frozen
contract and module constant are `seed+10000`); repaired docs-only and closed by
R1 `PASS`. Independent Pre-RESULT review was `PASS_WITH_COMMENTS`; every number,
gate and the lower-bound root were independently recomputed from the five
persisted files.

**Consequences**: attempt 1/1 is consumed at the first gate L1 SC call (stream 0,
block 0); streams 2026091470..2026091472 are consumed and public masters
2026101470..2026101472 are public control. No rerun, seed/model/K/threshold change
or tuning. This is a synthetic single-point mechanism signal only — not real-data
FER, efficiency, leakage, key-rate, qualification or promotion evidence; the
operational numbers are interface diagnostics. Any scaling decision requires a
separate authorized change. No commit/push.

## 2026-09-13 — Phase 4-P6 adaptive hard-L1 gate BLOCKED on a gate-check defect (scientific gates true)

**Decision**: Record the Phase 4-P6 adaptive hard-L1 disclosure gate as
`BLOCKED(d1_exactly_nested_and_d2_disclosed_once)`. The persisted label is
`BLOCKED` even though all four scientific gates are true, because one of the
twelve integrity gates is `false`; the sole failing gate is diagnosed as a
**gate-check implementation defect** (class b), not a contract violation. The
failure root is preserved and no rerun/re-score/tuning is permitted in this
packet. Main-thread disposition is pending; this is not an acceptance.

**Context**: One authorized paired synthetic Tier-Y gate (exit 0) at the frozen
point GF32/N=256, `epsilon1=0.05`, strong dependent-L2, D1 `[45,60,72,112]`,
`K2=140`, five streams `2026091550..54` x 128 blocks (640 pairs; public masters
`2026101550..54`). Scientific gates 4/4 true: static exact 632/640, adaptive
exact 632/640, `adaptive_only=0`/`static_only=0`, `neither=8`, and the exact
integer leakage comparison `100*675,783 = 67,578,300 <= 85*847,360 = 72,025,600`
(20.2484% saving). Accounting: tags 640/942/1582, feedback 302, public control
4,149,888 bits, union bound 8.57603918436034e-17, transcript recount mismatch 0,
`undetected`/`decode_failed`/`resource_abort` all 0. Adaptive termination
`{45:403, 60:185, 72:39, 112:13}`. Wall 105.941485 s; RSS 394,567,680 B.
Planning-only f: static 2.4235, adaptive 1.9328. Tests 15 new + 216 total.
Independent Pre-EXECUTE = PASS; independent Pre-RESULT = PASS_WITH_COMMENTS,
with every number and 12+4 booleans independently recomputed.

**Root cause**: The gate at `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py:1342`
counts L2 events by `(block_id, arm)` while `block_id` is a per-stream index.
The runner loops blocks 0..127 inside each of five streams and the event id
omits `stream_seed`, so the 1,280 L2 events collapse onto 256 keys each counted
5; `all(count == 1 ...)` is spuriously false (the set-equality term still
passes). Under the frozen "D2 once per arm/block" contract the per-`(stream,
block, arm)` count is exactly 1 for all 640x2, so the **contract-correct gate
value is true**; had the check been keyed on the full identity the label would
have been `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`. The reviewer reproduced the
isolated false with a 2-stream probe and confirmed the focused suite never
exercises a multi-stream runner call.

**Preserved failure root / no-rerun**: Attempt 1/1 was consumed at the first
scientific SC call (stream 2026091550, block 0, static L1); streams and masters
are consumed. The output root
`.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
(the five files) plus the persisted `BLOCKED` label and failing gate are kept
byte-for-byte. No repair, rerun or re-score.

**Consequences**: The one requested main-thread decision is the disposition of
the BLOCKED result: accept the artifacts under the documented corrected gate
interpretation via a main-thread ruling paired with a successor fix keying the
D2 check on the composite `(stream, block, arm)` identity plus a multi-stream
test, or require a new authorization. This is synthetic N=256 development
evidence only — not real-data FER, efficiency, leakage, key-rate,
qualification or promotion; `undetected` is never merged with exact. No
commit/push.

## 2026-09-14 — Phase 4-P6R1 Δ successor: identity fix + read-only revalidation → candidate

**Decision**: Disposition the `NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1` BLOCKED
result through the Δ successor `NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX`: repair
the multi-stream transcript-event identity (and the D2-once gate grouping) and
read-only revalidate the original five P6 artifacts. All corrected gates are
true, so the successor returns candidate label
`ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`. This is a **candidate only**;
main-thread acceptance is separate. The original P6 evidence root and its
persisted `BLOCKED` label are preserved immutable, and no attempt, seed,
sample, rerun or decoder call is consumed.

**Context**: The P6 gate scored only one integrity gate false
(`d1_exactly_nested_and_d2_disclosed_once`) while all four scientific gates
were true; the independent P6 `PRE_RESULT_REVIEW.md` diagnosed the cause as a
gate-check implementation defect: the D2 count was keyed on `(block_id, arm)`
although `block_id` is a per-stream index (the five streams share block indices
0..127), collapsing 1,280 L2 events onto 256 keys each counted 5, so
`all(count == 1 …)` was spuriously false. Under the frozen "D2 once per
arm/block" contract the per-`(stream, block, arm)` count is exactly 1.

**R1 disposition (delta, no new science)**: code delta limited to event
identity (`stream_seed` + stream-qualified `frame_key`) and the D2-once gate
grouping by `(stream_seed, block_id, arm)` (+32/−6; no constant, decoder,
threshold, K, seed, accounting or schema change) plus one multi-stream
regression test (old `(block,arm)` multiplicities [2,2,2,2] → old gate false;
corrected gate true; missing/dup disclosures detected). Tests: focused 16
passed, full NB-Polar suite 217 passed. Read-only revalidation of the original
five files (`adaptive_l1_revalidate.py` → `revalidation.json`): 640 unique
`(stream_seed, block_index)` identities; 1,280 D2 arm-block obligations each
exactly 1; L2 disclosure total 1,280; all 12 integrity and 4 scientific gates
true after the sole correction (632/640 both arms; adaptive = static; cells
632/0/0/8; leakage 67,578,300 ≤ 72,025,600); the only difference vs the
persisted run is that one gate's `false → true`. Old-root sha256/mtimes
unchanged; `decoder_calls=rng_calls=tag_calls=attempts_consumed=0`.

**Alternatives considered**:
- Rerun/re-score the consumed P6 gate: rejected — the freeze forbids it and the
  failure root is preserved byte-for-byte.
- Rewrite the persisted `BLOCKED` label in place: rejected — the original
  result and its status history stay immutable; the corrected value is recorded
  only in the successor result.
- Treat the corrected gate as acceptance: rejected — R1 returns a candidate;
  main-thread acceptance is a separate step.

**Consequences**: Independent `INDEPENDENT_REVALIDATION_REVIEW.md` returned
PASS_WITH_COMMENTS (non-blocking notes: a narrative `+31` line count that is
actually `+32`; declarative rather than instrumented zero-call counters; an
anchor-based D2 recount). `STATUS.yaml` is
`ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE_PENDING_MAIN_THREAD_ACCEPTANCE`,
`result: ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`, `next_gate:
MAIN_THREAD_ACCEPTANCE`, `attempts_allowed/used: 0/0`,
`original_root_immutable: true`. This is synthetic N=256 development evidence
only — not real-data FER, efficiency, leakage, key-rate, qualification or
promotion; `undetected` is never merged with exact. No commit/push.

### 2026-09-14 — P6-R1 main-thread acceptance

Accepted as `ADAPTIVE_HARD_L1_DISCLOSURE_ACCEPTED`. Within the frozen synthetic
N=256 dependent-L2 point, adaptive `[45,60,72,112]` matched static K1=112 at
632/640 exact and reduced key-dependent disclosure by 20.2484%. The original
P6 `BLOCKED` root and status history remain immutable; acceptance belongs to
the attempt-free P6-R1 revalidation. This is not real-channel FER, efficiency,
key-rate, empirical-construction, scaling or promotion evidence. Next gate is
the X06 empirical-vs-BEC construction-order Tier-X probe.

### 2026-09-14 — Route target construction to V25 TRAIN population

Accept X07's earliest divergence as `POPULATION_SESSION_IDENTITY_1M`, not as a
scientific candidate. V49 and X06 entropy values describe different sessions
and populations, so X06 zero recovery cannot adjudicate construction order for
the V49 target channel.

Select V25 1M TRAIN counts with the fixed V49 floor-only support rule. Reject
for this purpose: tuning Model-F smoothing; using Model-F CAL as the target
construction law; treating X06 as evidence empirical construction is
ineffective; or stopping NB-Polar solely from this cross-population mismatch.

Freeze `NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION` as the next Tier-Y
gate awaiting explicit authorization. It tests whether pooled empirical
construction supports the fixed N=256 two-layer hard-candidate development
point. BEC is report-only; empirical is not required to beat it.

### 2026-09-14 — P7 target-population empirical construction gate CANDIDATE (not acceptance)

`NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION` executed its single
authorized 640-pair Tier-Y development gate once (exit 0) and returned the
persisted candidate label `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE` on the
accepted `POPULATION_SESSION_IDENTITY_1M` route (V25 1M TRAIN counts, not the
Model-F CAL artifact). Main-thread acceptance is pending; this is not an
acceptance.

- Target/support: source `1M` (`channel_counts.npz`, 25,166,822 B,
  `[Alice,Bob]` 1024x1024) via accepted `load_v25_channel_counts`;
  column-normalize + `1e-15` floor + column renormalize; `P1/P2` from accepted
  `derive_p1/derive_p2` under `A=32*U1+U2`; no lambda/backoff/tuning.
- Ratified entropy semantics: the frozen literals
  `0.02428054681872374 / 0.7767572780789994 / 0.8010378248977232` (V49 1M TRAIN
  `nll_*` columns) are the **raw-MLE in-sample population conditional
  entropies** (`H1 = sum_b p_b H(P1_raw)`, `H2 = sum_b p_b sum_u1
  P1_raw(u1|b) H(P2_raw)`), matched to `<= 4.5e-14` at `1e-12` tolerance; the
  floor-induced total-entropy change is a **separate** `<= 1e-9` guard (recorded
  `5.1600945738528026e-11`). The strict floored-table reading at `1e-12` is
  unsatisfiable; independent Pre-EXECUTE review item #1 ratified the raw-MLE
  reading and the floored entropies are reported but never gated against the
  literals.
- Construction/result: TRAIN `2026091650..52` x256, DEV `2026091660..64` x128 =
  640; orders frozen before DEV (min pairwise TRAIN-order Spearman L1
  `0.9973291943236439` / L2 `0.9950453479056992`; `orders_sha256`
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`);
  empirical exact **640/640**; BEC control exact 640/640 (report-only; both arms
  saturate, so this gate carries no empirical-vs-BEC discrimination); cells
  both 640 / empirical_only 0 / bec_only 0 / neither 0; one-sided 95% Wilson LB
  `0.9957903841321254`; 11/11 integrity + 3/3 scientific gates true; disclosure
  989 bits per fully invoked arm, totals 1,265,920 key-dependent / 3,357,440
  public / 1280 tags, recount mismatch 0; wall `132.523651 s`, peak RSS
  `383,832,064 B`.
- Consumption/no-rerun: the single artifact content read (1/1) and the single
  scientific attempt (1/1) were consumed at the first NPZ content open
  (`open_count 1`, no reopen/retry); no rerun, no retuning, no seed/order/K/floor/
  threshold change. Seeds `2026091650..52`/`2026091660..64` and masters
  `2026101660..64` are spent. Independent Pre-EXECUTE and Pre-RESULT reviews both
  PASS.
- Scope: synthetic N=256 V25-1M-TRAIN model-sampled development signal only — no
  held-out/real-frame FER, efficiency, key rate, scaling, qualification or
  promotion; `undetected` is never success; no commit/push. Next gate is
  main-thread acceptance.

### 2026-09-14 — Accept P7 target empirical construction; freeze P8 target-rate screen/confirm

Accept `TARGET_EMPIRICAL_CONSTRUCTION_ACCEPTED` within the frozen V25 1M TRAIN
model-sampled N=256 development scope. The accepted support rule is columnwise
MLE with fixed `1e-15` floor and renormalization. P7 showed stable pooled
empirical construction and 640/640 exact recovery at K1=45/K2=140 with all
gates true and both independent reviews PASS. Because the paired BEC control
also achieved 640/640, accept no empirical superiority or order-discrimination
claim. Do not extend this result to held-out/real FER, efficiency, key rate,
scaling, qualification, or promotion.

Freeze P8 as the next Tier-Y gate, awaiting explicit user authorization with
artifact read/attempt 0/1. P8 searches the frozen 35-point static rate grid
using SCREEN data and deterministic minimum-disclosure selection, then tests
the selected point once on disjoint CONFIRM streams; BEC remains report-only.
No adaptive schedule, N>256, FWHT/APP/SCL, real/EVAL data, commit, or push is
authorized.

### 2026-09-14 — Accept P8 selected static rate point; freeze P9 lower-boundary resolution

Accept `TARGET_EMPIRICAL_RATE_POINT_ACCEPTED` within the frozen synthetic
V25-1M-TRAIN model-sampled N=256 development scope. All 35 P8 SCREEN points
were eligible and deterministic selection chose K1=8/K2=80. Disjoint CONFIRM
achieved empirical 638/640 exact with one-sided 95% Wilson LB 0.9906013677,
all integrity/scientific gates true, zero undetected/nonfinite/resource abort/
truth leak, and exact transcript recount. Both independent reviews support
acceptance; the sole read/attempt was consumed without rerun or tuning.

This accepts feasibility, not a global minimum: (8,80) was the lower corner of
the frozen grid and all points passed, so P8 is left-censored. BEC 621/640 and
17 empirical-only cells remain report-only and do not establish general
superiority. Do not extend the result to real/held-out FER, efficiency, key
rate, scaling, qualification, promotion, adaptive operation, APP/SCL/FWHT.

Freeze `NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION` as the next Tier-Y
gate, awaiting explicit authorization with read/attempt 0/1. P9 extends SCREEN
to 56 points including both zero axes and the P8 anchor, selects the eligible
lexicographic minimum, and confirms once on disjoint streams. No eligible point
is a valid negative. P9 is the final N=256 static-rate localization gate before
the route choice between adaptive target-rate work and N-scaling/decoder
acceleration. No commit/push or promotion is authorized.

### 2026-09-14 — Accept P9 lower-rate point; route next to FWHT scaling probe

Accept `TARGET_EMPIRICAL_LOWER_RATE_POINT_ACCEPTED` within the frozen synthetic
V25-1M-TRAIN model-sampled N=256 scope. The zero-axis 56-point SCREEN selected
K1=6/K2=70; disjoint CONFIRM achieved 624/640 exact, Wilson one-sided 95% LB
0.9626753340557015, and all integrity/scientific gates true. Both independent
reviews PASS. The Wave-C delivery certificate failure did not cause a second
run; the retry stopped on the existing root and read-only evidence established
the single genuine execution.

Accept only the frozen-grid result, not a continuous/global optimum. BEC and
P8-anchor comparisons remain report-only. Planning-only f=2.1651599289 remains
above f<=1.3, so another N=256 static/adaptive gate is not the next priority.
Freeze `NBPOLAR-PHASE4-P10-FWHT-KERNEL-SCALING-PROBE` as a Tier-X injected-data
engineering probe of direct-vs-FWHT GF(32) minus-node equivalence, fallback,
timing/memory scaling and the unmodified SC baseline through N=1024. It has no
artifact access, attempt, claim status, production change, commit, or push and
awaits explicit authorization.

### 2026-09-14 — Reject exact-semantics FWHT route; freeze exact chunked SC gate

Batch the X10-X12 Tier-X scaling milestone. X10's FWHT primitive was fast but
did not preserve exact tail support. X11 correctly STOPPED after finite
roundoff flipped near-tied SC decisions and produced direct/hybrid exception
parity failure; independent reviewer-go reproduced the causal chain. Do not
advance the current FWHT approach into an exact-semantics production gate, and
do not treat X11's stdout timing transcript as persisted performance evidence.

X12 established that contiguous row chunking of the unchanged q²
`logaddexp.reduce` calculation preserves bitwise arrays, support, decisions,
exceptions and ties over its frozen matrix. Chunk512 completed N=262144 in
65.7253 s with cumulative peak RSS 754,647,040 B. Freeze
`NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC` as the next Tier-Y allocation-only
implementation gate. It awaits explicit authorization, has attempt 0/1 and no
artifact access, and makes no FER/efficiency/key-rate/throughput/promotion
claim.

### 2026-09-14 — Accept exact chunked SC; freeze target f=1.3 N profile

Accept `EXACT_CHUNKED_SC_ACCEPTED` as an allocation-only implementation change.
Default 512-row chunking preserved the accepted direct arithmetic and all
frozen semantic/exception checks, paired exactly at N=65536, and completed
N=262144 in 66.088 s at 710,504,448 B RSS. Both independent reviews support
acceptance; attempt 1/1 was consumed without rerun and no artifact was read.
This is not a throughput, FER, efficiency, key-rate, qualification or promotion
claim; report-only timing targets remain report-only.

Freeze `NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE` as the next Tier-Y
gate. It uses V25 1M TRAIN model sampling and N-specific BEC-surrogate orders,
allocates the exact f=1.3 disclosure budget deterministically, and reports a
six-N/128-block recovery profile without a recovery pass threshold. It does not
extrapolate P7's N=256 empirical order or qualify large-N FER. Artifact read and
attempt are 0/1 pending explicit authorization; no commit/push or promotion.

### 2026-09-14 — Accept P12 terminal resource blocker; probe metric lifetimes

Accept `BLOCKED(resource_limits_met_and_no_abort)` as P12's terminal outcome.
The only run reached N=262144 L2 metric construction and failed on a 64-MiB
float64 allocation outside the SC/resource guard. Read/attempt 1/1 are spent;
no persisted profile exists, earlier in-memory blocks are not evidence, and
independent review confirmed there was no rerun.

The blocker is outside P11's chunked minus-node and includes cross-stage and
cross-block retention of N×32 planes. Do not rerun or repair P12. Freeze
`NBPOLAR-PHASE4-X13-METRIC-MEMORY-LIFETIME-PROBE` to compare two exact injected
ownership/lifetime strategies, scalar-only outcome retention and sequential
N=262144 behavior under 2 GiB. It is Tier-X, has no artifact access/attempt/
claim, and awaits explicit authorization. A future P12-R1 requires a fresh
packet, root, seeds, read and attempt.
## 2026-09-17 — Accept P19 descriptively; route NB-Polar to real-data correction feasibility

Accept `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE` from the
finalized worktree evidence. The concurrent `faac0411` commit contains a
superseded 11/15 checkpoint and is not the result. The single P19 run passed
20/20 integrity gates, consumed reads/attempt 1/1 without rerun and produced
15/15 `verify_failed` outcomes across base, +128 L1, +512 L2, both and an
isolated true-L1 control.

The +128 L1 arms corrected L1 on all three blocks, but complete recovery
remained 0/3; the true-L1 control and the registered L2 backoff also recovered
none. Accept only the same-block mechanism interpretation: hard-L1 propagation
is not sufficient to explain these failures, and the tested backoffs did not
recover them. Do not infer FER, global backoff failure, qualification or route
rejection, and do not tune a successor on these three closed blocks.

The independent checkout's active objective is now real-data NB-Polar
correction feasibility, not cross-family comparison: (1) operational
non-oracle complete-block recovery under a preregistered meaningful disclosure
cap, (2) reproduction on new blocks/independent sessions, then (3) efficiency
optimization toward `f<=1.3`. Security remains an external interface contract.

Before another real-data execution, freeze P20A to repair the statically
confirmed internal-SC `MemoryError` misclassification and to make L1,
hard-L2, oracle-L2 and pair endpoints unambiguous. P20A is injected-only and
authorizes no protected read or scientific attempt. L1 SCL is conditional on
evidence that true-L1 L2 is recoverable and a bounded list covers the missing
candidate; it is not the default next route.

## 2026-09-19 NB-Polar H2a–H2e adjudication accepted (descriptive; 56-row P20N+P20O+P20Q, X10-continuity, A4 recheck PASS)

**Decision**: Record T8 main-thread verdicts as descriptive only from `workspace/h2/504e036a-f040-4d88-88ba-152702f92ffd/h2_final_adjudication.md` + `h2_summary.json` (git-ignored run root; durable plan `.workbuddy/queue/NBPOLAR-H2-ADJUDICATION-ANALYSIS/H2_ANALYSIS_PLAN.md` §§4/6 applied verbatim): H2a REFUTED (8/14 evaluable blocks anomalous, strongest P20N b3 gap 0.097058, X10 4/4 reproduced diff 0.0); H2b SUPPORTED (median r_fail 2.2835 n=37; IR-2 median 0.883 n=12, no vote-flip); H2c SUPPORTED (in-X 35/37=0.9459; 12/14+11/11+12/12; out-of-U given in-X 23/23 on 2M segments, no threshold vote); H2d SUPPORTED-flat (mean_abs_diff 0.002185 n=37 ≤0.05); H2e REFUTED-geometry-incoherent (evaluable 20/20+12/12+20/20; IR-4 pooled in-prefix 66/320=0.20625<0.50 despite IR-2 0.883≥0.50; truncated scope first-4096+top-16+histogram, never full-block order, never FER).

**Context**: Analysis-only (zero decoder/RNG/tag/protected counters); 56-row join (P20N 16 + P20O 20 + P20Q 20); A4 recheck PASS 6/6 (session ses_f46181fa5ffe3gj5wry5EdHFGy); H2a–d X10-consistent, H2e NOT-DECIDABLE→evaluable-but-incoherent.

**Observation (not verdict)**: Fail sites in-X + hazard-elevated yet top-16 hazard mass mostly outside-prefix — static top-k geometry does not mirror fail-site geometry; prime clue for next single-factor direction.

**Alternatives considered**:
- FER/reliability/efficiency/branch-selection readings: rejected — descriptive only, no threshold vote.
- Recheck-transcript internals: rejected — not evidence.
- Verbatim large tables: rejected — run root is git-ignored; durable plan + summary carry the record.

**Consequences**: No rerun/retuning, no OpenSpec/AGENTS/troubleshooting change; next branch (L2-order-positions-under-raw-prior / L2-side-bounded-search-at-fixed-point / second-single-construction-form per P20Q §16) remains main-thread planning input — H2 selects nothing.

## 2026-09-19 NB-Polar Phase 4 P20R order-position 1.5M accepted (descriptive NEGATIVE, 0/1 single block)

**Decision**: Record the single P20R Tier-Y execution as `TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`, accepted descriptive only. The new-B order single factor produced a descriptive NEGATIVE on its first single-block evaluation: no restoration, with even the true-L1 oracle pair failing on this block.

**Context**: Single-factor L2-order-position packet `.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/` (`MAIN_THREAD_ACCEPTANCE.md` / `PRE_EXECUTE_REVIEW.md` PASS / `PRE_RESULT_REVIEW.md` PASS on disk; Stage-A 21/21 green with derive-once + pinned new-B digest `c7853286…e751` reviewer-recomputed exact; D2 FEASIBLE margin 3928.304784481981 pre-DEV). One-shot Stage B (exit 0, wall 44.37 s / RSS ~521 MiB, SC 6/6, tags 4/4, sampling 0, genie 0+0) on the single 1.5M VAL-remainder block 2044..2171 (CONSUMED, one draw, N=32768, K1/K2 331/6689, tag master 2026092340): A 0/1, B 0/1, C 0/1, D 0/1, all `verify_failed`, `undetected` 0; `b_maintained`/`b_restored` 0, A→B {0,0,0,1}; `d_restored` 0, C→D {0,0,0,1}. Byte-exact disclosed-set manipulation (K2 6689 both arms; intersection 1213; |A−B|=|B−A|=5476; size-delta 0). First errors all L2-layer: A/C coord 133 (in-X, U-domain-out), B/D coord 0 (out-of-X). Disclosure caps A/B 35164 Δ0, C/D 33509 Δ0; key 137346 / public 1310972, recount 0; 34/34 integrity gates. IR payload: IR-2 A 0.99966 vs B 0.32919 (geometry contrast), IR-4 top-16 in-prefix 4/16 all records, IR-5 truncated. Chain: four single factors now tested descriptively — P20N/P20O/P20Q construction-side (B 1/4→2/5→4/5) + P20R order-side 0/1 negative; §16 next-branch candidates (L2-side bounded search at fixed point / second single construction form / further order refinement) eligible for planning selection, NO selection made.

**Observation (not verdict)**: H2 input — the IR-2 rank shift (0.99966→0.32919) joins the archive for main-thread H2 analysis; no H2 verdict here.

**Alternatives considered**:
- FER/reliability/efficiency readings: rejected — one block, descriptive only, no threshold vote.
- Branch selection in this packet: rejected — §16 candidates remain main-thread planning input.

**Consequences**: No rerun/retuning of P20R; P19 roots untouched; no push. 2044..2171 CONSUMED; stub 2172..2212 + 2M HOLD remainder 3556..3644 never-decoded.

**Limitation**: The A anchor (α1 + frozen order) and the true-L1 oracle pair also recorded non-exact on this block; the result is block-dominated and does NOT discriminate the order factor.

## 2026-09-20 Next-branch decision record adopted (corrections + D4 hygiene; D1 pending; D3 launched)

**Decision**: Adopt `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md` (main-thread review 2026-09-19; non-packet, non-freeze, no execution authorization) as the binding next-branch record: (i) P20R block-dominated qualifier applied to the P20R decision-log entry — the A anchor (α1 + frozen order) and the true-L1 oracle pair also recorded non-exact on block 2044..2171, so the 0/1 negative is block-dominated and does NOT discriminate the order factor; (ii) 4-segment never-used ledger correction applied to `AGENT_PROJECT_MEMORY.md` top P20R scope and the `DOCUMENT_INDEX.md` P20R row — 1.5M VAL 2172..2212 (41 frames / 10,496 pairs), 1.5M HOLD 2725..2766 (42 / 10,752), 2M VAL 2827..2915 (89 / 22,784), 2M HOLD 3556..3644 (89 / 22,784), total 261 frames / 66,816 pairs; under the current same-split rule = 0 full N=32768 blocks, while the two 2M segments combine to 178 frames = 1 block + 50-frame stub and the 1.5M remainder (83 frames) is low-information (oracle 1/8) treated as unusable per the record §3; (iii) evidence-size standing rule in force — single committed evidence file ≤ ~2 MB, larger frozen artifacts under git-ignored `workspace/` with digest + summary line committed, per-packet exceptions ended (P20Q's 2.25 MB was the last), AGENTS.md formalization deferred to the next OpenSpec change; (iv) P20R commit `f0e87f4` pushed with this batch (branch-private, evidence double-reviewed); (v) D1 (2M cross-split merge authorization, D1-A vs D1-B) awaits explicit user decision — NO merge authorized here; (vi) D3 synthetic SCL list-survival probe (`NBPOLAR-X14-SCL-LIST-SURVIVAL (renamed from the X11 draft label; x11–x13 prefixes occupied)`) launched per the record (synthetic-only, zero protected-data cost); (vii) D2 (max-information mechanism probe on the single block) contingent on D1-A.

**Context**: Docs-only adoption batch; no decoder execution, no protected-data opens, no consumed-block revisits. Binding constraint per the record is population first, factors second: any real-data evaluation must land on 2M (high-information, oracle ~70%), never the 1.5M remainder.

**Alternatives considered**:
- Deciding D1-A vs D1-B in this batch: rejected — pending explicit user decision.
- FER/reliability/efficiency/branch-superiority readings: rejected — descriptive only, no threshold vote.
- Cross-session merge (1.5M with 2M): rejected — never mixed per the record §5.
- P20R rerun/retuning or revisiting consumed blocks: rejected.
- Consuming the 1.5M stub or 1.5M HOLD remainder: rejected — treated as unusable.
- Changing α/floor/K/decoder this round, or starting (b)/(c): rejected — not in this round.

**Update (2026-09-20, user decision)**: **D1-A AUTHORIZED** — the user authorized the 2M same-session cross-split merge (VAL remainder `2827..2915` + HOLD remainder first 39 frames `3556..3594` = exactly one 128-frame N=32768 block) to re-place the final real-data block on the high-information 2M population; D2 (mechanism probe on that block, no recovery-rate reading) is thereby unblocked and its packet `NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED` is in freeze at this writing. Never-decoded after P20S: 2M HOLD `3595..3644` (50 frames) + 1.5M remainder 83 frames.

**Consequences**: P20R stays accepted descriptive with narrowed interpretive scope; D1-A authorized and D2 packet in freeze; D3 synthetic work proceeds on a separate track; no AGENTS.md edit in this batch.

**Addendum (2026-09-20, user decision)**: local-spike formula FROZEN = **F-median8** (`score[i] = h[i] − median(W8(i))`, tie-break ascending; deterministic zero-sampling; feeds P20S arm B + X14 Q2 alignment).

## 2026-09-20 Milestone: P20S mechanism probe accepted; synthetic SCL line (X14→X17) closed as non-informative

**Decision**: (i) P20S-R1 (`NBPOLAR-PHASE4-P20S-R1-GATE-FIX`) accepted as `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE_ACCEPTED_DESCRIPTIVE` — independent Pre-RESULT PASS 9/9 (reviewer-go session ses_f44c186afffej4IC26000cx8cB), 36/36 integrity gates, geometry only: A exact prefix-mean 0.87406; B L2 fail @coord 0, hazard 0.513, IR-2 0.4322, fail site outside the disclosed prefix, floor 0.3717, prefix-mean 0.87683; O oracle exact; A△B 1599/1599; IR-4 top-16 in-prefix 0; IR-5 uncapped full-block series. (ii) Synthetic probe chain X14 (near-random flat) → X15 (0.75 diagonal, mismatch unchanged 0.9686) → X16 (exact N=32768 + real disclosure ratios, 0.76902 ≈ derived no-information ceiling 0.76931, G2 0.999 informative tables) → X17 (H-a U/X truth confusion confirmed and localized to probe bodies; positive control P=0.000 rules out a feed/decoder defect; corrected full-scale C still ≈ chance at 0.763/0.961). (iii) CONSEQUENCE: the SCL-unlock question cannot be answered on synthetic data at this operating point — re-asking survival there is proven pointless; any future SCL work must change the operating point (disclosure placement/amount, channel strength, or the list-decoding question itself) and be separately gated; SCL stays locked. (iv) No production module was changed in this chain. (v) D3's synthetic line is recorded as non-informative with a four-probe capability record, not as a scientific negative about SCL.

**Alternatives considered**:
- Promoting the X17 corrected-feed numbers to an SCL verdict: rejected — descriptive Tier-X probe, operating point sub-threshold, SCL stays locked.
- Rerunning R1 to remove telemetry-only jsonl variance: rejected — 9/9 IR-5 bins identical, scientific fields identical; future delta successors freeze-exclude `wall_s`/`resources.*` up front.
- Changing production decoder/feed modules on the H-a finding: rejected — production runner already correct; confusion was probe-body only.

**Consequences**: R1 packet closed (`PACKET_CLOSED_AWAITING_NEXT_PLANNING`); X17 `COMPLETE_AWAITING_FOCUSED_REVIEW` (focused numerical review milestone-batched); no rerun/retuning; no OpenSpec/AGENTS.md change in this batch.

## 2026-09-20 H2 v2 accepted (full-block geometry join; synthetic SCL line closed)

**Decision**: (i) H2 v2 re-adjudication on 59 rows (56 archive + 3 P20S/R1) — verdicts H2a REFUTED (evaluable 8→9, new gap −0.00277 non-anomalous), H2b SUPPORTED (n 37→38, new r_fail 0.5853, median 2.2835→2.2651), H2c SUPPORTED (35/38 = 0.921; new datum = 3rd out-of-X L2 fail archive-wide, first on spike-local order, coord 0, out under both domain flags), H2d SUPPORTED-flat (new d=0, mean 0.002128), H2e-truncated REFUTED-geometry-incoherent (unchanged) + H2e-full-block-n1 REFUTED-geometry-incoherent (IR-4 0/48 vs IR-2 0.4322, conjunction not met, n=1 caveat); (ii) IR-5 `.bin` bytes ruled protected → manifest/sha-level evidence only (hazard sha identical across A/B/O ⇒ hazard values order-independent under frozen α1; A≡O masks; B differs); (iii) synthetic SCL line X14→X17 closed as non-informative at this operating point (positive control P=0.000 rules out feed defect; corrected full-scale C ≈ chance ⇒ sub-threshold, not wiring); (iv) consequence: no further synthetic survival re-asks at this operating point; any SCL work needs an operating-point change (new top-level OpenSpec change) and separate authorization; (v) ledger: 0 full N=32768 blocks remain (133 frames / 34,048 pairs never-decoded).

**Recheck**: independent reviewer-go recheck `H2V2_RECHECK: PASS_WITH_FINDINGS` (2026-09-20, session `ses_f44aa4832ffeidyigKTYTP3ucx`); record `.workbuddy/queue/NBPOLAR-H2-ADJUDICATION-ANALYSIS/H2V2_RECHECK.md`; run root `workspace/h2/497eecf4-d060-42a2-a862-49e8059590b7/`; one doc typo fixed in `h2a_table.md` (P20S operational-only `n_exact` 2→1; JSON already correct); `h2v2_record_table.json` (2,973,931 bytes) excluded from commit per the evidence-size rule — sha256 `74be86226f18c5f64c4e43a3d11fed2688cdff067711b3a0da95b1e5d450743a`, 59 rows recorded in the recheck file instead.

**Alternatives considered**:
- Pooling truncated vs full-block scopes: rejected — scope labels load-bearing, pooling forbidden.
- FER/efficiency/leakage/key-rate/reliability/deployment readings from v2: rejected — descriptive only.
- Opening IR-5 `.bin` bytes for value-level evidence: rejected — protected per the binding scope ruling.

**Consequences**: H2 v2 accepted descriptive; synthetic SCL line closed at this operating point; no rerun/retuning; no OpenSpec/AGENTS.md change in this batch.

## 2026-09-20 Geometry mining: §3 trigger met (Q-G1/Q-G2); reduced-N held pending gates

**Decision**: (i) Order-independence confirmed at manifest level — hazard sha `ef4398d3…` identical across A/B/O; A≡O masks; B differs; |A−B|=|B−A|=1599 = 23.70% swapped, size-delta 0 — ⇒ hazard is a property of the frozen α1 table and orders only choose disclosed positions. (ii) Disclosed prefix covers the low-hazard fifth (IR-1 6746/26022; IR-3 A/O 1641 vs B 1651 above-threshold; IR-4 top-16 in-prefix 0/48 on ALL arms with hazards 9.0768–9.2784 bits ≈ 10.4–10.6× prefix mean) ⇒ 100% of the top-16 tail is undisclosed under both orders. (iii) The single B failure (L2 @ coord 0, 0.513 bits, IR-2 0.43222, outside prefix under both flags, floor 0.3717) is the 3rd operational out-of-prefix fail archive-wide and the 1st on a spike-local order — existence case only, n=1 no discrimination (P20R-B is a descriptive parallel, different session/K/alt/order, never pooled). (iv) §3 trigger = YES with named questions Q-G1 (does the spike-local fail pattern recur at N=8192 on the 2M HOLD tail, within-N paired) and Q-G2 (does spike-local disclose more tail mass than frozen at the same N). (v) DECISION (main thread, recommend path): proceed with (iii) analysis-only AND authorize (iv) SCOPING ONLY (OpenSpec delta + freeze, NO execution, NO tail contact) — (iv) remains one N=8192 block = persistence probe, not statistical discrimination, and still needs its own Stage-A/Stage-B authorizations + independent reviews. (vi) Confirm 0 full N=32768 blocks remain (133 frames / 34,048 pairs never-decoded; N=8192 would use 3595..3626 with remainder 3627..3644).

**Alternatives considered**:
- Authorizing (iv) execution now: rejected — no freeze, no Stage-A/Stage-B authorizations, no independent reviews yet.
- Pooling P20R-B with P20S-B for order discrimination: rejected — different session/K/alt/order; descriptive parallel only.
- Disclosing tail positions or list decoding on this evidence: rejected — neither executed; L2 tail-decodability needs option (i), not (iv).

**Consequences**: geometry run root `workspace/geometry/58503bc3-0306-45b0-b70c-2599aaf82820/` committed (commit `e7600347`); feasibility study `.workbuddy/queue/NBPOLAR-REDUCED-N-FEASIBILITY.md` committed; (iv) scoping gated on OpenSpec delta + freeze + explicit authorizations; no tail contact; no rerun/retuning.

## 2026-09-20 Reduced-N (N=8192) persistence probe — scoping only, no execution

**Decision**: (i) extend the umbrella change `formal-ir-nbpolar-phase4-p0/` with `specs/nbpolar-reduced-n-persistence/` (spec + design + proposal) + tasks RN-1..RN-8, each marked `[GATE — NOT AUTHORIZED]`; (ii) population = ONE N=8192 block on the 2M HOLD tail 3595..3626 (32 frames / 8192 pairs) with declared remainder 3627..3644 (18 / 4608); 1.5M stubs not used; no cross-split combining; D1-A not invoked; 1.5M↔2M never mixable; (iii) rebuild-vs-reuse split — rebuild: construction/allocation, FROZEN_N=8192 runner+tests, K ≈1760 by the frozen formula (estimate only, never hand-filled), fresh length-8192 L1/L2 + spike orders, tag value 81983 + new domain, SC stages 13, IR-5 48 KiB/record, disclosure values, population gates, all reviews/authorizations; reuse read-only: 2M session-H inputs (worktree arrays, never the counts NPZ), formula shapes, code paths, recount/gate/truth-isolation/oracle machinery; (iv) comparability boundary restated — per-N results are NOT comparable across N; the 1/4→2/5→4/5 chain, the H2 verdicts, the 32768 IR-5 geometry and all leakage literals do not transfer; (v) effort class = P16-scale, not P20S-scale thin reuse; (vi) trigger provenance: §3 trigger met by geometry mining (Q-G1 spike-local fail-pattern recurrence at N=8192; Q-G2 tail-mass disclosure comparison at the same N); (vii) this scoping authorizes NOTHING — no data contact, no execution; the 2M HOLD tail stays never-decoded until its own Stage-A/Stage-B authorizations + independent reviews.

**Context**: geometry mining met the §3 trigger with named questions Q-G1/Q-G2; the 2M HOLD tail (50 frames / 12,800 pairs) fits exactly one N=8192 block plus an 18-frame remainder; the N=32768 ladder is exhausted (0 full blocks remain; 133 frames / 34,048 pairs never-decoded).

**Alternatives considered**:
- Authorizing reduced-N execution in this scoping: rejected — no delta freeze review, no Stage-A/Stage-B authorizations, no independent reviews yet.
- Using the 1.5M stubs or pooling across N/sessions: rejected — 1.5M↔2M mixing forever forbidden; per-N results not comparable.

**Consequences**: scoping-only delta committed and pushed (no execution, no data contact — zero protected opens, attempts 0/1); next gate is RN-1 freeze review; the full 50-frame 2M HOLD tail stays never-decoded until separately authorized Stage-A/Stage-B execution + independent reviews.

## 2026-09-20 Corrections to review findings (RN questions, counts boundary, X17/SCL qualification, mechanism reading)

**Decision**: (i) RN Q-G1 unified to the mining formulation (undisclosed below-mean coord-class site with floor-rate elevation, paired vs frozen order); spec ADDED-1 + proposal Problem fixed; Q-G2 aligned to "top-hazard-tail mass"; (ii) counts boundary resolved — V25 counts-NPZ opens 0/0 at every stage reaffirmed; construction/order derivation inputs = worktree-reused prior arrays only; TRAIN "sampling" = synthetic draws from the worktree prior in Stage-A derivation with budget+seeds pinned at freeze (never counts opens, never DEV/real frames); design R1/R4 reworded; spec "63-row" corrected to the actual 59-row H2 v2 join (16+20+20+3; P20R read-only); the feasibility study's "63-row" mention is left frozen as superseded; (iii) X17: independent focused numerical review commissioned 2026-09-20 (pending at this writing; see FOCUSED_REVIEW.md when complete) — positive control proves decodability under control conditions only; working-point-related defects are NOT excluded; full-scale at-chance alone does NOT prove sub-threshold; causes not fully distinguished; the synthetic-branch closure stands with this qualification; (iv) mechanism reading downgraded — hazard equality is a per-block/per-arm manifest fact; 6746/32768≈20.59% is a position fraction, not proof of "lowest fifth" selection; top-16 uncoverable (0/48) does NOT directly translate to most-dangerous-SC-channels-undisclosed; all such statements now read as descriptive geometric observations; (v) RN-1 stays in revision prep — the present freeze draft is NOT approved for freezing; still no authorization for construction, data reads, or execution.

**Context**: 2026-09-20 user review of the RN-1 revision-prep draft, the H2 v2 / X17 closeout, and the geometry-mining mechanism reading. Corrections are additive qualifiers — no frozen evidence file is rewritten.

**Alternatives considered**:
- Rewriting frozen evidence or the superseded feasibility study in place: rejected — frozen stays frozen; corrections live in the live delta files plus this entry.
- Treating these edits as a freeze pass: rejected — RN-1 stays in revision prep; freeze review is a separate future gate.

**Consequences**: RN delta files (spec ADDED-1/ADDED-4/ADDED-7, design R1/R4, proposal Problem) carry the unified wording; AGENT_PROJECT_MEMORY.md mechanism line downgraded; RN-1 still needs freeze review + user authorization before any construction, data reads, or execution.

**Addendum (2026-09-20)**: X17 independent focused numerical review complete — PASS_WITH_FINDINGS (numbers recomputed exact; H-a code-localized; positive control proves control-regime decodability only; full-scale at-chance does not prove sub-threshold; causes undistinguished).
This supersedes the "pending" note in the 2026-09-20 Corrections entry, item (iii).

## 2026-09-20 RN-1 freeze review PASS (reduced-N delta; revision-prep corrections verified)

**Verdict**: RN-1 FREEZE REVIEW PASS (2026-09-20, main thread) on `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-reduced-n-persistence/` (spec.md + design.md + proposal.md) + umbrella tasks.md reduced-N section (RN-1..RN-8).

**Checklist**: (1) population arithmetic verified — DEV 3595..3626 = 32 frames × 256 = 8192 pairs, remainder 3627..3644 = 18 × 256 = 4608, single contiguous HOLD segment/single session, 1.5M stubs excluded, no cross-split combining, D1-A not invoked; (2) arm rule verified — A newly-derived N=8192 frozen-order-equivalent anchor (α1) / B spike-local at identical K with carried F-median8 formula-id and R=8 re-frozen as a new decision / O true-L1 oracle diagnostic deployable=false; (3) K estimate-only rule verified — ≈1760 estimate only, derived in-packet from recomputed 2M H, never hand-filled (AGENTS.md §5.5); (4) comparability boundary verified — non-transfer list (1/4→2/5→4/5 chain, H2 verdicts over the 59-row join, IR-5 32768 geometry, leakage literals), within-N-only judgment, no cross-N inference; (5) gate markers verified — RN-1..RN-8 all `[GATE — NOT AUTHORIZED]`, scoping authorizes nothing, all boxes unchecked; (6) revision-prep corrections verified — Q-G1 unified to the mining formulation (undisclosed below-mean coord-class site with floor-rate elevation, paired vs frozen order) in spec + proposal, Q-G2 aligned to top-hazard-tail mass, tasks.md ID-only confirmed by grep, counts boundary resolved (V25 counts-NPZ 0/0 reaffirmed; worktree-only inputs; synthetic sampling budget + seeds pinned at freeze), 59-row join (P20R read-only) confirmed, residual contradiction grep (`new counts|counts-train|local-hazard spike|63-row|OPEN_PIN|UNDECIDED`) clean; (7) honest scope verified — n=1 descriptive persistence probe, no FER/reliability/efficiency/leakage/key-rate/recovery/scaling/promotion claim, no H2 input.

**Consequence**: RN-2 (Tier-Y packet freeze for the N=8192 probe) proceeds under the standing pre-authorization 2026-09-20; Stage-A/Stage-B still need their own freezes + independent reviews + authorizations per the gate sequence; the 2M HOLD tail stays never-decoded until then.

## 2026-09-20 NB-Polar Phase 4 P20T N=8192 persistence probe accepted (descriptive; within-N only; ladder ends by exhaustion)

**Decision**: Record the single P20T Tier-Y execution as `TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE_ACCEPTED_DESCRIPTIVE`, accepted descriptive only. Within-N paired geometry only (Q-G1/Q-G2 asked, neither decided); no FER/reliability/efficiency/cross-N/H2 reading; no branch selection.

**Context**: Packet `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/` (`MAIN_THREAD_ACCEPTANCE.md` / `OPERATOR_RETURN.md` / `P20T_FREEZE.md` on disk; Stage-A 23/23 green; independent Pre-EXECUTE PASS + Pre-RESULT PASS; branch `codex/nbpolar-phase0`). One-shot Stage B (exit 0, wall 8.36 s / RSS ~350 MiB, attempts 1/1, DEV 1/1, counts 0/0, SC 5/5, tags 3/3, sampling 0) on the single 2M HOLD-tail N=8192 block 3595..3626 (CONSUMED, one draw, K_total/K1/K2 1760/84/1676, tag master 2026092400; construction digest `d77466ec…`, fresh-order `66aefea8…`, spike-order `355a32d3…`, formula `F_MEDIAN8_CARRIED_20260920_H_MINUS_LOCAL_MEDIAN_W8_R8_REFROZEN_8192`). A/B/O all `verify_failed`, L2 first errors: A @193 X-disclosed/U-undisclosed (fail hazard 0.509b vs prefix-mean 0.873b, IR-2 0.4001); B @3 undisclosed under both flags (0.438b vs 0.888b, IR-2 0.0500); O identical to A (diagnostic, non-deployable). Floor hits A 12 vs B 1084; set-delta byte-exact (∩713, ±963, Δ0); IR-4 top-16 in-prefix A=4/B=3/O=4 with byte-identical coords (flags differ); IR-3 A 403/403 vs B 419/417; 31/31 gates; recount key 26172 / public 245949, mismatch 0; `undetected` 0. Q-G1 elements + Q-G2 contrast recorded, neither decided (n=1, no baseline at this N). Chain state: FIVE single-factor efforts now — P20N/P20O/P20Q construction-side (N=32768, B 1/4→2/5→4/5 descriptive), P20R order-side (1.5M, 0/1 block-dominated negative), P20T reduced-N persistence (N=8192, within-N only, non-transferable). Process: the new-N derivation from worktree prior with zero counts opens pattern worked (construction/orders/spike reviewer-recomputed); delta-successor rule re-confirmed — `wall_s`/`resources.*` telemetry stays freeze-excluded from byte-equality (P20S-R1 lesson, re-observed).

**Alternatives considered**:
- FER/reliability/efficiency/cross-N readings of the A/B/O geometry: rejected — n=1 at a new N with no baseline has no discriminating power; within-N descriptive only.
- Branch selection or H2 input from this packet: rejected — explicit no-H2-input scope; operating-point redesign / acquisition / closeout deferred to main-thread planning.
- Recheck transcripts or wall-clock literals as evidence: rejected — non-evidential; telemetry excluded from byte-equality by rule.

**Consequences**: No rerun/retuning of P20T; P19 roots untouched; no push. DEV 3595..3626 CONSUMED; HOLD remainder 3627..3644 (18 frames) + 1.5M VAL stub 2172..2212 (41) + 1.5M HOLD 2725..2766 (42) stay never-decoded; nothing formable remains under any authorized rule — the real-data ladder ends by population exhaustion, not by verdict.

## 2026-09-20 Sciverse q-ary polar SCL survey completed (10 papers + 2 abstract companions)

**Decision**: Record the bounded research-only survey `.workbuddy/queue/LITERATURE-SCL-QARY-POLAR-SURVEY.md` (10 papers + 2 abstract companions, sciverse skill only, no implementation/execution) as complete. Its L-ladder recommendation (L∈{4,8,32} + binary control) is REJECTED for the RN probe and DEFERRED to a future separately-gated SCL track.

**Context**: (i) Bottom line — q-ary SCL typically needs smaller L than binary (4× per field upgrade, two independent studies: Yuan & Steiner 2018 GF256 L/4; Abbasi N=8192 GF16/L=8 ≈ GF4/L=32 ≈ binary/L=128, AWGN very-low-rate — the only external N=8192 q-ary SCL reference); spike-local reliability gating is a published winning family (split-reduced, critical-set, pruned-tree) but our frozen-hazard signal itself is novel (IR-4 top-16 in-prefix 0/48 has no published analogue); adversarial case weak — no list-failure-on-heavy-tail evidence; nearest negatives are GF(5) q-mismatch (Falk) and HD-QKD IR's zero polar presence (Müller 2024, NB-LDPC/Cascade standard); hard gaps — zero GF(32)-polar-SCL points, zero N≥8192 q-ary outside AWGN/low-rate, zero heavy-tail/QKD-channel SCL studies, zero frozen-hazard phenomena in print. (ii) L-ladder REJECTED for RN: frozen SC-only scope, no SCL module exists in `formal_ir/nbpolar/`, SCL stays locked; an SCL arm would be a second factor plus a new decoder. DEFERRED to a future separately-gated SCL track with its own OpenSpec change + freeze + authorization. (iii) Corpus bias noted: sciverse full-text is AI-conference-heavy; 2 companions honestly marked abstract-level (excluded from the 10-count); Feng 2020 full-text fetch failed (FETCH_FAILED).

**Alternatives considered**:
- Adopt L∈{4,8,32} + binary control into the RN probe now: rejected — second factor + new decoder outside the frozen SC-only scope.
- Treat the survey as SCL-unlock evidence: rejected — survey only, no execution; X14-style survival stays the hard gate.

**Consequences**: No code/artifact change; no execution; SCL stays locked; no OpenSpec box checked. A future SCL track needs its own change + freeze + authorization.

## 2026-09-20 P20T delivery check + closeout batch (descriptive results kept)

**Decision**: (i) Delivery check on the accepted P20T root (independent reviewer-go, read-only, no decoder re-run): DELIVERY INCOMPLETE on three §9 aggregate tables — mismatch-coverage table, full-block series summaries, full-scope top-128/1024 concentration are ABSENT-MISSING (no supersession on record; the Pre-RESULT IR-1..IR-5 confirmation did not cover them); IR-1 tails minimal-present; A-vs-B set-delta present. The accepted descriptive label is UNAFFECTED (integrity 31/31, per-record scalars/IR intact); only immediate Q-G1/Q-G2 asking power is weakened, and the answers remain derivable post-hoc from the IR-5 `.bin` series. (ii) Interpretation balance recorded: on the reported metrics of this block, B covered no more tail than A (top-16 in-prefix B=3 vs A=4; tail8 B=0 vs A=1) — this does NOT generalize to "spike order ineffective"; conversely the paired A/B difference on this block is a valid observation, not nothing. (iii) Floor guardrail: B's earlier first error + larger cumulative floor hits may include post-error-propagation consequences; cumulative values do NOT support "floor caused the first error"; future causal study must separate pre-error / at-error / post-error instead of adding same-type aggregates. (iv) Status closeout: `NBPOLAR-REDUCED-N-PERSISTENCE/` (scoping skeleton) and `NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE/` (RN-2 pre-execution freeze) are SUPERSEDED by the accepted `NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/` — kept for provenance via `SUPERSEDED.md` markers, never for new work; X17 `STATUS.yaml` `status:` corrected to `COMPLETE_REVIEWED_PASS_WITH_FINDINGS` (was stale `COMPLETE_AWAITING_FOCUSED_REVIEW`); the nine P20T IR-5 `.bin` files are committed under a recorded one-packet exception to the never-stage-`*.bin` guard (each ≤32768 B totaling ~147 KB; irreproducible without DEV reopen, which is forbidden on the consumed block; manifest digests cross-checked) — saved in git, retrievable via the evidence root; acceptance-docs-committed is NOT equated with complete-evidence-pushed. (v) Future SCL rule: SCL is a separate project; its first step is a synthetic working point that distinguishes SC vs list gains, and only then is an L-ladder decided with re-justified L values (never inherited from the survey's L∈{4,8,32}).

**Context**: 2026-09-20 user review (five points, in priority order: delivery check first, then batched status/adjudication text; RN descriptive results kept). Corrections are additive; no frozen evidence file rewritten.

**Alternatives considered**:
- Re-running the decoder to produce the missing tables: rejected — one-shot spent, DEV reopen forbidden; derivation is post-hoc from committed `.bin` series only.
- Leaving the `.bin` files worktree-only: rejected — DEV-consumed truth makes them irreproducible; complete evidence must be pushed.
- Deleting the survey's L-ladder lines: rejected — kept with adjudication tags (inline + §7) so provenance stays readable.
- Generalizing the B-vs-A tail observation to "spike order ineffective": rejected — n=1, no baseline at this N.

**Consequences**: P20T evidence root complete in git; status entries unambiguous; interpretation guardrails durable; RN scope unchanged; SCL stays locked.

## 2026-09-20 Milestone batch: G2 SCL + Q1/Q2 Tier-X queue

**Decision**: (i) G2 landed as commit `dba4f42f` — new module `comparison_bench/src/comparison_bench/formal_ir/nbpolar/scl.py` (288 lines) plus `comparison_bench/tests/test_nbpolar_scl.py` (458 lines); 16 T0/T1 focused tests pass; `sc.py` untouched (frozen baseline); NO synthetic execution ran and none is authorized at this point — SCL stays locked. (ii) The prereg re-analysis queue is adopted as the standing Tier-X route (zero data consumption): Q1+Q2 are the first batch; Q6 is RETIRED (ceiling locked + narrative trend-misread risk); queue cap = 6 probes; at the cap the route FORCES a return to the exhaustion-route decision (operating-point redesign / data acquisition / closeout) — the queue may not silently extend. (iii) Q1 (`workspace/probes/q1-geometry-revival/`) recorded `Q1_DESCRIPTIVE_ONLY`. (iv) Q2 (`workspace/probes/q2-table-vs-input/`) recorded `MEMORY17_UPGRADE_MULTI_ROOT_REPLICATED`. (v) Focused numerical reviews for Q1 and Q2 both returned PASS_WITH_FINDINGS (non-blocking; records stay worktree-only). (vi) All Q1/Q2 preregs, bodies and results stay worktree-only under `workspace/probes/` (gitignored by design); this entry is the durable record.

**Context**: Q1 (real-data read-only persisted evidence only; zero decoder/RNG calls, zero `.bin` opens, zero protected opens): width-weighted prefix-mass totals N=32768 A/O 18070 vs B 18053 (run bins {29}/{37,38,39}/{46,47} identical on all arms); N=8192 A/O 4480 vs B 4479; set-delta N=32768 n=1599, Δ0, ∩5147; N=8192 n=963, Δ0, ∩713; IR-4 top-16 in-prefix N=32768 0/0, N=8192 A/O 4 vs B 3. Descriptive only, within-N, no trend reading. Q2 (both roots byte-exact): hazard sha identical across A/B/O; masks/order digests A≡O≠B; set-delta Δ0; recount mismatch 0; one execution-error rerun recorded in `results.json` (first run mis-applied B-differs to the hazard sha against the prereg rule — implementation-logic fix, frozen params/command unchanged, science reruns 0). G2 context: the SCL track scoping commits `75055934`/`8eaaa74d` and the G1 amendment `f2dab81d` (frozen working-point axis N=16384, K1=167/K2=3373 first-natural, d=0.90; G1 review PASS) precede the implementation; the G2 module carries the frozen `scl_decode`/`SCLResult` interface with L=1 equivalence to `sc_decode` as the hardest T1 test.

**Alternatives considered**:
- Promoting Q1/Q2 descriptive tokens to trend, FER, reliability or efficiency readings, or to cross-N comparisons: rejected — Tier-X descriptive only, within-N, no thresholds; Q6 was retired precisely to cap narrative risk.
- Running the G2 synthetic working-point execution inside this batch: rejected — not authorized; G3 remains its own gate requiring a fresh freeze plus explicit user authorization.
- Committing Q1/Q2 prereg/body/results files: rejected — `workspace/probes/*` is gitignored by design (evidence-size rule); the durable record is this entry plus the milestone memory line.

**Consequences**: No execution, no protected opens, no data consumption in this batch; SCL stays locked; the queue continues under its cap of 6, and reaching the cap forces the exhaustion-route decision (redesign / acquisition / closeout).

## 2026-09-20 Milestone batch 2: G3 synthetic working-point STOP (SCL stays locked)

**Decision**: Record the G3 Tier-X probe `workspace/probes/scl-synthetic-working-point/` as `SCLW_STOP_SANITY_HIGH` — a frozen working-point sanity STOP, not an SCL result. SCL stays locked.

**Context**: Tier-X probe with worktree-only/gitignored root; prereg frozen before the run; sibling-venv interpreter substitution documented; rerun budget 1/1 consumed with the reason recorded. Greedy-SC pooled mismatch 0.770302 vs applicable ceiling 0.769312 (exact arithmetic) sits above the G1 high edge 0.749 → NO disclosure bite for greedy at the frozen d=0.90 point (N=16384, K1=167/K2=3373 first-natural). This is the second ceiling-hugging operating point after X16 d=0.75 — the SCL-unlock question is unanswerable on synthetic data at either tested point. The list arm (N=256, unfrozen top-L stub, no spike-local pruning) showed path-survival 0.0 at all L — wiring-only evidence, NOT an SCL negative and NOT an unlock claim. Wiring checks pass: G2 0.99981 / G3-strata 0.10062. Per the freeze: stop, no repair; any working-point amendment is a main-thread/G1 decision. Focused numerical review PASS with non-blocking F1–F3 (executed-body sha unrecorded; a `size_bytes` second field corrected post-run; run-1 artifact counters zeroed).

**Alternatives considered**:
- Treat the greedy no-bite or the list-arm 0.0 path-survival as SCL evidence (negative or unlock claim): rejected — frozen-point sanity stop; the list arm is an unfrozen stub with no spike-local pruning, so path-survival 0.0 is wiring-only.
- Amend the working point in-packet to chase a disclosure bite: rejected — per the freeze, stop with no repair; a working-point amendment is a main-thread/G1 decision.

**Consequences**: SCL stays locked; no synthetic working-point conclusion at d=0.90 or d=0.75; no rerun/repair; the probe record stays worktree-only under `workspace/probes/` (gitignored by design); this entry is the durable record. Any future SCL working point needs its own freeze + explicit user authorization.

## 2026-09-20 Milestone batch 3: Q3/Q4 Tier-X + queue at 4/6 (forced exhaustion-route return pending)

**Decision**: Record Q3 and Q4 of the standing Tier-X re-analysis queue (zero data consumption, worktree-only records) and the queue state 4/6 used. The cap/pool-exhaustion rule now FORCES a return to the user-owned exhaustion-route decision (operating-point redesign / data acquisition / closeout), which remains PENDING user decision.

**Context**: Q3 (`Q3_DESCRIPTIVE_ONLY`, focused review PASS): 92 records / 26 within-packet pairs; both_fail 3/3/3/3/3/3/1 = 19; restored 0/0/0/0/1/2/4 = 7 (S5 P20N n=4→1, S6 P20O n=5→2, S7 P20Q n=5→4); cross-packet pooling is forbidden and was not performed; the 1/4→2/5→4/5 narrative trend reading is forbidden; the prereg "91 vs 92" narrative-vs-per-file discrepancy is disclosed and left unrepaired, pending main-thread adjudication. Q4 (`Q4_DESCRIPTIVE_ONLY` + `Q4_UNDETECTED_ALL_ZERO` + `Q4_STATUS_COHERENCE_NO_ANOMALY_READINGS`, focused review PASS): 165 records / 18 aggregates; archive-complete status {verify_failed 109, exact 56}; accepted-subset (17 roots, P20S superseded isolated) {108, 54}; 46 located `undetected` values all zero, 17 `undetected_zero` flags; P20G blocked-stub contributes 0 records; A1–A8 anomaly counters all zero, BUT A8 is evaluable only on 150/165 records (P19 lacks a deployable key on 15 records) — the coherence token must not be read as 165-record coverage. Guard-tamper incident: an out-of-root `ropen`/`check_finite` on an in-root module overwrote both accepted artifacts with stop payloads; recovery by deterministic re-execution was verified byte-identical (science fields identical; only the executed-body sha differs, by a path patch); the executed-body sha is now recorded and verified for all four queue probes; no post-run field corrections. Queue state: Q1, Q2, Q3, Q4 used (4/6); Q5 remaining (TRAIN counts structure — only meaningful if an L2 redesign is chosen); Q6 remains retired.

**Alternatives considered**:
- Reading Q3's per-segment restored counts (0/0/0/0/1/2/4) or Q4's subset aggregates as a trend, reliability, FER or efficiency claim: rejected — Tier-X descriptive only, within-scope, no thresholds; cross-packet pooling and the 1/4→2/5→4/5 narrative are explicitly forbidden.
- Reading the Q4 status-coherence token as full 165-record coverage: rejected — A8 is evaluable on 150/165 only; the token records absence of anomaly readings, not coverage.
- Repairing the Q3 prereg "91 vs 92" discrepancy in-packet or extending the queue past the cap: rejected — the discrepancy is disclosed for main-thread adjudication, and the cap is the forced-return mechanism, not a soft limit.

**Consequences**: No execution, no protected opens, no data consumption in this batch; all four queue probe records stay worktree-only under `workspace/probes/` (gitignored by design); this entry is the durable record. The queue may not silently extend: the exhaustion-route return (operating-point redesign / acquisition / closeout) is forced and awaits the user decision; Q5 stays conditional on an L2-redesign choice.

## 2026-09-20 Route A: N=32768 real-data ladder formally closed (population exhaustion terminal)

**Decision**: Record the formal closeout of the N=32768 real-data ladder as `TARGET_EMPIRICAL_N32768_REAL_DATA_LADDER_CLOSED_POPULATION_EXHAUSTION` — a population-exhaustion terminal, NOT a verdict closure. Route A user-decided 2026-09-20 (A+B parallel; route B scoping proceeds in parallel).

**Context**: (i) Ledger end-state — DEV 3595..3626 (32 frames × 256 = 8192 pairs) CONSUMED by P20T; remainder 3627..3644 (18 frames / 4608 pairs) + 1.5M VAL stub 2172..2212 (41/10,496) + 1.5M HOLD 2725..2766 (42/10,752) never-decoded; 0 formable full N=32768 blocks remain under any authorized rule (same-split only; 1.5M↔2M mixing forever forbidden). (ii) What the ladder produced — all descriptive, no FER/reliability/efficiency claim: construction-side 1/4→2/5→4/5 across three independent segments (P20N/P20O/P20Q; the trend narrative is FORBIDDEN — three construction events across three segments license no reliability reading); order-side 0/1 negative (P20R, block-dominated — the oracle pair also failed, so the negative does not discriminate the order factor); reduced-N N=8192 n=1 no-bite (P20T, within-N only, non-transferable); H2 v2 verdicts (H2a REFUTED, H2b/c SUPPORTED, H2d flat, H2e geometry-incoherent — descriptive re-adjudication on 59 rows, truncated vs full-block scopes never pooled); Q2 multi-root replication (A≡O / B-differs, byte-exact); Q3 within-packet restored 0/0/0/0/1/2/4 (cross-packet pooling forbidden). (iii) What it did NOT produce — stage-2 replication, any threshold/pass verdict, any cross-N inference, or any SCL conclusion (the synthetic line is non-informative at two operating points: X16 d=0.75 and G3 d=0.90).

**Alternatives considered**:
- Reading the closeout as a verdict (negative or positive) on the alt-L2 construction or the order factor: rejected — population exhaustion ends the data, not the hypothesis; the descriptive record stands without a verdict.
- Mixing 1.5M and 2M splits or reopening consumed DEV to form more N=32768 blocks: rejected — forbidden under every authorized rule (same-split; no DEV reopen on a consumed block).
- Continuing real-data execution under route A after this closeout: rejected — nothing formable remains; further real-data work requires route B (operating-point redesign) or route C (acquisition, user-side).

**Consequences**: No further real-data execution is possible without route B (operating-point redesign) or route C (acquisition, user-side). This closeout changes no frozen evidence: every accepted packet, review, and ledger entry stays as recorded. The Tier-X queue continues unaffected (4/6 used; Q5 conditional on an L2-redesign choice; Q6 retired). SCL stays locked. Next work: route B scoping (planner, in parallel) — no construction, data reads, or execution authorized.

## 2026-09-20 Route B: B2 axis = C-P1 (disclosure placement) + B3 freeze review PASS

**Decision**: (i) B2 axis selection (user-authorized 2026-09-20): axis (i) disclosure PLACEMENT, minimum-delta candidate C-P1 — hazard-ranked L2 disclosure placement at the G3-verbatim triple (N=16384, K1=167 first-natural L1 true-u1 conditioning, K2=3373 L2 forced-correct, diagonal pin d=0.90 X15-recipe shape). Placement-invariance (single-factor attribution): the disclosed SET changes, the disclosed COUNT does not — K2/N = 3373/16384 under either placement, so the applicable no-information ceiling (1 − K2/N) × 31/32 = 0.7693119049072266 is placement-invariant and any in-band reading is attributable to placement alone. G1 mismatch band [0.05, 0.719]: margin rule M ≥ 50 × recorded max |Δ| = 50 × 0.00099 = 0.0495; high-edge candidates 0.7693119049072266 − 0.0495 = 0.7198119049072266 and 0.7693119049072266 − 0.05 = 0.7193119049072266; frozen high edge 0.719 is the conservative truncation below both candidates; low edge 0.05 carried (X17-P proves 0.000 reachable, so ≤ 0.05 leaves no room for downstream list gain). Differ proof: C-P1 differs from all four proven-pointless configs — G3 (placement only; N, K amounts, channel identical), X16 (N plus placement), X14/X15 (all axes). The G3 first-natural reading at this exact triple (seeds 2026092501..2508; pooled mismatch 0.770302 → `SCLW_STOP_SANITY_HIGH`) is NOT re-run inside C-P1; C-P1 runs hazard-ranked placement only, on fresh seeds. (ii) B3 independent freeze review: `PASS_WITH_FINDINGS_20260920` — F1 `BR_STOP_SC_CONSISTENCY` re-encode self-check carried into the body plan at the same 3 raise sites as G3's `SCLW_STOP_SC_CONSISTENCY` (full-block sc re-encode; small-block sc re-encode; list re-encode), rationale: the B4 body re-runs the frozen `sc.py` path and G3's self-check must not be silently lost; F2 `BR_STOP_SANITY_LOW` sub-0.05 readings clarified as recorded descriptively with execution PROCEEDING (retire-or-re-ask-once within budget) so the implementer does not halt on a low reading. Both findings are fixed in this batch. The ceiling/margin arithmetic and the seed grep were independently re-verified; probe root `workspace/probes/b1-placement-hazard-ranked/` target-absence confirmed; seeds 2026092600..2026092619 reserved-NOT-activated.

**Context**: Route B (user-decided 2026-09-20, parallel with route A) = L2 model/representation + disclosure-placement redesign; scoping committed `0ea05c3a`. The freeze packet is `.workbuddy/queue/NBPOLAR-L2-REPRESENTATION-REDESIGN/` (FREEZE_DRAFT.md + STATUS.yaml; state `DRAFT_NOT_FROZEN_NOT_AUTHORIZED`); every number in it is read from already-committed records (design.md (b) C-P1 candidate + band rule, the G3 freeze draft and probe-root prereg, decision-log G3 + geometry-mining entries, X16 packet). No artifact was read, no decoder was run, no protected open, zero data contact in producing or reviewing this packet.

**Alternatives considered**:
- Re-running the G3 first-natural reading at this triple inside C-P1: rejected — the point is already proven; C-P1 asks placement only, on fresh seeds.
- Reading the B3 PASS_WITH_FINDINGS as freeze, implementation, or execution authorization: rejected — B4 implementation and B6 execution remain separate explicit user gates; the review verdict authorizes nothing.
- Activating the reserved seed band 2026092600..2026092619 now: rejected — reserved-NOT-activated; re-grep is required at any future freeze.

**Consequences**: B4 implementation and B6 execution still require separate explicit user authorization (`next_gate: B4_IMPLEMENTATION_AUTHORIZATION_PENDING_USER`). All execution/implementation counters stay 0 and SCL stays locked (`scl-synthetic-list-gate` track untouched; its G0–G6 gates remain NOT AUTHORIZED); Q5 stays retired-conditional (axis (i) selected at B2, not (iii)). Zero real-data contact; `sc.py` and all `formal_ir/nbpolar/` existing modules stay frozen untouched (read-only import only).

## 2026-09-20/21 Route B C-P1: RETIRE-ceiling (axis i retired; forced switch to axis ii)

**Decision**: Record C-P1 (hazard-ranked L2 disclosure placement at the G3-verbatim triple N=16384, K1=167 first-natural L1 true-u1 conditioning, K2=3373 L2 forced-correct, diagonal pin d=0.90 X15-recipe shape) as B6 execution COMPLETE, B7 focused review PASS_WITH_FINDINGS, and B8 disposition RETIRE-ceiling per the pre-registered decision rule: charge 1 probe to axis (i); RETIRE-ceiling; RETIRE axis (i); forced switch to axis (ii) — C-P2 (tiered/non-contiguous disclosure amount) at the same triple. Route budget now 1/6. SCL lock re-stated; Q5 stays retired-conditional. No FER/reliability/efficiency claim; zero real-data contact.

**Context**: Reading: hazard-ranked placement at the G3-verbatim triple → pooled greedy-SC mismatch 0.7681045532226562 (100677/131072) vs placement-invariant ceiling 0.7693119049072266 (delta −0.0012073516845703); G1 band [0.05, 0.719] FAIL (above the high edge by 0.04910); per-seed mean 0.768105 / std 0.001493 / range [0.765869, 0.769653]; effect vs G3 first-natural = 0.002197265625 (≈2.2× the recorded noise 0.00099, ≈23× short of the band margin) → placement moved the needle but nowhere near the band: ceiling-hugging repeat under hazard-ranked placement too. Wiring green: G2 0.999754 ≥ 0.50; G3 0.098907 ∈ band (strata 10/10336/2618/118108 = 131072). Q2: coverage_local_spike 0.0 STRUCTURALLY DEGENERATE (disclosed set = F-median8 top-K2 set, forced-correct → tautology, NOT a finding); coverage_mean_hazard 0.046455 genuine but small. B7 focused review PASS_WITH_FINDINGS: F1 Q2 degeneracy annotate-not-read; F2 F1 raise-site 3 adapted — sites 2/3 under --selftest, site 1 full-block sc re-encode ran on all 8 blocks; F3 budget disposition + cosmetic size_bytes self-report 49561 vs on-disk 49860, both ≪ 2MB. Provenance: prereg byte-identical to FREEZE_DRAFT §3 (sha 20506798…), 1 execution / 0 reruns, seeds 2026092601..2608 only, tag_calls 0, decoder_calls 8 (frozen sc.py only, git-clean), worktree-only probe root.

**Alternatives considered**:
- Reading the 0.002197265625 effect vs G3 first-natural as a placement gain or in-band progress: rejected — ≈2.2× recorded noise and ≈23× short of the band margin; the G1 band FAIL is the pre-registered reading, so the point retires as ceiling-hugging.
- Reading Q2 coverage_local_spike 0.0 as a localization finding: rejected — structurally degenerate (the disclosed set IS the F-median8 top-K2 set and is forced-correct, so 0.0 is a tautology); per B7 F1 it is annotated, not read.
- Charging a second probe to axis (i) or amending the placement in-packet to chase the band: rejected — the pre-registered decision rule retires axis (i) after one probe and forces the axis (ii) switch; a same-axis retry would exceed the intent of the max-2-per-axis budget rule.
- Treating the B8 disposition as authorization for C-P2: rejected — C-P2 needs its own B3-style freeze review plus explicit user authorization; the disposition authorizes nothing.

**Consequences**: Axis (i) disclosure placement retired (ceiling-hugging at the frozen triple under both first-natural and hazard-ranked placement); route budget 1/6 used; next gate = C-P2 freeze draft (axis (ii) tiered/non-contiguous disclosure amount at the same triple) pending B3-style review + user authorization. SCL stays locked; Q5 stays retired-conditional; no FER/reliability/efficiency claim; zero real-data contact; `sc.py` and all `formal_ir/nbpolar/` existing modules stay frozen untouched (read-only import only); the probe record stays worktree-only under `workspace/probes/b1-placement-hazard-ranked/` (gitignored by design); this entry is the durable record.

## 2026-09-21 Route B C-P2 freeze review PASS (M=0.065 adjudicated; axis ii amount/structure)

**Decision**: C-P2 (axis (ii) — L2 disclosure AMOUNT/STRUCTURE at the G3-verbatim triple) freeze review PASS_WITH_FINDINGS_20260921, findings F1-F3 fixed in this batch; the one open decision of draft §2.1 is adjudicated M = 0.065. Route budget 2/6 after C-P2; B4 implementation and B6 execution still require explicit user authorization.

**Context**: Variants V1a-V1d (amount ladder K2' = 2349/2861/3885/4397 first-natural contiguous, tier step 512), V2 (structure at fixed count 3373: first-natural tier-1 2349 + stride-13 spread tier-2 1024) and V3 (hazard-derived tier-1 F-median8 top-1024 + exact even-spread tier-2 2349 at fixed count 3373) at the G3-verbatim triple (N=16384, K1=167 first-natural L1, d=0.90 X15-recipe shape), each banded against its OWN exactly-recomputed ceiling (ceiling(K2') = (16384 - K2') x 31/524288). Noise record updated: max |delta| = 0.0012073516845703125 (C-P1) replaces 0.00099, so M >= 50 x 0.0012073516845703125 = 0.060367584228515625; retaining M = 0.05 would give only 41.4x < 50x (nominal-M basis, same as the M = 0.065 -> 53.8x figure) and is NON-COMPLIANT, so M = 0.065 is rule-correct (independent review confirmed the rule application; M = 0.05 rejected). Q2 local-spike arm DROPPED on V3 (hazard-derived tier-1 makes the detector-vs-detector contrast structurally tautological - C-P1's 0.0 was a tautology, not a finding); V3 keeps mean-hazard coverage as a single-detector descriptive scalar only. Seeds 2026092800..2026092819 reserved-NOT-activated (re-grep required at freeze before activation); V3 tier-2 pinned to an exact deterministic rule (indices floor(j*L/2349), L = 15360, strictly increasing => 2349 distinct positions by construction; K2' = 3373 exact). Findings fixed: F1 zero-hit grep claims scoped like the C-P1 precedent (zero hits in workspace/probes/, any body, results.json, tag files; packet-doc reservation lines excepted; command #3 expectation restated accordingly); F2 the loose "stride-6 spread of the first 2349 non-tier-1 positions" replaced by the exact even-spread rule with dedup-by-construction and a B5 disclosed-set size assert (|tier-2| = 2349, K2' = 3373); F3 M multiples restated on a consistent nominal-M basis (M=0.05 -> 41.4x, M=0.065 -> 53.8x). No implementation, no execution, no protected opens, no decoder runs, zero data contact; SCL stays locked; Q5 stays retired-conditional.

**Alternatives considered**:
- Retaining M = 0.05 with the updated noise record: rejected - 41.4x < 50x violates the derivation rule; M = 0.05 is only available by explicitly retaining the stale 0.00099 noise record with a stated reason, which the review did not support.
- Reading the freeze-review PASS as implementation/execution authorization: rejected - B4 and B6 remain separate explicit user gates; the review verdict authorizes nothing.
- Carrying the Q2 local-spike arm on V3: rejected - under hazard-derived tier-1 placement the local-spike detector's top set overlaps the disclosed set by construction, so any coverage reading mixes a forced-correct artifact with signal (C-P1's tautological 0.0).

**Consequences**: C-P2 freeze draft is reviewed but NOT FROZEN and NOT AUTHORIZED: B4 implementation and B6 execution still require explicit user authorization (`next_gate: C_P2_B4_IMPLEMENTATION_PENDING_USER`). Route budget 2/6 used; all execution/implementation counters stay 0; SCL stays locked; Q5 stays retired-conditional; zero real-data contact; `sc.py` and all `formal_ir/nbpolar/` existing modules stay frozen untouched (read-only import only); the probe root `workspace/probes/b2-amount-structure/` does not yet exist and seed band 2026092800..2026092819 stays reserved-NOT-activated; this entry is the durable record.

## 2026-09-21 Literature fit-check corrections applied (SciVerse original-text verification)

**Decision**: Record the SciVerse original-text verification corrections as durable literature semantics. Metadata: Tarable 2024 DOI corrected to `10.1109/TQE.2024.3361810` — the user-supplied `10418979` is an Xplore document ID, not a DOI — and `docs/hd-qkd-ir-performance-roadmap-20260824.md:240` is updated to cite the DOI; the Ogrodnik journal version `10.1364/opticaq.560373` (Optica Quantum 2025) is preferred over the arXiv preprint. Content corrections: (i) Müller 2024 has NO own real data — HD-Cascade was evaluated entirely on QSC simulation (q=4/8/32, QBER 1–20%), and the "4D experiment" only borrowed setup parameters from a recent 4D-QKD implementation for SKR extrapolation → our real-ToA + empirical-channel differentiation boundary is LARGER than previously recorded; (ii) counterintuitive original finding recorded: HD-Cascade message count seems to DECREASE with increasing dimension — a mandatory citation line for any interaction-cost claim; (iii) Scarinzi 2025 — the winning adaptive quantity is the per-block mean channel capacity C̄, with mean QBER as the DEFEATED baseline (the previous "mean QSER" wording is corrected); block-average LLR ≡ full LLR for their setting — equivalence in OUR empirical-channel regime is an open probe question and must not be transferred without a probe; (iv) Zahidy 2024 `f_err,4D = 1.06` is a verbatim *estimated* value built on borrowed Cascade plus a binaryized-entropy denominator → the AGENTS.md §5.5 textbook case, forbidden as measured efficiency; (v) Ogrodnik 2025 experiment only reaches 4D (d=8 simulated) and its key rates are self-described *simplistic* — a mandatory qualifier; (vi) Kanitschar & Huber 2025 downgraded — entangled HD-QKD, not directly applicable to ToA prepare-and-measure. Independence register: three non-independent groups — Scarinzi ↔ Tarable via Ferrari; AIR ↔ SLA via Tang / Bo Liu; Müller 2024 ↔ 2025 ↔ Zahidy 2024 same DTU + CNR/UNIFI group — within-group cross-corroboration is forbidden and surface reference count ≠ independent-evidence count. Unverified/excluded: Müller 2025 numbers (`6.7 kbit/s`, `f=1.036 / 1.166`, `446 vs 3.14 messages`, `FER<0.003`) are tagged unverified because the SciVerse full text is not indexed; the retracted paper's arXiv `2101.12565` is explicitly excluded (retraction `10.1007/s11082-024-07829-y`; the repository's Mao Entropy 2021 citation is unaffected); Qi Han 2019 (60 Mbps, f≈1.1) is recorded as an unretracted CPU-throughput anchor.

**Context**: The literature fit-check (`docs/nbpolar/LITERATURE_FIT_CHECK_20260921.md`) re-verified every literature entry used in NB-Polar planning against original text via SciVerse. The repository-side doc edits (roadmap:240 DOI swap, survey annotations, §5 red lines, independence register, unverified tags) were already applied in `84e77bba`; this entry is the deferred durable decision-log record. These corrections touch no algorithm, code, config, or execution state.

**Alternatives considered**:
- Keep "mean QSER" as the Scarinzi adaptive quantity: rejected — the original text shows mean QBER was the defeated baseline and per-block mean channel capacity C̄ was the winning quantity.
- Transfer Scarinzi's block-average-LLR ≡ full-LLR equivalence into our empirical-channel regime: rejected — the equivalence holds only for their setting; in our regime it is an open probe question requiring its own probe.
- Cite Müller 2024 as real-data HD-Cascade evidence: rejected — the paper has no own real data (QSC simulation only; the 4D setup parameters were borrowed for SKR extrapolation).
- Use Zahidy 2024 `f_err,4D = 1.06` as a measured reconciliation-efficiency value: rejected — §5.5; it is *estimated* from borrowed Cascade with a binaryized-entropy denominator.
- Count AIR and SLA, the Müller/Zahidy DTU group, or Scarinzi/Tarable as independent corroboration: rejected — the independence register forbids within-group cross-corroboration.
- Treat the Müller 2025 numbers as verified: rejected — the SciVerse full text is not indexed; they stay unverified until the OA PDF is checked.
- Use the retracted paper's arXiv `2101.12565` (570 Mbps / f=1.038) as a throughput benchmark: rejected — retracted (`10.1007/s11082-024-07829-y`); Qi Han 2019 is the unretracted CPU-throughput anchor.

**Consequences**: The adaptive-quantity decision is recorded as per-block C̄ (feeds the future route-B axis (iii) / Q5 probe line). No algorithm or execution change; no claim-bearing use of literature f values. Any interaction-cost claim citing HD-Cascade must carry the decreasing-message-count citation line; Ogrodnik key rates must carry the *simplistic* + 4D-only qualifier; Kanitschar & Huber stays downgraded unless a prepare-and-measure version of its framework appears.

## 2026-09-21 Müller 2025 / Zhou AIR / Kanitschar PDF verification (appendix C) — numbers verified, f_eff contract externalized

**Decision**: Record the user-provided PDF verification (`pdftotext -layout`, appendix C of `docs/nbpolar/LITERATURE_FIT_CHECK_20260921.md`) as durable literature semantics: (a) all four previously-unverified Müller 2025 numbers are now VERIFIED verbatim — ~27 h acquisition, ~6.7 kbit/s post-sift acquisition rate, f_Cascade = 1.036 / f_LDPC = 1.166, mean messages 446 vs 3.14, Cascade FER < 0.003 on 1000 samples — and the original "The blind protocol has no frame errors by design" quote CONFIRMS our existing no-equivalence rule (blind-LDPC "no frame error" is a protocol design property, never evidence for finite-budget exact recovery); (b) KEY ADOPTION: the §2.2 λ_total contract does not need to be invented — adopt Müller 2025 eq (11)/(13) f_eff = (1−FER_cluster−P_Collision)·f + (FER_cluster+P_Collision)/H(q) + t/(n·H(q)), i.e. per-frame expected leakage nH(q)·f_eff = leak_IR + n(FER_cluster+P_Collision) + t, with FER_cluster = 1−(1−FER)^k (k = clustered frames), t = 50 bits EV tag, P_Collision = 1e-10, and failed frames leaking all n bits ("all n bits are assumed to be leaked to adhere to security"); citation chain B1/Martínez-Mateo 2014 (f_FER) → Müller 2025 (f_eff eq 11). The q-ary adaptation rule (replace H(q) with empirical H(X|Y)) is recorded as a rule only — it is NOT applied to any frozen number, the 34119-bit budget stays frozen, and any re-derivation requires a new preregistration, never post-hoc. (c) Protocol-layer candidate recorded (zero data consumption): clustered verification + one repeat request (Müller: "more than 40 frames clustered together being optimal in some cases") as an alternative to our current per-frame independent Toeplitz tag — a future protocol candidate requiring its own OpenSpec change/freeze, not authorized here. (d) Project-justification citation recorded from the Müller 2025 Discussion: the analysis assumes a binary symmetric / iid channel, "how well the actual channels of QKD devices follow these assumptions is still not well researched", the only HD channel model mentioned anywhere is high-dimensional energy-time entanglement, and the authors explicitly encourage study of non-memoryless channels' impact on the efficiency measure itself. (e) Zhou 2022 AIR verified: f = 1.046 at 1 Gb block / QBER 0.02, overall failure probability ≈ 1e-8, and 4× smaller block than SLA; mechanism is gradual disclosure of high-error-probability polarized channels (isomorphic to NB-Polar nested disclosure); the transferable item is treating failure probability as an allocatable per-round budget ε_i — we currently only count outcomes and do not allocate budgets. (f) Kanitschar & Huber 2025 stays DOWNGRADED: entangled time-/frequency-bin HD-QKD, finite-size security lives in the companion paper [40], not applicable to our ToA prepare-and-measure data; any citation must carry that qualifier.

**Context**: Appendix C of the fit-check verified three user-provided PDFs section by section after `pdftotext -layout` extraction. The Müller 2025 paper's eq (11)/(13) turned out to be the exact original of the λ_total contract the repo was about to invent for itself, including the failed-frame-whole-frame-leaked convention that B2.2 had identified as the missing piece. The doc-side edits (appendix A.3 marked OBSOLETE-by-C.1 with a pointer, §5 Müller red lines updated to "numbers verified but binary/BSC long-frame — no GF32/ToA extrapolation, no blind-protocol equivalence") were applied in this same batch; no other file is touched.

**Alternatives considered**:
- Apply the q-ary adaptation (H(q) → empirical H(X|Y)) to the frozen 34119 budget now: rejected — the adaptation rule is recorded but no frozen number may move without a new preregistration; post-hoc re-derivation is forbidden.
- Treat the clustered-verification + repeat-request mechanism as an adopted protocol change: rejected — recorded as a candidate only; it needs its own change/freeze and explicit authorization before any implementation.
- Use the verified Müller 2025 numbers as GF32/ToA performance evidence: rejected — they are binary/BSC long-frame industrial results; verification of the numbers does not license cross-domain extrapolation (§5 red line, `roadmap:246`).
- Equate blind-LDPC "no frame errors by design" with finite-budget exact recovery: rejected — the original text's *by design* qualifier confirms the distinction; `undetected` and `verify_failed` stay independently counted (AGENTS.md §5.5).
- Cite Kanitschar & Huber for prepare-and-measure ToA net-key security: rejected — entangled HD-QKD framework with finite-size in the companion paper [40]; not applicable without the qualifier.

**Consequences**: Literature accounting for the f_eff / λ_total contract is now externally anchored (no self-invented contract); the §2.2 contract change can cite Müller 2025 eq (11)/(13) with the B1(2014) prototype chain. No algorithm, code, config, or execution change; no frozen number touched (34119 budget unchanged); no claim-bearing use of the verified numbers; the clustered-verification protocol candidate is queued as a future change requiring its own freeze.

## 2026-09-21 Correction: protocol identity is entanglement-based (not prepare-and-measure); KH25 upgraded, novelty claim narrowed

**Decision**: Correct a confirmed protocol-identity error and its downstream literature consequences. This project's HD-QKD data is **entanglement-based, coincidence-detected**: Type-II SPDC `TypeII_776.1nm_3s`; the two hardware channels A/B are paired by `_pair_nearest_unique` (def `src/qkd_io/ttbin_pipeline.py:219`, invoked :420) yielding `coincidence_rate_hz` (:422); PIE = key bits per coincidence (`docs/SECURITY_MODEL.md:11-13`); time-bin layer = high-dimensional arrival-time encoding (`:28`); polarization layer = BBM92-type (`:29`). It is **NOT prepare-and-measure**. Four earlier items are therefore **SUPERSEDED** — marked here by line number, not deleted or rewritten: (1) `docs/decision-log.md:5092` item (vi) "Kanitschar & Huber 2025 downgraded — entangled HD-QKD, not directly applicable to ToA prepare-and-measure"; (2) `docs/decision-log.md:5105` "Kanitschar & Huber stays downgraded unless a prepare-and-measure version of its framework appears"; (3) `docs/decision-log.md:5109` item (f) "Kanitschar & Huber 2025 stays DOWNGRADED: … not applicable to our ToA prepare-and-measure data; any citation must carry that qualifier"; (4) `docs/decision-log.md:5118` "Cite Kanitschar & Huber for prepare-and-measure ToA net-key security: rejected — entangled HD-QKD framework with finite-size in the companion paper [40]; not applicable without the qualifier." **Verdict adopted**: Kanitschar & Huber 2025 (KH25, PRL 135, 010802) is **A-grade RELEVANT** for the key-rate/security framework (upgraded from the prior downgrade). The information-reconciliation novelty claim is **narrowed** (see Context).

**Context**: (i) KH25 structural fit — its demonstration state |Ψ₁⟩ = |DD⟩ ⊗ (1/√d)Σ_k|kk⟩ maps onto our polarization layer (BBM92-type, the |DD⟩ factor) plus the time-bin arrival-time layer (the maximally-entangled (1/√d)Σ_k|kk⟩ factor); T_T (ToA) is exactly our measurement; its key rate is reported in **bits per coincidence event**, the same denominator as our PIE; "Our method works generically … requiring only partial information about the density matrix" is drivable from measured statistics (no full tomography); the noise model is "only for demonstration … we do not rely on any particular noise model" and can be replaced by our empirical P(y|x). This is the protocol-investigation evidence chain in `docs/nbpolar/LITERATURE_FIT_CHECK_20260921.md` Appendix D (D.1–D.3), independently confirmed by a read-only reviewer with ≥3 independent evidence lines. (ii) Two retained qualifiers — (a) KH25 explicitly **excludes IR**: H(X|Y) is "purely classical … we focus on the first term", so our λ_EC is an **exogenous input** to it (complementary, not competing) and KH25 gives **no input** to disclosure placement/amount/decoder choice; (b) finite-size/composition lives only in the companion arXiv:2505.03874, so any finite-key citation of KH25 must carry it. (iii) Novelty narrowing (mandatory consequence) — the Boutros–Soljanin line A1 (Boutros & Soljanin, IEEE Trans. Commun. 2023, `10.1109/TCOMM.2023.3302135`) is the mainstream TE-QKD IR literature on our own data model, so we must **NO LONGER claim "no one has done IR on ToA/high-dimensional"**. The acceptable narrow claim: A1/A2/A3 build on Gaussian-jitter + iid + memoryless models/simulation (A3 verbatim "the induced … channel is memoryless under the adopted model"; no detector dead-time), whereas we use real Type-II ToA coincidence data + empirical P(y|x) + explicit memory testing (A2 Markov model) + verification-aware λ_total + measured FER/interaction/throughput → net key. (iv) Müller 2025 scoping — its "only mentioned HD channel model is high-dimensional energy-time entanglement" is scoped to its BSC/iid-assumption Discussion; usable as the "assumptions unverified, non-memoryless channels under-researched" project-justification citation, **NEVER** as a uniqueness claim about the literature. (v) Physical-layer anchor — Zhong, Zhou et al., New J. Phys. 17, 022002 (2015), origin of "bits per coincidence", already cited by `SECURITY_MODEL.md:101`; it was omitted from the literature table across survey rounds and should be added as the physical-layer anchor (omission noted).

**Alternatives considered**:
- Keep KH25 downgraded because it is "entangled, not P&M": rejected — that ground inverted the error; our data is itself entanglement-based, so KH25's entangled HD-QKD framework is structurally on-target, not off-target.
- Read the KH25 upgrade as an IR/disclosure/decoder input: rejected — KH25 explicitly excludes H(X|Y); the upgrade is scoped to the key-rate/security outer framework, and our λ_EC stays an exogenous input to it.
- Cite KH25 finite-size from the PRL alone: rejected — finite-size/composition is only in the companion arXiv:2505.03874 and must be cited together.
- Retain the broad "no prior IR on ToA/HD" novelty claim: rejected — Boutros–Soljanin A1 (TCOM 2023) is exactly that work; the claim is narrowed to the model/verification differential above.
- Treat Müller 2025's energy-time-entanglement mention as literature-uniqueness evidence: rejected — it is scoped to the BSC/iid-assumption Discussion and serves only as project justification.

**Cautions**: (a) "Zhong-like" is a **method label**, not a source-identity claim — the repo repeatedly disclaims strict Zhong instantiation (e.g. `POLAR_CODE_MAINFLOW_20260327.md:181-185`). (b) Not established anywhere in the repo; requires **user confirmation before any formal claim**: Franson-interferometric vs non-interferometric energy-time correlation; which hardware channel is Alice vs Bob; whether the polarization and time-bin registers come from the same acquisition or separate arms; the meaning of `600k`/`1p2M` (low-confidence inference = source brightness/coincidence scale); `1M`/`1p5M`/`2M` are acquisition/session identifiers and `_0dB` = loss setting.

**Consequences**: The four cited decision-log items are superseded in meaning but kept for provenance. KH25 is upgraded to A-grade for the key-rate/security framework, carrying the two qualifiers (IR excluded; finite-size in companion arXiv:2505.03874). The broad TE-QKD IR novelty claim is retracted and narrowed to the model/verification differential. Companion doc corrections: `docs/nbpolar/PAPER_READ_20260921.md` (KH25 verdict rows) and `docs/nbpolar/LITERATURE_FIT_CHECK_20260921.md` (Appendix D + inline strikethroughs, already applied). No algorithm, code, config, or execution change; no frozen number touched; no protected-data contact.

## 2026-09-21 PI rulings on protocol identity + data-scale parameters (R1/R2/R3)

**Decision**: Record three verbatim PI rulings that supersede-by-clarification the caution at `:5135(b)`: (R1) the data is **time-energy entanglement**; this project's object is the **information-reconciliation (IR) part of CW high-dimensional time-of-arrival (ToA) encoding** — independent of downstream security protocols and of whether polarization is used; Alice/Bob assignment is equivalent regardless of which arm. (R2) `600k` / `1p2M` denote **data-scale parameters such as wide-spectrum noise level or maximum single counts**, not protocol identity. (R3) PI is aware **prior IR work on ToA/high-dimensional exists**; every form of "no one has done IR on ToA/high-dimensional" is therefore **deleted**.

**Context**: The `:5135(b)` caution listed four blanks requiring user confirmation before any formal claim: Franson-interferometric vs non-interferometric energy-time correlation; which hardware channel is Alice vs Bob; whether polarization and time-bin registers come from the same acquisition or separate arms; the meaning of `600k`/`1p2M`. R1–R3 resolve these at the IR axis, not the physics axis. Macro-plan: `docs/nbpolar/MACRO_PLAN_20260921.md` §0.

**Alternatives considered**:
- Keep all four blanks as confirmation-gated for formal IR statements: rejected — R1/R2 make three of them non-observables on the IR axis; gating IR claims on them would block statements that do not depend on them.
- Treat R1 as changing the data pipeline or decoder scope: rejected — R1 is a scoping clarification only; no algorithm, code, config, or execution change.
- Read R3 as affecting only future papers: rejected — R3 requires deletion across the whole repo, including planning docs and PAPER_READ.

**Consequences**: Three of the four `:5135(b)` blanks (Alice/Bob assignment, same-vs-separate acquisition, `600k`/`1p2M`) become non-observables on the IR axis and require no confirmation for formal IR statements. The Franson item is demoted to a physical-layer provenance note and does not enter IR claims.

**Cautions**: R1–R3 are PI rulings on scope and narrative, not measurements; they authorize no execution and touch no frozen number. The Franson provenance note is retained, not deleted — it is only excluded from IR claims.

## 2026-09-21 Novelty claim narrowed (R3): minimum claim available now

**Decision**: Delete all "no prior ToA/HD IR" phrasing repo-wide (R3). Adopt the §4 wording: existing TE-QKD reconciliation work (A1/A2/A3) is built on **Gaussian jitter + iid + memoryless** models/simulations; we report measured q-ary (GF(32)) Polar reconciliation results on **real CW time-energy-entanglement ToA coincidence data** — empirical P(y|x) channel instead of QSC/BSC, explicit memoryless-assumption testing, verification-aware λ_total accounting, measured FER, interaction rounds and throughput. Record the minimum claim available now (no need to wait for the representation question): at **fixed disclosure budget, zero disclosure increment**, changing only the empirical-prior smoothing (alt-L2 Laplace-α1) lifts full-block recovery from **A 0/14 to B 7/14**, reproduced across two independent sessions (P20N 1/4, P20O 2/5, P20Q 4/5), `undetected` isolated at 0 throughout, integrity gates all green.

**Context**: A1 = Boutros & Soljanin, IEEE Trans. Commun. 2023, `10.1109/TCOMM.2023.3302135` is exactly prior ToA/HD IR work, so the broad claim is indefensible. The defensible selling point per R3 is **working error correction on real-scene, real data**. The 0/14 → 7/14 record is descriptive of already-accepted packets (P20N/P20O/P20Q); this entry creates no new claim. Macro-plan: `docs/nbpolar/MACRO_PLAN_20260921.md` §4.

**Alternatives considered**:
- Retain a softened "first in ToA/high-dimensional" phrasing: rejected — A1 is exactly that work; any form is deleted, not softened.
- Wait for the representation (MFD/Gray) question before writing any claim: rejected — the 0/14 → 7/14 minimum claim does not depend on representation and is available now.
- Read the cross-session P20N/P20O/P20Q counts as a reliability trend: rejected — Tier-X descriptive discipline stands; the counts are reported as reproduced observations, not a trend verdict.

**Consequences**: PAPER_READ is narrowed accordingly (KH25 AXIS-SPLIT wording; overbroad "never use" bar corrected; placement+amount combination re-scoped to "within these three read papers" with A1 re-check required before any paper use). No algorithm, code, config, or execution change; no frozen number touched.

**Cautions**: The minimum claim stays within already-accepted evidence; it must not be extended to FER/efficiency/throughput comparisons without the Stage 3 measurement set (preregistered disclosure cap, per-block λ decomposition with H(q) → empirical H(X|Y) substitution preregistered, never post-hoc).

## 2026-09-21 S2/S4 zero-data discriminator results + C-P2 B4 NOT AUTHORIZED + A3 substitution downgraded

**Decision**: (i) Record the S2/S4 zero-data discriminator verdicts from Tier-X probe `workspace/probes/nbpolar_s2s4_zero_data_discriminators/` (non-claim, decoder-free, zero protected reads): H-A rate/finite-length **REFUTED** (54.8σ margin at frozen K2=6689, predicted FER≈0; reversal needs 555× V; ΔK2 = **−1382** to FER=0.01, i.e. 1382 symbols = 20.7% of K2 already surplus); H-B strong form (H2 mis-estimated) **REFUTED** (±0.3% estimation noise: MM +0.29%/+0.25%; split-half −0.31%/−0.28%, seed 20260920); H-B weak form (floor spike kills the SC path) **SUPPORTED** (floor hits 99.77%/99.75%; floor→bulk LLR span 48.8 bits; Laplace-α1 lifts floor 1e-15→~2e-3); H-C (A3 ±1 premise) **premise holds** (`delta_mass_le1 = 1.0000` both sessions linear+circular; posterior support median=p90=p99=max=2.0; H2=0.8004 ≈ h2(SER)=h2(0.2468)=0.8062). The earlier `2^(H2/SER) ≈ 9` heuristic ("errors are 3–4 bins wide") was **REFUTED by direct measurement** (residue-space artifact) and must not be reused. Record two zero-data-cost findings: (A) disclosure is mis-split between layers while the total is right (L1 f ≈ 2.0 over-disclosed by +112/+116/+115, L2 f ≈ 1.275 short by −126/−130/−129, totals ≈ 1.297–1.298 within ~13 symbols of f=1.3 Shannon — a finding, not a recommended experiment, since P19 `l2_plus` K2 6492→7004 (+512) already failed 0/3); (B) the A3 MFD definition is inapplicable under natural labeling (natural XOR-weight mean 1.9375 vs Gray 1.0000; A3 Definition 2 *"Thanks to the Gray code, the neighbor of zero has a unit Hamming weight"* makes unit weight a definitional premise). (ii) **C-P2 B4: NOT AUTHORIZED** (route budget 2/6 used, 4/6 remain) on three grounds: dispersion shows 54.8σ margin at frozen K2 with predicted FER≈0 ⇒ L2 amount is not the binding knob; the C-P2 freeze text (N=16384, K1=167 fixed, varying K2') tests exactly that surplus knob; the newly found defect is the inter-layer split ratio, which C-P2 does not test. NOT a rejection of axis (ii) forever — re-freeze required if Stage 1 later shows the amount axis binding. `next_gate` remains `C_P2_B4_IMPLEMENTATION_PENDING_USER` with this rationale recorded. (iii) A3 Corollary 1 substitution: performed only as a caveated design-perspective note (asymptotic diversity slope, not FER; Corollary 3 `R_c ≤ 1 − log2q/m` follows from sufficient condition `L < d_Hmin`, not iff; two-layer 5+5 bit architecture where the original text states partial weight enumeration "cannot lead to a general condition") — **consumes neither Tier-X 4/6 nor route-B 2/6** (pure arithmetic on frozen constants, not a probe) and **must not trigger representation switching**. Arithmetic archive: L = 16384 (32768 per layer); t ≤ 3375–3506; hard-decision bound `R_c ≤ 1 − 2·5/10 = 0`; soft-decision bound `R_c ≤ 1 − 5/10 = 0.5`; actual R = 0.784–0.794, outside both bounds; inverse: max q at R=0.79 under soft bound = **4**; q=32 needs m ≥ 24 (d = 2^24 bins), **unreachable**.

**Context**: The probe is Tier-X non-claim: no decoder, no protected reads, frozen constants only. The C-P2 freeze review PASS (`:5077`) authorized nothing; B4/B6 remain user gates. Stage 1 gate (S5 bounded search diagnostic `CRITICAL_PATH` 4.3 never run; S6 synthetic matched-channel control, 300 blocks from empirical P(y|x)) admits exactly one winning direction into Stage 2. Macro-plan: `docs/nbpolar/MACRO_PLAN_20260921.md` §§1–2, 5–6.

**Alternatives considered**:
- Authorize C-P2 B4 despite the dispersion margin: rejected — it would spend route budget testing a knob already shown 54.8σ in surplus.
- Recommend the constant-total split-rebalance (+130 to L2) as the next experiment: rejected — strictly weaker than the already-failed P19 l2_plus (+512, 0/3).
- Charge the A3 Corollary 1 arithmetic against Tier-X or route-B budget, or let it trigger representation switching: rejected — pure arithmetic on frozen constants; representation switching requires S3+S5+S6 jointly pointing.
- Reuse the `2^(H2/SER) ≈ 9` heuristic as error-width evidence: rejected — directly refuted by measurement.

**Consequences**: Route budget stays 2/6 used; `next_gate` unchanged (`C_P2_B4_IMPLEMENTATION_PENDING_USER`) with NOT-AUTHORIZED rationale recorded. Stage 2 prefers the prior/floor/support line (sole empirically supported direction: 7/14 vs 0/14); MFD/Gray labeling is the secondary arm; split-rebalance and C-P2 are not recommended. No execution, no protected opens, no data consumption; `sc.py` and all `formal_ir/nbpolar/` modules untouched; probe record stays worktree-only (gitignored by design); this entry is the durable record.

**Cautions**: All probe verdicts are non-claim-bearing (Tier-X); no FER/reliability/efficiency reading. The V67/V68/V69/V70 history trap applies — every one ended with `successor: new_representation` and produced no decoder evidence; the Stage 1 gate must be held by criteria that can see decode outcomes (S5/S6 class).

## 2026-09-21 PI ruling: correlation-based auto-alignment before pairing (R1 rewrite for the 10-acquisition census)

**Decision**: Before any pairing, derive the alignment offset from each acquisition's OWN timetag data via the correlation/dt-distribution peak (`_estimate_peak_stats_from_timetags`, `src/workflow/export_joint_sequence_sidecar.py:715`), applied to timestamps before binning/pairing. Never inherit the frozen `delay_used_ps = -50/+50/+50` (those belong to the 01-21 V25 sources). The inherited sigma gate `[50,150] ps` (calibrated for the 01-21 sources) is replaced, not widened, by a unit-independent acceptance: `status == "ok"` AND `peak_to_bg >= 10` (contrast ratio, scale-free); reject-only conditions are `status != "ok"`, `peak_to_bg < 10`, or no peak found. Frozen scan params: `scan_range_ps = max(50_000, 2*204800) = 409600`, `bin_ps = max(10, 200//2) = 100`, `frame_period_ps` not passed. A mandatory per-acquisition self-check requires the derived offset to maximize pairing yield (sweep over the search range at a coarse step; derived offset at or within one coarse step of the yield maximum), else `ALIGN_INCONSISTENT`.

**Context**: The measurement delay set during acquisition is not necessarily precise, so an inherited delay silently misaligns pairing. `legacy_v1` pairing only requires timestamp/bin-width/superframe unit-self-consistency; what breaks it is a wrong offset, and a correlation-derived offset in raw units is correct under any unit reading — so auto-alignment makes pairing immune to the ps-vs-0.1ps timestamp-unit ambiguity, which now affects only physical interpretation and cross-session comparability. Pilot evidence (same day, `workspace/census_20260921/20260112_Type2PPLN_3s/census.json`): offset `-50`, `peak_to_bg = 121.5`, sweep peaks at the derived offset (35402 at grid 0 vs 35399 at -50; within-one-step holds, strict exact-max fails by 3 pairs), `n_pairs ~ 35.4k` → 138 frames → `TIER_INSUFFICIENT`; no H emitted per R3. Packet refs: `.workbuddy/queue/NBPOLAR-DATA-CENSUS-HFULL-20260921/TASK_PACKET.md` §1.2/B1/stop-rules rewritten; `DURATION_TOKEN_VS_SPAN_DISCREPANCY_10X` stays open for interpretation/comparability.

**Alternatives considered**:
- Keep the inherited sigma `[50,150] ps` gate, or widen it until new sources pass: rejected — calibrated for different sources; widening to force a pass would be tuning.
- Inherit the frozen `-50/+50/+50` delays: rejected — they belong to the 01-21 V25 sources, and the PI instruction explicitly forbids it.
- Derive a per-acquisition skip to replace the inherited 702: rejected — that would be tuning on census data; 702 stays frozen with `INHERITED_NOT_DERIVED` label plus the non-decision first-1500 diagnostic.

**Consequences**: Stage B census pairs only at correlation-derived offsets with recorded `peak_center/sigma/to_bg`, offset sign convention `tA_aligned = tA_raw + offset`, and the yield-vs-offset sweep per acquisition. `ALIGN_FAIL` ⇒ exclude-and-continue; `ALIGN_INCONSISTENT` ⇒ record and stop loudly. No decoder, no threshold, and no pairing-rule change is authorized by this ruling.

**Cautions**: This ruling authorizes alignment methodology only — no execution, no claim, no FER reading. The pilot's `TIER_INSUFFICIENT` + strict yield-max miss is a reported blocker awaiting PI decision, not something to tune around.

## 2026-09-21 Dual-rule descriptive census: (W) vs (N) measured, new-source σ outside frozen [50,150]

**Decision**: Settle the pairing-rule question empirically, not by argument: measure BOTH generations per acquisition, decoder-free, frozen constants only — (W) wide `legacy_v1` same-superframe (`b=t//200`, same `b//1024`, 204800-unit window) and (N) narrow `_pair_nearest_unique` (greedy monotonic 1-1, preregistered window grid `{200,500,1000,2000,4000,40000}`, no "best" picked), each with far-offset (`|offset|≥2` superframes) accidental baselines. Record the σ picture against the frozen `[50,150]` design gate without relaxing it: 7/10 inside (SHG 112.5/114.4; Type0-500K 104.7, 1M 132.4; 01-21 Type2 77.6/66.7/91.4), 3/10 outside (pilot 385.7 = 2.57× upper; Type0-1.5M 175.9 = 1.17×; Type0-2M 233.2 = 1.55×). New-source σ far outside the 01-21 design range is a CONTRACT INCOMPATIBILITY with the frozen `gate_ps=200` pairing gate (designed together with `[50,150]`), not a tuning target — flagged for the PI.

**Context**: The pilot had used rule (W) while the frozen `pairing:"nearest"`+`rule:"legacy_v1"` string is most consistent with policy `nearest_unique` — the wrong generation may have been instructed. Census evidence (all 10 align `ok`, `other_frac` ≤ 0.087): pilot (W) 35,399 pairs/138f INSUFFICIENT at 69.5% accidental vs (N) grid 4782→20286 pairs (18–79f, all INSUFFICIENT) at 1.0%→47.6% accidental, with true excess saturating ≈10.4–10.8k under both rules — the same ≈10.7k true population; (N)-200 is the cleaner channel but neither rule permits H on the pilot. Tier census: (W) FULL 8 / INSUFFICIENT 2; (N) w=200 FULL 5 / INSUFFICIENT 5, w=40000 FULL 7 / INSUFFICIENT 3. H emitted only where a rule reaches ≥ REDUCED (8 rows, all (W)/FULL, frozen skip-702 sizing): H_total 4.34–7.62 on 53–96%-accidental streams, not comparable to the frozen ≈0.8 clean-coincidence references. Artifacts: `workspace/census_20260921/*/dual_rule_census.json` + `dual_rule_summary.json` (pilot `census.json` untouched); packet addendum in `.workbuddy/queue/NBPOLAR-DATA-CENSUS-HFULL-20260921/TASK_PACKET.md` §11.

**Alternatives considered**:
- Decide the rule by reading the frozen string (`pairing:"nearest"` ⇒ narrow): rejected — the string is genuinely ambiguous across two implemented generations; only measurement settles which channel each rule yields.
- Pick a "best" (N) window from the grid: rejected — the choice is a contract decision for the PI, the census reports the grid.
- Relax/widen the σ gate so new sources pass, or shrink CAL/VAL to force H where tiers fail: rejected — both would be tuning; the gate stands and the 2 no-H acquisitions stay no-H.
- Promote the 8 (W) H values against the frozen ≈0.8 references: rejected — they describe accidental-dominated streams (high entropy = weak correlation), a finding about the (W) channel, not a comparable efficiency result.

**Consequences**: The PI must decide (1) the pairing-rule contract — (W) high-yield/high-accidental vs (N) clean/low-yield, and any (N) window; (2) whether the σ/`gate_ps=200` incompatibility for new sources requires a contract change; (3) the usability of accidental-dominated (W) H values. No threshold, constant, or code change was made (`src/`, `experiments/`, `tools/`, frozen script untouched; scratch survey script only).

**Cautions**: Descriptive census only — no FER, no qualification, no promotion, no claim. The (W) H rows must never appear in the same comparison column as the frozen clean-coincidence H values. The within-one-step yield self-check passed 10/10 with strict-exact misses (≤0.008%) recorded as plateau notes, never tuned.

## 2026-09-21 Narrow-rule (N) H census: clean-rule H recovered, usable cells exist

**Decision**: Record the (N)-rule H table as the census's scientifically meaningful output (decoder-free, frozen constants only, no window picked, no gate relaxed). The (N) symbol mapping is identical to (W) — `(b_A % 1024, b_B % 1024)`, `b = t // 200` floor, `tA` aligned by each acquisition's frozen `peak_center_ps`; only pair selection differs (greedy monotonic 1-1 within symmetric window). 60 cells measured (10 acquisitions × grid `{200,500,1000,2000,4000,40000}`), 32 H rows emitted (all FULL; no REDUCED tier exists under (N); 28 INSUFFICIENT cells emit no H, no padding). Primary = factorized H1+H2 (raw-count MLE + 1e-15 floor, frozen skip-702 CAL sizing); flat full-joint H_full (30-pt 4-fold CV λ) kept as a SEPARATE field — λ\* = 0.0 on all 32 cells so Hflat == H_total bit-identical, never merged into one column.

**Context**: (N)-200 FULL H_total — `20260113_SHG_Type2PPLN_3s` 0.817348 (H1 0.0254, H2 0.7920, acc 0.58%), `20260113_SHG_Type2PPLN_3s_2` 0.816770 (0.0253/0.7915, 0.58%), `20260121_Type2_1-5M_3s` 0.821496 (0.0254/0.7961, 0.27%), `20260121_Type2_1M_3s` 0.799726 (0.0254/0.7743, 0.19%), `20260121_Type2_2M_3s` 0.831278 (0.0261/0.8051, 0.36%) — reported against frozen references (0.8010378248977231 / 0.8255660516732963 / 0.8325627219737477) with no better/worse claim. Type0-500K/1M (N)-200 are INSUFFICIENT (144f/253f) and emit no H. (N)-40000 FULL H (1.5M 6.7681 at 84% acc; 2M 6.9936 at 89% acc) is accidental-dominated, not comparable. H rises monotonically with accidental fraction along every window ladder (e.g. 1M: 0.7997 → 3.80 at 28.6% acc), confirming the channel degrades by contamination, not breakage.

**Alternatives considered**:
- Keep withholding (N) H as "mapping undefined in the frozen contract": rejected — the mapping is rule-independent; only pair selection differs, and recomputed n_pairs+tier matched the census on all 60 cells.
- Claim the packet's "~99% capture for σ ≤ 150 at w=200" line: corrected — Gaussian ±200 coverage is 0.9900/0.9973/0.9714 for the 01-21 sources (σ 77.6/66.7/91.4, unbiased) but only 0.9247/0.9195 for SHG (σ 112.5/114.4) and 0.8692 for Type0-1M (σ 132.4); ~99% holds only for σ ≲ 87.
- Read the naive mixture `H ≈ p·10 + (1−p)·0.8` as exact for (W): checked — directionally right (monotonic rise ⇒ accidental-dominated, pipeline sound) but overshoots by 1.3–2.0 bits on all 8 (W) rows; implied accidental entropy under (W) is ≈7.5–8.0 bits, not uniform-10.

**Consequences**: YES — scientifically usable cells (clean acc ≲ 5% AND FULL AND unbiased gauss-cover ≳ 0.95) EXIST: the three 01-21 acquisitions at w ∈ {200, 500, 1000, 2000} (12 cells, H_total 0.7997–1.0323) plus SHG w ∈ {500, 1000} (4 cells, 0.8648–0.9628); SHG w=200 is clean+FULL but marginally biased (0.92) under the strict gate. The window/gate contract choice remains the PI's. Evidence: `workspace/census_20260921/narrow_h_summary.json`, `narrow_h_table.csv` (gitignored); script `workspace/narrow_h_census_20260921.py`.

**Cautions**: Descriptive census only — no FER, no decoder, no qualification, no promotion. (N)-wide-window and all (W) H rows must never share a comparison column with clean-coincidence H values. H1 ≈ 0.025 everywhere on clean cells (U1 nearly determined) is a reported structural observation, not an efficiency claim.

## 2026-09-21 Type0 minimal CAL sizing: PI challenge to the inherited tier, split-half SE scaling, descriptive rescue

**Decision**: Answer the PI's challenge — the inherited skip-702 + CAL1024/VAL256 tier (1342/1982 frames) is a convention from sessions with >500k pairs, not a statistical necessity — with a preregistered minimal sizing run (prereg frozen before compute) on the four `20260120_Type0_nofilter_*` acquisitions that emitted no H under rule (N): NEW skip-0 rule (`SKIP0_MINIMAL_SIZING_DESCRIPTIVE`, no proportional skip invented), CAL {128, 256, 512} frames = {32768, 65536, 131072} symbols, windows {200, 500, 1000, 2000}, canonical raw-MLE + 1e-15 floor factorized H1+H2 primary with flat hierarchical-CV H_full as a SEPARATE field, per-cell split-half SE (seed 20260920, fresh rng per cell, SE=|diff|/√2) plus Miller–Madow bias, `CAL_EXCEEDS_AVAILABLE` stop rule (never pad/reuse/borrow). 48 cells: 31 OK (all 16 re-pairings matched census n_pairs exactly), 17 EXCEEDS.

**Context**: Statistical basis verified from the S2/S4 probe (1p5M split-half H2 0.80031/0.79544 ⇒ half-sample SE 0.00345 bits at N≈212k; predicted SE(N)=0.00345×sqrt(212000/N)). Measured pooled mean meas/pred SE ratios: CAL128 1.42 (n=16), CAL256 0.92 (n=11), CAL512 1.71 (n=4) against a 0.80 single-draw null — within ~2× of prediction, NOT much larger in the preregistered >2× veto sense, but single-cell SE values scatter 0.06–4.57 (expected ~75% noise of a one-draw spread estimate; in-cell 128/256 SE ratios 0.05–11.9 vs 1.414). The binding small-CAL caveat is BIAS, not variance: MM bias is 3–8% of H at CAL128 (exceeding SE in most cells), 2–6% at CAL256 — minimal sizing is bias-limited (reported, not subtracted). Defensible cells (acc ≤ 5% AND gauss ≥ 0.95 AND SE ≤ 1.5%): exactly three — 500K w500 CAL128 H=0.861162±0.010110; 500K w1000 CAL128 H=0.978600±0.007131; 1M w500 CAL256 H=0.944344±0.001665 (its CAL128 fails the SE gate at 2.12% — a concrete 128-frames-insufficient case). 1.5M/2M have NO defensible cell at any size: broader peaks (σ 176/233) force coverage-vs-purity conflict (w200 covers only 0.745/0.609; w500+ exceeds 5% accidental) that no CAL sizing resolves. H1 at w200 is 0.0248–0.0279 across all four (matches frozen S2 H1); H2 carries the window/accidental dependence (H spans 0.79–2.26 across windows); flat-CV λ*=0.0 on all 31 cells. Evidence: `workspace/type0_minimal_sizing_20260921/{prereg.md,results.json,minimal_h_table.csv,ANALYSIS.md}` (gitignored); script `compute_minimal_h.py`.

**Alternatives considered**:
- Treat the inherited tier as statistically necessary and leave the four acquisitions H-less: rejected by measurement — variance at CAL128/256 is order-predicted, and 3 clean cells exist.
- Promote the three defensible H values next to the frozen three (≈0.8): rejected — skip-0 sizing with 3–8% unsubtracted plug-in bias and per-window H dependence makes them per-(acq, window) descriptives, explicitly labelled `MINIMAL_SIZING_DESCRIPTIVE_NOT_COMPARABLE_TO_FROZEN`.
- Read individual >2× SE ratios as proof the sizing is unsafe: rejected — single-draw spread estimates scatter that widely by construction; the pooled level is what the prereg criterion addresses, and it passes.

**Consequences**: The PI's challenge is half-sustained — the tier is not a variance necessity, but minimal-sizing H stays descriptive-only and cannot enter any comparison column with the frozen three. 500K is rescued at CAL128 (w500/1000); 1M needs CAL256 at w500; 1.5M/2M are not rescuable by sizing (peak-width/purity limited). No frozen constant, tier, code, or prior H value was changed; decoder-free; no writes outside the scoped workspace dir.

**Cautions**: Descriptive only — no FER, no decoder, no qualification, no promotion. Single-cell SE numbers are order-of-magnitude (one-draw estimates). Unsubtracted MM bias (up to ~8%) dominates the error budget at CAL128 — any downstream use must carry it.

## 2026-09-21 Prior form is the converging root cause: nonparametric M0 floor prices sparse rare cells at ~4e-18 (S8/S9/S10/F-accounting/V25-identity)

**Decision**: Record as the session's converging descriptive finding that the nonparametric empirical prior (`counts_ab` raw-count MLE + 1e-15 floor — the incumbent P7 rule) mishandles sparse rare cells, and that this prior-form defect — not rate, not disclosure amount, not construction — is the leading hypothesis for what has been killing the decoder. Concretely: (F1) S9 shows the M2 ±1 parametric prior decodes where the M0 table does not (synthetic, 11/16 vs 0/16 paired); (F2) S8 shows the ±1 prior wins on held-out fit, CAL size, and accounting simultaneously; (F3) the prior-estimation accounting gap is confirmed open (adopted λ_total has no prior-estimation term; `docs/SECURITY_MODEL.md` has zero case-sensitive `CAL|prior|calibration` mentions) and the frozen Release baseline shows the copyable parametric-prior pattern; (F4) S10 refines the Type0 window picture (1.5M admits a usable sliver at w350–400 — the earlier "unrescuable at any size" line is corrected for window-usability only; 2M admits none; all cells stay tier-INSUFFICIENT so no H was emitted); (F5) the three `20260121_Type2_*` acquisitions ARE the V25 sources (timestamps match exactly; their ≈0.80 census H is the same data, not independent corroboration); (F6) strategic consequence: adopting the ±1 prior would drop CAL from 1024 frames to ~8–32 frames, simultaneously dissolving the Type0 tier insufficiency, the prior-estimation accounting gap, and the data-scarcity constraint — recorded as the recommended direction, explicitly **pending real-data validation** (F1 is synthetic-only). No FER/efficiency/qualification claim; no frozen number touched; no code, test, or build change.

**Context**: All probes are Tier-X, descriptive-only, zero real-data reads (S9/S8) or decoder-free census (S10/minimal-sizing).

F1 — S9 `workspace/probes/nbpolar_s9_decoder_prior_relevance/results.json` (COMPLETE_DESCRIPTIVE_ONLY, 96 SC calls, 0 protected reads; N=32768, GF32×GF32 F03, frozen P16 construction, matched K1=319/K2=6492, 16 shared model-sampled EVAL blocks, one 64-bit Toeplitz tag per block; TRAIN 8×32768=262144 pairs seed 2026092101, EVAL 16 blocks seed 2026092117; ground truth B uniform over 1024, A=(B+delta) mod 1024 with S8-M1-pooled weights q0=0.7439766376397192, q+=0.25465866259422926, q−=0.0013646997660514686, q_rest=0.0 exactly):

| arm | prior | construction | exact | 95% Wilson CI | verify_failed | undetected | decode_failed |
|---|---|---|---|---|---|---|---|
| A | M0 table (incumbent) | frozen P16 | **0/16** | (0.000, 0.194) | 16 | 0 | 0 |
| B | M2 ±1 parametric | frozen P16 | **11/16** | (0.444, 0.858) | 5 | 0 | 0 |
| C | M2 ±1 parametric | M2-rederived | 13/16 | (0.570, 0.934) | 3 | 0 | 0 |

Paired: A-vs-B → B-only 11, A-only 0, neither 5. B-vs-C → C-only 2, B-only 0, both-exact 11 (within CIs ⇒ re-deriving the construction is unnecessary for safety). Err-layer split: A L1 8 / L2 8; B L1 2 / L2 3 / none 11; C L1 2 / L2 1 / none 13. **Mechanism** (all numbers recomputed from the artifact): TRAIN gives 262144/1024 = ~256 samples/column; ground-truth −1 rate 0.00136 ⇒ P(zero −1 in a column) = e^−0.349 ≈ 0.705, i.e. ~70% of M0 columns see ZERO −1 events and price them at ~4e-18 (≈1e-15 floor ÷ ~256 column total after per-column renorm), while M2's pooled fit prices them at 0.00147 (TRAIN empirical 0.00147247314453125); each EVAL block holds 32768×0.00136 ≈ 45 true −1 deltas, each costing M0 log2(0.00147/4e-18) ≈ 48 bits of spurious penalty. Budget: per-block wall mean ~11.9–12.0 s (2 SC calls ⇒ ~6 s per SC call at N=32768); RSS peak 958,611,456 B ≈ 0.96 GB for the 3-arm run (budget 1800 s / 1.5 GiB, 680 s total, no early stop).

F2 — S8 `workspace/probes/nbpolar_s8_parametric_prior/results.json` (COMPLETE_DESCRIPTIVE_ONLY, 0 decoder calls, 0 protected reads; split-A fit / split-B score, seed 20260920; estimator = model-implied full 1024×1024 P(A|B) + 1e-15 floor + per-B-column renorm, S6 `h1h2_of` convention, no λ program). Held-out NLL: M0 nonparametric 0.863743271229636/0.8787817713782088 (2436/2635 params, M0 anchor reproduces S5 to 0.0); **M1 pooled ±1 (2 params) 0.8272030725917509/0.8345441152453187**; M2 per-session ±1 0.8271575915650822/0.8345428765281956; M3 +boundary context 0.8271630985988352/0.8345424651488408; M4 per-Bob-column ±1 (2048 params) ≡ M0 to all digits (gap 0.0). Parametric models BEAT the incumbent by 0.0366–0.0442 bits/symbol (they remove dead-cell floor spikes). M1-vs-M2 gap: −4.5481026668681146e-05 (1p5M) / −1.2387171230976435e-06 (2M) — M1 ≈ M2 while both sources share delay sign; re-check if a delay −50 source ever enters CAL. Minimum CAL for 1% H accuracy: incumbent 262144 symbols = 1024 frames (never reaches 0.1% on the grid); M1 1000/500 symbols ≈ 3.9/2.0 frames; M2 2000/500 symbols ≈ 7.8/2.0 frames. Prior cost vs per-block net key (4 bits/symbol = 131072 bits/block): incumbent sacrifice 262144 symbols = 1048576 bits ≈ 8× a block / 2× a 4-block packet; **M2 sacrifice 2000–8000 bits ≈ 0.015–0.06× a block; reveal ~18–22 bits ≈ 1.4e-4–1.7e-4× a block** (order-of-magnitude params·log2(n) bound, NOT a composable proof). M4's parameter count makes it as expensive as M0 (same 1024-frame minimum) — skip it. Caveat from the artifact's own `m1_row_note`: S8's subsample M1 rows use the PER-SESSION delta refit, not a two-session pool, so the "M1 ~2–4 frames" readout is unaffected at 1% but the M1 0.1% readout carries the pooled-vs-per-session mismatch (0.42% 1p5M / 0.03% 2M at full CAL) as a floor — use M2 0.1% for the tight-accuracy answer. S8's P5 decoder-relevance caveat is now ADDRESSED by S9 (P5 explicitly proposed this exact synthetic-channel decode comparison and it was run, not merely planned).

F3 — accounting gap + Release pattern. `docs/SECURITY_MODEL.md` has zero case-sensitive mentions of CAL/prior/calibration (verified by grep, exit 1; case-insensitive hits are only "practical"/"Calculation" substrings); the adopted λ_total contract (Müller eq 11/13 per the 2026-09-21 f_eff entry) has no prior-estimation term. The frozen Release baseline (`/mnt/d/Code/HD-QKD_Polar_Release`) has no such object: its decoder receives only a **parametric per-bit-plane BSC** (1 scalar, LLR `±log((1−p)/p)` via `_llr_from_side_info` in `pipelines/current/round1b_run_actual_ir_replay.py:67-70`); the only q×q conditional (`_build_chan_ll_table`, `src/workflow/export_joint_sequence_sidecar.py:400`) feeds `_map_sanity` (line 1618–1619) and a saved sidecar `chan_ll_table.npy` — other tools reference that file only for namespace-gate verification (`materialize_loss_namespaced_candidates.py:194`, `verify_candidate_namespace_gates.py`), never as a decoder input; channel parameters are estimated **in-sample on the key data** (per-plane BERs from the aligned key sequences via `_extract_real_layer_bers` in `experiments/run_real_polar_max_pie.py`, no CAL/sacrifice object in that path); the claim is scoped `public_ec_only_not_secure` (`tools/security_reports/round2_build_finite_key_audit_table.py`, `RECONCILIATION_CLAIM_BOUNDARY`) with `composable_security_claim_flag = 0` (`tools/security_reports/round2_build_actual_ir_finite_key_shadow.py:97`) and an exhaustive fail-closed public-message inventory (`OTHER_DISCLOSURE_INVENTORY_TAG`, `blocked_*` statuses). **Release's 1-parameter-per-plane channel IS the parametric-prior pattern.** Copyable pattern: (1) decoder receives a parametric channel only; (2) either estimate in-sample (Release — but label the reuse bias and scope the claim) or keep a small CAL and charge it — NB-Polar should keep a small CAL (~8–32 frames) because at that size the cost is negligible and in-sample reuse bias is avoided; (3) exhaustive public-message inventory with fail-closed tags; (4) scope the claim.

F4 — S10 `workspace/probes/nbpolar_s10_window_refine/results.json` (Tier-X, decoder-free; grid {200,250,300,350,400,450,500}, offset −50 inherited, tier floors FULL 1982 / REDUCED 1342, usable gate coverage≥0.95 AND accidental≤0.05; 28 cells, all tier-INSUFFICIENT, best 558 frames (2M w500) vs the 1342 REDUCED floor, so no H was emitted — a valid outcome, not a failure): **500K usable from w=250 up** (w200 gauss-cover 0.944 < 0.95); **1M from w=300 up** (w250 cover 0.941 < 0.95); **1.5M admits a usable sliver at w=350–400** (cover 0.953/0.977, accidental 0.041/0.047); **2M admits NO usable window** (w450 cover 0.946 < 0.95 with accidental already 0.075; w500 cover 0.968 but accidental 0.082). The earlier "1.5M/2M unrescuable at any size" line (minimal-sizing entry) is **overturned for 1.5M on window-usability only** — its required window (1.96σ = 1.96×175.87 ≈ 345) fell exactly in the old grid gap — NOT on tier sufficiency (still INSUFFICIENT everywhere) and NOT on the minimal-sizing "defensible" gate (which additionally required SE ≤ 1.5%; S10's "usable" is coverage+accidental only — different gates, no contradiction).

F5 — V25-source identity. `docs/hd-qkd-ir-roadmap-review-20260823.md:21` states "V25 | 三源 type2_2026-01-21 经验信道"; X07 probe records `source_id: type2_1M_20260121_184040` with `provenance_raw_ttbin` carrying timestamp 184040; decision-log `:3601-3603` gives the three source/delay IDs (`type2_1M_20260121_184040`, `type2_1p5M_20260121_183806`, `type2_2M_20260121_183657`); **timestamps 184040/183806/183657 match the three intake directories** (`Type2_1M_3s_2026-01-21_184040`, `Type2_1-5M_3s_2026-01-21_183806`, `Type2_2M_3s_2026-01-21_183657` per `RAW_DATA_INVENTORY_20260921.md:44-49`) **exactly**. (Path-casing note: X07 writes the provenance with lowercase `type2_1M_3s_2026-01-21_184040`, the inventory with `Type2_1M_3s_...` — same timestamped acquisition.) Their census H (≈0.8215/0.7997/0.8313 at (N)-200) coinciding with the frozen references is NOT independent corroboration — it is the same data via another estimation path (V25 TRAIN frames 0..1199 of the same `pairs.parquet`). **The genuinely new usable data is the SHG pair** ((N)-200 H 0.817348/0.816770, gauss-cover 0.9247/0.9195 ≈ 0.92 marginally-biased-but-FULL, plus fully-usable w500/1000 cells at 0.8648–0.9628 per the (N)-H census entry) **plus whatever the ±1 prior unlocks.**

F6 — strategic consequence. If the ±1 prior is adopted, CAL drops from 1024 frames to ~8–32 frames (S8 1% minima ≈ 2–8 frames, padded for the 0.1%-level mismatch floor and real-data margin). That single change simultaneously dissolves: the Type0 tier insufficiency (S10 — every Type0 acquisition already has ≥144 frames ≥ the new CAL need), the prior-estimation accounting gap (F3 — a ~2000–8000-bit CAL is negligible and chargeable), and the data-scarcity constraint that motivated the whole 10-acquisition intake. Recorded as the recommended direction, explicitly **pending real-data validation**: the next real-data packet should test the M2 prior at fixed K1=319/K2=6492 on already-accepted blocks before any new acquisition is opened for method development.

**Alternatives considered**:
- Treat S9's B 11/16 (or C 13/16) as FER/reliability/efficiency evidence or as qualification for the ±1 prior: rejected — synthetic only, 16 blocks (wide CIs: B (0.444, 0.858)), ground truth pro-M2 by design (exact ±1 support, q_rest=0 — M2 is correctly specified, so the test shows only that the LLR structure stops hurting SC, not that M2 is true); descriptive only.
- Read arm A's 0/16 as proof the nonparametric prior can never work: rejected — specific to raw-MLE-plus-floor on sparse rare cells (TRAIN 256/column vs −1 rate 0.00136); a lifted floor or any pooled smoothing is a different prior, untested by arm A.
- Re-derive the construction under M2 (arm C path) as the recommended route: rejected for safety — B-vs-C differs by 2 blocks within overlapping CIs (B-only 0, C-only 2); frozen-P16-orders + M2 tables (arm B) is the minimal change.
- Adopt in-sample key-data estimation (Release-style, 0 CAL bits) for NB-Polar: rejected as the default — avoids CAL cost but imports reuse bias; keep a small ~8–32-frame CAL and charge it.
- Promote the 1.5M w350–400 sliver to a usable-data claim or emit H from S10: rejected — all 28 cells tier-INSUFFICIENT; S10's "usable" gate is coverage+accidental only and must never be confused with the minimal-sizing "defensible" (SE-gated) verdict.
- Count the V25-source census-H coincidence as independent corroboration of the frozen ≈0.8 references: rejected — same `pairs.parquet` TRAIN population via another path.
- Adopt M4 (per-B-column ±1): rejected — 2048 params/session, NLL ≡ M0 to all digits, same 1024-frame CAL minimum as the incumbent.

**Consequences**: The prior-form question is now the Stage 1 leading hypothesis (macro-plan §9; Stage 1/2 updated to route the next real-data packet at it). No rerun/retuning of S8/S9/S10; probe records stay worktree-only (gitignored by design); this entry is the durable record. Next gate is main-thread planning of the real-data M2-prior packet (fixed K, accepted blocks first).

**Cautions**: (a) S9 is SYNTHETIC-ONLY — no real-data, FER, efficiency, or qualification claim; 16 EVAL blocks ⇒ wide CIs; ground truth was pro-M2 by design. (b) S8 P3-NLL subsamples are drawn from FULL counts (overlap-optimistic) — P3-H error is unaffected (reference = same-model full-CAL fit); the reveal-bits column is an order-of-magnitude bound, not a security proof. (c) The task-statement shorthand "M1 ≈ M2 gap ~1e-5 bits" smooths actuals −4.55e-05 (1p5M) / −1.24e-06 (2M) — recorded here exactly. (d) "Sacrificed sample = 0 / estimation leakage = 0 bits" for the Release in-sample path is the packet's reading of a codeless-CAL path (BERs from the aligned key sequences, no CAL object), not a re-verified literal from the Release file text. (e) `composable_security_claim_flag = 0` lives in `round2_build_actual_ir_finite_key_shadow.py:97`, a sibling of the cited audit-table file — cited exactly, not smoothed. (f) F1–F6 dissolve constraints only if real-data validation confirms S9's direction; until then the 10-acquisition intake, tier gates, and accounting-gap entries stand unmodified.

---

## 2026-09-21: Arithmetic corrections from the independent adversarial review (S9 floor penalty, Miller–Madow sign, CAL-size SE, δ-tail bound, D4 fixed-f vs fixed-K; remainder 101 frames)

**Decision**: Record five independently recomputed arithmetic corrections (C1–C5) to numbers cited in recent S9/S2-S4/G1/D4 narrative, all verified from the frozen artifacts with `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (numpy 2.5.3) on branch `codex/nbpolar-phase0`: (C1) the S9 floor penalty is **40.4214 bits**, not ~48 bits (overstatement exactly **8.0 bits**); only **~30.35** of the ~44.72 true −1 deltas per EVAL block fall in TRAIN-zero-−1 columns, not all ~45. (C2) the S2/S4 Miller–Madow "corrected H2" subtracted the bias instead of adding it: correct values are **0.8026903611** (1p5M) and **0.8089106006** (2M). (C3) the ideal-iid H2 SE at n=8192 is **0.00804/0.00814 bits** (~1.00%/1.01% of H2) from sqrt(V2/n) vs **0.01755 bits** (~2.2%) from split-half scaling — a ~2× disagreement that is itself a finding. (C4) the rule-of-three 95% upper bounds are **3.6621e-4** (n=8192) and **1.5e-5** (n=200000). (C5) freezing f=1.3 under S8-M2 H_total gives **K_total 7053 (+33, 1p5M) / 7106 (+26, 2M)**; freezing K_total instead gives **f = 1.2939 / 1.2952**. The S9 A/B observation difference (B 11/16 vs A 0/16 paired on shared synthetic EVAL, descriptive only) **SURVIVES** C1 — the penalty shrink weakens but does not remove the mechanism — so M2 remains a valid Stage-1 candidate, but the quantitative "~4e-18 / ~48 bits per delta" mechanism narrative is **withdrawn**. The "±0.3% estimation noise ⇒ H2 misestimation refuted" claim is **softened** to "bias small, sign not established". The never-decoded remainder is **101 frames, not 261**; after a 32-frame CAL only **69 frames** remain — less than one 128-frame block.

**Context**: An independent adversarial review returned NO-GO with arithmetic findings in the S9 and S2/S4 probes; the code paths were confirmed on inspection (`workspace/probes/nbpolar_s9_decoder_prior_relevance/body.py:141-143` floors probabilities, not counts; `workspace/probes/nbpolar_s2s4_zero_data_discriminators/body.py:240` computes `H2s - mm_bias`). Every figure below was recomputed from the frozen artifacts (S9 `results.json` TRAIN `delta_hist [194963, 66795, 386]` / 262144 pairs; S2/S4 `results.json` `H2_stored` / `miller_madow_bias_bits` / `V2` / split-half `H2_half1/H2_half2`), plus a decoder-free rebuild of the synthetic TRAIN with the frozen seed 2026092101 (695/1024 columns with zero −1, total −1 = 386, matching the artifact exactly).

- **C1 — S9 floor penalty.** Pooled −1 rate q = 386/262144 = 0.00147247314453125. Floor-on-probabilities penalty: log2(q/1e-15) = **40.42137846 → 40.4214 bits**. The doc's implicit double-division (floor-on-counts, 1e-15/256 ≈ 3.9e-18): log2(q/(1e-15/256)) = **48.42137846 → 48.4214 bits**. Overstatement = **8.0 bits exactly** (= log2(256)). Expected true −1 deltas per EVAL block (ground-truth rate 0.0013646997660514686 × 32768) = **44.71848193 → 44.7185**; expected number falling in TRAIN-zero-−1 columns (× 695/1024 rebuilt) = **30.35092280 → 30.3509**. All four task figures **confirmed, no disagreement**. (Renorm after flooring changes the floored value only at ~1e-12 relative for ~256-count columns, so log2(q/1e-15) stands as stated.)
- **C2 — Miller–Madow sign.** The MM correction adds (K−1)/(2·n·ln2); the probe subtracted it. 1p5M: artifact wrong value 0.7980427483783825 → correct H2s+bias = **0.8026903611207041 → 0.8026903611** (bias 0.0023238063711608047, +0.2903%). 2M: wrong 0.8048907456263215 → correct **0.8089106006356572 → 0.8089106006** (bias 0.0020099275046678374, +0.2491%). Task figures **confirmed, no disagreement**. Downstream: the "±0.3% ⇒ H-B refuted" framing rested on MM (+0.29%/+0.25%) and split-half (−0.31%/−0.28%) roughly cancelling; with the sign fixed they no longer cancel (MM +0.29%/+0.25% additive vs split-half −0.31%/−0.28%), so the framing is softened to: **two bias estimators of opposite sign and comparable magnitude — the bias is small but its SIGN is not established**.
- **C3 — ideal iid SE at 8192.** sqrt(V2/n): 1p5M sqrt(0.5295937795023029/8192) = **0.00804038 bits (1.0046% of H2)**; 2M sqrt(0.5424414072827268/8192) = **0.00813732 bits (1.0085% of H2)**. Split-half scaling 0.00345×sqrt(212000/8192) = **0.01755060 → 0.01755 bits (~2.19% of H2)**. **One minor flag**: the task's 0.00824 (1.03%) is ~2.5% above either recomputed value (0.00804/0.00814) and is not reproducible from the artifact V2 at n=8192 — use 0.00804/0.00814. The substantive finding is unaffected: the two SE estimates disagree by **~2.18×**, so the small-sample SE is not well characterised. (Provenance of the inputs as given: 0.00345 = |H2h1−H2h2|/√2 = 0.00344796… on 1p5M halves; 212000 ≈ half of the 1p5M n_total 424960.)
- **C4 — δ-tail bound.** Rule of three, zero |δ|≥2 observations: 3/8192 = **3.662109375e-4 → 3.662e-4**; 3/200000 = **1.5e-5**. **Confirmed.** Consequence: **a 32-frame (8192-symbol) CAL cannot establish a tight δ-tail bound even with zero observations** — δ-tail CHARACTERISATION and prior FITTING must use different sample sizes, and the characterisation sample must be preregistered separately and much larger (this is needed for the G1 gate).
- **C5 — D4 fixed-f vs fixed-K_total.** Budget literal K_total = floor((1.3·N·H_total−64)/5), N=32768, S8-M2 H_total 0.8294/0.8356 (TOTALS incl. H1): frozen-f gives **7053 (1p5M, +33 vs current 7020) / 7106 (2M, +26 vs current 7080)**. Frozen-K instead gives **f = (5·7020+64)/(32768·0.8294) = 1.29385112 → 1.2939** and **(5·7080+64)/(32768·0.8356) = 1.29520750 → 1.2952**. **Confirmed.** The two options differ by only ~0.5% (33/7020 = 0.47%, 26/7080 = 0.37%), but the choice must still be stated explicitly in the next packet.
- **Remainder 101, not 261.** Prior ledger 41+42+89+89 = 261; P20S consumed 128 (merged segments [2827,2915] = 89 + [3556,3594] = 39; `.workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m/report.md:7`); P20T consumed 32 (DEV 3595..3626; `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/MAIN_THREAD_ACCEPTANCE.md:8`, item §4). Remainder = 41+42+18 (HOLD 3627..3644) = **101 frames**; after a 32-frame CAL, **69 frames** remain — less than one 128-frame block, and P20T's own acceptance already reads "ladder ends by exhaustion".

**Alternatives considered**:
- Retain the "~4e-18 / ~48 bits per true −1 delta" narrative as an order-of-magnitude illustration: rejected — the 8-bit double-division error compounds with the all-~45-charged error (only ~30.4 of ~44.7 fall in zero columns); the quantitative narrative is withdrawn while the S9 observation (B 11/16 vs A 0/16 paired, CIs (0.444,0.858) vs (0.000,0.194), `undetected` 0) stands.
- Retain "H-B strong form REFUTED (±0.3%)": rejected — the cancellation the verdict rested on disappears with the MM sign fix; H-B stays at "bias small, sign not established" (already the reading in `docs/nbpolar/STATE.md:23` / `docs/nbpolar/MACRO_PLAN_20260921.md:38`).
- Retain the 261-frame ledger: rejected — P20S/P20T consumption is accepted record; 261 = pre-consumption population.
- Re-derive the 54.8σ dispersion margin or recompute the S8 NLL table in this entry: rejected as out of scope — the five items are arithmetic corrections only; the 54.8σ figure (plug-in posteriors, untouched by C1–C5) is not re-verified here and its "refutation" reading is already softened in the nbpolar docs, not re-decided here.

**Consequences**: M2 remains a valid Stage-1 candidate (S9 direction + S8 NLL untouched); no probe rerun. The following worktree documents still cite the withdrawn numbers and need fixing (verified by grep at entry time; frozen `.workbuddy/` packet files are historical and are NOT to be edited): S9 mechanism — `AGENT_PROJECT_MEMORY.md:3` (~4e-18 / ~48 bits root-cause line), `docs/decision-log.md:5246` (entry title) and `:5260` (mechanism paragraph), `docs/troubleshooting.md:746-749`, `openspec/changes/nbpolar-prior-rebaseline/proposal.md:19`; H-B verdict — `docs/decision-log.md:5171` ("H-B strong form … REFUTED (±0.3% …)" line; `:5176` carries the same 54.8σ rationale), `openspec/changes/nbpolar-prior-rebaseline/design.md:87` ("S2/S4 refutations (54.8σ margin, ±0.3% H2 noise …)"); remainder — `AGENT_PROJECT_MEMORY.md:64`, `docs/decision-log.md:4872`, `docs/nbpolar/DOCUMENT_INDEX.md:265`, `docs/nbpolar/LITERATURE_FIT_CHECK_20260921.md:98`. Already correct at entry time (no fix needed): `docs/nbpolar/STATE.md:9,23,36,50,69,71,73` and `docs/nbpolar/MACRO_PLAN_20260921.md:38-39,91,274-276` (these carry the corrected 40.4214 / MM-additive / 101-frame readings). The G1 gate must preregister a separate, much larger δ-tail characterisation sample. The next D4 packet must state explicitly whether f=1.3 or K_total is frozen.

**Cautions**: (a) C3 minor flag stands: use recomputed 0.00804/0.00814 bits, not the task's 0.00824; the ~2× SE disagreement finding is unaffected either way. (b) C1's 44.7185/30.3509 use the ground-truth −1 rate; TRAIN-empirical variants are 48.25 total / 32.75 in zero columns — same mechanism, do not mix the two rates. (c) The 695/1024 zero-−1-column count is a TRAIN rebuild (seed 2026092101, decoder-free); the Poisson prediction e^−0.349×1024 ≈ 722 is close but the rebuilt 695 is authoritative for the 30.3509. (d) The `.workbuddy/` P20S `TASK_PACKET.md:122` "totalling 261 frames" line is pre-consumption history in a frozen packet — superseded, not edited. (e) This entry corrects arithmetic only; S9 stays synthetic-descriptive (16 blocks, pro-M2 ground truth by design) and no FER/efficiency/qualification claim follows.
