# TASK PACKET — NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION (PREPARATION ONLY)

Per AGENTS.md §10.1: one complete frozen packet before delegation. This packet
authorizes NOTHING. No production-code execution, no protected reads, no decoder
run under this packet until verbatim user authorization flips `STATUS.yaml`.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verified `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/`
- Parent packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/` (implements its §4 (a)–(e) only; §§5–8 OUT)
- Change: `openspec/changes/nbpolar-prior-rebaseline/` (implements T2/T3/T4 at Stage-1 scope; T1/T5–T8 OUT)
- Python for Stage 1: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (sibling venv; THIS checkout has no `.venv`. TimeTagger never imported in Stage 1)

## Goal

Deliver the decoder-free Stage-1 implementation surface for the M2 ±1 CANDIDATE:
strict adapter beside the frozen package, M0-reproducing switch, synthetic-only
K re-split path, `SECURITY_MODEL.md` CAL note + inventory skeleton, and the
`--freeze-config` runner interface — so Stages 2–3 can later freeze without re-adjudicating science.

## Non-Goals

No `sc.py`/algebra/transform change; no construction re-derivation; no K decision
(fixed-K vs fixed-f DEFERRED); no M1 pooling; no FER/efficiency/promotion claim;
no G1/G2/G3 execution; no S9 citation as evidence; no tunable added beyond the frozen MOD.

## Impact Scope

New `comparison_bench/src/comparison_bench/formal_ir/prior_m2.py` (outside `nbpolar/`);
new `comparison_bench/tests/test_nbpolar_prior_m2.py`; new `scripts/m2_prior_validation.py`;
append-only note in `docs/SECURITY_MODEL.md`; packet `STATUS.yaml` only.
`src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`,
and every file under `formal_ir/nbpolar/` are never written.

## Allowed / Forbidden

READ: parent `TASK_PACKET.md` §4 + `STATUS.yaml` CLI CONTRACT; `nbpolar/{prior,sc}.py`
(read-only oracle of conventions); `v72p2d5_model_f_input.py` (counts_ab/p_b contract);
`PHASE4_P0_PRIOR_CONTRACT.md` §§2–4; change D1–D7 + T2/T3/T4; S8 `body.py` (numbers only).
WRITE (additive): the three new files above + `SECURITY_MODEL.md` note + packet STATUS only.
FORBIDDEN (hard stop): modify `sc.py`/`algebra.py`/`transform.py` or anything under
`src/`/`experiments/`/`tools/`; reuse S8's all-1024-δ fit; open protected data or `.ttbin`;
run any decoder (`sc_decode`/genie/SCL); write outside `workspace/`; add checksums/atomic
writes/locking/retry frameworks (AGENTS.md §5.7).

## Spec 1 — M2 adapter API (`formal_ir/prior_m2.py`, numpy+stdlib ONLY, zero imports from `nbpolar/`)

Constants: `N_LABELS=1024`, `Q_SYMBOL=32`, `FLOOR=1e-15` (literal, never a parameter),
`MODES=("LINEAR_ONLY","CIRCULAR")`, `DEFAULT_MOD="LINEAR_ONLY"` (frozen value, not a tunable;
freeze records `mod_boundary` explicitly and G1/G2 never switch it post-freeze).
Error prefix: `m2 contract:`. Counts input: int64 `(1024,1024)` `[Alice,Bob]`, axis0=Alice
(matches `build_model_f_input`); joint output: float64 `(1024,1024)` `[A,B]`, columns sum 1
within 1e-12. Packing (vendored literally): `U1=s>>5`, `U2=s&31`, `s=low+32*high`;
conditioning `FULL_BOB_ONLY`.
- `fit_m2_triple(counts_ab, *, mod="LINEAR_ONLY") -> dict`: `n0=#{a==b}`;
  `n_plus=#{a==(b+1)%1024}` excluding cell `(0,1023)` iff LINEAR_ONLY;
  `n_minus=#{a==(b-1)%1024}` excluding cell `(1023,0)` iff LINEAR_ONLY; `n`=total.
  Returns `{q0,q_plus1,q_minus1,q_rest,n0,n_plus,n_minus,n_total,mod}` (q=n_x/n).
