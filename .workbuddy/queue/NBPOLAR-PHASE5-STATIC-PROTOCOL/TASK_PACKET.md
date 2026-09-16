# Heavy task packet — NB-Polar Phase 5 static protocol

## Mission and authority

Implement and measure the smallest scientifically valid static NB-Polar
reconciliation protocol. This packet is inert until the exact user grant in
`AUTHORIZATION_PROMPT.md` is supplied. The operator implements and reports;
the main thread owns acceptance and scientific conclusions.

## Frozen predecessor and point

- Predecessor: `EMPIRICAL_PRIOR_SC_INTERFACE_ACCEPTED`.
- GF32 polynomial 37, alpha 2, natural-order transform, accepted reference SC.
- Synthetic erasure point: `N=256`, `epsilon=0.05`, `K=45`.
- Static disclosure set: first 45 entries of the accepted Phase 3 analytic
  order (worst-first), exactly matching `evaluate_blocks(..., k=45)`; publish
  their actual GF32 values and SC-reconstruct the remaining 211 coordinates.
- One SC invocation and one final 64-bit Toeplitz verification per attempted
  block. No retry or adaptation.

## Allowed files

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/protocol.py`
- `comparison_bench/src/comparison_bench/methods/nbpolar_static.py`
- `comparison_bench/tests/test_nbpolar_protocol.py`
- existing NB-Polar `__init__.py` only for explicit public exports
- this OpenSpec change and this queue directory
- lifecycle/index/decision/troubleshooting/project-memory docs required by the return

Do not modify frozen `src/`, `experiments/`, `tools/`, sibling checkouts,
`results/`, or `comparison_bench/outputs_comparison/`.

## Acceptance IDs

- **P5-A01** zero and non-zero disclosed values round-trip without sentinels.
- **P5-A02** disclosed coordinates equal `U=A G` and the static set is invariant.
- **P5-A03** full recovered `U` re-encodes to the complete 1024-ary label vector.
- **P5-A04** Alice truth cannot enter the SC metric or undecoded coordinates.
- **P5-A05** decoder is invoked once; verification is invoked at most once after it.
- **P5-A06** the tag never selects, retries or changes a decoder path.
- **P5-A07** verified non-exact is `undetected`, never success or exact.
- **P5-A08** exact, verified, undetected, failed-decode, verify-failed and
  resource-abort accounting is disjoint and exhaustive.
- **P5-A09** transcript recount equals `5*45 + 64 = 289` key-dependent bits
  for every verification invocation; Toeplitz seed bits are public control.
- **P5-A10** existing `FrameBatch`, `IRRunConfig`, `IRRunResult` signatures are unchanged.
- **P5-A11** exhaustive tiny cases, wrong-tag mutation and independent recount pass.
- **P5-A12** all accepted NB-Polar predecessor tests pass without artifact access.

## Autonomous implementation and exploration

Implement the protocol and a thin adapter. Use injected and synthetic data to
compare direct reconstruction against an independently written literal oracle,
exercise arbitrary disclosed zeros, malformed/static-set rejection, all
terminal outcomes and resource accounting. Profile N=64/256/1024 only to set
the execution budget. Keep one operational path and one small independent
oracle; do not add generalized protocol infrastructure.

Routine in-scope fixes are allowed. Stop on a frozen-requirement conflict,
accepted-predecessor defect, inability to maintain truth isolation, or a
scientifically meaningful accounting ambiguity.

## Pre-EXECUTE freeze

Before any 300-block scientific call, freeze and independently review:

- one fresh run seed not used by Phase 1–4;
- a deterministic per-block independent Toeplitz-seed derivation and its public-bit count;
- exact 300-block command and a new absent additive output root under this queue;
- the static coordinate set, attempt-consumption point and no-rerun rule;
- total/per-case runtime and RSS ceilings based on the synthetic profile;
- exact output schema, Wilson calculation and outcome precedence;
- proof that artifact/real-data/DEV/EVAL and forbidden roots are unreachable.

Any review failure blocks execution until repaired and re-reviewed. The single
attempt is consumed at the first scientific decoder call.

## Development run and gates

Run exactly 300 frozen synthetic blocks. Persist compact plan, per-block scalar
outcomes, transcript accounting summary, aggregate summary and report. Do not
persist private symbol vectors, decoded keys or Toeplitz seed contents.

Hard gates:

1. all P5-A01–A12 remain true;
2. outcome accounting is exhaustive and mutually exclusive;
3. independent disclosure recount has zero mismatch;
4. `undetected == 0`, truth-leak violations 0, nonfinite 0;
5. one-sided 95% Wilson lower bound for exact recovery is at least 0.90;
6. average key-dependent disclosure is below `10*N` input bits;
7. all planned blocks execute unless the preregistered resource stop fires.

The label `STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE` is a synthetic development
signal only. It is not real FER, leakage efficiency, key rate, qualification,
promotion or evidence for adaptive disclosure.

## Pre-RESULT and return

An independent reviewer must recompute the Wilson bound, every outcome total,
verification invocation universe, disclosure decomposition and transcript
recount from actual artifacts. It must verify `undetected` isolation and the
absence of private/raw outputs. FAIL blocks solidification.

Return only:

- `STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE`, with complete reviewed evidence; or
- `BLOCKED(<single earliest gate>)`, with command, raw error, remedies,
  attempt/seed state, unrun stages and the one main-thread decision required.

No commit or push.
