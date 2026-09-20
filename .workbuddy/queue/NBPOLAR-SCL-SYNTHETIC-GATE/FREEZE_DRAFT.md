# FREEZE_DRAFT.md — NBPOLAR-SCL-SYNTHETIC-GATE (G1/S2 prerequisite, DRAFT ONLY)

- State: `DRAFT_NOT_FROZEN_NOT_AUTHORIZED` — content plan for the G1 freeze
  review (S2 prerequisite). This draft freezes nothing, authorizes nothing,
  implements nothing, executes nothing.
- No-contact statement: NO implementation, NO execution, NO protected opens
  (V25 counts, parquet/pairs, 1M/1.5M/2M content, `raw_prior_*.npz`), NO decoder
  runs, NO data contact. Every number below is read from already-committed
  records (proposal/design/tasks, STATUS/SCOPING_NOTES, survey §§4–7, X14–X17
  packets + FOCUSED_REVIEWs, decision-log 2026-09-20 entries, frozen `sc.py`
  signature/docstring). Read-only inventory only.
- Reviewer-go verdict answered here: `NEEDS-REVISION` docs-only + 3 risks —
  (R1) parametric working point, (R2) under-specified list interface,
  (R3) seed hygiene. Each section below carries its risk tag.
- Conventions: PROPOSED = candidate value for G1 to confirm/amend/reject;
  FROZEN = already-frozen recipe carried verbatim (cited); UNFROZEN = slot
  shape frozen, values/mechanism explicitly left open for G2+.

---

## 1. Frozen triple proposal (R1) — (N, K1/K2, channel-strength)

**PROPOSED working-point triple (single candidate, minimal-delta axis):**

| Axis | Proposed value | Proven-pointless values it differs from |
|---|---|---|
| N | **16384** (14 polarization levels) | X14/X15 N=256; X16/X17-C N=32768; X17 small-N arms N=256 |
| Disclosure | **K1=167** (first-natural L1, true-u1 conditioning) + **K2=3373** (first-natural L2 forced-correct) | X14/X15 undisclosed (K used for pm/K only, zero `known_positions`); X16/X17-C K1=334/K2=6746; X17-A2 N=256 K1=3/K2=53 |
| Channel strength | **diagonal pin d=0.90**, X15-recipe shape verbatim (8-neighbor share 0.9×(1−d)=0.09 → 0.01125 each; rare96 pre-floor 0 kept; rest share 0.1×(1−d)=0.01 → ≈1.0881e-5 each) | X14 flat Dirichlet; X15/X16/X17-C d=0.75; X17-P d=0.999 control |

Why this triple (each axis moved for a recorded reason):

1. **Scale N=16384** — exact halving of the 2M literals with zero rounding:
   334/32768×16384 = 167 exact; 6746/32768×16384 = 3373 exact
   (K1/N ≈ 1.019%, K2/N ≈ 20.587%, identical ratios to 2M). Rejected N=4096/8192
   per the X16 argument (K1 rounds: 41.75 / 83.5). Cost ≈ ½ of X16 per SC
   (P20S anchor ≈ 7.0 s/SC at N=32768 → est. ~3 s/SC here; 8 SC ≈ 25 s +
   overhead inside `timeout 600`). Memory: top-level `_minus_block` transient
   (8192,32,32) float64 ≈ 64 MiB + `decision_metrics` (16384,32) ≈ 4 MiB —
   inside the 2 GiB P20S envelope. Estimates only, no new risk class.
2. **Disclosure first-natural, exact-ratio** — caller-side truth injection only
   (D1/D2 semantics of X16 §2 carried verbatim at the new K); placement stays
   first-natural for 2M comparability. Hazard-ranked placement is deferred: X17
   A4randomK 0.75293 vs A4rev 0.75879/0.95690 reads random-K≈first-K
   (qualitative, review non-blocking note) — no recorded signal justifies
   spending the freeze on placement.
3. **Strength d=0.90** — the single parametric step (R1): recipe-identical shape,
   error mass 0.25→0.10, moving toward the X17 P-control regime (d=0.999,
   P=0.000 exact 4/4, which provably decodes) while staying far from
   near-noiseless (10% symbol error is well above any decode floor). The X14→X15
   record (sharpening to d=0.75 moved mismatch ≈0.0002) shows strength alone at
   small-N undisclosed points moves nothing — hence strength moves TOGETHER
   with scale+disclosure, never alone.

**Ceiling-margin arithmetic (RECORDED scalars only, no artifact reads):**

