# NEXT single-factor branch proposal (proposal only — no implementation, no freeze, no execution)

- Status: DRAFT proposal for user decision. No packet freeze, no decoder, no data opens, no authorization.
- Frozen inputs read: P20Q `MAIN_THREAD_ACCEPTANCE.md` + `TASK_PACKET.md` §16 + §4 ledger;
  H2 `H2_ANALYSIS_PLAN.md` + `h2_final_adjudication.md` (run root
  `workspace/h2/504e036a-f040-4d88-88ba-152702f92ffd/`);
  decision-log H2 entry (`docs/decision-log.md` ~4839+); P20B `OPERATOR_RETURN.md` (bounded-search history only).
- Scope note: P20Q §16 auto-triggers did NOT fire (see §4). This proposal answers the held-open
  main-thread planning branch, informed by H2 (which "selects nothing" per decision-log).

## 1. Per-candidate evaluation (one paragraph each, descriptive only)

### (a) L2-order positions under the raw prior — FAVORED as next

The H2 number that most directly describes a position SET is H2e's IR-4 pooled in-prefix fraction
66/320 = 0.20625 (< 0.50 threshold): the top-16 hazard-ranked positions sit mostly OUTSIDE the
currently disclosed prefix, so the disclosed set misses recorded hazard mass under truncated scope
(first-4096 + top-16 + histogram). Alongside it, H2b (median fail/prefix ratio 2.2835, n=37) with
IR-2 median 0.883 (n=12) places fail sites in the hazard tail — a prefix that covered the tail would
be the coherent single change, with construction (α1), K1/K2, floor, and decoder all held frozen.
Tempering note (no verdict): H2c in-X 35/37 = 0.9459 says fail sites already lie inside disclosed X,
so the current set is not catastrophically misplaced; and H2a REFUTED (8/14 evaluable blocks
anomalous, strongest gap 0.097058 on P20N b3) warns that any re-ranking by AVERAGE hazard will not
order arms — the new order rule must target local-spike geometry, not the mean. Net: (a) is the only
candidate with a direct H2 position-set number behind it.

### (b) L2-side bounded search at the fixed disclosure point — DISFAVORED as next (defer)

H2b (median 2.2835, range 0.4713..10.3421) and H2d-flat (mean_abs_diff 0.002185, n=37 ≤ 0.05) are
compatible with local sensitivity probing — floor carries no signal, hazard spikes do — and H2e
incoherence (0.20625 vs IR-2 0.883) shows a static top-k does not mirror fail sites, which a bounded
local probe could explore without committing to a new global order. Against it as NEXT: bounded
search presupposes a neighborhood worth searching around the CURRENT point, while H2e 0.20625 says
the current point's position set is incoherent with fail-site geometry — searching around it is
premature until one alternate position set is tried. Recorded history (descriptive, different
session/operating point, not a verdict on this setting): P20B bounded-search diagnostic showed
`search_better_count` 0/3 with all arms 0/3 on 1M. Net: (b) stays a live later step after (a)
either way; it does not answer the H2e position-set question first.

### (c) Second single construction form — DISFAVORED as next (defer)

No H2 number specifically implicates the smoothing family: H2b/H2c implicate fail-site geometry
(spikes, in-X 35/37, out-of-U 23/23 on 2M segments), H2e implicates the position set (0.20625), and
H2a REFUTED (8/14 anomalous) holds under the CURRENT α1 form without isolating a family cure —
claiming another form would fix it is a verdict about an untested factor and is not made here.
The chain (P20N B 1/4 → P20O B 2/5 → P20Q B 4/5, all descriptive, zero disclosure delta by design)
shows the current α1 form still strengthening, and the §16 falsification trigger for abandoning it
(B maintains NONE and restores NONE with L2 persistence) did NOT fire (observed 4/5 restoration).
A second form now would confound construction×position attribution on a single block of fresh
population. Net: (c) remains deferred until (a) is resolved descriptively.

## 2. Recommendation (exactly ONE)

**Next single factor: (a) L2-order positions under the raw prior** — one alternate disclosed-position
rule derived from the reused raw prior, with α1 construction, K1/K2 sizes, floor 1e-15, and greedy SC
all frozen.

- Why this one first: it is the smallest change addressed to the sharpest H2 clue — fail sites are
  in-X (35/37) and hazard-elevated (median 2.2835), yet top-16 hazard mass sits mostly outside-prefix
  (pooled 0.20625). Order is the only candidate that moves the position set; (b) searches around a
  point H2e calls incoherent, and (c) replaces a form whose §16 falsification trigger never fired.
- Descriptive positive (no FER language): on the single fresh block, the new-order operational arm
  records exact while the frozen-order anchor arm records a non-exact L2-layer first error at a
  hazard-elevated in-X site — i.e., the A-fail→B-exact restoration pattern re-appears under a changed
  position set at identical K sizes.
- Descriptive negative (no FER language): both operational arms record non-exact with L2-layer first
  errors persisting at in-X sites, or the new-order arm records non-exact wherever the anchor does —
  i.e., the position-set change leaves the recorded pattern indistinguishable from the frozen-order
  baseline on this block.
