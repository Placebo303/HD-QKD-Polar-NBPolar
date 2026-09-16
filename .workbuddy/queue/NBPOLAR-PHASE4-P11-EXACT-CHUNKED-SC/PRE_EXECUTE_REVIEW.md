# Pre-EXECUTE review — NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC (independent, read-only)

Reviewer: independent reviewer-go (did not write the code).
Scope: Tier-Y packet `NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC`, Wave-A implementation freeze only.
Constraint observed: frozen gate command NEVER run; unit-test invocations only (focused + predecessor suite + tiny smoke reads);
no artifact/evidence/raw/held-out/real/EVAL/tag/protocol access; no old-root writes; no commit/push.
Attempt state at review end: 0/1 used; gate root still absent (verified §8/§9).

## Verdict: PASS

The frozen implementation, tests, command, output schema, target absence, budgets and attempt point satisfy
`TASK_PACKET.md` P11-01..P11-07. Wave-C single execution is authorized subject ONLY to the frozen command/root/seed
and the ratified partial-evidence semantics in §5. Two non-blocking documentation notes (§4N1, §4N2) require no
pre-execution repair; any other change requires re-freeze and re-review.

---

## 1. STATUS exactness — PASS

Command:

```bash
cat .workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/STATUS.yaml
```

Raw evidence (byte-exact at review time):

```yaml
task_id: NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC
state: IMPLEMENTATION_COMPLETE_PENDING_PRE_EXECUTE
tier: Y
predecessor: X12_PROBE_COMPLETE_DESCRIPTIVE_ONLY
documentation_authorized: true
implementation_authorized: true
decoder_execution_authorized: true
artifact_access_authorized: false
attempts_allowed: 1
attempts_used: 0
scientific_promotion: false
result: null
independent_pre_execute: pending
independent_pre_result: pending
next_gate: INDEPENDENT_PRE_EXECUTE
```

Checks: three authorized flags exactly `true` (documentation/implementation/decoder_execution);
`artifact_access_authorized: false`; `attempts 0/1`; `result: null`; both independent reviews `pending`;
`state`/`next_gate` as declared. No other flags present. PASS.

## 2. OpenSpec P11 delta consistency — PASS

Commands:

```bash
grep -n "^- \[.\].*P11" openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md
grep -n "authorizes no production" openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p11/spec.md
```

Raw evidence:

- `tasks.md` P11-1..P11-9 ALL `- [ ]` (unchecked, 9/9). P11-1 states "no production behavior is authorized by this doc";
  P11-5 states "this doc authorizes nothing"; P11-6..P11-9 reserve review/execution/acceptance to main thread + reviewer.
- `specs/nbpolar-phase4-p11/spec.md:16`: "This document authorizes no production behavior."
- `P11_FREEZE.md:5`: "It authorizes nothing; an independent reviewer-go Pre-EXECUTE PASS is required before the first formal `sc_decode`."
- Delta contract matches `TASK_PACKET.md`: allocation-only `_minus_block` (keyword-only `chunk_rows` default 512,
  contiguous slices, `first_slice[:, index] + second_slice[:, None, :]` + `np.logaddexp.reduce(axis=2)` + single
  full-matrix `_normalize_rows`, `None` golden comparator, bool/non-integral/nonpositive rejection, no
  FWHT/clipping/caching/reorder/dynamic-range/approx/env-config/no new `sc_decode` arg); frozen seed/env/steps/gates/
  labels/scope identical to P11-02..P11-07. PASS.
- Note: `tasks.md` diff is 416 insertions covering P3..P11 phases (shared file accumulating phases); the P11 section
  itself is additive and correctly scoped. Not scope creep for this packet.

## 3. Allocation-only proof — PASS

Command:

```bash
git diff -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py
```

Raw evidence (complete diff, 28+/36- lines, only `_minus_block`):

- `sc.py:176-178`: `def _minus_block(first, second, index, *, chunk_rows: int | None = 512)` — keyword-only, default exactly 512.
- `sc.py:187-189`: `chunk_rows=None` runs the literal accepted expression
  `first[:, index] + second[:, None, :]` → `np.logaddexp.reduce(axis=2)` → `_normalize_rows` (golden path).
