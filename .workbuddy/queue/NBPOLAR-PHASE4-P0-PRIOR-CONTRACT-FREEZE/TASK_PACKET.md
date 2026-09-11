# Heavy task packet — Phase 4-P0 Model-F prior-contract freeze

## State and purpose

`PLAN_READY_AWAITING_EXPLICIT_AUTHORIZATION`. This packet is prepared only. It
does not authorize file reads outside ordinary source/document inspection,
adapter implementation, CAL/Model-F execution, decoder execution, real data,
or Phase 4-P1.

The task freezes the mathematical and software boundary between accepted
Model-F statistics and the Phase 1-3 q-ary Polar stack. Its output must make an
axis, smoothing, provenance, support, or train/evaluation mistake detectable
before any q-ary SC call.

## Inputs to inspect after authorization

Read all source files before citing them. Treat sibling checkouts as read-only.

- Current NB-Polar: `docs/nbpolar/{ASSET_MAP,ARCHITECTURE,ROADMAP,
  VALIDATION_GATES,CRITICAL_PATH}.md`, Phase 1-3 code/tests and the accepted
  Phase 3-R1 artifacts.
- Comparison history: accepted Model-F count builder and per-Bob-column
  concentration implementation, especially `counts_ab`, `p_b`, `build_f`,
  symbol packing, high/low decomposition, D5 prior consumers, and D7 belief
  provenance findings.
- Release: binary channel-prior/decoder boundary and CAL/VAL separation only;
  no binary LLR, PW order, XOR transform, or CA-SCL code is reusable here.
- Durable project/OpenSpec documents and relevant archived decisions. Historical
  results are evidence about contracts and failure modes, never NB-Polar data.

## Required work products

### P0-1 source inventory and provenance map

Create an exact table of source path, class/function, input shape/dtype, output
shape/dtype, axis meaning, normalization direction, smoothing formula, symbol
packing, provenance, and accepted/rejected status. Resolve every competing
Model-F builder by formula and call site. Mark the accepted per-column formula

`p_global[a] = sum_b counts[a,b] / sum_{a,b} counts[a,b]`

`n_b[b] = sum_a counts[a,b]`

`f[a,b] = (counts[a,b] + lambda*p_global[a]) / (n_b[b] + lambda)`.

Show which historical implementation instead applied a per-cell pseudocount
and ban it by exact callable/path. Confirm whether stored matrices are indexed
`[Alice,Bob]` or `[Bob,Alice]` at every boundary; do not infer from names.

### P0-2 symbol contract

Freeze how one 10-bit HD symbol becomes `(high, low)` GF32 coordinates and how
Bob/context conditions each probability. Define valid ranges, endianness,
field-basis versus integer-label semantics, batch axes, and missing/support
behavior. State explicitly that high/low composition is not GF1024 field
multiplication.

Freeze these decoder-facing tensors in natural-U order:

- `P1[frame, i, a] = P(A_high=a | B_high, B_low, context)` or the narrower
  actually supported conditioning determined from code;
- oracle `P2_true[frame, i, a] = P(A_low=a | A_high_true, B, context)` for
  diagnostic use only;
- candidate `P2_hat[frame, i, a] = P(A_low=a | A_high_hat, B, context)` for the
  executable two-level route.

If existing evidence supports different conditioning, freeze that exact
contract and explain the data requirement. Never silently drop a Bob/context
variable.

### P0-3 SymbolMetric API

Specify the smallest immutable value object needed by `sc_decode`:

```text
SymbolMetric(
    logp: float64[N,q],
    conditioning: explicit enum/string,
    provenance: PRIOR_ONLY | ORACLE_CONDITIONED | CANDIDATE_CONDITIONED,
    symbol_order: 0..q-1,
    normalization: LOGSUMEXP_ZERO,
)
```

Define construction/validation helpers separately from the object. Freeze
conversion from probabilities/counts to log domain, exact-zero as `-inf`, row
normalization, allowed floors, and when smoothing occurs. No q-ary SC metric
may be called a complete APP.

### P0-4 separated evidence lifecycle

Name CAL, DEV and one future EVAL source without consuming them. CAL alone may
fit counts/lambda and freeze the adapter. DEV may select a bounded floor or
diagnose candidate-L2 behavior only if preregistered. EVAL is single-use and
cannot tune any parameter. VAL/EVAL must never enter construction, smoothing,
floor selection, or thresholds.

