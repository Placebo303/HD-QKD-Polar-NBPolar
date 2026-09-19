# Two-step authorization prompts — NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION

Per `AGENTS.md` §10.1 each step below is directly copyable. Stage A is complete
and copyable now. The Stage-B text is a TEMPLATE until Stage A fills the
`<FROZEN_AT_STAGE_A>` pins in `P20O_FREEZE.md`; the main thread pastes the filled
version only after Stage-A return + independent Pre-EXECUTE PASS + target-output
absence. Neither text authorizes anything beyond its named step.

---

## STEP 1 — Stage-A authorization (copyable now)

I authorize Stage A implementation ONLY for
`NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION` exactly as frozen in its
`TASK_PACKET.md` (§§2-7, §12).

This authorization permits: read-only inventory of the packet-§12 predecessor
helpers (including the accepted `raw_prior_val_1p5m` import target with the §2
delta list d1–d8 evidenced and the P20M `_selected_diagnostics` code point
cited, no logic change); the SINGLE counts-calibration open of the §3 2M TRAIN
array (`--source 2M` array ONLY — counts 0/1→1/1; every other array never opened;
zero DEV contact) and deriving the §3 2M raw prior (raw-count MLE + 1e-15 floor +
column renormalize, no lambda anywhere, `derive_p1`/`derive_p2` under A=32*U1+U2
FULL_BOB_ONLY, `p_b` cross-check, canonical digest, session H via `entropy_bits`,
never hand-filled) writing `raw_prior_2m.npz` (exact 10-key set, `lambda_star`
0.0) with digest + H literals + floor-hit rate pinned; model-sampling 16
synthetic TRAIN blocks from the 2M raw prior under frozen derivation seeds
2026092321..2026092324 → L1+L2 genie risks (32 calls, Stage A only) → pooled means
→ `select_empirical_split` → freezing K_total via the literal f=1.3 recomputation
(S2-i, never a carried absolute) + (K1,K2) + worst-first orders into
`raw_prior_orders_2m.json` (file-bytes digest pinned); deriving the §3 2M alt-L2
table from the SAME counts (`f_alt[a,b] = (counts_ab[a,b]+1)/(n_b[b]+1024)` with
frozen α=1, 1e-15 floor step retained + column renormalize, `derive_p2` under
A=32*U1+U2 FULL_BOB_ONLY, `p1`-equality within 1e-12, descriptive alt-H never a
budget input; closed-form alt step with zero DEV reads) writing
`alt_l2_tables_2m.npz` (exact 9-key set, `alpha` 1.0) with file-bytes digest +
floor-rate + `p1`-equality + alt-H pinned; computing the D1 feasibility literals
(`ce_alt`/`ce_incumbent` 2M-TRAIN-only estimator, L2 ceiling `5*K2+64`,
`alt_ideal_length_bits`) and evaluating the D2
`alt_construction_budget_feasibility` gate BEFORE any VAL contact (INFEASIBLE →
report the literals, VAL untouched, no Stage-B request); a new thin
maintain-confirmation runner (four hardcoded arms `A_incumbent_L2_operational`
2M-incumbent at session K / `B_alt_L2_operational` 2M-incumbent-p1 + p2_alt at
session K with the SAME 2M order prefixes / `C_incumbent_L2_oracle` /
`D_alt_L2_oracle` at session K2, loading the frozen artifacts read-only behind
the `session_prior_identity` + `alt_l2_identity` gates with the session K-literal
gate replayed never recarried, plus cross-file source-tag+digest, intra-file
VAL-containment, consumed-1M / consumed-1.5M exclusions incl. the DEV∩build-frames
disjointness declaration (S2-ii), and maintain-confirmation-identity + order-freeze
+ K-literal fail-closed gates) with the §7 mandatory instrumentation recorder
`_l2_hazard_diagnostics` (eight exact scalar fields + the optional ninth U-domain
scalar `l2_fail_in_prefix_u_domain` frozen present-or-absent before execution,
post-decode recording-only, truth-isolation boundary pinned) plus focused injected
tests under a fresh additive `workspace/p20o/<uuid>/` temp root; the P20O OpenSpec
delta at `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20o/spec.md`
plus the `tasks.md` P20O section; the three frozen Stage-A artifacts (§§3/9 identity)
+ the Stage-A freeze (`P20O_FREEZE.md`) + implementation notes.

