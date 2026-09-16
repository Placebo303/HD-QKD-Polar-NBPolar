# P17 Pre-EXECUTE review — N=32768 operational replication (Tier-Y)

Packet: `NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION`
Reviewer: independent Pre-EXECUTE (read-only; did not write the code).
Scope: Wave-A implementation only (OpenSpec delta + runner + tests + freeze). No gate execution authorized by this review alone; main-thread acceptance remains separate.

```
Verdict: PASS
```

All 11 required checks PASS. No blocking issue. Three non-blocking notes (R1 wart ratified, stacked-worktree scope reading, wall-margin conservatism) are recorded below; none blocks execution. Human review not required beyond the mandatory Pre-RESULT gate (standard Tier-Y lifecycle).

---

## 1. STATUS exactness — PASS

Command:

```bash
cat .workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/STATUS.yaml
```

Raw evidence (13 lines, verbatim):

```yaml
task_id: NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION
state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE
tier: Y
predecessor: TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE_ACCEPTED_ZERO_MARGIN
execution_authorized: true
artifact_reads_allowed: 1
artifact_reads_used: 0
attempts_allowed: 1
attempts_used: 0
result: null
pre_execute_review: pending
pre_result_review: pending
next_gate: INDEPENDENT_PRE_EXECUTE
```

Check: `execution_authorized true` ✓; reads 0/1 ✓; attempts 0/1 ✓; `result: null` ✓; both reviews `pending` ✓; `state`/`next_gate` exactly as declared (`IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE` / `INDEPENDENT_PRE_EXECUTE`) ✓. `PROMPT.md` (implement + Pre-EXECUTE-then-execute + Pre-RESULT, no commit/scope) and `AUTHORIZATION_PROMPT.md` (full Tier-Y authorization incl. one 128-block attempt, one NPZ open, no TRAIN/genie/BEC/adaptive/Model-F/HOLD/raw/real/EVAL/FWHT/APP/SCL/qualification/promotion/P12-P16/old-root/commit/push, STOP on any failure) are consistent with this state; neither authorizes production behavior beyond the frozen gate.

## 2. OpenSpec P17 delta consistency — PASS

Files:

- `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p17/spec.md` (171 lines, new)
- `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` P17 section lines 852–941 (9 boxes, all unchecked)
- `P17_FREEZE.md` (144 lines, authorizes nothing), `P17_IMPLEMENTATION_NOTES.md` (107 lines)

Commands:

```bash
rg -n "^- \[ \] P17|^- \[x\] P17" openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md
rg -n "authorizes nothing|no production|This document authorizes" openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p17/spec.md
```

Raw: 9× `- [ ] P17-1..P17-9` (lines 857, 860, 884, 892, 910, 917, 921, 925, 929); 0× `- [x] P17`. Spec line 16–17: “status, acceptance and route disposition are owned by the main thread, never by the implementing session. This document authorizes no production behavior.” Tasks lines 854–855 + 940–941: “implementing session reports evidence only and never checks its own boxes… No box above is checked by the implementing session.” Freeze §1 + notes §R-list repeat the no-authorization / no-checked-box rule.

Consistency vs `TASK_PACKET.md` (107 lines): predecessor-identity (spec §Requirement 1 ↔ P17-01 digest `055c90…c3faea1b`, N/K1/K2/orders, P16 immutable, mismatch→STOP); replication matrix (spec §2 ↔ P17-02: N=32768, K1=319/K2=6492, orders, chunk_rows=512, DEV 2026092030..2037×16=128, per-stream restart, master+10000 P17/N/block domain, single-arm disclosed-L1-SC → candidate-only-L2-metric → restarted-disclosed-L2-SC → 10-bit label → ONE 64-bit tag → ONE outcome, truth only in sampling/disclosed/tag/scoring); accounting/decision (spec §3 ↔ P17-03: 34119/327743, literal recount, 14 integrity gates in frozen order, exact≥121/128 + Wilson-LB≥0.90 over 128 P17 blocks only, P16 62/64 report-only with pinned-total structural exclusion, three labels); evidence/resources (spec §4 ↔ P17-04: absent root, exactly five scalar-only files pre-open + per-block checkpoint, MemoryError/BLOCKED/never-rerun, 2400 s / 2 GiB / single-thread env); bounded claim + dual independent review (spec §5 ↔ packet P17-03/04). P16-report-only rule explicit in spec lines 8–9, 106–117, 155–164 and tasks P17-2/P17-3/P17-4. No production default in CLI (13 required flags). No scope creep in delta.

