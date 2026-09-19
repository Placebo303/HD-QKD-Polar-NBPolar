# Two-step authorization prompts — NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M

Per `AGENTS.md` §10.1 each step below is directly copyable. Stage A is complete
and copyable now. The Stage-B text is a TEMPLATE until Stage A fills the
`<FROZEN_AT_STAGE_A>` pin in `P20N_FREEZE.md`; the main thread pastes the filled
version only after Stage-A return + independent Pre-EXECUTE PASS + target-output
absence. Neither text authorizes anything beyond its named step.

---

## STEP 1 — Stage-A authorization (copyable now)

I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M` exactly as frozen in its
`TASK_PACKET.md` (§§2-7, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor
helpers (including the accepted `raw_prior_val_1p5m` import target with the §2
delta list d1–d7 evidenced and the P20M `_selected_diagnostics` code point
cited, no logic change); deriving the §3 alt-L2 table (read `counts_ab` from
the digest-reverified P20M worktree npz ONLY — worktree-file read, never a
protected counts open; `f_alt[a,b] = (counts_ab[a,b]+1)/(n_b[b]+1024)` with
frozen α=1, 1e-15 floor step retained + column renormalize, `derive_p2` under
A=32*U1+U2 FULL_BOB_ONLY, `p1`-equality within 1e-12, descriptive alt-H never
  a budget input; closed form with zero sampling, zero genie calls, zero
  derivation seeds; the Stage-A derivation additionally computes the D1
  feasibility literals (`ce_alt`/`ce_incumbent` TRAIN-only estimator, ceilings
  33509/35164, `alt_ideal_length_bits`) and evaluates the D2
  `alt_construction_budget_feasibility` gate BEFORE any HOLD contact
  (INFEASIBLE → report the literals, HOLD untouched, no Stage-B request)) and
  writing the frozen artifact `alt_l2_tables_1p5m.npz`
(exact 9-key set, `alpha` 1.0) with its file-bytes digest + floor-hit
count/rate + zero-column count + `f_alt` range + descriptive alt-H pinned; a
new thin alt-L2 runner (four hardcoded arms `A_incumbent_L2_operational`
P20M-G1 construction at 331/6689 / `B_alt_L2_operational` incumbent-p1 +
p2_alt at 331/6689 with the SAME P20M order prefixes / `C_incumbent_L2_oracle`
/ `D_alt_L2_oracle` at K2 6689, loading the frozen artifact read-only behind
the `alt_l2_identity` gate with the carried K-literal gate 331/6689/7020
replayed never recomputed, plus cross-file source-tag+digest,
intra-file HOLD-containment, consumed-TRAIN / consumed-VAL-DEV / VAL-remainder
exclusions incl. the DEV∩build-frames disjointness declaration (S2-ii), and
alt-identity + order-freeze + K-literal fail-closed gates) with the §7
mandatory instrumentation recorder `_l2_hazard_diagnostics` (eight exact
scalar fields, post-decode recording-only, truth-isolation boundary pinned)
plus focused injected tests under a fresh additive `workspace/p20n/<uuid>/`
temp root; the P20N OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20n/spec.md`
plus the `tasks.md` P20N section; the frozen `alt_l2_tables_1p5m.npz`
(§§3/9 identity) + the Stage-A freeze (`P20N_FREEZE.md`) + implementation
notes.

This authorization explicitly permits ZERO protected content opens: NO V25
counts-NPZ open (counts stay 0/0; worktree-npz reads are worktree-file reads;
closed-form derivation happens ONLY in Stage A with zero sampling and zero
genie calls, and Stage B performs ZERO sampling), NO 1.5M HOLD/DEV/VAL-remainder
content open or stat (HOLD stays 0/1, VAL-remainder stays 0), NO 1M-pool or
reserved-2M open/stat/listing/read in any form (2M stays pristine by
non-access), NO real-data decoder execution, NO Stage-B output root, NO lambda
anywhere, NO K other than the §5 literals (alt-H never a budget input), NO
derivation on real frames, NO closed-block / consumed-1M-pool /
consumed-1.5M-TRAIN-DEV / P20M-VAL-DEV / VAL-remainder / HOLD-remainder /
reserved-2M tuning or peeking, NO second construction, NO construction sweep,
NO order re-derivation, NO disclosure change, NO efficiency tuning, NO SCL/new
kernel/model/schema, NO overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and NO commit or push.

Stage-B execution is NOT authorized by this text. It requires, in order:
Stage-A return (including the frozen alt-table digest + freeze +
implementation notes), an independent Pre-EXECUTE review (PASS, explicitly
  adjudicating the §3 derivation, the D2 feasibility outcome, the §5 K-literal, the §4 gate family, the §2
runner-delta design, and the §7 instrumentation boundary), the filled Stage-B
authorization below naming the exact frozen command + frozen alt-table digest
+ frozen order-file digest, and target-output absence. Stop at the packet
return contract or first concrete blocker.

---

## STEP 2 — Stage-B authorization (TEMPLATE — do NOT paste until pins are filled)

I authorize Stage B execution ONLY for
`NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M` with EXACTLY the frozen
Stage-B command from `P20N_FREEZE.md` (the `<FROZEN_AT_STAGE_A>` pin filled
below; byte-identical to the module `FROZEN_COMMAND`):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 900 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --prior-digest 372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/alt_l2_tables_1p5m.npz --alt-digest <FROZEN_AT_STAGE_A> --source 1p5M --floor 1e-15 --n 32768 --k1 331 --k2 6689 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 2213 2724 --block-frames 128 --remainder-frames 2725 2766 --tag-master 2026092300 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m
```

with alt-table digest `<FROZEN_AT_STAGE_A>` and order-file digest
`a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`, K literals
`331/6689/7020`, and HOLD DEV `2213..2724` + remainder `2725..2766` — all pinned
in `P20N_FREEZE.md` and adjudicated PASS by the independent Pre-EXECUTE review.

This authorization permits EXACTLY ONE attempt (attempts 0/1 → 1/1, consumed at
the first HOLD content open) producing ONLY the five frozen files under
`.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/`
(which must be ABSENT now), with HOLD reads 0/1 → 1/1, counts staying 0/0,
VAL-remainder 0 and 2M pristine. It permits no rerun, no construction/K/prior/
order change, no second attempt for any reason except a recorded
identical-freeze repeat of an execution error (never tuning), no 1M-pool or
reserved-2M access in any form, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and no commit or push. The operator
returns under the packet §15 contract and never marks its own work accepted.

(End of file)
