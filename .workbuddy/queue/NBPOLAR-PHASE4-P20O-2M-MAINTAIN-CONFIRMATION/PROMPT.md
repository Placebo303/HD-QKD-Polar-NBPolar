Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/TASK_PACKET.md`
(P20O maintain-confirmation of ALT-L2-LAPLACE-α1 at per-session disclosure on
type2_2M_20260121_183657 VAL, Tier-Y planning-frozen).

Stage A only, in order: (1) read-only callsite inventory of the §12
predecessor helpers (filenames listed in the packet — do not modify their
logic) plus the accepted `raw_prior_val_1p5m` import target with the §2 delta
list (d1–d8) evidenced and the P20M `_selected_diagnostics` code point
(`raw_prior_val_1p5m.py:1306-1334`) cited as the carried-over callsite pattern
for the §7 recorder; (2) perform the SINGLE authorized counts-calibration open
of the §3 2M TRAIN array (`--source 2M` array ONLY, counts 0/1→1/1; all other
arrays never opened; zero DEV contact) and derive the §3 2M raw prior (raw-count
MLE + 1e-15 floor + column renormalize, no lambda anywhere, `derive_p1`/`derive_p2`
under A=32*U1+U2 FULL_BOB_ONLY, `p_b` cross-check, canonical digest via
`per_session_calibration.canonical_prior_digest`, session H via `entropy_bits`)
writing `raw_prior_2m.npz` (exact 10-key set, `lambda_star` 0.0) with digest +
H literals + floor-hit rate pinned; model-sample 16 synthetic TRAIN blocks from
the 2M raw prior under frozen derivation seeds 2026092321..2026092324 → L1+L2
genie risks (32 calls, Stage A only) → pooled means → `select_empirical_split` →
freeze K_total via the literal f=1.3 recomputation (S2-i) + (K1,K2) + worst-first
orders into `raw_prior_orders_2m.json` (file-bytes digest pinned); derive the §3
2M alt-L2 table from the SAME counts (`f_alt[a,b]=(counts_ab[a,b]+1)/(n_b[b]+1024)`
frozen α=1, 1e-15 floor step retained + column renormalize, `derive_p2`,
`p1`-equality within 1e-12, descriptive alt-H never a budget input) writing
`alt_l2_tables_2m.npz` (exact 9-key set, `alpha` 1.0) with file-bytes digest +
floor-rate + `p1`-equality + alt-H pinned (closed-form alt step; zero DEV reads),
plus the D1 feasibility literals (`ce_alt`/`ce_incumbent` 2M-TRAIN-only estimator,
L2 ceiling `5*K2+64`, `alt_ideal_length_bits`) with the D2
`alt_construction_budget_feasibility` gate evaluated BEFORE any VAL contact
(INFEASIBLE → report the literals, VAL untouched, no Stage-B request); (3) add
the thin maintain-confirmation runner importing accepted `raw_prior_val_1p5m`
read-only with ONLY the §2 d1–d8 delta, four hardcoded arms per §§5-6
(`A_incumbent_L2_operational` 2M-incumbent at session K / `B_alt_L2_operational`
2M-incumbent-p1 + p2_alt at session K with the SAME 2M order prefixes /
`C_incumbent_L2_oracle` / `D_alt_L2_oracle` at session K2), loading the §3 frozen
artifacts read-only behind the `session_prior_identity` + `alt_l2_identity` gates
with the session K-literal gate (replayed, never recarried) plus cross-file
source-tag+digest, intra-file VAL-containment, consumed-1M / consumed-1.5M
exclusions incl. the DEV∩build-frames disjointness declaration (S2-ii), and
maintain-confirmation-identity + order-freeze + K-literal fail-closed gates, with
the §7 mandatory instrumentation recorder `_l2_hazard_diagnostics` (eight exact
scalar fields + the optional ninth U-domain scalar `l2_fail_in_prefix_u_domain`
frozen present-or-absent before execution, post-decode recording-only,
truth-isolation boundary pinned); freeze the population (FIRST 640 VAL frames of
the 2M file → 5 blocks at N=32768 — confirm exact integers `2187..2826` /
`2187..2314/2315..2442/2443..2570/2571..2698/2699..2826` / remainder `2827..2915`
or replace with a written equivalent + justification; JSON-manifest provenance
reads only for the population part), the preregistered per-arm caps from the
derived integers (A/B `5*(K1+K2)+64` with Δ exactly 0; C/D `5*K2+64` with Δ
exactly 0; 327743 public; totals frozen at Stage A), the exact Stage-A derive
command and Stage-B command templates (new P20O tag master 2026092310,
`--source 2M` vocabulary frozen at Stage A, frozen `--prior-digest` /
`--alt-digest` / `--k1/--k2` / `--order-digest` pins, pure 30-SC / 20-tag VAL
budget, 1200-s / 2-GiB / single-thread envelope), SC/tag/genie budgets and
wall/RSS ceilings, and the per-arm floor-hit reporting (S2); (4) add focused
injected tests (fresh additive `workspace/p20o/<uuid>/` temp root,
`pytest -p no:cacheprovider`); (5) run the Stage-A derivation producing the three
frozen artifacts (§§3/9 identity) and write the Stage-A freeze (`P20O_FREEZE.md`,
including all three digests + H/K/order/cap/command + derivation-seed pins +
D1 literals + D2 outcome) + implementation notes; (6) stage the P20O OpenSpec
delta at `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20o/spec.md`
plus the `tasks.md` P20O section (no seed literals in tracked files beyond the
P20O runner/tests/packet/spec documents; tag master 2026092310 and test seeds
2026092311..2026092317 and derivation seeds 2026092321..2026092324 verified absent
elsewhere by repo grep).

Hard limits: EXACTLY ONE protected counts open in Stage A (counts 1/1 for the 2M
`--source 2M` array ONLY; every other array 0) + ZERO VAL-DEV content opens or
stats in Stage A (VAL-DEV 0/1, VAL-remainder 0, 2M HOLD 0 at close); zero 1M-pool
or any 1.5M-split open/stat/listing/read in any form; zero real-data decoder
execution; zero Stage-B output root; no lambda anywhere; no K carried as an
absolute from 1.5M (S2-i; alt-H never a budget input); no K/floor/order/decoder/
step/success-point selection on closed blocks, the consumed 1M pool, any consumed
1.5M range, 2M TRAIN as DEV, 2M VAL remainder 2827..2915, or 2M HOLD; no derivation
on real frames; no second construction, no construction sweep, no order
re-derivation, no disclosure change; no efficiency tuning; no new-block peeking;
no SCL/new kernel/model/schema; no overwrite under `results/` or
`comparison_bench/outputs_comparison/`; no commit/push; no self-acceptance.

Report acceptance IDs P20O-R1..R9 (stage-appropriately), changed files, exact
test commands/results, frozen digests + H/K/order/cap/command + D1 literals + D2
outcome + population, and the split open audit (counts + VAL-DEV + VAL-remainder +
HOLD + 1M/1.5M separately, must be 1 + 0 + 0 + 0 + 0 at Stage-A close) plus the
honest-scope statement (§0) verbatim. Stop on requirement ambiguity or the first
concrete blocker with command, exact error/traceback, attempted remedies, and the
ONE decision needed from the main thread. Stage B is never executed from this
prompt — it needs an independent Pre-EXECUTE review (including the §3 prior/alt
derivation + D2 outcome + §5 budget/K-literal + §4 gate family + §2 runner-delta
design + §7 instrumentation boundary incl. the U-domain scalar) plus a separate
pasted Stage-B authorization.

(End of file)
