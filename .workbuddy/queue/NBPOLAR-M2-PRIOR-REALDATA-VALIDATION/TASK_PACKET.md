# TASK PACKET — NBPOLAR-M2-PRIOR-REALDATA-VALIDATION (M2 ±1 CANDIDATE real-data validation)

PREPARATION ONLY. No implementation or execution authorized by this packet.
Per AGENTS.md §10.1: one complete frozen packet before delegation.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verified `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/`
- Change: `openspec/changes/nbpolar-prior-rebaseline/` — this packet implements T2–T7. T1/T8, G3, construction re-derivation are OUT.
- Venv (TimeTagger 2.22.6 + shim): `/home/karel_303/.venvs/timetagger/bin/python`
- Nature: G1 descriptive/non-claim; G2 one-shot Tier-Y. No FER/efficiency/qualification claim follows (G3 deferred).
- Terminology: M2 is a CANDIDATE everywhere, never "baseline". M0 at 1024-frame CAL is the incumbent as-deployed.

## Goal

Test the Stage-1 leading CANDIDATE on real data: whether the per-session ±1 parametric prior (M2)
replicates its synthetic held-out-NLL win and decode recovery on genuinely new SHG data at frozen K —
recording a bounded negative otherwise. G1 characterises ±1 structure decoder-free; G2 one-shot-decodes it.

## Non-Goals

No `sc.py`/algebra/transform change; no construction re-derivation for decode; no K increase; no pooled M1
unless D1 preconditions met; no FER/efficiency/promotion claim; no G3; no reopening of any D7-frozen item.
No K_total re-split decision in-packet (G2 decodes frozen K1=319/K2=6492 regardless; re-split is a later freeze).

## Impact Scope

New strict adapter module beside (never inside) `comparison_bench/.../formal_ir/nbpolar/prior.py` + `sc.py`-untouched
tests (Stage 1, by coder); `docs/SECURITY_MODEL.md` CAL-note only; additive outputs under `workspace/m2_prior_validation/`.
`src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/` are never written.

## §1 Frozen decisions (record, do not re-litigate)

D1: M2 per-session ±1 (strict 3-param triple q0,q+1,q−1; §4) is the CANDIDATE default. M1 pooled only if pooled CAL
unavoidable AND delay signs verified shared; FORBIDDEN if a delay-−50 source enters CAL. D2: CAL = 32 frames /
8192 symbols per session, SACRIFICED, excluded from key denominator; reveal bits (~18–22) diagnostic only, never
a λ_prior term; floor 8 frames without new freeze. 32 frames is a CANDIDATE budget, NOT a 1% accuracy guarantee
(S8 grid single-draw non-monotone: M2-1p5M 0.769% at n=2000 but 1.686% at n=5000; ideal iid SE at 8192 is
0.00804/0.00814 bits ≈1.0% of H2 and the two SE estimators disagree ~2.2×). D3: sacrifice-only accounting.
D4: fixed-f=1.3 (K_total 7053/7106, +33/+26) and fixed-K_total (f=1.2939/1.2952) CANNOT both hold under M2 H_total
(1p5M 0.8294, 2M 0.8356); G2 decodes frozen K1=319/K2=6492 regardless — the K_total choice belongs to a separate
later re-split freeze, not this packet. D5: first packet decodes FROZEN P16 order (len-32768 `l2_order`); re-derivation
deferred to its own freeze gated on arm-B success. D6: G1 NLL+δ-tail → G2 one-shot decode at frozen K → G3
independent session → G4 inventory; S9 NEVER FER evidence (synthetic 16 blocks, pro-M2 ground truth by design).
D7: Phase 0–1 algebra/transform, `sc.py`, Toeplitz/disclosure/`undetected` primitives, registries, negatives frozen.
Corrected mechanism (do not use old text): floor acts on probabilities (`body.py:141-143`) ⇒ penalty 40.4214 bits
(not 48); only 30.3509 of 44.7185 true −1 deltas per block fall in TRAIN-zero-−1 columns (not all ~45); 99.77% is
the fraction of zero CELLS, not of events hitting the floor — never use it to quantify affected symbols.

