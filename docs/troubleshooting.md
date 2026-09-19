# Troubleshooting

Reusable failure modes and their fixes for the HD-QKD_Polar_Comparison project.

---

## Template

```
### <Symptom>

**Observed**: <What you see>

**Root cause**: <Why it happens>

**Fix**: <Steps to resolve>

**Prevention**: <How to avoid in future>
```

---

## Known Issues

### Phase 1 NB-Polar reference axis and empty-coordinate dtype

**Observed**: A dense field matvec broadcasts on the wrong axis, or an empty
coordinate list becomes float dtype and fails integer validation.

**Root cause**: NumPy indexing needs the source vector as `vec[:, None]` for
row-vector multiplication. `np.asarray([])` defaults to float dtype even when
the intended domain is integer coordinates.

**Fix**: Index the multiplication table with `vec[:, None]`; handle an empty
one-dimensional coordinate collection before dtype rejection and return an
explicit `int64` empty array.

**Prevention**: Retain the GF4/GF32 fast-versus-dense tests and the empty
selection test in `test_nbpolar_transform.py`.

### Pytest absent from system Python but available in Miniforge

**Observed**: `py -3.11 -m pytest` and `py -3.12 -m pytest` fail with
`No module named pytest` even though a pytest validation is required.

**Root cause**: Those system interpreters do not contain project test tools;
pytest 9.0.3 is installed in the existing Miniforge environment.

**Fix**: On this Windows host, set `PYTHONPATH` to the repository root and run
`D:/software/Miniforge3/python.exe -m pytest`. A plain-Python test runner is a
useful fallback, but it does not replace an available pytest collection check.

**Prevention**: Probe the known interpreters before reporting pytest as absent
from the machine.

### No module named pytest/numpy (bare interpreter)

**Observed**: `ModuleNotFoundError: No module named 'pytest'` (or `'numpy'`) when running a project command via bare `python -m ...` / `python3 -m ...`.

**Root cause**: bare `python`/`python3` binds the system interpreter (`/usr/bin/python3`), which lacks the project dependencies; they live in the repo-local `.venv/`.

**Fix**: use the project venv: `source .venv/bin/activate`, or run via `.venv/bin/python -m ...`.

**Prevention**: never use bare `python`/`python3` for project commands. Validate once: `.venv/bin/python -c "import numpy,pytest"`.

---

### Permission denied on pytest cache directories

**Observed**: When globbing or grepping the repo, you get `拒绝访问 (os error 5)` on files under `pytest-cache-files-*` directories.

**Root cause**: Pytest temporary cache directories have restrictive ACLs that block traversal even with read permissions.

**Fix**: These errors are harmless. Use `--glob` patterns that exclude these directories, or use tools that handle permission errors gracefully.

**Prevention**: Add `pytest-cache-files-*/` to `.gitignore`. Do not create these directories manually.

---

### .git/index.lock permission issue

**Observed**: Git operations (commit, stage) fail with `fatal: unable to create '.git/index.lock': Permission denied`.

**Root cause**: A stale lock file from a previous interrupted git operation, or concurrent git processes.

**Fix**: Remove the lock file: `Remove-Item -LiteralPath ".git/index.lock"`. If that fails, close other git clients and try again.

**Prevention**: Avoid running multiple git operations concurrently. Ensure git commands complete fully before starting new ones.

---

### Parquet fallback to pickle

**Observed**: Output files expected as `.parquet` are written as `.pkl` instead.

**Root cause**: The `pyarrow` or `fastparquet` library is not installed, so the code falls back to pickle serialization.

**Fix**: Install the optional comparison dependencies:
```bash
pip install -r comparison_bench/requirements-comparison.txt
```

**Prevention**: Ensure `comparison_bench/requirements-comparison.txt` is installed before running benchmarks.

---

### PowerShell execution policy warnings

**Observed**: PowerShell startup emits `execution-policy` warnings.

