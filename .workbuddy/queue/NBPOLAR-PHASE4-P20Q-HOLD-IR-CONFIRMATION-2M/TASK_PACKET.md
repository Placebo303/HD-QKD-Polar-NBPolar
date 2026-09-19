# Phase 4-P20Q — Instrumented α1 confirmation on 2M HOLD with mandatory H2 IR-1..IR-5 (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage-A implementation freeze with ZERO protected reads, Stage-B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read, decoder execution, or commit/push is authorized by this file.
- Predecessor: `NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION` terminal
  `TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (Stage-B single attempt SPENT 1/1; counts 1/1 for the 2M array ONLY; VAL-DEV open 1/1
  SPENT on 2M VAL 2187..2826; 20/20 records; A 0/5 / B 2/5 (b1, b2 exact) / C 0/5 / D 3/5;
  b_restored 2 descriptive, d_restored 3 diagnostic; 11 L2-fail records all
  natural-in-prefix but U-domain-out; undetected 0; SC 30/30; tags 20/20; recount 0;
  key 692580 / public 6554860; integrity 29/29; Pre-RESULT PASS; acceptance in
  `MAIN_THREAD_ACCEPTANCE.md`). Frozen reuse pins: 2M prior canonical digest
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`, orders sha
  `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`, alt-L2 table sha
  `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`,
  K1=334/K2=6746/K_total=7080, session H1/H2/H
  0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477.
- H2 adjudication: X10 probe `NBPOLAR-X10-H2-SCALAR-ADJUDICATION` reviewed PASS
  (`workspace/probes/nbpolar_x10_h2_scalar_adjudication/results.json`): H2a (average
  metric quality orders arms) REFUTED; H2b fail-position hazard elevated (median ratio
  2.246, n=25); H2c failures concentrate in the X-prefix (P20O 11/11 additionally
  out-of-U); H2d floor flat; H2e static order geometry NOT-DECIDABLE → instrumentation
  requirements IR-1..IR-5 (all bounded/size-capped/recording-only/truth-isolation-safe).
- User decision (2026-09-19): the next packet is `NBPOLAR-PHASE4-P20Q-...` — an instrumented
  α1 confirmation run on the 2M HOLD segment, reusing ALL P20O frozen artifacts (no new
  derivation, NO new counts read), with IR-1..IR-5 mandatory (freeze IR-5 as PRESENT, capped).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 and
  `docs/nbpolar/ROADMAP.md`.
- Gate discipline: any standing long-horizon authorization does NOT collapse Tier-Y gates.
  Stage A and Stage B each need their own explicit pasted authorization text; this packet
  authorizes neither.
- Selected session: `type2_2M_20260121_183657` (2M), scoring population first-use of 2M HOLD
  (see §4). The 1M pool, the entire 1.5M session, 2M TRAIN-as-DEV, and 2M VAL (DEV +
  remainder, both consumed) are fail-closed against P20Q DEV selection (see §4).

## 0. Planner header (OpenSpec workflow)

- **Goal**: Confirm ONE frozen construction — `ALT-L2-LAPLACE-α1` — at the frozen
  per-session disclosure on FIRST-USE 2M HOLD blocks at N=32768 (four arms A/B/C/D,
  new P20Q tag domain, nine carried X09-R1/P20O scalars + mandatory IR-1..IR-5 payload),
  reusing ALL P20O frozen artifacts byte-identical (no new derivation, no new counts read),
  and record the H2 decision quantities the IR fields must supply. Decide descriptively
  whether B maintains exact blocks where A is exact and whether any A-fail→B-exact
  restoration re-appears on the third 2M segment — operationally (B vs A) and under
  true-L1 conditioning (D vs C).
- **Non-Goals**: No new factor (same construction/prior/orders/K; arms exactly as P20O);
  no new derivation (no counts open at any stage); no K/order hand-fill or cross-session
  carry (all P20O-derived 2M artifacts reused read-only — S2-i satisfied by reuse, S2-ii
  by HOLD∩TRAIN disjointness); no λ anywhere; no floor-value change; no SCL/new
  kernel/model/schema; no FER/reliability/qualification/promotion claim; no H2 decision
  inside this packet (H2 stays main-thread analysis after acceptance); no reuse of any
  consumed/closed range (1M pool, all 1.5M TRAIN/VAL/HOLD, 2M TRAIN 0..2186 as DEV,
  2M VAL 2187..2915 incl. consumed DEV 2187..2826 + remainder 2827..2915); no 2M TRAIN-as-DEV
  or 2M VAL use; no closure of the 1M-HOLD thread; no efficiency tuning.
