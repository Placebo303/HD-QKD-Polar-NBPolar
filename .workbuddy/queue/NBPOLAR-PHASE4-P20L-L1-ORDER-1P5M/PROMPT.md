Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M/TASK_PACKET.md`
(P20L L1-order same-budget single-factor on type2_1p5M_20260121_183806, Tier-Y planning-frozen).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic) plus the accepted P13/P16
L1-genie procedure callsites (`construction.py` L1 path as called) with L1-only /
K-frozen / L2-frozen evidence; (2) freeze the §3 prior-reuse pins (P20H
`calibrated_prior.npz` canonical digest
`e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b` + lambda
137.3823795883264 + floor 1e-15 + recalibrated H1/H2/TOTAL literals, verified by a
worktree-file digest recomputation ONLY — zero NPZ/parquet content opens); (3) add the thin
L1-order runner reusing P18 loading/block formation and P16/P13 L1-genie helpers
unchanged, three hardcoded arms carried over per §§5-6 (`F0_old_order_base` P16 orders
K1=319/K2=6492 / `F1_new_l1_order_base` with the FROZEN same-budget L1-order swap —
new 1.5M L1 order first-319 prefix, P16 L2 order frozen, K1/K2 unchanged, keyΔ 0 /
`F2_true_l1_diagnostic` oracle at base) loading the §3 frozen prior read-only behind a
calibration-identity digest gate with Stage-A synthetic-only order derivation
(P20L-R1delta: 16 L1-only TRAIN genie calls in Stage A under the
zero-protected-read premise, product is the frozen order file
`new_l1_order_1p5m.json` per §9 with digest pinned in the freeze plus
old-order对照, Stage-B read-only `--order-file` + `--order-digest` gated use
with zero sampling);
freeze the exact order-derivation TRAIN seeds (expected `2026092271..2026092274`, 16
synthetic L1-only blocks model-sampled from the frozen prior — confirm exact integers
or replace with a written equivalent + justification), the population (FIRST 384 VAL
frames of the 1.5M file → 3 blocks at N=32768, VAL remainder never used — confirm exact
integers `1660..2043` / `1660..1787/1788..1915/1916..2043` / `2044..2212` or replace
with a written equivalent + justification; JSON-manifest provenance reads only for the
population part; SEPTUPLE gate: CROSS-FILE source-tag+digest first, then INTRA-FILE
VAL-containment + VAL-exterior/HOLD (VAL first), then P20H/P20I/P20J/P20K-TRAIN-DEV +
remainder exclusions, then CALIBRATION-IDENTITY + ORDER-FREEZE), the preregistered
per-arm disclosure caps (34119 / 34119 / 32524 key bits + 327743 public, keyΔ F1-vs-F0
exactly 0, ratios-vs-raw ~10.41%), the exact Stage-B command (new P20L tag master
2026092260, `--source 1p5M` vocabulary frozen at Stage A, frozen
`--order-file` + `--order-digest` with NO `--train-seeds` and zero Stage-B
sampling, pure 15-SC / 9-tag DEV budget, 600-s / 2-GiB / single-thread envelope), SC/tag/genie budgets and wall/RSS
ceilings; record the §3 reuse + §4 gate + §2 order-freeze evidence for Pre-EXECUTE;
(4) add focused injected tests (fresh additive `workspace/p20l/<uuid>/` temp root,
`pytest -p no:cacheprovider`); (5) run the Stage-A synthetic-only order
derivation producing the frozen order file `new_l1_order_1p5m.json` (§9
identity) and write the Stage-A freeze (`P20L_FREEZE.md`, including the
order-file sha256 digest + old-order对照) + implementation notes; (6) stage the P20L OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20l/spec.md` plus
the `tasks.md` P20L section carrying the P20L-R1delta semantics (no seed literals in tracked files; tag master 2026092260,
test seeds 2026092261..2026092267, and TRAIN seeds verified absent elsewhere by repo
grep).

Hard limits: ZERO protected content opens or stats in Stage A (counts 0 + DEV 0 + HOLD 0
at close; the §3 digest check is a worktree-file read, never a counts open; TRAIN seeds
are integers; synthetic order derivation happens ONLY in Stage A under the
zero-protected-read premise — worktree prior file + seed integers only, zero
DEV contact — and Stage B performs ZERO sampling of any kind); zero 1M-pool or reserved-2M
open/stat/listing/read in any form (2M pristine by non-access); zero real-data decoder
execution; zero Stage-B output root; no K/floor/order/decoder/step/success-point
selection on closed blocks, the consumed 1M pool, any consumed 1.5M TRAIN DEV
(0..1535), TRAIN remainder 1536..1659, VAL remainder 2044..2212, HOLD, or 2M; no prior
refit/resmoothing/relambda/λ change, no K reselection, no L2-order change, no
derivation on real frames, no disclosure-tier change, no alternative-construction or
bounded-search second factor, no efficiency tuning, no new-block peeking, no SCL/new
kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, no commit/push, no self-acceptance.

Report acceptance IDs P20L-R1..R8 (stage-appropriately), changed files, exact test
commands/results, frozen prior digest + program pin + TRAIN seeds + order-file
digest + population/cap/command, and the split open audit (counts + DEV + HOLD separately, must be 0 + 0 + 0
at Stage-A close). Stop on requirement ambiguity or the first concrete blocker with
command, exact error/traceback, attempted remedies, and the ONE decision needed from
the main thread. Stage B is never executed from this prompt — it needs an independent
Pre-EXECUTE review (including the §3 reuse + §4 septuple gate + §2 order-freeze design)
plus a separate pasted Stage-B authorization.
