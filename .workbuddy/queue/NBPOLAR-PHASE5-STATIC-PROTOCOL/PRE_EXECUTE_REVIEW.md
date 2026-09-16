# PRE-EXECUTE review — NBPOLAR-PHASE5-STATIC-PROTOCOL

**Verdict: PASS**

- Reviewer: independent reviewer-go (backup instance); read-only on the
  implementation, did not author any file under review.
- Date: 2026-09-13. Repository: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- Interpreter for every check below:
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
  (Python 3.12.3, numpy 2.5.3), as frozen in `P5_FREEZE.md` §2.
- Contract reviewed: `TASK_PACKET.md`, `STATUS.yaml`, `P5_FREEZE.md` (Rev 1,
  2026-09-13), `P5_IMPLEMENTATION_NOTES.md`, `openspec/changes/
  formal-ir-nbpolar-phase5-static-protocol/` (proposal/design/tasks/spec +
  R1/R2 Rev note), `docs/nbpolar/ARCHITECTURE.md`, user authorization text,
  and main-thread rulings R1/R2.
- **The frozen 300-block command was NOT executed.** Only bounded synthetic
  runs (16 blocks N=256, 3 blocks, tiny 2/4-block cases) with non-frozen seeds
  and `/tmp`-only output roots were run for budget/schema verification.

## 0. Complete frozen record (independently verified)

| item | frozen value | independent verification |
|---|---|---|
| run seed | **2026091317** | `git grep -c 2026091317 HEAD -- .` → **no output, exit 1 (empty)**. Working tree: only P5 docs/code mention it (`P5_FREEZE.md:92,219,256`, `P5_IMPLEMENTATION_NOTES.md:15,116`, `protocol.py:69,71`, `test_nbpolar_protocol.py:5,570`). No Phase 1–4 or D7 code/data use. |
| banned/consumed seeds | 2026091200..2026091213, 2026091314/1315/1316 | `protocol.py:73-77`; six representative refusals confirmed (`2026091200, 2026091207, 2026091213, 2026091314, 2026091315, 2026091316` → `ValueError: run seed … banned`). Range matches P1 (`synthetic.py:26-29`), R1 (`eval_r1.py:35-38`), P3 (`empirical_channel.py:73-75`, `BANNED_SEEDS` line 76). |
| Toeplitz master seed | **2026091318** | `git grep -c 2026091318 HEAD -- .` → **empty**. `protocol.py:72`. |
| per-block seed derivation | concat `SHA-256("nbpolar-p5-toeplitz-seed:2026091318:<block_index>:<counter>")` for counter=0,1,…; MSB-first unpack; truncate to seed length | `protocol.py:157-174`. Manual reimplementation of the rule matched `block_toeplitz_seed_bits(0)` bit-for-bit (2623/2623 bits). Deterministic across calls and across two processes (prefix bits `[0,0,1,1,1,1,0,1,…]`, popcount 1323 both). Independent across blocks: Hamming distance block 0 vs 1 = 1312/2623; block 0 vs 299 = 1339/2623. |
| seed length (public control) | **2560 + 63 = 2623 bits** (`SEED_BITS`, `protocol.py:83-84`) | measured `len(block_toeplitz_seed_bits(0)) == 2623`; tiny-N derivation `10n+63` (N=4 → 103). Message domain 10·256 = 2560 (`LABEL_BITS·DEFAULT_N`). |
| raw seed persistence | none | `frozen_plan.json` `toeplitz{}` = {`derivation`, `master_seed`, `seed_bits` (length only), `tag_bits`}; per-block records have 11 scalar fields, no seed content; transcript `payload` = {`seed_bit_length`}. No per-block seed bytes in any of the five files. |
| D set | `D = sorted(analytic_order(0.05, 256)[:45])` | Independently recomputed the erasure recursion `[2e−e², e²]` from scratch: worst-first slice `[0,1,2,4,8,3,16,5,32,6,9,10,64,17,12,128,18,33,7,20,34,24,11,65,36,66,40,13,129,68,19,14,48,130,72,21,132,80,22,35,136,96,25,144,26]` == `P5_FREEZE.md:57-59` == code result; ascending list == `P5_FREEZE.md:61-63`. `evaluate_blocks` convention matches (`construction.py:187,207`: `order[:k]`). |
| D set digest | — | SHA-256 of the ASCII comma-joined ascending list: `22e7f2a94a115bf68a56ede47b863a0c1761da4a2fbb9483dd4d961a51b5b371`. |
| exact command | below | `P5_FREEZE.md:216-220`; parses exactly (`build_parser()`, `protocol.py:848-857`), no extra flags. |
| output root | `.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate/` | **ABSENT now** (`test -e …` → absent; `find . -name static_protocol_dev_gate` → nothing; no `static_protocol*`/`dev_gate*` under the queue). |
| external timeout | **T = 600 s** | in the frozen command; 2× the internal 300 s total budget so the internal stop writes evidence first. |
| memory envelope | **`ulimit -v 2097152`** (2 GiB virtual); plan `rss_bytes_max = 2147483648` | in the frozen command and `frozen_plan.budget`; `protocol.py:86`. |
| total wall budget | **300 s** (`DEV_GATE_TOTAL_WALL_S`) | `protocol.py:89`; checked before each block (`protocol.py:633`). |
| per-block soft cap | **5.0 s** (`DEV_GATE_PER_BLOCK_SOFT_CAP_S`) | `protocol.py:90`; checked after each completed block (`protocol.py:650`). |
| output schema | exactly 5 files: `frozen_plan.json`, `per_block_outcomes.json`, `transcript_accounting.json`, `aggregate_summary.json`, `report.md` | `run_dev_gate` (`protocol.py:799-845`); tiny gate to `/tmp` wrote exactly these five; per-block records exactly the 11 frozen scalar fields; no vectors/keys/seed material. |
| Wilson | one-sided 95%: `p=s/n; z=1.6448536269514722; lower=(p+z²/2n − z·sqrt(p(1−p)/n + z²/4n²))/(1+z²/n); n=0→0`; denominator `n=attempted` | `protocol.py:177-189`, `532`; high-precision Decimal re-implementation agreed ≤3e-16 for (290,300), (270,300), (45,50), (300,300), (1,3). See non-blocking N-1 for the z last-ulp note. |
| outcome precedence | `resource_abort > decode_failed > verify_failed > exact > undetected`, disjoint/exhaustive over planned blocks | `protocol.py:364-369`, `92`, summary gates `protocol.py:533-549`; `verified = exact+undetected`, `verification_invocations = exact+undetected+verify_failed` (`protocol.py:507-508`). |
| attempt consumption | first scientific `sc_decode` call; stays consumed on failure; no rerun/tuning/seed change; no partial credit | `P5_FREEZE.md:8-10,222-225`; `STATUS.yaml:19 attempts_used: 0`; code order: root refusal → seed validation → block generation → `sc_decode` (`protocol.py:813-821`, `639-643`). |

