# Run log — NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER (Tier-X, synthetic only)

## P0 draft check (S2-P: PASS, 2026-09-23)

- Branch: `codex/nbpolar-phase0` (`.git/HEAD` → `ref: refs/heads/codex/nbpolar-phase0`; NOT switched).
- Packet files: 4/4 present (`TASK_PACKET.md`, `STATUS.yaml`, `AUTHORIZATION_PROMPT.md`, `prereg_frozen.md`).
- Interpreter: `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python` with numpy 2.4.4 + pandas 3.0.2; frozen import chain `PYTHONPATH=comparison_bench/src ... -c "from comparison_bench.formal_ir.nbpolar import algebra, transform, sc, oracle"` → `import-ok`. No substitution needed.
- Step-1 `results.json`: readable; top-level keys `probe/tier/question/freeze/gates/population/cells/attestation/counters/stop_rules_fired/wall_s`, 12 cells. Grep for per-(q,R) information-set arrays → NONE (cells carry `K_sym`/FER summaries only). G0 availability recorded: file readable, equality reference unavailable.
- Output root `workspace/exploration/nbpolar-native-highdim/step2/`: ABSENT before P1.
- Pre-existing dirty/untracked worktree files noted (e.g. `M comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv` predates this task); all preserved, none touched.

## P1 (S2-1 prereg part: PASS)

- Created output root; copied `prereg_frozen.md` → `workspace/exploration/nbpolar-native-highdim/step2/prereg.md`; `cmp` → `PREREG-BYTE-IDENTICAL`.

## P2 build

- Wrote packet-local builder `s2_transfer.py` (stdlib + numpy; one typo fix `设计` → `design` in docstring; syntax-checked via `ast.parse` → `syntax-ok`).
- Builder mirrors the frozen Step-1 conventions read-only (`s1_screen.py` design/decoder patterns; `comparison_bench.formal_ir.nbpolar` imported only):
  - Design = Step-1 arm-A verbatim (TRUE F4 likelihood, genie-SC MC, design seed 2026092400, top-K_sym); F3/F4 priors enter ONLY at decode time.
  - Arm I: `log(max(p_{δ}, 1e-15))` with verbatim triple (0.7562/0.2419/0.0018/rest 0), NOT renormalized. Arm U: `log(1/q)` flat.
  - G1a/G1b: per-(prior,q) 200 tiny instances (50 n=2 + 50 n=4 per group; F4-family y vs random-transition y; logp always the arm prior under test), brute successive-MAP, first-divergence, tie-tol 1e-9.
  - G2: noiseless round-trip 20 per q, arm-I path, R=0.50 info sets (Step-1 precedent).
  - G3: dedicated 256-block smoke at R=0.30 per (q, arm), bar FER < 0.9 both arms.
  - Probe + single end-of-run write implemented per packet (unreached).

## P2 run (exact frozen command)

```
PYTHONPATH=comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python .workbuddy/queue/NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER/s2_transfer.py --probe-root workspace/exploration/nbpolar-native-highdim/step2/
```

- stderr: `GATE-FAIL: G3 smoke arm-U q=4: FER=1.0 >= 0.9`
- Exit code: 1. Builder wrote NOTHING (no `results.json`, no `notes.md`).
- Gate evidence (in-memory; process reached G3, so all earlier gates passed):
  - G0: recorded `reference unavailable, deterministic recompute only` (Step-1 results.json readable but info-set-free).
  - G1a (informed): n=200/q, 0 hard mismatches per q — PASS.
  - G1b (uniform): n=200/q, 0 hard mismatches per q — PASS.
  - G2 (arm I, noiseless): 20/20 per q — PASS.
  - G3 arm-I q=4: passed (run proceeded past it to arm U); G3 arm-U q=4: FER=1.0 (256/256 fails) — FAIL, hard STOP.

## Why G3-arm-U fails structurally (not a flake)

- `log P_U(y|x') = log(1/q)` is constant in BOTH `y` and `x'`: the uniform arm is a blind decoder. `sc_decode` normalizes each flat row to uniform; every info decision is an exact tie → argmax picks symbol 0 → `u_hat[info] = 0` on every block regardless of `y`.
- Success requires the random message to equal the all-zero vector: probability `q^-K` (`4^-38` at R=0.30). Observed 256/256 smoke fails → FER=1.0 ≥ 0.9 deterministically. No rerun within the frozen spec can change this; any "fix" would redefine F4 or G3, which the packet forbids (coder must not redefine requirements).

## Attempted remedies

