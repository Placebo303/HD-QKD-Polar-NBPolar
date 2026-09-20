# FREEZE_DRAFT.md — NBPOLAR-L2-REPRESENTATION-REDESIGN (C-P1 freeze draft, B3 prerequisite, DRAFT ONLY)

- State: `DRAFT_NOT_FROZEN_NOT_AUTHORIZED` — content plan for the C-P1 freeze review
  (gate B3 of `openspec/changes/l2-representation-redesign/`). This draft freezes nothing,
  authorizes nothing, implements nothing, executes nothing.
- No-contact statement: NO implementation, NO execution, NO protected opens (V25 counts,
  parquet/pairs, 1M/1.5M/2M content, `raw_prior_*.npz`), NO decoder runs, NO data contact.
  Every number below is read from already-committed records: `design.md` (b) C-P1 candidate
  + band rule, `NBPOLAR-SCL-SYNTHETIC-GATE/FREEZE_DRAFT.md` (format template + G3
  prereg), decision-log 2026-09-20 G3 entry + geometry-mining entry, X16 packet
  `PREREG_DRAFT.md`, and the G3 probe-root prereg
  (`workspace/probes/scl-synthetic-working-point/prereg.md`). Read-only inventory only.
- Conventions: FROZEN = recipe/value carried verbatim with citation; PROPOSED = candidate
  value for B3 to confirm/amend/reject. Per design (b), values are PROPOSED; the freeze
  confirms or re-derives with the stated arithmetic and must re-show it if amended.

---

## 1. Frozen probe design C-P1 (axis i — disclosure PLACEMENT, minimum delta)

### 1.1 Triple — G3 reused VERBATIM, placement moved

| Axis | C-P1 value | Proven-pointless values it differs from |
|---|---|---|
| N | 16384 (14 polarization levels) | X14/X15 N=256; X16/X17-C N=32768; X17 small-N arms N=256 |
| Disclosure amount | K1=167 (L1 true-u1 conditioning, first-natural) + K2=3373 (L2 forced-correct) — exact-ratio halving of the 2M literals (334/32768 → 167; 6746/32768 → 3373; zero rounding; K1/N ≈ 1.019%, K2/N ≈ 20.587%) | X14/X15 undisclosed (K used for pm/K only); X16/X17-C K1=334/K2=6746; X17-A2 N=256 K1=3/K2=53 |
| Channel | diagonal pin d=0.90, X15-recipe shape verbatim (8-neighbor share 0.9×(1−d)=0.09 → 0.01125 each; rare96 pre-floor 0; rest share 0.1×(1−d)=0.01 → ≈1.0881e-5 each) | X14 flat Dirichlet; X15/X16/X17-C d=0.75; X17-P d=0.999 control |
| Disclosure placement (THE moved axis) | hazard-ranked: the L2 disclosed set = the K2=3373 L2 positions of highest frozen F-median8 hazard, descending rank (FROZEN formula h[i] − median(W8(i)), tie-break ascending, decision-log 2026-09-20 addendum; hazard atom base-2 h_j = −log2 p2[u1_cond_j, b_j, u2_true_j]); L1 disclosure K1=167 stays first-natural (placement move applies to L2 only) | G3: identical triple with first-natural L2 placement (pooled mismatch 0.770302 → `SCLW_STOP_SANITY_HIGH`); X16: first-natural at N=32768 (0.76902 ≈ ceiling) |

Recorded scalars only: every channel/table parameter above is a recorded literal from the
G3/X16 records; no artifact is read to produce this draft.

**Placement-invariance property (single-factor attribution).** The disclosed SET changes;
the disclosed COUNT does not. K2/N = 3373/16384 under either placement, so the applicable
no-information ceiling (1 − K2/N) × 31/32 = 0.7693119049072266 is placement-invariant, and
any in-band reading is attributable to placement alone. Hazard is a property of the frozen
table (decision-log 2026-09-20 geometry mining: hazard sha identical across A/B/O; orders
only choose disclosed positions), so the hazard ranking is deterministic given the frozen
table and the truth feed — no RNG beyond table construction.

