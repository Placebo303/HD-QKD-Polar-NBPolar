# Delta spec — P20N fixed-disclosure ALT-L2-LAPLACE-α1 on type2_1p5M_20260121_183806 HOLD

## Alternative L2 construction (Stage-A closed-form derivation, zero new protected counts reads)

P20N replaces NOTHING about the P20M operating point and changes exactly ONE
construction element: the L2 conditional. The frozen rule
ALT-L2-LAPLACE-α1 reads `counts_ab` from the digest-pinned P20M worktree npz
(canonical digest `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`;
a worktree-file read, never a protected counts open) → `n_b[b]` column totals
→ `f_alt[a,b] = (counts_ab[a,b] + 1) / (n_b[b] + 1024)` (frozen α=1 unit
pseudocount; 1024 = Alice-alphabet size) → `1e-15` floor + column renormalize
(retained formally; expected no-op, Stage A reports the hit count; zero columns
fall back to `p_global`, expected 0) → `p2_alt` via the accepted
`prior.derive_p2` under `A = 32*U1 + U2`, `FULL_BOB_ONLY`. The L1 path is
byte-identical: `p1` for ALL arms is the incumbent P20M `p1` (Stage A asserts
elementwise equality within 1e-12). No lambda anywhere (`alpha` stored `1.0`,
a smoothing-form marker, not a tuned weight). Product:
`alt_l2_tables_1p5m.npz` under the P20N queue dir with keys exactly
(`counts_ab`, `f_alt`, `p1`, `p2_alt`, `alpha`, `floor_value`, `h1_inc`,
`h2_alt`, `h_total_alt`); `h2_alt`/`h_total_alt` are recomputed via the
accepted `target_construction.entropy_bits` functional and are DESCRIPTIVE
ONLY (never a budget input). Identity pin = file-bytes sha256 frozen at Stage
A. Stage B loads the frozen file read-only behind the `alt_l2_identity` gate
(digest + alpha-1.0/floor pins + exact key set + `p1`-equality recheck +
incumbent-prior-digest pin) and refuses on mismatch before any SC call.
FORBIDDEN at any stage: any other construction form, any α other than the
frozen `1`, any L1 change, any V25 counts-NPZ open, any derivation on
HOLD/DEV/VAL frames, any fitting input (consumed 1.5M TRAIN DEV, TRAIN
remainder, P20M VAL DEV, VAL remainder, any 1M split, reserved 2M, Model-F CAL
artifact). Split-counted counts opens stay 0/0. Stage-A derivation is
closed-form arithmetic with ZERO sampling and ZERO genie calls.

## Budget-feasibility gate (Stage-A only, TRAIN-only, HOLD never touched on failure)

Stage A SHALL compute the D1 feasibility literals from the SAME TRAIN counts
(zero protected reads; construction-validity quantities, never decoding inputs
and never thresholds on results): `ce_alt_insample_bits_per_symbol =
(1/total) * sum_{a,b} counts_ab[a,b] * (-log2 p2_alt[u1(a), b, u2(a)])` with
`u1(a) = (a>>5)&31`, `u2(a) = a&31`, `total = counts_ab.sum()`;
`ce_incumbent_insample_bits_per_symbol` = the same estimator with the
incumbent `p2`; `alt_feasibility_ceiling_bits = 5*6689+64 = 33509` (L2-only
gate ceiling) with the operational ceiling `35164` for reference;
`alt_ideal_length_bits = ce_alt_insample_bits_per_symbol * 32768`. The D2 gate
`alt_construction_budget_feasibility` SHALL be evaluated BEFORE any Stage-B
root creation and before any HOLD contact, with the outcome frozen in
`P20N_FREEZE.md` and `STATUS.yaml`: IF `alt_ideal_length_bits > 33509` THEN the
construction is declared `ALT_CONSTRUCTION_BUDGET_INFEASIBLE` — the Stage-A
return reports the D1 literals, the construction is recorded as
falsified-by-arithmetic, HOLD stays 0/1, and no Stage-B authorization is
requested. ELSE the D1 literals freeze and the packet proceeds to
Pre-EXECUTE/Stage B as designed.

