# TASK_PACKET.md — NBPOLAR-X17-METRIC-FEED-AUDIT (frozen Tier-X probe, proposal only)

Probe: `NBPOLAR-X17-METRIC-FEED-AUDIT` | Tier: X (non-claim, synthetic-only, decoder-free except the frozen greedy-SC mismatch oracle)
Workdir: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` | Branch: `codex/nbpolar-phase0`
Authorizing record: X16 `TASK_PACKET.md` §5 branch rule (G1-high WITH G2-pass ⇒ SC-path disease ⇒ metric-feed audit next, NOT closeout) + `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md` §4 D3.
Cost class: zero-cost synthetic diagnostic. Consumes NO counts/DEV/HOLD/VAL reads and NO attempt.
Status: PROPOSAL — awaiting main-thread approval + freeze.
No partial X17 dir exists (planner grep `nbpolar_x17|X17` clean 2026-09-20; `2026092390..2399` clean; probe-root listing confirms absence); this packet creates rather than completes.

## 0. Trigger (frozen inputs, not re-argued)

X16 decisive result (`workspace/probes/nbpolar_x16_synthetic_scale_disclosure/results.json`, status `X16_STOP_SANITY_G1_HIGH`):
pooled greedy-SC mismatch 0.76902 ≈ derived no-information ceiling 0.76931; undisclosed-region
mismatch 0.96838 ≈ chance 0.96875. Meanwhile G2 0.99919 PASS, argmax-L1 hit 0.944, Q1b non-spike
L8 ≈ 0.999. Tables highly informative; SC path at chance. Per X16 §5: G1-high WITH G2-pass ⇒
SC-path disease ⇒ this audit, NOT closeout.

## 1. Read-only inventory (planner read-verified, no execution; accepted modules read-only)

### 1a. SC recursion — what it consumes

| Path:line | Signature / contract |
|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py:216` | `sc_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None) -> SCResult` |
| `sc.py:7-12` | Input contract: `logp_x[j,a]` is **ln P(X_j = a \| Bob/context)**, shape `(N,q)`, symbol axis last, natural order; rows normalized to logsumexp 0; exact-zero (`-inf`) preserved |
| `sc.py:219-223` | `known_positions`/`known_values` map **U coordinates → disclosed GF symbols** (zero is a value); input order irrelevant; undisclosed decided by argmax, ties to smallest index |
| `sc.py:234-259` | Recursion splits contiguous halves in **natural order** (`_minus_block` left, `_plus_block` with `beta = polar_transform(u_hat[left])`); no bit-reversal anywhere |
| `sc.py:54-65` | `SCResult`: `u_hat` (U-domain, natural order), `x_hat = polar_transform(u_hat)`, `decision_metrics`, `known_count`, `known_mask` |
| `sc.py:166-173` | `_combination_index`: `index[u,v] = u + alpha*v` via field ops |

### 1b. Prior — how L1/L2 metrics are built, what conditioning they assume

| Path:line | Signature / semantics |
|---|---|
| `prior.py:162-165` | `derive_p1(f) -> [U1,B] (32,1024)` — marginal over U2 |
| `prior.py:168-179` | `derive_p2(f) -> [U1,B,U2] (32,1024,32)` — conditional on U1; zero-mass slices → uniform |
| `prior.py:213-219` | `build_p1_metrics(bob, p1_table)` — per-position rows `p1[:,b_j]`; takes **no Alice input** |
| `prior.py:222-235` | `gather_p2_metrics(bob, u1, p2_table)` — rows `p2[u1_j,b_j,:]` for hard-u1 estimates; takes **no Alice truth** (caller injects) |
| `prior.py:288-325` | `probs_to_symbol_metric(probs, *, conditioning=FULL_BOB_ONLY, provenance=...)` — `np.log` (**natural**, matches SC ln contract), rows to logsumexp 0, identity `symbol_order` asserted |

### 1c. Transform / algebra — ordering and field

| Path:line | Signature / semantics |
|---|---|
| `transform.py:34-50` | `polar_transform(symbols, *, field, alpha=2)` — `G_N = F_alpha^{⊗n}`, **natural coordinate order: no bit reversal**; kernel `x0 = u0 + alpha*u1, x1 = u1`; caller's input never mutated |
| `transform.py:3-10` | In characteristic two the kernel is its own inverse ⇒ transform is an **involution**: `G(G(x)) = x` |
| `transform.py:108-120` | `transform_and_select(symbols, coordinates, ...)` — `u = transform(a)`, selected values in caller order |
| `algebra.py:40-42` | `make_gf32()` — frozen MVP field GF32 poly 37; `validate_symbols` (line 45) enforces int vector in `0..q-1` |

