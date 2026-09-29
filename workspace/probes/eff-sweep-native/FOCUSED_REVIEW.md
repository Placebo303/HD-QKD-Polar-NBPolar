# FOCUSED_REVIEW (Tier-X, reviewer-go) — eff-sweep-native
判定: PASS_WITH_COMMENTS（无阻断项；结果可作 Tier-X 非声明性探针数据，不得升格为 claim）

复核脚本: review_scratch/recheck.py（仅读 results.json / design.json）

- F1 (a) prereg 与运行一致: 网格 L16×{1.15,1.18,1.20,1.22,1.25}、L32×{1.15,1.18,1.20}、SC 臂 {1.20,1.25}、种子 2026093010/11、16块/种子=32块、top_m=4、threads=4 与 results.json/run.py 完全一致；32 块未降档，reruns=0，总墙钟 8784 s。
- F2 (b) 设计复用: H/H1/H2 直接读 scl-gate-t3/design.json（design_seed 2026093000, MC=64, status ok, 无重算，复用本身即确定性）；H1均值0.025466+H2均值0.791080=0.816546 vs H=0.816514，差3.3e-5，通过。
- F3 (c) 独立重算全部吻合: 8 个 SCL 点+2 个 SC 点的 exact/verify_failed/undetected(全为0)/decode_failed(0)/resource_abort(0)、FER、Wilson95(z=1.959964)、total=round(f·H·N/5)、k1=round(0.0469·total)、k2、f_book_no_crc=5·total/(H·N)（1.1500…1.2500）、f_book_with_crc=(5·total+16)/(H·N)（1.1506…1.2506）均一致。undetected=0 且未并入 FER；FER=非 exact 比例。
- F4 (d) monkeypatch: t3 通过 `scl_joint.scl_joint_decode` 模块属性调用，替换生效；native 模块以 scl_joint_mod 引入原模块（仅取类型/CRC 等），未回调被替换名，无递归。SC 臂走 tl.run_two_layer_block→sc_decode，不经 scl_joint，不受影响。线程数/taskset 只影响时间；native 文档称"FER 分布一致"（非承诺逐比特），故为非阻断提示（见 C2）。
- F5 (e) 配对: 所有 10 个点的 (seed,block) 集合完全相同（32 块，gen_block 同一 rng）。配对: f=1.20 SC 20 exact，L16 多救 9、L32 多救 11、SC-only=0；f=1.25 SC 28，L16 多救 3、SC-only=0。
- F6 (f) truth 隔离: truth 仅用于生成 CRC/披露值/tag/最终比对，与 t3 已审代码相同；写入仅限本探针目录（results_partial.json 已不在；run_log/smoke_note 属本目录）；未见越界写入，未用真实数据；reruns=0。
- F7 (g) 单调性: L16 FER 0.500/0.094/0.094/0.063/0.031，非严格递增但不违反单调；1.18 与 1.20 失败块同为 (10,13),(11,1),(11,8)——增加约 107 个披露坐标未改变这 3 个"难块"，且失败集随 f 上升嵌套收缩（1.22: 两块, 1.25: 一块），说明失败由个别块信道实现主导，属合理而非异常。L32: 0.375/0.063/0.031，同样嵌套。L32 在同 f 下 ≤L16。
- C1 统计力度: n=32，Wilson 区间很宽（如 3/32 → [0.032,0.242]），各相邻点区间大幅重叠。"FER≤~0.05 的最小 f" 只能粗略表述为: L16 ≈1.25（1/32，上限0.157），L32 ≈1.20（1/32），不能说 L16 与 L32 的差异显著；不应据此定稿阈值。
- C2 transcript 中 CPU 检查时间点（11:36、11:56、12:06）不在 cpu_check_log.txt（实际 11:04/11:24/11:44/12:04）；日志只到 12:04 二进制进程退出后为 NO_BINARY_PROCESS。不影响正确性，建议更正 transcript。
- C3 f_nominal 用 no-CRC 定义；含 CRC 高 0.0006，已如实并列记录。

结论: 数值、配对、隔离均通过，仅有说明性意见 C1–C3。