## Fixed disclosure and carried orders

`(K1,K2) = (331,6689)`, `K_total = 7020` SHALL be carried byte-identical from
the P20M freeze (literals replayed, never recomputed; the alt-H literals never
enter any budget). The L1 disclosed set SHALL be the first-331 positions of
the frozen P20M L1 order file and the L2 disclosed set the first-6689
positions of the frozen P20M L2 order file (digest
`a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`) on ALL four
arms — no reselection, on ANY data; the construction factor carries ZERO
key-bit delta by design (B−A = 0, D−C = 0). `A_incumbent_L2_operational` SHALL
use the incumbent tables at 331/6689 (P20M-G1 construction, 35164 key
bits/block); `B_alt_L2_operational` SHALL use incumbent `p1` + `p2_alt` at
331/6689 (35164 key bits/block); `C_incumbent_L2_oracle` / `D_alt_L2_oracle`
SHALL use incumbent `p2` / `p2_alt` under true-L1 conditioning at K2=6689
(33509 = 5*6689+64 key bits/block each). Public control is 327743 bits per tag
(`10*32768+63`); planned totals are 549384 key-dependent + 5243888 public
bits. An independent literal transcript recount SHALL match with zero mismatch
or the gate BLOCKS. Sample-CE-normalized ratios are descriptive and are NOT
qualification efficiency.

## Population and closed/consumed-data rule

Consumed/closed and SHALL NOT supply P20N blocks: the P18/P19 HOLD blocks (1M
1600..1983), the P20B VAL pool (1M 1200..1599), the P20C/P20E/P20F DEV blocks
(1M 0..383 / 384..767 / 768..1151), the P20H/P20I/P20J/P20K DEV blocks (1.5M
TRAIN 0..383 / 384..767 / 768..1151 / 1152..1535), TRAIN remainder 1536..1659,
and P20M VAL DEV (1.5M VAL 1660..2043); the ENTIRE 1M pool is fail-closed
against P20N DEV selection; the reserved 2M session file SHALL NOT be opened,
statted, listed, or read (pristine by non-access). VAL remainder 2044..2212
(169 frames) is reserved never-decoded. Stage B SHALL run on the declared
population only: the FIRST 512 HOLD frames (frozen HOLD base 2213: DEV frames
2213..2724 → DEV blocks 2213..2340 / 2341..2468 / 2469..2596 / 2597..2724 at
N=32768; remainder 2725..2766, 42 frames / 10752 pairs, counted, never
decoded). DEV frames SHALL be disjoint from the counts/build frames (build ⊂
TRAIN 0..1659; DEV ⊂ HOLD 2213..2724; declared frame sets, S2-ii). Exclusion is
enforced by the frozen §4 gate family (a)→(g): cross-file source-tag+digest
pin first (size 1869178 B, sha `ca351e52…a06b` provenance pin; never frame
numbers alone), then intra-file HOLD-containment, then consumed-TRAIN,
consumed-VAL-DEV, VAL-remainder exclusions incl. the DEV∩build-frames
declaration, then alt-identity + order-freeze + K-literal pins. Cross-packet
same-block tuning is forbidden.

