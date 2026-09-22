# D4 MAIN-THREAD RECORD — NBPOLAR-M2-PRIOR-K-RESPLIT-D4 (2026-09-22)

Label: `NBPOLAR_M2_PRIOR_K_RESPLIT_D4_COMPLETE_REPORT_ONLY` — **planning input; ADOPTS NEITHER branch.**

## 1. Basis

User authorization pasted verbatim (kai, 2026-09-22). One operator STOP (see §2) resolved by a main-thread scope
ruling; then operator all-complete return (D4-A..D4-D PASS) + independent focused numerical review
`D4_PASS_WITH_COMMENTS` (zero blocking; every number recomputed to full precision; scope compliance and the
no-adoption boundary verified).

## 2. The STOP and the ruling (process record)

The packet as first written said **"decoder-free"** in Non-Goals and in a stop rule, while simultaneously requiring
the frozen `select_empirical_split`, whose pooled `e/h` inputs can only be produced by the genie/SC path
(`block_genie_risks` → `genie_layer_risks` → `genie_conditionals` → `sc_decode`). The operator correctly STOPPED
rather than improvising a substitute (H-proportional, BEC-surrogate and a new DE path were all rejected).

Main-thread ruling: the packet, not the operator, was at fault. The authorization and FORBIDDEN forbid
decoder/genie/SC **on protected data** (`any decoder/genie/SC call on protected data`); synthetic M2 blocks have
zero protected contact. Corrected boundary (binding, in-packet):
- **ALLOWED**: synthetic genie TRAIN — 16 synthetic M2-model TRAIN blocks, seeds 2026100101–2026100116, via the
  frozen path; genie calls registered and reported.
- **UNCHANGED FORBIDDEN**: any protected/real read; any protected decoder/genie/SC; construction re-derivation;
  H-proportional as a selection rule; any adoption; any frozen-constant change.
- Descriptive label changed to **"no protected-data contact; synthetic-only"** (the "decoder-free" label was withdrawn).
- **R5**: the pre-clarification "K_total 6946 ⇒ f exactly 1.3 closure check" is mathematically unattainable
  (the budget literal's floor discards ~0.96 bits); replaced by an explicit deviation statement.

## 3. Results (recomputed in-packet; independently verified)

Inputs (frozen from G1R2): H_M2 = 0.8168138204133305 (H1 0.02525363754305251 + H2 0.791560182870278), N = 32768,
budget literal `K_total = floor((f·N·H − 64)/5)`.

- Branch A (fixed f = 1.3): N·H = 26765.355267304014 → 1.3·N·H = 34794.96184749522 → −64 = 34730.96184749522
  → ÷5 = 6946.192369499045 → floor **K_total = 6946** (+135 vs the frozen G2 point 6811).
- Branch B (fixed K_total, f derived): f(6811) = **1.2747449**; f(6946) = **1.2999641** (deviation
  **−3.59e-5** from 1.3, reported never rounded — R5); f(7020) = **1.3137879**.
- (K1,K2) per branch from the frozen `select_empirical_split` (imported, never reimplemented; `k_total` required,
  no literal), e/h pooled from the 16 synthetic M2 TRAIN blocks:

| K_total | f implied | K1 | K2 | TRAIN residual |
|---|---:|---:|---:|---:|
| 6811 (frozen G2 point) | 1.2747449 | 328 | 6483 | 1.414e-4 |
| **6946 (fixed-f branch)** | 1.2999641 | 335 | 6611 | 7.454e-6 |
| 7020 (1.5M scale) | 1.3137879 | 346 | 6674 | 1.386e-6 |

- H-proportional contrast (211,6600)/(215,6731)/(217,6803) — present as a **NON-SELECTING** descriptive column
  only; banned as a selection rule, as required.
- The 6811 re-split (328, 6483) vs the frozen (319, 6492) is recorded as descriptive contrast only.

## 4. Compliance

32 registered genie calls (16 blocks × 2 layers), **all synthetic**; `sc_calls_on_protected = 0`;
zero protected/real data contact (imports only); 6/6 focused tests green; NO-ADOPTION banner in report.md +
results.json; frozen G2 K (319/6492) untouched; no construction re-derivation; no FER/efficiency/qualification
language; writes confined to `workspace/m2_prior_validation/k_resplit_d4/` + the test file + packet STATUS.
Venv deviation (sibling venv instead of timetagger) is non-material — the timetagger venv lacks pandas, which the
frozen import chain requires; no TimeTagger/data path is used; disclosed in run_log.

## 5. Status and what this does NOT do

- **ADOPTS NEITHER BRANCH.** The fixed-f vs fixed-K_total choice remains a later preregistered main-thread/PI
  decision (D4). These numbers are planning inputs for a future rate freeze and are **not** a license to re-split
  inside G2 or G3: G2 decodes at the frozen 319/6492.
- Docs-only corrections applied after review: `PROMPT.md` stale "6946 ⇒ exactly 1.3" line replaced by the R5
  tolerance; `AUTHORIZATION_PROMPT.md` stale "decoder-free" label replaced by the clarified boundary.
- Milestone batch (decision-log / memory / index / scoped commit) is main-thread work executed after this record.
