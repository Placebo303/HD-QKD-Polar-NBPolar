# Pre-RESULT review — Phase 4-P18 N=32768 1M-HOLD operational microcheck

- Task: `NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK` (Tier Y, claim-bearing single attempt, attempt 1/1 spent)
- Reviewer: independent `reviewer-go` (backup instance), read-only, resumed session
- Date: 2026-09-16 (WSL); HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e`; branch `codex/nbpolar-phase0`
- Scope: the five frozen artifacts under `holdout_microcheck/`, the frozen contract, the runner, test reruns and git scope — **not** a rerun of the gate
- **Verdict: PASS_WITH_COMMENTS** — zero blocking issues; all 17 recomputed gates true, all required arithmetic matches, label coherent. Comments are non-blocking process notes (see end).

## Resumption note (what was recovered vs re-verified)

- A previous `reviewer-go-backup` attempt (session `ses_f59cc2717ffeJejCxUJCt4vp5Y`) was terminated mid-run after completing items 1–8 and the focused test run. Its structured transcript was read as recovery evidence; all of its recorded numbers are reproduced below and were **independently re-verified in this session** (not merely copied).
- Re-verified fresh in this session: file inventory + deep scalar audit; P16 digest from the construction JSON; K/leakage/f replay; manifest; preconditions; blocks + remainder; per-block and aggregate arithmetic; accounting/recount; outcome buckets; all 17 integrity gates; label derivation; consumption/input stats (stat only); protected-input current stat; resources; bounded wording; focused suite (26) and full NB-Polar suite (409) with a zero-protected-opens audit plugin; git scope.
- Recovered (not re-executed): the prior attempt's deep-audit *design* (max-list/string/nonfinite scan) and its zero-protected-opens audit of the focused file. Both were re-run here and agreed; nothing in the recovered transcript is load-bearing without this session's confirmation.
- No rerun of the gate: output-root mtimes are unchanged at 2026-09-16 01:51:27–01:52:05 and the repo has zero writes after 01:52:10 except this review file.

## Provenance and closures (read first)

- This review **never content-opened either protected input**. The V25 TRAIN NPZ and the HOLD parquet were inspected only via `os.stat` (size, mtime_ns, mode); no read, no np.load, no pandas read. Commands are summarized at the end of this review.
- The gate was **not rerun**. No process executed `holdout_microcheck` in this session. The output root contains exactly the five run-time files with run-time mtimes.
- Consumption state (from the run's own persisted accounting, not re-consumed): NPZ opens 1, parquet opens 1, attempts 1 — allowed 1/1/1 each; no reopen, no retry.
- Test runs used the pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest -q -p no:cacheprovider` with fresh `/tmp` basetemps (`/tmp/p18_review_full_1789498256`, `/tmp/p18_review_focused_1789500042`) and an audit plugin wrapping `builtins.open`/`os.open` for both protected path fragments. Both runs reported `protected_open_hits: []` with guard sanity true.
- The only file written by this review is this document.

## 1. Root inventory and scalar-only audit — PASS

Command (pinned interpreter, inline): recursive `Path.rglob('*')` listing + `os.stat` sizes.

- Recursive entries: exactly
  `aggregate_summary.json`, `frozen_plan.json`, `input_and_construction_identity.json`, `per_block_outcomes.jsonl`, `report.md` — count = 5, no sidecars, no checkpoints, no `.tmp`.
- Sizes (bytes): frozen_plan 9842, identity 5390, per_block 3118, aggregate 9951, report 2928 — all equal the recorded five-file schema sizes.
- `per_block_outcomes.jsonl`: 3 lines, `block_index` [0, 1, 2], 36 keys per line, all three key sets identical, and equal to the frozen key set (block-record minus `stream_seed`, plus `frame_start/frame_end/frame_count/raw_ser/l1_nll_bits/l2_nll_bits/total_nll_bits/total_nll_bits_per_pair/l1_correct/full_block_key_dependent_bits/public_control_bits_per_tag/disclosure_ce_ratio`): missing = [], extra = [].
- Deep scalar-only audit across all five artifacts: max list length = 17 (`integrity_gate_order`); all other lists ≤ 8 (order heads, dev seeds, block ranges, path lists); no non-finite floats; no oversized payload strings — the longest strings are declared prose (`frozen_command` 1065, `operational_rule` 428, `ratio_rule` 421, `claim_scope` 416 chars).
- No private vectors/labels/metrics/raw rows/tag seed bits: the only `seed`-named keys are `predecessor_dev_seeds` (public P16 dev seeds) and `tag_seed_domain` (the template string `nbpolar-p18-holdout-microcheck-seed:<master>:<n>:<block_index>`); the only `head` keys are `l1_head8`/`l2_head8` (8-value heads, full orders stay in the immutable P16 file). No hex/binary seeds, no symbol arrays, no per-frame rows.

