# DELTA.md — P20S-R1 single gate-expression fix (delta-successor, AGENTS.md §10.4 fast path)

- Packet: `NBPOLAR-PHASE4-P20S-R1-GATE-FIX` (delta-successor of P20S Stage-B).
- Predecessor: `NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED`
  (P20S Stage-B executed once, exit 0, 15/15 files present, 35/36 gates TRUE,
  `BLOCKED(blocks_exact_with_declared_remainder)` on a frozen code defect;
  see predecessor `OPERATOR_RETURN.md` §4 for the read-only root-cause analysis).
- Branch: `codex/nbpolar-phase0`. Workdir: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- Status: PREPARE ONLY. Stage-B execution is NOT authorized by this document
  (requires the independent freeze review + pasted execution authorization first).
- Date: 2026-09-20.

## 1. Single changed item (a) — the ONLY code delta

- File: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_mechanism_probe_2m.py`.
- Function: `_integrity_gates` (the `blocks_exact_with_declared_remainder`
  gate conjunct, formerly line 2548).
- Before (defective — `list()` applied to the scalar-int frame bound):
  `list(formation["remainder"]["frame_start"]) == [int(FROZEN_REMAINDER_FRAME_RANGE[0])]`
  `formation["remainder"]["frame_start"]` is stored as scalar int `3595`
  (`form_merged_blocks`, `"frame_start": int(rem_first)`), so `list(3595)`
  raises `TypeError: 'int' object is not iterable`, caught by the gate's
  `except (KeyError, TypeError, ValueError)` → `blocks_ok = False`.
- After (fixed — scalar-int comparison, no `list()` on the scalar bound):
  `int(formation["remainder"]["frame_start"]) == int(FROZEN_REMAINDER_FRAME_RANGE[0])`
  Scalar bounds compare via `int()` (accepts `int` / numpy-integer scalars
  uniformly); range-style lists elsewhere in the same gate
  (`block_segments`, `val_stub_frames`, `hold_remainder_frames`) keep their
  `list() == list()` comparison — each kind compared by its appropriate form,
  uniformly across the gate. No other code touched: no other runner logic,
  no accepted module, no `FROZEN_OUT_ROOT` / `FROZEN_COMMAND` constant edit
  (the R1 `--out-dir` is passed explicitly on the command line, §7).

## 2. Everything else INHERITED unchanged from P20S (b)

Identical freeze — every scientific input replays the P20S freeze byte-for-byte:

- Population/merge: merged 2M DEV = VAL-remainder tail `2827..2915`
  (89 frames) FOLLOWED BY HOLD-remainder head `3556..3594` (39 frames),
  VAL-segment-then-HOLD-segment, ONE 128-frame block at N=32768
  (32768 pairs); HOLD tail `3595..3644` (50 frames / 12800 pairs) counted
  never decoded; 1.5M VAL stub `2172..2212` (41) + 1.5M HOLD remainder
  `2725..2766` (42) counted never decoded, never contacted beyond counting;
  build frames 2M TRAIN `0..2186` (S2-ii disjointness declared with frame sets).
- Reuse digests (P20O frozen 2M files, read-only): prior
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`
  + H `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477`;
  orders-A `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`;
  alt `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`
  (alpha 1.0, floor 1e-15, exact key sets, `p1`-equality within 1e-12).
- Spike formula: frozen DECIDED 2026-09-20 F-median8
  (`F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8`: score[i] = h[i] −
  median(h over the R=8 clipped natural neighborhood of i); first K2=6746
  by descending score; ascending tie-break; deterministic; zero sampling /
  genie / protected reads; inputs worktree `raw_prior_2m.npz` arrays only).
- Spike-order digest: `139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864`
  (`new_spike_order_2m.json` under the P20S packet dir, reused read-only).
- K literals: `(K_total,K1,K2) = (7080,334,6746)` replayed (never recomputed,
  never recarried from 1.5M, never from alt-H); budget literal
  `1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536] = 7080`.
