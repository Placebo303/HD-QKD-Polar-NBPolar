# Phase 4-P10 Tier-X packet — GF(32) FWHT kernel and scaling probe

## Mission

Determine, without artifact access or scientific claims, whether the all-finite
GF(32) SC minus-node can use a numerically equivalent Walsh-Hadamard convolution
with useful speed/memory scaling. This is an engineering probe, not decoder
acceptance.

## X10-01 — Strict Tier-X scope

Write only `workspace/probes/nbpolar_x10_fwht_kernel_scaling/prereg.md` and
`results.json`. No production/test/OpenSpec/ledger/memory/index edits. No
artifact, evidence-root, raw, held-out, real, EVAL, decoder gate, official seed,
or tag access. No attempt is defined or consumed; no candidate/accepted or
scientific pass/fail label.

Before benchmarking, freeze `prereg.md` with exactly three top-level lines:
question; exact parameters; exact command. Embed the complete stdlib+NumPy
execution body so executed code is recoverable without a third file.

## X10-02 — Frozen prototype

Use GF(32) addition as five-bit XOR. For every all-finite row pair, reproduce
the accepted `_minus_block` probability convolution, including the alpha=2
field-multiplication permutation, and normalize to log probabilities.

- vectorized length-32 FWHT and inverse scaling by 32;
- rowwise max subtraction before exponentiation;
- clip negative roundoff only to zero and report the raw minimum;
- dispatch any row with nonfinite input to accepted direct `_minus_block` and
  report fallback counts;
- do not change tie-breaking, support, field, transform, or decoder semantics.

## X10-03 — Frozen matrix

Probe seed `2026091740`. Regimes: dense logits uniform on [-20,0]; dense logits
uniform on [-200,0]; one dominant symbol with others uniform on [-80,-20]; and
deterministic 25% `-inf` fallback rows with at least one finite value.

For each regime and row count `[1,8,32,128,512,2048]`, compare prototype and
direct reference. Use 2 untimed warmups and exactly 7 timed repetitions per
implementation/cell, alternating order. Report every duration and median.

Also profile the unmodified accepted `sc_decode` at N `[64,256,1024]`, three
fresh injected all-finite metric blocks per N. Do not splice FWHT into SC.

## X10-04 — Required results

`results.json` records environment/parameters; per-cell maximum probability
and finite-log error, argmax mismatch, support mismatch, raw negative minimum,
fallback rows, all timings/medians; speed ratios; estimated temporary bytes for
direct q² gather versus FWHT q storage; all full-SC timings; aggregate worst
discrepancies; and every execution/error/rerun. Set no threshold or winner.

## X10-05 — Review and STOP

Obtain independent `reviewer-go` focused numerical review in the return message
without a third probe file. It independently checks the GF(32) identity on
literal/random rows, recomputes aggregates, checks timing/write scope, and
confirms zero forbidden access. Main thread trusts that evidence.

One execution-error rerun is allowed only with unchanged frozen parameters,
model and seed, with both executions recorded. STOP on semantic ambiguity,
external input, production-file need, or inability to preserve nonfinite
semantics. Bounds: 2 GiB virtual memory, 1800 s wall. No commit/push.

## Return contract

Return `X10 complete` or a concrete blocker, with two-file inventory, execution
accounting, numerical discrepancies, timing table, fallback result, SC profile,
review verdict, boundaries, and recommended next Tier-Y engineering gate.
