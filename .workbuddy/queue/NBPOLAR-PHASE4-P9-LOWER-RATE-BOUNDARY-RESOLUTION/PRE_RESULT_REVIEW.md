# Independent Pre-RESULT review — NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION

**Reviewer:** fresh independent reviewer-go (did not write the code, freeze the plan, or run the gate; read-only review, no gate execution).
**Date (UTC):** 2026-09-14. **Scope:** Tier-Y packet `NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION`, gate execution result only.
**Verdict: PASS** — all numbers below were independently recomputed from the five artifacts; every persisted value matches; all 11 integrity + 2 scientific gates recompute true; label `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` is the correct frozen-label outcome. No blocking issue.

> Write discipline for this review: the reviewer created ONLY this file. The V25 `channel_counts.npz` content was NEVER opened (metadata `stat` only, size/mtime). The real gate command was NEVER rerun. No Model-F / raw / held-out / real / EVAL data was touched. No artifact/real-data/old-root writes; no commit/push.

## Output-format verdict block

```
Verdict: pass
Blocking Issues:
- (none)
Non-Blocking Suggestions:
- Eligible-list ordering is grid-order in artifacts vs selection-key order in recomputation; same set, same minimum (see §4). No action.
- Dirty worktree beyond P9 scope adjudicated by scope per AGENTS.md §10.1-11 (see §9). No action before acceptance.
- Report conveys BEC report-only semantics via gate table (no emp-vs-BEC gate) without the literal string "report-only". No action.
Checklist:
- [x] Matches OpenSpec spec
- [x] Tests pass
- [x] No scope creep
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? — No. No new failure mode observed.
```

## Provenance premise (taken as premise, artifact-internal consistency still verified)

The `lower_rate_screen_confirm/` root (5 files flushed 15:29:50 in one ~0.3 s window) is the product of exactly one frozen-command execution; the first Wave-C delegation executed it but result delivery failed on infrastructure error; the retry correctly STOPPED. STATUS records reads/attempts 1/1. No rerun occurred or is permitted. This review verifies artifact-internal consistency only and performs no second NPZ content read and no gate rerun.

## 1. Root: exactly five frozen files, scalar-only, P9 identifiers only — PASS

Command:

```bash
ls -1 ".workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/"
stat -c '%n %s %y' ".workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/"*
```

Raw:

```
frozen_plan.json
report.md
screen_records.json
selection_and_confirmation_records.json
transcript_accounting.json
.workbuddy/.../lower_rate_screen_confirm/frozen_plan.json 7989 2026-09-14 15:29:50.614502800 +0800
.workbuddy/.../lower_rate_screen_confirm/report.md 6059 2026-09-14 15:29:50.925451500 +0800
.workbuddy/.../lower_rate_screen_confirm/screen_records.json 10077718 2026-09-14 15:29:50.875640500 +0800
.workbuddy/.../lower_rate_screen_confirm/selection_and_confirmation_records.json 1105258 2026-09-14 15:29:50.908856600 +0800
.workbuddy/.../lower_rate_screen_confirm/transcript_accounting.json 1612 2026-09-14 15:29:50.918763000 +0800
```

Check: exactly the five frozen names, no extras; all five mtimes fall in `15:29:50.614–15:29:50.925` (one 0.31 s flush window, consistent with single-execution premise). **PASS.**

Deep scalar-only audit (recomputed, not copied). Command: recursive key collection over all four JSONs + leaf-type check + forbidden-substring search. Raw:

