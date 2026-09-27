# Tasks: `nbpolar-op-k1-ramp-k550`

Status: **executed and reviewed (Tier-X synthetic; descriptive, non-claim).**
Every task below is carried by artifacts under `workspace/`.

- [x] K1-T1 — Adjudicate and record the next-probe decision (DP-K1..K5) in the packet `STATUS.yaml` `adjudications:` section; select the `operational k1 dose ramp` theme and do **not** consume bounded-list candidates C2/C3/C4.
- [x] K1-T2 — Freeze the bounded 5-point grid `k1 ∈ {10,80,160,320,450}`, `k2=550`, `d1=worst_k(H1,k1)` per point, `d2=worst_k(H2,550)`, design seed `2026092600` / `DESIGN_MC=128` unchanged, run seeds `2026092701..2026092702`, 32 blocks per point, single arm, wall ≤600 s / RSS ≤1 GiB.
- [x] K1-T3 — Record the bookkeeping-only cross-check (`disclosed=5*(k1+k2)`; k1=10 anchor 2800 / f≈2.9344139789; k1=160 ⇒ 3550 matching the `k2-dose-ramp` 3550 point) and the prohibition on calling any k1 point an efficiency operating point.
- [x] K1-T4 — Record the OpenSpec change (`proposal`/`design`/`tasks`) with the C1 Scope-OUT boundary carried over verbatim plus the "k1 is a dose variable, not an efficiency claim" clause.
- [x] K1-T5 — Derive `run.py` mechanically from `workspace/probes/l2-singlefactor-c1-k550/run.py`; allow only: `K1_GRID`, per-config `d1`, identifiers/seeds/output paths, removal of the CAND arm and overlap gate (retaining `undetected` isolation STOP and budget STOP), and per-k1 result recording.
- [x] K1-T6 — Freeze the three-line `prereg.md` with the exact WSL C command.
- [x] K1-T7 — Prepare the packet `{STATUS.yaml,FREEZE_REVIEW.md,EXECUTION_TRANSCRIPT.md,FOCUSED_REVIEW.md,DUPLICATE_RUN_NOTE.md}` with the `authorizations:` basis and an explicit "touches no real data" statement.
- [x] K1-T8 — Main-thread freeze review (`FREEZE_REVIEW.md`): 7/7 PASS, two non-blocking notes (HN rounding 954.18 vs in-run 954.1939276637445; per-k1 Toeplitz stream via `bidx`). No FAIL.
- [x] K1-T9 — One-shot execution after verifying target-output absence: wall 118.757 s, RSS 216719360 B, cells 10/10, `reruns=0`; per-point operational exact `{10:0, 80:30, 160:32, 320:32, 450:32}` of 32 each; oracle 32/32 at every point.
- [x] K1-T10 — Independent focused numerical review + main-thread descriptive adjudication (`FOCUSED_REVIEW.md`): joined with the fine probe, operational exact first leaves zero in `k1∈(10,20]` and saturates at `k1=160`.
- [x] K1-T11 — Fine interpolation probe `op-k1ramp-fine-base` at `k1 ∈ {20,40,60}` on identical seeds and identical shared `d2`: freeze review → one-shot (wall 85.682 s, cells 6/6) → focused review; per-point operational exact `{20:2, 40:14, 60:24}`.
- [x] K1-T12 — Record the duplicate one-shot incident (`DUPLICATE_RUN_NOTE.md`): the same frozen configuration was also executed once in `workspace/probes/op-k1-ramp-k550/` by a concurrent automation tick; totals match, kept as an independent cross-check, never as a second result.
- [x] K1-T13 — Split-at-fixed-total probe `op-k1k2-split-560`: `k1+k2=560` constant (disclosed 2800 bits at every point), `k1 ∈ {10,40,80,160,240,320,400,480}`, `k2 = 560-k1`, `d1=worst_k(H1,k1)` and `d2=worst_k(H2,k2)` both per point, 32 blocks/point, 256 blocks total. Tests **allocation**, not dose magnitude. Freeze review cleared the per-point `d2` semantic change (DP-S3) after one `RETURN_TO_AUTHORING` round (fatal `%`-format mismatch fixed; AST check zero mismatches).
- [x] K1-T14 — One-shot execution (wall 159.388 s, RSS 215060480 B, cells 16/16) + focused numerical review + main-thread descriptive adjudication: operational exact `0/14/28/1/0/0/0/0` of 32 for k1=10..480, oracle `32/32/30/1/0/0/0/0`; single-peaked and non-monotone with the peak at `k1≈80 (k2≈480)`; both ends collapse.

