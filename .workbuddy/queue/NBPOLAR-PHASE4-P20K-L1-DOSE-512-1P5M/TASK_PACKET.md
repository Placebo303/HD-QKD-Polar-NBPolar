# Phase 4-P20K — Frozen L1-dose-512 single-factor packet on type2_1p5M_20260121_183806 (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage A implementation-freeze, Stage B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read, decoder execution, or commit/push is authorized by this file.
- Predecessor: `NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M` terminal
  `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_ESCALATION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; DEV open 1/1 SPENT
  on 1.5M TRAIN 768..1151; 9/9 records; 21/21 gates PASS; D0 base-K1 0/3
  verify_failed + D1 L1+256 (K1 575, keyΔ +1280) 0/3 verify_failed +
  d1_restored 0/3; all six operational first errors L1-layer with D1 coordinates
  all later — blk0 14/L1→23/L1, blk1 6/L1→25/L1, blk2 1/L1→21/L1; D2 oracle 3/3
  exact isolated; undetected 0; SC 15/15; tags 9/9; recount 0;
  key 306126 / public 2949687; 2M pristine by non-access).
- P20I precedent (carried): +128 L1 single-factor on 1.5M TRAIN 384..767 —
  C0 0/3 + C1 0/3 verify_failed, c1_restored 0/3; first errors all L1-layer
  (blk0 2→2 unchanged; blk1 17→1 moved earlier; blk2 13→16 moved later);
  C2 oracle 3/3 exact at base K2.
- P20H precedent (carried): calibrated-prior +1024 L2 confirmation on 1.5M TRAIN
  0..383 — B0 0/3 + B1 0/3 verify_failed, b1_restored 0/3; first errors
  16/L1 + 6/L1 + 8/L1 identical across B0/B1 per block; B2 oracle 3/3 exact
  at base K2.
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2
  (reproducible reliability; confirmation on new blocks/sessions; stop rules)
  and `docs/nbpolar/ROADMAP.md`.
- Gate discipline: any standing long-horizon authorization does NOT collapse
  Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_1p5M_20260121_183806` (1.5M). The 2M session
  (`type2_2M_20260121_183657`) is registered but RESERVED pristine (see §4, §16).

## 0. Planner header (OpenSpec workflow)

- **Goal**: Decide the single open question left by P20I+P20J — with the P20H
  per-session prior held read-only and everything else carried over, does ONE
  preregistered doubling-chain-endpoint L1-disclosure increment (+ΔK1=512,
  single tier, order-prefix) restore any complete operational block on three NEW
  1.5M TRAIN blocks at N=32768 (three arms E0/E1/E2, carried-over
  construction/order/caps logic, new P20K tag domain), and does the +256
  full-deferral pattern continue or saturate at double the dose? Zero further
  tuning.
- **Non-Goals**: No efficiency tuning, no P20D alternative L2 construction,
  no minimality probe beyond the single frozen +ΔK1 tier, no second L1 tier
  (`E1b`), no second L2 step, no second independent session on 2M, no SCL/new
  kernel/model/schema, no FER/qualification/promotion claim, no reuse of any
  consumed/closed range (1M full pool, P20H DEV 0..383, P20I DEV 384..767,
  P20J DEV 768..1151).
