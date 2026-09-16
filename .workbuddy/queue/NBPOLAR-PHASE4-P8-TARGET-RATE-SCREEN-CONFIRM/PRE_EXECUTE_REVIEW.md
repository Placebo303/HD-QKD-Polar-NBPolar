# Pre-EXECUTE review — NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM

**Verdict: PASS**

Independent reviewer (did not write the code). Read-only review; the V25
`channel_counts.npz` content was never opened (stat metadata only). The real
gate command was never run. No Model-F/raw/held-out/real/EVAL data, no
old-root writes, no commit/push.

## 1. STATUS exactness — PASS

Command:

```bash
cat .workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/STATUS.yaml
git rev-parse HEAD
```

Raw evidence (`STATUS.yaml` verbatim):

```yaml
task_id: NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM
state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE
predecessor: TARGET_EMPIRICAL_CONSTRUCTION_ACCEPTED
documentation_authorized: true
implementation_authorized: true
artifact_read_authorized: true
decoder_execution_authorized: true
development_gate_authorized: true
artifact_reads_allowed: 1
artifact_reads_used: 0
attempts_allowed: 1
attempts_used: 0
real_data_authorized: false
eval_authorized: false
adaptive_authorized: false
scalable_decoder_authorized: false
scl_authorized: false
scientific_promotion: false
result: null
independent_pre_execute: pending
independent_pre_result: pending
next_gate: INDEPENDENT_PRE_EXECUTE
```

Check: five authorized flags (`documentation/implementation/artifact_read/
decoder_execution/development_gate`) are `true`; `real_data/eval/adaptive/
scalable_decoder/scl/scientific_promotion` are `false`; reads `0/1`,
attempts `0/1`; `result: null`; both independent reviews `pending`;
`state`/`next_gate` as declared. No drift.

## 2. OpenSpec P8 delta consistency — PASS

Commands:

```bash
grep -n "P8\|target_rate" openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md | head
grep -n "\[ \]\|\[x\]" openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md | tail -n 20
```

Evidence:

- Delta spec: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p8/spec.md`
  (7 Requirements: frozen input/orders/support; preconditions; SCREEN+selection;
  CONFIRM+BEC; accounting/recount; gates/labels; CLI/five-file/scope; bounded
  claim/review). Grids `K1=[8,10,12,16,24,32,45]` × `K2=[80,94,110,125,140]`,
  streams `2026091680..1682` ×64 / `2026091690..1694` ×128, selection
  lexicographic `(K1+K2,K1,K2)` over eligible only, Wilson `z=1.6448536269514722`
  `>=0.95`, labels `TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT` /
  `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE` /
  `TARGET_EMPIRICAL_RATE_POINT_NOT_CONFIRMED` / `BLOCKED(<earliest gate>)`,
  12-flag CLI, five-file root — all match `TASK_PACKET.md` P8-01..P8-07.
- Tasks P8 section `tasks.md:295-350`: P8-1..P8-9 all `- [ ]` (unchecked);
  prior P7 boxes remain `[x]`; P4 boxes remain `[ ]` (untouched future work).
  Evidence lines: `300:- [ ] P8-1` through `339:- [ ] P8-9`; footer
  `349-350: No box above is checked by the implementing session.`
- No production behavior authorized by docs: `spec.md:13-15` ("status,
  acceptance and route disposition are owned by the main thread, never by the
  implementing session"); `tasks.md:297-299` (same); `P8_FREEZE.md:7`
  ("FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing");
  `P8_IMPLEMENTATION_NOTES.md:3-4` ("Documentation only; this file authorizes
  nothing and checks no OpenSpec box").

## 3. Frozen identity — PASS

Commands (stat only, never open):

```bash
stat -c '%s %n' /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz
ls -la .workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm/
grep -rn "2026091690" --include="*.py" --include="*.md" . | head
```

Evidence:

- NPZ path: `/mnt/d/Code/HD-QKD_Polar_Comparison/.../run_04/channel_counts.npz`;
  `stat st_size == 25166822` (observed `25166822`, matches
  `target_rate.py:136 EXPECTED_NPZ_BYTES`, `TASK_PACKET.md:36-44`,
  `P8_FREEZE.md:46-48`). Content not opened by this review.
- Source `1M` (`target_rate.py:123 FROZEN_SOURCE`), floor `1e-15`
  (`target_rate.py:124 FROZEN_FLOOR`), N=256 (`target_rate.py:122 FROZEN_N`).
- P7 order identity `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`
  recomputed from the orders JSON only (JSON read, NPZ never touched):

```bash
python3 -c "import json,hashlib; doc=json.load(open('.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/construction_orders.json')); print(hashlib.sha256(json.dumps(doc['layers'],sort_keys=True,separators=(',',':')).encode()).hexdigest())"
# 8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104
# recorded == recomputed == frozen; both pooled orders valid 256-permutations (verified)
```

  Module enforces it at `target_rate.py:153 EXPECTED_ORDERS_SHA`,
  `447-501 validate_orders_doc`, `504-517 load_construction_orders`.
- SCREEN seeds `(2026091680,2026091681,2026091682)` ×64 =192
  (`target_rate.py:125-127`); CONFIRM `(2026091690..2026091694)` ×128 =640
  (`target_rate.py:131-133`); K1 `(8,10,12,16,24,32,45)` K2 `(80,94,110,125,140)`
  =35 (`target_rate.py:128-130`, `431-435 screen_grid`, `1284-1285` assert 35).
- Toeplitz master `stream+10000` with phase/arm/block separation:
  `target_rate.py:134 PUBLIC_TAG_MASTER_OFFSET=10000`,
  `273 SEED_PREFIX="nbpolar-p8-target-rate-seed"`,
  `611-634 arm_seed_bits` (`prefix = SEED_PREFIX:master:phase:arm:index`,
  SHA-256 counter expansion, `2623` bits), call sites `1448` (SCREEN
  `block.stream_seed+10000`) and `1579` (CONFIRM `seed+10000`), `810` per-block.
- Exact 12-flag command byte-identical across packet / freeze / module:
  packet `TASK_PACKET.md:130-134` == freeze `P8_FREEZE.md:184-188` (three lines
  `cd …` / `ulimit -v 2097152` / `timeout 3600 … -m …target_rate --counts … --source 1M
  --orders … --n 256 --floor 1e-15 --screen-seeds 2026091680 2026091681 2026091682
  --screen-blocks 64 --k1-grid 8 10 12 16 24 32 45 --k2-grid 80 94 110 125 140
  --confirm-seeds 2026091690 … 1694 --confirm-blocks 128 --out-dir …/rate_screen_confirm`);
  module `target_rate.py:254-266 FROZEN_COMMAND` reconstructs the same string;
  parser `2362-2384 build_parser` requires exactly those 12 flags (all
  `required=True`, no production default).
- Output root `rate_screen_confirm/` ABSENT now (`ls` → `No such file or directory`).
- Seed freshness (repo grep): CONFIRM `2026091690..1694` appear only in P8
  packet/freeze/module/tests-constant-assertions (fully fresh). SCREEN
  `2026091680..1682` coincide numerically with P7 test-local seeds — adjudicated
  in §4, not a consumption.

## 4. SEED-COINCIDENCE ADJUDICATION — PASS (ratified, not a blocker)

Operator-flagged question: frozen P8 SCREEN `2026091680..1682` coincide
numerically with P7 focused-test local seeds. Are the P8 SCREEN streams
scientifically fresh?

Independent verification (all from P7 evidence, NPZ never opened):

- P7 consumed streams were TRAIN `2026091650,1651,1652` ×256 and DEV
  `2026091660..1664` ×128. Evidence: `P7 AUTHORIZATION_PROMPT.md:1`,
  `P7_FREEZE.md:98-99,192` (frozen command), `target_construction.py:111-114`
  (`FROZEN_TRAIN_SEEDS`, `FROZEN_DEV_SEEDS`), `target_construction_gate/
  frozen_plan.json:30-34,147-149`, `aggregate_summary.json` keys
  `train_2026091650..52` / `2026091660..64`.
- P7 test-local `2026091680..1686` are injected-synthetic RNG seeds for tiny
  tables, never official streams. Evidence: `test_nbpolar_target_construction.py:1-11`
  header ("Injected tiny/synthetic tables … never the frozen TRAIN/DEV streams"),
  `42-50` (`TEST_SEED_A=2026091680 … TEST_SEED_G=2026091686`; "frozen gate streams
  are only read from the module constants and are never used as inputs"),
  `81-97 injected_counts` (synthetic 1024×1024 sparse matrix via
  `default_rng(seed)`), `293,526,597,662-738` (injected `counts=` runs,
  loader patched with raising stub, `input_mode=="injected_counts"`,
  `open_count==0`), `P7 PRE_EXECUTE_REVIEW.md:91` ("focused tests … use injected
  counts … frozen streams are never used as inputs (test seeds 2026091680..86)"),
  `P7 PRE_RESULT_REVIEW.md:279` ("2026091680..86, disjoint from the frozen streams").
- Therefore test-local use is not consumption: no NPZ content open, no TRAIN/DEV
  sampling, no scientific stream consumed. P8 SCREEN `1680..1682` have never been
  consumed as official gate streams (P7 gate consumed only `1650..52/1660..64`).

**Ruling: FRESH — RATIFIED.** Precise rule: a seed integer is *consumed* only when
it drives sampling from the accepted V25 TRAIN model inside an authorized gate
attempt (NPZ content open + `default_rng(stream_seed)` → `sample_target_block`
→ SC/tag). Use of the same integer as a local RNG seed for synthetic/injected
tiny tables with `counts=` seam, `input_mode=="injected_counts"`, loader raising
stub, and `open_count==0` is *not* consumption and does not taint the integer for
future frozen gate use. P8 SCREEN streams satisfy the fresh side; CONFIRM streams
are additionally repo-fresh. No repair needed; proceed with the frozen streams
unchanged (no seed change permitted).

Single decision that would have been needed on genuine consumption (not triggered):
freeze new disjoint SCREEN streams + update packet/freeze/module/tests/OpenSpec
and re-review — not required.

## 5. Selection/threshold logic — PASS

- Lexicographic min `(K1+K2,K1,K2)` over eligible only, no runtime/DEV tiebreak:
  `target_rate.py:547-558 select_point` (`min(eligible, key=(k1+k2,k1,k2))`);
  grid ties e.g. `(10,94)` over `(24,80)` at sum 104 verified in tests
  (`test_nbpolar_target_rate.py:219-236`).
- Wilson LB `z=1.6448536269514722 >=0.95`: `target_rate.py:164 WILSON_MIN`,
  `520-544 screen_eligibility` (gates on `wilson_lb>=0.95`, records
  `count_rule_188_of_192` + `wilson_count_agree`); CONFIRM gates `1689-1702`
  (`>=618/640` + `wilson>=0.95`).
- Independently recomputed (pinned interpreter) — exact:

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c "import math; ..."
# 187/192 -> 0.9474773285638652 (<0.95, ineligible)
# 188/192 -> 0.9544033287216636 (>=0.95, eligible)
# 617/640 -> 0.9498753087068414 (<0.95)
# 618/640 -> 0.9516826902311426 (>=0.95)
# full 0..192: eligible ⟺ exact>=188 TRUE; full 0..640: LB>=0.95 ⟺ exact>=618 TRUE
# WILSON_Z == 1.6448536269514722 exact
```

  Matches `P8_FREEZE.md:117-118,131-132` and `P8_IMPLEMENTATION_NOTES.md:58-62`.
