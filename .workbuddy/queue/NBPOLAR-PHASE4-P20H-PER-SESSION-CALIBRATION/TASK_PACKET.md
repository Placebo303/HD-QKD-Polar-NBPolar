# Phase 4-P20H — Frozen per-session-calibration +1024 confirmation on type2_1p5M_20260121_183806 (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: Stage A calibration-freeze + implementation, Stage B single authorized execution).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, calibration open,
  protected read, decoder execution, or commit/push is authorized by this file.
- Predecessor: `NBPOLAR-PHASE4-P20G-1P5M-183806` terminal
  `BLOCKED_TARGET_POPULATION_CONTRACT_ACCEPTED_TERMINAL_DESCRIPTIVE` (Stage-B single
  attempt SPENT 1/1; NPZ content open 1/1 consumed at `load_v25_channel_counts`;
  1.5M DEV parquet content NEVER opened, `dev_content_opens=0`; 0 SC / 0 tags / 0 records;
  failing `h1_matches_literal,h2_matches_literal,total_matches_literal` on the 1p5M counts
  array vs carried-over 1M literals H1 0.02428054681872374 / H2 0.7767572780789994 /
  TOTAL 0.8010378248977232; no rerun permitted under P20G).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
  reliability; confirmation on new blocks/sessions; stop rules) and `docs/nbpolar/ROADMAP.md`.
- Gate discipline: any standing long-horizon authorization does NOT collapse Tier-Y gates.
  Stage A and Stage B each need their own explicit pasted authorization text; this packet
  authorizes neither.
- Selected session: `type2_1p5M_20260121_183806` (1.5M). The 2M session
  (`type2_2M_20260121_183657`) is registered but RESERVED pristine (see §4, §16).

## 0. Planner header (OpenSpec workflow)

- **Goal**: Decide the single open question left by P20G — after per-session channel-statistics
  calibration, does the frozen +1024 point confirm on 1.5M TRAIN-first-384-frame DEV at
  N=32768 (three arms, carried-over construction/order/K/caps, new P20H tag domain)?
  P20G proved 1M priors do not transfer directly; the pending hypothesis becomes testable
  only with the session's own TRAIN-fitted prior under strict CAL→DEV separation.
- **Non-Goals**: No efficiency tuning, no P20D alternative construction, no minimality probe
  (+512 vs +1024), no second independent session on 2M, no SCL/new kernel/model/schema,
  no FER/qualification/promotion claim, no reuse of any consumed/closed 1M range.
- **Impact Scope**: New thin runner + focused injected tests + P20H OpenSpec delta
  (`specs/nbpolar-phase4-p20h/spec.md` + `tasks.md` P20H section, same umbrella change
  `formal-ir-nbpolar-phase4-p0`) + packet docs + Stage-A calibration product + Stage-B
  evidence root. No change to `src/`, `experiments/`, `tools/`, P16 construction file,
  P12–P20G accepted roots, or `results/` / `comparison_bench/outputs_comparison/`.
- **Acceptance Criteria**: P20H-R1..R8 (see §14), independent Pre-EXECUTE PASS +
  Pre-RESULT review on actual artifacts + main-thread acceptance. Descriptive-only label;
  `undetected` isolated; oracle never operational.
- **Tasks**: (planner task list for coder agents) H1 freeze the calibration program
  (§3, R1); H2 freeze population/double-gate (§4, R2); H3 freeze caps (§5, R3);
  H4 freeze +1024 step (§6/R4); H5 wire endpoints/taxonomy (§7/R5); H6 enforce one-shot
  budget/stop (§8/R6); H7 Stage-A suites green with declared calibration-open audit (R8);
  H8 independent Pre-EXECUTE adjudication of the §3 calibration-vs-tuning gate (R7);
  H9 single authorized Stage-B attempt (R6/R7); H10 independent Pre-RESULT + acceptance.

## 1. Mission

With ONE preregistered change against P20G — the prior is per-session calibrated on
1.5M TRAIN counts by the frozen §3 program (Stage A, DEV-zero-contact, read-only in
Stage B) — and everything else carried over byte-identical from P20C/P20E/P20F/P20G
(K1=319, K2 base 6492 / B1 7516 via frozen order-prefix extension, floor 1e-15,
N=32768, new P20H tag domains only), zero further tuning:

> Does +1024 maintain exact on three 1.5M TRAIN-first-384-frame blocks — and does a
> P20C-style restoration event (B0 fail → B1 exact) appear on per-session-calibrated
> data, or not?

Same-file 1M TRAIN remains geometrically exhausted (P20C 0..383 + P20E 384..767 +
P20F 768..1151; remainder 1152..1199 < one block). P20G DEV 0..383 is UNCONSUMED
(0 records, DEV never content-opened) and is therefore the legitimate P20H DEV range.
All branches after this packet are deferred to §16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- P20C/P20E/P20F (all descriptive-accepted): B1 +1024 operational 9/9 exact cumulative
  (P20C 3/3 with one restoration blk1; P20E 3/3 maintain; P20F 3/3 maintain); B0 8/9.
  Restoration denominator 0 on both follow-ups — neither replicated nor falsified.
- P20G (terminal BLOCKED, accepted as terminal-descriptive): verbatim FREEZE §10 command
  executed once 2026-09-18 22:22:32 +0800; fail-closed
  `BLOCKED(target_population_contract)` BEFORE any DEV open: loaded `--source 1p5M`
  counts array (shape (1024,1024), floor 1e-15) mismatches ALL THREE carried-over 1M
  literals (H1/H2/TOTAL above); gates 1–3 PASS (construction digest, split manifest,
  double-gate pins), gate 4 FAIL, remaining 16 gates not evaluated; 0 SC/0 tags/0 records;
  NPZ open 1/1 + attempt 1/1 SPENT; DEV 0 opens; 2M pristine by non-access.
  Scientific meaning: **1M priors are not directly portable to 1.5M** — the pending
  hypothesis converts to an open question: per-session channel-statistics calibration
  followed by the same +1024 test, or not.
- Decision (planner, first principles): the ONLY scientifically reasonable Round 6 is a
  per-session-calibration confirmation packet (P20H) restoring the Phase-4-established
  CAL→DEV adapter pattern (§3). Alternatives rejected in writing: (a) rerun P20G as-is —
  forbidden (attempt 1/1 exhausted; identical rerun cannot discriminate); (b) patch the
  1M literals post-hoc inside P20G — tuning on failure, forbidden; (c) fit on DEV/HOLD
  or on 1M DEV — DEV-tuning, forbidden; (d) jump to P20D now — premature (no genuine
  negative exists; P20G is BLOCKED-on-prior, not B0-fails-unrestored); (e) efficiency
  round now — premature (no replicated restoration + maintain under calibrated prior);
  (f) minimality probe now — cannot discriminate (restoration denominator still 0);
  (g) consume 2M now — destroys the second-replication option; 2M stays pristine.
  All of (d)–(g) stay deferred per §16.
- Session inventory (unchanged from P20G §2 provenance; no new protected access by this
  planner): 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 (256 rows/frame
  exact); pairs size 1869178 B / sha `ca351e52…a06b`; 2M TRAIN 2187/559872 reserved.
  Both clear the 384-frame cost class; 1.5M selected for scale comparability, 2M reserved.

## 3. Calibration-program freeze (normative — the single deliberate delta vs P20G)

FROZEN program = the accepted P0/P2 Model-F concentration fitting program, isomorphic
(same formula / smoothing / flow), new-session input only:

- Formula (P0 `design.md` §1, verbatim): `p_global[a] = sum_b counts[a,b]/sum counts`;
  `n_b[b] = sum_a counts[a,b]`; `f[a,b] = (counts[a,b] + lambda*p_global[a])/(n_b[b]+lambda)`.
  Column meaning `P(A|B)` shape (1024,1024) `[Alice,Bob]`, columns sum to 1 within 1e-12;
  unseen-Bob column falls back to `p_global` exactly. Banned twin
  (`build_f_model` per-cell `counts+lam`) SHALL NOT be called.
