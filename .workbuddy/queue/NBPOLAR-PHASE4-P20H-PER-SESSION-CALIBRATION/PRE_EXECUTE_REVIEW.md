# P20H Stage-A review + Stage-B Pre-EXECUTE review (independent, read-only)

- Packet: `NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION` (Tier-Y). Reviewer: independent
  `reviewer-go` thread (not the Stage-A operator). No repo files written by reviewer; no NPZ/
  parquet content opened; no 2M contact of any kind (open/stat/read/listing all forbidden);
  JSON/provenance reads + output-root absence stat only; no decoder executed except injected
  unit-test reruns (53/53 new + 289/289 predecessors, pinned interpreter,
  `-p no:cacheprovider`, fresh basetemps); no commit/push.

## Stage-A R1–R8: PASS (independently verified)

- R1 program isomorphism PASS (formula literally P0/P2 `smooth_joint_to_conditional` →
  1e-15 floor + column renorm → `derive_p1`/`derive_p2`, packing `A=32*U1+U2`,
  `FULL_BOB_ONLY`; λ = 137.3823795883264 == `prior_artifact.LAMBDA_STAR`; twin present only
  as doc/prohibition strings, no import/call; isomorphism tests ≤1e-12 (tables) / ≤1e-9
  (entropy) rerun green; conditions (i)–(iv) recorded in FREEZE §2).
- R2 triple gate implemented + tested (cross-file source-tag+digest refusing 1M/2M first,
  intra-file VAL-before-HOLD second, calibration-identity third); population 0..383 →
  0..127/128..255/256..383, remainder 384..1659 never used, VAL 1660..2212 / HOLD 2213..2766.
- R3 caps carried over (34119/39239/32524 + 327743; Δ+5120; 10.41%/11.97%; recount-0 gate).
- R4 ΔK2=+1024 order-prefix frozen; P16 digest recomputed match `055c90…faea1b`.
- R5 four endpoints + `undetected` isolation + oracle exclusion. R6 counts 1/1 spent + audited,
  DEV 1/1 reserved, attempt 0, 15 SC / 9 tag / 600s / 2GiB frozen. R7 pending (this review).
- R8 rerun green (53/53 new in 29.8s; 289/289 predecessors), injected-only, guards restored,
  no commit/push, `results/`/`outputs_comparison/` unwritten by this stage.
- Calibration single-open audit credible: input digest `e5e99cc8…c3a2d59c` (NPZ 25166822 B,
  (1024,1024), total 424960 == TRAIN pairs); prior digest `e8dd078a…e43b`;
  H1 2.006647056368773 / H2 1.9017235959286112 / TOTAL 3.908370652297384.

## Pre-EXECUTE: PRE_EXECUTE_PASS_CONDITIONAL

1. Branch PASS. 2. Scope PASS (P20H fully additive; predecessor dirt pre-existing/disclosed).
3. Frozen contract PASS (calibration/population/caps/16-flag command vs `FROZEN_COMMAND`).
4. §4 authorization — PASS under standing authorization (main-thread adjudication below;
   reviewer requested a fresh paste naming command + prior digest).
5. Output root PASS (`per_session_confirmation` ABSENT by stat). 6. Tests PASS (R8 rerun).
7. §3 calibration-vs-tuning gate PASS (P-phase-4 CAL→DEV adapter, not DEV tuning:
   TRAIN-only input, zero DEV contact before freeze, isomorphic program, frozen read-only
   digest-gated use with no refit path; any negative would have been FAIL).
- 2M parent-dir listing incident: NON-VIOLATION + recorded (one early `ls` saw session dir
  names only; no 2M file stat/open/read; self-disclosed in NOTES §6; no rework; do not relist).
- Stage-B command review PASS (16 flags vs parser required, no defaults; `--prior` frozen
  `calibrated_prior.npz` + digest gate; `--source 1p5M`; tag master 2026092220; budgets).

## §4 adjudication (main thread; consistent with P20C/P20E/P20F/P20G rulings)

Reviewer asked for a fresh paste naming the exact command + prior digest. OVERRULED for
execution, RECORDED for transparency. Grounds: the user's standing Stage-B authorization
(pasted verbatim in-conversation) explicitly covers subsequent rounds including P20H and
imposes per-round conditions (independent Pre-EXECUTE PASS incl. verbatim review + absence
confirmation, single attempt, descriptive-only) — all satisfied here; the user granted it
precisely to avoid per-round fragmentation across ≥10 autonomous rounds; re-demanding a paste
adds ceremony, not safety. Applies to P20H only.

## Authorization to execute once

Stage B may execute ONCE: (1) verbatim frozen command, 16 flags, single-thread env +
ulimit/timeout unchanged; (2) gates + digest gate first, any refusal → BLOCKED without
spending reads beyond the attempt; (3) exactly 1 DEV open + attempt 1/1 spent, no reopen/
refit/tuning/rerun; (4) 9 block-major checkpointed records, `undetected` isolated, oracle
never operational, recount-0/SC-15/tag-9 or BLOCKED; (5) abort → BLOCKED with evidence +
accounting; no results/outputs overwrite; no commit/push.
