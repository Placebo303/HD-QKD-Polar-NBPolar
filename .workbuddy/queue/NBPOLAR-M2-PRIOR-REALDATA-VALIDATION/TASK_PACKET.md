# TASK PACKET — NBPOLAR-M2-PRIOR-REALDATA-VALIDATION (M2 ±1 prior real-data validation)

PREPARATION ONLY. No implementation or execution authorized by this packet.
Per AGENTS.md §10.1: one complete frozen packet before delegation.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verified via `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/`
- Change: `openspec/changes/nbpolar-prior-rebaseline/` — this packet implements T2–T7. T1/T8, G3, construction re-derivation are OUT.
- Venv (TimeTagger 2.22.6 + `sys.modules["TimeTagger"]` shim): `/home/karel_303/.venvs/timetagger/bin/python`
- Nature: G1 descriptive/non-claim; G2 one-shot Tier-Y. No FER/efficiency/qualification claim follows this packet (G3 deferred).

## Goal

Test the Stage-1 leading hypothesis on real data: whether the per-session ±1 parametric prior (M2) replicates its
synthetic held-out-NLL win and decode recovery on genuinely new SHG data at frozen K — replacing the disproven M0
floor regime as the prior baseline if G1+G2 pass, recording a bounded negative otherwise.

## Non-Goals

No `sc.py`/algebra/transform change; no construction re-derivation for decode; no K increase; no pooled M1 unless its
preconditions are met; no FER/efficiency/promotion claim; no G3; no reopening of any D7-frozen item or negative result.

## Impact Scope

New small adapter module beside (never inside) `comparison_bench/.../formal_ir/nbpolar/prior.py` + `sc.py`-untouched
tests (Stage 1, by coder); `docs/SECURITY_MODEL.md` CAL-note only; additive outputs under `workspace/m2_prior_validation/`.
`src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/` are never written.

## §1 Frozen decisions (record, do not re-litigate)

D1: M2 per-session ±1 (q0,q±1 + direction sign) is the default. M1 pooled only if pooled CAL unavoidable AND delay
signs verified shared; FORBIDDEN if a delay-−50 source enters CAL. D2: CAL = 32 frames / 8192 symbols per session,
SACRIFICED (excluded from key denominator); reveal bits (~18–22) diagnostic only; floor 8 frames without new freeze.
D3: sacrifice-only accounting, no λ_prior term; release-style in-sample estimation rejected as default. D4: K_total
frozen on f=1.3 literal; (K1,K2) re-derived via accepted `select_empirical_split` at constant total; H-proportional
split BANNED; P19 `l2_plus` (+512) already failed 0/3 — rebalance only, never increase. D5: first packet decodes at
FROZEN P16 (K1=319/K2=6492, `l2_order` len 32768); re-derivation deferred to its own freeze gated on arm-B success.
D6: G1 NLL+δ-mass → G2 one-shot decode at frozen K → G3 independent session → G4 inventory; S9 NEVER FER evidence.
D7: Phase 0–1 algebra/transform, `sc.py`, Toeplitz/disclosure/`undetected` primitives, registries, all negatives frozen.
Sequencing: T3 real-data (K1′,K2′) numbers are DIAGNOSTIC-ONLY in this packet (need Stage-2 H); G2 decodes frozen K only.

## §2 Data scope (constrain to this)

- PRIMARY: SHG pair, genuinely new, never decoded, abundant (N-rule ≈1.26M pairs ⇒ ~4900 frames each):
  `20260113_SHG_Type2PPLN_3s` (`/mnt/d/Data/Raw Data/2026.1.13/SHG_Type2PPLN_3s_2026-01-13_162106/*.ttbin`) and
  `..._3s_2` (`.../SHG_Type2PPLN_3s_2_2026-01-13_162148/*.ttbin`). σ≈112.5/114.4; (N)-w200 coverage ≈0.92
  (marginally biased under strict ≥0.95); δ-mass ≤1 NOT yet verified — Stage 2 establishes it.
- RESERVED for G3 (not this packet): 261-frame never-decoded remainder (1.5M VAL 2172–2212, 1.5M HOLD 2725–2766,
  2M VAL 2827–2915, 2M HOLD 3556–3644 = 66,816 pairs; minus 32-frame CAL ⇒ 229 frames ≈ 1.8 blocks — thin, NLL-level
  at most). Recommended G3 session is SHG `_2`, not this remainder (see return notes).
- Already-decoded segments are DEVELOPMENT data, never the confirmation sample. Read PRIMARY `.ttbin` ONLY
  (`FileReader` auto-follows `.1`; concatenation duplicates every event). Alignment is correlation-derived PER
  ACQUISITION, never inherited (`decision-log.md:5185`); S10 inherited-offset maps are conditional until re-paired.

