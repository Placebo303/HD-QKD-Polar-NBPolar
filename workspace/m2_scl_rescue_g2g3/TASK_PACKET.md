# TASK PACKET — m2-scl-rescue-g2g3

Per AGENTS.md §3/§10.1/§10.3: this document authorizes NOTHING by itself.
Execution requires (in order): (1) independent Pre-EXECUTE review PASS on
THIS packet, (2) the PI authorization already on file (verbatim below,
2026-09-28 — already given, no re-paste needed per the task instruction that
created this packet), (3) Pre-RESULT review before `results.json` is treated
as a finished artifact or cited in any adjudication/decision-log entry.
**This preparation pass did NOT execute anything and did NOT read raw
.ttbin data content** (only file-existence checks — see §6).

## Main-thread rulings (2026-09-28)

The main thread adjudicated the open questions raised in the first
preparation pass (§0/§7 below, kept verbatim for audit trail — nothing in
those sections is withdrawn, this section is the ruling layered on top):

- **D1 (classification, resolves §0 / STATUS.yaml Q1)**: classified as a
  **"真实数据描述性诊断" (real-data descriptive diagnostic)**. Review rigor
  matches Tier-Y (independent Pre-EXECUTE AND Pre-RESULT both required); no
  threshold, no pass/fail verdict, no state-string change, and it counts as
  **zero attempts** against any Tier-Y attempt budget anywhere.
- **D2 (output root, resolves §0 / STATUS.yaml Q2)**: keep
  `workspace/m2_scl_rescue_g2g3/` — no move to `workspace/probes/`.
