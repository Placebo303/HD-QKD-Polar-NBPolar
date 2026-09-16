# Main-thread disposition — Phase 6 fixed incremental

Disposition: `FIXED_INCREMENTAL_NEGATIVE_ACCEPTED`.

The reviewed one-shot paired result is accepted as a valid synthetic negative
result for the frozen strict-stop scheduler. Incremental exact recovery was
271/300, below 285, with Wilson lower bound 0.8715597837542944 below 0.90.
Static K45 was 298/300. Incremental disclosure fell 28.17%, but that does not
override the recovery gates.

All 29 incremental failures were level-0 `ImpossibleDisclosedValueError` before
verification. This is accepted as a scheduler-mechanism result, not an SC
implementation defect. Attempt 1/1 and run seed 2026091340 are consumed; public
Toeplitz master 2026091341 and the five-file evidence root are immutable.

Successor ruling: choose option (a). At non-final levels only, an
`ImpossibleDisclosedValueError` becomes `decode_rejected_continue`: the current
candidate is absent/rejected, one public feedback request is counted, the next
increment is disclosed, and SC restarts from scratch. It is never success and
invokes no tag. The same error at final K45 remains terminal `decode_failed`.
This ruling changes no K, construction, threshold, SC logic or old evidence.