- **Impact Scope**: New thin runner + focused injected tests + P20K OpenSpec
  delta (`specs/nbpolar-phase4-p20k/spec.md` + `tasks.md` P20K section, same
  umbrella change `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A freeze
  + implementation notes + Stage-B evidence root. No change to `src/`,
  `experiments/`, `tools/`, P16 construction file, P12–P20J accepted roots,
  P20H calibration product, or `results/` / `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20K-R1..R8 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance.
  Descriptive-only label; `undetected` isolated; oracle never operational.
- **Tasks**: (planner task list for coder agents) H1 freeze prior reuse (§3, R1);
  H2 freeze population/sextuple-gate (§4, R2); H3 freeze caps (§5, R3);
  H4 freeze +ΔK1 tier + order-prefix rule (§2/§6, R4); H5 wire endpoints/taxonomy
  (§7, R5); H6 enforce one-shot budget/stop (§8, R6); H7 Stage-A suites green
  with zero-protected-open audit (R8); H8 independent Pre-EXECUTE adjudication
  of the prior-reuse + population gates (R7); H9 single authorized Stage-B
  attempt (R6/R7); H10 independent Pre-RESULT + acceptance.

## 1. Mission

With ONE preregistered change against P20H/P20I/P20J — L1 disclosure +ΔK1=512
via the frozen order-prefix rule (Stage-A frozen, Stage-B read-only) — and
everything else carried over from P20H (per-session prior digest-pinned
read-only, K2 base 6492, floor 1e-15, N=32768, greedy SC only, new P20K tag
domains only), zero further tuning:

> Does +512 L1 restore any complete operational block on three NEW 1.5M
> TRAIN blocks (1152..1535) — and does the +256 full-deferral pattern
> continue or saturate when L1 disclosure doubles again while L2 disclosure
> stays at base?

P20H DEV 0..383, P20I DEV 384..767, and P20J DEV 768..1151 are CONSUMED (9+9+9
records, DEV 1/1 + attempt 1/1 SPENT each) and SHALL NOT supply P20K blocks.
All branches after this packet are deferred to §16 and must not be prejudged
here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- P20J (descriptive-accepted): +256 L1 single-factor on 1.5M TRAIN 768..1151.
  D0 0/3 + D1 0/3 verify_failed, d1_restored 0/3; all six operational first
  errors L1-layer with D1 coordinates ALL later (blk0 14→23; blk1 6→25;
  blk2 1→21); D2 oracle 3/3 exact at BASE K2. The +256 step (+1280 key bits)
  delayed every first error but restored nothing — the second dose is falsified
  as a fix, while showing stronger causal activity than +128 (full deferral vs
  mixed move).
- P20I (descriptive-accepted): +128 L1 single-factor on 1.5M TRAIN 384..767.
  C0 0/3 + C1 0/3 verify_failed, c1_restored 0/3; all six operational first
  errors L1-layer (blk0 2→2 unchanged; blk1 17→1 moved earlier; blk2 13→16
  moved later); raw SER ~0.2520/0.2526/0.2535; C2 oracle 3/3 exact at BASE K2.
  The +128 step (+640 key bits) moved first-error coordinates but restored
  nothing — the minimal dose is falsified as a fix, while proving L1
  sensitivity (coordinates move when L1 disclosure grows).
- P20H (descriptive-accepted): calibrated-prior +1024 L2 confirmation on 1.5M
  TRAIN 0..383. B0 0/3 + B1 0/3 verify_failed, b1_restored 0/3; all six
  operational first errors L1-layer (16/L1 + 6/L1 + 8/L1, identical across
  B0/B1 per block); B2 oracle 3/3 exact at base K2=6492. The +1024 L2 step
  (+5120 key bits) left first-error coordinates unchanged — L2 disclosure did
  not salvage when hard L1 itself is wrong.
- Dose response (descriptive only, cross-packet coordinates MUST NOT be read as
  a slope): +128 mixed move (one unchanged, one earlier, one later) /
  +256 full deferral (14→23, 6→25, 1→21) / both zero recovery — disclosure is
  causally active (coordinates respond to L1 disclosure) but insufficient
  (nothing restored). The three dose segments are NON-SAME-BLOCK (384..767 vs
  768..1151 on different TRAIN frames), so inter-packet coordinate deltas are
  not a dose-response slope; the slope claim is forbidden. What IS licensed:
  within each packet, the paired D0→D1 (C0→C1) same-block move is observed.
- Oracle reading (first principles, P20H + P20I + P20J convergent): 3/3 exact
  under true-L1 conditioning at base K2=6492 on ALL THREE 1.5M segments proves
  that, GIVEN true L1, the base-K2 L2 path is sufficient on these nine blocks.
  The bottleneck is therefore L1 disclosure (K1=319 insufficient at L1 SER
  ~0.252–0.256), not L2 construction/insufficiency at this operating point.
  SC is sequential: extra L2 disclosure conditions on wrong hard L1 and cannot
  rescue it.
- P20D literal trigger vs semantic offset (frozen): the P20J §16
  zero-restoration trigger reads literally satisfied (D0 failures occurred on
  new-segment blocks but D1 restored NONE under the frozen prior + frozen +256
  tier). It SHALL NOT auto-trigger P20D here. P20D is fixed-disclosure + ONE
  alternative L2 construction — the wrong factor when every operational first
  error across P20H (6/6), P20I (6/6), and P20J (6/6) is L1-layer and the
  oracle shows base L2 sufficient given true L1 on all three segments.
  Constructing an L2 alternative now would change the factor the evidence
  exonerates. Moreover the L1 dose-response is incomplete at the top: only TWO
  non-zero L1 doses (+128, +256) have been tried on 1.5M calibrated data, and
  +256 showed strictly stronger activity (full deferral) than +128 (mixed
  move) — the chain has not saturated. The scientifically reasonable Round 9 is
  therefore ONE preregistered L1-dose-512 endpoint single-factor packet.
  Upgrade once more to the doubling endpoint, then talk P20D. This offset
  rationale is frozen and not re-argued in Stage A/B.
- +ΔK1 tier decision (planner, options argued in writing; single tier):
  (A) +512 (K1 319→831, K_total 6811→7323, key 34119→36679, keyΔ 2560);
  (B) +384 (K1 319→703, midpoint, keyΔ 1920);
  (C) +1024 (K1 319→1343, keyΔ 5120);
  (D) jump to P20D now.
  Decision: (A) +512. Reasons: (i) doubling-chain endpoint — the accepted L2
  lineage doubled +512→+1024 (P20E→P20F pattern); the L1 lineage tried +128
  (P20I) then +256 (P20J) and must double once more to +512 to COMPLETE the
  +128/+256/+512 chain before any larger jump or factor switch, preserving
  single-step dose-response resolution and giving the disclosure route a clean
  closure condition; (ii) saturation test — +256 moved every first error later
  without restoration; doubling again tests whether deferral continues (deeper
  insufficiency) or saturates (mechanism change), the most informative next
  single observation; (iii) practical meaning preserved: +512 keeps E1 at
  ~11.19% of raw (see §5), still far below raw per the strategy bar — a larger
  overcommit in one move is unjustified, and (B) +384 breaks doubling
  discipline for no empirical reason while (C) +1024 skips the endpoint and
  burns budget; (iv) falsifiability with closure: +512 yields crisp §16
  branches — any E1 restoration reopens the dose line (maintain confirmation);
  zero restoration completes the three-dose L1 set (+128/+256/+512) on 1.5M and
  licenses closing the disclosure route (turn to non-disclosure factors);
  maintain-only re-opens planning with full chain evidence; (v) H1-ratio
  scaling stays rejected per P20I §2 (ill-posed definition/units mismatch,
  ~82× implying ΔK1 ~10⁴, violating the far-below-raw bar) and is not
  reopened; (vi) (D) P20D now is the wrong factor per above, deferred to the
  §16 zero-restoration branch AFTER the chain is complete. Single tier only —
  any second tier inside this packet is a second factor, forbidden.
- ΔK1 placement rule (frozen): order-prefix extension, isomorphic with the
  accepted K2 rule. E1 K1=831 is the first-831 prefix of the SAME frozen P16
  L1 order object — no reselection, no re-ranking, on ANY data (P20K DEV,
  P20I/P20H/P20J DEV, closed 1M ranges, 2M). Same slicing semantics as the
  accepted `l2_order[:k2]` rule (pinned by test). Any data-guided picking
  BLOCKS.
- Alternatives rejected in writing: (a) rerun P20J as-is — forbidden (attempt
  1/1 exhausted; identical rerun cannot discriminate); (b) refit/re-smooth the
  prior on P20K DEV or any DEV — DEV-tuning, forbidden (§3); (c) jump to P20D
  now — wrong factor per above, deferred to §16 zero-restoration branch;
  (d) efficiency round now — premature (no recovery under calibrated prior);
  (e) minimality probe beyond the single frozen tier (e.g. +256 vs +512 inside
  this packet) — second factor/step, forbidden; (f) consume 2M now — destroys
  the second-replication option; 2M stays pristine. All of (c)–(f) stay
  deferred per §16.
- Session inventory (unchanged from P20G/P20H/P20I/P20J §2 provenance; no new
  protected access by this planner): 1.5M TRAIN 1660/424960 + VAL 553/141568 +
  HOLD 554/141824 (256 rows/frame exact); pairs size 1869178 B / sha
  `ca351e52…a06b`; 2M TRAIN 2187/559872 reserved. 1.5M TRAIN geometric
  position: P20H consumed 0..383; P20I consumed 384..767; P20J consumed
  768..1151; P20K takes the NEXT 384 frames 1152..1535; remainder 1536..1659
  (124 frames) never used under this packet.

## 3. Prior-reuse freeze (normative — zero new calibration)

- FROZEN prior = the P20H Stage-A product read-only (no refit, no
  resmoothing, no relambda, no floor change):
  `per_session_calibration/calibrated_prior.npz` under
  `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/`
  (keys exactly `counts_ab`, `f_prior`, `p1`, `p2`, `p_b`, `lambda_star`,
  `floor_value`, `h1`, `h2`, `h_total`), canonical digest pin
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  (sorted-key `key + shape + dtype + C-order bytes` sha256), lambda pin
  `137.3823795883264`, floor pin `1e-15`, recalibrated literals H1
  `2.006647056368773` / H2 `1.9017235959286112` / TOTAL `3.908370652297384`.
- Stage B loads the frozen file read-only behind a calibration-identity digest
  gate (digest equality + lambda/floor pins + exact key set + recomputed
  H1/H2/TOTAL within 1e-12 of the literals, or BLOCKED before any SC call).
  The V25 counts NPZ is NEVER opened in this packet (counts opens 0; any NPZ
  loader inside the Stage-B runner BLOCKS at review). Prior load is a
  worktree-file read, not a protected open.
- FORBIDDEN inputs for any fitting: 1.5M DEV (1152..1535 and remainder), 1.5M
  VAL/HOLD, P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, ANY 1M
  split, reserved 2M, Model-F CAL artifact. No calibration fallback inside
  Stage B. This packet performs zero calibration opens (split-counted counts
  0/0; see §8).

## 4. Population and closed/consumed-data rule (normative)

- The three P18/P19 HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599),
  P20C/P20E/P20F DEV blocks (1M 0..383 / 384..767 / 768..1151, remainder
  1152..1199 never used), P20H DEV blocks (1.5M TRAIN 0..383, remainder
  accounting 384..1659 at P20H time), P20I DEV blocks (1.5M TRAIN 384..767,
  remainder accounting 768..1659 at P20I time), and P20J DEV blocks (1.5M TRAIN
  768..1151, remainder accounting 1152..1659 at P20J time) are CONSUMED/CLOSED
  and SHALL NOT supply P20K blocks. The ENTIRE 1M pool is fail-closed against
  P20K DEV selection (cross-file gate).
