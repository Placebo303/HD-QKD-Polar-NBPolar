# TASK_PACKET.md — NBPOLAR-X16-SYNTHETIC-SCALE-DISCLOSURE (frozen Tier-X probe, proposal only)

Probe: `NBPOLAR-X16-SYNTHETIC-SCALE-DISCLOSURE` | Tier: X (non-claim, synthetic-only, decoder-free except the frozen Q2 mismatch oracle)
Workdir: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` | Branch: `codex/nbpolar-phase0`
Authorizing record: `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md` §4 D3 (proposal only —
NO implementation, NO execution, NO protected opens, NO decoder beyond the frozen greedy-SC
mismatch oracle in Q2, NO list decoder).
Cost class: zero-cost synthetic diagnostic. Consumes NO counts/DEV/HOLD/VAL reads and NO attempt.
Status: PROPOSAL — awaiting main-thread approval + freeze.

## 0. Read-only inventory (verified by planner grep/read, no execution)

### 0a. Real disclosure structure (the operating point to restore)

| Path | What it provides | Status |
|---|---|---|
| `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/P20O_FREEZE.md:74-75` | 2M-session frozen literals `(K_total,K1,K2) = (7080,334,6746)` | Present; ratio source (never recomputed, never recarried) |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/P20O_FREEZE.md:143-151` | Per-arm caps `5*(K1+K2)+64 = 35464` (A/B), `5*K2+64 = 33794` (C/D oracle) | Present; disclosure-size semantics |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/P20S_FREEZE.md:32-54` | P20S replay: `K1 334 / K2 6746 / K_total 7080`; arms disclose first-K1 / first-K2 prefixes of frozen worst-first orders | Present; structural reference |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/OPERATOR_RETURN.md:181-183` | Stage-B cost: 5 SC, wall **35.131961 s** ⇒ **≈ 7.0 s/SC at N=32768** (single-thread pins) | Present; runtime anchor for §3 N-justification |
| `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/per_block_arm_outcomes.jsonl:1` | Observed RSS HWM ≈ 539 MB for a full N=32768 IR record | Present; memory anchor for §3 |

Derived ratios (arithmetic only, no new tuning): `K1/N = 334/32768 ≈ 1.019%`;
`K2/N = 6746/32768 ≈ 20.587%`; `K_total/N ≈ 21.606%`. The 1.5M triple
`(7020,331,6689)` never enters 2M work (S2-i); X16 uses the 2M values.

### 0b. Synthetic scale precedent (why N=256, and why it is suspect)

| Path | What it provides | Status |
|---|---|---|
| `.workbuddy/queue/NBPOLAR-X06-EMPIRICAL-CONSTRUCTION-ORDER-PROBE/TASK_PACKET.md:31` | `N=256` as the cheap small-scale convention (X06 ran 256 blocks × 3 TRAIN streams + 128 × 5 DEV — seconds-scale) | Present; N=256 entered as a cost convention, never as a polarization claim |
| `workspace/probes/nbpolar_x14_scl_list_survival/results.json:6-15` | X14 froze `N=256, K2_synth=52` (= `floor(6689/32768×256)`, the *1.5M*-ratio pin), `K1_synth = 0` (no L1 disclosure anywhere in the packet) | Present; X15 kept N=256/K2=52 identically |
| `.workbuddy/queue/NBPOLAR-X15-STRUCTURED-CHANNEL-LIST-SURVIVAL/TASK_PACKET.md:99` | `prefix first 52 (K2_synth = 52)`; §4: prefix supplies order only | Present; confirms no disclosed-position conditioning in X15 either |

So both failed probes ran at 8 polarization levels with **zero** `known_positions`
passed to the SC path: the K2 prefix supplied only `pm` and the Q2 `K`.

### 0c. The SC/metric path natively supports disclosed-position conditioning at any scale

