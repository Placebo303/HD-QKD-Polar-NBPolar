# Delta spec — P20R single-factor L2-order-position on 1.5M VAL remainder with mandatory H2 IR-1..IR-5

## Reuse-only scoring point (P20M/P20N 1.5M artifacts reused read-only, zero protected opens)

P20R SHALL reuse ALL of the P20M/P20N 1.5M scoring point read-only with digest replay
(never re-derived; S2-i satisfied by same-session reuse): the raw-count prior
(`raw_prior_1p5m.npz`, canonical digest
`372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`; keys exactly
`counts_ab, f_raw, p1, p2, p_b, lambda_star, floor_value, h1, h2, h_total`;
`lambda_star` `0.0`; floor `1e-15`; H `0.02519949692375297 / 0.8003665547495433 /
0.8255660516732963` recomputed within 1e-12; `p_b` cross-check) from the 1.5M TRAIN
counts; the worst-first L1+L2 orders (`raw_prior_orders_1p5m.json`, file-bytes digest
`a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`; K1 331 / K2 6689 /
K_total 7020; the FROZEN-A order); the α1 alt table (`alt_l2_tables_1p5m.npz`,
file-bytes digest `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`;
keys exactly `counts_ab, f_alt, p1, p2_alt, alpha, floor_value, h1_inc, h2_alt,
h_total_alt`; `alpha` `1.0`; `p1`-equality within 1e-12; descriptive alt-H never a
budget input). Stage A SHALL verify all three by worktree-file digest recomputation ONLY
with ZERO protected opens (counts 0/0 at every stage; the V25 counts NPZ never
opened/statted/listed). `(K1,K2)` = `(331,6689)` SHALL be replayed literals (never
recomputed, never recarried from 2M; alt-H never a budget input). Stage B SHALL load all
three read-only behind the `reuse_prior_identity` + `reuse_alt_identity` +
`reuse_order_freeze_A` gates and refuse on mismatch before any SC call. FORBIDDEN: any new
derivation or sampling at any stage beyond the single frozen new-B permutation (genie 0+0);
any K carried as an absolute from 2M or recomputed from alt-H; any derivation on
DEV/VAL/HOLD frames.

## New-B order derivation (Stage-A only, worktree-prior arrays only, B-1 frozen)

The ONLY derivation SHALL be the alternate L2-order permutation computed off-protected-data
from the reused worktree prior arrays ONLY by the frozen program
(`l2_order_position_1p5m.py:derive_new_l2_order`, deterministic, pinned in
`P20R_FREEZE.md` with module path + function + rule). The exact ranking functional is the
frozen B-1 user decision (2026-09-19; `TASK_PACKET.md` §3; Stage A SHALL NOT invent or
alter it): rank all 32768 L2 positions by descending alt-table true-cell hazard mass
(-log2 mass at each position's true (U1_cond,B,U2) cell under p2_alt with U1_cond =
hard-L1 candidate, the same hazard definition as the IR recorders), take the first K2=6689
positions as arm B's disclosed L2 set; tie-break by ascending natural block coordinate;
deterministic, zero sampling, zero genie calls, zero protected reads. Arm A's set stays the
frozen incumbent-order first-K2 prefix. The Stage-A product
(`new_l2_order_1p5m.json`: full carried L1 + new-L2 permutations + provenance with the
zero-sampling attestation; file-bytes digest
`c78532860d74512046a1a53224bc6643de0e495614103774df67ba7e5203e751`) SHALL be derived
once in Stage A, pinned in `P20R_FREEZE.md`, and gated on equality thereafter
(`new_order_identity_B` + `order_derivation_program_identity`).

## Budget-feasibility replay (Stage-A only, DEV never touched on mismatch)

Stage A SHALL replay the D1 feasibility literals from the P20N freeze (zero DEV reads;
construction-validity quantities, never decoding inputs and never thresholds on results):
`ce_alt` 0.9027311772313849, `ce_incumbent` 0.8003665547439149, ceilings 33509/35164,
`alt_ideal_length_bits` 29580.69521551802. The D2 gate
`alt_construction_budget_feasibility_replayed` SHALL be evaluated BEFORE any Stage-B root
creation and before any DEV contact, frozen in `P20R_FREEZE.md` and `STATUS.yaml`: replay
MISMATCH (digests, H, K, new-B derivation, or FEASIBLE outcome) → BLOCKED at Stage A, DEV
stays 0/1, no Stage-B authorization requested. FEASIBLE-replay (margin 3928.304784481981)
→ the literals freeze and the packet proceeds to Pre-EXECUTE/Stage B.

