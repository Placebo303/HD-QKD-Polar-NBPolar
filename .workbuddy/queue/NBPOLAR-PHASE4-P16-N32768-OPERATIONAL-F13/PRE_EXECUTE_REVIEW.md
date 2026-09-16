# Pre-EXECUTE review — NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13 (Tier-Y)

Reviewer: independent reviewer-go (did not write the code). Read-only review;
no production code, test, spec, freeze, or STATUS file was modified by this
review. The single NPZ artifact was **never content-opened**: metadata `stat`
only (25166822 bytes). The frozen gate command was **never run**. No
Model-F/HOLD/raw/real/EVAL/FWHT/APP/SCL access; no P12–P15/old-root writes;
no commit/push.

## Verdict: PASS

The Wave-A implementation matches the frozen packet and the P16 OpenSpec
delta; refusals, consumption, construction, DEV causality, accounting, gates,
labels, budgets, and scope all check out against the actual code. The five
flagged items are adjudicated below (all ratified). Two non-blocking notes
and three observations are recorded; none can alter a scientific conclusion.
Execution of the single frozen attempt is cleared **subject only to the
frozen command, root absence, and STOP rules restated in the Wave-C rule**.

---

## 1. STATUS exactness — PASS

`STATUS.yaml` (re-read at review close, unchanged):
`task_id` correct; `state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`;
`tier: Y`; three predecessors as declared; `execution_authorized: true`;
`artifact_reads_allowed: 1 / used: 0`; `attempts_allowed: 1 / used: 0`;
`result: null`; `pre_execute_review: pending`; `pre_result_review: pending`;
`next_gate: INDEPENDENT_PRE_EXECUTE`.
`execution_authorized: true` alongside pending reviews is conforming: it is
the user's packet-level authorization (see `AUTHORIZATION_PROMPT.md`), while
the review gates are tracked separately — and no content open occurred
(root absent, flag False, reads/attempts 0).

## 2. OpenSpec P16 delta consistency — PASS

- `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p16/spec.md`
  (168 lines) mirrors `TASK_PACKET.md` P16-01…P16-06: 1M source + stat-first
  open + one-open/one-attempt (Requirement 1), exact P7 floor/support rule +
  entropy/column preconditions (Requirement 1), frozen matrix
  (N=32768/TRAIN 2026092000..2003x4/DEV 2026092010..2017x8, per-stream RNG
  restart, P13-shared genie TRAIN, `(residual,K1,K2)` lexicographic freeze
  before DEV), five-step operational DEV with six buckets, `5*(K1+K2)+64`
  disclosure + `10*N+63=327743` public control + literal recount,
  13 integrity gates in frozen order + exact>=62/64 AND Wilson>=0.90,
  twelve-flag CLI + five-file stub-before-open + per-block checkpointing +
  budgets, and the operational-but-model-sampled boundary (bounded claim,
  "not real-data qualification", candidate/not-confirmed/BLOCKED only).
- All nine P16 task boxes unchecked: `grep` shows `- [ ] P16-1` … `- [ ] P16-9`
  only, no `[x]`/`[X]` in the P16 section of `tasks.md`.
