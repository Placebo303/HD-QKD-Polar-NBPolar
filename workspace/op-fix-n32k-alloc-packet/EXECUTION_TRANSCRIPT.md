# op-fix-n32k-alloc — execution transcript (Tier X, non-claim)

Probe root: `workspace/probes/op-fix-n32k-alloc/`. Predecessor: `workspace/probes/op-n32k-ratio/`
(runner + prereg + label-keyed POINTS architecture, inherited unchanged except the sign fix,
grid, seeds and output root).

## 0. Confirmed defect (same as op-fix-n1024-alloc)
Same sign bug as documented in `workspace/op-fix-n1024-alloc-packet/EXECUTION_TRANSCRIPT.md` §0
and `workspace/op-n32k-ratio-packet/FOCUSED_REVIEW.md` Part 2: `op-n32k-ratio/run.py:157,165`
build `table[a,b] = pmf[(a-b)%Q]` / `Wmat[a,b] = pmf[(a-b)%Q]` (mirror channel) instead of the
correct `pmf[(b-a)%Q]`. Fixed identically here.

## 1. Heartbeat check
- Reused the same-session heartbeat check from op-fix-n1024-alloc (no new tick boundary crossed
  between the two launches); see that packet's EXECUTION_TRANSCRIPT.md §1 for the full note,
  including the flagged-not-blocking overnight-cap/stop-time observation.
- Launch-ordering gate: this probe is launched only after op-fix-n1024-alloc's run process has
  exited (see §5).

## 2. Grid (frozen before prereg)
H = 0.9318300074841255 bits/symbol, H*N = 30534.205685239824 (N=32768); total = round(f*H*N/5);
k1 = round(share*total); k2 = total - k1.

| label | total | f_book | k1 | k2 | k1 share |
|---|---|---|---|---|---|
| T7023_k1_329_k2_6694 | 7023 | 1.1500217285 | 329 | 6694 | 0.0469 |
| T7023_k1_632_k2_6391 | 7023 | 1.1500217285 | 632 | 6391 | 0.0900 |
| T7023_k1_983_k2_6040 | 7023 | 1.1500217285 | 983 | 6040 | 0.1400 |
| T7023_k1_1405_k2_5618 | 7023 | 1.1500217285 | 1405 | 5618 | 0.2000 |
| T7939_k1_372_k2_7567 | 7939 | 1.3000174430 | 372 | 7567 | 0.0469 |
| T7939_k1_715_k2_7224 | 7939 | 1.3000174430 | 715 | 7224 | 0.0901 |
| T7939_k1_1111_k2_6828 | 7939 | 1.3000174430 | 1111 | 6828 | 0.1399 |
| T7939_k1_1588_k2_6351 | 7939 | 1.3000174430 | 1588 | 6351 | 0.2000 |

The T7939 row is numerically identical to op-n32k-ratio's own T7939 row (same H, same rounding
rule); only the sign-fixed `table`/`Wmat` and the new seeds differ for those 4 points.

## 3. Pre-launch checks (2026-09-27 ~12:55 local)
- (a) Genie design sanity: reused the shared N=1024 quick check from
  `workspace/probes/op-fix-n1024-alloc/prelaunch_check.py` per the freeze's explicit allowance
  ("use the design pass output or a quick N=256/1024 check"); result H1+H2=0.9317 vs H=0.93183,
  |diff|=0.0002 < 0.05 -> PASS. The full N=32768/DESIGN_MC=64 design pass is not separately
  pre-checked (it is the run itself); this mirrors the reviewed op-n32k-ratio predecessor's own
  budget-driven choice not to re-run a full-N sanity pass outside the timed run.
- (b) AST `%`-format check on `run.py`: 7 format expressions, 0 placeholder/argument
  mismatches -> PASS.
- (c) Aggregation keyed by `f_label` (encodes total,k1,k2), never by `k1` alone; all 8 labels
  and all 8 (total,k1,k2) tuples verified distinct by inspection of the `POINTS` tuple
  (identical pattern to the reviewed-PASS op-n32k-ratio predecessor).
