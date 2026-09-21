# OPERATOR PROMPT — NBPOLAR-M2-PRIOR-REALDATA-VALIDATION (copy-paste, self-contained)

You are the operator executing a frozen M2-prior validation packet. Do NOT redesign. Do NOT guess.
If the packet is ambiguous, STOP and report (second return condition).

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD` shows `ref: refs/heads/codex/nbpolar-phase0`. Else STOP.
- Python: `/home/karel_303/.venvs/timetagger/bin/python` for EVERYTHING (TimeTagger shim required for Stages 2–3).
- Packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md` (overrides this prompt on conflict).
- Output roots (additive only): `workspace/m2_prior_validation/<ACQ>/`. NEVER `results/` or
  `comparison_bench/outputs_comparison/`. NEVER modify `src/`, `experiments/`, `tools/`, `sc.py`.
- S9 is synthetic-only: NEVER cite it as FER evidence. NEVER pool M1 with a delay-−50 source in CAL.

## 1. Stage 1 — Implementation (NO protected reads; injected arrays + temp roots only)

Build: new adapter module (NOT a `sc.py` edit) with M0-reproducing switch; frozen-`select_empirical_split`
re-split path (synthetic fixtures; real-data numbers diagnostic-only); `SECURITY_MODEL.md` CAL note + inventory
skeleton; runner `scripts/m2_prior_validation.py` exposing the exact §5/§6 CLIs.
Report I1–I4 with: oracle-diff report, pytest log, `git status`/`git diff` snippet proving `sc.py`/algebra/
transform untouched, replay log, doc diff. No `.ttbin` open in Stage 1 (grep-verifiable).

## 2. Stage 2 — G1 (decoder-free real data; needs G1-freeze values + execution authorization)

Per acquisition (`20260113_SHG_Type2PPLN_3s` first; `_2` after `_1` G1 passes):
PRIMARY `.ttbin` ONLY (never concatenate `.1`) → ONE frozen-params alignment call
(scan_range 409600, bin 100, `status==ok` AND `peak_to_bg>=10`, yield-sweep self-check; NEVER inherit −50) →
pair at derived offset under the FROZEN (N) window → δ-mass `{0,±1,±2..k}` linear+circular →
skip (FROZEN) → CAL 32 sacrificed → split-A fit / split-B score (seed 20260920, same split M0 vs M2).

```bash
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py \
  --stage-g1-nll --acq-id 20260113_SHG_Type2PPLN_3s \
  --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s --authorized
```

Report G1-1–G1-4 from `g1.json` + run log. STOP rules: |δ|≥2 mass above the preregistered bound ⇒ premise FAILS,
do NOT proceed to Stage 3. ALIGN_FAIL ⇒ exclude, continue. ALIGN_INCONSISTENT ⇒ STOP loudly.

## 3. Stage 3 — G2 (Tier-Y one-shot; needs G2-freeze + Pre-EXECUTE PASS + pasted authorization)

Arms A (M0+frozen P16) vs B (M2+frozen P16), matched K1=319/K2=6492, preregistered blocks, 64-bit tag/block.
Verify target-output absence BEFORE running. Run EXACTLY ONCE — no rerun, no tuning, no seed change.

```bash
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py \
  --stage-g2-decode --acq-id 20260113_SHG_Type2PPLN_3s --arms A,B --blocks <N-FROZEN> \
  --k1 319 --k2 6492 --tag-master <FROZEN> \
  --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/g2 --authorized
```

Report G2-1–G2-4: per-block `exact`/`verify_failed`/`undetected`/`decode_failed`/`nonfinite` (never merge
`undetected`), first-error coordinate+layer, disclosure bits, wall/RSS. Inconclusive-by-rule ⇒ bounded negative.

## 4. Stage 4 — review gate

Do NOT publish results before independent reviewer-go Pre-RESULT PASS (R1). Await main-thread adjudication (R2).
Budget CAP (binding): Stage 2 ≤300 s / 2 GiB per acq; Stage 3 ≤900 s / 2 GiB single-threaded. Exceed ⇒ STOP.
Return: (1) all-complete with per-ID evidence + tables + run log; or (2) concrete blocker with failing command,
exact error, remedies, and the SINGLE decision needed.