- `MOD` semantics: LINEAR_ONLY = the two wrap cells `(0,1023)`/`(1023,0)` count as tail
  (floor, conservative); CIRCULAR = wrap is a neighbour (q-priced). Fixed-triple MOD toggle
  changes EXACTLY those 2 cells pre-floor and nothing else.
- `build_m2_joint(q0,q_plus1,q_minus1, *, mod="LINEAR_ONLY", floor=1e-15)`: per-cell rule
  `q0` if `a==b`, `q+1`/`q-1` on the ±1 diagonals minus LINEAR-excluded wrap cells, else 0;
  then `maximum(floor)` + per-B-column renorm. `floor != 1e-15` ⇒ ValueError.
- `build_m0_joint(counts_ab)`: S8 `fit_m0` literally — raw-count MLE columns, empty column →
  uniform `1/1024`, then `maximum(1e-15)` + per-column renorm. This is the P7
  raw-MLE-plus-floor rule, NEVER the λ-concentration formula (see resolution R5).
- `build_prior(counts_ab, *, mode, mod="LINEAR_ONLY")`: `mode ∈ {"M2","M0"}` exact; M0
  ignores MOD (test asserts identical output under both). Unknown mode ⇒ ValueError.
- `split_symbol/combine_symbol`: vendored identical contracts (`(U2,U1)`, `s=low+32*high`).
- `prob_rows_to_logp(probs)`: `(N,32)` finite nonneg, every row positive mass; `0→-inf`
  else `ln p`, subtract rowwise logsumexp; rows logsumexp 0 within 1e-12; no NaN/+inf.
- Layer factorization (CALLER-side, never in module): caller applies UNCHANGED frozen
  `derive_p1`→`(32,1024)` `[U1,B]` = P(U1|B_full) and `derive_p2`→`(32,1024,32)` = P(U2|U1,B),
  then `build_p1_metrics`/`gather_p2_metrics` + `probs_to_symbol_metric(provenance=PRIOR_ONLY)`.
  M2 induces P1/P2 solely through the joint it supplies. Output logp `(N,q)` rows logsumexp 0,
  exact-zero → `-inf`, per `sc.py` consumer contract.

## Spec 2 — M0 switch

`build_prior(..., mode="M0")` reproduces the incumbent P7 table rule BIT-EXACT: same counts
in → identical float64 bits out (`max-abs-diff == 0.0` vs an independent literal in-test
reimplementation sharing no helper). Fixture MUST include zero cells + one empty B column.
Bit-exactness is RULE-level, not CAL-regime-level: it does not reproduce the 1024-frame CAL.

## Spec 3 — K re-split path (synthetic fixtures ONLY)

Call the FROZEN `select_empirical_split(n, e1_mean, h1_mean, e2_mean, h2_mean, k_total)`
(imported by runner/tests from `nbpolar.empirical_genie_scaling`; never reimplemented).
Tests feed HAND-BUILT e/h vectors (no genie/SC call) and recompute `(K1,K2)` by independent
literal enumeration (worst-first `(e,h,index)` order, exhaustive K1 scan, lexicographic min
of `(residual,K1,K2)`); assert exact equality. `k_total` is a REQUIRED caller argument with
no literal baked in; H-proportional code is ABSENT (grep-verified). The fixed-K vs fixed-f
choice (7053/7106 vs 1.2939/1.2952) is DEFERRED — Stage 1 emits no real-data (K1′,K2′).

## Spec 4 — Test suite (`comparison_bench/tests/test_nbpolar_prior_m2.py`)

