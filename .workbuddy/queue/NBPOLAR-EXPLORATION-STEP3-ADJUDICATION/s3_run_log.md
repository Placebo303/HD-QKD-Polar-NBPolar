# S3 run log — NBPOLAR-EXPLORATION-STEP3-ADJUDICATION (s0-style)

- Branch (`.git/HEAD`): `ref: refs/heads/codex/nbpolar-phase0` — no switch, no commit, no push.
- Interpreter: `.venv/bin/python` absent; timetagger venv absent; used stdlib-only
  `python3` (3.12.3) fallback per prereg ordered policy — recorded here.
- P0 draft check: 4 packet files present; output root
  `workspace/exploration/nbpolar-native-highdim/step3/` absent — PASS.
- P1: `mkdir -p` output root; `cp prereg_frozen.md → prereg.md`; `diff` → BYTE_IDENTICAL.
- P2: wrote packet-local stdlib builder `s3_adjudicate.py` (this dir); ran
  `python3 .workbuddy/queue/NBPOLAR-EXPLORATION-STEP3-ADJUDICATION/s3_adjudicate.py
  --out-root workspace/exploration/nbpolar-native-highdim/step3/`
  wall ~0.04 s (budget ≤ 300 s), single-threaded, zero-output crash: none,
  rebuilds: 0.
- Outputs: `prereg.md`, `results.json`, `notes.md` (exactly 3 files in output root).
- Row seconds (s_c1 / s_c2 at A5 1e9 ops/s):
  full-native 34.360 / 2063.598; probe-GF32 0.067 / 0.519;
  probe-GF16xGF64 0.143 / 1.089; probe-GF8xGF128 0.539 / 4.076.
- Verdict: PROBE-ONLY (full-native NOT within ~20 s; all 3 probe rows within ~80 s).
- Scope: writes only to output root + this packet dir; no data paths, no
  `formal_ir/`/`src/` imports, no decoder execution, no installs.
- Unrelated dirty/untracked worktree files preserved untouched.
