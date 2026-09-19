# FOCUSED_REVIEW_PENDING.md — NBPOLAR-X17-METRIC-FEED-AUDIT

- Probe result: COMPLETE (`X17_PROBE_COMPLETE_DESCRIPTIVE_ONLY`;
  `workspace/probes/nbpolar_x17_metric_feed_audit/results.json`).
- Key numbers (pooled/descriptive only): A0 0.751 all / 0.947 undisclosed
  (≈ chance 0.96875 — bug replay as predicted); A1 rescore of the SAME
  decode: u_hat-vs-U-true 0.958 vs x_hat-vs-X-true 0.411 (far below
  chance); A2 corrected U-truth feed 0.688 all (misses the descriptive
  [0.05, 0.45] band); A3 oracle-u1 0.662; A4 controls nominal
  (shuffle-identical TRUE 4/4, bit-reversed 0.957 ≈ chance, random-K ≈
  first-K); A5 uniform/sign-flip ≈ chance (0.977/0.967 undisclosed);
  P positive control 0.000 exact 4/4; C full-scale N=32768 corrected feed
  0.763 all / 0.961 undisclosed (≈ chance).
- Main-thread adjudication: H-a probe-side U/X truth confusion CONFIRMED
  and localized — probe-body only (X16 `body.py` fed X-domain high/low
  as U known_values and scored U-output vs X-truth); no production
  impact (production `two_layer.py:629-634` moves truth to U-domain
  correctly). A genuine feed/decoder defect is RULED OUT (P = 0.000
  exact). But the remediated full-scale operating point still sits at
  chance (C undisclosed 0.961) ⇒ sub-threshold operating point, not a
  wiring bug.
- An independent focused numerical review of the probe arithmetic is
  pending and milestone-batched (Tier-X probes batch ledger updates at
  milestones per AGENTS.md §10.4); it cannot change the probe's
  descriptive-only status or unlock SCL.
