# TASK PACKET — NBPOLAR-EXPLORATION-STEP0-SURVEY (Tier-X channel-survey probe)

**GATED PACKET.** Authorizes exactly ONE Tier-X descriptive survey run and nothing else.
User authorization is recorded verbatim in `STATUS.yaml` (`authorizations`) as the overnight
main-thread delegation inside the already-accepted exploration plan; scope is bound by this
packet. No decode, no SC call, no tag, no raw-data read, no EVAL/RESERVE contact, no
frozen-constant change, no claim of any kind.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (**verify `.git/HEAD`**): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0-SURVEY/`
- Probe root (created BY this run): `workspace/exploration/nbpolar-native-highdim/step0/`
  holding EXACTLY `prereg.md`, `results.json`, `notes.md`.
- Parent plan (already accepted 2026-09-23, read-only):
  `openspec/changes/nbpolar-native-highdim-exploration/` — proposal §Step 0, design §D2,
  `step0-survey-prereg-skeleton.md` (the accepted prereg content; this packet freezes the run).
- Nature: **Tier-X probe** (AGENTS.md §10.4): descriptive survey of the residual channel from
  frozen, already-derived artifacts. Non-claim: produces no FER / leakage / efficiency /
  promotion / qualification / composable-key statement; creates no candidate/accepted token;
  consumes no attempt; changes no scientific status. Review path = independent **focused
  numerical review** after the run (not Pre-EXECUTE/Pre-RESULT).

## Inputs (READ-ONLY; every path must exist at draft check — missing ⇒ STOP)

| ID | Path (repo-relative) | Role |
|---|---|---|
| M1 | `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/delta_profiles.json` | PRIMARY: signed-Δ histograms + \|Δ\| summaries + tail gate. Population: SHG_1 (`20260113_SHG_Type2PPLN_3s`) CHAR segment, 200,192 pairs, (N) W_P=200, MOD CIRCULAR, skip-702, derived offset +50 ps (G1R2 contract). Required keys: `acq_id`, `segment`, `n_pairs`, `mod_frozen` (must equal CIRCULAR), `profile.linear_counts` (len 2047, offset −1023), `profile.circular_counts` (len 1025, offset −512), `summaries.CIRCULAR` (`n0`/`n_plus`/`n_minus`/`n_tail`/`n_total`) |
| M2 | `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/delta_profiles.json` | CONTEXT ONLY (superseded G1 contract, `mod_frozen` LINEAR_ONLY, W_P=500). Carried as context; **never numerically compared against M1** (cross-contract comparison forbidden) |
| M3 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/G1R2_ADJUDICATION.md` | Frozen anchor record (wrap closure, CAL triple, H values) — human anchor; builder does not read it |
| M4 | `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/G1_ADJUDICATION.md` | Frozen anchor record (G1 linear profile, tail budget) — human anchor |
| M5 | `.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/S11_ADJUDICATION.md` | Frozen Tier-X record (window grid, wrap-alias accounting) — human anchor |
| M6 | `comparison_bench/outputs_comparison/real_frame_batch.parquet` | CANDIDATE bin-occupancy source ONLY; conditional on the Phase-A schema + provenance check (below); failure ⇒ UNMEASURABLE (never a substitute source) |

## Fixed definitions (verbatim from `step0-survey-prereg-skeleton.md` §3; nothing may be re-chosen)

- **Δ convention:** Δ = b_B − b_A, b_A, b_B ∈ {0,…,1023}; positive = Bob later. Primary
  histogram CIRCULAR, 1025 integer bins k−0.5…k+0.5 centered −512…+512, counts read as-is
  from M1 `profile.circular_counts` (offset −512); no re-binning, no smoothing, no fit.
  LINEAR 2047-bin histogram (offset −1023) reported alongside as the wrap cross-check.
- **|Δ| denominator:** per symbol; n_pairs = 200,192. |Δ| distribution folded as
  \|Δ\|_circ = min(k, 1024−k) for circular bin k (so \|Δ\| ∈ 0…512; ±512 fold together).
- **Occupancy normalization:** o[b] = c_A[b] / n, uniform reference u = 1/1024; reported
  descriptives: max_b o[b], min_b o[b], max_b o[b] / u, fraction of bins with o[b] < u/2.
- **Period-crossing event:** Δ_linear ∈ {−1023, +1023} (M1 `linear_counts` indices 0 and
  2046); period 204800 ps; rate = n_cross / n_pairs (per-symbol denominator).
- **Population for all M1-derived metrics:** the M1 CHAR segment only (200,192 pairs,
  post-skip-702, W_P=200, CIRCULAR, +50 ps). M2 is recorded context, not a second population.