## 3. Reuse + P16-immutability — PASS

Commands:

```bash
git rev-parse HEAD  # ab173f2a5e17336383a897b941080b731ba3dd9e (unchanged)
git diff --name-only  # 17 tracked modified files (P3/P4 stacked waves); NO P12-P16 gate modules, NO evidence roots, NO loader
git status --porcelain | head  # P17 wave files are untracked additions (see §11); HEAD unchanged; no commit
ls -la .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/
stat .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json
```

Raw P16 root (untouched, read-only stat): five files `aggregate_summary.json` 2586645 B / `construction_and_allocation.json` 2581862 B / `frozen_plan.json` 6991 B / `per_block_outcomes.jsonl` 42760 B / `report.md` 2529 B; mtime 2026-09-15 18:28 (before P17 runner 19:38 / tests 19:36 / spec 19:41 / freeze 20:22). Sizes identical to `P17_FREEZE.md` §8. No writes to `sc.py` from this wave: `git diff -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py` shows ONLY the accepted P11 chunked-`_minus_block` change (`chunk_rows=512` default, `None` = golden path, contract checks), which predates P17 and is reused read-only. P17 runner (`operational_f13_replication.py:106,109,111-115,117-123`) only CALLS accepted semantics: `opf.run_operational_block`, `opf.classify_operational_outcome`, `opf._block_record/_abort_block/_record_dict_consistent/_transcript_mismatches/_order_is_permutation/_check_chunk_contract/_cell_resource_record/_peak_rss_bytes/_budget_exceeded/_write_json/_append_jsonl`, `target_preconditions`, `sample_full_block`, `wilson_lower_bound`, `make_gf32/polar_transform/labels_to_bits/seed_bits_for`, `toeplitz_tag/canonical_event`, `load_v25_channel_counts`. Structural review of the 1691-line runner confirms ZERO TRAIN/genie/BEC/adaptive/order-selection paths: functional token audit (`test_no_forbidden_access_rule`, test file lines 1038–1062) asserts absence of `block_genie_risks/select_empirical_split/budget_k_total/genie/Genie/GENIE/train/Train/TRAIN/adaptive/FWHT/rescue/analytic_order/allocate_layer_ks/load_v31/parquet/TTBin/ttbin/HOLD_/EVAL_/oracle/bec/BEC` in `opr.__file__` text — passes (25/25). Residual `raw`/`retry`/`second arm` hits are prose/accounting-field names (`raw-MLE`, `raw seed bits never persisted`, `retry_after_open: False`, “no second arm”), not code paths; the only counters are `calls={"sc":…}` (runner line 1123) with `set(calls)=={"sc"}` gate (lines 1531–1535) — no second counter exists.

## 4. Predecessor identity — PASS

