# W3 仓库清理记录（HYGIENE_LOG，2026-09-30）

> 按 `docs/nbpolar/CLOSURE_PACKET_20260930.md` §5（W3）执行。分支：`codex/nbpolar-phase0`。
> 硬性规则遵守情况：未解码、未读 `.ttbin`、未跑任何 `run.py`；未改任何结果目录文件内容；
> 未改 `src/`、`experiments/`、`tools/`；未写 `results/`、`comparison_bench/outputs_comparison/`；
> 未 push、未装包、未删除任何文件；未用 heredoc/管道喂 Python；未动 `openspec/`。

## 1. 原生编译产物加入 .gitignore — 完成

- 做了什么：先读 `.gitignore`（59 行，原文件为 CRLF 行尾），确认 4 条规则均不存在后，
  在末尾追加注释行 + 4 条规则（追加部分保持 CRLF，与原文件一致）：
  - `comparison_bench/src/comparison_bench/formal_ir/nbpolar/_native/*.so`
  - `comparison_bench/src/comparison_bench/formal_ir/nbpolar/_native/*.dll`
  - `comparison_bench/src/comparison_bench/formal_ir/nbpolar/_native/rust_kernels/target/`
  - `src/reconciliation/cpp_polar/ca_scl.so`
- 结果：`git status --short` 中 `?? .../_native/libnbpolar_kernels.so`、
  `?? .../_native/libnbpolar_kernels_rust.so`、`?? .../_native/nbpolar_kernels_win.dll`、
  `?? .../_native/rust_kernels/target/`、`?? src/reconciliation/cpp_polar/ca_scl.so` 五项
  全部消失；`git check-ignore -v` 逐一验证四类路径均命中新规则。编译产物文件本身未删除。
- 附带说明：文件末尾多了一个空行（编辑工具行为），对 gitignore 语义无影响，未手工再改。

## 2. 遗留改动 `workspace/r2_binary_baseline_shg_64/_test_aggregation.py` — 不提交、不还原

- 做了什么：`git diff -- <该文件>` 输出为空；`md5sum` 工作树文件与
  `git show HEAD:<该文件>` 的 blob 完全一致（均为 `26af8e99642c8ed75c4782782ed7df75`）；
  `git status --porcelain=v2` 显示新旧 hash 相同（`85f8af6…`）的 `.M` 标记，
  即仅 stat 脏（index "needs update"），**无任何内容增删**。
- 判定：不符合任务包"只新增测试用例（无删除行）"的前提（新增 0 行、删除 0 行），
  按任务包分支"其他任何情况 → 不提交、不还原"处理：**未运行 pytest，未提交，未还原**，
  结果目录内文件内容未动。
- 提醒（给 W4）：该文件的 stat 脏标记仍在 `git status` 里显示为 `M`，但内容与 HEAD 一致；
  W4 按包内显式文件列表 `git add` 时不要把它当成实质改动加入提交。

## 3. STATE.md 旧吞吐数字 — 完成（只追加，未改原文）

- 做了什么：在 `docs/nbpolar/STATE.md` §0「R2 测量 `r2-fer-shg-64` 主线程裁定（2026-09-29）」
  段落末尾（`> \`workspace/r2_fer_shg_64/RESULT_SUMMARY.md\`。` 之后）追加一行（LF，`> ` 引用前缀）：
  `> （2026-09-30 注：约 60 符号/s 为 scl_joint 参考实现；原生实现见 docs/nbpolar/R3_EFFICIENCY_ACCOUNTING_20260930.md。）`
- 结果：`git diff --stat` 显示 STATE.md 仅 +1 行；原文（"吞吐约 60 符号/s"所在行及全段）一字未动；
  M2 状态串未动。

## 4. 已知与本包无关的先存改动 — 已识别，按要求不碰不提交

- `comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv`（M）——不碰不提交。
- `workspace/pytest-evidence-test/**`（多项 M）——不碰不提交。
- 以上均未 `git add`、未修改、未还原。

## 5. OpenSpec — 未归档任何 change，未改 `openspec/`（按要求无动作）