- `sc.py:190-198`: `bool`/non-`Integral` → `TypeError`, nonpositive → `ValueError`, BEFORE `np.empty` allocation (line 200).
- `sc.py:199-207`: `rows = first.shape[0]`; `out = np.empty((rows, first.shape[1]), dtype=np.float64)`;
  contiguous `range(0, rows, chunk)` slices in original order, each `first_slice[:, index] + second_slice[:, None, :]`
  → `logaddexp.reduce(axis=2)`; single full-matrix `_normalize_rows(out)` (never per-slice).
- `sc.py:255`: sole production call site `left_in = _minus_block(block[:half], block[half:], index)` untouched
  (production path becomes chunked-512 by default with zero call-site churn).
- Forbidden-token scan (`grep -ni "fwht\|clip\|cache\|reorder\|dynamic.range\|approx\|getenv\|environ"` on `sc.py` +
  `sc_chunked_gate.py`): no hits in logic (only prose "environment" in report/env dict). No FWHT/clipping/caching/
  reorder/dynamic-range/approx/env-config. PASS.
- `sc_decode` public signature byte-identical: HEAD `def sc_decode(logp_x, *, field, alpha: int = 2,
  known_positions=None, known_values=None) -> SCResult` (HEAD line 188) == worktree `sc.py:216` (identical string);
  runtime `inspect.signature` confirms `(logp_x, *, field, alpha=2, known_positions=None, known_values=None)` with no
  `chunk` parameter; `_frozen_contract_check` (runner `sc_chunked_gate.py:89-97`) enforces both invariants fail-closed.
- No other P11 source file changed: P11 tracked source delta is `sc.py` only; new files are untracked
  `sc_chunked_gate.py` + `test_nbpolar_sc_chunked.py` + `specs/nbpolar-phase4-p11/` + queue dir + `tasks.md` P11 section.
  Other `git diff --name-only` entries (`__init__.py`, `empirical_*.py`, `AGENTS.md`, memory/docs, P3 freeze) are the
  declared pre-existing dirty worktree (IMPLEMENTATION_NOTES §dirty-worktree note); HEAD remains
  `ab173f2a5e17336383a897b941080b731ba3dd9e` with no commit. PASS.

## 4. Runner audit — PASS (with 2 non-blocking notes)

File: `comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc_chunked_gate.py` (708 lines, read in full).

- Requires all three flags, NO defaults: `build_parser` lines 680-682
  (`--seed`/`--chunk-rows`/`--out-dir`, all `required=True`, no `default=`). Smoke + focused test confirm missing args → `SystemExit 2`. PASS.
- Frozen-value enforcement before first decode: lines 172-177 (absent-root `FileExistsError`, `seed != 2026091800` →
  `ValueError`, `chunk-rows != 512` → `ValueError`) all BEFORE imports/contract-check/RNG/first `_minus_block`
  (line 232) and first `sc_decode` (V0 line 289). Focused refusal test bombs `sc_mod.sc_decode` and proves no decode on
  refusal paths. PASS.
- Absent-root refusal BEFORE first `sc_decode`: line 172-173 `if out_path.exists(): raise FileExistsError` precedes every
  decode; `mkdir(parents=True, exist_ok=False)` at line 661 plus post-write `written != FOUR_FILES` guard (lines 668-670).
  PASS.
- Step order: §1a primitives (229-249, rows-asc × kinds) → §1b V0 16 cases (251-301) → §1c N=64/256 controls
  (303-412: F1/F2/F3 → K4 → C3 → C4 → T5) → §2 paired N=65536 direct-FIRST then default-512 (414-436) →
  §3 N=262144 default-512 (438-469). Arm order `direct_before_chunked` persisted (line 430). PASS.
- RNG stream discipline: single `np.random.default_rng(FROZEN_SEED)` (line 217); draw order primitives → V0 fixed
  (no draws) → N64 controls → N256 controls (each: f1/f2/f3 uniform, `choice` pos, c3 uniform, C4 `integers`+`uniform`
  data-dependent count stream-ordered) → N65536 block → N262144 block. Matches frozen `rng_stream_order` string
  (line 504) and X12 prereg order (primitives rows-asc × kinds → N64 → N256 → scaling N-asc, C4 data-dependent).
  X12 used seed 2026091780 with 12 primitive rows incl. 8192; P11 freezes 11 rows (excl. 8192) per P11-03 scope and
  single paired-N65536 + single N262144 per P11-04 — intentional Tier-Y narrowing, documented in freeze §3/§6 and
  IMPLEMENTATION_NOTES X12-promotion notes. PASS.
