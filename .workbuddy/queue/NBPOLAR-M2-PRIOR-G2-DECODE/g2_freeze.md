# G2 FREEZE — NBPOLAR-M2-PRIOR-G2-DECODE (one-shot three-arm decode on SHG `_1`, w=200/CIRCULAR)

Per AGENTS.md §6: change behavior/architecture ⇒ OpenSpec change first; §10.1: one complete frozen packet before
delegation. This document authorizes NOTHING by itself. Execution requires (in order): (1) independent freeze review
PASS, (2) independent Pre-EXECUTE PASS, (3) explicit user authorization pasted in full, (4) Pre-RESULT before any
publication/commit.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/`
- Change: `openspec/changes/nbpolar-prior-rebaseline/` (T6 freeze + T7 execute; T5 done via G1R2)
- Parent spec: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md` §5 (G2) + §6 (Stage 4)
- Venv: `/home/karel_303/.venvs/timetagger/bin/python`
- Nature: **Tier-Y decision gate (claim-bearing execution)**. M2 is a CANDIDATE, never "baseline".

## Goal

Decide, on SHG `_1` real data at frozen K and frozen P16 order, whether the M2 ±1 CANDIDATE restores complete blocks
relative to a matched-CAL M0 control — and, for the first time on SHG, measure the incumbent as-deployed regime.

## Non-Goals

No `sc.py`/algebra/transform change; no construction re-derivation; no K increase and no K re-split; no M1 pooling
(D1 precondition absent: one source only, no verified shared-delay pool); no G3; no FER/efficiency/qualification/
promotion claim; no post-freeze threshold/seed/K/window/MOD change; no rerun or tuning after a verdict.

## Impact Scope

WRITE: `scripts/m2_prior_validation.py` (the `--stage-g2-decode` body — the ONLY code file); focused tests
`comparison_bench/tests/test_nbpolar_m2_g2_decode.py`; `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/`
outputs; packet `STATUS.yaml` (ids/counters/artifacts only) + `g2_freeze_config.json`.
**Routing**: G2 writes ONLY to its own packet dir (`NBPOLAR-M2-PRIOR-G2-DECODE`, config `g2_freeze_config.json`) and
its own out-root; it SHALL NOT write to any G1/G1R2 packet dir (blocking-fix B3).
READ (frozen sources): `formal_ir/prior_m2.py`; `formal_ir/nbpolar/{prior,sc,empirical_genie_scaling,two_layer}.py`;
P16 `construction_and_allocation.json` (orders + K); parent packet §5/§6; `REAL_DATA_FEASIBILITY_STRATEGY.md`;
`docs/troubleshooting.md` (TimeTagger traps); G1R2 outputs (contract values).
FORBIDDEN (hard stop): modify `sc.py`/`algebra.py`/`transform.py` or anything under `src/`, `experiments/`, `tools/`,
`results/`, `comparison_bench/outputs_comparison/`, `formal_ir/nbpolar/`; construct the M1 pooled model; pad/reuse/
borrow CAL or EVAL frames; open SHG `_2`; write outside `workspace/`; add checksums/atomic writes/locking/retry
frameworks (AGENTS.md §5.7).

## Contract values (this freeze; inherit + extend the G1R2 contract)

Population: `20260113_SHG_Type2PPLN_3s` (SHG `_1`) only. SHG `_2` remains FROZEN for G3; any touch ⇒ STOP.

| # | Key | Value | Basis |
|---|---|---|---|
| 1 | `pairing_window_primary` | 200 | inherited from G1R2; w=200 CIRCULAR tail = 0 (S11 full-stream measurement) |
| 2 | `pairing_window_sensitivity` | 500 | former primary; sensitivity readout only, no switching |
| 3 | `mod_boundary` | CIRCULAR | user decision; wrap events are ±1 time-bin errors (S11 offset-scan asymmetry 40→154→294→466→632) |
| 4 | `skip_frames` | 702 | `INHERITED_NOT_DERIVED`, never re-derived per acquisition |
| 5 | `cal_split_rule` | `RULE-FIT32-SCORE-HELDOUT` | inherited verbatim (no new token). Each arm fits on **its OWN sacrificed CAL**: A1 = post-skip 0–1023 (1024×256 = 262,144 pairs), A2 and B = post-skip 1024–1055 (8,192 pairs); decode applies to EVAL only; no within-CAL split; seed N/A |
| 6 | `g2_blocks` | 14 | **EVAL = post-skip frames 2398–4189** (1,792 frames = 14×128); 16-block layout infeasible at w=200 (post-skip budget 4,219 frames vs 4,446 required, deficit 227) — recorded deviation, not a preference |
| 7 | `tag_master` | `2026103001` | **INHERITED from G1R2 (value-identical), not "fresh"** — G1R2 was decoder-free and consumed **no** tag, so this stream is unused and safe to reuse; no other packet consumes it. (CORRECTION 2026-09-22: the pre-review text claimed "fresh (no existing packet uses 2026093001/2026103001)", which is false — see `g1r2_freeze_config.json`.) Rule `TAG_MASTER = EVAL_SEED + 10000`, `EVAL_SEED = 2026093001` |
| 8 | `char_sample_pairs` | 200192 | inherited (CHAR frames 1056–1837; ≥200k) |
| 9 | `cal_frame_ids` | 32-frame CAL = post-skip frames 1024–1055 | matched for A2 and B |
| 10 | `a1_cal_ids` | 1024-frame CAL = post-skip frames 0–1023 | A1's own sacrificed incumbent budget |
| 11 | `mod_boundary` (repeat) | CIRCULAR | MOD is frozen here; G2 never switches it |
| 12 | `g2_arms` | `[A1_M0_1024f_incumbent, A2_M0_32f_matched, B_M2_32f_candidate]` | see Arms below |

