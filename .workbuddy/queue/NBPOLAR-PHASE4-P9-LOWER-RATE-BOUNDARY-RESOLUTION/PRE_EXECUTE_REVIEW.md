# Independent Pre-EXECUTE review — NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION

**Reviewer:** independent reviewer-go (did not write the code; read-only review, no gate execution).
**Date (UTC):** 2026-09-14. **Scope:** Tier-Y packet `NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION`, Wave-A only.
**Verdict: PASS** — the single frozen attempt may proceed with the frozen command exactly as written. No blocking issue found.

> Write discipline for this review: the reviewer created ONLY this file. The V25 `channel_counts.npz` content was NEVER opened (metadata `stat` only). The real gate command was NEVER run. No Model-F / raw / held-out / real / EVAL data was touched. No old-root write, no commit, no push.

## Output-format verdict block

```
Verdict: pass
Blocking Issues:
- (none)
Non-Blocking Suggestions:
- Ratify the parser/main gate-id split (§3.1 of implementation notes) at execution level (see check 6).
- Note the dirty-worktree scope adjudication (see check 9): extra dirt is out-of-scope and untouched.
- Batch the stale P8-era test-header comment (>=2026091700) into the next milestone docs pass (see check 7).
Checklist:
- [x] Matches OpenSpec spec
- [x] Tests pass
- [x] No scope creep
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? — No. No new failure mode was observed; no doc update required by this gate.
```

## 1. STATUS exactness — PASS

Exact command + raw evidence:

```bash
cat .workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/STATUS.yaml
```

Raw (22 lines, verbatim):

