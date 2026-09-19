# Delta spec — P20E +1024 confirmation on new blocks

## Zero-tuning carry-over semantics

P20E varies NOTHING against the frozen P20C point: prior (Model-F
concentration path), `1e-15` floor, P16 construction order (`K1=319`
base L1 set; B1 `K2=7516` by the SAME frozen-order-prefix +1024 step),
per-arm disclosure caps, kernel, representation, transform and greedy SC
SHALL be carried over byte-identical across all three arms. The only
deliberate differences from P20C are the new-block population and the
new P20E tag domain — both provenance/identity changes, never algorithm
changes. Any other deviation is a packet violation, not a tuning
choice.

## Confirmation-step freeze

`B1_L2plus` SHALL disclose exactly ΔK2 = +1024 L2 symbols beyond the
frozen base (K2 6492 → 7516; K_total 6811 → 7835) by
FROZEN-ORDER-PREFIX EXTENSION: the disclosed L2 set is the first 7516
positions of the frozen P16 L2 order. Positions are fixed by the
construction file and SHALL never be selected on closed blocks, the
consumed VAL pool, the consumed P20C DEV blocks, or the new DEV data.
The step SHALL be frozen before execution and unchanged after; there
SHALL be no tag-guided selection, no evidence reuse, no post-hoc
step-picking, and no second step (`B1b`) without a new packet.
`B1_L2plus` SHALL invoke the same 2 SC calls and 1 tag per block as
`B0_sc_base`.

## Population and closed/consumed-data rule

The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K,
floor, order, decoder, disclosure step, or any successful point. The
P20B VAL pool (frames 1200..1599, including remainder 1584..1599) is
CONSUMED and SHALL NOT supply P20E blocks. The P20C DEV blocks (frames
0..383) are CONSUMED and SHALL NOT supply P20E blocks. Stage B SHALL
run on the declared new-block population only: the same-file TRAIN
subrange of the same registered 1M source (DEV blocks 384..511 /
512..639 / 640..767 at N=32768; remainder 768..1199 never used), which
is disjoint from ALL THREE forbidden ranges by a triple fail-closed
gate (consumed P20C DEV first, then consumed VAL, then closed HOLD).
Cross-packet same-block tuning is forbidden.

## Disclosure cap

Per-arm key-dependent disclosure is carried over unchanged from P20C
and frozen: 34119 bits base operational (`5*(319+6492)+64`), 39239 bits
`B1_L2plus` (`5*(319+7516)+64`, delta exactly +5120 vs base), 32524 bits
oracle control (`5*6492+64`), plus one 64-bit tag per record; public
control is 327743 bits per tag. The caps sit at 34119/327680 (~10.41%)
and 39239/327680 (~11.97%) of raw input bits per block — far below raw.
An independent literal transcript recount SHALL match with zero
mismatch or the gate BLOCKS. Sample-CE-normalized ratios are
descriptive and are NOT qualification efficiency.

## Endpoints and arms

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`,
`pair_exact` and tag-verified `exact` per record, with `undetected`
isolated (never success) and `decode_failed` / `nonfinite` /
`resource_abort` via the P20A resource path. `B1` records SHALL carry
the frozen disclosure triple (`l2_delta_k2_applied`,
`l2_disclosure_rule`, `key_bit_delta_vs_base`).
`B2_true_l1_diagnostic` carries oracle provenance, is deployable=false,
and is excluded from every operational aggregate. Outcome labels are
descriptive only: any exact count is COMPLETE when integrity holds;
there is NO recovery, FER, superiority or qualification threshold.
Repeat-recovery (`b1_restored_count` on the new blocks) and maintenance
counts are development signals, never pass/fail verdicts; the
positive/negative branch decision belongs to later planning, never to
this packet's label.

## One-shot semantics

Single attempt, no rerun, no seed/disclosure-step change after
preregistration; resource aborts preserve evidence and accounting and
BLOCK, never succeed. The SCL entry gate is unchanged: this
confirmation unlocks nothing by itself. Tag domains are new P20E
(master 2026092100, prefix `nbpolar-p20e-plus1024-confirmation-seed`).

## Scope

P20E SHALL use injected data and temporary roots in Stage A with zero
protected reads and zero real-data execution. It SHALL NOT change the
field, transform, SC arithmetic, prior, floor, construction order
(including the carried-over prefix-extension rule itself), disclosure
beyond the frozen carried-over step, verification tag semantics,
outcome precedence or scientific status; add SCL, a new
kernel/model/schema, a second disclosure step or an alternative
construction; reuse the closed blocks, the consumed VAL pool or the
consumed P20C DEV blocks; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push.
