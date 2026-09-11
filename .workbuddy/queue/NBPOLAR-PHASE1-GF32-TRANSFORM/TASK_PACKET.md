# Task packet: NBPOLAR-PHASE1-GF32-TRANSFORM

## 0. Operator contract

Repository: current worktree root (`.`)  
Branch: `codex/nbpolar-phase0`  
OpenSpec owner: `openspec/changes/formal-ir-nbpolar-mvp/`  
Accepted prerequisite: `docs/research_cycles/NBPOLAR-PHASE0/FREEZE_REVIEW_VERDICT.md`  
Lifecycle: `IMPLEMENTATION_AUTHORIZED / FOCUSED_T0_T1_AUTHORIZED`

This packet implements only Phase 1: finite-field adapter, frozen NB-Polar
transform, dense oracle, and source-coordinate extraction. It includes no SC
decoder, channel prior, construction, Model-F, reconciliation protocol, or
performance experiment.

Return only under one of two conditions:

1. `COMPLETE`: every P1 acceptance ID below passes, with changed files and
   exact command/output summary.
2. `BLOCKED`: one exact failing command/error, remedies attempted, and the one
   decision needed from the main thread. Do not return merely because work is
   unfinished.

Do not commit, push, archive OpenSpec, or mark the work accepted. The main
thread owns review and acceptance.

## 1. Read order

Read completely before editing:

1. `AGENTS.md`
2. `AGENT_PROJECT_MEMORY.md` top NB-Polar section
3. `docs/nbpolar/ARCHITECTURE.md`
4. `docs/nbpolar/ROADMAP.md` Phase 0 and Phase 1
5. `docs/nbpolar/VALIDATION_GATES.md`
6. `openspec/changes/formal-ir-nbpolar-mvp/design.md`
7. `openspec/changes/formal-ir-nbpolar-mvp/tasks.md`
8. `comparison_bench/src/comparison_bench/formal_ir/nonbinary_field.py`

Before editing, inspect the current contents of every target file and the
nearest test conventions. Preserve unrelated dirty changes.

## 2. Ownership and file allowlist