## §3 Allowed / Forbidden

READ: `formal_ir/nbpolar/{prior,sc,transform,algebra,empirical_genie_scaling}.py`, P16 orders artifact, intake
inventory, `docs/nbpolar/{STATE,MACRO_PLAN_20260921,REAL_DATA_FEASIBILITY_STRATEGY}.md`, change D1–D7.
WRITE (additive): new `prior_m2.py` + focused tests + `scripts/m2_prior_validation.py` (Stage-1 deliverables);
`workspace/m2_prior_validation/<acq_id>/` outputs; `docs/SECURITY_MODEL.md` CAL note; packet STATUS only.
FORBIDDEN (hard stop): `experiments/run_e2e_pipeline.py`; `tools/longrun_*`/`minrerun_*`/`routeA_*`; any decoder on
protected data outside Stage-3 authorized blocks; writes into `results/` or `comparison_bench/outputs_comparison/`;
modification of `src/`/`experiments/`/`tools/`/`sc.py`/algebra/transform; any threshold/seed/K change after freeze;
any citation of S9 as FER evidence; any M1 pooling with a delay-−50 source in CAL.

## §4 Stage 1 — Implementation (decoder-free; NO protected reads beyond already-derived artifacts)

Deliverables: (a) new adapter module (per-session triple → model-implied 1024×1024 P(A|B) → 1e-15 floor +
per-B-column renorm → unchanged `derive_p1`/`derive_p2`/`SymbolMetric`), with a switch reproducing the incumbent on
demand; (b) K re-split code path via frozen `select_empirical_split` (validated on synthetic fixtures; real-data
numbers diagnostic-only); (c) `SECURITY_MODEL.md` CAL/prior-accounting note + inventory skeleton; (d) runner
`scripts/m2_prior_validation.py` exposing EXACT Stage-2/3 commands below (flags frozen, block/tag TO-FREEZE).

| ID | Acceptance | Evidence |
|----|-----------|----------|
| I1 | Adapter matches independent literal oracle within frozen tolerances; switch reproduces M0 table bit-exact | oracle-diff report + switch test |
| I2 | Focused unit tests + T0 green; `git diff` shows ZERO change to `sc.py`/algebra/transform | pytest log + `git status` snippet |
| I3 | Re-split path replays frozen-selector semantics on synthetic fixtures; H-proportional path absent | replay log (K1/K2 recomputed by reviewer) |
| I4 | CAL-note merged (32-frame sacrifice, reveal diagnostic, no λ_prior, claim scope unchanged) + inventory skeleton | doc diff + main-thread doc review |

## §5 Stage 2 — G1 freeze + execution (real data, DECODER-FREE; answers "does the channel have ±1 structure")

Per acquisition (PRIMARY SHG `_1` first; `_2` after `_1` G1 passes — both before any Stage 3): correlation-derived
alignment (ONE frozen-params call: scan_range 409600, bin 100, accept `status==ok` AND `peak_to_bg>=10` + yield-sweep
self-check) → pairing at derived offset under FROZEN (N) window TO-FREEZE → δ-mass profile `{0,±1,±2..k}` linear AND
circular → skip TO-FREEZE → CAL 32 sacrificed frames → split-A fit / split-B score (seed 20260920, SAME split for M0
vs M2, both fit on the 32-frame CAL) → held-out NLL M0 vs M2 + H1/H2/H_total both models.
Exact command (sibling venv; `--authorized` required, exits non-zero without it):
`/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --stage-g1-nll --acq-id <ACQ> --out-root workspace/m2_prior_validation/<ACQ> --authorized`

| ID | Acceptance | Evidence |
|----|-----------|----------|
| G1-1 | Offset derived per acquisition (peak_center/sigma/to_bg recorded); no inherited −50/+50/+50 | per-acq `g1.json`: `align` + `yield_sweep` |
| G1-2 | Pairing at derived offset, frozen window; δ-mass `{0,±1,±2..k}` linear+circular reported | `delta_profile_{linear,circular}` |
| G1-3 | CAL exactly 32 sacrificed frames, listed, excluded from denominator; split seed 20260920 same-split M0-vs-M2 NLL | `cal_frame_ids` (32), `split_seed`, `nll_M0/nll_M2` |
| G1-4 | H1/H2/H_total for M0+M2; STOP gate evaluated against preregistered |δ|≥2 bound (TO-FREEZE) | `H_*` table + gate verdict |

