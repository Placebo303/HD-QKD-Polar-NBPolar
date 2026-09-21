# Phase 4-P0 prior-contract freeze (FREEZE_ACCEPT)

> **PARTIALLY SUPERSEDED (2026-09-21)** — The following are superseded by
> `openspec/changes/nbpolar-prior-rebaseline/` (±1 parametric prior):
>   - §1: the `f[a,b]=(counts+λ·p_global)/(n_b+λ)` nonparametric prior
>     formula and `DECODER_FLOOR=1e-15`
>   - §5: the 262,144-symbol (1024-frame) CAL that fits counts/`lambda`
> Everything else in this document — §2 axis/provenance table, §3
> SymbolMetric API, §4 tensors, §6 validation matrix, §7–§8, and the
> truth-isolation requirements — REMAINS IN FORCE. Retained for provenance.
> Read `docs/nbpolar/STATE.md` first.

Companion OpenSpec change: `openspec/changes/formal-ir-nbpolar-phase4-p0/`
(proposal/design/tasks/specs). Packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P0-PRIOR-CONTRACT-FREEZE/TASK_PACKET.md`.
Independent reviewer-go returned PASS WITH COMMENTS and the main thread
accepted this contract. Implementation/CAL/Model-F/real-data/decoder/P1 remain
unauthorized. No `.py` was added or modified; no data was loaded or executed.

## 1. Prior contract (exact)

```text
p_global[a] = sum_b counts[a,b] / sum_{a,b} counts[a,b]
n_b[b]      = sum_a counts[a,b]
f[a,b]      = (counts[a,b] + lambda*p_global[a]) / (n_b[b] + lambda)
```

Reference: `comparison_bench/src/comparison_bench/formal_ir/v72p2d4r2_cal_gf32_model_rate_audit.py`
`build_f` (:329-375). D5 twin: `.../v72p2d5_gf32_rate_mother.py`
`build_f_model_concentration` (:274-305) via `prepare_model_f_prior_candidate`
(:2361-2388). Banned twin: same file `build_f_model` (:246-271, `sm=counts+lam`
:265) via `prepare_model_f_prior` (:2330-2358) — `LAMBDA_APPLICATION_CONTRACT_DEFECT`.
`LAMBDA_STAR=137.3823795883264`, `FLOOR=1e-300` (audit CE),
`DECODER_FLOOR=1e-15` (D5 :46-48), `NORM_TOL=1e-12`, `CHAIN_TOL=1e-10`.

## 2. Axis / provenance table

| # | Source path: callable | In → out (shape/dtype) | Axis / normalization | Smoothing / packing | Provenance | Status |
|---|---|---|---|---|---|---|
| 1 | `.../v72p2d4r2_...audit.py:build_canonical_counts` | `(alice[n],bob[n])` int64 0..1023 → `counts` (1024,1024) float | axis0 Alice, axis1 Bob; none | none / full symbols | CAL-only | ACCEPTED canonical builder |
| 2 | `.../v72p2d5_model_f_input.py:build_model_f_input` | injected arrays → `counts_ab` (1024,1024) int64 + `p_b` (1024,) float64 | `[Alice,Bob]`; `p_b=sum(axis0)/262144`, `p_b==marginal` checked 1e-12 (:147-149) | `lambda*` carried, not applied / `symbol=low+32*high;high=U1;low=U2` (:164-167) | CAL702..1725, 262144 syms | ACCEPTED input path |
| 3 | `.../v72p2d4r2_...audit.py:build_f` | TRAIN `(a,b)` → `P_A_given_B` (1024,1024) `[A,B]` + `P_U1_given_B` (1024,32) `[B,U1]` + `P_U2_given_U1_B` (32,1024,32) `[U1,B,U2]` | cols (P_F) / rows (P1) / last-axis (P2) sum 1, 1e-12 | §1 formula; unseen-B→`p_global`; zero-slice→uniform; `symbols_to_layers` :236-243 | CAL TRAIN-only, 30-pt inner-grid `lambda` | ACCEPTED formula |
| 4 | `.../v72p2d5_gf32_rate_mother.py:build_f_model_concentration` + `prepare_model_f_prior_candidate` | `counts_ab` → `p_f` (A,B) | columns sum 1, 1e-12 asserted | §1 formula; zero-col→`p_global` | D7-C H03 accepted (decision-log:3506) | ACCEPTED for NB-Polar |
| 5 | same file: `build_f_model` + `prepare_model_f_prior` | `counts_ab` → `p_f` | columns normalized | per-cell `counts+lam` | historical LDPC production | BANNED for NB-Polar |
| 6 | `.../v72p2d3_gf32_contrast.py:_smooth_counts` / `build_stage1_P` / `build_stage2_P` | CAL vectors → `[Bob,U1]` / `[U1,Bob,U2]` tables | rows sum 1 | `lam*p_global` but transposed layout; synthetic-only (:492,:515) | synthetic/diagnostic | REJECTED (scope+layout) |
| 7 | D5 `marginalize_f_to_p1` (:308) / `conditionalize_f_to_p2` (:323) | `p_f` → `[U1,B]` (32,n_b) / `[U1,B,U2]` | col / last-axis sum 1 | reshape assumes `Alice=U1*32+U2` | derivation | ACCEPTED (transpose P1 explicitly vs row 3) |
| 8 | D5 `app_fed_l2_prior` (:353); V50–V55 `get_l1_app_prior_l2`; V35 `require_check_updated_provenance` (:540) | beliefs+`p2` → L2 prior | renormalized | `DECODER_FLOOR` 1e-15 | cross-layer APP, fail-closed | EXCLUDED from first SC path |
| 9 | V35 `get_conditional_posterior_l2` (:432); D5 `oracle_l2_prior` (:378) | `(counts,bob,u1)` → `(N,32)` | rows sum 1 | floor 1e-15 + renorm | oracle/true-U1 diagnostic pattern | REFERENCE pattern only |
| 10 | `formal_ir/nbpolar/sc.py:sc_decode` (:188) | `logp_x` (N,q) float64 → `SCResult` | rows `logsumexp 0`, `-inf` kept (:88-121) | log domain; no smoothing | operational, truth-free | ACCEPTED consumer |
| 11 | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/algebra.py:make_gf32` (:40); `comparison_bench/src/comparison_bench/formal_ir/nonbinary_field.py:get_field_spec` | — → GF32 poly 37, basis polynomial, LSB-first labels | symbols `0..31` int labels | bit packing §3, never GF1024 mult | field identity | ACCEPTED |
| 12 | D7-A `v72p2d7_gf32_decoder_certification.py` (:22-52); D7-B/C provenance (`...bidirectional_oracle.py:119-121`; `...schedule_discriminator.py:114-116`) | independent tables / labels | — | `Q=32`, poly `0b100101`=37 | independent oracle + `PRIOR_ONLY` lineage | REUSABLE PATTERN only |

