# H2a–H2e Main-Thread Analysis Plan (FROZEN, read-only, descriptive)

- Packet: `NBPOLAR-H2-ADJUDICATION-ANALYSIS` · main-thread analysis after P20Q acceptance.
- Tier: analysis only — NOT Tier-X probe, NOT Tier-Y gate. No decoder, no RNG, no tag, no protected open, no DEV/HOLD contact.
- P20Q accepted descriptive (commits d5c0afb + 1612c84b): 2M HOLD DEV 2916..3555 (5x128), A 0/5 B 4/5 C 0/5 D 4/5, 12 L2-fails natural-in-prefix but U-domain-out, IR-1..IR-5 complete 20/20, undetected 0, integrity 30/30.
- X10 baseline (`workspace/probes/nbpolar_x10_h2_scalar_adjudication/results.json`): H2a REFUTED, H2b SUPPORTED median 2.246 n=25, H2c SUPPORTED in-X 23/25 + P20O 11 out-of-U, H2d flat mean 0.0030, H2e NOT-DECIDABLE.

## Goal

Adjudicate H2a–H2e (L2 order/metric non-generalization: alt restores blocks despite higher CE / higher prefix hazard means) SOLELY from persisted worktree evidence — P20N (16) + P20O (20) nine-scalar rows plus P20Q (20) nine-scalar + IR-1..IR-5 rows — with X10 as the frozen scalar baseline. Emit descriptive SUPPORTED / REFUTED / NOT-DECIDABLE labels only in the final adjudication section. No FER, efficiency, leakage, key-rate, reliability, or promotion claim.

## Non-Goals

- No new decoder execution (SC calls 0), no RNG/tag calls, no protected parquet/NPZ opens/stats/listings (V25 counts, pairs parquet, 1M/1.5M/2M content — not even stat).
- No new DEV/HOLD contact, no new tag domains, no K/budget/order/alt recompute or hand-fill (K1/K2/K_total, budget literal, CE ratios replayed as literals only for identity checks, never recomputed as analysis inputs).
- No new tag domains, no construction/prior/order derivation, no SCL/new kernel/model/schema.
- No H2 verdict inside any sub-computation (H2a–H2e tables are descriptives only); verdicts ONLY in the final main-thread adjudication section.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push by the operator.

## Impact Scope

- Reads (worktree files only): the 8 frozen inputs in §1. Forbidden: everything else.
- Writes (additive only): ONE new run root `workspace/h2/<uuid>/` (primary; `<uuid>` fresh per run) with the §5 file set; this plan file itself. No other writes.
- Affects: main-thread H2 decision only. Touches no runner, no frozen evidence root, no OpenSpec specs (plan doc only; if spec text later needs change, separate OpenSpec change).

## Acceptance Criteria

- A1: operator recomputes every §3–§4 number from the §1 files with stdlib only; decoder/RNG/tag/protected-open counters all 0; wall/RSS recorded.
- A2: record counts P20N 16 / P20O 20 / P20Q 20 exact; P20Q IR-1..IR-5 present 20/20 with frozen caps/nullability; undetected 0 re-isolated (never merged into success); oracle arms C/D never merged into operational aggregates.
- A3: each H2 sub-table contains descriptives only (no verdict token); exactly ONE final adjudication file contains the five verdict tokens with the §4 thresholds applied verbatim.
- A4: independent read-only recheck (separate thread) replays counts, thresholds, leakage-formula non-use, undetected isolation, per-packet stratification, and write-scope before any `OPERATOR_RETURN.md`-style solidification. FAIL blocks solidification.

## Tasks (ordered, coder-operator, stdlib only)

