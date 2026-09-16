# Pre-EXECUTE review — NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE (Tier-Y)

Reviewer: independent reviewer-go (did not write the code). Read-only review;
no code, packet, OpenSpec, or STATUS file was modified. The single artifact
read belongs to the gate run: the V25 `channel_counts.npz` content was NEVER
opened in this review (metadata `stat` only). The real profile command was
never run. No Model-F/raw/held-out/real/EVAL/tag/protocol access; no old-root
writes; no commit/push.

## Verdict: PASS

The frozen command may be executed exactly once by the Wave-C operator under
the exit-code semantics in §7(b) below. All ten required checks pass. The five
operator-flagged items are adjudicated (all ratified, two cosmetic notes).
No blocking issue was found.

---

## 1. STATUS exactness — PASS

Exact command + raw evidence:

```
$ cat .workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/STATUS.yaml
task_id: NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE
state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE
tier: Y
predecessor: EXACT_CHUNKED_SC_ACCEPTED
artifact_reads_allowed: 1
artifact_reads_used: 0
attempts_allowed: 1
attempts_used: 0
implementation_authorized: true
artifact_read_authorized: true
decoder_execution_authorized: true
real_data_authorized: false
scientific_promotion: false
result: null
independent_pre_execute: pending
independent_pre_result: pending
next_gate: INDEPENDENT_PRE_EXECUTE
```

Checklist: implementation/artifact_read/decoder_execution `true`, real_data
`false`, scientific_promotion `false`; reads 0/1, attempts 0/1; `result: null`;
both reviews `pending`; `state`/`next_gate` as declared. All exact. PASS.

## 2. OpenSpec P12 delta consistency — PASS

- Delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p12/spec.md`
  (148 lines) covers budget/construction/allocation (§P12-02 formula, clip,
  lexicographic rule, pre-SC freeze, no-empirical-order), six-N/128-block
  matrix with master+10000 and P12/N/layer/block separation, buckets with
  undetected-never-success, truth boundary, accounting/recount, CP-95, five
  files, nine-flag CLI, integrity-only gates, no-threshold statement
  ("There SHALL be no recovery threshold… report-only"), forbidden paths,
  bounded claim, and both independent reviews. Consistent with TASK_PACKET
  P12-01..P12-07 in every frozen value I compared (N/seeds/blocks, H
  literals, 1e-12/1e-9 tolerances, 512 chunk, 1800 s/2 GiB, labels).
- All P12 boxes unchecked: `grep -c "\[x\]"` over `tasks.md` lines 478–530
  returns `0`; all nine P12-1..P12-9 lines show `- [ ]`. PASS.
- Docs authorize no production behavior: spec.md lines 15–16 ("This document
  authorizes no production behavior"), tasks.md P12-1 ("no production
  behavior is authorized by this doc"), P12_FREEZE.md ("It authorizes
  nothing"). PASS.

## 3. Reuse proof — PASS

- `git diff --name-only` (tracked files) contains NO entry for
  `target_construction.py`, `target_rate.py`, loader, adapters, baselines, or
  old roots (grep over the name list returns empty). The one tracked
  `sc.py` diff (`_minus_block` chunk_rows keyword-only, default 512) is the
  accepted P11 predecessor change (`EXACT_CHUNKED_SC_ACCEPTED`), not this
  wave — this wave's files are all untracked additions.
- The runner (`target_n_scaling.py` lines 89–116) only CALLS accepted
  semantics: `load_v25_channel_counts`, `analytic_erasure_probs`,
  `analytic_order`, `derive_p1`/`derive_p2` (via `target_construction`
  tables), `build_p1_metrics`/`gather_p2_metrics`/`probs_to_symbol_metric`
  with `PRIOR_ONLY`→`CANDIDATE_CONDITIONED` provenance, `sc_decode`
  (no chunk argument passed; frozen default enforced by contract check
  lines 378–394), `sample_target_block`, `classify_outcome`,
  `target_preconditions`, Toeplitz tag/accounting. No accepted file is
  edited by this wave. PASS.

## 4. Frozen budget/allocation — PASS (independently recomputed)

Command + raw evidence (pinned interpreter):

```
$ /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c "... floor((1.3*N*H-64)/5) ..."
N=256    K=40    leak=264    f=1.2873923901554465
N=4096   K=840   leak=4264   f=1.2995836059713126
N=16384  K=3399  leak=17059  f=1.29981219126786
N=65536  K=13636 leak=68244  f=1.2999645814655583
N=131072 K=27285 leak=136489 f=1.2999741058529144
N=262144 K=54583 leak=272979 f=1.2999788680465925
```

All six K_total/leakage/f reproduce the operator-reported values exactly
under the literal H; under the float64 sum `H1+H2=0.8010378248977231` the
K values are identical and f differs by ≤1 ulp (one-ulp literal note in
P12_FREEZE.md §2 confirmed: floors are ≥0.27 from any integer boundary).
Runner cross-check via `budget_k_total`/`allocate_layer_ks` reproduces all
six (K1/K2) = (1/39, 37/803, 166/3233, 678/12958, 1381/25904, 2776/51807)
with `leakage=5*K+64 ≤ 1.3*N*H` holding at every point (worst f=1.29998).

- Clipping `[0,2N]` + full-budget-use + leakage inequality: implemented in
  `budget_k_total` (target_n_scaling.py:421–429) and asserted per-N before
  any SC (lines 1241–1248, raising
  `BLOCKED(budget_allocation_orders_reproduced)`). Covered by
  `test_budget_formula_and_clip` and
  `test_budget_full_use_inequality_frozen_points`. PASS.
- Lexicographic rule (residual-sum, then K1, then K2): implemented lines
  456–464 (`key = (residual, k1, k2)`, strict `<` keeps smallest K1 on
  residual ties). Independent enumeration with my own BEC recurrence and
  own argmin (fresh code, tiny/fresh seeds — NOT frozen streams, NOT the
  NPZ) spot-checks N=256 → (1,39,res 6.1515800257144235 vs runner
  …424, Δ~1e-13) and N=4096 → (37,803, Δ~1e-13): MATCH. Tie-break unit
  test (`test_k_tie_break_to_smallest_k1`, all-zero reliabilities →
  smallest feasible K1) passes. PASS.
- Index tie-break in BEC order: delegated to accepted `analytic_order`
  (stable descending, coordinate-index tie-break); verified
  `analytic_order(0.0,8)==range(8)`, `analytic_order(0.5,4)==[0,1,2,3]`,
  and my own order implementation matches the accepted one at N=256/4096
  exactly. PASS.
- All K/order/residual freeze-before-first-SC: code order is allocation
  loop (lines 1238–1280, incl. frozen sha) → execution loop (line 1293+);
  preconditions (line 1218) precede both; post-execution sha recomparison
  (lines 1373–1381) forbids adaptive repair. PASS.
- P7 empirical orders never imported/extrapolated: grep over the runner
  for `empirical` finds only scope docstrings ("never reused or
  extrapolated"); construction flows exclusively through
  `analytic_erasure_probs`/`analytic_order`. PASS.

## 5. Refusal/consumption ordering — PASS (probed, ratified)

Probes (exact commands, raw evidence):

- CLI-parse refusal BEFORE open: `python -m …target_n_scaling --counts x`
  → `returncode 2`, argparse usage error on stderr. PASS.
- Absent-root refusal BEFORE open: existing dir → `FileExistsError
  (refusing to overwrite…)` with a forbidden-loader patch proving the
  loader is never called; `_NPZ_CONTENT_OPENED` stays `False`; nothing
  created. Chunk-512 refusal likewise (`frozen point requires
  chunk-rows=512`), no directory created, guard still `False`. PASS.
- Preconditions AFTER open but BEFORE any SC (zero-SC probe):
  `test_precondition_failure_zero_sc_and_no_root` patches `sc_decode` to
  raise on any call, feeds a zero-Bob-column table → raises
  `TargetPopulationContractError(BLOCKED(target_population_contract))`,
  no output root created. PASS.
- Consumption at first NPZ open with reopen guard: `run_target_n_scaling`
  lines 1153–1166 (stat check → `load_v25_channel_counts` → guard set);
  second NPZ-mode call raises `ValueError (reopen refused…)` (line
  1154–1155). Injected-counts path consumes 0/0 and never touches the
  guard (verified `False` after every injected probe/test/smoke). PASS.
- Precondition-failure path records BLOCKED with consumption spent:
  `TargetPopulationContractError` subclasses `ValueError` (verified MRO),
  so `main` catches it → exit 2 with the `BLOCKED(target_population_
  contract)` label in the stderr refusal message and no output files.
  This MATCHES the packet ("consumed together at the first NPZ content
  open" + "after content open do not repair"): the label cannot be
  persisted because no root may be created, so the refusal message plus
  the freeze doc is the record. RATIFIED — see §7(b) for the operator
  rule that follows from this.

## 6. Execution matrix — PASS

- Six N/seeds/blocks exact: module constants
  `FROZEN_N_VALUES=(256,4096,16384,65536,131072,262144)`,
  `FROZEN_STREAM_SEEDS=(2026091820,…,2026091825)`,
  `FROZEN_BLOCKS=(64,32,16,8,4,4)`; `sum=128=FROZEN_TOTAL_BLOCKS`
  (verified by import). Matches TASK_PACKET P12-03 and P12_FREEZE §1. PASS.
- Master seed+10000 with domain separation: `master=int(seed)+10000`
  (lines 1255, 1348); tag seed
  `nbpolar-p12-n-scaling-seed:<master>:<n>:verify:<block>` (line 578).
  Verified pairwise-distinct across master/N/block. See §7(d). PASS.
- Per-block flow sample→L1→candidate-L2→label→tag (lines 1322–1350);
  grep finds no executed comparator/oracle/retry/repeat path (only
  prohibition docstrings). PASS.
- chunk_rows=512 plumbed to all SC calls: `_decode_layer` calls the
  accepted `sc_decode` (which exposes no chunk argument — asserted by the
  contract check lines 388–389) whose `_minus_block` production default
  is exactly 512 (asserted lines 383–387); CLI value ≠512 refused before
  open. PASS.
- Truth boundary: internal truth copies + `_truth_isolation_sentinel`
  mutation proof (lines 808–817); operational L2 metric uses the hard
  candidate only (line 773); `test_l2_metric_uses_hard_candidate_not_truth`
  and `test_truth_inputs_never_aliased` pass. PASS.
- Buckets exclusive, undetected never success: `_arm_record_consistent`
  (lines 888–951) enforces one-of-five outcomes, `exact ⟺ tag_pass ∧
  label_match`, `undetected ⟺ tag_pass ∧ ¬label_match`, `exact` flag set
  only for `outcome=="exact"` (lines 936–937); gate requires
  `buckets_disjoint_exhaustive` with per-record proof. PASS.
- Disclosure formula + partial-failure + recount: `key_dependent_bits =
  5*K1 + (5*K2 iff L2 invoked) + (64 iff tag invoked)` (lines 834–839),
  `public_control_bits = seed_bits_for(n) iff tag invoked`; independent
  literal `recount_events` with zero-mismatch gate (lines 1040–1088,
  1383–1384). `test_transcript_recount_literal` passes. PASS.
- Clopper-Pearson two-sided 95%: verified against closed forms —
  (0,n)→hi=`1-(0.025)^{1/n}`, (n,n)→lo=`(0.025)^{1/n}` agree to ≤5e-16
  at n=1,4,16,64; interior points satisfy the `math.comb` binomial-tail
  identity to <1e-6 (`test_clopper_pearson_small_n_against_binomial_
  identity`). PASS.
- Five-file scalar-only schema: `OUTPUT_FILES` = frozen_plan,
  allocation_and_orders, per_block_outcomes, aggregate_summary, report.md;
  smoke run writes exactly these five; scalar-only asserted (no
  `high_hat`/`decision_metrics` strings). Labels exact:
  `TARGET_F13_N_SCALING_PROFILE_CANDIDATE` / `BLOCKED(<earliest gate>)`
  (lines 1463–1467, gate order line 222–233 matches freeze §5). PASS.
- NO recovery threshold anywhere in code: grep for
  threshold/THRESHOLD/Wilson/recovery-pass finds only `no recovery
  threshold`, `no_threshold: True`, `report-only` strings. Recovery and
  first-success live only in `recovery_report_only`, never in gates. PASS.

## 7. Operator-flagged items — adjudication

**(a) "13-flag" wording vs actual `--flag` count — COSMETIC, ratified.**
`build_parser` exposes exactly nine required `--flags`: `--counts`,
`--source`, `--floor`, `--target-f`, `--n-values`, `--stream-seeds`,
`--blocks`, `--chunk-rows`, `--out-dir` (plus `-h/--help`). The frozen
command is byte-equal between TASK_PACKET P12-06 and `FROZEN_COMMAND`
(verified programmatically: `byte-equal: True`). "13" miscounts
otherwise; the implementation requires exactly the nine frozen flags
with no production default. No repair needed; Wave-C operator uses the
frozen command verbatim.

**(b) Exit-0-on-BLOCKED — RATIFIED with precise operator semantics.**
Verified in code: `main` (lines 1918–1951) returns `0` iff the run
completed and persisted one of the two frozen labels with the five
files; it returns `2` on any pre-completion refusal (`ValueError` —
including `TargetPopulationContractError` —, `FileExistsError`,
`OSError`, plus argparse's own 2). Gate failures discovered DURING/AFTER
execution (including `budget_allocation_orders_reproduced` reproduction
mismatch, coverage, buckets, truth, recount, accounting, resources)
persist `BLOCKED(<earliest gate>)` in `aggregate_summary.json` and exit
0. Allocation-time budget violation and precondition failure happen
AFTER the NPZ open but BEFORE any output: they raise
`BLOCKED(…)` as an exception → exit 2, no files, consumption spent,
label in stderr only. This is consistent with the packet's STOP
semantics ("after content open do not repair… STOP and preserve
evidence"). Wave-C operator rule: (i) exit 0 → read
`aggregate_summary.json: outcome_label`; `CANDIDATE` is a completed
profile, `BLOCKED(<gate>)` is a completed-but-blocked run — neither is
a pass/fail on recovery; (ii) exit 2 → STOP, preserve stderr + freeze
doc, check whether the refusal names a post-open contract (consumption
spent, no rerun) or a pre-open refusal (consumption intact); (iii) any
other exit code → treat as unknown STOP, no rerun. Do NOT reinterpret
exit 0 + `BLOCKED(...)` as success, and do NOT rerun an exit-2
post-open refusal.

**(c) 1e-9 residual reproduction bound — RATIFIED.** Bound enforced at
gate line 1754 (`abs diff ≤ 1e-9`); K_total/K1/K2/orders reproduce by
EXACT equality — the tolerance covers only float summation noise on the
undisclosed-reliability sum. My independent re-summation differs from
the runner by ~1e-13 (summation order), two orders below the bound;
the freeze's worst observed drift (1.5e-10) is an order below it. Exact
float equality would be spurious across summation orders, so the bound
is the scientifically honest form of "exact reproduction" for the
scalar sum while identity of the allocation rides on the exact
integer/order equalities. No change.

**(d) Constant `verify` layer token — RATIFIED.** The seed prefix
`nbpolar-p12-n-scaling-seed:<master>:<n>:verify:<block>` carries all
four frozen dimensions; the layer dimension is degenerate by design
(exactly one verification tag per block), so a constant token keeps the
derivation injective across (phase, master, N, block) — verified
pairwise-distinct — while documenting the layer it separates. Any
future second tag layer MUST introduce a distinct token; for this
frozen point the constant satisfies "domain-separated by
P12/N/layer/block" vacuously and correctly.

**(e) 285 vs 272 test count — 285 CONFIRMED for the record.** Single
invocation: 285 passed (`-k nbpolar`, 22 unrelated broken files
ignored — see §8). Focused P12 file: 23 passed. Predecessor NB-Polar
suite (`-k "nbpolar and not target_n_scaling"`): 262 passed. 262+23=285.
"272" is stale; the true frozen totals are 23 + 285.

## 8. Tests — PASS (23 + 285, pinned interpreter, fresh basetemps)

```
$ /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q -p no:cacheprovider \
    --basetemp=/tmp/p12-preexec-focus comparison_bench/tests/test_nbpolar_target_n_scaling.py
