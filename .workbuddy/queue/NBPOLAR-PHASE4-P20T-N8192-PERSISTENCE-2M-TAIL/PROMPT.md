# P20T Stage-A operator prompt (frozen packet scope only)

Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/TASK_PACKET.md`
(P20T N=8192 persistence probe on the single 2M HOLD-tail DEV block, Tier-Y
planning-frozen, full N=8192 re-derivation from worktree-prior-only synthetic
TRAIN sampling under frozen seeds + carried F-median8 formula-id with R=8
re-frozen + N=8192-sized IR-5).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic) plus the P16
`operational_f13` construction/allocation pattern reference (P16-02: synthetic
TRAIN blocks, pooled risks, worst-first orders, K rule, TRAIN-residual (K1,K2)
selection), the P20S `l2_mechanism_probe_2m` spike-derivation + IR-5 writer
pattern references, and the P20Q `_ir_hazard_diagnostics` code point cited as the
carried-over callsite pattern for the §7 recorder extension; (2) perform ZERO
protected opens beyond the §3 frozen worktree-file reads and JSON-manifest
metadata (counts 0/0 at every stage; the V25 counts NPZ is never
opened/statted/listed; DEV 0/1; 1M 0; 1.5M 0; 2M-non-DEV 0 in every form) and
verify the §3 reuse pins by worktree-file digest recomputation ONLY (prior
canonical digest `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`
+ H literals `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477`
recomputed within 1e-12 + floor pins; N=32768 order/K/tag/leakage literals are
NOT carried — they stay at N=32768); (3) run the frozen N=8192 derivation program
under the frozen TRAIN seeds `2026092410..2026092413` × 4 blocks per stream
(= 16 TRAIN blocks, P16 4×4 pattern, per-stream RNG restart, P13-shared
genie rows, synthetic sampling from the worktree prior arrays ONLY — zero
counts-NPZ opens, zero real-frame use) to produce construction/allocation +
fresh length-8192 L1/L2 worst-first orders + K via `floor((1.3·8192·H−64)/5)`
from recomputed H (≈1760 estimate only, never hand-filled) with (K1,K2) by
TRAIN-residual selection (never from 334/6746), frozen before DEV; then derive
the length-8192 spike order permutation under the carried F-median8 formula-id
with R=8 re-frozen for 8192-geometry (deterministic, zero scoring-time
sampling/genie, zero protected reads, K2-prefix disclosed, L1 carried; formula-id
+ R=8 re-freeze + program pin + file-bytes digest + A-vs-B set-delta table pinned
in the freeze supplement); (4) add the new `FROZEN_N = 8192` runner (or
thin-importer + new frozen constants with justification) importing accepted
helpers read-only with ONLY new-N sizing (13 SC stages, chunk_rows 128, 8192
lengths), three hardcoded arms per §6 (`A_anchor_frozen_order_equivalent` α1 +
newly-derived order at in-packet K / `B_spike_local_order` α1 + new spike order
at in-packet K, the probed factor / `O_true_l1_oracle` newly-derived-order
true-L1 diagnostic at carried K2, D-continuity), loading the §3 Stage-A files
read-only behind the construction-identity + fresh-order-identity + spike-identity
+ derivation-program gates with the K-rule replay gate plus cross-file 2M
identity, single-segment intra-file containment, consumed-1M / consumed-1.5M /
consumed-2M exclusions incl. the DEV∩build-frames disjointness declaration
(S2-ii), and frame-set-identity (exact 32-frame list rule: 3595..3626) +
order-position-identity (arm-specific digests) + tag-domain fail-closed gates,
with the §7 carried nine-scalar recorder (arm-specific order digest) PLUS the
mandatory IR-1..IR-4 recorder (P20Q-identical caps/formulas: IR-1 64-bin
histograms {prefix, outside} under the record's OWN order + IR-2 first-error
hazard-rank percentile + IR-3 above-threshold prefix counts at EXACTLY two frozen
thresholds 1.0×/2.0× record prefix-mean hazard + IR-4 top-16 with ranks, all
PRESENT bounded recording-only post-decode, truth-isolation boundary pinned) PLUS
the IR-5 N=8192-sized writer (per record: 8192 float32-LE hazard series + 8192
uint8 in-prefix flags + 8192 uint8 U-domain flags + `ir5full-v1` manifest; binary
`.bin` + JSON manifest ONLY — NO text-JSON float dumps, NO npz/npy/parquet;
per-record 48 KiB, root ≈ 144 KiB ≤ ~1.5 MB, every committed file ≤ ~2 MB);
freeze the DEV population (HOLD 3595..3626 → ONE block at N=8192 — confirm exact
integers / remainder 3627..3644 / 1.5M stubs 2172..2212 + 2725..2766 counted
never-decoded or replace with a written equivalent + justification; JSON-manifest
provenance reads only for the population part), the derived per-arm caps (A/B
`5·(K1+K2)+64` with Δ exactly 0; O `5·K2+64`; 81983 public; totals derived at
Stage A), the A-vs-B set-delta table (size-delta exactly 0), the exact Stage-A
verify command and Stage-B command templates (new P20T tag master 2026092400,
`--source 2M` vocabulary frozen at Stage A, frozen digests / K literals /
formula-id / program pin, pure 5-SC / 3-tag DEV budget, 1200-s / 2-GiB /
single-thread envelope), sampling/SC/tag budgets (derivation = 16-block budget
only; scoring-time sampling 0) and wall/RSS ceilings, the IR-3 multiplier pins
(1.0×/2.0×) + IR-4 k=16 + IR-5 8192-sizing pins, and the per-arm floor-hit
reporting (S2); (5) add focused injected tests (fresh additive
`workspace/p20t/<uuid>/` temp root, `pytest -p no:cacheprovider`, test seeds
`2026092401..2026092407`); (6) write the Stage-A freeze supplement (including all
reuse digest replays + H/K derivation + TRAIN-residual selection outcome +
fresh-order/construction/spike digests + formula-id with R=8 re-freeze + program
pin + set-delta table + IR-3 multipliers + IR-4 k + IR-5 8192-sizing pins + D
status + population) + implementation notes; (7) stage nothing under OpenSpec
beyond the existing RN delta (spec/design/proposal + `tasks.md` RN section already
frozen; no seed literals in tracked files beyond the P20T runner/tests/packet
documents; tag master 2026092400, test seeds 2026092401..2026092407, and
derivation seeds 2026092410..2026092413 verified absent elsewhere by repo grep).

Hard limits: ZERO protected opens in Stage A beyond the §3 frozen worktree-file
reads + JSON-manifest metadata (counts 0/0 + DEV 0/1 + 1M 0 + 1.5M 0 + 2M-non-DEV
0 at close); zero 1M-pool or any-1.5M-split or any-2M-TRAIN/VAL-DEV/HOLD-DEV
open/stat/listing/read in any form (remainder + 1.5M stubs counted
never-decoded, never contacted beyond counting); zero scoring-time
sampling/genie calls at every stage (derivation sampling ONLY under the §3 frozen
16-block budget/seeds); zero real-data decoder execution; zero Stage-B output
root; no spike derivation under any formula other than carried F-median8 with R=8
re-frozen; no lambda anywhere; no K carried as an absolute from 1.5M or N=32768
or recomputed from alt-H (in-packet derivation only); no K/floor/order/decoder/
step/success-point selection on closed blocks, the consumed 1M pool, any consumed
1.5M range, consumed 2M ranges, or the remainder beyond counting; no derivation
or sampling on real frames; no second construction, no construction sweep, no
bounded search, no second order beyond the single spike set, no disclosure-size
change (B−A = 0); no decoder change; no H2 input; no cross-N reading; no
recovery-rate reading; no new-block peeking; no SCL/new kernel/model/schema; no
text-JSON float dumps; no npz/npy/parquet evidence files; no overwrite under
`results/` or `comparison_bench/outputs_comparison/`; no commit/push; no
self-acceptance.

Report acceptance IDs P20T-R1..R9 (stage-appropriately), changed files, exact test
commands/results, frozen digest replays (prior/construction/fresh-order/spike) +
formula-id with R=8 re-freeze + program pin + H/K derivation + set-delta table +
IR-3 multipliers + IR-4 k + IR-5 8192-sizing pins + population, and the split open
audit (counts + DEV + 1M + 1.5M + 2M-non-DEV separately, must be 0 + 0 + 0 + 0 + 0
at Stage-A close) plus the honest-scope statement (§0) verbatim. Stop on
requirement ambiguity or the first concrete blocker with command, exact
error/traceback, attempted remedies, and the ONE decision needed from the main
thread. Stage B is never executed from this prompt — it needs an independent
Pre-EXECUTE review (including the §3 reuse/derivation contract + formula-id with
R=8 re-freeze + program pin + TRAIN-seed/budget pins + K-rule derivation + §4
gate family (a)→(g) + runner design + §7 nine-scalar + IR-1..IR-4 boundary + IR-5
8192-sizing rule + arm-specific order-digest rule + comparability boundary) plus a
separate pasted Stage-B authorization.

(End of file)
