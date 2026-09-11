# Design: `nbpolar-phase0-freeze` (doc-only Phase0 slice)

## Context

Parent: `openspec/changes/formal-ir-nbpolar-mvp/` (Phase0–2 implementation owner) + `docs/nbpolar/` (7 plan files) + `docs/research_cycles/NBPOLAR-PHASE0/` (4 packet files). Reviewer: PASS with comments on candidate A. This change freezes Phase0 document alignment only.

## D1 — Granularity (slice, not duplication)

- This change OWNS: freeze-review checklist, 3-blocker intents, audit commands, ACCEPT/BLOCKED verdict.
- MVP OWNS: all Phase0–2 `.py` implementation and its tests. This change SHALL NOT restate MVP tasks as its own implementation tasks.
- Anti-creep rule: any sentence containing code creation (`algebra.py`, `transform.py`, `sc.py`, `methods/nbpolar.py`), Model-F execution (`counts_ab`/CAL/TTBin), decoder/SCL/rate-scan execution, or result-root creation is scope creep and SHALL be deleted or moved to MVP Phase1+ review, never completed here.

## D2 — Literature (F1): count 3→2 with explanation (Recommended)

- Observed: `rg` over `docs/nbpolar/` hits Mori-Tanaka + Bravo-Santos only; Park-Barg zero hits. Some review context assumed 3 references.
- Decision: state explicitly in `ARCHITECTURE.md` §Mathematical references that the Phase0 freeze rests on **2 references** (Mori-Tanaka arXiv:1211.5264 for the 2×2 kernel primitive-alpha condition; Bravo-Santos arXiv:1511.03881 for q-ary source polarization + LR-vector SC). Add one sentence: "A third Park-Barg citation is not a Phase0 dependency; if construction-phase work later needs it, a separate review will add the exact ID + use statement."
- Rejected alternative: inserting a Park-Barg citation + use claim without a read source — rejected because it would fabricate provenance for a freeze gate.
- Verification: `rg -n "Park|Barg|Mori|Bravo" docs/nbpolar/` must show exactly Mori + Bravo after intent (Park only in the explicit non-dependency sentence).

## D3 — Path discipline (F2): relative POSIX intent map

