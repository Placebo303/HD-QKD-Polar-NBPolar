# Phase 4-P20T — N=8192 persistence probe on the 2M HOLD tail (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage-A new-derivation implementation + N=8192
  order freeze with ZERO protected reads, Stage-B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, derivation,
  protected read, decoder execution, or commit/push is authorized by this file.
- RN-1 verdict: FREEZE REVIEW PASS (2026-09-20, main thread) on
  `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-reduced-n-persistence/`
  (spec.md + design.md + proposal.md) + umbrella tasks.md reduced-N section
  (RN-1..RN-8) — see `docs/decision-log.md` "2026-09-20 RN-1 freeze review PASS".
  Revision-prep corrections verified therein (Q-G1 mining formulation, Q-G2
  top-hazard-tail-mass alignment, counts 0/0 with worktree-only inputs, 59-row
  join, residual-contradiction grep clean).
- Standing pre-authorization (2026-09-20): RN-2 (this Tier-Y packet freeze)
  proceeds under the standing pre-authorization; Stage-A and Stage-B still need
  their own freezes + independent reviews + authorizations per the gate sequence
  (standing pre-authorization does not collapse Tier-Y gates).
- Predecessor (read-only reference, never modified, never re-derived):
  `NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m/` (accepted descriptive,
  15/15 files, N=32768). Scoping parent:
  `.workbuddy/queue/NBPOLAR-REDUCED-N-PERSISTENCE/` (STATUS + SCOPING_NOTES,
  state `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`).
- Decision parents: `.workbuddy/queue/NBPOLAR-REDUCED-N-FEASIBILITY.md`
  (population arithmetic, C1–C10 cost inventory, comparability verdict, gate
  class); geometry-mining §3 trigger met with named questions Q-G1/Q-G2.
- Structural template: P20S `TASK_PACKET.md` (§§0–16) for RIGOR/STRUCTURE ONLY.
  No N=32768 literal is carried as a P20T pin (K 334/6746/7080, tag master
  2026092360, order/alt digests as tables, 32768 caps/geometries, leakage
  literals — all listed in the §7/§9 non-transfer boundary, never frozen here).
- Gate discipline: any standing long-horizon authorization does NOT collapse
  Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_2M_20260121_183657` (2M), scoring population first-and-only
  use of the single N=8192 block DEV 3595..3626 on the 2M HOLD tail (see §4).
  The 1M pool, the entire 1.5M session, 2M TRAIN-build, all consumed 2M ranges,
  and the N=32768 order/alt files (length/geometry-incompatible) are fail-closed
  against P20T derivation and DEV selection (see §§3–4). 1.5M and 2M are never
  mixed; NOTHING is pooled across N.

## 0. Planner header (OpenSpec workflow)

- **Goal**: Record the single descriptive persistence observation available at a
  reduced block size — three arms (α1 + NEWLY DERIVED N=8192
  frozen-order-equivalent anchor, α1 + NEW spike-local order candidate at
  identical K under carried F-median8 with R=8 re-frozen, true-L1 oracle
  diagnostic), P20Q-identical IR-1..IR-4 shapes/formulas, IR-5 full-block
  8192-position hazard series per record in capped binary encoding (48
  KiB/record), full P16-scale re-derivation (construction/allocation, K via the
  frozen budget formula from recomputed 2M H, fresh length-8192 L1/L2/spike
  orders, new tag domain) — and pre-register within-N paired judgment quantities
  that directly answer Q-G1/Q-G2 at N=8192 with zero cross-N inference.
- **Non-Goals**: No FER, reliability, efficiency, leakage, key-rate,
  recovery-rate, scaling-superiority, or promotion claim; no cross-N inference;
  no H2 verdict or H2 input inside this packet; no new construction factor (α1
  rule carried on all arms); no K/disclosure-size change between operational arms
  (B−A = 0 by design; O discloses K2 only as carried diagnostic continuity); no
  floor-value change; no SCL/new kernel/model/schema; no bounded search or second
  construction (both stay deferred); no K carried as an absolute from
  (334,6746) or recomputed from alt-H; no hand-filled K (AGENTS.md §5.5); no
  reuse of any N=32768 order/alt file in any form (length + per-N geometry
  mismatch); no derivation or sampling on real DEV frames at any stage; no
  calibration on DEV; no `--n 8192` passed to any frozen-point N=32768 runner
  (`target_construction.py:1559` hard gate `n == FROZEN_N`); no reuse of any
  consumed/closed range (full ledger §4); no cross-session pooling (1.5M × 2M
  forever forbidden); no cross-N pooling; no overwrite under `results/` or
  `comparison_bench/outputs_comparison/`; no commit/push.
- **Impact Scope**: New `FROZEN_N = 8192` runner (or thin-importer + new frozen
  constants) + focused injected tests + N=8192 derivation program + packet docs +
  Stage-A freeze supplement (construction/allocation artifact + fresh order
  digests + spike digest + formula-id pin + R=8 re-freeze decision +
  derivation-program pin with sampling budget/seeds + K derivation display +
  set-delta table + tag domain + caps + budgets, recorded alongside this packet)
  + implementation notes + Stage-B evidence root (5 JSON/JSONL/md files + 1 IR-5
  manifest + 9 N=8192 `.bin` series). No change to `src/`, `experiments/`,
  `tools/`, any N=32768 construction/order/alt file, any accepted P16–P20S/R1
  root, X08/X09/X10/X11/X17 probe roots, H2 run root, the reduced-N OpenSpec
  delta (RN-1 PASS, frozen), or `results/` /
  `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20T-R1..R9 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance.
  Within-N-descriptive label; `undetected` isolated; oracle never operational;
  outcomes recorded per record but explicitly NOT read as recovery rates; H2 and
  every cross-N reading explicitly deferred out of this packet.
- **Tasks**: (planner task list for coder agents) H1 freeze the §3
  reuse-vs-derive split + R=8 re-freeze decision + sampling budget/seed rule
  (R1); H2 freeze single-segment population/gates incl. the exact 32-frame list
  rule (§4, R2); H3 freeze in-packet-K caps from the derived point (§5, R3); H4
  freeze arm pins — new frozen-order-equivalent A + spike-local B (carried
  F-median8, re-frozen R=8) + derivation-program pin + oracle continuity (§§3/6,
  R4); H5 wire endpoints/taxonomy + mandatory nine-scalar semantics + IR-1..IR-4
  (P20Q-identical) + IR-5 full-block 8192 binary series + manifest (§7, R5); H6
  enforce one-shot budget/stop (§8, R6); H7 Stage-A suites green with zero-open
  audit (R8); H8 independent Pre-EXECUTE adjudication of derivation/K-literal/
  population/IR boundary (R7); H9 single authorized Stage-B attempt (R6/R7); H10
  independent Pre-RESULT + acceptance (Q-G1/Q-G2 quantities checked present,
  never decided in-packet).
- **Honest scope** (binding on proposal/design/packet/return language): a
  descriptive persistence probe; n=1; NO FER, reliability, efficiency, leakage,
  key-rate, recovery-rate, scaling-superiority, or promotion claim; NO cross-N
  inference; NO H2 (re-)adjudication input; NO extension of any N=32768 chain.
  Any exact count is COMPLETE when integrity holds and is explicitly NOT read as
  a recovery rate.

## 1. Mission

With a FULL new derivation at N=8192 under frozen rules — the §3 worktree-reused
2M prior arrays as the SOLE off-protected-data derivation input (never the V25
counts NPZ: counts 0/0 at every stage), synthetic TRAIN-block sampling at N=8192
from those arrays under frozen budget/seeds pinned at the Stage-A freeze, pooled
per-layer risks → worst-first `(e,h,index)` orders → `K_total` via the frozen
budget formula with recomputed 2M H → exhaustive `(K1,K2)` by TRAIN residual
frozen before DEV — and everything else fixed by the freeze (α1 rule, carried
F-median8 formula-id with R=8 re-frozen as a new decision, identical (K1,K2) on
A/B, floor 1e-15, N=8192, greedy SC only, new P20T tag domain only), zero
further tuning:

> On the ONE N=8192 DEV block (2M HOLD 3595..3626), what within-N paired
> observation does each arm (newly-derived frozen-order-equivalent anchor,
> spike-local order, true-L1 oracle) record — Q-G1 spike-local fail-site pattern
> recurrence (A vs B on the same block) and Q-G2 top-hazard-tail-mass disclosure
> contrast (under each record's own order) — with the nine-scalar semantics and
> the full-block 8192-position IR-5 series preserved per record, and with
> per-record outcomes recorded but explicitly NOT read as recovery rates?

P20O 2M VAL DEV 2187..2826 CONSUMED (1/1 SPENT); P20Q 2M HOLD DEV 2916..3555
CONSUMED (1/1 SPENT); P20S merged block (VAL 2827..2915 + HOLD 3556..3594)
CONSUMED (R1 attempt spent; both roots immutable); P20R 1.5M VAL-remainder DEV
2044..2171 CONSUMED (1/1 SPENT, block-dominated non-discriminating). Post-P20S
never-decoded ledger: 1.5M VAL stub 2172..2212 (41 frames / 10,496 pairs) +
1.5M HOLD remainder 2725..2766 (42 / 10,752) + 2M HOLD tail 3595..3644 (50 /
12,800) = 133 frames / 34,048 pairs = ZERO full N=32768 blocks under any
convention. The ENTIRE 1M pool is fail-closed. All branches after this packet
are deferred to §16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- Population constraint binds before factors (RN-1 PASS checklist item 1): the
  post-P20S never-decoded ledger holds exactly 133 frames / 34,048 pairs, i.e.
  ZERO complete N=32768 blocks. The 2M HOLD tail 3595..3644 (50 frames / 12,800
  pairs) is one contiguous segment inside HOLD intra-file range 2916..3644 and
  fits EXACTLY one N=8192 block (32 frames: 3595..3626, 32×256 = 8192 pairs)
  with a declared 18-frame remainder (3627..3644, 18×256 = 4608 pairs).
  First-contiguous-block rule (same convention as all P20 DEV selections).
- Geometry-mining §3 trigger met with named questions (RN-1 verified): Q-G1 —
  does the spike-local L2 fail-site pattern (first error at an undisclosed
  below-mean coord-class site with floor-rate elevation, paired against the
  frozen order) recur at N=8192 on the 2M HOLD tail under within-N paired
  comparison (arm A vs arm B on the same block)? Q-G2 — does the spike-local
  order disclose more top-hazard-tail mass than the frozen-order equivalent at
  the same N (IR-1 prefix/outside tail-mass contrast A vs B; full-scope
  top-128/top-1024 concentration per record's own order)? This packet is the
  persistence probe for exactly these two questions — descriptive only, n=1,
  never statistical discrimination.
- Rebuild-vs-derive stance (frozen, not re-argued; effort class P16-scale, NOT
  P20S-scale thin reuse): at N=8192 nothing is thin-reusable except session-H
  inputs, formula shapes, and code paths (§3). Construction/allocation, runner,
  K, L1/L2/spike orders, tag domain, SC sizing, IR-5 sizing, disclosure values,
  population gates, and all reviews/authorizations are rebuilt or re-frozen.
  Reusing the N=32768 order/alt files would be a length + per-N-geometry
  violation; carrying (K1,K2) = (334,6746) would violate same-N derivation.
- Alternatives rejected in writing: (a) any N=32768 order/alt file reuse in any
  form — length- and geometry-incompatible, forbidden; (b) any K carried from
  (334,6746), recomputed from alt-H, or hand-filled — forbidden (estimate-only
  rule §3); (c) any `--n 8192` passed to a frozen-point N=32768 runner —
  forbidden by the `target_construction.py:1559` hard gate; (d) λ anywhere —
  X08-falsified, forbidden; (e) floor change — H3/H2d exonerated, forbidden;
  (f) SCL/list/belief decoder — decoder change; SCL unlock runs on synthetic
  X11, never on this block; (g) consuming any 1.5M remainder, any consumed 2M
  range, the 1M pool, or any second N=8192 block — forbidden (only R1 exists);
  (h) cross-session or cross-N pooling — forever forbidden; (i) freezing any
  scalar or IR payload as absent — forbidden; (j) any FER/recovery-rate,
  efficiency, leakage, key-rate, scaling, or H2 reading of this packet's
  outcomes at any stage — forbidden; (k) second construction, construction
  sweep, bounded search, second order beyond the single spike set, fourth arm,
  second construction form, or disclosure change — all deferred or forbidden
  (§16).
- Session inventory (no new protected access by this planner; provenance from
  the split manifest `nbldpc_v25_split_manifest_v1` read as JSON metadata only,
  plus P20M/N/O/Q/R1 §§2/4): 2M TRAIN 2187/559872 + VAL 729/186624 + HOLD
  729/186624 (256 rows/frame; frame bases TRAIN 0..2186, VAL 2187..2915, HOLD
  2916..3644; see §4). 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824.
  Geometric position: P20T DEV R1 is the FIRST 32 frames of the 2M HOLD tail
  (3595..3626 = ONE full block: 32×256 = 8192 pairs); remainder 3627..3644 (18
  frames / 4608 pairs) never-decoded under this packet.
- Runner-derivation design choice (frozen; the "design.md" decision): a NEW
  `FROZEN_N = 8192` runner module (or thin-importer + new frozen constants, to
  be confirmed or replaced with a written equivalent + justification + re-review
  at Stage A) importing accepted patterns read-only (population pattern,
  TRAIN-exclusion gate family, order-file + digest mechanism, P20A
  endpoint/taxonomy/recount/resource machinery, hazard/IR recorder code points).
  Exact delta list, nothing else: (d1) population → single-segment 2M HOLD DEV
  R1 (§4; all other sessions/ranges excluded as consumed or never-decoded);
  (d2) derivation inputs → §3 worktree prior arrays ONLY (never the V25 counts
  NPZ); (d3) K pins → derived in-packet at Stage A from recomputed 2M H
  (estimate ≈1760 only; never carried, never hand-filled); (d4) orders → DUAL
  NEW: fresh frozen-order-equivalent file (length-8192, arms A/O) + fresh spike
  order file (length-8192, arm B), each digest-gated at Stage A, each disclosing
  first-K1 / first-K2 prefixes at identical sizes (§§3/6); (d5) arms A/B/O per
  §6 (same K on A/B, carried K2 on O; same α1 tables; order SET is the only
  delta between A and B); (d6) new P20T tag domain (§6); (d7) N=8192
  construction/allocation derivation program (worktree-prior-only synthetic
  TRAIN sampling under frozen budget/seeds, deterministic given seeds, zero
  protected reads, carried F-median8 formula-id with R=8 re-frozen) + dual
  order-identity gates + derivation-program pin (§§3/9); (d8) single-segment DEV
  population + DEV∩build-frames disjointness declared inside the TRAIN-exclusion
  gate (§4); (d9) IR-5 full-block 8192-position binary series + manifest (§7).
  No SC/transform/floor-semantics/tag-semantics change; no second factor. The
  alternative (edit any accepted module) is rejected: it would touch an accepted
  evidence-producing file; the new module leaves every accepted file
  byte-identical.

## 3. Reuse freeze + new-derivation stance (normative — worktree prior arrays read-only, zero Stage-A protected reads; ALL N-dependent artifacts newly derived)

- Counts source: NONE. Stage A performs ZERO protected opens (counts 0/0 at
  Stage-A close; the V25 counts NPZ is NEVER opened/statted/listed at any stage
  of this packet). FORBIDDEN derivation inputs: any 1M split, any 1.5M split,
  2M DEV/HOLD-DEV frames for derivation, Model-F CAL artifact, the V25 counts
  NPZ in any form, any N=32768 order/alt file in any form (length +
  per-N-geometry mismatch).
- Reused products (read-only; Stage A verifies by worktree-file digest
  recomputation ONLY — canonical recipe for the prior; zero parquet/NPZ
  protected opens):
  (p1) worktree `raw_prior_2m.npz` ARRAYS as the SOLE off-protected-data
  derivation input — canonical digest replay-expected
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587` (recipe
  `per_session_calibration.canonical_prior_digest`; verified at Stage A, never
  re-derived); keys exactly `counts_ab, f_raw, p1, p2, p_b, lambda_star,
  floor_value, h1, h2, h_total` (`lambda_star` `0.0`; `floor_value` `1e-15`);
  session H literals `0.02566204884275839 / 0.8069006731309893 /
  0.8325627219737477` recomputed via the accepted entropy function within 1e-12
  (never hand-filled per AGENTS.md §5.5; `beta_eff_empirical` never hand-filled);
  `p_b` cross-check pinned at Stage A.
  (p2) Formula SHAPES (never N-literals): budget formula, tag-length rule,
  K-split exhaustive-selection rule, F-median8 ranking rule, IR-1..IR-4
  shapes/formulas, nine-scalar semantics, D1/D2 feasibility shape (fresh
  TRAIN-only computation at Stage A, zero DEV reads — P20O D1/D2 literals are
  N=32768-specific and are NEVER replayed as P20T pins).
  (p3) Code PATHS (called, never changed): `sc.py`, `sc_chunked_gate.py`,
  `transform.py`, causal two-layer wiring, Toeplitz accounting, P20A
  resource/endpoint machinery, recount/gate machinery.
  (p4) Gate PATTERNS: single-segment containment, TRAIN-exclusion,
  consumed-range exclusions, S2-ii disjointness declaration, truth isolation,
  `undetected` isolation, oracle isolation.
- N=8192 derivation contract (Stage-A work, authorized separately): model-sampled
  synthetic TRAIN blocks at N=8192 drawn ONLY from the worktree-reused prior
  arrays (sampling budget = block count, plus derivation seeds — BOTH pinned at
  the Stage-A freeze; zero counts-NPZ opens, zero real-frame use) → pooled
  per-layer risks → worst-first `(e,h,index)` orders → `K_total` via the frozen
  budget formula with recomputed 2M H → exhaustive `(K1,K2)` selection by TRAIN
  residual, frozen before DEV. (K1,K2) SHALL NOT be carried from (334,6746).
- K rule (estimate-only, normative): `K_total = floor((1.3·N·H−64)/5)` with
  N=8192 and recomputed 2M H (never hand-filled). The arithmetic estimate ≈1760
  (1.3·8192=10649.6; ×H≈8866.5; −64≈8802.5; /5≈1760.5) is an ESTIMATE ONLY,
  never a committable literal; the −64 tag term breaks exact quartering
  (7080/4=1770 is NOT the answer).
- Fresh length-8192 worst-first empirical L1/L2 orders + fresh length-8192 spike
  order (digests `<FROZEN_AT_STAGE_A>`, pinned at the Stage-A freeze; Stage-B
  equality-gated). New tag value `10·N+63` = **81983** bits/tag (frozen
  arithmetic in this packet); NEW tag domain (fresh master + prefix, pinned at
  Stage-A freeze with repo grep disjointness proof against ALL frozen masters
  incl. 2026092360); focused test seeds fresh and disjoint, pinned at freeze.
- New runner (or thin-importer + new frozen constants) with `FROZEN_N = 8192`;
  the `target_construction.py:1559` hard gate (`n == FROZEN_N`) forbids passing
  `--n 8192` to any frozen-point N=32768 runner. SC stage count = log2(8192) =
  **13**; `chunk_rows` geometry re-sized (P11 precedent; exact value frozen at
  Stage A); all frozen sizing constants new. IR-5 series 8192 f32-LE (32 KiB) +
  8192 u8 (8 KiB) + 8192 u8 (8 KiB) = 48 KiB/record, 3 records ≈ 144 KiB, same
  `ir5full-v1` manifest linkage; IR-1 (64-bin), IR-2, IR-3 (1.0×/2.0×), IR-4
  (top-16) formulas and caps carried P20Q-identical.
- SPIKE FORMULA — CARRIED F-median8, R=8 RE-FROZEN AS A NEW DECISION.
  Carried functional (verbatim, N-length-generalized): "F-median8: score[i] =
  h[i] − median(h over the R=8 clipped natural neighborhood of i), where h[i]
  is the frozen arm-table hazard atom (-log2 true-cell mass, same recipe as the
  IR recorders); rank all N L2 positions by descending score; take the first K2
  positions as arm B's disclosed L2 set; tie-break by ascending natural block
  coordinate; deterministic, zero sampling at scoring, zero genie calls, zero
  protected reads (inputs: worktree prior arrays + Stage-A-derived N=8192 arm
  tables only); arm A's set stays the newly-derived frozen-order-equivalent
  first-K2 prefix." The R=8 window convention vs 8192-geometry SHALL be re-frozen
  as a NEW freeze decision at Stage A (not an automatic carry); the re-freeze
  rationale + window rule are recorded in the freeze supplement. Stage A SHALL
  derive under this carried formula-id with the re-frozen R=8 decision (no
  re-ask of the formula-id, no alteration; no derivation before the Stage-A
  authorization; no DEV contact, DEV stays 0/1). L1 carried (newly-derived
  N=8192 L1 order) on all arms; disclosed-L2 SET-delta IS the probed factor
  (size-delta exactly 0 by design).
- Fresh TRAIN-only feasibility (same D1/D2 shape, new literals): Stage A computes
  budget feasibility TRAIN-only from the newly derived point with ZERO DEV reads
  BEFORE any DEV contact; literals `<FROZEN_AT_STAGE_A>` pinned in the freeze
  supplement. A feasibility MISMATCH or computation failure BLOCKS before any DEV
  open (DEV stays 0/1) and no Stage-B authorization is requested.
- Stage B loads the frozen Stage-A files read-only behind the
  `worktree_prior_input_identity` + `session_h_recomputed` +
  `k_derived_in_packet` + `construction_allocation_identity` +
  `frozen_order_identity_A` + `spike_order_identity_B` +
  `derivation_program_identity` gates (digests + floor pin + H recomputation
  within 1e-12 + K-derivation display + formula-id + R=8 re-freeze pin, or
  BLOCKED before any SC call).

## 4. Population and closed/consumed-data rule (normative)

- The following are CONSUMED/CLOSED and SHALL NOT supply P20T blocks: the three
  P18/P19 HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599), P20C/P20E/
  P20F DEV blocks (1M 0..383 / 384..767 / 768..1151, remainder 1152..1199 never
  used), P20H DEV (1.5M TRAIN 0..383), P20I DEV (384..767), P20J DEV (768..1151),
  P20K DEV (1152..1535, remainder 1536..1659 insufficient/closed), P20M VAL DEV
  (1.5M VAL 1660..2043), 1.5M VAL stub 2172..2212 (never-used), P20N HOLD DEV
  (1.5M HOLD 2213..2724), HOLD remainder 2725..2766 (never-used), P20O 2M VAL DEV
  2187..2826 (CONSUMED 1/1), P20Q 2M HOLD DEV 2916..3555 (CONSUMED 1/1), P20S
  merged block VAL 2827..2915 + HOLD 3556..3594 (CONSUMED; R1 attempt spent);
  P20L never executed (zero consumption). The ENTIRE 1M pool and the ENTIRE 1.5M
  session are fail-closed against P20T derivation and DEV selection
  (cross-file gate). 1.5M TRAIN 0..1659, 1.5M VAL 1660..2212, 1.5M HOLD
  2213..2766 SHALL NOT be opened/statted/listed/read under this packet in any
  form. 2M TRAIN 0..2186 SHALL NOT supply P20T blocks (build frames). 2M VAL DEV
  2187..2826, 2M HOLD DEV 2916..3555, and the P20S merged ranges SHALL NOT be
  opened/statted/listed/read under this packet in any form. No cross-split
  combining is needed (R1 lies wholly inside HOLD); the D1-A merge precedent is
  NOT invoked.
- Single-block-first-and-only-use justification (same canonical TRAIN→held-out
  separation as P20M §4, frozen, not re-argued in Stage A/B): NO P20T segment has
  ever been decoded, tuned on, or scored by any EXECUTED NB-Polar packet; 2M
  TRAIN supplies the session hypotheses (worktree prior arrays; orders/K derived
  per §3, never from DEV frames); using R1 as a one-shot scoring population is
  declared once, consumed once, never tuned, never returned to a validation role.
  The remainder stays undecoded.
- Stage B runs on the DECLARED population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet` ONLY (provenance pin frozen in Stage A by manifest cross-check; mismatch blocks; planner performed zero opens/stats/listings) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 2M TRAIN 2187/559872 + VAL 729/186624 + HOLD 729/186624 (JSON-metadata read only) |
| construction/order-derivation input | §3 worktree prior arrays ONLY (off-protected-data; never a DEV frame; never the V25 counts NPZ) |
| DEV frame rule | HOLD `3595..3626` (first 32 frames of the 2M HOLD tail 3595..3644), in (frame_id, pair_idx) order, single contiguous segment (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed; frame arithmetic: 3626−3595+1 = 32; 32×256 = 8192) |
| DEV blocks (N=8192) | ONE block: `3595..3626` (32 frames; 8192 pairs = ONE full block) |
| unused remainder | HOLD frames `3627..3644` (3644−3627+1 = 18; 18×256 = 4608 pairs) recorded never used — counted, never decoded |
| 1.5M remainders | VAL stub `2172..2212` (41 frames / 10496 pairs) + HOLD remainder `2725..2766` (42 frames / 10752 pairs) recorded never used — counted, never decoded, never contacted beyond counting |
| build-frames disjointness (S2-ii) | counts/build frames ⊂ 2M TRAIN `0..2186` (§3 derivation inputs are TRAIN-fitted worktree arrays); DEV R1 = HOLD `3595..3626`; disjoint by split identity; declared frame sets above; the TRAIN-exclusion gate refuses any overlap before any protected content open |
| consumed-1M exclusions | entire 1M pool (any split/subrange) — overlap refuses before any protected content open |
| consumed-1.5M exclusions | all 1.5M TRAIN `0..1659` + VAL `1660..2212` + HOLD `2213..2766` — overlap refuses before any protected content open |
| consumed-2M exclusions | 2M TRAIN `0..2186` as DEV; 2M VAL DEV `2187..2826`; 2M HOLD DEV `2916..3555`; P20S merged ranges `2827..2915` + `3556..3594` — all in any form |
| N=32768 artifact exclusions | N=32768 order/alt files (length/geometry-incompatible) SHALL NOT enter derivation or scoring in any form |
| block count | 1 at N=8192 |
| tag domains | new P20T domain (§6) |

- Fail-closed gate family (frozen in the runner, order (a)→(g), cross-file first):
  (a) CROSS-FILE 2M — DEV content-open path + stat-size/sha pin must equal the
  2M session identity; any 1M or 1.5M path or digest mismatch refuses before any
  SC call (frame integers alone are never identity); (b) INTRA-FILE
  SINGLE-SEGMENT containment — DEV must lie wholly inside HOLD 2916..3644 with
  zero TRAIN/VAL-DEV/HOLD-DEV overlap (incl. zero P20S-merged-range overlap),
  else refuse before any protected content open; (c) CONSUMED-1M EXCLUSION —
  entire 1M pool; (d) CONSUMED-1.5M EXCLUSION — all 1.5M ranges above;
  (e) CONSUMED-2M EXCLUSION — 2M TRAIN-as-DEV + 2M VAL DEV + 2M HOLD DEV + P20S
  merged ranges, incl. the DEV∩build-frames disjointness declaration: DEV R1 vs
  build ⊂ 2M-TRAIN with the frame sets above (S2-ii); (f) WORKTREE-PRIOR-INPUT +
  H-RECOMPUTED + K-DERIVED + DERIVATION-PROGRAM — §3 prior canonical digest +
  floor pin + exact key set + H-literal recomputation within 1e-12 + budget
  derivation display + sampling budget/seeds pin + derivation-program pin (module
  + function + formula-id + R=8 re-freeze + argv + zero-counts attestation) must
  match, else refuse before any SC call; (g) DEV-FRAME-SET-IDENTITY +
  ORDER-POSITION-IDENTITY + TAG-DOMAIN — the exact 32-frame list rule (frames
  3595..3626 in order) + the §6 order triple (new frozen-order-equivalent digest
  on A/O, new spike digest on B, in-packet K literals, `--source 2M`
  vocabulary) + P20T tag-domain pins must match, else refuse before any SC call.

## 5. Preregistered disclosure point (normative — derived in-packet at Stage A from recomputed 2M H; estimate-only until then)

- K rule (new derivation, S2-i satisfied by same-session worktree inputs):
  `K_total = floor((1.3·8192·H−64)/5)` with recomputed 2M H, clipped to
  `[0,16384]`; `(K1,K2)` by exhaustive TRAIN-residual selection frozen before
  DEV (P16 pattern). NEVER carried from (334,6746); NEVER recomputed from alt-H;
  NEVER hand-filled. Until Stage A derives it, the ONLY citable number is the
  ≈1760 ESTIMATE (never a cap, never a gate literal).
- Caps PREREGISTERED at Stage A from the in-packet K (rule `5*(K1+K2)+64`
  key-dependent bits per operational block, `10*8192+63 = 81983` public bits per
  tag, one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_anchor_frozen_order_equivalent (operational) | `<FROZEN_AT_STAGE_A>` | `<FROZEN_AT_STAGE_A>` | `5*(K1+K2)+64` (≈8864 at the ≈1760 estimate) | 81983 |
| B_spike_local_order (probe candidate) | same K1 | same K2 | same as A (Δ vs A exactly 0) | 81983 |
| O_true_l1_oracle (diagnostic) | 0 | carried K2 | `5*K2+64` | 81983 |

- Planned totals (derived at Stage A from the in-packet integers):
  key-dependent `2*(5*(K1+K2)+64) + (5*K2+64)` bits; public `3*81983` bits.
  B-vs-A key-bit delta is exactly 0 (order factor carries ZERO disclosure-size
  delta by design).
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate
  BLOCKS. Per-record fields pin the in-packet point (`prior_source`
  worktree-2M-reuse, `k1/k2/k_total` derived-in-packet, `budget_literal_derived`,
  `l1_order_digest`, `l2_order_digest` (arm-specific: new frozen-order-equivalent
  on A/O, new spike on B), `floor_hit_rate`).

## 6. Arms (frozen; order is the ONLY delta between operational arms; oracle is the diagnostic continuity)

- `A_anchor_frozen_order_equivalent`: frozen greedy SC with newly-derived N=8192
  incumbent `p1` + α1 `p2` tables, NEWLY DERIVED N=8192 worst-first L1+L2 order
  prefixes (first-K1 / first-K2 of the Stage-A
  `<FROZEN_AT_STAGE_A>` digest) at in-packet K1/K2 ("frozen-order equivalent" =
  the same derivation RULE as the P20O 2M orders applied fresh at N=8192; the
  N=32768 order files SHALL NOT be reused in any form). Operational anchor at
  N=8192 (2 SC + 1 P20T-domain tag per block).
- `B_spike_local_order`: frozen greedy SC with tables byte-identical to A (α1),
  SPIKE L2-order positions (first-K2 of the Stage-A new length-8192 spike file,
  digest `<FROZEN_AT_STAGE_A>`) under the carried F-median8 formula-id with the
  re-frozen R=8 decision, with the SAME newly-derived L1 order and SAME
  in-packet K1/K2 (probe candidate; 2 SC + 1 tag per block). Construction, K
  sizes, floor, decoder all byte-identical to A; the disclosed-L2 SET delta IS
  the probed factor.
- `O_true_l1_oracle`: true-L1-conditioned diagnostic with the newly-derived N=8192
  tables + newly-derived frozen-order-equivalent order at carried K2 (provenance
  ORACLE, deployable=false, excluded from every operational aggregate; never a
  correction result; 1 SC + 1 P20T-domain tag per block). Order-factor
  attribution lives in the A-vs-B operational pair ONLY; O never enters any
  operational aggregate.
- No other arms. Block-major (A, B, O) on the single DEV block R1; checkpoint
  after every (arm, block) record; 3 records total. Kernel/representation/
  transform/SC arithmetic unchanged; greedy SC only; no SCL/new kernel/model/
  schema. Stage A performs synthetic TRAIN sampling ONLY under the frozen
  budget/seeds (worktree arrays, zero counts opens, zero real frames); Stage B
  performs pure DEV scoring (5 SC + 3 tags) with ZERO sampling at scoring —
  Stage-B sampling calls pinned at 0, Stage-A genie calls pinned at 0.
- Tag domain (new P20T): master `<FROZEN_AT_STAGE_A>`, prefix
  `<FROZEN_AT_STAGE_A>`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 81983` bits). Prefix/master/arm tokens SHALL differ
  from ALL frozen domains (incl. P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/
  P20I/P20J/P20K/P20M/P20N/P20O/P20Q/P20R/P20S incl. master 2026092360 and all
  test/derivation seeds). Stage A verifies by repo grep that the new master and
  focused-test seeds appear in no tracked file outside the P20T runner/tests/
  packet documents (planner pre-check rule: new-domain grep clean; zero protected
  access).
- Sampling/derivation seeds: synthetic TRAIN sampling budget (block count) +
  derivation seeds pinned at the Stage-A freeze; provenance + zero-counts
  attestation in the construction artifact. Disjointness holds by the grep rule
  above. Stage B takes NO derivation seeds and performs no sampling.
- L2 disclosed-set rule (single-factor guard): arms A/O disclose the first-K2
  positions of the SAME newly-derived N=8192 frozen-order-equivalent file
  (digest-gated `<FROZEN_AT_STAGE_A>`); arm B discloses the first-K2 positions
  of the SAME new spike file (digest-gated `<FROZEN_AT_STAGE_A>`); the L1 set is
  the first-K1 of the SAME newly-derived N=8192 L1 order on all arms. Positions
  are fixed by the frozen Stage-A files, never selected on closed blocks,
  consumed ranges, or DEV data. K sizes frozen identical on A/B; the SET-delta
  between the A and B L2 lists is recorded byte-exact (symmetric difference +
  rank-displacement table, descriptive only).

## 7. Thresholds, endpoints, and mandatory instrumentation (within-N Q-G1/Q-G2 only — no recovery-rate reading)

- Outcome label `TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE` iff ALL
  integrity gates (§9) hold — regardless of per-record outcomes. ANY outcome
  pattern is COMPLETE when integrity holds.
- Choice + justification: within-N geometry-descriptive (no recovery/FER/Wilson
  threshold). This is the single-block persistence probe of the spike-local
  fail-site pattern at N=8192 with the full-block hazard series preserved — n=1
  counts cannot discriminate arms, so there is no empirical basis for ANY count
  threshold here. Any invented gate (e.g. a 62/64-class import) is explicitly
  forbidden. Branch and H2 decisions belong to main-thread analysis AFTER
  acceptance (§16); H2 input from this packet is forbidden.
- NO recovery-rate reading, NO threshold votes, NO FER / reliability /
  efficiency / leakage / key-rate / recovery / scaling-superiority / promotion
  claim. Outcomes (`exact` vs non-exact) are recorded per record for completeness
  but explicitly NOT read as recovery rates. The pre-registered judgment
  quantities are Q-G1/Q-G2 geometry ONLY (see below); any (or no) outcome pattern
  counts as COMPLETE. No efficiency language anywhere (CE ratios never called
  efficiency).
- Status taxonomy frozen: `exact` (tag-verified: outcome exact AND tag_pass AND
  label_match) vs `verify_failed`, `undetected` isolated (never success), plus
  `decode_failed` / `nonfinite` / `resource_abort` via the P20A path. P20A
  four-endpoint separation (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` /
  `pair_exact`) per record. First-error coordinate/layer rows (natural block
  symbol index) recorded per record. Per-record floor-hit fields (`floor_hits`,
  `floor_hit_rate`) complete per record (S2 reporting).
- Carried nine-scalar semantics (ALL NINE per-record SCALARS, scalar fields
  intact, arm-specific order digest): `l2_order_digest` (= new
  frozen-order-equivalent digest on A/O records, new spike digest on B records,
  gated), `l2_prefix_len` (= in-packet K2 on every record, gated),
  `l2_fail_in_prefix`, `l2_fail_hazard_bits`, `l2_fail_nbhd_mean_bits` (frozen
  radius R=8 window, clipped to the block), `l2_prefix_hazard_mean_bits`,
  `l2_fail_nbhd_floor_frac`, `l2_prefix_floor_frac`,
  `l2_fail_in_prefix_u_domain` (frozen PRESENT). Semantics identical to P20Q §7
  at N=8192 (true cells under the record's own arm table; failing fields null
  unless `first_error_layer == L2`; prefix-wide means on every completed record;
  hazards = `-log2` arm-table mass at each position's true `(U1_cond, B, U2)`
  cell with `U1_cond` = hard-L1 candidate on A/B, true high on O).
- Mandatory IR-1..IR-4 (ALL FROZEN PRESENT, same caps/formulas as P20Q §7 at
  N=8192; Stage A pins exact formulas with injected vectors; never post-hoc):
  - IR-1 per-record 64-bin log-spaced hazard histograms {prefix, outside} using
    true cells (~1 KB/record): fields `ir1_hist_edges_bits` (65 float64,
    log-spaced over hazard-bits, frozen formula), `ir1_hist_prefix_counts`
    (64 int), `ir1_hist_outside_counts` (64 int). Split by disclosed L2 prefix
    membership (X-domain, first-K2 of the RECORD'S OWN order file — new
    frozen-order-equivalent on A/O, new spike on B); hazards under the record's
    own arm table. Every completed record (never null).
  - IR-2 hazard-rank percentile of the first-error coordinate (1 float): field
    `ir2_first_error_hazard_rank_pct` (float64 in [0,1], 1.0 = most hazardous;
    fraction of block positions with hazard <= fail-site hazard; null unless
    `first_error_layer == L2` with computable hazard, else null with frozen
    nullability).
  - IR-3 above-threshold prefix counts (≤3 scalars × ≤2 frozen thresholds):
    EXACTLY two thresholds, per-record deterministic, no tuning —
    `ir3_thresh_lo_bits` = 1.0 × record `l2_prefix_hazard_mean_bits`,
    `ir3_thresh_hi_bits` = 2.0 × record `l2_prefix_hazard_mean_bits` (frozen
    multipliers; deterministic per-record, frozen before the run, never fed
    back). Fields (6 scalars): `ir3_thresh_lo_bits`, `ir3_thresh_hi_bits`,
    `ir3_prefix_above_lo_count`, `ir3_prefix_above_lo_frac`,
    `ir3_prefix_above_hi_count`, `ir3_prefix_above_hi_frac` (prefix positions
    using true cells under the record's OWN order; every completed record, never
    null).
  - IR-4 top-k hazardous positions with ranks (k≤16, frozen k=16): fields
    `ir4_topk_coords` (16 int, natural block symbol indices),
    `ir4_topk_hazard_bits` (16 float), `ir4_topk_in_prefix` (16 bool/int,
    X-domain prefix flags under the record's OWN order), `ir4_topk_ranks`
    (16 int, 1-based hazard ranks). Hazard-order listing only; error-coordinate
    join is post-hoc. Every completed record (never null; N=8192 always fills
    16).
- IR-5 full-block 8192-position series preserved per record (the N=8192 full
  block IS 8192 positions). Per record, EXACTLY three binary little-endian
  series + manifest linkage (NO text-JSON float dumps; NO `*.npz`/`*.npy`/
  `*.parquet`, which are git-ignored; encoding satisfies the evidence-size
  standing rule, every committed file ≤ ~2 MB):
  - `<arm>_hazard_bits_f32le.bin`: float32 LE [8192] = 32768 B — true-cell
    hazard bits in natural block order under the record's own arm table
    (`U1_cond` = hard-L1 candidate on A/B, true high on O; same hazard
    definition as the nine scalars/IR recorders).
  - `<arm>_inprefix_u8.bin`: uint8 [8192] = 8192 B — X-domain disclosed-prefix
    flags under the record's OWN order (new frozen-order-equivalent on A/O, new
    spike on B).
  - `<arm>_inu_u8.bin`: uint8 [8192] = 8192 B — U-domain flags under the
    record's own arm table.
  - `ir5_full_manifest.json`: per-file sha256 + shape + dtype + endianness +
    order-identity (new frozen-order-equivalent vs new spike file digest) +
    record linkage + format version (frozen `ir5full-v1`); digests cross-checked
    by the `ir5_full_manifest_identity` gate.
  - Size budget (frozen): 32 KiB hazard series + 8 KiB + 8 KiB = 48 KiB per
    record; 3 records ≈ 144 KiB; full Stage-B root ≤ ~1 MB; every committed file
    ≤ ~2 MB with the largest single file at 32768 B. The JSONL records carry
    IR-5 manifest REFERENCES (file names + digests), never inline float arrays.
  - Writer code point (frozen at Stage A): successor module
    `n8192_tail_persistence_probe.py` (RECOMMENDED name; Stage A confirms or
    freezes a written equivalent with justification + re-review), full-block
    writer function pinned at Stage A — called post-decode (after tag scoring)
    alongside the nine-scalar and IR-1..IR-4 recorders (the P20Q
    `_ir_hazard_diagnostics` code point is the carried-over callsite pattern).
  - Truth-isolation boundary (normative): block truth (high/low/bob) and the arm
    tables enter the IR writers for RECORDING ONLY after all SC calls for the
    record have completed; outputs are written into the record dict / `.bin`
    files and never passed to any operational decode path, metric builder, or
    disclosure/order decision. A focused truth-isolation sentinel test pins this
    boundary (mutating truth changes no metric/decision input).
- Judgment form (pre-registered Q-G1/Q-G2 geometry ONLY; NO decision asserted
  here): the accepted run must supply (i) full-block 8192 series tables
  (per-record full-8192 mean/tail mass under the record's own order, from the
  IR-5 bins); (ii) spike-order coverage of disclosed-set mismatch positions —
  the byte-exact A-vs-B symmetric-difference set characterized by its
  hazard-rank distribution under each order (purely positional; NOT an outcome
  comparison); (iii) IR-1 tails under both orders (prefix vs outside tail-mass
  contrast A vs B — the Q-G2 contrast); (iv) full-scope top-128/top-1024
  concentration per record's own order (the Q-G2 concentration); plus the nine
  carried scalars (with arm-specific order digests) for continuity and the
  byte-exact A-vs-B set-delta table. Q-G1 is judged by whether the fail-site
  pattern (undisclosed below-mean coord-class site with floor-rate elevation,
  paired A vs B on the same block) recurs — recorded, never decided in-packet.
  These quantities are not recovery rates, not thresholds, not pass/fail votes.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized
  execution; no rerun, no seed change, no prior/budget/order/construction tuning
  after preregistration. Execution-error rerun only as a recorded repeat of the
  identical freeze, never as tuning. P20H–P20S/R1 spent attempts do NOT transfer
  (independent packet).
- Reads (split-counted): counts-calibration opens 0/0 at every stage (new
  derivation is worktree-only; the V25 counts NPZ is never opened/statted/
  listed) + DEV R1 open 1/1 reserved for Stage B (parquet, consumed at first DEV
  R1 content open). 1M reads 0; 1.5M reads 0; 2M non-DEV reads 0 (remainder +
  all 1.5M remainders counted never-decoded, never contacted beyond counting).
  Any reopen, new calibration/derivation on real frames, real-frame use for
  derivation, or DEV refit is forbidden. Worktree-file loads and the Stage-A
  synthetic derivation are worktree reads, not protected opens.
- SC/tag/genie/sampling budget: Stage-A synthetic TRAIN sampling = the frozen
  budget (block count + seeds pinned at the Stage-A freeze; worktree arrays
  only) + Stage-A genie 0; Stage-B pure DEV scoring 5 SC (1 block × (2+2+1)) + 3
  tags + 3 records with ZERO sampling at scoring (Stage-B sampling 0).
  Derived per-record recomputation must equal counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  accounting; abort is BLOCKED, never success. Wall/RSS ceilings frozen in the
  Stage-A freeze supplement (P20S-class envelope — 1200 s external timeout, 2
  GiB virtual/RSS caps, single thread — is the not-to-exceed precedent at the
  strictly smaller N=8192 scoring budget; the synthetic-sampling compute budget
  is pinned alongside the sampling budget/seeds).
- Strategy stop rules binding: no tuning on closed blocks or the new DEV after
  the one shot; no reuse of consumed 1M pool (any split/subrange), any consumed
  1.5M range (TRAIN 0..1659, VAL DEV 1660..2043, stub 2172..2212, HOLD
  2213..2766), consumed 2M TRAIN-as-DEV / VAL DEV 2187..2826 / HOLD DEV
  2916..3555 / P20S merged ranges, remainder 3627..3644 beyond counting, or any
  other session; no N=32768 file reuse in any form; no second factor after any
  probe pattern; no oracle-as-operational; no population-reliability inference
  from this single block alone; no recovery-rate reading of this packet's
  outcomes; no tuning inside this packet; no H2 verdict and no H2 input inside
  this packet; no cross-N inference or pooling.
- Spike-window guard (pre-registered): the `P20T_STOP_SPIKE_WINDOW_UNREFROZEN`
  guard fires if the R=8 vs-8192-geometry re-freeze decision (rationale +
  window rule, §3) is absent or contradictory at the Stage-A freeze — derivation
  SHALL NOT proceed until it is recorded.
- SCL entry gate UNCHANGED (unlocks nothing by itself; SCL work runs on synthetic
  X11, never on this block).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B fifteen files)

- Stage-A freeze pins (zero protected opens): worktree-prior path + canonical
  digest replay + H-literal recomputation + `p_b` cross-check + floor pin;
  sampling budget (block count) + derivation seeds + derivation-program pin
  (module + function + formula-id + R=8 re-freeze + argv + zero-counts
  attestation); K derivation display + (K1,K2) integers + fresh
  frozen-order-equivalent digest + fresh spike digest + formula-id pin + R=8
  re-freeze decision + A-vs-B set-delta table; fresh TRAIN-only feasibility
  outcome; exact module path + N-flag Stage-B command verbatim + population
  integers + S2-ii declaration + caps from in-packet K + budgets + tag domain +
  grep proof + P16-pattern construction digest + IR-3 multiplier pins (1.0×/2.0×)
  + IR-4 k=16 + IR-5 8192 encoding/size pins; recorded alongside this packet.
  Stage-A product identities: construction/allocation artifact + fresh
  frozen-order-equivalent order file + fresh spike order file (digests pinned at
  Stage A) under this queue dir; worktree prior path points at the P20O queue
  dir (digest replay-expected, never re-derived).
- Stage-B root:
  `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE/n8192_tail_persistence_probe/`
  (exactly fifteen files; per-(arm, block) checkpointing; pure DEV scoring —
  zero scoring sampling; one DEV content open; no reopen/rerun). Root must be
  ABSENT at Pre-EXECUTE.
- Fifteen files: `frozen_plan.json`, `input_and_derivation_identity.json`
  (worktree-prior digest-gate proof + H-recomputation proof + K-derivation
  display + construction digest-gate proof + fresh frozen-order-equivalent
  digest-gate proof + fresh spike digest-gate proof + derivation-program pin
  (module + function + formula-id + R=8 re-freeze + argv + sampling budget/seeds
  + zero-counts attestation) + formula-id pin + A-vs-B set-delta table +
  tag-domain pins + grep proof + split manifest + DEV integers + DEV∩build-frames
  disjointness declaration with frame sets + IR-3 multiplier pins + IR-4 k pin +
  IR-5 8192 encoding/size pins + fresh TRAIN-only feasibility outcome),
  `per_block_arm_outcomes.jsonl` (3 records at completion, each carrying the nine
  scalars with arm-specific order digest + IR-1..IR-4 payload with frozen
  nullability/caps + IR-5 manifest references), `aggregate_summary.json` (incl.
  the Q-G1/Q-G2 geometry tables: full-block 8192 series summaries +
  mismatch-coverage table + IR-1 tails under both orders + full-scope
  top-128/1024 concentration + A-vs-B set-delta table — all explicitly labelled
  non-recovery), `report.md`, `ir5_full_manifest.json` (per-file sha256 + shape +
  dtype + endianness + order-identity + record linkage + `ir5full-v1`), plus the
  nine IR-5 `.bin` files (`A_hazard_bits_f32le.bin`, `A_inprefix_u8.bin`,
  `A_inu_u8.bin`, `B_…×3`, `O_…×3`). Per-record §7 endpoints + first error
  coordinate/layer, zero-count hits, floor hits + floor-hit rate + log loss,
  true-H vs candidate-H L2 NLL, taxonomy, construction-point fields
  (`l2_construction` alt-α1-equivalent at N=8192 on all arms, `k1/k2/k_total`
  derived-in-packet, `prior_digest` (worktree reuse), `l1_order_digest`,
  `l2_order_digest` arm-specific) + the NINE scalars + IR-1..IR-4 fields (all
  PRESENT per the Stage-A freeze) + IR-5 file references with digests.
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); genie
  call counts (Stage-A 0 + Stage-B 0) + sampling calls (Stage-A frozen budget,
  Stage-B 0) + SC counts (L1/L2 split: A 2 / B 2 / O 1) + tag counts exact;
  block SER/NLL (recorded, never a reliability claim); wall/RSS; per-arm
  floor-hit rate + per-arm prefix hazard means + Q-G1/Q-G2 geometry tables
  reported. NO per-arm exact counts are read as recovery rates; transition cells
  are NOT computed (counting vocabulary is out of scope for this packet).
