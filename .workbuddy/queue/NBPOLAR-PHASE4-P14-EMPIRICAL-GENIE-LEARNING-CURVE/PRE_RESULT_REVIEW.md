# Pre-RESULT review — NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE (independent)

Reviewer: independent reviewer-go (did not write the code, freeze the plan, or run the gate).
Read-only review; the only file written by this review is this document.
The V25 `channel_counts.npz` content was NEVER opened (metadata stat only).
The gate command was NEVER rerun (read 1/1 + attempt 1/1 spent per the artifacts).
No Model-F/HOLD/raw/real/EVAL/tag access; no P13/old-root writes; no commit/push.

**Verdict: PASS_WITH_COMMENTS** — the gate evidence recomputes clean: 13/13
integrity gates independently recomputed TRUE, all DEV/paired/report-only
numbers match to 0 or float dust (≤3e-17), classification correctly derives
`..._NOT_CONFIRMED`, tests 15 + 320 pass. Comments (§11) are non-blocking.

## 1. Root inventory — exactly five frozen files, no extras/sidecars

Command:

```bash
ls -la .workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/
ls -1 ... | wc -l
```

Raw evidence (2026-09-15, local +0800):

```text
aggregate_summary.json            10678  2026-09-15 03:36:41
frozen_plan.json                   6389  2026-09-15 03:17:40
learning_curve_constructions.json 7532077 2026-09-15 03:36:41
per_block_genie_residuals.jsonl    7058  2026-09-15 03:36:40
report.md                          3547  2026-09-15 03:36:41
count = 5, no hidden files, no sidecars
```

`frozen_plan.json` stub time 03:17:40 precedes all DEV-finalized files
(03:36:40–41); `aggregate_summary.json` created_utc `2026-09-14T19:36:40Z`
vs plan `2026-09-14T19:17:41Z`: Δ1199 s ≈ wall 1110 s + finalization. PASS.

Deep scalar-only audit: per-prefix keys are exactly the 15 frozen names
(`b f freeze_sha256 k1 k2 k_total l1_order l2_order leakage_bits
pooled_e1_mean pooled_h1_mean pooled_e2_mean pooled_h2_mean
train_blocks_used train_residual`) — no counts/symbols/truth/decoder-output/
metric-plane/RNG-state arrays. Token scan hits are prose only:
`counts` → `counts_path` + frozen command + `support_rule` prose;
`truth` → gate name `truth_isolation` + `truth_boundary` prose;
`metric` → sampling-rule prose. No persisted arrays beyond pooled
means + public orders + scalars. PASS.

JSONL: 32 lines; every line has exactly the frozen key set
`{block_index error n r_128 r_16 r_32 r_64 r_8 stream_seed}`;
`error` null on 32/32; `n` = {16384}; DEV seeds {2026091940..43} × 8
each; 32 unique (seed, block) pairs; stream-major sorted
(first (2026091940,0), last (2026091943,7)). PASS.

## 2. Preconditions / consumption / NPZ metadata

Command: recompute from `aggregate_summary.json` entropy block.

```text
H1  measured 0.024280546818678802  literal 0.02428054681872374  |d| = 4.4939746368655165e-14  (≤1e-12 ✓)
H2  measured 0.7767572780789994   literal 0.7767572780789994   |d| = 0.0                      (≤1e-12 ✓)
TOT measured 0.8010378248976782   literal 0.8010378248977232   |d| = 4.5075054799781356e-14   (≤1e-12 ✓)
floor change 5.1600945738528026e-11 (≤1e-9 ✓); column dev 1.1357581541915351e-13; p_b sum 1.0
all 7 precondition checks true (recomputed from record, not copied)
```

Consumption (recomputed from `attempt_read_accounting`):
reads 1/1, attempts 1/1, open_count 1, before 0/0, retries 0,
reopen False, retry_after_open False, observed == expected == 25166822,
stat_size_checked true. NPZ metadata stat (never opened):
`size=25166822 mtime=2026-08-19 01:34:09 +0800` — matches
`expected_npz_bytes`; mtime predates the gate (no rewrite). PASS.

## 3. Nested construction (K_total, argmin, orders, nesting, freeze, streams)

K_total recompute (independent):

