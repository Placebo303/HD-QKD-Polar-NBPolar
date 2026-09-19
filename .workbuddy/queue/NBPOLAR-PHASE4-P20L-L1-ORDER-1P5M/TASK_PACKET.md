# Phase 4-P20L — Frozen L1-order single-factor packet on type2_1p5M_20260121_183806 (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage A implementation-freeze, Stage B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read, decoder execution, or commit/push is authorized by this file.
- Revision: `P20L-R1delta` (planner-only doc revision; no K/prior/construction/population/cap/tag/budget/gate change): order-derivation creation point moved from Stage-B in-run pre-DEV to Stage-A synthetic-only derivation producing the frozen order file `new_l1_order_1p5m.json` with Stage-B digest-gated read-only use and zero Stage-B sampling. Reason: reviewability over in-run creation — the single factor must be frozen and independently reviewable (difference degree / overlap coordinates / digest pin vs the old order) before the one-shot attempt; an in-run creation bug would waste the single attempt on an unreviewable product. All other freeze pins byte-identical in meaning.
- Predecessor: `NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M` terminal
  `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_512_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; DEV open 1/1 SPENT
  on 1.5M TRAIN 1152..1535; 9/9 records; 21/21 gates PASS; E0 base-K1 0/3
  verify_failed + E1 L1+512 (K1 831, keyΔ +2560) 0/3 verify_failed +
  e1_restored 0/3; same-block E0→E1 coordinates blk0 16/L1→3/L1, blk1 7/L1→5/L1,
  blk2 3/L1→2/L1, all six operational first errors L1-layer; E2 oracle 3/3 exact
  isolated; undetected 0; SC 15/15; tags 9/9; recount 0; key 309966 /
  public 2949687; 2M pristine by non-access; Pre-RESULT PASS; STATUS notes
  carry a known stale-planning-text residual, non-semantic).
- Dose-chain precedent carried (all descriptive-accepted): P20I +128 on 1.5M TRAIN
  384..767 (C0 0/3 + C1 0/3, mixed first-error move 2→2 / 17→1 / 13→16, C2 oracle
  3/3); P20J +256 on 1.5M TRAIN 768..1151 (D0 0/3 + D1 0/3, full deferral
  14→23 / 6→25 / 1→21, D2 oracle 3/3); P20H +1024 L2 on 1.5M TRAIN 0..383
  (B0 0/3 + B1 0/3, first errors identical 16/6/8 across B0/B1, B2 oracle 3/3).
  Cumulative disclosure-route evidence: 18/18 operational failures with first error
  all L1-layer across the three L1-dose packets (I/J/K), 0/9 L1-restoration;
  oracle 12/12 exact at base K2 given true L1 across H/I/J/K.
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2
  (reproducible reliability; confirmation on new blocks/sessions; stop rules;
  single-factor options 1/2/3) and `docs/nbpolar/ROADMAP.md`.
- Gate discipline: any standing long-horizon authorization does NOT collapse
  Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_1p5M_20260121_183806` (1.5M), scoring population
  first-use of 1.5M VAL (see §4). The 2M session
  (`type2_2M_20260121_183657`) is registered but RESERVED pristine (see §4, §16).

## 0. Planner header (OpenSpec workflow)

- **Goal**: With everything from P20H carried over read-only (per-session prior
  digest-pinned, K1=319/K2=6492, floor 1e-15, N=32768, greedy SC only, same
  disclosure budget) and exactly ONE preregistered change — the L1 disclosure
  positions (old P16 1M-derived L1 order vs new 1.5M-prior-derived L1 order,
  same K1=319 prefix length, L2 order frozen) — decide whether same-budget
  better-placed L1 disclosure restores any complete operational block on three
  NEW 1.5M VAL blocks at N=32768 (three arms F0/F1/F2, new P20L tag domain),
  with zero further tuning.
- **Non-Goals**: No disclosure-budget change (no +ΔK tier of any size), no P20D
  alternative L2 construction, no bounded-search second factor, no prior
  refit/resmoothing/relambda or λ change, no K reselection, no SCL/new
  kernel/model/schema, no FER/qualification/promotion claim, no efficiency
  tuning, no reuse of any consumed/closed range, no 2M first use.