- Applicable no-information ceiling at the proposed triple (disclosed):
  (1 − K2/N) × 31/32 = (1 − 3373/16384) × 0.96875
  = (13011/16384) × 0.96875 = 0.79412841796875 × 0.96875
  = **0.7693119049072266 ≈ 0.76931** (same ceiling as X16 by ratio construction).
- Recorded ceiling-hugging noise (max |Δ| vs applicable ceiling):
  X14 +0.00028 (0.96903 vs 0.96875); X15 −0.00012 (0.96863 vs 0.96875);
  X16 −0.00030 (0.76902 vs 0.76931). Recorded max |Δ| = **0.00030**.
- PROPOSED G1 mismatch band: **[0.05, 0.749]** (high edge = 0.76931 − 0.02).
  Margin 0.02 ≈ **65× the recorded ceiling noise** — a reading inside the band
  is a genuine disclosure/channel bite, not ceiling noise. Low edge 0.05: X17-P
  proves 0.000 reachable, so ≤ 0.05 leaves no room for list gain (near-floor).
- Stop/notes: mismatch > 0.749 → `SCLW_STOP_SANITY_HIGH` (still at ceiling; no
  tuning, no repair — X16 precedent). Mismatch < 0.05 → `SCLW_NOTE_FLOOR`
  (proceed descriptively; list-gain gap expected degenerate; S7 interprets —
  X16 no-low-side-stop precedent).
- Bonus avoid-context (not a named triple): X17-A2 corrected small-N disclosed
  (N=256, K1=3/K2=53) read 0.68848, missing the descriptive [0.05,0.45] band —
  small-N disclosed also non-decodable, supporting the full-intermediate-scale
  move rather than another small-N re-ask.

G1 derivation rule (if G1 amends numbers): high edge = applicable ceiling −
  M with M ≥ 50 × recorded max |Δ| (currently 0.00030 → M ≥ 0.015; proposed M
  = 0.02); low edge ∈ [0.03, 0.10] with the stated floor rationale; any
  amendment re-shows this arithmetic.

---

## 2. Variance-band + spike-fraction edges (R1)

**PROPOSED G1 (mismatch operating band): [0.05, 0.749]** — see §1 arithmetic.
Justification from recorded X-line variance: the X-line shows essentially ZERO
informative variance (all complete arms within 0.00030 of their ceilings; X17-C
0.76318 likewise at chance, descriptive). The band is therefore set by
noise-multiple (≈65×), not by fitting — there is no recorded variance to fit,
and fitting to ceiling noise would be overfitting. Marked PROPOSED; G1 confirms
or applies the §1 derivation rule.

**PROPOSED G3 (spike-fraction band): [0.02, 0.70]** — carried verbatim from
X16/X17 (X17 measured 253/1024 = 0.24707 ∈ band; X14 measured 747/7168 ≈
0.1042 under undisclosed small-N). Population arithmetic at the new scale:
8 blocks × 16384 = 131072 L2 positions; lower 0.02 ⇒ ≥ ~2.6k spike positions
(bin×L cells populated); upper 0.70 ⇒ non-spike reference ≥ 30% (reference
fraction stable). Violation → `SCLW_STOP_SPIKE_DEGENERATE` (strata unpopulated;
no repair).

**G2 (ranking-wiring floor, FROZEN carry-over): Q1b non-spike L8 survival ≥
0.50** — identical decoder-free ranking machinery + sharper channel (d=0.90 ⇒
≈0.90 capture expected) ⇒ X15/X16 rationale holds a fortiori; 0.50 stays a
loose wiring floor. Violation → `SCLW_STOP_WIRING`.

**Q2 re-ask condition (FROZEN X16 rule):** Q2 (F-median8 vs mean-hazard) asked
only if mismatch variance exists; mismatch < 0.005 over 131072 positions →
null-with-reason per X14-review precedent while Q1/Q1b proceed.

---

## 3. Full `scl_decode` / `SCLResult` interface freeze (R2)

Location (PROPOSED, created only under G2 authorization): NEW module
`comparison_bench/src/comparison_bench/formal_ir/nbpolar/scl.py` alongside
frozen `sc.py`. `sc.py` untouched (read-only import for the L=1 reference arm;
shared minus/plus kernels reused by import where the freeze allows).

**PROPOSED frozen signature:**

`scl_decode(logp_x, *, field, alpha, known_positions, known_values, list_width_L, prune_rule) -> SCLResult`

