# AUTHORIZATION — NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.
 User preference: batch authorization — this text is self-contained; no other file must be opened to understand it.)

**PRECONDITION (verified by the main thread before this authorization is requested):** the G3
adjudication must stand as `NBPOLAR_M2_PRIOR_G3_SUCCESS`, the G4 inventory must stand as
`NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`, with M2 at `VALIDATED_AT_FROZEN_CONTRACT`
(STATE.md §4.1, 2nd rung; R2 FER gate and R3 efficiency gate NOT done). If G3 is not accepted
or G4 is not COMPLETE, this packet is VOID — do not paste this authorization. Stage-3 does NOT
itself pass the R2 FER or R3 efficiency gate (those remain prerequisites for claim-bearing
statements under their own packets, not for this measurement set).

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT (Tier-Y one-shot Stage-3 measurement
set: preregistered cap + per-block λ decomposition — RECORD/MEASURE ONLY, NO DECODE, NO
RE-RUN) on branch `codex/nbpolar-phase0` in repo
`/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, per
`.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT/TASK_PACKET.md`
(D6 Stage-3 gate parallel to G4; change
`openspec/changes/archive/2026-09-22-nbpolar-prior-rebaseline/`). M2 stays
`VALIDATED_AT_FROZEN_CONTRACT`; Stage-3 alone neither promotes nor demotes it and produces no
FER/efficiency number.

A. Authorized work (Tier-Y one-shot; phases in order):
   - Phase 0: implement the packet-local, READ-ONLY measurement builder
     `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT/s3_build_measurement.py` +
     inline self-checks (row-count agreement, input-path existence, cap byte-identity
     Phase-A→Phase-B, recount cross-check). It touches no existing module; no production
     decode may ever be reachable from it or from any test.
   - Phase A: input-manifest freeze — enumerate the exact read-only input paths + field
     locators from the packet's manifest and emit `s3_freeze_config.json` with every
     TO-FREEZE field non-null (missing/null ⇒ hard error, never a default): the
     frozen-constants block copied verbatim, the per-block λ decomposition caliber
     (column list + Müller eq 11/13 substitution wording, exactly one frozen option), the
     cap object (`{kind, value_or_formula, unit, source_artifacts, comparison_rule}`,
     recorded BEFORE any computation), the budget, and the preregistered outcome strings.
   - Pre-EXECUTE: independent review PASS + this authorization recorded in `STATUS.yaml`
     BEFORE any measurement build.
   - Phase B: ONE-SHOT measurement build over the already-frozen artifacts at the frozen
     constants **N=32768, K1=319, K2=6492, P16 digest
     `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`, W_P=200 / W_S=500
     / CIRCULAR / skip=702, frame_pairs=256, floor 1e-15, chunk 512, bin 200 ps, G2
     tag_master 2026103001 (INHERITED), G3 tag_master 2026110101, census σ =
     114.43029692866367 (frozen quoted value only — never recomputed)** → emits
     `s3_lambda_decomposition.json`, `s3_lambda_decomposition.md`, `s3_counts.json`,
     `s3_run_log.md`, covering the frozen G2/G3 per-block λ decomposition + preregistered
     cap comparison, with `undetected` isolated (0/42 per stage as frozen, never merged)
     and disclosure sums cross-checked against the frozen per-stage recount
     (key 1,432,998 = 34,119×42; public 13,765,206 = 327,743×42 for G2 and G3 as recorded
     in their artifacts; G4 accumulations 2,865,996 / 27,530,412 are two-stage sums and
     SHALL be cited only with that label, never as per-stage values).
   - Pre-RESULT: independent review PASS before any publication/commit; then main-thread
     adjudication.
   Acceptance IDs: S3-0, S3-1, S3-2, S3-3, S3-4, S3-5, R1, R2.
   Touches: ONLY new files inside `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT/` +
     that packet's own `STATUS.yaml` (stage/counters/artifacts/result). Touches nothing under
     `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`,
     `comparison_bench/tests/`, `formal_ir/`, `scripts/`; never modifies `prior_m2.py`,
     `sc.py`, `algebra.py`, `transform.py`, `scripts/m2_prior_validation.py`,
     `docs/SECURITY_MODEL.md`, or any G1/G1R2/G2/G3/G4 artifact. No writes outside this
     packet dir — single output route: only the five `s3_*` outputs + this packet's
     `STATUS.yaml`; never `results/`, never `comparison_bench/outputs_comparison/`, never
     `workspace/`, never `workspace/probes/`.

B. Explicitly NOT authorized: any read of raw SHG acquisition data (both SHG sessions stay
   untouched); any decode, SC call, or tag generation; any alignment derivation or census
   reproduction/recomputation of σ; any gate arithmetic beyond the frozen cap-comparison
   caliber (Wilson / `B_tail` / `delta_min` are N/A unless explicitly bound inside the frozen
   cap formula at Phase A); any FER/efficiency/qualification/promotion/composable-key claim
   or S9-as-FER citation or R2/R3 verdict language; any S8/S9 synthetic probe parameter or
   Stage-1 test-output input; any K change, re-split, construction re-derivation, model
   selection, or threshold/window/MOD/skip change; any cap or decomposition-caliber edit
   after Phase A (any need ⇒ STOP/blocker + new freeze); any edit or overwrite of existing
   verdict/adjudication/freeze/STATUS artifacts of any prior packet (incl. G4); any write
   under `results/` or `comparison_bench/outputs_comparison/` or `workspace/` or
   `workspace/probes/`; any fresh real-data execution (any such need is a separately
   authorized execution item with its own freeze/packet/authorization — Open Q4); any
   rebuild/patch after a complete `s3_lambda_decomposition.json` exists; any
   checksum/SHA-256/atomic-write/locking/retry machinery (AGENTS.md §5.7); any
   Pre-EXECUTE/Pre-RESULT self-approval; any decision-log / project-memory / index update
   in-packet.

**Decode-specific lines of the G3/G4 template, marked N/A with reasons (retained, not deleted):**
- N/A — three-arm decode (A1/A2/B), EVAL blocks, COMPLETE-BLOCKS-ONLY: Stage-3 runs no
  decoder and allocates no frames; it only measures already-adjudicated per-block outputs.
- N/A — Wilson gate / `B_tail` / `delta_min` / `g2/g3_blocks` verdict arithmetic: Stage-3's
  success is the completeness criteria (S3-0…S3-5), not a decode verdict; no CI is computed
  unless explicitly bound inside the frozen cap formula.
- N/A — decode budget 900 s / SC-call arithmetic (126 SC) / tag invocations: Stage-3 budget
  is **PROPOSED TO-FREEZE ≤ 300 s wall / 2 GiB RSS single-threaded** (G4-analogue; frozen at
  authorization), expected `sc_calls: 0`, `tag_invocations: 0`, `s3_runs: 1`, `reruns: 0`.
- N/A — SHG `_2` Phase-A first-contact closure and alignment-reproduction-vs-σ gate: Stage-3
  reads no raw acquisition data, so there is no "first contact" to gate and no offset to
  derive; σ is quoted, never recomputed (recomputation ⇒ STOP).
- N/A — CAL padding/reuse/borrow prohibition as a frame-handling rule: no frames are handled;
  the rule survives as a REFERENCE rule — CAL IDs copied exactly as frozen, never re-derived
  or edited.
- RETAINED (not N/A): one-shot/no-rerun discipline, independent Pre-EXECUTE + Pre-RESULT,
  verbatim authorization with `authorizations: []` = not authorized, `undetected` isolation,
  disclosure recount cross-check (per-stage only), TO-FREEZE non-null (incl. cap +
  decomposition caliber), ambiguity ⇒ STOP, G3 participation-disclosure statement wherever G3
  is cited, no-claim scope.

Constraints (binding): budget PROPOSED TO-FREEZE ≤ 300 s wall / 2 GiB RSS single-threaded
(frozen at authorization); exceeded ⇒ STOP, record as blocker, no scope-narrowing to fit.
Corrective rebuild ONLY if the first build crashed with zero measurement output files —
exactly one rebuild, recorded in `STATUS.yaml`; once a complete
`s3_lambda_decomposition.json` exists ⇒ no rebuild/patch/addendum. Recount mismatch ⇒ STOP;
frozen numbers stand; never publish a corrected number. Cap byte-identity Phase-A→Phase-B
mismatch ⇒ STOP. Any forbidden-path touch, raw-data read, or decode/SC/tag call ⇒ STOP.
Reporting: per-ID PASS with output paths + row/count arithmetic + cap byte-identity + 
cross-check block + run log + scoped `git status -- <packet dir>`; or concrete blocker with
failing command, exact error, remedies, and the SINGLE decision needed. No decision-log /
memory / index updates in-packet.

**Outcome strings PROPOSED → FROZEN at authorization, BEFORE the build:**
`NBPOLAR_M2_PRIOR_STAGE3_MEASUREMENT_COMPLETE` (all criteria + R1 PASS) /
`NBPOLAR_M2_PRIOR_STAGE3_MEASUREMENT_INCOMPLETE_BLOCKED` (any failure/blocker; failure layer
in the body). Stage-3 PASS records only the Stage-3 conjunct of the D6 validation-gates row;
M2 remains `VALIDATED_AT_FROZEN_CONTRACT`; R2 FER (`FER_MEASURED_AT_CONTRACT`) and R3
efficiency (`EFFICIENCY_ACCOUNTED`) gates remain outstanding under their own packets and are
not substituted; no level skipping.

**Target-output absence confirmed:** `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT/`
contains ONLY `TASK_PACKET.md`, `AUTHORIZATION_PROMPT.md`, `STATUS.yaml` at authorization
time; `s3_freeze_config.json`, `s3_lambda_decomposition.json`, `s3_lambda_decomposition.md`,
`s3_counts.json`, `s3_run_log.md` do NOT exist yet. No prior packet's outputs will be
overwritten.

**No-rerun declaration:** this is a single-shot record/measure. One complete measurement
build; no tuning of cap, caliber, scope, or schema after seeing the inputs; no second build
to "improve" a comparison or "complete" an existing decomposition.

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: ______ — <date> — s3_authorized: true (precondition: G3 accepted `NBPOLAR_M2_PRIOR_G3_SUCCESS` + G4 COMPLETE `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE`, M2 `VALIDATED_AT_FROZEN_CONTRACT`) / execution_one_shot: true / measure_only_no_decode: true / raw_data_read: false / cap_and_caliber_frozen_at_phase_A: true

---

**本包本身不授权任何事（This packet authorizes NOTHING by itself）。** 执行须主线粘贴上方全文（verbatim）并使
`STATUS.yaml` 的 `authorizations` 非空后方可进行；在此之前 `stage: PACKET_DRAFT`、
`next_gate: USER_AUTHORIZATION_PENDING`，不得进行任何 Stage-3 工作（含路径存在性检查）。
