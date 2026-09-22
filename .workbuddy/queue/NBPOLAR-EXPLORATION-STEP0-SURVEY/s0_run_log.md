# S0 RUN LOG — NBPOLAR-EXPLORATION-STEP0-SURVEY (operator record, 2026-09-23)

- P0 draft check PASS: branch `codex/nbpolar-phase0` (via `.git/HEAD`); 5 packet files
  present; M1–M5 exist and readable; M1 shapes per amendment 1 (linear 2047/−1023,
  circular 1024/−512, `profile.summaries.CIRCULAR`, n_pairs 200192, mod CIRCULAR,
  both histogram sums 200192); M6 file exists (conditional input); interpreter resolved
  per ordered policy to `/home/karel_303/.venvs/timetagger/bin/python` (`.venv` absent,
  no AGENTS.md §8 deviation); probe root absent. Zero writes at P0.
- P1: probe root created; `prereg_frozen.md` → `prereg.md`; `diff` → BYTE_IDENTICAL.
- P2: wrote packet-local `s0_build_survey.py` (stdlib core + M6 import probes only);
  single run via the exact command form with the timetagger interpreter; exit 0,
  wrote `results.json` + `notes.md` (single end-of-run write). `s0_runs: 1`,
  `reruns: 0`, `rebuilds: 0`.
- Key numbers: n0 150909 / n_plus 48832 / n_minus 451 / n_tail 0;
  mass(|D|=1) = 49283/200192 ≈ 0.24617867; n_cross = 45 (44+1),
  rate ≈ 2.247842071611253e-04 per symbol; wrap closure 450+1=451 ✓ and
  48788+44=48832 ✓, all five frozen-anchor booleans true; occupancy
  UNMEASURABLE_FROM_FROZEN_ARTIFACTS (no pyarrow/pandas under either interpreter;
  both interpreters resolve to the same binary /usr/bin/python3.12, so the deduped
  evidence records 2 import attempts — corrected 2026-09-23 per focused-review
  comments R-5/R-6; nothing installed).
- No hard STOP fired; stop-rule-3 designed conditional only. No decode/raw/EVAL/RESERVE
  contact; no M1-vs-M2 arithmetic; no FER/claim object. Unrelated dirty/untracked
  worktree files untouched.