- **Impact Scope**: New thin runner + focused injected tests + P20L OpenSpec
  delta (`specs/nbpolar-phase4-p20l/spec.md` + `tasks.md` P20L section, same
  umbrella change `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A freeze
  + implementation notes + Stage-B evidence root. No change to `src/`,
  `experiments/`, `tools/`, P16 construction file, P12–P20K accepted roots,
  P20H calibration product, or `results/` / `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20L-R1..R8 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance.
  Descriptive-only label; `undetected` isolated; oracle never operational.
  STATUS notes must describe the current stage truthfully at every gate;
  stale planning-text copy BLOCKS review (P20K lesson).
- **Tasks**: (planner task list for coder agents) H1 freeze prior reuse (§3, R1);
  H2 freeze order-derivation program/input/seeds + population/gates (§4, R2);
  H3 freeze caps — same budget both operational arms (§5, R3); H4 freeze
  L1-order swap rule, K-frozen, L2-frozen (§2/§6, R4); H5 wire endpoints/taxonomy
  (§7, R5); H6 enforce one-shot budget/stop (§8, R6); H7 Stage-A suites green
  with zero-protected-open audit (R8); H8 independent Pre-EXECUTE adjudication
  of reuse + order + population gates (R7); H9 single authorized Stage-B
  attempt (R6/R7); H10 independent Pre-RESULT + acceptance.

## 1. Mission

With ONE preregistered change against P20H/P20I/P20J/P20K — L1 disclosure
POSITIONS (Stage-A synthetic-only derivation → frozen order file → digest pin,
Stage-B read-only digest-gated use with zero sampling) — and everything else carried over from P20H
(per-session prior digest-pinned read-only, K1=319/K2=6492, floor 1e-15,
N=32768, greedy SC only, new P20L tag domains only), zero further tuning:

> Does same-budget 1.5M-derived L1 order restore any complete operational block
> on three NEW 1.5M VAL blocks (1660..2043) — and do operational first errors
> stay L1-layer under both orders, or does the bottleneck layer move?

P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, P20K DEV 1152..1535 are
CONSUMED (9+9+9+9 records, DEV 1/1 + attempt 1/1 SPENT each) and SHALL NOT
supply P20L blocks. 1.5M TRAIN remainder 1536..1659 (124 frames) is documented
insufficient for one N=32768 block and SHALL NOT supply P20L blocks. All
branches after this packet are deferred to §16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- Disclosure route closed (descriptive, convergent H/I/J/K): +128 moved
  coordinates without restoration (mixed move); +256 deferred every first error
  without restoration (full deferral 14→23/6→25/1→21); +512 again restored
  nothing (16→3/7→5/3→2, all six operational first errors L1-layer, keyΔ +2560
  spent). The three dose segments are NON-SAME-BLOCK, so inter-packet coordinate
  deltas are never a slope; licensed fact is narrower and sufficient: within
  each packet, paired same-block E0→E1 moves respond to L1 disclosure yet 0/9
  blocks restore across I/J/K (18/18 operational first errors L1-layer). The
  +128/+256/+512 doubling chain is therefore COMPLETE on 1.5M calibrated data;
  further disclosure tiers are closed as evidence, not as a verdict on all
  disclosure ever.
- Oracle reading (first principles): 3/3 exact under true-L1 conditioning at
  base K2=6492 on EVERY 1.5M segment (H B2, I C2, J D2, K E2 → 12/12) proves
  that, GIVEN true L1, the base-K2 L2 path with the frozen P16 L2 order is
  sufficient on these twelve blocks. SC is sequential: extra L2 disclosure
  conditions on wrong hard L1 and cannot rescue it (P20H B1 first errors
  identical to B0). The bottleneck is L1-side at this operating point.
- Candidate ranking (planner, written, evidence-strength order; exactly one
  frozen):
  (b) L1-coordinate order replacement — STRONGEST, FROZEN. The P16 L1 order is
  a 1M-statistics product: worst-first `(e,h,index)` from P13 true-prefix genie
  risks pooled on 1M TRAIN model samples under 1M literals H1
  `0.02428054681872374` / H2 `0.7767572780789994` / TOTAL
  `0.8010378248977232`. The 1.5M session under the frozen P20H prior sits at H1
  `2.006647056368773` / H2 `1.9017235959286112` / TOTAL `3.908370652297384`
  (~83× in H1). Disclosing the first-319/575/831 prefix of a 1M ranking on
  1.5M data plausibly discloses the WRONG 319 coordinates: more budget delays
  failure (covers more error mass by brute force) without hitting the true
  1.5M unreliable set — exactly the observed deferral-without-restoration
  pattern. The test holds disclosure BUDGET fixed (K1=319 both arms, keyΔ 0)
  and varies only POSITIONS: same program, new session input, no DEV contact.
  Practically meaningful (identical leakage, better placement) and upstream of
  every other L1-side hypothesis: if positions are wrong, search diagnostics
  around the wrong set are confounded, so order precedes search in causal
  order.
  (c) L1 bounded-search diagnostic (P20B L1-side 1.5M version: frozen
  disclosure/construction/prior, bounded rescore-only re-evaluation for SC-missed
  candidates) — SECOND, DEFERRED. P20B on 1M VAL gave a bounded negative (S1
  0/3, search_better 0/3, greedy selected with 0.0-bit dNLL): SC did not miss a
  present candidate there. A 1.5M L1-side analogue would distinguish SC-search
  failure from position/prior failure — but ONLY after positions stop being
  the confound. Running it now, under the known-wrong 1M order, risks an
  ambiguous negative. Deferred to the §16 order-negative trigger, at frozen
  new-order disclosure.
  (a) P20D original concept (fixed disclosure + ONE alternative L2
  construction) — WEAKEST, DEFERRED. Semantic offset is maximal: it changes
  the factor the oracle evidence exonerates. 12/12 true-L1-conditioned exact
  at base K2 plus the P20H +1024-L2 no-move negative are two independent
  L2-side negatives. P20D's only remaining justification would be
  "L2 construction matters under hard-L1 errors even though it suffices under
  true L1" — a speculative second-order effect with no positive evidence on
  twelve blocks. Not worth spending a Tier-Y attempt now; deferred to the §16
  L2-implication trigger (new-order oracle non-exact, or bottleneck-layer move
  to L2 with search-positive-but-unrestored pattern).
- Known alternate hypothesis, explicitly frozen out (not a fourth arm): the
  2026-09-19 λ critique (λ=137.38 lifts H1 ~0.02→2.007; absolute-bit budget
  frozen across sessions; in-sample/out-of-sample concerns). Prior-form/λ work
  is a DIFFERENT single factor (prior/model structure) from order positions.
  This packet freezes the P20H prior byte-identical (same λ, same H literals)
  so the order factor is isolated; λ/prior-form work is deferred to §16 with
  its own trigger and its own packet. No λ change, no refit, no debate in
  Stage A/B.
- Order-derivation design (frozen principle; Stage A derives and freezes):
  input = the P20H calibrated prior read-only (digest-pinned §3; itself the
  1.5M TRAIN-fitted product — this IS the "same program, new 1.5M TRAIN input"
  with zero new counts opens); program = the accepted P13/P16 L1 genie
  procedure byte-identical (true-prefix genie L1 risks → pool means per
  coordinate → worst-first `(e,h,index)` order1; L2 NOT re-derived, K NOT
  reselected); TRAIN = model-sampled synthetic blocks from the prior under new
  preregistered TRAIN seeds (same 16-block count class as P16; disjoint from
  every frozen master/stream/tag/test seed; never a real frame, never DEV);
  freeze = Stage-A synthetic-only derivation (P20L-R1delta revision; §12
  allowed work): the 16 synthetic L1-only TRAIN genie calls run in Stage A
  under the zero-protected-read premise (worktree prior file + seed integers
  only; zero DEV contact, zero counts opens), output is the frozen order file
  `new_l1_order_1p5m.json` (§9 product identity) with its sha256 digest pinned
  in `P20L_FREEZE.md` plus old-order对照 (difference degree / overlap
  coordinates / digest pin of the P16 L1 order vs the new order) for
  independent review; Stage B loads the frozen file read-only behind the
  order-digest gate (§10 `--order-file` + `--order-digest`) and performs ZERO
  sampling (no TRAIN genie call, no re-derivation, no reselection).
  Single factor = L1 order positions at fixed
  K1=319. F1 uses first-319 prefix of the NEW L1 order; F0 uses first-319
  prefix of the SAME frozen P16 L1 order object (no reselection, on ANY data).
  L2 order stays the frozen P16 L2 order for both operational arms.
- Alternatives rejected in writing: (a) fourth disclosure tier (any +ΔK1) —
  chain complete, forbidden; (b) rerun any of P20H/I/J/K as-is — attempts
  exhausted, forbidden; (c) refit/resmooth/relambda the prior on any DEV/VAL —
  DEV-tuning, forbidden (§3); (d) K reselection on any real data (including
  the new VAL DEV) — second factor, forbidden; (e) L2 order swap inside this
  packet — second factor, forbidden; (f) bounded search inside this packet —
  second factor, deferred per above; (g) P20D now — wrong factor per above,
  deferred; (h) efficiency round now — premature (no recovery anywhere);
  (i) consume 2M now — destroys the independent-session confirmation option
  for a same-session diagnostic; 2M stays pristine.
- Session inventory (no new protected access by this planner; provenance from
  P20G/H/I/J/K §2 + split manifest `nbldpc_v25_split_manifest_v1`): 1.5M TRAIN
  1660/424960 + VAL 553/141568 + HOLD 554/141824 (256 rows/frame exact); pairs
  size 1869178 B / sha `ca351e52…a06b`; 2M TRAIN 2187/559872 reserved.
  Geometric position (TRAIN base 0 carried from P20H §3): P20H 0..383, P20I
  384..767, P20J 768..1151, P20K 1152..1535 consumed; remainder 1536..1659
  (124 frames / 31744 pairs, < one 128-frame block) never used; VAL 1660..2212
  never touched by any NB-Polar packet (intra-file gate, never selected);
  HOLD 2213..2766 never touched. P20L DEV is the FIRST 384 VAL frames
  1660..2043; VAL remainder 2044..2212 (169 frames) never used under this
  packet.

## 3. Prior-reuse freeze (normative — zero new calibration)

- FROZEN prior = the P20H Stage-A product read-only (no refit, no
  resmoothing, no relambda, no floor change, no λ change):
  `per_session_calibration/calibrated_prior.npz` under
  `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/`
  (keys exactly `counts_ab`, `f_prior`, `p1`, `p2`, `p_b`, `lambda_star`,
  `floor_value`, `h1`, `h2`, `h_total`), canonical digest pin
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  (sorted-key `key + shape + dtype + C-order bytes` sha256), lambda pin
  `137.3823795883264`, floor pin `1e-15`, recalibrated literals H1
  `2.006647056368773` / H2 `1.9017235959286112` / TOTAL `3.908370652297384`.
- The order-derivation TRAIN is model-sampled SYNTHETIC blocks from this frozen
  prior (new preregistered TRAIN seeds §6); sampling a worktree-file prior is
  not a protected open and never touches a real frame. The V25 counts NPZ is
  NEVER opened in this packet (counts opens 0; any NPZ loader inside the
  Stage-B runner BLOCKS at review). Prior load is a worktree-file read, not a
  protected open.
- Stage B loads the frozen file read-only behind a calibration-identity digest
  gate (digest equality + lambda/floor pins + exact key set + recomputed
  H1/H2/TOTAL within 1e-12 of the literals, or BLOCKED before any TRAIN
  sampling and before any SC call).
- FORBIDDEN inputs for any fitting or derivation: 1.5M DEV (1660..2043 and
  remainder), 1.5M HOLD, P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151,
  P20K DEV 1152..1535, TRAIN remainder 1536..1659, ANY 1M split, reserved 2M,
  Model-F CAL artifact. No calibration fallback inside Stage B. This packet
  performs zero calibration opens (split-counted counts 0/0; see §8).

## 4. Population and closed/consumed-data rule (normative)

- The three P18/P19 HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599),
  P20C/P20E/P20F DEV blocks (1M 0..383 / 384..767 / 768..1151, remainder
  1152..1199 never used), P20H DEV blocks (1.5M TRAIN 0..383), P20I DEV blocks
  (1.5M TRAIN 384..767), P20J DEV blocks (1.5M TRAIN 768..1151), and P20K DEV
  blocks (1.5M TRAIN 1152..1535, remainder accounting 1536..1659) are
  CONSUMED/CLOSED and SHALL NOT supply P20L blocks. The ENTIRE 1M pool is
  fail-closed against P20L DEV selection (cross-file gate). 1.5M TRAIN
  remainder 1536..1659 (124 frames < one 128-frame N=32768 block) is
  documented insufficient and SHALL NOT supply P20L blocks.
