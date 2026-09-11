# Heavy autonomous task packet: NBPOLAR-PHASE2-SC-ORACLE

## 0. Mission and authority

Build the first correctness-reference q-ary successive-cancellation decoder
for the accepted native NB-Polar transform, together with an independently
implemented exhaustive oracle and a test suite that localizes failures to
metric algebra, recursion, partial sums, known-coordinate handling, or numeric
support.

This packet grants substantial implementation freedom inside a narrow
scientific boundary. The operator is expected to explore, derive, prototype,
debug, and select a design without requesting approval for ordinary code
choices. It may reject its first design if oracle evidence exposes a flaw.

The task ends only as:

- `COMPLETE / IMPLEMENTATION_CANDIDATE`: all P2 acceptance IDs pass; or
- `BLOCKED(<one root cause>)`: a frozen invariant cannot be met after bounded
  investigation, with exact reproduction and one main-thread decision needed.

The operator cannot mark the implementation accepted or unlock Phase 3.

## 1. Required reading before edits

Read completely:

1. `AGENTS.md`
2. the NB-Polar section at the top of `AGENT_PROJECT_MEMORY.md`
3. `docs/nbpolar/ARCHITECTURE.md`
4. `docs/nbpolar/ROADMAP.md`, especially Phase 2 and stop rules
5. `docs/nbpolar/VALIDATION_GATES.md`
6. `openspec/changes/formal-ir-nbpolar-mvp/design.md`
7. `openspec/changes/formal-ir-nbpolar-mvp/tasks.md`
8. Phase 1 `TASK_PACKET.md`, `OPERATOR_RETURN.md`, and `INDEPENDENT_REVIEW.md`
9. all files under `formal_ir/nbpolar/` and `test_nbpolar_transform.py`

Inspect nearby test/import conventions before choosing filenames. Preserve
unrelated dirty changes.

## 2. Fixed mathematical definition

### P2-MATH-01 — source model

- Input metric `logp_x[j,a]` represents `ln P(X_j=a | B/context)`.
- Shape is exactly `(N,q)`, dtype convertible to float64, symbol axis last.
- Each row is normalized so `logsumexp(row)=0` within absolute `1e-12`.
- `-inf` means exact zero support and must remain zero probability.
- A row with no finite support is invalid and must fail clearly.
- The initial side information is memoryless across transformed source
  coordinates for this reference decoder: block score is
  `sum_j logp_x[j, x_j]`.

Do not introduce scalar LLRs or call SC decision scores a full APP over X.

### P2-MATH-02 — transform and kernel

Use the accepted Phase 1 transform unchanged:

```text
x_left  = beta_left + alpha * beta_right
x_right = beta_right
alpha = 2 in GF32
```

Natural ordering is frozen. Do not add bit reversal. If implementation
experiments suggest a different convention, treat that as a bug to isolate,
not permission to change the transform.

### P2-MATH-03 — q-ary SC node recursion

For paired child symbol log metrics `L0`, `L1`:

```text
minus[u] = logsumexp_v(L0[u + alpha*v] + L1[v])
plus[v | beta_left] = L0[beta_left + alpha*v] + L1[v]
```

Normalize every produced q-vector. At an internal node:

1. build the left synthetic metrics;
2. recursively decode the left `U` subtree;
3. transform that subtree's decoded `U` values to the encoded partial sums
   `beta_left` required by the plus branch;
4. build right metrics conditioned on those partial sums;
5. recursively decode the right subtree;
6. return natural-order `U` decisions.

Using raw left `U` decisions where encoded partial sums are required is a
blocking correctness defect.

### P2-MATH-04 — classic SC conditioning

At coordinate `i`, the SC metric is
`P(U_i | U_0..U_{i-1}, B/context)` with all undecoded suffix coordinates
marginalized. A disclosed coordinate is forced to its supplied value when its
turn is reached. Do not condition an earlier decision on a later disclosed
coordinate merely because the whole disclosure map is available.

This definition must also be used by the exhaustive oracle. If the operator
wants to explore future-known-symbol conditioning, it may note it as a later
research alternative but must not mix it into this implementation.

### P2-MATH-05 — known coordinates

- Known coordinates are positions in U, not X.
- Their values are actual GF symbols, including zero.
- Position membership is separate from symbol value; zero never means unknown.
- Known and unknown coordinates may be interleaved arbitrarily.
- At a known coordinate, record the normalized conditional metric but choose
  the disclosed value even when it is not the MAP symbol.
- Contradictory exact-zero support is not silently repaired. Return a clear
  impossible/failed status or a documented exception consistently.

