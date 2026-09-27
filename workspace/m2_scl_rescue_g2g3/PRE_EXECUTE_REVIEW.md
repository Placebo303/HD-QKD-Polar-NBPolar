# Pre-EXECUTE Review — m2-scl-rescue-g2g3

Reviewer: independent Pre-EXECUTE reviewer (reviewer-go role, AGENTS.md §3/§10.3).
Scope: `workspace/m2_scl_rescue_g2g3/{run.py,TASK_PACKET.md,prereg.md,STATUS.yaml,AUTHORIZATION_PROMPT.md}`.
No files modified except this one. run.py not executed; no decoder run; no raw .ttbin content read (existence/size only, and only via prior evidence — this pass read no new raw data).

## Verdict: PASS_WITH_COMMENTS

## Findings

1. **[PASS] Branch/cleanliness.** Branch = `codex/nbpolar-phase0`. `git diff --stat` on `scl_joint.py`, `two_layer.py`, `sc.py`, `scl.py`, `transform.py`, `algebra.py`, `prior.py`, `prior_m2.py`, `scripts/m2_prior_validation.py` is empty — no uncommitted changes to any frozen file run.py imports.

2. **[PASS] Frozen inputs match G2/G3 freeze.** `g2_freeze_config.json`/`g3_freeze_config.json` confirm `cal_frame_ids=[1024,1055]`, `mod_boundary="CIRCULAR"`, `tag_master` 2026103001(G2)/2026110101(G3) — identical to `run.py`'s `SESSION_CFG`/constants. Source constants in `scripts/m2_prior_validation.py` confirm `G2_K1=319`, `G2_K2=6492`, `G2_N=32768`, `G2_EVAL_SEED=2026093001`, `G3_EVAL_SEED=2026100101`, matching TASK_PACKET.md §3 table exactly. Window=200/skip=702/CIRCULAR are passed as literals identical to the frozen pipeline calls.

3. **[PASS] Fidelity-check design and target-block truth.** Read (JSON only, not raw timetags) both `per_block_outcomes.jsonl` files: G2 blocks 1/5/12 and G3 blocks 0/1/2/4/10/11 all show `arm=B_M2_32f_candidate`, `outcome=verify_failed`, `first_error_layer=L2`, `l1_exact=True` (except G3 block 11 = False), `hard_l2_exact=False` — byte-for-byte consistent with `workspace/analysis/g2g3-layer-attribution/REPORT.md` §3 tables (verified the correct arm sub-table, not the A1/A2 sub-tables). `run.py::_fidelity_check` diffs exactly these 5 fields (`outcome`, `first_error_coordinate`, `first_error_layer`, `l1_exact`, `hard_l2_exact`) against this same file. D3's per-block-stop-plus-`fidelity_compromised`-flag is implemented correctly in `main()` (lines 586-612).

4. **[PASS] SCL rescue semantics.** `d1_positions=l1_order[:319]`/`d1_values=u1_true[...]`, `d2_positions=l2_order[:6492]`/`d2_values=u2_true[...]` — Alice-truth-valued frozen disclosures, matching `scl_joint_decode`'s real signature and `sc_decode`'s disclosure contract. `crc_true = labels_crc16(labels_true)` (Alice truth). Tag recomputed with the SAME `operational_seed_bits(tag_master, N, block_index, ...)` stream for both `tag_true` (Alice) and `tag_hat` (SCL candidate). `accepted = crc_pass AND tag_pass` (F1, matches T3 gate convention at `workspace/probes/scl-gate-t3`, confirmed present on disk). `exact`/`undetected`/`verify_failed` derived correctly and isolated per spec. Inspected `scl_joint_decode`'s canonical-merge-then-CRC-scan logic: candidate ranking is by `joint_metric` (from Bob-only likelihoods) with `crc_true` used only to pick the first CRC-passing candidate in that fixed order — no truth leakage into the ranking itself.

5. **[PASS] Bookkeeping.** `DISCLOSED_BITS_PER_COORDINATE=5`, `TAG_BITS=64` confirmed in `two_layer.py` ⇒ `kdb_no_crc=5*(319+6492)+64=34119`, `kdb_with_crc=34135`, matching TASK_PACKET.md §5 and `run.py` exactly. `f_book=kdb/(H*N)` convention matches the cited decision-log formula, with H computed from the real per-session CAL fit.