```yaml
task_id: NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION
state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE
predecessor: TARGET_EMPIRICAL_RATE_POINT_ACCEPTED
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

Check: exactly five authorized flags `true` (documentation, implementation, artifact_read, decoder_execution, development_gate); all others (`real_data`, `eval`, `adaptive`, `scalable_decoder`, `scl`, `scientific_promotion`) `false`; reads 0/1, attempts 0/1; `result: null`; both independent reviews `pending`; `state`/`next_gate` as declared. **PASS.**

## 2. OpenSpec P9 delta consistency — PASS; all P9 boxes unchecked; docs authorize nothing

Commands:

```bash
grep -n "P9-" openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md | head -20
grep -n "\[ \]\|\[x\]" openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md | tail -15
grep -n "authorizes no" openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p9/spec.md
```

Raw evidence:

- `tasks.md` P9 section (lines 354–408) contains 9 items `P9-1..P9-9`, every one `- [ ]` (unchecked). Prior P8 items remain `- [x]`; the implementing session checked no box. Verified: `grep` shows `- [ ] P9-1` through `- [ ] P9-9`, zero `- [x] P9-*`.
- `specs/nbpolar-phase4-p9/spec.md:15`: "This document authorizes no production behavior." `tasks.md` P9 preamble: "Status/acceptance of every item below is owned by the main thread; the implementing session reports evidence only and never checks its own boxes."
- Delta consistency vs `TASK_PACKET.md`: mission (resolve P8 left-censored search, final N=256 static localization before adaptive-vs-N-scaling choice) matches spec §1 + freeze §1; 8×7 grid with `(0,0)` + `(8,80)` anchor matches spec "frozen shared-block SCREEN" requirement; lexicographic `(K1+K2,K1,K2)` selection with no runtime/DEV tiebreak matches; integrity/scientific gates + three P9 labels + `BLOCKED(<gate>)` match; delta-only scope ("selects only P9 protocol/prefix/labels/grid/root; P8 byte-for-byte") matches; no-interpolation rule ("a selected grid boundary is not by itself a search-truncation ambiguity because both axes include zero") matches packet P9-03. **PASS.**

## 3. Delta-only proof — PASS (with dirty-worktree scoping note; see §9)

Because `target_rate.py` / `test_nbpolar_target_rate.py` / P9 spec are UNTRACKED in this worktree (HEAD `ab173f2` predates the NB-Polar Wave work), `git diff` on the module is vacuous. The equivalent proof was done by content inspection + P8-preservation tests:

Commands:

```bash
git diff --name-only  # tracked set; target_rate.py NOT in it (untracked, delta file)
git status --porcelain comparison_bench/src/comparison_bench/formal_ir/nbpolar/ comparison_bench/tests/
grep -c "open(" comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py  # 0
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c "from comparison_bench.formal_ir.nbpolar import target_rate as tr; print(tr.FROZEN_K1_GRID, tr.FROZEN_K2_GRID, tr.FROZEN_NCONFIGS, tr.FROZEN_SCREEN_SEEDS, tr.FROZEN_CONFIRM_SEEDS)"
```

Raw evidence:

- Tracked `git diff --name-only` lists 16 files (P3 STATUS/AGENTS/CURRENT_TASK/`__init__`/empirical_* /docs/tasks.md etc.); `target_rate.py` is `??` untracked, so no tracked P8-behavior file was overwritten by Wave-A.
- P8 constants in the module are intact byte-for-value: `FROZEN_K1_GRID=(8,10,12,16,24,32,45)`, `FROZEN_K2_GRID=(80,94,110,125,140)`, `FROZEN_NCONFIGS=35`, `FROZEN_SCREEN_SEEDS=(2026091680,1681,1682)`, `FROZEN_CONFIRM_SEEDS=(2026091690..1694)`, `PROTOCOL_NAME="nbpolar-p8-target-rate-screen-confirm"`, `SEED_PREFIX="nbpolar-p8-target-rate-seed"`, `FROZEN_COMMAND` (P8, no `--gate-id`), `EXPECTED_NPZ_BYTES=25166822`, `EXPECTED_ORDERS_SHA=8ec...104`, entropy literals, `SCREEN_EXACT_MIN=188`/`CONFIRM_EXACT_MIN=618`/`WILSON_MIN=0.95`, budgets — all present and unchanged.
- P9 additions are isolated: lines 129–181 (P8/P9 gate-id constants, P9 protocol/mode/seed/frame prefixes, P9 grids/seeds/root/labels, `P9_PRIOR_OFFICIAL_STREAMS`); helpers `_normalize_gate_id` (354), `_gate_protocol/mode/seed_prefix/frame_prefix/labels/grids/frozen_seeds/frozen_command` (370–415); `gate_id` threading through `arm_seed_bits` (775), `run_rate_arm` (902), `run_confirm_pair` (1070), `block_events` (1260), `_check_seed_lists` (1405, P9-only prior-overlap refusal), `run_target_rate` (1426, `gate_id=P8_GATE_ID` default), `_integrity_gates` (2286, `exp_nconfigs` 56 vs 35), `_render_report` (2475), `build_parser`/`main` (2586/2622). No SC/prior/construction/tag/outcome/support/truth/accounting logic changed: imports reuse `load_v25_channel_counts`, `target_construction` helpers, `analytic_order`, `derive_p1/derive_p2`, `sc_decode`, `polar_transform`, `make_gf32`, `labels_to_bits/seed_bits_for/OUTCOMES/DISCLOSED_BITS_PER_COORDINATE/LABEL_SCALE/TAG_BITS`, `wilson_lower_bound/WILSON_Z`, `toeplitz_tag/canonical_event`.
- P9 tag-domain prefix and protocol name DIFFER from P8 (refusal-tested): `nbpolar-p9-lower-rate-boundary-seed` ≠ `nbpolar-p8-target-rate-seed`; `nbpolar-p9-lower-rate-boundary-screen-confirm` ≠ `nbpolar-p8-target-rate-screen-confirm`; frame `nbpolar-p9-lower-rate-boundary` ≠ `nbpolar-p8-target-rate`; labels triple all differ; grid-mismatch refused in BOTH directions (probed: P9 rejects P8 grids, P8 rejects P9 grids). Silent P8-identifier reuse is impossible.
- P7/P8 evidence roots untouched: P8 `rate_screen_confirm/` still exactly 5 files (frozen_plan/report/screen/selection/transcript, mtime 2026-09-14 12:59); P7 `construction_orders.json` mtime 2026-09-14 03:33, sha still matches (see §4). **Delta-only verdict: PASS.**

## 4. Frozen identity — PASS (NPZ stat only; never opened)

Commands (NO content open anywhere in this review):

```bash
stat /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c "import json,hashlib; doc=json.load(open('.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/construction_orders.json')); print(doc['orders_sha256']); print(hashlib.sha256(json.dumps(doc['layers'],sort_keys=True,separators=(',',':')).encode()).hexdigest())"
rg -n "def load_v25_channel_counts" comparison_bench/src/comparison_bench/formal_ir/v35_algorithm_development.py
ls .workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/  # must fail
```

Raw evidence:

- NPZ `stat`: `Size: 25166822`, regular file, Modify 2026-08-19. `st_size == 25166822` matches `EXPECTED_NPZ_BYTES` and the packet/freeze/module. Content NOT opened by this reviewer (no `load_v25_channel_counts`, no `np.load`, no `unzip -l` content read).
- Source `1M`; floor `1e-15` (`FROZEN_FLOOR`, `_check_floor`, CLI `--floor 1e-15`); N=256 (`FROZEN_N`, `_check_power_of_two` + `n != 256` refusal).
- P7 orders identity recomputed from JSON only: recorded `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`; recomputed canonical `sha256(layers)` identical; `match True`; both pooled orders length-256 valid permutations (also enforced by `validate_orders_doc` + `is_valid_permutation` before any NPZ access).
- Accepted loader `comparison_bench/src/comparison_bench/formal_ir/v35_algorithm_development.py:349`: `def load_v25_channel_counts(...)` confirmed at line 349.
- Grids: `P9_FROZEN_K1_GRID=(0,2,4,6,8,12,24,45)` (8) × `P9_FROZEN_K2_GRID=(0,20,40,50,60,70,80)` (7) = 56 via `screen_grid` K1-major; includes `(0,0)` (global zero-disclosure corner) and `(8,80)` (accepted P8 anchor, per P8 `MAIN_THREAD_ACCEPTANCE.md`: 35/35 eligible, selected K1=8/K2=80, CONFIRM 638/640, LB 0.9906013676984646, left-censored).
- SCREEN seeds `2026091710,1711,1712` ×64 = 192; CONFIRM `2026091720..1724` ×128 = 640; Toeplitz master `stream+10000` (`PUBLIC_TAG_MASTER_OFFSET`), P9-domain-separated (`arm_seed_bits(..., gate_id)` → `P9_SEED_PREFIX`).
- Frozen 13-field command byte-identical across packet/freeze/module: `pkt == frz` → `True` for the `timeout 3600 ...` line; module `P9_FROZEN_COMMAND` carries the same 13 flags (`--gate-id` first, then `--counts --source --orders --n --floor --screen-seeds --screen-blocks --k1-grid --k2-grid --confirm-seeds --confirm-blocks --out-dir`) with verbatim P9 values; `--gate-id p9-lower-rate-boundary` count == 1; out-root `.../lower_rate_screen_confirm`.
- Output root ABSENT: `ls .../lower_rate_screen_confirm/` → `No such file or directory`.
- Seed freshness + disjointness: `grep -rn 2026091710 P7-dir` → exit 1 (no hit); same for P8-dir → exit 1; among repo-tracked files P9 streams appear ONLY in `target_rate.py` + `test_nbpolar_target_rate.py` + P9 spec (+ P9 queue docs, expected); numeric disjointness from ALL prior official streams (`1650..52`, `1660..64`, `1680..82`, `1690..94`) holds and is enforced at runtime by `_check_seed_lists(..., gate_id=P9)` → `P9 streams overlap prior official streams` refusal (probed). **PASS.**

## 5. Selection / thresholds — PASS (boundary values recomputed independently)

Commands:

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c "
import math; z=1.6448536269514722
def lb(k,n):
 p=k/n; d=1+z*z/n; c=p+z*z/(2*n); m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (c-m)/d
print(lb(187,192), lb(188,192), lb(617,640), lb(618,640))"
```

