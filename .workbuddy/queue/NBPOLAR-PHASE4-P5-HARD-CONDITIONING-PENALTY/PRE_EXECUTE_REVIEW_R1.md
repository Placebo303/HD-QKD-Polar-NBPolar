# Pre-EXECUTE re-review R1 — NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY

Targeted re-review Rev 1 (2026-09-13, session window ~17:45-17:50). Fresh independent
reviewer; did not write the code, the freeze, or the R0 review. Read-only except this file.
The real 384-pair gate command was **NOT** run; no artifact/real-data/old-root access; no
commit/push. Repository `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; HEAD
`ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged); pinned interpreter
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3).

Scope: close R0 blocker B-1 (docs-only master enumeration repair in `P5_FREEZE.md` /
`P5_IMPLEMENTATION_NOTES.md`) and confirm no collateral change to the frozen executable
contract or premises.

## Verdict: PASS

B-1 is closed with the corrected values in both repaired locations. No other packet file
was modified after the R0 review. All frozen items, the executable contract and the
premises re-verify unchanged and consistent. R0 `NEEDS_CHANGES` is superseded; the packet
may proceed to the authorized single attempt.

## 1. B-1 closure — PASS

Repaired locations, read directly (raw current content):

- `P5_FREEZE.md:100-104`:
  ```
  - Stream seeds **2026091470, 2026091471, 2026091472**, 128 paired blocks each
    (384 pairs in one attempt); public tag master `stream_seed + 10000` =
    **2026101470, 2026101471, 2026101472**.  All six values are absent from HEAD
    (`git grep` returns no matches); the seeds are accepted and are not in the
    refused set.
  ```
- `P5_IMPLEMENTATION_NOTES.md:121-123`:
  ```
  - `git grep` for 2026091470/2026091471/2026091472 (and the three masters
    2026101470..2026101472) over HEAD returns no matches; the gate seeds are
    unused.
  ```

Arithmetic confirmed: `2026091470+10000=2026101470`, `...471`, `...472`.

