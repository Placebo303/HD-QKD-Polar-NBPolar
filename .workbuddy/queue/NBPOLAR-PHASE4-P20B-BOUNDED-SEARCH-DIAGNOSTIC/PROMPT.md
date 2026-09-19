Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/TASK_PACKET.md`
(P20B bounded search diagnostic, Tier-Y planning-frozen).

Stage A only: start with a read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic); add the thin bounded-search
diagnostic runner reusing P18 loading/block formation and P16 operational helpers unchanged;
freeze ONE search bound M + ONE neighborhood definition + coherent single-model scoring with
no tag-guided selection and no evidence reuse; keep prior / `1e-15` floor / P16 construction
(K1=319/K2=6492) / base disclosure / kernel / representation / SC identical across arms;
add focused injected tests (fresh additive `workspace/p20b/<uuid>/` temp root,
`pytest -p no:cacheprovider`); write `P20B_FREEZE.md` (bound, population declaration with
digests excluding closed frames 1600..1983, numeric disclosure cap at frozen base, exact
Stage-B command, SC/tag budgets, wall/RSS ceilings) + `P20B_IMPLEMENTATION_NOTES.md`.

Hard limits: zero protected TRAIN/HOLD/VAL/EVAL/raw reads (not even stat), zero decoder
execution on real data, zero Stage-B output root, no K/floor/order/decoder/success-point
selection on the closed three blocks, no disclosure-backoff or alternative-construction
second factor, no SCL/new kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, no commit/push, no self-acceptance.

Report acceptance IDs P20B-R1..R8 (stage-appropriately), changed files, exact test
commands/results, frozen bound/population/cap/command, and protected-open audit (must be
zero). Stop on requirement ambiguity or the first concrete blocker with command, exact
error/traceback, attempted remedies, and the ONE decision needed from the main thread.
Stage B is never executed from this prompt — it needs an independent Pre-EXECUTE review
plus a separate pasted Stage-B authorization.
