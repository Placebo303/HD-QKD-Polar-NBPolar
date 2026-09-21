# Stage-1 Focused Review Record — NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION

Reviewer: reviewer-go (independent subagent, session `ses_f3c4b141affeUIS1KSvFzxHqqW`), read-only except `workspace/.tmp_review_m2/` (created, verified, cleaned).
Branch `codex/nbpolar-phase0` verified (`ref: refs/heads/codex/nbpolar-phase0`). Packet `TASK_PACKET.md` Specs 1–6, R1–R6. Sibling venv used. Record persisted 2026-09-21 by main thread.

## Per-check (A–H)

**A. Focused evidence re-run — PASS**
- `pytest comparison_bench/tests/test_nbpolar_prior_m2.py -p no:cacheprovider -q`: `21 passed` in ~6.7s, exit 0. Independently reproduced.
- `scripts/m2_prior_validation.py --help`: exit 0, no side effects.
- `--selfcheck`: exit 0, `12/12 PASS` + `SELFCHECK_PASS`.
- `git diff --stat -- .../nbpolar/sc.py algebra.py transform.py`: empty.
- `grep -rE "from.*nbpolar|import.*nbpolar|from \. |import \." .../prior_m2.py`: no hits (exit 1). AST scan: only `__future__`, `numbers`, `numpy`.
- Scoped `git status` for 4 packet files: `M docs/SECURITY_MODEL.md`, `M scripts/m2_prior_validation.py`, `?? .../prior_m2.py`, `?? .../test_nbpolar_prior_m2.py` — exactly the claimed 4.

**B. Adapter Spec 1 — PASS**
- Signatures match: `fit_m2_triple(counts_ab,*,mod)`, `build_m2_joint(q0,q+1,q-1,*,mod,floor=1e-15)`, `build_m0_joint(counts_ab)`, `build_prior(*,mode,mod)`, `split/combine_symbol`, `prob_rows_to_logp`. Verified via `inspect.signature`.
- Constants literal: `N_LABELS=1024`, `Q_SYMBOL=32`, `FLOOR=1e-15`, `MODES=(LINEAR_ONLY,CIRCULAR)`, `DEFAULT_MOD=LINEAR_ONLY`.
- `fit` LINEAR_ONLY excludes exactly `(0,1023)` from `n_plus`, `(1023,0)` from `n_minus`; `build_m2_joint` zeroes those wrap cells pre-floor, then `maximum(floor)` + per-B-column renorm; `floor !=1e-15` → `ValueError("m2 contract:…")`.
- `build_m0_joint`: raw-MLE per-B-column, empty column → `1/1024`, then `maximum(FLOOR)` + renorm. No λ/p_global/concentration code (only docstring "NEVER the lambda…" comment).
- `build_prior` exact `M2/M0`, M0 ignores MOD, unknown → `ValueError`. Packing `(s&31,(s>>5)&31)`, `s=low+32*high` exhaustive 0..1023 verified. `prob_rows_to_logp`: `0→-inf` else `ln p` minus row logsumexp, max|lse| ~1e-15 ≤1e-12, no NaN/+inf. All errors prefixed `m2 contract:`. No `nbpolar/` imports (grep+AST). `numpy+stdlib` only.

**C. Spec 2 bit-exactness — PASS (independent)**
- Own scratch reimplementation (delta-matrix+bincount oracle for M2, literal S8 `fit_m0` for M0, zero cells + empty col 700 fixture): M0 `max-abs-diff==0.0`, `array_equal` true, M0 MOD-ignored diff `0.0`; M2 oracle diff `0.0` both MODs; T3 changed cols `[0,1023]`, untouched 1022 cols `0.0`, wrap toggle true, fit ints `10/4/3/31` vs `10/11/8/31`. Confirms operator S1-1/S1-2.

**D. Spec 3 K re-split — PASS**
- `select_empirical_split` IMPORTED in test from `nbpolar.empirical_genie_scaling`, never reimplemented; absent from `prior_m2.py` and runner (grep exit 1).
- Test feeds hand-built e/h vectors (no genie/SC), literal worst-first `(e,h,index)` + exhaustive K1 enumeration, `k_total ∈ (0,5,2n-1,2n)` with `n=16` ≡ `{0,5,31,32}` — matches S1-5 claim spelling.
- `k_total` no literal in module/runner (grep `7053/7106/1.2939/1.2952` exit 1). `proportional` case-insensitive absent in both files.

**E. Spec 5 runner contract — PASS (all refusal demos independently reproduced)**
- `--authorized` `action="store_true"` (AST), absent → exit 2 before any read/create (verified empty dir).
- `--freeze-config` REQUIRED with stage flag → exit 2; 19 keys exact sorted match to packet list; missing 2 → exit 2 listing exactly `delta_min, tag_master`; null `B_tail` → exit 2; never defaults.
- Exactly-one-of `--stage-g1-nll/--stage-g2-decode/--selfcheck` → exit 2 on 0 or 2.
- Flag↔key 8-map exact, mismatch (`501` vs `500`) → exit 2 naming `pairing_window_primary`. `--k1/--k2` pinned `319/6492` (bad `320` → exit 2 naming `319`). `--out-root` dual guards: forbidden `results/`/`outputs_comparison/` + must-resolve-under-`workspace/`; `/tmp/...` refused exit 2 creating nothing.
- Post-validation G1/G2 → exit 3 `STAGE_BODY_PENDING_FREEZE`, zero creation (verified both). Bodies contain no pairing/NLL/decode science, only print+return 3. `main(argv=None)` + `__main__` guard, repo-root `sys.path.insert(0,…)`, top imports stdlib+numpy only, YAML/TimeTagger/`src.qkd_io` deferred; `_ensure_timetagger_shim` defined never called at Stage-1 import; import in fresh cwd creates nothing.