Packing (§3): D5 spells this as `low=s%32`, `high=s//32`; equivalently,
`low=s&31`, `high=(s>>5)&31`, `s=low+32*high`, `U1=high`,
`U2=low` (D4R2 :236-243; D3 :377-411; D5 :400-416; V35 :421-429).
Conditioning: joint full-Bob `B∈0..1023`; `conditioning=FULL_BOB_ONLY`.

## 3. SymbolMetric API (frozen)

```text
SymbolMetric(logp: float64[N,q], conditioning: FULL_BOB_ONLY,
             provenance: PRIOR_ONLY | ORACLE_CONDITIONED | CANDIDATE_CONDITIONED,
             symbol_order: 0..q-1, normalization: LOGSUMEXP_ZERO)
```

Helpers (separate from object): `smooth_joint_to_conditional`,
`derive_p1`, `derive_p2`, `build_p1_metrics`, `gather_p2_metrics`,
`probs_to_symbol_metric` (`0→-inf`, else `ln p`, row-normalize),
`apply_explicit_floor` (opt-in, caller-recorded). Floor forbidden by
default; DEV may preregister one bounded value; EVAL immutable. Never APP.

## 4. Tensors

```text
P1[frame,i,a]      = P(A_high=a | B_full)                  (F,N,32)
P2_true[frame,i,a] = P(A_low=a | A_high_true, B_full)      oracle only
P2_hat[frame,i,a]  = P(A_low=a | A_high_hat_hard, B_full)  executable, hard
```