| # | Test | Tolerance |
|---|---|---|
| T1 | Adapter joint vs independent literal oracle (no shared helper) | max-abs ≤1e-12 |
| T2 | M0 switch bit-exact (zero cells + empty column fixture) | diff == 0.0 exactly |
| T3 | MOD toggle, fixed triple: differ exactly at 2 wrap cells, ==0.0 elsewhere; fit attribution exact ints | exact |
| T4 | `prob_rows_to_logp` normalization | max\|logsumexp\| ≤1e-12 |
| T5 | Exact-zero → `-inf` (zero-containing synthetic rows), no NaN/+inf, no all-`-inf` row | exact |
| T6 | Packing round-trip exhaustive 0..1023 | exact ints |
| T7 | Batch/position permutation equivariance | max-abs ≤1e-12 |
| T8 | Noiseless loopback, DECODER-FREE (one-hot rows → argmax recovers; no `sc_decode` call in Stage 1) | exact |
| T9 | `sc.py`/`algebra.py`/`transform.py` unmodified (`git diff --stat` empty + grep `prior_m2\|M2` in `nbpolar/` zero hits) | exact |
| T10 | No import of frozen package from new module (grep + AST import scan zero hits) | exact |
| T11 | K re-split replay on synthetic e/h vectors; H-proportional text absent | exact equality |
| T12 | Runner: missing/null freeze key → exit 2 listing keys; no `--authorized` → non-zero, reads/creates nothing; `store_true` AST check; import side-effect-free | exact |

## Spec 5 — Runner contract (SPECIFY `scripts/m2_prior_validation.py`, do not write it here)

Import-safe (no argparse/file/decoder work at import; `main(argv=None)` + `__main__` guard);
insert repo root at `sys.path[0]` before any `comparison_bench` import; apply the Swabian
`sys.modules["TimeTagger"]` shim before any `src.qkd_io` import (per `troubleshooting.md`).
`--authorized` is `action="store_true"` (NOT store_false); absent ⇒ stderr + exit 2 FIRST,
reading nothing and creating nothing. `--freeze-config <path>` (JSON/YAML) REQUIRED with any
stage flag; must hold ALL 19 TO-FREEZE keys (`B_tail,delta_min,g2_success_rule,
g2_inconclusive_rule,g2_fail_rule,pairing_window_primary,pairing_window_sensitivity,
skip_frames,cal_split_rule,g2_blocks,tag_master,char_sample_pairs,cal_frame_ids,
heldout_frame_ids,mod_boundary,a1_cal_ids,disjointness_matrix,block_formation_fallback,
g2_arms`); any null/absent ⇒ exit 2 listing ALL missing keys, never a default.
`--stage-g1-nll`/`--stage-g2-decode` (store_true, mutually exclusive, exactly one required).
G1 flags: `--acq-id --window-primary --window-sensitivity --skip --mod --char-pairs --out-root`.
G2 flags: `--acq-id --arms --blocks --k1 --k2 --tag-master --window-primary --mod --out-root`.
Flag↔key cross-check REQUIRED (`--window-primary`=pairing_window_primary,
`--window-sensitivity`=pairing_window_sensitivity, `--skip`=skip_frames, `--mod`=mod_boundary,
`--char-pairs`=char_sample_pairs, `--blocks`=g2_blocks, `--tag-master`=tag_master,
`--arms`=g2_arms); mismatch ⇒ exit 2 listing mismatches. `--k1/--k2` must equal 319/6492.
`--acq-id/--out-root` are runtime selectors (no freeze key). `--out-root` MUST resolve under
`workspace/` else exit 2. Post-validation Stage-1 bodies exit 3 `STAGE_BODY_PENDING_FREEZE`
with zero data contact (G1/G2 bodies belong to later freezes).

## Spec 6 — `SECURITY_MODEL.md` note + inventory skeleton (small: orchestrator may run direct)

Append section `## NB-Polar M2 CAL / prior accounting (CANDIDATE, descriptive)`. MUST state:
(1) the 32-frame CAL is SACRIFICED and excluded from the key denominator; (2) reveal bits
(~18–22, params·log2(n) order-of-magnitude) are diagnostic-only; (3) NO λ_prior term enters
λ_total; (4) claim scope unchanged (no composable net-key claim); (5) M2 is a CANDIDATE,
never the baseline. Inventory skeleton table columns: `message | producer | key-dependence |
size-bits | seed/mask/code | status`; rows at 0 bits for CAL frame list, fitted triple,
reveal bits, P16 orders, (K1,K2), Toeplitz tags. Point at the Release fail-closed exhaustive
public-message list as the shape pattern (`MACRO_PLAN_20260921.md` §9 F3).

