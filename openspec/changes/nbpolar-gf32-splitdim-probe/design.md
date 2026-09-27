# Design — nbpolar-gf32-splitdim-probe

Status: **draft (docs-only).** Provenance split (F9): sampling / channel /
arm-skeleton values below are **adapted from the Step-1/Step-1B freeze (F1–F8)**
of the archived exploration change — that freeze covers the **small-q
(q ∈ {4, 8, 16}) screening grid only**, does **not** define the split-dim
object, and does **not cover A1–A7**. The split-dim object is defined in D2a
and the Step-3 assumption set A1–A7 is added in D2b. Nothing here is
re-derived or varied.

---

## D1 — One question

**Q**: under the frozen F4 channel and F5–F8 sampling, does native GF32
split-dimension decoding (Arm A) show a measurable signal relative to the
soft-decision arm (Arm B) — i.e., are the per-seed outcome distributions
separated enough to justify further split-dim work?

Nothing else is measured — the probe is **FER-only**: it computes no f, no
entropy, and no efficiency term (F10; see the D2 K_sym/entropy row). No
threshold is declared claim-bearing; the probe
returns numbers and dispersion, and the go/no-go reading is a later,
separately reviewed judgment.

## D2 — Frozen probe parameters (skeleton adapted from Step-1 F1–F8; object = D2a, assumptions = D2b)

