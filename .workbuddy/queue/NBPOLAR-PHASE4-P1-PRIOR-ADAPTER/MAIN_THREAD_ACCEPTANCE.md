# Main-thread acceptance — Phase 4-P1

Disposition: `IMPLEMENTATION_ACCEPTED_SYNTHETIC_ONLY`.

The pure dense prior adapter and synthetic qualification V-P0-01 through
V-P0-07 are accepted after independent reviewer-go ACCEPT. Frozen evidence is
the 66/66 Phase 1-4-P1 focused regression plus the independent 11/11
decoder-free prior review. The historical first `BLOCKED` return remains
preserved; option (a) resolved its contradictory sentinel without changing
Phase 1-3 algorithm logic.

Acceptance covers formulas, axes, dual fallbacks, 5+5 packing, probability/log
conversion, exact-zero support, explicit opt-in floor API, provenance, and
batch/position equivariance on synthetic fixtures. It does not validate CAL
data, Model-F fit, decoder behavior with empirical priors, DEV/EVAL performance,
FER, leakage, key rate, qualification, or promotion.

Phase 4-P2 remains all-false and requires separate explicit authorization.
