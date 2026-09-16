# Pre-RESULT review — NBPOLAR-PHASE5-STATIC-PROTOCOL

**Verdict: PASS_WITH_COMMENTS**

- Reviewer: fresh independent reviewer-go (backup instance), read-only. Did not
  write the code, freeze the plan, or run the development gate.
- Date: 2026-09-13. Repository: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- Pinned interpreter for every check: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
  (Python 3.12.3, numpy 2.5.3), as frozen in `P5_FREEZE.md` §2.
- Contract adjudicated: `P5_FREEZE.md` Rev 1 (schema §6, seeds §4, gates §7,
  Wilson §7, budget §5), `TASK_PACKET.md`, rulings R1/R2. The three operator
  observations were adjudicated against the freeze doc, not against prompt
  wording.

## Independence statement

- The frozen 300-block command was **NOT rerun** — attempt 1/1 was consumed by
  the reviewed run at its first scientific `sc_decode` call. No scientific
  decoder call was made by this review; only bounded recomputation scripts over
  the five persisted files and read-only code inspection.
- No real-data, artifact, DEV/EVAL, parquet, TTBin or sibling-execution access.
  No commit, no push, no file edit except this review document.
- The reviewed run wrote exactly the 5 frozen files to
  `.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate/`;
  all file mtimes are 2026-09-13 02:31:13.43–.46 (+0800), a single generation.

## 0. Artifact inventory, schema and private-content check

- Output root contains **exactly 5 files** (incl. hidden scan; `find -mindepth 1`
  count = 5): `frozen_plan.json`, `per_block_outcomes.json`,
  `transcript_accounting.json`, `aggregate_summary.json`, `report.md`.
- `frozen_plan.json` top-level keys (19) = `attempt_consumption_point, budget,
  channel, created_utc, disclosure_coordinates, disclosure_rule, epsilon, field,
  k, label_domain, mode, n, outcome_precedence, planned_blocks, protocol, q,
  repository, run_seed, toeplitz` — exactly the freeze §6.1 list; nothing more.
- `per_block_outcomes.json` = `{n_blocks: 300, blocks: [300 records]}`; every
  record has exactly the 11 freeze §6.2 scalar keys (`block_index, outcome,
  exact, verification_invoked, key_dependent_bits, public_control_bits,
  nonfinite, truth_leak_violation, error_type, metric_wall_s, decode_wall_s`),
  `block_index` sequence 0..299, no list/dict/array values (non-scalar count 0).
- `transcript_accounting.json` keys = `event_count, incremental{key_dependent_bits,
  public_control_bits, verification_invocations}, recount{...}, mismatch_count,
  transcript_sha256` (freeze §6.3).
- `aggregate_summary.json` carries every freeze §6.4 item: `outcome_totals`,
  `attempted`, `coverage`, `verified`, `verification_invocations`, `undetected`,
  key-dependent/public totals, average, `transcript{}`, `truth_leak_count`,
  `nonfinite_count`, `decode_error_types`, `wilson{}`, `hard_gates{}`,
  `candidate`, `claim_scope`, `wall_s`, `rss_bytes_peak`, `resource_stop_fired`.
- No private/raw content: raw-text scan of all four JSONs for `u_hat`, `x_hat`,
  `labels`, `seed`, `symbol`, `payload` → all absent; long-token scan (≥40 chars)
  finds only the public `transcript_sha256` digest and the key name
  `average_key_dependent_bits_per_attempted_block`. The only coordinates listed
  are the 45 public disclosure coordinates (allowed by freeze §6).

## 1. Outcome totals recomputed from `per_block_outcomes.json`

Method: `Counter(r["outcome"])` over the 300 records (not `aggregate_summary.json`).

| bucket | recomputed | persisted `outcome_totals` |
|---|---|---|
| exact | 300 | 300 |
| undetected | 0 | 0 |
| verify_failed | 0 | 0 |
| decode_failed | 0 | 0 |
| resource_abort | 0 | 0 |

- Disjoint/exhaustive: sum = **300** == planned 300. Histogram identical.
- `attempted` = 300 − 0 = **300** (coverage 1.0).
- `exact` boolean agrees with `outcome == "exact"` for all 300 records
  (mismatches 0).
