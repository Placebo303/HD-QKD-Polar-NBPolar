# OPERATOR_RETURN — NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE

Final post-execution operator return. Operator session 2026-09-13 (WSL). The
single authorized three-arm paired 300-block development gate was executed once
(exit 0) and two independent reviews are recorded (Pre-EXECUTE PASS, Pre-RESULT
PASS). Returned label:
**`DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE`**.

Claim scope: synthetic paired development signal only. This is a CANDIDATE, not
an acceptance. It is **not** real-data FER, leakage efficiency, key rate,
qualification or promotion evidence. No commit or push. `attempts_used: 1`.

## 1. Mission

Test whether advancing after a **non-final** impossible-disclosure rejection
recovers the strict-stop losses while retaining disclosure savings. The accepted
Phase 6 point, order, `K=(29,33,37,41,45)`, decoder, tags, thresholds and
accounting are unchanged; only the rejection handling differs. Three arms run on
the identical 300 per-block arrays: the static K=45 comparator, the accepted
Phase 6 strict-stop incremental schedule, and the Phase 6-R1
decode-reject-advance schedule.

## 2. R1 delta semantics (the only semantic change)

At a non-final level (K=29/33/37/41, levels 0..3) an
`ImpossibleDisclosedValueError` becomes `decode_rejected_continue`:

1. the intermediate rejection is recorded (`rejected_levels`);
2. no candidate is created and no tag is invoked at that level;
3. exactly one public feedback request is counted;
4. the next fixed increment is disclosed and SC restarts from scratch on the
   **original** metric with no carried state, belief, partial sum or hard
   decision.

At the final level K=45 the same error stays terminal `decode_failed`. No other
exception may continue: `NumericNonfiniteError`, any other exception and
nonfinite marginals stay fail-closed terminal at every level. An intermediate
rejection is never success and never a final outcome bucket. The strict-stop
path is byte-pinned to Phase 6 and its consistency proof rejects any record
carrying a rejection.

## 3. Implementation summary

- modified `comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py`
  (R1 mode via a shared private impl + `run_incremental_r1_block`, mode-aware
  consistency checker and transcript emitter, `terminating_level`,
  `rescue_comparison`, three-arm block runner/gates/plan/report, `R1_*`
  constants/validator/budgets, CLI mode; Phase 6 default path unchanged)
- modified `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py`
  (`NBPolarIncrementalR1Method`; strict class output unchanged)
- modified `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py`
  (explicit R1 aliases only)
- new `comparison_bench/tests/test_nbpolar_incremental_r1.py` (17 R1 tests,
  R1-A01..A12 + refusals/adapter/schema/forbidden-marker scan)
- modified `openspec/changes/formal-ir-nbpolar-phase6-r1-decode-reject-advance/design.md`
  (Rev 1 frozen-conventions note only; no task box checked)
- queue docs (`STATUS.yaml`, `R1_FREEZE.md`, `R1_IMPLEMENTATION_NOTES.md`, this
  file)

Test evidence (pinned interpreter, fresh `/tmp` basetemps, `-q -p no:cacheprovider`):

```text
test_nbpolar_incremental_r1.py   -> 17 passed, 1 warning
all 11 test_nbpolar_*.py files   -> 170 passed, 1 warning
```

No Phase 5 code, frozen baseline, `results/`, `outputs_comparison/` or sibling
checkout was modified.

## 4. Frozen identity

| item | frozen value |
|---|---|
| run seed | `2026091350` (consumed at the first `sc_decode`, static arm block 0) |
| Toeplitz master | `2026091351` (public control; raw bits never persisted) |
| nested schedule | `K=(29,33,37,41,45)`; static comparator `K=45` |
| point | q=32, N=256, epsilon=0.05 |
| budgets | internal total 900 s; per-paired-block soft cap 15.0 s; external `timeout 1800`; `ulimit -v 2097152` (2 GiB) |
| output root | `.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/` |

