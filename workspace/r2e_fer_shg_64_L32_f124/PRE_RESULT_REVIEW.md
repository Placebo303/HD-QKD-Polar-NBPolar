# Pre-RESULT 审查记录 — r2e-fer-shg-64-L32-f124（2026-09-29）

独立 reviewer（只读：未改任何文件、未重跑解码、未读 .ttbin、无 git 写；从 64 个 part 文件 / `results.json` / `run.log` / 前驱与 R2D 产物重算）总裁决：**PASS**，无阻塞项。

R1 判定规则 PASS（D=64，exact 61 / verify_failed 3 / decode_failed 0，p̂=3/64，Wilson 95% [0.016069,0.128999] 独立重算一致；undetected 全块 false；fidelity 28/28 EVAL 块五字段逐一比对 0 mismatch；64 块逐块 0 差异）；R2 f_book 分解 PASS（G2 1.245976/1.246574、G3 1.238902/1.239496，与 kdb 33349/33365 一致）；R3 undetected 隔离 PASS；R4 四套分层逐块重算一致 PASS（official：A1_CAL 16/0、HELDOUT 20/0、EVAL 25/3；task：never_decoded 28/0、heldout_model_selection 8/0、previously_decoded_eval 25/3；selection：clean-G3 30/2 Wilson [0.017310,0.201475]、selection_touched-G2 31/1 Wilson [0.005538,0.157446]；汇总 61/3 同表；clean 层仅描述标注存在）；R5 失败块表 PASS（失败集 {gbi23, gbi53, gbi59} 与交叉表核实：R2D G2 31/32 唯一失败 gbi23 L2错84 与本轮一致；G3 在 R2D 无对应记 n/a，如实）；R6 描述性对照不超范围 PASS；R7 披露记账与 K 区分 PASS（SC 保真路径 K1=319/K2=6492，SCL 路径 k1=253/k2=6404）；R8 耗时/资源 PASS（总 wall 3761.5 s ≤ 7200 s，单块最大 57.16 s，RSS 最大 1.3929 GiB，not_started/resource_abort 0）；R9 写入范围 PASS（只写包目录，无晋级断言）。

额外核实：gbi23 计入全部分母（`known_hard_block` 在分母中）；clean 层"仅描述、主判定为 64 块汇总"标注存在；§10 程序性偏差声明如实（`run.log` 缺 EXIT 行，以 DONE + 64 parts + `results.json` mtime 22:25:41 + 零 Traceback 实质替代，充分，未手工补写）；无手工补写痕迹。

措辞意见 C1–C5（可选，不触发重审）：略。

Open 问题（不阻塞裁定）：OQ1 —— 某简报行数 401 vs 实测 145（不影响任何数字）；OQ2 —— 执行窗口外先存 dirty（早于执行窗口，已排除在本次提交路径之外）。
