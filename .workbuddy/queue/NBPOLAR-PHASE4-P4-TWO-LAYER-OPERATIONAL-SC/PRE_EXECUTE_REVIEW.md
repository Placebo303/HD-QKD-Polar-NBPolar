# Independent Pre-EXECUTE review — NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC

Reviewer: independent backup reviewer-go instance (read-only; did not write the
module, tests, freeze or notes; no file edited other than this review).
Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, HEAD
`ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged during review; all P4 work
uncommitted, nothing staged). Date: 2026-09-13.
Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3,
numpy 2.5.3). All temp work under `/tmp/opencode/p4_review/`.
Authoritative inputs read: `TASK_PACKET.md`, `STATUS.yaml`, `PROMPT.md`,
`P4_FREEZE.md`, `P4_IMPLEMENTATION_NOTES.md`, `AUTHORIZATION_PROMPT.md`,
`docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`,
`openspec/changes/formal-ir-nbpolar-phase4-p0/` (incl. the P4 delta spec),
`two_layer.py`, `test_nbpolar_two_layer.py`, accepted helpers.

**Real 96-block gate command executed by this review: NO.**
**Attempts consumed by this review: 0 (`attempts_used` still 0).**
**Gate root before and after this review: ABSENT.**
No Model-F/artifact/parquet/TTBin/real-data access; no sibling write; no
old-evidence-root modification; no commit/push.

## Verdict: PASS

The frozen gate identity is byte-faithful to the packet and the delta spec;
the causal semantics, provenance, truth isolation, taxonomy/accounting and
tiny oracles all pass independent checks; the focused and full test suites are
green at the expected counts; scope and premises are clean. Both
operator-flagged items are adjudicated acceptable, with explicit consequences
recorded in §4 below. No blocking issue found; the single attempt may be
consumed at the frozen command, subject to the main thread's authorization.

---

## 1. Required checklist (PASS/FAIL + raw results)

All commands run with the pinned interpreter and cwd = repo root unless noted.

### 1. STATUS edit exactness — PASS

```text
$ python - <<'PY'  (yaml.safe_load over STATUS.yaml)
total keys: 19 | boolean flags: 13
TRUE flags: ['decoder_execution_authorized', 'development_gate_authorized',
             'documentation_authorized', 'implementation_authorized',
             'synthetic_exploration_authorized']
FALSE flags: ['artifact_read_authorized', 'empirical_construction_authorized',
              'phase7_authorized', 'raw_data_authorized', 'real_data_authorized',
              'scalable_decoder_authorized', 'scientific_promotion', 'scl_authorized']