- Arms A/B/O: `A_anchor_frozen_order` (operational, frozen order, K1/K2) /
  `B_spike_local_order` (operational, spike order, SAME K — order SET is the
  only delta) / `O_true_l1_oracle` (diagnostic control, carried K2, never
  operational); greedy SC only; alt-α1 tables on all arms.
- Caps: key `5*(K1+K2)+64` per operational block (A/B 35464, O 33794),
  planned key total 104722 bits; public `10*32768+63 = 327743` bits/tag,
  planned public total 983229 bits.
- Budgets: 5 SC calls (A 2 / B 2 / O 1) + 3 tags + 3 records; genie 0+0
  (zero sampling at every stage).
- IR-1..IR-4 + IR-5: mandatory IR-1 (64-bin) / IR-2 (rank percentile) /
  IR-3 (EXACTLY two thresholds 1.0x/2.0x record prefix-mean) / IR-4 (top-16)
  ALL FROZEN PRESENT (P20Q-identical caps/formulas, recording-only,
  post-decode, truth-isolation boundary) + IR-5 UNCAPPED full-block binary
  series (`ir5full-v1`: 32768 float32-LE hazards + 32768 u8 in-prefix +
  32768 u8 in-U per record; binary `.bin` + JSON manifest ONLY).
- Tag master: `2026092360`, prefix
  `nbpolar-p20s-mechanism-probe-2m-seed` (new P20S domain).
- Envelope: external `timeout 1200` s, virtual `ulimit -v 2097152` KiB,
  `RSS_LIMIT_BYTES = 2 GiB`, single-thread exports
  (`OPENBLAS/OMP/MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2`).
- Gate family (a)→(g): cross-file 2M identity → intra-file dual-segment
  containment → consumed-1M / consumed-1.5M / consumed-2M (+S2-ii) exclusions
  → reuse-prior/alt/frozen-order/K-literal/spike-derivation-program pins →
  merged-frame-set-identity + order-position-identity + tag-domain.
- Judgment form: geometry/coverage quantities ONLY. NO recovery-rate reading,
  no threshold votes, no FER/reliability/efficiency language, no H2 verdict
  in-packet (`undetected` isolated, never success; oracle never operational).

## 3. Rationale — recorded identical-freeze repeat, never tuning (c)

- P20S Stage-B ran ONCE (exit 0; all 15 scientific artifacts produced and
  inventoried in predecessor `OPERATOR_RETURN.md` §2). Its integrity
  conjunction came out BLOCKED on exactly ONE gate expression — the §1
  scalar-vs-list representation defect — while the operator verified every
  underlying quantity TRUE from the frozen artifacts (segments
  `2827..2915` + `3556..3594` = 128 frames / 32768 pairs; remainder
  `3595..3644` = 50 frames / 12800 pairs never decoded; stubs declared;
  35/36 gates TRUE).
- The P20S attempt is therefore CONSUMED (attempts 1/1 SPENT; merged-DEV
  1/1 read). This successor re-executes the IDENTICAL freeze purely to obtain
  a correct label — no scientific input changes, no new information exists or
  is sought (the population is consumed; no unconsumed block remains for any
  adjacent question). Under the AGENTS.md §10.4 delta-successor rule this is
  a recorded identical-freeze repeat (an execution-error-class repeat of a
  frozen predicate defect), never tuning: same population, same files, same
  digests, same K, same arms, same caps, same budgets, same formula — the §1
  one-expression predicate fix is the entire delta.

## 4. Determinism requirement (d)

- The §1 fix touches ONLY the label predicate (`_integrity_gates`); it cannot
  alter decoding, recording, or serialization. Hence the R1 per-record outputs
  MUST equal P20S's byte-for-byte.
- Freeze-review and Pre-RESULT acceptance MUST digest-compare, at minimum:
  (i) every record of `per_block_arm_outcomes.jsonl` (R1 vs P20S, all 3
  records, exact bytes per record); (ii) all nine IR-5 `.bin` files
  (`A/B/O × hazard_bits_f32le / inprefix_u8 / inu_u8`, sha256 per file).
