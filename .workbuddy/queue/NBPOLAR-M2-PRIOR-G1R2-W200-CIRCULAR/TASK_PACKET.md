# TASK PACKET — NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR (delta-successor of G1; G1 scope: decoder-free NLL/pairing)

Per AGENTS.md §10.4 (delta-successor fast path) and §10.1 (one complete frozen packet before delegation). This packet authorizes NOTHING until verbatim user authorization flips `STATUS.yaml`.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/`
- Delta doc (authoritative for the change): `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1r2_delta.md`
- Predecessor (inherited verbatim except the **8 deltas** listed in the delta doc): `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1_freeze.md` + `TASK_PACKET.md` §5
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (TimeTagger 2.22.6 + Swabian shim per `docs/troubleshooting.md`)
- Nature: G1-scope — DESCRIPTIVE / NON-CLAIM and DECODER-FREE. M2 is a CANDIDATE, never the baseline.
- Route decision (user-confirmed 2026-09-21): narrow-window-centred validation, option 1; MOD = CIRCULAR.

## Goal

Re-run the G1 decoder-free premise/characterisation measurement on SHG `_1` under the corrected pairing+MOD contract (W_P=200, CIRCULAR), inheriting every other frozen value: closure → verification → one execution producing the reproduction gate, the δ-tail gate, CAL32 FIT triple, H1/H2/H_total for both models, the held-out NLL, and the remainder check — the inputs the later G2 freeze needs.

## Non-Goals

No decoder call of any kind; no G2 execution/freeze closure; no G3; no SHG `_2` read; no K decision; no construction re-derivation; no post-freeze change; no pooled-M1 CAL; no rerun/tuning after a gate verdict; no FER/efficiency/qualification/promotion claim.

## Impact Scope

WRITE: `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/` (closure + execution outputs); this packet's `STATUS.yaml` (counters/artifacts/ids only) + `g1r2_freeze_config.json`; and — per delta item **8** (REVISION 1) — a **scoped, separately reviewed re-parameterization of `scripts/m2_prior_validation.py`** (G1's w=500/4,256/66-reserve science constants and the G1 packet-dir/label hardcodes become window/ledger/packet driven). The runner's inherited mechanics (19-key set, `--authorized`, flag↔key cross-checks, K pin, out-root confinement, `--closure-only`, import purity) must NOT change, and G1's executed/adjudicated evidence + its code path stay intact (a `G1` legacy contract is retained and selected by the G1 window/ledger values, so re-running G1 reproduces its accepted numbers). FORBIDDEN (hard stop): any write under `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, `formal_ir/nbpolar/`; any SHG `_2` touch; any decoder; any out-of-scope write; checksums/atomic writes/locking/retry frameworks (AGENTS.md §5.7).

## The 19 TO-FREEZE values (delta summary; full basis in `g1r2_delta.md`)

CHANGED: `pairing_window_primary` 500 → **200**; `pairing_window_sensitivity` 200 → **500**; `mod_boundary` LINEAR_ONLY → **CIRCULAR**; `tag_master` 2026102201 → **2026103001** (= EVAL_SEED 2026093001 + 10000); ledger expectation 4,256 → **4,219** post-skip frames; RESERVE 66 → **29**.
UNCHANGED: `B_tail` 2.0e-4; `delta_min` 0.020; `g2_success_rule`/`g2_inconclusive_rule`/`g2_fail_rule` (Wilson, z=1.96); `skip_frames` 702; `cal_split_rule` RULE-FIT32-SCORE-HELDOUT; `g2_blocks` 14; `char_sample_pairs` 200,192; `g2_arms`; `block_formation_fallback`.
CLOSURE (re-emitted by Phase A, same ranges): `cal_frame_ids` = post-skip 1024–1055 (32); `heldout_frame_ids` = 1838–2397 (560); `a1_cal_ids` = 0–1023 (1024); `disjointness_matrix`.

**Reproduction-gate literals (w=200)**: n_pairs 1,259,992; pre-skip n_frames 4,921; accidental 0.0058; linear {0: 950276, +1: 306566, −1: 2849, tail: 301 (= −1023:293 + +1023:8)}; circular {0: 950276, +1: 306859, −1: 2857, **tail: 0**}; alignment peak 50 / σ 112.45189572400645 / status ok.

**Segment layout** (identical ranges to G1): A1-CAL 0–1023 | CAL32 1024–1055 | CHAR 1056–1837 | HELDOUT 1838–2397 | EVAL 2398–4189 | RESERVE 4190–4218 (29). Fallback: COMPLETE-BLOCKS-ONLY else INSUFFICIENT ⇒ INCONCLUSIVE; never pad/reuse/shrink.