Raw evidence (this review, `z=1.6448536269514722`):

- `187/192 → 0.9474773285638652 < 0.95`; `188/192 → 0.9544033287216636 ≥ 0.95`; full `0..192` sweep: `eligible == (exact ≥ 188)` with zero mismatches (module `screen_eligibility` + focused test full-range re-verification agree).
- `617/640 → 0.9498753087068414 < 0.95`; `618/640 → 0.9516826902311426 ≥ 0.95`; Wilson LB monotonic in k, so `LB ≥ 0.95 ⟺ exact ≥ 618` at the frozen 640 shape (focused test re-verifies `0..640`).
- Selection: `select_point` (`target_rate.py:711`) = `min(eligible, key=(K1+K2,K1,K2))`; no runtime/DEV/CONFIRM outcome enters; `None` iff no eligible. CONFIRM gates: `planned==640 and exact ≥ 618` AND `planned==640 and wilson ≥ 0.95` (`target_rate.py:1900-1910`); no-eligible → `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` with `confirm_results==[]`, `confirm=={"executed": False}`, NO confirm (code guard line 1756 + test `test_p9_screen_no_eligible_point_path`).
- No-interpolation: grids exact-match refused (`tuple(k1_list) != exp → ValueError`, probed both directions); both axes include zero so a boundary selection is a valid grid point, not a truncation ambiguity. **PASS.**

