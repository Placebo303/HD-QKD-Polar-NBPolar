# Commit-ready 清单 — 2026-09-27 隔夜（**未执行任何 git 动作**）

- 生成阶段：隔夜自动化 P0（`docs/nbpolar/OVERNIGHT_PLAN_20260927.md` §2）。
- **本夜不 `git add` / 不 `commit` / 不 `push` / 不 `stage`**（Git Safety Protocol：仅在用户明确指示时提交）。本清单供明早用户明示后执行。
- 数据来源：`git status --porcelain`（2026-09-27 隔夜第 1 轮 tick）。

---

## 批次 A — C1 探针 OpenSpec change（应当 commit，优先级最高）

路径（整个未跟踪目录）：

```
openspec/changes/nbpolar-l2-c1-k550-probe/
```

建议提交信息：

```
nbpolar: add l2-singlefactor C1 k550 probe change (proposal/design/tasks)

Tier-X synthetic probe packet for the L2 construction single-factor line.
Scope OUT boundaries: no real/protected data, no Tier-Y, no status-string
change, no results/ or comparison_bench/outputs_comparison/ writes,
one-shot only (reruns=0).
```

---

## 批次 B — 隔夜沉淀文档（本阶段新增/修改）

| 路径 | 类型 | 说明 |
|---|---|---|
| `docs/decision-log.md` | M | 追加 2026-09-27 C1 沉淀条目（Decision/Context/Alternatives/Consequences 四段） |
| `docs/nbpolar/DOCUMENT_INDEX.md` | M | 新增 4 行：C1 FOCUSED_REVIEW / C1 STATUS.yaml / OVERNIGHT_PLAN / overnight_state |
| `docs/nbpolar/OVERNIGHT_PLAN_20260927.md` | ?? | 隔夜执行计划（§0–§5） |
| `workspace/overnight_state_20260927.md` | ?? | 隔夜进度表 + heartbeat（**运营文件，可考虑不入库**） |
| `workspace/COMMIT_READY_20260927.md` | ?? | 本清单（**运营文件，可考虑不入库**） |
| `docs/nbpolar/R2_T4_PI_DECISION_CARDS_20260927.md` | ?? | R2 T4 四张 PI 决策卡片（无推荐数值、无倾向性措辞） |
| `workspace/OVERNIGHT_REPORT_20260927.md` | ?? | 隔夜晨报（**运营文件，可考虑不入库**） |
| `openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md` | M | 仅 +1 行指向决策卡片（**PENDING 状态未改、无数值**） |

建议提交信息：

```
docs(nbpolar): record C1 Tier-X probe as DESCRIPTIVE_TIER_X_REVIEWED_WITH_LIMITATIONS

Decision-log entry, document-index rows and the 2026-09-27 overnight plan.
No status string changed; no R2 PENDING value filled; no git action taken
by the overnight automation itself.
```

---

## 批次 B2 — 隔夜 P1–P5 新增（`op-k1-ramp-k550`，**追加到本清单**）

路径：

```
openspec/changes/nbpolar-op-k1-ramp-k550/            (proposal/design/tasks)
workspace/probes/op-k1-ramp-k550/prereg.md
workspace/probes/op-k1-ramp-k550/run.py
workspace/op-k1-ramp-k550-packet/TASK_PACKET.md
workspace/op-k1-ramp-k550-packet/STATUS.yaml
workspace/op-k1-ramp-k550-packet/FREEZE_REVIEW.md
workspace/op-k1-ramp-k550-packet/EXECUTION_TRANSCRIPT.md
workspace/op-k1-ramp-k550-packet/FOCUSED_REVIEW.md
docs/decision-log.md                                  (M, 新增 09-27 两条)
docs/nbpolar/DOCUMENT_INDEX.md                        (M)
```

建议提交信息：

```
nbpolar: op-k1-ramp-k550 Tier-X k1 dose ramp (descriptive, one-shot)

Bounded 5-point k1 grid {10,80,160,320,450} at k2=550, single arm BASE,
d2=worst_k(H2,550) set-identical to C1. Operational exact counts 0/32,
30/32, 32/32, 32/32, 32/32; oracle 160/160; undetected 0.
Bookkeeping-only dose diagnostic: no point is an efficiency operating point.
Tier-X non-claim; no status string changed; no R2 value filled.
```

> **注意**：`workspace/probes/op-k1-ramp-k550/results.json` 与 `.numba_cache/` 属工作树产物（gitignore 范围），**不入库**；durable record = packet 四件套 + decision-log 条目。

---

## 批次 B3 — 隔夜 P1–P5 并发双轨中的 **A 套**（权威记录）+ 细网格探针（**追加到本清单**）

