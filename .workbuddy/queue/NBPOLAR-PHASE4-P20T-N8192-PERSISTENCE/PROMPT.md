Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE/TASK_PACKET.md`
(P20T N=8192 persistence probe on the 2M HOLD tail DEV R1 3595..3626, Tier-Y
planning-frozen, full P16-scale new derivation at N=8192 from worktree-reused
prior arrays under frozen sampling budget/seeds + carried F-median8 with R=8
re-frozen + full-block 8192 IR-5).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor
helpers (filenames listed in the packet — do not modify their logic) plus the
P20Q `_ir_hazard_diagnostics` code point cited as the carried-over callsite
pattern for the §7 recorder extension, the P20R `l2_order_position_1p5m`
derivation-program pattern reference, and the P20S `l2_mechanism_probe_2m`
mechanism-probe + IR-5 writer pattern reference; evidence the §2 delta list
(d1–d9) for the NEW `FROZEN_N = 8192` runner (confirm the recommended
`n8192_tail_persistence_probe` module path or freeze a written equivalent with
justification + re-review; NEVER point `--n 8192` at any frozen-point N=32768
runner per the `target_construction.py:1559` hard gate); (2) perform ZERO
protected opens (counts 0/0 at every stage; the V25 counts NPZ is never
opened/statted/listed; DEV R1 stays 0/1; 1M 0; 1.5M 0; 2M-non-DEV 0 in every
form) and verify the §3 worktree inputs by worktree-file digest recomputation
ONLY (prior canonical digest
`b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587` replay-expected
+ H literals `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477`
recomputed within 1e-12, never hand-filled + `p_b` cross-check + floor 1e-15 pin
+ exact key set; N=32768 order/alt files NEVER enter in any form); confirm the
§4 DEV integers against the split-manifest JSON metadata ONLY (HOLD `3595..3626`
→ ONE N=8192 block, 32×256 = 8192; remainder `3627..3644`, 18×256 = 4608,
counted never decoded; 1.5M stubs counted never decoded; no parquet/NPZ
open/stat/listing); grep-verify the §6 tag/test-seed freshness (new P20T master
+ prefix + focused-test seeds absent from every tracked file outside the P20T
runner/tests/packet documents, incl. master 2026092360 exclusion); (3) freeze
the synthetic TRAIN sampling budget (block count) + derivation seeds in the
freeze supplement (worktree arrays ONLY, zero counts opens, zero real frames,
zero genie) and record the carried F-median8 formula-id with the R=8
vs-8192-geometry RE-FREEZE as a new decision (rationale + window rule in the
supplement; the `P20T_STOP_SPIKE_WINDOW_UNREFROZEN` guard fires only if this
decision is absent/contradictory) — then run the §3 derivation (pooled
per-layer risks → worst-first `(e,h,index)` length-8192 orders → `K_total` via
`floor((1.3·8192·H−64)/5)` from recomputed H (≈1760 estimate only, never a
literal before derivation, never hand-filled) → exhaustive `(K1,K2)` by TRAIN
residual frozen before DEV, never carried from (334,6746), never from alt-H) to
emit the construction/allocation artifact + fresh frozen-order-equivalent order
file + fresh spike order file (length-8192 permutations; file-bytes digests +
formula-id pin + R=8 re-freeze + derivation-program pin with sampling
budget/seeds + A-vs-B set-delta table with size-delta exactly 0 + zero-counts
attestation pinned); compute the fresh TRAIN-only feasibility outcome (same
D1/D2 shape, new literals, zero DEV reads — mismatch ends the packet at Stage A
with DEV untouched and no Stage-B request); (4) add the new `FROZEN_N = 8192`
runner with ONLY the §2 d1–d9 delta, three hardcoded arms per §§5-6
(`A_anchor_frozen_order_equivalent` α1 + newly-derived frozen-order-equivalent
at in-packet K / `B_spike_local_order` α1 + newly-derived spike order at
identical in-packet K, the probed factor /
`O_true_l1_oracle` newly-derived frozen-order-equivalent true-L1 diagnostic at
carried K2, deployable=false), loading the §3 worktree inputs + Stage-A-derived
files read-only behind the `worktree_prior_input_identity` +
`session_h_recomputed` + `k_derived_in_packet` +
`construction_allocation_identity` + `frozen_order_identity_A` +
`spike_order_identity_B` + `derivation_program_identity` gates, plus cross-file
2M identity, single-segment intra-file containment, consumed-1M / consumed-1.5M
/ consumed-2M (+ P20S merged ranges + N=32768-file) exclusions incl. the
DEV∩build-frames disjointness declaration (S2-ii), and exact-32-frame-list
(3595..3626 in order) + order-position-identity + tag-domain fail-closed gates,
with the §7 nine-scalar recorder (arm-specific order digest) PLUS the mandatory
IR-1..IR-4 recorder (P20Q-identical caps/formulas: IR-1 64-bin histograms
{prefix, outside} under the record's OWN order + IR-2 first-error hazard-rank
percentile + IR-3 above-threshold prefix counts at EXACTLY two frozen thresholds
1.0×/2.0× record prefix-mean hazard + IR-4 top-16 with ranks, all PRESENT bounded
recording-only post-decode, truth-isolation boundary pinned) PLUS the IR-5
full-block 8192 writer (per record: 8192 float32-LE hazard series = 32768 B +
8192 uint8 in-prefix flags + 8192 uint8 U-domain flags + `ir5full-v1` manifest =
48 KiB/record; binary `.bin` + JSON manifest ONLY — NO text-JSON float dumps, NO
npz/npy/parquet; 3 records ≈ 144 KiB, root ≤ ~1 MB, every committed file ≤
~2 MB); freeze the DEV population (R1 3595..3626 → ONE block at N=8192; remainder
3627..3644 / 1.5M stubs counted never-decoded; S2-ii declaration), the caps from
in-packet K (operational `5*(K1+K2)+64` with B−A exactly 0; oracle `5*K2+64`;
public 81983/tag; totals derived at Stage A), the A-vs-B set-delta table
(size-delta exactly 0), the exact Stage-A verify/derivation command and Stage-B
command templates (new P20T tag master/prefix, `--source 2M` vocabulary frozen
at Stage A, all `<FROZEN_AT_STAGE_A>` replay pins + derivation-program pin, pure
5-SC / 3-tag DEV budget, 1200-s / 2-GiB / single-thread envelope precedent),
SC/tag/genie/sampling budgets (Stage-A sampling = frozen budget, Stage-B
sampling 0, genie 0+0, zero sampling at scoring) and wall/RSS ceilings, the IR-3
multiplier pins (1.0×/2.0×) + IR-4 k=16 + IR-5 8192 encoding/size pins, the SC
stage count 13 + re-sized `chunk_rows` (P11 precedent), and the per-arm
floor-hit reporting (S2); (5) add focused injected tests (fresh additive
`workspace/p20t/<uuid>/` temp root, `pytest -p no:cacheprovider`, fresh
disjoint test seeds pinned at freeze); (6) write the Stage-A freeze supplement
(including worktree digest replay + H/K derivation display + (K1,K2) +
sampling budget/seeds + fresh order/spike digests + formula-id + R=8 re-freeze +
program pin + set-delta table + feasibility outcome + population + S2-ii + caps
+ budgets + tag domain + grep proof + commands verbatim + IR-3 multipliers +
IR-4 k + IR-5 8192 encoding/size pins + module path) + implementation notes;
(7) record the packet supplement alongside this packet — Stage A stages NO
OpenSpec edit (reduced-N delta already RN-1 PASS frozen).

Hard limits: ZERO protected opens in Stage A (counts 0/0 + DEV 0/1 + 1M 0 +
1.5M 0 + 2M-non-DEV 0 at close); zero 1M-pool or any-1.5M-split or any-2M-TRAIN/
VAL-DEV/HOLD-DEV/P20S-merged-range open/stat/listing/read in any form (remainder
+ 1.5M stubs counted never-decoded, never contacted beyond counting); zero V25
counts-NPZ contact at any stage in any form; zero N=32768 order/alt file use in
any form; zero `--n 8192` to any frozen-point N=32768 runner; zero sampling/
genie calls except the frozen worktree-only synthetic TRAIN budget (zero real
frames, zero DEV); zero real-data decoder execution; zero Stage-B output root;
no K carried from (334,6746), recomputed from alt-H, or hand-filled (estimate
≈1760 only until derived); no spike derivation under any formula other than
carried F-median8 with the re-frozen R=8 decision; no lambda anywhere; no
K/floor/order/decoder/step/success-point selection on closed blocks, the
consumed 1M pool, any consumed 1.5M range, consumed 2M ranges, remainder
3627..3644 beyond counting, or stubs beyond counting; no derivation or sampling
on real frames; no second construction, no construction sweep, no bounded
search, no second order beyond the single spike set, no fourth arm, no
disclosure-size change (B−A = 0); no decoder change; no H2 verdict and no H2
input; no recovery-rate reading; no cross-N inference or pooling; no new-block
peeking; no SCL/new kernel/model/schema; no text-JSON float dumps; no
npz/npy/parquet evidence files; no overwrite under `results/` or
`comparison_bench/outputs_comparison/`; no commit/push; no self-acceptance.

Report acceptance IDs P20T-R1..R9 (stage-appropriately), changed files, exact
test commands/results, frozen derivation record (worktree digest replay +
H/K derivation + (K1,K2) + sampling budget/seeds + fresh order/spike digests +
formula-id + R=8 re-freeze + program pin + set-delta table + feasibility outcome
+ population + S2-ii + caps + budgets + tag domain + grep proof + commands) and
the split open audit (counts + DEV + 1M + 1.5M + 2M-non-DEV separately, must be
0 + 0 + 0 + 0 + 0 at Stage-A close) plus the honest-scope statement (§0)
verbatim. Stop on requirement ambiguity or the first concrete blocker with
command, exact error/traceback, attempted remedies, and the ONE decision needed
from the main thread — the R=8 re-freeze is a NEW Stage-A decision (not a
pre-decided literal); the `P20T_STOP_SPIKE_WINDOW_UNREFROZEN` guard fires only
if it is absent/contradictory. Stage B is never executed from this prompt — it
needs an independent Pre-EXECUTE review (including the §3 worktree-input/H/
K-derivation + construction record + formula-id carried text + R=8 re-freeze +
sampling budget/seeds pin + feasibility outcome + §5 in-packet-K caps + §4 gate
family (a)→(g) + §2 runner-derivation design + §7 nine-scalar + IR-1..IR-4
boundary + IR-5 8192 encoding/size rule + arm-specific order-digest rule) plus a
separate pasted Stage-B authorization.

(End of file)