**Root cause**: The current PowerShell profile or system policy restricts script execution.

**Fix**: These warnings are non-fatal. If needed, set `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.

**Prevention**: This is an environment-level configuration issue, not a project issue. Ignore unless it blocks actual script execution.

---

### Legacy Windows paths in code

**Observed**: Some files (e.g., `polar_existing_bridge.py`) contain hardcoded Windows paths like `D:\Data\Raw Data\QKD_Loss\...`.

**Root cause**: Historical provenance paths baked into the code base.

**Fix**: These are **provenance only** — do not use them as execution defaults. For WSL, use POSIX paths via `/mnt/d/Data/...` or project-relative paths. Do not bake new Windows absolute paths into code.

**Prevention**: Use environment variables (`PROJECT_DATA_ROOT`, `PROJECT_RESULTS_ROOT`) or config keys instead of hardcoded paths.

---

### Report table generation fails on `bin_width_ps` NaN values

**Observed**: `make_report_tables.py` can fail while grouping or sorting report rows if `bin_width_ps` contains missing values.

**Root cause**: Imported or merged result rows may not have complete `bin_width_ps` metadata, especially when combining heterogeneous Polar/imported and comparison outputs.

**Fix**: Preserve the missing value semantics and handle NaN explicitly in report-table generation instead of coercing it into a misleading physical bin width.

**Prevention**: When adding report tables, treat `bin_width_ps` as nullable metadata and include missing-metadata checks in report-generation tests.

---

### Historical Cascade v3 sweep errors from missing `mapping`

**Observed**: An earlier v3 Cascade sweep sent all tasks to `run_errors_ir_v3.csv`.

**Root cause**: The CLI glue layer did not pass the `mapping` parameter into the Cascade sweep path.

**Fix**: Pass `mapping` through the CLI/config glue and rerun the affected sweep additively.

**Prevention**: Do not interpret `run_errors_ir_v3.csv` as the current total failure state without checking timestamps, param hashes, rerun outputs, and manifests.

---

### `ValueError: plan frozen equality` during formal execute after a source edit

**Observed**: A formal execute (`run_ldpc_v5_development.py execute`) aborts
before writing any artifacts with `ValueError: plan frozen equality` even
though the plan was prepared successfully minutes earlier.

**Root cause**: A prepared plan binds the frozen source hashes of the
implementation files. Any edit to those files (e.g., a performance refactor)
after prepare makes the plan's provenance check reject the current source,
by design — plans are immutable.

**Fix**: This is a source-changed-under-plan condition, not a retry. Record
the intended code change, then delete the stale official package directory
(no artifacts were written), re-prepare, main-review the new plan, and execute
once. Treat this as the single approved execute cycle.

**Prevention**: Freeze source files before `prepare`; if a code change is
needed, expect prepare/execute/verify to be invalidated and plan for one fresh
cycle with main-thread approval (recorded in the decision log).

---

### Robustness noise injections must match the decoder's error-channel model

**Observed**: An injected-symbol-error-rate sweep (uniform random symbol
replacement on Bob) failed 0/1152 even at SER 0.05, while real data at
SER 0.035–0.215 succeeds 100%.

**Root cause**: `plane_error_channel` builds the decoder prior from the frozen
calibration table only (Bob-conditioned, adjacent +/-1 at fixed probabilities,
nominal SER 0.243). Uniform replacement is out-of-distribution noise — the
prior is structurally mismatched, so even weak errors defeat decoding. This is
expected and diagnostic, not a capability boundary.

**Fix**: For capability-boundary questions, inject model-consistent noise:
adjacent +/-1 errors drawn at the frozen nominal probabilities (plus_one
3865/16384, minus_one 116/16384) — then the prior exactly matches the
distribution (validated 768/768 at SER 0.2430). Keep uniform-noise runs as
out-of-distribution controls.

**Prevention**: State the noise model of any SER sweep before running; check
it against `v5_plane_error_channel` (hardcoded `adjacent_nominal`) semantics.

---

### V13 D01 bursts_runs aggregate: run counter reset before the end check

**Observed** (2026-08-14): the recorded D01 `bursts_runs` aggregate said
`run_count=8`, `max_run_length=2`, `runs_per_frame_mean=0.0625` while
`error_symbol_fraction=0.0771` implies ~2525 error symbols — mathematically
inconsistent; a read-only recompute produced the same impossible numbers.

**Root cause**: in `nonbinary_v13_diagnostics._frame_channel_stats` the loop
body was

```python
run = run + 1 if value else 0      # zeroes run FIRST
if not value and run:              # now run is always 0 at a gap
    runs.append(run); run = 0
