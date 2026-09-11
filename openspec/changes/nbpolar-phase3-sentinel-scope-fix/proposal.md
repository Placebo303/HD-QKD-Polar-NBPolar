# Proposal: scope the Phase 3 prior-coupling sentinel

## Problem

P3-T1-09 combines two different boundaries in one text pattern. It correctly
forbids `synthetic.py` and `construction.py` from importing the later prior
adapter, but also applies `from .prior` to package `__init__.py`. Phase 4-P0
independently requires the accepted public prior API to be exported there.
Those frozen requirements are mutually exclusive.

## Change

Keep all existing forbidden legacy/protocol patterns on all three files. Apply
the `.prior` import ban only to `synthetic.py` and `construction.py`. No
production implementation, algorithm, stream, threshold, or Phase 3 evidence
changes.