6. **[PASS] Output/no-overwrite scope.** `results.json` and all 9 `part_*.json` absent (only prep artifacts present). Grepped every `open(...,"w"...)` in `run.py`: exactly 3 write sites, all targeting `_part_path(...)` or `RESULTS_PATH`, both resolved under `THIS_DIR` (`workspace/m2_scl_rescue_g2g3/`). No write call anywhere touches `results/`, `comparison_bench/outputs_comparison/`, or any `workspace/m2_prior_validation/*` path (those are only opened `"r"`). `main()` refuses to run if `results.json` or any target part file already exists.

7. **[PASS_WITH_COMMENT] Budget/parallelism.** Wall budget (1200s soft pre-check + 120s hard-terminate margin) and `MAX_PARALLEL=8` are implemented correctly (`_run_one_block_entry`, `_launch_all`). **Gap**: the 2 GiB RSS budget is recorded only as a post-hoc advisory (`_peak_rss_gib()` read from `/proc/self/status` `VmHWM`) — nothing in `run.py` ever compares live RSS against `BUDGET_RSS_GIB_PER_BLOCK` or aborts on it; an RSS blowup is caught only indirectly, if it also causes a wall hang past budget+120s. Non-blocking: the T3 precedent (`workspace/probes/scl-gate-t3/results.json`) empirically shows ~0.65 GiB per 16-block SCL-joint batch at the same N=32768/L=16, i.e. far under 2 GiB, so a concrete OOM/RSS-driven wrong-conclusion risk is low. Minimal fix if the main thread wants it closed before execution: a periodic `psutil`/`/proc/<pid>/status` RSS poll in `_launch_all`'s existing 2s loop that also `terminate()`s on RSS breach (mirrors the existing wall-check pattern) — small, optional, does not block this PASS.

8. **[PASS] Authorization scope.** Verbatim PI text "授权，用 SCL L=16 重解那 9 个失败块，可以继续往下推进" is recorded identically in `AUTHORIZATION_PROMPT.md`, `STATUS.yaml`, `TASK_PACKET.md`, and `run.py`'s own docstring. `TARGETS` is a hardcoded 9-tuple module constant, never derived from input — structurally the script cannot decode any other block or open any other session/arm (`ARM` is a fixed string constant used everywhere, including `g2_cal_ids(ARM)`).

9. **[PASS] Focused test.** Ran `D:\software\Miniforge3\python.exe -m pytest -p no:cacheprovider comparison_bench/tests/test_nbpolar_scl_joint.py -q` with `PYTHONPATH=<repo root>`: **6 passed** in 55.92s (one benign `Unknown config option: cache_dir` warning, unrelated).

## Cross-check notes (S4/S5, manual attribute/signature audit)

Verified every frozen call site run.py makes resolves to a real, currently-defined function/attribute with matching parameter names: `verify_predecessor_construction`, `make_gf32`, `operational_seed_bits`, `labels_to_bits`, `toeplitz_tag`, `seed_bits_for`, `disclosed_bits_per_coordinate`(`=tl.DISCLOSED_BITS_PER_COORDINATE`), `tag_bits`(`=tl.TAG_BITS`), `alpha`(`=tl.ALPHA`) all present on the `SimpleNamespace` returned by `_load_g2_decoder_chain`; `fit_g2_arm(arm, cal_a, cal_b, mod, m2_mod)`, `run_g2_block(*, arm, block_index, eval_frames, bob, alice, fit, p1_table, p2_table, l1_order, l2_order, k1, k2, tag_master, eval_seed, chain, polar_fn, prior_mod)`, `g2_truth_views(alice, polar_fn)` all match call-site kwargs exactly; `scl_joint_decode(bob, crc_true, *, field, alpha, p1_table, p2_table, d1_positions, d1_values, d2_positions, d2_values, list_width_L, top_m)` and its `SCLJointResult` fields (`high_hat/low_hat/label_hat/m1/m2/joint_metric/crc_true/crc_hat/crc_pass/crc_bits/l1_survivor_count/top_m_used/candidates_considered/metric_provenance`) all match `run.py::_rescue_block`'s usage.

## Blocking items

None. No FAIL findings.