两套（`op-k1ramp-k550-base` = A / `op-k1-ramp-k550` = B）是同一冻结配置的两次独立 one-shot，
A 为权威记录，B 保留为交叉验证（总计数字一致），详见
`workspace/op-k1ramp-k550-packet/DUPLICATE_RUN_NOTE.md`。

路径：

```
openspec/changes/nbpolar-op-k1-ramp-k550/              (proposal/design/tasks — 已被双轨共用，含 K1-T11/T12)
workspace/probes/op-k1ramp-k550-base/prereg.md
workspace/probes/op-k1ramp-k550-base/run.py
workspace/probes/op-k1ramp-k550-base/results.json      (工作树产物，可考虑不入库)
workspace/op-k1ramp-k550-packet/STATUS.yaml
workspace/op-k1ramp-k550-packet/FREEZE_REVIEW.md
workspace/op-k1ramp-k550-packet/EXECUTION_TRANSCRIPT.md
workspace/op-k1ramp-k550-packet/FOCUSED_REVIEW.md
workspace/op-k1ramp-k550-packet/DUPLICATE_RUN_NOTE.md
workspace/probes/op-k1ramp-fine-base/prereg.md
workspace/probes/op-k1ramp-fine-base/run.py
workspace/probes/op-k1ramp-fine-base/results.json      (工作树产物，可考虑不入库)
workspace/op-k1ramp-fine-packet/STATUS.yaml
workspace/op-k1ramp-fine-packet/EXECUTION_TRANSCRIPT.md
workspace/op-k1ramp-fine-packet/FOCUSED_REVIEW.md
docs/nbpolar/DOCUMENT_INDEX.md                          (M，再 +3 行)
```

建议提交信息：

```
nbpolar: op-k1ramp k1 dose ramp + fine interpolation (Tier-X, descriptive)

Coarse grid {10,80,160,320,450} and fine grid {20,40,60} at k2=550 on the
same seeds and the same shared d2. Operational exact per 32 blocks:
0/2/14/24/30/32/32/32 for k1=10..450; oracle 32/32 at every point;
first non-zero in k1 in (10,20], saturation at k1=160.
Bookkeeping-only dose diagnostic: no k1 point is an efficiency operating point.
Tier-X non-claim; no status string changed; no R2 PENDING value filled.
```

---

## 批次 B4 — 追加 2：固定总披露配比探针 `op-k1k2-split-560`（**追加到本清单**）

路径：

```
workspace/probes/op-k1k2-split-560/prereg.md
workspace/probes/op-k1k2-split-560/run.py
workspace/probes/op-k1k2-split-560/results.json      (工作树产物，可考虑不入库)
workspace/op-k1k2-split-packet/STATUS.yaml
workspace/op-k1k2-split-packet/FREEZE_REVIEW.md
workspace/op-k1k2-split-packet/EXECUTION_TRANSCRIPT.md
workspace/op-k1k2-split-packet/FOCUSED_REVIEW.md
openspec/changes/nbpolar-op-k1-ramp-k550/tasks.md    (M，K1-T13/T14)
docs/decision-log.md                                  (M，09-27 第三条)
docs/nbpolar/DOCUMENT_INDEX.md                        (M)
```

建议提交信息：

```
nbpolar: op-k1k2-split-560 allocation probe at fixed 2800-bit disclosure

k1+k2=560 held constant (2800 bits, identical f at every point); d1 and d2
recomputed per point. Operational exact per 32 blocks: 0/14/28/1/0/0/0/0 for
k1=10/40/80/160/240/320/400/480. Single-peaked, non-monotone; both ends
collapse. Allocation effect only - no efficiency claim, no operating point,
no extrapolation to the frozen real-data K1=319/K2=6492.
```

---

## 批次 B5 — 追加 3：固定配比缩放总量探针 `op-kratio-scale`（**追加到本清单**）

路径：

```
workspace/probes/op-kratio-scale/prereg.md
workspace/probes/op-kratio-scale/run.py
workspace/probes/op-kratio-scale/results.json      (工作树产物，可考虑不入库)
workspace/op-kratio-scale-packet/STATUS.yaml
workspace/op-kratio-scale-packet/EXECUTION_TRANSCRIPT.md
workspace/op-kratio-scale-packet/FOCUSED_REVIEW.md
docs/decision-log.md                                 (M，09-27 第四条)
docs/nbpolar/DOCUMENT_INDEX.md                       (M)
```

建议提交信息：