- C4/impossible + X11-C3 + ties: C4 400-try bounded search requiring identical `ImpossibleDisclosedValueError`
  type+message parity (366-398); C3 X11 pattern (`j%3==0` odd-off + positive-support values at sorted 25% positions,
  350-364); T5 exact-tie zeros / ramp `arange-31` / near-tie `col1=-1e-9` (400-412). PASS.
- Attempt recorded 1/1 at first formal `sc_decode`: `frozen_plan.attempt_accounting` (521-529)
  `attempts_allowed 1 / consumed_before 0 / consumed_by_this_run 1`, `consumption_point` = ATTEMPT_CONSUMPTION_POINT
  (51-54), `artifact_reads 0/0`, `no_reopen` N/A string. See NOTE 4N1. PASS.
- Exit codes: `main` lines 686-704: `ValueError/FileExistsError/OSError` → 2 (refusal, nothing written);
  non-candidate label → 1 (blocked, four files with earliest `BLOCKED(<gate>)`); candidate → 0. `GateBlocked` catch → 1
  is documented-unreachable (conversion happens inside `run_chunked_gate`). See NOTE 4N2. PASS.
- Four-file schema scalar-only: `FOUR_FILES` (59-64) + writes (661-667) exactly `frozen_plan.json`,
  `equivalence_records.json`, `scaling_record.json`, `report.md`; post-write exact-set guard. Cell/case/control/cmp
  dicts persist ONLY scalars: equality booleans, mismatch counts, `max_finite_abs_err`, support masks counts,
  exception type+message, walls, RSS dicts, accounting, gates. Verified: no input vectors/decisions/metrics/decoded
  keys/raw arrays/artifacts persisted (report lines 654-658 state the exclusion; `_cmp_results` 123-152 and cell dicts
  235-247 expose only parities/counts/magnitudes). PASS.
- Labels exact: `GATE_NAMES` (45-50) `semantic_parity / paired_n65536_exact / large_n262144_completion / large_n262144_rss`
  in order; `EXACT_CHUNKED_SC_CANDIDATE` (225); `BLOCKED(<gate>)` via `GateBlocked` (67-72); cascade-false from failed
  index (483-487). PASS.
- Envelope: `TIMEOUT_S 600` / `VSZ_KB 2097152` (43-44) + frozen three-line `ulimit -v 2097152` + `timeout 600` command;
  hard gates N262144 completion + `peak < 1610612736` (468); planning `120 s / 1073741824` RECORDED at 459-464
  (`planning_targets_report_only` with `*_met` booleans) but NOT gated (only hard-limit `fail` at 468-469). X12
  65.73 s / 754.6 MB cumulative-HWM cited as descriptive support only; "no throughput superiority" bounded wording at
  645-653. Correctly separated. PASS.

**NOTE 4N1 (non-blocking):** consumption-point parenthetical names "step-1 N=64 F1_moderate direct arm" (freeze §5,
runner line 51-54), but code order calls the first `sc_decode` in V0 (`nan_entry` direct arm, line 289) before N64 F1
(line 315+). Primitives use `_minus_block` directly (no `sc_decode`). Functionally conservative (attempt consumed no
later than stated; V0 blocks already write partial BLOCKED evidence with no rerun), but the label string misnames the
first arm. Ratified meaning for Wave-C: ANY `sc_decode` inside the frozen run consumes the attempt (V0 included);
no rerun after ANY block. Optional future correction: reword to "first formal `sc_decode` in the frozen run (V0
`nan_entry` direct arm)" — NOT required before this gate; do not re-freeze for this alone.

**NOTE 4N2 (non-blocking):** `main` adds exit 3 for unexpected exceptions with traceback (lines 699-701). Packet
registers 0/1/2 only. Additive and non-confusing (3 ≠ candidate/blocked/refusal; preserves traceback). Ratified as-is.

## 5. OPERATOR-FLAGGED ITEM — `dir()`-guarded partial-evidence fallback — RATIFIED (PASS)

Location: `sc_chunked_gate.py:470-476`:

```python
except GateBlocked as blocked:
    label = str(blocked)
    failed_gate = blocked.gate
    if "paired_record" not in dir():
        paired_record = None
    if "scaling_record" not in dir():
        scaling_record = None
```

