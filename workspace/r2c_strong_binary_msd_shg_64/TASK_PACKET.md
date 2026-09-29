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

## 1. 实现要点（相对合同的操作性落地）

- L-1：`load_lab` 先设 `PYTHONDONTWRITEBYTECODE=1`、`NUMBA_CACHE_DIR=_stage/numba_cache`，复制 `msd_scl.cpp` 到 `_stage/scl_cpp/` 并重定向 `scl_fast.CPP_DIR/CPP_SOURCE`；运行前后各记 `git status --porcelain` + `src/` 文件 (path,size,mtime_ns) 快照，必须相同，否则 exit 4；记录 5 个被用文件的 `git diff --quiet` 与 sha256（provenance）。`qkd_recon/__init__.py` 仅设 `__version__`，无写盘副作用（已读源码核对）。
- 构造（`freeze_construction`，签名不含任何测试块）：不变性门（R=r_real/r_null≤1.25，残差与边缘均匀性各 20 组 8192 样本零假设）→ 8 折（连续 1024 符号）CV 择优 P-M2/P-HIST（差<0.005 nat/符号取 P-M2）→ 表（`diff_pmf`，α=0/1，clip=30）→ caps（同 pmf 的 `conditional_capacities`）。R>1.25 ⇒ STOP，只写 `construction_frozen_*.json`，无 part/results（D2）。
- DE：每层根 = M_root=4096 个 (a,δ~pmf,b,prefix=a 的高 i 位) 的对称对齐 LLR `L·(1−2a_i)`；`de_llr_populations_from_root(n_log=15, n_samples=1024, seed=20260929)`；`de_order_from_population` 得 reliable-first 序。
- k_i(μ)=floor(N·max(0,caps_i−μ))，k_i<16 ⇒ 整层披露；f(μ)=(Σ(N−k_i)+64)/(H_total·N)；对目标 f 取**满足 f(μ)≥目标的最小 μ**（确定性二分）。
- F3：对 f∈[1.10,1.90]（操作者选定，见 §3）做 4 步二分，每步评估设计集（M_design=256 帧/层，公共随机数：随机流只依赖 (session,layer,块序)，与 k 无关；真前缀；冻结位=Alice 真 u，信息位置零后传入引擎），`Σp̃_i≤0.03` 则上界下移；F3=最终上界；F4=F3+0.10。整层披露层 p̃=0。
- 译码：逐层 0→9 硬前缀，前层出错继续（无早停、无 genie）；整层披露层直接取 Alice 值计入前缀；块判定=32768 符号逐符号全等；64 比特 Toeplitz tag（R2B 约定：`src.reconciliation.verification.universal_hash_tag`，layer_id=0，block_index=global_block_index，消息=10 比特 MSB 优先序列化）；`undetected`=tag 过 ∧ 非 exact，单列。
- 每码字 wall 监控：超 T0 校准计时的 5×（且 ≥2 s）⇒ 该 (块,f 点) 记 `resource_abort_codeword_wall`，不进分母，不静默丢弃。总 wall 超预算 ⇒ 未开始的块记 `not_started_total_wall_budget`。

## 2. 验收项（ID）

- T0a lab import 与 stage 编译成功且 lab 无新增文件；T0b `fit['joint']` 循环结构 + P-M2 投影；T0c N=32768/L=16 计时 + RSS（重，`R2C_HEAVY=1`）；T0d 位面/前缀/LLR 符号约定。
- T1a 全表 L≥2^k 的 `decode_batch` == 引擎自身 min-sum 度量的穷举最优（pm 一致），并与 numba `scl_decode_batch` 逐位一致；T1b 全 0 冻结值失败/真值成功；T1c 整层披露、k<MIN_K、`K_frozen(μ)` 单调、f 记账手算；T1d DE 根符号对齐（阈值预注册在测试内）。
- T2a 合成全链路记账自洽；T2b 无测试块泄漏（签名 + AST + 毒化测试块运行时输出不变）；T2c 与 lab `polar_run` 层循环独立复现逐层逐位一致（合成数据）；T2d N=32768/L=16 合成冒烟（重）。
- T3 全流程（合成）+ strict replay（1 进程 vs 2 进程逐字段一致）+ lab 前后不变 + NB 配对表 + 分层表。
- 运行测试命令见测试文件头；`R2C_HEAVY=1` 才跑重项。

## 3. 需主线程/PI 知悉的操作者选择与合同摘录问题（不改冻结参数）

见 `PROMPT.md` 末尾"回报给主线程的偏差清单"，逐条列出。

## 4. 返回条件

全部完成，或具体阻塞（失败命令 + 完整报错 + 已尝试补救 + 需主线程决定的单一事项）。
