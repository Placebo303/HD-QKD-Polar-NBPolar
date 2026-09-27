# TASK PACKET — NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT (preregistered cap + per-block λ decomposition)

**GATED PACKET. This packet authorizes NOTHING.** Execution requires the main thread to paste
`AUTHORIZATION_PROMPT.md` **verbatim** (AGENTS.md §10.1); until then `STATUS.yaml` stays
`stage: PACKET_DRAFT` / `authorizations: []` and **no Stage-3 work of any kind may be performed**
(not even a path-existence listing). One complete frozen packet before delegation; the operator
never marks its own work accepted.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT/`
- Change: `openspec/changes/archive/2026-09-22-nbpolar-prior-rebaseline/` — D6 **Stage-3
  measurement set** (preregistered cap + per-block λ decomposition), the D6 gate parallel to G4
  and explicitly carved out of G4 (G4 TASK_PACKET.md § Scope boundary + Main-thread adjudication
  2026-09-22 item 2). Nature: **claim-bearing precondition measurement set; no decode re-run,
  no frozen-constant change**.
- Venv (for the packet-local builder only, if authorized): same convention as G4
  (`/home/karel_303/.venvs/timetagger/bin/python`) — TO-CONFIRM at freeze; no other interpreter.
- Nature: **Tier-Y one-shot RECORD/MEASURE gate**. No decoder, no SC call, no tag generation,
  no raw-data read, no re-derivation of any frozen constant, no re-run of G2/G3 decode.
  Stage-3 measures **already-executed, already-adjudicated** G2/G3 per-block disclosure under the
  frozen M2 contracts and compares it against a **preregistered cap** under a frozen comparison
  caliber. It changes no decode conclusion and produces no FER/efficiency claim by itself.
- M2 state at dispatch (STATE.md §4.1): `VALIDATED_AT_FROZEN_CONTRACT` (2nd rung; R2 FER gate
  and R3 efficiency gate NOT done; G4 COMPLETE required as precondition — see Authorization).

## Goal

Produce ONE preregistered, countable, artifact-traceable measurement set covering:

1. **Per-block λ decomposition** over the frozen G2 + G3 `per_block_outcomes.jsonl` rows:
   per-block disclosure bits decomposed into frozen accounting columns (key-dependent /
   public-control / CAL-sacrifice handling / reveal-bits diagnostic / tag record /
   `undetected` isolation row), each row traceable to `path + field locator + value as-is`.
   Decomposition caliber (exact column list, formula, Müller eq 11/13 substitution
   `H(q) → empirical H(X|Y)`) is a **TO-FREEZE** item (§ Decomposition caliber); the operator
   computes only the frozen caliber, never an ad-hoc variant.
2. **Preregistered cap declaration + comparison**: ONE cap object recorded in
   `s3_freeze_config.json` BEFORE any computation (numeric value or closed-form formula with
   all inputs bound to frozen artifacts), plus a frozen comparison caliber
   (per-block vs cap: pass/count rule, aggregation rule, `undetected` handling).
   **Cap definition caliber is TO-FREEZE** — no existing frozen numeric basis was found in
   D6 / spec validation-gates / STATE §4.1 (D6 names only "preregistered cap"; see Open
   questions Q1). The operator sets no number; a missing/null cap ⇒ hard STOP.
3. **Numeric consistency**: disclosure sums cross-checked against the frozen per-stage
   recount (G2 and G3 each: key 1,432,998 = 34,119×42; public 13,765,206 = 327,743×42;
   tags 42/stage). The G4 two-stage accumulations 2,865,996 / 27,530,412 are **two-stage
   sums, NOT per-stage or orbit totals** — citation must be per-stage only.
4. **No-claim scope**: the set is a claim-bearing *precondition* (D6), not itself a claim.
   No FER, no efficiency, no qualification, no promotion, no composable-key statement;
   S9 never cited as FER/efficiency evidence.

### Stage-3 identity (two-sense disambiguation, inherited from G4)

- **This Stage-3** = `design.md` D6 "Stage 3 measurement set" = `MACRO_PLAN_20260921.md` §5
  Stage 3 真实数据可行性与测量集 (preregistered disclosure cap + per-block λ decomposition;
  B1 → Müller eq 11/13 path; R2/R3-line measurement work per
  `REAL_DATA_CORRECTION_ROADMAP_20260922.md`).
- **Not** the parent packet `NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md` §6 "Stage 3"
  (the G2 freeze + one-shot execution) — that stage is closed (G2 SUCCESS). Do not conflate.
- **Not G4**: G4 (inventory, COMPLETE) is a read-only *input* to Stage-3. Stage-3 computes no
  inventory row, lists no CAL frame, and changes no G4 artifact.

## Non-Goals

No decode of any kind; no SC calls; no tag generation; no alignment derivation or census
reproduction (census σ quoted-only, never recomputed); no gate arithmetic beyond the frozen
comparison caliber (Wilson / `B_tail` / `delta_min` are N/A unless the frozen cap formula
explicitly binds them — needing them otherwise ⇒ new freeze); no FER/efficiency/
qualification/promotion/composable claim; no S9 citation as FER/efficiency evidence; no model
selection, no K change, no construction re-derivation; no edit of any existing
verdict/adjudication/freeze/STATUS artifact of G1/G1R2/G2/G3/G4; no read of raw SHG
acquisition data; no writes outside this packet dir; no code change in any existing module;
no read, use, or citation of S8/S9 synthetic probe parameters or Stage-1 test outputs;
no new real-data execution inside this packet (see § New-execution boundary).

### New-execution boundary (explicit)

- This packet as drafted **authorizes no new real-data execution** (no new decode, no new
  session read, no new acquisition touch). Its domain is already-frozen G2/G3/G4 artifacts.
- **If** the mainline later decides Stage-3 (or its R2/R3 successors) require a fresh
  real-data run, that run is a **separately authorized execution item**: own freeze, own
  Tier-Y one-shot packet, own Pre-EXECUTE/Pre-RESULT, own verbatim authorization. It SHALL
  NOT be smuggled into this packet at execution time (such a need ⇒ STOP / return
  condition 2). See Open questions Q4.

## Impact Scope

WRITE (new additive files only, this packet dir exclusively):
`s3_build_measurement.py` (packet-local, read-only builder, if authorized),
`s3_freeze_config.json` (Phase-A input manifest + TO-FREEZE cap + decomposition caliber),
`s3_lambda_decomposition.json`, `s3_lambda_decomposition.md`, `s3_counts.json`,
`s3_run_log.md`, this packet's `STATUS.yaml` (stage/counters/artifacts/result only — never
another packet's STATUS).

FORBIDDEN (hard stop ⇒ second return condition):
modify anything under `scripts/`, `formal_ir/`, `src/`, `experiments/`, `tools/`,
`results/`, `comparison_bench/outputs_comparison/`, `comparison_bench/tests/`; modify
`prior_m2.py`, `sc.py`, `algebra.py`, `transform.py`, or `scripts/m2_prior_validation.py`;
modify `docs/SECURITY_MODEL.md` or any G1/G1R2/G2/G3/G4 packet artifact (their
STATUS/verdicts/freeze files are read-only inputs); write under `results/` or
`comparison_bench/outputs_comparison/` (never, append-or-not does not apply); write anywhere
outside this packet dir (including `workspace/` and `workspace/probes/` — single output
route); read any raw SHG acquisition file; rerun any decode/census/alignment/pairing/CAL
allocation; recompute the census σ; add checksums/SHA-256/atomic writes/locking/retry
frameworks (AGENTS.md §5.7 — provenance is `path + field locator + artifact content
as-is`, not digests); any Pre-EXECUTE/Pre-RESULT self-approval; any decision-log /
project-memory / index update in-packet.

## Frozen constants (verbatim — any change requires a NEW freeze; do not guess)

| # | Key | Value | Stage-3 handling |
|---|---|---|---|
| 1 | `N` | 32768 | recorded verbatim as contract context (measurement row context, not re-derived) |
| 2 | `K1` | 319 | recorded verbatim (frozen; D4 deferred, no re-split) |
| 3 | `K2` | 6492 | recorded verbatim (frozen; no increase) |
| 4 | P16 construction digest | `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` | quoted verbatim; inner P16 procedure digest of the canonical `construction_and_allocation.json` (wrapper file's own sha256 differs — P17-established; Stage-3 computes NO digest) |
| 5 | `W_P` | 200 | recorded verbatim |
| 6 | `W_S` | 500 | recorded verbatim (sensitivity readout only) |
| 7 | `MOD` | CIRCULAR | recorded verbatim |
| 8 | `skip` | 702 | recorded verbatim (`INHERITED_NOT_DERIVED`) |
| 9 | `frame_pairs` | 256 | recorded verbatim |
| 10 | `floor` | 1e-15 | recorded verbatim |
| 11 | `chunk` | 512 | recorded verbatim (`chunk_rows`) |
| 12 | `bin` | 200 ps | recorded verbatim = pairing `bin_width_ps=200` (census frozen block). NOT the alignment scan `bin=100 ps` — different constant; Stage-3 derives neither |
| 13 | G2 `tag_master` | 2026103001 | recorded verbatim, labeled **INHERITED** (from G1R2; EVAL_SEED 2026093001 by frozen rule `TAG_MASTER = EVAL_SEED + 10000`) |
| 14 | G3 `tag_master` | 2026110101 | recorded verbatim (EVAL_SEED 2026100101, same frozen rule) |
| 15 | census σ | 114.43029692866367 | **frozen value, quoted only** — any citation MUST carry "frozen quoted value, not recomputed in Stage-3" + source artifact path. Recomputation ⇒ STOP |

Not in this freeze list (e.g. other census constants `d`/`period_ps`/`threshold_ps`/`gate_ps`,
gate values `B_tail 2.0e-4` / `delta_min 0.020` / Wilson `z=1.96`) are **not restated, not
verified, not computed** by Stage-3 — they remain whatever the G1–G4 artifacts say. Needing
them ⇒ new freeze (unless the frozen cap formula explicitly binds one of them at Phase A).

## Discipline mapping (G4 template → Stage-3; inapplicable decode items marked N/A, never deleted)

| G4 discipline item | Stage-3 status |
|---|---|
| Tier-Y one-shot, `s3_runs: 1`, `reruns: 0` | **RETAINED** (applies to the measurement build: exactly one complete build; see rebuild rule in Stop rules) |
| Independent Pre-EXECUTE PASS + authorization recorded BEFORE the build | **RETAINED** |
| Independent Pre-RESULT PASS before any publication/commit | **RETAINED** |
| Verbatim user authorization in `STATUS.yaml` before dispatch | **RETAINED** (`authorizations: []` = not authorized) |
| `undetected` isolation (never merged into success/FER) | **RETAINED as measurement discipline**: G2/G3 `undetected` counts (0/42 each, as frozen) enter only as isolated rows/columns; never merged into any λ total, cap comparison, or success number |
| Disclosure recount discipline | **RETAINED**: Stage-3 sums per-block disclosure over the frozen `per_block_outcomes.jsonl` rows and compares to the frozen per-stage recount (key 1,432,998 = 34,119×42; public 13,765,206 = 327,743×42; tags 42/stage). Mismatch ⇒ STOP/blocker; **never publish a corrected number** — frozen values stand. G4 accumulations (2,865,996 / 27,530,412) cited only as two-stage sums with that label |
| Every TO-FREEZE non-null (null/absent ⇒ hard error, never a default) | **RETAINED** (`s3_freeze_config.json` fields — incl. cap object + decomposition caliber) |
| Ambiguity ⇒ STOP and report (return condition 2), never guess | **RETAINED**, incl. the ambiguity register below |
| Participation disclosure (G3: decoder/model independence, NOT no-prior-contact) | **RETAINED** wherever G3 artifacts are cited |
| No decision-log / memory / index updates in-packet | **RETAINED** |
| No-claim scope (no FER/efficiency/qualification/promotion/composable statement; no S9-as-FER citation) | **RETAINED** — Stage-3 is a claim *precondition*, not a claim |
| Phase-A first-contact rules for SHG `_2`, alignment reproduction vs census σ | **N/A** — Stage-3 reads **no raw acquisition data** and performs **no derivation**; both SHG acquisitions stay untouched. Reason: measurement operates solely on already-produced derived artifacts |
| Three-arm decode A1/A2/B, EVAL blocks, COMPLETE-BLOCKS-ONLY | **N/A** — no decode, no frames allocated. Reason: Stage-3 touches no frame and runs no decoder |
| Wilson gate, `B_tail`, `delta_min`, `g2/g3_blocks` verdict arithmetic | **N/A** — Stage-3 renders no decode verdict; success = completeness criteria (§ Success criteria). Values are not restated or evaluated unless explicitly bound inside the frozen cap formula at Phase A |
| SC calls, tag invocations, decode wall budget 900 s | **N/A** (expected `sc_calls: 0`, `tag_invocations: 0`); replaced by the measurement budget in Stop rules |
| K/construction enforcement at decode time | **N/A** as execution constraint (nothing decodes); retained as recorded contract context |
| "Never pad/reuse/borrow frames" | **N/A as a frame-handling rule** (no frames handled); **RETAINED as a listing rule**: any CAL/segment frame ID referenced is copied exactly as frozen in `cal_ids*.json` / G4 inventory; never re-derived, re-allocated, or edited |

## Decomposition caliber (TO-FREEZE — proposed recommendation, NOT frozen)

The exact per-block λ decomposition is **not yet frozen** (no existing frozen column list was
found in D6 / spec / STATE). Phase A SHALL freeze exactly one of the following (mainline
decision; operator proposes, mainline disposes — operator computes nothing until frozen):

- **Recommended (Option A)**: per `(stage, block)` row with columns
  `{block_id, key_dependent_bits, public_control_bits, cal_handling (= sacrificed_excluded_from_denominator ref),
  reveal_bits_diagnostic (= diagnostic_only_never_lambda ref, value as recorded),
  tag_ref (= tag_master + index), undetected_isolated (= 0 as frozen, separate column, never summed),
  lambda_block (= frozen formula of the disclosure columns), cap_comparison (= frozen rule)}`,
  where `lambda_block` and the Müller eq 11/13 `H(q) → empirical H(X|Y)` substitution are
  written as a closed-form expression in `s3_freeze_config.json` with every input bound to a
  frozen artifact field. Rationale: minimal, recount-compatible, keeps reveal-bits out of λ
  (D3), keeps `undetected` isolated (D7), reuses the G4 Release-handling semantics without
  redefining them.
- **Option B**: Option A + an explicit `lambda_total` aggregation rule (sum/mean with stated
  denominator, CAL-excluded) — only if the mainline needs a session-level number for the
  R2/R3 handoff. Heavier; requires the denominator rule to be frozen alongside.
- **Forbidden**: any caliber that adds reveal-bits into λ, merges `undetected` into any
  total, re-derives CAL IDs, recomputes σ, or cites S9/S8/Stage-1 values.

## Cap caliber (TO-FREEZE — no frozen numeric basis; mainline decision required)

- D6 + spec validation-gates require a **preregistered cap** but state **no definition and
  no number**. No value is set in this packet. `s3_freeze_config.json` SHALL contain exactly
  one `cap` object (`{kind, value_or_formula, unit, source_artifacts, comparison_rule}`),
  all fields non-null, recorded BEFORE the build. Null/absent ⇒ hard STOP.
- **Recommended solution (for mainline裁决, not executed here)**: cap as a closed-form
  scalar bound in bits (or bits/symbol with stated N conversion) of the form
  `cap = F(frozen H source, frozen f or margin, N)` with `H source` bound to a frozen
  artifact (e.g. frozen `H_M2` from G1R2) and `F` written out verbatim at Phase A; the
  comparison rule states per-block vs cap (count-over-cap / max / stated aggregation) with
  `undetected` excluded. Rationale: preregister-before-use (D3 pattern), no post-hoc tuning,
  recount-compatible. Alternatives (fixed-bit cap from a prior freeze; session-relative cap)
  are legitimate mainline choices — any choice is a **new freeze**, never an in-packet edit.
- Until the cap is frozen, **no comparison sentence** (over/under cap, margin, rate) may be
  written anywhere, even as a "preliminary".

## Input manifest (READ-ONLY; every path must exist at Phase A — missing path ⇒ STOP)

Contract / rules / gate text:
1. `openspec/changes/archive/2026-09-22-nbpolar-prior-rebaseline/design.md` — D6 (Stage-3
   measurement-set definition), D3 (sacrifice-only + reveal-bits diagnostic), D7 (frozen list).
2. `openspec/specs/nbpolar-prior-rebaseline/spec.md` — validation-gates (Stage-3 as claim
   precondition) + sacrificed-small-CAL requirements.
3. `docs/nbpolar/STATE.md` §4.1 — promotion ladder (Stage-3 position; R2 FER / R3 efficiency
   relationship; no skipping).
4. `docs/SECURITY_MODEL.md` — CAL/prior accounting note + inventory skeleton context (read-only).
5. `docs/nbpolar/MACRO_PLAN_20260921.md` §5 Stage 3 + §9 F3 (measurement-set boundary; Release
   pattern) — boundary reference only.
6. `docs/nbpolar/REAL_DATA_CORRECTION_ROADMAP_20260922.md` — R2/R3/Stage-3 ownership (boundary only).
7. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G4-INVENTORY/{TASK_PACKET.md, AUTHORIZATION_PROMPT.md, STATUS.yaml, g4_freeze_config.json, g4_inventory.json, g4_counts.json}` — G4 discipline template + inventory values as read-only inputs (skeleton/provenance, NOT edited).

