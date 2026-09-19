Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/TASK_PACKET.md`
(P20R single-factor L2-order-position on the 1.5M VAL remainder, Tier-Y
planning-frozen, reuse-only + one worktree-prior permutation).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic) plus the accepted
`l2_alt_hold_ir_2m` import target with the §2 delta list (d1–d8) evidenced and the P20Q
`_ir_hazard_diagnostics` code point cited as the carried-over callsite pattern for the
§7 recorder extension; (2) perform ZERO protected opens (counts 0/0 at every stage; the
V25 counts NPZ is never opened/statted/listed; DEV 0/1; VAL-DEV 0; HOLD 0; 1M 0; 2M 0 in
every form) and verify the §3 1.5M reuse pins by worktree-file digest recomputation
ONLY (prior canonical digest `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`
+ H literals `0.02519949692375297 / 0.8003665547495433 / 0.8255660516732963` within 1e-12
+ `p_b` cross-check + floor pins; frozen-A orders file-bytes digest
`a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`; alt file-bytes
digest `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78` +
alpha-1.0/floor pins + exact key sets + `p1`-equality within 1e-12 + descriptive alt-H
replay; K literals `(7020,331,6689)` replayed never recomputed with the S2-i
budget-literal replay display `1.3*32768*0.8255660516732963-64 over 5, floored, clipped
[0,65536] = 7020` (never from 2M, never from alt-H); D2 FEASIBLE replay with margin
`3928.304784481981` BEFORE any DEV contact — replay mismatch ends the packet at Stage A
with DEV untouched and no Stage-B request); (3) derive the new-B order permutation by
the §3 contract (worktree-prior arrays ONLY via `derive_new_l2_order`, deterministic,
zero sampling/genie/seeds, zero protected reads, length-32768 permutation, K2-prefix
disclosed, L1 carried frozen; program pin + file-bytes digest + A-vs-B set-delta table
pinned in `P20R_FREEZE.md` — the exact ranking functional is B-1, DECIDED 2026-09-19
(alt-table worst-first re-rank; full frozen text in `TASK_PACKET.md` §3; Stage A SHALL
NOT invent or alter it); NEVER invent any functional beyond it; (4) add the thin
order-position runner importing accepted `l2_alt_hold_ir_2m` read-only with ONLY the
§2 d1–d8 delta, four hardcoded arms per §§5-6 (`A_frozen-order_operational` α1 +
frozen order at carried K / `B_new-order_operational` α1 + new order at carried K, the
single factor / `C_frozen-order_oracle` / `D_new-order_oracle` at carried K2), loading
the §3 reuse artifacts + new-B order file read-only behind the
`reuse_prior_identity` + `reuse_alt_identity` + `reuse_order_freeze_A` +
`new_order_identity_B` + `order_derivation_program_identity` gates with the K-literal
replay gate plus cross-file source-tag+digest, intra-file VAL-remainder-containment,
consumed-1M / consumed-1.5M / consumed-2M exclusions incl. the DEV∩build-frames
disjointness declaration (S2-ii), and order-position-identity + tag-domain fail-closed
gates, with the §7 carried nine-scalar recorder (arm-specific order digest) PLUS the
mandatory IR-1..IR-5 recorder `_ir_hazard_diagnostics` (same caps/formulas as P20Q §7:
IR-1 64-bin histograms {prefix, outside} under the record's OWN order + IR-2
first-error hazard-rank percentile + IR-3 above-threshold prefix counts at EXACTLY two
frozen thresholds 1.0×/2.0× record prefix-mean hazard + IR-4 top-16 hazardous positions
with ranks + IR-5 capped 4096×2 float32 series with truncation flag, all PRESENT bounded
recording-only post-decode, truth-isolation boundary pinned); freeze the population
(FIRST 128 VAL-remainder frames of the 1.5M file → ONE block at N=32768 — confirm exact
integers `2044..2171` / stub `2172..2212` / 2M HOLD remainder `3556..3644` counted
never-decoded or replace with a written equivalent + justification; JSON-manifest
provenance reads only for the population part), the replayed per-arm caps (A/B
`5*(K1+K2)+64 = 35164` with Δ exactly 0; C/D `5*K2+64 = 33509` with Δ exactly 0;
327743 public; totals 137346/1310972 frozen at Stage A), the A-vs-B set-delta table
(size-delta exactly 0), the exact Stage-A verify command and Stage-B command templates
(new P20R tag master 2026092340, `--source 1p5M` vocabulary frozen at Stage A, frozen
`--prior-digest` / `--alt-digest` / `--k1/--k2` / `--order-digest` /
`--new-order-digest` replay pins + derivation-program pin, pure 6-SC / 4-tag DEV
budget, 1200-s / 2-GiB / single-thread envelope), SC/tag/genie budgets (genie 0+0) and
wall/RSS ceilings, the IR-3 multiplier pins (1.0×/2.0×) + IR caps, and the per-arm
floor-hit reporting (S2); (5) add focused injected tests (fresh additive
`workspace/p20r/<uuid>/` temp root, `pytest -p no:cacheprovider`, test seeds
`2026092341..2026092347`); (6) write the Stage-A freeze (`P20R_FREEZE.md`, including
all reuse digest replays + H/K/frozen-A-order/cap/command + new-B digest + program pin
+ set-delta table + IR-3 multipliers + IR caps + D2 replay outcome) + implementation
notes; (7) stage the P20R OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20r/spec.md` plus
the `tasks.md` P20R section (no seed literals in tracked files beyond the P20R
runner/tests/packet/spec documents; tag master 2026092340 and test seeds
2026092341..2026092347 verified absent elsewhere by repo grep).

