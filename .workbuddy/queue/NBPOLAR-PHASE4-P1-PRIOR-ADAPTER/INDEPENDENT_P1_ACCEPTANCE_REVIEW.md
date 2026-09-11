# Independent Phase 4-P1 acceptance review

Verdict supplied by reviewer-go: **ACCEPT**. The review was read-only and made
no file changes. This file persists the external independent verdict reported
by the user; the original reviewer transcript was not written into this
checkout.

The review accepted:

- `prior.py` against the Phase 4-P0 contract;
- the package export of three types and six pure functions;
- synthetic V-P0-01 through V-P0-07 with an independent test-local oracle;
- option (a), which keeps `.prior` forbidden in the two Phase 3 algorithm files
  while preserving common bans over all three original files;
- the 66-pass full focused regression and separately reviewed 11/11
  decoder-free prior evidence;
- absence of CAL, Model-F, SC, DEV/EVAL, data-driven floor, Phase 1-3 logic
  changes, output pollution, or P2 authorization.

Non-blocking nits are deferred to the next already-authorized code/doc edit:
clarify one `__all__` comment, refine the package docstring, and normalize the
troubleshooting heading level. They do not justify touching accepted code now.

This verdict grants no Phase 4-P2, CAL, Model-F, decoder, real-data, EVAL,
performance-claim, commit, or push authorization.