### P2-MATH-06 — result/provenance

The production decoder result must distinguish at least:

- `u_hat` and reconstructed `x_hat`;
- terminal status;
- one normalized q-vector decision metric per U coordinate, or an explicitly
  documented equivalent sufficient for oracle comparison;
- chosen symbol log score per coordinate;
- metric provenance describing the input as a prior and the returned rows as
  SC conditionals;
- known-coordinate count/mask without conflating zero values with unknown.

Do not expose a field named `final_beliefs` or `APP` that could be confused
with the historical NB-LDPC interface.

## 3. Autonomous design freedom

The operator may decide:

- dataclass versus small immutable records for input/result contracts;
- recursive node objects versus pure recursive functions;
- cached field index tables versus direct field calls, provided the reference
  remains readable and deterministic;
- whether metric validation/normalization lives in `sc.py` or a small
  `metrics.py`;
- whether the oracle lives in `oracle.py` or a clearly separate test helper;
- internal representation of known coordinates;
- exception versus explicit failed-result behavior for impossible disclosed
  values, provided it is deterministic and tested;
- test decomposition and helper organization;
- a small amount of profiling to reject an obviously pathological design.

Before settling, investigate at least two plausible recursion organizations
or explain why one is algebraically forced. Record the chosen architecture and
one rejected alternative in `EXPLORATION_NOTES.md`. This is design evidence,
not a literature review.

The operator may fix a Phase 1 defect only if an oracle test proves it and the
fix is necessary for Phase 2. Such a fix must be minimal, separately listed,
and rerun the complete Phase 1 test. Otherwise Phase 1 files are read-only.

## 4. File ownership

Allowed production paths:

- update `formal_ir/nbpolar/__init__.py` only to export accepted Phase 2 API;
- add `formal_ir/nbpolar/sc.py`;
- optionally add one of `formal_ir/nbpolar/metrics.py` and
  `formal_ir/nbpolar/oracle.py`, or both when separation materially improves
  independence/readability;
- minimal proven fixes to Phase 1 `algebra.py`/`transform.py` under the rule
  above.

Allowed tests and packet artifacts:

- add focused `comparison_bench/tests/test_nbpolar_sc.py`;
- optionally add one additional tiny-oracle test file if that makes independent
  enumeration clearer;
- this packet's `EXPLORATION_NOTES.md`, `OPERATOR_RETURN.md`, and `STATUS.yaml`.

Forbidden:

- `prior.py`, `construction.py`, `protocol.py`, `methods/nbpolar.py`, SCL;
- changes to existing NB-LDPC/Cascade/binary Polar modules;
- Model-F, CAL/VAL/TTBin or real-data loaders;
- benchmark runners, result/output directories, rate scans, leakage or tags;
- new dependencies, JIT, C/C++, GPU, multiprocessing, or generalized plugin
  frameworks;
- sibling checkout edits, commit, push, OpenSpec archive, or claim promotion.

## 5. Independent exhaustive oracle

The oracle must not import or call production SC recursion, minus/plus helpers,
partial-sum helpers, or production decision logic. Reusing the accepted field
and transform is allowed; for the strongest tests, prefer a literal block-score
enumeration that only needs `polar_transform_reference`.

For a candidate prefix `p` and coordinate `i`:

1. enumerate all suffix U assignments for the tiny field/block;
2. transform each complete U candidate to X with the Phase 1 reference;
3. sum the input log metrics at the candidate X symbols;
4. aggregate scores by candidate `U_i` with stable logsumexp;
5. normalize the q-vector;
6. compare production SC at the same decoded/forced prefix.

Required oracle domains:

- exhaustive state coverage for GF4 at N=2 and N=4 where tractable;
- GF32 N=2 coverage;
- deterministic asymmetric, uniform, one-hot, and exact-zero-support metrics;
- prefixes that are not the true or MAP prefix, so correctness is not hidden by
  an easy decision path.

The oracle must provide useful mismatch evidence: N, coordinate, prefix,
candidate symbol, production value, oracle value, and finite/support mismatch.

## 6. Required acceptance matrix

### P2-T0-01 — syntax/import and Phase 1 regression

- `py_compile` all new/modified Phase 2 files and tests.
- Existing `test_nbpolar_transform.py` remains 17/17 under pytest.
- New package imports have no side effects or file I/O.

### P2-T0-02 — metric validation and normalization

Test shape, dtype, q/N consistency, NaN, positive infinity, all-negative-
infinity rows, non-normalized rows, and exact-zero support. Either normalize
finite valid rows explicitly or reject them according to one documented API
contract; do not silently replace invalid rows with uniform metrics.

