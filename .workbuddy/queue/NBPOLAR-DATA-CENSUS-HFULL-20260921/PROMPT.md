# OPERATOR PROMPT — NBPOLAR-DATA-CENSUS-HFULL-20260921 (copy-paste, self-contained)

You are the operator executing a frozen zero-decoder census packet.
Do NOT redesign. Do NOT guess. If the packet is ambiguous, STOP and report.

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify with `git rev-parse --abbrev-ref HEAD`.
  If it shows anything else, STOP and report. Do NOT switch branches.
- Python: this checkout has NO `.venv`. Use the timetagger venv for EVERYTHING:
  `/home/karel_303/.venvs/timetagger/bin/python`
  (TimeTagger 2.22.6 + numpy 2.5.3 verified 2026-09-21).
- Packet: `.workbuddy/queue/NBPOLAR-DATA-CENSUS-HFULL-20260921/TASK_PACKET.md`
  (full contract — read it first; it overrides this prompt on any conflict).
- Intake script: `scripts/census_intake_20260921.py` (skeleton, prepared).
- Raw paths: read EXACT `path_posix` values from
  `workspace/data_intake_20260921/inventory.json`. Do not reconstruct paths.
- Output root (additive only): `workspace/census_20260921/<acq_id>/`.
  NEVER write into `results/` or `comparison_bench/outputs_comparison/`.
  NEVER modify `src/`, `experiments/`, `tools/`.
  NEVER run `experiments/run_e2e_pipeline.py`, `tools/longrun_*`,
  `tools/minrerun_*`, `routeA_*`, or any decoder.

## 1. Frozen parameters (do not tune)

`d=1024`, `bin_width_ps=200`, `period_ps=204800`, `pairing=nearest`,
`rule=legacy_v1`, `frame_pairs=256`, `gate_ps=200`, `threshold_ps=40000`.
Channels FIXED: logical A = hardware 1, B = hardware 5 (NOT searched).
Delay (R1 REWRITE 2026-09-21 — SUPERSEDES the old `|delay−peak|<50ps`,
`sigma∈[50,150]` gate, which was calibrated for the 01-21 V25 sources and is
inapplicable to new sources): ONE estimator invocation per acquisition with
frozen scan params (`scan_range_ps=409600`, `bin_ps=100` — TASK_PACKET.md
§1.2); acceptance is unit-independent — `status=="ok"` AND `peak_to_bg>=10`.
FAIL ⇒ record `ALIGN_FAIL`, exclude that acquisition, continue — NO tuning, NO
sigma widening, NO second scan range. Yield-vs-offset self-check: derived
offset at/within one coarse step of the yield maximum (a strict-exact miss by
a plateau margin is PASS-with-note, never tuned); beyond one step ⇒
`ALIGN_INCONSISTENT` (record, STOP loudly). Do NOT inherit the frozen
−50/+50/+50 delays (01-21 V25 sources only). Dual-rule census: pair under (W)
wide legacy_v1 always + (N) nearest-unique grid {200,500,1000,2000,4000,40000};
report σ vs frozen [50,150] per acquisition without relaxing the gate.
Skip: default **702 frames for ALL acquisitions, labelled
`INHERITED_NOT_DERIVED`** (known weakness — stated plainly, census is
descriptive/non-claim because of it) + mandatory NON-DECISION companion
diagnostic per acquisition (per-frame coincidence counts over the first ~1500
frames; recorded, does not change the run). Do NOT invent per-acquisition
skips mid-run.
Length tiers (B0: after pairing, before any H work; thresholds in full frames):
TIER_FULL ≥ 1982 frames → frozen sizing (skip 702, CAL 1024, VAL 256);
TIER_REDUCED 1342–1981 frames → reduced sizing (skip 702, CAL 512, VAL 128,
labelled `REDUCED_SIZING`, NOT directly comparable); TIER_INSUFFICIENT < 1342
frames → record `INSUFFICIENT_LENGTH`, no H. No frame reuse, no padding, no
partial-frame inclusion (trailing <256 remainder excluded, recorded).
Channel 1001 (sync/marker) excluded by construction — pairing masks select only
ch 1/5; all else lands in `other` against the 0.20 guard.
PI RULING 2026-09-21: Type0 and SHG are only SOURCE differences, NO effect on IR —
ALL 10 acquisitions are in scope. Ignore any `TYPE0_SOURCE_UNVERIFIED` exclusion
language in the inventory doc/JSON.

H estimators: PRIMARY = factorized chain H1+H2 with raw-count MLE + 1e-15 floor
(λ program refuted — raw+floor only). SECONDARY = flat full-joint H_full
(v70 hierarchical, λ by 30-pt 4-fold CV) in a SEPARATE field, never the same
comparison column as the primary chain.

## 2. Stage A0 — environment enablement (FIRST, before anything else)

**A0-3 modifies an environment OUTSIDE the repo (pip install into the sibling
venv) and needs its OWN authorization (AUTHORIZATION_PROMPT.md item B).
Do NOT run the A0-3 install on Stage A/B authorization alone.**