Define three future diagnostics, kept separate:

1. L1 using P1;
2. L2-oracle using P2_true, an upper-bound mechanism diagnostic;
3. L2-candidate using P2_hat, the executable dependency test.

Specify paired block identities and failure precedence. Truth may enter only
the oracle diagnostic and scoring; it must be structurally impossible for it
to enter P1, candidate-L2, or the ordinary decoder call.

### P0-5 validation and early falsification matrix

Freeze stable IDs and quantitative gates for the later adapter implementation:

- exact axis/transpose sentinel using an asymmetric hand-built count matrix;
- per-Bob-column sums equal 1 within absolute 1e-12;
- direct formula versus adapter maximum absolute error <=1e-12;
- probability-to-log round trip on positive support <=1e-12;
- exact-zero support remains `-inf` unless the frozen smoothing formula makes
  it positive;
- GF32 label/packing roundtrip exhaustive over 0..31 and selected 10-bit pairs;
- batch/position permutation equivariance;
- one-hot/noiseless and uniform-prior SC sanity using the Phase 2 oracle;
- CAL/DEV/EVAL identity non-overlap and provenance assertions;
- truth-leak sentinels for P1 and candidate-L2;
- held-out cross entropy reported against uniform and unsmoothed baselines,
  with its acceptance threshold frozen only from CAL/DEV evidence;
- runtime/memory budget for N=256 metric creation, measured without decoder.

Each gate must name its oracle/ground truth, failure category, first diagnostic
to inspect, and whether it blocks implementation, decoder execution, or only a
performance claim.

### P0-6 architecture and implementation handoff

Choose exact module/file names for Phase 4-P1, expected to remain near:

- `formal_ir/nbpolar/prior.py` for pure count/probability/log-metric adapters;
- one focused test file with synthetic fixtures;
- no benchmark method, protocol wrapper, or result-root writer.

Freeze function signatures, dataclasses/enums only when needed, dependencies,
allowed imports, error semantics, and `__init__.py` exports. Prefer NumPy and
existing field/symbol helpers. Do not build a generic channel framework,
configuration system, cache, manifest, checksum layer, or compatibility shim.

Produce the next paired Phase 4-P1 `TASK_PACKET.md` and `PROMPT.md`, but mark
them not authorized. Phase 4-P1 must begin with synthetic fixtures and an
independent formula oracle before any CAL artifact is loaded.

## Required alternatives and decisions

Compare at least three bounded designs:

1. direct dense `(N,32)` log-metric materialization;
2. conditional-table object plus per-frame gather;
3. lazy callback/view evaluated by SC.

Select one for the reference decoder using scientific clarity, truth-isolation,
memory at N=256, and oracle testability. Also decide whether floor is forbidden,
fixed, or selected on CAL/DEV; whether P1 conditions on both Bob components;
and whether candidate-L2 hard conditioning is sufficient for the first test.
Do not average alternatives: select one MVP and defer the rest explicitly.

## Allowed files after authorization

- this Phase 4-P0 packet directory;
- a new Phase 4 OpenSpec proposal/design/tasks/spec delta;
- additive updates to `docs/nbpolar/`, `docs/decision-log.md`, and
  `AGENT_PROJECT_MEMORY.md` after review;
- the not-authorized Phase 4-P1 WorkBuddy packet.

No `.py`, data, results, or existing Phase 1-3 artifact may be modified.

## Mandatory review

Before return, a real independent reviewer must check every cited callable and
axis against source, recalculate the smoothing formula, trace truth provenance,
verify CAL/DEV/EVAL isolation, and confirm the P1 packet remains unauthorized.
Self-review is diagnostic only. Needs-changes must be repaired and reviewed
again without widening scope.

## Return contract

Return exactly one of:

- `FREEZE_CANDIDATE` with changed-file list, exact source citations, selected
  API and alternatives, complete validation matrix, independent review verdict,
  memory triage, risks, and the inactive P1 packet; or
- `BLOCKED(<single earliest defect>)` with raw evidence, attempted read-only
  remedies, later items not run, and one decision needed.

No Phase 4 implementation or scientific conclusion follows automatically.
