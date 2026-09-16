# Pre-RESULT review — NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY

Fresh independent Pre-RESULT reviewer (2026-09-13, session window ~18:00-18:20 WSL).
Did not write the code, freeze the plan, or run the gate. Read-only: this file is the
only write. Pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(3.12.3, numpy 2.5.3). Repository `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`;
HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged).

## Verdict

```
Verdict: PASS_WITH_COMMENTS

Blocking Issues: none — result may be solidified as-is.

Non-Blocking Suggestions:
- Persisted `oracle_candidate_divergence` is in-memory only; the per-block bitwise
  P2_hat==P2_true check that underwrites the structural `operational_only==0`
  argument exists in code and in the tiny-n focused test, but is not persisted.
  Optional future observability; not required by the freeze.
- Gate 10 (`attempt_accounting_at_frozen_point`) is a frozen-record
  self-consistency check (module constants + coverage), not an external ledger
  read. `STATUS.yaml` intentionally still holds `attempts_used: 0`; the
  main-thread/operator return owns the ledger update for this consumed attempt.
- Task-prompt text said 13 `test_nbpolar_*.py` files; the actual glob is 14 files
  (201 tests, all passing). Totals are as expected; no action.
- X01 `STATUS.yaml` plus five working docs were last modified 17:06:20-17:20:05
  (packet setup window, before the 17:43 freeze) under `documentation_authorized`;
  already inside the R1 pre-execute 55-entry dirty scope. No old evidence root was
  touched by or after the gate.
```

Checklist:

- [x] Matches OpenSpec spec / frozen packet contract
- [x] Tests pass (focused 9/9; full NB-Polar 201/201)
- [x] No scope creep beyond declared P5 paths + output root
- [ ] docs/decision-log.md or docs/troubleshooting.md needs update? No

## 0. Independence statement

The frozen 384-pair command was **NOT rerun**; attempt 1/1 was consumed at the
first gate L1 SC call (stream 0, block 0). No artifact/real-data/old-root access
beyond the five gate files and the packet's own docs; no sibling checkout content
read; no commit/push/staging. All my numbers below were recomputed with my own
scripts (`/tmp/opencode/p5_review/recompute{,2,3}.py`) directly from the five
persisted files; the p2 table rebuild, the binomial root and the transcript
recount are decoder-free. Test basetemps were fresh `/tmp/opencode/p5_review/bt_*`
with `PYTHONDONTWRITEBYTECODE=1 -q -p no:cacheprovider`, and left the worktree
byte-identical (`git status --porcelain` still 55 entries; no pre-existing repo file was
modified — the only write after 18:00 is this review file).

## 1. Output root and scalar-only audit