- The 2M session file SHALL NOT be opened, statted, listed, or read under this
  packet (reserved, not consumed; pristine by non-access; stat itself violates
  the packet).
- Stage B runs on the DECLARED population (P20J-UNCONSUMED next segment):

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin; mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| DEV frame rule | NEXT 384 TRAIN frames after P20J in (frame_id, pair_idx) order → frozen TRAIN base 0: `1152..1535` (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed) |
| DEV blocks (N=32768) | `1152..1279`, `1280..1407`, `1408..1535` (3 × 128 frames) |
| unused remainder | frames `1536..1659` (124 frames / 31744 pairs) recorded never used — counted, never decoded |
| intra-file VAL / HOLD | 1660..2212 / 2213..2766 — disjoint by fail-closed gate (VAL first) |
| P20H DEV exclusion | 1.5M TRAIN `0..383` — overlap refuses before any protected content open |
| P20I DEV exclusion | 1.5M TRAIN `384..767` — overlap refuses before any protected content open |
| P20J DEV exclusion | 1.5M TRAIN `768..1151` — overlap refuses before any protected content open |
| 1M full pool + reserved 2M | excluded by the cross-file gate (checked FIRST); never touched |
| block count | 3 at N=32768 (same cost class as P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J) |
| tag domains | new P20K domain (§6) |

