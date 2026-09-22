# Exploration proposal: native high-dimensional error correction for time-bin HD-QKD

## Status

`EXPLORATION_ONLY / PLAN_CANDIDATE` — not an execution authorization.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, branch `codex/nbpolar-phase0`.
- This change authorizes **no code, no experiment, no freeze change, no frozen-constant
  change, no production-data execution, no Tier-X probe run, no Tier-Y decision gate**.
- Every Step below is a **design + prereg task only**. Any future run needs its own
  freeze document and explicit user authorization (AGENTS.md §10.1–10.4).
- Structure/naming follows the reference
  `openspec/changes/archive/2026-09-22-nbpolar-prior-rebaseline/`
  (proposal/design/tasks + delta-spec convention; date-prefixed name only at archive time).
- Self-contained handoff: a new dialogue can resume from this proposal + `design.md` +
  `tasks.md` alone, without reading chat history.

## Goal

Decide, by the cheapest scientifically valid path, whether **native high-dimensional
(q-ary) error correction for arrival-time coding** has a performance advantage over the
already-implemented-and-measured binary trio (LDPC / Polar / Cascade) on the existing
data — succeeding on existing data first, testing on new data last (user intent).

## Non-Goals

- No production code; no implementation of any q-ary polar / HD-Cascade decoder.
- No change to any frozen constant, contract, or accepted packet.
- No simulation FER ever recorded as real-data FER (strict sim/real ledger separation).
- No new-data test, no confirmation claim, no security / composable-key claim.
- No reopening of any frozen negative result or sibling-verdict history.
- No Stage-3 gate execution (deferred — see §Stage-3 below).

## Frozen facts (verified; no number here may be altered)

- Operating point: time-bin high-dim `d=1024`, `N=32768` symbols/block
  (= 128 frames × 256 pairs), `K1=319` / `K2=6492`, P16 construction,
  `w=200` CIRCULAR, `skip=702`, `frame_pairs=256`, floor `1e-15`,
  `chunk=512`, bin `200 ps`.
- Frozen contract: efficiency `f(6811)=1.2747449`;
  per-block `key_dependent_bits=34,119` (algebraically `5·(K1+K2)+64`,
  **per-row constant, zero variance**); `public_control_bits=327,743`;
  `undetected` 0/42 isolated (never merged into success/FER).
- Data budget: per-session EVAL is 14 blocks only (2398–4189); RESERVE is
  SHG_1 29 frames / SHG_2 99 frames (both < 128, cannot form a new block);
  frozen rule: never pad/reuse/shrink, COMPLETE-BLOCKS-ONLY else INSUFFICIENT;
  already-decoded segments are DEVELOPMENT data, never a confirmation sample.
- Sibling state: binary LDPC / binary Polar / binary Cascade are implemented and
  measured. NB-LDPC wrong routes on record: GF(32)×GF(32) multilayer (V7R3),
  V54 Q_SUB=32 production shell, V13R3 native q=1024 (n=256, rate 0.336);
  current d=1024 NB-LDPC position is `f≈12.1`, leakage 6.64 bits/symbol,
  target `f≈1.1`. q-ary polar has zero implementation (NOT_FOUND); HD-Cascade has
  no code; qLDPC reference stops at q≤256 / d≤64.
- Cascade correction (no silent verdict drift): there is **no** standing verdict
  "binary Cascade is unsuitable for high dimensions". The Release checkout rejected
  Cascade-**lite** efficiency (2.43× Shannon, β clamped to zero, in the low-dim
  d=32~512 context); the d=1024 head-to-head was Cascade 60/60 vs Layered LDPC
  59/60 with p=1.0 ⇒ `no_decision`. What was ruled "unsuitable for the mainline"
  is Route C (q-ary Polar, for interface-rewrite reasons) — unrelated to Cascade.
