# Pre-EXECUTE review — Phase 4-P18 N=32768 1M-HOLD operational microcheck

- Task: `NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK` (Tier Y, claim-bearing single attempt)
- Reviewer: independent reviewer-go (backup instance), read-only
- Date: 2026-09-16 (WSL), HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e`, branch `codex/nbpolar-phase0`
- Scope: frozen packet + Wave-A artifacts + protected-input resolution + tests + budgets, not the run itself
- **Verdict: PASS** — no blocking issues; executed exactly as frozen after main-thread acknowledgement of the rulings below.

## Review provenance and closures (read first)

- This review NEVER content-opened the V25 TRAIN NPZ or the HOLD pairs parquet. Both were
  inspected only through `ls -la`, `stat`, `os.walk` and JSON metadata reads.
- `train_artifact_reads_used = 0/1`, `hold_data_reads_used = 0/1`, `attempts_used = 0/1`
  (STATUS.yaml, unchanged after this review); output root
  `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/`
  was absent before and after this review (`ls -d` -> "No such file or directory").
- The only file written by this review is this document. Test runs used fresh `/tmp`
  basetemps and `-p no:cacheprovider`; no repo-bound process ran the real gate command.
- Side-effect scan after the review (`find . -newermt "2026-09-16 01:10"`, excluding `__pycache__`)
  returned no entries.

## Complete frozen record (as reviewed)

| item | frozen value | verification |
|---|---|---|
| packet | `TASK_PACKET.md` 100 lines, mtime 2026-09-15 23:24 | `wc -l` = 100; unmodified |
| authorization | `AUTHORIZATION_PROMPT.md` present, one NPZ read + one parquet read + one attempt | read; `execution_authorized: true` |
| predecessor | `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE_ACCEPTED_MODEL_SAMPLED` | matches P17 `STATUS.yaml` state and P17 main-thread acceptance |
| P16 identity | N=32768, K1=319, K2=6492, K_total=6811, leakage=34119, f=1.2998502888172847, digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` | recomputed read-only via `verify_predecessor_construction` -> exact match |
| split manifest | `nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1M = 400 HOLD frames / 102400 HOLD pairs (TRAIN 1200/307200, VAL 400/102400) | JSON read both checkouts; JSON-equal; values match |
| NPZ (protected #1) | `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz` | stat only: 25,166,822 B, mtime 1787074449; worktree copy absent |
| HOLD parquet (protected #2) | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet` | stat only: 1,354,289 B, mtime 1789155517 (Sep 12 03:38:37); resolved under this worktree |
| blocks | 1600..1727 / 1728..1855 / 1856..1983 (128 frames = 32768 pairs each); remainder 1984..1999 = 16 frames / 4096 pairs, unused | code + tests |
| tag | master 2026092050, 64-bit Toeplitz, P18 domain prefix `nbpolar-p18-holdout-microcheck-seed`, per block 0..2 | code L129/L178/L1526-1529; tests prove scored seeds are P18-domain and differ from P16/P17 |
| decoder path | one L1 + one candidate-conditioned L2 SC per block, P16 orders/K, `chunk_rows=512` (`_minus_block` keyword-only default), `sc_decode` no chunk arg | `_check_chunk_contract` L445-461 in operational_f13.py; sc.py L176 signature |
| budgets | 600 s external `timeout`, `ulimit -v 2097152`, 2 GiB RSS cap, `OPENBLAS/OMP/MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2` | command block + constants |
| output root | `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/`, exactly five files | absent now; file list frozen in `OUTPUT_FILES` |
| reads/attempts | 0/1, 0/1, result null, reviews pending | STATUS.yaml |
| tests | focused 26; full NB-Polar 409 (383 + 26) | reproduced by this review |
| frozen command | `P18_FREEZE.md` section 5 == `holdout_microcheck.FROZEN_COMMAND` byte-for-byte | programmatic string equality = True |

## Checklist (PASS/FAIL per required item)