```text
literal H=0.8010378248977232 → raw 3399.4929680123178 → floor 3399
measured H=0.8010378248976782 → raw 3399.4929680121254 → floor 3399
leakage 5*3399+64 = 17059 ≤ budget 17061.464840060627; f = 1.2998121912679332 ≤ 1.3 ✓
K1+K2 = 3399 on all five: B=8 (158+3241), B=16 (161+3238), B=32 (162+3237),
B=64 (162+3237), B=128 (173+3226)
residuals: 5.3882981160102705e-05 / 0.0002739494046524113 / 0.0013067725980560572 / 0.0036843863984939752 / 0.013279461298516686
```

Argmin replay via accepted `select_empirical_split` from the persisted
pooled means: all FIVE prefixes reproduce `(k1, k2, residual)` exactly
(|d| = 0.0) with identical L1/L2 orders (B=8 and B=128 verified first per
the "at least two" rule; B=16/32/64 additionally replayed exact).
Freeze-SHA replay (canonical `b,k_total,k1,k2,orders,pooled-means`):
all five match (`6b650c04…`, `7e42df33…`, `98601ff8…`, `6f2094d5…`,
`059dc2b8…`) and agree with the aggregate digest. PASS.

Orders: all checked layers are full permutations of 0..16383 with ZERO
worst-first `(e,h,index)` violations over all 16383 adjacent pairs each
(B=8 L1/L2, B=128 L1/L2; spot-check rule exceeded). Finite pooled means
(length 16384 each, e∈[0,0.96875]). Nesting from records:
`train_blocks_used == B` on all five; telescoping running-sum diffs
(`B2·mean_B2 − B1·mean_B1`) are ≥ −4e-323 (float dust, within 1e-9) on all
16 (layer, step) pairs — consistent with one nested stream-major sequence;
orders differ across B (B=8 L1 starts [0,2,4,8,16], B=128 [16,0,1,2,4]),
so learning visibly moved with B. `frozen_before_first_dev` true;
structural freeze-before-DEV confirmed in code (TRAIN loop → snapshot →
DEV loop; missing-prefix guard raises before any DEV genie call). PASS.

Streams: TRAIN exactly `2026091930..37`, DEV exactly `2026091940..43`;
disjoint (intersection ∅); JSONL seeds == DEV set, ∩ TRAIN = ∅;
stream-major order verified sorted. PASS.

## 4. DEV statistics, paired diffs, classification, flat-curve note

Per-prefix recompute from the 32 JSONL `R` values (t factor 1.695518782, df=31):

```text
B=8   mean 0.1175773969604019  std 0.18328617696455768(|d| 2.8e-17) min 0.00023161951066219544 max 0.6632266438755844 UCB 0.17251343416734777 (>0.01)
B=16  mean 0.13176399133297984 std 0.18728900823240302 min 0.00015639852900284357 max 0.6981597350727797 UCB 0.18789978997914214 (>0.01)
B=32  mean 0.1060391737357177  std 0.17563973337252425 min 0.0002421531531953125  max 0.6972184077530478  UCB 0.15868335611416776 (>0.01)
B=64  mean 0.08983984405791562 std 0.16445710274458678 min 0.0004354717782820705 max 0.8070449161693778  UCB 0.13913227660764454 (>0.01)
B=128 mean 0.1419810706809162  std 0.19735260988460465 min 0.00017760231322272446 max 0.806151592316756  UCB 0.2011332146072146 (>0.01)
```

ALL FIVE `UCB≤0.01` are False (recomputed, not copied); only B=128 gates
classification. Paired `R_B−R_8` + adjacent steps recompute exact
(|d| ≤ 2.8e-17): R_16−R_8 (0.014186594372577927/0.17294151558954643/
0.06602204477258328), R_32−R_8 (−0.011538223224684209/0.1348726212270291/
0.028886905721941962), R_64−R_8 (−0.02773755290248629/0.11712473187364603/
0.0073680329885239225), R_128−R_8 (0.024403673720514288/0.16989973009547454/
0.07532741520801287); steps R_32−R_16 (−0.025724817597262136/
0.1031757123802204/0.005199853690245681), R_64−R_32 (−0.01619932967780208/
0.08917824709781177/0.010529906436730147), R_128−R_64 (0.05214122662300058/
0.12867194063944914/0.09070783669434054). vs-R8 counts recompute exact:
16: 19/13/0, 32: 19/13/0, 64: 20/12/0, 128: 17/15/0, 8: 0/0/32.
Report-only Spearman_vs_128 + topK recompute exact (|d| = 0.0):
L1/L2 = 8: 0.9929179557129755/0.9976659246808045; 16: 0.9942806123577369/
0.9984572002774081; 32: 0.9958371560141577/0.9990437934812538; 64:
0.9979087564465174/0.9994517134307482. PASS.