- **Impact Scope**: New thin runner + focused injected tests + P20Q OpenSpec delta
  (`specs/nbpolar-phase4-p20q/spec.md` + `tasks.md` P20Q section, same umbrella change
  `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A freeze (`P20Q_FREEZE.md`) +
  implementation notes + Stage-B evidence root. No change to `src/`, `experiments/`,
  `tools/`, P16 construction file, P12–P20O accepted roots (`raw_prior_2m.npz`,
  `raw_prior_orders_2m.json`, `alt_l2_tables_2m.npz`, `raw_prior_1p5m` family,
  `l2_alt_hold_1p5m/`, `l2_alt_maintain_2m/`), X08/X09/X10 probe roots, or `results/` /
  `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20Q-R1..R9 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance. Descriptive-only label;
  `undetected` isolated; oracles never operational; H2 decision explicitly deferred to
  main-thread analysis after acceptance.
- **Tasks**: (planner task list for coder agents) H1 verify + freeze P20O artifact reuse
  (§3, R1); H2 freeze HOLD population/gates (§4, R2); H3 freeze replayed caps from the
  carried point (§5, R3); H4 freeze single-factor arm pins (§2/§6, R4); H5 wire
  endpoints/taxonomy + mandatory nine scalars + IR-1..IR-5 incl. IR-3 thresholds (§7, R5);
  H6 enforce one-shot budget/stop (§8, R6); H7 Stage-A suites green with zero-open audit
  (R8); H8 independent Pre-EXECUTE adjudication of reuse/alt/K-literal/population/IR
  boundary (R7); H9 single authorized Stage-B attempt (R6/R7); H10 independent Pre-RESULT
  + acceptance (H2 quantities checked present, never decided in-packet).
- **Honest scope** (binding on proposal/design/packet/return language): third-segment
  (2M HOLD) confirmation of the frozen α1 construction with the mandatory H2
  instrumentation; descriptive only; 2M HOLD is consumed by this packet; 1.5M VAL remainder
  stays untouched; no reliability/FER claim; the H2 decision is analysis, not a FER result.

## 1. Mission

With ZERO new derivation — the §3 P20O 2M TRAIN-derived raw prior + its session-derived
disclosure point + its session-derived worst-first orders + its α1 alt table, ALL reused
read-only with digest replay (S2-i satisfied by reuse, never carried across sessions) — and
everything else fixed (floor 1e-15, N=32768, greedy SC only, new P20Q tag domains only,
same K1/K2, same frozen order prefixes, disclosed sets byte-identical), zero further tuning:

> On FIRST-USE 2M HOLD blocks, does the alt-L2 operational arm (B) maintain exact
> wherever the incumbent-L2 operational arm (A) is exact at the frozen disclosure — and
> does any A-fail→B-exact restoration re-appear — with the hazard/coverage state AND the
> mandatory H2 IR-1..IR-5 payload recorded under each construction?

P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, P20K DEV 1152..1535 are CONSUMED;
P20M VAL DEV 1660..2043 CONSUMED; VAL remainder 2044..2212 RESERVED never-decoded under this
packet; P20N HOLD DEV 2213..2724 CONSUMED, HOLD remainder 2725..2766 never used; P20O 2M VAL
DEV 2187..2826 CONSUMED (1/1 SPENT), VAL remainder 2827..2915 never used; P20L never executed
(zero consumption). The ENTIRE 1M pool is fail-closed. All branches after this packet are
deferred to §16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- Operating-point route closed on 1.5M (P20M); construction route opened on 1.5M HOLD (P20N:
  B 1/4 vs A 0/4, all 14 failures L2-layer); maintain-confirmation replicated restoration on
  the independent 2M session (P20O VAL: A 0/5, B 2/5, C 0/5, D 3/5; b_restored 2 descriptive,
  d_restored 3 diagnostic; 11/11 L2 failures natural-in-prefix but U-domain-out). Scale:
  three events, three segments — no reliability claim. The live next branch is the
  third-segment HOLD confirmation with the H2 instrumentation the X10 probe mandates.
- X10 adjudication (reviewed PASS, frozen, not re-argued): H2a REFUTED (exact arms carry
  HIGHER prefix hazard means; e.g. P20N b3 gap 0.0971 bits, P20O b1/b2/b4 gaps
  0.0304/0.0431/0.0684 bits); H2b SUPPORTED (median fail/prefix ratio 2.246, n=25;
  strongest 10.342); H2c SUPPORTED (in-X 23/25; P20O 11 in-X with 11 out-of-U);
  H2d SUPPORTED-flat (mean |fail_nbhd_floor − prefix_floor| = 0.0030); H2e
  NOT-DECIDABLE (per-position series absent) → IR-1..IR-5 mandatory, all bounded,
  recording-only, truth-isolation-safe. The H2 DECISION itself is main-thread analysis
  AFTER P20Q acceptance, never an in-packet verdict and never a FER result.
- Reuse semantics (frozen, not re-argued): the scoring point was derived from the SCORING
  session's own TRAIN (P20O §3, S2-i). Re-deriving it in P20Q would cost a second counts
  open and a second sampling for zero new information; reusing the frozen P20O artifacts
  read-only with digest replay preserves S2-i (same-session hypotheses, never carried
  across sessions) and S2-ii (build ⊂ TRAIN vs DEV ⊂ HOLD disjointness, §4). The alt-L2
  RULE stays the confirmed single factor (α=1, frozen). Fixed disclosure means fixed
  WITHIN the packet after the Stage-A reuse freeze (B−A = 0, D−C = 0 by design).
- Alternatives rejected in writing: (a) re-derive prior/orders/alt in P20Q — second counts
  open + second sampling for identical inputs, forbidden; (b) any α other than 1, any
  second construction, any construction sweep — second factor, forbidden; (c) L2-order
  re-derivation under the alt prior — second factor (order+construction), forbidden;
  disclosed sets stay the frozen P20O 2M-derived prefixes on all arms; (d) λ-concentration
  retune — the X08-falsified operating point, forbidden; (e) floor change — H3 exonerated,
  forbidden as the factor; (f) K change or budget recompute from alt H — violates fixed
  disclosure; alt-H descriptive only (§3); (g) SCL/list/belief decoder — decoder change, out
  of scope; (h) consume 1.5M VAL remainder 2044..2212 (169 frames, one block + stub) or
  2M VAL remainder now — destroys reserved populations; both stay untouched (never decoded);
  (i) freeze any IR field as absent — X10 mandates all five PRESENT (user decision), forbidden.
- Session inventory (no new protected access by this planner; provenance from the split
  manifest `nbldpc_v25_split_manifest_v1` read as JSON metadata only, plus P20M/N/O §2/§4):
  2M TRAIN 2187 frames / 559872 pairs + VAL 729 / 186624 + HOLD 729 / 186624 (256 rows/frame;
  see §4 for frame bases). 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824.
  Geometric position: P20Q 2M-HOLD DEV is the FIRST 640 HOLD frames 2916..3555 (5 blocks of
  128); HOLD remainder 3556..3644 (89 frames / 22784 pairs) never used under this packet.
- Runner-delta design choice (frozen; the §10 "design.md" decision): a THIN NEW runner
  module importing the accepted `l2_alt_maintain_2m` runner read-only (which itself
  thin-imports accepted `raw_prior_val_1p5m`: VAL/HOLD population pattern, TRAIN-exclusion
  gate family, order-file + `--order-digest` mechanism with zero Stage-B sampling, P20A
  endpoint/taxonomy/recount/resource machinery, `_l2_hazard_diagnostics` code point with
  nine scalars). Exact delta list, nothing else: (d1) population → 2M HOLD DEV
  (§4; VAL-DEV/VAL-remainder excluded as consumed); (d2) prior/orders/alt sources → the
  P20O frozen files reused read-only behind replayed `reuse_prior_identity` +
  `reuse_alt_identity` + `reuse_order_freeze` gates (digests + lambda-0.0/alpha-1.0/floor
  pins + exact key sets + H-literal recomputation within 1e-12 + `p_b` cross-check +
  `p1`-equality recheck within 1e-12; worktree-file reads only, never the V25 counts NPZ);
  (d3) K pins → the P20O-derived (K_total,K1,K2)=(7080,334,6746) replayed as literals
  (never recomputed, never recarried; alt-H never a budget input); (d4) orders → the P20O
  frozen `raw_prior_orders_2m.json` via the reused order-file mechanism (byte-identical on
  all four arms; disclosed sets = first-K1 / first-K2 prefixes); (d5) arms A/B/C/D per §6
  (same K, same frozen order prefixes as P20O); (d6) new P20Q tag domain (§6);
  (d7) mandatory IR-1..IR-5 recorder extension (§7) computed post-decode alongside the nine
  carried scalars (recording-only, bounded, truth-isolation sentinel); (d8) 2M-HOLD
  population + DEV∩build-frames disjointness declared inside the TRAIN-exclusion gate (§4).
  No SC/transform/floor-semantics/tag-semantics change; no second factor. The alternative
  (edit any accepted module) is rejected: it would touch an accepted evidence-producing
  file; the thin importer leaves every accepted file byte-identical.

## 3. Reuse freeze (normative — P20O artifacts reused read-only, zero Stage-A protected reads)

- Counts source: NONE. Stage A performs ZERO protected opens (counts 0/0 at Stage-A close;
  the V25 counts NPZ is NEVER opened/statted/listed at any stage of this packet). The §3
  P20O derivation inputs are not re-read. FORBIDDEN reuse inputs: any 1M split, any 1.5M
  split, 2M DEV/VAL-remainder/HOLD frames for derivation, Model-F CAL artifact.
- Reused products (paths under the P20O queue dir, read-only; Stage A verifies by
  worktree-file digest recomputation ONLY — canonical recipe for the prior, file-bytes
  sha256 for orders/alt; zero parquet/NPZ protected opens):
  (p1) `raw_prior_2m.npz` — canonical digest
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587` (recipe
  `per_session_calibration.canonical_prior_digest`: sorted-key `key + shape + dtype +
  C-order bytes` sha256); keys exactly `counts_ab, f_raw, p1, p2, p_b, lambda_star,
  floor_value, h1, h2, h_total` (`lambda_star` `0.0`; `floor_value` `1e-15`); session H
  literals `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477` recomputed via
  accepted `target_construction.entropy_bits` within 1e-12 (never hand-filled;
  `beta_eff_empirical` never hand-filled per AGENTS.md §5.5); `p_b` cross-check pinned.
  (p2) `raw_prior_orders_2m.json` — file-bytes sha256
  `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; full L1+L2
  worst-first permutations, K1 334 / K2 6746 / K_total 7080.
  (p3) `alt_l2_tables_2m.npz` — file-bytes sha256
  `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`; keys exactly
  `counts_ab, f_alt, p1, p2_alt, alpha, floor_value, h1_inc, h2_alt, h_total_alt`
  (`alpha` `1.0`; `floor_value` `1e-15`); `p1` = the P20O 2M incumbent `p1` (Stage A
  asserts equality within 1e-12 elementwise); descriptive alt-H `1.3245794596410305 /
  1.3502415084837889` (never a budget input).
- Budget/split replay (S2-i satisfied by reuse): `K_total = 7080` via the literal
  `1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536]` (P20O §3 display,
  replayed never recomputed); `(K1,K2) = (334,6746)` replayed never recarried; NO
  recomputation from alt H; NO hand-fill; NO new sampling (Stage-A genie calls 0, Stage-B
  sampling 0).
- D1/D2 replay: D1 literals replayed from the P20O freeze (`ce_alt` 0.8850983725781965,
  `ce_incumbent` 0.8069006731253678, ceilings 33794/35464, `alt_ideal_length_bits`
  29002.90347264234); D2 `alt_construction_budget_feasibility` = FEASIBLE replayed (margin
  4791.09652735766). Stage A replays the arithmetic from worktree files BEFORE any HOLD
  contact; a replay mismatch BLOCKS before any HOLD open (HOLD read stays 0/1) and no
  Stage-B authorization is requested.
- Stage B loads the frozen files read-only behind the `reuse_prior_identity` +
  `reuse_alt_identity` + `reuse_order_freeze` gates (digests + lambda-0.0/alpha-1.0/floor
  pins + exact key sets + H-literal recomputation within 1e-12 + `p_b` cross-check +
  `p1`-equality recheck within 1e-12 + K-literal replay, or BLOCKED before any sampling
  and before any SC call).

## 4. Population and closed/consumed-data rule (normative)

- The following are CONSUMED/CLOSED and SHALL NOT supply P20Q blocks: the three P18/P19
  HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599), P20C/P20E/P20F DEV blocks
  (1M 0..383 / 384..767 / 768..1151, remainder 1152..1199 never used), P20H DEV (1.5M TRAIN
  0..383), P20I DEV (384..767), P20J DEV (768..1151), P20K DEV (1152..1535, remainder
  1536..1659), P20M VAL DEV (1.5M VAL 1660..2043), 1.5M VAL remainder 2044..2212 (RESERVED
  never-decoded under this packet), P20N HOLD DEV (1.5M HOLD 2213..2724), HOLD remainder
  2725..2766, P20O 2M TRAIN-build 0..2186 as DEV, P20O 2M VAL DEV 2187..2826 (CONSUMED 1/1),
  2M VAL remainder 2827..2915 (never decoded). The ENTIRE 1M pool and the ENTIRE 1.5M
  session are fail-closed against P20Q DEV selection (cross-file gate). 2M TRAIN 0..2186
  SHALL NOT supply P20Q blocks (build frames). 2M VAL 2187..2915 SHALL NOT be
  opened/statted/listed/read under this packet in any form.
