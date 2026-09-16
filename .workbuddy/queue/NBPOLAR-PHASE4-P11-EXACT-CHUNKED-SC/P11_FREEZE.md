# P11 freeze — exact chunked SC allocation gate (Wave-A implementation freeze)

Packet: `NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC` (Tier-Y). This document freezes
the implementation, tests, command, output schema, target absence, budgets
and attempt point for the Wave-C gate execution. It authorizes nothing; an
independent reviewer-go Pre-EXECUTE PASS is required before the first formal
`sc_decode`. The gate has NOT been run in this wave (attempts used: 0).

## 1. Frozen implementation contract (P11-02)

Only `_minus_block` allocation changed in
`comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py`:

- Accepted per-slice expression, float64 dtype and reduction order retained.
- Keyword-only `chunk_rows`, production default exactly `512`.
- Contiguous row slices in original order; each slice runs
  `first_slice[:, index] + second_slice[:, None, :]` then
  `np.logaddexp.reduce(..., axis=2)`; the accepted `_normalize_rows` is
  applied once over the full assembled matrix (never per-slice: a second
  normalization would not be bitwise-identical).
- `chunk_rows=None` is the original unchunked expression, golden comparator
  for tests/gate only.
- Explicit bool/non-integral/nonpositive sizes raise clear
  `TypeError`/`ValueError` before allocation.
- No FWHT, clipping, caching, reordered summation, dynamic-range logic,
  approximation, environment configuration, or new public `sc_decode`
  argument. `sc_decode` calls `_minus_block` with its unchanged public
  signature; all result/provenance schemas stable.

New thin runner `formal_ir/nbpolar/sc_chunked_gate.py` (no production
default; required `--seed`/`--chunk-rows`/`--out-dir`; absent-root refusal
before the first `sc_decode`) performs exactly P11-04 steps 1-3 and writes
exactly the four files of §4.

## 2. Seed, environment, and frozen command (P11-04/P11-06)

Seed `2026091800`; NumPy float64; GF(32) primitive polynomial 37, alpha 2.
Pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(Python 3.12.3, NumPy 2.5.3 at freeze time; Pre-EXECUTE reconfirms).

Exact verbatim three-line command (byte-equivalence with this file is a
Pre-EXECUTE check):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc_chunked_gate --seed 2026091800 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate
```

## 3. Gate steps, gates, and labels (P11-04/P11-05)

1. Frozen injected semantic matrix (P11-03 scope), default-512 vs
   `chunk_rows=None`: 33 primitive cells (rows
   1/31/32/33/127/128/129/511/512/513/2048 x moderate/wide/-inf-support),
   16 V0 validation cases, N=64/256 full-SC controls (F1 moderate, F2 wide,
   F3 mixed support, K4 25% known positive-support, C3 X11 pattern
   positive-support, C4 impossible-disclosure search, T5 exact/ramp/near
   ties). Requires exact equality/exception parity everywhere.
2. One paired N=65536 moderate all-finite block, direct(None) FIRST then
   default-512: exact `u_hat`, `x_hat`, decision metrics/scores, status and
   provenance equality.
3. One default-512 N=262144 moderate all-finite block: status `ok`, finite
   outputs, no resource failure, process peak RSS < 1610612736 bytes.

Frozen gates (in order): `semantic_parity`, `paired_n65536_exact`,
`large_n262144_completion`, `large_n262144_rss`. All true returns
`EXACT_CHUNKED_SC_CANDIDATE` (pending main-thread acceptance); otherwise the
earliest `BLOCKED(<gate>)`.

## 4. Absent root and four-file schema (P11-05)

Root `.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/`
is ABSENT at freeze time (verified §7) and must remain absent until the
authorized execution. Exactly four compact files: `frozen_plan.json`,
`equivalence_records.json`, `scaling_record.json`, `report.md` (params, env,
every comparison, exceptions, large-N wall/RSS, attempt/seed accounting,
gates, bounded wording; no input vectors, decisions, metrics, decoded keys,
raw arrays or artifacts).

## 5. Attempt accounting, consumption point, no-rerun rule

Attempts allowed 1; attempts used 0 at freeze time. The single attempt is
consumed at the first formal `sc_decode` call (step-1 N=64 F1_moderate
direct arm). No artifact read is authorized or consumed; no-reopen semantics
N/A because no artifact/content file is ever opened (all inputs are
RNG-injected from the frozen seed). After consumption: no repair, cleanup,
seed/chunk/threshold change, rerun or retune; STOP and preserve evidence on
any blocker or failed gate.

Test-vs-gate distinction: unit tests calling `_minus_block`/`sc_decode` on
injected tiny arrays (N<=256, fresh test seeds, temp roots) are REQUIRED
P11-03 tests and consume nothing. The attempt is the Wave-C frozen-command
run only. The frozen seed was never executed in this wave.

## 6. Budgets

`ulimit -v 2097152`; total timeout 600 s (command wrapper). Hard gates:
N=262144 completion + peak RSS < 1610612736 bytes (1.5 GiB), supported by
X12's 65.73 s / 754.6 MB cumulative-HWM observations (descriptive only).
Planning targets decode wall <= 120 s and RSS <= 1 GiB are RECORDED but not
gated on (one draw cannot discriminate timing variance); no throughput
superiority claim is allowed.

## 7. Forbidden paths and freeze-time verification

Forbidden: artifact/evidence-root/raw/held-out/real/EVAL access; official
prior seeds; tag/protocol execution; N>262144; FWHT/APP/SCL;
FER/efficiency/key-rate/qualification/promotion claims; old-root edits;
commit/push.

Verified at freeze time (2026-09-14, Wave-A):

- Gate root absent: `exact_chunked_sc_gate/` does not exist.
- NPZ never touched: the runner opens no data file (only
  `/proc/self/status` for RSS plus its own four output writes); no stat,
  load, or content open of any artifact path exists in the runner source.
- Frozen seed `2026091800` fresh: repo-wide grep finds it only in the P11
  runner source, the P11 focused tests (constant check + refusal-path use,
  never executed), the P11 OpenSpec delta, and this freeze directory.
- HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` unchanged by this wave;
  no commit or push performed (pre-existing unrelated worktree
  modifications preserved untouched).
- Frozen gate never run: no gate output exists; attempts used 0.
- Tests: 10/10 new P11 focused tests pass; full 262/262 (252 accepted
  predecessor + 10 new) green with the pinned interpreter and fresh
  basetemps.

## 8. Handoff

Next gate: independent reviewer-go Pre-EXECUTE review of this freeze
(command byte-equivalence, thresholds, seed, budgets, absent root, attempt
point), then Wave-C single execution. Pre-RESULT review must recompute the
recorded equivalence/resource facts before any return.