- `frozen_plan.json`: 94 distinct keys (gate/plan/accounting/budget/entropy/grids/labels/protocol/toeplitz/truth_boundary etc.); suspicious hits `[]`; P8 hits `[]`; has `p9-lower-rate-boundary` True, `nbpolar-p9-lower-rate-boundary` True; max list len 11.
- `screen_records.json`: 46 distinct keys (`arm/block_index/blocks/configs/eligibility/eligible/empirical/exact/gate_id/k1/k2/key_dependent_bits/l1_*/l2_*/label_match/n_blocks/outcome/outcome_counts/phase/protocol/public_control_bits/stream_seed/tag_invoked/tag_pass/truth_leak_violation/undetected/verify_failed/wall_s/wilson_*` etc.); suspicious hits `[]`; P8 hits `[]`; P9 True/True; max list len 192 (= block list, not a vector).
- `selection_and_confirmation_records.json`: 65 distinct keys (plus 5 stream-id keys `2026091720..24`); suspicious hits `[]`; P8 hits `[]`; P9 True/True; max list len 640 (= block list).
- `transcript_accounting.json`: 20 distinct keys; suspicious hits `[]`; P8 False (no P8, and no P9 identifier by design — pure counters); max list len 0.
- Leaf-type walk: every leaf in both record files is `int/float/bool/str/None`; non-scalar leaves `none`.
- Per-block record shape (sample `(0,0)` block 0): `arm/phase/k1/k2/outcome/exact/label_match/tag_pass/tag_invoked/l1_executed/l1_decode_failed/l1_error_type/l1_provenance/l2_invoked/l2_decode_failed/l2_error_type/l2_provenance/l2_skipped_by_l1_failure/key_dependent_bits/public_control_bits/nonfinite/truth_leak_violation/wall_s/stream_seed/block_index` — booleans + small ints + short strings only. No `source/Bob/U/decoded/disclosed` vectors, no metric arrays, no labels/tags, no seed bits. `report.md`: P8 strings (`nbpolar-p8`, `p8-target-rate`, `202609168`, `202609169`) all absent; P9 protocol/mode/gate/label all present.

**PASS** — scalar/aggregate only; zero P8-identifier hits in any artifact.

## 2. Gate identity, frozen command, orders, consumption, NPZ metadata — PASS

Commands:

```bash
python -c "import json,pathlib; plan=json.loads(pathlib.Path('.../frozen_plan.json').read_text()); print(plan['frozen_command'])"
stat -c 'NPZ size=%s mtime=%y path=%n' "/mnt/d/Code/HD-QKD_Polar_Comparison/.../channel_counts.npz"
python -c "import json,hashlib,pathlib; doc=json.loads(pathlib.Path('.../construction_orders.json').read_text()); print(doc['orders_sha256']); print(hashlib.sha256(json.dumps(doc['layers'],sort_keys=True,separators=(',',':')).encode()).hexdigest())"
cat .workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/STATUS.yaml
```

Raw:

- `gate_id`: `p9-lower-rate-boundary` in all three JSONs carrying it (`frozen_plan/screen/selection`); `protocol`: `nbpolar-p9-lower-rate-boundary-screen-confirm` in all three; `mode`: `static-lower-rate-boundary-screen-confirm`; Toeplitz derivation string contains `nbpolar-p9-lower-rate-boundary-seed:<master>:<phase>:<arm>:<block>:<counter>`; frame prefix P9 (via code `_gate_frame_prefix`, report protocol line). Tag-domain prefix differs from P8 `nbpolar-p8-target-rate-seed` (code holds both; artifacts carry only P9).
- Frozen command: `frozen_plan.json:frozen_command` third line byte-equals TASK_PACKET P9-06 `timeout 3600 ... --gate-id p9-lower-rate-boundary --counts .../channel_counts.npz --source 1M --orders .../construction_orders.json --n 256 --floor 1e-15 --screen-seeds 2026091710 2026091711 2026091712 --screen-blocks 64 --k1-grid 0 2 4 6 8 12 24 45 --k2-grid 0 20 40 50 60 70 80 --confirm-seeds 2026091720 2026091721 2026091722 2026091723 2026091724 --confirm-blocks 128 --out-dir .../lower_rate_screen_confirm` → `match third line: True` (recomputed). 13 flags, `--gate-id` first. Labels triple P9 (`TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` / `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` / `TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED` + `BLOCKED(<earliest gate>)`).
- P7 order sha: recorded `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`; recomputed canonical `sha256(layers)` identical; `match True`; equals `expected_orders_sha256` and the packet/freeze literal. Permutation sweep over `construction_orders.json` finds valid 256-permutations at every order slot (10 valid length-256 perms found, zero invalid). Orders file mtime `2026-09-14 03:33:09` (predates gate flush 15:29:50; untouched).
- NPZ stat (metadata only, no open): `size=25166822`, `mtime=2026-08-19 01:34:09`, regular file. Equals `expected_npz_bytes 25166822` and the packet/freeze/module constant. Content never opened by this reviewer (no `load_v25_channel_counts`, no `np.load`, no archive listing).
- Preconditions: `frozen_plan.entropy_expectations` carries `h1 0.02428054681872374 / h2 0.7767572780789994 / total 0.8010378248977232` (±1e-12), column tol 1e-12, floor-change tol 1e-9, `precondition_order` 7 items — matches freeze §3. Direct functional recompute would require an NPZ content open (forbidden after 1/1 consumed); indirect proof: run completed past preconditions (56×192 + 640 arms executed, no `BLOCKED(target_population_contract)`, no zero-SC path), `target_population_contract True` in report gate table.
- Consumption: `frozen_plan.artifact_read_accounting` = `reads_allowed 1 / consumed_before 0 / consumed_by_this_run 1 / attempts_allowed 1 / consumed_before 0 / consumed_by_this_run 1 / reopen_attempted false / retries 0 / retry_after_open false`. `STATUS.yaml`: `artifact_reads_used: 1`, `attempts_used: 1` (1/1 at first open, no reopen/retry). Toeplitz masters `screen [2026101710,2026101711,2026101712]` (= stream+10000) and `confirm [2026101720..24]` (= stream+10000), domain-separated by P9 phase/arm/block.