- 2M-HOLD-first-use justification (same canonical TRAIN→held-out separation as P20M §4,
  frozen, not re-argued in Stage A/B): 2M HOLD has never been decoded, tuned on, or scored
  by any EXECUTED NB-Polar packet; 2M TRAIN supplies the session hypotheses (raw prior +
  alt table both from TRAIN-fitted counts, never from HOLD frames); using HOLD as a one-shot
  scoring population is declared once, consumed once, never tuned, never returned to a
  validation role. The 2M HOLD remainder stays undecoded.
- Stage B runs on the DECLARED population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet` ONLY (provenance pin frozen in Stage A by manifest cross-check; mismatch blocks; planner performed zero opens/stats/listings) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 2M TRAIN 2187/559872 + VAL 729/186624 + HOLD 729/186624 (JSON-metadata read only) |
| construction-derivation input | P20O §3 2M TRAIN counts (reused artifacts ONLY; never a HOLD frame) |
| HOLD DEV frame rule | FIRST 640 HOLD frames in (frame_id, pair_idx) order → frozen HOLD base 2916: `2916..3555` (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed; manifest-count arithmetic: TRAIN 2187 [0..2186] + VAL 729 [2187..2915] = HOLD base 2916, same arithmetic P20O used for TRAIN/VAL) |
| HOLD DEV blocks (N=32768) | `2916..3043`, `3044..3171`, `3172..3299`, `3300..3427`, `3428..3555` (5 × 128 frames; 163840 pairs) |
| unused remainder | HOLD frames `3556..3644` (89 frames / 22784 pairs) recorded never used — counted, never decoded |
| build-frames disjointness (S2-ii) | counts/build frames ⊂ 2M TRAIN `0..2186` (P20O §3 input = 2M TRAIN counts ONLY); DEV ⊂ 2M HOLD `2916..3555`; disjoint by split identity; declared frame sets above; the TRAIN-exclusion gate refuses any overlap before any protected content open |
| consumed-1M exclusions | entire 1M pool (any split/subrange) — overlap refuses before any protected content open |
| consumed-1.5M exclusions | all 1.5M TRAIN `0..1659` + VAL `1660..2212` + HOLD `2213..2766` — overlap refuses before any protected content open |
| consumed-2M exclusions | 2M TRAIN `0..2186` as DEV; 2M VAL `2187..2915` (incl. consumed DEV 2187..2826 + remainder 2827..2915) in any form |
| block count | 5 at N=32768 |
| tag domains | new P20Q domain (§6) |

- Fail-closed gate family (frozen in the runner, order (a)→(g), cross-file first):
  (a) CROSS-FILE — DEV content-open path + stat-size/sha pin must equal the 2M identity;
  any 1M or 1.5M path or digest mismatch refuses before any SC call (frame integers alone
  are never identity); (b) INTRA-FILE HOLD — DEV ranges must overlap NONE of 2M
  TRAIN-exterior/2M-VAL, and must lie wholly inside 2M HOLD 2916..3644, else refuse before
  any protected content open; (c) CONSUMED-1M EXCLUSION — entire 1M pool; (d) CONSUMED-1.5M
  EXCLUSION — all 1.5M ranges above; (e) CONSUMED-2M EXCLUSION — 2M TRAIN-as-DEV + 2M VAL
  (DEV + remainder) + DEV∩build-frames disjointness declaration: DEV ⊂ 2M-HOLD vs build ⊂
  2M-TRAIN with the frame sets above (S2-ii); (f) REUSE-PRIOR/ALT/ORDER/K-LITERAL — §3
  canonical/file-bytes digests + lambda-0.0/alpha-1.0/floor pins + exact key sets +
  H-literal recomputation within 1e-12 + `p_b` cross-check + `p1`-equality within 1e-12 +
  budget-literal replay (S2-i) + order-file digest must match, else refuse before any SC
  call; (g) HOLD_CONFIRMATION_IDENTITY + ORDER-FREEZE — the §6 construction quadruple +
  `--source 2M` vocabulary + P20Q tag-domain pins must match AND the P20O frozen order-file
  digest must match with K1/K2 literals replaying exactly, else refuse before any SC call.

## 5. Preregistered disclosure point (normative — P20O-session-derived, replayed at Stage A)

- K rule (S2-i satisfied by reuse): `(K_total,K1,K2)` = `(7080,334,6746)` (P20O Stage-A
  derived from the §3 2M session H via the §3 budget+split rules; replayed as literals in
  Stage A with the `1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536]`
  display; never carried as an absolute from 1.5M). NO recomputation from alt H (the §3
  alt-H literals are descriptive only); NO hand-fill; NO new sampling.
- Caps PREREGISTERED at Stage A from the carried point (rule `5*(K1+K2)+64`
  key-dependent bits/block, `10*32768+63 = 327743` public bits/tag, one 64-bit tag per
  record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_incumbent_L2_operational (control) | 334 | 6746 | 35464 = 5*7080+64 | 327743 |
| B_alt_L2_operational (candidate) | same K1 | same K2 | same as A (Δ vs A exactly 0) | 327743 |
| C_incumbent_L2_oracle (diagnostic) | 0 | 6746 | 33794 = 5*6746+64 | 327743 |
| D_alt_L2_oracle (diagnostic) | 0 | same K2 | same as C (Δ vs C exactly 0) | 327743 |

- Planned totals (replayed at Stage A from the carried integers): key-dependent
  `5*(2*(5*(K1+K2)+64)+2*(5*K2+64))` = 692580 bits; public `20*327743 = 6554860` bits.
  B-vs-A and D-vs-C key-bit deltas are exactly 0 (construction factor carries ZERO
  disclosure delta by design).
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate BLOCKS.
  Per-record fields pin the session point (`prior_source` raw/2M-reuse, `k1/k2/k_total`,
  `budget_literal_replayed`, `alt_digest`, `l1_order_digest`, `l2_order_digest`,
  `floor_hit_rate`).

## 6. Arms (frozen; P20O-session construction pair replayed per §§3/5, all else P20O-identical)

- `A_incumbent_L2_operational`: frozen greedy SC with the P20O 2M incumbent tables
  (2M raw prior + 2M-derived L1+L2 orders, carried session K1/K2) (operational control;
  2 SC + 1 P20Q-domain tag per block). Paired same-block control for B on the new HOLD segment.
- `B_alt_L2_operational`: frozen greedy SC with 2M incumbent `p1` + §3 2M `p2_alt`,
  SAME 2M-derived L1+L2 order prefixes (first-K1 / first-K2), SAME K1/K2 (operational; the
  single-factor candidate; 2 SC + 1 tag per block).
- `C_incumbent_L2_oracle`: true-L1-conditioned diagnostic with 2M incumbent `p2` at
  carried K2 (provenance ORACLE, deployable=false, excluded from every operational
  aggregate; never a correction result; 1 SC + 1 P20Q-domain tag per block).
- `D_alt_L2_oracle`: true-L1-conditioned diagnostic with 2M `p2_alt` at carried K2
  (provenance ORACLE, deployable=false, excluded from every operational aggregate; never a
  correction result; 1 SC + 1 P20Q-domain tag per block).
- No other arms. Block-major (A, B, C, D) per HOLD block; checkpoint after every (arm,
  block) record; 20 records total. P16 construction file unchanged (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` carried read-only);
  kernel/representation/transform/SC arithmetic unchanged; greedy SC only; no SCL/new
  kernel/model/schema. Stage A performs ZERO sampling; Stage B performs pure HOLD scoring
  (30 SC + 20 tags) with ZERO sampling — Stage-B TRAIN genie calls pinned at 0, Stage-A
  genie calls pinned at 0 (reuse needs no derivation sampling).