## Endpoints, arms, and mandatory instrumentation

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`,
`pair_exact` and tag-verified `exact` per record, with `undetected` isolated
(never success) and `decode_failed` / `nonfinite` / `resource_abort` via the
P20A resource path. `B` records SHALL carry the construction-point fields
(`l2_construction`, `k1/k2/k_total`, `alt_digest`, `l1_order_digest`,
`l2_order_digest`) and per-record floor-hit fields (`floor_hits`,
`floor_hit_rate`). `C`/`D` carry oracle provenance, are deployable=false, and
are excluded from every operational aggregate. Outcome labels are descriptive
only (P20M-style, chosen over P16-style: this is the first out-of-sample test
of an alternative L2 construction at fixed disclosure, so no restoration
threshold has an empirical basis; a 62/64-class gate would be an invented
threshold): any exact count is COMPLETE when integrity holds; there is NO
recovery, FER, superiority or qualification threshold. Alt-L2-restoration
(`b_restored_count`: A fail → B exact; `d_restored_count`: C fail → D exact on
the new HOLD segment) and maintenance counts are development signals, never
pass/fail verdicts; the §16 branch decision belongs to later planning, never
to this packet's label.

Both X09-R1 instrumentation requirements SHALL be persisted as per-record
SCALARS (scalar-only five-file rule intact, no vectors): Req1 (H2 — hazard +
coverage at the frozen order) `l2_order_digest`, `l2_prefix_len` (= 6689,
gated), `l2_fail_in_prefix`, `l2_fail_hazard_bits`,
`l2_fail_nbhd_mean_bits` (frozen radius R=8 window), `l2_prefix_hazard_mean_bits`;
Req2 (H3 — failure-neighborhood floor stats) `l2_fail_nbhd_floor_frac`,
`l2_prefix_floor_frac`. Failing-position fields are null unless
`first_error_layer == L2` (natural block symbol index, settled X09-R1 D4);
prefix-wide means use true cells on every completed record. Writer code point:
successor module `l2_alt_hold_1p5m.py::_l2_hazard_diagnostics`, called
post-decode (after tag scoring) from the successor's record writers (the P20M
`_selected_diagnostics` code point is the carried-over callsite pattern).
Truth-isolation boundary (normative): truth and arm tables enter the recorder
for RECORDING ONLY after all SC calls for the record complete; outputs are
record fields and never enter any metric builder, decoder call, disclosure or
order decision (pinned by a focused sentinel test).

## One-shot semantics

Single attempt, no rerun, no construction/K/prior/order change after
preregistration; resource aborts preserve evidence and accounting and BLOCK,
never succeed. Reads are split-counted: counts-calibration opens 0/0
(worktree-npz reads only, never a protected counts open) + HOLD open 1/1
reserved for Stage B (parquet, consumed at the first HOLD content open);
VAL-remainder reads stay 0; 2M stays 0; any reopen, new calibration,
derivation on real frames, or HOLD refit is forbidden. The SCL entry gate is
unchanged: this diagnostic unlocks nothing by itself. Tag domains are new
P20N (master 2026092300, prefix `nbpolar-p20n-l2-alt-hold-1p5m-seed`); focused
test seeds are `2026092301..2026092307` (Stage-A provenance only); NO
derivation seeds exist (closed-form derivation takes none).

## Scope

P20N SHALL use injected data, worktree-prior arrays, and temporary roots in
Stage A with zero protected content opens (counts 0 + HOLD 0 +
VAL-remainder 0 at close), zero 1M-pool or reserved-2M open/stat/listing, zero
real-data decoder execution and zero Stage-B output root. It SHALL NOT use
lambda anywhere; carry any K other than the §5 literals; change the field,
transform, SC arithmetic, floor value, L1 tables, L1/L2 orders, disclosed
sets, verification tag semantics, outcome precedence or scientific status; add
SCL, a new kernel/model/schema, a fifth arm, a second construction, a
construction sweep, or an order re-derivation; reuse the closed blocks, the
consumed 1M pool (any split, any subrange), any consumed 1.5M TRAIN DEV,
TRAIN remainder 1536..1659, P20M VAL DEV 1660..2043, VAL remainder 2044..2212,
HOLD remainder 2725..2766, or the reserved 2M file; derive on or tune with
HOLD/DEV/VAL; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push. Honest scope: this
packet tests ONE preregistered alternative L2 construction at fixed disclosure
on the first HOLD-segment use; it can restore L2 or falsify this
construction; it licenses no reliability/recovery claim; 2M and VAL remainder
remain untouched; the 1M-HOLD thread stays open.

(End of file)