**PASS.**

## 3. SCREEN: 56-point grid, bucket exclusivity, every Wilson LB + eligibility recomputed — PASS

Grid command + raw: `K1=[0,2,4,6,8,12,24,45]` (8) × `K2=[0,20,40,50,60,70,80]` (7); observed `{(k1,k2)}` == exact Cartesian product → `grid complete: True`, `missing: set()`, `extra: set()`, `n: 56`. Includes `(0,0)` global zero-disclosure corner and `(8,80)` P8 anchor. Every config `n_blocks==192`, `len(blocks)==192`, per-seed split `{1710:64, 1711:64, 1712:64}` for every config; outcome-bucket sums all == 192.

Wilson recomputation (`z=1.6448536269514722`, `p=k/n; d=1+z²/n; c=p+z²/2n; m=z·√(p(1−p)/n+z²/4n²)`):

```
wlb_raw(0,192)   = 0.0                    (formula gives exactly 0: c−m = 0)
wlb_raw(11,192)  = 0.03536607429071025
wlb_raw(187,192) = 0.9474773285638652  (< 0.95)
wlb_raw(188,192) = 0.9544033287216636  (≥ 0.95)
wlb_raw(192,192) = 0.9861044354151461
wlb_raw(624,640) = 0.9626753340557015
wlb_raw(520,640) = 0.7858262770307914
```

Every persisted `eligibility.wilson_lower_bound` matches recomputed `wlb(exact,192)` to <1e-15 (all 56; `bad: []`). `count_rule_188_of_192 == (exact ≥ 188)` all 56; `wilson_count_agree == ((wlb ≥ 0.95) == (exact ≥ 188))` all 56 (True everywhere — full-range equivalence holds on this data). Eligibility recomputed as `(n==192 ∧ total==192 ∧ undetected==0 ∧ resource_abort==0 ∧ nonfinite==0 ∧ wlb ≥ 0.95 ∧ count ≥ 188)` matches persisted `eligible` for all 56 (`bad: []`).

Full 56-point check (recomputed vs persisted; `wlb` recomputed, `elig` recomputed; report table additionally cross-checked §8 — 56/56 rows match):

