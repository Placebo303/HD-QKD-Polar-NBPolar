I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION` exactly as frozen in its
`TASK_PACKET.md` (§§3-6, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor helpers;
a new thin plus1024-confirmation runner (three hardcoded arms `B0_sc_base` /
`B1_L2plus` carried-over +1024 order-prefix step / `B2_true_l1_diagnostic`) plus
focused injected tests under a fresh additive `workspace/p20e/<uuid>/` temp root; the
P20E OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20e/spec.md`
plus the `tasks.md` P20E section; `P20E_FREEZE.md` + `P20E_IMPLEMENTATION_NOTES.md`.

This authorization explicitly permits NO protected TRAIN/HOLD/VAL/EVAL/raw-data read
(not even stat), NO real-data decoder execution, NO Stage-B output root, NO disclosure
or construction change of any kind, NO closed-block / consumed-VAL-pool / consumed-P20C-
block tuning or peeking, NO efficiency tuning, NO SCL/new kernel/model/schema, NO
overwrite under `results/` or `comparison_bench/outputs_comparison/`, and NO commit or
push.

Stage-B execution is NOT authorized by this text. It requires, in order: Stage-A return,
`P20E_FREEZE.md`, an independent Pre-EXECUTE review (PASS), a separate pasted Stage-B
authorization naming the exact frozen command, and target-output absence. Stop at the
packet return contract or first concrete blocker.