Exact frozen command (executed once, exit 0):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.incremental --mode three-arm-paired-dev-gate --run-seed 2026091350 --blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate
```

## 5. Run result — three arms on 300 identical blocks

300/300 `paired_match` true. Outcomes are disjoint and exhaustive per arm.

| arm | exact | decode_failed | undetected | avg key-dependent bits/block | key total | tags | feedback | public control bits (seed / control) |
|---|---|---|---|---|---|---|---|---|
| static K=45 | 298 | 2 | 0 | 288.573333 | 86572 | 298 | 0 | 781654 / 781654 |
| strict-stop | 280 | 20 | 0 | 214.253333 | 64276 | 314 | 34 | 823622 / 823656 |
| R1 | 298 | 2 | 0 | 220.506667 | 66152 | 333 | 67 | 873459 / 873526 |

- R1 rejections: 32 across 20 blocks; rejected-level histogram `{0:20, 1:7, 2:3, 3:2}`; no final-level rejection.
- R1 vs strict-stop rescue identities: **rescued 18 / persisted 282 / regressed 0 / other 0** (partition exhaustive; no threshold uses these counts).
- Disclosure vs static: integer 5% rule `6615200 <= 8224340` true; saving fraction **0.235873031** (R1 avg 220.506667 vs static 288.573333 = 23.59% lower).
- Verification union bound total `5.1228552649940085e-17` over 945 tag invocations (298+314+333).
- Transcript mismatch counts static/strict/R1 = 0/0/0; truth-leak violations 0/0/0; nonfinite 0/0/0.
- One-sided 95% Wilson lower bound (exact recovery): static 0.9800565738801275; strict-stop 0.9055618244501542; R1 0.9800565738801275.
- Wall 16.595318 s; peak RSS 114622464 B; `resource_stop_fired` false.
- **18/18 frozen hard gates true**; only then is the candidate label emitted.
- Candidate label: **`DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE`**.

## 6. Output files (exactly five, scalar-only)

`.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/`:

| file | size |
|---|---|
| `aggregate_comparison.json` | 11041 B |
| `frozen_plan.json` | 8343 B |
| `per_block_three_arm_outcomes.json` | 806286 B |
| `report.md` | 2707 B |
| `transcript_accounting.json` | 2649 B |

No symbol vectors, labels, disclosed values, decoded keys or raw seed bits are
persisted.

## 7. Non-blocking notes and disposition

1. **Static-arm `terminating_k` records 29 (all 300 static records)** — metadata
   only; static `key_dependent_bits` and every gate use K=45, so no result-chain
   number is affected. **Carried.**
2. **STATUS.yaml stale after the run** (`attempts_used: 0`) — **fixed by this
   closeout**; now `attempts_used: 1`.
3. **report.md wording** does not literally state the strict-stop arm is an
   in-run recomputation — unambiguous from `frozen_plan.arms`/`mode` and the
   absence of any P6-root reference. **Carried wording note.**
4. **Inherited abort `paired_match` note** (Pre-EXECUTE finding 4) — unexecuted
   `resource_abort` records carry `paired_match: true`; moot here (0 aborts) and
   the coverage gate would catch an all-abort run. **No action for this packet.**

## 8. Attempt / seed accounting

- **Attempt 1/1 consumed** at the first scientific `sc_decode` call (static
  comparator arm, block 0). No rerun, no seed change, no tuning, no partial
  credit.
- Run seed `2026091350` consumed and persisted in the plan/aggregate.
- Toeplitz master `2026091351` is the public control identifier only (no raw
  bits persisted).
- The real output root was refused-if-present and is now the immutable
  evidence root.

## 9. Review verdicts

- **Pre-EXECUTE: PASS** (`PRE_EXECUTE_REVIEW.md`) — all ten required checks
  passed; the frozen command was authorized to run once; no blocking issues.
- **Pre-RESULT: PASS** (`PRE_RESULT_REVIEW.md`) — all 18 gates independently
  recomputed true, all accounting/pairing/Wilson/disclosure/recount checks
  reproduced exactly; the candidate label is warranted; no blocking issues.

## 10. Bounded scope and unrun stages

- Bounded to a synthetic paired development signal. No real-data FER, leakage
  efficiency, key rate, qualification or promotion claim.
- Unrun stages: **none** — implementation, synthetic qualification, profile,
  freeze, Pre-EXECUTE review, the single execution, and Pre-RESULT review are
  complete. Only **main-thread acceptance** remains.
- Not run/not touched: real data, Model-F artifacts, `results/`,
  `comparison_bench/outputs_comparison/`, sibling checkouts, SCL/CRC, Phase 7,
  the immutable Phase 5/P6 evidence roots, and any commit or push.
- The operator does not self-accept and does not check the R1 OpenSpec task
  boxes; acceptance is the main thread's decision.