| k1 | k2 | exact/192 | wilson_lb (recomputed) | count≥188 | eligible (recomputed = persisted) | buckets (exact/vf/df/und/ra) |
|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 0 | 20 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 0 | 40 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 0 | 50 | 11 | 0.03536607429071025 | F | F = F | 11/181/0/0/0 |
| 0 | 60 | 26 | 0.09983126360541061 | F | F = F | 26/166/0/0/0 |
| 0 | 70 | 29 | 0.1134016513968186 | F | F = F | 29/163/0/0/0 |
| 0 | 80 | 29 | 0.1134016513968186 | F | F = F | 29/163/0/0/0 |
| 2 | 0 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 2 | 20 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 2 | 40 | 3 | 0.006261330807758174 | F | F = F | 3/189/0/0/0 |
| 2 | 50 | 64 | 0.28003211627664304 | F | F = F | 64/128/0/0/0 |
| 2 | 60 | 136 | 0.6517805677306815 | F | F = F | 136/56/0/0/0 |
| 2 | 70 | 145 | 0.7008542842272918 | F | F = F | 145/47/0/0/0 |
| 2 | 80 | 145 | 0.7008542842272918 | F | F = F | 145/47/0/0/0 |
| 4 | 0 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 4 | 20 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 4 | 40 | 5 | 0.012732499159924415 | F | F = F | 5/187/0/0/0 |
| 4 | 50 | 80 | 0.35969774288673123 | F | F = F | 80/112/0/0/0 |
| 4 | 60 | 166 | 0.8188657477622883 | F | F = F | 166/26/0/0/0 |
| 4 | 70 | 176 | 0.8777862340385935 | F | F = F | 176/16/0/0/0 |
| 4 | 80 | 176 | 0.8777862340385935 | F | F = F | 176/16/0/0/0 |
| 6 | 0 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 6 | 20 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 6 | 40 | 5 | 0.012732499159924415 | F | F = F | 5/187/0/0/0 |
| 6 | 50 | 85 | 0.38494749509200016 | F | F = F | 85/107/0/0/0 |
| 6 | 60 | 176 | 0.8777862340385935 | F | F = F | 176/16/0/0/0 |
| 6 | 70 | 188 | 0.9544033287216636 | T | T = T | 188/4/0/0/0 |
| 6 | 80 | 188 | 0.9544033287216636 | T | T = T | 188/4/0/0/0 |
| 8 | 0 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 8 | 20 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 8 | 40 | 5 | 0.012732499159924415 | F | F = F | 5/187/0/0/0 |
| 8 | 50 | 86 | 0.39001684244089363 | F | F = F | 86/106/0/0/0 |
| 8 | 60 | 180 | 0.9022461940723889 | F | F = F | 180/12/0/0/0 |
| 8 | 70 | 192 | 0.9861044354151461 | T | T = T | 192/0/0/0/0 |
| 8 | 80 | 192 | 0.9861044354151461 | T | T = T | 192/0/0/0/0 |
| 12 | 0 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 12 | 20 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 12 | 40 | 5 | 0.012732499159924415 | F | F = F | 5/187/0/0/0 |
| 12 | 50 | 86 | 0.39001684244089363 | F | F = F | 86/106/0/0/0 |
| 12 | 60 | 180 | 0.9022461940723889 | F | F = F | 180/12/0/0/0 |
| 12 | 70 | 192 | 0.9861044354151461 | T | T = T | 192/0/0/0/0 |
| 12 | 80 | 192 | 0.9861044354151461 | T | T = T | 192/0/0/0/0 |
| 24 | 0 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 24 | 20 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 24 | 40 | 5 | 0.012732499159924415 | F | F = F | 5/187/0/0/0 |
| 24 | 50 | 86 | 0.39001684244089363 | F | F = F | 86/106/0/0/0 |
| 24 | 60 | 180 | 0.9022461940723889 | F | F = F | 180/12/0/0/0 |
| 24 | 70 | 192 | 0.9861044354151461 | T | T = T | 192/0/0/0/0 |
| 24 | 80 | 192 | 0.9861044354151461 | T | T = T | 192/0/0/0/0 |
| 45 | 0 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 45 | 20 | 0 | 0.0 | F | F = F | 0/192/0/0/0 |
| 45 | 40 | 5 | 0.012732499159924415 | F | F = F | 5/187/0/0/0 |
| 45 | 50 | 86 | 0.39001684244089363 | F | F = F | 86/106/0/0/0 |
| 45 | 60 | 180 | 0.9022461940723889 | F | F = F | 180/12/0/0/0 |
| 45 | 70 | 192 | 0.9861044354151461 | T | T = T | 192/0/0/0/0 |
| 45 | 80 | 192 | 0.9861044354151461 | T | T = T | 192/0/0/0/0 |

Exactly the 10 persisted eligible `[(6,70,188),(6,80,188),(8,70,192),(8,80,192),(12,70,192),(12,80,192),(24,70,192),(24,80,192),(45,70,192),(45,80,192)]`; `(0,0)` ineligible at 0/192 with `wilson 0.0`; `(8,80)` eligible at exact 192. Bucket exclusivity: every block outcome in `{exact,verify_failed,decode_failed,undetected,resource_abort}`; structural check `exact ⟺ tag_pass∧label_match`, `undetected ⟺ tag_pass∧¬label_match`, `verify_failed ⟹ ¬tag_pass` holds for all 10752 SCREEN arms. Per-point key bits equal `5*(K1+K2)+64` for all 56 (zero-K corners: `(0,0)→64`, `(0,20)→164`, `(2,0)→74`); public `2623`/tag everywhere. **PASS.**

