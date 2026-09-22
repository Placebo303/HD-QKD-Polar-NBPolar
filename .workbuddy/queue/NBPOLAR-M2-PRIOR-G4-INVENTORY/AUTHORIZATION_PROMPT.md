# AUTHORIZATION — NBPOLAR-M2-PRIOR-G4-INVENTORY
(Main thread: paste this FULL text into your reply to authorize. Links alone are insufficient per AGENTS.md §10.1.
 User preference: batch authorization — this text is self-contained; no other file must be opened to understand it.)

**PRECONDITION (verified by the main thread before this authorization is requested):** the G3 adjudication must
stand as `NBPOLAR_M2_PRIOR_G3_SUCCESS` with M2 at `VALIDATED_AT_FROZEN_CONTRACT` (STATE.md §4.1). If G3 is not
accepted, this packet is VOID — do not paste this authorization. G4 does NOT require the R2 FER or R3 efficiency
gate (those remain prerequisites for claim-bearing statements, not for this inventory).

---

I AUTHORIZE packet NBPOLAR-M2-PRIOR-G4-INVENTORY (Tier-Y one-shot exhaustive public-message inventory; Release
pattern; CAL frames listed — RECORD/AUDIT ONLY, NO DECODE) on branch `codex/nbpolar-phase0` in repo
`/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`, per
`.workbuddy/queue/NBPOLAR-M2-PRIOR-G4-INVENTORY/TASK_PACKET.md`
(D6 gate G4; change `openspec/changes/nbpolar-prior-rebaseline/`). M2 stays `VALIDATED_AT_FROZEN_CONTRACT`;
G4 alone neither promotes nor demotes it.

A. Authorized work (Tier-Y one-shot; phases in order):
   - Phase 0: implement the packet-local, READ-ONLY inventory builder
     `.workbuddy/queue/NBPOLAR-M2-PRIOR-G4-INVENTORY/g4_build_inventory.py` + inline self-checks (row-count
     agreement, input-path existence, CAL set-equality vs `cal_ids*.json`, recount cross-check). It touches no
     existing module: no `comparison_bench/tests/` file is required (rationale on record: pure aggregation over
     frozen JSON/JSONL, no numerics, no production decoder path; Pre-EXECUTE covers it). No production decode may
     ever be reachable from it or from any test.
   - Phase A: input-manifest freeze — enumerate the exact read-only input paths + field locators from the
     packet's manifest and emit `g4_freeze_config.json` with every TO-FREEZE field non-null (missing/null ⇒
     hard error, never a default), the frozen-constants block copied verbatim, and the preregistered outcome
     strings.
   - Pre-EXECUTE: independent review PASS + this authorization recorded in `STATUS.yaml` BEFORE any inventory build.
   - Phase B: ONE-SHOT inventory build over the already-frozen artifacts at the frozen constants
     **N=32768, K1=319, K2=6492, P16 digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`,
     W_P=200 / W_S=500 / CIRCULAR / skip=702, frame_pairs=256, floor 1e-15, chunk 512, bin 200 ps,
     G2 tag_master 2026103001 (INHERITED), G3 tag_master 2026110101, census σ = 114.43029692866367 (frozen
     quoted value only — never recomputed)** → emits `g4_inventory.json`, `g4_inventory.md`, `g4_counts.json`,
     `g4_run_log.md`, covering G1/G1R2/G2/G3 public messages + CAL frame listings + Release-handling mapping,
     with `undetected` isolated and disclosure sums cross-checked against the frozen recount
     (key 1,432,998 = 34,119×42; public 13,765,206 = 327,743×42 for G2 and G3 as recorded in their artifacts).
   - Pre-RESULT: independent review PASS before any publication/commit; then main-thread adjudication.
   Acceptance IDs: G4-0, G4-1, G4-2, G4-3, G4-4, R1, R2.
   Touches: ONLY new files inside `.workbuddy/queue/NBPOLAR-M2-PRIOR-G4-INVENTORY/` +
     that packet's own `STATUS.yaml` (stage/counters/artifacts/result). Touches nothing under `src/`,
     `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, `comparison_bench/tests/`,
     `formal_ir/`, `scripts/`; never modifies `prior_m2.py`, `sc.py`, `algebra.py`, `transform.py`,
     `scripts/m2_prior_validation.py`, `docs/SECURITY_MODEL.md` (skeleton not written back in-packet; any
     docs update is a separate main-thread docs commit at archive stage — Main-thread adjudication
     2026-09-22 item 8), or any G1/G1R2/G2/G3 artifact. No writes
     outside this packet dir — single output route (Main-thread adjudication 2026-09-22 item 7): only the
     five `g4_*` outputs + this packet's `STATUS.yaml`; never `workspace/probes/` or anywhere else.

