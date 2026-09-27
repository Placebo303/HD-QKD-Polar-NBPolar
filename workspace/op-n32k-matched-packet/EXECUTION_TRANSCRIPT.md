# op-n32k-matched — execution transcript (Tier X, non-claim)

Probe root: `workspace/probes/op-n32k-matched/`. Predecessor in this session:
`workspace/probes/op-n32k-fine-f4/` (probe A1; runner architecture inherited unchanged except
channel, design_seed, grid, seeds, output root, and budget).

## 0. Motivation
Probe A1 (`op-n32k-fine-f4`) probes the k1-share optimum on the parametric F4@q1024 channel at
f_book in {1.20,1.25}. This probe (A2) asks the same allocation question on a channel matched to
real data: delta pmf taken from the real CAL32 G1R2 circular triple
(`.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/G1R2_ADJUDICATION.md`,
q0/q+1/q-1/q_rest = 0.7562/0.2419/0.0018/0, task-frozen 4-decimal values, renormalized to sum 1
since the raw sum is 0.9999), at f_book in {1.15,1.20,1.30} x k1 share in {0.02,0.0469,0.09,0.14}.

## 1. Source value precision note
The source adjudication file's exact circular-triple figures are
q0=0.7562255859375, q+1=0.241943359375, q-1=0.0018310546875, q_rest=0 (these sum to exactly
1.0, no renormalization needed at that precision). The task packet explicitly froze the rounded
4-decimal values (0.7562/0.2419/0.0018) and explicitly instructed renormalizing their 0.9999
raw sum. Implemented exactly as frozen in the task (not substituted with the source file's
fuller precision) -- recorded as an observation in `STATUS.yaml`, not changed.

## 2. Grid (frozen before prereg)
H = 0.8165136251021449 bits/symbol (G1R2-matched@q1024; matches the freeze's expectation of
approx 0.8166 to within rounding of the task-frozen 4-decimal channel values), H*N =
26755.518467347083 (N=32768); total = round(f*H*N/5); k1 = round(share*total); k2 = total - k1.

| label | total | f_book_actual | k1 | k2 | k1 share (actual) |
|---|---|---|---|---|---|
| T6154_k1_123_k2_6031 | 6154 | 1.15004 | 123 | 6031 | 0.01999 |
| T6154_k1_289_k2_5865 | 6154 | 1.15004 | 289 | 5865 | 0.04696 |
| T6154_k1_554_k2_5600 | 6154 | 1.15004 | 554 | 5600 | 0.09002 |
| T6154_k1_862_k2_5292 | 6154 | 1.15004 | 862 | 5292 | 0.14007 |
| T6421_k1_128_k2_6293 | 6421 | 1.19994 | 128 | 6293 | 0.01993 |
| T6421_k1_301_k2_6120 | 6421 | 1.19994 | 301 | 6120 | 0.04688 |
| T6421_k1_578_k2_5843 | 6421 | 1.19994 | 578 | 5843 | 0.09002 |
| T6421_k1_899_k2_5522 | 6421 | 1.19994 | 899 | 5522 | 0.14001 |
| T6956_k1_139_k2_6817 | 6956 | 1.29992 | 139 | 6817 | 0.01998 |
| T6956_k1_326_k2_6630 | 6956 | 1.29992 | 326 | 6630 | 0.04687 |
| T6956_k1_626_k2_6330 | 6956 | 1.29992 | 626 | 6330 | 0.08999 |
| T6956_k1_974_k2_5982 | 6956 | 1.29992 | 974 | 5982 | 0.14002 |

## 3. Pre-launch checks
- (a) Design H1+H2 sanity: baked into `run.py` as a full in-run post-design assertion
  (`|H1.mean()+H2.mean()-H| <= 0.01`). This is a genuinely NEW design (new design_seed, channel
  changed vs op-n32k-fine-f4), not reused-equivalent, so there is no predecessor design-pass
  measurement to point to in advance; the assertion is the run's own gate. If violated, `run.py`
  returns status `design_sanity_fail` with no grid execution.
- (b) AST `%`-format check on `run.py`: 10 format expressions, 0 placeholder/argument
  mismatches -> PASS.
- (c) Aggregation keyed by `f_label` (encodes total,k1,k2), never by `k1` alone; all 12 labels
  and all 12 (total,k1,k2) tuples are distinct by construction.
- (d) Descriptive strings/numbers checked against the frozen 3-total x 4-share grid above;
  `deviations_from_plan_A_rows` names the channel change and new design_seed as the primary
  deltas.
