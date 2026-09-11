# OPERATOR_RETURN_R1 — NBPOLAR-PHASE3-R1-CONSTRUCTION-RECOVERY

Terminal: `BLOCKED(INDEPENDENT_REVIEW_UNAVAILABLE)`

## 1. Terminal and first failing gate

`BLOCKED(INDEPENDENT_REVIEW_UNAVAILABLE)`. All R1 implementation,
TRAIN/DEV, selection, and freeze stages are complete and green; the
single earliest gate that stops the lifecycle is the packet-mandated
real reviewer-go PASS on the frozen EVAL contract. This environment
exposes no subagent/review invocation tool (function list is
bash/edit/grep/question/read/sciverse/skill/webfetch/websearch/write;
no reviewer-go skill; no `reviewer-go`/`opencode` binary on PATH), so a
separate operator process or self-check cannot authorize EVAL (packet:
"not authorization"). EVAL is therefore unattempted: R1 seed 2026091213
unconsumed, `eval_r1_fresh/` absent. No Phase 4, no promotion.

## 2. Changed files and line counts

| File | Change | Note |
|------|--------|------|
| `formal_ir/nbpolar/construction.py` | +85 / −0 | `resolvable_rank_corr`, `analytic_construction`, `failure_summary`; no existing line touched |
| `formal_ir/nbpolar/__init__.py` | +6 / −0 | 3 imports + 3 `__all__` entries |
| `formal_ir/nbpolar/eval_r1.py` | 143 new | one-shot entry: frozen-arg CLI, banned-seed + existing-out refusal |
| `comparison_bench/tests/test_nbpolar_r1.py` | 299 new | 10 focused R1 tests |
| R1 packet `PLAN_R1.md` | 94 new | frozen options/seeds/grid/rules/thresholds (pre-TRAIN/DEV) |
| R1 packet `EVAL_FREEZE_R1.md` | 107 new | selection proof, DEV table, literal 256-order, exact command, EVAL-not-run |
| R1 packet `OPERATOR_RETURN_R1.md` | this file | BLOCKED return |
| R1 packet `STATUS.yaml` | state edit | → BLOCKED, EVAL unattempted |

Predecessor tests untouched; Phase 1/2 production untouched
(`sc_decode` gains no truth arg; oracle suite green). No commit/push.

## 3. Pre-EXECUTE self-check (PASS, recorded before edits)

Branch `codex/nbpolar-phase0` confirmed; unrelated dirty (AGENTS.md
etc.) preserved untouched; frozen roots (`src experiments tools
results outputs_comparison`) empty diff; R1 packet + authorization +
all predecessor artifacts (RETURN/FREEZE/adjudication/review/notes)
read; TRAIN/DEV authorized, EVAL-after-real-review only; R1 target
outputs absent; baseline 45/45 green before edits (plain-python
runners; pytest not installed, installs out of scope).

## 4. Selected architecture (why it answers D1–D3)

- D1 rank resolution: `resolvable_rank_corr` (Spearman over `e>0`,
  `min_n` fail-loud guard) + top-K overlap are the preregistered
  construction metrics; full-vector Spearman is reported, never a gate.
  Quant demo reproduces the predecessor phenomenon on a fresh stream
  (full 0.7603 vs resolvable 0.9995, 192-way zero tie).
- D2 failure class: `failure_summary` pins impossible = failed decode +
  non-exact, separate tag inside one total (`exact+failed==attempted`
  invariant enforced); tiny-oracle rule demonstrated deterministically
  (noiseless wrong disclosure → impossible; oracle shows zero support
  for the forced value, full support for truth).
- D3 replayability: `eval_r1.py` takes the literal full permutation +
  all scalars as required flags, refuses banned seeds
  {2026091200–1203} and any existing out dir; `--help` verified, no
  stream consumed by verification.
- Rejected: larger-K-only fix without construction change (DEV shows
  K=69 still drops blocks for genie orders); genie-order retention
  (loses the frozen tie-break to analytic 100 vs 99 at K=45).

## 5. Test table (55/55, plain-python runners)

17 transform + 16 SC/oracle + 12 predecessor construction + 10 new R1,
all PASS. New coverage: helper semantics + min_n/shape guards,
quantized-tie demo, gate on R1 unit stream (resolv 0.9946/n=69,
overlap 1.000), analytic exactness + erasure-only guard,
failure-summary math + violation cases, noiseless impossible category
+ oracle support check, 4-grid eval invariant, R1 seed separation,
entry guards (banned-seed/bad-order refused, nothing written) + tiny
end-to-end in tempdir, surface + forbidden-coupling scan, resource.

## 6. TRAIN/DEV evidence (R1 streams 2026091211/1212; 104.4 s total)

TRAIN (sequential): O1/512 + O2/2048 per eps ∈ {0.05, 0.10}, 0
impossible in 5120 TRAIN blocks. Gate at eps=0.10: O1 resolv
0.9954/n=69 ov50 1.000 PASS; O2 resolv 0.9966/n=77 ov50 1.000 PASS;
O3 exact-by-construction PASS (calibration = O2 row).
DEV (100/candidate): retained (≥98) → O1 {53:100, 61:100, 69:99},
O2 {45:99, 53:100, 61:99, 69:99}, O3 {45:100, 53:99, 61:100, 69:100};
(0.10,58) retains nothing (94–96), gate discriminates. Selection per
frozen rule: smallest K=45 (O2, O3) → same eps → higher exact →
**O3 analytic, eps=0.05, K=45** (100/100, imposs 0; full order and
first-45 in EVAL_FREEZE_R1 §§1/4).

## 7. Frozen EVAL (not executed — awaiting real review)

R1_EVAL_SEED=2026091213, 300 erasure blocks, eps=0.05, K=45, frozen
first-45 + literal 256-permutation, GF32/alpha2. Prereg: exact ≥
285/300 over all attempts (impossible inside denominator, separately
tagged); init-error ≥ 240/300; NaN/other 0 hard; list failures, no
rerun. Exact command in EVAL_FREEZE_R1 §4 (entry `--help` verified).
Stop: 600 s / NaN / resource abort; peak < 2 GiB. Target
`eval_r1_fresh/` verified absent.

## 8. Scope and resource audits

`py_compile` 4 files OK; `git diff --check` exit 0; frozen production
roots empty diff; scoped forbidden-pattern scan zero (incl. new
files); TRAIN 80.7 s + DEV 23.7 s + suites ≈ 2 min, total < 10 min;
per-block peak ~tens KiB « 2 GiB. No Model-F/real-data/adapters/SCL/
rate/benchmark roots/commit/push/Phase 4/broad claims. Predecessor
seed 2026091203 and its diagnostic never touched.

## 9. Next gate and boundary

One decision needed: provide a real independent reviewer-go PASS on
`EVAL_FREEZE_R1.md` (code, tests, full order, stream separation, DEV
selection, command, thresholds, target absence). On PASS, the operator
runs the §7 command exactly once and files the Pre-RESULT review. On
needs-changes, repair + re-review without touching EVAL. Without that
PASS, EVAL stays unattempted and no Phase 4 follows.
