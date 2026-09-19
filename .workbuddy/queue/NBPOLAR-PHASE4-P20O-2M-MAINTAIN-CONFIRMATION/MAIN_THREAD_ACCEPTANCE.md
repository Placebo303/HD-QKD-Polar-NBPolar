# P20O main-thread acceptance

- Date 2026-09-19. Packet `NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION`.
- Gate records: Pre-EXECUTE **PASS** (`ses_f46e4e9ddffeqvIlFewSzcTLVv`,
  `PRE_EXECUTE_REVIEW.md`); Pre-RESULT **PASS** (`ses_f46d1de2dffeuf2NvfKKrLeJ9W`,
  `PRE_RESULT_REVIEW.md`).
- Operator return: single run, exit 0, wall 215 s, RSS ≤ 651 MiB, retries 0.

## Acceptance

ACCEPTED AS DESCRIPTIVE under label
`TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE`
(integrity 29/29 gate keys true — operator's "28/28" is a count slip; recount 0;
`undetected` 0 isolated). No recovery / FER / reliability / efficiency claim.

## Result (as reviewed)

| arm | point | exact | notes |
|---|---|---|---|
| A 2M-incumbent-L2 operational | 334/6746 | 0/5 | L1 failures b0/b4 (@6834/14296); L2 failures b1/b2/b3 |
| B 2M-alt-L2 operational | 334/6746 | **2/5** | **b1, b2 EXACT**; b0/b4 L1 failures; b3 L2 |
| C 2M-incumbent-L2 oracle | 0/6746 | 0/5 | L2 failures all 5 |
| D 2M-alt-L2 oracle | 0/6746 | **3/5** | **b1, b2, b4 EXACT**; b0 L2; b3 L2 |

`b_restored_count 2` (b1, b2: A-fail→B-exact), `b_maintained 0`, `d_restored 3`,
`d_maintained 0`; key `692580 = 10*35464 + 10*33794`; public `6554860`; SC 30;
tags 20; sampling 0.

## Scientific reading (descriptive; planning input only)

1. **Restoration replicated on an independent session**: with the same frozen
   `ALT-L2-LAPLACE-α1` construction at the 2M session's own derived point, B restores
   2/5 blocks (b1, b2) where the incumbent arm A is 0/5. Combined with P20N on 1.5M
   HOLD (B 1/4 vs A 0/4): **3 restoration events across two independent sessions**
   (B 3/9 vs A 0/9, descriptive, block-level).
2. Oracle-vs-operational gap persists: D 3/5 > B 2/5 (b4: D exact while A/B fail at
   L1; b0: all arms fail). Residuals remain on both layers — L1 is not universal on
   2M (b0/b4 operational L1 first errors at natural coords 6834/14296) and L2 still
   fails b3 under all arms.
3. **X09-R1 H2 sub-question closed**: the ninth U-domain scalar shows all 11 L2
   failures are natural-index-in-X-prefix but **U-domain-out** → genuine
   undisclosed-region SC errors; no disclosure-pinning violation (definitively
   resolves the P20N domain-mixed reading).
4. No maintain events (A is never exact) — the alt construction *restores* blocks the
   incumbent loses; "maintenance" has not been demonstrated because no incumbent
   successes exist. No reliability claim; no promotion.
5. Scale discipline: 5 blocks / 20 records, one segment, single draw. The 2M VAL DEV
   `2187..2826` is CONSUMED regardless of outcome; remainder `2827..2915`, 2M HOLD
   `2916..3644`, and all 1M/1.5M data remain untouched.

## Ledger

counts-calibration 1/1 SPENT; 2M VAL-DEV 1/1 SPENT; attempts 1/1 SPENT;
VAL-remainder 0; 2M HOLD 0; 1M/1.5M 0; no overwrite under `results/` or
`comparison_bench/outputs_comparison/`; no commit/push.

## Honest scope (verbatim, packet §0)

first use of the reserved 2M independent session to attempt to maintain one prior 1.5M
restoration event with the frozen construction; positive/negative both informative; no
reliability claim; 1.5M VAL remainder and the 1M-HOLD thread stay out of scope; 2M is
consumed by this packet regardless of outcome.