### 1d. Truth source vs production runner — the suspect divergence

| Path:line | What it says |
|---|---|
| `empirical_channel.py:294-327` | `sample_full_block(rng, p_b, f_full, q_high, q_low, n) -> (bob, a_full, high, low)` with `low = a_full % 32`, `high = a_full // 32` — **X-domain** per-coordinate label components (docstring: truth goes "only to frozen disclosure maps and scoring") |
| `two_layer.py:629-630` (production, correct) | `u1_true = polar_transform(high_arr)`; `u2_true = polar_transform(low_arr)` — truth moved to **U-domain** before disclosure/scoring |
| `two_layer.py:633-634` | Disclosures `u1_true[pos1]`, `u2_true[pos2]` — U values into U coordinates ✓ |
| `two_layer.py:666,675-678` | L2 metric from X-domain `op_high_hat = sc1.x_hat`; decode; `x_hat` scored vs X truth ✓ |
| X16 `body.py:420-421` (**SUSPECT**) | `bob, _, u1_true, u2_true = sample_full_block(...)` — raw X-domain `high/low` **misnamed**, `polar_transform` never applied to truth (transform imported line 83-89 but used only for the re-encode self-check line 461-464) |
| X16 `body.py:448-449` (**SUSPECT**) | `known_values = u2_true[:6746]` — **X-domain values forced into U coordinates** |
| X16 `body.py:465` (**SUSPECT**) | `mismatch = res.u_hat != u2_true` — **U-domain output scored against X-domain truth** |
| X16 `body.py:466-471` (void check) | Disclosed-mismatch assert passes **trivially by forcing** (forced positions equal by construction) — catches nothing about domain |

Primary hypothesis H-a: X14/X15/X16 chance-level SC mismatch is (at least dominantly) this probe-side
U/X domain confusion, NOT a channel or decoder property. It predicts the exact observed pattern:
decoder-free per-position ranking (G2, always X-domain-consistent) informative; any U-vs-X comparison
at chance. Production runner is unaffected (transforms correctly); remediation, if confirmed, is a
probe-body correction decided by the main thread — never an in-probe fix, never a production change.

## 2. Frozen definitions (X14 §2 / X15 §2 / X16 §2 reused VERBATIM where applicable)

Hazard atom, spike definition + strata (`[2,4)/[4,8)/[8,∞)` + `nonspike_ref`, margin 2.0 bits),
per-position ranking + survival (`L ∈ {4,8}`, sc.py tie convention), Q1b, F-median8 detector
(`R=8`, top-K selection, coverage) — all byte-identical to X16 §2.
**Superseded:** X16 §3 G1 (`mismatch < 0.75` stop) is **retired** — mismatch is now the measured
audit variable; stopping on it would prejudge the audit. G2 (Q1b-nonspike-L8 ≥ 0.50) and G3
(spike fraction ∈ [0.02,0.70]) are **retained** as structural wiring checks (identical decoder-free
machinery + identical channel family ⇒ same expectations). New stops: structural only (§6).

## 3. Audit arms (all synthetic-only; accepted modules read-only; SCL stays locked)

Small-N audit scale N=256 (X15 operating point; SC calls are ms) × 4 blocks (seeds `2026092391..2394`),
channel = X15 0.75-diagonal recipe verbatim; plus ONE N=32768 confirmation arm (X16 recipe, 1 block,
seed `2026092399`) with corrected truth-side. Per-arm decoder use: frozen greedy `sc_decode` (L=1)
only, same call shape as X16. Arms (each isolates one candidate defect):

- **A0 baseline replay** — X16 recipe verbatim at N=256 (X-domain known_values + U-vs-X scoring).
  Prediction: reproduces chance-level mismatch ≈ 0.96875 (undisclosed). Anchors the bug.
- **A1 rescore-only** — same decode as A0, but additionally score `u_hat` vs `u_true = polar_transform(low)`
  and `x_hat` vs `low`. No new decode. Discriminates H-a scoring half: if decoder works,
  `x_hat`-vs-`low` drops far below chance while `u_hat`-vs-`low` stays at chance.
