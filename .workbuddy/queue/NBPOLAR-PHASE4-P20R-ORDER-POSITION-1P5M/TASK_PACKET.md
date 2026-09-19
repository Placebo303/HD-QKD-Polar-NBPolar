# Phase 4-P20R — Single-factor L2-order-position packet on 1.5M VAL remainder (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage-A implementation + new-order freeze with ZERO protected reads, Stage-B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read, decoder execution, or commit/push is authorized by this file.
- Predecessor: `NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M` terminal
  `TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (Stage-B single attempt SPENT 1/1; counts 0/0; HOLD-DEV 1/1 SPENT on 2M HOLD
  2916..3555; 20/20 records; A 0/5 / B 4/5 (b_restored 4 descriptive) / C 0/5 /
  D 4/5 (d_restored 4 diagnostic); 12 L2-fail records all natural-in-prefix but
  U-domain-out; undetected 0; SC 30/30; tags 20/20; recount 0; key 692580 /
  public 6554860; integrity 30/30; Pre-RESULT PASS; acceptance in
  `MAIN_THREAD_ACCEPTANCE.md`). P20Q §16 auto-triggers did NOT fire (no
  maintain event, no L1-return, no H2 verdict in-packet); the held-open
  item-4 branch decision is served by H2 analysis + this proposal.
- H2 predecessor evidence (read-only, no verdict in this packet):
  `workspace/h2/504e036a-f040-4d88-88ba-152702f92ffd/h2_final_adjudication.md`
  (main-thread T8, descriptive only): H2a REFUTED (8/14 evaluable blocks
  anomalous, strongest gap 0.097058 on P20N b3); H2b SUPPORTED (median
  fail/prefix ratio 2.2835, n=37); H2c SUPPORTED (in-X 35/37 = 0.9459;
  out-of-U 23/23 on 2M segments); H2d SUPPORTED-flat (mean_abs_diff 0.002185);
  H2e REFUTED-geometry-incoherent (IR-4 pooled in-prefix 66/320 = 0.20625 <
  0.50 with IR-2 median 0.883041 ≥ 0.50, truncated scope first-4096 + top-16 +
  histogram). Decision-log H2 entry + X10 probe
  `NBPOLAR-X10-H2-SCALAR-ADJUDICATION` (reviewed PASS) are the frozen
  instrumentation basis. This packet decides nothing about H2; it supplies the
  next single-factor position-set observation.
- Proposal predecessor: `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-PROPOSAL.md`
  (DRAFT, §1(a) favored as next, §§2–4 single-factor recommendation + population
  sketch + stop rules). This packet freezes that recommendation; the proposal
  itself authorizes nothing.
- User decisions (2026-09-19, frozen, not re-asked):
  (1) population = single-block 1.5M VAL-remainder DEV 2044..2171 (128 frames →
  ONE N=32768 block; stub 2172..2212 + 2M HOLD remainder 3556..3644 stay
  never-decoded);
  (2) full instrumentation (nine scalars + IR-1..IR-5 all PRESENT, same
  caps/formulas as P20Q §7);
  (3) pure order delta — arm A = α1 construction + FROZEN 1.5M order (P20N order
  `a9f18a9f…638`), arm B = α1 + NEW L2-order positions derived from the REUSED
  1.5M raw prior (P20M TRAIN-derived artifacts, worktree-file only, zero
  protected derivation reads); C/D oracle pair mirrors A/B under true-L1
  (diagnostic only).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 and
  `docs/nbpolar/ROADMAP.md`.
- Gate discipline: any standing long-horizon authorization does NOT collapse
  Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_1p5M_20260121_183806` (1.5M), scoring population
  first-use of the 1.5M VAL remainder (see §4). The 2M session is fail-closed
  against P20R DEV selection except the counted-never-decoded HOLD remainder
  (see §4).

## 0. Planner header (OpenSpec workflow)

- **Goal**: Test exactly ONE factor — L2 disclosed-position SET (order) under the
  raw prior — at frozen α1 construction, frozen per-session disclosure
  (K1=331/K2=6689/K_total=7020 replayed from the 1.5M session point), frozen
  floor 1e-15, greedy SC only, on ONE first-use 1.5M VAL-remainder block at
  N=32768 (four arms A/B/C/D, new P20R tag domain, nine carried X09-R1/P20O/P20Q
  scalars + mandatory IR-1..IR-5 payload all PRESENT), reusing the frozen 1.5M
  raw prior + α1 alt table read-only with digest replay and computing the ONE
  alternate L2-order permutation off-protected-data from the reused worktree
  prior by the frozen program with zero sampling. Decide descriptively whether
  the A-fail→B-exact restoration pattern re-appears under a changed position
  set at identical K sizes — operationally (B vs A) and under true-L1
  conditioning (D vs C, diagnostic only).
- **Non-Goals**: No new construction factor (α1 frozen on all arms); no
  K/disclosure-size change (B−A = 0, D−C = 0 by design); no floor-value change;
  no SCL/new kernel/model/schema; no bounded search or second construction
  form; no K carried as an absolute from 2M or recomputed from alt-H; no
  derivation or sampling on real DEV/VAL/HOLD frames at any stage; no
  calibration on DEV; no reuse of any consumed/closed range (full ledger §4);
  no cross-session pooling (1.5M and 2M never mixed); no full-block order claims
  beyond recorded scope; no H2 verdict inside this packet (H2 stays
  main-thread analysis after acceptance); no overwrite under `results/` or
  `comparison_bench/outputs_comparison/`; no commit/push.
