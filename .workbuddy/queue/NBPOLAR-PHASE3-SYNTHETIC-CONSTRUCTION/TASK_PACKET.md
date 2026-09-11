# Heavy autonomous task packet: Phase 3 synthetic construction

## 0. Objective

Implement and falsify the first NB-Polar construction pipeline without touching
QKD data. The pipeline must answer four separate questions:

1. Do the q-ary synthetic channel generators produce the declared posterior?
2. Does genie traversal estimate the correct synthetic-coordinate risks?
3. Does the selected disclosure order reflect polarization rather than input
   index or a binary PW import?
4. At one frozen easy q=32 point, does accepted Phase 2 SC correct blocks whose
   pointwise Bob MAP is initially wrong?

The operator has freedom to explore algorithms and data structures, but must
preserve disjoint data streams and the one-shot EVAL gate. A failed result must
remain attributable to generator, construction, ordering, decoder integration,
or finite sample/block effects.

## 1. Read before editing

Read completely:

- `AGENTS.md` and the current NB-Polar entries in `AGENT_PROJECT_MEMORY.md`;
- `docs/nbpolar/ARCHITECTURE.md`, `ROADMAP.md`, `VALIDATION_GATES.md`;
- `openspec/changes/formal-ir-nbpolar-mvp/{design,tasks}.md`;
- Phase 1 and Phase 2 packets, operator returns, exploration notes, and
  independent reviews;
- every current file in `formal_ir/nbpolar/` and both focused test files.

Before editing, record current status and preserve unrelated dirty files.

## 2. Fixed definitions

### P3-MATH-01 — source/channel orientation

Generate Alice source symbols `X` uniformly in GF(q). Bob observes side
information `Y`; the decoder input is `logp_x[j,a] = ln P(X_j=a | Y_j)`.
Alice transforms `U = X G_N`. Construction estimates the conditional synthetic
channels of U given Y and a true U prefix. Do not reverse Alice/Bob axes.

### P3-MATH-02 — q-ary erasure side information

For erasure probability `epsilon`:

- with probability `1-epsilon`, `Y=X` and the posterior is one-hot at X;
- with probability `epsilon`, Y is a distinct erasure marker and the posterior
  is uniform over q symbols;
- erasure decisions and X samples use an explicit RNG passed by the caller;
- no hidden global RNG.

For the 2x2 kernel, analytic synthetic erasure probabilities are:

```text
epsilon_minus = 2*epsilon - epsilon**2
epsilon_plus  = epsilon**2
```

Apply this recursion in the same natural U-coordinate order as the accepted
transform. This analytic vector is an oracle for erasure construction only.

### P3-MATH-03 — q-ary symmetric side information

For QSC crossover `p` with uniform X:

- `Y=X` with probability `1-p`;
- otherwise Y is uniform over the other `q-1` symbols;
- posterior equals `1-p` at `a=Y` and `p/(q-1)` elsewhere;
- require `0 <= p <= (q-1)/q`; the endpoint may be supported or clearly
  rejected, but behavior must be documented and tested.

### P3-MATH-04 — genie construction statistics

For each TRAIN sample, traverse U in natural order while forcing the true
prefix only inside the construction path. At coordinate i record the normalized
conditional `p_i` and accumulate:

```text
h_i = E[-log2 p_i[U_i_true]]
e_i = E[1 - max_a p_i[a]]
```

Also record finite sample counts and impossible/support failures. The
operational `sc_decode` API must not acquire an Alice-truth argument. A private
shared traversal core is allowed only if the operational wrapper cannot expose
truth and the Phase 2 suite remains unchanged.

The initial disclosure order is deterministic descending `(e_i, h_i,
-coordinate)` or another explicitly justified risk order. Ties resolve by
coordinate index. Binary PW is forbidden.

### P3-MATH-05 — disclosure semantics

Construction returns an ordered U-coordinate list. For a selected count K,
Alice discloses actual U values at the first K coordinates. SC receives those
positions/values. Count K is a synthetic development control in this phase;
do not call `5*K` a complete protocol leakage result and do not add a tag.

## 3. Autonomous design space

The operator may choose:

- whether channel generators return a dataclass or `(x,y,logp)` arrays;
- vectorized versus batch-loop generation;
- a private decision-policy callback, a dedicated genie traversal, or another
  clean method to reuse SC algebra without exposing truth in `sc_decode`;
- online accumulators versus retained per-sample statistics;
- construction result dataclass fields and compact diagnostics;
- how to compare rankings when Monte Carlo ties occur;
- TRAIN/DEV batch sizes above the packet minima if runtime remains bounded;
- a bounded DEV-only search over the frozen candidate grid below;
- implementation refactors within new Phase 3 files.

Investigate at least two genie-traversal designs and record the choice in
`EXPLORATION_NOTES.md`. If a Phase 2 change is mathematically necessary, prove
it with a failing accepted regression, make the smallest fix, and rerun all
Phase 1/2 tests. Otherwise Phase 1/2 production code is read-only.

## 4. Allowed files

Production:

- add `formal_ir/nbpolar/synthetic.py`;
- add `formal_ir/nbpolar/construction.py`;
- update `formal_ir/nbpolar/__init__.py` for the small Phase 3 public surface;
- minimal proven Phase 2 refactor under §3, reported separately.

Tests and task artifacts:

- add `comparison_bench/tests/test_nbpolar_construction.py`;
- optionally one additional focused synthetic-generator test file;
- this packet's `EXPLORATION_NOTES.md`, `EVAL_FREEZE.md`,
  `REVIEWER_GO_EVAL_FREEZE.md`, `OPERATOR_RETURN.md`, and `STATUS.yaml`.

Forbidden:

- Model-F/prior adapters, CAL/VAL/TTBin and all real/private data;
- `methods/nbpolar.py`, protocol/tag/leakage/rate-adaptation/SCL code;
- existing NB-LDPC, Cascade, binary Polar, Release, or sibling files;
- production benchmark/output roots;
- external packages, network, multiprocessing, GPU/JIT optimization;
- commit, push, qualification, promotion, or Phase 4 work.

All Phase 3 evidence stays as compact text/tables inside the WorkBuddy packet;
do not create `run_01` or write under results/output directories.

## 5. Frozen stream separation

Use distinct RNG instances and seeds:

```text
unit/oracle seed = 2026091200
TRAIN seed       = 2026091201
DEV seed         = 2026091202
EVAL seed        = 2026091203
```

TRAIN builds the construction. DEV selects one candidate from the allowed grid.
EVAL is used once after freeze and cannot alter K, channel point, order, or
thresholds. No EVAL sample may enter construction or candidate selection.

The operator must make accidental seed/stream reuse structurally visible in
the API and tests. Seed integers are provenance; do not add checksum machinery.

## 6. TRAIN/DEV candidate grid

The primary channel for the first gate is q=32 erasure side information:

```text
q = 32
N = 256
epsilon in {0.05, 0.10, 0.15, 0.20}
K_margin in {16, 24, 32}
K = ceil(N*epsilon) + K_margin
TRAIN samples >= 512
DEV blocks = 100 per candidate
EVAL blocks = 300 for the selected candidate
```

Build one construction per epsilon or justify reuse only if the analytic and
genie definitions make it exact. Candidate selection is deterministic:

1. retain candidates with DEV exact recovery >=98/100;
2. among retained candidates choose smallest K;
3. then smaller epsilon;
4. then smaller margin.

If none passes, do not tune outside the grid. Return
`BLOCKED(NO_EASY_SYNTHETIC_POINT)` with per-candidate results and attribution.

QSC is generator/construction evidence in this packet, not the 300-block gate.
Use q=4 tiny and at least one q=32 N<=64 DEV sanity point; do not search QSC for
a replacement success after an erasure-grid failure.

## 7. Pre-EVAL freeze and internal review

After TRAIN/DEV and before reading EVAL, create `EVAL_FREEZE.md` containing:

- selected epsilon, K, margin and exact disclosure coordinate list;
- construction sample count and TRAIN seed;
- DEV table for all candidates and deterministic selection proof;
- EVAL seed 2026091203 and exactly 300 blocks;
- pass criteria below;
- exact command and time/resource stop;
- statement that EVAL has not yet run.

Then request reviewer-go to inspect code, tests, stream separation, selection,
and `EVAL_FREEZE.md`. Save its result verbatim or faithfully in
`REVIEWER_GO_EVAL_FREEZE.md`. Only a reviewer-go PASS permits the one EVAL run.
Needs-changes may be repaired and re-reviewed before EVAL. A FAIL or unavailable
reviewer stops as BLOCKED; do not self-authorize.

## 8. Acceptance matrix

### P3-T0-01 — syntax/import/regression

- Compile all modified/new files.
- Phase 1+2 tests remain 33/33.
- Phase 3 imports perform no I/O and use no global RNG.

### P3-T1-01 — generator empirical contract

At fixed seeds, verify exact shapes/support/posterior values. On at least 20,000
scalar draws per channel, empirical erasure/crossover frequencies must be
within a predeclared binomial tolerance (for example 5 standard deviations plus
one count). This is a generator check, not a channel-performance result.

### P3-T1-02 — erasure analytic recursion

- N=2 exactly matches `2e-e^2` and `e^2` in natural coordinate order.
- N in {4,8,256} produces values in [0,1] and preserves average epsilon within
  absolute 1e-12.
- epsilon 0 and 1 endpoints behave exactly.

### P3-T1-03 — tiny genie versus exhaustive oracle

For GF4 N<=4 erasure and QSC samples, compare every genie conditional used by
construction with `oracle_sc_metric` at the true prefix. Require probability
error <=1e-12, finite log error <=1e-9, support mismatch zero.

### P3-T1-04 — construction statistics

- `h_i` lies in [0,log2(q)] and `e_i` in [0,1-1/q] within numeric tolerance;
- noiseless channel yields all-zero risk;
- fully erased uniform channel yields the analytically expected limit;
- deterministic repeats with the same TRAIN seed are identical;
- changed seed changes samples but preserves declared metadata;
- order is a permutation of 0..N-1 with deterministic tie-breaking.

### P3-T1-05 — polarization signal

