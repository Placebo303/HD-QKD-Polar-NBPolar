# Independent Pre-EXECUTE review — NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC

Reviewer: independent reviewer-go instance (did not write the code; read-only).
Date: 2026-09-16. Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(Python 3.12.3, numpy 2.5.3, pytest 9.1.1, pandas 3.0.5).

Constraint closures (verified at review time):

- **NEITHER protected input was content-opened by this review.** `channel_counts.npz`
  and `pairs.parquet` were accessed with `stat` only (size/mtime): NPZ 25,166,822 B /
  mtime_ns 1787074449691122000; parquet 1,354,289 B / mtime_ns 1789155517259296100.
  Matches `P19_FREEZE.md` §11 exactly.
- The real gate command was **never run**. No Model-F/raw/real/EVAL access; no
  P12–P18/old-root writes; no commit/push. The only file written by this review is
  this file.
- Reads 0/1 + 0/1, attempts 0/1 (STATUS.yaml and module globals), result null,
  output root absent before and after this review.

## VERDICT

**PASS WITH COMMENTS** — the frozen execution contract is internally consistent,
packet-faithful and safe to execute once as registered. R1, R2, R4 and R8 are
**ratified** below with exact equivalences. Four non-blocking findings (N1–N4);
none can change the run, a gate, or a scientific conclusion. N1 is a one-character
documentation fix that is cheap to apply before Wave-C; if it is not applied, the
authoritative command is `P19_FREEZE.md` §6 (this review uses it) and the Pre-RESULT
review must compare evidence against that document, not against the plan-copy string.

Blocking issues: **none**.

## Non-blocking findings (file:line)

- **N1** `holdout_backoff_diagnostic.py:390` (`FROZEN_COMMAND` literal) reads
  `cd /mnt/Code/HD-QKD_Polar_Comparison-nbpolar`, while `P19_FREEZE.md:139` (and
  every other line of the command) has the correct `/mnt/d/Code/...`. The string is
  never executed (only persisted in `frozen_plan.json`); `/mnt/Code` does not exist,
  so a copied command fails loudly with no side effects. Recommended: fix the one
  character and re-run the focused P19 file (41 s) before Wave-C so the persisted
  plan matches the freeze; otherwise treat freeze §6 as authoritative (this review
  does). Not blocking per AGENTS.md §1.1 (cannot cause a wrong conclusion,
  irreproducible result, unauthorized execution or destructive overwrite).
- **N2** `P19_FREEZE.md:192` and `P19_IMPLEMENTATION_NOTES.md:148-154` justify the
  strict count gates by quoting an `"Assert these counts"` instruction. That literal
  sentence is not in `TASK_PACKET.md`; the packet's actual text is `"...for 27 SC
  calls and 15 tags"` (packet:41) and `"Integrity covers ... 27 SC calls and 15
  tags"` (packet:59). The substance (27/15 as integrity totals) is packet text; only
  the quotation is loose. Documentation only.
- **N3** The count gates use a joint `full_budget` (`hb.py:1608-1621`): an L2-only
  shortfall (L1/L2 SC exactly 27, tags 14) sets `sc_calls_exact=False` as well as
  `tags_exact=False`, so the label is `BLOCKED(sc_calls_exact)` rather than
  `BLOCKED(tags_exact)`. Both booleans are persisted, so the transcript is fully
  diagnosed; the earliest-gate rule is applied mechanically. Semantics note only.
- **N4** `test_nbpolar_holdout_backoff_diagnostic.py:1489`
  `assert "holdout_microcheck" in hb.__file__ or True` is a tautology. Cosmetic.

## Numbered checklist (exact commands + raw evidence)

### 1. STATUS exactness — PASS

`cat .workbuddy/.../STATUS.yaml` shows, verbatim: `state:
IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE`; `tier: Y`; `execution_authorized:
true`; `train_artifact_reads_allowed: 1` / `used: 0`; `hold_data_reads_allowed: 1` /
`used: 0`; `attempts_allowed: 1` / `used: 0`; `result: null`; `pre_execute_review:
pending`; `pre_result_review: pending`; `next_gate: INDEPENDENT_PRE_EXECUTE`. All
declared values exact.

