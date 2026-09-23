# Tasks: native high-dimensional exploration (docs/plan/review only)

Ownership: main thread owns acceptance; operators report evidence only and never check
their own boxes. **No task authorizes code, execution, Tier-X runs, Tier-Y gates,
freezes, or production-data access.** Role rules per AGENTS.md §4: planner writes no
production code; reviewer edits no files; coder never self-accepts.

## Plan acceptance (this change)

- [x] T1: planner — write the Step-0 survey prereg skeleton (read-only input paths,
  histogram/|Δ|/occupancy/period-crossing definitions, denominators, stop rule).
  Gate: every input path is read-only and non-`.ttbin`; frozen numbers verbatim.
  Needs user authorization: NO (docs only). — ACCEPTED 2026-09-23 (main thread):
  artifact `step0-survey-prereg-skeleton.md`; T2 review gate PASS; R-1 comment
  closed (`remainder_driver.py` listed).
- [x] T2: reviewer-go — independent review of T1 (scope, truth isolation,
  DEVELOPMENT/confirmation boundary, write-root discipline). Output findings only.
  Gate: review PASS else revise-required. Needs user authorization: NO.
  — COMPLETE 2026-09-23: gate PASS (R-1 comment closed in the skeleton; R-2..R-8 PASS).
- [x] T3: planner — write the Step-1 small-q screening design (q ∈ {4,8,16} arms A/B,
  matched conditions, FER–f separation metric, Tier-X prereg template, qualitative
  no-go bar (fixed) + future-freeze numeric-threshold placeholder). No algorithm
  selected here.
  Gate: sim/real firewall + stop-loss-as-design present; no run authorized.
  Needs user authorization: NO. — ACCEPTED 2026-09-23 (main thread): artifact
  `step1-screening-design.md`; T4 review gate PASS; two non-blocking suggestions
  batched to milestone close (proposal §Step 1 numeric-no-go wording; prereg
  template exact-command item).
- [x] T4: reviewer-go — independent review of T3 (Park–Barg/MSD fairness of arm B,
  separation-statistic checkability, post-hoc-tuning guards). Findings only.
  Gate: review PASS else revise-required. Needs user authorization: NO.
  — COMPLETE 2026-09-23: gate PASS (two non-blocking suggestions closed at milestone:
  proposal §Step 1 wording aligned to OQ2; exact-command item added to §6 templates).
- [x] T5: planner — write the Step-2 transfer-prior design (uniform vs informed init,
  fixed M2-transition reference, gain metric, negative-recording rule, EVAL/RESERVE
  boundary guard). No prior-code change.
  Gate: boundary guard explicit; no confirmation-data consumption path.
  Needs user authorization: NO. — ACCEPTED 2026-09-23 (main thread): artifact
  `step2-transfer-prior-design.md`; paired arms + fixed-numerical-reference
  discipline + boundary guard verified; T8 final review still pending.
- [x] T6: planner — write the Step-3 adjudication + GF(32) probe envelope (assumption
  list, ops/memory-vs-budget table skeleton, SCALE/PROBE-ONLY/STOP trifurcation with
  falsifiers, sibling-negative constraints). No implementation.
  Gate: every complexity figure carries its assumption; no code path opened.
  Needs user authorization: NO. — ACCEPTED 2026-09-23 (main thread): artifact
  `step3-complexity-adjudication-and-probe-envelope.md`; OQ3 pre-allowed set
  applied; C4 ~20 s labeled INFERRED with provenance; §7→§6 cross-ref
  corrections applied; T8 final review still pending.
- [x] T7: coder-doc — assemble the exploration index (steps ↔ designs ↔ future
  write-root map, ledger schema L1/L2/L3, §5.7 minimalism checklist, frozen-number
  recheck table). Docs only; no production code.
  Gate: main-thread doc review; zero edits outside this change directory.
  Needs user authorization: NO. — ACCEPTED 2026-09-23 (main-thread doc review):
  artifacts `exploration-index.md` + `stage3-deferral-discriminative-power-note.md`
  (OQ4 one-pager); proposal Impact Scope enumerated; T8 final review still pending.
- [x] T8: reviewer-go — final independent review of proposal/design/tasks consistency
  (frozen-number invariance, no-delta-spec rationale, Tier-X/Tier-Y division,
  stop-loss checkability, role-rule compliance). Findings only.
  Gate: review PASS else revise-required. Needs user authorization: NO.
  — COMPLETE 2026-09-23: gate PASS; all non-blocking comments closed in-file
  (step3 §7→§6 residual, T3 gate phrasing, Step-3 output-path/tier label,
  W_P/W_S label alignment).
- [x] T9: memory — memory triage at close (durable entries only, no speculative
  content). Gate: triage recorded. Needs user authorization: NO.
  — COMPLETE 2026-09-23: one durable entry written to AGENT_PROJECT_MEMORY.md
  (head, 2026-09-23); decision-log entry recommended for the milestone commit.

## Explicitly out of this task list (each needs its own packet + user authorization)

- O1: any Tier-X probe run (Steps 0–2) — needs its own `prereg.md` freeze + pasted
  full authorization text before execution; writes only to
  `workspace/exploration/nbpolar-native-highdim/<id>/`.
- O2: any Tier-Y decision gate or claim-bearing statement — needs independent
  Pre-EXECUTE + Pre-RESULT reviews and main-thread acceptance.
- O3: any decoder implementation, GF(32) graph work, prior/CAL change, freeze edit,
  or new-data test — each needs its own OpenSpec change.
- O4: Stage-3 re-entry — needs a discriminative-power-restoring design under its
  own freeze (see proposal §Stage-3).

## Small-task note

T1–T9 are all docs/review/memory and small enough to implement directly — the
orchestrator may run them without the full implement pipeline. O1–O4 are not small
and are not authorized here at all.

## 待用户裁决的开放问题（2026-09-23）

本节只追加裁决占位，不改上文 T1–T9 与 O1–O4 的内容与勾选，不新增 FER/效率/晋级断言。

- OQ1：Step-1 筛选 ladder 是否锁定 q∈{4,8,16}，还是预允许 q=32。Decision: DECIDED 2026-09-23（用户裁决）——锁定 q∈{4,8,16}，不预允许 q=32（与 design D3 现状一致）。
- OQ2：Step-1 止损用硬性 FER–f 分离阈值（现在定）还是定性 bar 留给未来 freeze。Decision: DECIDED 2026-09-23（用户裁决）——定性 bar 现在定，硬性数值阈值留给未来 freeze（与 design D3 现状一致）。
- OQ3：Step-3 是否确认 GF(32) 为裂维探针，还是预允许其他因式分解。Decision: DECIDED 2026-09-23（用户裁决）——预允许其他因式分解；GF(32) 为基线候选而非唯一锁定族，Step-3 裁决在预允许因式分解集合内比较。T6 与 design.md D5 按此调整。
- OQ4：Stage-3 押后（λ 逐行恒等于 34,119 = 5·(K1+K2)+64 ⇒ cap 比较退化为构造恒等式、判别力为零）是否接受，还是要求附一页纸面判别力说明。Decision: DECIDED 2026-09-23（用户裁决）——接受押后，且要求附一页 paper-only 判别力说明（cap 恒等式推导 + 判别力恢复条件），由 T7 落实。
