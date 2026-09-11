# Main-thread ruling — P3-T1-09 versus Phase 4-P0 export

Decision: option **(a)**, scope the sentinel to its intended algorithm layer.

`synthetic.py` and `construction.py` remain forbidden from importing `.prior`.
`__init__.py` may perform the Phase 4-P0-mandated public API export. All common
binary-Polar, method, protocol and result-layer bans remain active on the
original three-file scan. The change is specified by
`openspec/changes/nbpolar-phase3-sentinel-scope-fix/`.

This resolves a contradictory test contract. It does not alter Phase 3 code or
evidence, authorize CAL/Model-F/SC/DEV/EVAL, or accept the P1 implementation.
