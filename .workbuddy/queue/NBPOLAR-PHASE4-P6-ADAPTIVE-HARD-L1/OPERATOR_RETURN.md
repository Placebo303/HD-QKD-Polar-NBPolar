# Operator return — NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1 (BLOCKED, pending main-thread disposition)

Status: `BLOCKED(d1_exactly_nested_and_d2_disclosed_once)`. This is **not** an
acceptance and **not** a repair. The single authorized attempt executed once
(exit 0); the persisted label is `BLOCKED`; the failure root is preserved and no
rerun/re-score/re-tuning is permitted in this packet. The operator reports
evidence only; the main thread owns disposition and scientific scope.

## 1. Mission

Implement and execute one paired synthetic Tier-Y development gate for the X05
frontier schedule `K1=[45,60,72,112]`, fixed `K2=140`, against the static
`K1=112` endpoint. Sole claim tested: at the frozen dependent-L2 point, adaptive
hard-L1 disclosure preserves the static endpoint's exact recovery while reducing
mean key-dependent disclosure by at least 15%.

## 2. Frozen point, schedule, streams, command, root

- Field/point: GF32 (q=32) polynomial 37, alpha 2, natural SC order, `N=256`;
  `epsilon1=0.05`; strong dependent profile `epsilon2(u1)=0.02+0.36*u1/31`.
- Disclosure sets: analytic worst-first nested D1 prefixes `[45,60,72,112]`;
  fixed D2 prefix `K2=140`, disclosed once per arm/block.
- Streams: five fresh streams `2026091550..2026091554` x 128 common blocks =
  640 paired blocks; public Toeplitz masters `stream+10000` =
  `2026101550..2026101554` (public control, domain-separated per arm/block/level).
- Budgets: address-space limit 2 GiB, wall timeout 3600 s, one attempt consumed
  at the first scientific SC call.
- Frozen command (three-line WSL, run once):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.adaptive_l1 --n 256 --epsilon1 0.05 --profile strong --k1-levels 45 60 72 112 --k2 140 --seeds 2026091550 2026091551 2026091552 2026091553 2026091554 --blocks-per-seed 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate
```

- Output root: `.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
  (absent before execution; contains exactly the five files listed in §7).

## 3. Run results (from the five persisted artifacts)

Run completed exit 0; wall `105.941485 s` (<= 3600 s); peak RSS `394,567,680 B`
(<= 2,147,483,648 B); `resource_stop_fired=false`, `retries=0`.

- Integrity gates: **11/12 true**; sole failing
  `d1_exactly_nested_and_d2_disclosed_once = false` (diagnosis in §5).
- Scientific gates: **4/4 true**.

Outcomes (both arms; mutually exclusive/exhaustive, sum 640; `undetected` never
merged with exact):

| arm | exact | verify_failed | decode_failed | undetected | resource_abort |
|---|---|---|---|---|---|
| static | 632 | 8 | 0 | 0 | 0 |
| adaptive | 632 | 8 | 0 | 0 | 0 |

Paired cells: `both_exact=632`, `adaptive_only=0`, `static_only=0`,
`neither=8`. The 8 `neither` blocks are the same blocks in both arms, all
`verify_failed` at stage 4; per-stream `neither` = 1/1/4/1/1.

Adaptive termination histogram (stage): `{1:403, 2:185, 3:39, 4:13}`;
termination_k1 `{45:403, 60:185, 72:39, 112:13}`; static termination_k1 = 112 on
all 640.

Disclosure / saving:

- static total key-dependent bits `847,360` (mean `1324.0`);
  adaptive total `675,783` (mean `1055.9109375`); mean saving `268.0890625` bits.
- percentage saving `20.248418617824772%`.
- exact integer leakage comparison:
  `100*675,783 = 67,578,300 <= 85*847,360 = 72,025,600` -> **true**
  (20.2484% reduction; 15% requirement met with slack 4,447,300).

Accounting / tags / feedback / transcript:

- tag invocations static 640 / adaptive 942 / total 1,582; feedback invocations
  302; public control bits total `4,149,888` (public seed 4,149,586 + feedback
  302).
- union bound `min(1, 1582*2^-64) = 8.57603918436034e-17`.
- transcript event_count 4746; event types `l1_disclosure=1582`,
  `l2_disclosure=1280`, `verification_tag=1582`, `control=302`;
  transcript recount mismatch **0**.

Per-stream (stream : both_exact/neither): `2026091550: 127/1`,
`2026091551: 127/1`, `2026091552: 124/4`, `2026091553: 127/1`,
`2026091554: 127/1`; rows sum to the global totals.

Planning-only f (surrogate, not real-channel efficiency): static `2.4235`,
adaptive `1.9328`.

Tests: 15 new (`test_nbpolar_adaptive_l1.py`) plus 216 total (accepted NB-Polar
predecessor suite) green.

## 4. Persisted label

`outcome_label = BLOCKED`; `integrity_all_pass=false`;
`failing_integrity_gates=[d1_exactly_nested_and_d2_disclosed_once]`;
`scientific_all_pass=true`. The artifact was persisted honestly with the failing
gate `false`.