- Literature anchors: Park & Barg (arXiv:1107.4965 / IEEE TIT 2013,
  DOI 10.1109/TIT.2012.2219035) — q=2^r asymptotics remain r ordered bit-levels,
  so the native-vs-binarized question is whether inter-level conditional dependence
  (MSD / joint soft information) is preserved; Jiang & Narayanan (ISIT 2006) —
  BICM-style neglect of inter-level correlation costs rate; Zhou–Wang–Wornell
  (ITA 2013, DOI 10.1109/ITA.2013.6502993) — ±1 delay as limited-magnitude error,
  modeling the channel but solving with layered binary codes; Müller
  (arXiv:2305.08631 / QiP 2024, DOI 10.1007/s11128-024-04395-w) — q=8, n=30000,
  FER=1% ⇒ f≈1.10–1.17 reference scale; complexity walls — Trifonov 2018 RS
  kernel O(q^l·l), Chen–Bai–Ma 2022 (DOI 10.1016/j.jiixd.2022.10.002) SCL
  (q²+q)·L·n·log n/2; Boutros & Soljanin (IEEE TComm 2023,
  DOI 10.1109/TCOMM.2023.3302135) — jitter modeling with standard codes.
- **New increment:** literature search found no published HD-QKD IR work injecting
  a delay/drift prior, timing-offset distribution, or non-uniform bin occupancy
  into a q-ary decoder's initial messages ⇒ the project's M2 ±1 delay prior is a
  genuine increment, and Step 2 below tests its transfer to a native-symbol setting.

## Impact Scope

- New: `openspec/changes/nbpolar-native-highdim-exploration/`
  (`proposal.md`, `design.md`, `tasks.md`; **no `specs/` delta — see below**).
- Read-only inputs only (never modified, never re-derived here): frozen artifacts under
  `results/` and `comparison_bench/outputs_comparison/`, plan/contract docs under
  `docs/nbpolar/`, sibling checkouts as read-only history reference.
- Explicitly untouched: `scripts/`, `comparison_bench/.../formal_ir/`,
  `prior_m2.py`, `src/`, `experiments/`, `tools/`, `results/`,
  existing `openspec/changes/*` and `openspec/changes/archive/*`.
- Exclusive write root for any future exploration output (not created by this change):
  `workspace/exploration/nbpolar-native-highdim/` — never `results/` or
  `comparison_bench/outputs_comparison/`. No SHG `.ttbin` reads at any step.

## Affected specs

**无 delta spec.** Reason: this is an exploration-only change that modifies no merged-spec
requirement. `openspec/specs/` carries no native-highdim requirement to amend, and no
frozen contract value moves. If a later change proposes decoder/interface/contract edits,
that change will carry its own delta spec; this proposal only records the exploration
questions, stop-loss rules, and ledger discipline.

## Exploration path (Step 0–3; design + prereg only, no runs authorized)

Conventions for every step: §Step ledger — sim and real FER live in separate ledgers;
a sim FER is never cited as a real FER. §Write scope — new files go only to the
exploration write root above. §Frozen box — N / K1 / K2 / P16 / w and every number in
§Frozen facts stay fixed. §Minimalism — AGENTS.md §5.7 applies (no checksum / atomic-write
/ retry-framework / over-validation / hardening beyond the concrete failure mode).

### Step 0 — channel survey: what does the existing error actually look like?

- Scientific question: is the residual channel (±1-dominated? heavy-tail? period-crossing?)
  of a type where preserving inter-level dependence could plausibly matter?
- Read-only inputs: already-derived per-block/per-frame tables and registries
  (frozen DEVELOPMENT artifacts); no `.ttbin` access.
- Design outputs (later, under separate authorization): error histogram, |Δ|
  distribution, bin-occupancy non-uniformity, period-crossing rate — all descriptive,
  Tier-X style, written only to the exploration write root.
- Success: a preregistered survey spec exists with metrics, binnings, and denominators
  fixed in advance. Stop-loss: if the survey spec cannot be written without new raw
  reads or without touching frozen artifacts, stop and return to planner.
- Not doing: no decoder, no prior change, no N/K/P/w move, no FER claim of any kind.

### Step 1 — small-q simulation screening (q ∈ {4, 8, 16}): native-symbol vs bit-plane binary

- Scientific question: does native-symbol decoding separate from bit-plane binary
  decomposition on FER–f (at matched rate/block-length/prior), i.e. is there a
  measurable signal worth scaling, or does Park–Barg ordering + good MSD already
  explain everything?
