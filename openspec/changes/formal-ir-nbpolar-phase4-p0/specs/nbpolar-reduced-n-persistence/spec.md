# Delta spec — N=8192 persistence probe on the 2M HOLD tail (SCOPING ONLY)

- Status: `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`. This delta spec is a
  proposal + freeze-design input under the umbrella change
  `formal-ir-nbpolar-phase4-p0`. It authorizes NO implementation, NO
  derivation, NO execution, NO protected opens, NO tail/DEV data contact,
  NO commit/push.
- Authority: planner subagent scoping, 2026-09-20, branch
  `codex/nbpolar-phase0`. Parent analysis:
  `.workbuddy/queue/NBPOLAR-REDUCED-N-FEASIBILITY.md` (population
  arithmetic, C1–C10 cost inventory, comparability verdict, gate class).
- Predecessor root (read-only reference, never modified, never re-derived):
  `NBPOLAR-PHASE4-P20S-R1-GATE-FIX/l2_mechanism_probe_2m/` (accepted
  descriptive, 15/15 files, N=32768).

## ADDED-1. Probe questions and honest-scope bounds (normative)

The probe SHALL answer at most the following two descriptive questions,
both scored WITHIN N=8192 only:

- Q-G1: does the spike-local fail-site pattern (first-error at a
  local-hazard spike; fail site vs disclosed prefix under both domain
  flags) recur at N=8192 on the 2M HOLD tail under within-N paired
  comparison (arm A vs arm B on the same block)?
- Q-G2: does the spike-local order disclose more tail mass than the
  frozen-order equivalent at the same N (IR-1 prefix/outside tail-mass
  contrast A vs B; full-scope top-128/top-1024 concentration per record's
  own order)?

Honest scope (binding on every downstream packet/freeze/return): a
descriptive persistence probe; n=1; NO FER, reliability, efficiency,
leakage, key-rate, recovery-rate, scaling-superiority, or promotion claim;
NO cross-N inference; NO H2 (re-)adjudication input; NO extension of any
N=32768 chain. Any exact count is COMPLETE when integrity holds and is
explicitly NOT read as a recovery rate.

## ADDED-2. Population (normative — exact frames)

- Source file identity (to be pinned at freeze by manifest cross-check):
  the 2M session `type2_2M_20260121_183657` pairs parquet, HOLD split
  only. Frame convention: 256 rows/frame; N=8192 block = 32 frames.
- DEV block R1: frames **3595..3626** (3626−3595+1 = 32; 32×256 = 8192
  pairs). Single contiguous segment, single split (HOLD), single session;
  first-contiguous-block rule (same convention as all P20 DEV selections).
- Declared remainder (counted, never decoded): frames **3627..3644**
  (3644−3627+1 = 18; 18×256 = 4608 pairs).
- The 1.5M stubs SHALL NOT be used: VAL stub 2172..2212 (41 frames /
  10,496 pairs) and HOLD 2725..2766 (42 frames / 10,752 pairs) stay
  counted never-decoded (low-information controls only, never pooled,
  never primary evidence; 1.5M↔2M mixing forever forbidden).
- No cross-split combining is needed (the 50-frame tail 3595..3644 is one
  contiguous segment inside HOLD intra-file range 2916..3644); the D1-A
  merge precedent is NOT invoked. The 2M HOLD tail 3595..3644 stays
  never-decoded until the separately authorized Stage-B execution.

## ADDED-3. Arm structure (normative)

Exactly three arms on the single N=8192 DEV block (block-major; checkpoint
per (arm, block) record; 3 records total):

- `A_anchor_frozen_order_equivalent`: operational anchor at the frozen α1
  construction with the NEWLY DERIVED N=8192 worst-first empirical order
  (ADDED-4). "Frozen-order equivalent" means the same derivation RULE as
  the P20O 2M orders applied fresh at N=8192 — it SHALL NOT reuse the
  N=32768 order files (`raw_prior_orders_2m.json`, digest
  `b2255449…0906`) in any form (length mismatch + per-N geometry).
- `B_spike_local_order`: probe candidate with byte-identical α1 tables to
  A at identical (K1,K2); disclosed-L2 SET = first-K2 of the NEWLY
  DERIVED N=8192 spike-local order under the carried F-median8
  formula-id (score[i] = h[i] − median over the R=8 clipped natural
  neighborhood; descending rank; ascending tie-break; deterministic).
  The R=8 window convention vs 8192-geometry SHALL be re-frozen as a new
  freeze decision (not an automatic carry). The SET-delta between the A
  and B L2 lists IS the probed factor (size-delta exactly 0 by design).
- `O_true_l1_oracle`: true-L1-conditioned diagnostic at carried K2
  (provenance ORACLE, deployable=false, excluded from every operational
  aggregate; the P20O/P20Q-D continuity).

## ADDED-4. N=8192 derivation contract (normative — new derivation)