The execution session owns only:

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py`
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/algebra.py`
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/transform.py`
- one focused Phase 1 test file under `comparison_bench/tests/`, preferably
  `test_nbpolar_transform.py` unless repository naming conventions require a
  nearby equivalent;
- this packet's `OPERATOR_RETURN.md`, created only at terminal return;
- this `STATUS.yaml`, changed only to `IMPLEMENTATION_CANDIDATE` or `BLOCKED`.

Forbidden edits:

- existing code in `nonbinary_field.py`;
- any existing file under `src/`, `experiments/`, `tools/`, or `results/`;
- existing decoder, NB-LDPC, Cascade, Release, benchmark-output, or real-data
  code;
- `methods/nbpolar.py`, `prior.py`, `construction.py`, `sc.py`, `protocol.py`;
- canonical mathematical decisions, OpenSpec requirements, decision log, and
  Phase 0 verdict;
- sibling checkouts.

If an allowlisted design cannot work without a forbidden edit, stop as
`BLOCKED`; do not silently widen ownership.

## 3. Frozen mathematical contract

### P1-MATH-01 — field

- Symbols are integer scalars/arrays in `0..q-1`.
- Required fields: GF4 for exhaustive tests and GF32 for the MVP.
- GF32 polynomial basis uses primitive polynomial integer `37`
  (`x^5+x^2+1`).
- `alpha=2`; its non-zero multiplicative cycle in GF32 must have length 31.
- Addition is characteristic-two XOR; multiplication and validation come from
  the existing `GF2mField` semantics through a thin, explicit adapter.
- Do not copy the full field implementation into the new package and do not
  add a generalized algebra framework.

### P1-MATH-02 — kernel orientation

For a row-vector pair `[u0,u1]`:

```text
x0 = u0 + alpha*u1
x1 = u1
```

The pair transform is self-inverse in characteristic two. The implementation
must expose this orientation plainly; a transpose or channel-coding convention
is a failure.

### P1-MATH-03 — length-N transform

- `N` is a positive power of two.
- `G_N = F_alpha tensor_power log2(N)` in natural coordinate order.
- There is no implicit bit reversal or Release ordering.
- The fast in-place/buffered butterfly and slow independent dense/reference
  transform must agree exactly.
- Applying the frozen transform twice returns the input exactly.

The dense oracle must be structurally independent enough to expose butterfly
stage/order errors. It may construct a small generator matrix using field
operations or use a literal recursive definition. It must not call the fast
transform internally.

### P1-MATH-04 — source coordinate extraction

Provide a small function that:

1. validates a symbol vector and a one-dimensional coordinate collection;
2. computes `u = transform(a)`;
3. returns `u` and the actual values at the requested coordinates;
4. preserves coordinate order as explicitly documented;
5. preserves disclosed value zero exactly.

This is a source-transform helper, not a reconciliation protocol. Do not add
leakage, tags, transcripts, decoder state, or `IRRunResult` here.

## 4. Required public API

Use the smallest readable API consistent with nearby code. The following
capabilities and semantics are required; exact names may change only if a
nearby repository convention clearly improves them and the return explains
the mapping.

`algebra.py`:

```python
def make_gf2m(m: int, primitive_polynomial: int) -> GF2mField: ...
def make_gf32() -> GF2mField: ...
def validate_symbols(values, q: int, *, name: str = "symbols") -> np.ndarray: ...
```

`transform.py`:

```python
def kernel_pair(u0, u1, *, field, alpha: int): ...
def polar_transform(symbols, *, field, alpha: int = 2) -> np.ndarray: ...
def polar_transform_reference(symbols, *, field, alpha: int = 2) -> np.ndarray: ...
def transform_and_select(symbols, coordinates, *, field, alpha: int = 2): ...
```

Return new arrays unless the function name and docstring explicitly promise
mutation. Keep dtype integer and preserve a stable shape. Reject booleans,
floats, negative symbols, symbols `>=q`, non-vector input, duplicate or
out-of-range coordinates, and non-power-of-two length with clear `ValueError`
or `TypeError`. Do not add schema libraries or elaborate exception wrappers.

`__init__.py` should export only the Phase 1 public surface.

## 5. Implementation constraints

- Python + NumPy only; reuse existing repository dependencies.
- Prefer clear loops/vectorized field-table operations over premature JIT,
  FWHT, caching, or dispatch frameworks.
- No random behavior in production functions.
- Tests may use deterministic `np.random.default_rng(20260911)`.
- No file I/O, environment variables, network, subprocess, or output roots.
- No hashes, manifests, backup systems, compatibility layers, or generalized
  kernel registry.
- No use of LDPC matrices, BP schedules, graph seeds, Cascade state, binary
  Polar PW order, BSC LLR, CRC, or `polar_existing` as a backend.
- Do not import Alice truth into any future-decoder shaped object; Phase 1 has
  no decoder object at all.

## 6. Frozen acceptance matrix

### P1-T0-01 — import and syntax

- New package imports from the repository's supported test environment.
- `python -m py_compile` passes for all three new module files and the focused
  test file.

### P1-T0-02 — GF32 constants and closure

- `q=32`, `m=5`, primitive polynomial `37` are observable and correct.
- `alpha=2` has cycle length exactly 31 over non-zero values.
- Addition/multiplication outputs remain within `0..31`.
- Invalid field parameters and invalid symbols fail clearly.

### P1-T1-01 — literal kernel examples

Test hand-computed/literal pairs including:

- `(0,0)`;
- non-zero `u0` with zero `u1`;
- zero `u0` with non-zero `u1`;
- values whose XOR result is zero;
- at least one independently calculated GF4 and GF32 product.

Every pair transformed twice must return the original pair.

### P1-T1-02 — exhaustive GF4 N=4 oracle

Enumerate all `4^4=256` vectors. For every vector:

- fast transform equals independent reference exactly;
- double transform equals input exactly;
- outputs remain valid GF4 symbols.

### P1-T1-03 — exhaustive GF32 N=2 oracle

Enumerate all `32^2=1024` vectors and apply the same three assertions.

### P1-T1-04 — deterministic random lengths

For GF32 `N in {8,64,256,1024}`, test at least 20 deterministic random vectors
per length:

- fast equals reference exactly;
- inverse/double transform equals input;
- input array is unchanged unless explicitly using a private in-place helper.

If the independent dense oracle is unreasonably slow at N=1024, a literal
recursive reference is acceptable. Do not weaken the N=1024 equality gate.

### P1-T1-05 — no hidden bit reversal

Use basis vectors and at least one non-palindromic vector at N=4 and N=8 to
show that the returned coordinate order matches the literal natural-order
Kronecker convention. Include a regression assertion that would fail under
bit reversal.

### P1-T1-06 — source coordinate semantics

- empty coordinate set returns an empty selected vector;
- arbitrary unsorted coordinates follow the documented input-order contract;
- selected values equal `u[coordinates]` exactly;
- selected zero is retained, not dropped or interpreted as unknown;
- duplicate and out-of-range coordinates fail;
- the helper's `u` equals the standalone transform.

### P1-T1-07 — focused forbidden-dependency audit

Run a scoped search over the new package. Any production import/reference to
LDPC graph/BP, Cascade, binary PW/BSC/LLR/CRC, Model-F, TTBin, real data, or
`polar_existing` is a failure. Test prose may name forbidden concepts only to
assert absence.

## 7. Exact execution plan

The operator may adapt module-style test paths to current repository import
conventions, but must report exact commands actually used.

1. Baseline before edit:

```powershell
git status --short
rg -n "class GF2mField|class FieldSpec" comparison_bench/src/comparison_bench/formal_ir/nonbinary_field.py
```

2. T0:

```powershell
python -m py_compile comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py comparison_bench/src/comparison_bench/formal_ir/nbpolar/algebra.py comparison_bench/src/comparison_bench/formal_ir/nbpolar/transform.py comparison_bench/tests/test_nbpolar_transform.py
```

3. Focused T1, using a fresh task-owned Windows test root if needed:

```powershell
python -m pytest -q -p no:cacheprovider comparison_bench/tests/test_nbpolar_transform.py
```

4. Scope and forbidden dependency checks:

```powershell
git status --short
git diff --check -- comparison_bench/src/comparison_bench/formal_ir/nbpolar comparison_bench/tests/test_nbpolar_transform.py
rg -n "LDPC|PEG|QC|BP|Cascade|\bPW\b|BSC|LLR|CRC|Model-F|TTBin|polar_existing" comparison_bench/src/comparison_bench/formal_ir/nbpolar
git diff --stat -- src experiments tools results comparison_bench/outputs_comparison
```

Expected final audit: zero changes in frozen directories/output roots and zero
forbidden production dependencies. A non-zero `rg` result is triaged only if
it occurs in an explicit non-reuse docstring; production coupling is forbidden.

## 8. Budget and stop rules

- Target implementation wall time: one execution session.
- Focused tests: under 5 minutes total on the local machine.
- No individual test command should run longer than 120 seconds without a
  clear progress reason; stop and report a performance blocker rather than
  reducing coverage.
- No decoder calls, no Model-F/data loading, no result directories.
- Any transform mismatch stops downstream work. Diagnose in this order:
  field table/primitive polynomial, kernel orientation, butterfly pairing,
  stage order, then coordinate order.
- Do not proceed to SC code even when Phase 1 passes.

## 9. COMPLETE return format

Create `OPERATOR_RETURN.md` in this packet directory with:

1. `Terminal: IMPLEMENTATION_CANDIDATE`
2. changed-file list;
3. public API summary;
4. acceptance table P1-T0-01 through P1-T1-07 with PASS/FAIL and evidence;
5. exact commands and concise outputs/counts;
6. scope audit confirming frozen directories and output roots unchanged;
7. known limitations limited to Phase 1;
8. `Next gate: INDEPENDENT_IMPLEMENTATION_REVIEW`;
9. explicit statement that Phase 2, decoder, Model-F, real data, result, and
   scientific claims remain unauthorized.

Set `STATUS.yaml` to `IMPLEMENTATION_CANDIDATE`. Do not set ACCEPTED.

## 10. BLOCKED return format

Create `OPERATOR_RETURN.md` with:

1. `Terminal: BLOCKED(<single root cause>)`;
2. failing acceptance ID and exact command/error;
3. minimal remedies already tried;
4. unchanged/partial files;
5. the one decision needed from the main thread.

Set `STATUS.yaml` to `BLOCKED`. Do not continue with speculative repairs or a
weakened transform convention.

