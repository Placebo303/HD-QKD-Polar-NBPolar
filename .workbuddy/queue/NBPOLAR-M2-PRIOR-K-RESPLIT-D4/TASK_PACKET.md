# TASK PACKET — NBPOLAR-M2-PRIOR-K-RESPLIT-D4 (K_total fixed-f vs fixed-K derivation under the M2 contract)

Per AGENTS.md §10.1: one complete frozen packet before delegation. Authorizes NOTHING until verbatim user
authorization flips `STATUS.yaml`.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch (verify `.git/HEAD`): `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-M2-PRIOR-K-RESPLIT-D4/`
- Change: `openspec/changes/nbpolar-prior-rebaseline/` — D4 (deferred K allocation) **preparation**; this packet
  **derives and reports both branches; it ADOPTS NEITHER**.
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (or the sibling venv; no TimeTagger needed — no data contact)
- Nature: **decoder-free, synthetic-only, no protected data, no claim.** Planning input for a later rate freeze.

## Goal

Close out D4: using the M2 contract as measured by G1R2 (w=200 / CIRCULAR on SHG `_1`), derive the preregistered
**fixed-f vs fixed-K_total** comparison and the resulting (K1,K2) from the **frozen** `select_empirical_split`, and
report both branches with their arithmetic — so the later rate/efficiency work starts from preregistered numbers
instead of post-hoc hand arithmetic.

## Non-Goals

**No K adoption/decision** (main-thread/PI owned). No protected/real-data read. No construction change.
No re-run of G1/G1R2/G2. No FER/efficiency/qualification claim. No change to any frozen K used by G2 (319/6492).

**SCOPE CLARIFICATION 2026-09-22 (main-thread ruling, resolves an operator STOP).** The pre-clarification text said
"decoder-free" in Non-Goals and in the stop rule while simultaneously requiring the frozen genie-derived e/h inputs —
an internal contradiction. The corrected, binding boundary is:
- **ALLOWED: synthetic genie TRAIN.** Building the pooled e/h risk vectors via the frozen path
  (`block_genie_risks` → `genie_layer_risks` → `genie_conditionals` → `sc_decode`) on **16 synthetic M2-model TRAIN
  blocks** at seeds 2026100101–2026100116. These are model-sampled synthetic blocks: **zero protected/real data
  contact**, which is exactly what the authorization forbids (`any decoder/genie/SC call on **protected data**`).
  Genie call counts are registered and reported.
- **STILL FORBIDDEN (unchanged)**: any protected/real data read; any decoder/genie/SC call on protected data; any
  construction re-derivation; H-proportional split as a selection rule; any K adoption or frozen-constant change.
- The descriptive label of this packet is **"no protected-data contact; synthetic-only"**, not "decoder-free".

## Impact Scope

WRITE: `workspace/m2_prior_validation/k_resplit_d4/` outputs (report + JSON); this packet's `STATUS.yaml`
(ids/counters/artifacts); focused tests `comparison_bench/tests/test_nbpolar_m2_k_resplit.py`.
No modification of `scripts/m2_prior_validation.py`, `prior_m2.py`, or anything under
`formal_ir/nbpolar/`, `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`.
FORBIDDEN: any real-data read (this packet is synthetic + frozen-artifact only); any decoder/genie/SC call on
protected data; checksums/atomic writes/locking/retry frameworks (AGENTS.md §5.7).

## Inputs (frozen, from G1R2 — recomputed and verified)

- M2 CIRCULAR CAL triple (SHG `_1`, 32-frame CAL, frames 1024–1055):
  q0 = 0.7562255859375, q+1 = 0.241943359375, q−1 = 0.0018310546875, q_rest = 0.
- Measured entropies under the contract: **H_M2 = 0.8168138204133305** (H1 0.02525363754305251 +
  H2 0.791560182870278); H_M0 = 0.6910589201904378.
- N = 32768; budget literal (D4/frozen convention): `K_total = floor((f·N·H_total − 64)/5)`.

## Derivation (both branches; each computed in-packet, not hand-copied)