**Differ proof (vs all four proven-pointless points).** vs G3 — placement only (N, K
amounts, channel identical); vs X16 — N (16384 vs 32768) plus placement; vs X14/X15 — all
axes. No proven point is re-asked: the first-natural reading at this exact triple already
exists (G3, seeds 2026092501..2508) and is NOT re-run inside C-P1; C-P1 runs the
hazard-ranked placement only, on fresh seeds.

### 1.2 G1 mismatch band [0.05, 0.719] — derivation (recorded scalars only)

- Applicable no-information ceiling at the C-P1 triple (disclosed):
  (1 − K2/N) × 31/32 = (1 − 3373/16384) × 0.96875 = (13011/16384) × 0.96875
  = 0.79412841796875 × 0.96875 = **0.7693119049072266 ≈ 0.76931** (identical to X16/G3 by
  ratio construction; placement-invariant per §1.1).
- Recorded ceiling-hugging noise (max |Δ| vs applicable ceiling): X14 +0.00028,
  X15 −0.00012, X16 −0.00030, G3 +0.00099 → recorded max |Δ| = **0.00099** (G3 is the
  worst recorded point; the earlier 0.00030 record predates G3).
- Derivation rule (carried verbatim from FREEZE_DRAFT §1): high edge = applicable
  ceiling − M with M ≥ 50 × recorded max |Δ| = 50 × 0.00099 = **0.0495 minimum**; low edge
  ∈ [0.03, 0.10] with a stated floor rationale.
- PROPOSED (B3 confirms or re-derives): M = 0.05 ≈ 50.5× the updated noise (satisfies the
  0.0495 minimum). High-edge candidates: 0.7693119049072266 − 0.0495 = 0.7198119049072266
  ≈ 0.7198; 0.7693119049072266 − 0.05 = 0.7193119049072266 ≈ 0.7193. Frozen high edge
  **0.719** — conservative truncation below both candidates. Low edge **0.05** carried:
  X17-P proves 0.000 reachable, so ≤ 0.05 leaves no room for any downstream list gain.
- Stop semantics (carried): mismatch > 0.719 → ceiling-hugging repeat → stop, no repair,
  no tuning (X16/G3 precedent). Mismatch < 0.05 → near-floor/degenerate reading, no repair;
  interpretation per §5. Clarifying clause (F2): a sub-0.05 reading labeled
  `BR_STOP_SANITY_LOW` is recorded descriptively and execution PROCEEDS — the probe completes
  its seed sequence and pools per-seed values, and the retire-or-re-ask-once disposition is
  applied at §5 within budget; the token names the reading, not an execution halt, so the
  implementer must not halt the probe on a low reading.

---

## 2. Wiring gates carried (must be green before any band reading counts)

- **G2 (ranking-wiring floor, FROZEN carry-over): Q1b non-spike L8 survival ≥ 0.50** —
  identical decoder-free ranking machinery + sharper channel (d=0.90 ⇒ ≈0.90 capture
  expected) ⇒ X15/X16 rationale holds a fortiori; 0.50 stays a loose wiring floor.
  Violation → `BR_STOP_WIRING`.
- **G3 (spike-fraction band, FROZEN carry-over): [0.02, 0.70]** — population arithmetic at
  this scale: 8 blocks × 16384 = 131072 L2 positions; lower 0.02 ⇒ ≥ ~2.6k spike positions
  (bin×L cells populated); upper 0.70 ⇒ non-spike reference ≥ 30% (reference fraction
  stable). Violation → `BR_STOP_SPIKE_DEGENERATE` (strata unpopulated; no repair).
- **Q2 null-with-reason rule (FROZEN X16 rule):** Q2 (F-median8 vs mean-hazard) asked only
  if mismatch variance exists; mismatch < 0.005 over 131072 positions → null-with-reason
  per X14-review precedent while Q1/Q1b proceed.
