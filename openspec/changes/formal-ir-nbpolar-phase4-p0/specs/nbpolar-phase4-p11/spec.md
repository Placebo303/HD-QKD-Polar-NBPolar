# NB-Polar Phase 4-P11 specification delta

Phase 4-P11 promotes the Tier-X X12 probe's bitwise-equivalent row chunking
into the accepted reference SC implementation as an allocation-only change,
then executes one frozen synthetic engineering gate proving semantic parity
and N=2^18 reachability. It changes decoder allocation only: the accepted
minus-node expression, dtype, reduction order, field tables, support,
tie-breaking, exception behavior, public `sc_decode` signature and all
result/provenance schemas remain stable. The claim scope is narrow: exact
equivalence between the default-512 chunked path and the unchunked golden
path plus a resource completion record at N=262144; it is not target-channel
FER, efficiency, key rate, scaling superiority, throughput, qualification or
promotion. Implementation tasks live in the companion P11 section of
`tasks.md`; status, acceptance and route disposition are owned by the main
thread, never by the implementing session. This document authorizes no
production behavior.

## Requirement: allocation-only `_minus_block` contract

The gate SHALL change only `_minus_block` allocation in
`formal_ir/nbpolar/sc.py`: retain the accepted per-row expression, float64
dtype and reduction order; add keyword-only `chunk_rows` with production
default exactly `512`; process contiguous row slices in original order, each
computing `first_slice[:, index] + second_slice[:, None, :]` followed by
`np.logaddexp.reduce(..., axis=2)`; apply the accepted `_normalize_rows`
once over the full assembled matrix. `chunk_rows=None` SHALL invoke the
original unchunked expression and exist only as the golden comparator for
tests and the gate. Explicit chunk sizes that are bool, non-integral or
nonpositive SHALL be rejected with a clear `TypeError`/`ValueError` before
allocation. FWHT, clipping, caching, reordered summation, dynamic-range
logic, approximation, environment configuration and any new public
`sc_decode` argument are forbidden. `sc_decode` SHALL keep calling
`_minus_block` with its unchanged public signature and schemas.

## Requirement: focused tests on injected data only

Focused tests SHALL use injected arrays with fresh test seeds and temporary
roots only, never artifact, evidence-root, raw, held-out, real, EVAL, tag or
production paths and never the gate seed for execution. Coverage SHALL be:
chunk sizes 32/128/512/2048 including default-is-512; row boundaries
1/31/32/33/127/128/129/511/512/513/2048; finite moderate/wide and exact
`-inf` support; exact array equality against `chunk_rows=None`; N=64/256
full-SC equality for moderate, wide, mixed support, known coordinates, the
X11-C3 pattern, impossible disclosure, near/exact ties and
invalid/nonfinite inputs with identical exception type and message; the
public `sc_decode` signature unchanged; invalid chunk sizes rejected
(bool/0/negative/float/str); and the no-production-invocation rule. The
focused file(s) AND the complete accepted 252-test NB-Polar predecessor
suite SHALL be green with the pinned interpreter and fresh basetemps.

## Requirement: frozen one-shot engineering gate

The gate SHALL use seed `2026091800`, NumPy float64, GF(32) primitive
polynomial 37 and alpha 2. Before execution the exact implementation, tests,
command, output schema, target absence and resource checks SHALL be frozen
in `P11_FREEZE.md` with an independent reviewer-go Pre-EXECUTE PASS. The
single scientific/engineering attempt SHALL be consumed at the first formal
`sc_decode` call; no artifact read is authorized or consumed. The one
execution SHALL perform: (1) the frozen injected semantic matrix from the
P11-03 scope for default 512 versus `chunk_rows=None`, requiring exact
equality/exception parity everywhere; (2) one paired N=65536 moderate
all-finite block, direct first then default-512, requiring exact `u_hat`,
`x_hat`, decision metrics/scores, status and provenance equality; (3) one
default-512 N=262144 moderate all-finite block requiring status `ok`,
finite outputs, no resource failure and process peak RSS below
`1,610,612,736` bytes (1.5 GiB). Planning targets decode wall `<= 120`
seconds and RSS `<= 1` GiB SHALL be recorded but not gated on; one draw
cannot discriminate timing variance, so no throughput superiority claim is
allowed. The complete command SHALL finish within its 600-second timeout
under `ulimit -v 2097152`. Any semantic mismatch, resource abort,
threshold miss, test/review failure or unexpected existing root SHALL
return the earliest `BLOCKED(<gate>)`; never rerun or retune.

## Requirement: frozen CLI, four-file output and bounded scope

The CLI SHALL require every argument — `--seed`, `--chunk-rows` and
`--out-dir` — with no production default, and SHALL refuse an existing
output root before the first `sc_decode`. The only output root
`.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/`
SHALL be absent before execution and SHALL contain exactly four compact
files (`frozen_plan.json`, `equivalence_records.json`,
`scaling_record.json`, `report.md`); input vectors, decisions, metrics,
decoded keys, raw arrays and artifacts SHALL NOT be persisted. The report
SHALL cover parameters, environment, every semantic comparison, exceptions,
large-N wall/RSS, attempt/seed accounting, gates and bounded wording. All
frozen gates true SHALL return `EXACT_CHUNKED_SC_CANDIDATE` (pending
main-thread acceptance); otherwise the earliest `BLOCKED(<gate>)`.
Forbidden: artifact/evidence-root/raw/held-out/real/EVAL access, official
prior seeds, tag/protocol execution, N>262144, FWHT/APP/SCL,
FER/efficiency/key-rate/qualification/promotion claims, old-root edits,
commit or push.

## Requirement: bounded claim and independent review

The only permitted conclusions are the registered candidate label and the
blocker return; a candidate means the default-512 allocation path is
bitwise-equivalent to the accepted unchunked reference everywhere in the
frozen matrix and completes the single N=262144 block within the frozen
resource envelope. It SHALL NOT be described as FER, efficiency, key-rate,
scaling, qualification or promotion evidence. An independent Pre-EXECUTE
review SHALL pass before the single attempt, and an independent Pre-RESULT
review SHALL recompute the recorded equivalence/resource facts before any
result or label is published; neither the run nor the implementing session
may accept its own work.
