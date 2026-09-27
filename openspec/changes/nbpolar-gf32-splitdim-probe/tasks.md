# Tasks — nbpolar-gf32-splitdim-probe

Status: **draft (docs-only skeleton).** Ordered BT1→BT7.
BT1–BT2 are authoring tasks executable now. BT3 is the PI gate.
**BT4–BT6 are NOT AUTHORIZED** — the required verbatim authorization is not
granted. Packet state: `authorizations: []`.

---

## BT1 — Author the 3-line prereg

Write the prereg (design D3) under this change: question; the **split-dim
object definition verbatim from design D2a** (factorization d = 1024 = 32×32,
closed-set baseline, mixed-radix map `x = 32a + b`, per-stage decoded alphabet
GF(32), channel domain q = 1024, **n_sym = 128 with the D2a argument vs A3's
paper-table n = 32768**); the Step-3 assumptions **A1–A7** as recorded in D2b;
exact frozen parameters (F4 channel 0.75/0.24/0.005/0.005, R 0.30–0.60, seeds
2026092401..2026092416 ×64 blocks, arms A = native split-dim / **B =
Step-1B `B-soft`**, plane order 0..4, design seed 2026092400; sampling and
channel inputs **adapted from** Step-1 F4–F8 — F1–F8 is the small-q screening
freeze and does not define this object); and the command line as an explicit
`<backfilled after BT3 — then recorded verbatim in results.json>` placeholder
(design D3: backfilled only after BT3). **Freeze-claim condition (F8): the
prereg may state "frozen/parameters frozen at this point" only if the D2a
object definition and A1–A7 are present in it; otherwise BT1 returns
unresolved and no freeze may be claimed.**

- Needs user authorization: **NO** (docs authoring; no run).

## BT2 — Author the packet skeleton (format follows AGENTS.md §10.1 task-packet conventions; **tier = Tier-X**) with `authorizations: []`

Create the probe packet skeleton — AGENTS.md §10.1 packet format, **tier =
Tier-X** per `PROBE_TIER` (this is explicitly **not** a Tier-Y packet):
input set, arms, exact output path
`workspace/probes/gf32-splitdim-signal/results.json`, result schema (per-seed
values + mean / sample-std / range + wall + RSS), stop rule D5, review mode D6,
write scope D7, and **`authorizations: []`**.

- Needs user authorization: **NO** (skeleton; authorization list empty by construction).

## BT3 — PI verbatim authorization gate

The PI pastes the **full verbatim authorization text** (required for BT4) and
confirms the frozen prereg parameters. Absent this, execution stays blocked.

- Needs user authorization: **PI decision required — NOT granted at document creation.**

## BT4 — Execute the probe (Tier-X run)

Run the exact prereg command; outputs confined to
`workspace/probes/gf32-splitdim-signal/`.

- Needs user authorization: **NOT AUTHORIZED** (blocked on BT3; verbatim
  authorization required and not granted now).

## BT5 — Write the single `results.json`

One record only: per-seed values, mean / sample-std / range, wall, RSS, status,
echoed prereg (design D4). If the run failed, write the honest failure state —
no status promotion to `ok`.

- Needs user authorization: **NOT AUTHORIZED** (depends on BT4).

## BT6 — Focused numerical review

Review commands, completeness, arithmetic, truth isolation, and write-scope
(design D6). Non-claim: no thresholds, no verdict, no attempt token.

- Needs user authorization: **NOT AUTHORIZED** (no run exists to review until BT4/BT5 complete).

## BT7 — Milestone-batched memory/index update

Decision-log / index / project-memory entry batched at the next milestone
(PROBE_TIER forbids per-probe updates). Not executed as part of this change.

- Needs user authorization: **deferred to milestone; not part of this change.**

---

## Standing unauthorized items (O-list)

- O1 Any execution before verbatim PI authorization (BT3) — including smoke runs.
- O2 Any write outside `workspace/probes/gf32-splitdim-signal/`; any read of
   artifact or real-data paths.
- O3 Claim-bearing thresholds, pass/fail verdicts, FER/efficiency/secret-key claims.
- O4 Rerun, seed/model change, or tuning after prereg freeze (except a recorded
   execution-error correction per D5).
- O5 Archive, G4, frozen baseline (`src/`, `experiments/`, `tools/`),
   `results/`, `comparison_bench/outputs_comparison/`, and
   `docs/nbpolar/STATE.md` modifications; git push; change archival.
- O6 Per-probe decision-log / index / project-memory updates.