Frozen command (recorded, not executed):

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.protocol --mode dev-gate --run-seed 2026091317 --blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate
```

Budget independently re-measured (non-frozen seed 2026091319, in-memory, no output files):
16 blocks at N=256/K=45 ran in 0.2978 s total; max per-block (metric+decode)
26.3 ms, median 16.6 ms (freeze profile: median 15.61 ms, max 19.90 ms).
Projected 300 blocks ≈ 5.0 s (median) to ≈ 7.9 s (at the observed max), i.e.
≈ 38–60× margin under the 300 s total cap; max observed block is ≈ 190× under
the 5 s soft cap. Process peak RSS 103.6 MB ≪ 2 GiB. All 16 blocks exact,
recount mismatch 0, `incremental == recount`, key-dependent 289/block.

## 1. STATUS edit exactness — PASS

`.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/STATUS.yaml` contains exactly
the six authorized flags `true`:

`documentation_authorized`, `implementation_authorized`,
`synthetic_exploration_authorized`, `decoder_execution_authorized`,
`development_gate_authorized`, `phase5_authorized`.

All other capability flags remain `false`: `artifact_read_authorized`,
`raw_data_authorized`, `real_data_authorized`, `dev_eval_authorized`,
`rate_adaptation_authorized`, `scl_authorized`, `phase6_authorized`,
`scientific_promotion`. `attempts_allowed: 1`, `attempts_used: 0`.
`state: AUTHORIZED_FOR_AUTONOMOUS_PHASE5_STATIC_PROTOCOL` and
`next_gate: IMPLEMENTATION_AND_SYNTHETIC_QUALIFICATION_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW`
match the authorization scope and the current lifecycle position (implementation
and synthetic qualification complete; this review is the next gate).
The pre-authorization all-`false` baseline is attested by `CURRENT_TASK.md:26`
("已冻结为全 false，等待显式授权") and by the P4 STATUS
(`next_gate: PHASE5_STATIC_PROTOCOL_FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`);
the file is untracked, so no git byte-diff baseline exists. No field
additions/removals beyond the declared schema.

## 2. Freeze items — PASS (each item independently checked)

1. **Seed freshness** — `git grep 2026091317 HEAD` and `git grep 2026091318
   HEAD` are both empty (exit 1). Working-tree occurences are P5-only (see §0).
2. **Per-block Toeplitz derivation** — deterministic, independent per block,
   exactly the documented SHA-256 counter rule; 2623 public bits; master
   constant 2026091318; no raw seed contents persisted (see §0).
3. **Static set D** — recomputed from scratch; identical to
   `analytic_order(0.05,256)[:45]` and to both frozen listings (see §0).
4. **Command, root, timeout, ulimit** — exact command parses unchanged; root
   ABSENT; `timeout 600`; `ulimit -v 2097152` (see §0).
5. **Attempt consumption / no rerun** — recorded in freeze §8 and §1; code
   path order confirmed; `attempts_used` still 0 (see §0 and closure).
6. **Budget from synthetic profile** — independently re-measured sample has
   ≥38× total and ≥190× per-block margin; RSS 103.6 MB (see §0).
7. **Schema, Wilson, precedence** — five files/scalars only; Wilson matches a
   60-digit independent implementation; buckets disjoint/exhaustive;
   `verified` and `verification_invocations` explicitly nested (see §0).
8. **Forbidden-path proof** — `protocol.py` imports only stdlib, numpy, the
   accepted nbpolar modules and `formal_ir/shared.py` (`protocol.py:36-60`);
   adapter imports only accepted modules (`nbpolar_static.py:34-44`). Zero
   occurrences of `outputs_comparison`, `model_f`, `v72p2d5`, `parquet`,
   `ttbin`, `TTBin`, `results/`, `HD-QKD_Polar_Comparison/`, `DEV_SEED`,
   `EVAL_SEED` in either file (the only "artifact" hits are docstring prose
   "no artifact": `protocol.py:30`, `nbpolar_static.py:30`). The only write
   paths are `path.write_text`/`out_path.mkdir` inside `run_dev_gate`
   (`protocol.py:687-688,796,829`); the adapter has no write calls at all. The
   adapter builds its metric from `bob_symbols` only (`nbpolar_static.py:67-74`)
   and never passes Alice truth to the decoder.

## 3. Code review — PASS

- **One SC invocation per block**: single `sc_decode` call in `run_static_block`
  (`protocol.py:312-319`). Instrumented tiny dev-gate (3 blocks): decode calls
  = 3.
- **At most one tag after decode**: tag computed only after a successful
  `sc_decode` (`protocol.py:360-363`); 2 `toeplitz_tag` calls per verification
  (Alice + Bob tags). Instrumented: 6 tag calls for 3 verifications;
  `decode_failed` path invokes none (`protocol.py:322-340`, test A05).
- **Tag cannot select/retry/modify a decoder path**: no data flow from tag to
  decoder; test A06 proves one decoder call under a forced tag mismatch and
  identical `u_hat`/`labels_hat` vs. the unpatched run.
- **Disclosed values are actual GF32 values incl. zero**: `disclosed =
  np.array(u_truth[positions], copy=True)` (`protocol.py:302`); zero never a
  sentinel (test A01).
- **Recovered U re-encodes to `32*x_hat` labels**: `labels_hat =
  labels_from_symbols(x_hat)` (`protocol.py:342-344`), `sc_decode` returns
  `x_hat = polar_transform(u_hat)` (`sc.py:234`); test A03.
- **`decode_failed`/`resource_abort` never merged**: distinct outcome strings
  and buckets (`protocol.py:92,322-340,236-251`); per-block accounting gate
  `per_block_disclosure_consistent` (`protocol.py:518-531`).
- **Independent recount is a separate literal implementation**:
  `recount_transcript` walks the event list literally (`protocol.py:450-464`)
  and does not call `transcript_summary`; test A09 tampers events and detects
  mismatch.
- **Truth-isolation sentinel sound**: metric built from channel observation
  only; SC receives only `known_positions=D, known_values=U[D]`; sentinel
  snapshots metric/decisions, mutates live truth buffers, and requires bitwise
  equality (`protocol.py:192-207,350-358`). Positive and adversarial cases
  tested (A04).
- **Refusals**: existing root refused before any decoder call
  (`protocol.py:813-815`); instrumented → 0 decoder calls. Banned seeds refused
  (`protocol.py:109-114`); instrumented → 0 decoder calls.
- **No import-time I/O / global RNG**: AST scan shows only imports, constants,
  `try/except ImportError` and function/class definitions at top level (plus the
  standard `if __name__ == "__main__"` guard at `protocol.py:885`); the only
  RNG is the explicit `np.random.default_rng(seed)` inside `execute_blocks`
  (`protocol.py:623`).
- **Adapter signatures**: `FrameBatch`/`IRRunConfig`/`IRRunResult` unchanged
  (`types.py` not modified; test A10 asserts field lists and `run(self, batch,
  cfg)`); `beta_eff_empirical` comes from
  `metrics.leakage.compute_beta_eff_empirical` (`nbpolar_static.py:185`),
  derived, never hand-filled; success = `exact` only with `undetected` in
  metadata (`nbpolar_static.py:14-28,175,200-204`).

## 4. Tests — PASS

Commands (fresh basetemp, cache disabled):

```bash
V=/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python
BASETEMP=$(mktemp -d /tmp/opencode/p5_focused_bt_XXXX)
$V -m pytest -q -p no:cacheprovider --basetemp="$BASETEMP" comparison_bench/tests/test_nbpolar_protocol.py
# -> 16 passed, 1 warning in 5.71s

