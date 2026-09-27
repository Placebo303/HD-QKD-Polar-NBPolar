# op-fix-n1024-alloc — execution transcript (Tier X, non-claim)

Probe root: `workspace/probes/op-fix-n1024-alloc/`. Predecessor: `workspace/probes/op-peak-refine/`
(runner architecture) + `workspace/probes/op-n32k-ratio/` (label-keyed multi-total POINTS
architecture, reused here so aggregation is keyed by (total,k1,k2), never by k1 alone).

## 0. Confirmed defect (why this probe exists)
`workspace/op-n32k-ratio-packet/FOCUSED_REVIEW.md` Part 2 and
`workspace/probes/op-n32k-ratio/review_scratch/check_table_sign.py` show that
`op-peak-refine/run.py:148,156` and `op-n32k-ratio/run.py:157,165` build
`table = pmf[(np.arange(Q)[:, None] - np.arange(Q)[None, :]) % Q]`, i.e.
`table[a,b] = pmf[(a-b)%Q]`, while the generative model is `y=(x+delta)%Q` with
Alice=x, Bob=y, so the decoder contract (`table[a,b] = P(Bob=b|Alice=a)`)
requires `table[a,b] = pmf[(b-a)%Q]`. Both runners fed the decoder the
mirror-image channel. Same bug in `Wmat` (Bhattacharyya/Z construction input).
Review's small-N check: corrected table gives genie H1+H2 = 0.9356 at N=1024
(MC=48, seed 99001) vs channel H=0.93183; as-coded gives 1.3946 there.

## 1. Heartbeat check
- `date` = Sun Sep 27 12:49:18 2026 (local); `workspace/overnight_state_20260927.md`
  `last_heartbeat` = 2026-09-27 05:05 -> ~7h44m old, not within 6 min -> no active-tick
  collision -> proceed per the heartbeat-collision check this packet was scoped to.
