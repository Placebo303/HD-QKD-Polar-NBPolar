# TASK_PACKET.md — NBPOLAR-X15-STRUCTURED-CHANNEL-LIST-SURVIVAL (frozen Tier-X probe, approved-pending-freeze)

Probe: `NBPOLAR-X15-STRUCTURED-CHANNEL-LIST-SURVIVAL` | Tier: X (non-claim, synthetic-only, decoder-free)
Workdir: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` | Branch: `codex/nbpolar-phase0`
Authorizing record: `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md` §4 D3 + user standing pre-authorization 2026-09-20
Cost class: zero-cost synthetic diagnostic. Consumes NO counts/DEV/HOLD/VAL reads and NO attempt.
Status: APPROVED_PENDING_FREEZE (main thread applied standing pre-authorization 2026-09-20; freeze only next).

## 0. Read-only inventory (verified by planner grep/read, no execution)

| Path | What it provides | Status |
|---|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_channel.py` | Caller-injected table sampler; no structured/diagonal sampler exists | Present; reuse read-only (sampling recipes only, tables injected by body) |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/synthetic.py` | q-ary QSC/erasure generators | Present; NOT used by X15 (different channel family) |
| X06 probe (`NBPOLAR-X06-EMPIRICAL-CONSTRUCTION-ORDER-PROBE`) | Only probe that consumed a real-derived table | Recorded scalars reused as QUALITATIVE context only: f_min 0.0002142 / f_max 0.3392 / h1 4.2867 / h2 3.2227 (λ-smoothing differs, no quantitative transfer) |
| P20J TASK_PACKET (lines 11, 77) | Recorded raw SER ~0.2520 / 0.2526 / 0.2535 (1.5M population) | Provenance for p_err=0.25 pin (population caveat, §4) |
| X14 ancestor (`NBPOLAR-X14-SCL-LIST-SURVIVAL`, PASS_WITH_FINDINGS) | Near-random channel outcome | Mismatch 6946/7168 = 96.9% ≈ chance; Q1 0.0 structural; Q2 void (no variance to cover) |
| Fresh seeds `2026092369..2377` + `nbpolar_x15_structured_channel_list_survival` | Planner grep absent 2026-09-20 | Absent; operator re-verifies by repo grep at freeze (§7) |

## 1. Questions (identical to X14)

**Q1 (primary):** With the synthetic channel structure reproduced (here: structured diagonal
concentration + 96/1024 planted floor-mass pin kept), does the TRUE path survive in an L=4 / L=8
candidate list at L2 spike positions — i.e., is the true `(b, u1, u2)` cell within the top-L
ranked candidates under the frozen arm-table/prior likelihood? Ranking-only coverability
analysis; SCL stays locked whatever the numbers say. Per-position top-L survival is a
necessary-condition proxy for list decoding, not proof of SCL path survival — reported as
coverability evidence only.

**Q1b (secondary, same machinery):** The symmetric L1 rank — is the true `u1` within the top-L
of the `p1[·,b]` column ranking? Directly relevant to gate condition 3 for an L1 list.

**Q2 (secondary):** Does a local-spike detector select the positions where greedy-SC mismatches
actually occur better than mean-hazard (global top-K hazard) ranking — the H2a-REFUTED baseline?
Coverage fractions only, descriptive.

## 2. Frozen definitions (X14 §2 reused VERBATIM)

**Hazard atom (frozen recipe, `l2_alt_hold_1p5m.py:1321`):**
`h_j = −log2 p2[u1_cond_j, b_j, u2_true_j]`, bits base 2; exact-zero mass raises (never replaced
by uniform; synthetic construction guarantees positive arm-table mass).

**Spike definition (frozen quantities only):** Let `pm = mean(h_j)` over the disclosed prefix
(the `l2_prefix_hazard_mean_bits` recipe). Position `j` is a **spike** iff excess
`e_j = h_j − pm ≥ 2.0` bits. **Strata** by excess depth: `[2,4)`, `[4,8)`, `[8,∞)` bits, plus a
non-spike reference stratum (`e_j < 2.0`, recorded as `nonspike_ref`). Margin and bins are
descriptive recording buckets, never thresholds or verdicts.

**Ranking definition (frozen, per-position):** At each L2 position `j` with conditioning
`(u1_cond_j, b_j)` from the operational (hard-`u1`) path, sort the 32 `u2` symbols by arm-table
mass `p2[u1_cond_j, b_j, :]` descending, ties toward the smallest symbol index (the `sc.py`
argmax convention). `r_j` = 1-based rank of the true `u2_j`. **Survival:** `survives_j(L)` iff
`r_j ≤ L`, for `L ∈ {4, 8}`. **Survival fraction** = mean of `survives_j(L)` over spike
positions in a block, reported per-seed then pooled across seeds as mean / sample-std(n−1) /
range — stratified by excess-depth bin × L. Q1b repeats this with `p1[·,b_j]` columns and true
`u1_j`.

**Local-spike detector (Q2, frozen F-median8):** `d_j = h_j − median(h over the R=8 clipped
natural neighborhood of j)` (the `FROZEN_HAZARD_R=8` recipe with median; user decision
2026-09-20, P20S §3 verbatim). Detector selection = top-K2_synth positions by `d_j`; baseline
selection = top-K2_synth by global `h_j` (the H2a-REFUTED mean-hazard logic). **Coverage** =
fraction of greedy-SC operational mismatch positions contained in each selection, reported
descriptively per-seed + pooled. Mismatches come from the accepted greedy `sc_decode` (L=1) run
once per block against synthetic truth — the sole decoder use, recording-only.

`u1_cond` = argmax-p1 hard-u1 (X14's within-freeze reading kept for comparability; reviewer note
carried).

## 3. Structure sanity gates (checked before the main question)

Gates are wiring/structure checks only, not claim thresholds. Any violation → `X15_STOP_SANITY_*`
+ return, no input repair.

- **G1 (mismatch operating band):** pooled greedy-SC mismatch ratio-of-sums ∈ [0.15, 0.90].
  Rationale: X14 0.969 is the chance ceiling for a near-random channel; lower edge from
  pointwise SER ~0.25 plus the X06 observation that undisclosed blocks always error.
- **G2 (diagonal capture floor):** pooled Q1b non-spike L8 survival ≥ 0.50. Rationale: diagonal
  0.75 ⇒ ≈0.75+ capture expected; 0.50 is a loose wiring floor.
- **G3 (spike-rate band):** pooled spike fraction ∈ [0.05, 0.60]. Reference: X14 747/7168 ≈ 0.104.
- **Calibration scalars (recorded descriptively, no gates):** table f_min/f_max, model H1/H2 bits,
  diagonal mass, pointwise argmax hit rates, model_mean_hazard_bits.

## 4. Channel construction recipe (deterministic per-column, in-body)

Per Bob column `b` (1024 labels), deterministic masses over Alice labels `A`:

- `A = b`: 0.75 (diagonal pin; p_err = 0.25 from recorded raw SER ~0.25; population caveat: rests
  on 1.5M SER, no 2M raw SER found).
- 8 neighbors `(b+k mod 1024, k=1..8)`: share 0.9 × 0.25 = 0.225 → 0.028125 each (C8 concentrated
  noise; FROZEN_20260920_C8_NEIGHBORS_90PCT_ERROR_MASS — recommend option auto-selected under
  standing pre-authorization; transparent engineering choice, zero provenance claim).
- rare15 `(b+37k mod 1024, k=1..96)`: pre-floor 0, preserving the 96/1024 = 9.375% pin.
- Remaining 919: share 0.1 × 0.25 = 0.025 → ≈2.72e-5 each.
- Disjointness proven: 37 coprime to 1024 and the 941k′ mod 1024 values {941, 882, 823, 764, 705,
  646, 587, 528} ∉ 1..96 — body still asserts it; violation → X15_STOP_NONFINITE.

Then X14-identical pipeline: raw-count MLE + 1e-15 floor + column renormalize → `derive_p1` /
`derive_p2` (`A = 32·U1 + U2`, FULL_BOB_ONLY) → `probs_to_symbol_metric`. Static order natural,
prefix first 52 (`K2_synth = 52`).

Consequences: deterministic table ⇒ `rng_calls` = 56 block-sampling only; master 2026092369 is a
reserved label, never a stream; 8 block seeds × 4 blocks = 32 blocks = 8192 L2 positions;
`results.json` scalar-only ~15–20 KB.

Frozen scales: N=256, q=32, alpha=2, GF(32) poly 37, chunk_rows=512, floor 1e-15, p_b uniform.

## 5. Tier compliance adjudication

- Opening `raw_prior_*.npz` = artifact access = crosses the Tier-X line: NOT proposed.
- Reading committed packet docs / recorded scalars is always allowed.
- Parameterizing a fully synthetic in-body model by published scalars (p_err=0.25, 96/1024 pin) is
  Tier-X compliant — same as X14's 9.35% pin. No escalation required.
- Q2 re-run YES: the diagonal concentrates mismatches, restoring variance; same frozen detector,
  so the v1/v2 delta is attributable to channel structure alone.

## 6. Goal / Non-Goals / Impact Scope / Acceptance Criteria / Tasks

- **Goal:** Preregistered, synthetic-only, descriptive survival/coverage evidence under the
  structured diagonal channel (Q1/Q1b/Q2 + §3 sanity gates), maximally comparable to X14 (minimal
  delta: channel structure only).
- **Non-goals (binding):** No FER/reliability/efficiency/branch-superiority verdicts; no
  thresholds, no pass/fail; no SCL implementation or unlock; no protected opens (V25 counts,
  parquet/pairs, 1M/1.5M/2M content); no real-data decoder run; no tag-domain use
  (`toeplitz_tag` never called; `tag_calls: 0`); no α/floor/K/decoder/production-module changes
  (read-only reuse); no (b)/(c) bounded-search or second-construction work; no D1/D2 real-data
  work; no ledger/memory/index updates per-probe (batched at milestones per Tier-X rules).
- **Impact scope:** Three new packet docs (this dir) + three new probe-root files
  (`prereg.md`, `body.py`, `results.json`). No files outside these six are created or modified.
  `formal_ir/nbpolar/` modules are read-only imports. `results/`,
  `comparison_bench/outputs_comparison/`, ledgers, and sibling checkouts are untouched.
- **Acceptance criteria:** (i) three packet docs + frozen 3-line prereg consistent; (ii) fresh
  seeds/tag-absence proven by repo grep at freeze; (iii) focused tests + full NB-Polar suite green
  (T0/T1 at implementation; T2 not required for Tier-X); (iv) single execution under the frozen
  command writes only `results.json` with per-seed values + mean/sample-std/range and zero
  protected opens; (v) sanity gates evaluated before the main question with `X15_STOP_SANITY_*`
  on violation; (vi) focused numerical review recorded; (vii) no claim, threshold, or verdict
  token anywhere in outputs.
- **Tasks (coder, after freeze authorization):**
  1. Freeze: verify seeds 2026092369..2026092377 absent by repo grep; write `prereg.md` (verbatim
     `PREREG_DRAFT.md` content) into the probe root BEFORE any generation; embed the §2/§4
     recipes as the frozen `body.py`; add 3 self-tests: (a) rank-1-peaked + tie-break
     X14-identical; (b) diagonal-smoke — column sums, disjointness, argmax=diagonal, floor-hit
     96/1024; (c) sanity-gate asserts. Verify: grep output clean, tests green, no protected
     imports.
  2. Execute once under the frozen command (`PREREG_DRAFT.md` line 3); on execution-error only,
     one recorded rerun. Verify: exit 0, `results.json` sole write, scalar-only, < 2 MB,
     per-seed + pooled stats present.
  3. Return deltas only: sanity-gate values, survival fractions by bin × L (Q1/Q1b), Q2 coverage
     pairs, measured floor-hit rate vs 9.375% pin, calibration scalars, spike counts per stratum,
     command/wall, blocker-or-none. Obtain focused numerical review. No commit/push; no claims.

## 7. Stop rules

Any protected-path import/open attempt; nonfinite result; missing seed-grep proof at freeze;
`results.json` > 2 MB; body/prereg token mismatch; any sanity-gate violation → `X15_STOP_*` +
return, no input repair (no tuning, no re-pinning, no rerun to change numbers).

## 8. Standing rules inherited

Tier-X: synthetic-only, probe-root-only writes, 3-line prereg, per-seed + mean/std/range, no
thresholds/verdicts, SCL stays locked, no candidate/accepted token, no scientific-status change.
Evidence-size rule (decision record D4, in force): single committed file ≤ ~2 MB — satisfied
(~15–20 KB estimate).