1. T1 inventory: stat (never open content beyond §1) + record the §1 file table (path/size/mtime) into `h2_input_inventory.json`; STOP per §6 on any mismatch.
2. T2 normalize: load the three jsonl files with strict (no-NaN/Infinity) JSON; build the 56-row compact table (§2 field contract); write `h2_record_table.json` (full) — no verdicts.
3. T3 H2a descriptives (§3/H2a): per-(packet,block) pm-ordering table + IR-3/IR-1 corroboration columns; write `h2a_table.json/.md`.
4. T4 H2b descriptives (§3/H2b): fail-site ratio distribution + by-arm split + IR-2 distribution; write `h2b_table.json/.md`.
5. T5 H2c descriptives (§3/H2c): in-X / out-of-U cross-tab + coord distribution + IR-2/IR-4 corroboration; write `h2c_table.json/.md`.
6. T6 H2d descriptives (§3/H2d): floor-diff distribution; write `h2d_table.json/.md`.
7. T7 H2e descriptives (§3/H2e): IR-4 top-k concentration + IR-5 truncation-scope + IR-1 tail shape + missing-quantity list; write `h2e_table.json/.md`.
8. T8 final adjudication (main-thread only): apply §4 thresholds verbatim to T3–T7 outputs; write `h2_final_adjudication.md` (+ `h2_summary.json`) — the ONLY file containing verdict tokens.
9. T9 manifest + focused review packet: `run_manifest.json` (command, interpreter, wall/RSS, zero counters, input digests-sizes, output list) and request independent recheck per A4.

---

## 1. Frozen inputs (worktree evidence ONLY)

| id | path | records | note |
|---|---|---|---|
| P20N-jsonl | `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/per_block_arm_outcomes.jsonl` | 16 (4 blocks x A/B/C/D) | 1.5M HOLD 2213..2724; K1 331/K2 6689; order `a9f18a9f…`; alt `6f4a4f76…`; NO u-domain field |
| P20N-sum | `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/aggregate_summary.json` | — | A 0/4 B 1/4 C 0/4 D 1/4; pm means 0.8236 (inc) / 0.9005 (alt) |
| P20O-jsonl | `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/per_block_arm_outcomes.jsonl` | 20 (5 x A/B/C/D) | 2M VAL 2187..2826; K1 334/K2 6746; order `b2255449…`; alt `98e25495…`; u-domain PRESENT |
| P20O-sum | `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/aggregate_summary.json` | — | A 0/5 B 2/5 C 0/5 D 3/5; b_restored 2; d_restored 3 |
| P20Q-jsonl | `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m/per_block_arm_outcomes.jsonl` | 20 (5 x A/B/C/D) | 2M HOLD 2916..3555; same K/order/alt as P20O; nine scalars + IR-1..IR-5; 2248515 B |
| P20Q-sum | `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m/aggregate_summary.json` | — | A 0/5 B 4/5 C 0/5 D 4/5; b/d_restored 4; 12 L2-fails in-X + out-of-U; IR payload tables |
| P20Q-report | `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m/report.md` | — | human-readable descriptive summary (no verdict) |
| X10-results | `workspace/probes/nbpolar_x10_h2_scalar_adjudication/results.json` | 36+9 rows | frozen scalar baseline: H2a REFUTED (4/4 blocks anomalous); H2b median 2.246 n=25; H2c 23/25, P20O 11/11 out-of-U; H2d 0.0030; H2e NOT-DECIDABLE; prereg cutoffs 1.10/0.5/0.05 |
| (context) | `.../frozen_plan.json`, `.../input_and_predecessor_identity.json` per packet + X10 `prereg.md` | — | threshold/field semantics + identity pins; no content recompute |

## 2. Field + join contract (normative)

