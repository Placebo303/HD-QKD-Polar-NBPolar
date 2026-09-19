# Delta spec — P20B bounded-search diagnostic

## Single-factor semantics

P20B varies exactly one factor against the frozen operational baseline:
a preregistered bounded search around the frozen greedy SC path. Prior
(Model-F concentration path), `1e-15` floor, P16 construction
(`K1=319`/`K2=6492`, N=32768), base disclosure, kernel, representation,
transform and SC arithmetic SHALL be identical across all three arms. Any
deviation is a packet violation, not a tuning choice.

## Search freeze

The search SHALL rescore at most `M=8` candidates including the greedy
path (`P20B-NBHD-1`): the greedy hard path plus single-symbol U-domain
divergent alternates at undisclosed coordinates only, ranked by ascending
SC margin gap with deterministic tie-break (layer L1 < L2, coordinate
ascending), each alternate re-encoded with the frozen transform.
Rescoring is argmin total NLL bits under the same floored tables as SC
(greedy wins ties); no tag and no truth enter selection; exactly one
final tag verifies the selected label afterwards. The bound,
neighborhood and scoring model SHALL be frozen before execution and
unchanged after; there SHALL be no tag-guided candidate selection and no
evidence reuse. `S1_bounded_search` SHALL invoke the same 2 SC calls and
1 tag per block as `S0_sc_base` (rescore-only: no extra SC).

## Population and closed-data rule

The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K,
floor, order, decoder, search bound/neighborhood, or any successful
point. Stage B SHALL run on the declared VAL development population
(frames 1200..1599 of the same registered 1M source; DEV blocks
1200..1327 / 1328..1455 / 1456..1583; remainder 1584..1599 unused), which
is disjoint from the closed range by a fail-closed gate. Confirmation on
new blocks/sessions is a later packet, never this one.

## Disclosure cap

Per-block key-dependent disclosure SHALL NOT increase over the frozen
base: 34119 bits operational (`5*(319+6492)+64`), 32524 bits oracle
control (`5*6492+64`), plus one 64-bit tag per record; public control is
327743 bits per tag. The cap sits at 34119/327680 (~10.41%) of raw input
bits per block. An independent literal transcript recount SHALL match
with zero mismatch or the gate BLOCKS. Sample-CE-normalized ratios are
descriptive and are NOT qualification efficiency.

## Endpoints and arms

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`,
`pair_exact` and tag-verified `exact` per record, with `undetected`
isolated (never success) and `decode_failed` / `nonfinite` /
`resource_abort` via the P20A resource path. `S2_true_l1_diagnostic`
carries oracle provenance, is deployable=false, and is excluded from
every operational aggregate. Outcome labels are descriptive only: found
counts 0 and >0 are both COMPLETE when integrity holds; there is NO
recovery, FER, superiority or qualification threshold.

## One-shot semantics

Single attempt, no rerun, no seed/bound/neighborhood change after
preregistration; resource aborts preserve evidence and accounting and
BLOCK, never succeed. The SCL entry gate is unchanged: this diagnostic
informs its conditions but unlocks nothing by itself.

## Scope

P20B SHALL use injected data and temporary roots in Stage A with zero
protected reads and zero real-data execution. It SHALL NOT change the
field, transform, SC arithmetic, prior, floor, construction, disclosure,
verification tag semantics, outcome precedence or scientific status; add
SCL, a new kernel/model/schema, a disclosure backoff or an alternative
construction; overwrite `results/` or `comparison_bench/outputs_comparison/`;
or commit/push.