```
nbpolar: op-kratio-scale total-budget probe at fixed 1:6 allocation ratio

Totals 560/448/336/280/224 (disclosed 2800..1120 bits) at k1:k2 = 1:6, a
derived choice from the preceding peak band, not an independently
preregistered ratio. Operational exact 28/0/0/0/0 of 32; oracle 30/0/0/0/0.
Same-ratio scaling only: does NOT establish low-f unreachability, makes no
efficiency claim, and no extrapolation to real-data budgets.
```

---

## 批次 B6 — 追加 4：低总量有界配比搜索 `op-lowtotal-ratio`（**追加到本清单**）

路径（注意：错误记录**保留**，不是要删的垃圾）：

```
workspace/probes/op-lowtotal-ratio/prereg.md
workspace/probes/op-lowtotal-ratio/run.py
workspace/probes/op-lowtotal-ratio/results.json                        (工作树产物，可考虑不入库)
workspace/probes/op-lowtotal-ratio/results.execution_error_attempt1.json (保留的错误记录，可考虑不入库)
workspace/op-lowtotal-packet/STATUS.yaml
workspace/op-lowtotal-packet/EXECUTION_TRANSCRIPT.md
workspace/op-lowtotal-packet/FOCUSED_REVIEW.md
docs/nbpolar/SYNTHESIS_20260927.md
openspec/changes/nbpolar-op-k1-ramp-k550/tasks.md    (M，K1-T17/T18)
docs/decision-log.md                                  (M，09-27 第五条)
docs/nbpolar/DOCUMENT_INDEX.md                       (M)
```

建议提交信息：

```
nbpolar: op-lowtotal-ratio bounded low-total k1-share search

Totals 448 and 336 x four k1 shares each (ratios ~1:13..1:2.5), 8 points,
256 blocks. Operational exact 1/32 at T448_k1_32_k2_416, zero at the other
seven points. Bounded grid: does not establish low-f unreachability. First
launch was an implementation defect (execution_error); its record is kept
and the measurement launch followed.
```

---

## 批次 B7 — 追加 5：峰值带细化 `op-peak-refine`（**追加到本清单**）

路径：

```
workspace/probes/op-peak-refine/prereg.md
workspace/probes/op-peak-refine/run.py
workspace/probes/op-peak-refine/results.json      (工作树产物，可考虑不入库)
workspace/op-peak-refine-packet/STATUS.yaml
workspace/op-peak-refine-packet/EXECUTION_TRANSCRIPT.md
workspace/op-peak-refine-packet/FOCUSED_REVIEW.md
openspec/changes/nbpolar-op-k1-ramp-k550/tasks.md (M，K1-T19/T20)
docs/decision-log.md                               (M，09-27 第六条)
docs/nbpolar/DOCUMENT_INDEX.md                    (M)
docs/nbpolar/SYNTHESIS_20260927.md                (M，峰值平台结论)
```

建议提交信息：

```
nbpolar: op-peak-refine peak-band refinement at fixed total 560

k1 = 60/100/120 (k2 = 500/460/440) at k1+k2=560, 2800 bits and identical f
at every point. Operational exact 24/26/20 of 32; oracle 32/26/20. Brackets
the coarse peak as a plateau over k1 in [60,120], top at k1~80-100.
Bookkeeping-only allocation diagnostic: no efficiency claim, no operating point.
```

---

## 批次 C — 既存欠账（**需明早主线程/PI 决定去留，本夜不代决**）

已修改未提交：

```
AGENT_PROJECT_MEMORY.md
docs/nbpolar/README.md
docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md
docs/nbpolar/STATE.md
openspec/changes/nbpolar-r2-fer-measurement-contract/tasks.md
```

未跟踪的规划草稿（去留由 PI/主线程决定，不自动加入）：

```
docs/nbpolar/ACQUISITION_SPEC_DRAFT_20260922.md
docs/nbpolar/FER_DEFINITION_DRAFT_20260922.md
docs/nbpolar/NEXT_L2_PROBE_DESIGN_20260925.md
docs/nbpolar/R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md
docs/nbpolar/R2_OPEN_INPUTS_DECISION_LIST_20260925.md
```

> **注意**：`docs/nbpolar/STATE.md` 含 `STATE.md:65` route lock 与 M2 状态串。批次 C 提交前必须逐行 diff 确认**未**改动 rung/ladder state、M2 状态串、G2/G3 冻结的 K1=319/K2=6492。

---

## 挂起项（明早需用户一句话）

1. 是否执行批次 A（C1 change）的 commit？
2. 是否执行批次 B？
3. 批次 C 的 5 份规划草稿：入库 / 移出 / 删除？
4. 是否 `archive` `nbpolar-l2-c1-k550-probe`？
5. 是否 `push`（本地领先远程多个 commit）？
