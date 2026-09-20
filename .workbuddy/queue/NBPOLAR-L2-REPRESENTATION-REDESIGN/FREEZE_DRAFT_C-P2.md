# FREEZE_DRAFT_C-P2.md — NBPOLAR-L2-REPRESENTATION-REDESIGN (C-P2 freeze draft, axis ii, DRAFT ONLY)

- State: `DRAFT_NOT_FROZEN_NOT_AUTHORIZED` — content plan for the C-P2 freeze review
  (B3-style gate of `openspec/changes/l2-representation-redesign/`). This draft freezes
  nothing, authorizes nothing, implements nothing, executes nothing.
- Forced-by record: B8 disposition `AXIS_I_RETIRED_FORCED_SWITCH_TO_AXIS_II`
  (decision-log 2026-09-20/21 entry; packet `STATUS.yaml`). C-P1 (hazard-ranked L2
  disclosure placement at the G3-verbatim triple) read pooled greedy-SC mismatch
  ratio-of-sums **0.7681045532226562** (100677/131072) above the frozen G1 high edge
  0.719 → `BR_STOP_SANITY_HIGH` → RETIRE-ceiling → axis (i) retired → forced switch to
  axis (ii) = C-P2 at the same triple. Route budget now 1/6; C-P2 is probe 1 of axis (ii).
- No-contact statement: NO implementation, NO execution, NO protected opens (V25 counts,
  parquet/pairs, 1M/1.5M/2M content, `raw_prior_*.npz`), NO decoder runs, NO data contact.
  Every number below is read from already-committed records: `design.md` (b) C-P2
  candidate + knee rule + ceiling-margin derivation rule, `FREEZE_DRAFT.md` (C-P1 format
  + band rules + G2/G3/Q2 carries), decision-log 2026-09-20 B2/B3 entry + 2026-09-20/21
  B6/B7/B8 entry, the C-P1 probe root (`workspace/probes/b1-placement-hazard-ranked/
  results.json` + `prereg.md`), the G3 probe root
  (`workspace/probes/scl-synthetic-working-point/results.json`), and the P20C packet
  (`OPERATOR_RETURN.md` +1024 restoration, descriptive). Read-only inventory only.
- Conventions: FROZEN = recipe/value carried verbatim with citation; PROPOSED = candidate
  value for the C-P2 freeze review to confirm/amend/reject. Per design (b), values are
  PROPOSED; the freeze confirms or re-derives with the stated arithmetic and must re-show
  it if amended.

---

## 1. Frozen probe design C-P2 (axis ii — disclosure AMOUNT / STRUCTURE)

### 1.1 Why this design (the forced switch, restated)

Axis (i) placement is retired on its pre-registered reading: C-P1 moved the disclosed SET
(hazard-ranked, F-median8 top-K2) while holding the COUNT (K2=3373) and still ceiling-hugged
(0.7681045532226562 vs placement-invariant ceiling 0.7693119049072266; effect vs G3
first-natural 0.770302 = 0.002197265625 ≈ 2.2× recorded noise, ≈23× short of the band
margin). The recorded evidence that amount/structure can bite: **P20C (real DEV,
descriptive)** — +1024 L2 disclosure under the frozen order (K2 6492→7516) restored block 1
(B0 2/3 verify_failed @L2@723 → B1 3/3 exact; `b1_restored_count` 1; key delta exactly
+5120 = 5×1024). X16/G3 show first-natural AMOUNT at full scale gives no synthetic bite,
so amount is moved in tier steps together with, and separately attributable to, structure.

### 1.2 Triple — G3/C-P1 reused VERBATIM, L2 amount/structure moved

| Axis | C-P2 value | Proven-pointless / recorded values it differs from |
|---|---|---|
| N | 16384 (14 polarization levels) | X14/X15 N=256; X16 N=32768; X17 small-N arms N=256 |
| L1 disclosure | K1=167 first-natural true-u1 conditioning (UNCHANGED in every arm — axis ii moves L2 only) | X14/X15 undisclosed (K for pm/K only); X16 K1=334; X17-A2 K1=3 |
| L2 disclosure amount/structure | six arms, §1.3 (base K2=3373 = exact-ratio halving of the 2M literals 6746/32768 → 3373; zero rounding; K2/N ≈ 20.587% at base) | X16 K2=6746 first-natural; G3 K2=3373 first-natural contiguous (recorded 0.770302); C-P1 K2=3373 hazard-ranked contiguous (recorded 0.768105) |
| Channel | diagonal pin d=0.90, X15-recipe shape verbatim (8-neighbor share 0.9×(1−d)=0.09 → 0.01125 each; rare96 pre-floor 0; rest share 0.1×(1−d)=0.01 → ≈1.0881e-5 each) | X14 flat Dirichlet; X15/X16 d=0.75; X17-P d=0.999 control |

