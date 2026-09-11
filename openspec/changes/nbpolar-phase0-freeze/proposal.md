# Change `nbpolar-phase0-freeze` — doc-only Phase0 freeze-review

## Status

`FREEZE_ACCEPT / IMPLEMENTATION_NOT_AUTHORIZED / EXECUTE_NOT_AUTHORIZED` —
accepted document freeze. No decoder, Model-F, real-data, or qualification
authorization.

## Granularity declaration (anti-duplication, frozen)

This change is a **doc-only freeze-review of the `formal-ir-nbpolar-mvp` Phase0 packet slice**. It is NOT a new large change and does NOT duplicate the MVP.

- Parent/source of truth: `openspec/changes/formal-ir-nbpolar-mvp/` (Phase0–2) plus `docs/nbpolar/` (7 files) plus `docs/research_cycles/NBPOLAR-PHASE0/` packet (4 files).
- This change adds **no `.py`, no Model-F, no real-data, no decoder execution, no result root, no duplication** of MVP Phase1/2 implementation tasks.
- Any code / Model-F / decoder / real-data clause appearing in review is **scope creep and SHALL be stripped** before Freeze ACCEPT.
- MVP remains the implementation owner for Phase0–2 code; this change only freezes the Phase0 document/alignment gate so Phase1 can be judged.

## Problem

The first review returned **needs changes** on four blocking details. After
repair, the second review returned **PASS with comments**; the current-tree
independent recheck records `FREEZE_ACCEPT`. The three post-ACCEPT alignment
items were:

1. **Literature**: Park-Barg has zero hits in `docs/nbpolar/`; either add citation + use statement, or correct count 3→2 with explanation.
2. **Path discipline**: `ARCHITECTURE.md:35`, `DOCUMENT_INDEX.md:4`, `README.md:38-39` (and MVP `design.md:35-36`, packet files) use `D:\Code\...`; must become relative POSIX (`comparison_bench/...`, sibling only as provenance).
3. **1e-12 reproducibility**: freeze packet must state abs-tol, float64-ln vs bits, and D4R2 exact file/line.

## Proposal

Freeze-review the Phase0 alignment packet (GF32/poly37/alpha2 contract, row-vector orientation, natural order, probability axis, Model-F concentration-smoothing formula reference, `d`/`q`/`N` units, source-disclosure semantics, CAL/DEV/EVAL boundary, verification protocol) through 6 doc-only tasks, each bound to frozen inputs + exact command + budget + return artifact + stop rule. PASS unblocks Phase1 judgment; FAIL stops with a single root cause as BLOCKED.

## Scope

In scope (doc-only):

- Disposition of the 3 Freeze blockers as document intents (file:line intent, no code edits in this change).
- `rg` audits (literature hits, Windows-path hits, ban-list hits) and pure-array recalculations (mapping round-trip, normalization, concentration-formula semantics on synthetic tiny inputs — no CAL/real data).
- Freeze-review checklist + ACCEPT/BLOCKED verdict record.

Out of scope (explicitly excluded; any such clause is scope creep):

- New/modified `.py` under `comparison_bench/`, `src/`, `experiments/`, `tools/`; no `algebra.py`/`transform.py`/`sc.py` implementation (MVP Phase1/2 owns it).
- Model-F fitting/loading (`counts_ab`, CAL frames, TTBin), real-data decoder calls, SCL, puncturing/shortening, rate scans, performance/qualification/promotion claims.
- Modifications to `results/`, `comparison_bench/outputs_comparison/`, frozen baseline, or the three sibling checkouts.

Isolation ban list (verbatim, SHALL NOT enter NB-Polar even by reference as implementation):

> H1/H2/H_inc, PEG/QC/degree, BP/schedule/seeds, H[:k] disclosure, LDPC leakage formula, Cascade parity/bisection/look-back, binary XOR/PW/BSC-LLR/CA-SCL-CRC, polar_existing作q-ary后端禁用

Full form in `docs/nbpolar/ASSET_MAP.md` §Do not reuse remains binding.

## Three-fix disposition (file:line intent — detail in design.md)

| # | Fix | Intent (this change proposes intent; edits land as a later docs commit after ACCEPT) |
|---|---|---|
| F1 | Literature | `docs/nbpolar/ARCHITECTURE.md` §Mathematical references: adopt **count 3→2 with explanation** (Recommended): keep Mori-Tanaka (kernel condition) + Bravo-Santos (source-polarization/SC); explicitly state Park-Barg is NOT a Phase0 dependency, deferred to Phase3-construction review if ever needed. Alternative (add Park-Barg citation + use) rejected for this freeze to avoid inventing an unread citation. |
| F2 | Paths | `docs/nbpolar/DOCUMENT_INDEX.md:4`, `docs/nbpolar/README.md:38-39`, MVP `design.md:35-36`, packet `REVIEW_ENTRYPOINT.md:5`/`PHASE0_PROMPT.md:3` repo/branch lines, packet `EXECUTION_PACKET.md:18`: replace `D:\Code\...` with relative POSIX (`comparison_bench/...`, `docs/...`, `openspec/...`); siblings named only as provenance (`../HD-QKD_Polar_Comparison`, `../HD-QKD_Polar_Release` — no code dependency). (`docs/nbpolar/ARCHITECTURE.md:30-39` is already relative POSIX — not a fix target.) |
| F3 | 1e-12 | Freeze packet (this change `design.md` + MVP packet reference): **abs-tol** for all `1e-12` checks (`abs(a-b) <= 1e-12`, no rel-tol); **float64 `ln` internally, bits only for entropy/disclosure reporting** (`log2 = ln/ln2` at report boundary); **D4R2 exact provenance**: `comparison_bench/src/comparison_bench/formal_ir/v72p2d4r2_cal_gf32_model_rate_audit.py:329` (`build_f`, `(counts+lambda*p_global)/(n_b+lambda)`) + `docs/research_cycles/V72P2D4-CAL-RATE/RESULT_SUMMARY_R2.md:21-28` (inner `selected_lam=137.3823795883264` at :21; CE means L1 3.814742/L2 3.347605/total 7.162347 at :28; :17 is the synthetic-repro fixture 6.422161/5.083351/11.505513, not the CE source) — cited as formula provenance only, NOT as NB-Polar evidence; D4R2 version/seed pinning stays an open item. |

## Affected specs

- Delta: `specs/freeze-review/spec.md` (new; freeze-review gate requirements only).
- No merge into `openspec/specs/` at propose time. MVP specs untouched.

## Acceptance (Freeze ACCEPT gate)

- [x] 6 tasks all PASS with frozen-input/command/budget/artifact/stop records.
- [x] F1–F3 intents unambiguous and landed in the canonical documents.
- [x] Ban-list `rg` audit has zero normative-reuse hits; no code/Model-F clause remains.
- [x] Verdict recorded as `FREEZE_ACCEPT → Phase1 judgment unlocked`.
- [x] No `.py`, result root, raw input, or sibling modification created by this change.
