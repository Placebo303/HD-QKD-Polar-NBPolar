# FREEZE REVIEW RECORD — NBPOLAR-M2-PRIOR-G1-REALDATA-NLL (T5 gate)

Freeze under review: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1_freeze.md`.
Reviewer: reviewer-go (independent subagent). Branch `codex/nbpolar-phase0` verified. Read-only; arithmetic recomputed in the sibling venv (no `.ttbin`, no TimeTagger). Record persisted by main thread 2026-09-21.

## First review — verdict FREEZE_FAIL (arithmetic only; scope/gates/structure PASSed)

Blocking:
- **B1** — §3 layout totals wrong: 14-block allocated written 4,230 (correct **4,190**); 16-block total written 4,666 (correct **4,444→4,446**); deficit written 410 (correct **190**); 16→14 delta inconsistent (436 vs true 256). §4 ranges were correct and self-consistent; §3 contradicted them. Phase-A threshold inherited wrong.
- **B2** — W_P=1000 numbers wrong: post-skip frames written 4,317 (correct **4,315**); accidental written 3.65% (correct **2.84%**, census (N)-1000 `accidental_fraction = 0.0284078081379145`).

## Rework applied (main thread, arithmetic-only; no design change)

`g1_freeze.md`: §3 infeasibility line (4,446 / 190), §3 W_P=1000 bullet (4,315 / shortfall 131 / 2.84%), §3 ADOPTED bullet (4,190 allocated / 66 reserve / 256 delta), NEW §3 honest-alternatives bullet (16-block + CHAR-150k = 4,251 ≤ 4,256 with 5-frame reserve — feasible but fragile; NOT adopted), §4 fallback threshold (4,190), §5 #10 basis (190). Parent `STATUS.yaml` g2_blocks comment + child `TASK_PACKET.md` Phase-A threshold + child `PROMPT.md` propagated. Non-blocking items also addressed: exact B_tail bound 1.979e-4 recorded (frozen 2.0e-4 kept per parent verbatim); Phase-A one-time vs Phase-B per-acquisition budget split note (§7); `decision-log:5224` citation for w=200 cover 0.9247. Freeze status → `G1_FREEZE_REVISED_PENDING_REREVIEW`.

## Re-review — verdict FREEZE_PASS

Blocking Issues: None. Both first-review findings corrected; every required downstream location carries the corrected values; zero stale hits survive in the freeze packet set; no design/value change crept in.

Independent recomputation (re-review): 14-block = 1024+32+782+560+14×128 = 4,190 ✓; 4,190+66 = 4,256 ✓; 16-block = 4,446 ✓; deficit 190 ✓; delta 256 ✓; W_P=500 post-skip floor(1,089,556/256) = 4,256 ✓; W_P=1000 4,315 / shortfall 131 / 2.84% ✓ (old 3.65% matches none of the six census cells); honest alternative 4,251 ≤ 4,256, 587×256 = 150,272 ≥ 150k, U ≈ 2.0e-5, NOT adopted ✓; §4 ranges inclusive lengths 1,024/32/782/560/1,792/66 sum 4,190 + 66 = 4,256 = frames 0..4,255 ✓; stale sweep (`4230`/`4666`/`4317`/`3.65%`/`410`) over all 9 packet files — zero hits; invariance confirmed (g2_blocks 14, CHAR 200,192, HELDOUT 560, W_P 500, skip 702, MOD LINEAR_ONLY, tag_master 2026102201, gates unchanged, SHG `_2` frozen, M2 CANDIDATE, no new claim language).

Remark (not a finding): the re-review tasking's CHAR U 3/153600 = 1.952e-5 is exactly 1.953125e-5; the freeze's rounded 2.0e-5 covers both that and the adopted 587-frame 3/150272 = 1.996e-5; the 10×-under-B_tail margin holds either way.

## Gate status

T5 (freeze review): **PASS** (after one revise-required cycle). Remaining before any execution: explicit user authorization pasted in full; Phase-A closure fills the four list-type keys; closure outputs + Phase-0 code verified before Phase B (per child TASK_PACKET).