## §2 Data route (constrain to this; SHG `_2` reserved)

- FROZEN-SESSION REMAINDER (G1 NLL/H level only, NO decode, no new alignment): 101 frames total, NOT 261 —
1.5M VAL 2172–2212 (41) + 1.5M HOLD 2725–2766 (42) + 2M HOLD 3627–3644 (18). P20S consumed 128, P20T consumed 32.
After a 32-frame CAL only 69 frames remain (<1 128-frame block). Ladder ends by exhaustion (P20T acceptance).
δ-mass already verified here (`delta_mass_le1=1.0000`); use frozen derived pairs only. No SC call here.
**EXEMPTIONS (this population)**: exempt from G1-1 (no new alignment — frozen derived pairs) AND exempt from the
≥200k δ-tail characterisation gate (101 frames × 256 = 25,856 pairs physically cannot supply 200k). The full
G1-1~G1-4 four-gate set belongs to SHG `_1` ONLY; the remainder contributes an NLL/H comparison check only.
- PRIMARY G1+G2 POPULATION — SHG `_1` ONLY: `20260113_SHG_Type2PPLN_3s`
(`/mnt/d/Data/Raw Data/2026.1.13/SHG_Type2PPLN_3s_2026-01-13_162106/` primary + `.1` continuation).
G1: δ-tail characterisation on a large preregistered sample (≥200k pairs, TO-FREEZE §5) + prior fitting on the
preregistered 32-frame CAL + held-out NLL on a temporally separated segment. G2: one-shot decode on SHG `_1`
only, at frozen K1=319/K2=6492 and frozen P16 order.
- RESERVED FOR G3 — SHG `_2` (`.../SHG_Type2PPLN_3s_2_2026-01-13_162148/`): **PARTICIPATION DISCLOSURE — it is
NOT untouched.** The 2026-09-21 dual-rule census already ran decoder-free alignment (σ=114.4 ps), a full pairing grid,
and (N)-200 H_total=0.816770 on it (`docs/decision-log.md:5220`), and its cells entered the "usable" list that informed
the W_P=500 recommendation — so the primary-window choice is DATA-INFORMED from `_2` as well as `_1`. What has NEVER
happened: prior fitting, any decoder run, or M2 model selection using `_2`. From this packet onward it is FROZEN: no
G1/G2 preview, no model selection, no window choice, no pairing read. Any touch ⇒ STOP + blocker.
  **G3 CONTRACT**: when G3 runs, its alignment and window parameters must be INHERITED from `_1`'s frozen rules —
  never re-derived or tuned against `_2`'s known characteristics. G3's independence is decoder/model independence,
  NOT no-prior-contact independence; that distinction must be stated in any G3 result.
- Already-decoded segments are DEVELOPMENT data, never the confirmation sample. Read PRIMARY `.ttbin` ONLY via
`FileReader` (auto-follows `.1`; never concatenate `.1` manually — duplication). S10 usability maps used inherited
offset −50 and are CONDITIONAL until re-paired; never cite them as window evidence.

## §3 Allowed / Forbidden

READ: `formal_ir/nbpolar/{prior,sc,transform,algebra,empirical_genie_scaling}.py`, P16 orders artifact, intake
inventory, `docs/nbpolar/{STATE,MACRO_PLAN_20260921,REAL_DATA_FEASIBILITY_STRATEGY}.md`, change D1–D7, S8/S9/S10
`results.json` (numbers only, no re-derivation of facts in the packet header).
WRITE (additive): new `prior_m2.py` + focused tests + `scripts/m2_prior_validation.py` (Stage-1 deliverables);
`workspace/m2_prior_validation/<acq_id>/` outputs; `docs/SECURITY_MODEL.md` CAL note; packet STATUS only.
FORBIDDEN (hard stop): `experiments/run_e2e_pipeline.py`; `tools/longrun_*`/`minrerun_*`/`routeA_*`; any decoder on
protected data outside Stage-3 authorized blocks; writes into `results/` or `comparison_bench/outputs_comparison/`;
modification of `src/`/`experiments/`/`tools/`/`sc.py`/algebra/transform; any threshold/seed/K/window change after
freeze; any citation of S9 as FER evidence; any M1 pooling with a delay-−50 source in CAL; any read of SHG `_2`.