- **Impact Scope**: New thin runner + focused injected tests + P20R OpenSpec
  delta (`specs/nbpolar-phase4-p20r/spec.md` + `tasks.md` P20R section, same
  umbrella change `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A freeze
  (`P20R_FREEZE.md`, incl. new-order artifact + dual digests + derivation-program
  pin) + implementation notes + Stage-B evidence root. No change to `src/`,
  `experiments/`, `tools/`, P16 construction file, P20M accepted roots
  (`raw_prior_1p5m.npz`, `raw_prior_orders_1p5m.json`), P20N accepted root
  (`alt_l2_tables_1p5m.npz`), P20O/P20Q accepted roots (`raw_prior_2m.npz`,
  `raw_prior_orders_2m.json`, `alt_l2_tables_2m.npz`, `l2_alt_hold_ir_2m/`),
  X08/X09/X10 probe roots, H2 run root, or `results/` /
  `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20R-R1..R9 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance.
  Descriptive-only label; `undetected` isolated; oracles never operational; H2
  decision explicitly deferred to main-thread analysis after acceptance.
- **Tasks**: (planner task list for coder agents) H1 verify + freeze 1.5M
  artifact reuse + freeze new-order derivation contract (§3, R1); H2 freeze
  VAL-remainder population/gates (§4, R2); H3 freeze replayed caps from the
  carried 1.5M point (§5, R3); H4 freeze single-factor order pins — frozen-A
  order + new-B order + derivation-program pin (§§2–3/§6, R4); H5 wire
  endpoints/taxonomy + mandatory nine scalars + IR-1..IR-5 incl. IR-3 thresholds
  (§7, R5); H6 enforce one-shot budget/stop (§8, R6); H7 Stage-A suites green
  with zero-open audit (R8); H8 independent Pre-EXECUTE adjudication of
  reuse/new-order/K-literal/population/IR boundary (R7); H9 single authorized
  Stage-B attempt (R6/R7); H10 independent Pre-RESULT + acceptance (H2
  quantities checked present, never decided in-packet).
- **Honest scope** (binding on proposal/design/packet/return language):
  single-block (1.5M VAL remainder) single-factor test of one alternate
  L2-order position rule under the frozen α1 construction at frozen disclosure
  with the mandatory H2 instrumentation; descriptive only; the VAL-remainder DEV
  block is consumed by this packet; the 41-frame stub and the 2M HOLD remainder
  stay untouched; no H2 verdict, no reliability claim; the H2 decision is
  analysis, not a block result.

## 1. Mission

With ZERO new protected derivation — the §3 1.5M TRAIN-derived raw prior + its
session-derived disclosure point + its session-derived worst-first orders +
its α1 alt table, ALL reused read-only with digest replay (S2-i satisfied by
same-session reuse, never carried across sessions) — and the ONLY derivation
being the alternate L2-order position rule computed off-protected-data from
the reused worktree prior by the frozen program with zero sampling, zero
genie, zero protected reads (S2-i preserved; DEV content opens only at Stage
B), and everything else fixed (α1 construction, K1/K2, floor 1e-15, N=32768,
greedy SC only, new P20R tag domains only), zero further tuning:

> On ONE first-use 1.5M VAL-remainder block, does the new-order operational arm
> (B) record exact where the frozen-order anchor arm (A) records a non-exact
> L2-layer first error at identical K sizes — and does any A-fail→B-exact
> restoration re-appear — with the hazard/coverage state AND the mandatory H2
> IR-1..IR-5 payload recorded under each order?

P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, P20K DEV 1152..1535 are
CONSUMED; TRAIN remainder 1536..1659 insufficient/closed; P20M VAL DEV
1660..2043 CONSUMED; 1.5M VAL remainder 2044..2171 is the P20R DEV (first use,
consumed by this packet), stub 2172..2212 RESERVED never-decoded; P20N HOLD DEV
2213..2724 CONSUMED, HOLD remainder 2725..2766 never-used; P20O 2M VAL DEV
2187..2826 CONSUMED, VAL remainder 2827..2915 never-used; P20Q 2M HOLD DEV
2916..3555 CONSUMED, HOLD remainder 3556..3644 never-decoded under this packet;
P20L never executed (zero consumption). The ENTIRE 1M pool is fail-closed. All
branches after this packet are deferred to §16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- Construction route (descriptive, no verdict): P20N (1.5M HOLD: B 1/4 vs A 0/4,
  all 14 failures L2-layer) → P20O (2M VAL: A 0/5, B 2/5, C 0/5, D 3/5;
  b_restored 2 descriptive, d_restored 3 diagnostic) → P20Q (2M HOLD: A 0/5,
  B 4/5, C 0/5, D 4/5; b_restored 4 descriptive, d_restored 4 diagnostic; 12/12
  L2 failures natural-in-prefix but U-domain-out). Three events, three segments
  — no reliability claim. The chain shows the current α1 form still active at
  zero disclosure delta by design; the §16 falsification trigger for abandoning
  it never fired as a P20R precondition. Order is the remaining single upstream
  position-set factor.
- H2 predecessor (frozen input, not re-argued): H2a REFUTED (8/14 evaluable
  blocks anomalous, strongest gap 0.097058 on P20N b3 — re-ranking by AVERAGE
  hazard will not order arms); H2b SUPPORTED (median fail/prefix ratio 2.2835,
  n=37; IR-2 median 0.883, n=12 — fail sites live in the hazard tail);
  H2c SUPPORTED (in-X 35/37 = 0.9459; out-of-U 23/23 on 2M — fail sites already
  inside disclosed X, so the current set is not catastrophically misplaced);
  H2d SUPPORTED-flat (mean_abs_diff 0.002185 — floor carries no signal);
  H2e REFUTED-geometry-incoherent (IR-4 pooled in-prefix 66/320 = 0.20625 <
  0.50 with IR-2 median ≥ 0.50 — top-16 hazard mass sits mostly outside the
  currently disclosed prefix under truncated scope). Net: the only candidate
  with a direct position-set number behind it is (a) L2-order positions under
  the raw prior. The new order rule must target local-spike geometry, not the
  mean (H2a warning). The H2 DECISION itself stays main-thread analysis AFTER
  P20R acceptance, never an in-packet verdict.
- Reuse-vs-derive stance (frozen, not re-argued): the scoring point was derived
  from the SCORING session's own TRAIN (P20M §3, S2-i). Re-deriving prior/orders/
  alt in P20R would cost new counts opens and new sampling for zero new
  information; reusing the frozen 1.5M artifacts read-only with digest replay
  preserves S2-i (same-session hypotheses, never carried across sessions) and
  S2-ii (build ⊂ TRAIN vs DEV ⊂ VAL-remainder disjointness, §4). The α1 RULE
  stays frozen (alpha 1.0). The ONLY derivation is the alternate L2-order
  permutation computed from the reused worktree prior arrays by the frozen
  program with zero sampling, zero genie, zero protected reads (§3). Fixed
  disclosure means fixed WITHIN the packet after the Stage-A freeze (B−A = 0,
  D−C = 0 by design); the SET-delta between the A and B L2 position lists IS
  the factor, recorded byte-exact.
- Alternatives rejected in writing: (a) re-derive prior/alt/orders from
  protected counts in P20R — second counts open + second sampling for identical
  inputs, forbidden; (b) any α other than 1, any second construction, any
  construction sweep — second factor, forbidden; (c) L2-side bounded search at
  the fixed point now — searches around a point H2e calls incoherent,
  premature until one alternate position set is tried, deferred; (d) second
  single construction form now — confounds construction×position attribution on
  a single block, deferred; (e) λ anywhere — the X08-falsified operating point,
  forbidden; (f) floor change — H3/H2d exonerated, forbidden as the factor;
  (g) K change or budget recompute from alt-H or from 2M — violates fixed
  disclosure and same-session reuse (S2-i); alt-H descriptive only (§3);
  (h) SCL/list/belief decoder — decoder change, out of scope; (i) consume the
  41-frame stub 2172..2212, the 89-frame 2M HOLD remainder 3556..3644 beyond
  counting, any consumed population, or any 1M range — destroys reserved/
  consumed populations, forbidden; (j) cross-session pooling (1.5M + 2M mixed)
  — forbidden; (k) freeze any IR field as absent — user decision requires all
  five PRESENT, forbidden.
- Session inventory (no new protected access by this planner; provenance from
  the split manifest `nbldpc_v25_split_manifest_v1` read as JSON metadata only,
  plus P20M/N/O/Q §§2/4): 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD
  554/141824 (256 rows/frame; see §4 for frame bases). 2M TRAIN 2187/559872 +
  VAL 729/186624 + HOLD 729/186624. Geometric position: P20R 1.5M-VAL-remainder
  DEV is the FIRST 128 VAL-remainder frames 2044..2171 (ONE full block:
  128×256 = 32768 pairs); stub 2172..2212 (41 frames / 10496 pairs)
  never-decoded under this packet.
- Runner-delta design choice (frozen; the §10 "design.md" decision): a THIN NEW
  runner module importing the accepted P20Q `l2_alt_hold_ir_2m` runner read-only
  (which itself thin-imports accepted `l2_alt_maintain_2m` → accepted
  `raw_prior_val_1p5m`: VAL/HOLD population pattern, TRAIN-exclusion gate
  family, order-file + `--order-digest` mechanism with zero Stage-B sampling,
  P20A endpoint/taxonomy/recount/resource machinery, `_l2_hazard_diagnostics`
  + `_ir_hazard_diagnostics` code points with nine scalars + IR-1..IR-5).
  Exact delta list, nothing else: (d1) population → 1.5M VAL-remainder DEV
  (§4; 2M paths excluded as consumed); (d2) prior/alt sources → the P20M/P20N
  frozen 1.5M files reused read-only behind replayed `reuse_prior_identity` +
  `reuse_alt_identity` + `reuse_order_freeze_A` gates (§3; worktree-file reads
  only, never the V25 counts NPZ); (d3) K pins → the 1.5M-session-derived
  (K_total,K1,K2)=(7020,331,6689) replayed as literals (never recomputed, never
  recarried from 2M, never from alt-H); (d4) orders → DUAL: frozen-A order file
  (`raw_prior_orders_1p5m.json`, byte-identical on arms A/C) + Stage-A new-B
  order file (`new_l2_order_1p5m.json`, byte-identical on arms B/D), each
  digest-gated, each disclosing first-K1 / first-K2 prefixes at identical sizes
  (§§3/6); (d5) arms A/B/C/D per §6 (same K, same α1 tables; order SET is the
  only delta between A and B, mirrored between C and D); (d6) new P20R tag
  domain (§6); (d7) new-order derivation program (worktree-prior-only,
  deterministic, zero sampling/genie, zero protected reads) + dual
  order-identity gates + derivation-program pin (§§3/9); (d8) 1.5M-VAL-remainder
  population + DEV∩build-frames disjointness declared inside the
  TRAIN-exclusion gate (§4). No SC/transform/floor-semantics/tag-semantics
  change; no second factor. The alternative (edit any accepted module) is
  rejected: it would touch an accepted evidence-producing file; the thin
  importer leaves every accepted file byte-identical.

## 3. Reuse freeze + new-order derivation stance (normative — 1.5M artifacts reused read-only, zero Stage-A protected reads; ONE new permutation by the frozen program)

- Counts source: NONE. Stage A performs ZERO protected opens (counts 0/0 at
  Stage-A close; the V25 counts NPZ is NEVER opened/statted/listed at any stage
  of this packet). The §3 P20M/P20N derivation inputs are not re-read.
  FORBIDDEN reuse inputs: any 1M split, any 2M split for derivation, 1.5M
  DEV/VAL-remainder/HOLD frames for derivation, Model-F CAL artifact.
- Reused products (paths under the frozen queue dirs, read-only; Stage A
  verifies by worktree-file digest recomputation ONLY — canonical recipe for
  the prior, file-bytes sha256 for orders/alt; zero parquet/NPZ protected
  opens):
  (p1) `raw_prior_1p5m.npz` (P20M queue dir) — canonical digest
  `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac` (recipe
  `per_session_calibration.canonical_prior_digest`: sorted-key `key + shape +
  dtype + C-order bytes` sha256); keys exactly `counts_ab, f_raw, p1, p2, p_b,
  lambda_star, floor_value, h1, h2, h_total` (`lambda_star` `0.0`;
  `floor_value` `1e-15`); session H literals
  `0.02519949692375297 / 0.8003665547495433 / 0.8255660516732963` recomputed via
  accepted `target_construction.entropy_bits` within 1e-12 (never hand-filled;
  `beta_eff_empirical` never hand-filled per AGENTS.md §5.5); `p_b` cross-check
  pinned.
  (p2) `raw_prior_orders_1p5m.json` (P20M queue dir) — file-bytes sha256
  `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`; full
  L1+L2 worst-first permutations, K1 331 / K2 6689 / K_total 7020. This is the
  FROZEN-A order (anchor).
  (p3) `alt_l2_tables_1p5m.npz` (P20N queue dir) — file-bytes sha256
  `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`; keys
  exactly `counts_ab, f_alt, p1, p2_alt, alpha, floor_value, h1_inc, h2_alt,
  h_total_alt` (`alpha` `1.0`; `floor_value` `1e-15`); `p1` = the P20M 1.5M
  incumbent `p1` (Stage A asserts equality within 1e-12 elementwise);
  descriptive alt-H `0.02519949692375297 / 1.4447543021770293 /
  1.4699537991007823` (never a budget input).
- Budget/split replay (S2-i satisfied by same-session reuse):
  `K_total = 7020` via the literal
  `1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536]` (P20M §3
  display, replayed never recomputed); `(K1,K2) = (331,6689)` replayed never
  recarried from 2M (334/6746/7080 never enter this packet); NO recomputation
  from alt-H; NO hand-fill; NO new sampling (Stage-A genie calls 0, Stage-B
  sampling 0).
- New-order derivation contract (the ONLY derivation; Stage-A product):
  the alternate L2-order permutation SHALL be computed off-protected-data from
  the reused worktree prior arrays ONLY (`counts_ab`/`f_raw`/`p1`/`p2` from the
  §3 `raw_prior_1p5m.npz` worktree file; the frozen-A order file as
  shape/reference only) by the frozen program
  (`l2_order_position_1p5m.py:derive_new_l2_order`, deterministic, pinned in
  `P20R_FREEZE.md` with module path + function + argv). Derivation opens zero
  protected content (worktree-file reads only); performs zero sampling, zero
  genie calls, zero derivation seeds (sampling 0 at every stage); emits a
  byte-exact length-32768 L2 permutation plus the carried L1 prefix unchanged
  (L1 order stays the frozen P20M L1 order on all arms); discloses first-K2
  positions at identical size K2=6689 (size-delta zero; SET-delta IS the
  factor). Stage-A product identity: path
  `.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/new_l2_order_1p5m.json`,
  format JSON holding the full L1 (carried frozen) + new-L2 permutations plus
  provenance (reused-prior digest + program pin + zero-sampling attestation),
  file-bytes sha256 `<FROZEN_AT_STAGE_A>` with freeze rule = derive once in
  Stage A, pin in `P20R_FREEZE.md`, gate on equality thereafter. The exact
  per-position ranking functional (FROZEN B-1 user decision 2026-09-19 — Stage A SHALL NOT invent or alter it): Rank all 32768 L2 positions by descending
  alt-table true-cell hazard mass (-log2 mass at each position's true (U1_cond,B,U2) cell under p2_alt with U1_cond = hard-L1 candidate,
  the same hazard definition as the IR recorders), take the first K2=6689 positions as arm B's disclosed L2 set; tie-break by ascending
  natural block coordinate; deterministic, zero sampling, zero genie calls, zero protected reads (inputs: worktree `raw_prior_1p5m.npz` arrays only); arm A's set stays the frozen incumbent-order first-K2 prefix (see §15 blocker resolved). All derivation CONTRACT constraints above
  (inputs, determinism, zero sampling/reads, length, K2 size, provenance) are
  frozen here independent of the B-1 functional (decided 2026-09-19).
- D1/D2 status: no feasibility recompute is required for a pure order delta at
  frozen K (disclosure sizes unchanged; §5 caps replay). Stage A replays the
  P20N D2 FEASIBLE outcome as a literal (margin `3928.304784481981` bits,
  TRAIN-only, zero VAL-remainder reads) BEFORE any DEV contact; a replay
  mismatch BLOCKS before any DEV open (DEV read stays 0/1) and no Stage-B
  authorization is requested.
- Stage B loads the frozen files read-only behind the `reuse_prior_identity` +
  `reuse_alt_identity` + `reuse_order_freeze_A` + `new_order_identity_B` +
  `order_derivation_program_identity` gates (digests + lambda-0.0/alpha-1.0/
  floor pins + exact key sets + H-literal recomputation within 1e-12 + `p_b`
  cross-check + `p1`-equality recheck within 1e-12 + K-literal replay, or
  BLOCKED before any sampling and before any SC call).

## 4. Population and closed/consumed-data rule (normative)

- The following are CONSUMED/CLOSED and SHALL NOT supply P20R blocks: the three
  P18/P19 HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599), P20C/P20E/
  P20F DEV blocks (1M 0..383 / 384..767 / 768..1151, remainder 1152..1199 never
  used), P20H DEV (1.5M TRAIN 0..383), P20I DEV (384..767), P20J DEV (768..1151),
  P20K DEV (1152..1535, remainder 1536..1659 insufficient/closed), P20M VAL DEV
  (1.5M VAL 1660..2043), P20N HOLD DEV (1.5M HOLD 2213..2724), HOLD remainder
  2725..2766 (never-used), P20O 2M TRAIN-build 0..2186 as DEV, P20O 2M VAL DEV
  2187..2826 (CONSUMED 1/1), VAL remainder 2827..2915 (never-used), P20Q 2M HOLD
  DEV 2916..3555 (CONSUMED 1/1); P20L never executed (zero consumption). The
  ENTIRE 1M pool and the ENTIRE 2M session (except the counted-never-decoded
  HOLD remainder §4 table) are fail-closed against P20R DEV selection
  (cross-file gate). 1.5M TRAIN 0..1659 SHALL NOT supply P20R blocks (build
  frames). 2M TRAIN 0..2186 SHALL NOT supply P20R blocks (other-session build
  frames). 2M VAL 2187..2915 and 2M HOLD DEV 2916..3555 SHALL NOT be
  opened/statted/listed/read under this packet in any form.
