# NB-Polar document index

This directory is the canonical planning home for the independent NB-Polar
track in the current worktree. It must not be treated as an extension of the
binary Polar Release checkout.

> Staleness note (2026-09-21): this index stops at P20R — P20S/P20T packets
> and the S8/S9/S10 Tier-X probes are not yet indexed; the current
> never-decoded ledger (101 frames, not 261) lives in the decision-log
> 2026-09-21 arithmetic-corrections entry.

## GPT-6 Astra reasoning pack

`astra6/` contains a compact current-state brief, minimal examples, four
paired reasoning tasks/prompts, and a cross-cutting master prompt. It is
analysis-only and grants no implementation, data-read, decoder-execution,
publication, commit, or push authority. Start with `astra6/README.md`.

| Document | Role | State |
|---|---|---|
| `README.md` | scope, ownership, current status | Phase 0 accepted |
| `STATE.md` | one-page entry point; read first | active |
| `ASSET_MAP.md` | three-checkout asset and reuse map | read-only synthesis |
| `ARCHITECTURE.md` | algorithm and software contracts | Phase 0 frozen |
| `ROADMAP.md` | phased implementation and gates | Phase 0 frozen |
| `CRITICAL_PATH.md` | serial coding order and stop attribution | Phase 0 frozen |
| `VALIDATION_GATES.md` | quantitative checks and early falsification tests | Phase 0 frozen |
| `WORKBUDDY_LIFECYCLE.md` | task, authorization, review and acceptance workflow | active rule |
| `PROBE_TIER.md` | Tier-X probe template and Tier-Y threshold/delta rules | active rule |
| `REAL_DATA_FEASIBILITY_STRATEGY.md` | post-P19 project objective, evidence interpretation, L2-first route and stop rules | active route |
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
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/` | Heavy autonomous CAL-derived P1 metric to SC interface exploration | `EMPIRICAL_PRIOR_SC_INTERFACE_ACCEPTED`; model-sampled interface evidence only |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/` | five-arm same-block HOLD layer/backoff diagnostic | accepted descriptive; 15/15 verify_failed, no FER claim |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20A-RESOURCE-ENDPOINT-INSTRUMENTATION/` | injected-only resource classification and endpoint semantics packet/prompt | frozen awaiting explicit authorization |
| `../../.workbuddy/queue/NBPOLAR-X08-PER-SESSION-PRIOR-ENTROPY-AUDIT/` | Tier-X per-session prior entropy audit packet | probe complete; λ diagnosis confirmed |
| `../../workspace/probes/nbpolar_x08_per_session_prior_entropy_audit/results.json` | X08 probe result (λ prior H1 2.0066 vs raw+floor H1 0.0252; K_total 33285 vs 7020; L1 side info 65754 vs 826 bits) | Tier-X descriptive evidence |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M/` | L1-order 1p5m packet | superseded by P20M with zero consumption |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/` | VAL raw-prior 1p5m packet (Stage A `raw_prior_1p5m.npz` + orders; Stage-B VAL 1660..2043) | accepted descriptive `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE`; 25/25 gates |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/MAIN_THREAD_ACCEPTANCE.md` | bounded main-thread acceptance (G0/G1/G2; undetected 0; counts 0/0, DEV 1/1, HOLD 0/1, attempts 1/1) | accepted descriptive; L2-side single-factor planning next, nothing auto-triggered |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/` | HOLD alt-L2 1p5m packet (Stage A `alt_l2_tables_1p5m.npz` α=1 Laplace L2 table, D2 FEASIBLE; Stage-B HOLD 2213..2724) | accepted descriptive `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE`; 28/28 gates |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/MAIN_THREAD_ACCEPTANCE.md` | bounded main-thread acceptance (A 0/4; B alt-L2 operational 1/4 block-3 exact; C 0/4; D 1/4; undetected 0; HOLD 1/1, attempts 1/1, counts 0/0, 2M pristine) | accepted descriptive; maintain-confirmation planning next, nothing auto-triggered |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/` | 2M VAL maintain-confirmation packet (Stage A `raw_prior_2m.npz` + `raw_prior_orders_2m.json` + `alt_l2_tables_2m.npz` K334/6746/7080; Stage-B VAL 2187..2826) | accepted descriptive `TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE`; A 0/5, B 2/5, C 0/5, D 3/5 |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/MAIN_THREAD_ACCEPTANCE.md` | bounded main-thread acceptance (A 0/5; B alt-L2 operational 2/5 blocks-1,2 exact; C 0/5; D 3/5 blocks-1,2,4 exact; b_restored 2; b_maintained 0; undetected 0; 2M counts 1/1, VAL-DEV 1/1, attempts 1/1; remainder/HOLD/1M/1.5M untouched) | accepted descriptive; next single-factor planning next, nothing auto-triggered |
| `../../.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/` | static synthetic reconciliation, verification and disclosure packet | `STATIC_PROTOCOL_DEVELOPMENT_ACCEPTED`; attempt consumed |
| `../../.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/MAIN_THREAD_ACCEPTANCE.md` | bounded Phase 5 disposition | accepted synthetic development signal only |
| `../../openspec/changes/formal-ir-nbpolar-phase5-static-protocol/` | Phase 5 behavior and scientific gates | implementation and one development attempt complete |
| `../../.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/P5_FREEZE.md` | static protocol freeze Rev 1 (R1/R2 rulings; authorizes nothing) | frozen; independent Pre-EXECUTE PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; R-1 closeout |
| `../../.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/OPERATOR_RETURN.md` | Phase 5 operator return | candidate accepted by main thread within bounded scope |
| `../../.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate/` | 300-block dev-gate evidence root (frozen_plan/per_block_outcomes/transcript_accounting/aggregate_summary/report) | accepted bounded evidence; attempt 1/1 consumed |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/` | fixed nested disclosure, restart SC and paired static comparison | `FIXED_INCREMENTAL_NEGATIVE_ACCEPTED`; attempt consumed |
| `../../openspec/changes/formal-ir-nbpolar-phase6-fixed-incremental/` | Phase 6 fixed-schedule semantics and gates | implementation and one paired development attempt complete; blocked |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/P6_FREEZE.md` | fixed nested-disclosure freeze Rev 1 (authorizes nothing) | frozen; independent Pre-EXECUTE PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS (4 non-blocking findings) |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; N-1..N-4 |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/OPERATOR_RETURN.md` | Phase 6 operator return | negative result accepted; option (a) successor |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate/` | paired 300-block dev-gate evidence root (frozen_plan/per_block_paired_outcomes/transcript_accounting/aggregate_comparison/report) | blocked evidence; attempt 1/1 consumed |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/` | non-final impossible-decode rejection advancement | `DECODE_REJECT_ADVANCE_DEVELOPMENT_ACCEPTED`; attempt 1/1 consumed |
| `../../openspec/changes/formal-ir-nbpolar-phase6-r1-decode-reject-advance/` | Phase 6-R1 scheduler delta | accepted within single-layer synthetic scope; tasks complete |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/R1_FREEZE.md` | R1 freeze Rev 1 (authorizes nothing) | frozen; independent Pre-EXECUTE PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS (non-blocking findings) |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS (non-blocking comments) |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/OPERATOR_RETURN.md` | Phase 6-R1 final operator return | candidate accepted by main thread within bounded scope |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/` | three-arm paired 300-block dev-gate evidence root (frozen_plan/per_block_three_arm_outcomes/transcript_accounting/aggregate_comparison/report) | accepted bounded evidence; attempt 1/1 consumed |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/` | decoder-free two-layer BEC surrogate target-N and f sensitivity | `TWO_LAYER_RATE_FEASIBILITY_ACCEPTED`; no decoder/attempt |
| `../../openspec/changes/formal-ir-nbpolar-phase6-r2-two-layer-rate-feasibility/` | explicit `f<=1.3`, L2 coverage audit and target-N contract | candidate evidence returned; tasks unchecked; no execution |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/two_layer_rate_sensitivity.json` | 66-row two-layer BEC sensitivity result (K, residual, leakage, f) | candidate result artifact; decoder-free |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/R2_REPORT.md` | two-layer rate feasibility report and L2 audit | candidate report; surrogate planning estimate only |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/INDEPENDENT_RESULT_REVIEW.md` | independent decoder-free result recomputation | PASS_WITH_COMMENTS; 66/66 rows zero-difference |
| `../../.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/OPERATOR_RETURN.md` | Phase 6-R2 final operator return | candidate accepted as surrogate planning evidence |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/` | P1 to candidate-conditioned P2 two-stage SC with oracle-L2 comparator | `TWO_LAYER_OPERATIONAL_SC_INTERFACE_ACCEPTED`; attempt 1/1 consumed |
| `../../openspec/changes/formal-ir-nbpolar-phase4-p4-two-layer-operational-sc/` | causal operational-L2 behavior, accounting and bounded paired gate | candidate returned; one development attempt complete; tasks unchecked |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/P4_FREEZE.md` | two-layer operational SC freeze Rev 1 (authorizes nothing) | frozen; independent Pre-EXECUTE PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS (NB-1..NB-7 non-blocking; seed-overlap and layer-independence adjudicated) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; 13/13 gates recomputed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/OPERATOR_RETURN.md` | Phase 4-P4 final operator return | interface accepted; performance interpretation rejected |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/` | paired 96-block two-layer interface gate evidence root (frozen_plan/per_block_two_layer_outcomes/transcript_accounting/aggregate_summary/report) | accepted interface evidence; attempt 1/1 consumed |
| `../../.workbuddy/queue/NBPOLAR-X01-PROBE-TIER-BOOTSTRAP/` | workflow bootstrap plus four-family five-seed probe | workflow complete; X01 closed as reviewed non-claim probe |
| `../../openspec/changes/nbpolar-probe-tier-and-decision-gate-slimming/` | Tier X/Tier Y and delta-successor lifecycle | implemented and active |
| `probes/X02_DEPENDENT_L2_POINT_SEARCH.md` | compact Tier-X dependent-L2 operating-point search | completed non-claim probe; focused review PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/` | powered paired discriminator at X02 strong/45/140 | `HARD_L1_CONDITIONING_PENALTY_ACCEPTED`; attempt consumed |
| `../../openspec/changes/formal-ir-nbpolar-phase4-p5-hard-conditioning-penalty/` | paired hard-L1 conditioning penalty semantics | candidate returned; one development attempt complete; tasks unchecked |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/P5_FREEZE.md` | hard-conditioning penalty freeze Rev 1 (authorizes nothing) | frozen; independent Pre-EXECUTE R1 PASS (R0 docs-only B-1 repaired) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review (R0) | NEEDS_CHANGES; docs-only B-1 (repaired) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/PRE_EXECUTE_REVIEW_R1.md` | independent Pre-EXECUTE re-review (R1) | PASS; B-1 closed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; all numbers/gates/root recomputed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/OPERATOR_RETURN.md` | Phase 4-P5 operator return | accepted within synthetic mechanism scope |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/` | paired 384-pair penalty gate evidence root (frozen_plan/per_block_paired_outcomes/transcript_accounting/aggregate_summary/report) | accepted mechanism evidence; attempt 1/1 consumed |
| `probes/X03_BOB_MARGINAL_L2.md` | hard vs Bob-marginal vs oracle Tier-X probe | frozen; awaiting authorization |
| `probes/X03B_ORACLE_LABEL_CORRECTION.md` | X03 oracle final-label semantic correction | frozen Tier-X delta; awaiting authorization |
| `probes/X04_L1_DISCLOSURE_PARETO.md` | nested K1 disclosure/end-to-end recovery Pareto probe at the dependent-L2 point | frozen Tier-X; awaiting authorization |
| `probes/X04_PROMPT.md` | direct operator prompt for X04 | frozen Tier-X; awaiting authorization |
| `probes/X05_L1_LADDER_REPLAY.md` | decoder-free enumeration of adaptive K1 schedules from X04 scalar records | frozen Tier-X; awaiting authorization |
| `probes/X05_PROMPT.md` | direct operator prompt for X05 | frozen Tier-X; awaiting authorization |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/TASK_PACKET.md` | paired Tier-Y S22 adaptive hard-L1 development gate | BLOCKED pending main-thread disposition; run once |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/AUTHORIZATION_PROMPT.md` | direct authorization text for the P6 implementation and one-shot gate | authorized; attempt 1/1 consumed |
| `../../openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p6/spec.md` | P6 adaptive hard-L1 delta spec inside the Phase 4 change | implemented; tasks unchecked; BLOCKED pending disposition |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/P6_FREEZE.md` | adaptive hard-L1 disclosure freeze (authorizes nothing) | frozen; independent Pre-EXECUTE PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS (six non-blocking findings) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; failing gate diagnosed as gate-check defect (contract-correct value true) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/OPERATOR_RETURN.md` | Phase 4-P6 operator return | BLOCKED; pending main-thread disposition |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/` | paired 640-block adaptive hard-L1 gate evidence root (frozen_plan/per_block_paired_outcomes/transcript_accounting/aggregate_summary/report) | BLOCKED evidence; attempt 1/1 consumed; failure root preserved |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/TASK_PACKET.md` | Δ repair of the multi-stream D2 identity checker plus read-only revalidation of the immutable P6 root | authorized; code fix + read-only revalidation complete; candidate pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/AUTHORIZATION_PROMPT.md` | direct authorization for P6-R1 without decoder, seed or attempt | authorized; attempt-free (0/0) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/revalidation.json` | single machine-readable read-only revalidation result (12 integrity + 4 scientific gates; corrected D2 grouping) | `integrity_all_pass=true`; `result_label=ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`; old root unchanged |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/INDEPENDENT_REVALIDATION_REVIEW.md` | independent revalidation review of the R1 delta and the corrected gates | PASS_WITH_COMMENTS (three non-blocking notes) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/OPERATOR_RETURN_R1.md` | final Δ-successor operator return | candidate returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/MAIN_THREAD_ACCEPTANCE.md` | bounded main-thread acceptance of corrected P6-R1 | accepted synthetic development mechanism |
| `../../.workbuddy/queue/NBPOLAR-X06-EMPIRICAL-CONSTRUCTION-ORDER-PROBE/TASK_PACKET.md` | heavy Tier-X empirical-genie versus BEC construction-order discriminator | frozen; awaiting explicit authorization |
| `../../.workbuddy/queue/NBPOLAR-X06-EMPIRICAL-CONSTRUCTION-ORDER-PROBE/AUTHORIZATION_PROMPT.md` | direct authorization including one artifact-content read | frozen; not yet authorized |
| `../../.workbuddy/queue/NBPOLAR-X07-ENTROPY-CONTRACT-RECONCILIATION/TASK_PACKET.md` | decoder-free reconciliation of V49, raw-count, smoothed-model and X06 sampling entropies | frozen; awaiting explicit authorization |
| `../../.workbuddy/queue/NBPOLAR-X07-ENTROPY-CONTRACT-RECONCILIATION/AUTHORIZATION_PROMPT.md` | direct authorization including one diagnostic artifact-content read | frozen; not yet authorized |
| `../../.workbuddy/queue/NBPOLAR-X07-ENTROPY-CONTRACT-RECONCILIATION/MAIN_THREAD_DISPOSITION.md` | main-thread population/session attribution and route choice | descriptive attribution accepted; Model-F rejected for target construction |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/TASK_PACKET.md` | Tier-Y V25 TRAIN-count empirical construction and paired development gate | candidate returned; one development attempt complete; acceptance pending main thread |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/AUTHORIZATION_PROMPT.md` | direct P7 implementation and one-shot execution authorization | authorized; read 1/1 + attempt 1/1 consumed |
| `../../openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p7/spec.md` | P7 target-population empirical construction delta spec inside the Phase 4 change | candidate returned; tasks unchecked; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/P7_FREEZE.md` | target-population empirical construction freeze Rev 1 (authorizes nothing) | frozen; independent Pre-EXECUTE PASS (review item #1 ratified) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS; raw-MLE entropy-functional semantics ratified; five non-blocking findings |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS; inputs/orders/outcomes/Wilson/accounting/gates recomputed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/OPERATOR_RETURN.md` | Phase 4-P7 final operator return | candidate returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/` | 640-pair target-population development gate evidence root (frozen_plan/construction_orders/per_block_paired_outcomes/aggregate_summary/report) | candidate evidence; read 1/1 + attempt 1/1 consumed; empirical 640/640 exact |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_construction.py` | target-population empirical construction core, gates and frozen gate CLI | candidate implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_target_construction.py` | focused tests for support rule, preconditions, orders, arms, accounting and scope | 11 passed; 228 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/MAIN_THREAD_ACCEPTANCE.md` | bounded acceptance of target-population construction at K45/K140 | accepted; empirical-vs-BEC superiority not claimed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/TASK_PACKET.md` | Tier-Y shared-block rate grid with deterministic selection and disjoint confirmation | candidate returned; one gate attempt complete; acceptance pending main thread |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/AUTHORIZATION_PROMPT.md` | direct P8 implementation and one-shot execution authorization | authorized; read 1/1 + attempt 1/1 consumed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/P8_FREEZE.md` | target-rate SCREEN→CONFIRM freeze Rev 1 (authorizes nothing) | frozen; independent Pre-EXECUTE PASS (seed-coincidence ratified FRESH) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS; SCREEN-seed / P7-test-local-seed coincidence ratified FRESH |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; 35-point SCREEN, selection, CONFIRM, accounting, gates recomputed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/OPERATOR_RETURN.md` | Phase 4-P8 final operator return | candidate returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm/` | 35-config SCREEN + selected-point CONFIRM evidence root (frozen_plan/screen_records/selection_and_confirmation/report/transcript_accounting) | candidate evidence; read 1/1 + attempt 1/1 consumed; selected (8,80), CONFIRM 638/640 |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py` | target-rate SCREEN→CONFIRM core, gates and frozen gate CLI | candidate implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_target_rate.py` | focused tests for grid/identity, Wilson equivalence, selection, isolation, pairing, accounting and scope | 12 passed; 240 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/MAIN_THREAD_ACCEPTANCE.md` | bounded P8 feasibility acceptance with explicit left-boundary-censoring limitation | accepted; not a global minimum-rate claim |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/TASK_PACKET.md` | Tier-Y zero-axis lower-rate SCREEN and disjoint CONFIRM successor | candidate returned; one gate attempt complete; acceptance pending main thread |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/AUTHORIZATION_PROMPT.md` | direct P9 implementation and one-shot execution authorization | authorized; read 1/1 + attempt 1/1 consumed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/MAIN_THREAD_ACCEPTANCE.md` | bounded acceptance of K1=6/K2=70 on the registered zero-axis grid | accepted; synthetic N=256 only |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P10-FWHT-KERNEL-SCALING-PROBE/TASK_PACKET.md` | Tier-X GF(32) FWHT numerical-equivalence and scaling probe | executed descriptively; followed by X11/X12 |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P10-FWHT-KERNEL-SCALING-PROBE/AUTHORIZATION_PROMPT.md` | direct P10 two-file Tier-X authorization | used; no attempt or status claim |
| `../../workspace/probes/nbpolar_x10_fwht_kernel_scaling/` | bare FWHT kernel numerical/timing probe | Tier-X complete; support-tail hazard found |
| `../../workspace/probes/nbpolar_x11_hybrid_fwht_endtoend/` | hybrid FWHT/direct end-to-end probe | Tier-X STOP; exception parity failed after near-tie decision divergence |
| `../../workspace/probes/nbpolar_x12_exact_chunked_sc_scaling/` | bitwise exact row-chunked direct-SC scaling probe | Tier-X complete; N=262144 reached |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/TASK_PACKET.md` | Tier-Y allocation-only exact chunked SC implementation and gate | frozen; single gate executed, candidate pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/AUTHORIZATION_PROMPT.md` | direct P11 implementation and one-shot gate authorization | authorized; attempt 1/1 consumed; 0 artifact reads |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/MAIN_THREAD_ACCEPTANCE.md` | acceptance of default-512 exact SC allocation change | accepted; no decoder-algorithm change |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/TASK_PACKET.md` | Tier-Y target-population f=1.3 six-N development profile | TERMINAL BLOCKED(resource_limits_met_and_no_abort); single run resource-aborted, read/attempt 1/1 spent |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/AUTHORIZATION_PROMPT.md` | direct P12 one-read/one-attempt authorization | used; read/attempt 1/1 spent; no rerun |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/P12_FREEZE.md` | P12 freeze (authorizes nothing) | frozen; single gate executed once, resource-aborted |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | CONFIRMED_SINGLE_RESOURCE_ABORT; null artifacts verified |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/OPERATOR_RETURN.md` | Phase 4-P12 terminal operator return | BLOCKED; verbatim stderr preserved; no rerun; successor needs new authorization |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/MAIN_THREAD_DISPOSITION.md` | main-thread acceptance of terminal resource blocker | accepted BLOCKED; no profile evidence accepted |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/TASK_PACKET.md` | Tier-Y empirical-genie f=1.3 scaling gate at N=4096/8192/16384 | single gate executed, NOT_CONFIRMED pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/AUTHORIZATION_PROMPT.md` | direct P13 one-read/one-attempt authorization | used; read/attempt 1/1 spent; no rerun |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/P13_FREEZE.md` | empirical-genie scaling freeze (authorizes nothing) | frozen; single gate executed once, NOT_CONFIRMED |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/P13_IMPLEMENTATION_NOTES.md` | P13 implementation and test notes | frozen; 20 focused + 305 NB-Polar green |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; all numbers recomputed, non-blocking only |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/OPERATOR_RETURN.md` | Phase 4-P13 final operator return | NOT_CONFIRMED returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/` | empirical-genie scaling gate evidence root (frozen_plan/construction_and_allocations/per_block_genie_residuals/aggregate_summary/report) | NOT_CONFIRMED evidence; read 1/1 + attempt 1/1 consumed; DEV UCBs 0.952/0.486/0.252 all >0.01 |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_scaling.py` | empirical-genie scaling core, gates and frozen gate CLI | NOT_CONFIRMED implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_empirical_genie_scaling.py` | focused tests for genie oracle, orders, K budget, TRAIN/DEV separation, UCB, BEC report-only, accounting and scope | 20 passed; 305 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/TASK_PACKET.md` | Tier-Y N=16384 empirical-genie learning-curve gate (nested B=8/16/32/64/128 from one 128-block TRAIN, one 32-block DEV) | single gate executed, NOT_CONFIRMED pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/P14_FREEZE.md` | empirical-genie learning-curve freeze (authorizes nothing) | frozen; single gate executed once, NOT_CONFIRMED |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/P14_IMPLEMENTATION_NOTES.md` | P14 implementation and test notes | frozen; 15 focused + 320 NB-Polar green |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; all numbers recomputed, non-blocking only |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/OPERATOR_RETURN.md` | Phase 4-P14 final operator return | NOT_CONFIRMED returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/` | empirical-genie learning-curve gate evidence root (frozen_plan/learning_curve_constructions/per_block_genie_residuals/aggregate_summary/report) | NOT_CONFIRMED evidence; read 1/1 + attempt 1/1 consumed; DEV UCBs 0.1725/0.1879/0.1587/0.1391/0.2011 all >0.01 |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_learning_curve.py` | empirical-genie learning-curve core, gates and frozen gate CLI | NOT_CONFIRMED implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_empirical_genie_learning_curve.py` | focused tests for K pin, nested accumulation, 320-call budget, order/K replay, five-way DEV scoring, paired UCB, stream separation, accounting and scope | 15 passed; 320 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/TASK_PACKET.md` | Tier-Y empirical-genie mid-N scaling gate at N=32768/65536 (16 TRAIN + 16 DEV per N, 128 genie calls) | single gate executed, NOT_CONFIRMED pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/P15_FREEZE.md` | empirical-genie mid-N scaling freeze (authorizes nothing) | frozen; single gate executed once, NOT_CONFIRMED |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/P15_IMPLEMENTATION_NOTES.md` | P15 implementation and test notes | frozen; 15 focused + 335 NB-Polar green |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS; all numbers bit-exact, two non-blocking notes |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/OPERATOR_RETURN.md` | Phase 4-P15 final operator return | NOT_CONFIRMED returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate/` | empirical-genie mid-N gate evidence root (frozen_plan/construction_and_allocations/per_block_genie_residuals/aggregate_summary/report) | NOT_CONFIRMED evidence; read 1/1 + attempt 1/1 consumed; DEV UCBs 0.0359/0.0761 both >0.01 |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/empirical_genie_mid_n.py` | empirical-genie mid-N core, gates and frozen gate CLI | NOT_CONFIRMED implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_empirical_genie_mid_n.py` | focused tests for K pins, both-N grouping, stream separation, order/allocation replay, df=15 UCB, checkpoint/accounting and scope | 15 passed; 335 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/TASK_PACKET.md` | Tier-Y N=32768 empirical-construction operational f=1.3 gate (16 TRAIN + 64 DEV, one 64-bit tag per block) | single gate executed, CANDIDATE pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/P16_FREEZE.md` | N=32768 operational freeze (authorizes nothing) | frozen; single gate executed once, CANDIDATE |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/P16_IMPLEMENTATION_NOTES.md` | P16 implementation and test notes | frozen; 23 focused + 358 NB-Polar green |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; 62/64 recount + Wilson recomputed, zero-count margin stated |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/OPERATOR_RETURN.md` | Phase 4-P16 final operator return | CANDIDATE returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/` | N=32768 operational gate evidence root (frozen_plan/construction_and_allocation/per_block_outcomes/aggregate_summary/report) | CANDIDATE evidence; read 1/1 + attempt 1/1 consumed; DEV 62/64 exact, Wilson LB 0.9098711859061207 |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/operational_f13.py` | N=32768 operational core, gates and frozen gate CLI | CANDIDATE implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_operational_f13.py` | focused tests for K pin, buckets/precedence, Wilson 62/61 boundaries, tag/domain, causal wiring, accounting and scope | 23 passed; 358 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/TASK_PACKET.md` | Tier-Y N=32768 operational replication gate (128 fresh DEV blocks, P16 report-only, never pooled) | single gate executed, CANDIDATE pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/P17_FREEZE.md` | N=32768 operational replication freeze (authorizes nothing) | frozen; single gate executed once, CANDIDATE |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/P17_IMPLEMENTATION_NOTES.md` | P17 implementation and test notes | frozen; 25 focused + 383 NB-Polar green |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; 123/128 recount + Wilson recomputed, count margin 2, item-8 resolved |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/OPERATOR_RETURN.md` | Phase 4-P17 final operator return | CANDIDATE returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate/` | N=32768 operational replication gate evidence root (frozen_plan/predecessor_construction_identity/per_block_outcomes/aggregate_summary/report) | CANDIDATE evidence; read 1/1 + attempt 1/1 consumed; DEV 123/128 exact, Wilson LB 0.921934049951655 |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/operational_f13_replication.py` | N=32768 operational replication core, gates and frozen gate CLI | CANDIDATE implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_operational_f13_replication.py` | focused tests for predecessor identity, buckets/precedence, Wilson 121/120 boundaries, tag/domain, non-pooling, accounting and scope | 25 passed; 383 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/TASK_PACKET.md` | Tier-Y N=32768 1M-HOLD operational microcheck (three registered blocks, no FER/recovery threshold) | single gate executed, COMPLETE pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/P18_FREEZE.md` | N=32768 1M-HOLD microcheck freeze (authorizes nothing) | frozen; single gate executed once, COMPLETE |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/P18_IMPLEMENTATION_NOTES.md` | P18 implementation and test notes | frozen; 26 focused + 409 NB-Polar green |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS; R8 invented flags and R9 unreachable branch ratified |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; 17/17 gates recomputed (resumed from an interrupted prior attempt's transcript; suites re-run, gate not rerun) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/OPERATOR_RETURN.md` | Phase 4-P18 final operator return | COMPLETE returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/` | N=32768 1M-HOLD microcheck evidence root (frozen_plan/input_and_construction_identity/per_block_outcomes/aggregate_summary/report) | COMPLETE evidence; reads 1/1 + 1/1 and attempt 1/1 consumed; 17/17 gates true, 0/3 exact descriptive |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_microcheck.py` | thin P18 HOLD microcheck runner (accepted P16/P17 helpers reused, unchanged) | COMPLETE implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_holdout_microcheck.py` | focused tests for identity refusal, HOLD slicing/remainder, one-open guards, no fitting, tag domain, truth isolation, buckets, NLL/disclosure arithmetic, checkpoints and scope | 26 passed; 409 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/TASK_PACKET.md` | Tier-Y N=32768 1M-HOLD five-arm layer/backoff diagnostic (base/+128 L1/+512 L2/both/oracle control, no FER/recovery/winner threshold) | single gate executed, COMPLETE pending main-thread acceptance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/P19_FREEZE.md` | N=32768 1M-HOLD layer/backoff diagnostic freeze (authorizes nothing) | frozen; single gate executed once, COMPLETE; §6 command authoritative |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/P19_IMPLEMENTATION_NOTES.md` | P19 implementation and test notes | frozen; 30 focused; 104 combined P19+P16/P17/P18 suites green |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS WITH COMMENTS; N1–N4 non-blocking (N1 one-char `FROZEN_COMMAND` typo, never executed) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; 20/20 gates recomputed; downgrade solely for external-commit provenance anomaly (item A) — worktree files authoritative, never `git show HEAD:` |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/OPERATOR_RETURN.md` | Phase 4-P19 final operator return (incl. external-commit anomaly adjudication and bounded scope) | COMPLETE returned; accepted descriptively by main thread |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/MAIN_THREAD_ACCEPTANCE.md` | bounded P19 disposition and next gate | accepted descriptive; closed to tuning |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/` | N=32768 1M-HOLD layer/backoff diagnostic evidence root (frozen_plan/input_and_predecessor_identity/per_block_arm_outcomes/aggregate_summary/report) | COMPLETE evidence; reads 1/1 + 1/1 and attempt 1/1 consumed; 20/20 gates true, 15/15 `verify_failed` descriptive; worktree files authoritative vs the external mid-run commit |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/holdout_backoff_diagnostic.py` | thin P19 five-arm layer/backoff diagnostic runner (accepted P16/P17/P18/P7/P11 helpers reused, unchanged) | COMPLETE implementation; accepted modules untouched |
| `../../comparison_bench/tests/test_nbpolar_holdout_backoff_diagnostic.py` | focused tests for identity refusal before reads, P18 slicing/remainder, one-open guards, no fitting, five-arm semantics and +128/+512 arithmetic, tag-domain separation, oracle isolation, buckets/recount tampers, paired recovery tables and no-threshold COMPLETE, checkpoints/budgets and scope | 30 passed; independently re-run green by Pre-RESULT |

| `../../.workbuddy/queue/NBPOLAR-PHASE4-X13-METRIC-MEMORY-LIFETIME-PROBE/TASK_PACKET.md` | Tier-X injected two-layer metric ownership/lifetime probe | frozen; awaiting explicit authorization |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-X13-METRIC-MEMORY-LIFETIME-PROBE/AUTHORIZATION_PROMPT.md` | direct X13 two-file probe authorization | not yet authorized; no attempt |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/P11_FREEZE.md` | exact chunked SC freeze (authorizes nothing) | frozen; independent Pre-EXECUTE PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS (partial-evidence fallback ratified) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS; all numbers recomputed from the four artifacts |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/OPERATOR_RETURN.md` | Phase 4-P11 final operator return | candidate returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/` | exact chunked SC gate evidence root (frozen_plan/equivalence_records/scaling_record/report) | candidate evidence; attempt 1/1 consumed; 33+16+18 parity, N65536 exact, N262144 ok 66.09 s / 710.5 MB |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py` | allocation-only `_minus_block` chunking delta (keyword-only `chunk_rows=512`, `None` golden) | candidate implementation; `sc_decode` signature unchanged |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc_chunked_gate.py` | thin injected-data gate runner (no production default) | candidate implementation; required flags + absent-root refusal |
| `../../comparison_bench/tests/test_nbpolar_sc_chunked.py` | focused tests for chunking parity, boundaries, support, full-SC, refusals and scope | 10 passed; 262 full NB-Polar total |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/P9_FREEZE.md` | lower-rate boundary-resolution freeze Rev 1 (authorizes nothing) | frozen; independent Pre-EXECUTE PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS; 56-point SCREEN, selection, CONFIRM, accounting, gates recomputed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/OPERATOR_RETURN.md` | Phase 4-P9 final operator return | candidate returned; main-thread acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/` | 56-config SCREEN + selected-point CONFIRM evidence root (frozen_plan/screen_records/selection_and_confirmation/report/transcript_accounting) | candidate evidence; read 1/1 + attempt 1/1 consumed; selected (6,70), CONFIRM 624/640 |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py` | target-rate SCREEN→CONFIRM core incl. P9 gate-id delta, gates and frozen gate CLI | candidate implementation; accepted P7/P8 evidence roots untouched |
| `../../comparison_bench/tests/test_nbpolar_target_rate.py` | focused tests for grid/identity, Wilson equivalence, selection, isolation, pairing, accounting and scope incl. P9 56-point/zero-K/domain-separation additions | 24 passed (P9 focused); 252 full NB-Polar total |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1_revalidate.py` | read-only revalidation helper over the immutable P6 five files (pure stdlib, no decoder/RNG/tag) | candidate implementation; zero forbidden calls |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py` | adaptive hard-L1 core, integrity/scientific gates and frozen gate CLI | candidate implementation; D2-once gate keyed on the compound multi-stream identity |
| `../../comparison_bench/tests/test_nbpolar_adaptive_l1.py` | focused tests for nested sets, restart/no-state, tag/feedback, accounting and scope | 16 passed; multi-stream compound-identity regression added |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/penalty_gate.py` | dependent-L2 paired penalty statistic/runner wrapper | candidate implementation; injected synthetic tables only |
| `../../comparison_bench/tests/test_nbpolar_penalty_gate.py` | focused tests for dependent table, guard, classifier, exact bound and scope | 9 passed |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer.py` | two-stage operational SC core module and frozen gate CLI | candidate implementation; injected synthetic tables only |
| `../../comparison_bench/tests/test_nbpolar_two_layer.py` | focused tests for causal wiring, taxonomy, accounting and scope | 12 passed |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer_rate.py` | decoder-free two-layer BEC recurrence and minimum-K analysis module | candidate implementation; no decoder/RNG |
| `../../comparison_bench/tests/test_nbpolar_two_layer_rate.py` | focused tests for recurrence, calibration, arithmetic and scope | 10 passed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/P3_STAGEB_FREEZE.md` | Stage B freeze v2/Rev 2a (frozen contract; authorizes nothing) | F-1 repaired docs-only → R1 PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/PRE_EXECUTE_REVIEW.md` | independent Pre-EXECUTE review (R0) | NEEDS_CHANGES F-1 (repaired docs-only) |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/PRE_EXECUTE_REVIEW_R1.md` | independent Pre-EXECUTE re-review (R1) | PASS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/PRE_RESULT_REVIEW.md` | independent Pre-RESULT review | PASS_WITH_COMMENTS |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/OPERATOR_RETURN.md` | Stage A/B operator return (candidate) | candidate returned; acceptance pending |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/` | Stage B evidence root (frozen_plan/oracle_records/stress_and_profile/diagnostic_summary/report) | candidate evidence; attempt 1/1 consumed |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/` | order-position 1p5m packet (new-B L2 order under frozen α1, single VAL-remainder block 2044..2171; `MAIN_THREAD_ACCEPTANCE.md`; never-used ledger corrected per next-branch decision §2(ii): 1.5M VAL 2172..2212 (41/10,496), 1.5M HOLD 2725..2766 (42/10,752), 2M VAL 2827..2915 (89/22,784), 2M HOLD 3556..3644 (89/22,784); pre-consumption 261 frames / 66,816 pairs — post-P20S (−128) / post-P20T (−32) never-decoded remainder 101 frames (41+42+18); 69 after a 32-frame CAL (<1 block)) | accepted descriptive negative `TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`; 34/34 gates; DEV 1/1, counts 0/0, attempts 1/1; §16 planning next, nothing auto-triggered |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/` | HOLD alt-L2 2M IR-confirmation packet (Stage-B HOLD DEV 2916..3555 CONSUMED; accepted IR-1..IR-5 payload tables are the pre-registered H2 inputs) | accepted descriptive `TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`; A 0/5, B 4/5, C 0/5, D 4/5; b_maintained 0, b_restored 4 descriptive; no H2 verdict in-packet |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/` | merged-block mechanism probe 2M packet (single full-block A/B/O geometry; uncapped IR-5 series) | accepted descriptive via R1 `TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`; 36/36 gates after the R1 one-expression fix |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/` | P20S-R1 delta-successor gate-expression fix (DELTA.md; identical freeze, one predicate corrected) | accepted descriptive; ONE authorized execution (exit 0, 15/15 files, recount mismatch 0); no other delta |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE/` | RN-2 pre-execution Tier-Y freeze for the N=8192 persistence probe | superseded by the `-2M-TAIL` packet (SUPERSEDED.md); kept for provenance |
| `../../.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/` | P20T N=8192 persistence probe packet (single 2M HOLD-tail block 3595..3626, CONSUMED; K_total/K1/K2 1760/84/1676) | accepted descriptive `TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE_ACCEPTED_DESCRIPTIVE`; 31/31 gates; A/B/O all `verify_failed` (O identical to A, diagnostic only); Q-G1/Q-G2 asked, neither decided |
| `../../.workbuddy/queue/NBPOLAR-H2-ADJUDICATION-ANALYSIS/` | H2 v2 descriptive re-adjudication on 59 rows (`H2V2_RECHECK.md`; P20R read-only context, not joined) | `H2V2_RECHECK: PASS_WITH_FINDINGS`; H2a REFUTED, H2b/c SUPPORTED, H2d SUPPORTED-flat, H2e REFUTED-geometry-incoherent (truncated + full-block n=1); no FER/efficiency/leakage/key-rate/reliability conclusion |
| `../../.workbuddy/queue/NBPOLAR-X14-SCL-LIST-SURVIVAL/` | Tier-X SCL list-survival synthetic probe (near-random channel; Q1 structural, Q2 void) | Tier-X complete; focused review PASS_WITH_FINDINGS |
| `../../.workbuddy/queue/NBPOLAR-X15-STRUCTURED-CHANNEL-LIST-SURVIVAL/` | Tier-X structured-channel list-survival successor proposal | Tier-X proposal; `APPROVED_PENDING_FREEZE` (freeze only; execution not authorized) |
| `../../.workbuddy/queue/NBPOLAR-X16-SYNTHETIC-SCALE-DISCLOSURE/` | Tier-X synthetic scale/disclosure operating-point proposal (frozen N=32768) | Tier-X PROPOSAL; execution requires main-thread approval; d=0.75 point later shown non-informative |
| `../../.workbuddy/queue/NBPOLAR-X17-METRIC-FEED-AUDIT/` | Tier-X metric-feed audit (H-a U/X truth confusion localized to probe bodies; positive control decodes; corrected full-scale still at chance) | Tier-X complete; `COMPLETE_REVIEWED_PASS_WITH_FINDINGS`; synthetic line closed as non-informative |
| `../../openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-reduced-n-persistence/` | RN reduced-N delta spec — N=8192 persistence probe on the 2M HOLD tail (proposal + freeze-design input) | scoping only (`SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`); parent `.workbuddy/queue/NBPOLAR-REDUCED-N-FEASIBILITY.md`; superseded skeleton `../../.workbuddy/queue/NBPOLAR-REDUCED-N-PERSISTENCE/` kept for provenance |
| `../../openspec/changes/scl-synthetic-list-gate/` | SCL track change proposal (synthetic list-gate; proposal.md + design.md + tasks.md) | scoping only; SCL stays locked |
| `../../.workbuddy/queue/NBPOLAR-SCL-SYNTHETIC-GATE/` | SCL scoping skeleton (`STATUS.yaml` / `SCOPING_NOTES.md`) | `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`; zero implementation/execution/decoder counters; 20260925 seed band reserved, not activated |
| `../../comparison_bench/src/comparison_bench/formal_ir/nbpolar/scl.py` | G2 SCL module with frozen `scl_decode`/`SCLResult` interface (L=1 equivalence to `sc_decode` the hardest T1 test) | G2 landed `dba4f42f`; 16 T0/T1 focused tests pass (`../../comparison_bench/tests/test_nbpolar_scl.py`); NO synthetic execution ran or is authorized — SCL stays locked |
| `../../workspace/probes/scl-synthetic-working-point/` | G3 Tier-X frozen working-point probe (N=16384, K1=167/K2=3373, d=0.90; list arm N=256 unfrozen top-L stub) | `SCLW_STOP_SANITY_HIGH` — greedy pooled mismatch 0.770302 above ceiling 0.769312, no disclosure bite; wiring-only list arm; SCL stays locked; worktree-only record |
| `../../workspace/probes/q1-geometry-revival/` | Q1 Tier-X geometry revival (persisted-evidence read-only; width-weighted prefix-mass, set-delta, IR-4) | `Q1_DESCRIPTIVE_ONLY`; focused review PASS; worktree-only record |
| `../../workspace/probes/q2-table-vs-input/` | Q2 Tier-X table-vs-input replication (hazard sha, masks/order digests, set-delta, recount) | `MEMORY17_UPGRADE_MULTI_ROOT_REPLICATED` (A≡O / B-differs byte-exact); focused review PASS; worktree-only record |
| `../../workspace/probes/q3-disclosure-efficiency-face/` | Q3 Tier-X disclosure-efficiency face (92 records / 26 within-packet pairs; restored 0/0/0/0/1/2/4) | `Q3_DESCRIPTIVE_ONLY`; cross-packet pooling forbidden; focused review PASS; worktree-only record |
| `../../workspace/probes/q4-status-distribution-audit/` | Q4 Tier-X status distribution audit (165 records / 18 aggregates; 46 located `undetected` all zero) | `Q4_DESCRIPTIVE_ONLY` + `Q4_UNDETECTED_ALL_ZERO` + `Q4_STATUS_COHERENCE_NO_ANOMALY_READINGS` (A8 evaluable 150/165 only); focused review PASS; worktree-only record |
| `../../../HD-QKD_Polar_Comparison/openspec/changes/archive/2026-09-11-formal-ir-future-nbpolar-app-transfer-superseded/` | superseded hybrid APP-transfer draft, retained for provenance | archived |
| `../../.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/` | M2-prior real-data validation parent packet (19 TO-FREEZE keys all null; G1/G2/G3 unauthorized; SHG `_2` reserved for G3) | Stage 1 §4 (a)–(e) complete via child acceptance; G1 freeze preparation next, gated on independent freeze review + explicit user authorization |
| `../../.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/` | M2-prior Stage 1 implementation packet (strict M2 ±1 adapter beside `formal_ir/nbpolar/` + M0 switch + synthetic re-split + CAL note + Spec-5 runner interface; `prior_m2.py` + `test_nbpolar_prior_m2.py` + `scripts/m2_prior_validation.py` + `docs/SECURITY_MODEL.md` +39) | `NBPOLAR_M2_PRIOR_STAGE1_IMPLEMENTATION_COMPLETE_ACCEPTED`; S1-1..S1-8 PASS, focused review PASS_WITH_COMMENTS, 21/21 tests; M2 stays CANDIDATE; implements parent `NBPOLAR-M2-PRIOR-REALDATA-VALIDATION` §4 (a)–(e) |
| `../../.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/REVIEW.md` | independent Stage-1 focused review (checks A–H re-run/recomputed) | PASS_WITH_COMMENTS; zero blocking issues; two cosmetic carried items |
| `../../.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/MAIN_THREAD_ACCEPTANCE.md` | bounded Stage-1 acceptance (label `NBPOLAR_M2_PRIOR_STAGE1_IMPLEMENTATION_COMPLETE_ACCEPTED`) | accepted; M2 CANDIDATE, S9 synthetic-only, no K decision, no freeze values, G1/G2/G3 unauthorized |
| `../../.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/` | G1 real-data NLL packet (SHG `_1` decoder-free; CHAR 200,192 pairs; CAL32 post-skip frames 1024–1055 sacrificed; HELDOUT 1838–2397; frozen-session remainder check) | `NBPOLAR_M2_PRIOR_G1_COMPLETE_ADJUDICATED_BOUNDED_NEGATIVE`; δ-tail FAIL, NLL PASS; M2 stays CANDIDATE |
| `../../.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/G1_ADJUDICATION.md` | bounded-negative adjudication (basis, both gate verdicts, remainder check, not-established scope, diagnostics, route consequence) | adjudicated 2026-09-21; T5 complete; T6/T7 blocked; G3 void unless new candidate |
| `../../.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/FREEZE_REVIEW.md` | independent G1 freeze review (T5 gate) | PASS after one revise-required cycle (arithmetic B1/B2 fixed, no design change) |
| `../../.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/g1_freeze_config.json` | 19-key TO-FREEZE closure config (nulls filled at closure) | frozen; verified |
| `../../workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/{g1.json,cal_ids.json,run_log.md,delta_profiles.json,g1_closure_reproduction.json,cal_ids_closure.json,run_log_closure.md}` | G1 Phase-B + Phase-A closure evidence root (decoder-free; reproduction bit-exact vs closure ledger) | descriptive evidence; no rerun/tuning |
| `../../workspace/m2_prior_validation/remainder_101f/{g1.json,cal_ids.json,run_log.md,remainder_driver.py}` | frozen-session remainder check (NLL/H only, no gate; pooled Δ 1.957900) | descriptive; matched-CAL M0 pathology replicates |
| `../../.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/TASK_PACKET.md` | S11 Tier-X tail-nature probe task packet (incl. main-thread scoped correction: anchor = post-skip frames 1056–1837, the frozen SEG_RANGES/G1 CHAR segment) | probe complete; descriptive/non-claim |
| `../../.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/PROMPT.md` | direct operator prompt for S11 | probe complete |
| `../../.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/STATUS.yaml` | operator all-complete return (S11-P..S11-R PASS; one run, 19.5 s / 1.24 GiB, no rerun) | probe complete |
| `../../.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/S11_ADJUDICATION.md` | S11 adjudication (`NBPOLAR_S11_SHG_TAIL_NATURE_COMPLETE_DESCRIPTIVE`; w=500 tail = pairing contamination; far-offset baseline structured; no route selected) | adjudicated 2026-09-21; independent `S11_NUMERICS_PASS` |
| `../../workspace/probes/nbpolar_s11_shg_tail_nature/` | S11 probe root (`prereg.md` / `body.py` / `results.json`) | Tier-X complete; gitignored worktree-only; durable record = adjudication + decision-log entry |

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