- The 2M session file SHALL NOT be opened, statted, listed, or read under this
  packet (reserved, not consumed; pristine by non-access; stat itself violates
  the packet).
- VAL-first-use justification (frozen): 1.5M VAL 1660..2212 has never been
  decoded, tuned on, or scored by any NB-Polar packet; TRAIN is geometrically
  exhausted for N=32768 DEV (only 124 sub-block frames remain); 2M must be
  preserved for a future independent-session confirmation once something
  restores. Using VAL here as a one-shot scoring population with TRAIN-derived
  hypotheses (order derived from TRAIN-fitted prior, never from VAL frames) is
  the canonical TRAIN→held-out separation — stronger than the prior
  TRAIN-subset→TRAIN-subset practice — PROVIDED it is declared once, consumed
  once, never tuned, and never returned to a validation role. HOLD stays
  untouched; the VAL remainder stays undecoded. This rationale is frozen and
  not re-argued in Stage A/B.
- Stage B runs on the DECLARED population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin; mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| order-derivation TRAIN | 16 synthetic blocks model-sampled from the §3 frozen prior under new preregistered TRAIN seeds, derived IN STAGE A ONLY (exact seeds frozen at Stage A; disjoint from every frozen master/stream/tag/test seed; never a real frame); product is the frozen `new_l1_order_1p5m.json` order file (§9); Stage B performs zero sampling |
| DEV frame rule | FIRST 384 VAL frames in (frame_id, pair_idx) order → frozen VAL base 1660: `1660..2043` (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed) |
| DEV blocks (N=32768) | `1660..1787`, `1788..1915`, `1916..2043` (3 × 128 frames) |
| unused remainder | VAL frames `2044..2212` (169 frames / 43264 pairs) recorded never used — counted, never decoded |
| intra-file TRAIN/HOLD | TRAIN 0..1659 / HOLD 2213..2766 — disjoint by fail-closed gate (TRAIN-consumed ranges checked before HOLD) |
| consumed-TRAIN exclusions | 1.5M TRAIN `0..383` (P20H), `384..767` (P20I), `768..1151` (P20J), `1152..1535` (P20K), remainder `1536..1659` — overlap refuses before any protected content open |
| 1M full pool + reserved 2M | excluded by the cross-file gate (checked FIRST); never touched |
| block count | 3 at N=32768 (same cost class as P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K) |
| tag domains | new P20L domain (§6) |

