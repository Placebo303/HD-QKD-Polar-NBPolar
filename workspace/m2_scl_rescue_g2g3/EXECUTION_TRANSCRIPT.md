# EXECUTION TRANSCRIPT — m2-scl-rescue-g2g3

One-shot execution, authorized by the main thread on 2026-09-28 after
independent Pre-EXECUTE review (`PRE_EXECUTE_REVIEW.md`, verdict
`PASS_WITH_COMMENTS`). This is a **descriptive real-data re-decode
diagnostic** (main-thread ruling D1) — no threshold, no pass/fail verdict,
no change to `NBPOLAR_M2_PRIOR_G2_SUCCESS`/`NBPOLAR_M2_PRIOR_G3_SUCCESS`/the
M2 status ladder, zero attempts counted against any Tier-Y budget. **This
transcript reports what ran; it renders no adjudication** — that is the main
thread's decision after independent Pre-RESULT review.

## Command (verbatim, both attempts — prereg.md §C, unchanged)

```
wsl.exe -e bash -c "PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar /home/karel_303/.venvs/timetagger/bin/python /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/m2_scl_rescue_g2g3/run.py"
```

Launched via the Bash tool's `run_in_background: true` wrapping this single
foreground `wsl.exe -e bash -c "..."` invocation (no `nohup`/`&` inside the
WSL command; no `cd` anywhere — all paths absolute, to avoid drvfs mount
races), per the main thread's explicit instruction.

## Attempt 1 — pre-measurement implementation-defect death (excluded from reruns)

- Started: `2026-09-27T17:43:38Z`. Failed: `~2026-09-27T17:43:58Z` (exit 1).
- G2 session setup completed (`H_total=0.816814 bits`); G3 session setup
  crashed inside `scripts/m2_prior_validation.py::_load_g2_decoder_chain`
  (`ValueError: pandas.__spec__ is None`) before any raw G3 read, and before
  any block's fidelity/rescue call for either session.
- **Zero measurement occurred**: 0 SC/SCL/tag calls on protected EVAL data,
  0 `part_*.json`, no `results.json`.
- Root cause: `run.py` (attempt 1) called the frozen
  `_load_g2_decoder_chain()` twice in one process (once per session); its
  own pandas-absent guard is not safe to re-evaluate once it has already
  installed a spec-less fail-closed stub into `sys.modules["pandas"]`.
- Fix (in `run.py` only; no frozen file touched, no parameter/seed change):
  load the decoder chain + `scl_joint` module ONCE in `main()` and pass them
  into `_reproduce_session_context()` for both sessions.
- Full record: `session_setup_execution_error_attempt1.json`. Re-ran static
  self-check after the fix (`py_compile` pass; AST `%`-format scan: 0
  expressions, 0 mismatches) before relaunching.
- Per AGENTS.md §10.4 / main-thread instruction: this attempt is **excluded
  from the reruns counter** (pre-measurement defect death); attempt 2 is the
  one and only measurement attempt. `STATUS.yaml counters.reruns` stays `0`.

## Attempt 2 — the measurement (exit 0)

- Started: `2026-09-27T17:57:55Z`. Finished: `~2026-09-27T18:17:07Z`
  (`wall_s_total` reported by `run.py` = **1152.02 s** ≈ 19.2 min).
- stdout/stderr (verbatim):
  ```
  [setup] reproducing G2 session context (raw read + align + CAL fit)...
  [setup] G2 ready: H_total=0.816814 bits, f_book_no_crc=1.274745, f_book_with_crc=1.275343
  [setup] reproducing G3 session context (raw read + align + CAL fit)...
  [setup] G3 ready: H_total=0.821478 bits, f_book_no_crc=1.267507, f_book_with_crc=1.268101
  DONE fidelity_ok=9/9 fidelity_mismatch=0 rescued_exact=8 still_failed=1 undetected=0 errors_or_aborts=0 wall_s=1152.0
  [exited with code 0]
  ```
- Session-level alignment reproduction (both matched their session's own
  frozen literals bit-exact — `run.py` would have raised `ALIGN_INCONSISTENT`
  otherwise, and did not):
  - G2: `n_pairs=1259992`, `n_frames=4921`, `peak_center_ps=50`,
    `peak_sigma_ps=112.45189572400645`, `peak_to_bg=1366.27`, `status=ok`.
  - G3: `n_pairs=1277938`, `n_frames=4991`, `peak_center_ps=50`,
    `peak_sigma_ps=114.43029692866367` (= `G3_REPRO_GATE`), `peak_to_bg=1385.55`,
    `status=ok`.
  - `H_total_bits`: G2 = 0.8168138204133305, G3 = 0.8214782076249098.
  - Disclosure bookkeeping (block-invariant, both sessions):
    `kdb_no_crc=34119`, `kdb_with_crc=34135`.
    `f_book_no_crc`/`f_book_with_crc`: G2 = 1.274745 / 1.275343;
    G3 = 1.267507 / 1.268101.
- `results.json["fidelity_compromised"] = false` (no block hit
  `STOPPED_FIDELITY_MISMATCH`, so the summary aggregate rescue counts are
  reported, per main-thread ruling D3).

### Per-block results (from `results.json["blocks"]` / `part_*.json`)

