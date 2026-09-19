# P20G Stage-B Pre-RESULT review (independent, read-only)

- Packet: `NBPOLAR-PHASE4-P20G-1P5M-183806` (Tier-Y). Reviewer: independent `reviewer-go` thread
  (not the Stage-B operator). Read-only over evidence-root JSON/MD + FREEZE + RETURN + STATUS;
  no decoder rerun; no protected NPZ/parquet content opened; no commit/push.
- Stage-B outcome under review: `BLOCKED(target_population_contract)` — verbatim FREEZE §10
  single execution, fail-closed refusal inside budget (not a resource abort). Attempt 1/1 spent;
  no rerun performed or authorized.

## Verdict: PRE_RESULT_PASS (accept BLOCKED(target_population_contract) as terminal)

1. Fail-closed correctness PASS — gate order predecessor → split_manifest → dev_block_range
   (double: cross-file first, intra-file VAL-first) → `target_population_contract` (4th gate)
   matches FREEZE §9; attempt consumed at first NPZ open, shape (1024,1024) checked, literals
   compared, then raise before any DEV parquet open; `per_block_arm_outcomes.jsonl` 0 bytes /
   0 records; aggregate/report in RUNNING stub state; SC 0/15, tags 0/9; 3 PASS + 1 FAIL + 16
   unevaluated = 20 gates, consistent with freeze.
2. BLOCKED-label applicability PASS — 20 gates not all true, so COMPLETE does not apply
   (FREEZE §7 / packet §7: COMPLETE iff all gates hold); `BLOCKED(target_population_contract)`
   named after the earliest failing gate, the only lawful label; zero COMPLETE verdicts for
   this packet; no FER/promotion language mixed in.
3. Scientific meaning fidelity PASS — loaded `--source 1p5M` counts array (1024², floor 1e-15)
   vs carried-over 1M literals H1 0.02428054681872374 / H2 0.7767572780789994 / TOTAL
   0.8010378248977232, all three mismatched → direct cross-session carry-over of the 1M
   Model-F prior refused; any change to preconditions/thresholds/prior inside this packet would
   be tuning and was correctly refused; no "1.5M channel is bad" or superiority claims;
   Model-F cross-session applicability recorded as direct-carry-over refused, per-session
   calibration an open question.
4. Accounting honesty PASS — planned key 317646 (3·34119 + 3·39239 + 3·32524; operational
   220074 + oracle 97572) / public 2949687 (9·327743) / B1 Δ+5120 vs actual SC 0/15, tags 0/9,
   records 0/9, key/public 0/0; recount "mismatch 0 over zero transcribed events" explicitly
   vacuous, verdict attributed to the earlier gate, not accounting; attempt 0→1 + no-repeat
   declared; FROZEN_COMMAND consistency pre-verified True.
5. Consumption & isolation PASS — attempt 1/1 SPENT at first protected content open
   (matches code ATTEMPT_CONSUMPTION_POINT); NPZ open 1 → STATUS train 1/1, no reopen/rerun;
   DEV parquet content opens 0 (stat-size pre-check only, never entered `load_pairs_table`);
   HOLD reads 0; 2M pristine procedurally (no 2M path in argv; sole 2M string is the runner's
   refusal literal; operator honestly noted non-verification-by-stat per packet §4); remainder
   384..1659 never decoded.
6. Artifact integrity PASS — `independent_session/` exactly five files
   (`frozen_plan` 7324B / identity 2874B / jsonl 0B / aggregate 26B RUNNING / report 46B
   RUNNING), matching FREEZE §9 inventory, RUNNING stub state consistent with fail-closed;
   OPERATOR_RETURN.md §§1–8 complete; STATUS fields consistent
   (`STAGE_B_EXECUTED_AWAITING_PRE_RESULT`, `BLOCKED_target_population_contract`, attempt
   1/1, train 1/1, hold 0/1); `src/experiments/tools/results` zero diff.
7. Language review PASS — zero recovery counts (only "b1_restored not computable / denominator
   0" negatives), zero FER/promotion/efficiency claims, B2 never operational, `undetected` 0
   and isolated; branch decision explicitly deferred to main-thread planning.

## Branch recommendation (reviewer's, adopted)

Accept BLOCKED as terminal; route planner to design a new packet with re-frozen
target-population contract for per-session channel statistics (1.5M DEV 0..383 unconsumed and
available; 2M stays pristine). No out-of-packet retune/rerun. A delta-successor fast path is
allowed only if main thread rules the BLOCKED stemmed from a frozen-literal/contract error
rather than a scientific refusal — otherwise any repeat is forbidden.
