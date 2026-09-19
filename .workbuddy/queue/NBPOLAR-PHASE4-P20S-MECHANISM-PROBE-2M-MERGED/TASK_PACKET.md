# Phase 4-P20S — Maximum-information mechanism probe on the final merged 2M block (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage-A implementation + spike-order freeze with ZERO protected reads, Stage-B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read, decoder execution, or commit/push is authorized by this file.
- User decision 2026-09-20: D1-A authorized (2M same-session cross-split merge for the final block); D2 mechanism-probe form frozen.
- Predecessor: `NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M` terminal
  `TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (Stage-B single attempt SPENT 1/1; 1.5M VAL-remainder DEV 2044..2171 CONSUMED;
  A 0/1, B 0/1, C 0/1, D 0/1 — block-dominated, non-discriminating for the order
  factor per main-thread review §D1/D2; 1.5M remainder populations closed).
- Decision parent: `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md`
  (§D1/D2 + §5). D1-A authorizes exactly ONE merged 2M block
  (VAL remainder 2827..2915 + HOLD remainder head 3556..3594); D2 fixes its form as
  a maximum-information MECHANISM PROBE — three arms
  {frozen-order anchor, local-spike order candidate, true-L1 oracle}, IR-5
  truncation opened to the full-block 32768-position hazard series, judgment by
  geometry/coverage quantities only, NO recovery-rate reading, no threshold votes.
- Structural template: P20Q `TASK_PACKET.md` (§§2–16) for reuse/caps/recorder rigor;
  P20R `TASK_PACKET.md` §4 (ledger) + `P20R_FREEZE.md` (runner pattern, IR caps) for
  the thin-importer + new-order derivation pattern; P20Q `l2_alt_hold_ir_2m.py` +
  P20R `l2_order_position_1p5m.py` for the thin-import code pattern.
- Gate discipline: any standing long-horizon authorization does NOT collapse
  Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_2M_20260121_183657` (2M), scoring population first-and-only
  use of the merged 2M VAL-remainder + HOLD-remainder-head block (see §4). The 1M
  pool, the entire 1.5M session, 2M TRAIN-build, and all consumed 2M ranges are
  fail-closed against P20S DEV selection (see §4). 1.5M and 2M are never mixed.

## 0. Planner header (OpenSpec workflow)

- **Goal**: Record the maximum-information mechanism observation available on the
  final real-data block at N=32768 — three arms (α1 + frozen P20O 2M order anchor,
  α1 + new LOCAL-SPIKE order candidate at identical K, true-L1 oracle diagnostic),
  nine carried X09-R1/P20O/P20Q scalars + IR-1..IR-4 exactly as P20Q §7, IR-5
  UNCAPPED (full-block 32768-position hazard series per record in capped binary
  encoding), reusing ALL P20O frozen 2M artifacts byte-identical (zero new
  derivation reads) — and pre-register geometry/coverage judgment quantities that
  directly answer the H2e geometry question at full-block scope. n=1 recovery
  counts have no discriminating power (P20R demonstrated); this packet replaces
  counting with geometry.
- **Non-Goals**: No single-factor A/B recovery-count confirmation; no recovery-rate
  reading, no threshold votes, no FER/reliability/efficiency language; no new
  construction factor (α1 frozen on all arms); no K/disclosure-size change (B−A =
  0 by design; O discloses K2 only as the carried D-continuity); no floor-value
  change; no SCL/new kernel/model/schema; no (b) bounded search or (c) second
  construction form (both stay deferred); no K carried as an absolute from 1.5M or
  recomputed from alt-H; no derivation or sampling on real DEV frames at any stage;
  no calibration on DEV; no reuse of any consumed/closed range (full ledger §4);
  no cross-session pooling (1.5M × 2M forever forbidden); no H2 verdict inside this
  packet; no overwrite under `results/` or `comparison_bench/outputs_comparison/`;
  no commit/push.