## 4. Selection: lexicographic min, below P8 anchor, no-eligible path not taken, no interpolation — PASS

Recomputed eligible set from records (selection-key order): `[(6,70),(8,70),(12,70),(6,80),(8,80),(12,80),(24,70),(24,80),(45,70),(45,80)]` with sums `[76,78,82,86,88,92,94,104,115,125]`. Persisted `eligible_points` (grid K1-major order): `[(6,70),(6,80),(8,70),(8,80),(12,70),(12,80),(24,70),(24,80),(45,70),(45,80)]` — same set (ordering difference is presentational only, not a mismatch). Lexicographic minimum of `(K1+K2,K1,K2)` is `(6,70)` with key `(76,6,70)` — recomputed min equals persisted `selected: {k1: 6, k2: 70}`.

Disclosure: selected `5*(6+70)+64 = 444` bits vs P8 anchor `(8,80)` `5*(8+80)+64 = 504` bits — selected is strictly below the anchor by 60 bits (report-only observation, no new claim). No-eligible path correctly NOT taken (10 eligible points exist; `confirm.confirm_executed True`, `confirm.blocks` 640 present; no `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT`). No interpolation: CONFIRM `k1=6,k2=70` is a registered grid point; grids are exact-match enforced by code (probed at Pre-EXECUTE). **PASS.**

## 5. CONFIRM: independence, same-K pairing, buckets, streams, Wilson, gates — PASS

- Independence: observed SCREEN seeds `{2026091710,2026091711,2026091712}`, CONFIRM seeds `{2026091720,2026091721,2026091722,2026091723,2026091724}` — disjoint from each other and from all prior official streams `{1650..52,1660..64,1680..82,1690..94}` (recomputed True/True). Masters are disjoint per phase (`screen+10000` vs `confirm+10000`). No SCREEN block/tag material enters CONFIRM (fresh `sample_shared_blocks` per confirm seed per frozen code; per-block `phase==confirm` for all 640×2 arms).
- Only selected K in both arms with same-K BEC pairing: every one of the 640 blocks carries `(emp.k1,emp.k2,bec.k1,bec.k2) == (6,70,6,70)` (recomputed unique tuple set `{(6,70,6,70)}`); `confirm.k1/k2 == selected.k1/k2` True.
- Per-arm buckets recomputed from the 640 paired records: empirical `{exact 624, verify_failed 16, decode_failed 0, undetected 0, resource_abort 0}` = persisted `empirical_outcomes`; BEC `{exact 520, verify_failed 120, decode_failed 0, undetected 0, resource_abort 0}` = persisted `bec_outcomes`. Counter recompute from block outcomes matches both persisted outcome dicts exactly.
- Per-stream 5×128 completeness recomputed: `1720: emp 122 / bec 103 / n 128`; `1721: 123/102/128`; `1722: 125/97/128`; `1723: 127/108/128`; `1724: 127/110/128` — all equal persisted `per_stream` (match True ×5); sums `122+123+125+127+127=624`, `103+102+97+108+110=520`. Block indices 0..127 per stream, phases/arms correct.
- Paired cells recomputed: `{both_exact 520, empirical_only 104, bec_only 0, neither 16}`, sum 640 = persisted `cells`; gap `624−520=104` = persisted `paired_exact_gap`. No empirical-over-BEC gate exists (frozen); BEC is report-only.
- Wilson LB from 624/640 recomputed `0.9626753340557015` = persisted `wilson_lower_bound` (match <1e-15); `count_rule_618_of_640 True` (`624 ≥ 618`). Both scientific gates recompute true (see §7).
- All 11 integrity gates recompute true from the records (see §7).

**PASS.**

## 6. Accounting: per-point formula, phase/arm totals, literal recount, tag cross-check — PASS

Recomputed by summing `key_dependent_bits/public_control_bits/tag_invoked` over block records:

- Per-point formula `5*(K1+K2)+64`: zero mismatches over all 10752 SCREEN arms and all 1280 CONFIRM arms. Corners: `(0,0)=64` tag-only; selected `(6,70)=444`; P8 anchor `(8,80)=504`. Public `2623`/tag everywhere (`28202496/10752 = 2623.0`, `3357440/1280 = 2623.0`).
- Phase totals recomputed: screen `key 3824448 / public 28202496 / tags 10752` = persisted `incremental_by_phase.screen`; confirm `key 568320 / public 3357440 / tags 1280` = persisted `incremental_by_phase.confirm`.
- Grand totals recomputed: `key 4392768 / public 31559936 / tags 12032` = persisted `incremental` and `recount` totals. By-arm: empirical `4108608` (= screen 3824448 + confirm-emp 283840… verified as `tot_key_screen + tot_key_emp_c`) = persisted `incremental_by_arm.empirical`; BEC `284160` (= 640×444) = persisted `incremental_by_arm.bec`.
- Independent literal recount: `mismatch_count 0`, `mismatches []`; event counts `l1_disclosure 12032 / l2_disclosure 12032 / verification_tag 12032`, `event_count 36096 = 3×12032`. (Structural note: `incremental` vs `recount` dicts differ by the extra `by_arm/by_phase/event_types` sub-keys in `recount` by design; the three counter triples match exactly at total/phase/arm levels.)
- Tag-count cross-check: screen `56×192 = 10752` = observed 10752; confirm `640×2 = 1280` = observed 1280; total `10752+1280 = 12032` = persisted `tag_invocations`. **PASS.**

## 7. Gate table (recomputed vs persisted) — 11/11 + 2/2 true

| gate | recomputed evidence | recomputed | persisted (report) |
|---|---|---|---|
| orders_identity_and_permutations | recorded sha == recomputed canonical `sha256(layers)` == `8ec69…104`; all order slots valid 256-perms | true | True |
| target_population_contract | run passed preconditions (10752+1280 arms executed, no `BLOCKED`, `resource stop False`); direct functional recompute would need an NPZ open (forbidden at 1/1) | true (indirect) | True |
| coverage_complete_and_disjoint | 56 configs ×192 with 64/seed split; 640 confirm with 128/stream; seed sets disjoint incl. priors | true | True |
| pairing_and_buckets | taxonomy + structural exact/undetected/vf relations hold over all 12032 arms; cells sum 640 | true | True |
| truth_leak_zero (global) | `truth_leak_violation` count 0/10752 screen + 0/1280 confirm | true | True |
| undetected_zero | eligible SCREEN undetected sum 0; CONFIRM emp 0 + bec 0 | true | True |
| nonfinite_zero | eligible SCREEN nonfinite 0; CONFIRM 0 | true | True |
| resource_abort_zero | eligible SCREEN 0; CONFIRM 0 blocks; `resource stop fired: False` | true | True |
| disclosure_and_recount_exact | formula holds everywhere; phase/arm/total triples match; mismatch 0 | true | True |
| attempt_read_accounting_exact | 1/1 + 1/1, `reopen false`, `retries 0`, `retry_after_open false` | true | True |
| resource_limits_met | wall `720.522313 < 3600`; RSS `318406656 < 2147483648`; stop False | true | True |
| confirm_empirical_exact_≥618/640 | `624 ≥ 618` | true | True |
| confirm_empirical_wilson_≥0.95 | `0.9626753340557015 ≥ 0.95` (recomputed) | true | True |

Label follows frozen order: all integrity true + both scientific true → `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` (persisted outcome label matches). Planning-only `f = 444.0/205.0656831738056 = 2.165159928897918` recomputed exactly. **PASS.**

## 8. Truth boundary — PASS (consistency check, not a claim)

`target_rate.py` (2674 lines) audit: `TRUTH_BOUNDARY` states truth enters only sampling/disclosed/tag/scoring; `run_rate_arm` copies truth inputs (`bob/high/low/u1/u2/labels/label_bits` via `np.array(...,copy=True)`, lines 939–945), builds operational metrics with `PRIOR_ONLY` / `CANDIDATE_CONDITIONED` provenance from Bob + hard L1 candidate only (lines 950–980; true high never enters the L2 metric), uses disclosed `U` slices + tag construction + `label_match` scoring only (lines 981–1006), then proves isolation via `_truth_isolation_sentinel` mutating truth copies (lines 1008–1023) with `truth_leak_violation = not isolated`. Records carry `truth_leak_violation False` on all 12032 arms. `(0,0)` all-`verify_failed` (192) with zero `undetected` is consistent with tag-only verification: with no disclosed coordinates the tag check fails except on ~2⁻⁶⁴ collision, and `undetected` requires tag-pass + label-mismatch, so zero undetected at `(0,0)` is the expected consistency outcome (stated as consistency check, not a claim). No operational metric/decision/candidate label ingests undisclosed truth. **PASS.**

