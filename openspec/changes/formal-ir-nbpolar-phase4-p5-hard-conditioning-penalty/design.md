# Design

Freeze the X02 strong profile at N256/K1=45/K2=140. Use three new fixed streams
of 128 blocks in one 384-pair attempt. Record the paired four-cell table:
both-exact, oracle-only, operational-only, neither-exact.

The penalty endpoint is the oracle-only event, conditional on requiring zero
operational-only events. Its one-sided 95% Clopper-Pearson lower bound is the
root p of `Pr[Binomial(384,p) >= oracle_only]=0.05`, independently recomputed
without applying Clopper-Pearson to a difference of marginal rates.