### 2. OpenSpec P19 delta consistency — PASS

`cat openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p19/spec.md`
(221 lines) vs `TASK_PACKET.md` (88 lines): mission; P16 identity (N/K1/K2/K_total,
digest `055c9064…faea1b`, K/f replay, `5*6811+64 = 34119 <= 1.3*N*H`); manifest
`400/102400`; one-open inputs with the 25,166,822-byte stat check and the exact P7
floor rule; P18 `form_holdout_blocks` with blocks `1600..1727 / 1728..1855 /
1856..1983` and unused remainder `1984..1999`; the five arms with K
`319/6492, 447/6492, 319/7004, 447/7004, oracle 0/6492`, leakages
`34119/34759/36679/37319/32524`, fixed +128/+512, `chunk_rows=512`, tag master
`2026092060`, P19/arm/block seed domain, 27 SC / 15 tags asserted; oracle control
"true high-layer conditioning used ONLY as an oracle-labelled L2 conditioning/label
control", never operational/deployable, excluded from aggregates; scalar-only
descriptive outputs incl. buckets/`undetected`-not-success/SER/NLL/CE-ratio; paired
tables + first-operational-recovery-arm + neutral non-monotone flag; the 20 integrity
gates in frozen order; no-threshold rule with COMPLETE for 0/3..3/3 and
`BLOCKED(<earliest gate>)` otherwise; sixteen-flag CLI, five-file pre-open creation,
per-(arm, block) checkpoints, 2 GiB/600 s budgets, no-rerun/forbidden list and the
bounded claim. No divergence from the packet found; the strict 27/15 + resource-stop
carve-out (delta:146-150) is the R1 decision ratified below.

`awk '/## P19 implementation tasks/,0' tasks.md` → 9 × `- [ ]`, 0 × `- [x]`: all
P19 boxes unchecked, as required.

### 3. Reuse + immutability — PASS

`stat -c '%y %n'`: `sc.py` 2026-09-14 19:35, `prior.py` 09-12 03:38,
`pairs_loader.py` 09-12, `v35_algorithm_development.py` 09-12,
`target_construction.py` 09-14, `two_layer.py` 09-13, `transform.py`/`shared.py`
09-12, `operational_f13.py` 09-15 16:27, `operational_f13_replication.py` 09-15
19:38, `holdout_microcheck.py` 09-16 00:35, `__init__.py` 09-13 — all predate the
P19 wave (files created 09-16 20:02–20:37). P16 evidence root mtimes 09-15
18:07–18:28 and P18 evidence root 09-16 01:51–01:52 unchanged; P17 root
(`operational_replication_gate`) 09-15 21:08–21:42 unchanged; `find` over P12–P18
roots for files newer than 19:00 today returns only P18 *queue* lifecycle docs
(`MAIN_THREAD_ACCEPTANCE.md`, `STATUS.yaml`), never evidence-root files.
`git grep` shows predecessor sharing is by identity
(`hb.run_operational_block is opf.run_operational_block`, test:513-527, green).
`chunk_rows=512` plumbed: `hb.py:1860` calls `opf._check_chunk_contract(512)`, which
asserts `_minus_block(chunk_rows=512)` keyword-only default and that `sc_decode`
exposes no chunk argument; `sc.py:177/216` confirm both. The control's
`_decode_layer` reaches the same default path.

### 4. Identity ordering before the protected opens — PASS