- No-eligible path returns `TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT` without CONFIRM:
  `target_rate.py:1543 selection=None if resource_stop… else select_point(…)`,
  `1550 if selection is not None:` (CONFIRM skipped), `1718-1719` label,
  `1888-1918 selection_file confirm={"executed":False}`; test
  `test_p8_screen_no_eligible_point_path` (`381-416`) asserts
  `selection is None`, `confirm_results==[]`, label, 35 configs all ineligible.

## 6. Code review — PASS

File: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py`
(2429 lines). Accepted modules untouched (see §9).

- Refusal ordering (absent-root/orders-identity before NPZ open; preconditions
  after open but before ANY SC; zero SC/genie on failure): `1228-1310`
  (`1256 exists→FileExistsError` first; `1258-1279` frozen scalar/grid/seed-list
  validation; `1288-1310` orders identity via `load_construction_orders`/
  `validate_orders_doc` raising `OrdersIdentityError`); `1313-1323` NPZ stat check;
  `1323` single `load_v25_channel_counts` (consumption point); `1381-1392`
  `target_preconditions` raising `TargetPopulationContractError` before
  `1396 make_gf32`, `1397 start`, `1419-1450` SCREEN SC. Probe (this review,
  injected counts, failing entropies): raised
  `TargetPopulationContractError(BLOCKED(target_population_contract))` with
  **0 SC calls**; smoke `input_mode=="injected_counts" open_count==0`. Confirmed
  by tests `test_p8_orders_identity_refusals_before_any_npz_access` (loader
  raising stub) and `test_p8_cli_frozen_flags_and_refusals` (existing-root/grid/
  overlap refusals before open). Reading of `P8_FREEZE.md:79-91 §3.1` confirmed:
  preconditions necessarily follow the content open (functionals of the counts);
  "before open" covers absent-root + orders-identity; packet proper requires
  preconditions only before SC — consistent.
- Shared-block sampling (identical block object across all 35): `561-608
  SharedBlock` + `576-608 sample_shared_blocks` (one `default_rng(stream_seed)`
  per stream, `sample_target_block` once per block); `1420-1450` samples
  `screen_blocks_all` once then `for k1,k2 in grid: for block in
  screen_blocks_all: run_rate_arm(block=block)` — identical object. Spy test
  (`304-339`) asserts `id()` identity per position across 35 configs.
- Per-stream pooled SCREEN + disjoint CONFIRM, no SCREEN material into CONFIRM:
  `1421-1423` SCREEN per-stream RNG; `1562-1564` CONFIRM freshly sampled from
  `confirm_seed_list`; `1217-1225 _check_seed_lists` refuses overlap (tested
  `239-273`); `611-634` phase/arm/block domain separation + `1448/1579`
  disjoint masters; `run_confirm_pair 898-952` takes only CONFIRM `block`.
  Tests assert `screen_streams=={TEST_SEED_F}`, `confirm=={TEST_SEED_G}`,
  disjoint (`367-373`), and `default_rng(frozen)` never appears in tests
  (`864-880`).
- Selected-only CONFIRM at same K1/K2, report-only BEC: `1550-1595` (only
  `selected_k1/k2`), `1551-1558` BEC orders from accepted P7 surrogates,
  `run_confirm_pair` empirical+BEC; BEC exact/cells report-only (`1661-1664`,
  `1902-1914`), empirical need not beat BEC. Test `344-366` asserts only
  `(8,80)` confirmed, both arms, same K, correct order objects.
- Truth boundary (truth only sampling/disclosed/tag/scoring): `765-773`
  internal truth copies; `778-809` operational path uses `bob_arr`/candidate/
  disclosures only (`build_p1_metrics(bob)`, `gather_p2_metrics(bob,high_hat)`);
  truth copies used only for `u1/u2_disclosed`, tag construction `819-821`,
  scoring `818 label_match`; `836-851` per-arm sentinel over protected
  metrics/decisions; `852/874 truth_leak_violation`. Test `419-466` asserts
  caller arrays unmutated and broken sentinel → `BLOCKED(truth_leak_zero)`.
- Buckets mutually exclusive, undetected never merged: `221-227
  OUTCOME_PRECEDENCE`, `829-834 classify_outcome`, `988-1049
  _arm_record_consistent` (exact requires tag+match; undetected requires
  tag+¬match; verify_failed requires ¬tag; decode_failed requires SC fail;
  resource_abort isolated), `2104-2169` decision-path zero gates; tests
  `477-539` assert taxonomy incl. bad-undetected rejected.
- Accounting `5*(K1+K2)+64` + `2623`/tag + independent recount:
  `867-872` (L1 `5*K1` even on L1 fail, L2 `5*K2` only when invoked, tag `64`
  only when invoked), `174 PUBLIC_CONTROL_BITS_PER_TAG=seed_bits_for(256)=2623`,
  `1082-1136 block_events` (L1/L2/tag events), `1139-1199 recount_events`
  (phase/arm read literally from event id), `1181-1199 _transcript_mismatches`,
  `1621-1622/2183-2248` zero-mismatch gate. Tests `542-611` assert
  partial (`5*K1`, `5*(K1+K2)`) / full (`5*(K1+K2)+64`) + recount + tamper.
- Consumption at first open with reopen guard: `1327-1348` accounting
  (`v25_npz: reads 1/1, attempts 1/1, open_count 1, stat checked`;
  `injected: 0/0`); single call `1323`, no loop/retry; `1617-1619`
  orders-digest after==before; `2201-2225` `attempt_read_accounting_exact`.
- Five-file scalar-only schema: `246-252 OUTPUT_FILES`, `2035-2058` writes
  exactly five files; `_arm_record 955-981` persists scalars only (no
  bob/U/decoded/disclosed vectors, metric arrays, labels, tags, raw seeds);
  `report.md` via `_render_report 2258-2359` covers 35 rows/selection/CONFIRM/
  leakage/planning-`f`/wall/RSS.
- Labels exact: `1716-1724` (`BLOCKED` / `TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT` /
  `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE` iff integrity+scientific+`shape_is_frozen` /
  else `NOT_CONFIRMED`), `1724 blocked_detail=BLOCKED(<earliest>)`,
  `1707-1715 shape_is_frozen` (frozen seeds/blocks/grids + `orders_mode=="p7_file"`).

## 7. Tests — PASS

Commands (pinned interpreter, fresh basetemps):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_target_rate.py -q -p no:cacheprovider --basetemp=/tmp/p8_preexec_focused
# 12 passed, 1 warning in 14.67s
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider --basetemp=/tmp/p8_preexec_full2
# 240 passed, 1 warning in 125.52s
```

