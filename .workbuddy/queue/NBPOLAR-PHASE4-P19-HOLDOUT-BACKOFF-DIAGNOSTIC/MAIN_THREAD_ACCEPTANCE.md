# Main-thread acceptance — Phase 4-P19

Decision: accept
`TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE` as a complete
descriptive same-block layer/backoff diagnostic.

The authoritative evidence is the finalized worktree five-file root. A
concurrent external commit captured an 11/15 `RUNNING` checkpoint; that commit
is not the result and must never be restored over the worktree evidence.

All 20 integrity gates passed. The single run consumed both protected reads
and its one attempt without reopen, retry or tuning. Across base, +128 L1,
+512 L2, both increments and the isolated true-L1 control, all 15 records were
`verify_failed`, with zero undetected, nonfinite, truth-leak or resource
outcomes.

The +128 L1 arms made L1 correct on all three blocks, but neither those arms
nor the true-L1 control recovered a complete block. The registered +512 L2
increment also recovered none. This establishes only that hard-L1 propagation
is not a sufficient explanation for these three failures and that the tested
backoffs did not recover them.

It is not a HOLD FER estimate, a winner/superiority result, a global backoff
failure, qualification, promotion or a reason to reject NB-Polar. The three
blocks are closed diagnostic data and may not be used to tune a successor.

Next gate: implementation/accounting-only resource-exception and endpoint
instrumentation repair. No protected data read or decoder experiment is
authorized. After its independent acceptance, a separate L2 real-correction
feasibility design may be frozen on independent development data.

