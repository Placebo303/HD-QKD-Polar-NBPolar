Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/TASK_PACKET.md`
(P20Q instrumented α1 confirmation on type2_2M_20260121_183657 HOLD, Tier-Y
planning-frozen, reuse-only).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic) plus the accepted
`l2_alt_maintain_2m` import target with the §2 delta list (d1–d8) evidenced and the P20O
`_l2_hazard_diagnostics` code point cited as the carried-over callsite pattern for the §7
IR recorder extension; (2) perform ZERO protected opens (counts 0/0 at every stage; the V25
counts NPZ is never opened/statted/listed; HOLD-DEV 0/1; VAL-DEV 0; 1M/1.5M 0 in every form)
and verify the §3 P20O reuse pins by worktree-file digest recomputation ONLY (prior
canonical digest `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587` + H
literals `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477` within 1e-12 +
`p_b` cross-check + floor pins; orders file-bytes digest
`b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; alt file-bytes digest
`98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5` + alpha-1.0/floor pins +
exact key sets + `p1`-equality within 1e-12 + descriptive alt-H replay; K literals
`(7080,334,6746)` replayed never recomputed with the S2-i budget-literal replay display;
D1/D2 FEASIBLE replay with margin `4791.09652735766` BEFORE any HOLD contact — replay
mismatch ends the packet at Stage A with HOLD untouched and no Stage-B request);
(3) add the thin HOLD-IR runner importing accepted `l2_alt_maintain_2m` read-only with ONLY
the §2 d1–d8 delta, four hardcoded arms per §§5-6 (`A_incumbent_L2_operational`
2M-incumbent at carried K / `B_alt_L2_operational` 2M-incumbent-p1 + p2_alt at carried K
with the SAME 2M order prefixes / `C_incumbent_L2_oracle` / `D_alt_L2_oracle` at carried
K2), loading the §3 reuse artifacts read-only behind the `reuse_prior_identity` +
`reuse_alt_identity` + `reuse_order_freeze` gates with the K-literal replay gate plus
cross-file source-tag+digest, intra-file HOLD-containment, consumed-1M / consumed-1.5M /
consumed-2M (TRAIN-as-DEV + VAL DEV + VAL remainder) exclusions incl. the DEV∩build-frames
disjointness declaration (S2-ii), and hold-confirmation-identity + order-freeze + K-literal
fail-closed gates, with the §7 carried nine-scalar recorder PLUS the mandatory IR-1..IR-5
recorder `_ir_hazard_diagnostics` (IR-1 64-bin histograms {prefix, outside} + IR-2
first-error hazard-rank percentile + IR-3 above-threshold prefix counts at EXACTLY two
frozen thresholds 1.0×/2.0× record prefix-mean hazard + IR-4 top-16 hazardous positions
with ranks + IR-5 capped 4096×2 float32 series with truncation flag, all PRESENT bounded
recording-only post-decode, truth-isolation boundary pinned); freeze the population (FIRST
640 HOLD frames of the 2M file → 5 blocks at N=32768 — confirm exact integers `2916..3555`
/ `2916..3043/3044..3171/3172..3299/3300..3427/3428..3555` / remainder `3556..3644` or
replace with a written equivalent + justification; JSON-manifest provenance reads only for
the population part), the replayed per-arm caps (A/B `5*(K1+K2)+64 = 35464` with Δ exactly
0; C/D `5*K2+64 = 33794` with Δ exactly 0; 327743 public; totals 692580/6554860 frozen at
Stage A), the exact Stage-A verify command and Stage-B command templates (new P20Q tag
master 2026092330, `--source 2M` vocabulary frozen at Stage A, frozen `--prior-digest` /
`--alt-digest` / `--k1/--k2` / `--order-digest` replay pins, pure 30-SC / 20-tag HOLD
budget, 1200-s / 2-GiB / single-thread envelope), SC/tag/genie budgets (genie 0+0) and
wall/RSS ceilings, the IR-3 multiplier pins (1.0×/2.0×) + IR caps, and the per-arm
floor-hit reporting (S2); (4) add focused injected tests (fresh additive
`workspace/p20q/<uuid>/` temp root, `pytest -p no:cacheprovider`, test seeds
`2026092331..2026092337`); (5) write the Stage-A freeze (`P20Q_FREEZE.md`, including all
three digest replays + H/K/order/cap/command + IR-3 multipliers + IR caps + D1/D2 replay
outcome) + implementation notes; (6) stage the P20Q OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20q/spec.md` plus the
`tasks.md` P20Q section (no seed literals in tracked files beyond the P20Q
runner/tests/packet/spec documents; tag master 2026092330 and test seeds
2026092331..2026092337 verified absent elsewhere by repo grep).

Hard limits: ZERO protected opens in Stage A (counts 0/0 + HOLD-DEV 0/1 + VAL-DEV 0 +
VAL-remainder 0 + 1M/1.5M 0 at close); zero 1M-pool or any 1.5M-split or any 2M-VAL
open/stat/listing/read in any form; zero sampling/genie calls at every stage; zero
real-data decoder execution; zero Stage-B output root; no lambda anywhere; no K carried as
an absolute from 1.5M or recomputed from alt-H (S2-i; replay only); no K/floor/order/
decoder/step/success-point selection on closed blocks, the consumed 1M pool, any consumed
1.5M range, consumed 2M VAL, 2M TRAIN as DEV, 2M HOLD remainder 3556..3644, or 2M VAL
remainder; no derivation or sampling on real frames; no second construction, no
construction sweep, no order re-derivation, no disclosure change; no efficiency tuning; no
H2 verdict; no new-block peeking; no SCL/new kernel/model/schema; no overwrite under
`results/` or `comparison_bench/outputs_comparison/`; no commit/push; no self-acceptance.

Report acceptance IDs P20Q-R1..R9 (stage-appropriately), changed files, exact test
commands/results, frozen digest replays + H/K/order/cap/command + IR-3 multipliers + IR caps
+ D1/D2 replay outcome + population, and the split open audit (counts + HOLD-DEV + VAL-DEV
+ VAL-remainder + 1M/1.5M separately, must be 0 + 0 + 0 + 0 + 0 at Stage-A close) plus the
honest-scope statement (§0) verbatim. Stop on requirement ambiguity or the first concrete
blocker with command, exact error/traceback, attempted remedies, and the ONE decision
needed from the main thread. Stage B is never executed from this prompt — it needs an
independent Pre-EXECUTE review (including the §3 reuse/alt replay + D2 replay outcome + §5
budget/K-literal replay + §4 gate family + §2 runner-delta design + §7 nine-scalar +
IR-1..IR-5 boundary incl. IR-3 thresholds and IR-5 cap) plus a separate pasted Stage-B
authorization.

(End of file)
