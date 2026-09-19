I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF` exactly as frozen in its
`TASK_PACKET.md` (§§3-6, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor helpers;
a new thin L2-disclosure-backoff runner (three hardcoded arms `B0_sc_base` /
`B1_L2plus` +1024 order-prefix step / `B2_true_l1_diagnostic`) plus focused injected
tests under a fresh additive `workspace/p20c/<uuid>/` temp root; the P20C OpenSpec
delta at `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20c/spec.md`
plus the `tasks.md` P20C section; `P20C_FREEZE.md` + `P20C_IMPLEMENTATION_NOTES.md`.

This authorization explicitly permits NO protected TRAIN/HOLD/VAL/EVAL/raw-data read
(not even stat), NO real-data decoder execution, NO Stage-B output root, NO disclosure
step beyond the single frozen +1024, NO construction change, NO closed-block or
consumed-VAL-pool tuning, NO SCL/new kernel/model/schema, NO overwrite under `results/`
or `comparison_bench/outputs_comparison/`, and NO commit or push.

Stage-B execution is NOT authorized by this text. It requires, in order: Stage-A return,
`P20C_FREEZE.md`, an independent Pre-EXECUTE review (PASS), a separate pasted Stage-B
authorization naming the exact frozen command, and target-output absence. Stop at the
packet return contract or first concrete blocker.