- Read-only inputs: synthetic channel family preregistered in the design (small q only;
  parameters frozen at prereg time per Tier-X rule; seeds frozen; no real data).
- Design outputs (later): paired FER–f curves per q, separation statistic with
  uncertainty, preregistered stop-loss line (e.g. no separation at small q ⇒ do not
  scale to d=1024; clear separation ⇒ proceed to Step 2/3 designs).
- Stop-loss is a design requirement, not a post-hoc judgment: the screening design must
  state the numeric no-go condition before any run.
- Not doing: no d=1024 simulation, no real-data FER, no sim→real generalization claim.

### Step 2 — transfer-prior injection: non-uniform init from the real transition matrix

- Scientific question: does initializing a (small-q, Step-1-compatible) decoder with the
  real-data transition matrix as non-uniform initial messages beat a uniform init —
  and is a negative recorded as a result, not discarded?
- Read-only inputs: the frozen M2 ±1 / transition-matrix finding as a **numerical
  reference only** (no prior-code change, no re-fit here); Step-1 screening envelope.
- Design outputs (later): uniform-vs-informed paired comparison with preregistered gain
  metric; negative-outcome recording rule (a clean zero/negative is kept evidence).
- Stop-loss: if the transfer design requires re-estimating the prior on EVAL data or
  touching RESERVE frames, stop — that would violate the DEVELOPMENT/confirmation
  boundary.
- Not doing: no M2 modification, no CAL change, no EVAL/RESERVE consumption.

### Step 3 — d=1024 paper-complexity adjudication + GF(32) split-dimension probe design

- Scientific question: even if Steps 0–2 look promising, does a native d=1024 decoder
  survive the complexity wall on paper (RS-kernel / SCL scaling above), and is a
  GF(32) split-dimension probe the right bounded next object?
- Read-only inputs: the cited complexity formulas as stated (no re-derivation claimed
  here); sibling GF(32) history as negative-result record.
- Design outputs (later): a one-page complexity adjudication (ops/memory vs block
  budget, with explicit assumptions) plus a bounded GF(32) probe envelope
  (what is asked, what would falsify it, what it cannot claim).
- Stop-loss: if the paper adjudication shows d=1024 native decoding exceeds the
  practical envelope by orders of magnitude with no credible reduction path, the
  recommendation is to stop scaling and record the negative — not to launch code.
- Not doing: no decoder implementation, no GF(32) graph work, no complexity-figure
  tuning to justify a preferred answer.

## Stage-3 gate status in this proposal: DEFERRED (押后)

The Stage-3 `taste` adjudication cap is a closed-form scalar bound
`cap = f_scalar · N · H_total` tied to existing frozen constants. Because λ is
per-row constant here, the comparison degenerates into a construction identity with
zero discriminative power. Reason to defer (not to abolish): running it now would
produce a verdict-shaped artifact that cannot discriminate any hypothesis. It returns
only if a future design restores discriminative power (non-constant λ or a
non-identical construction comparison), under its own freeze.

## Acceptance Criteria

- Proposal/design/tasks are internally consistent; every frozen number matches
  §Frozen facts verbatim; no frozen file outside this change directory is touched.
- Each Step has: read-only inputs, exploration-root-only outputs, success/stop-loss
  criteria, one answerable scientific question, and an explicit not-doing list.
- Sim/real ledger separation and Tier-X/Tier-Y division are stated and checkable.
- `tasks.md` assigns every task an agent role compatible with AGENTS.md §4
  (planner writes no production code; coder never self-accepts; reviewer edits no files).
- Memory triage is the closing task.

## Tasks

See `tasks.md` (T1–T9, all docs/plan/review; no execution authorized).

## Open questions for the user (need adjudication before any future run packet)

1. Is the small-q set {4, 8, 16} the right screening ladder, or should q=32 enter Step 1?
2. Should Step 1's stop-loss be a hard numeric FER–f separation threshold now, or a
   qualitative bar left to the future freeze?
3. Is GF(32) confirmed as the Step-3 split-dimension probe, or should another
   factorization be pre-allowed?
4. Does the user accept DEFERRED Stage-3 as stated, or require a paper-only
   discriminative-power note attached to this change?
