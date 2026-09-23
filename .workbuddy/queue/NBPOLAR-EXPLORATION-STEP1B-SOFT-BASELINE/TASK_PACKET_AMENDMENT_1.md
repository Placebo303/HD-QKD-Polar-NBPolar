# TASK PACKET AMENDMENT 1 — NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE (2026-09-23, main thread)

**Trigger:** the principal supplied a pointer to the mature binary construction repo
`/mnt/d/Code/qkd-reconciliation-lab` (HD-QKD research-line binary Polar IR demo:
`qkd_recon.polar_core` = 3GPP-PW-order binary Polar SC/SCL; `qkd_recon.msd_conditional` =
production multistage conditional LLR tables incl. the shift-invariant difference-domain
estimator; `qkd_recon.channel_models` = Gray mapping + transition matrix). Read-only recon
confirmed: `msd_conditional.conditional_llr` is a soft per-plane metric conditioned on the
hard decoded prefix (production MSD semantics), and `build_msd_llr_tables_shift` fits the
F4 channel exactly (F4 is shift-invariant by construction). The execution interpreter
`/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python` has numpy 2.4.4 + pandas 3.0.2 +
**numba** (polar_core's dependency) — verified by listing, no installs. This amendment adds
the lab pipeline as a FOURTH arm, making the binary baseline the strongest available
(production-proven), per the closure adjudication's priority. No scientific-scope change;
the base packet's arms A / B-hard / B-soft are unchanged.

## Amendment (binding)

**New arm B-lab (fourth arm; all arms remain paired on the same message+noise per
(seed,block)):**

- Construction: per-plane binary polar via read-only import of the lab's
  `qkd_recon.polar_core` — static 3GPP polarization-weight order (`beta = 2**0.25`),
  non-systematic butterfly encoder, position-incremental SC with a frozen info mask;
  info mask = the `k_i` most reliable positions per plane.
- MSD conditioning via read-only import of the lab's `qkd_recon.msd_conditional`:
  per-plane LLR tables from `build_msd_llr_tables_shift` on the **exact F4 difference
  pmf** with `smoothing=0.0` (the pmf is exact and complete — no estimation noise; the
  smoothing would only add pseudo-counts) and `clip=30.0` (lab default; inactive at F4
  magnitudes, max \|LLR\| ≈ log2(0.75/0.005) ≈ 7.2); plane i decoded with
  `conditional_llr(tables, i, bob_symbols, prefix_values)` where the prefix is the HARD
  decoded value of planes 0..i−1 (the lab's production semantics: soft per-plane metric,
  hard-prefix conditioning).
- Per-plane allocation: `k_i = K_sym` for every plane (uniform; rate matched on average:
  r·K_sym message bits over r·n_sym channel uses). The lab's adaptive
  `rate_allocation.py` is OUT of scope for this screening (recorded simplification — a
  future packet may test it).
- Channel knowledge parity: the lab tables use the exact F4 distribution, matching the
  informed-channel setup arms A/B already have (no arm is handicapped).
- Provenance (recorded in `notes.md`): lab path, imported module/function names, and the
  lab's git HEAD via a read-only `git -C /mnt/d/Code/qkd-reconciliation-lab rev-parse HEAD`.
  The lab repo is READ-ONLY: never modified, never written; imported via an explicit
  `sys.path` insertion recorded in the builder. (Lab license: MIT.)

**Gate G1c (new):** oracle agreement for the lab arm — ≥200 tiny instances
(n_sym ∈ {2,4}; 100 F4-family + 100 random uniform transitions) per q: the lab-arm decode
vs brute-force MAP, 0 hard mismatches, ties ≤1e-9 with first-divergence cascade semantics
documented (same convention as G1/G1b).

**Metric extension:** `cells` per (q,R) gains `armB_lab` per-seed FER series +
mean/sample-std/range, and a tertiary paired ΔFER = FER_Blab − FER_A series + stats.
The primary paired comparison of the probe remains **B-soft − A** (the adjudicated
question); B-lab is the production-baseline reference. NO numeric threshold; a
native-negative outcome is kept evidence.

**Budget revision:** wall ≤ 7200 s (four arms); RSS ≤ 4 GiB; single-threaded;
`s1b_runs: 1`, `reruns: 0`; one corrective rebuild only after a zero-output crash.

**Acceptance IDs (revised):** S1B-2 now includes G1c (lab-arm oracle, 0 hard mismatches);
S1B-3 covers four arms × 12 cells × 1024 blocks × 16 seeds with pairing intact; S1B-4 adds
the lab-arm series statistics to the recomputation matrix; S1B-5 adds: the lab repo is
byte-untouched (read-only import only; recorded provenance).

**Interpreter (unchanged F7, confirmed by recon):** primary
`/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python` (numpy + pandas + numba + the
frozen `formal_ir` import chain). Nothing installed.

## Continuity

Everything else in `TASK_PACKET.md` holds verbatim: arms A/B-hard/B-soft (F1–F3), channel
and pairing (F4), metric conventions (F5), gates G0/G1/G1b/G2/G3/G4 (F6), write scope,
stop rules, and the two return conditions.
