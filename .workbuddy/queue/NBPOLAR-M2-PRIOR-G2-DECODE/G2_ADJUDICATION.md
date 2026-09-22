# G2 MAIN-THREAD ADJUDICATION — NBPOLAR-M2-PRIOR-G2-DECODE (2026-09-22)

Label: `NBPOLAR_M2_PRIOR_G2_SUCCESS` — Tier-Y one-shot three-arm decode on SHG `_1` (w=200 / CIRCULAR).
**Verdict: SUCCESS** (adopt M2 for the next gate, G3 — independent-session confirmation).

## 1. Basis

User authorization pasted verbatim (kai, 2026-09-22) + independent freeze review PASS (after three FAIL cycles:
B1–B5, then two residual one-line fixes) + Pre-EXECUTE PASS (S1 deferred-loader mechanism ACCEPT-WITH-CONDITION;
S3 arms-spelling fix verified) + **one-shot execution** + **Pre-RESULT PASS** (publication/commit MAY proceed; zero
blocking findings; all Tier-Y properties verified independently). Counters: `g2_runs: 1`,
`sc_calls_on_protected: 126` (= 3/block × 42), `tag_invocations: 42`, `reruns: 0`.

## 2. Result

| Arm | Prior / CAL | exact | Wilson 95% (n=14, z=1.96) | Gate role |
|---|---|---:|---|---|
| **B** | M2 CANDIDATE @ matched 32f | **11/14** | **[0.5241027623, 0.9242875166]** | candidate |
| **A2** | M0 @ matched 32f | **0/14** | [0.0, 0.2153170119] | comparator |
| **A1** | M0 @ own 1024f (incumbent) | **0/14** (all `verify_failed`) | — | descriptive, **no gate** |

**SUCCESS**: Wilson-lower(B) = 0.5241 > Wilson-upper(A2) = 0.2153 — strict non-overlap, as preregistered.
`undetected` = 0/42 and isolated (never merged into success/FER); `nonfinite` = 0; `decode_failed` = 0;
`resource_abort` = 0; taxonomy over 42 rows = {exact 11, verify_failed 31}. Disclosure recount mismatch 0
(key 1,432,998 = 34,119 × 42; public 13,765,206 = 327,743 × 42; 42 tags from tag_master 2026103001).
Budget: per-block wall min/mean/max 19.49/19.68/20.26 s; total **855.1 s ≤ 900**; RSS 1.12 GiB ≤ 2;
`budget_aborted: false`. Frozen contract intact: K1=319/K2=6492, P16 orders (len 32768) + pinned inner digest
`055c9064…c3faea1b`, W_P=200/W_S=500/CIRCULAR/skip=702, EVAL 2398–4189 = 14 blocks, segments all-disjoint,
alignment repro 50 / 112.45189572400645 / ok, ledger 4219 (216 dropped).

## 3. Adjudication

1. **SUCCESS is adopted** — the preregistered gate was met on the first (and only) verdict-bearing execution;
   no rerun, no tuning, no seed/threshold/K/window/MOD change.
2. **What this establishes**: at frozen K and frozen P16 construction, on SHG `_1` under the w=200/CIRCULAR
   contract, the M2 ±1 CANDIDATE restores complete blocks where the **matched-CAL M0 control restores none**
   (11/14 vs 0/14, strictly non-overlapping CIs), with `undetected` isolated and disclosure recount exact.
3. **What this does NOT establish** (binding): no FER-as-population estimate; no efficiency, qualification,
   promotion, or composable net-key claim; **no cross-contract superiority** vs G1 (w=500/LINEAR, which stands
   as its own bounded negative); no claim that the ±1 model is "true" (q_rest = 0 remains a weak statement at a
   32-frame CAL: zero-observation bound 3/8192 = 3.66e-4 — G2 is the test of whether that matters, and it passed
   here, but the bound is unchanged); no G3/SHG `_2` result.
4. **A1 = 0/14 is a descriptive first measurement** of the incumbent as-deployed regime on SHG data — it is NOT a
   benchmark claim and NOT a failure of the incumbent proof. It is recorded for what it is: the first time the
   1024-frame incumbent regime has been measured on this source.
5. **M2 remains a CANDIDATE until G3 passes.** D6's gate sequence is G1 → G2 → **G3 (independent session)** → G4
   (exhaustive public-message inventory). G2 SUCCESS unlocks G3; it does not complete the D6 sequence.

## 4. Diagnostic finding carried forward (Pre-RESULT comment 1 — does NOT affect the gate)

The isolated oracle third SC call conditions on `views["u1"]` (polar-transformed), whereas the frozen operational
path (`operational_f13.run_operational_block`) conditions L2 on `high_hat` (untransformed high — the domain
`derive_p2` is built in). Consequence visible in the artifacts: `oracle_l2_exact` = 0/42 on all arms (even the 11
B-exact blocks where `high_hat == high_true`), and the `nll_l2_trueH` (~6.3) vs `nll_l2_candH` (~45–47) pair is
non-discriminative across arms, while the **operational** hard-L2 path discriminates (B 11/14 vs A1/A2 0/14).
The gate uses only the frozen operational path + tag + label, so **SUCCESS arithmetic is unaffected**.
Recorded as a domain-semantics note: for G3 and any future NLL interpretation, "H-conditioned L2" must state
which domain (untransformed `high_hat` vs polar-transformed `u1`). No re-derivation or re-run for G2.

## 5. Ledger / next gates

- Parent packet: G2 outcome recorded; T6 (freeze) and T7 (execute) complete.
- **G3 (SHG `_2`)** — **UNLOCKED**: the held authorization (kai 2026-09-22) becomes operative; precondition met
  (G2 SUCCESS). Contract inherited; alignment method inherited with reproduction check vs census σ ≈ 114.4 ps;
  K frozen 319/6492; tag_master 2026110101 (EVAL_SEED 2026100101); participation disclosure required in every
  output (decoder/model independence, NOT no-prior-contact independence).
- Re-split: still DEFERRED. The D4 report (K_total 6946 under fixed-f=1.3; f(6811)=1.2747, f(7020)=1.3138) is a
  planning input for a later rate freeze and is NOT a license to re-split inside G3.
- Consumption: SHG `_1` decode blocks 2398–4189 (14 blocks) consumed; frozen-session remainder untouched;
  SHG `_2` untouched until G3's own Phase-A closure.
- Milestone batch (decision-log / memory / STATE / index / scoped commit) is main-thread work executed after this
  adjudication.