- Tag domain (new P20Q): master 2026092330, prefix `nbpolar-p20q-hold-ir-2m-seed`, seed
  string `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from ALL of
  P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K/P20M/P20N/P20O.
  Stage A verifies by repo grep that master 2026092330 and focused-test seeds
  `2026092331..2026092337` appear in no tracked file outside the P20Q runner/tests/packet/
  spec documents (planner pre-checked 202609233* absent relative to all frozen masters in
  tasks.md/P20O freeze; zero protected access).
- No derivation seeds (reuse; zero sampling at any stage). Disjointness holds by the grep
  rule above. Stage B takes NO derivation seeds and performs no sampling.
- L2 disclosed-set rule (single-factor guard): on ALL four arms the disclosed L2 set is the
  first-K2 positions of the SAME frozen 2M order file (digest-gated); the L1 set is the
  first-K1 of the SAME file. Positions are fixed by the frozen file, never selected on
  closed blocks, consumed ranges, or HOLD data.

## 7. Thresholds, endpoints, and mandatory instrumentation (descriptive only — P20M-style)

- Outcome label `TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE` iff ALL
  integrity gates (§9) hold — regardless of exact-count. Any exact count (including 0/20
  and partials) is COMPLETE when integrity holds.
- Choice + justification: P20M-style descriptive (no recovery/FER/Wilson threshold). This is
  the THIRD-segment test of the frozen alt construction at frozen disclosure with new
  mandatory instrumentation — there is no empirical basis for a maintenance or H2 threshold
  here. A 62/64-class gate would be an invented threshold, explicitly forbidden. Branch and
  H2 decisions belong to main-thread analysis AFTER acceptance (§16).
- NO recovery / FER / Wilson / superiority / qualification / promotion claim. Descriptive
  reading only, preregistered before execution: per-arm exact counts; `b_maintained_count`
  = blocks where B is exact; `b_restored_count` = blocks where A fails and B is exact; the
  A→B transition table (A-exact/B-exact, A-exact/B-fail, A-fail/B-exact, A-fail/B-fail); and
  the oracle pair C→D (`d_restored_count`, `d_maintained_count`) as diagnostic only.
  "Maintain" = B exact wherever A exact; "restore" = A fail → B exact. Any (or neither)
  counts as COMPLETE. The positive/negative branch decision and the H2 decision stay with
  the main thread after acceptance.
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`, `undetected` isolated
  (never success/FER), plus `decode_failed` / `nonfinite` / `resource_abort` via the P20A
  path. P20A four-endpoint separation (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` /
  `pair_exact`) per record. First-error coordinate/layer rows (natural block symbol index,
  settled X09-R1 D4) are the primary diagnostic signal. Per-record incumbent floor-hit
  fields (`floor_hits`, `floor_hit_rate`) complete per record (S2 reporting).
- Carried X09-R1/P20O instrumentation (ALL NINE per-record SCALARS, scalar fields intact):
  `l2_order_digest`, `l2_prefix_len` (= session K2 on every record, gated),
  `l2_fail_in_prefix`, `l2_fail_hazard_bits`, `l2_fail_nbhd_mean_bits` (frozen radius R=8
  window, clipped to the block), `l2_prefix_hazard_mean_bits`, `l2_fail_nbhd_floor_frac`,
  `l2_prefix_floor_frac`, `l2_fail_in_prefix_u_domain` (frozen PRESENT since P20O).
  Semantics identical to P20O §7 (true cells under the record's own arm table; failing fields
  null unless `first_error_layer == L2`; prefix-wide means on every completed record).
- Mandatory IR-1..IR-5 (ALL FROZEN PRESENT, bounded/size-capped/recording-only/post-decode/
  truth-isolation-safe; Stage A pins exact formulas with injected vectors; never post-hoc):
  - IR-1 per-record 64-bin log-spaced hazard histograms {prefix, outside} using true cells
    (~1 KB/record): fields `ir1_hist_edges_bits` (65 float64, log-spaced over hazard-bits,
    frozen formula), `ir1_hist_prefix_counts` (64 int), `ir1_hist_outside_counts` (64 int).
    Split by disclosed L2 prefix membership (X-domain, first-K2 of the frozen 2M L2 order);
    hazards = `-log2` arm-table mass at each position's true `(U1_cond, B, U2)` cell under
    the record's own arm table (`U1_cond` = hard-L1 candidate on A/B, true high on C/D).
    Every completed record (never null).
  - IR-2 hazard-rank percentile of the first-error coordinate (1 float): field
    `ir2_first_error_hazard_rank_pct` (float64 in [0,1], 1.0 = most hazardous; fraction of
    block positions with hazard <= fail-site hazard; null unless `first_error_layer == L2`
    with computable hazard, else null with frozen nullability).
  - IR-3 above-threshold prefix counts (≤3 scalars × ≤2 frozen thresholds): EXACTLY two
    thresholds, per-record deterministic, no tuning — `ir3_thresh_lo_bits` = 1.0 × record
    `l2_prefix_hazard_mean_bits`, `ir3_thresh_hi_bits` = 2.0 × record
    `l2_prefix_hazard_mean_bits` (frozen multipliers; justification: X10 median
    fail/prefix ratio 2.246 → 2.0× marks the elevated tail, 1.0× marks above-mean mass;
    deterministic per-record, frozen before the run, never fed back). Fields (6 scalars):
    `ir3_thresh_lo_bits`, `ir3_thresh_hi_bits`, `ir3_prefix_above_lo_count`,
    `ir3_prefix_above_lo_frac`, `ir3_prefix_above_hi_count`, `ir3_prefix_above_hi_frac`
    (prefix positions using true cells; every completed record, never null).
  - IR-4 top-k hazardous positions with ranks (k≤16, frozen k=16): fields `ir4_topk_coords`
    (16 int, natural block symbol indices), `ir4_topk_hazard_bits` (16 float),
    `ir4_topk_in_prefix` (16 bool/int, X-domain prefix flags), `ir4_topk_ranks` (16 int,
    1-based hazard ranks). Hazard-order listing only; error-coordinate join is post-hoc.
    Every completed record (never null; N=32768 always fills 16).
  - IR-5 capped per-position series (≤4096×2 float32 + truncation flag) as the escalation,
    FROZEN PRESENT: fields `ir5_series_hazard_bits` (≤4096 float32, first 4096 natural-order
    positions 0..4095 with true-cell hazards), `ir5_series_in_prefix` (≤4096 int/bool,
    X-domain prefix flags), `ir5_series_truncated` (bool; true at N=32768 since 32768 >
    4096), `ir5_series_total_len` (=32768). Recording-only dump of the frozen hazard table
    + masks; the decoder consumes only the frozen order as before. Every completed record.
  - Size envelope: IR-1 ~1 KB + IR-2 8 B + IR-3 6 scalars + IR-4 ≤16×4 scalars + IR-5
    ≤4096×2 float32 (~32 KB) + flags ≈ ≤35 KB/record; 20 records ≈ ≤700 KB. Bounded by the
    frozen caps; larger blocks truncate only via the IR-5 flag (no silent growth).
  - Writer code point (frozen): successor module `l2_alt_hold_ir_2m.py`, function
    `_ir_hazard_diagnostics(*, block, view, p2_arm, counts_arr, l2_order, k2, first_error,
    prefix_mean, ...)` — called post-decode (after tag scoring) from the successor's
    `_operational_record` / `_control_record` equivalents alongside the nine carried scalars
    (the P20O `_l2_hazard_diagnostics` code point is the carried-over callsite pattern).
  - Truth-isolation boundary (normative): block truth (high/low/bob) and the arm tables
    enter `_ir_hazard_diagnostics` for RECORDING ONLY after all SC calls for the record have
    completed; its outputs are written into the record dict and never passed to
    `run_operational_block`, `run_oracle_control_block`, `_decode_layer`, `build_p1_metrics`,
    `gather_p2_metrics`, or any disclosure/order decision. A focused truth-isolation
    sentinel test pins this boundary (mutating truth changes no metric/decision input).
- H2 decision quantities (pre-registered; the H2 DECISION stays main-thread analysis after
  acceptance — NO outcome asserted here): the IR payload tables the accepted run must supply
  are (i) per-record `ir2_first_error_hazard_rank_pct` distribution (median/spread over L2
  failures, split A vs B, C/D separately); (ii) IR-1 histogram summaries (prefix vs outside
  mass, tail shape per record); (iii) IR-3 above-threshold prefix mass (lo/hi counts/fracs
  per record vs exactness); (iv) IR-4 top-k prefix flags + ranks (X-prefix concentration,
  static-order geometry probe); (v) IR-5 capped series + truncation flags as the escalation
  if IR-1..IR-4 leave H2 undecided; plus the nine carried scalars for P20N/P20O continuity.
  These quantities inform H2a–H2e; they are not FER, not thresholds, not pass/fail verdicts.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized execution; no
  rerun, no seed change, no prior/budget/order/construction tuning after preregistration.
  Execution-error rerun only as a recorded repeat of the identical freeze, never as tuning.
  P20H–P20O spent attempts do NOT transfer (independent packet).
- Reads (split-counted): counts-calibration opens 0/0 at every stage (reuse; the V25 counts
  NPZ is never opened/statted/listed) + HOLD-DEV open 1/1 reserved for Stage B (parquet,
  consumed at first HOLD content open). VAL-DEV reads 0; VAL-remainder reads 0; 1M/1.5M reads
  0. Any reopen, new calibration/derivation, real-frame use for derivation, or HOLD refit is
  forbidden. Prior-file/alt-file/order-file loads are worktree-file reads, not protected opens.
- SC/tag/genie budget: Stage-A genie 0 + Stage-B pure HOLD 30 SC (5 blocks × (2+2+1+1)) +
  20 tags + 20 records with ZERO sampling at every stage (Stage-A sampling 0, Stage-B
  sampling 0); derived per-record recomputation must equal counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence + accounting; abort
  is BLOCKED, never success. Wall/RSS ceilings frozen in Stage-A freeze (P20O-class
  reference at the same 30-SC / 20-tag budget: external 215 s / ~651 MiB runner peak;
  P20Q plans the same 30-SC / 20-tag HOLD budget with the bounded IR payload; external
  timeout 1200 s + virtual/RSS caps 2 GiB + single thread frozen).
- Strategy stop rules binding: no tuning on closed blocks or the new HOLD DEV after the one
  shot; no reuse of consumed 1M pool (any split/subrange), any consumed 1.5M range, 2M TRAIN
  as DEV, 2M VAL (DEV + remainder), 2M HOLD remainder 3556..3644 beyond counting, or any
  other session; no third factor after inconclusive single-factor; no near-raw disclosure
  claim; no oracle-as-operational; no population-reliability inference from this single gate
  alone; no efficiency tuning inside this packet; no H2 verdict inside this packet.
- SCL entry gate UNCHANGED (unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B five files)

- Stage-A freeze pins (zero protected opens): reuse-artifact paths + canonical/file-bytes
  digest replays + H-literal recomputation + `p_b` cross-check + `p1`-equality recheck +
  floor-hit replays; K_total literal replay display + (K1,K2) integers + order-file digest
  replay; alt file-bytes digest replay + alpha/floor/key-set/`p1`-equality/alt-H replays;
  D1/D2 replay literals + outcome; exact module path + N-flag Stage-B command verbatim +
  population integers + caps + budgets + tag domain + P16 construction digest + IR-3
  threshold multipliers (1.0×/2.0×) + IR caps; recorded in `P20Q_FREEZE.md`. Stage-A
  product identities: NO new artifacts (reuse paths point at the P20O queue dir:
  `../NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz`,
  `raw_prior_orders_2m.json`, `alt_l2_tables_2m.npz`; digests pinned in the freeze).
- Stage-B root:
  `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m/`
  (exactly five files; per-(arm, block) checkpointing; pure HOLD scoring — zero sampling;
  one HOLD content open; no reopen/rerun). Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json` (P16 construction
  digest + reuse-prior digest-gate proof + reuse-alt digest-gate proof (file bytes sha256
  equals the frozen `--alt-digest`) + reuse-order digest-gate proof + K-literal replay +
  budget-literal replay + tag-domain pins + split manifest + HOLD DEV integers +
  DEV∩build-frames disjointness declaration with frame sets + IR-3 multiplier pins + IR cap
  pins), `per_block_arm_outcomes.jsonl` (20 records at completion, each carrying the nine
  scalars + IR-1..IR-5 payload with frozen nullability/caps), `aggregate_summary.json`
  (incl. the IR payload tables: rank-percentile distribution + histogram summaries +
  above-threshold mass + top-k concentration), `report.md`. Per-record §7 endpoints + first
  error coordinate/layer, zero-count hits, floor hits + floor-hit rate + log loss, true-H vs
  candidate-H L2 NLL, taxonomy, construction-point fields (`l2_construction`, `k1/k2/k_total`,
  `prior_digest`, `alt_digest`, `l1_order_digest`, `l2_order_digest`) + the NINE carried
  scalars + the IR-1..IR-5 fields (all PRESENT per the Stage-A freeze).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); genie call
  counts (Stage-A 0 + Stage-B 0) + SC counts (L1/L2 split) + tag counts exact; block
  SER/NLL; wall/RSS; `b_maintained_count` / `b_restored_count` / `d_restored_count` /
  `d_maintained_count` descriptive + the A→B transition table; per-arm floor-hit rate +
  per-arm prefix hazard means + IR payload tables reported.
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `reuse_prior_identity` (P20O npz canonical digest +
  lambda-0.0/floor pins + exact key set + H literals within 1e-12 + `p_b` cross-check,
  worktree-file only); `reuse_alt_identity` (file-bytes digest + alpha-1.0/floor pins +
  exact key set + `p1`-equality within 1e-12 + descriptive alt-H literals);
  `alt_construction_budget_feasibility_replayed` (P20O FEASIBLE replay required before
  Pre-EXECUTE; replay mismatch ends the packet at Stage A with HOLD untouched);
  `dev_split_manifest_identity`; `dev_block_range_identity` (§4 gate family (a)→(g):
  cross-file first, then intra-file HOLD-containment, then consumed-1M, consumed-1.5M,
  consumed-2M (TRAIN-as-DEV + VAL DEV + VAL remainder) exclusions incl. the DEV∩build-frames
  disjointness declaration, then reuse-prior + reuse-alt + order-freeze + K-literal +
  hold-confirmation-identity pins); `order_derivation_identity` (P20O program pin +
  order-file digest, Stage-B file-bytes digest equality replay-exact, zero Stage-B sampling);
  `k_literal_exact` + `budget_literal_replayed` (S2-i: f=1.3 literal replayed from the P20O
  freeze, never a carried absolute, never recomputed from alt-H); `target_population_contract`;
  `dev_population_exact` (640 HOLD frames / 163840 pairs / 256 rows per frame / pair indices /
  symbol range); `blocks_exact_with_declared_remainder` (five exact HOLD DEV ranges per arm
  in block-major slot order + never-used HOLD remainder 89 frames / 22784 pairs, counted from
  the pool but never decoded); `twenty_records_exact`; `genie_calls_exact` (Stage-A 0 +
  Stage-B 0); `sc_calls_exact` (derived 30); `tags_exact` (derived 20);
  `orders_valid_k_prefixes_within_registered_arms` (P20O-derived prefixes + construction
  quadruple); `hazard_instrumentation_complete` (all nine §7 scalars present with correct
  nullability on every completed record); `ir_payload_complete` (IR-1..IR-5 all PRESENT with
  frozen caps/nullability on every completed record: 64-bin histograms + rank percentile +
  two-threshold counts + top-16 + capped series with truncation flag); `floor_hit_rate_reported`;
  `oracle_isolation`; `buckets_disjoint_exhaustive` (unique arm/block + schema);
  `undetected_zero`; `nonfinite_zero`; `truth_isolation` (incl. the IR recorder sentinel);
  `disclosure_recount_exact`; `one_open_per_protected_input` (counts 0 + HOLD-DEV 1);
  `input_stat_unchanged`; `no_unregistered_access`; `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (implementation + injected tests + reuse-freeze; authorized separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_l2_alt_hold_ir_2m.py -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20q/<uuid>/` temp root;
  protected-open audit declared separately (counts 0 + HOLD-DEV 0 at Stage-A close). Safe
  smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A reuse verification (ZERO protected opens; worktree-file digest recomputation
  ONLY): recompute the P20O prior canonical digest + H literals + `p_b` + `p1`-equality +
  alt/ order file-bytes digests from the three P20O worktree files; replay K literals +
  D1/D2 literals; confirm the §4 HOLD frame integers against the split-manifest JSON
  metadata (no parquet/NPZ open/stat/listing); grep-verify the §6 tag/test-seed freshness.
  Template (pins filled in the freeze; all flags required, no production default):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_ir_2m --verify-reuse --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --k1 334 --k2 6746
