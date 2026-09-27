# Change Proposal: nbpolar-gf32-splitdim-probe

Status: **draft (docs-only skeleton; NO execution authorization)**
Date opened: 2026-09-23
Tier: **Tier-X style probe** per `docs/nbpolar/PROBE_TIER.md` — but this change
grants **no** authorization; it prepares the packet only.

---

## Problem

The archived exploration change `nbpolar-native-highdim-exploration` closed with
a **PROBE-ONLY** verdict for Step 3 (`step3-complexity-adjudication-and-probe-envelope.md`):
the split-dimension (split-dim) GF32 route is admitted for a bounded synthetic
signal probe, not for integration or real data. No probe packet, prereg, or
output directory exists yet, so the one question the verdict permits — *does
native split-dim decoding show a signal against the soft-decision arm under the
frozen F4 channel and the Step-3 A1–A7 probe envelope?* — cannot be run
reproducibly.

## Why

- **One bounded question, cheap, reversible**: a synthetic-only probe under
  `workspace/probes/gf32-splitdim-signal/` cannot touch artifacts, frozen
  outputs, or claims, and is the shortest scientifically valid path to a
  go/no-go on split-dim before any integration work.
- **Reproducibility**: freezing channel, seeds, block counts, arms, and the
  exact result schema in a 3-line prereg (PROBE_TIER) removes post-hoc
  parameter drift.
- **Non-self-granting**: the packet is built with `authorizations: []`; the run
  requires a separate verbatim authorization that is **not granted now**.

## Scope — IN

1. **Packet + prereg authoring (docs only)**: 3-line prereg and a Tier-X
   packet skeleton with `authorizations: []`.
2. **Corrected inheritance split (F9)**: F1–F8 is the **Step-1 small-q
   (q ∈ {4, 8, 16}) screening** freeze. It does **not** define the split-dim
   object and does **not cover A1–A7**. Therefore:
   - **Split-dim object assumptions A1–A7** (Step-3 envelope; enumerated in
     `design.md` D2b): **A1** factorization — closed pre-allowed set
     {GF(32) = 32×32 baseline, GF(16)×GF(64), GF(8)×GF(128)}, product 1024;
     **A3** paper-table block length n = 32768 symbols per factor stage
     (probe measurement length explicitly argued in `design.md` D2a);
     **A7** probe-cost bound ≤ 4× A5 decode budget (≤ ~80 s); plus A2 (L=1,
     kernel width l=2), A4 (memory model L·q·n float32 summed over fields),
     A5 (~20 s/decode, C4 INFERRED; 1e9 float ops/s), A6 (only L=1
     reduction paths admitted for probe rows).
   - **Sampling/channel/arm inputs adapted from Step-1 F4–F8**
     (provenance-labeled; NOT a claim that F1–F8 covered this probe): F4
     channel **0.75 / 0.24 / 0.005 / 0.005**; `n_sym = 128`; rate grid
     **R ∈ 0.30–0.60**; **16 seeds 2026092401..2026092416 × 64 blocks**;
     design seed 2026092400.
3. **Split-dim object definition written into BT1 (F8)**: factorization
   (d = 1024 = 32×32), decoded-object alphabet (per-factor GF(32)), and block
   length (`n_sym = 128`, argued vs A3 n = 32768) per `design.md` D2a. **If
   the object definition is not in the prereg, BT1 may not claim a freeze.**
4. **Two arms (F11, exact implementations)**: **Arm A** = native q-ary
   split-dimension decode (two per-factor GF(32) SC stages, read-only reuse of
   `comparison_bench.formal_ir.nbpolar`); **Arm B** = **Step-1B `B-soft`**
   (exact soft-carrying MSD on Gray bit-planes) — the Step-1 F2 **hard**-
   conditioning variant (`B-hard`) is **not** used; F2 contributes only the
   bit-plane / Gray / plane-order skeleton, plane order `0..r−1` with
   **r = log2 32 = 5 planes per GF(32)**. Arms paired on identical
   blocks/seeds.
5. **Single result artifact**: one `results.json` with per-seed values and
   **mean / sample-std / range**, plus **wall time and RSS**.
6. **Stop rule**: end honestly — one shot, report what happened; no rerun, no
   seed change, no tuning (PROBE_TIER).
7. **Focused numerical review** (commands, completeness, arithmetic, truth
   isolation, write-scope) as the only review mode for the eventual run.

## Scope — OUT (explicit non-goals)

- **Execution of the probe.** This change does not authorize any run. The
  required verbatim authorization is **NOT granted now** and must be pasted in
  full by the PI before task BT4.
- Any artifact or real-data access; any write outside
  `workspace/probes/gf32-splitdim-signal/`.
- Claim-bearing thresholds, pass/fail verdicts, or FER/efficiency claims —
  Tier-X probes are non-claim by rule.
- Integration of split-dim into the benchmark layer, Stage-3, R3, real-data
  acquisition, or archive/G4/frozen/STATE changes.
- Per-probe decision-log / index / project-memory updates (batched at
  milestones per PROBE_TIER).

## Affected specs

- **Merged specs under `openspec/specs/` (they DO exist; READ-ONLY; no delta
  added by this change)**: `final-ir-method-selection`, `formal-ir-methods`,
  `nbpolar-prior-rebaseline`. Inherited unchanged as binding constraints:
  `openspec/specs/nbpolar-prior-rebaseline/spec.md` §validation gates
  (:61–70 — no FER/efficiency/qualification claim SHALL precede G1 + G2 + G3 +
  G4 + the Stage-3 measurement set; S9 SHALL never be cited as FER/efficiency
  evidence) and §decoder and verification boundary (:53–59 — Toeplitz tag,
  disclosure counting, and `undetected` isolation SHALL remain unchanged).
  This change adds **no** delta spec to any merged spec.
- **Inherited (read-only)**: Step-1 F1–F8 (small-q screening) freeze facts,
  the Step-1B `B-soft` arm definition, and the Step-3 **A1–A7** assumption
  envelope + PROBE-ONLY verdict from
  `openspec/changes/archive/2026-09-23-nbpolar-native-highdim-exploration/`;
  `docs/nbpolar/PROBE_TIER.md` procedure.
- **New artifacts**: `proposal.md`, `design.md`, `tasks.md` in this directory,
  plus (after PI authorization, not now) the prereg and packet under this
  change and outputs confined to `workspace/probes/gf32-splitdim-signal/`.

## Authorization state

`authorizations: []` — **empty**. Verbatim authorization required for BT4 and
not granted at document creation time.