- Fail-closed septuple gate (frozen in the runner, order (a)→(g), VAL/HOLD
  before consumed-TRAIN): (a) CROSS-FILE — DEV content-open path +
  stat-size/sha pin must equal the 1.5M identity; any 1M or 2M path or digest
  mismatch refuses before any sampling or SC call (frame integers alone are
  never identity); (b) INTRA-FILE VAL/HOLD — DEV ranges must overlap NONE of
  1.5M VAL-exterior/HOLD, and must lie wholly inside VAL 1660..2212, else
  refuse before any protected content open; (c) P20H-DEV EXCLUSION — DEV must
  overlap NONE of TRAIN 0..383; (d) P20I-DEV EXCLUSION — NONE of 384..767;
  (e) P20J-DEV EXCLUSION — NONE of 768..1151; (f) P20K-DEV + REMAINDER
  EXCLUSION — NONE of 1152..1659;   (g) CALIBRATION-IDENTITY + ORDER-FREEZE —
  §3 digest pins must match AND the Stage-A frozen order-file digest
  (`--order-digest` vs `new_l1_order_1p5m.json` bytes) must match with
  derivation inputs (prior digest + program pin + TRAIN seeds) replaying
  exactly, else refuse before any SC call. No sampling or derivation exists
  in Stage B.

## 5. Preregistered disclosure cap (normative — same budget both operational arms)

- Caps PREREGISTERED per arm, frozen before Pre-EXECUTE. The order factor
  carries ZERO key-bit delta by construction (same K1/K2, positions differ).

| arm | K1 | K2 | L1 order | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|---|
| F0_old_order_base (operational) | 319 | 6492 | P16 1M order first-319 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| F1_new_l1_order_base (operational) | 319 | 6492 | NEW 1.5M L1 order first-319, L2 = P16 frozen | 34119 = 5*6811+64 (Δ vs F0 exactly 0) | 327743 |
| F2_true_l1_diagnostic (oracle) | 0 | 6492 | — (true L1) | 32524 = 5*6492+64 | 327743 |

- Planned totals if all invoked: key 302286 = 3*34119 (102357) + 3*34119
  (102357) + 3*32524 (97572) (operational 204714 + oracle 97572);
  public 2949687 = 9*327743.
