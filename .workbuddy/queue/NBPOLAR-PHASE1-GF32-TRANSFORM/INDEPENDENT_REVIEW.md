# Independent review: NBPOLAR-PHASE1-GF32-TRANSFORM

Date: 2026-09-11  
Verdict: `IMPLEMENTATION_ACCEPTED`

## Reviewed scope

- `formal_ir/nbpolar/__init__.py`
- `formal_ir/nbpolar/algebra.py`
- `formal_ir/nbpolar/transform.py`
- `tests/test_nbpolar_transform.py`
- operator return and frozen task packet

The fast butterfly and dense Kronecker reference are independent code paths.
The basis-vector tests distinguish natural order from bit reversal. GF4 N=4
and GF32 N=2 exhaustive checks, deterministic GF32 lengths through N=1024,
source-coordinate order, retained zero values, input immutability, and invalid
input behavior match the packet.

## Independent execution

The system Python 3.11 and 3.12 interpreters do not contain pytest. A separate
installed environment was found at `D:/software/Miniforge3/python.exe` with
pytest 9.0.3. The exact independent command was:

```powershell
$env:PYTHONPATH=(Get-Location).Path
D:/software/Miniforge3/python.exe -m pytest -q -p no:cacheprovider comparison_bench/tests/test_nbpolar_transform.py
```

Result: `17 passed, 1 warning in 2.06s`. The warning is the repository-level
unknown pytest option `cache_dir`; it does not affect collection or results.
The plain-Python runner also independently returned `17 passed`.

`np.int64` inputs are accepted through `numbers.Integral` in the reused field
backend. Frozen code/output directories and `nonbinary_field.py` have zero
diff; the scoped forbidden-dependency search has zero hits.

## Accepted limitations

- `N=1` is a documented identity code path and lacks a dedicated test.
- The public alpha argument accepts zero. The accepted MVP configuration is
  still fixed to primitive `alpha=2`; Phase 2 must not select or advertise a
  degenerate kernel.

These do not change the Phase 1 transform result. Any future generalized
kernel API must add its own admissibility contract.

## Boundary

This acceptance covers Phase 1 implementation and focused synthetic tests.
It is not decoder, Model-F, real-data, performance, qualification, result, or
scientific evidence. Phase 2 requires its own packet.
