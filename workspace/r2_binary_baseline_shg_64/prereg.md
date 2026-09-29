Q: On the SAME frozen 64-block R2 pool NB-Polar's `workspace/r2_fer_shg_64/`
already measured (`docs/nbpolar/DATA_LEDGER.md` §7; SHG `_1`+`_2`, 32 blocks
each, `stratum_official` A1_CAL_characterization(8)+HELDOUT_model_selection(10)
+EVAL_already_decoded(14) per session, CAL32 excluded), what is the frozen
binary-Polar-baseline (`src/reconciliation/real_polar_sc_rescue.py` +
`src/reconciliation/cpp_scl_wrapper.py`'s CA-SCL, `src/reconciliation/
verification.py`'s Toeplitz tag -- this repo's OWN `src/`/`experiments/`
frozen baseline, NOT the sibling `HD-QKD_Polar_Release` repo's improved
`low_dim_opt/` line) SC-arm (primary) taxonomy (exact/verify_failed/
undetected/decode_failed), pooled and per-stratum, with Wilson(z=1.96) CIs,
at up to `MAX_F_POINTS=4` `sc_margin` grid points (one near NB-Polar's own
`f_book_with_crc`, up to three more bracketing the SC-arm's FER<=0.05
achievable-rate frontier), PLUS the CA-SCL(L=4,CRC-16) secondary/descriptive
message-exact-match rate at the same grid points, PLUS a 64-block pairwise
2x2 contingency table (NB exact/binary exact) per grid point -- a purely
descriptive comparison, NO win/lose threshold, per
`docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md`?

P: Setup (once per session, G2 then G3): import
`workspace/r2_fer_shg_64/run.py` BY FILE PATH (read-only reference, not
copied, not executed as `__main__`) to reuse its `build_session_blocks`/
`_reproduce_session_context`/`SESSION_CFG`/`ARM` UNCHANGED -- this guarantees
byte-identical `(frames_a, frames_b)` (the same raw d=1024 integer arrays
NB-Polar's own GF(32) `A=32*U1+U2` framing consumes) without re-deriving the
alignment/pairing/chunking chain. From the SAME CAL32 ids
(`mod.g2_cal_ids("B_M2_32f_candidate")`, frames 1024-1055, excluded from the
64-block pool), compute this session's own 10 per-layer marginal BERs
(`layer_ber`, MSB layer_idx=0/shift=9 first, matching
`_extract_real_layer_bers`'s convention verbatim) -- CAL32-ONLY, never EVAL/
HELDOUT/A1_CAL. Freeze the binary construction (`freeze_binary_construction`):
polarization-weight order (`_polar_weight_order(4096)[::-1]`, beta=2**0.25,
frozen, layer-independent), per-layer per-margin rate search reusing
`_build_candidates` + `_simulate_layer_sc_fer_early` (FER_THRESH=0.05,
~~CALIB_N_FRAMES=4000~~ **CALIB_N_FRAMES=100** Monte-Carlo trials/candidate,
memoryless BSC(p=layer_ber) model -- the SAME model the frozen baseline's own
rate search uses), scanning ~~`sc_margin` over [0.00,0.30] step 0.01~~
**`sc_margin` over the short candidate list `SC_MARGIN_CANDIDATES = {0.02,
0.05, 0.08, 0.12, 0.18, 0.25, 0.30}` (7 points, not a dense sweep)**; select
up to 4 grid points (closest to NB-Polar's own `f_book_with_crc` for this
session, plus up to 3 more spanning the usable-margin range, by sorted
`f_book_sc`). Write `construction_frozen_<SESSION>.json` BEFORE any EVAL/
HELDOUT/A1_CAL block is touched (Pre-EXECUTE-checkable evidence that
construction saw CAL32 only).

> **2026-09-29 Pre-EXECUTE F2 修正前的旧值**（保留、加删除线，不删除，供
> 审计追溯）：`CALIB_N_FRAMES=4000`；`sc_margin` 细网格扫描
> `[0.00,0.30]` step `0.01`（31 点）。这两个值在一次真实（合成数据，非
> SHG 真实数据）计时探针发现冻结的 `polar_sc_decode_with_frozen` 是
> O(N² log N)（而非标准 O(N log N)）后被替换——细网格扫描在 N=4096 下预计
> 需上百 CPU 小时，已用一次真实尝试证实不可行（跑 >8 分钟未完成，被终止；
> 该尝试全程未读取任何 `.ttbin`/CAL32 真实帧，`STATUS.yaml` 的
> `incidents` 有完整记录）。修正依据、时序实测数据、完整推导见合同
> `docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md` §3.1
> （该节本身就是这次修正的权威记录，本文件只是同步冻结值，不重复推导）。
> `run.py` 从一开始就没有读取过 `prereg.md`，所以这次文本修正不改变、也
> 不影响任何已执行的代码路径（本包尚未在真实数据上执行过任何解码）。

Execution order (SERIAL single process, Pre-EXECUTE round-2 F4; TWO PASSES, main-thread
ruling D_BIN_TWO_PASS): PASS 1 = G2 construction, G3 construction, then ALL 64 blocks x
frozen grid points with the SC primary arm ONLY (+ per-block tag); PASS 2 = the CA-SCL
secondary arm over the pass-1-ok blocks x grid points, total-wall permitting (total wall
checked before every block; entries not run are recorded
`ca_scl_not_started_total_wall_budget` in separate `scl_part_*.json` files -- they never
affect SC D or Tables A/B1; Table B2 covers only finished blocks and states how many).
Per (session, block) pair and frozen grid point, decode all 10 layers
x 8 codewords (N=4096 each) of that 32768-symbol block:
- SC (primary): `u_a = polar_encode_non_systematic(a_bits, 12)` (confirmed
  self-inverse over GF(2) for this kernel, `_selfcheck_involution.py`);
  `llr[i] = +lam if b_bits[i]==0 else -lam` (`lam=log((1-p)/p)`, p=this
  layer's CAL32-frozen BER, clipped +/-20, SAME formula the frozen baseline
  itself uses); `u_hat = polar_sc_decode_with_frozen(llr, mask, u_a, 12)`
  (mask=info positions from the frozen construction); `a_hat_bits =
  polar_encode_non_systematic(u_hat, 12)`; codeword-exact iff
  `a_hat_bits==a_bits`; disclosed_bits = N-k (frozen positions of `u_a`,
  genuinely disclosed, no overwrite).
- CA-SCL (secondary, descriptive only; PASS 2): last-16-ascending-index info
  positions of `u_a` overwritten with `calc_crc16(msg)` (msg = the other
  k-16 true info positions) -- a genuine 16-bit/codeword overhead this
  decoder's own internal CRC path-selection requires (`main.cpp:213-237`);
  `decoder.decode_batch(...)`; message-exact-match recorded (msg positions
  only, CRC positions excluded from the exactness comparison since they are
  overhead, not reconciled content).
- Reassemble the block's 10 SC-decoded layers into `a_hat_sym` (32768
  symbols); ONE per-block Toeplitz `universal_hash_tag` check
  (`src/reconciliation/verification.py`, tag_bits = NB-Polar's own
  `chain.tag_bits`, fetched at runtime not hardcoded) with `point_id =
  f"r2-binary-baseline-shg64-margin{sc_margin}"`, `layer_id=0`,
  `block_index=global_block_index` (reused from the NB packet's own block
  metadata, NOT re-derived, so no seed-reuse-across-methods risk since the
  point_id differs from NB-Polar's own). `accepted = tag_pass`; `exact =
  accepted AND array_equal(a_hat_sym, true symbols)`; `undetected = accepted
  AND NOT exact` (isolated); `verify_failed = NOT accepted`; `decode_failed =
  False` (SC is deterministic, always produces a candidate -- schema
  completeness only, matches the NB-Polar side's own near-unreachable
  branch). Per-block SHA-256 of `(frames_a[s:e+1], frames_b[s:e+1])` recorded
  as cross-check evidence (equality with the NB packet's own symbols is a
  code-invariant here, not something in doubt -- both call the identical
  imported function -- the hash is recorded per the originating task's
  explicit request).

Budget (serial single process; all three checks are implemented in `run.py`):
total wall <= 4 h (`BUDGET_WALL_S_TOTAL`, from main() start; checked before each
session's construction and before each block; once exceeded nothing new starts,
remaining blocks are recorded `status="not_started_total_wall_budget"` -- no grid
results, not in D, counted separately; the block already running finishes);
per-block wall <= 1200 s (cumulative from block start, checked before each grid
point); RSS <= 4 GiB (process VmHWM, checked after each grid point, over budget ->
`resource_abort_rss_post_decode`). No tuning on overbudget. Projected serial time:
construction ~151 min (75 min/session worst case x 2) + SC decode ~28 min + the
unmeasured CA-SCL secondary arm (rough guess 15-70 min) => ~3.3-4.2 h. Because CA-SCL is
pass 2, hitting the 4 h check at the upper end truncates ONLY the CA-SCL arm (SC primary arm
already complete); if pass 1 itself is cut short, pooled D < 56 => INSUFFICIENT.
Main-thread ruling C5: `--dry-run-one` is NOT run first for this execution (it would
cost ~75 min of construction that is then discarded; the in-code total-wall check is
the backstop). The dry-run feature is kept. `--dry-run-one` decodes exactly 1
real block (G2 global_block_index 0, frames 0-127; all grid points) for
timing only, not aggregated; its outputs go to `dry_run/` (marked not counted
in results); the full run re-decodes that block into the top level and never
reuses `dry_run/` files (construction is rebuilt fresh too). No tuning, no
parameter/grid change under any outcome; one-shot, reruns=0 (a rerun to fix
an implementation defect -- never a parameter/grid/threshold change -- is a
separate recorded attempt). Readiness: `results.json` and any top-level
`part_*.json` must be ABSENT before a full launch (enforced in-code since
the Pre-EXECUTE round-1 F3 fix; one such file => `_fail`). `--authorize` flag required;
`run.py` refuses otherwise. Forbidden: any edit to `src/`, `experiments/`,
`tools/`, `comparison_bench/src/`, or `workspace/r2_fer_shg_64/` (read-only
reference); reading raw `.ttbin` content beyond what the imported
`_reproduce_session_context` itself does (identical to the NB packet's own
scope); any git write.

Aggregate output (`results.json`, not yet built by this preparation pass --
the full 64-block run has NOT been executed): per-grid-point taxonomy
(pooled + `stratum_official` + `stratum_task`), Wilson(z=1.96) CIs, CA-SCL
descriptive message-exact-match rate, the 64-block 2x2 contingency table vs
the frozen `workspace/r2_fer_shg_64/results.json` per-block `exact` outcomes,
and `f_book_sc`/`f_book_scl` per session per grid point. NO win/lose verdict
string anywhere (descriptive comparison only, per the contract §5).

Authorization: **NOT YET GRANTED.** See `AUTHORIZATION_PROMPT.md`
(template) and `STATUS.yaml` (`state:
prepared_awaiting_pre_execute_review_and_pi_authorization`). PI has given a
directional go-ahead ("按建议起草对比合同，reviewer核查合同后可以直接开始",
2026-09-29) but this does not itself satisfy AGENTS.md §10.3's independent
Pre-EXECUTE review, nor does it confirm this packet's specific budget
numbers (§6 of the contract) or `sc_margin` search range -- those need
explicit confirmation in `AUTHORIZATION_PROMPT.md`'s final text.

C: (from repository root, WSL; NOT to be run until PI authorization +
independent Pre-EXECUTE PASS are on record)

```
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 \
PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar \
/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python \
/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2_binary_baseline_shg_64/run.py \
--authorize
```

Dry-run timing probe (kept but NOT used for this execution, main-thread ruling C5;
still requires `--authorize`+PI text per `run.py`'s own guard, since it opens the
same raw `.ttbin` the full run would):

```
... run.py --authorize --dry-run-one
```