### 1. STATUS exactness + RESUMED-RUN provenance — PASS

Command: `cat .workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/STATUS.yaml`
Raw: `state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`; `tier: Y`;
`execution_authorized: true`; `train_artifact_reads_allowed: 1` / `used: 0`;
`hold_data_reads_allowed: 1` / `used: 0`; `attempts_allowed: 1` / `used: 0`;
`result: null`; `pre_execute_review: pending`; `pre_result_review: pending`;
`next_gate: INDEPENDENT_PRE_EXECUTE`. All exactly as declared; predecessor string matches
the P17 accepted state.

Resumption adjudication (resumed interrupted run):
- Queue directory holds exactly the allowed 6 pre-run files: `TASK_PACKET.md`,
  `STATUS.yaml`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `P18_FREEZE.md`,
  `P18_IMPLEMENTATION_NOTES.md`; no output root, no sidecars (command: `ls -la`).
- mtime-scope scan `find . -path ./.git -prune -o -type f -newermt "2026-09-16 00:00" -print`
  returns only: `P18_FREEZE.md` (01:08), `P18_IMPLEMENTATION_NOTES.md` (01:09),
  `STATUS.yaml` (00:33), `holdout_microcheck.py` (00:35), `test_nbpolar_holdout_microcheck.py`
  (00:34), `specs/nbpolar-phase4-p18/spec.md` (00:32), `tasks.md` (00:32) and the two
  `__pycache__` byproducts of the test runs. Nothing else in the repo was written in the
  wave window; no accepted module or old root appears.
- Doc corrections verified accurate, not merely asserted: this review re-ran the focused
  file (26 passed) and the full `test_nbpolar_*.py` suite (409 passed), so the corrected
  "26 focused / 409 total (383 + 26)" counts are reproducible; earlier 25/408 counts were
  indeed stale. R9 is present in `P18_IMPLEMENTATION_NOTES.md` (lines 174-183).
- Frozen inputs unopened: `reads_used = 0`, `attempts_used = 0`, root absent, and both
  protected files are only stat-visible (see items 5 and 12). Resumption compliant.

### 2. OpenSpec P18 delta consistency, boxes unchecked — PASS

- `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p18/spec.md`
  (167 lines, 6 `## Requirement:` sections) matches the packet on every frozen item:
  predecessor/manifest verification before any root or open; one content open per input
  with attempt consumption at the NPZ; exact HOLD formation and remainder; frozen
  operational path with orders/K/chunk/10-bit label/P18 tag domain; truth boundary;
  scalar-only five-file schema; integrity-gate order and no-threshold label rule;
  sixteen required flags with no production defaults; budgets and forbidden paths.
  Style matches the accepted P17 delta (`## Requirement:` form, no Scenarios).
- `tasks.md` P18 section (lines 945-1042): all nine items `- [ ]`; `grep -c '\- \[x\]'`
  over the section = 0; closing note "No box above is checked by the implementing session".

### 3. Reuse + immutability, P11 chunk plumbed — PASS

- mtimes of all reused modules predate the wave: `sc.py` 2026-09-14 19:35,
  `prior.py` 09-12, `two_layer.py` 09-13, `target_construction.py` 09-14,
  `operational_f13.py` 09-15 16:27, `operational_f13_replication.py` 09-15 19:38,
  `pairs_loader.py` 09-12, `v35_algorithm_development.py` 09-12, `shared.py` 09-12,
  `nbpolar/__init__.py` 09-13. No writes in the Sep 16 window (item 1 scan).
- P16 root untouched: `operational_f13_gate/` five files 2581862 / 2586645 / 6991 /
  42760 / 2529 B, mtimes 2026-09-15 18:28 (sizes identical to `P18_FREEZE.md` section 10).
  P17 root untouched: five files mtimes 2026-09-15 21:42. No `holdout_microcheck` dir
  anywhere in the tree (only the absent frozen root path).