**F. Spec 6 doc note — PASS**
- `git diff --stat`: `+39` lines only. Section `## NB-Polar M2 CAL / prior accounting (CANDIDATE, descriptive)` states: (1) 32-frame CAL sacrificed + excluded from denominator, (2) reveal ~18–22 diagnostic-only never leakage, (3) no λ_prior in λ_total, (4) claim scope unchanged, (5) M2 CANDIDATE. Inventory header `message|producer|key-dependence|size-bits|seed/mask/code|status` + 6 rows at 0 bits (CAL list, triple, reveal, P16 orders, (K1,K2)=(319,6492), Toeplitz tags) with specified statuses; points at Release list pattern `MACRO_PLAN §9 F3`.

**G. Scope cleanliness — PASS**
- Frozen `src/experiments/tools/results/.../nbpolar/` untouched: `git diff --stat` for `nbpolar/` empty; `git status` for those dirs shows only pre-existing `outputs_comparison/test_fixtures/...csv` stat-dirty with empty content diff (`H` cached normal, `SHOW HEAD` 2-line fixture) — no content change.
- No protected/`.ttbin`/decoder contact: `prior_m2` zero hits for `sc_decode/genie/TimeTagger/ttbin/FileReader`; runner shim text only, never invoked. No `sha/atomic/lock/retry/checksum` (grep exit 1). Writes only under `workspace/` (runner refuses otherwise; tests use `workspace/.tmp_stage1` auto-cleaned; reviewer `workspace/.tmp_review_m2` cleaned).
- OpenSpec creep: T5–T8/G1/G2/G3 OUT respected — runner has guards+exit-3 only, `prior_m2` docstring G1/G2 mention is MOD-freeze semantics only, no K/G/NLL/FER science.

**H. Test-coverage T1–T12 — PASS**
- 21 `def test_*`: T1–T11 each one fn + T12a–T12j ten fns. Covers oracle ≤1e-12, bit-exact, MOD toggle+fit ints, logp norm, zero→-inf, packing exhaustive, equivariance, loopback decoder-free, frozen untouched, no-import AST+grep, K replay + H-absent, runner help/missing/null/no-auth/store_true/import-free/k-pin/exit3/cross-check/out-root/mutual-exclusion/selfcheck. Packet "T1–T11 vs T12" wording both covered.

**S1-1..S1-8:** S1-1 PASS, S1-2 PASS, S1-3 PASS, S1-4 PASS, S1-5 PASS, S1-6 PASS, S1-7 PASS, S1-8 PASS.

## Operator concerns (4)

1. **T3 "exactly 2 cells" pre- vs post-floor — ACCEPTABLE.** Frozen Spec-1 sentence is pre-floor; post-renorm spread within cols 0/1023 is mathematically necessary. Test header documents this and asserts the checkable form (1022 cols bit-identical + wrap toggle + exact-int attribution); independently confirmed.
2. **T9 bare-`M2` allowlist — ACCEPTABLE.** Exactly two `M2_prefix` lines in `empirical_diagnostic.py:362,401`, pre-existing at `faac0411`, file `git diff/status` empty; `prior_m2` zero hits; non-allowlisted `M2` zero hits. `.pyc` binary hit irrelevant. Pinning allowlist vs touching frozen file is correct.
3. **`--selfcheck` `stubs-raise` → `stage-bodies-exit3` — ACCEPTABLE.** Spec 5 mandates exit-3 bodies so old check could not exit 0. Selfcheck correctly asserts `rc==3` + `STAGE_BODY_PENDING_FREEZE` + no creation. Leftover fn name `t_stubs_raise_not_implemented` is stale label only (see non-blocking).
4. **Pre-existing tree dirt — ACCEPTABLE (not packet fault).** `.codebuddy/memory/2026-09-19.md` (+11 P20 note), csv stat-dirty, `?? .codebuddy/memory/2026-09-21.md`, `?? .workbuddy/memory/` lie outside packet scope and were left untouched; scoped 4-file status matches. Do not accept them as part of this packet.

## Verdict

```
Verdict: pass with comments
```

**Blocking Issues:** None. No forbidden touch, data contact, decoder call, or semantic violation found.

**Non-Blocking Suggestions:**
- Rename `t_stubs_raise_not_implemented` in runner selfcheck + test comment to `t_stage_bodies_exit3` to match asserted behavior (cosmetic).
- Document the extra `_out_root_refusal` forbidden-tree guard as additive to Spec-5 `workspace/` confinement (already consistent with AGENTS.md output policy, just note it).
- `STATUS.yaml` still `pending` on all S1-* — correctly left for main-thread acceptance; do not have operator self-accept.
- CSV `M` with empty `git diff` is stat/mode quirk only; leave untouched.
