# Exploration index: native high-dimensional error correction (docs-only navigation map — authorizes nothing)

## §0 Status

- `EXPLORATION_ONLY / DOCS_ONLY` — this file is a **navigation map** over the
  exploration change. It **authorizes no code, no run, no freeze change, no
  frozen-constant change, no data access, no Tier-X probe run, and no Tier-Y
  decision gate**.
- Parent scope: `openspec/changes/nbpolar-native-highdim-exploration/`
  (proposal + design + tasks + step artifacts + this index + the OQ4
  `stage3-deferral-discriminative-power-note.md`).
- Any future run needs its own freeze document plus separate verbatim user
  authorization per AGENTS.md §10.1–10.4. Nothing here satisfies that
  requirement.
- Minimalism (AGENTS.md §5.7): plain markdown only. No code, no checksums, no
  atomic writes, no schema validators, no retry frameworks, no defensive
  machinery (see §4).

## §1 Steps ↔ designs map

| Step | Scientific question (one line) | Design artifact | Task | Proposal / design anchor |
|---|---|---|---|---|
| Step 0 | Is the residual channel (±1-dominated? heavy-tail? period-crossing?) of a type where preserving inter-level dependence could plausibly matter? | `step0-survey-prereg-skeleton.md` | T1, accepted 2026-09-23 | Proposal §Step 0 + design §D2 |
| Step 1 | Does native-symbol decoding separate from bit-plane binary decomposition on FER–f at matched rate/block-length/prior, or does Park–Barg ordering + good MSD already explain everything? | `step1-screening-design.md` | T3, accepted 2026-09-23 | Proposal §Step 1 + design §D3 |
| Step 2 | Does initializing a small-q decoder with the real-data transition matrix as non-uniform initial messages beat a uniform init, with a negative recorded as a result? | `step2-transfer-prior-design.md` | T5, accepted 2026-09-23 | Proposal §Step 2 + design §D4 |
| Step 3 | Does a native d=1024 decoder survive the complexity wall on paper, and is a split-dimension probe (GF(32) baseline) the right bounded next object? | `step3-complexity-adjudication-and-probe-envelope.md` | T6, accepted 2026-09-23 | Proposal §Step 3 + design §D5 |
| Stage-3 | Deferred gate: the Stage-3 cap comparison degenerates into a construction identity with zero discriminative power — recorded, not run. | `stage3-deferral-discriminative-power-note.md` (OQ4 note, this task) | T7, accepted 2026-09-23 | Proposal §Stage-3 + design §D6 |

## §2 Future write-root map

- Future root (not created by this change): `workspace/exploration/nbpolar-native-highdim/<step>/`
  with `step0/`, `step1/`, `step2/`, `step3/` (Step-3 paper-only, tier-N/A) —
  each holding at most `prereg.md` / `results.json` / `notes.md`.
- Addendum root (envelope delta, recorded in the addendum packet):
  `workspace/exploration/nbpolar-native-highdim/step0-m6-addendum/` — separate Tier-X
  probe id completing Step-0's deferred M6 occupancy metric; the completed `step0/`
  root stays read-only.
- None of these directories exists or is created by this change.
- Each future run needs its own freeze plus verbatim user authorization
  (AGENTS.md §10.1–10.4).
- Tier division per AGENTS.md §10.4: Steps 0–2 future runs are Tier-X probes
  (prereg → one result record → focused numerical review; no
  candidate/accepted token, no status change); any claim-bearing gate is
  Tier-Y (own change, freeze, independent Pre-EXECUTE/Pre-RESULT reviews,
  explicit user authorization).