- Reuse is by import, proven structurally: `test_accepted_helpers_shared_not_reimplemented`
  asserts `hm.run_operational_block is opf.run_operational_block` and
  `hm.verify_predecessor_construction is opr.verify_predecessor_construction`.
- P11 chunk contract plumbed: `opf._check_chunk_contract(512)` (L1016) inspects
  `sc._minus_block` (`chunk_rows: int | None = 512`, keyword-only, L176-177) and
  `sc_decode` (no chunk parameter, L216); `run_operational_block` reaches `sc_decode`
  via `_decode_layer` with the production default.

### 4. Identity ordering before opens; tamper probes injected-only — PASS

Code order in `holdout_microcheck.py`:
absent root L1006 -> frozen flag contracts L1008-1024 -> digest-flag pin L1030-1031 ->
P16 predecessor identity L1032 -> split manifest identity L1034 -> one-open guards
L1039-1042 -> input existence + stat-only records L1044-1070 -> five-file stubs
L1125-1138 -> NPZ content open L1148 -> HOLD content open L1183. CLI parsing happens in
`main` before `run_holdout_microcheck`. Every refusal above raises before the stubs exist.
- P16 identity recomputed in this review: digest exact match; N/K1/K2/K_total/leakage/f
  all match the frozen record; orders are length-32768 permutations.
- Manifest read (JSON only) declares 400/102400 for `type2_1M_20260121_184040`.
- Tamper probes use fabricated construction/manifest files in temp dirs only
  (`make_construction_file`, `make_manifest`, test L118-183); the real P16 file is never
  written; test refusals assert `assert not root.exists()` with forbidden loaders/arm.

### 5. Protected path resolution — PASS (adjudicated; see ruling below)

(a) Resolved worktree file exists, stat only: 1,354,289 B, mtime 1789155517
    (Sep 12 03:38:37), 2648 blocks.
(b) Competing copies found (stat only, no content read):
    `/mnt/d/Code/HD-QKD_Polar_Comparison/.../type2_1M_20260121_184040/pairs.parquet`
    (1,354,289 B, mtime Sep 10 19:05:50) and
    `/mnt/d/Code/HD-QKD_Polar_Comparison-worktree-cascade-single/.../pairs.parquet`
    (1,354,289 B, mtime Aug 30 08:39). All three copies are size-equal mirrors.
    Whole-tree metadata comparison of the two same-project trees (nbpolar vs sibling,
    `os.walk` + `stat` only): 741 vs 746 files; the only omitted files are the four
    25,166,822-byte `channel_counts.npz` and one unrelated `per_block.jsonl`; 0 binary
    files differ in size; all 685 size differences are text files (.json/.csv/.jsonl/
    .md/.txt) grown by CRLF conversion (+1 byte per line, e.g. manifest 803 -> 849 B).
    The mirrored `split_manifest.json` is JSON-equal across checkouts; the shared
    `v13r3fresh_pairs_20260816/build_manifest.json` is JSON-equal and records the origin
    path `D:\Code\HD-QKD_Polar_Comparison\...\pairs.parquet`, size 1354289 and
    sha256 `1b89728751bc3535ea5917fccb581ee446f411ba0cf38c6b3f1a23fd9081af93`
    (a pre-run content hash is impossible without a prohibited content read; size and
    copy-provenance evidence is the available substitute).
(c) No FAIL: no competing true source is demonstrably different. All copies are
    size-equal; the entire mirrored tree preserved every binary byte count; text
    differences are CRLF-only. The package resolves the parquet to the running
    checkout's mirror and pins only the NPZ to the cross-checkout absolute path because
    the mirror omits it (L137-140). That is the documented, tested constant and the
    frozen command's cwd makes it deterministic.

### 6. One-open/consumption design; R9 — PASS (R9 ratified)