- **A2 corrected feed** — `known_values = u_true[:K2]` (U-domain), score vs `u_true`. Discriminates H-a
  disclosure half. Prediction under H-a: mismatch far below chance (channel diag 0.75, pointwise
  L2 hit 0.75 ⇒ predicted descriptive band [0.05, 0.45] at N=256; recorded, never gated).
- **A3 oracle-u1** — A2 + true-`high` conditioning everywhere (vs D1 argmax). Quantifies the
  conditioning penalty (defect b). Prediction: gap vs A2 small (argmax-L1 hit 0.944 recorded).
- **A4 order controls** — (i) shuffled `known_positions` input order ⇒ `u_hat` bit-identical
  (sc.py order-irrelevance assert); (ii) bit-reversed metric rows ⇒ mismatch returns to chance
  (proves natural order is the live assumption); (iii) random-K disclosed set ≡ first-K set
  (iid positions; documents equivalence). Discriminates defects (a)-index-order and (e)-set.
- **A5 log-domain controls** — `SymbolMetric` asserts (logsumexp-0, identity order) pass;
  uniform-metric control ⇒ mismatch ≈ chance; sign-flipped-logp control ⇒ mismatch at/above chance.
  Discriminates defect (d). Prediction: current sign correct (A2 decodes, flipped does not).
- **P positive control (REQUIRED)** — near-noiseless channel (diagonal pin 0.999, neighbors share
  0.0009, rest 0.0001; recipe shape otherwise X15-verbatim), N=256, corrected U-truth feed + scoring,
  4 blocks (seeds `2026092395..2398`). **Preregistered expected mismatch band: [0.00, 0.05]**
  (descriptive prediction, NOT a gateverdict — no PASS/FAIL token whatever the numbers say).
  If P measures ≈ chance ⇒ defect is in the decoder/feed itself, not the channel and not scoring
  (localizes to `sc.py` feed path; production impact assessed by main thread). If P decodes ⇒
  metric-domain feed (defect f / X14-review rival) is vindicated end-to-end and closed.
- **P2 wiring assert** — all-known decode returns truth exactly (X16 self-test (iii) kept).
- **C full-scale confirmation** — X16 recipe at N=32768 with corrected truth-side (A2+A3, 1 block,
  seed `2026092399`; 2 SC ≈ 15 s). Decides whether H-a explains X16 quantitatively at exact scale.

Defect → measurement map: (a) index-order → A4ii; (b) U1-conditioning → A3−A2 gap; (c) domain
(X-metric as U) → P decodes + A1/A2 pattern (feed vindicated, truth-side was wrong); (d) log/sign →
A5; (e) disclosure set/order → A4i/A4iii. H-a (probe U/X truth confusion) → A0 vs A1/A2 split.

## 4. Post-result branch (for the main thread after X17 returns)

- **Defect-localized** (A1/A2 pattern explains chance + P decodes + C confirms at scale) → main-thread
  **remediation decision** (probe-body truth-side correction + re-run of the survival question;
  production modules untouched — inventory shows the runner transforms correctly). Possibly a
  P16-scale change ONLY if main-thread review finds production impact; never decided in-probe.
- **No defect found** (P decodes AND corrected full-scale C still at chance) → declare the synthetic
  line **non-informative for the SCL question** (four-probe negative-capability record:
  X14/X15/X16 + X17 audit) and redirect the SCL question to a later gated effort. Either outcome
  consumes no attempt and moves no scientific status.

## 5. Goal / Non-Goals / Impact Scope / Acceptance Criteria / Tasks

- **Goal:** Preregistered, synthetic-only, decoder-free-except-oracle wiring audit that localizes the
  X16 SC-path disease to one of the §3 candidate defects via discriminating measurements + a
  positive control with a preregistered expected band — the exact evidence the X16 §5 branch needs.
- **Non-goals (binding):** No FER/reliability/efficiency verdicts; no thresholds, no pass/fail; no SCL
  implementation or unlock; no protected opens (pairs/V25/parquet/1M/1.5M/2M content, `raw_prior_*.npz`);
  no real-data decoder run; no tag-domain use (`tag_calls: 0`); **no edits to accepted modules**
  (`sc.py`, `prior.py`, `transform.py`, `algebra.py`, `empirical_channel.py`, `two_layer.py` read-only);
  **no in-probe fix** even if H-a confirmed (remediation is a separate main-thread decision); no
  production-run or real-data conclusion; no ledger/memory/index updates per-probe (milestone-batched).