Classification derivation: integrity all-true (13/13 recomputed, §6) AND
B=128 UCB 0.2011332146072146 > 0.01 → `NOT_CONFIRMED` (not CANDIDATE,
not BLOCKED). Persisted label
`TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED` derives
correctly. Flat-curve observation (descriptive numbers only, no causal
claim): mean B=128 (0.1419810706809162) is NOT below mean B=8
(0.1175773969604019); paired R_128−R_8 mean +0.024403673720514288 —
the mission question's descriptive answer on these records. PASS.

## 5. No P13 merge

P14 B=8 uses P14 seeds only: runner constants are exactly TRAIN
`2026091930..37` / DEV `2026091940..43`; no `20260918*` seed appears in
any gate artifact (grep empty); the `1860/1913` grep hits inside
`learning_curve_constructions.json` are polar coordinate indices
(0..16383 ranges contain them), not seeds. Runner references P13 only in
prose ("historical reference", "shared helpers"); no P13-evidence import,
path, value, or comparison exists in code or gates. P13 seeds
(1860..1913 family) are disjoint from P14 streams. PASS.

## 6. Gates (all 13 recomputed from records — not copied)

| gate | recomputed | persisted | note |
|---|---|---|---|
| target_population_contract | True | True | 7/7 checks + diffs ≤1e-12, floor ≤1e-9 |
| one_n_cell_complete | True | True | 128 TRAIN + 32 DEV recs, 0 errors, n=16384 |
| nested_prefixes_exact | True | True | set {8,16,32,64,128}, used==B |
| streams_disjoint_frozen | True | True | exact frozen tuples, disjoint |
| orders_valid_frozen_before_dev | True | True | perms + 5/5 SHA replay + flag |
| budget_allocation_reproduced | True | True | literal K=3399, 5/5 split replay ≤1e-9, leak≤budget |
| risks_finite | True | True | all pooled + residual + 160 DEV scalars finite |
| zero_genie_exceptions | True | True | 0 block errors, 320 calls |
| truth_isolation | True | True | provenance_violations 0 |
| no_unregistered_calls | True | True | 320/320 |
| checkpoint_accounting_consistent | True | True | 5 files + JSONL 32 == records |
| attempt_read_accounting_exact | True | True | 1/1 + 1/1, open 1, no reopen |
| resource_limits_met_and_no_abort | True | True | wall 1110.17 ≤ 1800, Vm ≤ 2GiB, no stop |

`failing_integrity_gates` [] empty (verified); `integrity_all_pass` true.
Partial-fallback path NOT taken: 128/128 TRAIN, 32/32 DEV, exit-0
NOT_CONFIRMED label (not BLOCKED). PASS.

## 7. Resources / accounting

`wall_s` 1110.16709 vs `resources.wall_s` 1110.717597 (Δ 0.550507 s =
finalization after the run clock — consistent, not a mismatch).
VmPeak 508308 kB (~496 MB), VmSize 462600 kB, rss_hwm 283115520 B
(~270 MB) — all far below the 2 GiB `ulimit -v 2097152`; no resource
stop; wall ≈ 62% of the 1800 s budget. Per Pre-EXECUTE instruction,
resources are judged by VmPeak/VmSize + wall (authoritative); here
`rss_bytes_peak` (270 MB) sits BELOW VmPeak, so the documented WSL2
`ru_maxrss` phantom did not materialize on this run — no disregard
needed. Checkpoint consistency verified (§6, gate 11). 320/320 genie
calls, 0 exceptions/violations, truth isolation holds. PASS.

## 8. Bounded wording (report.md read fully — 59 lines)