- Exactly one content open per input in code order (NPZ L1148, parquet L1183); module
  flags `_NPZ_CONTENT_OPENED`/`_HOLD_PARQUET_CONTENT_OPENED` (L293-295) refuse reopen at
  L1039-1042 before any I/O; accounting records `counts_content_opens=1`,
  `hold_content_opens=1`, `attempts_consumed_by_this_run=1` (L1150-1151, L1185-1188),
  consumption point "first protected content open" (L180/ATTEMPT_CONSUMPTION_POINT).
- stat-before at L1051/L1063 (before any content open), stat-after at L1466/L1469; the
  `input_stat_unchanged` gate compares size+mtime.
- MemoryError is caught around the entire post-open path (try opens at L1126 before the
  stubs, closes with `except MemoryError` L1508-1514 -> finalize BLOCKED(resource...) ->
  `HoldoutMicrocheckResourceError`); the per-block generic handler re-raises MemoryError
  (L1406-1407) rather than converting it to `decode_failed`.
- R9 ruling: **ratify, no repair.** The post-open plain-`ValueError`/`KeyError` branches
  (L1154 source-missing, L1158-1159 counts shape, `normalize_pair_columns` malformed
  table) are defensive and unreachable for the verified frozen inputs (the NPZ is the
  exact artifact loaded successfully by accepted P16 and P17 with the same loader; the
  parquet is the registered artifact loaded by the accepted pipeline; sizes/mtimes are
  pinned). On such a branch the five stubs survive, the process exits non-zero, and the
  Wave-C rule below classifies the outcome as STOP with the attempt consumed. Rewriting
  tested post-open control flow for an unreachable branch is not warranted.

### 7. HOLD formation, path and calls — PASS

- `form_holdout_blocks` (L567-691): `np.lexsort((pair_idx, frame_id))`; exactly 400
  frames 1600..1999; 102400 rows; `pair_idx` equals tiled 0..255; symbols 0..1023;
  blocks 1600..1727/1728..1855/1856..1983 at exactly 32768 pairs; remainder 1984..1999
  = 16 frames / 4096 symbols recorded `used: False`. No RNG anywhere (independent grep:
  `np.random`, `default_rng`, `random_state`, `bootstrap`, `polyfit`, `curve_fit`,
  `FWHT`, `adaptive`, `oracle` all 0 occurrences).
- One L1 + one candidate-conditioned L2 per block through the accepted
  `run_operational_block` (L1531-1552) with verified orders/K1/K2 and the chunk
  contract; 10-bit label via `labels_to_bits`; one 64-bit tag per block with P18-domain
  seed (L436-464, L1526-1529).
- Six SC calls / three tags enforced as recomputed maxima (`sc_calls_exact` L1700-1710,
  `tags_exact` L1711-1715): a partial `decode_failed` block stays descriptive, matching
  the packet's "COMPLETE regardless of 0..3 exact" while keeping the 6/3 plan.
- Truth boundary: accepted sentinel path plus `provenance_violations` counter (L1435-1436,
  L1717-1720); tests assert PRIOR_ONLY/CANDIDATE_CONDITIONED provenance on every executed
  block and array immutability.

### 8. Outputs / labels / thresholds — PASS

- Five files created as stubs before any content open (L1125-1138), checkpointed after
  every block including abort-filled blocks (L1387-1391, L1457-1460; `persist` rewrites
  identity + aggregate + report and appends the jsonl). No sidecars.
- Scalar-only records (L1555-1584): frame range, raw SER, per-layer/total NLL (+per-pair),
  outcome bucket, L1 correctness, tag result, 34119/327743 constants + actual bits,
  wall/RSS-HWM/VmPeak/VmSize; banned-key walk test (`test_five_file_scalar_only_inventory_and_resources`)
  passes.
- No threshold path: independent grep of the module for `wilson|Wilson|recovery_gates|
  EXACT_MIN|exact_fraction|fer_rate|thresholds|rtol` = 0; `hold_microcheck_label`
  (L694-703) consumes only the integrity gates; `decision.recovery_threshold = None`.
