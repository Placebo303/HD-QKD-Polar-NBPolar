# Phase 4-P20G — Frozen +1024 independent-session confirmation on type2_1p5M_20260121_183806 (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: implementation Stage A + single authorized execution Stage B).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read,
  decoder execution, or commit/push is authorized by this file.
- Predecessor: `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (P20F) + P20A `IMPLEMENTATION_ACCEPTED` (resource passthrough + endpoint instrumentation).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` (three stages:
  feasibility → reproducible reliability → efficiency optimization; confirmation on new
  blocks/sessions; stop rules) and `docs/nbpolar/ROADMAP.md` current-priority section.
- Gate discipline: any standing long-horizon authorization ("proceed at least five rounds")
  does NOT collapse Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.
- Selected session: `type2_1p5M_20260121_183806` (1.5M). The 2M session
  (`type2_2M_20260121_183657`) is registered but RESERVED untouched for a possible later
  replication (see §2 decision record and §16).

## 1. Mission

Confirm the frozen +1024 candidate on an INDEPENDENT acquisition session, changing nothing:

> With construction / disclosure / order / prior / floor / kernel / representation / SC
> all carried over byte-identical from P20C/P20E/P20F (K1=319, K2 base 6492 / B1 7516 via frozen
> order-prefix extension, floor 1e-15, N=32768, new P20G tag domains only), zero tuning,
> does +1024 maintain exact on three new independent-session blocks — and does a P20C-style
> restoration event (B0 fail → B1 exact) replicate on genuinely new data, or not?

This is strategy stage 2 (reproducible reliability), second half: independent-session
confirmation. Same-file TRAIN confirmation is geometrically exhausted (P20C 0..383 +
P20E 384..767 + P20F 768..1151 = all 1152 usable TRAIN frames; remainder 1152..1199 is
48 frames < one 128-frame N=32768 block). All branches after this packet are deferred to
§16 and must not be prejudged here.

## 2. Background and first-principles decision record (frozen, not re-argued in Stage A/B)

- P20C (descriptive-accepted,
  `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE_ACCEPTED_DESCRIPTIVE`):
  B0 2/3 exact (blk1 `verify_failed` at L2@723 with L1 exact); B1 3/3 exact (ΔK2=+1024,
  K2 6492→7516 order-prefix, key Δ+5120); B2 oracle 2/3 exact (excluded from aggregates).
  Operational exact 5/6, `b1_restored_count` 1 (block1 B0 fail→B1 exact). First positive
  DEV signal for the information-insufficiency hypothesis; SCL still unlocked.
- P20E (descriptive-accepted,
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE_ACCEPTED_DESCRIPTIVE`):
  three NEW blocks 384..511 / 512..639 / 640..767, all arms 3/3 exact (overall 9/9;
  operational 6/6). `b1_restored_count` analogue 0/3: B0 never failed ("maintain" mode,
  descriptive only). Cumulative B1 +1024 operational 6/6, B0 5/6.
- P20F (descriptive-accepted,
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE_ACCEPTED_DESCRIPTIVE`):
  three NEW blocks 768..895 / 896..1023 / 1024..1151, all arms 3/3 exact (overall 9/9;
  operational 6/6). `b1_restored_count` analogue 0/3 ("maintain" mode, descriptive only).
  Cumulative descriptive: B1 +1024 operational 9/9 exact (P20C 3/3 + P20E 3/3 + P20F 3/3),
  B0 8/9. The single P20C restoration event (blk1) has had two replication opportunities
  (P20E, P20F) with denominator 0 both times — neither replicated nor falsified.
- Same-file exhaustion (arithmetic, frozen): 1M TRAIN = 1200 frames = 0..1199.
  Consumed: P20C 0..383 + P20E 384..767 + P20F 768..1151. Remainder 1152..1199 = 48
  frames / 12288 pairs < 128 frames needed for one N=32768 block. VAL pool 1200..1599
  consumed (P20B); HOLD 1600..1983 closed (P18/P19). THEREFORE no same-file whole-block
  continuation exists without violating consumed/closed rules. Recovery-replication
  inside 1M is geometrically impossible; this packet does not attempt it.
