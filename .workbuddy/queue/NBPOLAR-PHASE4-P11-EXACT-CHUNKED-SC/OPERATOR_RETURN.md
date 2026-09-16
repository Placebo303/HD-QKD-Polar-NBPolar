# P11 operator return — NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC (candidate, acceptance pending)

Packet: `NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC` (Tier-Y). This return is a
candidate record, not an acceptance. Main-thread acceptance is the next gate.

## Mission

Promote the X12 bitwise-equivalent row chunking into the accepted reference SC
as an allocation-only change, then run one frozen synthetic engineering gate
proving semantic parity and N=2^18 reachability.

## Contract diff summary

Allocation-only `_minus_block` promotion in
`comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py`: keyword-only
`chunk_rows` with production default exactly `512`; contiguous row slices in
original order each running the accepted
`first_slice[:, index] + second_slice[:, None, :]` +
`np.logaddexp.reduce(..., axis=2)` with the accepted `_normalize_rows` once
over the full assembled matrix; `chunk_rows=None` as the unchunked golden
comparator; bool/non-integral/nonpositive rejected with `TypeError`/`ValueError`
before allocation. `sc_decode` public signature unchanged; no FWHT, clipping,
caching, reordered summation, dynamic-range logic, approximation, or
environment configuration. New thin injected-data runner
`formal_ir/nbpolar/sc_chunked_gate.py` (required `--seed`/`--chunk-rows`/
`--out-dir`, absent-root refusal before the first `sc_decode`).

## Seed / environment

Seed `2026091800`; NumPy float64; GF(32) polynomial 37, alpha 2; pinned
interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(Python 3.12.3, NumPy 2.5.3). Single gate execution, exit 0,
wall_total 97.955511 s.

## Semantic totals (default-512 vs `None`)

- 33 primitive cells (11 rows × 3 kinds) all exact: exact, support, err 0.0,
  support parity — 33/33.
- 16 V0 invalid-input cases: all exception type+message parity — 16/16.
- N=64 full-SC 9 cases + N=256 full-SC 9 cases, all parity (moderate / wide /
  neginf / known25 / X11-C3 / C4-impossible / T5 ties): N=64 C4 U[3]=2 and
  N=256 C4 U[3]=12 `ImpossibleDisclosedValueError` parity — 18/18.

## N=65536 paired direct-first exact parity

Paired N=65536, direct-first then default-512: status ok, u_hat 0 mismatches,
x_hat 0 mismatches, metrics/scores err 0.0, provenance equal. Walls
direct 15.684 s / chunked 14.584 s are report-only (no throughput claim).

## N=262144 completion + RSS

Status ok, finite True. Decode wall 66.088411 s: report-only planning target
≤120 s met (report-only). Peak RSS 710504448 B: hard gate < 1610612736 B
(1.5 GiB) met (margin 900108288 B); report-only 1 GiB met
(margin 363237376 B). Hard vs report-only gates kept separate:
`large_n262144_completion` and `large_n262144_rss` are the only hard gates.

## Gates / label

`semantic_parity` True; `paired_n65536_exact` True;
`large_n262144_completion` True; `large_n262144_rss` True →
`EXACT_CHUNKED_SC_CANDIDATE` (pending main-thread acceptance).

## Consumption

Attempt 1/1 consumed at the first formal `sc_decode` in the frozen run;
0 artifact reads authorized/consumed (0/0). No rerun, seed/chunk/threshold
change, or retune.

## Reviews

- Independent Pre-EXECUTE: PASS. Partial-evidence fallback ratified
  (BLOCKED→four files with `None` for unreached records, exit 1; pre-decode
  refusal→nothing written, exit 2) — not taken (exit-0 full-evidence path).
  Non-blocking notes: consumption-point label naming carryover (ratified, 1/1
  count unaffected); additive exit 3 for unexpected exceptions (ratified).
- Independent Pre-RESULT: PASS_WITH_COMMENTS, all non-blocking (carried-over
  consumption-point label; stale STATUS lifecycle fields, fixed by this
  closeout). All numbers recomputed exactly from the four artifacts.

## Four-file inventory (`exact_chunked_sc_gate/`)

- `frozen_plan.json` — 2152 B
- `equivalence_records.json` — 23808 B
- `scaling_record.json` — 580 B
- `report.md` — 8018 B

Scalar-only; no input vectors, decisions, metrics, decoded keys, raw arrays,
or artifacts.

## Bounded scope

Synthetic injected-data engineering gate only: the default-512 allocation path
is bitwise-equivalent to the accepted unchunked reference everywhere in the
frozen matrix and completes the single N=262144 block within the frozen
resource envelope. This is not target-channel FER, efficiency, key-rate,
scaling, qualification, or promotion evidence. No throughput superiority claim
is allowed; one draw cannot discriminate timing variance; the 120 s / 1 GiB
values are report-only.

## Unrun stages / closeout

Unrun stages: none — main-thread acceptance remains. No commit/push performed;
no OpenSpec box checked; no code/artifact/old-root change by this closeout
(this closeout fixes STATUS lifecycle fields only).
