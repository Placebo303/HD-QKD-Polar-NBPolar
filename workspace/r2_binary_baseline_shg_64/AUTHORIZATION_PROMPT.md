# AUTHORIZATION PROMPT — r2-binary-baseline-shg-64 (TEMPLATE — NOT YET GRANTED)

This is a **template**. It is NOT a record of authorization already given.
Per AGENTS.md §10.1 item 1, the main thread must paste the PI's full
verbatim authorization text here (not merely link to it) before execution.

The 2026-09-29 PI direction on record so far
(`docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md` §8) is
**directional** ("按建议起草对比合同，reviewer核查合同后可以直接开始") and
does **not** by itself satisfy this template — it authorized DRAFTING the
contract and previewed a fast path to execution ONCE an independent
reviewer has checked the contract, but it does not itself confirm this
packet's specific numbers (budget in contract §6, `sc_margin` search range
in contract §3) or serve as the AGENTS.md §10.3 Pre-EXECUTE review.

---

## Copy-paste block for the PI (fill in before pasting back)

```
授权执行 r2-binary-baseline-shg-64：在 SHG _1/_2 全会话共 64 块
（docs/nbpolar/DATA_LEDGER.md §7 冻结清单，与 workspace/r2_fer_shg_64/ 同一
64 块池）上，用本仓库冻结的二元 Polar 分层译码器（d=1024，10 层，每层
N=4096，PW 构造 β=2^0.25，SC 主译码器 + CA-SCL(L=4,CRC-16) 描述性副译码器，
逐块 Toeplitz universal-hash tag 验证）做一次性描述性对比测量，不设"谁胜"
门槛。构造（每层 rate/frozen 集合）仅用 CAL32（帧 1024-1055）拟合，每层
rate 搜索的 Monte-Carlo 帧数 `CALIB_N_FRAMES=100`（基线自身 `--frames` CLI
默认值，非任意选择；`run.py` 常量，见合同 §3.1）。`sc_margin` 候选清单为
**短清单** `{0.02, 0.05, 0.08, 0.12, 0.18, 0.25, 0.30}`（7 点，非细网格扫描，
呼应基线自身 `--scl-margins` 短列表风格，`run.py::SC_MARGIN_CANDIDATES`）；
从该清单的"每层均可行（FER<0.05）"可用点中，取 (a) 与 NB-Polar
`f_book_with_crc` 最接近的一点，(b) 按 `f_book_sc` 排序后再取跨度两端 +
中点，最多凑够 **4 个** f 网格点（`MAX_F_POINTS=4`）。

预算与执行方式：**串行单进程执行**（无并行、无父进程强杀）。代码内总 wall
检查：从 main() 开始计时，总 wall ≤ ___ h（确认或修改合同提案的 4 h）；每个
session 的 construction 开始前、每块开始前各检查一次，超限后不再启动新工作，
尚未开始的块记 `status="not_started_total_wall_budget"`（不含 grid 结果、不进
D、单独计数），正在跑的那一块允许跑完。每块 wall 从块开始累计计时，上限 ≤ ___ s
（确认或修改合同提案的 1200 s，每个网格点开始前检查）；RSS 按进程 VmHWM 在每个
网格点后检查，上限 ≤ ___ GiB（确认或修改合同提案的 4 GiB），超限记
`resource_abort_rss_post_decode`。超预算不调参。串行预计耗时：construction 约
151 min（每 session 约 75 min × 2，最坏情形）+ SC 解码约 28 min，另加 CA-SCL 副臂
（C++，L=4，未实测；粗估每码字约 0.05–0.2 s、全量约 15–70 min）——合计约
3.3–4.2 h。**两遍执行顺序（主线程裁定 D_BIN_TWO_PASS）**：第 1 遍两个 session 各做
construction，然后对全部 64 块 × 选定 f 网格点只跑 SC 主臂；第 2 遍在总 wall 仍有余量时
再跑 CA-SCL 副臂，每块开始前检查总 wall，超限后尚未跑的 CA-SCL 条目记
`ca_scl_not_started_total_wall_budget`（不影响 SC 主臂的 D 和表 A/B1；表 B2 只统计已跑完的块
并写明覆盖数）。因此上限一端触及 4 h 时被截断的是副臂，不是主臂；若第 1 遍自身超时，则
按上述规则记 not_started（D<56 则报 INSUFFICIENT）。**本次执行不先跑 `--dry-run-one`**，直接全量，由代码内总 wall
检查兜底（主线程裁定，理由见 STATUS.yaml `dry_run_plan`）。（确认以此作为本次
执行的正式预算。）

判定规则：本次为描述性对比，不设通过/失败门槛；输出只做 pooled/分层
taxonomy、Wilson 95% CI、CA-SCL 描述性匹配率、与 r2-fer-shg-64 的 64 块
逐块配对四格表；undetected ≥ 1 时单列、该网格点判定搁置（不 STOP 其余
网格点）；28 个已解码块的保真度问题不适用（本包复用与 NB-Polar 完全相同
的会话重建代码路径，非独立实现）。

输出只写 workspace/r2_binary_baseline_shg_64/。one-shot，reruns=0（只允许
修复实现缺陷后重启一次，绝不因为结果不理想而重跑）。

本授权不替代 AGENTS.md §10.3 的独立 Pre-EXECUTE 和 Pre-RESULT 审查，也不
替代主线程对本次对比结论范围的最终把关（合同 §5：结论限定在本次数据/配置
范围内，不得外推）。
```