- Fail-closed sextuple gate (frozen in the runner, order (a)→(b)→(c)→(d)→(e)→(f),
  VAL before HOLD): (a) CROSS-FILE — DEV content-open path + stat-size/sha pin
  must equal the 1.5M identity; any 1M or 2M path or digest mismatch refuses
  before any SC call (frame integers alone are never identity); (b) INTRA-FILE
  — DEV ranges must overlap NONE of 1.5M VAL/HOLD, else refuse before any
  protected content open; (c) P20H-DEV EXCLUSION — DEV ranges must overlap NONE
  of P20H DEV 0..383, else refuse before any protected content open;
  (d) P20I-DEV EXCLUSION — DEV ranges must overlap NONE of P20I DEV 384..767,
  else refuse before any protected content open; (e) P20J-DEV EXCLUSION — DEV
  ranges must overlap NONE of P20J DEV 768..1151, else refuse before any
  protected content open; (f) CALIBRATION-IDENTITY — Stage-B prior/table/literal
  digest must equal the §3 frozen digest before any SC call, else refuse.

## 5. Preregistered disclosure cap (normative, single frozen tier)

- Caps PREREGISTERED per arm, frozen before Pre-EXECUTE, each FAR below raw
  input bits with ratio shown. Key increment rule: keyΔ = 5·ΔK1 = 5·512 = 2560.

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| E0_sc_base (operational) | 319 | 6492 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| E1_L1plus512 (operational) | 831 | 6492 | 36679 = 5*7323+64 (base +2560) | 327743 |
| E2_true_l1_diagnostic (oracle) | 0 | 6492 | 32524 = 5*6492+64 | 327743 |

