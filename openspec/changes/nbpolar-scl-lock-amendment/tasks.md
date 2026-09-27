# Tasks: SCL Lock Amendment

Status: **draft — PENDING PI adjudication; grants no authorization; SCL
remains locked until PI approves.**

- [ ] T1 — PI adjudication of this amendment. PI reviews `proposal.md` +
  `design.md` and rules on: (i) accept / modify / reject the replacement
  gate for lock items (a)/(b); (ii) whether an M2 true-L1-control re-run
  (D2 option i) is required before, instead of, or alongside the synthetic
  gate; (iii) CRC length; (iv) the L ∈ {4,8,16} ladder (as proposed, or
  re-derived via `scl-synthetic-list-gate` design §(b)); (v) the D4
  pre-written outcome-band edges. No task below starts before T1 records a
  `DECIDED` ruling for each of (i)-(v). **[GATE — NOT AUTHORIZED without T1]**

- [ ] T2 — Implement CRC + joint two-layer list scoring in a new code path
  alongside frozen `scl.py` (new module or additive extension per the PI's
  T1 ruling on interface placement; `scl.py`'s existing `L=1`/single-field
  contract stays byte-for-byte reproducible). Focused tests required before
  any execution:
  - `L=1` identity: new decoder at `L=1` bit-identical to `sc_decode` /
    existing `scl_decode` `L=1` output (regression, satisfies lock item e).
  - Small-N enumerator oracle agreement: brute-force joint L1+L2 path
    enumeration matches the new decoder's top candidate on a tiny synthetic
    case.
  - CRC disclosure accounting: CRC bits counted toward `f_book` exactly once,
    consistent with the C10-style disclosure convention cited in
    `nbpolar-r2-fer-measurement-contract`.
  **[GATE — NOT AUTHORIZED until T1 is DECIDED]**

- [ ] T3 — Tier-X probe: three-line prereg (`prereg.md`) + one frozen-command
  run + one `results.json` at the D4 working point (channel `G1R2-matched@q1024`,
  N=32768, f_book≈1.20, k1 share 4.69%) across L ∈ {4,8,16}; probe-root-only
  writes (`workspace/probes/<id>/`); focused numerical review (commands,
  completeness, arithmetic, truth isolation, write scope) per AGENTS.md §10.4
  Tier-X rules — no Pre-EXECUTE/Pre-RESULT. **[GATE — NOT AUTHORIZED until T1
  and T2 are complete and the PI explicitly authorizes execution]**

- [ ] T4 — Record the T3 outcome against the T1-decided D4 bands in
  `docs/decision-log.md` (append-only) and, if the PI rules it in scope,
  a `docs/nbpolar/STATE.md` §0 sync line. This does not change the SCL lock
  string by itself — only T1's ruling can do that. **[NOT AUTHORIZED by this
  change; requires the PI's own decision-log/STATE update decision]**

- [ ] T5 — If T3/T4 land in the "unlock-for-real-data-candidate" band: prepare
  (do not execute) a real-data Tier-Y packet skeleton (`TASK_PACKET.md`,
  `PROMPT.md`, `STATUS.yaml`, `AUTHORIZATION_PROMPT.md` with
  `authorizations: []`) per AGENTS.md §10.1/§10.4. This task produces no
  verbatim authorization text and starts no real-data touch.
  **[NOT AUTHORIZED — skeleton only, empty authorization list by
  construction]**

## Standing rule

Every box above stays unchecked and every task stays gated until the PI
records the T1 ruling. This file grants no execution, no code merge, and no
lock removal by itself.