| Item | Value |
|------|-------|
| Channel (F4 formula) | `0.75 / 0.24 / 0.005 / 0.005` — formula inherited from Step-1 F4; **instantiated on the object alphabet q = 1024 (D2a)**: P(δ=0)=0.75, P(δ=+1)=0.24, P(δ=−1)=0.005, residual 0.005 uniform over the other q−3 = 1021 offsets, δ integer-domain on x |
| Block length (measurement) | `n_sym = 128` object symbols per block — the measurement length **argued in D2a** against A3's paper-table n = 32768 (small-q provenance: Step-1 F5) |
| Rate grid (F5) | `R ∈ {0.30, 0.40, 0.50, 0.60}` (0.3–0.6) |
| Design seed (F5) | `2026092400` |
| Run seeds (F6) | `2026092401 .. 2026092416` (16 seeds) × **64 blocks** each |
| Field per factor stage | GF(32) (q = 32), **poly37 / α = 2 — provenance: Phase-1 GF(32) algebra (`docs/nbpolar/STATE.md` §1 "GF(32) poly37/α2 … 17/17", `.workbuddy/queue/NBPOLAR-PHASE1-GF32-TRANSFORM/OPERATOR_RETURN.md:45`), NOT F3 (F10 correction: Step-1 F3 froze only GF(4)/GF(8)/GF(16) polynomials 0b111 / 0b1011 / 0b10011, α = 2)** |
| Arms (F11, exact) | **A** = native split-dimension decode: two per-factor GF(32) SC stages, read-only reuse of `comparison_bench.formal_ir.nbpolar` (F1). **B** = **Step-1B `B-soft`** — Gray bit-plane binary polar with exact soft-carrying MSD conditioning (`EXPLORATION_SUITE_REPORT.md` §11); the Step-1 **F2 `B-hard`** variant is **NOT used** (F2 contributes only the bit-plane / Gray / plane-order skeleton); plane order `0..r−1` = **0,1,2,3,4 (r = log2 32 = 5)**, reflected Gray labeling. Paired: identical blocks/seeds across arms |
| K_sym / entropy (F10) | K_sym for code construction: same set as F5 — **{38, 51, 64, 77}** (n_sym = 128 unchanged), re-derived at BT1 if the PI requires. **The entropy term H (H_d / H_δ at this probe's alphabet) is NOT frozen by F1–F8 (F5 covered q ∈ {4,8,16} only) and is NOT computed ⇒ this probe is FER-only: it reports no f and no efficiency** |

Parameters, models, and seeds **freeze at prereg time** and must not change
afterwards (PROBE_TIER). A rerun only to fix an execution error is allowed and
must be recorded in the single result record.

### D2a — Split-dim object definition: factorization + alphabet + length (F8)

**Freeze prerequisite**: BT1/`prereg.md` may not claim a *freeze* until this
object definition is written into it — unclear object ⇒ no freeze claim.

- **Factorization (A1)**: `d = 1024 = 32 × 32` over `GF(32) × GF(32)` — the
  **baseline** row of the CLOSED pre-allowed set {GF(32) = 32×32,
  GF(16)×GF(64), GF(8)×GF(128)} (`EXPLORATION_SUITE_REPORT.md`:151–152;
  step-3 envelope §6, closed at design time, no post-hoc additions). This
  probe runs the GF(32) baseline row only.
- **Object alphabet**: a block symbol is an object `x ∈ {0 … 1023}`
  (d = 1024), split mixed-radix `x = 32·a + b` with `a = ⌊x/32⌋`,
  `b = x mod 32`, `a, b ∈ GF(32)` (poly37/α2, Phase-1 provenance per D2).
  The coordinate map is a BT1 freeze field: stated here as the default and
  not changeable after prereg freeze.
- **Decoded alphabet per factor stage**: each stage is decoded over
  **GF(32) (q = 32)** — the alphabet Arm A's SC and Arm B's Gray bit-planes
  see (r = log2 32 = **5** planes). Arm B's planes are **GF(32) symbol
  bit-planes, not a 10-bit d = 1024 decomposition**.
- **Channel domain**: F4's numbers act on the **object alphabet (q = 1024)**:
  P(δ=0)=0.75, P(δ=+1)=0.24, P(δ=−1)=0.005, residual 0.005 uniform over the
  other q−3 = 1021 offsets, δ = ±1 in the integer domain of x. Under
  `x = 32a + b` this puts most ±1 mass on b and reaches a only via
  carry/borrow (b = 31 / b = 0) — that uneven error split across dimensions
  is exactly the structure a split-dimension decode is probed on; a
  per-stage GF(32) channel instantiation would make the split vacuous and is
  a different, non-adjudicated variant (STOP if encountered).
- **Length (A3 reconciliation — explicit argument for n_sym = 128)**: probe
  block = **n_sym = 128 object symbols**; both factor stages are decoded per
  block; block failure = either stage fails ground-truth comparison (block
  error rate, F8-style).
  1. A3 is the Step-3 *paper complexity table* input ("Block length n used
     in the SCL formula per row", step-3 §3/§5; report :154) — a paper-only
     ops/memory assumption under A4–A7, never executed, and not a
     measurement-unit definition.
  2. D1 asks whether the split-dim object **preserves the Step-1 separation
     signal**; that signal was defined and measured on F5/F6 blocks of
     n_sym = 128 (F8: FER = block error rate over 16 × 64 paired blocks).
     Keeping the block unit keeps the paired comparison same-unit with the
     reference signal.
  3. Cost class: ×256 block-length scaling (128 → 32768) would multiply wall
     by roughly two orders of magnitude (order-of-magnitude estimate from
     Step-1's 24,576 n_sym = 128 decodes in 169.4 s — an estimate, not a
     measurement), turning the proposal's "cheap, reversible" probe into an
     expensive run. That is a scientific scope change requiring PI
     adjudication, not a docs decision.
  4. Therefore A3's **n = 32768 is recorded verbatim as the paper
     assumption and is not this probe's measurement length**. If the PI
     prefers A3 alignment, the length must be adjudicated **before** BT1
     freezes the prereg, with the chosen value written explicitly; until this
     D2a object definition appears in the prereg, no freeze may be claimed.

### D2b — Step-3 assumption set A1–A7 (added coverage; F1–F8 does not cover these)

Source: `step3-complexity-adjudication-and-probe-envelope.md` §3/§6 and
`EXPLORATION_SUITE_REPORT.md`:151–158. Recorded as inheritance; none is
re-derived, tuned, or moved after any reading (step-3 §9/§10):

| ID | Assumption (summary of the archived verbatim) | Role in this probe |
|----|-----------------------------------------------|--------------------|
| A1 | Alphabet / factorization per row: full-native q = 1024 row; probe rows = CLOSED pre-allowed set {GF(32) = 32×32 baseline, GF(16)×GF(64), GF(8)×GF(128)}, product 1024 | defines the split-dim object (D2a) |
| A2 | SCL list L = 8 full-native / **L = 1 probe rows**; RS-kernel width l = 2; iterations N/A | probe rows decode with L = 1 |
| A3 | Block length **n = 32768 symbols per factor stage** (split rows sum over both fields) | paper-table assumption; probe measurement length argued as n_sym = 128 in D2a |
| A4 | Memory model: L·q·n float32 values, split rows sum over fields | recorded only (paper table) |
| A5 | Budget ≈ 20 s/decode (**C4 INFERRED** from G2/G3 wall telemetry — never a frozen constant) + machine rate 1e9 float ops/s effective single-thread | cost reference for A7 |
| A6 | Reduction paths: only L = 1 admitted for probe rows, nothing else credited | recorded only |
| A7 | **Probe-cost bound ≤ 4× the A5 decode budget (≤ ~80 s)** — fixed before the reading, never tuned after | per-decode cost bound; the probe reports wall time against it, honestly, with no tuning (D5) |

### D2c — Sibling-negative distinction record: V7R3 / V54 (step-3 §7; GF32-BT3-COND-30)

Source (frozen constraint, read-only, never reused):
`openspec/changes/archive/2026-09-23-nbpolar-native-highdim-exploration/step3-complexity-adjudication-and-probe-envelope.md`
§7 "Sibling-negative constraints" (:187–196):

- **V7R3** — GF(32)×GF(32) multilayer: on record as a wrong route.
  Constraint: any future probe touching a multilayer structure in this shape
  must distinguish itself from V7R3 **in its own freeze**; V7R3 code is not
  reused and no reuse path is opened.
- **V54** — Q_SUB=32 production shell: on record as a wrong route.
  Constraint: a Q_SUB=32-shaped probe envelope must distinguish itself from
  the V54 shell **in its own freeze**; the V54 shell is not reused and no
  reuse path is opened.

Distinction of THIS probe (Tier-X, non-claim; recorded docs-only before BT3):

| Negative | Wrong-route shape | How this probe is distinguished | Reuse |
|----------|-------------------|----------------------------------|-------|
| V7R3 | GF(32)×GF(32) **multilayer** structure | Arm A is a fixed **two-stage, single-level** per-factor GF(32) SC decode — exactly two stages, one per factor of the closed 32×32 row (D2a); block failure = **either stage** fails ground-truth (F8-style). No multilayer/recursive stacking beyond the two factors and no layer-growth path: the factorization set is CLOSED at design time (D2a / step-3 §6). The output is per-seed FER / ΔFER numbers and dispersion only — no token, no claim, never promoted to a d = 1024 native-performance claim (D1/D6) | V7R3 code not reused; Arm A reuses only read-only `comparison_bench.formal_ir.nbpolar` (F1/D2); no V7R3 reuse path opened |
| V54 | Q_SUB=32 **production shell** (system-level q substitution) | q = 32 appears **only as the per-stage decoded alphabet** inside a synthetic probe (D2a); the channel acts on the **q = 1024 object alphabet**, so q = 32 is not a system/configuration substitution parameter. No production shell, no Q_SUB config/CLI surface, no write outside the probe root (D7); Tier-X, one synthetic `results.json` | V54 shell not reused; no V54 reuse path opened |

**Freeze-piece reference (prereg untouched — GF32-BT3-COND-30):** the
`prereg.md` P line was frozen at BT1 and is **not edited** by this docs fix.
The P line already incorporates the object/assumption definitions by
reference to this design ("design D2a", "recorded as inheritance per design
D2b"); D2c is a section of the same design document, so the V7R3/V54
distinction enters the frozen piece **by that existing design reference**.
Caveat: step-3 §7 literally asks for the distinction "in its own freeze". If
the main thread judges that an explicit V7R3/V54 citation inside the P line
is required, that is a **refreeze decision for the main thread** — out of
this docs-only scope; the prereg P line stays untouched meanwhile.

## D3 — Three-line prereg

Exactly three lines, per `docs/nbpolar/PROBE_TIER.md`:

```
Q: does native GF32 split-dim (A) separate from soft-decision (B) under frozen F4, seeds 2026092401..16, R 0.3–0.6?
P: object d=1024=32×32 (D2a), per-stage GF(32) poly37/α2, ch F4@q=1024:0.75/0.24/0.005/0.005, n_sym=128 (D2a argument vs A3=32768), A1–A7 as D2b, R∈{0.30,0.40,0.50,0.60}, seeds 2026092401..16 ×64 blocks, arms A(native split-dim)/B(Step-1B B-soft, planes 0..4), design seed 2026092400, sampling adapted from Step-1 F4–F8 (small-q; does not define object)
C: <exact command — filled only after verbatim authorization>
```

The command line stays as an explicit placeholder until the authorization gate
(BT3/BT4); no command is implied by this design document. **After BT3 (verbatim
authorization) the exact command is backfilled into the prereg/packet, and the
command string actually executed is recorded verbatim in the `results.json`
provenance (D4) — the backfill happens only post-BT3 and is logged as such.**

## D4 — Single result record

One file, `workspace/probes/gf32-splitdim-signal/results.json`:

- **per-seed values** for each arm and rate, **and the per-seed paired
  ΔFER = FER_B − FER_A** (definition verbatim from the frozen prereg `METRIC`
  line; design and TASK_PACKET follow the prereg — the prereg is not edited);
- aggregate **mean / sample-std / range** (sample-std, n−1 denominator) for
  each arm **and for ΔFER** (same three statistics, same prereg `METRIC`
  wording);
- **wall time** and **peak RSS** for the probe process;
- one `status` field (`ok` or honest failure state — status values are never
  silently promoted to `ok`);
- the exact prereg + parameters echoed for provenance.

**Completeness criterion (GF32-BT3-COND-31 — decision recorded):** ΔFER
**IS** included in the `results.json` completeness check under the focused
review (D6). Completeness = every field frozen by the prereg `METRIC` line is
present: per-seed FER per arm **and** per-seed paired ΔFER, plus
mean / sample-std (n−1) / range for arms **and** ΔFER, together with wall
time, peak RSS, `status`, echoed prereg/parameters, the exact executed
command, the execution/rerun log and counters. A missing ΔFER field is an
**incomplete record, reported as such** — never silently dropped, and never
synthesized after the reading.

No per-run directories, no secondary summaries, no incremental appends — one
record at the end (PROBE_TIER: "ONE result record").

## D5 — Stop rule: end honestly

One shot. On completion or on failure, write the single `results.json` with
what actually happened. Forbidden: rerun to improve a number, seed/model change
after freeze, tuning against the observed output, retry loops, or suppressing
a bad run. An execution-error rerun is permitted only as a recorded correction,
never as a second attempt at a better result.

## D6 — Review mode: focused numerical review only

The eventual run is reviewed only by the focused numerical review defined in
PROBE_TIER (commands, completeness, arithmetic, truth isolation, write-scope)
instead of Pre-EXECUTE/Pre-RESULT. There is no candidate/accepted token, no
attempt counting, and no promotion of previously accepted evidence — this probe
can never strengthen a claim.

## D7 — Write scope and isolation

- Output root: **`workspace/probes/gf32-splitdim-signal/`** only (prereg,
  packet copy, `results.json`).
- Forbidden writes: anywhere else — `results/`,
  `comparison_bench/outputs_comparison/`, archive, G4 artifacts, frozen
  baseline (`src/`, `experiments/`, `tools/`), `docs/nbpolar/STATE.md`.
- Forbidden reads/access: any artifact or real-data path; synthetic data only.
- No decision-log / index / project-memory update per probe (batched at
  milestone).

## D8 — Authorization gate

The packet carries **`authorizations: []`**. The run (BT4) requires the PI's
**verbatim** authorization text pasted in full. That authorization is **NOT
granted at the time this design is written**; absent it, BT4–BT6 remain
NOT AUTHORIZED and no command may be executed.

## Non-goals of this design

No claim thresholds, no power analysis, no CI machinery beyond mean/std/range,
no framework or packaging beyond the PROBE_TIER three-line + one-JSON pattern
(research-code engineering policy: simplest correct implementation).