- **Impact Scope**: New thin runner + focused injected tests + P20S OpenSpec delta
  (`specs/nbpolar-phase4-p20s/spec.md` + `tasks.md` P20S section, same umbrella
  change `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A freeze supplement
  (spike-order artifact + formula-id pin + dual digests + derivation-program pin,
  recorded alongside this packet) + implementation notes + Stage-B evidence root
  (5 JSON/JSONL/md files + 1 IR-5 manifest + 9 full-block `.bin` series). No change
  to `src/`, `experiments/`, `tools/`, P16 construction file, P20O accepted roots
  (`raw_prior_2m.npz`, `raw_prior_orders_2m.json`, `alt_l2_tables_2m.npz`),
  P20M/P20N accepted roots, P20Q/P20R accepted roots, X08/X09/X10 probe roots, H2
  run root, or `results/` / `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20S-R1..R9 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance.
  Geometry/coverage-descriptive label; `undetected` isolated; oracle never
  operational; outcomes recorded per record but explicitly NOT read as recovery
  rates; H2 decision explicitly deferred to main-thread analysis after acceptance.
- **Tasks**: (planner task list for coder agents) H1 verify + freeze P20O 2M
  artifact reuse (§3, R1); H2 freeze merged population/gates incl. the block
  -convention amendment (§4, R2); H3 freeze replayed caps from the carried 2M
  point (§5, R3); H4 freeze arm pins — frozen-A order + spike-B order (formula-id
  DECIDED 2026-09-20 F-median8) + derivation-program pin + oracle D-continuity
  (§§3/6, R4); H5 wire endpoints/taxonomy + mandatory nine scalars + IR-1..IR-4
  (P20Q-identical) + IR-5 UNCAPPED full-block binary series + manifest (§7, R5);
  H6 enforce one-shot budget/stop (§8, R6); H7 Stage-A suites green with zero-open
  audit (R8); H8 independent Pre-EXECUTE adjudication of reuse/spike-formula/
  K-literal/population/IR-5-encoding boundary (R7); H9 single authorized Stage-B
  attempt (R6/R7); H10 independent Pre-RESULT + acceptance (geometry quantities
  checked present, never decided in-packet).
- **Honest scope** (binding on proposal/design/packet/return language): a single
  merged-block (2M VAL-remainder tail + HOLD-remainder head) mechanism probe of one
  local-spike L2-order position rule under the frozen α1 construction at frozen
  disclosure with full-block hazard geometry recorded; descriptive geometry only;
  the merged DEV block is consumed by this packet; the HOLD tail 3595..3644 and all
  1.5M remainders stay untouched; no recovery claim, no H2 verdict; the H2 decision
  is analysis, not a block result.

## 1. Mission

With ZERO new protected derivation — the §3 P20O 2M TRAIN-derived raw prior + its
session-derived disclosure point + its session-derived worst-first orders + its α1
alt table, ALL reused read-only with digest replay (S2-i satisfied by same-session
reuse, never carried across sessions) — and the ONLY derivation being the
local-spike L2-order permutation computed off-protected-data from the reused
worktree prior by the frozen program under the frozen DECIDED 2026-09-20 F-median8 §3 formula with zero
sampling, zero genie, zero protected reads (S2-i preserved; DEV content opens only
at Stage B), and everything else fixed (α1 construction, K1/K2, floor 1e-15,
N=32768, greedy SC only, new P20S tag domains only), zero further tuning:

> On the ONE merged final 2M block, what full-block hazard geometry does each arm
> (frozen-order anchor, local-spike order, true-L1 oracle) record — spike-order
> coverage of disclosed-set mismatch positions, IR-1 tails under both orders,
> IR-4-style concentration at full-block scope — with the nine carried scalars and
> the uncapped IR-5 series preserved per record, and with per-record outcomes
> recorded but explicitly NOT read as recovery rates?

P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, P20K DEV 1152..1535 are
CONSUMED; TRAIN remainder 1536..1659 insufficient/closed; P20M VAL DEV 1660..2043
CONSUMED; P20N HOLD DEV 2213..2724 CONSUMED, HOLD remainder 2725..2766 never-used;
P20O 2M VAL DEV 2187..2826 CONSUMED (1/1 SPENT), VAL remainder 2827..2915
never-used until this packet; P20Q 2M HOLD DEV 2916..3555 CONSUMED (1/1 SPENT),
HOLD remainder 3556..3644 never-used until this packet; P20R 1.5M VAL-remainder DEV
2044..2171 CONSUMED (1/1 SPENT, block-dominated non-discriminating); P20L never
executed (zero consumption). The ENTIRE 1M pool is fail-closed. All branches after
this packet are deferred to §16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- Population constraint binds before factors (main-thread review §D1): the
  never-decoded ledger after P20R holds exactly four segments — 1.5M VAL stub
  2172..2212 (41), 1.5M HOLD remainder 2725..2766 (42), 2M VAL remainder 2827..2915
  (89), 2M HOLD remainder 3556..3644 (89) — totalling 261 frames / 66816 pairs, i.e.
  ZERO complete N=32768 blocks under the standing "block = 128 consecutive frames
  within one split" convention. The two 2M segments jointly hold 178 frames = 1
  complete block + a 50-frame stub. Session-difficulty evidence (§D1 review:
  true-L1 oracle ceiling ~12.5% on 1.5M vs ~70% on 2M across P20M/P20N/P20R vs
  P20O/P20Q) forces the final block onto 2M; the 1.5M remainders (83 frames) are
  low-information and stay never-decoded.
- D1-A block-convention amendment (user decision 2026-09-20, frozen here, not
  re-argued): the standing block convention is amended FOR THIS FINAL BLOCK ONLY —
  the merged block = 2M VAL-remainder tail `2827..2915` (89 frames) FOLLOWED BY 2M
  HOLD-remainder head `3556..3594` (first 39 of 3556..3644), in that order, forming
  exactly 128 frames = 1 block at N=32768 (32768 pairs, 256 rows/frame). Merge
  justification (written once, gated thereafter): same session
  `type2_2M_20260121_183657`; BOTH segments non-build (build ⊂ TRAIN 0..2186);
  BOTH unconsumed (never decoded, never tuned on, never scored); S2-i satisfied
  (session's own TRAIN-derived artifacts reused read-only, never carried across
  sessions); S2-ii holds (merged DEV disjoint from build frames by split
  identity). The exact 128-frame list rule (VAL-segment-then-HOLD-segment) is
  enforced by gate (g). This amendment sets NO precedent for cross-session pooling:
  1.5M × 2M mixing stays forever forbidden.
- D2 mechanism-probe form (user decision 2026-09-20, frozen here): n=1 recovery
  counts have no discriminating power (P20R demonstrated: anchor and both oracles
  non-exact on a block the current working point cannot recover). The final block
  is therefore a maximum-information MECHANISM PROBE, not a confirmation: arms =
  {α1 + frozen-order anchor, α1 + local-spike-order candidate, true-L1 oracle};
  IR-5's 4096 truncation is opened to store the full-block 32768-position hazard
  series (the direct answer to H2e's geometry question — until now only truncated
  range + top-16 existed, which IS the H2e "incoherent" evidence gap); judgment =
  geometry/coverage quantities only, NO recovery-rate reading, no threshold votes.
- Factor content (frozen ordering, (a) only): (a) order/position priority with the
  LOCAL-SPIKE derivation criterion — H2e's pooled IR-4 in-prefix 66/320 = 0.20625
  is the unique direct position-set number, and H2a-REFUTED forbids mean-hazard
  ranking as the derivation criterion (global average-metric ordering of arms is
  refuted; the spike rule must target LOCAL excess, §3). (b) bounded search and
  (c) second construction stay deferred (§16).
- Reuse-vs-derive stance (frozen, not re-argued): re-deriving prior/orders/alt in
  P20S would cost new counts opens and new sampling for zero new information;
  reusing the frozen P20O 2M artifacts read-only with digest replay preserves S2-i
  (same-session hypotheses) and S2-ii (build ⊂ TRAIN vs merged DEV disjoint, §4).
  The α1 RULE stays frozen (alpha 1.0). The ONLY derivation is the alternate spike
  L2-order permutation from the reused worktree prior arrays by the frozen program
  under the frozen DECIDED 2026-09-20 F-median8 §3 formula (§3). Fixed disclosure WITHIN the packet after
  the Stage-A freeze (B−A = 0 by design); the SET-delta between the A and B L2
  position lists IS the probed factor, recorded byte-exact.
- Alternatives rejected in writing: (a) re-derive prior/alt/orders from protected
  counts — second counts open + second sampling, forbidden; (b) any α other than
  1, any second construction, any construction sweep — second factor, forbidden;
  (c) L2-side bounded search now — deferred (b); (d) second single construction
  form now — deferred (c); (e) λ anywhere — X08-falsified, forbidden; (f) floor
  change — H3/H2d exonerated, forbidden; (g) K change or budget recompute from
  alt-H or from 1.5M — violates fixed disclosure and same-session reuse (S2-i);
  alt-H descriptive only (§3); (h) SCL/list/belief decoder — decoder change; SCL
  unlock runs on synthetic X11 (D3), never on this block; (i) consume the HOLD tail
  3595..3644, any 1.5M remainder, any consumed population, or any 1M range —
  forbidden; (j) cross-session pooling — forbidden; (k) freeze any of the nine
  scalars or IR-1..IR-4 as absent — forbidden; (l) single-factor A/B
  recovery-count confirmation on this block — explicitly replaced by the mechanism
  probe (D2), forbidden as a reading of this packet's outcomes.
- Session inventory (no new protected access by this planner; provenance from the
  split manifest `nbldpc_v25_split_manifest_v1` read as JSON metadata only, plus
  P20M/N/O/Q/R §§2/4): 2M TRAIN 2187/559872 + VAL 729/186624 + HOLD 729/186624
  (256 rows/frame; see §4 for frame bases). 1.5M TRAIN 1660/424960 + VAL
  553/141568 + HOLD 554/141824. Geometric position: P20S merged DEV is the LAST
  89 VAL-remainder frames 2827..2915 followed by the FIRST 39 HOLD-remainder frames
  3556..3594 (ONE full block: 128×256 = 32768 pairs); HOLD tail 3595..3644 (50
  frames / 12800 pairs) never-decoded under this packet.
- Runner-delta design choice (frozen; the §10 "design.md" decision): a THIN NEW
  runner module importing the accepted P20Q `l2_alt_hold_ir_2m` runner read-only
  (which itself thin-imports accepted `l2_alt_maintain_2m` → accepted
  `raw_prior_val_1p5m`: population pattern, TRAIN-exclusion gate family,
  order-file + `--order-digest` mechanism with zero Stage-B sampling, P20A
  endpoint/taxonomy/recount/resource machinery, `_l2_hazard_diagnostics` +
  `_ir_hazard_diagnostics` code points with nine scalars + IR-1..IR-5). Exact delta
  list, nothing else: (d1) population → merged 2M DEV (§4; all other sessions/
  ranges excluded as consumed or never-decoded); (d2) prior/orders/alt sources →
  the P20O frozen 2M files reused read-only behind replayed `reuse_prior_identity`
  + `reuse_alt_identity` + `reuse_order_freeze_A` gates (§3; worktree-file reads
  only, never the V25 counts NPZ); (d3) K pins → the P20O-derived
  (K_total,K1,K2)=(7080,334,6746) replayed as literals (never recomputed, never
  recarried from 1.5M, never from alt-H); (d4) orders → DUAL: frozen-A order file
  (`raw_prior_orders_2m.json`, byte-identical on arms A/O) + Stage-A spike order
  file (`new_spike_order_2m.json`, byte-identical on arm B), each digest-gated,
  each disclosing first-K1 / first-K2 prefixes at identical sizes (§§3/6);
  (d5) arms A/B/O per §6 (same K on A/B, carried K2 on O; same α1 tables; order
  SET is the only delta between A and B); (d6) new P20S tag domain (§6);
  (d7) spike-order derivation program (worktree-prior-only, deterministic, zero
  sampling/genie, zero protected reads, frozen DECIDED 2026-09-20 F-median8 §3 formula-id) + dual
  order-identity gates + derivation-program pin (§§3/9); (d8) merged-DEV
  population + DEV∩build-frames disjointness declared inside the TRAIN-exclusion
  gate (§4); (d9) IR-5 UNCAPPED full-block binary series + manifest (§7) replacing
  the P20Q 4096 cap, same truth-isolation boundary. No SC/transform/
  floor-semantics/tag-semantics change; no second factor. The alternative (edit
  any accepted module) is rejected: it would touch an accepted evidence-producing
  file; the thin importer leaves every accepted file byte-identical.

## 3. Reuse freeze + spike-order derivation stance (normative — P20O 2M artifacts reused read-only, zero Stage-A protected reads; ONE new permutation by the frozen program under the frozen DECIDED 2026-09-20 F-median8 formula)

- Counts source: NONE. Stage A performs ZERO protected opens (counts 0/0 at
  Stage-A close; the V25 counts NPZ is NEVER opened/statted/listed at any stage of
  this packet). The §3 P20O derivation inputs are not re-read. FORBIDDEN reuse
  inputs: any 1M split, any 1.5M split, 2M DEV/HOLD-DEV frames for derivation,
  Model-F CAL artifact.
- Reused products (paths under the P20O queue dir
  `NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION`, read-only; Stage A verifies by
  worktree-file digest recomputation ONLY — canonical recipe for the prior,
  file-bytes sha256 for orders/alt; zero parquet/NPZ protected opens):
  (p1) `raw_prior_2m.npz` — canonical digest
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587` (recipe
  `per_session_calibration.canonical_prior_digest`: sorted-key `key + shape +
  dtype + C-order bytes` sha256); keys exactly `counts_ab, f_raw, p1, p2, p_b,
  lambda_star, floor_value, h1, h2, h_total` (`lambda_star` `0.0`;
  `floor_value` `1e-15`); session H literals
  `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477` recomputed via
  accepted `target_construction.entropy_bits` within 1e-12 (never hand-filled;
  `beta_eff_empirical` never hand-filled per AGENTS.md §5.5); `p_b` cross-check
  pinned.
  (p2) `raw_prior_orders_2m.json` — file-bytes sha256
  `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; full L1+L2
  worst-first permutations, K1 334 / K2 6746 / K_total 7080. This is the FROZEN-A
  order (anchor; arms A/O).
  (p3) `alt_l2_tables_2m.npz` — file-bytes sha256
  `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`; keys exactly
  `counts_ab, f_alt, p1, p2_alt, alpha, floor_value, h1_inc, h2_alt,
  h_total_alt` (`alpha` `1.0`; `floor_value` `1e-15`); `p1` = the P20O 2M
  incumbent `p1` (Stage A asserts equality within 1e-12 elementwise); descriptive
  alt-H `1.3245794596410305 / 1.3502415084837889` (never a budget input).
- Budget/split replay (S2-i satisfied by same-session reuse): `K_total = 7080`
  via the literal `1.3*32768*0.8325627219737477-64 over 5, floored, clipped
  [0,65536]` (P20O §3 display, replayed never recomputed); `(K1,K2) =
  (334,6746)` replayed never recarried from 1.5M (331/6689/7020 never enter this
  packet); NO recomputation from alt-H; NO hand-fill; NO new sampling (Stage-A
  genie calls 0, Stage-B sampling 0).
- LOCAL-SPIKE ORDER FORMULA — DECIDED 2026-09-20 (F-median8). FROZEN functional
  (verbatim user decision 2026-09-20, feeds P20S arm B + X14 Q2 alignment):
  "F-median8: score[i] = h[i] − median(h over the R=8 clipped natural neighborhood of i), where h[i] is the frozen arm-table hazard atom (-log2 true-cell mass, same recipe as the IR recorders); rank all 32768 L2 positions by descending score; take the first K2=6746 positions as arm B's disclosed L2 set; tie-break by ascending natural block coordinate; deterministic, zero sampling, zero genie calls, zero protected reads (inputs: worktree `raw_prior_2m.npz` arrays only); arm A's set stays the frozen incumbent-order first-K2 prefix."
  Stage A SHALL derive under this frozen formula (no re-ask, no alteration; no
  derivation, no DEV contact, DEV stays 0/1 only if the §3 formula text below is
  missing/contradictory). Frozen R=8 window convention; deterministic,
  window-parameterized, zero sampling/genie/protected reads; inputs worktree
  `raw_prior_2m.npz` arrays ONLY; L1 carried frozen on all arms; first-K2=6746
  disclosed; tie-break ascending natural block coordinate; provenance +
  zero-sampling attestation in the spike file. Static hazard vector: `h[j] = -log2 p2_alt[U1hard[b],b,u2]` at cell `j = b*32+u2`
  (C-order flatten of the (1024,32) table), `U1hard[b] = argmax_u1 p1[u1,b]`
  (hard-L1 candidate from incumbent `p1`, ties to smallest `u1`), `p2_alt`
  recomputed from the worktree `counts_ab` by the frozen α=1 rule (unit
  pseudocount + 1e-15 floor + column renormalize + accepted `derive_p2`),
  bit-exact vs the frozen alt file. The same formula also feeds the X11 synthetic
  probe (D3), hence full determinism + window-parameterization is mandatory.
  Historical context (pre-decision candidates, NOT alternatives — F-median8 above
  is the sole frozen functional):
  - F-median8 (DECIDED 2026-09-20 — the frozen functional above): `score[i] = h[i] − median{ h[j] : j ∈ [i−8,i+8] ∩
    [0,32767] }`; disclosed set = first 6746 positions by descending score.
    Decision rationale: median is robust to the heavy-tail/zero-count
    structure the empirical channel carries (D3 context); it targets LOCAL excess
    rather than any global average, satisfying the H2a-REFUTED constraint; single
    frozen scale (R=8, the carried nbhd convention), no extra parameter.
  - F-mean8: identical with local MEAN instead of median. REJECTED by the
    2026-09-20 decision (retained as historical context only): reintroduces
    mean-based ranking (the H2a-refuted spirit) inside the window.
  - F-multi8_32: `score[i] = max( h[i]−median(W8(i)), h[i]−median(W32(i)) )`
    with `W_R(i) = [i−R,i+R] ∩ [0,32767]`; disclosed set = first 6746 by
    descending score. REJECTED by the 2026-09-20 decision (retained as
    historical context only): adds a second scale parameter with no
    discriminating evidence available at n=1.
- Spike-order derivation contract (once the formula-id is chosen): the alternate
  L2-order permutation SHALL be computed off-protected-data from the reused
  worktree prior arrays ONLY by the frozen program
  (`l2_mechanism_probe_2m.py:derive_spike_l2_order`, deterministic, pinned with
  module path + function + formula-id + argv). Derivation opens zero protected
  content (worktree-file reads only); performs zero sampling, zero genie calls,
  zero derivation seeds (sampling 0 at every stage); emits a byte-exact
  length-32768 L2 permutation plus the carried L1 prefix unchanged; discloses
  first-K2 positions at identical size K2=6746 (size-delta zero; SET-delta IS the
  probed factor). Stage-A product identity: path
  `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/new_spike_order_2m.json`,
  format JSON holding the full L1 (carried frozen) + new-L2 permutations plus
  provenance (reused-prior digest + formula-id + program pin + zero-sampling
  attestation), file-bytes sha256 `<FROZEN_AT_STAGE_A>` with freeze rule = derive
  once in Stage A, pin alongside this packet, gate on equality thereafter. All
  derivation CONTRACT constraints above (inputs, determinism, zero
  sampling/reads, length, K2 size, provenance) are frozen here under the
  DECIDED 2026-09-20 F-median8 formula.
- D1/D2 status: no feasibility recompute is required for a pure order delta at
  frozen K (disclosure sizes unchanged; §5 caps replay). Stage A replays the P20O
  D1 literals (`ce_alt` 0.8850983725781965, `ce_incumbent` 0.8069006731253678,
  ceilings 33794/35464, `alt_ideal_length_bits` 29002.90347264234) and D2 FEASIBLE
  outcome (margin `4791.09652735766` bits, TRAIN-only, zero merged-DEV reads)
  BEFORE any DEV contact; a replay mismatch BLOCKS before any DEV open (DEV read
  stays 0/1) and no Stage-B authorization is requested.
- Stage B loads the frozen files read-only behind the `reuse_prior_identity` +
  `reuse_alt_identity` + `reuse_order_freeze_A` + `spike_order_identity_B` +
  `order_derivation_program_identity` gates (digests + lambda-0.0/alpha-1.0/floor
  pins + exact key sets + H-literal recomputation within 1e-12 + `p_b` cross-check
  + `p1`-equality recheck within 1e-12 + K-literal replay + formula-id pin, or
  BLOCKED before any sampling and before any SC call).

## 4. Population and closed/consumed-data rule (normative)

- The following are CONSUMED/CLOSED and SHALL NOT supply P20S blocks: the three
  P18/P19 HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599), P20C/P20E/
  P20F DEV blocks (1M 0..383 / 384..767 / 768..1151, remainder 1152..1199 never
  used), P20H DEV (1.5M TRAIN 0..383), P20I DEV (384..767), P20J DEV (768..1151),
  P20K DEV (1152..1535, remainder 1536..1659 insufficient/closed), P20M VAL DEV
  (1.5M VAL 1660..2043), 1.5M VAL stub 2172..2212 (never-used), P20N HOLD DEV
  (1.5M HOLD 2213..2724), HOLD remainder 2725..2766 (never-used), P20O 2M TRAIN-build
  0..2186 as DEV, P20O 2M VAL DEV 2187..2826 (CONSUMED 1/1), P20Q 2M HOLD DEV
  2916..3555 (CONSUMED 1/1), P20R 1.5M VAL-remainder DEV 2044..2171 (CONSUMED 1/1);
  P20L never executed (zero consumption). The ENTIRE 1M pool and the ENTIRE 1.5M
  session are fail-closed against P20S DEV selection (cross-file gate). 1.5M TRAIN
  0..1659, 1.5M VAL 1660..2212, 1.5M HOLD 2213..2766 SHALL NOT be
  opened/statted/listed/read under this packet in any form. 2M TRAIN 0..2186 SHALL
  NOT supply P20S blocks (build frames). 2M VAL DEV 2187..2826 and 2M HOLD DEV
  2916..3555 SHALL NOT be opened/statted/listed/read under this packet in any form.