- Adapter chain (P0/P2 accepted): chain-split to `P_U1_given_B` / `P_U2_given_U1_B`,
  `marginalize_f_to_p1` / `conditionalize_f_to_p2`, accepted `derive_p1`/`derive_p2`
  tables under packing `A = 32*U1 + U2` (`low = s&31 = U2`, `high = (s>>5)&31 = U1`),
  joint-Bob conditioning `FULL_BOB_ONLY`, fixed `1e-15` floor before SC (diagnosed,
  never retuned in Stage B), `SymbolMetric` log-domain contract (exact zero → `-inf`,
  row `logsumexp 0`). Lambda = the accepted fitting-program constant procedure output
  (Stage A freezes the literal value + its provenance; no hand-fill; no DEV influence).
- Input (sole allowed): 1.5M TRAIN counts ONLY — the `--source 1p5M` counts array
  (TRAIN-derived; Stage A freezes array identity + byte/sha digest + shape). FORBIDDEN
  inputs: 1.5M DEV (0..383 and remainder), 1.5M VAL/HOLD, ANY 1M split (TRAIN/VAL/HOLD,
  consumed or closed), reserved 2M in any form, Model-F CAL artifact rejected for this
  purpose by P7/P12–P17 precedent. DEV-zero-contact during calibration (no parquet open,
  no frame/row/symbol read) is a freeze condition, verified by the one-open guards.
- Output (Stage-A frozen, Stage-B read-only): per-session prior tables (`P1`/`P2_hat`
  derivation of the calibrated joint) + recalibrated literal triple
  (H1/H2/TOTAL recomputed from the calibrated array, replacing the 1M literals for
  the `target_population_contract` gate) + input digest + lambda + floor pin.
  Threshold/formula/input-digest/output-literals are ALL frozen in Stage A; Stage B
  verifies digest match read-only before any SC call and refuses on mismatch.
  No refit/resmoothing/relambda after any DEV contact — that would be tuning.
