# Delta spec — P20H per-session-calibration +1024 confirmation on type2_1p5M_20260121_183806

## Calibration-program freeze (the single deliberate delta vs P20G)

P20H varies exactly ONE input against the frozen P20C/P20E/P20F/P20G
point: the prior is per-session calibrated on 1.5M TRAIN counts by the
frozen §3 program (Stage A, DEV-zero-contact, read-only in Stage B).
The program is isomorphic with the accepted P0/P2 Model-F concentration
fitting program (same formula / smoothing / flow, banned per-cell twin
excluded): `p_global[a] = sum_b counts[a,b]/sum counts`,
`n_b[b] = sum_a counts[a,b]`,
`f[a,b] = (counts[a,b] + lambda*p_global[a])/(n_b[b]+lambda)` with the
frozen lambda `137.3823795883264` (accepted fitting-program constant
procedure output, no hand-fill, no DEV influence, no per-session search),
accepted `derive_p1`/`derive_p2` under packing `A = 32*U1 + U2`,
joint-Bob conditioning `FULL_BOB_ONLY`, fixed `1e-15` floor before SC.
Input is 1.5M TRAIN counts ONLY; 1.5M DEV/VAL/HOLD, any 1M split, the
reserved 2M file and the Model-F CAL artifact are forbidden inputs.
Output is the digest-pinned `calibrated_prior.npz` plus the recalibrated
H1/H2/TOTAL literals replacing the 1M literals for the
`target_population_contract` gate. Threshold/formula/input-digest/
output-literals are ALL frozen in Stage A; Stage B verifies digest match
read-only before any SC call and refuses on mismatch. No
refit/resmoothing/relambda after any DEV contact. Calibration-vs-tuning
is adjudicated at Pre-EXECUTE under §3 (i)–(iv): TRAIN-only input, DEV
zero contact before freeze, isomorphic program, frozen read-only
product; else BLOCKED-to-planner with no Stage-B fallback.

## Extension-step freeze

`B1_L2plus` SHALL disclose exactly ΔK2 = +1024 L2 symbols beyond the
frozen base (K2 6492 → 7516; K_total 6811 → 7835) by
FROZEN-ORDER-PREFIX EXTENSION: the disclosed L2 set is the first 7516
positions of the frozen P16 L2 order. Positions are fixed by the
construction file and SHALL never be selected on closed blocks, the
consumed 1M pool, the reserved 2M file, or the new DEV data. The step
SHALL be frozen before execution and unchanged after; there SHALL be no
tag-guided selection, no evidence reuse, no post-hoc step-picking, and
no second step (`B1b`) without a new packet. `B1_L2plus` SHALL invoke
the same 2 SC calls and 1 tag per block as `B0_sc_base`.

## Population and closed/consumed-data rule

The three P18/P19 HOLD blocks (1M frames 1600..1983), the P20B VAL pool
(1M frames 1200..1599), the P20C DEV blocks (1M frames 0..383), the
P20E DEV blocks (1M frames 384..767) and the P20F DEV blocks (1M frames
768..1151) are CONSUMED or CLOSED and SHALL NOT supply P20H blocks; the
ENTIRE 1M pool is fail-closed against P20H DEV selection; the reserved
2M session file SHALL NOT be opened, statted, listed, or read under this
packet. Stage B SHALL run on the declared population only: the FIRST
384 TRAIN frames of the 1.5M file in (frame_id, pair_idx) order (frozen
TRAIN base 0: DEV blocks 0..127 / 128..255 / 256..383 at N=32768;
remainder 384..1659 counted, never decoded). Exclusion is enforced by a
fail-closed triple gate in frozen order: (a) CROSS-FILE gate — the DEV
content-open path plus size/sha pin must match the 1.5M pairs identity
(source-tag + digest pin is the identity, never frame numbers alone);
any 1M path, any 2M path, or any digest/size mismatch refuses before
any SC call; (b) INTRA-FILE gate — DEV ranges must overlap NONE of the
1.5M VAL/HOLD frame sets (1660..2212 / 2213..2766), else the run refuses
before any protected content open; (c) CALIBRATION-IDENTITY gate — the
Stage-B prior/table/literal digest must equal the Stage-A frozen
calibration digest before any SC call, else the run refuses (this
replaces P20G's failed 1M-literal gate). Cross-packet same-block tuning
is forbidden.

## Disclosure cap

Per-arm key-dependent disclosure is carried over unchanged from
P20C/P20E/P20F/P20G and frozen: 34119 bits base operational
(`5*(319+6492)+64`), 39239 bits `B1_L2plus` (`5*(319+7516)+64`, delta
exactly +5120 vs base), 32524 bits oracle control (`5*6492+64`), plus
one 64-bit tag per record; public control is 327743 bits per tag. The
caps sit at 34119/327680 (~10.41%) and 39239/327680 (~11.97%) of raw
input bits per block — far below raw. An independent literal transcript
recount SHALL match with zero mismatch or the gate BLOCKS.
Sample-CE-normalized ratios are descriptive and are NOT qualification
efficiency.

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
Repeat-recovery (`b1_restored_count` on the calibrated new-session
blocks) and maintenance counts are development signals, never pass/fail
verdicts; the positive/negative branch decision belongs to later
planning, never to this packet's label.

## One-shot semantics

Single attempt, no rerun, no seed/disclosure-step change after
preregistration; resource aborts preserve evidence and accounting and
BLOCK, never succeed. Reads are split-counted: one counts-calibration
open (Stage A, 1.5M TRAIN NPZ array) plus one DEV open (Stage B,
parquet); HOLD reads stay 0; any reopen, second calibration, or DEV
refit is forbidden. The SCL entry gate is unchanged: this confirmation
unlocks nothing by itself. Tag domains are new P20H (master 2026092220,
prefix `nbpolar-p20h-per-session-calibration-seed`).

## Scope

P20H SHALL use injected data and temporary roots in Stage A with exactly
one declared counts-calibration open and zero 1.5M DEV/VAL/HOLD content
opens or stats, zero 1M-pool or reserved-2M open/stat/listing, zero
real-data decoder execution and zero Stage-B output root. It SHALL NOT
change the field, transform, SC arithmetic, floor value, construction
order (including the carried-over prefix-extension rule itself),
disclosure beyond the frozen carried-over step, verification tag
semantics, outcome precedence or scientific status; add SCL, a new
kernel/model/schema, a second disclosure step or an alternative
construction; reuse the closed blocks, the consumed 1M pool (any split,
any subrange) or the reserved 2M file; calibrate on DEV or refit after
any DEV contact; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push.