B. Explicitly NOT authorized: any read of raw SHG acquisition data (both SHG sessions stay untouched); any
   decode, SC call, or tag generation; any alignment derivation or census reproduction/recomputation of
   σ — numeric re-derivation only; a cross-artifact STRING consistency check of the quoted σ is allowed
   (Main-thread adjudication 2026-09-22 item 6); any gate arithmetic (Wilson / `B_tail` / `delta_min` are N/A for G4); any λ decomposition, disclosure
   cap, or Stage-3 measurement set (separate future packet, own freeze, own authorization — disambiguation
   confirmed, adjudication item 2); any
   FER/efficiency/qualification/promotion/composable-key claim or S9-as-FER citation; any S8/S9 synthetic
   probe parameter or Stage-1 test-output input (closure domain OUT, adjudication item 1); any K change,
   re-split, construction re-derivation, model selection, or threshold/window/MOD/skip change; any edit or
   overwrite of existing verdict/adjudication/freeze/STATUS artifacts of any prior packet; any write under
   `results/` or `comparison_bench/outputs_comparison/` or `workspace/probes/`; any rebuild/patch after a complete
   `g4_inventory.json` exists; any extension of the row schema or Release-handling enum beyond the
   packet-local freeze (six classes accepted, adjudication item 3; `result_publication` added, item 4)
   without a new freeze; any checksum/SHA-256/atomic-write/locking/retry machinery (AGENTS.md §5.7); any
   Pre-EXECUTE/Pre-RESULT self-approval; any decision-log / project-memory / index update in-packet.

**Decode-specific lines of the G3 template, marked N/A with reasons (retained, not deleted):**
- N/A — three-arm decode (A1/A2/B), EVAL blocks, COMPLETE-BLOCKS-ONLY: G4 runs no decoder and allocates no frames; it only reads already-adjudicated outputs.
- N/A — Wilson gate / `B_tail` / `delta_min` / `g2/g3_blocks`: G4's success is the completeness criteria (G4-0…G4-4), not a statistical verdict; no CI is computed.
- N/A — decode budget 900 s / SC-call arithmetic (126 SC) / tag invocations: G4 budget is **≤ 300 s wall / 2 GiB RSS single-threaded** (FROZEN — Main-thread adjudication 2026-09-22 item 5), expected `sc_calls: 0`, `tag_invocations: 0`, `g4_runs: 1`, `reruns: 0`.
- N/A — SHG `_2` Phase-A first-contact closure and alignment-reproduction-vs-σ gate: G4 reads no raw acquisition data, so there is no "first contact" to gate and no offset to derive; σ is quoted, never recomputed (recomputation ⇒ STOP). Allowed: a cross-artifact STRING consistency check of the quoted σ across G3 freeze/adjudication/decision-log — traceability only, operator executes directly (Main-thread adjudication 2026-09-22 item 6).
- N/A — CAL padding/reuse/borrow prohibition as a frame-handling rule: no frames are handled; the rule survives as a LISTING rule — CAL IDs copied exactly as frozen in `cal_ids*.json`, never re-derived or edited.
- RETAINED (not N/A): one-shot/no-rerun discipline, independent Pre-EXECUTE + Pre-RESULT, verbatim authorization with `authorizations: []` = not authorized, `undetected` isolation, disclosure recount cross-check, TO-FREEZE non-null, ambiguity ⇒ STOP, G3 participation-disclosure statement wherever G3 is cited, no-claim scope.

Constraints (binding): budget ≤ 300 s wall / 2 GiB RSS single-threaded (FROZEN — proposed ⇒ frozen, Main-thread adjudication 2026-09-22 item 5); exceeded ⇒ STOP, record as blocker,
no scope-narrowing to fit. Corrective rebuild ONLY if the first build crashed with zero inventory output
files — exactly one rebuild, recorded in `STATUS.yaml` (FROZEN — Main-thread adjudication 2026-09-22 item 5); once a complete `g4_inventory.json` exists ⇒ no rebuild/patch/addendum.
Recount mismatch ⇒ STOP; frozen numbers stand; never publish a corrected number. Any forbidden-path touch,
raw-data read, or decode/SC/tag call ⇒ STOP. Reporting: per-ID PASS with output paths + row/count arithmetic
+ cross-check block + run log + scoped `git status -- <packet dir>`; or concrete blocker with failing
command, exact error, remedies, and the SINGLE decision needed. No decision-log / memory / index updates
in-packet.