```
  Stage A confirms the module path (thin importer of accepted `l2_alt_maintain_2m` per the
  §2 delta list d1–d8, or freezes a written equivalent with justification) and the
  `--source` vocabulary (only `2M`). Forbidden by default: `longrun_*`, `minrerun_*`,
  `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A freeze with the
  `<FROZEN_AT_STAGE_A>` pins filled; NOT AUTHORIZED until independent Pre-EXECUTE PASS +
  pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_ir_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest <FROZEN_AT_STAGE_A> --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest <FROZEN_AT_STAGE_A> --source 2M --floor 1e-15 --n 32768 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames 2916 3555 --block-frames 128 --remainder-frames 3556 3644 --tag-master 2026092330 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m
```
  All flags required, no production default; four hardcoded arms with the construction swap
  pinned (never CLI-tunable: A = 2M-incumbent-L2 at carried K; B = 2M-alt-L2 at carried K;
  C = 2M-incumbent oracle; D = 2M-alt oracle); Stage-B prior path MUST equal the §3 reuse
  pins; `--alpha` takes no Stage-B value (construction is frozen in the alt file). Stage A
  fills every `<FROZEN_AT_STAGE_A>` pin (`--prior-digest`, `--alt-digest`, `--k1/--k2`,
  `--order-digest`) with the §3 replayed values plus the `--source` vocabulary (only `2M`)
  and the IR-3 multiplier + IR-cap pins in `frozen_plan.json`. Forbidden by default as above.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git show HEAD:`
  blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: reuse-verification freeze (`P20Q_FREEZE.md`: §3 digest/H/`p_b`/`p1`-equality
  replays + K-literal replay + order digest replay + D1/D2 replay + population integers +
  caps + budgets + tag domain + IR-3 multipliers + IR caps + module path + both commands
  verbatim) + implementation notes (exact files, diffs, test commands/results, frozen
  reuse/population/cap/command, D1/D2 replay outcome) + thin runner + focused injected
  tests. NO new artifacts (reuse paths point at the P20O queue dir). Protected content
  opens 0 at Stage-A close (counts 0/0 + HOLD-DEV 0/1; zero sampling at every stage).
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md` (+ freeze,
  `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec P20Q delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20q/spec.md`
  + `tasks.md` P20Q section (same umbrella change as P18/P19/P20A/P20B/P20C/P20E/P20F/P20G/
  P20H/P20I/P20J/P20K/P20M/P20N/P20O; no new top-level change).

## 12. Allowed work

- New thin HOLD-IR runner (importer per §2 d1–d8) + focused injected tests (temporary roots
  only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py`, `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`,
  `raw_prior_val_1p5m.py` (gate/population/record-writer pattern references),
  `l2_alt_hold_1p5m.py` (construction-swap + instrumentation pattern reference),
  `l2_alt_maintain_2m.py` (import target; gate/population/record-writer/nine-scalar
  pattern references) (+ `construction.py` / `prior.py` / `sc.py` contracts as called).