**Output routing (CORRECTION 2026-09-22, blocking-fix B3):** G2 uses **its own** packet dir
`.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/` and config name `g2_freeze_config.json`. The G2 body
SHALL NOT write to any G1 (`NBPOLAR-M2-PRIOR-G1-REALDATA-NLL`) or G1R2 (`NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR`)
packet dir — routing must be **stage-keyed** (`--stage-g2-decode` ⇒ G2 packet dir), not window-only, so the w=200
contract cannot be reused to overwrite adjudicated G1R2 evidence.

**Closure mechanism (CORRECTION 2026-09-22, blocking-fix B2):** `--closure-only` applies to `--stage-g1-nll` only
(the runner hard-refuses it with `--stage-g2-decode`). G2's Phase-A closure therefore **reuses the G1R2 closure
literals verbatim** (ledger 4,219; reserve 4190–4218; A1-CAL 0–1023; CAL32 1024–1055; HELDOUT 1838–2397;
disjointness proof) by copying them into `g2_freeze_config.json` under this packet dir — **no G2 `--closure-only`
invocation exists**. The EVAL block list (2398–4189 = 14 blocks) is emitted at the same time.

**Canonical out-root (CORRECTION 2026-09-22, blocking-fix B4):** `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/`
(matching the existing `…_g1r2` sibling convention). The other spelling (`…/20260113_SHG_Type2PPLN_3s/g2/`) is
**withdrawn** — the G2-4 target-output absence check requires exactly one canonical path.