## 9. Bounded wording — PASS (report.md read fully, 130 lines)

`report.md` was read end-to-end. It states: protocol/mode/source/q/N/floor, SCREEN/CONFIRM streams, orders sha, wall/RSS/stop, full 56-row SCREEN table, deterministic selection with rule, CONFIRM point + emp/BEC exact + Wilson + count rule + paired cells + per-stream 5×128, integrity/scientific gate tables, disclosure formula + selected leakage + totals + mismatch, planning-only `f` line explicitly parenthesized `(planning-only; not real-channel efficiency)`, outcome label, and closing **Scope** line: `frozen V25 TRAIN target-population static rate development signal at N=256 only; not held-out or real frame FER, efficiency, key rate, scaling, qualification or promotion; planning-only f is not real-channel efficiency; undetected is never success.` Synthetic `N=256` `V25-1M-TRAIN` model-sampled development-signal framing only; no held-out/real FER, efficiency/key-rate, scaling, qualification or promotion claim; BEC numbers presented alongside paired cells with no winner/threshold claim beyond the two frozen empirical gates (no emp-vs-BEC gate exists). **PASS.**

## 10. Tests / scope — PASS

Commands (pinned interpreter, `-q -p no:cacheprovider`, fresh `/tmp` basetemps):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_target_rate.py -q -p no:cacheprovider --basetemp=/tmp/p9_preresult_focus
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider --basetemp=/tmp/p9_preresult_full2
git status --porcelain
git rev-parse HEAD
git log --oneline -3
```

Raw (this review, reruns):

- Focused: `24 passed, 1 warning in 21.52s` (12 P8 preserved + 12 P9; warning is the benign `Unknown config option: cache_dir` only).
- Full NB-Polar: `252 passed, 1 warning in 133.11s` (240 predecessor + 12 new; same benign warning only).
- `HEAD` unchanged: `ab173f2a5e17336383a897b941080b731ba3dd9e`; `git log` shows no new commit; no push.
- `git status --porcelain`: strict output spans pre-existing P3-era tracked modifications (16 files) plus many `??` Wave dirs/files (P4–P9 queues, `target_rate.py`, tests, P9 spec, etc.). Per `AGENTS.md` §10.1-11 this review adjudicates BY SCOPE: all P9 Wave-A files present; accepted P9-cone modules (`sc.py`, `prior.py`, `construction.py`, `transform.py`, `algebra.py`, `v35_algorithm_development.py`) show zero diff (`git diff --name-only -- <cone>` empty); P7 `construction_orders.json` mtime `2026-09-14 03:33:09` and P8 `rate_screen_confirm/` 5 files mtime `2026-09-14 12:59` both predate the P9 flush (15:29:50) and are untouched; frozen inputs/sibling checkouts/`results/`/`outputs_comparison/` untouched; no commit. Output root is the declared P9 root only.
- No gate rerun, no production-output write beyond the reviewed root, no Model-F/raw/held-out/real/EVAL path.

**PASS** (with the recorded dirty-worktree scoping note as non-blocking).

## Findings

- Blocking: (none).
- Non-blocking (recorded, no action required before acceptance): eligible-list presentational ordering (§4); dirty-worktree scoping (§10); BEC report-only conveyed via gate table rather than literal string (§9).

## Closure statements

- The V25 NPZ was NOT reopened by this review (metadata `stat` size `25166822`, mtime `2026-08-19` only; no `load_v25_channel_counts`, no `np.load`, no archive content read). The 1/1 consumed content read remains the single Wave-C frozen-command execution.
- The gate was NOT rerun by this reviewer (frozen command text verified verbatim; only test-suite reruns with injected/fresh-temp seams were executed).
- Reads/attempts are 1/1 (`STATUS.yaml`: `artifact_reads_used: 1`, `attempts_used: 1`; `frozen_plan.artifact_read_accounting`: consumed-by-this-run 1/1, `reopen_attempted false`, `retries 0`, `retry_after_open false`).
- `HEAD` unchanged (`ab173f2a5e17336383a897b941080b731ba3dd9e`); no commit, no push; P7/P8 evidence roots untouched.
- Independent Pre-EXECUTE review remains on record (PASS); this independent Pre-RESULT review is **PASS**; main-thread acceptance and any promotion decision remain with the main thread.