- Merged-block-first-and-only-use justification (same canonical TRAIN→held-out
  separation as P20M §4, frozen, not re-argued in Stage A/B): NEITHER merged
  segment has ever been decoded, tuned on, or scored by any EXECUTED NB-Polar
  packet; 2M TRAIN supplies the session hypotheses (raw prior + alt table both
  from TRAIN-fitted counts, spike order from the same worktree prior, never from
  merged-DEV frames); using the merged block as a one-shot scoring population is
  declared once, consumed once, never tuned, never returned to a validation role.
  The HOLD tail stays undecoded.
- Stage B runs on the DECLARED population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet` ONLY (provenance pin frozen in Stage A by manifest cross-check; mismatch blocks; planner performed zero opens/stats/listings) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 2M TRAIN 2187/559872 + VAL 729/186624 + HOLD 729/186624 (JSON-metadata read only) |
| construction/order-derivation input | §3 worktree `counts_ab`/prior arrays ONLY (TRAIN-fitted; never a merged-DEV frame) |
| merged DEV frame rule | VAL-remainder tail `2827..2915` (89 frames) FOLLOWED BY HOLD-remainder head `3556..3594` (first 39 of 3556..3644), in (frame_id, pair_idx) order within each segment, VAL-segment-then-HOLD-segment concatenation (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed; manifest-count arithmetic: TRAIN 2187 [0..2186] + VAL 729 [2187..2915] = VAL-remainder tail 2827..2915; HOLD base 2916 + P20Q DEV 640 = HOLD remainder 3556..3644) |
| merged DEV blocks (N=32768) | ONE block: `2827..2915` + `3556..3594` (128 frames; 32768 pairs = ONE full block) |
| unused tail | HOLD frames `3595..3644` (50 frames / 12800 pairs) recorded never used — counted, never decoded |
| 1.5M remainders | VAL stub `2172..2212` (41 frames / 10496 pairs) + HOLD remainder `2725..2766` (42 frames / 10752 pairs) recorded never used — counted, never decoded, never contacted beyond counting |
| build-frames disjointness (S2-ii) | counts/build frames ⊂ 2M TRAIN `0..2186` (P20O §3 input = 2M TRAIN counts ONLY); merged DEV = VAL `2827..2915` + HOLD `3556..3594`; disjoint by split identity; declared frame sets above; the TRAIN-exclusion gate refuses any overlap before any protected content open |
| consumed-1M exclusions | entire 1M pool (any split/subrange) — overlap refuses before any protected content open |
| consumed-1.5M exclusions | all 1.5M TRAIN `0..1659` + VAL `1660..2212` + HOLD `2213..2766` — overlap refuses before any protected content open |
| consumed-2M exclusions | 2M TRAIN `0..2186` as DEV; 2M VAL DEV `2187..2826`; 2M HOLD DEV `2916..3555` — all in any form |
| block count | 1 at N=32768 |
| tag domains | new P20S domain (§6) |

- Fail-closed gate family (frozen in the runner, order (a)→(g), cross-file first):
  (a) CROSS-FILE 2M — merged DEV content-open path + stat-size/sha pin must equal
  the 2M session identity; any 1M or 1.5M path or digest mismatch refuses before
  any SC call (frame integers alone are never identity); (b) INTRA-FILE
  DUAL-SEGMENT containment — the VAL segment must lie wholly inside VAL
  2187..2915 with zero TRAIN/VAL-DEV overlap AND the HOLD segment wholly inside
  HOLD 2916..3644 with zero HOLD-DEV overlap, else refuse before any protected
  content open; (c) CONSUMED-1M EXCLUSION — entire 1M pool; (d) CONSUMED-1.5M
  EXCLUSION — all 1.5M ranges above; (e) CONSUMED-2M EXCLUSION — 2M TRAIN-as-DEV
  + 2M VAL DEV + 2M HOLD DEV incl. the DEV∩build-frames disjointness declaration:
  merged DEV vs build ⊂ 2M-TRAIN with the frame sets above (S2-ii);
  (f) REUSE-PRIOR/ALT/FROZEN-ORDER/K-LITERAL + SPIKE-DERIVATION-PROGRAM — §3
  canonical/file-bytes digests + lambda-0.0/alpha-1.0/floor pins + exact key sets
  + H-literal recomputation within 1e-12 + `p_b` cross-check + `p1`-equality
  within 1e-12 + budget-literal replay (S2-i) + frozen-A order-file digest must
  match AND the spike derivation-program pin (module + function + formula-id +
  argv + zero-sampling attestation) must match, else refuse before any SC call;
  (g) MERGED-FRAME-SET-IDENTITY + ORDER-POSITION-IDENTITY + TAG-DOMAIN — the exact
  128-frame list rule (frames 2827..2915 then 3556..3594, in that order) + the §6
  order triple (frozen-A digest on A/O, spike digest on B, K1/K2 literals
  replaying exactly, `--source 2M` vocabulary) + P20S tag-domain pins must match,
  else refuse before any SC call.

## 5. Preregistered disclosure point (normative — P20O-session-derived, replayed at Stage A)

- K rule (S2-i satisfied by same-session reuse): `(K_total,K1,K2)` =
  `(7080,334,6746)` (P20O Stage-A derived from the §3 2M session H via the §3
  budget+split rules; replayed as literals in Stage A with the
  `1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536]`
  display; never carried as an absolute from 1.5M 331/6689/7020). NO recomputation
  from alt-H (the §3 alt-H literals are descriptive only); NO hand-fill; NO new
  sampling.
- Caps PREREGISTERED at Stage A from the carried point (rule
  `5*(K1+K2)+64` key-dependent bits/block, `10*32768+63 = 327743` public
  bits/tag, one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_anchor_frozen_order (operational) | 334 | 6746 | 35464 = 5*7080+64 | 327743 |
| B_spike_local_order (probe candidate) | same K1 | same K2 | same as A (Δ vs A exactly 0) | 327743 |
| O_true_l1_oracle (diagnostic) | 0 | 6746 | 33794 = 5*6746+64 | 327743 |

- Planned totals (replayed at Stage A from the carried integers):
  key-dependent `2*35464 + 33794 = 104722` bits; public `3*327743 = 983229`
  bits. B-vs-A key-bit delta is exactly 0 (order factor carries ZERO
  disclosure-size delta by design).
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate
  BLOCKS. Per-record fields pin the session point (`prior_source` raw/2M-reuse,
  `k1/k2/k_total`, `budget_literal_replayed`, `alt_digest`,
  `l1_order_digest`, `l2_order_digest` (arm-specific: frozen-A on A/O, spike on
  B), `floor_hit_rate`).

## 6. Arms (frozen; order is the ONLY delta between operational arms; oracle is the P20O/P20Q-D continuity)

- `A_anchor_frozen_order`: frozen greedy SC with incumbent `p1` + §3 `p2_alt`
  (α1), FROZEN P20O L1+L2 order prefixes (first-334 / first-6746 of digest
  `b2255449…da8acf3bd0906`) at carried K1/K2 (operational anchor = P20O/P20Q
  construction + order continuity; 2 SC + 1 P20S-domain tag per block).
- `B_spike_local_order`: frozen greedy SC with incumbent `p1` + §3 `p2_alt`
  (α1, byte-identical tables to A), SPIKE L2-order positions (first-6746 of the
  Stage-A `new_spike_order_2m.json`, digest `<FROZEN_AT_STAGE_A>`) with the SAME
  carried L1 order and SAME K1/K2 (probe candidate; 2 SC + 1 tag per block).
  Construction, K sizes, floor, decoder all byte-identical to A; the
  disclosed-L2 SET delta IS the probed factor.
- `O_true_l1_oracle`: true-L1-conditioned diagnostic with `p2_alt` + FROZEN order
  at carried K2 (provenance ORACLE, deployable=false, excluded from every
  operational aggregate; never a correction result; 1 SC + 1 P20S-domain tag per
  block). Order/table pin (default, frozen here): FROZEN order + alt-L2 tables —
  the P20O/P20Q arm-D continuity. Rationale (frozen, not re-argued): D is the
  diagnostic that tracked B's restoration on both 2M segments (3/5, 4/5) and hence
  carries the oracle ceiling onto the merged population; C (incumbent oracle, 0/5
  twice) carries no ceiling information and is dropped to fit the 3-record probe
  budget. Order-factor attribution lives in the A-vs-B operational pair ONLY; O
  never enters any operational aggregate.
- No other arms. Block-major (A, B, O) on the single merged DEV block;
  checkpoint after every (arm, block) record; 3 records total. P16 construction
  file unchanged (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` carried
  read-only); kernel/representation/transform/SC arithmetic unchanged; greedy SC
  only; no SCL/new kernel/model/schema. Stage A performs ZERO sampling; Stage B
  performs pure merged-DEV scoring (5 SC + 3 tags) with ZERO sampling — Stage-B
  TRAIN genie calls pinned at 0, Stage-A genie calls pinned at 0 (reuse +
  deterministic permutation need no derivation sampling).