This authorization explicitly permits EXACTLY ONE protected counts open: the 2M
`--source 2M` TRAIN array (counts 0/1→1/1; every other array 0). It permits ZERO
2M VAL-DEV/VAL-remainder/HOLD content opens or stats (VAL-DEV stays 0/1,
VAL-remainder 0, HOLD 0), ZERO 1M-pool or any 1.5M-split open/stat/listing/read in
any form, ZERO real-data decoder execution, ZERO Stage-B output root, NO lambda
anywhere, NO K carried as an absolute from 1.5M (S2-i; alt-H never a budget input),
NO derivation on real frames, NO closed-block / consumed-1M-pool / any-consumed-1.5M /
2M-TRAIN-as-DEV / VAL-remainder / HOLD tuning or peeking, NO second construction, NO
construction sweep, NO order re-derivation, NO disclosure change, NO efficiency tuning,
NO SCL/new kernel/model/schema, NO overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and NO commit or push.

Stage-B execution is NOT authorized by this text. It requires, in order: Stage-A
return (including all three frozen digests + freeze + implementation notes), an
independent Pre-EXECUTE review (PASS, explicitly adjudicating the §3 prior/alt
derivation, the D2 feasibility outcome, the §5 budget/K-literal, the §4 gate family,
the §2 runner-delta design, and the §7 instrumentation boundary incl. the U-domain
scalar), the filled Stage-B authorization below naming the exact frozen command +
frozen digests + frozen order-file digest + frozen K literals, and target-output
absence. Stop at the packet return contract or first concrete blocker.

---

## STEP 2 — Stage-B authorization (TEMPLATE — do NOT paste until pins are filled)

I authorize Stage B execution ONLY for
`NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION` with EXACTLY the frozen Stage-B
command from `P20O_FREEZE.md` (the `<FROZEN_AT_STAGE_A>` pins filled below;
byte-identical to the module `FROZEN_COMMAND`):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_maintain_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest <FROZEN_AT_STAGE_A> --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest <FROZEN_AT_STAGE_A> --source 2M --floor 1e-15 --n 32768 --k1 <FROZEN_AT_STAGE_A> --k2 <FROZEN_AT_STAGE_A> --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames 2187 2826 --block-frames 128 --remainder-frames 2827 2915 --tag-master 2026092310 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest <FROZEN_AT_STAGE_A> --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m
```

with prior digest `<FROZEN_AT_STAGE_A>`, alt-table digest `<FROZEN_AT_STAGE_A>`,
order-file digest `<FROZEN_AT_STAGE_A>`, K literals `<FROZEN_AT_STAGE_A>`, and VAL DEV
`2187..2826` + remainder `2827..2915` — all pinned in `P20O_FREEZE.md` and adjudicated
PASS by the independent Pre-EXECUTE review.

This authorization permits EXACTLY ONE attempt (attempts 0/1 → 1/1, consumed at the
first VAL content open) producing ONLY the five frozen files under
`.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/`
(which must be ABSENT now), with VAL-DEV reads 0/1 → 1/1, counts staying 1/1 (no second
counts open), VAL-remainder 0, 2M HOLD 0, and 1M/1.5M 0 in every form. It permits no
rerun, no prior/alt/construction/K/order change, no second attempt for any reason except
a recorded identical-freeze repeat of an execution error (never tuning), no 1M-pool or
any-1.5M access in any form, no 2M TRAIN-as-DEV or HOLD access, no overwrite under
`results/` or `comparison_bench/outputs_comparison/`, and no commit or push. The operator
returns under the packet §15 contract and never marks its own work accepted.

(End of file)
