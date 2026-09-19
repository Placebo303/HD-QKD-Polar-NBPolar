# Delta spec — P20O maintain-confirmation of ALT-L2-LAPLACE-α1 at per-session disclosure on type2_2M_20260121_183657 VAL

## Per-session prior + budget + split + orders (Stage-A 2M-TRAIN derivation, zero DEV contact)

P20O SHALL derive ALL of the scoring point from the 2M session's own TRAIN (never
carried across sessions — S2-i): the raw-count prior (raw MLE + 1e-15 floor + column
renormalize, no lambda anywhere; `derive_p1`/`derive_p2` under `A = 32*U1 + U2`,
`FULL_BOB_ONLY`; `p_b` cross-check; `lambda_star` stored `0.0`) from the SINGLE
authorized `--source 2M` TRAIN counts array (counts 0/1→1/1 for that array ONLY; every
other array never opened); the session H literals via the accepted
`target_construction.entropy_bits` functional (never hand-filled); `K_total` via the
literal `floor((1.3*32768*H_total-64)/5)` recomputation clipped `[0,65536]` displayed
(S2-i); `(K1,K2)` via the accepted `select_empirical_split` semantics on 16 synthetic
TRAIN blocks model-sampled from the 2M raw prior under frozen derivation seeds
`2026092321..2026092324` (L1+L2 genie, 32 calls, Stage A only; never a real frame, never
DEV); the worst-first L1+L2 orders into the frozen `raw_prior_orders_2m.json`.
Products: `raw_prior_2m.npz` (keys exactly `counts_ab, f_raw, p1, p2, p_b, lambda_star,
floor_value, h1, h2, h_total`; canonical digest via
`per_session_calibration.canonical_prior_digest`) + `raw_prior_orders_2m.json`
(file-bytes digest). Stage B loads both read-only behind the `session_prior_identity`
gate (digests + lambda-0.0/floor pins + exact key sets + H recomputation within 1e-12 +
`p_b` cross-check) and refuses on mismatch before any SC call. FORBIDDEN: any K carried
as an absolute from 1.5M; any derivation on DEV/VAL/HOLD frames; any second counts open.

## Alternative L2 instantiation (Stage-A closed-form, same frozen rule, new digest)

P20O SHALL instantiate the confirmed single factor on the SAME 2M TRAIN counts by the
SAME closed-form rule ALT-L2-LAPLACE-α1: `n_b[b]` column totals →
`f_alt[a,b] = (counts_ab[a,b] + 1) / (n_b[b] + 1024)` (frozen α=1; 1024 = Alice-alphabet
size) → `1e-15` floor + column renormalize (retained formally; Stage A reports the hit
count; zero columns fall back to `p_global`) → `p2_alt` via accepted `prior.derive_p2`
under `A = 32*U1 + U2`, `FULL_BOB_ONLY`. The L1 path is byte-identical: `p1` for ALL arms
is the Stage-A 2M incumbent `p1` (Stage A asserts elementwise equality within 1e-12). No
lambda anywhere (`alpha` stored `1.0`, a smoothing-form marker, not a tuned weight).
Product: `alt_l2_tables_2m.npz` under the P20O queue dir with keys exactly (`counts_ab`,
`f_alt`, `p1`, `p2_alt`, `alpha`, `floor_value`, `h1_inc`, `h2_alt`, `h_total_alt`);
`h2_alt`/`h_total_alt` recomputed via `entropy_bits` and DESCRIPTIVE ONLY (never a budget
input). Identity pin = file-bytes sha256 frozen at Stage A. Stage B loads the frozen file
read-only behind the `alt_l2_identity` gate and refuses on mismatch before any SC call.
FORBIDDEN: any other construction form, any α other than `1`, any L1 change, any
construction sweep/tuning, any order re-derivation under the alt prior.

## Budget-feasibility gate (Stage-A only, TRAIN-only, VAL never touched on failure)