| session | block | fidelity match | outcome(exp=act) | first_err_coord | first_err_layer | l1_exact(SC) | hard_l2_exact(SC) | label_exact | crc_pass | tag_pass | accepted | exact | undetected | l1_exact_scl | hard_l2_exact_scl | l1_err_syms | l2_err_syms | wall_fidelity_s | wall_rescue_s | wall_total_s | rss_gib |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G2 | 1  | True | verify_failed | 1253 | L2 | True  | False | **True**  | True  | True  | True  | **True**  | False | True | **True**  | 0 | 0  | 22.93 | 589.67 | 612.60 | 0.538 |
| G2 | 5  | True | verify_failed | 978  | L2 | True  | False | **False** | False | False | False | **False** | False | True | **False** | 0 | 78 | 23.34 | 585.94 | 609.28 | 0.540 |
| G2 | 12 | True | verify_failed | 2000 | L2 | True  | False | **True**  | True  | True  | True  | **True**  | False | True | **True**  | 0 | 0  | 22.97 | 580.81 | 603.78 | 0.540 |
| G3 | 0  | True | verify_failed | 6611 | L2 | True  | False | **True**  | True  | True  | True  | **True**  | False | True | **True**  | 0 | 0  | 22.92 | 587.90 | 610.82 | 0.549 |
| G3 | 1  | True | verify_failed | 911  | L2 | True  | False | **True**  | True  | True  | True  | **True**  | False | True | **True**  | 0 | 0  | 22.97 | 581.84 | 604.82 | 0.552 |
| G3 | 2  | True | verify_failed | 119  | L2 | True  | False | **True**  | True  | True  | True  | **True**  | False | True | **True**  | 0 | 0  | 23.70 | 586.89 | 610.59 | 0.557 |
| G3 | 4  | True | verify_failed | 175  | L2 | True  | False | **True**  | True  | True  | True  | **True**  | False | True | **True**  | 0 | 0  | 23.99 | 587.69 | 611.68 | 0.519 |
| G3 | 10 | True | verify_failed | 1207 | L2 | True  | False | **True**  | True  | True  | True  | **True**  | False | True | **True**  | 0 | 0  | 23.02 | 586.20 | 609.22 | 0.568 |
| G3 | 11 | True | verify_failed | 379  | L2 | **False** | False | **True**  | True  | True  | True  | **True**  | False | True | **True**  | 0 | 0  | 20.10 | 469.16 | 489.27 | 0.565 |

All 9 rows: `outcome`/`first_error_coordinate`/`first_error_layer`/`l1_exact`/
`hard_l2_exact` from the fidelity check (`actual`) matched the frozen
`per_block_outcomes.jsonl` row (`expected`) exactly — `fidelity.match=True`,
`mismatches=[]` for all 9 (see `results.json["blocks"][*]["fidelity"]` for
the full expected/actual pairs). G3 block 11 is the one block whose SC
`l1_exact=False` (a block-level L1 error existed under the frozen SC path);
all other 8 blocks had SC `l1_exact=True` (pure L2-layer SC failures),
matching `workspace/analysis/g2g3-layer-attribution/REPORT.md` exactly.

For every block, `l1_survivor_count=16`, `top_m_used=4`,
`candidates_considered=64` (i.e. `top_m` × `list_width_L` L2 candidates per
L1 survivor, as designed).

### Resource summary

- Max `wall_total_s` per block: 612.60 s (G2 block 1) — within the 1200 s
  per-block budget with ~2x margin.
- Max `rss_gib_peak_advisory`: 0.568 GiB (G3 block 10/11) — within the 2 GiB
  per-block budget with large margin (consistent with the T3 precedent cited
  in `TASK_PACKET.md` §7 R3/`PRE_EXECUTE_REVIEW.md` finding 7).
- `n_errors_or_aborts = 0`: no block hit `resource_abort_wall_pre_rescue`,
  `resource_abort_wall_post_rescue`, `resource_abort_wall_hard_terminate`, or
  any `error:*` status.
- 8-way parallelism: G2 blocks 1/5/12 and G3 blocks 0/1/2/4/10 (8 blocks)
  ran concurrently (all finished within `wall_total_s` 603-613s of each
  other); G3 block 11 started after a slot freed and finished faster
  (`wall_total_s=489.27s`) — consistent with the designed ≤8-concurrent
  launcher.

### Summary (`results.json["summary"]`, `fidelity_compromised=false` branch)

```
n_targets=9, n_fidelity_ok=9, n_fidelity_mismatch=0,
n_rescued_exact=8, n_still_failed=1, n_undetected=0, n_errors_or_aborts=0
```

## Deviations from the frozen plan

- **None in method/parameters**: `list_width_L=16`, `top_m=4`, `K1=319`,
  `K2=6492`, `N=32768`, construction digest, `tag_master`/`eval_seed` per
  session — all exactly as frozen in `prereg.md`/`TASK_PACKET.md`. No
  parameter, seed, K, window, or MOD change of any kind.
- **One recorded execution-defect death + fix + single relaunch** (attempt 1
  above) — pre-measurement, excluded from reruns per the main thread's own
  instruction; documented in full in
  `session_setup_execution_error_attempt1.json` and `STATUS.yaml
  execution.attempt_1`.
- Total wall (1152.02 s ≈ 19.2 min) came in under the ~25-35 min estimate in
  `TASK_PACKET.md` §7 R3 — the per-session setup (raw read + align + CAL
  fit) was faster than the conservative estimate assumed.
- No other deviation: no additional block/session/arm was ever opened;
  `TARGETS` is a hardcoded 9-tuple, never touched.

## No adjudication rendered here

This transcript is a factual record only. `results.json["claims"]` states
explicitly: no significance test, no threshold, no pass/fail verdict, no
candidate/accepted promotion, no change to
`NBPOLAR_M2_PRIOR_G2_SUCCESS`/`NBPOLAR_M2_PRIOR_G3_SUCCESS`/the M2 status
ladder. `results["blocks"]` and this transcript are ready for independent
Pre-RESULT review (`STATUS.yaml next_gate: PRE_RESULT_REVIEW`); the main
thread owns whatever interpretation follows.