## 2. Identity / manifest / preconditions — PASS

Command (inline): read the P16 construction JSON (`JSON only`) and recompute the canonical digest from the replicated recipe; rebuild K/leakage/f from ratified literals; JSON-read the split manifest; compare artifact precondition values to the literals.

- P16 digest recomputed **independently here**: `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` = `cell.freeze_sha256` = artifact `digest_recomputed` = `digest_expected` (all four equal; `digest_match` true). Recipe replicated only from the JSON `cell` payload keys `n,k_total,k1,k2,l1_order,l2_order,pooled_e1_mean,pooled_h1_mean,pooled_e2_mean,pooled_h2_mean` with `json.dumps(sort_keys=True, separators=(",",":"))` + SHA-256.
- P16 protocol `nbpolar-p16-operational-f13-gate`, `frozen_before_first_dev: true`; orders are length-32768 valid permutations (l1/l2 independently checked); `l1_head8`/`l2_head8` equal the recorded heads.
- K replay: `floor((1.3*32768*0.8010378248977231 - 64)/5) = 6811`; `319 + 6492 = 6811`; leakage `5*6811 + 64 = 34119`; `f = 1.2998502888172847 ≤ 1.3`; limit `1.3*N*h_total = 34122.92968012317` bits > 34119.
- Split manifest (`nbldpc_v25_split_manifest_v1`, JSON read of `nbldpc_v25_20260818/run_04/split_manifest.json`): 1M `type2_1M_20260121_184040` HOLD = 400 frames / 102400 pairs exactly as required; TRAIN 1200/307200, VAL 400/102400.
- Preconditions vs ratified literals (recorded → literal, diff):
  - h1 0.024280546818678802 vs 0.02428054681872374 → 4.494e-14 ≤ 1e-12
  - h2 0.7767572780789994 vs 0.7767572780789994 → 0.0 ≤ 1e-12
  - total 0.8010378248976782 vs 0.8010378248977232 → 4.508e-14 ≤ 1e-12; also `h1+h2 == total` exactly
  - floor entropy change 5.1600945738528026e-11 ≤ 1e-9 (floor_total 0.8010378249492791)
  - column dev 1.1357581541915351e-13 ≤ 1e-12; `p_b_sum` 1.0; 7/7 `checks` true.

## 3. Blocks and remainder — PASS

- `block_ranges` in frozen_plan, aggregate and per-block records all equal `[[1600,1727],[1728,1855],[1856,1983]]`; pairwise non-overlapping and contiguous (1727+1=1728, 1855+1=1856).
- Remainder recorded `{frame_start:1984, frame_end:1999, frames:16, symbols:4096, used:false}`; closes the HOLD span `[1600,1999]` exactly; remaining frame gap = 0.
- Block sizes: `frame_count = 128` rows/frame × 256 pairs = 32768 symbols each, for all three blocks (raw rows not persisted by design, so sizes are verified from the formation contract + record fields).
- Runner formation logic (`form_holdout_blocks`, current source, mtime 2026-09-16 00:35:50 predating the run) enforces on the loaded table: 400 unique frames in `[1600,1999]`, rows == 102400, `pair_idx` exactly 0..255 per frame (`np.tile` equality), symbols in `0..1023` (`values.min() >= 0`, `values.max() < N_BOB=1024`), `np.lexsort((pair_idx, frame_id))` ordering only, per-block masks == 32768, remainder mask from the declared range. No RNG/shuffle/sampling path.

## 4. Per-block and aggregate arithmetic — PASS

Recomputed from the persisted scalars (inline script):

| block | L1 NLL bits | L2 NLL bits | total = L1+L2 | 34119/total | total/32768 |
|---|---|---|---|---|---|
| 0 | 773.8421894692976 | 26815.50805586987 | 27589.350245339167 | 1.2366728355903898 | 0.8419601515301259 |
| 1 | 868.6436203445395 | 27015.516878425602 | 27884.160498770143 | 1.2235978917674373 | 0.8509570464712568 |
| 2 | 806.8510674338244 | 26881.237733518323 | 27688.088800952148 | 1.232262733815947 | 0.8449734131149947 |

