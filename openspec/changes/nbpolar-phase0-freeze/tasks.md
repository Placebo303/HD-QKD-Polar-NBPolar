# Tasks: `nbpolar-phase0-freeze` (6 doc-only freeze tasks)

Global rules: no `.py` created/modified; no Model-F/CAL/real-data/decoder/SCL execution; no result root; no sibling edits. Each task lists frozen inputs, exact command, budget, return artifact, stop rule. Any code/Model-F clause found is scope creep → strip, do not implement. Overall PASS → Phase1 judgment unlocked; any FAIL → whole freeze BLOCKED with single root cause.

## F0-1 — Literature disposition (F1)

- Frozen inputs: `docs/nbpolar/ARCHITECTURE.md:70-83`, `docs/nbpolar/ROADMAP.md`, this change `proposal.md:18-22` (Freeze-blocker statement recording the Park-Barg zero-hit).
- Exact command: `rg -n "Park|Barg|Mori|Bravo|1211.5264|1511.03881" docs/nbpolar/` (read-only audit).
- Budget: ≤15 min wall; no execution, no citation fetching beyond confirming the two arXiv IDs already in text.
- Return artifact: checklist record `F0-1: <rg hit summary> + intent=count-3→2-with-nondep-sentence` (recorded in review verdict, no doc edit in this change).
- Stop: PASS (hits = Mori+Bravo only, intent sentence fixed) → F0-2. FAIL (a third citation claim appears without source, or Park-Barg silently required as dependency) → BLOCKED(single root: literature provenance).

## F0-2 — Path-discipline audit (F2)

