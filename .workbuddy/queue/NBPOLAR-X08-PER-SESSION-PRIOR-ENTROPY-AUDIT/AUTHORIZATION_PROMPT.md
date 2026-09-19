# X08 authorization basis (main thread -> operator)
Basis: user briefing 2026-09-19 proposing the zero-cost S0 check: raw-MLE+floor
H1/H2 from the already-produced P20H calibrated_prior.npz counts_ab; no new
protected counts read (counts budget 0/0 untouched).

Authorized: create the X08 packet docs; create the probe root (must be absent);
ONE read-only content open of the digest-pinned worktree file above;
decoder-free NumPy computation of the two entropy variants; write prereg.md,
body.py, results.json under the probe root only.

Not authorized: protected/raw-data opens, sibling-checkout artifact opens,
decoder/RNG/tag calls, calibration refit, any lambda beyond the control and 0,
edits to accepted modules, writes outside the two roots, commit/push, claims
or pass/fail verdicts.
