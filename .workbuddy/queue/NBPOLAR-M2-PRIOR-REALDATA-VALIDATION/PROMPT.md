# OPERATOR PROMPT — NBPOLAR-M2-PRIOR-REALDATA-VALIDATION (copy-paste, self-contained)

You are the operator executing a frozen M2-CANDIDATE validation packet. Do NOT redesign. Do NOT guess.
If the packet is ambiguous, STOP and report (second return condition). M2 is a CANDIDATE, never the baseline.

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD` shows `ref: refs/heads/codex/nbpolar-phase0`. Else STOP.
- Python: `/home/karel_303/.venvs/timetagger/bin/python` for EVERYTHING (TimeTagger shim required for Stages 2–3).
- Packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md` (overrides this prompt on conflict).
- Output roots (additive only): `workspace/m2_prior_validation/<ACQ>/`. NEVER `results/` or
  `comparison_bench/outputs_comparison/`. NEVER modify `src/`, `experiments/`, `tools/`, `sc.py`.
- S9 is synthetic-only: NEVER cite it as FER evidence. NEVER pool M1 with a delay-−50 source in CAL.
- SHG `_2` (`20260113_SHG_Type2PPLN_3s_2`) is FROZEN from this packet onward. **PARTICIPATION DISCLOSURE: it is NOT untouched** — the 2026-09-21 dual-rule census already ran decoder-free alignment (σ=114.4 ps), a full pairing grid and (N)-200 H_total=0.816770 on it (`docs/decision-log.md:5220`), and its cells informed the W_P=500 recommendation. NEVER done on it: prior fitting, any decoder run, or M2 model selection. Any further read ⇒ STOP.
- Frozen remainder is 101 frames (41+42+18), not 261. After 32-frame CAL only 69 remain (<1 block, NLL-level only).

## 1. Stage 1 — Implementation (NO protected reads; injected arrays + temp roots only)

Build: NEW strict 3-parameter M2 adapter (triple → model-implied 1024×1024 → 1e-15 floor + renorm; S8's all-1024-δ
fit SHALL NOT be reused) with explicit frozen MOD param (recommended LINEAR_ONLY) + M0-reproducing switch;
frozen-`select_empirical_split` re-split path (synthetic fixtures; real-data numbers diagnostic-only, no K decision);
`SECURITY_MODEL.md` CAL note (32-frame CANDIDATE budget, reveal diagnostic, no λ_prior, M2 CANDIDATE label) +
inventory skeleton; runner `scripts/m2_prior_validation.py` exposing the exact §5/§6 CLIs with all TO-FREEZE flags.
Report I1–I4 with: oracle-diff + MOD tests, pytest log, `git status`/`git diff` proving `sc.py`/algebra/transform
untouched, replay log, doc diff. No `.ttbin` open in Stage 1 (grep-verifiable).

## 2. Stage 2 — G1 (decoder-free real data; needs G1-freeze values + execution authorization)

Two populations, in order: (a) frozen 101-frame remainder — NLL/H level only, NO decode, frozen derived pairs, no new
alignment (δ-mass already verified there); (b) SHG `_1` (`20260113_SHG_Type2PPLN_3s`) — PRIMARY `.ttbin` ONLY (never
concatenate `.1`) → ONE frozen-params alignment call (scan_range 409600, bin 100, `status==ok` AND `peak_to_bg>=10`,
yield-sweep self-check; NEVER inherit −50) → pair at derived offset under FROZEN primary window + sensitivity window
(no post-hoc switching; census-informed = DATA-INFORMED) → δ-mass `{0,±1,±2..k}` linear+circular under frozen MOD →
frozen skip → CAL 32 sacrificed → RULE-FIT32-SCORE-HELDOUT (fit ALL 32, score disjoint temporally-separated held-out;
same CAL for M0 vs M2). Gates per §5: δtail PASS iff 95% upper U < B_tail (rec. 2.0e-4) on the LARGE char sample
(≥200k pairs; 32-frame CAL alone can NEVER pass — zero obs at 8192 leaves 3.662e-4); NLL PASS iff Δ > Δ_min
(rec. 0.020 bits/symbol; matched-CAL descriptive only — incumbent is G2 arm A1, not this NLL).

```bash
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py \
  --stage-g1-nll --acq-id 20260113_SHG_Type2PPLN_3s \
  --window-primary <W_P-FROZEN> --window-sensitivity <W_S-FROZEN> --skip <SKIP-FROZEN> --mod <MOD-FROZEN> \
  --char-pairs <NCHAR-FROZEN> --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s --authorized
```

Report G1-1–G1-4 from `g1.json` + run log with U/Δ arithmetic. STOP: δtail FAIL ⇒ premise FAILS, no Stage 3.
INCONCLUSIVE on either gate ⇒ bounded negative, no proceed. ALIGN_FAIL ⇒ exclude, continue. ALIGN_INCONSISTENT ⇒ STOP.

## 3. Stage 3 — G2 (Tier-Y one-shot on SHG `_1` only; needs G2-freeze + Pre-EXECUTE PASS + pasted authorization)

Three arms at matched frozen K1=319/K2=6492 + frozen P16 order on the SAME preregistered blocks: A1 = M0 at OWN
1024-frame CAL (incumbent as-deployed reference, no gate); A2 = M0 at matched 32-frame CAL (prior-form control);
B = M2 CANDIDATE at 32 frames. 64-bit tag/block from frozen TAG_MASTER. Verify target-output absence BEFORE running.
Run EXACTLY ONCE — no rerun, no tuning, no seed change. Full §6 semantics per block: `l1_exact`/`hard_l2_exact`/
`oracle_l2_exact`/`pair_exact`, first-error coordinate+layer, raw TRAIN zero-count hits, fixed-floor hits + log loss,
true-H- and candidate-H-conditioned L2 NLL, taxonomy `exact`/`verify_failed`/`undetected`/`decode_failed`/`nonfinite`/
`resource_abort` (`undetected` never merged). Outcome gate (preregistered BEFORE run): SUCCESS iff Wilson-lower(B) >
Wilson-upper(A2) (z=1.96, strict non-overlap); FAIL iff point(B) ≤ point(A2); INCONCLUSIVE iff point(B) > point(A2)
but CIs overlap ⇒ bounded negative.

```bash
/home/karel_303/.venvs/timetagger/bin/python scripts/m2_prior_validation.py \
  --stage-g2-decode --acq-id 20260113_SHG_Type2PPLN_3s --arms A1,A2,B --blocks <N-FROZEN> \
  --k1 319 --k2 6492 --tag-master <FROZEN> --window-primary <W_P-FROZEN> --mod <MOD-FROZEN> \
  --out-root workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/g2 --authorized
```

Report G2-1–G2-4 with CI arithmetic. Budget CAP (binding): Stage 2 ≤600 s / 2 GiB per acq; Stage 3 ≤900 s / 2 GiB
single-threaded (3×16×2×~6 s ≈ 576 s + overhead). Exceed ⇒ STOP.

## 4. Stage 4 — review gate

Do NOT publish results before independent reviewer-go Pre-RESULT PASS (R1). Await main-thread adjudication (R2).
G3 (SHG `_2`), K re-split, and construction re-derivation need their own freezes — explicitly OUT.
Return: (1) all-complete with per-ID PASS/FAIL/INCONCLUSIVE + evidence + tables + run log; or (2) concrete blocker
with failing command, exact error, remedies, and the SINGLE decision needed.