## Builder spec (packet-local, stdlib-first, read-only on inputs)

File: `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0-SURVEY/s0_build_survey.py`
CLI: `--probe-root workspace/exploration/nbpolar-native-highdim/step0/`
(no other arguments; no network; no randomness; deterministic)

Requirements:
1. Stdlib-only core (`json`, `pathlib`, `argparse`, `sys`). No numpy/pandas dependency for
   the M1/M2 path. Optional `pyarrow`/`pandas` import ONLY for the M6 check (see step 7).
2. Load M1; assert required keys, lengths (2047 / 1025), `mod_frozen == "CIRCULAR"`,
   `n_pairs == 200192`, `sum(circular_counts) == n_pairs`, `sum(linear_counts) == n_pairs`,
   `summaries.CIRCULAR.n_total == n_pairs`. Any assertion failure ⇒ **no output written**,
   exit non-zero with the exact failing check (STOP, return condition 2).
3. Emit histograms as-is; compute the |Δ| folded distribution (513 values, \|Δ\| 0…512) and
   `mass_le1 = (abs_hist[1]) / n_pairs` plus `n0`/`n_plus`/`n_minus`/`n_tail` from
   `summaries.CIRCULAR`.
4. Period-crossing: `n_cross = linear_counts[0] + linear_counts[2046]`;
   `rate_per_symbol = n_cross / n_pairs`; report both linear cell counts separately.
5. Wrap-closure cross-check (VERIFY, never correct): circular[−1] (index 511) must equal
   linear[−1] (index 1022) + linear[+1023] (index 2046); circular[+1] (index 513) must equal
   linear[+1] (index 1024) + linear[−1023] (index 0); circular tail (from
   `summaries.CIRCULAR.n_tail`) reported as-is. Compare against the frozen anchors quoted in
   `STATUS.yaml` (44 / 1 / 451 / 48832 / tail 0) and report `frozen_anchor_match` booleans.
6. Context M2: load; record `mod_frozen`, `summaries` headline counts (n_plus/n_minus/n_tail/
   n_total) under key `context_m2_never_compared` with the never-compare note. NO M1-vs-M2
   arithmetic anywhere.
7. Occupancy (M6): try `import pyarrow` (or `pandas.read_parquet`) with each available
   interpreter in the ordered policy below; read the parquet; Phase-A checks: (a) a per-pair
   Alice bin-index column exists (and a Bob column if present); (b) alphabet size is 1024
   (NOT d=8 synthetic); (c) provenance indicates the frozen-contract real population
   (inspect parquet metadata / adjacent columns / `run_manifest.json` as needed — synthetic
   `dataset_id` such as `synthetic_d8_*` ⇒ provenance FAIL). If interpreter, column,
   alphabet, or provenance checks fail ⇒ `bin_occupancy.status =
   UNMEASURABLE_FROM_FROZEN_ARTIFACTS` with the failing reason recorded (this is the designed
   conditional, NOT a blocker, and NEVER licenses a substitute source or a mixed population).
   If all pass: compute c_A over the parquet rows, state the actual denominator n explicitly
   (it may differ from 200,192 — say so), report the four fixed descriptives.
8. Emit `results.json` (required keys below) and `notes.md` (provenance, interpreter policy
   actually used + M6 attempts, stop rules fired, wrap-closure results, non-claim statement)
   into the probe root. Single write at end of run; partial failure ⇒ no output files.
9. `results.json` required top-level keys: `probe`, `tier` ("X"), `question`, `inputs`
   (per-ID id/path/role/read), `population` (acq_id, segment, n_pairs, mod_frozen, W_P,
   MOD, skip, offset provenance), `metrics.{delta_histogram_circular, delta_histogram_linear,
   abs_delta_distribution, period_crossing, wrap_closure_check, bin_occupancy}`,
   `context_m2_never_compared`, `attestation` (`no_fer_object: true`, `no_claim: true`,
   `ledger: "L3 descriptive — never cited as L1 FER"`), `counters`, `stop_rules_fired`.
10. §5.7 minimalism: plain stdlib script, no checksums, no atomic writes, no retry
    framework, no schema validator, no logging framework; errors as plain messages with
    non-zero exit.

## Interpreter policy (ordered; record which was used in notes.md)

1. `.venv/bin/python` if it exists (it does NOT in this checkout — verified 2026-09-23);
2. else `/home/karel_303/.venvs/timetagger/bin/python` if it exists (repo-documented packet venv);
3. else `python3` — permitted ONLY because the builder core is stdlib-only; record this as a
   documented deviation from AGENTS.md §8 with the reason in `notes.md`.