- Decision (planner, first principles): with same-file TRAIN exhausted and the
  restoration signal still at denominator 0 on two follow-ups, the ONLY scientifically
  reasonable Round 5 direction is strategy stage-2 second half — freeze the +1024 point
  and confirm it on an independent session. Alternatives rejected in writing:
  (a) same-file re-slicing/overlap/resampling — violates consumed-data and no-tuning
  rules, destroys attribution; (b) re-tuning K/order/floor/disclosure on 1M to force a
  failure — tuning on consumed data, forbidden; (c) P20D alternative construction now —
  premature: the trigger for P20D is a genuine negative (B0 fails unrestored by B1),
  which does not exist (P20E/P20F are maintain-mode, not negatives); (d) efficiency
  round now — premature: the trigger (replicated restoration AND maintain) is not met;
  (e) minimality probe (+512 vs +1024) now — cannot discriminate with restoration
  denominator at 0. All of (c)–(e) stay deferred per §16.
- Session inventory (provenance reads ONLY — directory listings + JSON manifests; zero
  NPZ/parquet content opens, zero stats on protected content by this planner):
  - `type2_1p5M_20260121_183806/`: `pairs.parquet` PRESENT (directory listing).
    Split manifest (`nbldpc_v25_split_manifest_v1`): TRAIN 1660 frames / 424960 pairs;
    VAL 553 / 141568; HOLD 554 / 141824 (256 rows/frame throughout: 1660×256=424960,
    553×256=141568, 554×256=141824 — exact). Build manifest: same v13r3fresh pipeline
    (point 1024,200; factor 1; nearest pairing; legacy_v1; occupancy 1) as 1M;
    distinct raw inputs (main ttbin sha `b3d308c3…`, chunk ttbin sha `d040a1a2…`,
    sizes 21264 / 31014064); pairs artifact size 1869178 B, sha `ca351e52…a06b`
    (provenance only).
  - `type2_2M_20260121_183657/`: `pairs.parquet` PRESENT (directory listing).
    Split manifest: TRAIN 2187 / 559872; VAL 729 / 186624; HOLD 729 / 186624
    (256 rows/frame exact). Build manifest: same pipeline; distinct raw inputs
    (sizes 21264 / 41768912); pairs size 2458335 B (provenance only).
  - Both candidates are therefore registered, present, and geometrically sufficient
    for the 3-block cost class (need: 384 TRAIN frames; 1.5M has 1660 = 4.3×; 2M has
    2187 = 5.7×).
- Binary choice (planner decision): SELECT 1.5M (`type2_1p5M_20260121_183806`); RESERVE 2M.
  Reasons, in order: (1) Sufficiency parity — both clear the 384-frame bar with large
  margin; 2M's extra headroom buys no additional scientific power for a 3-block gate.
  (2) Same-source independence — 1.5M is a distinct acquisition session (distinct raw
  ttbin shas/sizes, distinct pairs sha) under the identical apparatus family, date
  (2026-01-21), Type2 line and processing pipeline, temporally contiguous with 1M
  (183806 vs 184040) — a genuine independent-session test without a channel-regime
  change. (3) Parsimony and scale comparability — 1.5M TRAIN (1660 frames) is closer
  to the 1M development scale (1200) than 2M (2187), keeping the cost class and the
  statistical regime comparable. (4) Reservation value — consuming the largest pool
  first destroys the option of a second untouched independent replication; using 1.5M
  now keeps 2M pristine for a later round if P20G maintains or restores. 2M SHALL NOT
  be opened, statted, or read under this packet.

## 3. Freeze (normative — carried over, zero tuning)

FROZEN identical for every arm (any deviation is a packet violation, not a choice):

- Prior: frozen Model-F concentration prior path + fixed `1e-15` floor before SC.
  Diagnose only; never retune, never refit on the new session.
  Cross-session applicability is a STATED TO-BE-VERIFIED ASSUMPTION (see evidence-reuse
  isolation in §4), adjudicated at Pre-EXECUTE — never a finding of this packet.
- Construction order: accepted P16 order (digest pinned in the Stage-A freeze),
  K1=319 base L1 set unchanged on every arm. B1's +1024 set is the SAME first-7516
  prefix of the SAME frozen P16 L2 order — no reselection, no re-derivation, on ANY data.
- Disclosure: K2=6492 (B0, B2) / 7516 (B1); K_total 6811 / 7835. Caps per §5.
- Kernel / representation / transform / SC arithmetic: unchanged; greedy SC only;
  no SCL, no new kernel/model/schema.
- Verification: one final 64-bit Toeplitz tag per block/record under NEW P20G tag
  domains (§6, master 2026092210); verification never selects a candidate.