Genie-proxy-only language present throughout ("proxy, not FER" table
heading; residual_scope: "not operational FER, not a real-channel result
and not proof of any minimum N or TRAIN size"; claim_scope: "not held-out
or real frame FER, efficiency, key rate, scaling, qualification or
promotion"). No more-TRAIN / regularization / larger-N RECOMMENDATION
appears in any artifact (that choice is packet-reserved to the main
thread — none found to flag). No ε_eff/HOLD/qualification/promotion
language. BEC absent by design: zero `bec` tokens in the gate root
(confirmed by case-insensitive scan; the only `efficiency` hits are the
scope disclaimers). PASS.

## 9. Tests / scope

Pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`,
`-q -p no:cacheprovider`, fresh basetemps:

```text
focused test_nbpolar_empirical_genie_learning_curve.py → 15 passed in 365.15s (basetemp /tmp/p14-preresult-focused)
full    test_nbpolar_*.py                          → 320 passed in 485.72s (basetemp /tmp/p14-preresult-full)
```

Expectation 15 + 320 met exactly; no regressions. `git status
--porcelain`: P14 declared set is untracked-new (runner, focused test,
P14 spec dir, P14 queue dir); tracked `M` entries belong to prior-phase
work (P3/P11 etc.), not this gate — HEAD unchanged `ab173f2a`,
verified by `git log --oneline -1` + `git rev-parse HEAD`. Gate-window
mtime sweep (local 2026-09-15 03:17–03:37) shows the gate wrote ONLY its
own root (empty outside-list). Accepted modules / P13 / X-roots untouched
by the gate execution. No commit/push; no rerun. PASS (with worktree note
in §11.2).

## 10. Checklist

- [x] Matches OpenSpec spec (P14 delta: matrix, construction, DEV stats,
      13 gates, labels, five-file schema, proxy boundary, P13-reference-only)
- [x] Tests pass (focused 15/15; full NB-Polar 320/320; pinned interpreter;
      fresh basetemps; no NPZ/frozen-stream/production-path use by reviewer)
- [x] No scope creep (gate wrote only its five-file root; no tag/Toeplitz/
      BEC/FER/qualification surface; no P13/old-root writes)
- [x] docs/decision-log.md or docs/troubleshooting.md needs update? NO —
      no new reusable failure mode was observed by this review (the
      ru_maxrss phantom did not materialize; wall gloss note in §11.1 is
      prompt-context arithmetic, not a repo failure mode). Milestone-batched
      docs remain the main thread's call.

## 11. Findings (all non-blocking)

1. (context arithmetic, non-blocking) The task context glosses wall
   1110.16709 s as "≈19m33s"; 1110 s is 18m30s (19m33s would be ≈1173 s).
   The persisted raw number 1110.16709 is correct and consistent
   (plan→summary Δ1199 s); only the human gloss is off. No artifact repair.
2. (worktree hygiene, non-blocking) The worktree is dirty from prior-phase
   work (tracked `M` on P3/P11-era files, many `??` queue dirs). None of it
   is P14-gate-caused (gate-window sweep is clean; HEAD `ab173f2a`
   unchanged). Main thread owns adjudication/cleanup per AGENTS.md §10.1.
3. (STATUS, non-blocking) `STATUS.yaml` still shows freeze-time state
   (reads/attempts 0, reviews pending) while the gate artifacts record
   1/1 spent. Expected — STATUS update is the main thread's acceptance
   step, not the reviewer's.

## Closure statements

- The V25 `channel_counts.npz` content was NOT reopened by this review
  (metadata stat `25166822` bytes + `2026-08-19` mtime only); the module
  flag was never touched by the reviewer (no imports of the runner's
  NPZ path in this review).
- The gate was NOT rerun by this review (read 1/1 + attempt 1/1 remain
  spent exactly as the artifacts record; no new output written anywhere
  except this review file).
- The only file written by this review is this `PRE_RESULT_REVIEW.md`.
- HEAD is unchanged (`ab173f2a`); no commit/push by this review.
- Recommendation: main thread records Pre-RESULT PASS_WITH_COMMENTS,
  updates STATUS.yaml (reads/attempts 1/1, result
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED`), and proceeds
  to acceptance — the next scientific choice (more TRAIN, regularization,
  or larger N) is packet-reserved to the main thread.
