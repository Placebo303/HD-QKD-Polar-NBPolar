# P11 implementation notes (Wave-A)

## Decisions

- OpenSpec delta written before any production edit (P11-01); production
  diff is confined to `_minus_block` plus the new thin runner.
- `_minus_block` keeps positional `(first, second, index)` compatibility and
  adds keyword-only `chunk_rows=512`, so the single existing call site in
  `sc_decode` is untouched and the production path becomes chunked by
  default with zero call-site churn.
- `_normalize_rows` runs once over the full assembled matrix, exactly as the
  X12 probe proved bitwise-equivalent; per-slice normalization was rejected
  because re-normalizing near-zero logsumexp residuals is not bitwise
  identical to a single normalization.
- Output buffer sized `(rows, first.shape[1])`; `rows=0` degrades to the
  same empty result as the direct path.
- `bool` is rejected explicitly before the `Integral` check (Python `bool`
  subclasses `int`); numpy integers remain accepted as integrals.
- New focused tests live entirely in `test_nbpolar_sc_chunked.py`; the
  canonical `test_nbpolar_sc.py` was left untouched to minimize blast radius.
- The gate runner enforces the frozen seed/chunk values fail-closed
  (matching prior frozen-point runner style) and converts mid-run blocks
  into partial-evidence four-file writes with the earliest `BLOCKED(<gate>)`
  label; only pre-decode refusals write nothing (exit 2).
- The runner was deliberately never executed in this wave; its Step 1-3
  logic mirrors the X12 probe body plus the production `None`-arm, but
  Wave-C Pre-EXECUTE must re-verify it by reading (a first-run bug cannot be
  fixed by rerun after attempt consumption).

## X12 promotion notes

- Promoted expression: per contiguous slice
  `first[s:e][:, index] + second[s:e][:, None, :]`,
  `np.logaddexp.reduce(axis=2)`, single full-matrix `_normalize_rows`.
- Promoted evidence: 36/36 primitive cells exact, 16/16 V0 parity, 9/9
  controls at N=64 and N=256, restoration identity intact, N=262144
  chunk512-only median 65.73 s with 754.6 MB cumulative HWM (descriptive;
  supports the 1.5 GiB hard gate and the report-only 120 s / 1 GiB targets).
- X12 used chunk sizes [32,128,512,2048]; P11 freezes production default 512
  and keeps `None` as the golden comparator. The gate matrix reuses X12's
  row boundaries, kinds, control definitions, and C4 search schedule with
  the new frozen seed 2026091800 (fresh; X12 used 2026091780).

## Review items flagged for Pre-EXECUTE / Pre-RESULT

1. Runner never executed in Wave-A: re-read `run_chunked_gate` step order,
   RNG stream order, C4-search boundedness, and the four-file writers
   against this freeze before authorizing.
2. `except GateBlocked` inside `run_chunked_gate` references
   `paired_record`/`scaling_record` via `dir()`-guarded fallback; confirm
   partial-evidence behavior is acceptable for mid-step-1 blocks.
3. `main()` maps a non-candidate label to exit 1 and refusals to exit 2;
   confirm exit-code expectations for the Wave-C harness.
4. Cumulative-HWM RSS attribution (ru_maxrss/VmHWM) is process-wide, not an
   isolated arm footprint; the hard gate compares this peak against
   1.5 GiB, consistent with X12's descriptive 754.6 MB reading.
5. Focused-test C4 search uses fresh test seeds with a bounded 400-try
   schedule; both N=64/256 controls established green in this wave.
6. Dirty-worktree note: the checkout carries pre-existing unrelated
   modifications (P3 queue docs, AGENTS.md, memory, empirical modules);
   this wave touched only the seven P11 files listed in the return and
   preserved everything else.