- Nine scalars per record: `l2_order_digest`, `l2_prefix_len` (=K2: 6689 P20N / 6746 P20O/P20Q), `l2_fail_in_prefix` (bool/null), `l2_fail_hazard_bits` (float/null), `l2_fail_nbhd_mean_bits` (float/null, R=8), `l2_prefix_hazard_mean_bits` (float, always present on completed records), `l2_fail_nbhd_floor_frac`, `l2_prefix_floor_frac`, `l2_fail_in_prefix_u_domain` (bool/null; ABSENT-column on P20N → treat as null, never impute).
- Nullability: failing-scalar fields non-null IFF `first_error_layer == "L2"` with computable hazard; else null. Prefix means present on every completed record. `exact` = (`outcome == "exact"`) AND `tag_pass` AND `label_match`; `undetected` isolated, never success.
- P20Q IR (P20Q records only; P20N/P20O have no IR — never backfill): IR-1 `ir1_hist_edges_bits[65] + ir1_hist_prefix_counts[64] + ir1_hist_outside_counts[64]` (prefix+outside=32768 every row); IR-2 `ir2_first_error_hazard_rank_pct` in [0,1], null unless L2-fail; IR-3 `ir3_thresh_lo_bits = 1.0*pm`, `ir3_thresh_hi_bits = 2.0*pm` + `ir3_prefix_above_lo/hi_count/frac` (never null); IR-4 `ir4_topk_coords/hazard_bits/in_prefix/ranks[16]` (never null; ranks 1-based); IR-5 `ir5_series_hazard_bits/in_prefix[<=4096] + ir5_series_truncated(bool; true at N=32768) + ir5_series_total_len(=32768)`.
- Joins: stratify by `packet` (P20N vs P20O vs P20Q — different sessions/K/orders/alts, never pooled for K/budget/order claims). Join key within packet: `(block_index, arm)`. Arms: A/B operational (paired), C/D oracle (paired, diagnostic only, never merged into A/B). Cross-packet rollups are descriptive concatenations with per-packet sub-rows preserved (X10-continuity: main 36 + P20Q 20 = 56-row table; P20Q-only IR columns null elsewhere).
- Numerics: floats must be finite (strict parse; NaN/Infinity → STOP). Ratios require `pm > 0`. Eps for pm-ordering anomaly: `1e-12` (X10-frozen). Medians = statistics.median; means = fmean; fractions = exact integer ratios.

## 3. Per-H2 computations (descriptives ONLY — no verdict token in these outputs)

### H2a — average metric quality orders arms
- Question: within each block, does lower `l2_prefix_hazard_mean_bits` predict exactness (i.e., every exact arm pm ≤ every failing arm pm)?
- Inputs: `packet, block_index, arm, exact, l2_prefix_hazard_mean_bits` (56 rows) + P20Q IR-3 (`ir3_prefix_above_lo/hi_frac`, thresholds) + IR-1 (prefix vs outside mass/tail) as corroboration columns.
- Computation: per (packet,block_index): collect evaluable arms (pm finite non-null + exact non-null); if block has ≥1 exact AND ≥1 non-exact → evaluable; `fail_min_pm = min(pm|fail)`, `exact_max_pm = max(pm|exact)`, `gap = exact_max_pm - fail_min_pm`, `anomaly = gap > 1e-12`. Pooled: `n_blocks, n_evaluable, n_anomaly`, per-block rows + strongest-gap record list. Corroboration (no verdict): per-record IR-3 above-lo/hi frac vs exactness; IR-1 prefix-tail-8 mass per block (from P20Q-sum `prefix_tail8_mass` + recomputed histogram tail).
- Outputs: `h2a_table.json` (per-block rows + pooled counts + corroboration columns) + `h2a_table.md` (same as markdown table). X10 continuity check: reproduce X10 H2a per-block gaps (P20N b3 0.0971; P20O b1 0.0304/b2 0.0431/b4 0.0684) before adding P20Q blocks.

### H2b — fail-site hazard elevation
- Question: are first-error sites more hazardous than their block prefix average (`l2_fail_hazard_bits / pm > 1`)?
- Inputs: L2-fails only: `l2_fail_hazard_bits, l2_prefix_hazard_mean_bits` (+ `l2_fail_nbhd_mean_bits` for nbhd/prefix secondary) + arm + packet + P20Q IR-2 (`ir2_first_error_hazard_rank_pct`).
- Computation: per fail with fh finite + pm finite + pm>0: `r_fail = fh/pm`; per fail with nm finite: `r_nbhd = nm/pm`. Distributions: n/min/p50/max/mean overall + by-arm-group (A vs B; C/D separate) + by-packet (P20N/P20O/P20Q). Strongest: max-r record id. IR-2 corroboration: n/min/p50/max/mean of rank_pct over L2-fails with non-null IR-2 (P20Q: expect 12 values; plus P20Q-sum cross-check median 0.8830 range 0.3802..0.9894), split A-operational/B-operational/oracle. Expected evaluable: X10 n=25 + P20Q 12 L2-fails.
- Outputs: `h2b_table.json/.md` (ratio distributions + strongest + IR-2 distribution). No p-values.

