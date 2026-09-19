# Two-step authorization prompts — NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M

Per `AGENTS.md` §10.1 each step below is directly copyable. Stage A is complete
and copyable now. The Stage-B text is a TEMPLATE until Stage A fills every
`<FROZEN_AT_STAGE_A>` pin in `P20M_FREEZE.md`; the main thread pastes the filled
version only after Stage-A return + independent Pre-EXECUTE PASS + target-output
absence. Neither text authorizes anything beyond its named step.

---

## STEP 1 — Stage-A authorization (copyable now)

I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M` exactly as frozen in its
`TASK_PACKET.md` (§§2-6, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor helpers
(including the accepted P13/P16 budget/split callsites and the `l1_order_1p5m`
import target with the §2 delta list d1–d7 evidenced, no logic change); deriving the
§3 corrected prior (read `counts_ab` from the digest-reverified P20H worktree npz
ONLY — worktree-file read, never a protected counts open; raw-count MLE + 1e-15
floor + column renormalize with no lambda anywhere, `derive_p1`/`derive_p2` under
A=32*U1+U2 FULL_BOB_ONLY, `p_b` cross-check) and writing the frozen artifact
`raw_prior_1p5m.npz` (exact 10-key set, `lambda_star` 0.0) with its canonical digest
+ session H literals + floor-hit rate pinned; a new thin raw-prior runner (three
hardcoded arms `G0_old_point_base` λ-prior/P16-order control at 319/6492 /
`G1_raw_prior_session_budget` corrected-prior + derived (K1,K2) + derived worst-first
orders / `G2_true_l1_diagnostic`, loading the frozen artifact read-only behind the
`corrected_prior_identity` gate, with the session-derived point frozen from the
same-run session H — K_total via the literal f=1.3 recomputation displayed (S2-i),
(K1,K2) via `select_empirical_split` semantics on 16 synthetic TRAIN blocks
model-sampled from the corrected prior under the frozen derivation seeds, never a
real frame, never DEV, worst-first L1+L2 orders into the frozen order file
`raw_prior_orders_1p5m.json` with Stage-B read-only `--order-file` +
`--order-digest` gated use and zero sampling — plus cross-file source-tag+digest,
intra-file VAL-containment + VAL-exterior/HOLD, consumed-TRAIN + remainder exclusion
incl. the DEV∩build-frames disjointness declaration (S2-ii), and
corrected-prior-identity + order-freeze + budget-literal fail-closed gates) plus
focused injected tests under a fresh additive `workspace/p20m/<uuid>/` temp root;
the P20M OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20m/spec.md`
plus the `tasks.md` P20M section; the frozen `raw_prior_1p5m.npz` +
`raw_prior_orders_1p5m.json` (§§3/9 identity) + the Stage-A freeze (`P20M_FREEZE.md`)
+ implementation notes.

This authorization explicitly permits ZERO protected content opens: NO V25 counts-NPZ
open (counts stay 0/0; worktree-npz reads are worktree-file reads; derivation seeds
are integers; synthetic derivation happens ONLY in Stage A — corrected-prior arrays +
seed integers only, zero DEV contact — and Stage B performs ZERO sampling), NO 1.5M
DEV/VAL/HOLD content open or stat (DEV stays 0/1, HOLD stays 0/1), NO 1M-pool or
reserved-2M open/stat/listing/read in any form (2M stays pristine by non-access), NO
real-data decoder execution, NO Stage-B output root, NO lambda anywhere, NO K carried
as an absolute from another session (S2-i), NO derivation on real frames, NO
closed-block / consumed-1M-pool / consumed-1.5M-TRAIN-DEV / TRAIN-remainder /
VAL-remainder / HOLD / reserved-2M tuning or peeking, NO second factor (disclosure
tier, order swap on real data, alternative construction, bounded search), NO
efficiency tuning, NO SCL/new kernel/model/schema, NO overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and NO commit or push.

Stage-B execution is NOT authorized by this text. It requires, in order: Stage-A return
(including both frozen product digests + freeze + implementation notes), an independent
Pre-EXECUTE review (PASS, explicitly adjudicating the §3 derivation, the §5 budget
literal, the §4 gate family, and the §2 runner-delta design), the filled Stage-B
authorization below naming the exact frozen command + frozen prior digest + frozen
order-file digest, and target-output absence. Stop at the packet return contract or
first concrete blocker.

---

## STEP 2 — Stage-B authorization (TEMPLATE — do NOT paste until pins are filled)

I authorize Stage B execution ONLY for
`NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M` with EXACTLY the frozen Stage-B command from
`P20M_FREEZE.md` (all `<FROZEN_AT_STAGE_A>` pins filled below; byte-identical to the
module `FROZEN_COMMAND`):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.raw_prior_val_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz --source 1p5M --floor 1e-15 --n 32768 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 1660 2043 --block-frames 128 --remainder-frames 2044 2212 --tag-master 2026092280 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json --order-digest <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m
```

with corrected-prior digest `<FROZEN_AT_STAGE_A>`, order-file digest
`<FROZEN_AT_STAGE_A>`, derived `--k1/--k2` `<FROZEN_AT_STAGE_A>`, session H literals
`<FROZEN_AT_STAGE_A>`, and budget-literal display `<FROZEN_AT_STAGE_A>` — all pinned
in `P20M_FREEZE.md` and adjudicated PASS by the independent Pre-EXECUTE review.

This authorization permits EXACTLY ONE attempt (attempts 0/1 → 1/1, consumed at the
first DEV content open) producing ONLY the five frozen files under
`.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/`
(which must be ABSENT now), with DEV reads 0/1 → 1/1 and HOLD stays 0/1. It permits
no rerun, no seed/K/prior/order change, no second attempt for any reason except a
recorded identical-freeze repeat of an execution error (never tuning), no 1M-pool or
reserved-2M access in any form, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and no commit or push. The operator returns
under the packet §15 contract and never marks its own work accepted.
