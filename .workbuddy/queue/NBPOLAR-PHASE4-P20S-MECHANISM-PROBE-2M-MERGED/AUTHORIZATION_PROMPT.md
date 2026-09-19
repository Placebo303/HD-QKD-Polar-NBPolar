# Two-step authorization prompts — NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED

Per `AGENTS.md` §10.1 each step below is directly copyable. Stage A is copyable now
with the spike-formula pin DECIDED 2026-09-20 (F-median8): STEP-1 below permits implementation + reuse
verification + tests + spike derivation under the frozen §3 F-median8 formula
(verbatim §3 text; no re-ask, no alteration). The Stage-B text is a
TEMPLATE until Stage A fills the `<FROZEN_AT_STAGE_A>` pins; the main thread
pastes the filled version only after Stage-A return + independent Pre-EXECUTE
PASS + target-output absence. Neither text authorizes anything beyond its named
step. Blocker B-1 (§15) is RESOLVED 2026-09-20 — F-median8 DECIDED; the pre-registered stop is retained only as a consistency guard (see STEP-1).

---

## STEP 1 — Stage-A authorization (copyable now, spike derivation under frozen F-median8 included)

I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED` exactly as frozen in its
`TASK_PACKET.md` (§§2-7, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor helpers
(including the accepted `l2_alt_hold_ir_2m` import target with the §2 delta list
d1–d9 evidenced and the P20Q `_ir_hazard_diagnostics` code point cited as the
carried-over callsite pattern for the §7 recorder extension, plus the P20R
`l2_order_position_1p5m` derivation-program pattern reference, no logic change);
ZERO protected opens (counts 0/0 at every stage — the V25 counts NPZ is never
opened/statted/listed; merged-DEV stays 0/1; 1M 0; 1.5M 0; 2M-non-DEV 0 in every
form) and verifying the §3 P20O 2M reuse pins by worktree-file digest
recomputation ONLY (prior canonical digest
`b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587` + H literals
`0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477` within 1e-12 +
`p_b` cross-check + floor pins, frozen-A orders file-bytes digest
`b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`, alt file-bytes
digest `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5` +
alpha-1.0/floor pins + exact key sets + `p1`-equality within 1e-12 + descriptive
alt-H replay; K literals `(7080,334,6746)` replayed never recomputed with the S2-i
budget-literal replay display `1.3*32768*0.8325627219737477-64 over 5, floored,
clipped [0,65536] = 7080` (never from 1.5M, never from alt-H); D1 literal replay
(`ce_alt` 0.8850983725781965, `ce_incumbent` 0.8069006731253678, ceilings
33794/35464, `alt_ideal_length_bits` 29002.90347264234) + D2 FEASIBLE replay with
margin `4791.09652735766` BEFORE any DEV contact — replay mismatch ends the packet
at Stage A with DEV untouched and no Stage-B request); confirming the §4 merged
population integers against the split-manifest JSON metadata ONLY (VAL-remainder
tail `2827..2915` + HOLD-remainder head `3556..3594` → ONE block at N=32768, HOLD
tail `3595..3644` counted never decoded, 1.5M remainders counted never decoded; no
parquet/NPZ open/stat/listing); a new thin mechanism-probe runner importing
accepted `l2_alt_hold_ir_2m` read-only with ONLY the §2 d1–d9 delta, three
hardcoded arms `A_anchor_frozen_order` α1 + frozen order at carried K /
`B_spike_local_order` α1 + spike order at carried K (the probed factor, derived ONLY under the frozen DECIDED 2026-09-20 F-median8 formula, verbatim: "F-median8: score[i] = h[i] − median(h over the R=8 clipped natural neighborhood of i), where h[i] is the frozen arm-table hazard atom (-log2 true-cell mass, same recipe as the IR recorders); rank all 32768 L2 positions by descending score; take the first K2=6746 positions as arm B's disclosed L2 set; tie-break by ascending natural block coordinate; deterministic, zero sampling, zero genie calls, zero protected reads (inputs: worktree `raw_prior_2m.npz` arrays only); arm A's set stays the frozen incumbent-order first-K2 prefix.") /
`O_true_l1_oracle` frozen-order true-L1 diagnostic at carried K2, loading the
frozen P20O 2M artifacts read-only behind the `reuse_prior_identity` +
`reuse_alt_identity` + `reuse_order_freeze_A` + `spike_order_identity_B` +
`order_derivation_program_identity` gates with the K-literal replay gate, plus
merged cross-file 2M identity, dual-segment intra-file containment, consumed-1M /
consumed-1.5M / consumed-2M exclusions incl. the DEV∩build-frames disjointness
declaration (S2-ii), and merged-frame-set-identity (exact 128-frame list rule:
2827..2915 then 3556..3594) + order-position-identity + tag-domain fail-closed
gates, with the §7 carried nine-scalar recorder (arm-specific order digest) PLUS
the mandatory IR-1..IR-4 recorder (P20Q-identical caps/formulas: IR-1 64-bin
histograms {prefix, outside} under the record's OWN order + IR-2 first-error
hazard-rank percentile + IR-3 above-threshold prefix counts at EXACTLY two frozen
thresholds 1.0×/2.0× record prefix-mean hazard + IR-4 top-16 with ranks, all
PRESENT bounded recording-only post-decode with the truth-isolation boundary
pinned) PLUS the IR-5 UNCAPPED full-block writer (per record: 32768 float32-LE
hazard series + 32768 uint8 in-prefix flags + 32768 uint8 U-domain flags +
`ir5full-v1` manifest linkage; binary `.bin` + JSON manifest ONLY, no text-JSON
float dumps, no npz/npy/parquet; per-record ≤ ~400 KB, root ≤ ~1.5 MB, every
committed file ≤ ~2 MB) plus focused injected tests under a fresh additive
`workspace/p20s/<uuid>/` temp root (test seeds `2026092361..2026092367`); the
P20S OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20s/spec.md`
plus the `tasks.md` P20S section; the Stage-A freeze supplement (reuse replays +
spike digest + formula-id + program pin + set-delta table + population + caps +
budgets + tag domain + IR-3 multipliers + IR-4 k + IR-5 encoding/size pins + all
commands verbatim) + implementation notes.

