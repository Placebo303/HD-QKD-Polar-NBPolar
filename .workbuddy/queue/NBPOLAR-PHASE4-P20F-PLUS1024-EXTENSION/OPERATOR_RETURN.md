# P20F Stage-B OPERATOR_RETURN (single authorized execution, descriptive only)

- Task: `NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION` (Tier-Y), branch `codex/nbpolar-phase0`.
- Authorization chain: user long-term Stage-B authorization (covering subsequent rounds
  incl. P20F); independent Stage-A R1–R8 PASS + Pre-EXECUTE
  `PRE_EXECUTE_PASS_CONDITIONAL` (standing auth covers §4) in `PRE_EXECUTE_REVIEW.md`;
  STATUS protected/decoder authorized true.
- Five iron rules observed: verbatim command / single attempt / no tuning /
  descriptive-only / stop-on-anomaly. No repeat, no rerun, no second factor, no SCL,
  no `results/` or `outputs_comparison/` write, no commit/push, no self-acceptance.

## 1. Command (verbatim FREEZE §10, FROZEN_COMMAND consistency True)

Executed from `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar` with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2`,
`ulimit -v 2097152`, `timeout 600`, 16 flags incl. `--dev-frames 768 1151`,
`--remainder-frames 1152 1199`, `--tag-master 2026092200`, digest
`055c90…c3faea1b`. Pre-exec: output root `plus1024_extension/` absent (stat
confirmed No such file); module `FROZEN_COMMAND` printed byte-identical to FREEZE
§10 (`FROZEN_COMMAND==FREEZE_S10: True`) before run.

## 2. Execution result

- Start 2026-09-18T13:09:43Z, end 2026-09-18T13:11:18Z; exit code 0; wall 92.957429 s
  (< 600 s); peak RSS 579555328 B (~552.7 MiB, < 2 GiB); VM peak 1822584 KB
  (~1.74 GiB, < 2 GiB virtual limit); single thread; `resource_stop_fired: false`.
- Stdout: 9 records, `integrity_all_pass: true`, label
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE`.

## 3. Evidence root (exactly five files, created pre-open, checkpointed per record)

`.workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/plus1024_extension/`:
`frozen_plan.json`, `input_and_predecessor_identity.json`,
`per_block_arm_outcomes.jsonl` (9 records), `aggregate_summary.json`, `report.md`.
Scalar-only; no counts/symbols/truth/orders/seeds persisted.

## 4. Per-arm exact counts + endpoint rows (descriptive, no threshold)

| arm | exact | key bits | public bits |
|---|---|---|---|
| B0_sc_base (operational) | 3/3 | 102357 = 3×34119 | 983229 = 3×327743 |
| B1_L2plus (operational, ΔK2=+1024, K2 6492→7516, +5120 key bits/block) | 3/3 | 117717 = 3×39239 | 983229 |
| B2_true_l1_diagnostic (ORACLE, deployable=false, excluded) | 3/3 | 97572 = 3×32524 | 983229 |

Overall: exact 9 / verify_failed 0 / undetected 0 / decode_failed 0 / nonfinite 0 /
abort 0. Operational exact 6/6.

Endpoint table (all tag-verified exact; P20A four-endpoint separation holds):

| block (frames) | B0 l1/hard-L2/pair | B1 l1/hard-L2/pair (dK2=1024, frozen-order-prefix-extension) | B2 oracle-L2 | raw SER |
|---|---|---|---|---|
| 0 (768..895) | T/T/T exact | T/T/T exact, restored=false | exact (truth-conditioned) | 0.239776611328125 |
| 1 (896..1023) | T/T/T exact | T/T/T exact, restored=false | exact (truth-conditioned) | 0.236236572265625 |
| 2 (1024..1151) | T/T/T exact | T/T/T exact, restored=false | exact (truth-conditioned) | 0.239501953125 |

- `b1_restored_count` analogue = 0/3: B0 never failed on the new blocks, so no
  P20C-style recovery event occurred; B1 maintained exact everywhere B0 was exact
  ("maintain" pattern, descriptive only — not a pass/fail verdict, no FER/superiority claim).
- `undetected` isolated at 0, never merged into success. B2 never operational.

## 5. Accounting identities (all hold)

- SC calls: 15 = 3 blocks × (2+2+1); derived per-record recomputation matches
  counter (`sc_calls_exact: true`). Tags: 9 = 3×3, derived match (`tags_exact: true`).
- Key disclosure: 317646 = 3×34119 + 3×39239 + 3×32524 (operational 220074 +
  oracle 97572); B1−base = +5120 = 5×1024 per block. Public: 2949687 = 9×327743.
  Independent recount mismatch 0 (`disclosure_recount_exact: true`).
- Ratios vs raw (327680 bits/block): base 0.10412292 (~10.41%), B1 0.11974792
  (~11.97%) — far below raw; CE-normalized ratios descriptive only, not efficiency.
- Integrity gates 20/20 true, `failing_integrity_gates: []`, incl. quadruple overlap
  pre-check (consumed P20C 0..383 first → consumed P20E 384..767 → consumed
  1200..1599 → closed 1600..1983), blocks exact with declared remainder (48 frames /
  12288 pairs, 1152..1199, counted never decoded), oracle isolation, truth isolation,
  one-open-per-input, stat unchanged, no unregistered access, resource limits met.

## 6. Consumption (one-shot semantics)

- First protected content open consumed the single attempt: counts NPZ open 1/1 +
  DEV TRAIN pairs open 1/1, `reopen_attempted: false`, `retries: 0`. No HOLD read.
- STATUS: `train_artifact_reads_used: 1`, `hold_data_reads_used: 0`,
  `attempts_used: 1/1`, state `STAGE_B_EXECUTED_AWAITING_PRE_RESULT`, result
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE`. Attempt 1/1
  consumed — any repeat is forbidden.

## 7. Not run / remaining gates

- Independent Pre-RESULT review (`PRE_RESULT_REVIEW.md`) and main-thread acceptance
  (`MAIN_THREAD_ACCEPTANCE.md`) — pending, owned outside this operator return.
- Positive/negative branch decision (§16: independent-session round vs P20D vs
  minimality probe vs efficiency) — deferred to main-thread planning after
  acceptance; this packet renders no verdict.
- No commit/push performed.

## 8. Blockers

None. No anomaly, no BLOCKED gate, no resource abort, no command mismatch.