Independent recompute (JSON read only, never the NPZ; pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`):

```bash
python -c "import json,hashlib,pathlib; p=pathlib.Path('.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json'); doc=json.loads(p.read_text()); cell=doc['cell']; payload={...same 10-key recipe...}; print(hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest())"
```

Raw: protocol `nbpolar-p16-operational-f13-gate` ✓; `frozen_before_first_dev True` ✓; N/K_total/K1/K2 = 32768/6811/319/6492 ✓; L1/L2 length 32768, both valid permutations ✓; stored `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` == recomputed == frozen flag ✓; K-replay `floor((1.3*32768*0.8010378248977232-64)/5)=6811`, `319+6492=6811` ✓; leakage `5*6811+64=34119`, `f=1.2998502888172847≤1.3` ✓. Runner pins the same values (`operational_f13_replication.py:130-141,160-162,172-178,476-492,495-581`): protocol-marker + frozen-before-DEV + N/K + permutation + stored==recomputed + flag==recomputed + K/f replay; mismatch raises before any root/open, consuming nothing.

Tamper probe (injected copy in `/tmp`, NEVER the real P16 root):

```bash
# fabricated 32768-perm file in /tmp with different orders → digest 4efb6a8c… ≠ frozen
opr.run_operational_replication(..., construction=fab_path, construction_digest=FROZEN, out_dir=/tmp/.../out-tamper)
# → ValueError: predecessor construction identity: digest flag != recomputed digest; root absent; _NPZ_CONTENT_OPENED False
```

Also: digest-flag pin (`runner lines 982–983`), absent-file, K/order/n/digest/protocol tampers — all refuse with zero execution and no root (focused tests lines 339–402, all green). PASS.

## 5. Operational replication audit + R1 adjudication — PASS (R1 RATIFIED, non-blocking wart)

Per-block flow (`runner lines 1257–1362` + P16 helper `operational_f13.py:708-837`): sample once (`sample_full_block`, per-stream RNG restart lines 1276–1281) → disclose true U1 at verified `order1[:K1]`, operational L1 SC (`calls["sc"]+1`) → L2 metrics ONLY from Bob + hard L1 candidate (`gather_p2_metrics(bob,high_hat)`, `CANDIDATE_CONDITIONED`; true high never enters) → disclose true U2 at verified `order2[:K2]`, restarted L2 SC → `label_hat=32*high_hat+low_hat` → exactly ONE 64-bit Toeplitz tag → `classify_operational_outcome` exactly one of six buckets with frozen precedence (`OUTCOME_PRECEDENCE` lines 259–266; `nonfinite` outranks `decode_failed`; `undetected` never success). Causal wiring + truth boundary verified by sentinel test (P16 helper internal truth copies + provenance `PRIOR_ONLY`/`CANDIDATE_CONDITIONED`, `truth_leak_violation` flag; runner `truth_ok` gate lines 1515–1518; `TRUTH_BOUNDARY` constant lines 238–243). No oracle/comparator/rescue/retry/adaptive/second tag: single `run_operational_block` call per block, single `tag_fn` closure, `PLANNED_SC_CALLS_MAX=256` / `PLANNED_TAG_INVOCATIONS=128` (lines 148–149), `no_unregistered_calls` recomputed from records (lines 1525–1535). Bucket exclusivity + precedence: `buckets_disjoint_exhaustive` (lines 1501–1513) + classifier test (test lines 497–518) + `undetected_zero`/`nonfinite_zero` gates (lines 1519–1523).

R1 (tag seam) adjudication — RATIFY, proceed:

- Fact: P16 helper `operational_f13.py:808` derives `seed = operational_seed_bits(master,n,block_index,…)` under prefix `nbpolar-p16-operational-f13-seed` (line 204), then calls `tag_fn(label_bits, seed, TAG_BITS)` (lines 819–820). P17 runner `lines 1286–1290` precomputes `p17_seed = replication_seed_bits(master,n,gidx,…)` under prefix `nbpolar-p17-operational-replication-seed` (line 209) and passes `def _tag_fn(bits,_seed,tag_bits,_fixed=p17_seed): return toeplitz_tag(bits,_fixed,tag_bits)` — the helper’s `_seed` argument is accepted but DISCARDED.
- Hence the helper-internal P16-domain array IS derived in-memory (CPU + transient allocation) but NEVER scored, NEVER persisted, NEVER leaves the call: the spy test (`test_p16_operational_parity_and_p17_tag_domain`, test lines 448–492) intercepts the actual `toeplitz_tag` seed — `seen` has exactly 2 entries (true tag + hat tag), both byte-equal to `p17_seed`, both DIFFERENT from `opf.operational_seed_bits(master,n,gidx)`. Scored/persisted domain is therefore EXACTLY P17/N/block; P16-domain bits reach no scoring, no event, no record, no file (banned-key walk test lines 1008–1035 confirms no `seed_bits` key in any of the five files).
- “Silent P16-domain reuse forbidden” is satisfied in the scored/persisted sense (the only sense the spec constrains: spec §2 “invoke exactly one 64-bit tag in the P17/N/block seed domain… prefix SHALL differ… raw seed bits SHALL NOT be persisted”; task P17-2 “no P16-domain tag reuse”). The residual in-memory derivation is a known wart (implementation notes R1), not a reuse: fixing it requires changing the accepted P16 helper, which is FORBIDDEN in this wave. The parity test’s scored-seed proof is SUFFICIENT (it observes the exact seeds that reach scoring). No repair before execution; optionally note the wart in the Wave-C report. Non-blocking.

## 6. Seeds/streams + R2 adjudication — PASS (R2 RATIFIED)

Frozen matrix (`runner lines 138–143`): `FROZEN_DEV_SEEDS = (2026092030,…,2026092037)`, `FROZEN_DEV_BLOCKS_PER_STREAM=16`, `FROZEN_DEV_TOTAL=128`. Per-stream RNG restart (`lines 1276–1278`: one cached `default_rng(seed)` per stream, slots sequential — exactly the frozen draw order). Repo grep:

```bash
rg -l --glob '*.py' "2026092030" .  # → only operational_f13_replication.py + its focused test
rg -n "2026092000|2026092010" comparison_bench/src/.../operational_f13_replication.py  # → only P16_PRIOR_STREAMS blocklist (lines 174-178)
```

All 8 streams fresh relative to P16 TRAIN `2026092000..2003` + DEV `2026092010..2017` (all 12 in blocklist) and all listed priors/probes (focused test lines 298–310 asserts disjointness incl. X11 `2026091760` + 14 prior seeds). Toeplitz master `seed+10000` (`PUBLIC_TAG_MASTER_OFFSET`, line 146; per-block `master=int(seed)+10000` line 1286) with domain `nbpolar-p17-operational-replication-seed:<master>:<n>:<block>` (lines 444–473; `SEED_PREFIX` ≠ P16’s, test lines 405–415 + parity proof). Full-run test asserts `arm.masters == {s: s+10000}` (line 615).

R2 (exact-seed pin as gate vs refusal) adjudication — RATIFY, consistent with P16 precedent and packet STOP semantics: structural refusals (before open, zero execution) cover count≠8, non-distinct, P16-overlap, digest-flag, contracts (`runner lines 988–1005`; tests lines 750–839). Exact-frozen-equality is a GATE (`_integrity_gates` lines 1460–1483: `shape_frozen` + `streams_ok`; `dev_coverage_complete`/`streams_disjoint_frozen`), so fresh-seed injected tests execute the pipeline but BLOCK (`BLOCKED(dev_coverage_complete)`, test lines 633–649). The frozen production CLI enforces the exact eight streams through those gates + the frozen command; a non-frozen production grouping could run but can never pass — STOP semantics preserved (no silent pass). No repair.

## 7. Non-pooling + decision + R4/R5 adjudication — PASS (R3/R4/R5 RATIFIED)

Decision inputs are EXACTLY the 128 P17 blocks: `recovery_gates(exact,total=128)` (lines 603–628) pins `exact_ok = (total==128 and exact≥121)`; any other total — including P16-shaped (62,64) — structurally fails (test lines 544–548). `_integrity_gates.coverage_ok` requires `len(dev_records)==128 and shape_frozen` when final (line 1478). P16 62/64 appears ONLY as `P16_REPORT_EXACT/TOTAL/WILSON_LB` constants (lines 197–199) → `predecessor_report_only` in plan/summary (lines 803–808, 1171–1176) → report.md discussion with explicit never-pooled statement (lines 892–898); zero reads in any gate (`rg P16_REPORT` hits only those report paths; `recovery_gates`/`select_label`/`_integrity_gates` take only P17 records/events). Test `test_p16_numbers_never_enter_decision` (lines 652–671) asserts `recovery.total==128`, `report_only.pooled_into_decision==False`, report contains `62/64` + `never pooled/zero weight`.

Scientific gates: exact≥121/128 AND one-sided 95% Wilson LB≥0.90 (`EXACT_MIN=121`, `WILSON_MIN=0.90`, lines 181–182). Independently recomputed (pinned interpreter, `protocol.wilson_lower_bound`, z=1.6448536269514722 + own implementation cross-check): 121/128→0.9021084760149684→round10 `0.9021084760` TRUE; 120/128→0.8924595822417636→`0.8924595822` FALSE; 62/64→0.9098711859061207→`0.9098711859` (report-only). Runner asserts both boundaries in code before first DEV (`check_wilson_boundary`, lines 584–600, tol 1e-9) and tests assert all three label branches (lines 523–562). Disclosure `5*(319+6492)+64=34119` + public `10*32768+63=327743` + literal N/arm-tagged recount with zero-mismatch gate (lines 669–747, 1537–1559); partial-failure counts only disclosed bits (test lines 695–714).

R4 (digest-recipe equality) — RATIFY: P17 `_canonical_digest` (lines 476–492) uses the identical 10-key set, `int`/`float` coercions, `sort_keys=True, separators=(",",":")` as P16’s freeze recipe (`operational_f13.py:1720–1736`) and verify path (lines 2015–2018). Byte-equality proven by §4 recompute (stored==recomputed==frozen).

R5 (abort-fill/MemoryError) — RATIFY: budget-stop abort-fills remaining blocks via `opf._abort_block` (zero-disclosure honest records), checkpoints the same five files per block, completes as `BLOCKED(resource_limits_met_and_no_abort)` (lines 1261–1273, 1364–1373); `MemoryError` preserves checkpoints, best-effort BLOCKED finalization, raises `ReplicationResourceError`, never reruns (lines 1317–1318, 1408–1429); `TargetPopulationContractError` best-effort BLOCKED stubs then fail-closed (lines 1387–1407). Tests: MemoryError classification (lines 921–944), abort-fill 126 aborts + checkpoints + BLOCKED (lines 947–982), precondition zero-call + BLOCKED stubs (lines 889–918). No fabrication path (abort records carry `resource_abort`, zero bits, no tag; `buckets_ok` + `resource_ok` gates force BLOCKED).

## 8. Refusal/consumption/checkpoint ordering — PASS

Order in `run_operational_replication` (lines 939–1048): absent-root (966–967) → CLI/floor/source/N/K/chunk/tag contracts (968–977) → digest-flag pin (982–983) → predecessor identity (984) → seed count/distinct/P16-overlap/grouping (988–1005) → create EXACTLY five files as stubs BEFORE content open (1017–1032, no sidecars) → stat-only size check + single accepted content open (1038–1048; `load_v25_channel_counts` exactly once; `_NPZ_CONTENT_OPENED` guard lines 316/1036–1037) → shape check → preconditions with ZERO SC calls (1095–1113; `calls={"sc":0}` created line 1123 AFTER preconditions) → Wilson pin (1117–1119) → DEV with per-block checkpoint of the same five files (1360–1362) → final gates/label/checkpoint (1364–1373).

Probes (this review, injected/`/tmp` only, real NPZ never touched):

- digest-flag mismatch → `ValueError: digest flag != frozen digest`, no root, `_NPZ_CONTENT_OPENED False` ✓
- existing root → `FileExistsError: refusing to overwrite`, sentinel intact, no sidecars ✓
- CLI missing flags → subprocess exit 2 ✓
- tampered injected construction (orders differ) → `ValueError: digest flag != recomputed digest`, no root, no open, real P16 root untouched ✓
- grouping/contract + checkpoint-resume + reopen-guard + precondition-zero-call + MemoryError + abort-fill — all covered by focused tests (lines 750–982) with `forbidden_loader/forbidden_arm` sentinels proving zero production calls on refusal ✓

Consumption: read 1/1 + attempt 1/1 together at first NPZ open in the frozen run (`accounting` lines 1052–1070; `attempt_read_accounting_exact` gate lines 1574–1597); injected tests consume 0/0 with `open_count 0` (lines 1071–1091); reopen refused (`ValueError: reopen refused`, test lines 867–886). Post-open: no repair/rerun/seed/N/K/floor/order/threshold/tag change (frozen-run contract; `retry_after_open False` throughout).

## 9. Tests — PASS (25 + 383 green, pinned interpreter, fresh basetemps)

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/p17-focused3-VoAa3J comparison_bench/tests/test_nbpolar_operational_f13_replication.py
# → 25 passed in 335.91s
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/p17-full-fYZ2uz comparison_bench/tests/test_nbpolar_*.py
# → 383 passed in 1560.83s
```

Matches operator report (25 focused; 383 total = 358 baseline + 25). Coverage vs P17-05 list: identity+tamper (323–402) ✓; zero-TRAIN/genie (313–318, 1038–1062) ✓; P16 parity + P17 tag-domain proof (448–492) ✓; all outcomes + precedence incl. nonfinite>decode_failed + undetected≠success (497–518, 674–692) ✓; Wilson 121/120 + three labels (523–562) ✓; pinned-128 non-pooling (544–548, 652–671) ✓; disclosure 34119/327743 + recount tamper (567–650, 695–738) ✓; fresh streams (298–310) ✓; checkpoint refusal (842–864) ✓; one-open/attempt + reopen guard (867–886) + precondition zero-call (889–918) + MemoryError (921–944) + abort-fill (947–982) ✓; scalar-only outputs (1008–1035) ✓; chunk/CLI refusals (985–1005) ✓; forbidden access (1038–1062) ✓.

Test hygiene: never opens the real NPZ (only `/nonexistent/channel_counts.npz` in the reopen-guard refusal path, which raises before touching the filesystem); never uses frozen streams 2030..37 as inputs (only asserts the frozen tuple value; all runs use `TEST_DEVS=2026091790..1797` + spares, disjoint from frozen/P16/priors/probes); accesses the real P16 root NEVER (not even read — identity tests fabricate files via `make_construction_file` in temp dirs); only injected 1024×1024 tables + temp roots + patched seams. `opr._NPZ_CONTENT_OPENED is False` asserted post-run (lines 585, 886, 944).

## 10. Wall/RSS projection — PASS (envelope holds; naive 18.5 s/block corrected)

Ground truth from accepted P16 gate (read-only):

```bash
python -c "import json,pathlib,statistics; recs=[json.loads(l) for l in pathlib.Path('.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/per_block_outcomes.jsonl').read_text().splitlines()]; walls=[r['wall_s'] for r in recs]; print(len(walls), statistics.mean(walls), min(walls), max(walls), sum(walls))"
# → 64 blocks, mean 12.3559619375 s, min 11.793906, max 13.153319, sum 790.781564 s
# aggregate_summary.json: wall_s 1183.61887, rss_bytes_peak 545861632, sc_calls 128, genie_calls 32 (16 TRAIN blocks × 2)
```

CORRECTION (check carefully as instructed): `1183.6/64 ≈ 18.5 s/block` is WRONG — it amortizes TRAIN + construction + load/preconditions/checkpoint overhead over DEV blocks. Isolated DEV cost is mean **12.356 s/block** (sum 790.78 s for 64 DEV). Overhead = 1183.61887 − 790.781564 = **392.84 s**, which includes NPZ load + P7 preconditions + 16 TRAIN genie blocks (32 genie calls) + construction/allocation search + 64-block checkpoint I/O + final gates. P17 performs ZERO TRAIN and NO construction search (orders arrive via the verified file; `CONSTRUCTION_RULE` lines 244–248), so its overhead is STRICTLY SMALLER than P16’s; using the full P16 overhead is a conservative upper bound.

Projection for 128 DEV-only blocks (256 SC calls, zero TRAIN) vs 2400 s cap:

- expected: `2 × 790.781564 + 392.837306 = 1974.40 s` → margin `2400 − 1974.40 = 425.60 s` (17.7%) ✓
- conservative (max per-block): `128 × 13.153319 + 392.837306 = 2076.46 s` → margin `323.54 s` (13.5%) ✓
- realistic (P17 overhead ≈ load/preconditions/verify + 128 checkpoints ≈ 200 s, no TRAIN/allocation): `1581.56 + 200 ≈ 1781.6 s` → margin ≈ 618 s (25.8%).

Envelope HOLDS in all three arithmetics. Per-block variance is tiny (σ≈0.30 s), so the mean projection is tight.

Bounded smoke (this wave): injected tiny tables + temp roots only — `test_full_run_128_exact_gates_and_accounting` (lines 567–650) runs 128 FakeArm blocks with real tables/orders/Wilson/gates/accounting/checkpointing, asserts exactly `OUTPUT_FILES`, 128 JSONL records, 256 SC / 128 tags, recount exact, gates recorded. No production path touched.

RSS: P16 peaked **545861632 B** (≈520.6 MiB) at the SAME N=32768 with the SAME per-block footprint (chunked SC `chunk_rows=512`, metric planes + pooled construction already loaded: orders 2×32768 int64 ≈ 0.5 MiB + pooled means). P17 runs blocks SEQUENTIALLY (same peak, not cumulative) with no TRAIN planes and no allocation-search residency; checkpoint JSON deltas are KiB-scale. Projected peak ≈ P16 peak ± few MiB ≪ 2 GiB cap (headroom ≈ 3.9×). `resource_limits_met_and_no_abort` gate enforces `rss ≤ 2147483648` + wall ≤ cap + zero aborts (lines 1598–1606); `VmPeak/VmSize` recorded per record. PASS.

## 11. Scope/premises — PASS

```bash
git status --porcelain  # HEAD ab173f2a unchanged; no commit
stat /mnt/d/Code/HD-QKD_Polar_Comparison/.../channel_counts.npz  # Size: 25166822
ls .workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/  # 6 files, NO operational_replication_gate/
cat .../STATUS.yaml  # reads/attempts still 0/0, result null
```

- `git status --porcelain` vs declared Wave-A set (implementation notes §Files changed, 7 items): untracked additions `comparison_bench/src/.../operational_f13_replication.py` (1691 lines), `comparison_bench/tests/test_nbpolar_operational_f13_replication.py` (1062 lines), `openspec/.../specs/nbpolar-phase4-p17/` (spec.md), `.workbuddy/queue/NBPOLAR-PHASE4-P17-.../` (packet dir: TASK_PACKET/STATUS/PROMPT/AUTHORIZATION/P17_FREEZE/P17_IMPLEMENTATION_NOTES + this review); tracked modification `openspec/.../tasks.md` (P17 §852–941 appended, boxes unchecked). The worktree additionally carries pre-existing stacked-wave modifications (17 tracked files incl. P11 `sc.py` chunking, P3 empirical files, docs/memory) and untracked P4–P16 wave dirs — all OUTSIDE this wave’s manifest and untouched by it (P17 runner/tests/spec reference but never modify them). No accepted-module/P12-P16/old-root writes from this wave; P16 root sizes/mtimes unchanged (§3); no `results/` or `comparison_bench/outputs_comparison/` writes; no commit/push (HEAD `ab173f2a`, log shows no new commit).
- HEAD unchanged ✓; no commit ✓; output root ABSENT ✓ (queue dir holds only the 6 packet files); reads/attempts still 0/0 ✓ (`STATUS.yaml` unmodified by review; `opr._NPZ_CONTENT_OPENED False` after all probes); NPZ metadata stat 25166822 only — content NEVER opened (no `load_v25_channel_counts` call with the real path in any test/probe/review command) ✓; P16 `construction_and_allocation.json` JSON-read only (digest recompute + stat), never written ✓.

---

## R1–R5 adjudications (summary)

- **R1 tag-seam: RATIFY, proceed (non-blocking wart).** Scored/persisted seeds are EXACTLY P17/N/block (spy proof §5); helper-internal P16-domain derivation is in-memory-only, never scored/persisted, and unfixable without touching accepted P16 code. No domain-separation violation. Record wart in Wave-C report; no repair.
- **R2 exact-seed pin as gate: RATIFY.** Structural refusals + exact-equality gates + frozen CLI jointly enforce the frozen matrix; consistent with P16 precedent and packet STOP semantics. Injected-test fresh seeds exercise the pipeline but BLOCK by design.
- **R3 non-pooling: RATIFY.** Total pinned to 128 structurally excludes 62/64; P16 context is report-only with `pooled_into_decision: False` and never enters any gate input (code + records-path audit §7).
- **R4 digest-recipe equality: RATIFY.** Identical 10-key recipe, separators, sort order; byte-equality proven by independent recompute (§4).
- **R5 abort-fill/MemoryError: RATIFY.** Checkpoints preserved, BLOCKED finalized if possible, never rerun, no fabrication path (§7–§8, tests cited).

## Wave-C exit-code / label reading rule (binding)

- `exit 0 ⟺ run completed with a persisted label — READ `aggregate_summary.json: outcome_label`` (covers `..._REPLICATION_CANDIDATE`, `..._REPLICATION_NOT_CONFIRMED`, AND integrity/resource `BLOCKED(<earliest gate>)` via abort-fill or gate failure, all checkpointed through `checkpoint(summary)`).
- `exit 2 = pre-open refusal (no root created OR existing root untouched; consumption 0) AND post-open contract `BLOCKED(target_population_contract)` (five BLOCKED stubs written; consumption spent) — DISAMBIGUATE BY ROOT/STUBS per P14/P16 precedent: absent root + `refused` on stderr → pre-open; five files with `outcome_label BLOCKED(target_population_contract)` → post-open. (`TargetPopulationContractError(ValueError)` is caught by `main`’s `except (ValueError,FileExistsError,OSError)` → 2; verified `target_construction.py:340`, runner `1651–1671`.)
- Other non-zero (notably `ReplicationResourceError(RuntimeError)` from `MemoryError`, uncaught → traceback, exit 1) = post-open resource/unexpected with checkpoints preserved and BLOCKED finalized if possible — NEVER rerun, NEVER repair, NEVER reuse the root. Any non-zero without the five-file inventory or with an unexpected traceback is post-open-unexpected → same no-rerun rule.

## Complete frozen record

- digest: `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` (recomputed §4; flag + stored + frozen all equal)
- N/K: 32768 / K_total 6811 / K1 319 / K2 6492; leakage `5*6811+64=34119`; `f=1.2998502888172847≤1.3`; L1/L2 valid 32768-perms; K-replay `floor((1.3*32768*H−64)/5)=6811`
- seeds: DEV `2026092030..2026092037` × 16 = 128 (per-stream restart); masters `seed+10000`; domain `nbpolar-p17-operational-replication-seed:<master>:<n>:<block>` (≠ P16’s); P16 streams `2026092000..2003` + `2026092010..2017` blocklisted
- command: frozen 13-flag command byte-identical across TASK_PACKET §P17-05 / `FROZEN_COMMAND` (runner lines 292–305) / `P17_FREEZE.md` §4 (verified single-line-normalized equality §8 + CLI `build_parser` 13 required dests)
- root: `.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate/` ABSENT; five files `frozen_plan.json / predecessor_construction_identity.json / per_block_outcomes.jsonl / aggregate_summary.json / report.md` pre-open + per-block checkpoint, no sidecars
- budgets: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2`, `ulimit -v 2097152` (2 GiB virtual), 2 GiB RSS cap, `timeout 2400` / `TOTAL_WALL_S 2400.0`; chunk_rows 512, tag-bits 64, source 1M, floor 1e-15; NPZ `channel_counts.npz` 25166822 B, shape (1024,1024), loader `v35_algorithm_development.load_v25_channel_counts`, one open, read 1/1 + attempt 1/1 at first open, no reopen
- schema: predecessor identity scalars + per-block scalar outcomes only (no counts/symbols/truth/decoded/metrics/seeds/RNG); per-record wall/RSS-HWM/VmPeak/VmSize
- gates: 14 integrity in frozen order (`INTEGRITY_GATE_ORDER` runner lines 268–283) + recovery exact≥121/128 AND Wilson-LB≥0.90; boundaries 121/128→`0.9021084760` PASS / 120/128→`0.8924595822` FAIL (recomputed §7); labels `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE` / `..._REPLICATION_NOT_CONFIRMED` / `BLOCKED(<earliest gate>)`; P16 62/64 + `0.9098711859` report-only, zero weight

## Findings (file:line)

- Blocking: none.
- Non-blocking: (1) R1 in-memory P16-seed derivation wart — `operational_f13.py:808` + `operational_f13_replication.py:1286-1290` (ratified §5, no action). (2) Dirty stacked worktree — P17 manifest exact per §11; reviewers should scope by file manifest, not raw `git diff` (pre-existing P11 `sc.py` chunking + P3/doc/memory modifications are not this wave). (3) Wall projection conservatism documented — P17 overhead strictly below P16’s; §10 gives three arithmetics, all passing.

## Closure statements

- The V25 `channel_counts.npz` content was NOT opened (metadata `stat` 25166822 B only; no loader call with the real path in any review/test/probe command).
- Artifact reads / scientific attempts are still 0 (`STATUS.yaml` 0/1 + 0/1, `result: null`; `opr._NPZ_CONTENT_OPENED False` after all probes; focused tests assert the same).
- The output root is still absent (queue dir holds only the 6 packet files; no `operational_replication_gate/`).
- The accepted P16 root is untouched (five-file sizes/mtimes identical to freeze; `construction_and_allocation.json` JSON-read only for the digest recompute; tamper probes used `/tmp` injected copies only).
- No commit/push was made (HEAD `ab173f2a` unchanged).
- No Model-F/HOLD/raw/real/EVAL/FWHT/APP/SCL access; no P12-P16/old-root writes.

Wave-C may proceed to the single authorized 128-block attempt under the frozen command and STOP rules. Independent Pre-RESULT review remains mandatory before any result/label publication.
