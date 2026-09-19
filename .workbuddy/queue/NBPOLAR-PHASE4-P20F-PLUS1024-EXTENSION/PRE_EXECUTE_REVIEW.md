# P20F Stage-A review + Stage-B Pre-EXECUTE review (independent, read-only)

- Packet: `NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION` (Tier-Y). Reviewer: independent `reviewer-go`
  thread (not the Stage-A operator). No repo files written by reviewer; no protected
  TRAIN/HOLD/VAL/EVAL/raw stat/open (output-root absence stat only); no decoder executed except
  injected unit-test reruns (36/36 new + 217/217 predecessors, pinned interpreter,
  `-p no:cacheprovider`, fresh basetemps); no commit/push. Branch: `codex/nbpolar-phase0`.

## Stage-A R1–R8: PASS (stage-appropriate)

- R1 zero-tuning carry-over vs P20E pinned (only population + tag domain differ).
- R2 population 768..895/896..1023/1024..1151 + remainder 1152..1199 (48f, never used);
  quadruple gate P20C → P20E → VAL → HOLD verified; last-usable-segment arithmetic holds
  (384+384+384+48 = 1200 TRAIN frames; 48 < 128).
- R3 caps 34119/39239/32524 + 327743 recomputed exact (10.41%/11.97%; Δ+5120 = 5·1024;
  totals 317646/2949687; recount-0 gate).
- R4 +1024 order-prefix frozen, never CLI-tunable. R5 four endpoints + oracle isolation +
  undetected isolation. R6 one-shot 0/1, P20A resource path, stop rules + SCL gate intact.
- R7 descriptive label, gates pending correct. R8 tests green, injected-only, guards False.
- Diff audit: P20F scope = thin runner + 36-test + umbrella spec + tasks append + FREEZE + NOTES;
  predecessor diffs are pre-existing P20A dependency; no P20D/efficiency/SCL creep.

## Pre-EXECUTE: PRE_EXECUTE_PASS_CONDITIONAL

1. Branch PASS. 2. Cleanliness PASS with comments (manifest isolated; unrelated dirt disclosed).
3. Frozen contract PASS. 4. §4 PASS (conditional): user standing Stage-B authorization (pasted in
   main thread, covering P20C + subsequent rounds incl. P20F) cures the authorization gap; its 5
   conditions align with freeze gates; stricter no-rerun governs. 5. Target absence PASS
   (`stat plus1024_extension/`: No such file). 6. Tests PASS (rerun counts above). 7. Four-pool
   equivalence ACCEPTED (TRAIN 768..1151 last整块 tranche; remainder insufficient).
- Stage-B command verbatim PASS (module `FROZEN_COMMAND` byte-identical to FREEZE §10; 16/16
  flags; `--dev-frames 768 1151 --remainder-frames 1152 1199 --tag-master 2026092200`).

## Authorization to execute once

Stage B may execute ONCE under the 5 iron rules: (1) exact frozen command from repo root with
sibling `.venv`, single attempt 0→1, no rerun/retune/reseed; (2) descriptive label only
(`…EXTENSION_COMPLETE` iff 20/20 gates; B2 never operational); (3) `undetected` isolated,
recount-0/SC-15/tag-9 or BLOCKED; (4) five files only, per-(arm,block) checkpoints;
(5) any abort preserves accounting and is BLOCKED; stop rules + closed/consumed ranges binding.