- Calibration-vs-tuning adjudication (written into this packet; Pre-EXECUTE adjudicates):
  per-session TRAIN calibration is the P-phase-4-established **adapter pattern**
  (P0 lifecycle: CAL fits counts/lambda → DEV selects at most one preregistered bounded
  floor / diagnoses candidate-L2 → EVAL tunes nothing; P7/P12–P17 precedent: V25 1M TRAIN
  count matrix → `derive_p1`/`derive_p2`, never the Model-F CAL artifact), NOT DEV tuning,
  IFF ALL of: (i) calibration input = 1.5M TRAIN only (§3 input rule); (ii) DEV zero
  contact before freeze (guards false at freeze time; DEV open count 0 at Stage-A close);
  (iii) program isomorphic with the 1M-accepted formula/smoothing/flow (no new smoother,
  no per-DEV lambda search, no floor search on DEV); (iv) frozen before execution and
  read-only in Stage B (digest-gated). Pre-EXECUTE owns this gate: PASS-to-execute iff
  (i)–(iv) evidenced in the calibration product; else BLOCKED-to-planner. No
  calibration fallback inside Stage B. This does NOT contradict P20G §4 ("refit is not a
  fallback"): P20G forbade post-hoc refit *after* its zero-tuning freeze/execution;
  P20H is a NEW packet whose preregistered lifecycle puts TRAIN fitting BEFORE any DEV
  contact — different stage, not post-hoc.

## 4. Population and closed/consumed-data rule (normative)

- The three P18/P19 HOLD blocks (1M 1600..1983), P20B VAL pool (1M 1200..1599 incl.
  remainder 1584..1599), P20C/P20E/P20F DEV blocks (1M 0..383 / 384..767 / 768..1151,
  remainder 1152..1199 never used) are CONSUMED/CLOSED and SHALL NOT supply P20H blocks.
  The ENTIRE 1M pool is fail-closed against P20H DEV selection (cross-file gate).
- The 2M session file SHALL NOT be opened, statted, listed, or read under this packet
  (reserved, not consumed; pristine by non-access; stat itself violates the packet).
- Stage B runs on the DECLARED population (P20G-UNCONSUMED, reused legitimately):

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin; mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| DEV frame rule | FIRST 384 TRAIN frames of the 1.5M file in (frame_id, pair_idx) order → frozen TRAIN base 0: `0..383` (Stage A confirms or replaces with written equivalent + justification + re-review; never assumed) |
| DEV blocks (N=32768) | `0..127`, `128..255`, `256..383` (3 × 128 frames) |
| unused remainder | frames `384..1659` (1276 frames / 326656 pairs) recorded never used — counted, never decoded |
| intra-file VAL / HOLD | 1660..2212 / 2213..2766 — disjoint by fail-closed gate (VAL first) |
| 1M full pool + reserved 2M | excluded by the cross-file gate (checked FIRST); never touched |
| block count | 3 at N=32768 (same cost class as P18/P19/P20B/P20C/P20E/P20F/P20G) |
| tag domains | new P20H domain (§6) |

- Fail-closed double gate (frozen in the runner, order (a)→(b), VAL before HOLD):
  (a) CROSS-FILE — DEV content-open path + stat-size/sha pin must equal the 1.5M identity;
  any 1M or 2M path or digest mismatch refuses before any SC call (frame integers alone
  are never identity); (b) INTRA-FILE — DEV ranges must overlap NONE of 1.5M VAL/HOLD,
  else refuse before any protected content open. Plus (c) CALIBRATION-IDENTITY gate —
  Stage-B prior/table/literal digest must equal the Stage-A frozen calibration digest
  before any SC call, else refuse (this replaces P20G's failed 1M-literal gate).

## 5. Preregistered disclosure cap (normative, carried over from P20C/P20E/P20F/P20G)

- Caps CARRIED OVER unchanged (no growth, no tuning) — per arm, frozen before Pre-EXECUTE,
  each FAR below raw input bits with ratio shown.

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| B0_sc_base (operational) | 319 | 6492 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| B1_L2plus (operational) | 319 | 7516 | 39239 = 5*7835+64 | 327743 |
| B2_true_l1_diagnostic (oracle) | 0 | 6492 | 32524 = 5*6492+64 | 327743 |

- Planned totals if all invoked: key 317646 = 3*34119 + 3*39239 + 3*32524
  (operational 220074 + oracle 97572); public 2949687 = 9*327743. B1 key-bit
  delta vs base exactly +5120 = 5*1024.
- Meaningfulness bar (unchanged): base 34119/327680 ≈ 10.41%, B1 39239/327680 ≈ 11.97%
  of raw input bits (10*N per block) — far below raw. Sample-CE-normalized ratios are
  descriptive, NOT qualification efficiency.
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate BLOCKS.

## 6. Arms (frozen; identical to P20C/P20E/P20F/P20G for comparability, prior swapped per §3)

- `B0_sc_base`: frozen greedy SC at base disclosure/construction (operational; 2 SC +
  1 P20H-domain tag per block; k1=319/k2=6492 on the frozen P16 order).
- `B1_L2plus`: frozen greedy SC with the SAME +1024 L2 order-prefix step (operational;
  the confirmation candidate; 2 SC + 1 P20H-domain tag per block; k1=319/k2=7516 as the
  first-7516 prefix of the SAME frozen P16 L2 order — no reselection, on ANY data).
- `B2_true_l1_diagnostic`: true-L1-conditioned diagnostic at BASE disclosure
  (provenance ORACLE, deployable=false, excluded from every operational aggregate;
  never a correction result; 1 SC + 1 P20H-domain tag per block).
- No other arms. Block-major (B0, B1, B2) per DEV block; checkpoint after every
  (arm, block) record; 9 records total. P16 construction/order/K migration unchanged
  (digest pinned in Stage-A freeze); kernel/representation/transform/SC arithmetic
  unchanged; greedy SC only; no SCL/new kernel/model/schema.
- Tag domain (new P20H): master 2026092220, prefix
  `nbpolar-p20h-per-session-calibration-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix/master/arm tokens differ from ALL of
  P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G. Stage A verifies by repo grep that master
  2026092220 and focused-test seeds 2026092221..2227 appear in no tracked file outside
  the P20H runner/tests/packet/spec documents.

## 7. Thresholds and labels (descriptive only)

- Outcome label `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_PER_SESSION_CALIBRATION_COMPLETE`
  iff ALL integrity gates (§9) hold — regardless of exact-count. Any exact count
  (including 0/9 and partials) is COMPLETE when integrity holds.
- NO recovery / FER / Wilson / superiority / qualification / promotion claim.
  Descriptive reading only: "repeat recovery" = blocks where B0 fails and B1 is exact
  on the calibrated new-session blocks (`b1_restored_count` analogue, count + per-block
  endpoint rows); "maintain" = B1 exact where B0 exact. Either (or neither) counts as
  COMPLETE; branch decisions belong to main-thread planning AFTER acceptance (§16).
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`, `undetected`
  isolated (never success/FER), plus `decode_failed` / `nonfinite` / `resource_abort`
  via the P20A path. P20A four-endpoint separation (`l1_exact` / `hard_l2_exact` /
  `oracle_l2_exact` / `pair_exact`) per record.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized execution;
  no rerun, no seed change, no disclosure/construction/calibration tuning after
  preregistration. Execution-error rerun only as a recorded repeat of the identical
  freeze, never as tuning. P20G's spent attempt does NOT transfer (independent packet).
- Reads (independent, separately counted): counts-calibration open 1/1 (Stage A, NPZ
  1p5M array, consumed at first calibration content open) + DEV open 1/1 (Stage B,
  parquet, consumed at first DEV content open). HOLD reads 0/1 untouched. Any reopen,
  second calibration, or DEV refit is forbidden.
- SC/tag budget: 15 SC (3 blocks × (2+2+1)), 9 tags, 9 records; derived per-record
  recomputation must equal counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence + accounting;
  abort is BLOCKED, never success. Wall/RSS ceilings frozen in Stage-A freeze (P20C-class
  reference ~92.9 s / ~579 MB; P20E ~100.1 s / ~554 MB; P20F ~93.0 s / ~553 MB at the
  identical 15 SC / 9-tag budget; P20H plans the identical decoder budget PLUS a
  separately-recorded calibration cost; external timeout 600 s + virtual/RSS caps
  2 GiB + single thread frozen).
- Strategy stop rules binding: no tuning on closed blocks; no reuse of consumed 1M pool
  (any split/subrange) or reserved 2M; no third factor after inconclusive single-factor;
  no near-raw disclosure claim; no oracle-as-operational; no population-reliability
  inference from this single gate alone; no efficiency tuning inside this packet.
- SCL entry gate UNCHANGED (unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage A calibration product + Stage-B five files)

- Calibration product (Stage A, frozen): `per_session_calibration/` (exact filenames
  frozen in Stage A; recommended): `calibration_plan.json` (formula/lambda-procedure/
  floor/input-identity pins, pre-open), `calibration_input_identity.json` (NPZ path +
  source tag + digest + shape + split-manifest cross-check, post-open),
  `calibrated_prior.npz` (per-session P-joint / P1 / P2 tables — the ONLY prior Stage B
  may load, digest-pinned), `recalibrated_literals.json` (H1/H2/TOTAL + derivation,
  replacing 1M literals for the gate), `calibration_report.md`.
  Scalar-only elsewhere: never sampled symbols, truth vectors, decoded labels/keys,
  metric planes, raw rows, per-arm orders, tag seeds or RNG state beyond the pinned
  tables/digests.
- Stage-B root: `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation/`
  (exactly five files, created pre-open; per-(arm, block) checkpointing; one DEV content
  open; no reopen/rerun). Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9 records at completion), `aggregate_summary.json`,
  `report.md`. Per-record §7 endpoints + first error coordinate/layer, zero-count hits,
  floor hits + log loss, true-H vs candidate-H L2 NLL, taxonomy, B1 disclosure triple
  (ΔK2=1024, order-prefix, +5120 vs base).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); SC counts
  (L1/L2 split) + tag counts exact; block SER/NLL; wall/RSS (decoder + calibration
  reported separately); `b1_restored_count` analogue descriptive.
