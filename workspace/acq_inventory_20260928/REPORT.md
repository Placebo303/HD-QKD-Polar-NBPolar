# 采集配置盘点 + 现有分段规则 + 候选会话计帧（2026-09-28）

只读盘点，遵守 AGENTS.md。头文件配置一律用 TimeTagger.FileReader(path).getConfiguration()
（primary .ttbin only，从不打开 .1），未调用 hasData()/getData()/getLastMarker()
等任何事件流 API。第 (f) 节的计帧步骤是 PI/协调者 2026-09-28 追加授权的例外：
对参照会话与 1 个候选会话调用了冻结后处理链（含事件流读取），仅用于计数，
未做先验拟合、delta统计、解码、tag 计算，未把任何帧内容写入磁盘。
未解码，未写入 results/ 或 comparison_bench/outputs_comparison/，未做 git 操作。

TimeTagger 包核实（PI 2026-09-28 追加要求）：/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python
里没有装 TimeTagger（ModuleNotFoundError）。实际用的是 /home/karel_303/.venvs/timetagger/bin/python，
模块文件 /home/karel_303/.venvs/timetagger/lib/python3.12/site-packages/Swabian/TimeTagger/__init__.py，
getVersion()=2.22.6，即官方 PyPI 包 Swabian-TimeTagger（与 docs/troubleshooting.md 和
AGENT_PROJECT_MEMORY.md 2026-09-21 intake 记录的安装位置一致，也是 G2/G3 production 用的同一个 venv）。
头文件配置用 TimeTagger.FileReader(path).getConfiguration()（本机返回 Python dict，不是 JSON 字符串，
已用 json.dumps 落盘为 JSON）。计帧用的 _read_timetags_production/_read_timetags_g3_production，
底层是 src/qkd_io/ttbin_pipeline.py 里的 read_ttbin_events()，其内部就是
from TimeTagger import FileReader; reader = FileReader(str(p)); reader.hasData()/reader.getData(...)——
官方 API，不是自写二进制解析器。两步全部用的官方包，无需作废重读。

原始数据来源：docs/nbpolar/RAW_DATA_INVENTORY_20260921.md。
配置工具脚本（scratch，未提交到仓库）：read_config.py / count_frames.py。
完整配置见同目录 configs.json；完整计帧结果见 frame_census.json；
参与账本见 participation_ledger.json。

## (a) 两个参照会话配置摘要

两者共用同一台 Time Tagger X（serial 222300114U, FPGA ID 98467210997048069,
PCB 1.1 (1), firmware TT-X FW6 TS 2024-02-21 17:27:46 OK 1.45, min sw 2.14.0），
软件版本 2.20.2，resolution HighResB，led disabled，无 fpga link，无 network server。

### SHG _1（20260113_SHG_Type2PPLN_3s）

- current time（采集起始）: 2026-01-13 16:21:06 +0800
- registered channels（configuration 级）: [1, 5, 9, 13, 17]（5 路输入均配置，
  但 FileWriter 只落盘 [1001, 1, 5]——9/13/17 未写入本次 ttbin，只是硬件保留配置）
- inputs（仅取 ch1/ch5，本项目固定 HW_A=1/HW_B=5）：
  - ch1: trigger level 0.5 V, deadtime [1333,1333] ps, delay hardware [293,0],
    delay software [0,0], hardware delay compensation [0,0], event divider [1,1],
    resolution HighResB, resolution rms 1.5, normalization [False,False],
    test signal False, conditional filter filtered/triggers [False,False],
    input hysteresis 20, input impedance high False, input mux 0
  - ch5: trigger level 0.5 V, deadtime [1333,1333] ps, delay hardware [0,0],
    delay software [0,0], hardware delay compensation [703,703], event divider [1,1],
    resolution HighResB, resolution rms 1.5, normalization [False,False],
    test signal False, 其余同 ch1