- OPEN ITEM (flag only, do not fix — fixing would touch repo-root `.gitignore`,
  outside this change's scope): `workspace/exploration/` currently falls under
  the `.gitignore` `workspace/*` pattern (only `workspace/probes/*` entries are
  negated), so a future packet must decide probe-record durability (gitignore
  negation vs worktree-only + decision-log record) — main-thread decision at
  the future packet.

## §3 Ledger schema L1/L2/L3 (from design §D1)

- L1 — frozen real-data record (read-only: `results/`,
  `comparison_bench/outputs_comparison/`, `docs/nbpolar/` registries).
- L2 — future synthetic/sim ledger.
- L3 — future descriptive-survey ledger.
- Rule (verbatim from design §D1): L2/L3 values are never merged into,
  compared numerically against, or cited as L1 FER.

## §4 §5.7 minimalism checklist (from design §D7)

- Plain `prereg.md` / `results.json` / `notes.md`; no checksums, no atomic
  writes, no retry frameworks, no schema validators, no caching layers, no
  hardening beyond the named concrete failure modes (wrong-ledger citation,
  frozen-file touch, raw-data read, post-hoc tuning).
- Each future packet names its single realistic failure mode or omits the
  mechanism.

## §5 Frozen-number recheck table (verbatim provenance; unchanged by this change)

| # | Constant | Value | Unchanged by this change |
|---|---|---|---|
| 1 | d | 1024 | unchanged |
| 2 | N | 32768 (=128 frames × 256 pairs) | unchanged |
| 3 | K1 | 319 | unchanged |
| 4 | K2 | 6492 | unchanged |
| 5 | Construction | P16 | unchanged |
| 6 | W_P / W_S / MOD / skip | 200 / 500 / CIRCULAR / 702 | unchanged |
| 7 | frame_pairs | 256 | unchanged |
| 8 | floor | 1e-15 | unchanged |
| 9 | chunk | 512 | unchanged |
| 10 | bin | 200 ps | unchanged |
| 11 | f(6811) | 1.2747449 | unchanged |
| 12 | key_dependent_bits | 34,119 (=5·(K1+K2)+64, per-row constant) | unchanged |
| 13 | public_control_bits | 327,743 | unchanged |
| 14 | undetected | 0/42 isolated (never merged into success/FER) | unchanged |
| 15 | EVAL | 14 blocks (2398–4189) | unchanged |
| 16 | RESERVE | SHG_1 29 / SHG_2 99 frames | unchanged |
| 17 | Block rule | never pad/reuse/shrink, COMPLETE-BLOCKS-ONLY else INSUFFICIENT | unchanged |
| 18 | DEVELOPMENT ≠ confirmation | already-decoded segments = DEVELOPMENT data, never a confirmation sample | unchanged |

(No number in this table is moved by this change; all values match proposal
§Frozen facts verbatim. They are provenance context, not results.)

## §6 OQ adjudication record (2026-09-23; recorded, not re-opened)

- OQ1 — q∈{4,8,16} locked; q=32 not pre-allowed. Applied: tasks.md OQ
  section; step1 §0; design D3.
- OQ2 — qualitative bar now; hard numeric threshold at the future freeze.
  Applied: tasks.md OQ section; step1 §0; design D3; proposal §Step 1.
- OQ3 — other factorizations pre-allowed; GF(32) baseline. Applied: tasks.md
  OQ section; step3 §0/§6; design D5; proposal §Step 3.
- OQ4 — Stage-3 deferred + this one-page note. Applied: tasks.md OQ section;
  proposal §Stage-3 + adjudication note; design D6; this change via T7
  (`stage3-deferral-discriminative-power-note.md`).

## §7 Task status snapshot (descriptive; this file flips no checkbox)

- T1–T9 ALL COMPLETE 2026-09-23: T1/T3/T5/T6/T7 accepted, T2/T4/T8 review gates PASS, T9 memory triage recorded.
- Suite execution (2026-09-23, under the user's full-suite instruction recorded verbatim in each packet's STATUS.yaml): see §8 below.

## §8 Suite execution packets (2026-09-23; Tier-X, non-claim)

Shared authorization: user instruction 「我的意思是做完全套本项目的方向探索部分」
(2026-09-23), bound per packet in each `AUTHORIZATION_PROMPT.md` / `STATUS.yaml`
(own freeze + focused numerical review + main-thread adjudication per probe; synthetic
only; no real data; no Tier-Y; no frozen-constant change).

| Probe | Root | Status 2026-09-23 |
|---|---|---|
| Step-0 channel survey | `step0/` | **COMPLETE_DESCRIPTIVE** `NBPOLAR_EXPLORATION_STEP0_SURVEY_COMPLETE_DESCRIPTIVE` — ±1-dominated residual (\|Δ\|≤1 incl. zero bin = 1.0000 — the established `delta_mass_le1` fact, NOT the stored key `mass_le1` = 0.24617866847826086 which is \|Δ\|=1 only, per audit D1; +1/−1 ≈ 108×); period-crossing 45/200,192; wrap closure re-verified; focused review PASS_WITH_COMMENTS |
| Step-0 M6 occupancy addendum | `step0-m6-addendum/` | **COMPLETE_DESCRIPTIVE** — `UNMEASURABLE_FROM_FROZEN_ARTIFACTS` (no parquet reader on this machine; d=8 synthetic manifest context recorded); focused review PASS_WITH_COMMENTS |
| Step-3 paper adjudication | `step3/` | **COMPLETE_DESCRIPTIVE** — verdict **PROBE-ONLY** (full-native ≈100× over the inferred ~20 s budget on C2; all three pre-allowed split probes within the ~80 s bound); focused review PASS |
| Step-1 small-q screening | `step1/` | **COMPLETE_DESCRIPTIVE** `NBPOLAR_EXPLORATION_STEP1_SCREENING_COMPLETE_DESCRIPTIVE` — clear separation at cell-mean level (native arm A better than Gray bit-plane MSD arm B in 12/12 cells; largest at high rate: q8 R0.60 ΔFER +0.4102, q4 R0.50 +0.2529, q16 R0.60 +0.1152; seed-level nuance: q4 R0.60 has 3/16 negative seeds — carried in the adjudication); focused review PASS |
| Step-2 transfer-prior probe | `step2/` | **COMPLETE_DESCRIPTIVE** `NBPOLAR_EXPLORATION_STEP2_PRIOR_TRANSFER_COMPLETE_DESCRIPTIVE` — kept-evidence NEGATIVE: injected M2 prior (frozen floor) ≤ 0 g_succ at cell-mean in every discriminating cell vs the no-injection true-channel baseline; g_nll strongly negative where floored tail cells bind (floor-mishandling visible); amendment 3 replaced the degenerate blind-uniform control; focused review PASS_WITH_COMMENTS |

Durable records for the suite are batched at the milestone (AGENTS.md §10.4): one
`docs/decision-log.md` entry + one `AGENT_PROJECT_MEMORY.md` update at suite close;
probe-root artifacts remain worktree-only (gitignored by design).
Independent audit (2026-09-23): reviewer-go adversarial full-suite audit
PASS_WITH_COMMENTS — every value re-verified exact against the raw artifacts; two
citation-level defects (D1 `mass_le1` naming; D2 Step-2 q4_R0.60 positive seeds
2/16→3/16) corrected same-day across report/index/decision-log/memory, plus record
hygiene (STATUS duplicate keys, G3 smoke exact value, M2 4dp note, M6 review ID).
Record: decision-log suite entry (audit paragraph) + `EXPLORATION_SUITE_REPORT.md` §9;
commit `433c7371`.
