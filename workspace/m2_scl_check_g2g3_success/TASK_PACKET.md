# TASK PACKET — m2-scl-check-g2g3-success

Per AGENTS.md §3/§10.1/§10.3/§10.4 (delta-successor fast path): this
document authorizes NOTHING by itself. Execution requires (in order): (1)
independent Pre-EXECUTE review PASS on THIS packet, (2) the PI
authorization already on file (verbatim below, 2026-09-28 — already given,
no re-paste needed per the task instruction that created this packet), (3)
Pre-RESULT review before `results.json` is treated as a finished artifact
or cited in any adjudication/decision-log entry.
**This preparation pass did NOT execute anything, did NOT run any decoder,
did NOT read raw .ttbin data content (existence checks only), and did NOT
modify any existing file, including anything under
`workspace/m2_scl_rescue_g2g3/`.**

## 0. Inheritance (delta-successor of `workspace/m2_scl_rescue_g2g3/`)

This packet is a delta-successor, per AGENTS.md §10.1 item 5 and §10.4's
"Delta-successor fast path", of `workspace/m2_scl_rescue_g2g3/` (Pre-EXECUTE
PASS_WITH_COMMENTS, Pre-RESULT PASS, commit `326594ca`). It reuses that
predecessor's contract unchanged except for the explicit delta below:

| | Predecessor (`m2_scl_rescue_g2g3`) | This packet (`m2_scl_check_g2g3_success`) |
|---|---|---|
| Question framing | Can SCL **rescue** SC `verify_failed` blocks? | Does SCL **preserve** SC `outcome=exact` blocks, or does it break/silently-corrupt any? |
| Target blocks | 9: G2 {1,5,12}; G3 {0,1,2,4,10,11} — all `verify_failed` | 19: G2 {0,2,3,4,6,7,8,9,10,11,13} (11); G3 {3,5,6,7,8,9,12,13} (8) — all `outcome=exact` |
| Target source | `workspace/analysis/g2g3-layer-attribution/REPORT.md` §3/§4 (attribution report) | Direct filter of the frozen `per_block_outcomes.jsonl` (arm=`B_M2_32f_candidate`, outcome=`exact`), cross-checked against an independently stated expected list in this prep pass (§2 below) |
| Authorization | PI, 2026-09-28: "授权，用 SCL L=16 重解那 9 个失败块，可以继续往下推进" | PI, 2026-09-28: "授权，19 块也跑 SCL L=16" |
| Decoder / params (L, top_m, CRC, K1/K2, N, digest, window/skip/MOD, tag_master, eval_seed, venv) | frozen | **identical, unchanged** |
| `accepted` formula | `crc_pass AND tag_pass` (ruling F1) | **identical, unchanged** (inherited) |
| Budget / parallelism / reruns | 1200s/2GiB per block, ≤8 concurrent, reruns=0 | **identical, unchanged** |
| Fidelity-check mechanism | per-block STOP + `fidelity_compromised` global flag (ruling D3) | **identical, unchanged** (inherited) |
| Summary field names | `n_rescued_exact`, `n_still_failed` (= "not exact", i.e. includes `undetected`), `n_undetected`, `n_errors_or_aborts` | `n_preserved_exact` (= `rescue.exact`), `n_broken` (= `rescue.verify_failed` **specifically**, not "not exact"), `n_undetected` (unchanged), `n_errors_or_aborts` (unchanged) — **see §3 decision point D-NEW1** |
| Output dir | `workspace/m2_scl_rescue_g2g3/` | `workspace/m2_scl_check_g2g3_success/` |
| `probe_id` | `m2-scl-rescue-g2g3` | `m2-scl-check-g2g3-success` |

