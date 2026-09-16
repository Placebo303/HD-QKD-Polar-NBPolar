# Pre-RESULT review — NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE (Tier-Y FAILURE accounting)

Reviewer: independent reviewer-go (did not write the code, did not operate the gate run).
Read-only review except for writing THIS file. Nothing was rerun (attempt 1/1 spent;
rerun forbidden). The V25 `channel_counts.npz` content was NOT reopened (metadata
`stat` only; read 1/1 spent). No old-root writes; no commit/push.

## Verdict: CONFIRMED_SINGLE_RESOURCE_ABORT

The single authorized Tier-Y run FAILED with a resource abort. Failure accounting is
confirmed: exactly one execution, no retry, no output root, no label, consumption
spent, null artifacts verified. Closeout label for the (unpersisted) run:

```
BLOCKED(resource_limits_met_and_no_abort)
```

Frozen gate name per P12_FREEZE.md §5 gate list (quoted verbatim): the ordered hard
gates are "`target_population_contract`, `six_n_rows_and_128_blocks`,
`budget_allocation_orders_reproduced` ..., `coverage_complete`,
`buckets_disjoint_exhaustive` ..., `truth_leak_zero`, `disclosure_and_recount_exact`,
`attempt_read_accounting_exact`, `resource_limits_met_and_no_abort`", with
"otherwise the earliest `BLOCKED(<gate>)`". The abort below is the
"no resource abort" / `resource_limits_met_and_no_abort` gate — the earliest (and
only) failed frozen gate. No other gate was reached for evaluation (no artifacts
exist to recompute); per freeze §5/§7 any breach "fails
`resource_limits_met_and_no_abort` by construction".

---

## 1. Single-execution proof (exactly once, never retried)

Checkable evidence (commands + raw output):

```
$ ls -la .workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/
AUTHORIZATION_PROMPT.md  P12_FREEZE.md  P12_IMPLEMENTATION_NOTES.md
PRE_EXECUTE_REVIEW.md  PROMPT.md  STATUS.yaml  TASK_PACKET.md
$ (test ! -e .../target_f13_n_scaling && echo ROOT_ABSENT || echo ROOT_PRESENT)
ROOT_ABSENT
$ ls -la .../target_f13_n_scaling
ls: cannot access '.../target_f13_n_scaling': No such file or directory
$ find .workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE -maxdepth 2
... (7 contract files only; no target_f13_n_scaling, no second root)
$ ls -d .../NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/*/
ls: cannot access '.../*/': No such file or directory
$ ls -la /tmp/p12_gate_stdout.txt /tmp/p12_gate_stderr.txt
-rw-r--r-- 1 karel_303 karel_303    0 Sep 14 20:54 /tmp/p12_gate_stdout.txt
-rw-r--r-- 1 karel_303 karel_303 1731 Sep 14 21:12 /tmp/p12_gate_stderr.txt
$ stat /tmp/p12_gate_stdout.txt /tmp/p12_gate_stderr.txt
stdout: Size 0, Birth 2026-09-14 20:54:03.680783798 +0800, Modify 20:54:03 (never written)
stderr: Size 1731, Birth 2026-09-14 20:54:03.680783798 +0800, Modify 2026-09-14 21:12:30.239323551 +0800
$ ls /tmp/*p12* /tmp/*target* /tmp/*scaling*
/tmp/p12_gate_stderr.txt + /tmp/p12_gate_stdout.txt only;
no /tmp/*target*, no /tmp/*scaling* (no stray writes)
$ wc -c /tmp/p12_gate_stdout.txt
0 /tmp/p12_gate_stdout.txt
```

Wall consistency: stderr-birth→last-write delta = 20:54:03 → 21:12:30 = 1107 s
(18.45 min), consistent with the operator-reported wall ~18m52s (tee-close vs
process-wall difference, well within the 1800 s budget). Both tee files share one
birth timestamp (single tee launch); stdout stayed 0 bytes; stderr holds exactly
one traceback (see §2). There is exactly one tee pair — no second launch, no
duplicate evidence.

What is checkable vs testimony:

- CHECKABLE: absent output root (a completed retry would have created it; a
  retry after a created root would refuse with FileExistsError — absent proves no
  completed attempt exists); single tee pair with shared birth and one traceback;
  no duplicate roots/files anywhere (packet dir, /tmp); HEAD unchanged; no commit
  (see §4/§6).