## Fixed disclosure and dual orders (order SET is the single factor)

`(K_total,K1,K2)` = `(7020,331,6689)` SHALL be replayed literals (S2-i satisfied by
same-session reuse). The L1 disclosed set SHALL be the first-331 positions of the frozen
P20M L1 order on ALL four arms (L1 carried frozen). The L2 disclosed set SHALL be the
first-6689 positions of the frozen-A order file (digest
`a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`) on arms A/C and the
first-6689 positions of the Stage-A new-B order file (digest
`c78532860d74512046a1a53224bc6643de0e495614103774df67ba7e5203e751`) on arms B/D — no
reselection, on ANY data; the order factor carries ZERO key-bit delta by design (B−A = 0,
D−C = 0; size-delta exactly 0; the SET-delta IS the factor, recorded byte-exact with rank
displacement). `A_frozen-order_operational` SHALL use the α1 tables at carried (K1,K2)
(`5*(K1+K2)+64 = 35164` key bits/block); `B_new-order_operational` SHALL use the
byte-identical α1 tables at carried (K1,K2) (same key bits/block); `C_frozen-order_oracle`
/ `D_new-order_oracle` SHALL use the α1 `p2_alt` under true-L1 conditioning at carried K2
(`5*K2+64 = 33509` key bits/block each). Public control is 327743 bits per tag
(`10*32768+63`); planned totals 137346 + 1310972 replayed at Stage A. An independent literal
transcript recount SHALL match with zero mismatch or the gate BLOCKS.

## Population and closed/consumed-data rule

Consumed/closed and SHALL NOT supply P20R blocks: the entire 1M pool (any split/subrange);
all consumed 1.5M ranges (TRAIN 0..1659, VAL DEV 1660..2043, HOLD 2213..2766); consumed 2M
TRAIN-as-DEV / VAL (DEV + remainder) / HOLD DEV in any form. Stub 2172..2212 (41 frames /
10496 pairs) is reserved never-decoded; 2M HOLD remainder 3556..3644 (89 frames / 22784
pairs) is counted never-decoded, never contacted beyond counting. Stage B SHALL run on the
declared population only: the FIRST 128 VAL-remainder frames of `type2_1p5M_20260121_183806`
in (frame_id, pair_idx) order (frozen VAL-remainder base 2044 by TRAIN 1660 + P20M DEV 384
manifest-count arithmetic: DEV frames 2044..2171 → ONE block 2044..2171 at N=32768; 32768
pairs). DEV frames SHALL be disjoint from the counts/build frames (build ⊂ 1.5M TRAIN
0..1659; DEV ⊂ 1.5M VAL-remainder 2044..2171; declared frame sets, S2-ii). Exclusion is
enforced by the frozen §4 gate family (a)→(g): cross-file source-tag+digest pin first
(never frame numbers alone), then intra-file VAL-remainder-containment, then consumed-1M,
consumed-1.5M, consumed-2M exclusions incl. the DEV∩build-frames declaration, then
reuse-prior + reuse-alt + frozen-A-order + new-B-order + derivation-program + K-literal +
order-position-identity pins. Cross-packet same-block tuning is forbidden.

