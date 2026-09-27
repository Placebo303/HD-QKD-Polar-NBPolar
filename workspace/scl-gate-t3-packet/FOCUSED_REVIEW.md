# FOCUSED_REVIEW — Tier-X probe `scl-gate-t3`（AGENTS.md §10.4 聚焦数值复核）

角色：独立评审（reviewer-go）。仅新增本文件与 `workspace/probes/scl-gate-t3/review_scratch/*`；未修改任何既有文件；未做 git 写操作；未接触真实数据。不作科学判定，判定线由主线程按 T1 裁决适用。

## 判定：**PASS_WITH_COMMENTS**

## Findings

**F1 [PASS] prereg ↔ run.py/launch 一致。** `run.py` 常量 `CRC_BITS=16`(=`scl_joint.CRC_BITS`)、`TOP_M_DEFAULT=4`、`L_VALUES=(4,8,16)`、`SEEDS=(2026093003,2026093004)`、`BLOCKS=8`、`DESIGN_SEED=2026093000`、`DESIGN_MC=64`、`MASTER=tl.FROZEN_TOEPLITZ_MASTER` 与 prereg.md 逐项对应。两套 pmf 严格分离：`sample_pmf`（原始质量/0.9999，仅用于抽样 x,y）与 `decode_pmf_floored`（`prior.apply_explicit_floor(raw,1e-15,...)`，用于 table/p1/p2 及设计通道）；`apply_explicit_floor` 源码确认「先对*未归一化*的原始质量做 floor，再整体重新归一化」，与 prereg 描述完全一致。设计阶段 `known_positions=allpos`（genie SC，全披露），`|H1.mean()+H2.mean()-H|<=0.01` 为硬 `assert`，`design.json`/`results.json` 中 `sanity.pass=true`（abs_diff≈3.28e-5）。

**F2 [PASS] 配对有效，与 op-n32k-matched 逐块一致。** `gen_block` 的 `rngb=default_rng([seed,block])→x=integers(0,1024,32768)→dd=choice(1024,32768,p=sample_pmf)→y=(x+dd)%1024` 与 op-n32k-matched/run.py 内联抽样代码逐字节等价（`sample_pmf`/`matched_pmf` 用同一 raw 质量与归一化公式）。独立重算 SC 臂逐块 `label_match`：A 点 10/16 exact（block 集合与 op-n32k-matched 完全相同：(03,1)(03,2)(03,4)(03,6)(03,7)(04,0)(04,1)(04,2)(04,3)(04,6)），B 点 0/16 exact，与 prereg/results.json 声称的 op-n32k-matched 基准（10/16、0/16）一致。差异仅在于 A 点 4 个块的结局标签从 op-n32k-matched 的 `decode_failed` 变为本探针的 `verify_failed`——这是 floor 改变数值路径（不再抛未 floor 时的数值异常，而是走到 CRC/tag 判定）的预期后果，不影响 label_match 集合。

**F3 [PASS] 独立重算 results.json 全部计数、flips_vs_sc、accepted/undetected/exact 派生逻辑。** 用脚本从 6 个 `part_SCL_*.json` + `part_SC.json` 重新计算 `sc_totals`/`scl_totals`/`oracle_totals`/`flips_vs_sc`（6 行 × 3 种 totals + flips），与 `results.json.rows` **逐字段完全一致，0 处不符**。逐条记录核对 `accepted==(crc_pass and tag_pass)`、`undetected==(accepted and not label_exact)`、`exact==(accepted and label_exact)` 全部成立，`undetected` 在所有记录中恒为 0（未与 exact/FER 合并，隔离正确）。`scl_joint.py` 源码确认 CRC 是对**候选**标签重算（`label=cand.low+32*cand.high; crc_hat=labels_crc16(label)`），函数签名内不接触 Alice 真值；`run.py::_scl_style_eval` 的 tag 同样对 `got.label_hat`（候选）重算 `tag_hat` 后与 `tag_true` 比较——两处均无用真值作弊。

**F4 [PASS，含解释] B 点 SCL 与 oracle 逐块结果确认为同一批块、完全相同（非聚合巧合）。** 逐 (seed,block) 比对 `part_SCL_B_L{4,8,16}.json` 的 `scl_records` 与 `oracle_records`，三个 L 下 `outcome`/`label_exact` 逐块 100% 相同。可能的解释（描述性，非科学结论）：B 点 k1=578（worst-H1 披露份额比 A 点更大），使得 SCL 对 L1 未披露位置的估计在 top_m=4 展开下几乎总能收敛到真值候选；此时 SCL 联合解码等价于「L1 已知」的 oracle 路径——凡 CRC+tag 通过必判定为 exact（两臂 undetected 均为 0），凡 L2 在真值 L1 条件下本身不可纠（oracle 也失败）则联合解码同样失败。A 点（k1=301，披露更少）未见此现象（SCL/oracle 计数在 L=4,8 处不同），与该解释方向一致。

**F5 [PASS] 记账数字复核。** `HN=26755.518469035287`；两点 `disclosed_no_crc=5*6421=32105`，`+CRC16=32121`，`f_book_no_crc=32105/HN=1.1999393709060722`，`f_book_with_crc=32121/HN=1.200537378379503`（四舍五入 1.19994/1.20054，与任务描述一致），`key_dependent_bits=32121+64=32185`。两点数值相同（两点 total 均为 6421，disclosed 只依赖 total，不依赖 k1/k2 分配），这是预期行为非 bug。

