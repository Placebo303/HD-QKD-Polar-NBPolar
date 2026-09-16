# P5 implementation notes — NB-Polar Phase 4-P5 hard-conditioning penalty

Rev 1 (2026-09-13). Operator session notes for the freeze; evidence only, no
acceptance. Companion documents: `P5_FREEZE.md`, `TASK_PACKET.md`,
`AUTHORIZATION_PROMPT.md`, `X02_PROVENANCE_ADDENDUM.md`,
`docs/nbpolar/probes/X02_DEPENDENT_L2_POINT_SEARCH.md`.

## 1. What was built

One module
`comparison_bench/src/comparison_bench/formal_ir/nbpolar/penalty_gate.py` with:
the explicit dependent `[Alice,Bob]` table (`P(B|A) = Ph(B_high|high) *
Pl(B_low|low, high)` with the per-high-value profile kernel), the pre-decoder
`p2_maxdiff` computation and floor refusal, the explicit-RNG dependent block
sampler, the four-cell paired classifier, the exact-binomial one-sided lower
bound by monotone bisection, the 10 integrity gates, the frozen discriminator,
the five-file writer and the frozen CLI.  One focused test file
`comparison_bench/tests/test_nbpolar_penalty_gate.py` with 9 tests.  No accepted
module was modified.

## 2. Alternatives and decisions

1. **Reuse the accepted paired runner per block (packet instruction).**  Each
   block is one in-memory `two_layer.run_two_layer_block` call, so the
   operational/oracle arms, provenance, tags, truth-isolation sentinel and
   outcome taxonomy are exactly the accepted P4 semantics.  Only the statistic
   wrapper is new.  No decoder, construction, prior or protocol change.
2. **Table construction mirrors X02 literally.**  The X02 probe built the
   dependent table by assigning per-high-value blocks
   `ph[high, bh] * pl[al, bl]`; the P5 builder uses the same loops and asserts
   the column-sum deviation (`3.774758283725532e-15 <= 1e-12`) without ever
   renormalizing, so the derived `P2` and `p2_maxdiff` are the exact X02
   arithmetic.  Measured `p2_maxdiff = 0.34875000000000267`, bit-identical to
   X02's persisted value; closed form `0.36 * 31/32`.
3. **Refuse-to-decode guard as a testable helper.**  `require_p2_maxdiff` is a
   one-line fail-closed check; the runner calls it before the decoder loop.  The
   weak/medium profiles are computed by the same builder and are below the
   0.30 floor (0.11625 / 0.2325), so the guard is exercised by tests.
4. **Own literal transcript recount.**  The wrapper performs its own literal
   recount (parses the arm from the event id, sums event fields) instead of
   reusing `two_layer.recount_transcript`; it is independent of both the
   incremental accumulation and the accepted module's recount.  Events
   themselves come from the accepted `two_layer.block_events`.
5. **Bisection direction and edge cases.**  The tail `P[Bin(n,L) >= X]` is
   increasing in `L`; the first prototype had the direction inverted and was
   caught immediately by an equation-residual check.  Final residuals against an
   independent direct product-sum tail are `<= 3.5e-16` for X in
   {1,2,200,365,370,380}; small-n cross-checks agree within 1e-9.  Frozen edge
   handling: `X=0 -> 0.0`, `X=384 -> 0.05**(1/384)`.
6. **Shape guard for the candidate label.**  The discriminator booleans are
   exactly the three frozen conditions (`oracle_exact >= 365`,
   `operational_only == 0`, `L > 0.30`).  The `HARD_L1_CONDITIONING_PENALTY_
   CANDIDATE` label additionally requires `planned_pairs == 384`, so a small
   smoke run can never emit the candidate label; non-384 runs return
   NOT_CONFIRMED with `shape_is_frozen_384=false`.
7. **Internal wall budget as an optional keyword.**  The CLI has no budget flag;
   `total_wall_s` defaults to the frozen 3600 s and the budget-stop path
   (remaining blocks `resource_abort`, `resource_stop_fired=true`) is tested
   with a microsecond budget so the `resource_abort_zero` gate is real rather
   than vacuous.  The frozen command relies on the external
   `timeout 3600` / `ulimit -v 2097152` envelope.