VARIED: NOTHING. This packet varies no factor. The only deliberate differences from
P20C/P20E/P20F are the new-session population (§4) and the new tag domain (§6) — both
provenance/identity changes, never algorithm changes.

## 4. Population and closed/consumed-data rule (normative)

- The three P18/P19 HOLD blocks (1M frames 1600..1983) SHALL NOT select K, floor,
  order, decoder, disclosure, or any successful point.
- The P20B VAL pool (1M frames 1200..1599, INCLUDING remainder 1584..1599) is
  CONSUMED and SHALL NOT supply P20G blocks.
- The P20C DEV blocks (1M frames 0..383), P20E DEV blocks (1M 384..767) and P20F DEV
  blocks (1M 768..1151, remainder 1152..1199 never used) are CONSUMED and SHALL NOT
  supply P20G blocks. The ENTIRE 1M pool (TRAIN 0..1199 / VAL 1200..1599 / HOLD
  1600..1999) is fail-closed against P20G DEV selection (see double gate below).
  Cross-packet same-block tuning is forbidden.
- The 2M session file (`type2_2M_20260121_183657/pairs.parquet`) SHALL NOT be opened,
  statted, or read under this packet. It is reserved, not consumed.
- Stage B runs on the DECLARED new-session population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin from build manifest; any mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| DEV frame rule | FIRST 384 TRAIN frames of the 1.5M file in (frame_id, pair_idx) order → 3 blocks × 128 frames at N=32768 (exact integers frozen at Stage A from JSON provenance, expected pattern `b..b+127 / b+128..b+255 / b+256..b+383` for the file's TRAIN base `b`; Stage A freezes a written equivalent with justification if the base differs — never assumed) |
| unused remainder | ALL remaining 1.5M TRAIN frames (expected 1276 frames) recorded never used — counted from the pool, never decoded |
| block count | 3 at N=32768 (mirrors P18/P19/P20B/P20C/P20E/P20F cost class) |
| tag domains | new P20G domain below |

- Stage A confirms (or replaces with a written equivalent + justification + re-review)
  the exact DEV integers via JSON-manifest provenance reads ONLY, never a content open:
  manifest 1.5M TRAIN/VAL/HOLD counts + build-manifest file pins; the runner additionally
  fail-closes (digest + counts + range gates below), so any layout drift blocks before
  any SC call.
- Evidence-reuse isolation (Pre-EXECUTE adjudicates): Model-F prior is a FROZEN
  aggregate concentration model, identical across arms, never refit or reselected on the
  new session; the comparison is an INTER-ARM differential (base vs +1024 vs oracle) on
  new-session frames, not a prior effect; no K/floor/order/step selection touches the new
  DEV, the 1M consumed/closed ranges, or the reserved 2M file. If Pre-EXECUTE rejects
  the cross-session isolation, Stage B is BLOCKED and the packet returns to the planner —
  per-session refit is NOT a fallback (it would be tuning).
- Fail-closed double gate (frozen in the runner, checked first, in this order):
  (a) CROSS-FILE gate — the DEV content open must match the 1.5M pairs path + size/sha
  pin; any 1M path (`type2_1M_20260121_184040`) or 2M path, or any digest mismatch,
  refuses before any SC call (bare frame integers collide across files, so source-tag +
  digest pin is the identity — never frame numbers alone); (b) INTRA-FILE gate — DEV
  ranges must overlap NONE of the 1.5M VAL/HOLD frame sets, else the run refuses before
  any protected content open. Gate order (a)→(b) is frozen.

## 5. Preregistered disclosure cap (normative, carried over)

- Cap rule: caps are CARRIED OVER unchanged from P20C/P20E/P20F (no growth, no tuning) —
  preregistered per arm, frozen before Pre-EXECUTE, each FAR below raw input bits
  with its ratio shown.

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| B0_sc_base (operational) | 319 | 6492 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| B1_L2plus (operational) | 319 | 7516 | 39239 = 5*7835+64 | 327743 |
| B2_true_l1_diagnostic (oracle) | 0 | 6492 | 32524 = 5*6492+64 | 327743 |

- Planned totals if all invoked: key 317646 = 3*34119 + 3*39239 + 3*32524
  (operational 220074 + oracle 97572); public 2949687 = 9*327743. B1 key-bit
  delta vs base exactly +5120 = 5*1024.
- Meaningfulness bar (unchanged): base 34119/327680 ≈ 10.41% and B1
  39239/327680 ≈ 11.97% of raw input bits (10*N per block at N=32768) — both far
  below raw. Sample-CE-normalized ratios are reported descriptively and are NOT
  qualification efficiency.
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate BLOCKS.

## 6. Arms (frozen; identical to P20C/P20E/P20F for comparability)

- `B0_sc_base`: frozen greedy SC at base disclosure/construction (operational; 2 SC +
  1 P20G-domain tag per block).
- `B1_L2plus`: frozen greedy SC with the SAME +1024 L2 order-prefix step as P20C/P20E/P20F,
  all else identical (operational; the confirmation candidate; 2 SC + 1 P20G-domain
  tag per block).
- `B2_true_l1_diagnostic`: true-L1-conditioned diagnostic at BASE disclosure
  (provenance ORACLE, deployable=false, excluded from every operational aggregate;
  never described as a correction result; 1 SC + 1 P20G-domain tag per block).
- No other arms. Run block-major (B0, B1, B2) per DEV block; checkpoint after every
  (arm, block) record; 9 records total. Five-file + per-arm checkpointing pattern
  reused from P18/P19/P20B/P20C/P20E/P20F.
- Tag domain: master 2026092210, prefix
  `nbpolar-p20g-independent-session-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix, master and arm tokens differ from
  the P16, P17, P18, P19, P20B, P20C, P20E and P20F domains; raw seed bits are never persisted.
  Stage A verifies by repo grep that master 2026092210 and focused-test seeds
  2026092211..2217 appear in no tracked file outside the P20G runner/tests/packet/
  spec/queue documents.

## 7. Thresholds and labels (descriptive only)

- Outcome label `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_INDEPENDENT_SESSION_COMPLETE` iff ALL
  integrity gates (§9) hold — regardless of exact-count. Any exact count (including
  0/9 and any partial outcome) is COMPLETE when integrity holds.
- This packet makes NO recovery / FER / Wilson / superiority / qualification /
  promotion claim. Confirmation reading is descriptive only:
  - "repeat recovery" = blocks where B0 fails and B1 is exact on the NEW-session blocks
    (P20C analogue `b1_restored_count`), reported as a count with per-block
    endpoint rows — a development signal, never a pass/fail verdict;
  - "maintain" = B1 exact where B0 exact, reported the same way.
  Either pattern (or its absence) counts as COMPLETE; the positive/negative branch
  decision belongs to main-thread planning AFTER acceptance (§16), never to this
  packet's label.
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`, with
  `undetected` isolated (never merged into success/FER), plus `decode_failed` /
  `nonfinite` / `resource_abort` via the P20A path. P20A four-endpoint separation
  (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` / `pair_exact`) recorded per record.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized execution;
  no rerun, no seed change, no disclosure/construction tuning after preregistration.
  An execution-error rerun is allowed only as a recorded repeat of the identical
  freeze, never as tuning.
- SC/tag budget: 15 SC calls (3 blocks x (2+2+1)) and 9 tags; derived per-record
  recomputation must equal the counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  call/disclosure accounting; abort is a BLOCKED result, never success.
- Wall/RSS ceilings frozen in Stage-A freeze (P20C class reference: ~92.9 s wall,
  ~579 MB RSS peak; P20E ~100.1 s / ~554 MB; P20F ~93.0 s / ~553 MB at the identical
  15 SC / 9-tag budget at N=32768; P20G plans the identical budget, strictly inside the
  same class; external timeout 600 s + virtual/RSS caps 2 GiB + single thread frozen
  as in P20E/P20F §8).
- Strategy stop rules restated as binding: no tuning on closed blocks; no reuse of
  the consumed 1M pool (any split) or the reserved 2M file; no third factor after an
  inconclusive single-factor result; no near-raw disclosure feasibility claim; no
  oracle-as-operational; no population-reliability inference from this single gate
  alone (one independent session is necessary but not sufficient for a reliability
  claim); no efficiency tuning inside this confirmation packet.
- SCL entry gate UNCHANGED (all five strategy conditions must still be shown; this
  confirmation unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage B, all frozen in Stage-A freeze)

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/independent_session/`
  (exactly five files, created pre-open; per-(arm, block) checkpointing; one content
  open per protected input; no reopen/rerun). Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9 records at completion), `aggregate_summary.json`,
  `report.md`. Scalar-only: never counts, sampled symbols, truth vectors, decoded
  labels/keys, metric planes, raw rows, per-arm orders, tag seeds or RNG state.
- Per-record separation (P20A endpoints): `l1_exact`, `hard_l2_exact`,
  `oracle_l2_exact`, `pair_exact`, `exact`, first error coordinate + layer, raw
  zero-count hits, `1e-15` floor hits + log loss, true-H-conditioned vs
  candidate-H-conditioned L2 NLL, outcome taxonomy, plus B1 disclosure fields
  (ΔK2=1024 applied, order-prefix positions fixed, key-bit delta +5120 vs base).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); SC-call
  counts (L1/L2 split) and tag-invocation counts exact; block SER/NLL; wall/RSS;
  `b1_restored_count` analogue recomputed descriptively (B0 fail→B1 exact on new blocks).
