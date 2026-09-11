# Design: separate package-surface and algorithm-layer checks

P3-T1-09 SHALL use a common legacy/protocol pattern for `synthetic.py`,
`construction.py`, and `__init__.py`. A separate `.prior` pattern SHALL apply
only to `synthetic.py` and `construction.py`. This preserves Phase 3 dependency
isolation while allowing Phase 4-P0's explicit package export.

No import-spelling evasion, lazy import, or relocation of the accepted API is
allowed. The test continues to report exact filename, line and content.
