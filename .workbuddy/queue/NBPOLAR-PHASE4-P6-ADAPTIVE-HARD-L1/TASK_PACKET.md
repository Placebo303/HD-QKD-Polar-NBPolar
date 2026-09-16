# Tier-Y task packet — adaptive hard-L1 disclosure gate

## Objective and predecessor

Implement and execute one paired synthetic development gate for the X05
frontier schedule `K1=[45,60,72,112]`, fixed `K2=140`, against static K1=112.
The sole claim tested is: at this frozen dependent-L2 point, adaptive hard-L1
disclosure preserves the static endpoint's exact recovery while reducing mean
key-dependent disclosure by at least 15%.

Predecessors: accepted Phase 4-P5 mechanism result plus X04/X05 Tier-X planning
evidence. X04/X05 are design inputs, not acceptance evidence for and must remain
unchanged.

## P6-A — OpenSpec and allowed implementation

Before behavior changes, extend the existing Phase 4 OpenSpec change with a P6
delta and tasks covering this exact contract. Then add only:

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py`;
- the necessary export in that package's `__init__.py`;
- `comparison_bench/src/comparison_bench/methods/nbpolar_adaptive_l1.py` only if
  the unchanged `FrameBatch/IRRunConfig/IRRunResult` adapter is needed;
- `comparison_bench/tests/test_nbpolar_adaptive_l1.py`;
- this packet's lifecycle/review/result documents and ordinary milestone docs.

Reuse accepted field, SC, dependent-table, sampler, two-layer outcome, Toeplitz
and accounting code. Do not change `sc.py`, construction, prior semantics,
P5/X03/X03b/X04/X05, or any earlier evidence root.

## P6-B — Frozen scientific point

- GF32 polynomial 37, alpha 2, natural SC order, N=256;
- epsilon1=0.05;
- strong dependent profile `epsilon2(u1)=0.02+0.36*u1/31`;
- analytic worst-first nested D1 prefixes `[45,60,72,112]`;
- fixed D2 prefix K2=140, disclosed once per arm/block;
- five fresh streams `2026091550..2026091554`, 128 common blocks each, total
  640 paired blocks;
- public Toeplitz master `stream+10000`, domain-separated per arm/block/level;
- one attempt, consumed at the first scientific SC call;
- address-space limit 2 GiB and wall timeout 3600 seconds.

Static arm: one fresh L1 SC at K1=112, one candidate-conditioned L2 SC at
K2=140, then one 64-bit verification tag.

Adaptive arm: at each K1 stage, restart L1 SC from the original P1 metric,
restart candidate-conditioned L2 SC from the original P2 table gathered by the
current hard L1 candidate, then verify the full 10-bit label. On tag match,
accept and stop. On mismatch before K1=112, emit one public one-bit feedback,
disclose only the next D1 increment and advance. At K1=112, mismatch is
`verify_failed`. A nonterminal `ImpossibleDisclosedValueError` produces no
candidate/tag, emits one feedback bit and advances; at the terminal stage it is
`decode_failed`. Other exceptions remain fail-closed.

Never reuse decoder state, metrics, partial sums, candidate labels or tag seed
between stages. Alice truth is allowed only for sampling, disclosed values,
tag construction and scoring—not in undisclosed operational metrics or
decisions.

## P6-C — Frozen accounting

For adaptive termination/exhaustion at one-based stage j and K1=K_j:

- key-dependent bits = `5*(K_j+140) + 64*tag_invocations`;
- public seed bits = `2623*tag_invocations`;
- feedback bits = `feedback_invocations`;
- public control = public seed bits + feedback bits.

Static fully invoked cost is `5*(112+140)+64 = 1324` bits. Decode rejection
does not create a tag. Persist and independently recount disclosure, tag and
feedback events. Verification union bound is
`min(1.0, total_tag_invocations*2^-64)`.

## P6-D — Tests before execution

Cover nested-set construction; level restart/no-state reuse; tag accept/advance;
nonterminal and terminal impossible-disclosure semantics; label assembly;
truth-isolation sentinels; accounting at every termination class; transcript
recount/tamper; paired block identity; no production invocation from tests; and
tiny deterministic injected cases. Run focused tests plus the 201-test accepted
NB-Polar predecessor suite. Test seeds must not use frozen streams or masters.

## P6-E — Pre-EXECUTE, command and attempt

Create a freeze document containing the exact three-line WSL command below and
an absent-target check. An independent reviewer-go must PASS Pre-EXECUTE before
the command is run. The reviewer checks OpenSpec/code/tests, frozen constants,
fresh streams, attempt point, truth boundary, exact integer leakage gate,
target-root absence and test results.

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.adaptive_l1 --n 256 --epsilon1 0.05 --profile strong --k1-levels 45 60 72 112 --k2 140 --seeds 2026091550 2026091551 2026091552 2026091553 2026091554 --blocks-per-seed 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate
```

The output root must be absent before execution and contain exactly five files
afterward: `frozen_plan.json`, `per_block_paired_outcomes.json`,
`transcript_accounting.json`, `aggregate_summary.json`, `report.md`. No rerun,
seed/K/model/threshold adjustment or partial replacement is allowed.

## P6-F — Hard gates and return labels

Integrity gates:

- 640/640 paired coverage; stream/block identity exact;
- result buckets mutually exclusive and exhaustive for both arms;
- disclosed D1 sets exactly nested and D2 disclosed once;
- operational provenance and truth isolation complete;
- undetected, nonfinite and resource_abort all zero;
- transcript recount mismatch zero;
- tag/feedback/public-control accounting and union bound exact;
- wall/RSS within frozen limits; attempt/seed accounting exact.

Scientific gates:

- static exact >=620/640;
- adaptive exact equals static exact;
- paired `adaptive_only=0` and `static_only=0`;
- exact integer leakage comparison
  `100*adaptive_total_key_dependent <= 85*static_total_key_dependent`.

All integrity and scientific gates true returns
`ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`. Integrity true but any scientific gate
false returns `ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED`. An integrity failure
returns `BLOCKED(<earliest frozen gate>)`. Report every outcome, paired cell,
termination histogram, mean/total disclosure, percentage saving, feedback/tag
count, per-stream breakdown and planning-only f; never merge undetected with
exact.

Before publishing the result, an independent reviewer-go performs Pre-RESULT
recalculation from the five artifacts. Its checks are trusted under AGENTS.md
section 4.1. Reviewer PASS/PASS_WITH_COMMENTS permits operator return but does
not grant main-thread acceptance.

## Stop and boundary rules

STOP on Pre-EXECUTE failure, target-root presence, test failure, command error,
resource limit, contract ambiguity or any integrity gate failure. Preserve the
failure root and return the raw failing command/gate; do not repair and rerun.

This gate is synthetic N=256 development evidence only. It is not real-channel
FER, reconciliation efficiency, key rate, qualification or promotion. No real
data/artifact, empirical construction, N>256, FWHT, soft APP, SCL, learned
policy, commit or push is authorized.
