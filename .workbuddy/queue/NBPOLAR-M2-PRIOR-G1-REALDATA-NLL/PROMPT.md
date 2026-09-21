# OPERATOR PROMPT — NBPOLAR-M2-PRIOR-G1-REALDATA-NLL (copy-paste, self-contained)

You are the operator implementing a frozen G1 packet. Do NOT redesign. Do NOT guess.
If the packet or the freeze is ambiguous or they conflict, STOP and report (second return
condition). M2 is a CANDIDATE, never the baseline. G1 is DESCRIPTIVE / NON-CLAIM and
DECODER-FREE — you never call a decoder.

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD` shows
  `ref: refs/heads/codex/nbpolar-phase0`. Else STOP.
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` for EVERYTHING (TimeTagger 2.22.6 +
  Swabian shim per `docs/troubleshooting.md` — read the import-namespace and `.1`-segment
  traps there before touching any `.ttbin`).
- Packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/TASK_PACKET.md` (authoritative;
  overrides this prompt on conflict). Freeze:
  `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1_freeze.md` (all 19 TO-FREEZE
  values + gate rules + segment layout). Conflict ⇒ STOP.
- NEVER modify anything under `src/`, `experiments/`, `tools/`, `results/`,
  `comparison_bench/outputs_comparison/`, or `formal_ir/nbpolar/`. NEVER read SHG `_2`.
  NEVER call a decoder. NEVER write outside `workspace/` + this packet dir + the runner file.

## 1. Phase 0 — implement the G1 runner body (synthetic only; no data)

Per TASK_PACKET §Phase 0: implement `--stage-g1-nll` body + `--closure-only` flag in
`scripts/m2_prior_validation.py`, preserving every Stage-1 guard verbatim. Vendored (N)
pairing from `workspace/dual_rule_census_20260921.py` (frozen constants only). M2/M0 model
construction via `formal_ir/prior_m2.py`; layer metrics via UNCHANGED frozen
`nbpolar.prior` helpers (imported, never modified). Tests: synthetic fixtures + explicit
fake runner only (AGENTS.md §10.1 item 8 — never invoke the production path from tests).

## 2. Phase A — freeze closure (SHG `_1` only; decoder-free)

Run the `--closure-only` command from TASK_PACKET §Exact commands. Reproduction gate
(all five exact): peak_center 50 / σ 112.45189572400645 / status ok / n_pairs 1,269,268 /
n_frames 4,958 (PRE-skip). Mismatch ⇒ STOP loudly. Then skip-702, enumerate the post-skip
ledger (expect 4,256 complete frames; verify ≥ 4,190 allocated), apply the freeze §4 layout,
emit the four closure keys + `g1_freeze_config.json` (all 19 keys) in this packet dir.
Budget ≤ 300 s / 2 GiB. Do NOT run Phase B.

## 3. Return after Phase 0 + Phase A (exactly two conditions)

1. Complete: per-ID `G1-0`, `G1-A` PASS with evidence paths + pytest log + closure outputs +
   `git status` snippet; Phase B explicitly not run (awaiting freeze review).
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the
   SINGLE decision needed. "Still incomplete" is not a report.

(Phase B is dispatched later, same sessionID, only after the main thread records the
freeze-review PASS.)
