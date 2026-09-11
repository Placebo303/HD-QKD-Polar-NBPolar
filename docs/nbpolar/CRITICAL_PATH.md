# NB-Polar implementation critical path

This sequence is intentionally serial. A later step is not started when the
preceding gate has failed or is still unauthorized.

1. **Review and freeze the packet.** Review DOCUMENT_INDEX, ASSET_MAP,
   ARCHITECTURE, ROADMAP, VALIDATION_GATES, and the Phase 0 packet together.
   Confirm the scope contains no Release file, result root, raw input, or
   decoder execution. Keep all authorization flags false.
2. **Add the algebra contract.** Create
   comparison_bench/src/comparison_bench/formal_ir/nbpolar/algebra.py with
   a Polar-neutral GF32 adapter, explicit polynomial 37, alpha=2, symbol
   bounds, and 5+5 physical-label packing helpers. Reuse the existing
   GF2mField only behind this adapter.
3. **Prove the transform.** Add transform.py with the row-vector
   F_alpha butterfly and a slow dense reference. Run exhaustive GF4 N=4,
   GF32 N=2, and random N=8/64/256/1024 equivalence plus self-inverse
   tests. Stop on any orientation, index-order, or inverse mismatch.
4. **Add source-coordinate handling.** Implement extraction of U=A G and
   explicit known-coordinate values. Test zero, non-zero, arbitrary, and
   all-public disclosures. No decoder is involved yet.
5. **Add reference q-ary SC.** Create sc.py with normalized log-domain
   minus/plus recursions, left partial sums, exact-zero support, and a
   metric-provenance field. Add an independent N<=4 enumerator and compare
   every conditional distribution to 1e-12. Then pass the noiseless source
   loopback and finite-score gates.
6. **Only after the SC gate, add synthetic channels and construction.** Add
   QSC/erasure generators and a genie Monte Carlo reliability order using
   disjoint train/evaluation streams. First prove that SC corrects an
   intentionally wrong initial MAP; do not import binary PW order.
7. **Only after synthetic construction passes, add Model-F.** Adapt CAL counts
   with the per-Bob-column concentration contract, expose P(high|B) and
   P(low|high,B), and run L1, oracle-L2, and candidate-L2 as separate
   diagnostics. Verify axes, normalization, held-out CE, and truth isolation.
8. **Only after prior diagnostics pass, add reconciliation protocol.** Wrap
   the normal IRMethod/IRRunResult boundary, publish one static coordinate
   set with actual GF32 values, re-encode the full source, and verify with
   one final independent Toeplitz tag. Recompute static and key-dependent
   leakage independently.
9. **Only after protocol accounting passes, add rate adaptation.** Introduce
   nested disclosure sets and one restart-from-scratch schedule. Count every
   invocation and never let a tag select a decoder path.
10. **Only after the reference route is accepted, add performance features.**
    Implement ordinary q-ary SCL with L in {1,4,8}, require L=1 to equal SC,
    then profile and optimize. CRC, puncturing, shortening, FWHT, and real
    data each need their own scoped gate.

The first coding handoff is therefore algebra.py + transform.py + focused T0
tests. It must return before sc.py is started. The first scientific handoff
is a noiseless and enumerated SC result; it is not a Model-F benchmark.

## Stop attribution

- Algebra/transform failure: inspect field basis, alpha, row orientation,
  natural ordering, and dense-reference indexing.
- SC failure with a correct transform: inspect log-sum-exp, plus partial sums,
  known values, and metric provenance.
- Synthetic failure with a correct SC oracle: inspect construction or metric
  mismatch before adding SCL.
- Model-F failure: inspect axis, smoothing, support, and train/eval split.
- Protocol failure: inspect symbol packing, leakage units, disclosure recount,
  and verification invocation accounting.