- `undetected == 0` is persisted as its own key/bucket row and is **not folded**
  into `exact`: `outcome_totals.undetected = 0`, `aggregate_summary.undetected = 0`,
  and `wilson.successes = exact = 300`; the `verified` union (exact+undetected)
  is reported separately as 300.

## 2. Per-block disclosure recomputation

For every block (K=45, TAG=64, seed_bits=2623):

- `key_dependent_bits == 5*45 + (64 if verification_invoked else 0)` → violations
  **0/300**.
- `public_control_bits == 2623 iff verification_invoked` → violations **0/300**.
- `verification_invoked == (outcome in {exact, undetected, verify_failed})` →
  violations **0/300**.
- Totals recomputed: key-dependent **86700**, public control **786900**,
  verification invocations **300**; persisted aggregate totals identical; each
  verification unit = 225 + 64 = 289 bits; `per_verification_key_dependent_bits`
  = 289 and `average_key_dependent_bits_per_attempted_block` = 289.0.

## 3. Transcript accounting and verification universe

- All events were **reconstructed independently** from the per-block records
  using the frozen event construction (disclosure event 225 bits +
  verification event 64/2623 bits when invoked), then canonicalized with the
  accepted `shared.canonical_event`.
  - events = **600**; key-dependent **86700**; public control **786900**;
    verification events **300**.
  - reconstructed `transcript_sha256` =
    `767418d2670fb1f7e36d71a23ab1afb4593ec6164aef62bce5d97f5b7903b048` =
    persisted value (match).
- `transcript_accounting.json`: `incremental == recount == {86700, 786900, 300}`,
  `mismatch_count = 0`; `aggregate_summary.transcript` identical to the file.
- Verification-invocation universe: `exact + undetected + verify_failed =
  300 + 0 + 0 = 300` == transcript `verification_invocations` = 300 (and ==
  per-record `verification_invoked` count). Consistent.

## 4. Wilson bound and thresholds (independent high-precision recomputation)

- 60-digit `Decimal` reimplementation of the frozen formula
  (`z = 1.6448536269514722`, `s/n = 300/300`):
  `lower = 0.991062127824871822324879296687674970823589242668490623429486`.
- Persisted `wilson.lower_bound = 0.9910621278248719`; absolute difference
  **7.8e-17** (double rounding only). `z`, `successes=300`, `denominator=300`
  match. `lower ≥ 0.90` holds independently.
- Average key-dependent disclosure recomputed = **289.0 bits** < `10*N = 2560`;
  `verification_invocations` 300 (< 300×2^64 union bound irrelevant here, no
  over-claim).
- Envelope: `wall_s = 4.998916 < 300`; `rss_bytes_peak = 111190016 < 2147483648`;
  max (metric+decode) per-block wall = 0.021691 s < 5.0 s soft cap;
  `resource_stop_fired = false`.

## 5. Truth isolation, nonfinite, coverage and all 11 gates recomputed

Code inspection (frozen implementation identity):

- `sc_decode` receives only `(logp, field, alpha, known_positions=D,
  known_values=U[D])` (`protocol.py:312-319`); Alice truth `x`/`u_truth` never
  enters the decoder arguments.
- Adapter metric is built from `bob_symbols` only
  (`nbpolar_static.py:67-74`); Alice truth never enters the metric.
- Bob's tag input is `labels_hat_bits` (reconstructed labels) plus the public
  per-block seed (`protocol.py:360-363`); the Alice-side tag over
  `labels_true_bits` is the verification reference and the pass/fail result
  never selects, retries or modifies a decoder path (single `sc_decode` call
  before the tag).
- Adversarial post-decision truth-mutation sentinel (`protocol.py:192-207,
  350-358`): all 300 records `truth_leak_violation = false`,
  `truth_leak_count = 0`.

Artifact counts: `nonfinite_count = 0`, `resource_stop_fired = false`,
`coverage = 1.0`.

Each of the 11 freeze §7 gates was independently recomputed from the per-block
records and the reconstructed transcript; the resulting map is **identical** to
persisted `hard_gates`:

1. `outcome_accounting_disjoint_exhaustive` — true (Σ = 300).
2. `coverage_complete` — true (attempted = 300).
3. `resource_stop_preregistered` — true (0 aborts).
4. `per_block_disclosure_consistent` — true (0/300 violations).
5. `verification_universe_consistent` — true (300 = 300 = 300).
6. `recount_zero_mismatch` — true (0, incremental == recount).
7. `undetected_zero` — true (0).
8. `truth_leak_zero` — true (0).
9. `nonfinite_zero` — true (0).
10. `wilson_lower_ge_0_90` — true (0.99106… ≥ 0.90).
11. `avg_key_dependent_below_input_bits` — true (289 < 2560).

All true → `candidate = STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE` independently
reproduces.

## 6. `frozen_plan.json` identity

- `run_seed = 2026091317` = `FROZEN_RUN_SEED`; `protocol`, `mode`, `q=32`,
  `n=256`, `k=45`, `epsilon=0.05` match freeze §3.
- `disclosure_coordinates` (45, sorted) == `sorted(analytic_order(0.05,256)[:45])`
  recomputed from the accepted construction; worst-first slice equals
  `P5_FREEZE.md:57-59`; comma-joined SHA-256 =
  `22e7f2a94a115bf68a56ede47b863a0c1761da4a2fbb9483dd4d961a51b5b371`.
- `toeplitz`: master **2026091318**, `seed_bits = 2623`, `tag_bits = 64`,
  derivation string matches freeze §4; independent reimplementation of the
  SHA-256 counter-mode rule matched `block_toeplitz_seed_bits(i)` bit-for-bit
  for i = 0, 1, 299 (2623/2623 bits each); seed contents are never persisted.
- `label_domain`: `packing = label_j = 32 * x_hat_j`, `bits_per_label = 10`,
  `message_bits = 2560`, low-half-zero flag true (freeze R2).
- `budget = {total_wall_s: 300.0, per_block_soft_cap_s: 5.0,
  rss_bytes_max: 2147483648}` == freeze §5.
- `outcome_precedence` order = `resource_abort > decode_failed > verify_failed >
  exact > undetected` (freeze §3), with the §6 semantics text.
- `attempt_consumption_point = "first scientific sc_decode call"` (freeze §8).

## 7. Bounded wording (`report.md`, read in full)

- Scope line present: "synthetic development signal only; this is not real-data
  FER, leakage efficiency, key rate, qualification or promotion evidence."
- No real-data FER, leakage-efficiency, key-rate, qualification or promotion
  claim anywhere; the only "accepted" word is the accepted predecessor analytic
  order in `disclosure_rule`.
- Candidate label is explicitly the development candidate; `undetected` is a
  separate bucket row (0) and the "verified union (exact + undetected): 300"
  line plus separate `aggregate_summary.undetected` key keep it isolated; the
  Wilson line is labeled "(exact recovery)" with successes = exact. No
  over-claim flagged.

## 8. Implementation state (P5-A01–A12 "remain true")

Commands (pinned interpreter, fresh `/tmp/opencode` basetemps, cache disabled):

```bash
V=/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python
BT1=$(mktemp -d /tmp/opencode/p5_pr_focused_XXXX)
BT2=$(mktemp -d /tmp/opencode/p5_pr_full_XXXX)
$V -m pytest -q -p no:cacheprovider --basetemp="$BT1" comparison_bench/tests/test_nbpolar_protocol.py
$V -m pytest -q -p no:cacheprovider --basetemp="$BT2" comparison_bench/tests/test_nbpolar_*.py
```

- Focused: **16 passed**, 1 warning in 4.02 s.
- Full: **136 passed** (16 new + 120 predecessor), 1 warning in 62.69 s.
- Frozen run seed usage: `2026091317` appears in the test file only in
  `assert proto.validate_run_seed(2026091317) == 2026091317` (CLI usability);
  RNG/decoder seeds are `TEST_SEED=2026091319`, `TEST_SEED_B=2026091320`,
  `TEST_SEED_C=2026091330`. No test generates blocks or calls the decoder with
  the frozen run seed.

## 9. Scope and provenance