- 1.5M-VAL-remainder-first-use justification (same canonical TRAIN→held-out
  separation as P20M §4, frozen, not re-argued in Stage A/B): the VAL remainder
  has never been decoded, tuned on, or scored by any EXECUTED NB-Polar packet;
  1.5M TRAIN supplies the session hypotheses (raw prior + alt table both from
  TRAIN-fitted counts, new order from the same worktree prior, never from
  VAL-remainder frames); using the remainder DEV as a one-shot scoring
  population is declared once, consumed once, never tuned, never returned to a
  validation role. The stub stays undecoded.
- Stage B runs on the DECLARED population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin frozen in Stage A by manifest cross-check; mismatch blocks; planner performed zero opens/stats/listings) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 (JSON-metadata read only) |
| construction/order-derivation input | §3 worktree `counts_ab`/prior arrays ONLY (TRAIN-fitted; never a VAL-remainder frame) |
| VAL-remainder DEV frame rule | FIRST 128 VAL-remainder frames in (frame_id, pair_idx) order → `2044..2171` (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed; manifest-count arithmetic: TRAIN 1660 [0..1659] + VAL 553 [1660..2212] = VAL-remainder base 2044 by P20M DEV consumption 1660..2043) |
| VAL-remainder DEV blocks (N=32768) | `2044..2171` (1 × 128 frames; 32768 pairs = ONE full block) |
| unused stub | VAL-remainder frames `2172..2212` (41 frames / 10496 pairs) recorded never used — counted, never decoded |
| 2M HOLD remainder | frames `3556..3644` (89 frames / 22784 pairs) recorded never used — counted, never decoded, never contacted beyond counting |
| build-frames disjointness (S2-ii) | counts/build frames ⊂ 1.5M TRAIN `0..1659` (P20M §3 input = 1.5M TRAIN counts ONLY); DEV ⊂ 1.5M VAL-remainder `2044..2171`; disjoint by split identity; declared frame sets above; the TRAIN-exclusion gate refuses any overlap before any protected content open |
| consumed-1M exclusions | entire 1M pool (any split/subrange) — overlap refuses before any protected content open |
| consumed-1.5M exclusions | all 1.5M TRAIN `0..1659` + VAL DEV `1660..2043` + HOLD `2213..2766` (DEV 2213..2724 + remainder 2725..2766) — overlap refuses before any protected content open |
| consumed-2M exclusions | 2M TRAIN `0..2186` as DEV; 2M VAL `2187..2915` (incl. consumed DEV 2187..2826 + remainder 2827..2915); 2M HOLD DEV `2916..3555` — all in any form |
| block count | 1 at N=32768 |
| tag domains | new P20R domain (§6) |