- hardware buffer size: 67108864
- stream block size events: 1048576; latency 20
- measurements 注册: Coincidences(groups=[[1,5]], window=1000, virtual ch 1001),
  Counter x2 (binwidth 1e11/2e10), Countrate([1,5]), Correlation(ch1=5,ch2=1,binwidth=1,
  n_bins=1000), FrequencyCounter([1,5]), FileWriter(channels=[1001,1,5],
  filename=D:\SPDC源测试\2026.1.13\SHG_Type2PPLN_3s_2026-01-13_162106.ttbin)
- 目录/文件名信息：SHG_Type2PPLN（SHG 上转换 + Type-II PPLN 源标签），3s 采集时长，
  日期 2026-01-13

### SHG _2（20260113_SHG_Type2PPLN_3s_2）

- current time: 2026-01-13 16:21:48 +0800（比 _1 晚 42 秒，同日第二次运行）
- registered channels: [1, 5]（只注册 2 路，不含 9/13/17）
- inputs ch1/ch5：与 _1 的 ch1/ch5 逐字段完全一致（trigger level、deadtime、
  delay hardware/software、hardware delay compensation、resolution=HighResB、
  resolution rms 1.5、normalization=False、test signal=False 等，无一项不同）
- measurements/FileWriter：同 _1，filename 换成
  ...SHG_Type2PPLN_3s_2_2026-01-13_162148.ttbin
- 目录/文件名信息：与 _1 同一天、同一源标签，_2 是当天第二次运行序号（不是亮度）

结论：两个参照会话的 ch1/ch5 采集电子学配置逐字段相同（仅 _1 额外注册了
3 路未写盘的监控通道）。这是本次比对表的基准。

## (b) 全部 ttbin 头文件配置比对表（vs SHG _1 的 ch1/ch5 逐字段 diff）

| 会话 | 日期 | resolution | 与参照配置是否一致 | 不一致字段（ch1/ch5，取值：参照到本会话） | 清单帧数 | 是否已被使用 |
|---|---|---|---|---|---|---|
| 20260112_Type2PPLN_3s | 2026-01-12 | HighResB | 基本一致 | 仅 ch1 delay hardware 289 到 293 ps（微小，ch5 完全一致；resolution/normalization/rms 三项均相同） | 未知（清单未计） | 否（仅被 2026-09-21 FileReader 去重探针读过一次，未做 CAL/解码；本次(f)节已计帧，见下） |
| 20260113_SHG_Type2PPLN_3s（参照 G2） | 2026-01-13 | HighResB | 参照本身 | 无 | 未知，本次已计帧 4219（含 CAL/CHAR/HELDOUT/EVAL 全消耗） | 是——G2 全流程消耗至 frame 4189，RESERVE 29 未用（decision-log.md:137,:5511） |
| 20260113_SHG_Type2PPLN_3s_2（参照 G3） | 2026-01-13 | HighResB | 参照本身 | 无 | 未知，本次已计帧 4289 | 是——G3 全流程消耗至 frame 4189，RESERVE 99 未用（decision-log.md:137,:5558） |
| 20260120_Type0_nofilter_500K_3s | 2026-01-20 | Standard | 不一致 | resolution HighResB 到 Standard；resolution rms 1.5 到 2.0；normalization [F,F] 到 [T,T]；ch1 delay hardware 289 到 55 | 未知 | 部分——2026-09-21 SKIP0_MINIMAL_SIZING_DESCRIPTIVE census：CAL128 @ w500/w1000 有 2 个 defensible H 格（decision-log.md:5382/:5386），非 CAL/EVAL 消耗，仅描述性 H |
| 20260120_Type0_nofilter_1M_3s | 2026-01-20 | Standard | 不一致 | 同上（ch1 delay hardware 289 到 55） | 未知 | 部分——同一 census，CAL256 @ w500 有 1 个 defensible H 格 |
| 20260120_Type0_nofilter_1_5M_3s | 2026-01-20 | Standard | 不一致 | 同上 | 未知 | 部分——同一 census，无 defensible 格（peak sigma176，覆盖/纯度冲突） |
| 20260120_Type0_nofilter_2M_3s | 2026-01-20 | Standard | 不一致 | 同上 | 未知 | 部分——同一 census，无 defensible 格（peak sigma233） |
| 20260121_Type2_1-5M_3s | 2026-01-21 | Standard | 不一致 | resolution/rms/normalization 同上；ch1 delay hardware 289 到 -126；ch5 delay hardware 0 到 33 | 未知 | 是——V25 三源之一（type2_1p5M_20260121_183806，decision-log.md:5417），已用于冻结经验信道/训练集 |
| 20260121_Type2_1M_3s | 2026-01-21 | Standard | 不一致 | 同上 | 未知 | 是——V25 三源之一（type2_1M_20260121_184040） |
| 20260121_Type2_2M_3s | 2026-01-21 | Standard | 不一致 | 同上 | 未知 | 是——V25 三源之一（type2_2M_20260121_183657） |

