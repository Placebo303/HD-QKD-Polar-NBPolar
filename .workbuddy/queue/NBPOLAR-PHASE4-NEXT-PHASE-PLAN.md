# NBPOLAR Phase-4 Next-Phase Plan (planning only — no implementation, no execution)

- Status: DRAFT plan for user decision. No freeze, no authorization, no commit/push.
- Authority: planner subagent, 2026-09-20, branch `codex/nbpolar-phase0`.
- Inputs read (no protected opens, no execution):
  `NBPOLAR-PHASE4-P20S-R1-GATE-FIX/MAIN_THREAD_ACCEPTANCE.md` +
  `l2_mechanism_probe_2m/{aggregate_summary.json, per_block_arm_outcomes.jsonl}` (accepted R1 root),
  `NBPOLAR-H2-ADJUDICATION-ANALYSIS/H2_ANALYSIS_PLAN.md` +
  `workspace/h2/504e036a-f040-4d88-88ba-152702f92ffd/h2_final_adjudication.md` (H2 v1),
  `NBPOLAR-X17-METRIC-FEED-AUDIT/FOCUSED_REVIEW_PENDING.md` (X17),
  `NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md` (D1–D4, D1-A executed via P20S).
- Standing verdicts carried in: H2 v1 (H2a REFUTED, H2b SUPPORTED median 2.2835 n=37,
  H2c SUPPORTED 35/37, H2d flat mean 0.002185, H2e REFUTED-geometry-incoherent truncated-scope);
  X17 synthetic SCL line non-informative at this operating point (P positive control 0.000
  rules out feed defect; corrected full-scale C ≈ chance ⇒ sub-threshold point, not wiring).

## Goal

1. Specify H2 v2 (read-only re-adjudication incl. the first full-block evidence) as an
   analysis-only packet ready to freeze.
2. Rank the post-X17 / post-P20S branch options by information gain per cost and name the
   recommended next step.
3. Record the exact consumed/never-decoded ledger state after P20S/R1.

## Non-Goals

- No production-code change, no decoder/RNG/tag execution, no new DEV/HOLD contact, no
  protected opens (pairs parquet, NPZ priors/alts, V25 counts — not even stat), no K/budget/
  order/alt recompute or hand-fill, no new tag domains, no construction/prior/order derivation.
- No FER, efficiency, leakage, key-rate, reliability, recovery-rate, scaling-superiority, or
  promotion claim anywhere in H2 v2 or the geometry archive mining (descriptive only, per D2).
- No verdict token inside any H2 v2 sub-computation; verdicts ONLY in the final adjudication file.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push.
- This document does NOT authorize anything and does NOT modify any OpenSpec spec.

## Impact Scope

- Reads (worktree files only): H2 v1 run root `workspace/h2/504e036a-…/` (15 files),
  P20N/P20O/P20Q/P20R `per_block_arm_outcomes.jsonl` + `aggregate_summary.json` nine-scalar rows,
  P20S/R1 accepted root `l2_mechanism_probe_2m/` (jsonl + summary + `ir5_full_manifest.json` +
  `report.md` + `frozen_plan.json` + `input_and_predecessor_identity.json` as identity pins;
  the 9 IR-5 `.bin` files are joined ONLY via their frozen sha256/size manifest entries and the
  persisted per-record IR scalars — the v2 operator MUST confirm with the main thread whether
  opening the `.bin` series counts as a protected open; default rule below assumes YES and
  restricts v2 to persisted scalars + manifest unless explicitly authorized otherwise, §4).
  X10 `workspace/probes/nbpolar_x10_h2_scalar_adjudication/results.json` as frozen baseline.
- Writes (additive only): ONE new run root `workspace/h2/<uuid>/` (fresh uuid) with the §3 file set.
- Affects: main-thread H2 decision only. Touches no runner, no frozen evidence root, no OpenSpec specs.

---

## 1. H2 v2 analysis plan (read-only join, stdlib, no decoder/protected opens)

