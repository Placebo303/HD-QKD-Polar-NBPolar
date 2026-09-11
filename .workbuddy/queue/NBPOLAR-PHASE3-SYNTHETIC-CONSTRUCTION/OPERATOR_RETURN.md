# OPERATOR_RETURN — NBPOLAR-PHASE3-SYNTHETIC-CONSTRUCTION

Terminal: BLOCKED(EVAL_GATE)

## 1. Terminal and first failing gate

`BLOCKED(EVAL_GATE)`. First failure is P3-T1-08 zero
impossible-disclosure: frozen eps=0.05 K=45 EVAL gives 299/300 exact
(pass >=285), 300/300 initial-error (pass >=240), but 1
impossible-disclosure at block 104 (fail zero). Exact means U and X
both match; failures listed without rerun. EVAL preserved unchanged;
no Phase 4.

## 2. Changed files and line counts

| File | Lines | Note |
|------|-------|------|
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/synthetic.py` | 138 new | erasure/QSC generators, analytic oracle, frozen seeds |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/construction.py` | 277 new | genie via full-true `sc_decode`, order, eval, spearman |
| `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py` | 56 edited (+36) | Phase 3 public surface (27 names) |
| `comparison_bench/tests/test_nbpolar_construction.py` | 474 new | 12 focused tests, plain-python runnable |
| `comparison_bench/tests/test_nbpolar_sc.py` | 618 edited (+2/-3) | one-line `__all__` subset-fix (see §11) |
| `.workbuddy/.../EXPLORATION_NOTES.md` | 87 new | two genie designs, order, tie, DEV evidence |
| `.workbuddy/.../EVAL_FREEZE.md` | 74 new | frozen candidate, DEV table, EVAL identity, EVAL-not-run statement |
| `.workbuddy/.../REVIEWER_GO_EVAL_FREEZE.md` | 46 new | independent verification PASS, one EVAL authorized |
| `.workbuddy/.../OPERATOR_RETURN.md` | this file | BLOCKED return |
| `.workbuddy/.../STATUS.yaml` | edited | → `BLOCKED` |

Phase 1 `algebra.py`/`transform.py` logic unchanged. No commit/push.

## 3. Pre-EXECUTE self-check (PASS, recorded before edits)

Branch `codex/nbpolar-phase0` confirmed; `git status` preserved
unrelated dirty (AGENTS.md etc.); frozen dirs
`src experiments tools results outputs_comparison nonbinary_field.py`
empty diff; packet/contract/seeds/grid read; STATUS.yaml authorized
TRAIN/DEV + EVAL-after-review; target outputs absent (no freeze/return
yet); Phase 1/2 33/33 pytest PASS before edits.

## 4. Selected architecture

`genie_conditionals` reuses accepted `sc_decode` with full-true
disclosure per TRAIN sample (no new core, no truth arg added, Phase 2
suite unchanged except surface subset-fix). Risks `h/e` averaged over
TRAIN; order descending `(e,h)` ties by index. Evaluation discloses
only first-K actual U values. Analytic per-element
`[2e-e^2, e^2]` matches natural `G_N`. Rejected: duplicate
minus/plus recursion (~60 lines, private-import risk); policy-callback
core (invasive Phase 2 refactor). See EXPLORATION_NOTES.

## 5. P3-T0/T1 table

| ID | Result | Evidence |
|----|--------|----------|
| P3-T0-01 | PASS | py_compile 5 files OK; 45/45 pytest (17+16+12); imports no I/O/global RNG (`default_rng` absent in production) |
| P3-T1-01 | PASS | shapes/support/posterior exact; 20k scalars erasure 2992/3000 tol253, QSC 1978/2000 tol213 (5-sigma+1 predeclared) |
| P3-T1-02 | PASS | N=2 exact `2e-e^2/e^2`; N=4,8,256 mean within 1e-12, values in [0,1]; endpoints 0/1 exact |
| P3-T1-03 | PASS | 26 tiny rows (GF4 N=4 erasure/QSC, GF32 N=2) max prob 2.2e-16, max log 8.9e-16, 0 support mismatch; `sc_decode` has no truth param |
| P3-T1-04 | PASS | h in [0,log2q], e in [0,1-1/q]; noiseless zero; full-erase limit (h=5,e=31/32 for q=32); repeats identical, new seed diverges but metadata preserved; order permutation with index tie-break; QSC q=4 tiny OK |
| P3-T1-05 | FAIL on main-thread adjudication | analytic mean 0.10 exact and extreme 0.816>=0.20; frozen full-vector Spearman is 0.7665<0.90. Resolvable-subset Spearman 0.9959 and overlap 0.98 are retained as diagnostics, not substituted for the frozen population. |
| P3-T1-06 | PASS | U-coordinate disclosure, zero retained, later-known leaves earlier rows bitwise equal; N=64 order is permutation |
| P3-T1-07 | PASS | DEV 12×100 all init 100/100; EVAL init 300/300>=240; argmax-before-SC, no truth-centered metric |
| P3-T1-08 | FAIL | EVAL 300: exact 299>=285 PASS, init 300>=240 PASS, but impossible 1 (block 104) violates zero; NaN 0, other 0; no rerun |
| P3-T1-09 | PASS | seeds 2026091200/01/02/03 distinct; same-seed identical, new-seed divergent; order from TRAIN stats only; no PW/Release import in production |
| P3-T1-10 | PASS | scoped rg zero (Model-F/TTBin/CAL/VAL/LDPC/PEG/QC/BP/Cascade/PW/BSC/LLR/CRC/SCL/polar_existing/IRRunResult/outputs); N=64 decode 0.004s; TRAIN 35s+DEV 19s+EVAL 5s+tests 37s <30min; peak blocks ~tens KiB <2GiB |