注：registered channels 差异（20260121_Type2_* 多注册 ch9）不影响 ch1/ch5 本身配置，未单列。

## (c) 候选新源清单（配置一致 + 未被用过 + 帧数已知）

按严格标准（配置逐字段一致 AND 未被 CAL/EVAL 消耗 AND 帧数已知）：

- 20260112_Type2PPLN_3s：配置基本一致（仅 ch1 4ps 硬件延迟差，可忽略），未被
  CAL/EVAL 消耗。第 (f) 节已按冻结链计帧：总配对数仅 4782（window=200），
  远小于 skip=702 帧所需的 179712 配对——INSUFFICIENT，可用 EVAL 块数 = 0。
- 其余 7 个会话（4个Type0_nofilter, 3个Type2 V25）配置均与参照不一致（resolution
  Standard vs HighResB 等），未进入本次计帧范围（按协调者 2026-09-28 追加指示的
  范围限定：只对配置一致且未用的候选计帧）。

本次盘点的候选新源数 = 0（无同时满足配置一致加未用加有可用帧数的会话）。

## (d) 头文件里没有、需要实验室补充的参数

头文件 getConfiguration() 只有电子学/采集参数，以下光学/光子学参数不在头文件里，
需要实验室记录补充：

- 泵浦功率 / 泵浦亮度（brightness）——目录名里的 500K/1M/1_5M/2M/1-5M 只是
  文件命名里的人工标注 token，不是头文件字段，且语义未定义（未知单位、未知是计数率
  还是泵浦功率刻度）
- 损耗设置（衰减器/损耗 dB）——RAW_DATA_INVENTORY_20260921.md Q4 已确认：10 个新
  会话文件名中都没有 _0dB 风格 token，损耗未知
- 实测计数率 / 符合率（真实单通道 cps、符合 cps）——头文件只有 deadtime/trigger
  level 等硬件设置，不含运行时实测速率（measurements 里的 Countrate/Counter
  只是配置了哪些测量通道，不含具体数值——数值在事件流里，本次未读取）
- 环境温度、PPLN 晶体温度/相位匹配点、SHG 转换效率等光学台架参数
- 采集操作员/备注字段——getConfiguration() 没有 free-text 备注/操作员/测量名字段
  （measurements[].name 只是固定的测量类型名如 Coincidences/Counter，不是自由
  文本备注）

## (e) 现有分段规则（CAL / CHAR / HELDOUT / EVAL / RESERVE）

出处：.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/g2_freeze_config.json
（G3 版 .workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/g3_freeze_config.json 的
disjointness_matrix/eval_blocks/skip_frames/pairing_window_* 字段与 G2 逐字节
相同，两会话共用同一套切分参数）。

配对与切帧参数：
- pairing_window_primary (W_P) = 200 —— g2_freeze_config.json:1676
- pairing_window_sensitivity (W_S) = 500 —— g2_freeze_config.json:1677（仅用于
  G1R2 readout 敏感性自检，不是实际配对窗口）