- ANY byte difference in those comparisons is a STOP-level non-determinism
  finding: halt, retain both roots immutable, report to the main thread. It is
  NOT to be repaired, tuned, or re-run inside this packet.

## 5. Output roots (e)

- New R1 root:
  `.workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m/`
  (exactly the fifteen frozen files; must be ABSENT at freeze review and at
  Pre-EXECUTE).
- The P20S root
  `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m/`
  is NEVER overwritten or modified by this packet (read-only reference for
  the §4 digest comparison).

## 6. Authorization source (f)

- Source: user standing pre-authorization 2026-09-20, quoted verbatim:
  "我预授权给你向下自主探索与推进的权力，允许你往下推进至少十轮，需要抉择的地方都自动选择recommend项，需要授权的地方都标注我已预授权"
  (recorded in predecessor `STAGE_A_AUTHORIZATION_RECORD.md`).
- Scope of the standing authorization as applied to this delta packet:
  this §1 single-expression delta + its freeze review + ONE R1 execution of
  the §7 frozen command on the §5 new root ONLY.
- Explicitly NOT authorized by that source for this packet: any rerun beyond
  the single R1 attempt; any tuning (prior/alt/construction/K/order/formula/
  IR-threshold/population change); any H2 verdict; any recovery-rate reading;
  any commit or push; any self-acceptance by the operator.

## 7. R1 frozen Stage-B command (new `--out-dir`; all other flags identical to P20S)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_mechanism_probe_2m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz --prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587 --alt-prior .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/alt_l2_tables_2m.npz --alt-digest 98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5 --source 2M --floor 1e-15 --n 32768 --k1 334 --k2 6746 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet --dev-frames-val 2827 2915 --dev-frames-hold 3556 3594 --block-frames 128 --remainder-frames 3595 3644 --tag-master 2026092360 --chunk-rows 512 --tag-bits 64 --order-file .workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_orders_2m.json --order-digest b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906 --spike-order-file .workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/new_spike_order_2m.json --spike-order-digest 139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864 --spike-formula F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m
```

- The module's `FROZEN_COMMAND` constant itself is NOT edited (still renders
  the P20S `--out-dir` from the unchanged `FROZEN_OUT_ROOT`); the R1 command
  above is that frozen string with ONLY `--out-dir` pointed at the §5 new
  root. NOT EXECUTED in this PREPARE task.

## 8. Review gates for this packet

- Freeze review (independent): adjudicate §1 (single-expression scope, no
  other code touched) + §§2–5 (identical freeze, determinism rule, new-root
  absence, P20S-root intact) + §6 (authorization scope) before any execution.
- On FAIL: `revise-required`; no execution.
- After PASS + pasted execution authorization: single R1 attempt, then
  independent Pre-RESULT review (thresholds, leakage decomposition,
  `undetected` isolation, per-source breakdown, disclosure accounting, §4
  digest equality) before any result publication. Operator never self-accepts.

## Main-thread adjudication (2026-09-20)

- Binding ruling (main thread): the R1-vs-P20S
  `per_block_arm_outcomes.jsonl` byte diff is TELEMETRY-ONLY and NON-BLOCKING.
- Evidence: the ONLY differing keys across all 3 records are `wall_s` and
  `resources.{wall_s, vm_peak_kb, vm_size_kb, rss_bytes_hwm}`; all 9 IR-5
  `.bin` files are byte-identical; every scientific/IR/gate/order/tag/
  order-digest field is identical across all 3 records
  (see `OPERATOR_RETURN.md` §4 for the per-file digests and key-level diff).
- Reason: R1 is an identical-freeze re-execution of consumed data under the
  AGENTS.md §10.4 delta-successor rule, so byte-equality cannot hold for
  wall-clock/resource telemetry by construction.
- Determinism requirement (§4) is satisfied at the level of all scientific
  fields; the telemetry-only diff does not constitute non-determinism.
- No third execution is authorized or needed (P20S block consumed, R1 attempt
  spent). Both roots retained immutable: the P20S root as the BLOCKED-label
  provenance record, the R1 root as the accepted-descriptive record.