| Path | What it provides | Status |
|---|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py:216-264` | `sc_decode(..., known_positions, known_values)`: disclosed U coordinates hold actual GF symbols (zero is a value); undisclosed decided by argmax-ties-to-smallest; exact-zero-support disclosure raises `ImpossibleDisclosedValueError`; N any power of two (scale-agnostic) | Present; reuse read-only — X16 passes real-ratio disclosure here |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py:222-235` | `gather_p2_metrics(bob, u1, p2_table)`: takes hard-u1 estimates per position — accepts true-u1 injection at disclosed L1 positions without signature change | Present; reuse read-only |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py:162-179` | `derive_p1` → `[U1,B]` (32,1024); `derive_p2` → `[U1,B,U2]` (32,1024,32), zero-mass slices → uniform | Present; X15-identical pipeline kept |

No production-module change is needed: disclosure restoration is a *caller-side*
delta (what truth the body injects), not a code change.

### 0d. Failure chain (frozen inputs, not re-argued)

- X14 (flat Dirichlet): greedy-SC mismatch **6946/7168 = 0.96903 ≈ chance 31/32 = 0.96875**
  (Δ +0.00028); Q1 spike survival 0.0 (reviewer: structural — spike ≡ low-mass truth
  ranked by same-row mass); Q2 both arms ≈ K/N = 52/256 = 0.203125 (void).
- X15 (0.75-diagonal structured channel, **sharper than real**: diagonal 0.75 vs recorded
  real f_max 0.3392 from X06): mismatch **7935/8192 = 0.96863** (Δ −0.00012 vs chance) —
  essentially UNCHANGED from X14 (Δ ≈ 0.0002 between probes) → G1 `[0.15,0.90]` violated →
  `X15_STOP_SANITY_G1` (`results.json` stop payload: `pooled mismatch ratio-of-sums
  0.9686279296875 outside [0.15, 0.90]`).
- No partial X16 dir exists (planner grep `NBPOLAR-X16|X16-SYNTHETIC|nbpolar_x16` clean);
  this packet creates rather than completes.
- Fresh seeds `2026092380..2026092388` + `nbpolar_x16_synthetic_scale_disclosure`:
  planner grep absent 2026-09-20 (probes for `2026092380`, `2026092387`, X16 names clean);
  operator re-verifies the FULL range by repo grep at freeze (§7).

## 1. Diagnosis verdict (evidence-based)

**Main-thread diagnosis SUPPORTED as the leading structural explanation** (X16 is the
experimental test, not the confirmation):

1. **Channel-structure moves nothing.** X14→X15 sharpened the channel from near-random
   to a 0.75 diagonal (sharper than the recorded real f_max 0.3392) while holding every
   other recipe fixed; mismatch moved 0.96903 → 0.96863 (Δ ≈ 0.0002, noise around the
   0.96875 chance ceiling). A channel-driven ceiling would have moved. It did not.
2. **The disclosure handle is absent in both probes.** X14 §3 / X15 §4 use the 52-prefix
   for `pm` and Q2-K only; neither packet passes `known_positions`/`known_values` to
   `sc_decode` (which defaults to all-undecided, §0c). The real pipeline discloses
   K1=334 L1 positions (≈1%) + K2=6746 L2 prefix (≈20.6%) at N=32768 with 15 polarization
   levels; the probes ran 8 levels with zero anchors. An unanchored greedy SC at small N
   has no correction handle, so mismatch sits at the chance ceiling regardless of
   per-column sharpness.
3. **Scale compounds it.** N=256 (8 levels) entered via the X06 cost convention (§0b),
   never as a polarization claim; the SCL-coverability question belongs to the polarized
   regime where disclosure + polarization jointly concentrate errors.

**One recorded rival mechanism (falsification risk, carried openly):** the X14 reviewer
flagged the metric-feed reading (argmax-p1 hard-u1 L2 metrics fed to an X-domain SC —
a possible domain/double-transform artifact). If SO, even disclosed X16 could stay at
chance. §3 G1/G2 branching discriminates: ranking (Q1b/G2) is decoder-free and
domain-clean, while G1 exercises the SC path. G1-high + G2-pass ⇒ SC-path disease
(metric-feed audit next, NOT closeout); G1-high + G2-fail ⇒ channel-level
non-informative ⇒ closeout (§5).

## 2. Frozen definitions (X14 §2 / X15 §2 reused VERBATIM — v1/v2/v3 comparable)

**Hazard atom (frozen recipe, `l2_alt_hold_1p5m.py:1321`):**
`h_j = −log2 p2[u1_cond_j, b_j, u2_true_j]`, bits base 2; exact-zero mass raises (never
replaced by uniform; synthetic construction guarantees positive arm-table mass).

**Spike definition (frozen quantities only):** Let `pm = mean(h_j)` over the disclosed
prefix (the `l2_prefix_hazard_mean_bits` recipe). Position `j` is a **spike** iff excess
`e_j = h_j − pm ≥ 2.0` bits. **Strata** by excess depth: `[2,4)`, `[4,8)`, `[8,∞)` bits,
plus a non-spike reference stratum (`e_j < 2.0`, recorded as `nonspike_ref`). Margin and
bins are descriptive recording buckets, never thresholds or verdicts.

**Ranking definition (frozen, per-position):** At each L2 position `j` with conditioning
`(u1_cond_j, b_j)` from the operational (hard-`u1`) path, sort the 32 `u2` symbols by
arm-table mass `p2[u1_cond_j, b_j, :]` descending, ties toward the smallest symbol index
(the `sc.py` argmax convention). `r_j` = 1-based rank of the true `u2_j`.
**Survival:** `survives_j(L)` iff `r_j ≤ L`, for `L ∈ {4, 8}`. **Survival fraction** =
mean of `survives_j(L)` over spike positions in a block, reported per-seed then pooled
across seeds as mean / sample-std(n−1) / range — stratified by excess-depth bin × L.
Q1b repeats this with `p1[·,b_j]` columns and true `u1_j`.

**Local-spike detector (Q2, frozen F-median8):** `d_j = h_j − median(h over the R=8
clipped natural neighborhood of j)` (the `FROZEN_HAZARD_R=8` recipe with median; user
decision 2026-09-20, P20S §3 verbatim). Detector selection = top-K2_synth positions by
`d_j`; baseline selection = top-K2_synth by global `h_j` (the H2a-REFUTED mean-hazard
logic). **Coverage** = fraction of greedy-SC operational mismatch positions contained in
each selection, reported descriptively per-seed + pooled. Mismatches come from the
accepted greedy `sc_decode` (L=1) run once per block against synthetic truth — the sole
decoder use, recording-only.

**X16 disclosure deltas (caller-side truth injection — NOT definition changes; the
"operational hard-u1 path" and "known-coordinate" semantics of §0c are preserved, the
restored operating point only changes what the operational path knows, exactly as real
disclosure does):**
- (D1) L1 disclosure: `u1_cond_j = u1_true_j` at the first-K1 (= 334) natural positions;
  argmax-p1 hard-u1 elsewhere (X14 within-freeze reading kept where undisclosed).
- (D2) L2 disclosure: `sc_decode` receives `known_positions` = first-K2 (= 6746) natural
  positions with `known_values` = true u2 there (forced-correct, mirroring real disclosed
  semantics); all other positions decided by argmax convention.
- Static natural order kept (table is position-free ⇒ table-marginal E[h] is
  position-free, X15 precedent); disclosed prefix = first-K positions for pm (frozen
  `l2_prefix_hazard_mean_bits` recipe at the restored K).

**Q2 re-asked — YES, and for the first time askably.** Q2 was void twice for lack of
variance (X14: both arms at K/N; X15: gated before variance could exist). The restored
operating point is DESIGNED to restore variance; the detector/baseline/K-selection are
byte-identical to X14/X15, so any v1/v2/v3 coverage delta is attributable to
operating-point restoration alone. Interpretation caveat (descriptive note, not a rule):
disclosed positions cannot mismatch, so mismatch mass lives in the undisclosed region
while selection ranges over all positions. If variance is absent anyway
(mismatch < 0.005 over 262144 positions), Q2 is recorded null-with-reason per the X14
review precedent (`DESCRIPTIVE-PASS, INFERENTIALLY VOID`) while Q1/Q1b — the PRIMARY
question, decode-independent — still proceed.

## 3. Restored-operating-point design

- **N = 32768 (exact real scale).** Rejected N=4096/8192: K1 would round (334/32768×4096
  = 41.75) breaking exact-ratio fidelity, and 12–13 levels test the N-scale half of the
  diagnosis only weakly. At N=32768 the synthetic K values ARE the real K values
  (K1=334, K2=6746, zero rounding), polarization scale is exact (15 levels), and cost is
  affordable (§3 estimates below). This directly tests both halves of the diagnosis.
- **Disclosure mirrors real ratios exactly:** disclosed L1 = 334/32768 ≈ 1.019%,
  disclosed L2 = 6746/32768 ≈ 20.587% (2M-session values, §0a — never new tuning).
- **Channel: X15 diagonal kept** (0.75 pin / C8-90% / rare96-zero / rest-mass per X15 §4
  verbatim). It is sharper than real (f_max 0.3392), so it remains the conservative
  structure: success here does not overclaim about the noisier real channel.
- **Blocks: 8 seeds × 1 block = 8 blocks = 262144 L2 positions** (36× X14's 7168; strata
  populations massive from few SC calls). Master `2026092380` is a reserved identity
  label only (deterministic table ⇒ zero table RNG, X15 precedent); block seeds
  `2026092381..2026092388`.
- **Runtime estimate (anchored, not guessed):** P20S measured ≈ 7.0 s/SC at N=32768
  (§0a). 8 SC ⇒ ≈ 56 s + vectorized sampling/metric/transform overhead (seconds) ⇒
  est. 90–180 s total ⇒ `timeout 600` gives 3–6× headroom.
- **Memory estimate (anchored):** SC top-level `_minus_block` transient
  (16384,32,32) float64 ≈ 134 MB + `decision_metrics` (32768,32) ≈ 8 MB + tables/metrics
  ≈ 35 MB ⇒ est. peak < 400 MB vs observed P20O HWM 539 MB, inside the 2 GiB P20S
  envelope. No new risk class.

### Sanity gates (wiring/structure checks only, not claim thresholds)

- **G1 (disclosure-bite gate, ONE-SIDED stop):** pooled greedy-SC mismatch ratio-of-sums
  **< 0.75**, else `X16_STOP_SANITY_G1_HIGH` + return. Justification: with K2=6746
  forced-correct, the no-information ceiling is
  `(1 − 6746/32768) × 31/32 = (26022/32768) × 0.96875 ≈ 0.769`. A value at/above 0.75
  means disclosure did not bite ⇒ the channel is still non-informative AT THE SC PATH
  (the X14/X15 disease persisting ⇒ fire the §5 branch, do not repair inputs).
  Expected once disclosure exists: BELOW the ceiling, plausibly LOW (0.00–0.35) — the
  diagonal is sharper than real and real P20Q operational arms reached 4/5 exact blocks
  WITH disclosure. There is NO low-side stop (a near-zero mismatch is informative,
  not broken); below 0.005 a low-variance note is recorded and Q2 goes null-with-reason
  while Q1/Q1b proceed. X15's `[0.15,0.90]` is NOT reused: its lower edge presumed an
  undisclosed error floor that disclosure explicitly removes, and its upper edge sat
  below no derived ceiling.
- **G2 (ranking-wiring floor, UNCHANGED from X15):** pooled Q1b non-spike L8 survival
  ≥ 0.50, else `X16_STOP_SANITY_G2`. Justification carried verbatim: identical
  decoder-free ranking machinery + identical channel ⇒ same expectation (diagonal 0.75
  ⇒ ≈0.75 capture; 0.50 is a loose wiring floor).
- **G3 (spike non-degeneracy, RE-SPECIFIED):** pooled spike fraction ∈ **[0.02, 0.70]**,
  else `X16_STOP_SANITY_G3`. Justification: bounds serve stratified-reporting
  populations at the new scale — lower 0.02 ⇒ ≥ ~5k spike positions over 262144 (bin×L
  cells populated); upper 0.70 ⇒ non-spike reference ≥ 30% (reference fraction stable).
  Reference only: X14 measured 0.104 at N=256 undisclosed; the shift direction under
  disclosure + full scale is DESCRIPTIVE (recorded, never gated tightly).
- **Stop-path discrimination rule (new, packet-level, no definition change):** on a G1
  stop, the body still records the decoder-free scalars (G2 value, G3 value, calibration
  scalars of X15 §3: table f_min/f_max, model H1/H2, diagonal mass, pointwise argmax hit
  rates, model_mean_hazard_bits, measured floor-hit rate) into the stop payload BEFORE
  returning — they cost no SC call. This is what lets the main thread execute the §1
  branch (SC-path disease vs channel disease) without a second probe.

## 4. Implementation scope for the coder operator

**New files only** (X08/X09/X10 pattern; zero production-module edits):

- `workspace/probes/nbpolar_x16_synthetic_scale_disclosure/prereg.md` — the frozen
  3-line prereg (verbatim `PREREG_DRAFT.md` content), written BEFORE any synthetic
  generation.
- `workspace/probes/nbpolar_x16_synthetic_scale_disclosure/body.py` — single
  self-contained probe script (stdlib + numpy only). Read-only imports allowed:
  `empirical_channel` (sampling recipes only; tables injected in-body),
  `prior` (`derive_p1/derive_p2/build_p1_metrics/gather_p2_metrics/probs_to_symbol_metric`),
  `algebra.make_gf32`, `transform.polar_transform`, `sc.sc_decode` (Q2 mismatch oracle
  + D2 disclosure conditioning only). Must NOT import or create any list decoder; must
  NOT open any protected artifact (assert by path refusal: `pairs_loader`, V25 counts,
  parquet, 1M/1.5M/2M content never imported/touched). Embeds: §2 definitions + D1/D2
  disclosure deltas, X15-§4 channel recipe at N=32768, 4 injected self-tests
  ((a) rank-1-peaked + tie-break X14-identical; (b) diagonal-smoke — column sums,
  disjointness, argmax=diagonal, floor-hit 96/1024; (c) disclosure-smoke — all-known
  SC returns exact, K1/K2 prefix sizes exact; (d) sanity-gate asserts), per-seed
  computation, `results.json` writer (+ stop-payload writer with decoder-free scalars).
- `workspace/probes/nbpolar_x16_synthetic_scale_disclosure/results.json` — the ONLY
  file `body.py` writes (indent=1): `probe_id`, `tier: "X"`, status
  `"X16_PROBE_COMPLETE_DESCRIPTIVE_ONLY"` (or `X16_STOP_SANITY_*` / `X16_STOP_IMPOSSIBLE`
  payload), question, per-seed survival tables (Q1/Q1b, by bin × L) + pooled
  mean/sample-std(n−1)/range, Q2 coverage pairs, measured floor-hit rate, spike-position
  counts per stratum, calibration scalars, command, interpreter, `decoder_calls` (Q2 SC
  count = 8 on the complete path), `rng_calls`, `tag_calls: 0`,
  `protected_opens_attempted: false`, writes, notes. Scalar-only; expected < 100 KB
  (8 seeds × small tables; evidence-size rule satisfied by construction).

**Frozen command** (§6 line 3 of prereg): single-thread env pins + `timeout 600 … body.py`.
**Stop rules:** any protected-path import/open attempt; nonfinite result;
`ImpossibleDisclosedValueError` → `X16_STOP_IMPOSSIBLE` (disclosed truth without SC
support — structural finding, no repair); missing fresh-seed grep proof at freeze;
`results.json` > 2 MB; body/prereg token mismatch; any sanity-gate violation →
`X16_STOP_*` + return, no input repair (no tuning, no re-pinning, no rerun to change
numbers). Execution-error only ⇒ one recorded rerun.
**Focused review:** independent reviewer-go focused numerical review (commands,
completeness, arithmetic, truth isolation, write scope) — Tier-X rule, no
Pre-EXECUTE/Pre-RESULT.

## 5. CLOSEOUT ALTERNATIVE (explicit)

If this design could NOT reach an informative operating point without real-data artifact
access or a P16-scale redesign, the recommendation would be: declare D3's synthetic line
non-informative (recording the two-probe negative-capability finding — channel
sharpness moves nothing at the undisclosed operating point) and redirect the SCL
question to a later, properly gated effort. **That alternative is NOT recommended
because the design closes every gap with frozen machinery:** `sc.py` natively conditions
on disclosed positions at any power-of-two N (§0c, read-verified — no code change, no
redesign); exact 2M ratios transfer with zero rounding at N=32768; cost is ≈ 7 s/SC × 8
(measured anchor) inside a 600-s envelope; Tier-X compliance holds (§6).

**Post-execution branch (for the main thread after X16 returns):** if X16 completes,
the SCL-coverability evidence speaks. If X16 stops G1-high WITH G2-pass ⇒ SC-path
disease ⇒ commission a metric-feed audit (rival mechanism, §1), do NOT close out. If
X16 stops G1-high WITH G2-fail ⇒ channel-level non-informative ⇒ declare the D3
synthetic line non-informative (three-probe negative capability recorded) and redirect
the SCL question to a later gated effort. Either stop consumes no attempt and moves no
scientific status.

## 6. Goal / Non-Goals / Impact Scope / Acceptance Criteria / Tasks

- **Goal:** Preregistered, synthetic-only, descriptive survival/coverage evidence at the
  restored operating point (N=32768, real-ratio L1+L2 disclosure, X15 diagonal channel):
  Q1/Q1b top-L survival at frozen-hazard spikes + Q2 F-median8 vs mean-hazard coverage +
  §3 sanity gates — the exact evidence D3 needs to unlock-or-refute the SCL route
  without touching protected data or implementing SCL.
- **Non-goals (binding):** No FER/reliability/efficiency/branch-superiority verdicts; no
  thresholds, no pass/fail; no SCL implementation or unlock (coverability evidence only);
  no protected opens (V25 counts, parquet/pairs, 1M/1.5M/2M content, `raw_prior_*.npz`);
  no real-data decoder run; no tag-domain use (`toeplitz_tag` never called;
  `tag_calls: 0`); no α/floor/channel/K/decoder/production-module changes (read-only
  reuse; K values are replayed 2M literals, §0a); no (b)/(c) bounded-search or
  second-construction work; no D1/D2 real-data work; no ledger/memory/index updates
  per-probe (batched at milestones per Tier-X rules).
- **Impact scope:** Three new packet docs (this dir) + three new probe-root files
  (`prereg.md`, `body.py`, `results.json`). No files outside these six are created or
  modified. `formal_ir/nbpolar/` modules are read-only imports. `results/`,
  `comparison_bench/outputs_comparison/`, ledgers, and sibling checkouts are untouched.
- **Acceptance criteria:** (i) three packet docs + frozen 3-line prereg consistent; (ii)
  fresh seeds/tag-absence proven by repo grep at freeze; (iii) focused tests + full
  NB-Polar suite green (T0/T1 at implementation; T2 not required for Tier-X); (iv)
  single execution under the frozen command writes only `results.json` with per-seed
  values + mean/sample-std(n−1)/range and zero protected opens; (v) sanity gates
  evaluated with `X16_STOP_*` on violation, stop payloads carrying decoder-free scalars
  (§3 rule); (vi) focused numerical review recorded; (vii) no claim, threshold, or
  verdict token anywhere in outputs.
- **Tasks (coder, after freeze authorization):**
  1. Freeze: verify seeds 2026092380..2026092388 + root name absent by repo grep; write
     `prereg.md` (verbatim `PREREG_DRAFT.md`) into the probe root BEFORE any generation;
     embed the §2/§3 recipes as the frozen `body.py`; add the 4 self-tests (§4).
     Verify: grep output clean, tests green, no protected imports.
  2. Execute once under the frozen command (`PREREG_DRAFT.md` line 3); on
     execution-error only, one recorded rerun. Verify: exit 0, `results.json` sole
     write, scalar-only, < 2 MB, per-seed + pooled stats present.
  3. Return deltas only: gate values, survival fractions by bin × L (Q1/Q1b), Q2
     coverage pairs (or null-with-reason), measured floor-hit rate vs 9.375% pin,
     calibration scalars, spike counts per stratum, command/wall, blocker-or-none.
     Obtain focused numerical review. No commit/push; no claims.

## 7. Tier compliance adjudication

- Synthetic-only truth injection (D1/D2) is Tier-X compliant — same class as Q2's
  existing oracle use (synthetic truth conditioning a synthetic SC run); no artifact or
  real-data access of any kind.
- Parameterizing the in-body model by replayed 2M K literals (334/6746) is Tier-X
  compliant — same as X14's 9.35% pin and X15's p_err=0.25 pin (published scalars, no
  content opens).
- Tier-X: probe-root-only writes, 3-line prereg, per-seed + mean/std/range, no
  thresholds/verdicts, SCL stays locked, no candidate/accepted token, no
  scientific-status change. Evidence-size rule (D4): single file ≤ ~2 MB — satisfied
  (< 100 KB estimate).

## 8. Standing rules inherited

Decision record §5 non-goals bind this probe (§6). Per-probe ledger/memory/index updates
are milestone-batched per Tier-X rules.

## 9. Label note (single decision needed, not a blocker)

No X16 prefix exists anywhere in repo or probe roots (planner grep clean, §0d), so the
label `NBPOLAR-X16-SYNTHETIC-SCALE-DISCLOSURE` / root
`nbpolar_x16_synthetic_scale_disclosure/` collides with nothing. **ONE decision needed
from the main thread at approval:** approve the X16-proceed design as frozen (RECOMMENDED
— §5 shows every gap closed with frozen machinery), or direct the closeout alternative
(now — only if the main thread judges the §1 rival mechanism disqualifying before data,
which the G1/G2 branch is explicitly designed to discriminate after data).
