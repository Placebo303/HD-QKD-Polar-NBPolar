Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/TASK_PACKET.md`
(P20N fixed-disclosure ALT-L2-LAPLACE-α1 on type2_1p5M_20260121_183806 HOLD,
Tier-Y planning-frozen).

Stage A only, in order: (1) read-only callsite inventory of the §12
predecessor helpers (filenames listed in the packet — do not modify their
logic) plus the accepted `raw_prior_val_1p5m` import target with the §2 delta
list (d1–d7) evidenced and the P20M `_selected_diagnostics` code point
(`raw_prior_val_1p5m.py:1306-1334`) cited as the carried-over callsite pattern
for the §7 recorder; (2) derive the §3 alt-L2 table (read `counts_ab` from the
digest-reverified P20M worktree npz ONLY — worktree-file read, never a
protected counts open; `f_alt[a,b] = (counts_ab[a,b]+1)/(n_b[b]+1024)` with
frozen α=1, 1e-15 floor step retained + column renormalize, `derive_p2` under
A=32*U1+U2 FULL_BOB_ONLY, `p1`-equality within 1e-12 against the P20M
artifact, descriptive alt-H via `entropy_bits` — never a budget input) and
write the frozen artifact `alt_l2_tables_1p5m.npz` (exact 9-key set,
`alpha` 1.0) with its file-bytes sha256 digest + floor-hit count/rate +
zero-column count + `f_alt` min/max + descriptive alt-H literals pinned for
  the freeze (closed form: zero sampling, zero genie calls, zero derivation
  seeds), plus the D1 feasibility literals (`ce_alt`/`ce_incumbent` TRAIN-only
  estimator, ceilings 33509/35164, `alt_ideal_length_bits`) with the D2
  `alt_construction_budget_feasibility` gate evaluated BEFORE any HOLD contact
  (INFEASIBLE → report the literals, HOLD untouched, no Stage-B request);
  (3) add the thin alt-L2 runner importing accepted
`raw_prior_val_1p5m` read-only with ONLY the §2 d1–d7 delta, four hardcoded
arms per §§5-6 (`A_incumbent_L2_operational` P20M-G1 construction at 331/6689 /
`B_alt_L2_operational` incumbent-p1 + p2_alt at 331/6689 with the SAME P20M
order prefixes / `C_incumbent_L2_oracle` / `D_alt_L2_oracle` at K2 6689),
loading the §3 frozen artifact read-only behind the `alt_l2_identity` gate and
the carried K-literal gate (331/6689/7020 replayed, never recomputed), the
shared frozen P20M order file via the reused `--order-file` + `--order-digest`
gated use with zero sampling; freeze the population (FIRST 512 HOLD frames of
the 1.5M file → 4 blocks at N=32768 — confirm exact integers `2213..2724` /
`2213..2340/2341..2468/2469..2596/2597..2724` / remainder `2725..2766` or
replace with a written equivalent + justification; JSON-manifest provenance
reads only for the population part; §4 gate family (a)→(g): CROSS-FILE
source-tag+digest first, then INTRA-FILE HOLD-containment, then
consumed-TRAIN / consumed-VAL-DEV / VAL-remainder exclusions incl. the
DEV∩build-frames disjointness declaration with frame sets — S2-ii, then
ALT-IDENTITY + ORDER-FREEZE + K-LITERAL), the preregistered per-arm caps from
the carried integers (A/B 35164 with Δ exactly 0; C/D 33509 with Δ exactly 0;
327743 public; totals 549384 + 5243888), the exact Stage-A derive command and
Stage-B command templates (new P20N tag master 2026092300, `--source 1p5M`
vocabulary frozen at Stage A, frozen `--alt-digest` pin, pure 24-SC / 16-tag
HOLD budget, 900-s / 2-GiB / single-thread envelope), SC/tag/genie budgets and
wall/RSS ceilings, and the per-arm floor-hit reporting (S2); implement the §7
mandatory instrumentation recorder `_l2_hazard_diagnostics` at the frozen code
point with the eight exact scalar field names, post-decode recording-only
semantics, and the truth-isolation boundary (record the derivation + K-literal
+ gate + runner-delta + instrumentation-boundary evidence for Pre-EXECUTE);
(4) add focused injected tests (fresh additive `workspace/p20n/<uuid>/` temp
root, `pytest -p no:cacheprovider`); (5) run the Stage-A derivation producing
the frozen `alt_l2_tables_1p5m.npz` (§§3/9 identity) and write the Stage-A
freeze (`P20N_FREEZE.md`, including the alt-table digest + alpha/floor/key-set
+ `p1`-equality + floor-rate + K literals + order digest + budget totals +
derivation-zero-sampling statement) + implementation notes; (6) stage the P20N
OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20n/spec.md`
plus the `tasks.md` P20N section (no seed literals in tracked files; tag
master 2026092300 and test seeds 2026092301..2026092307 verified absent
elsewhere by repo grep; no derivation seeds exist).

Hard limits: ZERO protected content opens or stats in Stage A (counts 0 + HOLD
0 + VAL-remainder 0 at close; the worktree-npz reads are worktree-file reads,
never counts opens; closed-form derivation happens ONLY in Stage A and Stage B
performs ZERO sampling of any kind); zero 1M-pool or reserved-2M
open/stat/listing/read in any form (2M pristine by non-access); zero real-data
decoder execution; zero Stage-B output root; no lambda anywhere; no K other
than the §5 literals (alt-H never a budget input); no K/floor/order/decoder/
step/success-point selection on closed blocks, the consumed 1M pool, any
consumed 1.5M TRAIN DEV (0..1659), P20M VAL DEV 1660..2043, VAL remainder
2044..2212, HOLD remainder 2725..2766, or 2M; no derivation on real frames; no
second construction, no construction sweep, no order re-derivation, no
disclosure change; no efficiency tuning; no new-block peeking; no SCL/new
kernel/model/schema; no overwrite under `results/` or
`comparison_bench/outputs_comparison/`; no commit/push; no self-acceptance.

Report acceptance IDs P20N-R1..R9 (stage-appropriately), changed files, exact
test commands/results, frozen alt-table digest + alpha/floor/key-set +
`p1`-equality + floor-rate + D1 literals + D2 outcome + K literals + order
digest + population/cap/command, and the split open audit (counts + HOLD + VAL-remainder + 2M
separately, must be 0 + 0 + 0 + 0 at Stage-A close) plus the honest-scope
statement (§0) verbatim. Stop on requirement ambiguity or the first concrete
blocker with command, exact error/traceback, attempted remedies, and the ONE
decision needed from the main thread. Stage B is never executed from this
prompt — it needs an independent Pre-EXECUTE review (including the §3
derivation + §5 K-literal + §4 gate family + §2 runner-delta design + §7
instrumentation boundary) plus a separate pasted Stage-B authorization.

(End of file)
