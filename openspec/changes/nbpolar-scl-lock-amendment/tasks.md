# Tasks: SCL Lock Amendment

Status: **APPROVED by PI 2026-09-27 (T1 DECIDED)**. T1's ruling is recorded
below verbatim (values); T2 (implementation) is authorized to start now; T3
(Tier-X execution) is authorized conditional on T2's tests passing and
main-thread confirmation. Real-data SCL use stays locked (D5, unchanged).

~~Status: **draft — PENDING PI adjudication; grants no authorization; SCL
remains locked until PI approves.**~~ (superseded 2026-09-27; see
`docs/decision-log.md` 2026-09-27 "PI 裁决三项" entry)

- [x] T1 — **DECIDED by PI 2026-09-27** (verbatim record:
  `docs/decision-log.md` 2026-09-27 "PI 裁决三项：SCL 锁修订 T1 = DECIDED..."
  entry). PI reviewed `proposal.md` + `design.md` and ruled:
  - **(i)** Accept: replace lock items (a)/(b) with the synthetic scoreboard
    gate — for the **synthetic Tier-X scope only**.
  - **(ii)** D2 **option (iii)**: run the synthetic gate in parallel with a
    one-shot, read-only M2 real-data layer-failure attribution ("Analysis B"
    — reads existing G2/G3 per-block records only; no decode; no raw-data
    read).
  - **(iii)** CRC length = **16 bits**, counted toward `f_book` exactly once.
  - **(iv)** L ∈ **{4, 8, 16}** (accepted as proposed; not re-derived via the
    `scl-synthetic-list-gate` design §(b) survival-curve procedure).
  - **(v)** Outcome bands accepted **as proposed in D4**: L=16 operational
    ≥15/16 at f≈1.20, oracle-consistent (no operational-exceeds-oracle
    anomaly) ⇒ unlock-for-real-data-candidate; L=16 operational ≤12/16 ⇒
    list-decoding insufficient, pivot to L2 construction/N; in between ⇒ one
    bounded follow-up at the same point/ladder, no tuning.
  - **Working point** (as ruled): channel `G1R2-matched@q1024`, explicit
    `1e-15` floor, N=32768, f_book≈1.20, k1 share 4.69%
    (`T6421_k1_301_k2_6120`), 16 blocks.
  - **M=4 implementation constraint** (main-thread addition, binding for T2):
    joint list decoding = L1 SCL of width L; take the top **M=4** L1
    candidates ranked by joint metric (`log P(u1|y) + log P(u2|u1,y)`);
    expand each into its own width-L L2 SCL; merge all resulting candidates
    and rank by the same joint metric; return the first candidate that
    passes CRC-16. Implementation lives in a new module — `scl.py`'s
    existing single-layer `L=1` contract stays byte-for-byte reproducible
    and its regression test is mandatory.
  - Real-data SCL use **stays locked** (design D5, unchanged by this
    ruling).
  **[T1 CLOSED — T2 now AUTHORIZED to start; T3 conditionally authorized,
  see below]**

- [x] T2 — **DONE 2026-09-27.** Implement CRC + joint two-layer list scoring in a new code path
  alongside frozen `scl.py` (new module or additive extension per the PI's
  T1 ruling on interface placement; `scl.py`'s existing `L=1`/single-field
  contract stays byte-for-byte reproducible). Focused tests required before
  any execution:
  - `L=1` identity: new decoder at `L=1` bit-identical to `sc_decode` /
    existing `scl_decode` `L=1` output (regression, satisfies lock item e).
  - Small-N enumerator oracle agreement: brute-force joint L1+L2 path
    enumeration matches the new decoder's top candidate on a tiny synthetic
    case.
  - CRC disclosure accounting: CRC bits counted toward `f_book` exactly once,
    consistent with the C10-style disclosure convention cited in
    `nbpolar-r2-fer-measurement-contract`.
  **[AUTHORIZED — T1 DECIDED 2026-09-27; implement now]**
  **[DONE 2026-09-27]** New module `comparison_bench/src/comparison_bench/formal_ir/nbpolar/scl_joint.py`
  + `comparison_bench/tests/test_nbpolar_scl_joint.py`; `test_nbpolar_scl.py`
  gained one relative-tolerance assertion fix at the `L1` identity check
  (float64 summation-order 1-ULP gap between `scl.py`'s `+=` accumulation
  and the reference's vectorized `np.sum`; see
  `workspace/probes/scl-joint-timing/CODE_REVIEW.md`). 22 passed, 0 failed.

