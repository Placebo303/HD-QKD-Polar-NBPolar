I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC` exactly as frozen in its
`TASK_PACKET.md` (§§3-6, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor helpers;
a new thin bounded-search diagnostic runner plus focused injected tests under a fresh
additive `workspace/p20b/<uuid>/` temp root; the P20B OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20b/spec.md` plus the
`tasks.md` P20B section; `P20B_FREEZE.md` + `P20B_IMPLEMENTATION_NOTES.md`.

This authorization explicitly permits NO protected TRAIN/HOLD/VAL/EVAL/raw-data read
(not even stat), NO real-data decoder execution, NO Stage-B output root, NO disclosure or
construction change, NO closed-block tuning, NO SCL/new kernel/model/schema, NO overwrite
under `results/` or `comparison_bench/outputs_comparison/`, and NO commit or push.

Stage-B execution is NOT authorized by this text. It requires, in order: Stage-A return,
`P20B_FREEZE.md`, an independent Pre-EXECUTE review (PASS), a separate pasted Stage-B
authorization naming the exact frozen command, and target-output absence. Stop at the
packet return contract or first concrete blocker.
