Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/TASK_PACKET.md`
(P20J L1-dose-escalation +256 single-factor on type2_1p5M_20260121_183806, Tier-Y planning-frozen).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic); (2) freeze the §3 prior-reuse
pins (P20H `calibrated_prior.npz` canonical digest
`e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b` + lambda
137.3823795883264 + floor 1e-15 + recalibrated H1/H2/TOTAL literals, verified by a
worktree-file digest recomputation ONLY — zero NPZ/parquet content opens); (3) add the thin
L1-dose-escalation runner reusing P18 loading/block formation and P16 operational helpers
unchanged, three hardcoded arms carried over per §§5-6 (`D0_sc_base` base K1=319/K2=6492 /
`D1_L1plus` with the FROZEN +256 L1 order-prefix-extension step K1=575/K2=6492 /
`D2_true_l1_diagnostic` oracle at base) loading the §3 frozen prior read-only behind a
calibration-identity digest gate; freeze the exact population (NEXT 384 TRAIN frames of the
1.5M file → 3 blocks at N=32768, remainder never used — confirm exact integers
`768..1151` / `768..895/896..1023/1024..1151` / `1152..1659` or replace with a written equivalent
+ justification; JSON-manifest provenance reads only for the population part;
QUINTUPLE gate: CROSS-FILE source-tag+digest first, then INTRA-FILE DEV-vs-VAL/HOLD
(VAL first), then P20H-DEV 0..383 exclusion, then P20I-DEV 384..767 exclusion, then
CALIBRATION-IDENTITY), the preregistered per-arm disclosure caps (34119 / 35399 / 32524 key bits + 327743 public, keyΔ 1280 = 5·256,
ratios-vs-raw ~10.41%/~10.80%), the exact Stage-B command (new P20J tag master 2026092240,
`--source 1p5M` vocabulary frozen at Stage A, 15-SC / 9-tag budget, 600-s / 2-GiB /
single-thread envelope), SC/tag budgets and wall/RSS ceilings; record the §3 reuse + §4
gate evidence for Pre-EXECUTE; (4) add focused injected tests (fresh additive
`workspace/p20j/<uuid>/` temp root, `pytest -p no:cacheprovider`); (5) write the Stage-A
freeze (`P20J_FREEZE.md`) + implementation notes; (6) stage the P20J OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20j/spec.md` plus
the `tasks.md` P20J section (no seed literals in tracked files; tag master 2026092240
and test seeds 2026092241..2026092247 verified absent elsewhere by repo grep).

Hard limits: ZERO protected content opens or stats in Stage A (counts 0 + DEV 0 + HOLD 0
at close; the §3 digest check is a worktree-file read, never a counts open); zero 1M-pool
or reserved-2M open/stat/listing/read in any form (2M pristine by non-access); zero
real-data decoder execution; zero Stage-B output root; no K/floor/order/decoder/step/
success-point selection on closed blocks, the consumed 1M pool, P20H DEV 0..383, P20I DEV
384..767, or 2M; no prior refit/resmoothing/relambda, no calibration on DEV, no NPZ loader inside the
Stage-B runner; no second L1 tier (`D1b`), no second L2 step, no alternative-construction
second factor, no efficiency tuning, no new-block peeking, no SCL/new kernel/model/schema,
no overwrite under `results/` or `comparison_bench/outputs_comparison/`, no commit/push,
no self-acceptance.

Report acceptance IDs P20J-R1..R8 (stage-appropriately), changed files, exact test
commands/results, frozen prior digest + population/cap/command, and the split open audit
(counts + DEV + HOLD separately, must be 0 + 0 + 0 at Stage-A close). Stop on requirement
ambiguity or the first concrete blocker with command, exact error/traceback, attempted
remedies, and the ONE decision needed from the main thread. Stage B is never executed
from this prompt — it needs an independent Pre-EXECUTE review (including the §3 reuse +
§4 quintuple gate) plus a separate pasted Stage-B authorization.
