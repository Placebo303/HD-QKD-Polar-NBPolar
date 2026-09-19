# Phase 4-P20M — Frozen raw-prior + session-budget packet on type2_1p5M_20260121_183806 (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage A derivation-freeze, Stage B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read, decoder execution, or commit/push is authorized by this file.
- Predecessor: `NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M` terminal
  `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_512_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; DEV open 1/1 SPENT
  on 1.5M TRAIN 1152..1535; 9/9 records; 21/21 gates PASS; E0 base-K1 0/3
  verify_failed + E1 L1+512 (K1 831, keyΔ +2560) 0/3 verify_failed +
  e1_restored 0/3; all six operational first errors L1-layer; E2 oracle 3/3 exact
  isolated; undetected 0; SC 15/15; tags 9/9; recount 0; key 309966 /
  public 2949687; 2M pristine by non-access; Pre-RESULT PASS).
- X08 audit (Tier-X probe, completed, reviewer-go focused review all-PASS;
  `workspace/probes/nbpolar_x08_per_session_prior_entropy_audit/results.json`):
  the P20H artifact
  `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz`
  (canonical digest `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`,
  keys exactly `counts_ab/f_prior/p1/p2/p_b/lambda_star/floor_value/h1/h2/h_total`):
  lambda=137.3823795883264 reproduces stored H1=2.006647056368773,
  H2=1.9017235959286112, TOTAL=3.908370652297384 (exact); raw-MLE + 1e-15 floor +
  column-renorm variant gives H1=0.025199496923753, H2=0.800366554749543,
  TOTAL=0.825566051673296 with 1,046,140/1,048,576 cells floor-hit (all zero-count
  cells) and 0 zero columns; implied K_total 33285 (lambda) vs 7020 (raw) via
  `floor((1.3*32768*H_total-64)/5)` clipped [0,65536]; N*H1 side info 65754 bits
  vs 826 bits. λ is confirmed as the entropy/budget root cause of the
  P20H/P20I/P20J/P20K L1 failures (all operational arms first-error at L1, 0/3;
  oracle-L1 arms 3/3). X08 does NOT prove a corrected prior recovers blocks —
  that is exactly what this successor tests out-of-sample. The 1M-HOLD thread
  (P18/P19 0/3 incl. true-L1 control) stays open and is out of scope here.
- Supersession: `NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M` is SUPERSEDED-BY-P20M per the
  2026-09-19 user decision (Stage B never executed, zero consumption: DEV 0/1,
  HOLD 0/1, attempt 0/1; its files preserved as-is). Its declared VAL DEV segment
  1660..2043 is released to this successor.
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2
  (reproducible reliability; confirmation on new blocks/sessions; stop rules)
  and `docs/nbpolar/ROADMAP.md`.
- Gate discipline: any standing long-horizon authorization does NOT collapse
  Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_1p5M_20260121_183806` (1.5M), scoring population
  first-use of 1.5M VAL (see §4). The 2M session
  (`type2_2M_20260121_183657`) is registered but RESERVED pristine (see §4, §16).

## 0. Planner header (OpenSpec workflow)

- **Goal**: Test the X08 finding out-of-sample with exactly ONE preregistered
  operating-point change against the P20H/P20I/P20J/P20K failing point — the
  corrected raw-count prior + its session-derived budget (K_total via the literal
  f=1.3 formula on the same-run session H; (K1,K2) split + worst-first orders via
  the accepted P13/P16 machinery on synthetic session-TRAIN risks) — on three NEW
  1.5M VAL blocks at N=32768 (three arms G0/G1/G2, new P20M tag domain), zero
  further tuning. Decide whether the corrected prior + session budget restores
  any complete operational block where λ + carried-over K restored none.
- **Non-Goals**: No λ tuning or smoothing-form search beyond the single frozen
  raw rule; no disclosure tier beyond the session-derived point; no order
  reselection on real data; no P20D alternative L2 construction; no bounded
  search; no SCL/new kernel/model/schema; no FER/qualification/promotion claim;
  no reuse of any consumed/closed range; no 2M first use; no closure of the
  1M-HOLD thread.