- **D3 (fidelity-mismatch scope, resolves §7 R1)**: keep the per-block STOP
  implementation as-is (one block's `STOPPED_FIDELITY_MISMATCH` does not stop
  the other 8 blocks' independent processes). ADDITIONALLY: if ANY of the 9
  blocks comes back `STOPPED_FIDELITY_MISMATCH`, `results.json` gets a
  top-level `"fidelity_compromised": true`, and `results.json["summary"]`
  reports ONLY per-block-count fields (`n_targets`, `n_fidelity_ok`,
  `n_fidelity_mismatch`, `n_errors_or_aborts`) — the aggregate rescue tally
  (`n_rescued_exact`/`n_still_failed`/`n_undetected`) is WITHHELD entirely
  from `summary` in that case (per-block `rescue` data, where it ran, still
  appears inside `results["blocks"][*]`). Implemented in `run.py::main()`.
- **D4 (budget mechanism, resolves §7 R2)**: accepted as specified — per-block
  soft check before starting the SCL call, parent-process hard `terminate()`
  at budget+120s as the actual stop mechanism. No change needed.
- **F1 (accepted-definition correction)**: `accepted` was `tag_pass` alone in
  the first draft; **corrected to `accepted = crc_pass AND tag_pass`**, to
  match the T3 gate convention already used in
  `workspace/probes/scl-gate-t3` (reviewed PASS_WITH_COMMENTS). `crc_pass`
  and `tag_pass` are both recorded as separate fields regardless. `exact =
  accepted AND label_exact`; `undetected = accepted AND NOT label_exact`
  (isolated, never merged into `exact`); `verify_failed = NOT accepted`.
  Implemented in `run.py::_rescue_block()`.

Note: `prereg.md` is left byte-unchanged (it is the frozen pre-registration
record); its step-(b) text still reads `accepted(=tag_pass)`, which F1
supersedes. Treat this TASK_PACKET.md section and `run.py::_rescue_block()`
as authoritative for the `accepted` formula, not `prereg.md`'s original
wording.

Re-ran the static self-check after the F1/D3 code changes:
`python3 -m py_compile run.py` → pass; AST `%`-format scan → 0 expressions
found (all f-strings), 0 possible mismatches. See STATUS.yaml
`static_selfcheck` (updated in place with a `rechecked_after_ruling` note).

## 0. Classification (open question — see STATUS.yaml Q1; RESOLVED by D1 above, kept for audit trail)

This is a **descriptive real-data re-decode diagnostic**, not cleanly either
of AGENTS.md's two tiers:

- **Not Tier-X** (§10.4): Tier-X forbids "artifact/real-data access"; this
  script reads real SHG `_1`/`_2` `.ttbin` timetags.
- **Not Tier-Y**: it renders no threshold, no pass/fail verdict, creates no
  candidate/accepted token, and changes no frozen state string
  (`NBPOLAR_M2_PRIOR_G2_SUCCESS` / `NBPOLAR_M2_PRIOR_G3_SUCCESS` / the M2
  status ladder all stay exactly as G2/G3 left them).
- It also consumes **no new EVAL data** — the 9 target blocks were already
  decoded and recorded by G2/G3; this only re-decodes them with a different
  decoder and counts how many come back exact.

Proposed treatment (pending main-thread confirmation): review it with the
SAME rigor as a Tier-Y Pre-EXECUTE/Pre-RESULT pass (frozen contract, explicit
authorization, target-output absence, focused checks, independent
re-verification of the fidelity-check result before the rescue count is
cited anywhere) but without threshold/verdict machinery, since there is no
threshold to gate on — the result is a raw count out of 9, explicitly
labelled non-claim in `results.json["claims"]`.

## 1. Scope

### Allowed to write (additive only; must not pre-exist)

- `workspace/m2_scl_rescue_g2g3/results.json`
- `workspace/m2_scl_rescue_g2g3/part_<SESSION>_<block>.json` (9 files)
- `workspace/m2_scl_rescue_g2g3/session_setup_execution_error_attempt1.json` —
  coordinator-authorized exception (2026-09-28), added after attempt 1 died
  during session setup with zero measurement before any block was touched
  (see main-thread instruction and STATUS.yaml `execution.attempt_1`); not
  in the original scope, permitted specifically for this pre-measurement
  implementation-defect record, per AGENTS.md §10.4's "an implementation-
  defect death before any measurement may be relaunched once after a fix,
  error record kept as results.execution_error_attempt1.json" convention.
- `workspace/m2_scl_rescue_g2g3/EXECUTION_TRANSCRIPT.md` — written after
  attempt 2 completed (exit 0), per main-thread instruction (2026-09-28).

### Allowed to read

- Raw `.ttbin` for `20260113_SHG_Type2PPLN_3s` (SHG `_1`) and
  `20260113_SHG_Type2PPLN_3s_2` (SHG `_2`) — via the SAME frozen readers G2/G3
  used (`_read_timetags_production` / `_read_timetags_g3_production`); no new
  acquisition, no different window/skip/MOD.
- `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/per_block_outcomes.jsonl`
  and `.../20260113_SHG_Type2PPLN_3s_2_g3/per_block_outcomes.jsonl` (read-only,
  for the fidelity check).
- `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
  (frozen P16 construction, digest-pinned, read via
  `verify_predecessor_construction` — never re-derived).
- `scripts/m2_prior_validation.py`,
  `comparison_bench/src/comparison_bench/formal_ir/{prior_m2.py,nbpolar/*.py}`
  — imported, never edited.

### Forbidden (hard stop if touched)

- Any edit to `sc.py`, `scl.py`, `scl_joint.py`, `two_layer.py`,
  `transform.py`, `algebra.py`, `prior.py`, `prior_m2.py`,
  `operational_f13*.py`, `m2_prior_validation.py`, or any other file under
  `src/`, `experiments/`, `tools/`, `comparison_bench/src/`.
- Any write under `results/`, `comparison_bench/outputs_comparison/`, or any
  EXISTING directory under `workspace/m2_prior_validation/` (this packet only
  reads `per_block_outcomes.jsonl` there).
- Any edit to `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/` or
  `.../NBPOLAR-M2-PRIOR-G3-CONFIRM/` (STATUS.yaml, freeze configs, or any
  other file in those packet dirs).
- Any change to `NBPOLAR_M2_PRIOR_G2_SUCCESS` / `NBPOLAR_M2_PRIOR_G3_SUCCESS`
  / the M2 status ladder, in this or any other document.
- Drawing any EVAL frame/block outside the 9 named targets, or any CAL/HELDOUT
  frame for any purpose other than reproducing the SAME CAL fit G2/G3 already
  used.
- git commit/push of any kind (operator scope is preparation only per this
  task's instructions).

## 2. Functionality (what `run.py` does)

1. Refuse to run if `results.json` or any target `part_*.json` already
   exists (one-shot, additive-only).
2. For each session (G2 once, G3 once — NOT per block): re-derive
   `frames_a`/`frames_b` via the exact frozen pipeline (`_read_timetags_*`,
   `_align_frozen`, `_yield_sweep_selfcheck`, `_sweep_accept`,
   `pair_narrow_nearest_unique(window=200)`, `chunk_frames(skip=702)`),
   re-verify the alignment reproduction gate bit-exact against the session's
   own frozen literals (`G3_REPRO_GATE` for G3; the G1R2 contract's
   `repro_gate` for G2 — same values `run_stage_g2`/`run_stage_g3_decode`
   already assert), fit the B-arm (`B_M2_32f_candidate`) M2 CAL prior via
   `fit_g2_arm`, derive `p1_table`/`p2_table`, verify the frozen P16
   construction digest, and compute the session-level H_total/disclosure
   bookkeeping (§5).
3. For each of the 9 target (session, block) pairs, in its OWN process (fork,
   ≤8 concurrent):
   a. **Fidelity check**: call the frozen `run_g2_block` (the SAME SC block
      body G2/G3 used) on that exact block, and diff `outcome`,
      `first_error_coordinate`, `first_error_layer`, `l1_exact`,
      `hard_l2_exact` against the frozen `per_block_outcomes.jsonl` row. Any
      diff ⇒ record `status=STOPPED_FIDELITY_MISMATCH` and skip step (b) FOR
      THAT BLOCK ONLY (see §7 R1 for the scope-of-STOP clarification).
   b. **Rescue**: call `scl_joint_decode` (L=16, top_m=4) with the SAME
      `p1_table`/`p2_table`, SAME frozen L1/L2 disclosure positions/values,
      and a CRC-16 computed from Alice's true label (the caller-computed
      `crc_true` the module's docstring requires). Recompute the per-block
      Toeplitz tag with the SAME `operational_seed_bits(tag_master, N,
      block_index)` stream G2/G3 used, against the SCL candidate label.
      Record `label_exact`, `crc_pass`, `tag_pass`, `accepted (=crc_pass AND
      tag_pass — corrected per main-thread ruling F1, 2026-09-28, to match
      the `workspace/probes/scl-gate-t3` gate convention; the first draft
      had `accepted=tag_pass` alone)`, `exact (=accepted AND label_exact)`,
      `undetected (=accepted AND NOT label_exact, isolated, never merged
      into exact)`, `verify_failed (=NOT accepted)`, plus descriptive
      `l1_error_symbols_scl` /
      `l2_error_symbols_scl` (new fields; Hamming distance of the SCL
      high/low hats vs Alice truth — not part of the frozen G2/G3 schema).
   c. Enforce a per-block 1200s wall / 2GiB RSS budget (soft check before
      starting the SCL call; the parent process backstops with a hard
      `terminate()` at budget+120s — see §7 R2 for why this is a backstop,
      not a mid-call preemption).
   d. Write exactly one `part_<SESSION>_<block>.json`.
4. Collect the 9 part files into one `results.json` (frozen params,
   authorization record, per-session disclosure/H_total bookkeeping, the 9
   block records, a summary count, and an explicit non-claim statement).

## 3. Frozen contract (verbatim; see `prereg.md` for the copy-paste command)

| Key | Value | Source |
|---|---|---|
| Target blocks | G2: 1,5,12; G3: 0,1,2,4,10,11 (9 total) | `workspace/analysis/g2g3-layer-attribution/REPORT.md` §3/§4 |
| Arm | `B_M2_32f_candidate` | same report; only arm with verify_failed-but-l1-mostly-exact structure the task targets |
| Decoder | `scl_joint_decode`, `list_width_L=16`, `top_m=4` | PI ruling 2026-09-27 (M=4 constraint), `scl_joint.py` `TOP_M_DEFAULT=4` |
| CRC | CRC-16/CCITT-FALSE, 16 bits, disclosed once | `scl_joint.CRC_BITS=16` |
| K1/K2 | 319/6492 | `G2_K1`/`G2_K2` (= `FROZEN_K1`/`FROZEN_K2`) |
| N | 32768 | `G2_N` |
| P16 construction | pinned digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` | `G2_CONSTRUCTION_PATH`/`G2_CONSTRUCTION_DIGEST` |
| Window/skip/MOD | 200 / 702 / CIRCULAR | inherited G1R2 contract, unchanged |
| tag_master (G2) | 2026103001 | `G2_TAG_MASTER` |
| tag_master (G3) | 2026110101 | `G3_TAG_MASTER` |
| eval_seed (G2) | 2026093001 | `G2_EVAL_SEED` |
| eval_seed (G3) | 2026100101 | `G3_EVAL_SEED` |
| Venv | `/home/karel_303/.venvs/timetagger/bin/python` | same as G2/G3 (needs TimeTagger shim + fail-closed pandas stub) |
| Per-block budget | wall ≤1200s, RSS ≤2GiB | this task's instruction |
| Parallelism | ≤8 concurrent (fork), one process per block | this task's instruction; WSL 8-core/15GB |
| Reruns | 0 (one-shot); a rerun to fix an execution defect is a separate recorded attempt, never a silent overwrite | AGENTS.md §10.1/§10.4 |

## 4. Test / evidence matrix (acceptance IDs)

| ID | Check | Evidence |
|---|---|---|
| S1_py_compile | `python3 -m py_compile run.py` exits 0 | done in this prep pass, see STATUS.yaml |
| S2_ast_percent | AST scan: 0 `%`-format expressions (all f-strings) ⇒ 0 possible placeholder/arg mismatches | done in this prep pass |
| S3_paths_exist | inventory.json, both raw `.ttbin` primaries, P16 construction json, both `per_block_outcomes.jsonl` files all exist on disk | done in this prep pass (existence only, no content read) |
| S4_attr_crosscheck | every `mod.*`/`chain.*`/`scl_joint_mod.*`/`res.*` attribute `run.py` references exists in the actual frozen source (grep cross-check, not execution) | done in this prep pass |
| S5_signature_match | every frozen-function call in `run.py` matches the real function's parameter names/order (manual line-by-line check against the read source) | done in this prep pass |
| E1_fidelity_9of9 | **Pre-EXECUTE gate**: at execution time, all 9 blocks' fidelity check must match before ANY block proceeds to rescue (§7 R1 resolves whether a single mismatch stops only that block or the whole run) | pending execution |
| E2_no_new_data | `results.json["targets"]` == the frozen 9-tuple list exactly; no other block/session ever opened | pending execution (structural: `TARGETS` is a module constant, not derived from input) |
| E3_no_state_write | grep after run: no byte touched under `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/`, `.../G3-CONFIRM/`, `results/`, `comparison_bench/outputs_comparison/`, or any pre-existing `workspace/m2_prior_validation/*` file | pending execution |
| E4_one_shot | `results.json` and all 9 `part_*.json` absent before the run (checked in-code); reruns counter stays 0 unless an execution-defect rerun is explicitly recorded | pending execution |
| E5_budget | per-block wall/RSS recorded in each part file; any `resource_abort_*`/hard-terminate status is reported, never silently dropped | pending execution |

## 5. Disclosure bookkeeping (session-level, computed once per session)

- `kdb_no_crc = 5*(K1+K2) + 64 = 5*6811 + 64 = 34119` (matches the frozen
  `key_dependent_bits` G2/G3 already recorded for every block).
- `kdb_with_crc = kdb_no_crc + 16 = 34135`.
- `H_total_bits`: computed via the frozen `model_entropy_bits(fit["joint"],
  p_b, prior_mod)` helper on each session's OWN B-arm CAL-fit joint (the SAME
  helper/formula the project already uses for this quantity — see
  `docs/decision-log.md` line ~5906 for the identical `f_book = kdb/(H*N)`
  convention on a synthetic point; here H is computed from the REAL CAL fit,
  not assumed).
- `f_book_no_crc = kdb_no_crc / (H_total_bits * N)`,
  `f_book_with_crc = kdb_with_crc / (H_total_bits * N)`.
- These 4 numbers are computed ONCE per session (G2, G3) and stamped onto
  every block record for that session in `results.json["per_session"]`, since
  K1/K2/CRC/H_total are all block-invariant (derived from CAL only).

## 6. Static self-check performed in THIS preparation pass (no execution)

- `python3 -m py_compile run.py` → pass.
- AST scan for `%`-format expressions → 0 found, 0 possible mismatches.
- Path existence (existence only, `os.path`/`ls`, no file content read):
  - `workspace/data_intake_20260921/inventory.json` → exists.
  - Raw primaries for both acquisitions (Windows path
    `D:\Data\Raw Data\2026.1.13\SHG_Type2PPLN_3s_2026-01-13_162106\...ttbin`
    and `...SHG_Type2PPLN_3s_2_2026-01-13_162148\...ttbin`, i.e. the same
    files the inventory's POSIX `/mnt/d/...` paths resolve to under WSL) →
    both exist (primary + `.1` continuation, ~59-60MB each).
  - `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
    → exists.
  - Both `per_block_outcomes.jsonl` files → exist; the 9 target rows were
    read (JSON, not raw timetags) and independently confirmed to match
    REPORT.md's table exactly (`verify_failed`, `l1_exact=True` for 8/9,
    `l1_exact=False` for G3 block 11, `hard_l2_exact=False` for all 9).
- Manual attribute/signature cross-check (§4 S4/S5) against the actual
  `scripts/m2_prior_validation.py` and
  `comparison_bench/.../nbpolar/{operational_f13.py,scl_joint.py,two_layer.py}`
  source — every call site matches a real, currently-defined signature.

## 7. Notes / clarifications flagged for the main thread (R1/R2 RESOLVED by main-thread rulings D3/D4 above; kept verbatim for audit trail)

- **R1 (scope of the fidelity STOP)** — RESOLVED by **D3**: per-block STOP
  implementation kept as-is; PLUS the new top-level `fidelity_compromised`
  flag and summary-suppression behavior described in D3 above. Original text
  follows unchanged. The originating instruction says "任何
  一块不一致，立即 STOP，不进入 (b)". `run.py` implements this as a PER-BLOCK
  stop (that one block's worker records `STOPPED_FIDELITY_MISMATCH` and never
  calls the rescue step; the other 8 blocks' independent processes are
  unaffected). If the intent was a GLOBAL stop (abort the entire run the
  moment any one block's fidelity check fails), that would need an
  orchestration change (e.g. a shared abort flag checked before each rescue
  call) — flagging so the main thread can confirm before Pre-EXECUTE review,
  since a global-stop design is a materially different run shape.
- **R2 (budget enforcement is a backstop, not a preemption)** — RESOLVED by
  **D4**: accepted as specified, no change. Original text follows unchanged.
  `sc_decode`/
  `scl_decode` are atomic library calls with no internal checkpoint; a
  block's own soft check can only refuse to START an over-budget rescue call,
  never interrupt one mid-flight. The parent process's hard `terminate()` at
  budget+120s is the actual stop mechanism for a runaway block. This mirrors
  how G2/G3's own budget check works (checked only BETWEEN blocks, never
  mid-SC-call) — not a weaker guarantee introduced by this packet.
- **R3 (timing)**: `workspace/probes/scl-gate-t3/results.json` (T2/T3, already
  PASS_WITH_COMMENTS-reviewed) gives an empirical same-N(32768)/same-L(16)
  precedent: ~600s wall per SCL-joint block, ~0.65GiB RSS per 16-block batch.
  Scaled to our per-process-per-block design and 8-way parallelism: ≈600s for
  the first 8 blocks (concurrent) + ≈600s for the 9th (waits for a slot) ≈
  1200s of SCL compute, plus two sequential one-time session-setup passes
  (raw read + align + CAL fit — no empirical timing on file for this exact
  step, but G2's own full one-shot run, including 126 SC calls across 3 arms
  × 14 blocks, completed in 855.1s total; the setup-only portion, i.e.
  everything before the per-block loop, is a small fraction of that). Rough
  total wall estimate: 25-35 minutes. No global wall budget is imposed beyond
  the per-block 1200s/2GiB caps (per this task's instructions).
- **R4 (venv)**: `run.py` needs pandas absent (or fails safely, per
  `_load_g2_decoder_chain`'s fail-closed stub) and the TimeTagger shim
  present, so it must run under the SAME venv G2/G3 used
  (`/home/karel_303/.venvs/timetagger/bin/python`), not the
  `hd-qkd-polar-comparison` venv the synthetic Tier-X probes use.
