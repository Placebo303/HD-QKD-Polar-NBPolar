# op-n32k-fine-f4 — execution transcript (Tier X, non-claim)

Probe root: `workspace/probes/op-n32k-fine-f4/`. Predecessor: `workspace/probes/op-fix-n32k-alloc/`
(reviewed PASS, sign-fixed; runner architecture inherited unchanged except the grid, seeds,
output root, and a new post-design sanity assertion).

## 0. Motivation
Predecessor `op-fix-n32k-alloc` found, on F4@q1024/N=32768 with sign-corrected table/Wmat: at
f_book=1.30 (T7939), op exact/16 by k1 share 0.0469/0.0901/0.1399/0.2000 was 0/0/13/2 -- a sharp,
non-monotonic peak near share≈0.14; at f_book=1.15 (T7023), all four shares measured 0/16. This
probe brackets the peak more finely (shares 0.11/0.14/0.17) at two new totals (f_book≈1.20/1.25)
to see whether SC can reach a usable exact-decode rate between the 1.15 (all-zero) and 1.30
(peaked) points.

## 1. Heartbeat check
- `workspace/overnight_state_20260927.md` last_heartbeat = 2026-09-27 05:05 (verified against
  file mtime per that file's own incident note); real current time at operator start = 2026-09-27
  14:13 (`date` command). Gap ≈ 9h08m, far outside the 6-minute abort window ⇒ not aborted.
- The overnight 6-probe cap in that file applied to the finished overnight window (stopped
  2026-09-27 08:00); this session carries explicit PI authorization for two new Tier-X probes
  per the task packet, so the cap does not block this launch.

## 2. Grid (frozen before prereg)
H = 0.9318300074841255 bits/symbol (F4@q1024, unchanged), H*N = 30534.205685239824 (N=32768);
total = round(f*H*N/5); k1 = round(share*total); k2 = total - k1.

| label | total | f_book_actual | k1 | k2 | k1 share (actual) |
|---|---|---|---|---|---|
| T7328_k1_806_k2_6522 | 7328 | 1.19997 | 806 | 6522 | 0.10999 |
| T7328_k1_1026_k2_6302 | 7328 | 1.19997 | 1026 | 6302 | 0.14001 |
| T7328_k1_1246_k2_6082 | 7328 | 1.19997 | 1246 | 6082 | 0.17003 |
| T7634_k1_840_k2_6794 | 7634 | 1.25007 | 840 | 6794 | 0.11003 |
| T7634_k1_1069_k2_6565 | 7634 | 1.25007 | 1069 | 6565 | 0.14003 |
| T7634_k1_1298_k2_6336 | 7634 | 1.25007 | 1298 | 6336 | 0.17003 |

## 3. Pre-launch checks (2026-09-27 ~14:20 local)
- (a) Design H1+H2 sanity: NOT pre-checked separately; baked into `run.py` as a full in-run
  post-design assertion (`|H1.mean()+H2.mean()-H| <= 0.01`), because the design pass here is
  "reused-equivalent" (same channel/design_seed/DESIGN_MC as the reviewed op-fix-n32k-alloc,
  which measured design H1+H2=0.9316289 vs channel H=0.93183, diff=0.00020) -- the full pass is
  the run itself. If violated, `run.py` returns status `design_sanity_fail` with no grid
  execution.
- (b) AST `%`-format check on `run.py`: 8 format expressions, 0 placeholder/argument
  mismatches -> PASS (verified via `ast.walk` over `BinOp(Mod)` nodes with a `%`-spec regex).
- (c) Aggregation keyed by `f_label` (encodes total,k1,k2), never by `k1` alone; all 6 labels
  and all 6 (total,k1,k2) tuples are distinct by construction (visually confirmed in `POINTS`).
- (d) Descriptive strings/numbers checked against the frozen 2-total x 3-share grid above;
  `deviations_from_plan_A_rows` names the design-sanity-assertion addition as the only new
  runner delta beyond grid/seeds/output-root.
- `results.json` ABSENT at prereg-freeze time (verified by `ls`).
- Timing decision (recorded before freeze, per task instruction): predecessor per-block time
  ~21s + ~860s design => estimate 96 blocks*21s + 860s = 2876s < 4000s budget. Estimate does NOT
  exceed budget -> full 2 seeds x 8 blocks/point (16/point) kept, no reduction.

## 4. Launch
- **Attempt 1 (FAILED, not a measurement/implementation-defect rerun)**: launched
  2026-09-27T14:23:47 local via `wsl -e bash -c "cd /mnt/d/... && nohup env ... python
  run.py ... & echo PID"`, reported PID 1302946. After a 20s wait, the PID no longer existed
  and `run_stdout.log` was never created (`ls` on the probe root showed only `prereg.md`,
  `run.py`). Root cause: the operator's own `wsl -e bash -c "..."` wrapper process exited
  immediately after echoing the backgrounded PID, and the WSL2 lightweight VM was torn down
  (idle teardown) before/while the `nohup`'d child could establish itself, so no process,
  log, or results.json was ever produced -- this occurred BEFORE any measurement or design
  sample was taken, so it is not counted as a probe rerun and needed no error record.
  Corrective action: relaunch via the operator's own Bash-tool backgrounding
  (`run_in_background: true`) around the single foreground `wsl -e bash -c "..."` invocation
  (no internal `&`/`nohup`), which keeps the underlying `wsl.exe` process (and hence the WSL2
  VM) resident on the Windows side for the full run duration.
- **Attempt 1b relaunch also needed a path fix**: the first relaunch attempt still included an
  explicit `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar &&` prefix and failed with
  `cd: ... No such file or directory` (mount not yet established on a cold-started VM). Verified
  that `wsl -e bash -c "pwd"` already resolves to the correct project root automatically (wsl.exe
  maps the caller's Windows cwd), so the `cd` prefix was dropped and the command used
  workspace-relative paths from the implicit correct directory.
- **Attempt 2 (actual launch)**: launched 2026-09-27T14:27:03 local (host `date`), via Bash-tool
  background command (task id `byyvmzh7g`), WSL PID 1303073 (confirmed alive via `ps` at
  14:32:30, 99.7% CPU, RSS 725 MB, well under budget), stdout ->
  `workspace/probes/op-n32k-fine-f4/run_stdout.log`.
- Completion: background task notified completed (exit code 0) at 2026-09-27T15:14 local.
  stdout: `A3 MC genie design samples=64/64 complete=True wall=856.634`; design sanity
  `H1+H2=0.931629 vs H=0.931830 diff=0.000201 pass=True`; 12 cell lines; final line
  `WROTE .../results.json` / `STATUS ok WITHIN True CELLS {'expected': 12, 'completed': 12}
  WALL 2820.295`. reruns=0; no execution_error record.

## 5. Result record (descriptive, Tier X, non-claim)
`workspace/probes/op-n32k-fine-f4/results.json`: status ok, within_budget true,
stop_rules_triggered [], wall 2820.295 s (design 856.634 s for 64 samples; 12 cells advancing
over the remaining ~1964 s), peak RSS 1,188,827,136 B (~1.11 GiB).

| total | f_book | k1 | k2 | k1 share | op exact/16 | oracle exact/16 | op verify_failed | undetected | decode_failed | resource_abort |
|---|---|---|---|---|---|---|---|---|---|---|
| 7328 | 1.19997 | 806  | 6522 | 0.11 | 2  | 8  | 14 | 0 | 0 | 0 |
| 7328 | 1.19997 | 1026 | 6302 | 0.14 | 1  | 1  | 15 | 0 | 0 | 0 |
| 7328 | 1.19997 | 1246 | 6082 | 0.17 | 0  | 0  | 16 | 0 | 0 | 0 |
| 7634 | 1.25007 | 840  | 6794 | 0.11 | 6  | 15 | 10 | 0 | 0 | 0 |
| 7634 | 1.25007 | 1069 | 6565 | 0.14 | 10 | 10 | 6  | 0 | 0 | 0 |
| 7634 | 1.25007 | 1298 | 6336 | 0.17 | 1  | 1  | 15 | 0 | 0 | 0 |

Totals: operational {exact: 20, undetected: 0, verify_failed: 76, decode_failed: 0,
resource_abort: 0}; oracle {exact: 35, undetected: 0, verify_failed: 61, decode_failed: 0,
resource_abort: 0}. `undetected` is genuinely 0 everywhere (isolated, never merged into
success); every per-point breakdown above shows the same isolation. kdb observed
{36704, 38234} = disclosed+64 for the two totals (36640/38170), correct.

Descriptive comparison to op-fix-n32k-alloc (non-claim): at f_book=1.20 (between the
predecessor's 1.15-all-zero and 1.30-peaked rows) the finer share grid still shows the
best point at share=0.11 (2/16), degrading to 1/16 at 0.14 and 0/16 at 0.17 -- i.e. at 1.20
the peak (if any) sits below share 0.11, not inside [0.11,0.17]. At f_book=1.25 the peak is
sharper and stronger: share=0.14 gives 10/16 operational exact (oracle also 10/16, no
divergence), versus 6/16 at 0.11 and only 1/16 at 0.17 -- a cleaner, higher single-point peak
than the predecessor's f_book=1.30/share=0.14 point (13/16), though at higher disclosed bits
(38170 vs 35115) it is not directly comparable as an efficiency point. Both f_book=1.20 and
1.25 remain well short of "usable" in any threshold sense (best observed: 10/16 ≈ 63% at one
grid point); no pass/fail or operating-point claim is made for any point.