- A wiring failure is a wiring stop, not an axis reading; it does not consume the per-axis
  probe budget (design (c) 1).
- **Stop tokens (SCLW_STOP_* family renamed B-route):** `BR_STOP_SANITY_HIGH` (G1 high),
  `BR_STOP_SANITY_LOW` (G1 low / degenerate — descriptive reading, NOT an execution halt,
  see §1.2), `BR_STOP_WIRING` (G2),
  `BR_STOP_SPIKE_DEGENERATE` (G3), `BR_STOP_IMPOSSIBLE` (disclosed truth without support),
  `BR_STOP_SC_CONSISTENCY` (sc re-encode self-check; body plan below),
  `BR_STOP_PROTECTED_OPEN` / `BR_STOP_WRITE_OUTSIDE` / `BR_STOP_NONFINITE` /
  `BR_STOP_PREREG_MISMATCH` / `BR_STOP_SEED_GREP` / `BR_STOP_SIZE` (generic; write scope is
  probe-root-only `workspace/probes/b1-placement-hazard-ranked/`; evidence ≤ ~2 MB).
  Execution-error-only single recorded rerun (Tier-X rule).
- **Body-plan carry (F1):** the B4 body is built from the G3 body template and re-runs the
  frozen `sc.py` decode path verbatim, so the re-encode self-check is carried as
  `BR_STOP_SC_CONSISTENCY` at the same 3 raise sites as G3's `SCLW_STOP_SC_CONSISTENCY`
  (full-block sc re-encode; small-block sc re-encode; list re-encode) — rationale: the B4
  body re-runs the frozen `sc.py` path; G3's self-check must not be silently lost.

---

## 3. Probe root + 3-line prereg (verbatim candidate for the probe-root prereg.md)

Probe root: `workspace/probes/b1-placement-hazard-ranked/` — probe-root-only writes.
Target-output absence verified this session: no such root exists (probes listing shows 26
legacy roots, none `b1-*`).

1. Question: at the G3 triple reused verbatim (N=16384, K1=167 first-natural L1 true-u1
   conditioning, K2=3373 L2 forced-correct with disclosure placement = hazard-ranked
   F-median8 descending rank instead of first-natural, d=0.90 X15-shape synthetic channel),
   does greedy-SC pooled mismatch fall inside the frozen G1 band [0.05, 0.719] — i.e. does
   disclosure placement alone produce a bite where first-natural placement ceiling-hugged
   (G3 0.770302) — with populated spike strata; per-seed values then pooled
   mean/sample-std(n−1)/range over 8 seeds; descriptive only, no FER/reliability/
   efficiency/branch-superiority claims, no pass/fail verdicts, SCL stays locked, zero
   real-data contact.
2. Parameters: N=16384 q=32 alpha=2 poly37 chunk_rows=512 floor 1e-15; channel d=0.90 /
   8-neighbor share 0.09 (0.01125 each) / rare96 pre-floor 0 / rest share 0.01
   (≈1.0881e-5 each) / C8-90pct shape; K1=167 K2=3373 hazard-ranked L2 (F-median8
   descending, tie-break ascending; L1 first-natural); table-label 2026092600 (identity
   only, zero table RNG), working-point blocks 2026092601..2026092608 ×1 block (131072 L2
   positions); G1 mismatch band [0.05,0.719] with BR_STOP_SANITY_HIGH/LOW, G2
   Q1b-nonspike-L8 ≥0.50, G3 spike [0.02,0.70], margin 2.0 bits, bins
   [2,4)/[4,8)/[8,inf)+nonspike_ref, R=8 F-median8; Q2 null-with-reason if mismatch <0.005
   over 131072 positions; ceiling (placement-invariant) 0.7693119049072266;
   decoder_calls=8, rng_calls recorded, tag_calls=0.