Code order (`hb.py:1850-1921`): existing root refusal → floor/source/n/k1/k2/
chunk-rows/tag-bits/hold-frames/block-frames/remainder-frames/tag-master contracts →
`check_frozen_arm_table()` → digest-flag pin → `verify_predecessor_construction`
(P16 JSON read) → `verify_split_manifest` (JSON) → `verify_p18_block_identity()`
(code-level) → one-open guards → NPZ existence + stat-only size check and parquet
existence/stat → five-file stub creation (`:1970-1984`) → first protected open
(`:1994`). Refusal probes consumed nothing (zero root, zero loader calls): focused
tests `test_predecessor_identity_tamper_refusals_zero_reads_zero_root` (6 tampers),
`test_manifest_and_p18_pin_refusals_zero_reads_zero_root` (4 + 3 tampers),
`test_one_open_guards_refuse_reopen_with_zero_execution`,
`test_existing_root_refusal_zero_execution`, `test_cli_parser_and_run_contract_
refusals_before_open` (11 flag refusals + subprocess exit 2) — all re-run green
below. Tamper probes fabricate construction/manifest copies under `tempfile`
directories only (`make_construction_file`/`make_manifest`); the real P16 root is
read (JSON, 2,581,862 B) only by the accepted verifier. Independent recomputation in
this review: `verify_predecessor_construction(...)` → n=32768, k_total=6811, k1=319,
k2=6492, `digest_match=True`, recomputed digest
`055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`, f=1.2998502888172847,
leakage_bits=34119, orders length 32768; manifest → `nbldpc_v25_split_manifest_v1`,
hold 400/102400; `verify_p18_block_identity()["verified"] is True`.

### 5. Five-arm semantics audit — PASS

`FROZEN_ARMS` (`hb.py:246-257`) in exact order
`base(319,6492,34119)` → `l1_plus(447,6492,34759)` → `l2_plus(319,7004,36679)` →
`both_plus(447,7004,37319)` → `true_l1_control(oracle,0,6492,32524)`;
`check_frozen_arm_table()` re-derives increments (`+128`/`+512`), leakage
`5*(K1+K2)+64`, oracle label, base `f<=1.3` and the design totals 27/15 before any
root exists. Slot loop (`hb.py:2058-2062`, `2191-2295`) is arm-major
(base→l1_plus→l2_plus→both_plus→control) × blocks 0..2. Operational arms call the
accepted `run_operational_block` with the verified `order1[:K1]` + candidate-
conditioned `order2[:K2]` (2 SC/block; `operational_f13.py:781-825`); the control
calls `run_oracle_control_block` (1 SC/block, `hb.py:637-757`). Design totals
`PLANNED_SC_CALLS=27`, `PLANNED_TAG_INVOCATIONS=15` (`hb.py:264-268`), key bits
`526200`, public bits `15*327743=4916145`. Tag domain: prefix
`nbpolar-p19-holdout-backoff-diagnostic-seed`, string
`<prefix>:<master>:<n>:<arm>:<block_index>:<counter>`, SHA-256 MSB-first truncated
to `10*N+63 = 327743` (`hb.py:576-609`), master 2026092060. Domain distinctness from
P16/P17/P18 (prefixes `…p16-operational-f13-seed`, `…p17-operational-replication-seed`,
`…p18-holdout-microcheck-seed`) is proven by test
`test_p19_seed_domain_arm_block_separation` (15 distinct seeds; scored closure seed
equals the P19-domain seed) — green. Assert-and-STOP semantics: fail-closed asserts
before the root, budget abort-fill, MemoryError classification, no repair/retry
paths (`grep retry/reopen`: guards + accounting only). Independent bounded smoke
(injected counts/table, fakes at the SC seams, `/tmp` root): 15 records in order
base×3…control×3, 27 SC/15 tags, partition `{operational:12, control:3,
unassigned:0}`, control records carry `ORACLE_TRUE_L1_CONTROL` + `oracle_truth_use`
with 32524 key bits, operational 34119/34759/36679/37319 with
`CANDIDATE_CONDITIONED` L2, label COMPLETE, `integrity_all_pass=True`.

### 6. Oracle isolation and R4 — PASS (R4 ratified)