## §4 Stage 1 — Implementation (decoder-free; NO protected reads beyond already-derived artifacts)

Deliverables: (a) NEW strict 3-parameter M2 adapter — per-session triple (q0,q+1,q−1; q_rest→floor) → model-implied
full 1024×1024 P(A|B) → 1e-15 floor + per-B-column renorm → unchanged `derive_p1`/`derive_p2`/`SymbolMetric`.
S8's all-1024-δ fit is NOT equivalent on tailed data and SHALL NOT be reused. Mod-boundary semantics is an explicit
frozen parameter MOD (TO-FREEZE §5; recommended LINEAR_ONLY: 0↔1023 wrap jumps count as tail, conservative).
(b) M0-reproducing switch (incumbent table on demand, bit-exact); (c) K re-split code path via frozen
`select_empirical_split` validated on synthetic fixtures only — real-data (K1′,K2′) numbers DIAGNOSTIC-ONLY,
no construction decision; (d) `SECURITY_MODEL.md` CAL/prior-accounting note + inventory skeleton; (e) runner
`scripts/m2_prior_validation.py` exposing EXACT Stage-2/3 commands below (flags frozen, TO-FREEZE filled at freeze).

**CLI CONTRACT (single mechanism, no ambiguity)**: the runner SHALL accept ALL frozen parameters through ONE
`--freeze-config <path>` pointing at a JSON/YAML file containing every TO-FREEZE key in `STATUS.yaml`
(`B_tail`, `delta_min`, `g2_success_rule`, `g2_inconclusive_rule`, `g2_fail_rule`, `pairing_window_primary`,
`pairing_window_sensitivity`, `skip_frames`, `cal_split_rule`, `g2_blocks`, `tag_master`, `char_sample_pairs`,
`mod_boundary`, `a1_cal_ids`, `cal_frame_ids`, `heldout_frame_ids`, `disjointness_matrix`,
`block_formation_fallback`, `g2_arms`). The per-stage commands below name the flags for readability; the
authoritative source of values is the freeze-config file, and the runner SHALL refuse to run if any key is null
or absent. A missing/null key is a hard error, never a default.

| ID | Acceptance | Evidence |
|----|-----------|----------|
| I1 | Strict adapter matches independent literal oracle within frozen tolerances; switch reproduces M0 table bit-exact; MOD param toggles wrap handling per freeze | oracle-diff report + switch + MOD tests |
| I2 | Focused unit tests + T0 green; `git diff` shows ZERO change to `sc.py`/algebra/transform | pytest log + `git status` snippet |
| I3 | Re-split path replays frozen-selector semantics on synthetic fixtures; H-proportional path absent; real numbers diagnostic-only | replay log (K1/K2 recomputed by reviewer) |
| I4 | CAL-note merged (32-frame CANDIDATE budget sacrifice, reveal diagnostic, no λ_prior, M2 CANDIDATE label, claim scope unchanged) + inventory skeleton | doc diff + main-thread doc review |

## §5 Stage 2 — G1 freeze + execution (real data, DECODER-FREE)

