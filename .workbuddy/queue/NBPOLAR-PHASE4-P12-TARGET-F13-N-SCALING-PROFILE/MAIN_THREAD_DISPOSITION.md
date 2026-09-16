# Main-thread disposition — Phase 4-P12

Accept the terminal result **`BLOCKED(resource_limits_met_and_no_abort)`**.
The sole run and artifact read are consumed. No scientific profile is accepted:
the in-memory smaller-N work was never persisted and N=262144 failed while
allocating the candidate-conditioned L2 metric. Independent reviews establish
that this was one genuine execution and no rerun occurred.

The failure is outside P11's SC chunking: multiple N×32 metric planes and copies
coexist before SC. Preserve the empty output-root history and do not repair or
rerun P12. Next: a Tier-X injected metric-lifetime probe, followed—only if it
finds an exact solution—by a fresh P12-R1 packet and new authorization.
