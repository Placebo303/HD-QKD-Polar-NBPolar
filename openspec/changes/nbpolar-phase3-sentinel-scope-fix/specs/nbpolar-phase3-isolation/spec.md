# Delta specification: Phase 3 dependency isolation

`synthetic.py` and `construction.py` SHALL NOT import the Phase 4 prior adapter.
The package `__init__.py` MAY export the Phase 4 prior API. Existing bans on
binary Polar, method/protocol, and result-layer coupling remain applicable to
all files previously scanned by P3-T1-09.
