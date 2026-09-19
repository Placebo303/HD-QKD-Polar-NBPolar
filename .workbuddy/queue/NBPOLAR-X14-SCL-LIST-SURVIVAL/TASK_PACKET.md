# TASK_PACKET.md — NBPOLAR-X14-SCL-LIST-SURVIVAL (frozen Tier-X probe, proposal only)

Probe: `NBPOLAR-X14-SCL-LIST-SURVIVAL` | Tier: X (non-claim, synthetic-only, decoder-free)
Workdir: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` | Branch: `codex/nbpolar-phase0`
Authorizing record: `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md` §4 D3 (proposal only —
NO implementation, NO execution, NO protected opens, NO decoder beyond the frozen greedy-SC
mismatch oracle in Q2, NO list decoder).
Cost class: zero-cost synthetic diagnostic. Consumes NO counts/DEV/HOLD/VAL reads and NO attempt.
Status: PROPOSAL — awaiting main-thread approval + the single X11-label decision (§9).
RESOLVED 2026-09-20 (main thread): renamed X11→X14 to avoid prefix collision (`nbpolar_x11_hybrid_fwht_endtoend`, x12, x13 occupied); proposal APPROVED; execution gated on fresh-seed re-grep + Q2 formula alignment + coder freeze.

## 0. Read-only inventory (verified by grep/read, no execution)

| Path | What it provides | Status |
|---|---|---|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/synthetic.py` | q-ary erasure/QSC generators + `analytic_erasure_probs`; explicit-`Generator` contract; frozen stream seeds 2026091200..1203 | Present; reuse read-only (contract reference only — X11 uses `empirical_channel`, not these generators) |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_channel.py` | Model-sampled source: `sample_full_block`, `build_p1_metrics`, `P3_UNIT/TRAIN/DIAG_SEED` (2026091314..1316), `BANNED_SEEDS` 2026091200..1213, truth-isolation signature | Present; reuse read-only: `sample_full_block` + `build_p1_metrics` recipes |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py` | Reference greedy q-ary SC (`sc_decode`), log-domain minus/plus, `chunk_rows=512` default, argmax-ties-to-smallest-index; docstring states "no list decoding" | Present; reuse read-only: Q2 mismatch oracle only (`sc_decode` as-is, L=1 greedy) |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py` | `derive_p1` → `[U1,B]` (32,1024); `derive_p2` → `[U1,B,U2]` (32,1024,32), zero-mass slices → uniform 1/32; `build_p1_metrics` / `gather_p2_metrics`; `probs_to_symbol_metric` (exact-zero → `-inf`, logsumexp-0) | Present; reuse read-only: full metric recipe chain |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py:1321` | `_hazard_bits`: `-log2` arm-table mass at `(U1_cond,B,U2)` cells (frozen ranking/hazard atom) | Present; recipe frozen — X11 reuses the formula, never edits |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py:1331` | `_l2_hazard_diagnostics`: 8 frozen scalars, `FROZEN_HAZARD_R=8` window, `l2_prefix_hazard_mean_bits`, fail/nbhd/prefix floor fracs, X-domain natural-index semantics (X09-R1 D4) | Present; recipe frozen — X11 reuses R=8 + prefix-mean + floor-frac definitions |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py:333` | `frozen_arm_table()`: A/B/C/D arms, K1=331/K2=6689/K_total=7020, `5K+64` leakage arithmetic | Present; structural reference for Q1 disclosure-ratio scaling only |
| SCL-lock record | `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` §"SCL entry gate" (5 conditions); `docs/nbpolar/CRITICAL_PATH.md` step 6; `sc.py` "no list decoding"; per-packet "SCL entry gate UNCHANGED" lines; `AGENT_PROJECT_MEMORY.md` "SCL still locked" | Present; X11 changes none of them (coverability evidence only) |
| 9.35% heavy-tail record | `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation/per_block_arm_outcomes.jsonl` block-0 B0: `raw_zero_count_hits=3063`, `floor_hits_1e15=3063`, `floor_hit_log_loss_bits=21624.798748072426`; `3063/32768 = 0.093475… ≈ 9.35%`; `.codebuddy/memory/2026-09-19.md:32` corroborates | Exact recorded value 3063/32768 (block 0; blocks 1–2 read 2854/2851 — X11 reproduces the block-0 9.3475% figure; see §2) |
| X08/X09/X10 probe pattern | `workspace/probes/<id>/{prereg.md,body.py,results.json}` (X08, X09, X09-r1, X10-h2; X11-fwht has prereg+results only); frozen command `timeout 120 … body.py` with single-thread env pins; `results.json` carries probe_id/tier/status/question/command, `decoder_calls/rng_calls/tag_calls`, writes, notes | Present; X11 follows it with the 3-line-prereg Tier-X variant (§5) |
| H2 verdicts (frozen input, not re-argued) | Decision record §1 + `workspace/h2/504e036a-…/h2_final_adjudication.md`: H2a REFUTED (8/14 anomalous), H2b SUPPORTED (median r_fail 2.2835), H2c SUPPORTED (in-X 35/37), H2d flat, H2e REFUTED-geometry-incoherent (IR-4 pooled 66/320 = 0.20625); H2a ⇒ order criterion must be local-spike, never mean-hazard | Present; constrains Q2 detector choice |
| Fresh seeds | Repo grep for `2026092350`, `2026092351..2026092357`, `nbpolar_x11_scl`, `X11-SCL` → sole hit is the decision-log adoption line (L4872); used tag/test range ends at 2026092347 (P20R) | Fresh; operator re-verifies by grep at freeze (§7) |
| Missing / not needed | No SCL module exists under `formal_ir/nbpolar/` (only `sc.py`) — expected; X11 must NOT create one | — |