- Meaningfulness bar: 34119/327680 ≈ 10.41% of raw input bits (10*N per
  block) — far below raw, identical for F0/F1 so any F0→F1 difference is
  positions, not budget. Sample-CE-normalized ratios are descriptive, NOT
  qualification efficiency.
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate
  BLOCKS. Per-record order-source fields (`l1_order_source` old-1M/new-1p5M,
  `l1_order_digest`, `l1_prefix_len` 319, `key_bit_delta_vs_F0` 0) pinned.

## 6. Arms (frozen; order swapped per §2, all else P20H-identical)

- `F0_old_order_base`: frozen greedy SC at base disclosure with the frozen P16
  orders (operational; 2 SC + 1 P20L-domain tag per block; k1=319/k2=6492 on
  the P16 order objects).
- `F1_new_l1_order_base`: frozen greedy SC at the SAME base disclosure with
  the Stage-A frozen order file (§9 `new_l1_order_1p5m.json`, digest-gated;
  P20L-R1delta revision) (operational; the single-factor candidate;
  2 SC + 1 P20L-domain tag per block; k1=319/k2=6492; L1 set = first-319 of
  the frozen NEW 1.5M L1 order FILE, L2 set = first-6492 of the SAME frozen P16 L2
  order — no reselection, on ANY data).
- `F2_true_l1_diagnostic`: true-L1-conditioned diagnostic at BASE disclosure
  (provenance ORACLE, deployable=false, excluded from every operational
  aggregate; never a correction result; 1 SC + 1 P20L-domain tag per block).
- No other arms. Block-major (F0, F1, F2) per DEV block; checkpoint after every
  (arm, block) record; 9 records total. P16 construction/K migration unchanged
  except the Stage-A frozen order file (digest-pinned in the freeze);
  kernel/representation/transform/SC arithmetic unchanged; greedy SC only; no
  SCL/new kernel/model/schema. Order derivation (16 synthetic L1-only TRAIN
  genie calls) runs IN STAGE A ONLY producing the frozen order file (§9);
  Stage B performs pure DEV scoring (15 SC + 9 tags) with ZERO sampling —
  the Stage-B TRAIN genie call count is pinned at 0 and the 16 derivation
  calls are accounted in the Stage-A freeze, separately from DEV SC.