23 passed … in 6.94s
$ … --basetemp=/tmp/p12-preexec-nb -k "nbpolar and not target_n_scaling"   [22 unrelated files ignored]
262 passed, 2346 deselected … in 124.79s
$ … --basetemp=/tmp/p12-preexec-full285 -k "nbpolar"                        [same ignores]
285 passed, 2323 deselected … in 125.48s
```

Interpreter pinned: Python 3.12.3, NumPy 2.5.3 (matches freeze §3).
Coverage matches the P12-05 list: budget floors, K feasibility/ties,
literal BEC recurrence/order + index tie-break, f/accounting,
axes/packing, causal two-layer wiring, buckets/truth isolation,
tag/recount, CP edges + binomial-identity interior points, absent-root
refusal, no-production-invocation rule. Tests never open the NPZ
(`channel_counts`/`load_v25` appear only behind `forbidden_loader`
patches or in docstrings), never execute frozen streams 2026091820..25
(their only test-file occurrence is the line-7 scope docstring; executed
seeds are ≥2026091900 and disjoint), never invoke production paths
(injected 1024×1024 tables, temp roots, fake SC/tag seams only). The 22
ignored files are pre-existing collection errors unrelated to NB-Polar
(`scipy`/`ldpc`/`comparison_bench.formal_ir` import failures) — noted,
not caused by this wave.

## 9. Bounded smoke — PASS

Injected tiny tables only (synthetic 1024×1024, fresh seed), temp root:

```
files: ['aggregate_summary.json', 'allocation_and_orders.json',
        'frozen_plan.json', 'per_block_outcomes.json', 'report.md']
