# Phase 4-X13 Tier-X packet — two-layer metric memory-lifetime probe

## Mission

Find the smallest exact change that lets the full two-layer N=262144 metric
pipeline fit under 2 GiB. Test ownership/lifetime alternatives on injected
tables only; do not alter production or rerun P12.

## X13-01 — Tier-X boundary

Write only `workspace/probes/nbpolar_x13_metric_memory_lifetime/prereg.md` and
`results.json`. Freeze the three-line preregistration with complete embedded
stdlib+NumPy body before the first probe call. No production/test/OpenSpec/
ledger/memory/index edit; no artifact/evidence-root/official seed/raw/held-out/
real/EVAL/tag/FWHT/APP/SCL/scientific gate. No attempt or claim label.

Use probe seed `2026091840`, GF(32) polynomial 37, alpha=2, chunk_rows=512.
Create deterministic injected normalized P1 `[1024,32]`, P2 `[32,1024,32]`
and p_b tables; sample synthetic Bob/high/low vectors without reading external
files.

## X13-02 — Frozen alternatives

Compare the accepted pipeline with exactly these probe-local alternatives:

1. `lifetime_only`: preserve accepted builders/converter, but after extracting
   L1 `x_hat` and required scalar provenance, delete L1 probabilities, metric,
   SCResult and other N×32 arrays before constructing L2; likewise release L2
   probabilities and SCResult at last use. Before appending a block outcome,
   reduce it to the scalar fields used by accounting/gates so no decoded
   high/low/label arrays survive across blocks.
2. `owned_log`: add the same lifetime release, gather an owned float64 L2
   probability array, validate it under the accepted contract, apply `np.log`
   and row normalization in place, pass the resulting log array directly to
   accepted `sc_decode`, and retain provenance as the frozen enum scalar. Never
   mutate a caller-owned/view array.

Do not change probabilities, floor/support, normalization formula/order,
decoder, decisions, exception taxonomy or truth isolation. Do not invent a
public `consume` flag or weaken `SymbolMetric` immutability.

## X13-03 — Exactness and memory matrix

At N=64 and 256 compare baseline, `lifetime_only` and `owned_log` for finite,
exact-zero support, known-coordinate, impossible-disclosure and X11-C3 cases.
Require/report exact equality of constructed log metrics, support, provenance,
exception type/message, u/x decisions, decision metrics/scores and outcomes.
Any mismatch triggers STOP without rerun.

Run each alternative in a fresh child process under `ulimit -v 2097152` at
N=65536 for 4 sequential blocks and N=262144 for 2 sequential blocks. Record exit/status,
stage reached, wall and peak RSS. Run `lifetime_only` first, then `owned_log`;
do not select or modify an alternative after results. A child MemoryError is a
descriptive result and must be captured in the parent record.

Instrument a simple live-array ledger at stage boundaries and after each scalar
outcome append: name, shape, dtype,
nbytes and whether still referenced for every N×32 array. Record formula totals
and HWM caveat. Checkpoint the single results record after every stage so a
resource STOP cannot erase completed evidence.

## X13-04 — Review and return

Independent reviewer-go, in the return message only, reconstructs all small-N
exactness cases, audits ownership/no-aliasing and accepted validation order,
recomputes the live-array ledger, checks child-process resource results,
checkpoint completeness, two-file scope and forbidden access. Its explicit
evidence is trusted.

No winner/threshold. Report which frozen alternatives completed each N/block sequence and
their exactness/RSS descriptively. One rerun is allowed only for execution-code
error with unchanged inputs/alternatives/seed; semantic or resource failure is
not rerunnable. Total wall 1200 s, each child 400 s, 2 GiB. No commit/push.

Return `X13 complete` or a concrete blocker, with two-file inventory, execution
accounting, small-N parity, per-alternative N/RSS/stage results, array ledger,
review and the exact recommended P12-R1 delta (or route stop).