- ZERO protected opens in Stage A: worktree-file digest recomputation of the §3 P20O
  artifacts + split-manifest JSON-metadata confirmation of the §4 HOLD integers +
  grep-verification of the §6 tag/test-seed freshness + closed-form IR formula pins on
  injected vectors (zero sampling, zero genie calls, zero real frames).
- P20Q OpenSpec delta + packet docs + Stage-A freeze/return/review files + Stage-B evidence
  root (root only after Stage-B authorization) + the §3 reuse identity (§§3/9).

## 13. Forbidden work

- Any NPZ/parquet content open or stat/listing of 2M HOLD-DEV/HOLD-remainder, 2M VAL
  (DEV/remainder), 2M TRAIN counts, any 1M split, or any 1.5M split in Stage A (Stage-A
  protected opens: counts 0/0, HOLD-DEV 0/1); any counts open at any stage; any K carried as
  an absolute from 1.5M or recomputed from alt-H (S2-i; replay only); any derivation or
  sampling on real DEV/VAL/HOLD frames at any stage; any decoder execution before
  Pre-EXECUTE PASS + pasted Stage-B authorization.
- Any change to GF32/transform/SC arithmetic, floor value, 2M L1 tables, 2M L1/L2 orders,
  disclosed sets, tag scheme semantics, outcome precedence, accepted evidence roots, P20O
  products, X08/X09/X10 probe roots, or `src/` + `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the consumed 1M
  pool (any split/subrange), any consumed 1.5M range (TRAIN 0..1659, VAL 1660..2212, HOLD
  2213..2766), 2M TRAIN as DEV, 2M VAL (DEV 2187..2826, remainder 2827..2915), or 2M HOLD
  remainder 3556..3644; no second construction, no construction sweep, no order
  re-derivation, no disclosure change, no efficiency tuning; no new-block peeking before the
  authorized attempt; no calibration on DEV/HOLD; no H2 verdict inside this packet.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push;
  no self-acceptance; no P20D scope creep beyond the single frozen construction; no
  P20H–P20O rerun under this packet.

## 14. Acceptance IDs

- `P20Q-R1`: P20O 2M reuse verified read-only from worktree files (canonical + file-bytes
  digests replay-exact; H literals within 1e-12; `p_b` cross-check; `p1`-equality within
  1e-12; exact key sets; lambda-0.0/alpha-1.0/floor pins; zero protected opens at every
  stage); reuse pins frozen at Stage A. Derivation-gate BLOCKED → planner rework, never a
  Stage-B fallback.
- `P20Q-R2`: budget/split/orders replayed 2M-session-derived (S2-i literal replay displayed
  from the P20O freeze; zero Stage-B sampling; zero Stage-A sampling); closed/consumed
  blocks select nothing; consumed 1M pool + entire 1.5M session + consumed 2M TRAIN-as-DEV +
  consumed 2M VAL (DEV + remainder) excluded by source-tagged cross-file gates; 2M HOLD DEV
  2916..3555 (5 blocks 2916..3043/3044..3171/3172..3299/3300..3427/3428..3555, HOLD remainder
  3556..3644 never used) gated + Pre-EXECUTE-approved; 1M/1.5M/2M-VAL untouched in every form.
- `P20Q-R3`: disclosure point preregistered per arm from the carried integers (A/B
  `5*(K1+K2)+64` with Δ exactly 0; C/D `5*K2+64` with Δ exactly 0; 327743 public; totals
  692580/6554860 frozen at Stage A), recount mismatch 0; CE ratios never called efficiency.
- `P20Q-R4`: single-factor construction replay (A 2M-incumbent-control pins + B 2M-alt-
  candidate pins + shared-prefix rule + C/D oracle pair, §3 α=1 rule replayed,
  `p1`-equality within 1e-12) frozen before execution, unchanged after; P16 construction
  migration pinned; no tag-guided selection, no evidence reuse, no post-hoc re-picking, no
  re-derivation.
- `P20Q-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9; `undetected`
  isolated; oracle arms never operational; first-error coordinate/layer rows + per-record
  floor-hit fields + all nine carried scalars complete per record with correct nullability
  + IR-1..IR-5 ALL PRESENT with frozen caps/nullability on every completed record (IR-3
  two thresholds 1.0×/2.0× prefix-mean; IR-4 k=16; IR-5 capped 4096 + truncation flag);
  instrumentation + IR recorded-only (truth-isolation sentinel green).