- Tag domain (new P20S): master 2026092360, prefix
  `nbpolar-p20s-mechanism-probe-2m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from ALL
  of P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K/P20M/P20N/P20O/
  P20Q/P20R (incl. masters 2026092280/2026092300/2026092310/2026092330/2026092340
  and all test/derivation seeds). Stage A verifies by repo grep that master
  2026092360 and focused-test seeds `2026092361..2026092367` appear in no tracked
  file outside the P20S runner/tests/packet/spec documents (planner pre-checked
  202609236* absent; zero protected access).
- No derivation seeds (deterministic permutation; zero sampling at any stage).
  Disjointness holds by the grep rule above. Stage B takes NO derivation seeds
  and performs no sampling.
- L2 disclosed-set rule (single-factor guard): arms A/O disclose the first-6746
  positions of the SAME frozen 2M order file (digest-gated
  `b2255449…da8acf3bd0906`); arm B discloses the first-6746 positions of the SAME
  spike order file (digest-gated `<FROZEN_AT_STAGE_A>`); the L1 set is the
  first-334 of the SAME frozen P20O L1 order on all arms. Positions are fixed by
  the frozen files, never selected on closed blocks, consumed ranges, or DEV
  data. K sizes frozen identical on A/B; the SET-delta between the A and B L2
  lists is recorded byte-exact (symmetric difference + rank-displacement table,
  descriptive only).

## 7. Thresholds, endpoints, and mandatory instrumentation (geometry/coverage only — no recovery-rate reading)

- Outcome label `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE` iff
  ALL integrity gates (§9) hold — regardless of per-record outcomes. ANY outcome
  pattern is COMPLETE when integrity holds.
- Choice + justification: geometry/coverage-descriptive (no recovery/FER/Wilson
  threshold). This is the maximum-information probe of the final block at frozen
  α1 and frozen disclosure with the full-block hazard series preserved — n=1
  counts cannot discriminate arms (P20R), so there is no empirical basis for ANY
  count threshold here. A 62/64-class gate would be an invented threshold,
  explicitly forbidden. Branch and H2 decisions belong to main-thread analysis
  AFTER acceptance (§16).
- NO recovery-rate reading, NO threshold votes, NO FER / superiority /
  qualification / promotion claim. Outcomes (`exact` vs non-exact) are recorded
  per record for completeness but explicitly NOT read as recovery rates. The
  pre-registered judgment quantities are geometry/coverage ONLY (see below); any
  (or no) outcome pattern counts as COMPLETE. No efficiency language anywhere (CE
  ratios never called efficiency).
- Status taxonomy frozen: `exact` (tag-verified: outcome exact AND tag_pass AND
  label_match) vs `verify_failed`, `undetected` isolated (never success),
  plus `decode_failed` / `nonfinite` / `resource_abort` via the P20A path. P20A
  four-endpoint separation (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` /
  `pair_exact`) per record. First-error coordinate/layer rows (natural block
  symbol index, settled X09-R1 D4) recorded per record. Per-record floor-hit
  fields (`floor_hits`, `floor_hit_rate`) complete per record (S2 reporting).