- Planned totals if all invoked: key 309966 = 3*34119 (102357) + 3*36679
  (110037) + 3*32524 (97572) (operational 212394 + oracle 97572);
  public 2949687 = 9*327743. E1 key-bit delta vs base exactly +2560 = 5*512.
- Meaningfulness bar: base 34119/327680 ≈ 10.41%, E1 36679/327680 ≈ 11.19%
  of raw input bits (10*N per block) — far below raw. Sample-CE-normalized
  ratios are descriptive, NOT qualification efficiency.
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate
  BLOCKS.

## 6. Arms (frozen; prior + L1 step swapped per §§2-3, all else P20H/P20I/P20J-identical)

- `E0_sc_base`: frozen greedy SC at base disclosure/construction (operational;
  2 SC + 1 P20K-domain tag per block; k1=319/k2=6492 on the frozen P16 order).
- `E1_L1plus512`: frozen greedy SC with the §2 +512 L1 order-prefix step
  (operational; the single-factor candidate; 2 SC + 1 P20K-domain tag per
  block; k1=831/k2=6492 as the first-831 prefix of the SAME frozen P16 L1
  order — no reselection, on ANY data).
- `E2_true_l1_diagnostic`: true-L1-conditioned diagnostic at BASE disclosure
  (provenance ORACLE, deployable=false, excluded from every operational
  aggregate; never a correction result; 1 SC + 1 P20K-domain tag per block).
- No other arms. Block-major (E0, E1, E2) per DEV block; checkpoint after every
  (arm, block) record; 9 records total. P16 construction/order/K migration
  unchanged (digest pinned in Stage-A freeze); kernel/representation/transform/
  SC arithmetic unchanged; greedy SC only; no SCL/new kernel/model/schema.