- mod_boundary = CIRCULAR —— g2_freeze_config.json:1675
- skip_frames = 702 —— g2_freeze_config.json:1678；同一常量定义于
  scripts/census_intake_20260921.py:84（SKIP_FRAMES = 702）
- 每帧长度 = 256 配对/帧（FRAME_PAIRS）—— scripts/census_intake_20260921.py:64；
  等价常量 G1_FRAME_PAIRS = 256 于 scripts/m2_prior_validation.py:346
- 每块 = 128 帧（由 eval_blocks 每段区间长度验证，如 [2398,2525] = 128 帧，
  见下）—— g2_freeze_config.json:1680-1737
- 实际配对循环实现：pair_narrow_nearest_unique() ——
  scripts/m2_prior_validation.py:945-978
- 切帧实现（skip + 定长分块 + 丢弃尾部不完整帧）：chunk_frames() ——
  scripts/m2_prior_validation.py:984 起

五段在参照会话里的帧区间（post-skip 编号，即 chunk_frames 输出的帧序号 0..N-1）：

| 段 | 帧区间 | 长度（帧） | 用途 | 出处 |
|---|---|---|---|---|
| A1_CAL（M0 incumbent） | 0-1023 | 1024 | M0 先验 1024 帧拟合（incumbent arm） | g2_freeze_config.json:1069-1072（disjointness_matrix.segments.a1_cal） |
| CAL32（M2 candidate） | 1024-1055 | 32 | M2 候选先验 32 帧拟合 | g2_freeze_config.json:1073-1076（cal32）；帧号列表 cal_frame_ids 于 :1030-1063 |
| CHAR（特征化） | 1056-1837 | 782（等于200192 配对除以256） | delta-tail / NLL 特征化样本 | g2_freeze_config.json:1077-1080（char）；char_sample_pairs=200192 于 :1065 |
| HELDOUT（留出） | 1838-2397 | 560 | M0/M2 NLL 打分留出集 | g2_freeze_config.json:1085-1088（heldout）；帧号列表 heldout_frame_ids 于 :1113-1673 |
| EVAL | 2398-4189 | 1792（等于14x128） | 实际解码评估，14 个 128 帧块 | g2_freeze_config.json:1081-1084（eval）；14 个块区间列表 eval_blocks 于 :1680-1737（如 [2398,2525]……[4062,4189]，每段 128 帧） |
| RESERVE | 4190到ledger末尾 | G2: 29（4190-4218）；G3: 99（4190-4288） | 未用 | decision-log.md:5511（G2 reserve 4190-4218 (29), no id >=4219）；decision-log.md:137,:5558（G3 RESERVE 99 untouched）；本次 (f) 节实测复现 |

互斥判定：g2_freeze_config.json:1090-1103 的 pairwise_overlap 显式给出全部
10 对段间重叠计数，值全为 0，且 all_disjoint 为 true——即由该 JSON 自带的组合式
互斥校验保证，不是靠帧号区间目测。段与段之间没有额外间隔/排除缓冲——CHAR 紧接
CAL32 之后（1056=1055+1），HELDOUT 紧接 CHAR 之后（1838=1837+1），EVAL 紧接
HELDOUT 之后（2398=2397+1），RESERVE 紧接 EVAL 之后（4190=4189+1）；唯一的跳过
缓冲是最前面的 skip_frames=702（在 post-skip 编号之前，即从原始配对流跳过
702x256=179712 个配对后才开始编号为帧 0）。

## (f) 候选会话计帧结果（decoder-free frame census，冻结链复用）

调用链严格复刻 workspace/m2_scl_rescue_g2g3/run.py 的顺序：
_read_timetags_production/_read_timetags_g3_production 到 _align_frozen 到
_yield_sweep_selfcheck 到 _sweep_accept 到 pair_narrow_nearest_unique(window=200)
到 chunk_frames(skip=702)。只输出计数，未做先验拟合/delta统计/解码/tag计算，未写帧
内容到磁盘。完整结果见 frame_census.json。

参照会话核对（先算参照，核对通过才继续候选）：