| File:line | Current | Intent |
|---|---|---|
| `docs/nbpolar/DOCUMENT_INDEX.md:4` (ownership) | `D:\Code\HD-QKD_Polar_Comparison-nbpolar` | `docs/nbpolar/` is canonical home of this worktree; sibling checkouts named only as provenance |
| `docs/nbpolar/README.md:38-39` (ownership boundary) | `D:\Code\HD-QKD_Polar_Release` | `../HD-QKD_Polar_Release` read-only baseline/provenance; new code only under this worktree's `comparison_bench/` |
| MVP `design.md:35-36` (implementation scope) | `D:\Code\...` absolute | Same POSIX rule; recorded as known pre-existing debt acknowledged by this freeze, fixed in the post-ACCEPT docs commit |
| Packet `EXECUTION_PACKET.md:18` (forbidden scope) | `D:\Code\HD-QKD_Polar_Release` | `../HD-QKD_Polar_Release`; same POSIX rule, fixed in the post-ACCEPT docs commit |
| Packet `REVIEW_ENTRYPOINT.md:5` / `PHASE0_PROMPT.md:3` (repo/branch lines) | `D:\Code\...` absolute | Same POSIX rule; recorded as known pre-existing debt acknowledged by this freeze, fixed in the post-ACCEPT docs commit |
| `docs/nbpolar/ARCHITECTURE.md:30-39` (module layout) | already relative POSIX | Not a fix target — zero `D:\` hits confirmed by the F0-2 audit |
| `openspec/project.md` provenance citations | `D:/Code/...` absolute | Keep as provenance citations only (per project.md §Inherited roadmap); NOT new defaults — no change required, explicitly noted |

Verification: `rg -n "D:\\\\|D:/" docs/nbpolar/ openspec/changes/formal-ir-nbpolar-mvp/ docs/research_cycles/NBPOLAR-PHASE0/` — after intent, zero hits except explicitly marked provenance citations.

## D4 — 1e-12 reproducibility (F3): frozen semantics

- **Tolerance**: every `1e-12` in ROADMAP/VALIDATION (mapping, prior normalization, D4R2 agreement, SC conditional) means **absolute tolerance**: `max|a-b| <= 1e-12`. No relative tolerance, no norm-averaging. `1e-9` finite log-score gate likewise absolute.
- **float64-ln vs bits**: internal metric is float64 natural log (`logp = ln P`, `logsumexp(row)=0`). Entropy/disclosure convert at the report boundary only (`bits = nats/ln2`); `L_static = 5 × disclosed GF32 coords`, `L_keydep = L_static + 64`. Exact-zero support is `-inf`; numeric floors declared separately from statistical smoothing.
- **D4R2 provenance (formula only, not evidence)**: concentration formula `(counts + lambda*p_global)/(n_b + lambda)` per-column over Bob, from `comparison_bench/src/comparison_bench/formal_ir/v72p2d4r2_cal_gf32_model_rate_audit.py:329` (`build_f`; `p_global=counts.sum(axis=1)/n`, `n_b=counts.sum(axis=0)`, `(counts+lam*p_global[:,None])/(n_b[None,:]+lam)` at :346-349); reference numbers from `docs/research_cycles/V72P2D4-CAL-RATE/RESULT_SUMMARY_R2.md:21-28` (inner `selected_lam=137.3823795883264` at :21; CE means L1 3.814742/L2 3.347605/total 7.162347 at :28; :17 is the synthetic-repro fixture 6.422161/5.083351/11.505513, not the CE source; sibling Comparison provenance). Phase0 freeze pins the **formula + tolerance**, NOT the numbers as NB-Polar results. Exact D4R2 file revision pinning stays open (see Unresolved).
- Pure-array recalc in tasks uses **synthetic tiny inputs only** (e.g. 3×3 counts), never CAL/real data, to prove formula/axis semantics without Model-F execution.

## D5 — Isolation (ban list, verbatim)

> H1/H2/H_inc, PEG/QC/degree, BP/schedule/seeds, H[:k] disclosure, LDPC leakage formula, Cascade parity/bisection/look-back, binary XOR/PW/BSC-LLR/CA-SCL-CRC, polar_existing作q-ary后端禁用

Enforcement: task F0-5 runs ban-list `rg` over the freeze scope statement; any hit in NB-Polar normative text (outside the ban list itself and ASSET_MAP §Do not reuse) = FAIL. `polar_existing` bridge stays a binary-Polar read path; using it as a q-ary backend is explicitly forbidden.

## D6 — Six-task freeze structure

Each task binds: frozen inputs (exact files), exact command (`rg` / `python -c` read-only, no file writes outside the change dir), budget (wall-clock, no execution), return artifact (checklist record), stop rule (PASS→next / FAIL single-root BLOCKED). Global stop: any task FAIL → whole freeze BLOCKED with the single failing command + error + one needed decision; no auto-advance to Phase1. Any code/Model-F clause discovered mid-review is stripped as creep, not completed.

## Unresolved (NOT decided by this change; carried as open items)

1. **Thresholds**: `1e-12`/`1e-9` absolute gates are frozen as syntax; whether they are the right tightness for GF32 SC at N≥256 is Phase1-2 empirical business (MVP owns).
2. **D4R2 version pin**: exact sibling file revision/SHA for `build_f` + `RESULT_SUMMARY_R2.md` not pinned in this worktree (sibling read-only); post-ACCEPT docs commit records the observed revision string without importing code.
3. **Seeds**: Phase0 needs no seeds (no stochastic execution); construction/decoder seeds remain MVP Phase2+ frozen-packet business.