For valid rows, absolute `max|logsumexp(row)| <= 1e-12`.

### P2-T1-01 — local minus/plus oracle

For GF4 exhaustively enumerate all finite small integer/log-score vectors from
a compact deterministic grid and all valid conditioning symbols. For GF32 use
a deterministic representative matrix including `-inf`. Compare production
minus/plus helpers to direct double-loop definitions:

- probability difference at most `1e-12` after normalization;
- finite log-score difference at most `1e-9`;
- exact finite versus `-inf` support match;
- no NaN.

If helpers remain private, test through an explicit internal test surface or
node-level wrapper without widening the public package API unnecessarily.

### P2-T1-02 — exhaustive SC conditional comparison

Compare every production decision row with the enumeration oracle along the
actual decoded prefix for:

- GF4 N=2 and N=4;
- GF32 N=2;
- no known coordinates;
- partial known coordinates, including known zero and non-MAP known value;
- all known coordinates.

Compare normalized probabilities at absolute `1e-12`, finite log scores at
absolute `1e-9`, and support exactly. Whole-block MAP equality is not required
and must not be used as the oracle.

### P2-T1-03 — partial-sum discriminator

Include at least one fixed N=4 or N=8 case where using raw left U decisions in
the plus branch produces a different conditional from using transformed
partial sums. Assert the oracle-correct answer and demonstrate that the test
would fail for the wrong implementation.

### P2-T1-04 — known-symbol semantics

Cover empty, sparse, interleaved, and all-known sets. Confirm:

- known zero is selected as zero;
- a known non-MAP value is forced;
- arbitrary coordinate order in input is either accepted with explicit mapping
  or rejected clearly according to the chosen API;
- duplicates, out-of-range positions, invalid symbols, and shape mismatches
  fail clearly;
- a later known coordinate does not alter an earlier classic-SC conditional.

### P2-T1-05 — noiseless loopback

For GF4 exhaustive N=4 and GF32 deterministic N in `{2,4,8,64}`:

1. generate U/A symbols;
2. compute X/A through the accepted transform;
3. construct one-hot `logp_x` at the true X values with exact `-inf` elsewhere;
4. decode under no-known, partial-known, and all-known patterns;
5. require `u_hat` and `x_hat` exact in 100% of cases.

No Alice truth may enter the decoder API. Tests construct the metric externally.

### P2-T1-06 — nontrivial correction evidence

Construct at least one tiny asymmetric metric where independent X-coordinate
MAP contains an error but source SC plus a disclosed U coordinate recovers the
full U/X block. Freeze the literal metric and expected decisions in the test.
This proves the decoder is doing more than echoing pointwise MAP without making
a performance claim.

### P2-T1-07 — surprisal-chain identity

Using the independent oracle with a forced true prefix, verify for tiny cases:

```text
sum_i ln P(U_i=true_i | U_<i=true_<i, B)
  == sum_j logp_x[j, X_j=true_j]
```

Compare at absolute `1e-9` for finite cases and test an exact-zero impossible
case separately. Do not add a truth/forced-prefix argument to the operational
decoder merely to make this test convenient.

### P2-T1-08 — deterministic failure attribution

Every intentionally invalid/impossible case must land in one stable category:

- metric contract;
- field/shape contract;
- known-coordinate contract;
- impossible disclosed value;
- numeric nonfinite failure.

No broad catch may convert one category into uniform metrics or a successful
decode.

### P2-T1-09 — forbidden coupling audit

New production Phase 2 files must have zero dependency on Model-F, LDPC/BP,
Cascade, binary PW/BSC/LLR/CRC, SCL, real-data loaders, `IRRunResult`, output
roots, or `polar_existing`. Test/oracle prose may mention them only in an
explicit absence assertion.

### P2-T1-10 — bounded resource sanity

Run at least one GF32 N=64 noiseless decode and one finite asymmetric decode.
Record wall time and peak object/array shapes or a concise complexity account.
This is a sanity check only. Do not tune, optimize, or claim a throughput
result. A single N=64 reference decode taking more than 30 seconds is a design
warning requiring explanation before return.

## 7. Exploration workflow

Use this order so failures remain attributable:

1. Freeze an independent stable logsumexp/normalization oracle.
2. Validate GF4 minus/plus locally before building recursion.
3. Make N=2 SC agree with enumeration for arbitrary prefixes.
4. Add N=4 recursion without known coordinates.
5. Add the partial-sum discriminator.
6. Add known coordinates, including zero and non-MAP values.
7. Add noiseless loopback and surprisal-chain tests.
8. Only then run N=64 resource sanity and full focused regression.

