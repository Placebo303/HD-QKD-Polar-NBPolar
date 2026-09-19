# Phase 4-P20N — Fixed-disclosure ONE-alternative-L2-construction packet on type2_1p5M_20260121_183806 HOLD (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage-A alt-table freeze, Stage-B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read, decoder execution, or commit/push is authorized by this file.
- Predecessor: `NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M` terminal
  `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; DEV open 1/1
  SPENT on 1.5M VAL 1660..2043; 9/9 records; 25/25 gates PASS; G0 0/3 L1 first
  errors + G1 0/3 with L1 breakthrough (2/3 hard-L1-exact; first errors L2/26,
  L1/848, L2/31) + G2 oracle 0/3 (L2/26, L2/3646, L2/31); undetected 0; SC
  15/15; tags 9/9; recount 0; key 308376 / public 2949687; 2M pristine by
  non-access; Pre-RESULT PASS; acceptance in `MAIN_THREAD_ACCEPTANCE.md`).
- X09/X09-R1 attribution probe (reviewed PASS;
  `workspace/probes/nbpolar_x09_l2_attribution_r1/results.json`, delta doc
  `.workbuddy/queue/NBPOLAR-X09-L2-ATTRIBUTION/X09R1_DELTA.md`):
  H1 NOT SUPPORTED (every L2-failing block has positive ideal-length margin:
  G1 NLL 28,764–32,807 vs cap 35,164; G2 NLL 27,302–27,491 vs cap 33,509;
  N*H2 = 26,226 bits); H3 NOT SUPPORTED (failing-block floor hits 43/43/30/25/25
  vs in-sample per-block max 3,262); H2 NOT DECIDABLE from persisted artifacts
  (needs decode-time instrumentation); `first_error_coord` is a natural block
  symbol index (`l1_order_1p5m.py:1399-1411`).
- Historic P20D definition (P20C §16, P20L §16): "fixed disclosure + ONE
  preregistered alternative L2 construction on independent development data",
  with construction work "constrained tuning, not open-ended" (P20C wording).
  P20L's prior objection ("the oracle evidence exonerates the L2 construction")
  is FLIPPED by P20M's out-of-sample oracle failure (G2 0/3 at candidate K2
  where in-sample oracle arms were 3/3 exact). §16 triggers fired per P20M
  `MAIN_THREAD_ACCEPTANCE.md` §3 (oracle non-exact AND bottleneck-layer move).
- User decision (2026-09-19): next packet = alternative L2 construction +
  mandatory instrumentation; data segment = HOLD 2213..2766 (554 frames, never
  touched; 4 blocks of 128 + 42-frame remainder). P20M consumed TRAIN 0..1659
  (all DEV segments) and VAL 1660..2043; VAL remainder 2044..2212 stays
  untouched; 2M stays pristine.
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2
  and `docs/nbpolar/ROADMAP.md`.
- Gate discipline: any standing long-horizon authorization does NOT collapse
  Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_1p5M_20260121_183806` (1.5M), scoring population
  first-use of 1.5M HOLD (see §4). The 2M session
  (`type2_2M_20260121_183657`) is registered but RESERVED pristine (see §4, §16).

## 0. Planner header (OpenSpec workflow)

- **Goal**: Test exactly ONE preregistered alternative L2 construction at fixed
  disclosure (K1=331/K2=6689 carried over from P20M, zero K change) on four NEW
  1.5M HOLD blocks at N=32768 (four arms A/B/C/D, new P20N tag domain), with
  the mandatory X09-R1 decode-time instrumentation persisted as per-record
  SCALARS. Decide whether the alternative L2 conditional restores any complete
  block where the incumbent raw-MLE+floor L2 fails — operationally (B vs A)
  and under true-L1 conditioning (D vs C).
- **Non-Goals**: No K/disclosure change of any kind; no L1 change (prior, K1,
  L1 order all frozen P20M); no L2 order change (shared frozen P20M L2 prefix
  on all arms); no second construction, no construction search/sweep, no DEV
  tuning; no λ retune; no floor-value change (floor step retained formally);
  no SCL/new kernel/model/schema; no FER/qualification/promotion claim; no
  reuse of any consumed/closed range; no VAL-remainder use; no 2M first use;
  no closure of the 1M-HOLD thread.
