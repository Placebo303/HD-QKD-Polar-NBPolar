# Geometry-archive mining report — P20S/R1 uncapped full-block hazard geometry (n=1 block, N=32768)

| item | value |
|---|---|
| run root | `workspace/geometry/58503bc3-0306-45b0-b70c-2599aaf82820/` |
| branch | `codex/nbpolar-phase0` |
| authorization | STANDING PRE-AUTHORIZATION 2026-09-20 (analysis-only branch, option A) |
| mode | analysis-only, read-only; no decoder, no protected opens |
| protected ruling (recorded) | Main-thread ruling: IR-5 `.bin` BYTE contents are PROTECTED — not opened, statted, or parsed. Manifest-level evidence only (`ir5_full_manifest.json`: sha/size/shape/`ir5full-v1` linkage) plus scalar + IR-1..IR-4 fields already present in JSON |
| counters | decoder_calls 0, rng_calls 0, tag_calls 0, protected_opens 0 |
| scope | descriptive only; no FER/reliability/efficiency/threshold-verdict language; `test_evidence_package.py` never run; no commit/push; writes only under the run root |

## 0. Inputs used (all read-only, none executed)

| file | role |
|---|---|
| `.workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m/aggregate_summary.json` | IR-1..IR-4 scalars, per-arm aggregates, integrity flags |
| `.../per_block_arm_outcomes.jsonl` (3 rows) | per-record scalars incl. fail-site fields, histograms, top-16 lists |
| `.../ir5_full_manifest.json` | manifest-level IR-5 evidence (sha/size/shape/linkage only) |
| `.../frozen_plan.json` + `input_and_predecessor_identity.json` | frozen orders, alt digest, set-delta, K literals |
| `.../report.md` | accepted-descriptive packet record |
| P20N/P20O/P20Q/P20R `report.md` + `per_block_arm_outcomes.jsonl` | continuity framing (L2-fail census, order-derivation rules) |
| `workspace/h2/497eecf4-d060-42a2-a862-49e8059590b7/` (summary + h2e table) | predecessor numbers (H2 v2), cited as context only |
| NEXT-PHASE-PLAN §§1–4 | §3 trigger criterion + option (iv) design reference |

## 1. Order-independence finding (manifest-level)

| arm | hazard series sha256 | in-prefix mask sha256 | in-U mask sha256 | order digest | order |
|---|---|---|---|---|---|
| A anchor frozen | `ef4398d3…28563` | `9e9f5e98…ad28a` | `c3502047…890479` | `b2255449…0906` | frozen |
| B spike-local | `ef4398d3…28563` | `cf75440d…6830e` | `bf4e871b…18769f` | `139f34c3…1864` | spike-local (`F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8`) |
| O oracle | `ef4398d3…28563` | `9e9f5e98…ad28a` | `c3502047…890479` | `b2255449…0906` | frozen |

| manifest fact | value |
|---|---|
| hazard file shape/bytes per arm | 32768 positions, 131072 bytes (`<f4` LE), format `ir5full-v1`, uncapped full-block |
| mask file shape/bytes per arm per domain | 32768 positions, 32768 bytes (`u1`) |
| hazard bytes A vs B vs O | identical (shared sha) |
| in-prefix mask A vs O | identical; B differs |
| in-U mask A vs O | identical; B differs |
| alt construction digest (all arms) | `98e25495…5fb5` (frozen α1) |
| disclosed-set delta A vs B | `|A−B| = |B−A| = 1599` (1599/6746 = 23.70% swapped), size-delta 0 |

Descriptive implication: hazard values are a property of the frozen α1 table alone — reordering changes no position's hazard. The orders change only which 6746 positions fall inside the disclosed prefix. The "which positions to disclose" question is therefore purely a selection problem over a fixed hazard landscape.

## 2. Disclosed-set composition (H2e mechanism question at n=1)

| IR | A anchor frozen | B spike-local | O oracle |
|---|---|---|---|
| IR-1 prefix mass / outside mass | 6746 / 26022 | 6746 / 26022 | 6746 / 26022 |
| IR-1 share of block disclosed | 20.587% | 20.587% | 20.587% |
| IR-1 prefix tail-8 mass | 0 | 0 | 0 |
| IR-3 above-lo (1.0× prefix mean) | 1641 (24.326%) | 1651 (24.474%) | 1641 (24.326%) |
| IR-3 above-hi (2.0× prefix mean) | 1641 (24.326%) | 1651 (24.474%) | 1641 (24.326%) |
| IR-3 prefix mean (thresh-lo, bits) | 0.8740592319509212 | 0.8768295338061611 | 0.8740592319509212 |
| IR-4 top-16 in-prefix count | 0 | 0 | 0 |

