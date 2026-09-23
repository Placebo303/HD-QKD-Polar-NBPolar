# Step-1 small-q simulation screening design (native-symbol vs bit-plane binary decomposition) (design artifact — authorizes nothing)

## 0. Status

- `EXPLORATION_ONLY / DOCS_ONLY` — this file is a **design artifact** for the
  future Step-1 small-q simulation screening. It **authorizes no code, no run,
  no freeze change, no frozen-constant change, no data access, no Tier-X probe
  run, and no Tier-Y decision gate**.
- Parent scope: `openspec/changes/nbpolar-native-highdim-exploration/`,
  specifically proposal §Step 1 ("small-q simulation screening (q ∈ {4, 8, 16}):
  native-symbol vs bit-plane binary") and design §D3 (Step-1 screening design).
- Any future screening execution needs its own freeze document plus separate
  verbatim user authorization per AGENTS.md §10.1–10.4. Nothing here satisfies
  that requirement.
- This file selects **no reference decoder algorithm** for arm A. Naming the
  algorithm is a future-freeze item (see §8). No list size, iteration cap,
  channel parameter value, seed, or numeric stop-loss constant is fixed here.
- Minimalism (AGENTS.md §5.7): plain markdown only. No code, no checksums, no
  atomic writes, no schema validators, no retry frameworks, no defensive
  machinery (see §11).

### User-adjudicated decisions OQ1/OQ2 (2026-09-23; recorded verbatim, not re-opened)

- Proposal adjudication note (2026-09-23): "(1) {4, 8, 16} locked; q=32 not
  pre-allowed. (2) Qualitative bar fixed now; the hard numeric separation
  threshold is deferred to the future freeze."
- `tasks.md` OQ section (2026-09-23): "OQ1：Step-1 筛选 ladder 是否锁定
  q∈{4,8,16}，还是预允许 q=32。Decision: DECIDED 2026-09-23（用户裁决）——锁定
  q∈{4,8,16}，不预允许 q=32（与 design D3 现状一致）。"
- `tasks.md` OQ section (2026-09-23): "OQ2：Step-1 止损用硬性 FER–f
  分离阈值（现在定）还是定性 bar 留给未来 freeze。Decision: DECIDED
  2026-09-23（用户裁决）——定性 bar 现在定，硬性数值阈值留给未来
  freeze（与 design D3 现状一致）。"
- Consequence: the Step-1 screening ladder is LOCKED to q ∈ {4, 8, 16}.
  q=32 is NOT pre-allowed anywhere in Step 1 — not as an arm, not as a pilot,
  not as an extra point. The stop-loss is the qualitative bar fixed in §5;
  no hard numeric FER–f separation threshold is set here.

## 1. Scientific question, success criterion, stop-loss, not-doing list

(Substance identical to proposal §Step 1 and design §D3; neither weakened nor
extended.)

- **Scientific question:** does native-symbol decoding separate from bit-plane
  binary decomposition on FER–f at matched rate/block-length/prior — i.e. is
  there a measurable signal worth scaling, or does Park–Barg ordering + good
  MSD already explain everything?
- **Read-only inputs:** synthetic channel family preregistered at the family
  level in §3 below (small q only; seeds frozen only at the future freeze; no
  real data, no `.ttbin` path, no frozen-artifact read beyond what the future
  freeze names).
- **Design outputs (later, under separate authorization):** paired FER–f curves
  per q (§4), separation statistic with uncertainty (§4), qualitative stop-loss
  bar (§5) applied without post-hoc tuning (§6).
- **Success:** a future `prereg.md` exists fixing every item in the §6 template
  shape before any run, and a single future `results.json` records per-seed
  values + mean/sample-std/range for the paired metric.
- **Stop-loss (qualitative bar, per OQ2):** no separation across q ∈ {4, 8, 16}
  ⇒ do not scale to d=1024 and record the negative; clear separation ⇒ Step 2/3
  designs may be frozen next (§5). The hard numeric threshold is a
  FUTURE-FREEZE item and must not be tuned post-hoc.
- **Not doing:** no decoder implementation, no d=1024 anything (no d=1024
  simulation, no d=1024 complexity claim here), no real-data contact, no claim
  of any kind — no FER claim, no efficiency claim, no promotion claim, no
  qualification claim, no composable-key or security claim (§9).

## 2. Arms, matched on rate, block length, channel seed, prior family

- **Arm A — native-symbol small-q decoder.** Operates directly on the q-ary
  symbol alphabet (q ∈ {4, 8, 16} per the locked ladder). The reference
  algorithm is deliberately NOT selected here: naming it (decoder family,
  message representation, schedule) is a future-freeze item (see §8). This
  design fixes only the arm's *role*: the native-symbol side of the paired
  comparison.
- **Arm B — bit-plane binary decomposition with ORDERED MSD-style
  conditioning.** The q-ary symbol (q=2^r with r ∈ {2, 3, 4}) is decomposed
  into r ordered bit-planes following the Park–Barg q=2^r ordered bit-level
  structure, and decoding preserves inter-level conditional dependence along
  that order: each level is decoded conditioned on the already-decided
  earlier levels (multistage / MSD-style conditioning with joint soft
  information carried across levels), in the fixed Park–Barg level order.
  This is NOT BICM-naive: a BICM-style arm that decodes each bit-plane
  independently while neglecting inter-level correlation is explicitly excluded
  from arm B. The Jiang–Narayanan rate loss from neglecting inter-level
  correlation is the failure mode arm B must avoid — arm B is fair only
  insofar as it preserves the conditional dependence the native-vs-binarized
  question is actually about.
- **Fairness requirements between arms (all to be frozen exactly at the future
  freeze; enumerated here as requirements, not values):**
  1. Same information available to both: identical channel draws, identical
     prior family, identical rate and block length; neither arm receives side
     information the other lacks.
  2. Same stopping-criteria class: the two arms share the same stopping rule
     family (e.g. iteration/list budget class fixed jointly), so a separation
     cannot be an artifact of one arm being allowed to try harder.
  3. No oracle leakage into either arm: no ground-truth symbol, error position,
     or draw-dependent tuning shared with either decoder; all parameters and
     seeds are fixed at prereg time.
  4. Paired draws: both arms run on the same seeds and the same channel draws
     (§4), so the comparison is paired, not two independent samples.

## 3. Synthetic channel family (family-level preregistration; values deferred)

- Preregistered in this design at the **family level only**: a synthetic
  q-ary channel family over the locked ladder q ∈ {4, 8, 16}.
- A ±1-dominated limited-magnitude parameterization is allowed as one family
  member (motivated by the Step-0 question of whether the residual channel is
  ±1-dominated; cf. the Zhou–Wang–Wornell limited-magnitude modeling analogy
  cited in the proposal). No other family member is named here; the future
  freeze may only instantiate members within the small-q family envelope fixed
  by its own preregistration.
- **Explicitly deferred to the future freeze (no numeric channel parameters
  invented here):** exact per-member parameter values, exact noise/transition
  specification, exact seed values and seed count, exact block-length and rate
  values for the screening operating points, exact prior-family instantiation.
  The future `prereg.md` must fix all of these before any run (§6).

## 4. Metric: paired FER–f at matched operating points, with uncertainty

- **Metric:** paired frame-error-rate vs reconciliation-efficiency (FER–f) at
  matched operating points (matched rate, block length, channel seed, prior
  family per §2).
- **Pairing:** for each q ∈ {4, 8, 16}, each seed, and each channel draw, both
  arms decode the same received block; the separation statistic is defined on
  these paired outcomes (same seeds, same draws) — never on unpaired or
  cross-seed aggregates.
- **Recorded values:** the future `results.json` records per-seed values plus
  mean / sample-std / range across seeds, separately per q and per arm, plus
  the paired per-seed difference series from which the separation statistic is
  computed.
- **Uncertainty stated:** uncertainty is the observed seed-to-seed spread —
  reported as the per-seed values with their mean, sample standard deviation,
  and range. No confidence-interval model, significance threshold, or numeric
  decision constant is fixed here; those belong to the future freeze (OQ2).
- **Separation reading (qualitative, per OQ2):** whether the paired difference
  series shows a consistent same-sign separation across the q ladder (§5). This
  reading is recorded once against the pre-fixed bar; it is not re-tuned after
  seeing the data (§6).

## 5. Stop-loss (qualitative bar, per OQ2; no numeric threshold set here)

- **Bar (fixed now):** no separation across q ∈ {4, 8, 16} ⇒ do not scale to
  d=1024 and record the negative as kept evidence; clear separation ⇒ Step 2/3
  designs may be frozen next (each under its own freeze and authorization —
  this bar permits freezing those designs, it does not authorize any run).
- "No separation" and "clear separation" are qualitative readings of the §4
  paired difference series with its stated seed-to-seed spread, applied once
  against this bar.
- **Explicitly a FUTURE-FREEZE item (OQ2):** the hard numeric FER–f separation
  threshold (numeric constant, decision rule, per-q aggregation formula) is
  deferred to the future freeze. It must not be tuned post-hoc: no threshold
  may be chosen, moved, or reinterpreted after the result record exists (§6).
- Zero numeric threshold is invented in this design; any number appearing in a
  future threshold belongs to the future freeze document, not here.

## 6. Tier-X prereg template shape (what the future `prereg.md` must fix)

Per AGENTS.md §10.4, the future screening run — if ever authorized — is a
Tier-X probe. Its `prereg.md` must fix, before any run, at minimum:

1. Question: the §1 scientific question restated for the exact screening
   instance.
2. Exact q set: q ∈ {4, 8, 16} (locked; q=32 explicitly excluded).
3. Arms: the named reference algorithm for arm A (future-freeze selection) and
   the exact MSD-ordered conditioning order/specification for arm B, with the
   §2 fairness requirements instantiated as frozen values.
4. Channel family + seeds: exact family members, exact parameter values, exact
   seed list — frozen at prereg time, unchanged afterwards.
5. Matched conditions: exact rate, block length, prior-family instantiation,
   stopping-criteria class shared by both arms.
6. Metric: the §4 paired FER–f operating points, per-seed recording rule
   (values + mean/sample-std/range), and the separation-statistic definition.
7. Stop-loss bar: the §5 qualitative bar restated for the instance, plus — only
   if the future freeze sets one — the deferred hard numeric threshold it
   introduces (fixed before the run, never after).
8. Write root: the single future root
   `workspace/exploration/nbpolar-native-highdim/step1/` holding at most
   `prereg.md`, `results.json`, `notes.md` (cf. design §D1 envelope).
9. Exact command: the exact command (interpreter + entrypoint + config + seed
   list) to be executed, frozen at prereg per AGENTS.md §10.4.

- **Rerun-once rule:** one rerun is allowed only to fix an execution error, and
  it must be recorded in the single result record (`notes.md` entry: what
  failed, what was fixed, what changed in execution only — never in parameters,
  models, or seeds).
- **No-post-hoc-tuning guards:** parameters, models, and seeds freeze at prereg;
  no threshold (qualitative reading or numeric constant) may be tuned after the
  fact; a rerun required to fix an execution error never re-opens the frozen
  bar. The probe ends with ONE result record; it creates no candidate/accepted
  token, consumes no claim attempt, and changes no scientific status.

## 7. Sim/real firewall

- Parameters, models, and seeds freeze at prereg (§6); nothing learned from the
  screening output flows back into the frozen configuration.
- No sim FER ever enters a real-data table or is cited as a real FER. Synthetic
  (L2) and real-data (L1) values live in separate ledgers (design §D1: L1
  frozen real-data record vs L2 future synthetic/sim ledger); L2 values are
  never merged into, compared numerically against, or cited as L1 FER.
- No d=1024 simulation at Step 1 — the ladder is locked to q ∈ {4, 8, 16}.
- No real-data FER is produced, read as input (beyond the frozen numerical
  references named by the parent proposal where applicable), or claimed here.
- No sim→real generalization claim: a small-q separation signal, if observed,
  motivates freezing Step 2/3 designs — it does not assert anything about
  d=1024 native performance or about real-data FER.
- Separate ledgers reaffirmed: L2 synthetic (this step's future ledger) vs L1
  real (read-only frozen record). Step-0 descriptive outputs live in L3 and are
  likewise never cited as FER.

## 8. Explicitly deferred to the future freeze (state each)

1. Reference decoder algorithm for arm A (family, message form, schedule).
2. List sizes (wherever a list decoder is named).
3. Iteration caps / stopping-budget numeric values (the §2 fairness requirement
   fixes the class now; the numbers wait for the freeze).
4. Numeric stop-loss constant and decision rule (OQ2: hard threshold deferred).
5. Exact channel parameter values (per-member specification within the §3
   family envelope).
6. Seeds (exact seed list and count).

Nothing in this list may be filled in by assumption, placeholder, or inference
in this design; each is fixed only by the future freeze before any run.

## 9. Not doing

- No decoder implementation (no q-ary polar / HD-Cascade / list-decoder code).
- No d=1024 anything: no d=1024 simulation, no d=1024 extrapolation, no GF(32)
  or split-dimension work (Step 3 scope, not this step).
- No real-data contact: no `.ttbin` read, no EVAL/RESERVE consumption, no
  frozen-artifact modification, no prior-code change.
- No claim of any kind: no FER claim, no efficiency claim, no promotion claim,
  no qualification claim, no composable-key or security claim. Any future
  claim-bearing gate is Tier-Y and needs its own change, freeze, independent
  Pre-EXECUTE/Pre-RESULT reviews, and explicit user authorization.

## 10. Frozen-number box (verbatim provenance; not screening results)

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
§Frozen facts verbatim. They are provenance context for the matched-condition
envelope, not screening inputs or results.)

## 11. Minimalism (§5.7)

- Plain markdown: this file plus the future `prereg.md` / `results.json` /
  `notes.md` triplet only. No code, no checksums, no atomic writes, no schema
  validators, no retry frameworks, no caching layers, no hardening beyond the
  concrete failure modes named here (wrong-ledger citation, frozen-file touch,
  raw-data read, post-hoc threshold tuning — each guarded in §6–§7).
- Each future packet names its single realistic failure mode or omits the
  mechanism.