Recorded scalars only: every channel/table parameter above is a recorded literal from the
G3/C-P1 records; no artifact is read to produce this draft.

### 1.3 Variants — six arms in ONE probe; tier step Δ = 512

Motivation anchors (recorded, descriptive): P20C +1024 restoration (§1.1); C-P1
descriptive placement scalars — hazard-ranked disclosed-set mean hazard 4.658 vs
first-natural prefix 1.029 vs undisclosed 0.116 (the two placements select genuinely
different geometry, so a hazard tier-1 is a real structural move, not a relabeling).

| Arm | Variant | K2' | Disclosed-set construction (deterministic; zero RNG) | Placement family |
|---|---|---|---|---|
| V1a | amount −2 tiers | 2349 | first 2349 natural L2 positions (contiguous prefix) | first-natural |
| V1b | amount −1 tier | 2861 | first 2861 natural L2 positions (contiguous prefix) | first-natural |
| V1c | amount +1 tier | 3885 | first 3885 natural L2 positions (contiguous prefix) | first-natural |
| V1d | amount +2 tiers | 4397 | first 4397 natural L2 positions (contiguous prefix) | first-natural |
| V2 | structure at fixed count | 3373 | tier-1 = first 2349 natural; tier-2 = stride-13 spread {2349 + 13k, k = 0..1023} over the remainder (1024 positions) | first-natural-derived (non-contiguous) |
| V3 | structure at fixed count, hazard tier-1 | 3373 | tier-1 = F-median8 top-1024 (C-P1 frozen ranking formula: descending score, tie-break ascending index); tier-2 = exact even-spread rule: R = the L = 16384 − 1024 = 15360 L2 positions NOT in tier-1, ascending; tier-2 = { R[floor(j·L/2349)] : j = 0..2348 } — exactly 2349 positions | hazard-derived tier-1 + even-spread tier-2 |

**V3 tier-2 exactness (dedup guarantee, one line):** the index sequence floor(j·L/2349) with L = 15360 advances by ≈ 6.54 positions per step, so it is strictly increasing and the 2349 picks are distinct BY CONSTRUCTION — |tier-2| = 2349 exactly, K2' = 1024 + 2349 = 3373 exactly, and the B5 focused tests assert these disclosed-set sizes exactly (|tier-2| = 2349, K2' = 3373) as a hard check.

Which placement each variant uses, and why:

- **V1a–V1d (first-natural contiguous):** the AMOUNT axis is moved at the placement where
  the recorded anchor sits (G3 first-natural, K2=3373), so the ladder reads amount alone.
  Hazard placement is retired (axis i) and must not be mixed into the amount reading.
- **V2 (first-natural-derived, non-contiguous):** isolates STRUCTURE at fixed count —
  attribution vs G3 is structure only, the ceiling is unchanged, and the Q2
  detector-vs-detector contrast stays valid (§3.2).
- **V3 (hazard-derived tier-1 + even-spread tier-2):** the design.md (b) C-P2 sketch carried for
  continuity; it completes the placement×structure 2×2 at fixed count (G3 = natural
  contiguous [recorded]; C-P1 = hazard contiguous [recorded]; V2 = natural tiered;
  V3 = hazard tiered) and its cleanest attribution is vs C-P1 = structure only. Its Q2
  local-spike arm is DROPPED (§3.3).
- All disclosed sets are handed to `sc_decode` in ascending position order (order-irrelevant
  per frozen `sc.py`; C-P1 verbatim). L1 K1=167 stays first-natural in every arm.

**Paired-block design (PROPOSED):** the 8 blocks are drawn ONCE per seed and shared across
all six arms (same seeds ⇒ same blocks in every arm), so arm-to-arm comparisons are paired
on identical blocks. `rng_calls` = 16 (8 blocks × 2; C-P1 count verbatim),
`decoder_calls` = 48 (6 arms × 8 blocks; one greedy `sc_decode` per arm-block),
`tag_calls` = 0, zero table RNG (table-identity label only).