## Endpoints, arms, carried scalars, and mandatory IR-1..IR-5

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`, `pair_exact` and
tag-verified `exact` per record, with `undetected` isolated (never success) and
`decode_failed` / `nonfinite` / `resource_abort` via the P20A resource path. `C`/`D` carry
oracle provenance, are deployable=false, and are excluded from every operational aggregate.
Outcome labels are descriptive only (P20M-style: no restoration threshold has an empirical
basis): any exact count is COMPLETE when integrity holds; there is NO recovery, FER,
superiority, H2-verdict, or qualification threshold. Order-position signals
(`b_maintained_count`: B exact; `b_restored_count`: A fail → B exact; the A→B transition
table; `d_restored_count`/`d_maintained_count` diagnostic only) are development signals,
never pass/fail verdicts; the §16 branch decision and the H2 decision belong to
main-thread analysis after acceptance, never to this packet's label.

All NINE X09-R1/P20O scalars SHALL be carried per record with P20O semantics (true cells
under the record's own arm table AND the record's OWN order — frozen-A on A/C, new-B on
B/D; failing fields null unless `first_error_layer == L2`; prefix-wide means on every
completed record; R=8 window; ninth U-domain scalar PRESENT).

IR-1..IR-5 SHALL ALL be PRESENT per record (bounded/size-capped/recording-only/post-decode/
truth-isolation-safe; Stage A pins exact formulas with injected vectors; never post-hoc;
same caps/formulas as P20Q §7; every prefix flag under the record's OWN order):
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
Writer code point: successor module `l2_order_position_1p5m.py::_ir_hazard_diagnostics`,
called post-decode (after tag scoring) alongside the nine carried scalars (the P20Q
`_ir_hazard_diagnostics` code point is the carried-over callsite pattern). Truth-isolation
boundary (normative): truth and arm tables enter the recorder for RECORDING ONLY after all
SC calls complete; outputs never enter any metric builder, decoder call, disclosure or
order decision (pinned by a focused sentinel test).

The H2 decision quantities the accepted run must supply are pre-registered here with NO
outcome asserted: per-record rank-percentile distribution (A-vs-B split, C/D separately);
histogram summaries (prefix vs outside mass, tail shape per record, A-vs-B contrast);
above-threshold prefix mass (lo/hi per record vs exactness); top-k concentration (X-prefix
concentration under EACH order — the direct position-set observation); capped series +
truncation flags as escalation; plus the nine carried scalars (arm-specific order digests)
and the byte-exact A-vs-B disclosed-set delta table. These inform H2a–H2e in main-thread
analysis after acceptance; they are not FER and not thresholds.

## One-shot semantics

Single attempt, no rerun, no reuse/parameter change after preregistration; resource aborts
preserve evidence and accounting and BLOCK, never succeed. Reads are split-counted:
counts-calibration opens 0/0 at every stage (reuse + deterministic permutation; the V25
counts NPZ never opened/statted/listed) + VAL-remainder-DEV open 1/1 reserved for Stage B
(parquet, consumed at the first DEV content open); VAL-DEV 0; HOLD 0; 1M 0; 2M 0 in every
form (2M HOLD remainder counted never-decoded); any reopen, new derivation/sampling, or DEV
refit is forbidden. The SCL entry gate is unchanged. Tag domains are new P20R (master
2026092340, prefix `nbpolar-p20r-order-position-1p5m-seed`); focused test seeds are
`2026092341..2026092347` (Stage-A provenance only); there are NO derivation seeds (the
frozen permutation is deterministic; zero sampling at every stage; genie 0+0).

## Scope

P20R SHALL use zero protected opens + injected data + the P20M/P20N worktree artifacts +
the single worktree-prior permutation + temporary roots in Stage A with DEV 0/1 at close,
zero 1M-pool / any-2M-split / any-1.5M-TRAIN/VAL-DEV/HOLD open/stat/listing, zero
sampling/genie calls at every stage, zero real-data decoder execution and zero Stage-B
output root. It SHALL NOT re-derive prior/alt/orders from protected counts; carry any 2M
K/order/prior absolute or recompute K from alt-H (S2-i; replay only); use lambda anywhere;
change the field, transform, SC arithmetic, floor value, 1.5M L1 tables, frozen-A orders,
disclosed sizes, verification tag semantics, outcome precedence or scientific status; add
SCL, a new kernel/model/schema, a fifth arm, a second construction, a construction sweep, a
bounded search, a second order beyond the single new-B set, or a disclosure change; freeze
any IR field as absent; reuse the closed blocks, the consumed 1M pool, any consumed 1.5M
range, consumed 2M ranges, stub 2172..2212 beyond counting, or 2M HOLD remainder beyond
counting; derive on or tune with DEV; decide H2 in-packet; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push.
Honest scope: single-block (1.5M VAL remainder) single-factor test of one alternate
L2-order position rule under the frozen α1 construction at frozen disclosure with the
mandatory H2 instrumentation; descriptive only; the VAL-remainder DEV block is consumed by
this packet; the 41-frame stub and the 2M HOLD remainder stay untouched; no H2 verdict, no
reliability claim; the H2 decision is analysis, not a block result.

(End of file)
