# Design: L2 Representation & Disclosure-Placement Redesign (scoping only — nothing authorized)

All gates below are `NOT AUTHORIZED`. This design freezes selection rules, an axis ranking,
and a decision procedure; it freezes NO working-point numbers, NO disclosure sets, NO prior
structures, NO seeds.

## (a) Redesign axes — explicitly enumerated and ranked

Ranking criterion: information per unit of change, given the recorded evidence. Lower rank =
tried first. The list-decoding question is NOT an axis of this change; it is a downstream
option (rank 4) that stays locked.

1. **Axis (i) — Disclosure PLACEMENT change (hazard-ranked vs first-natural). RANK 1.**
   - What moves: WHICH L2 positions receive forced-correct disclosure, not how many. Placement
     is a caller-side truth-injection choice (D1/D2 semantics carried from X16 §2 /
     FREEZE_DRAFT §1); never a `sc.py` change; zero production edits.
   - Why legitimate now: hazard-ranked placement was deferred at the SCL freeze
     (FREEZE_DRAFT §1 item 2 — "no recorded signal justifies spending the freeze for
     placement", citing the qualitative X17 A4randomK 0.75293 vs A4rev 0.75879/0.95690 note).
     The deferral condition has since been met by recorded evidence: first-natural placement
     ceiling-hugs at BOTH tested channel strengths (X16 d=0.75 |Δ| 0.00030; G3 d=0.90
     |Δ| 0.00099 → `SCLW_STOP_SANITY_HIGH`), and real-data L2 fails concentrate in the
     undisclosed region (P20Q: 12/12 L2 fails natural-in-prefix but U-domain-out; IR-4 top-16
     in-prefix 0/48 — the disclosed prefix covers the low-hazard tail while the dangerous tail
     stays undisclosed, recorded as descriptive geometric observation only).
   - Cost: minimum. Same channel, same N, same K amounts; only the disclosed-position set
     changes. Hazard ranking reuses the FROZEN F-median8 local-spike formula
     (`h[i] − median(W8(i))`, tie-break ascending, decision-log 2026-09-20 addendum) and the
     frozen hazard atom (base-2 `h_j = -log2 p2[u1_cond_j, b_j, u2_true_j]`).
2. **Axis (ii) — Disclosure AMOUNT / STRUCTURE change (non-contiguous prefix, tiered). RANK 2.**
   - What moves: how much L2 disclosure and in what structure (contiguous first-K prefix →
     tiered sets, e.g. a hazard-ranked tier plus a spread tier; non-contiguous support).
   - Evidence it can bite: P20C (real DEV, descriptive) — +1024 L2 disclosure under the frozen
     order restored the base-failed block (B1 3/3 vs B0 2/3), the first positive DEV signal
     for the information-insufficiency hypothesis. But X16/G3 show that first-natural AMOUNT
     at full scale gives no synthetic bite, so amount alone (same structure) is the weaker
     single factor; amount is moved together with structure or after placement.
   - Cost: moderate. Caller-side only, but tier definitions and their interaction with the
     hazard ranking need freezing.
3. **Axis (iii) — L2 channel / prior MODEL change (structured prior re-estimation, Q5
   TRAIN-counts input). RANK 3.**
   - What moves: the L2 representation itself — the per-column channel model structure and the
     prior re-estimation recipe (still raw-count MLE + 1e-15 floor as the canonical rule; λ
     stays control-only). The Q5 queue item (TRAIN counts structure probe) is the natural
     first Tier-X probe of this axis.
   - Evidence it matters: L1 truth-mass ~0.10–0.15 vs ~0.28 needed (G1 L1 discriminator);
     L2 unrecovered at f=1.0 even at oracle 1/16 (D7-C); incumbent-metric spikiness reads
     (P20N: alt metric has HIGHER average prefix hazard yet restored a block; floors
     exonerated in-run). A structured prior that suppresses spurious conditional spikes could
     move the operating point in a way neither placement nor amount can.
   - Cost: highest of (i)–(iii). Touches the model, not just the caller; needs the Q5 probe
     before any channel-structure freeze; must not silently promote NB-LDPC graph / Cascade /
     binary-Polar logic (AGENTS.md §0) — only q-ary NB-Polar-native structures.
4. **Axis (iv) — List decoding (SCL) as a DOWNSTREAM OPTION ONLY. RANK 4 (not an axis of this
   change).**
   - SCL stays locked. `scl.py` exists (G2 commit `dba4f42f`) but is locked; the
     `scl-synthetic-list-gate` track stays frozen at its own gates. Only after (i)–(iii)
     produce an informative operating point does an SCL re-freeze become a legitimate
     proposal — via the SCL track's own G1 + explicit authorization. No automatic promotion.

## (b) Synthetic working-point rules

### Proven-pointless configurations (never re-asked)

| Probe | N | Disclosure passed to SC | Channel | Outcome |
|---|---|---|---|---|
| X14 | 256 | none (K2_synth=52 for pm/K only) | flat Dirichlet | mismatch 0.96903 ≈ chance 0.96875 |
| X15 | 256 | none (prefix first 52) | 0.75 diagonal | mismatch 0.96863; G1 stop |
| X16 | 32768 | K1=334 + K2=6746 first-natural forced-correct | 0.75 diagonal | mismatch 0.76902 ≈ ceiling 0.76931; STOP |
| G3 | 16384 | K1=167 + K2=3373 first-natural forced-correct | 0.90 diagonal | mismatch 0.770302 > high edge → `SCLW_STOP_SANITY_HIGH` |

Any new synthetic working point MUST differ from ALL FOUR. Re-asking survival at any of these
exact triples is proven pointless (decision-log closeout); "add N" is barred by the strategy
stop rule (proposal).

### Minimum-delta candidates

- **C-P1 (axis i, MINIMUM DELTA — freeze candidate):** reuse the G3 triple verbatim —
  N=16384 (14 polarization levels), K1=167 / K2=3373 (exact-ratio halving of the 2M literals
  334/32768, 6746/32768; zero rounding), d=0.90 X15-recipe shape verbatim — and move ONLY
  the L2 disclosure placement from first-natural to hazard-ranked (F-median8 order).
  Differences: vs G3 (placement), vs X16 (N + placement), vs X14/X15 (all axes).
  **Single-factor property:** placement does not change K2/N, so the applicable ceiling
  arithmetic is unchanged and any in-band reading is attributable to placement alone.
- **C-P2 (axis ii, successor if C-P1 retires):** same triple; K2 restructured into tiered /
  non-contiguous sets (hazard-ranked tier-1 + spread tier-2) at equal total K2 — differs from
  all proven points on structure while holding N, channel, and amount.
- **C-P3 (axis iii, successor / parallel if Q5 activates):** same triple; structured prior
  re-estimation from TRAIN counts per the Q5 reading — differs on the model axis.

C-P2/C-P3 are named for continuity only; the freeze selects ONE candidate with its own
differ proof.

### Ceiling-margin arithmetic requirement (RECORDED scalars only)

- Applicable no-information ceiling at the C-P1 triple (disclosed):
  (1 − K2/N) × 31/32 = (1 − 3373/16384) × 0.96875 = (13011/16384) × 0.96875
  = 0.79412841796875 × 0.96875 = **0.7693119049072266 ≈ 0.76931** (identical to X16/G3 by
  ratio construction; placement-invariant).
- Recorded ceiling-hugging noise (max |Δ| vs applicable ceiling): X14 +0.00028,
  X15 −0.00012, X16 −0.00030, G3 +0.00099 → updated recorded max |Δ| = **0.00099** (G3 is
  now the worst recorded point; the earlier 0.00030 record predates G3).
- **Derivation rule (carried from FREEZE_DRAFT §1):** high edge = applicable ceiling − M with
  M ≥ 50 × recorded max |Δ| (currently 0.00099 → M ≥ 0.0495); low edge ∈ [0.03, 0.10] with a
  stated floor rationale. **PROPOSED band for C-P1: [0.05, 0.719]** (M = 0.05 ≈ 50.5× the
  updated noise; high edge 0.76931 − 0.05 = 0.71931; low edge 0.05 — X17-P proves 0.000
  reachable, so ≤ 0.05 leaves no room for any downstream list gain). Values are PROPOSED; the
  freeze confirms or re-derives with this arithmetic and must re-show it if amended.
- Stop semantics (carried): mismatch > high edge → ceiling-hugging repeat → STOP, no repair,
  no tuning (X16/G3 precedent). Mismatch < low edge → near-floor note, proceed descriptively.
- Wiring checks must pass before any band reading counts: ranking floor (Q1b non-spike L8
  survival ≥ 0.50, G2 shape) and spike-fraction band ([0.02, 0.70], G3 shape) — a wiring
  failure is a wiring stop, not an axis reading.

## (c) Decision procedure — how measurements pick the next axis

1. **Per-axis probe budget: max 2 synthetic Tier-X probes per axis before a FORCED axis
   switch.** A probe that stops on wiring/sanity (not an axis reading) does not consume the
   axis budget; a probe that produces a readable in-band or out-of-band mismatch does.
2. **Informativeness rules (applied per probe reading):**
   - **INFORMATIVE (in band):** mismatch inside [low, high] with wiring checks green → the
     axis has produced a working point with disclosure bite. Proceed within the axis to the
     next ranked question (e.g. placement variant refinement, or amount tiering at the chosen
     placement), and hand the point to the SCL track as a re-freeze CANDIDATE (its own G1 +
     authorization; no automatic promotion).
   - **RETIRED (above high edge):** ceiling-hugging repeat → the axis is non-informative at
     this triple; record the reading, retire the axis, switch. No in-packet amendment to
     chase a bite (G3 precedent).
   - **DEGENERATE (below low edge):** near-floor → record descriptively; if the downstream
     question is list gain, note the degenerate gap; axis may be retired or re-asked once
     within budget.
3. **Knee rule (axis ii only):** when tiered amounts are probed, knee = smallest disclosure
   increment whose marginal mismatch movement per increment falls below the freeze-set
   epsilon; increments beyond the knee are recorded, not spent.
4. **Retirement record:** each retired axis is recorded with its readings and the
   differ-from-proven-pointless proof of the configuration that retired it. Re-entry
   requires a NEW operating-point dimension, never a retry.
5. **Forced return:** if axes (i), (ii), and (iii) are all retired within budget (≤ 6 probes
   total on this route), the route FORCES a return to the user-owned exhaustion decision
   (redesign exhausted / data acquisition / closeout). The route may not silently extend.

## (d) Gate sequence (every item NOT AUTHORIZED)

1. `B1 proposal` — this change (proposal + design + tasks + skeleton). [NOT AUTHORIZED beyond scoping]
2. `B2 axis-selection decision` — main-thread decision of the FIRST axis and candidate
   (default C-P1; alternatives C-P2/C-P3; Q5 activates only if axis (iii) is chosen first).
   [NOT AUTHORIZED]
3. `B3 freeze review` — independent review of the frozen first-axis packet: selected candidate
   with differ-from-all-proven-pointless proof; ceiling-margin arithmetic re-shown at freeze;
   disclosure-set/prior freeze; seed/tag grep proof; 3-line prereg text; stop tokens.
   [NOT AUTHORIZED]
4. `B4 implementation authorization` — explicit user authorization to create the probe body
   (new files only; caller-side placement/amount injection; zero edits to
   `formal_ir/nbpolar/` existing modules; zero protected opens). [NOT AUTHORIZED]
5. `B5 focused tests` — T0/T1 green (placement-injection smoke: disclosed-set sizes exact;
   order-identity under shuffled `known_positions`; ceiling-arithmetic assert; gate asserts)
   + full NB-Polar suite green; path-refusal asserts. T2 at milestones only. [NOT AUTHORIZED]
6. `B6 single synthetic execution` — one frozen-command Tier-X run; probe-root-only writes
   (`workspace/probes/<id>/`); `results.json` scalar-only (< 2 MB) with per-seed values +
   mean/sample-std/range; `decoder_calls`/`rng_calls`/`tag_calls` recorded; zero protected
   opens; execution-error-only single recorded rerun. [NOT AUTHORIZED]
7. `B7 focused numerical review` — independent reviewer-go Tier-X review (commands,
   completeness, arithmetic, truth isolation, write scope). No Pre-EXECUTE/Pre-RESULT
   (Tier-X rule). [NOT AUTHORIZED]
8. `B8 acceptance + axis decision` — main-thread acceptance of descriptive readings; applies
   (c): in-band → next question / SCL re-freeze candidacy; out-of-band → retire + forced
   switch at budget; records Q5 disposition. No FER/reliability/efficiency claim; no
   real-data follow-on; SCL lock status explicitly re-stated. [NOT AUTHORIZED]

## (e) Interaction with the SCL track

- **SCL stays locked.** This change does not unlock, implement, extend, or re-freeze SCL; the
  `scl-synthetic-list-gate` track (G0–G6, all NOT AUTHORIZED) is untouched by this scoping.
- **B may produce the working point that justifies re-freezing SCL later.** If an axis
  (i)–(iii) probe reads INFORMATIVE per (c), that point becomes a candidate input to the SCL
  track's own G1 freeze — but promotion is never automatic: the SCL track needs its own
  freeze review + explicit user authorization, and the X14-style true-path top-L survival
  gate at frozen-hazard spikes remains the hard unlock criterion.
- **Converse:** a retired axis does not weaken SCL's closure record; X14→X17 + G3 stay
  recorded as non-informative at their operating points, not as an SCL negative.
- **Shared hygiene:** Tier-X rules carry verbatim (probe-root-only writes, 3-line prereg,
  per-seed + pooled stats, evidence-size ≤ ~2 MB, milestone-batched ledger/memory/index
  updates, never-stage guard for `*.bin`/raw/output roots).

## Rebuild-vs-reuse split

- Reusable read-only (never edited): frozen SC path (`sc.py` incl. `chunk_rows=512`, failure
  categories, tie convention); prior recipes (`derive_p1`/`derive_p2`,
  `build_p1_metrics`/`gather_p2_metrics`, `probs_to_symbol_metric`); FROZEN F-median8
  local-spike formula + hazard atom; transform/algebra (`polar_transform`, `make_gf32` poly 37,
  alpha=2); X14–X17/G3 prereg-body-results pattern; decision-log and packet records.
- New (this track only): probe body for the selected axis (channel/prior + disclosure
  placement/amount injection + paired measurement); axis-decision record; retirement ledger
  entries. New files live in new probe roots + the new packet dir; no existing production,
  evidence, ledger, or sibling-checkout file is modified.