Expectation met: 12 focused + 240 full (228 predecessor + 12 new).
Coverage vs packet P8-04 list: grid completeness/shared-block identity
(`test_p8_grid_complete_35_configs`, `test_p8_shared_block_identity…`);
Wilson 187/192 false + 188/192 true + full-range equivalence both shapes
(`test_p8_wilson_screen_boundary_and_equivalence`); selection ties/empty
(`test_p8_selection_deterministic_ties_and_empty`); isolation/disjointness
(`test_p8_stream_isolation_and_disjointness`); selected-only + pairing
(same test as shared-block); no-eligible path (`test_p8_screen_no_eligible_point_path`);
truth isolation (`test_p8_truth_isolation`); buckets (`test_p8_buckets_mutually_exclusive`);
partial/full accounting + recount + tamper (`test_p8_accounting_partial_full_and_recount`);
orders refusals (`test_p8_orders_identity_refusals_before_any_npz_access`);
CLI/refusals/frozen constants + no-forbidden-marker/empty-cwd-import
(`test_p8_cli_frozen_flags_and_refusals`,
`test_p8_no_forbidden_markers_or_production_invocation`). Tests never open the
NPZ (loader raising stubs + `counts=` seam; `channel_counts.npz` absent from test
source; `rate_screen_confirm` absent; `default_rng(frozen)` absent), never use
frozen streams for real sampling (fresh `>=2026091700`; frozen integers appear
only in constant assertions / parser-value checks / pre-open refusal probes that
return 2 without sampling), never invoke production paths (temp roots only,
`input_mode=="injected_counts"`, empty-cwd import creates no files).