- Tag domain (new P20K): master 2026092250, prefix
  `nbpolar-p20k-l1-dose-512-1p5m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from
  ALL of P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J. Stage A
  verifies by repo grep that master 2026092250 and focused-test seeds
  `2026092251..2026092257` appear in no tracked file outside the P20K
  runner/tests/packet/spec documents.

## 7. Thresholds and labels (descriptive only)

- Outcome label `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_512_1P5M_COMPLETE`
  iff ALL integrity gates (§9) hold — regardless of exact-count. Any exact count
  (including 0/9 and partials) is COMPLETE when integrity holds.
- NO recovery / FER / Wilson / superiority / qualification / promotion claim.
  Descriptive reading only: "L1-restoration" = blocks where E0 fails and E1 is
  exact on the new-segment blocks (`e1_restored_count` analogue, count +
  per-block endpoint rows); "maintain" = E1 exact where E0 exact. Either (or
  neither) counts as COMPLETE; branch decisions belong to main-thread planning
  AFTER acceptance (§16).
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`,
  `undetected` isolated (never success/FER), plus `decode_failed` /
  `nonfinite` / `resource_abort` via the P20A path. P20A four-endpoint
  separation (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` / `pair_exact`)
  per record.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized
  execution; no rerun, no seed change, no disclosure/construction/calibration
  tuning after preregistration. Execution-error rerun only as a recorded repeat
  of the identical freeze, never as tuning. P20H/P20I/P20J spent attempts do NOT
  transfer (independent packet).
- Reads (split-counted, continuing P20J mode): counts-calibration opens 0/0
  (no NPZ open in this packet; prior reuse only) + DEV open 1/1 reserved for
  Stage B (parquet, consumed at first DEV content open). HOLD reads 0/1
  untouched. Any reopen, new calibration, or DEV refit is forbidden. Prior file
  load is a worktree-file read, not a protected open.
- SC/tag budget: 15 SC (3 blocks × (2+2+1)), 9 tags, 9 records; derived
  per-record recomputation must equal counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  accounting; abort is BLOCKED, never success. Wall/RSS ceilings frozen in
  Stage-A freeze (P20C-class reference ~92.9 s / ~579 MB; P20E ~100.1 s /
  ~554 MB; P20F ~93.0 s / ~553 MB; P20H ~114.27 s / ~533 MB; P20I ~110.58 s /
  ~533 MB; P20J ~107.75 s / ~533 MB at the identical 15 SC / 9-tag budget;
  P20K plans the identical decoder budget; external timeout 600 s + virtual/RSS
  caps 2 GiB + single thread frozen).
- Strategy stop rules binding: no tuning on closed blocks; no reuse of consumed
  1M pool (any split/subrange), P20H DEV 0..383, P20I DEV 384..767, P20J DEV
  768..1151, or reserved 2M; no third factor after inconclusive single-factor;
  no near-raw disclosure claim; no oracle-as-operational; no
  population-reliability inference from this single gate alone; no efficiency
  tuning inside this packet.
- SCL entry gate UNCHANGED (unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B five files)

- Stage-A freeze pins (no protected opens): exact module path + 16-flag Stage-B
  command verbatim + population integers + caps + budgets + tag domain + prior
  digest/literals + construction digest; recorded in `P20K_FREEZE.md`.
- Stage-B root: `.workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/l1_dose_512_1p5m/`
  (exactly five files, created pre-open; per-(arm, block) checkpointing; one DEV
  content open; no reopen/rerun). Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9 records at completion),
  `aggregate_summary.json`, `report.md`. Per-record §7 endpoints + first error
  coordinate/layer, zero-count hits, floor hits + log loss, true-H vs
  candidate-H L2 NLL, taxonomy, E1 disclosure triple (ΔK1=512, order-prefix,
  +2560 vs base).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0);
  SC counts (L1/L2 split) + tag counts exact; block SER/NLL; wall/RSS;
  `e1_restored_count` analogue descriptive.
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `dev_split_manifest_identity`;
  `dev_block_range_identity` (SEXTUPLE gate: cross-file source-tag+digest pin
  first, then intra-file DEV-vs-VAL/HOLD overlap with VAL first, then
  P20H-DEV exclusion, then P20I-DEV exclusion, then P20J-DEV exclusion, then
  calibration-identity digest pin); `calibration_identity` (prior digest +
  lambda/floor pins + key-set exactness, reuse-only); `target_population_contract`
  (recalibrated literals, recomputed H1/H2 within 1e-12 + column
  normalization); `dev_population_exact` (384 frames / 98304 pairs / 256 rows
  per frame / pair indices / symbol range); `blocks_exact_with_declared_remainder`
  (three exact DEV ranges per arm in block-major slot order + never-used
  remainder 124 frames / 31744 pairs, counted from the pool but never decoded);
  `nine_records_exact`; `sc_calls_exact` (derived 15); `tags_exact` (derived 9);
  `orders_valid_k_prefixes_within_registered_arms` (per-arm K1/K2 pins + E1
  disclosure triple); `oracle_isolation`; `buckets_disjoint_exhaustive`
  (unique arm/block + schema); `undetected_zero`; `nonfinite_zero`;
  `truth_isolation`; `disclosure_recount_exact`; `one_open_per_protected_input`;
  `input_stat_unchanged`; `no_unregistered_access`;
  `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (injected tests + implementation-freeze; authorized separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_<l1_dose_512 files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20k/<uuid>/`
  temp root; protected-open audit declared separately (counts 0 + DEV 0 at
  Stage-A close). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A prior check (read-only, zero protected opens): verify the P20H
  `calibrated_prior.npz` canonical digest equals
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b` via the
  frozen `canonical_prior_digest` function (worktree-file read only; never a
  counts open).
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A
  freeze; NOT AUTHORIZED until independent Pre-EXECUTE PASS + pasted Stage-B
  authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l1_dose_512_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames <FROZEN_AT_STAGE_A> --block-frames 128 --remainder-frames <FROZEN_AT_STAGE_A> --tag-master 2026092250 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/l1_dose_512_1p5m
```
  All flags required, no production default; three hardcoded arms with the +512
  L1 prefix-extension pinned (never CLI-tunable); Stage-B prior path MUST equal
  the §3 frozen digest. Stage A confirms the module path (thin runner reusing
  P18 loading/block formation + P16 operational helpers read-only; new P20K tag
  domains; sextuple gate) or freezes a written equivalent with justification;
  Stage A also freezes the exact `--dev-frames` / `--remainder-frames` integers
  (expected `1152 1535` / `1536 1659`) and the `--source` vocabulary (only `1p5M`).
  Forbidden by default: `longrun_*`, `minrerun_*`, `routeA_*`,
  `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git
  show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: thin runner + focused injected tests + Stage-A freeze +
  implementation notes (exact files, diffs, test commands/results, frozen
  prior/population/cap/command/budget). Protected content opens 0 at Stage-A
  close (counts 0 + DEV 0; prior digest check is a worktree-file read).
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md`
  (+ freeze, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`,
  `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec P20K delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20k/spec.md`
  + `tasks.md` P20K section (same umbrella change as
  P18/P19/P20A/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J; no new top-level change).

## 12. Allowed work

- New thin L1-dose-512 runner + focused injected tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest function + formula pins only),
  `plus1024_per_session_confirmation.py` (gate/population pattern reference),
  `l1_disclosure_1p5m.py` (gate/population/cap pattern reference),
  `l1_dose_escalation_1p5m.py` (gate/population/cap pattern reference)
  (+ `construction.py`, `prior.py`, `sc.py` contracts as called).
- Read-only load of the P20H `calibrated_prior.npz` (digest-pinned; never
  refit/resmoothed).
- P20K OpenSpec delta + packet docs + Stage-A freeze/return/review files +
  Stage-B evidence root (root only after Stage-B authorization).

## 13. Forbidden work

- Any NPZ/parquet content open or stat of 1.5M DEV/VAL/HOLD, any 1M split, or
  reserved 2M in Stage A (Stage-A protected opens 0); any counts NPZ open,
  prior refit/resmoothing/relambda, or DEV calibration at any stage; any
  decoder execution before Pre-EXECUTE PASS + pasted Stage-B authorization.
- Any change to GF32/transform/SC arithmetic, floor value, construction order
  (including the frozen prefix-extension rules themselves), tag scheme
  semantics, outcome precedence, accepted evidence roots, P20H calibration
  product, or `src/` + `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the
  consumed 1M pool (any split/subrange), P20H DEV 0..383, P20I DEV 384..767,
  P20J DEV 768..1151, or the reserved 2M file; no second factor (alternative
  construction) inside this packet; no second L1 tier (`E1b`); no second L2
  step; no efficiency tuning; no new-block peeking before the authorized
  attempt; no calibration on DEV.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push; no self-acceptance; no P20D scope creep; no P20H/P20I/P20J rerun
  under this packet.

## 14. Acceptance IDs

- `P20K-R1`: prior reuse frozen read-only (§3 digest/lambda/floor/key-set pins;
  zero new calibration opens; V25 NPZ never opened; no refit path in runner);
  §3 reuse evidenced at Pre-EXECUTE. Reuse-gate BLOCKED → planner rework, never
  a Stage-B fallback.
- `P20K-R2`: closed blocks select nothing; consumed 1M pool excluded by
  source-tagged cross-file gate; P20H DEV 0..383, P20I DEV 384..767, and P20J
  DEV 768..1151 excluded by P20H-DEV/P20I-DEV/P20J-DEV gates; reserved 2M
  untouched (never opened/statted/listed); P20K DEV 1152..1535 (3 blocks
  1152..1279/1280..1407/1408..1535, remainder 1536..1659 never used)
  digest-pinned, sextuple-gated + calibration-identity-gated,
  Pre-EXECUTE-approved.
- `P20K-R3`: disclosure caps preregistered per arm (34119 / 36679 / 32524 +
  327743 public), keyΔ 2560 = 5·512, ratios-vs-raw shown (~10.41% / ~11.19%),
  recount mismatch 0; CE ratios never called efficiency.
- `P20K-R4`: +512 L1 step + order-prefix rule frozen before execution,
  unchanged after; P16 construction/order/K migration pinned; no tag-guided
  selection, no evidence reuse, no post-hoc re-picking.
- `P20K-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9;
  `undetected` isolated; oracle arm never operational.
- `P20K-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning;
  split-counted reads (counts 0/0 + DEV 1/1 + HOLD 0/1); resource aborts via
  P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20K-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded;
  main-thread acceptance owns the label; descriptive-only, no
  FER/qualification/promotion language; branch reading (§16) stays planning
  input, never an in-packet verdict.
- `P20K-R8`: Stage-A suites green on injected data with zero protected opens
  audit (counts 0 + DEV 0 at Stage-A close; 2M non-access); no commit/push;
  frozen dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs
`P20K-R1..R8` (stage-appropriately) complete with changed files + exact
commands/results + artifact inventory + split open audit (counts + DEV + HOLD
separately); or (b) a concrete blocker with failing command, exact
error/traceback, attempted remedies, and the ONE decision needed from the main
thread. "Still incomplete" is not a completion report. The operator never marks
its own work accepted and never authorizes Stage B.

## 16. Deferred options (not in this packet)

- E1-restoration → maintain-confirmation round (deferred): trigger = at least
  one block with E0 fail → E1 exact on the new segment (genuine L1-restoration
  event, not maintain-only). Then a LATER packet may preregister a maintain
  confirmation on further new data (1.5M remainder/used-pool recheck first;
  reserved 2M first-use is a candidate population but NOT pre-authorized here —
  the new packet decides, and the standing preference is to re-examine 1.5M
  remainder/used pools before touching 2M). This packet performs no follow-up
  confirmation and licenses no reliability claim.
- E1-zero-restoration → close the disclosure route (deferred): trigger =
  genuine L1-negative under the frozen prior + frozen +512 tier — E0 failures
  occur on new-segment blocks but E1 restores NONE (with first-error layer rows
  as evidence). Only THEN do all three L1 doses (+128, +256, +512) count as
  tried on 1.5M calibrated data, and only then does the disclosure route close
  as evidence: turn to NON-DISCLOSURE factors by new-packet decision — either
  fixed-disclosure alternative-L2-construction work (P20D strategy option 2 on
  independent development data) or L1-model/prior-structure work (model, prior
  form, or search diagnostic — one factor per packet). P20I alone and P20J
  alone did not license closure per the §2 semantic-offset rationale; P20K
  zero-restoration completes the three-dose set that does.
- Maintain-only (E0 exact somewhere and E1 exact wherever E0 exact, zero
  fail→exact events) → further planning (deferred): neither restoration nor
  negative; main thread re-evaluates dose (still-larger L1 tier as its own
  single-factor packet vs P20D vs efficiency vs L1-model work) with the full
  chain evidence in hand. This packet prejudges none of them.
- Disclosure-minimality probe, efficiency optimization, P20D candidate itself,
  second independent session on reserved 2M: ALL continue deferred,
  re-evaluated against P20K accepted evidence after acceptance.
- 2M stays PRISTINE under this packet — never opened, never statted, never
  listed — as the follow-up replication population. Any 2M packet needs its own
  freeze, tag domain, and reviews.