| observation | detail |
|---|---|
| prefix-mean shift B−A | +0.002770301855239965 bits (swapping 23.70% of disclosed positions barely moves the prefix mean or histogram shape) |
| above-threshold delta B−A | +10 positions |
| lo==hi counts on every arm | prefix histogram has zero mass in bins 40–45 (~0.615–1.652 bits); the 1.0× and 2.0× prefix-mean thresholds select identically |
| above-threshold cluster location | bins 46+ (high-hazard cluster: A 340+1266+30+1+1+3 = 1641; B 331+1285+29+1+1+4 = 1651, exact match to IR-3) |
| top-16 hazards (bits) | 9.0768–9.2784 (≈10.38–10.62× the prefix mean), coords identical on all arms |
| fail-site hazard vs tail | 0.513 bits ≈ 1/18 of the top-16 minimum; fail site sits below the prefix mean |

IR-4 top-16 (identical coords/hazards on A, B, O; in-prefix false on every arm):

| rank | coord | hazard (bits) | A in-prefix | B in-prefix | O in-prefix |
|---|---|---|---|---|---|
| 1 | 22700 | 9.278449458220482 | false | false | false |
| 2 | 16973 | 9.259743263690781 | false | false | false |
| 3 | 10863 | 9.255028569818728 | false | false | false |
| 4 | 17904 | 9.236014191900082 | false | false | false |
| 5 | 31267 | 9.233619676759703 | false | false | false |
| 6 | 20424 | 9.214319120800766 | false | false | false |
| 7 | 7721 | 9.197216693110052 | false | false | false |
| 8 | 17541 | 9.189824558880018 | false | false | false |
| 9 | 14729 | 9.167418145831736 | false | false | false |
| 10 | 32760 | 9.162391328756904 | false | false | false |
| 11 | 30358 | 9.157346935362844 | false | false | false |
| 12 | 29465 | 9.14720492494223 | false | false | false |
| 13 | 14092 | 9.14210705730255 | false | false | false |
| 14 | 18750 | 9.129283016944965 | false | false | false |
| 15 | 29382 | 9.08480838780436 | false | false | false |
| 16 | 8921 | 9.07681559705083 | false | false | false |

Descriptive reading: the disclosed prefix covers ~1/5 of positions concentrated at low hazard; 16/16 (100%) of the most-hazardous positions are undisclosed under both orders; the single fail site is a below-prefix-mean, mid-rank position while the entire hazardous tail sits outside the disclosed set.

## 3. Fail-site anatomy (single B failure)

| field | B value (P20S block 0) |
|---|---|
| first-error layer / coord | L2 @ coord 0 |
| fail hazard | 0.5131718176531462 bits |
| IR-2 rank pct | 0.432220458984375 (mid-rank; 0.4322×32768 = 14163) |
| fail-to-prefix-mean ratio | 0.5131718176531462/0.8768295338061611 = 0.5852583630772091 (reproduces H2 v2 `H2b_new_r_fail` exactly) |
| fail nbhd mean | 0.6992590731236983 bits |
| in-prefix / in-U-domain | false / false (outside disclosed prefix under both flags) |
| floor rate B vs A/O | 0.371734619140625 (24362 hits) vs 0.0002593994140625 (17 hits), ratio ≈1433× |

Archive L2-fail census (`first_error_layer == L2` in each packet jsonl):

| packet | L2 fails | out-of-prefix (`l2_fail_in_prefix=false`) | notes |
|---|---|---|---|
| P20N (1.5M, shared frozen order) | 14 | 2 (B_alt operational + D_alt oracle, same block) | no IR-2 ranks recorded |
| P20O (2M VAL, shared frozen order) | 11 | 0 | — |
| P20Q (2M HOLD, shared frozen order) | 12 | 0 | all in-prefix true; IR-2 n=12 median 0.8830413818359375 |
| P20R (1.5M VAL-remainder, frozen-A vs hazard-rank-new-B `c7853286…`) | 4 | 2 (B + D new-order) | B: coord 0, both flags false, hazard 0.5154976810580554, rank 0.329193115234375 |
| P20S (2M merged, frozen-A vs spike-local-B) | 1 | 1 (B spike-local) | this report |
| archive total | 42 | 5 (3 operational + 2 oracle) | — |