- COMPLETE for 0/3 and 3/3 exact is covered by `test_no_threshold_labels_zero_and_three_exact`
  (green); `BLOCKED(<earliest gate>)` ordering from `INTEGRITY_GATE_ORDER` (L190-208);
  resource abort-fill path finalizes `BLOCKED(resource_limits_met_and_no_abort)`
  (`test_budget_stop_abort_fill_and_precedence`).

### 9. R8 invented CLI flags — PASS (ratified; verbatim command below)

- The packet has no P18-05 command block; five flags were necessarily invented
  (`--hold-pairs`, `--hold-frames`, `--block-frames`, `--remainder-frames`,
  `--tag-master`). They pin the second protected input, the registered block/remainder
  ranges and the public seed domain, and each is refusal-checked before any open.
- Independent verification: the `P18_FREEZE.md` section 5 bash block equals
  `holdout_microcheck.FROZEN_COMMAND` byte-for-byte (programmatic comparison = True);
  `build_parser()` exposes exactly the 16 required flags, all `required=True`, no
  defaults; parsing the frozen argument vector yields exactly the frozen values
  (counts absolute, source 1M, floor 1e-15, n 32768, k1 319, k2 6492, construction +
  digest, hold-pairs relative, hold-frames 1600 1999, block-frames 128,
  remainder-frames 1984 1999, tag-master 2026092050, chunk-rows 512, tag-bits 64,
  out-dir relative). `--help` loads cleanly with exit 0.
- Ratified. Verbatim Wave-C command (frozen record; four lines):

```
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_microcheck --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --hold-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --hold-frames 1600 1999 --block-frames 128 --remainder-frames 1984 1999 --tag-master 2026092050 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck
```

### 10. Tests — PASS

Commands (pinned interpreter, fresh `/tmp` basetemps, `-p no:cacheprovider`):
- `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/p18_review_focused_FBed8V comparison_bench/tests/test_nbpolar_holdout_microcheck.py`
  -> **26 passed** in 23.64 s.
- same settings over `comparison_bench/tests/test_nbpolar_*.py` (25 files)
  -> **409 passed** in 1452.42 s. Matches the corrected 383 + 26 arithmetic.
- Smoke subset (`-k "five_file or budget_stop or tiny_real_block or malformed_hold_population_run_level or memory_error"`)
  -> 5 passed in 6.45 s (five files pre-open; checkpoint/abort-fill; tiny real SC block;
  run-level BLOCKED five-file inventory; MemoryError classification).
- Independent open-audit: ran the focused file under a `builtins.open` interception
  plugin (PYTHONPATH=/tmp, guard sanity-checked to fire on both protected basenames):
  **0 attempted opens** of any path containing `channel_counts.npz` or
  `v13r3fresh_pairs_20260816`; 26 passed. The runner tests additionally replace both
  loaders with asserting stubs.
- Coverage vs P18-04: identity refusal/zero-read/zero-root; exact slicing + malformed
  frame/row/pair/symbol; both one-open guards; structural no-fitting/sampling plus exact
  call counts; P16 orders + P18 tag-domain proof; truth isolation sentinel +
  immutability; all six buckets + precedence; NLL/SER/34119/327743/CE arithmetic +
  recount tamper; checkpoint recovery; budget abort-fill; MemoryError classification;
  `BLOCKED(<earliest>)` precedence; 0/3 and 3/3 labels; scalar-only outputs; real-mode
  accounting/stat gates via patched loaders; CLI/argparse/existing-root refusals.
- Tag-master discipline: 2026092050 appears in tests only in constant pins, disjointness
  checks and P18-vs-P16-vs-P17 seed-domain comparisons (L342/L367/L374/L379/L646-654);
  it is never used as the tag seed for real data (the scoring-domain tests use fresh
  masters 2026092064/10064).

### 11. Wall/RSS margin and bounded smoke — PASS

Projection from accepted P16/P17 evidence (JSON reads only):
- P17 per-block wall (one L1 + one L2 SC at N=32768, chunk 512): min 12.11 s,
  median 13.15 s, max 15.51 s over 128 blocks -> 3 P18 blocks <= 46.5 s using the
  observed max.
