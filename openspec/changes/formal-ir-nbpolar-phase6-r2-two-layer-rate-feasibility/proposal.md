# Proposal: Phase 6-R2 two-layer rate feasibility

Phase 6-R1 validly established a single-layer scheduler improvement, but the
implemented protocol embeds only L1 (`label=32*x_hat`, low half zero). The
roadmap also requires oracle-L2 and operational candidate-conditioned L2, and
the project objective requires reconciliation efficiency `f <= 1.3`.

Before SCL or further L1 scheduling work, add the smallest decoder-free study
that determines the target block-length band under explicit two-layer BEC
surrogates and audits the missing operational L2 dependency. This study is a
planning bound/sensitivity analysis, not a real-channel or lower-bound theorem.

No SC execution, artifact read, real data, Phase 7, performance implementation,
qualification or promotion is in scope.
