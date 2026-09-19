# P20M main-thread acceptance

- Date: 2026-09-19. Main thread (orchestrator). Packet: `NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M`.
- Gate records: Pre-EXECUTE **PASS** (reviewer-go session `ses_f487e1984ffehLtiRnmG90vJXs`,
  `PRE_EXECUTE_REVIEW.md`); Pre-RESULT **PASS** (reviewer-go session `ses_f4867e19dffeqmQF1neRfPzhV0`,
  `PRE_RESULT_REVIEW.md`).
- Operator return: `OPERATOR_RETURN.md`; single authorized run, exit 0, wall 104.85 s,
  RSS ~531 MB, retries 0, pasted command byte-identical to `FROZEN_COMMAND`.

## Acceptance

The Stage-B result is ACCEPTED AS DESCRIPTIVE under label
`TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE` (integrity 25/25, recount mismatch 0,
`undetected` 0 isolated). No recovery / FER / qualification / promotion / efficiency
claim is made or implied.

## Ledger reconciliation (after the Pre-RESULT caveat)

- `stage_b_authorized: true` (filled STEP-2 pasted); protected-data read authorized for
  the one DEV open; decoder authorized for the one-shot; **attempts 1/1 SPENT; DEV 1/1 SPENT;
  HOLD 0/1; counts-calibration 0/0**.
- Worktree-file loads only (prior + P20H calibrated npz; never the V25 counts NPZ);
  1M refused; 2M never opened/statted/listed; no overwrite under `results/` or
  `comparison_bench/outputs_comparison/`; no commit/push.

## Descriptive result (as reviewed)

| arm | point | exact | first errors (per block) |
|---|---|---|---|
| G0_old_point_base | λ prior, 319/6492 | 0/3 | L1/24, L1/5, L1/17 |
| G1_raw_prior_session_budget | raw prior, 331/6689 | 0/3 | L2/26 (l1_exact TRUE), L1/848, L2/31 (l1_exact TRUE) |
| G2_true_l1_diagnostic | oracle, K2 6689 | 0/3 | L2/26, L2/3646, L2/31 |

- `g1_restored_count` 0 (no G0-fail → G1-exact event); `undetected` 0;
  nonfinite/decode_failed/resource_abort 0; key recount 308376; public 2949687;
  tags 9/9; SC 15/15; Stage-B sampling 0.

## Scientific reading (descriptive; planning input only)

1. The X08 λ diagnosis is confirmed operationally: with the corrected prior + session-derived
   budget, L1 stopped failing immediately (first errors moved from ~2–17 to 848 / L2-layer)
   and 2/3 blocks reach hard-L1-exact (`l1_exact` TRUE).
2. The bottleneck moved to **L2**, and this is the FIRST genuine out-of-sample L2 evidence at
   the 1.5M point: the oracle arm (true L1) is 0/3 on VAL 1660..2043 at K2=6689, whereas oracle
   arms on TRAIN segments were 3/3 exact. L2 failures under true L1 at coordinates 26/3646/31
   cannot be attributed to the hard-L1 candidate.
3. §16 L2-implication triggers: **BOTH fired** — (i) new-point oracle non-exact (G2 0/3);
   (ii) bottleneck-layer move (G1 operational first errors L2-layer on 2/3 blocks). The P20D
   candidate / L2-side single factor therefore becomes live as main-thread planning input.
   Nothing is auto-triggered inside this packet; no follow-up is licensed by this acceptance.
4. No restoration/recovery evidence: `g1_restored_count` 0; operational 0/6; oracle 0/3.
   2M remains pristine for a future independent-session confirmation; the 1M-HOLD thread
   stays open.

## Honest scope (verbatim, §0)

this packet tests the corrected prior + session-derived budget at the operational point on the
first genuinely out-of-sample 1.5M segment; it does not establish NB-Polar real-block recovery
in general, does not close the 1M-HOLD thread, and the current published gates on DEV must not
be confused with out-of-sample evidence.