G1/G1R2/G2/G3 packets + frozen outputs (packet docs + workspace derived artifacts; same
closure as the G4 manifest — full path list to be enumerated verbatim in
`s3_freeze_config.json` at Phase A, incl. G2/G3 `per_block_outcomes.jsonl`,
`g2_summary.json` / `g3_summary.json`, `cal_ids*.json`, freeze configs, adjudications):
8. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL/` + `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s/`
9. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/` + `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2/`
10. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/` + `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2/`
11. `.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/` + `workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3/`

Construction + provenance context:
12. `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json` (canonical P16 path; path + K/orders presence recorded, no digest computed).

Explicitly NOT in the input manifest: raw SHG files; census script/packet
(`workspace/dual_rule_census_20260921.py` et al. — σ quoted from G3 artifacts +
`docs/decision-log.md` only); any sibling checkout; `results/`;
`comparison_bench/outputs_comparison/`; S8/S9 synthetic probe parameters; Stage-1 test
outputs; `docs/decision-log.md` / project-memory / index writes (never in-packet).

## Output spec (all under this packet dir; additive; never overwrite an existing file)

1. **`s3_freeze_config.json`** (Phase A): input manifest with per-item `path` + `exists` +
   `locators_used`, frozen-constants block copied verbatim from the table above, the frozen
   decomposition caliber + cap object (both TO-FREEZE → frozen at Phase A; null ⇒ hard
   error), outcome strings from the preregistration table below, budget, `authorizations`
   pointer. Every TO-FREEZE field non-null.
2. **`s3_lambda_decomposition.json`** (Phase B): `{packet, generated_by, row_count,
   decomposition_caliber_ref, cap_ref, rows:[...]}` — machine-countable per-block rows with
   `source_artifact` + `source_locator` per row.
3. **`s3_lambda_decomposition.md`** (Phase B): human report — scope + no-claim statement;
   per-stage tables (G2/G3); cap declaration block (value/formula + source + comparison
   rule, all as frozen); per-block decomposition table or range-compressed equivalent with
   explicit ID arrays sourced from `per_block_outcomes.jsonl`; recount cross-check block vs
   the frozen per-stage recount; `undetected` isolation line; G3 participation-disclosure
   statement where G3 is cited; inputs list verbatim from `s3_freeze_config.json`.
4. **`s3_counts.json`** (Phase B): `rows_by_stage`, cap-comparison summary (counts
   over/at/under cap per the frozen rule — NO verdict adjectives), `key_bits_sum`,
   `public_bits_sum`, `tags_total`, `cross_check{key:{computed,frozen,match},
   public:{...}, tags:{...}}`, `sc_calls: 0`, `tag_invocations: 0`, `s3_runs`, `reruns`.
5. **`s3_run_log.md`**: commands run, timestamps, per-ID status.
6. `STATUS.yaml` updated by the operator (stage/counters/artifacts/result only).

**Single output route:** the ONLY files this packet may ever write are the five outputs
listed above — `s3_freeze_config.json`, `s3_lambda_decomposition.json`,
`s3_lambda_decomposition.md`, `s3_counts.json`, `s3_run_log.md` — plus this packet's own
`STATUS.yaml`. Nothing is ever written under `results/`,
`comparison_bench/outputs_comparison/`, `workspace/`, or `workspace/probes/`.

## Acceptance Criteria / Success criteria (all must hold; FAIL ⇒ no publication, blocker return)

- **S3-0** Pre-conditions: `.git/HEAD` = `codex/nbpolar-phase0`; G3 stands accepted
  (`NBPOLAR_M2_PRIOR_G3_SUCCESS`), G4 stands COMPLETE
  (`NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`), M2 = `VALIDATED_AT_FROZEN_CONTRACT`;
  every input-manifest path exists; `s3_freeze_config.json` complete, all TO-FREEZE
  non-null (cap object + decomposition caliber frozen BEFORE the build); this authorization
  recorded in `STATUS.yaml` **before** the Phase-B build.
- **S3-1** Traceability: every decomposition row carries a resolvable `source_artifact` +
  `source_locator`; no row cites a path outside the input manifest without a recorded STOP;
  zero rows with unresolved `to_freeze` at the end.
- **S3-2** Per-block λ decomposition completeness: all frozen G2/G3 per-block rows decomposed
  under exactly the frozen caliber (no dropped block, no added block, no re-derived CAL/σ);
  `row_count` == number of JSON rows == number of MD table entries (or explicitly
  range-mapped equivalents with lossless ID arrays) == sum of `rows_by_stage`.
- **S3-3** Cap preregistration + comparison caliber: the cap object (value/formula + unit +
  source + comparison rule) is byte-identical between `s3_freeze_config.json` (Phase A) and
  the comparison applied in Phase B; no post-hoc cap edit, no preliminary comparison
  sentence; `undetected` excluded from every comparison.
- **S3-4** Numeric consistency: computed disclosure sums equal the frozen per-stage recount
  (G2/G3 each: key 1,432,998 = 34,119×42; public 13,765,206 = 327,743×42; tags 42/stage);
  G4 accumulations cited only as labeled two-stage sums; mismatch anywhere ⇒ blocker, frozen
  numbers stand, never a corrected number.
- **S3-5** No-claim scope: **no claim sentences** (no FER/efficiency/qualification/promotion/
  composable-key statement; no S9 citation as FER/efficiency evidence; no R2/R3 verdict
  language). The set declares itself a D6 precondition measurement, nothing more.
- **R1** Independent Pre-RESULT review PASS against S3-0…S3-5 before any publication/commit.
- **R2** Main-thread adjudication (only the main thread may accept; operator never self-accepts).

**Ladder note (STATE.md §4.1, no level skipping):** Stage-3 PASS records ONLY the Stage-3
conjunct of the D6 validation-gates row and **does not, by itself, move M2**: state stays
`VALIDATED_AT_FROZEN_CONTRACT` (R2 FER gate → `FER_MEASURED_AT_CONTRACT` and R3 efficiency
gate → `EFFICIENCY_ACCOUNTED` remain outstanding under their own preregistered packets and
cannot be replaced by Stage-3; the `READY_FOR_QUALIFICATION` conjunct additionally needs
sample-size + G4 + independent Pre-RESULT). Stage-3 FAIL/incomplete keeps every D6
claim-bearing statement forbidden. Stage-3 never promotes, never demotes, produces no new
FER/efficiency number, and cannot be satisfied by a partial decomposition.

## Preregistered outcome strings (PROPOSED → FROZEN at authorization, BEFORE the build)

| Outcome | State string |
|---|---|
| Complete measurement set, S3-0…S3-5 + R1 PASS | `NBPOLAR_M2_PRIOR_STAGE3_MEASUREMENT_COMPLETE` |
| Incomplete / any S3 criterion fails / blocker returned | `NBPOLAR_M2_PRIOR_STAGE3_MEASUREMENT_INCOMPLETE_BLOCKED` (failure layer stated in the body text; no new labels) |
| Builder crash with **no** output file written | no state string; recorded in `STATUS.yaml` counters with the crash reason; corrective-rebuild rule below applies; **no** science status invented |

No statistical FAIL/INCONCLUSIVE verdict exists for Stage-3 beyond the frozen cap-comparison
counts (counts are reported, never verdict adjectives).

## Stop rules

- Budget: **PROPOSED TO-FREEZE: ≤ 300 s wall / 2 GiB RSS, single-threaded** (reads and
  aggregation only, G4-analogue; decode budgets 900 s are N/A). Mainline freezes the numbers
  at authorization. Exceeded ⇒ STOP, record as blocker, no tuning, no narrowing of scope to
  fit the budget.
- Expected resource counters: `sc_calls: 0`, `tag_invocations: 0`, `s3_runs: 1`, `reruns: 0`.
- **Rebuild rule (one-shot analogue; PROPOSED TO-FREEZE):** a corrective rebuild is permitted
  ONLY if the first build crashed leaving **zero** measurement output files (exactly **one**
  such rebuild), recorded in `STATUS.yaml` (`rebuild: 1, reason: ...`). Once ANY complete
  `s3_lambda_decomposition.json` exists, no rebuild, re-generation, patch, or "addendum" run
  is allowed — any need afterwards ⇒ STOP/blocker + new freeze.
- Any raw SHG read, any decode/SC/tag invocation, any write outside this packet dir, any
  forbidden-path touch ⇒ STOP + blocker.
- Any attempt to recompute census σ, alignment, pairing, CAL allocation, K/orders, or to set
  the cap / decomposition caliber ad hoc ⇒ STOP.
- Recount cross-check mismatch ⇒ STOP; frozen numbers stand; never publish a corrected number.
- Missing/null TO-FREEZE value (incl. cap object, decomposition caliber) ⇒ hard error (never
  a default).
- Any ambiguity, incl. any row not fitting the frozen caliber, any schema conflict between
  artifacts, any `Stage 3` / `cap` / `λ` referent ambiguity ⇒ STOP (return condition 2),
  never guess.

### Ambiguity register (pre-declared STOP triggers — operator resolves none alone)

B1: cap definition/number/source (TO-FREEZE; mainline裁决 required — Open Q1). B2: per-block
λ column list + Müller eq 11/13 substitution wording (TO-FREEZE — Open Q2). B3: whether
Stage-3 counts feed R2 FER or R3 efficiency gates directly (no — boundary; Open Q3). B4: any
need for fresh real-data execution (out of scope here; separate authorization — Open Q4).
B5: any D6 scope item read as Stage-3 that is neither cap nor per-block decomposition ⇒
main-thread decision.

## Tasks (ordered; coder/operator agents execute exactly these, in order)

1. T0 — Draft check (this document): confirm packet dir holds ONLY the three draft files;
   confirm branch; confirm G3/G4 adjudication strings exist where cited; confirm no frozen
   constant reworded. No execution.
2. T1 — Phase 0 (post-authorization only): implement the packet-local READ-ONLY builder
   `s3_build_measurement.py` + inline self-checks (row-count agreement, input-path
   existence, recount cross-check, cap byte-identity Phase-A→Phase-B). Touches no existing
   module; no production decoder path reachable from it or any test.
3. T2 — Phase A: input-manifest freeze — enumerate exact read-only input paths + field
   locators and emit `s3_freeze_config.json` with every TO-FREEZE field non-null (cap object
   + decomposition caliber + budget + outcome strings as frozen at authorization).
4. T3 — Pre-EXECUTE: independent review PASS + authorization recorded in `STATUS.yaml`
   BEFORE any measurement build.
5. T4 — Phase B: ONE-SHOT measurement build over already-frozen artifacts at the frozen
   constants → emit `s3_lambda_decomposition.json`, `s3_lambda_decomposition.md`,
   `s3_counts.json`, `s3_run_log.md` with `undetected` isolated and sums cross-checked.
6. T5 — Pre-RESULT (R1): independent review PASS against S3-0…S3-5 before any
   publication/commit; then main-thread adjudication (R2).
7. T6 — Handoff: return per-ID PASS (S3-0…S3-5, R1, R2 noted as pending-main-thread) with
   output paths, row/count arithmetic, cross-check block, run log, scoped
   `git status -- <packet dir>`; or concrete blocker (return condition 2).

## Return (exactly two — AGENTS.md §10.1)

1. **All-complete:** per-ID PASS (S3-0…S3-5, R1, R2 noted as pending-main-thread) with output
   paths, row/count arithmetic (JSON == MD == counts sums), cap byte-identity statement,
   cross-check block, run log, scoped `git status -- <packet dir>`.
2. **Concrete blocker:** failing command + exact error/traceback + attempted remedies + the
   SINGLE decision needed from the main thread.

## Authorization statement

**This packet itself authorizes nothing.** No measurement work, no input-manifest freeze, no
builder script, not even a path-existence listing may be performed until the main thread
pastes `AUTHORIZATION_PROMPT.md` verbatim and `STATUS.yaml.authorizations` is non-empty.
Until then the correct stage is `PACKET_DRAFT` and the correct next gate is
`USER_AUTHORIZATION_PENDING`. **执行需主线粘贴 verbatim 授权后方可进行，本包本身不授权任何事。**