## 6. Code review — PASS (refusal ordering confirmed with the §3.1 reading)

Probed + inspected (`target_rate.py` line refs):

- Refusal ordering (freeze §3.1 reading CONFIRMED): (1) missing `--gate-id` → `main` return 2 before any artifact access (2624; probed `main(missing-gate) == 2`); (2) existing `--out-dir` → `FileExistsError` before anything else (1461; probed `main(existing-dir) == 2`, `never.exists() is False`); (3) frozen scalar/grid/seed validation incl. P9 prior-stream disjointness (1463–1484, `_check_seed_lists` 1405); (4) P7 orders identity/permutation/surrogate refusal (1492–1515, `OrdersIdentityError`, consumes nothing); (5) NPZ stat check (1518–1527); (6) single content open `load_v25_channel_counts` (1528, read 1/1 + attempt 1/1, `open_count 1`, no reopen path); (7) preconditions `target_preconditions` (1586–1597) AFTER open but BEFORE any SC (1624+), failure → `TargetPopulationContractError("BLOCKED(target_population_contract)...")` with no root. Zero-SC failure path PROBED: injected bad entropies → raised `TargetPopulationContractError`, `sc_calls == 0`, `root exists False`. The packet-brief phrase "before the first NPZ content open" covers gate/out-dir/grid/seed/orders/stat; preconditions necessarily follow the open (functionals of the counts) — this is the only coherent reading and the code implements it.
- Shared-block sampling across all 56: `sample_shared_blocks` (740, one `default_rng(stream_seed)` per stream, no global RNG) builds `screen_blocks_all` once (1624–1629); every grid point reuses the identical block object (loop 1633+); test spies all 56×52 calls share object identity per `(seed,index)`.
- Zero-K correctness: `l1_order[:0]`/`l2_order[:0]` empty slices flow through unchanged SC path; L2 still invoked (every L1 candidate must invoke L2, enforced by `_arm_record_consistent` 1194); tag still invoked; `(0,0)` = 64-bit tag-only (`5*(0+0)+64 = 64`); `K1=0`/`K2=0` disclose 0 for that layer (`block_events` 1285/1302). Probed + tested at n=8: `(0,0)→64`, `(0,4)→84`, `(3,0)→79` with event-level bit checks.
- Disjoint CONFIRM, no SCREEN material: fresh `sample_shared_blocks` per confirm seed (1768), `_check_seed_lists` distinct+disjoint + P9-prior refusal; `run_confirm_pair` takes only the selected K + confirm block; no screen block/outcome/tag seed crosses (masters are `seed+10000` per phase).
- Selected-only same-K CONFIRM + report-only BEC: loop runs ONLY `selection` (1756), empirical + BEC at identical `(selected_k1,selected_k2)` (1757–1788); BEC `report-only` (no empirical-vs-BEC gate; `paired_exact_gap`/cells persisted only).
- Truth boundary: per-arm truth copies (939–945), `PRIOR_ONLY`/`CANDIDATE_CONDITIONED` provenance, `_truth_isolation_sentinel` (831) mutating truth copies, `truth_leak_zero` gate (2452); tests mutate block truth and force sentinel-False → `BLOCKED`.
- Buckets exclusivity, undetected never exact: `OUTCOMES` taxonomy, `classify_outcome` precedence (`resource_abort > decode_failed > verify_failed > exact > undetected`), `_arm_record_consistent` structural proof (exact ⟺ tag_pass+label_match; undetected ⟺ tag_pass+¬label_match, never merged), `pairing_and_buckets` + decision-path zero gates (`undetected_zero`/`nonfinite_zero` over eligible SCREEN + CONFIRM only; rejected SCREEN report-only).
- Accounting `5*(K1+K2)+64` + `2623`/tag + recount: `key_dependent_bits = 5*K1 + (5*K2 if l2_invoked) + (64 if tag_invoked)` (1039), `public = seed_bits_for(n)=2623 if tag_invoked` (1044/237), partial-call semantics preserved incl. zero-K (L1-fail → `5*K1` only); `block_events`/`recount_events` literal phase/arm recount with `mismatch_count == 0` required (`disclosure_and_recount_exact` 2457). Probed: `(0,0)→64`, `(8,80)→504`, `(45,80)→689`; `seed_bits_for(256)==2623`.
- Consumption at first NPZ open with reopen guard: single `load_v25_channel_counts` call site (1528); accounting `open_count 1`, reads 1/1, attempts 1/1; injected mode `open_count 0`; no second open, no retry-after-open flags.
- Five-file scalar-only schema: `OUTPUT_FILES` (309) exactly `frozen_plan.json / screen_records.json / selection_and_confirmation_records.json / transcript_accounting.json / report.md`; `_arm_record` (1131) scalar-only (no bob/high/low/labels/metrics/tags/seeds persisted); `mkdir(parents=True)` only after all gates computed (2247), writes exactly 5 files.
- P9 labels exact: `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` / `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` / `TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED` (`_gate_labels`, plan 2046, summary outcome 1924–1932); `BLOCKED(<earliest gate>)` via `INTEGRITY_GATE_ORDER` frozen order.
- Gate-id closed-choice (missing/invalid refused; P8 preserved): parser `choices=[p8,p9]` (invalid → `SystemExit`, tested); `main` missing → return 2 before artifact access (tested, loader never runs); `_normalize_gate_id(None)→P8` ONLY for the injected Python seam (12 P8 tests call without gate id); `_normalize_gate_id("bogus")→ValueError` (probed); P8 path preserves P8 protocol/prefix/labels/grid/seeds/command. The parser-optional / main-required split is DELIBERATE (implementation notes §3.1) and execution-level REQUIRED — ratified here as acceptable because every production invocation goes through `main` and the frozen command always carries `--gate-id p9-lower-rate-boundary` first. **PASS (ratify the split; non-blocking).**

