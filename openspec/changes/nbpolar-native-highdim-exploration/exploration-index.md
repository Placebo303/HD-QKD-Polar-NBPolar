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

- T1/T3/T5/T6 accepted 2026-09-23 (review gates T2/T4 PASS).
- T2/T4 complete.
- T7 accepted 2026-09-23 (main-thread doc review).
- T8/T9 pending.