BASETEMP=$(mktemp -d /tmp/opencode/p5_full_bt_XXXX)
$V -m pytest -q -p no:cacheprovider --basetemp="$BASETEMP" \
  comparison_bench/tests/test_nbpolar_construction.py \
  comparison_bench/tests/test_nbpolar_empirical_sc.py \
  comparison_bench/tests/test_nbpolar_p2r1_diagnostic.py \
  comparison_bench/tests/test_nbpolar_prior.py \
  comparison_bench/tests/test_nbpolar_prior_artifact.py \
  comparison_bench/tests/test_nbpolar_protocol.py \
  comparison_bench/tests/test_nbpolar_r1.py \
  comparison_bench/tests/test_nbpolar_sc.py \
  comparison_bench/tests/test_nbpolar_transform.py
# -> 136 passed, 1 warning in 63.43s (16 new + 120 predecessor, exactly as declared)
```

Substance review of `test_nbpolar_protocol.py` (16 tests): A01 zero/non-zero
disclosed round-trip with a `sc_decode` spy proving values equal `U[D]` (lines
144-180); A02 D invariance and equality to `analytic_order(0.05,256)[:45]`
(183-210); A03 full 1024-ary label re-encode and MSB-first bit expansion
(213-231); A04 truth sentinel positive + aliased detection and metric spy
(234-265); A05 decoder-once / verification-once instrumentation, including the
`decode_failed` no-tag path (268-300); A06 wrong-tag mutation (alternating tag)
→ `verify_failed`, no retry (303-325); A07 forced collision → `undetected`,
never success, hard gate `undetected_zero` false, candidate null (328-361);
A08 disjoint/exhaustive scripted run exercising `exact + decode_failed +
undetected` with exact totals and 289/225 bit split (364-409); A09 recount and
tamper detection (412-439); A10 adapter round-trip and unchanged signatures
(442-516); A11 exhaustive tiny GF32/mul/transform/label/Toeplitz literal oracle
plus seed determinism/independence (519-564); refusals (567-585); five-file
schema (588-617); resource abort both stops (620-642); Wilson known values
(645-652); forbidden-marker/import-time scan (655-664).
Residual: the test file contains the frozen seed literal once, in
`assert proto.validate_run_seed(2026091317) == 2026091317` (line 570), which
only asserts CLI usability and never feeds an RNG/decoder — see N-5.

## 5. Scope / premises — PASS

- `git status --porcelain` matches the declared set: new P5 implementation
  `formal_ir/nbpolar/protocol.py`, `methods/nbpolar_static.py`,
  `tests/test_nbpolar_protocol.py`; modified `formal_ir/nbpolar/__init__.py`
  (explicit exports only; `git diff HEAD` = the protocol import block and
  `__all__` names, P5 delta only), `STATUS.yaml`, `P5_FREEZE.md`,
  `P5_IMPLEMENTATION_NOTES.md`, and
  OpenSpec `design.md` Rev note (mtime 02:09). The remaining untracked items
  (P4 queue return files, `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/
  nbpolar-phase4-p3/`, mtime 00:41) and modified docs (`AGENT_PROJECT_MEMORY.md`,
  `CURRENT_TASK.md`, `docs/decision-log.md`, `docs/troubleshooting.md`,
  `docs/nbpolar/DOCUMENT_INDEX.md`, P3/P4 OpenSpec files) all have mtimes
  ≤ 01:33:18, i.e. before the P5 implementation window (01:46–02:14), and none
  of their content has P5 fingerprints.
- Frozen `src/ experiments/ tools/` untouched (`git status` shows nothing
  there); `results/` and `comparison_bench/outputs_comparison/` have no file
  modified after 2026-09-13 01:00 (`find ... -newermt` empty).
- Sibling checkouts: no P5 fingerprint (`static_protocol_dev_gate`,
  2026091317/2026091318, `nbpolar_static`) found in the sibling's
  `comparison_bench/src`, `tests`, `docs`, `openspec`, `.workbuddy`; sibling
  activity on 2026-09-13 01:44–02:04 belongs to its own D7 root-cause cycle
  (e.g. `V72P2D7-ROOT-CAUSE-RESET/D7_F_CORRIGENDUM_R1.md`), not to this packet.
  The sibling is used only as the pinned interpreter.
- No commit/push: `HEAD = ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged),
  `git diff --cached` empty.
