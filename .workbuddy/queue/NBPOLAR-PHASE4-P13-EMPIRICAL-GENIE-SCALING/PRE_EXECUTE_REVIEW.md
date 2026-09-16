# Pre-EXECUTE review — NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING (Tier-Y)

## Verdict: PASS

The frozen command may be executed exactly once by the Wave-C operator under the exit-code/label rule in §7 (Wave-C rule) below. All ten required checks pass. The four operator-flagged items are adjudicated (all ratified, with precise rules). No blocking issue was found.

Independent reviewer scope: read-only review of the frozen packet, OpenSpec P13 delta, new runner + focused tests, and accepted predecessors. The V25 `channel_counts.npz` content was never opened (stat size only). The real gate command was never run. No Model-F/HOLD/raw/real/EVAL/tag/FWHT/APP/SCL access; no old-root writes; no commit/push.

---

## 1. STATUS exactness — PASS

Exact command + raw evidence:

```
cat .workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/STATUS.yaml
---
task_id: NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING
state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE
tier: Y
predecessors:
  - TARGET_EMPIRICAL_LOWER_RATE_POINT_ACCEPTED
  - EXACT_CHUNKED_SC_ACCEPTED
  - P12_BLOCKED_RESOURCE_LIMITS
  - X13R1_COMPLETE_DESCRIPTIVE_ONLY
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

- `execution_authorized: true` ✓; reads 0/1, attempts 0/1, `result: null` ✓; both reviews `pending` ✓; `state`/`next_gate` as declared ✓.
- Matches packet P13-07 authorization gate (TASK_PACKET.md:120-124, AUTHORIZATION_PROMPT.md:1) and freeze §6 consumption point (P13_FREEZE.md:127-139).

## 2. OpenSpec P13 delta consistency — PASS

Commands:

```
cat openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p13/spec.md  # 158 lines
grep -n "^- \[ \]" openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md | tail  # P13-1..P13-9 all "[ ]"
```

- Matrix/construction/allocation/decision-rule/gates/labels/scope in spec.md match TASK_PACKET.md P13-01..P13-05 exactly:
  - Input/support/preconditions: spec.md:18-43 (source 1M, 25166822-byte stat, one read/one attempt at first open, P7 floor-only rule, H1/H2/total literals within 1e-12, floor change ≤1e-9) = packet P13-01 (TASK_PACKET.md:11-24).
  - Matrix: spec.md:45-64 (N=4096/8192/16384, 4 TRAIN×2 + 4 DEV×8 per N, per-stream RNG restart, B~p_b then A~P_floor once, oracle-conditioned L1 true-U1 / L2 true-U1+U2, no tag/Toeplitz) = packet P13-02 (TASK_PACKET.md:26-44).
  - Construction/allocation/DEV: spec.md:66-86 (pooled means, worst-first (e,h,index), K_total=floor((1.3·N·H−64)/5) clipped [0,2N], exhaustive (K1,K2) lexicographic (residual,K1,K2) frozen before DEV, scalar R + same-rows BEC report-only with zero extra SC, t-UCB 1.695518782 df=31, proxy-not-FER) = packet P13-03 (TASK_PACKET.md:46-68).
  - Decision: spec.md:88-109 (12 gates in frozen order, CANDIDATE iff empirical UCB≤0.01 smallest N, NOT_CONFIRMED, else BLOCKED(earliest), BEC report-only, proxy-not-FER wording) = packet P13-04 (TASK_PACKET.md:70-86).
  - CLI/five-file/checkpointing/scope: spec.md:111-140 (11 required flags no defaults, absent-root/chunk-512/seed-grouping refusals pre-open, five files pre-open + per-block/N checkpoint no sidecars, scalar-only, wall/RSS/VmPeak/VmSize, env + 2 GiB + 1800 s, MemoryError→BLOCKED never rerun, forbidden list) = packet P13-05 (TASK_PACKET.md:88-109).
- All nine P13 boxes unchecked: `grep` shows `- [ ] P13-1` through `- [ ] P13-9` (tasks.md:544-599), with ownership banner tasks.md:541-542 ("owned by the main thread; never checks its own boxes") and evidence footer tasks.md:602-606 (gate not run, root absent).
- Docs authorize no production behavior: spec.md:16 ("This document authorizes no production behavior."), tasks.md:544-546, P13_FREEZE.md:8-12 ("It authorizes nothing"), P13_IMPLEMENTATION_NOTES.md contains no authorization language.

## 3. Reuse proof — PASS

Commands:

```
git status --porcelain  # tracked mods pre-existing cumulative; untracked P13 files additive
git diff --name-only HEAD  # 17 tracked files; none is the new P13 runner/test
git diff HEAD -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py  # P11 chunked-SC only
grep -rn "empirical_genie_scaling" comparison_bench/src/.../target_construction.py target_n_scaling.py sc.py prior.py target_rate.py  # NO_BACKREF_OK
```

- `git status/diff` shows NO wave-attributable change to `sc.py`/`prior.py`/`target_n_scaling.py`/`target_rate.py`/`target_construction.py`/loader/old roots from this wave:
  - Tracked `sc.py` diff is exactly the accepted P11 chunked contract (`_minus_block(..., *, chunk_rows=512)` keyword-only, sc.py:176-177; `sc_decode` exposes no chunk arg, sc.py:216), covered by predecessor `EXACT_CHUNKED_SC_ACCEPTED`. P13 only CALLS it via the accepted `genie_conditionals` choke point (empirical_genie_scaling.py:102,541-552) and contract-checks it pre-open (empirical_genie_scaling.py:380-396). No `sc_decode(` functional call in the runner (only the contract-check string + docstring, verified `FORBIDDEN_TOKENS_ABSENT_OK`).
  - `target_construction.py` / `target_n_scaling.py` / `target_rate.py` are untracked pre-existing predecessor files (never in HEAD `ab173f2a`); P13 imports only `PRECONDITION_ORDER, TargetPopulationContractError, target_preconditions` (empirical_genie_scaling.py:111-115) and `allocate_layer_ks, budget_k_total` (empirical_genie_scaling.py:116) — read-only, no back-reference (grep `NO_BACKREF_OK`).
  - Loader `load_v25_channel_counts` imported once (empirical_genie_scaling.py:100), called once in NPZ mode (empirical_genie_scaling.py:868); no other source-file change beyond the allowed manifest (new runner + new test + P13 spec dir + P13 tasks section + P13 queue freeze/notes).
- R3 scoping detail in §7.

## 4. Frozen budget — PASS (independently recomputed)

Command:

```
python3 -c "import math; H=0.8010378248977232; [print(N, repr((1.3*N*H-64)/5), math.floor((1.3*N*H-64)/5)) for N in (4096,8192,16384)]"
```

Raw evidence (both float64 spellings far from integer boundaries):

| N | raw with 0.8010378248977232 (EXPECTED_TOTAL) | raw with 0.8010378248977231 (float64 H1+H2) | floor |
|---:|---|---|---:|
| 4096 | 840.2732420030794 (frac .27) | 840.2732420030792 (frac .27) | 840 |
| 8192 | 1693.3464840061588 (frac .35) | 1693.3464840061583 (frac .35) | 1693 |
| 16384 | 3399.4929680123178 (frac .49) | 3399.492968012317 (frac .49) | 3399 |

Matches operator-reported K_TOTAL 840/1693/3399 and freeze table (P13_FREEZE.md:49-53) plus `test_frozen_k_total_pinned` (test file:122-133, 20/20 green).

- Clipping `[0,2N]` in accepted helper `budget_k_total` (target_n_scaling.py:421-429: `max(0,min(2n,raw))`); runner enforces `k_total>2n` refusal (empirical_genie_scaling.py:471-472) and leakage `5·K+64 ≤ 1.3·N·H` recheck (empirical_genie_scaling.py:1024-1031).
- Lexicographic `(e-sum,K1,K2)` split selection: `select_empirical_split` (empirical_genie_scaling.py:461-497) orders via accepted `disclosure_order_from_stats` (empirical_genie_scaling.py:479-480; construction.py:104-111 worst-first `(e,h,index)`), enumerates `K1 in [max(0,K−N),min(N,K)]` (empirical_genie_scaling.py:481), key `(residual,K1,K2)` (empirical_genie_scaling.py:486). Covered by `test_empirical_order_and_ties` + `test_exhaustive_split_selection_with_ties` (test:192-220).
- BEC report-only allocation via accepted `allocate_layer_ks` (empirical_genie_scaling.py:1032,1441); pinned splits (37,803)/3.363831923437399, (80,1613)/2.264840263288221, (166,3233)/1.2717801865443192 reproduced by `test_frozen_bec_report_only_splits_pinned` (test:136-145).
- Freeze-before-first-DEV in code order: TRAIN pool (empirical_genie_scaling.py:1034-1078) → `select_empirical_split` + freeze SHA (empirical_genie_scaling.py:1080-1139) → per-N cell record → DEV loop (empirical_genie_scaling.py:1154+). Replay gate re-derives from literals + pooled risks (empirical_genie_scaling.py:1427-1459).
- P7 empirical orders never imported: `grep empirical_orders|target_entropies|build_target_conditional|sample_target_block` → `NO_P7_EMPIRICAL_ORDERS_IMPORT_OK` (only `target_preconditions` + support pattern imported).

## 5. Refusal/consumption/checkpoint ordering — PASS

Code-order audit (empirical_genie_scaling.py):

- Absent-root refusal first: `if out_path.exists(): raise FileExistsError` (empirical_genie_scaling.py:792-793) before any stub creation, validated by `test_checkpoint_resume_refusal_zero_execution` (test:301-324: sentinel untouched, no new files, loader+genie patched to boom).
- CLI-parse refusal pre-open: `build_parser` requires all 11 flags (empirical_genie_scaling.py:1548-1569); `test_chunk_contract_and_cli_parse_refusals` asserts subprocess exit 2 with only `--counts x` (test:501-512).
- Chunk/seed refusals pre-open: `_check_chunk_contract` incl. `_minus_block` default-512 + keyword-only + `sc_decode` no-chunk checks (empirical_genie_scaling.py:380-396), N power-of-two + 4-per-N grouping + distinct/disjoint seeds (empirical_genie_scaling.py:802-824) — all before stub creation; `test_seed_grouping_enforced_before_open` proves no loader call and no dirs created (test:358-383).
- Five files created BEFORE content open: `mkdir` + `frozen_plan.json` + `construction_and_allocations.json` + `per_block_genie_residuals.jsonl` (empty) + `aggregate_summary.json` + `report.md` stubs (empirical_genie_scaling.py:836-853); NPZ stat + `load_v25_channel_counts` only after (empirical_genie_scaling.py:856-869). Same five checkpointed per block/N via `checkpoint()` (empirical_genie_scaling.py:948-958,1212-1224,1288), no sidecars (only OUTPUT_FILES tuple, empirical_genie_scaling.py:247-253; writes grep shows only `out_path` targets).
- Preconditions after open but before ANY genie: `target_preconditions` (empirical_genie_scaling.py:921-932) precedes first `block_genie_risks` (TRAIN line 1064 / DEV line 1181); zero-genie probe `test_precondition_failure_zero_genie_and_blocked_stubs` passes with `seen==0` and BLOCKED stubs (test:327-355).
- Consumption at first content open with reopen guard: `_NPZ_CONTENT_OPENED` module guard (empirical_genie_scaling.py:281,857-869), `accounting` 1/1 + `open_count` 1 in NPZ mode (empirical_genie_scaling.py:873-891) vs 0/0 injected (empirical_genie_scaling.py:892-912); `test_no_production_loader_on_injected_path` confirms injected accounting 0/0 (test:386-398).
- MemoryError/resource path preserves checkpoints + finalizes BLOCKED if possible: `except MemoryError` → BLOCKED stubs + `EmpiricalGenieScalingResourceError` never rerun (empirical_genie_scaling.py:1322-1343); `_budget_exceeded` TRAIN/DEV → same error (empirical_genie_scaling.py:1040-1045,1157-1162); `except EmpiricalGenieScalingResourceError: raise` preserves checkpoints (empirical_genie_scaling.py:1299-1300). Covered by `test_memory_error_classification_path` + `test_resource_stop_path_is_blocked_error` (test:466-498).
- Post-open no-repair/no-rerun: `except TargetPopulationContractError` best-effort BLOCKED into existing stubs then fail closed (empirical_genie_scaling.py:1301-1321); freeze §6 + packet P13-07 prohibit any seed/order/allocation/threshold change after open.

## 6. Matrix/decision — PASS

- N/seeds/blocks exact: `FROZEN_N_VALUES=(4096,8192,16384)` (empirical_genie_scaling.py:132), `FROZEN_TRAIN_SEEDS` 12 in N order 1860..63/1880..83/1900..03 (empirical_genie_scaling.py:133-137), `FROZEN_DEV_SEEDS` 1870..73/1890..93/1910..13 (empirical_genie_scaling.py:138-142), TRAIN 2 / DEV 8 per stream (empirical_genie_scaling.py:143-146) → 8 TRAIN + 32 DEV per N, 120 blocks total (24 TRAIN + 96 DEV). N-to-seed slicing `train_list[4·pos:4·pos+4]` (empirical_genie_scaling.py:1022-1023); per-stream `np.random.default_rng(seed)` restart (empirical_genie_scaling.py:1038,1155).
- `B~p_b + A~P_floor` once per block via accepted `sample_full_block(rng, entropy.p_b, entropy.f, Q, Q, n)` (empirical_genie_scaling.py:1046-1048,1163-1165); sampler does `sample_bob` then one `rng.random(n)` column draw (empirical_channel.py:294-324).
- Oracle-conditioned genie: L1 `Provenance.PRIOR_ONLY` (empirical_genie_scaling.py:1051-1056,1169-1174), L2 `Provenance.ORACLE_CONDITIONED` on true high (empirical_genie_scaling.py:1057-1062,1175-1180); choke point `genie_layer_risks→genie_conditionals` counted even on raise (empirical_genie_scaling.py:531-546); TRAIN `ImpossibleDisclosedValueError` → skip + `zero_genie_exceptions` fail (empirical_genie_scaling.py:1068-1071,1479-1481); DEV exception → block error record gate fails (empirical_genie_scaling.py:1196-1205).
- NO tag/Toeplitz master anywhere functional: `grep toeplitz_tag|TAG_BITS|seed_bits_for|load_v31|parquet|TTBin|ttbin|fwht|sc_decode(|HOLD_|EVAL_` → absent (only prose "No tag or Toeplitz master" scope lines + `sc_decode` contract-check string); `not hasattr(egs,"sc_decode")/toeplitz_tag` asserted (test:515-527).
- chunk_rows=512 plumbed: `FROZEN_CHUNK_ROWS=512` (empirical_genie_scaling.py:147), `_check_chunk_contract` enforces 512 + `_minus_block` default-512 contract (empirical_genie_scaling.py:380-396); every genie call flows through accepted chunked SC (`genie_conditionals→sc_decode→_minus_block` default path, sc.py:176-177,216-255, construction.py:83-95).
- Pooled-risks-only persistence: cell persists `l1_order/l2_order/pooled_e1/h1/e2/h2_means` + BEC report-only orders (empirical_genie_scaling.py:1112-1127); per-block JSONL holds only `{n,stream_seed,block_index,r_empirical,r_bec,error}` (empirical_genie_scaling.py:1186-1193); `test_output_keys_carry_no_truth` bans bob/high/low/u1_true/u2_true/a_full/counts/logp/decision_metrics/high_hat/label_hat/seed_bits/rng_state/p_b/f_full (test:438-463); `test_tiny_end_to_end_files_calls_and_gates` asserts scalar-only (test:401-435).
- `(e,h,index)` worst-first: accepted `disclosure_order_from_stats` (construction.py:104-111), pinned tie order `[1,0,3,2]` (test:192-204).
- DEV scalar R + BEC report-only SAME rows zero extra SC: `dev_block_residuals` pure re-indexing (empirical_genie_scaling.py:556-571); call-count test patches `genie_conditionals` to boom and still computes both arms (test:255-271); tiny E2E `genie==24==planned` (test:401-418).
- t-UCB factor exactly `1.695518782` (empirical_genie_scaling.py:171), `mean+T·std/sqrt(32)` only when n==32 else None (empirical_genie_scaling.py:500-528); literal recomputed from `math.fsum` (test:239-252).
- Decision rule: `ucb≤0.01→CANDIDATE smallest N; integrity pass but none→NOT_CONFIRMED; else BLOCKED(earliest)` (empirical_genie_scaling.py:1262-1284; labels empirical_genie_scaling.py:174-175; threshold empirical_genie_scaling.py:172); proxy-not-FER wording in `RESIDUAL_SCOPE`/`CLAIM_SCOPE`/report header (empirical_genie_scaling.py:227-231,272-278,711).
- Truth isolation: provenance counters + `truth_isolation: violations==0` (empirical_genie_scaling.py:1483,1540); no DEV-based tuning possible (DEV loop only appends residuals + checkpoints, empirical_genie_scaling.py:1154-1224; split replay uses pooled TRAIN only, empirical_genie_scaling.py:1433-1440; `test_train_dev_separation_no_dev_leakage` mutation check, test:274-296).

## 7. Operator-flagged items — adjudications

### (R1) 2026091900..1903 numeral overlap — RATIFIED FRESH (rule below)

Evidence:

```
grep TEST_SEED test_nbpolar_target_n_scaling.py  # 2026091900..1907 test-local
grep FROZEN_STREAM_SEEDS target_n_scaling.py     # official P12 streams 2026091820..1825
grep FROZEN_TRAIN_SEEDS empirical_genie_scaling.py  # P13 N=16384 TRAIN 2026091900..1903
grep "202609182" test_nbpolar_target_n_scaling.py  # only line-7 docstring, never as input
```

- P12's consumed scientific streams are exactly 1820..1825 (P12_FREEZE.md:21-26,84; target_n_scaling.py:132). P12's `2026091900..1907` appear ONLY as injected-test seeds (`injected_counts()` + `counts=` seam + `forbidden_loader` patches, test_nbpolar_target_n_scaling.py:42-47,85,459-499) with `input_mode=injected_counts`, zero NPZ opens, zero target-model draws.
- P13's frozen streams 1860..1913 are numerically disjoint from every consumed stream (P7 1650-1664, P9 grids 1680-1724, P11 gate 1800, P12 1820-1825, probes). The 1900..1903 coincidence is with unconsumed test-local numerals only — same pattern as the P8 seed-coincidence already ratified FRESH.
- **Freshness rule (precise):** a frozen stream is scientifically fresh iff it is disjoint from every stream consumed against the V25 target artifact (official gate streams + any probe that opened the NPZ). Test-local injected numerals that never opened the artifact and never sampled the target tables do not consume freshness, regardless of numeral equality. Deterministic RNG streams are functions of (seed, target tables, sampling path); injected tables + patched loader share neither tables nor path with the gate.
- P13 satisfies the rule; P13's own focused tests use fresh 2026091620..1629 and never the frozen 1860..1913 (test_nbpolar_empirical_genie_scaling.py:33-47). No action. Wave-C must still use the frozen seeds verbatim (no substitution).

### (R2) 262-vs-true-total + full-suite triage — RATIFIED (305-gate sufficient)

Evidence:

```
pinned interpreter: /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q -p no:cacheprovider
focused P13 file: 20 passed in 9.39 s --basetemp=/tmp/p13-preexec-focused
NB-Polar subset (test_nbpolar_*.py): 305 passed in 145.46 s --basetemp=/tmp/p13-preexec-allnbpolar2
grep -rln empirical_genie_scaling comparison_bench/tests/  # only the new focused file (+pycache)
```

- Packet text cites "262-test predecessor suite" (TASK_PACKET.md:118); true accepted NB-Polar total is 285 after P12's +23, plus 20 new P13 = 305. The 262 figure is a stale-count cosmetic error, not a scope error — implementation notes §3 already correct it (P13_IMPLEMENTATION_NOTES.md:66-69).
- Freeze-reported full `comparison_bench/tests` triage (2117 passed / 468 failed / 22 collection errors, P13_FREEZE.md:168-172) was NOT re-run here (4617 s, out of Tier-Y gate scope). Instead: (i) all-NB-Polar 305/305 green re-proven above; (ii) `grep` proves no failing-file candidate references the new module (`NO_NONNBPOLAR_REF_OK`); (iii) freeze documents all 468 failures in legacy LDPC/nonbinary/v-series files (missing sibling artifacts, `D:/` fixtures under WSL), zero in any `test_nbpolar_*`.
- **Sufficiency rule:** for this Tier-Y gate the test gate is the focused 20/20 + the NB-Polar 305/305 (injected tables, temp roots, fresh seeds, never NPZ/frozen streams/production paths — verified §8). The full-suite remainder is environmental/pre-existing and out of wave scope; reported, not fixed, per research-code policy. RATIFIED.

### (R3) Dirty-worktree scoping — RATIFIED (wave-scoped, additive)

Evidence:

```
git log --oneline -1  # ab173f2a (HEAD unchanged, no commit)
git status --porcelain  # 17 tracked mods (cumulative P3..P13 incl. tasks.md +553) + additive untracked P13 files
git diff HEAD --stat  # tasks.md +553 spans P3..P13, not P13 alone
```

- HEAD is unchanged (`ab173f2a`); no commit was made. Tracked modifications (P3 queue files, AGENTS.md/memory/docs, `__init__.py`, `empirical_channel.py`, `empirical_diagnostic.py`, `empirical_oracle.py`, `sc.py`, tests) predate/cumulate across waves — implementation notes R3 discloses them (P13_IMPLEMENTATION_NOTES.md:94-98) and this wave touched none (proven by NO_BACKREF + import-only §3).
- P13 wave delta is additive: untracked `formal_ir/nbpolar/empirical_genie_scaling.py` (1609 lines), `tests/test_nbpolar_empirical_genie_scaling.py` (527 lines), `specs/nbpolar-phase4-p13/spec.md`, P13 tasks section (tasks.md:539-606), and the P13 queue dir (TASK_PACKET/STATUS/PROMPT/AUTHORIZATION + freeze/notes). `tasks.md` +553 cannot be attributed to P13 alone (spans P3..P13 from a pre-P-phase HEAD) — cosmetic baseline artifact, not a P13 scope violation.
- No accepted-module/old-root writes from this wave; writes confined to the absent-until-authorized gate root. RATIFIED with the note that Wave-C must re-verify `git status` dirtiness is still non-destructive before execution.

### (R4) Report renderer tolerating RUNNING partials — RATIFIED (no leak, unmistakable)

- `_render_report` (empirical_genie_scaling.py:687-764) renders only scalar plan/entropy-aggregate/per-N K+residual-stats/resources/gates/outcome/scope fields. It never touches counts, sampled symbols, truth vectors, decoder outputs, metric planes, or RNG state (persistence allow-list §6 + banned-keys test).
- Partial path `checkpoint(partial_summary(f"RUNNING({len})",...))` (empirical_genie_scaling.py:1212-1224) reuses the full-schema summary with `outcome_label=RUNNING(n)`, missing N cells rendered as `pending` rows (empirical_genie_scaling.py:719-721,739-741), `empirical/bec=None→None` cells, and failing gates listed. `RUNNING(...)` is textually distinct from `CANDIDATE`/`NOT_CONFIRMED`/`BLOCKED(...)`; pending rows + false gates prevent mistaking a partial for completed evidence. Final summaries always carry full keys (asserted by `test_tiny_end_to_end_files_calls_and_gates`, test:401-435). RATIFIED.

### (Wave-C exit-code/label reading rule, carried over from P12 with P13 adaptation) — BINDING

P13 diverges from P12 (stub-then-checkpoint vs P12 no-root refusal):

- `main()` (empirical_genie_scaling.py:1572-1605): `ValueError/FileExistsError/OSError` (pre-open refusals incl. existing-root, CLI parse, chunk/seed grouping, size mismatch) → stderr + exit 2, consumption intact (no open). Completed runs (integrity pass OR integrity-fail final summary incl. `BLOCKED(earliest)`) → stdout JSON + exit 0 with `outcome_label` persisted in all five files.
- Post-open contract/resource failures (`TargetPopulationContractError`, `EmpiricalGenieScalingResourceError`, `MemoryError`-derived) propagate as exceptions (non-zero, non-2 traceback) AFTER best-effort BLOCKED stubs are finalized into the pre-created five files (empirical_genie_scaling.py:1299-1343) — consumption spent.
- **Operator rule:** (i) exit 0 ⟺ completed label persisted → read `aggregate_summary.json:outcome_label` (`CANDIDATE` = completed gate meeting UCB≤0.01; `NOT_CONFIRMED` = completed gate meeting integrity but no N meets UCB; `BLOCKED(<earliest>)` = completed-but-blocked — none is operational FER/success); (ii) exit 2 → STOP, preserve stderr + freeze doc, classify pre-open (consumption intact) vs post-open contract named in the message (consumption spent, no rerun); (iii) any other non-zero → STOP as unknown, preserve checkpoint stubs + stderr, no rerun. Never reinterpret exit code as the scientific outcome; never rerun after any open.

## 8. Tests — PASS (20 + 305 re-run, pinned interpreter, fresh basetemps)

```
 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/p13-preexec-focused comparison_bench/tests/test_nbpolar_empirical_genie_scaling.py
 → 20 passed in 9.39 s
 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/p13-preexec-allnbpolar2 comparison_bench/tests/test_nbpolar_*.py
 → 305 passed in 145.46 s
```

- Coverage vs P13-06 list (TASK_PACKET.md:113-118): literal tiny genie oracle (test:161-187) ✓; empirical order/ties (test:192-220) ✓; K budget + exhaustive split + clip edges (test:122-156) ✓; TRAIN/DEV separation replay (test:274-296) ✓; scalar DEV residual (test:223-236) ✓; t-UCB literal incl. non-32 None seam (test:239-252) ✓; BEC report-only zero-extra-SC (test:255-271) ✓; checkpoint-resume refusal (test:301-324) ✓; precondition zero-genie + BLOCKED stubs (test:327-355) ✓; seed/chunk grouping pre-open (test:358-383) ✓; one-open/one-attempt injected accounting (test:386-398) ✓; tiny E2E files/calls/gates (test:401-435) ✓; no-truth keys (test:438-463) ✓; MemoryError + resource-stop BLOCKED (test:466-498) ✓; chunk/CLI + no-production-rule (test:501-527) ✓.
- Tests never open the NPZ (only `forbidden_loader` patches + docstrings), never use frozen streams 1860..1913 (fresh 1620..1629 only, test:33-47), never invoke production paths (injected 1024×1024 tables, temp roots, fake genie/budget seams).

## 9. Bounded smoke — PASS (injected tiny tables, temp root)

```
python (pinned venv): injected 1024×1024 table, N=[64], TRAIN 4×1 + DEV 4×2, temp root
→ files: [aggregate_summary.json, construction_and_allocations.json, frozen_plan.json, per_block_genie_residuals.jsonl, report.md]
→ genie_calls 24 == planned 24; outcome BLOCKED(three_n_cells_complete) [expected non-frozen shape]
→ wall 0.319 s, RSS 209.5 MB → margin vs 1800 s ≈5640×, vs 2 GiB ≈9.8× at tiny N
→ _NPZ_CONTENT_OPENED still False
```

- Five files created pre-open + checkpointed, gates recorded, scalar-only. Tiny-smoke margin does NOT prove the N=16384×40-block workload fits 1800 s/2 GiB.
- Cost-driver statement: genie SC calls dominate. Frozen run = 120 blocks × 2 calls = 240 genie calls (24 TRAIN×2 + 96 DEV×2; per-N 80), each an exact chunked SC at N=4096/8192/16384 (O(N log N) rows, chunk_rows=512 allocation-only). The safety net is the fail-closed `_budget_exceeded` wall/RSS guard → `BLOCKED(resource_limits_met_and_no_abort)` with checkpoints preserved, never rerun (empirical_genie_scaling.py:424-435,1040-1045,1157-1162,1299-1343). Same resource-abort lesson as P12 (N=262144 64 MiB alloc) applies at N=16384 scale.

## 10. Scope/premises — PASS

- `git status --porcelain` matches the declared Wave-A set modulo pre-existing cumulative dirt (adjudicated §7-R3); no accepted-module/old-root writes; HEAD `ab173f2a` unchanged; no commit (verified `git log --oneline -5`, branch `codex/nbpolar-phase0`).
- FROZEN root still absent: `test ! -e .../empirical_genie_scaling_gate → ROOT_ABSENT_OK`; queue dir holds only AUTHORIZATION_PROMPT/PROMPT/STATUS/TASK_PACKET + freeze/notes (no gate root).
- Reads/attempts still 0/1 (STATUS.yaml re-read at close); NPZ metadata stat only: `25166822 bytes` (matches `EXPECTED_NPZ_BYTES`, empirical_genie_scaling.py:149; spec.md:23; freeze §8).
- No gate execution, no side effects outside fresh /tmp basetemps + the review file itself.

---

## Complete frozen record

- K values: N=4096→840 (raw 840.2732420030792); N=8192→1693 (raw 1693.3464840061583); N=16384→3399 (raw 3399.492968012317). H1+H2 float64 = 0.8010378248977231; EXPECTED_TOTAL literal 0.8010378248977232 (1-ulp difference, floors identical, fracs .27/.35/.49). BEC report-only splits: (37,803)/3.363831923437399; (80,1613)/2.264840263288221; (166,3233)/1.2717801865443192.
- Seeds: TRAIN 2026091860..1863 (N=4096), 1880..1883 (N=8192), 1900..1903 (N=16384); DEV 1870..1873 / 1890..1893 / 1910..1913; 8 TRAIN + 32 DEV blocks per N; per-stream RNG restart.
- Command: the verbatim frozen bash block (TASK_PACKET.md:128-133 = P13_FREEZE.md:82-87 = FROZEN_COMMAND empirical_genie_scaling.py:255-271, byte-equivalent timeout line verified §6) with pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, `OPENBLAS/OMP/MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2`, `ulimit -v 2097152`, `timeout 1800`.
- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/` (absent).
- Budgets: 2 GiB virtual + 2 GiB RSS, 1800 s external + 1800 s internal wall guard, single-thread allocator env.
- Schema: exactly five files (`frozen_plan.json`, `construction_and_allocations.json`, `per_block_genie_residuals.jsonl`, `aggregate_summary.json`, `report.md`), stubs pre-open, checkpointed per block/N, no sidecars, scalar-only.
- Gates (frozen order): `target_population_contract`, `three_n_cells_complete`, `streams_disjoint_frozen`, `orders_valid_frozen_before_dev`, `budget_allocation_reproduced`, `risks_finite`, `zero_genie_exceptions`, `truth_isolation`, `no_unregistered_calls`, `checkpoint_accounting_consistent`, `attempt_read_accounting_exact`, `resource_limits_met_and_no_abort`.
- Labels: `TARGET_EMPIRICAL_GENIE_F13_SCALING_CANDIDATE` (≥1 N with DEV UCB≤0.01, smallest N recorded) / `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` / `BLOCKED(<earliest>)`; t-factor `1.695518782` (df=31); UCB threshold `0.01`; proxy-not-FER wording mandatory.

## Findings (file:line)

- Blocking: none.
- Non-blocking / notes:
  - Stale "262-test" count in TASK_PACKET.md:118 vs true 285/305 — cosmetic, corrected in freeze/notes; no repair required pre-execution (do not edit frozen packet).
  - `tasks.md` +553 spans P3..P13 from pre-P-phase HEAD — baseline artifact, not P13 scope creep; no action.
  - `main()` post-open BLOCKED paths raise (non-2) rather than returning 2 — intended STOP-with-stubs semantics; Wave-C must follow the §7 exit-code/label rule (read `outcome_label`, never rerun after open).

## Closure statements

- The V25 `channel_counts.npz` content was NOT opened during this review (metadata `stat` size `25166822` only; the single artifact read belongs to the gate run).
- Artifact reads/attempts are still 0/1 (`artifact_reads_used: 0`, `attempts_used: 0`, `result: null`, both reviews `pending` save this file).
- The target root `empirical_genie_scaling_gate/` is still absent.
- No files were modified except this `PRE_EXECUTE_REVIEW.md`; no commit/push was made.