- **Impact scope:** Three new packet docs (this dir) + three new probe-root files
  (`workspace/probes/nbpolar_x17_metric_feed_audit/{prereg.md,body.py,results.json}`). No files
  outside these six are created or modified. `results/`, `comparison_bench/outputs_comparison/`,
  ledgers, sibling checkouts untouched.
- **Acceptance criteria:** (i) three packet docs + frozen 3-line prereg consistent; (ii) fresh seeds
  `2026092390..2399` + root name proven absent by repo grep at freeze (planner pre-grep clean
  2026-09-20); (iii) focused tests + full NB-Polar suite green (T0/T1; T2 not required for Tier-X);
  (iv) single execution under the frozen command writes only `results.json`, scalar-only, < 2 MB,
  per-seed values + mean/sample-std(n−1)/range, zero protected opens; (v) G2/G3 wiring checks
  evaluated with `X17_STOP_*` on violation; per-arm predictions recorded descriptively, never as
  verdict tokens; (vi) focused numerical review recorded; (vii) no claim, threshold, candidate or
  accepted token anywhere in outputs.
- **Tasks (coder, after freeze authorization):**
  1. Freeze: repo-grep seeds `2026092390..2399` + `nbpolar_x17_metric_feed_audit` absent; write
     `prereg.md` (verbatim `PREREG_DRAFT.md`) BEFORE any generation; embed §2 + §3 recipes as frozen
     `body.py` (stdlib+numpy; read-only imports: `empirical_channel` sampling, `prior`,
     `algebra.make_gf32`, `transform.polar_transform`, `sc.sc_decode`; no list decoder; path-refusal
     asserts); self-tests: rank tie-break (X14-identical), diagonal-smoke, all-known-exact (P2),
     order-shuffle-identity (A4i), prereg-token + gate asserts. Verify: grep clean, tests green.
  2. Execute once under the frozen command (`PREREG_DRAFT.md` line 3); execution-error only ⇒ one
     recorded rerun. Verify: exit 0, `results.json` sole write, scalar-only < 2 MB, per-seed + pooled
     stats + per-arm (A0/A1/A2/A3/A4/A5/P/C) measurements present.
  3. Return deltas only: per-arm mismatch values vs predictions, A3−A2 gap, A4 identities, A5
     controls, P band measurement, C confirmation, G2/G3 values, calibration scalars, command/wall,
     blocker-or-none. Obtain focused numerical review. No commit/push; no claims.

## 6. Tier compliance adjudication

- Synthetic-only truth injection with corrected-domain conditioning is Tier-X compliant — same class
  as X16 D1/D2 (synthetic truth conditioning a synthetic SC run); no artifact or real-data access.
- Replaying published 2M K literals + X15 channel scalars as parameters is Tier-X compliant (no content opens).
- Preregistered expected bands (§3 A2/P) are descriptive predictions, not thresholds/verdicts: no
  `X17_PASS/FAIL` token is emitted on any measurement; stops are structural only (protected-path
  import/open; nonfinite; `ImpossibleDisclosedValueError` → `X17_STOP_IMPOSSIBLE`; missing seed-grep
  proof; `results.json` > 2 MB; body/prereg token mismatch; G2/G3 violation → `X17_STOP_SANITY_*`,
  no input repair). SCL stays locked; no scientific-status change. Evidence-size rule: scalar-only,
  estimated < 100 KB.

## 7. Label note (single decision needed, not a blocker)

No X17 label exists anywhere in repo or probe roots (planner grep clean, §0 header). Label
`NBPOLAR-X17-METRIC-FEED-AUDIT` / root `nbpolar_x17_metric_feed_audit/` collides with nothing.
**ONE decision needed from the main thread at approval:** approve the X17-audit design as frozen
(RECOMMENDED — X16 §5 mandates exactly this audit on the G1-high/G2-pass branch, and §1 shows the
prime suspect with exact line numbers), or redirect now (only if the main thread judges the wiring
question moot, which would contradict its own §5 branch rule).