- Real dev-gate root absent now (see §0).

## 6. Freeze-doc defect adjudication (R1/R2) — PASS

R1 is recorded in `P5_FREEZE.md:12-21` and `design.md:3-11` and implemented:
disclosure is the worst-first first-45 set (`protocol.py:117-134`), SC
reconstructs the remaining 211 coordinates; it matches the accepted Phase 3
`evaluate_blocks(..., k=45)` convention and `docs/nbpolar/ARCHITECTURE.md:92-94`
("Alice sends the actual values `U[D]`"). R2 is recorded and implemented:
`label_j = 32*x_hat_j`, message domain 2560 bits, seed 2623 bits
(`protocol.py:80-84,137-140`). The current `TASK_PACKET.md` contains no
contradicting "information set/complement" wording; the only occurrence is
inside the Rev note describing the superseded sentence. **No residual frozen
requirement conflict.** No decision is needed from the main thread.

## Findings

Blocking issues: **none**.

Non-blocking suggestions (no repair required before execution):

- **N-1 (precision note).** The frozen `z = 1.6448536269514722`
  (`protocol.py:85`) is the conventional published constant but is 2 ulp below
  the correctly rounded double of the true one-sided 95% quantile
  (70-digit independent computation: true z = 1.64485362695147271486…; nearest
  double `0x1.a515209676abdp+0` = 1.6448536269514726, distance 7.9e-17; frozen
  literal distance 5.2e-16). Effect on the Wilson bound is ≤ 1e-15 — irrelevant
  to the ≥ 0.90 gate. The implementation uses the frozen literal exactly, so no
  change is needed; recording it for provenance only.
