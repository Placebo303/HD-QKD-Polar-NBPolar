# Step-2 transfer-prior injection design (uniform vs informed init) (design artifact — authorizes nothing)

## 0. Status

- `EXPLORATION_ONLY / DOCS_ONLY` — this file is a **design artifact** for the
  future Step-2 transfer-prior probe. It **authorizes no code, no run, no
  freeze change, no frozen-constant change, no data access, no Tier-X probe
  run, and no Tier-Y decision gate**.
- Parent scope: `openspec/changes/nbpolar-native-highdim-exploration/`,
  specifically proposal §Step 2 ("transfer-prior injection: non-uniform init
  from the real transition matrix") and design §D4 (Step-2 transfer-prior
  design, uniform vs informed init).
- Any future Step-2 execution needs its own freeze document plus separate
  verbatim user authorization per AGENTS.md §10.1–10.4. Nothing here satisfies
  that requirement.
- This file selects **no decoder algorithm**, fixes **no seeds**, fixes **no
  numeric gain threshold**, and defines **no mapping arithmetic** from the
  frozen transition structure to initial messages (see §8). No number in the
  §10 frozen box is moved by this design.
- Minimalism (AGENTS.md §5.7): plain markdown only. No code, no checksums, no
  atomic writes, no schema validators, no retry frameworks, no defensive
  machinery (see §11).

## 1. Scientific question

(Substance identical to proposal §Step 2 and design §D4; neither weakened nor
extended.)

- **Scientific question:** does initializing a (small-q, Step-1-compatible)
  decoder with the real-data transition structure (the frozen M2 ±1 finding)
  as non-uniform initial messages beat a uniform init — and is a negative
  recorded as a result, not discarded?
- **Read-only inputs:** the frozen M2 ±1 / transition-matrix finding as a
  **fixed numerical reference only** (§2, §6); the Step-1 screening envelope
  (§3).
- **Design outputs (later, under separate authorization):** a uniform-vs-informed
  paired comparison with a preregistered gain metric (§4) and a
  negative-outcome recording rule (§5).
- **Not doing (summary; full list in §9):** no M2 modification, no CAL change,
  no EVAL/RESERVE consumption, no real-data FER, no claim of any kind.

## 2. Arms: informed init vs uniform-init control, PAIRED

- **Arm I — informed init.** The decoder is initialized with non-uniform
  initial messages taken from the frozen M2 ±1 / transition-matrix structure
  named in §6. The frozen structure is used as a **FIXED NUMERICAL REFERENCE
  ONLY**: it is read as numbers and copied into the future freeze's
  init-construction specification. Explicitly forbidden here and in any future
  Step-2 packet: re-estimation of the transition structure, re-fitting on any
  data, any change to `prior_m2.py`, any CAL change, any decoder change to
  accommodate the prior.
- **Arm U — uniform-init control.** Identical decoder, identical channel
  draws, identical everything except the initial messages, which are uniform
  over the q-ary alphabet. Arm U is the control; it exists only to give the
  paired difference in §4 a meaning.
- **PAIRED discipline:** both arms share seeds and channel draws. For each q,
  each seed, and each channel draw, both arms decode the same received block;
  the gain metric (§4) is defined on these paired outcomes — never on
  unpaired or cross-seed aggregates. Neither arm receives side information the
  other lacks; no ground-truth symbol, error position, or draw-dependent
  tuning enters either arm; all parameters and seeds are fixed at prereg time
  (see §7).

## 3. Envelope compatibility with the Step-1 screening envelope

(Step 2 runs inside the Step-1 envelope; it adds no new object. Conventions
follow the sibling artifact `step1-screening-design.md`, which is read for
compatibility and not modified.)

- **Same small-q family:** q ∈ {4, 8, 16} only (the locked Step-1 ladder).
  Step 2 adds no new q.
- **Same matched-condition conventions:** matched rate, block length, channel
  seed, and prior-family handling per the Step-1 fairness requirements; the
  only deliberate difference between the two Step-2 arms is the initial
  messages (§2).
- **Same seeding conventions:** seeds freeze at prereg time; paired draws
  shared across arms (§2, §7).
- **No d=1024 object:** no d=1024 simulation, no d=1024 extrapolation, no
  split-dimension or GF(32) work (Step-3 scope, not this step).
- **Same future decoder selection as Step-1 arm A:** the reference decoder
  algorithm for both Step-2 arms is the same future selection as the Step-1
  arm-A algorithm — deliberately not selected here (see §8).

## 4. Gain metric (preregistered; precisely defined; no threshold set here)

- **Paired quantities (both computed on the §2 paired outcomes, separately
  per q ∈ {4, 8, 16}):**
  1. **Paired decoding-success difference.** For each seed s and each paired
     trial t on the same channel draw, let `ok_I(s,t)` / `ok_U(s,t)` be the
     1/0 decode-outcome indicators of arms I and U. The per-seed paired
     difference is `g_succ(s) = (Σ_t ok_I(s,t) − Σ_t ok_U(s,t)) / T_s`,
     where the denominator `T_s` is the number of paired trials run under
     seed s at that q (identical draws for both arms, so the denominator is
     shared, not per-arm).
  2. **Paired NLL difference.** For each paired trial t, let `nll_I(s,t)` /
     `nll_U(s,t)` be the recorded negative log-likelihood values under the
     same paired draw. The per-seed paired difference is
     `g_nll(s) = (Σ_t (nll_U(s,t) − nll_I(s,t))) / T_s`
     (positive means the informed arm assigned higher likelihood to the
     transmitted block on average over the paired trials).
