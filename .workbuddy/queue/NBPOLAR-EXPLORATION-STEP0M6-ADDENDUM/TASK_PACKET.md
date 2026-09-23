# TASK PACKET — NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM (Tier-X: deferred M6 bin-occupancy check)

**GATED PACKET.** Authorizes exactly ONE small addendum probe and nothing else: the
deferred Phase-A check of the M6 occupancy source (`real_frame_batch.parquet`) under the
Step-0 skeleton §3c, with a reader-capable interpreter. User authorization is recorded
verbatim in `STATUS.yaml` (2026-09-23 full-suite instruction); scope is bound here.
Synthetic nothing — this READS a frozen benchmark artifact; no decoder, no real-data
decode, no EVAL/RESERVE contact, no frozen-constant change, no claim.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; Branch (verify `.git/HEAD`):
  `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM/`
- Output root (created by this task): `workspace/exploration/nbpolar-native-highdim/step0-m6-addendum/`
  holding EXACTLY `prereg.md`, `results.json`, `notes.md`.
  **Envelope delta (main thread, recorded):** the accepted design D1 envelope names
  `<step>/` roots; this addendum is a separate Tier-X probe id completing Step-0's
  deferred metric, hence the suffixed root. The completed Step-0 root
  `workspace/exploration/nbpolar-native-highdim/step0/` (prereg.md/results.json/notes.md)
  is READ-ONLY and must remain byte-unchanged — verify at draft check and at the end.
- Parent plan: `step0-survey-prereg-skeleton.md` §2 M6 + §3c + §6 stop rule 3.

## Inputs (read-only)

- M6: `comparison_bench/outputs_comparison/real_frame_batch.parquet` — the candidate
  occupancy source. Also read-only context: `comparison_bench/outputs_comparison/run_manifest.json`
  (provenance context; the frozen benchmark snapshot is synthetic-d8 for the BENCHMARK
  dataset — M6 must be checked against that).

## Task (exact)

1. P0 draft check: branch; packet files; M6 exists; the completed step0 root exists with
   exactly 3 files and is copied-by-hash-free byte check (record sizes; do NOT modify);
   output root absent; a reader-capable interpreter resolved.
2. P1: copy `prereg_frozen.md` → output root `prereg.md`; byte-identity.
3. P2: packet-local stdlib+pyarrow/pandas builder `s0m6_check.py`:
   - Interpreter policy (ordered, nothing installed): (1)
     `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python` (numpy+pandas; pyarrow
     presence to be probed); (2) any other existing interpreter that imports `pyarrow` or
     `pandas` (probe, record); (3) none ⇒ status UNMEASURABLE_FROM_FROZEN_ARTIFACTS with
     the recorded reason (this is a valid terminal outcome, not a failure).
   - If a reader exists: read the parquet; Phase-A checks IN ORDER: (a) a per-pair Alice
     bin-index column exists (record exact column names; Bob column recorded if present);
     (b) alphabet size 1024 — a d=8 synthetic frame batch FAILS provenance; (c) provenance
     is the frozen-contract real population — any `synthetic` marker (e.g. dataset_id
     `synthetic_d8_*` in the file's own metadata or its run_manifest context) FAILS.
   - If all pass: compute c_A over the parquet rows; `o[b] = c_A[b]/n` with the ACTUAL
     row count n as the stated denominator (do not assume 200,192; if the parquet's
     population is not the frozen-contract CHAR population, say so and record the
     denominator — do NOT mix populations); report the fixed descriptives: max_b o[b],
     min_b o[b], max_b o[b] / u, fraction of bins with o[b] < u/2 (u = 1/1024).
   - If any check fails: status UNMEASURABLE_FROM_FROZEN_ARTIFACTS with the failing check.
   - Write `results.json` (keys: probe/tier/question/inputs/checks{reader_attempts,
     column_check, alphabet_check, provenance_check}/occupancy{status, denominator_n,
     max_o, min_o, max_over_u, fraction_below_half_u, reason}/attestation/counters/
     stop_rules_fired) and `notes.md` (attempts, checks, outcome, non-claim statement).
4. P3: report per acceptance IDs.

## Budget & one-shot

wall ≤ 600 s; single-threaded; `s0m_runs: 1`, `reruns: 0`; one corrective rebuild only
after a zero-output crash, recorded.

## Write scope / stop rules

- Allowed: output root (3 files) + packet dir (`s0m6_check.py`, `s0m_run_log.md`).
- Forbidden: ANY write under `comparison_bench/` (read-only), `results/`, the completed
  step0 root, any frozen dir, `.ttbin` paths, other `workspace/` paths, change/archive
  dirs, `AGENT_PROJECT_MEMORY.md`, `docs/`. No installs; no network.
- Stop rules: output root pre-exists; the completed step0 root modified/missing; any
  write outside scope; any decoder/real-data-decode/EVAL/RESERVE contact; any claim
  object (FER/efficiency/etc.) ⇒ hard STOP. A reader-absence or check-failure outcome is
  NOT a stop — it is the recorded UNMEASURABLE terminal per the skeleton §6.

## Acceptance IDs

- **S0M-P** draft check PASS (incl. completed-step0-root integrity and output-root absence).
- **S0M-1** prereg byte-identical; one run; interpreter attempts recorded.
- **S0M-2** all three Phase-A checks executed in order with recorded outcomes.
- **S0M-3** occupancy measured with stated denominator and the four fixed descriptives,
  OR UNMEASURABLE with the failing check; no substitute source; no mixed population.
- **S0M-4** write scope exact; completed step0 root byte-unchanged; nothing else touched.
- **S0M-5** no-FER/no-claim attestation; zero claim language; counters 1/0/1 (one corrective rebuild, zero-output crash, recorded).

## Return (exactly two)

1. All-complete: per-ID PASS + the occupancy outcome (numbers or the failing check) +
   interpreter evidence + scoped write evidence.
2. Concrete blocker: failing command + exact error + attempted remedies + the single
   decision needed.