- Integrity gates in frozen order (all true or BLOCKED):
  `derivation_program_identity`; `worktree_prior_input_identity` (prior canonical
  digest + floor pin + exact key set + H literals within 1e-12 + `p_b`
  cross-check, worktree-file only, zero counts opens);
  `session_h_recomputed`; `k_derived_in_packet` (budget-literal display with
  recomputed H + floor/clip + exhaustive TRAIN-residual (K1,K2) frozen before
  DEV; never carried, never alt-H, never hand-filled);
  `construction_allocation_identity` (P16-pattern derivation record + artifact
  digest, Stage-B equality); `frozen_order_identity_A` (new length-8192
  permutations, Stage-A digest, Stage-B file-bytes equality, permutation-valid +
  K-prefix + L1 checks); `spike_order_identity_B` (new length-8192 spike
  permutation under carried F-median8 + re-frozen R=8, Stage-A digest, Stage-B
  equality, permutation-valid + K2-prefix + L1-carried checks);
  `order_set_delta_recorded` (symmetric difference + rank-displacement table
  byte-exact, size-delta exactly 0); `dev_split_manifest_identity`;
  `dev_block_range_identity` (§4 gate family (a)→(g): cross-file 2M identity
  first, then single-segment intra-file containment, then consumed-1M,
  consumed-1.5M, consumed-2M exclusions incl. the DEV∩build-frames disjointness
  declaration, then worktree-prior + H + K-derived + derivation-program pins,
  then DEV-frame-set-identity + order-position-identity + tag-domain pins);
  `target_population_contract`; `dev_population_exact` (32 frames / 8192 pairs /
  256 rows per frame / pair indices / symbol range, single-segment order);
  `blocks_exact_with_declared_remainder` (ONE exact DEV range per arm in
  block-major slot order + never-used remainder 18 frames / 4608 pairs +
  counted-never-decoded 1.5M stubs 83 frames / 21248 pairs);
  `three_records_exact`; `sampling_calls_exact` (Stage-A frozen budget +
  Stage-B 0); `genie_calls_exact` (Stage-A 0 + Stage-B 0); `sc_calls_exact`
  (derived 5); `tags_exact` (derived 3);
  `orders_valid_k_prefixes_within_registered_arms` (new frozen-order-equivalent
  prefixes on A/O + new spike prefix on B + α1×3 + in-packet K literals);
  `hazard_instrumentation_complete` (all nine §7 scalars present with correct
  nullability + arm-specific order digest on every completed record);
  `ir_payload_complete` (IR-1..IR-4 all PRESENT with frozen caps/nullability +
  IR-5 8192 full-block: nine `.bin` files byte-present with manifest digests
  matching on every completed record); `ir5_full_manifest_identity` (per-file
  sha256 + shape + dtype + endianness + order-identity + `ir5full-v1`, all
  equal); `evidence_size_rule_met` (every committed file ≤ ~2 MB; largest single
  file 32768 B); `train_feasibility_fresh` (TRAIN-only feasibility computed at
  Stage A from the new point with zero DEV reads; mismatch ends the packet at
  Stage A with DEV untouched); `floor_hit_rate_reported`; `oracle_isolation`;
  `buckets_disjoint_exhaustive` (unique arm/block + schema); `undetected_zero`;
  `nonfinite_zero`; `truth_isolation` (incl. the IR recorder sentinel);
  `disclosure_recount_exact`; `one_open_per_protected_input` (counts 0 + DEV 1);
  `input_stat_unchanged`; `no_unregistered_access`;
  `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (new-derivation implementation + orders/K/tag-domain freeze + injected
  tests + derivation-record; authorized separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_n8192_tail_persistence.py -p no:cacheprovider`
  (RECOMMENDED test path; Stage A confirms or freezes a written equivalent with
  justification + re-review) using injected/synthetic inputs and a fresh additive
  `workspace/p20t/<uuid>/` temp root; protected-open audit declared separately
  (counts 0 + DEV 0 at Stage-A close). Safe smoke per `AGENT_PROJECT_MEMORY.md`
  §4 stays valid.
