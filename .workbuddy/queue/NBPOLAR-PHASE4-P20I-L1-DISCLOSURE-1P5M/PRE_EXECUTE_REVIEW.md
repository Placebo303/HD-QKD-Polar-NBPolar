# P20I Stage-A review + Stage-B Pre-EXECUTE review (independent, read-only)

- Packet: `NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M` (Tier-Y). Reviewer: independent `reviewer-go`
  thread (not the Stage-A operator). No repo files written by reviewer; no NPZ/parquet content
  opened; no 2M contact of any kind; JSON/provenance reads + output-root absence stat only; no
  decoder executed except injected unit-test reruns (36/36 new + 342/342 predecessors: A 161 +
  B 68 + C 113; pinned interpreter, `-p no:cacheprovider`, fresh basetemps with pre-created
  parents); no commit/push. Branch: `codex/nbpolar-phase0`, HEAD `faac0411`.

## Stage-A R1–R8: PASS (independently verified)

- R1 prior read-only reuse PASS (pins in code: `FROZEN_PRIOR_DIGEST e8dd078a…e43b`,
  `FROZEN_LAMBDA 137.3823795883264`, floor 1e-15, H1/H2/TOTAL literals; no NPZ loader in
  runner; review opened no NPZ; STATUS counts 0/0).
- R2 population freeze PASS (DEV 384..767 → 384..511/512..639/640..767, remainder 768..1659
  never used; manifest TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824; quadruple gate
  order cross-file (1M/2M refused first) → intra-file VAL-before-HOLD → P20H exclusion →
  calibration-identity, verified in code order; reviewer zero 2M contact).
- R3 caps PASS (34119/34759/32524 + 327743; 3·34119=102357, 3·34759=104277, 3·32524=97572,
  total 304206 = operational 206634 + oracle 97572; public 9·327743=2949687; Δ+640 = 5·128;
  ~10.41%/10.61%; recount gate present).
- R4 +128 placement PASS (`FROZEN_K1_C1=447`, `l1_order[:447]` pure view isomorphic to K2 rule,
  same-object identity pinned; P16 JSON digest + K values match; placement by construction
  file, not data selection).
- R5 endpoints PASS (21-gate order incl. `oracle_isolation`/`undetected_zero`/
  `truth_isolation`/`nonfinite_zero`; C2 oracle/deployable=false; P20A 4-endpoint +
  MemoryError passthrough).
- R6 one-shot PASS (STATUS attempts 0/1, DEV 0/1, HOLD 0/1; single-open guards + attempt
  consumed at first open; 600s/2GiB/single-thread envelope).
- R7 gates-pending PASS (tasks unchecked, STATUS PENDINGs, FREEZE "authorizes nothing").
- R8 tests + audit PASS (reviewer rerun 36/36 new in 26.8s + 161/161 + 68/68 + 113/113 in
  841.2s = 378/378; injected-only incl. `test_zero_protected_opens_audit`; output root absent).
- Diff audit PASS (`tasks.md` +700/-0 append-only; new thin runner/tests/spec/FREEZE/NOTES;
  predecessor tracked-M is prior-cycle dirt; OpenSpec umbrella only; `C1b` single forbidding
  mention, no implementation; no P20D/minimality/efficiency creep).

## Pre-EXECUTE: PRE_EXECUTE_PASS_CONDITIONAL

1. Branch PASS. 2. Cleanliness PASS (frozen dirs zero diff outside §12 manifest; rest
   pre-existing). 3. Frozen contract PASS (packet + FREEZE + NOTES + spec + tasks consistent;
   16 flags == parser 16 required). 4. §4 PASS under standing authorization (main-thread
   ruling below; reviewer recorded the covering-position vs fresh-paste-position and left
   final ruling to main thread). 5. Target absence PASS (`l1_disclosure_1p5m/` ABSENT,
   re-verify at execution). 6. Tests PASS (378/378 rerun). 7. Quadruple-pool + prior-reuse
   PASS (TRAIN-base documented equivalence with fail-close adjudication recorded).
- Stage-B command verbatim PASS (FREEZE §10 vs module `FROZEN_COMMAND` via import: 16 flags
  `--prior/--source/--floor/--n/--k1/--k2/--construction/--construction-digest/--dev-pairs/
  --dev-frames/--block-frames/--remainder-frames/--tag-master/--chunk-rows/--tag-bits/
  --out-dir`, all required, no defaults; `--source 1p5M`, `--dev-frames 384 767`,
  `--remainder-frames 768 1659`, `--tag-master 2026092230`, `--n 32768`, `--k1 319`,
  `--k2 6492`, `--floor 1e-15` + dual digests + env budgets).

## §4 ruling (main thread; consistent with P20C/P20E/P20F/P20G/P20H rulings)

Standing Stage-B authorization (pasted verbatim in-conversation, covering P20C + subsequent
rounds incl. P20I, with per-round conditions) cures the authorization gap. Reviewer's
covering-position matches precedent; the fresh-paste alternative is recorded and declined for
the same standing grounds (explicit informed user grant to avoid per-round fragmentation;
identical substantive conditions; all other gates PASS). Applies to P20I only.

## Authorization to execute once

Stage B may execute ONCE: (1) single attempt consumed at first DEV content open; no
rerun/seed/disclosure/construction/calibration tuning; (2) verbatim 16-flag frozen command;
prior digest + lambda/floor/key-set/H (1e-12) gates pre-SC, mismatch → BLOCKED;
(3) output root absent at execution, five files + per-(arm,block) checkpoints, 9 records /
15 SC / 9 tags, recount-0; (4) quadruple gate source → VAL → HOLD → P20H → calibration
order; 1M pool fail-closed, 2M pristine (open/stat/list all forbidden);
(5) descriptive-only; `undetected` isolated, never success; oracle never operational; no
FER/efficiency/promotion language.