**Outcome strings FROZEN before the build (proposed ⇒ frozen, Main-thread adjudication 2026-09-22 item 5):** `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE` (all criteria + R1 PASS) /
`NBPOLAR_M2_PRIOR_G4_INVENTORY_INCOMPLETE_BLOCKED` (any failure/blocker; failure layer in the body). G4 PASS
records only the G4 conjunct of STATE.md §4.1's READY_FOR_QUALIFICATION row; M2 remains
`VALIDATED_AT_FROZEN_CONTRACT`; R2 FER and R3 efficiency gates remain outstanding and are not substituted.

**Target-output absence confirmed:** `.workbuddy/queue/NBPOLAR-M2-PRIOR-G4-INVENTORY/` contains ONLY
`TASK_PACKET.md`, `AUTHORIZATION_PROMPT.md`, `STATUS.yaml` at authorization time; `g4_freeze_config.json`,
`g4_inventory.json`, `g4_inventory.md`, `g4_counts.json`, `g4_run_log.md` do NOT exist yet. No prior packet's
outputs will be overwritten.

**No-rerun declaration:** this is a single-shot record/audit. One complete inventory build; no tuning of scope,
schema, or enums after seeing the inputs; no second build to "improve" or "complete" an existing inventory.

**Main-thread adjudications incorporated 2026-09-22 (mechanical merge; no operator discretion — each item
labeled `Main-thread adjudication 2026-09-22`):**
1. G4 closure domain = all G1/G1R2/G2/G3 public messages + CAL frames 明细 + Release-pattern mapping;
   census enters only as the quoted-σ source; S8/S9 synthetic probe parameters and Stage-1 test outputs are
   explicitly OUT; any domain expansion = a NEW freeze, never decided ad hoc during execution.
2. Stage-3 two-sense disambiguation confirmed: in D6/spec's "G4 + Stage-3", Stage-3 = `MACRO_PLAN_20260921.md`
   §5 measurement set, wholly carved out of G4 (separate packet, own freeze/authorization); G4 computes no λ,
   no cap, no FER.
3. The Release six-class enumeration is accepted as a packet-local freeze; `charged_0_labeled_public_ec_only_not_secure`
   is limited to a comparison record row against the Release in-sample mode and is never counted in
   NB-Polar's own accounting (NB-Polar accounts sacrificed CAL frames).
4. Result-publication convention = exhaustive-first: NLL/δ-profile-style result announcements are entered
   with `release_handling = result_publication` (size 0/N/A); where G1/G1R2 have no tag/disclosure fields,
   an explicit `none_recorded` row is written — never silence.
5. Newly frozen values (were proposed): budget 300 s / 2 GiB; the rebuild exception (one rebuild, only
   after a zero-output crash, accounted in `STATUS.yaml`); the preregistered state strings
   `NBPOLAR_M2_PRIOR_G4_INVENTORY_COMPLETE` / `NBPOLAR_M2_PRIOR_G4_INVENTORY_INCOMPLETE_BLOCKED`.
6. Ambiguity A resolved: a cross-artifact STRING consistency check of σ across the G3 freeze, adjudication,
   and `docs/decision-log.md` is allowed (traceability; operator executes it directly); any numeric
   re-derivation of σ remains forbidden (⇒ STOP).
7. Output single route confirmed: only `g4_freeze_config.json`, `g4_inventory.json`, `g4_inventory.md`,
   `g4_counts.json`, `g4_run_log.md` (+ this packet's `STATUS.yaml`); no writes to `workspace/probes/`.
8. `docs/SECURITY_MODEL.md` skeleton is NOT written back in-packet; the archive-stage docs update is a
   separate main-thread docs commit (the statement is retained in-packet).

To authorize, the main thread pastes this entire block with the line below completed:

AUTHORIZED BY: kai — <date> — g4_authorized: true (precondition: G3 accepted `NBPOLAR_M2_PRIOR_G3_SUCCESS`, M2 `VALIDATED_AT_FROZEN_CONTRACT`) / execution_one_shot: true / inventory_only_no_decode: true / raw_data_read: false

---

**本包本身不授权任何事（This packet authorizes NOTHING by itself）。** 执行须主线粘贴上方全文（verbatim）并使
`STATUS.yaml` 的 `authorizations` 非空后方可进行；在此之前 `stage: PACKET_DRAFT`、
`next_gate: USER_AUTHORIZATION_PENDING`，不得进行任何 G4 工作（含路径存在性检查）。
