I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20G-1P5M-183806` exactly as frozen in its
`TASK_PACKET.md` (§§3-6, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor helpers;
a new thin independent-session runner (three hardcoded arms `B0_sc_base` /
`B1_L2plus` carried-over +1024 order-prefix step / `B2_true_l1_diagnostic`, with
cross-file source-tag+digest and intra-file DEV-vs-VAL/HOLD fail-closed gates) plus
focused injected tests under a fresh additive `workspace/p20g/<uuid>/` temp root; the
P20G OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20g/spec.md`
plus the `tasks.md` P20G section; the Stage-A freeze + implementation notes.

This authorization explicitly permits NO protected TRAIN/HOLD/VAL/EVAL/raw-data read
(not even stat — including the 1.5M DEV file and the reserved 2M file), NO real-data
decoder execution, NO Stage-B output root, NO disclosure or construction change of any
kind, NO per-session prior refit, NO closed-block / consumed-1M-pool / reserved-2M
tuning or peeking, NO efficiency tuning, NO SCL/new kernel/model/schema, NO
overwrite under `results/` or `comparison_bench/outputs_comparison/`, and NO commit or
push.

Stage-B execution is NOT authorized by this text. It requires, in order: Stage-A return,
the Stage-A freeze, an independent Pre-EXECUTE review (PASS), a separate pasted Stage-B
authorization naming the exact frozen command, and target-output absence. Stop at the
packet return contract or first concrete blocker.
