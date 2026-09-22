# TASK PACKET — NBPOLAR-M2-PRIOR-G3-CONFIRM (independent-session confirmation on SHG `_2`)

**GATED PACKET — becomes operative ONLY if the G2 adjudication ADOPTS M2 (SUCCESS).**
If G2 is FAIL or INCONCLUSIVE, this packet is **VOID** and must not be dispatched. Per AGENTS.md §10.1:
one complete frozen packet before delegation; authorizes NOTHING until verbatim user authorization flips `STATUS.yaml`.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/`
- Change: `openspec/changes/nbpolar-prior-rebaseline/` — D6 gate **G3** (independent-session confirmation).
- Venv: `/home/karel_303/.venvs/timetagger/bin/python`
- Nature: Tier-Y one-shot confirmation. M2 remains a CANDIDATE until G3 passes; no FER/efficiency/qualification
  claim before G3 (and none from G3 alone — see Non-Goals).

## Goal

Confirm the M2 CANDIDATE on an **independent session** (SHG `_2`), using rules **inherited** from SHG `_1`'s frozen
contract, with the same matched-CAL three-arm design and the preregistered Wilson gate.

## Non-Goals

No re-derivation of alignment/window/MOD/skip against SHG `_2`; no model selection on SHG `_2`; no tuning; no G4
exhaustive inventory work; no FER/efficiency/qualification/promotion claim; no reuse of SHG `_1` frames.

## Impact Scope

WRITE: `scripts/m2_prior_validation.py` (a G3 stage/body — the ONLY code file, additive, preserving every
Stage-1/G1R2/G2 guard); focused tests `comparison_bench/tests/test_nbpolar_m2_g3_confirm.py`;
`workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3/` outputs; this packet's `STATUS.yaml`
(ids/counters/artifacts) + `g3_freeze_config.json`.
FORBIDDEN (hard stop): modify `sc.py`/`algebra.py`/`transform.py`/`prior_m2.py` or anything under
`formal_ir/nbpolar/`, `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`;
any SHG `_2` read **before** this packet's own Phase-A closure (the reservation below); writes outside scope;
checksums/atomic writes/locking/retry frameworks.

## SHG `_2` reservation + participation disclosure (recorded verbatim)

SHG `_2` (`20260113_SHG_Type2PPLN_3s_2`) is NOT untouched history: the 2026-09-21 dual-rule census already ran
**decoder-free** alignment (σ = 114.4 ps), a full pairing grid, and (N)-200 `H_total = 0.816770` on it, and its cells
entered the "usable" list that informed the W_P recommendation. **Never done on SHG `_2`: prior fitting, any decoder
run, or M2 model selection.** G3's independence is **decoder/model independence, NOT no-prior-contact independence**
— that distinction must be stated in any G3 result. From G1 onward no G1/G2 preview, model selection, window choice
or pairing read touched SHG `_2`; G3's own Phase-A closure is the first permitted contact.

## Contract (INHERITED from SHG `_1`'s frozen rules — never re-derived or tuned against SHG `_2`)

- Pairing rule (N) narrow nearest-unique; **W_P = 200**, W_S = 500 (sensitivity readout only, no switching);
  **MOD = CIRCULAR**; **skip = 702** (`INHERITED_NOT_DERIVED`); N = 32768; 128-frame blocks; floor 1e-15;
  chunk_rows 512; 64-bit Toeplitz tag per block.
- **Alignment**: the METHOD is inherited (scan_range 409600, bin 100, accept `status==ok AND peak_to_bg>=10`
  + yield-sweep self-check; never inherit an offset VALUE). The offset for SHG `_2` is derived by that method and
  **MUST reproduce the census value σ ≈ 114.4 ps** as a reproduction check; mismatch ⇒ STOP loudly
  (ALIGN_INCONSISTENT). (Census already-derived alignment is decoder-free and is the reproduction target, not a
  substitute for deriving it.)
- **Construction/K**: frozen P16 `construction_and_allocation.json` (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), **K1 = 319 / K2 = 6492** — no re-split
  (D4 deferred), no increase.
- **tag_master = 2026110101** (rule TAG_MASTER = EVAL_SEED + 10000, **EVAL_SEED = 2026100101**; fresh — no collision
  with S9 2026092101/2026092117, P20 2026092000–2026092400, G1 2026092201, G1R2/G2 2026093001, SCL reserve
  2026092517, L2 reserve 2026092617).
- Gates inherited: B_tail 2.0e-4, delta_min 0.020, Wilson 95% (z=1.96) SUCCESS/FAIL/INCONCLUSIVE rules;
  `undetected` isolated; disclosure recount; COMPLETE-BLOCKS-ONLY fallback else INSUFFICIENT ⇒ INCONCLUSIVE.

## Phase A — closure (first permitted SHG `_2` contact; decoder-free)

Derive alignment (reproduction check vs census σ ≈ 114.4), pair at W_P=200, apply skip-702, enumerate the post-skip
ledger, and allocate: A1-CAL (1024 frames, if the ledger allows) | CAL32 (32) | CHAR (782) | HELDOUT (560) |
EVAL blocks | RESERVE. **Target EVAL = 14 complete 128-frame blocks** (the G2 resolution); if fewer than 14 complete
blocks can be formed ⇒ COMPLETE-BLOCKS-ONLY and, if < 14, record **INSUFFICIENT ⇒ INCONCLUSIVE** (never pad/reuse;
never shrink N). Emit `cal_frame_ids`, `heldout_frame_ids`, `a1_cal_ids`, `disjointness_matrix`, `g3_blocks`, and the
complete `g3_freeze_config.json`. Budget ≤ 300 s / 2 GiB.

## Arms (matched K, same EVAL blocks, paired)

- **A1** = M0 at its own 1024 sacrificed frames (descriptive, no gate) — only if the ledger allows; else dropped and
  recorded.
- **A2** = M0 at matched 32 frames — gate comparator.
- **B** = M2 CANDIDATE (CIRCULAR) at matched 32 frames.

## Gate

Denominator = `g3_blocks` (target 14). SUCCESS iff Wilson-lower(B) > Wilson-upper(A2); FAIL iff point(B) ≤ point(A2);
INCONCLUSIVE iff point(B) > point(A2) with overlap ⇒ bounded negative, no tuning, no rerun. A1 no gate.

## Measurement semantics

As G2: per block `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`, `pair_exact`; first-error coordinate AND layer; raw
zero-count hits; floor hits + log loss; true-H and candidate-H L2 NLL; taxonomy with `undetected` isolated;
disclosure bits recount; wall/RSS; SC and tag counts. Plus the G3 participation-disclosure statement in every output.

## Caveats carried

(a) far-offset accidental baseline is structured, not uniform; (b) q_rest = 0 is weak at a 32-frame CAL
(zero-obs 3/8192 = 3.66e-4); (c) w=200 keeps a timing-truncated population — state in any rate/efficiency/leakage
sentence; (d) G3 is the FIRST decoder contact with SHG `_2`, and its independence claim is decoder/model
independence only.

## Acceptance IDs → evidence

`G3-0` (phase-0 code + tests green) · `G3-A` (closure: alignment reproduction, ledger, keys, config) ·
`G3-1` (freeze + Pre-EXECUTE PASS + authorization recorded before decode) · `G3-2` (one-shot decode, per-block
outcomes) · `G3-3` (measurement set + disclosure accounting + participation statement) ·
`G3-4` (no rerun/tuning; Wilson verdict) · `R1` (Pre-RESULT PASS) · `R2` (main-thread adjudication).

## Stop rules

Budget ≤ 900 s wall / 2 GiB RSS single-threaded (decode phase); exceeded ⇒ STOP (no tuning). Any SHG `_2` contact
before this packet's Phase-A closure ⇒ STOP + blocker. Alignment reproduction mismatch ⇒ STOP loudly. Verdict ⇒ no
rerun/tuning. Ambiguity ⇒ STOP (second return condition), never guess.

## Return (exactly two)

1. All-complete: per-ID PASS with evidence paths + logs + gate arithmetic + scoped `git status`.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision needed.

## Frozen resolutions

R1: G3 must not be dispatched unless the G2 adjudication ADOPTS M2 — the gate is verified by the main thread before
dispatch, not assumed. R2: all contract values are INHERITED; the only SHG `_2`-specific value is the derived
alignment offset (checked against census σ ≈ 114.4). R3: a G3 SUCCESS does not by itself license a composable
net-key or FER claim — D6's G4 inventory and the Stage-3 measurement set remain outstanding.