- Each `total_nll_bits` equals L1+L2 exactly (diff 0.0) and each CE ratio / per-pair value equals 34119/total and total/32768 exactly as recorded.
- Aggregate recomputed L1 2449.3368772476615, L2 80712.26266781379, total 83161.59954506146 == recorded aggregate exactly; aggregate ratio 102357/83161.59954506146 = 1.230820481567787 == recorded.
- Accounting: 34119×3 = 102357 == recorded key-dependent bits; 327743×3 = 983229 == recorded public-control bits; per-record `[34119,34119,34119]` and `[327743,327743,327743]`; 5×319+5×6492+64 = 34119; 10×32768+63 = 327743.
- Transcript recount: `{l1_disclosure:3, l2_disclosure:3, verification_tag:3}` equals the counts derived from the records; tag invocations 3; `mismatches: []`; jsonl line count 3.
- Outcome buckets: recorded `{exact:0, undetected:0, verify_failed:3, decode_failed:0, nonfinite:0, resource_abort:0}`; zero-filled derived counts equal the recorded counts and sum to 3 = block_count. Each record passes a full independent replication of `_record_dict_consistent` (outcome membership, error null, K1/K2, L1/L2 call coherence, tag-outcome coherence, exact⇔outcome, key-dependent/public bit formulas, provenance `PRIOR_ONLY`/`CANDIDATE_CONDITIONED`, `undetected is never success`).
- No threshold machinery in the artifacts: a key-level scan finds only the declared negations/identities `no_threshold_rule`, `recovery_threshold` (value `null`), `f_inequality`; string-token counts in `frozen_plan.json` are all negation contexts (`counter check: no Wilson token at all; FER/winner/promotion/qualification only inside "no …", "not …", "never" statements`). The runner source has 0 hits for `wilson|fer_rate|exact_fraction|EXACT_MIN`.

## 5. Label derivation — PASS

- All **17/17** integrity gates were recomputed from the persisted records/identity/manifest/accounting (not copied) and each is true, agreeing with the persisted `integrity.gates` table: predecessor_construction_identity, hold_split_manifest_identity, target_population_contract, hold_population_exact, blocks_exact_with_declared_remainder, orders_valid_k_replay_f_within_budget, sc_calls_exact (6 == 1+l2 per block == planned max 6), tags_exact (3 == planned 3), buckets_disjoint_exhaustive, truth_isolation (provenance_violations 0; no truth_leak), undetected_zero, nonfinite_zero, disclosure_recount_exact, one_open_per_protected_input, input_stat_unchanged, no_unregistered_access, resource_limits_met_and_no_abort.
- `failing_integrity_gates = []`; the label function consumes **only** the gates dict (`failing` → `BLOCKED(<earliest>)`, else COMPLETE); no count/threshold input exists. Recomputed label = `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE` == persisted, with `exact_count = 0`.
- Coherence check: 0/3 exact outcomes with a COMPLETE label is exactly the frozen no-threshold rule — the exact count is never read by the label path, so 0/3 exact changes nothing; the BLOCKED path was not taken and no recovery reinterpretation exists (`decision.recovery_threshold = null` in both plan and aggregate).

## 6. Consumption, inputs, resources — PASS

- Accounting (persisted): attempts allowed 1 / consumed 1; `counts_content_opens = 1`, `hold_content_opens = 1`, `retries = 0`, `reopen_attempted = false`, `retry_after_open = false`, mode `real` (`v25_npz` + `pairs_parquet`); consumption point = first protected content open (`load_v25_channel_counts`); `opened_content_paths == registered_content_paths` (2 paths).
- Input stats before == after, both artifacts, and current metadata (stat only, no open) still equals the recorded values: NPZ size 25166822 / mtime_ns 1787074449691122000; parquet size 1354289 / mtime_ns 1789155517259296100.
- Resources: in-run wall 37.274417 s ≤ 600 s; peak RSS 520798208 bytes ≤ 2147483648 (2 GiB); `resource_stop_fired: false`, reason `null`; no `resource_abort` record; `sc_calls = 6`, `tag_invocations = 3`, `provenance_violations = 0`.
- Per-block VmPeak/VmSize (kB): 1747608/1583760, 1765524/1601680, 1765524/1583760 — each VmPeak ≤ 2097152 (2 GiB ulimit); per-block RSS HWM 503291904 / 520798208 / 520798208 (max equals aggregate peak).