- Integrity gates (all true or BLOCKED; frozen order in the freeze): predecessor
  construction identity; split manifest identity (1.5M TRAIN 1660/424960 + VAL
  553/141568 + HOLD 554/141824); source-file identity (CROSS-FILE gate: 1.5M path +
  size/sha pin; 1M-full-pool and 2M exclusion); dev block range identity (INTRA-FILE
  gate: DEV disjoint from 1.5M VAL/HOLD); target population contract (7/7
  preconditions or frozen equivalent); dev population exact (384 frames / 98304 pairs /
  256 rows per frame / pair indices / symbol range); blocks exact with declared
  remainder (three exact DEV ranges per arm in block-major slot order + never-used
  remainder counted never decoded); nine records exact; SC calls exact (derived 15);
  tags exact (derived 9); order-prefix disclosure positions fixed within registered
  arms; oracle isolation; buckets disjoint exhaustive; undetected zero; nonfinite zero;
  truth isolation; disclosure recount exact; one open per protected input; input stat
  unchanged; no unregistered access; resource limits met and no abort.

## 10. Commands (exact argv frozen in Stage A / Stage-A freeze)

- Stage A (injected only, authorized separately): `.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_<independent_session files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20g/<uuid>/` temp root.
  Zero protected opens (audit required). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage B execution command (RECOMMENDED here, frozen verbatim in Stage-A freeze;
  NOT AUTHORIZED until independent Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_independent_session --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames <FROZEN_AT_STAGE_A> --block-frames 128 --remainder-frames <FROZEN_AT_STAGE_A> --tag-master 2026092210 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/independent_session
```
  Sixteen flags, all required, no production default; three hardcoded arms with the
  +1024 prefix-extension carried over pinned (never CLI-tunable). Stage A confirms the
  module path (`plus1024_independent_session` thin runner reusing P18 loading/block formation
  + P16 operational helpers read-only; new P20G tag domains; cross-file + intra-file
  fail-closed gates) or freezes a written equivalent with justification; Stage A also
  freezes the exact `--dev-frames` / `--remainder-frames` integers and the `--source`
  token vocabulary. Forbidden by default: `longrun_*`, `minrerun_*`,
  `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git show
  HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: thin runner + focused injected tests + Stage-A freeze +
  implementation notes (exact files, diffs, test commands/results, frozen
  population/cap/command/budget). No protected reads, no output root.
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md` (+ freeze,
  `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at their gates).