Control path (`hb.py:637-757`): metric gathers `gather_p2_metrics(bob, true_high,
p2_table)` — the accepted `[U1,B,U2]` table's U1 index — provenance
`ORACLE_CONDITIONED`, one L2 SC, `label_hat = 32*true_high + low_hat`, at most one
tag, no L1 SC/L1 disclosure; record carries `ORACLE_TRUE_L1_CONTROL` and
`oracle_truth_use=True`; `oracle_isolation_ok` uses a strict two-partition filter
with `unassigned` failure; `build_aggregates` operational aggregates read only the
operational partition; `recovery_diagnostics` pairs/recovers/first-arm only over
`OPERATIONAL_ARM_NAMES`; wording `ORACLE_RULE`, `deployable: False`,
`excluded_from_operational_aggregates: True` and the isolated report section
explicitly forbid an operational/deployable reading. The operational helper's L2
metric gathers on its hard L1 candidate `high_hat` (`operational_f13.py:805`), the
accepted P16 genie used `gather_p2_metrics(bob, high, p2)` with
`ORACLE_CONDITIONED` (`operational_f13.py:1670-1676`) — i.e. the same index space
(channel high-layer symbol of `A = 32*high + low`), so the control conditions on the
**true high-layer symbol in the accepted index space**, not on the transform-domain
`u1_true` vector, which is retained only as a sentinel input. This is exactly the
packet's "true U1 only as an oracle-labelled L2 conditioning/label control"
(packet:36-38) read through the accepted `[U1,B,U2]` construction. **R4 ratified.**
Truth isolation is enforced by the accepted sentinel and by structural record
consistency; tests `test_oracle_isolation_control_excluded_from_operational_
aggregates` (partition + three tamper variants) and the tiny real control test
(sentinel, arrays bitwise unchanged) are green.

### 7. R1 adjudication (strict-exact vs P18-style maxima) — RATIFIED, operator's reading is packet-faithful

Facts: `sc_calls_exact`/`tags_exact` (`hb.py:1595-1621`) recompute `derived_sc`
(1+l2_invoked per operational record, l2_invoked per control) and `derived_tags`,
and require the frozen totals exactly; the only exception is
`accounted_partial = resource_stop is not None and not full_budget`, so a registered
resource stop surfaces as `BLOCKED(resource_limits_met_and_no_abort)` with the fully
accounted partial transcript. Without a stop, a `decode_failed`/`nonfinite`/escaped
exception shortens the transcript and the label is `BLOCKED(sc_calls_exact)` or
`BLOCKED(tags_exact)` (test `test_scripted_buckets_undetected_nonfinite_blocked`
asserts `BLOCKED(sc_calls_exact)`).

Ruling: the packet-faithful reading is **strict-exact**. The packet names the totals
unqualified — "for 27 SC calls and 15 tags" (packet:41) and "Integrity covers …
27 SC calls and 15 tags" (packet:59) — with no "at most", and it does not carve out
decode failures; its only stated escape is `"Integrity/resource failure returns
BLOCKED(<earliest gate>)"` (packet:56-57). Under the packet's own definition a short
transcript means "integrity does not hold", so the "COMPLETE for every outcome
pattern" sentence remains consistent: it is conditioned on integrity holding. The
arm/block loop guarantees the declared invocation *pattern* for all 15 slots (12
operational passes × 2 calls, 3 control passes × 1 call), so **27/15 is the
all-invoked requirement**; an SC that raises is a declared-design deviation and is
blocked, never silently accepted. The P18 "recomputed maxima" wording belongs to the
P18 packet and is not reintroduced here. The residual imperfection (N3) is cosmetic
gate naming, not a false statement, and all gates/records are persisted.
Deciding strict-exact now also fixes the semantics before the single attempt
(one-shot, no rerun), and its failure direction is conservative (it can only
withhold COMPLETE, never fabricate it). **R1 ratified with the precise equivalence:**
(a) all 27/15 invoked and every other gate true → COMPLETE for every 0/3..3/3
recovery pattern; (b) registered resource stop → earliest failing gate is
`resource_limits_met_and_no_abort`; (c) no stop and a short transcript → the count
gate that is false (sc first when SCs short; sc also when only tags are short) →
`BLOCKED(sc_calls_exact)`/`BLOCKED(tags_exact)`; (d) nonfinite additionally leaves
`nonfinite_zero=False`, undetected leaves `undetected_zero=False`, both as persisted
gates.