- Docs authorize no production behavior: spec.md:18 ("authorizes no production
  behavior"), tasks P16 header ("never checks its own boxes"), `P16_FREEZE.md`
  §6 ("authorizes nothing"), `P16_IMPLEMENTATION_NOTES.md` ("No
  self-acceptance").

## 3. Reuse proof (no accepted-file changes from this wave) — PASS

- `git status --porcelain` + `git diff`: the only tracked file carrying P16
  strings is `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (the
  appended P16 section). `grep -rln "p16\|P16\|operational_f13"` over
  `target_rate.py two_layer.py sc.py prior.py empirical_genie_scaling.py
  target_n_scaling.py protocol.py empirical_channel.py transform.py
  v35_algorithm_development.py` returns nothing (RC=1).
- `sc.py`'s tracked diff is the accepted P11 chunked change (`chunk_rows`
  keyword-only, default 512), predating this wave (mtime 09-14; P16 files
  dated 09-15). The runner only *contract-checks* it
  (`operational_f13.py:445-461`) and calls accepted `sc_decode` with the
  production default — never passes a chunk argument (enforced at :455).
- The runner only CALLS accepted semantics: P7 load/support/preconditions
  (`load_v25_channel_counts`, `target_preconditions`, `PRECONDITION_ORDER`
  at :105/:117-121), P13 construction/allocation (`block_genie_risks`,
  `select_empirical_split` at :108 — single TRAIN-only genie call site at
  :1685), P4 wiring/constants (`DISCLOSED_BITS_PER_COORDINATE`,
  `LABEL_SCALE`, `TAG_BITS=64`, `labels_to_bits`, `seed_bits_for` at
  :124-130), P5 hard-candidate/tag pattern (`Provenance.PRIOR_ONLY` /
  `CANDIDATE_CONDITIONED`, Toeplitz tag at :766/:806/:819), P11 chunked SC
  (sole `sc_decode` call site at :623 inside `_decode_layer`), P12
  `budget_k_total` at :122/:1706. No P7 empirical-order (surrogate) import
  exists; imports are the allow-list at :104-130 only.

## 4. Frozen budget/construction — PASS

- Recomputed independently (pinned interpreter, `math.floor`, no repo code):
  `H=0.8010378248977232` → raw `6811.785936024635` → floor **6811**;
  `H=0.8010378248977231` → `6811.785936024634` → floor **6811**. Both
  spellings agree; 0.786 from any integer boundary. (Operator reported
  `...634` for both spellings; my `...232`-spelling value ends `...635` —
  1-ulp repr dust, immaterial. Non-blocking note N1.)
- Leakage `5*6811+64 = 34119` vs budget `1.3*32768*H = 34122.929680123176`;
  `f = 1.2998502888172847 <= 1.3` (operator `1.2998502888` ✓ rounding).
- Code: `k_total_raw` at :1705, shared-identity `budget_k_total` (P12,
  `target_n_scaling.py:421-429`, floor + clip `[0,2N]`) at :1706, full-budget
  use (every feasible `(K1,K2)`, `K2=K_total-K1`), `(5*K_total+64)/(N*H)<=1.3`
  assert at :1707-1713, exhaustive lexicographic `(residual,K1,K2)` via
  accepted `select_empirical_split` (`empirical_genie_scaling.py:461-497`,
  `key=(residual,k1,k2)` at :486-488), freeze digest + freeze-before-DEV
  checkpoint at :1720-1763, DEV never touches construction (orders passed
  read-only at :1810-1811; replay gate at :2020-2043).
- P7 empirical orders never imported (see §3 import allow-list).

## 5. Operational DEV audit — PASS

Per-block flow (`run_operational_block`, :708-884): sample (caller :1787) →
disclose U1 at `order1[:K1]` (:767) → L1 SC (:784-786) → L2 metrics from Bob
+ hard L1 candidate ONLY (`gather_p2_metrics(bob, high_hat, ...)` at :805;
  true high never enters) → disclose U2 at `order2[:K2]` (:807) → restarted
  L2 SC (:812-814) → `label_hat=32*high_hat+low_hat` (:816) → one 64-bit
  Toeplitz tag (:819-821) → single classify (:829-835) → sentinel
  (:837-852) → scalar record (:853-884).
- Causal wiring: truth-sentinel probe is code at :637-645/:843-852 (mutate
  every truth copy, prove protected metric/disclosure/decision arrays
  bitwise unchanged) and is covered by focused
  `test_causal_l1_candidate_l2_wiring_sentinel` (green). Truth enters only
  sampling, disclosed values, tag construction, scoring — verified by
  inspection (:753-762 copies; :767/:807 disclosed slices; :819 tag;
  :818 scoring).
- No oracle arm/rescue/adaptive/repeated decode: functional grep shows
  exactly one `sc_decode` site (:623), one TRAIN-only `block_genie_risks`
  site (:1685), two `sample_full_block` sites (:1667 TRAIN, :1787 DEV — one
  sample per block each); no FWHT/APP/SCL/belief/list/surrogate/rescue/
  retry/second-arm/UCB identifiers in logic (only docstring truth-boundary
  prose, `retry_after_open: False` accounting keys, and the documented
  test-only `l1_candidate_override`/`tag_fn` seams, never passed by the
  frozen CLI).
- Buckets: `OUTCOMES` (:203) and `OUTCOME_PRECEDENCE` (:258-265) are exactly
  the packet's six; `classify_operational_outcome` (:512-530) +
  `_record_dict_consistent` (:918-994, incl. `exact ⟺ outcome==exact` at
  :979-980, undetected never success) give disjoint/exhaustive buckets;
  `resource_abort` only via `_abort_block` (:680-705, DEV budget path
  :1771-1781) with zero disclosure and no events (`block_events` returns
  `[]` at :1029).
- **Adjudication item 1 (nonfinite bucket): RATIFIED.** Packet P16-02 step 5
  lists `exact, undetected, verify_failed, decode_failed, nonfinite,
  resource_abort`; code matches exactly (:203, :258-265, :512-530) with
  `nonfinite` outranking generic `decode_failed` (:526-527, :961-968) and
  the flag retained for the `nonfinite_zero` gate (:2067-2070). No accepted
  invariant breaks: P8's taxonomy (`protocol.py:92` five-tuple, nonfinite as
  flag folded into `decode_failed` + separate zero-gate) is untouched (§3);
  the six-bucket meaning lives only in `operational_f13.py` +
  `test_nbpolar_operational_f13.py`. No new merged meaning leaks into any
  accepted module.
- Tag semantics: master = DEV stream seed + 10000 at :1814
  (`PUBLIC_TAG_MASTER_OFFSET`, :157); domain
  `nbpolar-p16-operational-f13-seed:<master>:<n>:<block>` at :543-553
  (`SEED_PREFIX`, :204); 64-bit (`TAG_BITS`, :819-820); bit length
  `seed_bits_for(n)` = `10*32768+63` = **327743** verified
  (`two_layer.py:207-209`); raw seed never persisted (tag payload is only
  `{"seed_bit_length": …}` at :1076; banned-key walk covered by
  `test_scalar_only_outputs_carry_no_secret_material`, green).
- Disclosure: full block `5*(K1+K2)+64` (:868-872, replayed :981-989);
  partial failure counts only actual bits (L1-fail → `5*K1`; L2-fail →
  `5*K1+5*K2`, no tag; abort → 0); public `327743` per invoked tag
  (:873/:988); independent literal recount (`block_events` :1027-1079,
  `recount_events` :1082-1105, zero-mismatch gate :2097-2119) — my S2 smoke
  independently re-observed `64*(5*K+64)` / `64*327743` with `mismatches: []`.

## 6. Scientific gates — PASS

- `recovery_gates` (:582-602) requires BOTH `exact>=62/64` (`total==64`
  pinned at :589) AND one-sided 95% Wilson LB `>=0.90` (`WILSON_Z =
  1.6448536269514722`, `protocol.py:85`; formula `protocol.py:177-189`).
- Recomputed independently with my own Wilson implementation (same z):
  62/64 → `0.9098711859061207` → rounds `0.9098711859` TRUE;
  61/64 → `0.8883797143731994` → rounds `0.8883797144` FALSE. Both frozen
  boundary literals exact.
- Labels (:605-610): all integrity true + recovery pass → CANDIDATE;
  integrity true + either recovery gate false → NOT_CONFIRMED; else
  `BLOCKED(<earliest>)` in `INTEGRITY_GATE_ORDER` (:267-281, 13 gates).
- No recovery-threshold confusion: no genie UCB identifier anywhere in this
  gate (functional grep clean); `check_wilson_boundary` (:563-579) pins the
  62/61 pair pre-DEV, fail-closed on helper drift.

## 7. Refusal/consumption/checkpoint ordering — PASS (items 2+3 ratified)

- Refusal order in code: existing root (:1355) → floor/source/target-f
  (:1357-1364) → chunk contract incl. `_minus_block` default-512 signature
  pin (:1365/:445-461) → tag-bits (:1366) → N (:1367) → seed grouping
  4-TRAIN/8-DEV, distinct-within, disjoint-across (:1368-1397) → five stubs
  (:1410-1428) → stat size check (:1437-1442) → single content open + coupled
  read-1/1 + attempt-1/1 consumption (:1443-1466) with module reopen guard
  (:313/:1432-1433) → preconditions with zero genie/SC on failure
  (:1491-1517; first genie :1685, first SC in DEV) → TRAIN/DEV. My S1 probe
  independently re-observed: existing-root `FileExistsError`, overlap/`n`/
  chunk/tag `ValueError`s, CLI-parse `SystemExit(2)` — all pre-open, flag
  still False, no stray files.
- Five files created before open, checkpointed after the freeze (:1762-1763)
  and after every TRAIN (:1700-1702) and DEV (:1865-1867) block; no sidecars
  (`OUTPUT_FILES` :282-288; S2 smoke re-observed exactly the five files +
  64 jsonl lines).
- Consumption at first open with reopen guard ✓ (:1443-1444, :313);
  `MemoryError` path preserves checkpoints + finalizes BLOCKED if possible,
  never reruns (:1913-1934); post-open no-repair/no-rerun (all post-open
  failures are BLOCKEDs or resource errors; `main` returns 2/1, never
  retries).
- **Adjudication item 2 (TRAIN per-block checkpoint shape): RATIFIED.**
  TRAIN checkpoints rewrite the same five files with `RUNNING(train k/16)`
  progress summaries; `per_block_outcomes.jsonl` is untouched during TRAIN
  (appends only at :1777/:1856 in DEV); TRAIN contributes progress counters
  only (`pending_freeze` + `train_blocks_done`, :1594-1597). Matches
  packet P16-05 "after every block" and freeze §4; cannot fabricate evidence
  (final gates require `constructed` + 64 DEV records).
- **Adjudication item 3 (DEV abort-fill vs TRAIN-breach raise): RATIFIED.**
  TRAIN breach raises fail-closed `OperationalF13ResourceError` (:1661-1666
  — no honest construction possible, no label fabricated, checkpoints
  preserved); DEV breach abort-fills remaining blocks (:1771-1781) and
  completes as `BLOCKED(resource_limits_met_and_no_abort)` via the resource
  gate (abort records zero-disclosure/error-free, excluded from events at
  :1029 and from SC accounting at :2073-2077, `resource_ok` forced False at
  :2160-2166). Both preserve checkpoints; neither reruns nor fabricates.

## 8. OPERATOR-FLAGGED ITEM 4 (2026092001 coincidence) — RATIFIED, stream fresh

- Located independently: `comparison_bench/src/comparison_bench/formal_ir/
  nonbinary_v22_de_gate.py:45` (`seed: int = 2026092001`) and
  `comparison_bench/src/comparison_bench/cli/run_v22_de_gate.py:30`
  (`--seed` default `2026092001`), plus two historical `de_gate.json`
  outputs under `nbldpc_v22_20260816/`.
- Track determination: the v22 usage is the Monte-Carlo sampler seed for the
  V22 structured-construction **density-evolution** gate — candidate degree
  distributions evaluated on the V17 structured channel via
  `evaluate_candidate_structured` (MC-DE, `claim_boundary: diagnostic_only`).
  Neither v22 file references `load_v25_channel_counts`, `channel_counts.npz`,
  or `np.load`: the numeral seeds synthetic DE draws, never an artifact
  content open and never a Phase-4 scientific attempt.
- Freshness rule (same as the P8/P13 coincidences): fresh ⟺ disjoint from
  consumed artifact-read streams; test-local/different-track numerals ≠
  consumption. `2026092001`'s v22 appearance consumed nothing; P16 TRAIN is
  its first consumption-context appearance. The packet value is retained
  verbatim and the stream is scientifically fresh for P16. All other eleven
  frozen seeds appear only in P16 wave files (module, focused test as
  constant-reads, spec, tasks); all twelve are disjoint from every Phase-4
  consumed stream in code (P5 1470s, P6 1550s, P8 1700s, P9 1710s/1720s,
  P11 2026091800, X11 1760, P16-test 1753..1765).

## 9. Tests — PASS (23 + 358 green, pinned interpreter, fresh basetemps)

- Focused: `23 passed in 466.08s`
  (`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_operational_f13.py -q
  -p no:cacheprovider --basetemp=/tmp/p16-preexec-focused`).
- Full NB-Polar suite: 270 + 88 = **358 passed** (all 23
  `test_nbpolar_*.py` files, same pinned interpreter/flags,
  `--basetemp=/tmp/p16-preexec-full{,2}`; 1129.59s + 48.72s).
- Coverage matches the P16-05 list: K pin, matrix constants, shared-helper
  identity, every bucket + precedence (incl. nonfinite-outranks +
  undetected-never-success), Wilson 62/61 + all three label branches,
  tag/domain separation, tiny-n real-arm recovery/accounting/truth-isolation,
  causal sentinel, construction replay, full + partial disclosure,
  recount-tamper, grouping/contract refusals, checkpoint-resume refusal,
  zero-call precondition failure, one-open guard, MemoryError, abort-fill,
  scalar-only outputs, CLI refusals, no-forbidden-access.
- Tests never open the NPZ (all runs inject `counts=`; the loader is patched
  with a raising stub at :681/:741; reopen-guard test sets/RESTORES the
  module flag with `finally` and ends False), never execute frozen streams
  `2000..2003/2010..2017` (only constant-read assertions at :232-233; runner
  tests use fresh `1753..1759/1761..1765`), never invoke production paths.
- **Adjudication item 5 (check_wilson_boundary placement): RATIFIED.**
  Called at :1515 — post-open, post-preconditions, pre-TRAIN (first genie
  :1685), hence before the first DEV block per the packet. Zero artifact
  interaction (pure function of `WILSON_Z` + frozen literals; no counts, RNG,
  file, or call-counter contact). Cannot affect the frozen gate path: with
  the accepted helper it returns silently and changes no state; on helper
  drift it raises `ValueError` → `main` exit 2 with stubs present (a
  post-open contract BLOCKED under the Wave-C rule). No consumption, write,
  or tuning power.

## 10. Wall/RSS projection — PASS (explicit margin)

Grounding: P15 N=32768 cell 569.717255s / 32 genie blocks
(`OPERATOR_RETURN.md` §10; RSS 593866752 B); P11 N=65536 chunked decode
14.584s, N=262144 66.088411s. My bounded smoke (injected tables, temp root,
real kernels, N=32768): TRAIN-shaped block 15.55s (front 2.95 + genie 12.59);
single real `sc_decode` 7.78s/7.79s (consistent with O(N log N) scaling from
P11); `select_empirical_split` k=6811 0.35s.
Projection: TRAIN 16×15.55 ≈ 249s; DEV 64×(2.95 + 2×7.79) ≈ 1186s; freeze +
finalize + checkpoint-JSON ≈ 60–300s → **≈1500–1750s vs 2100s**, margin
≈ 350–600s (17–29%). RSS: P15 594MB @N=32768 bounds the base; chunked SC
bounds decode state (P11 710MB even at N=262144); pooled risks ≈ 1MB →
projected <1GB vs 2GiB cap and 2GiB `ulimit -v`. Fail-safes intact: in-run
wall/RSS guard (`_budget_exceeded`, TRAIN raise / DEV abort-fill), external
`timeout 2100`, single-thread BLAS/OpenMP + `MALLOC_ARENA_MAX=2` in the
frozen command. S2 orchestration smoke (own fakes/seeds/2000s-free,
temp root): five files pre-open, 64/64 records checkpointed, 13 gates
recorded, recount zero-mismatch, label as designed for non-frozen seeds,
NPZ flag still False.

## 11. Scope/premises — PASS

- `git status --porcelain` matches the declared Wave-A set (module, focused
  test, P16 spec dir, tasks.md P16 section, freeze + notes + STATUS in the
  packet queue) plus pre-existing out-of-scope dirt (P3 tracked edits,
  sibling phase queues) untouched by this review; no accepted-module,
  P12–P15, or old-root writes (§3).
- HEAD `ab173f2a` unchanged: no P16 commit exists (all P16 files untracked);
  no commit/push performed or requested.
- Output root still absent (`stat` → No such file); reads/attempts still 0
  (`STATUS.yaml` re-read unchanged); NPZ metadata stat 25166822 bytes only
  (== `EXPECTED_NPZ_BYTES`, :162); module flag False in every probe process.
- `FROZEN_COMMAND` (:290-303) is byte-identical to the packet §P16-06 command
  (programmatic diff: equal True).

---

## Wave-C exit-code / label reading rule (binding for the gate run)

- **Exit 0 ⟺ completed label persisted**: read `outcome_label` from
  `aggregate_summary.json` (CANDIDATE / NOT_CONFIRMED / `BLOCKED(<earliest>)`
  — DEV abort-fill and recovery-false paths both complete with exit 0).
- **Exit 2 = pre-open refusal AND post-open contract BLOCKEDs**:
  `ValueError`/`FileExistsError`/`OSError` in `main` (:2226-2228) —
  disambiguate by root/stubs per P14 precedent: no root → pre-open refusal
  (nothing consumed); five stubs present → post-open contract BLOCKED
  (`TargetPopulationContractError` subclasses `ValueError` at
  `target_construction.py:340`; `check_wilson_boundary` drift likewise).
- **Other non-zero (=1 + traceback) = post-open resource/unexpected, never
  rerun**: `OperationalF13ResourceError` (`RuntimeError`, TRAIN wall/RSS
  breach, MemoryError conversion) is NOT caught by `main`; checkpoints are
  preserved and consumption is spent.

## Frozen record (for Pre-RESULT recomputation)

K_total 6811 (raw 6811.78593602463x both H spellings); leakage 34119 ≤
34122.929680123176; f 1.2998502888172847 ≤ 1.3; public 327743/tag; seeds
TRAIN 2026092000..2003×4 = 16, DEV 2026092010..2017×8 = 64, masters
DEV-seed+10000, domain `nbpolar-p16-operational-f13-seed:<m>:32768:<b>`;
command = packet §P16-06 verbatim (single-thread env, `ulimit -v 2097152`,
`timeout 2100`, pinned interpreter, twelve flags, `--out-dir
.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate`);
budgets 2100s / 2GiB RSS / 2GiB virtual; schema exactly
`frozen_plan.json`, `construction_and_allocation.json`,
`per_block_outcomes.jsonl` (64 records), `aggregate_summary.json`,
`report.md`; gates per `INTEGRITY_GATE_ORDER` (13) + exact≥62/64 AND Wilson
LB≥0.90 (62/64→0.9098711859 pass; 61/64→0.8883797144 fail); labels
`TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` /
`..._NOT_CONFIRMED` / `BLOCKED(<earliest>)`; `PLANNED_GENIE_CALLS=32`,
`PLANNED_SC_CALLS_MAX=128`.

## Findings

Non-blocking suggestions (do NOT repair post-open; batch into a later packet
if ever wanted):
- N1 (`operational_f13.py:1827-1828`): the DEV-loop escaped-exception handler
  references `result.stream_seed`/`result.block_index` where `result` may be
  unbound if `run_operational_block` raised before assignment → would raise
  `UnboundLocalError` (exit 1, checkpoints preserved, no BLOCKED summary).
  Unreachable in the frozen run (all SC/tag failures are caught internally
  at :781-825; inputs pre-validated) — prefer `seed`/`block_index` locals.
- N2: checkpoint JSON (pooled means ≈ 4×32768 floats) costs a few s/block ×
  80, folded into the §10 upper band; margin still holds.
Observations (no action): O1 — 22 collection errors in
`comparison_bench/tests/` outside `test_nbpolar_*` (e.g.
`test_v72p2d7_*`) are pre-existing and out of scope. O2 — operator's raw-K
repr last-ulp dust (§4), immaterial. O3 — `STATUS execution_authorized: true`
with reviews pending is packet authorization, not a gate bypass (§1).
No blocking issues. No scope creep (thin runner + tests + delta + freeze
docs only; no second arm, retry, surrogate, or benchmark logic).

## Closure

NPZ content never opened (stat 25166822 bytes only); reads/attempts still
0/0; output root still absent; HEAD unchanged; no commit/push; no file
outside this review was written by the reviewer. Pre-RESULT must recompute
allocation, 64 outcomes, Wilson, disclosure/public accounting, gates,
resources, and the five-file inventory from the five artifacts before any
label is published.