3. Command: `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export
   OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 &&
   timeout 120 .venv/bin/python workspace/probes/b1-placement-hazard-ranked/body.py` —
   frozen command core `timeout 120 .venv/bin/python
   workspace/probes/b1-placement-hazard-ranked/body.py`; local `.venv` absent at authoring
   time, so sibling-venv substitution `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
   is PRE-AUTHORIZED for the single execution and must be recorded in `results.json` plus
   the operator command_note (G3 precedent); bare python/python3 never used;
   execution-error-only single rerun max, recorded. Timeout estimate: 8 SC ≈ 25–40 s (P20S
   anchor ≈ 7.0 s/SC at N=32768 → est ~3 s/SC at N=16384) plus table/hazard overhead;
   120 s ≈ 3–4× headroom; estimates only, no new risk class.

---

## 4. Seed range — fresh proposal + grep proof (reserved-NOT-activated)

Band 2026092600..2026092619 was reserved-but-unactivated at scoping (planner grep clean
2026-09-20); this freeze draft confirms the same band — no new band is opened.

| Role | Seeds |
|---|---|
| table-identity master (label only, deterministic table ⇒ zero table RNG) | 2026092600 |
| C-P1 working-point blocks (8 seeds × 1 block) | 2026092601..2026092608 |
| axis-(i) reserve (successor probe within budget, if ever needed) | 2026092609..2026092616 |
| tag-master reserve (UNUSED; tag_calls: 0) | 2026092617 |
| spares | 2026092618..2026092619 |

Avoided (occupied, never reused): X14 2026092350..2357, X15 2026092369..2377,
X16 2026092380..2388, X17 2026092390..2399, P20T 2026092400..2407 / 2410..2413,
P20S 2026092360..2367, SCL-gate reserved 2026092500..2519 (G3 used 2026092501..2508
working-point + 2026092509..2516 ladder reserve — confirmed in the G3 probe-root prereg),
test-local 2026092701..2026092703 (`comparison_bench/tests/test_nbpolar_scl.py`), and all
20260923xx..20260925xx.

**Grep proof (this session, read-only; decoders never run):** pattern `20260926`
repo-wide → 11 hits, ALL of them reservation lines in the scoping record itself
(`NBPOLAR-L2-REPRESENTATION-REDESIGN/STATUS.yaml:34-40`, `SCOPING_NOTES.md:35-36`,
`openspec/changes/l2-representation-redesign/proposal.md:96,140`) — zero hits in
`workspace/probes/`, any `*.py` body, `results.json`, tag files, or any other directory.
Occupied bands confirmed present in tracked records (X17 packet + tests; P20T packet; G3
probe-root prereg 2026092501..2508 / 2026092509..2516; test-local 2701..2703).
Grep-scope note: the search tool respects .gitignore, so gitignored worktree-only roots
under `workspace/probes/` were additionally verified by directory listing (no `b1-*` root)
and by direct read of the G3 prereg (2500s occupancy). A non-ignoring full grep is part of
the B3 freeze checklist; reservation alone authorizes nothing and re-grep is REQUIRED at
B3 before activation.

**Grep commands for the B3 freeze (copy-paste; read-only, decoders never run):**

```bash
# 1. Proposed-band absence outside this packet dir (expect: zero hits)
grep -rn "202609260[0-9]\|202609261[0-9]" workspace/ comparison_bench/src/ tools/ experiments/ results/ comparison_bench/outputs_comparison/ docs/ openspec/ 2>/dev/null; echo "exit=$?"
# 2. Full-band audit incl. packet docs (expect: ONLY L2-REPRESENTATION-REDESIGN reservation lines)
grep -rn "20260926" --exclude-dir=.git --exclude-dir=.venv . 2>/dev/null
# 3. Root-name absence (expect: zero hits)
grep -rn "b1-placement-hazard-ranked" --exclude-dir=.git --exclude-dir=.venv . 2>/dev/null
```

---

## 5. Decision rule for the axis outcome (applied at B8 by the main thread)

- **INFORMATIVE (in band):** mismatch inside [0.05, 0.719] with G2/G3 wiring green → axis
  (i) has produced a working point with disclosure bite from placement alone (attribution
  via the placement-invariance property, §1.1). Hands to: the next ranked question within
  axis (i) (placement variant refinement) or amount/structure tiering at the chosen
  placement (C-P2, axis ii); and the point to the SCL track as a re-freeze CANDIDATE — its
  own G1 freeze plus explicit user authorization; never automatic.
- **RETIRE-ceiling (above high edge):** mismatch > 0.719 → ceiling-hugging repeat at
  hazard-ranked placement too → record the reading, retire axis (i), forced switch to axis
  (ii) (C-P2 candidate at the same triple). No in-packet amendment to chase a bite (G3
  precedent).
- **DEGENERATE (below low edge):** mismatch < 0.05 → near-floor; record descriptively; if
  the downstream question is list gain, note the degenerate gap; the axis may be retired or
  re-asked once within budget.
- **Max-2-probes-per-axis rule (design (c) 1):** a probe that stops on wiring/sanity does
  not consume the axis budget; a probe that produces a readable in-band or out-of-band
  mismatch does. If axes (i), (ii) and (iii) all retire within budget (≤ 6 probes total on
  this route), the route FORCES a return to the user-owned exhaustion decision (redesign
  exhausted / data acquisition / closeout); the route may not silently extend.
- Whatever the outcome: no FER/reliability/efficiency claim; no real-data follow-on; SCL
  lock status explicitly re-stated (`scl-synthetic-list-gate` track untouched, G0–G6 NOT
  AUTHORIZED); Q5 disposition recorded — Q5 activates as this route's first Tier-X probe
  only if axis (iii) is selected; C-P1 is axis (i), so Q5 stays retired-conditional.

---

## 6. Standing constraints carried (binding, not re-litigated)

- Tier-X rules verbatim: probe-root-only writes; 3-line prereg frozen before the run;
  per-seed values + pooled mean/sample-std(n−1)/range; evidence size ≤ ~2 MB
  (`results.json` scalar-only, est. < 100 KB); milestone-batched ledger/memory/index
  updates; never-stage guard for `*.bin`, raw-data artifacts, and anything under
  `results/` / `comparison_bench/outputs_comparison/`.
- No production-module merge: `sc.py` and all `formal_ir/nbpolar/` existing modules stay
  untouched (frozen baseline; read-only import only); disclosure placement is a caller-side
  truth-injection choice (D1/D2 semantics of X16 §2 carried verbatim at the new K); zero
  protected opens; zero data contact.
- Proven-pointless carry-over: X14 (flat/N=256), X15 (d=0.75/N=256), X16 (d=0.75/N=32768
  first-natural), G3 (d=0.90/N=16384 first-natural) are never re-asked; add-N is barred by
  the strategy stop rule.
- Prior rule unchanged: raw-count MLE + 1e-15 floor for target-channel priors; λ stays
  control-arm only (X08 disposition).
- Small-task fast path NOT claimed: an axis freeze plus probe body needs the full
  B3..B8 gate sequence.

---

## NOT-AUTHORIZED footer (binding)

**This draft authorizes NOTHING.** No working-point numbers are frozen, no band is frozen,
no disclosure set is frozen, no seeds are activated, no probe body is created, no test is
run, no execution is permitted. B3 freeze review (independent review of this packet:
differ-from-all-proven-pointless proof, ceiling-margin arithmetic re-shown, disclosure-set
freeze, seed/tag grep proof, 3-line prereg text, stop tokens) plus explicit user
authorization (B4) are still REQUIRED before any implementation or execution. `sc.py`
stays frozen untouched; zero real-data contact; every gate in `design.md` (d) stays NOT
AUTHORIZED. SCL stays locked.
