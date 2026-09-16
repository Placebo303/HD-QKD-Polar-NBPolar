# P17 Pre-RESULT review — N=32768 operational replication (Tier-Y)

Packet: `NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION`
Reviewer: independent Pre-RESULT (read-only; did not write the code, freeze the plan, or run the gate).
Scope: frozen gate evidence only — the five artifacts under `operational_replication_gate/`
plus `operational_f13_replication.py` (read), P16 construction file (JSON read only),
metadata stats only. Gate NOT rerun. NPZ content NOT reopened.

```
Verdict: PASS_WITH_COMMENTS
```

All 10 required recomputation items check out number-by-number. The single comment (item 8)
is a reporting-level clarification, not a gate failure: per-record VmPeak/VmSize ARE present
in all 128 records; only the aggregate summary carries wall+RSS (by schema design), and the
frozen resource gate computes solely from wall/RSS/stop-flag — all evidenced. No repair is
possible or needed (no rerun); classification stands. Human review beyond main-thread
acceptance is not required.

---

## 1. Root: exactly five files, scalar-only, 128 JSONL lines — PASS

Commands (pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`):

```bash
ls -la .../operational_replication_gate/
wc -l .../per_block_outcomes.jsonl
python -c "import json,pathlib; recs=[json.loads(l) for l in ...]; print(sorted(recs[0].keys()), all_same_keys)"
```

Raw:
- Directory holds exactly 5 files, no sidecars:
  `aggregate_summary.json` 6118 B, `frozen_plan.json` 8486 B,
  `per_block_outcomes.jsonl` 85589 B, `predecessor_construction_identity.json` 953 B,
  `report.md` 2955 B (mtimes: frozen_plan 21:08 pre-open stub; other four 21:42 final checkpoint).
- `per_block_outcomes.jsonl` = 128 lines; all 128 records share one 25-key schema:
  `block_index, error, exact, k1, k2, key_dependent_bits, l1_decode_failed, l1_error_type,`
  `l1_executed, l1_provenance, l2_decode_failed, l2_error_type, l2_invoked, l2_provenance,`
  `l2_skipped_by_l1_failure, label_match, nonfinite, outcome, public_control_bits, resources,`
  `stream_seed, tag_invoked, tag_pass, truth_leak_violation, wall_s`;
  `resources` = `{rss_bytes_hwm, vm_peak_kb, vm_size_kb, wall_s}` in all 128 records.
- Banned-key walk (exact focused-test key set:
  `bob/high/low/high_true/low_true/u1_true/u2_true/a_full/counts/logp/decision_metrics/`
  `high_hat/low_hat/label_hat/label_bits/seed_bits/rng_state/p_b/f_full/labels_true/`
  `l1_order/l2_order/pooled_e1_mean/pooled_h1_mean/pooled_e2_mean/pooled_h2_mean`)
  over all keys of all five artifacts: intersection = EMPTY (PASS). Longest list values:
  frozen_plan 14 (`integrity_gate_order`), identity/summary 8 (heads), jsonl 0 — no vectors,
  no full orders (heads only), no private material. (Naive substring hits for
  `truth/counts/bob/metric` are prose in `truth_boundary/sampling_rule/claim_scope`, not keys.)

## 2. Outcome recount (INDEPENDENT — decides CANDIDATE vs NOT_CONFIRMED) — PASS

Recomputed from the 128 JSONL records (own tallies, not copied):

- Counter: `exact 123, verify_failed 5` (undetected 0 / decode_failed 0 / nonfinite 0 /
  resource_abort 0). Persisted `outcome_counts` identical.
- Per-stream 8x16 completeness, block_index 0-15 each, exact/verify_failed split:
  2026092030 15/1; 2026092031 15/1; 2026092032 16/0; 2026092033 15/1;
  2026092034 15/1; 2026092035 15/1; 2026092036 16/0; 2026092037 16/0.
  Matches the persisted per-stream claim exactly.
- The 5 verify_failed blocks: (2026092030,12), (2026092031,11), (2026092033,5),
  (2026092034,8), (2026092035,0).
- Bucket exclusivity: every outcome in the frozen six-set; every `error is None`;
  `_record_dict_consistent(record, n=32768, k1=319, k2=6492)` true for all 128 (helper used
  as a read-only record checker, not a gate rerun).
- label_match/tag_pass consistency: all 123 `exact` have `label_match true + tag_pass true
  + exact true`; all 5 `verify_failed` have `tag_pass false`; zero mismatches.
- SC/tag/truth-leak accounting from records: `l1_executed` 128/128, `l2_invoked` 128/128
  => 256 implied SC calls = persisted `sc_calls 256`; `tag_invoked` 128/128 = persisted
  `tag_invocations 128`; `truth_leak_violation` 0/128; `provenance_violations 0`;
  provenances `PRIOR_ONLY` 128 / `CANDIDATE_CONDITIONED` 128; `l1/l2_decode_failed` flags 0;
  `nonfinite` flags 0. Zero TRAIN/genie shaped activity is structural: per-block records carry
  only the single `sc` provenance pair and one tag each; no second counter, oracle, or
  comparator fields exist in the schema.

## 3. Wilson + recovery gates + label derivation — PASS

Own implementation (`p=k/n; d=1+z^2/n; c=p+z^2/2n; m=z*sqrt(p(1-p)/n+z^2/4n^2); LB=(c-m)/d`,
z=1.6448536269514722):

- 123/128: fraction 0.9609375; LB = 0.921934049951655 == persisted LB exactly.
- 121/128: LB = 0.9021084760149684 (rounds to frozen 0.9021084760); exact>=121 TRUE.
- 120/128: LB = 0.8924595822417636 (rounds to frozen 0.8924595822); exact>=120 would still
  pass count but LB>=0.90 FALSE — verified the boundary is load-bearing on both gates.
- 62/64 (report-only cross-check): 0.9098711859061207 -> 0.9098711859, matches persisted
  P16 context; never an input (see item 5).
- Count margin: 123-121 = exactly 2 (P16's zero margin is resolved).
- LB margin: 0.921934049951655-0.90 = +0.021934049951654933.
- Recovery `pass true` recomputed TRUE; label derivation: integrity 14/14 true (item 6-table
  below, recomputed) AND recovery true => `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE`
  uniquely correct (NOT_CONFIRMED would require recovery false; BLOCKED would require an
  integrity/resource failure; failing list is empty).

## 4. Predecessor identity + tag domains + P16 untouched — PASS

- Canonical digest recomputed HERE from the P16 JSON (same 10-key recipe
  n/k_total/k1/k2/l1_order/l2_order/pooled_e1_mean/pooled_h1_mean/pooled_e2_mean/pooled_h2_mean,
  sort_keys, separators `(',',':')`):
  recomputed `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  == stored `freeze_sha256` == construction-digest flag == identity-file `digest_recomputed`.
  N/K_total/K1/K2 = 32768/6811/319/6492; protocol `nbpolar-p16-operational-f13-gate`;
  `frozen_before_first_dev True`; L1/L2 valid 32768-permutations; identity heads
  l1 `[0,1,2,3,4,6,8,9]` / l2 `[2296,1706,3456,1708,1745,2282,4630,4868]` byte-match the file;
  leakage 34119, f 1.2998502888172847.
- P16 root untouched: five files with freeze sizes
  2586645/2581862/6991/42760/2529 B and mtimes 2026-09-15 18:07-18:28, all predating the P17
  run (frozen_plan stub 21:08, final checkpoint 21:42). P16 file opened JSON-only for the
  digest recompute; never written.
- Tag domains: frozen_plan `tag_seed_domain` =
  `nbpolar-p17-operational-replication-seed:<master>:<n>:<block_index>`; runner
  `SEED_PREFIX` is the P17 prefix; ZERO hits for the P16 prefix
  (`nbpolar-p16-operational-f13-seed`) anywhere in the five P17 artifacts — no P16-domain
  scoring is evidenced in persisted records (which persist no seeds at all). The ratified R1
  seam (helper-internal P16-domain array derived in-memory but discarded by the P17
  `_tag_fn` closure; scored seeds proven P17-only by the Pre-EXECUTE spy test) is inherited
  unchanged and remains ratified; nothing in this gate's evidence reopens it.

## 5. Non-pooling — PASS

- Decision inputs are exactly the 128 P17 blocks: `recovery.total 128`, `dev_total 128`,
  `dev_block_count 128`; recovery/exact logic pins total==128 (any P16-shaped total
  structurally fails).
- P16's 62/64 + 0.9098711859 appear ONLY in `predecessor_report_only`
  (`p16_exact/p16_total/p16_wilson_lb`, `pooled_into_decision false`) in frozen_plan +
  aggregate_summary, and in report.md discussion ("Predecessor context (report-only; never
  pooled...)" + "contribute zero weight... decision uses exactly the 128 P17 blocks").
  No P16 observation enters any gate computation (no P16 stream seed among the 128 records;
  no 62/64-derived input in recovery/integrity paths).

## 6. Preconditions / consumption / NPZ metadata — PASS

- Recorded H1 0.024280546818678802 vs literal ...2374: diff 4.4939746368655165e-14 <= 1e-12.
  H2 exact (diff 0.0). Total ...6782 vs ...7232: diff 4.5075054799781356e-14 <= 1e-12.
  Floored total 0.8010378249492791; floor change 5.1600945738528026e-11 <= 1e-9 guard.
  Column dev 1.1357581541915351e-13 <= 1e-12; p_b sum 1.0; all 7 check flags true.
- Consumption (durable record in aggregate_summary/frozen_plan): reads 1/1, attempts 1/1,
  opens 1, reopen false, retries 0, stat-size checked, observed==expected==25166822,
  consumed-at-first-open. NOTE: `STATUS.yaml` in this worktree still shows the pre-execute
  0/1+0/1/`result: null` state — it was not advanced by the run; the artifacts above are the
  authoritative consumption record (main-thread acceptance owns the STATUS update).
- NPZ metadata stat only (content never reopened by this review):
  `channel_counts.npz` 25166822 B, mtime 2026-08-19 (unchanged, predates everything).

## 7. Disclosure / accounting — PASS

- Per-block: `key_dependent_bits` 34119 in all 128; `public_control_bits` 327743 in all 128;
  k1 319 / k2 6492 in all 128.
- Totals recomputed: 128*34119 = 4367232; 128*327743 = 41951104 — match persisted
  key/public/tag-128 exactly. Recount `l1_disclosure/l2_disclosure/verification_tag`
  128/128/128; mismatches `[]`.
- Formulae: 5*6811+64 = 34119; 10*32768+63 = 327743; f 1.2998502888172847 <= 1.3 preserved.

## 8. Resources + MAIN-THREAD-FLAGGED ITEM (VmPeak/VmSize) — adjudicated — PASS_WITH_COMMENTS

- wall_s 2031.385216 <= 2400.0 cap: TRUE, margin 368.614784 s (15.4%).
- rss_bytes_peak 569614336 <= 2147483648 (2 GiB): TRUE, headroom 1577869312 B (~2.9x).
- `resource_stop_fired False`, reason null, zero `resource_abort` records.
- Exit/stderr: exit 0 + empty stderr are operator-reported and not re-verifiable from
  read-only artifacts; what IS verifiable is the completed final checkpoint (all five files,
  128/128 records, 14/14 gates, persisted CANDIDATE label at 21:42) — consistent with a
  completed run, no abort-fill, no BLOCKED path.
- Adjudication of the flagged item:
  (a) The frozen evidence schema and the frozen resource gate do NOT require
  aggregate-level VmPeak/VmSize. Evidence: summary schema (runner lines ~1221-1222) persists
  only `wall_s` + `rss_bytes_peak` at aggregate level BY DESIGN; the resource gate
  (`_integrity_gates`, lines ~1598-1606) computes
  `resource_ok = (resource_stop is None and aborts==0 and wall<=cap and (rss is None or
  rss<=RSS_LIMIT_BYTES))` — VmPeak/VmSize are not gate inputs. The P17-04/freeze
  "Record wall, RSS HWM, VmPeak and VmSize" requirement is specified PER RECORD
  (freeze section 5: "Per record: wall, RSS HWM, Linux VmPeak/VmSize"), and it IS met:
  all 128 records carry `resources.{wall_s, rss_bytes_hwm, vm_peak_kb, vm_size_kb}`
  with real values (vm_peak 661312-786044 kB; vm_size 452408-622200 kB; rss HWM up to
  569614336 == the aggregate peak). The operator's "VmPeak/VmSize ABSENT" describes only
  the aggregate level, where no such field exists in the schema.
  (b) Ruling: this is a PASS_WITH_COMMENTS documentation note, NOT a NEEDS-repair and NOT
  a FAIL. All 14 frozen gates are computable and true from recorded evidence (gate table
  below), so the classification stands; no rerun is possible or needed. Optional follow-up
  (outside this gate, no artifact change): record the aggregate-level VmPeak/VmSize
  convention explicitly in the next packet's freeze to prevent re-flagging.

## 9. Bounded wording — PASS

report.md read fully (70 lines). It claims ONLY a model-sampled replication at N=32768/f<=1.3:
protocol/mode, 1M source, N/K/chunk/tag, fresh DEV streams, wall/RSS, H literals, predecessor
identity, report-only P16 context with explicit never-pooled/zero-weight language, 128-block
outcome table + fraction + Wilson LB with both boundaries, disclosure totals, 14-gate table,
frozen label, and a scope paragraph that explicitly disclaims held-out/real-frame FER,
efficiency, key rate, scaling superiority, qualification, promotion, real-channel efficiency,
and success beyond the frozen label. No pooling language, no promotion language, no
"success" language beyond the frozen `..._REPLICATION_CANDIDATE` label. The only
case-insensitive hits for FER/held-out/qualification/promotion/key-rate/superiority are the
explicit negations in the scope paragraph.

## 10. Tests / scope / provenance — PASS

- Focused P17 file (pinned interpreter, fresh basetemp `/tmp/p17-preresult-focused-hybe0N`,
  `-q -p no:cacheprovider`): 25 passed in 345.61 s.
- Full NB-Polar suite (fresh basetemp `/tmp/p17-preresult-full-sts0y6`, same flags):
  383 passed in 1538.72 s.
- `git rev-parse HEAD` = `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged; no commit).
  `git status --porcelain`: 17 tracked modifications (pre-existing stacked P3/P4 waves incl.
  P11 `sc.py` chunking, docs/memory — none from this wave, none in P12-P16 gate modules,
  loader, or evidence roots) + untracked additions including the declared P17 set
  (runner 1691 lines, focused test 1062 lines, packet dir incl. this review, OpenSpec P17
  delta) alongside other-wave untracked dirs. P17 runner/test/packet are untracked additions
  as declared; P16 root is an untouched untracked dir (sizes/mtimes verified in item 4).
  Post-test output root still exactly the five files; no `results/` or
  `comparison_bench/outputs_comparison/` writes from this review.

---

## Gate table (recomputed here vs persisted)

| gate | recomputed | persisted | basis |
|---|---|---|---|
| predecessor_construction_identity | True | True | digest 055c90...c3faea1b triple-match; N/K/lengths |
| target_population_contract | True | True | diffs 4.49e-14/0/4.51e-14; floor 5.16e-11; col 1.14e-13 |
| construction_frozen_before_dev | True | True | P16 frozen flag + G1 |
| dev_coverage_complete | True | True | 128/128; 8 streams x block 0-15 |
| streams_disjoint_frozen | True | True | exact frozen 8-tuple; disjoint from P16's 12 |
| orders_valid_k_replay_f_within_budget | True | True | perms; replay 6811; leak 34119; f 1.29985...<=1.3 |
| buckets_disjoint_exhaustive | True | True | six-set + error-null + _record_dict_consistent 128/128 |
| truth_isolation | True | True | violations 0; leak flags 0; PRIOR_ONLY/CANDIDATE_CONDITIONED |
| undetected_zero | True | True | 0 undetected |
| nonfinite_zero | True | True | 0 nonfinite outcomes + flags |
| no_unregistered_calls | True | True | expected_sc 256 == sc_calls; tags 128 |
| disclosure_recount_exact | True | True | 4367232/41951104; events 128/128/128; mismatches [] |
| attempt_read_accounting_exact | True | True | 1/1, opens 1, no reopen, size 25166822 |
| resource_limits_met_and_no_abort | True | True | wall 2031.39<=2400; rss 569614336<=2GiB; no abort |
| failing_integrity_gates | [] | [] | — |
| recovery exact>=121/128 | True | True | 123/128, margin exactly 2 |
| recovery Wilson LB>=0.90 | True | True | 0.921934049951655, margin +0.0219 |
| outcome_label | ..._REPLICATION_CANDIDATE | ..._REPLICATION_CANDIDATE | uniquely derived |

## Findings

- Blocking issues: none.
- Non-blocking comments:
  1. (Item 8) Aggregate-level VmPeak/VmSize "absence" is a schema misreading — per-record
     values are present in all 128 records and the frozen gate does not take aggregate
     VmPeak/VmSize. Suggest stating the convention in the next freeze; no artifact change.
  2. `STATUS.yaml` still shows pre-execute 0/1+0/1/`result: null`; the artifacts carry the
     spent 1/1 record. Main-thread acceptance should advance STATUS (not this review).

## Closure statements

- The V25 `channel_counts.npz` content was NOT reopened (metadata `stat` 25166822 B +
  2026-08-19 mtime only; no loader call with the real path in any review command).
- The gate was NOT rerun (read 1/1 + attempt 1/1 spent per the artifacts; this review
  performed only JSON/stat recomputation plus the mandated test-suite reruns, which use
  injected tables/temp roots and never touch the real NPZ or frozen streams).
- The accepted P16 root is untouched (five-file sizes/mtimes identical to the freeze;
  construction file JSON-read only for the digest recompute).
- No TRAIN/genie/BEC/adaptive/Model-F/HOLD/raw/real/EVAL access; no P12-P16/old-root writes;
  HEAD unchanged at `ab173f2a`; no commit/push.
- The sole file written by this review is this `PRE_RESULT_REVIEW.md`.
