# NB-Polar document index

This directory is the canonical planning home for the independent NB-Polar
track in the current worktree. It must not be treated as an extension of the
binary Polar Release checkout.

| Document | Role | State |
|---|---|---|
| `README.md` | scope, ownership, current status | Phase 0 accepted |
| `ASSET_MAP.md` | three-checkout asset and reuse map | read-only synthesis |
| `ARCHITECTURE.md` | algorithm and software contracts | Phase 0 frozen |
| `ROADMAP.md` | phased implementation and gates | Phase 0 frozen |
| `CRITICAL_PATH.md` | serial coding order and stop attribution | Phase 0 frozen |
| `VALIDATION_GATES.md` | quantitative checks and early falsification tests | Phase 0 frozen |
| `WORKBUDDY_LIFECYCLE.md` | task, authorization, review and acceptance workflow | active rule |
| `../research_cycles/NBPOLAR-PHASE0/REVIEW_ENTRYPOINT.md` | review index | frozen |
| `../research_cycles/NBPOLAR-PHASE0/FREEZE_REVIEW_VERDICT.md` | durable Phase 0 verdict | FREEZE_ACCEPT |
| `../research_cycles/NBPOLAR-PHASE0/EXECUTION_PACKET.md` | original Phase 0-2 boundary packet | superseded by scoped WorkBuddy packets |
| `../research_cycles/NBPOLAR-PHASE0/PHASE0_PROMPT.md` | original matching prompt | retained for provenance |
| `../../openspec/changes/formal-ir-nbpolar-mvp/` | source-of-truth change proposal | Phase 0 accepted; later phases gated |
| `../../.workbuddy/queue/NBPOLAR-PHASE1-GF32-TRANSFORM/` | Phase 1 implementation packet and prompt | implementation accepted |
| `../../.workbuddy/queue/NBPOLAR-PHASE2-SC-ORACLE/` | autonomous SC/oracle implementation packet and prompt | implementation accepted |
| `../../.workbuddy/queue/NBPOLAR-PHASE3-SYNTHETIC-CONSTRUCTION/` | synthetic generator/construction packet and diagnostic EVAL | BLOCKED; diagnostic retained |
| `../../.workbuddy/queue/NBPOLAR-PHASE3-R1-CONSTRUCTION-RECOVERY/` | construction/gate recovery and fresh EVAL | EVAL_ACCEPTED_DIAGNOSTIC |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P0-PRIOR-CONTRACT-FREEZE/` | Model-F prior-contract freeze packet | FREEZE_ACCEPT |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/` | pure prior adapter and synthetic oracle | IMPLEMENTATION_ACCEPTED_SYNTHETIC_ONLY; 66/66 + 11/11 |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P2-CAL-DEV/` | accepted CAL artifact to prior-table validation | heavy packet prepared, all-false |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P2-R1-DIAGNOSTIC-INDEX-RECOVERY/` | Bob-axis recovery and bounded CAL prior-table validation | accepted; attempts consumed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/` | Heavy autonomous CAL-derived P1 metric to SC interface exploration | prepared, not authorized |
| `../../../HD-QKD_Polar_Comparison/openspec/changes/archive/2026-09-11-formal-ir-future-nbpolar-app-transfer-superseded/` | superseded hybrid APP-transfer draft, retained for provenance | archived |

The archived draft is not an implementation dependency. It proposed a
NB-Polar upper layer feeding the old NB-LDPC lower layer; the current track
uses a native q-ary Polar stack with independent prior, construction, and
decoder gates.

The three source projects remain separate:

- Comparison owns NB-LDPC history, Model-F statistics, shared benchmark
  semantics, and the research decision log.
- This worktree owns the new NB-Polar design and, after acceptance, its
  implementation in `comparison_bench/`.
- Release owns the frozen binary Polar line. It is a read-only baseline and
  protocol reference for this track.

No result document is created until a decoder-free or decoder execution has
actually occurred and passed its applicable review. Planning text must not be
read as execution authorization.
