# Operator return — NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM (candidate)

**Result: `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE` — pending main-thread acceptance. This is a candidate, not an acceptance.**

## 1. Mission

One Tier-Y static rate gate at N=256 on the accepted V25 1M TRAIN model:
select the lowest-disclosure grid point clearing the frozen SCREEN rule,
then test that single point once on disjoint CONFIRM streams with a paired
BEC-order control (report-only). Single gate executed once (exit 0,
artifact wall 522.26697 s, RSS 274264064 B). No rerun, no tuning.

## 2. Orders, support, preconditions

- Accepted P7 pooled empirical L1/L2 orders, sha
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`,
  valid 256-permutations (recorded == recomputed == frozen).
- V25 1M TRAIN NPZ 25166822 B read-only (size/mtime unchanged) via the
  accepted loader; floor-only support rule (floor 1e-15); P7
  entropy/support preconditions rechecked before any SC call.
- Reads 1/1 + attempts 1/1 consumed at the first NPZ content open
  (`open_count` 1); no reopen, no retry, no rerun. No Model-F, raw,
  held-out, real, or EVAL data; V25 NPZ and Model-F/real data untouched.

## 3. SCREEN summary and selection

- SCREEN seeds 2026091680..1682 x64 (192 shared blocks) over the exact
  35-grid K1=[8,10,12,16,24,32,45] x K2=[80,94,110,125,140], shared-block
  sampling (identical block per grid point).
- ALL 35 points eligible (exact/Wilson LB>=0.95 each): 1x189/3vf,
  4x190/2vf, 6x191/1vf, 24x192/0vf; undetected/decode-failed/nonfinite/
  resource_abort 0 everywhere.
- Deterministic selection (lexicographic min of (K1+K2,K1,K2) over
  eligible only): **(k1=8, k2=80)**, key-dependent disclosure 504 bits
  (5*(8+80)+64).

## 4. CONFIRM results, cells, Wilson, disclosure

- CONFIRM seeds 2026091690..1694 x128 (640), disjoint from SCREEN;
  selected point only + same-K BEC control (report-only).
- Empirical 638 exact / 2 verify_failed; BEC 621 / 19; paired cells both
  621 / empirical_only 17 / bec_only 0 / neither 2.
- Wilson one-sided 95% LB 0.9906013676984646 (>=0.95; 638>=618/640 met).
- Per-stream emp/bec: 127/124, 128/122, 128/123, 128/127, 127/125.
- Disclosure 5*(K1+K2)+64 per fully invoked point (selected 504),
  public 2623 bits/tag; totals key 5470080 / public 20984000 / tags 8000;
  transcript recount mismatch 0. Planning-only f 2.457749108478718.
- Integrity 11/11 true; scientific 2/2 true. Tests: 12 new, 240 total
  (228+12).

## 5. Independent reviews

- Pre-EXECUTE: **PASS** (seed-coincidence ratified FRESH — P8 SCREEN
  2026091680..1682 never consumed as official streams; P7 consumed only
  TRAIN 1650..1652 / DEV 1660..1664).
- Pre-RESULT: **PASS_WITH_COMMENTS**, all comments non-blocking
  (C1 observed H/open_count verified indirectly — schema never required
  machine persistence; C2 unrelated worktree dirt, P8 scope clean;
  C3 this closeout fixes STATUS).

## 6. Five-file inventory (`rate_screen_confirm/`, read-only)

| file | bytes |
|---|---|
| `frozen_plan.json` | 7838 |
| `report.md` | 6007 |
| `screen_records.json` | 6264408 |
| `selection_and_confirmation_records.json` | 1105263 |
| `transcript_accounting.json` | 1603 |

## 7. Bounded scope

Synthetic N=256 V25-1M-TRAIN model-sampled development signal only. Not
held-out/real FER, efficiency/key-rate, N-scaling, qualification, or
promotion. BEC gap (17 cells) report-only; empirical was not required to
beat BEC.

## 8. Unrun stages / closure

Unrun stages: none — main-thread acceptance remains (next gate
`MAIN_THREAD_ACCEPTANCE`). No commit/push; no code, artifact, or old-root
change; no OpenSpec box checked.
