# Delta spec — P20S maximum-information mechanism probe on the merged final 2M block with uncapped full-block IR-5

## Reuse-only scoring point (P20O 2M artifacts reused read-only, zero protected opens)

P20S SHALL reuse ALL of the P20O 2M scoring point read-only with digest replay
(never re-derived; S2-i satisfied by same-session reuse): the raw-count prior
(`raw_prior_2m.npz`, canonical digest
`b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`; keys exactly
`counts_ab, f_raw, p1, p2, p_b, lambda_star, floor_value, h1, h2, h_total`;
`lambda_star` `0.0`; floor `1e-15`; H `0.02566204884275839 / 0.8069006731309893 /
0.8325627219737477` recomputed within 1e-12; `p_b` cross-check) from the 2M TRAIN
counts; the worst-first L1+L2 orders (`raw_prior_orders_2m.json`, file-bytes digest
`b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; K1 334 / K2 6746 /
K_total 7080; the FROZEN-A order); the α1 alt table (`alt_l2_tables_2m.npz`,
file-bytes digest `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`;
keys exactly `counts_ab, f_alt, p1, p2_alt, alpha, floor_value, h1_inc, h2_alt,
h_total_alt`; `alpha` `1.0`; `p1`-equality within 1e-12; descriptive alt-H never a
budget input). Stage A SHALL verify all three by worktree-file digest recomputation ONLY
with ZERO protected opens (counts 0/0 at every stage; the V25 counts NPZ never
opened/statted/listed). `(K1,K2)` = `(334,6746)` SHALL be replayed literals (never
recomputed, never recarried from 1.5M; alt-H never a budget input). Stage B SHALL load all
three read-only behind the `reuse_prior_identity` + `reuse_alt_identity` +
`reuse_order_freeze_A` gates and refuse on mismatch before any SC call. FORBIDDEN: any new
derivation or sampling at any stage beyond the single frozen spike-B permutation (genie 0+0);
any K carried as an absolute from 1.5M or recomputed from alt-H; any derivation on
DEV/VAL/HOLD frames.

## Spike-B order derivation (Stage-A only, worktree-prior arrays only, F-median8 frozen)

The ONLY derivation SHALL be the alternate spike L2-order permutation computed
off-protected-data from the reused worktree prior arrays ONLY by the frozen program
(`l2_mechanism_probe_2m.py:derive_spike_l2_order`, deterministic, pinned in
`P20S_FREEZE.md` with module path + function + formula-id + argv). The exact ranking
functional is the frozen DECIDED 2026-09-20 user decision (`TASK_PACKET.md` §3; Stage A
SHALL NOT invent or alter it): "F-median8: score[i] = h[i] − median(h over the R=8
clipped natural neighborhood of i), where h[i] is the frozen arm-table hazard atom
(-log2 true-cell mass, same recipe as the IR recorders); rank all 32768 L2 positions by
descending score; take the first K2=6746 positions as arm B's disclosed L2 set; tie-break
by ascending natural block coordinate; deterministic, zero sampling, zero genie calls,
zero protected reads (inputs: worktree `raw_prior_2m.npz` arrays only); arm A's set stays
the frozen incumbent-order first-K2 prefix." The Stage-A product
(`new_spike_order_2m.json`: full carried L1 + spike-L2 permutations + provenance with the
zero-sampling attestation; file-bytes digest
`139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864`) SHALL be derived
once in Stage A, pinned in `P20S_FREEZE.md`, and gated on equality thereafter
(`spike_order_identity_B` + `order_derivation_program_identity`).

## Budget-feasibility replay (Stage-A only, DEV never touched on mismatch)

Stage A SHALL replay the D1 feasibility literals from the P20O freeze (zero DEV reads;
construction-validity quantities, never decoding inputs and never thresholds on results):
`ce_alt` 0.8850983725781965, `ce_incumbent` 0.8069006731253678, ceilings 33794/35464,
`alt_ideal_length_bits` 29002.90347264234. The D2 gate
`alt_construction_budget_feasibility_replayed` SHALL be evaluated BEFORE any Stage-B root
creation and before any DEV contact, frozen in `P20S_FREEZE.md` and `STATUS.yaml`: replay
MISMATCH (digests, H, K, spike derivation, or FEASIBLE outcome) → BLOCKED at Stage A, DEV
stays 0/1, no Stage-B authorization requested. FEASIBLE-replay (margin 4791.09652735766)
→ the literals freeze and the packet proceeds to Pre-EXECUTE/Stage B.

## Fixed disclosure and dual orders (order SET is the single factor)

`(K_total,K1,K2)` = `(7080,334,6746)` SHALL be replayed literals (S2-i satisfied by
same-session reuse). The L1 disclosed set SHALL be the first-334 positions of the frozen
P20O L1 order on ALL three arms (L1 carried frozen). The L2 disclosed set SHALL be the
first-6746 positions of the frozen-A order file (digest
`b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`) on arms A/O and the
first-6746 positions of the Stage-A spike order file (digest
`139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864`) on arm B — no
reselection, on ANY data; the order factor carries ZERO key-bit delta by design (B−A = 0;
size-delta exactly 0; the SET-delta IS the factor, recorded byte-exact with rank
displacement: intersection 5147, symmetric difference 1599/1599). `A_anchor_frozen_order`
SHALL use the α1 tables at carried (K1,K2) (`5*(K1+K2)+64 = 35464` key bits/block);
`B_spike_local_order` SHALL use the byte-identical α1 tables at carried (K1,K2) (same key
bits/block); `O_true_l1_oracle` SHALL use the α1 `p2_alt` under true-L1 conditioning at
carried K2 (`5*K2+64 = 33794` key bits/block; provenance ORACLE, deployable=false, the
P20O/P20Q-D continuity). Public control is 327743 bits per tag (`10*32768+63`); planned
totals 104722 + 983229 replayed at Stage A. An independent literal transcript recount SHALL
match with zero mismatch or the gate BLOCKS.

## Population and closed/consumed-data rule

Consumed/closed and SHALL NOT supply P20S blocks: the entire 1M pool (any split/subrange);
all consumed 1.5M ranges (TRAIN 0..1659, VAL DEV 1660..2043, VAL stub 2172..2212,
HOLD 2213..2766); consumed 2M TRAIN-as-DEV / VAL DEV 2187..2826 / HOLD DEV 2916..3555 in
any form. HOLD tail 3595..3644 (50 frames / 12800 pairs) is reserved never-decoded; 1.5M
VAL stub 2172..2212 (41 frames / 10496 pairs) + 1.5M HOLD remainder 2725..2766 (42 frames
/ 10752 pairs) are counted never-decoded, never contacted beyond counting. Stage B SHALL
run on the declared population only: the merged final 2M block of
`type2_2M_20260121_183657` — VAL-remainder tail `2827..2915` (89 frames) FOLLOWED BY
HOLD-remainder head `3556..3594` (first 39 of 3556..3644), in (frame_id, pair_idx) order
within each segment, VAL-segment-then-HOLD-segment concatenation (D1-A block-convention
amendment, final block only; manifest-count arithmetic: TRAIN 2187 [0..2186] + VAL 729
[2187..2915]; HOLD base 2916 + P20Q DEV 640 = HOLD remainder 3556..3644) → ONE block at
N=32768 (128 frames; 32768 pairs). DEV frames SHALL be disjoint from the counts/build
frames (build ⊂ 2M TRAIN 0..2186; declared frame sets, S2-ii). Exclusion is enforced by
the frozen §4 gate family (a)→(g): merged cross-file 2M identity first (never frame
numbers alone), then dual-segment intra-file containment, then consumed-1M, consumed-1.5M,
consumed-2M exclusions incl. the DEV∩build-frames declaration, then reuse-prior +
reuse-alt + frozen-A-order + K-literal + spike-derivation-program pins, then
merged-frame-set-identity (exact 128-frame list rule) + order-position-identity +
tag-domain pins. Cross-packet same-block tuning is forbidden. 1.5M × 2M mixing stays
forever forbidden.

## Endpoints, arms, carried scalars, and mandatory IR-1..IR-4 + uncapped IR-5

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`, `pair_exact` and
tag-verified `exact` per record, with `undetected` isolated (never success) and
`decode_failed` / `nonfinite` / `resource_abort` via the P20A resource path. `O` carries
oracle provenance, is deployable=false, and is excluded from every operational aggregate.
Outcome labels are descriptive only (no recovery threshold has an empirical basis at n=1):
any exact count is COMPLETE when integrity holds and is explicitly NOT read as a recovery
rate; there is NO recovery, FER, superiority, H2-verdict, or qualification threshold. No
A→B transition cells are computed (counting vocabulary is out of scope by D2 form); the
§16 branch decision and the H2 decision belong to main-thread analysis after acceptance,
never to this packet's label.

All NINE X09-R1/P20O scalars SHALL be carried per record with P20O semantics (true cells
under the record's own arm table AND the record's OWN order — frozen-A on A/O, spike on
B; failing fields null unless `first_error_layer == L2`; prefix-wide means on every
completed record; R=8 window; ninth U-domain scalar PRESENT).

IR-1..IR-4 SHALL ALL be PRESENT per record (bounded/recording-only/post-decode/
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
+ `ir4_topk_in_prefix` + `ir4_topk_ranks` (k=16 frozen; every completed record).
IR-5 SHALL be UNCAPPED (d9, the D2 opening of the P20Q 4096 cap): per record EXACTLY three
binary little-endian series — 32768 float32-LE true-cell hazard bits in natural block
order (131072 B) + 32768 uint8 X-domain in-prefix flags (32768 B) + 32768 uint8 U-domain
flags (32768 B) — plus the `ir5full-v1` manifest linkage (per-file sha256 + shape + dtype
+ endianness + order-identity + record linkage); binary `.bin` + JSON manifest ONLY (no
text-JSON float dumps, no npz/npy/parquet); per-record ~192 KiB ≤ ~400 KB, root ~576 KiB
≤ ~1.5 MB, every committed file ≤ ~2 MB; the JSONL records carry manifest REFERENCES
(file names + digests), never inline float arrays.
Writer code point: successor module `l2_mechanism_probe_2m.py::_ir5_full_block_writer`,
called post-decode (after tag scoring) alongside the nine carried scalars and the IR-1..IR-4
recorder (the P20Q `_ir_hazard_diagnostics` code point is the carried-over callsite
pattern). Truth-isolation boundary (normative): truth and arm tables enter the writers for
RECORDING ONLY after all SC calls complete; outputs never enter any metric builder,
decoder call, disclosure or order decision (pinned by a focused sentinel test).

The H2 decision quantities the accepted run must supply are pre-registered here with NO
outcome asserted: full-block hazard series tables (per-record full-32768 mean/tail mass
under the record's own order, from the uncapped IR-5 bins); spike-order coverage of the
byte-exact disclosed-set mismatch positions by hazard-rank distribution under each order
(purely positional); IR-1 tails under both orders (prefix vs outside tail-mass contrast
A vs B); IR-4-style concentration at full-block scope (in-prefix fractions over top-128 /
top-1024 hazard ranks from the uncapped series, per record's own order); plus the nine
carried scalars (arm-specific order digests) and the byte-exact A-vs-B disclosed-set delta
table. These inform H2a–H2e in main-thread analysis after acceptance; they are not FER and
not thresholds.

## One-shot semantics

Single attempt, no rerun, no reuse/parameter change after preregistration; resource aborts
preserve evidence and accounting and BLOCK, never succeed. Reads are split-counted:
counts-calibration opens 0/0 at every stage (reuse + deterministic permutation; the V25
counts NPZ never opened/statted/listed) + merged-DEV open 1/1 reserved for Stage B
(parquet, consumed at the first merged-DEV content open); 1M 0; 1.5M 0; 2M-non-DEV 0 in
every form (HOLD tail + all 1.5M remainders counted never-decoded); any reopen, new
derivation/sampling, or DEV refit is forbidden. The SCL entry gate is unchanged. Tag
domains are new P20S (master 2026092360, prefix
`nbpolar-p20s-mechanism-probe-2m-seed`); focused test seeds are `2026092361..2026092367`
(Stage-A provenance only); there are NO derivation seeds (the frozen permutation is
deterministic; zero sampling at every stage; genie 0+0).

## Scope

P20S SHALL use zero protected opens + injected data + the P20O worktree artifacts +
the single worktree-prior spike permutation + temporary roots in Stage A with merged-DEV
0/1 at close, zero 1M-pool / any-1.5M-split / any-2M-TRAIN/VAL-DEV/HOLD-DEV open/stat/
listing, zero sampling/genie calls at every stage, zero real-data decoder execution and
zero Stage-B output root. It SHALL NOT re-derive prior/alt/orders from protected counts;
carry any 1.5M K/order/prior absolute or recompute K from alt-H (S2-i; replay only); use
lambda anywhere; change the field, transform, SC arithmetic, floor value, 2M L1 tables,
frozen-A orders, disclosed sizes, verification tag semantics, outcome precedence or
scientific status; add SCL, a new kernel/model/schema, a fourth arm, a second
construction, a construction sweep, a bounded search, a second order beyond the single
spike set, or a disclosure change; freeze any IR field as absent; reuse the closed
blocks, the consumed 1M pool, any consumed 1.5M range, consumed 2M ranges, HOLD tail
3595..3644 beyond counting, or 1.5M remainders beyond counting; derive on or tune with
DEV; decide H2 in-packet; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push.
Honest scope: a single merged-block (2M VAL-remainder tail + HOLD-remainder head)
mechanism probe of one local-spike L2-order position rule under the frozen α1
construction at frozen disclosure with full-block hazard geometry recorded; descriptive
geometry only; the merged DEV block is consumed by this packet; the HOLD tail 3595..3644
and all 1.5M remainders stay untouched; no recovery claim, no H2 verdict; the H2 decision
is analysis, not a block result.

(End of file)
