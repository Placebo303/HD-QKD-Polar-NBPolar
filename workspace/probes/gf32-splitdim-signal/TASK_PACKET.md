# TASK PACKET (SKELETON) — GF32 split-dim signal probe (Tier-X, non-claim)

**SKELETON ONLY — THIS PACKET AUTHORIZES NOTHING.**

```yaml
authorizations: []
tier: Tier-X            # docs/nbpolar/PROBE_TIER.md — explicitly NOT Tier-Y
next_gate: BT3          # PI verbatim authorization — NOT GRANTED at document creation
```

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Change: `openspec/changes/nbpolar-gf32-splitdim-probe/` (tasks BT1–BT7; this skeleton = BT2).
- Packet location note: AGENTS.md §10.1 normally places `TASK_PACKET.md` / `STATUS.yaml` under `.workbuddy/queue/<id>/`; write scope D7 confines this change's writes to the probe root, so the packet copy lives here. `PROMPT.md` and `AUTHORIZATION_PROMPT.md` are deferred to BT3 (no authorization text exists or is drafted now). **GF32-BT3-COND-33 annotation:** `AUTHORIZATION_PROMPT.md` is absent **by construction** — at BT3 the **main thread must paste the full verbatim authorization text** (a link or reference is insufficient, AGENTS.md §10.1); the prereg **C line is backfilled only after BT3** and the executed command string is then **recorded verbatim in `results.json`**; the **P line stays untouched/frozen**.
- Tier declaration (explicit): **Tier-X probe run** per `docs/nbpolar/PROBE_TIER.md` / AGENTS.md §10.4 — synthetic sensitivity evidence only. **This is explicitly NOT a Tier-Y packet**: no claim-bearing thresholds, no candidate/accepted token, no attempt counting or consumption, no scientific-status change, no Pre-EXECUTE/Pre-RESULT review mode (replaced by focused numerical review per D6), no per-probe decision-log/index/project-memory update (milestone batch).

## Authorization gate — BT3 (verbatim) — NOT AUTHORIZED

Execution (BT4), the single `results.json` write (BT5), and review (BT6) require the PI's **full verbatim authorization text** pasted at BT3. That authorization is **NOT GRANTED**; `authorizations: []` is empty by construction. Absent it: no command may be executed — including smoke runs — and this skeleton grants no authority of its own.

> **GF32-BT3-COND-33:** `AUTHORIZATION_PROMPT.md` does not exist yet; when BT3 arrives the **main thread must paste the full text** (not a link). Prereg **C-line backfill happens only after BT3** and the executed command is recorded verbatim in `results.json`; **P line not modified** (frozen at BT1).

## Input set (synthetic only; frozen by `prereg.md`)

- Channel F4 on object alphabet q = 1024: `0.75 / 0.24 / 0.005 / 0.005` (residual uniform over the other 1021 offsets).
- Object: d = 1024 = 32×32, mixed-radix `x = 32a + b`, per-stage decoded alphabet GF(32) poly37/α2 (Phase-1 provenance), n_sym = 128 (D2a argument vs A3 n = 32768), assumptions A1–A7 as recorded in `prereg.md` P-line.
- Grid: R ∈ {0.30, 0.40, 0.50, 0.60}; K_sym {38, 51, 64, 77}; design seed 2026092400; run seeds 2026092401..2026092416 (16) × 64 blocks, paired across arms.
- Read-only code input: `comparison_bench.formal_ir.nbpolar` (F1 read-only reuse).
- **Forbidden reads**: any artifact or real-data path (`D:\Data\...` provenance only, `results/`, `comparison_bench/outputs_comparison/`, any `.ttbin`/real acquisition), any G4/archive artifact. Synthetic data only.

## Arms

- **A** — native split-dimension decode: two per-factor GF(32) SC stages.
- **B** — Step-1B `B-soft`: Gray bit-plane binary polar with exact soft-carrying MSD conditioning, plane order 0..4 (r = 5), reflected Gray. `B-hard` NOT used.
- Paired: identical blocks/seeds/message+noise across arms.

## Output

- Exact output path (the ONLY result artifact): `workspace/probes/gf32-splitdim-signal/results.json`.
- Result schema (design D4, **three-way unified per GF32-BT3-COND-31**: frozen definition = prereg `METRIC` line `paired ΔFER = FER_B − FER_A`; design D4 and this schema follow it — prereg untouched): per-seed values for each arm and rate **and per-seed paired ΔFER = FER_B − FER_A**; aggregate **mean / sample-std (n−1) / range** for each arm **and for ΔFER**; **wall time**; **peak RSS**; one `status` field (`ok` or an honest failure state — never silently promoted to `ok`); echoed prereg + frozen parameters + the exact executed command string; execution/rerun log; counters `{probe_runs, reruns}`.
- **Completeness criterion (COND-31):** ΔFER **IS** part of the `results.json` completeness check in the focused review (D6) — a record missing per-seed ΔFER or its mean/sample-std/range aggregates is reported **incomplete**, never silently dropped or back-filled after the reading.