- `git status --porcelain`: declared P5 paths only — new
  `formal_ir/nbpolar/protocol.py`, `methods/nbpolar_static.py`,
  `tests/test_nbpolar_protocol.py`, `openspec/changes/formal-ir-nbpolar-phase5-static-protocol/`,
  the P5 queue dir (incl. output root); modified tracked file is only
  `formal_ir/nbpolar/__init__.py` (protocol import block + `__all__` names,
  +50 lines).
- P3/P4 dirty files unchanged: their mtimes are ≤ 2026-09-13 01:33:18, before
  the P5 implementation window (01:46–02:14) and the run (02:31:13); none has a
  P5 fingerprint.
- `results/` and `comparison_bench/outputs_comparison/`: no entry newer than
  02:25; frozen `src/`, `experiments/`, `tools/` show no modifications.
- Sibling checkout `../HD-QKD_Polar_Comparison`: 0 files matching P5
  fingerprints (`static_protocol_dev_gate`, `STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE`,
  `nbpolar_static`, `2026091317`) in its `.workbuddy`, `comparison_bench/src`,
  `tests`, `docs`, `openspec`; its untracked items are 2026-09-11 history. Used
  only as the pinned interpreter.
- HEAD unchanged: `ab173f2a5e17336383a897b941080b731ba3dd9e`; `git diff --cached`
  empty; reflog shows only the original clone (no commit). Output root mtimes
  single generation.

## Adjudication of the three operator observations

**(a) `frozen_plan.json` has no `command` and no `attempts_used` key — NOT a defect.**
Freeze §6.1 defines the exact `frozen_plan.json` schema list, which contains
neither key; the persisted 19 top-level keys equal that list exactly. The exact
command lives in `P5_FREEZE.md` §8 and the authorization record; the attempt
state lives in `STATUS.yaml`. No artifact change required.

**(b) `STATUS.yaml` still says `attempts_used: 0` — closeout-owned correction required.**
Freeze lines 8–10: the attempt is "consumed at the first scientific `sc_decode`
call of the frozen command", so after this 300-block run the durable state must
no longer be 0. This is not a defect in the five reviewed artifacts (they carry
`attempt_consumption_point` by design and never persist attempt state), but the
successor docs/closeout step **must set `attempts_used: 1`** (and advance
`next_gate`) before the packet is recorded as closed. It does not invalidate the
run evidence and does not block solidification.

**(c) No literal `hard_gates_pass` key; `hard_gates{}` has 11 booleans all true — NOT a defect.**
Freeze §7 requires each gate to be "persisted as a boolean in `hard_gates`" and
§6.4 lists `hard_gates{}`; the candidate rule is `all(gates.values())` →
`candidate` label. No single `hard_gates_pass` key exists anywhere in the frozen
contract. Compliant.

## Findings

**Blocking issues: none.**

Non-blocking / closeout items:

- **R-1 (required closeout correction).** Update
  `.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/STATUS.yaml`
  `attempts_used: 0 → 1` in the successor docs step; the attempt was consumed
  by the reviewed run.
- **R-2 (cosmetic, no action required).** `report.md` states the five buckets as
  disjoint rows and the verified union but does not restate in prose that
  `undetected` is never success. With `undetected = 0` and the explicit
  separate keys the isolation is unambiguous; no over-claim.
- **R-3 (optional).** The exact command is not persisted inside
  `frozen_plan.json`; the freeze does not require it (§6.1, §8). No action.

## Checklist

- [x] Matches OpenSpec spec / freeze contract (schema §6, seeds §4, budget §5,
  gates §7, R1/R2)
- [x] Tests pass (16 focused + 136 full = 16 new + 120 predecessor)
- [x] No scope creep (only declared P5 paths; frozen dirs, results,
  outputs_comparison, sibling untouched; no commit/push)
- [x] No private/raw content persisted; five files only, scalar records only
- [x] All outcome/disclosure/Wilson/gate numbers independently recomputed and
  matching
- [x] `undetected` isolated; truth isolation holds; bounded wording verified
- [ ] `docs/decision-log.md` / `docs/troubleshooting.md` updates: successor
  closeout-owned (not part of this review's write scope)
- [ ] `STATUS.yaml attempts_used: 1` closeout correction (R-1)

**Independence:** the frozen dev-gate command was not rerun (attempt 1/1
consumed); this review is read-only and made no scientific decoder call.