1. **Branch A — fixed f = 1.3** (the planning budget literal):
   N·H = 32768 × 0.8168138204133305 = 26765.3553 (recompute); 1.3·N·H = 34794.9618; −64 = 34730.9618;
   ÷5 ⇒ **K_total = 6946** (floor). Compare with the frozen G2 point 319+6492 = 6811 and with the
   session-scale values 7020 / 7080.
2. **Branch B — fixed K_total** (f derived, not assumed): f = (5·K_total + 64)/(N·H). Report for each
   candidate K_total: **6811 ⇒ f ≈ 1.2747**; **7020 ⇒ f ≈ 1.3138**; **6946 ⇒ f ≈ 1.2999641** — i.e. **≈1.3 to ~4 s.f.,
   NOT exactly 1.3** (the budget literal's floor discards ~0.96 bits, so exact closure is mathematically unattainable).
   **Tolerance (frozen 2026-09-22):** report f to 7 decimals and state the deviation from 1.3 explicitly; do NOT
   write "= 1.3" and do NOT round it away. This replaced the pre-clarification "closure check ⇒ exactly 1.3".
3. **(K1,K2) split**: via the **frozen** `select_empirical_split(n, e1_mean, h1_mean, e2_mean, h2_mean, k_total)`
   imported from `nbpolar.empirical_genie_scaling` — **never reimplemented** — with e/h vectors built from the M2
   model on **16 synthetic TRAIN blocks** (preregistered seeds `2026100101` … `2026100116`; fresh, no collision with
   S9 2026092101/2026092117, P20 2026092000–2026092400, G1 EVAL_SEED 2026092201, G1R2/G2 EVAL_SEED 2026093001,
   SCL reserve 2026092517, L2 reserve 2026092617). `k_total` is a required caller argument; **no literal baked in**.
   Report the split for EACH branch's K_total.
4. **H-proportional split is BANNED** as a selection rule (S6/S8 caveat); it may appear only as a descriptive
   contrast column, clearly labelled.

## Outputs

`workspace/m2_prior_validation/k_resplit_d4/{report.md,results.json}` — per-branch K_total, derived f, (K1,K2),
the arithmetic shown explicitly, the frozen-selector provenance (import path + the exact call), the 16 seeds, and a
**no-adoption** banner. Plus `run_log.md`.

## Acceptance IDs → evidence

- `D4-A`: both branch arithmetics recomputed in-packet (N·H, 1.3·N·H, floor, and f for each candidate K_total) —
  arithmetic block in `results.json` + `report.md`.
- `D4-B`: (K1,K2) per branch from the frozen selector (import provenance; never reimplemented); seeds recorded.
- `D4-C`: focused tests green — hand-built synthetic e/h vectors, literal-enumeration replay of the split,
  branch arithmetic, `k_total` required/no-literal, H-proportional text absent as a selection rule.
- `D4-D`: no protected/real data read, no decoder contact, no adoption language anywhere in the outputs.

## Stop rules

Any protected/real-data read, or any decoder/genie/SC call **on protected data** ⇒ STOP + blocker.
Per SCOPE CLARIFICATION 2026-09-22, synthetic genie TRAIN IS authorized; the former clause "if building the e/h
vectors requires SC/genie ⇒ STOP" is **superseded** for the synthetic path only — it still applies to any protected
path. If a required input can only be obtained from protected data, or would require re-deriving the construction
outside the frozen `genie_conditionals` path ⇒ STOP and report rather than improvising a substitute.
Ambiguity ⇒ STOP (second return condition), never guess.

## Return (exactly two)

1. All-complete: per-ID PASS with evidence paths + the two-branch table + `git status` snippet.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE decision needed.

## Frozen resolutions

R1: this packet REPORTS, never ADOPTS — the fixed-f vs fixed-K choice remains a later preregistered decision
(main-thread/PI owned). R2: G2's frozen K (319/6492) is untouched by this packet. R3: numbers here are planning
inputs for a future rate freeze, never a license to re-split inside G2/G3. **R5 (added 2026-09-22):** the branch-B
closure at K_total 6946 gives f ≈ 1.2999641, NOT exactly 1.3 (floor-loss artifact of the budget literal); report the
deviation explicitly, never round it to "1.3". R4: hand-arithmetic values stated above
are for orientation and MUST be recomputed in-packet; any discrepancy is reported, not smoothed.