STOP: |δ|≥2 mass above bound ⇒ ±1 premise FAILS on this source — record, do NOT proceed to Stage 3. ALIGN_FAIL ⇒
exclude acquisition, continue; ALIGN_INCONSISTENT ⇒ STOP loudly. M0-vs-M2 NLL here is matched-CAL descriptive only
(M0's 1024-frame regime is not measured).

## §6 Stage 3 — G2 freeze + one-shot execution (Tier-Y; decoder on real data; the decisive test)

Requires: G1 passed, independent Pre-EXECUTE PASS, explicit user authorization pasted in full. Arms at MATCHED frozen
K1=319/K2=6492 with frozen P16 order: A (M0 prior) vs B (M2 prior). Preregistered block count TO-FREEZE (first N
consecutive 128-frame blocks after CAL; disjoint, listed). One-shot: no rerun, no tuning, no seed change.
Exact command:
`/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --stage-g2-decode --acq-id <ACQ> --arms A,B --blocks <N-FROZEN> --k1 319 --k2 6492 --tag-master <FROZEN> --out-root workspace/m2_prior_validation/<ACQ>/g2 --authorized`

| ID | Acceptance | Evidence |
|----|-----------|----------|
| G2-1 | Freeze (blocks/tag/window/skip/CAL IDs/budget) + Pre-EXECUTE PASS + pasted authorization all recorded BEFORE run | `g2_freeze.md` + review + auth ref |
| G2-2 | A-vs-B one-shot executed exactly once at frozen K/order, preregistered blocks, 64-bit Toeplitz tag per block | `per_block_outcomes.jsonl` (N rows/arm) |
| G2-3 | Per-block `exact`/`verify_failed`/`undetected`/`decode_failed`/`nonfinite` strictly separated (`undetected` NEVER merged); first-error coordinate+layer, disclosure bits, wall/RSS per block | outcome table + `disclosure_bits` + `wall_s`/`rss` |
| G2-4 | No rerun/tuning/seed change; target-output absence verified pre-run; inconclusive-by-rule ⇒ bounded negative, no tuning | run log + pre-run absence check |

## §7 Stage 4 — Pre-RESULT review + adjudication

| ID | Acceptance | Evidence |
|----|-----------|----------|
| R1 | Independent reviewer-go Pre-RESULT PASS (thresholds, leakage decomposition, `undetected` isolation, per-source breakdown, disclosure accounting vs artifacts) BEFORE any publication/commit of results | `PRE_RESULT_REVIEW.md` PASS |
| R2 | Main-thread adjudication recorded (adopt / revise-required / bounded negative); G3 + re-derivation explicitly deferred to own freezes | decision entry; no claim beyond packet scope |

## §8 Acceptance-ID list (operator reports IDs, not restatements)

I1, I2, I3, I4, G1-1, G1-2, G1-3, G1-4, G2-1, G2-2, G2-3, G2-4, R1, R2.

## §9 Budget (binding stop rule) + stop rules

Budget: Stage 2 decoder-free pairing+NLL ≈ ≤300 s wall / 2 GiB RSS per acquisition (single-threaded). Stage 3:
2 arms × 16 blocks × 2 SC calls × ~6 s ≈ 400 s + overhead ⇒ CAP 900 s wall / 2 GiB RSS single-threaded (S9 anchor:
680 s / 0.96 GB for 3 arms × 16 blocks). Exceeding CAP ⇒ STOP, record as blocker (no tuning to fit).
Stops: §5/§6 STOP lines; any §3 FORBIDDEN touch ⇒ STOP; G2 inconclusive-by-preregistered-rule ⇒ bounded negative,
no tuning; G3/re-derivation attempted in-packet ⇒ STOP (needs own freeze).

## §10 Return conditions (exactly two)

1. All-frozen-items-complete: per-ID PASS/FAIL with evidence paths + per-acquisition NLL/H table (Stage 2) /
   per-block outcome table (Stage 3) + run log path. 2. Concrete blocker: failing command + exact error/traceback
   (or adverse verdict + ID) + attempted remedies + the SINGLE decision needed. "Still incomplete" is not a report.
   Per-acquisition roots: `workspace/m2_prior_validation/<ACQ>/{g1.json,cal_ids.json,delta_profiles.json,run_log.md,
   g2/per_block_outcomes.jsonl}`. Nothing under `results/` or `comparison_bench/outputs_comparison/`.

## Tasks (coder-agent order)

1. Implement adapter + switch + oracle-matched tests (I1,I2). 2. Implement frozen-selector re-split path on synthetic
   fixtures (I3). 3. Write SECURITY_MODEL CAL note + inventory skeleton (I4). 4. Build runner with exact §5/§6 CLI.
   5. Freeze G1 (window/skip/bound) → execute §5 → evaluate STOP. 6. Freeze G2 → Pre-EXECUTE → one-shot §6.
   7. Pre-RESULT (R1) → adjudication (R2). T2–T7 only; G3/re-derivation need new freezes.