This authorization permits spike-order derivation ONLY under the frozen DECIDED 2026-09-20 F-median8 formula (verbatim: "F-median8: score[i] = h[i] − median(h over the R=8 clipped natural neighborhood of i), where h[i] is the frozen arm-table hazard atom (-log2 true-cell mass, same recipe as the IR recorders); rank all 32768 L2 positions by descending score; take the first K2=6746 positions as arm B's disclosed L2 set; tie-break by ascending natural block coordinate; deterministic, zero sampling, zero genie calls, zero protected reads (inputs: worktree `raw_prior_2m.npz` arrays only); arm A's set stays the frozen incumbent-order first-K2 prefix.") (Blocker B-1 RESOLVED 2026-09-20; the `NEXTBR_STOP_B1_LOCAL_SPIKE_FORMULA_UNDECIDED` guard applies only if the §3 formula text is missing/contradictory). It further permits ZERO protected counts opens
(counts 0/0 at every stage), ZERO merged-DEV/tail / VAL-DEV / TRAIN / HOLD-DEV
content opens or stats, ZERO 1M-pool or any-1.5M-split open/stat/listing/read in
any form, ZERO sampling/genie calls at every stage, ZERO real-data decoder
execution, ZERO Stage-B output root, NO lambda anywhere, NO K carried as an
absolute from 1.5M or recomputed from alt-H (S2-i; replay only from the P20O 2M
session point; alt-H never a budget input), NO derivation on real frames, NO
closed-block / consumed-1M-pool / any-consumed-1.5M / consumed-2M / tail tuning
or peeking, NO second construction, NO construction sweep, NO bounded search, NO
second order beyond the single spike set, NO disclosure-size change (B−A = 0), NO
decoder change, NO H2 verdict, NO recovery-rate reading, NO SCL/new kernel/model/
schema, NO text-JSON float dumps, NO npz/npy/parquet evidence files, NO overwrite
under `results/` or `comparison_bench/outputs_comparison/`, and NO commit or push.

