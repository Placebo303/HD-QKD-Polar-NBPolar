# P5 implementation notes — alternatives, evidence, rejected choices

Author: operator session, 2026-09-13. Companion to `P5_FREEZE.md` (frozen) and
`TASK_PACKET.md`. No commit or push was performed.

## 1. What was built

- `formal_ir/nbpolar/protocol.py` — static protocol core, accounting, transcript
  recount, truth sentinel, budget/profile hooks and the dev-gate CLI.
- `methods/nbpolar_static.py` — thin `IRMethod` adapter over the core.
- `tests/test_nbpolar_protocol.py` — 16 focused tests for P5-A01..A11, refusals,
  resource abort, Wilson values, five-file schema and forbidden-marker scan.
- `formal_ir/nbpolar/__init__.py` — explicit re-exports only.

Frozen constants: `FROZEN_RUN_SEED=2026091317`, `TOEPLITZ_MASTER_SEED=2026091318`,
`DEFAULT_N=256`, `DEFAULT_K=45`, `EPSILON=0.05`, `SEED_BITS=2623`,
`DEV_GATE_TOTAL_WALL_S=300.0`, `DEV_GATE_PER_BLOCK_SOFT_CAP_S=5.0`.

## 2. Alternatives tried and rejected

- **Adapter input semantics.** (a) Ignore the `FrameBatch` and self-generate
  synthetic frames: rejected — the adapter would silently discard its input.
  (b) Build Bob's metric from `bob_symbols` (observed label or `-1` erasure) and
  Alice's `x` from `alice_symbols // 32`: chosen, documented, and validated
  against unchanged `FrameBatch`/`IRRunConfig`/`IRRunResult` signatures.
- **Per-block Toeplitz seed.** Sequential single RNG stream: rejected — a stream
  position depends on how many blocks ran before, which couples seed material
  to resource-stop timing. Chosen: deterministic SHA-256 counter-mode derivation
  from master `2026091318` + `block_index`, truncated to `10n+63` bits.
- **Seed length.** First implementation hard-coded 2623 bits for every N; the
  tiny-N tests (A01/A11) failed with "expected a binary vector of the locked
  length". Fixed by deriving `10*n + 63` per call; for the frozen N=256 point
  this is exactly 2623. This was the only implementation bug found by tests.
- **Truth sentinel placement.** Mutating *copies* of the truth buffers after
  decoding cannot detect an aliased decision (the copy is untouched). Chosen:
  keep pristine copies for the record, then mutate the live truth buffers after
  the decisions exist and compare metric/decision snapshots bitwise. Unit-tested
  both positive (clean) and adversarial (aliased) cases.
- **Resource stop.** Preempting a running decoder is not possible without
  signals; chosen: check the total budget before each block and the per-block
  cap after it completes. Remaining planned blocks are recorded as
  `resource_abort`, and the five files are still written. Verified with
  `total_wall_s=-1` (all aborted, zero decoder calls) and
  `per_block_soft_cap_s=-1` (first block executed, remainder aborted).
- **Run-level undetected test.** With a scripted wrong decode, the real tag
  yields `verify_failed`, not `undetected`. A08 therefore scripts the tag
  wrapper: honest for block 0, forced collision for block 2, so a single 3-block
  run exercises `exact + decode_failed + undetected` with disjoint recount.
- **Profiling N=1024.** The frozen `K=45` disclosure is too sparse at N=1024:
  all 8 probe blocks raised `ImpossibleDisclosedValueError` (a legitimate
  `decode_failed`), so complete-decode timing used K=160/320 scaling probes.
  These probes are informational only; the frozen point remains N=256/K=45.
- **Candidate gating.** `coverage_complete` requires `attempted == planned`; a
  resource stop is preregistered behavior but cannot yield the development
  candidate label. This is the strict reading of hard gate 7 and is recorded in
  the freeze.

## 3. Measured evidence

### Focused tests (plain python and pytest)

```text
.venv/bin/python comparison_bench/tests/test_nbpolar_protocol.py
  16/16 passed (a11 exhaustive tiny oracle 1.36 s)

.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_protocol.py -q
  16 passed in 5.51 s

.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_*.py -q
  136 passed in 66.71 s
```

### Profile (in-memory, non-frozen seeds, no output files)

`/tmp/opencode/p5_profile.py`, profile seed 2026091330:

| workload | blocks | median wall | max wall | metric | decode | outcomes |
|---|---|---|---|---|---|---|
| N=64 K=45 | 64 | 4.24 ms | 14.79 ms | 0.06 ms | 4.18 ms | 64 exact |
| N=256 K=45 | 64 | 15.61 ms | 19.90 ms | 0.13 ms | 15.48 ms | 64 exact |
| N=1024 K=45 | 8 | 11.69 ms | 16.66 ms | 0.39 ms | 11.31 ms | 8 decode_failed |
| N=1024 K=160 | 14 | 70.74 ms | 74.24 ms | 0.42 ms | 70.08 ms | 14 exact |
| N=1024 K=320 | 14 | 69.69 ms | 77.35 ms | 0.39 ms | 69.31 ms | 14 exact |

Peak RSS 120000512 bytes ≈ 114.4 MiB. Expected 300-block N=256 cost
≈ 4.7 s; frozen ceilings 300 s total / 5 s per block / external `timeout 600` /
2 GiB `ulimit -v`.

### Dev-gate smoke (temp roots only, non-frozen seeds)

```text
ulimit -v 2097152; timeout 120 ... protocol --mode dev-gate \
  --run-seed 2026091319 --blocks 3 --out /tmp/opencode/p5_cli_smoke
  -> 3 exact, 5 files, candidate null (n too small for the Wilson gate)

same command again on the existing root
  -> "refused: refusing to overwrite existing output root" (exit 2)
```

The real output root `.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/
static_protocol_dev_gate` was never created; the frozen 300-block command and
seed were never executed. `attempts_used` remains 0.

## 4. Notes for the Pre-EXECUTE reviewer

- `D` is a set: `disclosure_coordinates` is sorted ascending; the freeze records
  the worst-first slice as well. The equality to
  `analytic_order(0.05,256)[:45]` is asserted in tests.
- The adapter rejects `verify_mode != "toeplitz64"` so the comparison-layer
  `crc32` default cannot silently become the formal protocol. It requires
  `dimension == 1024` and `frame_len_symbols == 256`.
- `n_frames_success` is `exact` only; `undetected` and `resource_abort` live in
  metadata and never inflate success.
- `beta_eff_empirical` comes from the shared
  `metrics.leakage.compute_beta_eff_empirical` (derived, not hand-filled).
- Tests never use seed 2026091317 and never touch the repository `results/`,
  `comparison_bench/outputs_comparison/`, or sibling checkouts.