- Fail-closed gate family (frozen in the runner, order (a)→(g), cross-file first):
  (a) CROSS-FILE — DEV content-open path + stat-size/sha pin must equal the 1.5M
  identity; any 1M or 2M path or digest mismatch refuses before any SC call
  (frame integers alone are never identity); (b) INTRA-FILE VAL-REMAINDER — DEV
  ranges must overlap NONE of TRAIN-exterior/VAL-DEV/HOLD, and must lie wholly
  inside VAL 1660..2212 with DEV wholly inside remainder 2044..2212, else refuse
  before any protected content open; (c) CONSUMED-1M EXCLUSION — entire 1M pool;
  (d) CONSUMED-1.5M EXCLUSION — all 1.5M ranges above; (e) CONSUMED-2M EXCLUSION
  — 2M TRAIN-as-DEV + 2M VAL (DEV + remainder) + 2M HOLD DEV incl. the
  DEV∩build-frames disjointness declaration: DEV ⊂ 1.5M-VAL-remainder vs build
  ⊂ 1.5M-TRAIN with the frame sets above (S2-ii); (f) REUSE-PRIOR/ALT/
  FROZEN-ORDER/K-LITERAL + NEW-ORDER-DERIVATION-PROGRAM — §3 canonical/
  file-bytes digests + lambda-0.0/alpha-1.0/floor pins + exact key sets +
  H-literal recomputation within 1e-12 + `p_b` cross-check + `p1`-equality
  within 1e-12 + budget-literal replay (S2-i) + frozen-A order-file digest must
  match AND the new-B order derivation-program pin (module + function + argv +
  zero-sampling attestation) must match, else refuse before any SC call;
  (g) ORDER-POSITION-IDENTITY + TAG-DOMAIN — the §6 order quadruple (frozen-A
  digest on A/C, new-B digest on B/D, K1/K2 literals replaying exactly,
  `--source 1p5M` vocabulary) + P20R tag-domain pins must match, else refuse
  before any SC call.

## 5. Preregistered disclosure point (normative — 1.5M-session-derived, replayed at Stage A)

- K rule (S2-i satisfied by same-session reuse): `(K_total,K1,K2)` =
  `(7020,331,6689)` (P20M Stage-A derived from the §3 1.5M session H via the §3
  budget+split rules; replayed as literals in Stage A with the
  `1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536]`
  display; never carried as an absolute from 2M 334/6746/7080). NO recomputation
  from alt-H (the §3 alt-H literals are descriptive only); NO hand-fill; NO new
  sampling.
- Caps PREREGISTERED at Stage A from the carried point (rule
  `5*(K1+K2)+64` key-dependent bits/block, `10*32768+63 = 327743` public
  bits/tag, one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_frozen-order_operational (anchor) | 331 | 6689 | 35164 = 5*7020+64 | 327743 |
| B_new-order_operational (candidate) | same K1 | same K2 | same as A (Δ vs A exactly 0) | 327743 |
| C_frozen-order_oracle (diagnostic) | 0 | 6689 | 33509 = 5*6689+64 | 327743 |
| D_new-order_oracle (diagnostic) | 0 | same K2 | same as C (Δ vs C exactly 0) | 327743 |

- Planned totals (replayed at Stage A from the carried integers):
  key-dependent `2*35164 + 2*33509 = 137346` bits; public `4*327743 = 1310972`
  bits. B-vs-A and D-vs-C key-bit deltas are exactly 0 (order factor carries
  ZERO disclosure-size delta by design).
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate
  BLOCKS. Per-record fields pin the session point (`prior_source` raw/1p5M-reuse,
  `k1/k2/k_total`, `budget_literal_replayed`, `alt_digest`,
  `l1_order_digest`, `l2_order_digest` (arm-specific: frozen-A vs new-B),
  `floor_hit_rate`).

## 6. Arms (frozen; order is the ONLY delta between operational arms, mirrored between oracles)

- `A_frozen-order_operational`: frozen greedy SC with incumbent `p1` + §3
  `p2_alt` (α1), FROZEN P20M L1+L2 order prefixes (first-331 / first-6689 of
  digest `a9f18a9f…1da11bc638`) at carried K1/K2 (operational anchor = P20N
  construction + P20N order continuity; 2 SC + 1 P20R-domain tag per block).
- `B_new-order_operational`: frozen greedy SC with incumbent `p1` + §3 `p2_alt`
  (α1, byte-identical tables to A), NEW L2-order positions (first-6689 of the
  Stage-A `new_l2_order_1p5m.json`, digest `<FROZEN_AT_STAGE_A>`) with the SAME
  carried L1 order and SAME K1/K2 (operational; the single-factor candidate;
  2 SC + 1 tag per block). Construction, K sizes, floor, decoder all
  byte-identical to A; the disclosed-L2 SET delta IS the factor.
- `C_frozen-order_oracle`: true-L1-conditioned diagnostic with `p2_alt` + FROZEN
  order at carried K2 (provenance ORACLE, deployable=false, excluded from every
  operational aggregate; never a correction result; 1 SC + 1 P20R-domain tag
  per block).
- `D_new-order_oracle`: true-L1-conditioned diagnostic with `p2_alt` + NEW order
  at carried K2 (provenance ORACLE, deployable=false, excluded from every
  operational aggregate; never a correction result; 1 SC + 1 P20R-domain tag
  per block).
- No other arms. Block-major (A, B, C, D) on the single DEV block; checkpoint
  after every (arm, block) record; 4 records total. P16 construction file
  unchanged (digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  carried read-only); kernel/representation/transform/SC arithmetic unchanged;
  greedy SC only; no SCL/new kernel/model/schema. Stage A performs ZERO sampling;
  Stage B performs pure VAL-remainder scoring (6 SC + 4 tags) with ZERO sampling
  — Stage-B TRAIN genie calls pinned at 0, Stage-A genie calls pinned at 0
  (reuse + deterministic permutation need no derivation sampling).
- Tag domain (new P20R): master 2026092340, prefix
  `nbpolar-p20r-order-position-1p5m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from
  ALL of P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K/P20M/P20N/
  P20O/P20Q (incl. masters 2026092280/2026092300/2026092310/2026092330 and all
  test/derivation seeds). Stage A verifies by repo grep that master 2026092340
  and focused-test seeds `2026092341..2026092347` appear in no tracked file
  outside the P20R runner/tests/packet/spec documents (planner pre-checked
  202609234* absent; zero protected access).
- No derivation seeds (deterministic permutation; zero sampling at any stage).
  Disjointness holds by the grep rule above. Stage B takes NO derivation seeds
  and performs no sampling.
- L2 disclosed-set rule (single-factor guard): arm A/C disclose the first-6689
  positions of the SAME frozen 1.5M order file (digest-gated
  `a9f18a9f…1da11bc638`); arms B/D disclose the first-6689 positions of the
  SAME new order file (digest-gated `<FROZEN_AT_STAGE_A>`); the L1 set is the
  first-331 of the SAME frozen P20M L1 order on all arms. Positions are fixed by
  the frozen files, never selected on closed blocks, consumed ranges, or DEV
  data. K sizes frozen identical on all arms; the SET-delta between the A and B
  L2 lists is recorded byte-exact (symmetric difference + rank-displacement
  table, descriptive only).

## 7. Thresholds, endpoints, and mandatory instrumentation (descriptive only — P20M-style)

- Outcome label `TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE`
  iff ALL integrity gates (§9) hold — regardless of exact-count. Any exact
  count (including 0/4 and partials) is COMPLETE when integrity holds.
- Choice + justification: P20M-style descriptive (no recovery threshold). This
  is the FIRST test of an alternate L2-order position set at frozen α1 and
  frozen disclosure on a fresh population — there is no empirical basis for a
  restoration threshold here. A 62/64-class gate would be an invented
  threshold, explicitly forbidden. Branch and H2 decisions belong to
  main-thread analysis AFTER acceptance (§16).
- NO recovery / superiority / qualification / promotion claim. Descriptive
  reading only, preregistered before execution: per-arm exact counts;
  `b_maintained_count` = blocks where B is exact; `b_restored_count` = blocks
  where A fails and B is exact; the A→B transition table (A-exact/B-exact,
  A-exact/B-fail, A-fail/B-exact, A-fail/B-fail, single-block degenerate);
  `a_fail_b_exact_hazard_elevated` = whether the restoration (if any) occurs at
  a hazard-elevated in-X site; and the oracle pair C→D (`d_restored_count`,
  `d_maintained_count`) as diagnostic only. "Maintain" = B exact wherever A
  exact; "restore" = A fail → B exact. Any (or neither) counts as COMPLETE. The
  positive/negative branch decision (proposal §2: new-order arm records exact
  while anchor records non-exact L2 first error at a hazard-elevated in-X site
  vs both non-exact with L2 persistence) and the H2 decision stay with the main
  thread after acceptance. No efficiency language anywhere (CE ratios never
  called efficiency).
- Status taxonomy frozen: `exact` (tag-verified: outcome exact AND tag_pass AND
  label_match) vs `verify_failed`, `undetected` isolated (never success),
  plus `decode_failed` / `nonfinite` / `resource_abort` via the P20A path. P20A
  four-endpoint separation (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` /
  `pair_exact`) per record. First-error coordinate/layer rows (natural block
  symbol index, settled X09-R1 D4) are the primary diagnostic signal.
  Per-record floor-hit fields (`floor_hits`, `floor_hit_rate`) complete per
  record (S2 reporting).