### 1.4 Placement-invariance of the ceiling — count-dependent

The C-P1 placement-invariance property (the disclosed SET moves, the COUNT does not ⇒ the
applicable no-information ceiling is placement-invariant) holds ONLY at fixed K2 count.
V1a–V1d move the count, so the applicable ceiling MUST be recomputed exactly per arm
(§2.2) and each arm is banded against its OWN ceiling. V2/V3 hold the count at 3373 ⇒ the
recorded ceiling 0.7693119049072266 applies unchanged and any in-band reading is
attributable to structure alone (V2 vs G3; V3 vs C-P1).

### 1.5 Tier-step rule (knee) — carried from design (c) 3, epsilon freeze-set

FROZEN rule text (design (c) 3): "when tiered amounts are probed, knee = smallest
disclosure increment whose marginal mismatch movement per increment falls below the
freeze-set epsilon; increments beyond the knee are recorded, not spent."

- Tier step Δ = 512 positions — exact-ratio halving of the P20C +1024 real-data step,
  consistent with the triple's exact-ratio construction (334→167, 6746→3373). Ladder =
  −2Δ, −1Δ, +1Δ, +2Δ around the recorded anchor 3373 (= 0Δ).
- Marginal movement per increment = |mismatch(K2_b) − mismatch(K2_a)| for adjacent ladder
  steps, normalized per Δ = 512 positions.
- **PROPOSED freeze-set epsilon ε = 0.005 per Δ-step:** (i) it is the route's existing
  freeze-set constant (Q2 null-with-reason threshold, carried in the C-P1 prereg line);
  (ii) C-P1's pooled per-seed sample_std = 0.001493 ⇒ ε ≈ 3.3× seed noise; (iii) the
  expected movement under ceiling-hugging is the per-step ceiling drop
  512 × 31 / 524288 = 0.0302734375 ≈ 6.1× ε, so ε discriminates "tracks the ceiling" from
  "decouples from the ceiling".
- Anchor caveat: the K2=3373 first-natural reading is the RECORDED G3 value 0.770302
  (seeds 2026092501..2508) and is NOT re-run (proven-pointless; C-P1 precedent). The two
  steps touching the anchor (2861→3373 and 3373→3885) are labeled CROSS-PROBE; the two
  in-probe steps (2349→2861 and 3885→4397) are labeled IN-PROBE. The knee disposition
  records which steps carried which label; a knee may not be declared on a cross-probe
  step alone unless its movement exceeds 2ε, else record "knee not determinable within
  ladder" and spend no further amount probe.
- Increments beyond the knee are recorded, not spent: no further amount probe on this
  route within the axis-(ii) budget.

### 1.6 Differ proofs (each arm vs every recorded point)

| Arm | vs G3 (natural, 3373) | vs C-P1 (hazard, 3373) | vs X16 (natural, 6746, N=32768) | vs X14/X15 |
|---|---|---|---|---|
| V1a–V1d | amount only | amount + placement | N + amount + placement | all axes |
| V2 | structure only | placement + structure | N + placement + structure | all axes |
| V3 | placement + structure | structure only | N + placement + structure | all axes |

No arm re-asks any recorded point: every K2' ∈ {2349, 2861, 3885, 4397} is new; V2/V3
disclosed sets at count 3373 differ from both G3's contiguous prefix and C-P1's hazard
top-3373 set. Add-N remains barred by the strategy stop rule.

### 1.7 Resource estimate (estimates only, no new risk class)

48 SC decodes at N=16384: C-P1 measured wall 34.35 s / peak RSS 195952640 B (≈187 MiB) for
8 SC + coverability + hazard + gates. Linear scaling ⇒ ≈ 200–210 s wall; per-decode memory
unchanged (arms run sequentially, same N, same frozen decoder). `timeout 600` ≈ 2.9×
headroom. Same single-thread pins; same decoder module set (frozen `sc.py` only; `scl` /
`sc_chunked_gate` asserted absent from `sys.modules` at import).

---

## 2. G1 mismatch band per variant (ceiling recomputed exactly per K2')

