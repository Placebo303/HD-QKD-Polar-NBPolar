# Phase 4-P20O — Maintain-confirmation of ALT-L2-LAPLACE-α1 at per-session disclosure on type2_2M_20260121_183657 VAL (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage-A per-session freeze, Stage-B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read, decoder execution, or commit/push is authorized by this file.
- Predecessor: `NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M` terminal
  `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; HOLD open 1/1
  SPENT on 1.5M HOLD 2213..2724; 16/16 records; A 0/4 / B 1/4 (b3 2597..2724 exact)
  / C 0/4 / D 1/4; b_restored 1 descriptive, d_restored 1 diagnostic; all 14 failures
  L2-layer; undetected 0; SC 24/24; tags 16/16; recount 0; key 549384 / public 5243888;
  integrity 28/28; Pre-RESULT PASS; acceptance in `MAIN_THREAD_ACCEPTANCE.md`).
- P20M accepted descriptive (VAL 1660..2043, raw prior no-λ unblocked L1, every
  operational arm 0/3, L2 bottleneck, oracle 0/3 out-of-sample) is the operating-point
  precedent; P20N is the construction precedent (`f_alt=(counts+1)/(n_b+1024)`, α=1 frozen).
- User decision (2026-09-19): the maintain-confirmation round
  (`b_restoration_branch_maintain_confirmation_round`) uses the **reserved 2M session
  `type2_2M_20260121_183657` (first use)**. 1.5M HOLD is consumed (1/1 SPENT); 1.5M VAL
  remainder 2044..2212 and all 1M data stay untouched; 2M has never been opened/statted/listed
  (planner performed zero 2M opens/stats/listings; manifest metadata read only, see §4).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2
  and `docs/nbpolar/ROADMAP.md`.
- Gate discipline: any standing long-horizon authorization does NOT collapse
  Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_2M_20260121_183657` (2M), scoring population
  first-use of 2M VAL (see §4). The 1M pool and the entire 1.5M session are
  fail-closed against P20O DEV selection (see §4).

## 0. Planner header (OpenSpec workflow)

- **Goal**: Maintain-confirm ONE frozen construction — `ALT-L2-LAPLACE-α1` — at fixed
  per-session disclosure on FIRST-USE 2M VAL blocks at N=32768 (four arms A/B/C/D,
  new P20O tag domain, eight X09-R1 scalars + one optional U-domain cross-check scalar),
  with the raw prior + budget + split + orders ALL derived from the 2M session's own
  TRAIN (never carried across sessions — S2-i). Decide descriptively whether B maintains
  exact blocks where A is exact and whether any A-fail→B-exact restoration re-appears on
  the independent session — operationally (B vs A) and under true-L1 conditioning (D vs C).
- **Non-Goals**: No construction sweep/tuning (α=1 frozen, single factor); no K/order
  hand-fill or cross-session carry (all 2M-derived in Stage A, frozen thereafter); no λ
  anywhere; no floor-value change; no SCL/new kernel/model/schema; no FER/reliability/
  qualification/promotion claim; no reuse of any consumed/closed range (1M pool, all 1.5M
  TRAIN/VAL/HOLD incl. VAL remainder 2044..2212 and HOLD DEV 2213..2724); no 2M TRAIN-as-DEV
  or 2M HOLD use; no closure of the 1M-HOLD thread; no efficiency tuning.