- (d) Descriptive strings/numbers checked against the frozen 2-total x 4-share grid above;
  `deviations_from_plan_A_rows` explicitly states DESIGN_MC/BLOCKS/design_seed are unchanged
  from op-n32k-ratio and names the sign fix as the primary semantic delta.
- `results.json` ABSENT at prereg-freeze time (verified by `ls`).

## 4. Launch
- op-fix-n1024-alloc completed 2026-09-27T13:02+08:00 with status ok (see its own packet) ->
  launch gate satisfied.
- Launched 2026-09-27T13:04+08:00 (background task bcergurmx), prereg C command verbatim,
  stdout -> `workspace/probes/op-fix-n32k-alloc/run_stdout.log`.
- Completion: process exit 0 at ~2026-09-27T14:00+08:00; stdout `WROTE .../results.json`,
  `STATUS ok WITHIN True CELLS {'expected': 16, 'completed': 16} WALL 3481.066`. reruns=0; no
  execution_error record.

## 5. Result record (descriptive, Tier X, non-claim)
`workspace/probes/op-fix-n32k-alloc/results.json`: status ok, within_budget true,
stop_rules_triggered [], wall 3481.066 s (design 860.1 s for 64 samples; 16 cells advancing
~164 s each), peak RSS 1,208,664,064 B (~1.13 GiB).
Design (sign-corrected): H1=0.094263, H2=0.837366, sum=0.931629 vs channel H=0.9318300075
(|diff|=0.00020) -- matches the shared N=1024 pre-launch sanity check closely and is
essentially identical to op-fix-n1024-alloc's own in-run design sum (0.931679), confirming the
fix is active and N-stable at N=32768 too (unlike the as-coded mirror-channel design sum, which
FOCUSED_REVIEW.md showed drifting upward with N: 1.336(N=256)->1.395(N=1024)->1.531(N=32768,
op-n32k-ratio's actual measurement)).

| total | f_book | k1 | k2 | k1 share | op exact/16 | oracle exact/16 | op verify_failed | undetected | decode_failed | resource_abort |
|---|---|---|---|---|---|---|---|---|---|---|
| 7023 | 1.1500 | 329  | 6694 | 0.0469 | 0  | 12 | 16 | 0 | 0 | 0 |
| 7023 | 1.1500 | 632  | 6391 | 0.0900 | 0  | 2  | 16 | 0 | 0 | 0 |
| 7023 | 1.1500 | 983  | 6040 | 0.1400 | 0  | 0  | 16 | 0 | 0 | 0 |
| 7023 | 1.1500 | 1405 | 5618 | 0.2000 | 0  | 0  | 16 | 0 | 0 | 0 |
| 7939 | 1.3000 | 372  | 7567 | 0.0469 | 0  | 16 | 16 | 0 | 0 | 0 |
| 7939 | 1.3000 | 715  | 7224 | 0.0901 | 0  | 16 | 16 | 0 | 0 | 0 |
| 7939 | 1.3000 | 1111 | 6828 | 0.1399 | 13 | 13 | 3  | 0 | 0 | 0 |
| 7939 | 1.3000 | 1588 | 6351 | 0.2000 | 2  | 2  | 14 | 0 | 0 | 0 |

Totals: operational {exact: 15, undetected: 0, verify_failed: 113, decode_failed: 0,
resource_abort: 0}; oracle {exact: 61, undetected: 0, verify_failed: 67, decode_failed: 0,
resource_abort: 0}. `undetected` is genuinely 0 everywhere (isolated, never merged into
success); every per-point breakdown above shows the same isolation. kdb observed
{35179, 39759} = disclosed+64 for the two totals (35115/39695), correct.

Descriptive comparison to op-n32k-ratio (non-claim): op-n32k-ratio's T7939 row (identical
k1/k2 grid, mirror-channel table) measured 0/16 operational exact at all four points. This
probe's sign-corrected T7939 row measures 0/16, 0/16, **13/16**, 2/16 at the same four
(k1,k2) -- a sharp, non-monotonic peak at k1=1111 (share 0.14) that does not exist in the
mirror-channel predecessor's flat-zero result, consistent with FOCUSED_REVIEW.md's diagnosis
that the predecessor's uniform failure was a sign-bug artifact rather than a genuine ~1.6-bit
two-layer disclosure floor at this scale.