- Carried X09-R1/P20O instrumentation (ALL NINE per-record SCALARS, scalar
  fields intact, arm-specific order digest): `l2_order_digest` (= frozen-A
  digest on A/C records, new-B digest on B/D records, gated), `l2_prefix_len`
  (= session K2 6689 on every record, gated), `l2_fail_in_prefix`,
  `l2_fail_hazard_bits`, `l2_fail_nbhd_mean_bits` (frozen radius R=8 window,
  clipped to the block), `l2_prefix_hazard_mean_bits`,
  `l2_fail_nbhd_floor_frac`, `l2_prefix_floor_frac`,
  `l2_fail_in_prefix_u_domain` (frozen PRESENT). Semantics identical to P20Q §7
  (true cells under the record's own arm table; failing fields null unless
  `first_error_layer == L2`; prefix-wide means on every completed record; hazards
  = `-log2` arm-table mass at each position's true `(U1_cond, B, U2)` cell with
  `U1_cond` = hard-L1 candidate on A/B, true high on C/D).
- Mandatory IR-1..IR-5 (ALL FROZEN PRESENT, bounded/size-capped/recording-only/
  post-decode/truth-isolation-safe; same caps/formulas as P20Q §7; Stage A pins
  exact formulas with injected vectors; never post-hoc):
  - IR-1 per-record 64-bin log-spaced hazard histograms {prefix, outside} using
    true cells (~1 KB/record): fields `ir1_hist_edges_bits` (65 float64,
    log-spaced over hazard-bits, frozen formula), `ir1_hist_prefix_counts`
    (64 int), `ir1_hist_outside_counts` (64 int). Split by disclosed L2 prefix
    membership (X-domain, first-6689 of the RECORD'S OWN order file — frozen-A
    on A/C, new-B on B/D); hazards under the record's own arm table. Every
    completed record (never null).
  - IR-2 hazard-rank percentile of the first-error coordinate (1 float): field
    `ir2_first_error_hazard_rank_pct` (float64 in [0,1], 1.0 = most hazardous;
    fraction of block positions with hazard <= fail-site hazard; null unless
    `first_error_layer == L2` with computable hazard, else null with frozen
    nullability).
  - IR-3 above-threshold prefix counts (≤3 scalars × ≤2 frozen thresholds):
    EXACTLY two thresholds, per-record deterministic, no tuning —
    `ir3_thresh_lo_bits` = 1.0 × record `l2_prefix_hazard_mean_bits`,
    `ir3_thresh_hi_bits` = 2.0 × record `l2_prefix_hazard_mean_bits` (frozen
    multipliers; justification: X10 median fail/prefix ratio 2.246 → 2.0× marks
    the elevated tail, 1.0× marks above-mean mass; deterministic per-record,
    frozen before the run, never fed back). Fields (6 scalars):
    `ir3_thresh_lo_bits`, `ir3_thresh_hi_bits`,
    `ir3_prefix_above_lo_count`, `ir3_prefix_above_lo_frac`,
    `ir3_prefix_above_hi_count`, `ir3_prefix_above_hi_frac` (prefix positions
    using true cells under the record's OWN order; every completed record,
    never null).
  - IR-4 top-k hazardous positions with ranks (k≤16, frozen k=16): fields
    `ir4_topk_coords` (16 int, natural block symbol indices),
    `ir4_topk_hazard_bits` (16 float), `ir4_topk_in_prefix` (16 bool/int,
    X-domain prefix flags under the record's OWN order), `ir4_topk_ranks`
    (16 int, 1-based hazard ranks). Hazard-order listing only; error-coordinate
    join is post-hoc. Every completed record (never null; N=32768 always fills
    16).
  - IR-5 capped per-position series (≤4096×2 float32 + truncation flag) as the
    escalation, FROZEN PRESENT: fields `ir5_series_hazard_bits` (≤4096 float32,
    first 4096 natural-order positions 0..4095 with true-cell hazards),
    `ir5_series_in_prefix` (≤4096 int/bool, X-domain prefix flags under the
    record's OWN order), `ir5_series_truncated` (bool; true at N=32768 since
    32768 > 4096), `ir5_series_total_len` (=32768). Recording-only dump of the
    frozen hazard table + masks; the decoder consumes only the frozen order as
    before. Every completed record.
  - Size envelope: IR-1 ~1 KB + IR-2 8 B + IR-3 6 scalars + IR-4 ≤16×4 scalars +
    IR-5 ≤4096×2 float32 (~32 KB) + flags ≈ ≤35 KB/record; 4 records ≈ ≤140 KB.
    Bounded by the frozen caps; larger blocks truncate only via the IR-5 flag
    (no silent growth).
  - Writer code point (frozen): successor module `l2_order_position_1p5m.py`,
    function `_ir_hazard_diagnostics(*, block, view, p2_arm, counts_arr,
    l2_order, k2, first_error, prefix_mean, ...)` — called post-decode (after
    tag scoring) from the successor's `_operational_record` / `_control_record`
    equivalents alongside the nine carried scalars (the P20Q
    `_ir_hazard_diagnostics` code point is the carried-over callsite pattern).
  - Truth-isolation boundary (normative): block truth (high/low/bob) and the arm
    tables enter `_ir_hazard_diagnostics` for RECORDING ONLY after all SC calls
    for the record have completed; its outputs are written into the record dict
    and never passed to `run_operational_block`, `run_oracle_control_block`,
    `_decode_layer`, `build_p1_metrics`, `gather_p2_metrics`, or any
    disclosure/order decision. A focused truth-isolation sentinel test pins this
    boundary (mutating truth changes no metric/decision input).
- H2 decision quantities (pre-registered; the H2 DECISION stays main-thread
  analysis after acceptance — NO outcome asserted here): the IR payload tables
  the accepted run must supply are (i) per-record `ir2_first_error_hazard_rank_pct`
  distribution (single-block value + A-vs-B split, C/D separately); (ii) IR-1
  histogram summaries (prefix vs outside mass, tail shape per record, A-vs-B
  contrast); (iii) IR-3 above-threshold prefix mass (lo/hi counts/fracs per
  record vs exactness); (iv) IR-4 top-k prefix flags + ranks (X-prefix
  concentration under EACH order — frozen-A vs new-B geometry contrast, the
  direct position-set observation); (v) IR-5 capped series + truncation flags
  as the escalation if IR-1..IR-4 leave H2 undecided; plus the nine carried
  scalars (with arm-specific order digests) for P20N/P20O/P20Q continuity and
  the byte-exact A-vs-B disclosed-set delta table. These quantities inform
  H2a–H2e; they are not thresholds, not pass/fail verdicts.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized
  execution; no rerun, no seed change, no prior/budget/order/construction
  tuning after preregistration. Execution-error rerun only as a recorded repeat
  of the identical freeze, never as tuning. P20H–P20Q spent attempts do NOT
  transfer (independent packet).
- Reads (split-counted): counts-calibration opens 0/0 at every stage (reuse;
  the V25 counts NPZ is never opened/statted/listed) + VAL-remainder-DEV open
  1/1 reserved for Stage B (parquet, consumed at first DEV content open).
  VAL-DEV reads 0; HOLD reads 0; 1M reads 0; 2M reads 0 (2M HOLD remainder
  counted never-decoded, never contacted beyond counting). Any reopen, new
  calibration/derivation on real frames, real-frame use for derivation, or DEV
  refit is forbidden. Prior-file/alt-file/order-file loads and the deterministic
  new-order derivation are worktree-file reads, not protected opens.
- SC/tag/genie budget: Stage-A genie 0 + Stage-B pure DEV 6 SC (1 block ×
  (2+2+1+1)) + 4 tags + 4 records with ZERO sampling at every stage (Stage-A
  sampling 0, Stage-B sampling 0); derived per-record recomputation must equal
  counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  accounting; abort is BLOCKED, never success. Wall/RSS ceilings frozen in
  Stage-A freeze (P20Q-class reference at the smaller 6-SC / 4-tag budget:
  external 198.39 s / ~620 MiB runner peak at 30-SC / 20-tag; P20R plans the
  same-class envelope with the bounded IR payload on 1 block; external timeout
  1200 s + virtual/RSS caps 2 GiB + single thread frozen).
- Strategy stop rules binding: no tuning on closed blocks or the new DEV after
  the one shot; no reuse of consumed 1M pool (any split/subrange), any consumed
  1.5M range (TRAIN 0..1659, VAL DEV 1660..2043, HOLD 2213..2766, stub beyond
  counting), consumed 2M TRAIN-as-DEV / VAL (DEV + remainder) / HOLD DEV,
  2M HOLD remainder beyond counting, or any other session; no third factor
  after inconclusive single-factor; no oracle-as-operational; no
  population-reliability inference from this single block alone; no tuning
  inside this packet; no H2 verdict inside this packet.
- SCL entry gate UNCHANGED (unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B five files)

- Stage-A freeze pins (zero protected opens): reuse-artifact paths +
  canonical/file-bytes digest replays + H-literal recomputation + `p_b`
  cross-check + `p1`-equality recheck + floor-hit replays; K_total literal
  replay display + (K1,K2) integers + frozen-A order-file digest replay; alt
  file-bytes digest replay + alpha/floor/key-set/`p1`-equality/alt-H replays;
  new-B order artifact path + file-bytes digest + derivation-program pin
  (module + function + argv + zero-sampling attestation) + A-vs-B set-delta
  table; D2 FEASIBLE replay literals + outcome; exact module path + N-flag
  Stage-B command verbatim + population integers + caps + budgets + tag domain +
  P16 construction digest + IR-3 threshold multipliers (1.0×/2.0×) + IR caps;
  recorded in `P20R_FREEZE.md`. Stage-A product identities: ONE new artifact
  (new-B order file under this queue dir:
  `new_l2_order_1p5m.json`; digest pinned in the freeze); reuse paths point at
  the P20M/P20N queue dirs (digests pinned in the freeze).
- Stage-B root:
  `.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/l2_order_position_1p5m/`
  (exactly five files; per-(arm, block) checkpointing; pure DEV scoring — zero
  sampling; one DEV content open; no reopen/rerun). Root must be ABSENT at
  Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json` (P16
  construction digest + reuse-prior digest-gate proof + reuse-alt digest-gate
  proof (file bytes sha256 equals the frozen `--alt-digest`) + frozen-A order
  digest-gate proof + new-B order digest-gate proof (file bytes sha256 equals
  the frozen `--new-order-digest`) + derivation-program pin (module + function
  + argv + zero-sampling attestation) + A-vs-B set-delta table + K-literal
  replay + budget-literal replay + tag-domain pins + split manifest + DEV
  integers + DEV∩build-frames disjointness declaration with frame sets + IR-3
  multiplier pins + IR cap pins), `per_block_arm_outcomes.jsonl` (4 records at
  completion, each carrying the nine scalars with arm-specific order digest +
  IR-1..IR-5 payload with frozen nullability/caps), `aggregate_summary.json`
  (incl. the IR payload tables + A-vs-B set-delta table: rank-percentile value
  + histogram summaries + above-threshold mass + top-k concentration under EACH
  order), `report.md`. Per-record §7 endpoints + first error coordinate/layer,
  zero-count hits, floor hits + floor-hit rate + log loss, true-H vs
  candidate-H L2 NLL, taxonomy, construction-point fields (`l2_construction`
  alt-α1 on all arms, `k1/k2/k_total`, `prior_digest`, `alt_digest`,
  `l1_order_digest`, `l2_order_digest` arm-specific) + the NINE carried scalars
  + the IR-1..IR-5 fields (all PRESENT per the Stage-A freeze).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0);
  genie call counts (Stage-A 0 + Stage-B 0) + SC counts (L1/L2 split) + tag
  counts exact; block SER/NLL; wall/RSS; `b_maintained_count` /
  `b_restored_count` / `d_restored_count` / `d_maintained_count` descriptive +
  the A→B transition table (single-block) + A-vs-B set-delta table; per-arm
  floor-hit rate + per-arm prefix hazard means + IR payload tables reported.
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `reuse_prior_identity` (1.5M npz
  canonical digest + lambda-0.0/floor pins + exact key set + H literals within
  1e-12 + `p_b` cross-check, worktree-file only); `reuse_alt_identity`
  (file-bytes digest + alpha-1.0/floor pins + exact key set + `p1`-equality
  within 1e-12 + descriptive alt-H literals);
  `alt_construction_budget_feasibility_replayed` (P20N FEASIBLE replay required
  before Pre-EXECUTE; replay mismatch ends the packet at Stage A with DEV
  untouched); `dev_split_manifest_identity`; `dev_block_range_identity` (§4
  gate family (a)→(g): cross-file first, then intra-file VAL-remainder
  containment, then consumed-1M, consumed-1.5M, consumed-2M exclusions incl. the
  DEV∩build-frames disjointness declaration, then reuse-prior + reuse-alt +
  frozen-A-order + K-literal + new-order-derivation-program pins, then
  order-position-identity + tag-domain pins); `order_derivation_identity`
  (derivation-program pin + reused-prior-digest input pin + Stage-A new-B order
  file-bytes digest, Stage-B file-bytes digest equality replay-exact, zero
  Stage-B sampling; ranking-functional = §3 frozen B-1 user decision 2026-09-19
  (Stage-A program pin `<FROZEN_AT_STAGE_A>`));
  `frozen_order_identity_A` (P20M program pin + frozen-A order-file digest,
  Stage-B file-bytes digest equality replay-exact, zero Stage-B sampling);
  `new_order_identity_B` (Stage-A new-B order-file digest, Stage-B file-bytes
  digest equality replay-exact, permutation-valid + K2-prefix-disclosed +
  L1-carried checks); `k_literal_exact` + `budget_literal_replayed` (S2-i:
  f=1.3 literal replayed from the P20M freeze, never a 2M absolute, never
  recomputed from alt-H); `target_population_contract`;
  `dev_population_exact` (128 VAL-remainder frames / 32768 pairs / 256 rows per
  frame / pair indices / symbol range); `blocks_exact_with_declared_remainder`
  (ONE exact DEV range `2044..2171` per arm in block-major slot order +
  never-used stub 41 frames / 10496 pairs + counted-never-decoded 2M HOLD
  remainder 89 frames / 22784 pairs); `four_records_exact`;
  `genie_calls_exact` (Stage-A 0 + Stage-B 0); `sc_calls_exact` (derived 6);
  `tags_exact` (derived 4);
  `orders_valid_k_prefixes_within_registered_arms` (frozen-A prefixes on A/C +
  new-B prefixes on B/D + construction quadruple α1×4 + K literals);
  `order_set_delta_recorded` (A-vs-B L2 disclosed-set symmetric difference +
  rank-displacement table byte-exact, size-delta exactly 0);
  `hazard_instrumentation_complete` (all nine §7 scalars present with correct
  nullability + arm-specific order digest on every completed record);
  `ir_payload_complete` (IR-1..IR-5 all PRESENT with frozen caps/nullability on
  every completed record: 64-bin histograms + rank percentile + two-threshold
  counts + top-16 + capped series with truncation flag);
  `floor_hit_rate_reported`; `oracle_isolation`;
  `buckets_disjoint_exhaustive` (unique arm/block + schema); `undetected_zero`;
  `nonfinite_zero`; `truth_isolation` (incl. the IR recorder sentinel);
  `disclosure_recount_exact`; `one_open_per_protected_input` (counts 0 +
  VAL-remainder-DEV 1); `input_stat_unchanged`; `no_unregistered_access`;
  `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (implementation + new-order derivation + injected tests +
  reuse-freeze; authorized separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_l2_order_position_1p5m.py -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20r/<uuid>/`
  temp root; protected-open audit declared separately (counts 0 + DEV 0 at
  Stage-A close). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A reuse + new-order verification (ZERO protected opens; worktree-file
  digest recomputation ONLY): recompute the P20M/P20N prior canonical digest +
  H literals + `p_b` + `p1`-equality + alt/order file-bytes digests from the
  frozen worktree files; replay K literals + D2 FEASIBLE replay; derive the
  new-B order permutation by the frozen program (worktree-prior-only, zero
  sampling, zero genie) and pin its file-bytes digest + program pin + set-delta
  table; confirm the §4 VAL-remainder frame integers against the split-manifest
  JSON metadata (no parquet/NPZ open/stat/listing); grep-verify the §6
  tag/test-seed freshness. Template (pins filled in the freeze; all flags
  required, no production default):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_order_position_1p5m --verify-reuse --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz --alt-digest 6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 --new-order-file .workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/new_l2_order_1p5m.json --new-order-digest <FROZEN_AT_STAGE_A> --k1 331 --k2 6689
```
  Stage A confirms the module path (thin importer of accepted
  `l2_alt_hold_ir_2m` per the §2 delta list d1–d8, or freezes a written
  equivalent with justification) and the `--source` vocabulary (only `1p5M`).
  Forbidden by default: `longrun_*`, `minrerun_*`, `routeA_*`,
  `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A freeze
  with the `<FROZEN_AT_STAGE_A>` pins filled; NOT AUTHORIZED until independent
  Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_order_position_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest <FROZEN_AT_STAGE_A> --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz --alt-digest <FROZEN_AT_STAGE_A> --source 1p5M --floor 1e-15 --n 32768 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 2044 2171 --block-frames 128 --remainder-frames 2172 2212 --tag-master 2026092340 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest <FROZEN_AT_STAGE_A> --new-order-file .workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/new_l2_order_1p5m.json --new-order-digest <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/l2_order_position_1p5m
```
  All flags required, no production default; four hardcoded arms with the order
  swap pinned (never CLI-tunable: A = α1 + frozen order at carried K; B = α1 +
  new order at carried K; C = frozen-order oracle; D = new-order oracle);
  Stage-B prior path MUST equal the §3 reuse pins; `--alpha` takes no Stage-B
  value (construction is frozen in the alt file). Stage A fills every
  `<FROZEN_AT_STAGE_A>` pin (`--prior-digest`, `--alt-digest`, `--k1/--k2`,
  `--order-digest`, `--new-order-digest`) with the §3 replayed/derived values
  plus the `--source` vocabulary (only `1p5M`) and the IR-3 multiplier + IR-cap
  pins in `frozen_plan.json`. Forbidden by default as above.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never
  `git show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: new-order artifact `new_l2_order_1p5m.json` (+ file-bytes digest +
  derivation-program pin + A-vs-B set-delta table + zero-sampling attestation)
  + reuse-verification freeze (`P20R_FREEZE.md`: §3 digest/H/`p_b`/`p1`-equality
  replays + K-literal replay + frozen-A order digest replay + new-B order digest
  + program pin + D2 replay + population integers + caps + budgets + tag domain
  + IR-3 multipliers + IR caps + module path + both commands verbatim) +
  implementation notes (exact files, diffs, test commands/results, frozen
  reuse/new-order/population/cap/command, D2 replay outcome) + thin runner +
  focused injected tests. NO other new artifacts (reuse paths point at the
  P20M/P20N queue dirs). Protected content opens 0 at Stage-A close (counts 0/0
  + DEV 0/1; zero sampling at every stage).
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md`
  (+ freeze, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`,
  `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec P20R delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20r/spec.md`
  + `tasks.md` P20R section (same umbrella change as P18/P19/P20A/P20B/P20C/P20E/
  P20F/P20G/P20H/P20I/P20J/P20K/P20M/P20N/P20O/P20Q; no new top-level change).

## 12. Allowed work

- New thin order-position runner (importer per §2 d1–d8) + new-order derivation
  program (worktree-prior-only, §3 contract) + focused injected tests
  (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`,
  `raw_prior_val_1p5m.py` (gate/population/record-writer pattern references),
  `l2_alt_hold_1p5m.py` (α1 construction-swap + 1.5M gate/population pattern
  reference), `l2_alt_maintain_2m.py` (gate/record-writer/nine-scalar pattern
  references), `l2_alt_hold_ir_2m.py` (import target; gate/population/IR
  record-writer pattern references) (+ `construction.py` / `prior.py` / `sc.py`
  contracts as called).
- ZERO protected opens in Stage A: worktree-file digest recomputation of the §3
  1.5M artifacts + deterministic new-order derivation from the worktree prior
  arrays (zero sampling, zero genie, §3 contract) + split-manifest JSON-metadata
  confirmation of the §4 VAL-remainder integers + grep-verification of the §6
  tag/test-seed freshness + closed-form IR formula pins on injected vectors
  (zero sampling, zero genie calls, zero real frames).
- P20R OpenSpec delta + packet docs + Stage-A freeze/return/review files +
  Stage-B evidence root (root only after Stage-B authorization) + the §3 reuse
  identity + the §3 new-order identity (§§3/9).

## 13. Forbidden work

- Any NPZ/parquet content open or stat/listing of 1.5M VAL-remainder-DEV/stub,
  1.5M VAL-DEV, 1.5M TRAIN, 1.5M HOLD, any 1M split, or any 2M split in Stage A
  (Stage-A protected opens: counts 0/0, DEV 0/1); any counts open at any stage;
  any K carried as an absolute from 2M or recomputed from alt-H (S2-i; replay
  only from the 1.5M session point); any derivation or sampling on real
  DEV/VAL/HOLD frames at any stage; any decoder execution before Pre-EXECUTE
  PASS + pasted Stage-B authorization.
- Any change to GF32/transform/SC arithmetic, floor value, 1.5M L1 tables,
  frozen 1.5M L1/L2 orders (A-side), disclosed sizes, tag scheme semantics,
  outcome precedence, accepted evidence roots, P20M/P20N products, P20O/P20Q
  products, X08/X09/X10 probe roots, H2 run root, or `src/` + `experiments/` +
  `tools/` frozen baseline. No disclosure-size change (B−A = 0, D−C = 0); no
  order change beyond the single new-B L2 position set; no decoder change.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the
  consumed 1M pool (any split/subrange), any consumed 1.5M range (TRAIN
  0..1659, VAL DEV 1660..2043, HOLD 2213..2766), stub 2172..2212 beyond
  counting, consumed 2M TRAIN-as-DEV / VAL (DEV 2187..2826, remainder
  2827..2915) / HOLD DEV 2916..3555, or 2M HOLD remainder 3556..3644 beyond
  counting; no second construction, no construction sweep, no bounded search,
  no second order beyond the single new-B set, no disclosure change; no tuning;
  no new-block peeking before the authorized attempt; no calibration on DEV; no
  H2 verdict inside this packet.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push; no self-acceptance; no P20D scope creep beyond the single frozen
  order factor; no P20H–P20Q rerun under this packet. No efficiency language
  anywhere.

## 14. Acceptance IDs

- `P20R-R1`: 1.5M reuse verified read-only from worktree files (prior canonical
  + orders/alt file-bytes digests replay-exact; H literals within 1e-12; `p_b`
  cross-check; `p1`-equality within 1e-12; exact key sets; lambda-0.0/alpha-1.0/
  floor pins; zero protected opens at every stage) + new-B order derivation
  contract verified (worktree-prior-only inputs, deterministic, zero sampling/
  genie, zero protected reads, length-32768 permutation, K2-prefix disclosed,
  program pin + file-bytes digest + set-delta table frozen at Stage A).
  Derivation-gate BLOCKED → planner rework, never a Stage-B fallback.
- `P20R-R2`: budget/split/orders replayed 1.5M-session-derived (S2-i literal
  replay displayed from the P20M freeze: K1 331/K2 6689/K_total 7020, never
  from 2M, never from alt-H; zero Stage-B sampling; zero Stage-A sampling);
  closed/consumed blocks select nothing; consumed 1M pool + all consumed 1.5M
  ranges + consumed 2M TRAIN-as-DEV + consumed 2M VAL (DEV + remainder) + consumed
  2M HOLD DEV excluded by source-tagged cross-file gates; 1.5M VAL-remainder DEV
  2044..2171 (ONE block 2044..2171, stub 2172..2212 + 2M HOLD remainder
  3556..3644 never used) gated + Pre-EXECUTE-approved; 1M/2M/1.5M-VAL-DEV/HOLD
  untouched in every form.
- `P20R-R3`: disclosure point preregistered per arm from the carried integers
  (A/B `5*(K1+K2)+64 = 35164` with Δ exactly 0; C/D `5*K2+64 = 33509` with Δ
  exactly 0; 327743 public; totals 137346/1310972 frozen at Stage A), recount
  mismatch 0; set-delta recorded byte-exact with size-delta exactly 0; CE ratios
  never called efficiency.
- `P20R-R4`: single-factor order pins (A frozen-order anchor + B new-order
  candidate + shared-L1 rule + C/D oracle mirror, §3 α1 rule replayed,
  `p1`-equality within 1e-12, derivation-program pin) frozen before execution,
  unchanged after; P16 construction migration pinned; no tag-guided selection,
  no evidence reuse, no post-hoc re-picking, no re-derivation.
- `P20R-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9;
  `undetected` isolated; oracle arms never operational; first-error
  coordinate/layer rows + per-record floor-hit fields + all nine carried scalars
  (arm-specific order digest) complete per record with correct nullability +
  IR-1..IR-5 ALL PRESENT with frozen caps/nullability on every completed record
  (IR-3 two thresholds 1.0×/2.0× prefix-mean; IR-4 k=16; IR-5 capped 4096 +
  truncation flag; record's OWN order used for every prefix flag);
  instrumentation + IR recorded-only (truth-isolation sentinel green).
- `P20R-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning;
  split-counted reads (counts 0/0 + VAL-remainder-DEV 1/1 + VAL-DEV 0 + HOLD 0 +
  1M 0 + 2M 0); resource aborts via P20A path with accounting preserved; stop
  rules + SCL gate intact.
- `P20R-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded (Pre-EXECUTE
  explicitly adjudicates §3 reuse/alt replay + new-order derivation contract +
  ranking-functional B-1 decision text (§3 frozen, user-decided 2026-09-19) + D2 replay outcome + §5 budget/K-literal replay +
  §4 gate family + §2 runner-delta design + §7 nine-scalar + IR-1..IR-5 boundary
  incl. IR-3 thresholds and IR-5 cap + arm-specific order-digest rule);
  main-thread acceptance owns the label; descriptive-only, no H2-verdict
  language; branch + H2 reading (§16) stays planning input, never an in-packet
  verdict; honest-scope statement (§0) repeated verbatim in the return.
- `P20R-R8`: Stage-A suites green on injected data with the zero-protected-open
  audit (counts 0/0 + DEV 0/1 at Stage-A close; 1M/2M/1.5M-VAL-DEV/HOLD
  non-access in every form); no commit/push; frozen dirs byte-untouched except
  the §12 manifest.
- `P20R-R9`: D2 replay (TRAIN-only FEASIBLE literal replayed from the P20N
  freeze, zero DEV reads; replay outcome frozen in `P20R_FREEZE.md`/STATUS
  BEFORE any DEV contact; MISMATCH → DEV untouched, no Stage-B request, point
  recorded blocked-by-replay; FEASIBLE-replay → literals frozen, packet
  proceeds) + new-order gate (derivation-program pin + new-B digest frozen in
  `P20R_FREEZE.md`/STATUS BEFORE any DEV contact; MISMATCH → DEV untouched, no
  Stage-B request). Gate-fired-by-replay → main-thread re-frame, never a
  Stage-B fallback.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs
`P20R-R1..R9` (stage-appropriately) complete with changed files + exact
commands/results + artifact inventory (incl. all reuse digest replays + new-B
order digest + program pin) + split open audit (counts + VAL-remainder-DEV +
VAL-DEV + HOLD + 1M + 2M separately); or (b) a concrete blocker with failing
command, exact error/traceback, attempted remedies, and the ONE decision needed
from the main thread. "Still incomplete" is not a completion report. The
operator never marks its own work accepted and never authorizes Stage B.

Blocker B-1 (RESOLVED 2026-09-19 by user decision — recorded, not a failure):
- B-1 new-B ranking functional: DECIDED — alt-table worst-first re-rank, full
  frozen text in §3 (Stage A SHALL NOT invent or alter it). The
  `NEXTBR_STOP_B1_RANKING_FUNCTIONAL_UNDECIDED` stop remains pre-registered
  only for a genuinely missing/contradictory freeze at Stage-A start (no
  derivation, no DEV contact, DEV stays 0/1).

## 16. Deferred options (not in this packet)

- New-order restoration (A fail → B exact on the single block, with or without
  B-maintain) → follow-up planning (deferred): trigger = genuine order-position
  restoration event under frozen α1 at frozen disclosure with the IR payload
  complete (descriptive positive of the proposal §2). Main thread re-evaluates
  with the full chain evidence in hand. This packet prejudges none of it and
  licenses no reliability claim.
- New-order negative (B restores NONE / B nowhere-exact-where-A-fails, with
  operational first errors remaining L2-layer at in-X sites) → next upstream
  single factor (deferred): trigger = genuine order-position negative on the
  fresh block (descriptive negative of the proposal §2). Only THEN does exactly
  ONE of (L2-side bounded search at the fixed point / second single
  construction form / further order refinement) become the next single factor on
  further new data by main-thread planning. Nothing is auto-triggered inside
  this packet.
- L1-layer return (operational first errors returning to L1-layer under either
  order) → prior/L1-side re-evaluation (deferred): trigger = L1-layer first
  errors on the VAL-remainder block (L1-side signal, not an order win). Main
  thread re-evaluates with the full chain evidence in hand.
- H2 adjudication → main-thread analysis AFTER P20R acceptance (deferred, never
  in-packet): trigger = accepted P20R IR-1..IR-5 payload tables (frozen-A vs
  new-B geometry contrast) joined with the P20N/P20O/P20Q archive. The H2a–H2e
  verdicts belong to that analysis; this packet supplies the pre-registered
  quantities and licenses no H2 verdict and no threshold.
- Disclosure-size planning, stub-41 follow-up, 2M HOLD-remainder use, closure of
  the 1M-HOLD thread: ALL continue deferred / out of scope, re-evaluated
  against P20R accepted evidence after acceptance.
- 1.5M VAL-remainder DEV 2044..2171 is CONSUMED by this packet regardless of
  outcome; stub 2172..2212 and 2M HOLD remainder 3556..3644 stay never-decoded.
  Any follow-up packet needs its own freeze, tag domain, and reviews.

(End of file)
