Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/TASK_PACKET.md`
(P20M raw-prior + session-budget operating-point swap on type2_1p5M_20260121_183806, Tier-Y planning-frozen).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic) plus the accepted P13/P16
budget/split machinery callsites (`target_n_scaling.budget_k_total`,
`empirical_genie_scaling.select_empirical_split`, `target_n_scaling.allocate_layer_ks`
as same-family reference only) and the accepted `l1_order_1p5m` import target with the
§2 delta list (d1–d7) evidenced; (2) derive the §3 corrected prior (read `counts_ab`
from the digest-reverified P20H worktree npz ONLY — worktree-file read, never a
protected counts open; raw-count MLE + 1e-15 floor + column renormalize, no lambda
anywhere, `derive_p1`/`derive_p2` under A=32*U1+U2 FULL_BOB_ONLY, `p_b` cross-check
against column totals/total) and write the frozen artifact `raw_prior_1p5m.npz`
(exact 10-key set, `lambda_star` 0.0) with its canonical digest + session H1/H2/TOTAL
literals + floor-hit count/rate pinned for the freeze; (3) add the thin raw-prior
runner importing accepted `l1_order_1p5m` read-only with ONLY the §2 d1–d7 delta,
three hardcoded arms per §§5-6 (`G0_old_point_base` λ-prior/P16-order control at
319/6492 / `G1_raw_prior_session_budget` corrected-prior + derived (K1,K2) + derived
worst-first orders / `G2_true_l1_diagnostic` oracle at candidate K2), loading the §3
frozen artifact read-only behind the `corrected_prior_identity` gate; freeze the
session-derived point (K_total via the literal f=1.3 recomputation displayed from the
same-run session H — S2-i; (K1,K2) via `select_empirical_split` semantics on 16
synthetic TRAIN blocks model-sampled from the corrected prior under the frozen
derivation seeds, never a real frame, never DEV; worst-first L1+L2 orders into the
frozen order file `raw_prior_orders_1p5m.json` with digest pinned plus Stage-B
read-only `--order-file` + `--order-digest` gated use with zero sampling);
freeze the population (FIRST 384 VAL frames of the 1.5M file → 3 blocks at N=32768 —
confirm exact integers `1660..2043` / `1660..1787/1788..1915/1916..2043` /
`2044..2212` or replace with a written equivalent + justification; JSON-manifest
provenance reads only for the population part; §4 gate family (a)→(g): CROSS-FILE
source-tag+digest first, then INTRA-FILE VAL-containment + VAL-exterior/HOLD (VAL
first), then P20H/P20I/P20J/P20K-TRAIN-DEV + remainder exclusions incl. the
DEV∩build-frames disjointness declaration with frame sets — S2-ii, then
CORRECTED-PRIOR-IDENTITY + ORDER-FREEZE + BUDGET-LITERAL), the preregistered
per-arm caps from the derived integers (G0 34119 + 327743 public; G1/G2 via the
5K+64 rule frozen at Stage A), the exact Stage-B command (new P20M tag master
2026092280, `--source 1p5M` vocabulary frozen at Stage A, frozen `--k1/--k2` +
`--order-file` + `--order-digest` with zero Stage-B sampling, pure 15-SC / 9-tag
DEV budget, 600-s / 2-GiB / single-thread envelope), SC/tag/genie budgets and
wall/RSS ceilings, and the per-arm floor-hit reporting (S2); record the §3
derivation + §5 budget-literal + §4 gate + §2 runner-delta evidence for
Pre-EXECUTE; (4) add focused injected tests (fresh additive
`workspace/p20m/<uuid>/` temp root, `pytest -p no:cacheprovider`); (5) run the
Stage-A derivation producing the frozen `raw_prior_1p5m.npz` +
`raw_prior_orders_1p5m.json` (§§3/9 identity) and write the Stage-A freeze
(`P20M_FREEZE.md`, including both product digests + H literals + K integers +
budget-literal display + `p_b` cross-check + floor-hit rate) + implementation
notes; (6) stage the P20M OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20m/spec.md` plus
the `tasks.md` P20M section (no seed literals in tracked files; tag master 2026092280,
test seeds 2026092281..2026092287, and derivation seeds 2026092291..2026092294
verified absent elsewhere by repo grep).

Hard limits: ZERO protected content opens or stats in Stage A (counts 0 + DEV 0 + HOLD 0
at close; the worktree-npz reads are worktree-file reads, never counts opens; derivation
seeds are integers; synthetic derivation happens ONLY in Stage A — corrected-prior
arrays + seed integers only, zero DEV contact — and Stage B performs ZERO sampling of
any kind); zero 1M-pool or reserved-2M open/stat/listing/read in any form (2M pristine
by non-access); zero real-data decoder execution; zero Stage-B output root; no lambda
anywhere; no K carried as an absolute from another session (S2-i); no K/floor/order/
decoder/step/success-point selection on closed blocks, the consumed 1M pool, any
consumed 1.5M TRAIN DEV (0..1535), TRAIN remainder 1536..1659, VAL remainder 2044..2212,
HOLD, or 2M; no derivation on real frames; no second factor (disclosure tier, order
swap on real data, alternative construction, bounded search); no efficiency tuning; no
new-block peeking; no SCL/new kernel/model/schema; no overwrite under `results/` or
`comparison_bench/outputs_comparison/`; no commit/push; no self-acceptance.

Report acceptance IDs P20M-R1..R8 (stage-appropriately), changed files, exact test
commands/results, frozen prior digest + H literals + K integers + budget-literal display
+ order-file digest + population/cap/command, and the split open audit (counts + DEV +
HOLD separately, must be 0 + 0 + 0 at Stage-A close) plus the honest-scope statement
(§0) verbatim. Stop on requirement ambiguity or the first concrete blocker with
command, exact error/traceback, attempted remedies, and the ONE decision needed from
the main thread. Stage B is never executed from this prompt — it needs an independent
Pre-EXECUTE review (including the §3 derivation + §5 budget literal + §4 gate family +
§2 runner-delta design) plus a separate pasted Stage-B authorization.