8. **Attempt accounting is descriptive, not self-granting.**  The wrapper
   persists the frozen accounting record (`attempts_allowed=1`,
   `attempts_consumed_before=0`, `attempts_consumed_by_this_run=1`,
   `retries=0`) and gates on it; it never touches `STATUS.yaml` or any ledger.
   The attempt stays owned by the main thread and the operator return.
9. **`tl._abort_arm` reuse.**  The resource-abort sentinel arms reuse the
   accepted private helper (same pattern as the accepted P4 tests); no accepted
   module was edited.
10. **No adapter.**  As in P4, the accepted `IRMethod`/`FrameBatch` contract is
    the single-layer `low half constant zero` convention and does not admit this
    paired two-layer statistic without a schema change; the frozen command
    imports the module path directly.

## 3. Evidence

### 3.1 Frozen table and point (recomputed, decoder-free)

- strong `p2_maxdiff = 0.34875000000000267` (X02 reference: same value);
- column-sum deviation `3.774758283725532e-15 <= 1e-12`;
- literal formula oracle `p2[u1, 32*bh+bl, u2] == Pl_{e2(u1)}[u2, bl]` within
  `2.1e-15` over sampled coordinates;
- profile means exactly 0.20; weak/medium `p2_maxdiff` 0.11625 / 0.2325;
- `D1` (45) and `D2` (140) recomputed from `analytic_order`; the first X with
  `L > 0.30` is X=131.

### 3.2 Tests (pinned interpreter, `-q -p no:cacheprovider`)

```text
comparison_bench/tests/test_nbpolar_penalty_gate.py                     9 passed   (5.32 s)
comparison_bench/tests/test_nbpolar_*.py (all NB-Polar)               201 passed  (104.98 s)
```

The 9 focused tests cover: dependent table normalization + `p2_maxdiff` +
literal `P2` formula + floor refusal; sampler determinism and literal draw-order
equivalence; four-cell classifier and the structural `operational_only`
impossibility; exact lower bound vs independent direct product-sum bisection,
residuals, monotonicity and edge cases; integrity gates and failure paths
(truth-leak sentinel, budget abort, pre-decoder `p2_maxdiff` refusal); CLI and
runner refusals without decoder calls (existing root, refused seeds, wrong
profile/K/N/epsilon, duplicate seeds, missing flags); the tiny smoke five-file
scalar-only schema and accounting; frozen constants/seed sets/fresh test seeds;
forbidden-marker and import-time-effect scans.

### 3.3 CLI smoke (non-frozen seed, temp root, NOT the gate)

```text
python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.penalty_gate \
  --n 256 --epsilon1 0.05 --profile strong --k1 45 --k2 140 \
  --seeds 2026091486 --blocks-per-seed 2 --out-dir /tmp/opencode/p5_cli_smoke
exit 0; five files; integrity_all_pass=true; X=1;
L=0.00013356736655250473; outcome HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED
(2-pair shape, not the frozen 384 shape)

repeat call: exit 2 ("refusing to overwrite existing output root")
seed 2026091360: exit 2 ("banned"); profile weak: exit 2; refused roots absent
```

### 3.4 Seed and scope evidence

- `git grep` for 2026091470/2026091471/2026091472 (and the three masters
  2026101470..2026101472) over HEAD returns no matches; the gate seeds are
  unused.
- Real output root `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-
  PENALTY/paired_penalty_gate/` confirmed absent; `attempts_used: 0`; no gate
  run executed with the frozen seeds.
- No changes under `results/` or `comparison_bench/outputs_comparison/`; no
  sibling checkout write; existing evidence roots untouched; no commit or push.

## 4. Non-blocking notes for the carrier / reviewer

1. The frozen point is a single X02-screened operating point; the gate is not a
   sweep and does not estimate a rate region.
2. `operational_only` is expected to be exactly 0 by the structural argument in
   freeze §6, not merely by observation; the gate still records it.
3. The lower-bound threshold `L > 0.30` corresponds to X >= 131 at n=384; the
   X02 strong/45/140 point measured oracle exact 96/96 over three 32-block
   streams, so the discriminating quantity at the 384-pair shape is the
   operational penalty, not the oracle saturation.
4. The two-block CLI smoke produced one `oracle_only` pair, which exercises the
   paired classifier and the `X`/`L` path with real decoder calls in a temp
   root; it is development evidence only.
5. The `python -m` invocation may emit the accepted cosmetic `runpy`
   `RuntimeWarning` seen in the P4/P5/P6 modules; it is not an error.
