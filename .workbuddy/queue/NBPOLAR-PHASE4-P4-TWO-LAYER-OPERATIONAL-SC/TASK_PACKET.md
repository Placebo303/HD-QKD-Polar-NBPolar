# Heavy task packet — Phase 4-P4 two-layer operational SC

## Mission

Build the smallest scientifically valid two-stage SC closed loop and execute a
paired oracle-L2 versus candidate-L2 synthetic interface gate. This restores
the Phase-4 dependency omitted before the protocol phases.

## Acceptance IDs

- P4-A01 P1 uses Bob only and L1 SC returns a source-domain hard candidate.
- P4-A02 operational P2_hat uses exactly Bob plus that candidate.
- P4-A03 oracle P2_true uses true L1 only in the labelled diagnostic arm.
- P4-A04 both L2 calls are fresh SC calls with no APP/state transfer.
- P4-A05 full label is `low_hat+32*high_hat`; tag is invoked only finally.
- P4-A06 operational output is invariant under truth mutation with fixed inputs.
- P4-A07 N=2/4 exhaustive probability/decode oracle errors meet Phase-2 tolerances.
- P4-A08 forced L1 error produces an auditable oracle/candidate L2 divergence.
- P4-A09 layer/final buckets are disjoint and disclosure recount is exact.
- P4-A10 paired N256 blocks, seed derivation and output root are frozen.
- P4-A11 focused plus predecessor tests pass.
- P4-A12 independent Pre-EXECUTE and Pre-RESULT reviews pass.

## Implementation and exploration

Add one two-layer core module, one thin method adapter only if the existing
benchmark contract requires it, and one focused test file. Reuse `prior.py`,
accepted transform/SC and final Toeplitz verification. Use injected synthetic
joint tables; do not load Model-F artifacts.

The development point is frozen now: independent layer-erasure injected joint
table, GF32, N=256, epsilon1=0.05, epsilon2=0.20, analytic worst-first sets
K1=45 and K2=110, 96 paired blocks, run seed 2026091360 and public Toeplitz
master 2026091361. The only output root is
`.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/`,
which must be absent before execution and contain exactly
`frozen_plan.json`, `per_block_two_layer_outcomes.json`,
`transcript_accounting.json`, `aggregate_summary.json`, and `report.md` after
success. Limit wall time to 3600 seconds and address space to 2 GiB.

The exact WSL command is:

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer --n 256 --epsilon1 0.05 --epsilon2 0.20 --k1 45 --k2 110 --blocks 96 --seed 2026091360 --toeplitz-master 2026091361 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate
```

Hard gates are: 96/96 paired coverage; both arms invoked for every block whose
L1 stage returns a candidate; candidate P2 provenance always
`CANDIDATE_CONDITIONED`; oracle P2 always `ORACLE_CONDITIONED`; operational
truth-leak count zero; nonfinite and undetected zero; all final buckets and
per-layer sub-buckets disjoint/exhaustive; disclosures equal exactly
`5*(K1+K2)` per fully invoked arm before the one final 64-bit tag; transcript
recount mismatch zero; injected wrong-L1 propagation tests pass before the
run; no resource abort. Exact-recovery and oracle/candidate divergence counts
are report-only and have no threshold, because this is an interface gate.

## Stop rules

STOP on axis/packing ambiguity, inability to recover source-domain L1 before
P2 gather, exhaustive-oracle mismatch, truth leak, nonfinite metric, failed
predecessor test, output-root collision, failed independent Pre-EXECUTE, or the
first failed frozen result gate. No rerun, seed change or parameter tuning.

## Forbidden

No artifact/parquet/TTBin or real data; no empirical construction; no N>256;
no FWHT/scalable decoder; no APP/soft L1 belief; no SCL/Phase7; no efficiency,
FER, qualification or promotion claim; no old-root modification, commit/push.