For the M6 parquet attempt, try each available interpreter until one imports `pyarrow` or
`pandas`; record every attempt and failure. Never install anything.

## Exact command

```
python3 .workbuddy/queue/NBPOLAR-EXPLORATION-STEP0-SURVEY/s0_build_survey.py --probe-root workspace/exploration/nbpolar-native-highdim/step0/
```
(the interpreter token is chosen per the policy above and recorded; everything else is exact)

## Budget & one-shot

wall ≤ 300 s; RSS ≤ 2 GiB; single-threaded; `s0_runs: 1`; `reruns: 0`; one corrective
rebuild permitted ONLY if the first run crashes leaving ZERO probe-root outputs (recorded in
`STATUS.yaml` counters + `notes.md`). No parameter, path, or definition may change between
prereg and run.

## Write scope

- Allowed: probe root — EXACTLY `prereg.md`, `results.json`, `notes.md`; packet dir —
  `s0_build_survey.py`, `s0_run_log.md`.
- Forbidden (hard stop): `results/`, `comparison_bench/outputs_comparison/` (read-only
  INPUTS only), any frozen directory, any `.ttbin` path, any other `workspace/` path, any
  existing change/archive directory, `AGENT_PROJECT_MEMORY.md`, `docs/` (main-thread owned),
  any repo-root tracked file. The unrelated dirty/untracked worktree files
  (`.codebuddy/`, `.workbuddy/memory/*`, `docs/nbpolar/*DRAFT*`,
  `comparison_bench/outputs_comparison/test_fixtures/*`, `workspace/pytest-evidence-test/**`,
  `.workbuddy/queue/NBPOLAR-M2-PRIOR-*`) stay untouched.

## Stop rules (any ⇒ STOP + blocker report, return condition 2)

1. Draft check fails: branch mismatch; packet file missing; any M1–M5 input missing/
   unreadable; M1 lacking required keys/lengths; probe root already exists with content.
2. Any §3 definition cannot be applied as written (ambiguity requiring re-derivation).
3. M6 schema/provenance check fails ⇒ occupancy := UNMEASURABLE_FROM_FROZEN_ARTIFACTS
   (designed conditional; not a blocker; never substitute a source or mix populations).
4. Any write outside scope; any raw-data / decode / EVAL / RESERVE contact; any
   cross-contract M1-vs-M2 numeric comparison ⇒ hard STOP.
5. Any FER / efficiency / claim object produced ⇒ hard STOP (the survey produces none by
   construction).

## Phases

- **P0 Draft check** (writes nothing except an optional packet-dir check log): verify
  branch, packet files, M1–M5 existence, M1 keys/lengths, interpreter availability, probe-root
  absence. Report PASS/FAIL. If FAIL ⇒ STOP (return condition 2). If PASS ⇒ continue.
- **P1** Copy `prereg_frozen.md` → probe root `prereg.md`; verify byte-identity.
- **P2** Write the builder per spec; run ONCE via the exact command; builder writes
  `results.json` + `notes.md`.
- **P3** Report per acceptance IDs below. The operator NEVER marks its own work accepted.

## Acceptance IDs (operator reports; main thread accepts)

- **S0-P** Draft check PASS (branch, packet files, M1–M5 exist, M1 keys/lengths, interpreter
  policy resolved, probe root absent).
- **S0-1** Probe-root `prereg.md` byte-identical to `prereg_frozen.md`.
- **S0-2** `results.json` has every required key; histogram sums equal 200,192; every rate
  carries its denominator; M2 carried context-only.
- **S0-3** Wrap-closure arithmetic internally consistent AND matches the frozen anchors
  (44 / 1 / 451 / 48832; circular tail 0), recomputed from M1 arrays.
- **S0-4** Occupancy handled per stop rule 3 (measured with provenance OK, or
  UNMEASURABLE with the failing reason; no substitute source; denominator stated).
- **S0-5** Write scope exactly the three probe-root files + packet-local files; nothing else
  touched (scoped evidence: list probe root + packet dir; confirm no other writes).
- **S0-6** No-FER/no-claim attestation present in `results.json` and `notes.md`; counters
  `s0_runs: 1`, `reruns: 0`; zero claim language anywhere in outputs.

## Return (exactly two — AGENTS.md §10.1)

1. **All-complete:** per-ID PASS with output paths, the key survey numbers (n0 / n_plus /
   n_minus / n_tail, mass_le1, n_cross + rate, wrap-closure booleans, occupancy outcome),
   counters, interpreter used, and scoped write-scope evidence.
2. **Concrete blocker:** failing command + exact error/traceback + attempted remedies +
   the SINGLE decision needed from the main thread.
