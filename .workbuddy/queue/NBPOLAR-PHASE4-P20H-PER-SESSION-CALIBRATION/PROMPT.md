Work in `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` (WSL) under `AGENTS.md`.
Implement exactly Stage A of the frozen packet
`.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/TASK_PACKET.md`
(P20H per-session-calibration +1024 confirmation on type2_1p5M_20260121_183806, Tier-Y planning-frozen).

Stage A only, in order: (1) read-only callsite inventory of the §12 predecessor helpers
(filenames listed in the packet — do not modify their logic); (2) freeze the §3
calibration program isomorphic to the accepted P0/P2 Model-F concentration procedure
(same formula/smoothing/flow, banned per-cell twin excluded, lambda-procedure + floor
1e-15 + packing `A = 32*U1 + U2` + `FULL_BOB_ONLY` pinned) with input = 1.5M TRAIN
counts ONLY (forbidden: 1.5M DEV/VAL/HOLD, any 1M split, reserved 2M, Model-F CAL
artifact) — execute the single declared counts-calibration open, write
`per_session_calibration/` (plan + input identity + digest-pinned `calibrated_prior.npz`
+ recalibrated H1/H2/TOTAL literals + report), DEV-zero-contact evidenced by the
one-open guards (DEV opens 0 at Stage-A close); (3) add the thin per-session
confirmation runner reusing P18 loading/block formation and P16 operational helpers
unchanged, three hardcoded arms carried over identical from P20C/P20E/P20F/P20G
(`B0_sc_base` / `B1_L2plus` with the SAME +1024 L2 order-prefix-extension step /
`B2_true_l1_diagnostic` oracle) but loading the Stage-A frozen prior read-only via a
calibration-identity digest gate; freeze the exact population (FIRST 384 TRAIN frames
of the 1.5M file → 3 blocks at N=32768, remainder never used — confirm exact integers
`0..383` / `0..127/128..255/256..383` / `384..1659` or replace with a written equivalent
+ justification; JSON-manifest provenance reads only for the population part;
CROSS-FILE source-tag+digest gate first, then INTRA-FILE DEV-vs-VAL/HOLD gate, then
CALIBRATION-IDENTITY gate), the carried-over per-arm disclosure caps (34119 / 39239 /
32524 key bits + 327743 public with ratios-vs-raw), the exact Stage-B command (new P20H
tag master 2026092220, `--source 1p5M` vocabulary frozen at Stage A, 15-SC / 9-tag
budget, 600-s / 2-GiB / single-thread envelope), SC/tag budgets and wall/RSS ceilings
(decoder + calibration costs reported separately); record the §3 (i)–(iv)
calibration-vs-tuning evidence for Pre-EXECUTE; (4) add focused injected tests (fresh
additive `workspace/p20h/<uuid>/` temp root, `pytest -p no:cacheprovider`); (5) write
the Stage-A freeze + implementation notes; (6) stage the P20H OpenSpec delta at
`openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20h/spec.md` plus
the `tasks.md` P20H section (no seed literals in tracked files; tag master 2026092220
and test seeds 2026092221..2227 verified absent elsewhere by repo grep).

Hard limits: exactly ONE counts-calibration content open in Stage A (declared, digest
recorded); ZERO 1.5M DEV/VAL/HOLD content opens or stats in Stage A (DEV opens 0 at
close); zero 1M-pool or reserved-2M open/stat/listing (2M pristine by non-access);
zero real-data decoder execution; zero Stage-B output root; no K/floor/order/decoder/
step/success-point selection on closed blocks, the consumed 1M pool, or 2M; no
calibration on DEV and no refit/resmoothing after any DEV contact; no second disclosure
step (`B1b`), no alternative-construction second factor, no efficiency tuning, no
new-block peeking, no SCL/new kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, no commit/push, no self-acceptance.

Report acceptance IDs P20H-R1..R8 (stage-appropriately), changed files, exact test
commands/results, frozen calibration digest + literals + population/cap/command, and
the split open audit (counts-calibration opens + DEV opens separately, must be 1 + 0
at Stage-A close). Stop on requirement ambiguity or the first concrete blocker with
command, exact error/traceback, attempted remedies, and the ONE decision needed from
the main thread. Stage B is never executed from this prompt — it needs an independent
Pre-EXECUTE review (including the §3 calibration-vs-tuning gate) plus a separate
pasted Stage-B authorization.