- **N-2.** `validate_run_seed` accepts 2026091318 (the Toeplitz master) as a
  run seed (`protocol.py:73-77`). The frozen command uses 2026091317, so this
  cannot affect the gate; optional future hardening only.
- **N-3.** `FROZEN_RUN_SEED` is defined/exported (`protocol.py:71`,
  `__init__.py:37,112`) but not enforced by the CLI; enforcement is the frozen
  command text. Consistent with the "no flags added or changed" rule.
- **N-4.** `run_static_block` maps any exception from `sc_decode` to
  `decode_failed` (`protocol.py:322`); the class name is persisted in
  `error_type`/`decode_error_types`, so an unexpected exception would be
  visible. Matches the frozen "SC exception → decode_failed" contract.
- **N-5.** The test file references the frozen seed literal once
  (`test_nbpolar_protocol.py:570`) in a `validate_run_seed` assertion; the seed
  is never used to generate blocks or call the decoder, so the "tests never use
  it" intent holds. The docstring wording at line 5 is slightly imprecise.
- **N-6.** `per_block_outcomes.json` names its record list `"blocks"`
  (`protocol.py:832`) while the freeze only specifies `n_blocks` plus the scalar
  fields; the key is captured by the schema test. No action needed.

## Closure statements

- The real 300-block dev-gate command **was not run**; no scientific
  `sc_decode` under the frozen seed was invoked. `attempts_used` remains **0**.
- The output root `.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/
  static_protocol_dev_gate/` is **still absent** (re-checked at the end of
  review).
- Model-F/artifacts/parquet/TTBin/real data were not read or touched;
  `results/` and `comparison_bench/outputs_comparison/` are unmodified; no
  sibling, commit, or push occurred.
- This review unblocks the frozen command subject to the already-recorded user
  authorization. At execution time the root must still be absent; the attempt
  is consumed at the first scientific `sc_decode` call and must not be rerun,
  retuned, or seed-changed after that point.