## 1. Questions

**Q1 (primary):** With the frozen empirical channel structure reproduced synthetically (including
the 9.35% zero-count heavy tail), does the TRUE path survive in an L=4 / L=8 candidate list at
L2 spike positions — i.e., is the true `(b, u1, u2)` cell within the top-L ranked candidates
under the frozen arm-table/prior likelihood? This tests the SCL-unlock gate condition 3
("a small preregistered list contains the needed candidate often enough to matter") WITHOUT
implementing SCL: ranking-only coverability analysis; SCL stays locked whatever the numbers say.
Coverability scope: per-position top-L survival is a necessary-condition proxy for list decoding; it does not by itself prove SCL path survival — reported as coverability evidence only.

**Q1b (secondary, same machinery):** The symmetric L1 rank — is the true `u1` within the top-L
of the `p1[·,b]` column ranking? Directly relevant to gate condition 3 for an L1 list.

**Q2 (secondary):** Validate the D2 local-spike order-derivation criterion on synthetic: does a
local-spike detector select the positions where greedy-SC mismatches actually occur better than
mean-hazard (global top-K hazard) ranking — the H2a-REFUTED baseline? Coverage fractions only,
descriptive.

## 2. Frozen definitions

**Hazard atom (frozen recipe, `l2_alt_hold_1p5m.py:1321`):**
`h_j = -log2 p2[u1_cond_j, b_j, u2_true_j]`, natural log avoided — bits, base 2, exact-zero mass
raises (never replaced by uniform; synthetic construction guarantees positive arm-table mass,
§3).

**Spike definition (frozen quantities only):** Let `pm = mean(h_j)` over the disclosed prefix
(the `l2_prefix_hazard_mean_bits` recipe). Position `j` is a **spike** iff excess
`e_j = h_j − pm ≥ 2.0` bits. **Strata** by excess depth: `[2,4)`, `[4,8)`, `[8,∞)` bits, plus a
non-spike reference stratum (`e_j < 2.0`). Margin and bins are descriptive recording buckets,
never thresholds or verdicts.

**Ranking definition (frozen, per-position):** At each L2 position `j` with conditioning
`(u1_cond_j, b_j)` from the operational (hard-`u1`) path, sort the 32 `u2` symbols by arm-table
mass `p2[u1_cond_j, b_j, :]` descending, ties toward the smallest symbol index (the `sc.py`
argmax convention). `r_j` = 1-based rank of the true `u2_j`. **Survival:** `survives_j(L)` iff
`r_j ≤ L`, for `L ∈ {4, 8}`. **Survival fraction** = mean of `survives_j(L)` over spike
positions in a block, reported per-seed then pooled across seeds as mean / sample-std / range —
stratified by excess-depth bin × L. Q1b repeats this with `p1[·,b_j]` columns and true `u1_j`.