### 2.1 Recorded ceiling-hugging noise — UPDATE REQUIRED (the one open decision)

Record carried into C-P1 (FREEZE_DRAFT §1.2): X14 +0.00028, X15 −0.00012, X16 −0.00030,
G3 +0.00099 → recorded max |Δ| = 0.00099. C-P1's own reading
(`ceiling_delta_measured_minus_ceiling` = −0.0012073516845703125) is a new, LARGER
below-ceiling deviation and joins the record (below-ceiling deviations already count:
X15, X16). **PROPOSED updated record: max |Δ| = 0.0012073516845703125 (C-P1, the worst
recorded point).** Consequence: M ≥ 50 × 0.0012073516845703125 = 0.060367584228515625.
Retaining the frozen M = 0.05 would give an effective multiple of
0.05 / 0.0012073516845703125 = 41.4× < 50× — NON-COMPLIANT with the derivation rule.
(Both multiples are stated on the same nominal-M basis: M = 0.05 → 41.4× and
M = 0.065 → 53.8× of the updated noise record 0.0012073516845703125.)
**PROPOSED M = 0.065** (53.8× the updated noise; conservative). This is the ONE
decision the freeze review must make: confirm the updated noise record → M = 0.065
(bands in the right-hand column below); or explicitly retain 0.00099 with a stated reason
→ M = 0.05 (left-hand column). §4.4 prereg carries the M = 0.065 column as PROPOSED.

### 2.2 Ceiling arithmetic per count (exact; RECORDED scalars only)

ceiling(K2') = (1 − K2'/N) × 31/32 = (16384 − K2') × 31 / 524288:

| K2' | (16384 − K2') | × 31 | ceiling (exact decimal) |
|---|---|---|---|
| 2349 | 14035 | 435085 | 0.8298585299072265625 |
| 2861 | 13523 | 419213 | 0.7995853424072265625 |
| 3373 | 13011 | 403341 | 0.7693119049072265625 (recorded; applies to V2/V3) |
| 3885 | 12499 | 387469 | 0.7390384674072265625 |
| 4397 | 11987 | 371597 | 0.7087650299072265625 |

### 2.3 Band table (low edge 0.05 for every arm — X17-P proves 0.000 reachable, so ≤ 0.05
leaves no room for any downstream list gain)

| Arm | K2' | ceiling | high edge @ M = 0.05 | high edge @ M = 0.065 (PROPOSED) |
|---|---|---|---|---|
| V1a | 2349 | 0.8298585299072265625 | 0.779 | 0.764 |
| V1b | 2861 | 0.7995853424072265625 | 0.749 | 0.734 |
| V1c | 3885 | 0.7390384674072265625 | 0.689 | 0.674 |
| V1d | 4397 | 0.7087650299072265625 | 0.658 | 0.643 |
| V2 | 3373 | 0.7693119049072265625 | 0.719 (C-P1 verbatim) | 0.704 |
| V3 | 3373 | 0.7693119049072265625 | 0.719 (C-P1 verbatim) | 0.704 |

Frozen-edge convention (C-P1 precedent): the frozen high edge is the conservative
truncation (3 decimals, rounded DOWN) below the ceiling − M candidate; e.g.
0.7693119049072265625 − 0.065 = 0.7043119049072265625 → 0.704.

### 2.4 Stop semantics (carried; per arm)

- Each arm's G1 measurement = pooled mismatch RATIO-OF-SUMS over that arm's 131072
  positions (C-P1 definition verbatim: total mismatches / total positions, not the mean of
  per-seed ratios).
- Above its OWN high edge → ceiling-hugging repeat at that amount/structure →
  `BR_STOP_SANITY_HIGH` for that arm; no repair, no tuning (X16/G3/C-P1 precedent).
- Below 0.05 → `BR_STOP_SANITY_LOW`, recorded DESCRIPTIVELY and execution PROCEEDS (F2
  clause verbatim: the token names the reading, not an execution halt; the
  retire-or-re-ask-once disposition is applied at §5 within budget; the implementer must
  not halt the probe on a low reading).
- All six arms run to completion before any gate evaluation (X16 precedent: stop payloads
  carry the complete descriptive evidence); the body never halts mid-run on a band reading.

---

## 3. Q2 contrast — explicit redefinition (B7 F1 / B8 carried)