When a mismatch occurs, classify it before editing:

- local q-vector mismatch -> field indexing or normalization;
- N=2 only -> kernel orientation/minus/plus;
- N>=4 plus-side only -> partial sums or stage order;
- known-coordinate only -> membership/value contract;
- one-hot only -> `-inf` support handling;
- oracle and SC agree but hard decode is poor -> do not change Phase 2; that is
  construction/prior work for a later packet.

Do not respond to a mismatch by changing alpha, graph/topology, seed, block
window, disclosure count, or adding SCL.

## 8. Test commands and environments

Use the existing Miniforge environment for the independent pytest path:

```powershell
$env:PYTHONPATH=(Get-Location).Path
D:/software/Miniforge3/python.exe -m pytest -q -p no:cacheprovider comparison_bench/tests/test_nbpolar_transform.py comparison_bench/tests/test_nbpolar_sc.py
```

If a second oracle test file is created, include it explicitly. Also run:

```powershell
python -m py_compile <all modified production and test Python files>
git diff --check -- comparison_bench/src/comparison_bench/formal_ir/nbpolar comparison_bench/tests/test_nbpolar_transform.py comparison_bench/tests/test_nbpolar_sc.py
git status --short
git diff --stat -- src experiments tools results comparison_bench/outputs_comparison
rg -n "LDPC|PEG|QC|BP|Cascade|\bPW\b|BSC|LLR|CRC|SCL|Model-F|TTBin|polar_existing|IRRunResult" comparison_bench/src/comparison_bench/formal_ir/nbpolar
```

The existing pytest `cache_dir` warning is known and non-blocking if collection
and tests complete. Do not edit global pytest configuration in this packet.

## 9. Budget

- One heavy autonomous execution session.
- Tiny enumeration must remain bounded: GF4 N<=4 and GF32 N=2 only.
- Focused full test wall target: under 5 minutes.
- N=64 single-decode warning threshold: 30 seconds.
- No N=256/1024 decoder performance run in this packet.
- No raw/private data access, network, package installation, or result root.

If exhaustive enumeration threatens the budget, reduce redundant metric-grid
combinations while retaining every acceptance category. Do not reduce the
field/block domains or tolerance gates without returning BLOCKED.

## 10. Required exploration notes

Create `EXPLORATION_NOTES.md` containing:

1. the two recursion/data-structure alternatives considered;
2. selected design and why it matches natural-order `F tensor n`;
3. how partial sums are represented and proved correct;
4. oracle independence argument;
5. numerical normalization and exact-zero policy;
6. the first meaningful mismatch found and how its layer was identified;
7. any Phase 1 issue discovered, whether changed or left as limitation;
8. measured N=64 sanity time and why no optimization was added.

Keep it technical and compact. Do not turn it into a general research essay.

## 11. COMPLETE return

Create `OPERATOR_RETURN.md` with:

1. `Terminal: IMPLEMENTATION_CANDIDATE`;
2. changed files and line counts;
3. selected API and recursion design;
4. P2-T0-01/02 and P2-T1-01..10 table with exact evidence;
5. pytest and compile commands/results;
6. oracle maximum probability/log-score errors and support mismatch count;
7. noiseless exact counts by field/N/known pattern;
8. partial-sum discriminator identity;
9. nontrivial correction example summary;
10. N=64 sanity time;
11. frozen-directory and forbidden-coupling audit;
12. known limitations and rejected alternatives;
13. `Next gate: INDEPENDENT_IMPLEMENTATION_REVIEW`;
14. explicit statement that Phase 3, Model-F, real data, benchmark/result,
    SCL, protocol, qualification, and scientific conclusions remain closed.

Set `STATUS.yaml` to `IMPLEMENTATION_CANDIDATE`. Do not modify decision-log,
project memory, canonical roadmap, or OpenSpec task checkboxes; main review owns
those updates.

## 12. BLOCKED return

Create `OPERATOR_RETURN.md` with:

1. `Terminal: BLOCKED(<single root cause>)`;
2. first failing acceptance ID;
3. smallest exact reproduction and error/mismatch table;
4. which layers already passed;
5. at least two investigated implementation approaches when relevant;
6. bounded remedies attempted;
7. partial file list;
8. one decision needed from the main thread.

Set `STATUS.yaml` to `BLOCKED`. Leave Phase 3 closed. Do not weaken a tolerance,
change the transform convention, add SCL, or tune unrelated parameters to make
the failure disappear.