Exact semantics ratified:

- **What it writes:** on ANY `GateBlocked` raised via `fail(gate, detail)` after attempt consumption, execution jumps to
  this handler, then FALLS THROUGH to the unconditional four-file build+write path (lines 478-672): `frozen_plan.json`
  (params/env/attempt/budgets/gates+label), `equivalence_records.json` (`primitive_cells` as accumulated,
  `validation_contract` as accumulated, `full_sc` as accumulated dict, `paired_n65536` = record or `None`),
  `scaling_record.json` (`scaling_record` = record or `None`, plus total wall/final RSS), `report.md` (all reached
  cells/cases/controls enumerated; unreached sections render "none (gate blocked before completion)" at lines 602-603,
  627-628). Gates cascade-false from the failed index (483-487); label is the earliest `BLOCKED(<gate>)`.
- **Success path:** no exception → both records defined → full evidence, label CANDIDATE, exit 0.
- **Mid-step-1 block** (primitives/V0/N64/N256): both `None`; partial lists/dict as accumulated. **Step-2 block before
  assignment:** `paired None`; **after paired parity assignment but failed parity:** paired defined, scaling `None`.
  **Step-3 status/finite/RSS fail:** both defined (scaling assigned lines 451-465 BEFORE the 466-469 checks), gates show
  the failed hard gate. All cases still write EXACTLY the four files (verified by 668-670 guard).
- **Failure/refusal paths that write NOTHING (exit 2):** pre-try refusals — existing root (173), wrong seed/chunk
  (174-177), contract/field violations (187-192) — raise before the try/four-file path and are mapped by `main` to
  exit 2. No partial directory is created (mkdir happens only at 661).
- **Ruling:** does NOT violate the four-file schema (same four names, same scalar-only shapes, `None` for unreached
  records is schema-consistent); does NOT violate no-rerun (single write, no retry; enables STOP-with-evidence);
  does NOT violate STOP-and-preserve (it IS the STOP-and-preserve implementation: stops remaining steps, preserves
  accumulated evidence, returns earliest BLOCKED label, exit 1). `dir()`-without-args in function scope reliably
  reports assigned locals in CPython; the two guarded names are assigned exactly once on their success paths
  (427, 451) and read unconditionally later (554/557/602/627), so the guard closes the only `UnboundLocalError` path.
  Pre-initializing to `None` would be stylistically cleaner but requires a re-freeze for zero semantic gain — DO NOT
  change before this gate. **Single decision needed on NEEDS_CHANGES only:** none; fallback is accepted as specified
  above. Wave-C MUST NOT delete/complete/rewrite partial four files after a BLOCKED label.

## 6. Tests — PASS (10 + 262 with pinned interpreter + fresh basetemps; frozen gate never run)