- **Denominators stated:** `T_s` = count of paired trials at (q, seed s);
  the q-level summary denominator is the seed count. No per-frame, per-pair,
  or real-data denominator enters this metric; this is a synthetic-probe
  count, not a real-data rate.
- **Uncertainty structure:** the future `results.json` records the per-seed
  values (`g_succ(s)`, `g_nll(s)` series) plus, for each, the mean, sample
  standard deviation, and range across seeds, separately per q. No
  confidence-interval model and no decision constant is fixed here.
- **The numeric success threshold is a FUTURE-FREEZE item — no threshold is
  invented in this design.** Any number appearing in a future gain gate
  belongs to the future freeze document, not here, and must not be tuned
  post-hoc (see §7).
- This metric is a probe readout, not a claim: recording `g_succ` / `g_nll`
  asserts nothing about real-data FER, efficiency, promotion, qualification,
  or composable-key/security status (see §9).

## 5. Negative-outcome recording rule

- A clean zero or negative gain (`g_succ` ≈ 0 or < 0; `g_nll` ≈ 0 or < 0,
  within the stated seed-to-seed spread) is **KEPT EVIDENCE**.
- The future `notes.md` records it **as a result, never as a failed run to
  discard** (per design §D4). A negative does not trigger a rerun, a
  re-mapping, a re-fit, or a threshold move; the rerun-once allowance in §7
  covers execution errors only.
- The qualitative reading (gain vs no-gain vs negative) is applied once
  against the pre-fixed prereg; it is not re-tuned after seeing the data.

## 6. Boundary guard (hard)

- **Forbidden:** any consumption of EVAL blocks, any read of RESERVE frames,
  any re-fit on confirmation-boundary data, any new raw read of any kind
  (no `.ttbin` path anywhere). **Violation ⇒ stop:** the operator stops and
  returns to the main thread; no substitute path, no placeholder, no
  post-hoc derivation.
- **Also forbidden:** any `prior_m2.py` change, any CAL change, any decoder
  change (reaffirmed from §2).
- **Named M2-reference artifacts** (each verified to exist by read-only
  directory listing and file reading at design time; each non-`.ttbin`;
  each used as a numerical reference only — never re-derived, never
  re-fitted, never written to):