No stale value remains:
- `grep -rn "20260924" . --exclude-dir=.git` → zero matches outside
  `PRE_EXECUTE_REVIEW.md` (R0's own record of the defect; expected).
- `git grep -l "20260924" HEAD` → no matches.
- OpenSpec P5 delta specs state `stream_seed + 10000` with no enumeration:
  `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p5/spec.md:19-20`;
  `openspec/changes/formal-ir-nbpolar-phase4-p5-hard-conditioning-penalty/specs/nbpolar-hard-conditioning-penalty/spec.md`
  (no master enumeration; consistent with freeze).

Constant feeds every derivation:
- `penalty_gate.py:79` `PUBLIC_TAG_MASTER_OFFSET = 10000`.
- Only three derivation sites, all through the constant (inspection of the exact
  functions): `_build_plan` → `masters = [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in
  seeds]` (:567); `_build_summary` → `"toeplitz_masters": [int(s) +
  PUBLIC_TAG_MASTER_OFFSET for s in seeds]` (:716); `run_penalty_gate` → `master =
  stream_seed + PUBLIC_TAG_MASTER_OFFSET` (:912).
- The runner passes that master to accepted `run_two_layer_block(..., toeplitz_master=
  master)`; the accepted module uses the passed master directly (no internal offset).
- Derived value printed from the module: `[2026101470, 2026101471, 2026101472]`; all
  three pass `tl.validate_toeplitz_master` (True/True/True).

## 2. No-collateral-change — PASS

Only two files have mtime later than the R0 review file (17:42:34):
`P5_FREEZE.md` (17:43:36) and `P5_IMPLEMENTATION_NOTES.md` (17:43:37). `STATUS.yaml`
(17:12:19), `TASK_PACKET.md`/`AUTHORIZATION_PROMPT.md` (17:06), the OpenSpec P5 change
docs (17:05) and the p0 P5 delta spec (17:19) are untouched. Full-content re-read of both
repaired docs shows every other frozen statement intact.

Other frozen items re-verified on the current files (raw evidence):

| item | raw current evidence | status |
|---|---|---|
| exact command | extracted bash blocks of `TASK_PACKET.md:19-21` and `P5_FREEZE.md:246-248` and module `FROZEN_COMMAND` are byte-identical (`packet==freeze: True`, `packet==module: True`), 414 bytes, sha256 `a5b66f7ffc479bb2b252266f9b0d3bfd487bc46bf30304ce07305b8803116ed8` (identical to R0) | PASS |
| D1/D2 sets | freeze lists parsed: 45/140 entries; equal to `tl.frozen_disclosure_sets(n=256,k1=45,k2=140,epsilon1=0.05)` and to independently re-sorted `analytic_order(0.05,256)[:45]` / `analytic_order(0.20,256)[:140]` (True/True both) | PASS |
| seeds/blocks/pairs | `FROZEN_SEEDS=(2026091470,2026091471,2026091472)`, `FROZEN_BLOCKS_PER_SEED=128`, `FROZEN_PAIRS=384`; 128×3=384 | PASS |
| profile strong | `PROFILE_FORMULAS["strong"]="0.02 + 0.36*u1/31"`, `profile_epsilon2("strong")` mean exactly `0.20`; `p2_maxdiff=0.34875000000000267` (unchanged) | PASS |
| K1/K2 | `FROZEN_K1=45`, `FROZEN_K2=140`; `FULLY_INVOKED_ARM_BITS=989=5*(45+140)+64` | PASS |
| budgets | `TOTAL_WALL_S=3600.0`, `EXTERNAL_TIMEOUT_S=3600`, `ULIMIT_VIRTUAL_KIB=2097152`, `RSS_LIMIT_BYTES=2147483648`; command carries `ulimit -v 2097152` / `timeout 3600`; freeze §11 same | PASS |
| attempt point | `ATTEMPT_CONSUMPTION_POINT="first gate L1 SC call (stream 0, block 0)"`, `ATTEMPT_ACCOUNTING={allowed:1, before:0, by_this_run:1, retries:0}`; freeze §10 and packet line 49-50 same | PASS |
| five-file schema | `OUTPUT_FILES == ("frozen_plan.json","per_block_paired_outcomes.json","transcript_accounting.json","aggregate_summary.json","report.md")`; freeze §11 lists exactly these | PASS |
| ten gates | `INTEGRITY_GATE_ORDER` length 10, names exactly R0-verified order (pairing coverage; p2_maxdiff≥0.30; provenance; truth-leak zero; undetected zero; nonfinite zero; resource-abort zero; cells disjoint/exhaustive; disclosures+transcript recount zero; attempt accounting); freeze §7 lists 10 | PASS |
| discriminator | `ORACLE_EXACT_MIN=365`, `LOWER_BOUND_MIN=0.30`, `LOWER_BOUND_TARGET=0.05`, root by monotone bisection, edges `X=0→0.0`, `X=384→0.05**(1/384)`; independent re-check: `L(130)=0.2985480937864875 < 0.30 < L(131)=0.30106362808316567`; direct-product-sum tail residuals `-2.57e-16` / `+2.22e-16` | PASS |
| return tokens | code emits `HARD_L1_CONDITIONING_PENALTY_CANDIDATE` / `HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED` / `BLOCKED` with frozen-order failing gate names; matches packet, freeze §8, authorization, delta spec | PASS |

## 3. Premises — PASS

- Gate root `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
  → `ABSENT` (checked at review open and again at close).
- `STATUS.yaml`: `attempts_allowed: 1`, `attempts_used: 0`, state/gate flags unchanged.
- HEAD `ab173f2a...` unchanged; `git log -1` top commit identical; `git reflog` holds only
  the clone entry; no commit/push/staging.
- Focused P5 tests (pinned interpreter, `-q -p no:cacheprovider`, fresh basetemp
  `/tmp/opencode/p5_rereview/bt`, `PYTHONDONTWRITEBYTECODE=1`):
  `comparison_bench/tests/test_nbpolar_penalty_gate.py` → **9 passed** (6.30 s).
- `git status --porcelain` = 55 entries, same count/scope as R0.
- All re-review computations were decoder-free (table build / `p2_maxdiff` / bisection);
  no runner or gate seed was executed.

## 4. Repaired masters not consumed — PASS

- `git grep -l` at HEAD for all nine values (seeds `2026091470..1472`, old masters
  `2026092470..2472`, new masters `2026101470..1472`) → zero matches for each.
- Worktree exact-value grep: the new masters `2026101470/71/72` occur only in
  `P5_FREEZE.md:102`, `P5_IMPLEMENTATION_NOTES.md:122` and the R0 review record. X01 probe
  masters (`2026101400..1434`) are numerically disjoint from the P5 masters.
- No file under `results/`, `comparison_bench/outputs_comparison/` or `workspace/probes/`
  was written since 16:55; the values are fresh probe/gate-only enumerations.

## Non-Blocking Suggestions

- None new. R0 notes N-1..N-7 remain informational; the docs-only repair does not affect
  them, and none blocks execution.

## Closure statements

- The real 384-pair gate command was **not run**; no frozen seed reached the runner.
- `attempts_used` is still **0**; the single attempt remains unconsumed.
- The gate output root is still **ABSENT** after this review (checked last at close).
- No commit, push or staging; HEAD `ab173f2a...` unchanged; nothing outside this review
  file was written by the reviewer.
- B-1 closed; this PASS is the requested targeted closure of the R0 `NEEDS_CHANGES` verdict.
