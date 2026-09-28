# AUTHORIZATION — m2-scl-check-g2g3-success

**Status: ALREADY GRANTED. This is a verbatim record, not a pending-paste
template — no re-authorization is required to move this packet to
Pre-EXECUTE review.** (Per AGENTS.md §10.1 every execution-ready packet
carries an `AUTHORIZATION_PROMPT.md`; this one documents authorization
already given rather than asking for it, per this task's own instruction.)

---

**AUTHORIZED BY**: PI, in-chat, **2026-09-28**.

**Verbatim text**:

> 授权，19 块也跑 SCL L=16

**Interpreted scope** (operator's reading, recorded here for audit — if
this reading is wrong, correct it before Pre-EXECUTE review, not after):

A. Authorized:
   - Re-decoding, with SCL (list_width_L=16, top_m=4, CRC-16-aided, per the
     already-DECIDED `nbpolar-scl-lock-amendment` T1/T2/T3 module
     `scl_joint.py`, the SAME module the predecessor packet
     `m2_scl_rescue_g2g3` already used), the 19 B-arm `outcome=exact`
     blocks: G2 blocks 0,2,3,4,6,7,8,9,10,11,13 (11 blocks); G3 blocks
     3,5,6,7,8,9,12,13 (8 blocks).
   - Building the preparation artifacts for this preservation check:
     `run.py`, `TASK_PACKET.md`, `prereg.md`, `STATUS.yaml`, this file —
     all under `workspace/m2_scl_check_g2g3_success/` (new, additive-only
     directory).
   - "19 块也跑 SCL L=16" ("run SCL L=16 on the 19 blocks too") is read as
     extending the ALREADY-AUTHORIZED SCL(L=16) re-decode methodology
     (predecessor packet, authorized 2026-09-28) from the 9 verify_failed
     blocks to the 19 exact-outcome blocks — i.e. it authorizes the SAME
     decoder/parameters on a DIFFERENT (disjoint) target set. It is read as
     covering the ordinary next steps of a frozen-packet workflow (packet
     preparation now; independent Pre-EXECUTE review next; then, if PASS,
     the one-shot execution) — not as a blanket waiver of those gates.

B. Explicitly NOT authorized by this text (unchanged AGENTS.md defaults):
   - Skipping independent Pre-EXECUTE review before execution.
   - Skipping independent Pre-RESULT review before `results.json` is cited
     in any adjudication document, decision-log entry, or commit.
   - Any change to `NBPOLAR_M2_PRIOR_G2_SUCCESS` / `NBPOLAR_M2_PRIOR_G3_SUCCESS`
     / the M2 status ladder / any G2 or G3 Wilson-gate verdict.
   - Drawing any EVAL/CAL/HELDOUT data beyond what reproduces the SAME CAL
     fit and the SAME 19 already-consumed EVAL blocks G2/G3 already used.
   - Modifying `sc.py`/`scl.py`/`scl_joint.py`/`two_layer.py`/`transform.py`/
     `algebra.py`/`prior.py`/`prior_m2.py`/`operational_f13*.py`/
     `m2_prior_validation.py`, or writing under `results/`,
     `comparison_bench/outputs_comparison/`, or any pre-existing
     `workspace/m2_prior_validation/*` directory, or any G2/G3
     `.workbuddy/queue/` packet dir, or the predecessor's
     `workspace/m2_scl_rescue_g2g3/` directory (read-only reference only).
   - git commit/push (this preparation pass made no git writes).
   - A rerun after a verdict, or any parameter/seed/K/window/MOD change
     under any outcome (one-shot; a rerun to fix an execution DEFECT is a
     separate recorded attempt, never a silent overwrite).

Constraints (binding, same as any frozen packet, inherited from the
predecessor): per-block budget ≤1200s wall / ≤2GiB RSS (exceeded ⇒ record
as resource_abort for that block, no tuning to fit); fidelity mismatch on
any block ⇒ STOP that block before the preservation-check step
(main-thread ruling D3, inherited); ambiguity ⇒ STOP and report, never
guess.

`STATUS.yaml`: `freeze_and_implementation_authorized: true` (this
authorization covers §A above) / `execution_authorized: false`
(independent Pre-EXECUTE review has not yet happened — that is the next
gate, not this authorization) / `decoder_modification: false`.
