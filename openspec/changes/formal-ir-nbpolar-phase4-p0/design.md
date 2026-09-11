# Design: Phase 4-P0 Model-F → GF32 prior-contract freeze

Frozen boundary between accepted Model-F statistics and the Phase 1–3 q-ary
Polar stack. Every mistake class below must be detectable before any q-ary
SC call. All line citations are to this worktree's `comparison_bench/`
carried history unless noted.

## 1. Accepted smoothing formula (P0-1)

Accepted per-Bob-column concentration (TASK_PACKET.md:40-44):

```text
p_global[a] = sum_b counts[a,b] / sum_{a,b} counts[a,b]
n_b[b]      = sum_a counts[a,b]
f[a,b]      = (counts[a,b] + lambda * p_global[a]) / (n_b[b] + lambda)
```

Reference implementation: `formal_ir/v72p2d4r2_cal_gf32_model_rate_audit.py`
`build_f` (:329-375; estimator doc :330-336; formula :345-349; column check
within `NORM_TOL=1e-12` :350-352). Column meaning: `P(A|B)` with shape
`(1024,1024)` indexed `[Alice,Bob]`, columns (axis 0) sum to 1.
Unseen Bob column (`n_b=0`) falls back to `p_global` exactly (limit of the
formula). Canonical counter: `build_canonical_counts` (:246-261):
`counts[a,b]=count(Alice=a,Bob=b)`, axis 0 Alice, axis 1 Bob.
CAL input path reuses it: `formal_ir/v72p2d5_model_f_input.py`
`build_model_f_input` (:78-125; reuse :100; `bob_counts=counts.sum(axis=0)`
:108; `p_b=bob/262144` :111; full-CAL shape/sum guards :102-107).
Accepted D5 backoff twin: `formal_ir/v72p2d5_gf32_rate_mother.py`
`build_f_model_concentration` (:274-305; formula :299-301; column assert
1e-12 :302-304) via `prepare_model_f_prior_candidate` (:2361-2388).
D7-C accepted this estimator (`prepare_model_f_prior_candidate` /
`build_f_model_concentration`, `LAMBDA_STAR=137.3823795883264`) per
`docs/decision-log.md:3506`; production LDPC phases historically keep the
rejected twin (see §2).

Chain split of the accepted joint (same two files): D4R2 `build_f` returns
`P_A_given_B (1024,1024) [A,B]`, `P_U1_given_B (1024,32) [B,U1]` rows sum to
1, `P_U2_given_U1_B (32,1024,32) [U1,B,U2]` last axis sums to 1 (:353-375;
zero-mass U1 slice → uniform 1/32). D5 `marginalize_f_to_p1` (:308-320)
returns `[U1,B] (32,n_b)` columns sum to 1 — the transpose of D4R2's P1
layout; `conditionalize_f_to_p2` (:323-342) returns `[U1,B,U2]` — the same
layout as D4R2's P2. The adapter boundary must transpose explicitly; names
alone (`P1`, `high`, `U1`) never imply orientation.

## 2. Banned competitors (P0-1)

- **Banned for all new NB-Polar evidence**:
  `formal_ir/v72p2d5_gf32_rate_mother.py` `build_f_model` (:246-271;
  `sm = counts + lam` :265, per-cell pseudocount) and its sole production
  source `prepare_model_f_prior` (:2330-2358; calls `build_f_model` :2345).
  Defect tag: `LAMBDA_APPLICATION_CONTRACT_DEFECT` (decision-log:3506).
  Historical LDPC production keeps calling it; NB-Polar P1 must never
  import it — the P1 packet allow-lists only the §1 callables.