- None available inside the frozen spec. No code change, no rerun (one-shot rule; a rerun cannot move a structural 1.0), no threshold reinterpretation. Root cause verified analytically AND empirically (see stderr + exit code above).

## Write-scope evidence (S2-5: PASS)

- Output root holds EXACTLY `prereg.md` (P1 copy). No `results.json`/`notes.md` created.
- `comparison_bench/`, `src/`, `experiments/`, `tools/`, `results/`, Step-0/Step-1/Step-3 roots: untouched (the one `M` under `comparison_bench/outputs_comparison/test_fixtures/` predates this task).
- Packet dir: added only `s2_transfer.py` + this log. No other workspace writes.

## Counters observed

- `s2_runs: 1, reruns: 0, rebuilds: 0` (single gated execution; `STATUS.yaml` left untouched — main thread owns durable status).

## Per-ID summary

- S2-P PASS; S2-1 PASS (prereg byte-identical, one run, frozen command); S2-2 FAIL (G3 arm-U FER=1.0; G0/G1a/G1b/G2 pass recorded above); S2-3 N/A (blocked, no probe arithmetic ran); S2-4 N/A (blocked); S2-5 PASS; S2-6 PASS (no claim; M2 triple entered only as frozen code constants, never as results; no artifacts published).

## Return condition

- Condition 2 (concrete blocker). Single decision needed from the main thread: amend the freeze so the blind uniform control is gateable (e.g. G3 smoke arm-I-only, or a recorded blind-control exemption with rationale) via a new freeze/packet — this packet's run stays consumed (1/0/0) with zero output-root result writes.

---

# Amendment-3 fresh execution (S2 re-dispatch, 2026-09-23)

## P0 draft check (S2-P: PASS)

- Branch: `codex/nbpolar-phase0` (`.git/HEAD` → `ref: refs/heads/codex/nbpolar-phase0`; NOT switched, NOT pushed, NOT committed).
- Packet files: 7/7 present (`TASK_PACKET.md`, `TASK_PACKET_AMENDMENT_3.md`, `STATUS.yaml`, `AUTHORIZATION_PROMPT.md`, `prereg_frozen.md` — the AMENDED version, `s2_transfer.py`, `s2_run_log.md`).
- Interpreter: `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python` 3.12.3, numpy 2.4.4, pandas 3.0.2; frozen import chain `PYTHONPATH=comparison_bench/src ... "from comparison_bench.formal_ir.nbpolar import algebra, transform, sc, oracle"` → `import-ok`.
- Step-1 `results.json`: readable; keys `probe/tier/question/freeze/gates/population/cells/attestation/counters/stop_rules_fired/wall_s`; 12 cells with `K_sym`/FER summaries only — NO per-(q,R) information-set arrays. G0 availability recorded: readable file, equality reference unavailable → expected outcome "reference unavailable, deterministic recompute only".
- Output root: held ONLY the stale pre-amendment `prereg.md` from the gate-failed run (no measurement ever existed); per amendment 3 this is a fresh packet execution, so refreshing `prereg.md` from the amended `prereg_frozen.md` is expected and recorded here. No other file in the root — proceed.
- Unrelated dirty/untracked worktree files preserved, none touched (the `M comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv` entry is stat-dirty only — `git diff --numstat` empty, mtime 2026-09-19, predates this task).

## P1 (S2-1 prereg part: PASS)

- `cp prereg_frozen.md → workspace/exploration/nbpolar-native-highdim/step2/prereg.md`; `cmp` → `PREREG-BYTE-IDENTICAL`.

## P2 builder amendment (packet-local `s2_transfer.py` only; `comparison_bench/` read-only)

- Arm U redefined per amendment 3: new `make_logp_true_channel(logpmf)` builder (`log P_U(y|x') = log P_F4(y|x')`); the old `logp_uniform_from_y` (flat `log(1/q)`) is GONE — grep confirms zero live references (remaining "uniform" strings are the Step-1 G1 random-transition y-generation, the frozen F2 tail wording, and degeneracy-history notes).
- G1b redirected to the true-channel builder (salt kept `[seed, 1750+q, 1]`); G3 smoke + paired probe use `(I=logp_informed_from_y, U=true-channel builder)` sharing code/seeds/messages/noise.
- `results.json`: `freeze.F4` = no-injection-baseline echo + new `F4_history` (blind-uniform degeneracy record); `question` = meaningful-form echo; new top-level `arm_u_redefinition` + `blind_uniform_degeneracy_note` keys; per-(q,R) `info_set_summary` (`K_sym`, `n_frozen`, design-method echo; NO digests).
- `notes.md`: arm-U redefinition echo + blind-uniform degeneracy note + G1b-redirect note.
- `ast.parse` → `syntax-ok`. No Step-0/1/3 root touched; no `comparison_bench/` modification (imports only); Step-1 `s1_screen.py` read-only reference (design/decoder conventions reused, unmodified).

