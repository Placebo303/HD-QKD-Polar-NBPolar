# TASK PACKET AMENDMENT 2 — NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE (2026-09-23, main thread)

**Trigger:** the dispatched (free-route) operator STOPPED at gate G1c with zero official-run
consumption and a fully diagnosed blocker. Frozen G1c compared the lab arm against an
**exact brute-force MAP** oracle. The lab's production `sc_decode_frame` f-node is
**min-sum** (`sign·min(|l|,|r|)`), an approximation; the operator proved (600 instances,
identical draws) that the 5/6/7 hard mismatches per 200 at q=4/8/16 are an inherent
decoder/oracle property mismatch, NOT an integration defect: substituting an exact-boxplus
SC with the same masks/priors gives 0/600 vs the exact oracle. Encoder equivalence, the
soft-prior cross-check (1.78e-15), G0 bit-exact reproduction (12/12 cells), G1/G1b
(hard=0), G2 (20/20 × 4 arms) and G3 smoke (all < 0.5) were all green; the official
one-shot was NOT consumed (`s1b_runs = 0`, output root holds only `prereg.md`). No tuning
was applied by the operator — correct discipline.

## Decision (binding): G1c redefined to a MIN-SUM MIRROR oracle

G1c's purpose is **integration fidelity** (the builder's use of the lab decoder — masks,
priors, plane wiring — is faithful), not algorithmic optimality. The exact-MAP oracle
tests the wrong property for an approximate decoder. Therefore:

- **G1c (redefined):** the lab arm's decode must equal the decode of an **independently
  coded packet-local min-sum recursion mirror** on ≥200 tiny instances per q
  (n_sym ∈ {2,4}; 100 F4-family + 100 random uniform transitions) — same priors, same
  frozen masks, same plane structure; **0 hard mismatches**, ties ≤1e-9. The mirror must
  be coded IN the new builder (not a copy of the lab function; it re-implements the
  documented min-sum f-node semantics `sign·min(|l|,|r|)` and the exact g-node, with the
  lab's clip applied), so the gate remains an independent check.
- **Documented approximation gap (new required record):** on the same instances the
  builder must also measure and record in `results.json` (`gates.G1c_approx_gap`) and
  `notes.md` the min-sum-vs-exact-MAP divergence counts (hard mismatches of the LAB-arm
  decode vs the exact brute-force MAP; the diagnostic observed 5/6/7 per 200 at
  q=4/8/16, all at n=4, magnitudes 0.24–27.9). This is a **property of the production
  binary baseline** (min-sum approximation), recorded as such; it is NOT a gate failure
  and must not be tuned away. The scientific consequence is carried into the milestone
  record: the B-lab arm is a min-sum-approximated production decoder, while arms A and
  B-hard/B-soft use exact recursions — the native-vs-binary axis is held clean by
  B-soft, and B-lab is the production reference with its approximation on record.

## Everything else unchanged

Arms A/B-hard/B-soft, channel and pairing (F4), metric conventions (F5), gates
G0/G1/G1b/G2/G3/G4, write scope, stop rules, budget (wall ≤ 7200 s), acceptance IDs
(S1B-2 now covers the redefined G1c), and the two return conditions — all per
TASK_PACKET + Amendment 1. The consumed pre-flight dev run remains accounted as
`s1b_runs: 0` with zero official outputs; the re-dispatched execution runs the official
one-shot fresh.