Stage A SHALL compute the D1 feasibility literals from the SAME 2M TRAIN counts (zero DEV
reads; construction-validity quantities, never decoding inputs and never thresholds on
results): `ce_alt_insample_bits_per_symbol = (1/total) * sum_{a,b} counts_ab[a,b] *
(-log2 p2_alt[u1(a), b, u2(a)])` with `u1(a) = (a>>5)&31`, `u2(a) = a&31`,
`total = counts_ab.sum()` (559872 expected); `ce_incumbent_insample_bits_per_symbol` =
the same estimator with the 2M incumbent `p2`; `alt_feasibility_ceiling_bits = 5*K2+64`
(L2-only gate ceiling, `<FROZEN_AT_STAGE_A>`) with the operational ceiling `5*K_total+64`
for reference; `alt_ideal_length_bits = ce_alt_insample_bits_per_symbol * 32768`. The D2
gate `alt_construction_budget_feasibility` SHALL be evaluated BEFORE any Stage-B root
creation and before any VAL contact, frozen in `P20O_FREEZE.md` and `STATUS.yaml`: IF
`alt_ideal_length_bits > 5*K2+64` THEN `ALT_CONSTRUCTION_BUDGET_INFEASIBLE` — the Stage-A
return reports the D1 literals, the point is recorded falsified-by-arithmetic, VAL stays
0/1, and no Stage-B authorization is requested. ELSE the D1 literals freeze and the packet
proceeds to Pre-EXECUTE/Stage B.

## Fixed per-session disclosure and 2M-derived orders

`(K_total,K1,K2)` SHALL be the Stage-A 2M-derived integers (literals replayed, never
recomputed; the alt-H literals never enter any budget; never a carried 1.5M absolute).
The L1 disclosed set SHALL be the first-K1 positions of the frozen 2M L1 order file and
the L2 disclosed set the first-K2 positions of the frozen 2M L2 order file
(digest `<FROZEN_AT_STAGE_A>`) on ALL four arms — no reselection, on ANY data; the
construction factor carries ZERO key-bit delta by design (B−A = 0, D−C = 0).
`A_incumbent_L2_operational` SHALL use the 2M incumbent tables at session (K1,K2)
(`5*(K1+K2)+64` key bits/block); `B_alt_L2_operational` SHALL use 2M incumbent `p1` +
`p2_alt` at session (K1,K2) (same key bits/block); `C_incumbent_L2_oracle` /
`D_alt_L2_oracle` SHALL use 2M incumbent `p2` / `p2_alt` under true-L1 conditioning at
session K2 (`5*K2+64` key bits/block each). Public control is 327743 bits per tag
(`10*32768+63`); planned totals frozen at Stage A (key `5*(2*(5*(K1+K2)+64)+2*(5*K2+64))`
+ public `20*327743 = 6554860`). An independent literal transcript recount SHALL match
with zero mismatch or the gate BLOCKS.

## Population and closed/consumed-data rule

Consumed/closed and SHALL NOT supply P20O blocks: the entire 1M pool (any split/subrange);
all 1.5M ranges (TRAIN 0..1659 incl. P20H–P20K DEV, TRAIN remainder 1536..1659, VAL DEV
1660..2043, VAL remainder 2044..2212, HOLD DEV 2213..2724, HOLD remainder 2725..2766);
2M TRAIN 0..2186 as DEV; 2M HOLD 2916..3644 in any form. 2M VAL remainder 2827..2915
(89 frames / 22784 pairs) is reserved never-decoded. Stage B SHALL run on the declared
population only: the FIRST 640 VAL frames of `type2_2M_20260121_183657` in
(frame_id, pair_idx) order (frozen VAL base 2187: DEV frames 2187..2826 → DEV blocks
2187..2314 / 2315..2442 / 2443..2570 / 2571..2698 / 2699..2826 at N=32768; 163840 pairs;
remainder 2827..2915 counted, never decoded). DEV frames SHALL be disjoint from the
counts/build frames (build ⊂ 2M TRAIN 0..2186; DEV ⊂ 2M VAL 2187..2826; declared frame
sets, S2-ii). Exclusion is enforced by the frozen §4 gate family (a)→(g): cross-file
source-tag+digest pin first (never frame numbers alone), then intra-file VAL-containment,
then consumed-1M, consumed-1.5M exclusions incl. the DEV∩build-frames declaration, then
session-prior + alt-identity + order-freeze + K-literal + maintain-confirmation-identity
pins. Cross-packet same-block tuning is forbidden.