- **Impact Scope**: New thin runner + focused injected tests + P20N OpenSpec
  delta (`specs/nbpolar-phase4-p20n/spec.md` + `tasks.md` P20N section, same
  umbrella change `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A freeze
  (incl. alt-L2-table artifact) + implementation notes + Stage-B evidence root.
  No change to `src/`, `experiments/`, `tools/`, P16 construction file, P20M
  accepted roots (`raw_prior_1p5m.npz`, `raw_prior_orders_1p5m.json`,
  `raw_prior_val_1p5m/`), P12–P20M accepted modules, X08/X09 probe roots, or
  `results/` / `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20N-R1..R8 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance.
  Descriptive-only label; `undetected` isolated; oracles never operational.
- **Tasks**: (planner task list for coder agents) H1 derive + freeze alt-L2
  table (§3, R1); H2 freeze population/gates (§4, R2); H3 freeze caps from the
  carried point (§5, R3); H4 freeze single-factor arm swap, A/C incumbent pins
  (§2/§6, R4); H5 wire endpoints/taxonomy + mandatory hazard instrumentation
  (§7, R5); H6 enforce one-shot budget/stop (§8, R6); H7 Stage-A suites green
  with zero-protected-open audit (R8); H8 independent Pre-EXECUTE adjudication
  of alt derivation + K-literal + population gates (R7); H9 single authorized
  Stage-B attempt (R6/R7); H10 independent Pre-RESULT + acceptance.
- **Honest scope** (binding on proposal/design/packet/return language): this
  packet tests ONE preregistered alternative L2 construction at fixed
  disclosure on the first HOLD-segment use; it can restore L2 or falsify this
  construction; a budget-infeasible construction is returned without consuming
  HOLD; it licenses no reliability/recovery claim; 2M and VAL remainder
  remain untouched; the 1M-HOLD thread stays open.

## 1. Mission

With ONE preregistered construction change against P20M — the L2 conditional
rebuilt from the SAME frozen counts under unit-Laplace smoothing (§3), L1 path
byte-identical, disclosed sets byte-identical, K1=331/K2=6689 byte-identical —
and everything else carried over (floor step retained formally, N=32768,
greedy SC only, new P20N tag domains only), zero further tuning:

> Does the Laplace-α1 L2 conditional restore any complete block on four NEW
> 1.5M HOLD blocks (2213..2724) — operationally and under true-L1 conditioning —
> and what hazard/coverage state do the failing coordinates carry under each
> construction?

P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, P20K DEV 1152..1535 are
CONSUMED; TRAIN remainder 1536..1659 is documented insufficient; P20M VAL DEV
1660..2043 is CONSUMED (9 records, attempt SPENT); VAL remainder 2044..2212 is
RESERVED never-decoded under this packet; P20L never executed (zero
consumption). All branches after this packet are deferred to §16 and must not
be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- Disclosure route closed on 1.5M calibrated data (descriptive, convergent
  H/I/J/K) and the VAL operating-point test (P20M): corrected prior + session
  budget moved the bottleneck L1→L2 (2/3 hard-L1-exact) but restored 0 blocks;
  the oracle arm is 0/3 out-of-sample at candidate K2 while in-sample oracle
  arms were 12/12 exact. The L2 conditional — not the budget, not the floor
  mass, not the disclosed-set size — is the remaining single construction
  degree. Fixed-disclosure construction work is exactly the historic P20D
  slot (P20C §16: "constrained tuning, not open-ended").
- X09-R1 attribution (frozen input, not re-litigated): H1 budget NOT SUPPORTED
  (positive margins on every L2-failing block); H3 floor NOT SUPPORTED
  (failing blocks carry 25–43 floor hits vs in-sample max 3,262 — failures
  live overwhelmingly on SUPPORTED cells); H2 NOT DECIDABLE from persisted
  artifacts (order positions index per-block symbols but per-block
  Bob/truth sequences are not persisted; the npz is a 1024×1024 TRAIN cell
  table). The mandated successor instrumentation (§7) closes H2 (per-position
  hazard scalars + disclosed-prefix membership for the frozen order) and
  sharpens H3 (failure-neighborhood floor stats on the disclosed prefix +
  failing-coordinate neighborhoods), persisted as SCALARS only.
- Incumbent support fact (P20M freeze): 1,046,140/1,048,576 cells
  (0.99768) are zero-count floor cells. The raw-MLE L2 conditional is therefore
  a near-degenerate table: supported cells carry over-sharp few-count spikes
  (where X09 shows the failures live), floored cells carry uniform 1e-15 mass.
  The single most-constrained tempering of exactly this pathology — with zero
  free parameters after freezing — is unit-Laplace smoothing of the joint
  before `derive_p2` (§3). L1 is untouched because L1 is unblocked (P20M G1
  2/3 hard-L1-exact) and the factor must stay single.
- Alternatives rejected in writing: (a) any +ΔK1/+ΔK2 disclosure step —
  disclosure is FIXED by the P20D definition, forbidden; (b) L2-order
  re-derivation under the alt prior — second factor (order+construction),
  forbidden; L2 disclosed set stays the frozen P20M prefix on all arms;
  (c) λ-concentration retune — the X08-falsified operating point, forbidden;
  (d) Jeffreys α=0.5 / Good-Turing / Kneser-Ney / hierarchical backoff with a
  mixture weight β — extra machinery or a free weight with no accepted-source
  pin, forbidden; (e) floor-value raise (e.g. 1e-12) — H3 already exonerates
  floor mass, and the floor step is retained formally as a no-op safety,
  forbidden as the factor; (f) temperature scaling of hazards — untuned free
  parameter, forbidden; (g) K change or budget recompute from an alt H —
  violates fixed disclosure; alt-H values are descriptive only (§3);
  (h) SCL/list/belief decoder — decoder change, out of scope;
  (i) rerun P20M as-is on HOLD — answers nothing new, forbidden;
  (j) consume VAL remainder 2044..2212 (only 42-frame stub beyond one block)
  or 2M now — destroys the confirmation populations; both stay untouched.
- Session inventory (no new protected access by this planner; provenance from
  P20M §2/§4 + STATUS.yaml + split manifest `nbldpc_v25_split_manifest_v1`):
  1.5M TRAIN 1660 frames/424960 pairs (DEV-consumed 0..1535 + remainder
  1536..1659) + VAL 553/141568 (DEV-consumed 1660..2043, remainder 2044..2212)
  + HOLD 554/141824 (frames 2213..2766, never touched); pairs file size
  1869178 B / sha `ca351e52…a06b` provenance pin; 2M TRAIN 2187/559872
  reserved. Geometric position: P20N HOLD DEV is the FIRST 512 HOLD frames
  2213..2724; HOLD remainder 2725..2766 (42 frames / 10752 pairs) never used
  under this packet.
- Runner-delta design choice (frozen; the §10 "design.md" decision): a THIN NEW
  runner module importing the accepted `raw_prior_val_1p5m` runner read-only
  (which itself thin-imports accepted `l1_order_1p5m`: VAL/HOLD population
  pattern, TRAIN-exclusion gate family, order-file + `--order-digest`
  mechanism with zero Stage-B sampling, P20A endpoint/taxonomy/recount/
  resource machinery, `_selected_diagnostics` code point). Exact delta list,
  nothing else: (d1) alt-L2-table source → the §3 Stage-A artifact behind a new
  `alt_l2_identity` gate (file-bytes digest + alpha-1.0 pin + floor pin + exact
  key set + incumbent-p1 equality within 1e-12 + alt-H descriptive literals);
  (d2) K pins → the CARRIED P20M integers (K1 331, K2 6689; K_total 7020
  literal display, never recomputed from alt H); (d3) orders → the P20M frozen
  `raw_prior_orders_1p5m.json` reused read-only via the same order-file
  mechanism (L1+L2 orders byte-identical on all four arms; disclosed sets =
  first-331 / first-6689 prefixes); (d4) arms A/B/C/D per §6 (A = incumbent
  L2 operational control = P20M G1 construction; B = alt-L2 operational; C =
  incumbent L2 oracle = P20M G2 construction; D = alt-L2 oracle);
  (d5) new P20N tag domain (§6); (d6) mandatory hazard instrumentation fields
  (§7) computed post-decode in `_l2_hazard_diagnostics`, recorded-only;
  (d7) HOLD population + DEV∩build-frames disjointness declared inside the
  TRAIN-exclusion gate (§4). No SC/transform/floor-semantics/tag-semantics
  change; no second factor. The alternative (edit the accepted module) is
  rejected: it would touch an accepted evidence-producing file; the thin
  importer leaves every accepted file byte-identical.

## 3. Alternative-L2 freeze (normative — Stage-A closed-form derivation, zero new protected counts reads)

- Construction rule ALT-L2-LAPLACE-α1 (frozen, the single factor):
  `n_b[b] = counts_ab.sum(axis=0)`;
  `f_alt[a,b] = (counts_ab[a,b] + 1) / (n_b[b] + 1024)` (α=1 unit pseudocount,
  frozen literal; 1024 = Alice-alphabet size, frozen);
  `f_alt = max(f_alt, 1e-15)` then column-renormalize (floor step RETAINED
  formally for runner comparability; expected no-op — Stage A reports the hit
  count, expected 0); zero columns fall back to `p_global` exactly (expected 0
  zero columns; Stage A reports the count).
  `p2_alt = derive_p2(f_alt)` via the accepted `prior.derive_p2` under
  `A = 32*U1 + U2`, `FULL_BOB_ONLY` (cites:
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py:168-179`).
  `p1` for ALL arms = the incumbent P20M `p1` (L1 fixed; Stage A asserts
  `p1_alt_file == p1_incumbent` within 1e-12 elementwise).
  Scale reference (descriptive, not a gate): mean TRAIN column total ≈
  424960/1024 ≈ 415, so minimum alt cell mass ≈ 1/(n_b+1024) ~ 7e-4 vs the
  incumbent 1e-15 floor — tempered support without any HOLD/VAL/DEV input.
- Source of `counts_ab`: the FROZEN P20M artifact
  `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz`
  (canonical digest-pinned
  `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`;
  reading its `counts_ab` array in Stage A is a WORKTREE-FILE read — zero new
  protected counts reads; split-counted counts budget stays 0/0). No other
  input: never VAL/HOLD/DEV frames, never the V25 counts NPZ, never 1M/2M.
- Stage-A product (new artifact under this queue dir):
  `alt_l2_tables_1p5m.npz` with keys exactly `counts_ab, f_alt, p1, p2_alt,
  alpha, floor_value, h1_inc, h2_alt, h_total_alt` (`alpha` stored `1.0`;
  `floor_value` stored `1e-15`; `h1_inc` = incumbent H1 literal carried from
  P20M `0.02519949692375297`; `h2_alt`/`h_total_alt` recomputed descriptively
  via the accepted `target_construction.entropy_bits` functional on
  (p1_inc, p2_alt) — DESCRIPTIVE ONLY, never a budget input; K stays
  331/6689 by §5). Identity pin = file-bytes sha256
  `<FROZEN_AT_STAGE_A>` with freeze rule = derive once in Stage A, pin in
  `P20N_FREEZE.md`, gate on equality thereafter. Stage A additionally pins:
  alt floor-hit count/rate, zero-column count, `p1` equality max-abs-diff,
  min/max of `f_alt`, and the descriptive alt-H literals.
- Stage B loads the frozen file read-only behind the `alt_l2_identity` gate
  (file-bytes digest equality + alpha-1.0 pin + floor pin + exact key set +
  `p1`-equality recheck within 1e-12 against the P20M artifact + incumbent
  prior-digest pin `372dcc1c…f7d46ac`, or BLOCKED before any sampling and
  before any SC call).
- FORBIDDEN inputs for derivation or fitting: 1.5M DEV/HOLD/VAL-remainder
  frames, any consumed 1.5M TRAIN DEV, TRAIN remainder 1536..1659, P20M VAL DEV
  1660..2043, VAL remainder 2044..2212, ANY 1M split, reserved 2M, Model-F CAL
  artifact. No calibration fallback inside Stage B. The V25 counts NPZ is NEVER
  opened in this packet. Stage-A derivation is closed-form arithmetic: ZERO
  sampling, ZERO genie calls, ZERO derivation seeds.
- Feasibility literals D1 (Stage A computes, TRAIN-only, zero protected
  reads; construction-validity quantities, never decoding inputs and never
  thresholds on results):
  `ce_alt_insample_bits_per_symbol = (1/total) * sum_{a,b} counts_ab[a,b] *
  (-log2 p2_alt[u1(a), b, u2(a)])` with `u1(a) = (a>>5)&31`, `u2(a) = a&31`,
  `total = counts_ab.sum()` (424960 expected; Stage A reports the integer),
  evaluated on the SAME TRAIN counts the tables were built from (in-sample
  code length of TRAIN symbols under the alt L2 metric; exact estimator
  frozen here);
  `ce_incumbent_insample_bits_per_symbol` = the same estimator with the
  incumbent `p2` (comparison reference; expected ≈ H2 `0.8003665547495433`);
  `alt_feasibility_ceiling_bits = 5*6689+64 = 33509` (L2-only gate ceiling)
  and the operational ceiling `35164 = 5*7020+64` for reference;
  `alt_ideal_length_bits = ce_alt_insample_bits_per_symbol * 32768`.
- Gate D2 `alt_construction_budget_feasibility` (Stage A ONLY, evaluated
  BEFORE any Stage-B root creation and before any HOLD contact; outcome
  frozen in `P20N_FREEZE.md` and `STATUS.yaml`): IF `alt_ideal_length_bits >
  33509` THEN the construction is declared `ALT_CONSTRUCTION_BUDGET_INFEASIBLE`:
  the Stage-A return reports the D1 literals, the packet records the
  construction as falsified-by-arithmetic, the HOLD segment is NOT touched
  (HOLD read stays 0/1), no Stage-B authorization is requested, and the main
  thread re-frames the next factor from the returned literals. ELSE the D1
  literals freeze and the packet proceeds to Pre-EXECUTE/Stage B as designed.

## 4. Population and closed/consumed-data rule (normative)

- The following are CONSUMED/CLOSED and SHALL NOT supply P20N blocks: the
  three P18/P19 HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599),
  P20C/P20E/P20F DEV blocks (1M 0..383 / 384..767 / 768..1151, remainder
  1152..1199 never used), P20H DEV (1.5M TRAIN 0..383), P20I DEV (384..767),
  P20J DEV (768..1151), P20K DEV (1152..1535, remainder accounting 1536..1659),
  P20M VAL DEV (1.5M VAL 1660..2043). The ENTIRE 1M pool is fail-closed
  against P20N DEV selection (cross-file gate). 1.5M TRAIN remainder
  1536..1659 (124 frames < one 128-frame block) SHALL NOT supply P20N blocks.
- VAL remainder 2044..2212 (169 frames) is RESERVED never-decoded under this
  packet (counted, never decoded). The 2M session file SHALL NOT be opened,
  statted, listed, or read under this packet (reserved, not consumed; pristine
  by non-access; stat itself violates the packet).
- HOLD-first-use justification (same canonical TRAIN→held-out separation as
  P20M §4, frozen, not re-argued in Stage A/B): 1.5M HOLD 2213..2766 has never
  been decoded, tuned on, or scored by any EXECUTED NB-Polar packet; TRAIN is
  geometrically exhausted for N=32768 DEV; VAL DEV is consumed; 2M must be
  preserved. Using HOLD as a one-shot scoring population with TRAIN-derived
  hypotheses (incumbent prior + alt table both from TRAIN-fitted counts, never
  from HOLD frames) is declared once, consumed once, never tuned, never
  returned to a validation role. The HOLD remainder stays undecoded.
- Stage B runs on the DECLARED population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin; mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| construction-derivation input | §3 worktree `counts_ab` ONLY (TRAIN-fitted; never a HOLD frame) |
| HOLD DEV frame rule | FIRST 512 HOLD frames in (frame_id, pair_idx) order → frozen HOLD base 2213: `2213..2724` (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed) |
| HOLD DEV blocks (N=32768) | `2213..2340`, `2341..2468`, `2469..2596`, `2597..2724` (4 × 128 frames) |
| unused remainder | HOLD frames `2725..2766` (42 frames / 10752 pairs) recorded never used — counted, never decoded |
| build-frames disjointness (S2-ii) | counts/build frames ⊂ TRAIN `0..1659` (P20H §3 input = 1.5M TRAIN counts ONLY); DEV ⊂ HOLD `2213..2724`; disjoint by split identity; declared frame sets above; the TRAIN-exclusion gate refuses any overlap before any protected content open |
| consumed-TRAIN exclusions | 1.5M TRAIN `0..383` (P20H), `384..767` (P20I), `768..1151` (P20J), `1152..1659` (P20K + remainder) — overlap refuses before any protected content open |
| consumed-VAL exclusions | 1.5M VAL DEV `1660..2043` (P20M) + VAL remainder `2044..2212` — overlap refuses before any protected content open |
| 1M full pool + reserved 2M | excluded by the cross-file gate (checked FIRST); never touched |
| block count | 4 at N=32768 |
| tag domains | new P20N domain (§6) |

- Fail-closed gate family (frozen in the runner, order (a)→(g), HOLD/VAL
  before consumed-TRAIN): (a) CROSS-FILE — DEV content-open path +
  stat-size/sha pin must equal the 1.5M identity; any 1M or 2M path or digest
  mismatch refuses before any SC call (frame integers alone are never
  identity); (b) INTRA-FILE HOLD — DEV ranges must overlap NONE of
  VAL-exterior/VAL-remainder, and must lie wholly inside HOLD 2213..2766, else
  refuse before any protected content open; (c) CONSUMED-TRAIN EXCLUSION —
  NONE of TRAIN 0..1659; (d) CONSUMED-VAL-DEV EXCLUSION — NONE of 1660..2043;
  (e) VAL-REMAINDER EXCLUSION — NONE of 2044..2212 (counted never decoded);
  (f) DEV∩build-frames disjointness declaration: DEV ⊂ HOLD vs build ⊂ TRAIN
  with the frame sets above (S2-ii); (g) ALT-IDENTITY + ORDER-FREEZE +
  K-LITERAL — §3 file-bytes digest pin must match AND the P20M order-file
  digest `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`
  must match with K1/K2 literals 331/6689 replaying exactly, else refuse
  before any SC call.

## 5. Preregistered disclosure point (normative — CARRIED P20M point, zero recompute)

- K rule (fixed disclosure; the P20D constraint): `(K1,K2) = (331,6689)`,
  `K_total = 7020`, CARRIED byte-identical from the P20M freeze
  (`STATUS.yaml` frozen_k1_g1/k2_g1/k_total_g1 + budget literal
  `1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536] = 7020`).
  NO recomputation from alt H (the §3 alt-H literals are descriptive only);
  NO `select_empirical_split` rerun; NO synthetic sampling at any stage.
  The K-literal gate displays `K1=331/K2=6689/K_total=7020` and refuses any
  other triple before any SC call.
- Caps PREREGISTERED per arm (rule `5*(K1+K2)+64` key-dependent bits/block,
  `10*32768+63 = 327743` public bits/tag, one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_incumbent_L2_operational (control) | 331 | 6689 | 35164 = 5*7020+64 | 327743 |
| B_alt_L2_operational (candidate) | 331 | 6689 | 35164 = 5*7020+64 (Δ vs A exactly 0) | 327743 |
| C_incumbent_L2_oracle (diagnostic) | 0 | 6689 | 33509 = 5*6689+64 | 327743 |
| D_alt_L2_oracle (diagnostic) | 0 | 6689 | 33509 = 5*6689+64 (Δ vs C exactly 0) | 327743 |

- Planned totals: key-dependent `549384` = 8*35164 + 8*33509 bits;
  public `5243888` = 16*327743 bits. B-vs-A and D-vs-C key-bit deltas are
  exactly 0 (construction factor carries ZERO disclosure delta by design).
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate
  BLOCKS. Per-record fields pin the construction point (`l2_construction`
  incumbent/alt, `k1/k2/k_total`, `alt_digest`, `l1_order_digest`,
  `l2_order_digest`, `floor_hit_rate`).

## 6. Arms (frozen; construction swapped per §3, all else P20M-identical)

- `A_incumbent_L2_operational`: frozen greedy SC with the P20M incumbent
  tables (raw prior `372dcc1c…f7d46ac`, P20M L1+L2 orders, K1=331/K2=6689)
  (operational control; 2 SC + 1 P20N-domain tag per block). Paired same-block
  control for B on the new HOLD segment. Construction-identical to P20M G1.
- `B_alt_L2_operational`: frozen greedy SC with incumbent `p1` + §3 `p2_alt`,
  SAME P20M L1+L2 orders (first-331 / first-6689 prefixes), SAME K1/K2
  (operational; the single-factor candidate; 2 SC + 1 tag per block).
- `C_incumbent_L2_oracle`: true-L1-conditioned diagnostic with incumbent `p2`
  at K2=6689 (provenance ORACLE, deployable=false, excluded from every
  operational aggregate; never a correction result; 1 SC + 1 P20N-domain tag
  per block). Construction-identical to P20M G2.
- `D_alt_L2_oracle`: true-L1-conditioned diagnostic with `p2_alt` at K2=6689
  (provenance ORACLE, deployable=false, excluded from every operational
  aggregate; never a correction result; 1 SC + 1 P20N-domain tag per block).
- No other arms. Block-major (A, B, C, D) per HOLD block; checkpoint after
  every (arm, block) record; 16 records total. P16 construction file unchanged
  (digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  carried read-only); kernel/representation/transform/SC arithmetic unchanged;
  greedy SC only; no SCL/new kernel/model/schema. Stage A performs ZERO genie
  calls, ZERO sampling (closed-form derivation only); Stage B performs pure
  HOLD scoring (24 SC + 16 tags) with ZERO sampling — the Stage-B TRAIN genie
  call count is pinned at 0.
- Tag domain (new P20N): master 2026092300, prefix
  `nbpolar-p20n-l2-alt-hold-1p5m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from
  ALL of P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K/P20L/P20M.
  Stage A verifies by repo grep that master 2026092300 and focused-test seeds
  `2026092301..2026092307` appear in no tracked file outside the P20N
  runner/tests/packet/spec documents (planner pre-checked 202609230* absent
  in runner .py + queue .md + tests at freeze time; NO derivation seeds exist
  — closed-form derivation takes none).
- L2 disclosed-set rule (single-factor guard): on ALL four arms the disclosed
  L2 set is the first-6689 positions of the SAME frozen P20M L2 order file
  (digest-gated); the L1 set is the first-331 of the SAME frozen P20M L1 order
  file. Positions are fixed by the frozen files, never selected on closed
  blocks, consumed ranges, or HOLD data.

## 7. Thresholds, endpoints, and mandatory instrumentation (descriptive only — P20M-style)

- Outcome label `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE`
  iff ALL integrity gates (§9) hold — regardless of exact-count. Any exact
  count (including 0/16 and partials) is COMPLETE when integrity holds.
- Choice + justification: P20M-style descriptive (no recovery/FER/Wilson
  threshold). This is the FIRST out-of-sample test of an alternative L2
  construction at fixed disclosure — there is no empirical basis for a
  restoration threshold here. A 62/64-class gate would be an invented
  threshold, explicitly forbidden. Branch decisions belong to main-thread
  planning AFTER acceptance (§16).
- NO recovery / FER / Wilson / superiority / qualification / promotion claim.
  Descriptive reading only: "alt-L2-restoration" = blocks where A fails and B
  is exact (`b_restored_count`, count + per-block endpoint rows), and the
  oracle pair C→D (`d_restored_count`); "maintain" = B exact where A exact.
  Any (or neither) counts as COMPLETE.
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`,
  `undetected` isolated (never success/FER), plus `decode_failed` /
  `nonfinite` / `resource_abort` via the P20A path. P20A four-endpoint
  separation (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` / `pair_exact`)
  per record. First-error coordinate/layer rows (natural block symbol index,
  settled X09-R1 D4) are the primary diagnostic signal. Per-record incumbent
  floor-hit fields (`floor_hits`, `floor_hit_rate`) complete per record (S2
  reporting, carried from P20M).
