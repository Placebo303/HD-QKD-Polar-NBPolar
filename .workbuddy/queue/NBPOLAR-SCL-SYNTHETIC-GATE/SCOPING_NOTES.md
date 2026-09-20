# SCOPING_NOTES.md — NBPOLAR-SCL-SYNTHETIC-GATE (no-contact statement)

- No-contact statement: this scoping performed NO implementation, NO execution, NO protected
  opens (V25 counts, parquet/pairs, 1M/1.5M/2M content, `raw_prior_*.npz`), NO decoder runs,
  NO data contact of any kind. All cited numbers are read from already-committed synthetic
  probe results (X14/X15/X16/X17), the committed survey file, the frozen `sc.py` docstring
  and signature, and the committed decision-log — read-only inventory only.
- SCL stays locked: this track is a SEPARATE project from RN and all accepted packets. No
  line in this scoping unlocks SCL, implements a list decoder, touches `formal_ir/nbpolar/`
  existing modules, or makes an unlock/FER/reliability/efficiency claim.
- RN scope untouched: reduced-N persistence, H2, P20T, and all accepted real-data evidence
  are outside this track. No H2 input, no construction/order derivation, no acquisition or
  closeout decision is made here.
- Seed hygiene: band 2026092500..2026092519 is reserved-but-unactivated (planner grep clean
  2026-09-20, zero hits repo-wide for `20260925`). The occupied bands 20260923xx..20260924xx
  (incl. X14 2026092350..2357, X15 2026092369..2377, X16 2026092380..2388, X17
  2026092390..2399, P20T 2026092400..2407/2410..2413, P20S 2026092360..2367) were avoided.
  Re-grep is required at any future freeze before activation; reservation alone authorizes
  nothing.
- Gate posture: proposal (S1) is this scoping. Freeze, implementation, tests, execution,
  review, and acceptance (S2..S7) are each NOT AUTHORIZED and need explicit future gates.
- No commit/push performed or authorized by this scoping.