```

The conditional expression reset `run` to 0 before the run-end check, so only
runs ending at the LAST position of a frame (the trailing `if run: append`)
were ever recorded. 8 frames happened to end with an error → 8 phantom runs.

**Fix** (code only; the D01 package remains immutable evidence): explicit
branch — `if value: run += 1` / `else: if run: runs.append(run); run = 0`.
Corrected aggregates for the same 128 bw200 characterization frames: 2340
runs (mean 18.3 runs/frame), run-length histogram {1: 2169, 2: 157, 3: 14},
max run length 3, 185 adjacent error pairs (7.3% of errors have a neighbor) —
errors are isolated single-symbol perturbations, not bursts. Additionally,
99.3% (2508/2525) of nonzero Alice-Bob differences lie in [0,128), matching
the LSB-dominated bit-plane mismatch and the adjacent-symbol error structure
known from the binary V5 plane channel. The corrected numbers are recorded in
the 2026-08-14 D04 decision-log entry.

**Prevention**: never write `x = x + 1 if cond else 0` when the OLD value of
`x` is read after the assignment in the same block; use explicit branches.
Cross-check derived aggregates against each other (run counts must cover the
error-symbol count) before trusting them in reports.

---

### D7-B file-location fallback: top-level load of a relative-import module

**Observed** (2026-09-10, WSL): the D7-B runner loads its core by file
location (`spec_from_file_location`), and the core's
`bind_historical_decoder()` fell back to file-loading
`v35_algorithm_development.py` as a top-level module when the
`comparison_bench` package was not importable. The bind then failed with
`ImportError('attempted relative import with no known parent package')`
before any decoder call and before output-root creation.

**Root cause**: a module file-loaded under a top-level name has no parent
package, so its explicit relative imports (here v35's
`from .nonbinary_field import ...`) can never resolve. The fallback's
`except ModuleNotFoundError` only proved the first import failed; it could
not make the fallback context package-correct.

**Fix**: derive `<repo>/comparison_bench/src` from the runner's own resolved
`__file__` and insert it into the current process's `sys.path` (only if
absent) before loading the core, so the core and v35 resolve through the
normal package name `comparison_bench.formal_ir.*` against the local source
tree. No hard-coded drive/mount/cwd/PYTHONPATH, no install, no copies.

**Prevention**: never file-load a module that contains relative imports as a
top-level module; ensure its package is importable first. Keep
`except ModuleNotFoundError` fallbacks narrow so an internal dependency
`ImportError` is never misreported as a merely absent package.

---

### Combined pytest across D7/formal_ir suites: `No module named 'comparison_bench.formal_ir'`

**Observed** (2026-09-10/11, WSL): collecting the D7-A, D7-B and D7-C test files
together in one pytest process yields `199 collected, 1 error` with
`ModuleNotFoundError: No module named 'comparison_bench.formal_ir'`; the same
combined run without the new module yields `179 collected, 1 error`. Each suite
alone passes.

**Root cause**: pre-existing `comparison_bench` package namespace collision when
multiple `formal_ir` test modules are collected in a single process. It is not
caused by the D7 modules.

**Fix**: run each suite in its own pytest process (D7-C, D7-A, D7-B separately).
Combined multi-file collection is not a supported qualification path.

**Prevention**: treat per-suite process isolation as the baseline for D7
qualification; do not read the combined-collection error as a new regression.

---

### `python: command not found` in the default WSL shell

**Observed** (2026-09-10/11, WSL): bare `python` is absent from the default PATH
(`/bin/bash: line 1: python: command not found`, exit 127) even though the
project venv exists, so a frozen command that spells `python` fails before the
script starts.

**Root cause**: the WSL shell does not expose the project interpreter on PATH by
default.

**Fix**: prefix the accepted venv bin directory, e.g.
`PATH="$HOME/.venvs/hd-qkd-polar-comparison/bin:$PATH" python ...` (the adapter
documented for the D7-B R2 execution); review pytest runs may instead use the
repo-local `.venv/bin/python`.

**Prevention**: any future authorized D7-C run must declare the same
venv-on-PATH adapter in its command record, so a bare `python` fails safely
(exit 127) rather than silently binding a different interpreter.

---

### V35 report rewrite claimed `NB_CANDIDATE_DEVELOPMENT_READY` (rejected)

**Observed** (2026-09-11, WSL): the uncommitted working copy of
`docs/v35-algorithm-development-report.md` had been rewritten to claim a
terminal `NB_CANDIDATE_DEVELOPMENT_READY` status and a positive numerical
table.

**Root cause**: the rewrite contradicted the committed corrected report at the
cycle entry HEAD, whose bounded status is
`NO_NB_CANDIDATE_FOR_TESTED_HAND_DESIGNED_CONFIGURATION` and
`PROTOCOL_PARTIAL_A4_NOT_EXECUTED`. The rewrite was uncommitted and its numbers
were not reproducible from the accepted `run_02` evidence.

**Fix**: reject the rewrite and restore the report content exactly to the
entry-HEAD version:
`git show HEAD:docs/v35-algorithm-development-report.md > docs/v35-algorithm-development-report.md`.
No backup file was created and no false numerical table is retained as an
active report.

**Prevention**: treat the committed corrected bounded status as authoritative;
do not promote an uncommitted rewrite whose numbers cannot be recomputed from
accepted evidence.

---
### Delegated execution completed but result delivery failed (lost delivery with completed side effects)

**Observed** (2026-09-14, NBPOLAR-PHASE4-P9): the first Wave-C delegation
executed the frozen command and flushed the 5-file evidence root at 15:29:50,
but its result delivery failed on an infrastructure certificate error. A retry
operator found the root already present.

**Root cause**: the failure was in result transport, not in execution — the
side effects (five flushed files) were complete while the return path was
broken. Re-executing would consume a second attempt and violate the
no-rerun freeze.

**Fix**: the retry operator correctly STOPPED without running anything
(`BLOCKED(prior-output-exists)`, nothing consumed by the retry). A read-only
inspection then verified the root as the genuine product of exactly one frozen
execution: single contiguous flush window (~0.3 s), expected protocol/prefix
identifiers only, expected record shapes (here 56x192+640x2), and the frozen
command verbatim in `frozen_plan.json`. STATUS counters were aligned to
reads/attempts 1/1. No rerun ever occurred.

**Prevention**: on a lost-delivery-with-present-output incident, never rerun to
"get a clean return" — STOP, read-only verify single-flush provenance against
the frozen plan, align counters to the single attempt, and record the incident
in `OPERATOR_RETURN.md` plus the decision log for main-thread adjudication.

## Text isolation tests must match architectural layers

Symptom: a later package-level API export fails an earlier textual
"forbidden import" test even though the forbidden dependency is absent from the
earlier algorithm modules.

Cause: one regex was applied both to algorithm files and package `__init__.py`,
combining two different contracts. A new legitimate export then became
impossible without violating one frozen requirement.

Fix: split the sentinel by responsibility. Keep dependency bans on the modules
whose algorithms must remain isolated; keep package-wide legacy/protocol bans
separate; allow explicitly accepted exports at the package surface. Never evade
the sentinel through alternate import spelling or lazy imports. Before freezing
a new cross-phase ban, test it against the planned next public API surface.
## NumPy advanced indexing can move the selected axis

For `[U1,B,U2]`, `f3[u1,:,nz]` selects U2 and advanced indexing can move that
axis ahead of B. To select supported Bob states, use `f3[u1,nz_b,:]`. Test with
unequal dimensions or a sparse non-all-true Bob mask and compare every element
to a loop oracle; square 32-valued axes can hide the error until a 1024-state
table is used.

## `ru_maxrss` units differ by platform (bytes vs KiB)

**Observed** (2026-09-13, WSL/Linux): a peak-RSS reading reported as "GiB" was
implausibly small (three orders of magnitude below the measured memory use), so
the `<2 GiB` resource envelope evidence was meaningless.

**Root cause**: `resource.getrusage(...).ru_maxrss` is in **KiB on Linux** but
in **bytes on macOS**. Dividing by `1024**3` assumes bytes and under-reports
GiB by 1024× on Linux.

**Fix**: convert platform-aware — `raw / 1024**2` on Linux, `raw / 1024**3` on
macOS (fixed in `comparison_bench/src/comparison_bench/formal_ir/nbpolar/
empirical_diagnostic.py` `_peak_rss_gib`).

**Prevention**: on Linux, sanity-check that a reported "GiB" RSS is not
implausibly small; convert `ru_maxrss` with a platform-aware helper rather than
a hard-coded divisor.

## `ru_maxrss` is corrupted under `ulimit -v` on this WSL2 kernel

**Observed** (2026-09-13, WSL2): the P5/P6 scripts persist a peak RSS from
`resource.getrusage().ru_maxrss` (used for `rss_bytes_peak`) while running under
the frozen `ulimit -v 2097152` wrapper. Under that wrapper the reading is not a
reliable measurement: P6 Pre-EXECUTE F-1 reproduced a constant 1193268 KiB
(≈1.14 GiB) from process start while the true `VmHWM` was ~105 MB, and the
P5/P6 runs persisted ~106 MiB values (P5 `111190016` B, P6 `111816704` B) that
are likewise environment-dependent.

**Root cause**: this WSL2 kernel's `ru_maxrss` accounting is unreliable under an
address-space (`-v`) limit, so it is not a real memory measurement there.

**Fix**: treat a persisted RSS from such a run as advisory, never as a memory
envelope claim. When an exact value matters, read `/proc/self/status` `VmHWM`
instead.

**Prevention**: do not gate on or claim `rss_bytes_peak`; record the plan's
`rss_bytes_max` and the true `VmHWM` separately.

## `RuntimeWarning: 'pkg.module' found in sys.modules after import of package 'pkg'`

**Observed** (2026-09-13, WSL): running a package module directly emits this
warning on stderr, e.g.

```bash
.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.protocol --mode dev-gate ...
# RuntimeWarning: 'comparison_bench.src.comparison_bench.formal_ir.nbpolar.protocol' found in sys.modules
#   after import of package 'comparison_bench.src.comparison_bench.formal_ir.nbpolar', but prior to execution
```

**Root cause**: `pkg/__init__.py` re-exports the submodule (here `protocol`), so
importing the package already puts the module in `sys.modules`; `python -m`
then finds it loaded before it runs it as `__main__`.

**Fix**: benign — no action needed for correctness; the run proceeds normally.
Suppress it in harnesses (e.g. `-W ignore::RuntimeWarning`) only if stderr
cleanliness is required.

**Prevention**: in `__init__.py`, import the submodule lazily (e.g. inside a
module-level `__getattr__`) instead of re-exporting eagerly at import time, or
route the standalone entrypoint through a dedicated script rather than `-m`.

## Frozen docs hand-enumerate a value derived by a code constant

**Observed** (2026-09-13, NBPOLAR-PHASE4-P5): the freeze and implementation
notes listed the public tag masters as `2026092470..2026092472` (`seed + 1000`),
while the frozen definition, packet, authorization and module constant
(`PUBLIC_TAG_MASTER_OFFSET = 10000`) are `seed + 10000` =
`2026101470..2026101472`. Independent Pre-EXECUTE R0 flagged it as a docs-only
blocker (B-1); it was repaired and closed by R1 PASS.

**Root cause**: a value that the executable path derives arithmetically from a
single module constant was copied into prose by hand with the wrong offset, so
the documentation contradicted the code and the emitted artifact metadata.

**Fix**: corrected the two docs-only enumerations to the constant-derived values;
no code, constant, command, seed, set or root change was needed.

**Prevention**: when a documented value is derived from a constant (offsets,
scales, bit counts), recompute it from that constant instead of transcribing it;
have the independent review recompute all derived values from the constant and
diff them against the prose.

### Multi-stream experiment gates keyed on a per-stream `block_id`

**Observed** (2026-09-13, NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1): the frozen
640-pair run persisted 11/12 integrity gates true but
`d1_exactly_nested_and_d2_disclosed_once = false`, even though D2 was disclosed
exactly once per arm/block in every block. An isolated 2-stream probe reproduced
the same single failure.

**Root cause**: the gate counted per-block events by `(block_id, arm)` while
`block_id` is the per-stream block index (the runner reuses indices 0..127 for
each stream and the event id omits `stream_seed`). Across five streams the 1,280
L2 events collapsed onto 256 keys `{(0..127) x {static, adaptive}}`, each counted
5, so `all(count == 1 ...)` was falsely unsatisfiable; the `set(l2_counts) ==
expected_l2` term still passed because a set hides multiplicity. The contract
("D2 disclosed once per arm/block") is per `(stream, block, arm)`, whose count is
exactly 1.

**Fix**: do not repair or rerun a consumed gate; preserve the failure root and
record the persisted `BLOCKED` label. The correct count key must include the
stream identity — composite `(stream, block, arm)` or an event identity that
already encodes the full paired block.

**Prevention**: in any multi-stream (shared-index) experiment, key per-block
event counters on the full identity `(stream, block, arm)`, never on a
per-stream `block_id`; add at least one multi-stream test to the focused suite,
since single-stream tests cannot expose a cross-stream key collision.

### Entropy literals from a raw-MLE table gated against a floored/smoothed table

**Observed** (2026-09-14, NBPOLAR-PHASE4-P7): the frozen `1e-12`
literal preconditions on `H1/H2/total` (`0.02428054681872374` /
`0.7767572780789994` / `0.8010378248977232`, the V49 1M/TRAIN `nll_*` columns)
are unsatisfiable if read as the entropies of the floored sampling table: the
`1e-15` cell floor shifts the total by `~5.16e-11` (H1 `~4.59e-11`, H2
`~5.70e-12`) on this near-zero-entropy sparse population. The strict reading
therefore fails precondition 3 while the packet's separate "floor-induced
change `<= 1e-9`" guard would simultaneously pass, which is self-contradictory.

**Root cause**: two different functionals were conflated. V49's `nll_*` literals
are the **raw-MLE in-sample population conditional entropies** (`H1 = sum_b p_b
H(P1_raw)`, `H2 = sum_b p_b sum_u1 P1_raw(u1|b) H(P2_raw)` with `P1_raw/P2_raw =
derive_p1/derive_p2(counts / column totals)`), not the A-level floored/renormalized
protocol-table entropies. Both are legitimately needed, but for different checks.

**Fix**: ratify and record which functional each check uses — literals compare
the raw-MLE population values at `1e-12`; the floored-table values are reported
only and fed to the separate `|floor_total - total| <= 1e-9` guard. Never gate
the floored entropies against the raw-MLE literals. Independent Pre-EXECUTE
review must confirm the functional before execution (P7 review item #1: PASS,
ratified).

**Prevention**: whenever a floor/smoothing/renormalization is applied before an
entropy check, state the functional explicitly in the freeze; recompute both the
raw and the transformed entropies in the independent review and confirm the
literal tolerance and the floor guard are jointly satisfiable on the actual
table before authorizing the run.

### Gate runner catches ValueError/OSError but not MemoryError, with end-only writes

**Observed** (2026-09-14, NBPOLAR-PHASE4-P12): the single gate run aborted
after ~18.5 min with an uncaught
`numpy._core._exceptions._ArrayMemoryError: Unable to allocate 64.0 MiB for
an array with shape (262144, 32)` at the L2 candidate-metric construction
(outside both SC try-guards) and exited 1 with empty stdout and zero output
files, instead of the fail-closed `resource_abort`-record + persisted
`BLOCKED(resource_limits_met_and_no_abort)` path.

**Root cause**: `main` caught only `(ValueError, FileExistsError, OSError)`,
but `_ArrayMemoryError` subclasses `MemoryError`, so the in-block allocator
failure bypassed both the between-block resource guard and the exception
mapping. Writes sat after the execution loop, so all in-memory progress from
~124 completed blocks was lost with the abort (the X11/X12 per-cell
checkpointing lesson not applied here).

**Fix**: none for the consumed packet (terminal; no rerun). For future gate
runners: catch `MemoryError` alongside the existing refusal types and route
it to the frozen resource gate; wrap in-block metric allocations (not just
SC calls) in the resource guard or pre-size them against the envelope; and
checkpoint per cell/block instead of writing only at the end.

**Prevention**: before freezing a gate runner, verify the caught-exception
tuple covers `MemoryError` (check the MRO of the array allocator error) and
that every full-size allocation site is either inside a guarded block or
bounded by the memory envelope; require per-cell checkpointing whenever a
run spans more than one cell.

### Reviewer subagent manually terminated mid-run: resume from its saved transcript

**Observed** (2026-09-16, NBPOLAR-PHASE4-P18): the first independent
`reviewer-go` Pre-RESULT attempt was manually terminated after completing
items 1–8 and the focused test run, leaving no review file, while its
full-suite run was interrupted mid-execution.

**Root cause**: the reviewer process was stopped, not the review — the
runner infrastructure was still healthy and the completed work was already
persisted in the thread's structured transcript.

**Fix**: complete the review as a resumption from the saved transcript.
Treat the transcript's recorded numbers as recovery input only: independently
re-verify every load-bearing value in the resuming session, re-run any
interrupted suite fresh (not from partial state), and write the review file in
the resuming session. Record the resumption explicitly in the review and in
the operator return. Do not rerun the frozen gate as part of the recovery.

**Prevention**: for a long review run, keep each stage's evidence in the
transcript so an interruption is recoverable; never accept recovered numbers
without independent recomputation, and never let a terminated reviewer trigger
a gate rerun or a second attempt.

### Concurrent external commit captures a mid-run artifact snapshot (add-before-commit race)

**Observed** (2026-09-16, NBPOLAR-PHASE4-P19): a concurrent external commit
(`faac0411…`, not made by the packet's operators) landed ~33 s after the run's
final write and committed the five evidence files at an 11/15 checkpoint
(`outcome_label: RUNNING(record 11/15)`, `integrity_all_pass false`). In the
worktree the four non-plan files show ` M` against that commit; the finalized
15/15 files are the worktree content.

**Root cause**: an unsynchronized `git add` captured the worktree while the run
was still writing, and the `git commit` landed after finalization. `git add`/
`git commit` never modify worktree files, so the worktree retained the complete
record; the anomaly is a versioning/provenance artifact, not a data-corruption
or scientific failure.

**Fix**: treat the **worktree** files as authoritative evidence and read them
from the filesystem. Do **not** use `git show HEAD:<path>` for the affected
paths, and do not `git restore`/`checkout --`/`stash`/`reset --hard` them —
that would overwrite the finalized artifacts with the superseded mid-run
snapshot and destroy the evidence. Reconstruct the sequence from same-domain
`created_utc` values and mtimes (final write < commit timestamp), confirm the
commit is additive and touched no protected input, and record the race as a
provenance incident in the operator return and decision log. If a commit is
later authorized, `git add` the finalized files after acceptance and cite the
worktree hashes; do not describe the committed blobs as the result.

**Prevention**: when a run writes an evidence root into a shared checkout,
expect concurrent external versioning; before accepting, compare the worktree
content against the committed blobs and prefer the worktree when they differ,
never silently reconciling with git. A Pre-RESULT review that finds such a race
should report it as a provenance anomaly (PASS_WITH_COMMENTS) rather than a
scientific failure, and must not trigger a rerun.

### Internal SC MemoryError swallowed by a decode-failure catch

**Observed by static audit** (2026-09-17): shared operational helpers wrap L1
and L2 SC calls in broad `except Exception` blocks. An internal `MemoryError`
therefore becomes `decode_failed`/an error-type string instead of reaching the
outer resource-stop handler. Existing runner tests that replace the entire
block helper with an OOM do not exercise this inner seam.

**Impact**: future large-N or list runs can misattribute a resource failure as
an algorithmic decoding failure. This path does not explain P18/P19, whose
persisted outcomes are `verify_failed` with no resource signal.

**Fix contract**: before another real-data run, explicitly re-raise
`MemoryError` at every audited inner SC seam and preserve the accepted
decode/nonfinite exception taxonomy. Add injected tests at both the L1 and L2
SC sites and verify call/disclosure accounting at the stop. Do not rerun or
rewrite historical gates.

**Prevention**: tests for a runner-level OOM and an inner decoder OOM are
different. Every helper that promises resource/decode separation needs both.

### Stray `D:/` directory regrowing in the repo root under WSL

**Observed** (2026-09-19): a `D:/` directory inside the repo root accumulated
2.3 GB / 3597 files.

**Root cause**: `comparison_bench/tests/test_evidence_package.py:27` hardcodes
`TEST_DIR = Path("D:/Code/...")`. Under WSL that Windows absolute path resolves
as a RELATIVE path, so the test's `mkdir -p` recreates the whole tree inside
the repo on every test run.

**Fix**: the tree was moved (not deleted) to `/mnt/d/Code/.stray_dcolon_20260919/`
(2.3G preserved; unique pytest tmp content not present elsewhere). The planned
source fix is a small future packet (or next docs batch): replace the hardcoded
Windows path with a repo-relative/tmp path. Until then the artifact reappears
on test runs — move it out again, and never `git add` the tree.

**Prevention**: never hardcode a Windows drive-letter path as a test output dir;
use a repo-relative path or tmp dir so WSL cannot reinterpret it as relative.

### `git diff --numstat` empty but file flagged `M` on a DrvFs/NTFS checkout (stat-dirty)

**Observed** (2026-09-19, P20Q acceptance): `git status --short` flags
`M comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`
while `git diff --numstat` is empty (blob hash == index).

**Root cause**: DrvFs/NTFS stat-info invalidation — mtime/size metadata changes
without a content change, so git reports the file modified on stat while the
content diff is empty.

**Fix**: confirm with `git diff --numstat` (empty) plus a blob-vs-index hash
comparison; never stage/commit on the lone `M` flag.

**Prevention**: treat a lone `M` on known fixture paths as stat-dirty until a
non-empty diff proves otherwise.