- `logp_x` / `field` / `alpha` / `known_positions` / `known_values`: contract-
  identical to `sc_decode` (float64 log-scores symbol-axis-last, logsumexp-0
  rows, exact-zero `-inf` preserved, NaN/+inf rejected; positions/values
  parallel arrays, zero is a value). No defaults frozen except `alpha=2` and
  `chunk_rows=512` carried from `sc.py`.
- `list_width_L`: caller-supplied positive integer, NO default. Width contract
  folded into the field/shape category (non-integer/≤0 → same
  TypeError/ValueError style as `chunk_rows` validation, `sc.py:190-198`).
- `prune_rule`: opaque callable slot, values UNFROZEN. FROZEN slot shape:
  `prune_rule(path_metrics: float64[P], position: int, is_spike: bool, width_L: int) -> keep: int64[M], M ≤ L`;
  deterministic (same inputs → same keep set); receives per-path accumulated
  metrics + position context, returns survivor indices best-first. Mechanism,
  thresholds, spike-local hooks: UNFROZEN (G2+ choice). T1 uses a test-only
  top-L-by-metric stub (not a frozen value).

**FROZEN path-metric definition:** PM(path, i) = Σ over undisclosed j ≤ i of
ln P(U_j = u_j | prefix, B/context) using the same normalized SC conditionals
as `sc.py` (natural log; suffix marginalized; per-coordinate recursion
identical). Disclosed positions contribute 0 (forced, never branched).
Exact-zero (−inf) conditional kills the path (dropped, counted in
`pruned_count`); a path killed at a disclosed position on ALL paths raises
`ImpossibleDisclosedValueError` (same category as `sc.py`).

**FROZEN cross-path tie-break:** smallest symbol index first (`sc.py` argmax
convention), then smallest path index — stable, deterministic, implementation-
independent.

**FROZEN multi-path disclosure interaction:** at disclosed positions every
surviving path takes the disclosed value (no split, metric +0); dead paths
stay dead; all-paths-zero-support → `ImpossibleDisclosedValueError`.

**FROZEN chunk_rows / error-category carry-over:** `chunk_rows=512` default,
allocation-only row-chunking semantics (`sc.py:176-207`); all five `sc.py`
failure categories carried verbatim (metric contract, field/shape contract
+ width, known-coordinate contract, `ImpossibleDisclosedValueError`, numeric
nonfinite). No new error category except via the width fold-in above.

**FROZEN `SCLResult` fields:** `u_candidates` int64[M,N] (M ≤ L, best-first);
`x_candidates` int64[M,N] re-encoded; `path_metrics` float64[M] (best-first);
`survivor_count` int M; `requested_width` int L; `pruned_count` int (total
pruned across positions, descriptive); `status` str ("ok" on every return);
`known_count` int; `known_mask` bool[N]; `metric_provenance` dict (`sc.py`
provenance + `list_width_L` + `prune_rule` name, mechanism values NOT
recorded as claims). No per-path per-position conditionals (M×N×q too big;
evidence-size rule).

**FROZEN L=1 equivalence (hardest T1 test):** `scl_decode(..., L=1, stub)`
reproduces `sc_decode` bit-identically (`u_hat`, `x_hat`,
`decision_log_scores` == `path_metrics[0]`).

**FROZEN measurement definitions (both, so S7 is interpretable):**

- Coverability (necessary-condition proxy, decoder-free): X14 §2 ranking
  recipe verbatim — per-position top-L rank survival `r_j ≤ L` at spike strata
  ([2,4)/[4,8)/[8,inf) + nonspike_ref, margin 2.0 bits, `sc.py` tie
  convention), per-seed then pooled mean/sample-std(n−1)/range; Q1b symmetric
  on p1 columns. Reported as coverability ONLY, never as list performance.
- Path-survival (stronger successor question): per-block indicator that the
  TRUE full path (all N positions equal truth) is among `u_candidates` at
  termination; pooled per-seed + mean/sample-std(n−1)/range at ladder L only.
  S7 reads: coverability gates necessity; path-survival gates any unlock-track
  continuation; neither is FER/reliability/efficiency.

---

## 4. L sweep set + knee/plateau decision rule (survey L NON-BINDING)

Survey L∈{4,8,32} (Yuan/Abbasi/Falk context) is EXPLICITLY non-binding
(survey §7 adjudication; design (b)). The sweep below derives from
working-point logic, not inheritance:

**PROPOSED descriptive coverability sweep: L ∈ {2, 4, 8, 16, 32, 64}** —
decoder-free ranking curve (X14-Q1 machinery; zero decoder cost, vectorized
argsort per position). Derivation: {4,8} kept for X14/X15 comparability (same
definitions, not same values); one economy doubling below (L=2: does ANY
survival exist?); doublings above to 64 for saturation (Abbasi: GF(16)
saturates by L>8 on AWGN; Falk: GF(5) needs far larger L — 64 bounds the first
look; larger L deferred to S7 only if 64 unsaturated AND cost justified).
Path-survival (list decoder) measured ONLY at the derived ladder (2–4 values),
never the full sweep.

**PROPOSED knee/plateau rule (applied at S7 to the measured curve):**
knee = smallest swept L with marginal absolute survival-fraction gain per
doubling < 0.05; plateau = smallest swept L with gain vs next doubling <
0.01; economy = largest swept L below knee (if none, economy = knee).
Ladder = {economy?, knee, plateau} (2–3 values) + measured curve attached.
Any future unlock claim cites survival at THOSE L values. Rule PROPOSED; S7
applies it exactly or records why the curve defeats it (e.g. monotone
unsaturated → no plateau claimed).

---

## 5. Binary/CRC-SCL control ruling (resolves design.md:103)

**Ruling: OUT for the working-point stage.**

One-line rationale: no binary polar construction exists in
`formal_ir/nbpolar/`, and adding one doubles the freeze surface (new kernel,
new construction, new metric path) for a first working point whose question
is q-ary SC-vs-list separation — the Falk q-mismatch warning is carried as a
reading lens on the ladder slope at S7, not as an arm. Revisit at S7 only if
the ladder slope suggests q-mismatch (flat-then-steep GF(5)-style behavior).

---

## 6. 3-line prereg text + stop tokens + T0/T1 focused-test list

**PROPOSED 3-line prereg (verbatim candidate for the probe-root prereg.md):**

1. Question: at (N=16384, K1=167/K2=3373 first-natural forced disclosure,
   d=0.90 X15-shape synthetic channel), does greedy-SC vs list decoding
   separate (paired mismatch/exact-block gap, descriptive) with populated
   spike strata; decoder-free coverability-vs-L over L∈{2,4,8,16,32,64} plus
   list path-survival at the S7-derived ladder — descriptive only, no
   FER/reliability/efficiency claims, SCL stays locked.
2. Parameters: N=16384 q=32 alpha=2 poly37 chunk_rows=512 floor 1e-15;
   channel d=0.90 / neighbors 0.09 / rest 0.01 / rare96-zero / C8-90pct shape;
   K1=167 K2=3373 first-natural; table-label 2026092500, blocks
   2026092501..2508 ×1 block (131072 L2 positions); G1 mismatch [0.05,0.749]
   high-stop, G2 Q1b-nonspike-L8 ≥0.50, G3 spike [0.02,0.70], margin 2.0 bits,
   bins [2,4)/[4,8)/[8,inf)+nonspike_ref, R=8 F-median8; decoder_calls=8
   reference + list calls recorded, rng_calls recorded, tag_calls=0.
3. Command: `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar &&
   export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
   MALLOC_ARENA_MAX=2 && timeout 600
   .venv/bin/python workspace/probes/nbpolar_scl_working_point/body.py`
   (bare python/python3 never used; interpreter fallback recorded).

**Stop tokens:** `SCLW_STOP_SANITY_HIGH` (G1 high), `SCLW_STOP_WIRING` (G2),
`SCLW_STOP_SPIKE_DEGENERATE` (G3), `SCLW_STOP_IMPOSSIBLE` (disclosed truth
without support), `SCLW_STOP_PROTECTED` / `SCLW_STOP_NONFINITE` /
`SCLW_STOP_SEED_GREP` / `SCLW_STOP_SIZE` / `SCLW_STOP_PREREG_MISMATCH`
(generic); `SCLW_NOTE_FLOOR` (mismatch <0.05, proceed descriptively).
Execution-error-only single recorded rerun (Tier-X rule).

**T0/T1 focused-test list (G3 gate; T2 milestones only):**
T0 — import/compile/structure; chunked-vs-unchunked (`chunk_rows=512` vs
`None`) identity; L=1-vs-`sc_decode` bit-identity on toy N=8; tie-break unit
(smallest-index on ties, cross-path then path-index). T1 — diagonal-smoke
(column sums, disjointness, argmax=diagonal, floor-hit 96/1024); disclosure-
smoke (all-known returns exact; K1/K2 prefix sizes exact); forced-no-branch
at disclosed positions (survivor metrics +0, no split); survivor-count ≤ L
invariant at every position; prune-slot shape/determinism with test-only stub;
order-identity (shuffled `known_positions` input order ⇒ bit-identical);
path-refusal asserts (no protected imports); gate asserts (G1/G2/G3
evaluation on synthetic fixtures). Plus full NB-Polar suite green.