- Stage-A derivation + verification (ZERO protected opens; worktree-file digest
  recomputation + manifest-metadata confirmation ONLY): recompute the worktree
  prior canonical digest + H literals + `p_b` from the frozen worktree file;
  run the §3 derivation program under the frozen sampling budget/seeds (worktree
  arrays only, zero counts opens, zero real frames) to emit the construction/
  allocation artifact + fresh frozen-order-equivalent orders + fresh spike order
  under carried F-median8 with the re-frozen R=8 decision; pin K derivation
  display + (K1,K2) + all file-bytes digests + formula-id pin + R=8 re-freeze +
  program pin + set-delta table + fresh TRAIN-only feasibility outcome; confirm
  the §4 DEV integers against the split-manifest JSON metadata (no parquet/NPZ
  open/stat/listing); grep-verify the §6 tag/test-seed freshness. Template (pins
  filled at Stage A; all flags required, no production default):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
<STAGE_A_FROZEN_MODULE> --verify-derivation --prior <WORKTREE_PRIOR_PATH> --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --n 8192 --sampling-blocks <FROZEN_AT_STAGE_A> --derivation-seeds <FROZEN_AT_STAGE_A> --spike-formula <FROZEN_AT_STAGE_A> --spike-window-r8-refrozen <FROZEN_AT_STAGE_A> --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A>
```
  Stage A confirms the module path (new `FROZEN_N = 8192` runner per the §2 delta
  list d1–d9, or freezes a written equivalent with justification) and the
  `--source` vocabulary (only `2M`). Forbidden by default: `longrun_*`,
  `minrerun_*`, `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data, full
  sweeps.