- **Rejected by scope (synthetic-only, transposed layout)**:
  `formal_ir/v72p2d3_gf32_contrast.py` `_smooth_counts` (:460-482),
  `build_stage1_P` (:485-504; "Synthetic-only … production SHALL use
  `get_l1_prior_production`" :492), `build_stage2_P` (:507-550; "production
  L2 prior is q@P" :515). Layout is `[Bob,U1]` / `[U1,Bob,U2]`, transposed
  vs the canonical `[Alice,Bob]` store (`R5_CANONICAL_COUNTS_SHAPE`,
  :97-102). Not a formula twin: `_smooth_counts` also uses
  `lam*p_global`, but its scope and layout disqualify it.
- **Excluded from the first SC path (historical consumers, reference only)**:
  `app_fed_l2_prior` (D5 :353-375, production `q@P` with `DECODER_FLOOR`),
  the V50–V55 `get_l1_app_prior_l2` family (cross-layer APP, fail-closed
  behind `require_check_updated_provenance`, `v35_algorithm_development.py`
  :540-551), and any `final_beliefs`-fed prior. ROADMAP Phase 4 keeps
  `app_fed_l2_prior` out of the first SC path; ARCHITECTURE forbids feeding
  SC scores into the old `q @ P` bridge.

## 3. Symbol contract (P0-2)

10-bit physical label `s ∈ 0..1023` splits by integer bit ops only:

```text
low  = s & 31          (bits 0..4)  = U2
high = (s >> 5) & 31   (bits 5..9)  = U1
s    = low + 32*high   = U2 + 32*U1   (D5 form: A = 32*U1 + U2)
```

Bit 0 is LSB. Three independent spellings agree:
D4R2 `symbols_to_layers` (:236-243), D3 `split_symbol`/`combine_symbol`/
`symbols_to_layers` (:377-411, mapping frozen :1-10), D5 `symbols_to_layers`
/`layers_to_symbols` (:400-416, `A=32*U1+U2`). D3's header binds the
direction to V35 `factorize_f03` (`v35_algorithm_development.py:421-429`:
`x1=(a>>5)&31`, `x2=a&31`; `u1=high/MSB`, `u2=low/LSB`).
High/low composition is integer-label packing, **not** GF(1024) field
multiplication (TASK_PACKET:54-56; `docs/nbpolar/README.md:23-34`;
ARCHITECTURE field contract). Valid ranges: `s∈0..1023`, `low/high/U1/U2`
∈ `0..31`; batch axes are caller-owned vectors (CAL length 262144;
Polar block `N=2**n`).

Decoder-facing tensors in natural-U order (conditioning is on the **joint**
10-bit Bob symbol; `B_high`/`B_low` are derived views of the same index,
never an independent factorization):

```text
P1[frame,i,a]     = P(A_high=a | B_full, ctx=RESERVED),      shape (F,N,32)
P2_true[frame,i,a]= P(A_low=a | A_high_true, B_full, ctx),   oracle only
P2_hat[frame,i,a] = P(A_low=a | A_high_hat_hard, B_full, ctx), executable
```

`B_full ∈ 0..1023` is the joint Bob label. No per-symbol context variable
exists in Model-F evidence; source/delay/session (`20260123_1M_600k_0dB`,
1M) are acquisition selectors frozen at CAL time, not side info. The
adapter carries `conditioning=FULL_BOB_ONLY`; any future context needs a
new freeze — a Bob component is never silently dropped.
Support: unseen-B column → `p_global`; zero-mass `(U1,B)` slice → uniform
1/32; exact-zero stays `-inf` in log domain unless the frozen formula made
it positive (gates V-P0-02/05).

## 4. SymbolMetric API (P0-3)

Smallest immutable value object for `sc_decode` (accepted consumer:
`formal_ir/nbpolar/sc.py:188-257`; input contract :7-12; row validation +
`logsumexp==0` normalization :88-121; provenance record :237-247):

```text
SymbolMetric(
    logp: float64[N,q],            # ln P, symbol axis last, rows logsumexp 0
    conditioning: Conditioning,    # FULL_BOB_ONLY (MVP frozen)
    provenance: PRIOR_ONLY | ORACLE_CONDITIONED | CANDIDATE_CONDITIONED,
    symbol_order: 0..q-1,          # identity tuple, length q
    normalization: LOGSUMEXP_ZERO,
)
```

Construction/validation helpers are separate from the object:
`smooth_joint_to_conditional` (§1 formula), `derive_p1`, `derive_p2`,
`build_p1_metrics` / `gather_p2_metrics` (pure table → `(F,N,32)` prob
gather), `probs_to_symbol_metric` (`p=0 → -inf`, `p>0 → ln p`, then
row-normalize; row sums and `-inf` preservation asserted), and
`apply_explicit_floor` (opt-in only, caller-recorded reason).
Floor decision: **forbidden by default** inside probability construction;
the log stage preserves `-inf` (matches `sc.py` exact-zero semantics);
DEV may select one bounded floor value only if preregistered, frozen
before EVAL; EVAL cannot change it. No q-ary SC metric is ever labelled a
complete APP (ARCHITECTURE prior contract; `sc.py` row role:
`P(U_i|U_<i,B/context)`, suffix marginalized).

## 5. Evidence lifecycle (P0-4)

- **CAL** (frozen, not consumed by P0): session `20260123_1M_600k_0dB`,
  source 1M, frames 702..1725, 1024×256 = 262144 symbols
  (`v72p2d5_model_f_input.py:33-51`; schema guards :94-125). CAL alone
  fits counts/`lambda` and freezes the adapter.
- **DEV** (reserved label `DEV-FUTURE-DISJOINT`, concrete IDs frozen at P1
  authorization before any load): disjoint frame set, same session
  preferred. May select the single bounded floor and diagnose candidate-L2
  only if preregistered.
- **EVAL** (reserved label `EVAL-SINGLE-USE-DISJOINT`, IDs frozen at P1):
  single use, tunes nothing.
- Banned for construction/smoothing/floor/thresholds: `VAL1726-1729`
  (D3 `VAL_FRAMES`, :71 — non-fresh descriptive range) and any EVAL/held-out
  sample. Precedent pattern: Phase 3-R1 stream separation (unit/TRAIN/DEV/
  EVAL `2026091210-1213`, banned predecessors `2026091200-1203`,
  `formal_ir/nbpolar/eval_r1.py:35-41`; freeze-before-run
  `.workbuddy/queue/NBPOLAR-PHASE3-R1-CONSTRUCTION-RECOVERY/EVAL_FREEZE_R1.md`).

Three kept-separate diagnostics with paired block identities (same frame
set, position order, disclosure rule across all three):
**D1** L1-exact using P1; **D2** L2-oracle using P2_true (upper-bound
mechanism diagnostic, cf. D5 `oracle_l2_prior` :378-397 and D7-C four-
condition design `v72p2d7_gf32_bidirectional_oracle.py:1-22` — oracle
conditions are counterfactual diagnostics, never protocol recovery);
**D3** L2-candidate using P2_hat with **hard** conditioning (single U1
value per position; sufficient for the first test — soft `q@P` weighting
is deferred because it reopens the APP-provenance question D7 closed).
Failure precedence: metric-contract → field/shape → known-coordinate →
impossible-disclosed (failed decode incl. in denominator, own class, per
R1-D2 `construction.py:335-359` `failure_summary`) → numeric-nonfinite
(hard) → SC-exact mismatch. Truth enters only D2 and scoring; P1 and
candidate-L2 builders take no Alice input, and the oracle gather helper
lives in the P1 **test file only** (never exported from `nbpolar/`),
so ordinary decoder calls cannot import it. Belief labels follow D7:
`PRIOR_ONLY_CURRENT_BELIEF`, never `posterior`/`APP`
(`v72p2d7_gf32_bidirectional_oracle.py:119-121`;
`v72p2d7_gf32_schedule_discriminator.py:114-116`); D7-C consumed no
cross-layer returned beliefs (decision-log:3512-3516).

## 6. Alternatives (bounded, one MVP)

1. **A — direct dense `(N,32)` log-metric materialization** (SELECTED for
   the reference decoder): the exact frozen tensor is asserted elementwise
   against the independent formula oracle (≤1e-12); truth isolation is
   structural (§5); memory at N=256 is trivial (~65 KiB/frame float64,
   ~20 MiB/300 frames); axis sentinel applies directly.
2. **B — conditional-table object plus per-frame gather** (DEFERRED):
   same math, less memory at large F; add only when `F×N×32` exceeds the
   V-P0-12 budget. Must preserve the dense-tensor equivalence test.
3. **C — lazy callback/view evaluated by SC** (DEFERRED): avoids
   materialization but hides conditioning provenance in a closure and
   complicates the truth-leak audit; revisit only on measured need.

Decisions: floor forbidden-by-default / DEV-selectable single value (§4);
P1 conditions on joint full-Bob (§3); candidate-L2 hard conditioning
suffices first (§5).

## 7. Handoff shape (P0-6, frozen names)

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py` —
  pure count/probability/log-metric adapters, NumPy + stdlib only
  (+ `validate_symbols`-style range checks); 3-line local bit packing
  citing §3 (no historical-LDPC import coupling).
- `comparison_bench/tests/test_nbpolar_prior.py` — one focused file,
  synthetic fixtures + independent literal-formula oracle (D7-A pattern:
  `v72p2d7_gf32_decoder_certification.py:27-52`, shared constants only
  `Q=32`/`poly 37`) before any CAL artifact.
- No benchmark method, protocol wrapper, or result-root writer.
- Error prefixes: `axis contract:` / `smoothing contract:` /
  `metric contract:` / `provenance contract:` / `lifecycle contract:`.
  Frozen fallbacks only: unseen-B → `p_global`, zero-slice → uniform.
- `nbpolar/__init__.py` exports add: `SymbolMetric`, `Conditioning`,
  `Provenance`, and the six pure functions; the oracle gather helper is
  NOT exported (test-local, §5).
- No generic channel framework, config system, cache, manifest, checksum,
  or compat shim (AGENTS.md §5.7).