```bash
# A0-1: glibc must be >= 2.28 (STOP and report if not)
ldd --version | head -1
# A0-2: numpy in the TARGET (sibling) venv
/home/karel_303/.venvs/timetagger/bin/python -c "import numpy; print(numpy.__version__)"
# A0-3 (ONLY with separate item-B install authorization):
/home/karel_303/.venvs/timetagger/bin/python -m pip install Swabian-TimeTagger
# A0-4/A0-5 (after A0-3):
/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py \
  --stage-a0-env-check --out-root workspace/census_20260921
```

Record A0-1–A0-5 per TASK_PACKET.md §4 (evidence:
`workspace/census_20260921/stage_a0_env.json` + run log lines).
Namespace-mismatch note: repo code needs `from TimeTagger import FileReader`;
if the bare import fails, the intake script already carries the preferred
`Swabian`-import shim at its top — record `filereader_import_path` from the
check output. If the shim path still fails, the fallback is pinning
`Swabian-TimeTagger==2.20.2` or `==2.21.2`; the Windows-export route needs a PI
decision and must not be started unilaterally.
**Any adverse A0 result ⇒ STOP. Do NOT proceed to Stage A.**

## 3. Stage A — parse-test gate (ONE acquisition, only after Stage A0 passes)

Target: `20260112_Type2PPLN_3s` (smallest Type-II). Confirm the two file paths
against inventory.json, then run:

```bash
/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py \
  --stage-a-parse-test --acq-id 20260112_Type2PPLN_3s \
  --out-root workspace/census_20260921
```

Record A1–A5 per TASK_PACKET.md §5 from
`workspace/census_20260921/20260112_Type2PPLN_3s/stage_a_parse.json`.
**If `stage_b_go` is false for ANY reason (primary-alone drops data, union≠sum,
channel ids differ, TimeTagger missing) ⇒ STOP. Do NOT proceed to Stage B.**
Return per §5 below (blocker condition).

**STAGE A RESULT 2026-09-21 (SUPERSEDES the "UNVERIFIED" line below):
auto-follow CONFIRMED on `20260112_Type2PPLN_3s` — either file yields the
identical full acquisition (3,836,088 / 3,836,088 events; concat = 7,672,176 =
exact 2× duplication). ⇒ BINDING MERGE RULE: read the PRIMARY `<stem>.ttbin`
ONLY; never concatenate. The frozen `stage_a_parse.json`
`union-is-concat-use-both-files` verdict is SUPERSEDED (concat Stage B was
NO-GO); the script now implements primary-only read.**

**Reminder: the hypothesis that `FileReader` auto-follows `.1` segments is
UNVERIFIED — Stage A tests it empirically. Do not assume it.**

## 4. Stage B — census (ONLY if Stage A passed with `stage_b_go: true`)

```bash
/home/karel_303/.venvs/timetagger/bin/python scripts/census_intake_20260921.py \
  --stage-b-census --authorized --out-root workspace/census_20260921
```

Without `--authorized` the script exits non-zero by design — do not bypass.
Per acquisition (ordered, no reorder/retry/tune): PRIMARY-ONLY read
(concatenation forbidden — Stage A confirmed autofollow) → channel verify (B2)
→ ONE frozen-params delay invocation + gate (B1) → pairing → B0 tier assignment
(B0-1) → skip/CAL/VAL per tier (B8) → framing (B3) → counts_ab (B4) →
H1/H2/H_total + flat H_full → `census.json` with full provenance (B9).
Record B0-1, B1–B9 per TASK_PACKET.md §6. A failed B1/B2 gate or an
INSUFFICIENT tier on one acquisition is recorded as that verdict for that
acquisition — exclude it, continue the rest, do not retry/tune; report
per-acquisition table PLUS `DELAY_GATE_FAIL` / `INSUFFICIENT_LENGTH` counts.
A B6/B7 violation ⇒ STOP the entire run immediately.

After the run, capture for the run log (`workspace/census_20260921/run_log.md`):
commands run, branch, `pip show Swabian-TimeTagger numpy` (or equivalent version lines),
`grep -rn "decoder\|decode" scripts/census_intake_20260921.py` output (B6),
`git status --short` snippet (B7), per-acquisition PASS/FAIL table.

## 5. Return (exactly one of the two)

1. **All-complete**: list of files created + per-ID (A0-1–A0-5, A1–A5, B0-1, B1–B9) PASS/FAIL with
   evidence paths + per-acquisition H table (H1/H2/H_total primary;
   H_full_flat secondary in a SEPARATE column) + run log path.
2. **Concrete blocker**: failing command + exact error/traceback (or adverse
   verdict + ID) + attempted remedies + the SINGLE decision needed.
   "Still incomplete" is not a completion report.

Descriptive census only: no FER, no qualification, no promotion, no
decision-log / memory / index updates.