### 1.1 Join contract (delta vs H2 v1 plan §2)

- Nine-scalar base: P20N 16 + P20O 20 + P20Q 20 + **P20R 4** (A/B/C/D single block, all non-exact,
  block-dominated per branch-decision §2(i)) + **P20S 3** (A exact / B `verify_failed` L2 / O oracle
  exact) = **63-row compact table** (v1: 56). Stratify by `packet` always (P20S: merged 2M
  VAL 2827..2915 + HOLD 3556..3594, K 334/6746/7080, A-order `b2255449…906` frozen, B-order
  `139f34c3…1864` spike-local, alt `98e25495…5fb5` — same K/order/alt family as P20O/P20Q, so
  P20S stratifies WITH the 2M session for descriptive concatenation, never pooled for K/budget/
  order claims; P20N stays separate — no u-domain column, different K/order/alt).
- Arms: A/B operational (paired within packet); C/D oracle (P20N/O/Q/R, diagnostic only);
  **O oracle (P20S, `deployable: false`) diagnostic only, never merged into operational aggregates.**
  `undetected` re-isolated (= 0 everywhere); `exact` = outcome exact AND tag_pass AND label_match.
- IR join: P20Q truncated IR (20 rows: IR-1 hist, IR-2 12 L2-fail ranks, IR-3, IR-4 top-16,
  IR-5 first-4096 `truncated=true`) + **P20S uncapped IR (3 rows: IR-1 masses 6746/26022 all arms;
  IR-2 B rank 0.4322; IR-3 A/O 1641 vs B 1651; IR-4 top-16 in-prefix 0/0/0; IR-5 full-block
  `ir5full-v1`, `total_len=32768`, `uncapped=true`, 3 arms × 3 bins)**. Scope labels are load-bearing:
  every H2e quantity carries `truncated` (P20Q) vs `full-block` (P20S) scope; cross-scope pooling
  FORBIDDEN (stratified report only).
- Frozen P20S quantities now available (literals from the accepted R1 root, never recomputed):
  A pm 0.8740592319509212 exact; B pm 0.8768295338061611, `verify_failed`, first-error L2 @ coord 0,
  fail hazard 0.5131718176531462 bits ⇒ **r_fail ≈ 0.5853**, nbhd mean 0.6992590731236983 bits,
  IR-2 rank pct **0.432220458984375** (MID-rank; cf. P20Q A 0.99966 / B 0.32919 extremes),
  `l2_fail_in_prefix=false` AND `l2_fail_in_prefix_u_domain=false` (fail site OUTSIDE disclosed
  prefix under both flags), floor rate B **0.371734619140625** vs A/O 0.0002593994140625,
  prefix floors 0.0 both, A△B **1599/1599 size-delta 0**, IR-1 6746/26022 all arms,
  IR-4 in-prefix **0/48 pooled** (0 on A, B, O), A≡O hazard/inprefix/inu series byte-identical
  (sha `ef4398d3…`, `9e9f5e98…`, `c3502047…`), B hazard series identical to A (`ef4398d3…`) with
  differing prefix/U masks (`cf75440d…`, `bf4e871b…`) — i.e. hazard values are order-independent
  under frozen α1, only the disclosed-position masks differ.

### 1.2 Per-H2: what is now available, decidable, and the verdict delta

- **H2a (pm orders arms).** New: +1 evaluable block (P20S: exact_max 0.87406 < fail_min 0.87683 ⇒
  gap < 0 ⇒ NOT anomalous; P20R block contributes 0 evaluable — no exact arm, block-dominated).
  Now decidable: yes — n_evaluable 8→9, n_anomaly stays 8. Prior REFUTED **STANDS (reinforced as a
  verdict: rule `n_anomaly ≥ 1` still fires 8/9)** with the that the newest block
  itself is ordering-consistent; record as consistency datum, no threshold change, no re-adjudication
  of the rule.
