# TASK PACKET AMENDMENT 1 — NBPOLAR-EXPLORATION-STEP0-SURVEY (2026-09-23, main thread)

**Trigger:** P0 draft check FAIL — operator correctly STOPPED with zero writes (probe root
absent, no builder, no outputs). Two factual defects were found, both in packet/skeleton
TEXT versus the frozen artifact. **No scientific-scope change, no definition-intent change,
no number change, no new authorization needed** — the same verbatim overnight delegation
(STATUS.yaml `authorizations`) covers the amended packet; this amendment is the recorded
delta per AGENTS.md §10.1 packet-freezing discipline.

## Defect 1 — `prereg_frozen.md` missing at dispatch

The file is now (re)written at `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP0-SURVEY/prereg_frozen.md`
with the corrected definitions below. Nothing else in the packet is re-opened.

## Defect 2 — M1 shape mismatch (artifact is ground truth; read as-is)

Verified directly from the frozen artifact (main thread + operator, independent):

- `profile.linear_counts`: len **2047**, `linear_offset` −1023 — matches the packet ✓
- `profile.circular_counts`: len **1024**, `circular_offset` −512 → residues **−512…+511**
  (one cell per distinct circular residue; the skeleton's "1025 cells −512…+512" was wrong)
- summaries live at **`profile.summaries.CIRCULAR`** = {n0 150909, n_plus 48832,
  n_minus 451, n_tail 0, n_total 200192} — values identical to the frozen anchors; the
  LINEAR_ONLY sibling block carries n_plus 48788 / n_minus 450 / n_tail 45.

**Bindings (exact):**

1. Builder assertion: `len(circular_counts) == 1024` (range −512…+511, offset −512);
   summaries read from `profile.summaries.CIRCULAR` (NOT top-level).
2. Index arithmetic (0-based after applying offsets): linear index = k + 1023;
   circular index = k + 512. Thus circular[−1] = idx 511, circular[+1] = idx 513.
3. Wrap-closure checks (VERIFY, never correct): `circular[511] == linear[1022] + linear[2046]`
   (anchors 450 + 1 = 451) and `circular[513] == linear[1024] + linear[0]`
   (anchors 48788 + 44 = 48832); circular tail = `profile.summaries.CIRCULAR.n_tail` (0).
4. |Δ| fold over residues j = 0…1023: `|Δ| = min(j, 1024−j)` ∈ 0…512 (only j = 0 gives 512);
   `mass_le1 = (circular[513] + circular[511]) / 200192`.
5. Frozen anchors unchanged: 44 / 1 / 451 / 48832 / tail 0. This amendment changes **where
   values are read from and how indices are computed — no number, no metric intent, no
   denominator, no population**.

## Parent-artifact correction (same session, main thread)

`step0-survey-prereg-skeleton.md` §3a primary-histogram bullet and the M1 manifest row
corrected 1025 → 1024 cells (residues −512…+511) and the summaries path pinned to
`profile.summaries.CIRCULAR`. Record-keeping note: the T2 review's "1025 cells" line
accepted the skeleton's text; this amendment supersedes that verification note.

## Continuity

Everything else in `TASK_PACKET.md` holds verbatim: inputs M1–M6 and roles, command form,
budget, write scope, stop rules, acceptance IDs S0-P/S0-1…S0-6, and the two return
conditions. The failed P0 consumed nothing (zero probe-root writes, zero rebuilds); the
re-dispatched operator starts P0 from scratch.