---

## Fields the main thread must confirm or amend before pasting

| Field | Contract's / `run.py`'s current frozen value | Confirmed value |
|---|---|---|
| `sc_margin` candidate list | `{0.02, 0.05, 0.08, 0.12, 0.18, 0.25, 0.30}` (7-point short list, NOT a dense sweep) | _______ |
| `CALIB_N_FRAMES` (rate-search Monte-Carlo trials/candidate) | 100 | _______ |
| Max f grid points | 4 | _______ |
| Per-block wall budget (cumulative from block start, checked before each grid point) | 1200 s | _______ |
| Per-block RSS budget (process VmHWM, checked after each grid point) | 4 GiB | _______ |
| Total wall budget (in-code check, measured from main() start) | 4 h | _______ |
| Execution mode | serial single process, TWO passes (pass 1: construction + SC primary arm on all 64 blocks; pass 2: CA-SCL secondary arm, total-wall permitting, else `ca_scl_not_started_total_wall_budget`); in-code total-wall check (not_started after 4 h); no parallelism, no hard-terminate | _______ |

Note (2026-09-29, Pre-EXECUTE F1 fix): an earlier draft of this table and
the copy-paste block above stated a dense `sc_margin` sweep
(`[0.00,0.30]` step `0.01`, i.e. 31 points) and `CALIB_N_FRAMES=4000`. Both
were revised in the contract's §3.1 (a real timing probe found the frozen
SC decoder is O(N² log N), making the dense sweep infeasible) BEFORE this
file was corrected to match. The table and copy-paste block above now
state the values actually frozen in `run.py` (`SC_MARGIN_CANDIDATES`,
`CALIB_N_FRAMES`) — verified line-by-line against `run.py`'s constants as
part of the Pre-EXECUTE F1 fix, not merely copied from the contract text.

## Gate checklist (all must be true before this template is filled and used)

- [ ] `docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md`
      reviewed and accepted by the main thread (no open blocking items;
      §11's non-blocking self-adjudications noted).
- [x] `TASK_PACKET.md` §7 aggregation implemented and unit-tested (fake data);
      round-2 additions: block accounting, error/not_started ids, INSUFFICIENT flag.
- [ ] Independent Pre-EXECUTE review of this packet: **PASS** (round 1 FAIL, round 2
      FAIL on F4 only; record the round-3 verdict here once done).
- [x] (Main-thread ruling C5) `--dry-run-one` is NOT run first; the in-code total-wall
      check (4 h) is the backstop. The dry-run feature is kept but unused for this execution.
- [ ] This file's copy-paste block filled with the PI's actual verbatim
      text (not a paraphrase) and the table above completed.