## 7. Tests — PASS (24 focused + 252 full, pinned interpreter, fresh basetemps)

Commands (pinned interpreter, `no:cacheprovider`, fresh `/tmp` basetemps):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_target_rate.py -q -p no:cacheprovider --basetemp=/tmp/p9_preexec_focus
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_\*.py -q -p no:cacheprovider --basetemp=/tmp/p9_preexec_full
```

Raw evidence (this review, reruns):

- Focused: `24 passed, 1 warning in 18.05s` (12 P8 preserved + 12 P9 new; warning is the benign `Unknown config option: cache_dir` only).
- Full NB-Polar: `252 passed, 1 warning in 124.41s` (240 predecessor + 12 new; same benign warning only).
- P9 coverage vs packet P9-06 list: 56-point grid + `(0,0)`/`(8,80)` (`test_p9_grid_complete_56_configs`); zero-K (`test_p9_zero_k_behavior`); P8 anchor inclusion (same test); shared-block identity across all 56 (`test_p9_shared_block_identity_selected_only_and_pairing`, 56×52 identity + selected-only `(0,0)` + same-K pairing + 5-file assert); eligibility boundary full-range (`test_p9_wilson_screen_boundary_and_equivalence`, 0..192 + 0..640 literal-Wilson); deterministic selection ties/empty (`test_p9_selection_deterministic_ties_and_empty`); no-eligible path with NO confirm (`test_p9_screen_no_eligible_point_path`); disjoint confirmation + prior-stream disjointness (`test_p9_stream_isolation_and_prior_disjointness`); same-K control + pairing (shared-block test); buckets/truth isolation (`test_p9_truth_isolation_and_buckets`); accounting/recount with zero-K (`test_p9_accounting_partial_full_and_recount_with_zero_k`); P9 domain separation (`test_p9_domain_separation_protocol_prefix_labels` + grid-mismatch both directions); absent root + gate-id closed-choice + P8 preservation (`test_p9_cli_gate_id_closed_choice_and_refusals`, loader-forbidden, `never.exists()`); no-production-input (`test_p9_no_forbidden_markers_or_production_invocation`: no `model_f/v72p2d5/parquet/ttbin/pandas`, only `default_rng(`, no `open(`, no `channel_counts.npz`/real-root literals in tests, frozen P9 streams never sampled, `load_v25` forbidden from injected tests, empty-cwd import creates no files).
- Staleness note (non-blocking): test-file header still says "fresh seeds >= 2026091700" (P8-era); P9 tests actually use `P9_TEST_SEED_* = 2026091730..1739` (verified lines 930–950) and assert disjointness from frozen P8+P9 streams. Batch the one-line header fix into the next milestone docs pass; tests themselves are correct. **PASS.**

## 8. Bounded smoke — PASS (injected tiny tables/orders only, temp root)

Command (injected `counts=`/`orders=`/`expected_entropies=` seam, P9 gate, temp root; real NPZ / frozen streams / production paths never touched):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c "<injected P9 run: 1 SCREEN block × 56 configs + 1 CONFIRM block, n=256, seeds 2026091732/33>"
```

Raw evidence (this review):

- `files ['frozen_plan.json', 'report.md', 'screen_records.json', 'selection_and_confirmation_records.json', 'transcript_accounting.json']`, `nfiles 5 expect5 True`.
- `protocol nbpolar-p9-lower-rate-boundary-screen-confirm gate p9-lower-rate-boundary`; `plan gate_id p9-lower-rate-boundary`; outcome `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` (valid negative on a 1-block toy shape; shape-gated, not a claim).
- `wall 3.537s rss 220155904 bytes`; margins vs budgets: `3600 − wall ≈ 3596.5 s`, `2 GiB − RSS ≈ 1.93 GB`. Production shape is ≈23k SC calls (SCREEN 56×192 = 10752 arms + CONFIRM 640×2 arms, ×2 layers at N=256 GF32); the P8 35-point precedent ran inside the same envelope and P9 is only ≈1.6× SCREEN arms with identical per-arm cost, so the envelope is credible. No budget breach path was exercised by the smoke (expected on a 1-block toy). **PASS.**

## 9. Scope / premises — PASS WITH RECORDED WORKTREE-SCOPING NOTE (no blocking deviation)

Commands:

```bash
git status --porcelain
git rev-parse HEAD  # ab173f2a5e17336383a897b941080b731ba3dd9e
git log --oneline -3
ls .workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/  # absent
cat .workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/STATUS.yaml  # reads/attempts 0
```

Raw evidence:

- `HEAD` unchanged: `ab173f2a5e17336383a897b941080b731ba3dd9e` (matches implementation-notes claim); `git log` shows no new commit; no push.
- Strict `git status --porcelain` does NOT equal the narrow Wave-A set: tracked modifications span P3 STATUS/AGENTS/CURRENT_TASK/`__init__`/empirical_* /docs/tasks.md (16 files), plus many `??` untracked Wave dirs/files (P4–P9 queues, `target_rate.py`, tests, P9 spec, etc.). Per `AGENTS.md` §10.1 item 11 (dirty-worktree scope review), this review adjudicates BY SCOPE: all P9 Wave-A files are present (P9 spec + P9 tasks section with unchecked boxes, `target_rate.py` delta, test additions, `P9_FREEZE.md`/`P9_IMPLEMENTATION_NOTES.md`, `STATUS.yaml`); unrelated dirt (P3/AGENTS/docs/probe-tier etc.) was NOT read for acceptance, does NOT enter the frozen command, and is preserved untouched. No accepted-module tracked file in the P9 dependency cone was modified (`sc.py`, `prior.py`, `construction.py`, `transform.py`, `algebra.py` show no diff); P7/P8 evidence roots untouched (§3); frozen inputs/old roots/sibling checkouts/`results/`/`outputs_comparison/` untouched.
- No commit; output root still absent; `artifact_reads_used: 0`, `attempts_used: 0` still. **PASS with the scoping note above (non-blocking).**

## Delta-only verdict

**Delta-only: PASS.** The change adds ONLY the closed-choice `--gate-id` selector, P9 protocol/mode/tag-domain/frame identifiers, P9 56-point grid + seeds + root + labels + frozen command, P9 prior-stream disjointness, and gate-aware plan/report/accounting plumbing; the P8 path (protocol/prefix/labels/grid/seeds/command/behavior) is preserved; SC/prior/construction/tag/outcome/support/truth/accounting semantics and P7/P8 evidence roots are unchanged. P9 identifiers differ from P8 in every required slot; cross-grid use is refused both ways.

## Complete frozen record (the only authorized execution)

- Gate id: `--gate-id p9-lower-rate-boundary` (required, closed-choice `p8-target-rate-screen-confirm | p9-lower-rate-boundary`; `main` refuses missing/invalid before any artifact access).
- Protocol/mode: `nbpolar-p9-lower-rate-boundary-screen-confirm` / `static-lower-rate-boundary-screen-confirm` (P8: `nbpolar-p8-target-rate-screen-confirm` / `static-target-rate-screen-confirm`).
- Tag-domain prefix: `nbpolar-p9-lower-rate-boundary-seed` (P8: `nbpolar-p8-target-rate-seed`); frame prefix `nbpolar-p9-lower-rate-boundary` (P8: `nbpolar-p8-target-rate`).
- Orders: P7 `.../NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/construction_orders.json`, sha `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104` (canonical `layers` digest, validated before open).
- Support: column-normalize → floor `1e-15` → renormalize per Bob column; `p_b` = column totals/total; `P1`/`P2` = accepted `derive_p1`/`derive_p2` under `A=32*U1+U2`; preconditions H1 `0.02428054681872374` / H2 `0.7767572780789994` / total `0.8010378248977232` (±1e-12), column error ≤1e-12, floor entropy change ≤1e-9, else `BLOCKED(target_population_contract)` with zero SC and no root.
- Streams/grids: SCREEN `2026091710 1711 1712` ×64 = 192; K1 `[0,2,4,6,8,12,24,45]` × K2 `[0,20,40,50,60,70,80]` = 56 incl. `(0,0)` + `(8,80)`; CONFIRM `2026091720..1724` ×128 = 640, disjoint from SCREEN + priors (`1650..52`, `1660..64`, `1680..82`, `1690..94`); Toeplitz master `stream+10000`, P9-phase/arm/block separated, 2623 public bits/tag.
- Command (3 lines, 13 flags, verbatim):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_rate --gate-id p9-lower-rate-boundary --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --orders .workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/construction_orders.json --n 256 --floor 1e-15 --screen-seeds 2026091710 2026091711 2026091712 --screen-blocks 64 --k1-grid 0 2 4 6 8 12 24 45 --k2-grid 0 20 40 50 60 70 80 --confirm-seeds 2026091720 2026091721 2026091722 2026091723 2026091724 --confirm-blocks 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm
```

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/` (ABSENT; must be absent at launch) with exactly 5 scalar-only files: `frozen_plan.json`, `screen_records.json`, `selection_and_confirmation_records.json`, `transcript_accounting.json`, `report.md`.
- Budgets: `timeout 3600`, `ulimit -v 2097152`, 2 GiB RSS, 3600 s wall; breach → `resource_abort` fill + `BLOCKED`, still 5 files.
- Schema/gates/labels: 11 integrity gates in frozen order (`orders_identity_and_permutations`, `target_population_contract`, `coverage_complete_and_disjoint`, `pairing_and_buckets`, `truth_leak_zero`, `undetected_zero`, `nonfinite_zero`, `resource_abort_zero`, `disclosure_and_recount_exact`, `attempt_read_accounting_exact`, `resource_limits_met`); 2 scientific gates (`confirm_empirical_exact_at_least_618_of_640`, `confirm_empirical_wilson_lower_bound_at_least_0p95`); labels `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` / `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` / `TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED` / `BLOCKED(<earliest gate>)`; accounting `5*(K1+K2)+64` + `2623`/tag + literal recount with zero mismatch; `z = 1.6448536269514722`.

## Findings (file:line)

- Non-blocking (ratified): parser-optional / main-required gate-id split — `target_rate.py:2598-2604` (parser `default=None`) vs `target_rate.py:2624-2631` (`main` refuses `None`/invalid with return 2). Execution-level REQUIRED holds; P8 injected-seam compatibility preserved. Ratified PASS.
- Non-blocking (scope): dirty worktree beyond Wave-A — `git status --porcelain` (§9). Adjudicated by scope per AGENTS §10.1-11; P9 scope clean, unrelated dirt preserved. No repair required before execution.
- Non-blocking (docs): stale test-header bound — `test_nbpolar_target_rate.py:6,38-40` says `>= 2026091700`; P9 tests correctly use `2026091730..1739` (lines 930–950) with disjointness asserts. One-line header refresh at the next milestone; not a gate blocker.
- No blocking finding. No timeless-hash/remote-equality demand was applied (provenance, not execution lock, per AGENTS §3/§10.3). No `docs/decision-log.md` / `docs/troubleshooting.md` update needed (no new failure mode).

## Closure statements

- The V25 NPZ content was NOT opened by this review (metadata `stat` size `25166822` only; no `load_v25_channel_counts`, no `np.load`, no archive listing of contents).
- Artifact reads still `0/1`; scientific attempts still `0/1` (`STATUS.yaml`: `artifact_reads_used: 0`, `attempts_used: 0`).
- The real output root `.../lower_rate_screen_confirm/` is still ABSENT.
- The real gate command was never run; no production output was created; no Model-F/raw/held-out/real/EVAL path was entered; no old-root write, commit, or push occurred.
- Independent Pre-RESULT review remains required before any result/label publication; the run may not accept its own work.