- TESTIMONY (consistent with, but not independently re-provable post-hoc without
  shell history): operator's "pre-run ROOT_ABSENT printed", "exact frozen command
  run ONCE (exit 1, stdout empty)", "no second attempt". Nothing in the checkable
  evidence contradicts any element of the testimony; every independently
  re-checkable element (ROOT_ABSENT now, stdout empty, exit-1-shaped stderr with
  no label, wall within budget, NPZ stat — §4) matches it.
- NO second attempt exists: no other output roots under the packet dir, no stray
  `target_f13*`/`per_block*`/`aggregate*` files in the packet dir or /tmp, no
  second tee pair, no results//outputs_comparison writes (§4).

## 2. Failure classification: RESOURCE abort (memory), not semantic/refusal

Raw stderr (`/tmp/p12_gate_stderr.txt`, 1731 bytes, read as the operator's own
capture file — allowed; the NPZ itself was not opened):

```
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File ".../comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_n_scaling.py", line 1955, in <module>
    raise SystemExit(main())
  File ".../target_n_scaling.py", line 1921, in main
    run = run_target_n_scaling(
  File ".../target_n_scaling.py", line 1330, in run_target_n_scaling
    arm = run_scale_arm(
  File ".../target_n_scaling.py", line 774, in run_scale_arm
    p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
  File ".../formal_ir/nbpolar/prior.py", line 319, in probs_to_symbol_metric
    return SymbolMetric(
  File "<string>", line 8, in __init__
  File ".../formal_ir/nbpolar/prior.py", line 255, in __post_init__
    mat = arr.astype(np.float64, copy=True)
numpy._core._exceptions._ArrayMemoryError: Unable to allocate 64.0 MiB for an array with shape (262144, 32) and data type float64
```

Code verified at the implicated lines:

- `target_n_scaling.py:773-774` — candidate-conditioned L2 metric construction
  `p2_probs = gather_p2_metrics(bob_arr[None,:], high_hat[None,:], p2_table)[0]`
  then `probs_to_symbol_metric(p2_probs, provenance=CANDIDATE_CONDITIONED)`.
  This line is OUTSIDE the two guarded SC `try` blocks (lines 760-768 guard only
  `sc1`; lines 777-791 guard only `sc2`), so a MemoryError here propagates.
- `prior.py:319` constructs `SymbolMetric(logp=...)`; `prior.py:255`
  `mat = arr.astype(np.float64, copy=True)` is the failing allocation.
- Call chain `:1330 run_scale_arm` ← `:1921 main` ← `:1955` matches the file
  (execution-loop call site; `main` argument plumbing; module entry).
  `main` catches only `(ValueError, FileExistsError, OSError)` → return 2
  (lines 1932-1934). Hierarchy check:
  `_ArrayMemoryError.__mro__ = (_ArrayMemoryError, MemoryError, Exception, ...)`,
  i.e. NOT a ValueError/OSError → uncaught → process exit 1 with empty stdout.
  That matches the operator report (exit 1, stdout empty).

Allocation arithmetic verified: `python3 -c "print(262144*32*8/1024/1024)"` →
`64.0 MiB`. The failing shape `(262144, 32)` float64 is exactly one full-N
N=262144 metric plane, occurring in the N=262144 arm (the last frozen row;
124 smaller-N blocks = 64+32+16+8+4 precede the 4 N=262144 blocks).

Why this is a RESOURCE abort and nothing else:

- NOT a semantic mismatch: H-literal/allocation/order/f-budget checks all passed
  (the run demonstrably passed preconditions, allocation, and ~124 blocks to
  reach line 774 — see §3); the error is an allocator refusal, not a value,
  shape-contract, or gate-comparison failure.
- NOT a precondition failure: that path raises
  `TargetPopulationContractError(BLOCKED(target_population_contract))`, a
  ValueError subclass → exit 2 with a refusal message. Observed: exit-1-shaped
  uncaught MemoryError, no refusal message.
- NOT a refusal-path issue (parse/absent-root/contract/stat-size): all of those
  raise before the NPZ content open, exit 2, with zero SC calls and near-zero
  wall. Observed: ~18.5 min wall and deep-execution traceback.