## Stop rule (D5 — end honestly)

One shot. On completion or failure, write the single `results.json` with what actually happened. Forbidden: rerun to improve a number, seed/model change after freeze, tuning against observed output, retry loops, suppressing a bad run. An execution-error rerun is permitted only as a recorded correction in the same `results.json`, never as a second attempt at a better result. Report wall honestly against the A7 bound (≤ 4× A5 ≈ 80 s per decode) with no tuning.

## Review mode (D6)

Focused numerical review only: commands, completeness, arithmetic, truth isolation, write-scope. **Not** Pre-EXECUTE/Pre-RESULT. No candidate/accepted token, no attempt accounting, no promotion of previously accepted evidence.

## Write scope (D7)

- Allowed write root: `workspace/probes/gf32-splitdim-signal/` ONLY (`prereg.md`, `TASK_PACKET.md`, `STATUS.yaml`, and after BT4/BT5 the single `results.json`).
- Forbidden writes: everywhere else — `results/`, `comparison_bench/outputs_comparison/`, archive, G4 artifacts, frozen baseline (`src/`, `experiments/`, `tools/`), `docs/nbpolar/STATE.md`, decision-log/index/project-memory, git push.

## Version-trace status of the probe root (GF32-BT3-COND-32 — record + proposal only)

- **Verified fact (docs-time check):** `.gitignore:22` (`workspace/probes/*`) ignores this probe root — `git check-ignore -v` matches `prereg.md` / `TASK_PACKET.md` / `STATUS.yaml` all against `.gitignore:22`, and `git status --porcelain` on the probe root is empty (files untracked and ignored).
- **Risk statement:** **无版本留痕风险** — the packet, frozen prereg and (later) `results.json` currently leave **no git version trace**; they exist only on disk, with no commit provenance.
- **Proposed remedy (PROPOSAL ONLY, not applied):** allow-list append `!workspace/probes/gf32-splitdim-signal/` next to the existing allow-list entries `.gitignore:23–37`, exactly as prior probes were admitted.
- **待主线程裁定 (pending main-thread adjudication):** editing `.gitignore` is outside this packet's write scope (D7: probe root only) — **the operator must NOT modify `.gitignore`**. The allow-list line is added only after explicit main-thread adjudication.

## Standing unauthorized items (O-list, inherited from tasks.md)

O1 any execution before verbatim BT3 authorization (incl. smoke); O2 any write outside the probe root or any artifact/real-data read; O3 claim-bearing thresholds / pass-fail verdicts / FER-efficiency-secret-key claims; O4 rerun, seed/model change or tuning after prereg freeze (except a recorded execution-error correction per D5); O5 archive/G4/frozen-baseline/`results/`/`outputs_comparison/`/STATE modifications, push, archival; O6 per-probe ledger updates.

## Acceptance IDs (stable; operators report these IDs)

- `GF32-BT1-PREREG` — `prereg.md` exists with exactly three lines Q/P/C; P contains the D2a object definition AND the full A1–A7 set (freeze-claim condition satisfied); F4/R/K_sym/seeds/arms/poly37 provenance/FER-only all present; C is the explicit `<backfilled after BT3>` placeholder.
- `GF32-BT2-PACKET` — this skeleton: `authorizations: []`, tier Tier-X explicit non-Tier-Y, write root = probe dir only, artifact/real-data reads forbidden, single `results.json` schema + wall/RSS + stop rule D5 + focused review D6, BT3 verbatim gate stated NOT AUTHORIZED.
- `GF32-BT3` — PI verbatim authorization + frozen-prereg confirmation. **NOT AUTHORIZED at document creation.**
- `GF32-BT4/5/6` — execute / single results.json / focused review. **NOT AUTHORIZED (blocked on BT3).**
- `GF32-BT7` — milestone-batched memory/index update; deferred, not part of this change.

## Return conditions (exactly two)

1. All-complete: per-ID report for the delegated BT, changed files, and nothing else (deltas only).
2. Concrete blocker: failing command, exact error/traceback, attempted remedies, and the single decision needed from the main thread.

## Out of scope

Probe execution, backfilled command, any authorization text, any artifact/real-data contact, any write outside this directory, R2/STATE/archive changes, git push, claim language of any kind.
