# P20N main-thread acceptance

- Date 2026-09-19. Packet `NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M`.
- Gate records: Pre-EXECUTE **PASS** (`ses_f480b89c3ffeF7kAH133WfZ4lf`,
  `PRE_EXECUTE_REVIEW.md`); Pre-RESULT **PASS** (`ses_f47de58a6ffeXDdb5E69vrIfzx`,
  `PRE_RESULT_REVIEW.md`).
- Operator return: `OPERATOR_RETURN.md`; single run, exit 0, wall 164.37 s,
  RSS 631.2 MB (< 2 GiB), retries 0.

## Acceptance

ACCEPTED AS DESCRIPTIVE under label
`TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE`
(integrity 28/28 gate keys true — operator's "26/26" is a count slip;
recount mismatch 0; `undetected` 0 isolated). No recovery / FER / reliability /
efficiency claim is made or implied.

## Result (as reviewed)

| arm | point | exact | first errors (natural block index) |
|---|---|---|---|
| A incumbent-L2 operational | 331/6689 | 0/4 | 111 / 76 / 3 / 81 |
| B alt-L2 operational | 331/6689 | **1/4** | 1009 / 20 / 5823 / — (**b3 2597..2724 EXACT**) |
| C incumbent-L2 oracle | 0/6689 | 0/4 | 111 / 76 / 3 / 81 |
| D alt-L2 oracle | 0/6689 | **1/4** | 1009 / 20 / 5823 / — (**b3 EXACT**) |

`b_restored_count 1`, `d_restored_count 1`, `b_maintain_count 0`; all 14 failures
L2-layer; L1 exact on all 8 operational records; key `549384`; public `5243888`;
SC 24; tags 16; Stage-B sampling 0.

## Scientific reading (descriptive; planning input only)

1. **First operational exact block on the 1.5M session, out-of-sample, fixed
   disclosure**: the α=1 Laplace L2 construction restored block 3 under BOTH the
   hard-L1 operational path (B) and the true-L1 oracle (D) — the gain is
   L2-metric-side, not L1-side.
2. Floor/heavy-tail exonerated in-run (neighbourhood floor fraction 0.0 on every
   failing record); the alt metric carries HIGHER average prefix hazard
   (0.8925–0.9035 vs 0.7954–0.8556) yet decoded one block exactly — descriptive
   support for "incumbent spikiness, not average length, drives the
   out-of-sample L2 failures".
3. Scale discipline: 1 of 4 blocks (one shared event, one session); this licenses
   NO reliability claim, NO promotion, NO confirmation. The deferred
   `b_restoration_branch_maintain_confirmation_round` is the live next branch.
4. X09-R1 H2 instrumentation payload: `l2_fail_in_prefix` true on 12/14 failures
   (false only on the shared B-b2/D-b2 event @5823) — reviewer-adjudicated as a
   frozen-definition domain artifact (X-domain error index vs U-domain disclosure
   set), not a disclosure-pinning violation. A U-domain cross-check would need
   arrays not persisted (successor instrumentation item).

## Ledger

counts 0/0; HOLD 1/1 SPENT; attempts 1/1 SPENT; VAL-remainder 0; 1M refused;
2M pristine by non-access; no overwrite under `results/` or
`comparison_bench/outputs_comparison/`; no commit/push.

## Honest scope (verbatim, packet §0)

this packet tests ONE preregistered alternative L2 construction at fixed
disclosure on the first HOLD-segment use; it can restore L2 or falsify this
construction; a budget-infeasible construction is returned without consuming
HOLD; it licenses no reliability/recovery claim; 2M and VAL remainder remain
untouched; the 1M-HOLD thread stays open.