## Endpoints, arms, and mandatory instrumentation

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`, `pair_exact` and
tag-verified `exact` per record, with `undetected` isolated (never success) and
`decode_failed` / `nonfinite` / `resource_abort` via the P20A resource path. `B` records
SHALL carry the session construction-point fields (`l2_construction`, `k1/k2/k_total`,
`prior_digest`, `alt_digest`, `l1_order_digest`, `l2_order_digest`) and per-record
floor-hit fields (`floor_hits`, `floor_hit_rate`). `C`/`D` carry oracle provenance, are
deployable=false, and are excluded from every operational aggregate. Outcome labels are
descriptive only (P20M-style: this is the first independent-session test of the frozen
construction at per-session disclosure, so no maintenance threshold has an empirical
basis): any exact count is COMPLETE when integrity holds; there is NO recovery, FER,
superiority or qualification threshold. Maintain-confirmation signals
(`b_maintained_count`: B exact; `b_restored_count`: A fail → B exact; the A→B transition
table; `d_restored_count`/`d_maintained_count` diagnostic only) are development signals,
never pass/fail verdicts; the §16 branch decision belongs to later planning, never to
this packet's label.

Both X09-R1 instrumentation requirements SHALL be persisted as per-record SCALARS
(scalar-only five-file rule intact, no vectors): Req1 `l2_order_digest`, `l2_prefix_len`
(= session K2, gated), `l2_fail_in_prefix`, `l2_fail_hazard_bits`,
`l2_fail_nbhd_mean_bits` (frozen radius R=8 window), `l2_prefix_hazard_mean_bits`; Req2
`l2_fail_nbhd_floor_frac`, `l2_prefix_floor_frac`. Failing-position fields are null unless
`first_error_layer == L2` (natural block symbol index, settled X09-R1 D4); prefix-wide
means use true cells on every completed record. The successor U-domain cross-check scalar
`l2_fail_in_prefix_u_domain` (null unless L2 failure, else U-domain first-mismatch index
computed on `polar_transform` hats vs U-domain truth vs the disclosed L2 prefix set) SHALL
be frozen present-or-absent before execution with its exact formula — never post-hoc —
recording-only, post-decode. Writer code point: successor module
`l2_alt_maintain_2m.py::_l2_hazard_diagnostics`, called post-decode (after tag scoring)
from the successor's record writers (the P20M `_selected_diagnostics` code point is the
carried-over callsite pattern). Truth-isolation boundary (normative): truth and arm tables
enter the recorder for RECORDING ONLY after all SC calls for the record complete; outputs
are record fields and never enter any metric builder, decoder call, disclosure or order
decision (pinned by a focused sentinel test).

## One-shot semantics

Single attempt, no rerun, no prior/budget/order/construction change after preregistration;
resource aborts preserve evidence and accounting and BLOCK, never succeed. Reads are
split-counted: counts-calibration opens 1/1 (Stage A, 2M array ONLY) + VAL-DEV open 1/1
reserved for Stage B (parquet, consumed at the first VAL content open); VAL-remainder 0;
2M HOLD 0; 1M/1.5M 0 in every form; any reopen, new calibration, derivation on real
frames, or VAL refit is forbidden. The SCL entry gate is unchanged. Tag domains are new
P20O (master 2026092310, prefix `nbpolar-p20o-maintain-2m-seed`); focused test seeds are
`2026092311..2026092317` (Stage-A provenance only); derivation seeds are
`2026092321..2026092324` (consumed in Stage A to produce the frozen orders; Stage B
performs zero sampling).

## Scope

P20O SHALL use the single 2M counts open + injected data + worktree prior arrays +
temporary roots in Stage A with VAL-DEV 0/1 at close, zero 1M-pool or any-1.5M-split
open/stat/listing, zero real-data decoder execution and zero Stage-B output root. It SHALL
NOT carry any 1.5M K/order/prior absolute (S2-i); use lambda anywhere; carry any K other
than the Stage-A 2M-derived literals; change the field, transform, SC arithmetic, floor
value, 2M L1 tables, 2M L1/L2 orders, disclosed sets, verification tag semantics, outcome
precedence or scientific status; add SCL, a new kernel/model/schema, a fifth arm, a second
construction, a construction sweep, or an order re-derivation; reuse the closed blocks, the
consumed 1M pool, any consumed 1.5M range, 2M TRAIN as DEV, 2M VAL remainder 2827..2915, or
2M HOLD; derive on or tune with DEV/VAL; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push. Honest scope: first use of the
reserved 2M independent session to attempt to maintain one prior 1.5M restoration event
with the frozen construction; positive/negative both informative; no reliability claim;
1.5M VAL remainder and the 1M-HOLD thread stay out of scope; 2M is consumed by this packet
regardless of outcome.

(End of file)
