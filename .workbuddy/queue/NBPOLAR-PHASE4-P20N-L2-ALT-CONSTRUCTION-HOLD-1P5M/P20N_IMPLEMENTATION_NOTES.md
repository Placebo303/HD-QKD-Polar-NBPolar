# P20N Stage-A implementation notes (2026-09-19)

Packet: `NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M`. Stage A only;
Stage B is NOT authorized and was NOT executed. No commit/push.

## 1. Files changed (exact paths)

New (both untracked additions; nothing else was written outside the packet
dir and the `workspace/p20n/` scratch root):

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py`
  — the thin P20N runner (2866 lines; sha256
  `d101831bc54f65096bfbb505afebdbe37b965540d52b572cd29b7d5a50bf9082`).
- `comparison_bench/tests/test_nbpolar_l2_alt_hold_1p5m.py`
  — focused injected tests (740 lines; sha256
  `ecb4b323e224b5b3c686201f223f567dce90acbaa10cbca33278c71d159676dd`).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz`
  — the frozen Stage-A alt-L2 table (§§3/9; 25430240 B; file-bytes sha256
  `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/P20N_FREEZE.md`
  — this freeze (all pins, D1 literals, D2 outcome).
- `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/P20N_IMPLEMENTATION_NOTES.md`
  — this file.
- `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/STATUS.yaml`
  — updated in place, stage-true.
- `workspace/p20n/derive_4qZWFV5C/derive_stdout.json` — the exact stdout of
  the single Stage-A derivation (tiny provenance capture; temp scratch root).

NOT changed: `src/`, `experiments/`, `tools/`, every accepted
`comparison_bench/.../formal_ir/nbpolar/*.py` (including
`l1_order_1p5m.py`, `raw_prior_val_1p5m.py`, `prior.py`,
`per_session_calibration.py`, `target_construction.py`), the P20M accepted
products (`raw_prior_1p5m.npz`, `raw_prior_orders_1p5m.json`,
`raw_prior_val_1p5m/`), X08/X09 probe roots, `results/`,
`comparison_bench/outputs_comparison/`, the P20N OpenSpec delta (spec +
tasks were staged by the planner at freeze time), and the packet's
`TASK_PACKET.md` / `PROMPT.md` / `AUTHORIZATION_PROMPT.md`.

Read-only reuse evidence (module hashes at Stage-A close, matching their
pre-session values — computed with sha256 over file bytes):

| accepted module | sha256 |
|---|---|
| `l1_order_1p5m.py` | `3bc6865f2bd3fbc558253cf1d1d693f3678666d89a1c88e3052c23b32e0e036d` |
| `raw_prior_val_1p5m.py` | `a9adc19aa53769a5449626b5ba60bf2929d48558fc8547681eb30d03d0835b6f` |
| `prior.py` | `c6fb48cbe718636f52063da82892519b0ec87bd43d56a57f97d5b0ea80f7ee32` |
| `per_session_calibration.py` | `c0d8d960b53191ccb884f56ea743815b000e98656648d8ac761d0708afdb0a31` |
| `target_construction.py` | `2adb50449019c12063998d362dc3ee9acf810abc0548ff27a0e43942b346d347` |

The pre-existing dirty worktree entries (` M` set: 27 files, all recorded
before this session) were preserved untouched; the only new tracked-status
entries are the two untracked files above.

## 2. §2 delta-list evidence (d1–d7), nothing else

- **d1 alt-L2-table source**: `verify_alt_l2_identity()` /
  `verify_alt_l2_arrays()` (module: file-bytes sha256 against
  `FROZEN_ALT_DIGEST`, α==1.0 pin, floor==1e-15 pin, exact 9-key set,
  `p1` equality vs the P20M artifact within 1e-12, `h1_inc` literal +
  `h_total_alt` consistency + `h2_alt` recomputation via `entropy_bits`,
  column/axis normalization). `run_derive_stage_a()` writes the artifact
  (fail-if-present) and computes the D1/D2 literals.
- **d2 K carried**: `FROZEN_K1/K2/K_TOTAL` = 331/6689/7020 module
  literals; `check_k_literals()` replays them and compares the carried
  budget-literal display, never reading the alt-H; the per-arm leaks are
  the frozen `5*(K1+K2)+64` / `5*K2+64` arithmetic.
- **d3 orders**: `verify_stage_b_order_file_p20m` (accepted P20M helper)
  is called with `expected_prior_digest=FROZEN_INCUMBENT_DIGEST`,
  `expected_k1=331`, `expected_k2=6689`, `expected_k_total=7020`; the same
  `l1_order`/`l2_order` arrays feed all four arms (first-331 / first-6689
  prefixes), zero sampling.
- **d4 arms**: four hardcoded `ArmSpec`s in `frozen_arm_table()` +
  `check_frozen_arm_table()` (A incumbent/331/6689, B alt/331/6689, C
  incumbent oracle, D alt oracle; B−A and D−C key-bit deltas exactly 0);
  no CLI surface can change them.
- **d5 tag domain**: `l2_alt_hold_1p5m_seed_bits()` with master
  `2026092300` and prefix `nbpolar-p20n-l2-alt-hold-1p5m-seed` (validated
  against `FROZEN_ARM_NAMES`; differs from every prior packet domain).
- **d6 instrumentation**: `_l2_hazard_diagnostics()` (the eight exact
  scalars, gated `l2_prefix_len == 6689`, radius R=8, natural block index
  space, true-cell prefix means, null-unless-L2 fail fields) called
  post-decode from `_operational_record()` / `_control_record()` at the
  carried-over P20M code point — the accepted
  `raw_prior_val_1p5m.py:1306-1334` `_selected_diagnostics` callsite
  pattern (P20M's `_selected_diagnostics` itself is reused read-only for
  the carried floor/NLL fields). Recording-only: the recorder's outputs
  are written into the record dict and are never passed to
  `run_operational_block`, `run_oracle_control_block`, `_decode_layer`,
  metric builders, disclosure or order decisions; pinned by
  `test_truth_isolation_recording_only`.
- **d7 HOLD population**: `form_hold_blocks()` mirrors the accepted VAL
  `form_dev_blocks` validation for the HOLD pool (first 512 HOLD frames
  2213..2724, four 128-frame blocks, remainder 2725..2766 counted never
  decoded, `(frame_id, pair_idx)` lexsort only, no sampling); gate family
  (b)–(f) in `verify_hold_containment()` /
  `verify_consumed_exclusions()`; cross-file identity (a) via the
  accepted `verify_dev_source_identity`; alt-identity + order-freeze +
  K-literal (g) before any SC call.
- Reused read-only helpers (no reimplementation): `run_operational_block`,
  `run_oracle_control_block`, `verify_predecessor_construction`,
  `verify_dev_source_identity`, `verify_dev_manifest`,
  `verify_corrected_prior`, `verify_stage_b_order_file_p20m`,
  `budget_literal_display`, `raw_prior_val_1p5m_block_events`,
  `raw_prior_val_1p5m_recount_events`, `_stat_record`, `_block_view`,
  `_dev_block_scoring`, `_scoring_absent`, `_selected_diagnostics` (P20M),
  plus `opf._check_chunk_contract` / `_check_tag_bits` / `_budget_exceeded`
  / `_cell_resource_record` / `_peak_rss_bytes` / `_write_json` /
  `_append_jsonl` / `OperationalBlockResult` (P20A machinery).

## 3. Exact commands and results

Stage-A derivation (executed EXACTLY once; no rerun; exit 0; in-process
wall 0.572503 s, command 4.594 s real):

```bash
cd /mnt/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_1p5m --derive --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alpha 1 --floor 1e-15 --out .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz
```

Result (stdout JSON verbatim in
`workspace/p20n/derive_4qZWFV5C/derive_stdout.json`): `alt_digest`
`6f4a4f76…2333e78`, `counts_total` 424960, `floor_hits` 0, `zero_columns`
0, `f_alt` range `0.000665335994677302`–`0.24762550881953543`,
`p1_equality_max_abs_diff` 0.0, D1 `ce_alt` `0.9027311772313849` /
`ce_incumbent` `0.8003665547439149` / `alt_ideal_length_bits`
`29580.69521551802`, D2 **FEASIBLE**, protected opens 0, sampling/genie/
decoder calls 0, worktree-npz opens 1.

Focused tests (frozen interpreter, fresh `workspace/p20n/<uuid>/` roots,
`pytest -p no:cacheprovider`):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_l2_alt_hold_1p5m.py -p no:cacheprovider -q
```

- Before the pin fill: `16 passed, 1 warning in 31.48s`.
- After the pin fill: `16 passed, 1 warning in 30.34s`.
- Coverage: frozen literals/arms/command, α=1 rule vs independent literal
  (all 7 test seeds), artifact key set/dtype/α/floor/digest + fail-if-
  present, alt-identity gate positive + digest/α/`p1`/key-set refusals,
  D1 estimator exactness (hand-computed 1.375 bits), D2 both branches,
  CLI mode/missing-flag refusals, K/floor/source/n/tag-master digest
  refusals, the eight §7 scalars with nullability + exact formulas,
  recording-only truth-isolation sentinel (post-decode callsite, truth
  mutation cannot change decode fields), HOLD formation + gate family
  (b)–(f) refusals, no Stage-B root, zero-sampling/zero-seed-flag pins,
  one-open reload refusal, repo grep rule.
- The one warning is the repository's pre-existing
  `PytestConfigWarning: Unknown config option: cache_dir` (benign).

Command checks:

- `FROZEN_COMMAND` is byte-identical to the
  `<FROZEN_AT_STAGE_A>`-filled `AUTHORIZATION_PROMPT.md` STEP-2 block
  (programmatic equality check, printed `True`).
- `sha256sum` independently re-derived the artifact file-bytes digest
  `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`.

## 4. Read audit at Stage-A close (separate counters)

- V25 counts-calibration content opens: **0** (budget 0/0).
- 1.5M HOLD parquet content opens/stats: **0** (budget 0/1, reserved for
  an authorized Stage B).
- VAL-remainder reads: **0**.
- Reserved 2M open/stat/listing/read: **0** (pristine by non-access).
- Worktree P20M-npz reads: **1** (the single authorized Stage-A
  derivation; no-reopen guard consumed once) — a worktree-file read, not a
  protected counts open.
- Real-data decoder execution: **0**. Stage-B output root: **ABSENT**.
- Attempts used: **0/1**.

## 5. Predecessor-suite status (honest)

`comparison_bench/tests/test_nbpolar_raw_prior_val_1p5m.py`: 16 passed,
3 failed. All three failures are PRE-EXISTING, environment-dependent
Stage-A-era assertions that P20M's own accepted Stage-B execution
invalidated — not caused by this Stage-A work (no accepted file was
touched):

1. `test_no_stage_b_root_and_no_protected_opens_in_stage_a` and
2. `test_cli_modes_refuse_before_read_write` both assert
   `not Path(pm.FROZEN_OUT_ROOT).exists()`; P20M's authorized Stage-B
   evidence root exists (created 2026-09-19 10:53).
3. `test_grep_rule_seed_placement` asserts the P20M master `2026092280`
   appears only in P20M-scoped files; `AGENT_PROJECT_MEMORY.md` (modified
   2026-09-19 11:01, before this session) now records it.

Both timestamps precede this session's first write; the two new P20N files
contain none of the P20M literals.

## 6. Grep-rule evidence (master 2026092300 + test seeds 2026092301..2026092307)

`git grep -l --untracked -E "202609230[0-7]" -- comparison_bench openspec
.workbuddy docs workspace` returns exactly the allowed P20N documents:

```
.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/AUTHORIZATION_PROMPT.md
.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/PROMPT.md
.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/STATUS.yaml
.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/TASK_PACKET.md
comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py
comparison_bench/tests/test_nbpolar_l2_alt_hold_1p5m.py
openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20n/spec.md
openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md
```

The frozen master `2026092300` lives in the runner; the focused-test seeds
`2026092301..2026092307` live only in the test file (asserted by
`test_grep_rule_seed_placement`). No derivation seeds exist: the Stage-A
derivation is closed-form arithmetic with zero sampling, zero genie calls
and zero RNG use (`test_zero_sampling_pin_and_no_seed_flags` pins the
absence of `np.random`/sampler/seed-flag code paths in the module).

## 7. OpenSpec delta

`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20n/spec.md`
and the `tasks.md` P20N section were staged by the planner at freeze time;
this Stage-A session neither edited nor checked any task box (per the
packet: "No box above is checked by the implementing session").

## 8. Honest scope (verbatim, TASK_PACKET.md §0)

this packet tests ONE preregistered alternative L2 construction at fixed
disclosure on the first HOLD-segment use; it can restore L2 or falsify this
construction; a budget-infeasible construction is returned without consuming
HOLD; it licenses no reliability/recovery claim; 2M and VAL remainder
remain untouched; the 1M-HOLD thread stays open.