## Acceptance IDs → evidence

S1-1 adapter+MOD (T1,T3): oracle-diff + MOD-diff reports. S1-2 M0 switch (T2): bit-exact log.
S1-3 metric contract (T4–T8): pytest log. S1-4 frozen untouched + no-import (T9,T10): pytest
log + `git diff --stat` + grep outputs. S1-5 re-split replay (T11): replay log (reviewer
recomputes K1/K2). S1-6 CAL note + skeleton: doc diff + main-thread doc review. S1-7 runner
contract (T12): `--help` + refusal demos (exit codes + stderr). S1-8 T0 green: full focused
pytest log, zero failures. Evidence paths reported per ID; "still incomplete" is not a report.

## Exact Stage-1 commands (repo `.venv`; `--authorized` NOT needed — no data, no decoder)

```
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
cat .git/HEAD  # expect: ref: refs/heads/codex/nbpolar-phase0
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_prior_m2.py -p no:cacheprovider -q
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python scripts/m2_prior_validation.py --help  # exit 0, no side effects
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python scripts/m2_prior_validation.py --selfcheck  # exit 0; exercises freeze-config/guard/out-root logic only
git status --porcelain -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/ scripts/ docs/SECURITY_MODEL.md
git diff --stat -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py comparison_bench/src/comparison_bench/formal_ir/nbpolar/algebra.py comparison_bench/src/comparison_bench/formal_ir/nbpolar/transform.py  # expect EMPTY
grep -rE "from.*nbpolar|import.*nbpolar|from \. |import \." comparison_bench/src/comparison_bench/formal_ir/prior_m2.py  # expect NO hits
```

## Stop rules + budget

Exceeding 300 s wall on the focused suite ⇒ STOP (blocker). Any §FORBIDDEN touch, any
`.ttbin`/protected read, any `sc_decode`/genie call, any post-freeze-style threshold/seed/K
choice ⇒ STOP + blocker. Ambiguity ⇒ STOP (second return condition), never guess.

## Return (exactly two)

1. All-complete: per-ID S1-1..S1-8 PASS with evidence paths + pytest log + `git status` snippet.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE
   decision needed from the main thread.

## Tasks (coder-agent order)

1. Implement `prior_m2.py` per Spec 1 + M0 switch per Spec 2 (S1-1, S1-2). 2. Write focused tests
   T1–T11 (S1-1..S1-5). 3. Re-split caller path + T11 replay, H-proportional absent (S1-5).
4. `SECURITY_MODEL.md` note + inventory skeleton per Spec 6 (S1-6; docs-small, may go direct).
5. Build runner per Spec 5 + T12 refusal demos (S1-7, S1-8). T2/T3/T4 scope only; G1/G2/G3 OUT.

## Frozen resolutions (report, do not smooth — parent §4 vs frozen conventions)

R1 placement: parent says "beside `nbpolar/prior.py`" (reads same-dir) vs brief "BESIDE (never
inside) `nbpolar/`". FROZEN: `formal_ir/prior_m2.py` (sibling of the package dir) — stricter wins.
R2 loopback vs no-decoder rule: T8 is metric-level, zero `sc_decode` calls in Stage 1.
R3 CLI: parent §5/§6 exact commands omit `--freeze-config` while the CLI CONTRACT mandates it.
FROZEN: `--freeze-config` REQUIRED on every stage invocation + flag cross-check (Spec 5).
R4 K: spec.md heading "constant-total" vs body "f=1.3 literal" vs D4 "neither frozen here".
FROZEN: `k_total` caller-supplied, no literal in code; 7053/7106 vs 1.2939/1.2952 DEFERRED.
R5 "incumbent table": bound to the P7 raw-MLE-plus-floor rule (S8 `fit_m0`), never λ-formula.
R6 MOD "frozen, not tunable": param exposed in API, value pinned by `mod_boundary` freeze.