## 8. Bounded smoke — PASS

Command: injected tiny 1024×1024 counts + injected 4-permutation orders + temp
root, constant tag, `screen 1×1 / confirm 1×1` (this review, not the gate).

Raw evidence: exactly five files
`['frozen_plan.json','report.md','screen_records.json',
'selection_and_confirmation_records.json','transcript_accounting.json']`;
gates all `True` on the tiny shape; label
`TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT` (tiny-shape negative path);
`wall 2.237s`, `RSS 219660288 B`; margin vs budgets `3600s / 2GiB`:
`~3597.8s` and `~1927823360 B` headroom on a 2-block smoke. Frozen gate is
~16k SC calls (SCREEN `35×192×2=13440` L1+L2 + CONFIRM `640×2×2=2560` worst
case at N=256 GF32) — smoke wall/RSS are orders of magnitude inside the
envelope, consistent with `P8_FREEZE.md:153-156` and notes `§6.6` (2 GiB/3600s
for ≈16k SC calls). No artifact read consumed (`open_count 0`).

## 9. Scope/premises — PASS with note

Commands:

```bash
git status --porcelain
git rev-parse HEAD
git diff --name-only -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py .../prior.py .../construction.py .../protocol.py .../two_layer.py .../target_construction.py .../v35_algorithm_development.py
git status --porcelain -- results/ comparison_bench/outputs_comparison/
```

Evidence:

- P8 Wave-A set present: `?? target_rate.py`, `?? test_nbpolar_target_rate.py`,
  `?? specs/nbpolar-phase4-p8/`, `M tasks.md` (P8 section only, 297 insertions),
  `?? .workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/`
  (TASK_PACKET/STATUS/P8_FREEZE/P8_IMPLEMENTATION_NOTES/AUTHORIZATION_PROMPT/PROMPT).
- No accepted-module edits: `git diff --name-only` over `sc.py/prior.py/
  construction.py/protocol.py/two_layer.py/target_construction.py/
  v35_algorithm_development.py` is empty. Loader
  `formal_ir/v35_algorithm_development.py:349` (`load_v25_channel_counts`) reused
  unchanged.
- No old-root/evidence writes: `git status` over `results/` and
  `comparison_bench/outputs_comparison/` is empty; no sibling-checkout writes.
- HEAD unchanged: `ab173f2a5e17336383a897b941080b731ba3dd9e` (matches
  `P8_IMPLEMENTATION_NOTES.md:22`); no commit made by this review.