- Note for the record (not a blocker under this check's scope): that file also carries a
  prior-tick standing instruction ("do not create any new probe... total probes tonight = 6,
  capped") tied to an 08:00 stop boundary already ~4h49m in the past. This is a new daytime
  session with fresh, explicit PI authorization for these two specifically-named probe IDs
  (distinct from the capped overnight sequence); flagged to the main thread/PI in the operator
  return rather than treated as a block, since the heartbeat-collision check was the only
  condition this packet's procedure named.

## 2. Root cause verification (no library edit; runner-local fix only)
- Confirmed the two buggy lines exist verbatim at `op-peak-refine/run.py:148` (`table`) and
  `:156` (`Wmat`), and `op-n32k-ratio/run.py:157`/`:165`.
- `comparison_bench/formal_ir/nbpolar/two_layer.py`, `prior.py`, `sc.py` are untouched;
  the fix is entirely inside this probe's own standalone `run.py` (inherited pattern from
  predecessors, which build the circulant inline rather than importing a shared helper).

## 3. Grid (frozen before prereg)
H = 0.9318300074841255 bits/symbol, H*N = 954.1939276637445 (N=1024); total = round(f*H*N/5);
k1 = round(share*total); k2 = total - k1.

| label | total | f_book | k1 | k2 | k1 share |
|---|---|---|---|---|---|
| T248_k1_12_k2_236 | 248 | 1.2995261907 | 12 | 236 | 0.047 |
| T248_k1_22_k2_226 | 248 | 1.2995261907 | 22 | 226 | 0.09 |
| T248_k1_35_k2_213 | 248 | 1.2995261907 | 35 | 213 | 0.14 |
| T248_k1_50_k2_198 | 248 | 1.2995261907 | 50 | 198 | 0.20 |
| T248_k1_74_k2_174 | 248 | 1.2995261907 | 74 | 174 | 0.30 |
| T305_k1_14_k2_291 | 305 | 1.5982076136 | 14 | 291 | 0.047 |
| T305_k1_27_k2_278 | 305 | 1.5982076136 | 27 | 278 | 0.09 |
| T305_k1_43_k2_262 | 305 | 1.5982076136 | 43 | 262 | 0.14 |
| T305_k1_61_k2_244 | 305 | 1.5982076136 | 61 | 244 | 0.20 |
| T305_k1_92_k2_213 | 305 | 1.5982076136 | 92 | 213 | 0.30 |
| T382_k1_18_k2_364 | 382 | 2.0016895357 | 18 | 364 | 0.047 |
| T382_k1_34_k2_348 | 382 | 2.0016895357 | 34 | 348 | 0.09 |
| T382_k1_53_k2_329 | 382 | 2.0016895357 | 53 | 329 | 0.14 |
| T382_k1_76_k2_306 | 382 | 2.0016895357 | 76 | 306 | 0.20 |
| T382_k1_115_k2_267 | 382 | 2.0016895357 | 115 | 267 | 0.30 |

Cross-checked independently via `wsl.exe -e sh -lc 'python3 -c "..."'` arithmetic (round(f*HN/5),
round(share*total)) before authoring `run.py`; all 15 values match.

## 4. Pre-launch checks (2026-09-27 ~12:55 local)
- (a) Genie design sanity: `workspace/probes/op-fix-n1024-alloc/prelaunch_check.py`
  (scratch, not a result) reproduces the exact design pass (N=1024, design_seed=2026092600,
  DESIGN_MC=128, sign-corrected table) that `run.py` will run. Result: H1=0.0940, H2=0.8377,
  sum=0.9317, channel H=0.9318300075, |diff|=0.0002 < 0.05 -> PASS. wall=38.2s.
- (b) AST `%`-format check on `run.py`: 7 format expressions, 0 placeholder/argument
  mismatches -> PASS.
- (c) Aggregation keyed by `f_label` (encodes total,k1,k2), never by `k1` alone (`points[].
  per_seed` filter and `per_label_op`/`per_label_or` dicts, mirroring op-n32k-ratio's
  reviewed-PASS pattern); all 15 labels and all 15 (total,k1,k2) tuples verified distinct by
  inspection of the `POINTS` tuple.
- (d) Descriptive strings/numbers checked by direct authorship against the frozen grid above
  (no mechanical derivation from a differently-parameterized predecessor string, unlike the
  overnight session's incident #3-#5); `deviations_from_plan_A_rows`, `single_factor`,
  `a3_split_rule` all reference the actual 15-point/3-total grid and the sign fix.
- `results.json` ABSENT at prereg-freeze time (verified by `ls`).

## 5. Launch
- Launched 2026-09-27T12:58:24+08:00 (background task bchyqyjtb), prereg C command verbatim,
  stdout -> `workspace/probes/op-fix-n1024-alloc/run_stdout.log`.
- Completion: process exit 0 at ~2026-09-27T13:02+08:00; stdout `WROTE .../results.json`,
  `STATUS ok WITHIN True CELLS {'expected': 30, 'completed': 30} WALL 261.503`. reruns=0; no
  execution_error record.

## 6. Result record (descriptive, Tier X, non-claim)
`workspace/probes/op-fix-n1024-alloc/results.json`: status ok, within_budget true,
stop_rules_triggered [], wall 261.503 s (design 38.7 s for 128 samples; 30 cells advancing
~7.3 s each), peak RSS 216,842,240 B (~0.20 GiB).
Design (sign-corrected): H1=0.093972, H2=0.837707, sum=0.931679 vs channel H=0.9318300075
(|diff|=0.00015) -- matches the pre-launch sanity check almost exactly (design_seed and
DESIGN_MC identical), confirming the fix is active in the actual run, not just the scratch check.

| total | f_book | k1 | k2 | k1 share | op exact/32 | oracle exact/32 | op verify_failed | undetected | decode_failed | resource_abort |
|---|---|---|---|---|---|---|---|---|---|---|
| 248 | 1.2995 | 12  | 236 | 0.047 | 0  | 27 | 32 | 0 | 0 | 0 |
| 248 | 1.2995 | 22  | 226 | 0.09  | 8  | 22 | 24 | 0 | 0 | 0 |
| 248 | 1.2995 | 35  | 213 | 0.14  | 7  | 12 | 25 | 0 | 0 | 0 |
| 248 | 1.2995 | 50  | 198 | 0.20  | 1  | 2  | 31 | 0 | 0 | 0 |
| 248 | 1.2995 | 74  | 174 | 0.30  | 0  | 0  | 32 | 0 | 0 | 0 |
| 305 | 1.5982 | 14  | 291 | 0.047 | 0  | 32 | 32 | 0 | 0 | 0 |
| 305 | 1.5982 | 27  | 278 | 0.09  | 12 | 32 | 20 | 0 | 0 | 0 |
| 305 | 1.5982 | 43  | 262 | 0.14  | 26 | 32 | 6  | 0 | 0 | 0 |
| 305 | 1.5982 | 61  | 244 | 0.20  | 29 | 29 | 3  | 0 | 0 | 0 |
| 305 | 1.5982 | 92  | 213 | 0.30  | 12 | 12 | 20 | 0 | 0 | 0 |
| 382 | 2.0017 | 18  | 364 | 0.047 | 3  | 32 | 29 | 0 | 0 | 0 |
| 382 | 2.0017 | 34  | 348 | 0.09  | 19 | 32 | 13 | 0 | 0 | 0 |
| 382 | 2.0017 | 53  | 329 | 0.14  | 30 | 32 | 2  | 0 | 0 | 0 |
| 382 | 2.0017 | 76  | 306 | 0.20  | 32 | 32 | 0  | 0 | 0 | 0 |
| 382 | 2.0017 | 115 | 267 | 0.30  | 32 | 32 | 0  | 0 | 0 | 0 |

Totals: operational {exact: 211, undetected: 0, verify_failed: 269, decode_failed: 0,
resource_abort: 0}; oracle {exact: 360, undetected: 0, verify_failed: 120, decode_failed: 0,
resource_abort: 0}. `undetected` is genuinely 0 everywhere (isolated, never merged into
success); every per-point breakdown above shows the same isolation. kdb observed
{1304, 1589, 1974} = disclosed+64 for the three totals (1240/1525/1910), correct.

Descriptive observation (non-claim): unlike the mirror-channel predecessors (0/16 or
near-0 everywhere), the sign-corrected decoder achieves 32/32 operational exact at the two
highest-total, highest-k1-share points (T382 k1=76 and k1=115), and a monotonic-looking rise
in op-exact with increasing total at fixed low-to-mid shares. This is consistent with the
FOCUSED_REVIEW.md diagnosis that the mirror-channel bug (not a genuine ~1.6-bit two-layer
disclosure floor) explained the predecessors' uniform failure.