Main-thread rulings **inherited unchanged** from the predecessor (per this
task's instruction; not re-litigated here, no new ruling text required):

- **D1 (classification)**: "真实数据描述性诊断" (real-data descriptive
  diagnostic); reviewed at Tier-Y rigor (independent Pre-EXECUTE AND
  Pre-RESULT both required); no threshold, no pass/fail verdict, no
  state-string change; counts as **zero attempts** against any Tier-Y
  attempt budget anywhere. Applies identically here: this is also a
  real-data descriptive diagnostic (a preservation check instead of a
  rescue attempt), with the same non-claim status.
- **D2 (output root)**: keep the named directory
  (`workspace/m2_scl_check_g2g3_success/`), not `workspace/probes/`.
- **D3 (fidelity-mismatch scope)**: per-block STOP; a mismatch on ANY
  target block sets top-level `fidelity_compromised=true` and withholds
  the aggregate tally from `summary` (per-block detail still appears in
  `results["blocks"]`). Implemented identically in this packet's
  `run.py::main()`.
- **D4 (budget mechanism)**: per-block soft check before starting the SCL
  call; parent-process hard `terminate()` at budget+120s. No change.
- **F1 (accepted-definition)**: `accepted = crc_pass AND tag_pass` (matches
  the `workspace/probes/scl-gate-t3` gate convention). `exact = accepted
  AND label_exact`; `undetected = accepted AND NOT label_exact` (isolated,
  never merged into `exact`); `verify_failed = NOT accepted`. Implemented
  identically in this packet's `run.py::_rescue_block()`.

## 1. Scope

### Allowed to write (additive only; must not pre-exist)

- `workspace/m2_scl_check_g2g3_success/results.json`
- `workspace/m2_scl_check_g2g3_success/part_<SESSION>_<block>.json` (19 files)
- `workspace/m2_scl_check_g2g3_success/EXECUTION_TRANSCRIPT.md` — to be
  written after execution completes (main-thread instruction, inherited
  convention from the predecessor).
- `workspace/m2_scl_check_g2g3_success/session_setup_execution_error_attemptN.json`
  — ONLY if an execution-defect death occurs before any measurement
  (inherited convention; not expected, since the predecessor already fixed
  the one known defect — the load-once fix is already present in this
  packet's `run.py`).

### Allowed to read

- Raw `.ttbin` for `20260113_SHG_Type2PPLN_3s` (SHG `_1`) and
  `20260113_SHG_Type2PPLN_3s_2` (SHG `_2`) — via the SAME frozen readers
  G2/G3/the predecessor used; no new acquisition, no different
  window/skip/MOD. **Not read in this preparation pass — existence
  confirmed only (§4 below).**
- `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/per_block_outcomes.jsonl`
  and `.../20260113_SHG_Type2PPLN_3s_2_g3/per_block_outcomes.jsonl`
  (read-only; already read in this prep pass for the target-list
  confirmation, §2 below, and read again at runtime for the fidelity
  check).
- `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
  (frozen P16 construction, digest-pinned; existence confirmed, not
  content-read, in this prep pass).
- `scripts/m2_prior_validation.py`,
  `comparison_bench/src/comparison_bench/formal_ir/{prior_m2.py,nbpolar/*.py}`
  — imported, never edited.
- `workspace/m2_scl_rescue_g2g3/run.py`, `TASK_PACKET.md`, `STATUS.yaml`,
  `prereg.md`, `AUTHORIZATION_PROMPT.md` — read-only, as the delta-successor
  base contract. **Not modified.**

### Forbidden (hard stop if touched)

- Any edit to `sc.py`, `scl.py`, `scl_joint.py`, `two_layer.py`,
  `transform.py`, `algebra.py`, `prior.py`, `prior_m2.py`,
  `operational_f13*.py`, `m2_prior_validation.py`, or any other file under
  `src/`, `experiments/`, `tools/`, `comparison_bench/src/`.
- Any write under `results/`, `comparison_bench/outputs_comparison/`, or
  any EXISTING directory under `workspace/m2_prior_validation/` (this
  packet only reads `per_block_outcomes.jsonl` there).
- **Any write to `workspace/m2_scl_rescue_g2g3/` (the predecessor packet) —
  read-only reference only, per this task's explicit instruction.**
- Any edit to `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/` or
  `.../NBPOLAR-M2-PRIOR-G3-CONFIRM/` (STATUS.yaml, freeze configs, or any
  other file in those packet dirs).
- Any change to `NBPOLAR_M2_PRIOR_G2_SUCCESS` / `NBPOLAR_M2_PRIOR_G3_SUCCESS`
  / the M2 status ladder, in this or any other document.
- Drawing any EVAL frame/block outside the 19 named targets, or any
  CAL/HELDOUT frame for any purpose other than reproducing the SAME CAL fit
  G2/G3/the predecessor already used.
- git commit/push of any kind (operator scope is preparation only per this
  task's instructions).
- Running the decoder / executing `run.py` (preparation only, per this
  task's instructions — this pass stops at `state=prepared_awaiting_pre_execute`).

## 2. Target-block confirmation (performed in this preparation pass)

Filtered both frozen `per_block_outcomes.jsonl` files for
`arm=="B_M2_32f_candidate"` and `outcome=="exact"` (read-only, JSON-line
parsing only — no raw `.ttbin` content read):

- **G2** (`workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/per_block_outcomes.jsonl`,
  14 B-arm rows total): exact blocks = `[0, 2, 3, 4, 6, 7, 8, 9, 10, 11, 13]`
  (11 blocks). **Matches the expected list given in the task instruction
  exactly.**
- **G3** (`workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3/per_block_outcomes.jsonl`,
  14 B-arm rows total): exact blocks = `[3, 5, 6, 7, 8, 9, 12, 13]`
  (8 blocks). **Matches the expected list given in the task instruction
  exactly.**

Total: 11 + 8 = **19 blocks**, matching the task's target count. No
mismatch encountered; the task's stop-on-mismatch rule was not triggered.
These 19 pairs are hardcoded verbatim into `run.py::TARGETS` (never
re-derived by `run.py` itself at runtime, preserving the predecessor's
`E2_no_new_data`-equivalent discipline: the target list is a frozen module
constant).

## 3. Diff against the predecessor's `run.py` (mechanical, per delta-successor scope)

Full unified diff generated in this prep pass (`diff -u
workspace/m2_scl_rescue_g2g3/run.py workspace/m2_scl_check_g2g3_success/run.py`,
310 lines). Summary of every substantive change:

1. **TARGETS** (module constant): 9 `verify_failed` pairs → 19 `exact` pairs
   (§2 above). Its preceding comment block rewritten to cite the
   `per_block_outcomes.jsonl` filter instead of the REPORT.md attribution
   report (the actual provenance for this packet's target list).
2. **Output directory**: no code change needed (`THIS_DIR =
   Path(__file__).resolve().parent` is already directory-relative); only
   docstring path strings referencing
   `workspace/m2_scl_rescue_g2g3/results.json` updated to
   `workspace/m2_scl_check_g2g3_success/results.json`.
3. **Prose ("失败块/rescue" → "成功块/preservation check")**: module
   docstring (title, Question section, Non-goals section) rewritten for
   the preservation-check framing and the 19-block count; function
   docstrings for `_fidelity_check` and inline comments in `main()`
   reworded from "SCL rescue" to "SCL preservation check" / "aggregate
   rescue tally" to "aggregate preservation-check tally"; `probe_id`,
   `classification`, and `claims` string values in the `results` dict
   reworded and re-counted (9→19); `DONE` stderr log lines reworded
   (`rescued_exact`/`still_failed` → `preserved_exact`/`broken`, `/9` →
   `/19`); `authorization` dict's `verbatim` field updated to this task's
   PI quote ("授权，19 块也跑 SCL L=16" — the predecessor's authorization
   text would be factually wrong here, so it was corrected rather than
   left stale; **flagged as a decision point below, D-NEW2**, since it is
   a 4th class of change beyond the three named in the task instruction).
4. **Summary field rename** (explicitly instructed, separate bullet in
   the task): `n_rescued_exact`→`n_preserved_exact` (same computation:
   `rescue.exact`); `n_still_failed`→`n_broken`, **with a definitional
   change**: the predecessor computed `n_still_failed` as "NOT
   `rescue.exact`" (which silently double-counts `undetected` blocks,
   since `undetected` implies not-exact); this packet computes `n_broken`
   as `rescue.verify_failed` specifically, per the task's literal
   instruction ("SCL 结果为 verify_failed"), giving a clean 3-way partition
   (`exact` / `undetected` / `verify_failed`) with no double-counting.
   **Flagged as decision point D-NEW1 below** since it is a behavior
   change relative to the predecessor's arithmetic, even though it is
   explicitly what the task instruction specifies.

No change to: module loading (`_load_mod`, `_load_scl_joint`), any frozen
parameter (`ARM`, `LIST_WIDTH_L`, `TOP_M`, `CRC_BITS_EXTRA`, `K1`/`K2`/`N`,
construction digest, `tag_master`, `eval_seed`), the `accepted = crc_pass
AND tag_pass` formula or any other `_rescue_block` computation, the
budget/parallelism/backstop constants (`MAX_PARALLEL=8`,
`BUDGET_WALL_S_PER_BLOCK=1200.0`, `BUDGET_RSS_GIB_PER_BLOCK=2.0`,
`HARD_TERMINATE_MARGIN_S=120.0`), `reruns` semantics, `_fidelity_check`'s
comparison logic, or the `fidelity_compromised` gating mechanism.

**Incidental, non-substantive diff noise**: a small number of em-dashes
(`—`) inside untouched docstring lines were normalized to `--` as a
side-effect of rewriting the surrounding paragraph (e.g. inside
`_load_scl_joint`'s and `main()`'s comments). No semantic content changed;
flagging for completeness since it is technically outside the three named
change categories.

Full diff text is available at `/tmp/run_py.diff` on the machine that ran
this preparation pass (not committed anywhere; regenerable at any time via
the `diff -u` command above against the unmodified predecessor).

### Decision points for the main thread (not adjudicated by this operator)

- **D-NEW1**: Is redefining "broken"/"still failed" from "not exact"
  (predecessor's `n_still_failed`) to "specifically verify_failed" (this
  packet's `n_broken`) — which changes which blocks get counted when
  `undetected` cases exist — acceptable, given the task instruction
  explicitly specifies `n_broken`＝"SCL 结果为 verify_failed"? Recommend:
  accept as specified (it is a cleaner, non-double-counting partition and
  is literally what the instruction asked for), but this operator does not
  have authority to rule on it.
- **D-NEW2**: Updating the `authorization.verbatim` field (and the module
  docstring's authorization line) to this task's own PI quote, rather than
  leaving the predecessor's quote in place unchanged, was necessary for
  factual accuracy (the predecessor's authorization text does not apply to
  this task) but is technically a 4th class of change beyond the three
  named in "只允许改三处". Recommend: accept as a necessary correction
  (an unmodified stale-but-wrong authorization string would be worse), but
  flagging since it was not literally one of the three named categories.

## 4. Static self-check performed in THIS preparation pass (no execution)

- `python3 -m py_compile workspace/m2_scl_check_g2g3_success/run.py` →
  **pass**.
- AST scan for `%`-format `BinOp(Mod)` expressions → **0 found, 0 possible
  mismatches** (all string formatting in the file uses f-strings, same as
  the predecessor).
- Path existence (existence only — `test -f`/`ls`, no file content read
  for the raw `.ttbin` primaries):
  - New output directory `workspace/m2_scl_check_g2g3_success/` → created,
    empty before this pass's writes.
  - `workspace/m2_scl_check_g2g3_success/results.json` → **absent**
    (confirmed before creating any file in this directory).
  - `workspace/data_intake_20260921/inventory.json` → exists.
  - Raw primaries for both acquisitions (`D:\Data\Raw
    Data\2026.1.13\SHG_Type2PPLN_3s_2026-01-13_162106\` and
    `...\SHG_Type2PPLN_3s_2_2026-01-13_162148\`, both a small `.ttbin`
    header file plus a `.1` continuation of ~57-59MB) → **both exist**
    (directory listing only; no byte of file content read).
  - `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
    → exists.
  - Both `per_block_outcomes.jsonl` files → exist; read (JSON lines, not
    raw timetags) for the §2 target-list confirmation.

## 5. Test / evidence matrix (acceptance IDs)

| ID | Check | Evidence |
|---|---|---|
| S1_py_compile | `python3 -m py_compile run.py` exits 0 | done in this prep pass, §4 |
| S2_ast_percent | AST scan: 0 `%`-format expressions | done in this prep pass, §4 |
| S3_paths_exist | inventory.json, both raw `.ttbin` primaries, P16 construction json, both `per_block_outcomes.jsonl` files all exist on disk | done in this prep pass, §4 (existence only) |
| S6_target_confirmation | 19-block target list, filtered from `per_block_outcomes.jsonl`, matches the independently stated expected list exactly (no stop triggered) | done in this prep pass, §2 |
| S7_no_predecessor_write | `workspace/m2_scl_rescue_g2g3/` untouched by this preparation pass | confirmed: no write tool invoked against that path this session |
| S8_no_git_write | no `git add`/`commit`/`push` invoked this session | confirmed: no git write tool invoked |
| E1_fidelity_19of19 | **Pre-EXECUTE gate**: at execution time, all 19 blocks' fidelity check must match before ANY block's rescue-result is trusted (per-block STOP, inherited D3) | pending execution |
| E2_no_new_data | `results.json["targets"]` == the frozen 19-tuple list exactly; no other block/session ever opened | pending execution (structural: `TARGETS` is a module constant, not derived from input) |
| E3_no_state_write | grep after run: no byte touched under `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/`, `.../G3-CONFIRM/`, `results/`, `comparison_bench/outputs_comparison/`, any pre-existing `workspace/m2_prior_validation/*` file, or `workspace/m2_scl_rescue_g2g3/*` | pending execution |
| E4_one_shot | `results.json` and all 19 `part_*.json` absent before the run (checked in-code); reruns counter stays 0 unless an execution-defect rerun is explicitly recorded | pending execution |
| E5_budget | per-block wall/RSS recorded in each part file; any `resource_abort_*`/hard-terminate status is reported, never silently dropped | pending execution |

## 6. Timing estimate

Per this task's instruction: 19 blocks, 8-way parallel, 3 waves (8+8+3),
each wave ≈600s SCL compute (empirical same-N=32768/L=16 precedent from
`workspace/probes/scl-gate-t3/results.json`, same as the predecessor's
estimate basis) ≈ 1800s SCL compute, plus 2 sequential session-setup
passes (raw read+align+CAL fit; the predecessor's full one-shot run,
9 blocks + setup, completed in 1152.02s total, so setup-only is a modest
fraction of that) ⇒ **rough total wall estimate ≈35 minutes**, matching
the task instruction's own estimate. No global wall budget beyond the
per-block 1200s/2GiB caps.

## 7. Current state

`STATUS.yaml`: `state: prepared_awaiting_pre_execute`. This packet has
**not** been executed, has **not** been reviewed (Pre-EXECUTE not yet
requested), and its `run.py` has **not** been run. Next step is
main-thread adjudication of §3's decision points, then independent
Pre-EXECUTE review.