> Main-thread adjudication B3 (doc-only, 2026-09-11): the proposed
> resolvability-primary reading is not ratified. Packet P3-T1-05 names the
> full genie-risk vector and freezes Spearman >=0.90. The observed 0.7665 is
> therefore FAIL. The e>0 subset result 0.9959 and top-50 overlap 0.98 remain
> useful diagnostics of finite-TRAIN tie resolution, without changing the
> preregistered population after observation.

## 6. Generator empirical checks

Unit stream: erasure eps=0.15 2992 erasures/20000 (exp 3000, 5σ+1=253);
QSC p=0.10 1978 flips/20000 (exp 2000, tol 213). Shapes/markers/
posteriors exact per §5. Endpoints: erasure 0 one-hot /1 uniform; QSC
0 one-hot, (q-1)/q uniform supported.

## 7. Analytic/genie oracle errors

Analytic preserves mean within 1e-12; per-element order correlates
0.77 vs block 0.62 (selected). Genie vs exhaustive oracle 26 rows
2.2e-16/8.9e-16/0 mismatch. TRAIN full-disclosure impossible 0/512
per epsilon (4×512).

## 8. Construction statistics and rank/overlap

q=32 N=256 eps=0.10 TRAIN 512 (unit): resolvable n=66 Spearman 0.998,
overlap 0.98, Pearson raw 0.9998. Official TRAIN eps=0.10: full 0.7665,
resolvable 0.9959 (n=66), overlap 0.98. h/5 vs analytic max 0.035
(Monte Carlo noise). Noiseless zero, full-erase limit exact.

## 9. Full DEV candidate table and selection

TRAIN_SEED sequential 512/epsilon (35.1 s, 0 impossible). DEV_SEED
sequential 100/candidate (19.4 s). Table in EVAL_FREEZE §2; sole
retained eps=0.05 K=45 99/100 imposs 0. Deterministic smallest-K
selects (0.05,45). No out-of-grid tuning; QSC not searched.

## 10. Reviewer-go EVAL-freeze verdict

`REVIEWER_GO_EVAL_FREEZE.md` PASS (fresh-process checklist: compile,
zero forbidden, seeds distinct, truth-free API, 45-order valid, DEV
re-derived, freeze states EVAL-not-run). One 300-block EVAL on frozen
eps=0.05 K=45 authorized. Needs-changes none.

## 11. Frozen EVAL identity and one-shot result (preserved)

EVAL_SEED=2026091203, exactly 300 erasure blocks eps=0.05 K=45 with
frozen 45-list, GF32 poly37 alpha2 natural order. Single run 5.1 s:
exact 299/300, initial-error 300/300, impossible 1 (block 104),
other 0, nan 0, fails=[104]. Criteria: exact>=285 PASS, init>=240
PASS, zero-impossible FAIL. No rerun/replacement; diagnostic unit-seed
checks (genie 298/1, analytic 297/2 per 300) did not touch EVAL stream.
Attribution per §9: layers 1–6 cleared (generator/analytic/genie/
accumulation/plumbing/SC all prove exact); finite TRAIN noise ruled
out (genie ≥ analytic on unit300); root is finite N/K insufficiency
within the frozen grid (even optimal analytic order shows ~1/300
impossible at K=45; grid max for eps=0.05 is 45).

## 12. Runtime/memory and scope audits

`py_compile` OK; `git diff --check` clean; 45/45 pytest 36.6 s (Miniforge,
known `cache_dir` warning only); frozen dirs empty diff; scoped rg zero;
TRAIN 35.1 s + DEV 19.4 s + EVAL 5.1 s + tests 36.6 s <30 min; N=256
decode 0.016 s, peak extra `(128,32,32)` float64 ~1 MiB <2 GiB.
Unrelated dirty (`AGENTS.md`, `AGENT_HANDOFF.md`, etc.) preserved
untouched. No `run_01`, no results/output writes, no Model-F/real-data/
adapters/SCL/rate/commit/push/Phase 4.

## 13. Rejected designs and discovered/fixed bugs

See EXPLORATION_NOTES §1/5: Alt B duplicate recursion, Alt C policy
core; block-order analytic; production `PW`/`protocol` docstrings and
bare-`VAL` test gate (fixed to word-boundary); erasure-0 finite-count
test fix; impossible-as-non-exact plumbing; Phase 2 `__all__`
exact-11 → subset proof (failing regression shown by 27-name surface;
smallest test-only fix, 33/33 preserved).

## 14. Next gate and boundary

Next: main-thread decision on EVAL_GATE (see §15). No acceptance,
qualification, promotion, or Phase 4. Model-F/CAL/VAL/TTBin, real data,
reconciliation-cost accounting, method adapters, SCL, rate adaptation,
benchmark roots, commit/push, and broad performance/scientific claims
are explicitly refused. Bounded synthetic result only.

## 15. BLOCKED: one decision needed

Increase the frozen grid (e.g., allow K_margin>32 for eps=0.05 or
N/K re-freeze) or relax P3-T1-08 zero-impossible to an
impossible-inclusive exact gate (e.g., exact>=285 counts impossible as
non-exact, which already passes 299/300)? Without one of these,
K=45 cannot give zero impossibles in 300 blocks even with optimal
ordering. Do not tune EVAL, reuse EVAL in TRAIN, or modify SC to
 rescue construction.

> Cure note §15-retention (doc-only, 2026-09-11): the two options above
> are both retained and neither is executed in this pass — no EVAL
> retune, no EVAL reuse in TRAIN, no SC/order/threshold change, no
> success-criterion edit. Option (b) is recorded as already numerically
> satisfied (299/300 exact >= 285 with impossible counted as non-exact)
> but is not adopted here; the BLOCKED terminal stands pending
> main-thread decision.