### H2c — prefix concentration + U-domain split
- Question: do L2 failures concentrate inside the disclosed X-prefix, and (P20O/P20Q) inside-X-but-outside-U?
- Inputs: L2-fails (+ all fails for denominator audit): `first_error_coord, first_error_layer, l2_fail_in_prefix, l2_fail_in_prefix_u_domain` (null on P20N) + P20Q IR-2 + IR-4 (`ir4_topk_in_prefix`, `ir4_topk_ranks/coords`).
- Computation: `inX_known` = fails with `l2_fail_in_prefix` non-null; `inX_true` = among them true; `frac_inX = inX_true/inX_known` overall + per-packet (P20N; P20O; P20Q). `outU_given_inX` = among P20O+P20Q in-X fails with u-domain non-null, count false / known (expect P20Q 12/12 per OPERATOR_RETURN §5; P20O 11/11). Coord distribution per (packet,arm-group): n/min/p50/max/mean of `first_error_coord`. IR corroboration: IR-2 median (high rank ⇒ fail site in hazard tail); IR-4 pooled `in_prefix` fraction over 20 P20Q records x16 (=320 flags) + per-record in-prefix counts 1..5 cross-check vs P20Q-sum.
- Outputs: `h2c_table.json/.md` (cross-tab + coord distributions + IR corroboration). Oracle C/D rows kept separate.

### H2d — floor flatness
- Question: is the floor-hit fraction flat between fail-neighbourhood and prefix (`|fail_nbhd_floor − prefix_floor| ≈ 0`)?
- Inputs: `l2_fail_nbhd_floor_frac, l2_prefix_floor_frac` on records where both finite.
- Computation: per record `d = |f − p|`; pooled `n_pairs, mean_abs_diff, max_abs_diff` overall + per-packet. Expected: X10 n=25 mean 0.0030 + P20Q additions.
- Outputs: `h2d_table.json/.md`.

### H2e — static-order geometry (IR-4/IR-5 escalation)
- Question: does recorded hazard geometry (top-k concentration + capped series + histogram tail) resolve what scalars could not (X10 NOT-DECIDABLE)?
- Inputs (P20Q only + absence proof elsewhere): IR-4 (320 top-k flags/ranks/hazards/coords), IR-5 (`ir5_series_truncated`, `total_len`, first-4096 series), IR-1 histograms (prefix vs outside mass/tail shape), IR-2 ranks, plus the X10 missing-quantity list as the absence baseline.
- Computation (all truncated-scope, explicitly labelled): (a) IR-4 pooled in-prefix fraction + per-record counts + rank list (ranks are 1..16 hazard-order, NOT block positions); (b) IR-5 scope statement: `truncated=true 20/20, total_len=32768 20/20` ⇒ full-block rank claims FORBIDDEN, first-4096-scope only; (c) IR-1 tail: per-record prefix-tail mass + outside-vs-prefix shape note (prefix 6746 + outside 26022 = 32768 every row); (d) evaluability flag: IR-4 present 20/20 AND IR-2 present on 12/12 P20Q L2-fails AND IR-5 present 20/20 (else NOT-DECIDABLE path). No per-position `(b,u1)` sequence is claimed beyond the frozen IR-5 first-4096 dump + IR-4 top-k list.
- Outputs: `h2e_table.json/.md` (concentration numbers + scope flags + missing-quantity delta vs X10). No SUPPORTED/REFUTED token here.

## 4. Pre-registered decision thresholds (applied ONLY in `h2_final_adjudication.md`; descriptive, no FER claim)

