# Delta spec — P20C L2 disclosure backoff

## Single-factor semantics

P20C varies exactly one factor against the frozen operational baseline:
ONE preregistered L2 disclosure step of +1024 symbols by
frozen-order-prefix extension. Prior (Model-F concentration path),
`1e-15` floor, P16 construction order (`K1=319` base L1 set), kernel,
representation, transform and greedy SC SHALL be identical across all
three arms. Any deviation is a packet violation, not a tuning choice.

## Disclosure-step freeze

`B1_L2plus` SHALL disclose exactly ΔK2 = +1024 L2 symbols beyond the
frozen base (K2 6492 → 7516; K_total 6811 → 7835) by
FROZEN-ORDER-PREFIX EXTENSION: the disclosed L2 set is the first 7516
positions of the frozen P16 L2 order. Positions are fixed by the
construction file and SHALL never be selected on closed blocks, the
consumed VAL pool, or DEV data. The step SHALL be frozen before
execution and unchanged after; there SHALL be no tag-guided selection,
no evidence reuse, no post-hoc step-picking, and no second step
(`B1b`) without a new packet. `B1_L2plus` SHALL invoke the same 2 SC
calls and 1 tag per block as `B0_sc_base`.

## Population and closed/consumed-data rule

The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K,
floor, order, decoder, disclosure step, or any successful point. The
P20B VAL pool (frames 1200..1599, including remainder 1584..1599) is
CONSUMED and SHALL NOT supply P20C blocks. Stage B SHALL run on the
declared same-file TRAIN development population (frames 0..1199 of the
same registered 1M source; DEV blocks 0..127 / 128..255 / 256..383;
remainder 384..1199 never used), which is disjoint from BOTH the closed
range and the consumed pool by a dual fail-closed gate. Confirmation on
new blocks/sessions is a later packet, never this one.

## Disclosure cap

Per-arm key-dependent disclosure is preregistered and frozen: 34119
bits base operational (`5*(319+6492)+64`), 39239 bits `B1_L2plus`
(`5*(319+7516)+64`, delta exactly +5120 vs base), 32524 bits oracle
control (`5*6492+64`), plus one 64-bit tag per record; public control is
327743 bits per tag. The caps sit at 34119/327680 (~10.41%) and
39239/327680 (~11.97%) of raw input bits per block — far below raw. An
independent literal transcript recount SHALL match with zero mismatch
or the gate BLOCKS. Sample-CE-normalized ratios are descriptive and are
NOT qualification efficiency.

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

## One-shot semantics

Single attempt, no rerun, no seed/disclosure-step change after
preregistration; resource aborts preserve evidence and accounting and
BLOCK, never succeed. The SCL entry gate is unchanged: this backoff
informs its information axis but unlocks nothing by itself.

## Scope

P20C SHALL use injected data and temporary roots in Stage A with zero
protected reads and zero real-data execution. It SHALL NOT change the
field, transform, SC arithmetic, prior, floor, construction order
(except the frozen prefix-extension rule itself), disclosure beyond the
single frozen step, verification tag semantics, outcome precedence or
scientific status; add SCL, a new kernel/model/schema, a second
disclosure step or an alternative construction; reuse the closed blocks
or the consumed VAL pool; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push.