**F6 [PASS，附带发现 F6a] 启动事故与重启合规。** `log_relaunch_attempt1_combined.txt` 记录的根因（`A&&B&&C&&CMD1 & CMD2 & ...` 括号绑定问题，只有 SC 臂在正确子 shell 中执行，6 个 SCL/oracle worker 在死前从未进入 Python，0 measurement）与 `part_SCL_*.json` 时间戳（均在 `relaunch_scl_attempt2.sh`（18:18:44 创建）之后，最早 19:02:37）互相印证：确认 attempt1 时刻不存在任何 `part_SCL_*.json`，重启合法（AGENTS/prereg 的「实现缺陷死亡前 0 measurement 可重启一次」例外）。SC 的 part 来自 attempt1 且状态 `ok`/`stop_reasons=[]`，独立复核其记录自洽（F2/F3），视为有效。
　**F6a [非阻断评论]** prereg.md 的 C 条目声明执行方式是整体 `bash .../launch_all.sh`；但 attempt1 实际执行的命令（log 中给出）是操作者手写的单行 `wsl.exe -e bash -c '...'`，只覆盖 design 之后的 SC+6 worker 段，并非直接调用 `launch_all.sh` 脚本文件本身（`launch_all.sh` 的 export 写法本身是正确的分行形式，反而没有 attempt1 描述的 bug）。`design.json`（18:03:10）与 `part_SC.json`/`log_sc.txt`（18:16:54，wall_s=635.3s）的文件时间差（13m44s，可用 smoke 步骤 ~148s + 若干 shell 开销解释）与两文件内部字段自洽；但 log 中打印的 `date`（18:16:54）与 SC 完成时间在同一秒，若按脚本严格顺序（`date` 先于 SC 启动）本应相差 635s——该文件自身已注明是「操作者终端捕获、多个后台进程交织输出，非探针写出的文件」，故判断为终端捕获缓冲/交织的记录瑕疵，而非数据问题；`part_SC.json`/`part_SCL_*.json` 内部自测 wall_s、RSS、stop_reasons 已独立验证自洽（F3、F7），不受此瑕疵影响。建议主线程知悉此处「执行命令」与 prereg C 条目文字不完全一致，但不影响冻结参数或结果有效性。

**F7 [PASS] 预算与 rerun。** 逐 part 文件核对：`part_SC.json` wall=635.3s / rss=894MB；6 个 `part_SCL_*` wall 范围 2597–9600s（均 <14400s 上限）、rss 645–693MB（均 <1GiB 上限）；全部 `status=ok`、`stop_reasons=[]`。Rerun 情况：SC 臂 0 次重跑（attempt1 一次成功）；6 个 SCL/oracle worker 为「实现缺陷死亡前 0 measurement」例外下的一次重启（attempt1 死亡 → attempt2 成功），未变更任何参数/种子/L，符合 prereg 的 one-shot rerun_policy 例外条款。

**F8 [PASS] 测试。** `D:\software\Miniforge3\python.exe -m pytest -p no:cacheprovider comparison_bench/tests/test_nbpolar_scl_joint.py comparison_bench/tests/test_nbpolar_scl.py -q`（从仓库根，无需额外 PYTHONPATH，测试文件自带 `sys.path.insert(parents[2])`）→ **22 passed, 0 failed**（1 个与本任务无关的 pytest 配置警告 `Unknown config option: cache_dir`）。`git diff -- comparison_bench/tests/test_nbpolar_scl.py` 确认只有 1 处改动：`test_nbpolar_scl.py:172` 附近把 `path_metrics[0] == float(np.sum(...))` 的精确相等改为 `abs(diff) <= 1e-12*max(1,|ref_sum|)` 相对容差比较，附充分注释说明浮点求和顺序差异（`scl.py` 累加 `+=` vs 参考实现向量化 `np.sum`）。该修复与 `workspace/probes/scl-joint-timing/CODE_REVIEW.md` 记录的唯一 `[FAIL-1]`（T-a 因精确浮点相等失败）根因/位置完全对应；该评审记录的其余项目均为 `[PASS]`。

**F9 [PASS] 写入范围。** `git status --porcelain` 除已知预存脏文件（`workspace/pytest-evidence-test/**`、`comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`）外，只有：`M comparison_bench/tests/test_nbpolar_scl.py`、`?? comparison_bench/src/comparison_bench/formal_ir/nbpolar/scl_joint.py`、`?? comparison_bench/tests/test_nbpolar_scl_joint.py`。`workspace/probes/scl-gate-t3/**` 与本评审新增的 `workspace/scl-gate-t3-packet/**` 经 `git check-ignore -v` 确认被 `.gitignore:20 workspace/*` / `:22 workspace/probes/*` 忽略，不会污染仓库状态。

**F10 [信息性，非阻断] Packet 目录本不存在。** 复核开始时 `workspace/scl-gate-t3-packet/` 目录不存在（无 `TASK_PACKET.md`/`PROMPT.md`/`STATUS.yaml`/`AUTHORIZATION_PROMPT.md`），与任务描述「packet 在该目录，可能不完整」一致（执行 subagent 在聚合前因用量上限中断，主线程随后只运行了冻结的 `aggregate.py` 生成 `results.json`，未补充其它 packet 文档）。Tier-X 探针本身不强制要求 §10.1 完整委派包文档，本项仅供主线程知悉，不影响本次复核范围内的数值/记账/写入范围判定。

## 结论
6 项核查项（1 一致性、2 配对、3 独立重算、4 oracle 解释、5 记账、6/7 事故与预算、8 测试、9 写入范围）**全部 PASS**；仅 F6a（prereg C 条目文字与 attempt1 实际命令行不完全一致，且该 incident log 内部时间戳与 wall_s 存在表面不一致，判断为终端捕获交织瑕疵而非数据问题）与 F10（packet 目录此前不存在）作为非阻断评论记录。总体 **PASS_WITH_COMMENTS**，不构成对本探针数值结果或 T3 记录有效性的阻断性质疑。