- Fixed path: P18's clock starts before the NPZ load (L1139) and covers load +
  preconditions + parquet + formation + scoring + tags. P16 ran 16 TRAIN + 64 DEV blocks
  in 1183.6 s overall; P17 ran 128 blocks in 2031.4 s overall, i.e. the identical
  load/prior/decoder class fits the same 600 s-style budget with two orders of magnitude
  fewer SC calls here. Conservative bound (max per-block + 3x adverse fixed overhead):
  <= 110 s; using the P17 whole-run overhead class as an upper bound: < 390 s. Both are
  inside the 600 s timeout; realistic projection is ~60-90 s (>= 6x margin; ~10x on the
  median-based number).
- RSS: predecessor peaks 545,861,632 B (P16) and 569,614,336 B (P17) including all
  machinery; P18 adds a 1.35 MB parquet table (102400 x 4 int64 columns, well under
  100 MB with pandas overhead) and holds 3 blocks of small vectors -> projected <= ~0.6 GB
  against the 2 GiB cap (>= 3x). The 2 GiB virtual limit (`ulimit -v 2097152`) is proven
  by two accepted runs at the same N with the same `sc.py` (pure numpy; no JIT).
- Parquet load expectation: registered 1M file = 512,000 pairs total (2000 frames x 256,
  `nonbinary_v25_gate.SOURCES` "parquet_rows": 512000); HOLD subset = 102,400 rows over
  frames 1600..1999; loader = accepted `load_pairs_table` (`pd.read_parquet`, pickle
  fallback) + `normalize_pair_columns` (int64 coercion). Load is ~1.35 MB, no sampling.
- Bounded smoke: the injected/temp-root runner tests in the focused file create the five
  files before the opens and checkpoint them per block (normal, abort-fill, blocked and
  MemoryError paths) - all green in the subset run above.

### 12. Scope and premises — PASS

- `git status --porcelain` for the declared paths: ` M tasks.md`;
  `?? .../specs/nbpolar-phase4-p18/`, `?? holdout_microcheck.py`, `?? test_nbpolar_holdout_microcheck.py`,
  `?? .workbuddy/queue/NBPOLAR-PHASE4-P18-.../`. All other modified files in the wide
  `git status` (`sc.py`, `prior.py`, empirical modules, docs, P3 queue) have mtimes
  <= 2026-09-15 and are pre-existing, unrelated to this wave; HEAD is unchanged at
  `ab173f2a` and no commit exists after the baseline.
- No accepted-module or old-root writes (item 3); P16/P17 roots stat-unchanged.
- Root absent; reads/attempts 0/1 each; NPZ stat 25,166,822 B only; HOLD parquet stat
  1,354,289 B only. No Model-F/raw/real/EVAL access anywhere in this review.

## Findings (file:line)

- `holdout_microcheck.py:1006` existing-root refusal before everything; `:1032/:1034`
  identity+manifest before root/stubs; `:1125-1138` five stubs pre-open; `:1148/:1183`
  the two single content opens; `:1150-1151/:1185-1188` consumption/accounting;
  `:1466-1470` closing stats; `:1502-1514` BLOCKED/MemoryError finalize;
  `:1531-1552` accepted block helper with P18 tag closure; `:1615-1831` gates;
  `:1834-1859` 16 required flags; `:1862-1900` exit codes.
- `holdout_microcheck.py:1154-1159`, `:1191`, `:1502-1514`, `:1883-1885` - R9 plain
  post-open `ValueError`/`KeyError` branches (unreachable for pinned inputs); ratified.
- `holdout_microcheck.py:1149-1151` - open flags/counters set after the loader returns;
  a loader-internal failure would under-report the physical open in the finalize record
  (non-blocking, see below).
