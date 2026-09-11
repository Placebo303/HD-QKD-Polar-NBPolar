# OPERATOR_RETURN — NBPOLAR-PHASE1-GF32-TRANSFORM

Terminal: IMPLEMENTATION_CANDIDATE

## 1. Changed files (new unless noted)

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py` (new, 14 lines)
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/algebra.py` (new, 73 lines)
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/transform.py` (new, 120 lines)
- `comparison_bench/tests/test_nbpolar_transform.py` (new, 255 lines)
- `.workbuddy/queue/NBPOLAR-PHASE1-GF32-TRANSFORM/STATUS.yaml` (edited: `READY_FOR_EXECUTION_SESSION` → `IMPLEMENTATION_CANDIDATE`)

No other file was created, edited, staged, committed, or pushed.

## 2. Public API summary

`algebra.py`: `make_gf2m(m, primitive_polynomial)` (thin adapter: pins
`q=2**m` through `get_field_spec`, rejects a non-pinned polynomial);
`make_gf32()` (frozen `m=5`, poly `37`); `validate_symbols(values, q,
name=...)` (new int64 vector; rejects bool/float/non-vector/out-of-range).

`transform.py`: `kernel_pair(u0, u1, *, field, alpha=2)` returns
`(u0+alpha*u1, u1)`; `polar_transform(...)` fast butterfly, natural
Kronecker order, never mutates input; `polar_transform_reference(...)`
independent dense `u·G_N` via literal Kronecker doubling plus XOR
accumulation, never calls the butterfly; `transform_and_select(...)`
returns `(u, u[coordinates])` in caller coordinate order with zeros kept.

`__init__.py` exports exactly these seven names.

## 3. Acceptance table

| ID | Result | Evidence |
|----|--------|----------|
| P1-T0-01 | PASS | `py_compile` OK on all 4 files; package imports under repo venv (numpy 2.4.4) |
| P1-T0-02 | PASS | `q/m/poly = 32/5/37` observable; alpha=2 cycle exactly 31; 32² add/mul closure; wrong-poly/bool/float/range inputs fail |
| P1-T1-01 | PASS | hand pairs incl. `(0,7)->(14,7)`, `(2,1)->(0,1)`, GF32 `8*8=10`, GF4 `2*2=3`→`(1,2)`; every pair double-applies to identity |
| P1-T1-02 | PASS | all 256 GF4 N=4 vectors: fast==reference, double==input, symbols in range |
| P1-T1-03 | PASS | all 1024 GF32 N=2 vectors: same three assertions |
| P1-T1-04 | PASS | GF32 N in {8,64,256,1024} × 20 `default_rng(20260911)` vectors: fast==reference, double==input, input unmutated |
| P1-T1-05 | PASS | N=4 `e1->[2,1,0,0]`, N=8 `e1->[2,1,0,...]`, hand GF4 `[1,0,3,2]->[1,3,0,2]`, N=8 non-palindromic vs third-path recursion; bit-reversed images asserted unequal |
| P1-T1-06 | PASS | empty→empty; unsorted input order kept; zero retained; dup/oob/2-D/float coords fail; helper `u` == standalone transform |
| P1-T1-07 | PASS | scoped `rg` over the 3 new modules: zero hits (exit 1) |

Total: 17/17 focused tests pass in ~1.4 s.

## 4. Exact commands and outputs

- `git branch --show-current` → `codex/nbpolar-phase0`
- `rg -n "class GF2mField|class FieldSpec" comparison_bench/.../nonbinary_field.py` → lines 22, 54
- `python -m py_compile <4 allowlisted files>` → `COMPILE_OK` (exit 0)
- `python comparison_bench/tests/test_nbpolar_transform.py` (PYTHONPATH=repo root, venv `hd-qkd-polar-comparison`) → `17 passed`, wall ~1.4 s
- `git diff --check -- <nbpolar + test file>` → clean
- `rg -n "LDPC|PEG|QC|BP|Cascade|\bPW\b|BSC|LLR|CRC|Model-F|TTBin|polar_existing" .../nbpolar` → zero hits
- `git diff --stat -- src experiments tools results comparison_bench/outputs_comparison` → empty

Runner adaptation (reported, not hidden): the `pytest` binary is not
installed in any container venv and package installs are forbidden to
this operator, so the packet's `python -m pytest` command fails with
`ModuleNotFoundError: No module named 'pytest'`. The focused test file
therefore uses zero pytest imports (plain asserts, explicit loops,
local `assert_raises`); it runs under plain `python` here and remains
collectible by pytest in an equipped environment. No coverage was cut:
all P1-T0/T1 IDs execute with the packet's seeds and vector counts.

## 5. Scope audit (frozen dirs / output roots unchanged)

`git status --short` after work shows only the pre-existing packet-external
dirty entries (AGENTS.md, AGENT_HANDOFF.md, AGENT_PROJECT_MEMORY.md,
CURRENT_TASK.md, README.md, docs/CURRENT_MAINLINE.md, docs/decision-log.md,
openspec/project.md, plus pre-existing untracked `.workbuddy/`,
`docs/nbpolar/`, `docs/research_cycles/NBPOLAR-PHASE0/`,
`openspec/changes/...` ×2) and the two new allowlisted paths
(`.../formal_ir/nbpolar/`, `.../tests/test_nbpolar_transform.py`).
`git diff --stat` over `src experiments tools results
comparison_bench/outputs_comparison` is empty; `nonbinary_field.py`
and every forbidden path are untouched.

## 6. Known limitations (Phase 1 only)

- Two implementation bugs were found and fixed during this session
  (reference-matvec broadcast axis; empty-list float dtype); both are
  covered by the passing matrix above.
- N=1 transform is defined (identity) but not exercised beyond code path.
- `alpha=0` is accepted (degenerate but well-defined); only alpha=2 is tested.

## 7. Next gate

Next gate: INDEPENDENT_IMPLEMENTATION_REVIEW

## 8. Authorization boundary

Phase 2, SC decoder, Model-F/CAL/VAL/TTBin, real data, result roots,
benchmarks, commits, pushes, qualification, and every scientific claim
remain unauthorized and untouched. No decoder object exists in this
change; no result directory was created.