- H2a: REFUTED if `n_anomaly ≥ 1` (≥1 evaluable block with `gap > 1e-12`); else SUPPORTED if `n_evaluable ≥ 1 AND n_anomaly == 0`; else NOT-DECIDABLE (0 evaluable blocks). X10 prior: REFUTED (4/4 anomalous).
- H2b: SUPPORTED iff `median(r_fail) > 1.10` (descriptive cutoff, X10-frozen); REFUTED iff median ≤ 1.10; NOT-DECIDABLE iff n == 0. IR-2 median reported as corroboration (no vote-flip; inconsistency noted explicitly).
- H2c: SUPPORTED iff `frac_inX ≥ 0.50` (descriptive, X10-frozen); REFUTED iff < 0.50; NOT-DECIDABLE iff `inX_known == 0`. Out-of-U fraction + IR-2/IR-4 reported separately (no threshold vote).
- H2d: SUPPORTED-flat iff `mean_abs_diff ≤ 0.05` (descriptive, X10-frozen); REFUTED (separation) iff > 0.05; NOT-DECIDABLE iff n == 0.
- H2e: NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS iff evaluability fails (IR-4 <20/20 or IR-2 <12/12 on P20Q L2-fails or IR-5 <20/20); else SUPPORTED-geometry-coherent iff (IR-4 pooled in-prefix frac ≥ 0.50 AND IR-2 median over P20Q L2-fails ≥ 0.50); else REFUTED-geometry-incoherent (evaluable but either < 0.50). Scope always labelled truncated (first-4096 + top-16 + histogram); never a full-block order claim, never FER.

## 5. Output files (additive under `workspace/h2/<uuid>/`; `<uuid>` fresh; no other writes)

- `h2_input_inventory.json` (8 inputs: path/size/mtime + P20Q digests/K/blocks replayed as literals for identity only).
- `h2_record_table.json` (56-row compact table; scalars only + IR where present; no verdicts).
- `h2a_table.json/.md`, `h2b_table.json/.md`, `h2c_table.json/.md`, `h2d_table.json/.md`, `h2e_table.json/.md` (descriptives only; any verdict token here = STOP-fail).
- `h2_final_adjudication.md` + `h2_summary.json` (ONLY files containing SUPPORTED/REFUTED/NOT-DECIDABLE tokens; per-H2 evidence line + threshold application + X10-delta note).
- `run_manifest.json` (command, interpreter, wall_s, rss_bytes, decoder_calls 0, rng_calls 0, tag_calls 0, protected_opens 0, input list, output list).
- Figures: markdown tables only (no new binaries). JSON indent=1 + trailing newline (X10 convention).

## 6. Stop rules (specific status, no input repair)

STOP with `H2_STOP_<REASON>` in the manifest and no adjudication when: required file missing/unreadable; record count ≠ P20N 16 / P20O 20 / P20Q 20; malformed JSONL or nonfinite numeric; P20Q IR field missing/cap-violated on any record (`prefix+outside ≠ 32768`, IR-4 ≠16, IR-5 `total_len ≠ 32768` or `truncated ≠ true`); recomputed exact counts disagree with any `aggregate_summary.json` (A/B/C/D per packet); `undetected ≠ 0` anywhere; any protected open/stat/listing attempted; any decoder/RNG/tag call; any write outside `workspace/h2/<uuid>/`; any K/budget recompute, new tag domain, or construction/prior/order edit; any verdict token outside `h2_final_adjudication.md`/`h2_summary.json`. Execution-error rerun: 1 allowed max, recorded in manifest (identical inputs, never tuning).

## 7. Provenance pins (literals for identity only — never recomputed as analysis)

P20N: K 331/6689/7020, order `a9f18a9f…638`, alt `6f4a4f76…e78`, blocks 2213..2724. P20O/P20Q: K 334/6746/7080, order `b2255449…906`, alt `98e25495…5fb5`, prior `b16f5216…587`, P20O VAL 2187..2826, P20Q HOLD 2916..3555 + remainder 3556..3644 never decoded. Tag masters: P20Q `2026092330` (analysis creates none). CE/disclosure ratios never called efficiency; oracles never operational.
