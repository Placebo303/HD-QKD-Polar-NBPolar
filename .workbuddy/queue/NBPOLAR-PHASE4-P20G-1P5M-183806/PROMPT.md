Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/TASK_PACKET.md`
(P20G frozen +1024 independent-session confirmation on type2_1p5M_20260121_183806, Tier-Y planning-frozen).

Stage A only: start with a read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic); add the thin
independent-session runner reusing P18 loading/block formation and P16 operational
helpers unchanged, with three hardcoded arms carried over identical from P20C/P20E/P20F
(`B0_sc_base` / `B1_L2plus` with the SAME +1024 L2 order-prefix-extension step /
`B2_true_l1_diagnostic` oracle); freeze the exact NEW-session population (FIRST 384
TRAIN frames of the 1.5M file → 3 blocks at N=32768, all remaining 1.5M TRAIN frames
never used — confirm exact integers or replace with a written equivalent + justification;
JSON-manifest provenance reads only: split manifest + build manifest + P16 construction
file; CROSS-FILE source-tag+digest gate against the full 1M pool and the reserved 2M file
first, then INTRA-FILE DEV-vs-VAL/HOLD overlap gate), the carried-over per-arm numeric
disclosure caps (34119 / 39239 / 32524 key bits + 327743 public with ratios-vs-raw),
the exact Stage-B command (new P20G tag master 2026092210, `--source 1p5M` vocabulary
frozen at Stage A, 15-SC / 9-tag budget, 600-s / 2-GiB / single-thread envelope),
SC/tag budgets and wall/RSS ceilings; keep Model-F prior / `1e-15` floor / P16 order
(K1=319, K2 base 6492 / B1 7516) / kernel / representation / SC identical across arms
with ZERO tuning and record the cross-session prior use as a to-be-verified assumption
for Pre-EXECUTE; add focused injected tests (fresh additive `workspace/p20g/<uuid>/`
temp root, `pytest -p no:cacheprovider`); write the Stage-A freeze + implementation notes.

Hard limits: zero protected TRAIN/HOLD/VAL/EVAL/raw reads (not even stat — this includes
the 1.5M and 2M pairs files), zero decoder execution on real data, zero Stage-B output
root, no K/floor/order/decoder/step/success-point selection on the closed three blocks,
the consumed 1M pool (any split, any subrange), or the reserved 2M file, no per-session
prior refit, no second disclosure step (`B1b`), no alternative-construction second factor,
no efficiency tuning, no new-block peeking, no SCL/new kernel/model/schema, no overwrite
under `results/` or `comparison_bench/outputs_comparison/`, no commit/push, no self-acceptance.

Report acceptance IDs P20G-R1..R8 (stage-appropriately), changed files, exact test
commands/results, frozen population/cap/command, and protected-open audit (must be
zero). Stop on requirement ambiguity or the first concrete blocker with command, exact
error/traceback, attempted remedies, and the ONE decision needed from the main thread.
Stage B is never executed from this prompt — it needs an independent Pre-EXECUTE review
plus a separate pasted Stage-B authorization.
