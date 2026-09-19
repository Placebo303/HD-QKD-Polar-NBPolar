# Delta spec — P20K L1-dose-512 +512 single-factor on type2_1p5M_20260121_183806

## Prior reuse (zero new calibration)

P20K varies exactly ONE input against the frozen P20H point: L1
disclosure +ΔK1=512 via the frozen order-prefix rule. The prior is
carried over read-only from the P20H Stage-A product
(`per_session_calibration/calibrated_prior.npz` under
`.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/`):
canonical digest
`e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
(sorted-key `key + shape + dtype + C-order bytes` sha256), lambda pin
`137.3823795883264`, floor pin `1e-15`, exact key set
(`counts_ab`, `f_prior`, `p1`, `p2`, `p_b`, `lambda_star`,
`floor_value`, `h1`, `h2`, `h_total`), recalibrated literals H1
`2.006647056368773` / H2 `1.9017235959286112` / TOTAL
`3.908370652297384` (recomputed H1/H2 within 1e-12). Stage B loads the
frozen file read-only behind a calibration-identity digest gate and
refuses on mismatch before any SC call. The V25 counts NPZ is NEVER
opened in this packet (no counts loader, no smoothing import in the
runner). FORBIDDEN at any stage: prior refit/resmoothing/relambda,
floor change, calibration on DEV, any fitting input (1.5M DEV/VAL/HOLD,
P20H DEV 0..383, P20I DEV 384..767, P20J DEV 768..1151, any 1M split,
reserved 2M, Model-F CAL artifact). This packet performs zero
calibration opens (split-counted counts 0/0).

## Extension-step freeze

`E1_L1plus512` SHALL disclose exactly ΔK1 = +512 L1 symbols beyond the
frozen base (K1 319 → 831; K_total 6811 → 7323; K2 stays 6492) by
FROZEN-ORDER-PREFIX EXTENSION: the disclosed L1 set is the first 831
positions of the SAME frozen P16 L1 order — isomorphic with the
accepted `l2_order[:k2]` rule, no reselection, no re-ranking, on ANY
data (P20K DEV, P20J DEV, P20I DEV, P20H DEV, closed 1M ranges, 2M).
Positions are fixed by the construction file and SHALL never be
selected on closed blocks, the consumed 1M pool, P20H DEV 0..383, P20I
DEV 384..767, P20J DEV 768..1151, or the new DEV data. The step doubles
the P20J +256 L1 dose (K1 575 → 831), completing the +128/+256/+512
doubling chain; the P20J `D1_L1plus` arm (K1 319→575) is the
second-dose precedent of this lineage. The step SHALL be frozen before
execution and unchanged after; there SHALL be no tag-guided selection,
no evidence reuse, no post-hoc step-picking, and no second tier
(`E1b`) without a new packet. `E1_L1plus512` SHALL invoke the same 2
SC calls and 1 tag per block as `E0_sc_base`.

## Population and closed/consumed-data rule

The three P18/P19 HOLD blocks (1M frames 1600..1983), the P20B VAL pool
(1M frames 1200..1599), the P20C/P20E/P20F DEV blocks (1M 0..383 /
384..767 / 768..1151), the P20H DEV blocks (1.5M TRAIN 0..383), the
P20I DEV blocks (1.5M TRAIN 384..767) and the P20J DEV blocks (1.5M
TRAIN 768..1151) are CONSUMED or CLOSED and SHALL NOT supply P20K
blocks; the ENTIRE 1M pool is fail-closed against P20K DEV selection;
the reserved 2M session file SHALL NOT be opened, statted, listed, or
read under this packet (pristine by non-access). Stage B SHALL run on
the declared population only: the NEXT 384 TRAIN frames of the 1.5M
file in (frame_id, pair_idx) order after the consumed P20H DEV prefix,
the consumed P20I DEV segment and the consumed P20J DEV segment
(frozen TRAIN base 0: DEV frames 1152..1535 → DEV blocks 1152..1279 /
1280..1407 / 1408..1535 at N=32768; remainder 1536..1659, 124 frames /
31744 pairs, counted, never decoded). Exclusion is enforced by a
fail-closed sextuple gate in frozen order: (a) CROSS-FILE gate — the
DEV content-open path plus size/sha pin must match the 1.5M pairs
identity (size 1869178 B, sha `ca351e52…a06b` provenance pin;
source-tag + digest pin is the identity, never frame numbers alone);
any 1M path, any 2M path, or any digest/size mismatch refuses before
any SC call; (b) INTRA-FILE gate — DEV ranges must overlap NONE of the
1.5M VAL/HOLD frame sets (1660..2212 / 2213..2766, VAL checked first),
else the run refuses before any protected content open; (c) P20H-DEV
EXCLUSION gate — DEV ranges must overlap NONE of P20H DEV 0..383, else
the run refuses before any protected content open; (d) P20I-DEV
EXCLUSION gate — DEV ranges must overlap NONE of P20I DEV 384..767,
else the run refuses before any protected content open; (e) P20J-DEV
EXCLUSION gate — DEV ranges must overlap NONE of P20J DEV 768..1151,
else the run refuses before any protected content open; (f)
CALIBRATION-IDENTITY gate — the Stage-B prior/table/literal digest
must equal the Stage-A frozen digest before any SC call, else the run
refuses. Cross-packet same-block tuning is forbidden.

## Disclosure cap

Per-arm key-dependent disclosure is preregistered and frozen: 34119
bits base operational (`5*(319+6492)+64`), 36679 bits `E1_L1plus512`
(`5*(831+6492)+64`, delta exactly +2560 = 5·512 vs base), 32524 bits
oracle control (`5*6492+64`), plus one 64-bit tag per record; public
control is 327743 bits per tag (`10*32768+63`). Planned totals if all
invoked: key 309966 = 3*34119 + 3*36679 + 3*32524 (operational 212394
+ oracle 97572); public 2949687 = 9*327743. The caps sit at
34119/327680 (~10.41%) and 36679/327680 (~11.19%) of raw input bits per
block — far below raw. An independent literal transcript recount SHALL
match with zero mismatch or the gate BLOCKS. Sample-CE-normalized
ratios are descriptive and are NOT qualification efficiency.

## Endpoints and arms

Runners SHALL separate `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`,
`pair_exact` and tag-verified `exact` per record, with `undetected`
isolated (never success) and `decode_failed` / `nonfinite` /
`resource_abort` via the P20A resource path. `E1` records SHALL carry
the frozen disclosure triple (`l1_delta_k1_applied`,
`l1_disclosure_rule`, `key_bit_delta_vs_base`).
`E2_true_l1_diagnostic` carries oracle provenance, is
deployable=false, and is excluded from every operational aggregate.
Outcome labels are descriptive only: any exact count is COMPLETE when
integrity holds; there is NO recovery, FER, superiority or
qualification threshold. L1-restoration (`e1_restored_count`: E0 fail →
E1 exact on the new-segment blocks) and maintenance counts are
development signals, never pass/fail verdicts; the §16 branch decision
belongs to later planning, never to this packet's label.

## One-shot semantics

Single attempt, no rerun, no seed/disclosure-step change after
preregistration; resource aborts preserve evidence and accounting and
BLOCK, never succeed. Reads are split-counted continuing P20J mode:
counts-calibration opens 0/0 (prior reuse only via a worktree-file
digest check, never an NPZ open) + DEV open 1/1 reserved for Stage B
(parquet, consumed at the first DEV content open); HOLD reads stay 0/1
untouched; any reopen, new calibration, or DEV refit is forbidden. The
SCL entry gate is unchanged: this diagnostic unlocks nothing by
itself. Tag domains are new P20K (master 2026092250, prefix
`nbpolar-p20k-l1-dose-512-1p5m-seed`).

## Scope

P20K SHALL use injected data and temporary roots in Stage A with zero
protected content opens (counts 0 + DEV 0 + HOLD 0 at close; the §3
digest check is a worktree-file read), zero 1M-pool or reserved-2M
open/stat/listing, zero real-data decoder execution and zero Stage-B
output root. It SHALL NOT change the field, transform, SC arithmetic,
floor value, construction order (including the frozen prefix-extension
rules themselves), disclosure beyond the frozen +512 tier,
verification tag semantics, outcome precedence or scientific status;
add SCL, a new kernel/model/schema, a second L1 tier, a second L2 step
or an alternative construction; reuse the closed blocks, the consumed
1M pool (any split, any subrange), P20H DEV 0..383, P20I DEV 384..767,
P20J DEV 768..1151 or the reserved 2M file; calibrate on DEV or refit
after any DEV contact; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push.