- Integrity gates (all true or BLOCKED; frozen order in the freeze): predecessor
  construction identity; split manifest identity (1.5M TRAIN 1660/424960 + VAL
  553/141568 + HOLD 554/141824); source-file identity (CROSS-FILE gate); dev block
  range identity (INTRA-FILE gate, VAL first); calibration identity (input digest +
  formula/lambda/floor pins + output-literal match + Stage-B digest equality);
  target population contract (recalibrated literals, 7/7 preconditions or frozen
  equivalent); dev population exact (384 frames / 98304 pairs / 256 rows/frame /
  pair indices / symbol range); blocks exact with declared remainder; nine records
  exact; SC calls exact (15); tags exact (9); order-prefix positions fixed; oracle
  isolation; buckets disjoint exhaustive; undetected zero; nonfinite zero; truth
  isolation; disclosure recount exact; one calibration open + one DEV open (no more);
  input stat unchanged; no unregistered access; resource limits met and no abort.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (injected tests + calibration-freeze; authorized separately):
  `.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_<per_session_calibration files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20h/<uuid>/` temp root;
  calibration open audit declared separately (see §8). Safe smoke per
  `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage-A calibration command (RECOMMENDED, frozen verbatim in Stage-A freeze; counts
  open 0→1 consumed here): thin calibration entrypoint applying the §3
  formula/adapter to `--source 1p5M` TRAIN counts only, writing `per_session_calibration/`
  and refusing on any DEV/VAL/HOLD/1M/2M contact. Exact module path + flags frozen
  in Stage A (written equivalent + justification if the path differs).
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A freeze;
  NOT AUTHORIZED until independent Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_per_session_confirmation --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1p5M --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames <FROZEN_AT_STAGE_A> --block-frames 128 --remainder-frames <FROZEN_AT_STAGE_A> --tag-master 2026092220 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation
```
  All flags required, no production default; three hardcoded arms with the +1024
  prefix-extension pinned (never CLI-tunable); Stage-B prior path MUST equal the
  Stage-A frozen digest. Stage A confirms the module path (thin runner reusing P18
  loading/block formation + P16 operational helpers read-only; new P20H tag domains;
  triple gate) or freezes a written equivalent with justification; Stage A also freezes
  the exact `--dev-frames` / `--remainder-frames` integers (expected `0 383` /
  `384 1659`) and the `--source` vocabulary (only `1p5M`). Forbidden by default:
  `longrun_*`, `minrerun_*`, `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data,
  full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git show
  HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: calibration program freeze + calibration product (§9) + thin runner + focused
  injected tests + Stage-A freeze + implementation notes (exact files, diffs, test
  commands/results, frozen calibration/population/cap/command/budget). DEV content
  opens 0 at Stage-A close except the single declared counts-calibration open.
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md` (+ freeze,
  `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at gates).
- OpenSpec P20H delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20h/spec.md`
  + `tasks.md` P20H section (same umbrella change as P18/P19/P20A/P20B/P20C/P20E/P20F/P20G;
  no new top-level change).

## 12. Allowed work

- New thin calibration entrypoint + per-session confirmation runner + focused injected
  tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py`, `l2_disclosure_backoff.py`,
  `plus1024_confirmation.py`, `plus1024_extension.py`, `plus1024_independent_session.py`
  (+ `construction.py`, `prior.py`, `sc.py` contracts as called).
- P20H OpenSpec delta + packet docs + calibration product + freeze/return/review files +
  Stage-B evidence root (root only after Stage-B authorization).

## 13. Forbidden work

- Any DEV/VAL/HOLD/EVAL/raw content open or stat before Stage-A calibration freeze
  (calibration input is TRAIN counts only); any DEV calibration/refit/resmoothing after
  freeze; any decoder execution before Pre-EXECUTE PASS + pasted Stage-B authorization.
- Any change to GF32/transform/SC arithmetic, floor value, construction order (including
  the carried-over prefix-extension rule itself), tag scheme semantics, outcome
  precedence, accepted evidence roots, or `src/` + `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on closed blocks, the consumed
  1M pool (any split/subrange), or the reserved 2M file; no second factor (alternative
  construction) inside this packet; no second disclosure step (`B1b`); no efficiency
  tuning; no new-block peeking before the authorized attempt; no calibration on DEV.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push;
  no self-acceptance; no P20D scope creep; no P20G rerun under this packet.

## 14. Acceptance IDs

- `P20H-R1`: calibration program frozen isomorphic to P0/P2 (§3 formula/smoothing/flow,
  banned twin excluded, lambda-procedure + floor + packing pinned); input = 1.5M TRAIN
  counts only with digest frozen; output prior + recalibrated literals frozen in Stage A
  and read-only in Stage B; DEV-zero-contact evidenced; §3 (i)–(iv) adjudicated at
  Pre-EXECUTE. Calibration-program BLOCKED → rework P20H-R1 path (see §16), never a
  Stage-B fallback.
- `P20H-R2`: closed blocks select nothing; consumed 1M pool excluded by source-tagged
  cross-file gate; reserved 2M untouched (never opened/statted/listed); P20G-unconsumed
  1.5M DEV (first 384 TRAIN frames → 3 blocks, remainder never used) digest-pinned,
  double-gated + calibration-identity-gated, Pre-EXECUTE-approved.
- `P20H-R3`: disclosure caps carried over per arm (34119 / 39239 / 32524 + 327743
  public), ratios-vs-raw shown (~10.41% / ~11.97%), recount mismatch 0; CE ratios never
  called efficiency.
- `P20H-R4`: carried-over +1024 step + order-prefix rule frozen before execution,
  unchanged after; P16 construction/order/K migration pinned; no tag-guided selection,
  no evidence reuse, no post-hoc re-picking.
- `P20H-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9; `undetected`
  isolated; oracle arm never operational.
- `P20H-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning; separate
  counts-calibration (1/1) + DEV (1/1) read accounting; resource aborts via P20A path
  with accounting preserved; stop rules + SCL gate intact.
- `P20H-R7`: independent Pre-EXECUTE (§3 gate included) + Pre-RESULT reviews recorded;
  main-thread acceptance owns the label; descriptive-only, no FER/qualification/promotion
  language; branch reading (§16) stays planning input, never an in-packet verdict.
- `P20H-R8`: Stage-A suites green on injected data with the declared single
  counts-calibration open audit (DEV opens 0 at Stage-A close); no commit/push; frozen
  dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs `P20H-R1..R8`
(stage-appropriately) complete with changed files + exact commands/results + artifact
inventory + separate calibration/DEV open audit; or (b) a concrete blocker with failing
command, exact error/traceback, attempted remedies, and the ONE decision needed from the
main thread. "Still incomplete" is not a completion report. The operator never marks its
own work accepted and never authorizes Stage B.

## 16. Deferred options (not in this packet)

- Calibration-positive → efficiency round (deferred): trigger = calibrated B1 maintains
  exact across new-session blocks AND at least one restoration replicates. Then a LATER
  packet may preregister reduced disclosure / wall / memory caps. This packet performs no
  efficiency tuning and licenses no efficiency claim.
- Confirmation-negative → P20D (deferred): trigger = genuine negative under the calibrated
  prior — B0 failures occur on new-session blocks but B1 restores NONE. Then strategy
  option 2 (fixed disclosure + ONE preregistered alternative L2 construction on
  independent development data) becomes the next candidate. P20G BLOCKED is not a
  negative; maintain-without-failure is not a negative.
- Calibration-program BLOCKED → rework P20H-R1 (deferred path, not Stage-B fallback):
  if the §3 gate fails (wrong input, DEV contact, non-isomorphic program, digest mismatch),
  Stage B is BLOCKED and the planner owns a P20H-R1 rework packet — never a silent
  in-packet refit.
- P20D candidate / disclosure-minimality probe (+512 vs +1024) / efficiency optimization /
  second independent session on reserved 2M: ALL continue deferred with P20G triggers
  unchanged, re-evaluated against calibrated-prior evidence after acceptance.
- 2M stays PRISTINE under this packet — never opened, never statted, never listed — as the
  follow-up replication population. Any 2M packet needs its own freeze, tag domain, and
  reviews.
