I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M` exactly as frozen in its
`TASK_PACKET.md` (§§2-6, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor helpers;
freezing the §3 prior-reuse pins (P20H `calibrated_prior.npz` canonical digest
`e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b` + lambda/floor/
literal pins, verified by a worktree-file digest recomputation ONLY); a new thin
L1-disclosure runner (three hardcoded arms `C0_sc_base` / `C1_L1plus` with the frozen +128
L1 order-prefix step / `C2_true_l1_diagnostic`, loading the frozen prior read-only behind
a calibration-identity digest gate, with cross-file source-tag+digest, intra-file
DEV-vs-VAL/HOLD, P20H-DEV-exclusion, and calibration-identity fail-closed gates) plus
focused injected tests under a fresh additive `workspace/p20i/<uuid>/` temp root; the P20I
OpenSpec delta at `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20i/spec.md`
plus the `tasks.md` P20I section; the Stage-A freeze (`P20I_FREEZE.md`) + implementation notes.

This authorization explicitly permits ZERO protected content opens: NO counts-NPZ open
(counts stay 0/0; the digest check is a worktree-file read), NO 1.5M DEV/VAL/HOLD content
open or stat (DEV stays 0/1, HOLD stays 0/1), NO 1M-pool or reserved-2M open/stat/listing/read
in any form (2M stays pristine by non-access), NO real-data decoder execution, NO Stage-B
output root, NO disclosure/construction/prior change beyond the frozen §§2-3/§§5-6 pins,
NO prior refit/resmoothing/relambda and NO calibration on DEV, NO closed-block /
consumed-1M-pool / P20H-DEV / reserved-2M tuning or peeking, NO second L1 tier or L2 step,
NO efficiency tuning, NO SCL/new kernel/model/schema, NO overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and NO commit or push.

Stage-B execution is NOT authorized by this text. It requires, in order: Stage-A return
(including the freeze + implementation notes), an independent Pre-EXECUTE review (PASS,
explicitly adjudicating the §3 reuse pins and the §4 quadruple gate), a separate pasted
Stage-B authorization naming the exact frozen command + frozen prior digest, and
target-output absence. Stop at the packet return contract or first concrete blocker.