- Zero-probability cells: 1021 of 1024 delta offsets carry exactly zero mass. `run.py`'s
  `matched_pmf()` asserts the constructed array sums to exactly 1.0; the existing
  `where`-guarded log/exp handling (already used for F4's near-zero residual mass) is reused
  as-is for these exact zeros; no floor was invented. `run.py` compiles cleanly
  (`compile()` check passed) with this pmf construction.
- `results.json` ABSENT at prereg-freeze time (verified by `ls`).
- Timing decision (recorded before freeze, per task instruction): estimate = design(~860s,
  same DESIGN_MC=64/N=32768 as predecessors) + 192 blocks * ~21s (A1's per-block time) =
  860 + 4032 = 4892s < 6000s budget (~18% margin). Estimate does NOT exceed budget -> full
  2 seeds x 8 blocks/point (16/point, 192 total) KEPT; no reduction to 2 seeds x 4 blocks.

## 4. Launch gate
- Probe A1 (`op-n32k-fine-f4`) completed 2026-09-27T15:14 local, status ok, 12/12 cells,
  wall 2820.295s -> launch gate satisfied. `results.json` re-verified ABSENT on
  `op-n32k-matched/` immediately before launch (`ls` at 15:16:41).
- Launched 2026-09-27T15:16:41 local (host `date`) via Bash-tool background command
  (task id `b0kywmvda`), no explicit `cd` (relies on the auto-mapped WSL cwd, same fix as
  op-n32k-fine-f4 attempt 2), stdout -> `workspace/probes/op-n32k-matched/run_stdout.log`.
  Confirmed alive via `ps` at 15:17:21 (PID 1304555, 98.7% CPU, RSS 343 MB).
- Completion: background task notified completed (exit code 0) at 2026-09-27T15:59 local.
  stdout: matched pmf p0=0.7562756275627562 p_plus1=0.0018001800180018
  p_minus1=0.24192419241924193 zero_cells=1021; `A3 MC genie design samples=64/64
  complete=True wall=446.718`; design sanity `H1+H2=0.816546 vs H=0.816514 diff=0.000033
  pass=True`; 24 cell lines; final line `WROTE .../results.json` / `STATUS ok WITHIN True
  CELLS {'expected': 24, 'completed': 24} WALL 2520.398`. reruns=0; no execution_error record.

## 5. Result record (descriptive, Tier X, non-claim)
`workspace/probes/op-n32k-matched/results.json`: status ok, within_budget true,
stop_rules_triggered [], wall 2520.398 s (design 446.718 s for 64 samples -- notably faster
than op-n32k-fine-f4's 856.6 s despite identical DESIGN_MC/N, plausibly because this channel's
much lower entropy concentrates the SC metric computation; 24 cells advancing over the
remaining ~2074 s), peak RSS 1,198,931,968 B (~1.12 GiB).

| total | f_book | k1 | k2 | k1 share | op exact/16 | oracle exact/16 | op verify_failed | op decode_failed | undetected | resource_abort |
|---|---|---|---|---|---|---|---|---|---|---|
| 6154 | 1.15004 | 123 | 6031 | 0.02   | 0  | 5  | 16 | 0  | 0 | 0 |
| 6154 | 1.15004 | 289 | 5865 | 0.0469 | 1  | 1  | 11 | 4  | 0 | 0 |
| 6154 | 1.15004 | 554 | 5600 | 0.09   | 0  | 0  | 16 | 0  | 0 | 0 |
| 6154 | 1.15004 | 862 | 5292 | 0.14   | 0  | 0  | 16 | 0  | 0 | 0 |
| 6421 | 1.19994 | 128 | 6293 | 0.02   | 0  | 14 | 16 | 0  | 0 | 0 |
| 6421 | 1.19994 | 301 | 6120 | 0.0469 | 10 | 13 | 2  | 4  | 0 | 0 |
| 6421 | 1.19994 | 578 | 5843 | 0.09   | 0  | 0  | 16 | 0  | 0 | 0 |
| 6421 | 1.19994 | 899 | 5522 | 0.14   | 0  | 0  | 16 | 0  | 0 | 0 |
| 6956 | 1.29992 | 139 | 6817 | 0.02   | 0  | 16 | 2  | 14 | 0 | 0 |
| 6956 | 1.29992 | 326 | 6630 | 0.0469 | 13 | 16 | 0  | 3  | 0 | 0 |
| 6956 | 1.29992 | 626 | 6330 | 0.09   | 14 | 14 | 2  | 0  | 0 | 0 |
| 6956 | 1.29992 | 974 | 5982 | 0.14   | 4  | 4  | 12 | 0  | 0 | 0 |

Totals: operational {exact: 42, undetected: 0, verify_failed: 125, decode_failed: 25,
resource_abort: 0}; oracle {exact: 83, undetected: 0, verify_failed: 109, decode_failed: 0,
resource_abort: 0}. `undetected` is genuinely 0 everywhere (isolated, never merged into
success); every per-point breakdown shows the same isolation. kdb observed
{1445, 1505, 1630, 30834, 32169, 34780, 34844}: the three small values equal 5*k1 exactly for
the three points carrying decode_failed at low-k1 shares (k1=289,301,326 -> 1445,1505,1630),
consistent with layer-1-only failure before layer-2/tag disclosure; 30834/32169/34844 are the
three totals' disclosed+64 (tag-inclusive) values; 34780 is T6956's disclosed total WITHOUT the
+64 tag, consistent with T6956_k1_139's 14 decode_failed cases failing after full two-layer
disclosure but without reaching the tag. Descriptive only; inherited kdb semantics unmodified.

Descriptive comparison to op-n32k-fine-f4 (probe A1, F4 channel, non-claim): on this real-data-
matched channel the k1-share optimum shifts markedly LOWER than on F4 as f_book rises, and the
peak is stronger: f_book=1.15 is all-zero-or-near-zero across all four shares (best 1/16 at
share 0.0469); f_book=1.20 peaks at share 0.0469 (10/16, vs F4's best-of-grid 2/16 at
share 0.11 for the same nominal f_book); f_book=1.30 peaks at share 0.09 (14/16 = 87.5%, the
single strongest point across BOTH probes in this session, vs F4's 13/16 at share 0.14/
f_book=1.30 from op-fix-n32k-alloc, or A1's own best of 10/16 at f_book=1.25/share=0.14).
The matched channel also shows a distinct failure mode absent on F4: 25 operational
decode_failed events concentrated at 4 of 12 points (F4 probes showed decode_failed=0
throughout this session), plausibly related to the near-deterministic (1021-zero-cell) pmf
shape; no threshold, significance, or operating-point claim is made for any point.