attempts_allowed/used: 1 0
state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P4_TWO_LAYER_OPERATIONAL_SC
next_gate: IMPLEMENTATION_AND_SYNTHETIC_QUALIFICATION_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW
exactly the five authorized: True
sha256 STATUS.yaml = c91fe4febd1b250488c1bc7d942b033ec452c8906c1038ff45545b37f46b95bd
```

Exactly the five scopes opened by `AUTHORIZATION_PROMPT.md` (documentation,
implementation, synthetic_exploration, decoder_execution, development_gate)
are true; every other boolean is false; `attempts_allowed: 1`,
`attempts_used: 0`; `predecessor: TWO_LAYER_RATE_FEASIBILITY_ACCEPTED`.
The state/next_gate strings match the established pre-execute convention
(P5/P6-R1 records use the same next_gate).

### 2. Frozen gate identity — PASS

```text
$ python /tmp/opencode/p4_review/frozen_identity.py
len D1/D2: 45 110
D1 == freeze: True   D2 == freeze: True
D1 == code:   True   D2 == code:   True
constants: 256 0.05 0.2 45 110 96
seeds: 2026091360 2026091361
budget: 3600.0 2147483648 3600 2097152
banned size: 27
```

- `D1 = sorted(analytic_order(0.05,256)[:45])` and
  `D2 = sorted(analytic_order(0.20,256)[:110])` recomputed independently from
  `construction.analytic_order`, and equal both the freeze text and
  `frozen_disclosure_sets()` output element-for-element (45/110 ascending,
  distinct). D1 equals the accepted Phase-5 static K=45 set. D1 ≠ D2[:45] is
  expected: they are different channel points (epsilon1=0.05 vs epsilon2=0.20),
  not a nesting chain.
- 96 paired blocks, N=256, epsilon1=0.05, epsilon2=0.20, run seed
  2026091360, public Toeplitz master 2026091361, 2 GiB (2097152 KiB /
  `RSS_LIMIT_BYTES=2147483648`), 3600 s internal and external.
- `git grep -n 2026091360 HEAD` → exit 1 (no matches); same for 2026091361.
- Exact command parses with `build_parser().parse_args([...])`; all nine flags
  required, no production default (`two_layer.py:1679-1693`).
- Root
  `.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/`
  is ABSENT (`ls` exit 2; re-verified at end of review).

### 3. Core semantics, taxonomy, accounting — PASS

Code review (file:line) + targeted spies:

- P1 is Bob-only, `PRIOR_ONLY`, no truth input: `build_p1_metrics(bob[None,:], p1_table)`
  (`two_layer.py:640-641`); spy showed the only P1 argument is `bob[None,:]`.
- L1 SC returns the source-domain hard candidate: one `_decode_layer` call
  (`:655`), `op_high_hat = sc1.x_hat` (`:656`); `sc.py:234` defines
  `x_hat = polar_transform(u_hat)` — the re-encoded source word.
- `P2_hat` is built ONLY from Bob + that candidate, `CANDIDATE_CONDITIONED`
  (`:665-669`). Forced-wrong-candidate spy (documented seam) showed the
  operational gather receives the override, never truth; the oracle gather
  receives `high_arr` (`:738-739`, `ORACLE_CONDITIONED`).
- Both L2 calls are fresh `sc_decode` calls on from-scratch metrics, no
  state/APP/belief transfer: spy over one block recorded exactly 3 decodes
  (L1, op L2, oracle L2), no shared memory between the three `logp` inputs,
  and each L2 input bitwise equals `probs_to_symbol_metric(fresh gather).logp`
  (`:675`, `:751`).
- Final label `low_hat + 32*high_hat` (`:677`) and per arm exactly one final
  verification event after the label, using the per-arm/per-block SHA-256
  counter-stream seed (`:679-683`, `:755-759`). Both tag evaluations for one
  arm share one 2623-bit seed; this is the accepted `shared`/`protocol.py:361-362`
  convention (one tag event per arm). The frozen runner passes none of the
  injection seams (`tag_fn=`, `l1_candidate_override=`, `tag_override=` absent
  in `run_two_layer_dev_gate`; inspected call site `:1575-1589`).
- No truth/oracle/APP input in the operational metric/args/tag: operational
  decode args are `d1`/`d2` (public frozen sets) and the Alice disclosure
  values only; the tag input is `labels_to_bits(op_label_hat)` with a
  truth-free seed. APP/soft/belief tokens occur only in comments/plan strings.
- Taxonomy `exact > undetected > verify_failed > decode_failed > resource_abort`
  with the documented precedence (`:693-704`, `:766-773`); per-layer
  sub-buckets partition executed arms. Independent smoke recount:
  `l1_ok+l1_fail = 6`, `l2_inv+l2_skip = 6`, `tag_inv = tag outcomes = 6`,
  all arms' outcome sums = 3 = blocks.
- Accounting `5*(K1+K2)+64 = 839` per fully invoked arm: independent literal
  recount from the smoke's per-block JSON (not the module's recount helper)
  gave per-arm `kdb=2517, pcb=7869, tags=3` for 3 blocks (= 839/2623/1 per
  block) and totals `5034 / 15738 / 6`, exactly equal to
  `transcript_accounting.json` incremental and recount fields;
  `mismatch_count = 0`; `transcript_sha256` present (64 hex).

### 4. Operator-flagged items — PASS (with consequences)

**(a) Frozen-model P2 layer-independence.** Independently measured on the
frozen injected table:

```text
max |P2[u1,b,:] - Pl[b_low,:]| (literal generative model): 8.8818e-16
max_b |P2[u1=0,b,:] - P2[u1=1,b,:]|: 7.771561172376096e-16   (operator 7.77e-16 confirmed)
max over all u1 pairs:               7.771561172376096e-16
sampled rows not bitwise equal to u1=0: 58/868
column-sum deviation: 9.5479e-15 <= 1e-12
```

Adjudication: the frozen layer-erasure model makes the table-derived P2 rows
mathematically equal to `Pl[b_low,:]`; the operational and oracle L2 metrics
therefore carry (up to float64 rounding) the same information about `low`.
**No hard gate is invalidated.** `exact` and `oracle_candidate_divergence` are
report-only in the packet, and the 13 gated checks are wiring/provenance/
isolation/accounting/taxonomy/budget/transcript plus the decoder-free pre-run
propagation test, none of which depends on a metric-level L1→L2 dependency.
The label-level propagation is still real: `label = low_hat + 32*high_hat`, so
a wrong L1 changes the five high bits (verified by forced wrong candidate:
`label_hat != labels_true`, `label_hat == low_hat + 32*wrong`). The pre-run
injected check uses a hand-built layer-dependent table and passes with
`metric_max_abs_diff = 0.6`, so the seam is proven where dependence exists.
**Consequence for the main thread:** the frozen run's
`oracle_candidate_divergence`/`exact` numbers must be described as an
index-change/float-noise signal and label-level propagation, NOT as
metric-level L1→L2 dependence; the gate's claim is exactly the packet's
"interface gate" scope. Record this in the Pre-RESULT acceptance text.

**(b) Seed overlap 2026091360/2026091361 with P6-R1 TEST-LOCAL seeds.**
Verified:

```text
$ git grep -n 2026091360 HEAD / 2026091361 HEAD  -> exit 1
BANNED size 27 == {1200..1213, 1314..1321, 1330, 1340, 1341, 1350, 1351}
all 27 refused by both validate_run_seed and validate_toeplitz_master
frozen 2026091360/2026091361 accepted by both
$ grep -rn 2026091360|2026091361 .workbuddy/queue/**  (json/md/yaml)
  only: R1_FREEZE.md §6 and R1 PRE_EXECUTE_REVIEW.md, both stating
  "R1 tests use 2026091360..1363" (test-local)
test_nbpolar_incremental_r1.py:56-57 TEST_SEED_A/B = 2026091360/2026091361
R1 accepted evidence root three_arm_paired_dev_gate uses run_seed 2026091350
```

Adjudication: acceptable. 1360/1361 were never consumed official streams
(the consumed set is the 27, cross-checked against `protocol.py:73-77`,
`incremental.py:139-160` and the R1 accepted evidence root which used
1350/1351); no accepted evidence artifact's numbers depend on them; the P4
Toeplitz namespace `nbpolar-p4-toeplitz-seed` is distinct from the P6 prefix,
so even the tag streams cannot collide. The only reuse is the raw
`default_rng` stream in deterministic, non-evidence R1 unit tests; the P4 gate
makes no statistical claim (interface gate, exact/divergence report-only), so
this cannot bias any gated boolean. No evidence entanglement found.

### 5. Pre-run propagation + tiny oracles — PASS

- `injected_wrong_l1_propagation_check()`: `passed=true`,
  `decoder_calls=0`, `metric_divergent=true`, `label_divergent=true`,
  `metric_max_abs_diff=0.6` — the decoder-free check that the gate itself runs
  before any SC call (`two_layer.py:1545-1547`).
- N=2/4 exhaustive checks (independent rerun, Phase-2 tolerances):
  `N=2: max prob diff 4.441e-16 <=1e-12; max finite log diff 1.776e-15 <=1e-9`;
  `N=4: 4.441e-16 <=1e-12; 3.553e-15 <=1e-9`, over P1, P2_hat and P2_true for
  every coordinate against the literal/vectorized oracle.
- Focused tests `test_p4_a07` (:400) and `test_p4_a08` (:430) pass
  (`3 passed` for `-k "a06 or a07 or a08"`).

### 6. Truth isolation — PASS

- Sentinel code `two_layer.py:424-437`, applied at `:808-819` over the
  operational P1 metric, operational P2/decisions, oracle P2/decisions and both
  disclosed-value maps, with in-place truth mutation afterwards; violations are
  counted and gated (`operational_truth_leak_zero`).
- `test_p4_a06` (:371) passes: sentinel returns False for an aliased truth
  buffer and True for a copy; a real block reports
  `truth_leak_violation=False` for both arms; results are bitwise stable across
  repeated identical calls and unchanged by post-call caller mutation.
- Code inspection: no truth path into the operational metric/decoder/tag
  (item 3); `validate_symbols` returns a copy (`algebra.py:45-73`), so caller
  arrays are never mutated by the sentinel.

### 7. Bounded re-measurement (non-frozen seeds, temp root, NOT the gate) — PASS

```text
$ python /tmp/opencode/p4_review/smoke.py
seeds 2026091380/2026091381, n=256, k1=45, k2=110, blocks=3,
out=/tmp/opencode/p4_review/p4_smoke_gate
files: [aggregate_summary.json, frozen_plan.json, per_block_two_layer_outcomes.json, report.md, transcript_accounting.json]
13 gates all pass: True (count 13)   candidate: TWO_LAYER_OPERATIONAL_SC_CANDIDATE
independent literal recount == transcript_accounting.json: True; mismatch_count 0
block_wall_s: [0.109339, 0.107724, 0.116126]; mean 111.1 ms
projected 96-block wall: 10.66 s  (~337x under the 3600 s budget)
```

- Exactly five files, per-block and arm record keys exactly the freeze §13
  schema; no `hex`/`high_hat`/`label_hat`/disclosed-value/raw-seed fields
  (only public `arm_labels` and the frozen public D1/D2/refused-seed lists).
- Resource envelope tested with the real command constraint:
  `bash -c 'ulimit -v 2097152; python ...'` completed; VmHWM = 138988 KiB
  (135.7 MiB) and `ru_maxrss` = 135.7 MiB. One earlier unconstrained smoke
  showed the known intermittent WSL2 `ru_maxrss` inflation (~1.26 GiB) that the
  operator documented; VmHWM in the constrained run is authoritative and the
  2 GiB envelope has ~15x margin.

### 8. Tests — PASS

```text
TMPDIR=<fresh> python -m pytest comparison_bench/tests/test_nbpolar_two_layer.py -q -p no:cacheprovider
  12 passed
TMPDIR=<fresh> python -m pytest comparison_bench/tests/test_nbpolar_*.py -q -p no:cacheprovider
  192 passed in 106.67s
```

Coverage inspection: P4-A01 :203, A02 :227, A03 :261, A04 :288, A05 :325,
A06 :371, A07 :400, A08 :430, A09 :454, failure taxonomy :514, A11 :608,
forbidden markers/import-time I/O :710. Refusal paths (existing root,
banned seed, `n > 256`, CLI exit 2) at :651-682; the import-time subprocess
check runs in a fresh cwd and asserts no file is created (:726-744). Test
seeds are 2026091364..2026091369 (:59-64); the suite asserts no
`default_rng(FROZEN_*)` and never references the real queue root (:720-724).
The frozen literals appear only in the parser-identity argv (:636-648, parse
only) and in one refusal-path `tl.main` call (:674-681, refused on the banned
run seed before any seed use) — non-consuming.

### 9. Scope and premises — PASS

- `git status --porcelain`: 44 entries (the P4 queue dir was already untracked
  as a whole, so this review adds no new entry); the 13 pre-existing modified
  files other than `tasks.md` all have mtime <= 12:33, before the P4 session
  started (~12:46); `tasks.md` is pre-existing dirty and carries the in-scope
  P4 section (13:08). The P4-session files are only `two_layer.py` (12:59),
  `test_nbpolar_two_layer.py` (13:06), the queue freeze/notes/STATUS
  (12:46-13:08) and the OpenSpec P4 delta spec + tasks section (13:08).
  Pre-existing dirty files (P3 queue, `__init__.py`, empirical modules,
  P5/P6 modules/tests, docs) unchanged by mtime.
- Accepted predecessors untouched: `prior.py`, `sc.py`, `transform.py`,
  `construction.py`, `algebra.py`, `formal_ir/shared.py` are not in
  `git status` (tracked clean). `nbpolar/__init__.py` has no `two_layer`
  re-export.
- No writes to `results/` or `comparison_bench/outputs_comparison/`
  (`git status --porcelain -- <paths>` empty); accepted evidence roots show
  newest file mtimes <= 11:09 (before the P4 session); no sibling writes.
- No Model-F/artifact/real-data path: `two_layer.py` imports only stdlib,
  numpy, the accepted nbpolar modules and `formal_ir/shared.py`; raw marker
  grep for `outputs_comparison`, `model_f`, `v72p2d5`, `parquet`, `ttbin`,
  `fwht`, `scl/crc`, `app_fed`, `app_prior`, `get_l1_app`, `pandas`,
  `pyarrow`, `scipy` = 0 each; no file-read primitive (`open(`,
  `read_text`, `np.load`, `json.load`, ...) anywhere in the module.
- HEAD unchanged (`ab173f2a`), nothing staged, no commit/push; gate root
  ABSENT at end of review; `STATUS.yaml` sha256 unchanged from §1.

---

## 2. Complete frozen record (as verified)

- **Model**: GF32 polynomial basis, primitive polynomial 37, alpha 2,
  natural-order transform; `A = 32*high + low`, `high/low` iid uniform GF32;
  independent layer-erasure observation `B_high = high` w.p. 1-eps1 else
  uniform, `B_low = low` w.p. 1-eps2 else uniform, `B = 32*B_high + B_low`;
  explicit `[Alice,Bob]` (1024,1024) table
  `f[a,b] = Ph(b_h|a_h)*Pl(b_l|a_l)`, columns sum to 1 within 9.55e-15;
  table-derived `P1[u1,b] = Ph(b_h|u1)`, `P2[u1,b,u2] = Pl(b_l|u2)` (layer-
  independent up to 8.88e-16); per-block RNG order `high`, `low`, `B_high`
  observation, `B_low` observation.
- **Point**: q=32, n=256, epsilon1=0.05, epsilon2=0.20, k1=45, k2=110,
  96 paired blocks.
- **D1** (45): `[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,17,18,19,20,21,22,24,
  25,26,32,33,34,35,36,40,48,64,65,66,68,72,80,96,128,129,130,132,136,144]`
- **D2** (110): `[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,
  22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,
  46,48,49,50,51,52,53,54,56,57,58,60,64,65,66,67,68,69,70,71,72,73,74,75,
  76,77,78,80,81,82,83,84,88,96,97,98,100,104,112,128,129,130,131,132,133,
  134,135,136,137,138,140,144,145,146,148,152,160,161,162,164,168,192,193,
  194]` (full list equal to freeze §4; verified element-for-element)
- **Seeds**: run 2026091360; public Toeplitz master 2026091361; 27 refused
  consumed seeds `{2026091200..2026091213, 2026091314..2026091321,
  2026091330, 2026091340, 2026091341, 2026091350, 2026091351}`; per-arm/
  per-block stream `SHA-256("nbpolar-p4-toeplitz-seed:<master>:<arm>:<index>:
  <counter>")`, MSB-first, 2623 bits; arms `operational`, `oracle`.
- **Exact command** (recorded only, NOT executed):
  `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar; ulimit -v 2097152;
  timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m
  comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer
  --n 256 --epsilon1 0.05 --epsilon2 0.20 --k1 45 --k2 110 --blocks 96
  --seed 2026091360 --toeplitz-master 2026091361 --out-dir
  .workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate`
- **Output root**: ABSENT (verified before and after review). After success
  exactly five files: `frozen_plan.json`, `per_block_two_layer_outcomes.json`,
  `transcript_accounting.json`, `aggregate_summary.json`, `report.md`
  (scalar-only; schema keys verified against freeze §13 in the smoke).
- **Budgets**: internal total wall 3600 s (remaining blocks become
  `resource_abort`, five files still written), external `timeout 3600`,
  `ulimit -v 2097152` (2 GiB), `rss_bytes_max = 2147483648`; measured
  ~111 ms/block → projected ~10.7 s (337x margin), ~136 MiB peak RSS.
- **Taxonomy**: `exact | undetected | verify_failed | decode_failed |
  resource_abort` per arm, disjoint/exhaustive; per-layer sub-buckets
  `l1_executed/l1_decode_failed`, `l2_invoked/l2_skipped_by_l1_failure/
  l2_decode_failed`, `tag_invoked` partition executed arms; both arms' L2
  invoked for every L1 candidate.
- **Accounting**: 225 L1 + 550 L2 + 64 tag = 839 key-dependent bits per fully
  invoked arm per block; 2623 public control bits per tag invocation; one
  independent literal recount with zero mismatch.
- **13 hard gates** (all persisted, all true in the smoke): paired coverage;
  both-arms-L2-for-L1-candidates; P1 PRIOR_ONLY; candidate
  CANDIDATE_CONDITIONED; oracle ORACLE_CONDITIONED; operational truth-leak
  zero; undetected zero; nonfinite zero; resource-abort zero; buckets
  disjoint/exhaustive; disclosures exact; transcript recount mismatch zero;
  pre-run injected wrong-L1 propagation passed. `exact` and
  `oracle_candidate_divergence` report-only, no threshold.

## 3. Findings (file:line)

Blocking: **none**.

Non-blocking:

- **NB-1 (docs consistency).** The OpenSpec change task list
  `openspec/changes/formal-ir-nbpolar-phase4-p4-two-layer-operational-sc/tasks.md`
  reuses IDs `P4-A01..A11` with different meanings than the packet acceptance
  IDs `P4-A01..A12` (e.g. change A09 = "freeze the gate" vs packet A09 =
  "buckets/recount"). The implementation/freeze/tests follow the packet IDs.
  Main thread should reconcile or mark the change task list as the
  planner-side checklist at acceptance (documentation-only).
- **NB-2 (test seed literals).** `test_nbpolar_two_layer.py:636-648` parses
  the exact frozen argv and `:674-681` passes `--toeplitz-master 2026091361`
  to one refusal-path `main` call (banned run seed 2026091351). Verified
  non-consuming (parse only; refusal precedes any seed use); recorded for
  transparency since freeze §17.6 asks for zero frozen-seed test use.
- **NB-3 (claim wording).** See §4(a): the main thread must phrase the
  frozen-run divergence/exact results as label-level propagation/wiring
  evidence only, not metric-level L1→L2 dependence.
- **NB-4 (RSS measurement).** WSL2 can inflate `ru_maxrss` (1.26 GiB observed
  once; VmHWM/RSS 135.7 MiB in the constrained run). If the frozen
  `aggregate_summary.json.rss_bytes_peak` looks anomalous, Pre-RESULT should
  cite VmHWM; no gate depends on it.
- **NB-5 (docs update).** `docs/decision-log.md` and `CURRENT_TASK.md`
  (mtime 12:33, main-thread) still describe P4 as frozen-pending-
  authorization; the main thread owns the post-gate/acceptance docs update.
  `docs/troubleshooting.md` needs no change.
- **NB-6 (record clarity).** For the oracle arm the persisted
  `l1_executed=True`/`l1_decode_failed=False` denote the shared block L1
  stage / true-L1 availability, not an oracle-arm L1 SC call
  (`two_layer.py:785-788`); consistent with the freeze per-arm convention,
  worth one clarifying sentence in the Pre-RESULT report if questioned.
- **NB-7 (budget symmetry).** Internal total wall equals the external
  `timeout 3600`; unreachable at the projected ~10.7 s (337x margin). Kept
  byte-faithful to the packet command; no change recommended.

## 4. Closure statements

- Real frozen 96-block command: **NOT executed** by this review; no gate SC
  call was made; the single gate attempt is unconsumed (`attempts_used: 0`).
- Only writes by this review: this file and `/tmp/opencode/p4_review/` scratch
  (verified `git status --porcelain` set unchanged, 44 entries, nothing
  staged).
- Gate root: **ABSENT** immediately after this review.
- HEAD: `ab173f2a5e17336383a897b941080b731ba3dd9e`, unchanged; no commit/push.

**Verdict: PASS — cleared for the single authorized execution, subject to the
main thread's authorization and the exact frozen command/root absence.**
