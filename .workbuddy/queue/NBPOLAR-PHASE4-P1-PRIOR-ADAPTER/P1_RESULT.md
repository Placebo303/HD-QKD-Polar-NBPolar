# P1 implementation return — PRIOR ADAPTER (operator report, NOT acceptance)

State: `BLOCKED` on a single frozen-requirement conflict (see section 4).
No self-acceptance; independent review (P1-5) owns the verdict.

## 1. Pre-EXECUTE self-check (all PASS before implementation)

- Branch: `codex/nbpolar-phase0` (working branch, no switch requested).
- Allow-list: `prior.py` imports NumPy + stdlib (`dataclasses`, `enum`,
  `numbers`) + local checks only; no pandas/parquet/decoder/benchmark/loader.
- Frozen contract versions read: `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`
  (116 lines, FREEZE_ACCEPT) + `openspec/changes/formal-ir-nbpolar-phase4-p0/`
  (proposal/design/tasks/specs).
- Authorization: `.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/STATUS.yaml`
  is `AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P1_IMPLEMENTATION`
  (documentation/implementation/phase4_p1 true, all else false).
- Target absence: `prior.py`, `test_nbpolar_prior.py`, P2 packet all absent.
- Synthetic-only plan; unrelated dirty files preserved (section 5).
- Environment note: repo `.venv` absent and system python3 lacks numpy;
  package installs are forbidden, so tests ran under the sibling checkout's
  interpreter (`../HD-QKD_Polar_Comparison/.venv/bin/python`, numpy 2.5.3)
  used as a runtime binary only — that checkout was not modified and none
  of its data was read.

## 2. Files (additive only; no Phase 1–3 / frozen file modified)

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py` (new,
  ~330 lines): `Conditioning` (`FULL_BOB_ONLY`), `Provenance`
  (`PRIOR_ONLY|ORACLE_CONDITIONED|CANDIDATE_CONDITIONED`), frozen
  `SymbolMetric`, helpers `smooth_joint_to_conditional`, `derive_p1`
  (`[U1,B]`), `derive_p2` (`[U1,B,U2]`), `build_p1_metrics`,
  `gather_p2_metrics` (no Alice input), `probs_to_symbol_metric`
  (`0→-inf`, row renorm), opt-in `apply_explicit_floor` (requires
  non-empty reason), `check_frame_ids_disjoint` (`lifecycle contract:`),
  local `split_symbol`/`combine_symbol` (design sec 3). Dual fallback:
  unseen-B → `p_global` (bit-exact assignment), zero-slice → uniform 1/32.
  Floor forbidden by default (no floor path in builders).
- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py`
  (minimal export add): `SymbolMetric`, `Conditioning`, `Provenance` + six
  pure functions. **This edit trips a frozen Phase-3 sentinel — section 4.**
- `comparison_bench/tests/test_nbpolar_prior.py` (new, 11 tests): synthetic
  fixtures + independent loop-based formula oracle + TEST-LOCAL oracle
  gather helper (asserted absent from `prior_mod`).
- `.workbuddy/queue/NBPOLAR-PHASE4-P2-CAL-DEV/` (new): `STATUS.yaml`
  all-false + unauthorized `TASK_PACKET.md`; no identities frozen.
- This file (`P1_RESULT.md`): operator evidence only.

## 3. Evidence

- V-P0-01–07: 11/11 green under plain python
  (`test_nbpolar_prior.py`: V01 transpose sentinel `f[33,7]=8/11` vs
  `f[7,33]=1/4`; V02 column sums ≤1e-12 incl `lambda=0`; V03 loop-oracle
  max-abs diff ≤1e-12; V04 `exp(logp)` round trip ≤1e-12; V05 zero→`-inf`;
  V06 exhaustive 32×32 packing + 12 selected 10-bit labels; V07 frame/pos
  permutation bit-exact) plus prefix-taxonomy, floor-opt-in, banned-twin
  source sentinel, decoder-free N=256 resource smoke (<60 s wall).
- Phase 1–3 regression (pytest, same interpreter):
  `test_nbpolar_transform + sc + construction + r1 + prior` → **65 passed,
  1 failed**: `test_nbpolar_construction.py::test_stream_and_oracle_isolation`
  asserts `hits == []` for pattern
  `polar_existing|from .prior|methods/nbpolar|protocol\.py|IRRunResult`
  over `synthetic.py, construction.py, __init__.py`; the required
  `from .prior import (` line in `__init__.py:19` is the sole hit.
- Banned twins never called: `build_f_model` / `prepare_model_f_prior` /
  `get_l1_app_prior_l2` / `app_fed_l2_prior` absent from `prior.py`
  (source-asserted in-test). No CAL/TTBin/real-data read, no Model-F/SC/
  decoder/benchmark/DEV/EVAL execution, no data-driven floor, no
  commit/push.

## 4. BLOCKED — single root cause (earliest gate)

**Conflict between two frozen requirements; unresolvable within operator
authority.** P1 requires the `__init__.py` export (`design.md` §7, packet
mission item 1, brief's "最小导出"), while frozen
`test_nbpolar_construction.py::test_stream_and_oracle_isolation`
(P3-T1-09, Phase 1–3 artifact) fails on any line matching `from .prior`
in `__init__.py`. Modifying that test is explicitly prohibited for P1.
Evasion-shaped workarounds (reworded/spaced imports, lazy `import_module`)
would pass the text scan while keeping the identical coupling and must
not be used; the failure is reported as-is.

**Single decision needed from main thread / planner:** either (a)
OpenSpec-sanctioned narrowing of the P3-T1-09 sentinel (e.g. apply the
`from .prior` alternative to `synthetic.py`/`construction.py` only, keep
`__init__.py` scanned for the remaining alternatives), or (b) a ruling
that the P1 export lives elsewhere (contradicts design §7; needs an
OpenSpec update). Implementation resumes after that ruling; no other work
is pending for a COMPLETE re-run.

## 5. Scope preservation

`git status`: only additive paths added (`formal_ir/nbpolar/prior.py`,
`tests/test_nbpolar_prior.py`, P2 packet dir, this file) plus the minimal
`__init__.py` export edit inside the already-untracked `nbpolar/` dir.
No tracked Phase 1–3, frozen-artifact, or unrelated file touched.