- Mandatory X09-R1 instrumentation (BOTH requirements, per-record SCALARS,
  scalar-only five-file rule intact — no vectors persisted):
  - Req1 (closes H2 — hazard + coverage at the frozen order): new fields
    `l2_order_digest`, `l2_prefix_len`, `l2_fail_in_prefix`,
    `l2_fail_hazard_bits`, `l2_fail_nbhd_mean_bits`, `l2_prefix_hazard_mean_bits`.
  - Req2 (sharpens H3 — failure-neighborhood floor stats on prefix +
    failing neighborhoods): new fields `l2_fail_nbhd_floor_frac`,
    `l2_prefix_floor_frac`.
  - Semantics (frozen; Stage A pins exact formulas with injected vectors):
    `l2_prefix_len` = 6689 on every record (gated); `l2_order_digest` = the
    frozen P20M order-file digest on every record; `l2_fail_in_prefix` = null
    unless `first_error_layer == L2`, else whether the failing position index
    lies in the disclosed L2 prefix set (first-6689 of the frozen L2 order;
    index spaces are the runner's native length-N block arrays per X09-R1 D4);
    `l2_fail_hazard_bits` = null unless L2 failure, else `-log2` arm-table
    mass at the failing position's true `(U1_cond, B, U2)` cell under the
    record's own arm table (`U1_cond` = hard-L1 candidate on A/B, true high
    on C/D); `l2_fail_nbhd_mean_bits` = null unless L2 failure, else the mean
    of that hazard quantity over the frozen radius-R=8 window around the
    failing position (clipped to the block); `l2_fail_nbhd_floor_frac` = null
    unless L2 failure, else the fraction of window cells whose raw
    (unfloored column-normalized TRAIN conditional from `counts_ab`) mass is
    below 1e-15; `l2_prefix_hazard_mean_bits` / `l2_prefix_floor_frac` = the
    same two quantities averaged over the disclosed-prefix positions using
    true cells (every record, never null on a completed record).
  - Writer code point (frozen): successor module `l2_alt_hold_1p5m.py`,
    function `_l2_hazard_diagnostics(*, block, view, p2_arm, counts_arr,
    l2_order, k2, first_error)` — called post-decode (after tag scoring)
    from the successor's `_operational_record` / `_control_record`
    equivalents (the P20M `_selected_diagnostics` code point,
    `raw_prior_val_1p5m.py:1306-1334`, is the carried-over callsite pattern).
  - Truth-isolation boundary (normative): block truth (high/low/bob) and the
    arm tables enter `_l2_hazard_diagnostics` for RECORDING ONLY after all SC
    calls for the record have completed; its outputs are written into the
    record dict and never passed to `run_operational_block`,
    `run_oracle_control_block`, `_decode_layer`, `build_p1_metrics`,
    `gather_p2_metrics`, or any disclosure/order decision. A focused
    truth-isolation sentinel test pins this boundary (mutating truth changes
    no metric/decision input).

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized
  execution; no rerun, no seed change, no construction/budget/order tuning
  after preregistration. Execution-error rerun only as a recorded repeat of
  the identical freeze, never as tuning. P20H–P20M spent attempts do NOT
  transfer (independent packet).
