# NBPOLAR-PHASE0 freeze review verdict

Date: 2026-09-11  
Verdict: `FREEZE_ACCEPT -> Phase1 judgment unlocked`

## Scope

This verdict accepts only the doc-only Phase 0 alignment freeze in
`openspec/changes/nbpolar-phase0-freeze/`. It authorizes no decoder,
Model-F/CAL/VAL/TTBin load, real-data run, result root, qualification, or
scientific promotion.

## Review history

- Review 1: `needs changes`; four blocking details were returned.
- Repair: F0-4 uses per-Bob-column concentration smoothing; D4R2 provenance
  identifies `build_f` and the correct result-summary lines; F2 points to the
  real packet path; F0-5 triages every match as ban-list, non-reuse boundary,
  or forbidden normative reuse.
- Review 2 supplied by the execution session: `PASS with comments`.
- Main-thread recheck on the current tree: PASS. This file is the durable
  repository record; it does not claim that an absent external review artifact
  was independently reconstructed.

## F0 checklist

- `F0-1 PASS`: canonical architecture uses Mori-Tanaka and Bravo-Santos. It
  explicitly states that Park-Barg is not a Phase 0 dependency.
- `F0-2 PASS`: the scoped path audit has zero Windows drive-path defaults after
  the post-ACCEPT edits; sibling paths are relative provenance only.
- `F0-3 PASS`: `1e-12` and `1e-9` mean absolute maximum error; probability
  metrics are float64 natural logs and bits occur only at report boundaries.
  D4R2 is formula provenance, not NB-Polar performance evidence.
- `F0-4 PASS`: packing round-trip, logsumexp normalization, and synthetic
  concentration column normalization each printed `OK`.
- `F0-5 PASS`: all search matches are ban-list or explicit non-reuse/boundary
  prose; category-(c) normative reuse count is zero.
- `F0-6 PASS`: the freeze sets `plan_accepted: true`; all implementation,
  decoder, real-data, result, and promotion flags remain false.

## Non-blocking comments

- D5 versus F0-5 wording is historical provenance and does not alter the ban.
- Future citations may include the implementation lines 346-349 in addition
  to the `build_f` definition at line 329; both identify the same frozen
  formula.

## Gate

Phase 1 may receive a separate implementation packet. Phase 2 and all
claim-bearing execution remain closed until their own review and authorization.