Stage-B execution is NOT authorized by this text. It requires, in order: the frozen DECIDED 2026-09-20 F-median8 formula-id (B-1 resolved) + Stage-A return (including all reuse digest
replays + spike digest + formula-id + program pin + freeze supplement +
implementation notes), an independent Pre-EXECUTE review (PASS, explicitly
adjudicating the §3 reuse/alt replay, the spike derivation contract +
formula-id decided text (§3, DECIDED 2026-09-20 F-median8), the D1/D2 replay outcome, the §5 budget/K-literal
replay, the §4 gate family (a)→(g) incl. the merged frame-set identity rule, the
§2 runner-delta design, and the §7 nine-scalar + IR-1..IR-4 boundary + IR-5
uncapped encoding/size rule + arm-specific order-digest rule), the filled
Stage-B authorization below naming the exact frozen command + replayed digests +
spike digest + formula-id + replayed K literals, and target-output absence. Stop
at the packet return contract or first concrete blocker.

---

## STEP 2 — Stage-B authorization (TEMPLATE — DO NOT PASTE until Stage A fills `<FROZEN_AT_STAGE_A>`)

I authorize Stage B execution ONLY for
`NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED` with EXACTLY the frozen Stage-B command from
the Stage-A freeze supplement (the `<FROZEN_AT_STAGE_A>` pins filled below; byte-identical to the
module `FROZEN_COMMAND`):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_mechanism_probe_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest <FROZEN_AT_STAGE_A> --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest <FROZEN_AT_STAGE_A> --source 2M --floor 1e-15 --n 32768 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames-val 2827 2915 --dev-frames-hold 3556 3594 --block-frames 128 --remainder-frames 3595 3644 --tag-master 2026092360 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest <FROZEN_AT_STAGE_A> --spike-order-file .workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/new_spike_order_2m.json --spike-order-digest <FROZEN_AT_STAGE_A> --spike-formula <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m
```

with prior digest `<FROZEN_AT_STAGE_A>` replayed, alt-table digest
`<FROZEN_AT_STAGE_A>` replayed, frozen-A order-file digest `<FROZEN_AT_STAGE_A>`
replayed, spike order-file digest `<FROZEN_AT_STAGE_A>` (Stage-A derived, pinned
in the freeze supplement), derivation-program pin + formula-id
`<FROZEN_AT_STAGE_A>` (pinned in the freeze supplement), K literals
`<FROZEN_AT_STAGE_A>` replayed, and merged DEV (VAL tail `2827..2915` + HOLD head
`3556..3594`) + tail `3595..3644` — all pinned in the freeze supplement and
adjudicated PASS by the independent Pre-EXECUTE review.

This authorization permits EXACTLY ONE attempt (attempts 0/1 → 1/1, consumed at the
first merged-DEV content open) producing ONLY the fifteen frozen files under
`.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m/`
(which must be ABSENT now), with merged-DEV reads 0/1 → 1/1, counts staying 0/0 (no counts
open at any stage), 1M 0, 1.5M 0, 2M-non-DEV 0 in every form (HOLD tail + 1.5M remainders
counted never-decoded). It permits no rerun, no prior/alt/construction/K/order/IR-threshold
change, no second attempt for any reason except a recorded identical-freeze repeat of
an execution error (never tuning), no 1M-pool or any-1.5M access in any form, no consumed-2M
access beyond the frozen merged DEV, no recovery-rate reading, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, no H2 verdict, and no commit or push. The
operator returns under the packet §15 contract and never marks its own work accepted.

(End of file)
