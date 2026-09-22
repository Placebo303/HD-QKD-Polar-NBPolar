# Design: native high-dimensional exploration (exploration-only)

No implementation or execution is authorized by this change. All "outputs" below are
**design artifacts to be written later under separate authorization**; this file fixes
their shapes, ledgers, and stop rules in advance.

## D1 — Exploration architecture: three ledgers, one write root

- Ledgers: (L1) frozen real-data record (read-only: `results/`,
  `comparison_bench/outputs_comparison/`, `docs/nbpolar/` registries);
  (L2) future synthetic/sim ledger; (L3) future descriptive-survey ledger.
  L2/L3 values are never merged into, compared numerically against, or cited as L1 FER.
- Write root (future only): `workspace/exploration/nbpolar-native-highdim/<step>/`
  containing at most `prereg.md`, `results.json`, `notes.md`.
  Forbidden writes: `results/`, `comparison_bench/outputs_comparison/`,
  any frozen directory, any `.ttbin` path, any existing change/archive directory.
- Tier mapping: Steps 0–2 future runs are Tier-X probes (prereg → one result record →
  focused numerical review; no candidate/accepted token, no status change, per
  AGENTS.md §10.4). Any claim-bearing gate is Tier-Y and needs its own change,
  freeze, independent Pre-EXECUTE/Pre-RESULT reviews, and explicit user authorization.

## D2 — Step-0 survey design (descriptive, Tier-X-shaped)

- Prereg fixes: which frozen derived tables are read (by path), exact histogram bins
  for error Δ, |Δ| denominator (per symbol / per frame), bin-occupancy normalization,
  period-crossing event definition.
- Result record: counts + rates with denominators and seed/path provenance; no model
  fit, no decoder input reuse claim.
- Checkable stop rule: prereg incomplete or requiring new raw reads ⇒ stop, return
  to planner. No FER object is produced at this step by construction.

## D3 — Step-1 screening design (q ∈ {4, 8, 16}, native vs bit-plane)

- Arms (matched on rate, block length, channel seed, prior family):
  arm A native-symbol decoder (small-q reference algorithm, to be named in the future
  freeze — not selected here); arm B bit-plane binary decomposition with ordered
  MSD-style conditioning (Park–Barg structure respected, not BICM-naive).
- Metric: paired FER–f at matched operating points with uncertainty (per-seed values +
  mean/sample-std/range in the future `results.json`); the design states the numeric
  no-go condition (no separation across q ⇒ do not scale; separation ⇒ Step 2/3
  designs may be frozen next).
- Sim/real firewall: screening parameters, models, and seeds freeze at prereg;
  a rerun to fix an execution error is allowed once and recorded; no threshold may be
  tuned post-hoc; no sim FER enters any real-data table or claim.
- Explicitly undecided here: the reference decoder algorithm, list sizes, iteration
  caps, and the numeric stop-loss constant — all deferred to the future freeze so this
  change stays execution-free.

## D4 — Step-2 transfer-prior design (uniform vs informed init)

- Informed init = the frozen real-data transition structure (M2 ±1 finding) used as a
  **fixed numerical reference** for non-uniform initial messages in the Step-1
  small-q envelope; uniform init is the control. Both arms share seeds/channel draws.
- Gain metric (preregistered): paired decoding-success / NLL difference with
  uncertainty; negative or zero gain is a kept result (`notes.md` records it as
  evidence, not as a failed run to discard).
- Boundary guard: the design must not consume EVAL blocks, RESERVE frames, or re-fit
  on confirmation-boundary data; violation ⇒ stop. No `prior_m2.py` or CAL change.

## D5 — Step-3 complexity adjudication + GF(32) probe envelope

- Paper adjudication inputs (as cited, not re-derived here): Trifonov-2018 RS-kernel
  O(q^l·l); Chen–Bai–Ma-2022 SCL (q²+q)·L·n·log n/2; candidate block budget from the
  frozen point (N=32768 symbols, d=1024 alphabet).
- Adjudication output: one page — assumed (q, L, l / kernel width, iterations),
  arithmetic ops + memory vs budget, and the explicit assumption list; conclusion is
  one of SCALE / PROBE-ONLY (GF(32) split-dimension) / STOP, each with its falsifier.
- GF(32) probe envelope: asks only whether the split-dimension object preserves the
  Step-1 separation signal at bounded cost; it cannot claim d=1024 native performance.
  Sibling GF(32) negatives (V7R3 multilayer, V54 shell, V13R3 q=1024) stay on record
  as constraints, not as reusable code.

## D6 — Stage-3 deferral (design rationale)

`cap = f_scalar · N · H_total` with per-row-constant λ collapses the taste comparison
to a construction identity: both sides differ only by the frozen arithmetic, so the
gate's output carries zero bits of hypothesis information. Deferral is the minimal
action (no gate edit, no constant move). Re-entry condition: a future design with
non-constant λ or a non-identical construction comparison, under its own freeze.

## D7 — Minimalism (§5.7) and risk register

- Minimalism: plain `prereg.md` / `results.json` / `notes.md`; no checksums, no atomic
  writes, no retry frameworks, no schema validators, no caching layers, no hardening
  beyond the concrete failure modes named here (wrong-ledger citation, frozen-file
  touch, raw-data read). Each future packet names its single realistic failure mode
  or omits the mechanism.
- R1: small-q separation may not transfer upward (Park–Barg ordering cuts both ways) —
  Step 3 exists for this. R2: informed-init gain may be prior-fitting in disguise —
  Step-2 boundary guard exists for this. R3: survey descriptives may tempt decoder
  conclusions — Step 0 produces no FER object. R4: complexity numbers are
  assumption-sensitive — D5 forces the assumption list into the artifact.
- Frozen-box recheck (reviewer-verifiable): N=32768, K1=319, K2=6492, P16, w=200
  CIRCULAR, skip=702, frame_pairs=256, floor 1e-15, chunk 512, bin 200 ps,
  f(6811)=1.2747449, 34,119 / 327,743 bits, undetected 0/42, EVAL 14 blocks,
  RESERVE 29/99 frames — none moved by this change.
