Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/TASK_PACKET.md`
(P20S maximum-information mechanism probe on the merged final 2M block, Tier-Y
planning-frozen, reuse-only + one worktree-prior spike permutation under the
frozen DECIDED 2026-09-20 F-median8 formula + uncapped full-block IR-5).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic) plus the accepted
`l2_alt_hold_ir_2m` import target with the §2 delta list (d1–d9) evidenced, the P20Q
`_ir_hazard_diagnostics` code point cited as the carried-over callsite pattern for
the §7 recorder extension, and the P20R `l2_order_position_1p5m`
`derive_new_l2_order` derivation-program pattern reference; (2) perform ZERO protected
opens (counts 0/0 at every stage; the V25 counts NPZ is never opened/statted/listed;
merged-DEV 0/1; 1M 0; 1.5M 0; 2M-non-DEV 0 in every form) and verify the §3 P20O 2M
reuse pins by worktree-file digest recomputation ONLY (prior canonical digest
`b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587` + H literals
`0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477` within 1e-12 +
`p_b` cross-check + floor pins; frozen-A orders file-bytes digest
`b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; alt file-bytes
digest `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5` +
alpha-1.0/floor pins + exact key sets + `p1`-equality within 1e-12 + descriptive alt-H
replay; K literals `(7080,334,6746)` replayed never recomputed with the S2-i
budget-literal replay display `1.3*32768*0.8325627219737477-64 over 5, floored, clipped
[0,65536] = 7080` (never from 1.5M, never from alt-H); D1 literal replay + D2 FEASIBLE
replay with margin `4791.09652735766` BEFORE any DEV contact — replay mismatch ends the
packet at Stage A with DEV untouched and no Stage-B request); (3) Confirm the frozen DECIDED 2026-09-20 F-median8 §3 formula text is present and unambiguous (verbatim: "F-median8: score[i] = h[i] − median(h over the R=8 clipped natural neighborhood of i), where h[i] is the frozen arm-table hazard atom (-log2 true-cell mass, same recipe as the IR recorders); rank all 32768 L2 positions by descending score; take the first K2=6746 positions as arm B's disclosed L2 set; tie-break by ascending natural block coordinate; deterministic, zero sampling, zero genie calls, zero protected reads (inputs: worktree `raw_prior_2m.npz` arrays only); arm A's set stays the frozen incumbent-order first-K2 prefix."); the `NEXTBR_STOP_B1_LOCAL_SPIKE_FORMULA_UNDECIDED` guard applies only if the §3 formula text is missing/contradictory — NEVER invent or alter any functional; then derive the spike order
permutation by the §3 contract (worktree-prior arrays ONLY via
`derive_spike_l2_order` under the frozen DECIDED 2026-09-20 F-median8 formula-id, deterministic, zero
sampling/genie/seeds, zero protected reads, length-32768 permutation, K2-prefix
disclosed, L1 carried frozen; formula-id + program pin + file-bytes digest + A-vs-B
set-delta table pinned in the freeze supplement); (4) add the thin mechanism-probe runner
importing accepted `l2_alt_hold_ir_2m` read-only with ONLY the §2 d1–d9 delta, three
hardcoded arms per §§5-6 (`A_anchor_frozen_order` α1 + frozen order at carried K /
`B_spike_local_order` α1 + spike order at carried K, the probed factor /
`O_true_l1_oracle` frozen-order true-L1 diagnostic at carried K2, D-continuity),
loading the §3 reuse artifacts + spike order file read-only behind the
`reuse_prior_identity` + `reuse_alt_identity` + `reuse_order_freeze_A` +
`spike_order_identity_B` + `order_derivation_program_identity` gates with the K-literal
replay gate plus merged cross-file 2M identity, dual-segment intra-file containment,
consumed-1M / consumed-1.5M / consumed-2M exclusions incl. the DEV∩build-frames
disjointness declaration (S2-ii), and merged-frame-set-identity (exact 128-frame list
rule: 2827..2915 then 3556..3594) + order-position-identity + tag-domain fail-closed
gates, with the §7 carried nine-scalar recorder (arm-specific order digest) PLUS the
mandatory IR-1..IR-4 recorder (P20Q-identical caps/formulas: IR-1 64-bin histograms
{prefix, outside} under the record's OWN order + IR-2 first-error hazard-rank
percentile + IR-3 above-threshold prefix counts at EXACTLY two frozen thresholds
1.0×/2.0× record prefix-mean hazard + IR-4 top-16 with ranks, all PRESENT bounded
recording-only post-decode, truth-isolation boundary pinned) PLUS the IR-5 UNCAPPED
full-block writer (per record: 32768 float32-LE hazard series + 32768 uint8 in-prefix
flags + 32768 uint8 U-domain flags + `ir5full-v1` manifest; binary `.bin` + JSON
manifest ONLY — NO text-JSON float dumps, NO npz/npy/parquet; per-record ≤ ~400 KB,
root ≤ ~1.5 MB, every committed file ≤ ~2 MB); freeze the merged population (VAL tail
2827..2915 + HOLD head 3556..3594 → ONE block at N=32768 — confirm exact integers /
HOLD tail 3595..3644 / 1.5M stub 2172..2212 + HOLD remainder 2725..2766 counted
never-decoded or replace with a written equivalent + justification; JSON-manifest
provenance reads only for the population part), the replayed per-arm caps (A/B
`5*(K1+K2)+64 = 35464` with Δ exactly 0; O `5*K2+64 = 33794`; 327743 public; totals
104722/983229 frozen at Stage A), the A-vs-B set-delta table (size-delta exactly 0),
the exact Stage-A verify command and Stage-B command templates (new P20S tag master
2026092360, `--source 2M` vocabulary frozen at Stage A, frozen `--prior-digest` /
`--alt-digest` / `--k1/--k2` / `--order-digest` / `--spike-order-digest` /
`--spike-formula` replay pins + derivation-program pin, pure 5-SC / 3-tag merged-DEV
budget, 1200-s / 2-GiB / single-thread envelope), SC/tag/genie budgets (genie 0+0) and
wall/RSS ceilings, the IR-3 multiplier pins (1.0×/2.0×) + IR-4 k=16 + IR-5
encoding/size pins, and the per-arm floor-hit reporting (S2); (5) add focused injected
tests (fresh additive `workspace/p20s/<uuid>/` temp root, `pytest -p no:cacheprovider`,
test seeds `2026092361..2026092367`); (6) write the Stage-A freeze supplement
(including all reuse digest replays + H/K/frozen-A-order/cap/command + spike digest +
formula-id + program pin + set-delta table + IR-3 multipliers + IR-4 k + IR-5
encoding/size pins + D1/D2 replay outcome) + implementation notes; (7) stage the P20S
OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20s/spec.md` plus
the `tasks.md` P20S section (no seed literals in tracked files beyond the P20S
runner/tests/packet/spec documents; tag master 2026092360 and test seeds
2026092361..2026092367 verified absent elsewhere by repo grep).

Hard limits: ZERO protected opens in Stage A (counts 0/0 + merged-DEV 0/1 + 1M 0 +
1.5M 0 + 2M-non-DEV 0 at close); zero 1M-pool or any-1.5M-split or any-2M-TRAIN/VAL-DEV/
HOLD-DEV open/stat/listing/read in any form (HOLD tail + 1.5M remainders counted
never-decoded, never contacted beyond counting); zero sampling/genie calls at every
stage (spike derivation is deterministic worktree-prior-only under the frozen DECIDED 2026-09-20 F-median8
formula-id); zero real-data decoder execution; zero Stage-B output root; no spike
derivation under any formula other than the frozen DECIDED 2026-09-20 F-median8 §3 text; no lambda anywhere; no K carried as
an absolute from 1.5M or recomputed from alt-H (S2-i; replay only from the P20O 2M
session point); no K/floor/order/decoder/step/success-point selection on closed blocks,
the consumed 1M pool, any consumed 1.5M range, consumed 2M ranges, HOLD tail 3595..3644
beyond counting, or 1.5M remainders beyond counting; no derivation or sampling on real
frames; no second construction, no construction sweep, no bounded search, no second
order beyond the single spike set, no disclosure-size change (B−A = 0); no decoder
change; no H2 verdict; no recovery-rate reading; no new-block peeking; no SCL/new
kernel/model/schema; no text-JSON float dumps; no npz/npy/parquet evidence files; no
overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push; no
self-acceptance; NEVER invent or alter the frozen DECIDED 2026-09-20 F-median8 §3 formula text.

Report acceptance IDs P20S-R1..R9 (stage-appropriately), changed files, exact test
commands/results, frozen digest replays (prior/alt/frozen-A/spike) + formula-id +
program pin + H/K/order/cap/command + set-delta table + IR-3 multipliers + IR-4 k +
IR-5 encoding/size pins + D1/D2 replay outcome + population, and the split open audit
(counts + merged-DEV + 1M + 1.5M + 2M-non-DEV separately, must be 0 + 0 + 0 + 0 + 0
at Stage-A close) plus the honest-scope statement (§0) verbatim. Stop on requirement
ambiguity or the first concrete blocker with command, exact error/traceback, attempted
remedies, and the ONE decision needed from the main thread — B-1 is RESOLVED 2026-09-20 (F-median8 DECIDED); the `NEXTBR_STOP_B1_LOCAL_SPIKE_FORMULA_UNDECIDED` guard applies only if the §3 formula text is missing/contradictory. Stage B is never executed from this
prompt — it needs an independent Pre-EXECUTE review (including
the §3 reuse/alt replay + spike derivation contract + formula-id decided text (DECIDED 2026-09-20 F-median8) + program
pin + D1/D2 outcome + §5 budget/K-literal replay + §4 gate family (a)→(g) + §2
runner-delta design + §7 nine-scalar + IR-1..IR-4 boundary + IR-5 uncapped
encoding/size rule + arm-specific order-digest rule) plus a separate pasted Stage-B
authorization.

(End of file)