### 8. R2 + R8 adjudication — RATIFIED

**R2:** `l1_plus` (34759), `l2_plus` (36679) and `both_plus` (37319) exceed
`1.3*N*H = 34122.9…` bits by construction; only `base` replays the accepted budget.
No f-gate misfires: `FROZEN_TARGET_F` is used only in `check_frozen_arm_table`
(base assertion, `hb.py:522-523`) and in descriptive plan fields
(`within_planning_f` per arm, `hb.py:1300`); `f_inequality_base_only` names the
base-only limit. Wording is descriptive everywhere: `backoff_note` ("descriptive
diagnostic disclosure levels, not qualified operational points"),
`RATIO_RULE`/aggregate `ratio_note` ("explicitly NOT qualification reconciliation
efficiency"), `CLAIM_SCOPE`, report section "no threshold, no winner". Ratified:
the three plus-arms are descriptive disclosure levels, never qualified operational
points.

**R8:** the constructed verbatim command (`P19_FREEZE.md` §6) is the accepted P18
command form (`P18_FREEZE.md:104-107`) with P19 values only: module
`holdout_backoff_diagnostic`, `--tag-master 2026092060` (P18: 2026092050), P19
`--out-dir`; the same 16 required flags in the same order as the P19 parser
(`hb.py:2389-2405`; parser `required` set checked by test:1357-1363). The five
hold flags were invented in P18 and already accepted there; no new flag was invented
for P19. `--k1 319 --k2 6492` pin the `base` arm and refuse anything else
(`_check_base_k1/_check_base_k2`); the other four arms are module constants with no
CLI surface, so the arms are not tunable. Ratified — see the recorded command and
N1 for the plan-copy `cd` character.

### 9. No-threshold + outputs — PASS

`backoff_label` takes only the 20 integrity gates; functional greps over
`hb.py` for `wilson|Wilson|WILSON|EXACT_MIN|exact_fraction|fer_rate|recovery_gates|
select_label|superiority|winner` find only the explicit no-threshold prose; no
`recovery` parameter exists; `protocol.py`'s Wilson helper is not imported. Every
0/3..3/3 pattern is COMPLETE exactly when the counts hold: tests
`test_no_threshold_labels_all_recovery_patterns` (4 operational + control patterns),
`test_scripted_buckets_undetected_nonfinite_blocked`, `test_outcome_classifier_every_
bucket_and_precedence` — all green. Non-monotone reporting is neutral
(`ordered_exact_counts_non_monotone` + `non_monotone_note`), paired tables are
per-block versus `base` with recovered/lost/same, `first_operational_recovery_arm`
scans operational arms only and is null when none has an exact block. Five files are
created before the opens (code `hb.py:1970-1984`; smoke: all five present at the
first loader call with 0 jsonl lines) and checkpointed after every record (smoke:
seams at slots 0..14 observed jsonl line counts 0,1,2,…,14; `persist` rewrites the
same three files, no sidecars). Scalar-only schema: banned-key walk over all four
JSON/JSONL artifacts green (`test_five_file_scalar_only_inventory_and_resources`),
CE-ratio is `arm_leakage*observed/sum(NLL)` per record/aggregate with the
not-qualification note. Remainder `1984..1999` recorded and unused (`used: False`);
`undetected` never success (`undetected_zero` gate, classifier precedence).
CHECKPOINT STOP: abort-fill persists 15 records with `resource_abort` slots and
finalizes BLOCKED (test green).

### 10. Tests re-run (this review, independent) — PASS

Pinned interpreter, fresh `/tmp` basetemps, `-q -p no:cacheprovider`:

- `…/python -m pytest comparison_bench/tests/test_nbpolar_holdout_backoff_diagnostic.py
  --basetemp=/tmp/p19_review_bt` → **30 passed** (41.49 s).
- `… test_nbpolar_operational_f13.py --basetemp=/tmp/p16_review_bt` → **23 passed**
  (476.27 s).
- `… test_nbpolar_operational_f13_replication.py test_nbpolar_holdout_microcheck.py
  --basetemp=/tmp/p1718_review_bt` → **51 passed** (368.58 s).

Total 104 green = operator-reported 30 + 23 + 51. No protected input is opened by
any of these suites (grep: all real-path loaders are monkeypatched to forbidden
stubs or throwaway temp files; the only path strings named are `/nonexistent/…` and
`tmp_path`). Adjudication of the packet-scoped rule: the packet permits omitting the
full NB-Polar suite "only if shared predecessor code changes or a focused failure
requires it; record why" (packet:78-80). No shared predecessor module changed
(mtime/diff evidence in check 3) and there was no focused failure, so the
packet-scoped set is sufficient; the operator's recorded reason matches the observed
state. **Ratified.**

### 11. Wall/RSS margin + bounded smoke — PASS

Projection from the accepted P18 evidence (read-only):
`holdout_microcheck/aggregate_summary.json` → wall 37.274417 s, RSS peak 520,798,208 B,
6 SC calls; `per_block_outcomes.jsonl` → 11.76–11.88 s per block (2 SC + metric/tag/
scoring) → ≈5.6–5.9 s per SC at N=32768 including load. P19 cost model: 12
operational passes × 11.8 s ≈ 141.6 s + 3 control passes × ≈6 s ≈ 18 s + load/setup
≈5 s + 15 checkpoints (small scalar writes) ≈ few s → **≈165 s projected**, ≈3.6×
margin under 600 s. Even a 1.5× per-pass inflation gives ≈250 s and a 2× gives
≈330 s, both under budget. The SC complexity is K-independent (disclosure prefixes
change data volume only), so the backoff arms do not change the envelope. RSS: P19's
live set is the same class as P18 (three N=32768 views + per-block metric planes +
scalars); projected peak ≤ ~0.7 GiB against the 2 GiB RSS cap and
`ulimit -v 2097152`, i.e. ≥ ~2.8× margin; `MemoryError` is caught over the entire
post-open path and finalized as `BLOCKED(resource_limits_met_and_no_abort)` with
checkpoints preserved (test green). Bounded smoke (this review): injected
counts/table only, fakes at `run_operational_block`/`run_oracle_control_block`, temp
root under `/tmp` — five files created pre-open, per-record checkpointing observed,
gates recorded, COMPLETE on the clean transcript; no protected access.

### 12. Scope/premises — PASS

`git status --porcelain` shows the P19 wave changes exactly as declared: new
`holdout_backoff_diagnostic.py`, new test file, new
`specs/nbpolar-phase4-p19/spec.md`, the P19 section in
`formal-ir-nbpolar-phase4-p0/tasks.md` (20:36), plus the packet directory files; the
remaining entries are pre-existing modifications from earlier accepted/ongoing work
(all mtimes ≤ 09-16 03:26) plus main-thread lifecycle docs updated at 19:38–19:41
(P18 acceptance / P19 kickoff), which `P19_FREEZE.md` §11 already accounts for.
HEAD unchanged at `ab173f2a5e17336383a897b941080b731ba3dd9e`; no commit; output root
absent; reads/attempts still 0; NPZ + parquet stat-only (25,166,822 /
1,354,289 B, mtimes unchanged); the fresh test seeds `2026092070..076` appear in no
other tracked file (`git grep` empty); no files newer than 19:00 under `results/` or
`comparison_bench/outputs_comparison/`.

## Complete frozen record (Wave-C)

| Item | Frozen value |
|---|---|
| Packet | `NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC`, Tier Y, one attempt |
| NPZ (TRAIN, cross-checkout, content-open 1/1) | `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz`, 25,166,822 B, mtime_ns 1787074449691122000 |
| HOLD parquet (content-open 1/1) | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet`, 1,354,289 B, mtime_ns 1789155517259296100 |
| Construction (P16, JSON only) | `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`; digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`; N=32768, K1=319, K2=6492, K_total=6811, f=1.2998502888172847, leakage 34119 |
| Manifest | `…/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, source `type2_1M_20260121_184040`, HOLD 400 frames / 102400 pairs |
| Blocks / remainder | `1600..1727`, `1728..1855`, `1856..1983` (32768 pairs each); remainder `1984..1999` (4096 pairs, unused) |
| Arms (order) | base 319/6492/34119; l1_plus 447/6492/34759; l2_plus 319/7004/36679; both_plus 447/7004/37319; true_l1_control oracle 0/6492/32524 (`ORACLE_TRUE_L1_CONTROL`, 1 SC, at most 1 tag) |
| Increments / SC / tags | +128 L1, +512 L2; 27 SC calls; 15 tags; 15 records; all-invoked key 526200 bits; public 4,916,145 bits |
| Tag domain | `nbpolar-p19-holdout-backoff-diagnostic-seed:<master>:<n>:<arm>:<block_index>:<counter>`, master `2026092060`, truncated to 327743 bits, seed bits never persisted |
| Env / budgets | `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2`; `ulimit -v 2097152`; 2 GiB RSS cap; `timeout 600`; in-run wall cap 600 s |
| Output root / files | `.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/` (absent now); `frozen_plan.json`, `input_and_predecessor_identity.json`, `per_block_arm_outcomes.jsonl`, `aggregate_summary.json`, `report.md`; created pre-open, checkpointed per record, no sidecars |
| Labels | `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE` iff all 20 integrity gates; else `BLOCKED(<earliest gate>)`; strict 27/15 counts (R1) |

### Wave-C verbatim command (authoritative: `P19_FREEZE.md` §6)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_backoff_diagnostic --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --hold-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --hold-frames 1600 1999 --block-frames 128 --remainder-frames 1984 1999 --tag-master 2026092060 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic
```

### Wave-C exit-code / label rule (binding for the operator)

1. **Exit 0** ⇒ the run finished and a finalized summary was persisted. ALWAYS read
   `holdout_backoff_diagnostic/aggregate_summary.json` → `outcome_label`; exit 0 does
   **not** imply COMPLETE (in-run blocked cases — resource abort-fill, undetected,
   nonfinite, count shortfall — finalize normally and exit 0).
2. **Exit 2** ⇒ refusal or post-open contract stop. Disambiguate by root/stubs:
   - no root, or root absent after the process → pre-open refusal (CLI parse, flag
     contract, identity/digest/manifest/P18-pin mismatch, one-open guard, absent or
     wrong-sized NPZ, absent parquet): consuming nothing;
   - root present with the five files and `aggregate_summary.json` carrying
     `BLOCKED(<earliest gate>)` → post-open contract stop (attempt consumed,
     checkpoints preserved).
3. **Exit 1 with traceback** ⇒ MemoryError path
   (`BackoffDiagnosticResourceError`) or an unexpected exception; root may hold
   finalized BLOCKED stubs — STOP, preserve, report.
4. **Exit 124 (timeout) or any other non-zero** ⇒ STOP, preserve the root, report;
   **never rerun, repair, retune, clean up, commit or push** (one attempt, consumed
   at the first protected content open).

## Closures

- NEITHER protected input was opened by this review (stat only). The real gate
  command was not run. No Model-F/raw/real/EVAL access; no P12–P18/old-root writes;
  no commit/push.
- Reads 0/1 + 0/1; attempts 0/1; result null; output root absent before and after
  this review.
- This review is advisory: it does not accept results, choose a route, or check any
  task box. A PASS here authorizes only the single frozen Wave-C attempt above,
  followed by the mandatory Pre-RESULT review.