Commands (pinned interpreter, no cache provider, fresh /tmp basetemps; gate command NOT invoked):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_sc_chunked.py -q -p no:cacheprovider --basetemp=/tmp/p11-chunked-basetemp
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_adaptive_l1.py ... [all 18 test_nbpolar_*.py] -q -p no:cacheprovider --basetemp=/tmp/p11-full262b-basetemp
```

Raw evidence:

- Focused: `10 passed in 6.83s` (exit 0). Interpreter `3.12.3`, NumPy `2.5.3` (matches freeze §2).
- Full NB-Polar: `262 passed in 131.73s` (exit 0) = 252 predecessor + 10 new (18 `test_nbpolar_*.py` files sum to 262;
  per-file collect counts verified: 16+12+32+17+17+9+9+11+13+16+10+16+10+11+24+17+12+10).
- Coverage vs P11-03 (file `comparison_bench/tests/test_nbpolar_sc_chunked.py`): CHUNKS 32/128/512/2048 (38);
  PRIM_ROWS 1/31/32/33/127/128/129/511/512/513/2048 (39); moderate/wide/`-inf` kinds (63-79);
  exact `array_equal` vs `chunk_rows=None` (146-159, 130-131); N=64 (244) + N=256 (247) full-SC parity incl. F1/F2/F3,
  K4 known-25%, C3 X11 pattern, C4 impossible-disclosure (400-try, 203-221), T5 exact/ramp/near ties (189-201),
  7 invalid + nan/+inf/all-`-inf` with identical type+message (223-241); default-is-512 + keyword-only (122-131);
  `sc_decode` signature unchanged incl. no `chunk` (252-262); invalid sizes bool/float/str/0/negative rejected,
  numpy-int accepted (265-278); CLI requires every arg + frozen constants (281-297); refusals-before-decode with
  bombed `sc_decode` (300-323); no-production-invocation rule (326-341). All P11-03 items present. PASS.
- Isolation: tests use injected arrays + fresh test seeds `2026091811/1812/1813` only (41-43); frozen seed `2026091800`
  appears ONLY as a constant assertion (291) and in refusal paths that assert NO decode (311-319, with `sc_decode`
  bombed); the frozen-seed execution path is never taken. `grep` for artifact tokens in the test file shows only the
  assembled-forbidden-token check (which asserts absence). Temp dirs only (`TemporaryDirectory`). PASS.

## 7. Bounded smoke (tiny injected arrays, temp root; gate NOT run) — PASS

Command (pinned interpreter; fresh smoke seed 999; NO frozen seed execution; NO gate root):

```bash
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -c "[tiny _minus_block None-vs-512 equality; tiny N=8 sc_decode; _rss_peak; GATE_NAMES/limits; parser-requires-args; frozen consts]"
```

Raw evidence: `tiny_equal: True`; `default: 512`; `tiny_decode: ok (8,)`; `rss: {ru_maxrss ~99MB, VmHWM ~100MB,
peak ~100MB}`; `gates: [semantic_parity, paired_n65536_exact, large_n262144_completion, large_n262144_rss]
hard: 1610612736 timeout: 600 vsz: 2097152`; `parser_requires_args: 2`;
`frozen_consts: 2026091800 512 65536 262144`.

- Four files / gates: verified by code inspection (FOUR_FILES + mkdir-exact-set guard + gate cascade); smoke did NOT
  create the gate root (creation belongs to the single Wave-C attempt).
- Wall/RSS margin for the N262144 step: not re-measured here (measurement IS the gate). Margin is supported by X12
  descriptive observations (65.73 s wall, 754.6 MB cumulative HWM vs 600 s timeout / 2 GiB VSZ / 1.5 GiB hard gate) plus
  smoke RSS ~100 MB at tiny-N showing no baseline pressure; hard vs report-only separation verified in §4. PASS.

## 8. Frozen identity — PASS

- Exact 3-line command byte-identical: `sed -n '116p' TASK_PACKET.md` == `sed -n '47p' P11_FREEZE.md` (`diff` →
  `BYTE_IDENTICAL`); three-line blocks `cd …/nbpolar` / `ulimit -v 2097152` / `timeout 600 … sc_chunked_gate --seed
  2026091800 --chunk-rows 512 --out-dir …/exact_chunked_sc_gate` identical modulo markdown fence. Runner
  `frozen_plan.command` (506-513) is the `&&`-joined semantic equivalent (same cwd/interpreter/module/args/root). PASS.
- Seed `2026091800` fresh: `grep -rln "2026091800" --exclude-dir=.git` returns EXACTLY 7 P11-scoped files —
  4 packet docs (`TASK_PACKET.md`, `P11_FREEZE.md`, `P11_IMPLEMENTATION_NOTES.md`, `AUTHORIZATION_PROMPT.md`) +
  `sc_chunked_gate.py` + `test_nbpolar_sc_chunked.py` + `specs/nbpolar-phase4-p11/spec.md`. No prior/official seed,
  no other module, no tasks.md hit. (Plain `rg` without `--no-ignore` under-reports `.workbuddy/`; `grep -rn` is the
  authoritative check.) PASS.
- Output root ABSENT: `ls …/exact_chunked_sc_gate/` → `No such file or directory` (before and after all test/smoke
  invocations). PASS.
- No artifact access possible: runner's only `open()` is `/proc/self/status` for RSS (line 79); no `np.load/stat/read`
  of any data path (artifact-token grep hits are prose/schema/accounting strings only, §4); four writes confined to the
  absent root. PASS.
- Environment pinned: `Python 3.12.3 / NumPy 2.5.3` at review time, matching freeze §2. PASS.

## 9. Scope / premises — PASS

- `git status --porcelain` P11 set matches declared Wave-A set: M `sc.py` (allocation delta only), M `tasks.md`
  (P11 section additive), untracked `sc_chunked_gate.py` / `test_nbpolar_sc_chunked.py` /
  `specs/nbpolar-phase4-p11/` / `.workbuddy/.../P11-EXACT-CHUNKED-SC/` (+ its 6 lifecycle docs). All other
  modified/untracked entries are pre-existing unrelated phases/worktree state (P3 empirical, P4-P10/X-probes, docs),
  preserved untouched per IMPLEMENTATION_NOTES. No `results/` / `workspace/probes/` / `outputs_comparison/` writes
  from this review (`git status --porcelain -- results/ workspace/probes/ comparison_bench/outputs_comparison/` empty).
- HEAD unchanged: `ab173f2a5e17336383a897b941080b731ba3dd9e` (freeze §7 value); `git log --oneline -3` shows no new
  commit. No commit/push performed. Attempts still 0 (`STATUS.yaml` re-read after tests/smoke). PASS.

---

## Complete frozen record (for Wave-C)

- Contract: allocation-only `_minus_block` chunking, keyword-only `chunk_rows=512` default, `None` golden path,
  `TypeError/ValueError` before allocation, single full-matrix `_normalize_rows`, `sc_decode` signature/schemes stable.
- Seed/env: `2026091800`, NumPy float64, GF(32) poly 37 alpha 2, pinned
  `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3 / NumPy 2.5.3).