- **Impact Scope**: New thin runner + focused injected tests + P20O OpenSpec
  delta (`specs/nbpolar-phase4-p20o/spec.md` + `tasks.md` P20O section, same
  umbrella change `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A freeze
  (raw-prior artifact + order file + alt-L2-table artifact) + implementation notes +
  Stage-B evidence root. No change to `src/`, `experiments/`, `tools/`, P16 construction
  file, P12–P20N accepted roots (`raw_prior_1p5m.npz`, `raw_prior_orders_1p5m.json`,
  `alt_l2_tables_1p5m.npz`, `raw_prior_val_1p5m/`, `l2_alt_hold_1p5m/`), X08/X09 probe roots,
  or `results/` / `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20O-R1..R9 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance.
  Descriptive-only label; `undetected` isolated; oracles never operational.
- **Tasks**: (planner task list for coder agents) H1 derive + freeze 2M raw prior
  (§3, R1); H2 freeze 2M budget/split/orders + alt table + D1/D2 (§3/§5, R1/R9);
  H3 freeze population/gates (§4, R2); H4 freeze caps from the derived point (§5, R3);
  H5 freeze single-factor arm swap, A/C incumbent pins (§2/§6, R4); H6 wire
  endpoints/taxonomy + mandatory hazard instrumentation incl. optional U-domain scalar
  (§7, R5); H7 enforce one-shot budget/stop (§8, R6); H8 Stage-A suites green
  with declared-open audit (R8); H9 independent Pre-EXECUTE adjudication of prior/alt/
  K-literal/population gates (R7); H10 single authorized Stage-B attempt (R6/R7);
  H11 independent Pre-RESULT + acceptance.
- **Honest scope** (binding on proposal/design/packet/return language): first use of
  the reserved 2M independent session to attempt to maintain one prior 1.5M restoration
  event with the frozen construction; positive/negative both informative; no reliability
  claim; 1.5M VAL remainder and the 1M-HOLD thread stay out of scope; 2M is consumed by
  this packet regardless of outcome.

## 1. Mission

With per-session calibration on the NEW session (2M TRAIN-derived raw prior + its
session-derived disclosure point + its session-derived worst-first orders) and ONE
carried construction factor (the frozen `ALT-L2-LAPLACE-α1` rule applied to the SAME
2M TRAIN counts, L1 path byte-identical to the 2M incumbent, disclosed sets
byte-identical, K1/K2 byte-identical within the packet) — and everything else fixed
(floor 1e-15, N=32768, greedy SC only, new P20O tag domains only), zero further tuning:

> On FIRST-USE 2M VAL blocks, does the alt-L2 operational arm (B) maintain exact
> wherever the incumbent-L2 operational arm (A) is exact at the session's own fixed
> disclosure — and does any A-fail→B-exact restoration re-appear — with the hazard/
> coverage state recorded under each construction, including the U-domain cross-check?

P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, P20K DEV 1152..1535 are
CONSUMED; 1.5M TRAIN remainder 1536..1659 insufficient; P20M VAL DEV 1660..2043
CONSUMED; VAL remainder 2044..2212 RESERVED never-decoded under this packet; P20N HOLD
DEV 2213..2724 CONSUMED (1/1 SPENT), HOLD remainder 2725..2766 never used; P20L never
executed (zero consumption). The ENTIRE 1M pool is fail-closed. All branches after this
packet are deferred to §16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- Operating-point route closed on 1.5M (P20M): corrected raw-count prior + session budget
  moved the bottleneck L1→L2 (2/3 hard-L1-exact) but restored 0 blocks; oracle 0/3
  out-of-sample at candidate K2 while in-sample oracles were 12/12 exact. Construction
  route opened on 1.5M HOLD (P20N): the single Laplace-α1 L2 tempering restored block 3
  exactly under BOTH B (operational) and D (oracle) vs A/C 0/4, with all 14 failures
  L2-layer, neighbourhood floor fraction 0.0 on every failing record, and higher average
  prefix hazard under alt (0.89–0.90 vs 0.80–0.86) — descriptive support for "incumbent
  spikiness, not average length, drives out-of-sample L2 failures". Scale: one event, one
  segment — no reliability claim. The deferred `b_restoration_branch_maintain_confirmation_round`
  is the live next branch; the user selected the reserved 2M first-use as its population.
- Per-session semantics (S2-i, frozen, not re-argued): raw prior + budget + split + orders
  are derived from the SCORING session's own TRAIN, never carried across sessions. Carrying
  the 1.5M (K1,K2)=(331,6689), orders, or prior to 2M would violate S2-i and is forbidden.
  The alt-L2 RULE is the confirmed single factor (α=1, frozen); its 2M instantiation is
  derived from the SAME 2M TRAIN counts by the SAME closed-form rule (new digest, §3).
  Fixed disclosure means fixed WITHIN the packet after the Stage-A freeze (B−A = 0, D−C = 0
  by design), not a carried absolute.
- Alternatives rejected in writing: (a) carry 1.5M K/orders/prior to 2M — violates S2-i,
  forbidden; (b) any α other than 1, any second construction, any construction sweep —
  second factor, forbidden; (c) L2-order re-derivation under the alt prior — second factor
  (order+construction), forbidden; disclosed sets stay the frozen 2M-derived prefixes on all
  arms; (d) λ-concentration retune — the X08-falsified operating point, forbidden; (e) floor
  change — H3 exonerated, floor step retained formally, forbidden as the factor; (f) K change
  or budget recompute from alt H — violates fixed disclosure; alt-H descriptive only (§3);
  (g) SCL/list/belief decoder — decoder change, out of scope; (h) rerun P20N as-is on 2M —
  answers nothing (wrong-session prior); (i) consume 1.5M VAL remainder 2044..2212 (169 frames,
  one block + stub) or 2M HOLD now — destroys the reserved populations; both stay untouched
  (VAL remainder never decoded; 2M HOLD never touched).
- Session inventory (no new protected access by this planner; provenance from the split
  manifest `nbldpc_v25_split_manifest_v1` read as JSON metadata only, plus P20M/N §2/§4):
  2M TRAIN 2187 frames / 559872 pairs + VAL 729 / 186624 + HOLD 729 / 186624 (256 rows/frame;
  see §4 for frame bases). 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824.
  Geometric position: P20O 2M-VAL DEV is the FIRST 640 VAL frames 2187..2826 (5 blocks of
  128); VAL remainder 2827..2915 (89 frames / 22784 pairs) never used under this packet.
- Runner-delta design choice (frozen; the §10 "design.md" decision): a THIN NEW runner
  module importing the accepted `raw_prior_val_1p5m` runner read-only (which itself
  thin-imports accepted `l1_order_1p5m`: VAL/HOLD population pattern, TRAIN-exclusion gate
  family, order-file + `--order-digest` mechanism with zero Stage-B sampling, P20A
  endpoint/taxonomy/recount/resource machinery, `_selected_diagnostics` code point).
  Exact delta list, nothing else: (d1) prior source → the §3 Stage-A 2M raw-prior artifact
  behind a new `session_prior_identity` gate (canonical digest + lambda-0.0 pin + exact key
  set + H-literal recomputation within 1e-12 + `p_b` cross-check); (d2) alt-L2-table source
  → the §3 Stage-A 2M alt artifact behind a new `alt_l2_identity` gate (file-bytes digest +
  alpha-1.0 pin + floor pin + exact key set + incumbent-p1 equality within 1e-12 + alt-H
  descriptive literals); (d3) K pins → the Stage-A 2M-derived (K_total,K1,K2) with the S2-(i)
  budget-literal display (never a carried absolute); (d4) orders → the Stage-A frozen
  `raw_prior_orders_2m.json` via the reused order-file mechanism (2M-derived L1+L2
  worst-first orders, byte-identical on all four arms; disclosed sets = first-K1 / first-K2
  prefixes); (d5) arms A/B/C/D per §6 (A = 2M-incumbent-L2 operational; B = 2M-alt-L2
  operational; C = 2M-incumbent oracle; D = 2M-alt oracle); (d6) new P20O tag domain (§6);
  (d7) mandatory hazard instrumentation fields (§7) computed post-decode in
  `_l2_hazard_diagnostics` incl. the optional U-domain cross-check scalar, recorded-only;
  (d8) 2M-VAL population + DEV∩build-frames disjointness declared inside the
  TRAIN-exclusion gate (§4). No SC/transform/floor-semantics/tag-semantics change; no second
  factor. The alternative (edit any accepted module) is rejected: it would touch an accepted
  evidence-producing file; the thin importer leaves every accepted file byte-identical.

## 3. Per-session Stage-A freeze (normative — 2M-TRAIN-derived, zero DEV contact)

- Counts source (sole allowed): the 2M TRAIN counts array selected by `--source 2M`
  from the channel-counts file
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`
  (path + source-tag pin only in this packet; the file is NEVER opened/statted/listed by
  the planner; Stage A performs the SINGLE authorized counts-calibration open, budget
  counts 0/1→1/1 for the 2M array ONLY; no other source content: never 1M/1.5M arrays,
  never Model-F CAL). FORBIDDEN derivation inputs: 2M DEV/VAL-remainder/HOLD, any 1M split,
  any 1.5M split (TRAIN DEV, TRAIN remainder, VAL DEV, VAL remainder, HOLD DEV, HOLD
  remainder), Model-F CAL artifact. The V25 counts NPZ SHALL NOT be opened for any other
  array. Stage A performs zero DEV contact (no 2M parquet open/stat, DEV stays 0/1).
- Raw-prior rule (frozen, same form as P20M §3): `n_b[b] = counts_ab.sum(axis=0)`;
  `f_raw[a,b] = counts_ab[a,b]/n_b[b]`; `f_raw = max(f_raw, 1e-15)` then column-renormalize;
  zero columns fall back to `p_global` exactly (Stage A reports the count);
  `p1`/`p2` via accepted `prior.derive_p1`/`derive_p2` under `A = 32*U1 + U2`,
  `FULL_BOB_ONLY` (cites `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py:162-179`).
  Cross-check pinned: `p_b == counts_ab` column totals / total (Stage A reports the integer,
  expected 559872). No lambda anywhere (`lambda_star` stored `0.0`).
- Stage-A products (new artifacts under this queue dir):
  (p1) `raw_prior_2m.npz` with keys exactly
  `counts_ab, f_raw, p1, p2, p_b, lambda_star, floor_value, h1, h2, h_total`
  (`lambda_star` `0.0`; `floor_value` `1e-15`); canonical digest via the frozen
  `per_session_calibration.canonical_prior_digest` recipe (sorted-key `key + shape + dtype +
  C-order bytes` sha256): value `<FROZEN_AT_STAGE_A>` with freeze rule = derive once in
  Stage A, pin in `P20O_FREEZE.md`, gate on equality thereafter; session H literals
  `<FROZEN_AT_STAGE_A>` recomputed via accepted `target_construction.entropy_bits`
  (never hand-filled; `beta_eff_empirical` never hand-filled per AGENTS.md §5.5);
  floor-hit count/rate + zero-column count pinned.
  (p2) `raw_prior_orders_2m.json`: full L1+L2 worst-first permutations + provenance
  (2M-prior digest + program pin + derivation-seed integers), file-bytes sha256
  `<FROZEN_AT_STAGE_A>`.
  (p3) `alt_l2_tables_2m.npz` with keys exactly
  `counts_ab, f_alt, p1, p2_alt, alpha, floor_value, h1_inc, h2_alt, h_total_alt`
  (`alpha` `1.0`; `floor_value` `1e-15`); rule `n_b[b] = counts_ab.sum(axis=0)`;
  `f_alt[a,b] = (counts_ab[a,b]+1)/(n_b[b]+1024)` (α=1 frozen; 1024 = Alice-alphabet size);
  `f_alt = max(f_alt, 1e-15)` then column-renormalize (retained formally; Stage A reports
  the hit count, expected 0); zero columns fall back to `p_global` exactly (Stage A reports
  the count); `p2_alt = derive_p2(f_alt)` under `A = 32*U1+U2`, `FULL_BOB_ONLY`;
  `p1` = the Stage-A 2M incumbent `p1` (L1 fixed; Stage A asserts equality within 1e-12
  elementwise); `h1_inc` = the Stage-A 2M H1 literal; `h2_alt`/`h_total_alt` recomputed
  descriptively via `entropy_bits` on (p1_inc, p2_alt) — DESCRIPTIVE ONLY, never a budget
  input. Identity pin = file-bytes sha256 `<FROZEN_AT_STAGE_A>`.
- Budget rule (S2-i, literal): `K_total = budget_k_total(32768, H_total, 1.3)`
  `= floor((1.3*32768*H_total-64)/5)` clipped `[0,65536]` (cites
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_n_scaling.py:421`;
  `FROZEN_TARGET_F = 1.3`). The declaration MUST be recomputed from the same run's 2M
  session H and displayed as a literal (`1.3*32768*<H_total>-64 over 5, floored, clipped`);
  never carried as an absolute from 1.5M. Value `<FROZEN_AT_STAGE_A>`.