Per-population G1 (remainder first, then SHG `_1`; SHG `_2` never): correlation-derived alignment per acquisition
(ONE frozen-params call: scan_range 409600, bin 100, accept `status==ok` AND `peak_to_bg>=10` + yield-sweep self-check;
NEVER inherit −50/+50/+50; remainder uses frozen derived pairs, no new alignment) → pairing at derived offset under
FROZEN windows (ONE primary W_P + ONE sensitivity W_S, TO-FREEZE; basis stated; post-hoc switching FORBIDDEN; any
window informed by the existing census is labelled DATA-INFORMED, not blind) → δ-mass profile `{0,±1,±2..k}` linear
AND circular under frozen MOD → skip FROZEN (TO-FREEZE; recommended 702 labelled INHERITED_NOT_DERIVED) →
CAL 32 sacrificed frames (listed) → RULE-FIT32-SCORE-HELDOUT (fit triple on ALL 32 frames; score on a temporally
separate held-out segment disjoint from CAL and from the char sample; no within-CAL split; split seed N/A) →
held-out NLL M0 vs M2 + H1/H2/H_total both models, SAME CAL for M0 vs M2.
Exact command (sibling venv; `--authorized` required, exits non-zero without it):
`/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --stage-g1-nll --acq-id <ACQ> --window-primary <W_P> --window-sensitivity <W_S> --skip <SKIP> --mod <MOD> --char-pairs <NCHAR> --out-root workspace/m2_prior_validation/<ACQ> --authorized`
G1-δtail gate (executable): statistic p̂=count(|δ|≥2)/n on the LARGE char sample only (denominator n=NCHAR pairs,
frozen MOD decides wrap). Confidence: one-sided 95% upper U (rule-of-three 3/n if zero obs, else Clopper-Pearson
upper). PASS iff U < B_tail (TO-FREEZE; recommended 2.0e-4: 40.4214×p×32768 ≤1%×26214 ⇒ p ≤1.98e-4 ≈2.0e-4, where
26214=32768×0.8 L2-budget and 262.14 is 1%). FAIL iff p̂ > B_tail (tail observed above budget). INCONCLUSIVE iff
p̂ ≤ B_tail ≤ U (sample too small to bound) ⇒ no proceed, bounded negative. NOTE: zero obs at n=8192 leaves
3.662e-4 > B_tail, so the 32-frame CAL can NEVER pass this gate — the large char sample (≥200k pairs, U=1.5e-5
on zero obs) is mandatory and separately preregistered.
G1-NLL gate (executable, matched-CAL descriptive only): statistic Δ=NLL_M0−NLL_M2 mean per-symbol on the held-out
segment (denominator n_heldout symbols; SAME 32-frame CAL for both; seed N/A under FIT32 rule). PASS iff
Δ > Δ_min (TO-FREEZE; recommended 0.020 bits/symbol ≈½ the S8 minimum 0.0366, ~12× the ~0.0016-bit SE at 200k).
FAIL iff Δ ≤ 0. INCONCLUSIVE iff 0 < Δ ≤ Δ_min ⇒ no proceed. CAVEAT (binding): matched 32-frame CAL is NOT the
incumbent — M0's as-deployed regime is 1024 frames and is measured only by G2 arm A1. This NLL never promotes M2.
STOP: δtail FAIL ⇒ premise FAILS on this source — record, do NOT proceed to Stage 3. ALIGN_FAIL ⇒ exclude
acquisition, continue; ALIGN_INCONSISTENT ⇒ STOP loudly. Remainder G1: NLL/H level only (32 CAL + 69 held-out).

| ID | Acceptance | Evidence |
|----|-----------|----------|
| G1-1 | Offset derived per acquisition (peak_center/sigma/to_bg recorded); no inherited −50/+50/+50; remainder reuses frozen pairs | per-acq `g1.json`: `align` + `yield_sweep` |
| G1-2 | Pairing at derived offset, frozen W_P (+W_S sensitivity, no switching), frozen MOD; δ-mass `{0,±1,±2..k}` linear+circular | `delta_profile_{linear,circular}` + window/mod record |
| G1-3 | CAL exactly 32 sacrificed frames, listed, excluded from denominator; FIT32-SCORE-HELDOUT with disjoint held-out; same-CAL M0-vs-M2 NLL | `cal_frame_ids` (32), `heldout_ids`, `nll_M0/nll_M2` |
| G1-4 | H1/H2/H_total for M0+M2; BOTH gates (δtail vs B_tail on NCHAR; NLL Δ vs Δ_min) evaluated with PASS/FAIL/INCONCLUSIVE per §5 rules | `H_*` table + gate verdicts + U/Δ arithmetic |