## 5. Failing-gate diagnosis (gate-check implementation defect, not a contract violation)

- Location: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py`
  gate `_integrity_gates` (`:1391-1405`; D2 term `and l2_once` at `:1401`);
  `l2_once` (`:1350-1354`) with the count key built at `:1341-1343`:
  `parts = str(event["event_id"]).split("-"); key = (int(event["block_id"]), parts[2])`.
  `expected_l2` (`:1346-1349`) is also keyed by the per-stream block index.
- Collapse mechanism: `paired_block_events` receives only `PairedBlockResult`,
  whose `block_index` is the per-stream index; the caller does not pass
  `stream_seed` (`:2110`), and the runner loops blocks 0..127 inside each of the
  five streams (`:2059-2062`, `:2087`). Hence `block_id = int(block_index)`
  (`:866/:872`) and event ids like `block-{block_index}-static-l2-disclosure`
  (`:909`) / `block-{block_index}-adaptive-l2` (`:956`) repeat across streams.
  The gate then counts by `(block_id, arm)` where `block_id` is per-stream: the
  1,280 L2 events (640 static + 640 adaptive) collapse onto 256 keys
  `{(0..127) x {static, adaptive}}`, each counted **5**. `set(l2_counts) ==
  expected_l2` is true (sets hide multiplicity) but `all(count == 1 ...)` is
  false. All other gate-4 conjuncts are true (D1 nested/prefix and
  `new_positions` partition, all 640 static `termination_k1 == 112`).
- Contract-correct value: under the frozen contract ("D2 disclosed once per
  arm/block") the executed behaviour is correct — per `(stream, block, arm)` the
  L2 disclosure count is exactly 1 for all 640 blocks x 2 arms
  (= 1,280/1,280), no block has 0 or >=2 disclosures. The contract-correct value
  of the gate is therefore **true**; had the check used the full block identity,
  `integrity_all_pass=true` and the label would have been
  `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`.
- Reviewer corroboration: the independent Pre-RESULT reviewer reproduced the
  isolated `false` with a 2-stream probe (fresh non-frozen seeds, `/tmp/`
  only) — 1 stream x 4 blocks: gate 4 true; 2 streams x 4 blocks: gate 4 false
  with exactly `['d1_exactly_nested_and_d2_disclosed_once']` failing — and
  confirmed the focused suite never exercises a multi-stream runner call
  (coverage gap).

This is a diagnosis only. Per the packet stop rule, a failing integrity gate is
not repaired or rerun; the failure root stays byte-for-byte and the persisted
label stays `BLOCKED`.

## 6. Reviewer verdicts

- Independent Pre-EXECUTE (`PRE_EXECUTE_REVIEW.md`): **PASS** (six non-blocking
  findings; no number/gate/conclusion change). No scientific SC call made there.
- Independent Pre-RESULT (`PRE_RESULT_REVIEW.md`): **PASS_WITH_COMMENTS**;
  every persisted number, all 12 integrity booleans and all 4 scientific
  booleans independently reproduced; sole failing gate diagnosed as a
  **gate-check implementation defect (class b)** with contract-correct value
  true. Non-blocking notes: `STATUS.yaml` `attempts_used` pending (fixed by this
  closeout); `report.md` omits some tables present in `aggregate_summary.json`;
  a future packet should key the D2 check on full block identity and add a
  multi-stream test (main-thread-owned successor decision).

Reviewer verdicts permit operator return but do not grant main-thread
acceptance.

## 7. Five-file inventory (output root)

| file | size (bytes) |
|---|---|
| `frozen_plan.json` | 15,248 |
| `per_block_paired_outcomes.json` | 1,125,035 |
| `transcript_accounting.json` | 2,090 |
| `aggregate_summary.json` | 9,090 |
| `report.md` | 2,023 |

Exactly these five files; single generation (all written within a 47 ms window);
no `.tmp`/partial/backup/second copy; root written once and not rewritten.

## 8. Attempt / seed accounting

- Attempts allowed 1; consumed before 0; consumed by this run **1**; retries 0.
  Attempt 1/1 was consumed at the first scientific SC call (stream 2026091550,
  block 0, static L1).
- Streams `2026091550..2026091554` and public masters `2026101550..2026101554`
  consumed; masters are public control. Seeds intersect the refused set = empty.
- No rerun. The failure root (the output root plus the persisted `BLOCKED` label
  and failing gate) is preserved; no partial replacement.

## 9. Bounded scope

Synthetic `N=256` development evidence only. This is **not** real-data FER,
reconciliation efficiency, leakage, key-rate, qualification or promotion
evidence. `undetected` frames are never merged with exact frames. `planning_only_f`
is not real-channel efficiency. No real/artifact data, empirical construction,
N>256, FWHT, soft APP, SCL or learned policy was used.

## 10. Requested main-thread decision (one)

Disposition of the BLOCKED result. Options: (a) accept the artifacts under the
documented corrected gate interpretation via a main-thread ruling, paired with a
successor fix of the D2-check identity (composite `(stream, block, arm)`) and a
multi-stream test; or (b) require a new authorization. A rerun is not permitted
in this packet. No other stage remains unrun beyond this main-thread
disposition.

No commit. No push.