---

## 7. Seed range proposal + grep cleanliness (R3)

**Proposal: REUSE reserved band 2026092500..2026092519** (reserved-but-
unactivated for exactly this gate; STATUS.yaml 2026-09-20). No new band
needed — reuse minimizes occupied-space growth. Assignment:

| Role | Seeds |
|---|---|
| table-identity master (label only, deterministic table ⇒ zero table RNG) | 2026092500 |
| working-point blocks (8 seeds × 1 block) | 2026092501..2026092508 |
| ladder/path-survival reserve | 2026092509..2026092516 |
| tag-master reserve (UNUSED; `tag_calls: 0`) | 2026092517 |
| spares | 2026092518..2026092519 |

Avoided (occupied, never reused): X14 2026092350..2357, X15 2026092369..2377,
X16 2026092380..2388, X17 2026092390..2399, P20T 2026092400..2407/2410..2413,
P20S 2026092360..2367, all 20260923xx..20260924xx.

**Cleanliness (draft-time read-only grep, 2026-09-20 session):** `20260925`
hits repo-wide = ONLY the reservation lines in this packet dir
(`STATUS.yaml:32-38`, `SCOPING_NOTES.md:14-18`) — zero hits in
`workspace/probes/`, `*.py` bodies, `results.json`, tag files, or any other
dir. Re-grep REQUIRED at G1 freeze before activation (reservation alone
authorizes nothing).

**Grep commands for the G1 freeze (copy-paste; read-only, decoders never run):**

```bash
# 1. Proposed-band absence outside this packet dir (expect: zero hits)
grep -rn "202609250[0-9]\|202609251[0-9]" workspace/ comparison_bench/src/ tools/ experiments/ results/ comparison_bench/outputs_comparison/ docs/ openspec/ 2>/dev/null; echo "exit=$?"
# 2. Full-band audit incl. packet docs (expect: ONLY SCL-SYNTHETIC-GATE reservation lines)
grep -rn "20260925" --exclude-dir=.git --exclude-dir=.venv . 2>/dev/null
```

---

## 8. Standing constraints carried (binding, not re-litigated)

- Frozen SC-only RN scope untouched; `sc.py` untouched (read-only inventory +
  L=1 reference import only); SCL stays locked through G6; no production-
  module merge; no real-data execution; no protected opens.
- No FER / reliability / efficiency / branch-superiority claims anywhere in
  this track; descriptive synthetic-only; coverability reported as
  necessary-condition proxy, never as list performance.
- Evidence-size rule (D4, in force): single committed file ≤ ~2 MB —
  `results.json` scalar-only (per-seed + pooled mean/sample-std(n−1)/range),
  est. < 100 KB. Probe-root-only writes (`workspace/probes/<id>/`).
- Never-stage guard reminder: never stage `*.bin`, raw-data artifacts, or
  anything under `results/` / `comparison_bench/outputs_comparison/` from
  this track; Tier-X per-probe ledger/memory/index updates milestone-batched.
- Small-task fast path NOT claimed: a list decoder is a new module and needs
  the full G1→G6 gate sequence (tasks.md note).

---

## Reviewer-risk closure map (for G1)

- R1 parametric working point → §1: single parametric step (d=0.90,
  recipe-identical), axis rationale recorded, margin rule stops-instead-of-
  tunes, G1 derivation rule for amendments.
- R2 under-specified list interface → §3: full slot-shape freeze (metric,
  tie-break, prune I/O contract, disclosure, error carry-over, both
  measurement definitions); values/mechanism UNFROZEN by explicit label.
- R3 seed hygiene → §7: reuse justification, assignment table, draft-time
  cleanliness result, copy-paste re-grep commands, re-grep-at-freeze rule.

---

## NOT-AUTHORIZED footer (binding)

**This draft authorizes NOTHING.** No working-point numbers are frozen, no L
values are frozen, no pruning values are frozen, no seeds are activated, no
module is created, no test is run, no execution is permitted. G1 freeze
review (S2) + explicit user authorization (S3) are still REQUIRED before any
implementation or execution. Every gate in design.md §(e) stays
NOT AUTHORIZED. SCL stays locked.
