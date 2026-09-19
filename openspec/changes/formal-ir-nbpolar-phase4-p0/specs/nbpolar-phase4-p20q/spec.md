# Delta spec — P20Q instrumented α1 confirmation on 2M HOLD with mandatory H2 IR-1..IR-5

## Reuse-only scoring point (P20O artifacts reused read-only, zero protected opens)

P20Q SHALL reuse ALL of the P20O 2M scoring point read-only with digest replay (never
re-derived, never carried across sessions beyond the same-session reuse — S2-i satisfied by
reuse): the raw-count prior (`raw_prior_2m.npz`, canonical digest
`b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`; keys exactly
`counts_ab, f_raw, p1, p2, p_b, lambda_star, floor_value, h1, h2, h_total`;
`lambda_star` `0.0`; floor `1e-15`; H `0.02566204884275839 / 0.8069006731309893 /
0.8325627219737477` recomputed within 1e-12; `p_b` cross-check) from the 2M TRAIN counts;
the worst-first L1+L2 orders (`raw_prior_orders_2m.json`, file-bytes digest
`b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; K1 334 / K2 6746 /
K_total 7080); the α1 alt table (`alt_l2_tables_2m.npz`, file-bytes digest
`98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`; keys exactly
`counts_ab, f_alt, p1, p2_alt, alpha, floor_value, h1_inc, h2_alt, h_total_alt`; `alpha`
`1.0`; `p1`-equality within 1e-12; descriptive alt-H never a budget input). Stage A SHALL
verify all three by worktree-file digest recomputation ONLY with ZERO protected opens
(counts 0/0 at every stage; the V25 counts NPZ never opened/statted/listed). `(K1,K2)` =
`(334,6746)` SHALL be replayed literals (never recomputed, never recarried; alt-H never a
budget input). Stage B SHALL load all three read-only behind the `reuse_prior_identity` +
`reuse_alt_identity` + `reuse_order_freeze` gates and refuse on mismatch before any SC call.
FORBIDDEN: any new derivation or sampling at any stage (genie 0+0); any K carried as an
absolute from 1.5M or recomputed from alt-H; any derivation on HOLD/VAL frames.

## Budget-feasibility replay (Stage-A only, HOLD never touched on mismatch)

Stage A SHALL replay the D1 feasibility literals from the P20O freeze (zero HOLD reads;
construction-validity quantities, never decoding inputs and never thresholds on results):
`ce_alt` 0.8850983725781965, `ce_incumbent` 0.8069006731253678, ceilings 33794/35464,
`alt_ideal_length_bits` 29002.90347264234. The D2 gate
`alt_construction_budget_feasibility_replayed` SHALL be evaluated BEFORE any Stage-B root
creation and before any HOLD contact, frozen in `P20Q_FREEZE.md` and `STATUS.yaml`: replay
MISMATCH (digests, H, K, or FEASIBLE outcome) → BLOCKED at Stage A, HOLD stays 0/1, no
Stage-B authorization requested. FEASIBLE-replay (margin 4791.09652735766) → the literals
freeze and the packet proceeds to Pre-EXECUTE/Stage B.

## Fixed disclosure and reused orders

`(K_total,K1,K2)` = `(7080,334,6746)` SHALL be replayed literals (S2-i satisfied by reuse).
The L1 disclosed set SHALL be the first-K1 positions of the frozen 2M L1 order file and the
L2 disclosed set the first-K2 positions of the frozen 2M L2 order file (digest
`b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`) on ALL four arms — no
reselection, on ANY data; the construction factor carries ZERO key-bit delta by design
(B−A = 0, D−C = 0). `A_incumbent_L2_operational` SHALL use the 2M incumbent tables at
carried (K1,K2) (`5*(K1+K2)+64 = 35464` key bits/block); `B_alt_L2_operational` SHALL use 2M
incumbent `p1` + `p2_alt` at carried (K1,K2) (same key bits/block); `C_incumbent_L2_oracle`
/ `D_alt_L2_oracle` SHALL use 2M incumbent `p2` / `p2_alt` under true-L1 conditioning at
carried K2 (`5*K2+64 = 33794` key bits/block each). Public control is 327743 bits per tag
(`10*32768+63`); planned totals 692580 + 6554860 replayed at Stage A. An independent literal
transcript recount SHALL match with zero mismatch or the gate BLOCKS.

## Population and closed/consumed-data rule

Consumed/closed and SHALL NOT supply P20Q blocks: the entire 1M pool (any split/subrange);
all 1.5M ranges (TRAIN 0..1659, VAL DEV 1660..2043, VAL remainder 2044..2212, HOLD DEV
2213..2724, HOLD remainder 2725..2766); 2M TRAIN 0..2186 as DEV; 2M VAL 2187..2915 (consumed
DEV 2187..2826 + remainder 2827..2915) in any form. 2M HOLD remainder 3556..3644 (89 frames
/ 22784 pairs) is reserved never-decoded. Stage B SHALL run on the declared population only:
the FIRST 640 HOLD frames of `type2_2M_20260121_183657` in (frame_id, pair_idx) order
(frozen HOLD base 2916 by TRAIN 2187 + VAL 729 manifest-count arithmetic: DEV frames
2916..3555 → DEV blocks 2916..3043 / 3044..3171 / 3172..3299 / 3300..3427 / 3428..3555 at
N=32768; 163840 pairs; remainder 3556..3644 counted, never decoded). DEV frames SHALL be
disjoint from the counts/build frames (build ⊂ 2M TRAIN 0..2186; DEV ⊂ 2M HOLD 2916..3555;
declared frame sets, S2-ii). Exclusion is enforced by the frozen §4 gate family (a)→(g):
cross-file source-tag+digest pin first (never frame numbers alone), then intra-file
HOLD-containment, then consumed-1M, consumed-1.5M, consumed-2M (TRAIN-as-DEV + VAL DEV +
VAL remainder) exclusions incl. the DEV∩build-frames declaration, then reuse-prior +
reuse-alt + order-freeze + K-literal + hold-confirmation-identity pins. Cross-packet
same-block tuning is forbidden.

## Endpoints, arms, carried scalars, and mandatory IR-1..IR-5

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`, `pair_exact` and
tag-verified `exact` per record, with `undetected` isolated (never success) and
`decode_failed` / `nonfinite` / `resource_abort` via the P20A resource path. `C`/`D` carry
oracle provenance, are deployable=false, and are excluded from every operational aggregate.
Outcome labels are descriptive only (P20M-style: no maintenance or H2 threshold has an
empirical basis): any exact count is COMPLETE when integrity holds; there is NO recovery,
FER, superiority, H2-verdict, or qualification threshold. Maintain-confirmation signals
(`b_maintained_count`: B exact; `b_restored_count`: A fail → B exact; the A→B transition
table; `d_restored_count`/`d_maintained_count` diagnostic only) are development signals,
never pass/fail verdicts; the §16 branch decision and the H2 decision belong to
main-thread analysis after acceptance, never to this packet's label.

All NINE X09-R1/P20O scalars SHALL be carried per record with P20O semantics (true cells
under the record's own arm table; failing fields null unless `first_error_layer == L2`;
prefix-wide means on every completed record; R=8 window; ninth U-domain scalar PRESENT).

IR-1..IR-5 SHALL ALL be PRESENT per record (bounded/size-capped/recording-only/post-decode/
truth-isolation-safe; Stage A pins exact formulas with injected vectors; never post-hoc):
IR-1 `ir1_hist_edges_bits` (65 float64, log-spaced) + `ir1_hist_prefix_counts` (64 int) +
`ir1_hist_outside_counts` (64 int) using true cells (~1 KB/record, every completed record);
IR-2 `ir2_first_error_hazard_rank_pct` (1 float64 in [0,1], 1.0 = most hazardous; null
unless L2 failure); IR-3 EXACTLY two thresholds `ir3_thresh_lo_bits` = 1.0 × record prefix
mean + `ir3_thresh_hi_bits` = 2.0 × record prefix mean (deterministic per-record, no tuning;
X10 median fail/prefix ratio 2.246 justifies 2.0× as the elevated tail and 1.0× as
above-mean mass) with `ir3_prefix_above_lo_count/frac` + `ir3_prefix_above_hi_count/frac`
(6 scalars; every completed record); IR-4 top-16 `ir4_topk_coords` + `ir4_topk_hazard_bits`
+ `ir4_topk_in_prefix` + `ir4_topk_ranks` (k=16 frozen; every completed record); IR-5
`ir5_series_hazard_bits` (≤4096 float32, first 4096 natural-order positions) +
`ir5_series_in_prefix` (≤4096 flags) + `ir5_series_truncated` (bool; true at N=32768) +
`ir5_series_total_len` (=32768) as the escalation (every completed record).
Writer code point: successor module `l2_alt_hold_ir_2m.py::_ir_hazard_diagnostics`, called
post-decode (after tag scoring) alongside the nine carried scalars. Truth-isolation boundary
(normative): truth and arm tables enter the recorder for RECORDING ONLY after all SC calls
complete; outputs never enter any metric builder, decoder call, disclosure or order decision
(pinned by a focused sentinel test).

The H2 decision quantities the accepted run must supply are pre-registered here with NO
outcome asserted: per-record rank-percentile distribution; histogram summaries
(prefix vs outside); above-threshold prefix mass (lo/hi); top-k concentration (prefix flags
+ ranks); capped series + truncation flags as escalation; plus the nine carried scalars for
continuity. These inform H2a–H2e in main-thread analysis after acceptance; they are not FER
and not thresholds.

## One-shot semantics

Single attempt, no rerun, no reuse/parameter change after preregistration; resource aborts
preserve evidence and accounting and BLOCK, never succeed. Reads are split-counted:
counts-calibration opens 0/0 at every stage (reuse; the V25 counts NPZ never
opened/statted/listed) + HOLD-DEV open 1/1 reserved for Stage B (parquet, consumed at the
first HOLD content open); VAL-DEV 0; VAL-remainder 0; 1M/1.5M/2M-VAL 0 in every form; any
reopen, new derivation/sampling, or HOLD refit is forbidden. The SCL entry gate is
unchanged. Tag domains are new P20Q (master 2026092330, prefix
`nbpolar-p20q-hold-ir-2m-seed`); focused test seeds are `2026092331..2026092337` (Stage-A
provenance only); there are NO derivation seeds (reuse; zero sampling at every stage;
genie 0+0).

## Scope

P20Q SHALL use zero protected opens + injected data + the P20O worktree artifacts +
temporary roots in Stage A with HOLD-DEV 0/1 at close, zero 1M-pool / any-1.5M-split /
any-2M-VAL open/stat/listing, zero sampling, zero real-data decoder execution and zero
Stage-B output root. It SHALL NOT re-derive or re-sample anything; carry any 1.5M K/order/
prior absolute or recompute K from alt-H (S2-i; replay only); use lambda anywhere; change
the field, transform, SC arithmetic, floor value, 2M L1 tables, 2M L1/L2 orders, disclosed
sets, verification tag semantics, outcome precedence or scientific status; add SCL, a new
kernel/model/schema, a fifth arm, a second construction, a construction sweep, an order
re-derivation, or a disclosure change; freeze any IR field as absent; reuse the closed
blocks, the consumed 1M pool, any consumed 1.5M range, consumed 2M VAL, 2M TRAIN as DEV, 2M
HOLD remainder 3556..3644, or 2M VAL remainder; derive on or tune with DEV/HOLD; decide H2
in-packet; overwrite `results/` or `comparison_bench/outputs_comparison/`; or commit/push.
Honest scope: third-segment (2M HOLD) confirmation of the frozen α1 construction with the
mandatory H2 instrumentation; descriptive only; 2M HOLD is consumed by this packet; 1.5M VAL
remainder stays untouched; no reliability/FER claim; the H2 decision is analysis, not a FER
result.

(End of file)