### 3.1 The degeneracy record (why the C-P1 form cannot be reused)

C-P1 asked Q2 under hazard-ranked placement, where the disclosed set IS the F-median8
top-K2 set: `coverage_local_spike` read exactly 0.0 on all 8 seeds (min = max = 0.0;
`n_mm_in_local` = 0 every seed) because disclosed positions are forced-correct and cannot
mismatch — a structural tautology, NOT a localization finding (B7 F1 annotate-not-read;
B8 rejected the "localization finding" reading). Under first-natural placement the same
contrast is genuine: G3 recorded `coverage_local_spike` 0.205249343832021 vs
`coverage_mean_hazard` 0.20205021542118556.

### 3.2 Redefinition for C-P2

- **Valid arms (V1a–V1d, V2 — first-natural-derived placement):** the Q2
  detector-vs-detector contrast is carried with the recorded definitions verbatim
  (`n_mm_in_local` = |mismatch ∩ F-median8 top-K2' set|, `n_mm_in_base` = |mismatch ∩
  raw-hazard top-K2' set|; coverage = hits / total mismatches; detector set size = the
  arm's own K2'). Null-with-reason if the arm's pooled mismatch < 0.005 (X14-review
  precedent carried). Recorded caveat: the disclosed prefix overlaps each detector's top
  set by a construction-defining count (C-P1 recorded
  `overlap_disclosed_vs_first_natural_prefix` 702.875 ± 24.97 at K2=3373), which caps
  coverage below 1 by construction; the overlap count is recorded per arm as a descriptive
  scalar and feeds no gate.
