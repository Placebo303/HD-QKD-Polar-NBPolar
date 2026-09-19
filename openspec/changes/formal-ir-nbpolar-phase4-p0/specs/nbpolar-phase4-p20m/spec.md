# Delta spec — P20M raw-prior + session-budget operating-point swap on type2_1p5M_20260121_183806

## Corrected prior (Stage-A derivation, zero new protected counts reads)

P20M replaces the P20H λ-smoothed prior with a corrected raw-count prior derived
in Stage A under a frozen rule: `counts_ab` read from the digest-pinned worktree
npz (canonical digest
`e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`; a
worktree-file read, never a protected counts open) → raw-count MLE
(`counts_ab`/column totals) + `1e-15` floor + column renormalize (zero columns
fall back to `p_global`; X08 reference count 0) → `p1`/`p2` via the accepted
`prior.derive_p1`/`derive_p2` under `A = 32*U1 + U2`, `FULL_BOB_ONLY`. No lambda
anywhere (`lambda_star` stored `0.0`). Cross-check pinned: `p_b == counts_ab`
column totals / total. Product: `raw_prior_1p5m.npz` under the P20M queue dir
with keys exactly (`counts_ab`, `f_raw`, `p1`, `p2`, `p_b`, `lambda_star`,
`floor_value`, `h1`, `h2`, `h_total`), canonical digest (same
`canonical_prior_digest` recipe) frozen at Stage A, session H1/H2/TOTAL literals
frozen at Stage A (X08 descriptive reference: `0.025199496923753` /
`0.800366554749543` / `0.825566051673296`). Stage B loads the frozen file
read-only behind the `corrected_prior_identity` gate (digest + lambda-0.0/floor
pins + exact key set + H literals within 1e-12 + `p_b` cross-check) and refuses
on mismatch before any SC call. FORBIDDEN at any stage: any lambda smoothing,
any V25 counts-NPZ open, prior refit/resmoothing, floor change, calibration or
derivation on DEV/VAL/HOLD or any real frame, any fitting input (consumed 1.5M
TRAIN DEV, TRAIN remainder, any 1M split, reserved 2M, Model-F CAL artifact).
Split-counted counts opens stay 0/0.

## Session-derived budget and split freeze

`K_total` SHALL be `budget_k_total(32768, H_total, 1.3)` =
`floor((1.3*32768*H_total-64)/5)` clipped `[0,65536]`, recomputed from the same
run's session H and displayed as a literal — never carried as an absolute from
another session (S2-i). `(K1,K2)` SHALL follow `select_empirical_split`
semantics: pooled TRAIN mean risks → worst-first `(e,h,index)` L1/L2 orders →
exhaustive integer K1 enumeration → lexicographic `(residual, K1, K2)` minimum.
TRAIN risks SHALL come from 16 synthetic blocks model-sampled from the corrected
prior under the frozen derivation seeds, L1+L2 genie, Stage A only (never a real
frame, never DEV). `allocate_layer_ks` is the same-family analytic reference,
not the selection rule. Integers, orders, and the order-file digest freeze at
Stage A; Stage B uses them read-only with zero sampling.

## Operating-point swap

`G1_raw_prior_session_budget` SHALL use the corrected prior + derived (K1,K2) +
derived worst-first orders (first-K prefixes; no reselection, on ANY data).
`G0_old_point_base` SHALL use the λ prior (digest above) + frozen P16 orders at
K1=319/K2=6492 as the paired same-block control (34119 key bits/block).
Per-arm caps follow `5*(K1+K2)+64` key-dependent bits/block plus one 64-bit tag
per record; public control is 327743 bits per tag (`10*32768+63`). `G1`/`G2`
integers freeze at Stage A. An independent literal transcript recount SHALL
match with zero mismatch or the gate BLOCKS. Sample-CE-normalized ratios are
descriptive and are NOT qualification efficiency.

## Population and closed/consumed-data rule