- Reads (split-counted): counts-calibration opens 0/0 (no protected NPZ open
  in this packet; §3 derivation reads the worktree P20M npz only) + HOLD open
  1/1 reserved for Stage B (parquet, consumed at first HOLD content open).
  VAL-remainder reads 0; 2M reads 0. Any reopen, new calibration, real-frame
  use for derivation, or HOLD refit is forbidden. Prior-file/alt-file loads
  and closed-form derivation are worktree-file reads, not protected opens.
- SC/tag/genie budget: Stage-A derivation 0 genie calls + 0 sampling (closed
  form, accounted in the Stage-A freeze) + Stage-B pure HOLD 24 SC
  (4 blocks × (2+2+1+1)) + 16 tags + 16 records with ZERO Stage-B sampling
  (Stage-B TRAIN genie calls pinned at 0); derived per-record recomputation
  must equal counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  accounting; abort is BLOCKED, never success. Wall/RSS ceilings frozen in
  Stage-A freeze (P20-class reference at larger DEV decoder budget: P20M
  ~104.85 s / ~531 MB for 15-SC / 9-tag; P20N plans 24-SC / 16-tag HOLD
  budget; external timeout 900 s + virtual/RSS caps 2 GiB + single thread
  frozen).
- Strategy stop rules binding: no tuning on closed blocks or the new HOLD DEV
  after the one shot; no reuse of consumed 1M pool (any split/subrange), any
  consumed 1.5M TRAIN DEV, TRAIN remainder 1536..1659, P20M VAL DEV 1660..2043,
  VAL remainder 2044..2212 beyond counting, HOLD remainder 2725..2766 beyond
  counting, or reserved 2M; no third factor after inconclusive single-factor;
  no near-raw disclosure claim; no oracle-as-operational; no
  population-reliability inference from this single gate alone; no efficiency
  tuning inside this packet.