- `P20Q-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning; split-counted
  reads (counts 0/0 + HOLD-DEV 1/1 + VAL-DEV 0 + VAL-remainder 0 + 1M/1.5M 0); resource
  aborts via P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20Q-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded (Pre-EXECUTE explicitly
  adjudicates §3 reuse/alt replay + D2 replay outcome + §5 budget/K-literal replay + §4 gate
  family + §2 runner-delta design + §7 nine-scalar + IR-1..IR-5 boundary incl. IR-3
  thresholds and IR-5 cap); main-thread acceptance owns the label; descriptive-only, no
  FER/qualification/promotion/H2-verdict language; branch + H2 reading (§16) stays planning
  input, never an in-packet verdict; honest-scope statement (§0) repeated verbatim in the return.
- `P20Q-R8`: Stage-A suites green on injected data with the zero-protected-open audit
  (counts 0/0 + HOLD-DEV 0/1 at Stage-A close; 1M/1.5M/2M-VAL non-access in every form);
  no commit/push; frozen dirs byte-untouched except the §12 manifest.
- `P20Q-R9`: D1/D2 replay (TRAIN-only literals replayed from the P20O freeze, zero HOLD
  reads; replay outcome frozen in `P20Q_FREEZE.md`/STATUS BEFORE any HOLD contact;
  MISMATCH → HOLD untouched, no Stage-B request, point recorded blocked-by-replay;
  FEASIBLE-replay → literals frozen, packet proceeds). Gate-fired-by-replay → main-thread
  re-frame, never a Stage-B fallback.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs `P20Q-R1..R9`
(stage-appropriately) complete with changed files + exact commands/results + artifact
inventory (incl. all three reuse digest replays) + split open audit (counts + HOLD-DEV +
VAL-DEV + VAL-remainder + 1M/1.5M separately); or (b) a concrete blocker with failing
command, exact error/traceback, attempted remedies, and the ONE decision needed from the
main thread. "Still incomplete" is not a completion report. The operator never marks its
own work accepted and never authorizes Stage B.

## 16. Deferred options (not in this packet)

- B-maintained (B exact wherever A exact, with or without an additional A-fail→B-exact event)
  → efficiency/disclosure-minimality planning (deferred): trigger = genuine 2M-HOLD maintain
  event under the frozen construction at frozen disclosure with the IR payload complete.
  Main thread re-evaluates with the full chain evidence in hand. This packet prejudges none
  of it and licenses no reliability claim.
- B-zero-maintain with L2-layer persistence → next upstream single factor (deferred):
  trigger = genuine alt-construction negative on the third segment — B maintains NONE and
  restores NONE with operational first errors remaining L2-layer (and D maintains/restores
  NONE under true L1). Only THEN is the Laplace-α1 L2 form falsified as the fix on a third
  segment, and only then does exactly ONE of (L2-order positions under the raw prior /
  L2-side bounded search at the fixed point / second single construction form) become the
  next single factor on further new data by main-thread planning. Nothing is auto-triggered
  inside this packet.
- B-zero-maintain with L1-layer return → prior/L1-side re-evaluation (deferred): trigger =
  operational first errors returning to L1-layer under the alt L2 on 2M HOLD (L1-side
  regression signal, not an L2 win). Main thread re-evaluates with the full chain evidence
  in hand.
- H2 adjudication → main-thread analysis AFTER P20Q acceptance (deferred, never in-packet):
  trigger = accepted P20Q IR-1..IR-5 payload tables (§7) joined with the P20N/P20O nine-scalar
  archive. The H2a–H2e verdicts belong to that analysis; this packet supplies the
  pre-registered quantities and licenses no H2 verdict, no FER reading, and no threshold.
- Disclosure-minimality probe, efficiency optimization, closure of the 1M-HOLD thread, any
  further 2M use beyond the HOLD remainder: ALL continue deferred / out of scope,
  re-evaluated against P20Q accepted evidence after acceptance.
- 2M HOLD remainder 3556..3644 stays never-decoded and 1.5M VAL remainder 2044..2212 stays
  never-decoded under this packet as follow-up populations. Any follow-up packet needs its
  own freeze, tag domain, and reviews. 2M HOLD DEV 2916..3555 is CONSUMED by this packet
  regardless of outcome.

(End of file)