- **H2b (fail-site elevation).** New: +1 ratio r_fail ≈ 0.5853 (< 1.10, below-1 point; v1 range
  0.4713..10.3421 already contains below-1 values) ⇒ n 37→38, median barely moves, stays ≫ 1.10;
  +1 IR-2 rank 0.4322 (MID-rank vs P20Q median 0.883 high-tail). Now decidable: yes. Prior
  SUPPORTED **REINFORCED** (median test unaffected); carry the IR-2 mid-vs-tail tension as an
  explicit corroboration note (no vote-flip, per frozen rule).
- **H2c (prefix concentration + U split).** New: the "fail site OUTSIDE disclosed prefix" datum —
  P20S B is the 3rd out-of-X L2 fail archive-wide (frac_inX 35/37 → **35/38 ≈ 0.921**), the first on
  a spike-local order arm, at boundary coord 0, out under BOTH domain flags; the out-of-U-given-in-X
  conditional is unchanged (23/23 — the new fail is not in-X, excluded by conditioning).
  Now decidable: yes. Prior SUPPORTED **STANDS (rule `frac_inX ≥ 0.50` still fires)**; the new datum
  sharpens the mechanism question (disclosed-prefix misses can still fail at coord 0) without moving
  the threshold verdict.
- **H2d (floor flatness).** New: +1 pair (fail_nbhd_floor 0.0 vs prefix_floor 0.0 ⇒ d = 0).
  Now decidable: yes. Prior SUPPORTED-flat **REINFORCED** (n 37→38, mean stays ≪ 0.05).
- **H2e (static-order geometry).** New: re-askable at FULL-BLOCK scope for one block — uncapped
  IR-5 (32768) + full masks + IR-4/IR-2/IR-1/IR-3 payloads. Sharpest new contrast: **IR-4 top-16
  in-prefix 0/48 on ALL arms (pooled frac 0.0) vs IR-2 mid-rank 0.4322** — i.e. the v1 incoherence
  (top-k mass outside-prefix 0.206 vs fail-site high-rank 0.883) reproduces in stronger form at full
  scope: the fail site is mid-rank while the entire top-16 sits outside-prefix. Now decidable: yes,
  at full-block scope for n=1 (descriptive; no full-block ORDER claim beyond the persisted series,
  no FER). Prior verdict (REFUTED-geometry-incoherent, explicitly truncated-scope) **NEEDS
  RE-ADJUDICATION for the new scope**: the truncated-scope verdict STANDS AS-IS (its inputs are
  unchanged), but the full-block question is new — preregister the v2 H2e rule BEFORE running
  (recommended: same AND-conjunction shape — full-block top-16 in-prefix frac ≥ 0.50 AND IR-2
  median over L2-fails ≥ 0.50 — applied stratified: P20Q-truncated and P20S-full-block reported
  separately, verdict per scope; v1 thresholds for H2a–H2d reused verbatim).

### 1.3 Output root + file set (same as H2 v1, §5 of the v1 plan)