Natural-U order. No per-symbol context exists; `ctx=RESERVED`.

## 5. Lifecycle

CAL: `20260123_1M_600k_0dB`, 1M, frames 702..1725, 262144 symbols — fits
counts/`lambda`, freezes adapter. DEV: `DEV-FUTURE-DISJOINT` (IDs frozen at
P1 auth; may select floor / diagnose D3 only if preregistered). EVAL:
`EVAL-SINGLE-USE-DISJOINT` (IDs frozen at P1; tunes nothing).
`VAL1726-1729` banned for construction/smoothing/floor/thresholds.
Diagnostics D1 (L1-exact/P1), D2 (L2-oracle/P2_true, upper-bound mechanism),
D3 (L2-candidate/P2_hat, executable dependency); paired identities; failure
precedence metric→shape→known→impossible (failed, own class)→nonfinite
(hard)→mismatch. Truth only in D2 + scoring; oracle helper test-local, never
exported from `nbpolar/`.

## 6. Validation matrix (absolute max-error unless noted)

| ID | Gate | Oracle / ground truth | Failure category → first diagnostic | Blocks |
|---|---|---|---|---|
| V-P0-01 | Axis/transpose sentinel on asymmetric hand-built counts | hand-computed expected P table | axis/transpose → column-vs-expected diff + reshape layout | implementation |
| V-P0-02 | Per-Bob-column sums =1 within 1e-12 | direct column sums | normalization → max `abs(colsum-1)` | implementation |
| V-P0-03 | Adapter vs direct literal formula ≤1e-12 | independent literal formula (D7-A pattern, no shared helper) | smoothing → max-abs diff + argmax cell | implementation |
| V-P0-04 | Prob→log round trip on `p>0` ≤1e-12 | `exp(logp)` vs `p` on positive mask | log conversion → max-abs err | implementation |
| V-P0-05 | Exact-zero stays `-inf` unless formula made it positive | zero mask of P table | support → violating cells | implementation |
| V-P0-06 | GF32 packing round-trip exhaustive `0..31` + selected 10-bit pairs | split/combine identities | packing → first mismatch triple | implementation |
| V-P0-07 | Batch/position permutation equivariance | permuted-gather vs gather-permuted | batch axis → max-abs diff | implementation |
| V-P0-08 | One-hot/noiseless + uniform-prior SC sanity via Phase-2 oracle | `oracle_sc_metric` + noiseless loopback | metric wiring → oracle compare triple | decoder execution |
| V-P0-09 | CAL/DEV/EVAL ID non-overlap + provenance assertions | frozen ID lists + token check | lifecycle → overlap diff | CAL/data execution |
| V-P0-10 | Truth-leak sentinels for P1 + candidate-L2 (mutated-Alice no-change; no operational import of oracle helper) | adversarial truth mutation + import allow-list | truth leak → diff + import graph | decoder execution |
| V-P0-11 | Held-out CE vs uniform + unsmoothed baselines, chain `<1e-10` | DEV held-out `CE(P1*P2)` | model → CE table + chain err; threshold frozen from CAL/DEV only | performance claim only |
| V-P0-12 | Runtime/memory for N=256 metric creation, no decoder (≤60 s wall, <2 GiB RSS on ≤1024-frame synthetic build) | wall/RSS measurement | resource → profile | decoder execution |

## 7. Alternatives

A dense `(N,32)` materialization — SELECTED (§memory trivial, §oracle
testable, §isolation structural). B table+gather — DEFERRED (add past
budget). C lazy callback — DEFERRED (provenance opacity). Floor:
forbidden-default/DEV-selectable. P1: joint full-Bob. L2-candidate: hard
conditioning sufficient first; soft `q@P` deferred (APP provenance).

## 8. Risks / non-claims

No Model-F, real-data, FER/leakage/key-rate, or performance conclusion
follows. `CE 3.814742/3.347605/7.162347` are D5 CAL-domain descriptives,
never NB-Polar inputs. DEV/EVAL concrete IDs intentionally unfrozen (CAL
read forbidden in P0) — frozen at P1 authorization. Release checkout never
opened; binary LLR/PW/XOR/CA-SCL reuse banned by inherited docs.