## P2 run (exact frozen command, exit 0, wall 196.0 s ≤ 3600 s)

```
PYTHONPATH=comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python .workbuddy/queue/NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER/s2_transfer.py --probe-root workspace/exploration/nbpolar-native-highdim/step2/
```

- Gates (S2-2: PASS): G0 `reference unavailable, deterministic recompute only` (12/12 cells `equal: null`); G1a informed 200/q, 0 hard mismatches (strict 200/199/198 + tie-tolerated remainder); G1b TRUE-CHANNEL 200/q, 0 hard mismatches (strict 193/200/197 + tie-tolerated remainder); G2 arm-I noiseless 20/20 per q; G3 smoke R=0.30 BOTH arms < 0.9 (q4: I 0.0977 / U 0.0000; q8/q16: 0.0 both arms; n=256 each).
- Run completeness (S2-3: PASS): 12/12 cells × 16 seeds × 64 paired trials × both arms; pairing intact (shared message+noise per (seed,block)).
- Metric integrity (S2-4: PASS): `g_succ=(Σok_I−Σok_U)/64`, `g_nll=Σ(nll_U−nll_I)/64`, `nll_arm=−Σ_{i∈info}log2 P_arm(true|y)` from `decision_metrics`; per-seed series (n=16) + mean/sample-std/range per cell; NO numeric threshold; negatives kept (see headline table — several cells negative, recorded as evidence per design §5).
- Write scope (S2-5: PASS): output root holds EXACTLY `prereg.md` + `results.json` + `notes.md` (gitignored, worktree-only); packet dir added only the amended `s2_transfer.py` + this log.
- No-claim (S2-6: PASS): attestation `no_real_data/no_fer_claim`, ledger `L2 synthetic screening — never cited as L1 real-data FER`; M2 triple verbatim (0.7562/0.2419/0.0018/rest 0, floor 1e-15, NOT renormalized) with G1R2 CAL32 provenance; counters `s2_runs=1 reruns=0 rebuilds=0`; `stop_rules_fired: []`.
- No tuning, no rerun, single-threaded, RSS within budget, deterministic, no network, no installs.

## Headline paired table (per-seed means; synthetic L2, non-claim)

| q | R | f | FER_I | FER_U | g_succ mean | g_nll mean |
|---|---|---|-------|-------|-------------|------------|
| 4 | 0.30 | 0.6733 | 0.0840 | 0.0000 | −0.0840 | −338.75 |
| 4 | 0.40 | 0.9036 | 0.3936 | 0.0596 | −0.3340 | −1331.64 |
| 4 | 0.50 | 1.1340 | 0.6152 | 0.4189 | −0.1963 | −2578.54 |
| 4 | 0.60 | 1.3643 | 0.9414 | 0.9326 | −0.0088 | −5305.54 |
| 8 | 0.30 | 0.9968 | 0.0000 | 0.0000 | 0.0000 | −0.00 |
| 8 | 0.40 | 1.3378 | 0.0000 | 0.0000 | 0.0000 | +0.00 |
| 8 | 0.50 | 1.6789 | 0.0713 | 0.0039 | −0.0674 | −775.91 |
| 8 | 0.60 | 2.0199 | 0.3174 | 0.1270 | −0.1904 | −3719.70 |
| 16 | 0.30 | 1.3189 | 0.0000 | 0.0000 | 0.0000 | +0.00 |
| 16 | 0.40 | 1.7701 | 0.0000 | 0.0000 | 0.0000 | +0.00 |
| 16 | 0.50 | 2.2214 | 0.0010 | 0.0000 | −0.0010 | −23.20 |
| 16 | 0.60 | 2.6726 | 0.0830 | 0.0088 | −0.0742 | −1333.56 |

Reading (kept evidence, not a claim): the injected M2 prior with the frozen floor rule does NOT beat the true-channel baseline on this envelope — g_succ ≤ 0 in every discriminating cell, and g_nll strongly negative wherever the floored tail cells bind (the floor-mishandling mechanism the amendment named is visible in the measurement). Zero-gain cells (q8 R≤0.40, q16 R≤0.40) are perfect-decode ties under both arms.

## Return condition

- Condition 1 (all-complete per IDs S2-P, S2-1..S2-6). Work NOT marked accepted — main thread owns acceptance.