## 7. Bounded wording (report.md read in full) — PASS

- Scope is exact: "real-input operational microcheck of the frozen V25 1M HOLD split at N=32768 only (three registered chronological blocks, frames 1600..1983)"; "not real-frame FER, reconciliation efficiency, leakage, key rate, scaling superiority, qualification or promotion".
- "Descriptive per-block scalars (no threshold, no recovery gate)"; "sample CE-normalized disclosure ratio: 1.230820481567787 (descriptive only; NOT qualification efficiency)"; "recovery threshold: None (none; 0..3 exact outcomes are descriptive)".
- The three `verify_failed` outcomes appear only in the neutral scalar table (frames, raw SER, NLL, L1-correct, tag, CE ratio) with no winner/regret/repair/rerun suggestion; a targeted grep for regret/repair/fix/retry/winner/promotion language returns only the words "fixed full-block value"/"fixed per-tag value" and the explicit negation sentences.
- Report numbers match the aggregate exactly (wall 37.274417; RSS 520798208; total NLL 83161.59954506146; keydep 102357; public 983229; CE 1.230820481567787; per-block NLL values; remainder 1984..1999/16/4096/False; 17-row gate table all True).

## 8. Tests and scope — PASS

- Focused P18 file (fresh, this session): `26 passed, 1 warning in 25.13s`, audit `protected_open_hits: []`.
- Full NB-Polar suite (fresh, this session, all 25 `test_nbpolar_*.py` files): `409 passed, 1 warning in 1541.41s (0:25:41)`, audit `protected_open_hits: []`, guard sanity true, exitstatus 0. Observed counts are TRUE observations: 26 focused / 409 total.
- `git status --porcelain`: the new/changed P18 set is exactly the declared scope (P18 queue dir; `formal_ir/nbpolar/holdout_microcheck.py`; `tests/test_nbpolar_holdout_microcheck.py`; the P18 spec delta dir; `tasks.md` modified) among the pre-existing P3–P17 untracked/modified waves. P12–P17 roots have no writes after 2026-09-16 01:00 (newest files 2026-09-14/15); X-roots untouched; P16 root newest file 2026-09-15 19:13; P17 root newest 2026-09-15 23:24.
- HEAD unchanged `ab173f2a5e17336383a897b941080b731ba3dd9e`; no new commit; gate artifacts not rewritten (mtimes 01:51:27–01:52:05); no repo file written after 01:52:10 except this review.

## 9. Non-blocking observations (do not affect acceptance)

1. Queue `STATUS.yaml` still carries the pre-execution bookkeeping (`reads_used: 0`, `attempts_used: 0`, `result: null`, `next_gate: INDEPENDENT_PRE_EXECUTE`) — expected at this stage; the main thread/operator should update queue state at acceptance. Not an artifact defect and outside this review's write scope.
2. `raw_ser` and `l1_correct` are descriptive-only and cannot be recomputed independently from the persisted scalars (raw rows/candidates are intentionally not persisted by the packet design). Internal consistency was checked across jsonl/report/aggregate; no issue.
3. The keys `no_threshold_rule`, `recovery_threshold` and `f_inequality` contain the substrings "threshold"/"qualif" as explicit negation/identity declarations; functional greps and downstream summaries must not misread them as live thresholds.

## Reviewer statement

All frozen Pre-RESULT items were recomputed or re-observed in this session. The five artifacts are internally consistent, the accepted P16 identity is independently reproduced, the 17 gates hold, the COMPLETE label is coherent with 0/3 exact outcomes, and the wording stays inside the frozen descriptive scope. No blocking issues. Neither protected input was reopened, and the gate was not rerun.

Commands used (summary): inline Python via the pinned interpreter for inventory/audit, digest recomputation, arithmetic/accounting, gate table and label, consumption and precondition checks; `os.stat` only for protected inputs; `git rev-parse HEAD` / `git log` / `git status --porcelain` / `find -newermt` for scope; the two pytest commands above. Full raw outputs are reproducible from the five artifacts and the P16 construction JSON.