`ls -A1` of `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
is exactly the five frozen files, no hidden files, no subdirectories:

| file | bytes | mtime (+0800) |
|---|---|---|
| frozen_plan.json | 6722 | 17:51:56.823661800 |
| per_block_paired_outcomes.json | 535730 | 17:51:56.835588600 |
| transcript_accounting.json | 1240 | 17:51:56.837600300 |
| aggregate_summary.json | 4040 | 17:51:56.837600300 |
| report.md | 1479 | 17:51:56.843296300 |

Single generation: all five within 19.7 ms, directory mtime 17:51:56.842292100.

Deep scalar audit (recursive walk of all four JSON files): 38 top-level plan keys,
35 aggregate keys, 10 transcript keys, 4 per-block doc keys; 384 block records;
each arm record has exactly the 19 frozen scalar fields (no extras); every arm
value is bool/int/float/str/None (`non-scalar arm field values: []`); every
`l1_error_type`/`l2_error_type` is null; `wall_s` finite. The only JSON arrays
are the `blocks` list (384 records) and the `D1` (45) / `D2` (140) coordinate
lists in `frozen_plan.json` — disclosure **coordinates**, not values. No long
hex/base64 blobs (0 matches for 64+-char hex or 80+-char base64 in every file);
no keys suggesting disclosed values, symbols, decoded keys or raw seed bits
(symbol/label/high/low/hat/disclosed-value keys absent; the only "disclosure"
keys are coordinate/accounting metadata). No raw seed bits are persisted; seeds
and toeplitz masters appear only as public integer metadata.

## 2. Coverage, pairing and the four-cell table (recomputed from records)

Command: my walk over `per_block_paired_outcomes.json.blocks`, classifying each
pair with the frozen rule `both_exact / operational_only / oracle_only / neither`
and comparing to the persisted `cell`.

- 384/384 records; per stream 128/128/128 (`2026091470/71/72`); each stream's
  `block_index` set is exactly 0..127; every block has both an `operational` and
  an `oracle` arm. Persisted-cell mismatches: **0**.
- Recomputed cells overall: **both_exact 233, oracle_only 144, operational_only 0,
  neither 7** (sum 384, disjoint by construction of the classifier, and equal to
  the persisted cells).
- Per stream: 1470 = 83/43/0/2, 1471 = 72/55/0/1, 1472 = 78/46/0/4.
- Outcome contingency (op, oracle): `(exact, exact) 233`, `(verify_failed, exact)
  144`, `(verify_failed, verify_failed) 7` — no other combination.
- Structural argument for `operational_only == 0`, confirmed in code and in the
  records: `two_layer.py:677` packs `op_label_hat = op_low_hat + 32*op_high_hat`
  and `:631` packs `labels_true = low + 32*high`; the packing is unique over
  GF32 x GF32, so `op_label_match` (a precondition of `op_outcome == "exact"`,
  `:699-704`) implies `op_high_hat == high_true`. Then `op_p2_probs` (`:666`,
  Bob + candidate) is bitwise the same gather as `or_p2_probs` (`:738`, Bob +
  truth) and both L2 SC calls receive identical arguments (`:675` / `:751`), so
  the oracle arm is exact whenever the operational arm is. Records agree:
  all 233 op-exact blocks are oracle-exact (`all oracle-exact: True`), and
  operational-only is 0.

## 3. Marginals (recomputed from records)

- operational outcomes: exact 233, verify_failed 151, undetected 0,
  decode_failed 0, resource_abort 0 (sum 384). Exact rate 233/384 = 0.606770833.
- oracle outcomes: exact 377, verify_failed 7, undetected 0, decode_failed 0,
  resource_abort 0 (sum 384). Exact rate 377/384 = 0.981770833.
- Folding check: `exact == (outcome == "exact")` for every arm in both arms;
  every exact arm has `tag_pass == True and label_match == True`; every
  `verify_failed` arm has `tag_pass == False`; no `undetected` arm exists (and
  the code maps `undetected` only to "tag pass and not exact", `:704`). No
  category is folded into exact; the four zero-semantics categories
  (undetected/nonfinite/decode_failed/resource_abort) are all 0 and remain 0.
- Every value equals the persisted `aggregate_summary.json.marginals`
  (operational_exact 233, oracle_exact 377, gap 144) and `report.md`.

## 4. Discriminator (independent root and rule)

- X recomputed from the per-block cells: **144** (persisted X = 144).
- My own independent implementation: direct product-sum tail
  `sum_{j=X}^{384} math.comb(384,j) * L**j * (1-L)**(384-j)` (exact integer
  binomials, no log space) with 200-step monotone bisection:
  - root **0.33388427364277450** (>= 12 digits: 0.33388427364277 to 14 digits);
  - residual at my root: `4.3021142204224816e-16` (tail = 0.04999999999999957);
  - persisted `lower_bound` = 0.3338842736427746; |mine - persisted| =
    `1.1102230246251565e-16` (1 ulp); tail at the persisted value =
    0.05000000000000006, |residual| = 5.55e-17.
  - monotonicity sanity: tail(0.30) = 0.00098630972695325789 < 0.05 <
    tail(0.35) = 0.1650485810228807; the frozen edge cases are implemented
    (`X=0 -> 0.0`, `X=384 -> 0.05**(1/384)`, covered by focused tests).
  - threshold crossing check: first X with L > 0.30 is X=131
    (L=0.30106362808316556); X=144 is deep inside the pass region.
- Frozen discriminator conditions: oracle_exact 377 >= 365 (True);
  operational_only 0 == 0 (True); L = 0.3338842736427746 > 0.30 (True).
- Label rule: integrity pass + discriminator pass + 384-pair shape ->
  `HARD_L1_CONDITIONING_PENALTY_CANDIDATE`; persisted label is exactly that.
  A 13-vs-14-file test-count discrepancy does not affect this.

## 5. Integrity gates — recomputed, not copied

All ten recomputed from the per-block records, the independent table rebuild and
the accounting; every one is True and equals the persisted boolean and the
report row (report rows in frozen gate order: verified):

| gate | my recomputation (raw basis) |
|---|---|
| pairing_coverage_complete | 384 records; 128/128/128; indices 0..127; both arms per block -> True |
| p2_maxdiff_at_least_0p30 | independent rebuild: 0.34875000000000267 >= 0.30 -> True |
| provenance_candidate_oracle_complete | op L2 CANDIDATE_CONDITIONED 384/384, oracle L2 ORACLE_CONDITIONED 384/384; op L1 PRIOR_ONLY 384/384 -> True |
| operational_truth_leak_zero | op violations 0 (oracle violations 0 too) -> True |
| undetected_zero | outcomes `undetected`: 0 of 768 arm records -> True |
| nonfinite_zero | `nonfinite`: 0 of 768 -> True |
| resource_abort_zero | outcomes `resource_abort`: 0 of 768; `resource_stop_fired=false` -> True |
| cells_disjoint_exhaustive | 233+144+0+7 = 384; persisted cell == reclassified cell for all 384 -> True |
| disclosures_exact_and_transcript_recount_zero | 768/768 fully invoked arms have key_dependent_bits = 5*(45+140)+64 = 989; every tag_invoked arm public_control_bits = 2623; totals 759552 / 2014464 / 768 tags; events l1 768 + l2 768 + tag 768 = 2304; my recount from records equals the persisted incremental, recount, by_arm and aggregate transcript; mismatch_count 0, mismatches [] -> True |
| attempt_accounting_at_frozen_point | plan/aggregate: allowed 1, before 0, by_this_run 1, retries 0, planned 384, consumption point "first gate L1 SC call (stream 0, block 0)"; block 0 shows L1 executed in the operational arm -> True |

Supporting raw numbers: independent decoder-free `[Alice,Bob]` table rebuild gives
column-sum max deviation `3.774758283725532e-15` (persisted identical, limit
1e-12); derived `P2` cross-u1 maxdiff `0.34875000000000267` bit-identical to the
persisted value; closed form `0.36*31/32 = 0.34875` (diff 2.66e-15); profile mean
`0.19999999999999998`; D1 45 unique sorted in range, D2 140 unique sorted in range.
`report.md` lists all ten gates `True` in frozen order. `failing_integrity_gates`
= [] and `integrity_all_pass` = true (verified independently, not trusted).

## 6. Truth isolation (code + records)

- Operational metric/decoder path: `two_layer.py:640` P1 built from Bob only
  (`PRIOR_ONLY`); `:655` L1 SC call with D1/disclosed U1 values; `:666` P2
  gathered from Bob + **candidate** `op_high_hat` (`CANDIDATE_CONDITIONED`);
  `:675` L2 SC call with D2/disclosed U2 values. No Alice truth or oracle value
  is an input to either metric or decoder call.
- Oracle arm (`:738`, `:751`) conditions on the true high layer and is labelled
  `ORACLE_CONDITIONED`; records show exactly that 384/384.
- Truth touchpoints are only the frozen-allowed ones
  (`frozen_plan.json.provenance_rules.truth_allowed_only_in = ["oracle arm",
  "disclosed-U map", "scoring"]`): the disclosed U maps, the `label_match`
  scoring comparison, and the verification tag's true counterpart used for the
  pass/fail comparison (`:679`/`:755`). The operational tag itself is generated
  from `op_label_hat` only; the true tag never feeds the operational tag
  generation.
- Aliasing sentinel: `two_layer.py:808-819` snapshots the protected metric and
  decision set, mutates every truth buffer in place (high, low, u1_true, u2_true,
  labels_true) and re-checks bitwise equality; both records show
  `truth_leak_violation=false`. The focused suite proves the gate is live: with
  `_truth_isolation_sentinel` patched to False, the run reports
  `operational_truth_leak_zero=False` and `BLOCKED` (test lines 301-308), and the
  p2-floor refusal test proves no decoder call can occur below the floor.

## 7. Bounded wording (full `report.md` read, 44 lines)

`report.md` states the point (q=32, N=256, epsilon1=0.05, profile strong, k1=45,
k2=140, seeds/masters, 384 planned pairs), p2_maxdiff + floor, wall/RSS, the
four-cell table, X and L, all ten gates, the three discriminator booleans and the
label, and closes with the exact frozen scope sentence: "synthetic single-point
N=256 hard-conditioning penalty signal only; not real-data FER, efficiency,
qualification or promotion; operational-arm numbers are interface diagnostics."
The words FER/efficiency/qualification/promotion/real-data occur only inside that
negation; key rate, secret key, throughput and security have zero occurrences.
The same `claim_scope` string is persisted in `frozen_plan.json` and
`aggregate_summary.json`. No performance, FER, leakage-efficiency, key-rate,
qualification or promotion claim is made anywhere; the operational-arm exact
count/rate are presented as interface diagnostics only.

## 8. Implementation state — tests (pinned interpreter, fresh /tmp basetemps)

- Focused P5 suite (`comparison_bench/tests/test_nbpolar_penalty_gate.py`):
  **9 passed** in 6.56 s (`-q -p no:cacheprovider`).
- Full NB-Polar suite: the 14 `test_nbpolar_*.py` files collect **201 tests** and
  **201 passed** in 103.49 s (same flags). Expected totals 9 new + 192
  predecessors = 201 are met; the packet prompt's "13 files" is one lower than
  the actual 14-file glob (informational only).
- Only warning observed is the pre-existing `PytestConfigWarning: Unknown config
  option: cache_dir` (benign, unrelated to the change).

## 9. Scope and provenance

- `git status --porcelain` = 55 entries, same count/scope as the R1 pre-execute
  review; no staging (`git diff --cached` empty); no commit; HEAD
  `ab173f2a5e17336383a897b941080b731ba3dd9e` unchanged; `git reflog` holds only
  the clone entry.
- Files modified since packet start (17:04) are exactly the P5 packet (docs,
  STATUS/TASK/AUTHORIZATION/freeze/reviews), the P5 implementation
  (`penalty_gate.py` 17:14:36, `test_nbpolar_penalty_gate.py` 17:15:52), the P5
  OpenSpec/planning docs (last 17:20:05), and the five gate files (17:51:56).
  Bytecode caches for those two modules date 17:21:32 (pre-run cache, not
  rewritten by the run).
- Accepted modules untouched by content/mtime: `two_layer.py` 12:59:11,
  `prior.py`/`sc.py`/`transform.py`/`construction.py` 2026-09-12 03:38,
  `protocol.py` 02:13:04 — all before the P5 packet window.
- Old evidence roots untouched: P3 packet newest 01:33, P4 packet newest 15:40,
  X02 probe results 16:53, `comparison_bench/outputs_comparison/` newest
  2026-09-12 03:38; `results/` does not exist in this checkout. No writes to
  results/outputs_comparison; sibling checkouts were not accessed for content
  (sibling writes therefore not independently verified and out of scope).
- Informational: `NBPOLAR-X01-PROBE-TIER-BOOTSTRAP/STATUS.yaml` and five
  working docs (`AGENT_PROJECT_MEMORY.md`, `CURRENT_TASK.md`,
  `docs/decision-log.md`, `docs/nbpolar/DOCUMENT_INDEX.md`,
  `openspec/.../phase4-p0/tasks.md`) were last modified 17:06:20-17:20:05, i.e.
  the packet setup window **before** the 17:43 freeze and the 17:51 run, under
  `documentation_authorized: true`; they were already part of the R1 dirty
  scope. No old evidence root was modified during or after the gate run.
- Single-generation gate root verified above. Attempt/seed state: the records
  persist `attempts_consumed_by_this_run=1`, `retries=0`, streams
  2026091470..1472 (128 blocks each) and public masters 2026101470..1472
  (`= seed + 10000`); 29 refused seeds; the frozen seeds are not refused. The
  single attempt is consumed by this run; `STATUS.yaml` still reads
  `attempts_used: 0` because the runner deliberately does not update the ledger
  (freeze §10) — the operator return/main thread owns that bookkeeping.

## 10. Deliberate non-actions

- Frozen 384-pair command not rerun; no decoder call made by this review.
- No file other than this `PRE_RESULT_REVIEW.md` was written.
- No commit, push, staging, or old-root modification.

FAIL would require precise rework items; there are none. The single blocking
question — does the persisted evidence support the claimed
`HARD_L1_CONDITIONING_PENALTY_CANDIDATE` at the frozen semantics? — is answered
yes by independent recomputation of every number, every gate, and the
discriminator root.