| 会话 | n_events | n_pairs (W=200) | align status | peak_to_bg | offset (ps) | sweep 自检 | n_frames_post_skip | RESERVE | 与已知值核对 |
|---|---|---|---|---|---|---|---|---|---|
| SHG _1 (G2) | 16130065 | 1259992 | ok | 1366.27 | 50 | within-one-step PASS | 4219 | 29 | 与 decision-log.md:143/:5511 的 ledger 4219/reserve 29 完全一致 |
| SHG _2 (G3) | 16344777 | 1277938 | ok | 1385.55 | 50 | within-one-step PASS | 4289 | 99 | 与 decision-log.md:119/:137/:5558 的 ledger 4289/RESERVE 99 完全一致 |

两个参照会话都 n_frames_post_skip 大于 4189（EVAL 结束帧），即 RESERVE 段确实存在，
核对通过——按指示继续计算候选会话。

候选会话：

| 会话 | n_events | n_pairs (W=200) | align status | peak_to_bg | offset (ps) | 结果 |
|---|---|---|---|---|---|---|
| 20260112_Type2PPLN_3s | 3836088 | 4782 | ok | 121.5 | -50 | chunk_frames 报错：stream of 4782 pairs shorter than skip 179712——0 帧、0 块，数据量不足以跳过 skip=702 |

n_events=3836088 与 offset=-50、peak_to_bg=121.5 与 2026-09-21 去重探针记录的数值
完全一致（交叉核对通过），但窄窗口（W=200）配对后只剩 4782 对——该会话虽然总事件数
不少，但 ch1/ch5 符合率（在 200ps 窗口内）远低于 SHG 会话，物理上不可用作 EVAL 源。

## (g) 参与账本 + 两种切法下的块数方案

完整账本见 participation_ledger.json（5 条记录：SHG _1/_2/20260112 三个
被计帧的会话 + 4个Type0_nofilter/3个Type2 的仅头文件记录）。

方案 A（照搬参照的五段切法）：CAL(1024)+CAL32(32)+CHAR(782)+HELDOUT(560)+
EVAL(1792等于14块) 共占 4190 帧固定开销，每会话额外 EVAL 块数等于
floor((n_frames_post_skip 减 4190) / 128)。SHG _1/_2 自身的 RESERVE（29/99 帧）
都小于 128，0 个额外块。此方案对 EVAL 高度吝啬（94% 帧数被 CAL/CHAR/HELDOUT
占用），不是达到 65 块的现实路径，除非有多个接近 SHG 规模（约 4200+ 帧）的全新会话。

方案 B（PI 对照方案：CAL 仍 32 帧，其余全部划 EVAL，留一个小 RESERVE）：
eval_blocks_per_session = floor((n_frames_post_skip 减 32 减 RESERVE) / 128)。用
SHG 规模举例（仅作公式演示，非真实新块）：RESERVE=0 时 SHG_1到32 块、SHG_2到33 块；
RESERVE=128 时 SHG_1到31 块、SHG_2到32 块。达到 65 块所需会话数：RESERVE=0 时约
2 个 SHG 规模的全新会话；RESERVE=128 时约 3 个。此方案目前
没有任何冻结配置或真实数据执行先例，采用前需要新的 OpenSpec 变更 + freeze review
（AGENTS.md 第3/第10.3节）。

关键限制：以上两个方案目前都没有可套用的新会话——本次盘点找到的唯一
配置匹配候选（20260112_Type2PPLN_3s）配对数只有 4782，不足以形成一个 128 帧块，
遑论 65 块。两个方案只列选项，不替 PI 做选择；是否放宽配置需与参照逐字段一致的
标准（例如接受 Type0_nofilter/Type2 会话尽管 resolution/normalization 不同——注意
这是采集电子学设置层面的不一致，不同于 PI 之前裁定的 Type0/SHG 只是光源差异、
对 IR 过程无影响那个物理源层面的问题），或寻找全新会话，由 PI 决定。
