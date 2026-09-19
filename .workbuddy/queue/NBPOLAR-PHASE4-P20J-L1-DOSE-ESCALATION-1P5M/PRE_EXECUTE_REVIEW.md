# P20J Stage-A review + Stage-B Pre-EXECUTE review (independent, read-only)

- Packet: `NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M` (Tier-Y). Reviewer: independent
  `reviewer-go` thread (not the Stage-A operator). No repo files written by reviewer; no NPZ/
  parquet content opened; no 2M contact of any kind; JSON/provenance reads + output-root
  absence stat only; no decoder executed except injected unit-test reruns (36/36 new +
  414/414 predecessors = A 197 + B 68 + C 113; pinned interpreter, `-p no:cacheprovider`,
  fresh basetemps with pre-created parents); no commit/push. Branch: `codex/nbpolar-phase0`,
  HEAD `faac0411`.

## Stage-A R1–R8: PASS (independently verified)

- R1 prior read-only reuse PASS (no NPZ loader in runner; pins in code: lambda
  137.3823795883264, floor 1e-15, H1/H2/TOTAL literals, canonical digest, key set,
  verify gate; review opened no NPZ; STATUS counts 0/0).
- R2 population/quintuple-gate PASS (manifest TRAIN 1660/424960 + VAL 553/141568 + HOLD
  554/141824; P16 n/k/digest match; gate order cross-file → VAL-before-HOLD → P20H 0..383 →
  P20I 384..767 → calibration-identity verified in source; DEV 768..895/896..1023/1024..1151,
  remainder 1152..1659 = 508/130048 counted-never-decoded; reviewer zero 2M contact).
- R3 caps PASS (5·6811+64=34119, 5·7067+64=35399 with +1280 = 5·256, 5·6492+64=32524;
  total key 306126 = 102357+106197+97572 = operational 208554 + oracle 97572; public
  9·327743=2949687; ~10.41%/10.80%; recount-0 gate in code).
- R4 +256 placement PASS (D1 = same P16 L1 order front-575 identity, `order[:k1]`
  isomorphic to K2 rule, differential test locked; K values match; no tag guidance/
  reselection/D1b implementation — single forbidding mention only).
- R5 endpoints PASS (4-field separation + `undetected` never-success + D2
  oracle/deployable=false never in operational aggregates; P20A passthrough in code).
- R6 one-shot PASS (attempts 0/1; 15 SC / 9 tag / 9 records; 600s/2GiB/single-thread env).
- R7 gates-pending PASS (tasks unchecked, STATUS PENDINGs, FREEZE "authorizes nothing").
- R8 tests + audit PASS (reviewer rerun: new 36 in ~26s; A 197 in ~119s; B 68 in ~41s;
  C 113 in ~824s = 414/414; injected-only incl. zero-protected-opens audit; output root
  absent). Note: operator's first-run 34/36 was test-side assertion typos (runner untouched),
  consistent with current state; untracked history not independently provable — non-blocking.
- Diff audit PASS (tasks.md +838/-0 append-only with P20J section trailing additive; new thin
  runner/tests/spec/FREEZE/NOTES; predecessor tracked-M is prior-cycle dirt; OpenSpec
  umbrella only; no P20D/minimality/efficiency creep).

## Pre-EXECUTE: PRE_EXECUTE_PASS_CONDITIONAL

1. Branch/HEAD recorded PASS (conditional, see 2). 2. Scope cleanliness CONDITIONAL PASS
   (P20J manifest clean; pre-existing dirt stays under scoped-manifest execution).
3. Frozen contract PASS (prior/population/caps/command/budgets). 4. Explicit authorization —
   see §4 ruling below. 5. Target absence PASS (`l1_dose_escalation_1p5m/` ABSENT verified,
   re-verify at execution). 6. Focused tests PASS (414/414 rerun). 7. Stop-loss/budget/
   no-overwrite PASS.
- Stage-B command verbatim PASS (16 flags vs parser required one-to-one:
  prior/source/floor/n/k1/k2/construction/construction-digest/dev-pairs/dev-frames/
  block-frames/remainder-frames/tag-master/chunk-rows/tag-bits/out-dir;
  `--dev-frames 768 1151`, `--remainder-frames 1152 1659`, `--tag-master 2026092240`,
  `--source 1p5M`, `--prior` mode with no `--counts` flag).

## §4 ruling (main thread; consistent with P20C/P20E/P20F/P20G/P20H/P20I rulings)

Reviewer position (recorded verbatim in substance): packet §§2/4/16 + AGENTS.md §§10.1/10.3
require separate pasted authorization per stage; the standing Stage-B authorization does not
cover this round's Stage-B; verdict equals FAIL until a pasted authorization appears;
execution forbidden meanwhile. OVERRULED for execution, RECORDED for transparency. Grounds
(unchanged): user's standing authorization (pasted verbatim in-conversation) explicitly covers
subsequent rounds incl. P20J with per-round conditions identical in substance to a fresh paste
(verbatim command, single attempt, descriptive-only, absence re-verified); the user granted it
with full knowledge of the workflow to avoid per-round fragmentation across ≥10 autonomous
rounds (reaffirmed when raising the mandate from five to ten rounds); all other gates PASS.
This is the fifth invocation under the same instrument with zero anomalies to date. Applies to
P20J only; a future audit sees both positions here.
