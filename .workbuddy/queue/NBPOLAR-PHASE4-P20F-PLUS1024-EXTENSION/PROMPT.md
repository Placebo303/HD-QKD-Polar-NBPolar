Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/TASK_PACKET.md`
(P20F +1024 extension confirmation on the last same-file TRAIN tranche, Tier-Y planning-frozen).

Stage A only: start with a read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic); add the thin
plus1024-extension runner reusing P18 loading/block formation and P16 operational
helpers unchanged, with three hardcoded arms carried over identical from P20C/P20E
(`B0_sc_base` / `B1_L2plus` with the SAME +1024 L2 order-prefix-extension step /
`B2_true_l1_diagnostic` oracle); freeze the exact NEW-block population (same-file TRAIN
pool blocks 768..895 / 896..1023 / 1024..1151 at N=32768, remainder 1152..1199 never used —
confirm or replace with a written equivalent; JSON-manifest provenance reads only,
QUADRUPLE overlap pre-check against P20C-consumed 0..383 AND P20E-consumed 384..767 AND
consumed VAL 1200..1599 AND closed 1600..1983), the carried-over per-arm numeric disclosure caps (34119 / 39239 /
32524 key bits + 327743 public with ratios-vs-raw), the exact Stage-B command (new P20F
tag master 2026092200, 15-SC / 9-tag budget, 600-s / 2-GiB / single-thread envelope),
SC/tag budgets and wall/RSS ceilings; keep prior / `1e-15` floor / P16 order (K1=319,
K2 base 6492 / B1 7516) / kernel / representation / SC identical across arms with ZERO
tuning; add focused injected tests (fresh additive `workspace/p20f/<uuid>/` temp root,
`pytest -p no:cacheprovider`); write `P20F_FREEZE.md` + `P20F_IMPLEMENTATION_NOTES.md`.

Hard limits: zero protected TRAIN/HOLD/VAL/EVAL/raw reads (not even stat), zero decoder
execution on real data, zero Stage-B output root, no K/floor/order/decoder/step/
success-point selection on the closed three blocks, the consumed VAL pool (including
remainder 1584..1599), or the consumed P20C DEV blocks 0..383 / P20E DEV blocks 384..767,
no second disclosure step (`B1b`), no alternative-construction second factor, no efficiency
tuning, no new-block peeking, no SCL/new kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, no commit/push, no self-acceptance.

Report acceptance IDs P20F-R1..R8 (stage-appropriately), changed files, exact test
commands/results, frozen population/cap/command, and protected-open audit (must be
zero). Stop on requirement ambiguity or the first concrete blocker with command, exact
error/traceback, attempted remedies, and the ONE decision needed from the main thread.
Stage B is never executed from this prompt — it needs an independent Pre-EXECUTE review
plus a separate pasted Stage-B authorization.