- OpenSpec P20G delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20g/spec.md`
  + `tasks.md` P20G section (same umbrella change as P18/P19/P20A/P20B/P20C/P20E/P20F; no new top-level change).

## 12. Allowed work

- New thin independent-session runner + focused injected tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py`, `l2_disclosure_backoff.py`,
  `plus1024_confirmation.py`, `plus1024_extension.py` (+ `construction.py`,
  `prior.py`, `sc.py` contracts as called).
- P20G OpenSpec delta + packet docs + freeze/return/review files + Stage-B evidence root
  (root only after Stage-B authorization).

## 13. Forbidden work

- Any protected TRAIN/HOLD/VAL/EVAL/raw read, stat, or open before Stage-B authorization
  (Stage A: JSON-manifest provenance reads ONLY — split manifest, build manifest, P16
  construction file; never a content open of any NPZ/parquet, including the 1.5M/2M
  pairs files); any decoder execution before Pre-EXECUTE PASS + pasted authorization.
- Any change to GF32/transform/SC arithmetic, prior/floor, construction order (including
  the carried-over prefix-extension rule itself), tag scheme semantics, outcome
  precedence, accepted evidence roots, or `src/` + `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on the closed three blocks, the
  consumed 1M pool (any split, any subrange), or the reserved 2M file; no second factor
  (alternative construction) inside this packet; no second disclosure step (`B1b`); no
  efficiency tuning; no new-block peeking before the authorized attempt; no per-session
  prior refit.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push;
  no self-acceptance; no P20D scope creep.

## 14. Acceptance IDs

- `P20G-R1`: prior/construction-order/floor/kernel/representation/SC carried over
  identical across arms; the +1024 prefix-extension step unchanged from P20C/P20E/P20F;
  Model-F cross-session use recorded as a to-be-verified assumption adjudicated at
  Pre-EXECUTE; only the new-session population and new tag domain differ.
- `P20G-R2`: closed three blocks select nothing; consumed 1M pool (TRAIN/VAL/HOLD, all
  subranges) excluded by the source-tagged cross-file gate; reserved 2M file untouched
  (never opened/statted); new 1.5M population (first 384 TRAIN frames → 3 blocks,
  remainder never used) independently declared, digest-pinned, double-gated,
  Pre-EXECUTE-approved.
- `P20G-R3`: disclosure caps carried over per arm (34119 / 39239 / 32524 + 327743
  public), ratios-vs-raw shown (~10.41% / ~11.97%), recount mismatch 0; CE ratios never
  called efficiency.
- `P20G-R4`: carried-over +1024 step + order-prefix rule frozen before execution,
  unchanged after; no tag-guided selection, no evidence reuse, no post-hoc re-picking.
- `P20G-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9; `undetected`
  isolated; oracle arm never operational.