- Carried X09-R1/P20O instrumentation (ALL NINE per-record SCALARS, scalar fields
  intact, arm-specific order digest): `l2_order_digest` (= frozen-A digest on A/O
  records, spike digest on B records, gated), `l2_prefix_len` (= session K2 6746
  on every record, gated), `l2_fail_in_prefix`, `l2_fail_hazard_bits`,
  `l2_fail_nbhd_mean_bits` (frozen radius R=8 window, clipped to the block),
  `l2_prefix_hazard_mean_bits`, `l2_fail_nbhd_floor_frac`, `l2_prefix_floor_frac`,
  `l2_fail_in_prefix_u_domain` (frozen PRESENT). Semantics identical to P20Q §7
  (true cells under the record's own arm table; failing fields null unless
  `first_error_layer == L2`; prefix-wide means on every completed record; hazards
  = `-log2` arm-table mass at each position's true `(U1_cond, B, U2)` cell with
  `U1_cond` = hard-L1 candidate on A/B, true high on O).
- Mandatory IR-1..IR-4 (ALL FROZEN PRESENT, same caps/formulas as P20Q §7; Stage A
  pins exact formulas with injected vectors; never post-hoc):
  - IR-1 per-record 64-bin log-spaced hazard histograms {prefix, outside} using
    true cells (~1 KB/record): fields `ir1_hist_edges_bits` (65 float64,
    log-spaced over hazard-bits, frozen formula), `ir1_hist_prefix_counts`
    (64 int), `ir1_hist_outside_counts` (64 int). Split by disclosed L2 prefix
    membership (X-domain, first-6746 of the RECORD'S OWN order file — frozen-A on
    A/O, spike on B); hazards under the record's own arm table. Every completed
    record (never null).
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
    using true cells under the record's OWN order; every completed record, never
    null).
  - IR-4 top-k hazardous positions with ranks (k≤16, frozen k=16): fields
    `ir4_topk_coords` (16 int, natural block symbol indices),
    `ir4_topk_hazard_bits` (16 float), `ir4_topk_in_prefix` (16 bool/int,
    X-domain prefix flags under the record's OWN order), `ir4_topk_ranks`
    (16 int, 1-based hazard ranks). Hazard-order listing only; error-coordinate
    join is post-hoc. Every completed record (never null; N=32768 always fills
    16).
- IR-5 UNCAPPED — full-block 32768-position series preserved (the D2 opening of
  the P20Q 4096 cap). Per record, EXACTLY three binary little-endian series +
  manifest linkage (NO text-JSON float dumps; NO `*.npz`/`*.npy`/`*.parquet`,
  which are git-ignored; encoding satisfies the D4 evidence-size standing rule,
  ≤ ~2 MB per committed file):
  - `<arm>_hazard_bits_f32le.bin`: float32 LE [32768] = 131072 B — true-cell
    hazard bits in natural block order under the record's own arm table
    (`U1_cond` = hard-L1 candidate on A/B, true high on O; same hazard
    definition as the nine scalars/IR recorders).
  - `<arm>_inprefix_u8.bin`: uint8 [32768] = 32768 B — X-domain disclosed-prefix
    flags under the record's OWN order (frozen-A on A/O, spike on B).
  - `<arm>_inu_u8.bin`: uint8 [32768] = 32768 B — U-domain flags under the
    record's own arm table (the full-block form of the carried ninth scalar).
  - `ir5_full_manifest.json`: per-file sha256 + shape + dtype + endianness +
    order-identity (frozen-A vs spike file digest) + record linkage + format
    version (frozen `ir5full-v1`); digests cross-checked by the
    `ir5_full_manifest_identity` gate.
  - Size budget (frozen): ~128 KiB hazard series + 32 KiB + 32 KiB = ~192 KiB per
    record; 3 records ≈ ~576 KiB; full Stage-B root ≤ ~1.5 MB; every committed
    file ≤ ~2 MB with the largest single file at 128 KiB. The JSONL records carry
    IR-5 manifest REFERENCES (file names + digests), never inline float arrays.
  - Writer code point (frozen): successor module `l2_mechanism_probe_2m.py`,
    function `_ir5_full_block_writer(*, block, view, p2_arm, counts_arr,
    l2_order, k2, ...)` — called post-decode (after tag scoring) from the
    successor's `_operational_record` / `_control_record` equivalents alongside
    the nine carried scalars and the IR-1..IR-4 recorder (the P20Q
    `_ir_hazard_diagnostics` code point is the carried-over callsite pattern).
  - Truth-isolation boundary (normative): block truth (high/low/bob) and the arm
    tables enter the IR writers for RECORDING ONLY after all SC calls for the
    record have completed; outputs are written into the record dict / `.bin`
    files and never passed to `run_operational_block`,
    `run_oracle_control_block`, `_decode_layer`, `build_p1_metrics`,
    `gather_p2_metrics`, or any disclosure/order decision. A focused
    truth-isolation sentinel test pins this boundary (mutating truth changes no
    metric/decision input).
- Judgment form (pre-registered geometry/coverage quantities ONLY; the H2 DECISION
  stays main-thread analysis after acceptance — NO outcome asserted here): the
  accepted run must supply (i) full-block hazard series tables (per-record
  full-32768 mean/tail mass under the record's own order, from the uncapped IR-5
  bins); (ii) spike-order coverage of disclosed-set mismatch positions — the
  byte-exact A-vs-B symmetric-difference set characterized by its hazard-rank
  distribution under each order (purely positional; NOT an outcome comparison);
  (iii) IR-1 tails under both orders (prefix vs outside tail-mass contrast A vs
  B); (iv) IR-4-style concentration at full-block scope (in-prefix fractions over
  top-128 / top-1024 hazard ranks from the uncapped series, per record's own
  order); plus the nine carried scalars (with arm-specific order digests) for
  P20N/P20O/P20Q/P20R continuity and the byte-exact A-vs-B set-delta table. These
  quantities inform H2a–H2e at full-block scope; they are not recovery rates, not
  thresholds, not pass/fail votes.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized
  execution; no rerun, no seed change, no prior/budget/order/construction tuning
  after preregistration. Execution-error rerun only as a recorded repeat of the
  identical freeze, never as tuning. P20H–P20R spent attempts do NOT transfer
  (independent packet).
- Reads (split-counted): counts-calibration opens 0/0 at every stage (reuse; the
  V25 counts NPZ is never opened/statted/listed) + merged-DEV open 1/1 reserved
  for Stage B (parquet, consumed at first merged-DEV content open). 1M reads 0;
  1.5M reads 0; 2M non-DEV reads 0 (HOLD tail + all 1.5M remainders counted
  never-decoded, never contacted beyond counting). Any reopen, new
  calibration/derivation on real frames, real-frame use for derivation, or DEV
  refit is forbidden. Prior-file/alt-file/order-file loads and the deterministic
  spike-order derivation are worktree-file reads, not protected opens.
- SC/tag/genie budget: Stage-A genie 0 + Stage-B pure merged-DEV 5 SC (1 block ×
  (2+2+1)) + 3 tags + 3 records with ZERO sampling at every stage (Stage-A
  sampling 0, Stage-B sampling 0); derived per-record recomputation must equal
  counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  accounting; abort is BLOCKED, never success. Wall/RSS ceilings frozen in the
  Stage-A freeze supplement (P20R-class reference at the smaller 5-SC / 3-tag
  budget; external timeout 1200 s + virtual/RSS caps 2 GiB + single thread
  frozen).
- Strategy stop rules binding: no tuning on closed blocks or the new merged DEV
  after the one shot; no reuse of consumed 1M pool (any split/subrange), any
  consumed 1.5M range (TRAIN 0..1659, VAL DEV 1660..2043, VAL stub, HOLD
  2213..2766), consumed 2M TRAIN-as-DEV / VAL DEV / HOLD DEV, HOLD tail 3595..3644
  beyond counting, or any other session; no second factor after any probe pattern;
  no oracle-as-operational; no population-reliability inference from this single
  block alone; no recovery-rate reading of this packet's outcomes; no tuning
  inside this packet; no H2 verdict inside this packet.
- Spike-formula guard (pre-registered, RESOLVED 2026-09-20 by the F-median8 decision): the `NEXTBR_STOP_B1_LOCAL_SPIKE_FORMULA_UNDECIDED` guard applies only if the §3 formula text is missing/contradictory.
- SCL entry gate UNCHANGED (unlocks nothing by itself; SCL work runs on synthetic
  X11 per D3, never on this block).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B fifteen files)

