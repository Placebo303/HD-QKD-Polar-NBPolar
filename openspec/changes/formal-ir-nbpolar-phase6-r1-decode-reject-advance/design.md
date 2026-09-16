# Design: Phase 6-R1 decode-reject advancement

At K=29/33/37/41, `ImpossibleDisclosedValueError` records
`decode_rejected_continue`, creates and verifies no candidate, counts one
public feedback request, discloses the next fixed increment and restarts SC
from original metrics. Other exceptions remain fail-closed. At K45 every
decode exception is terminal `decode_failed`.

Intermediate rejection is not a final outcome. Disclosed coordinates remain
cumulative and counted once; no tag bits accrue at a decode-rejected level.

One fresh 300-block run pairs three arms on identical blocks: static K45, the
accepted strict-stop scheduler, and decode-reject-advance. Old evidence is not
read or overwritten.

Rev 1 (2026-09-13), frozen operator conventions recorded in
`.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/R1_FREEZE.md`:
non-final rejected levels record `rejected_levels` and advance with exactly
one public feedback request; no candidate and no tag event exist at a rejected
level; both incremental arms share the `incremental` seed namespace so a
non-rejecting block is bit-identical to strict-stop; per-block invariant
`levels_invoked = tag_invocations + rejections` (+1 for a terminal
`decode_failed` level) and `feedback_control_invocations = levels_invoked -
1`; R1 seeds are run 2026091350 / Toeplitz master 2026091351 with the
separate `validate_r1_run_seed` refusing the Phase 1-6 consumed set plus
2026091321/2026091340/2026091341 while the Phase 6 validator stays pinned; the
only write target is the absent R1 output root. No task box is checked;
implementation awaits an independent Pre-EXECUTE PASS.
