# RESULT_SUMMARY — r2-fer-shg-64

配置：M2 先验 + SCL(L=16, top_m=4, CRC-16)；K1=319 / K2=6492；P16 construction
digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`；
W_P=200 / W_S=500 / CIRCULAR / skip=702；`tag_master_shared=2026102801`，
`eval_seed_shared=2026092801`。样本源：SHG `_1`/`_2` 全会话冻结 64 块池
（`docs/nbpolar/DATA_LEDGER.md` §7）。

**主线程裁定（2026-09-29）**：Pre-RESULT 独立审查结论为 **PASS**
（`PRE_RESULT_REVIEW.md`）。按冻结判定规则：`D=64 ≥ 56`，`undetected=0`，
`fidelity_compromised=false` ⇒ 裁定为 **`FER_MEASURED_AT_CONTRACT`**。
M2 状态由 `VALIDATED_AT_FROZEN_CONTRACT`（第 2 级）晋级为
**`FER_MEASURED_AT_CONTRACT`**（第 3 级）。下一级门是 **R3**（效率门：
verification-aware f_eff + 运行时/RSS 上界），尚未开始；本次measurement
不晋级到 R3 或更高级。

---

## 1. 汇总表（pooled）与分层表并列（P-1）

P-1 裁决：允许给出 64 块汇总 FER 数字，但必须与三层分层表同表并存，不得只给
一个未分层数字。以下汇总表（`taxonomy_pooled`）与两套分层表（`stratum_task`
细分、`stratum_official` 契约口径）逐字取自 `results.json`。

### 1.1 汇总（pooled）

| n_blocks | D_valid_denominator | exact | verify_failed | decode_failed | undetected | resource_abort | fidelity_mismatch | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|---|---|---|---|
| 64 | 64 | 62 | 2 | 0 | **0** | **0** | 0 | 0.03125 | [0.008612, 0.106975] |

### 1.2 分层表 — `stratum_task`（本任务精细分层：CHAR/HELDOUT 切分口径）

| stratum_task | n_blocks | D | exact | verify_failed | decode_failed | undetected | resource_abort | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|---|---|---|---|
| never_decoded | 28 | 28 | 27 | 1 | 0 | 0 | 0 | 0.035714 | [0.006332, 0.177126] |
| heldout_model_selection | 8 | 8 | 8 | 0 | 0 | 0 | 0 | 0.0 | [0.0, 0.324416] |
| previously_decoded_eval | 28 | 28 | 27 | 1 | 0 | 0 | 0 | 0.035714 | [0.006332, 0.177126] |

### 1.3 分层表 — `stratum_official`（R2 契约口径：A1_CAL / HELDOUT / EVAL）

| stratum_official | n_blocks | D | exact | verify_failed | decode_failed | undetected | resource_abort | p̂ | Wilson 95% CI |
|---|---|---|---|---|---|---|---|---|---|
| A1_CAL_characterization | 16 | 16 | 15 | 1 | 0 | 0 | 0 | 0.0625 | [0.011119, 0.283293] |
| HELDOUT_model_selection | 20 | 20 | 20 | 0 | 0 | 0 | 0 | 0.0 | [0.0, 0.161130] |
| EVAL_already_decoded | 28 | 28 | 27 | 1 | 0 | 0 | 0 | 0.035714 | [0.006332, 0.177126] |

### 1.4 分会话（session）细分

| session | n_blocks | exact | verify_failed | 失败块 id |
|---|---|---|---|---|
| G2 | 32 | 31 | 1 | `part_G2_23.json`（原 G2 EVAL block 5，`first_error_coordinate=978`/`first_error_layer=L2`） |
| G3 | 32 | 31 | 1 | `part_G3_38.json`（`never_decoded`/A1_CAL 块，无历史对照，首次 SCL 观测） |

undetected 与 resource_abort 在以上全部维度（pooled / stratum_task /
stratum_official / session）中均为 **显式 0**（不是省略字段）。

---

## 2. 选择自由度表（已在真实数据上行使过的模型选择步骤）

R2（统计）规则要求：参与过任一模型选择步骤（如 HELDOUT 的 NLL 打分）的块必须
标注并单独分层报告，不得径直排除。逐字取自 `results.json`
`selection_freedom_exercised`：

| stratum_official | 是否行使过选择自由度 | 说明 |
|---|---|---|
| A1_CAL_characterization | 否（M0 拟合，非模型选择） | "M0 (incumbent) prior fit only; not M2/NLL model selection." |
| HELDOUT_model_selection | **是** | "Participated in the NLL model-selection scoring gate (G1R2/G2/G3)." |
| EVAL_already_decoded | 否（在候选已冻结后解码） | "Not itself a model-selection step; decoded under the already-frozen candidate." |

---

## 3. 记账：f 与 H 并排（D-FER-04/05）

`kdb_no_crc = 34119`（两会话相同、按块常数，与解码结果无关）；
`kdb_with_crc = kdb_no_crc + 16(CRC) = 34135`。每块的披露量在解码前无条件
发生（D-FER-05 结构性说明：本协议 leak-then-decode，不需要 Müller eq(11)
式"失败块整帧计入、成功块只计已用部分"的加权）。

| session | H_total (bits) | f_book_no_crc | f_book_with_crc |
|---|---|---|---|
| G2（SHG `_1`） | 0.8168138204133305 | 1.2747448953789544 | 1.2753426830727925 |
| G3（SHG `_2`） | 0.8214782076249098 | 1.2675068411824560 | 1.2681012346130640 |

---

## 4. 保真核对（fidelity）

28/28 EVAL 块的 `fidelity.match=true`，与 per_block_outcomes 逐块一致；
与此前描述性 SCL 结果逐块一致率 28/28（`PRE_RESULT_REVIEW.md` F4）。
`fidelity_compromised=false`（0 mismatches）。

---

## 5. 执行

`reruns=0`；64/64 块 `status=="ok"`；总 wall `4493.36 s`；每块 wall_total_s
范围 `[534.0, 574.4] s`（≤ 1200 s/块预算）；`rss_gib_peak_advisory` 范围
`[0.5205, 0.5767] GiB`（≤ 2 GiB/块预算）。`resource_abort_block_ids=[]`，
`undetected_block_ids=[]`。

---

## 6. 适用域（D-ACQ-05）

结论仅适用于 2026-01-13 两次 SHG `Type2PPLN_3s`（`_1`/`_2`）采集自身的条件
（配置见 `workspace/acq_inventory_20260928/REPORT.md` §(a)/(b)）；不外推到
其他光源/采集配置。HELDOUT 与已解码 EVAL 已分层报告，未合并为单一未分层
数字。

---

## 7. Caveats

(a) 本次只有 SCL 一臂（M2 + SCL(L=16)），**没有同批的二元基线对照**，因此不
    得声称优于二元 Polar 或任何二元基线。
(b) A1_CAL 与 HELDOUT 块是**首次**做 SCL 观测（`part_G3_38.json` 等
    `never_decoded`/`heldout_model_selection` 块此前从未被任何解码器接触过），
    没有历史对照可比。
(c) 本次执行预算（每块 wall ≤ 1200 s、RSS ≤ 2 GiB、总 wall ≤ 3 h、8 路并行、
    超预算 STOP）是 PI 为**本次执行**确认的值（`STATUS.yaml`
    `pi_authorization_2026_09_28`），**不构成**对 D-ACQ-06（40 s/块，SC 口径）
    的一般性重裁。
(d) 64 块样本的 Wilson 95% CI 较宽（pooled 上界 0.107），样本量刚过 D-FER-03
    的 `n=56` 门槛（margin 8 块），不宜读作精确 FER 估计。
(e) 吞吐约 60 符号/s（每块 N=32768 符号、约 550 s/块解码），远不能满足实时
    QKD 后处理速率要求；本次测量不涉及、不作任何吞吐/实时性主张。

---

## 8. 允许的结论句

> 在 M2 先验 + SCL(L=16, top_m=4, CRC-16)、K1=319/K2=6492、P16 冻结构造下，
> SHG `_1`/`_2` 全会话冻结 64 块池（A1_CAL 16 + HELDOUT 20 + EVAL 28，仅限
> 2026-01-13 两次 SHG 采集自身条件）测得 p̂=0.03125（Wilson 95% CI
> [0.008612, 0.106975]），undetected=0，记账 f_book（含 CRC）≈1.268–1.275。

---

## 参考

- 数字来源：`workspace/r2_fer_shg_64/results.json`（`taxonomy_pooled`、
  `taxonomy_by_stratum_task`、`taxonomy_by_stratum_official`、
  `selection_freedom_exercised`、`per_session`、`timing`）。
- 独立审查：`workspace/r2_fer_shg_64/PRE_RESULT_REVIEW.md`（PASS，F1–F9）。
- 授权：`workspace/r2_fer_shg_64/STATUS.yaml`
  `pi_authorization_2026_09_28.verbatim`。
- 主线程裁定：本文件顶部 + `docs/decision-log.md` 2026-09-29 条目 +
  `docs/nbpolar/STATE.md` §4.1。