**Construction provenance (clarification N2):** canonical path
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`,
carrying K1=319/K2=6492 and the len-32768 `l1_order`/`l2_order`; the pinned digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` is the **inner P16 procedure digest**
(the wrapper file's own sha256 differs — expected, P17-established); the G2 body reuses the P17 digest-verification
procedure for the orders, and must pin the canonical path rather than re-deriving anything.

Inherited unchanged from `g1_freeze.md` (G1) / G1R2: `B_tail 2.0e-4`, `delta_min 0.020`, `g2_success_rule`,
`g2_inconclusive_rule`, `g2_fail_rule`, `heldout_frame_ids` (1838–2397), `disjointness_matrix`,
`block_formation_fallback` = COMPLETE-BLOCKS-ONLY else INSUFFICIENT ⇒ INCONCLUSIVE (never pad/reuse/shrink).

**Frozen decode constants**: K1 = **319**, K2 = **6492** (G2 decodes at these; no re-split, no increase);
P16 `construction_and_allocation.json`, file digest **055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b**
(carries K1=319/K2=6492 and the len-32768 `l1_order`/`l2_order`); N = 32768; 64-bit Toeplitz tag per block;
chunk_rows 512; floor 1e-15. Orders are REUSED from P16 (D5: frozen P16 order for the first packet); no re-derivation.

## Arms (matched K, same EVAL blocks, paired)

- **A1** = M0 (incumbent raw-MLE + 1e-15 floor) at its OWN 1024-frame sacrificed CAL (post-skip 0–1023) — incumbent
  as-deployed reference; reported, no gate.
- **A2** = M0 at the matched 32-frame CAL (1024–1055) — prior-form control; the gate comparator.
- **B** = M2 CANDIDATE (±1, CIRCULAR) at the matched 32-frame CAL (1024–1055).

All three arms share the 14 EVAL blocks (2398–4189), the frozen P16 order and K1/K2, and one 64-bit Toeplitz tag per
block from `tag_master`. CALs are sacrificed and excluded from any key denominator. Segment disjointness
(A1-CAL / CAL32 / CHAR / HELDOUT / EVAL) is proved by the closure ledger; any overlap invalidates the run.

## Gates (preregistered BEFORE the run; executable)

Wilson 95% (z=1.96) per arm on the exact fraction over the 14 frozen blocks (paired EVAL blocks, per-arm conservative CI,
as in S9): **SUCCESS** iff Wilson-lower(B) > Wilson-upper(A2) (strict non-overlap, matched-CAL pair);
**FAIL** iff point(B) ≤ point(A2); **INCONCLUSIVE** iff point(B) > point(A2) with overlapping CIs ⇒ bounded negative,
no tuning, no rerun. A1 carries no gate. `undetected` is isolated, never merged into success/FER.

## Measurement semantics (verbatim from `REAL_DATA_FEASIBILITY_STRATEGY.md`)

Per block: `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`, `pair_exact`; first-error coordinate AND layer; raw TRAIN
zero-count hits; fixed-floor (1e-15) hits and their log loss; true-H-conditioned L2 NLL; candidate-H-conditioned L2 NLL;
outcome taxonomy `exact`/`verify_failed`/`undetected`/`decode_failed`/`nonfinite`/`resource_abort`.
Plus: disclosure recount (key/public bits, mismatch 0), tag invocations, wall_s and RSS per block, SC/tag call counts.

**Caveats carried into the G2 record (per review N1; must appear in any interpretation of a verdict):**
(a) the census far-offset accidental baseline is **structured, not uniform** (S11 R4: far-offset tail ≈ 0.40 vs
uniform 0.997), so the w=200 accidental estimate (0.0058) must NOT be read as a uniform-accidental level;
(b) **q_rest = 0 is a weak statement** at a 32-frame CAL (zero-observation upper bound 3/8192 = 3.66e-4) — G2 is
precisely the test of whether that matters, so a FAIL or INCONCLUSIVE verdict must NOT later be misread as
"the ±1 premise was validated"; (c) w=200 keeps a **timing-truncated population** (c0 count is identical across
windows but jitter-heavy coincidences are preferentially dropped) — state it in any rate/efficiency/leakage sentence.

## Initial ledger values (from the G1R2 closure, recomputed)

- w=200 (N)-pairing: 1,259,992 pairs; pre-skip frames 4,921; post-skip complete frames **4,219** (216 trailing pairs dropped).
- Layout: A1-CAL 0–1023 (1024) | CAL32 1024–1055 (32) | CHAR 1056–1837 (782) | HELDOUT 1838–2397 (560) | EVAL 2398–4189 (1792)
  = 4,190 allocated; RESERVE 4190–4218 (29) — never used by G2.
- EVAL seed: `2026093001` **INHERITED from G1R2 (value-identical; G1R2 was decoder-free, so no seed/tag stream was
  ever consumed)** ⇒ tag_master `2026103001` (2026093001 + 10000). Not "fresh" — see row 7 and the B1 correction.

## Budget / stop rules

Budget ≤ 900 s wall / 2 GiB RSS, single-threaded. **CORRECTION 2026-09-22 (blocking-fix S2):** the measurement
semantics inherited from `REAL_DATA_FEASIBILITY_STRATEGY.md` require **3 SC calls per block** (L1, hard-L2, and the
third for `oracle_l2_exact`), not 2 — the pre-correction arithmetic (3 arms × 14 blocks × 2 ≈ 504 s) understated it.
Correct arithmetic: **3 arms × 14 blocks × 3 = 126 SC calls ≈ 756 s + overhead**, still inside the 900 s cap but with a
much thinner margin; the body counts all 3 calls and enforces the stop. The measurement set is NOT reduced to fit the
budget. Exceeding ⇒ STOP, record as blocker (no tuning to fit); SC-call count is reported per run. Stops: δ-tail FAIL ⇒ no proceed; any §3 FORBIDDEN touch ⇒ STOP;
any SHG `_2` read ⇒ STOP; verdict rendered ⇒ no rerun/tuning; every TO-FREEZE must be non-null (missing/null ⇒ hard error,
never a default). Ambiguity ⇒ STOP and report (second return condition), never guess.

## Tasks (operator order)

1. Implement `--stage-g2-decode` body in `scripts/m2_prior_validation.py` per Spec 1 (preserve every Stage-1/G1R2 guard).
2. Focused tests `test_nbpolar_m2_g2_decode.py` per Spec 2 (fake runner only; never invoke the production decode from tests).
3. Freeze closure: emit `g2_freeze_config.json` (all TO-FREEZE non-null) + the closure keys for A1-CAL/CAL32/HELDOUT/dedup.
4. Pre-EXECUTE (independent) + user authorization (verbatim) ⇒ one-shot run ⇒ Wilson gate ⇒ Pre-RESULT ⇒ main-thread adjudication.