- The frozen envelope (`ulimit -v 2097152`, 2 GiB; `timeout 1800`) plus
  P12_FREEZE §7 ("Any breach ... fails `resource_limits_met_and_no_abort` by
  construction") classifies exactly this event. Note the fail-closed
  `_budget_exceeded` guard (lines 1298-1321) polls wall/RSS between blocks and
  converts *detected* pressure into `resource_abort` records + exit 0 with a
  persisted `BLOCKED(resource_limits_met_and_no_abort)`; the uncaught
  in-block allocator failure here bypassed that between-block guard (no
  try around metric construction), escaping as exit 1 with no files. The
  gate it fails is nonetheless the same frozen gate. Exact closeout:

```
BLOCKED(resource_limits_met_and_no_abort)
```

## 3. Consumption: attempt 1/1 + read 1/1 spent, no reopen/rerun

- The run demonstrably passed the content open and all preconditions: the
  traceback reaches `run_scale_arm` line 774, which is downstream of (a) the
  NPZ `stat` + `load_v25_channel_counts` open (lines ~1153-1166), (b) the
  frozen-scalar preconditions, (c) allocation freeze + sha, and (d) the
  execution loop. A pre-open refusal could not produce this stack; ~18.5 min
  wall further proves deep execution (past the ~124 smaller-N blocks into the
  N=262144 arm). Per P12_FREEZE §6 / TASK_PACKET P12-01, read 1/1 and attempt
  1/1 "are consumed together at the first NPZ content open" — both are spent.
- No reopen/rerun: output root still absent (§1/§4); no second tee pair; no
  second evidence set; this review performed no execution (import + pytest
  `--collect-only` only, §6) and no NPZ content open (stat only, §4).
- STATUS.yaml on disk still records `artifact_reads_used: 0, attempts_used: 0,
  result: null, independent_pre_execute: pending` (Wave-C operator had not
  updated it at review time). That file state is STALE relative to fact: the
  evidence above proves reads/attempts are 1/1 spent. Closeout must record
  `artifact_reads_used: 1, attempts_used: 1` with the BLOCKED label (in STATUS /
  closeout docs, not by rerunning anything).

## 4. Null-artifact verification

```
$ test ! -e .../target_f13_n_scaling && echo ROOT_ABSENT  →  ROOT_ABSENT
$ find <packet> -maxdepth 2  →  7 contract files only (no five files, no partials)
$ ls /tmp/*target* /tmp/*scaling*  →  No such file or directory
$ git status --porcelain -- results/ comparison_bench/outputs_comparison/
(empty — no writes)
$ ls -lt comparison_bench/outputs_comparison/ | head  →  newest Sep 12 (pre-run; nothing from Sep 14 run)
$ stat -c '%s %y %n' .../run_04/channel_counts.npz
25166822 2026-08-19 01:34:09.691122000 +0800 .../channel_counts.npz
$ git log --oneline -5 | head -1  →  ab173f2a (unchanged; matches P12_FREEZE §8)
$ git rev-parse HEAD  →  ab173f2a5e17336383a897b941080b731ba3dd9e
```

- `target_f13_n_scaling/` STILL absent: no five files, no partial files from the
  run anywhere (packet dir holds only the 7 pre-run contract files; /tmp holds
  only the two operator tee files, which are the runner's only writes).
- The runner writes nothing until the end by construction: `out_path.mkdir`
  + all five `_write_json`/`report.md` writes sit at lines 1631-1646, AFTER the
  execution loop — an in-loop abort necessarily leaves zero output files. The
  `BLOCKED(...)` label therefore exists NOWHERE on disk (no
  `aggregate_summary.json`); the stderr traceback + this review are the record.
- NPZ metadata only: `stat` size exactly `25166822` bytes, mtime `2026-08-19`
  unchanged (matches freeze §8 and Pre-EXECUTE §10). Content never opened by
  this review.
- No writes to `results/`, `comparison_bench/outputs_comparison/`, or any old
  root (porcelain for those paths is empty; newest outputs_comparison entry
  predates the run).
- HEAD unchanged (`ab173f2a...`, identical to the freeze-recorded ID); no commit
  was made (log top is still the pre-P12 commit).

## 5. Mechanism note (descriptive only — NOT a repair plan)

Factual characterization of why a 64 MiB mapping failed ~18.5 min in under
`ulimit -v 2097152` (2 GiB address space):

- Per-block full-(N,32)-float64 materializations on the N=262144 path
  (`run_scale_arm`, lines 743-804 + `prior.py` conversions): (a) L1
  `build_p1_metrics` gather → (1,N,32) float64 then `[0]` → (N,32);
  `probs_to_symbol_metric` temporaries at `prior.py:305` (`astype` copy),
  `:315` (`np.log` with `full_like`), `:319`→`:255` (`SymbolMetric`
  `astype` copy); (b) candidate-L2 `gather_p2_metrics` → (1,N,32) then `[0]`
  → (N,32), with the same `probs_to_symbol_metric` chain — the observed
  failure is the (b)-chain `SymbolMetric` copy at `prior.py:255` for the
  (262144,32) plane. Each (N,32) float64 plane at N=262144 is exactly
  64.0 MiB, and several such planes plus `full_like`/log temporaries coexist
  per block alongside SC `decision_metrics` (chunk_rows=512 bounds only the
  `_minus_block` interior, not this metric path), int64 N-vectors
  (bob/high/low/u1/u2/labels/high_hat/low_hat/label_hat, ~2 MiB each),
  label-bits (N×10 uint8), `_truth_isolation_sentinel` snapshots (duplicates
  of the protected set), and the still-referenced L1 metric while L2 builds.
  Under the 2 GiB virtual-memory cap, after ~124 smaller-N blocks and ~18.5
  min of allocator churn, the first N=262144 block's additional 64 MiB copy
  request was refused. Nothing in the traceback indicates a wrong shape,
  wrong dtype, NaN/inf, contract violation, or refusal-path defect — the
  shapes/dtypes are exactly the frozen ones; the allocator said no.
- The X11/X12 lesson was NOT applied here: this runner persists nothing until
  the post-loop write block (lines 1631-1646) — no per-cell/per-block
  checkpointing — so all in-memory progress from the ~124 completed blocks was
  lost with the abort. (Stated as fact about this code path, not a proposal;
  no change is authorized by this review.)

## 6. Scope: tests and worktree untouched BY THE RUN

- Tests untouched by the run: the gate run executes only the frozen command
  (decoder path); it imports no test modules and writes no test artifacts. This
  review did NOT re-run the 285 suite as acceptance (per instructions, the gate
  run itself is the evidence). Light sanity only, no execution of frozen
  streams, no NPZ open:
  `import target_n_scaling → FROZEN_N_VALUES (256,4096,16384,65536,131072,262144),
  FROZEN_BLOCKS (64,32,16,8,4,4), FROZEN_TOTAL_BLOCKS 128`;
  `pytest --collect-only .../test_nbpolar_target_n_scaling.py → 23 tests collected`.
- `git status --porcelain` (85 entries): the worktree carries the dirty set
  disclosed at Pre-EXECUTE §10 (pre-existing P3-P11 wave appends, AGENTS.md /
  memory / docs edits) PLUS the declared P12 set (new `target_n_scaling.py`,
  new `test_nbpolar_target_n_scaling.py`, new `specs/nbpolar-phase4-p12/`, P12
  tail in `tasks.md`, new freeze queue dir, STATUS.yaml). The RUN itself added
  no entries: no accepted-module edits (no `target_construction.py` /
  loader / adapter / baseline / old-root diffs attributable to the run), no new
  output dirs, no test-file modifications. `results/` and
  `comparison_bench/outputs_comparison/` porcelain is empty (§4).

---

## Blocking Issues

- None beyond the confirmed failure itself: the run is a clean single
  resource abort mapping to `BLOCKED(resource_limits_met_and_no_abort)`.
  No integrity violation, no second attempt, no artifact to distrust.

## Non-Blocking Suggestions (closeout hygiene only — no rerun, no code change)

- Record consumption truthfully at closeout: `artifact_reads_used: 1`,
  `attempts_used: 1`, `result: BLOCKED(resource_limits_met_and_no_abort)`,
  with a pointer to the stderr traceback + this review (STATUS.yaml is stale
  at 0/0/null).
- Preserve `/tmp/p12_gate_stdout.txt` (0 B) and `/tmp/p12_gate_stderr.txt`
  (traceback) bytes/mtimes or copy them into the packet dir as the run's only
  evidence (they currently live outside the repo).
- Any successor packet should reckon with §5 (in-block metric allocation
  outside the between-block resource guard; end-only persistence) in its own
  proposal — not here, not as a patch to this frozen point.

## Checklist

- [x] Matches OpenSpec spec (failure path matches freeze §5/§7 semantics; no artifact to mismatch)
- [x] Tests pass (not re-run per instructions; 23-collect + import sanity; gate run is the evidence; no test files touched by the run)
- [x] No scope creep (run wrote nothing; review wrote only this file)
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? — No (batched at milestones per AGENTS.md §10.4; main thread's call)

## Closure statements

- Nothing was rerun; the NPZ was not reopened (stat metadata only: 25166822
  bytes, mtime 2026-08-19).
- No output root exists (`target_f13_n_scaling/` absent; no partial files).
- No `TARGET_F13_N_SCALING_PROFILE_CANDIDATE` or `BLOCKED(...)` label was
  persisted (no files were written by the run); the closeout label for the
  record is `BLOCKED(resource_limits_met_and_no_abort)`.
- Reads/attempts 1/1 spent at/after the first NPZ content open (proven by
  deep-execution traceback); no reopen, no second attempt, no commit/push.
