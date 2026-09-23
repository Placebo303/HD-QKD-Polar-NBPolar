# PREG (FROZEN) — NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM

> Copied verbatim into the output root BEFORE any computation.

- **Probe:** NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM — Tier-X, non-claim.
- **Question:** can the deferred M6 bin-occupancy metric of the Step-0 skeleton be
  measured from the frozen artifact `comparison_bench/outputs_comparison/real_frame_batch.parquet`
  — i.e. does it pass the Phase-A reader/column/alphabet/provenance checks — and if so,
  what is the Alice marginal bin-occupancy non-uniformity (max/min, max÷u, fraction < u/2,
  u = 1/1024)?
- **Inputs:** M6 (above, read-only) + `run_manifest.json` (provenance context only).
- **Phase-A checks (in order; any failure ⇒ UNMEASURABLE_FROM_FROZEN_ARTIFACTS with the
  failing check):** (1) reader-capable interpreter exists (nothing installed); (2)
  per-pair Alice bin-index column exists; (3) alphabet size 1024 (d=8 synthetic FAILS);
  (4) frozen-contract real provenance (any synthetic marker FAILS).
- **Occupancy rule (on full pass):** c_A over the parquet rows; o[b] = c_A[b]/n with the
  ACTUAL row count n stated (never assume 200,192; never mix populations); fixed
  descriptives max/min/max÷u/fraction<u/2.
- **Exact command:**
  `<interpreter> .workbuddy/queue/NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM/s0m6_check.py --out-root workspace/exploration/nbpolar-native-highdim/step0-m6-addendum/`
  (interpreter per ordered policy: hd-qkd-polar-comparison venv first, then any existing
  pyarrow/pandas-capable interpreter, else the UNMEASURABLE terminal).
- **Protected root:** `workspace/exploration/nbpolar-native-highdim/step0/` (completed
  Step-0 probe) — read-only, byte-unchanged (verified at draft check and at the end).
- **Write root:** `workspace/exploration/nbpolar-native-highdim/step0-m6-addendum/` —
  exactly `prereg.md`, `results.json`, `notes.md`. Nothing else, anywhere.
- **Budget:** wall ≤ 600 s, single-threaded, one run (`s0m_runs: 1`, `reruns: 0`).
- **Stop rules (packet §Stop rules, binding):** output root pre-exists; protected root
  modified/missing; out-of-scope write; any decoder/real-data-decode/EVAL/RESERVE
  contact; any claim object ⇒ hard STOP. Reader-absence/check-failure ⇒ UNMEASURABLE
  terminal (recorded, not a stop).
- **Non-claim:** descriptive L3-ledger readout only; no FER / efficiency / promotion /
  qualification / composable-key statement.
