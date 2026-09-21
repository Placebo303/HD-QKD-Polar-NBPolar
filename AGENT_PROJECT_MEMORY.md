## 2026-09-21 Decoder-plateau root cause: nonparametric empirical prior mishandles sparse rare cells (PENDING real-data validation; numbers in S5–S9 probe roots)

- Root cause [repo-observed, Tier-X descriptive]: the incumbent nonparametric prior (raw-count MLE columns + 1e-15 probability floor) prices TRAIN-unseen rare events at the 1e-15 floor, costing 40.4214 bits of spurious penalty per floored true −1 delta (only 30.3509 of 44.7185 true −1 deltas per block fall in TRAIN-zero-−1 columns) — that is the LEADING-CANDIDATE mechanism for the q-ary SC plateau; code rate, disclosure amount, construction, K allocation and temporal correlation are NOT excluded (the 54.8σ surplus is an ideal-model ML/uniform-input result that excludes SC suboptimality, prior mismatch and temporal correlation — it is not a refutation of rate). Chain (pointers only): S2/S4 frozen K2 carries 54.8σ surplus with predicted FER≈0 (`docs/decision-log.md` `:5169`); S5/S6/S7 floor sweep is monotonic with no knee and the `surprisal > median+20 bits` spike statistic is arithmetically forced to zero for any prior with LLR floor→max span < 20 bits, so held-out NLL is the only independent evidence there (macro plan §8; `workspace/probes/nbpolar_s5_prior_floor_screen/`, `nbpolar_s6_floor_lift_prior/`, `nbpolar_s7_intermediate_floor/`); S8 2-parameter pooled ±1 prior beats the incumbent table on held-out NLL on both sessions (`workspace/probes/nbpolar_s8_parametric_prior/results.json` P2); S9 synthetic 16-block decode at frozen K1/K2 319/6492: ±1 prior + frozen construction 11/16 exact vs table + frozen construction 0/16, `undetected` 0 in every arm (`workspace/probes/nbpolar_s9_decoder_prior_relevance/results.json`). Mechanism: ~70% of table columns see zero −1 events in TRAIN. The frozen Release baseline never had this problem: its decoder receives only a parametric per-bit-plane BSC scalar; the only q×q conditional there is a MAP-sanity diagnostic never loaded by a decoder.
- Strategic consequence [decision]: adopting the ±1 prior drops the CAL requirement from 1024 frames to single-digit frames (S8 P3/P4: incumbent needs full 262144-symbol CAL for 1% H accuracy; parametric shows S8 grid descriptive minima of ~2–8 frames — a CANDIDATE BUDGET with no statistical guarantee — and ~20 bits as a parameter-count diagnostic, not an accounting cost, vs ~44k), which would address the prior-estimation accounting gap (`docs/SECURITY_MODEL.md` has no CAL/prior/calibration term at all — verified 2026-09-21) and the CAL shortfall. It does NOT dissolve Type0 tier insufficiency (block completeness and data-quality constraints remain: Type0-500K has ≤146 frames, minus a 32-frame CAL leaves <1 block) and it does NOT dissolve data scarcity — the frozen-session never-decoded remainder is 101 frames (not 261; P20S consumed 128, P20T consumed 32), leaving 69 frames after a 32-frame CAL, i.e. the real-data ladder is EXHAUSTED per P20T's own acceptance. Validation must therefore run on the SHG acquisitions with a declared reserved segment for independent confirmation. Explicitly **PENDING real-data validation**: S9 is synthetic-only, 16 blocks, ground truth pro-±1 by design (S8's own P5 caveat — NLL ≠ decoder performance — is what S9 was built to close, synthetically).
- A3/Gray scope addendum [decision]: A3 rate bounds are not licensed for this project — Corollary 3 derives from a sufficient condition and the two-layer 5+5-bit architecture is outside the theorem's scope (`:5169`–`:5181` caveats). Under Gray the GF(32) neighbor-of-zero set equals the powers of α produced by polar generator rows ⇒ a STRUCTURAL concern for MFD here, opposite to the intuitive recommendation; comparative decoder performance and a full MFD verdict remain UNVERIFIED (the neighbor-set observation alone does not establish either).

## 2026-09-21 Ten-acquisition intake: TimeTagger WSL unblocked + pairing/H/spike traps (detail in decision-log + macro plan)

- TimeTagger [repo-observed]: `.ttbin` reading is unblocked on WSL without the vendor — PyPI `Swabian-TimeTagger` (official owner `swabian`), Linux wheel needs glibc ≥ 2.28 + numpy ≥ 1.23; user venv `/home/karel_303/.venvs/timetagger` holds 2.22.6. `FileReader` is a pure offline parser (no hardware/dongle). Import-namespace trap + `.1`-segment double-count trap live in `docs/troubleshooting.md` — read those before touching any new `.ttbin` intake.
- Semantic traps [decision; pointers only, numbers stay in-session]: (a) two pairing generations — wide same-superframe (W, accidental-dominated) vs narrow nearest-unique (N) — never pick a "best" window from the grid and never share (W) H with clean-coincidence columns (`docs/decision-log.md` `:5200`, `:5216`); (b) two H quantities — factorized H1+H2 (decoder input, raw-count MLE + 1e-15 floor) vs flat full-joint H_full (~7–8 bits at 0.25 counts/cell) — never one comparison column (`:5216`); (c) `surprisal > median + 20 bits` spike count is uninformative for any rule with LLR floor→max span < 20 bits (zero count forced by arithmetic); held-out NLL is the only independent evidence there (`MACRO_PLAN_20260921.md` §8); (d) alignment offset is correlation-derived per acquisition, never inherited; frozen σ gate `[50,150]` + `gate_ps=200` are a matched pair for the 01-21 sources, so out-of-range σ on new sources is contract incompatibility, not a widening target (`:5185`).
- Intake gate [decision]: 10-acquisition intake (~333 MiB, 2026-01-12/13/20/21) inventoried in `docs/nbpolar/RAW_DATA_INVENTORY_20260921.md`, census `:5200`/`:5216`; the three `20260121_Type2_*` acquisitions are likely the already-analyzed V25 sources — treat as NOT new data until the PI confirms. Census skip-702 stays `INHERITED_NOT_DERIVED` (never derive-per-acquisition).
- A3/Gray [repo-observed arithmetic; decision]: A3 MFD premise needs unit-weight neighbor-of-zero (Gray mean 1.0, natural mean 1.9375); under Gray the neighbor set is `{1,2,4,8,16}` = powers of α produced by polar generator rows, so Gray buys no MFD for this construction. Corollary 3's rate bound derives from sufficient `L < d_Hmin`, not the iff. Representation switch still gated on S3+S5+S6 jointly pointing (`:5169`–`:5181`, macro plan §5); route-B C-P2 B4 stays NOT AUTHORIZED and the K-split misallocation is a finding, not an experiment (same refs + macro plan §§2,6).

## 2026-09-20 Milestone batch: G2 SCL landed + Q1/Q2 Tier-X queue (SCL still locked; queue capped)

- SCL track [decision]: track scoped + frozen working-point axis (N=16384, K1=167/K2=3373 first-natural, d=0.90) + G1 review PASS across commits `75055934`/`8eaaa74d`/`f2dab81d` (docs-only); G2 landed as `dba4f42f` (`scl.py` + 16 T0/T1 tests pass, `sc.py` untouched) — SCL stays LOCKED: synthetic working-point execution is still a gated future step, nothing authorized here.
- Queue route [decision]: prereg re-analysis queue adopted (Tier-X, zero data consumption); Q1+Q2 first batch done; Q6 RETIRED (ceiling locked + narrative trend-misread risk); queue cap 6; reaching the cap FORCES the exhaustion-route decision (operating-point redesign / acquisition / closeout).
- Q1/Q2 [decision, descriptive only]: Q1 `Q1_DESCRIPTIVE_ONLY` (within-N geometry tokens: width-weighted totals N32768 A/O 18070 vs B 18053, N8192 4480 vs 4479; set-delta N32768 n=1599 Δ0 ∩5147, N8192 n=963 Δ0 ∩713; IR-4 top-16 N32768 0/0, N8192 A/O 4 vs B 3) + Q2 `MEMORY17_UPGRADE_MULTI_ROOT_REPLICATED` (hazard sha identical A/B/O, masks/order A≡O≠B, Δ0, recount 0 on both roots); focused reviews both PASS_WITH_FINDINGS (non-blocking, worktree-only records); no FER/reliability/efficiency/trend claim.
- Records [repo-observed]: Q1/Q2 preregs, bodies, results and review records stay worktree-only (`workspace/probes/*` gitignored by design); durable record = `docs/decision-log.md` 2026-09-20 milestone batch entry + this entry; `dba4f42f` is the only code-bearing artifact of this batch.
- Next gates [decision]: queue at 4/6 — Q3/Q4 done (descriptive tokens only: Q3 `Q3_DESCRIPTIVE_ONLY` 92 records/26 pairs, restored 0/0/0/0/1/2/4 within-packet; Q4 `Q4_DESCRIPTIVE_ONLY`/`Q4_UNDETECTED_ALL_ZERO`/`Q4_STATUS_COHERENCE_NO_ANOMALY_READINGS` 165 records/18 aggregates, A1–A8 zero but A8 evaluable 150/165); remaining = Q5 (TRAIN counts structure — only meaningful if an L2 redesign is chosen) + the user-owned exhaustion-route decision (operating-point redesign / acquisition / closeout), FORCED at the cap, PENDING user decision; SCL stays locked (G2 landed, G3 `SCLW_STOP_SANITY_HIGH` STOP).

## 2026-09-20 Project-level read-only review (reviewer-go ses_f422a844…, read-only, no decision)

- Direction [repo-observed]: broadly on-document-route. SCL scoping (`scl-synthetic-list-gate`, commits `75055934`/`8eaaa74d`, docs-only, zero protected opens) is compliant synthetic-only prep, not deviation — P20Q B/D 4/5 does not satisfy the `REAL_DATA_FEASIBILITY_STRATEGY.md` SCL 5-item conjunction; N=8192 probe does not break frozen-K/comparability (ADDED-7 non-transfer) but is a routing extension beyond the original serial sequence — its characterization (stage-1 restart vs pure mechanism observation) PENDING main-thread one-liner, not decided here.
- Data end-state [repo-observed; route choice PENDING main thread]: 0 full N=32768 blocks; ladder ends by population exhaustion, not verdict; stage-1 to P20Q descriptive, stage-2 unstarted; operating-point redesign / acquisition / closeout note DEFERRED with no plan.
- Gate-doc lag [repo-observed; fix PENDING main thread]: `CURRENT_TASK.md` head/body tense mismatch; this file's 2026-09-20 RN scoping entry is stale post-P20T (left frozen below, not rewritten); `docs/nbpolar/DOCUMENT_INDEX.md` stops at P20R (P20Q+ generation missing); `README.md` status still 2026-09-11 PLAN_CANDIDATE; RN real path is `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-reduced-n-persistence/` (shorthand `specs/…` does not exist).
- Guards to restate [repo-observed; pending]: 1/4→2/5→4/5 narrative trend-misread risk (guardrails in place); synthetic SCL closure = at-this-operating-point non-informative, not "SCL useless"; IR-5 `.bin` second exception (P20T 9 files vs P20Q 2.25 MB) — standing-rule exception standard needs restatement; Windows dual-source recurrence (`comparison_bench/tests/test_evidence_package.py:27` hard-coded `D:/` + `pytest.ini` `--basetemp D:/…`) — WSL reruns regrow the stray `D:/` tree (2.3 GB precedent).
- Hygiene [repo-observed]: root v68..v72p2 history-line files = path/range debt; openspec archive backlog large; git status small (DrvFs stat-only benign known); λ residual (`prior_artifact.py` `LAMBDA_STAR=137.3823795883264` etc.) known raw+floor-canonical, not a new bug.

## 2026-09-20 NB-Polar Phase 4 P20T N=8192 persistence probe accepted (descriptive; ladder exhausted)

- Factor [repo-observed]: packet `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/` accepted descriptive (`MAIN_THREAD_ACCEPTANCE.md`, independent Pre-EXECUTE PASS + Pre-RESULT PASS on disk; Stage-A 23/23 green; branch `codex/nbpolar-phase0`), label `TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE_ACCEPTED_DESCRIPTIVE`. Single N=8192 block on the 2M HOLD tail 3595..3626 (CONSUMED, one draw, K 1760/84/1676, tag master 2026092400; construction `d77466ec…` / orders `66aefe…` / spike `355a32d3…` reviewer-recomputed; formula `F_MEDIAN8_CARRIED_20260920_H_MINUS_LOCAL_MEDIAN_W8_R8_REFROZEN_8192`). A/B/O all `verify_failed`, L2 first errors (A @193 X-disclosed/U-undisclosed 0.509b vs 0.873b, IR-2 0.4001; B @3 undisclosed under both flags 0.438b vs 0.888b, IR-2 0.0500; O identical to A, diagnostic); floor hits A 12 vs B 1084; set-delta byte-exact (∩713, ±963, Δ0); IR-4 top-16 in-prefix A=4/B=3/O=4 with byte-identical coords; IR-3 A 403/403 vs B 419/417; 31/31 gates; recount 26172/245949 mismatch 0; `undetected` 0. Q-G1 elements + Q-G2 contrast recorded, neither decided (n=1, no baseline at this N).
- Chain [decision, descriptive only]: FIVE single-factor efforts now — P20N/P20O/P20Q construction-side (N=32768, B 1/4→2/5→4/5 descriptive), P20R order-side (1.5M, 0/1 block-dominated negative), P20T reduced-N persistence (N=8192, within-N only, non-transferable). No cross-N inference; the 1/4→2/5→4/5 chain, H2 verdicts, 32768 IR-5 geometry and leakage literals stay at N=32768.
- H2 input [observation]: NONE from this packet (explicit scope) — the within-N geometry joins nothing.
- Process [procedure]: new-N derivation from worktree prior with zero counts opens worked (all digests reviewer-recomputed); `wall_s`/`resources.*` telemetry stays freeze-excluded from byte-equality rules (P20S-R1 lesson, re-observed).
- Scope [decision]: descriptive only — no FER/reliability/efficiency claim, no branch selection, no recheck-transcript persistence. Ledger: DEV 3595..3626 CONSUMED; HOLD remainder 3627..3644 (18 frames) + 1.5M VAL stub 2172..2212 (41) + 1.5M HOLD 2725..2766 (42) stay never-decoded; nothing formable remains — ladder ends by population exhaustion, not by verdict. Operating-point redesign, acquisition, and closeout note DEFERRED to main-thread planning.

## 2026-09-20 Reduced-N (N=8192) persistence probe scoping (unexecuted; next gate RN-1 freeze review)

- Scoping [decision]: OpenSpec delta `specs/nbpolar-reduced-n-persistence/` (spec + design + proposal) + umbrella tasks RN-1..RN-8 (all `[GATE — NOT AUTHORIZED]`) committed and pushed; scoping only — zero protected opens, zero attempts, DEV 0/1, no data contact, no execution.
- Next gate [procedure]: RN-1 freeze review by the main thread (population 32/18, arm rule, K estimate-only rule, comparability boundary, gate markers); Stage-A/Stage-B authorizations + independent Pre-EXECUTE/Pre-RESULT + acceptance all future and separate.
- Ledger end-state [repo-observed]: 0 full N=32768 blocks remain (133 frames / 34,048 pairs never-decoded); authorizing N=8192 would consume 3595..3626 leaving 3627..3644 — until then the full 50-frame 2M HOLD tail stays never-decoded.

## 2026-09-20 Geometry mining: §3 trigger met (Q-G1/Q-G2); reduced-N held pending gates

- Order-independence [repo-observed]: hazard sha `ef4398d3…` identical across A/B/O at manifest level; A≡O masks; B differs; |A−B|=|B−A|=1599 = 23.70% swapped, size-delta 0 ⇒ on this single block, the orders changed only which 6746 positions were disclosed. In-code hazard also depends on Bob/truth/conditioning inputs, so this does NOT prove table-only determination.
- Top-16 tail undisclosed [repo-observed]: IR-4 top-16 in-prefix 0/48 on ALL arms (hazards 9.0768–9.2784 bits ≈ 10.4–10.6× prefix mean); disclosed prefix covers the low-hazard fifth (IR-1 6746/26022) ⇒ 100% of the top-16 tail undisclosed under both orders. Single B fail (L2 @ coord 0, 0.513 bits, IR-2 0.43222, out-of-prefix both flags, floor 0.3717) = 3rd operational out-of-prefix fail archive-wide, 1st on spike-local order; existence case only, n=1 (P20R-B descriptive parallel only, never pooled).
- §3 trigger [decision]: YES — Q-G1 (spike-local fail-pattern recurrence at N=8192, within-N paired) + Q-G2 (spike-local vs frozen tail-mass disclosure at same N). Run root `workspace/geometry/58503bc3-0306-45b0-b70c-2599aaf82820/` committed.
- Ledger end-state [repo-observed]: 0 full N=32768 blocks remain (133 frames / 34,048 pairs never-decoded); N=8192 would use 3595..3626 with remainder 3627..3644. (iv) = one N=8192 persistence probe, scoping-only (OpenSpec delta + freeze, NO execution/NO tail contact); needs Stage-A/Stage-B authorizations + independent reviews.

## 2026-09-20 H2 v2 accepted (full-block geometry join; synthetic SCL line closed)

- Verdicts [repo-observed]: H2 v2 descriptive re-adjudication on 59 rows (56 archive + 3 P20S/R1 full-block), independent recheck `H2V2_RECHECK: PASS_WITH_FINDINGS` (reviewer-go session `ses_f44aa4832ffeidyigKTYTP3ucx`; record `.workbuddy/queue/NBPOLAR-H2-ADJUDICATION-ANALYSIS/H2V2_RECHECK.md`; run root `workspace/h2/497eecf4-d060-42a2-a862-49e8059590b7/`). H2a REFUTED (evaluable 8→9, new gap −0.00277 non-anomalous); H2b SUPPORTED (n 37→38, new r_fail 0.5853, median 2.2835→2.2651); H2c SUPPORTED (35/38 = 0.921; new datum = 3rd out-of-X L2 fail archive-wide, coord 0, both domain flags out); H2d SUPPORTED-flat (new d=0, mean 0.002128); H2e-truncated REFUTED-geometry-incoherent (unchanged) + H2e-full-block-n1 REFUTED-geometry-incoherent (IR-4 0/48 vs IR-2 0.4322, conjunction not met, n=1 caveat). Descriptive only — no FER/efficiency/leakage/key-rate/reliability/deployment claim; oracles diagnostic-only; scopes never pooled.
- Synthetic line closeout [decision]: SCL probe chain X14→X17 closed as non-informative at this operating point (positive control P=0.000 rules out feed defect; corrected full-scale C ≈ chance ⇒ sub-threshold, not wiring). No further synthetic survival re-asks here; any SCL work needs an operating-point change (new top-level OpenSpec change) and separate authorization.
- Ledger end-state [repo-observed]: 0 full N=32768 blocks remain (133 frames / 34,048 pairs never-decoded).
- Scope ruling [procedure]: IR-5 `.bin` bytes are protected — manifest/sha-level evidence only, never opened (hazard sha identical across A/B/O ⇒ hazard values order-independent under frozen α1; A≡O masks; B differs).

## 2026-09-19 NB-Polar Phase 4 P20R order-position 1.5M accepted (descriptive NEGATIVE, 0/1 single block)

- Factor [repo-observed]: packet `.workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/` accepted descriptive (`MAIN_THREAD_ACCEPTANCE.md`, Pre-EXECUTE PASS session `ses_f45c56468ffe7FaiatcEtO4oN6`, Pre-RESULT PASS session `ses_f45ba5f5effeyrswF6FwH2Yq1Q` on disk; Stage-A 21/21 green), label `TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`. Single-factor new-B L2-order position (derive-once, digest `c7853286…e751` reviewer-recomputed exact; D2 FEASIBLE 3928.304784481981 pre-DEV) on the single 1.5M VAL-remainder block 2044..2171 (N=32768, K1/K2 331/6689, tag master 2026092340). A 0/1, B 0/1, C 0/1, D 0/1, all `verify_failed`; `b_maintained`/`b_restored` 0 (A→B {0,0,0,1}); `d_restored` 0 (C→D {0,0,0,1}); `undetected` 0; 34/34 gates; SC 6/6, tags 4/4, sampling 0, genie 0+0; wall 44.37 s / RSS ~521 MiB. Set-delta byte-exact (K2 6689; intersection 1213; |A−B|=|B−A|=5476; size-delta 0). First errors all L2: A/C coord 133 in-X U-out; B/D coord 0 out-of-X. Caps A/B 35164 Δ0, C/D 33509 Δ0; key 137346 / public 1310972 / recount 0. IR-2 A 0.99966 vs B 0.32919; IR-4 top-16 in-prefix 4/16; IR-5 truncated.
- Chain [decision, descriptive only]: four single factors now tested descriptively — P20N/P20O/P20Q construction-side (B 1/4→2/5→4/5) + P20R order-side 0/1 negative (even the true-L1 oracle pair failed on this block). §16 next-branch candidates (L2-side bounded search at fixed point / second single construction form / further order refinement) eligible for planning selection; NO selection made.
- H2 input [observation, no verdict]: IR-2 rank shift joins the archive for main-thread H2 analysis.
- Process [procedure]: derive-once + pin digest + reviewer recompute worked (Stage-A 21/21 green, zero protected opens).
- Scope [decision]: descriptive negative only — no FER/reliability/efficiency reading, no branch selection. 2044..2171 CONSUMED. Never-used ledger (corrected per `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md` §2(ii)): 1.5M VAL 2172..2212 (41 frames / 10,496 pairs), 1.5M HOLD 2725..2766 (42 / 10,752), 2M VAL 2827..2915 (89 / 22,784), 2M HOLD 3556..3644 (89 / 22,784) — pre-consumption total 261 frames / 66,816 pairs; P20S consumed 128 and P20T consumed 32, leaving a never-decoded remainder of 101 frames (41+42+18); after a 32-frame CAL only 69 frames remain (<1 128-frame block) and the ladder is exhausted per P20T's acceptance; under the current same-split rule = 0 full N=32768 blocks; the two 2M segments combine to 178 frames = 1 block + 50-frame stub; 1.5M remainder (83 frames) is low-information (oracle 1/8) and treated as unusable per the decision record §3. No push.

## 2026-09-19 NB-Polar Phase 4 P20Q HOLD IR confirmation on 2M accepted (descriptive complete; strongest restoration signal, still no reliability claim)

- Factor [repo-observed]: packet `.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/` accepted descriptive (`MAIN_THREAD_ACCEPTANCE.md`, `PRE_EXECUTE_REVIEW.md`, `OPERATOR_RETURN.md` on disk; Pre-RESULT PASS session `ses_f463b6cdaffeISG0o1eh7nP79u` recorded in `STATUS.yaml`; acceptance commit `d5c0afb`, branch `codex/nbpolar-phase0`). Reuse-only α1 confirmation on FIRST use of 2M HOLD DEV 2916..3555 (5 blocks; K1/K2 334/6746; tag master 2026092330), label `TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`. A 0/5, **B 4/5 (`b_restored` 4, `b_maintained` 0 vacuous)**, C 0/5, **D 4/5 (`d_restored` 4 diagnostic)**; A→B `{0,0,4,1}`; C→D `{0,0,4,1}`; `undetected` 0; integrity 30/30; key 692580 / public 6554860 / recount 0; SC 30; tags 20; wall 198.39 s / RSS ~620 MiB. IR-1..IR-5 PRESENT on all 20 records + nine scalars complete (0 missing cells).
- Chain [decision, descriptive only]: P20N B 1/4 → P20O B 2/5 → P20Q B 4/5, all descriptive, no reliability claim. 12 L2-fails all natural-in-prefix (X-domain) but U-domain-out — third-segment continuity of the P20N/P20O pattern. Strict-sense maintain absent everywhere (A never exact); A-fail→B-exact restoration 4/5 is the strongest yet at zero disclosure delta by design.
- Evidence-size [repo-observed]: one-packet exception — `per_block_arm_outcomes.jsonl` 2.25 MB committed as frozen evidence (acceptance commit message records the exception). No standing size rule adopted; the pre-freeze-evidence-size-rule proposal is DEFERRED (needs a main-thread decision, not inferable from one exception).
- Process [procedure]: OpenSpec P20Q delta (spec.md + tasks.md P20Q section) was planner-written pre-freeze and already merged in `ce84622` — Stage-A operator correctly staged nothing new; future operators verify via `git status` rather than assuming new delta files.
- Scope [decision]: descriptive confirmation only — no H2 verdict in-packet (accepted IR-1..IR-5 tables + nine scalars are pre-registered inputs for main-thread H2a–H2e analysis AFTER acceptance), no FER/recovery/qualification/promotion claim. 2M HOLD DEV 2916..3555 CONSUMED regardless of outcome; remainders 2M HOLD 3556..3644 + 1.5M VAL 2044..2212 stay never-decoded. Next: main-thread H2 analysis, then the efficiency/disclosure-minimality vs next-upstream-factor branch decision; nothing auto-triggers.

## 2026-09-19 X10 H2 scalar adjudication probe (reviewed PASS) + repo tidy + `D:` stray-dir incident

- X10 probe [repo-observed]: packet `.workbuddy/queue/NBPOLAR-X10-H2-SCALAR-ADJUDICATION/` (TASK_PACKET + AUTHORIZATION_PROMPT); Tier-X artifacts `workspace/probes/nbpolar_x10_h2_scalar_adjudication/{prereg.md,body.py,results.json}`; zero protected opens; decoder-free. H2a REFUTED (4/4 evaluable blocks: exact arm's prefix-hazard mean HIGHER than failing arm's — P20N b3 +0.0971; P20O b1 +0.0304, b2 +0.0431, b4 +0.0684 bits); H2b SUPPORTED (fail-site hazard / prefix-mean median ratio 2.246, n=25 L2 fails; per-arm medians >1.1); H2c SUPPORTED (23/25 in X-prefix; P20O 11/11 additionally out-of-U); H2d flat (mean |Δfloor| 0.0030); H2e static geometry NOT-DECIDABLE → IR-1..IR-5 (bounded, size-capped, recording-only): IR-1 64-bin log hazard histograms {prefix,outside} ~1KB/rec; IR-2 first-error hazard-rank percentile (1 float); IR-3 above-threshold prefix counts at 1.0×/2.0× record prefix-mean; IR-4 top-16 hazardous positions w/ ranks; IR-5 capped 4096×2 float32 series + truncation flag.
- Reading [decision, descriptive only]: failures driven by LOCAL relative hazard spikes, not average metric quality; α=1 smoothing flattens spikes while raising the mean — explains "alt CE/hazard higher yet restores blocks". No FER/reliability claim. H2 one instrumented run from resolution.
- Next [decision]: packet `NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M` frozen (reuse-only α1 confirmation on 2M HOLD 2916..3555, 5 blocks, IR-1..IR-5 PRESENT, zero new counts read); awaiting Stage-A authorization paste; nothing auto-triggered.
- Tidy [repo-observed]: branch `codex/nbpolar-phase0`; 92 dirty → 1 via 7 scoped commits (7a7c4cea gitignore+probe-versioning; 9ee31ad P19/P20/X sources+tests; 2e946ec P19–P20Q+X08–X10 packet evidence; ce84622 phase4-p0 specs p20a–p20q + tasks + feasibility strategy; d88adbc memory/decision-log/CURRENT_TASK/index; c3c729e X-probe results; 635b64af Astra6 zip +421B). No push. `.gitignore` ignores transient classes (`*.parquet`, `*.log`, `*.tmp`) and versions `workspace/probes/*` via per-dir negations (x04/x05 excluded: >2MB results.json stay ignored). Remaining 1 dirty entry `comparison_bench/outputs_comparison/test_fixtures/real_polar_max_pie_grid.csv` is DrvFs stat-only dirty (`git diff` empty, blob hash == index) — benign.
- Incident [repo-observed]: stray `D:/` dir in repo root accumulated 2.3 GB / 3597 files. Root cause: `comparison_bench/tests/test_evidence_package.py:27` hardcodes `TEST_DIR = Path("D:/Code/...")`; under WSL it resolves as RELATIVE and `mkdir -p` recreates the tree in-repo on every test run. Moved (not deleted) to `/mnt/d/Code/.stray_dcolon_20260919/` (2.3G preserved). Open follow-up (non-blocking): fix the hardcoded Windows path so the tree cannot regrow; until then it reappears on test runs; never `git add` it.

## 2026-09-19 NB-Polar Phase 4 P20O alt-L2 maintain-confirmation on 2M (first 2M use) accepted (descriptive complete; restoration replicated)

- Factor [repo-observed]: packet `.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/` accepted descriptive (`MAIN_THREAD_ACCEPTANCE.md`, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md` on disk). Maintain-confirmation of `ALT-L2-LAPLACE-α1` on the FIRST use of the reserved 2M independent session, with per-session Stage-A derivation (2M raw prior canonical digest `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`; orders sha `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; alt table sha `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5`; session H1/H2/H 0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477; K_total 7080, K1/K2 334/6746; D2 FEASIBLE margin 4791.09652735766).
- Stage B [repo-observed]: one-shot on 2M VAL 2187..2826 (5 blocks), label `TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE`. A 0/5, **B 2/5 (b1 `2315..2442`, b2 `2443..2570` exact)**, C 0/5, **D 3/5 (b1, b2, b4 `2699..2826` exact)**; `b_restored_count` 2, `b_maintained` 0, `d_restored` 3, `d_maintained` 0; integrity 29/29 gate keys; key 692580 = 10*35464 + 10*33794; public 6554860; SC 30; tags 20; `undetected` 0; counts 1/1 + 2M VAL-DEV 1/1 + attempts 1/1 SPENT; 2M remainder 2827..2915 and HOLD 2916..3644 untouched.
- Scientific reading [decision, descriptive only]: **restoration replicated on an independent session** — combined with P20N (1.5M HOLD B 1/4 vs A 0/4), the frozen alt-L2 construction yields B 3/9 vs control A 0/9 restoration events across two sessions. No maintain events (A is never exact anywhere). Oracle gap persists (D 3/5 > B 2/5); L1 is not universal on 2M (b0/b4 operational first errors L1 @6834/14296); alt metric has higher average CE/prefix-hazard yet restores blocks → mechanism likely order/metric-side (H2 open). No reliability/FER claim.
- Instrumentation [repo-observed]: the ninth U-domain scalar (`l2_fail_in_prefix_u_domain`) definitively closed the P20N domain-mixed reading — all 11 L2 failures are natural-index-in-X-prefix but U-domain-out (genuine undisclosed-region SC errors, no pinning violation). Instrumentation remains 9 scalars per record, NOT a per-position hazard series.
- Risks/debt [repo-observed, non-blocking]: λ code paths remain (`per_session_calibration.py` retains the λ program; `empirical_diagnostic.py` still references `LAMBDA_STAR`) — future misuse risk, disposition unchanged (raw+floor only for target-channel priors); the f=1.3 operating point still has no demonstrated margin; 1M-HOLD thread open; the worktree carried ~89 uncommitted changes before the pending milestone commit (being made separately).
- Scope [decision]: descriptive confirmation only — no FER/recovery/qualification/promotion claim; no rerun/retuning; P19 roots untouched; no commit/push. Next gate is main-thread planning for the next single factor (candidates: H2 adjudication from the 9 scalars; per-position instrumentation enhancement; L2 construction-family expansion with X02/X03/X03b materials; L1-side 2M robustness); nothing auto-triggered.

## 2026-09-19 NB-Polar Phase 4 P20N alt-L2 construction HOLD (1.5M HOLD) accepted (descriptive complete; first operational restoration)

- Factor [repo-observed]: packet `.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/` accepted descriptive (`MAIN_THREAD_ACCEPTANCE.md`, `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md` on disk). ONE preregistered alternative L2 construction `ALT-L2-LAPLACE-α1` — `f_alt=(counts_ab+1)/(n_b+1024)` (α=1; L1 path/K/order unchanged), artifact `alt_l2_tables_1p5m.npz` sha256 `6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78`; D2 feasibility FEASIBLE (ce_alt 0.9027311772313849 vs incumbent 0.8003665547439149; alt ideal length 29580.70 ≤ 33509).
- Stage B [repo-observed]: one-shot on HOLD 2213..2724 (first HOLD use), 4 blocks, fixed disclosure K1=331/K2=6689, tag master 2026092300, label `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE`. A control-L2 0/4 (L2 fails @111/76/3/81); B alt-L2 operational 1/4 (block 3 `2597..2724` EXACT; fails @1009/20/5823); C control-oracle 0/4; D alt-oracle 1/4 (b3 exact). `b_restored_count` 1, `d_restored_count` 1, `b_maintain_count` 0; all 14 failures L2-layer; L1 exact on all 8 operational records; `undetected` 0 isolated; integrity 28/28 gate keys true; key 549384 / public 5243888 / SC 24 / tags 16 / recount 0. Consumption: counts 0/0, HOLD 1/1 SPENT, attempts 1/1 SPENT, VAL-remainder 0, 2M pristine.
- Scientific reading [decision, descriptive only]: FIRST operational exact block on the 1.5M session, out-of-sample, at fixed disclosure, restored under BOTH hard-L1 (B) and true-L1 (D) → gain is L2-metric-side. Alt metric has HIGHER average prefix hazard (0.8925–0.9035 vs 0.7954–0.8556) yet decoded one block exactly; neighbourhood floor fraction 0.0 on every failing record → floors exonerated in-run; descriptive support for "incumbent spikiness, not average length, drives out-of-sample L2 failures". No reliability/recovery claim.
- Instrumentation [repo-observed]: X09-R1 payload `l2_fail_in_prefix` true on 12/14 failures, false on the shared B-b2/D-b2 event @5823; the field is a frozen-definition domain artifact (X-domain error index tested against the U-domain disclosure set) — not a pinning violation; a U-domain cross-check would need arrays not persisted (successor instrumentation item).
- Branch [decision]: the b3 restoration event activates the deferred `b_restoration_branch_maintain_confirmation_round`; no auto-trigger. Data options: VAL remainder 2044..2212 (one block + 41-frame stub) vs reserved 2M first-use (independent session; needs per-session raw calibration + new freeze/tags). 1M-HOLD thread remains open.
- Scope [decision]: descriptive confirmation only — no FER/recovery/qualification/promotion claim; no rerun/retuning; P19 roots untouched; no commit/push.

## 2026-09-19 NB-Polar Phase 4 X08 prior audit + P20M raw-prior VAL (1.5M VAL) accepted (descriptive complete); P20L superseded

- X08 Tier-X probe [repo-observed]: `workspace/probes/nbpolar_x08_per_session_prior_entropy_audit/results.json` (packet `.workbuddy/queue/NBPOLAR-X08-PER-SESSION-PRIOR-ENTROPY-AUDIT/`); on 1.5M TRAIN counts P20H λ=137.3823795883264 gives H1 2.006647056368773 / H2 1.9017235959286112 / TOTAL 3.908370652297384 vs P7-equivalent raw-count MLE + 1e-15 floor H1 0.025199496923753 / H2 0.800366554749543 / TOTAL 0.825566051673296; implied K_total 33285 vs 7020; L1 side-info N·H1 65754 vs 826 bits; floor hits 1,046,140/1,048,576; zero columns 0. Focused review PASS.
- Prior disposition [decision]: λ concentration program must not be used to build the target-channel prior for new sessions (reaffirms X07); raw+floor is the canonical rule; the λ point survives only as a control arm.
- P20L supersession [decision]: `NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M` SUPERSEDED by P20M (user decision 2026-09-19), zero consumption (Stage B never ran; counts 0/0, DEV 0/1, HOLD 0/1, attempts 0/1); VAL DEV segment 1660..2043 released; STATUS.yaml corrected by main thread (implementation_authorized false; stale "no order file exist" note superseded: `derive_l1_order_1p5m.py` + `new_l1_order_1p5m.json` exist unused).
- P20M Stage A [repo-observed]: `NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M` derived `raw_prior_1p5m.npz` (canonical digest `372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac`) under the raw rule (no λ) + `raw_prior_orders_1p5m.json` (sha `a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638`), K_total 7020 (same-run H literal) split K1=331/K2=6689 via accepted `select_empirical_split` on 16 synthetic TRAIN blocks (seeds 2026092291..2026092294); thin runner `raw_prior_val_1p5m.py`; 19 focused tests green. Packet dir holds `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS), `MAIN_THREAD_ACCEPTANCE.md`.
- P20M Stage B [repo-observed]: one-shot exit 0, wall 104.85 s, RSS ~531 MB on VAL 1660..2043 (first genuinely out-of-sample 1.5M segment), tag master 2026092280, label `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE`. G0 (λ control 319/6492) 0/3, L1 first errors 24/5/17; G1 (raw 331/6689) 0/3 with L1 breakthrough — first errors L2/26 (l1_exact TRUE), L1/848, L2/31 (l1_exact TRUE), `g1_restored_count` 0; G2 (true-L1 oracle K2 6689) 0/3, L2 first errors 26/3646/31, `oracle_l2_exact` false. Accounting 25/25 gates, `undetected` 0 isolated, key 308376 = 3×34119+3×35164+3×33509, public 2949687, tags 9, SC 15, sampling 0, counts 0/0, DEV 1/1 spent, HOLD 0/1, attempts 1/1 spent, 2M pristine.
- Scientific reading [decision, descriptive only]: λ fix unblocked L1 (first errors ~2–17 → 848/L2; 2/3 blocks hard-L1-exact) but L2 is now the bottleneck — FIRST genuine out-of-sample L2 evidence (prior TRAIN-segment oracle arms 3/3 exact; now 0/3 on VAL at K2=6689 under true L1). Both §16 L2-implication triggers fired (new-point oracle non-exact; bottleneck-layer move). No restoration/recovery evidence. Next planning input: L2-side single factor / P20D candidate; nothing auto-triggered; 2M reserved for future independent-session confirmation; 1M-HOLD thread stays open.
- Scope [decision]: descriptive confirmation only — no FER/recovery/qualification/promotion claim; no rerun/retuning; P19 roots untouched; no commit/push.
- Doc state [repo-observed]: `CURRENT_TASK.md` was stale at triage time (still said P20A pending); P20M reviews/acceptance persisted in the packet dir; CURRENT_TASK/DOCUMENT_INDEX batch update separate.

## 2026-09-18 NB-Polar Phase 4 P20K L1-disclosure +512 (1.5M DEV) accepted (descriptive complete)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20K` Stage B executed once verbatim with the FREEZE §10 16-flag command — exit 0, wall ~108 s, RSS ~559 MB, no transcription correction, no rerun/tuning. Long-term authorization + independent merged review: Stage A R1-R8 all PASS; Pre-EXECUTE `PRE_EXECUTE_PASS_CONDITIONAL`; `PRE_EXECUTE_REVIEW.md` on disk.
- Result [repo-observed]: label `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_512_1P5M_COMPLETE`; evidence root `l1_dose_512_1p5m/` (five files); 21/21 gates PASS. E0 base-K1 0/3 verify_failed (first errors 16/7/3, all L1 layer; raw SER ~0.258/0.254/0.257); E1 L1+512 (K1 831, keyΔ+2560) 0/3 verify_failed (first errors 3/5/2, all L1) → `e1_restored` 0/3 (no recovery); E2 oracle 3/3 exact isolated. Undetected 0. Key 309966 (102357+110037+97572) / public 2949687 / recount 0; ratio ~10.41%/11.19%. SC 15 / tag 9. Consumption counts 0/0 + DEV 1/1 + attempt 1/1; HOLD 0/1; 2M pristine.
- Reviews [repo-observed]: independent Pre-RESULT PASS, 8 items all PASS. STATUS notes residual template copy (non-semantic) only; full-repo dirty does not BLOCK.
- Acceptance [decision]: main-thread state `..._ACCEPTED_DESCRIPTIVE`; next_gate P20L. Scientific reading descriptive only: three-dose chain (+128 mixed / +256 all-delayed / +512 all-early, 9 blocks all zero recovery) COMPLETE — disclosure-route evidence closure holds (E1 zero-recovery trigger genuine satisfied); next step must be a new packet with a single factor转向 non-disclosure factor. SCL still locked.
- Scope [decision]: descriptive confirmation only — no FER/recovery/qualification/promotion claim; no rerun/retuning; P19 roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P20J L1-disclosure +256 (1.5M DEV) accepted (descriptive complete)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20J` Stage B executed once verbatim with the FREEZE §10 16-flag command — exit 0, wall ~108 s, RSS ~533 MB, no transcription correction, no rerun/tuning. Long-term authorization + independent merged review: Stage A R1-R8 all PASS; Pre-EXECUTE `PRE_EXECUTE_PASS_CONDITIONAL`; `PRE_EXECUTE_REVIEW.md` on disk.
- Result [repo-observed]: label `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_ESCALATION_1P5M_COMPLETE`; evidence root `l1_dose_escalation_1p5m/` (five files); 21/21 gates PASS. D0 base-K1 0/3 verify_failed; D1 L1+256 (K1 575, keyΔ+1280) 0/3 verify_failed → `d1_restored` 0/3 (no recovery); D2 oracle 3/3 exact isolated. First errors all L1 layer and D1 coordinates all later (blk0 14→23; blk1 6→25; blk2 1→21). Key 306126 (102357+106197+97572) / public 2949687 / recount 0; ratio ~10.41%/10.80%. SC 15 / tag 9. Consumption counts 0/0 + DEV 1/1 + attempt 1/1; HOLD 0/1; 2M pristine.
- Reviews [repo-observed]: independent Pre-RESULT pass with comments, 8 items all PASS. Dose response: +128 mixed move / +256 all-delayed / both zero recovery — disclosure causally active but insufficient; cross-packet coordinate comparison is non-same-block and must not be read as slope. STATUS notes residual template copy (non-semantic) only.
- Acceptance [decision]: main-thread state `..._ACCEPTED_DESCRIPTIVE`; next_gate P20K. Scientific reading descriptive only: "+256 falsifies the second dose, L1 bottleneck deeper than +256". §16 branch: D1 zero-recovery literally meets P20D candidate wording but failures all L1-side and P20D is an L2 construction — semantic offset, must not auto-trigger. SCL still locked.
- Scope [decision]: descriptive confirmation only — no FER/recovery/qualification/promotion claim; no rerun/retuning; P19 roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P20I L1-disclosure +128 (1.5M DEV) accepted (descriptive complete)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20I` Stage B executed once verbatim with the FREEZE §10 16-flag command — exit 0, wall ~111 s, RSS ~533 MB, no transcription correction, no rerun/tuning. Long-term authorization + independent merged review: Stage A R1-R8 all PASS; Pre-EXECUTE `PRE_EXECUTE_PASS_CONDITIONAL`; `PRE_EXECUTE_REVIEW.md` on disk.
- Result [repo-observed]: label `TARGET_EMPIRICAL_N32768_DEV_L1_DISCLOSURE_1P5M_COMPLETE`; evidence root `l1_disclosure_1p5m/` (five files); 21/21 gates PASS. C0 base-K1 0/3 verify_failed; C1 L1+128 (K1 447) 0/3 verify_failed → `c1_restored` 0/3 (no recovery); C2 oracle 3/3 exact isolated. `L1_exact` 6/6 operational false. First errors all L1 layer (blk0 2→2 unchanged; blk1 17→1 earlier; blk2 13→16 later). Raw SER ~0.252/0.253/0.254. Key 304206 (102357+104277+97572) / public 2949687 / recount 0; ratio ~10.41%/10.61%. SC 15 / tag 9. Consumption counts 0/0 + DEV 1/1 + attempt 1/1; HOLD 0/1; 2M pristine.
- Reviews [repo-observed]: independent Pre-RESULT pass with comments, 8 items all PASS. STATUS notes residual boilerplate copy (non-semantic) + mixed Chinese/English style issue only.
- Acceptance [decision]: main-thread state `..._ACCEPTED_DESCRIPTIVE`; next_gate P20J. Scientific reading descriptive only: "+128 moves first-error coordinates but fixes nothing" — +128 minimal dose falsified, L1 bottleneck deeper than +128. §16 branch: C1 zero-recovery literally meets P20D candidate wording but failures all L1-side and P20D is an L2 construction — semantic offset, must not auto-trigger. SCL still locked.
- Scope [decision]: descriptive confirmation only — no FER/recovery/qualification/promotion claim; no rerun/retuning; P19 roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P20H per-session calibration confirmation accepted (descriptive complete)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20H` Stage B executed once verbatim with the FREEZE §10 `--prior` 16-flag command — exit 0, wall ~114 s, RSS ~559 MB, no retry/reopen/refit. Long-term authorization + independent merged review: Stage A R1-R8 all PASS; Pre-EXECUTE `PRE_EXECUTE_PASS_CONDITIONAL` (§3 calibration gate PASS, §4 covered by long-term authorization + main-thread written ruling); `PRE_EXECUTE_REVIEW.md` on disk.
- Dispatch incident [procedure]: dispatch transcription wrongly wrote `--counts`/`--prior-digest` two flags; operator CORRECTION corrected it and executed per freeze verbatim — harmless, no extra open/rerun.
- Calibration [repo-observed]: single open; λ=137.3823795883264 (D4R2 LAMBDA_STAR); recalibrated H1 2.006647056368773 / H2 1.9017235959286112 / TOTAL 3.908370652297384; prior digest `e8dd078a5367…e43b`.
- Result [repo-observed]: label `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_PER_SESSION_CALIBRATION_COMPLETE`; evidence root `per_session_confirmation/` (five files); 21/21 gates PASS. B0 base-K2 0/3 verify_failed (first errors 16/6/8, all L1 layer; L1 SER ~0.256/0.254/0.255); B1 dK2=+1024 0/3 verify_failed (same first errors/SER); B2 oracle 3/3 exact isolated. Overall exact 3 (oracle only) / verify_failed 6 / rest 0; `b1_restored` 0/3 (no recovery, no sustain). SC 15 / tag 9; key 317646 / public 2949687 / recount 0. Consumption counts 1/1 (Stage A) + DEV 1/1 + attempt 1/1; HOLD 0/1; 2M pristine.
- Reviews [repo-observed]: independent Pre-RESULT PASS, 8 items all PASS. Branch meaning: P20D literal trigger formally satisfied but failures all L1-side, and B2 all-exact only proves base-K2 solvable given true L1 — P20D semantic offset must not auto-trigger.
- Acceptance [decision]: main-thread state `..._ACCEPTED_DESCRIPTIVE`; next_gate P20I. Scientific reading is descriptive only: on 1.5M the L1-disclosure shortfall is the bottleneck (K1=319 insufficient, +1024 L2 does not rescue); B2 all-exact proves the L2 chain sufficient given true L1; the next single factor should be an L1-disclosure increment on 1.5M, not P20D. SCL still locked.
- Scope [decision]: descriptive confirmation only — no FER/recovery/qualification/promotion claim; no rerun/retuning; P19 roots untouched; no commit/push.

## 2026-09-16 NB-Polar Phase 4 P20A resource-endpoint instrumentation implementation complete (reviewed, main-thread return pending)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20A-RESOURCE-ENDPOINT-INSTRUMENTATION` implementation stage complete + independent review `ACCEPT_WITH_COMMENTS`; all R1-R6 accepted; main-thread return pending. Zero protected reads (not even stat), zero attempts, zero output roots, zero result claims; no commit/push.
- Failure-classification seam [repo-observed]: `except MemoryError: raise` inserted before broad `except Exception` at 3 internal SC sites — `formal_ir/nbpolar/operational_f13.py` L1 site (~L804) and L2 site (~L841) in `run_operational_block`, plus `formal_ir/nbpolar/holdout_backoff_diagnostic.py` oracle-L2 site (~L728) in `run_oracle_control_block`. All other catches in the four shared helpers verified narrow; runner-level and outer-finalize handlers already correct (`operational_f13.py:1854`, `operational_f13_replication.py:1317`, `holdout_microcheck.py:1406`, `holdout_backoff_diagnostic.py:2260/2294`; finalize handlers opf:1948, replication:1408, microcheck:1508, backoff:2373). Decode/nonfinite taxonomy UNCHANGED (`classify_operational_outcome` untouched).
- Endpoint fields [repo-observed]: scalar fields `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`, `pair_exact` added (defaulted) to `OperationalBlockResult` and `OracleControlResult`, scored pre-truth-sentinel, persisted in block/control/abort records. `pair_exact` = tag-independent label equality; `exact` unchanged = tag-verified (`tag_pass` AND `label_match`). Cross-arm Nones: operational arms `oracle_l2_exact=None`; oracle arm `l1_exact`/`hard_l2_exact`/`pair_exact=None`.
- Endpoint asymmetry [decision]: 233/384 = operational-arm complete-pair exact; 377/384 = oracle-arm complete-label exact (ORACLE_CONDITIONED L2 AND true H in final label — not a pure L2 endpoint); denominator 384 paired N=256 synthetic blocks; 144 = `oracle_only` cell. Fixed one residual mislabel in `docs/nbpolar/astra6/PROJECT_BRIEF.md` item 2 (other docs already asymmetric; remaining 233/384 hits use gate-"exact" shorthand, not the symmetric-L2 mislabel).
- Tests [repo-observed]: 5 NEW MemoryError tests (9 total incl. 4 pre-existing): L1/L2 escape + runner finalize (ResourceError BLOCKED + 5-file finalize + empty jsonl) + oracle escape; ordinary-failure pinning (`RuntimeError`→`decode_failed`, `NumericNonfiniteError`→`nonfinite`). Suites green, injected-only: opf 29, replication 25, microcheck 26, backoff 33 = 113 total.
- Scope [decision]: no GF32/transform/arithmetic/prior/construction/disclosure/tag/precedence change; no SCL/new kernel/model/schema; no protected reads, attempts, output roots, or result claims; no commit/push.
- Review attribution notes [procedure]: (a) `PROJECT_BRIEF.md` item-11 hunk (five-arm 15/15 `verify_failed`) belongs to P19/main-thread lifecycle, not P20A — attribution only; (b) "frozen roots byte-identical" phrasing is stale (P19 roots advanced 11/15→15/15 under P19's own completion); (c) "9 new tests" should read "5 new (9 total)".

## 2026-09-16 NB-Polar Phase 4 P18 N32768 1M HOLD real-input microcheck accepted (descriptive complete)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK`
  executed once + independent Pre-EXECUTE PASS and Pre-RESULT
  PASS_WITH_COMMENTS (the latter completed as a resumption from an interrupted
  first attempt); state
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE_ACCEPTED_DESCRIPTIVE`,
  result label `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE`;
  main thread accepted it as descriptive only — NOT a FER/recovery/
  qualification/promotion claim.
- Code delta [repo-observed]: thin runner
  `formal_ir/nbpolar/holdout_microcheck.py` (fixed P16 construction reuse;
  zero TRAIN/genie/RNG/fitting paths on HOLD; five files created pre-open +
  per-block checkpointing; one content open per protected input); +26 focused
  tests (full NB-Polar suite 409 = 383 + 26 green, zero protected opens via
  audit). OpenSpec P18 delta under
  `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p18/spec.md` + tasks.
- Gate [repo-observed]: 1M HOLD split of `type2_1M_20260121_184040` = 400
  frames / 102400 symbols; three chronological N=32768 blocks (frames
  1600..1727, 1728..1855, 1856..1983); remainder frames 1984..1999 (4096
  symbols) unused; tag_master 2026092050; 6 SC calls / 3 tag invocations.
  Predecessor digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` match
  true; manifest 400/102400; preconditions 7/7; consumption train read 1/1 +
  hold read 1/1 + attempt 1/1 at first protected open (opens 1 each; no
  reopen/rerun; sizes+mtime unchanged).
- Result [repo-observed]: per-block buckets all `verify_failed` (exact 0/3;
  L1 correct true/false/false; tag pass false for all three); raw SER
  0.240936279296875 / 0.23980712890625 / 0.240264892578125; total NLL bits
  27589.350245339167 / 27884.160498770143 / 27688.088800952148 (aggregate
  83161.59954506146); disclosure key 102357 / public 983229 / tags 3, recount
  mismatch 0; sample CE-normalized disclosure ratio 1.2366728355903898 /
  1.2235978917674373 / 1.232262733815947 (aggregate 1.230820481567787;
  34119 per-block NLL; explicitly NOT qualification efficiency); 17/17
  integrity gates true; wall 37.274417 s; RSS peak 520798208 B; no resource
  stop. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/`
  (5 files).
- Scope [decision]: real-input microcheck at N=32768 with FIXED P16
  construction only — no recovery or FER threshold and not
  qualification/promotion; exact 0/3 is a descriptive observation with no
  FER meaning; no Model-F/HOLD fitting, no fitting/tuning on HOLD;
  P12-P17/old roots untouched; no commit/push.
- Process lesson [procedure]: a reviewer subagent manually terminated mid-run
  can be resumed from its saved session transcript — re-execute the
  interrupted suite fresh, write the review, and note the resumption in the
  review file (P18: the first Pre-RESULT attempt was interrupted during the
  full-suite run; the resumption re-ran both suites with zero protected
  opens). Primary coder-doc/memory/reviewer models can be region-blocked
  while their backup instances work.

## 2026-09-16 NB-Polar Phase 4 P19 HOLDOUT backoff diagnostic executed once (descriptive complete; acceptance pending)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC`
  executed once + two independent reviews; state label
  `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`; main-thread
  acceptance pending — do not describe as accepted, qualified, promoted, or
  as any FER/recovery/superiority/route result.
- Code delta [repo-observed]: thin runner
  `formal_ir/nbpolar/holdout_backoff_diagnostic.py` (reuses P18 loading/block
  formation and P16/P17 operational helpers unchanged; five arms hardcoded,
  not CLI-tunable; five files created pre-open + per-arm checkpointing; one
  content open per protected input); +30 focused tests (predecessor suites 23
  + 51 also green = 104 total; full NB-Polar suite intentionally skipped per
  packet rule — no shared predecessor change). OpenSpec P19 delta under
  `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p19/spec.md` + tasks.
- Gate [repo-observed]: same three P18 HOLD blocks (frames
  1600..1727 / 1728..1855 / 1856..1983) at N=32768; remainder 1984..1999
  unused; fixed P16 construction K1=319/K2=6492, predecessor digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`; tag
  master 2026092060 with P19/arm/block domains; five arms with K1/K2/leakage:
  `base` 319/6492/34119; `l1_plus` 447/6492/34759 (+128 L1); `l2_plus`
  319/7004/36679 (+512 L2); `both_plus` 447/7004/37319;
  `true_l1_control` (oracle, provenance ORACLE_TRUE_L1_CONTROL, K1=0/K2=6492/
  leakage 32524, deployable false, excluded from operational aggregates).
- Consumption [repo-observed]: train read 1/1 + hold read 1/1 + attempt 1/1
  at first protected open; opens 1 each; no reopen/rerun; 27/27 SC calls;
  15/15 tags; wall 186.42 s; RSS peak 615960576 B; no resource stop.
- Results [repo-observed]: all 15 records `verify_failed` (exact 0/15; tag
  false for all 15; paired-vs-base all verify_failed->verify_failed;
  first_operational_recovery_arm null; ordered non-monotone false); block SER
  0.2409 / 0.2398 / 0.2403; block NLL 27589.35 / 27884.16 / 27688.09;
  per-arm aggregate CE ratios `base` 1.230820 / `l1_plus` 1.253908 /
  `l2_plus` 1.3231707976032374 / `both_plus` 1.346258 / control 1.1732819
  (control excluded from operational aggregates; the earlier operator
  transcription 1.339389 for l2_plus is superseded — artifact value
  1.3231707976032374 is authoritative). Accounting key 526200 (operational
  428628 + control 97572), public 4916145, recount mismatch 0; 20/20
  integrity gates true; evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/`
  (5 files).
- External-commit anomaly [procedure]: a concurrent external commit landed
  during the run window (HEAD ab173f2a ->
  faac0411684819f5a9055cd71fc1b4bae6955287, author Placebo303,
  2026-09-16 21:14:28 +0800) committing a MID-RUN snapshot of the P19
  artifacts (RUNNING, record 11/15) — an add-before-commit race. The
  finalized worktree five files are authoritative for acceptance/evidence;
  never cite `git show HEAD:` blobs for those four modified paths, do not
  git restore/checkout/stash them, and re-add after acceptance if committing.
- Scope [decision]: five-arm descriptive diagnostic on the three registered
  1M HOLD blocks only — no threshold of any kind (0/15 and 15/15 both count
  as COMPLETE); oracle control never operational; CE ratio is NOT
  qualification efficiency; no fitting on HOLD; P12-P18/old roots untouched;
  no commit/push by this packet's operators.

## 2026-09-16 NB-Polar Phase 4 P19 HOLDOUT backoff diagnostic frozen (not authorized)

- [next/status] Tier-Y packet
  `NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC` remains frozen awaiting
  explicit user authorization; `execution_authorized: false`, TRAIN/HOLD
  protected reads 0/1 and attempt 0/1, with no result or review. P19 has not
  run.
- [scope] The same three P18 blocks have five frozen descriptive arms:
  `base`; `l1_plus` (+128 L1); `l2_plus` (+512 L2); `both_plus` (+128 L1 and
  +512 L2); and `true_l1_control` (oracle-labelled true-L1 control, excluded
  from operational aggregates). There is no recovery, FER, Wilson,
  superiority, qualification or promotion threshold; outcomes remain
  descriptive and cannot be converted to pass/fail.

## 2026-09-18 NB-Polar Phase 4 P17 operational F13 N32768 replication accepted (model-sampled only)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION`
  candidate stage executed once + two independent reviews; Pre-RESULT
  PASS_WITH_COMMENTS with independent 123/128 recount confirming the candidate
  classification. Main thread accepted
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE` as a
  model-sampled operational development signal only — not qualified, promoted,
  or a real-data FER result.
- Code delta [repo-observed]: thin runner
  `formal_ir/nbpolar/operational_f13_replication.py` (ZERO TRAIN/genie/BEC/
  adaptive paths; reads accepted P16 construction file read-only with digest
  verification; reuses P16 operational helpers + accepted P7/P11 contracts;
  P17 N/block tag domains; five files created pre-open + per-block
  checkpointing); +25 focused tests (full NB-Polar suite 383 = 358 + 25
  green). OpenSpec P17 delta under
  `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p17/spec.md` + tasks.
- Gate [repo-observed]: N=32768; V25 1M TRAIN NPZ 25166822 B read-only;
  preconditions 7/7; read 1/1 + attempt 1/1 at first open, opens 1, no
  reopen/rerun; 256 operational SC calls, 0 TRAIN/genie calls, 128 tags.
  Predecessor digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  triple-match (stored==recomputed==frozen); K_total=6811 (K1 319/K2 6492,
  f 1.29985, leakage 34119); DEV 128 blocks (streams 2026092030..2037x16,
  fresh vs P16); P16 root untouched; scored tag domains P17-only.
- DEV [repo-observed]: exact 123 / undetected 0 / verify_failed 5 /
  decode_failed 0 / nonfinite 0 / resource_abort 0 (per-stream
  15/1,15/1,16/0,15/1,15/1,15/1,16/0,16/0); exact fraction 123/128=
  0.9609375; one-sided 95% Wilson LB 0.921934049951655 (EXACT-COUNT MARGIN
  exactly 2 over 121/128→0.9021084760; LB margin +0.0219; 120/128→
  0.8924595822 False). P16's 62/64 report-only, pooled_into_decision false
  (decision inputs exactly the 128 P17 blocks). Disclosure totals key
  4367232 / public 41951104 / tags 128, recount mismatch 0. Resources: wall
  2031.39 s (margin 368.6 s vs 2400 s); RSS peak 569614336 B; per-record
  VmPeak/VmSize present; no resource stop. 14/14 integrity true. Evidence
  root
  `.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate/`
  (5 files).
- Scope [decision]: model-sampled replication at N=32768/f≤1.3 ONLY — not
  real-data FER/qualification/promotion; P16 never pooled; threshold-sit
  context (P16 was exactly 62/64 zero-margin; P17 has 2-count margin); no
  BEC/adaptive; no Model-F/HOLD/raw/real/EVAL beyond the single V25 TRAIN
  read; P12-P16/old roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P18 N32768 1M HOLD operational microcheck frozen

- [next/status] Tier-Y packet
  `NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK` is frozen awaiting explicit
  user authorization; `execution_authorized: false`, protected reads and
  attempt remain 0/1, and no result or review exists. Do not describe P18 as
  executed, candidate, accepted, or a FER result.
- [scope] P18 is a real-input/interface microcheck that reuses the accepted
  P16/P17 N=32768, K1=319/K2=6492, leakage=34119 construction and fixed TRAIN
  prior. The 1M HOLD split has 400 frames / 102400 symbols; at 32768 symbols
  per block it provides only three non-overlapping chronological blocks
  (frames 1600..1983), with 4096 symbols (frames 1984..1999) left as an
  unused remainder. The three blocks are explicitly insufficient for any FER,
  Wilson, qualification, or promotion claim; P18 has no recovery threshold.
- [boundary] P18 forbids shuffling, overlap, padding, resampling, HOLD fitting,
  pooling with TRAIN/VAL/P16/P17, and any decoder/prior/construction/tag
  semantic change. If later authorized, it must remain descriptive regardless
  of 0..3 exact outcomes, use one read per TRAIN NPZ and HOLD parquet, and
  preserve the five-file checkpointed root and no-commit/no-push rule.

## 2026-09-18 NB-Polar Phase 4 P16 operational F13 N32768 CANDIDATE (pending main-thread acceptance)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13`
  candidate stage executed once + two independent reviews; Pre-RESULT
  PASS_WITH_COMMENTS with independent 62/64 recount confirming CANDIDATE
  uniquely correct. Verdict is
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` only — NOT accepted,
  NOT qualified, NOT promoted, NOT BLOCKED. Main-thread acceptance pending.
- Code delta [repo-observed]: thin runner
  `formal_ir/nbpolar/operational_f13.py` (reuses P7 loader/support/preconditions,
  P13 construction/allocation, P4 causal wiring, P5 hard-candidate/tag semantics,
  P11 chunk_rows=512 SC; five files created pre-open + per-block checkpointing);
  +23 focused tests (full NB-Polar suite 358 = 335 + 23 green). OpenSpec P16
  delta under `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p16/spec.md` +
  tasks.
- Gate [repo-observed]: N=32768; V25 1M TRAIN NPZ 25166822 B read-only;
  preconditions 7/7; read 1/1 + attempt 1/1 at first open, opens 1, no
  reopen/rerun; TRAIN genie 32 + DEV SC 128 calls. K_total=6811 (K1 319/K2
  6492, f 1.29985, leakage 34119); TRAIN 16 blocks; DEV 64 blocks (streams
  2026092010..2017x8); orders frozen pre-DEV.
- DEV [repo-observed]: exact 62 / undetected 0 / verify_failed 2 /
  decode_failed 0 / nonfinite 0 / resource_abort 0 (the two verify_failed:
  stream 2026092015 block 5 + stream 2026092017 block 3, both tag False/label
  False); exact fraction 62/64=0.96875; one-sided 95% Wilson LB
  0.9098711859061207 (margin +0.00987 over the 0.90 gate; EXACT-COUNT MARGIN
  ZERO — one fewer exact flips to NOT_CONFIRMED at 61/64→0.8884). Disclosure
  totals key 2183616 / public 20975552 / tags 64, recount mismatch 0.
  Resources: wall 1183.62 s (≤2100); RSS peak 545861632 B; VmPeak ≤763408 kB;
  no resource stop. 13/13 integrity true. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/`
  (5 files).
- Scope [decision]: model-sampled operational outcome at N=32768/f≤1.3 ONLY —
  not real-data FER/qualification/promotion; no BEC arm; threshold-sit
  neutrality (exactly at 62/64); no Model-F/HOLD/raw/real/EVAL beyond the
  single V25 TRAIN read; P12-P15/old roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P15 empirical-genie mid-N scaling NEGATIVE (NOT_CONFIRMED, no candidacy, no acceptance)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING`
  negative stage executed once + two independent reviews; Pre-RESULT PASS.
  Verdict is `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` only
  — NOT candidate, NOT accepted, NOT qualified, NOT promoted, NOT BLOCKED.
  Main-thread acceptance pending.
- Code delta [repo-observed]: thin runner
  `formal_ir/nbpolar/empirical_genie_mid_n.py` (reuses P13 helpers +
  accepted P7/P11 contracts; per-N TRAIN-freeze-DEV loop; five files created
  pre-open + per-block checkpointing; NO BEC arm by design); +15 focused
  tests (full NB-Polar suite 335 = 320 + 15 green). OpenSpec P15 delta under
  `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p15/spec.md` + tasks.
- Gate [repo-observed]: V25 1M TRAIN NPZ 25166822 B read-only; preconditions
  7/7; read 1/1 + attempt 1/1 at first open, opens 1, no reopen/rerun; genie
  calls 128/128. Allocations: N=32768 K 6811 (K1 314/K2 6497, f 1.29985,
  leakage 34119) / N=65536 K 13636 (K1 607/K2 13029, f 1.29996, leakage
  68244); TRAIN 16+16 blocks; DEV 16+16; N-to-seed grouping exact
  (1960..63/1970..73 → 32768; 1980..83/1990..93 → 65536); TRAIN∩DEV ∅;
  orders frozen pre-DEV.
- DEV [repo-observed]: empirical residual one-sided 95% t UCBs (factor
  1.753050356, df=15, n=16): N=32768 mean 0.01915 / UCB 0.03590; N=65536
  mean 0.02877 / UCB 0.07613 — BOTH >0.01 →
  `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` (12/12 integrity
  true; candidate_ns empty). N=65536 mean exceeds N=32768 mean (descriptive
  numbers only, no improvement claim). Resources: wall 1620.51 s (≤2100);
  RSS peak 1033293824 B (0.48×2GiB); VmPeak max 1241560 KiB; no resource
  stop. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate/`
  (5 files).
- Scope [decision]: genie union-bound construction proxy only — not
  operational FER/real-channel/minimum-N; no qualification/promotion; no
  Model-F/HOLD/raw/real/EVAL/tag beyond the single V25 TRAIN read;
  P12/P13/P14/old roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P14 empirical-genie learning curve NEGATIVE (NOT_CONFIRMED, no candidacy, no acceptance)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE`
  negative stage executed once + two independent reviews; Pre-RESULT
  PASS_WITH_COMMENTS non-blocking. Verdict is
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED` only — NOT
  candidate, NOT accepted, NOT qualified, NOT promoted, NOT BLOCKED.
  Main-thread acceptance pending.
- Code delta [repo-observed]: thin runner
  `formal_ir/nbpolar/empirical_genie_learning_curve.py` (reuses P13 helpers +
  accepted P7/P11 contracts; nested 8/16/32/64/128 prefixes from ONE
  stream-major TRAIN sequence; each block decoded once per layer, 320 genie
  calls; five files created pre-open + per-block checkpointing); +15 focused
  tests (full NB-Polar suite 320 = 305 + 15 green). OpenSpec P14 delta under
  `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p14/spec.md` + tasks.
- Gate [repo-observed]: N=16384; V25 1M TRAIN NPZ 25166822 B read-only;
  preconditions 7/7; read 1/1 + attempt 1/1 at first open, no reopen/rerun.
  K_total=3399 (f 1.29981, leakage 17059); TRAIN 128 blocks (1930..37x16) +
  DEV 32 (1940..43x8); orders nested-exact, frozen before DEV; TRAIN∩DEV ∅;
  no P13 merge.
- DEV [repo-observed]: per-prefix empirical residual one-sided 95% t UCBs
  (n=32): B=8 mean 0.1176 / UCB 0.1725; B=16 0.1318 / 0.1879; B=32 0.1060 /
  0.1587; B=64 0.0898 / 0.1391; B=128 0.1420 / 0.2011 — ALL FIVE >0.01 →
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED` (13/13 integrity
  true). Paired R_128−R_8 mean +0.0244 / UCB +0.0753. Curve FLAT: B=128 not
  better than B=8 (descriptive numbers only). Allocations (K1,K2):
  (158,3241)/(161,3238)/(162,3237)/(162,3237)/(173,3226). Resources: wall
  1110.17 s; VmPeak 508308 kB; no resource stop. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/`
  (5 files).
- Scope [decision]: genie union-bound construction proxy only — not
  operational FER/real-channel/minimum-N; no route recommendation; no
  qualification/promotion; no Model-F/HOLD/raw/real/EVAL/tag beyond the
  single V25 TRAIN read; P13/old roots untouched; no commit/push.

## 2026-09-15 P13 empirical-genie negative accepted; P14 learning curve frozen

- [decision] Main thread accepted `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED_ACCEPTED` as a valid negative result within the V25 1M TRAIN model-sampled genie-proxy scope. P13 had 12/12 integrity gates true, independent Pre-EXECUTE PASS and Pre-RESULT PASS_WITH_COMMENTS, one read/attempt consumed, and no rerun or tuning.
- [result] At f=1.3, all registered N failed the frozen DEV residual-UCB criterion: N=4096 mean 0.8277 / one-sided 95% t-UCB 0.9523; N=8192 mean 0.3968 / UCB 0.4859; N=16384 mean 0.1932 / UCB 0.2525. `candidate_ns` is empty. The P13 8-block TRAIN construction was sample-limited; at N=16384 its TRAIN residual (~9.1e-5) was far below the DEV mean, so construction-sample sufficiency is the next confounder.
- [boundary] This is a genie union-bound construction proxy, not operational FER, minimum-N, efficiency, key-rate, qualification or promotion evidence. The small-N `eps_eff~0.115` scenario remains unestablished; higher HOLD entropy means fixed TRAIN disclosure has roughly f=1.23 relative to HOLD, not f~1.37.
- [next] `NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE` is frozen as the next Tier-Y gate, awaiting explicit authorization. At N=16384 it builds nested B=8/16/32/64/128 constructions from one 128-block TRAIN sequence, scores all five on the same disjoint 32-block DEV sequence, and freezes orders/allocations before DEV. Each TRAIN/DEV genie block is decoded once and reused across prefixes (320 calls total); only B=128's one-sided t-UCB (df=31, factor 1.695518782) may classify the result (`..._CANDIDATE` iff UCB<=0.01, otherwise `..._NOT_CONFIRMED`). DEV never tunes the construction.
- [procedure] P14 reads the V25 1M TRAIN NPZ exactly once and consumes one attempt at first content open; it uses the accepted 1e-15 floor, P11 chunk_rows=512, f=1.3 allocation, single-thread allocator environment, 2-GiB/1800-s limits, per-block checkpointing of exactly five files, and VmPeak/VmSize recording. No P13/old-root modification, Model-F/HOLD/raw/real/EVAL/tag/Toeplitz/operational decode/APP/SCL/FWHT work, rerun, tuning, commit or push.

## 2026-09-18 NB-Polar Phase 4 P13 empirical-genie scaling NEGATIVE (NOT_CONFIRMED, no candidacy, no acceptance)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING`
  negative stage executed once + two independent reviews; Pre-RESULT
  PASS_WITH_COMMENTS non-blocking. Verdict is
  `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` only — NOT candidate,
  NOT accepted, NOT qualified, NOT promoted, NOT BLOCKED. Main-thread
  acceptance pending.
- Code delta [repo-observed]: thin runner
  `formal_ir/nbpolar/empirical_genie_scaling.py` (accepted P7
  loader/support/preconditions/genie_conditionals, P11 chunk_rows=512 SC,
  f=1.3 BEC-budget/allocation helpers mirrored from P12, NO tag/Toeplitz;
  per-block checkpointing); +20 focused tests (full NB-Polar subset 305 =
  285 + 20 green). OpenSpec P13 delta under
  `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p13/spec.md` + tasks.
- Gate [repo-observed]: V25 1M TRAIN NPZ 25166822 B read-only; preconditions
  7/7; read 1/1 + attempt 1/1 at first open, no reopen/rerun. Allocations:
  N=4096 K 840 (K1 38/K2 802, f 1.29958) / N=8192 K 1693 (78/1615,
  f 1.29974) / N=16384 K 3399 (152/3247, f 1.29981); TRAIN 8+8+8, DEV
  32x3=96; orders frozen before DEV; genie_calls 240/240.
- DEV [repo-observed]: empirical residual one-sided 95% t UCBs (n=32):
  N=4096 mean 0.8277 / UCB 0.9523; N=8192 mean 0.3968 / UCB 0.4859; N=16384
  mean 0.1932 / UCB 0.2525 — ALL THREE >0.01 →
  `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` (12/12 integrity true;
  candidate_ns empty). Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/`
  (5 files).
- Guards [decision]: (1) eps_eff~0.115 is only a scenario hypothesis
  back-inferred from small-N, not established; (2) higher HOLD entropy =>
  fixed TRAIN disclosure is ~f=1.23 relative to HOLD (less redundancy),
  not f~1.37.
- Scope [decision]: genie union-bound construction proxy only — not
  operational FER/real-channel/minimum-N; no qualification/promotion; no
  Model-F/HOLD/raw/real/EVAL/tag beyond the single V25 TRAIN read; old
  roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P12 f=1.3 N-scaling profile TERMINAL BLOCKED (no candidacy, no acceptance)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE`
  Tier-Y terminal stage executed once + two independent reviews; no rerun
  permitted. Verdict is `BLOCKED(resource_limits_met_and_no_abort)` only —
  NOT candidate, NOT accepted, NOT qualified, NOT promoted. Independent
  Pre-RESULT: `CONFIRMED_SINGLE_RESOURCE_ABORT`.
- Code delta [repo-observed]: thin runner
  `formal_ir/nbpolar/target_n_scaling.py` (accepted P7 support/preconditions,
  P11 chunk_rows=512 SC, two-layer hard-candidate, Toeplitz tag/accounting);
  +23 focused tests (full suite 285 = 262 + 23). OpenSpec P12 delta under
  `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p12/spec.md` + tasks.
- Frozen matrix [repo-observed]: six-N profile (256x64, 4096x32, 16384x16,
  65536x8, 131072x4, 262144x4 = 128 blocks; seeds 2026091820..25) with
  analytic BEC K allocations (e.g. N=256: 40/1/39; N=262144:
  54583/2776/51807) — never executed to completion.
- Gate [repo-observed]: single run seed 2026091800 resource-aborted at the
  N=262144 arm: uncaught `_ArrayMemoryError` allocating (262144,32) float64
  (64 MiB) in `prior.py probs_to_symbol_metric` via
  `target_n_scaling.py:774` L2 candidate metric (outside SC try-guards;
  MemoryError not in caught ValueError/FileExistsError/OSError) -> exit 1
  after ~1107 s. Read 1/1 + attempt 1/1 SPENT. No output root, no label,
  ~124 blocks of progress lost (end-only writes, no checkpointing).
- Lessons [decision]: (1) gate runners must catch MemoryError AND checkpoint
  per cell (X11 lost-record + P12 lost-progress — X12 checkpointing is the
  positive pattern); (2) allocation-only SC chunking does not bound
  metric-pipeline memory — large-N profiling must budget the full per-block
  metric planes, not just SC temporaries.
- Scope [decision]: synthetic engineering gate only; terminal, no successor
  authorized; no FER/efficiency/key-rate/qualification/promotion implication;
  no Model-F/raw/held-out/real data touched beyond the single V25 TRAIN read;
  old roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P11 exact chunked SC (CANDIDATE, pending main-thread acceptance)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC`
  candidate stage executed once + two independent reviews; Pre-RESULT
  PASS_WITH_COMMENTS non-blocking. Verdict is
  `EXACT_CHUNKED_SC_CANDIDATE` only — NOT accepted, NOT qualified, NOT
  promoted.
- Code delta [repo-observed]: allocation-only promotion of X12 row-chunking
  into accepted reference SC: `_minus_block` gains keyword-only
  `chunk_rows=512` default (per-slice exact accepted expression +
  logaddexp.reduce(axis=2) + single full-matrix _normalize_rows;
  None = golden unchunked; bool/non-integral→TypeError,
  nonpositive→ValueError before allocation); `sc_decode` public signature
  UNCHANGED; thin gate runner `sc_chunked_gate.py` (required
  --seed/--chunk-rows/--out-dir, no defaults); +10 focused tests in
  `test_nbpolar_sc_chunked.py` (full suite 262 = 252 + 10). OpenSpec P11
  delta under `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p11/spec.md`
  + tasks.
- Gate [repo-observed]: seed 2026091800, float64, GF32 poly 37 alpha 2;
  attempt 1/1 at first formal sc_decode; 0 artifact reads. 33 primitive
  cells all exact (11 boundary rows x moderate/wide/-inf, err 0.0, support
  parity); 16 invalid-input cases exception type+message parity; N=64+N=256
  full-SC 9 controls each all parity (incl. X11-C3, C4
  impossible-disclosure, T5 ties); N=65536 paired direct-first exact parity
  (u/x 0 mismatches); N=262144 default-512 status ok, finite outputs, wall
  66.088411 s (report-only ≤120 met), peak RSS 710504448 B < 1610612736
  hard gate (margin 900108288); gates semantic_parity /
  paired_n65536_exact / large_n262144_completion / large_n262144_rss all
  True. Wall_total 97.955511 s (600 s envelope unhit). Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/`
  (4 files).
- Scope [decision]: synthetic injected-data engineering gate only — not
  FER/efficiency/key-rate, qualification/promotion; no throughput claim
  (single draw); no artifact/evidence/raw/held-out/real/EVAL/tag/protocol
  access; no N>262144/FWHT/APP/SCL; old roots untouched; no commit/push.

## 2026-09-17 NB-Polar Phase 4 P9 lower-rate boundary resolution (CANDIDATE, pending main-thread acceptance)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION`
  candidate stage executed once + two independent reviews; Pre-RESULT PASS zero
  comments. Verdict is `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` only —
  NOT accepted, NOT qualified, NOT promoted.
- Code delta [repo-observed]: delta-only `--gate-id p9-lower-rate-boundary` on
  accepted `target_rate.py` (P9 protocol name/tag-prefix/labels; P8 behavior
  preserved); +12 P9 tests in `test_nbpolar_target_rate.py` (24 focused; full
  suite 252 = 240 + 12). OpenSpec P9 delta under
  `formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p9/spec.md` + tasks.
- Target input [repo-observed]: accepted P7 pooled empirical orders (sha
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`) + V25 1M
  TRAIN NPZ (25166822 B) via accepted loader, floor 1e-15. One read + one
  attempt consumed at first NPZ open; no reopen/retry/rerun.
- SCREEN [repo-observed]: N=256; seeds 2026091710..1712 x64 = 192;
  shared-block sampling; exact 8x7 grid
  K1=[0,2,4,6,8,12,24,45] x K2=[0,20,40,50,60,70,80] = 56 pts incl. (0,0) and
  P8 anchor (8,80). Exactly 10 eligible (188→LB 0.9544 / 192→0.9861); (0,0)
  exact 0/192 (tag-only arm, all verify_failed, zero undetected); (8,80)
  192/192. Deterministic lexicographic-min (K1+K2,K1,K2) selected (k1=6,k2=70)
  — 444 key-dependent bits, BELOW the P8 anchor (8,80)/504 bits
  (report-only observation).
- CONFIRM [repo-observed]: seeds 2026091720..1724 x128 = 640, disjoint;
  selected point only + same-K BEC control report-only. Empirical exact
  624/640 (16 vf), BEC 520/640, paired cells 520/104/0/16, Wilson one-sided 95%
  LB 0.9626753340557015; per-stream emp [122,123,125,127,127], bec
  [103,102,97,108,110].
- Accounting [repo-observed]: 5*(K1+K2)+64 per fully invoked point ((0,0)=64
  tag-only); public 2623/tag; totals key 4392768 / public 31559936 / tags
  12032 (56x192+640x2 cross-check); recount mismatch 0; planning-only f
  2.165159928897918 (not real efficiency). 11/11 integrity + 2/2 scientific
  true. Wall 720.522313 s; RSS 318406656 B. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/`
  (5 files).
- Execution incident [repo-observed, decision]: first Wave-C delegation
  executed the gate but result delivery failed (infrastructure cert error);
  retry correctly STOPPED on existing root; read-only inspection verified
  single-flush provenance; counters aligned; NO rerun. Durable pattern: lost
  delivery with completed side effects → STOP, verify, align, never rerun.
- Scope [decision]: synthetic N=256 V25-1M-TRAIN model-sampled development
  signal only — not held-out/real FER, efficiency/key-rate, scaling,
  qualification/promotion; BEC gap + anchor comparison report-only; no
  interpolation; no Model-F/raw/held-out/EVAL; no N>256/APP/SCL/FWHT/adaptive;
  old roots untouched; no commit/push.

## 2026-09-11 venv-only

- Python唯一入口 `.venv/bin/python -m ...`；裸 `python`/`python3` 禁用（系统 python 缺 numpy/pytest）。
- AGENTS.md §8 已声明（含 WSL/bash POSIX-first，Windows 用 `.venv\Scripts\python`）；RUN_COMMANDS.md 已补头部 + 8 示例改 bash 围栏 + Windows 变体；troubleshooting 首条 `No module named numpy/pytest` → 用 venv 重跑。
- reviewer 两轮：venv 三件 scoped PASS，围栏内容 PASS 但工作树混脏需 hunk 级提交。

## NB-Polar Phase 3 blocked diagnostic (2026-09-11)

- Implementation [repo-observed]: reviewer-go test evidence reports 45/45 for
  Phase 1-3 code; generators and genie/oracle machinery remain a candidate.
- Gate [decision]: `BLOCKED(PHASE3_GATE_INVALID)`. Full-vector Spearman 0.7665
  fails frozen >=0.90; posthoc e>0 subset 0.9959 is diagnostic only. Tie count
  is 187.
- Procedure [decision]: operator self-check was not the required independent
  reviewer-go, so the EVAL was not procedurally authorized. Exact-call addendum
  still lacks the literal full 256-coordinate permutation.
- Preserved diagnostic [repo-observed]: sole seed 2026091203 EVAL, q32/N256,
  eps0.05/K45, 299/300 exact, 300/300 initial-error, one impossible at block
  104. No rerun, no gate relaxation, no Phase 4.
- Interpretation [decision]: small residual failure at the tested point is
  suggested; unique N/K causality is not proved. Any R1 needs a new reviewed
  packet and authorization, and must not reuse seed 2026091203.

## NB-Polar Phase 2 reference SC acceptance (2026-09-11)

- Phase 2 [repo-observed, decision]: reference q-ary SC and independent tiny
  enumeration oracle accepted after reviewer-go 33/33. Oracle: 221 rows,
  probability error 3.331e-16, finite-log error 1.776e-15, zero support
  mismatch; noiseless loopback 831/831.
- Semantics [decision]: classic SC marginalizes future suffix coordinates;
  disclosed U values are forced only at their turn, including zero. Plus uses
  transformed left partial sums. Alice truth is absent from `sc_decode`.
- Boundary [decision]: implementation evidence only; no construction/FER,
  Model-F, real data, protocol, result, qualification or promotion evidence.

## NB-Polar Phase 0/1 acceptance and Phase 2 packet (2026-09-11)

- Phase 0 [decision]: `FREEZE_ACCEPT`; durable verdict is
  `docs/research_cycles/NBPOLAR-PHASE0/FREEZE_REVIEW_VERDICT.md`.
- Phase 1 [repo-observed, decision]: the thin GF adapter, natural-order fast
  transform, independent dense reference, and coordinate selection are
  accepted. Plain runner and independent Miniforge pytest both passed 17/17;
  pytest was 2.06 s with one unrelated unknown-`cache_dir` warning.
- Limitations [decision]: N=1 identity lacks a dedicated test and the generic
  alpha argument accepts zero; the operative MVP remains primitive alpha=2.
- Active task [decision]:
  `.workbuddy/queue/NBPOLAR-PHASE2-SC-ORACLE/` authorizes autonomous synthetic
  reference SC/oracle implementation and focused tests only. Model-F, real
  data, benchmark/result roots, SCL, Phase 3 and scientific claims stay closed.

## NB-Polar independent worktree initialization (2026-09-11)

- Ownership [decision]: this checkout is the independent native NB-Polar
  planning and implementation location. Comparison owns NB-LDPC history and
  decisions; cascade-single owns binary Cascade exploration; Release owns the
  frozen binary Polar baseline.
- Canonical plan [repo-observed]: docs/nbpolar/ and
  openspec/changes/formal-ir-nbpolar-mvp/ are the current plan candidate.
  Phase 0–2 is not accepted or authorized; no decoder or result exists.
- Algorithm [decision]: MVP candidate is GF32 polynomial basis, polynomial 37,
  alpha=2 explicit 2x2 kernel, natural ordering, normalized float64 symbol
  metrics, source SC, static full-symbol disclosure, and one final universal
  tag. Model-F and Release behavior enter only through adapters.
- Guard [decision]: do not inherit NB-LDPC topology, prior-only APP flow,
  binary PW ordering, tag-selected paths, CRC, puncturing, shortening, or
  real-data execution into the MVP. See docs/nbpolar/VALIDATION_GATES.md.

## 2026-09-05 coder-fast → reviewer-go 必接规则持久化（一次性例外 R1 836e151c）

- Rule [decision]: 每次 coder-fast 完成（COMPLETE 返回）后必须接 reviewer-go 独立只读复核，无默认跳过；plan-only / 零生产代码不是省略理由。
- Exception [repo-observed]: V72P2D5 R1 push（commit `836e151c`）未做 post-commit reviewer 复核；用户 2026-09-05 显式特批跳过，记为一次性例外，下不为例。
- SOP status [repo-observed]: `docs/research-cycle-sop.md` 全文无 coder-fast/reviewer-go 字样，仅有通用“independent review”（§6步骤7、§10 Pre-RESULT）；`AGENTS.md` 仅 §6 行180 `/implement-change` 描述 planner → coder-fast → reviewer-go → memory triage 流水线，无强制“必接”条款；均判为明确缺失，不直接改工作流文件，补写需走 OpenSpec change。
- Follow-up [decision]: 后续每次 coder-fast COMPLETE 后调度 reviewer-go（push 前或 post-commit 补齐）；任何跳过需用户显式批准并在 `AGENT_PROJECT_MEMORY.md` + `docs/decision-log.md` 双记例外。
## 2026-09-05 V72P2D5-R1 plan revision PASS (plan-only, no code, no execution)

- Revision [repo-observed]: commit `836e151c` (`docs(v72p2d5-r1): revise GF32 rate-mother plan per review, no code no execution`), exactly 5 D5 plan files (`proposal.md`/`design.md`/`tasks.md`/`specs/spec.md`/`PLAN_FREEZE.md`); zero production `.py` modification; `REAL_EXECUTION_AUTHORIZED=false`, `DECODER_EXECUTED=false`, `VAL_LOADER_CALLS=0`, no `run_01`; Review PASS; `HEAD == origin`, ahead 0.
- Cap scope [decision]: `M_max=1000` is D5 synthetic cap only, not production sufficiency evidence.
- OQ2 verdicts [decision]: four-state `QUALIFIED / INCONCLUSIVE / CURRENT_CONFIGURATION_FAILED / BLOCKED`, replaces 90% death-line; `ROUTE_DEAD` deleted.
- Probability axis [decision]: `(Alice,Bob)` with `axis0` summation.
- Prefix gate [decision]: per-prefix 13-item structural gate + minimum 5-item PASS.
- M0 [decision]: two-stage natural prefix, non-hypothesis + deterministic row ordering without decoder.
- Seeds [decision]: frozen L1 `2026090501`, L2 `2026090502`, G0 `510..517`, G1 `600..699`, G2 `1000..1199`; search banned.
- Oracle [decision]: non-hard-gate, diagnostic-only `ORACLE_APP_NONMONOTONIC_DIAGNOSTIC`.
- Budget [decision]: P0 preflight n=64 2 blocks; G1 `<=900s`, G2 `<=3600s`, single call 120s, RSS `<2GiB`; calls G1 `APP100x2+oracle20x2`, G2 `APP200x3+oracle40x3`.
- Metric [decision]: `exact_failure_fraction`, not FER.
- Lifecycle [decision]: three-false, no single authorization across G0/G1/G2.
- Residual [repo-observed]: `M AGENT_PROJECT_MEMORY.md`, `M docs/decision-log.md` + untracked baseline uncommitted.
## 2026-09-05 V72P2D5 GF32 rate-mother PLAN_FREEZE (plan-only, no code, no execution)

- Freeze [repo-observed]: change `formal-ir-v72p2d5-gf32-rate-mother-plan`, commit `c3499522` (`docs(v72p2d5): freeze GF32 rate-mother plan, no code, no execution`), 5 files +540 lines (`proposal.md`/`design.md`/`tasks.md`/`specs/spec.md`/`PLAN_FREEZE.md` 111 lines); zero production `.py` modification; `REAL_EXECUTION_AUTHORIZED=false`, `DECODER_EXECUTED=false`, `VAL_LOADER_CALLS=0`, no `run_01`.
- Input [repo-observed]: `d=1024, U1/U2=[5,5], GF(32), N=1024`, model F, blocked outer-CV `CE_L1=3.814742 / CE_L2_oracle=3.347605 / CE_joint=7.162347` (worst `7.178766`, std `0.0158`, range `0.0423`), `lambda*=137.3823795883264` (D4R2 R2 audit); old `16/200/216` rows `MODEL_BUDGET_MISMATCH`, real use banned.
- Baseline [decision]: V31 QC-cyclic-projective `build_layer` (`nonbinary_v31.py:624`) is the sole selected baseline; per-layer single `M_max=1000` build + row-prefix disclosure `H[:k]` (reinterpretation, no constructor change); Lane-C (`construct_lane_c_prototype`) backup only; V36 (+32 rows, row-weight 10-14) and V35 (hardcoded 224) vetoed.
- Prior [decision]: `P1=sum_u2 P_F`, `P2=P_F/P1`; production `q@P` (`get_l1_app_prior_l2`), oracle-L2 (`get_conditional_posterior_l2`) diagnostic-only; sole adapter delta is frozen `lambda*` smoothing on `counts -> P_F`; floor dual-track audit `1e-300` / decoder `1e-15` with renormalization.
- Budget [repo-observed]: `rows=ceil(N*CE*f/5)`; n=1024 `f=1.0 782/686 tot1468`, `f=1.05 821/720`, `f=1.1 860/755`, `f=1.2 938/823`; old-216 gap `6254` bits / `1251` rows / `6.79x` (L1 need 3906 vs old 80; L2 need 3428 vs old 1000; total need 7334 vs old 1080).
- Gate [decision]: G0 tiny (marginal/conditional `<1e-12`, chain `<1e-10`, noiseless 100%) / G1 n=64 integration-trend (monotonic + oracle>=APP + zero crash, no kill) / G2 n=256 sole life-death (`f in {1.0,1.1,1.2}`, `m1={196,215,235}`, `m2={172,189,206}`, >=200 blocks; PASS = `f=1.2` end-to-end exact >=90% + monotonic + oracle>=APP; FAIL `<50%` route-dead / `50-90%` budget-insufficient both abandon n=1024 real).
- Lifecycle [decision]: `PLAN_CANDIDATE / EXECUTE_NOT_AUTHORIZED`; no apply before D5-T8 independent Plan Review ACCEPT (incl OQ1 per-layer `M_max` interpretation / OQ2 90% PASS line) + independent `EXECUTE_AUTH` for any decoder/VAL/n=1024 real run.

## 2026-09-04 V72P2D2-R1 orthogonal one-block BLOCKED RESOURCE_BLOCKED (descriptive-only, non-fresh, no promotion)

- Lifecycle [repo-observed]: base `e094f7e548380db4bfcbc1fe73472e670c32379a`, accepted-plan `4592bdad357a02f8f08a880ca0036beaed3ee900`, artifact `implementation_sha 580471cf` (R1 revision `a11cf239` in `cycle_state.yaml`) on `formal-ir-v72p1-addendum-clean`; single authorized R1 invocation consumed (`r1_execution_count_completed=1/1`); `r1_real_execution_authorized=false` after use, `scientific_promotion=false`, `no_run_01=true`; Pre-RESULT PASS; terminal `BLOCKED_RESOURCE_BLOCKED`, no rerun.
- Outcome [repo-observed]: `invocation_status=RESOURCE_BLOCKED`, `prep_status=PASS`, `fatal_error=timeout`; L `RESOURCE_BLOCKED` `timeout` 45 ckpts / 187 sweeps / 45 decoder calls, `final_checkpoint_rows=5792`, `final_syndrome_satisfied=false`, posthoc `final_oracle_exact=false`, disclosure 5792+44=5836 bits; I/P `NOT_ATTEMPTED`, 0 ckpts, 0 sweeps, 0 disclosure; A `LADDER_EXHAUSTED` `D1_REUSED` not rerun (carried 334 iters, 3100 bits / 620 syms); `normal_new_arm_count=0/3`; tag 0 `NOT_APPLICABLE` syndrome-only.
- Metering [repo-observed]: `prep_wall_s=7.765999999945052` (limit 600), `invocation_wall_s_before_report=610.25` (limit 2400), `peak_rss_bytes=277782528` (<2GiB); L `elapsed_s=602.484000000055` hit the per-arm 600s soft wall — resource stop, not a schedule/interleaver/prior verdict.
- Scope [decision]: single non-fresh VAL1726-1729 (session 20260123_1M_600k_0dB), mother 9036x10240 nnz49620, 72-pt ladder; DESCRIPTIVE_ONLY — no FER/SKR/information-limit/causal-graph/route/promotion; D2 `PREP_FAILED` root untouched; authorization consumed, no rerun.
- Evidence [repo-observed]: `comparison_bench/outputs_comparison/v72p2d2r1_orthogonal_oneblock_20260904/` exactly four files (manifest.json/results.json/table.csv/report.md) + `docs/research_cycles/V72P2D2-TRIAGE/RESULT_SUMMARY_R1.md` (`RESULT_SUMMARY.md` untouched) + `cycle_state.yaml`.

## 2026-09-04 V72P2D2 orthogonal one-block BLOCKED PREP_FAILED (descriptive-only, non-fresh, no promotion)

- Lifecycle [repo-observed]: base `e094f7e548380db4bfcbc1fe73472e670c32379a`, accepted-plan `4592bdad357a02f8f08a880ca0036beaed3ee900`, implementation `580471cf` on `formal-ir-v72p1-addendum-clean`; single authorized invocation consumed (`execution_count_completed=1/1`); `real_execution_authorized=false`, `scientific_promotion=false`, `result_created=true`; Pre-RESULT PASS; terminal `BLOCKED_PREP_FAILED`, `next_gate=BLOCKED_CLOSE_NO_RERUN`.
- Outcome [repo-observed]: `invocation_status=PREP_FAILED`, `prep_status=FAILED`, `fatal_error=NameError: name 'Q' is not defined`; L/I/P `NOT_ATTEMPTED`, 0 ckpts, 0 sweeps, 0 disclosure; A `LADDER_EXHAUSTED` `D1_REUSED` not rerun (carried 334 iters, 3100 bits / 620 syms); `normal_new_arm_count=0/3`; `no_run_01=true`; tag 0 `NOT_APPLICABLE` syndrome-only.
- Metering [repo-observed]: `prep_wall_s=0.43700000003445894` (limit 600), `invocation_wall_s_before_report=0.4529999999795109` (limit 2400), `peak_rss_bytes=174399488` (<2GiB); within budget, per-arm 600s wall not reached.
- Scope [decision]: single non-fresh VAL1726-1729 (session 20260123_1M_600k_0dB), mother 9036x10240 nnz49620, 72-pt ladder; DESCRIPTIVE_ONLY — no FER/SKR/information-limit/route/promotion; prep NameError is not a schedule/interleaver/prior verdict; authorization consumed, no rerun.
- Evidence [repo-observed]: `comparison_bench/outputs_comparison/v72p2d2_orthogonal_oneblock_20260904/` exactly four files (manifest.json/results.json/table.csv/report.md) + `docs/research_cycles/V72P2D2-TRIAGE/RESULT_SUMMARY.md` + `cycle_state.yaml`.

## 2026-09-04 V72P2D1 parity-layout diagnostic accepted close (descriptive-only, non-fresh, no promotion)

- Lifecycle [repo-observed]: base `ba0df2d3bea4147574e0b8224480f45c93505178`, implementation/accepted-plan `07744ccf3095eaa35b4c457005e268fb5ff52c41`, result `58656f59943b66f6319226d139e1fe67c41702a4` on `formal-ir-v72p1-addendum-clean` (`HEAD == origin` verified); single authorized invocation A-then-B serial, no rerun, no third layout, no other block; `CLOSED_ACCEPTED` / `RESULT_ACCEPTED`, pre-EXECUTE PASS + pre-RESULT PASS.
- Structure [repo-observed]: 9036x10240 nnz49620 both arms, deg2 9035 both arms, check-degree {4:1,5:4594,6:4441}; four-cycles 1196/1196, collisions 1194/1194, graph-isomorphic under degree-2 parity-column permutation (recomputed, not hand-filled); B col_map[1204:10239]=1204+permutation(9035), rng=default_rng(20260902), diagnostic-only seed.
- Baseline gate [repo-observed]: arm A reproduces V72P2 block0 — ckpt 72/72, iters 334/334, `LADDER_EXHAUSTED`, bit 3100/3100, sym 620/620, syndrome+tag+control 9036+64+71; lambda `221.22162910704503` exact-equal; CE `7.135005172802673` bitwise equal.
- Outcome [repo-observed]: A `LADDER_EXHAUSTED` 334 iters 118.97s / B `LADDER_EXHAUSTED` 321 iters 114.14s; invocation 240.17s (budget 1800s, 600s/arm, no overrun); 0 protocol-accepted, 0 verified-exact, 0 undetected (isolated, never merged); overall COMPLETED, fatal null.
- Metering [repo-observed]: per arm `leak_IR_bits=9100` (9036+64), `total_public_bits=9171` (+71 CONTINUE); `f_model_relative=1.2455097837734634`, `f_public_model_relative=1.2552274974710365` (denominator selected CAL-CV CE `7.135005172802673`, failed attempts included).
- Scope [decision]: single non-fresh block VAL1726-1729 (session 20260123_1M_600k_0dB, registry v71_data_registry.json schema v71_data_v1, data_sha 84d62779, CAL702..1725 shared prior); D1-D8 per-checkpoint wrapper scalars only (72 ckpts x 2 arms), no full prior/matrix/LLR/edge storage; DESCRIPTIVE_ONLY — no FER/SKR/information-limit/qualification/promotion; authorization consumed, no V73.
- Evidence [repo-observed]: `comparison_bench/outputs_comparison/v72p2d1_parity_layout_ab/` exactly four files (manifest.json/results.json/table.csv/report.md) + `docs/research_cycles/V72P2D1-PARITY/RESULT_SUMMARY.md` + `cycle_state.yaml`.

## 2026-09-03 V72P2-VAL descriptive real smoke completed (non-fresh, no promotion)

- Lifecycle [repo-observed]: exactly one authorized invocation used implementation/plan SHA `b33664d00b5b22a02b61df95b00c99ae0a0368b8`; all 9 assigned blocks were attempted with no rerun or tuning.
- Outcome [repo-observed]: 0/9 protocol-accepted, 0/9 undetected, 9/9 `LADDER_EXHAUSTED`, and no decoder/numeric errors; final candidates converged but syndrome/tag checks failed.
- Accounting [repo-observed]: total wall `1057.375s`, `3037` iterations; aggregate `leak_IR_bits=81900`, `total_public_bits=82539`; each block disclosed `9100/9171` IR/public bits.
- Prior denominator [repo-observed]: CAL-only selected CV `CE_ref_log2=7.135005172802673` at lambda `221.22162910704503`; all-attempt model-relative ratio `1.2455097837734632`.
- Claim boundary [decision]: this is descriptive reuse of non-fresh VAL, not FER, SKR, information-limit, algorithm-qualification, or promotion evidence; equal raw/final error counts do not establish bitwise identity.
- Historical timing [decision]: the V72P1 P1C one-iteration `1.046s` versus `<1s` failure remains explicit non-blocking evidence; do not claim the old timing suite passed.
- Evidence [repo-observed]: `comparison_bench/outputs_comparison/v72p2_val_descriptive_smoke_20260903/` and `docs/research_cycles/V72P2-VAL/REVIEW_VERDICT.md`.
- Authorization [decision]: V72P2 execution authorization is consumed; no successor execution or promotion is authorized.

## 2026-09-03 V72P1-ADP synthetic qualification accepted (synthetic-only, transcribed)

- Implementation SHA [repo-observed]: `ff88696f3c242cfb441dc9c82720e4fa6a371968` on `formal-ir-v72p1-addendum-clean` (`HEAD == origin` verified).
- Candidate [repo-observed]: `workspace/v72p1_baseline_check/20260903_h90q/` (v72p1_results.json/v72p1_manifest.json/v72p1_table.csv/v72p1_compact_report.md, seed 20260902, data_sha 84d62779, FrozenMotherSpec 9 / SoftJointConfig 8 / 11 arrays / CSR284248 / prefix1111 / checkpoint72).
- Solidified [repo-observed]: `comparison_bench/outputs_comparison/v72p1_synthetic_accepted_20260903_h90q/` (four files byte-identical, no rename, candidate preserved).
- Dual review [decision, transcribed]: `IMPLEMENTATION_REVIEW PASS` + `PRE_RESULT_REVIEW PASS` — user independent conclusion transcribed, covers only this implementation and candidate directory, synthetic qualification only (not re-reviewed this turn).
- Results [repo-observed]: P1A pack/prefix1111/checkpoint72/incremental/tag_ok deterministic pass; P1B tiny k2/3 n6/9 worst 1.998e-15 <1e-9 pass; P1C 9036x10240 1/3/10 all finite pass residual 4.2e-10 wall < thresholds; P1D n12k3 descriptive finite pass; overall true, five_state true, wall 53.125s peak 126.94MiB, llr_clip20.0 convergence_tol1e-6.
- Lifecycle [decision]: `accepted_plan_sha 73efd91f...` / `accepted_addendum_sha b0d55105...` unchanged; `implementation_sha ff88696f...`; `formal_execution_authorized false`; `scientific_promotion false`; real-data/formal decoder/run_01 not authorized, not verified. [repo-observed]

## 2026-08-28 V55 pre-EXECUTE / pre-RESULT 双重 review 门禁（强制）

- 根因 [repo-observed]: V55 连续复用 V54 模板常量 `efd34ef` 作为 `ACCEPTED_PLAN_SHA` 未替换，导致计划绑定错误。
- pre-EXECUTE review [decision, mandatory]: 每次正式 decoder 执行（`EXECUTE_AUTH` / 生产 `run_01`）前必须完成并记录：`HEAD == origin/<branch> == implementation SHA`、`ACCEPTED_PLAN_SHA` 重推导一致且 `rg <旧SHA>` 0 命中、目标 `run_01` 不存在、预算/门禁/`cycle_state` 与冻结 plan 一致、`py_compile` + 关键测试 PASS。FAIL 则阻塞执行，进入 `revise-required`/返工，新 SHA 重审。
- pre-RESULT review [decision, mandatory]: 每次输出 development result（`OPERATOR_RETURN.md` / `RESULT_SUMMARY.md` / `run_01` 固化/提交）前必须由独立线程或 reviewer 对照冻结 plan 复核阈值、泄漏公式分解、`undetected` 隔离（不得并入 success/FER）、per-source 分解、disclosure 等语义与实际产物。问题即返工，不得先产出后补 review；FAIL 阻塞固化，不得带病提交 `run_01`。
- 权威流程 [decision]: `AGENTS.md` §3 Mandatory Processes 与 §10.3、`docs/research-cycle-sop.md` §10 为长期流程；每次 execution/result 周期无例外适用。

## 2026-08-27 执行后分析口头通报规则（V42起）

- 触发条件 [decision]: 每次正式 execution 完成后必做，首个适用 scope 为 `v42_diagnostic_18_calls_exactly_once`，后续所有同类正式 run 均适用。
- 分析维度 [decision]: 覆盖有效性门禁（J6等）、总体/分源门禁、成对增量、迭代/残留误码行为、终态归属。
- 输出边界 [decision]: 分析结果仅通过消息口头告知用户，不得自动写入 `run_summary`、`decision-log` 或其他产出文档/制品，除非用户显式要求写入。
- 衔接约束 [decision]: 口头分析本身不改变生命周期；生命周期继续按 execution、result-candidate 和独立结果评审流程推进，不增加任何额外输出文件。

## 2026-08-25 V38R1 accepted development result: bounded machine candidate

- Current result [repo-observed]: exactly-once authorized `run_02` completed in
  result-candidate commit `2416486f724f4fb7cbf1058d9dc1bb1fc5ded5ed`; main
  acceptance commit is `c8c5cd2ed5b60665af58e6a1639e58f99726bc05`. The machine
  terminal is `V38_MULTIPLE_ROUTE_SIGNALS`; this is not a scientific,
  formal-execution, promotion, or automatic-V39 decision.
- Frozen execution [repo-observed]: 45 calls over the fixed 15-block-per-lane
  set, with no rerun, tuning, seed change, or automatic V39 follow-up.
  Lane A was 0/15 exact with median residual 115 and 15/15 improved; Lane B
  was 9/15 exact with median residual 0; Lane C was 14/15 exact with median
  residual 0, with its only non-exact block at 1p5M/360202 (residual 63).
  One Lane B block had `syndrome_ok` without exact recovery; success remains
  defined by `exact_l2`, not syndrome status alone.
- Claim boundary [decision]: blocks are V25 TRAIN empirical-count samples
  with oracle-L1 inputs, not real-frame FER evidence. Do not infer threshold,
  SKR, formal-execution, qualification, or promotion results. The current
  result supersedes the pre-execution boundary in the implementation-only
  entry below; further reruns/tuning and automatic V39 are prohibited.

## 2026-08-25 V38P0 invalidation and V38R1 implementation acceptance

- Root-cause invalidation [repo-observed, decision]: V38P0 `run_01` passed
  `u2_bob` instead of complete `bob` to `get_conditional_posterior_l2`.
  Therefore the 45-record decoder evidence and `V38_NO_ROUTE_SIGNAL` are
  invalid; the terminal state is `V38_DIRECTION_EVIDENCE_INVALID`.
- Bounded structural evidence [decision]: the 27/27 structural records remain
  retained, but they do not support lane-performance claims, a `d_v >= 3`
  conclusion, or a claim that cycle optimization is ineffective.
- V38R1 implementation [repo-observed]: corrected implementation candidate
  `8f7bc7d8d7366772ff425528cd1080fa67ef7509`; independent implementation
  acceptance commit `65301365517af5718fce382cc8c9e40dd371ad65`. This is an
  accepted implementation boundary, not a scientific result, qualification,
  promotion, or decoder-performance claim.
- Execution boundary [decision]: V38R1 `run_02` is absent, unauthorized, and
  unexecuted. Any future decoder run requires a new explicit user
  `EXECUTE_AUTH` bound to the accepted implementation SHA. Do not record
  V38R1 as scientific evidence until that separately authorized execution and
  review occur.

## 2026-08-25 V37R1 P1 empirical-P DE screening: bounded negative result (`P1_NO_FINITE_FEASIBLE_DE_ADVANCE`)

- Direct evidence [repo-observed]: 2,349 real empirical-P GF(32) DE screening
  runs across 261 configurations (259 finite-feasible candidates with $N_2 \le 183,
  d_{c,\max} \le 20$ + matched regular $d_v=2$ baseline + V36 positive control)
  $\times$ 3 sources (1M, 1.5M, 2M) $\times$ 3 seeds completed in 3262.8s.
  - Baseline $d_v=2$: 1M $\text{AUT}_{30}=73.61$, 1.5M=59.38, 2M=59.45 (mean 64.15).
  - Best finite candidate (`lam_d2_0.10_d3_0.90`): 1M=153.997 (+109.2%), 1.5M=154.117
    (+159.6%), 2M=154.091 (+159.2%), mean 154.07, `all_seeds_converged=False`.
  - V36 positive control ($\lambda=\{2: 0.85, 4: 0.15\}$): mean 81.59 (+8.7% to +42.4%).
  - Passing screening candidates: 0 / 259 (P1-B confirmation skipped conditionally).
  - Terminal state: `P1_NO_FINITE_FEASIBLE_DE_ADVANCE`.
- Scientific diagnosis [decision]: the gap (+109% to +160% higher $\text{AUT}_{30}$
  vs -5% target) is structural, not a grid step resolution issue. High code rate
  ($R \approx 0.8125 - 0.8203$) and finite-length cycle-free forest gate ($N_2 \le 183$)
  force $\bar{d}_v \ge 2.857$ and $d_c \in [16, 20]$. In GF(32), check degrees $\ge 16$
  exponentially inflate message convolution uncertainty, stalling early iteration
  mutual information propagation. The optimizer saturates at the lowest-degree
  boundary ($\lambda_2=0.10, \lambda_3=0.90$).
- Architectural roadmap [decision]:
  - Abandon unstructured single-edge irregular $\lambda$-distribution simplex tuning.
  - Pivot to structured low-degree NB-LDPC for V38+:
    1. Protograph / Multi-Edge-Type (MET) NB-LDPC (controlled degree-2 chains without random cycle explosion).
    2. Near-$d_v=2$ low-degree graph topology + GF(32) edge label / coefficient optimization.
    3. Non-binary Spatially-Coupled LDPC (SC-NB-LDPC) fallback.

## 2026-08-24 GitHub-centered ChatGPT/OpenCode research-cycle SOP

- Workflow [decision]: GitHub is the durable exchange surface. ChatGPT handles
  planning/read-only scientific review; OpenCode implements a frozen packet;
  the user/main reviewer owns acceptance and formal execution authorization.
- Handoffs [decision]: every prompt/return binds repository, branch/PR, full
  target SHA, cycle ID, entrypoint, lifecycle state, and allowed action. Agent
  text becomes durable only after it is copied into a cycle file and committed.
- Data/Git [decision]: each milestone includes compact machine-readable data or
  a result summary with provenance, seeds, commands, metrics, omissions, claim
  limits, and reproduction/retrieval instructions. Normal non-force pushes
  only; incompatible Polar/crosstalk history goes to a separate formal-IR
  branch rather than being merged or overwritten.
- Authority: `docs/research-cycle-sop.md`; prompts under `docs/prompts/`.

## 2026-08-24 V36 post-run scientific review correction

- Retained observation [repo-observed]: 15 paired development blocks gave
  baseline/candidate mean residual 174.80/157.07; 10/15 improved; exact 0/15.
- Gate [decision]: `NO_FINITE_GRAPH_ADVANCE` remains correct, but the route to
  A3 was not protocol compliant. A1 did not implement the frozen per-source
  >=10% same-setting DE confirmation; A2 realized 2288--3002 4-cycles and
  degree-2 cycle ranks 779--801 despite a zero-cycle requirement.
- Claim boundary [decision]: status is
  `POSITIVE_EXPLORATORY_RESIDUAL_SIGNAL / A1_DE_SELECTION_NOT_ACCEPTED /
  A2_STRUCTURAL_GATE_FAILED / NO_FINITE_GRAPH_ADVANCE`. No empirical-P DE
  superiority, trapping-set causality, general FER, or MET-necessity claim.

## 2026-08-24 V35R1 corrected bounded status

- `run_01` is invalid and superseded; `run_02` provides corrected A1--A3
  development evidence with 25 focused tests passing.
- All tested NB configurations had 0/15 exact recovery and the hand-designed
  mixed-degree graph worsened residuals. This supports only
  `NO_NB_CANDIDATE_FOR_TESTED_HAND_DESIGNED_CONFIGURATION`.
- The original OpenSpec required conditional A4 after A3 failure, but A4 was
  not executed in `run_02`. Durable status therefore also includes
  `PROTOCOL_PARTIAL_A4_NOT_EXECUTED`; do not claim the original full
  four-stage `NO_CANDIDATE_SUCCESS` terminal or a binary-MLC result.

## 2026-08-24 Strict first principle: high-performance correction algorithms

- User directive [decision]: the project's strict first principle is to find,
  implement, and experimentally validate scientifically reasonable
  high-performance IR/error-correction algorithms for the actual HD-QKD data.
- Priority measures [decision]: correction success/FER, leakage/reconciliation
  efficiency, throughput/runtime, memory/resource cost, and accepted-frame net
  secret-key yield.
- Engineering boundary [decision]: package maturity, general frameworks,
  defensive hardening, exhaustive audit, and verifier sophistication are
  secondary. They block algorithm work only for a concrete risk of wrong
  science/numerics, irreproducibility, unauthorized expensive execution, or
  destructive overwrite; otherwise mark non-blocking/deferred.
- Workflow consequence [decision]: use the shortest scientifically valid path
  from method hypothesis to implementation to performance measurement. Do not
  expand ordinary algorithm work into adversarial-verifier engineering.

## 2026-08-24 V34 matched empirical-P finite control: bounded FAIL / ER1 ACCEPT

- Lifecycle [repo-observed]: accepted accounting-corrected HEAD `c8cc1fbe`;
  user auth `user-v34-execute-auth-20260824-01`; one official 60-block execute;
  strict absolute-path verify consistent; independent ER1 ACCEPT; no run_02.
- Result [repo-observed]: 0/20 successes for each of 1M/1p5M/2M, no fatal or
  false accept. Mean GF(32) L2 errors changed 249.25->168.45,
  261.35->181.10, and 256.90->174.05; runtime means 10.1936/10.0084/9.9852 s.
  Status split is 37 converged-no-syndrome and 23 max-iter.
- Scientific boundary [decision]: direct empirical-P matching removed V32 B1's
  confounder but did not rescue this fixed V31 QC packet/V28R decoder at oracle
  L1 and max_iter=30. This is not NB-LDPC, FER, key-rate, qualification, or
  promotion evidence.
- Performance-first consequence [decision]: do not rerun/tune V34. Reuse its
  residuals for graph-structure diagnosis, then prioritize one empirical-P
  protograph/MET candidate and one rate-adaptive/incremental-syndrome mother
  code. Administrative archival must not delay algorithm work.
- Durable closeout: `docs/v34-formal-execution-er1-closeout-20260824.md`.

## 2026-08-24 V34 matched empirical-P finite control: P3 implementation candidate

- Current state [repo-observed]: V34 OpenSpec passed initial FR1 rejection,
  revised FR1 ACCEPT, independent science-amendment ACCEPT, and Codex main
  `ACCEPT_FREEZE`. Freeze baseline is `f5f61eb672afe8e399727fa5d7507ca9f2f9151a`;
  lifecycle freeze commit is `0c817a322d1d1674f65708563afe3b77c47ae961`.
- Scientific identity [decision]: change only the channel-law generator from
  V32's raw-SER uniform substitution to direct source-specific V25 train
  empirical P(A,B). Fresh seeds are nuisance randomization, not a paired trial.
  Keep V31 packet, V32 oracle-L1/V28R decoder, max_iter=30, 20 blocks/source,
  and source >=19/20 mechanical discriminator fixed.
- Reproducibility [decision]: NumPy exactly 2.4.0 and literal
  `V34-PCG64-REF1`; frozen 60-call digest
  `d30335b4d0d74df3e7729e01b02ae1ae73e43035652c59e81f871a5545fe73bb`.
- P3 evidence [repo-observed]: one CLI plus one focused test; compile,
  selfcheck and read-only real-input prepare PASS; focused fake suite
  `13 passed in 10.16s` under `workspace/v34_p3_main_20260824_01`; official
  V34 `run_01` absent. No real decoder or DE ran.
- Lifecycle boundary [decision]: current state is
  `IMPLEMENTATION_CANDIDATE / EXECUTE_NOT_AUTHORIZED`, not IR1 ACCEPT. Next is
  the Ox Alpha P4 evidence packet followed by independent Codex IR1. V34
  production execution still requires a new explicit user EXECUTE_AUTH bound
  to the accepted implementation HEAD and frozen matrix.
- Durable handoff:
  `docs/v34-p3-implementation-candidate-and-ox-alpha-handoff-20260824.md`.

## 2026-08-24 V33 exact-rate empirical-P ensemble DE: PASS / ER1 ACCEPT

- Current state [repo-observed, independently reviewed]: user-authorized V33
  official `run_01` executed exactly once on HEAD `41d31151`; 30/30 calls and
  all six source×layer cells PASS 5/5. Strict verify returned consistent with
  no problems; independent Luna ER1 ACCEPTED. State is
  `ARCHIVED / SUCCESSOR_NOT_AUTHORIZED`; archived under
  `openspec/changes/archive/2026-08-24-formal-nonbinary-ldpc-v33-rate-aligned-empirical-channel-de-diagnostic/`.
- Scientific boundary [decision]: this proves convergence only for the frozen
  V25 train-only empirical-P, F03/A02, V31 exact-rate ensemble MC-DE. It does
  not prove a fixed QC graph, decoder, FER, finite code, net key rate,
  qualification, or promotion. L1 converged in 23–25 iterations and L2 in
  37–44; the persisted numerical entropy floor is not zero FER.
- Performance-first sequence [decision]: V33 PASS permits a new proposal for
  exactly one corrected matched empirical-P finite-control using the same V31
  QC packet/decoder, oracle L1, 20 blocks/source, fresh frozen seeds, and no
  tuning/rerun. It does not authorize implementation or execution.
- Literature increment [decision]: a 2024--2026 search did not change
  V33-first. Post-V33 structural candidates now explicitly include informed
  NB-MLC/JRDO, Block-MDS/QC, and a short-block rate-adaptive mother code; see
  `docs/hd-qkd-ir-performance-roadmap-20260824.md` §10.
- Research-code boundary [decision]: engineering checks are justified only
  when they prevent a wrong operating point, invalid scientific attribution,
  or irreproducible execution. Mature-package infrastructure is not a goal.
  Current roadmap: `docs/hd-qkd-ir-performance-roadmap-20260824.md`.
- This entry supersedes older statements below that V33 is
  `DRAFT_PENDING_FREEZE_REVIEW` or `EXECUTE_NOT_AUTHORIZED`; those remain
  historical snapshots.

## 2026-08-23 B1 NLL unit correction + long-term roadmap review (R1–R4) + audit-correction archived

- Unit correction [repo-observed]: Ground 2 of
  `docs/nbldpc-v32-main-review-verdict-20260822.md` misstated units — B1 raw
  posterior NLL mean is ≈229–245 bits per n=1024 block (≈0.224–0.239
  bits/symbol), NOT bits/symbol; reference conditional entropies are ≈0.80–0.83
  bits/symbol. Additive correction recorded at
  `docs/nbldpc-v32-main-verdict-unit-correction-20260823.md`; the original
  verdict file is preserved byte-identical on purpose. Future citations must
  use the corrected unit phrasing.
- Long-term roadmap review finalized [decision]:
  `docs/hd-qkd-ir-roadmap-review-20260823.md` (supersedes the same-day
  conversation-only version). Fixes route naming R1 matched empirical-P /
  R2 allocation-factorization / R3 binary-MLC & NB-Polar / R4 HD-Cascade
  reference, avoiding collision with historical Route A–D names.
- Roadmap priority convention [decision]: V33 exact-V31-rate empirical-P
  ensemble DE is the mandatory highest-value prerequisite gate; corrected
  matched finite-control becomes the next high-value experiment only after
  V33 passes.
- Law A wording [decision]: nominal feasibility only means NB-Polar's immediate
  information-theoretic veto is untriggered; it does not show NB-Polar
  feasible; the two-layer D2 results must not be cited as R3 support.
- Audit-correction change archived [result]: after verifier fix `3110cb0e`,
  F-G1 = ACCEPT; Change A12 terminal `audit_corrected_rate_aligned_de_required`;
  archived under `openspec/changes/archive/
  2026-08-23-formal-nonbinary-ldpc-v32-operating-point-audit-correction/`
  (closeout commits d76a55c3 + b1171cc9; HEAD b1171cc9). Supersedes the interim
  stop-point status quoted inside the two 2026-08-23 docs. V32 scientific
  attribution remains inconclusive (`bridge_inconclusive`, main-review layer);
  no qualification/promotion; V33 draft still DRAFT_PENDING_FREEZE_REVIEW.

## 2026-08-23 S4 research-doc closeout: B1 NLL unit convention + route registry R1–R4

- Unit convention [decision, authoritative citation]: B1 posterior NLL must be
  stated as "raw posterior NLL mean ≈229–245 bits per n=1024 block
  (≈0.224–0.239 bits/symbol)"; the form "229–245 bits/symbol" is banned.
  Reference entropies are per-symbol: ≈0.80–0.83 bits/symbol. Authoritative
  note: `docs/nbldpc-v32-main-verdict-unit-correction-20260823.md` (original
  verdict file preserved byte-identical).
- Route registry [decision]: future roadmap citations use R1 = matched
  empirical-P NB-LDPC; R2 = allocation/factorization redesign; R3 =
  binary-MLC / NB-Polar P0; R4 = HD-Cascade reference. Historical repo
  "Route A/B/C/D" names stay reserved for their older meanings.
- Sequencing [decision]: V33 exact-V31-rate empirical-P ensemble DE is the
  mandatory prerequisite; corrected matched finite-control is authorized only
  after V33 full PASS. V33 four-piece OpenSpec candidate exists as
  DRAFT_PENDING_FREEZE_REVIEW (untracked); DE execution still requires freeze +
  explicit authorization.
- Scope guard [decision]: Law A (empirical-P nominal budget feasible) supports
  no feasibility claim for NB-Polar or any finite scheme; it only records that
  the immediate information-theoretic veto has not triggered.
- Accepted docs [repo-observed]: `docs/nbldpc-v32-main-verdict-unit-correction-
  20260823.md` and `docs/hd-qkd-ir-roadmap-review-20260823.md` (v2, R1–R4
  renaming + F-G1 ACCEPT state), committed in the S4 closeout commit.

## 2026-08-23 V32 finite-DE bridge + operating-point audit correction: ACCEPTED closeout

- Observed [repo-observed, R2-verified]: V32 bridge raw record valid (B0 6/6;
  B1–B4 0/60 each; B5 import ok; exact-once, no resume, 10047 s). Correction
  v2 evidence (`.../nbldpc_v32_operating_point_audit_v2/run_01/`, eight files):
  q_mass_on_p_zero_cells = 0.2394680/0.2541265/0.2553477 (1M/1p5M/2M);
  full_expected_nll = "infinity" ×3; conditional_finite_support_mean =
  0.397–0.431 bits/symbol; truncated_common_support_cross_entropy =
  7.77–7.91 bits. D0: B1 divergence observation; B2 l2_errors_final=1024 is a
  not_run sentinel; B3/B4 improve-but-no-syndrome (~250→~179). Dual law:
  empirical P nominal budget feasible only (pure gaps +180–187 bits); original
  Q_B1 information-theoretically infeasible (required ≈3269–3458 bits vs pure
  syndrome 1000–1040 bits).
- Rejected interpretation [decision]: B1 divergence does NOT prove fixed QC
  graph / message-passing / V28R decoder failure — B1's generator law Q_B1 was
  not matched to the V25 empirical posterior (positive mass on P-zero cells ⇒
  full expected NLL infinite). The persisted bridge terminal
  `finite_graph_decoder_mismatch` and the first operating-point audit
  (`post_hoc_exploratory_only` lifecycle) are superseded for all attribution
  claims; neither may be cited as an accepted root cause.
- Next authorized boundary [decision]: the only next question is exact-V31-rate
  empirical-P ensemble DE convergence (L1 0.984375 ×3; L2
  0.8203125/0.814453125/0.8125) under F03/A02 — candidate change
  `formal-nonbinary-ldpc-v33-rate-aligned-empirical-channel-de-diagnostic`
  exists as DRAFT_PENDING_FREEZE_REVIEW only; DE execution requires a frozen
  OpenSpec plus explicit authorization. Fixed-graph/decoder/NB-Polar successor
  selection undecided. No qualification/promotion; correction commit chain
  59ba0236 → 0765d893 → 29a5dafe → 3110cb0e (verifier semantic guards ACCEPT).

## 2026-08-21 V31 closeout: `finite_graph_fail`

- V31 deterministic finite-graph redesign gate executed and archived
  (user goal authorization 2026-08-20). No V30R packet rerun.
- Fixed F03 GF32+GF32, V25 source-conditioned channel, m1=16, n=1024/2048.
- M1: 60/60 DE confirmation PASS (30/30 per n).
- M2: `PEG-capacity-aware` rejected both n (L2 GF32 rank-deficient,
  deterministic); `QC-cyclic-projective` constructed OK both n (occupancy<=31,
  full rank, projective-safe).
- M3: n=1024 full window 300/300 exact/tag=0 (`converged_no_syndrome` L2),
  exact/tag FER=1.0; n=2048 bounded 1M prefix (14 blocks) same failure.
- Terminal `finite_graph_fail`; read-only verifier `ok=true`, problems=[].
- Evidence: `comparison_bench/outputs_comparison/nonbinary_diagnostics/
  nbldpc_v31_20260820/run_01/`
- Report: `docs/nbldpc-v31-deterministic-finite-graph-redesign-report-20260820.md`
- OpenSpec archived. No push; no random search; no seed tuning; no
  qualification/promotion.

## 2026-08-21 V31 closeout correction — authoritative state (Change A, run_02 authoritative)

- Change A state: `closeout_corrected`; C01-C16 ACCEPT after A9R (C09 limitation persisted); C17-C18 pending until commit. [decision]
- Authoritative evidence: `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v31_closeout_audit_v2/run_02/` (closeout_verify/recount/gate/run_manifest); superseded `run_01` retained with empty limitation. [repo-observed]
- V31: `ARCHIVED_PARTIAL`; n=1024 300/300 `finite_graph_fail` valid (0 exact/tag, syndrome 0, L1_ok 296 L2_ok 0, runtime 13015s); n=2048 14 blocks from 1M only; original both-n execution incomplete, global PASS impossible, bounded-prefix contingency post hoc. [repo-observed]
- PEG replay limitation (persisted in run_02): "The canonical V31 manifest does not retain independently reconstructable rejected PEG packets..." — does not alter QC/neg result. [decision]
- No V31 rerun, no n=2048 completion. [decision]
- Successor: only after Change A archive, V32 finite-DE bridge diagnostic is next (not yet started); qualification/promotion still not authorized. [decision]
- HEAD `c8d2acab`, field_id `c3a3660aa3cfbf788568cf366ee5de345ddc6be0372154a702c9e244a53bc6cf`, m1=16. [repo-observed]

## 2026-08-20 V30R closeout: `finite_graph_fail`

- V29 is closed with `v29_finite_gate_fail`; V28R's duplicate projective keys
  and guaranteed weight-2 pairs are a finite matrix-construction defect, not a
  GF32xGF32 route impossibility.
- Original V30 `P102_ACCEPTED` is superseded by the V30R document revision.
  Independent P103 freeze review was ACCEPTED on 2026-08-20. Canonical
  `run_01` implementation/execution and independent read-only verification are
  complete; verifier `ok=true`, `problems=[]`, terminal
  `finite_graph_fail`.
- V30R freezes at most one balanced-projective and one
  `PEG-projective-cycle-cancelled` packet per selected allocation, at most two
  allocations/four packets globally; M1 failed allocations still complete all
  12 registered calls; M3 screen is blocks `0..19`, only top-ranked eligible
  matrix confirmation is blocks `20..69`, and its failure is global with no
  fallback.
- Bounded cycle rule: duplicate projective key/proportional column is the
  4-cycle FRC hard failure and must be zero; labels minimize exact newly closed
  Tanner-6 degenerate count by `(degenerate_6_new, ratio_index)`; Tanner-8 is
  topology/girth aggregate only; standard variable-side ACE is not used for
  `d_v=2`. Evidence is aggregate plus deterministic replay, without cycle
  catalogs or candidate rejection lists.

- Canonical result: M0 reproduced `15/69/303/922/1107`; M1 persisted 72 screen
  and 60 confirmation calls, with `m1_9,m1_12` selected and both 30/30; M2
  retained valid balanced packets for `m1=9,12` and rejected both PEG packets
  because support `(0,1)` had no projectively unique ratio. M3 stopped after
  blocks `0..5` on source 1M for both valid packets (`0/6` exact, `0` false
  accepts), so terminal `finite_graph_fail` occurred before other sources and
  confirmation. M1/M3 meters were 74.828s/719.876s.
- Scientific boundary: this closes only the tested `n=1024` F03 fixed
  allocation/family finite conversion with the V28 decoder. It does not close
  the V25 empirical channel, V26 DE, or all NBLDPC. No qualification,
  promotion, same-packet rerun, tuning, or push is authorized.
- Report:
  `docs/nbldpc-v30r-projective-safe-finite-graph-report-20260820.md`.

- V30R frozen input binding: V25
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/data_inventory.json`
  and
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`;
  V26 canonical `.../nbldpc_v26_20260818/run_02/` (manifest/M0/verify);
  V28R canonical `.../nbldpc_v28_gf32_finite_code/run_02_v28r/`
  (config/evidence/manifest/verify). Source IDs and
  delay mapping are `type2_1M_20260121_184040/-50 ps/1M`,
  `type2_1p5M_20260121_183806/+50 ps/1p5M`,
  `type2_2M_20260121_183657/+50 ps/2M`; pair paths are the matching
  `v13r3fresh_pairs_20260816/<source_id>/pairs.parquet` entries. Field binding:
  `GF2mField.create(32)`, `0b100101`, field_id
  `c3a3660aa3cfbf788568cf366ee5de345ddc6be0372154a702c9e244a53bc6cf`, and
  zero-based `ratio_index`.

## 2026-08-20 V27 finite-leakage-margin gate: PASS (pass_finite_budget_ready, block_len=1024)

- V27 gate executed once on additive run root `comparison_bench/outputs_comparison/
  nonbinary_diagnostics/nbldpc_v27r_finite_leakage_margin/run_01/` (322.9s wallclock). Terminal
  `pass_finite_budget_ready`, passing_block_len=1024; all four block_lens confirmed all three
  sources at the m1_ep offset-0 candidate. [result]
- Independent candidate-delivery review (P-CDR, in-conversation) ACCEPT after fixing critical
  dedup bug: `candidates[(bl,src)]=cand` collapsed 5 candidates/source to 1; fixed to 3-tuple
  key `(block_len, source, m1)`. Read-only verifier ok=true (recomputed terminal == persisted).
  11 T0/T1 tests pass. [result]
- `pass_finite_budget_ready` authorizes Phase C (V28 GF32xGF32 finite-code engineering) and
  Phase D (V29 retrospective finite-code gate); stop before fresh qualification. No push.
  [consequence]

## 2026-08-20 V28 GF32xGF32 finite-code engineering: COMPLETE + acceptance ACCEPT

- V28 implemented (`nonbinary_v28.py`) + 11 T0/T1 tests pass + additive run_01 (1.40s) +
  `verify_v28` ok=true + main-thread acceptance ACCEPT. Terminal
  `engineering_ready_for_retrospective_gate`. [result]
- Reuse: `GF2mField.create(32)`, `nonbinary_codebook` three-shift-cyclic GF(32) mother matrices
  + `gf_rank`, `nonbinary_v10_fftqspa.decode_error_domain` (Bob-only GF(32) FFT-QSPA). [result]
- Matrices: H_mother_L1 6x1024, H_mother_L2 202x1024; per-source L2 = public row prefix
  H_mother_L2[:m2]; gf_rank full (identity parity half). Noiseless decode recovers x exactly
  (both layers, 3 sources). [result]
- Honest limit: V27 split is sparse high-rate; uniform-QSC iterative correction limited
  (decoder fail-closed, converged_no_syndrome). V29 measures real FER on frozen V25 holdout.
  [finding]
- Leakage = m_total*5+64; f<1.3 for all 3 sources; 64-bit tag = SHA-256(x1_hat||x2_hat)[:8B. [result]

## 2026-08-19 V27R OpenSpec revision: source-adaptive finite-leakage-margin (ACCEPTED + Phase B executed)

- V27 OpenSpec revised from worst-source to SOURCE-ADAPTIVE budget: each source
  (1M/1p5M/2M) uses its own full-precision H1/H2; m_total=floor((1.3*block_len*H_source-64)/5).
- Frozen table (block_len 1024/2048/4096/8192 -> m_total): 1M 200/413/840/1693;
  1p5M 206/426/866/1745; 2M 208/430/873/1760. m1_ep=round(m_total*H1/H_total) (Python
  round, round-half-to-even, frozen explicit rule); candidates m1_ep+offset, offset in
  {-2,-1,0,+1,+2}, all five eligible; m2=m_total-m1. Realized f=(5*m_total+64)/n/H_total
  all <1.3 (1.29409-1.29974). All arithmetic re-verified this session. [decision]
- V27 is asymptotic true-predecessor-conditioned multistage DE (L2 conditioned on correct
  L1; no finite-code error propagation); single 64-bit tag only in total block leakage,
  not between layers. source/delay = public acquisition selector (posterior + syndrome
  budget), not per-symbol side info, no repeated billing. block_len and mc_samples are
  two distinct fields. [decision]
- Ordering keys per (block_len,source) ascending: worst_final_entropy, mean_final_entropy,
  abs(offset), m1. Screen fully executes, then confirmation in rank order; next candidate
  on failure until pass or all five fail. pass = same block_len with all three sources
  confirmed; multiple -> min block_len. [decision]
- Terminal states ONLY: pass_finite_budget_ready / de_pass_no_finite_headroom /
  implementation_blocked / resource_blocked (old fixed_ensemble_margin_fail removed).
  24h global completed-call cumulative resource gate; checkpoint bound to full frozen
  config; V26 archived reference only (no rerun). [decision]
- V27R docs written to openspec/changes/formal-nonbinary-ldpc-v27-finite-leakage-margin-de-gate/
  (proposal/design/tasks/spec). Old worst-source drafts backed up in tmp_v27r/old_*.md.
- BLOCKER (review gate): independent Luna freeze review could NOT be delivered this session
  - subagent infrastructure failed repeatedly (subagent foreground/background + muse_spark
  all failed; background agents stayed "ready" with no result). P102 ACCEPT NOT recorded;
  Phase B NOT started, per strict gate. Freeze review must complete (Luna) before V27
  implementation/execution. [blocker]

## 2026-08-19 V26 channel-informed DE gate complete: pass_target_f13 + V26R closeout

- V26 result: A02 (F03 GF32+GF32) converges f=1.3 on all 2 layer x 3 source x 5 confirm
  seeds (30/30, final mean entropy 0.00000); A01 (F01 GF512+GF2) f=1.3 fails on the GF2
  residual layer, passes at f=1.6; terminal pass_target_f13. [repo-observed]
- Read-only verifier verify_run independently recomputes 72 screen + 60 confirmation +
  A02@f=1.3 30/30 + rate/rho/seed/entropy/terminal from channel_counts.npz; run_01 and
  run_02 both 0 mismatch ok=true; persisted readonly_verify.json per run. [repo-observed]
- Correct formulas: f_i=leak_i/H_i, leak_i=(1-R_i)log2(q_i)=m_i log2(q_i)/n,
  R_i=1-f_i H_i/log2(q_i); NOT f=R/H and NOT R=f*H (would mix bit/symbol with normalized
  leakage). Applied in proposal/design/spec/report/code and V27 planning. [decision]
- V26 Run roles: run_02 canonical, run_01 deterministic_repeat (RUN_MANIFEST.json +
  README at nbldpc_v26_20260818/). [decision]
- 24h completed-call resource gate implemented as RESOURCE_LIMIT_SECONDS in
  run_screen/run_confirmation (_run_gated_stage) -> resource_blocked terminal; V26 not
  triggered (screen~44s + confirm~112s). [repo-observed]
- Explicit source<->delay metadata: SOURCE_METADATA in nonbinary_v26_channel.py
  (1M/1p5M/2M -> delay_used_ps -50/+50/+50, n_pairs 512000/708352/933120); exposed on
  ChannelAdapter and recorded in M0 detail + RUN_MANIFEST. [repo-observed]
- M1 reference fixes: adapter_input_entropy_matches_iter0 now runs the real MC-DE first
  round (record_channel_entropy read-only flag on run_mcde_posterior; default off so
  screen/confirm numerics unchanged); gf2_bsc_reference now clearly decides pass/fail
  (noiseless must converge; feasible-rate ~0.427 must converge; at-capacity ~0.714 must
  fail) instead of "both non-converge = agree". [repo-observed]
- V26 closes with an archived OpenSpec change (local commit, no push). Pass_target_f13 only
  authorizes proposing A02 finite-code/construction change; still no FER/MET/qual/promo. [decision]
- V27 = NEW OpenSpec change (finite-leakage-margin DE gate), four parts written, returned to
  main-thread freeze review; NOT executed in this work. [pending]
---

## 2026-08-18 V25 M0-M4 complete (pass_ready_for_de_change)

- V25 P102 ACCEPT (main-thread): +-1 adjacent-bin errors with source/delay_used_ps
  direction = source/delay-conditioned channel (not alignment blocker). [decision]
- V25 engineering+science done: F01-F05 MSB->LSB factorization x {natural,Gray},
  N_ab/P(A|B) direction, chain-rule M3, C01-C06 M1, M0/M2 diagnostics, M4.
  [repo-observed]
- Empirical channel: H(A|B)~0.80 bits; holdout NLL of empirical delta models
  0.81-0.83 vs QSC 3.2 / V17 product 3.3-3.5; direction stable over time and
  flips with delay sign (-50->+1, +50->-1). [repo-observed]
- M4: high-field F01(GF512)+GF2, mid-field F03(GF32)+GF32 for V26; status
  pass_ready_for_de_change. Chain-rule closed (err<=5e-9). [repo-observed]
- Evidence: nbldpc_v25_20260818/run_04/ (12 files, verifier ok=true). [repo-observed]
- Successor: V26 channel-informed DE is a NEW change requiring user auth; V25
  PASS only proposes V26, never auto-starts. No finite/FER/MET/qualification/
  public-residual/oracle; no push. [decision]
---

## 2026-08-18 V25 立项（文档 + OpenSpec 草稿）

- 用户交付 V25 冻结任务包并指示“更新至文档”；已落盘
  `docs/nbldpc-v25-empirical-channel-and-factorization-plan-20260818.md`。 [decision]
- V25 OpenSpec change 已建（DRAFT_PENDING_P0_AUDIT_AND_FREEZE_REVIEW）：
  `openspec/changes/formal-nonbinary-ldpc-v25-empirical-timestamp-channel-and-multilevel-factorization-gate/`
  （proposal/design/tasks/spec）。 [repo-observed]
- V25 冻结科学边界：V24 只排除 V17 聚合信道/GF(1024)/bounded single-edge；不排除
  GF(512)/GF(256)/multilevel/source-conditioned/MET/重校准 delay。 [decision]
- V25 主模型 P(A|B,Z)；编码分层（保持 1024-bin）≠ 物理 bin 合并（对照）；
  候选 F01–F05 × L01 natural/L02 Gray；chain rule 闭合；M4 仅
  pass_ready_for_de_change / fail_no_stable_factorization /
  blocked_insufficient_joint_data / blocked_alignment_unresolved。 [decision]
- 禁止：MET/有限码/FER/fresh qualification/公开 residual/coarse SER 冒充总 FER/
  Alice-oracle 选候选/holdout 选 mapping/raw pipeline/改动冻结 Polar 基线/push。 [decision]
- 未实现未执行；下一步 P0 只读审计 + P1 freeze review，ACCEPT 前不实现。 [pending]
---


## 2026-08-18 V24 gate result: FAIL — bounded single-edge route closed

- Pre-registered V24 M0-M2 gate completed: terminal_state `fail`
  (`single_edge_bounded_optimization_failed`). [decision]
- M0 mechanism PASS; 135 valid candidates from 8192 attempts; screen/refine/
  holdout all 0-converged (~0.20-0.32 entropy floor); 0/4 finalists passed all
  five holdout seeds. 314 DE calls, 4.87 h accumulated (<24 h). Read-only
  verifier ok=True. [repo-observed]
- Evidence:
  comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v24_20260818/run_20260818T135145_prod/
- V21/V22/V23 archived under openspec/changes/archive/2026-08-18-*. [decision]
- Successor: true MET is a separate user-authorized change candidate only;
  adjusting q/channel/f target is a separate user decision. No automatic
  fallback; no push. [decision]


## 2026-08-18 V24 engineering + archive + gate launch

- V21/V22/V23 formally archived (user-authorized): moved under
  openspec/changes/archive/2026-08-18-* with archive notes. [decision]
- V24 engineering (I01-I11) complete, all 21 focused tests pass. New files:
  [repo-observed]
  - comparison_bench/src/comparison_bench/formal_ir/nonbinary_v24_single_edge_de.py
  - comparison_bench/src/comparison_bench/cli/run_v24_single_edge_de.py
  - comparison_bench/tests/test_nonbinary_v24_single_edge_de.py
- V24 implementation facts (frozen packet): indexed proposal generator =
  SeedSequence([24000,k]) per attempt; 1-8 nonzero degrees/side; lambda degree
  2..64, rho degree 2..512; counts sum 64; profile validity is pre-DE and never
  depends on entropy; N_valid fixed regardless of DE error/nonfinite.
  [repo-observed]
- Proposal sparsity measured: only 135 unique valid in-band candidates across
  8192 attempts (band R in [0.9375, 0.94140625]).
- Pre-registered M0-M2 gate launched 2026-08-18 background; M0 mechanism PASS;
  screen in progress; evidence root under
  comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v24_20260818/.
  24h completed-DE-call resource gate enabled. [repo-observed]
- Expected terminal state likely `fail` (single-edge DE non-convergence ~0.3
  entropy is consistent across all prior V22/V23 ensembles). PASS/FINAL relay
  only after full gate + verifier. [pending]


## 2026-08-17 NBLDPC current single-edge tooling correction and V24 planning

- Current state is `NBLDPC_CURRENT_SINGLE_EDGE_TOOLING_BLOCKED`, limited to
  tested candidates/current V22b aggregate single-edge kernel. The prior
  route-wide unreachable conclusion is superseded. [decision]
- V21=`CONCLUDED_STOP_GATE_TRIGGERED_PENDING_ARCHIVE`: S0/S1/S2 FER
  0.625/0.5625/0.5625 retained; P0/P1 not pre-frozen; runtime Alice-injection
  verifier and V01 not run. AST tests do not establish runtime semantic
  verification. [repo-observed]
- V22=`CONCLUDED_CURRENT_KERNEL_NEGATIVE_PENDING_ARCHIVE`: tested target
  candidates negative; finite I03/E02 and Bob-only V01 cancelled/not run after
  DE gate. [repo-observed]
- V23=`CONCLUDED_SINGLE_EDGE_DIAGNOSTIC_PENDING_ARCHIVE`: historical name
  notwithstanding, implementation aggregates base matrices to single-edge
  lambda/rho and invokes V22b; true topology-preserving protograph/MET DE was
  not implemented. Raw scan has 3 matrices; extra consolidated points lack
  independent raw/verify packages. [repo-observed]
- Closeout plan:
  `docs/nbldpc-v21-v24-closeout-and-successor-plan-20260817.md`. This round is
  planning/docs only: no code, DE, archive, scientific output, or push. The
  independent closeout/V24 freeze review returned ACCEPT after all contract
  blockers were closed; archive still requires later user authorization. [decision]
- V24 is `FROZEN_PENDING_USER_AUTHORIZATION`: P01–P06 complete and P07 is the
  next boundary. It covers bounded q1024 V17 structured single-edge lambda/rho
  DE optimization only. MET/finite/FER/qualification/promotion are out of scope;
  true MET is a separate change candidate only after V24 FAIL and user
  authorization. [decision]

## 2026-08-16 Route blocked awaiting user (superseded 2026-08-17)

- q1024 structured f<=1.3 not reachable with current tooling.
- Awaiting user choice: DE optimization / adjust target / MET / archive. [repo-observed]

## 2026-08-16 V19→V23 final review summary

- `docs/nbldpc-v19-v23-review-summary-20260816.md` written.
- Short-block OSD/top-K: scientific_not_ready; structured DE target f: not reachable.
- No new automatic direction without user input. [repo-observed]

## 2026-08-16 V23 DE not reachable conclusion

- q1024 structured rate0.9375 DE non-convergent across plain/SC/regular-protograph/irregular ensembles.
- entropy floor ~0.19-0.34; further needs full DE optimization or different channel decomposition.
- Evidence: nbldpc_v23_20260816/de_not_reachable_summary.json. [repo-observed]

## 2026-08-16 V23 protograph scan implemented

- 新增 nonbinary_v23_protograph.py + CLI + 测试。
- Regular protographs (2..8)x32..128 r0.9375 q1024 structured: all non-converged, entropy plateau ~0.2.
- Evidence: nbldpc_v23_20260816/protograph_scan_r09375_smoke/scan.json. [repo-observed]

## 2026-08-16 V23 protograph DE smoke

- V23 OpenSpec draft created.
- 2x32 all-ones protograph (r0.9375, q1024, structured V22b): non-converged, final entropy ~0.336.
- Next: small protograph grid scan / MET. [repo-observed]

## 2026-08-16 V22 DE_NOT_READY closeout

- q1024 r0.9375 structured DE non-converged across tools/budgets.
- V22 frozen scientific_not_ready; no finite construction.
- Next: MET/protograph DE (V23). [repo-observed]

## 2026-08-16 V22b budget scan still non-converged

- q1024 r0.9375 degree_max=512 n200 iter30: 3/3 non-converged.
- Structured target-rate DE not passing; need MET/protograph or accept not-ready. [repo-observed]

## 2026-08-16 V22b high-degree DE implemented

- 新增 nonbinary_v22b_mcde.py + de_gate + CLI + tests（临时提升 V14 DEGREE_MAX）。
- q1024 r0.9375 degree_max=512 可运行，non-converged at iter10。
- 证据：nbldpc_v22_20260816/v22b_de_gate_q1024_r09375_dmax512_smoke/de_gate.json。 [repo-observed]

## 2026-08-16 V22 task packet frozen

- 方案：additive V22b structured MC-DE with DEGREE_MAX>=128，然后 SC-LDPC 结构化适配。
- 阻塞：V14/V11 check degree cap=64，q1024 rate0.9375 无法运行。 [repo-observed]

## 2026-08-16 V22 structured DE diagnostic

- q1024 structured rate0.70: runs, non-converged.
- rate0.9375: rho check degree >64 cap in V14 MC-DE.
- Need MET/protograph or higher check-degree support to reach f<=1.3. [repo-observed]

## 2026-08-16 V22 SC-LDPC DE gate pass at p=0.05

- q1024, p=0.05, max_iter=50: 6/6 SC-LDPC rows converged, gate_passed=true.
- p=0.20/0.10 max_iter=20 non-converged.
- Evidence: nbldpc_v22_20260816/sc_de_gate_q1024_p005_iter50_smoke/sc_de_gate.json. [repo-observed]

## 2026-08-16 V22 SC-LDPC DE gate smoke

- 新增 `nonbinary_v22_sc_de_gate.py` + CLI + 测试（复用 V11 SC-MC-DE）。
- q1024 p=0.20 smoke：S1/S3 × G1/G2/G3 全部 non-converged。
- 证据：nbldpc_v22_20260816/sc_de_gate_q1024_p020_smoke/sc_de_gate.json。 [repo-observed]

## 2026-08-16 V22 q1024 DE gate smoke

- q1024 rate0.9375, 3 valid 8-degree candidates: all non-converged/error, gate_passed=false.
- Evidence: nbldpc_v22_20260816/de_gate_q1024_r09375_smoke/de_gate.json.
- Need real structured ensemble or larger budget. [repo-observed]

## 2026-08-16 V22 DE gate harness

- 新增 `nonbinary_v22_de_gate.py` + CLI + 测试。
- q16 smoke gate：3 个合法 8-degree 候选 non-converged。
- 下一步 q1024 DE gate。 [repo-observed]

## 2026-08-16 V21 Bob-only stop gate triggered

- 实现 V21 Bob-only 模块/CLI/测试；64 全新帧：
  S0 FER=0.625, S1 FER=0.5625, S2 FER=0.5625。
- 停止门触发：短块 OSD/top-K 分支冻结为 scientific_not_ready。
- V20 已移入 archive；V22 OpenSpec 草稿创建。 [repo-observed]

## 2026-08-16 V21 Bob-only plan frozen (post-review)

- 新契约：`docs/nbldpc-v21-bob-only-plan-20260816.md`。
- V20 addendum：31/64=oracle upper bound；40/96=top-4 oracle coverage；30/64=unverified Bob-only estimate；V01=counting-only。
- V20 status: CONCLUDED_PENDING_SCIENTIFIC_CORRECTION_AND_ARCHIVE。
- 下一步：Phase 0 收口 → V21 S0/S1/S2 Bob-only 验证。 [repo-observed]

## 2026-08-16 Round 108 — V20 M5 归档

- 使用规划 subagent 评估：建议归档 V20 M5。
- 已添加 archive_note.md；V20 tasks 状态 ARCHIVED。
- 最佳诊断：n64+bounded4 31/64, FER=0.515625。 [repo-observed]

## 2026-08-16 Round 107 — M2 random dense 不优于 PEG

- random dense H + bounded4 seed2252：3/8，差于 PEG+bounded4 5/8。
- M2 简单变体无增益。 [repo-observed]

## 2026-08-16 Round 106 — V20 M5 完成，等待新方向

- 全量回归 33 passed。
- V20 M5 COMPLETE；当前无自动下一步。 [repo-observed]

## 2026-08-16 Round 105 — V20 M5 最终结论

- 最终 N6 v6 表：n64+bounded4 主推 FER=0.515625；n80+bounded5 top-K 备选 FER=0.5833（12 seeds）。
- V20 M5 CONCLUDED。 [repo-observed]

## 2026-08-16 Round 104 — n80 12 seeds 仍差于 n64

- n80 seed2312: baseline 1/8 -> integrated 1/8（无增益）。
- 12 seeds 汇总：baseline 33/96 -> integrated 40/96（FER 0.6563 -> 0.5833），差于 n64 0.515625。
- 建议停止 n80 扩样，回到 n64 主推或探索混合策略。 [repo-observed]

## 2026-08-16 Round 103 — n80 11 seeds 仍差于 n64

- n80 seed2311: baseline 4/8 -> integrated 4/8（无增益）。
- 11 seeds 汇总：baseline 32/88 -> integrated 39/88（FER 0.6364 -> 0.5568），差于 n64 0.515625。
- n80 top-K 有正收益但整体不稳定。 [repo-observed]

## 2026-08-16 Round 102 — n80 高方差回落

- n80 seed2310: baseline 0/8 -> integrated 0/8。
- 10 seeds 汇总：baseline 28/80 -> integrated 35/80（FER 0.65 -> 0.5625），差于 n64 0.515625。
- n80 top-K 有正收益但不稳定，尚不能作为确定更优配置。 [repo-observed]

## 2026-08-16 Round 101 — n80 9 seeds 略优于 n64

- n80 seed2309: baseline 3/8 -> integrated 4/8。
- 9 seeds 汇总：baseline 28/72 -> integrated 35/72（FER 0.6111 -> 0.5139），略优于 n64 0.515625。
- 正收益：2301、2303、2305、2306、2307、2308、2309；无增益：2300、2304。 [repo-observed]

## 2026-08-16 Round 100 — n80 8 seeds 与 n64 打平

- n80 seed2308: baseline 2/8 -> integrated 3/8。
- 8 seeds 汇总：baseline 25/64 -> integrated 31/64（FER 0.6094 -> 0.515625），与 n64 最佳打平。
- 正收益：2301、2303、2305、2306、2307、2308；无增益：2300、2304。 [repo-observed]

## 2026-08-16 Round 99 — n80 top-K 成为新最佳（FER=0.5）

- n80 seed2307: baseline 4/8 -> integrated 5/8。
- 7 seeds 汇总：baseline 23/56 -> integrated 28/56（FER 0.5893 -> 0.5），**优于 n64 0.515625**。
- 新最佳配置：n=80,m=5 + bounded5 top-K=4。 [repo-observed]

## 2026-08-16 Round 98 — n80 第 4 个正收益 seed，几乎追平 n64

- n80 seed2306: baseline 4/8 -> integrated 5/8。
- 6 seeds 汇总：baseline 19/48 -> integrated 23/48（FER 0.6042 -> 0.5208），几乎追平 n64 0.515625。
- 正收益：2301、2303、2305、2306；无增益：2300、2304。 [repo-observed]

## 2026-08-16 Round 97 — n80 第 3 个正收益 seed

- n80 seed2305: baseline 3/8 -> integrated 4/8。
- 5 seeds 汇总：baseline 15/40 -> integrated 18/40（FER 0.625 -> 0.55），接近 n64 0.515625。
- 正收益：2301、2303、2305；无增益：2300、2304。 [repo-observed]

## 2026-08-16 Round 96 — n80 扩样后平均未优于 n64

- n80 seed2304: baseline 3/8 -> integrated 3/8（无增益）。
- 4 seeds 汇总：baseline 12/32 -> integrated 14/32（FER 0.625 -> 0.5625），尚未优于 n64 0.515625。
- 正收益 seeds 仍为 2301/2303。 [repo-observed]

## 2026-08-16 Round 95 — n80 top-K 多 seed 正收益

- n80 seed2303: baseline 3/8 -> integrated 4/8。
- 正收益 seeds：2301、2303；合计 baseline 7/16 -> integrated 9/16（FER 0.5625 -> 0.4375）。
- 2300 无增益；2302 潜在 2/8 待集成。 [repo-observed]

## 2026-08-16 Round 94 — n80 top-K 正结果

- n=80,m=5 seed=2026082301：
  - baseline（无 bounded-ML）：4/8 exact
  - + bounded5 top-K=4：5/8 exact（frame5 恢复）
- 首个 n80 正收益；需更多 seeds 统计平均。 [repo-observed]

## 2026-08-16 Round 93 — V20 M5 收尾完成

- V01 只读验证：8 个 bwml 输出合计 31/64 exact, FER=0.515625，无计数问题。
- V20 tasks M5 COMPLETE；V01/C01/C02 完成。
- 自动路线已到终点；进一步需新机制或用户方向。 [repo-observed]

## 2026-08-16 Round 92 — edge-label sweep 无提升

- 新增 `edge_label_seed`（API + CLI）。
- 固定 frame 2252 的 edge-label 1/2/3 均为 5/8 exact，无提升。
- 最佳仍 n64 31/64, FER=0.515625。 [repo-observed]

## 2026-08-16 Round 91 — 附加 n64 lambda/rho 探针无提升

- lambda062 seed2204 bounded4: 5/8（无提升）
- lambda058 seed2220 bounded4: 4/8（无提升）
- rho35_39 seed2252 bounded4: 3/8（更差）
- V20 M5 邻域基本穷尽；最佳仍 n64 31/64, FER=0.515625。 [repo-observed]

## 2026-08-16 Round 90 — frame_offset 分块支持；n80 top-K 无净提升

- 新增 `frame_offset`（API + CLI），支持分块跑有限码实验。
- n=80,m=5 seed=2026082300 top-K=2 分块完整集成：2/8 exact，与 V19 相同。
- n64 bounded4 仍为最佳：31/64, FER=0.515625。
- 新增 frame_offset 测试；全量 32 passed。 [repo-observed]

## 2026-08-16 Round 89 — top-K list decoding implemented; n80 potential

- `bounded_weight_ml_decode_candidates`（max_weight=5, top_k=4）实现并测试。
- n=80,m=5 seed=2026082300 frame0 直接验证 Alice 在 top4；单帧完整管线可 exact。
- 完整 8 帧 top-K 集成因计算量超时；后续需优化 numba top-K 或降低 K/帧数。
- n64 bounded4 单 ML 仍为 31/64, FER=0.515625。 [repo-observed]

## 2026-08-16 Round 88 — bounded-ML 扩展 max_weight=5；n80 单 ML 未提升

- `nonbinary_v19_bounded_ml.py` 增加 numba k=5 枚举，支持 n=80,m=5,max_weight=5。
- n80 seed2300 完整集成仍 2/8 exact；原因：weight<=3 错误候选先验得分高于 Alice，
  单 ML 不选 Alice；需 top-K 列表 + 公开校验/哈希。
- n64 bounded4 单 ML 仍是最佳实际改进：31/64, FER=0.515625。
- 新增测试 max5 identity；全量 30 passed。 [repo-observed]

## 2026-08-16 Round 87 — V20 bounded-ML 64 帧完整验证：31/64 exact, FER=0.515625

- 8 个 seed 全部用含 bounded-ML 的完整管线运行，确认 **31/64 exact_correct, FER=0.515625**。
- 新增 N6 v5 对比表：
  `n6_comparison_v5_q1024_v20_bwml/comparison_table.csv` + `comparison_summary.json`。
- 当前 q=1024 f≈1.136 最佳 FER=0.515625（diagnostic_only）。 [repo-observed]

## 2026-08-16 Round 86 — V20 批准；M5 bounded-ML 将 64 帧 FER 降至 0.515625

- 用户批准 V20 直接规划/执行；V20 status -> APPROVED/IN PROGRESS。
- 新增 `nonbinary_v19_bounded_ml.py`：bounded-weight ML 解码（max_weight=4，numba 加速），
  作为 V19 OSD 全失败后的 post-decoder 集成到 `nonbinary_v19_finite`。
- 在 n=64,m=4,lambda {2:0.6,3:0.4},f≈1.136 的 64 帧上：
  - V19 基线 28/64 exact, FER=0.5625
  - + bounded-ML **31/64 exact, FER=0.515625**
  - 恢复 seeds 2026082260/2144/2192，均用完整管线验证。
- 新增测试 `test_nonbinary_v19_bounded_ml.py`；V20 E01/E02 标记完成。 [repo-observed]

## 2026-08-16 Round 85 — BP-retry 诊断未恢复，V19 全路线穷尽

- 实现并运行 BP 随机先验扰动重试（blind-reconciliation 风格预研）：
  - hard frame 2055：beta=0.01/0.05/0.1/0.2 各 50 次，均未恢复；
    beta=0.5 因数值溢出/超时未完成。
  - seed 2252 的 3 个 mismatch 帧：beta=0.05 各 20 次，均未恢复。
- 至此 V19 已覆盖：PEG/FFT-QSPA、bounded/full OSD、MRB-OSD、rho 变体、
  code-seed sweep、BP-retry，均未把 f≤1.3 的 FER 降到可用水平。
- 下一步唯一可自动推进的是 V20 冻结；否则需用户提供新方向/新数据。 [repo-observed]

## 2026-08-16 Round 84 — V19 OSD/构造穷尽，V20 就绪待冻结

- 新增 `frame_seed` 参数（API + CLI `--frame-seed`），可固定帧数据、更换 code seed。
- hard frame seed 2055 固定帧、code seed 3001-3005 全部 `exact_mismatch`；
  rho 变体 {35,39}/{33,41}/{30,44} 仍失败。
- 直接 MRB-OSD probe（OSD-2 all-free/symbols 4-8、OSD-3/4 bounded、OSD-3 all-free/symbols 2）
  均未找到 Alice 码字；MRB-OSD 对 seed 2252/2276 也无变化。
- 结论：V19 PEG/FFT-QSPA/OSD 家族在 q=1024 f≤1.3 已穷尽。
- V20 proposal/design/tasks 已补充 Round 83-84 证据，标记 ready for freeze review；
  下一步需用户/主线程批准 V20 冻结。 [repo-observed]

## 2026-08-16 Round 83 — n=64 f=1.136 扩样 + MRB-OSD 诊断

- 最佳配置 n=64,m=4,lambda {2:0.6,3:0.4},f≈1.136 扩到 64 帧：
  **28/64 exact_correct, FER=0.5625**（32 帧时 15/32=0.53125；更大样本略差，诚实记录）。
- 同 f 中间块长：n=80,m=5 -> 2/8 exact (FER=0.75)；n=96,m=6 -> 1/8 exact (FER=0.875)。
  n=64 仍是该 f 点最佳。
- 新增 MRB-OSD：`nonbinary_v19_osd.osd_decode_candidates_mrb`（按可靠性升序置换列，
  使最不可靠列优先成为 pivot，信息集偏向最可靠列）；2 个新测试通过。
- `nonbinary_v19_finite` 对 n<=64 自动追加 MRB OSD-1 full + MRB OSD-2 broad。
- 初步对照：seed 2252 5/8、seed 2276 2/8，与旧 OSD 相同；MRB 尚未带来提升，
  下一步在更多 hard seeds / 更高阶 MRB 上评估，或转向 V20 冻结。 [repo-observed]

## 2026-08-16 V19 NBLDPC primary route — ROUTE EXHAUSTED (blocker)

- V19 diagnostics exhausted all current PEG/FFT-QSPA + bounded OSD attempts for
  q=1024 f≤1.3: every configuration yields `exact_mismatch` (0 exact).
- Comprehensive evidence:
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_primary_20260816/n4_finite_q1024_f129_blocker_summary.json`
- Next step is V20 OpenSpec change `formal-nonbinary-ldpc-v20-q1024-decode-improvement`
  (draft exists). No further automatic step is available until that change is frozen/approved.

## 2026-08-16 V19 NBLDPC primary route diagnostics (Route N0-N6 first pass)

- Added V19 nonbinary LDPC modules/CLIs/tests under comparison_bench only:
  `nonbinary_v19_channel.py`, `nonbinary_v19_de_search.py`, `nonbinary_v19_finite.py`,
  `cli/run_v19_nbldpc.py`, `cli/run_v19_three_way_compare.py`, 4 test files (11 passed).
- Evidence package:
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_primary_20260816/`
  - N1 channel: folded q=16 H=0.382911, full q=1024 H=0.549955.
  - N2a warm-started rate ladder from V18-B2 R=0.60 best at 0.65 small budget:
    non-converged, consistent with plain structured ceiling.
  - N2c extended-degree probe (degrees 48/60 at R=0.65): non-converged.
  - N3/N4 finite q=16 n=512 m=205 R≈0.5996 synthetic 4 frames:
    3 exact_correct / 1 exact_mismatch / 0 decode_failed, FER=0.25, f≈4.183.
  - q=1024 progress: `n4_finite_q1024_simple/finite_execute.json` (q=1024,
    n=64, m=24, R=0.625, 2/2 exact_correct, f≈6.819),
    `n4_finite_q1024_n128_simple/finite_execute.json` (q=1024, n=128, m=51,
    R≈0.602, 2/2 exact_correct, f≈7.245), and
    `n2_extended_probe_q1024/extended_degree_probe.json` (tiny DE probe,
    non-converged). `n6_comparison_v2_q1024` includes the q=1024 row and
    `leakage_decomposition.json` (q16 honest f≈3.016; q1024 n128 f≈7.245).
  - N2b capacity bound: `n2b_channel_aware_bounds/lsb_public_capacity.json`
    LSB-public does not reduce ideal f; full q=1024 coding is the binding target.
    Added `build_high_plane_w` and `high_plane_channels.json` for residual
    high-bit effective channels (l=0..6). A tiny q=512 R=0.92 DE probe on the
    l=1 high-plane channel was non-converged. [repo-observed]
  - q=1024 high-rate finite attempts: R=0.840 f=2.912 FER=0.5 (8/16 exact),
    R=0.891 f=1.989 FER=0.8125 (3/16 exact); all mismatches retained;
    `n6_comparison_v3_q1024_rates` records the tradeoff. A further n=1024,
    m=73, R≈0.929, f≈1.296 run ended 4/4 decode_failed (FER=1.0); corrected
    statuses in `n6_comparison_v4_corrected_statuses`. A 30-iteration probe and
    alternate degree-2/3 distributions all still decode_failed at f≈1.296, so
    the next step requires a new OpenSpec change for improved finite-length
    code/decoder design. Added optional `rho_edge` construction and a custom
    3-point rho probe at R=0.875 (`n4_finite_q1024_optrho_n512_m64`) also
    decode_failed. Added bounded single-symbol and two-symbol OSD-like
    postprocessors (`n4_finite_q1024_r089_simple_pp*`), which did not recover
    the tested frames. Added `find_two_degree_rho` and tested normalized
    Müller degree distribution at f≈1.296/f≈1.989; both still decode_failed.
    A longer n=2048,m=133 f≈1.181 attempt also decode_failed. Implemented
    bounded q-ary OSD-0/1 (`nonbinary_v19_osd.py`); R=0.89 q=1024 improved to
    2 exact / 2 exact_mismatch / 0 decode_failed, while f=1.296 n=1024 OSD-0
    still exact_mismatch. Added `osd_decode_candidates` and enumerated all
    OSD-1 single-flip candidates at f=1.296; still no exact match. Added
    bounded OSD-2 candidate search; f=1.296 probe still exact_mismatch, and a
    wider OSD-2 probe (top4/top16, 1531 candidates) also no exact. A PEG seed
    sweep (5 seeds) at f=1.296 all exact_mismatch. max_iter=50 + OSD still
    exact_mismatch (not iteration-limited). n=2048,m=126 f=1.119 OSD also
    exact_mismatch. Improved OSD reliability ordering (max-second-max) still
    exact_mismatch at f=1.296. V18-B2 optimized lambda with exact two-degree
    rho at f=1.296 also exact_mismatch. A 4-frame OSD run at f=1.296 gave
    4/4 exact_mismatch, FER=1.0. At R=0.84 OSD gave 3 exact / 5 mismatch /
    0 decode_failed in an 8-frame run. n=512,m=36 f=1.279 OSD also
    exact_mismatch, and n=128,m=9 bounded OSD also exact_mismatch. However,
    full OSD-1 on n=128,m=9 f=1.279 enumerated 121738 candidates and found
    Alice's codeword — first exact q=1024 f≤1.3 recovery. A second full
    OSD-1 frame at n=128 was not recovered; across four n=128 frames full
    OSD-1 recovered 1/4 exact (FER=0.75). A non-recovered frame also failed
    full OSD-1 + bounded OSD-2 and broad OSD-2 (top20/top4, top20/top16).
    n=64,m=4 f=1.136 full OSD-1 recovered 3/6 frames (FER=0.5); prior retry +
    full OSD-1 and broad OSD-2 also failed on a non-recovered frame; lambda
    {2:0.7,3:0.3} gave 0/2. Broad OSD-2 also failed on non-recovered seeds
    2056/2059. max_iter=50 + full OSD-1 also failed on seed2055; alternate
    code seeds 3001-3004 for the same frame also failed. Full OSD-1 summary:
    n=64 FER=0.6875 (5/16), n=128 FER=0.75 (2/8); broad OSD-2 did not recover
    any of the five n=64 non-recovered frames. Fast full OSD-1 enumeration
    (`osd_decode_candidates_fast`) integrated for n<=256 (~0.6s at n=64).
    Fast broad OSD-2 (`osd_decode_candidates_order2_fast`) also integrated
    for n<=128; fast bounded OSD-3 added; seed2055 still not recovered with
    top12/top8 or OSD-4 top8/top2/top4; fast OSD-1/2/3/4 integrated for
    n<=64, seed2055 still non-recovered. A new n=64 fast OSD-1/2/3/4 batch
    gave FER=0.5 (4/8), second batch 0/8; combined 4/16 FER=0.75.
    seed2055 remained non-recovered after prior-retry + OSD-1/2/3/4 and
    generic OSD order5/6. n=64 fast OSD-1..10 combined FER=0.71875
    (18/64); lambda {2:0.6,3:0.4} gave FER=0.5625 (7/16); lambda
    {2:0.7,3:0.3} gave FER=0.75 (2/8); {2:0.8,3:0.2} also FER=0.75 (2/8);
    {2:0.4,3:0.3,4:0.3} gave FER=0.625 (3/8); {2:0.55,3:0.45} gave
    FER=0.875 (1/8); {2:0.65,3:0.35} gave FER=0.625 (3/8). Best lambda
    {2:0.6,3:0.4} over 24 frames: FER=0.5833 (10/24); at n=128 same lambda
    gave 0/4. {2:0.62,3:0.38} gave 5/16 (FER=0.6875); {2:0.58,3:0.42} gave
    6/16 (FER=0.625); {2:0.59,3:0.41} gave 1/8 (FER=0.875); {2:0.61,3:0.39}
    gave 2/8 (FER=0.75). Best lambda {2:0.6,3:0.4} reached 15/32 exact
    (FER=0.53125). Comprehensive blocker summary
    written into V20 proposal/tasks. Created V20
    OpenSpec draft `formal-nonbinary-ldpc-v20-q1024-decode-improvement`
    (proposal/design/tasks) as the next step. [repo-observed]
  - N6 comparison table vs binary LDPC MLC (f≈4.169, FER=0); Polar MLC row
    `not_available` until clean evidence from `D:\Code\HD-QKD_Polar_Release`.
- Claim boundary: diagnostic_only. Frozen baselines untouched; outputs additive;
  local git commit only; push still user-gated. [decision]

## 2026-08-16 Proper CRC-aided SCL progress

- Implemented v19_polar_crc.py matching frozen C++ check_crc16.
- Plane 9, N=2048, PW-order, CA-SCL list=128 with valid CRC: 13/20 correct vs 0 before.
- FER still ~0.35; next is Tal-Vardy/polar-spectrum construction and/or SCL-flip. [repo-observed]

## 2026-08-16 Decoder improvement plan (literature-grounded)

- Polar path: current CA-SCL does not actually receive CRC bits from our MLC payload; next concrete step is proper CRC-aided SCL integration (reserve 16/24 CRC bits).
- Construction: replace PW/GA with Tal-Vardy quantization or polar-spectrum UBW/SUBW; consider SCL-flip/ADSCL.
- LDPC path: extend binary DE to dc>13 in v19, use MET-LDPC/degree-one VN and rate-compatible puncture/shorten for low-error high-rate planes.
- HD-QKD anchor: Mueller et al. 2024 f≈1.078–1.14 requires full DE-optimized irregular q-ary + blind reconciliation.
- Plan doc: docs/decoder-improvement-plan-20260816.md. [repo-observed, plan]

## 2026-08-16 V19 LDPC DE screener

- Added per-plane BSC DE-gated LDPC screener using frozen `binary_bsc_threshold`.
- With frozen DE bound dc<=13, only planes 8/9 found regular ensembles meeting f≈1.3 target.
- Planes 0–7 require very high-rate codes (small m/N) not reachable by regular dc<=13 LDPC.
- This explains the need for irregular/structured high-rate codes or extended DE tooling. [repo-observed, diagnostic_only]

## 2026-08-16 V19 Polar N=8192 negative result

- Tested N=8192, GA mask, CA-SCL list=128, plane 9, f≈1.3 per-plane target.
- Single frame decode took ~122 s and still failed.
- This closes the Polar/SCL scaling path with the current decoder; next recommendation is a different code family / optimized LDPC DE-gated design. [repo-observed, diagnostic_only]

## 2026-08-16 V19 Polar GA frozen-set attempt

- Added `v19_polar_ga.py` implementing GA/J-function reliability for per-plane BSC Polar construction.
- Tested GA masks with CA-SCL list=128 at N=2048 for planes 9/8/7; still frame errors at f≈1.3 target.
- Combined with earlier PW/MC attempts, cheap frozen-set construction is not sufficient for f≤1.3 with current Polar SC/SCL at N≤4096.
- Future path: larger N, CRC-aided SCL with tailored construction, different code family, or finite-length f relaxation. [repo-observed, diagnostic_only]

## 2026-08-16 V19 CA-SCL experimental decoders (list 32/128)

- Added experimental CA-SCL copies under comparison_bench (not frozen src):
  - `v19_ca_scl.cpp` (list=32), `v19_ca_scl128.cpp` (list=128), compiled DLLs, and wrapper `v19_ca_scl_wrapper.py`.
- Noiseless wrapper test passes; corrected output ordering (C++ returns info bits in ascending index order).
- At N=2048/4096 with PW-order or Monte-Carlo info selection, both list=32 and list=128 still fail to reach f≈1.3 target rates on multiple planes.
- Conclusion: reaching f≤1.3 needs GA/tailored frozen-set construction or a different code family; list size alone is not sufficient. [repo-observed, diagnostic_only]

## 2026-08-16 V19 binary-MLC prototype and high-rate code design attempts

- Added v19 channel scoping CLI: per-plane h2 sum = H_full≈0.549955, ideal binary-MLC f≈1.0.
  Existing binary v4 H1 f≈4.148; v5 H1+H2 f≈6.932. [repo-observed]
- Added v19 binary-MLC prototype using frozen v4 H1 + v5 H2 fallback on V17 per-plane BSC:
  50 frames/plane, 0 failures, average syndrome 587 bits/frame, measured f≈4.169. [repo-observed]
- Exploratory high-rate designs:
  - Random LDPC N=2048 target f≈1.22: many failures.
  - Polar SC and CA-SCL(list=4) N=2048 target f≈1.32: many failures.
  Conclusion: reaching f≤1.3 requires optimized code design (better polar construction/larger list/CRC or optimized LDPC), not naive random or current PW-order SC/SCL. [repo-observed, diagnostic_only]
- Next: v19 DE gate / optimized per-plane code design remains user-gated/new change. [decision]

## 2026-08-16 Route B M2 diagnosis: structured channel is the DE ceiling; QSC control converges

- Route A completed: 128 decode_failed frames are not iteration-limited and not QSC prior mismatch
  (max_iter 200/500, oracle prior, p-grid all failed). [repo-observed, diagnostic_only]
- Route B M0/M1/M1b completed: V18-B1 q=4 DE reproduction gate PASS after M1b correction
  (`threshold_proxy≈0.06758`, delta≈0.00142). [repo-observed]
- Route B M2: implemented structured-DE using V17 per-bit-plane + Gray + fold to q=16.
  Best plain result: rate=0.60, seed 2026081707, f≈4.18 (syndrome 1.6 bits/H_fold 0.3829).
  All rate>0.60 attempts failed (0.61/0.62/0.63/0.65, random and seeded).
  q=32 exploratory searches also all failed. [repo-observed]
- Decisive control: equal-entropy QSC(q=16, p=0.038, H≈0.3815) converged 16/16 at rate 0.63/0.65
  with the same DE budget; folded real structured channel 0/16. Conclusion: **channel structure limits
  plain irregular NB-LDPC DE, not search budget**. [repo-observed, diagnostic_only]
- Next automatic artifacts created: channel-aware DE gate proposal draft and Route C1 design draft.
  Execution of those routes remains a user-gated decision per plan
  `docs/route-b-c-d-next-steps-plan-20260819.md`. [decision]
- Local commits made; push still requires separate user authorization. [repo-observed]

# AGENT_PROJECT_MEMORY.md

## 2026-08-13 Mainline fusion merge — main = db00174d, two lines re-fused

- The local working line is now `main` at merge commit
  `db00174d2d9edb471da5cae159561c04fdf40ccd` (parents `c7853867…` PolarCode
  line + `8338c9e4…` formal-ir line), pushed to origin/main and synced
  (local main == origin/main). Supersedes the 2026-08-12 entry's
  "working branch is formal-ir-accumulation"; that branch is now a
  historical label only. [repo-observed]
- Line history: the local formal IR line (`comparison_bench/`, `openspec/`,
  `formal_ir/`, nonbinary LDPC v1-v12, cascade, ldpc v2-v5) and the remote
  PolarCode line (`pipelines/`, `tools/diagnostics|security_reports`,
  `src/qkd_io`, Route A/B-lite audit, P0/P1 release hygiene: checksum
  verification, `CURRENT_MAINLINE.md`, runtime paths) forked at `b6f61d40`
  and are now re-fused. The merge tree contains both sides completely
  (695 + 215 file diff verified). [repo-observed]
- Six conflict files resolved by policy: add/add → formal-ir version for
  `AGENT_HANDOFF.md`, `AGENT_PROJECT_MEMORY.md`, `wsl-env.sh`; content →
  two-side merge for `.gitignore`, `README.md`,
  `experiments/run_golden_sweep_four_datasets.py`. [decision]
- Local branch cleanup completed: `develop`, `codex/feat/polar-diagnostics-occupancy`,
  `wt-a1..wt-ab` deleted; all worktrees removed (formerly
  `C:/Users/admin/.codex/worktrees/*`). Local branches now only `main`
  (working line) and `formal-ir-accumulation` (historical tip `8338c9e4`,
  kept as label/backup, pushed to origin). [repo-observed]
- Remote branches preserved: origin/main (`db00174d`),
  origin/formal-ir-accumulation (`8338c9e4`),
  origin/codex/feat/polar-diagnostics-occupancy (stale, `e0494156` — do not
  treat as current), origin/project-restructure-20260427 (`0e4f7351`, merged
  into main history). [repo-observed]
- AGENT_PROJECT_MEMORY.md itself was committed in `8338c9e4` (carrying the
  2026-08-12 triage entry); the merge kept the formal-ir version. This entry
  is an uncommitted working-tree addition by design. [repo-observed]
- Still deliberately untracked (user decision: leave for now; they now hang
  on the main worktree): v12 real-micro/partition and ldpc_v5 transfer
  evaluation sources + tests — 8 py files under
  `comparison_bench/src/comparison_bench/{cli,formal_ir}/` and
  `comparison_bench/tests/` — plus
  `outputs_comparison/{final_ir_method_selection,formal_ir_methods,transfer_evaluation}/`,
  the `comparison_bench/新增卷 (D).lnk` Windows shortcut leftover, and
  `workspace/` scratch. Do not commit or delete unprompted. [repo-observed]
- Environment facts: `http.sslBackend schannel` already recorded in §3; local
  proxy 127.0.0.1:7899 had a transient outage during the merge (no durable
  impact); git 2.52.0 in use, supports `merge-tree --write-tree`. [repo-observed]

## 2026-08-12 Formal IR accumulation commit, branch, and push

- Current working branch is `formal-ir-accumulation`, HEAD =
  `189d6c31aa445d0666bd78d32490041a8b14092c` ("feat(formal-ir): accumulate
  formal IR source, tests, CLIs, OpenSpec changes, and agent docs", 342 files,
  +60736/−109), pushed to origin
  (https://github.com/Placebo303/HD-QKD-Polar-pipeline.git) with upstream
  tracking set and remote hash identical. This commit was previously a
  detached-HEAD chain (2bb0d5b → 921d002 → 9666eec → 189d6c3) and is now
  mounted on the new branch; develop (b039dfb), main (2f496c0), and
  codex/feat/polar-diagnostics-occupancy (7085f0b) were not touched.
  [repo-observed]
- Commit contents: `comparison_bench/src/comparison_bench/formal_ir/` (63
  modules: cascade, ldpc, ldpc_v2-v5, codebook_*, nonbinary field/qspa/v2-v11,
  real_qualification.py, long_v3_*), 37 CLIs under `cli/`, `data_lock.py`,
  `final_selection_audit.py`, 79 test files, `requirements-formal-ir.txt`, 2
  comparison_bench docs, 4 root docs, OpenSpec 4 archived + 16 active changes +
  2 new merged spec dirs (`openspec/specs/final-ir-method-selection/`,
  `openspec/specs/formal-ir-methods/`). Frozen baseline `src/`, `experiments/`,
  `tools/`, `results/` zero change; the 111 tracked
  `outputs_comparison/` files zero change. [repo-observed]
- Deliberately NOT committed (untracked, per repo output/scratch policy): all
  `workspace/` scratch roots (145 tracked files exist under them), the
  `outputs_comparison/final_ir_method_selection/` and
  `outputs_comparison/formal_ir_methods/` output directories, and the root
  `新建卷 (D).lnk` Windows shortcut leftover. Do not commit or delete these
  unprompted. [repo-observed]

## 2026-08-11 Nonbinary LDPC V11 spatial-coupling DE gate — failed_coupling, successor guidance

- Change: `formal-nonbinary-ldpc-v11-sc-de-gate`. Final state
  **failed_coupling** (`evidence/decision/final_gate_decision.json`, schema
  `v11_final_gate_decision_v1`, decided 2026-08-11 by main thread, confirmed
  by reviewer-go V11-50.3 independent final acceptance, 16/16 A01-A16 PASS).
  All checks pass (rate/resource/replay/structured/semantic true; gates
  0/3); the provisional `failed_reference` in the execution-root summary was
  a checks-pending placeholder and is superseded by the final decision file.
  [repo-observed, decision]
- Scientific conclusion: the spatial-coupling hypothesis is REJECTED under
  the frozen V10 S1/S3 lambda distributions and the frozen G1 (w=1,L=32,W=8),
  G2 (w=2,L=32,W=16), G3 (w=2,L=32,W=32) geometries. Coupled conservative
  thresholds: S1 G1 .2100 / G2 .2025 / G3 .2019 (gate >= .22, 0/3); S3
  G1 .3125 / G2 .3000 / G3 .3000 (gate >= .32, 0/3); every paired
  conservative gain is negative (S1 -0.0075/-0.0144/-0.0156; S3
  -0.0137/-0.0256/-0.0206). No silent promotion, no "closest to gate", no
  matrix shrink. [repo-observed, decision]
- Successor guidance: after V10 failed_ensemble and V11 failed_coupling,
  design.md §8's simple alternative (stop and honestly report that the
  current uncoupled ensemble family misses the robust gates) is the current
  valid option; V11's spatial-coupling test changed nothing. Any
  finite-length/lifting, windowed FFT-QSPA, decoder, canary, real-data,
  qualification, or promotion work requires a NEW OpenSpec change with fresh
  roots and fresh development/confirmation data. [decision]
- Reference reproduction (V11-10.1/10.2): `formal_ir/nonbinary_v11_smp_de.py`
  reproduces the four published q=4/q=16 SMP-DE anchors (uncoupled + coupled,
  rate-1/2 (3,6), W=30) within frozen tol 0.002 — q=4 uncoupled 0.0890 vs
  0.0888, q=4 coupled 0.0942 vs 0.0945, q=16 uncoupled 0.1075 vs 0.1072,
  q=16 coupled 0.1288 vs 0.1287; coupled gain reproduced in both orders
  (q=4 +0.0057 vs published +0.0052; q=16 +0.0215 vs +0.0213). Sources:
  uncoupled SMP-DE Lázaro et al., arXiv:1906.02537 (Globecom 2019); coupled
  Ben Yacoub et al., AEIT 2019, DOI 10.23919/AEIT.2019.8893373. Trace:
  `evidence/reference/smp_de_trace.json`. [repo-observed]
- Resource facts (reusable for future GF(1024) DE work): full-vector coupled
  MC-DE per-iteration costs at N=2000 — G1 ~2.25 s, G2 ~4.97 s, G3 ~9.89 s,
  uncoupled control ~0.23 s (microbenchmark2.json). numba njit hot-kernel
  integration in `nonbinary_v11_mcde.py` gave 11.65x total speedup (predicted
  serial 777.33 h -> 66.72 h; per-cell 9.5-12.5x). 4-worker batch parallelism
  (#3) gives only 2.04x with per-worker efficiency 0.51 — batch efficiency
  does NOT extrapolate to the uniform 60-task matrix (load imbalance); the
  correct extrapolation is task-level LPT scheduling simulation
  (formal_plan.md §4): 17.1-19.7 h (central 18.9 h), under the 24 h limit.
  Actual execute: 60/60 runs once 2026-08-08, 15.83 h wall < 24 h, peak RSS
  2.82 GiB < 3 GiB. [repo-observed]
- Process precedents (reusable): budget amendments AMEND-2026-08-06-01
  (numba, limited to `nonbinary_v11_mcde.py` hot kernels, scientific
  parameters unchanged) and AMEND-2026-08-06-02 (4-worker parallel executor,
  RSS judged per single-run peak) — both user-approved, engineering-only,
  exactly-once re-measurement with prior evidence unchanged
  (`evidence/resource/microbenchmark{2,3}.json`). The long scientific execute
  ran as a detached background process with executor bookkeeping
  (`nonbinary_v11_execute.py`): progress.json + heartbeat.json (daemon
  thread) + `--resume` (terminal runs never re-run; failed evidence
  immutable) + `--status`. Lesson: batch-efficiency extrapolation
  overestimates for uniform task matrices; use LPT task-level simulation
  (formal_plan.md §4.4). [repo-observed, decision]
- Reusable assets under `comparison_bench/src/comparison_bench/formal_ir/`:
  `nonbinary_v11_smp_de.py` (SMP-DE reference, four reproduced anchors);
  `nonbinary_v11_mcde.py` (full-vector coupled MC-DE kernel, numba hot
  kernels, w=0 byte-identity to V9 uncoupled — covered by the 24 V11 MC-DE
  tests); `nonbinary_v11_execute.py` (threshold bisection + parallel executor
  + gate decision, reusable for any future DE gate work);
  `nonbinary_v11_parallel.py` (worker-pool executor);
  `nonbinary_v11_microbench.py`. [repo-observed]
- Frozen baseline: `src/`, `experiments/`, `tools/`, `results/` zero change;
  regression 87 passed; no new entry under
  `comparison_bench/outputs_comparison/formal_ir_methods/` (A14 PASS). All
  evidence under the change's `evidence/` (reference/, resource/, replay/,
  decision/, formal_plan.{json,md}, literature-review.md). Execute/replay
  roots: `workspace/nbldpc_v11_execute_002d51de/`,
  `workspace/nbldpc_v11_replay_8e63bf62/` (60/60 byte-identical science
  fields). docs/decision-log.md 2026-08-11 entry appended. [repo-observed]

## 2026-08-06 Nonbinary V10 failed_ensemble — final state, no-hash amendment, V11 successor

- Change: `formal-nonbinary-ldpc-v10-de-peg-fftqspa`. Final state
  **failed_ensemble** (`evidence/v10_gate_decision.json`, schema
  `v10_gate_decision_v1`): the V10A GF(1024) four-search density-evolution
  ensemble gate FAILED (hard stop V10-S02). V10-30 (PEG), V10-40 (FFT-QSPA),
  V10-50 (canary), and V10-60 (development) are all HALTED. There is no
  "closest to gate", no rerun, no tuning; no codebook/decoder/canary/
  development/qualification/real-data/promotion output exists under this
  change. [repo-observed]
- V10-0 q=4 reference-recovery gate PASS: conservative threshold 0.06414,
  |δ| = |0.06414 − 0.069| = 0.00486 ≤ 0.012; main-thread accepted
  2026-08-05. [repo-observed]
- V10A searches: S1 (p=.20, f=1.15) conservative 0.2153 < 0.22 FAIL; S2
  (p=.20, f=1.08) conservative 0.1984 < 0.215 FAIL; S3 (p=.30, f=1.15)
  conservative 0.3166 < 0.32 FAIL; S4 (p=.30, f=1.08) no eligible candidate
  FAIL. [repo-observed]
- Execute/replay: V10A executed once (~10470 s, peak RSS 335 MB < 3 GiB);
  first replay attempt interrupted (PID 21032 died, S1 only); per precedent
  `replay_attempt2/` completed 04:36–07:07Z (RSS 339 MB); direct byte
  comparison PASS across 129 files — scientific files byte-identical, only
  provenance normalization differs (plan_binding digest key, run_complete
  role/stage). [repo-observed]
- 2026-08-06 protocol amendment (main-thread): defensive SHA-256/checksum/
  integrity-manifest mechanisms (plan-bound digest, manifest self/source
  hash, per-file compare sha256) removed per AGENTS.md §5.7; replacements
  are git baseline checks, direct byte comparison, structured field
  validation, and semantic recomputation. `v10_seed` is RETAINED as a
  deterministic RNG derivation primitive — DE population initialization and
  mutation RNG streams depend on it and completed results depend on its
  byte reproduction. Amendment record:
  `evidence/v10_protocol_amendment_no_hash_v1.json`. [decision]
- Evidence (change `evidence/`): `v10a_execute_results.json`,
  `v10a_replay_evidence.json`, `v10a_gate_decision.json`,
  `v10_gate_decision.json`, `v10_t3_regression.json` (git baseline PASS,
  frozen directories zero change), `v10_protocol_amendment_no_hash_v1.json`.
  [repo-observed]
- Tests: full V10 suite 89 passed (common 23 / de 24 / gate 13 / peg 12 /
  fftqspa 17). [repo-observed]
- Frozen baseline: git HEAD
  `a9c3c5d8696ad9fa967e2d5d8b9905c5a55c8344`; `src/`, `experiments/`,
  `tools/`, `results/` zero change;
  `comparison_bench/outputs_comparison/formal_ir_methods/` has no new V10
  output; the 12 tracked modifications are pre-existing dirty-worktree
  entries of other workflows. [repo-observed]
- V10-30.DESIGN task (PEG no-hash design note) remains unchecked and is
  left for future V11 inheritance. [repo-observed]
- Close-out (2026-08-06): `evidence/v10_s4_delta_correction.json` (schema
  `v10_s4_delta_correction_v1`) records the S4 `delta` boolean-false /
  null-semantics correction (build_evidence short-circuit bug); evidence
  immutable, script expression fixed; reviewer-go final review ACCEPT
  (`evidence/v10_independent_review_acceptance.json`, schema
  `v10_independent_review_acceptance_v1`, 89 tests pass). [repo-observed]
- Successor: a brand-new V11 NB-SC-LDPC OpenSpec change (fresh everything:
  new change, new roots, new development/confirmation data); starting V11 is
  a user decision; nothing further is authorized under V10. [decision]
- Archived (2026-08-06): change directory moved to
  `openspec/changes/archive/2026-08-06-formal-nonbinary-ldpc-v10-de-peg-fftqspa/`
  (equivalent rename; delta specs not merged; local commit, not pushed).
  [repo-observed]

## 2026-08-06 Research Code Engineering Policy (AGENTS.md §5.7)

- Change `research-code-engineering-policy` implemented via the OpenSpec flow;
  policy now lives at AGENTS.md §5.7 (lines 80-110) and was reviewed ACCEPT by
  reviewer-go (no blocking items). Not yet archived; archive action pending
  user decision. [repo-observed]
- Core requirements: this repository is local research code, not a production
  service. Unless a task explicitly requires it, do not add checksums/integrity
  manifests, atomic/transactional writes, backup/rollback, file locking,
  elaborate schema validation, retry frameworks, security hardening,
  compatibility layers, custom caching, or exception handling that hides
  errors. Assume trusted local inputs, manual single-machine runs, rerunnable
  failures, and Git version control. Prioritize scientific/numerical
  correctness, explicit units/assumptions/parameters, readable calculations,
  reproducible seeds, validation against known limits, clear errors, and
  minimal dependencies/abstraction. Identify the concrete failure mode before
  adding any defensive mechanism; do not generalize one-off scripts into
  production frameworks. [repo-observed]
- Scope: only AGENTS.md and the openspec change directory; frozen baseline
  (src/, experiments/, tools/, results/) untouched. Pre-existing dirty files
  (AGENT_HANDOFF.md, CURRENT_TASK.md, AGENT_PROJECT_MEMORY.md,
  docs/decision-log.md, AGENTS.md §10.1) belong to earlier work, not this
  change. [repo-observed]

## 2026-08-04 V9A GF(1024) long-block ensemble gate STOP

- Change: `formal-nonbinary-ldpc-v9-gf1024-long-ir`.
- V9A executed once under the frozen v2 budget protocol (pid 5084, 3968.5 s,
  peak RSS 428.3 MiB) and strict-replayed once (pid 29340, 4838.5 s). Scientific
  outputs are deterministic and byte-identical between execute and replay; only
  `run_meta.json` differs in provenance fields.
- All four searches (S1 robust gate .22, S2 target gate .215, S3 robust gate
  .32, S4 target gate .32) recorded zero eligible candidates; every gate FAILS.
- Conservative threshold undefined for every gate; downstream tier selection is
  null for both strata.
- Decision: frozen STOP before any finite codebook. V9B/V9C unreachable. No
  codebook, decoder, canary, development, qualification, real/N4 data,
  promotion, or formal comparison is authorized under this change.
- Evidence files under
  `openspec/changes/formal-nonbinary-ldpc-v9-gf1024-long-ir/evidence/`:
  `v9_00_freeze.json`, `v9a_plan_v2.json`, `v9a_execute_results.json`,
  `v9a_replay_evidence.json`, `v9a_gate_decision.json`,
  `v9a_interrupted_trial_freeze.json`, `v9a_interrupted_v2_attempt_freeze.json`,
  `v9a_independent_review_acceptance.json`.
- Process note: the replay script overwrote the shared
  `evidence/v9a_execute_results.json` path because it lacked a guard on that
  file; the orchestrator restored the original execute version from
  `workspace/v9a_04c9e7d25d7145659685415084d6fac7/v2_execute/`. Scientific
  impact: none (payload identical; only provenance fields changed); the missing
  guard is a process improvement for future changes, not a scientific defect.
- Close-out complete (2026-08-04): reviewer-go independent review verdict
  ACCEPT — all checklist items pass (matches OpenSpec spec, tests pass, no
  scope creep, decision log updated, V9B/V9C artifacts absent, scientific
  wording scoped), no blocking issues.
- Independent hash verification: 9/11 files byte-identical between execute and
  replay; 2 differ only in provenance (`evidence_v9a_execute_results.json`,
  `run_meta.json`). `S4.progress.jsonl` known hash verified:
  80ee59eb194c60a897ac43d4b09a5d1fd4ff76c8bd0a7394a155606e7cfc632a (this
  supersedes the `TO_BE_COMPUTED_BY_INDEPENDENT_REVIEWER` placeholder in
  `v9a_replay_evidence.json`).
- Change status: STOPPED at the V9A ensemble gate; will NOT advance to V9B/V9C.
  Close-out checklist V9A-C1 through V9A-C8 all checked. The change is
  archive-ready pending the archive action (`/opsx-archive`).
- Scientific boundary: the frozen 8-candidate V9A bounded enumeration failed
  its preregistered gates. This is NOT a general negation of GF(1024) LDPC and
  not a claim that complete ensemble optimization was exhausted; a successor
  requires a new OpenSpec change with fresh roots, a different ensemble family,
  and new development/confirmation data.
- Next: archive the change (OpenSpec archive action). No further work is
  authorized under this change.

## 2026-07-26 Nonbinary N3 evidence boundary

`nbldpc_formal_v1` completed its only frozen q=1024 synthetic N3 execution at
`comparison_bench/outputs_comparison/formal_ir_methods/20260726_v1_nbldpc_synthetic`.
Selected policy SHA `23a1b46300f1c841eed3ffc6f672840c7be17608260de6b09944cac74228983d`
was margin 7/scale 1.0/max_iter 10 with 32 checks in both strata. Confirmation
was non-promoted: p=.20 18/32 verified success and p=.30 5/32, both below the
31/32 gate; N4, reruns, and tuning are forbidden. The official strict verifier
failed only because post-execution whole-worktree git-status provenance drifted.
Source/CLI/contract hashes, commit, Python and NumPy matched; `_test_only=True`
diagnostic replay is not an official verifier pass. Preserve all seven artifacts.

## 1. Project Identity
- Project name: `HD-QKD_Polar_Comparison` [repo-observed]
- Research purpose: evaluate and compare information reconciliation (IR) methods for high-dimensional QKD data, while preserving the copied Polar pipeline as a frozen baseline and adding a separate comparison layer. [repo-observed]
- Main scientific/engineering objective: build a reproducible, non-invasive benchmark layer that can (a) read/import existing Polar results, (b) run executable comparison baselines on synthetic and real paired-symbol frame data, and (c) generate comparable CSV/Parquet/summary outputs without changing the original Polar workflow semantics. [repo-observed]
- Current maturity: mixed. The original Polar repository appears to be a mature replay/security/reporting codebase; `comparison_bench/` is an additive benchmark layer with working CLIs, tests, real-data imported Polar baseline, real-data/synthetic executable baselines, and v3 parameter-sweep/report outputs. [repo-observed]

## 2. Repository Structure Observed
- Top-level directories observed: `analysis/`, `comparison_bench/`, `docs/`, `experiments/`, `results/`, `src/`, `tools/`, `workspace/` [repo-observed]
- Top-level files observed: `README.md`, `requirements.txt`, `bootstrap_clone_clean.py`, `wsl-env.sh`, `LICENSE`, `.gitignore` [repo-observed]
- Original pipeline entrypoints:
  - `experiments/run_e2e_pipeline.py` [repo-observed]
  - `experiments/run_real_polar_max_pie.py` [repo-observed]
  - `experiments/run_golden_sweep_driver.py` [repo-observed]
  - `experiments/run_golden_sweep_four_datasets.py` [repo-observed]
- Original source areas:
  - `src/qkd_io/ttbin_pipeline.py` [repo-observed]
  - `src/workflow/coarse_grain_joint.py` [repo-observed]
  - `src/workflow/export_joint_sequence_sidecar.py` [repo-observed]
  - `src/workflow/llr_from_joint.py` [repo-observed]
  - `src/reconciliation/real_polar_sc_rescue.py` [repo-observed]
  - `src/reconciliation/cpp_scl_wrapper.py` [repo-observed]
  - `src/reconciliation/verification.py` [repo-observed]
  - `src/reconciliation/cpp_polar/` containing `.dll`, `.exe`, and C++ files [repo-observed]
- Original tooling area includes many audit/security/reporting scripts, for example:
  - `tools/longrun_build_replay_index.py` [repo-observed]
  - `tools/longrun_run_actual_ir_replay.py` [repo-observed]
  - `tools/longrun_build_finite_key_audit_table.py` [repo-observed]
  - `tools/longrun_build_security_master_table.py` [repo-observed]
  - `tools/minrerun_run_frame_audit.py` [repo-observed]
  - `tools/minrerun_rebuild_security_master_20dB.py` [repo-observed]
  - `tools/routeA_run_formal_cross_loss.py` [repo-observed]
- Comparison layer structure:
  - `comparison_bench/README.md` [repo-observed]
  - `comparison_bench/requirements-comparison.txt` [repo-observed]
  - `comparison_bench/configs/benchmark_realdata.yaml` [repo-observed]
  - `comparison_bench/configs/benchmark_synth.yaml` [repo-observed]
  - `comparison_bench/configs/cascade_param_sweep.yaml` [repo-observed]
  - `comparison_bench/configs/layered_ldpc_param_sweep.yaml` [repo-observed]
  - `comparison_bench/configs/qldpc_param_sweep.yaml` [repo-observed]
  - `comparison_bench/configs/ir_methods_v3_master.yaml` [repo-observed]
  - `comparison_bench/docs/architecture.md` [repo-observed]
  - `comparison_bench/docs/data_contract.md` [repo-observed]
  - `comparison_bench/docs/method_notes.md` [repo-observed]
  - `comparison_bench/src/comparison_bench/cli/` with:
    - `build_dataset.py` [repo-observed]
    - `run_benchmark.py` [repo-observed]
    - `compare_methods.py` [repo-observed]
    - `smoke_test.py` [repo-observed]
    - `run_cascade_param_sweep.py` [repo-observed]
    - `run_layered_ldpc_param_sweep.py` [repo-observed]
    - `run_qldpc_param_sweep.py` [repo-observed]
    - `run_ir_v3_master.py` [repo-observed]
    - `make_report_tables.py` [repo-observed]
  - `comparison_bench/src/comparison_bench/io/` with:
    - `pairs_loader.py` [repo-observed]
    - `dataset_builder.py` [repo-observed]
    - `polar_existing_bridge.py` [repo-observed]
    - `table_store.py` [repo-observed]
  - `comparison_bench/src/comparison_bench/methods/` with:
    - `cascade_lite.py` [repo-observed]
    - `layered_ldpc_lite.py` [repo-observed]
    - `qldpc_reference.py` [repo-observed]
    - `qary_ldpc.py` [repo-observed]
    - `polar_existing.py` [repo-observed]
    - `base.py` [repo-observed]
  - `comparison_bench/src/comparison_bench/pipeline/` with:
    - `run_ir_benchmark.py` [repo-observed]
    - `merge_with_security.py` [repo-observed]
  - `comparison_bench/src/comparison_bench/sweep/` with:
    - `runtime.py` [repo-observed]
    - `common.py` [repo-observed]
    - `rows.py` [repo-observed]
  - `comparison_bench/tests/` with six current test files [repo-observed]
- Historical context from prior work:
  - real-data imported Polar baseline was matched against a real result root under a legacy Windows data path. [memory-derived]
  - representative sidecar frame batches were built from real paired-symbol sidecar exports. [memory-derived]

## 3. Execution Environment
- Expected OS: Windows host environment is directly observed; WSL support is also explicitly provisioned via `wsl-env.sh`. [repo-observed]
- Expected Python/MATLAB/Octave/other runtime:
  - Python with `numpy`, `pandas`, `numba`, `tqdm` from root `requirements.txt` [repo-observed]
  - optional comparison dependencies: `pyyaml`, `pyarrow`, `pytest` from `comparison_bench/requirements-comparison.txt` [repo-observed]
  - compiled Polar binaries exist under `src/reconciliation/cpp_polar/` (`.dll`, `.exe`) [repo-observed]
  - MATLAB/Octave usage is [uncertain]; no current comparison harness file directly invokes them, but prior planning discussed possible external hooks. [memory-derived]
- Known environment constraints:
  - PowerShell profile loading emits execution-policy warnings in this environment. [memory-derived]
  - git commit/stage operations may fail due to `.git/index.lock` permission issues. [memory-derived]
  - git push over HTTPS to GitHub can fail with `SSL certificate OpenSSL verify result: unable to get local issuer certificate (20)`; fixed on this host via `git config --global http.sslBackend schannel` (global host-level config, not repo content — other hosts may need the same fix). [memory-derived]
  - pytest cache/temp directories can trigger permission-denied warnings. [memory-derived]
  - some outputs may fall back from parquet to pickle if parquet support is missing. [repo-observed]
- WSL migration notes:
  - `wsl-env.sh` sets `PROJECT_DATA_ROOT`, `PROJECT_RESULTS_ROOT`, `TMPDIR`, and `PIP_CACHE_DIR` to POSIX-style defaults. [repo-observed]
  - For WSL work, prefer `/mnt/...` or project-relative POSIX paths, not Windows absolute paths. [repo-observed]
  - Historical Windows data/result paths should be treated as provenance only, not future execution defaults. [repo-observed]

## 4. Main Workflows

### Workflow: original Polar end-to-end pipeline
- entrypoint: `experiments/run_e2e_pipeline.py` [repo-observed]
- input: raw `.ttbin`-derived or paired-sequence materialization inputs [repo-observed]
- output: Polar evaluation artifacts under repository result directories [repo-observed]
- safe smoke command: [uncertain]
- heavy command, if known: [uncertain]
- do-not-run-by-default commands:
  - `experiments/run_e2e_pipeline.py` on raw data, because this is the core heavy baseline workflow and should not be rerun casually. [repo-observed]

### Workflow: original real Polar sweep / max PIE
- entrypoint: `experiments/run_real_polar_max_pie.py` [repo-observed]
- input: cached grid/source tables or materialized real-data intermediates [memory-derived]
- output: Polar result tables such as `polar_diag_summary.csv`, `polar_e2e_results.csv`, or related CSVs [memory-derived]
- safe smoke command: [uncertain]
- heavy command, if known: [uncertain]
- do-not-run-by-default commands:
  - `experiments/run_real_polar_max_pie.py` against raw or large real-data inputs by default. [repo-observed]

### Workflow: replay / security / audit aggregation
- entrypoint:
  - `tools/longrun_build_replay_index.py` [repo-observed]
  - `tools/longrun_run_actual_ir_replay.py` [repo-observed]
  - `tools/longrun_build_finite_key_audit_table.py` [repo-observed]
  - `tools/longrun_build_security_master_table.py` [repo-observed]
- input: prior Polar logs/results and audit/replay inputs [repo-observed]
- output: audit/shadow/master security summaries under result directories [repo-observed]
- safe smoke command: [uncertain]
- heavy command, if known: [uncertain]
- do-not-run-by-default commands:
  - any `longrun_*` or `minrerun_*` scripts unless explicitly asked. [repo-observed]

### Workflow: real-data / synthetic comparison benchmark
- entrypoint:
  - `python -m comparison_bench.src.comparison_bench.cli.build_dataset` [repo-observed]
  - `python -m comparison_bench.src.comparison_bench.cli.run_benchmark` [repo-observed]
  - `python -m comparison_bench.src.comparison_bench.cli.compare_methods` [repo-observed]
- input:
  - paired symbol tables with normalized columns [repo-observed]
  - or sidecar directories containing `a_eff.npy`, `b_eff.npy`, and optional `sidecar_meta.json` [repo-observed]
  - benchmark YAML configs under `comparison_bench/configs/` [repo-observed]
- output:
  - `comparison_bench/outputs_comparison/ir_benchmark_results.csv` [repo-observed]
  - `comparison_bench/outputs_comparison/ir_frame_results.parquet` [repo-observed]
  - `comparison_bench/outputs_comparison/run_manifest.json` [repo-observed]
  - `comparison_bench/outputs_comparison/ir_method_summary.csv` [repo-observed]
- safe smoke command:
  - `python -m comparison_bench.src.comparison_bench.cli.smoke_test --config comparison_bench/configs/benchmark_synth.yaml` [repo-observed]
- heavy command, if known:
  - `python -m comparison_bench.src.comparison_bench.cli.run_benchmark --config comparison_bench/configs/benchmark_realdata.yaml` [repo-observed]
- do-not-run-by-default commands:
  - full real-data benchmark on all sidecars or all frames unless explicitly requested. [memory-derived]

### Workflow: v3 IR method parameter sweeps
- entrypoint:
  - `python -m comparison_bench.src.comparison_bench.cli.run_cascade_param_sweep --config comparison_bench/configs/cascade_param_sweep.yaml` [repo-observed]
  - `python -m comparison_bench.src.comparison_bench.cli.run_layered_ldpc_param_sweep --config comparison_bench/configs/layered_ldpc_param_sweep.yaml` [repo-observed]
  - `python -m comparison_bench.src.comparison_bench.cli.run_qldpc_param_sweep --config comparison_bench/configs/qldpc_param_sweep.yaml` [repo-observed]
  - `python -m comparison_bench.src.comparison_bench.cli.run_ir_v3_master --config comparison_bench/configs/ir_methods_v3_master.yaml` [repo-observed]
- input:
  - frame-batch parquet built under `comparison_bench/outputs_comparison/` [repo-observed]
  - sweep YAML configs [repo-observed]
- output:
  - `cascade_param_sweep_results.csv` and frame/diagnostic companions [repo-observed]
  - `layered_ldpc_param_sweep_results.csv` and frame/diagnostic companions [repo-observed]
  - `qldpc_param_sweep_results.csv` and frame/diagnostic companions [repo-observed]
  - `run_errors_ir_v3.csv` [repo-observed]
  - `ir_v3_run_manifest.json` [repo-observed]
- safe smoke command:
  - there is no dedicated tiny smoke CLI; the lightest current path is to restrict configs before running. [uncertain]
- heavy command, if known:
  - `python -m comparison_bench.src.comparison_bench.cli.run_ir_v3_master --config comparison_bench/configs/ir_methods_v3_master.yaml` [repo-observed]
- do-not-run-by-default commands:
  - v3 master runner or any full representative/all-point sweep in a fresh environment without confirming output policy first. [repo-observed]

### Workflow: v3 report table generation
- entrypoint: `python -m comparison_bench.src.comparison_bench.cli.make_report_tables --config comparison_bench/configs/ir_methods_v3_master.yaml` [repo-observed]
- input: existing v3 sweep CSV outputs [repo-observed]
- output: `comparison_bench/outputs_comparison/report_tables_v3/` CSV tables [repo-observed]
- safe smoke command: same as entrypoint, but only after sweep outputs already exist. [repo-observed]
- heavy command, if known: same as entrypoint; relatively lighter than the sweep commands. [repo-observed]
- do-not-run-by-default commands:
  - none obvious beyond not pointing it at incomplete/missing sweep outputs. [repo-observed]

## 5. Data and Result Policy
- raw data directories:
  - raw real data is external to the repo. Historical provenance includes a legacy Windows path under `D:\Data\Raw Data\QKD_Loss\TypeII_776.1nm_3s` [memory-derived, legacy Windows path]
  - WSL default logical data root is `PROJECT_DATA_ROOT=/mnt/d/Data` from `wsl-env.sh`. [repo-observed]
- result/output directories:
  - original result area: `results/` [repo-observed]
  - comparison result area: `comparison_bench/outputs_comparison/` [repo-observed]
- checkpoint directories:
  - `comparison_bench/outputs_comparison/` contains run manifests and append-only sweep outputs, effectively acting as benchmark checkpoints. [repo-observed]
  - external run/checkpoint roots may exist outside the repo; treat them as [uncertain] unless explicitly mounted. [uncertain]
- files/directories agents must not overwrite:
  - `results/` and anything under it unless explicitly requested. [repo-observed]
  - `comparison_bench/outputs_comparison/` existing benchmark results, diagnostics, manifests, test fixtures, or summaries unless explicitly requested. [repo-observed]
  - raw data outside the repo. [repo-observed]
  - original Polar outputs imported by `polar_existing` bridge. [repo-observed]
- preferred new-output naming convention:
  - new comparison outputs should stay under `comparison_bench/outputs_comparison/` and use additive names consistent with current patterns such as `*_results.csv`, `*_frame_results.parquet`, `*_diagnostics.csv`, `*_manifest.json`, or nested subdirectories like `report_tables_v3/`. [repo-observed]
- Evidence-size rule (effective 2026-09-20) [decision]: a single committed evidence file must stay ≤ ~2 MB (2 MiB); larger frozen artifacts go under `workspace/` (git-ignored) and only their digest + summary line are committed. Per-packet size exceptions end (P20Q's 2.25 MB exception was the last). AGENTS.md formalization to ride the next OpenSpec change.

## 6. Schema and Interface Contract
- CSV columns that must not silently change:
  - normalized input columns: `frame_id`, `pair_idx`, `alice_symbol`, `bob_symbol` [repo-observed]
  - propagated metadata columns: `loss_db`, `dimension`, `bin_width_ps`, `n_eff_pairs`, `threshold_ps`, `effective_pairing_window_ps`, `processing_rule_version`, `pairing_path_tag` [repo-observed]
  - benchmark output columns include at least:
    - `dataset_id`, `data_mode`, `source_path`, `loss_db`, `dimension`, `bin_width_ps`, `n_eff_pairs`, `frame_len_symbols`, `frame_len_bits`, `method`, `method_variant`, `method_status`, `processing_rule_version`, `pairing_path_tag`, `threshold_ps`, `effective_pairing_window_ps`, `n_frames_total`, `n_frames_attempted`, `n_frames_success`, `n_frames_failed_decode`, `n_frames_failed_verify`, `accepted_frame_fraction`, `rejected_frame_fraction`, `raw_ser`, `raw_ber`, `post_ir_ser`, `post_ir_ber`, `leak_EC_actual_bits`, `leak_EC_per_frame`, `leak_EC_per_input_bit`, `beta_eff_empirical`, `runtime_s`, `throughput_input_bits_per_s`, `throughput_output_bits_per_s`, `notes`, `backend_status`, `error_message`, `real_ir_success`, `success_classification` [repo-observed]
  - frame-level output columns include at least:
    - `dataset_id`, `method`, `frame_idx`, `decode_success`, `verify_success`, `raw_frame_ser`, `raw_frame_ber`, `post_frame_ser`, `post_frame_ber`, `leak_bits_frame`, `iterations_used`, `runtime_ms` [repo-observed]
- JSON/YAML keys that must not silently change:
  - `datasets`, `methods`, `global` in benchmark YAMLs [repo-observed]
  - `output_dir`, `max_workers`, `frame_batch_path`, `polar_results_root`, `data_mode`, `frame_len_symbols`, `max_frames_per_dataset` in real-data benchmark YAML [repo-observed]
  - sweep config sections: `cascade`, `layered_ldpc`, `qldpc`, plus `cascade_config`, `layered_ldpc_config`, `qldpc_config` in the v3 master YAML [repo-observed]
- CLI arguments that must not silently change:
  - `build_dataset.py`: `--input`, `--output`, `--dimension`, `--frame-len-symbols`, `--dataset-id`, `--scan-sidecars` [repo-observed]
  - `build_representative_subset.py`: `--input`, `--output` [repo-observed]

  - `run_benchmark.py`: `--config` [repo-observed]
  - `compare_methods.py`: `--input`, `--output` [repo-observed]
  - `smoke_test.py`: `--config` [repo-observed]
  - `run_cascade_param_sweep.py`: `--config` [repo-observed]
  - `run_layered_ldpc_param_sweep.py`: `--config` [repo-observed]
  - `run_qldpc_param_sweep.py`: `--config` [repo-observed]
  - `run_ir_v3_master.py`: `--config` [repo-observed]
  - `make_report_tables.py`: `--config` [repo-observed]
- config keys that must not silently change:
  - method names: `polar_existing`, `cascade_lite`, `layered_ldpc_lite`, `qldpc_reference` [repo-observed]
  - v3 sweep keys including `block_size_schedule`, `num_passes`, `permutation_mode`, `seed`, `verify_mode`, `frame_caps`, `parity_fraction`, `max_iter`, `osd_order`, `bp_method`, `mapping`, `llr_mode`, `bitplane_rate_mode`, `check_fraction`, `row_weight`, `decoder`, `channel_model` [repo-observed]
- function signatures that must not silently change:
  - `FrameBatch`, `IRRunConfig`, `IRRunResult` dataclass fields in `comparison_bench/src/comparison_bench/types.py` [repo-observed]
  - `load_pairs_table(path: Path) -> pd.DataFrame` [repo-observed]
  - `normalize_pair_columns(df: pd.DataFrame) -> pd.DataFrame` [repo-observed]
  - `build_frame_batch(...) -> FrameBatch` [repo-observed]
  - `locate_existing_polar_outputs() -> list[Path]` and `run_polar_existing(batch: FrameBatch, cfg: IRRunConfig) -> IRRunResult` [repo-observed]
- output file naming conventions:
  - base benchmark outputs: `ir_benchmark_results.csv`, `ir_frame_results.parquet`, `run_manifest.json`, `ir_method_summary.csv` [repo-observed]
  - v3 outputs: `cascade_param_sweep_results.csv`, `layered_ldpc_param_sweep_results.csv`, `qldpc_param_sweep_results.csv`, `run_errors_ir_v3.csv`, `ir_v3_run_manifest.json`, `report_tables_v3/*.csv` [repo-observed]

## 7. Baseline and Scientific Semantics
- baseline algorithms:
  - original imported baseline: `polar_existing` [repo-observed]
  - executable classical baseline: `cascade_lite` [repo-observed]
  - executable binary LDPC baseline: `layered_ldpc_lite` [repo-observed]
  - q-ary reference baseline: `qldpc_reference` [repo-observed]
- current assumptions:
  - original Polar code is frozen and must be treated as read-only baseline logic. [repo-observed]
  - comparison layer is outer-wrapper only; it should read existing Polar outputs first and only use CLI mode if explicitly configured. [repo-observed]
  - `cascade_lite` is an internal simplified multi-pass parity/bisection baseline, not a full industrial Cascade transcript implementation. [repo-observed]
  - `layered_ldpc_lite` is a binary bit-plane baseline using `ldpc.BpOsdDecoder` when available, with explicit failure statuses rather than fake success. [repo-observed]
  - `qldpc_reference` currently represents a reference-grade q-ary decoder path, not a production qLDPC system. [memory-derived]
- high-risk variables:
  - `dimension` / `q` [repo-observed]
  - `bin_width_ps` [repo-observed]
  - `frame_len_symbols` [repo-observed]
  - `parity_fraction` [repo-observed]
  - `max_iter` [repo-observed]
  - `mapping` (`gray` vs `natural`) [repo-observed]
  - `llr_mode` and `bitplane_rate_mode` in layered LDPC sweeps [repo-observed]
  - `block_size_schedule`, `num_passes`, and `permutation_mode` in Cascade sweeps [repo-observed]
- known coupling/confounding factors:
  - raw SER and dimension are strongly coupled to decode success on real-data representative points. [memory-derived]
  - imported `polar_existing` point-level results are not always frame-identical to executable baseline frame subsets. [memory-derived]
  - leakage numbers are method-specific decompositions and should only be compared when the decomposition semantics remain consistent. [repo-observed]
  - sidecar-derived frame batches depend on `a_eff.npy` / `b_eff.npy` plus sidecar metadata, so path/layout assumptions matter. [repo-observed]
- metrics that must preserve meaning:
  - `raw_ser`, `raw_ber`, `post_ir_ser`, `post_ir_ber` [repo-observed]
  - `leak_EC_actual_bits`, `leak_EC_per_frame`, `leak_EC_per_input_bit` [repo-observed]
  - `accepted_frame_fraction`, `rejected_frame_fraction` [repo-observed]
  - `n_frames_success`, `n_frames_failed_decode`, `n_frames_failed_verify` [repo-observed]
  - `beta_eff_empirical` must remain derived from leakage and error inputs, not hand-filled. [repo-observed]

## 8. Known Issues and Fragile Points
- path issues:
  - original and comparison workflows have historical Windows-specific path usage; these must be translated deliberately for WSL. [repo-observed]
  - `polar_existing_bridge.py` still contains a legacy Windows default for `DEFAULT_POLAR_RESULTS_ROOT`; treat that as historical provenance, not a future path contract. [repo-observed, legacy Windows path]
- environment issues:
  - git commit/stage may fail because `.git/index.lock` cannot be created. [memory-derived]
  - PowerShell profile warnings are noisy but not necessarily fatal. [memory-derived]
  - optional parquet/YAML dependencies may be missing, causing fallback behavior. [repo-observed]
- data format issues:
  - sidecar directories are directory-based datasets, not flat CSV files. [repo-observed]
  - `load_pairs_table()` supports CSV, parquet/pickle, and sidecar directories; unsupported formats will fail. [repo-observed]
  - comparison outputs also contain test fixtures and temporary pytest artifacts under `comparison_bench/outputs_comparison/`; do not treat those as production outputs. [repo-observed]
- numerical/scientific interpretation risks:
  - `polar_existing` imported results may legitimately contain `NaN` for fields absent from source tables, especially leakage/runtime supplements. [memory-derived]
  - `qldpc_reference` results must not be described as full industrial qLDPC results unless method status and notes explicitly justify that. [repo-observed]
  - `cascade_lite` strong performance in representative sweeps should not be overinterpreted as final paper-grade evidence without broader sweeps. [memory-derived]
  - `layered_ldpc_lite` failure regions may reflect multiple causes: high raw SER, short frame length, parity allocation, or bit-plane independence assumptions. [memory-derived]
- long-running commands:
  - any `longrun_*`, `minrerun_*`, or `routeA_*` tooling under `tools/` [repo-observed]
  - real-data benchmark sweeps and `run_ir_v3_master` can be substantial even with representative subsets. [repo-observed]

## 9. Agent Operating Constraints
- minimal patch only. [repo-observed]
- no broad refactoring of original repository structure. [repo-observed]
- no raw data modification. [repo-observed]
- no result overwrite in `results/` or `comparison_bench/outputs_comparison/` unless explicitly asked. [repo-observed]
- no baseline semantic change to the copied Polar workflow. [repo-observed]
- no schema change unless explicitly requested. [repo-observed]
- WSL/POSIX path default for future harness and agent docs. [repo-observed]
- treat legacy Windows paths as provenance only; do not bake them into new harness defaults. [repo-observed]
- preserve current CLI names, config keys, output file names, and CSV field names. [repo-observed]
- do not silently convert `reference`, `stub`, `unavailable`, `decode_failed`, or `no_verified_success` into `ok`. [memory-derived]
- follow AGENTS.md §5.7 Research Code Engineering Policy: local research code, simplest scientifically correct implementation, no unrequested defensive machinery (checksums, locking, retries, etc.). [repo-observed]

## 10. Unknowns To Verify
- Which original `docs/` files inside this repo are authoritative versus copied from another upstream state. [uncertain]
- Whether MATLAB/Octave is actually required anywhere in this repository copy. [uncertain]
- Whether the original Polar front-half and replay/security scripts are fully runnable in WSL without binary/toolchain adjustments. [uncertain]
- Whether `src/reconciliation/cpp_polar/` binaries are Windows-only in practice or have a portable rebuild path documented elsewhere. [uncertain]
- Whether all existing v3 comparison outputs should be treated as canonical or as exploratory benchmark artifacts. [uncertain]
- Whether any additional AGENTS-style repository guidance already exists outside the scanned paths. [uncertain]
- Whether the external real raw-data root used historically is mounted in the target WSL environment. [uncertain]
- Whether AGENTS.md §10.1 items 7 and 11 should be revised to remove hash wording
  ("self-hashes recomputed", "hashes for untracked files"): this conflicts with
  §5.7 and the 2026-08-06 no-hash amendment, and is a pending main-thread
  decision (noted in `evidence/v10_protocol_amendment_no_hash_v1.json`);
  revising AGENTS.md would require a separate OpenSpec change. [decision-pending]

## 11. Multi-Agent Workflow Files

### Created (2026-06-15)
- `AGENTS.md` — repository-level agent rules (baseline protection, output policy, schema stability, path discipline, agent constraints, OpenSpec workflow). [created]
- `docs/decision-log.md` — durable decisions and rejected alternatives. [created]
- `docs/troubleshooting.md` — reusable failure modes and fixes. [created]
- `openspec/project.md` — project-level context for OpenSpec change management. [created]
- `openspec/changes/real-ir-success-first/` — active change proposal details. [created]
- `CURRENT_TASK.md` — current active documentation/workflow task. [created]
- `RUN_COMMANDS.md` — curated smoke/benchmark/do-not-run command list. [created]
- `REVIEW_CHECKLIST.md` — review checklist for baseline protection and schema stability. [created]
- `AGENT_HANDOFF.md` — concise handoff note for the next agent. [created]
- `comparison_bench/src/comparison_bench/metrics/success.py` — success classification module. [created]
- `comparison_bench/src/comparison_bench/cli/build_representative_subset.py` — representative subset extractor. [created]
- `comparison_bench/configs/benchmark_representative.yaml` — representative subset benchmark config. [created]
- `comparison_bench/tests/test_success_classifier.py` — success classification unit tests. [created]
- `docs/real-ir-success-audit-20260615.md` — audit report summarizing baseline evaluations on representative frames. [created]

### Current OpenSpec state (verified 2026-07-25)
- Phase 0 reconciliation is `docs/openspec-phase0-reconciliation-20260725.md`.
  All five historical IR changes remain active: `real-ir-success-first` has
  32/34 evidenced tasks; optimization has 14/14 tasks but lacks its written
  512/1024-symbol evidence; expanded evidence has 19/20; evidence-package
  has 26/26 tasks but lacks clean direct fixed-path pytest and a before/after
  non-modification proof; group-meeting has 21/29 and lacks its frame-count,
  expected-config/test, and clean-full-suite requirements. Do not archive any
  historical change from artifact presence alone. [repo-observed]
- `final-ir-method-selection` was archived on 2026-07-25 at
  `openspec/changes/archive/2026-07-25-final-ir-method-selection/`; its
  canonical specification is `openspec/specs/final-ir-method-selection/spec.md`.
  It is the bounded comparison protocol that
  ranks only executable `cascade_lite` and `layered_ldpc_lite`; qLDPC remains
  `reference_only`, and `polar_existing` is historical, non-frame-identical
  context. It requires group-disjoint tuning/confirmation, one frozen global
  configuration per candidate, retained attempted failures, unranked
  method-specific leakage, bounded stopping, and a non-numerical Route A
  field-compatibility gate. [repo-observed]

### Final-IR authoritative evidence chain (verified 2026-07-25)
- v1 data lock is
  `comparison_bench/outputs_comparison/final_ir_method_selection/20260725_v1/`.
  The locked domain is real d=1024, 64-symbol frames, dataset raw SER
  [0.20, 0.30), with 60 tuning frames from
  `real_typeii_20db_d1024_bw200_blk0` and 60 confirmation frames from
  `real_typeii_20db_d1024_bw180_blk0`; the groups are disjoint. Verify
  read-only with `python -m comparison_bench.src.comparison_bench.cli.lock_final_ir_data --verify --manifest comparison_bench/outputs_comparison/final_ir_method_selection/20260725_v1/data_lock_manifest.json`.
  [repo-observed]
- v1 Phase-3 outputs are invalid for decisions (`invalid_run_notice.json`).
  v2 is the sole authoritative bounded run:
  `.../20260725_v2/`; it froze Cascade `[12,6,24,13]`, 4 passes,
  seeded-random gray, and LDPC parity 1.0, 50 iterations,
  `bsc_estimated`/`uniform` gray before confirmation. It retained all 60
  attempts per candidate: Cascade 60/60 independently verified successes and
  LDPC 59/60. [repo-observed]
- v3 audit is superseded by its additive notice. v4 is authoritative:
  `.../20260725_v4_audit/`. Its read-only audit verifies the same 60 locked
  confirmation keys, frozen corrected-grid configurations, all status
  denominators, and evidence hashes. One Cascade-only discordance gives the
  pre-registered exact two-sided paired p-value 1.0 at alpha 0.05; outcome is
  strictly `no_decision`, not a winner. Claims do not extend beyond the locked
  domain, do not rank cross-method leakage, and do not select Polar or qLDPC.
  [repo-observed]
- The Route A compatibility gate is `fail`: comparison outcomes lack the
  documented universal-hash verification, leakage-accounting, and
  correctness-budget fields. No Route A numerical rerun or formal-proof claim
  was made. [repo-observed]
- Phase-5 verification: five-module `py_compile`, focused unittests 7/7,
  read-only v1/v4 verification, and safe comparison pytest 22/22 passed with
  `test_evidence_package.py` excluded because it writes a fixed tracked path.
  External pytest temp/permission behavior remains an infrastructure caveat;
  the six tracked `workspace/pytest-tmp/` deletions are pre-existing and must
  remain untouched. [repo-observed]

### Formal IR qualification evidence chain (verified 2026-07-25)
- Formal candidates are additive under
  `comparison_bench/src/comparison_bench/formal_ir/`; the
  frozen Polar pipeline and the `cascade_lite`/`layered_ldpc_lite` methods and
  their evidence remain unchanged. [repo-observed]
- The sole authoritative synthetic qualification is
  `comparison_bench/outputs_comparison/formal_ir_methods/20260725_v3_synthetic/`.
  Its strict read-only report promotes `cascade_formal_v1` in both strata
  (32/32 `verified_success` at p=.01 and p=.02). It does not promote
  `ldpc_formal_v1` (29/32 and 14/32); all 21 retained non-successes are
  `verify_failed`, with zero unclassified/internal/provenance/accounting
  failures. [repo-observed]
- The invalid real v1 root received only its additive invalid-lock notice and
  made zero formal-method calls. The sole authoritative real qualification is
  `comparison_bench/outputs_comparison/formal_ir_methods/20260725_v2_real_cascade/`:
  its strict verifier accepts exactly seven artifacts, its preflight passed
  29 tests with exit 0, and Cascade achieved 60/60 requested confirmation
  frames as `verified_success`, with union bound `3.2526065174565133e-18` and
  zero unclassified/internal/provenance/accounting failures. The resulting
  promotion is limited to d=1024, 64 symbols, bw120, frame SER `[.20,.30)`;
  LDPC was not run on real data. [repo-observed]
- Read-only verification commands (do not rerun the qualification runners):
  `python -m comparison_bench.src.comparison_bench.cli.run_formal_synthetic_qualification --output-dir comparison_bench/outputs_comparison/formal_ir_methods/20260725_v3_synthetic --verify`
  and
  `python -m comparison_bench.src.comparison_bench.cli.run_formal_real_qualification --output-dir comparison_bench/outputs_comparison/formal_ir_methods/20260725_v2_real_cascade --verify`.
  [repo-observed]
- Before any frame-identical Polar/Cascade/LDPC comparison, a separate
  LDPC-improvement OpenSpec change must obtain fresh synthetic and real LDPC
  promotion. Do not substitute a lite method or tune on confirmation data.
  [repo-observed]

### Formal LDPC v2 improvement evidence (verified 2026-07-26)
- Archived change is
  `openspec/changes/archive/2026-07-26-improve-formal-ldpc-v2/`. Additive
  `ldpc_formal_v2` freezes
  nine policies: rate margin 0/1/2 crossed with `OSD_0/0`, `OSD_CS/1`, and
  `OSD_CS/2`. The n=64 nested codebook has 16 masters per plane and selected
  prefix matrices 32/40/48/56. Its structural screening is a proxy, not
  verified decoding evidence. [repo-observed]
- The v1 integration root `20260725_v1_ldpc_v2_synthetic` is invalid: the
  v1 codebook verifier makes all 576 policy outcomes plus 64 associated
  outcomes `unsupported_domain`. Its seven artifacts remain immutable and an
  additive invalid notice records the exclusion. [repo-observed]
- Fresh v2 plan SHA256 is
  `c0770b5b1c80c277448ca832b01a5dd6d8413df78870fa040c6546d0098ede18`, with
  zero old/new CSPRNG overlap. Strict verification passed. Development results
  are 26/64 (margin 0), 33/64 (margin 1), and 56/64 (margin 2), identical for
  every OSD variant; the selected policy is rate margin 2 with `OSD_0/0`.
  [repo-observed]
- Confirmation records 28/32 at p=.01 and 29/32 at p=.02, seven
  `verify_failed`, and verification invoked for all 64 outcomes, with zero
  unclassified/internal/provenance/accounting failures. Status is
  `non_promoted`; no real lock or run is authorized, and confirmation must not
  be used to tune. [repo-observed]
- Artifact SHA256 prefixes: plan `c077...`, codebook `360b77...`, outcomes
  `9adb0...`, policy `303919...`, transcript `4b438...`, manifest `d185fc...`,
  report `53fbe5...`. Final checks: v2-focused 25 passed plus 5 subtests,
  general 52 passed/11 skipped, formal-real 12 passed, strict verification
  passed, and frozen `src/`, `experiments/`, `tools/`, and `results/` diff is
  empty. Terra low only implemented frozen tasks and specified tests; the main
  thread retained planning and acceptance. [repo-observed]
- Short- and medium-term engineering work is complete with reproducible
  evidence, but LDPC has not met promotion; the fair three-method comparison
  remains blocked. [repo-observed]

## 11. Parallel Binary and Nonbinary LDPC Direction (2026-07-26)

- Binary and nonbinary LDPC are now planned as independent parallel research
  lanes. The detailed handoff is
  `comparison_bench/docs/ldpc_parallel_handoff.md`. [repo-observed]
- Binary starts from immutable, non-promoted `ldpc_formal_v2` evidence and
  targets longer frames, deterministic QC/PEG/protograph families,
  incremental redundancy, and per-bit-plane soft information. Existing
  confirmation evidence cannot be used for tuning. [repo-observed]
- Nonbinary N0 field-backend work is implemented under the independent
  `nbldpc_formal_v1` identity in
  `comparison_bench/src/comparison_bench/formal_ir/nonbinary_field.py`.
  It pins deterministic polynomial-basis GF(2^m) arithmetic for powers-of-two
  q through 1024, canonical field metadata/IDs, and a read-only fail-closed
  preflight. `qldpc_reference` remains unchanged and reference-grade.
  This proves field-backend feasibility only, not decoder feasibility,
  qualification, promotion, or comparison readiness. [repo-observed]
- The two lanes require separate OpenSpec changes, codebooks,
  development/confirmation splits, artifacts, leakage accounting, verifiers,
  and promotion decisions. Only independently promoted methods may enter a
  later frame-identical comparison. [repo-observed]

## 12. Binary LDPC Long-Frame v3 Phase 1 (2026-07-26)

- Active OpenSpec change:
  `openspec/changes/binary-ldpc-long-frame-and-ir-v3/`. [repo-observed]
- Candidate-only `codebook_long_v3.py` supports n=256/512/1024, ten planes,
  four deterministic candidates, and nested 1/2, 5/8, 3/4, 7/8 check
  prefixes. HGF2V3 bytes and a reconstruction-verified manifest bind all 120
  candidate identities. [repo-observed]
- Actual-rank, no-zero/duplicate-column, weight-bound, exact 4-cycle, and
  `column_pair_extrinsic_degree_v1` proxy tests passed. Main-thread evidence:
  focused 4 passed in 10.88 s; v2 regression 7 passed/1 skipped in 81.41 s;
  compilation/diff checks passed and frozen directories were unchanged.
  [repo-observed]
- Phase 1 is engineering evidence only: no FER, candidate selection, decoder,
  confirmation/real data, qualification, or promotion. Next freeze a
  sacrificed-development FER evaluation contract. [repo-observed]

## 13. Binary LDPC Long-Frame v3 Phase 2 (2026-07-26)

- `long_v3_development.py` implements exact sacrificed p=.01/.02 generation,
  canonical seed/source hashes, pinned BP+OSD-0 metadata, four-prefix
  incremental evaluation, retained statuses, and exact four-candidate
  selection. It is in-memory and writes no result artifact. [repo-observed]
- Selection is frozen as worst-stratum successes, total successes, syndrome
  disclosure, then candidate ID. Runtime and structural proxies are excluded.
  Tests independently verify the data/policy/selection hash preimages and
  fail-closed malformed-grid behavior. [repo-observed]
- Main-thread evidence: focused 5 passed in 0.53 s; Phase1/v2 regression
  11 passed/1 skipped in 92.68 s; compilation and frozen-directory checks
  passed. [repo-observed]
- Phase 2 used injected test decoders only. No pinned-backend development
  sweep, candidate FER evidence, selection, confirmation, real data,
  qualification, or promotion exists yet. Next freeze a bounded backend
  preflight/pilot. [repo-observed]

## 14. Binary LDPC Long-Frame v3 Phase 3A Pilot (2026-07-26)

- A single in-memory pinned-backend pilot ran exactly once at
  n=256/plane0/candidate0/p=.01 on 16 sacrificed frames. Backend was
  `ldpc==2.4.1`; exit 0; stderr empty; process 0.3227008000249043 s; external
  wall 1.0 s. [repo-observed]
- Outcomes were 16/16 exact success, terminal p050=15/p0625=1, and 2080 total
  syndrome bits. No file was written and no candidate was selected.
  [repo-observed]
- This clears one-slice backend feasibility only. It is not comparative FER,
  n=512/1024 evidence, qualification, or promotion. Next freeze an immutable,
  verifier-bound full sacrificed-development sweep contract. [repo-observed]

## 15. Binary LDPC Long-Frame v3 Phase 3B Tooling (2026-07-26)

- Additive runner/verifier tooling now freezes a 3840-row, 30-selection
  sacrificed-development grid with prepare/execute no-overwrite lifecycle,
  six canonical artifacts, code/backend/hash DAG, failure finalization, and
  production/test isolation. [repo-observed]
- Read-only verification reconstructs deterministic source provenance and the
  accepted candidate-selection function, but does not rerun LDPC decoding.
  Its success is artifact integrity only. [repo-observed]
- Main-thread evidence: Phase3B focused 3 passed in 12.30 s; all long-v3
  12 passed in 12.94 s; v2 regression 7 passed/1 skipped in 81.34 s;
  compilation/diff/frozen-directory checks passed. Test artifacts are under
  `workspace/formal_long_v3_phase3b_tests_run3`. [repo-observed]
- No production plan or 3840-row sweep exists yet. Next create and inspect one
  fresh plan, then separately authorize its single execution. [repo-observed]

## 16. Binary LDPC Long-Frame v3 Phase 3C Development Evidence (2026-07-26)

- Immutable development root:
  `comparison_bench/outputs_comparison/formal_ir_methods/20260726_v1_binary_ldpc_long_v3_development/`.
  Execute ran once in 28.9 s with 3840 outcomes/30 selections; strict verifier
  ran once in 11.2 s, exit 0, without decoder reexecution. [repo-observed]
- All 3840 per-plane candidate outcomes were
  `development_exact_success`. Selected per-plane mean syndrome bits:
  n256 129.0/134.6, n512 260.4/280.4, n1024 541.6/635.2 for p001/p002.
  [repo-observed]
- The current per-plane terminal is chosen using Alice-truth exact equality.
  This is a sacrificed-development oracle and not a deployable stopping signal;
  its leakage and 100% result are not qualification evidence. [repo-observed]
- Next aggregate ten planes into global incremental rounds with one
  frame-wide Toeplitz verification tag, count slowest-plane syndrome/tag
  leakage, then select the formal length/policy before fresh confirmation.
  [repo-observed]

## 17. Binary LDPC Long-Frame v3 Phase 4 Frame Development (2026-07-26)

- Ten-plane read-only aggregation produced 96 q=1024 development frames and
  modeled one 64-bit frame-wide Toeplitz tag over at most four global rounds.
  Aggregation SHA256 is
  `029e33c42f254e40725a370065d30196216501085d5def5f0f0c935aca6c933c`.
  [repo-observed]
- All lengths retained 16/16 success in both strata. Mean frame key-disclosure
  fractions p001/p002: n256 .5640625/.68125; n512 .590625/.7546875; n1024
  .6625/.8421875. [repo-observed]
- Frozen development choice is n=256 with tuple
  `[-16,-32,.68125,.62265625,256]`. This is sacrificed-development design
  selection only; the stopping tag was modeled, not executed. [repo-observed]
- Next implement actual n256 ten-plane formal decoding, locked Toeplitz
  seed/tag, transcript, caps and fail-closed statuses before any fresh
  qualification. [repo-observed]

## 18. Binary LDPC Long-Frame v3 Phase 5 Formal Method (2026-07-26)

- `formal_ir/ldpc_v3.py` implements `ldpc_formal_v3` for exactly q=1024,
  n=256 and ten MSB-first Gray planes with frozen candidates
  `[1,0,1,2,0,0,1,3,2,3]`. [repo-observed]
- It reconstructs canonical long-v3 matrices, validates a self-hashed
  sacrificed calibration, requires `ldpc==2.4.1`, and decodes all ten planes
  in four possible synchronous incremental-syndrome rounds. [repo-observed]
- One 64-bit frame-wide Toeplitz tag is disclosed once and checked only after
  complete rounds. The decoder receives no tag/match or Alice truth. Strict
  transcript validation binds terminal prefix, syndrome/tag/seed disclosure,
  epsilon, caps, backend and frozen selection. [repo-observed]
- Main-thread evidence: focused 6 passed in 2.15 s; long-v3 regression 13
  passed in 16.12 s; v2 regression 7 passed/1 skipped in 81.27 s;
  compilation/diff/frozen-directory checks passed. [repo-observed]
- This accepts method engineering only. No confirmation runner/artifact,
  strict package verifier, qualification, promotion, real-data result, or fair
  comparison eligibility exists. Phase 6 must be planned and frozen before
  execution. [repo-observed]

## 19. Binary LDPC v3 Phase 6 TTBIN Bridge and Synthetic Stop (2026-07-26)

- Phase 6A read-only bridge binds the real 20 dB main/chunk TTBIN and exact
  q=1024 sidecars, selects 64 bw100 calibration plus 32 each bw120/180/200
  reserved confirmation frames, and reconstructs source/lock/calibration
  hashes. Calibration plane p_hat ranges from .000366 to .122620.
  [repo-observed]
- Immutable synthetic package
  `comparison_bench/outputs_comparison/formal_ir_methods/20260726_v1_binary_ldpc_v3_synthetic/`
  was prepared, executed, and strictly verified exactly once. Verification
  accepted 64 outcomes and returned `decoder_reexecution=false`.
  [repo-observed]
- Calibrated confirmation achieved 3/32 and 1.25x stress achieved 1/32 versus
  31/32 gates. The other 60 outcomes are `verify_failed`; forbidden
  internal/provenance/accounting failures are zero. [repo-observed]
- Binary v3 is non-promoted. Phase 6C real tooling/output was not created and
  is locked. Do not tune or retry from confirmation. A successor requires a
  new OpenSpec improvement and fresh synthetic confirmation. [repo-observed]
- Nonbinary N1 is implemented in
  `comparison_bench/src/comparison_bench/formal_ir/nonbinary_codebook.py` as a
  pure in-memory n=64 family: one deterministic 32x64 mother matrix and exact
  16/24/32 ordered prefixes, with three SHA256-derived cyclic shifts,
  explicit nonzero GF(q) coefficients, an identity parity half, and rank
  calculated with the pinned N0 GF(q) arithmetic. [repo-observed]
- Canonical `NBLDPC1` bytes include the full field representation,
  construction, dimensions, topology, coefficients, seed, and ordering.
  Golden codebook/manifest SHA256 tests plus reconstruction-based tamper
  checks cover field, coefficient, rank, prefix, codebook-ID, and manifest-ID
  drift. Focused N0+N1+qLDPC tests passed 22/22; the selected
  formal/nonbinary/qLDPC regression passed 29/29. [repo-observed]
- N1 is structural rank/hash evidence only. It does not establish a soft
  decoder, distance/FER performance, qualification, promotion, outputs, or
  comparison readiness. N2 must freeze decoder and formal accounting
  contracts before implementation or dependency selection. [repo-observed]
- Nonbinary N2 is implemented in
  `comparison_bench/src/comparison_bench/formal_ir/nonbinary_qspa.py` as a pure
  full-message probability-domain FFT-QSPA feasibility decoder. It consumes
  Bob symbols, Alice's public syndrome, and verified N1 codebooks; its public
  decoder signature has no Alice truth or callback. q=4 coefficient/coset
  check updates match brute-force convolution, and q=1024 executes inside the
  frozen n=64/check/iteration/16-MiB declared dense-message bounds.
  [repo-observed]
- `syndrome_consistent` is deliberately separate from locked Toeplitz
  verification. Symbols map to fixed-width MSB-first bits; syndrome
  disclosure is checks*log2(q), invoked verification tags add their exact
  length, and public-control bits remain separate. N0-N2 plus qLDPC tests
  passed 35/35; selected formal verification/Cascade/LDPC regressions passed
  17 with 2 skipped. [repo-observed]
- N2 is bounded engineering feasibility only. It does not prove general
  correction, FER/performance, calibration, synthetic/real qualification,
  promotion, outputs, production readiness, or comparison eligibility. N3
  requires planner-owned pre-registration before execution. [repo-observed]

## 20. Nonbinary LDPC v2 Development Non-Readiness (2026-07-26)

- `nbldpc_formal_v2` Phase 1/2 was accepted with 21 focused tests; the joint
  N0-N3/v2/formal regression passed 86 with 8 skipped. [repo-observed]
- The immutable root
  `comparison_bench/outputs_comparison/formal_ir_methods/20260726_v2_nbldpc_synthetic/`
  contains one reviewed plan (112 frames, 24 policies, 1216 unique seeds,
  overlap zero), one execution, and one successful strict full replay.
  [repo-observed]
- The selected tempered+damped QC48 policy used margin 8, max_iter 10, and
  32/40 checks for p=.20/.30. Development achieved 0/24 and 5/24 verified
  successes against a 22/24-per-stratum readiness floor. Confirmation was
  never generated or executed. [repo-observed]
- Status is `non_promoted_development`, not confirmation FER or real-data
  evidence. No rerun, tuning, N4 sidecar adapter, or `.ttbin` processing is
  authorized. [repo-observed]

## 21. Binary LDPC v4 Development Backend Stop (2026-07-27)

- `binary-ldpc-adjacent-channel-v4` implements deterministic adjacent-channel
  modeling, 40 anchored sparse binary codebooks, a fixed 648-bit formal
  method, immutable development/synthetic/real packages, and read-only
  source/transcript/gate verifiers. Focused main-thread acceptance passed
  15+8+3+4 tests; cross-version regression passed 119 with 10 skipped.
  [repo-observed]
- Sole production development evidence:
  `comparison_bench/outputs_comparison/formal_ir_methods/20260727_v1_binary_ldpc_v4_development/`.
  Plan content SHA256 is
  `af644e2f4a3dab596f34350b18ecfb1df56cb46b93670cb16e89f3ca1ae67c5e`.
  The read-only verifier returned verified/completed with
  `decoder_reexecution=false`, but readiness was false. [repo-observed]
- Nominal and stress each retained 512 denominators, zero frame successes,
  and 5,120 selected-plane `development_decoder_error` outcomes. This is an
  implementation failure and must not be interpreted as FER or code quality.
  [repo-observed]
- A no-decode diagnostic confirmed the backend mismatch: `ldpc==2.4.1`
  rejects NumPy-array `error_channel` with `expected list`, while the same
  vector converted by `.tolist()` constructs. The formal v4 path converts it;
  the frozen development path did not. [repo-observed]
- No v4 production synthetic or real directory exists. The frozen stop rule
  forbids editing/tuning/rerunning this package. A continuation needs a new
  versioned OpenSpec implementation-correction lane and fresh evidence; fair
  Cascade/LDPC/Polar comparison remains blocked. [decision]

## 22. Binary LDPC v4 Backend Correction Readiness (2026-07-27)

- `binary-ldpc-v4-backend-correction-v1` added only versioned development
  files. It converts the frozen Bob-conditioned float64 error channel to a
  Python list at the `ldpc==2.4.1` constructor boundary; historical v4 source
  and evidence hashes remain unchanged. [repo-observed]
- Immutable corrected package:
  `comparison_bench/outputs_comparison/formal_ir_methods/20260727_v2_binary_ldpc_v4_development/`.
  Plan content SHA256 is
  `1e208832ac421e69c0488d33e39953755ba487c25f9bf9db43bdda79cc53daaf`.
  Prepare/execute/read-only verification each ran once; verification returned
  completed/verified, `decoder_reexecution=false`, and readiness true.
  [repo-observed]
- Frozen development results are 510/512 adjacent nominal and 511/512
  adjacent stress, with zero forbidden failures. Selected candidates are
  `[0,0,0,0,0,0,2,0,2,2]`. This clears only the 495/512 sacrificed-
  development screen. [repo-observed]
- No corrected-v4 synthetic or real production output was created. Synthetic
  qualification still requires a fresh main-thread plan audit and one
  independent execution; comparison eligibility and real `.ttbin` claims
  remain unestablished. [decision]

## 23. Binary LDPC v4 Corrected Synthetic Promotion (2026-07-28)

- Immutable package
  `comparison_bench/outputs_comparison/formal_ir_methods/20260728_v2_binary_ldpc_v4_synthetic/`
  strictly verified with 256 outcomes, no decoder reexecution, and promotion:
  nominal 127/128, stress 126/128, zero forbidden failures. [repo-observed]
- Plan content SHA256 is
  `02a198ea4d03ae4d7dad7db6e2b4099e85f5b75c0d8acad34e8449d67cb769fb`.
  Fresh roots/seeds have zero overlap with v3 and development. Do not rerun or
  tune from this confirmation. [repo-observed]
- Real qualification remains unrun. Current bw120/bw180/bw200 sidecars each
  have 117 complete frames; excluding 32 v3-reserved identities leaves 85,
  below the frozen 128 by 43 per stratum. Real prepare must remain blocked
  until traceable same-domain source data fills that deficit. [decision]
- Prefer at least 64 newly supplied complete frames per real stratum to absorb
  duplicate/incomplete rejection. Preserve 128 denominators and 126/128 gates;
  do not reuse reserved frames or weaken the claim to fit current data.
  [decision]

## 24. Binary LDPC v4 Real-Source Intake Acceptance (2026-07-28)

- The only other local 20 dB tree is a byte-identical raw-capture copy. Its
  main/chunk SHA256 pair equals the registered capture, so it is not new
  statistical capacity. [repo-observed]
- The Phase 4 intake layer now builds and reconstructs a no-overwrite,
  self-hashed multi-acquisition source extension. It rejects duplicate raw
  pairs and frame payloads, binds exact q=1024 bw120/bw180/bw200 sidecars,
  counts only complete 256-symbol frames, and performs no decoding.
  [repo-observed]
- Main acceptance passed 3 source, 5 real, 7 bridge/source, and 25
  backend/development/formal-real tests. Historical v3/development source
  hashes remain exact and no real production directory exists.
  [repo-observed]
- Real prepare remains unauthorized until a genuinely distinct 20 dB
  acquisition supplies enough validated capacity and a main-thread-reviewed
  extension manifest. The 128 denominators and 126/128 gate remain frozen.
  [decision]

## 25. Project-Wide Delegation Workflow (2026-07-29)

- Substantial delegated implementation starts from one complete frozen task
  packet: file scope, functionality, full test/evidence matrix, commands,
  artifacts, stop rules, and return conditions. [decision]
- The main thread owns planning, requirements, thresholds, OpenSpec,
  acceptance, and scientific conclusions. The implementation subagent is an
  operator and returns only a complete candidate or a concrete reproducible
  blocker; partial “still incomplete” reports are not completion. [decision]
- Main review normally occurs at spec freeze, complete candidate delivery, and
  independent acceptance. Tests progress from focused development to combined
  focused candidate to main regression/compile/frozen-hash/no-output review.
  [decision]
- Verifier acceptance matrices must pre-register byte drift, locally re-signed
  semantic tampering, re-signed manifest/index tampering, and deep
  cross-artifact reconstruction. Known Windows ACL failures require an
  explicitly writable non-production test root. [decision]
- These coordination optimizations do not alter prepare/review/execute/verify,
  immutable failure retention, scientific thresholds, or no-rerun/no-tuning
  boundaries. [decision]
- Acceptance items use stable IDs. Successor evidence machinery starts from
  the nearest accepted predecessor and an explicit delta list. [decision]
- Tests use T0 compile/structural, T1 focused, T2 fake qualification/replay,
  and T3 regression stages; T2/T3 run only at milestones and test-only calls
  explicitly pass fake runners. [decision]
- Windows tests use additive workspace UUID roots with pytest cache disabled.
  Process termination requires positive ownership; dirty-worktree acceptance
  includes untracked hashes, frozen diffs, and output-root checks. [decision]
- Handoffs report only changed files, commands/results, concrete blockers, and
  remaining acceptance IDs; they do not repeat durable project context.
  [decision]

## 26. Binary LDPC v4 16 dB Transfer Result (2026-07-29)

- The sole 16 dB transfer package completed and strictly verified with all 384
  outcomes: bw120 125/128, bw180 128/128, bw200 128/128, and zero forbidden
  failures. Because every layer required 126/128, the package is immutable
  `non_promoted_transfer`. [repo-observed]
- Read-only verification reported no decoder reexecution and changed none of
  the nine files. Plan content SHA256 is
  `ddbf41983d866ce5d320404323ff319b64a867f8f8c32185a890ab7baf97b2da`;
  source-lock content SHA256 is
  `5c654377751cea776a203269b8213959313aa9a0be738935816d36b52181ea87`.
  [repo-observed]
- The 16 dB evidence must not be tuned or rerun and does not promote 16 dB or
  20 dB. A separately scoped unchanged-method 10 dB transfer is frozen under
  `binary-ldpc-v4-10db-transfer-qualification-v1`; if promoted, its claim is
  limited to that independent 10 dB acquisition. [decision]

## 27. Binary LDPC v4 10 dB v1 Prepare Rejection (2026-07-29)

- The v1 10 dB prepare was rejected before execute because validation included
  its own newly written plan in the prior-real root set. It contains exactly
  plan and lock, no outcomes. Preserve it as `invalid_pre_execute`; plan file
  SHA256 is `dae9d27a068bf9b15f25ae684bd3cf290623524b0e92af8989869579b0ac523c`
  and lock file SHA256 is
  `6596316074b0e473de26ba44a87556016f23b082dc36239e06a65fa4e7d11baf`.
  [repo-observed]
- A versioned correction must exclude only the current plan from prior-plan
  discovery while continuing to bind and forbid the invalid v1 roots/seeds.
  No scientific inputs or gates may change. [decision]

## 28. Binary LDPC v4 10 dB v2 Result and v5 Route (2026-07-29)

- The corrected v2 10 dB package strictly verified all 384 outcomes but was
  non-promoted: bw120 125/128, bw180 127/128, bw200 128/128, zero forbidden
  failures. Plan content SHA256 is
  `c6f3592ac24fd32ac136d16f06fd88157757216a81c40643e86d0ba3882af2f6`.
  [repo-observed]
- All four failures were retained `verify_failed` after complete syndrome
  disclosure and Toeplitz mismatch. v4 fixed-rate robustness, not source,
  backend, accounting, or resource failure, is the remaining issue.
  [repo-observed]
- Do not test progressively easier losses until one passes. The v5 route
  pre-locks disjoint unused 10 dB development and confirmation frames, screens
  frozen stronger-OSD/incremental-redundancy policies on development, then
  requires fresh synthetic promotion before one sealed real qualification.
  [decision]

## 29. Nonbinary LDPC v3 Covered-Layered Result (2026-07-30)

- The sole v3 synthetic package was planned once, executed once, and strictly
  replay-verified once. The selected layered-l075 margin-8 policy used 32/40
  checks and passed development readiness at 23/24 for p=.20 and 24/24 for
  p=.30. [repo-observed]
- Sealed confirmation was materialized only after readiness and achieved
  32/32 for p=.20 and 30/32 for p=.30, with zero prohibited failures. The
  frozen 31/32-per-stratum gate failed by one p=.30 frame, so the package is
  immutable synthetic non-promotion evidence. [repo-observed]
- Strict verification returned `verified=True`, `run_status=completed`,
  `promoted=False`. Plan SHA256 is
  `0f35b8679166599efb294caee21822156ba971bec6271875cf55516523cfdee1`;
  selected-policy SHA256 is
  `6193f92af05c1d3a5145cbe31c95a4d20f1eaf5a09970936613c326cc1c59a28`.
  [repo-observed]
- Do not rerun, tune confirmation, overwrite evidence, build N4, access
  sidecars, or process `.ttbin`. Real-data work requires promoted synthetic
  confirmation and a new approved OpenSpec change. [decision]

## 30. Nonbinary LDPC v4 Incremental-Redundancy Result (2026-07-31)

- The sole v4 IR package was planned, executed, and strictly replay-verified
  once. Verification returned `verified=True`, `run_status=completed`,
  `promoted=False`. [repo-observed]
- Development selected `nbldpc_v4_ir_warm`: 64/64 at p=.20 and 63/64 at
  p=.30. Sealed confirmation achieved 128/128 and 120/128; all eight misses
  were p=.30 `decode_failed`, with zero prohibited failures. [repo-observed]
- The package is immutable at
  `comparison_bench/outputs_comparison/formal_ir_methods/20260731_v4_nbldpc_ir_synthetic/`.
  Do not rerun, tune, overwrite, build N4, access sidecars, or process `.ttbin`.
  Any successor requires new OpenSpec, fresh synthetic splits, and a
  pre-registered method change. [decision]
- Reusable process lesson: historical qualification suites whose own official
  roots now exist can correctly reject a test replay as identity reuse. Retain
  that evidence and use isolated algorithm regressions; never edit immutable
  outputs or weaken freshness guards merely to make an old suite green.
  [repo-observed]

## 31. Binary LDPC v5 Development, Synthetic, and Sealed Real Promotion (2026-08-01/2026-08-12)
- Phase 2 sacrificed development selected V5-C2: 1536/1536 verified success
  (512/stratum across bw120/bw180/bw200 real 10 dB frames), zero forbidden
  failures, 1 round, no fallback. Leakage 648 bits/frame = 2.531 b/symbol =
  0.253 b/input bit (h1 syndrome 584 + verification 64); real raw SER
  bw120 0.1228 / bw180 0.0833 / bw200 0.0767; 204.7 s total. Package immutable
  at comparison_bench/outputs_comparison/formal_ir_methods/
  20260731_v1_binary_ldpc_v5_development/. [repo-observed]
- Robustness evidence committed to comparison_bench/docs/ldpc_v5_robustness/:
  E1 new-seed rerun 768/768, E3 model-consistent (SER 0.243) 768/768,
  E2 uniform OOD control 0/1152 as expected. [repo-observed]
- Phase 3 fresh synthetic confirmation (2026-08-01): 256/256 verified success
  (nominal 128/128 + stress_125 128/128), zero forbidden failures,
  promoted=true, ready_for_real_qualification=true, decoder_reexecution=false.
  Package immutable at .../20260801_v1_binary_ldpc_v5_synthetic/; plan sha256
  c91171dcdde8c1cf5fb31cc21cbad72115756fff034763ce93c75cbef17c10ab. [repo-observed]
- Phase 4 sealed real qualification COMPLETED and PROMOTED (2026-08-12):
  384/384 verified_success — bw120/bw180/bw200 each 128/128, zero forbidden
  failures; report `promoted=true`, `run_status=completed`,
  `decoder_reexecution=false`. Official package (ten files, run_id
  `binary_ldpc_v5_real_qualification_v1`, plan_sha256
  `a79cd16f19b968364a4c46fb4887f933eeb472e45c19d098a938ae5dc58ad01b`,
  report_sha256
  `18b5566ed636a79473ff7290cb55d90d4ab20a170895b53f786ea2455ad953d5`):
  comparison_bench/outputs_comparison/formal_ir_methods/
  20260801_v2_binary_ldpc_v5_real/. Execute ~5m12s, read-only verify ~4m29s,
  detached background process. Chain: partition lock (20260731) → v5
  development (V5-C2, 1536/1536) → v5 synthetic (256/256, 20260801) → v5 real
  (384/384, 20260801_v2), each once with read-only verification. [repo-observed]
- v4's two real transfers remain retained as non-promoted failure evidence
  (16 dB 125/128 and 10 dB v2 125/128, both below the 126/128 gate); v5 is
  the first all-green real 10 dB Type-II promotion. Do not tune or rerun
  them. [decision]
- Comparison eligibility updated (2026-08-12): binary LDPC v5 may participate
  in comparison within the promoted 10 dB Type-II q=1024 Gray 256-symbol
  bw120/bw180/bw200 domain only; all other domains and methods (v4, 16 dB,
  20 dB, other captures, nonbinary, Cascade/Polar) keep their prior status.
  A rate-adaptive successor requires a separate OpenSpec change. [decision]
- Polar numerical comparison remains blocked: results/ is empty in this
  checkout and polar_existing imports are historical, non-frame-identical,
  leakage NaN. No Polar-vs-v5 numeric claim is supportable. [repo-observed]
- Reusable process lessons (2026-08-12): (a) Long qualification stages
  (prepare/execute/verify, ~5-20 min) exceed subagent/session channel
  timeouts; run them as a detached background process (background bat +
  log-file polling) outside the opencode session. (b) Three latent production
  bugs (synthetic_dir directory semantics, generator empty-dict check,
  missing root_id) were masked by tests that mocked core functions
  (`_seed_schedule`, `_validate_roots`, `_validate_plan`) and surfaced only at
  production prepare; keep a real-path smoke in tests rather than mocking
  whole core paths, so such defects surface at T0/T1 instead of at sealed
  qualification time. [decision]

## 32. Nonbinary LDPC v5 Multistage Change Terminated — Four Routes Non-Promoted (2026-08-02)
- The v5 multistage change (formal-nonbinary-ldpc-v5-multistage-ir) ran all four
  pre-registered routes A/B/C/D, each planned once, executed once, and strictly
  replay-verified once; every route hit the same p=.30 tail pattern
  (promotion gates p=.20 128/128, p=.30 127/128) and is `promoted=false`.
  Per task 7.4 the change terminates with four immutable non-promoted
  packages: 20260731_v5a_nbldpc_multistage_synthetic (three-level warm IR),
  20260731_v5b_nbldpc_mother_synthetic (NBLDPC5B mother, zero w2/w3),
  20260731_v5c_nbldpc_decoder_synthetic (sched/EMS decoders),
  20260731_v5d_nbldpc_post_synthetic (list L=2 x top-8 + ADMM rho=1.0
  <=50-iteration post-processing over the v5c decoders). [repo-observed]
- Route D execution (HEAD 192f455): run_status=completed, readiness true,
  512 outcomes; strict replay returned {'verified': True,
  'run_status': 'completed', 'promoted': False} with an unchanged worktree.
  Evidence: evidence/v5d_acceptance_d1_d2.json and v5d_acceptance_c3_c4.json. [repo-observed]
- Route D implementation corrections (main-thread approved, recorded in the
  module docstring and decision-log 2026-08-02): the frozen x-update prior
  term sign was wrong (+prior/RHO; correct is x = z - lambda - prior/rho) —
  a q=4 brute-force experiment showed recovery 0% -> 87-100% after the fix;
  and the frozen z-update alternating projection onto {simplex AND
  output-sum=e_s} is a strict subset of the GF(q) check polytope (it forces
  all output symbols to s) and could not recover codewords — replaced by the
  per-bit parity-relaxation projection (bitwise-XOR linearization), 100%
  exact recovery in the same experiment. A _V5D_BY_V5C reverse map fixes the
  production trigger (post.start delegates v5c and the state carries the v5c
  policy id). [decision]
- Procedural deviation recorded: the v5d 7.3 plan was created before the
  D1/D2 acceptance evidence file; closed read-only at the same HEAD with the
  plan unchanged (see v5d_acceptance_d1_d2.json). [repo-observed]
- Bounds: list L=2, top-8 symbols, exactly 64 candidates, at most one round,
  syndrome filter; ADMM rho=1.0, <=50 iterations, deterministic init, no
  random source; verification cap 3; no additional syndrome/tag disclosure. [repo-observed]
- N4, sidecar access, .ttbin processing, real-data qualification, and any
  comparison claim remain locked. A nonbinary successor requires a new
  OpenSpec change with fresh development and confirmation data; neither
  codebook redesign (B), decoder-family change (C), nor list/ADMM post (D)
  closed the p=.30 tail at the 128/128 floor. [decision]
- Reusable process lesson (already recorded at section 30): official roots
  existing in the shared output root make the same-run-id lane test suite
  self-conflict on identity freshness; that is the designed anti-replay
  guard, not a regression. [repo-observed]

## 33. Nonbinary LDPC v6 Long-Block Engineering Candidate Accepted (2026-08-02)

- Engineering candidate of change `formal-nonbinary-ldpc-v6-long-block`
  implemented and independently reviewed ACCEPTED (V6-50) 2026-08-02 at HEAD
  `a9c3c5d8696ad9fa967e2d5d8b9905c5a55c8344`. Seven new files:
  `formal_ir/nonbinary_v6_codebook.py`, `formal_ir/nonbinary_v6_long.py`,
  `formal_ir/nonbinary_v6_development.py`,
  `cli/run_formal_nonbinary_v6_development.py`,
  `tests/test_nonbinary_v6_codebook.py`, `tests/test_nonbinary_v6_long.py`,
  `tests/test_nonbinary_v6_development.py`, plus
  `evidence/v6_engineering_acceptance.json` under the change directory. No
  existing file modified; frozen `src/`/`experiments/`/`tools/`/`results/`
  diff empty; no official v6 output root exists under
  `comparison_bench/outputs_comparison/formal_ir_methods/`. [repo-observed]
- Method identity `nbldpc_formal_v6_long`: GF(1024), n=1024 symbols, two
  deterministic degree-2 PEG codebooks (1024,320) for p=.20 and (1024,480)
  for p=.30; check degrees 6/7 and 4/5; full GF rank 320/480; zero parallel
  edges; frozen seeds {320: 2026080200, 480: 2026080300} from a one-time
  bounded rank search, never re-searched at runtime; magic `b"NBLDPC6\n"`.
  [repo-observed]
- Decoder: ascending-row layered FFT-QSPA, lambda .75, max 50 iterations,
  single-threaded (workers=1 by construction), whole-graph syndrome check
  after every iteration, 64-bit Toeplitz verification only after syndrome
  consistency, syndrome disclosure 10*m bits plus 64 key-dependent tag bits,
  no fallback, fail-closed on NaN/Inf/non-finite/wrong length/malformed
  syndrome/allocation cap (dense message bound 50,331,648 bytes <= 64 MiB).
  [repo-observed]
- Acceptance: T0 16, T1 38, T2 6 (fake lifecycle + strict read-only replay
  with explicit fake runner; production decoder never entered), T3 51
  v5-regression (N0 field, N1 codebook, N2 qspa, v3 core, v5a codebook, v5a
  core); all 8 tamper classes rejected (byte, semantic self-hash, manifest
  link, source identity, transcript recanonicalized, leakage, gate
  rebuilding/promotion forgery); CLI default action is plan, execute is a
  hard SystemExit(2) refusal. Evidence JSON binds HEAD, source hashes,
  command exit codes, tier results, A01-A10. [repo-observed]
- Diagnostic observation, strictly diagnostic-only and NOT FER/qualification
  evidence: a full-rate random p=.20 frame does not converge within 50
  iterations (~85 s per frame); 1-2 planted errors and noiseless frames
  converge in 1 iteration. Consistent with the change's weak-baseline
  hypothesis. [repo-observed]
- Boundary state: V6-51 (reviewed sacrificed development plan with fresh
  roots) NOT authorized; V6-52 successor choice (qualification / n=4096 /
  multiplicative repetition / GF(32)xGF(32)) NOT made; no confirmation
  material, no real data, no promotion. v5 change remains terminated with
  four immutable non-promoted packages. [decision]
- Process note: memory-agent triage delegation returned empty three times
  without writing; the durable section above was appended directly by the
  orchestrator from verified session evidence. [decision]

## 34. Nonbinary LDPC v6 Canary 0/4 Both Strata — Long-Block Baseline Stopped (2026-08-02)

- Main-thread decision: no large-scale v6 development run. A small sacrificed
  8-frame canary (4 p=.20 + 4 p=.30, fixed (1024,320)/(1024,480) codebooks,
  lambda .75, max_iter 50, workers=1, fresh roots 202608024000/202608024100,
  no confirmation) was staged via a minimal additive CANARY config in
  `nonbinary_v6_development.py` (production execution authorized only for
  CANARY config with explicit workspace output; CONFIG 64-frame plan path and
  official-root lock preserved). Canary tests 8/8 new + 46 total + 51 v5
  regression passed. [repo-observed]
- Canary plan created once and read-only reviewed READY-FOR-SINGLE-EXECUTION
  (evidence/v6_51_canary_plan_evidence.json), executed exactly once (exit 0,
  450.9 s) and strict-replayed exactly once (exit 0, 518.6 s). Result: 0/4
  verified success in BOTH strata; all 8 frames `decode_failed` at
  max_iter=50 with zero forbidden statuses; run_status
  `development_completed`, promoted false. Package retained at
  `workspace/nbldpc_v6_canary_b01c42a5dee14ed0913e78d60944cc38/canary_plan`;
  no official root under `formal_ir_methods/` created.
  Evidence: evidence/v6_51_canary_execution_addendum.json. [repo-observed]
- Pre-registered gate fired: any stratum 0/4 -> stop the degree-2 n=1024
  long-block baseline, do NOT go to n=4096, prefer multiplicative repetition
  (2,3) mother code. V6-52 chose multiplicative repetition as the single
  successor; a new OpenSpec change must be proposed before implementation.
  [decision]
- Scientific note (diagnostic only): even the p=.30 stratum at 480 checks
  (4.6875 bits/symbol disclosed vs 3.88 entropy) failed 0/4 in 50 iterations
  on full-rate random frames; noiseless and 1-2 planted-error frames converge
  in 1 iteration. Consistent with a structurally weak degree-2 long-block
  baseline, not a tuning issue; canary is sacrificed and must not be tuned or
  rerun. [repo-observed]
- tasks.md V6-51/V6-52 marked complete with gate outcome; v6 change now has
  only the successor-change proposal as open work. [decision]

## 35. Nonbinary LDPC v7 Successor Ladder — All Four Routes failed_canary, Ladder Exhausted (2026-08-02..04)

- Change `formal-nonbinary-ldpc-v7-successor-ladder` freezes the ordered
  route ladder R1A -> R1B -> R2 -> R3 with one shared controller
  (`formal_ir/nonbinary_v7_ladder.py`, hash-bound advance, no confirmation
  path, exactly-once, no-rerun, gates: canary 0/4 in either stratum ->
  `failed_canary`; development ready = per-stratum >=15/16 verified + zero
  forbidden + strict replay + disclosure <=8.75 bits/symbol excluding tag +
  median <=120 s/frame). All v7 evidence lives in
  `openspec/changes/formal-nonbinary-ldpc-v7-successor-ladder/evidence/`;
  all v7 plans/packages live under fresh `workspace/nbldpc_v7_*` roots; no
  official `formal_ir_methods` v7 directory exists. [repo-observed]
- R1A (identity `nbldpc_formal_v7_r1a_mr0`): GF(1024) n=256 (2,3) PEG mother,
  m=170 (168 degree-3 + 2 degree-4 checks, seed 2026080400), flooding
  FFT-QSPA primary, max_iter 100. Engineering accepted (T0 19/T1 64/T2 11/
  T3 97). Sacrificed 4+4 canary executed once + strict-replayed once (exit 0,
  111.0 s / 108.8 s): 0/4 + 0/4 verified, 8/8 `decode_failed` -> canary gate
  fires -> `failed_canary`, frozen; 16+16 not eligible. Package at
  `workspace/nbldpc_v7_r1a_canary_af8ff2e751cf433ba74deb74bbe1deba/canary_plan`.
  [repo-observed]
- R1B (identity `nbldpc_formal_v7_r1b_mr1`): exact R1A mother under new
  identity + one multiplicative repetition (deterministic nonzero GF(1024)
  multipliers, seed 2026080401, rate 1/6 nominal), prior-combining decoder,
  same syndrome 1700 bits + tag. Engineering accepted (T0 15/T1 76/T2 17/
  T3 119). Sacrificed 4+4 canary executed once + strict-replayed once (exit 0,
  59.3 s / 59.6 s): p=.20 3/4, p=.30 0/4 -> gate fires on p=.30 ->
  `failed_canary`, frozen; 16+16 not eligible. Multiplicative repetition
  improved p=.20 but did not close the p=.30 tail. Package at
  `workspace/nbldpc_v7_r1b_canary_a209a853f5e34de69bf930deb60d5673/canary_plan`.
  [repo-observed]
- R2 (identity `nbldpc_formal_v7_r2_qsc_de`): faithful q-ary density
  evolution validated against published vectors (q=2 BSC (3,6) ~0.084;
  BEC (3,6)=0.429438, (3,4)=0.647426, (4,8)=0.383441, (4,6)=0.506132; q=4
  exhaustive checks), bounded search <=32 distributions (degrees 2..8, mean
  check degree <=12), per-stratum n=1024 PEG codebooks with 321 (p=.20) /
  458 (p=.30) checks, layered FFT-QSPA max_iter 100. One frozen-vector
  correction recorded ((3,4) mislabel). Engineering accepted (T0 32/T1 100/
  T2 24/T3 142). Sacrificed 4+4 canary executed once + strict-replayed once
  (exit 0, 1311.2 s / 1308.5 s): 0/4 + 0/4 verified, 8/8 `decode_failed` ->
  gate fires -> `failed_canary`, frozen; 16+16 not eligible. Package at
  `workspace/nbldpc_v7_r2_canary_d6c752a0772043768a1ca88a1ca63ed3/canary_plan`.
  [repo-observed]
- R3 (identity `nbldpc_formal_v7_r3_gf32x2`): reversible 10-bit -> high/low
  5-bit split (split roundtrip SHA256 `4716bf82...`), two GF(32) n=1024 codes
  m0=m1=404/558, layer-0-first with layer-1 priors ONLY from
  Bob/public/verified layer-0, joint 64-bit tag, flooding damped EMS nm=32
  (=q, the exact min-sum GF(32) update, exhaustively validated; FFT-QSPA
  oracle test-only), max_iter 100, disclosure 3.945/5.449 bits/symbol
  excluding tag. Engineering completed (2026-08-04): T0 19/T1 105/T2 33/
  T3 179, independent review 10/10 PASS
  (evidence/v7_r3_engineering_acceptance.json; schema v7_r3_engineering_v1;
  manifest_id b052a92748119b57d426fda4583d697f6577e6761e2b52332fee9f6e13c57582;
  13 reused-source hashes unchanged; check-count freeze m0=m1=ceil(1.15*H_32(p)/5*1024)).
  Sacrificed 4+4 canary staged and reviewed READY-FOR-SINGLE-EXECUTION; a
  minimal canary-only authorization edit applied (run() + CLI + 2 tests;
  post-edit hashes dd8ebe41.../68a17e92.../ad603eab...; first-half plan backed
  up, plan re-created in the same directory with 8 fresh 10303-bit seed
  records disjoint from all 10744 prior seed_ids, file SHA256
  43379354...fca2); executed once + strict-replayed once (exit 0, 668.8 s /
  663.4 s; git porcelain unchanged by replay): 0/4 + 0/4 verified, 8/8
  `decode_failed` (layer-0 failed every frame, 24 transcript events 3/frame,
  verification never invoked) -> gate fires -> `failed_canary`, frozen; 16+16
  development eligibility a separate main-thread decision, not claimed.
  Package at
  `workspace/nbldpc_v7_r3_canary_d006ec637ecb4b1e9463a7f4462eebf3/canary_plan`.
  [repo-observed]
- Process note: the Task tool intermittently returned empty results or
  cancelled/resumed sessions throughout this session (memory triage, several
  coder-fast engineering runs, reviewer-go returns); every completed stage was
  verified on disk before acceptance, and fresh-session retries succeeded for
  R1A/R1B/R2. R3 completion must resume from the existing partial state
  (resume session `ses_0391fa61bffeavVGlmfaDy7q1c` or fresh session with the
  partial-state inventory). [decision]
- Ladder closeout: V7-40 frozen ladder report (evidence/v7_ladder_report.md)
  at HEAD a9c3c5d8696ad9fa967e2d5d8b9905c5a55c8344 — first development-ready
  route NONE, `ladder_exhausted` TRUE, all four routes `failed_canary`, every
  failed artifact retained, no official v7 output root, no
  rerun/tuning/confirmation/real data/N4; no fourth route invented (R4
  proximal-ADMM never authorized). V7-41 independent acceptance PASS
  (main-thread-confirmed); V7-42 pending: stop unless a new qualification
  change is proposed. Decision-log entries for the R1A/R1B/R2/R3 canary
  non-promotions and the 2026-08-04 ladder-exhausted closeout exist.
  [decision]

## 36. Nonbinary LDPC v7 Ladder Exhausted — Durable Pattern And Stop Rule (2026-08-04)

- Every v7 route failed its sacrificed 4+4 canary (R1A 0/4+0/4; R1B p=.20 3/4,
  p=.30 0/4 tail; R2 0/4+0/4; R3 0/4+0/4) at max_iter=100, consistent with the
  v6 long-block baseline failure (0/4 both strata at max_iter=50, §34). The
  degree-2/3 PEG ensembles at these rates do not approach the needed
  correction under the frozen FFT-QSPA / EMS decoders on full-rate random
  frames; noiseless and 1-2 planted-error frames converge in 1-2 iterations,
  so this is a structural capacity gap, not a tuning issue. [decision]
- Do NOT re-run or tune any v7 route: the four canary packages are immutable
  non-ready evidence and the current rows are NOT tuning data. No fourth
  route was invented (R4 proximal-ADMM was never authorized). [decision]
- A nonbinary successor must be a NEW OpenSpec change with fresh development
  and confirmation data, new roots, and its code/rate/decoder change frozen
  before new development data. Qualification, promotion, and comparison
  eligibility claims remain unauthorized for every v7 route. [decision]
- No official `comparison_bench/outputs_comparison/formal_ir_methods/` v7
  directory exists before or after the ladder (recursive v7 scans clean);
  all v7 evidence lives under
  `openspec/changes/formal-nonbinary-ldpc-v7-successor-ladder/evidence/` and
  all canary packages under fresh `workspace/nbldpc_v7_*` roots.
  [repo-observed]

## 37. Nonbinary LDPC V8 Reference-Reproduction Correction (2026-08-04)

- New active change:
  `formal-nonbinary-ldpc-v8-reference-reproduction`. It is engineering and
  reference-only: error-domain syndrome algebra, an independent probability
  oracle, full-vector q-ary QSC Monte-Carlo density evolution, and one exactly
  sourced published reproduction. No V8 canary/development/confirmation/
  real/N4/comparison output is authorized. [decision]
- Scientific correction to §§35-36: V7 T0-T3 engineering suites passed, while
  the four scientific canaries failed. The failures reject the frozen
  implementations at their gates; they do not establish that nonbinary LDPC
  as a class has a structural capacity gap. [decision]
- R1B synthesized a second independently corrupted observation from Alice and
  combined it with Bob's observation. Preserve its package, but treat it only
  as an algorithmic diagnostic outside the project's one-Bob-observation plus
  public-disclosure reconciliation contract. [repo-observed, decision]
- R2 used a scalar two-level reliability surrogate rather than full q-entry
  message populations. Its variable update did not faithfully establish the
  paper contract of exact sampled degrees plus a channel term, and its degree
  perspective was not independently reproduced from a q-ary published target.
  Therefore R2 0/8 is evidence about that implementation, not closure of the
  literature's full-vector MC-DE route. [repo-observed, decision]
- V8 must reproduce a precisely cited q-ary QSC reference before any GF(1024)
  project adaptation. If exact degree vectors, perspective, channel convention,
  or target cannot be extracted, stop `implementation_blocked` rather than
  guessing. A future finite-length V9 requires a separate OpenSpec change and
  fresh data. [decision]

## 38. Nonbinary LDPC V8 Reference Reproduction — Implemented, Independently Accepted (2026-08-04)

- V8 reference-reproduction change implemented and INDEPENDENTLY REVIEWED
  ACCEPTED (reviewer-go, read-only, 2026-08-04) at HEAD
  a9c3c5d8696ad9fa967e2d5d8b9905c5a55c8344. Operator did not self-accept;
  V8-A01..A12 all pass (A12 satisfied by the independent review). [decision]
- Additive files only:
  `comparison_bench/src/comparison_bench/formal_ir/nonbinary_v8_error_domain.py`,
  `nonbinary_v8_reference.py`, `nonbinary_v8_mcde.py` + 3 tests
  (`test_nonbinary_v8_error_domain.py`, `test_nonbinary_v8_reference.py`,
  `test_nonbinary_v8_mcde.py`) + 7 evidence files under the change's
  `evidence/` dir (v8_engineering_acceptance.json schema v8_engineering_v1,
  v8_source_manifest.json, v8_reproduction_trace.json,
  v8_literature_provenance.json, v8_muller2024_table1_extract.txt SHA256
  d343f0204e87994e64efd32531bc12490fb4e7125cd90b52cfaf2397279b57bd,
  v8_v7_interpretation_audit.md, v8_v9_recommendation.md). [repo-observed]
- Semantics: error-domain contract d = H*(x+y) with reconstruction
  x_hat = y + e_hat; independent direct probability-domain oracle (pairwise
  XOR convolution + sparse support enumeration + brute-force tiny-code
  coset/MAP; imports only GF2mField from nonbinary_field; import-boundary
  enforced — no V1-V7 FFT/FWHT/check-update/decoder calls); full-vector QSC
  Monte-Carlo density evolution (length-q messages, edge-perspective degree
  distributions with tested node/edge conversion, exact sampled degrees per
  update, fresh channel message at every variable update, direct convolution
  with no FWHT, base-q mean message entropy convergence, seeded deterministic
  populations, fail-closed normalization); golden regressions detect the old
  R2 missing-channel and fixed-dv_max behavior. [repo-observed, decision]
- Tiers (pytest -p no:cacheprovider, fresh
  `workspace/nbldpc_v8_reference_9c3f51e2a74b48d9b6c0a5f8e1d23a4b` root):
  T0 11/0, T1 31/0, T2 3/0, T3 179/0 (frozen 16-file v5+v6+v7-R1A/R1B/R2
  regression subset). Reviewer independently re-ran T0/T1/T2: identical.
  [repo-observed]
- Published reproduction (single frozen run, no rerun/tuning): Muller et al.,
  "Efficient Information Reconciliation for High-Dimensional Quantum Key
  Distribution", Quantum Inf Process 23, 195 (2024), arXiv:2307.02225v2,
  Section 3.1 Table 1 row rate 0.75: q=4, DET published 0.069, edge-view
  lambda 0.107x+0.245x^3+0.192x^6+0.034x^9+0.207x^18+0.161x^25+0.049x^27
  (Eq. 13 exponents = degree-1, so DE degrees {2,4,7,10,19,26,28});
  concentrated two-point check distribution inferred from the fixed rate
  dc_mean = 1/((1-R)*sum(lambda_d/d)) = 24.3285893 -> {24,25} (documented
  inference). Frozen params: seed 2026080418, 20000 nodes, max 200
  iterations, entropy < 0.01 base-q for 20 consecutive iterations, p in
  [0.01,0.12] step 0.0025, frozen tolerance 0.015. Result:
  threshold_proxy 0.062421875, delta 0.006578 <= 0.015 -> PASS.
  [repo-observed, decision]
- Output policy: no V8 directory under
  `comparison_bench/outputs_comparison/formal_ir_methods/`; no
  canary/development/confirmation/real-data/N4/comparison execution; frozen
  src/experiments/tools/results and all V1-V7 files unchanged; nothing staged.
  Engineering/reference-only boundary: V8 authorizes only a separate future
  V9 proposal (paper-faithful syndrome reconciliation with reproduced
  ensemble and blind puncturing/shortening, fresh roots); no
  FER/readiness/qualification/promotion/comparison claim. [decision]
- Process note: tasks.md V8-50.7 checkbox remains pending until this memory
  section exists; docs/decision-log.md, CURRENT_TASK.md, and AGENT_HANDOFF.md
  already updated with the same verified facts. [repo-observed]

## 39. Nonbinary LDPC V8-60 Audit-Correction Close-Out (2026-08-04)

- V8-60 was a NON-TUNING FORMULA CORRECTION discovered by an independent audit
  of the accepted V8 candidate (2026-08-04); HEAD
  a9c3c5d8696ad9fa967e2d5d8b9905c5a55c8344 unchanged. Three corrections:
  (1) `concentrated_check_distribution` now solves the edge-perspective rate
  condition sum_j rho_j/j = (1-R)*sum_i lambda_i/i EXACTLY for adjacent check
  degrees {floor(dc), ceil(dc)} with w_lo = (target - 1/d_hi)/(1/d_lo - 1/d_hi),
  w_hi = 1 - w_lo, target = (1-R)*integral_lambda, dc = 1/target (integer dc
  degenerates to regular); the old mean-matched weights (w_lo = dc_hi -
  dc_mean) approximated it with ~1e-4 relative error; new public helper
  `reconstructed_rate()`; tests assert |reconstructed_rate - rate| <= 1e-12
  (5 configs). (2) REPRODUCTION_CITATION first author corrected to "Ronny
  Müller" (was wrong given name "Rasmus T. Müller"); full arXiv:2307.02225v2
  author list. (3) Tolerance re-derived with valid arithmetic:
  0.0005 + 0.00125 + 0.005 + 0.005 = 0.01175 <= 0.012 (frozen tolerance 0.012);
  the old claim 0.005+0.003+0.0025=0.015 was arithmetically invalid and is NOT
  reused. [decision]
- Corrective reference run executed EXACTLY ONCE with parameters frozen before
  the run: q=4, R=0.75, Muller et al. 2024 Table 1 row 0.75 (DET published
  0.069), concentrated rho {24: 0.6623423944, 25: 0.3376576056}, n_samples
  100000 and max_iter 150 (the paper's own MC-DE budget), seed 2026080418,
  p in [0.01, 0.12] step 0.0025, entropy < 0.01 base-q for 20 consecutive
  iterations. Result: threshold_proxy 0.062421875, delta 0.006578125 <= 0.012
  -> PASS. No rerun, no tuning. [repo-observed, decision]
- History preservation: evidence/v8_reproduction_trace.json preserved
  byte-identical (SHA256
  dd5678fd2d77b67dd7f3fc7ee221a49b0d33eab37ab5d226d96e6d243b071de3), marked as
  the pre-correction approximate trace via
  v8_reproduction_trace_precorrection_annotation.json;
  v8_engineering_acceptance.json NOT rewritten — its A12=blocked status is
  explicitly resolved by the main-thread evidence/
  v8_acceptance_closeout_addendum.json; v8_literature_provenance.json,
  v8_muller2024_table1_extract.txt, v8_v7_interpretation_audit.md,
  v8_v9_recommendation.md unchanged. [repo-observed]
- New evidence files: v8_reproduction_trace_corrected.json,
  v8_reproduction_trace_precorrection_annotation.json,
  v8_60_correction_evidence.json (formula/constants old->new, tolerance
  arithmetic, source-hash old->new), v8_independent_review_acceptance.json,
  v8_acceptance_closeout_addendum.json. v8_source_manifest.json regenerated
  with v8_60_delta; only two files changed: nonbinary_v8_mcde.py (new SHA256
  2c84a5ee76d09f4d6cea537289ff82d88ab19abd31d1a41951a7d24acdd66543) and
  test_nonbinary_v8_mcde.py
  (a508a4228ee06114424db2242b4db784bfa1b9cabcbae54f4cd7172ed988a81f).
  [repo-observed]
- Golden regressions: q=4 golden re-recorded under corrected rho {4: 1/6,
  5: 5/6} (same seed 2026080420; recording not tuning); omitted-channel/
  fixed_max tamper modes still differ (old-R2 detection preserved); q=8 golden
  byte-identical (regular {6:1.0}). [repo-observed]
- Tiers (V8-60.8 scope, NO T3 rerun): compile exit 0; T0 17/0; T1 32/0; T2 4/0
  (read-only reproduction-trace, source-manifest, no-production-runner,
  precorrection-preservation). Independent reviewer-go re-ran T1 32/0 and
  T2 4/0: identical; overall verdict ACCEPTED
  (evidence/v8_independent_review_acceptance.json), blocking findings none;
  non-blocking: v9 recommendation cites pre-correction numbers (superseded by
  corrected run), cosmetic duplicated line, pre-existing package __init__
  binding. [repo-observed, decision]
- Boundary: V8 remains engineering/reference-only; no V9, no canary/
  development/confirmation/real-data/N4, no official output, nothing
  staged/committed/pushed; only a separate future V9 OpenSpec proposal is
  authorized. [decision]

## 40. Nonbinary LDPC V9 GF(1024) Long-Block Route Frozen (2026-08-04)

- New active OpenSpec change:
  `formal-nonbinary-ldpc-v9-gf1024-long-ir`. V8-60's q=4 reproduction is a
  method/audit validation only; it is not GF(1024) threshold or finite-length
  FER evidence. [decision]
- Frozen autonomous state machine: V9A scalable full-vector GF(1024) WHT
  MC-DE and separate p=.20/.30 ensembles; robust f=1.15 conservative
  multi-seed thresholds must be >=.22/.32 before any codebook. Target f=1.08
  failure permits robust continuation only with
  `efficiency_target_not_met`. Rates/checks are computed as
  ceil(f*H_q(p)*n), with harmonic-exact edge-view rho. [decision]
- On V9A robust PASS only: V9B n=4096 irregular PEG/ACE-or-equivalent graph,
  nonzero GF(1024) labels, error-domain layered log-FFT-SPA (100-150 frozen
  iterations, workers=1), T0-T3 and independent acceptance, then one fresh
  4+4 canary and one strict replay. Gate: >=3/4 each stratum, zero forbidden,
  exact disclosure, median <=2h/superframe, peak RSS <=3GiB. [decision]
- On V9B PASS only: V9C n=16384 fresh 4+4 gate (>=3/4 each, median <=8h,
  <=3GiB), then n=32768 with exactly 32 ordered disjoint 1024-symbol synthetic
  constituents and fixed-rate syndrome/tag leakage. n=32768 uses one fresh
  4+4 canary, then on PASS one fresh 16+16
  development; ready gate >=15/16 each, zero forbidden, strict replay, median
  <=24h, <=3GiB. [decision]
- Every scientific stage is prepare -> independent read-only review -> exactly
  one execute -> exactly one strict replay. Failed evidence is immutable and
  stops the route; no tuning/rerun. V9 stops after the development decision;
  qualification/confirmation/real/N4/promotion/formal comparison require a
  separate future change. [decision]

## 41. Nonbinary V9 Freeze-Review Corrections (2026-08-04)

- V9A robust conservative multi-seed gates are >=.22/.32; target gates are
  >=.215/.32, with .215 below the p=.20 f=1.08 capacity threshold ~.21827.
  All four searches plus validation use one pre-frozen,
  independently reviewed, exactly-once deterministic execute and exactly-once
  strict replay. Target failure selects robust with
  `efficiency_target_not_met`; robust failure stops. [decision]
- All finite matrices require GF(1024) full row rank `rank(H)=m` before plan.
  n=4096/16384/32768 superframes bind respectively 4/16/32 ordered disjoint
  1024-symbol constituents with complete provenance and no cross-stage reuse.
  [decision]
- n=32768 canary has a hard 24h timeout per superframe and median <=16h advance
  gate. V9C is fixed-rate per stratum: `m=ceil(f*H_q(p)*n)`, syndrome leakage
  `L_recon=10*m`, separate fixed 64-bit tag, `L_total=10*m+64`; these are hard
  caps and no shortened/index/other reconciliation payload is allowed. Blind
  adaptation is prohibited in V9 and deferred to a future V10. [decision]

## 42. Nonbinary V12 Real Micro-Feasibility — source_partition_blocked (2026-08-13)

- Change: `formal-nonbinary-ldpc-v12-real-micro-feasibility`. Terminal state
  **source_partition_blocked** (`partition_state` and `plan_state`
  `source_partition_blocked`): 0 frames, 0 seed records, no decoder, no
  arrays. Implementation V12-I01..I05 complete; engineering acceptance
  V12-T0..T2 passed 41/41 tests (prepare-only production lane added to the six
  V12 files: `nonbinary_v12_real_micro.py` `prepare_production`,
  `partition.py` `prepare` with `production_prepare_authorized`, CLI `prepare`
  action). [repo-observed, decision]
- Root cause: the reconstructed traceable 10 dB pool (2304 rows, 768 per
  stratum incl. 768 bw200) is 100% covered by historical identities from the
  V4 10 dB/16 dB transfer locks (20260729_v1/v2) and V5
  development/partition role locks (20260731_v1): 2848 excluded frame + 2688
  excluded payload identities, zero eligible bw200 rows -> no source rows to
  partition. [repo-observed]
- Official preparation package (exactly 3 artifacts):
  `comparison_bench/outputs_comparison/formal_ir_methods/20260813_v2_nonbinary_v12_real_micro/`
  (`exclusion_manifest.json`, `partition_lock.json`, `pre_run_plan.json`;
  schemas `nbldpc_v12_exclusion_manifest_v1` / `partition_lock` / `plan`;
  run_id `nbldpc_v12_real_micro`). The v1 intermediate package
  (`20260813_v1_...`) was deleted by explicit user decision; v2's exclusion
  manifest (33 packages) still lists the deleted v1 package as a
  formal_package with 0 identities. [decision]
- V12-X01/X02 never ran (blocked — no eligible frames). V12-D01 recorded;
  V12-D02 completed 2026-08-13. `docs/decision-log.md`,
  `AGENT_HANDOFF.md`, `CURRENT_TASK.md`, and the §42 memory triage were
  updated. [repo-observed]
- Scientific implication: a fresh acquisition is required for any future
  four-frame bw200 canary; no successor/rerun/tuning/promotion is
  automatically authorized. Claim boundary: no finite decoder correction
  established for the existing pool. [decision]
- Procedural: the user's own binary V5 transfer-evaluation work
  (`ldpc_v5_transfer_evaluation.py`,
  `run_ldpc_v5_transfer_evaluation.py`,
  `outputs_comparison/transfer_evaluation/`) is user-owned/kept, out of V12
  scope, adjudicated as NOT a V12 operator violation — an evaluation-only,
  non-qualification retrospective transfer evaluation of frozen V5-C2
  (2026-08-12). [decision]
- Status supersession: the 2026-08-12 AGENT_HANDOFF current state (binary LDPC
  v5 REAL PROMOTED) is now previous state; V12 blocked supersedes it as
  current. The pre-existing 2026-08-13 mainline-fusion merge entry at the top
  of this file is unchanged and not duplicated here. [repo-observed]

## 43. Nonbinary LDPC V13 Existing-Data Diagnostics Plan (2026-08-14)

- User decision: diagnose the nonbinary LDPC algorithm on the existing 10 dB
  Type-II, q=1024, Gray, 256-symbol data before considering a new acquisition.
  V12 remains terminal `source_partition_blocked`; V12-X01/X02 are not
  reopened. [decision]
- The existing pool is sufficient for retrospective diagnostics/development,
  including channel aggregates, tiny interface oracles, optional decoder
  telemetry, and post-hoc exact-correction checks. Its frame/payload identities
  are already used by V4/V5, so every V13 artifact is
  `diagnostic_only`/`retrospective_reuse`; it is not fresh canary,
  confirmation, qualification, or promotion evidence. [decision]
- New OpenSpec change:
  `formal-nonbinary-ldpc-v13-existing-data-diagnostics`. Status is **PLAN
  DRAFTED / EXECUTION NOT AUTHORIZED**. P01-P07 are drafted; P08 independent
  read-only freeze review is pending. All D/R/I/E/A/C tasks are unexecuted and
  unauthorized. [repo-observed]
- Frozen plan: bw200 is primary; bw120/bw180 are deferred to a post-bw200
  cross-stratum check. Reconstruct mutually exclusive characterization,
  development, and retrospective-audit roles; ambiguous history yields
  `blocked_role_ledger`. Prefer V5 development as NB development and sealed
  V5 real frames as frame-identical audit without relabeling V5 evidence.
  [decision]
- Alice truth is allowed only for offline aggregates and post-hoc exact
  equality. It cannot enter decoder prior, stopping, candidate selection,
  retry, frame ordering, or same-frame tuning. Persistent telemetry contains no
  raw Alice/Bob arrays or per-position error masks; only required aggregate and
  decoder-internal traces are planned. [decision]
- D-stage D05 emits separate fields: `diagnosis_class` is exactly `interface`,
  `prior`, `decoder`, `code`, `mixed`, or `inconclusive`; `run_state` is
  `diagnosis_complete` for a supported single-factor conclusion and
  `diagnosis_inconclusive` for mixed/insufficient evidence. A D02/oracle
  failure may directly set `run_state=implementation_interface_fault`.
  Diagnostic engineering gates are V13-DT0/DT1/DT2 before D04; candidate
  implementation gates are V13-IT0/IT1/IT2/IT3 before E01.
  After D05 and a new amendment, at most one prior-only, decoder-only, or
  code-only candidate may be selected; mixed/inconclusive stops the route.
  [decision]
- Future additive diagnostics, if separately authorized, use
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/<run_id>/` with
  six minimal artifacts: `data_role_ledger.json`, `channel_diagnostics.json`,
  `diagnostic_outcomes.csv`, `decoder_telemetry.jsonl`,
  `root_cause_report.json`, and `diagnostic_run_manifest.json`. Frozen
  `src/`, `experiments/`, `tools/`, `results/`, and official
  `formal_ir_methods` roots remain unchanged. `diagnostic_outcomes.csv`
  contains baseline, candidate-development, and retrospective-audit rows with
  `phase` and `method` fields. [decision]
- Allowed `run_state` values are `plan_only`, `blocked_role_ledger`,
  `implementation_interface_fault`, `diagnosis_complete`,
  `diagnosis_inconclusive`,
  `failed_existing_data_feasibility`, `retrospective_non_ready`,
  `ready_for_fresh_confirmation`, and `invalid_diagnostic_execution`.
  `promoted`, `qualified`, and `observed_fresh_correction` are forbidden.
  Fresh acquisition/qualification requires a separate OpenSpec change and
  explicit user decision. [decision]

## 44. Nonbinary LDPC V13 Existing-Data Diagnostics — D-Stage Complete (2026-08-14)

- Change: `formal-nonbinary-ldpc-v13-existing-data-diagnostics`. **PLAN
  FROZEN**: P01-P08 accepted via independent read-only freeze review, zero
  blockers; four non-blocking planning corrections applied (code-branch
  evidence source pinned to offline short-cycle/girth analysis plus frozen
  rank=170 facts; spec scenario added; 512/stratum V5 development basis for
  32+64 denominators; V7 R1A label harmonized). [decision]
- D stage authorized and completed: D01-D03 plus DT0-DT2 (D04/D05 NOT
  authorized). New files: `comparison_bench/src/comparison_bench/formal_ir/
  nonbinary_v13_diagnostics.py`, `cli/run_nonbinary_v13_diagnostics.py`,
  `cli/verify_nonbinary_v13_diagnostics.py`,
  `tests/test_nonbinary_v13_diagnostics.py`. Tests 21/21 passed
  (DT0 8 + DT1 8 + DT2 5) in fresh `workspace/nbldpc_v13_<uuid>/` roots with
  `pytest -p no:cacheprovider`. [repo-observed]
- D01 real run exactly once: run_id `v13_d01_20260814`, package
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13_d01_20260814/`
  (six-file set). Role ledger 2304 rows = characterization 384 (128/stratum) +
  development 1536 (512/stratum) + retrospective_audit 384 (128/stratum);
  mutually exclusive, zero V4<->V5 identity overlap. [repo-observed]
- bw200 aggregates (128 frames, 32768 symbols, aggregate-only, no raw arrays
  persisted) — **empirical observations only, no root-cause conclusion (D05
  not run)**: raw SER mean 0.0771 (min 0.0391, max 0.1133); bit-plane
  mismatch monotone MSB->LSB 3.1e-5 .. 3.75e-2; zero-diff mass 0.9229, only 8
  runs max run length 2 (isolated errors, no bursts); QSC p=.20 calibration
  mismatch 0.1229; model entropy 2.722 b/symbol; NLL mean 1.247 b/symbol;
  empirical conditional entropy / necessary-leakage lower bound 0.547 b/symbol
  (empirical diagnostic, not a Shannon or finite-length proof). [repo-observed]
- D03 hook: wrapper/adapter only, V7 R1A sources byte-unchanged; hook-off
  element-for-element identical; hook-on adds aggregate telemetry without
  changing word/status/iterations. Independent read-only review: ACCEPT, zero
  blockers; two non-blocking warnings (stale planning docs — updated;
  manifest time field missing — noted for D04). [repo-observed]
- Claim boundary: highest V13 state is `ready_for_fresh_confirmation`; no
  decoder correction/qualification/promotion established. D04 (32-frame bw200
  baseline probe) requires separate main-thread authorization after DT0-DT2;
  D05 (root-cause report) requires D04; real-data decoder execution remains
  unauthorized. V12 remains `source_partition_blocked` (not reopened).
  [decision]
- Procedural: AGENT_HANDOFF.md / CURRENT_TASK.md updated 2026-08-14 with V13
  D-stage-complete as current state; V12 entries retained as previous state.
  [repo-observed]

## 45. Nonbinary LDPC V13 — D04 Baseline Probe Authorized, Implemented, Executed Once (2026-08-14)

- Change: `formal-nonbinary-ldpc-v13-existing-data-diagnostics`. Main thread
  authorized V13-D04 (unchanged V7 R1A `p=.20`, 32 pre-registered bw200
  development frames, exactly once). [decision]
- Implementation (in `comparison_bench/` only): `run_d04` core lane in
  `nonbinary_v13_diagnostics.py` (deterministic pre-registration sorted by
  frame_id, D04-limited manifest authorization, frozen-failure packages at
  `implementation_interface_fault`/`blocked_role_ledger`/
  `invalid_diagnostic_execution`), CLI `d04` action (requires `--authorized`
  + `--production` + fresh output root; `d05` remains a hard stop exit 2),
  read-only `verify_package` D04 branch, and DT3 lane tests (fake lifecycle,
  tamper, Alice boundary, no-overwrite, frozen failures). Tests 27/27 pass.
  V7 R1A frozen sources byte-unchanged; hook equivalence held on all frames.
  [repo-observed]
- D04 production run exactly once: run_id `v13_d04_20260814`, six-file package
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13_d04_20260814/`,
  strict read-only verifier PASS (32 outcome rows, 32 telemetry records,
  ledger ready 2304). Outcome: **8/32 `syndrome_consistent` + `exact_correct`
  (all converging at iteration 1), 24/32 `decode_failed` at the 100-iteration
  limit, zero `decoder_error`, zero exact mismatches, zero
  non-finite/normalisation/underflow events.** Telemetry observations
  (empirical only, no D05 conclusion): decode_failed frames end highly
  concentrated (mean posterior max 0.986, entropy 0.103 bits) with mean 3.79
  unsatisfied checks; oscillation detected on 11/32 frames. [repo-observed]
- Claim boundary: package run_state=`plan_only`, `d05_emitted=false`; no
  diagnosis_class/run_state conclusion. D05 (root-cause report + independent
  review) remains unauthorized and unimplemented; R/I/E/A/C locked; no
  decoder execution beyond the 32 pre-registered frames. 8/32 is not
  promotion/qualification/fresh correction. [decision]
- Procedural note: writing the package to the official
  `nonbinary_diagnostics/` root required a one-time sandbox escalation
  (danger-full-access, user-approved); normal workspace-write mode denies
  process writes under `comparison_bench/outputs_comparison/` (observed
  again on `__pycache__` and probe mkdirs). Future official-output runs from
  this harness need the same escalation. [repo-observed]

## 46. Nonbinary LDPC V13 — D05 Root-Cause Report: code / diagnosis_complete (2026-08-14)

- D05 emission (main-thread authorized per the recommended steps): offline
  girth analysis shows the frozen V7 R1A graph is **85 disconnected 2-check
  components** (256 all-degree-2 variables; 84 pairs with 3 parallel edges +
  1 pair with 4; Tanner girth 4; per-component kernel d_min = 3). Structural
  ceiling over the 32 D04 development frames: structural failure fraction
  0.75 == observed failure fraction 0.75 with **perfect frame-level
  correspondence** (24/24 decode-failed frames contain >=1 component with
  >=2 errors; 8/8 exact-correct frames contain none). [repo-observed]
- Emission `v13_d05_20260814_corrected` (authoritative, verifier PASS):
  `diagnosis_class=code`, `run_state=diagnosis_complete`, successor **R3
  code-only**; QSC p=.20 prior mismatch (calibration 0.1229, |entropy gap|
  2.17 bits/symbol) documented as co-factor (structure alone explains 100% of
  the observed failures). First emission `v13_d05_20260814` invalidated by a
  decision-machinery defect (ceiling doc lacked observed fractions -> default
  1.0; signed entropy-gap comparison), preserved immutably with sibling
  notice `v13_d05_20260814_invalid_execution_notice.json`; V8-60 precedent
  (fix + one additive re-emit). Decision-log 2026-08-14. [repo-observed]
- Decisive cross-checks: consistent with V7 synthetic canaries 0/4+0/4 (SER
  0.20 -> ~51 errors/frame -> every component multi-error); the D04 bimodal
  behavior (iteration-1 success vs 100-iteration failure) is the 4-cycle
  message-passing signature; D01 corrected run stats (2340 runs, max 3, 92.7%
  singletons) and 99.3% of nonzero diffs < 128 remain channel facts. [decision]
- Boundary: independent read-only review (reviewer-go) of the D05 conclusion
  is the next scientific gate; R1/R2 locked; R3 requires OpenSpec amendment +
  freeze review + main-thread approval; highest state remains
  `ready_for_fresh_confirmation`; promoted/qualified/observed_fresh_correction
  forbidden. [decision]

## 47. Nonbinary LDPC V13 — R3 候选 E01/A01/A02 全绿 → ready_for_fresh_confirmation (2026-08-14)

- R3 code-only candidate `nbldpc_v13_r3_code_v1`（amendment 冻结）：连通
  简单 check 图（170 校验节点、256 全 degree-2 变量、校验度 168x3+2x4、
  无平行边、check-girth 4/Tanner girth 8、rank 170），确定性种子搜索冻结
  seed=20260818；prior（QSC p=.20）、decoder 接口（flooding FFT-QSPA 镜像
  循环）、校验数/rate/max_iter 全不变。实现 `nonbinary_v13_r3_candidate.py`
  + `run_e01`/`run_a01`/`run_a02` + CLI + verify 分支；测试 49/49（含 IT0-
  IT3 与 A01/A02 fake 生命周期）。[repo-observed]
- **E01**（v13_e01_20260814，64 个预注册 bw200 development 帧）：
  candidate **64/64 exact_correct**，baseline（unchanged R1A）13/64，零
  forbidden；门通过。**A01**（v13_a01_20260814，128 个 frame-identical V5
  audit 帧，candidate-only 预注册）：**128/128 exact_correct**（raw SER
  0.039–0.113），median 0.90 s/frame，disclosure 6.640625 ≤ 8.75 → 门全过
  → **run_state=`ready_for_fresh_confirmation`**（V13 最高状态）。
  **A02**（v13_a02_20260814，bw120+bw180 各 128 audit 帧）：128/128 与
  128/128，readiness gate 满足，no_state_promotion=true。六个生产包全部
  只读 verifier PASS、git 提交。闭环：与 D05 `code` 诊断一致——图连通性/
  girth 是根因，替换后同先验下全部精确纠错。[repo-observed]
- 科学边界：ready_for_fresh_confirmation 不是 promotion/qualification/
  fresh correction；fresh acquisition 已由用户决定、新开独立 change
  （见 §50）。V13 **C01 完成**（独立验收 ACCEPT、零 blockers；本记忆
  triage 即 C01 的记忆部分）；V12 已正式归档（2026-08-15，见 §50）。
  [decision]
- 可复用经验：E01/A01 候选帧解码 median ~0.9–1.0 s/帧（q=1024 flooding，
  大多帧 1–2 轮收敛）；一次 E01 全屏（64 帧×2 解码）约 20–40 分钟，A01
  （128 帧）约 5–10 分钟——远比最坏 100 迭代估计快，因为收敛帧占多数。
  [repo-observed]

## 48. Nonbinary LDPC V14 效率可行性门——冻结、实现、执行中 (2026-08-14)

> 2026-08-15 supersession：本节为门执行前的中间状态；门已执行完毕，
> **gate_state=fail**、效率路线冻结（见 §49），V15/V16 归档为 aborted
> drafts（见 §50）。

- 立项依据：SciVerse 调研（docs/nonbinary-ldpc-efficiency-roadmap-survey.md）
  ——文献效率锚点 Müller 2024 f=1.078–1.14（q=8），V13 R3 f≈12.1 需高码
  率（m≈15–18 → rate 0.93–0.94）+ 结构化先验（H=0.547 vs QSC 2.72）。
  [decision]
- 冻结门：3 λ × m∈{15,16,17,18} 共 12 点评估；Stage 0 QSC 回归
  （0.069±0.012）；Stage 1 折叠 φ_m 小 q 验证；Stage 2 q=1024 点评估；
  PASS=f≤1.3 且收敛；FAIL=路线冻结。预算 3 GiB/24h/execute-once+回放；
  降级链 Li→Cohen→resource_blocked。freeze review：首轮 BLOCKERS 修复后
  ACCEPT。 [decision]
- DE 机制事实（可复用）：V9 run_mcde 信道块（:446-457）~10 行改动即
  支持任意 w（更新核已接受任意 (N,q) 先验）；q=1024 单点 DE 可行
  （numba ~1.18s/500样本×30迭代）而 profile 搜索不可行（V11 66.7h）；
  V9A/V10/V11 失败根因=测量前承诺不可达门限/零候选/继承门限。
  [repo-observed]
- 实现（flash 子代理 + 独立 verifier ACCEPT）：nonbinary_v14_channel.py
  / nonbinary_v14_mcde.py（numba 本地核，QSC 与 V9 等价 1e-12）/ cli/
  run_v14_gate.py；测试 64/64；V8/V9/V11/V13 源码零改动。gate 首启失败
  （证据目录整体 fail-closed 误伤先存的模型文件）已修为按文件
  fail-closed。 [repo-observed]
- 下一步：门结果 → V15（高码率候选，合成资格；fresh 实数据需用户决定
  采集）/ 或路线冻结声明；V16（rate-adaptive + syndrome 估计 + 子块确认）。
  [decision]

## 49. Nonbinary LDPC V14 效率可行性门——FAIL：普通系综在 f<=1.3 无解 (2026-08-15)

- V14 门执行一次（evidence 提交 1cdc63b6；E02 独立 review ACCEPT）：
  Stage 0 QSC 回归 PASS（proxy 0.060 vs 0.069, |d|=0.009<=0.012）；
  Stage 1 折叠验证全绿；Stage 2 的 12 个冻结点（3 λ × m∈{15..18}，
  q=1024 结构化信道）全部非收敛——最终 base-q 熵 0.288-0.357（阈值
  0.01 的 29-36 倍，非边际）；f 值 1.032-1.239 全满足 <=1.3 但收敛是
  绑定判据 → gate_state=fail。预算 wall 87min/577MiB。 [repo-observed]
- 科学含义：码率点全在容量内（R<=0.9414 vs C~0.9432）→ 非信息论不可
  能，是普通不规则系综（degree-2 含 λ、dc~51 集中 ρ）在高码率的 BP
  阈值结构性缺口（与 V10/V11 的 QSC .22/.32 失败同类）。机制可信
  （T2 与 V9 等价 1e-12 + Stage 0 文献回归双背书）。 [decision]
- 后果：V15/V16 不立项（提案/骨架保留为 gated drafts）；效率路线冻结；
  下一步只能用户决定新 change（SC-LDPC 阈值饱和 / Cohen 位面分解 /
  多边族），且必须新 DE 门先行。V13 R3（f~12）仍为唯一验证正确器；
  fresh-confirmation-only 路线不受影响。 [decision]
- 可复用经验：q=1024 结构化 DE 单点 ~7 min（numba；12 点 87 min）；
  普通 irregular 系综在 rate>0.93 不收敛是"可预测的负结果"——高码率
  必须换系综族而非调 profile；gate-first 纪律防止了 V15 的浪费性构造。
  [repo-observed]

## 50. P0 状态收口 + P1/P2 新目标 (2026-08-15)

- **P0 收口（用户更新目标，纯 housekeeping，无科学执行）**：V12 正式
  归档 → `openspec/changes/archive/2026-08-15-formal-nonbinary-ldpc-v12-real-micro-feasibility/`
  （保留 `source_partition_blocked`、X01/X02 未执行、v2 prepare 包；
  归档≠成功、不重开执行；delta spec 未合并——V9/V10 先例）。
  V15/V16 归档为 **aborted drafts**（`...v15-high-rate-candidate-aborted/`、
  `...v16-rate-adaptive-deployment-aborted/`；未立项/前置门失败；delta
  spec 未合并）。陈旧文档全部修复：CURRENT_TASK.md、V14 tasks.md
  （头部状态、测试数字、回放完成）、V13 tasks.md（C01 COMPLETE、
  IT0-IT3 49/49——原始记录为 `test_nonbinary_v13_diagnostics.py` 49 个
  test）、AGENT_HANDOFF.md（Current State 重写）、记忆 §47/§48。
  V14 测试数字统一：修复前 13+49=62/62 → 修复后 15+49=**64/64**
  （decision-log 2026-08-14 原始记录）。本地领先 `origin/main` 28 个
  提交；push 待单独授权。 [decision]
- **P1（立即优先）**：V13 R3 fresh acquisition——新开独立 OpenSpec
  change `formal-nonbinary-ldpc-v13-r3-fresh-acquisition`（不复用 V12
  执行身份、不自动宣称 promotion）。冻结：新 frame/payload identities；
  acquisition/window/stratum 设置；characterization/canary/confirmation
  角色隔离；R3 码本（nbldpc_v13_r3_code_v1）、先验（QSC p=.20）、
  max_iter=100 保持不变；分布漂移与无 eligible frame 停止规则；失败
  原样保留、禁替换帧/调参/重跑。流程：冻结 → prepare → 主线程 review
  → 单次 fresh execute → 只读 verify → fresh-confirmed / frozen
  failure。证据收益最高、技术不确定性最低；只回答"R3 在 fresh 数据上
  是否仍能纠错"，效率仍 f≈12。 [decision]
- **P2**：独立效率研究门 `formal-nonbinary-ldpc-v17-multibit-structured-de-gate`
  ——只做可行性门、不构造有限码。次序：Cohen/多位信道机制复现门 →
  V13 已观测 MSB→LSB 单调失配映射为冻结信道模型 → 预注册少量边标签/
  位面候选 → 执行前冻结收敛/效率/预算/replay 标准 → 一次执行。
  PASS → 另开有限码 candidate change；FAIL → 冻结，不启动 V15/V16、
  不扩大搜索。选它作第一效率路线：直接对应当前数据的位面不均匀性；
  SC-LDPC 在 QSC 下负耦合增益、结构化信道下未否定，排第二；多边/
  高维 λ 搜索空间大，排第三。 [decision]

## 51. P1 prepare 执行（no_eligible_frames）+ P2 V17 门实现与生产执行 (2026-08-15)

- **P1（fresh acquisition）PREP 完成**：change 冻结 + 独立 freeze review
  ACCEPT（三个警告 amendment 修复：A02 表述、规模不足规则
  `insufficient_eligible_frames`（eligible<192 冻结）、漂移阈值引用 V13
  D01 参考区间）。PREP 工具由 flash 子代理实现（FA1–FA5 全过、19 测试、
  decoder-free/array-free、复用 V12 partition 排除机制、身份
  `v13r3fresh-<stratum>-<uuid>`（sha256(seed||canonical)）、schema
  `nbldpc_v13r3_fresh_plan_v1`/`no_eligible_v1`/`insufficient_v1`、
  production_prepare_authorized 默认 False）。主线程独立重跑 19/19。
  生产 prepare 执行一次（提交 17542dc4）→ **`state=no_eligible_frames`**
  （`D:\Data` 无 fresh 10 dB Type-II 帧数据源——最新 2026-07-28 JSI
  非帧数据）；包
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_prepare_20260815/no_eligible_package.json`
  （decoder 不变式完整冻结）。主线程 review ACCEPT → 判定 **frozen
  failure（数据不可得）**；execute/verify 阻塞；用户提供 fresh 数据后
  重新 prepare（确定性工具，非失败重跑）。 [decision]
- **P2（V17 门）实现完成**：freeze review ACCEPT（两个警告 amendment
  修复：评估点集固定 m∈{15,16,17,18} 全集、Stage 0 锚点 A/B 具体化
  （内部一致 ≤0.005 + 文献交叉 |δ|≤0.012，无布尔 fallback））。
  实现由 flash 子代理完成（VA1–VA6 全过、17 测试、5 新文件：stage0/
  channel/mcde/CLI/tests；V8/V9/V11/V13/V14 源码零改动）；主线程独立
  重跑 17/17。Stage 1 模型从 D01 包只读构建：per-bit-plane 错误概率
  = `aggregates.bit_plane_mismatch.mismatch_rate`（10 值 MSB→LSB 单调
  3.05e-5→3.75e-2），joint_structure=`product_of_per_plane_marginals`
  （D01 无联合统计，显式声明保守近似），entropy=0.549955 bits/symbol
  （≈V13 0.547 一致）。Stage 2：3 候选（bitplane/edgelabel/planeweight）
  × m∈{15,16,17,18}。生产 gate 执行中（2026-08-15，后台）。 [repo-observed]
- 提交链：fb6e579d（P0）→ 240e3a2e（P1/P2 立项）→ 3a6d2990（决策日志）
  → 037ee5a6（freeze ACCEPT+amendment）→ 757464f4（W1 完全关闭）→
  d801427c（P1/P2 实现）→ 17542dc4（P1 prepare 包）。 [repo-observed]

## 52. P2 V17 门生产执行完成：mechanism_unverified（FAIL 类）(2026-08-16)

- **生产 gate 执行一次**（后台任务，wall 7026.6 s，peak RSS 541 MB
  ≤ 3 GiB/24h）→ **`gate_state=mechanism_unverified`**。Stage 0
  锚点 A（q=4 退化 p1=p2 内部一致性）**失败**：bit-plane 分解阈值
  0.0525 vs 符号级 0.0600，Δ=0.0075 > 0.005（方向性成立：位面分解
  p=0.055 起 joint 未收敛，符号级至 0.060 仍收敛）；锚点 B（文献
  交叉）通过：|0.060−0.069|=0.009 ≤ 0.012。Stage 1 模型构建成功
  （D01 只读聚合，10 位面误码率 3.05e-5→3.75e-2 MSB→LSB 单调，
  product-of-marginals 显式保守近似，熵 0.549955）。Stage 2 诊断
  12/12 未收敛（bitplane/edgelabel/planeweight × m∈{15..18}，
  f_achieved∈[1.065,1.279] 全 < f_limit 1.3，收敛为绑定判据），
  diagnostic_only=true，无 pass_point。
- **strict replay 5/5 字节一致**（`workspace/v17_replay_20260816/`
  副本 + `replay` 动作 ok=true，`v17_replay_evidence.json` 记账）；
  **E02 独立 gate review ACCEPT（零 blockers）**（G1–G7 全过：
  判定链/数值/纪律/预算/schema/回放/执行器范围）。C01 收尾完成：
  decision-log 2026-08-16 条目 + 记忆 §52 + tasks.md I/E/C 全部
  checked + CURRENT_TASK/AGENT_HANDOFF 同步（本地提交）。 [decision]
- **冻结纪律生效**：位面/边标签效率路线冻结；不启动 V15/V16、不
  扩大搜索、无"最接近"续行、无 rerun/调参；Stage 2 诊断点不构成
  效率结论。效率路线下一步只能由用户决定另开新 change（② SC-LDPC
  仍排第二——QSC 负耦合、结构化未否定；③ 多边/高维 λ 第三）。
  P1（V13 R3 fresh acquisition）独立推进不受影响，仍阻塞于 fresh
  数据（用户提供后重新 prepare 即可）。 [decision]
- 证据：`openspec/changes/formal-nonbinary-ldpc-v17-multibit-structured-de-gate/evidence/`
  6 文件（v17_stage0 / v17_multibit_channel_model / v17_stage2 /
  v17_gate_decision / v17_gate_manifest + v17_replay_evidence 记账）。
  本地领先 `origin/main` 36 个提交；push 待单独授权。 [repo-observed]


## 53. V13-R3 fresh 数据准入——2026-01-21 三源拒绝 (2026-08-16)

- 用户提供三个 `D:\Data\Raw Data\2026.1.21\...` Type2 ttbin 源后，按修正后的
  “v13r3fresh_20260816” 规划执行 **D0 数据准入**：判定
  `data_intake_rejected_for_fresh_confirmation`。
- 原因：时间戳 2026-01-21 早于 frozen fresh 边界；损耗/10 dB 元数据不可核验；
  folder1 已有 Release D2 烟测 `raw_ser=0.254663`，远超 V13 D01 参考 0.0771。
- 证据包：
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_intake_20260816/intake_decision.json`。
- 修正规划：
  `docs/nonbinary-ldpc-v13-r3-fresh-data-intake-20260816-plan.md`。
- D1–D5 已于 2026-08-16（shell 可用后）执行完毕：D1 环境/git 基线、
  D2/D3 三源 sidecar（`map_sanity` 全 FAIL）、D4 三源 pairs-table + manifest、
  D5 全量漂移预检。D5 三源全部 `precheck_state=drift_exceeded`
  （raw SER mean ≈0.240–0.256，偏差远超 0.03 阈值），自动停止，不进入 P/E/V。
  真正 fresh 数据到达前，P1 保持 `no_eligible_frames`；push 仍待用户单独授权。

## 54. V13-R3 legacy drift audit——2026-01-21 三源执行 (2026-08-16)

- 用户决定：使用三份 `2026-01-21` Type2 数据继续，不要求 fresh 边界。
- 新 change：`formal-nonbinary-ldpc-v13-r3-legacy-drift-audit`；claim boundary
  仅 `legacy_drift_audit`。
- 实现：`formal_ir/nonbinary_v13r3_legacy_audit.py`、
  `cli/run_v13r3_legacy_drift_audit.py`、8 个测试。
- 生产执行一次：每源前 64 完整帧（frame_id 0..63），共 192 帧；不变 R3
  候选 `nbldpc_v13_r3_code_v1` 解码。结果 **188 exact_correct**、
  **4 decode_failed**（`iteration_limit`：type2_1M frame 15/20、
  type2_2M frame 52/56）；失败原样保留；只读 verify OK。
- 证据包：
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3_legacy_drift_audit_20260816/`
- 边界：不构成 fresh-confirmed / promotion / qualification；P1
  `no_eligible_frames` 与 P2 V17 `mechanism_unverified` 均不变。push 待授权。

## 55. V13-R3 legacy drift audit——全量 8412 帧完成 (2026-08-16)

- 在 192 帧审计后，用户要求继续；使用 `--all-frames --chunks 8` 并行执行全量。
- 结果：8412 帧中 **8284 exact_correct**、**128 decode_failed**（iteration_limit）、
  0 exact_mismatch。分源：2729/2767、1970/2000、3585/3645。
- 8 chunk 各自 verify OK；合并包：
  `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3_legacy_drift_audit_full_20260816/`
- 边界：legacy_drift_audit only；不构成 fresh/promotion/qualification。

## 2026-08-20 V29 retrospective finite-code gate: FAIL and V30 successor (historical pre-execution snapshot)

- Canonical V29 `run_02` stopped after 9 persisted 1M blocks under explicit
  user authorization: exact=1, tag_verified=1, 8 failures, remaining=91,
  maximum possible=92<95. Terminal `v29_finite_gate_fail`; readonly verifier
  `ok=true`; prefix FER is `observed_prefix_only`, never full FER.
- V29 `run_01` is retained as superseded 0-call `implementation_blocked`.
- Correct V28 lifecycle: the original ACCEPT was superseded by V28R; V28R is
  engineering evidence only. Its independent L1 audit is 15 support groups,
  max group 69, 303 duplicate projective classes, 922 columns in duplicate
  classes, and 1107 guaranteed proportional/weight-2 pairs, proving
  `d_min<=2` for that finite construction. This is not a GF32×GF32 route
  impossibility result; it is a projective-duplicate matrix defect.
- The original V30 `FROZEN_P102_ACCEPTED` projective-safe finite-graph gate is
  superseded by V30R `FROZEN_P103_ACCEPTED`. At the time of the P103 review,
  V30R only had authorization to proceed and had not yet claimed execution.
  V30R reuses V26 channel semantics and V29 leakage policy but must not reuse
  the V29 holdout as fresh qualification. This historical snapshot predates
  the later V30R execution and is superseded by the V30R closeout at the top
  of this file.

## 2026-09-04 V72P2D1-PARITY corrigendum link (descriptive-only correction, history unchanged)

- Corrigendum [decision]: `docs/research_cycles/V72P2D1-PARITY/CORRIGENDUM.md`
  corrects the M1-M7 "four-cycles 1196/1196, collisions 1194/1194
  (graph-isomorphic)" reading; pure-H check-check 1196/1196 does not imply
  fixed-symbol-grouping full-factor-graph isomorphism
  (symbol-factor-check 8452/328, collision rows 8170/326);
  D1 is input-syndrome consistency only (NOT_RECORDED: candidate syndrome
  violation count, quantiles, sum(c2v), prior-only baseline, edge gain);
  two-arm 72ckpt candidate-vs-Bob all 0, A334/B321, verification failed,
  metering 9100/9171 retained. Descriptive-only; incomplete observations
  are not PASS. No decoder run / rerun / tuning / four-file overwrite /
  per-symbol key read.

## 2026-09-04 V72P2D1 algorithm-route exploration (read-only, proposed successors)

- `docs/research_cycles/V72P2D1-PARITY/ALGORITHM_ROUTE_RESEARCH.md` records
  the route study at b04e5757. Pure-H four-cycle/collision counts are
  1196/1196 and 1194/1194; symbol-factor 8452/328 is a workspace recount,
  while symbol/collision rows 8170/326 remain external, not repo-verified.
- The b04 O1 supplement read only the four VAL1726--1729 frames (not CAL) and
  is `POSTHOC_RECONSTRUCTED`; this route exploration itself read no raw/parquet,
  ran no decoder, and did not change code, results, or lifecycle.
- Static review found no active-path LLR-direction, local-factor
  self-exclusion, syndrome-aware SPA, or warm-start semantic error. The
  Bob-oriented weak-fixed-point explanation is an inference, not a proven root
  cause. `run_incremental_decoder` returning stale variable-to-check output is
  a separate known bug; current D1 used `run_decoder`.
- The mother has 1204 high-degree columns (mean degree about 26.2035) versus
  9035 degree-2 and one degree-1 parity columns. Fixed symbol grouping leaves
  symbol edge totals 19/20/303 in both A/B; a degree-balanced interleaver and
  grouped-symbol mask BP are `PROPOSED`, not accepted designs.
- M0 hierarchical prior (lambda 221.22162910704503, CE about 7.135/7.150)
  and historical V70R1 M2 (VAL CE 6.7871) should be compared only under a new
  frozen plan. Proposed next diagnostic is one-block L/I/P orthogonal triage;
  three arms failing to escape would stop binary edge-level micro-tuning and
  permit proposing tiny exhaustive grouped-symbol-mask or GF32 comparison work.

## 2026-09-04 双 PRIVATE 仓分离终态：拓扑/remote 布局（durable）

- 终态 [decision]: 双 PRIVATE 仓分离：Release 仓为原 pipeline 仓改名，Comparison 仓为新建仓；各自 origin 已切换至自家新地址，legacy-origin 保留旧 URL 只读。
- 分支与保护 [decision]: Release 默认分支 main，保护 main 与 polar-mainline；Comparison 默认分支 main，formal-ir 为受保护工作分支。
- 发布前必检 [decision]: 两仓互不可见为发布前必检项；历史豁免仅放行已审计项。
- 审计链 [repo-observed]: 唯一来源为 `openspec/changes/repo-remote-decoupling` 三件套（proposal/design/tasks）；脏态书面豁免已归档，不在此记录临时盘点数字。
## 2026-09-06 — Simplified single-user research-cycle gate

- Git commit IDs are provenance, not authorization tokens. Do not require
  `HEAD == origin == implementation SHA`, stale-SHA grep, or a commit that
  records its own ID for ordinary local research cycles.
- Pre-EXECUTE checks the intended branch, scoped code/config/test/packet
  cleanliness, frozen scientific contract, focused tests, explicit user
  authorization, and absence of the target output.
- Documentation-only commits after code acceptance do not invalidate accepted
  code. Use exact revision locking only for a concrete multi-writer,
  destructive, release, or evidence-integrity risk named in the packet.
- Keep independent scientific review, no-overwrite outputs, honest partial and
  failure states, and Pre-RESULT review for claim-bearing evidence.
- Review by milestone, not by commit: docs-only and tiny unchanged-scope fixes
  use focused checks and are batched into the next independent scientific
  review. Active packets inherit this simplified Git rule.
## 2026-09-07 V72P2D5 unauthorized G1 output VOID_RETAINED_IN_PLACE (docs-only disposition)

- Disposition [decision]: `workspace/v72p2d5_g1/20260906_r1/` (4 files,
  `decoder_calls=440`, app_exact 0, app_failure 1.0, oracle 0) is
  `VOID_RETAINED_IN_PLACE` — retained unmodified as forensic evidence only,
  barred from citation as a G1 result, performance measurement, or method
  evidence; delete and quarantine-move both rejected (incident I08).
- Blocker [repo-observed]: `MODEL_F_INPUT_PRE_RESULT_REVIEW_R1.md` =
  `PRE_RESULT_REVIEW_FAIL`, sole blocker PR16 (G1 root exists while
  `g1_execution_authorized=false`, `next_gate=P0_PACKET_REVIEW`); Model-F
  artifact content PASS on PR01-PR15 and PR17-PR23.
- Root cause [repo-observed]: incident I09 test-isolation defect; repair
  complete per `TEST_ISOLATION_REWORK_EVIDENCE_R1.md` (SAFE A/B/C + AST static
  guard, 165 collected / 165 passed, focused 10 passed, binder/writer entries 0,
  P0/G2 roots absent).
- Lifecycle [decision]: all `*_execution_authorized` stay false;
  `scientific_promotion=false`; `next_gate=P0_PACKET_REVIEW`; PR16 addressed by
  record only, clearance needs independent Pre-RESULT re-review; a future
  authorized G1 run needs a new output root, no reuse or comparison.

## 2026-09-07 V72P2D5 Model-F input RESULT ACCEPTED (docs-only, no authorization)

- Acceptance [decision]: Model-F CAL-TRAIN input
  `workspace/v72p2d5_model_f_input/20260907_r1/` (2 files, `CAL702..1725`,
  1024x256=262144 symbols, `counts_ab` int64 `(1024,1024)` axis `(Alice,Bob)`,
  `p_b` derived from `axis0`, `lambda_star=137.3823795883264`) accepted as the
  P0/G1/G2 prior input; recorded at cycle level, artifact `status` left
  `MODEL_F_INPUT_CANDIDATE` (protected immutable root, loader accepts both).
- Review chain [repo-observed]: implementation accepted; Pre-EXECUTE R2 PASS
  post-PX11; one authorized prepare + one verify, authorization consumed;
  Pre-RESULT R1 FAIL on PR16; disposition `VOID_RETAINED_IN_PLACE`;
  Pre-RESULT R2 PASS, C01-C11 PASS, `195 passed`.
- Caveat [decision]: PR16 cleared BY RECORD not by condition — the G1 root
  still exists; R2 reinterpreted PR16 by intent. Do not later read this as a
  physical clearance.
- Residual [decision]: `R-R1` prod-side bare-authorized defaults unchanged,
  test-side guard only, future P0/G1/G2 packets must re-verify isolation;
  `R-R2` no global formal-root absence gate, per-test snapshots instead.
- Lifecycle [decision]: nine `*_execution_authorized` false,
  `scientific_promotion` false, `next_gate` `P0_PACKET_REVIEW`; P0/G1/G2 each
  need their own packet review and separate explicit authorization.

## 2026-09-07 V72P2D5 P0 cost preflight ACCEPTED as cost measurement only (docs-only, no authorization)

- Acceptance [decision]: second authorized P0 invocation
  `workspace/v72p2d5_p0_cost/20260906_r1/` accepted as `P0_RESULT_ACCEPTED`,
  scope `COST_MEASUREMENT_ONLY`, recorded in `P0_RESULT_ACCEPTANCE_R1.md`;
  cost acceptance is not scientific promotion and grants no G1 authorization.
- Measured [repo-observed]: phase `p0-cost`, block_length 64, f_list 1.0/1.2,
  frozen_rows 1.0 m1 49/m2 43 and 1.2 m1 59/m2 52, seeds 2026090510/2026090511,
  decoder_calls 12, decode-attributed 8.064733600011096 s vs 1440 s cap (no
  `RESOURCE_OVERRUN`), projected_g1_s 161.8241519993171, projected_g2_s
  485.47245599795133, projection_blocked false, passed true, operator wall
  8.6278899 s exit 0 empty stdout/stderr.
- Not established [decision]: no correctness, no `exact_failure_fraction`, no
  FER, no leakage, no key rate, no net rate, no qualification of NB-LDPC /
  dv3 mother / rate points / Model-F, no statement G1/G2 will pass, no
  authorization for anything.
- Reviews [repo-observed]: Pre-EXECUTE PASS (five questions decided),
  loader-fix PASS (`299416ae`), Pre-RESULT PASS with limitations, guard-rework
  PASS with L1-L4; both P0 authorizations consumed, first
  (`a71188fb`/`3ecaebb6`) produced no run (0.376 s false missing-input refusal
  from consumer path defect), second (`f1cdf970`/`b4696273`) produced result.
- Limitations [decision]: L1/L2/L3/L4/L-RSS/L-SCALE/L-ITER all
  `MUST_CARRY_INTO_G1_PACKET`; `projected_g2_s` grants G2 nothing (no
  width/row-count scaling); RSS null on Windows; all 12 decodes ran to
  `MAX_ITER = 90` cap.
- Lifecycle [decision]: nine `*_execution_authorized` false,
  `scientific_promotion` false, `next_gate` `G1_PACKET_REVIEW`; G1 neither
  frozen nor authorized; next is G1 packet freeze, then independent
  Pre-EXECUTE review, then separate explicit G1 authorization, no
  merge/reorder.

## 2026-09-07 V72P2D5 G1 readiness implementation-only acceptance + Pre-EXECUTE packet frozen (docs-only, no authorization)

- Acceptance [decision]: G1 readiness implementation `cf61ee63`
  (predecessor `614aab9e`, spec/review `d47e7da1`) accepted as
  implementation readiness only (`G1_IMPLEMENTATION_ACCEPTANCE_R1.md`);
  scope excludes any decoder/G1 result, FER, leakage, key rate,
  qualification, or G2 claim; acceptance grants no authorization.
- Review chain [repo-observed]: packet review PASS, readiness code review
  PASS (`G1_READINESS_CODE_REVIEW_PASS`), scope addendum PASS
  (`G1_CODE_REVIEW_SCOPE_ADDENDUM_PASS`, exact frozen three pytest files,
  `219 passed`), live Windows RSS positive without decoder execution.
- Packet [repo-observed]: `G1_PRE_EXECUTE_PACKET_R1.md`
  `G1_PRE_EXECUTE_PACKET_FROZEN / EXECUTE_NOT_AUTHORIZED`; phase `g1`,
  root `workspace/v72p2d5_g1/20260907_r2`, width 64, f 1.0 then 1.2,
  rows L1 49/59 L2 43/52, seeds graph 2026090501/2026090502 + blocks
  2026090600..2026090699, oracle first 20 per f diagnostic-only, GF32 cold
  max_iter 90 damping 1.0, 440 calls, outer wall `<=900 s`, watchdog
  960 s + grace 30 s, RSS peak `<2147483648` / None fails, four
  no-overwrite files, one attempt consuming authorization; exact frozen
  `timeout.exe -k 30 960 ... --phase g1` command; 13 independent checks;
  7 outcomes with `passed` iff `G1_TREND_PASS`; frozen signal; full
  operator return; no result acceptance before Pre-RESULT review.
- Boundaries [decision]: process-vs-entrypoint wall (outer controls 900 s);
  `app_iterations_max<=180` asserted not clamped; exception/timeout/refusal
  operator-side; G1 synthetic trend only, never real FER/qualification.
- Lifecycle [decision]: nine `*_execution_authorized` false,
  `scientific_promotion` false, G1 unauthorized/unexecuted, G2
  unauthorized; `next_gate` `INDEPENDENT_G1_PRE_EXECUTE_REVIEW`; next is
  independent Pre-EXECUTE review (no authorization flip, no G1 run).
## 2026-09-07 V72P2D5 G1 result accepted as synthetic completed-no-signal failure (no pass, bounded attribution only)

- Acceptance [decision]: sole frozen G1 root `workspace/v72p2d5_g1/20260907_r2` accepted (`docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/G1_RESULT_ACCEPTANCE_R1.md`) with scope `SYNTHETIC_COMPLETED_NO_SIGNAL_FAIL`, outcome `G1_COMPLETED_NO_SIGNAL_FAIL`, `passed: false`. Chain `cf61ee63 → 6494b623 → f4d577fb → 58c68961`; dual review Pre-EXECUTE PASS + Pre-RESULT `G1_PRE_RESULT_REVIEW_PASS` (internal coherence only).
- Literals [repo-observed]: both f APP exact `0/100` (rate `0.0`, failure `1.0`), APP syndrome-ok `0`, oracle exact/syndrome `0`, `app_iterations_max 180`, APP `18000 = 100×180`, oracle `1800 = 20×90`, `decoder_calls 440 = 400 + 40`, crashes/nonfinite `0`; wall `238.86517630005255 s <= 900` (operator `239.110 s`), RSS `115142656 < 2147483648`. Resource-pass/signal-fail: signal FALSE (top exact `0`), terminal no-signal failure, `passed=false`.
- Boundary [decision]: not trend pass, qualification, G2 readiness, method success, rerun permission, or reinterpretation; exact/syndrome/oracle isolated, stored zeros literal (no FER/undetected/correctness relabel). Single attempt consumed; no second G1, no G2, no real data.
- Lifecycle [decision]: `g1_execution_attempts/completed 1/1`, `g1_result_accepted true` with scope/outcome/passed recorded; `next_gate` `G1_NO_SIGNAL_ATTRIBUTION_IN_PROGRESS`; nine authorizations false, promotion false. Next is bounded failure attribution only (no formal CLI phase, no formal-root write).


## 2026-09-07 V72P2D5 G1 no-signal attribution (disclosure-insufficient, no code change)

- Attribution [decision]: accepted G1 dual-zero attributed to FINITE_LENGTH_DISCLOSURE_INSUFFICIENT (sole primary) in `docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/G1_NO_SIGNAL_ATTRIBUTION_R1.md`. Evidence: accepted Model-F actual CE L1/L2 ~= 5.0/5.0 bits (uniform priors, mass-on-truth ~= 1/32) vs frozen sizing 3.81/3.35; need 64/64 (f=1.0) and 77/77 (f=1.2) vs frozen 49/43, 59/52. Paired APP 0/4 + oracle 0/4 saturated; full-H2[:52] 0/4; cap-180 still fails; decoy-prior exact=1 all prefixes; GF32 cross-match exact.
- Rejected [repo-observed]: decoder/field, APP-propagation, iteration-cap, prefix-rank as primary (prefix STRUCTURE_BLOCKED carried secondary; rank full). No implementation defect -> no OpenSpec/code diff; frozen constants/result untouched.
- Lifecycle [decision]: `next_gate` `G1_NO_SIGNAL_ATTRIBUTION_IN_PROGRESS -> G1_ATTRIBUTION_ROUTE_DECISION`; single next probe for main thread (square m=n=64 oracle, approve/reject/redirect). Nine authorizations false, promotion false, G2 absent, no rerun.


## 2026-09-08 V72P2D5 G1 wide attribution R2 (lambda-contract defect + candidate)

- Attribution [decision]: terminal class `LAMBDA_APPLICATION_CONTRACT_DEFECT` supersedes R1 bucket as primary (R1 carried secondary) in `docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/G1_WIDE_ATTRIBUTION_R2.md`. Evidence root `workspace/d5_g1_wide_attribution_r2_5c38a20ae60b41ceb0b6a0d7757aa2aa/` (53 dev calls, CAL-only): frozen `lambda*` selected as total per-column concentration but applied per cell (99.82% prior, MI 0.0004 vs 2.48 bits); C0 square-oracle 0/4 vs C1 4/4; C1 L2 at H2[:52] 2/4; C1 L1 fails everywhere incl. square (binding constraint, mass 0.096).
- Implementation [decision]: OpenSpec `v72p2d5-g1-information-recovery-r2` + additive `build_f_model_concentration` / `prepare_model_f_prior_candidate` (frozen path untouched); 8 new tests green; 3-file D5 suite 226 passed + 1 pre-existing stale fail (`test_G1R01...` absence assertion vs accepted root, untouched).
- Lifecycle [decision]: `next_gate` `G1_ATTRIBUTION_ROUTE_DECISION -> INDEPENDENT_G1_INFORMATION_RECOVERY_R2_REVIEW`. Accepted G1/model-F artifacts, authorizations, thresholds, seeds unchanged; no rerun, no G2, no push.

## 2026-09-08 V72P2D5 G1 R2 acceptance (additive backoff-prior candidate, no formal change)

- Acceptance [decision]: R2 review `G1_INFORMATION_RECOVERY_R2_REVIEW_PASS` landed and accepted (`G1_INFORMATION_RECOVERY_R2_ACCEPTANCE_R1.md`) as `G1_INFORMATION_RECOVERY_R2_ACCEPTED`, scope `ADDITIVE_NONFORMAL_BACKOFF_PRIOR_CANDIDATE`, terminal `LAMBDA_APPLICATION_CONTRACT_DEFECT`; `formal_g1_result_changed false`, `production_wiring_changed false`. Chain `88053563→a93106f5→21576add→1d4fa912`; like-for-like `10.0 → 7.51` (MI `0.0004 → 2.48`, tmass `0.031 → 0.254`); three-call square split old 0/4 vs candidate oracle-L2 4/4; C1 L1 `0.096` fails incl. square; C1 L2 only 52–64 rows.
- Lifecycle [decision]: `g1_information_recovery_r2_review PASS_R1`, `candidate_accepted true`, `implementation a93106f5`; `next_gate` `INDEPENDENT_G1_INFORMATION_RECOVERY_R2_REVIEW -> G1_L1_ESTIMATOR_DISCRIMINATOR_IN_PROGRESS`. Accepted Model-F/G1 unchanged, all authorizations false, G2 absent, no rerun, no push.

## 2026-09-08 V72P2D5 G1 L1 discriminator (BP-threshold terminal, route-stop)

- Result [repo-observed]: prereg `f0e4a1c` before scores/calls; CAL-only winner E2 (`kap*≈62.10` unanimous, mean L1 NLL 3.7717 vs 3.8147); E1≡E3 bit-identical (backoff linearity). Paired decoder 75 calls: n64 0/24 incl. square; n128/n256 nonzero-rate 0/4; square-only 1/4, 2/4; mass ~0.10–0.15 vs ~0.28 needed; 0 nonfinite, flags agree, max call 2.41s, peak RSS 182894592 B. Evidence `workspace/d5_g1_l1_discriminator_r1_a9a6bcf3/`; report `G1_L1_ESTIMATOR_DISCRIMINATOR_R1.md`.
- Lifecycle [decision]: terminal `L1_BP_THRESHOLD_NOT_RECOVERABLE_AT_N64`; `next_gate` `-> D5_ROUTE_STOP_REVIEW`. No code (not recoverable), production untouched, four-file suite 259 passed, formal G1 unchanged, authorizations false, G2 absent, no push.

## 2026-09-08 V72P2D5 D5 route-stop acceptance (current-path stop, decomposition successor)

- Acceptance [decision]: `D5_ROUTE_STOP_REVIEW_PASS` accepted (`D5_ROUTE_STOP_ACCEPTANCE_R1.md`); terminal `D5_CURRENT_TWO_LAYER_RATE_MOTHER_BP_PATH_STOPPED`; reason `ACCEPTED_G1_NO_SIGNAL_PLUS_CAL_ONLY_L1_DISCRIMINATOR_NO_USEFUL_RECOVERY`; scope exactly the current fixed high-five/low-five two-layer rate-mother/BP path.
- Lifecycle [decision]: GF32/NB-LDPC open; formal G1 accepted completed-no-signal unchanged; G2 unauthorized/absent; successor is the reversible 5+5 decomposition discriminator. `next_gate` `D5_ROUTE_STOP_REVIEW -> D5_DECOMPOSITION_SUCCESSOR_PREREG`. No push.

## 2026-09-08 V72P2D5 decomposition successor R1 (no N64 recovery, graph/mother route next)

- Result [repo-observed]: prereg `e4d3af7` before scores/calls; 252 CAL-only (chain ≤8.88e-16, joint invariant 7.162347, control CE_L1 3.814742 = c1 E1); rank-1 IS current mapping `(5,6,7,8,9)` m=(59,52). 192/600 calls: APP 0/8 everywhere; oracle-L2 6/8+8/8 rank-1 only (diagnostic); 0 crash/nonfinite/disagreement; four-file suite 259 passed. Evidence `workspace/d5_decomposition_successor_r1_c765e3010674/`.
- Lifecycle [decision]: terminal `DECOMPOSITION_NO_N64_RECOVERY`; no code/OpenSpec (§4.6 not-strong). `next_gate` `-> D5_GRAPH_MOTHER_SUCCESSOR_PROPOSAL` (main-thread proposal, not authorized). Formal roots unchanged, authorizations false, no push.
## 2026-09-09 V72P2D6 R1c-A3 post-run verifier rework (blocked run)

- Result [repo-observed]: A3 repaired the A2 verifier by OpenSpec amendment (key +`n`, stage-separated recompute, crash precedence, EMPTY confirmation, stored+recomputed fail-closed report); corrected `--verify` once on the immutable root: exit 0, 15/15 PASS, `stored D6_GRAPH_TOPOLOGY_NO_USEFUL_RECOVERY` vs `recomputed D6_GRAPH_STRUCTURE_INVARIANT_BLOCKED degree-invariant:64`, agreement False. 184 rows reconcile; 64 attempted degree crashes from degree-1 check rows in frozen T3/M1 graphs. Focused 42/42; seven-file non-perf 323/323.
- Lifecycle [decision]: Pre-RESULT `PASS_BLOCKED_RUN` (blocked attempt, never topology evidence); `next_gate` `-> D6_GRAPH_MOTHER_R1C_A3_BLOCKED_AWAITING_MAIN_THREAD_ROUTE`. Zero decoder calls in A3; authorizations false; G2 absent; no push.
## 2026-09-09 V72P2D6 R1c-A4 structure performance (READY)

- Result [repo-observed]: scaling structure 10897.7 s -> 2.5 s (≈4280x, T2 pruning + two-build replay + overflow passthrough; T2 semantics untouched); n64 outputs exactly equal (21.0 s vs 42.2 s); RSS ≈ 90 MB; zero decoder calls. Equivalence vs committed A2 evidence exact. Focused 51/51; seven-file non-perf 332/332.
- Lifecycle [decision]: performance review `PASS` -> `READY_FOR_FUTURE_D6_PRE_EXECUTE_REVIEW` (structure path only). No execution authorized; authorizations false; G2 absent; no push.
## 2026-09-10 V72P2D6 R1c-A5 validity closure + repair infeasibility + R1d readiness (eligible-only)

- Result [repo-observed]: independent 144-cell matrix (8 arms x widths x layers x prefixes) proves the frozen gate never checked check-node degree: T3/T4/M1 carry degree-1 rows at f1.2+square everywhere (10-81 cells), M1 exactly at the zone-counting bound (zone-1 rows below, all 6 cells); T2 rank-deficient at every square (63/62, 123/122, 246/240); B0/B1 bounds (n128-L2 dup, n256 f1.0 disconnection) recorded unmodified. Frozen eligible + A2 selection {B0,B1,T1,T3,M1} reproduced exactly (132/132 cross-check, 51/51 recompute, committed JSON match). I1 gate landed (eligible-AND, dispatch guard, verify INFO/PASS-FAIL); crash-precedence terminal landed. Repair study: 0/10 sandbox rules admissible (R-T3-03/R-T4-03/R-M1-01 are byte-identical non-repairs; rest fail R3) -> `STRUCTURALLY_INFEASIBLE_AS_FROZEN` + 3-option `REQUIRES_MAIN_THREAD_RULING` menu, nothing landed. Production builders byte-identical. Historical root verify exit 0, 15/15, agreement False, mtimes intact. Focused 56/56; seven-file 90/90 (membership reconstructed and named).
- Lifecycle [decision]: reviews `PASS_ELIGIBLE_ONLY_BRANCH` x2 (validity); R1d package `NOT_AUTHORIZED`; `next_gate` -> `D6_GRAPH_MOTHER_R1C_A5_TRACK_A_COMPLETE_TRACK_B_PENDING`. Zero decoder calls; authorizations false; G2 absent; no push.
## 2026-09-10 V72P2D6 R1c-A6 exact-equivalent T2 acceleration (PASS, 20-35x)

- Result [repo-observed]: staged/vectorized/integer-encoded T2 (`_build_T2_support_fast`, reference intact, no float, no key/order change) proven exactly equal (n64 live-ref, n128/n256 replay-verified fixtures, committed n64 rows, traces, seq==par, A4 guards green). Task walls: n64 1.2 s (<=5), n128 26.6 s (<=90), n256 516.1/479.7 s (<=600); factors 34.5x/24.7x/19.9x; n64 all-8 1.5 s (<=8); fb-only 0.6/1.3 s vs A4 2.5/2.7 s; RSS ~93 MB; zero decoder calls. Slow-task inventory measured (v38 T0 2.0 s, T1 812/810 s, orchestration 345/344 s, lane-A ~40 s, helpers <=46 ms; V30R 74.8/719.9 s cited, not re-runnable). Focused 61/61 + slow n256 cell; seven-file 95/95.
- Lifecycle [decision]: performance review `D6_R1C_A6_REVIEW_PASS` (no NOT_MET). `next_gate` -> `D6_GRAPH_MOTHER_R1C_A5A6_COMPLETE_AWAITING_MAIN_THREAD_RULING`. No execution authorized; authorizations false; G2 absent; no push.
## 2026-09-10 V72P2D6 R1d Option C freeze (eligible-only {B0,B1,T1}, Pre-EXECUTE pending)

- Ruling [repo-observed]: main-thread Option C — no SC/M knob lift; SC/accumulator inadmissible as frozen; R1d exactly {B0_D5_DV3_NATIVE, B1_D5_DV3_COMMON_LABELS, T1_PEG_DV3} (B0/B1 controls, T1 sole new arm, T1-only scaling fallback); T2 rank-bound record only; no A2 call/root reuse; schema `r1d-v2` (`row_degree_min`, `rows_below_degree_2`, version marker) for new roots, A2 immutable old-schema.
- Freeze [repo-observed]: OpenSpec `v72p2d6-gf32-graph-mother-r1d-option-c` + `D6_GRAPH_MOTHER_OPTION_C_ACCEPTANCE_R1.md` (A/B rejection + 22/22-cell validity proof, 0 conflicts) + `D6_GRAPH_MOTHER_R1D_EXECUTION_PACKET_R1.md` (exact `--r1d` command, 552-call worst case, budgets/stop-rules, no-reuse, claim ceiling).
- Lifecycle [decision]: `next_gate` -> `D6_GRAPH_MOTHER_R1D_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. R1d NOT authorized, NOT executed; no R1d root. Authorizations false; G2 absent; no push.
## 2026-09-10 V72P2D6 R1d Option C implementation + Pre-EXECUTE (PASS, awaiting explicit authorization)

- Result [repo-observed]: eligible-only layer landed additive-only (mother +121 pure-append; dev `--r1d` default-off, A4 callsite pins green); 13 R1d tests cover all 12 packet properties; focused D6 + seven-file non-perf 356/356 green (fresh `workspace/d6_r1d_tests_*` basetemp; perf-v38 skipped, out-of-scope deps). Independent subset re-derivation 22 == 22, live spot-check pass. Reviews `D6_R1D_IMPLEMENTATION_REVIEW_PASS` (0 rework) then `D6_R1D_PRE_EXECUTE_REVIEW_PASS_AWAITING_EXPLICIT_AUTHORIZATION` (grants nothing). Zero decoder calls; no R1d root; A2 immutable git-clean old-schema; no A2/VOID/formal reuse.
- Lifecycle [decision]: R1d NOT authorized, NOT executed; `next_gate` unchanged (`D6_GRAPH_MOTHER_R1D_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`). Separate explicit grant + mandatory Pre-RESULT review required. Authorizations false; G2 absent; no push.

## 2026-09-10 D7-A GF32 decoder certification PASS (tiny-synthetic only, no production change)

- Verdict [decision]: D7_A_DECODER_CERTIFICATION_PASS — historical decode_row_layered_fftqspa matches independent poly-37 oracle within tol 1e-10 (check-update <=3.3e-16, tree posterior <=6.7e-16, loopy per-sweep <=7.2e-13); final_beliefs is log-domain so _softmax_rows in _run_layered_block is correct (no double-exp); zero production diff, no trace hook.
- Next [decision]: D7_B_EASY_REGIME_PACKET_FREEZE readiness only; D7-B/C/D execution, R1d, G1, G2 unauthorized. R1d stays R1D_PAUSED_PENDING_DECODER_CERTIFICATION.
- Scope note [repo-observed]: D7-A oracle comparison_bench/src/comparison_bench/formal_ir/v72p2d7_gf32_decoder_certification.py + comparison_bench/tests/test_v72p2d7_gf32_decoder_certification.py (14/14); pre-existing unrelated failure test_qldpc_reference_source_is_not_mutated from CRLF churn, untouched.
## 2026-09-10 D7-B easy-regime freeze + harness + Pre-EXECUTE PASS (no execution)

- Freeze [decision]: R1+A1 64-cell matrix (caps [1,2,4,8,16,32,90], 420-call stop, 120/1500/1800+30s, <2GiB); TREE_6 active literal rows [3,3,2] c0=[0,1,2]/[1,7,13] c1=[2,3,4]/[29,1,7] c2=[4,5]/[13,29] (V=9, E=8, rank 3, nine proofs pass); superseded [2,3,2]/7-edge rejected by test (7<8), never dispatched; dual tree-exact (never 32^6/production).
- Evidence [repo-observed]: harness + 19 tests + runner; D7-A oracle reused, v35/D5 untouched; tiers 19/19 D7-B, 14/14 D7-A, 25/25 v35, field 13/14 (known CRLF pin failure); RSS 85139456; timeout rehearsal 124; out-of-repo sentinel probe zero scientific calls; unauthorized refuses, no root; reviews IMPLEMENTATION_PASS then PRE_EXECUTE_PASS_AWAITING_EXPLICIT_AUTHORIZATION (0 rework).
- Lifecycle [decision]: D7-B NOT authorized/NOT executed; `next_gate` -> `D7_B_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. R1d paused; G1/G2 absent; no push.
## 2026-09-10 D7-B WSL launch binding rework + renewed Pre-EXECUTE PASS (no execution)

- Disposition [decision]: spent R1 UUID `0f1ad3ec-...` (exit-3 relative-import ImportError) retained as `D7_B_PRE_EXECUTION_LAUNCH_BINDING_BLOCKED` (launch defect; no terminal/count/result); return + BLOCKED pre-result review + disposition committed (T0 `13c1c3c`); authorization lifecycle `ce52ac5`→invoke→`9e41e0d` preserved exactly, never reused.
- Repair [repo-observed]: runner-local src setup only (`scripts/v72p2d7_gf32_easy_regime.py` +4: `<repo>/comparison_bench/src` from resolved `__file__`, insert-if-absent; T2 `04b7a8e`); core/v35/D5/D7-A/field byte-unchanged; core fallbacks stay `except ModuleNotFoundError`-only. Reusable failure pattern in `docs/troubleshooting.md`: never file-load a relative-import module as top-level; keep absent-package fallbacks narrow.
- Evidence [repo-observed]: L01–L12 zero-decoder green (miniature original-failure capture; help/dry-run both cwds, 64 cells; src-only insertion; exact package-loaded v35 bind never called; fake-shadow refusal; unauthorized exit 3 pre-bind; frozen contract; roots/auth unchanged); full D7-B 31/31, D7-A 14/14, v35 milestone 25/25. WSL canonical (venv python 3.12.3, NumPy 2.4.4, kernel 6.18.33.2-WSL2, GNU timeout 9.4); WSL-A1 addendum freezes shell-spelling-only command; no new UUID. Reviews `D7_B_WSL_LAUNCH_REWORK_REVIEW_PASS` (0 repair) then `D7_B_PRE_EXECUTE_REVIEW_PASS_WSL_R2_AWAITING_FRESH_AUTHORIZATION` (grants nothing). Local pytest absent in WSL venv (installs forbidden) so suites ran via an uncommitted /tmp shim; committed L10 shells plain `python -m pytest`.
- Lifecycle [decision]: documented gate `D7_B_WSL_READY_AWAITING_FRESH_EXPLICIT_AUTHORIZATION` (docs only; `cycle_state.yaml` untouched: auth false, attempts/completed 0/0, decoder/result false). Future run needs fresh explicit user authorization with one new UUID. R1d paused; G1/G2 unauthorized; no push.
- Lifecycle [decision]: D7-B WSL R2 (`c605d1e6-...`) accepted with stored terminal `D7_B_RESOURCE_OVERRUN` retained; scope exactly `HARD_DECISION_EASY_REGION_OBSERVED_WITH_RESOURCE_AND_SOFT_BELIEF_LIMITATIONS` (64/64 exact+syndrome at cap 1; 49 iter-0 + 15 iter-1; posterior tol failed, MAP agreed; RSS null = telemetry unknown, no measured breach, no <2GiB PASS). `d7b_r2_accepted true`; `next_gate` → `D7_B_EARLY_EXIT_SOFT_BELIEF_AUDIT`. All authorizations false; R1d/G1/G2 absent; no push.
- Evidence [repo-observed]: acceptance `D7_B_RESULT_ACCEPTANCE_R2.md` (§3 twelve points); review `D7_B_PRE_RESULT_REVIEW_PASS_R2`; R2 root five files (111/44743/1008/80/449) byte-identical across two reads, untouched; zero decoder calls, zero production edits.
- Lifecycle [decision]: D7-B early-exit soft-belief audit classified `D7_B_MIXED_METRIC_AND_INTERFACE_DEFECT` + `D7_B_RSS_TELEMETRY_DEPENDENCY_GAP`; review `D7_B_EARLY_EXIT_SOFT_BELIEF_AUDIT_REVIEW_PASS` (E06 transcription: 25 it0 + 4 TREE PAIR it1 at 0.00689, total 29 unchanged); `next_gate` → `D7_B_LAYER_INTERFACE_CORRECTION_PROPOSAL`. All authorizations false; R1d/D7-C/D/G1/G2 absent; no push.
- Evidence [repo-observed]: audit `D7_B_EARLY_EXIT_SOFT_BELIEF_AUDIT_R1.md` (E01–E12, 49/15, zero decoder); review `D7_B_EARLY_EXIT_SOFT_BELIEF_AUDIT_REVIEW_R1.md`; R2 root five files unchanged; terminal `D7_B_RESOURCE_OVERRUN` retained.

## 2026-09-11 D7-B layer-interface proposal PASS + D7-C bidirectional-oracle freeze/implementation/reviews (no execution)

- Proposal [decision]: Phase P froze OpenSpec `v72p2d7-layer-interface-belief-provenance` + `D7_B_LAYER_INTERFACE_CORRECTION_PROPOSAL_R1.md` (`86f6baf6`); independent review issued the sole allowed PASS `D7_B_LAYER_INTERFACE_CORRECTION_PROPOSAL_PASS_D7_C_NONBLOCKING`. Preferred alternative A exposes `belief_provenance` enum `PRIOR_ONLY`/`CHECK_UPDATED`/`WARM_START_UNSPECIFIED`; cross-layer APP consumers fail closed unless `CHECK_UPDATED`. Interface implementation mandatory before any sequential/alternating/joint cross-layer APP route, not before D7-C; no historical result reinterpreted; no v35 stopping change. D7-B documented next route `D7_C_BIDIRECTIONAL_ORACLE_PACKET_FREEZE_INTERFACE_REWORK_DEFERRED`.
- Inventory [repo-observed]: 22 production/interface `final_beliefs` entries + V64 runner extension (`scripts/execute_v64_fresh_verify.py:188`); sibling `nonbinary_v10_fftqspa.py` excluded (different probability-domain contract, no `final_beliefs` field). Defect chain E02/E03/E08/E09: cold row-layered iteration-0 return is the untouched log-prior; D5 `_run_layered_block` forwards `softmax -> app_fed_l2_prior` unconditionally with no `iterations == 0` guard.
- Freeze [decision]: D7-C R1+A1 frozen (commits `0c304875` OpenSpec/prereg/execution packet; `391fc6b0` module/tests/runner; `ca00b234` implementation review; Pre-EXECUTE review committed separately, SHA not recorded here). n=64; seeds `2026091300..2026091315`; f `[1.0,1.2]`; L1 rows 49/59, L2 rows 43/52; D5-native mothers `build_dv3_nested_support(64,64,49,2026090501)`/`(64,64,43,2026090502)` + `assign_gf32_coefficients`; 128 calls in fixed order; budgets 120 s/1500 s/1800 s+30 s/<2 GiB; six-file scalar output; four single-layer priors direct from `J`; iteration-0/current belief labeled only `PRIOR_ONLY_CURRENT_BELIEF`; no cross-layer belief flow.
- Estimator [decision]: H03 accepted estimator uniquely `d5.prepare_model_f_prior_candidate` / `build_f_model_concentration`, `LAMBDA_STAR=137.3823795883264` (per-Bob-column total concentration); rejected `prepare_model_f_prior`/`build_f_model` (per-cell pseudocount, `LAMBDA_APPLICATION_CONTRACT_DEFECT`).
- Reviews [repo-observed]: `D7_C_IMPLEMENTATION_REVIEW_PASS` (0 rework, C01–C20, 20/20 tests) then `D7_C_PRE_EXECUTE_REVIEW_PASS_AWAITING_EXPLICIT_AUTHORIZATION` (128-matrix, external-cwd sentinels, stdlib RSS KiB→bytes, unauthorized refusal before decoder/Model-F/root, protected metadata identical). Reusable env notes: combined multi-file pytest hits a pre-existing `comparison_bench` namespace collision -> run suites per-process; bare `python` absent from default WSL PATH -> the future authorized run must declare the same venv-on-PATH adapter used for D7-B R2; per-call watchdog is post-hoc measurement + outer GNU timeout; six-file verifier checks only internal consistency of the six files.
- Lifecycle [decision]: D7-C NOT authorized, NOT executed. All authorization false; no UUID; no `workspace/d7_c_bidirectional_oracle_*` root; D7-B R2 root `c605d1e6-8577-4c52-a865-12500fc8c964` immutable; R1d paused; G1/G2 unauthorized. `next_gate` `D7_C_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`; parallel state `LAYER_INTERFACE_IMPLEMENTATION_DEFERRED_BEFORE_CROSS_LAYER_APP`. Mandatory Pre-RESULT review before any result; no push.

## 2026-09-11 D7-C bounded bidirectional-dependence diagnostic accepted (route to D7-D schedule discriminator)

- Acceptance [decision]: `D7_C_RESULT_ACCEPTED_BIDIRECTIONAL_DEPENDENCE_DIAGNOSTIC` per §0 of `D7_C_ACCEPT_D7_D_SCHEDULE_FREEZE_IMPLEMENT_PRE_EXECUTE_R1_TASK_PACKET.md`, recorded in `D7_C_RESULT_ACCEPTANCE_R1.md`. Accepted scope: 128/128 frozen single-layer calls completed, finite, internally coherent; exact and syndrome agreed 128/128, 43 exact; f=1.0 L1 `0/16 -> 10/16`, L2 `0/16 -> 1/16`; f=1.2 L1 `3/16 -> 16/16`, L2 `0/16 -> 13/16`; f=1.2 `STRONG_ORACLE_LIFT` in both layers; terminal `D7_C_BIDIRECTIONAL_DEPENDENCE` accepted as a bounded mechanism-classification result; no crash/nonfinite/resource/watchdog issue; RSS known < 2 GiB; D7-C consumed no cross-layer returned beliefs and is unaffected by the deferred D7-B APP-interface implementation.
- Paired counts [repo-observed]: per-stratum (oracle_only/marginal_only/both/neither) f=1.0 L1 `10/0/0/6`, f=1.0 L2 `1/0/0/15`, f=1.2 L1 `13/0/3/0`, f=1.2 L2 `13/0/0/3`; each sums to 16, no `marginal_only` pair anywhere.
- Evidence [repo-observed]: immutable root `workspace/d7_c_bidirectional_oracle_94c0ea15-a786-4cb8-a991-6fec521cccae` (six files 282/23599/2709/1130/362/728 B, zero subdirs); lifecycle authorize `b07b5441` → one invocation → revoke `d3bd3c8b` → result `b4ba2896`; independent Pre-RESULT `D7_C_PRE_RESULT_REVIEW_PASS_R1`; verifier `VERIFY_OK {'ok': True, 'problems': [], 'records': 128, 'terminal': 'D7_C_BIDIRECTIONAL_DEPENDENCE'}`; outer wall 33.743 s, stored wall 32.631 s, max call 0.439 s, RSS 105172992 B, exit 0.
- Ceiling [decision]: accepted that true other-layer symbols materially improve recovery under the frozen priors/matrices/decoder/disclosures/n=64/16 paired blocks; NOT accepted that an implementable alternating/joint decoder can generate that information, bootstrap from marginal priors, achieve FER, improve leakage/key rate, qualify the code, or generalize beyond this matrix; f=1.0 L2 remains effectively unrecovered even at oracle 1/16; no FER/leakage/key-rate/CAL/qualification/promotion claim.
- Route [decision]: `next_gate` → `D7_D_SCHEDULE_DISCRIMINATOR_PACKET_FREEZE` (D7-D isolates schedule only; do not implement alternating/joint BP). All authorizations stay false; D7-C/D7-B roots immutable; R1d/G1/G2 unauthorized; interface implementation remains deferred before cross-layer APP; no push.

## 2026-09-11 D7-D GF32 schedule discriminator freeze + implementation + dual review PASS (readiness only, no execution)

- Freeze [decision]: OpenSpec `v72p2d7-gf32-schedule-discriminator` + prereg/execution packet committed `3a05899`; discriminator module `v72p2d7_gf32_schedule_discriminator.py` (1395 lines) + tests (1535) + runner `scripts/v72p2d7_gf32_schedule_discriminator.py` (104) + flooding certification doc committed `43f07186`. Frozen matrix: 128 D7-C identities (16 seeds × f{1.0,1.2} × 4 conditions) × schedules `[ROW_LAYERED, FLOODING]` = 256 calls, `call_idx` `2k-1`/`2k`; identical non-schedule inputs within each pair; D7-C constant aliases (`LAMBDA_STAR` etc.); work-normalized check-node/edge updates; five first-match strata + exact ten-entry terminal priority; budgets per-call 120 s / stored wall 1500 s / outer GNU timeout 1800 s + 30 s kill grace / RSS <2 GiB via stdlib `resource`; seven-file scalar future root; frozen future command (no UUID).
- Certification/reviews [repo-observed]: F01–F08 flooding certification all PASS (tiny ≤4-var synthetic, D7-A oracle, tol `1e-10`, no patch); S01–S22 all PASS (30-test suite, 30 passed); `D7_D_IMPLEMENTATION_REVIEW_PASS` (`727bca7a`); `D7_D_PRE_EXECUTE_REVIEW_PASS_AWAITING_EXPLICIT_AUTHORIZATION` (doc written, uncommitted at closeout). Regression scope: D7-A 14 / D5 165 / v35 25 green; D7-B scoped 29 green; D7-C raw 19 passed with stale pre-execution `test_c19` invariant (accepted D7-C root now exists) — non-blocking, S20 deselection scoped, refresh as a separate scoped change.
- Lifecycle [decision]: readiness only — D7-D NOT authorized, NOT executed; pre-closeout `next_gate` `D7_D_IMPLEMENTATION_PENDING`; all authorization flags false (`decoder_executed`/`result_created`/`scientific_promotion` false); no UUID, no `workspace/d7_d_schedule_discriminator_*` root; D7-C root `94c0ea15-...` and D7-B R2 root immutable; `layer_interface_implementation` remains `DEFERRED_MANDATORY_BEFORE_CROSS_LAYER_APP`; R1d/G1/G2 unauthorized; no push. Environmental carry-forward: the future authorized execution must declare the venv-on-PATH adapter (Python 3.12.3 / NumPy 2.4.4 / GNU timeout 9.4) as recorded for D7-C.

## 2026-09-11 D7-D bounded result acceptance (schedule effect inconclusive; route to BP provenance Alternative A)

- Acceptance [decision]: `D7_D_RESULT_ACCEPTED_SCHEDULE_EFFECT_INCONCLUSIVE` per §0 of `D7_D_ACCEPT_BP_INTERFACE_READINESS_R1_TASK_PACKET.md`, recorded in `D7_D_RESULT_ACCEPTANCE_R1.md` after Phase-A A01 independent recomputation (0 discrepancies, root read twice identical). Accepted facts for UUID `64660d16-397d-4ef3-8454-3066d27c12c7`: 256/256 paired calls completed; row-layered exact `43/128`, flooding exact `40/128`, layered-only `3`, flooding-only `0`, both `40`, neither `85` (syndrome-only `3/0/40/85`); no crash/nonfinite/watchdog; stored terminal `D7_D_SCHEDULE_EFFECT_INCONCLUSIVE`; Pre-RESULT `D7_D_PRE_RESULT_REVIEW_PASS_R1`; budgets 120/1500/1800+30 s and RSS `<2 GiB` passed.
- Ceiling [decision]: no preregistered flooding or layered advantage; `43 vs 40` and the three layered-only identities (26 `1.0/2026091306/L1_ORACLE_U2`, 46 `1.0/2026091311/L1_ORACLE_U2`, 101 `1.2/2026091309/L1_MARGINAL`) are reported, not promoted to schedule superiority; schedule choice is not the dominant failure explanation; D7-C oracle dependence remains stronger route evidence but does not prove alternating/joint BP bootstrap; no FER/leakage/key-rate/qualification/promotion/general-equivalence/general NB-LDPC claim.
- Evidence [repo-observed]: immutable root `workspace/d7_d_schedule_discriminator_64660d16-397d-4ef3-8454-3066d27c12c7` (seven files 3164/57659/17690/1777/1546/455/290 B, zero subdirs); lifecycle authorize `7a3f0d92` → one invocation → revoke `eba385bb` → result `63a69f57`; verifier `VERIFY_OK {'ok': True, 'problems': [], 'records': 256, 'terminal': 'D7_D_SCHEDULE_EFFECT_INCONCLUSIVE'}`; eight labels `EXACT_TIE_LOW, MIXED_SCHEDULE_EFFECT, EXACT_TIE_LOW, EXACT_TIE_LOW, EXACT_TIE_LOW, EXACT_TIE_HIGH, EXACT_TIE_LOW, EXACT_TIE_HIGH`; outer wall 67.178 s, stored wall 65.945 s, max call 0.436 s, RSS 105304064 B.
- Route [decision]: `D7_D_SCHEDULE_EFFECT_INCONCLUSIVE` has no frozen automatic successor; this ruling selects Alternative A (explicit belief provenance plus fail-closed cross-layer consumers) as the next mainline action; `next_gate` → `BP_INTERFACE_PROVENANCE_IMPLEMENTATION`. R1d stays `PAUSED_OPTIONAL_LOCAL_CONFIRMATION_NOT_MAINLINE_GATE` (not a mainline gate); G1/G2 unauthorized; old D5/D6 checkboxes are historical accounting. Dimension/bw expansion waits for a working provenance-safe fixed-dimension mechanism and, for more than two layers, a separate mathematical/leakage contract. No forced sweep, warm-start, alternating/joint decoder or scientific run; no D7-E work; all authorizations false; no push.
## 2026-09-11 NB-Polar Phase 3-R1 execution authorization

- Phase 3-R1 construction recovery is the active NB-Polar task. Implementation
  and separated TRAIN/DEV work are authorized under
  `.workbuddy/queue/NBPOLAR-PHASE3-R1-CONSTRUCTION-RECOVERY/`.
- A single fresh synthetic EVAL is allowed only after a real independent
  reviewer-go PASS on the final frozen contract. Seed 2026091203 and the old
  diagnostic root are never rerun or reused.
- Model-F, real data, Phase 4, benchmark/result roots, scientific promotion,
  commit, and push remain unauthorized.
## 2026-09-11 NB-Polar Phase 3-R1 bounded diagnostic acceptance

- Independent Pre-RESULT review passed with comments. The sole fresh synthetic
  EVAL used O3 analytic, q32/N256, erasure eps=0.05, K45, seed 2026091213:
  299/300 exact, impossible 1 at block 219, initial-error 300/300, other/nan 0.
- Accept only `EVAL_ACCEPTED_DIAGNOSTIC`. It does not establish unique N/K
  causality, Model-F/real-data performance, leakage, key rate, qualification,
  promotion, or permission for Phase 4.
- Seed 2026091213 and `eval_r1_fresh/` are consumed and immutable. The old
  seed-2026091203/block-104 result remains a procedure-invalid diagnostic.
## 2026-09-11 NB-Polar Phase 4-P0 prior contract FREEZE_ACCEPT

- Reviewer-go passed P0-1..P0-6 with four non-blocking wording/hygiene comments;
  the main thread accepts the per-Bob-column concentration formula, explicit
  axes/packing, dense SymbolMetric MVP, six pure helpers, evidence separation,
  truth isolation, and V-P0-01..12 as the implementation contract.
- Phase 4-P1 is deliberately limited to pure adapter code plus synthetic
  V-P0-01..07 and an independent formula oracle. CAL, Model-F, DEV/EVAL,
  decoder execution and performance claims require a later separate packet.
## 2026-09-11 NB-Polar P1 sentinel-conflict ruling

- P3-T1-09 over-scanned `__init__.py` for `from .prior`, conflicting with the
  accepted Phase 4-P0 export. Option (a) scopes only that prior ban to
  `synthetic.py`/`construction.py`; common legacy/protocol/result bans still
  cover the original files. Do not use import-spelling evasion.
- Post-ruling evidence: full focused suite 66/66 and independent prior suite
  11/11. P1 is an implementation candidate; P2/CAL/decoder remain unauthorized.
## 2026-09-11 NB-Polar Phase 4-P1 synthetic adapter accepted

- Reviewer-go ACCEPT plus 66/66 full focused and independent 11/11 prior tests
  support `IMPLEMENTATION_ACCEPTED_SYNTHETIC_ONLY` for the dense pure adapter
  and V-P0-01..07.
- CAL, Model-F, empirical-prior decoding, DEV/EVAL, FER/leakage/key-rate and P2
  remain outside this acceptance. P2 authorization flags are all false.
- Defer the `__all__` comment, package docstring and troubleshooting heading
  nits until a later already-authorized edit; do not churn accepted code alone.
## 2026-09-11 NB-Polar WorkBuddy authorization handoff rule

- Every next packet includes TASK_PACKET.md, PROMPT.md,
  AUTHORIZATION_PROMPT.md and STATUS.yaml. When authorization is next, paste
  the entire copyable grant in chat; a link is not enough.
- Main thread continues after operator/reviewer returns: adjudicate, update
  durable docs/memory, and prepare the next complete packet.
- Phase 4-P2 reads only the accepted sibling Model-F input root after synthetic
  qualification and independent Pre-EXECUTE review; no SC/raw data/DEV/EVAL.
## 2026-09-11 NB-Polar P2 diagnostic index failure

- P2 attempt 1/1 passed the accepted artifact loader, then failed only in the
  entropy diagnostic: `[U1,B,U2]` was indexed on U2 instead of B. No output was
  created; no SC/Model-F/raw data ran.
- Preserve the BLOCKED attempt. P2-R1 requires `f3[u1,nz_b,:]`, asymmetric
  tests and a loop oracle before one separately authorized successor read.
## 2026-09-12 NB-Polar P2-R1 CAL prior validation accepted

- R1 corrected `[U1,B,U2]` indexing and passed 88 tests plus independent
  Pre-EXECUTE/Pre-RESULT review. The sole read produced two compact summaries;
  formula error 0, chain discrepancy 8.88e-16, no SC/raw data.
- Accept only CAL prior-table/entropy bookkeeping. Both P2 attempts are
  consumed. P3 remains separately authorized and model-sampled only.
## 2026-09-13 NB-Polar Phase 4-P3 Stage B empirical-prior SC interface ACCEPTED

- Acceptance [decision]: main thread accepts the reviewed candidate as
  `EMPIRICAL_PRIOR_SC_INTERFACE_ACCEPTED`, limited to model-sampled interface
  consistency. Sole Stage B execution exit 0, wall
  17.645 s, peak RSS 0.2329 GiB, 6/6 hard gates true; independent Pre-RESULT
  `PASS_WITH_COMMENTS`. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/`
  holds exactly five files (frozen_plan.json, oracle_records.json,
  stress_and_profile.json, diagnostic_summary.json, report.md).
- Accounting [decision]: artifact-content attempt 1/1 consumed on first content
  open; seed 2026091316 consumed; unit 2026091314 / TRAIN 2026091315 not used;
  no rerun allowed; frozen budget 3600 s total / 120 s per case / <2 GiB.
- Executed [repo-observed]: 328 blocks = B1 128 (N=2/4, 64 each) + B2 160
  (N=16/64, 5 masks x 16) + B3 40 (N=256, 5 masks x 8); exact 48 (B1 9 / B2 31
  / B3 8); non-exact 280; resource_abort 0, nonfinite 0, truth-leak 0.
- B1 oracle [repo-observed]: vs independent exhaustive oracle max prob err
  1.11e-15 (tol 1e-12), max log err 5.33e-15 (tol 1e-9), support mismatch 0,
  numeric 0. B3 initial-MAP-error 40/40.
- B4/B5 [repo-observed]: B4 medians at N=64/256/1024 (M5 first N//2, 5 reps)
  metric 3.80e-5/4.31e-5/1.18e-4 s, decode 0.00776/0.0345/0.1675 s; B5
  non-exact attribution SC_decision 119 + expected_under_disclosure 161 = 280,
  all other categories 0, unattributed 0.
- Scope [decision]: interface/mechanism diagnostic only — no FER, leakage,
  reconciliation, key rate, construction/K or performance claim; input is the
  sibling Model-F artifact
  `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz`
  (LAMBDA_STAR 137.3823795883264).
- Locations [repo-observed]: P3 code
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/` (empirical_channel.py,
  empirical_oracle.py, empirical_diagnostic.py); tests
  `comparison_bench/tests/test_nbpolar_empirical_sc.py` — focused 32 passed,
  8-file predecessor suite 120 passed.
- Environment [repo-observed]: this checkout has no repo-local `.venv`; accepted
  runtime is `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (numpy 2.5.3,
  pytest 9.1.1). pytest needs `-p no:cacheprovider --basetemp=<fresh /tmp path>`
  because pytest.ini's Windows basetemp path is unusable in WSL.
- Workflow lesson [decision]: the stale planning draft
  `openspec/changes/formal-ir-nbpolar-mvp/P3_STAGEB_FREEZE.md` must not govern
  execution; the authoritative freeze is the packet-local
  `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/P3_STAGEB_FREEZE.md`.
  F-1 (B5 attribution-precedence text vs classifier) was repaired docs-only and
  re-reviewed before the artifact-content read.
- Next gate [decision]: Phase 5 static-protocol OpenSpec and WorkBuddy packet
  are frozen all-false awaiting explicit authorization. No real data,
  adaptation, SCL, Phase 6, qualification or promotion is opened.
## 2026-09-13 NBPOLAR-PHASE5-STATIC-PROTOCOL development ACCEPTED

- Acceptance [decision]: `STATIC_PROTOCOL_DEVELOPMENT_ACCEPTED`, limited to
  the single reviewed synthetic development run; qualification and promotion
  are not granted. Implementation
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/protocol.py`
  (GF32 polynomial 37, alpha=2, N=256, erasure eps=0.05, K=45) + thin adapter
  `comparison_bench/src/comparison_bench/methods/nbpolar_static.py`
  (FrameBatch/IRRunConfig/IRRunResult signatures unchanged; beta_eff derived)
  + tests `comparison_bench/tests/test_nbpolar_protocol.py` (16 new; suite
  total 136 = 16 + 120 predecessor).
- Frozen protocol [candidate]: static disclosure K=45 =
  `construction.analytic_order(0.05, 256)[:45]` worst-first, publishing actual
  GF32 U values including zeros; exactly one `sc_decode` per block; 10-bit
  physical label `label = 32*x_hat` over a 2560-bit message; at most one 64-bit
  Toeplitz tag after decode from a deterministic public per-block seed stream
  (master 2026091318, SHA-256 counter derivation, 2623 seed bits/block);
  disjoint outcomes {exact, undetected, verify_failed, decode_failed,
  resource_abort} with nested verified/verification_invocations and an
  independent transcript recount.
- Rulings [decision, 2026-09-13]: R1 disclosed set = first 45 of the worst-first
  analytic order (packet "disclose its complement" wording superseded); R2
  label domain = 10-bit embedding 32*x_hat (tag message 2560 bits, seed 2623
  bits/block).
- Sole gate execution [repo-observed]: 300 blocks, exit 0, wall 4.998916 s,
  peak RSS 111190016 B (<2 GiB); exact 300 / undetected 0 / verify_failed 0 /
  decode_failed 0 / resource_abort 0; one-sided 95% Wilson exact-recovery lower
  bound 0.9910621278248719 (threshold 0.90); key-dependent total 86700 bits
  (avg 289/block < 2560), public control 786900; transcript recount mismatch 0;
  truth-leak 0; 11/11 gates true. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate/`
  holds exactly five files (frozen_plan.json, per_block_outcomes.json,
  transcript_accounting.json, aggregate_summary.json, report.md).
- Accounting [decision]: attempt 1/1 consumed at the first scientific
  `sc_decode` call; run seed 2026091317 consumed; master 2026091318 is public
  control; no rerun. Budget 300 s total / 5 s per-block soft cap / 600 s
  external timeout / <2 GiB. Packet and OpenSpec locations:
  `.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/` and
  `openspec/changes/formal-ir-nbpolar-phase5-static-protocol/`.
- Scope [decision]: synthetic development signal only — no real-data FER,
  leakage efficiency, key rate, qualification, promotion, adaptive disclosure,
  SCL/CRC, benchmark or Phase 6. Next gate is Phase 6 rate-adaptation contract
  freeze; Phase 6 remains unauthorized.
- Successor freeze [decision]: Phase 6 uses fixed nested worst-first sizes
  29/33/37/41/45, restart-from-scratch SC and one tag per invoked level. Tag
  mismatch may advance only to the immediate next frozen level; it never ranks
  candidates or alters decoding. The paired synthetic gate requires >=285/300
  exact, Wilson LB >=0.90, undetected 0 and >=5% average key-dependent-bit
  reduction versus same-block static K45. Packet/OpenSpec prepared all-false;
  no Phase 6 attempt or seed consumed.
- Environment/reusable [repo-observed]: unchanged from the 2026-09-13 P3 entry
  (accepted interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`;
  pytest `-p no:cacheprovider --basetemp=<fresh /tmp path>`); running the
  protocol module emits a benign RuntimeWarning because `nbpolar/__init__.py`
  re-exports it.
## 2026-09-13 NBPOLAR-PHASE6-FIXED-INCREMENTAL BLOCKED(incremental_exact_ge_285) — negative result, no acceptance

- Implementation [repo-observed]:
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py`
  (frozen nested worst-first K=(29,33,37,41,45) =
  `analytic_order(0.05,256)[:K_i]`, publish only new actual GF32 U values with
  each coordinate counted once; every invoked level restarts `sc_decode` from
  scratch on the original metric with the cumulative known set) + thin adapter
  `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py` +
  tests `comparison_bench/tests/test_nbpolar_incremental.py` (17 new; suite
  153 = 17 + 136 predecessor).
- Frozen mechanism [decision]: one independent 64-bit Toeplitz tag per invoked
  level over the 2560-bit `label = 32*x_hat` domain; tag match accepts the
  current candidate and terminates, mismatch advances exactly one level, final
  mismatch is verify_failed; decode/numeric failure stops fail-closed;
  per-arm/per-block/per-level public seed derivation via SHA-256 counter stream
  from master 2026091341; key_dependent = 5*K_j + 64*j; feedback control
  counted as 1 public bit per advance; tag union bound = tag invocations x
  2^-64.
- Sole paired gate execution [repo-observed]: 300 blocks, single attempt, exit
  0, wall 9.619874 s; run seed 2026091340 consumed at the first `sc_decode`.
  Static K45 arm exact 298/300, avg 288.573333 key-dependent bits, Wilson LB
  0.9800565738801275; incremental arm exact 271/300, decode_failed 29 (all
  `ImpossibleDisclosedValueError` at level 0), undetected 0, avg 207.293333
  bits (-28.17%), Wilson LB 0.8715597837542944; 18 gates 16 true / 2 FALSE
  (`incremental_exact_ge_285`: 271 < 285; `incremental_wilson_lower_ge_0_90`:
  0.87156 < 0.90); candidate null; result `BLOCKED(incremental_exact_ge_285)`;
  main-thread disposition pending. Disclosure saving real but not sufficient;
  public control 1534471 bits (static seed 781654 + incremental seed 752801 +
  feedback 16); truth-leak 0, nonfinite 0, recount mismatch 0. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE6-FIXED-INCREMENTAL/paired_incremental_dev_gate/`
  holds exactly five files (frozen_plan.json, aggregate_comparison.json,
  per_block_paired_outcomes.json, transcript_accounting.json, report.md).
- Mechanism [decision]: with fewer disclosed coordinates (K=29) a wrong early
  hard decision can make a later true disclosed value zero-support in the
  accepted `sc.py`, raising `ImpossibleDisclosedValueError`; the frozen
  fail-closed rule terminates the block instead of advancing, costing ~10% of
  blocks. The disclosure saving (~28%) is real but the recovery signal is lost
  at the frozen threshold. Valid scheduled science, not an implementation
  defect; no tuning, K/threshold change or rerun is permitted; any design
  revision needs a main-thread/OpenSpec successor packet.
- Review state [decision]: Pre-EXECUTE PASS (4 non-blocking findings) and
  Pre-RESULT PASS_WITH_COMMENTS; both confirmed the two failing gates, the
  mechanism, and that this is a negative development result only.
- Scope [decision]: synthetic paired development signal only — no real-data
  FER, leakage efficiency, key rate, qualification or promotion claim; the
  single attempt is consumed and no rerun is authorized.
- Environment/reusable [repo-observed]:
  `resource.getrusage(...).ru_maxrss` under `ulimit -v 2097152` on this WSL2
  kernel can be corrupted (persisted `rss_bytes_peak` ~1.22 GB while true
  `/proc/self/status` VmHWM ~105 MB) — treat RSS as advisory and prefer VmHWM;
  benign runpy RuntimeWarning when running the protocol via `python -m` because
  `nbpolar/__init__.py` re-exports it; pytest needs
  `-p no:cacheprovider --basetemp=<fresh /tmp path>`; interpreter
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3).

## 2026-09-13 Phase 6 strict-stop negative accepted; R1 successor frozen

- Acceptance [decision]: `FIXED_INCREMENTAL_NEGATIVE_ACCEPTED`; paired static
  298/300 versus incremental 271/300, incremental Wilson 0.8715598, while
  disclosure 207.293 versus 288.573 bits saves 28.17%. Recovery gates fail.
- Attribution [decision]: 29 level-0 `ImpossibleDisclosedValueError` failures
  are valid strict-stop scheduler science, not an SC implementation defect.
  Attempt 1/1 and run seed 2026091340 consumed; public master 2026091341 and
  five-file paired root immutable.
- Successor [decision]: option (a). At non-final levels the impossible decode
  is `decode_rejected_continue`, with no candidate/tag, one feedback request,
  next fixed increment and restart SC. Final K45 remains decode-failed. P6-R1
  OpenSpec/packet prepared all-false; no new attempt or seed consumed.

## 2026-09-13 NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE three-arm gate CANDIDATE (not acceptance)

- Implementation [repo-observed]: extended
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/incremental.py`
  (non-final-level `ImpossibleDisclosedValueError` -> `decode_rejected_continue`:
  no candidate/tag, one public feedback, next increment disclosed, SC restarted
  from the original metric; K45 same error stays terminal `decode_failed`; all
  other exceptions remain fail-closed; strict-stop default path pinned
  unchanged) + adapter
  `comparison_bench/src/comparison_bench/methods/nbpolar_incremental.py`
  (`NBPolarIncrementalR1Method`) + tests
  `comparison_bench/tests/test_nbpolar_incremental_r1.py` (17 new; full NB-Polar
  suite 170 = 120 + 16 + 17 + 17).
- Sole three-arm gate execution [repo-observed, candidate]: 300 paired blocks,
  single attempt, exit 0; run seed consumed at the first `sc_decode` (static arm
  block 0), master public control seed, no rerun. Static K45 arm exact 298/300,
  avg 288.573333 key-dependent bits; strict-stop arm exact 280/300, avg
  214.253333, 20 decode_failed; R1 arm exact 298/300, avg 220.506667 (-23.59%
  vs static), Wilson LB 0.9800565738801275; rejection histogram
  {0:20,1:7,2:3,3:2}; rescued 18 / persisted 282 / regressed 0 / other 0
  (reported identities, no threshold); union bound 5.1228552649940085e-17 over
  945 tag invocations; transcript mismatch 0; truth leak 0; nonfinite 0; 18/18
  gates true; candidate label `DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE`.
  Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE6-R1-DECODE-REJECT-ADVANCE/three_arm_paired_dev_gate/`
  holds exactly five compact scalar-only files (frozen_plan.json,
  per_block_three_arm_outcomes.json, transcript_accounting.json,
  aggregate_comparison.json, report.md).
- Mechanism [decision, candidate]: the R1 semantic delta recovers the
  strict-stop losses caused by K<45 impossible disclosure under a wrong early
  prefix while retaining most of the disclosure saving; K45-level exceptions
  stay terminal and account for the residual 2 decode_failed (same count as the
  static arm).
- Carried non-blocking notes [repo-observed]:
  static-arm `terminating_k` metadata records 29 while key bits/gates use 45;
  the report could state the strict arm is an in-run recomputation.
- Scope/status [decision]: synthetic paired development signal only — no
  real-data FER, leakage efficiency, key rate, qualification, promotion,
  Phase 7, learned policy or SCL; CANDIDATE pending main-thread acceptance, not
  an acceptance/promotion. Environment unchanged from the two 2026-09-13
  entries above (interpreter
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`; pytest
  `-p no:cacheprovider --basetemp=<fresh /tmp path>`; `ru_maxrss` under
  `ulimit -v` is advisory).

## 2026-09-13 Phase 6-R1 accepted; two-layer efficiency gap prioritized

- Acceptance [decision]: `DECODE_REJECT_ADVANCE_DEVELOPMENT_ACCEPTED` in the
  frozen single-layer BEC synthetic scope only. The prior candidate evidence,
  reviews, attempt/seed consumption and immutable five-file root are unchanged.
- Gap [repo-observed]: Phase 5/6 protocol gates use the 10-bit embedding with
  L1 in the high half and constant-zero low half. They do not execute the
  roadmap's oracle-L2(true L1) or operational-L2(candidate L1) paths and do not
  establish whole-system reconciliation efficiency.
- Priority [decision]: Phase 7/SCL is paused. The next all-false packet is
  `NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY`, which adds an explicit
  `f<=1.3` target and a decoder-free per-source N=2^8..2^18 BEC-surrogate
  sensitivity plus L2 execution audit.
- Claim boundary [decision]: a scratch recurrence reproduced N256/epsilon0.05
  K43 and suggested an f≈1.3 crossing near 2^17–2^18. This is unaccepted
  planning evidence until independently reproduced; BEC is not registered as
  a rigorous lower bound for the empirical neighbor-shift channel.
## 2026-09-13 NBPOLAR-PHASE6-R2 two-layer BEC rate feasibility CANDIDATE (decoder-free, no acceptance)

- Implementation [repo-observed, candidate]: decoder-free module
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer_rate.py`
  + tests `comparison_bench/tests/test_nbpolar_two_layer_rate.py` (10 new;
  full NB-Polar suite 180 = 170 predecessor + 10). OpenSpec change
  `openspec/changes/formal-ir-nbpolar-phase6-r2-two-layer-rate-feasibility/`.
- Frozen inputs [candidate]: full-precision per-source L1/L2 entropies from
  `docs/v49_distribution_tables/v49_train_val_hold_nll.csv` TRAIN rows
  (nll_u1/nll_u2; mirrored in `docs/v49-distribution-shift-diagnosis-20260827.md`
  §3.1; chain-verified against the V27R decision-log recomputation and V26 A02
  rows): 1M H1=0.02428054681872374 / H2=0.7767572780789994; 1p5M
  0.02519949687789926 / 0.8003665547438703; 2M 0.025662048796915037 /
  0.8069006731253232. Surrogate mapping `epsilon_l = H_l/5`.
- Method [candidate]: BEC recurrence `z_minus=2z-z**2; z_plus=z**2` natural
  order; minimum worst-first disclosure K per layer with residual union bound
  <= layer budget (equal 0.005/0.005 vs entropy-proportional
  0.01*H_l/(H1+H2)); `nH = N*(H1+H2)`, `leakage = 5*(K1+K2)+64`
  (tag-free variant reported), `f = leakage/nH`, `f<=1.3` target.
- Calibration [candidate]: reproduction of the scratch N=256 / epsilon=0.05 /
  budget=1e-2 -> K=43 exactly (residual 0.0080281681532746, max
  operational-vs-literal difference 0.0); H1-nll vs same-row `ent` alternative
  changes zero K selections.
- Result [candidate]: full 66/66 rows over N=2^8..2^18 x 3 sources x 2
  allocations, all finite, axes complete. First `f<=1.3` crossing is N=2^18
  on all six axes (f 1.2596..1.2670); log2-linear interpolation of the last
  two rows puts the exact crossing at 2^17.20..2^17.36, matching the
  decision-log scratch "near 2^17-2^18". Independently recomputed by
  reviewer-go with zero differences (PASS_WITH_COMMENTS, non-blocking
  citation notes only); CANDIDATE pending main-thread acceptance.
- L2 audit (R2-A07) [candidate]: oracle-L2 (true-L1-conditioned) and
  operational candidate-L2 have never entered SC execution; only the
  single-layer L1 high-plane path (`label=32*x_hat`, low half constant zero)
  has ever run in the accepted P3/P5/P6/R1 gates. `prior.gather_p2_metrics` /
  `derive_p2` and the ORACLE_CONDITIONED / CANDIDATE_CONDITIONED provenance
  values have zero production call sites (test-only), and `sc_decode` accepts
  no L1/L2 conditioning argument. Successor prerequisites (decision output
  only, not implemented): L2 prior extraction per the P0 contract
  (P2_true/P2_hat) plus a two-stage restart SC; a paired two-layer development
  gate with frozen thresholds; empirical construction and a scalable decoder
  for N >= 2^17 (e.g. FWHT q-ary SC), explicitly out of R2 scope.
- Scope/labels [decision]: surrogate planning estimate only — not empirical
  neighbor-shift channel performance, not a rigorous optimistic lower bound,
  not decoder/FER/leakage-efficiency/key-rate evidence, not
  qualification/promotion. No SC call, no artifact/parquet/TTBin read, no
  block sampling, no attempt/seed consumed (attempts 0/0), no commit/push,
  old evidence roots untouched. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY/`
  (`two_layer_rate_sensitivity.json`, `R2_REPORT.md`,
  `INDEPENDENT_RESULT_REVIEW.md`); predecessor gap/priority context is the
  entry above.

## 2026-09-13 Phase 6-R2 accepted; Phase 4-P4 operational L2 frozen

- Acceptance [decision]: `TWO_LAYER_RATE_FEASIBILITY_ACCEPTED`. Reviewer-go
  independently reproduced K43, all 66 rows and all six N=2^18 first-grid
  crossings. No attempt/seed or decoder was used.
- Bound [decision]: retain the BEC table as surrogate planning evidence only;
  the interpolated 2^17.20–2^17.36 crossing is not an empirical-channel or
  decoder result and is not registered as a rigorous lower bound.
- Successor [decision]: before empirical construction, FWHT scaling or SCL,
  execute the missing causal two-stage interface on injected synthetic tables:
  P1 -> L1 SC -> source-domain hard candidate -> P2_hat -> fresh L2 SC -> full
  10-bit label/tag, paired with an isolated P2_true oracle arm.
- Packet [repo-observed]:
  `.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/` and OpenSpec
  `formal-ir-nbpolar-phase4-p4-two-layer-operational-sc` are frozen all-false;
  artifact/real data/N>256/empirical construction/FWHT/SCL remain unauthorized.

## 2026-09-13 NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC two-stage SC gate CANDIDATE (not acceptance)

- Implementation [repo-observed, candidate]: two-stage SC closed loop
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/two_layer.py` plus
  tests `comparison_bench/tests/test_nbpolar_two_layer.py` (12 new; full
  NB-Polar suite 192 across 13 `test_nbpolar_*.py` files); OpenSpec change
  `formal-ir-nbpolar-phase4-p4-two-layer-operational-sc`.
- Two-stage semantics [candidate]: Bob-only P1 (PRIOR_ONLY) -> L1 SC ->
  source-domain hard candidate `high_hat = sc1.x_hat` ->
  `P2_hat = gather_p2_metrics(B, high_hat, p2_table)` (CANDIDATE_CONDITIONED)
  -> fresh L2 SC -> `label = low_hat + 32*high_hat` -> one final 64-bit tag;
  the strictly isolated oracle arm uses true L1 (ORACLE_CONDITIONED) with the
  same D2/U2 disclosures.
- Sole 96-block paired gate [repo-observed, candidate]: run seed 2026091360
  consumed at the first gate SC call (block 0 operational L1); master
  2026091361 public control; candidate label
  `TWO_LAYER_OPERATIONAL_SC_CANDIDATE`; 13/13 hard gates true; both arms
  L1/L2 invoked 96/96; provenance counts 96/96/96 (P1 PRIOR_ONLY, L2
  CANDIDATE_CONDITIONED, L2 ORACLE_CONDITIONED); operational exact 26 /
  verify_failed 70; oracle exact 44 / verify_failed 52;
  undetected/decode_failed/resource_abort 0; truth-leak 0; accounting 839
  bits per fully invoked arm (5*45 + 5*110 + 64), key-dependent total 161088,
  public control 503616 (192 tags x 2623); transcript recount mismatch 0;
  report-only `oracle_candidate_divergence_count` 34/96 is float64
  last-bit inequality of the candidate- vs oracle-conditioned P2 arrays (no
  threshold); artifact wall 10.154709 s; no rerun/tuning. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/`
  holds exactly five scalar-only files (frozen_plan.json,
  per_block_two_layer_outcomes.json, transcript_accounting.json,
  aggregate_summary.json, report.md).
- Model consequence [decision]: the frozen independent-layer-erasure injected
  model makes table-derived `P2` numerically independent of the L1 candidate
  (max row difference 7.771561172376096e-16), so the paired
  operational/oracle comparison is degenerate at the metric level; the gate
  validates causal wiring, provenance isolation, label-level propagation (the
  forced wrong-L1 pre-run check) and accounting, NOT a metric-level L1->L2
  dependency. Any future paired L1->L2 gate needs a model whose P2 genuinely
  depends on U1 (e.g. dependent-layer/joint-erasure construction), and the
  arms' discriminative dynamic range should be checked before freezing.
- Seed note [decision]: 2026091360/2026091361 equal P6-R1 test-local seeds;
  adjudicated acceptable (test-only, no consumed official stream, distinct
  Toeplitz namespace).
- Review state [repo-observed]: independent Pre-EXECUTE PASS (with the
  model-independence consequence recorded) and independent Pre-RESULT
  PASS_WITH_COMMENTS; both recomputed the frozen artifact numbers and neither
  reran the gate.
- Scope/status [decision]: synthetic two-layer interface gate only — no
  real-data FER, leakage efficiency, key rate, f<=1.3 claim, qualification or
  promotion; no Model-F artifact/parquet/TTBin/real data; no N>256/FWHT/SCL or
  Phase 7; old evidence roots untouched; no commit/push; CANDIDATE pending
  main-thread acceptance, not an acceptance. Environment unchanged (pinned
  interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`; pytest
  `-p no:cacheprovider --basetemp=<fresh /tmp path>`).

## 2026-09-13 P4 interface accepted; X01 workflow/probe successor

- P4 [decision]: `TWO_LAYER_OPERATIONAL_SC_INTERFACE_ACCEPTED`; causal wiring,
  provenance, isolation and accounting only. Attempt/seed remain consumed.
- Degeneracy [repo-observed]: independent-layer P2 changes across L1 by at most
  7.77e-16; 26/96, 44/96 and 34/96 are not performance evidence.
- Workflow [decision]: propose a non-claim Tier X plus retained Tier Y. X01 is
  frozen all-false with four five-seed families including dependent L2; Tier X
  cannot retroactively upgrade accepted evidence.

## 2026-09-13 Two-tier workflow active; X01 routes to X02

- Workflow [decision]: AGENTS.md §10.4 is active project-wide. X01 completed
  with focused review and remains non-claim design evidence.
- X01 [probe-observed]: P5/R1 exact dispersion is small; P4 dispersion is much
  larger; dependent P2 has cross-u1 max difference 0.2325. These observations
  do not alter accepted results.
- Route [decision]: skip redundant R1 Gate A and defer weak-oracle P4 Gate B.
  Run X02 Tier X over three dependence profiles and a frozen K1/K2 grid to find
  an informative operating point before defining any Tier-Y threshold.

## 2026-09-13 X02 routes to Phase 4-P5 penalty discriminator

- X02 [probe-observed]: strong/K1=45/K2=140 gave oracle 96/96 and operational
  47/96 across three probe streams; use as design evidence only.
- Statistics [decision]: the Tier-Y endpoint is a paired four-cell table.
  Clopper-Pearson applies only to the oracle-only event when operational-only
  is zero, never directly to the difference of marginal exact rates.
- Packet [decision]: P5 is frozen all-false for 384 new pairs; a confirmed
  penalty is a synthetic negative mechanism result, not algorithm success.

## 2026-09-13 NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY paired gate CANDIDATE (not acceptance)

- Implementation [repo-observed, candidate]: hard-L1 conditioning penalty gate
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/penalty_gate.py` wraps
  the accepted `two_layer.run_two_layer_block` and adds the dependent-L2
  table/sampler, the four-cell statistic, ten integrity gates and the
  exact-binomial discriminator; tests
  `comparison_bench/tests/test_nbpolar_penalty_gate.py` (9 new; full NB-Polar
  suite 201 across 14 `test_nbpolar_*.py` files). OpenSpec: the P5 spec/tasks
  delta lives under `formal-ir-nbpolar-phase4-p0`
  (`specs/nbpolar-phase4-p5/spec.md` + the P5 tasks section); no separate
  Phase-4-P5 change directory exists.
- Frozen point [decision, candidate]: GF32/poly37/alpha2 natural order, N=256,
  epsilon1=0.05, strong dependent-L2 `epsilon2(u1)=0.02+0.36*u1/31` (mean 0.20),
  K1=45/K2=140; streams 2026091470..1472 with 128 paired blocks each (384
  pairs), public Toeplitz masters 2026101470..72; derived P2 cross-u1 maxdiff
  0.34875000000000267 clears the >=0.30 gate.
- Sole gate execution [repo-observed, candidate]: attempt 1/1 consumed at the
  first gate L1 SC call (stream 0 block 0); no rerun/tuning. Cells both_exact
  233 / oracle_only 144 / operational_only 0 / neither 7; operational exact
  233/384 (0.606771, 151 verify_failed), oracle exact 377/384 (0.981771, 7
  verify_failed); undetected/nonfinite/decode_failed/resource_abort all 0;
  X=144 and the one-sided 95% exact lower bound on the oracle-only proportion
  is 0.3338842736427746 > 0.30. Ten integrity gates all true; accounting 989
  key-dependent bits per fully invoked arm (225+700+64), totals 759552 /
  2014464 (768 tags x 2623); recount mismatch 0; persisted label
  `HARD_L1_CONDITIONING_PENALTY_CANDIDATE`; evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
  holds exactly five scalar-only files.
- Finding [decision, candidate]: at the X02-recommended strong dependent-L2
  point the hard-L1 candidate conditioning shows a material penalty signal
  (oracle 0.982 vs operational 0.607 on the same blocks), the paired exact gap
  is one-sided, and operational_only is structurally zero; the frozen decision
  statistic is the exact binomial lower bound on the oracle-only proportion,
  not Clopper-Pearson on a marginal-rate difference.
- Review state [repo-observed]: independent Pre-EXECUTE R0 NEEDS_CHANGES
  (docs-only masters-enumeration defect B-1: `P5_FREEZE.md` listed
  2026092470..72 instead of 2026101470..72) -> repaired -> R1 PASS; independent
  Pre-RESULT PASS_WITH_COMMENTS.
- Carried notes [repo-observed]: per-block `oracle_candidate_divergence` is
  deliberately not persisted (structural argument via code + contingency +
  tiny-n test); integrity gate 10 is a frozen-record self-consistency check.
- Scope/status [decision]: synthetic single-point N=256 hard-conditioning
  interface signal only — no real-data FER, efficiency, key rate, qualification
  or promotion; no artifact/real data; no N>256/FWHT/SCL/APP-soft; old evidence
  roots untouched; no commit/push; CANDIDATE pending main-thread acceptance,
  not an acceptance.

## Standing reviewer-go trust rule

- User instruction [decision]: repository `reviewer-go` reports come from
  independent subagents. Their stated reruns, recomputations, tests and
  artifact checks may be trusted as independent evidence without routine
  main-thread duplication.
- Main-thread duty [decision]: still adjudicate scope and scientific meaning.
  Recheck only for internal contradiction, conflict with persisted artifacts,
  a missing frozen gate, or an out-of-scope conclusion.

## 2026-09-13 NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1 adaptive hard-L1 gate BLOCKED (gate-check defect, not acceptance)

- Implementation [repo-observed]: adaptive hard-L1 gate
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py` plus
  tests `comparison_bench/tests/test_nbpolar_adaptive_l1.py` (15 new; full
  NB-Polar suite 216 = 201 + 15); the P6 spec/tasks delta lives under
  `formal-ir-nbpolar-phase4-p0` (`specs/nbpolar-phase4-p6/spec.md` + the P6
  tasks section); no separate Phase-4-P6 change directory exists.
- Frozen point/schedule [decision]: GF32/N256, epsilon1=0.05, strong
  dependent-L2 `epsilon2(u1)=0.02+0.36*u1/31`, nested D1 [45,60,72,112],
  D2=140; streams 2026091550..1554 x 128 common blocks each (640 pairs);
  public Toeplitz masters 2026101550..54. Static arm: one L1 SC at D1=112,
  one candidate-conditioned L2 SC, one final tag. Adaptive arm: per-stage
  restart L1/L2 with one tag per stage; a tag match stops, a mismatch advances
  with one feedback bit, a nonterminal impossible-disclosure advances without
  a tag, and a terminal impossible is decode_failed.
- Sole gate execution [repo-observed]: attempt 1/1 consumed at the first
  scientific SC call (stream 2026091550 block 0 static L1); exit 0; no rerun
  or repair. Scientific gates all true: static exact 632/640, adaptive exact
  632; cells both 632 / adaptive_only 0 / static_only 0 / neither 8; leakage
  100x adaptive_total 67578300 <= 85x static_total 72025600 (20.2484%
  saving); per-arm outcomes exact 632 / verify_failed 8 / all other buckets
  0; termination histogram {45:403, 60:185, 72:39, 112:13}; tags
  640/942/1582, feedback 302, public control 4149888, union bound 8.576e-17,
  transcript recount mismatch 0; per-stream both/neither 127/1, 127/1, 124/4,
  127/1, 127/1; artifact wall 105.941485 s, RSS 394567680 B.
- Integrity [repo-observed, decision]: 11/12 gates true; the sole failing gate
  `d1_exactly_nested_and_d2_disclosed_once` is a gate-check implementation
  defect at `adaptive_l1.py:1342` — L2 events are counted by `(block_id, arm)`
  while `block_id` is per-stream, so the 1280 L2 events (640 static + 640
  adaptive) collapse onto 256 keys each counted 5, making `all(count == 1)`
  false. The contract-correct value is TRUE (per `(stream, block, arm)`
  identity the D2 disclosure count is exactly 1 for all 640x2); the reviewer
  reproduced the isolated false with a 2-stream probe.
- Lesson [decision]: a multi-stream identity/count gate must key on the full
  `(stream, block, arm)` identity and ship with a multi-stream test; counting
  on `(block_id, arm)` alone is silently wrong whenever block_id is
  stream-local.
- Disposition [decision]: no rerun/repair is permitted in this packet; the
  main thread owns disposition (a ruling on the corrected gate interpretation
  plus a successor fix keying the D2 check on full `(stream, block, arm)`
  identity and adding a multi-stream test). Persisted label is `BLOCKED`; this
  is not an acceptance.
- Review state [repo-observed]: two independent reviews verified the stage
  against the single executed run; the persisted `BLOCKED` label is caused by
  the gate-check defect above, not by a scientific or resource outcome
  failure.
- Scope/status [decision]: synthetic N=256 development evidence only — no
  real-data FER, efficiency, key rate, qualification or promotion; no
  artifact/real data; no N>256/FWHT/soft-APP/SCL; predecessor probes/roots
  untouched; no commit/push. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
  holds exactly five scalar-only files.

## 2026-09-14 NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX Δ-successor revalidation CANDIDATE (not acceptance)

- Fix [repo-observed, candidate]:
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1.py`
  repairs only the multi-stream event identity (13 hunks, +32/-6): every future
  transcript event carries the public scalar `stream_seed` and a
  stream-qualified `frame_key`, and the D2-once gate groups by
  `(stream_seed, block_id, arm)` with the matching `expected_l2`; no scientific
  constant, threshold, decoder path, outcome, disclosure formula or schema line
  changed. P6-R1 rev note in `formal-ir-nbpolar-phase4-p0/tasks.md`.
- Regression/tooling [repo-observed, candidate]: pure record/checker test
  `test_p6_r1_multistream_compound_d2_identity_gate` (two streams sharing block
  indices; fails under the old `(block_id, arm)` grouping; detects
  missing/duplicate disclosures) in
  `comparison_bench/tests/test_nbpolar_adaptive_l1.py`; new stdlib-only helper
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/adaptive_l1_revalidate.py`.
  Focused 16 passed; full NB-Polar suite 217 passed.
- Read-only revalidation [repo-observed, candidate]: original P6 root
  `.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
  (five files, sha256 f27fa45d… / 7b794ddd… / c3084898… / 2c2c09bf… /
  d595e95f… unchanged) recomputes 640 unique `(stream_seed, block_index)`
  identities, 1280 `(stream, block, arm)` D2 obligations each exactly one
  disclosure, L2 total 1280, all 12 integrity gates true and all 4 scientific
  gates true (static exact 632/640; adaptive exact 632 = static; cells both
  632 / adaptive_only 0 / static_only 0 / neither 8; leakage 67,578,300 <=
  72,025,600, 20.2484% saving). The only difference vs the persisted booleans
  is `d1_exactly_nested_and_d2_disclosed_once false→true`; the original
  aggregate summary/report and persisted `BLOCKED` label were never rewritten.
- Accounting/immutability [repo-observed, candidate]: zero decoder/RNG/tag
  calls, no new sample or seed, `attempts_consumed=0` (R1 STATUS 0/0); the P6
  attempt 1/1 and streams 2026091550..54 remain consumed; old root
  byte-for-byte unchanged; single machine result
  `.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/revalidation.json`;
  no commit/push.
- Review/status [repo-observed]: `INDEPENDENT_REVALIDATION_REVIEW.md` is
  PASS_WITH_COMMENTS (no blocking issue; operator narrative `+31/-6` is a docs
  off-by-one, reviewer counted +32/-6) and `OPERATOR_RETURN_R1.md` returns
  successor label `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE` as a candidate
  pending main-thread acceptance — not an acceptance.
- Reusable pattern [decision]: multi-stream gates must key per-block event
  counts on the full `(stream, block, arm)` identity and ship a multi-stream
  regression test; an event-identity checker fix can be validated without
  rerunning the experiment by read-only recomputation of frozen artifacts,
  preserving the old persisted label and replacing only the diagnosed gate
  value.

## 2026-09-14 Phase 4-P6R1 main-thread acceptance

- Acceptance [decision]: `ADAPTIVE_HARD_L1_DISCLOSURE_ACCEPTED` within the
  frozen synthetic N=256 dependent-L2 development scope. Corrected gates are
  12/12 integrity and 4/4 scientific; adaptive/static exact are both 632/640
  and adaptive key-dependent disclosure is lower by 20.2484%.
- Provenance [decision]: original P6 evidence and persisted `BLOCKED` label stay
  immutable; acceptance belongs to the P6-R1 successor revalidation, which
  consumed zero decoder/RNG/tag calls and zero new attempt/seed.
- Boundary/next [decision]: no real-channel FER, efficiency, key-rate,
  qualification, N-scaling, APP/SCL or FWHT claim. Next is X06, a one-artifact-
  read Tier-X empirical-genie versus BEC construction-order discriminator.

## 2026-09-14 X07 population/session divergence accepted; P7 frozen

- X07 [decision]: accepted only as descriptive provenance diagnosis
  `POPULATION_SESSION_IDENTITY_1M`. V49's `0.8010378248977232 bits/symbol` is
  the floor-only TRAIN entropy of V25 session `type2_1M_20260121_184040`; X06
  sampled distinct Model-F CAL session `20260123_1M_600k_0dB`, whose accepted-
  smoothed model entropy is `7.5094403148357545 bits/symbol`.
- Attribution [decision]: axis, packing, Bob weighting and normalization are
  excluded. X07 auxiliary MI fields are not accepted evidence; required
  entropy/CE/provenance quantities were independently reproduced.
- Construction route [decision]: use V25 1M TRAIN counts with columnwise MLE,
  fixed `1e-15` floor and renormalization. Do not tune lambda or use Model-F
  CAL as the target-channel construction law.
- P7 freeze [decision]: Tier-Y N=256 target-population construction gate;
  TRAIN 2026091650..52 (3x256), DEV 2026091660..64 (5x128), pooled empirical
  L1/L2 orders, paired BEC report-only control, K1=45/K2=140. Candidate gates
  include construction Spearman >=0.95, empirical exact >=620/640, one-sided
  Wilson lower bound >=0.95 and all integrity gates.
- Lifecycle/boundary [decision]: P7 is `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`,
  artifact read and attempt 0/1. Synthetic development only; no held-out/real
  FER, efficiency, key rate, scaling, qualification or promotion claim.

## 2026-09-14 NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION gate CANDIDATE (not acceptance)

- Implementation [repo-observed, candidate]: P7 target-population empirical
  construction gate
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_construction.py`
  plus `comparison_bench/tests/test_nbpolar_target_construction.py` (11 tests;
  full NB-Polar suite 228 = 217 predecessor + 11); the P7 spec/tasks delta lives
  under `formal-ir-nbpolar-phase4-p0` (`specs/nbpolar-phase4-p7/spec.md` + P7
  tasks section); no separate Phase-4-P7 change directory exists.
- Target input/consumption [repo-observed, candidate]: V25 1M TRAIN counts at
  `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`
  (25,166,822 B; [Alice,Bob] 1024x1024) via accepted `load_v25_channel_counts`;
  the single artifact content read and the single attempt are consumed at the
  first NPZ content open (open_count 1, no reopen/retry). TRAIN seeds
  2026091650..52 (x256), DEV seeds 2026091660..64 (x128) and Toeplitz masters
  2026101660..64 are spent; the X07 "attempt 0/1" freeze state is superseded.
- Support rule [decision, candidate]: column-normalize counts; floor every cell
  below `1e-15` to `1e-15` and renormalize columns; p_b from column totals;
  P1/P2 = accepted `derive_p1/derive_p2` under A=32*U1+U2; no lambda, backoff,
  tuning, floor scan or held-out fitting.
- Ratified entropy semantics [decision]: the frozen literals
  0.02428054681872374 / 0.7767572780789994 / 0.8010378248977232 (V49 1M TRAIN
  `nll_*` columns) are the raw-MLE in-sample conditional entropies under p_b
  (matched to <=4.5e-14); the floor-induced total-entropy change has the
  separate <=1e-9 guard (recorded 5.1600945738528026e-11). The strict
  floored-table reading at 1e-12 is unsatisfiable (V49's own floored `ent`
  exceeds its `nll` by ~1.5e-12); Pre-EXECUTE review item #1 ratified the
  raw-MLE reading, not the floored-table reading.
- Sole gate execution [repo-observed, candidate]: exit 0; module wall
  132.523651 s; peak RSS 383,832,064 B; no rerun. 11/11 integrity gates and
  3/3 scientific gates true -> label `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`.
  Construction stability: min pairwise TRAIN-order Spearman L1
  0.9973291943236439 / L2 0.9950453479056992; permutations valid; orders frozen
  before DEV (`orders_sha256`
  8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104).
- DEV result/accounting [repo-observed, candidate]: 640 paired blocks;
  empirical exact 640/640; BEC control exact 640/640 (report-only; both
  saturate so no empirical-vs-BEC discrimination); cells both 640 /
  empirical_only 0 / bec_only 0 / neither 0; one-sided 95% Wilson lower bound
  0.9957903841321254 > 0.95; truth-leak/undetected/nonfinite/resource_abort 0;
  recount mismatch 0; disclosure 989 key-dependent bits per fully invoked arm
  (L1 225 + L2 700 + tag 64), totals 1,265,920 key-dependent / 3,357,440 public
  / 1280 tags; planning-only f 4.8228 (no gate depends on f). Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/`
  holds exactly five scalar-only files.
- Review/status [repo-observed]: independent Pre-EXECUTE PASS with the ratified
  entropy semantics and independent Pre-RESULT PASS; CANDIDATE pending
  main-thread acceptance — not an acceptance.
- Scope/status [decision]: synthetic N=256 V25-1M-TRAIN model-sampled
  development signal only — no held-out/real-frame FER, efficiency, key rate,
  scaling, qualification or promotion; no Model-F/raw/held-out/EVAL artifact; no
  N>256/APP/SCL/FWHT; old evidence roots untouched; no commit/push.
- Context [decision]: this packet operationalized the accepted X07
  `POPULATION_SESSION_IDENTITY_1M` finding — V25 1M TRAIN is the 0.801-bit
  near-neighbor channel; the Model-F CAL artifact is a different, 7.5-bit
  population and is not the target-channel construction law.

## 2026-09-14 P7 target empirical construction accepted; P8 frozen

- [decision] Main thread accepted `TARGET_EMPIRICAL_CONSTRUCTION_ACCEPTED` for
  the V25 1M TRAIN model-sampled N=256 point with columnwise MLE, fixed
  `1e-15` floor and renormalization, pooled empirical orders, K1=45/K2=140,
  and the accepted two-layer hard-candidate SC/accounting semantics.
- [accepted evidence] The sole Tier-Y read/attempt was consumed without rerun
  or tuning; both independent reviews PASS. Minimum pairwise order Spearman was
  L1 0.9973291943 / L2 0.9950453479; empirical DEV exact was 640/640 with
  one-sided 95% Wilson LB 0.9957903841 and zero integrity failures. The BEC
  control also reached 640/640, so no empirical-over-BEC or order-discrimination
  claim is accepted.
- [accepted contract] V49 entropy literals are raw-MLE in-sample conditional
  entropies and the floor perturbation is governed separately. The accepted P7
  pooled order identity is
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`.
- [boundary] This is synthetic V25-1M-TRAIN model-sampled N=256 development
  evidence only, not held-out/real FER, efficiency, key rate, scaling,
  qualification, promotion, or APP/SCL/FWHT/adaptive evidence.
- [next gate] `NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM` is frozen at
  `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION` with reads/attempts 0/1. It screens
  the fixed 35-point static K1/K2 grid on 192 shared blocks, selects the
  eligible lexicographic minimum `(K1+K2,K1,K2)`, and confirms once on 640
  disjoint blocks with a report-only paired BEC control. No eligible point is a
  valid negative result; execution and both independent reviews remain pending.

## 2026-09-14 P8 target empirical rate point accepted; P9 lower boundary frozen

- [decision] Main thread accepted `TARGET_EMPIRICAL_RATE_POINT_ACCEPTED` in the
  frozen synthetic V25-1M-TRAIN model-sampled N=256 static scope. All 35 SCREEN
  points were eligible; deterministic `(K1+K2,K1,K2)` minimization selected
  K1=8/K2=80, or 504 key-dependent bits per fully invoked arm.
- [accepted evidence] Disjoint CONFIRM achieved 638/640 exact, 2
  verify_failed, one-sided 95% Wilson LB 0.9906013677, zero integrity failures,
  and exact transcript recount. All 11 integrity and 2 scientific gates were
  true; independent Pre-EXECUTE PASS and Pre-RESULT PASS_WITH_COMMENTS support
  acceptance. The sole read/attempt was consumed without rerun or tuning.
- [interpretation] This accepts feasibility, not a global minimum-rate claim:
  every SCREEN point passed and (8,80) was the lower grid corner, so P8 is
  left-boundary censored. Same-K BEC was 621/640 with 17 empirical-only paired
  cells, but is report-only and establishes no general superiority.
- [boundary] Planning-only f=2.4577491085 is not real efficiency. This is not
  held-out/real FER, efficiency, key rate, scaling, qualification, promotion,
  adaptive, APP, SCL, or FWHT evidence; no commit/push.
- [next gate] `NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION` is frozen
  awaiting explicit authorization with reads/attempts 0/1. It screens the 56
  points K1=[0,2,4,6,8,12,24,45] x K2=[0,20,40,50,60,70,80] on 192 new shared
  blocks, then confirms one deterministic eligible minimum on 640 disjoint
  blocks. Both zero axes remove grid-boundary ambiguity. This is the final
  N=256 static-rate localization gate before choosing adaptive target-rate work
  versus N-scaling/decoder acceleration.

## 2026-09-14 NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM gate CANDIDATE (not acceptance)

- Implementation [repo-observed, candidate]: P8 rate SCREEN→CONFIRM gate
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/target_rate.py`
  plus `comparison_bench/tests/test_nbpolar_target_rate.py` (12 tests;
  full suite 240 = 228 + 12); the P8 spec/tasks delta lives under
  `formal-ir-nbpolar-phase4-p0` (`specs/nbpolar-phase4-p8/spec.md` + P8
  tasks section); no separate Phase-4-P8 change directory exists.
- Target input/consumption [repo-observed, candidate]: accepted P7 pooled
  empirical L1/L2 orders (sha
  `8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104`) +
  V25 1M TRAIN NPZ (25166822 B) via accepted loader with floor-1e-15 rule;
  the single read and the single attempt are consumed at the first NPZ
  content open (open_count 1, no reopen/retry/rerun).
- SCREEN [repo-observed, candidate]: N=256; seeds 2026091680..1682 (x64 =
  192) with shared-block sampling; grid K1=[8,10,12,16,24,32,45] x
  K2=[80,94,110,125,140] = 35 points. ALL 35 eligible (Wilson LB>=0.95
  each; splits 1x189/4x190/6x191/24x192; undetected/decode/resource 0).
  Deterministic lexicographic-min (K1+K2,K1,K2) selected (k1=8,k2=80) —
  the lowest-disclosure eligible point.
- CONFIRM [repo-observed, candidate]: seeds 2026091690..1694 (x128 = 640),
  disjoint from SCREEN; selected point only plus same-K BEC control
  report-only. Empirical exact 638/640 (2 verify_failed); BEC 621/640;
  paired cells 621/17/0/2; one-sided 95% Wilson LB 0.9906013676984646;
  per-stream emp/bec 127/124, 128/122, 128/123, 128/127, 127/125.
- Accounting [repo-observed, candidate]: 5*(K1+K2)+64 key-dependent bits per
  fully invoked point (selected 504 bits); public 2623/tag; totals key
  5470080 / public 20984000 / tags 8000; independent recount mismatch 0;
  planning-only f 2.457749108478718 (not real efficiency). 11/11 integrity
  + 2/2 scientific gates true → `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE`.
  Wall 522.26697 s; RSS 274264064 B. Evidence root
  `.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm/`
  holds exactly five files.
- Review/status [repo-observed]: one executed run plus two independent
  reviews; CANDIDATE pending main-thread acceptance — not an acceptance.
- Scope/status [decision]: synthetic N=256 V25-1M-TRAIN model-sampled
  development signal only — not held-out/real FER, efficiency/key-rate,
  scaling, qualification/promotion; BEC gap report-only; no
  Model-F/raw/held-out/EVAL; no N>256/APP/SCL/FWHT/adaptive; old roots
  untouched; no commit/push.

## 2026-09-14 P9 lower-rate point accepted; FWHT scaling probe frozen

- [decision] Main thread accepted `TARGET_EMPIRICAL_LOWER_RATE_POINT_ACCEPTED`
  for the frozen V25-1M-TRAIN model-sampled N=256 grid. Among 56 registered
  points reaching both zero axes, deterministic selection chose K1=6/K2=70.
- [accepted evidence] Disjoint CONFIRM achieved 624/640 exact, Wilson one-sided
  95% LB 0.9626753340557015, 444 key-dependent bits per full arm, zero integrity
  failures, and exact recount. Both independent reviewer-go reviews PASS. The
  Wave-C certificate failure lost delivery only; read-only reconstruction
  established one genuine run and the retry correctly stopped, so read/attempt
  remain 1/1 with no rerun or tuning.
- [scope] This is the lowest eligible point of the frozen finite grid, not a
  continuous/global optimum. BEC 520/640 and 104 empirical-only cells are
  report-only. Planning-only f=2.1651599289 is not real efficiency and remains
  above the project target f<=1.3. No held-out/real FER, key rate, scaling,
  qualification, promotion, adaptive, APP/SCL/FWHT claim, commit, or push.
- [route] Stop further N=256 static/adaptive gating for now. The next gate is
  the non-claim Tier-X `NBPOLAR-PHASE4-P10-FWHT-KERNEL-SCALING-PROBE`, frozen
  awaiting authorization. It uses injected data only to compare the accepted
  direct GF(32) minus-node with an all-finite FWHT prototype, preserve direct
  fallback for nonfinite rows, and profile the unmodified reference SC through
  N=1024. No attempt or artifact access.

## 2026-09-14 X10-X12 scaling milestone; exact chunked Tier-Y gate frozen

- [probe evidence] X10 found useful bare-kernel FWHT scaling but wide/dominant
  inputs created 5371 exact-support mismatches. X11 then STOPPED correctly:
  ~1e-15 to 1e-14 finite numerical perturbations flipped near-tied early SC
  decisions, changed plus paths, and caused direct-success versus hybrid
  `ImpossibleDisclosedValueError`. Independent reviewer-go reproduced the
  mechanism. Do not advance this FWHT path to an exact-semantics Tier-Y gate;
  X11 timing transcript is not persisted performance evidence.
- [probe evidence] X12 retained the accepted q² `logaddexp.reduce` operation
  and reduction order, changing only row allocation. Chunk sizes
  32/128/512/2048 preserved exact arrays/support across 144 primitive cells,
  72 full-SC comparisons, 16 validation exceptions, impossible disclosure,
  X11-C3, known coordinates and tie controls; all 148 monkeypatches restored.
  Chunk512 completed N=262144 in 65.7253 s; process cumulative HWM was
  754,647,040 B and chunk temporary storage 4 MiB versus a 1 GiB direct-gather
  estimate. Independent focused review PASS.
- [boundary/next] These are Tier-X engineering observations, not FER,
  efficiency, qualification, promotion, or throughput claims. P11 is frozen as
  a Tier-Y allocation-only `sc.py` change with default 512, exact comparator
  semantics, injected one-shot N=65536 parity and N=262144 resource gates, no
  artifact access, and attempt 0/1 awaiting explicit authorization.

## 2026-09-14 P11 exact chunked SC accepted; P12 f=1.3 profile frozen

- [decision] Main thread accepted `EXACT_CHUNKED_SC_ACCEPTED`. Default
  `chunk_rows=512` changes allocation only and preserved bitwise results,
  support, exceptions and full-SC behavior in the frozen injected matrix.
  N=65536 paired exactly; N=262144 completed in 66.088 s at 710,504,448 B RSS.
  Both independent reviews support acceptance; attempt 1/1, artifact reads 0/0,
  no rerun. The 120-second/1-GiB values remain report-only.
- [boundary] Acceptance is engineering reachability, not FER, efficiency,
  key-rate, throughput superiority, qualification or promotion. X11's FWHT
  exception-parity blocker remains historical and is not repaired by chunking.
- [next] P12 is frozen to profile V25-1M-TRAIN model-sampled recovery at the
  actual f=1.3 budget over N=256..262144. Each N uses its own analytic BEC order
  and deterministic full-budget K split; no P7 empirical-order extrapolation.
  The 128-block uneven sample matrix has no recovery pass threshold and cannot
  qualify FER. Read/attempt 0/1 await explicit authorization.

## 2026-09-14 P12 terminal resource blocker; metric-lifetime probe frozen

- [decision] Accept terminal `BLOCKED(resource_limits_met_and_no_abort)`.
  P12 executed once and reached the N=262144 candidate-conditioned L2 metric,
  where an uncaught 64-MiB float64 allocation failed under 2 GiB. Read/attempt
  1/1 are spent; no output root exists and the roughly 124 in-memory earlier
  blocks are not evidence. Independent review confirmed one run and no rerun.
- [mechanism] P11 chunks only SC minus-node allocation. P12 retained L1/L2
  probability, SymbolMetric and SCResult planes, and long-lived result objects
  retained decoded arrays across blocks. The successor must preserve prior.py
  immutability/SC semantics, release temporaries at last use, retain scalar-only
  outcomes, catch resource errors outside decode taxonomy, and checkpoint every
  block without resume.
- [next] X13 is frozen as a two-file injected Tier-X comparison of lifetime-only
  versus owned-in-place-log metric construction, including sequential large-N
  blocks and live-array accounting. It does not rerun P12, access artifacts,
  modify production, consume an attempt, or create a scientific status.

## 2026-09-14 X13R1 metric-memory completion; P13 empirical-genie scaling frozen

- [decision] Record `X13R1_COMPLETE_DESCRIPTIVE_ONLY`. The four isolated
  injected cells completed 6/6 blocks for both `lifetime_only` and `owned_log`
  (N=65536 x4 and N=262144 x2) under the 2 GiB child limit, with no timeout or
  MemoryError. Parent replay of X13 N=64 controls passed 19 parity keys and
  X13 remained immutable. The independent reviewer-go focused review was
  supplied after execution and accepted as post-run evidence; that timing is
  retained in the probe record.
- [boundary] X13R1 shows that release-at-last-use removes the specific P12
  allocation blocker in the injected setting, but it does not select
  `lifetime_only` versus `owned_log`, establish target-channel recovery, or
  authorize a P12 rerun. Neither alternative is promoted yet; no attempt,
  artifact read, scientific status change, production edit, or commit/push.
- [next] Before any P12 retry, frozen Tier-Y packet
  `NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING` measures target V25 1M TRAIN
  empirical-genie residuals at N=4096, 8192 and 16384. It uses true-prefix
  genie risks, empirical worst-first orders, an exhaustive TRAIN-only integer
  split at `f=1.3`, and independent DEV residual/UCB reporting; DEV never tunes
  the frozen allocation. The smallest registered N with one-sided DEV residual
  UCB <= 0.01 is only a planning candidate, not FER or minimum-N evidence.
- [procedure] P13 is frozen awaiting explicit authorization: one V25 TRAIN NPZ
  content read and one scientific attempt, five-file per-block checkpointed
  root, scalar-only persistence, 2 GiB/1800 s limits, `OPENBLAS_NUM_THREADS=1`,
  `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `MALLOC_ARENA_MAX=2`, and VmPeak /
  VmSize recording. Any resource, semantic, integrity, or review failure stops
  without rerun; no Model-F/HOLD/raw/real/EVAL or old-root access.

## 2026-09-15 P14 empirical-genie learning curve accepted negative; P15 mid-N scaling frozen

- [decision] Main thread accepted
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED` as a valid
  negative within the V25-1M-TRAIN model-sampled genie-proxy scope. At
  N=16384 and fixed `f=1.3`, nested TRAIN prefixes B=8..128 did not yield a
  monotone or material DEV residual reduction: B=8 mean/UCB was 0.1176/0.1725,
  B=128 was 0.1420/0.2011, and paired B128-B8 mean was +0.0244. Orders were
  already highly stable, so eight-block construction size is not accepted as
  the material cause of P13's miss.
- [boundary] P14 is genie-construction proxy evidence only, not operational
  FER, a minimum-N result, qualification, or promotion. Its single read and
  attempt were consumed without rerun or tuning. The next route resumes the N
  axis; it does not retry P12 or use BEC orders.
- [next] Tier-Y packet
  `NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING` is frozen awaiting
  explicit authorization. It measures empirical true-prefix genie residuals
  at N=32768 and 65536 using 16 TRAIN plus 16 disjoint DEV blocks per N,
  empirical worst-first orders, an exhaustive `f=1.3` integer split frozen
  before DEV, and a one-sided df=15 t-UCB. It plans 128 genie calls, no BEC,
  tags, Toeplitz or operational decode, one V25 TRAIN NPZ content read and one
  scientific attempt, and an exactly five-file checkpointed evidence root.
  The frozen environment uses single-thread BLAS/OpenMP, `MALLOC_ARENA_MAX=2`,
  a 2-GiB virtual-memory limit and a 2100-second timeout; any resource,
  semantic, integrity or review failure stops without rerun or tuning.

## 2026-09-15 P15 empirical-genie mid-N negative accepted; P16 operational f=1.3 frozen

- [decision] Main thread accepted
  `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` as a valid negative
  within the V25-1M-TRAIN model-sampled genie-proxy scope. At fixed `f=1.3`,
  N=32768 had DEV mean/UCB 0.01915/0.03590 and N=65536 had 0.02877/0.07613;
  neither met the UCB <= 0.01 criterion. The larger-N mean was affected by a
  rare high-residual block, so no monotone cross-N improvement is accepted.
- [boundary] P15 is genie construction proxy evidence only, not operational
  FER, a minimum-N result, qualification or promotion. Its one NPZ read and
  one scientific attempt were consumed without rerun or tuning; P12-P15 roots
  remain immutable. The next route tests operational recovery at N=32768 and
  does not extend the genie curve or retry P12.
- [next] Tier-Y packet
  `NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13` is frozen awaiting explicit user
  authorization. It uses the accepted V25-1M-TRAIN empirical construction at
  N=32768, 16 disjoint TRAIN blocks and 64 disjoint DEV blocks, empirical
  worst-first orders and an exhaustive `f=1.3` integer split frozen before
  DEV. Each DEV block performs one hard-candidate L1 decode, candidate-
  conditioned L2 restart and one 64-bit Toeplitz verification; there is no
  BEC arm, adaptive retry or oracle arm. Gates are exact >=62/64 and one-sided
  95% Wilson LB >=0.90, with `undetected` isolated from success.
- [procedure] P16 plans one V25 TRAIN NPZ content read and one scientific
  attempt, five checkpointed files, scalar-only persistence, `chunk_rows=512`,
  `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
  `MALLOC_ARENA_MAX=2`, a 2-GiB virtual-memory limit and a 2100-second
  timeout. It records RSS HWM, VmPeak and VmSize; resource, semantic,
  integrity or review failure stops without rerun or tuning. No Model-F/HOLD,
  raw/real/EVAL, FWHT/APP/SCL, qualification/promotion, old-root modification,
  commit or push is authorized by the frozen packet.

## 2026-09-15 P16 operational N=32768 candidate accepted; P17 replication frozen

- [decision] Main thread accepted
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` as a model-sampled
  operational development signal. P16 completed with exact 62/64,
  undetected 0, and one-sided Wilson 95% LB 0.9098711859. The construction
  used N=32768, K1=319, K2=6492, total disclosure 34119 bits per block, and
  the accepted V25-1M-TRAIN empirical orders. Independent reviewer-go
  Pre-EXECUTE and Pre-RESULT evidence is trusted under the repository review
  rule; main-thread scope acceptance remains separate.
- [boundary] P16 has zero count margin: 62/64 is exactly the frozen count
  threshold and 61/64 would fail both recovery gates (Wilson LB 0.8884).
  Therefore it is not a stable rate point, finite-length FER claim,
  qualification, promotion, or real-data result. Its one artifact read and
  one scientific attempt are consumed; observations are not pooled into the
  next decision and the P16 evidence root remains immutable.
- [next] Tier-Y packet
  `NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION` is frozen awaiting
  explicit authorization. It reuses the accepted P16 construction identity,
  orders, N=32768, K1/K2, disclosure and operational protocol without TRAIN or
  genie work. It uses fresh DEV streams `2026092030..2026092037`, 16 blocks per
  stream (128 blocks total), with one L1 SC, candidate-conditioned L2 restart,
  and one 64-bit tag per block; P16 observations are report-only and contribute
  zero observations to P17 gates. The frozen gates are exact >=121/128 and
  one-sided Wilson 95% LB >=0.90 (the boundary LB is 0.9021084760).
- [procedure] P17 consumes one V25-1M-TRAIN NPZ content read and one new
  scientific attempt at the first content open, performs no adaptive retry,
  oracle/comparator arm, rescue, second tag, retuning, or rerun, and writes
  exactly five checkpointed scalar-only files. It requires predecessor
  construction identity, 128/128 coverage, 256 operational SC calls, 128 tags,
  exhaustive outcome buckets, truth isolation, exact accounting, one-open
  provenance and resource checks. Resource/semantic/integrity/review failure
  stops with evidence preserved; no commit/push or old-root modification.
- [route principle] The evidence route is
  empirical channel -> asymptotic DE/construction threshold -> finite-length
  backoff or scaling -> finite graph and decoder/target-FER verification.
  An asymptotic DE or construction result selects a candidate rate/order but
  never establishes finite-length decoder usability. Information-theoretic
  finite-length backoff (rate margin for a target error probability) is a
  separate correction from graph/decoder effects such as short cycles, rank
  deficiency, trapping/absorbing structures, layered error propagation and
  BP convergence; the latter require finite-graph and decoder evidence.
## 2026-09-17 — P19 acceptance and real-data feasibility route

- Main thread accepted
  `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE` descriptively from
  the finalized worktree root. The external `faac0411` commit captured only an
  11/15 `RUNNING` checkpoint; never restore or cite its blobs as the result.
- P19 passed 20/20 integrity gates and returned 15/15 `verify_failed` on the
  same three HOLD blocks. Base L1 correctness was true/false/false; +128 L1
  made it true/true/true. Nevertheless +128 L1, +512 L2, both, and the
  true-L1 control all recovered 0/3 complete blocks.
- Interpretation is bounded: hard-L1 propagation is not sufficient for these
  failures, and the registered backoffs did not recover them. This is not FER,
  qualification, a global backoff failure or an NB-Polar route rejection. The
  three blocks are closed diagnostic data and cannot tune K, floor, order or
  decoder.
- The project objective is now operational non-oracle real-data complete-block
  correction under a preregistered meaningful disclosure cap, then independent
  reproduction, then efficiency optimization. `f<=1.3` is not a Phase-1
  feasibility requirement and may not be manufactured by changing the
  denominator.
- Source audit confirmed broad SC `except Exception` paths can swallow an
  internal `MemoryError` as `decode_failed`; P20A freezes injected-only
  resource passthrough and endpoint instrumentation before any new real run.
- Endpoint semantics: operational 233/384 was complete-pair exact; oracle
  377/384 used true H in the final label. Their 144 difference is not the
  strict hard-L1-induced L2-error count. Future records separate L1,
  hard-L2, oracle-L2 and pair exact.
- The target model applies the fixed `1e-15` floor before SC. Diagnose raw
  zero-count hits, floor hits and log loss; never tune the floor on HOLD.
- HOLD L2 NLL is true-H-conditioned, not candidate-H-conditioned. Its increase
  cannot be attributed to hard-L1 propagation.
- L1 SCL starts only after true-L1 L2 recovery and list-coverage evidence;
  otherwise isolate L2 prior, construction, disclosure and search one factor
  at a time on independent development data.

## 2026-09-18 NB-Polar Phase 4 P20A accepted; P20B bounded-search diagnostic frozen (not authorized)

- P20A [repo-observed]: main thread accepted `IMPLEMENTATION_ACCEPTED`
  (independent review `ACCEPT_WITH_COMMENTS`, R1-R6 all accepted). STATUS is
  `IMPLEMENTATION_ACCEPTED` / `main_thread_acceptance`; next gate
  `P20B_PLANNING_AWAITING_PROPOSAL`.
- P20A delta [repo-observed]: `MemoryError` re-raise passthrough at 3 internal
  SC sites (`operational_f13.py` L1 + L2 in `run_operational_block`,
  `holdout_backoff_diagnostic.py` oracle-L2 in `run_oracle_control_block`);
  decode/nonfinite taxonomy unchanged. Endpoint fields `l1_exact`,
  `hard_l2_exact`, `oracle_l2_exact`, `pair_exact` (defaulted, scored
  pre-truth-sentinel, persisted in block/control/abort records); `pair_exact`
  is tag-independent label equality, `exact` remains tag-verified.
- P20A endpoints [repo-observed]: 233/384 operational-arm complete-pair exact;
  377/384 oracle-arm complete-label exact (oracle-conditioned, not a pure L2
  endpoint); denominator 384 paired N=256 synthetic blocks; 144 =
  `oracle_only` cell. Zero protected reads, zero attempts, zero output roots,
  zero result claims; no commit/push.
- P20A tests [repo-observed]: 5 new (9 total incl. 4 pre-existing) MemoryError
  escape + ordinary-failure pinning; suites green injected-only: opf 29 +
  replication 25 + microcheck 26 + backoff 33 = 113.
- P20A review notes [procedure]: "9 new" reads "5 new (9 total)";
  `PROJECT_BRIEF.md` item-11 hunk belongs to P19 lifecycle, not P20A;
  "frozen roots byte-identical" phrasing is stale.
- P20B [next/status]: Tier-Y packet
  `.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/`
  (4 files: `TASK_PACKET` / `PROMPT` / `AUTHORIZATION_PROMPT` / `STATUS`)
  frozen awaiting explicit user authorization (`execution_authorized`,
  stage-B authorization, and promotion all false); two stages — StageA
  implementation + injected tests → FREEZE → independent Pre-EXECUTE, then
  separately authorized StageB single execution → Pre-RESULT → acceptance.
  P20B has not run.
- P20B scope [decision]: strategy option 3 — bounded-search diagnostic with
  fixed prior/construction/disclosure (`S0_sc_base` / `S1_bounded_search` /
  `S2_true_l1_diagnostic`); options 1/2 recorded as P20C/P20D candidates only.
  OpenSpec delta follows the same umbrella path as P20A
  (`formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20b/`); no top-level
  `nbpolar-phase4-p20a` spec exists.
- P20B pending [pending]: independent development population undeclared;
  neighborhood definition binary choice deferred to StageA freeze;
  disclosure/budget quotas to be filled at freeze. Awaiting user decision on
  topic selection and the two-step gate.

## 2026-09-18 NB-Polar Phase 4 P20B bounded-search diagnostic Stage A complete + dual independent reviews (Stage B NOT authorized)

- P20B topic [decision]: strategy option 3 bounded-search diagnostic (user-approved); options 1/2 recorded as P20C/P20D candidates only.
- Stage A code delta [repo-observed]: new thin runner `comparison_bench/src/comparison_bench/formal_ir/nbpolar/bounded_search_diagnostic.py` — three arms `S0_sc_base` via `run_operational_block` / `S1` M=8 NBHD-1 `P20B-NBHD-1-hamming1-u-domain-margin-ranked` rescore-only + 1 final tag / `S2` via `run_oracle_control_block` + P20B domain tag closure; VAL DEV shaping; five files + per-(arm,block) checkpoint; P20A passthrough; 20 P19 mirror gates. Shared helpers zero logic change. +34 injected tests. Umbrella OpenSpec delta `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20b/spec.md` + `tasks.md` P20B-1..9 (all unchecked). Plus `P20B_FREEZE.md` + `P20B_IMPLEMENTATION_NOTES.md`.
- Frozen gate [repo-observed]: M=8 / single NLL / K1=319 / K2=6492 / floor 1e-15 / N=32768; population VAL frames 1200..1327 / 1328..1455 / 1456..1583 + remainder 1584..1599 (closed 1600..1983 non-overlapping, overlap pre-check, digest `055c9064…faea1b` match, manifest HOLD/VAL each 400/102400); cap 34119 op / 32524 control key bits/block + 327743 public/tag, ratio ~10.41%, recount-0 gate; Stage-B command FREEZE §10 verbatim 16 flags (`--dev-frames 1200 1599 --tag-master 2026092080`, block-major, 600s/2GiB/single-thread); S2 ORACLE `deployable=false` never operational; `undetected` isolated; SCL gate/stop rules unchanged.
- Stage A review [repo-observed]: independent R1-R8 all ACCEPT (34/34 new + 113/113 predecessor independent rerun green, injected-only, zero protected opens, frozen dirs clean). Notes: runner docstring-heavy logic thin; predecessor suite ~14min per §10.1 milestone batch; P20A Ms vs unrelated csv M isolation.
- Pre-EXECUTE [repo-observed]: independent 6/7 PASS, verdict `PRE_EXECUTE_FAIL`; sole blocker §4 authorization chain — `AUTHORIZATION_PROMPT.md` authorizes Stage A only, STATUS protected/decoder still false, user "P20B=option 3 + continue" names no 16-flag exact command so not Tier-Y execution authorization. Target output root stat-confirmed absent. VAL equivalence accepted as development population (same file fresh HOLD remainder 16 frames < N=32768 single-block 128-frame requirement; source/file/digest/geometry/cost class unchanged). Execution command verbatim-reviewed; executor must run verbatim.
- Scope [decision]: Stage A complete only — Stage B not run, not authorized, no result/acceptance/qualification/promotion claim; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P20B Stage B bounded-search diagnostic executed once (descriptive complete, accepted)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC` Stage B
  single execution success, exit 0, no rerun. User independently pasted the
  16-flag verbatim command as authorization; main thread recorded
  protected/decoder authorization true on disk. Pre-EXECUTE 6/7 PASS plus the
  pasted authorization补齐.
- Result [repo-observed]: descriptive label
  `TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE`; five-file evidence
  root `bounded_search_diagnostic/`; 20/20 gates all true. S0 0/3 exact
  (verify_failed x3, L1 F/T/T, first errors L1@15433 / L2@42 / L2@55); S1 0/3
  exact with all three blocks `selected_source=greedy#0`,
  `search_found_better=false`, dNLL 0.0, `rescores_used` 8 → bounded negative
  holds (descriptive, zero FER/promotion semantics); S2 0/3 oracle never
  operational.
- Accounting/resources [repo-observed]: per-block 34119 / 32524 / 327743
  identity; totals key 302286 / public 2949687; cap/raw ~10.41%; recount 0;
  wall 111.31 s; RSS ~541 MB; no resource stop. Consumption train 1/1 +
  hold/dev 1/1 + attempt 1/1.
- Reviews [repo-observed]: independent Pre-RESULT 8 items all PASS (threshold
  rule: found count unrelated to COMPLETE; leakage recount; undetected
  isolation; per-source attribution; single-factor semantics; artifact freeze
  consistency; first-error口径注记 non-blocking; language carries no promotion
  claim).
- Acceptance [decision]: main-thread state
  `TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE_ACCEPTED_DESCRIPTIVE`;
  next_gate P20C. Scientific reading is descriptive only: within M=8/NBHD-1 SC
  shows no missed candidate; information insufficiency remains the primary
  hypothesis; disclosure/construction work may proceed per packet §16; SCL
  remains unlocked (still not unlocked).
- Scope [decision]: VAL DEV diagnostic only — no FER/recovery/qualification/
  promotion claim; no rerun/tuning; P19 roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P20C Stage B L2-disclosure backoff executed once (descriptive complete, accepted)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF` Stage B
  single execution success — verbatim FREEZE §10 16-flag command, exit 0,
  wall 92.9 s, no repeat. Long-term authorization + independent Pre-EXECUTE
  `PRE_EXECUTE_PASS_CONDITIONAL`; `PRE_EXECUTE_REVIEW.md` on disk; STATUS
  authorization field true.
- Result [repo-observed]: descriptive label
  `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE`; evidence root
  `l2_disclosure_backoff/` (five files); 20/20 gates all true. B0 2/3 exact
  (blk1 verify_failed; L1 exact while hard-L2 stops at L2@723); B1 3/3 exact
  (ΔK2=+1024, K2 6492→7516 order-prefix, key Δ+5120); B2 oracle 2/3 exact
  (blk1 also fail; ORACLE/deployable=false excluded from aggregates).
  Operational exact 5/6, `b1_restored_count` 1 (block1 B0 fail→B1 exact);
  overall exact 7 / verify_failed 2 / undetected 0 / decode_failed 0 /
  nonfinite 0 / abort 0; 15 SC + 9 tag recalculations consistent.
- Accounting/resources [repo-observed]: key 102357 / 117717 / 97572, total
  317646 (operational 220074), public 2949687, recount 0; ratios
  10.41% / 11.97%; digest matches input, stat unchanged; RSS ~579 MB; no
  resource stop. Consumption attempt 1/1, NPZ 1/1 + DEV TRAIN pairs 1/1,
  HOLD 0/1 untouched.
- Reviews [repo-observed]: independent Pre-RESULT 8 items all PASS.
- Acceptance [decision]: main-thread state
  `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE_ACCEPTED_DESCRIPTIVE`;
  next_gate P20E confirmed. Scientific reading is descriptive only: +1024 L2
  disclosure under frozen order restored the base-failed block (B1 3/3 vs B0
  2/3), and that same block also failed under true-L1-oracle base disclosure
  — first positive DEV signal for the information-insufficiency (L2
  disclosure) hypothesis; SCL still unlocked; P20D alternative construction
  deferred pending confirmed results.
- Scope [decision]: VAL DEV diagnostic only — no FER/recovery/qualification/
  promotion claim; no rerun/tuning; P19 roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P20E Stage B plus1024 confirmation executed once (descriptive complete, accepted)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION` Stage B
  single execution success — verbatim FREEZE §10 command, exit 0,
  wall ~100 s, RSS ~554 MB, no repeat. Long-term authorization + independent
  merged review Stage A R1-R8 all PASS + Pre-EXECUTE
  `PRE_EXECUTE_PASS_CONDITIONAL`; `PRE_EXECUTE_REVIEW.md` on disk.
- Result [repo-observed]: descriptive label
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE`; evidence root
  `plus1024_confirmation/` (five files); 20/20 gates all true. B0 3/3 exact,
  B1 3/3 exact (ΔK2=+1024, K2 6492→7516 order-prefix, key Δ+5120), B2 oracle
  3/3 exact (ORACLE/deployable=false excluded from aggregates). Overall exact
  9 / verify_failed 0 / undetected 0 / decode_failed 0 / nonfinite 0 / abort 0;
  operational 6/6. Blocks 384..511 / 512..639 / 640..767, SER ~0.240 / 0.239 /
  0.237; b1_restored analogy 0/3 (B0 no failures, no restoration event,
  "maintain" mode). 15 SC + 9 tag recalculations consistent.
- Accounting/resources [repo-observed]: key 317646 (operational 220074),
  public 2949687, recount 0; ratios 10.41% / 11.97%; no resource stop.
  Consumption attempt 1/1, NPZ 1/1 + DEV TRAIN pairs 1/1, HOLD 0/1 untouched.
- Reviews [repo-observed]: independent Pre-RESULT PASS WITH COMMENTS, 8 items
  all PASS. Honesty assessment: maintain-exact holds; restoration-event
  denominator is 0 — neither replicated nor falsified, and the two must not
  substitute for each other. `OPERATOR_RETURN` "zero FER claim" already
  revised by main thread to "no FER/superiority claim".
- Acceptance [decision]: main-thread state
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE_ACCEPTED_DESCRIPTIVE`;
  next_gate P20F. Cumulative descriptive: B1 +1024 operational 6/6 exact
  (P20C 3/3 + P20E 3/3), B0 5/6; SCL still unlocked; P20D alternative
  construction continues deferred.
- Scope [decision]: VAL DEV diagnostic only — no FER/recovery/qualification/
  promotion claim; no rerun/tuning; P19 roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P20F Stage B plus1024 extension executed once (descriptive complete, accepted)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION` Stage B
  single execution success — verbatim FREEZE §10 command, exit 0,
  wall ~93 s, RSS ~580 MB, no repeat. Long-term authorization + independent
  merged review Stage A R1-R8 all PASS + Pre-EXECUTE
  `PRE_EXECUTE_PASS_CONDITIONAL`; `PRE_EXECUTE_REVIEW.md` on disk.
- Result [repo-observed]: descriptive label
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE`; evidence root
  `plus1024_extension/` (five files); 20/20 gates all true. B0/B1/B2 each 3/3
  exact; overall exact 9 / verify_failed 0 / undetected 0 / decode_failed 0 /
  nonfinite 0 / abort 0; operational 6/6. Blocks 768..895 / 896..1023 /
  1024..1151, SER ~0.2398 / 0.2362 / 0.2395; b1_restored 0/3 (maintain mode,
  denominator 0). 15 SC + 9 tag recalculations consistent.
- Accounting/resources [repo-observed]: key 317646, public 2949687, recount 0;
  ratios 10.41% / 11.97%; no resource stop. Remainder 48 frames / 12288 pairs
  (1152..1199) counted, never decoded. Consumption attempt 1/1, NPZ 1/1 + DEV
  TRAIN pairs 1/1, HOLD 0/1 untouched.
- Reviews [repo-observed]: independent Pre-RESULT pass with comments, 8 items
  all PASS; two provenance typos non-blocking: `predecessor_construction.protocol`
  suspected stale copy, `tag_seed_domain` missing counter segment — fix next round.
- Acceptance [decision]: main-thread state
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE_ACCEPTED_DESCRIPTIVE`;
  next_gate P20G. Cumulative descriptive: same-file TRAIN three-tranche B1 +1024
  operational 9/9 exact, B0 8/9; recovery event only P20C blk1 one case, never
  replicated; maintain-evidence thickening vs recovery-replication absence must be
  recorded distinctly, never generalized to overall reliability; SCL still
  unlocked; same-file TRAIN usable whole blocks exhausted (remainder 1152..1199
  insufficient for a whole block).
- Scope [decision]: VAL DEV diagnostic only — no FER/recovery/qualification/
  promotion claim; no rerun/tuning; P19 roots untouched; no commit/push.

## 2026-09-18 NB-Polar Phase 4 P20G Stage B 1.5M target-population-contract BLOCKED (terminal, descriptive, accepted)

- Packet [repo-observed]: `NBPOLAR-PHASE4-P20G-1P5M-TARGET-POPULATION-CONTRACT`
  Stage B single execution terminated `BLOCKED(target_population_contract)` —
  verbatim FREEZE §10 command, within-budget fast fail-closed refusal, not a
  resource abort. Long-term authorization + independent Pre-EXECUTE
  `PASS_CONDITIONAL` + §4 divergence resolved by main-thread written ruling
  adopting execution; divergence and reasons recorded in
  `PRE_EXECUTE_REVIEW.md`.
- Mechanism [repo-observed]: 1.5M counts array (1024x1024, floor 1e-15)
  channel statistics vs reused 1M literals H1 0.02428054681872374 / H2
  0.7767572780789994 / TOTAL 0.8010378248977232 — all three mismatched;
  digest/manifest/double-gate PASS then 4th gate FAIL, remaining 16 gates
  unevaluated, stopped before SC; 0 records, 0 SC / 0 tag. Planned key 317646 /
  public 2949687 vs actual 0/0, zero-event recount.
- Consumption [repo-observed]: attempt 1/1 + NPZ open 1 (train 1/1) consumed;
  1.5M DEV parquet content open 0 (stat-size precheck only); HOLD 0/1
  untouched; 2M pristine. Five-file root RUNNING stub retained;
  `OPERATOR_RETURN` §1–§8 complete.
- Reviews [repo-observed]: independent Pre-RESULT PASS, 7 items all PASS
  (fail-closed correct, BLOCKED sole legal outcome, no FER semantics, honest
  accounting, consumption isolation, artifact completeness, clean language;
  branch suggestion accepts BLOCKED terminal).
- Acceptance [decision]: main-thread state
  `BLOCKED_TARGET_POPULATION_CONTRACT_ACCEPTED_TERMINAL_DESCRIPTIVE`;
  next_gate P20H. Scientific reading is descriptive only: 1M frozen Model-F
  prior is not directly transferable to the 1.5M session (direct reuse
  rejected); per-session channel-statistics calibration is an open problem;
  1.5M DEV 0..383 remain unconsumed and available.
- Scope [decision]: VAL DEV diagnostic only — no FER/recovery/qualification/
  promotion claim; no retuning/rerun outside this packet; SCL still unlocked;
  P19 roots untouched; no commit/push.
