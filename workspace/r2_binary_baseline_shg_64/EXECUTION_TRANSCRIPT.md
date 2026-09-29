# EXECUTION TRANSCRIPT — r2-binary-baseline-shg-64 (operator, facts only)

## Command (prereg C 段原文，经 `MSYS_NO_PATHCONV=1 wsl.exe -e bash -c` 包装，Bash run_in_background)
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2_binary_baseline_shg_64/run.py --authorize
(stdout+stderr -> run_stdout.log; 无 dry-run；reruns=0)

## Pre-launch
- 首次核对 2026-09-29 06:05:57：解释器缺 Swabian.TimeTagger，启动前停下（INC_2026_09_29_02_ENV_MISSING_PACKAGE，STATUS.yaml 已登记）；主线程补装 Swabian-TimeTagger 2.22.6。
- 重新核对 10:44:10：results.json / part_*.json / scl_part_*.json / dry_run 均不存在；numpy 2.4.4、numba 0.65.1、`from Swabian import TimeTagger`、src.reconciliation.real_polar_sc_rescue / verification、experiments.run_real_polar_max_pie 均可 import。

## Times / exit
- 启动 2026-09-29 10:44（本地）；结束 12:16:56；退出码 0。
- results.json timing: total_wall_s 5556.4（92.6 min），pass1_wall_s 2314.9，pass2_wall_s 3240.6，total_wall_exceeded False（预算 14400 s）。
- construction wall（timing.construction_wall_s_by_session）：G2 633.8 s，G3 626.5 s；search_wall_s：G2 606.3，G3 598.6。
- 最终日志行：`[done] results.json written; margins=[0.02, 0.08, 0.18] stop_undetected=False block_accounting_consistent=True not_started=0`

## Grid
- 每 session 只找到 3 个可用网格点（MAX_F_POINTS=4，未填满；all_layers_usable=True），两 session 同为 sc_margin {0.02, 0.08, 0.18}。
- target_f（NB f_book_with_crc）：G2 1.2753，G3 1.2681。
- f_book_sc / f_book_scl：
  - 0.02: G2 4.3325/4.3803, G3 4.1108/4.1584
  - 0.08: G2 4.2347/4.2826, G3 4.2502/4.2978
  - 0.18: G2 4.8179/4.8657, G3 4.7198/4.7673
  （f_book_sc 相对 margin 非单调，MC 噪声，review C3 已提示）
- 所选点均远离 target_f（~1.27），最近点约 4.1–4.3。

## Accounting / counts
- block_accounting: 64 = contributing 64 + error 0 + not_started 0 + resource_abort 0 + no_grid 0，consistent True。
- pass 2：64 块全部跑完，blocks_not_started_total_wall 0。
- 各 margin pooled：见 results.json per_margin[*].taxonomy_pooled（decode_failed 0, resource_abort 0, undetected 0 全部 margin）。
- 每块 wall：SC pass1 16.2–17.0 s；CA-SCL pass2 49.5–53.6 s。
- rss_gib_peak_advisory（VmHWM，进程生命周期峰值）：所有 entry 均为 1.3005 GiB（min=max，预算 4 GiB）。
- stderr/stdout 异常：无 Traceback；仅有 wsl 启动的编码乱码提示行。