For q=32, N=256, epsilon=0.10:

- analytic erasure vector has the same mean epsilon within 1e-12;
- at least 20% of coordinates are near an extreme using frozen thresholds
  `z<=0.01 or z>=0.99`;
- genie risk has positive Spearman rank correlation with analytic erasure risk,
  target >=0.90; implement the rank calculation locally without adding scipy;
- top-K overlap for K=ceil(25.6)+24=50 is at least 80%.

If Monte Carlo noise misses either ranking gate, increase TRAIN samples within
the time budget before EVAL; do not inspect EVAL or change thresholds.

### P3-T1-06 — disclosure/decoder integration

On tiny and N=64 cases, verify that disclosed positions are U coordinates,
actual values including zero are retained, and SC receives no truth outside the
disclosed set. A later known coordinate must retain classic SC semantics.

### P3-T1-07 — initial MAP error

For every DEV/EVAL block, record whether pointwise `argmax(logp_x)` differs from
X. This is computed before SC. The EVAL pass requires at least 240/300 blocks
(80%) to have an initial symbol error; no truth-centered metric construction is
allowed.

### P3-T1-08 — one-shot easy-point EVAL

For the frozen selected erasure candidate over exactly 300 EVAL blocks:

- all 300 attempted unless a registered resource/numeric stop occurs;
- exact recovery count >=285/300 (failure <=5%);
- initial-error blocks >=240/300;
- zero NaN, invalid metric, impossible-disclosure, or resource abort;
- exact means both U and reconstructed X match;
- report failures by block index without rerun or replacement.

This is a development gate only. Do not call it FER qualification or infer
Model-F/QKD performance.

### P3-T1-09 — stream and oracle isolation

Tests must fail if TRAIN/DEV/EVAL seeds alias, if EVAL samples enter
construction, if the construction uses evaluation outcomes to reorder
coordinates, or if production construction imports binary PW/Release order.

### P3-T1-10 — forbidden coupling and resource sanity

Scoped production search must find zero Model-F, TTBin, CAL/VAL, LDPC/BP,
Cascade, PW/BSC/LLR/CRC/SCL, protocol, `IRRunResult`, or output-root dependency.
Record TRAIN, DEV and EVAL wall times. Total task target is under 30 minutes and
peak memory should stay comfortably below 2 GiB; if exceeded, stop and report.

## 9. Failure attribution order

On failure, inspect in this order:

1. generator empirical/posterior contract;
2. natural-order analytic erasure recursion;
3. genie conditional versus exhaustive oracle;
4. `h_i/e_i` accumulation and rank/tie semantics;
5. disclosure coordinate/value plumbing;
6. accepted Phase 2 SC integration;
7. finite TRAIN noise;
8. only then finite N/K insufficiency within the frozen grid.

Do not change alpha, import binary PW, add SCL, tune EVAL, reuse EVAL in TRAIN,
or modify the accepted decoder to rescue a construction failure.

## 10. Commands

Use the existing Miniforge pytest environment:

```powershell
$env:PYTHONPATH=(Get-Location).Path
D:/software/Miniforge3/python.exe -m pytest -q -p no:cacheprovider comparison_bench/tests/test_nbpolar_transform.py comparison_bench/tests/test_nbpolar_sc.py comparison_bench/tests/test_nbpolar_construction.py
```

Also run scoped compile, `git diff --check`, forbidden dependency search, and:

```powershell
git status --short
git status --short -- src experiments tools results comparison_bench/outputs_comparison comparison_bench/src/comparison_bench/formal_ir/nonbinary_field.py
```

Do not edit pytest configuration to remove the known `cache_dir` warning.

## 11. COMPLETE return

Create `OPERATOR_RETURN.md` containing:

1. `Terminal: IMPLEMENTATION_CANDIDATE_SYNTHETIC_GATE_PASS`;
2. changed files and selected construction architecture;
3. full P3-T0/T1 table;
4. generator empirical checks;
5. analytic/genie oracle errors;
6. construction statistics and rank/overlap evidence;
7. full DEV candidate table;
8. reviewer-go EVAL-freeze verdict;
9. frozen EVAL identity, 300-block exact/initial-error/failure counts;
10. runtime/memory and scope audits;
11. rejected designs and discovered/fixed bugs;
12. `Next gate: INDEPENDENT_IMPLEMENTATION_AND_RESULT_REVIEW`;
13. explicit refusal of Model-F, real-data, protocol, SCL, qualification,
    promotion, Phase 4, commit and push claims.

Set status to `IMPLEMENTATION_CANDIDATE_SYNTHETIC_GATE_PASS`. Do not ACCEPT.

## 12. BLOCKED return

Create `OPERATOR_RETURN.md` with terminal
`BLOCKED(<GENERATOR|ANALYTIC_ORDER|GENIE_ORACLE|CONSTRUCTION|NO_EASY_SYNTHETIC_POINT|EVAL_REVIEW|EVAL_GATE|RESOURCE>)`, the first failing gate,
exact evidence, layers already cleared, remedies tried without EVAL leakage,
and the one decision needed. Preserve a failed one-shot EVAL unchanged. Do not
continue to Phase 4.