- Frozen inputs: `docs/nbpolar/DOCUMENT_INDEX.md:4`, `docs/nbpolar/README.md:38-39`, `openspec/changes/formal-ir-nbpolar-mvp/design.md:35-36`, `docs/research_cycles/NBPOLAR-PHASE0/EXECUTION_PACKET.md:18`, `docs/research_cycles/NBPOLAR-PHASE0/REVIEW_ENTRYPOINT.md:5`, `docs/research_cycles/NBPOLAR-PHASE0/PHASE0_PROMPT.md:3`, `AGENTS.md:§5.4`. (`docs/nbpolar/ARCHITECTURE.md:30-39` is already relative POSIX — zero `D:\` hits, not a fix target.)
- Exact command: `rg -n "D:\\\\|D:/" docs/nbpolar/ openspec/changes/formal-ir-nbpolar-mvp/ docs/research_cycles/NBPOLAR-PHASE0/` (read-only).
- Budget: ≤15 min wall; no file moves.
- Return artifact: checklist record `F0-2: <hit list> + POSIX intent map per design.md D3` (edits deferred to post-ACCEPT docs commit).
- Stop: PASS (all hits triaged as fix-intent or marked provenance-citation) → F0-3. FAIL (a Windows absolute path remains as a new default outside provenance) → BLOCKED(single root: path discipline).

## F0-3 — 1e-12 reproducibility freeze (F3)

- Frozen inputs: `docs/nbpolar/ROADMAP.md:18-21,57-59,80-83`, `docs/nbpolar/ARCHITECTURE.md:95-107`, `docs/nbpolar/VALIDATION_GATES.md:28-30`, `docs/nbpolar/ASSET_MAP.md:9`, sibling provenance `docs/research_cycles/V72P2D4-CAL-RATE/RESULT_SUMMARY_R2.md:21-28` (inner `selected_lam` at :21, CE means at :28; :17 is the synthetic-repro fixture, not the CE source) + `comparison_bench/src/comparison_bench/formal_ir/v72p2d4r2_cal_gf32_model_rate_audit.py:329` (`build_f`) (cited, not executed).
- Exact command: `rg -n "1e-12|1e-9|logsumexp|float64|ln|log2|nats|bits" docs/nbpolar/` (inventory sweep; hits triaged per design.md D4, not every hit is a gate) plus read-only recite of abs-tol + ln-vs-bits + D4R2 file/line table from design.md D4 (no CAL load, no real data).
- Budget: ≤20 min wall; no numeric execution beyond reading.
- Return artifact: checklist record `F0-3: abs-tol + ln-internal/bits-report + D4R2 provenance table confirmed`.
- Stop: PASS (tolerance kind, ln/bits boundary, formula provenance all explicit) → F0-4. FAIL (any 1e-12 without abs-tol kind, or D4R2 numbers claimed as NB-Polar evidence) → BLOCKED(single root: reproducibility).

## F0-4 — Pure-array semantic recalc (synthetic tiny inputs only, no Model-F)

- Frozen inputs: `docs/nbpolar/README.md:21-28` (A=32*high+low), `docs/nbpolar/ARCHITECTURE.md:95-107` (logp norm), `docs/nbpolar/ASSET_MAP.md:9` (concentration formula shape).
- Exact commands (read-only, no repo writes, synthetic inputs only):
  - `python -c "import numpy as np; A=np.arange(1024); assert all((32*(a//32)+(a%32))==a for a in A); print('packing round-trip 0..1023 OK')"`
  - `python -c "import numpy as np; rng=np.random.default_rng(0); L=rng.normal(size=(4,32)); L-=np.logaddexp.reduce(L,axis=1,keepdims=True); assert np.allclose(np.logaddexp.reduce(L,axis=1),0,atol=1e-12); print('logsumexp norm OK')"`
  - `python -c "import numpy as np; c=np.array([[3.,1.],[0.,2.]]); lam=1.5; pg=c.sum(axis=1)/c.sum(); n=c.sum(axis=0); f=(c+lam*pg[:,None])/(n+lam); assert f.shape==(2,2) and np.allclose(f.sum(axis=0),1,atol=1e-12); print('concentration column-norm OK (synthetic)')"`
- Budget: ≤20 min wall total; stdlib+numpy only (numpy from root `requirements.txt`; pure-python fallback if the review container lacks numpy); any CAL/TTBin/real-data load attempt aborts the task as creep.
- Return artifact: checklist record `F0-4: 3 one-liner outputs pasted (or single failing line)`.
- Stop: PASS (all three OK) → F0-5. FAIL (any assert/nonfinite, or axis ambiguity found) → BLOCKED(single root: array semantics — packing vs axis vs normalization, named exactly).

## F0-5 — Ban-list isolation audit (verbatim list)

- Frozen inputs: `docs/nbpolar/ASSET_MAP.md:35-45`, this change `proposal.md` Scope + `design.md` D5, `docs/nbpolar/ARCHITECTURE.md:150-156`, `docs/nbpolar/CRITICAL_PATH.md`.
- Exact command: `rg -n "H1|H_inc|PEG|QC|degree|BP|schedule|seed|H\[:k\]|leakage|Cascade|parity|bisection|look-back|XOR|\bPW\b|BSC|LLR|CA-SCL|CRC|polar_existing" docs/nbpolar/ openspec/changes/nbpolar-phase0-freeze/` then triage each hit as (a) inside the ban list itself, (b) ASSET_MAP §Do-not-reuse / boundary prose, or (c) normative reuse — (c) is forbidden.
- Budget: ≤20 min wall; read-only.
- Return artifact: checklist record `F0-5: <hit triage table> + zero normative-reuse statement`, quoting the verbatim ban list: H1/H2/H_inc, PEG/QC/degree, BP/schedule/seeds, H[:k] disclosure, LDPC leakage formula, Cascade parity/bisection/look-back, binary XOR/PW/BSC-LLR/CA-SCL-CRC, polar_existing作q-ary后端禁用.
- Stop: PASS (zero category-(c) hits; polar_existing only as binary read path, never q-ary backend) → F0-6. FAIL (any normative reuse / q-ary-backend claim / code clause) → BLOCKED(single root: isolation breach, quoted line).

## F0-6 — Freeze verdict (ACCEPT vs BLOCKED)

- Frozen inputs: F0-1..F0-5 checklist records + `docs/research_cycles/NBPOLAR-PHASE0/cycle_state.yaml` (still PLAN_CANDIDATE, all execution flags false) + `docs/decision-log.md` boundary entries.
- Exact command: `cat docs/research_cycles/NBPOLAR-PHASE0/cycle_state.yaml` + `rg -n "plan_accepted|implementation_authorized|decoder_executed|result_created" docs/research_cycles/NBPOLAR-PHASE0/cycle_state.yaml` (read-only aggregation check); verify `cycle_state.yaml` still shows `plan_accepted:false`, `implementation_authorized:false`, `decoder_executed:false`, `result_created:false`.
- Budget: ≤15 min wall.
- Return artifact: verdict record `FREEZE_ACCEPT → Phase1 judgment unlocked` OR `BLOCKED(<single root cause + failing command/error + one needed decision>)`. No `run_01`, no result commit.
- Stop: PASS → Phase1 (MVP implementation judgment) may be scheduled as a separate authorized change. FAIL → remain BLOCKED; fix the single named root cause and re-review; never publish-then-patch.