- Either pattern resolves only the position-set question on one block; neither licenses any
  reliability, efficiency, or family claim.

## 3. Packet sketch (for the future frozen packet, not frozen here)

- Population (exact, 128-frame arithmetic, N=32768 = 128 frames × 256 rows):
  - 1.5M VAL remainder 2044..2212 = 169 frames (2212−2044+1). DEV = FIRST 128 frames 2044..2171
    (ONE full block: 128×256 = 32768 pairs). Stub 2172..2212 = 41 frames declared never-decoded.
  - 2M HOLD remainder 3556..3644 = 89 frames (3644−3556+1): 89 < 128 → ZERO full blocks; stays
    never-decoded (counted, never contacted beyond counting).
  - Consumed populations (P20N 1.5M HOLD DEV 2213..2724; P20O 2M VAL DEV 2187..2826; P20Q 2M HOLD DEV
    2916..3555; all §4 ledger entries) are fail-closed and supply no frames.
- Session consequence: scoring returns to the 1.5M session (VAL remainder), NOT 2M.
- Reuse-vs-derive stance: REUSE frozen 1.5M TRAIN-derived artifacts read-only with digest replay —
  `raw_prior_1p5m.npz` (digest `372dcc1c…cf7d46ac`), `raw_prior_orders_1p5m.json` (sha
  `a9f18a9f…1da11bc638`), K1/K2 331/6689 — zero new counts opens, zero new sampling (S2-i
  same-session rule). The ONLY derivation is the alternate L2-order position rule computed
  off-protected-data from the reused raw prior (derivation opens zero protected content; DEV content
  opens only at Stage B). S2-ii build⊂TRAIN vs DEV⊂VAL-remainder disjointness re-declared.
- New tag-domain rule: fresh tag master for the new packet (never reuse 2026092330/2026092280 or any
  prior master); per-arm 64-bit tags; tag-verified exactness as before (`exact` = outcome exact AND
  tag_pass AND label_match; `undetected` isolated, never success).
- Arm structure (order is the ONLY delta between operational arms):
  - A (anchor): alt-α1 construction + FROZEN 1.5M order positions (P20N continuity anchor).
  - B (test): alt-α1 construction + NEW raw-prior order positions (the single factor).
  - C/D: true-L1 oracles (diagnostic only, never merged into A/B).
  - K sizes frozen identical on all arms (K1/K2 331/6689): size-delta zero; the SET-delta between A
    and B position lists IS the factor, recorded byte-exact.
- Budget envelope class: single-block Tier-Y gate class — 1 block × 4 arms (SC/tag counts derived in
  freeze); wall/RSS envelope at or below the P20Q Stage-B class (single attempt, timeout-1200 class);
  zero disclosure-size delta; recording scope (nine scalars mandatory; IR-1..IR-5 presence decided at
  freeze — see open question 2).
- P20Q §16 trigger answered: NONE — explicitly, no auto-trigger fired. B-zero-maintain/L2-persistence
  required B restores NONE (observed B 4/5); B-maintained efficiency planning required a genuine
  maintain event (observed b_maintained 0, vacuous); L1-return required L1-layer operational errors
  (observed 12/12 L2 on P20Q). This proposal serves the held-open item-4 branch decision
  (efficiency/disclosure-minimality vs next-upstream-factor) with H2 as input.

## 4. Non-goals + stop rules

- Non-goals (explicitly out of scope): any FER/reliability/superiority/efficiency/key-rate claim; any
  α/floor/K/decoder/SCL change; any bounded search or second construction form; consuming the 41-frame
  stub 2172..2212, the 89-frame 2M HOLD remainder, or any consumed population; cross-session pooling
  (1.5M and 2M never mixed); full-block order claims beyond recorded scope; any overwrite under
  `results/` or `comparison_bench/outputs_comparison/`; commit/push by the operator.
- Stop rules (STOP with `NEXTBR_STOP_<REASON>`, no adjudication): DEV frame arithmetic ≠ 128/41 split
  or any stub-frame contact; any digest replay mismatch on reused 1.5M artifacts; any protected-content
  open during order derivation; any second-factor edit (construction/α/floor/K/decoder); disclosure
  size recount mismatch; `undetected` ≠ 0 anywhere or merged into success; oracle arms merged into
  operational aggregates; verdict/reliability language in packet artifacts; any write outside the new
  packet root. Execution-error rerun: 1 allowed max, recorded (identical inputs, never tuning).

## 5. Open questions for the user (max 3)

1. Population: confirm the single-block 1.5M VAL-remainder DEV (2044..2171, stub 2172..2212 never
   decoded) as the next gate, or hold for a fresh/larger never-decoded population instead?
2. Recording scope: full IR-1..IR-5 payload again on the single block, or nine scalars only (lighter
   packet, weaker H2-continuity)?
3. Anchor arm: A as alt-construction + frozen-order (pure order delta, proposed) or A as full
   incumbent (order+construction anchor, two deltas on B)?
