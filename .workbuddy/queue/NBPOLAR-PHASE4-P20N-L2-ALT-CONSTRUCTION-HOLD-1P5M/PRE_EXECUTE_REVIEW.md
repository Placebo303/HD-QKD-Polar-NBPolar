# P20N Pre-EXECUTE review (independent; Stage A -> Stage B gate)

- Reviewer: `reviewer-go` (independent subagent), session `ses_f480b89c3ffeF7kAH133WfZ4lf`, 2026-09-19.
- Scope (packet §14 R7 + `AGENTS.md` §10.3): §3 alt-L2 derivation + D2
  feasibility outcome, §5 K-literal, §4 gate family/population, §2 runner-delta
  design, §7 instrumentation boundary, plus branch / scoped cleanliness /
  authorization / target-output absence / focused tests.
- Verdict: **PASS (PX1–PX7; two non-blocking doc-wording caveats)**. Stage B MAY
  be authorized once the filled STEP-2 text is pasted and target-output absence
  is re-confirmed at execution time. (The reviewer marks nothing accepted and
  authorizes nothing.)

## Verdicts (abridged evidence)

| ID | Verdict | Key evidence |
|---|---|---|
| PX1 command/pins | PASS (doc caveat) | argv byte-identical to module `FROZEN_COMMAND` (`ARGV_EQUAL True`; EXPORT/ULIMIT equal); alt sha `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`; prior digest `372dcc1c…f7d46ac`; order digest `a9f18a9f…1bc638`; K `331/6689/7020`; N 32768 / source 1p5M / master 2026092300 / alpha 1.0 / floor 1e-15; DEV `2213..2724` + remainder `2725..2766`; caps 35164/33509/327743. Caveat: freeze §5 `cd` line typo (corrected by main thread, doc-only). |
| PX2 §3 derivation | PASS | Own recomputation: `f_alt` max-abs-diff `0.0`, `p2_alt` `0.0`; artifact keys exactly 9 (`alpha, counts_ab, f_alt, floor_value, h1_inc, h2_alt, h_total_alt, p1, p2_alt`); `alpha 1.0`; floor hits `0/1048576`; zero columns 0; `f_alt` range `0.000665335994677302..0.24762550881953543`; `p1`-equality `0.0` (α1-derived-marginal delta 0.7353595255735041 proves L1 carried); `h2_alt 1.4447543021770293`; column dev `6.894484982922222e-14`. |
| PX3 D1/D2 | PASS | Own independent CE estimator: `ce_alt 0.9027311772313849` (diff 0.0), `ce_incumbent 0.8003665547439149` (diff 0.0), `alt_ideal_length_bits 29580.69521551802` (diff 0.0), ceiling 33509 → **FEASIBLE**, margin `3928.304784481981`. Outcome frozen in `P20N_FREEZE.md`/`STATUS.yaml` BEFORE any HOLD contact (HOLD counters 0, Stage-B root ABSENT, worktree reads 1). |
| PX4 §4 gates/population | PASS | Family (a)→(g) fail-closed in frozen order before any protected content open (loads ≥:2195); HOLD-containment + consumed-TRAIN/VAL-DEV/VAL-remainder exclusions + S2-ii; 1M/2M refused paths; mode separation refuses before read/write; K-literal gate replays `331/6689/7020`. |
| PX5 §2 delta + §7 instrumentation | PASS | Only the frozen delta list vs accepted `raw_prior_val_1p5m`; exactly 4 hardcoded arms (Δ caps exactly 0); `_l2_hazard_diagnostics` eight exact scalars, null-unless-L2-fail fields, R=8, post-decode recording-only; truth-isolation sentinel green; no extra factors/sweeps. |
| PX6 Pre-EXECUTE checklist | PASS | Branch `codex/nbpolar-phase0`; STEP-1 recorded, `stage_b_authorized: false`; Stage-B root ABSENT; P20N suite `16 passed` (`-p no:cacheprovider`); predecessor `test_nbpolar_raw_prior_val_1p5m.py` 3 failures root-caused pre-existing (P20M accepted root exists since 10:53:48; `AGENT_PROJECT_MEMORY.md` records its master 2026092280 since 11:01:39) — not caused by P20N. |
| PX7 write scope | PASS | New module + new test + packet dir (`P20N_FREEZE.md`, `P20N_IMPLEMENTATION_NOTES.md`, `STATUS.yaml`, `alt_l2_tables_1p5m.npz`) + `workspace/p20n/derive_4qZWFV5C/derive_stdout.json`; accepted modules byte-unchanged (sha table); counters counts 0/0 + HOLD 0/1 + VAL-remainder 0 + worktree-npz 1 + attempts 0/1; 2M pristine; no commit. |

## Caveats (non-blocking)

1. `P20N_FREEZE.md` §5 `cd` line typo (`/mnt/Code/...` → `/mnt/d/Code/...`) —
   corrected by the main thread after this review (doc-only; argv unchanged;
   the module `FROZEN_COMMAND` and the STEP-2 block were already correct).
2. `P20N_IMPLEMENTATION_NOTES.md` §5 wording about "no P20M literals" in the new
   files — the only `2026092280` hit is the test's intentional refusal probe
   (`test_nbpolar_l2_alt_hold_1p5m.py:476`). Wording only.

No files were edited by this review; no commit/push; not a self-acceptance.
