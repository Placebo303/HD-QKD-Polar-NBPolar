# Phase 4-P1 post-ruling result

State: `P1_IMPLEMENTATION_CANDIDATE`.

The historical `P1_RESULT.md` remains the immutable first return showing the
frozen P3-T1-09 conflict. Main-thread ruling option (a) scoped that sentinel to
its intended algorithm layer without changing Phase 1-3 production code.

## Verification

Main thread ran from WSL with the sibling venv as the Python runtime only:

```text
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q
-p no:cacheprovider
comparison_bench/tests/test_nbpolar_transform.py
comparison_bench/tests/test_nbpolar_sc.py
comparison_bench/tests/test_nbpolar_construction.py
comparison_bench/tests/test_nbpolar_r1.py
comparison_bench/tests/test_nbpolar_prior.py
```

Result: `66 passed, 1 warning in 38.14s`, exit 0. The warning is the existing
unknown pytest `cache_dir` option and does not affect collection or results.

Independent focused review returned PASS WITH COMMENTS and separately reran
the decoder-free prior suite: 11/11 passed. It confirmed that common
legacy/protocol/result bans still cover all original files, `.prior` remains
forbidden in `synthetic.py` and `construction.py`, the required package export
contains exactly three types and six pure functions, and no oracle helper is
exported. P2 remains all-false.

No CAL, Model-F, SC decoder from the P1 adapter, DEV/EVAL, benchmark, real data,
floor selection, commit, push, or scientific claim occurred. Independent P1
acceptance remains the next lifecycle gate.