## §6 Stage 3 — G2 freeze + one-shot execution (Tier-Y; decoder on SHG `_1` only; decisive test)

Requires: G1 passed on SHG `_1`, independent Pre-EXECUTE PASS, explicit user authorization pasted in full. Three arms
at MATCHED frozen K1=319/K2=6492 with frozen P16 order on the SAME preregistered EVAL blocks (first N consecutive
128-frame blocks after CAL+held-out; disjoint; listed; TO-FREEZE; recommended 16 to match S9): A1 = M0 at its OWN
1024-frame sacrificed CAL (incumbent as-deployed reference); A2 = M0 at the matched 32-frame CAL (prior-form control);
B = M2 CANDIDATE at 32 frames. 64-bit Toeplitz tag per block from frozen TAG_MASTER (TO-FREEZE; rule
TAG_MASTER=EVAL_SEED+10000, value frozen at freeze time). One-shot: no rerun, no tuning, no seed change.
Freeze-time closure (all three TO-FREEZE in `STATUS.yaml`, all must be filled before G2-1 PASS): (a) `a1_cal_ids` — the
explicit frame list forming arm A1's own 1024-frame sacrificed CAL on SHG `_1`; (b) `disjointness_matrix` — a recorded
proof that A1-CAL / 32-frame CAL / char sample / held-out / EVAL are pairwise disjoint (the operator may not overlap
them, and any overlap invalidates the run); (c) `block_formation_fallback` — if the preregistered EVAL block count
cannot be formed from available frames, apply COMPLETE-BLOCKS-ONLY, else record INSUFFICIENT and return INCONCLUSIVE;
never pad, never reuse frames, never shrink N.
Measurement semantics (inherit `REAL_DATA_FEASIBILITY_STRATEGY.md` verbatim): per block `l1_exact`, `hard_l2_exact`,
`oracle_l2_exact`, `pair_exact`; first-error coordinate AND layer; raw TRAIN zero-count hits; fixed-floor (1e-15) hits
and their log loss; true-H-conditioned L2 NLL; candidate-H-conditioned L2 NLL; outcome taxonomy `exact` /
`verify_failed` / `undetected` / `decode_failed` / `nonfinite` / `resource_abort` — `undetected` NEVER merged.
G2 outcome gate (executable, preregistered BEFORE run): denominator = frozen block count N; per-arm 95% Wilson CI
(z=1.96) on exact fraction; arms share EVAL blocks (paired) but CIs are per-arm conservative as in S9. SUCCESS iff
Wilson-lower(B) > Wilson-upper(A2) (strict non-overlap on the matched-CAL pair); A1 reported as incumbent reference
with no gate (descriptive). FAIL iff point(B) ≤ point(A2). INCONCLUSIVE iff point(B) > point(A2) but CIs overlap ⇒
bounded negative, no tuning, no rerun. No FER/efficiency reading (G3 deferred).
Exact command:
`/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --stage-g2-decode --acq-id 20260113_SHG_Type2PPLN_3s --arms A1,A2,B --blocks <N> --k1 319 --k2 6492 --tag-master <FROZEN> --window-primary <W_P> --mod <MOD> --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/g2 --authorized`