**Local-spike detector (Q2, frozen F-median8):** `d_j = h_j − median(h over the R=8 clipped natural
neighborhood of j)` (the `FROZEN_HAZARD_R=8` recipe with median; user decision 2026-09-20, P20S §3
verbatim). Detector selection = top-K2_synth positions
by `d_j`; baseline selection = top-K2_synth by global `h_j` (the H2a-REFUTED mean-hazard logic).
**Coverage** = fraction of greedy-SC operational mismatch positions contained in each selection,
reported descriptively per-seed + pooled. Mismatches come from the accepted greedy `sc_decode`
(L=1) run once per block against synthetic truth — the sole decoder use, recording-only.
ALIGNED 2026-09-20: frozen F-median8 (user decision; P20S §3 verbatim).

## 3. Frozen synthetic channel (in-body, no protected data)

- `q_high=32`, `n_b=1024` Bob labels, `p_b` uniform (preregistered; no estimation, no tuning).
- Joint `f_full[A,B]` (1024×1024): per column, `s=96` deterministically chosen rare Alice symbols
  (function of column index only, no RNG) carry pre-floor mass 0; the remaining 928 symbols share
  mass via one symmetric Dirichlet(α=1.0) draw at the table master seed, column-renormalized.
  Then the accepted P20M pipeline verbatim: raw-count MLE + `1e-15` floor + column renormalize →
  `derive_p1` / `derive_p2` (`A = 32·U1 + U2`, FULL_BOB_ONLY) → `probs_to_symbol_metric`.
- Heavy-tail pin: `96/1024 = 0.09375 ≈ 9.375%` expected DEV floor-hit rate vs the recorded
  `3063/32768 = 9.3475%` — 0.03 pp apart by construction; the body records the *measured*
  hit rate descriptively (no post-hoc adjustment, no rerun to change it).
- Static disclosure order (H2e-theme, no DEV tuning): rank L2 positions once per table by
  table-marginal expected hazard `E[h]`; prefix length `K2_synth = 52` (frozen ratio
  `6689/32768 × 256 = 52.2`, floored). Survival strata are order-free; the prefix supplies only
  `pm` and the Q2 `K`.
- Scale: `N=256`, `alpha=2`, GF(32) polynomial 37, `chunk_rows=512` (accepted default), floor
  `1e-15`. 7 block seeds × 4 blocks = 28 blocks = 7168 L2 positions; runtime is seconds.

## 4. Implementation scope for the coder operator

**New files only** (follow the X08/X09/X10 pattern; zero production-module edits):

- `workspace/probes/nbpolar_x14_scl_list_survival/prereg.md` — the frozen 3-line prereg
  (verbatim `PREREG_DRAFT.md` content), written BEFORE any synthetic generation.
- `workspace/probes/nbpolar_x14_scl_list_survival/body.py` — single self-contained probe script
  (stdlib + numpy only). Read-only imports allowed: `empirical_channel` (sampling recipes),
  `prior` (`derive_p1/derive_p2/probs_to_symbol_metric`), `algebra.make_gf32`,
  `transform.polar_transform`, `sc.sc_decode` (Q2 mismatch oracle only). Must NOT import or
  create any list decoder; must NOT open any protected artifact (assert by path refusal:
  `pairs_loader`, V25 counts, parquet, 1M/1.5M/2M content are never imported/touched).
  Embeds: §3 channel recipe, §2 hazard/spike/rank/detector definitions, 2 injected self-tests
  (rank-1-of-uniform sanity: true cell top-ranked under a peaked row; floor-hit-rate smoke at
  master seed recorded, never gated), per-seed computation, `results.json` writer.
- `workspace/probes/nbpolar_x14_scl_list_survival/results.json` — the ONLY file `body.py`
  writes (indent=1): `probe_id`, `tier: "X"`, status
  `"X14_PROBE_COMPLETE_DESCRIPTIVE_ONLY"`, question, per-seed survival tables (Q1/Q1b, by
  bin × L) + pooled mean/sample-std/range, Q2 coverage pairs, measured floor-hit rate,
  spike-position counts per stratum, command, interpreter, `decoder_calls` (Q2 SC count),
  `rng_calls`, `tag_calls: 0`, `protected_opens_attempted: false`, writes, notes.
  Scalar-only; expected size < 100 KB (evidence-size rule §8 satisfied by construction).

**Frozen command** (§5, line 3 of prereg): single-thread env pins + `timeout 300 … body.py`.
**Stop rules:** any protected-path import/open attempt, nonfinite result, missing fresh-seed
grep proof at freeze, `results.json` > 2 MB, body/prereg content mismatch → STOP with a
specific `X14_STOP_<REASON>` status, return, no repair by editing inputs.
**Focused review:** independent reviewer-go focused numerical review of the return (commands,
completeness, arithmetic, truth isolation, write scope) — Tier-X rule, no Pre-EXECUTE/Pre-RESULT.

