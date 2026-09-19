Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF/TASK_PACKET.md`
(P20C L2 disclosure backoff, Tier-Y planning-frozen).

Stage A only: start with a read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic); add the thin L2-backoff
runner reusing P18 loading/block formation and P16 operational helpers unchanged, with
three hardcoded arms (`B0_sc_base` / `B1_L2plus` with the ONE preregistered +1024 L2
order-prefix-extension step / `B2_true_l1_diagnostic` oracle); freeze the exact DEV
population (recommended same-file TRAIN pool blocks 0..127 / 128..255 / 256..383 at
N=32768 — confirm or replace with a written equivalent; JSON-manifest provenance reads
only, overlap pre-check against BOTH closed 1600..1983 and consumed VAL 1200..1599),
the per-arm numeric disclosure caps (34119 / 39239 / 32524 key bits + 327743 public with
ratios-vs-raw), the exact Stage-B command (new P20C tag domains, 15-SC / 9-tag budget,
600-s / 2-GiB / single-thread envelope), SC/tag budgets and wall/RSS ceilings; keep
prior / `1e-15` floor / P16 order / kernel / representation / SC identical across arms;
add focused injected tests (fresh additive `workspace/p20c/<uuid>/` temp root,
`pytest -p no:cacheprovider`); write `P20C_FREEZE.md` + `P20C_IMPLEMENTATION_NOTES.md`.

Hard limits: zero protected TRAIN/HOLD/VAL/EVAL/raw reads (not even stat), zero decoder
execution on real data, zero Stage-B output root, no K/floor/order/decoder/step/
success-point selection on the closed three blocks or the consumed VAL pool (including
remainder 1584..1599), no second disclosure step (`B1b`), no alternative-construction
second factor, no SCL/new kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, no commit/push, no self-acceptance.

Report acceptance IDs P20C-R1..R8 (stage-appropriately), changed files, exact test
commands/results, frozen step/population/cap/command, and protected-open audit (must be
zero). Stop on requirement ambiguity or the first concrete blocker with command, exact
error/traceback, attempted remedies, and the ONE decision needed from the main thread.
Stage B is never executed from this prompt — it needs an independent Pre-EXECUTE review
plus a separate pasted Stage-B authorization.
