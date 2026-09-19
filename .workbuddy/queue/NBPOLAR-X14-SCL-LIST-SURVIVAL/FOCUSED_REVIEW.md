# FOCUSED_REVIEW.md — NBPOLAR-X14-SCL-LIST-SURVIVAL (Tier-X focused numerical review)

Probe: `NBPOLAR-X14-SCL-LIST-SURVIVAL` | Date: 2026-09-20 | Reviewer: reviewer-go (independent) | Session: ses_f454e5ad0ffeCVj4f4fnMY2H6S | Verdict: `X14_REVIEW: PASS_WITH_FINDINGS`

1. prereg/body/results consistency: PASS — prereg 3-line question/parameters/command match body recipes and results frozen block.
2. arithmetic: PASS — pooled means/std recomputed, floor-hit 96/1024=0.09375 exact, counts 100+36+611+6421=7168 and 6946/7168 exact.
3. truth isolation: PASS — no list decoder, allowed imports only, path-refusal asserts.
4. write scope/counters: PASS — 28 SC, rng 1080, tag 0, 15kB; note 106B double-_finish size-record nuance non-blocking.
5a. Q1 near-tautology: FINDING — spikes ≡ model-rare truths ranked by same-row mass.
5b. conditioning deviation: ACCEPTABLE WITHIN-FREEZE NOTE — argmax-p1 plausible decoder-free reading, direction conservative.
5c. channel fidelity: FINDING — 96.9% mismatch ≈ 3.125% chance, Q2 both ≈K/N.
5d. Q2 null: DESCRIPTIVE-PASS, INFERENTIALLY VOID.
6. stop rules: PASS — no protected open, no nonfinite, size < 2 MB, seeds frozen.
7. no claims/SCL-lock: PASS — descriptive only, no thresholds/verdicts, SCL stays locked.

Guardrails: Do not cite Q1=0 as SCL-refuting evidence — it accounts 'model-rare truths rank low by definition'. Do not cite Q2 null as detector evidence — both arms at chance (K/N) on a 96.9%-mismatch near-random synthetic. Carry only: L2-spike coverability under this synthetic definition is zero even with favorable argmax-u1 conditioning; real-data SCL gate still needs a structured-channel probe.
