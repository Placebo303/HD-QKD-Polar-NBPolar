# Heavy task packet — Phase 6-R1 decode-reject advancement

## Mission and frozen delta

Test whether advancing after a non-final impossible-disclosure rejection
recovers the strict-stop losses while retaining disclosure savings. Keep the
accepted Phase 6 point, order, K=(29,33,37,41,45), decoder, tags, thresholds and
accounting. Change only:

- K<45 `ImpossibleDisclosedValueError` -> `decode_rejected_continue`;
- no candidate/tag at that level; count one feedback request;
- disclose the next fixed increment and restart SC from original metrics;
- K45 same error -> terminal `decode_failed`.

No other exception may continue. Intermediate rejection is never success.

## Allowed scope

Modify Phase 6 `incremental.py` and its adapter only for this delta; add
`tests/test_nbpolar_incremental_r1.py`; update this R1 OpenSpec/queue and
required lifecycle docs. Old Phase 5/P6 evidence roots are immutable.

## Acceptance IDs

- R1-A01 only non-final impossible-disclosure continues.
- R1-A02 rejected levels create no candidate/tag.
- R1-A03 exactly one feedback and next increment occur.
- R1-A04 SC restarts from original metrics with no state.
- R1-A05 final K45/other exceptions remain terminal.
- R1-A06 coordinate/tag/seed/feedback counts recount exactly.
- R1-A07 final buckets remain disjoint/exhaustive.
- R1-A08 three arms consume identical blocks.
- R1-A09 rescued/persisted/regressed identities are reported.
- R1-A10 Phase 5/strict-stop behavior remains pinned.
- R1-A11 truth leak/nonfinite/undetected handling is unchanged.
- R1-A12 focused and predecessor tests pass.

## Qualification and execution

Force injected rescue at every next level, persistent failure through K45,
other exceptions, tag mismatch and false match. Prove fresh SC state and
independently recount transcripts. Do not tune scientific parameters.

Freeze new run/public-master seeds, arm/block/level derivation, exact paired
matrix/command, absent output root, attempt point, budgets, five scalar-only
artifacts and gates. Obtain independent Pre-EXECUTE PASS.

Execute static K45, strict-stop and R1 arms on the same 300 new blocks. Consume
attempt 1/1 at first SC call; no rerun. R1 requires exact>=285, Wilson LB>=0.90,
undetected=0 and >=5% lower average key-dependent bits than static, plus all
coverage/accounting/truth/nonfinite/resource gates. Report rescue/regression
against strict-stop without adding a pass threshold.

Independent Pre-RESULT must recompute all arms, pairing, Wilson, disclosure,
invocations, union bound, continuation taxonomy and recount. Return only
`DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE` or the earliest `BLOCKED(...)`.
No artifacts/real data/SCL/Phase7/qualification/promotion/commit/push.
