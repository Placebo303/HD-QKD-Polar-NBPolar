# TASK PACKET — NBPOLAR-M2-PRIOR-G1-REALDATA-NLL (G1 freeze closure + decoder-free execution)

Per AGENTS.md §10.1: one complete frozen packet before delegation. This packet authorizes NOTHING until verbatim user authorization flips `STATUS.yaml`.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/`
- Parent packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/` (implements its §5 only; §§6–8 G2/Pre-RESULT OUT)
- Freeze: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1_freeze.md` (`G1_FREEZE_PREPARED_PENDING_REVIEW`) — authoritative for all 19 TO-FREEZE values and gate rules. TASK_PACKET conflicts with the freeze ⇒ STOP and report.
- Change: `openspec/changes/nbpolar-prior-rebaseline/` (T5 at G1 scope; T6/T7/T8 OUT)
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (TimeTagger 2.22.6 + Swabian shim per `docs/troubleshooting.md`) for EVERYTHING in this packet. Never the Stage-1 sibling venv here (no TimeTagger).
- Nature: G1 is DESCRIPTIVE / NON-CLAIM and DECODER-FREE. M2 is a CANDIDATE, never the baseline. No FER/efficiency/qualification claim follows under any outcome.

## Goal

Execute the frozen G1: Phase-A closure (frame ledger + segment lists + freeze-config on SHG `_1`), then — ONLY after the independent freeze review PASSes — Phase-B G1 execution (δ-tail gate + matched-CAL held-out NLL M0-vs-M2 + H tables on SHG `_1`; NLL/H-only check on the frozen-session remainder), with both preregistered gates evaluated and all evidence under `workspace/m2_prior_validation/`.

## Non-Goals

No decoder call of any kind (`sc_decode`/genie/SCL); no G2 execution or G2 freeze closure beyond the values already in `g1_freeze.md`; no G3; no SHG `_2` read; no construction re-derivation; no K decision; no prior/decoder/science change; no FER/efficiency/promotion claim; no S9 citation as evidence; no post-freeze threshold/seed/K/window change.

## Impact Scope

WRITE (additive): runner `scripts/m2_prior_validation.py` (G1 body implementation — the ONLY code file); `workspace/m2_prior_validation/<acq>/…` outputs; parent packet `STATUS.yaml` (Phase-A closure values only, by the operator at Phase-A return; `next_gate`/gate flags are MAIN-THREAD — do not touch); this packet's `STATUS.yaml` (counters/artifacts only); freeze-config JSON under this packet dir. READ: parent `TASK_PACKET.md`, `g1_freeze.md`, parent `STATUS.yaml`, `formal_ir/nbpolar/{prior,sc,transform,algebra,empirical_genie_scaling}.py`, `formal_ir/prior_m2.py` (Stage-1 surface), `src/qkd_io` (FileReader usage conventions only), `workspace/census_20260921/**` (read-only census artifacts), `docs/nbpolar/{STATE,MACRO_PLAN_20260921,REAL_DATA_FEASIBILITY_STRATEGY}.md`, `docs/troubleshooting.md` (TimeTagger traps). FORBIDDEN (hard stop): modify anything under `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, or `formal_ir/nbpolar/`; any SHG `_2` touch; any decoder; any write outside `workspace/` + this packet dir + the runner file; checksums/atomic writes/locking/retry frameworks (AGENTS.md §5.7).

## Phase 0 — G1 body implementation (decoder-free, synthetic fixtures + fake runner ONLY; no data contact)

Implement the `--stage-g1-nll` body of `scripts/m2_prior_validation.py` (currently exit-3 `STAGE_BODY_PENDING_FREEZE`). PRESERVE every Stage-1 guard verbatim: `--authorized` store_true gate (exit 2 before any read/create), `--freeze-config` all-19-keys enforcement (null/absent ⇒ exit 2 listing keys, never a default), flag↔key cross-checks, `--out-root` workspace confinement, import purity (repo-root sys.path insert BEFORE the Swabian `sys.modules["TimeTagger"]` shim BEFORE any `src.qkd_io` import; no argparse/file/decoder work at import; `main(argv=None)` + `__main__` guard).

Body requirements:
1. Pairing: (N) narrow nearest-unique, vendored literally from the 2026-09-21 census implementation (`workspace/dual_rule_census_20260921.py` — frozen constants d=1024, bin 200 ps, period 204800 ps, frame_pairs=256, gate 200 ps, threshold 40000 ps; symbol map `(b_A % 1024, b_B % 1024)`, `b = t // 200`, `tA_aligned = tA_raw + offset`). Never the (W) legacy rule for G1 science.
2. Alignment: ONE frozen-params call per acquisition (scan_range 409600, bin 100, accept `status==ok AND peak_to_bg>=10` + yield-sweep self-check); record `peak_center/sigma/to_bg`; NEVER inherit −50/+50/+50; remainder population reuses frozen derived pairs (no new alignment).
3. Framing: apply `skip_frames` (702) to the paired stream; chunk into 256-pair frames; drop the trailing incomplete frame.
4. G1 science (decoder-free): δ-mass profile `{0,±1,±2..k}` linear AND circular under frozen MOD on the CHAR segment; CAL32 counts → M2 triple via `formal_ir/prior_m2.py` (`fit_m2_triple` → `build_m2_joint`) and M0 table via `build_m0_joint` (matched-CAL); H1/H2/H_total for both models via the UNCHANGED frozen `derive_p1`/`derive_p2` + `build_p1_metrics`/`gather_p2_metrics` + `probs_to_symbol_metric(provenance=PRIOR_ONLY)` conventions (imported from `nbpolar.prior`, never modified); held-out per-symbol NLL for both models on HELDOUT under RULE-FIT32-SCORE-HELDOUT (fit on ALL 32 CAL frames; score on the disjoint held-out segment; seed N/A).
5. Gate evaluation: both gates exactly per `g1_freeze.md` §6 (δtail: p̂, rule-of-three/Clopper-Pearson upper U, PASS/FAIL/INCONCLUSIVE vs B_tail; NLL: Δ vs Δ_min).
6. Remainder population: NLL/H-only check (32 CAL + 69 held-out from the 101-frame remainder; frozen derived pairs; NO alignment, NO char sample — exempt per freeze §1.2).
7. Outputs (additive, under `workspace/m2_prior_validation/<acq>/`): `g1.json` (alignment + pairing + gates), `cal_ids.json` (Phase-A lists), `delta_profiles.json`, `run_log.md`. Remainder outputs under `workspace/m2_prior_validation/remainder_101f/`.
8. Focused tests (synthetic + fake runner ONLY; per AGENTS.md §10.1 item 8 test-only calls must pass an explicit fake runner — NEVER invoke the production path from tests): extend `comparison_bench/tests/test_nbpolar_prior_m2.py` OR add `comparison_bench/tests/test_nbpolar_m2_g1_body.py` covering: freeze-config key enforcement still green; MOD handling in δ-profile; frame chunking + skip arithmetic on synthetic streams; NLL/gate arithmetic on synthetic M0/M2 fixtures (hand-computed); remainder exemption path; import purity; exit codes 0/2/3 unchanged where applicable.

## Phase A — freeze closure (SHG `_1`, ONE framing pass; decoder-free; no prior fitting, no NLL)

Run the closure: reproduce census alignment + (N)-w=500 pairing (reproduction gate: `peak_center 50` / `σ 112.45189572400645` / `status ok` / `n_pairs 1,269,268` / `n_frames 4,958` pre-skip — any mismatch ⇒ STOP loudly, ALIGN_INCONSISTENT); apply skip-702; enumerate the post-skip ledger (expect 4,256 complete frames; verify 4,256 ≥ 4,190 allocated); apply the `g1_freeze.md` §4 layout; emit `cal_frame_ids` (frames 1024–1055), `heldout_frame_ids` (1838–2397), `a1_cal_ids` (0–1023), `disjointness_matrix`, and the complete freeze-config JSON (all 19 keys, closure keys filled) at `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/g1_freeze_config.json`. Record the census-reproduction evidence in the closure output. Budget ≤ 300 s wall / 2 GiB RSS.

**PHASE A ENDS THE OPERATOR'S FIRST RETURN.** After Phase A (+ Phase 0 code), return per §Return. Phase B runs ONLY after the main thread records an independent freeze review PASS (review covers `g1_freeze.md` + the filled freeze-config + the Phase-0 code). A review FAIL blocks Phase B.

## Phase B — G1 execution (only after freeze-review PASS; decoder-free)

Re-verify the reproduction gate against the Phase-A ledger (bit-exact; mismatch ⇒ STOP); execute G1-1..G1-4 on SHG `_1` (alignment record; pairing at W_P=500 with W_S=200 sensitivity readout, NO switching; δ-profile linear+circular; CAL32 FIT + held-out NLL; H tables both models; both gate verdicts with full U/Δ arithmetic); remainder-population NLL/H check. Budget ≤ 600 s wall / 2 GiB RSS per acquisition, single-threaded (parent §9). Exceeding ⇒ STOP, record blocker (no tuning to fit).

## Exact commands

```
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
cat .git/HEAD  # expect: ref: refs/heads/codex/nbpolar-phase0
# Phase 0 (synthetic, no data):
/home/karel_303/.venvs/timetagger/bin/python -m pytest comparison_bench/tests/test_nbpolar_prior_m2.py comparison_bench/tests/test_nbpolar_m2_g1_body.py -p no:cacheprovider -q
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --selfcheck
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --help
# Phase A (closure; --authorized required):
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py --freeze-config .workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/g1_freeze_config.json --stage-g1-nll --acq-id 20260113_SHG_Type2PPLN_3s --window-primary 500 --window-sensitivity 200 --skip 702 --mod LINEAR_ONLY --char-pairs 200192 --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s --authorized --closure-only
# Phase B (execution; same command WITHOUT --closure-only; remainder: --acq-id remainder_101f)
```

NOTE: the `--closure-only` switch is a NEW Phase-A-only flag the operator must add in Phase 0 (store_true; absent ⇒ normal G1 body; it restricts the body to closure outputs + zero NLL/gate science). It does not weaken any Stage-1 guard. If `--closure-only` conflicts with the frozen CLI CONTRACT in any way, STOP and report rather than improvising.

## Acceptance IDs → evidence

- `G1-A` (Phase A): census-reproduction evidence (5 values exact) + post-skip ledger count + five segment lists + disjointness matrix + filled freeze-config JSON.
- `G1-1`: per-acq alignment record (peak_center/sigma/to_bg; no inherited offsets; remainder reuses frozen pairs).
- `G1-2`: pairing at derived offset under frozen W_P (+W_S sensitivity, no switching), frozen MOD; δ-profile linear+circular.
- `G1-3`: CAL exactly 32 sacrificed frames listed + excluded from denominator; FIT32-SCORE-HELDOUT disjoint; same-CAL M0-vs-M2 NLL.
- `G1-4`: H1/H2/H_total both models + both gate verdicts with U/Δ arithmetic.
- `G1-0` (Phase 0): focused suite green + selfcheck green + `git diff --stat` on `formal_ir/nbpolar/` empty + no-import scan clean.

## Stop rules + budget

Any FORBIDDEN touch (incl. any SHG `_2` read, any decoder call, any write outside scope) ⇒ STOP + blocker. Reproduction-gate mismatch ⇒ STOP loudly. Budget exceeded ⇒ STOP (no tuning). Ambiguity (incl. any freeze/packet conflict) ⇒ STOP (second return condition), never guess. Phase B before freeze-review PASS ⇒ STOP.

## Return (exactly two)

1. Phase-0+Phase-A complete: per-ID `G1-0`, `G1-A` PASS with evidence paths + pytest log + closure outputs + `git status` snippet; Phase B explicitly NOT run (awaiting review).
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision needed. "Still incomplete" is not a report.
(After the main thread records the freeze-review PASS and re-dispatches with the same sessionID: Phase-B return with per-ID `G1-1..G1-4` PASS/FAIL/INCONCLUSIVE + gate arithmetic + evidence paths.)

## Frozen resolutions (report, do not smooth)

R1: G1 is descriptive/non-claim even on PASS — it never promotes M2; only G2/G3 can move scientific status.
R2: the freeze-adopted (N)-w=500 pairing contract is the PI pairing-rule decision for THIS packet (surfaced in `g1_freeze.md` §5 #6); authorizing this packet confirms it. W_S=200 is sensitivity-only.
R3: g2_blocks=14 is a recorded deviation from the recommended 16 (freeze §3 arithmetic); do not "restore" 16 without a new freeze.
R4: skip-702 applies to the (N) stream even though the census (N) counts were pre-skip (freeze §2–§3); the reproduction gate compares PRE-skip census values, the ledger is POST-skip.
R5: the remainder population contributes an NLL/H comparison check only; its 25,856 pairs can never supply the ≥200k char gate (exempt, recorded, never padded).
