# Tasks: Phase 6 fixed incremental disclosure

- [ ] P6-01 freeze nested sets for K=29,33,37,41,45 and prove strict nesting.
- [ ] P6-02 implement incremental-only disclosure and restart-from-scratch SC.
- [ ] P6-03 implement tag mismatch to fixed-next-level control with no candidate selection.
- [ ] P6-04 count each coordinate once and every verification/control invocation.
- [ ] P6-05 preserve disjoint exact/undetected/verify-failed/decode-failed/resource-abort outcomes.
- [ ] P6-06 add independent transcript, union-bound and paired-arm recounts.
- [ ] P6-07 pass tiny, tamper, nesting, restart and no-tag-selection tests.
- [ ] P6-08 obtain independent Pre-EXECUTE PASS on one paired 300-block run.
- [ ] P6-09 execute at most one fresh paired development attempt.
- [ ] P6-10 obtain independent Pre-RESULT review and return candidate or blocker.

Evidence pointer: `OPERATOR_RETURN.md` (result `BLOCKED(incremental_exact_ge_285)`;
no task boxes checked) and output root
`.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate/`.