- SCL entry gate UNCHANGED (unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B five files)

- Stage-A freeze pins (no protected opens): alt-table artifact path +
  file-bytes digest + alpha/floor pins + exact key set + `p1`-equality
  max-abs-diff + floor-hit count/rate + zero-column count + `f_alt` min/max +
  descriptive alt-H literals + D1 feasibility literals + D2 gate outcome; K1/K2/K_total literals + order-file digest pin;
  exact module path + N-flag Stage-B command verbatim + population integers +
  caps + budgets + tag domain + P16 construction digest; recorded in
  `P20N_FREEZE.md`. Stage-A alt-table product identity: path
  `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz`,
  file-bytes sha256 pinned in the freeze.
- Stage-B root:
  `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/`
  (exactly five files; per-(arm, block) checkpointing; pure HOLD scoring —
  zero sampling; one HOLD content open; no reopen/rerun).
  Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`
  (P16 construction digest + incumbent-prior digest + alt-table digest-gate
  proof (file bytes sha256 equals the frozen `--alt-digest`) + order-file
  digest-gate proof + K-literal display + split manifest + HOLD DEV integers
  + DEV∩build-frames disjointness declaration with frame sets),
  `per_block_arm_outcomes.jsonl` (16 records at completion),
  `aggregate_summary.json`, `report.md`. Per-record §7 endpoints + first error
  coordinate/layer, zero-count hits, floor hits + floor-hit rate + log loss,
  true-H vs candidate-H L2 NLL, taxonomy, construction-point fields
  (`l2_construction`, `k1/k2/k_total`, `alt_digest`, `l1_order_digest`,
  `l2_order_digest`) + the EIGHT instrumentation scalars of §7 (Req1+Req2).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0);
  genie call counts (Stage-A 0 + Stage-B 0) + SC counts (L1/L2 split) + tag
  counts exact; block SER/NLL; wall/RSS; `b_restored_count` /
  `d_restored_count` descriptive; per-arm floor-hit rate + per-arm prefix
  hazard means reported.
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `incumbent_prior_identity` (P20M npz
  digest + lambda-0.0/floor pins + exact key set + H literals within 1e-12 +
  `p_b` cross-check);   `alt_l2_identity` (file-bytes digest + alpha-1.0/floor
  pins + exact key set + `p1`-equality within 1e-12 + descriptive alt-H
  literals); `alt_construction_budget_feasibility` (Stage-A-only D2 gate:
  FEASIBLE outcome required before Pre-EXECUTE; INFEASIBLE ends the packet
  at Stage A with HOLD untouched); `dev_split_manifest_identity`;
  `dev_block_range_identity` (§4 gate family (a)→(g): cross-file first, then
  intra-file HOLD-containment, then consumed-TRAIN, consumed-VAL-DEV,
  VAL-remainder exclusions incl. the DEV∩build-frames disjointness
  declaration, then alt-identity + order-freeze + K-literal pins);
  `order_derivation_identity` (P20M program pin + order-file digest,
  Stage-B file-bytes digest equality replay-exact, zero Stage-B sampling);
  `k_literal_exact` (K1=331/K2=6689/K_total=7020 replayed, never recomputed);
  `target_population_contract`; `dev_population_exact` (512 HOLD frames /
  131072 pairs / 256 rows per frame / pair indices / symbol range);
  `blocks_exact_with_declared_remainder` (four exact HOLD DEV ranges per arm
  in block-major slot order + never-used HOLD remainder 42 frames /
  10752 pairs, counted from the pool but never decoded);
  `sixteen_records_exact`; `genie_calls_exact` (Stage-A 0 + Stage-B 0);
  `sc_calls_exact` (derived 24); `tags_exact` (derived 16);
  `orders_valid_k_prefixes_within_registered_arms` (shared P20M prefixes +
  construction quadruple); `hazard_instrumentation_complete` (all eight §7
  scalars present with correct nullability on every completed record);
  `floor_hit_rate_reported`; `oracle_isolation`;
  `buckets_disjoint_exhaustive` (unique arm/block + schema); `undetected_zero`;
  `nonfinite_zero`; `truth_isolation`; `disclosure_recount_exact`;
  `one_open_per_protected_input` (counts 0 + HOLD 1); `input_stat_unchanged`;
  `no_unregistered_access`; `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (derivation + injected tests + implementation-freeze; authorized
  separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_l2_alt_hold_1p5m.py -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20n/<uuid>/`
  temp root; protected-open audit declared separately (counts 0 + HOLD 0 at
  Stage-A close). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A derivation (read-only worktree input, zero protected opens): read
  `counts_ab` from the §3 P20M worktree npz (digest-reverified first) → apply
  the §3 α=1 rule (floor step retained, `derive_p2`, `p1`-equality check) →
  write `alt_l2_tables_1p5m.npz` + freeze file-bytes digest/alpha/floor/key-set/
  `p1`-equality/floor-rate/zero-columns/`f_alt`-range/descriptive alt-H. Zero
  HOLD contact, zero counts opens, zero sampling, zero genie calls throughout.
  Template (pins filled in the freeze; all flags required, no production
  default):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_1p5m --derive --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alpha 1 --floor 1e-15 --out .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz
```
  Stage A confirms the module path (thin importer of accepted
  `raw_prior_val_1p5m` per the §2 delta list d1–d7, or freezes a written
  equivalent with justification) and the `--alpha` vocabulary (only `1`).
  Forbidden by default: `longrun_*`, `minrerun_*`, `routeA_*`,
  `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A
  freeze with the `<FROZEN_AT_STAGE_A>` pin filled; NOT AUTHORIZED until
  independent Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 900 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz --alt-digest <FROZEN_AT_STAGE_A> --source 1p5M --floor 1e-15 --n 32768 --k1 331 --k2 6689 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 2213 2724 --block-frames 128 --remainder-frames 2725 2766 --tag-master 2026092300 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m
```
  All flags required, no production default; four hardcoded arms with the
  construction swap pinned (never CLI-tunable: A = incumbent-L2/331/6689;
  B = alt-L2/331/6689; C = incumbent oracle; D = alt oracle); Stage-B prior
  path MUST equal the §3 frozen digest; `--alpha` takes no Stage-B value
  (construction is frozen in the alt file). Stage A fills the
  `<FROZEN_AT_STAGE_A>` pin (`--alt-digest`) plus the `--source` vocabulary
  (only `1p5M`). Forbidden by default as above.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git
  show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: alt-table artifact `alt_l2_tables_1p5m.npz` (+ digest/alpha/floor/
  key-set/`p1`-equality/floor-rate/alt-H freeze) + thin runner + focused
  injected tests + Stage-A freeze + implementation notes (exact files, diffs,
  test commands/results, frozen construction/population/cap/command,
  D1 feasibility literals + D2 gate outcome).
  Protected content opens 0 at Stage-A close (counts 0 + HOLD 0; worktree-npz
  reads are not protected opens; closed-form derivation uses only the worktree
  prior arrays).
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md`
  (+ freeze, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`,
  `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec P20N delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20n/spec.md`
  + `tasks.md` P20N section (same umbrella change as
  P18/P19/P20A/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K/P20M; no new
  top-level change).

## 12. Allowed work

- New thin alt-L2 runner (importer per §2 d1–d7) + focused injected tests
  (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`,
  `raw_prior_val_1p5m.py` (gate/population/record-writer pattern references;
  `raw_prior_val_1p5m` additionally the import target), P13/P16 machinery
  (`target_n_scaling.budget_k_total` as carried-literal reference only)
  (+ `construction.py` / `prior.py` / `sc.py` contracts as called).
- Read-only load of `counts_ab` from the §3 P20M worktree npz (digest-pinned;
  worktree-file read, never a protected counts open) + closed-form §3
  derivation IN STAGE A ONLY to produce the frozen alt-table artifact
  (§§3/9; zero protected reads, zero HOLD contact).
- P20N OpenSpec delta + packet docs + Stage-A freeze/return/review files +
  Stage-B evidence root (root only after Stage-B authorization) + the frozen
  `alt_l2_tables_1p5m.npz` (Stage-A product, §3/§9 identity).

## 13. Forbidden work

- Any NPZ/parquet content open or stat of 1.5M HOLD/DEV/VAL-remainder, any 1M
  split, or reserved 2M in Stage A (Stage-A protected opens 0); any V25
  counts-NPZ open; any K carried as anything but the §5 literals; any
  derivation on real HOLD/DEV/VAL frames at any stage; any decoder execution
  before Pre-EXECUTE PASS + pasted Stage-B authorization.
- Any change to GF32/transform/SC arithmetic, floor value, L1 tables, L1/L2
  orders, disclosed sets, tag scheme semantics, outcome precedence, accepted
  evidence roots, P20M products, X08/X09 probe roots, or `src/` +
  `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the
  consumed 1M pool (any split/subrange), any consumed 1.5M TRAIN DEV
  (0..1659), P20M VAL DEV 1660..2043, VAL remainder 2044..2212, HOLD remainder
  2725..2766, or the reserved 2M file; no second construction, no construction
  sweep, no order re-derivation, no disclosure change, no efficiency tuning;
  no new-block peeking before the authorized attempt; no calibration on HOLD.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push; no self-acceptance; no P20D scope creep beyond the single
  frozen construction; no P20H–P20M rerun under this packet.

## 14. Acceptance IDs

- `P20N-R1`: alt-L2 table derived read-only from §3 P20M worktree `counts_ab`
  under the frozen α=1 rule (floor step retained + renorm + `derive_p2` pin +
  `p1`-equality within 1e-12 + descriptive alt-H; zero protected counts opens;
  V25 NPZ never opened; zero sampling; zero genie calls); file-bytes digest +
  alpha/floor/key-set/`p1`-equality/floor-rate literals frozen at Stage A.
  Derivation-gate BLOCKED → planner rework, never a Stage-B fallback.
- `P20N-R2`: K/orders/population frozen carried (K1=331/K2=6689/K_total=7020
  literals replayed, never recomputed; shared P20M order-file digest +
  Stage-B digest-gate equality, zero Stage-B sampling); closed/consumed blocks
  select nothing; consumed 1M pool excluded by source-tagged cross-file gate;
  all consumed 1.5M TRAIN DEV + P20M VAL DEV + VAL remainder excluded; HOLD
  DEV 2213..2724 (4 blocks 2213..2340/2341..2468/2469..2596/2597..2724, HOLD
  remainder 2725..2766 never used) gated + Pre-EXECUTE-approved; reserved 2M
  untouched (never opened/statted/listed).
- `P20N-R3`: disclosure point preregistered per arm from the carried integers
  (A/B 35164 + 327743 public with Δ exactly 0; C/D 33509 + 327743 public with
  Δ exactly 0), planned totals 549384 + 5243888 shown, recount mismatch 0; CE
  ratios never called efficiency.
- `P20N-R4`: single-factor construction swap (A incumbent-control pins +
  B alt-candidate pins + shared-prefix rule + C/D oracle pair) frozen before
  execution, unchanged after; P16 construction migration pinned; no
  tag-guided selection, no evidence reuse, no post-hoc re-picking, no
  re-derivation.
- `P20N-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9;
  `undetected` isolated; oracle arms never operational; first-error
  coordinate/layer rows + per-record floor-hit fields + all eight §7
  hazard/coverage scalars complete per record with correct nullability;
  instrumentation recorded-only (truth-isolation sentinel green).
- `P20N-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning;
  split-counted reads (counts 0/0 + HOLD 1/1 + VAL-remainder 0 + 2M 0);
  resource aborts via P20A path with accounting preserved; stop rules + SCL
  gate intact.
- `P20N-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded
  (Pre-EXECUTE explicitly adjudicates §3 derivation + D2 feasibility outcome +
  §5 K-literal + §4 gate family + §2 runner-delta design + §7 instrumentation
  boundary);
  main-thread acceptance owns the label; descriptive-only, no
  FER/qualification/promotion language; branch reading (§16) stays planning
  input, never an in-packet verdict; honest-scope statement (§0) repeated
  verbatim in the return.
- `P20N-R8`: Stage-A suites green on injected data with zero protected opens
  audit (counts 0 + HOLD 0 at Stage-A close; 2M non-access); no commit/push;
  frozen dirs byte-untouched except the §12 manifest.

- `P20N-R9`: feasibility literals + gate (D1 estimator frozen with TRAIN-only
  inputs, zero protected reads; D2 outcome frozen in `P20N_FREEZE.md`/STATUS
  BEFORE any HOLD contact; INFEASIBLE → HOLD untouched, no Stage-B request,
  construction recorded falsified-by-arithmetic; FEASIBLE → literals frozen,
  packet proceeds). Gate-fired-by-arithmetic → main-thread re-frame, never a
  Stage-B fallback.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs
`P20N-R1..R9` (stage-appropriately) complete with changed files + exact
commands/results + artifact inventory (incl. the Stage-A alt-table digest) +
split open audit (counts + HOLD + VAL-remainder + 2M separately); or (b) a
concrete blocker with failing command, exact error/traceback, attempted
remedies, and the ONE decision needed from the main thread. "Still incomplete"
is not a completion report. The operator never marks its own work accepted and
never authorizes Stage B.

## 16. Deferred options (not in this packet)

- B-restoration → maintain-confirmation round (deferred): trigger = at least
  one block with A fail → B exact on the new HOLD segment (genuine
  alt-L2-restoration event, not maintain-only). Then a LATER packet may
  preregister a maintain confirmation on further new data (HOLD remainder
  2725..2766 is only 42 frames = sub-block, so NOT a confirmation population;
  reserved 2M first-use with per-session raw calibration + frozen alt
  construction + new tags is the candidate confirmation population but NOT
  pre-authorized here). This packet performs no follow-up confirmation and
  licenses no reliability claim.
- B-zero-restoration with L2-layer persistence → next upstream single factor
  (deferred): trigger = genuine alt-construction negative under fixed
  disclosure — B restores NONE with operational first errors remaining
  L2-layer (and D restores NONE under true L1). Only THEN is the Laplace-α1
  L2 form falsified as the fix, and only then does exactly ONE of (L2-order
  positions under the raw prior / L2-side bounded search at the fixed point /
  second single construction form) become the next single factor on further
  new data by main-thread planning. Nothing is auto-triggered inside this
  packet.
- B-zero-restoration with L1-layer return → prior/L1-side re-evaluation
  (deferred): trigger = operational first errors returning to L1-layer under
  the alt L2 (L1-side regression signal, not an L2 win). Main thread
  re-evaluates with the full chain evidence in hand. This packet prejudges
  none of them.
- Maintain-only (A exact somewhere and B exact wherever A exact, zero
  fail→exact events) → further planning (deferred): neither restoration nor
  negative; main thread re-evaluates with the full chain evidence in hand.
- Disclosure-minimality probe, efficiency optimization, second independent
  session on reserved 2M, closure of the 1M-HOLD thread: ALL continue deferred
  / out of scope, re-evaluated against P20N accepted evidence after acceptance.
- 2M stays PRISTINE under this packet — never opened, never statted, never
  listed — as the follow-up confirmation population. Any 2M packet needs its
  own freeze, tag domain, and reviews.

(End of file)
