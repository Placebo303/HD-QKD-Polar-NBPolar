# P20K Stage-A review + Stage-B Pre-EXECUTE review (independent, read-only)

- Packet: `NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M` (Tier-Y). Reviewer: independent `reviewer-go`
  thread (not the Stage-A operator). No repo files written by reviewer; no NPZ/parquet content
  opened; no 2M contact of any kind; JSON/provenance reads + output-root absence stat only; no
  decoder executed except injected unit-test reruns (36/36 new + 450/450 predecessors =
  A 233 + B 68 + C 113; pinned interpreter, `-p no:cacheprovider`, fresh basetemps); no
  commit/push. Branch: `codex/nbpolar-phase0`, HEAD `faac0411`.

## Stage-A R1–R8: PASS (independently verified)

- R1 prior read-only reuse PASS (digest/lambda/floor/H pins in code; no NPZ loader tokens;
  `recalibrated_literals.json` matches pins via JSON-only read).
- R2 population/sextuple-gate PASS (DEV 1152..1279/1280..1407/1408..1535; remainder 1536..1659
  = 124f/31744p never decoded; gate order cross-file → VAL → HOLD → P20H → P20I → P20J →
  calibration-identity in source with order asserts; split manifest JSON-verified; 2M
  refusal-string only + zero-contact test).
- R3 caps PASS (34119/36679/32524 + 327743; Δ2560 = 5·512; totals 309966 = 212394 + 97572;
  public 2949687; ~10.41%/11.19%; recount-0 gate tested).
- R4 +512 placement PASS (E1 = first-831 of SAME P16 L1 order; construction JSON digest +
  K values verified; no tag guidance/reselection/E1b implementation).
- R5 endpoints PASS (4-field separation + `undetected` isolation + E2 ORACLE/
  deployable=false excluded; tested). R6 one-shot PASS (single-open guards; 15 SC / 9 tag /
  9 records; 600s/2GiB/single-thread; P20A passthrough; attempts 0).
- R7 gates-pending PASS (no self-accept; freeze authorizes nothing).
- R8 tests + audit PASS (reviewer rerun 36 + 233 + 68 + 113 = 450/450; injected-only;
  output root absent). `FROZEN_OUT_ROOT` fix confirmed literal-only.
- Diff audit PASS (untracked runner/tests/spec/FREEZE/NOTES + tasks.md tail +145/zero
  deletions; predecessor tracked-M is prior-cycle dirt; OpenSpec umbrella only; no
  P20D/minimality/efficiency creep).

## Pre-EXECUTE: PRE_EXECUTE_PASS_CONDITIONAL

1. Branch PASS. 2. Scoped cleanliness PASS-conditional (P20A dirt is accepted dependency).
3. Frozen contract PASS. 4. Authorization — see §4 ruling below. 5. Target absence PASS
   (root absent by ls; re-verify at execution). 6. Focused tests PASS (450/450 rerun).
7. Budget/stop/no-overwrite PASS.
- Stage-B command verbatim PASS (16 flags vs parser required, no defaults; module
  `FROZEN_COMMAND` renders identical argv to FREEZE §10).

## §4 ruling (main thread; consistent with P20C/P20E/P20F/P20G/P20H/P20I/P20J rulings)

Reviewer position: standing Stage-B authorization is background only and does not collapse the
per-packet paste gate; final ruling left to main thread. OVERRULED for execution, RECORDED
for transparency, on the same standing grounds: user's standing authorization (pasted
verbatim in-conversation) explicitly covers subsequent rounds incl. P20K with per-round
conditions identical in substance to a fresh paste; granted with full workflow knowledge to
avoid per-round fragmentation across ≥10 autonomous rounds (reaffirmed at five→ten); all
other gates PASS. Sixth invocation under the same instrument. Applies to P20K only.