- Split rule: `select_empirical_split` semantics (cites
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_scaling.py:461`) —
  pooled TRAIN mean risks → worst-first `(e,h,index)` L1/L2 orders → exhaustive integer K1
  enumeration with `K2 = K_total-K1` → lexicographic minimum of `(TRAIN residual e sum, K1, K2)`.
  TRAIN risks = 16 synthetic blocks model-sampled from the §3 2M raw prior under frozen
  derivation seeds (§6; L1+L2 genie, 32 calls, Stage A only; never a real frame, never DEV).
  `(K1,K2)` and the worst-first orders freeze at Stage A: values `<FROZEN_AT_STAGE_A>` with
  freeze rule = derive in Stage A, pin integers + order-file digest in `P20O_FREEZE.md`,
  gate on equality thereafter.
- Feasibility literals D1 (Stage A computes, TRAIN-only, zero DEV reads; construction-validity
  quantities, never decoding inputs and never thresholds on results):
  `ce_alt_insample_bits_per_symbol = (1/total) * sum_{a,b} counts_ab[a,b] *
  (-log2 p2_alt[u1(a), b, u2(a)])` with `u1(a) = (a>>5)&31`, `u2(a) = a&31`,
  `total = counts_ab.sum()` (559872 expected; Stage A reports the integer), evaluated on the
  SAME 2M TRAIN counts the tables were built from;
  `ce_incumbent_insample_bits_per_symbol` = same estimator with the 2M incumbent `p2`;
  `alt_feasibility_ceiling_bits = 5*K2+64` (L2-only gate ceiling, `<FROZEN_AT_STAGE_A>`)
  and the operational ceiling `5*K_total+64` for reference;
  `alt_ideal_length_bits = ce_alt_insample_bits_per_symbol * 32768`.
- Gate D2 `alt_construction_budget_feasibility` (Stage A ONLY, evaluated BEFORE any Stage-B
  root creation and before any DEV contact; outcome frozen in `P20O_FREEZE.md` and
  `STATUS.yaml`): IF `alt_ideal_length_bits > 5*K2+64` THEN the construction is declared
  `ALT_CONSTRUCTION_BUDGET_INFEASIBLE` on the 2M point: the Stage-A return reports the D1
  literals, the packet records the point as falsified-by-arithmetic, the 2M DEV segment is
  NOT touched (DEV read stays 0/1), no Stage-B authorization is requested, and the main
  thread re-frames the next factor from the returned literals. ELSE the D1 literals freeze
  and the packet proceeds to Pre-EXECUTE/Stage B as designed.
- Stage B loads the frozen files read-only behind the `session_prior_identity` +
  `alt_l2_identity` gates (digests + lambda-0.0/alpha-1.0/floor pins + exact key sets +
  H-literal recomputation within 1e-12 + `p_b` cross-check + `p1`-equality recheck within
  1e-12, or BLOCKED before any sampling and before any SC call).

## 4. Population and closed/consumed-data rule (normative)

- The following are CONSUMED/CLOSED and SHALL NOT supply P20O blocks: the three P18/P19
  HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599), P20C/P20E/P20F DEV blocks
  (1M 0..383 / 384..767 / 768..1151, remainder 1152..1199 never used), P20H DEV (1.5M TRAIN
  0..383), P20I DEV (384..767), P20J DEV (768..1151), P20K DEV (1152..1535, remainder
  1536..1659), P20M VAL DEV (1.5M VAL 1660..2043), 1.5M VAL remainder 2044..2212 (RESERVED
  never-decoded under this packet), P20N HOLD DEV (1.5M HOLD 2213..2724), HOLD remainder
  2725..2766. The ENTIRE 1M pool and the ENTIRE 1.5M session are fail-closed against P20O
  DEV selection (cross-file gate). 2M TRAIN 0..2186 SHALL NOT supply P20O blocks (build
  frames). 2M HOLD 2916..3644 SHALL NOT be opened/statted/listed/read under this packet.
- 2M-VAL-first-use justification (same canonical TRAIN→held-out separation as P20M §4,
  frozen, not re-argued in Stage A/B): 2M VAL has never been decoded, tuned on, or scored
  by any EXECUTED NB-Polar packet; 2M TRAIN supplies the session hypotheses (raw prior +
  alt table both from TRAIN-fitted counts, never from VAL frames); using VAL as a one-shot
  scoring population is declared once, consumed once, never tuned, never returned to a
  validation role. The 2M VAL remainder stays undecoded; 2M HOLD stays untouched.
- Stage B runs on the DECLARED population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet` ONLY (provenance pin frozen in Stage A by manifest cross-check; mismatch blocks; planner performed zero opens/stats/listings) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 2M TRAIN 2187/559872 + VAL 729/186624 + HOLD 729/186624 (JSON-metadata read only) |
| construction-derivation input | §3 2M TRAIN counts (`--source 2M` array) ONLY (TRAIN-fitted; never a VAL frame) |
| VAL DEV frame rule | FIRST 640 VAL frames in (frame_id, pair_idx) order → frozen VAL base 2187: `2187..2826` (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed) |
| VAL DEV blocks (N=32768) | `2187..2314`, `2315..2442`, `2443..2570`, `2571..2698`, `2699..2826` (5 × 128 frames; 163840 pairs) |
| unused remainder | VAL frames `2827..2915` (89 frames / 22784 pairs) recorded never used — counted, never decoded |
| build-frames disjointness (S2-ii) | counts/build frames ⊂ 2M TRAIN `0..2186` (§3 input = 2M TRAIN counts ONLY); DEV ⊂ 2M VAL `2187..2826`; disjoint by split identity; declared frame sets above; the TRAIN-exclusion gate refuses any overlap before any protected content open |
| consumed-1M exclusions | entire 1M pool (any split/subrange) — overlap refuses before any protected content open |
| consumed-1.5M exclusions | all 1.5M TRAIN `0..1659` + VAL `1660..2212` + HOLD `2213..2766` — overlap refuses before any protected content open |
| 2M TRAIN-as-DEV / 2M HOLD | NONE of TRAIN `0..2186` as DEV; NONE of HOLD `2916..3644` in any form |
| block count | 5 at N=32768 |
| tag domains | new P20O domain (§6) |

- Fail-closed gate family (frozen in the runner, order (a)→(g), cross-file first):
  (a) CROSS-FILE — DEV content-open path + stat-size/sha pin must equal the 2M identity;
  any 1M or 1.5M path or digest mismatch refuses before any SC call (frame integers alone
  are never identity); (b) INTRA-FILE VAL — DEV ranges must overlap NONE of 2M
  TRAIN-exterior/2M-HOLD, and must lie wholly inside 2M VAL 2187..2915, else refuse before
  any protected content open; (c) CONSUMED-1M EXCLUSION — entire 1M pool; (d) CONSUMED-1.5M
  EXCLUSION — all 1.5M ranges above; (e) DEV∩build-frames disjointness declaration: DEV ⊂
  2M-VAL vs build ⊂ 2M-TRAIN with the frame sets above (S2-ii); (f) SESSION-PRIOR/ALT/
  ORDER/K-LITERAL — §3 canonical/file-bytes digests + lambda-0.0/alpha-1.0/floor pins +
  exact key sets + H-literal recomputation within 1e-12 + `p_b` cross-check + `p1`-equality
  within 1e-12 + budget-literal recomputation (S2-i) + order-file digest must match, else
  refuse before any SC call; (g) MAINTAIN_CONFIRMATION_IDENTITY + ORDER-FREEZE — the §6
  construction quadruple + `--source 2M` vocabulary + P20O tag-domain pins must match AND
  the Stage-A frozen 2M order-file digest must match with K1/K2 literals replaying exactly,
  else refuse before any SC call.

## 5. Preregistered disclosure point (normative — 2M-session-derived, frozen at Stage A)

- K rule (S2-i; the per-session constraint): `(K_total,K1,K2)` =
  `<FROZEN_AT_STAGE_A>` (Stage-A derived from the §3 2M session H via the §3 budget+split
  rules; displayed as the `1.3*32768*<H_total>-64 over 5, floored, clipped [0,65536]` literal
  + `select_empirical_split` provenance; never carried as an absolute from 1.5M).
  NO recomputation from alt H (the §3 alt-H literals are descriptive only); NO hand-fill.
- Caps PREREGISTERED per arm at Stage A from the derived point (rule
  `5*(K1+K2)+64` key-dependent bits/block, `10*32768+63 = 327743` public bits/tag,
  one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| A_incumbent_L2_operational (control) | `<FROZEN>` | `<FROZEN>` | `5*(K1+K2)+64` frozen at Stage A | 327743 |
| B_alt_L2_operational (candidate) | same K1 | same K2 | same as A (Δ vs A exactly 0) | 327743 |
| C_incumbent_L2_oracle (diagnostic) | 0 | `<FROZEN K2>` | `5*K2+64` frozen at Stage A | 327743 |
| D_alt_L2_oracle (diagnostic) | 0 | same K2 | same as C (Δ vs C exactly 0) | 327743 |

- Planned totals (frozen at Stage A from the derived integers): key-dependent
  `5*(2*(5*(K1+K2)+64)+2*(5*K2+64))` bits; public `20*327743 = 6554860` bits.
  B-vs-A and D-vs-C key-bit deltas are exactly 0 (construction factor carries ZERO
  disclosure delta by design).
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate
  BLOCKS. Per-record fields pin the session point (`prior_source` raw/2M,
  `k1/k2/k_total`, `budget_literal`, `alt_digest`, `l1_order_digest`, `l2_order_digest`,
  `floor_hit_rate`).

## 6. Arms (frozen; 2M-session construction pair per §§3/5, all else P20N-identical)

- `A_incumbent_L2_operational`: frozen greedy SC with the Stage-A 2M incumbent tables
  (2M raw prior + 2M-derived L1+L2 orders, session K1/K2) (operational control;
  2 SC + 1 P20O-domain tag per block). Paired same-block control for B on the new 2M segment.
- `B_alt_L2_operational`: frozen greedy SC with 2M incumbent `p1` + §3 2M `p2_alt`,
  SAME 2M-derived L1+L2 order prefixes (first-K1 / first-K2), SAME K1/K2
  (operational; the single-factor candidate; 2 SC + 1 tag per block).
- `C_incumbent_L2_oracle`: true-L1-conditioned diagnostic with 2M incumbent `p2`
  at session K2 (provenance ORACLE, deployable=false, excluded from every operational
  aggregate; never a correction result; 1 SC + 1 P20O-domain tag per block).
- `D_alt_L2_oracle`: true-L1-conditioned diagnostic with 2M `p2_alt` at session K2
  (provenance ORACLE, deployable=false, excluded from every operational aggregate;
  never a correction result; 1 SC + 1 P20O-domain tag per block).
- No other arms. Block-major (A, B, C, D) per VAL block; checkpoint after every
  (arm, block) record; 20 records total. P16 construction file unchanged
  (digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  carried read-only); kernel/representation/transform/SC arithmetic unchanged; greedy SC
  only; no SCL/new kernel/model/schema. Stage-A derivation genie calls (32 L1+L2 on 16
  synthetic blocks) run IN STAGE A ONLY; Stage B performs pure VAL scoring (30 SC + 20 tags)
  with ZERO sampling — the Stage-B TRAIN genie call count is pinned at 0.
- Tag domain (new P20O): master 2026092310, prefix
  `nbpolar-p20o-maintain-2m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from ALL of
  P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K/P20L/P20M/P20N.
  Stage A verifies by repo grep that master 2026092310 and focused-test seeds
  `2026092311..2026092317` and derivation seeds `2026092321..2026092324` appear in no
  tracked file outside the P20O runner/tests/packet/spec documents (planner pre-checked
  202609231*/232* absent at freeze time).
- Derivation seeds (frozen): `2026092321..2026092324` (4 streams × 4 blocks = 16 synthetic
  TRAIN blocks model-sampled from the §3 2M raw prior, L1+L2 genie, CONSUMED IN STAGE A to
  produce the frozen orders). Disjoint from every frozen master/stream/tag/test seed by the
  grep rule above. Stage B takes NO derivation seeds and performs no sampling.
- L2 disclosed-set rule (single-factor guard): on ALL four arms the disclosed L2 set is the
  first-K2 positions of the SAME frozen 2M order file (digest-gated); the L1 set is the
  first-K1 of the SAME file. Positions are fixed by the frozen file, never selected on
  closed blocks, consumed ranges, or VAL data.

## 7. Thresholds, endpoints, and mandatory instrumentation (descriptive only — P20M-style)

- Outcome label `TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE`
  iff ALL integrity gates (§9) hold — regardless of exact-count. Any exact count
  (including 0/20 and partials) is COMPLETE when integrity holds.
- Choice + justification: P20M-style descriptive (no recovery/FER/Wilson threshold). This
  is the FIRST independent-session test of the frozen alt construction at per-session
  disclosure — there is no empirical basis for a maintenance threshold here. A 62/64-class
  gate would be an invented threshold, explicitly forbidden. Branch decisions belong to
  main-thread planning AFTER acceptance (§16).
- NO recovery / FER / Wilson / superiority / qualification / promotion claim. Descriptive
  reading only, preregistered before execution: per-arm exact counts; `b_maintained_count`
  = blocks where B is exact; `b_restored_count` = blocks where A fails and B is exact;
  the A→B transition table (A-exact/B-exact, A-exact/B-fail, A-fail/B-exact, A-fail/B-fail);
  and the oracle pair C→D (`d_restored_count`, `d_maintained_count`) as diagnostic only.
  "Maintain" = B exact wherever A exact; "restore" = A fail → B exact. Any (or neither)
  counts as COMPLETE. The positive/negative branch decision stays with the main thread
  after acceptance.
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`, `undetected`
  isolated (never success/FER), plus `decode_failed` / `nonfinite` / `resource_abort` via
  the P20A path. P20A four-endpoint separation (`l1_exact` / `hard_l2_exact` /
  `oracle_l2_exact` / `pair_exact`) per record. First-error coordinate/layer rows (natural
  block symbol index, settled X09-R1 D4) are the primary diagnostic signal. Per-record
  incumbent floor-hit fields (`floor_hits`, `floor_hit_rate`) complete per record (S2
  reporting).
- Mandatory X09-R1 instrumentation (BOTH requirements, per-record SCALARS, scalar-only
  five-file rule intact — no vectors persisted):
  - Req1 (closes H2 — hazard + coverage at the frozen order): fields `l2_order_digest`,
    `l2_prefix_len`, `l2_fail_in_prefix`, `l2_fail_hazard_bits`, `l2_fail_nbhd_mean_bits`,
    `l2_prefix_hazard_mean_bits`.
  - Req2 (sharpens H3 — failure-neighbourhood floor stats on prefix + failing
    neighbourhoods): fields `l2_fail_nbhd_floor_frac`, `l2_prefix_floor_frac`.
  - Semantics (frozen; Stage A pins exact formulas with injected vectors):
    `l2_prefix_len` = session K2 on every record (gated); `l2_order_digest` = the frozen
    2M order-file digest on every record; `l2_fail_in_prefix` = null unless
    `first_error_layer == L2`, else whether the failing position index lies in the disclosed
    L2 prefix set (first-K2 of the frozen 2M L2 order; index spaces are the runner's native
    length-N block arrays per X09-R1 D4); `l2_fail_hazard_bits` = null unless L2 failure,
    else `-log2` arm-table mass at the failing position's true `(U1_cond, B, U2)` cell under
    the record's own arm table (`U1_cond` = hard-L1 candidate on A/B, true high on C/D);
    `l2_fail_nbhd_mean_bits` = null unless L2 failure, else the mean of that hazard quantity
    over the frozen radius-R=8 window around the failing position (clipped to the block);
    `l2_fail_nbhd_floor_frac` = null unless L2 failure, else the fraction of window cells
    whose raw (unfloored column-normalized 2M TRAIN conditional from `counts_ab`) mass is
    below 1e-15; `l2_prefix_hazard_mean_bits` / `l2_prefix_floor_frac` = the same two
    quantities averaged over the disclosed-prefix positions using true cells (every record,
    never null on a completed record).
  - Successor instrumentation item (optional ninth scalar, P20N `MAIN_THREAD_ACCEPTANCE.md`
    §4 item 4): field `l2_fail_in_prefix_u_domain` = null unless `first_error_layer == L2`,
    else whether the U-domain first-mismatch index (computed on `polar_transform` hats vs
    U-domain truth, i.e., U-domain prefix membership) lies in the disclosed L2 prefix set.
    Recording-only, post-decode; closes the domain-mixed `l2_fail_in_prefix` ambiguity
    in-run. Stage A freezes the exact formula with injected vectors + the truth-isolation
    boundary, or freezes the scalar as absent-with-reason before execution — never post-hoc.
    The eight X09-R1 scalars are mandatory regardless.
  - Writer code point (frozen): successor module `l2_alt_maintain_2m.py`, function
    `_l2_hazard_diagnostics(*, block, view, p2_arm, counts_arr, l2_order, k2, first_error,
    ...)` — called post-decode (after tag scoring) from the successor's
    `_operational_record` / `_control_record` equivalents (the P20M `_selected_diagnostics`
    code point, `raw_prior_val_1p5m.py:1306-1334`, is the carried-over callsite pattern).
  - Truth-isolation boundary (normative): block truth (high/low/bob) and the arm tables
    enter `_l2_hazard_diagnostics` for RECORDING ONLY after all SC calls for the record have
    completed; its outputs are written into the record dict and never passed to
    `run_operational_block`, `run_oracle_control_block`, `_decode_layer`, `build_p1_metrics`,
    `gather_p2_metrics`, or any disclosure/order decision. A focused truth-isolation
    sentinel test pins this boundary (mutating truth changes no metric/decision input).

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized execution;
  no rerun, no seed change, no prior/budget/order/construction tuning after preregistration.
  Execution-error rerun only as a recorded repeat of the identical freeze, never as tuning.
  P20H–P20N spent attempts do NOT transfer (independent packet).
- Reads (split-counted): counts-calibration opens 1/1 (Stage A, 2M array ONLY, consumed at
  the first calibration content open; all other arrays 0) + VAL-DEV open 1/1 reserved for
  Stage B (parquet, consumed at first VAL content open). VAL-remainder reads 0; 2M HOLD
  reads 0; 1M/1.5M reads 0. Any reopen, new calibration, real-frame use for derivation
  outside §3, or VAL refit is forbidden. Prior-file/alt-file loads and synthetic derivation
  sampling are worktree-file/prior reads, not protected opens.
- SC/tag/genie budget: Stage-A derivation 32 TRAIN genie calls (L1+L2 on 16 synthetic
  blocks; frozen order-file product, accounted in the Stage-A freeze) + Stage-B pure VAL
  30 SC (5 blocks × (2+2+1+1)) + 20 tags + 20 records with ZERO Stage-B sampling
  (Stage-B TRAIN genie calls pinned at 0); derived per-record recomputation must equal
  counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence + accounting;
  abort is BLOCKED, never success. Wall/RSS ceilings frozen in Stage-A freeze (P20-class
  reference at larger DEV decoder budget: P20N ~164 s / ~631 MB for 24-SC / 16-tag HOLD
  budget; P20O plans 30-SC / 20-tag VAL budget; external timeout 1200 s + virtual/RSS caps
  2 GiB + single thread frozen).
- Strategy stop rules binding: no tuning on closed blocks or the new VAL DEV after the one
  shot; no reuse of consumed 1M pool (any split/subrange), any consumed 1.5M range, 2M TRAIN
  as DEV, 2M VAL remainder 2827..2915 beyond counting, 2M HOLD, or any other session; no
  third factor after inconclusive single-factor; no near-raw disclosure claim; no
  oracle-as-operational; no population-reliability inference from this single gate alone;
  no efficiency tuning inside this packet.
- SCL entry gate UNCHANGED (unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B five files)

- Stage-A freeze pins (one counts open + zero DEV opens): counts-input identity (path +
  `--source 2M` tag + array digest + shape) + raw-prior artifact path + canonical digest +
  H literals + `p_b` cross-check + floor-hit count/rate + zero-column count; K_total literal
  recomputation display + (K1,K2) integers + derivation-seed integers + worst-first orders +
  order-file digest; alt-table artifact path + file-bytes digest + alpha/floor pins + exact
  key set + `p1`-equality max-abs-diff + floor-hit count/rate + zero-column count + `f_alt`
  min/max + descriptive alt-H literals + D1 feasibility literals + D2 gate outcome;
  exact module path + N-flag Stage-B command verbatim + population integers + caps + budgets
  + tag domain + P16 construction digest; recorded in `P20O_FREEZE.md`. Stage-A product
  identities: paths `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz`,
  `raw_prior_orders_2m.json`, `alt_l2_tables_2m.npz` (file-bytes/canonical sha256 pinned
  in the freeze).
- Stage-B root:
  `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/`
  (exactly five files; per-(arm, block) checkpointing; pure VAL scoring — zero sampling;
  one VAL content open; no reopen/rerun). Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`
  (P16 construction digest + session-prior digest-gate proof + alt-table digest-gate proof
  (file bytes sha256 equals the frozen `--alt-digest`) + order-file digest-gate proof +
  K-literal display + budget-literal display + derivation-seed pins (provenance only, no
  Stage-B sampling) + split manifest + VAL DEV integers + DEV∩build-frames disjointness
  declaration with frame sets), `per_block_arm_outcomes.jsonl` (20 records at completion),
  `aggregate_summary.json`, `report.md`. Per-record §7 endpoints + first error
  coordinate/layer, zero-count hits, floor hits + floor-hit rate + log loss, true-H vs
  candidate-H L2 NLL, taxonomy, construction-point fields (`l2_construction`, `k1/k2/k_total`,
  `prior_digest`, `alt_digest`, `l1_order_digest`, `l2_order_digest`) + the EIGHT mandatory
  instrumentation scalars of §7 (+ the optional ninth U-domain scalar when frozen present).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); genie call
  counts (Stage-A 32 + Stage-B 0) + SC counts (L1/L2 split) + tag counts exact; block
  SER/NLL; wall/RSS; `b_maintained_count` / `b_restored_count` / `d_restored_count` /
  `d_maintained_count` descriptive + the A→B transition table; per-arm floor-hit rate +
  per-arm prefix hazard means reported.
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `session_prior_identity` (new 2M npz canonical
  digest + lambda-0.0/floor pins + exact key set + H literals within 1e-12 + `p_b`
  cross-check); `alt_l2_identity` (file-bytes digest + alpha-1.0/floor pins + exact key
  set + `p1`-equality within 1e-12 + descriptive alt-H literals);
  `alt_construction_budget_feasibility` (Stage-A-only D2 gate: FEASIBLE outcome required
  before Pre-EXECUTE; INFEASIBLE ends the packet at Stage A with VAL untouched);
  `dev_split_manifest_identity`; `dev_block_range_identity` (§4 gate family (a)→(g):
  cross-file first, then intra-file VAL-containment, then consumed-1M, consumed-1.5M
  exclusions incl. the DEV∩build-frames disjointness declaration, then session-prior +
  alt-identity + order-freeze + K-literal + maintain-confirmation-identity pins);
  `order_derivation_identity` (program pin + session-prior-digest input pin +
  derivation-seed pins + Stage-A order-file digest, Stage-B file-bytes digest equality
  replay-exact, zero Stage-B sampling); `k_literal_exact` + `budget_literal_recomputed`
  (S2-i: f=1.3 literal recomputed from the same-run 2M session H and displayed, never a
  carried absolute); `target_population_contract`; `dev_population_exact` (640 VAL frames /
  163840 pairs / 256 rows per frame / pair indices / symbol range);
  `blocks_exact_with_declared_remainder` (five exact VAL DEV ranges per arm in block-major
  slot order + never-used VAL remainder 89 frames / 22784 pairs, counted from the pool but
  never decoded); `twenty_records_exact`; `genie_calls_exact` (Stage-A 32 + Stage-B 0);
  `sc_calls_exact` (derived 30); `tags_exact` (derived 20);
  `orders_valid_k_prefixes_within_registered_arms` (2M-derived prefixes + construction
  quadruple); `hazard_instrumentation_complete` (all eight §7 scalars present with correct
  nullability on every completed record + the ninth U-domain scalar present-or-absent per
  the Stage-A freeze); `floor_hit_rate_reported`; `oracle_isolation`;
  `buckets_disjoint_exhaustive` (unique arm/block + schema); `undetected_zero`;
  `nonfinite_zero`; `truth_isolation`; `disclosure_recount_exact`;
  `one_open_per_protected_input` (counts 1 + VAL-DEV 1); `input_stat_unchanged`;
  `no_unregistered_access`; `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (derivation + injected tests + implementation-freeze; authorized separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_l2_alt_maintain_2m.py -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20o/<uuid>/`
  temp root; protected-open audit declared separately (counts 1 + VAL-DEV 0 at
  Stage-A close). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A derivation (single protected counts open for the 2M array ONLY, zero DEV
  contact): open `--source 2M` counts → apply the §3 raw rule → write `raw_prior_2m.npz` +
  freeze digest/H literals/`p_b`/floor-rate → model-sample 16 synthetic TRAIN blocks under
  the frozen derivation seeds → L1+L2 genie risks → pooled means → `select_empirical_split`
  → freeze K_total/(K1,K2)/orders → write `raw_prior_orders_2m.json` + freeze file digest →
  apply the §3 α=1 rule from the SAME counts → write `alt_l2_tables_2m.npz` + freeze
  file-bytes digest/alpha/floor/key-set/`p1`-equality/floor-rate/zero-columns/`f_alt`-range/
  descriptive alt-H → compute D1 literals + evaluate D2 BEFORE any VAL contact. Template
  (pins filled in the freeze; all flags required, no production default):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_maintain_2m --derive --counts comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 2M --alpha 1 --floor 1e-15 --n 32768 --target-f 1.3 --deriv-seeds 2026092321 2026092322 2026092323 2026092324 --out-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --out-orders .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --out-alt .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz
```
  Stage A confirms the module path (thin importer of accepted `raw_prior_val_1p5m` per the
  §2 delta list d1–d8, or freezes a written equivalent with justification) and the `--alpha`
  vocabulary (only `1`) + `--source` vocabulary (only `2M`). Forbidden by default:
  `longrun_*`, `minrerun_*`, `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data,
  full sweeps.
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A freeze with the
  `<FROZEN_AT_STAGE_A>` pins filled; NOT AUTHORIZED until independent Pre-EXECUTE PASS +
  pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_maintain_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest <FROZEN_AT_STAGE_A> --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest <FROZEN_AT_STAGE_A> --source 2M --floor 1e-15 --n 32768 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames 2187 2826 --block-frames 128 --remainder-frames 2827 2915 --tag-master 2026092310 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m
```
  All flags required, no production default; four hardcoded arms with the construction swap
  pinned (never CLI-tunable: A = 2M-incumbent-L2 at session K; B = 2M-alt-L2 at session K;
  C = 2M-incumbent oracle; D = 2M-alt oracle); Stage-B prior path MUST equal the §3 frozen
  digests; `--alpha` takes no Stage-B value (construction is frozen in the alt file).
  Stage A fills every `<FROZEN_AT_STAGE_A>` pin (`--prior-digest`, `--alt-digest`,
  `--k1/--k2`, `--order-digest`) plus the `--source` vocabulary (only `2M`). Forbidden by
  default as above.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git show HEAD:`
  blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: raw-prior artifact `raw_prior_2m.npz` (+ canonical digest/H-literal/`p_b`/
  floor-rate freeze) + order file `raw_prior_orders_2m.json` (+ digest freeze) + alt-table
  artifact `alt_l2_tables_2m.npz` (+ file-bytes digest/alpha/floor/key-set/`p1`-equality/
  floor-rate/alt-H freeze) + thin runner + focused injected tests + Stage-A freeze +
  implementation notes (exact files, diffs, test commands/results, frozen prior/budget/
  split/orders/population/cap/command, D1 feasibility literals + D2 gate outcome).
  Protected content opens 1 at Stage-A close (counts 1/1 for the 2M array ONLY + VAL-DEV 0/1;
  derivation seeds are integers; synthetic derivation consumes only the §3 counts array).
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md`
  (+ freeze, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md`
  at gates).
- OpenSpec P20O delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20o/spec.md`
  + `tasks.md` P20O section (same umbrella change as P18/P19/P20A/P20B/P20C/P20E/P20F/P20G/
  P20H/P20I/P20J/P20K/P20M/P20N; no new top-level change).

## 12. Allowed work

- New thin maintain-confirmation runner (importer per §2 d1–d8) + focused injected tests
  (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py`, `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`,
  `raw_prior_val_1p5m.py` (gate/population/record-writer pattern references;
  `raw_prior_val_1p5m` additionally the import target), `l2_alt_hold_1p5m.py`
  (construction-swap + instrumentation pattern reference), P13/P16 machinery
  (`target_n_scaling.budget_k_total` + `empirical_genie_scaling.select_empirical_split`
  as the derivation rules; `target_n_scaling.allocate_layer_ks` as same-family reference
  only) (+ `construction.py` / `prior.py` / `sc.py` contracts as called).
- Single protected counts-calibration open of the §3 2M TRAIN array IN STAGE A ONLY +
  closed-form §3 raw derivation + synthetic TRAIN sampling from the derived 2M raw prior
  under frozen seeds IN STAGE A ONLY + closed-form §3 α=1 alt derivation from the SAME
  counts IN STAGE A ONLY to produce the three frozen artifacts (§§3/9; zero DEV contact).
- P20O OpenSpec delta + packet docs + Stage-A freeze/return/review files + Stage-B
  evidence root (root only after Stage-B authorization) + the three frozen Stage-A products
  (§3/§9 identity).

## 13. Forbidden work

- Any NPZ/parquet content open or stat of 2M VAL-DEV/VAL-remainder/HOLD, any 1M split, or
  any 1.5M split in Stage A (Stage-A protected opens: counts 1/1 for the 2M array ONLY,
  VAL-DEV 0/1); any second counts open or any other-array open; any K carried as an absolute
  from 1.5M (S2-i); any derivation on real DEV/VAL/HOLD frames at any stage; any decoder
  execution before Pre-EXECUTE PASS + pasted Stage-B authorization.
- Any change to GF32/transform/SC arithmetic, floor value, 2M L1 tables, 2M L1/L2 orders,
  disclosed sets, tag scheme semantics, outcome precedence, accepted evidence roots, P20N
  products, X08/X09 probe roots, or `src/` + `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the consumed 1M
  pool (any split/subrange), any consumed 1.5M range (TRAIN 0..1659, VAL 1660..2212, HOLD
  2213..2766), 2M TRAIN as DEV, 2M VAL remainder 2827..2915, or 2M HOLD; no second
  construction, no construction sweep, no order re-derivation, no disclosure change, no
  efficiency tuning; no new-block peeking before the authorized attempt; no calibration on DEV/VAL.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push;
  no self-acceptance; no P20D scope creep beyond the single frozen construction; no
  P20H–P20N rerun under this packet.

## 14. Acceptance IDs

- `P20O-R1`: 2M raw prior derived read-only from the §3 2M TRAIN counts under the frozen
  raw rule (no lambda; floor + renorm + `derive_p1`/`derive_p2` pins; `p_b` cross-check;
  single protected counts open for the 2M array ONLY; all other arrays never opened);
  new artifact canonical digest + H literals + floor-hit rate frozen at Stage A.
  Derivation-gate BLOCKED → planner rework, never a Stage-B fallback.
- `P20O-R2`: budget/split/orders frozen 2M-session-derived (S2-i literal recomputation
  displayed from same-run 2M H; `select_empirical_split` semantics on 16 synthetic 2M-TRAIN
  risks under frozen derivation seeds 2026092321..2026092324; DEV-zero contact; Stage-A
  order-file digest + Stage-B digest-gate equality, zero Stage-B sampling);
  closed/consumed blocks select nothing; consumed 1M pool + entire 1.5M session excluded by
  source-tagged cross-file gates; 2M TRAIN-as-DEV + 2M HOLD excluded; 2M VAL DEV 2187..2826
  (5 blocks 2187..2314/2315..2442/2443..2570/2571..2698/2699..2826, VAL remainder 2827..2915
  never used) gated + Pre-EXECUTE-approved; 1M/1.5M untouched in every form.
- `P20O-R3`: disclosure point preregistered per arm from the 2M-derived integers
  (A/B `5*(K1+K2)+64` with Δ exactly 0; C/D `5*K2+64` with Δ exactly 0; 327743 public;
  totals frozen at Stage A), recount mismatch 0; CE ratios never called efficiency.
- `P20O-R4`: single-factor construction instantiation (A 2M-incumbent-control pins +
  B 2M-alt-candidate pins + shared-prefix rule + C/D oracle pair, §3 α=1 rule on the SAME
  2M counts, `p1`-equality within 1e-12) frozen before execution, unchanged after; P16
  construction migration pinned; no tag-guided selection, no evidence reuse, no post-hoc
  re-picking, no re-derivation.
- `P20O-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9; `undetected`
  isolated; oracle arms never operational; first-error coordinate/layer rows + per-record
  floor-hit fields + all eight §7 hazard/coverage scalars complete per record with correct
  nullability (+ the ninth U-domain scalar present-or-absent per the Stage-A freeze);
  instrumentation recorded-only (truth-isolation sentinel green).
- `P20O-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning; split-counted
  reads (counts 1/1 for the 2M array ONLY + VAL-DEV 1/1 + VAL-remainder 0 + HOLD 0 + 1M/1.5M 0);
  resource aborts via P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20O-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded (Pre-EXECUTE explicitly
  adjudicates §3 prior/alt derivation + D2 feasibility outcome + §5 budget/K-literal + §4
  gate family + §2 runner-delta design + §7 instrumentation boundary incl. the U-domain
  scalar); main-thread acceptance owns the label; descriptive-only, no FER/qualification/
  promotion language; branch reading (§16) stays planning input, never an in-packet verdict;
  honest-scope statement (§0) repeated verbatim in the return.
- `P20O-R8`: Stage-A suites green on injected data with the declared single-counts-open
  audit (counts 1/1 for the 2M array ONLY + VAL-DEV 0/1 at Stage-A close; 1M/1.5M/2M-HOLD
  non-access except the §3 array); no commit/push; frozen dirs byte-untouched except the
  §12 manifest.
- `P20O-R9`: feasibility literals + gate (D1 estimator frozen with 2M-TRAIN-only inputs,
  zero DEV reads; D2 outcome frozen in `P20O_FREEZE.md`/STATUS BEFORE any VAL contact;
  INFEASIBLE → VAL untouched, no Stage-B request, point recorded falsified-by-arithmetic;
  FEASIBLE → literals frozen, packet proceeds). Gate-fired-by-arithmetic → main-thread
  re-frame, never a Stage-B fallback.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs `P20O-R1..R9`
(stage-appropriately) complete with changed files + exact commands/results + artifact
inventory (incl. all three Stage-A product digests) + split open audit (counts + VAL-DEV +
VAL-remainder + HOLD + 1M/1.5M separately); or (b) a concrete blocker with failing command,
exact error/traceback, attempted remedies, and the ONE decision needed from the main thread.
"Still incomplete" is not a completion report. The operator never marks its own work accepted
and never authorizes Stage B.

## 16. Deferred options (not in this packet)

- B-maintained (B exact wherever A exact, with or without an additional A-fail→B-exact event)
  → efficiency/disclosure-minimality planning (deferred): trigger = genuine 2M maintain event
  under the frozen construction at per-session disclosure. Main thread re-evaluates with the
  full chain evidence in hand. This packet prejudges none of it and licenses no reliability claim.
- B-zero-maintain with L2-layer persistence → next upstream single factor (deferred):
  trigger = genuine alt-construction negative on the independent session — B maintains NONE
  and restores NONE with operational first errors remaining L2-layer (and D maintains/restores
  NONE under true L1). Only THEN is the Laplace-α1 L2 form falsified as the fix on a second
  session, and only then does exactly ONE of (L2-order positions under the raw prior / L2-side
  bounded search at the fixed point / second single construction form) become the next single
  factor on further new data by main-thread planning. Nothing is auto-triggered inside this packet.
- B-zero-maintain with L1-layer return → prior/L1-side re-evaluation (deferred): trigger =
  operational first errors returning to L1-layer under the alt L2 on 2M (L1-side regression
  signal, not an L2 win). Main thread re-evaluates with the full chain evidence in hand.
- Disclosure-minimality probe, efficiency optimization, closure of the 1M-HOLD thread, any
  further 2M-HOLD use: ALL continue deferred / out of scope, re-evaluated against P20O
  accepted evidence after acceptance.
- 2M VAL remainder 2827..2915 stays never-decoded and 2M HOLD stays pristine under this
  packet as follow-up populations. Any follow-up packet needs its own freeze, tag domain,
  and reviews. 2M VAL DEV 2187..2826 is CONSUMED by this packet regardless of outcome.

(End of file)