| # | Path (repo-relative) | Carries (transition / ±1 structure) | Provenance label |
|---|---|---|---|
| R1 | `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/delta_profiles.json` | PRIMARY ±1 structure: signed error-Δ histogram source (`profile.circular_counts` with `circular_offset` −512; `profile.linear_counts` with `linear_offset` −1023) and the \|Δ\| summary (`summaries.CIRCULAR`: n0 / n_plus / n_minus / n_tail / n_total); the ±1 cells and their wrap closure are the numerical reference for the informed init | G1R2 frozen derived artifact. SHG `_1` (`20260113_SHG_Type2PPLN_3s`), CHAR segment, 200,192 pairs, (N) W_P=200, MOD CIRCULAR, skip-702, derived offset +50 ps. Verified: directory listing + file read (header keys, offsets, summaries present) |
| R2 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/G1R2_ADJUDICATION.md` | CAL-conditional transition triple + wrap accounting: linear {−1023: 44, −1: 450, 0: 150909, +1: 48788, +1023: 1} / circular {−1: 451, 0: 150909, +1: 48832, tail 0} closure; CAL32 triple q0/q+1/q−1/q_rest = 0.7562255859375 / 0.241943359375 / 0.0018310546875 / 0; H_M2 = 0.8168138 / H_M0 = 0.6910589; held-out NLL reference | G1R2 main-thread adjudication `NBPOLAR_M2_PRIOR_G1R2_COMPLETE_DESCRIPTIVE` (descriptive/non-claim, decoder-free). Verified: directory listing + file read |

- The numbers quoted in the R1/R2 descriptions above are frozen-artifact
  content restated as reference provenance, not Step-2 inputs, results, or
  claims. The future freeze copies the needed values verbatim from R1/R2; it
  never recomputes them from raw data.

## 7. Tier-X prereg template shape + sim/real firewall + rerun-once + no-post-hoc guards

Per AGENTS.md §10.4, the future Step-2 run — if ever authorized — is a
Tier-X probe inside the design §D1 envelope. Its `prereg.md` must fix,
before any run, at minimum:

1. Question: the §1 scientific question restated for the exact probe
   instance.
2. Arms: arm I informed-init construction (which R1/R2 values, frozen
   verbatim) and arm U uniform control, with the §2 paired-draw discipline
   instantiated as frozen values.
3. Channel family + seeds: exact synthetic family members, exact parameter
   values, exact seed list — frozen at prereg time, unchanged afterwards
   (within the §3 small-q envelope; q ∈ {4, 8, 16} locked).
4. Informed-init construction: how the frozen transition structure maps to
   initial messages at each q ∈ {4, 8, 16} (fixed by the future freeze, not
   here — see §8).
5. Gain metric: the §4 paired quantities, denominators, per-seed recording
   rule (values + mean/sample-std/range), stated separately per q.
6. Negative-recording rule: the §5 rule restated for the instance (zero /
   negative gain kept as a result in `notes.md`).
7. Write root: the single future root
   `workspace/exploration/nbpolar-native-highdim/step2/` holding at most
   `prereg.md`, `results.json`, `notes.md` (cf. design §D1 envelope).
   That directory is NOT created by this design task.
8. Exact command: the exact command (interpreter + entrypoint + config + seed
   list) to be executed, frozen at prereg per AGENTS.md §10.4.

- **Freeze-at-prereg:** parameters, models, seeds, init construction, and
  the metric definition freeze at prereg time and must not change
  afterwards.
- **Rerun-once-for-execution-error rule:** one rerun is allowed only to fix
  an execution error, and it must be recorded in the single result record
  (`notes.md` entry: what failed, what was fixed, what changed in execution
  only — never in parameters, models, seeds, or init construction).
- **No-post-hoc-tuning guards:** no threshold (qualitative reading or
  numeric constant) may be chosen, moved, or reinterpreted after the result
  record exists; a rerun required to fix an execution error never re-opens
  the frozen bar or the frozen init construction. The probe ends with ONE
  result record; it creates no candidate/accepted token, consumes no claim
  attempt, and changes no scientific status.
- **Sim/real firewall:** parameters, models, and seeds freeze at prereg;
  nothing learned from the probe output flows back into the frozen
  configuration. No sim value ever enters a real-data table or is cited as a
  real FER. Synthetic (L2) and real-data (L1) values live in separate ledgers
  (design §D1: L1 frozen real-data record vs L2 future synthetic/sim
  ledger); L2 values are never merged into, compared numerically against, or
  cited as L1 FER. No sim→real generalization claim: a small-q informed-init
  gain signal, if observed, motivates freezing further designs — it does not
  assert anything about d=1024 native performance or about real-data FER.

## 8. Explicitly deferred to the future freeze (state each)

1. Exact decoder algorithm — the same future selection as the Step-1 arm-A
   reference algorithm (family, message form, schedule).
2. How the frozen transition structure maps to initial messages at each
   q ∈ {4, 8, 16} (the init-construction arithmetic from the R1/R2 values).
3. Seeds (exact seed list and count).
4. Numeric gain threshold (numeric constant, decision rule, per-q
   aggregation formula — the hard gate deferred alongside the Step-1 OQ2
   pattern).

Nothing in this list may be filled in by assumption, placeholder, or
inference in this design; each is fixed only by the future freeze before any
run.

## 9. Not doing

- No M2 modification (no re-estimation, no re-fit, no `prior_m2.py` change).
- No CAL change and no decoder change.
- No EVAL/RESERVE consumption (no EVAL block reads, no RESERVE frame reads,
  no re-fit on confirmation-boundary data) and no new raw reads of any kind
  (no `.ttbin`).
- No real-data FER (no real-data decode, no real-data success/FER object).
- No claim of any kind: no FER claim, no efficiency claim, no promotion
  claim, no qualification claim, no composable-key or security claim. Any
  future claim-bearing gate is Tier-Y and needs its own change, freeze,
  independent Pre-EXECUTE/Pre-RESULT reviews, and explicit user
  authorization.

## 10. Frozen-number box (verbatim provenance; not Step-2 results)

d=1024; N=32768 (=128 frames × 256 pairs); K1=319; K2=6492; P16
construction; W_P=200 / W_S=500 / CIRCULAR / skip=702; frame_pairs=256;
floor=1e-15; chunk=512; bin=200 ps; f(6811)=1.2747449;
key_dependent_bits=34,119 (=5·(K1+K2)+64, per-row constant);
public_control_bits=327,743; undetected 0/42 isolated (never merged into
success/FER); EVAL 14 blocks (frames 2398–4189); RESERVE SHG_1 29 frames /
SHG_2 99 frames; never pad/reuse/shrink, COMPLETE-BLOCKS-ONLY else
INSUFFICIENT; already-decoded segments = DEVELOPMENT data, never a
confirmation sample.

(No number in this box is moved by this design; all values match proposal
§Frozen facts verbatim. They are provenance context for the envelope, not
Step-2 inputs or results.)

## 11. Minimalism (§5.7)

- Plain markdown: this file plus the future `prereg.md` / `results.json` /
  `notes.md` triplet only. No code, no checksums, no atomic writes, no schema
  validators, no retry frameworks, no caching layers, no hardening beyond the
  concrete failure modes named here (wrong-ledger citation, frozen-file
  touch, raw-data read, post-hoc threshold tuning — each guarded in §6–§7).
- Each future packet names its single realistic failure mode or omits the
  mechanism.
