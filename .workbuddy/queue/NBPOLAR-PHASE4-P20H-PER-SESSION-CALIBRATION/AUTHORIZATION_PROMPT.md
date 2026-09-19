I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION` exactly as frozen in its
`TASK_PACKET.md` (§§3-6, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor helpers;
freezing + executing the §3 per-session calibration program ONCE (accepted P0/P2
Model-F concentration formula/smoothing/flow, input = 1.5M TRAIN counts ONLY via
`--source 1p5M`, output = digest-pinned `calibrated_prior.npz` + recalibrated
H1/H2/TOTAL literals, DEV-zero-contact) into `per_session_calibration/`; a new thin
per-session confirmation runner (three hardcoded arms `B0_sc_base` / `B1_L2plus`
carried-over +1024 order-prefix step / `B2_true_l1_diagnostic`, loading the frozen
prior read-only behind a calibration-identity digest gate, with cross-file
source-tag+digest, intra-file DEV-vs-VAL/HOLD, and calibration-identity fail-closed
gates) plus focused injected tests under a fresh additive `workspace/p20h/<uuid>/`
temp root; the P20H OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20h/spec.md`
plus the `tasks.md` P20H section; the Stage-A freeze + implementation notes.

This authorization explicitly permits exactly ONE protected content open: the 1.5M
TRAIN counts-calibration open in Stage A (declared and digest-recorded). It permits
NO 1.5M DEV/VAL/HOLD content open or stat (DEV opens stay 0), NO 1M-pool or reserved-2M
open/stat/listing/read in any form (2M stays pristine by non-access), NO real-data
decoder execution, NO Stage-B output root, NO disclosure/construction/calibration
change beyond the frozen §3 program, NO calibration on DEV and NO refit after any DEV
contact, NO closed-block / consumed-1M-pool / reserved-2M tuning or peeking, NO
efficiency tuning, NO SCL/new kernel/model/schema, NO overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and NO commit or push.

Stage-B execution is NOT authorized by this text. It requires, in order: Stage-A return
(including the calibration product + freeze), an independent Pre-EXECUTE review (PASS,
explicitly adjudicating the §3 calibration-vs-tuning gate (i)–(iv)), a separate pasted
Stage-B authorization naming the exact frozen command + frozen calibration digest, and
target-output absence. Stop at the packet return contract or first concrete blocker.