- Stage-A freeze pins (zero protected opens): reuse-artifact paths +
  canonical/file-bytes digest replays + H-literal recomputation + `p_b`
  cross-check + `p1`-equality recheck + floor-hit replays; K_total literal replay
  display + (K1,K2) integers + frozen-A order-file digest replay; alt file-bytes
  digest replay + alpha/floor/key-set/`p1`-equality/alt-H replays; spike order
  artifact path + file-bytes digest + formula-id pin + derivation-program pin
  (module + function + formula-id + argv + zero-sampling attestation) + A-vs-B
  set-delta table; D1/D2 replay literals + FEASIBLE outcome; exact module path +
  N-flag Stage-B command verbatim + population integers + caps + budgets + tag
  domain + P16 construction digest + IR-3 threshold multipliers (1.0×/2.0×) + IR-4
  k=16 + IR-5 uncapped encoding/size pins; recorded alongside this packet. Stage-A
  product identities: ONE new artifact (spike order file under this queue dir:
  `new_spike_order_2m.json`; digest pinned at Stage A); reuse paths point at the
  P20O queue dir (digests pinned alongside this packet).
- Stage-B root:
  `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m/`
  (exactly fifteen files; per-(arm, block) checkpointing; pure merged-DEV scoring
  — zero sampling; one merged-DEV content open; no reopen/rerun). Root must be
  ABSENT at Pre-EXECUTE.
- Fifteen files: `frozen_plan.json`, `input_and_predecessor_identity.json` (P16
  construction digest + reuse-prior digest-gate proof + reuse-alt digest-gate
  proof (file bytes sha256 equals the frozen `--alt-digest`) + frozen-A order
  digest-gate proof + spike order digest-gate proof (file bytes sha256 equals the
  frozen `--spike-order-digest`) + derivation-program pin (module + function +
  formula-id + argv + zero-sampling attestation) + formula-id pin + A-vs-B
  set-delta table + K-literal replay + budget-literal replay + D1/D2 replay +
  tag-domain pins + split manifest + merged-DEV integers + DEV∩build-frames
  disjointness declaration with frame sets + IR-3 multiplier pins + IR-4 k pin +
  IR-5 uncapped encoding/size pins), `per_block_arm_outcomes.jsonl` (3 records at
  completion, each carrying the nine scalars with arm-specific order digest +
  IR-1..IR-4 payload with frozen nullability/caps + IR-5 manifest references),
  `aggregate_summary.json` (incl. the geometry/coverage tables: full-block series
  summaries + mismatch-coverage table + IR-1 tails under both orders + full-scope
  top-128/1024 concentration + A-vs-B set-delta table — all explicitly labelled
  non-recovery), `report.md`, `ir5_full_manifest.json` (per-file sha256 + shape +
  dtype + endianness + order-identity + record linkage + `ir5full-v1`), plus the
  nine IR-5 `.bin` files (`A_hazard_bits_f32le.bin`, `A_inprefix_u8.bin`,
  `A_inu_u8.bin`, `B_…×3`, `O_…×3`). Per-record §7 endpoints + first error
  coordinate/layer, zero-count hits, floor hits + floor-hit rate + log loss,
  true-H vs candidate-H L2 NLL, taxonomy, construction-point fields
  (`l2_construction` alt-α1 on all arms, `k1/k2/k_total`, `prior_digest`,
  `alt_digest`, `l1_order_digest`, `l2_order_digest` arm-specific) + the NINE
  carried scalars + IR-1..IR-4 fields (all PRESENT per the Stage-A freeze) + IR-5
  file references with digests.
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); genie
  call counts (Stage-A 0 + Stage-B 0) + SC counts (L1/L2 split: A 2 / B 2 / O 1)
  + tag counts exact; block SER/NLL (recorded, never a reliability claim);
  wall/RSS; per-arm floor-hit rate + per-arm prefix hazard means + geometry/
  coverage tables reported. NO per-arm exact counts are read as recovery rates;
  the A→B transition cells are NOT computed (counting vocabulary is out of scope
  for this packet by D2 form).
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `reuse_prior_identity` (P20O npz canonical
  digest + lambda-0.0/floor pins + exact key set + H literals within 1e-12 + `p_b`
  cross-check, worktree-file only); `reuse_alt_identity` (file-bytes digest +
  alpha-1.0/floor pins + exact key set + `p1`-equality within 1e-12 + descriptive
  alt-H literals); `alt_construction_budget_feasibility_replayed` (P20O FEASIBLE
  replay required before Pre-EXECUTE; replay mismatch ends the packet at Stage A
  with DEV untouched); `dev_split_manifest_identity`; `dev_block_range_identity`
  (§4 gate family (a)→(g): merged cross-file 2M identity first, then dual-segment
  intra-file containment, then consumed-1M, consumed-1.5M, consumed-2M exclusions
  incl. the DEV∩build-frames disjointness declaration, then reuse-prior +
  reuse-alt + frozen-A-order + K-literal + spike-derivation-program pins, then
  merged-frame-set-identity + order-position-identity + tag-domain pins);
  `order_derivation_identity` (derivation-program pin + formula-id pin + reused-
  prior-digest input pin + Stage-A spike order file-bytes digest, Stage-B
  file-bytes digest equality replay-exact, zero Stage-B sampling);
  `frozen_order_identity_A` (P20O program pin + frozen-A order-file digest,
  Stage-B file-bytes digest equality replay-exact, zero Stage-B sampling);
  `spike_order_identity_B` (Stage-A spike order-file digest, Stage-B file-bytes
  digest equality replay-exact, permutation-valid + K2-prefix-disclosed +
  L1-carried checks); `k_literal_exact` + `budget_literal_replayed` (S2-i: f=1.3
  literal replayed from the P20O freeze, never a 1.5M absolute, never recomputed
  from alt-H); `target_population_contract`; `dev_population_exact` (128 merged
  frames / 32768 pairs / 256 rows per frame / pair indices / symbol range, with
  the VAL-then-HOLD segment order); `blocks_exact_with_declared_remainder` (ONE
  exact merged DEV range per arm in block-major slot order + never-used HOLD tail
  50 frames / 12800 pairs + counted-never-decoded 1.5M remainders 83 frames /
  21248 pairs); `three_records_exact`; `genie_calls_exact` (Stage-A 0 + Stage-B
  0); `sc_calls_exact` (derived 5); `tags_exact` (derived 3);
  `orders_valid_k_prefixes_within_registered_arms` (frozen-A prefixes on A/O +
  spike prefixes on B + construction triple α1×3 + K literals);
  `order_set_delta_recorded` (A-vs-B L2 disclosed-set symmetric difference +
  rank-displacement table byte-exact, size-delta exactly 0);
  `hazard_instrumentation_complete` (all nine §7 scalars present with correct
  nullability + arm-specific order digest on every completed record);
  `ir_payload_complete` (IR-1..IR-4 all PRESENT with frozen caps/nullability +
  IR-5 uncapped: nine `.bin` files byte-present with manifest digests matching on
  every completed record); `ir5_full_manifest_identity` (per-file sha256 + shape
  + dtype + endianness + order-identity + `ir5full-v1`, all equal);
  `evidence_size_rule_met` (every committed file ≤ ~2 MB; largest single file
  131072 B); `floor_hit_rate_reported`; `oracle_isolation`;
  `buckets_disjoint_exhaustive` (unique arm/block + schema); `undetected_zero`;
  `nonfinite_zero`; `truth_isolation` (incl. the IR recorder sentinel);
  `disclosure_recount_exact`; `one_open_per_protected_input` (counts 0 +
  merged-DEV 1); `input_stat_unchanged`; `no_unregistered_access`;
  `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (implementation + spike-order derivation + injected tests +
  reuse-freeze; authorized separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_l2_mechanism_probe_2m.py -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20s/<uuid>/`
  temp root; protected-open audit declared separately (counts 0 + merged-DEV 0 at
  Stage-A close). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A reuse + spike verification (ZERO protected opens; worktree-file digest
  recomputation ONLY): recompute the P20O prior canonical digest + H literals +
  `p_b` + `p1`-equality + alt/order file-bytes digests from the frozen worktree
  files; replay K literals + D1/D2 FEASIBLE replay; derive the spike order
  permutation by the frozen program under the frozen DECIDED 2026-09-20 F-median8 §3 formula-id
  (worktree-prior-only, zero sampling, zero genie) and pin its file-bytes digest
  + formula-id pin + program pin + set-delta table; confirm the §4 merged frame
  integers against the split-manifest JSON metadata (no parquet/NPZ
  open/stat/listing); grep-verify the §6 tag/test-seed freshness. Template (pins
  filled at Stage A; all flags required, no production default):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_mechanism_probe_2m --verify-reuse --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --spike-order-file .workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/new_spike_order_2m.json --spike-order-digest <FROZEN_AT_STAGE_A> --spike-formula <FROZEN_AT_STAGE_A> --k1 334 --k2 6746