**Gates** (§6 of the inherited freeze, MOD-switched): δ-tail statistic p̂ = count(|δ_circ| ≥ 2)/n on CHAR (200,192 pairs) — one-sided 95% upper U = rule-of-three 3/n if zero obs else Clopper-Pearson; PASS iff U < 2.0e-4; FAIL iff p̂ > 2.0e-4; INCONCLUSIVE iff p̂ ≤ B_tail ≤ U. NLL: Δ = mean per-symbol (NLL_M0 − NLL_M2) on HELDOUT (143,360 symbols), PASS iff Δ > 0.020; FAIL iff Δ ≤ 0; INCONCLUSIVE iff 0 < Δ ≤ 0.020. δ-tail FAIL ⇒ record, do NOT proceed toward G2.

**Expected-in-advance note** (not a result): S11 measured the FULL-STREAM w=200 CIRCULAR tail = 0 and CHAR is a subset, so p̂ = 0 and U = 1.4986e-5 are forced by inclusion. The new information from this packet is the CAL32 triple, the H values and the held-out NLL under this contract.

## Phases

**Phase A — closure (SHG `_1`, decoder-free; no prior fitting, no NLL)**: reproduce the census alignment + (N) w=200 pairing (5 literals above; mismatch ⇒ STOP loudly, ALIGN_INCONSISTENT); apply skip-702; enumerate the post-skip ledger (expect 4,219; verify ≥ 4,190); apply the layout; emit the four closure keys + the complete 19-key `g1r2_freeze_config.json`. Budget ≤ 300 s / 2 GiB.

**Verification gate (main thread)**: independent verification of the closure + delta consistency before any execution.

**Phase B — execution (decoder-free)**: re-verify the reproduction gate vs the Phase-A ledger; run G1R2-1..G1R2-4 (alignment record; pairing at W_P=200 with W_S=500 sensitivity readout, no switching; δ-profile linear AND circular on CHAR; CAL32 FIT + held-out NLL matched-CAL; H1/H2/H_total both models; both gates with full U/Δ arithmetic); remainder-population NLL/H check (frozen derived pairs, sibling venv, no gate). Budget ≤ 600 s / 2 GiB per invocation, single-threaded.

## Acceptance IDs → evidence

`G1R2-A` closure (reproduction 5/5 exact + ledger 4,219 ≥ 4,190 + five lists + disjointness + 19-key config) · `G1R2-1` alignment · `G1R2-2` pairing + δ-profile (linear+circular) · `G1R2-3` CAL32 FIT + held-out NLL · `G1R2-4` H tables + both gate verdicts with U/Δ arithmetic · `G1R2-R` remainder check (pooled + per-segment). Evidence root `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/{g1.json,cal_ids.json,delta_profiles.json,run_log.md}` (+ `*_closure.*` preserved) and `workspace/m2_prior_validation/remainder_101f_g1r2/`.

## Exact commands

```
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
cat .git/HEAD  # expect: ref: refs/heads/codex/nbpolar-phase0
# Phase A (closure):
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --freeze-config .workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/g1r2_freeze_config.json --stage-g1-nll --acq-id 20260113_SHG_Type2PPLN_3s --window-primary 200 --window-sensitivity 500 --skip 702 --mod CIRCULAR --char-pairs 200192 --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2 --authorized --closure-only
# Phase B (execution; same command WITHOUT --closure-only). Remainder:
# /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python <same> --acq-id remainder_101f --out-root workspace/m2_prior_validation/remainder_101f_g1r2
```

## Stop rules + budget

Any FORBIDDEN touch (SHG `_2`, decoder, out-of-scope write, runner modification) ⇒ STOP + blocker. Reproduction mismatch ⇒ STOP loudly. Budget exceeded ⇒ STOP (no tuning). Post-verdict rerun/tuning ⇒ STOP. Ambiguity ⇒ STOP (second return condition), never guess.

## Return (exactly two)

1. All-complete: per-ID PASS with evidence paths + gate arithmetic + run logs + scoped `git status` (Phase A returns with Phase B explicitly not run; Phase B dispatched later after the verification gate).
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision needed. "Still incomplete" is not a report.

## Frozen resolutions (report, do not smooth)

R1: same-point semantic correction under §10.4 — do not describe as a new hypothesis or a new route.
R2: the δ-tail PASS is arithmetically forced by S11's full-stream measurement; the packet's value is the triple/H/NLL, and results must not be reported as "the premise was validated" beyond what the CHAR subset shows.
R3: G1's bounded negative stands under its own contract; never write that it was wrong.
R4: tag_master 2026103001 is fresh per the grep of all existing packet tag masters.
R5: **REVISION 1 (2026-09-21)** — the first delta's "runner must NOT be modified" premise was disproven by the independent delta review (DELTA_FAIL, blocking G): four hardcodes make this packet unexecutable at w=200 (see delta item 8). Corrected stance: a **scoped runner re-parameterization is part of this packet's authorized work** (delta item 8), implemented as its own reviewed code step with G1's accepted record and code path intact; the runner's inherited **mechanics** (19-key enforcement, `--authorized`, cross-checks, K pin, confinement, `--closure-only`, import purity) still must NOT be weakened. If anything beyond item 8's four sites proves necessary, STOP and report.
