# G1 FREEZE — NBPOLAR-M2-PRIOR-REALDATA-VALIDATION Stage 2 (real-data held-out NLL replication, DECODER-FREE)

- Status: `G1_FREEZE_REVIEW_PASS_PENDING_AUTHORIZATION` — T5 freeze review PASS (first review FREEZE_FAIL on §3 arithmetic ⇒ revised ⇒ re-review PASS; record `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/FREEZE_REVIEW.md`). This document FREEZES the 19 TO-FREEZE values for the Stage-2 G1 run. It authorizes NOTHING by itself. Execution requires: (1) explicit user authorization pasted in full, (2) the Phase-A closure outputs filling the three list-type keys, (3) closure + Phase-0 code verification before Phase B.
- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; branch `codex/nbpolar-phase0` (verified `.git/HEAD`). DO NOT SWITCH.
- Parent packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md` (authoritative scientific spec; this freeze implements its §5 only — §§6–8 G2/Pre-RESULT are LATER, SEPARATE freezes).
- Change: `openspec/changes/nbpolar-prior-rebaseline/` (implements T5 at G1 scope; T6/T7/T8 OUT).
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (TimeTagger 2.22.6 + Swabian shim per `docs/troubleshooting.md`; Stage-1 sibling venv is NOT sufficient here — the closure/execution reads `.ttbin` via `FileReader`).
- Nature: G1 is DESCRIPTIVE / NON-CLAIM, decoder-free. M2 is a CANDIDATE, never the baseline. No FER/efficiency/qualification claim follows from G1 under any outcome.

## 1. Populations (constrain to this)

1. **PRIMARY — SHG `_1` only**: `20260113_SHG_Type2PPLN_3s`, primary `/mnt/d/Data/Raw Data/2026.1.13/SHG_Type2PPLN_3s_2026-01-13_162106/SHG_Type2PPLN_3s_2026-01-13_162106.ttbin` + `.1` continuation (read primary only via `FileReader` auto-follow; NEVER concatenate). Full G1-1..G1-4 four-gate set.
2. **FROZEN-SESSION REMAINDER (NLL/H level ONLY, no decode, no new alignment)**: 101 frames = 1.5M VAL 2172–2212 (41) + 1.5M HOLD 2725–2766 (42) + 2M HOLD 3627–3644 (18); frozen derived pairs only. EXEMPT from G1-1 (no new alignment) and from the ≥200k char-sample gate (101×256 = 25,856 pairs physically cannot supply 200k). Scope: 32-frame CAL + held-out NLL/H comparison only (32 CAL + 69 held-out frames).
3. **SHG `_2`** (`20260113_SHG_Type2PPLN_3s_2`): FROZEN — no G1/G2 preview, no model selection, no window choice, no pairing read. Reserved for G3 with the parent-STATUS participation disclosure. Any touch ⇒ STOP + blocker.

## 2. Census provenance (already-derived, decoder-free; read-only inputs to the closure)

From `workspace/census_20260921/20260113_SHG_Type2PPLN_3s/dual_rule_census.json` + `dual_rule_summary.json` (2026-09-21 dual-rule census, frozen constants only):

- Events 16,130,065; channels 1/5; other_frac 0.0796.
- Alignment (census call, params: scan_range 409600 ps, bin 100 ps, accept `status==ok AND peak_to_bg>=10` + yield-sweep self-check): `peak_center_ps = 50`, `peak_sigma_ps = 112.45189572400645` (inside frozen design gate [50,150]), `peak_to_bg = 1366.2727272727273`, `status = ok`. Offset convention `tA_aligned = tA_raw + peak_center_ps`, offset +50 applied to Alice.
- Pairing rule **(N) narrow nearest-unique** at window 500: `n_pairs = 1,269,268`, `n_frames = 4,958` (= floor(n_pairs/256), PRE-skip), `tier = FULL`, `accidental_fraction = 0.014403577495060145`.
- Frozen constants (census `frozen` block): `d=1024`, `bin_width_ps=200`, `period_ps=204800`, `frame_pairs=256`, `gate_ps=200`, `threshold_ps=40000`, `skip_frames=702`, `tier_full_min=1982`, `tier_reduced_min=1342`.
- The census (N) counts are PRE-skip (skip-702 is applied only in the census (W)-H path, `dual_rule_census_20260921.py:300-315`). The G1 stream applies skip-702 per §4 below.

## 3. Frame-budget arithmetic (why g2_blocks = 14, not the recommended 16)

Post-skip available complete frames on SHG `_1` at W_P=500:
- skip pairs = 702 × 256 = 179,712; remaining pairs = 1,269,268 − 179,712 = 1,089,556;
- complete frames = floor(1,089,556 / 256) = **4,256** (uses 1,089,536 pairs; the trailing 20 pairs are an incomplete frame and are dropped). Tier post-skip: 4,256 ≥ 1,982 ⇒ FULL.

Required frames per segment: A1-CAL 1,024 + CAL32 32 + CHAR 782 (200,192 pairs ≥ 200,000) + HELDOUT 560 (143,360 symbols) + EVAL 16×128 = 2,048 ⇒ **4,446 > 4,256 — the recommended 16-block layout is INFEASIBLE by 190 frames** at W_P=500 with skip-702.

Alternatives considered (recorded, not smoothed):
- W_P=1000 (also fully-usable per census): 1,284,506 pairs ⇒ floor((1,284,506 − 179,712)/256) = 4,315 post-skip frames — still short of the 16-block total 4,446 (by 131); buys slack, not blocks; and raises accidental 1.44% → 2.84%. Rejected: W_P=500 is the cleanest unbiased usable cell (w=200 cover 0.9247 is marginally biased, attested `docs/decision-log.md:5224`; w=500/1000 are the unbiased usable cells, recommendation stands).
- Drop skip-702 on SHG `_1`: would gain 702 frames and admit 16 blocks — rejected: skip-702 is the frozen `INHERITED_NOT_DERIVED` convention; changing it on new data without evidence is a contract change, not a freeze detail.
- Shrink CHAR below 200k pairs: 150k pairs gives U = 2.0e-5 (still 10× under B_tail) — held as fallback, NOT taken: the ≥200k recommendation carries 13.3× margin and the δ-tail gate is the G1 premise; keep it.
- **ADOPTED: EVAL = 14 blocks (1,792 frames).** Keeps CHAR ≥ 200k and HELDOUT at 560 frames (SE ≈ 0.00189 bits ⇒ Δ_min is ~10.6× SE; the S8-observed effect 0.0366–0.0442 would be ~19–23× SE — the NLL gate retains discriminating power). Total allocated 4,190 ≤ 4,256; 66 frames RESERVE (unallocated, never touched). The 16→14 change removes exactly 2 blocks = 256 frames (4,446 − 256 = 4,190 ✓, matching the §4 ranges). Deviation from the g2_blocks=16 recommendation is recorded here with this arithmetic; G2's Wilson gate operates on the frozen 14 blocks.
- **Recorded after correction (honest alternatives)**: with the TRUE deficit of 190 frames, a 16-block layout could be forced by shrinking CHAR to 150k pairs (587 frames; zero-obs U = 2.0e-5, still 10× under B_tail) — 1,024+32+587+560+2,048 = 4,251 ≤ 4,256, leaving only ~5 frames RESERVE. That is feasible but fragile (any ledger surprise exhausts the reserve and triggers the §4 fallback), and it degrades the δ-tail gate margin 13.3× → 10×. NOT adopted: at 14 blocks BOTH preregistered gate margins are preserved with a 66-frame reserve.

## 4. Segment layout (deterministic rule; Phase A enumerates the explicit lists)

Frame indices are 0-based over the post-skip complete-frame stream (frames 0..4255), chronological:

| Segment | Frames | Count | Pairs/symbols | Purpose |
|---|---|---|---|---|
| A1-CAL | 0–1023 | 1,024 | 262,144 pairs | Arm A1 incumbent M0 1024-frame sacrificed CAL |
| CAL32 | 1024–1055 | 32 | 8,192 pairs | Arms A2/B matched 32-frame sacrificed CAL (FIT32) |
| CHAR | 1056–1837 | 782 | 200,192 pairs | δ-tail characterisation sample (G1-2) |
| HELDOUT | 1838–2397 | 560 | 143,360 symbols | Held-out NLL scoring segment (G1-3) |
| EVAL | 2398–4189 | 1,792 | 14 blocks × 128 frames | G2 decode blocks (LATER freeze; frozen K1=319/K2=6492, frozen P16 order) |
| RESERVE | 4190–4255 | 66 | — | Unallocated; never read, never decoded |

Disjointness: the five used segments are pairwise disjoint by construction (contiguous, non-overlapping chronological ranges). Phase A records the explicit lists and the disjointness matrix; any overlap invalidates the run. Trailing 20 pairs (incomplete frame) are dropped, never padded. If the Phase-A ledger yields FEWER than 4,190 complete post-skip frames ⇒ `block_formation_fallback` applies: COMPLETE-BLOCKS-ONLY for EVAL (form as many complete 128-frame blocks as available from the EVAL range); if fewer than 1 complete block ⇒ record INSUFFICIENT and return INCONCLUSIVE. Never pad, never reuse frames, never shrink N.

## 5. The 19 TO-FREEZE values (frozen herein)

| # | Key | Frozen value | Basis |
|---|---|---|---|
| 1 | `B_tail` | `2.0e-4` | 40.4214 × p × 32768 ≤ 1% × 26214 ⇒ p ≤ 1.98e-4 ≈ 2.0e-4 (26214 = 32768×0.8 L2 budget; 262.14 = 1%). Exact bound 0.01×26214/(40.4214×32768) = 1.979e-4; the frozen 2.0e-4 is ~1% looser (40.4214×2.0e-4×32768 = 264.91 vs 262.14) — kept verbatim per parent `TASK_PACKET.md` §5, recorded here for the review trail |
| 2 | `delta_min` | `0.020` bits/symbol | ≈ ½ the S8 minimum observed margin 0.0366; ~10.6× the held-out SE at 143,360 symbols (SE ≈ 0.00189, S8-implied scaling — a synthetic-stream estimate, not a SHG measurement) |
| 3 | `g2_success_rule` | Wilson-lower(B) > Wilson-upper(A2), strict non-overlap, z=1.96 | parent §6 |
| 4 | `g2_inconclusive_rule` | point(B) > point(A2) but CIs overlap ⇒ bounded negative | parent §6 |
| 5 | `g2_fail_rule` | point(B) ≤ point(A2) | parent §6 |
| 6 | `pairing_window_primary` | `500` | DATA-INFORMED (N)-rule usable cell: clean (acc 1.44%), FULL, unbiased gauss cover ≥0.95. **This freeze adopts the (N) narrow nearest-unique pairing contract at w=500 — the pending PI pairing-rule decision (STATE.md §4) is thereby DECIDED for this packet; authorizing this freeze confirms that decision.** |
| 7 | `pairing_window_sensitivity` | `200` | cleanest cell (acc 0.58%) but marginally biased (gauss cover 0.9247); sensitivity readout only, NO switching |
| 8 | `skip_frames` | `702` | `INHERITED_NOT_DERIVED`; never re-derived per acquisition |
| 9 | `cal_split_rule` | `RULE-FIT32-SCORE-HELDOUT` | fit triple on ALL 32 CAL frames; score on HELDOUT (temporally separated, disjoint); no within-CAL split; split seed N/A |
| 10 | `g2_blocks` | `14` | deviation from recommended 16 — see §3 arithmetic (16 infeasible by 190 frames at W_P=500 + skip-702); EVAL = frames 2398–4189 |
| 11 | `tag_master` | `2026102201` | rule TAG_MASTER = EVAL_SEED + 10000 with EVAL_SEED = 2026092201 (fresh, unused by S9 2026092101/2026092117 or any P20 packet) |
| 12 | `char_sample_pairs` | `200192` | = 782 frames × 256 ≥ 200,000; zero-obs rule-of-three upper U = 3/200192 = 1.4986e-5 (13.3× under B_tail) |
| 13 | `cal_frame_ids` | Phase-A list (rule: post-skip frames 1024–1055) | explicit 32-frame list; TO-FREEZE closure |
| 14 | `heldout_frame_ids` | Phase-A list (rule: post-skip frames 1838–2397) | explicit list; TO-FREEZE closure |
| 15 | `mod_boundary` | `LINEAR_ONLY` | wrap cells (0,1023)/(1023,0) count as tail (conservative); frozen, not tunable; G1/G2 never switch post-freeze |
| 16 | `a1_cal_ids` | Phase-A list (rule: post-skip frames 0–1023) | explicit 1024-frame list for arm A1's incumbent CAL on SHG `_1`; TO-FREEZE closure |
| 17 | `disjointness_matrix` | Phase-A proof | pairwise-disjoint A1-CAL / CAL32 / CHAR / HELDOUT / EVAL recorded at closure; any overlap invalidates the run |
| 18 | `block_formation_fallback` | `COMPLETE-BLOCKS-ONLY` else `INSUFFICIENT ⇒ INCONCLUSIVE` | never pad/reuse/shrink |
| 19 | `g2_arms` | `[A1_M0_1024f_incumbent, A2_M0_32f_matched, B_M2_32f_candidate]` | unchanged from parent STATUS |

Remainder population (frozen sessions) uses its own preregistered mini-layout: 32 CAL frames + 69 held-out frames from the 101-frame remainder (chronological within each segment; frozen derived pairs; NO alignment, NO char sample — exempt per §1.2).

## 6. Gate rules (executable, preregistered BEFORE any run)

**G1-δtail (on CHAR only, n = 200,192 pairs, frozen MOD decides wrap):** statistic p̂ = count(|δ| ≥ 2)/n. One-sided 95% upper U: rule-of-three 3/n if zero observations, else Clopper-Pearson upper. PASS iff U < B_tail (2.0e-4). FAIL iff p̂ > B_tail. INCONCLUSIVE iff p̂ ≤ B_tail ≤ U ⇒ bounded negative, no proceed. STOP: δtail FAIL ⇒ premise fails on this source — record, do NOT proceed toward G2.

**G1-NLL (matched-CAL, descriptive only):** statistic Δ = mean per-symbol (NLL_M0 − NLL_M2) on HELDOUT (n = 143,360 symbols; SAME 32-frame CAL for both models; FIT32; seed N/A). PASS iff Δ > Δ_min (0.020). FAIL iff Δ ≤ 0. INCONCLUSIVE iff 0 < Δ ≤ Δ_min ⇒ no proceed. CAVEAT (binding): matched 32-frame CAL is NOT the incumbent — M0's as-deployed regime is 1024 frames and is measured only by G2 arm A1. This NLL never promotes M2.

**Alignment/pairing reproduction gate (Phase B):** the Phase-A closure alignment + (N)-w=500 pairing MUST reproduce bit-exactly (peak_center 50 / σ 112.45189572400645 / status ok / n_pairs 1,269,268 / n_frames 4,958 pre-skip). Any mismatch ⇒ STOP loudly (ALIGN_INCONSISTENT), no tuning.

**δ-mass profile (G1-2, descriptive):** {0, ±1, ±2..k} linear AND circular under frozen MOD, on CHAR; recorded, no gate.

## 7. Two-phase execution design (both decoder-free; both under the same G1 authorization)

**Phase A — freeze closure (SHG `_1`, ONE framing pass, no prior, no decoder):** reproduce census alignment + (N)-w=500 pairing (reproduction gate §6); apply skip-702; enumerate the post-skip frame ledger; apply the §4 layout rule; emit `cal_frame_ids`, `heldout_frame_ids`, `a1_cal_ids`, `disjointness_matrix`, and the complete freeze-config JSON (all 19 keys). Phase A touches no prior fitting, no NLL, no decoder. Budget: ≤ 300 s wall / 2 GiB RSS (census full dual-rule pairing took 42.1 s; single-window closure is smaller).

**Phase B — G1 execution (SHG `_1` + remainder):** re-verify the §6 reproduction gate against the Phase-A ledger; run G1-1..G1-4 (alignment record; pairing + δ-profile at W_P with W_S sensitivity readout, no switching; CAL32 FIT + held-out NLL M0-vs-M2; H1/H2/H_total both models); evaluate both gates; remainder-population NLL/H check. Budget: ≤ 600 s wall / 2 GiB RSS per acquisition, single-threaded (parent §9). Budget split (recorded per freeze review): Phase A's ≤ 300 s is a one-time amortized closure cost, NOT part of the parent §9 per-acquisition Stage-2 cap; Phase B alone carries the ≤ 600 s per-acquisition cap.

## 8. Stop rules (binding)

Any §3 FORBIDDEN touch of the parent packet (incl. any SHG `_2` read, any decoder call, any write into `results/` or `comparison_bench/outputs_comparison/`, any threshold/seed/K/window change after this freeze) ⇒ STOP + blocker. Reproduction-gate mismatch ⇒ STOP loudly. Budget exceeded ⇒ STOP, record blocker (no tuning to fit). G1 INCONCLUSIVE ⇒ bounded negative, no tuning, no rerun. Any attempt to pull G2 execution or G3 into this packet ⇒ STOP (separate freezes). Ambiguity ⇒ STOP (second return condition), never guess.

## 9. Deliberately NOT frozen here (later freezes, explicitly out)

G2 freeze closure beyond the values above (per-block EVAL list finalization is the §4 rule + Phase-A list; G2's own Pre-EXECUTE review + authorization are separate); G3 (SHG `_2`); the D4 K_total choice (fixed-f 7053/7106 vs fixed-K f=1.2939/1.2952 — G2 decodes frozen K1=319/K2=6492 regardless); construction re-derivation (frozen P16 order kept); any FER/efficiency reading.

## 10. Acceptance IDs for the G1 packet (operator reports IDs, not restatements)

`G1-1` alignment per acquisition (census-reproduced, recorded; remainder reuses frozen pairs) · `G1-2` pairing at derived offset, frozen W_P (+W_S sensitivity, no switching), frozen MOD, δ-profile linear+circular · `G1-3` CAL exactly 32 sacrificed frames listed + excluded from denominator, FIT32-SCORE-HELDOUT with disjoint held-out, same-CAL M0-vs-M2 NLL · `G1-4` H1/H2/H_total both models + both gate verdicts with U/Δ arithmetic · plus `G1-A` Phase-A closure (reproduction gate + five segment lists + disjointness matrix + freeze-config JSON). Evidence root: `workspace/m2_prior_validation/<ACQ>/{g1.json,cal_ids.json,delta_profiles.json,run_log.md}` per parent §10.