`workspace/h2/<uuid>/` (fresh uuid, additive only): `h2_input_inventory.json` (now 10+ inputs:
v1's 8 + P20R jsonl/sum + P20S R1 jsonl/sum/manifest/report/frozen-plan/identity pins);
`h2_record_table.json` (63 rows, scope-labelled, no verdicts); `h2a_table.json/.md`,
`h2b_table.json/.md`, `h2c_table.json/.md`, `h2d_table.json/.md`, `h2e_table.json/.md`
(descriptives only); `h2_final_adjudication.md` + `h2_summary.json` (ONLY verdict-bearing files);
`run_manifest.json` (decoder/RNG/tag/protected-open counters 0, wall/RSS). Markdown tables only,
JSON indent=1 + trailing newline (X10 convention).

### 1.4 Stop rules (inherit v1 plan §6, plus)

STOP with `H2V2_STOP_<REASON>`, no adjudication, when: any v1 §6 condition fires (counts P20N 16 /
P20O 20 / P20Q 20 / P20R 4 / P20S 3; P20Q IR caps; `prefix+outside = 32768` every IR-1 row;
IR-4 = 16; P20Q IR-5 `truncated=true` AND P20S IR-5 `uncapped=true, total_len=32768`;
`undetected = 0`; oracle isolation); any verdict token outside the two adjudication files;
any `.bin` content open without explicit main-thread authorization (§4 gate); any K/budget
recompute. Execution-error rerun: 1 max, recorded (identical inputs, never tuning). Independent
read-only recheck (separate thread) per v1 A4 before any solidification; FAIL blocks it.

---

## 2. Post-X17 branch plan (ranked by information gain per cost)

Context pins: synthetic SCL line CLOSED as non-informative at this operating point (X17:
feed-defect ruled out by P=0.000 positive control; remediated full-scale still ≈ chance ⇒
sub-threshold point — this WEAKENS branch-decision D3's synthetic-unlock path as scoped: D3's
step-2 question can no longer be answered at the current point); real-data N=32768 population
under the old rule is EXHAUSTED (§3: 0 full blocks); 1.5M remainder is low-information
(oracle ceiling ~12.5% vs 2M ~70%).

| rank | option | info gain | cost / gate class |
|---|---|---|---|
| **1 (recommended next)** | **(iii) Analysis-only: H2 v2 (§1) + full-block geometry-archive mining** (rank curves, prefix/outside hazard distributions, spike localization, A/B/O series diff — all from persisted evidence, stdlib only) | High-per-cost: last extractable value from the consumed merged block; decides H2e at full scope; scopes any future order rule | **Cost ~0. Gate: standing pre-authorization (analysis-only)** — freeze packet + Tier-X-style prereg, no new authorization beyond normal packet freeze |
| 2 | **(iv) Reduced-N probe on the 2M tail: ONE N=8192 block from HOLD 3595..3644 (50 frames → 1 block + 18-frame stub)** with frozen α1 re-derived at N=8192 + spike-local order; 1.5M stubs (41+42) usable at N=8192 only as low-information controls, never pooled | Medium: tests whether the mechanism (L2-spike failure, H2e geometry) persists off the N=32768 point; stays in the high-information 2M session | **Cost medium. Gate: NEW — P16-scale OpenSpec change (new construction/order/K at N=8192, cross-N incomparability disclaimer) + fresh freeze + explicit user authorization** (touches real data + production code paths) |
| 3 | **(i) Full operating-point change at N=32768** (N reduction / K reallocation / disclosure placement move, per NEXT-BRANCH-DECISION D1-B note) | Potentially high, but speculative: abandons the only point with characterized geometry; cross-point comparisons invalid | **Cost high. Gate: NEW top-level OpenSpec change (explicitly NOT a packet)** + freeze + explicit authorization |
| 4 | **(ii) New data acquisition** | High (fresh 2M-session frames reopen the N=32768 ladder) | **Out of our control** — no gate we can pass; record as dependency, do not plan around |
| 5 (fallback) | **(v) Closeout**: archive H2 v2 + geometry notes, write N=32768 closeout, freeze further real-data execution | Zero new info; preserves honesty of the record | **Gate: user decision only** — take iff (iv)/(i) are declined |

Recommendation: freeze and run **(iii)** now under standing pre-authorization; present **(iv)** vs
**(i)** vs **(v)** as the ONE user decision (§4). Do NOT pursue further synthetic-SCL work at the
current operating point without (i)-class rescoping (X17 closed that point).

### Inventory note for (iv) — no still-usable N=32768 population exists

Checked the 4-segment ledger (§3): the only same-session combinable remainder is the 2M HOLD tail
(50 frames < 128); 1.5M↔2M mixing is forbidden (session-difficulty asymmetry + D-decision);
1.5M stubs are low-information. "Never-decoded tails" = exactly the three §3 rows; none yields an
N=32768 block under any authorized rule. The only real-data path without new acquisition is a
reduced-N OpenSpec change (iv), which is why (iii) comes first.

---

## 3. Ledger update statement (exact state after P20S/R1 acceptance)

- CONSUMED by P20S/R1 (merged DEV, spent regardless of outcome): **2M VAL 2827..2915 (89 frames)**
  + **2M HOLD 3556..3594 (39 frames)** = 128 frames = 1 × N=32768 block. Attempt accounting: P20S
  block consumed, R1 attempt spent; both roots retained immutable (P20S BLOCKED-label provenance,
  R1 accepted-descriptive).
- NEVER-DECODED (unchanged tails, counted, no contact beyond counting): **1.5M VAL stub 2172..2212
  (41 frames / 10,496 pairs)**; **1.5M HOLD 2725..2766 (42 frames / 10,752 pairs)**;
  **2M HOLD tail 3595..3644 (50 frames / 12,800 symbols)**. Total **133 frames / 34,048 pairs**.
- DERIVED: **0 full N=32768 blocks** remain under the old rule (128 contiguous / same split /
  same session); largest same-session contiguous remainder = 50 (2M HOLD tail) ⇒ 0 blocks;
  2M-internal combinable remainder = 0 further blocks. Previously consumed reference: P20N 1.5M
  HOLD 2213..2724; P20O 2M VAL 2187..2826; P20Q 2M HOLD 2916..3555; P20R 1.5M VAL 2044..2171.
- Forward rule: no further real-data decode executes without a new freeze + explicit authorization;
  any use of the §3 never-decoded tails at reduced N requires the (iv) OpenSpec change first.

---

## 4. Authorization map + stop rules for the next phase

- **Fits standing pre-authorization (analysis-only):** H2 v2 exactly as §1 (read-only join, stdlib,
  zero decoder/RNG/tag calls, zero protected opens — DEFAULT RULE: the 9 IR-5 `.bin` files are
  manifest/sha-only inputs; any byte-content open needs explicit main-thread ruling first),
  writes confined to `workspace/h2/<uuid>/` + this plan file. Geometry-archive mining under the
  same counters. Batch ledger/memory updates at the milestone (AGENTS.md §10.4).
- **Requires new freeze + SEPARATE explicit user authorization:** anything touching real data
  (incl. the (iv) N=8192 tail probe), any production-code edit (construction/order/K/decoder),
  any top-level OpenSpec change ((i) operating-point redesign, (iv) reduced-N construction),
  any new DEV/HOLD contact, any protected open beyond §1, any claim-bearing (Tier-Y) execution.
- **Stop rules:** any §1.4 condition; any scope creep from (iii) into real-data execution;
  any verdict/H2-threshold edit smuggled into analysis files (threshold changes = new plan +
  re-freeze); any commit/push by the operator (batched separately by the main thread).

## Tasks (for coder-operators; each verifiable, no production code)

1. T1 — Freeze the H2 v2 packet (inputs §1.1 + thresholds §1.2/H2e-v2-rule + outputs §1.3 + stops
   §1.4) as `TASK_PACKET.md` + `AUTHORIZATION_PROMPT.md` + `STATUS.yaml`; main-thread freeze review.
   *Verify: packet names all 10+ inputs with digests; H2e v2 rule written before any computation.*
2. T2 — Run the §1 join + tables (stdlib only, counters zero) into `workspace/h2/<uuid>/`.
   *Verify: 63-row table; counts 16/20/20/4/3; scope labels on every H2e quantity; no verdict token
   outside the two adjudication files.*
3. T3 — Independent read-only recheck (separate thread) per v1 A4 + §1.4; FAIL blocks solidification.
4. T4 — Geometry-archive mining note (descriptive): full-block rank curves, prefix/outside shapes,
   spike-localization read of the P20S series + masks (manifest/sha-pinned; `.bin` bytes only if
   the §4 ruling allows). *Verify: no recovery-rate reading, no H2 verdict in the note.*
5. T5 — Present the ONE user decision: (iv) N=8192 2M-tail OpenSpec change vs (i) full redesign vs
   (v) closeout. *Verify: decision recorded in `docs/decision-log.md`; no execution starts from T5.*