| framing statement | basis |
|---|---|
| P20S-B is the 3rd operational out-of-prefix L2 fail archive-wide (5th including oracle) | P20N-B, P20R-B, then P20S-B; oracle out-of-prefix: P20N-D, P20R-D |
| P20S-B is the 1st L2 fail on a spike-local order | P20N-B shared the frozen order (alt-construction packet); P20R-B used a hazard-descending rank order, not a spike-local formula |
| nearest archive neighbor is P20R-B | coord 0, both domain flags false, ~0.51-bit hazard, low-mid rank — but different session (1.5M vs 2M), K (331/6689/7020 vs 334/6746/7080), alt table, and order rule: descriptive parallel only, never pooled |

What this single site can support: a recorded existence case — under the spike-local order, the first error occurred at an undisclosed below-mean mid-rank position with a large floor-hit count on the candidate path, while the top-16 tail stayed undisclosed on all arms.

What it cannot support (n=1, no baseline at this packet): any comparison between orders (one paired A-exact/B-fail draw gives no discrimination); whether the floor-rate elevation is typical of spike-local orders or specific to this draw; whether disclosing tail positions or list decoding would change the recorded outcome (neither was executed).

## 4. What the archive still cannot answer

| # | unanswered question | why blocked | what would unblock (option) |
|---|---|---|---|
| L1 | Does any spike-local selection outperform the frozen order? | n=1 paired draw (A exact / B fail); P20R n=1 block all-fail: no discrimination | multi-block evidence or rescoped operating point — main-thread decision ((iv), (i), or (v)) |
| L2 | Is the undisclosed top-hazard tail decodable if disclosed? | no operating point has ever disclosed those positions (IR-4 0/16 under every order) | disclosure-placement move = option (i) |
| L3 | Would list (SCL-family) decoding change any real-data outcome? | all real-data runs SC-only; X14/X15 are synthetic probes | list-decoder execution — outside the scoped (iv) design |
| L4 | Is the B floor-rate elevation (0.3717 vs 0.0002594) typical of spike-local orders? | single draw; floor counts are path-dependent | repeated draws under spike-local orders |
| L5 | Does the spike-local fail-site pattern persist off N=32768? | zero reduced-N real-data evidence | option (iv) N=8192 2M-tail probe |
| L6 | Are the prefix empty-band / mid-rank-fail features general? | single merged block | further blocks (none remain at N=32768 under the old rule) |

## 5. Trigger evaluation for the NEXT-PHASE-PLAN §3 criterion (option (iv) justification)

Criterion: mining yields a NAMED mechanism question that is (a) unanswerable from the archive AND (b) testable at reduced N without needing a cross-N baseline.

| named question | (a) unanswerable from archive? | (b) testable at reduced N, no cross-N baseline? |
|---|---|---|
| Q-G1: does the spike-local L2 fail-site pattern (first error at an undisclosed below-mean coord-class site with floor-rate elevation, paired against the frozen order) recur at N=8192 on the 2M HOLD tail? | yes — zero N=8192 real-data evidence (L5) | yes — the (iv) design is a within-N=8192 paired frozen-vs-spike-local comparison on the 2M tail block (50 frames → 1 block + stub); it compares arms within N=8192, never N=8192-vs-N=32768 |
| Q-G2: does a spike-local order disclose more top-hazard-tail mass than the frozen order at the same N? | yes — at N=32768 the swap moved the prefix mean by +0.00277 bits and IR-4 stayed 0/16 on both orders | yes — answerable inside (iv) from the re-derived N=8192 α1 table + order set-delta + IR-1..IR-4 geometry at N=8192 alone |

Trigger verdict: YES. Q-G1 (primary, mechanism persistence) and Q-G2 (secondary, reselection geometry) jointly satisfy (a)+(b). This justifies option (iv) subject to its own gates (P16-scale OpenSpec change + fresh freeze + explicit user authorization; touches real data and production code paths).

Honesty caveat: (iv) yields a single N=8192 block (n=1) — a persistence probe, not statistical discrimination. L1–L4 and L6 remain unaddressed by (iv); L2 explicitly requires option (i), not (iv).