## 5. Non-goals (binding; cf. decision record §5)

No FER/reliability/efficiency/branch-superiority verdicts; no thresholds, no pass/fail; no SCL
implementation or unlock (the probe reports coverability evidence only); no protected opens
(V25 counts, parquet/pairs, 1M/1.5M/2M content); no real-data decoder run; no tag-domain use
(`toeplitz_tag` never called; seeds 2026092350..2026092357 fresh, grep-verified); no tag domains
beyond these; no α/floor/K/decoder/production-module changes (read-only reuse); no (b)/(c)
bounded-search or second-construction work; no D1/D2 real-data work; no ledger/memory/index
updates per-probe (batched at milestones per Tier-X rules).

## 6. Goal / Non-Goals / Impact Scope / Acceptance Criteria

- **Goal:** Produce preregistered, synthetic-only, descriptive evidence on whether the true
  `(b,u1,u2)` cell survives top-4/top-8 per-position likelihood ranking at frozen-hazard spike
  positions (stratified by spike depth), plus a Q2 local-spike vs mean-hazard coverage
  comparison — the exact evidence D3 needs to unlock-or-refute the SCL route without touching
  protected data or implementing SCL.
- **Non-Goals:** §5 above (binding).
- **Impact Scope:** Three new packet docs (this dir) + three new probe-root files (§4). No
  files outside these six are created or modified. `formal_ir/nbpolar/` modules are read-only
  imports. `results/`, `comparison_bench/outputs_comparison/`, ledgers, and sibling checkouts
  are untouched.
- **Acceptance Criteria:** (i) three packet docs + frozen 3-line prereg consistent; (ii) fresh
  seeds/tag-absence proven by repo grep at freeze; (iii) focused tests + full NB-Polar suite
  green (T0/T1 at implementation; T2 not required for Tier-X); (iv) single execution under the
  frozen command writes only `results.json` with per-seed values + mean/sample-std/range and
  zero protected opens; (v) focused numerical review recorded; (vi) no claim, threshold, or
  verdict token anywhere in outputs.

## 7. Tasks (ordered, for coder agents after authorization)

1. Freeze: verify seeds 2026092350..2026092357 absent by repo grep; write `prereg.md` (verbatim
   draft) into the probe root; embed the §2–§3 recipes as the frozen `body.py`; add the 2
   injected self-tests (T0/T1). Verify: grep output clean, tests green, no protected imports.
2. Execute once under the frozen command (§5); on execution-error only, one recorded rerun.
   Verify: exit 0, `results.json` sole write, scalar-only, < 2 MB, per-seed + pooled stats present.
3. Return deltas only: survival fractions by bin × L (Q1/Q1b), Q2 coverage pairs, measured
   floor-hit rate vs 9.375% pin, spike counts per stratum, command/wall, blocker-or-none.
   Obtain focused numerical review. No commit/push; no claims.

## 8. Standing rules inherited

Evidence-size rule (decision record D4, in force): single committed file ≤ ~2 MB — satisfied
(§4 size estimate). Tier-X rules: synthetic-only, probe-root-only writes, 3-line prereg,
per-seed + mean/sample-std/range, no claim thresholds, no pass/fail, no candidate/accepted
token, no scientific-status change.

## 9. Label note (single decision needed, not a blocker)

`workspace/probes/nbpolar_x11_hybrid_fwht_endtoend/` already occupies the `x11` prefix
(prereg.md + results.json, no body.py). The new root `nbpolar_x14_scl_list_survival/` and packet
dir `NBPOLAR-X14-SCL-LIST-SURVIVAL` are fully distinct names — no overwrite is possible — but
the "X11" label is reused because the decision record D3 names this probe X11. **ONE decision
needed from the main thread at approval:** keep the D3-mandated X11 label (recommended — record
fidelity; distinct full IDs prevent any collision) or rename to the next free X number.

RESOLVED 2026-09-20 (main thread): renamed X11→X14 to avoid prefix collision (`nbpolar_x11_hybrid_fwht_endtoend`, x12, x13 occupied); proposal APPROVED; execution gated on fresh-seed re-grep + Q2 formula alignment + coder freeze.