- [x] K1-T15 — Total-scale probe `op-kratio-scale` at the FIXED allocation ratio `k1:k2 = 1:6` (a derived choice from the peak band of K1-T13, declared as such): `K_TOTALS=(560,448,336,280,224)` ⇒ `k1/k2 = 80/480, 64/384, 48/288, 40/240, 32/192`, disclosed `2800/2240/1680/1400/1120` bits, 32 blocks/point, 160 blocks total. Freeze review cleared it after fixing one factual-error string; the AST placeholder/argument check reported zero mismatches.
- [x] K1-T16 — One-shot execution (wall 115.022 s, RSS 215396352 B, cells 10/10) + focused numerical review + adjudication: operational exact `28/0/0/0/0` of 32 and oracle `30/0/0/0/0`; the lowest total with non-zero operational success is 560 (2800 bits). Recorded as **same-ratio scaling only**, explicitly not establishing low-`f` unreachability.

- [x] K1-T17 — Bounded low-total ratio search `op-lowtotal-ratio`: totals 448 and 336 x four k1 shares each (ratios ~1:13, 1:6, 1:3.67, 1:2.5), 8 points, 256 blocks. Review flagged and fixed an aggregation-key collision (`k1=96` occurs at both totals ⇒ keyed by `f_label`) and a stale `a3_split_rule` text.
- [x] K1-T18 — First launch ended in `execution_error` (string placeholder removed by a text fix; no records/points/verdict). Error record preserved; defect fixed; a single measurement launch followed. Focused review + adjudication: operational exact 1/32 at `T448_k1_32_k2_416`, zero at the other seven points.

- [x] K1-T19 — Peak-band refinement `op-peak-refine` at fixed total 560: `k1 ∈ {60,100,120}` ⇒ `k2 = 500/460/440`, 32 blocks/point, 96 blocks. Freeze review PASS first round (no dangling names, all formatting consistent, aggregation key unique).
- [x] K1-T20 — One-shot execution (wall 84.256 s, RSS 215613440 B, cells 6/6) + focused review: operational exact `24/26/20` of 32 and oracle `32/26/20`; joined with K1-T13 this brackets the peak as a plateau over `k1 ∈ [60,120]` with its top at `k1≈80–100`.

## Outcome artifact map

| item | path |
|---|---|
| dose ramp | `workspace/probes/op-k1ramp-k550-base/{prereg.md,run.py,results.json}` |
| fine interpolation | `workspace/probes/op-k1ramp-fine-base/{prereg.md,run.py,results.json}` |
| fixed-total allocation | `workspace/probes/op-k1k2-split-560/{prereg.md,run.py,results.json}` |
| total-scale at fixed ratio | `workspace/probes/op-kratio-scale/{prereg.md,run.py,results.json}` |
| low-total ratio search | `workspace/probes/op-lowtotal-ratio/{prereg.md,run.py,results.json,results.execution_error_attempt1.json}` |
| packets | `workspace/op-k1ramp-k550-packet/`, `workspace/op-k1ramp-fine-packet/`, `workspace/op-k1k2-split-packet/`, `workspace/op-kratio-scale-packet/`, `workspace/op-lowtotal-packet/` |
| synthesis memo | `docs/nbpolar/SYNTHESIS_20260927.md` |
| overnight report | `workspace/OVERNIGHT_REPORT_20260927.md` |
| R2 decision cards | `docs/nbpolar/R2_T4_PI_DECISION_CARDS_20260927.md` |

## Execution boundary

Five probes are complete (dose ramp, fine interpolation, fixed-total allocation, total-scale at a
fixed ratio, bounded low-total ratio search). **No further probe is authorized by this change** —
a peak-band refinement, an extended low-total search, or any real-data K-allocation work each
requires its own packet, freeze review, and verbatim authorization. Git actions remain suspended
pending explicit user instruction.