- Construction/allocation SHALL be fully re-derived at N=8192 per the P16
  pattern: model-sampled TRAIN blocks at N=8192 → pooled per-layer risks
  → worst-first `(e,h,index)` orders → K_total via the frozen budget
  formula with the 2M session H recomputed within 1e-12 → exhaustive
  `(K1,K2)` selection by TRAIN residual, frozen before DEV. (K1,K2) SHALL
  NOT be carried from (334,6746).
- K rule: `K_total = floor((1.3·N·H−64)/5)` with N=8192 and 2M
  H=0.8325627219737477 recomputed (never hand-filled per AGENTS.md
  §5.5). The arithmetic estimate ≈1760 (1.3·8192=10649.6; ×H≈8866.5;
  −64≈8802.5; /5≈1760.5) is an ESTIMATE ONLY, never a committable
  literal; the −64 tag term breaks exact quartering (7080/4=1770).
- Fresh L1/L2 worst-first empirical orders at N=8192 (length-8192
  permutations); fresh spike order at N=8192; new tag domain (ADDED-6).
- New runner (or thin-importer + new frozen constants) with
  `FROZEN_N = 8192`; the `target_construction.py:1559` hard gate
  (`n == FROZEN_N`) forbids passing `--n 8192` to any frozen-point
  runner. SC stage count = log2(8192) = **13**; `chunk_rows` geometry
  re-sized (P11 precedent); all frozen sizing constants new.
- N-dependent values (shapes frozen here, literals frozen in-packet):
  tag length `10·N+63` = **81983** bits/tag; key `5·(K1+K2)+64` per
  operational block (≈8864 at the ≈1760 estimate); oracle `5·K2+64`;
  IR-5 series 8192 f32-LE (32 KiB) + 8192 u8 (8 KiB) + 8192 u8 (8 KiB)
  = 48 KiB/record, 3 records ≈ 144 KiB, same `ir5full-v1` manifest
  linkage; IR-1 (64-bin), IR-2, IR-3 (1.0×/2.0×), IR-4 (top-16) formulas
  and caps carried P20Q-identical.

## ADDED-5. Reuse pins (normative — read-only)

The following SHALL be reused read-only (digest-pinned, never re-derived,
never carried as N-literals): the 2M session-H inputs (H literals
`0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477`
recomputed within 1e-12; worktree `raw_prior_2m.npz` arrays as the
off-protected-data derivation input — never the V25 counts NPZ); formula
shapes (budget, tag-length, K-split selection, F-median8 ranking,
IR-1..IR-4, nine-scalar semantics); code paths (`sc.py`,
`sc_chunked_gate.py`, `transform.py`, causal two-layer wiring, Toeplitz
accounting, P20A resource/endpoint machinery, recount/gate machinery);
gate patterns (single-segment containment, TRAIN-exclusion,
consumed-range exclusions, S2-ii disjointness declaration, truth
isolation, `undetected` isolation, oracle isolation).

## ADDED-6. One-shot semantics and tag domain (normative)

Single attempt, no rerun, no reuse/parameter change after
preregistration; resource aborts preserve evidence and BLOCK, never
succeed. DEV open 1/1 reserved for the separately authorized Stage-B
execution (consumed at the first DEV content open); counts-calibration
opens 0/0 at every stage; 1M/1.5M/2M-non-DEV 0 in every form. Tag domain
SHALL be new (fresh master + prefix, pinned at Stage-A freeze with repo
grep disjointness proof against all frozen masters incl. 2026092360);
focused test seeds fresh and disjoint. SC/tag budget shape follows P20S
(5 SC: A 2 / B 2 / O 1; 3 tags; 3 records; zero sampling at scoring).

## ADDED-7. Comparability boundary (normative — non-transfer list)

Per-N results (K, disclosure, hazard geometry, FER-like behavior) are NOT
comparable across N. The following SHALL NOT transfer to N=8192: the
1/4→2/5→4/5 restoration chain (scored at K2=6746 under 32768-length
orders); the H2 verdicts (H2a REFUTED / H2b SUPPORTED / H2c SUPPORTED /
H2d flat / H2e truncated-scope verdict — adjudications over the 63-row
N=32768 join; an N=8192 block contributes zero rows; cross-N pooling
forbidden); the IR-5 32768 geometry (rank structure, prefix fractions,
top-k baselines — no curve overlays, no shared thresholds); any leakage
literal (key 35464/35464/33794, public 327743/tag, totals 104722/983229,
budget literal `1.3·32768·H`).

## ADDED-8. Scope (normative)

This probe SHALL use zero protected opens + injected data + temporary
roots in Stage A with DEV 0/1 at close, zero sampling/genie calls at
scoring, and the single N=8192 DEV block in Stage B. It SHALL NOT carry
any 1.5M/2M K/order/prior absolute across N or recompute K from alt-H;
use lambda anywhere; change the field, transform, SC arithmetic, floor
value (1e-15), verification tag semantics, outcome precedence, or
scientific status; add SCL, a new kernel/model/schema, a fourth arm, a
second construction, a construction sweep, or a disclosure change; reuse
any consumed range; derive on or tune with DEV; decide H2 in-packet;
pool across N; overwrite `results/` or
`comparison_bench/outputs_comparison/`; or commit/push.

(End of file)