| ID | Acceptance | Evidence |
|----|-----------|----------|
| G2-1 | Freeze (N/tag/window/mod/skip/CAL IDs/char-size/B_tail/Δ_min/budget) + Pre-EXECUTE PASS + pasted authorization all recorded BEFORE run | `g2_freeze.md` + review + auth ref |
| G2-2 | A1-vs-A2-vs-B one-shot executed exactly once at frozen K/order, preregistered blocks, 64-bit tag per block | `per_block_outcomes.jsonl` (N rows/arm) |
| G2-3 | Full §6 measurement set per block with `undetected` isolated + `resource_abort`; disclosure bits, wall/RSS per block | outcome table + `disclosure_bits` + `wall_s`/`rss` + NLL pair |
| G2-4 | No rerun/tuning/seed change; target-output absence verified pre-run; SUCCESS/FAIL/INCONCLUSIVE per preregistered Wilson rule | run log + pre-run absence check + CI arithmetic |

## §7 Stage 4 — Pre-RESULT review + adjudication

| ID | Acceptance | Evidence |
|----|-----------|----------|
| R1 | Independent reviewer-go Pre-RESULT PASS (B_tail/Δ_min/Wilson rules, leakage decomposition, `undetected` isolation, per-source breakdown, disclosure accounting vs artifacts) BEFORE any publication/commit | `PRE_RESULT_REVIEW.md` PASS |
| R2 | Main-thread adjudication recorded (adopt / revise-required / bounded negative); G3 (SHG `_2`) + re-split + re-derivation explicitly deferred to own freezes | decision entry; no claim beyond packet scope |

## §8 Acceptance-ID list (operator reports IDs, not restatements)

I1, I2, I3, I4, G1-1, G1-2, G1-3, G1-4, G2-1, G2-2, G2-3, G2-4, R1, R2.

## §9 Budget (binding stop rule) + stop rules

Budget: Stage 2 decoder-free pairing+NLL+char sample ≈ ≤600 s wall / 2 GiB RSS per acquisition (single-threaded;
larger than before because the ≥200k-pair char sample is mandatory). Stage 3: 3 arms × 16 blocks × 2 SC calls × ~6 s
≈ 576 s + overhead ⇒ CAP 900 s wall / 2 GiB RSS single-threaded (S9 anchor: 680 s / 0.96 GB for 3 arms × 16 blocks).
Exceeding CAP ⇒ STOP, record as blocker (no tuning to fit). Stops: §5/§6 STOP lines; any §3 FORBIDDEN touch (incl.
any SHG `_2` read) ⇒ STOP; G1 INCONCLUSIVE or G2 INCONCLUSIVE-by-rule ⇒ bounded negative, no tuning; G3/re-split/
re-derivation attempted in-packet ⇒ STOP (needs own freeze).

## §10 Return conditions (exactly two)

1. All-frozen-items-complete: per-ID PASS/FAIL/INCONCLUSIVE with evidence paths + per-population NLL/H table
(Stage 2) / per-block outcome table with full §6 semantics (Stage 3) + run log path. 2. Concrete blocker: failing
command + exact error/traceback (or adverse verdict + ID) + attempted remedies + the SINGLE decision needed.
"Still incomplete" is not a report. Roots: `workspace/m2_prior_validation/<ACQ>/{g1.json,cal_ids.json,
delta_profiles.json,run_log.md,g2/per_block_outcomes.jsonl}`. Nothing under `results/` or
`comparison_bench/outputs_comparison/`.

## Tasks (coder-agent order)

1. Implement strict adapter + switch + MOD param + oracle-matched tests (I1,I2). 2. Frozen-selector re-split path on
synthetic fixtures, diagnostic-only real numbers (I3). 3. SECURITY_MODEL CAL note + inventory skeleton (I4).
4. Build runner with the §CLI-CONTRACT `--freeze-config` interface (all 19 TO-FREEZE keys required, null/absent ⇒
hard error, never a default). 5. Freeze G1 (W_P/W_S/skip/MOD/NCHAR/B_tail/
Δ_min/CAL-split) → execute §5 → evaluate both gates. 6. Freeze G2 (N/tag) → Pre-EXECUTE → one-shot §6 → Wilson gate.
7. Pre-RESULT (R1) → adjudication (R2). T2–T7 only; G3/re-split/re-derivation need new freezes.