- [x] T3 — **DONE 2026-09-27.** Tier-X probe: three-line prereg (`prereg.md`) + one frozen-command
  run + one `results.json` at the D4 working point (channel `G1R2-matched@q1024`,
  N=32768, f_book≈1.20, k1 share 4.69%) across L ∈ {4,8,16}; probe-root-only
  writes (`workspace/probes/<id>/`); focused numerical review (commands,
  completeness, arithmetic, truth isolation, write scope) per AGENTS.md §10.4
  Tier-X rules — no Pre-EXECUTE/Pre-RESULT. **[CONDITIONALLY AUTHORIZED by
  the T1 2026-09-27 ruling — execute once T2's focused tests pass and the
  main thread confirms; the T1 ruling is itself the PI's Tier-X execution
  authorization, no further authorization request needed]**
  **T1 addendum (PI 2026-09-27, after G2/G3 layer attribution
  `workspace/analysis/g2g3-layer-attribution/REPORT.md`)**: real-data B-arm
  failures are 8/9 L2-only (L1 exact), while the synthetic D4 point fails in
  L1. T3 therefore measures a **second working point** on the same channel:
  f_book≈1.20, k1 share 9% (`T6421_k1_578_k2_5843`; SC op 0/16, oracle
  0/16 ⇒ L2-dominated), same L ladder, same outcome bands applied per point.
  The D4 point (share 4.69%) is unchanged.
  **[DONE 2026-09-27]** Independent focused review
  `workspace/scl-gate-t3-packet/FOCUSED_REVIEW.md` = PASS_WITH_COMMENTS. Full
  result and adjudication recorded verbatim in `docs/decision-log.md`
  2026-09-27 "SCL 合成门 T3 执行结果与主线程裁决" entry: A point
  (`T6421_k1_301_k2_6120`, share 4.69%) L16 operational 16/16, oracle-consistent
  ⇒ `unlock-for-real-data-candidate` (L1-dominated case); B point
  (`T6421_k1_578_k2_5843`, share 9%) L16 operational 7/16 ⇒
  `list-decoding-insufficient` (L2-dominated case).

- [x] T4 — **DONE 2026-09-27.** Record the T3 outcome against the T1-decided D4 bands in
  `docs/decision-log.md` (append-only) and, if the PI rules it in scope,
  a `docs/nbpolar/STATE.md` §0 sync line. This does not change the SCL lock
  string by itself — only T1's ruling can do that. **[NOT AUTHORIZED by this
  change; requires the PI's own decision-log/STATE update decision]**
  **[DONE 2026-09-27]** Recorded in `docs/decision-log.md` 2026-09-27 "SCL
  合成门 T3 执行结果与主线程裁决" entry (see T3 above) and in
  `docs/nbpolar/STATE.md` §0. Per that entry's adjudication, T5 below is
  deferred rather than auto-prepared.

- [ ] T5 — **暂缓（见 decision-log 2026-09-27 "SCL 合成门 T3 执行结果与主线程裁决"）。**
  A 点 unlock 仅覆盖 L1 主导情形，真实数据 G2/G3 失败模式 8/9 为纯 L2（B 类），
  两者不匹配，故不自动准备真实数据 Tier-Y 骨架。If T3/T4 land in the "unlock-for-real-data-candidate" band: prepare
  (do not execute) a real-data Tier-Y packet skeleton (`TASK_PACKET.md`,
  `PROMPT.md`, `STATUS.yaml`, `AUTHORIZATION_PROMPT.md` with
  `authorizations: []`) per AGENTS.md §10.1/§10.4. This task produces no
  verbatim authorization text and starts no real-data touch.
  **[NOT AUTHORIZED — skeleton only, empty authorization list by
  construction]**
  2026-09-28 真实数据描述性重解（非 Tier-Y、非门）结果见 decision-log；T5 骨架仍暂缓。
  2026-09-28 28 块描述性合并结果见 decision-log；T5 骨架仍暂缓，改由 R2 合同草案候选配置承接（待 PI 裁决）。

## Standing rule

Every box above stays unchecked and every task stays gated until the PI
records the T1 ruling. This file grants no execution, no code merge, and no
lock removal by itself.
