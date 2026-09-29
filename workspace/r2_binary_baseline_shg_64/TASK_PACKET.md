# TASK PACKET — r2-binary-baseline-shg-64

Per AGENTS.md §3/§10.1/§10.3/§10.4: this document authorizes NOTHING by
itself. This is a **descriptive comparison measurement** (real-data,
consumes the SAME already-protected 64-block pool NB-Polar's `r2-fer-shg-64`
used) — not a Tier-Y decision gate (no win/lose threshold is computed) but
still real-data and one-shot, so it follows the same discipline: independent
Pre-EXECUTE review, explicit PI authorization, and Pre-RESULT review before
any publication. Execution requires, IN ORDER:

1. `docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md` read and
   accepted (no open blocking items per its §11).
2. Independent Pre-EXECUTE review PASS on this packet (AGENTS.md §10.3).
3. Explicit PI authorization, verbatim, pasted from `AUTHORIZATION_PROMPT.md`
   (currently a template — the 2026-09-29 PI direction "起草合同，reviewer
   核查合同后可以直接开始" is directional, not itself the execution text).
4. After execution: independent Pre-RESULT review PASS before any
   `RESULT_SUMMARY.md`/decision-log entry cites `results.json`.

**This preparation pass did NOT execute anything, did NOT run any real-data
decode of the 64-block pool, did NOT read raw `.ttbin` content, and did NOT
modify `src/`, `experiments/`, `tools/`, `comparison_bench/src/`, or
`workspace/r2_fer_shg_64/`.** No git write of any kind was performed. The
only real-data-adjacent step taken was building/running a SYNTHETIC smoke
test (`_smoke_synthetic.py`, this directory) against small in-memory
synthetic symbol arrays, never against acquisition data.

## 0. Delta relationship to `workspace/r2_fer_shg_64/`

This is NOT a delta-successor in the AGENTS.md §10.1/§10.4 sense (different
codec family, different decoder, different claim shape — descriptive, not
Tier-Y). It IS a **hard dependency**: it imports
`workspace/r2_fer_shg_64/run.py` BY FILE PATH (read-only) to reuse
`build_session_blocks`/`_reproduce_session_context`/`SESSION_CFG`/`ARM`
unchanged, guaranteeing byte-identical `(frames_a, frames_b)` symbol arrays
and identical `stratum_official`/`stratum_task` block metadata — this is the
PI-requested fairness/comparability mechanism (contract §2), not an
independent re-implementation.

## 1. Scope

### Allowed to write (additive only)

- `docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md` (already
  written, this preparation pass).
- `workspace/r2_binary_baseline_shg_64/` (this directory; new).

### Allowed to read

- `workspace/r2_fer_shg_64/run.py`, `RESULT_SUMMARY.md`, `results.json`,
  `STATUS.yaml` — read-only reference (imported by file path for the
  functions named above; NOT modified; NOT executed as `__main__`).
- `src/reconciliation/real_polar_sc_rescue.py`, `cpp_scl_wrapper.py`,
  `verification.py`, `cpp_polar/main.cpp` — imported/inspected, never edited.
- `experiments/run_real_polar_max_pie.py` — imported for `calc_crc16`,
  `_build_candidates`, `_simulate_layer_sc_fer_early`, never edited.
- `scripts/m2_prior_validation.py` — imported transitively via the
  `workspace/r2_fer_shg_64/run.py` re-import, never edited directly by this
  packet.
- `docs/nbpolar/DATA_LEDGER.md`, `AGENTS.md` — read-only planning sources.
- Raw `.ttbin` for `20260113_SHG_Type2PPLN_3s` / `_2` — via the SAME frozen
  readers the NB packet uses, transitively, at execution time only (NOT
  touched by this preparation pass — existence/listing only, inherited from
  the NB packet's own prior confirmation).

### Forbidden (hard stop if touched)

- Any edit to `sc.py`/`scl.py`/`scl_joint.py`/`two_layer.py`/`transform.py`/
  `algebra.py`/`prior.py`/`prior_m2.py`/`operational_f13*.py`/
  `m2_prior_validation.py`/`real_polar_sc_rescue.py`/
  `run_real_polar_max_pie.py`/`cpp_scl_wrapper.py`/`verification.py`/
  `cpp_polar/main.cpp`/`run_e2e_pipeline.py`, or any other file under
  `src/`, `experiments/`, `tools/`, `comparison_bench/src/`.
- **Any write to `workspace/r2_fer_shg_64/`** (read-only reference only).
- Any write under `results/`, `comparison_bench/outputs_comparison/`, or any
  EXISTING directory under `workspace/m2_prior_validation/`.
- git commit/push of any kind.
- Running `run.py` against real data without `--authorize` AND an on-record
  PI authorization AND Pre-EXECUTE PASS (enforced in code: `run.py` refuses
  without `--authorize`; the OTHER two gates are process discipline, not
  code-enforced, matching the NB packet's own precedent).
- CAL32/EVAL/HELDOUT/A1_CAL frame boundaries: never drawn outside the
  frozen 64-block pool (inherited from the NB packet's own frozen block
  descriptors; this packet never re-derives frame ranges independently).

## 2. Binary-baseline API inventory (evidence trail)

See `docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md` §1 for
the full file:line evidence table (construction, rate allocation, decoder,
verification, native N choices, the CA-SCL CRC-embedding finding). Not
repeated here to avoid drift between two copies of the same evidence.

## 3. Design decisions (self-adjudicated per "closest to the baseline's own
native practice"; flagged, not hidden)

- **D_BIN_PRIMARY_ARM**: SC chosen as the primary/claim-bearing arm; CA-SCL
  is descriptive-only. Rationale: CA-SCL's internal CRC path-selection
  (`main.cpp:213-237`) requires overwriting 16 real u-domain bits/codeword
  with a computed CRC, which SC's single-path decode does not need. See
  contract §1 finding row and §11. **Recommend: accept as specified** — the
  alternative (design a CRC-preserving reconciliation protocol for CA-SCL)
  is out of this task's scope/effort budget.
- **D_BIN_CODE_LENGTH**: N=4096 (largest of the frozen {1024,2048,4096}).
  **Recommend: accept** — minimizes relative per-codeword overhead; a
  smaller N is a numerical alternative, not a structural blocker.
- **D_BIN_LAYER_INDEPENDENCE**: 10 bit-planes decoded independently, no
  MSD-conditional refinement (the sibling Release repo's improved scheme is
  out of scope per AGENTS.md §0). **Recommend: accept** — this is what
  "reuse the frozen baseline's own layer order and conditioning" means
  concretely, confirmed by `_extract_real_layer_bers`'s own independence.
- **D_BIN_F_GRID_SEARCH_RANGE**: `sc_margin` is a SHORT candidate list
  `{0.02, 0.05, 0.08, 0.12, 0.18, 0.25, 0.30}` (7 points), not a fine
  arange sweep — REVISED from an initial dense-sweep draft after a
  concrete performance finding (§6 below / contract §3.1) showed the
  dense-sweep version was computationally infeasible. **Recommend:
  accept** — `--dry-run-one` will still reveal whether this list contains
  a point near NB-Polar's `f_book_with_crc`; if not, widening the list is
  a non-blocking, easily-changed numeric parameter.
- **D_BIN_SC_DECODER_COMPLEXITY** (new finding, not in the original design):
  `polar_sc_decode_with_frozen` (`src/reconciliation/real_polar_sc_rescue.py:90-134`)
  is O(N² log N) per frame (re-runs the full `_encoding_step` propagation
  at every leaf position), not the standard O(N log N) SC decoder
  complexity — measured 80.8 ms/call at N=4096 post-JIT
  (`_selfcheck_sc_timing.py`). This made the packet's ORIGINAL
  `CALIB_N_FRAMES=4000` + dense `sc_margin` sweep design infeasible
  (confirmed by a real attempt that ran >8 CPU-minutes without finishing,
  killed). **Resolved in this same preparation pass**: `CALIB_N_FRAMES`
  lowered to 100 (the frozen baseline's own `--frames` CLI default, not an
  arbitrary smaller number) and the margin sweep replaced by the 7-point
  list above (echoing the baseline's own `--scl-margins` short-list
  style). Re-verified via the synthetic smoke test (N=256 override, 5.6s
  wall) and a fresh timing probe. **Recommend: accept the revised
  numbers** — flagged prominently because it changes the contract's own
  §3/§6 numbers from the version PI's directional go-ahead was based on;
  the Pre-EXECUTE reviewer should re-check this arithmetic specifically.
  **Corrected total-time arithmetic (Pre-EXECUTE round 1, C2 fix)**:
  contract §3.1's ~75 min worst-case construction-search estimate
  (7×10×8×100×80.8ms) is PER SESSION, not both sessions combined — with 2
  sessions (G2, G3) the construction total is ~150 min, plus ~28 min for
  the 64-block × ≤4-grid-point SC decode itself (contract §3.1 item 4),
  giving a combined estimate of **~178 min ≈ 3.0 h**, which still clears
  the §6 4 h total-wall budget with margin. The PASS-worthy conclusion
  ("budget is generously conservative") is unaffected; only the earlier
  write-up's per-session-vs-combined framing was imprecise.
- **D_BIN_TAG_REUSE**: block-level tag reuses `verification.py`'s
  `universal_hash_tag` (this repo's own frozen scheme) rather than
  NB-Polar's `chain.toeplitz_tag` (a different, also-frozen, function in a
  different module) — both are Toeplitz-style universal hashes; using each
  method's OWN native verification function (rather than importing NB's tag
  function into the binary side) was judged the more faithful "reuse each
  baseline's own machinery" reading. **Recommend: accept**; either choice
  is defensible and this is flagged for main-thread awareness, not because
  it is contested.

## 4. Evidence that the reused functions are reused, not re-derived

- `_polar_weight_order`, `polar_encode_non_systematic`,
  `polar_sc_decode_with_frozen`: imported from
  `src.reconciliation.real_polar_sc_rescue`, called with no signature
  changes (`run.py` here imports them via `_load_binary_baseline_functions`).
- `PolarSCLDecoder`: imported from `src.reconciliation.cpp_scl_wrapper`,
  instantiated with `force_rebuild=False` (its own designed self-build path,
  unchanged).
- `universal_hash_tag`: imported from `src.reconciliation.verification`,
  called with no signature changes.
- `calc_crc16`, `_build_candidates`, `_simulate_layer_sc_fer_early`:
  imported from `experiments.run_real_polar_max_pie`, called with no
  signature changes.
- `build_session_blocks`, `_reproduce_session_context`, `SESSION_CFG`,
  `ARM`, `_load_mod`, `_load_scl_joint`: imported from
  `workspace/r2_fer_shg_64/run.py` BY FILE PATH
  (`importlib.util.spec_from_file_location`), called with no signature
  changes. `mod.g2_cal_ids` is reached transitively via the NB packet's own
  `mod` (the `scripts.m2_prior_validation` module), not re-imported
  separately.
- Involution/self-inverse property of `polar_encode_non_systematic`
  numerically confirmed against the ACTUAL frozen function (not assumed):
  `_selfcheck_involution.py`, this directory, `n_log in {2,3,4,6}`, 30
  random trials each, 0 failures.

## 5. Static self-check performed in THIS preparation pass

- `python3 -m py_compile workspace/r2_binary_baseline_shg_64/run.py` →
  **pass** (WSL `hd-qkd-polar-comparison` venv).
- AST scan for `%`-format `BinOp(Mod)` expressions (`_selfcheck_ast_percent.py`)
  → **0 found**.
- Synthetic (non-real-data) smoke test (`_smoke_synthetic.py`): see §6.

## 6. Test / evidence matrix (acceptance IDs)

| ID | Check | Evidence |
|---|---|---|
| S1_py_compile | `python -m py_compile run.py` exits 0 | done, §5 |
| S2_ast_percent | AST scan: 0 `%`-format expressions | done, §5 |
| S3_involution | `polar_encode_non_systematic` is self-inverse (numeric) | done, `_selfcheck_involution.py` |
| S4_smoke_construction | `freeze_binary_construction` on a synthetic layer-BER profile returns <=MAX_F_POINTS usable grid points | **done, PASS** — 3 grid points found, wall 5.6s (N=256 smoke override) |
| S5_smoke_sc_decode | SC decode of a synthetic low-BER codeword is exact; disclosed_bits == N-k | **done, PASS** — layer0 k=176, disclosed_bits=80=256-176 |
| S6_smoke_tag | tag(true)==tag(true); tag(true)!=tag(1-bit-corrupted) | **done, PASS** |
| S7_smoke_accounting | per-block measured `sc_disclosed_total` == analytically expected, over 2 synthetic blocks | **done, PASS** — 329728==329728 over 2 blocks |
| S12_sc_timing | quantify `polar_sc_decode_with_frozen`'s real per-call cost at N=4096/1024/256 | **done** — `_selfcheck_sc_timing.py`: 80.771/4.420/0.244 ms/call post-JIT; confirms O(N² log N), drove the D_BIN_SC_DECODER_COMPLEXITY revision in §3 |
| S8_results_absent | `results.json` and any TOP-LEVEL `part_*.json` absent before a full launch | directory was empty before this pass's writes; **enforced in code since Pre-EXECUTE round-1 F3 fix** (`main()` `_fail`s if `results.json` OR any top-level `part_*.json` exists; `--dry-run-one` outputs live under `dry_run/` and neither trigger nor are reused by that check). Earlier wording ("checked in-code") was inaccurate before the F3 fix: only `results.json` was checked. Tested by `_test_f3_guard.py` (S14). |
| S14_f3_guard_test | `_test_f3_guard.py`: temp dir, real-data loaders mocked to raise; fake top-level part file / results.json -> `SystemExit(2)` before any loader; `dry_run/` files do not trigger the guard; dry-run outputs land only under `dry_run/` with `dry_run=True`; `_load_all_part_records` rejects `dry_run=True` at top level | see round-2 report |
| S9_no_predecessor_write | `workspace/r2_fer_shg_64/` untouched | confirmed: no write tool invoked against that path this session |
| S10_no_git_write | no `git add`/`commit`/`push` invoked | confirmed |
| S11_no_frozen_edit | no edit tool invoked against any file under `src/`, `experiments/`, `tools/`, `comparison_bench/src/` | confirmed |
| S13_aggregation_unit_test | `_test_aggregation.py`: fake part-records covering ok/exact, ok/verify_failed, ok/undetected, ok/decode_failed, resource_abort, block-level error+empty-grid; plus fake nb_parts covering frame-mismatch and missing-in-nb branches | **done, PASS** — all pooled/stratum/session/f_breakdown/tag_bits-recovery/cross-comparison counts hand-verified to match |
| E1_cal32_only_construction | `construction_frozen_<SESSION>.json` written BEFORE any block decode begins, derived only from `mod.g2_cal_ids(ARM)` symbols | structural (code order in `main()`); pending execution |
| E2_no_new_frame_range | every decoded block's `(frame_start,frame_end)` is one of the NB packet's own 64 frozen block descriptors | structural (blocks come from `nb_mod.build_session_blocks`, never independently derived); pending execution |
| E3_one_shot | `results.json`/`part_*.json` absent before run (checked in-code); `reruns` stays 0 unless an execution-defect rerun is explicitly recorded | pending execution |
| E4_budget | SERIAL single process. Total wall 4 h checked in code (`_run_sessions`: before each session's construction and before each block; exceeded => remaining blocks recorded `not_started_total_wall_budget`, running block finishes); per-block wall 1200 s cumulative from block start (checked before each grid point); RSS 4 GiB by VmHWM after each grid point; nothing silently dropped | mechanism implemented (Pre-EXECUTE round-2 F4) and unit-tested with a mocked clock (S15); real behaviour pending execution. There is NO parallelism and NO parent hard-terminate (earlier text claiming 8-way/fork/hard-terminate was wrong and has been removed) |
| S15_total_wall_test | `_test_total_wall.py`: fake clock + mocked runners/construction; W1-W5 (not_started after budget, pre-construction check, exceeded-at-start, dry-run path, block accounting, INSUFFICIENT) plus W6 (D_BIN_TWO_PASS): pass 2 truncated -> SC 8/8 blocks complete, D unchanged with/without CA-SCL records, CA-SCL entries marked `ca_scl_not_started_total_wall_budget`, Tables A/B1 unchanged, B2 coverage stated | see round-3 report |
| S16_two_pass | Execution is TWO-PASS (D_BIN_TWO_PASS): pass 1 = both constructions, then SC primary arm over all blocks x grid points; pass 2 = CA-SCL arm into separate `scl_part_*.json` (never rewrites `part_*.json`), total-wall checked before each block; full-run guard also refuses if any top-level `scl_part_*.json` exists | implemented in `run.py::_run_sessions`, `_run_scl_block_entry`; tested by S14 (G7) and S15 (W1, W6) |
| E5_no_verdict | `results.json` contains no win/lose or PASS/FAIL string (contract §5: descriptive only) | structural, by construction (`aggregate_results`/`build_cross_comparison` emit only counts/rates, never a verdict string); unit-tested against fake data (S13); pending a real execution to confirm on real output |
| E6_nb_readonly | `workspace/r2_fer_shg_64/`'s own decode is never re-run; only its committed `part_*.json` files are read | structural (`load_nb_parts` only opens files, calls no decode function); confirmed by code inspection + S13 |

## 7. Aggregation (RESOLVED 2026-09-29, per main-thread requirement)

**Full-run aggregation is now implemented** in `run.py`:
`aggregate_results()` builds, per `sc_margin` grid point, the pooled /
`stratum_official` / `stratum_task` / per-session taxonomy (exact/
verify_failed/decode_failed/undetected/resource_abort, `D`, `p_hat`,
Wilson(z=1.96)) using the SAME ok-only-into-`D` convention as
`workspace/r2_fer_shg_64/run.py`'s own reviewed `_taxonomy_counts`
(`_binary_taxonomy_counts`, verbatim field names/rule); `stop_undetected`
scans ALL blocks/margins regardless of status; each margin's `f_breakdown_by_session`
carries the per-layer disclosed-bit/CRC/tag decomposition plus `H_total`/
`f_book_sc`/`f_book_scl` (read straight from `construction_frozen_<SESSION>.json`,
never recomputed at aggregation time). `load_nb_parts()` reads
`workspace/r2_fer_shg_64/part_*.json` READ-ONLY (that packet's decode is
NEVER re-run) and `build_cross_comparison()` produces the three 2x2 tables
(§4.1/§5 of the contract: Table A same-strength NB-SC vs binary-SC; Table
B1 NB-SCL vs binary-SC; Table B2 NB-SCL vs binary-CA-SCL's explicitly-
caveated message-exact proxy), matched by `(session, global_block_index)`
with an explicit `frame_start`/`frame_end` equality check per pair
(mismatches are LISTED, never silently dropped) — this is the closest
available analogue to "hash-check same block" given the NB packet's own
`part_*.json` files do not persist a raw-symbol hash themselves; this
packet's own `block_hash` (SHA-256 of the raw `(x,y)` arrays) is still
recorded per block for audit, and equality with the NB side is guaranteed
BY CONSTRUCTION since both import the identical
`_reproduce_session_context`/`build_session_blocks`, not by a runtime hash
comparison against a value the NB side never wrote.

`main()` now calls this aggregation + cross-comparison at the end of a
full (non-`--dry-run-one`) run and writes `results.json`.

Round-2 additions (F4/C4/C5/C6): `results.json` now carries `block_accounting`
(64 = contributing + error + not_started + resource_abort [+ no_grid_entries, expected 0],
`consistent` flag), `error_block_ids` (block-level `error:*`, incl. mid-block exceptions),
`not_started_block_ids`, top-level `n_blocks_contributing`, per-margin `insufficient`
(pooled D<56), `timing` (per-session construction wall, total wall) and
`construction_search_wall_s_by_session`. Per-margin tallies only include block-level
status=="ok" blocks (as in the NB packet); `undetected` scanning still covers ALL records.
Cross tables put undetected entries in the non-exact cell; `stop_undetected` is global.

Verified by a NEW unit test (`_test_aggregation.py`, this directory) using
hand-built FAKE part-file-shaped records covering every `status` branch
(ok/exact, ok/verify_failed, ok/undetected, ok/decode_failed [schema
completeness], `resource_abort_wall_mid_grid`, and a block-level `error:*`
status with an EMPTY `grid` list) plus a hand-built fake `nb_parts` dict
exercising the frame-mismatch and missing-in-NB-parts branches of
`build_cross_comparison`. **PASS** (see report for the exact counts
checked). This is a pure-Python test with NO real part files and NO real
data — `_smoke_synthetic.py` (also PASS) separately covers the decode/
construction/tag chain end-to-end on synthetic symbol data.

## 8. What this preparation pass explicitly did NOT do / still does NOT finish

- CA-SCL's own `.so` build was NOT exercised in the synthetic smoke test
  (kept the smoke fast and independent of a g++ toolchain call); the SC
  arm and the tag/accounting/aggregation/cross-comparison chains were
  smoke-tested, which covers the packet's PRIMARY claim-bearing path. CA-SCL
  remains descriptive-only and its unavailability (build failure) is
  designed to be non-fatal to the SC arm (`run.py::main`'s `try/except`
  around `PolarSCLDecoder(...)`).
- No real 64-block execution was performed; `results.json` in this
  directory does not exist. The aggregation code above has only been
  exercised against fake/synthetic data, never against a real
  `part_*.json` set produced by an authorized run.

## 9. Return conditions

- **Complete**: contract accepted, packet passes Pre-EXECUTE review, PI
  authorization on file verbatim, execution runs to completion or to a
  recorded STOP condition, Pre-RESULT review requested.
- **Blocked**: none currently identified (see contract §11 — all open items
  are non-blocking, self-adjudicated per stated principles). If the main
  thread disagrees with any §3 decision here, report the specific item; do
  not silently re-decide.

## 10. Current state

`STATUS.yaml`: `state: prepared_awaiting_pre_execute_review_and_pi_authorization`.
This packet has **not** been executed against real data, has **not** been
reviewed (Pre-EXECUTE not yet requested), and `run.py` refuses to run
without `--authorize`. Aggregation (§7) is now implemented and unit-tested
against fake data. Next step: main-thread review of §3's decisions, then
independent Pre-EXECUTE review.
