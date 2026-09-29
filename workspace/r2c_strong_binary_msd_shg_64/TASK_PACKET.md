# TASK PACKET — r2c-strong-binary-msd-shg-64

合同：`docs/nbpolar/R2C_STRONG_BINARY_MSD_CONTRACT_20260929.md`（PI 2026-09-29 批准 D1–D8 推荐项）。
本包**不授权任何事**；授权文本见 `AUTHORIZATION_PROMPT.md`，STATUS.yaml `authorizations` 为空。
前驱（只读）：`workspace/r2_fer_shg_64/`（NB-Polar，提供 H_total、F2 目标、`part_*.json` 配对）、`workspace/r2_binary_baseline_shg_64/`（R2B，标签/块判定约定）。

## 0. 文件与边界

| 项 | 路径 |
|---|---|
| 算法库（新增） | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/r2c_msd_binary.py`（按文件路径加载，不改包 `__init__`） |
| 测试（新增） | `comparison_bench/tests/test_r2c_msd_binary.py`；`workspace/r2c_strong_binary_msd_shg_64/_test_run_driver.py` |
| 驱动 | `workspace/r2c_strong_binary_msd_shg_64/run.py`（`--authorize` 才碰真实数据；`--dry-run` 纯合成，写 `dry_run/`） |
| 允许写（执行时，新增，不得预先存在） | 本目录 `results.json`、`part_<G2|G3>_<global_block_index:02d>.json`（64）、`construction_frozen_<G2|G3>.json`、`lab_readonly_check.json` |
| `_stage/` | lab 引擎编译产物 + numba cache（非证据，`.gitignore`） |
| 禁止 | 改 `src/ experiments/ tools/`、前驱目录、`results/`、`comparison_bench/outputs_comparison/`；写 `D:\Code\qkd-reconciliation-lab`；读池外帧；git 写操作；无授权运行 `run.py --authorize` |

## 1. 实现要点（相对合同的操作性落地；含 PI 修订 E1/E2，2026-09-29）

- L-1：`load_lab` 先设 `PYTHONDONTWRITEBYTECODE=1`、`NUMBA_CACHE_DIR=_stage/numba_cache`，复制 `msd_scl.cpp` 到 `_stage/scl_cpp/` 并重定向 `scl_fast.CPP_DIR/CPP_SOURCE`；运行前后各记 `git status --porcelain` + `src/` 文件 (path,size,mtime_ns) 快照，必须相同，否则 exit 4；记录 5 个被用文件的 `git diff --quiet` 与 sha256（provenance）。`qkd_recon/__init__.py` 仅设 `__version__`，无写盘副作用（已读源码核对）。
- 模型（`freeze_construction`，签名不含任何测试块）：不变性门（R=r_real/r_null≤1.25，残差与边缘均匀性各 20 组 8192 样本零假设）→ 8 折（连续 1024 符号）CV 择优 P-M2/P-HIST（差<0.005 nat/符号取 P-M2）→ 表（`diff_pmf`，α=0/1，clip=30）→ caps（同 pmf 的 `conditional_capacities`）。R>1.25 ⇒ STOP，只写 `construction_frozen_*.json`，无 part/results（D2）。
- **E1 构造（genie-SC Monte Carlo，替换采样 DE；`genie_mc_order`）**：每层用**选定的 CAL32 拟合 pmf** 合成 4096 帧 (a,b)（a 均匀，b=(a+δ) mod 1024，δ~pmf），真前缀、真 u=polar_encode(该层比特平面)；genie SC（真 u 反馈）f 节点 = 原生引擎同款 min-sum，g 节点 `r+(1−2b_l)·l` 无截断；每个叶子 s=LLR·(1−2u)，Z_j=mean_frames exp(−s_j/2)；顺序=按 Z 升序（reliable-first），平局按 mean s 降序（`np.lexsort((-S, Z))`）。种子 = 20260929+7 000 000+1000·session_idx+layer（与设计集 20260929+1000·idx+layer、零假设 20260929+idx 区分）。`de_order`/`de_root_llr` 保留在库中，**不在 run 路径使用**。
- k_i(μ_i)=floor(N·max(0,caps_i−μ_i))，k_i<16 ⇒ 整层披露；f=(Σ(N−k_i)+64)/(H_total·N)。
- **E2 逐层 μ_i（F3，`DesignEvaluator.solve_layer_mus` + `_mu_task`）**：设计集 M_design=**1024** 帧/层/评估点（主线程允许的实现选择：0.03/n_active=0.003 在 M=256 下只允许 0 个错误，M=1024 允许 ≤2 个错误；p̃_i=(e_i+0.5)/(M+1)）。n_active=μ=0 时 k_i≥16 的层数（真实数据预期 10）；每层阈值 thr=0.03/n_active。每层独立求满足 p̃_i≤thr 的最小 μ_i：先试 μ=0（失败即早停），再在 [0, min(cap_i, 0.30)] 上二分 7 步（分辨率≈0.0023 bit）；设计帧对该 (session,layer) 用同一随机流（公共随机数，与 k 无关，前缀取真值，冻结位=真 u、信息位置零后传入引擎）；评估中一旦错误数 > e_max 即早停并判失败（失败评估不进缓存/统计；通过评估为完整 M 帧）。若 7 步内无通过则评估上沿一次并加 flag（`mu_upper_bracket_edge_*`）。F3 向量 = 各层 μ_i；F3 的 f 由此得到。整层披露层 p̃=0，不计入 Σ。
- **F1/F2/F4（固定目标 f）**：以 F3 的 μ_i 向量为形状，统一平移 Δ（μ_i+Δ，截断到 ≥0），对 f(Δ)≥目标取最小 Δ（确定性二分，Δ∈[−max μ_i, max cap_i]）。F1=1.20，F2=NB f_book_with_crc（每会话），F4=f(F3)+0.10。各点做一次完整设计集评估，仅记录预测 Σp̃，**不据此改 k**。测试块不参与构造/μ_i/Δ。
- 译码：逐层 0→9 硬前缀，前层出错继续（无早停、无 genie）；整层披露层直接取 Alice 值计入前缀；块判定=32768 符号逐符号全等；64 比特 Toeplitz tag（R2B 约定：`src.reconciliation.verification.universal_hash_tag`，layer_id=0，block_index=global_block_index，消息=10 比特 MSB 优先序列化）；`undetected`=tag 过 ∧ 非 exact，单列。
- 每码字 wall 监控：超 T0 校准计时的 5×（且 ≥2 s）⇒ 该 (块,f 点) 记 `resource_abort_codeword_wall`，不进分母，不静默丢弃。总 wall 超预算 ⇒ 未开始的块记 `not_started_total_wall_budget`。
- 结果附加信息（描述性）：`construction_frozen_*.json` 含每层 genie 序摘要（sha/首尾位置）、每层 μ_i 二分轨迹、各点逐层设计 p̃ 与 `sum_Z_info_set`（info 集上 Z 之和，genie 统计量）。

## 2. 验收项（ID）

- T0a lab import 与 stage 编译成功且 lab 无新增文件；T0b `fit['joint']` 循环结构 + P-M2 投影；T0c N=32768/L=16 计时 + RSS（重，`R2C_HEAVY=1`）；T0d 位面/前缀/LLR 符号约定。
- T1a 全表 L≥2^k 的 `decode_batch` == 引擎自身 min-sum 度量的穷举最优（pm 一致），并与 numba `scl_decode_batch` 逐位一致；T1b 全 0 冻结值失败/真值成功；T1c 整层披露、k<MIN_K、`K_frozen(μ)` 单调、f 记账手算；T1d DE 根符号对齐（旧路径，保留）；T1e genie 统计量==独立标量递归 + BSC 上与 lab DE 序 top-N/2 重合≥0.85；T1c 含逐层 μ_i 向量 k/f 记账、统一平移 Δ 单调性与二分、n_active、M_design 可分辨性。
- T2a 合成全链路记账自洽；T2b 无测试块泄漏（签名 + AST + 毒化测试块运行时输出不变）；T2c 与 lab `polar_run` 层循环独立复现逐层逐位一致（合成数据）；T2d N=32768/L=16 合成冒烟（重）；T2e genie 构造对 r2c-layer-diag 已知坏位（layer 8 位 16727/16943/16702，μ=0.084 k=23141）不进信息集（重）；T2b 含毒化测试块不改变构造（含 E1/E2 函数签名/AST）；`_t3_realscale_synth.py` 全规模合成冒烟（每会话 ≥8 块）。
- T3 全流程（合成）+ strict replay（1 进程 vs 2 进程逐字段一致）+ lab 前后不变 + NB 配对表 + 分层表。
- 运行测试命令见测试文件头；`R2C_HEAVY=1` 才跑重项。

## 3. 需主线程/PI 知悉的操作者选择与已知局限（不改冻结参数）

操作者选定（合同/PI 修订未指定）：(1) E2 每层二分区间 [0, min(cap_i,0.30)]、7 步、先试 μ=0；(2) n_active 定义=μ=0 时 k_i≥16 的层数（合成/预期真实=10，thr=0.003）；(3) M_design=1024（主线程允许；e_max=2）；(4) 设计帧公共随机数、通过评估完整 M 帧、失败评估早停不入统计；(5) genie 种子基数 20260929+7 000 000+1000·idx+layer；(6) 平移 Δ∈[−max μ_i, max cap_i]，最小 Δ 使 f≥目标。
局限（描述性，非阻塞）：(a) **合成帧无尾部**：P-M2 pmf 底值 1e-15，设计集/genie 帧不含真实数据中约 1e-6 量级的尾部符号（全规模合成冒烟中被测块采样自含 1e-9 底值尾部的信道，而 CAL32 拟合看不到它），设计预测 Σp̃ 可能低估块失败；(b) F3 的 μ_i 用设计集选出后又用同一设计集报告预测（选择偏差，CRN），测试块独立；(c) 每层二分在 MC 噪声下非严格单调，取二分终点；(d) 设计集 e_max=2/1024 的分辨率使 Σ 目标 0.03 只是近似。

全规模合成冒烟（`_t3_realscale_synth.py 4 8 2`，d=1024,N=32768,L=16，M_design=1024，genie 4096 帧，每会话 8 块，≤4 进程）：总 wall 3418 s（genie 构造 CPU 合计 433 s，20 层；设计集/二分/8 次评估其余；块译码含其中）；单码字计时 0.31 s；RSS 构造任务峰值 0.65 GiB、设计任务 0.15 GiB。真实运行 32 块/会话，块译码比冒烟多约 4×（2560 码字≈<15 min 串行 4 进程），预计总 wall ≈ 1–1.5 h，远低于 6 h 预算。

## 4. 返回条件

全部完成，或具体阻塞（失败命令 + 完整报错 + 已尝试补救 + 需主线程决定的单一事项）。