- Command (exact 3 lines):
  ```bash
  cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
  ulimit -v 2097152
  timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc_chunked_gate --seed 2026091800 --chunk-rows 512 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate
  ```
- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/` ABSENT until execution; exactly
  four files (`frozen_plan.json`, `equivalence_records.json`, `scaling_record.json`, `report.md`), scalar-only.
- Budgets: `ulimit -v 2097152`, `timeout 600`; hard gates N262144 completion + RSS `< 1610612736`; planning
  `120 s / 1 GiB` recorded-not-gated; no throughput claim.
- Gates/labels: `semantic_parity → paired_n65536_exact → large_n262144_completion → large_n262144_rss`; all-true →
  `EXACT_CHUNKED_SC_CANDIDATE` (pending main-thread acceptance + Pre-RESULT recomputation); else earliest
  `BLOCKED(<gate>)`; exits 0 candidate / 1 blocked / 2 refusal (+3 unexpected, §4N2).
- Attempt: 1 allowed / 0 used; consumed by ANY `sc_decode` in the frozen run (V0 included, §4N1); no artifact reads;
  no rerun/retune/repair/cleanup/seed/chunk/threshold change after consumption; STOP-and-preserve on any blocker.
- Forbidden: artifact/evidence/raw/held-out/real/EVAL, prior seeds, tag/protocol, N>262144, FWHT/APP/SCL,
  FER/efficiency/key-rate/qualification/promotion, old-root edits, commit/push.

## Findings with file:line

- Blocking: none.
- Non-blocking NOTE 4N1: `sc_chunked_gate.py:51-54` + `P11_FREEZE.md:83` parenthetical vs actual first `sc_decode` at
  `sc_chunked_gate.py:289` (V0) — ratified meaning in §4N1; no repair before gate.
- Non-blocking NOTE 4N2: `sc_chunked_gate.py:699-701` exit 3 — ratified additive; no repair before gate.
- Informational: `tasks.md` 416-line diff spans P3..P11 (shared-phase file); P11 section itself additive with 9/9 boxes
  unchecked. `rg` default under-reports `.workbuddy/` seed hits; `grep -rn` (§8) is authoritative.

## Closure statements

- Frozen gate NEVER run by this review (no `sc_chunked_gate` execution with the frozen seed; only focused/full pytest
  with fresh test seeds + tiny injected smoke reads + code inspection).
- Attempts still 0 (`STATUS.yaml`: `attempts_used: 0`, both independent reviews `pending`).
- Gate root still absent (`exact_chunked_sc_gate/`: `No such file or directory` after all checks).
- No artifact/evidence/raw/held-out/real/EVAL/tag/protocol path opened; no old-root/production output written; no
  commit/push; HEAD `ab173f2a5e17336383a897b941080b731ba3dd9e` unchanged.
- This file (`.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/PRE_EXECUTE_REVIEW.md`) is the SOLE write of this
  review.