- **Impact Scope**: New thin runner + focused injected tests + P20M OpenSpec
  delta (`specs/nbpolar-phase4-p20m/spec.md` + `tasks.md` P20M section, same
  umbrella change `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A freeze
  (incl. corrected-prior artifact + order file) + implementation notes + Stage-B
  evidence root. No change to `src/`, `experiments/`, `tools/`, P16 construction
  file, P12–P20K accepted roots, P20H calibration product, X08 probe root, or
  `results/` / `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20M-R1..R8 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance.
  Descriptive-only label; `undetected` isolated; oracle never operational.
- **Tasks**: (planner task list for coder agents) H1 derive + freeze corrected
  prior artifact (§3, R1); H2 freeze budget/split/orders + population/gates
  (§4, R2); H3 freeze caps from the derived point (§5, R3); H4 freeze
  operating-point swap rule, G0 control pinned (§2/§6, R4); H5 wire
  endpoints/taxonomy + floor-hit reporting (§7, R5); H6 enforce one-shot
  budget/stop (§8, R6); H7 Stage-A suites green with zero-protected-open audit
  (R8); H8 independent Pre-EXECUTE adjudication of prior/budget/population
  gates (R7); H9 single authorized Stage-B attempt (R6/R7); H10 independent
  Pre-RESULT + acceptance.
- **Honest scope** (binding on proposal/design/packet/return language): this
  packet tests the corrected prior + session-derived budget at the operational
  point on the first genuinely out-of-sample 1.5M segment; it does not establish
  NB-Polar real-block recovery in general, does not close the 1M-HOLD thread,
  and the current published gates on DEV must not be confused with
  out-of-sample evidence.

## 1. Mission

With ONE preregistered operating-point change against P20H/P20I/P20J/P20K —
the corrected raw-count prior (no lambda anywhere) + its session-derived
disclosure point (Stage-A derived and frozen, Stage-B read-only) — and
everything else carried over (floor 1e-15, N=32768, greedy SC only, new P20M
tag domains only), zero further tuning:

> Does the corrected prior + session-derived budget restore any complete
> operational block on three NEW 1.5M VAL blocks (1660..2043) — and where does
> the first error move when the prior entropy (and hence the budget) drops from
> the λ-inflated point to the raw-count point?

P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, P20K DEV 1152..1535 are
CONSUMED (9+9+9+9 records, DEV 1/1 + attempt 1/1 SPENT each) and SHALL NOT
supply P20M blocks. 1.5M TRAIN remainder 1536..1659 (124 frames, sub-block) is
documented insufficient and SHALL NOT supply P20M blocks. P20L never executed
(zero consumption) and its VAL declaration is released, not consumed. All
branches after this packet are deferred to §16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- Disclosure route closed on 1.5M calibrated data (descriptive, convergent
  H/I/J/K): +128 moved coordinates without restoration (mixed move); +256
  deferred every first error without restoration; +512 again restored nothing
  (all six operational first errors L1-layer, keyΔ +2560 spent). The +128/+256/
  +512 doubling chain is COMPLETE as evidence. Oracle reading: 3/3 exact under
  true-L1 conditioning at base K2 on EVERY 1.5M TRAIN segment (12/12) — GIVEN
  true L1, the base-K2 L2 path suffices; the bottleneck is L1-side.
- X08 root cause (frozen input, not re-litigated): λ=137.38 lifts session H1
  ~0.025→2.007 and inflates K_total 7020→33285 while every operational arm ran
  the carried-over K1=319 (frozen K1 levels 319/447/575/831 provide only
  1595/2235/2875/4155 bits against N*H1 side info 65754 bits at λ vs 826 bits
  raw). The prior form and the budget derived from its H are ONE operating-point
  factor: under S2 gate (i) the f=1.3 budget MUST be recomputed from the
  same-run session H, so prior and budget cannot vary independently without
  violating the gate. This packet therefore swaps the operating point as a
  bundle and holds everything else fixed.
- Alternatives rejected in writing: (a) further disclosure tiers (any +ΔK1) —
  chain complete, forbidden; (b) rerun any of P20H/I/J/K as-is — attempts
  exhausted, forbidden; (c) refit/resmooth/relambda on any DEV/VAL — DEV-tuning,
  forbidden (§3); (d) K hand-picked or carried as an absolute from another
  session — violates S2-(i), forbidden; (e) order swap on real data inside this
  packet — second factor (P20L superseded, order work deferred to §16);
  (f) bounded search / P20D / efficiency inside this packet — second factors,
  deferred; (g) consume 2M now — destroys the independent-session option;
  2M stays pristine.
- Session inventory (no new protected access by this planner; provenance from
  P20G/H/I/J/K §2 + split manifest `nbldpc_v25_split_manifest_v1`): 1.5M TRAIN
  1660/424960 + VAL 553/141568 + HOLD 554/141824 (256 rows/frame exact); pairs
  size 1869178 B / sha `ca351e52…a06b`; 2M TRAIN 2187/559872 reserved.
  Geometric position (TRAIN base 0 carried from P20H §3): P20H 0..383, P20I
  384..767, P20J 768..1151, P20K 1152..1535 consumed; remainder 1536..1659
  (124 frames / 31744 pairs, < one 128-frame block) never used; VAL 1660..2212
  never touched by any executed NB-Polar packet (P20L declared but never ran);
  HOLD 2213..2766 never touched. P20M DEV is the FIRST 384 VAL frames
  1660..2043; VAL remainder 2044..2212 (169 frames) never used under this packet.
- Runner-delta design choice (frozen; the §10 "design.md" decision): a THIN NEW
  runner module importing the accepted `l1_order_1p5m` runner read-only (it
  already implements the VAL population, the TRAIN-exclusion gate family, the
  Stage-A order-file + `--order-digest` mechanism with zero Stage-B sampling,
  and the P20A endpoint/taxonomy/recount/resource machinery). Exact delta list,
  nothing else: (d1) prior source → the §3 corrected-prior artifact behind a new
  `corrected_prior_identity` gate (digest + lambda-0.0 pin + exact key set +
  H-literal recomputation within 1e-12); (d2) K pins → the Stage-A derived
  (K_total, K1, K2) with the S2-(i) budget-literal display; (d3) orders → the
  Stage-A frozen `raw_prior_orders_1p5m.json` via the reused order-file
  mechanism (L1+L2 worst-first orders from the corrected prior); (d4) arms
  G0/G1/G2 per §6 (G0 = λ-prior/P16-order control at carried-over K);
  (d5) new P20M tag domain (§6); (d6) per-record floor-hit fields + the S2
  `floor_hit_rate_reported` gate; (d7) DEV∩build-frames disjointness declared
  inside the TRAIN-exclusion gate (§4). No SC/transform/floor/tag-semantics
  change; no second factor. The alternative (documented minimal delta to the
  accepted module) is rejected: it would touch an accepted evidence-producing
  file; the thin importer leaves every accepted file byte-identical.

## 3. Corrected-prior freeze (normative — Stage-A derivation, zero new protected counts reads)

- Prior rule (frozen): raw-count MLE + 1e-15 floor + column renormalize, no
  lambda anywhere. Source of `counts_ab`: the X08/P20H worktree npz file
  `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz`
  (digest-pinned `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`;
  reading its `counts_ab` array in Stage A is a WORKTREE-FILE read — zero new
  protected counts reads; split-counted counts budget stays 0/0). Rule detail:
  `n_b[b] = counts_ab.sum(axis=0)`; `f_raw[a,b] = counts_ab[a,b]/n_b[b]`;
  `f_raw = max(f_raw, 1e-15)` then column-renormalize; zero columns fall back to
  `p_global` exactly (X08 reference: 0 zero columns expected; Stage A reports
  the count). `p1`/`p2` via accepted `prior.derive_p1`/`derive_p2` under
  `A = 32*U1 + U2`, `FULL_BOB_ONLY` (cites:
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py:162-179`).
  Cross-check pinned: `p_b == counts_ab` column totals / total (X08 reference
  total 424960).
- Stage-A product (new artifact under this queue dir): `raw_prior_1p5m.npz`
  with keys exactly `counts_ab, f_raw, p1, p2, p_b, lambda_star, floor_value,
  h1, h2, h_total` (`lambda_star` stored `0.0` = "no smoothing" marker;
  `floor_value` stored `1e-15`). Canonical digest via the frozen
  `per_session_calibration.canonical_prior_digest` recipe (sorted-key `key +
  shape + dtype + C-order bytes` sha256): value `<FROZEN_AT_STAGE_A>` with
  freeze rule = recompute in Stage A, pin in `P20M_FREEZE.md`, gate on equality
  thereafter. Session H literals `<FROZEN_AT_STAGE_A>` (X08 descriptive
  reference only: H1 `0.025199496923753` / H2 `0.800366554749543` / TOTAL
  `0.825566051673296`; Stage A recomputes via the accepted
  `target_construction.entropy_bits` functional and freezes the literals).
- Stage B loads the frozen file read-only behind the `corrected_prior_identity`
  gate (digest equality + lambda-0.0 pin + floor pin + exact key set +
  recomputed H1/H2/TOTAL within 1e-12 of the frozen literals + `p_b`
  cross-check, or BLOCKED before any sampling and before any SC call).
- FORBIDDEN inputs for derivation or fitting: 1.5M DEV (1660..2043 and
  remainder), 1.5M HOLD, any consumed 1.5M TRAIN DEV, TRAIN remainder 1536..1659,
  ANY 1M split, reserved 2M, Model-F CAL artifact. No calibration fallback
  inside Stage B. The V25 counts NPZ is NEVER opened in this packet.

## 4. Population and closed/consumed-data rule (normative)

- The three P18/P19 HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599),
  P20C/P20E/P20F DEV blocks (1M 0..383 / 384..767 / 768..1151, remainder
  1152..1199 never used), P20H DEV blocks (1.5M TRAIN 0..383), P20I DEV blocks
  (1.5M TRAIN 384..767), P20J DEV blocks (1.5M TRAIN 768..1151), and P20K DEV
  blocks (1.5M TRAIN 1152..1535, remainder accounting 1536..1659) are
  CONSUMED/CLOSED and SHALL NOT supply P20M blocks. The ENTIRE 1M pool is
  fail-closed against P20M DEV selection (cross-file gate). 1.5M TRAIN
  remainder 1536..1659 (124 frames < one 128-frame N=32768 block) is
  documented insufficient and SHALL NOT supply P20M blocks.
- The 2M session file SHALL NOT be opened, statted, listed, or read under this
  packet (reserved, not consumed; pristine by non-access; stat itself violates
  the packet).
- VAL-first-use justification (carried frozen from P20L §4): 1.5M VAL 1660..2212
  has never been decoded, tuned on, or scored by any EXECUTED NB-Polar packet;
  TRAIN is geometrically exhausted for N=32768 DEV; 2M must be preserved for a
  future independent-session confirmation once something restores. Using VAL as
  a one-shot scoring population with TRAIN-derived hypotheses (corrected prior
  from TRAIN-fitted counts, never from VAL frames) is the canonical
  TRAIN→held-out separation — PROVIDED it is declared once, consumed once,
  never tuned, and never returned to a validation role. HOLD stays untouched;
  the VAL remainder stays undecoded. Frozen, not re-argued in Stage A/B.
- Stage B runs on the DECLARED population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin; mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| prior-derivation input | §3 worktree `counts_ab` ONLY (TRAIN-fitted; never a VAL frame) |
| DEV frame rule | FIRST 384 VAL frames in (frame_id, pair_idx) order → frozen VAL base 1660: `1660..2043` (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed) |
| DEV blocks (N=32768) | `1660..1787`, `1788..1915`, `1916..2043` (3 × 128 frames) |
| unused remainder | VAL frames `2044..2212` (169 frames / 43264 pairs) recorded never used — counted, never decoded |
| build-frames disjointness (S2-ii) | counts/build frames ⊂ TRAIN `0..1659` (P20H §3 input = 1.5M TRAIN counts ONLY); DEV ⊂ VAL `1660..2043`; disjoint by split identity; declared frame sets above; the TRAIN-exclusion gate refuses any overlap before any protected content open |
| intra-file TRAIN/HOLD | TRAIN 0..1659 / HOLD 2213..2766 — disjoint by fail-closed gate (TRAIN-consumed ranges checked before HOLD) |
| consumed-TRAIN exclusions | 1.5M TRAIN `0..383` (P20H), `384..767` (P20I), `768..1151` (P20J), `1152..1535` (P20K), remainder `1536..1659` — overlap refuses before any protected content open |
| 1M full pool + reserved 2M | excluded by the cross-file gate (checked FIRST); never touched |
| block count | 3 at N=32768 (same cost class as P18–P20K) |
| tag domains | new P20M domain (§6) |

- Fail-closed gate family (frozen in the runner, order (a)→(g), VAL/HOLD
  before consumed-TRAIN): (a) CROSS-FILE — DEV content-open path +
  stat-size/sha pin must equal the 1.5M identity; any 1M or 2M path or digest
  mismatch refuses before any SC call (frame integers alone are never
  identity); (b) INTRA-FILE VAL/HOLD — DEV ranges must overlap NONE of
  VAL-exterior/HOLD, and must lie wholly inside VAL 1660..2212, else refuse
  before any protected content open; (c) P20H-DEV EXCLUSION — NONE of TRAIN
  0..383; (d) P20I-DEV EXCLUSION — NONE of 384..767; (e) P20J-DEV EXCLUSION —
  NONE of 768..1151; (f) P20K-DEV + REMAINDER EXCLUSION — NONE of 1152..1659
  (includes the DEV∩build-frames disjointness declaration: DEV ⊂ VAL vs build
  ⊂ TRAIN); (g) CORRECTED-PRIOR-IDENTITY + ORDER-FREEZE + BUDGET-LITERAL —
  §3 digest/literal pins must match AND the Stage-A frozen order-file digest
  must match with derivation inputs replaying exactly AND the budget literal
  must recompute from the same-run H, else refuse before any SC call.

## 5. Preregistered disclosure point (normative — session-derived, frozen at Stage A)

- Budget rule (S2-i, literal): `K_total = budget_k_total(32768, H_total, 1.3)`
  `= floor((1.3*32768*H_total-64)/5)` clipped `[0,65536]` (cites:
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_n_scaling.py:421`,
  used by `empirical_genie_scaling`; `FROZEN_TARGET_F = 1.3`). The declaration
  MUST be recomputed from the same run's session H and displayed as a literal
  (`1.3*32768*<H_total>-64 over 5, floored, clipped`); never carried as an
  absolute from another session. X08 descriptive reference: 7020 at
  H_total 0.825566051673296.
- Split rule: `select_empirical_split` semantics (cites:
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_scaling.py:461`) —
  pooled TRAIN mean risks → worst-first `(e,h,index)` L1/L2 orders → exhaustive
  integer K1 enumeration with `K2 = K_total-K1` → lexicographic minimum of
  `(TRAIN residual e sum, K1, K2)`. TRAIN risks = 16 synthetic blocks
  model-sampled from the §3 corrected prior under frozen derivation seeds
  (§6; L1+L2 genie, 32 calls, Stage A only; never a real frame, never DEV).
  `allocate_layer_ks` (`target_n_scaling.py:432`) is the same-family analytic
  (BEC-surrogate) reference and is NOT the selection rule. `(K1,K2)` and the
  worst-first orders freeze at Stage A: values `<FROZEN_AT_STAGE_A>` with freeze
  rule = derive in Stage A, pin integers + order-file digest in
  `P20M_FREEZE.md`, gate on equality thereafter.
- Caps PREREGISTERED per arm at Stage A from the derived point (rule
  `5*(K1+K2)+64` key-dependent bits/block, `10*32768+63 = 327743` public
  bits/tag, one 64-bit tag per record):

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| G0_old_point_base (operational control) | 319 | 6492 | 34119 = 5*6811+64 | 327743 |
| G1_raw_prior_session_budget (operational candidate) | <FROZEN_AT_STAGE_A> | <FROZEN_AT_STAGE_A> | <5*(K1+K2)+64, frozen at Stage A> | 327743 |
| G2_true_l1_diagnostic (oracle) | 0 | <candidate K2> | <5*K2+64, frozen at Stage A> | 327743 |

- Planned totals + ratios-vs-raw displayed at Stage A from the frozen integers
  (far-below-raw bar per strategy; sample-CE-normalized ratios descriptive, NOT
  qualification efficiency).
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate
  BLOCKS. Per-record fields pin the operating point (`prior_source`
  lambda/raw, `k1/k2/k_total`, `budget_literal`, `l1_order_digest`,
  `floor_hit_rate`).

## 6. Arms (frozen; operating-point swap per §§2-3/§5, all else P20H-identical)

- `G0_old_point_base`: frozen greedy SC at the carried-over failing point —
  λ prior (digest `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`)
  + frozen P16 orders, k1=319/k2=6492 (operational control; 2 SC + 1 P20M-domain
  tag per block). Paired same-block control for G1 on the new VAL segment.
- `G1_raw_prior_session_budget`: frozen greedy SC at the corrected point —
  §3 raw prior + Stage-A derived (K1,K2) + Stage-A frozen worst-first orders
  (§9 `raw_prior_orders_1p5m.json`, digest-gated; no reselection, on ANY data)
  (operational; the single-factor candidate; 2 SC + 1 tag per block).
- `G2_true_l1_diagnostic`: true-L1-conditioned diagnostic at the CANDIDATE K2
  (provenance ORACLE, deployable=false, excluded from every operational
  aggregate; never a correction result; 1 SC + 1 P20M-domain tag per block).
- No other arms. Block-major (G0, G1, G2) per DEV block; checkpoint after every
  (arm, block) record; 9 records total. P16 construction file unchanged except
  the Stage-A frozen order file (digest-pinned in the freeze);
  kernel/representation/transform/SC arithmetic unchanged; greedy SC only; no
  SCL/new kernel/model/schema. Derivation genie calls (32 L1+L2) run IN STAGE A
  ONLY; Stage B performs pure DEV scoring (15 SC + 9 tags) with ZERO sampling —
  the Stage-B TRAIN genie call count is pinned at 0.
- Tag domain (new P20M): master 2026092280, prefix
  `nbpolar-p20m-raw-prior-val-1p5m-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from
  ALL of P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K/P20L.
  Stage A verifies by repo grep that master 2026092280, focused-test seeds
  `2026092281..2026092287`, and derivation seeds `2026092291..2026092294`
  appear in no tracked file outside the P20M runner/tests/packet/spec
  documents (planner pre-checked 202609228*/229* absent at freeze time).
- Derivation seeds (frozen): `2026092291..2026092294` (4 streams × 4 blocks =
  16 synthetic TRAIN blocks model-sampled from the §3 corrected prior, L1+L2
  genie, CONSUMED IN STAGE A to produce the frozen orders). Stage A confirms
  exact integers or replaces with a written equivalent + justification +
  re-review; never assumed. Disjoint from every frozen master/stream/tag/test
  seed by the grep rule above. Stage B takes NO derivation seeds and performs
  no sampling.

## 7. Thresholds and labels (descriptive only — P20I-style, chosen over P16-style)

- Outcome label `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE`
  iff ALL integrity gates (§9) hold — regardless of exact-count. Any exact count
  (including 0/9 and partials) is COMPLETE when integrity holds.
- Choice + justification: P20I-style descriptive (no recovery/FER/Wilson
  threshold). This is the FIRST out-of-sample test of the corrected prior at a
  new session-derived operating point — there is no empirical basis for a
  recovery threshold here. A P16-style 62/64-class gate would be an invented
  threshold, explicitly forbidden. Branch decisions belong to main-thread
  planning AFTER acceptance (§16).
- NO recovery / FER / Wilson / superiority / qualification / promotion claim.
  Descriptive reading only: "raw-prior-restoration" = blocks where G0 fails and
  G1 is exact on the new VAL segment (`g1_restored_count`, count + per-block
  endpoint rows); "maintain" = G1 exact where G0 exact. Either (or neither)
  counts as COMPLETE.
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`,
  `undetected` isolated (never success/FER), plus `decode_failed` /
  `nonfinite` / `resource_abort` via the P20A path. P20A four-endpoint
  separation (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` / `pair_exact`)
  per record. First-error coordinate/layer rows are the primary diagnostic
  signal. Per-record floor-hit fields (`floor_hits`, `floor_hit_rate`) complete
  per record (S2 reporting).

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized
  execution; no rerun, no seed change, no prior/budget/order tuning after
  preregistration. Execution-error rerun only as a recorded repeat of the
  identical freeze, never as tuning. P20H/P20I/P20J/P20K spent attempts do NOT
  transfer (independent packet).
- Reads (split-counted): counts-calibration opens 0/0 (no protected NPZ open in
  this packet; §3 derivation reads the worktree npz only) + DEV open 1/1
  reserved for Stage B (parquet, consumed at first DEV content open). HOLD reads
  0/1 untouched. Any reopen, new calibration, real-frame use for derivation, or
  DEV refit is forbidden. Prior-file load and synthetic derivation sampling are
  worktree-file/prior reads, not protected opens.
- SC/tag/genie budget: Stage-A derivation 32 TRAIN genie calls (L1+L2 on 16
  synthetic blocks; frozen order-file product, accounted in the Stage-A freeze)
  + Stage-B pure DEV 15 SC (3 blocks × (2+2+1)) + 9 tags + 9 records with ZERO
  Stage-B sampling (Stage-B TRAIN genie calls pinned at 0); derived
  per-record recomputation must equal counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  accounting; abort is BLOCKED, never success. Wall/RSS ceilings frozen in
  Stage-A freeze (P20-class reference at the identical DEV decoder budget:
  P20J ~107.75 s / ~533 MB; P20K ~107.64 s / ~559 MB; P20M plans the identical
  15-SC / 9-tag DEV budget in Stage B with the 32 light TRAIN genie calls
  accounted in Stage A; external timeout 600 s + virtual/RSS caps 2 GiB +
  single thread frozen).
- Strategy stop rules binding: no tuning on closed blocks or the new VAL DEV
  after the one shot; no reuse of consumed 1M pool (any split/subrange), any
  consumed 1.5M TRAIN DEV, TRAIN remainder 1536..1659, VAL remainder 2044..2212
  beyond counting, HOLD, or reserved 2M; no third factor after inconclusive
  single-factor; no near-raw disclosure claim; no oracle-as-operational; no
  population-reliability inference from this single gate alone; no efficiency
  tuning inside this packet.
- SCL entry gate UNCHANGED (unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B five files)

- Stage-A freeze pins (no protected opens): corrected-prior artifact path +
  canonical digest + H literals + `p_b` cross-check + floor-hit count/rate;
  K_total literal recomputation display + (K1,K2) integers + worst-first orders;
  exact module path + N-flag Stage-B command verbatim + derivation-seed
  integers + population integers + caps + budgets + tag domain + P16
  construction digest + frozen order-file digest; recorded in `P20M_FREEZE.md`.
  Stage-A order-file product identity: path
  `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json`,
  format JSON holding the full L1 + L2 worst-first permutations plus provenance
  (corrected-prior digest + program pin + derivation-seed integers), sha256
  digest of the file bytes pinned in the freeze.
- Stage-B root: `.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/`
  (exactly five files; per-(arm, block) checkpointing; pure DEV scoring —
  zero sampling; one DEV content open; no reopen/rerun).
  Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`
  (P16 construction digest + corrected-prior digest + order-file digest-gate
  proof (file bytes sha256 equals the frozen `--order-digest`) + budget-literal
  display + derivation-seed pins (provenance only, no Stage-B sampling) +
  split manifest + VAL DEV integers + DEV∩build-frames disjointness
  declaration with frame sets), `per_block_arm_outcomes.jsonl` (9 records at
  completion), `aggregate_summary.json`, `report.md`. Per-record §7 endpoints +
  first error coordinate/layer, zero-count hits, floor hits + floor-hit rate +
  log loss, true-H vs candidate-H L2 NLL, taxonomy, G1 operating-point fields
  (`prior_source`, `k1/k2/k_total`, `budget_literal`, `l1_order_digest`).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0);
  derivation-genie call counts + SC counts (L1/L2 split) + tag counts exact;
  block SER/NLL; wall/RSS; `g1_restored_count` descriptive; per-arm floor-hit
  rate reported (S2).
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `corrected_prior_identity` (new-npz
  digest + lambda-0.0/floor pins + exact key set + H literals within 1e-12 +
  `p_b` cross-check); `dev_split_manifest_identity`;
  `dev_block_range_identity` (§4 gate family (a)→(g): cross-file first, then
  intra-file VAL-containment + VAL-exterior/HOLD, then P20H/P20I/P20J/P20K-TRAIN
  + remainder exclusions incl. the DEV∩build-frames disjointness declaration,
  then corrected-prior-identity + order-freeze + budget-literal pins);
  `order_derivation_identity` (program pin + corrected-prior-digest input pin +
  derivation-seed pins + Stage-A order-file digest, Stage-B file-bytes digest
  equality replay-exact, zero Stage-B sampling);
  `budget_literal_recomputed` (S2-i: f=1.3 literal recomputed from the same-run
  session H and displayed, never a carried absolute);
  `target_population_contract` (corrected literals, recomputed H1/H2 within
  1e-12 + column normalization); `dev_population_exact` (384 VAL frames /
  98304 pairs / 256 rows per frame / pair indices / symbol range);
  `blocks_exact_with_declared_remainder` (three exact VAL DEV ranges per arm in
  block-major slot order + never-used VAL remainder 169 frames / 43264 pairs,
  counted from the pool but never decoded); `nine_records_exact`;
  `genie_calls_exact` (Stage-A 32 derivation calls in the freeze + Stage-B 0
  sampling calls); `sc_calls_exact` (derived 15); `tags_exact` (derived 9);
  `orders_valid_k_prefixes_within_registered_arms` (G0 P16 prefixes +
  G1 derived-order prefixes + operating-point triple);
  `floor_hit_rate_reported` (S2: construction floor-hit count/rate + per-arm
  per-record floor-hit fields present); `oracle_isolation`;
  `buckets_disjoint_exhaustive` (unique arm/block + schema); `undetected_zero`;
  `nonfinite_zero`; `truth_isolation`; `disclosure_recount_exact`;
  `one_open_per_protected_input` (counts 0 + DEV 1); `input_stat_unchanged`;
  `no_unregistered_access`; `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (derivation + injected tests + implementation-freeze; authorized
  separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_<raw_prior files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20m/<uuid>/`
  temp root; protected-open audit declared separately (counts 0 + DEV 0 at
  Stage-A close). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A derivation (read-only worktree input, zero protected opens): read
  `counts_ab` from the §3 worktree npz (digest-reverified first) → apply the §3
  raw rule → write `raw_prior_1p5m.npz` + freeze digest/H literals/`p_b`
  cross-check/floor-hit rate → model-sample 16 synthetic TRAIN blocks under the
  frozen derivation seeds → L1+L2 genie risks → pooled means →
  `select_empirical_split` → freeze K_total/(K1,K2)/orders → write
  `raw_prior_orders_1p5m.json` + freeze file digest. Zero DEV contact, zero
  counts opens throughout.
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A
  freeze with all `<FROZEN_AT_STAGE_A>` pins filled; NOT AUTHORIZED until
  independent Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.raw_prior_val_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --source 1p5M --floor 1e-15 --n 32768 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 1660 2043 --block-frames 128 --remainder-frames 2044 2212 --tag-master 2026092280 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m
```
  All flags required, no production default; three hardcoded arms with the
  operating-point swap pinned (never CLI-tunable: G0 = λ-prior/P16-order
  control at 319/6492; G1 = raw-prior/derived-order candidate at derived K);
  Stage-B prior path MUST equal the §3 frozen digest. Stage A confirms the
  module path (thin importer of accepted `l1_order_1p5m` per the §2 delta list
  d1–d7, or freezes a written equivalent with justification) and fills every
  `<FROZEN_AT_STAGE_A>` pin (`--k1/--k2`, `--order-digest`) plus the
  derivation-seed provenance and the `--source` vocabulary (only `1p5M`).
  Forbidden by default: `longrun_*`, `minrerun_*`, `routeA_*`,
  `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git
  show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: corrected-prior artifact `raw_prior_1p5m.npz` (+ digest/H-literal/
  cross-check/floor-rate freeze) + order file `raw_prior_orders_1p5m.json`
  (+ digest freeze) + thin runner + focused injected tests + Stage-A freeze +
  implementation notes (exact files, diffs, test commands/results, frozen
  prior/budget/split/orders/population/cap/command). Protected content opens 0
  at Stage-A close (counts 0 + DEV 0; worktree-npz reads are not protected
  opens; derivation seeds are integers; synthetic derivation consumes only the
  worktree prior arrays).
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md`
  (+ freeze, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`,
  `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec P20M delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20m/spec.md`
  + `tasks.md` P20M section (same umbrella change as
  P18/P19/P20A/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K; no new top-level change).

## 12. Allowed work

- New thin raw-prior runner (importer per §2 d1–d7) + focused injected tests
  (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`
  (gate/population/order-file pattern references; `l1_order_1p5m` additionally
  the import target), P13/P16 machinery (`target_n_scaling.budget_k_total`,
  `empirical_genie_scaling.select_empirical_split`,
  `target_n_scaling.allocate_layer_ks` as same-family reference only)
  (+ `construction.py` / `prior.py` / `sc.py` contracts as called).
- Read-only load of `counts_ab` from the §3 worktree npz (digest-pinned;
  worktree-file read, never a protected counts open) + synthetic TRAIN sampling
  from the derived corrected prior under frozen seeds IN STAGE A ONLY to
  produce the frozen prior artifact + order file (§§3/5/9; zero protected
  reads, zero DEV contact).
- P20M OpenSpec delta + packet docs + Stage-A freeze/return/review files +
  Stage-B evidence root (root only after Stage-B authorization) + the frozen
  `raw_prior_1p5m.npz` + `raw_prior_orders_1p5m.json` (Stage-A products,
  §3/§9 identity).

## 13. Forbidden work

- Any NPZ/parquet content open or stat of 1.5M DEV/VAL/HOLD, any 1M split, or
  reserved 2M in Stage A (Stage-A protected opens 0); any V25 counts-NPZ open,
  any lambda smoothing anywhere, any K carried as an absolute from another
  session (S2-i), any derivation on real DEV/VAL/HOLD/TRAIN-remainder frames at
  any stage; any decoder execution before Pre-EXECUTE PASS + pasted Stage-B
  authorization.
- Any change to GF32/transform/SC arithmetic, floor value, tag scheme
  semantics, outcome precedence, accepted evidence roots, P20H calibration
  product, X08 probe root, or `src/` + `experiments/` + `tools/` frozen
  baseline.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the
  consumed 1M pool (any split/subrange), any consumed 1.5M TRAIN DEV
  (0..1535), TRAIN remainder 1536..1659, VAL remainder 2044..2212, HOLD, or the
  reserved 2M file; no second factor (disclosure tier, order swap on real data,
  alternative construction, bounded search) inside this packet; no efficiency
  tuning; no new-block peeking before the authorized attempt; no calibration
  on DEV/VAL.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push; no self-acceptance; no P20D scope creep; no P20H/P20I/P20J/P20K
  rerun under this packet.

## 14. Acceptance IDs

- `P20M-R1`: corrected prior derived read-only from §3 worktree `counts_ab`
  under the frozen raw rule (no lambda; floor + renorm + `derive_p1`/`derive_p2`
  pins; `p_b` cross-check; zero protected counts opens; V25 NPZ never opened);
  new artifact digest + H literals + floor-hit rate frozen at Stage A.
  Derivation-gate BLOCKED → planner rework, never a Stage-B fallback.
- `P20M-R2`: budget/split/orders frozen session-derived (S2-i literal
  recomputation displayed from same-run H; `select_empirical_split` semantics
  on synthetic session-TRAIN risks under frozen derivation seeds; DEV-zero
  contact; Stage-A order-file digest + Stage-B digest-gate equality, zero
  Stage-B sampling); closed/consumed blocks select nothing; consumed 1M pool
  excluded by source-tagged cross-file gate; all consumed 1.5M TRAIN DEV +
  TRAIN remainder excluded; DEV∩build-frames disjointness declared with frame
  sets (S2-ii); VAL DEV 1660..2043 (3 blocks 1660..1787/1788..1915/1916..2043,
  VAL remainder 2044..2212 never used) gated + Pre-EXECUTE-approved; reserved
  2M untouched (never opened/statted/listed).
- `P20M-R3`: disclosure point preregistered per arm from the derived integers
  (G0 34119 + 327743 public; G1/G2 Stage-A-frozen via the 5K+64 rule),
  ratios-vs-raw shown, recount mismatch 0; CE ratios never called efficiency.
- `P20M-R4`: operating-point swap (G0 control pins + G1 candidate pins +
  order-prefix rule on the derived orders) frozen before execution, unchanged
  after; P16 construction migration pinned; no tag-guided selection, no
  evidence reuse, no post-hoc re-picking, no re-derivation.
- `P20M-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9;
  `undetected` isolated; oracle arm never operational; first-error
  coordinate/layer rows + per-record floor-hit fields complete per record.
- `P20M-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning;
  split-counted reads (counts 0/0 + DEV 1/1 + HOLD 0/1); resource aborts via
  P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20M-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded (Pre-EXECUTE
  explicitly adjudicates §3 derivation + §5 budget literal + §4 gate family +
  §2 runner-delta design); main-thread acceptance owns the label;
  descriptive-only, no FER/qualification/promotion language; branch reading
  (§16) stays planning input, never an in-packet verdict; honest-scope
  statement (§0) repeated verbatim in the return.
- `P20M-R8`: Stage-A suites green on injected data with zero protected opens
  audit (counts 0 + DEV 0 at Stage-A close; 2M non-access); no commit/push;
  frozen dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs
`P20M-R1..R8` (stage-appropriately) complete with changed files + exact
commands/results + artifact inventory (incl. both Stage-A product digests) +
split open audit (counts + DEV + HOLD separately); or (b) a concrete blocker
with failing command, exact error/traceback, attempted remedies, and the ONE
decision needed from the main thread. "Still incomplete" is not a completion
report. The operator never marks its own work accepted and never authorizes
Stage B.

## 16. Deferred options (not in this packet)

- G1-restoration → maintain-confirmation round (deferred): trigger = at least
  one block with G0 fail → G1 exact on the new VAL segment (genuine
  raw-prior-restoration event, not maintain-only). Then a LATER packet may
  preregister a maintain confirmation on further new data (VAL remainder
  2044..2212 recheck first — only 169 frames = one full block + 41-frame stub,
  so a one-block micro-confirmation at most; reserved 2M first-use with
  per-session raw calibration + frozen derived point + new tags is the
  candidate confirmation population but NOT pre-authorized here). This packet
  performs no follow-up confirmation and licenses no reliability claim.
- G1-zero-restoration all-L1 → next upstream single factor (deferred):
  trigger = genuine prior-budget-negative under the corrected prior + frozen
  session-derived point — G0 failures occur on new-segment VAL blocks but G1
  restores NONE with operational first errors remaining L1-layer. Only THEN is
  the prior+budget operating point falsified as the fix, and only then does
  exactly ONE of (order-positions under the raw prior / L1-side bounded search
  at the raw-prior point) become the next single factor on further new data by
  main-thread planning. Nothing is auto-triggered inside this packet; P20D
  stays deferred (semantic offset, frozen since P20H).
- L2-implication → P20D candidate (deferred): trigger = EITHER new-point oracle
  non-exact (G2 fails at candidate K2 — true-L1-conditioned L2 insufficiency at
  the corrected point, the first genuine L2-construction evidence on 1.5M) OR
  bottleneck-layer move (operational first errors become L2-layer under G1).
  Until such L2-side evidence exists, P20D stays deferred.
- Maintain-only (G0 exact somewhere and G1 exact wherever G0 exact, zero
  fail→exact events) → further planning (deferred): neither restoration nor
  negative; main thread re-evaluates with the full chain evidence in hand.
  This packet prejudges none of them.
- Disclosure-minimality probe, efficiency optimization, second independent
  session on reserved 2M, closure of the 1M-HOLD thread: ALL continue deferred
  / out of scope, re-evaluated against P20M accepted evidence after acceptance.
- 2M stays PRISTINE under this packet — never opened, never statted, never
  listed — as the follow-up confirmation population. Any 2M packet needs its
  own freeze, tag domain, and reviews.