- Root absent; reads/attempts still `0/0` (`STATUS.yaml` re-read after checks).
- Note (non-blocking): the worktree is dirty beyond the Wave-A set (other
  phases P3-P6/X-probes, `AGENTS.md`, `CURRENT_TASK.md`, etc. — see full
  `git status --porcelain`). Per `AGENTS.md §10.1(11)` dirty worktrees are
  reviewed by scope: unrelated changes are preserved, not attributed to P8.
  P8 scope itself is clean; this note does not block execution. The gate runner
  must still refuse if the frozen root appears and must not touch unrelated paths.

## Frozen record (complete)

- Orders/support/streams: P7 `construction_orders.json` sha
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`;
  NPZ `…/run_04/channel_counts.npz` `25166822 B`; source `1M`; floor `1e-15`;
  N=256 GF32 (poly 37, alpha 2, natural); P1/P2 via accepted `derive_p1/derive_p2`
  under `A=32*U1+U2`; entropies `H1 0.02428054681872374 / H2 0.7767572780789994 /
  total 0.8010378248977232` tol `1e-12`, floor-change `<=1e-9`.
- Grids/streams: SCREEN `2026091680,1681,1682` ×64 =192; `K1 [8,10,12,16,24,32,45]`
  × `K2 [80,94,110,125,140]` =35; CONFIRM `2026091690..1694` ×128 =640 disjoint;
  Toeplitz master `stream+10000`, domain `nbpolar-p8-target-rate-seed:master:phase:arm:block:counter`,
  `2623` public bits/tag, `64`-bit tag; disclosure `5*(K1+K2)+64`.
- Command: the 12-flag `timeout 3600 …target_rate --counts … --source 1M --orders …
  --n 256 --floor 1e-15 --screen-seeds 2026091680 2026091681 2026091682 --screen-blocks 64
  --k1-grid 8 10 12 16 24 32 45 --k2-grid 80 94 110 125 140 --confirm-seeds 2026091690
  2026091691 2026091692 2026091693 2026091694 --confirm-blocks 128 --out-dir …/rate_screen_confirm`
  (byte-identical packet/freeze/module); budgets `ulimit -v 2097152`, `2 GiB`, `3600s`;
  one read + one attempt consumed at first NPZ open; no rerun/tuning.
- Schema/gates/labels: five files `frozen_plan.json / screen_records.json /
  selection_and_confirmation_records.json / transcript_accounting.json / report.md`
  (scalar-only); integrity order `orders_identity_and_permutations,
  target_population_contract, coverage_complete_and_disjoint, pairing_and_buckets,
  truth_leak_zero, undetected_zero, nonfinite_zero, resource_abort_zero,
  disclosure_and_recount_exact, attempt_read_accounting_exact, resource_limits_met`;
  scientific `confirm_empirical_exact_at_least_618_of_640,
  confirm_empirical_wilson_lower_bound_at_least_0p95`; labels
  `TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT` / `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE` /
  `TARGET_EMPIRICAL_RATE_POINT_NOT_CONFIRMED` / `BLOCKED(<earliest gate>)`;
  scope V25-1M-TRAIN N=256 static development only.

## Findings

No blocking issues. Non-blocking notes:

- Worktree dirt beyond Wave-A (§9 note) — preserve unrelated changes; P8 scope clean.
- `target_rate.py:32` docstring says "V49 1M TRAIN literals" where the packet/freeze
  say V25/ratified P7 population semantics — provenance comment wording only;
  numeric literals match (`155-157`); not a behavior difference.
- P8 tests legitimately spell frozen integers in constant/parser/refusal probes
  (`test_nbpolar_target_rate.py:240-246,734-771,819-856`); sampling uses only
  `>=2026091700` with `counts=` seam and raising loader stubs — not consumption.

## Closure statements

- The V25 NPZ content was **not opened** by this review (stat size `25166822` only).
- Artifact reads / scientific attempts are still **0/1 used** (`STATUS.yaml`
  `artifact_reads_used: 0`, `attempts_used: 0`; `result: null`).
- The frozen output root `rate_screen_confirm/` is still **absent**.
- The gate command was **never executed** by this review; no Model-F/raw/held-out/
  real/EVAL data was touched; no old-root writes; no commit/push; HEAD still
  `ab173f2a5e17336383a897b941080b731ba3dd9e`.
- This review wrote **only** this `PRE_EXECUTE_REVIEW.md` file.
