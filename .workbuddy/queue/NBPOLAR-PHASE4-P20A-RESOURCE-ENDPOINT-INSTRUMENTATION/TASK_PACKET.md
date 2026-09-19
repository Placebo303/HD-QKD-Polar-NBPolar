# Phase 4-P20A — resource classification and endpoint instrumentation

## Mission

Repair the shared NB-Polar failure-classification seam and add the minimum
endpoint records needed for future L1/L2 mechanism attribution. This is an
implementation/accounting task with injected inputs only.

## Allowed work

- Audit broad `except Exception` blocks around SC calls in the shared
  NB-Polar operational helpers used by P16-P19 and their direct successors.
- Ensure `MemoryError` escapes to the caller's resource-stop path.
- Preserve the explicitly accepted decode/nonfinite exception taxonomy.
- Add injected L1- and L2-site `MemoryError` tests, including call/disclosure
  accounting at the stop.
- Add or expose separate scalar endpoint fields for L1 exact, hard-L2 exact,
  oracle-L2 exact and complete-pair exact where future runners need them.
- Correct documentation that treats the 233/384 and 377/384 endpoints as
  symmetric L2 counts.

## Forbidden work

- No protected artifact, HOLD, TRAIN, VAL, EVAL or raw-data read.
- No decoder experiment, real run, historical rerun or result rewrite.
- No change to GF32, transform, SC arithmetic, prior/floor, construction,
  disclosure K, tag, outcome precedence or accepted evidence roots.
- No SCL, new kernel, new model, new data schema or route decision.
- No commit or push.

## Acceptance IDs

- `P20A-R1`: every audited internal SC `MemoryError` reaches resource handling.
- `P20A-R2`: injected L1 and L2 tests distinguish resource from decode failure.
- `P20A-R3`: ordinary decode/nonfinite behavior and accounting remain unchanged.
- `P20A-R4`: endpoint names distinguish L1, hard-L2, oracle-L2 and pair exact.
- `P20A-R5`: focused predecessor suites pass with injected data only.
- `P20A-R6`: no protected read, scientific attempt, output root or result claim.

## Return conditions

Return only when all IDs are complete, or on a concrete blocker with the exact
command/error, attempted remedy and one decision needed from the main thread.
An operator cannot accept its own work or authorize P20B.