n_blocks: 3, wall 0.145 s, rss 221 MB (limit 2 GiB → 9.7× margin at tiny N)
outcome_label: BLOCKED(six_n_rows_and_128_blocks)   [expected: non-frozen shape]
guard (injected path): False; input_mode: injected_counts
```

Gates recorded (integrity dict persisted); disclosure/recount exact;
`budget_allocation_orders_reproduced: false` is CORRECT here (gate
recomputes from frozen EXPECTED literals; injected seam differs) —
proof the reproduction gate is live, not tautological. Scaling note:
tiny-smoke wall does not prove the N=262144 step fits 1800 s; the
safety net is the fail-closed resource guard (`_budget_exceeded` →
remaining blocks become `resource_abort` → `resource_limits_met_and_
no_abort` fails by construction), plus `chunk_rows=512` bounding the
`_minus_block` allocation and only 4 blocks at each of the top two N.
Margin is declared, not proven — acceptable for a Tier-Y development
profile with a fail-closed gate.

## 10. Scope/premises — PASS with disclosed dirty-worktree note

- `git status --porcelain` does NOT equal the narrow Wave-A set: the
  worktree carries pre-existing unrelated modifications (P3–P11 wave
  appends, AGENTS.md/memory/docs edits) and HEAD is unchanged at
  `ab173f2a5e17336383a897b941080b731ba3dd9e` (matches freeze §8; no
  commit made by this wave — verified). The P12-scoped set verified
  individually: new `target_n_scaling.py`, new
  `test_nbpolar_target_n_scaling.py`, new `specs/nbpolar-phase4-p12/`,
  P12 tail section of `tasks.md` (lines 473–535, all boxes unchecked),
  new freeze queue directory, STATUS.yaml accounting-only state. No
  accepted-module or old-root writes by this wave (§3 proof above).
- Root still absent: `test ! -e …/target_f13_n_scaling` →
  `ROOT_ABSENT_OK` (re-verified at review time).
- Reads/attempts still 0: STATUS.yaml `artifact_reads_used: 0`,
  `attempts_used: 0`; every injected probe/test/smoke in this review
  left the module guard `False`.
- NPZ: `stat` reports exactly `25166822` bytes; content never opened.

## Findings (file:line)

No blocking findings. Non-blocking notes (no repair required pre-execution):

- `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md:473–535` —
  P12 section is a tail append; the tracked `tasks.md` diff vs HEAD
  also contains prior-wave (P4–P11) appends from the dirty worktree.
  Disclosed, not a P12 defect.
- `target_n_scaling.py:1744,1747` — gate reproduction uses
  `EXPECTED_H1+EXPECTED_H2` (float64 sum …231) while frozen f values
  were pinned with the literal …232; K/allocation identical, f differs
  ≤1 ulp, gate checks only `f ≤ 1.3`. No action.
- `target_n_scaling.py:260,578` — constant `verify` layer token; see
  §7(d). No action for this frozen point.
- Reviewer recommends (Wave-C hygiene, not gating): the operator paste
  the §7(b) exit-code rule into the execution log before launching the
  frozen command.

## Closure statements

- The V25 `channel_counts.npz` content was NOT opened during this
  review; only `stat` metadata (25166822 bytes) was read.
- The real profile command was NOT run; all execution evidence above
  comes from injected tiny tables, refusal probes, and the test suite.
- Reads/attempts remain 0/1; result remains null; both independent
  reviews except this one remain pending (Pre-RESULT still required
  after any gate run, recomputing all allocations, outcomes, intervals,
  accounting, and gates from the five artifacts).
- The output root remains absent; HEAD is unchanged; no commit was made.

## Complete frozen record (for the Wave-C operator)

- Allocations: N=256: K_total 40, K1 1, K2 39, leakage 264,
  f 1.2873923901554465; N=4096: 840/37/803/4264/1.2995836059713126;
  N=16384: 3399/166/3233/17059/1.29981219126786; N=65536:
  13636/678/12958/68244/1.2999645814655583; N=131072:
  27285/1381/25904/136489/1.2999741058529144; N=262144:
  54583/2776/51807/272979/1.2999788680465925 (residuals in P12_FREEZE
  §2; independently reproduced §4 above).
- Command (verbatim, byte-verified §5): `cd
  /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, `ulimit -v 2097152`,
  `timeout 1800
  /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m
  comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_n_scaling
  --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/
  outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/
  channel_counts.npz --source 1M --floor 1e-15 --target-f 1.3 --n-values
  256 4096 16384 65536 131072 262144 --stream-seeds 2026091820
  2026091821 2026091822 2026091823 2026091824 2026091825 --blocks 64 32
  16 8 4 4 --chunk-rows 512 --out-dir .workbuddy/queue/
  NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/target_f13_n_scaling`
- Streams/root/budgets/schema/gates/labels: streams 2026091820..25
  (masters +10000), root absent until execution, 1800 s / 2 GiB envelope
  (`ulimit -v 2097152`), five scalar-only files, nine integrity gates in
  frozen order (§6), labels `TARGET_F13_N_SCALING_PROFILE_CANDIDATE` /
  `BLOCKED(<earliest gate>)`, no recovery threshold, recovery
  report-only, `undetected` never success.

## Checklist

- [x] Matches OpenSpec spec
- [x] Tests pass (23 focused + 285 combined, pinned interpreter)
- [x] No scope creep (thin runner + focused tests + delta + freeze docs only)
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? —
  No: this wave introduces no new durable failure mode or decision
  beyond the packet; milestone-batched ledger updates per AGENTS.md
  §10.4 remain the main thread's call.