- `test_nbpolar_holdout_microcheck.py:395-475` identity tamper refusals; `:480-546`
  formation; `:551-613` one-open/no-sampling; `:618-731` tag domain/truth; `:780-853`
  buckets/labels; `:859-947` five-file/recount; `:952-1042` failure paths;
  `:1047-1149` real-mode accounting; `:1154-1261` CLI/existing-root refusals.

## Non-blocking suggestions

1. R9-class disambiguation is mandatory for the operator: "exit 2 with the root present
   and `aggregate_summary.json` still `pending_content_open`" is a non-finalized
   post-open STOP (attempt consumed), not a pre-open refusal. See the Wave-C rule below.
2. The `attempt_read_accounting` counters are written after the loader returns
   (`:1150-1151`); on a loader-internal failure the finalize record would show 0 opens
   despite the physical open. For Pre-RESULT, verify the run through `input_stats_after`
   plus the message rather than the counters alone. No repair before Wave-C (unreachable
   input class; touching tested post-open code is not justified).
3. Path provenance note for the main thread: the run reads the Sep 12 worktree mirror of
   the registered parquet (metadata-equal to the sibling original and to the
   cascade-single mirror, all 1,354,289 B). Ratify the mirror convention or, if canonical
   strictness is preferred, the sibling absolute path could be substituted with no
   expected change; no evidence shows any divergence.
4. CE-ratio semantics (R3): the per-block numerator stays the nominal 34119 for partially
   invoked blocks while actual disclosure remains in the recount; aggregate
   `34119 * #NLL-blocks / sum(NLL)`. Descriptive only; keep it out of any efficiency
   language in the report.
5. `docs/decision-log.md` / `docs/troubleshooting.md` updates are not required for this
   Pre-EXECUTE gate; batch any durable entries (R9, mirror convention) with the Wave-C
   memory triage per the milestone-batching rule.

## Wave-C exit-code / label rule (binding for the operator)

1. **Exit 0** => the run finished and a finalized summary was persisted. ALWAYS read
   `holdout_microcheck/aggregate_summary.json` `outcome_label`: either
   `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE` (all integrity
   gates true) or `BLOCKED(<earliest gate>)`. Exit 0 occurs for in-run BLOCKED cases too
   (e.g. the wall/RSS abort-fill finalize), so exit 0 does NOT imply COMPLETE.
2. **Exit 2** => refusal or post-open contract stop. Disambiguate by root/stubs:
   - root ABSENT => pre-open refusal (CLI parse, existing root, flag/digest mismatch,
     predecessor/manifest mismatch, absent or wrong-sized NPZ, absent parquet): zero
     reads and zero attempts consumed.
   - root PRESENT with the five files and a `BLOCKED(...)` label =>
     `TargetPopulationContractError`/`HoldoutMicrocheckContractError` post-open stop:
     attempt consumed, checkpoints preserved.
   - root PRESENT with `status: pending_content_open` and no finalized label =>
     non-finalized post-open failure (defensive R9 branch): attempt consumed, STOP.
3. **Exit 1 with traceback** => MemoryError path (`HoldoutMicrocheckResourceError`) with
   `BLOCKED(resource_limits_met_and_no_abort)` finalized when the files exist; any other
   traceback is an unexpected failure. **Exit 124** (timeout) or any other non-zero =>
   STOP.
4. In every non-zero/ambiguous case: preserve the root, report the exact command, exit
   code and first error, and NEVER rerun, repair, retune, clean, commit or push. The
   single scientific attempt/deadline has been consumed or aborted; only the main thread
   may decide any successor.

## Closures

- NEITHER protected input was content-opened by this review (stat/JSON only; verified by
  the absence of any open in the review commands and by the focused-test open audit).
- `train_artifact_reads_used = 0/1`; `hold_data_reads_used = 0/1`; `attempts_used = 0/1`.
- Output root `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/`
  is absent; HEAD `ab173f2a` unchanged; no commit/push; no old-root writes.

**Verdict: PASS.** Execute the frozen command exactly once only after the main thread
explicitly ratifies this review (and notes rulings R8/R9 and the mirror-path convention).