- Tag domain (new P20L): master 2026092260, prefix
  `nbpolar-p20l-l1-order-1p5m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from
  ALL of P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K. Stage A
  verifies by repo grep that master 2026092260, focused-test seeds
  `2026092261..2026092267`, and TRAIN seeds (expected
  `2026092271..2026092274`, 16 synthetic blocks) appear in no tracked file
  outside the P20L runner/tests/packet/spec documents.
- TRAIN seeds (expected `2026092271..2026092274`, 4 streams × 4 blocks = 16
  synthetic TRAIN blocks, model-sampled from the §3 prior, L1-genie only,
  CONSUMED IN STAGE A to produce the frozen order file):
  Stage A confirms exact integers or replaces with a written equivalent +
  justification + re-review; never assumed. They must be disjoint from every
  frozen P16/P17 DEV stream, every P20 tag master/test seed, and the P20L tag
  master/test seeds. Stage B takes NO `--train-seeds` and performs no
  sampling (P20L-R1delta).

## 7. Thresholds and labels (descriptive only)

- Outcome label `TARGET_EMPIRICAL_N32768_DEV_L1_ORDER_1P5M_COMPLETE`
  iff ALL integrity gates (§9) hold — regardless of exact-count. Any exact count
  (including 0/9 and partials) is COMPLETE when integrity holds.
- NO recovery / FER / Wilson / superiority / qualification / promotion claim.
  Descriptive reading only: "L1-order-restoration" = blocks where F0 fails and
  F1 is exact on the new VAL segment (`f1_restored_count`, count +
  per-block endpoint rows); "maintain" = F1 exact where F0 exact. Either (or
  neither) counts as COMPLETE; branch decisions belong to main-thread planning
  AFTER acceptance (§16).
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`,
  `undetected` isolated (never success/FER), plus `decode_failed` /
  `nonfinite` / `resource_abort` via the P20A path. P20A four-endpoint
  separation (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` / `pair_exact`)
  per record. First-error coordinate/layer rows are the primary
  order-diagnostic signal (L1-layer persistence vs layer move).

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized
  execution; no rerun, no seed change, no disclosure/construction/calibration/
  order tuning after preregistration. Execution-error rerun only as a recorded
  repeat of the identical freeze, never as tuning. P20H/P20I/P20J/P20K spent
  attempts do NOT transfer (independent packet).
- Reads (split-counted): counts-calibration opens 0/0 (no NPZ open in this
  packet; prior reuse + synthetic TRAIN sampling only) + DEV open 1/1 reserved
  for Stage B (parquet, consumed at first DEV content open). HOLD reads 0/1
  untouched. Any reopen, new calibration, real-TRAIN-frame use for derivation,
  or DEV refit is forbidden. Prior file load and synthetic TRAIN sampling are
  worktree-file/prior reads, not protected opens.
- SC/tag/genie budget: Stage-A derivation 16 TRAIN genie L1-only calls
  (frozen order-file product, accounted in the Stage-A freeze) + Stage-B pure
  DEV 15 SC (3 blocks × (2+2+1)) + 9 tags + 9 records with ZERO Stage-B
  sampling (Stage-B TRAIN genie calls pinned at 0); derived
  per-record recomputation must equal counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  accounting; abort is BLOCKED, never success. Wall/RSS ceilings frozen in
  Stage-A freeze (P20-class reference at the identical DEV decoder budget:
  P20C ~92.9 s / ~579 MB; P20J ~107.75 s / ~533 MB; P20K ~107.64 s / ~559 MB;
  P20L plans the identical 15-SC / 9-tag DEV budget in Stage B (zero sampling)
  with the 16 light TRAIN L1 genie calls accounted in Stage A (order-file
  derivation); external timeout 600 s + virtual/RSS caps 2 GiB + single thread
  frozen).
- Strategy stop rules binding: no tuning on closed blocks or the new VAL DEV
  after the one shot; no reuse of consumed 1M pool (any split/subrange), any
  consumed 1.5M TRAIN DEV, TRAIN remainder 1536..1659, VAL remainder 2044..2212
  beyond counting, HOLD, or reserved 2M; no third factor after inconclusive
  single-factor; no near-raw disclosure claim; no oracle-as-operational; no
  population-reliability inference from this single gate alone; no efficiency
  tuning inside this packet.
- SCL entry gate UNCHANGED (unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B five files)

- Stage-A freeze pins (no protected opens): exact module path + N-flag Stage-B
  command verbatim + order-derivation program pin + TRAIN-seed integers +
  population integers + caps (same-budget) + budgets + tag domain + prior
  digest/literals + construction digest + frozen order-file digest;
  recorded in `P20L_FREEZE.md`. Stage-A order-file product identity
  (P20L-R1delta): path
  `.workbuddy/queue/NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M/new_l1_order_1p5m.json`,
  format JSON holding the full L1 permutation plus provenance (prior digest +
  program pin + TRAIN-seed integers), sha256 digest of the file bytes pinned
  in the freeze with old-order对照 (difference degree / overlap coordinates /
  P16-L1-order digest pin) for independent review.
- Stage-B root: `.workbuddy/queue/NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M/l1_order_1p5m/`
  (exactly five files; per-(arm, block) checkpointing; pure DEV scoring —
  zero sampling; one DEV content open; no reopen/rerun).
  Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`
  (P16 construction digest + P20H prior digest + BOTH L1 order digests with
  the Stage-A order-file digest-gate proof (file bytes sha256 equals the
  frozen `--order-digest`) + TRAIN-seed pins (derivation provenance only, no
  Stage-B sampling) + split manifest + VAL DEV integers), `per_block_arm_outcomes.jsonl` (9 records at completion),
  `aggregate_summary.json`, `report.md`. Per-record §7 endpoints + first error
  coordinate/layer, zero-count hits, floor hits + log loss, true-H vs
  candidate-H L2 NLL, taxonomy, F1 order fields (`l1_order_source`,
  `l1_order_digest`, `l1_prefix_len` 319, `key_bit_delta_vs_F0` 0).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0);
  TRAIN-genie call counts + SC counts (L1/L2 split) + tag counts exact; block
  SER/NLL; wall/RSS; `f1_restored_count` descriptive.
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `prior_identity`;
  `dev_split_manifest_identity`; `dev_block_range_identity` (SEPTUPLE gate:
  cross-file source-tag+digest pin first, then intra-file VAL-containment +
  VAL-exterior/HOLD overlap with VAL checked first, then P20H-DEV, P20I-DEV,
  P20J-DEV, P20K-DEV+remainder exclusions, then calibration-identity +
  order-freeze pins); `order_derivation_identity` (program pin + prior-digest
  input pin + TRAIN-seed pins + L1-only + K-frozen + L2-frozen pins +
  Stage-A order-file digest pinned in the freeze, Stage-B file-bytes
  digest equality replay-exact, zero Stage-B sampling); `target_population_contract`
  (recalibrated literals, recomputed H1/H2 within 1e-12 + column
  normalization); `dev_population_exact` (384 VAL frames / 98304 pairs /
  256 rows per frame / pair indices / symbol range);
  `blocks_exact_with_declared_remainder` (three exact VAL DEV ranges per arm
  in block-major slot order + never-used VAL remainder 169 frames /
  43264 pairs, counted from the pool but never decoded);
  `nine_records_exact`; `genie_calls_exact` (Stage-A 16 derivation calls in
  the freeze + Stage-B 0 sampling calls);
  `sc_calls_exact` (derived 15); `tags_exact` (derived 9);
  `orders_valid_k_prefixes_within_registered_arms` (F0 old-order prefixes +
  F1 new-L1-prefix/old-L2 pins + F1 zero-Δ ordering triple);
  `oracle_isolation`; `buckets_disjoint_exhaustive` (unique arm/block +
  schema); `undetected_zero`; `nonfinite_zero`; `truth_isolation`;
  `disclosure_recount_exact`; `one_open_per_protected_input` (counts 0 + DEV
  1); `input_stat_unchanged`; `no_unregistered_access`;
  `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (injected tests + implementation-freeze; authorized separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_<l1_order files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20l/<uuid>/`
  temp root; protected-open audit declared separately (counts 0 + DEV 0 at
  Stage-A close). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A prior check (read-only, zero protected opens): verify the P20H
  `calibrated_prior.npz` canonical digest equals
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b` via the
  frozen `canonical_prior_digest` function (worktree-file read only; never a
  counts open). Stage A additionally greps the new master/test/TRAIN seeds
  absent elsewhere and pins the order-derivation program callsite inventory
  (§12) with L1-only/K-frozen/L2-frozen evidence.
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A
  freeze; NOT AUTHORIZED until independent Pre-EXECUTE PASS + pasted Stage-B
  authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l1_order_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames <FROZEN_AT_STAGE_A> --block-frames 128 --remainder-frames <FROZEN_AT_STAGE_A> --tag-master 2026092260 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M/new_l1_order_1p5m.json --order-digest <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M/l1_order_1p5m
```
  Frozen order-file mechanism (P20L-R1delta, exactly one, no alternative):
  Stage B takes the Stage-A frozen order file ONLY via `--order-file`
  (path above, read-only) gated by `--order-digest` equality against the
  freeze-pinned sha256 of the file bytes; mismatch BLOCKS before any SC call.
  There is NO `--train-seeds` flag and NO sampling code path in Stage B —
  pure 16-flag DEV scoring. TRAIN seeds (expected 2271..2274) live ONLY as
  Stage-A derivation provenance in the freeze, never as Stage-B argv.
  All flags required, no production default; three hardcoded arms with the
  L1-order swap pinned (never CLI-tunable: F1 = new-L1-prefix/old-L2 at same
  K); Stage-B prior path MUST equal the §3 frozen digest. Stage A confirms
  the module path (thin runner reusing P18 loading/block formation + P16/P13
  L1-genie helpers read-only; new P20L tag domains; septuple gate; Stage-A
  frozen order file + order-digest gate with zero Stage-B sampling) or freezes a written equivalent with justification;
  Stage A also freezes the exact `--dev-frames` / `--remainder-frames` /
  `--order-digest` values (expected `1660 2043` / `2044 2212` /
  order-file sha256) plus the TRAIN-seed derivation provenance
  (expected `2026092271 2026092272 2026092273 2026092274`) and the `--source`
  vocabulary (only `1p5M`). Forbidden by default: `longrun_*`,
  `minrerun_*`, `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data,
  full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git
  show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: thin runner + focused injected tests + Stage-A synthetic-only
  order derivation (16 L1-only TRAIN genie calls from the frozen prior under
  frozen TRAIN seeds, zero protected reads, zero DEV contact) producing the
  frozen order file `new_l1_order_1p5m.json` (§9 identity) + Stage-A freeze +
  implementation notes (exact files, diffs, test commands/results, frozen
  prior/program/seeds/population/cap/command/budget/order-file digest).
  Protected content opens
  0 at Stage-A close (counts 0 + DEV 0; prior digest check is a worktree-file
  read; TRAIN seeds are integers, not data; synthetic sampling consumes only
  the worktree prior file).
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md`
  (+ freeze, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`,
  `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec P20L delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20l/spec.md`
  + `tasks.md` P20L section (same umbrella change as
  P18/P19/P20A/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K; no new top-level change).
  The umbrella `spec.md` does not yet exist at this revision; Stage A drafts
  it carrying the P20L-R1delta semantics (Stage-A order derivation + frozen
  order file + Stage-B zero-sampling digest-gated use).

## 12. Allowed work

- New thin L1-order runner + focused injected tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest function + formula pins only),
  `plus1024_per_session_confirmation.py` (gate/population pattern reference),
  `l1_disclosure_1p5m.py`, `l1_dose_escalation_1p5m.py`,
  `l1_dose_512_1p5m.py` (gate/population/cap pattern references),
  P13/P16 empirical-genie L1 procedure (`construction.py` L1 path as called)
  (+ `prior.py`, `sc.py` contracts as called).
- Read-only load of the P20H `calibrated_prior.npz` (digest-pinned; never
  refit/resmoothed) + synthetic TRAIN sampling from it under frozen seeds
  IN STAGE A ONLY to produce the frozen order file `new_l1_order_1p5m.json`
  (§§2/9; zero protected reads, zero DEV contact, P20L-R1delta).
- P20L OpenSpec delta + packet docs + Stage-A freeze/return/review files +
  Stage-B evidence root (root only after Stage-B authorization) + the frozen
  order file `new_l1_order_1p5m.json` (Stage-A product, §9 identity).

## 13. Forbidden work

- Any NPZ/parquet content open or stat of 1.5M DEV/VAL/HOLD, any 1M split, or
  reserved 2M in Stage A (Stage-A protected opens 0); any counts NPZ open,
  prior refit/resmoothing/relambda/λ change, K reselection, L2-order change,
  or derivation on real DEV/VAL/HOLD/TRAIN-remainder frames at any stage; any
  decoder execution before Pre-EXECUTE PASS + pasted Stage-B authorization.
- Any change to GF32/transform/SC arithmetic, floor value, the frozen P16 L2
  order, tag scheme semantics, outcome precedence, accepted evidence roots,
  P20H calibration product, λ, or `src/` + `experiments/` + `tools/` frozen
  baseline.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the
  consumed 1M pool (any split/subrange), any consumed 1.5M TRAIN DEV
  (0..1535), TRAIN remainder 1536..1659, VAL remainder 2044..2212, HOLD, or the
  reserved 2M file; no second factor (disclosure tier, alternative
  construction, bounded search) inside this packet; no efficiency tuning; no
  new-block peeking before the authorized attempt; no calibration on DEV/VAL.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push; no self-acceptance; no P20D scope creep; no P20H/P20I/P20J/P20K
  rerun under this packet.

## 14. Acceptance IDs

- `P20L-R1`: prior reuse frozen read-only (§3 digest/lambda/floor/key-set
  pins; zero new calibration opens; V25 NPZ never opened; no refit/λ path in
  runner); §3 reuse evidenced at Pre-EXECUTE. Reuse-gate BLOCKED → planner
  rework, never a Stage-B fallback.
- `P20L-R2`: order-derivation program/input/seeds frozen L1-only/K-frozen/
  L2-frozen with DEV-zero-contact (program pin + prior-digest input pin +
  TRAIN-seed pins + Stage-A frozen order-file digest + old-order对照 with
  difference degree / overlap coordinates / P16-L1 digest pin; Stage-B
  order-digest gate equality, zero Stage-B sampling); closed/consumed blocks
  select nothing; consumed 1M pool excluded by source-tagged cross-file gate;
  all consumed 1.5M TRAIN DEV + TRAIN remainder excluded; VAL DEV 1660..2043
  (3 blocks 1660..1787/1788..1915/1916..2043, VAL remainder 2044..2212 never
  used) digest-pinned, septuple-gated + order-freeze-gated,
  Pre-EXECUTE-approved; reserved 2M untouched (never opened/statted/listed).
- `P20L-R3`: disclosure caps preregistered per arm (34119 / 34119 / 32524 +
  327743 public), keyΔ F1-vs-F0 exactly 0, ratios-vs-raw shown (~10.41%),
  recount mismatch 0; CE ratios never called efficiency.
- `P20L-R4`: L1-order swap + L1-only/K-frozen/L2-frozen rules frozen before
  execution, unchanged after; P16 construction/L2-order/K migration pinned; no
  tag-guided selection, no evidence reuse, no post-hoc re-picking, no
  re-derivation.
- `P20L-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9;
  `undetected` isolated; oracle arm never operational; first-error
  coordinate/layer rows complete per record.
- `P20L-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning;
  split-counted reads (counts 0/0 + DEV 1/1 + HOLD 0/1); resource aborts via
  P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20L-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded (Pre-EXECUTE
  explicitly adjudicates §3 reuse + §4 septuple gate + §2 order-freeze design);
  main-thread acceptance owns the label; descriptive-only, no
  FER/qualification/promotion language; branch reading (§16) stays planning
  input, never an in-packet verdict; STATUS notes truthful at every gate
  (stale-copy BLOCKS).
- `P20L-R8`: Stage-A suites green on injected data with zero protected opens
  audit (counts 0 + DEV 0 at Stage-A close; 2M non-access); no commit/push;
  frozen dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs
`P20L-R1..R8` (stage-appropriately) complete with changed files + exact
commands/results + artifact inventory + split open audit (counts + DEV + HOLD
separately); or (b) a concrete blocker with failing command, exact
error/traceback, attempted remedies, and the ONE decision needed from the main
thread. "Still incomplete" is not a completion report. The operator never marks
its own work accepted and never authorizes Stage B.

## 16. Deferred options (not in this packet)

- F1-restoration → maintain-confirmation round (deferred): trigger = at least
  one block with F0 fail → F1 exact on the new VAL segment (genuine
  order-restoration event, not maintain-only). Then a LATER packet may
  preregister a maintain confirmation on further new data (VAL remainder
  2044..2212 recheck first — only 169 frames = one full block + 41-frame
  stub, so a one-block micro-confirmation at most; reserved 2M first-use with
  per-session calibration + frozen new order + new tags is the candidate
  confirmation population but NOT pre-authorized here). This packet performs
  no follow-up confirmation and licenses no reliability claim.
- F1-zero-restoration all-L1 → bounded-search diagnostic (deferred (c)):
  trigger = genuine order-negative under the frozen prior + frozen same-budget
  swap — F0 failures occur on new-segment VAL blocks but F1 restores NONE
  with operational first errors remaining L1-layer. Only THEN is the
  same-budget order factor falsified as a fix, and only then does the L1-side
  1.5M bounded-search packet (fixed new-order disclosure/construction/prior,
  rescore-only `P20B-NBHD-1`-class neighborhood, one coherent NLL model, no
  tag-guided selection) become the next single factor on further new data.
  P20L alone decides nothing about search; search is never auto-triggered
  inside this packet.
- L2-implication → P20D candidate (deferred (a)): trigger = EITHER new-order
  oracle non-exact (F2 fails at base K2 — true-L1-conditioned L2 insufficiency
  under the new order, the first genuine L2-construction evidence on 1.5M) OR
  bottleneck-layer move (operational first errors become L2-layer under F1)
  with search-positive-but-unrestored pattern at the next search packet. Until
  such L2-side evidence exists, P20D stays deferred; F1-zero-restoration under
  all-L1 first errors SHALL NOT trigger P20D (semantic offset, frozen since
  P20H/P20I/P20J/P20K).
- Prior-form/λ work (deferred): trigger = F1-zero-restoration all-L1 (order
  also falsified → next upstream single factor is prior/model structure: λ,
  smoothing form, floor, or per-coordinate model — exactly one per packet).
  The 2026-09-19 λ critique is recorded as the motivating observation, not as
  an in-packet change.
- Maintain-only (F0 exact somewhere and F1 exact wherever F0 exact, zero
  fail→exact events) → further planning (deferred): neither restoration nor
  negative; main thread re-evaluates (order maintain-confirmation vs search vs
  prior-form vs P20D) with the full chain evidence in hand. This packet
  prejudges none of them.
- Disclosure-minimality probe, efficiency optimization, second independent
  session on reserved 2M: ALL continue deferred, re-evaluated against P20L
  accepted evidence after acceptance.
- 2M stays PRISTINE under this packet — never opened, never statted, never
  listed — as the follow-up confirmation population. Any 2M packet needs its
  own freeze, tag domain, and reviews.