Hard limits: ZERO protected opens in Stage A (counts 0/0 + DEV 0/1 + VAL-DEV 0 + HOLD 0
+ 1M 0 + 2M 0 at close); zero 1M-pool or any-2M-split or any-1.5M-TRAIN/VAL-DEV/HOLD
open/stat/listing/read in any form (2M HOLD remainder counted never-decoded, never
contacted beyond counting); zero sampling/genie calls at every stage (new-order
derivation is deterministic worktree-prior-only); zero real-data decoder execution;
zero Stage-B output root; no lambda anywhere; no K carried as an absolute from 2M or
recomputed from alt-H (S2-i; replay only from the 1.5M session point); no K/floor/order/
decoder/step/success-point selection on closed blocks, the consumed 1M pool, any
consumed 1.5M range, consumed 2M ranges, stub `2172..2212` beyond counting, or 2M HOLD
remainder beyond counting; no derivation or sampling on real frames; no second
construction, no construction sweep, no bounded search, no second order beyond the
single new-B set, no disclosure-size change (B−A = 0, D−C = 0); no decoder change; no
H2 verdict; no new-block peeking; no SCL/new kernel/model/schema; no overwrite under
`results/` or `comparison_bench/outputs_comparison/`; no commit/push; no
self-acceptance; NEVER invent or alter the B-1 ranking functional (frozen in
`TASK_PACKET.md` §3).

Report acceptance IDs P20R-R1..R9 (stage-appropriately), changed files, exact test
commands/results, frozen digest replays (prior/alt/frozen-A/new-B) + program pin +
H/K/order/cap/command + set-delta table + IR-3 multipliers + IR caps + D2 replay
outcome + population, and the split open audit (counts + DEV + VAL-DEV + HOLD + 1M + 2M
separately, must be 0 + 0 + 0 + 0 + 0 + 0 at Stage-A close) plus the honest-scope
statement (§0) verbatim. Stop on requirement ambiguity or the first concrete blocker
with command, exact error/traceback, attempted remedies, and the ONE decision needed
from the main thread — B-1 is DECIDED (frozen §3); the
`NEXTBR_STOP_B1_RANKING_FUNCTIONAL_UNDECIDED` stop applies only if the freeze is
genuinely missing/contradictory at Stage-A start, with no derivation and DEV 0/1. Stage B
is never executed from this prompt — it needs
an independent Pre-EXECUTE review (including the §3 reuse/alt replay + new-B derivation
contract + B-1 decision text + program pin + D2 outcome + §5 budget/K-literal replay + §4 gate family + §2
runner-delta design + §7 nine-scalar + IR-1..IR-5 boundary incl. IR-3 thresholds, IR-5
cap, and arm-specific order-digest rule) plus a separate pasted Stage-B authorization.

(End of file)
