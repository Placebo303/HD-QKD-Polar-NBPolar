# FOCUSED_REVIEW.md — NBPOLAR-X17-METRIC-FEED-AUDIT

- Probe: `NBPOLAR-X17-METRIC-FEED-AUDIT` | Date: 2026-09-20 | Reviewer: reviewer-go (independent) | Verdict: `X17_REVIEW: PASS_WITH_FINDINGS`
- Scope: focused numerical review only (prereg/body/results consistency, arithmetic, truth isolation, write scope, H-a localization, control-arm readings, no-claims). No decoder execution, no protected opens. Descriptive-only; SCL stays locked whatever the numbers say.

## Adjudications (one line each)

1. prereg/body/results consistency PASS (prereg byte-identical, all frozen arms + 5 selftests embedded, results carries all fields).
2. arithmetic PASS (A0 0.75098/0.94704, A1 0.95801-vs-0.41113 same-decode contrast, A2 0.68848 misses [0.05,0.45], A3 0.66211, A4rev 0.75879/0.95690, A4randomK 0.75293, A5uni 0.77441/0.97660, A5flip 0.76660/0.96675, P 0.000 exact 4/4 in [0.00,0.05], C 0.76318/0.96103, G2 1.0≥0.50, G3 253/1024=0.24707∈[0.02,0.70]).
3. truth isolation PASS (sole decoder greedy sc_decode, refused-module asserts, sole writer results.json).
4. write scope + counters PASS (3 files, 38/26/0, <2 MB, no commit/push).
5. H-a localization PASS (X16 body.py:420 misnames X-domain high/low as u-truth, :448-449 feeds X as U known_values, :465 scores U-output vs X-truth; X17 A0 replays, A1/A2 corrected; production two_layer.py:629-634 correct and untouched).
6. positive-control reading PASS-WITH-QUALIFICATION (P=0.000 proves decodability under control conditions only; does NOT exclude working-point defects).
7. C-arm reading PASS-WITH-QUALIFICATION (corrected full-scale ≈ chance does NOT prove sub-threshold; causes undistinguished; synthetic-vs-real structure mismatch open).
8. no-claims PASS (descriptive-only, SCL locked).

## Non-blocking notes

C "≈chance" descriptive-not-exact; random-K≈first-K qualitative; seed-absence/T0-T1/single-execution operator-asserted but internally consistent.

## Citation guardrail

May cite: H-a real + code-localized; A0 reproduces X16 chance scoring; A1 0.958-vs-0.411 proves the scoring half; P vindicates metric-feed end-to-end in control regime; production unaffected; G2/G3 wiring intact. May NOT cite: FER/reliability/efficiency verdicts; A2/C as sub-threshold proof or real-channel property; P as working-point evidence; numerical random-K≡first-K; or anything SCL-related.