- Stage B execution command (RECOMMENDED here, frozen verbatim at Stage A with
  the `<FROZEN_AT_STAGE_A>` pins filled; NOT AUTHORIZED until independent
  Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 <STAGE_A_FROZEN_MODULE> --prior <WORKTREE_PRIOR_PATH> --prior-digest <FROZEN_AT_STAGE_A> --source 2M --floor 1e-15 --n 8192 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction <FROZEN_AT_STAGE_A> --construction-digest <FROZEN_AT_STAGE_A> --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames 3595 3626 --block-frames 32 --remainder-frames 3627 3644 --tag-master <FROZEN_AT_STAGE_A> --tag-prefix <FROZEN_AT_STAGE_A> --chunk-rows <FROZEN_AT_STAGE_A> --tag-bits 64 --order-file <FROZEN_AT_STAGE_A> --order-digest <FROZEN_AT_STAGE_A> --spike-order-file <FROZEN_AT_STAGE_A> --spike-order-digest <FROZEN_AT_STAGE_A> --spike-formula <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE/n8192_tail_persistence_probe
```
  All flags required, no production default; three hardcoded arms with the order
  swap pinned (never CLI-tunable: A = α1 + newly-derived frozen-order-equivalent
  at in-packet K; B = α1 + newly-derived spike order at in-packet K; O =
  newly-derived frozen-order-equivalent true-L1 oracle at carried K2); Stage-B
  prior path MUST equal the §3 worktree pin; `--alpha` takes no Stage-B value
  (construction is frozen in the Stage-A artifact). Stage A fills every
  `<FROZEN_AT_STAGE_A>` pin (sampling budget/seeds, `--prior-digest`,
  `--k1/--k2` derived-in-packet, order/spike digests, `--spike-formula` +
  R=8 re-freeze, construction path/digest, tag master/prefix, chunk-rows) plus
  the `--source` vocabulary (only `2M`) and the IR-3 multiplier + IR-4 k + IR-5
  8192-encoding pins in `frozen_plan.json`. The single-segment frame flags (or a
  written equivalent frozen at Stage A) enforce gate (g). Forbidden by default as
  above. This command SHALL NEVER be pointed at any N=32768 frozen-point runner.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git
  show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: construction/allocation artifact (P16-pattern derivation record +
  digest) + fresh frozen-order-equivalent order file (+ file-bytes digest) +
  fresh spike order file (+ file-bytes digest + formula-id pin + R=8 re-freeze +
  derivation-program pin with sampling budget/seeds + A-vs-B set-delta table +
  zero-counts attestation) + K derivation display + (K1,K2) + fresh TRAIN-only
  feasibility outcome + reuse-verification freeze supplement (§3 digest/H/`p_b`
  replays + sampling budget/seeds + K derivation + order/spike digests +
  formula-id + R=8 re-freeze + program pin + set-delta table + population + caps
  from in-packet K + budgets + tag domain + grep proof + IR-3 multipliers + IR-4
  k + IR-5 8192 encoding/size pins + module path + all commands verbatim) +
  implementation notes (exact files, diffs, test commands/results, frozen
  derivation/population/cap/command, feasibility outcome) + new `FROZEN_N = 8192`
  runner + focused injected tests. NO other new artifacts (worktree prior path
  points at the P20O queue dir; digest replay-expected). Protected content opens
  0 at Stage-A close (counts 0/0 + DEV 0/1; synthetic sampling worktree-only).
- Stage B (only after authorization): evidence root (§9, fifteen files) +
  `OPERATOR_RETURN.md` (+ freeze supplement, `PRE_EXECUTE_REVIEW.md`,
  `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec reduced-N delta: already frozen (RN-1 PASS 2026-09-20;
  `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-reduced-n-persistence/`
  + `tasks.md` reduced-N section, same umbrella change). Stage A stages no spec
  edit.

## 12. Allowed work

- New `FROZEN_N = 8192` runner (per §2 d1–d9) + N=8192 derivation program
  (worktree-prior-only synthetic TRAIN sampling under frozen budget/seeds, §3
  contract, carried F-median8 formula-id with re-frozen R=8) + focused injected
  tests (temporary roots only).
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
  `l2_alt_hold_ir_2m.py` (gate/population/IR record-writer pattern references),
  `l2_order_position_1p5m.py` (dual-order + derivation-program pattern
  references), `l2_mechanism_probe_2m.py` (mechanism-probe + IR-5 writer pattern
  reference) (+ `construction.py` / `prior.py` / `sc.py` contracts as called).
- ZERO protected opens in Stage A: worktree-file digest recomputation of the §3
  prior inputs (H recomputation + `p_b` + floor/key-set pins) + P16-pattern
  synthetic derivation from the worktree prior arrays under frozen budget/seeds
  (zero counts opens, zero real frames, zero genie) + split-manifest
  JSON-metadata confirmation of the §4 integers + grep-verification of the §6
  tag/test-seed freshness + closed-form IR formula pins on injected vectors
  (zero real frames).
- Packet docs + Stage-A freeze supplement/return/review files + Stage-B evidence
  root (root only after Stage-B authorization) + the §3 derivation identity
  (§§3/9).

## 13. Forbidden work

- Any NPZ/parquet content open or stat/listing of DEV R1/remainder segments, 2M
  VAL-DEV, 2M TRAIN, 2M HOLD-DEV, P20S merged ranges, any 1M split, or any 1.5M
  split in Stage A (Stage-A protected opens: counts 0/0, DEV 0/1); any counts
  open at any stage (0/0 always); any K carried as an absolute from (334,6746),
  recomputed from alt-H, or hand-filled (S2-i + AGENTS.md §5.5; derivation only
  from recomputed 2M H); any N=32768 order/alt file use in any form; any `--n
  8192` passed to a frozen-point N=32768 runner; any derivation or sampling on
  real DEV frames at any stage; any decoder execution before Pre-EXECUTE PASS +
  pasted Stage-B authorization; any spike derivation under any formula other
  than carried F-median8 with the re-frozen R=8 decision.
- Any change to GF32/transform/SC arithmetic, floor value, carried formula
  shapes, disclosed-size rule (B−A = 0), tag scheme semantics, outcome
  precedence, accepted evidence roots, P20O/P20Q/P20R/P20S products, X08/X09/X10/
  X11/X17 probe roots, H2 run root, or `src/` + `experiments/` + `tools/` frozen
  baseline. No disclosure-size change; no order change beyond the single spike
  L2 position set at identical K; no decoder change.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the
  consumed 1M pool (any split/subrange), any consumed 1.5M range (TRAIN
  0..1659, VAL DEV 1660..2043, stub 2172..2212, HOLD 2213..2766), consumed 2M
  TRAIN-as-DEV / VAL DEV 2187..2826 / HOLD DEV 2916..3555 / P20S merged ranges,
  remainder 3627..3644 beyond counting; no second construction, no construction
  sweep, no bounded search, no second order beyond the single spike set, no
  fourth arm, no disclosure change; no tuning; no new-block peeking before the
  authorized attempt; no calibration on DEV; no H2 verdict and no H2 input
  inside this packet; no recovery-rate reading of this packet's outcomes at any
  stage; no cross-N inference or pooling.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push; no self-acceptance; no P20S rerun under this packet. No efficiency
  language anywhere. No text-JSON float dumps of the full-block series; no
  `*.npz`/`*.npy`/`*.parquet` evidence files.

## 14. Acceptance IDs

- `P20T-R1`: new-derivation contract verified (P16-pattern construction/
  allocation from worktree-prior arrays only; synthetic sampling budget + seeds
  pinned; worst-first length-8192 orders; K derived in-packet from recomputed H
  with (K1,K2) by TRAIN residual never carried from (334,6746); carried
  F-median8 with R=8 re-frozen as a new decision; new tag domain; new
  `FROZEN_N = 8192` runner + focused tests; zero counts opens at every stage).
  Derivation-gate BLOCKED → planner rework, never a Stage-B fallback.
- `P20T-R2`: single-segment population gated (DEV R1 3595..3626 → ONE N=8192
  block; remainder 3627..3644 + 1.5M stubs never used; no cross-split combining;
  D1-A not invoked; consumed 1M pool + all consumed 1.5M ranges + consumed 2M
  TRAIN-as-DEV + VAL DEV + HOLD DEV + P20S merged ranges + N=32768 files excluded
  by source-tagged gates incl. the exact 32-frame list rule + S2-ii declaration;
  Pre-EXECUTE-approved); 1M/1.5M/2M-consumed untouched in every form.
- `P20T-R3`: disclosure point preregistered from the in-packet K
  (`5*(K1+K2)+64` operational with B−A exactly 0; `5*K2+64` oracle; 81983
  public; totals derived at Stage A), recount mismatch 0; set-delta recorded
  byte-exact with size-delta exactly 0; CE ratios never called efficiency.
- `P20T-R4`: arm pins (A newly-derived frozen-order-equivalent + B spike-local
  at identical K + shared newly-derived L1 rule + O newly-derived
  frozen-order-equivalent oracle continuity, §3 α1 rule, formula-id +
  derivation-program pin with sampling budget/seeds) frozen before execution,
  unchanged after; no tag-guided selection, no evidence reuse, no post-hoc
  re-picking, no re-derivation.
- `P20T-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9;
  `undetected` isolated; oracle arm never operational; first-error
  coordinate/layer rows + per-record floor-hit fields + all nine scalars
  (arm-specific order digest) complete per record with correct nullability +
  IR-1..IR-4 ALL PRESENT with P20Q-identical caps/nullability on every completed
  record (IR-3 two thresholds 1.0×/2.0× prefix-mean; IR-4 k=16; record's OWN
  order used for every prefix flag) + IR-5 full-block 8192 (nine `.bin` files +
  `ir5full-v1` manifest with matching digests on every completed record:
  48 KiB/record); instrumentation + IR recorded-only (truth-isolation sentinel
  green).
- `P20T-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning;
  split-counted reads (counts 0/0 + DEV 1/1 + 1M 0 + 1.5M 0 + 2M-non-DEV 0); 5
  SC / 3 tags / 3 records derived; Stage-A synthetic sampling = frozen budget,
  Stage-B sampling 0, genie 0+0, zero sampling at scoring; resource aborts via
  P20A path with accounting preserved; stop rules + spike-window guard + SCL gate
  intact; comparability boundary intact (non-transfer list restated, zero H2-join
  rows contributed, no cross-N pooling).
- `P20T-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded (Pre-EXECUTE
  explicitly adjudicates §3 worktree-input/H/K-derivation + construction record
  + formula-id carried text + R=8 re-freeze + sampling budget/seeds pin + fresh
  TRAIN-only feasibility outcome + §5 in-packet-K caps + §4 gate family (a)→(g)
  incl. the exact 32-frame list rule + §2 runner-derivation design + §7
  nine-scalar + IR-1..IR-4 boundary + IR-5 8192 encoding/size rule +
  arm-specific order-digest rule); main-thread acceptance owns the label;
  within-N Q-G1/Q-G2-descriptive only, no recovery-rate/FER/qualification/
  promotion/H2-verdict language; honest-scope statement (§0) repeated verbatim
  in the return.
- `P20T-R8`: Stage-A suites green on injected data with the zero-protected-open
  audit (counts 0/0 + DEV 0/1 at Stage-A close; 1M/1.5M/2M-consumed non-access in
  every form; full accepted predecessor suite green on injected/tiny inputs,
  temporary roots, fresh test seeds only); no commit/push; frozen dirs
  byte-untouched except the §12 manifest.
- `P20T-R9`: K-estimate-only rule + non-transfer boundary enforced (≈1760
  estimate-only display with recomputed H, never a literal before Stage-A
  derivation; never hand-filled; 1/4→2/5→4/5 chain, H2 verdicts over the 59-row
  join (P20N 16 + P20O 20 + P20Q 20 + P20S/R1 3; P20R 4 read-only never joined),
  IR-5 32768 geometry, and all leakage literals do NOT transfer; N=8192 block
  contributes zero H2-join rows) + fresh-feasibility gate (TRAIN-only outcome
  frozen alongside this packet/STATUS BEFORE any DEV contact; MISMATCH → DEV
  untouched, no Stage-B request). Gate-fired → main-thread re-frame, never a
  Stage-B fallback.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs
`P20T-R1..R9` (stage-appropriately) complete with changed files + exact
commands/results + artifact inventory (incl. worktree-prior digest replay +
H/K derivation display + fresh order/spike digests + formula-id + R=8 re-freeze
+ program pin with sampling budget/seeds + set-delta table + feasibility
outcome + population + caps) + split open audit (counts + DEV + 1M + 1.5M +
2M-non-DEV separately); or (b) a concrete blocker with failing command, exact
error/traceback, attempted remedies, and the ONE decision needed from the main
thread. "Still incomplete" is not a completion report. The operator never marks
its own work accepted and never authorizes Stage B.

Blocker list: NONE open at freeze. Pre-registered guards retained as consistency
checks only: `P20T_STOP_SPIKE_WINDOW_UNREFROZEN` (§8; fires only if the R=8
re-freeze decision is absent/contradictory) and the fresh-feasibility gate
(P20T-R9; fires only on TRAIN-only feasibility mismatch, ending the packet at
Stage A with DEV untouched).

## 16. Deferred options (not in this packet)

- New-acquisition ladder: any real-data block beyond DEV R1 requires newly
  acquired frames (the post-P20T never-decoded ledger holds only the 18-frame
  remainder + 83 low-information 1.5M frames + the P20S-consumed ranges = no
  further N=8192 block except by new acquisition or a new N/design under a new
  OpenSpec change, not a packet). Trigger = new frames landed + their own
  freeze, tag domain, and reviews. Nothing is auto-triggered inside this packet.
- Bounded search at the fixed point → follow-up planning (deferred): trigger =
  accepted P20T Q-G1/Q-G2 geometry tables analyzed by the main thread. This
  packet prejudges none of it and licenses no reliability claim.
- Second single construction form → follow-up planning (deferred): trigger =
  main-thread reading of the accepted P20T geometry against the α1 form. Only
  then does exactly ONE second form become the next single factor on new data by
  main-thread planning. Nothing is auto-triggered inside this packet.
- SCL via X11 synthetic probe → parallel mainline algorithm work, zero
  protected-data cost (deferred from this packet, active elsewhere): the carried
  F-median8 formula-id is shared deterministically with X11 for synthetic
  validation subject to the re-frozen R=8 vs-geometry decision; list-survival is
  decided there, never on this block.
- 1.5M closure: VAL stub 2172..2212 (41) + HOLD remainder 2725..2766 (42) stay
  never-decoded; no 1.5M packet follows without new acquisition or a new N/design
  (which needs a new OpenSpec change, not a packet).
- H2 adjudication → main-thread analysis on the N=32768 archive ONLY (deferred,
  never in-packet): this N=8192 block contributes ZERO rows to the 59-row H2 v2
  join and supplies NO H2 input; the H2a–H2e verdicts stay with the N=32768
  analysis. This packet supplies Q-G1/Q-G2 within-N quantities and licenses no
  H2 verdict, no threshold, and no recovery-rate reading.
- Cross-N readings → forbidden outright (not deferred): no scaling, superiority,
  efficiency, leakage, key-rate, or reliability comparison between N=8192 and
  N=32768 under any framing.
- DEV R1 is CONSUMED by this packet regardless of outcome; remainder 3627..3644
  and all 1.5M remainders stay never-decoded. Any follow-up packet needs its own
  freeze, tag domain, and reviews.

(End of file)
