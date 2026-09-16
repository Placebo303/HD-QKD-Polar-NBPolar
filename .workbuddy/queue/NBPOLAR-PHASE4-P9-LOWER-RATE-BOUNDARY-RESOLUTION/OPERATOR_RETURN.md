# Operator return — NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION (CANDIDATE)

**Result label (candidate, not acceptance): `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE`.**
Main-thread acceptance is pending; this document is a factual operator return only.

## 1. Mission

Resolve the P8 left-censoring limitation: the P8 35-point grid (`K1>=8`, `K2>=80`)
could not probe below the selected anchor `(K1=8,K2=80)`, so no global
minimum-rate claim was possible. P9 is a delta-only Tier-Y successor that runs a
SCREEN over an extended 56-point grid reaching the zero axes (`K1=0`, `K2=0`,
including `(0,0)`) plus the P8 `(8,80)` anchor, then a disjoint CONFIRM at the
deterministically selected point only.

## 2. Gate identity

- Gate id: `p9-lower-rate-boundary`; P9 protocol name / tag-domain prefix /
  result labels throughout the five artifacts (zero P8-identifier hits).
- Frozen packet: `.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/`
  (`TASK_PACKET.md`, `STATUS.yaml`, `P9_FREEZE.md`,
  `P9_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`).
- Evidence root (read-only): `lower_rate_screen_confirm/` (five files, §8).

## 3. Orders, support, preconditions

- Accepted P7 orders reused verbatim, sha
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`.
- V25 1M TRAIN NPZ (`channel_counts.npz`, 25166822 B) read-only; support rule =
  column-normalize + `1e-15` floor + column renormalize (no lambda/backoff/tuning).

## 4. SCREEN summary

- Seeds `2026091710..1712` x64 (192 paired blocks) over the exact 8x7 grid
  `K1=[0,2,4,6,8,12,24,45]` x `K2=[0,20,40,50,60,70,80]` = 56 points, including
  `(0,0)` and the P8 anchor `(8,80)`.
- Exactly 10 eligible points (Wilson one-sided 95% LB >= 0.95):
  `(6,70,188)`, `(6,80,188)`, `(8,70,192)`, `(8,80,192)`, `(12,70,192)`,
  `(12,80,192)`, `(24,70,192)`, `(24,80,192)`, `(45,70,192)`, `(45,80,192)`.
- `(0,0)`: exact 0/192 (verify_failed 192; tag-only arm, zero undetected).
- Deterministic lexicographic selection: `(k1=6,k2=70)`; selection key `(76,6,70)`.

## 5. CONFIRM results

- Seeds `2026091720..1724` x128 (640 paired blocks), disjoint from SCREEN and
  from all prior streams; selected point only, plus same-K BEC control
  (report-only).
- Empirical 624/640 exact (16 verify_failed); BEC 520/640 (120 verify_failed).
- Paired cells: both 520 / empirical_only 104 / bec_only 0 / neither 16.
- Wilson one-sided 95% LB `0.9626753340557015` (>= 0.95, >= 618/640 met).
- Per-stream empirical `[122,123,125,127,127]`; per-stream BEC
  `[103,102,97,108,110]`.

## 6. Disclosure and accounting

- `5*(K1+K2)+64` key-dependent bits per fully invoked point: selected
  `(6,70)` = 444 bits vs P8 anchor `(8,80)` = 504 bits (report-only observation);
  `(0,0)` = 64 tag-only.
- Public control 2623 bits; tag accounted per fully invoked point.
- Totals: key 4392768 / public 31559936 / tags 12032 (56x192+640x2 cross-check);
  transcript recount mismatch 0.
- Planning-only realized `f` for the selected point: `2.165159928897918`.
- Artifact wall 720.522313 s; RSS 318406656 B.

## 7. Consumption (frozen counters, no rerun)

- Reads 1/1 + attempts 1/1 consumed at the first NPZ content open; the NPZ was
  never reopened, no seed/grid/order/floor/threshold change, no rerun or tuning.
- Tests: 24 focused + 252 full NB-Polar (240 + 12).

## 8. Execution incident (Wave-C delegation; recorded durably, main-thread adjudication)

The first Wave-C delegation executed the frozen command and flushed the 5-file
root at 15:29:50, but its result delivery failed on an infrastructure
certificate error; the retry operator found the root present and correctly
STOPPED without running anything (`BLOCKED(prior-output-exists)` return,
nothing consumed by the retry); a read-only inspection then verified the root
as the genuine product of exactly one frozen execution (0.3 s contiguous flush,
P9 identifiers only, 56x192+640x2 shapes, frozen command verbatim in
`frozen_plan.json`); STATUS counters were aligned to reads/attempts 1/1; NO
rerun ever occurred. This incident changes no scientific fact; the evidence
root is the single attempt's product.

## 9. Independent reviews

- Pre-EXECUTE: **PASS** (zero blocking issues; non-blocking notes only).
- Pre-RESULT: **PASS** (zero comments; all numbers recomputed from the five
  artifacts; 11 integrity + 2 scientific gates recomputed true; label
  `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` confirmed as the correct
  frozen-label outcome).

## 10. Five-file inventory (`lower_rate_screen_confirm/`, read-only)

| File | Size (B) |
|---|---|
| `frozen_plan.json` | 7989 |
| `report.md` | 6059 |
| `screen_records.json` | 10077718 |
| `selection_and_confirmation_records.json` | 1105258 |
| `transcript_accounting.json` | 1612 |

Single 0.3 s contiguous flush at 15:29:50; P9 identifiers only; zero P8 hits.

## 11. Bounded scope

Synthetic N=256 V25-1M-TRAIN model-sampled development signal only. Not
held-out/real FER, not efficiency/key-rate, not scaling, not qualification or
promotion. The BEC gap and the anchor-vs-selected disclosure comparison are
report-only; no interpolation between grid points is claimed.

## 12. Unrun stages / next gate

None unrun at operator level. Next gate is **main-thread acceptance** (pending).
No commit/push performed.
