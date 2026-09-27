# TASK PACKET — L2 C1 reverse-Shannon control at k2=550 — Tier-X preparation

- Packet: `l2-singlefactor-c1-k550-packet`; probe: `l2-singlefactor-c1-k550`.
- Route is frozen by the main thread: C1, reverse-Shannon information-set control. This is the one bounded successor selected after the k550 C3 exact-overlap stop. No further route is automatic.
- User has granted broad authorization for continued synthetic work. This packet is prepared only; execution remains pending main-thread freeze review.

## Scope

Read-only inheritance sources: `workspace/probes/l2-singlefactor-k550/{prereg.md,results.json}`, `workspace/l2-singlefactor-k550-packet/{TASK_PACKET.md,PROMPT.md,STATUS.yaml,FOCUSED_REVIEW.md}`, `docs/nbpolar/NEXT_L2_PROBE_DESIGN_20260925.md`, and the frozen decoder/channel modules. The inherited runner imports `qkd_recon.polar_core` through `/mnt/d/Code/qkd-reconciliation-lab/src` at runtime; this external code dependency is read-only and is not a data input. Do not read real/protected/artifact data or unrelated sibling checkouts.

Authoring files for this packet:

- `openspec/changes/nbpolar-l2-c1-k550-probe/{proposal.md,design.md,tasks.md}`
- `workspace/probes/l2-singlefactor-c1-k550/{prereg.md,run.py}`
- `workspace/l2-singlefactor-c1-k550-packet/{TASK_PACKET.md,PROMPT.md,AUTHORIZATION_PROMPT.md,STATUS.yaml}`

At eventual execution, the only result artifact is `workspace/probes/l2-singlefactor-c1-k550/results.json`; any Numba cache remains inside that probe root. Forbidden writes include `results/`, `comparison_bench/outputs_comparison/`, the source baseline, existing probes, `docs/nbpolar/STATE.md`, and all files outside the declared preparation set.

## Frozen contract

- `N=q=1024`, `n_log=10`, `R=10`; F4 `p0=.75`, `p(+1)=.24`, `p(-1)=.005`, residual `.005` uniform over 1021 offsets, `y=(x+delta)%1024`, uniform Alice symbols.
- Reuse the k550 predecessor's M2 prior, GF32 two-layer SC/oracle and operational decode semantics, shared `d1=worst_k(H1,10)`, and `toeplitz_master=2026091361`.
- `k1=10`, `k2=550` only, no fallback. Disclosure is 2800 bits; `f_book≈2.9344139789` is bookkeeping only; exclude the 64-bit tag from f.
- BASE `worst_k(H2,550)`; CAND C1 `best_k(H2,550)` from ascending stable H2 sorting with ascending index as tie-break. Both use the same H2 from 128 shared design MC genie rows.
- Design seed `2026092600`; run seeds `2026092601..2026092604`; 16 paired blocks per seed (64 per arm); `DESIGN_MC=128`. Pair by `default_rng([seed,block])`, draw x before delta, and reuse `(x,y)` across both construction and decoder arms.
- Design-stage readout: intersection, Jaccard, identical, gate minimum 495. If identical or overlap `>=495/550`, stop before measurement with `non_discriminating`, zero cells, and one result record.
- `undetected>0` stops immediately and stays isolated; `decode_failed` and `resource_abort` are separate incidents. No thresholds, significance, A/B verdict, FER/efficiency/security/R2 claim, token, attempt accounting, or automatic continuation.
- T0 import created an empty `.numba_cache` directory under the new probe root; STATUS records it. No `results.json` was created.
- Wall `<=200 s`, peak RSS `<=1 GiB`, one-shot `reruns=0`. Output root is the new probe directory only.

## Acceptance IDs

- **C1-P1** OpenSpec captures the exact single-factor delta and boundaries.
- **C1-P2** Prereg has exactly Q/P/C lines and all frozen values plus exact command.
- **C1-P3** Runnable code is predecessor-derived with only intended C1/identity/seed/path delta; no execution and no result creation.
- **C1-P4** Packet, prompt, authorization record, and status agree; broad user authorization is recorded but execution awaits main-thread freeze review.
- **C1-P5** T0 syntax/import/structural checks only; no design MC, decoder, smoke run, or output creation.

## Stop and return

Stop if any frozen parameter cannot be implemented without changing the science contract. Do not tune or choose replacements. Do not run C, call `main()`, create a result, or create a result directory during preparation. Return after C1-P1..P5 are complete or with the exact blocker. Main thread owns freeze review, execution authorization, and post-run adjudication.
