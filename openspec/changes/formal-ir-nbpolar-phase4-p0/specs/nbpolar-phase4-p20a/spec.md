# Delta spec — P20A resource classification and endpoint instrumentation

## Resource exception semantics

An NB-Polar operational helper that catches decoder exceptions SHALL NOT map
`MemoryError` raised inside an L1 or L2 SC call to `decode_failed` or
`nonfinite`. It SHALL re-raise the exception so the owning runner's frozen
resource-stop path classifies it as a resource failure.

Injected tests SHALL cover both the L1 and L2 call sites and SHALL verify the
SC-call, disclosure, tag and checkpoint accounting applicable at the stop.

Ordinary accepted decoder failures and numerical-nonfinite failures SHALL keep
their existing outcome precedence and evidence semantics.

## Layer endpoint semantics

Future two-layer mechanism and feasibility runners SHALL distinguish at least:

- L1 exact;
- hard-candidate-conditioned L2 exact;
- true-L1 oracle-conditioned L2 exact;
- operational complete-pair exact.

An oracle arm that inserts true L1 into the final label SHALL NOT be described
as symmetric with an operational complete-pair endpoint. A paired count between
those arms SHALL NOT be labelled a strict hard-L1-induced L2-error count unless
the two L2 endpoints were recorded separately.

## Scope

P20A SHALL use injected data and temporary roots only. It SHALL NOT read a
protected artifact, execute a scientific gate, rewrite historical evidence,
or change the field, transform, SC arithmetic, prior, floor, construction,
disclosure, verification tag or scientific status.