- `P20G-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning; resource aborts
  via P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20G-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded; main-thread acceptance
  owns the label; descriptive-only, no FER/qualification/promotion language; branch
  reading (§16) stays planning input, never an in-packet verdict.
- `P20G-R8`: Stage-A suites green on injected data with zero protected opens; no
  commit/push; frozen dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs `P20G-R1..R8`
(stage-appropriately) complete with changed files + exact commands/results + artifact
inventory; or (b) a concrete blocker with failing command, exact error/traceback,
attempted remedies, and the ONE decision needed from the main thread. "Still incomplete"
is not a completion report. The operator never marks its own work accepted and never
authorizes Stage B.

## 16. Deferred options (not in this packet)

- Positive branch → efficiency round (deferred): trigger = restoration replicates on the
  new session (B0 fail → B1 exact at least once) or B1 maintains exact across new-session
  blocks where B0 shows failures elsewhere. Then a LATER packet may preregister reduced
  disclosure / wall / memory caps. This packet performs no efficiency tuning and licenses
  no efficiency claim.
- Negative branch → P20D (deferred): trigger = genuine negative — B0 failures occur on
  new-session blocks but B1 restores NONE of them. Then strategy option 2 (fixed
  disclosure + ONE preregistered alternative L2 construction on independent development
  data) becomes the next candidate. P20E/P20F maintain-mode (no B0 failures) is not a
  negative; P20D stays deferred until a negative exists.
- Maintain branch → re-discuss (deferred): if B0 is 3/3 exact again (restoration
  denominator 0 a third time), the planner re-discusses — candidates are a second
  independent session (reserved 2M) vs the disclosure-minimality probe, with no
  auto-advance. This packet renders no verdict.
- Disclosure-minimality probe (deferred): +512 vs +1024 at frozen order. Trigger: at
  least one restoration event replicated, so the smaller-step comparison discriminates.
  With the restoration denominator at 0 after P20E/P20F, the probe cannot yet
  discriminate; it stays deferred.
- P20D candidate (deferred): strategy option 2, fixed disclosure + ONE preregistered
  alternative L2 construction on independent development data. Stays deferred until a
  genuine negative exists (see above).
- Efficiency optimization (deferred): reduce disclosure / wall / memory under a new
  preregistered cap. Stays deferred until restoration replicates AND maintain holds.
- Second independent session on 2M (deferred): the reserved
  `type2_2M_20260121_183657` file (TRAIN 2187/559872, VAL/HOLD 729/186624 each) stays
  PRISTINE under this packet — never opened, never statted — as the follow-up
  replication population. Any 2M packet needs its own freeze, tag domain, and reviews.