The three P18/P19 HOLD blocks (1M frames 1600..1983), the P20B VAL pool (1M
frames 1200..1599), the P20C/P20E/P20F DEV blocks (1M 0..383 / 384..767 /
768..1151), the P20H/P20I/P20J/P20K DEV blocks (1.5M TRAIN 0..383 / 384..767 /
768..1151 / 1152..1535) and TRAIN remainder 1536..1659 are CONSUMED or CLOSED and
SHALL NOT supply P20M blocks; the ENTIRE 1M pool is fail-closed against P20M
DEV selection; the reserved 2M session file SHALL NOT be opened, statted,
listed, or read under this packet (pristine by non-access). P20L is SUPERSEDED
with zero consumption; its declared VAL segment is released, not consumed.
Stage B SHALL run on the declared population only: the FIRST 384 VAL frames
(frozen VAL base 1660: DEV frames 1660..2043 → DEV blocks 1660..1787 /
1788..1915 / 1916..2043 at N=32768; remainder 2044..2212, 169 frames / 43264
pairs, counted, never decoded). DEV frames SHALL be disjoint from the
counts/build frames (build ⊂ TRAIN 0..1659; DEV ⊂ VAL 1660..2043; declared
frame sets, S2-ii) with the floor-hit rate reported per construction and per
arm (S2). Exclusion is enforced by the frozen §4 gate family (a)→(g):
cross-file source-tag+digest pin first (size 1869178 B, sha `ca351e52…a06b`
provenance pin; never frame numbers alone), then intra-file VAL-containment +
VAL-exterior/HOLD overlap (VAL first), then P20H/P20I/P20J/P20K-TRAIN +
remainder exclusions incl. the DEV∩build-frames declaration, then
corrected-prior-identity + order-freeze + budget-literal pins. Cross-packet
same-block tuning is forbidden.

## Endpoints and arms

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`,
`pair_exact` and tag-verified `exact` per record, with `undetected`
isolated (never success) and `decode_failed` / `nonfinite` /
`resource_abort` via the P20A resource path. `G1` records SHALL carry the
operating-point fields (`prior_source`, `k1/k2/k_total`, `budget_literal`,
`l1_order_digest`) and per-record floor-hit fields (`floor_hits`,
`floor_hit_rate`). `G2_true_l1_diagnostic` carries oracle provenance, is
deployable=false, and is excluded from every operational aggregate.
Outcome labels are descriptive only (P20I-style, chosen over P16-style: this is
the first out-of-sample test at the new operating point, so no recovery
threshold has an empirical basis; a 62/64-class gate would be an invented
threshold): any exact count is COMPLETE when integrity holds; there is NO
recovery, FER, superiority or qualification threshold. Raw-prior-restoration
(`g1_restored_count`: G0 fail → G1 exact on the new VAL segment) and
maintenance counts are development signals, never pass/fail verdicts; the §16
branch decision belongs to later planning, never to this packet's label.

## One-shot semantics

Single attempt, no rerun, no seed/prior/budget/order change after
preregistration; resource aborts preserve evidence and accounting and
BLOCK, never succeed. Reads are split-counted: counts-calibration opens 0/0
(worktree-npz reads only, never a protected counts open) + DEV open 1/1
reserved for Stage B (parquet, consumed at the first DEV content open); HOLD
reads stay 0/1 untouched; any reopen, new calibration, derivation on real
frames, or DEV refit is forbidden. The SCL entry gate is unchanged: this
diagnostic unlocks nothing by itself. Tag domains are new P20M (master
2026092280, prefix `nbpolar-p20m-raw-prior-val-1p5m-seed`); derivation seeds
are `2026092291..2026092294` (Stage-A provenance only, never Stage-B argv).

## Scope

P20M SHALL use injected data, worktree-prior arrays, seed integers, and
temporary roots in Stage A with zero protected content opens (counts 0 + DEV 0
+ HOLD 0 at close), zero 1M-pool or reserved-2M open/stat/listing, zero
real-data decoder execution and zero Stage-B output root. It SHALL NOT use
lambda anywhere; carry any K/f absolute from another session; change the field,
transform, SC arithmetic, floor value, verification tag semantics, outcome
precedence or scientific status; add SCL, a new kernel/model/schema, a second
arm, a second derivation, or an alternative construction; reuse the closed
blocks, the consumed 1M pool (any split, any subrange), any consumed 1.5M TRAIN
DEV, TRAIN remainder 1536..1659, VAL remainder 2044..2212, HOLD, or the reserved
2M file; derive on or tune with DEV/VAL; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push. Honest scope: this
packet tests the corrected prior + session-derived budget at the operational
point on the first genuinely out-of-sample 1.5M segment; it does not establish
NB-Polar real-block recovery in general, does not close the 1M-HOLD thread, and
the current published gates on DEV must not be confused with out-of-sample
evidence.
