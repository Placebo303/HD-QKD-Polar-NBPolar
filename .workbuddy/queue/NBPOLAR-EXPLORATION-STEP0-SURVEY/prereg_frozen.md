# PREG (FROZEN) — NBPOLAR-EXPLORATION-STEP0-SURVEY (amendment 1 applied 2026-09-23)

> Copied verbatim into the probe root BEFORE any computation (TASK_PACKET P1). Parameters,
> definitions, command, write root, budget and stop rules are frozen here; nothing may
> change between this file and the run. Amendment 1 (main thread, 2026-09-23) corrected the
> M1 shape facts to the frozen artifact (circular 1024 cells; summaries at
> `profile.summaries.CIRCULAR`) — no definition intent and no number changed.

- **Probe:** NBPOLAR-EXPLORATION-STEP0-SURVEY — Tier-X (AGENTS.md §10.4), non-claim.
- **Question:** Is the residual channel of the frozen DEVELOPMENT population
  (±1-dominated? heavy-tail? period-crossing?) of a type where preserving inter-level
  conditional dependence could plausibly matter? (proposal §Step 0)
- **Population (frozen):** M1 = `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/delta_profiles.json`
  — SHG_1 (`20260113_SHG_Type2PPLN_3s`), CHAR segment, n_pairs = 200,192, (N) W_P=200,
  MOD CIRCULAR, skip-702, derived offset +50 ps (G1R2 contract). No sampling; descriptive
  over frozen derived data (no models, no seeds).
- **Inputs:** M1 (primary), M2 (`..._3s/delta_profiles.json`, CONTEXT ONLY, G1 w=500
  LINEAR_ONLY — never numerically compared to M1), M3–M5 (frozen anchor records, human
  anchors, not read by the builder), M6 (`comparison_bench/outputs_comparison/real_frame_batch.parquet`,
  CANDIDATE occupancy source, conditional on the Phase-A schema+provenance check).
- **Fixed definitions (per `step0-survey-prereg-skeleton.md` §3 as amended):**
  Δ = b_B − b_A over bins 0…1023; primary CIRCULAR histogram = 1024 cells covering residues
  −512…+511 (M1 `profile.circular_counts`, offset −512, read as-is); LINEAR 2047-cell
  cross-check (offset −1023); |Δ| folded over residues j=0…1023 as min(j, 1024−j) ∈ 0…512,
  denominator per symbol n_pairs = 200,192; occupancy o[b] = c_A[b]/n with uniform ref
  u = 1/1024 (descriptives: max, min, max÷u, fraction < u/2); period-crossing ⟺
  Δ_linear ∈ {−1023, +1023}, period 204800 ps, rate = n_cross/n_pairs.
- **Wrap-closure index arithmetic (0-based, offsets applied; VERIFY, never correct):**
  linear index = k + 1023; circular index = k + 512. circular[−1] = idx 511,
  circular[+1] = idx 513. Check circular[511] == linear[1022] + linear[2046]
  (frozen anchors 450 + 1 = 451) and circular[513] == linear[1024] + linear[0]
  (frozen anchors 48788 + 44 = 48832); circular tail = `profile.summaries.CIRCULAR.n_tail`
  (frozen anchor 0). mass_le1 = (circular[513] + circular[511]) / 200192.
- **Exact command:**
  `<interpreter> .workbuddy/queue/NBPOLAR-EXPLORATION-STEP0-SURVEY/s0_build_survey.py --probe-root workspace/exploration/nbpolar-native-highdim/step0/`
  (interpreter per TASK_PACKET ordered policy: `.venv/bin/python` → timetagger venv →
  stdlib-only `python3` deviation, recorded).
- **Write root:** `workspace/exploration/nbpolar-native-highdim/step0/` — exactly
  `prereg.md`, `results.json`, `notes.md`. Nothing else, anywhere.
- **Budget:** wall ≤ 300 s, RSS ≤ 2 GiB, single-threaded, one run (`s0_runs: 1`,
  `reruns: 0`; one corrective rebuild only after a zero-output crash, recorded).
- **Stop rules (TASK_PACKET §Stop rules, binding):** missing/unreadable input or M1
  key/length/shape failure ⇒ STOP (no outputs); §3 ambiguity ⇒ STOP; M6 schema/provenance
  failure ⇒ occupancy UNMEASURABLE_FROM_FROZEN_ARTIFACTS (designed conditional, never a
  substitute); any out-of-scope write, raw-data/decode/EVAL/RESERVE contact, or
  cross-contract M1-vs-M2 numeric comparison ⇒ hard STOP; any FER/efficiency/claim object
  ⇒ hard STOP.
- **Non-claim:** produces no FER object of any kind; L3 descriptive-survey ledger only;
  never merged into, compared numerically against, or cited as L1 real-data FER.