- **Invalid arm (V3 — hazard-derived tier-1 placement):** the local-spike arm is DROPPED,
  with the reason recorded in `results.json` under
  `Q2_LOCAL_SPIKE_DROPPED_NON_FIRST_NATURAL`: under any non-first-natural (hazard-ranked)
  placement the local-spike detector's top set and the disclosed set overlap BY
  CONSTRUCTION (V3's tier-1 = F-median8 top-1024 ⊆ disclosed ∩ detector-top), so coverage
  mixes a forced-correct artifact with signal; the C-P1 extreme (full overlap) produced a
  tautological 0.0, and no C-P2 arm may reproduce a tautological 0.0 reading. For V3 the
  mean-hazard coverage is still reported as a SINGLE-detector descriptive scalar (its top
  set is not contained in the disclosed set), and NO detector-vs-detector contrast is
  claimed for V3.

---

## 4. Wiring gates carried, stop tokens, prereg, probe root, seeds

### 4.1 Wiring gates (FROZEN carry-over; evaluated per arm)

- **G2 (ranking-wiring floor): Q1b non-spike L8 survival ≥ 0.50 per arm** — identical
  decoder-free ranking machinery + sharper channel (d=0.90 ⇒ ≈0.90 capture expected)
  ⇒ X15/X16/C-P1 rationale holds a fortiori (C-P1 measured 0.999754). Violation →
  `BR_STOP_WIRING`.
- **G3 (spike-fraction band): [0.02, 0.70] per arm** — population arithmetic at this
  scale: 8 blocks × 16384 = 131072 L2 positions; lower 0.02 ⇒ ≥ ~2.6k spike positions
  (bin×L cells populated); upper 0.70 ⇒ non-spike reference ≥ 30% (reference fraction
  stable). Violation → `BR_STOP_SPIKE_DEGENERATE` (C-P1 measured 0.098907).
- **Strata comparability (PROPOSED):** the spike reference pm is FROZEN at mean(h) over
  the first-natural K2=3373 prefix (G3 verbatim) for ALL arms, so the bins
  ([2,4)/[4,8)/[8,inf)+nonspike_ref, margin 2.0 bits, R=8 F-median8) and the spike
  population are identical across arms and comparable with G3/C-P1; the hazard table and
  pm are properties of the frozen table + reference prefix, not of an arm's disclosure.
- A wiring failure is a wiring stop, not an axis reading; it does not consume the per-axis
  probe budget (design (c) 1).

### 4.2 Stop tokens (BR_STOP_* family carried verbatim)

`BR_STOP_SANITY_HIGH` (G1 high, per arm), `BR_STOP_SANITY_LOW` (G1 low — descriptive
reading, execution PROCEEDS, F2), `BR_STOP_WIRING` (G2), `BR_STOP_SPIKE_DEGENERATE` (G3),
`BR_STOP_IMPOSSIBLE` (disclosed truth without support), `BR_STOP_SC_CONSISTENCY`
(sc re-encode self-check; F1 body-plan carry: site 1 full-block sc re-encode inside the
per-arm-block decode path — exercised 48 times, once per arm-block, inside the frozen
decode calls and adding no decoder call; sites 2/3 small-block and fully-forced sc
re-encode under `--selftest` only, because any extra in-run decoder call would break the
frozen decoder_calls line; G3's third site was the list re-encode and is carried as the
sc-only analog, not silently dropped), `BR_STOP_PROTECTED_OPEN` / `BR_STOP_WRITE_OUTSIDE` /
`BR_STOP_NONFINITE` / `BR_STOP_PREREG_MISMATCH` / `BR_STOP_SEED_GREP` / `BR_STOP_SIZE`
(generic; write scope is probe-root-only `workspace/probes/b2-amount-structure/`;
evidence ≤ ~2 MB). Execution-error-only single recorded rerun (Tier-X rule).

### 4.3 Probe root + absence verification

Probe root: `workspace/probes/b2-amount-structure/` — probe-root-only writes.
Target-output absence verified this session: the probes listing shows 27 legacy roots
(incl. `b1-placement-hazard-ranked/`), none `b2-*`; repo-wide grep for
`b2-amount-structure` → zero hits in `workspace/probes/`, any `*.py` body,
`results.json`, tag files, or any other directory — the only hits are the
packet-doc reservation lines in this draft itself (C-P1 precedent scoping).

### 4.4 3-line prereg (verbatim candidate for the probe-root prereg.md)

1. Question: at the G3/C-P1 triple reused verbatim (N=16384, K1=167 first-natural L1
   true-u1 conditioning, d=0.90 X15-shape synthetic channel), does greedy-SC pooled
   mismatch fall inside each arm's own G1 band when the L2 disclosure AMOUNT/STRUCTURE
   moves — amount ladder K2' ∈ {2349, 2861, 3885, 4397} first-natural contiguous (tier
   steps ±512 around the recorded G3 anchor 3373), non-contiguous tiered structure at
   fixed K2=3373 (first-natural tier-1 2349 + stride-13 spread tier-2 1024), and
   hazard-ranked tier-1 1024 + exact even-spread tier-2 2349 at fixed K2=3373 — i.e. does
   amount/structure produce a bite where placement alone ceiling-hugged (C-P1
   0.7681045532226562); per-seed values then pooled mean/sample-std(n−1)/range over 8
   seeds per arm on paired shared blocks; knee rule ε=0.005 per 512-step; descriptive
   only, no FER/reliability/efficiency/branch-superiority claims, no pass/fail verdicts,
   SCL stays locked, zero real-data contact.