```
  Stage A confirms the module path (thin importer of accepted `l2_alt_hold_ir_2m`
  per the §2 delta list d1–d9, or freezes a written equivalent with justification)
  and the `--source` vocabulary (only `2M`). Forbidden by default: `longrun_*`,
  `minrerun_*`, `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data, full
  sweeps.
- Stage B execution command (RECOMMENDED here, frozen verbatim at Stage A with
  the `<FROZEN_AT_STAGE_A>` pins filled; NOT AUTHORIZED until independent
  Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_mechanism_probe_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest <FROZEN_AT_STAGE_A> --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest <FROZEN_AT_STAGE_A> --source 2M --floor 1e-15 --n 32768 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames-val 2827 2915 --dev-frames-hold 3556 3594 --block-frames 128 --remainder-frames 3595 3644 --tag-master 2026092360 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest <FROZEN_AT_STAGE_A> --spike-order-file .workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/new_spike_order_2m.json --spike-order-digest <FROZEN_AT_STAGE_A> --spike-formula <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m
```
  All flags required, no production default; three hardcoded arms with the order
  swap pinned (never CLI-tunable: A = α1 + frozen order at carried K; B = α1 +
  spike order at carried K; O = frozen-order true-L1 oracle); Stage-B prior path
  MUST equal the §3 reuse pins; `--alpha` takes no Stage-B value (construction is
  frozen in the alt file). Stage A fills every `<FROZEN_AT_STAGE_A>` pin
  (`--prior-digest`, `--alt-digest`, `--k1/--k2`, `--order-digest`,
  `--spike-order-digest`, `--spike-formula`) with the §3 replayed/derived values
  plus the `--source` vocabulary (only `2M`) and the IR-3 multiplier + IR-4 k +
  IR-5 encoding pins in `frozen_plan.json`. The dual-segment frame flags (or a
  written equivalent frozen at Stage A) enforce gate (g). Forbidden by default as
  above.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git
  show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: spike-order artifact `new_spike_order_2m.json` (+ file-bytes digest +
  formula-id pin + derivation-program pin + A-vs-B set-delta table +
  zero-sampling attestation) + reuse-verification freeze supplement (§3
  digest/H/`p_b`/`p1`-equality replays + K-literal replay + frozen-A order digest
  replay + spike digest + formula-id + program pin + D1/D2 replay + population
  integers + caps + budgets + tag domain + IR-3 multipliers + IR-4 k + IR-5
  encoding/size pins + module path + all commands verbatim) + implementation
  notes (exact files, diffs, test commands/results, frozen reuse/spike/
  population/cap/command, D1/D2 replay outcome) + thin runner + focused injected
  tests. NO other new artifacts (reuse paths point at the P20O queue dir).
  Protected content opens 0 at Stage-A close (counts 0/0 + merged-DEV 0/1; zero
  sampling at every stage).
- Stage B (only after authorization): evidence root (§9, fifteen files) +
  `OPERATOR_RETURN.md` (+ freeze supplement, `PRE_EXECUTE_REVIEW.md`,
  `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec P20S delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20s/spec.md`
  + `tasks.md` P20S section (same umbrella change as P18/P19/P20A/P20B/P20C/P20E/
  P20F/P20G/P20H/P20I/P20J/P20K/P20M/P20N/P20O/P20Q/P20R; no new top-level change).

## 12. Allowed work

- New thin mechanism-probe runner (importer per §2 d1–d9) + spike-order
  derivation program (worktree-prior-only, §3 contract, frozen DECIDED 2026-09-20 F-median8 formula-id) +
  focused injected tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`,
  `raw_prior_val_1p5m.py` (gate/population/record-writer pattern references),
  `l2_alt_hold_1p5m.py` (α1 construction-swap pattern reference),
  `l2_alt_maintain_2m.py` (gate/record-writer/nine-scalar pattern references),
  `l2_alt_hold_ir_2m.py` (import target; gate/population/IR record-writer pattern
  references), `l2_order_position_1p5m.py` (dual-order + derivation-program
  pattern references) (+ `construction.py` / `prior.py` / `sc.py` contracts as
  called).
- ZERO protected opens in Stage A: worktree-file digest recomputation of the §3
  P20O artifacts + deterministic spike-order derivation from the worktree prior
  arrays under the frozen DECIDED 2026-09-20 F-median8 formula-id (zero sampling, zero genie, §3 contract) +
  split-manifest JSON-metadata confirmation of the §4 merged integers +
  grep-verification of the §6 tag/test-seed freshness + closed-form IR formula
  pins on injected vectors (zero sampling, zero genie calls, zero real frames).
- P20S OpenSpec delta + packet docs + Stage-A freeze supplement/return/review
  files + Stage-B evidence root (root only after Stage-B authorization) + the §3
  reuse identity + the §3 spike identity (§§3/9).

## 13. Forbidden work

- Any NPZ/parquet content open or stat/listing of merged-DEV/tail segments, 2M
  VAL-DEV, 2M TRAIN, 2M HOLD-DEV, any 1M split, or any 1.5M split in Stage A
  (Stage-A protected opens: counts 0/0, merged-DEV 0/1); any counts open at any
  stage; any K carried as an absolute from 1.5M or recomputed from alt-H (S2-i;
  replay only from the P20O 2M session point); any derivation or sampling on real
  DEV frames at any stage; any decoder execution before Pre-EXECUTE PASS + pasted
  Stage-B authorization; any spike derivation under any formula other than the frozen DECIDED 2026-09-20 F-median8 §3 text.
- Any change to GF32/transform/SC arithmetic, floor value, 2M L1 tables, frozen
  2M L1/L2 orders (A/O-side), disclosed sizes, tag scheme semantics, outcome
  precedence, accepted evidence roots, P20O products, P20Q/P20R products,
  X08/X09/X10 probe roots, H2 run root, or `src/` + `experiments/` + `tools/`
  frozen baseline. No disclosure-size change (B−A = 0); no order change beyond
  the single spike L2 position set; no decoder change.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the
  consumed 1M pool (any split/subrange), any consumed 1.5M range (TRAIN
  0..1659, VAL DEV 1660..2043, stub 2172..2212, HOLD 2213..2766), consumed 2M
  TRAIN-as-DEV / VAL DEV 2187..2826 / HOLD DEV 2916..3555, HOLD tail 3595..3644
  beyond counting; no second construction, no construction sweep, no bounded
  search, no second order beyond the single spike set, no disclosure change; no
  tuning; no new-block peeking before the authorized attempt; no calibration on
  DEV; no H2 verdict inside this packet; no recovery-rate reading of this
  packet's outcomes at any stage.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push; no self-acceptance; no P20D scope creep beyond the single frozen
  order factor; no P20H–P20R rerun under this packet. No efficiency language
  anywhere. No text-JSON float dumps of the full-block series; no
  `*.npz`/`*.npy`/`*.parquet` evidence files.

## 14. Acceptance IDs

- `P20S-R1`: P20O 2M reuse verified read-only from worktree files (prior
  canonical + orders/alt file-bytes digests replay-exact; H literals within
  1e-12; `p_b` cross-check; `p1`-equality within 1e-12; exact key sets;
  lambda-0.0/alpha-1.0/floor pins; zero protected opens at every stage) + spike
  derivation contract verified (worktree-prior-only inputs, deterministic, zero
  sampling/genie, zero protected reads, length-32768 permutation, K2-prefix
  disclosed, formula-id pin + program pin + file-bytes digest + set-delta table
  frozen at Stage A). Derivation-gate BLOCKED → planner rework, never a Stage-B
  fallback.
- `P20S-R2`: budget/split/orders replayed 2M-session-derived (S2-i literal replay
  displayed from the P20O freeze: K1 334/K2 6746/K_total 7080, never from 1.5M,
  never from alt-H; zero Stage-B sampling; zero Stage-A sampling);
  closed/consumed blocks select nothing; consumed 1M pool + all consumed 1.5M
  ranges + consumed 2M TRAIN-as-DEV + consumed 2M VAL DEV + consumed 2M HOLD DEV
  excluded by source-tagged cross-file gates; merged DEV (VAL tail 2827..2915 +
  HOLD head 3556..3594 → ONE block, HOLD tail 3595..3644 + 1.5M remainders never
  used) gated by the exact 128-frame list rule + Pre-EXECUTE-approved; 1M/1.5M/
  2M-consumed untouched in every form.
- `P20S-R3`: disclosure point preregistered per arm from the carried integers
  (A/B `5*(K1+K2)+64 = 35464` with Δ exactly 0; O `5*K2+64 = 33794`;
  327743 public; totals 104722/983229 frozen at Stage A), recount mismatch 0;
  set-delta recorded byte-exact with size-delta exactly 0; CE ratios never called
  efficiency.
- `P20S-R4`: arm pins (A frozen-order anchor + B spike candidate + shared-L1 rule
  + O frozen-order oracle D-continuity, §3 α1 rule replayed, `p1`-equality within
  1e-12, formula-id + derivation-program pin) frozen before execution, unchanged
  after; P16 construction migration pinned; no tag-guided selection, no evidence
  reuse, no post-hoc re-picking, no re-derivation.
- `P20S-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9;
  `undetected` isolated; oracle arm never operational; first-error
  coordinate/layer rows + per-record floor-hit fields + all nine carried scalars
  (arm-specific order digest) complete per record with correct nullability +
  IR-1..IR-4 ALL PRESENT with P20Q-identical caps/nullability on every completed
  record (IR-3 two thresholds 1.0×/2.0× prefix-mean; IR-4 k=16; record's OWN
  order used for every prefix flag) + IR-5 UNCAPPED (nine `.bin` files +
  `ir5full-v1` manifest with matching digests on every completed record);
  instrumentation + IR recorded-only (truth-isolation sentinel green).
- `P20S-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning;
  split-counted reads (counts 0/0 + merged-DEV 1/1 + 1M 0 + 1.5M 0 + 2M-non-DEV
  0); 5 SC / 3 tags / 3 records derived; resource aborts via P20A path with
  accounting preserved; stop rules + formula-guard + SCL gate intact.
- `P20S-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded (Pre-EXECUTE
  explicitly adjudicates §3 reuse/alt replay + spike derivation contract +
  formula-id decided text (§3, DECIDED 2026-09-20 F-median8) + D1/D2 replay
  outcome + §5 budget/K-literal replay + §4 gate family (a)→(g) incl. the merged
  frame-set identity rule + §2 runner-delta design + §7 nine-scalar + IR-1..IR-4
  boundary + IR-5 uncapped encoding/size rule + arm-specific order-digest rule);
  main-thread acceptance owns the label; geometry/coverage-descriptive only, no
  recovery-rate/FER/qualification/promotion/H2-verdict language; branch + H2
  reading (§16) stays planning input, never an in-packet verdict; honest-scope
  statement (§0) repeated verbatim in the return.
- `P20S-R8`: Stage-A suites green on injected data with the zero-protected-open
  audit (counts 0/0 + merged-DEV 0/1 at Stage-A close; 1M/1.5M/2M-consumed
  non-access in every form); no commit/push; frozen dirs byte-untouched except
  the §12 manifest.
- `P20S-R9`: D1/D2 replay (TRAIN-only FEASIBLE literal replayed from the P20O
  freeze: margin 4791.09652735766, zero merged-DEV reads; replay outcome frozen
  alongside this packet/STATUS BEFORE any DEV contact; MISMATCH → DEV untouched,
  no Stage-B request, point recorded blocked-by-replay; FEASIBLE-replay →
  literals frozen, packet proceeds) + spike gate (formula-id + derivation-program
  pin + spike digest frozen BEFORE any DEV contact; MISMATCH → DEV untouched, no
  Stage-B request). Gate-fired-by-replay → main-thread re-frame, never a
  Stage-B fallback.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs
`P20S-R1..R9` (stage-appropriately) complete with changed files + exact
commands/results + artifact inventory (incl. all reuse digest replays + spike
digest + formula-id + program pin) + split open audit (counts + merged-DEV + 1M
+ 1.5M + 2M-non-DEV separately); or (b) a concrete blocker with failing command,
exact error/traceback, attempted remedies, and the ONE decision needed from the
main thread. "Still incomplete" is not a completion report. The operator never
marks its own work accepted and never authorizes Stage B.

Blocker B-1 (RESOLVED 2026-09-20 — F-median8 DECIDED; derivation proceeds under the frozen §3 formula):
- B-1 spike formula choice: DECIDED 2026-09-20 (F-median8) (§3 frozen verbatim text; Stage A
  SHALL NOT invent or alter any functional; F-mean8 / F-multi8_32 rejected, retained in §3 as historical context only). Consistency guard retained: the `NEXTBR_STOP_B1_LOCAL_SPIKE_FORMULA_UNDECIDED` guard applies only if the §3 formula text is missing/contradictory.

## 16. Deferred options (not in this packet)

- New-acquisition ladder: any real-data block beyond the merged final block
  requires newly acquired frames (the post-P20S never-decoded ledger holds only
  the 50-frame HOLD tail + 83 low-information 1.5M frames = no further N=32768
  block under any convention). Trigger = new frames landed + their own freeze,
  tag domain, and reviews. Nothing is auto-triggered inside this packet.
- (b) L2-side bounded search at the fixed point → follow-up planning (deferred):
  trigger = accepted P20S geometry/coverage tables (spike coverage of mismatch
  positions, full-block concentration) analyzed by the main thread. Main thread
  re-evaluates with the full chain evidence in hand. This packet prejudges none
  of it and licenses no reliability claim.
- (c) Second single construction form → follow-up planning (deferred): trigger =
  main-thread reading of the accepted P20S geometry against the α1 form. Only
  then does exactly ONE second form become the next single factor on new data by
  main-thread planning. Nothing is auto-triggered inside this packet.
- SCL via X11 synthetic probe (D3) → parallel mainline algorithm work, zero
  protected-data cost (deferred from this packet, active elsewhere): the §3 spike
  formula (whichever id is chosen) is shared deterministically with X11 for
  synthetic validation; list-survival of the true path at L=4/8 is decided there,
  never on this block.
- 1.5M closure: VAL stub 2172..2212 (41) + HOLD remainder 2725..2766 (42) stay
  never-decoded; no 1.5M packet follows without new acquisition or a new N/design
  (which needs a new OpenSpec change, not a packet).
- H2 adjudication → main-thread analysis AFTER P20S acceptance (deferred, never
  in-packet): trigger = accepted P20S full-block geometry/coverage tables joined
  with the P20N/P20O/P20Q/P20R archive (now at full-block scope for the first
  time via uncapped IR-5). The H2a–H2e verdicts belong to that analysis; this
  packet supplies the pre-registered quantities and licenses no H2 verdict, no
  threshold, and no recovery-rate reading.
- The merged DEV block is CONSUMED by this packet regardless of outcome; HOLD
  tail 3595..3644 and all 1.5M remainders stay never-decoded. Any follow-up
  packet needs its own freeze, tag domain, and reviews.

(End of file)