2. Parameters: N=16384 q=32 alpha=2 poly37 chunk_rows=512 floor 1e-15; channel d=0.90 /
   8-neighbor share 0.09 (0.01125 each) / rare96 pre-floor 0 / rest share 0.01
   (≈1.0881e-5 each) / C8-90pct shape; K1=167 first-natural L1 in every arm; arms V1a
   K2=2349 / V1b K2=2861 / V1c K2=3885 / V1d K2=4397 first-natural contiguous prefixes;
   V2 K2=3373 = first 2349 natural + stride-13 spread {2349+13k, k=0..1023}; V3 K2=3373 =
   F-median8 top-1024 (descending, tie-break ascending) + even-spread tier-2 =
   {R[floor(j*15360/2349)], j=0..2348} over the ascending non-tier-1 positions R
   (L = 15360; strictly increasing indices => 2349 distinct positions by construction;
   all disclosed sets passed to sc_decode in
   ascending position order; table-label 2026092800 (identity only, zero table RNG),
   paired working-point blocks 2026092801..2026092808 ×1 block shared across all arms
   (131072 L2 positions per arm); spike reference pm frozen at the K2=3373
   first-natural prefix mean (G3 verbatim; strata identical across arms); per-arm G1
   bands (M=0.065 PROPOSED): V1a [0.05,0.764], V1b [0.05,0.734], V1c [0.05,0.674],
   V1d [0.05,0.643], V2/V3 [0.05,0.704], with BR_STOP_SANITY_HIGH/LOW (low =
   descriptive, execution proceeds); G2 Q1b-nonspike-L8 ≥0.50 per arm; G3 spike
   [0.02,0.70] per arm; margin 2.0 bits, bins [2,4)/[4,8)/[8,inf)+nonspike_ref, R=8
   F-median8; Q2 detector-vs-detector (top-K2' sets) on V1a–V1d/V2 with
   null-with-reason if arm pooled mismatch <0.005, local-spike arm DROPPED on V3
   (Q2_LOCAL_SPIKE_DROPPED_NON_FIRST_NATURAL); knee ε=0.005 per 512-step with
   cross-probe anchor labels; decoder_calls=48, rng_calls=16, tag_calls=0.
3. Command: `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export
   OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 &&
   timeout 600 .venv/bin/python workspace/probes/b2-amount-structure/body.py` —
   frozen command core `timeout 600 .venv/bin/python
   workspace/probes/b2-amount-structure/body.py`; local `.venv` absent at authoring
   time, so sibling-venv substitution `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
   is PRE-AUTHORIZED for the single execution and must be recorded in `results.json` plus
   the operator command_note (G3/C-P1 precedent); bare python/python3 never used;
   execution-error-only single rerun max, recorded. Timeout estimate: 48 SC ≈ 200–210 s
   (C-P1 measured 34.35 s for 8 SC + coverability + hazard) plus per-arm coverability;
   600 s ≈ 2.9× headroom; estimates only, no new risk class.

### 4.5 Seed range — fresh proposal + grep note (reserved-NOT-activated)

Band 2026092800..2026092819 is PROPOSED as a fresh reservation for C-P2 — no existing
band is opened, reused, or extended.

| Role | Seeds |
|---|---|
| table-identity master (label only, deterministic table ⇒ zero table RNG) | 2026092800 |
| C-P2 working-point blocks (8 seeds × 1 block, paired across arms) | 2026092801..2026092808 |
| axis-(ii) reserve (successor probe within budget, if ever needed) | 2026092809..2026092816 |
| tag-master reserve (UNUSED; tag_calls: 0) | 2026092817 |
| spares | 2026092818..2026092819 |

Avoided (occupied, never reused): X14 2026092350..2357, X15 2026092369..2377,
X16 2026092380..2388, X17 2026092390..2399, P20T 2026092400..2407 / 2410..2413,
P20S 2026092360..2367, SCL-gate/G3 2026092500..2519 (G3 working-point 2026092501..2508 +
ladder reserve 2026092509..2516), C-P1 2026092600..2619 (table 2026092600 + blocks
2026092601..2608 used; 2609..2619 reserve), test-local 2026092701..2703, all
20260923xx..20260925xx, and early official 20260911 / 20260912xx / 20260930.

**Grep note (this session, read-only; decoders never run):** patterns `20260928`,
`20260929`, `202609280[0-9]`, `202609281[0-9]`, and `b2-amount-structure` repo-wide →
zero hits in `workspace/probes/`, any `*.py` body, `results.json`, tag files, or any
other directory — the only hits are the packet-doc reservation lines in this draft
itself (C-P1 precedent scoping; the search tool respects .gitignore, so gitignored
worktree-only roots under `workspace/probes/` were additionally verified by directory
listing — no `b2-*` root).
A non-ignoring full grep is part of the C-P2 freeze checklist; reservation alone
authorizes nothing and re-grep is REQUIRED at freeze before activation.

**Grep commands for the freeze (copy-paste; read-only, decoders never run):**

```bash
# 1. Proposed-band absence outside this packet dir (expect: zero hits)
grep -rn "202609280[0-9]\|202609281[0-9]" workspace/ comparison_bench/src/ tools/ experiments/ results/ comparison_bench/outputs_comparison/ docs/ openspec/ 2>/dev/null; echo "exit=$?"
# 2. Full-band audit incl. packet docs (expect: ONLY L2-REPRESENTATION-REDESIGN reservation lines)
grep -rn "20260928" --exclude-dir=.git --exclude-dir=.venv . 2>/dev/null
# 3. Root-name absence (expect: ONLY packet-doc reservation lines)
grep -rn "b2-amount-structure" --exclude-dir=.git --exclude-dir=.venv . 2>/dev/null
```

---

## 5. Decision rule for the axis outcome (applied at B8 by the main thread)

- **INFORMATIVE (in band):** an arm inside its own band with G2/G3 wiring green → axis
  (ii) has produced a working point with disclosure bite from amount/structure alone
  (attribution per §1.4). Hands to: the next ranked question within axis (ii) (knee
  refinement / tier-composition refinement) or the SCL track as a re-freeze CANDIDATE —
  its own G1 freeze plus explicit user authorization; never automatic.
- **RETIRE-ceiling (above its own high edge):** ceiling-hugging repeat at that
  amount/structure → record the reading. If ALL arms retire → retire axis (ii), forced
  switch to axis (iii) (C-P3; Q5 activates as its first Tier-X probe). No in-packet
  amendment to chase a bite (G3/C-P1 precedent).
- **DEGENERATE (below low edge):** mismatch < 0.05 → near-floor; record descriptively
  (F2: execution proceeded); the axis may be retired or re-asked once within budget.
- **Knee application:** at B8, compute marginal movements per 512-step across the ladder
  (in-probe steps and cross-probe anchor steps labeled per §1.5); knee = smallest
  increment with movement < ε = 0.005; increments beyond the knee are recorded, not spent.
- **Max-2-probes-per-axis rule (design (c) 1, restated):** C-P2 is probe 1 of axis (ii);
  route total after C-P2 = 2/6 (C-P1 charged 1). A probe that stops on wiring/sanity does
  not consume the axis budget; a probe that produces a readable in-band or out-of-band
  mismatch does. If axes (i), (ii) and (iii) all retire within budget (≤ 6 probes total on
  this route), the route FORCES a return to the user-owned exhaustion decision (redesign
  exhausted / data acquisition / closeout); the route may not silently extend.
- Whatever the outcome: no FER/reliability/efficiency claim; no real-data follow-on; SCL
  lock status explicitly re-stated (`scl-synthetic-list-gate` track untouched, G0–G6 NOT
  AUTHORIZED); Q5 disposition recorded — Q5 stays retired-conditional unless axis (iii) is
  selected.

---

## 6. Standing constraints carried (binding, not re-litigated)

- Tier-X rules verbatim: probe-root-only writes; 3-line prereg frozen before the run;
  per-seed values + pooled mean/sample-std(n−1)/range; evidence size ≤ ~2 MB
  (`results.json` scalar-only, est. < 100 KB); milestone-batched ledger/memory/index
  updates; never-stage guard for `*.bin`, raw-data artifacts, and anything under
  `results/` / `comparison_bench/outputs_comparison/`.
- No production-module merge: `sc.py` and all `formal_ir/nbpolar/` existing modules stay
  untouched (frozen baseline; read-only import only); disclosure amount/structure is a
  caller-side truth-injection choice (D1/D2 semantics of X16 §2 carried verbatim at the
  new counts); zero protected opens; zero data contact.
- Proven-pointless carry-over: X14 (flat/N=256), X15 (d=0.75/N=256), X16
  (d=0.75/N=32768 first-natural), G3 (d=0.90/N=16384 first-natural), and now C-P1
  (d=0.90/N=16384 hazard-ranked) are never re-asked; add-N is barred by the strategy stop
  rule.
- Prior rule unchanged: raw-count MLE + 1e-15 floor for target-channel priors; λ stays
  control-arm only (X08 disposition).
- Small-task fast path NOT claimed: an axis freeze plus probe body needs the full
  B3..B8 gate sequence.

---

## NOT-AUTHORIZED footer (binding)

**This draft authorizes NOTHING.** No working-point numbers are frozen, no band is frozen,
no disclosure set is frozen, no seeds are activated, no probe body is created, no test is
run, no execution is permitted. The C-P2 freeze review (independent review of this packet:
differ-from-all-proven-pointless proof incl. C-P1, ceiling-margin arithmetic re-shown per
arm, the noise-record/M decision of §2.1, disclosure-set freeze, seed/tag grep proof,
3-line prereg text, Q2 redefinition, stop tokens) plus explicit user authorization
(B4-style implementation gate) are still REQUIRED before any implementation or execution.
`sc.py` stays frozen untouched; zero real-data contact; every gate in `design.md` (d)
stays NOT AUTHORIZED. SCL stays locked.
