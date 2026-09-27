# Design: L2 C1 reverse-Shannon information-set control

## Frozen object and route

- Tier-X synthetic-only probe; `N=q=1024`, `n_log=10`, `R=10`.
- F4 channel: `p0=0.75`, `p(+1)=0.24`, `p(-1)=0.005`, residual mass `0.005` spread uniformly over the other 1021 offsets; `x` is uniform and `y=(x+delta) mod 1024`.
- Reuse the k550 predecessor's M2 prior, two-layer GF32 SC/oracle and operational decode semantics, shared `d1=worst_k(H1,10)`, `toeplitz_master=2026091361`, and disclosure accounting. No decoder or channel change.
- Preserve the predecessor's read-only runtime import of `qkd_recon.polar_core` through `/mnt/d/Code/qkd-reconciliation-lab/src`; this code dependency is not a data input and receives no writes.
- Single point `k1=10`, `k2=550`, no fallback. Disclosed bits are `5*(10+550)=2800`; `f_book≈2.9344139789` is bookkeeping only and not an efficiency point; the 64-bit tag remains excluded from `f`.
- BASE: `worst_k(H2,550)`, the 550 largest per-row Shannon entropies.
- CAND: `best_k(H2,550)`, the 550 smallest per-row Shannon entropies, selected with `np.argsort(H2, kind="stable")[:550]` and returned sorted by index. Stable ascending sort over the index-ordered vector supplies deterministic ascending-index tie-breaking.
- Both sets use the same `H2` computed from the same 128 design MC genie rows. `H2` is row Shannon entropy; no e/h statistic or new SC call is used to form C1.

## Frozen sampling and pairing

- Design seed `2026092600`; `DESIGN_MC=128`.
- Run seeds `2026092601..2026092604`, 16 blocks per seed, 64 blocks per arm.
- Per `(seed,block)`, use `default_rng([seed,block])`, draw `x` then `delta`, and reuse the resulting `(x,y)` for BASE and CAND and both decoder arms.
- Only the C1-vs-BASE information-set construction varies. k2 remains 550 even if the design gate stops the measurement.

## Gate and result

Before measurement, record intersection count, Jaccard, `identical`, and `gate_min=495`. If the sets are identical or intersection is at least 495, emit one `results.json` with `status=non_discriminating` and zero completed measurement cells. Otherwise measure the frozen arms once. `undetected` is isolated and triggers immediate stop; `decode_failed` and `resource_abort` remain separately counted incidents.

The only scientific readout is descriptive: per-seed oracle exact counts and paired discordance directions, totals, operational k1=10 secondary counts, isolated outcomes, wall time, and peak RSS. No significance wording, pass/fail verdict, candidate token, attempt accounting, R2 input, or automatic continuation.

## Runtime limits and writes

- Wall limit 200 seconds; peak RSS limit 1 GiB. Check after every design chunk of 32 samples and each measurement block; stop on breach with an honest incomplete status.
- One shot, `reruns=0`. No seed change, tuning, extra samples, or fallback.
- Probe output is confined to `workspace/probes/l2-singlefactor-c1-k550/`, with one result record. The Numba cache path, if used, is inside that probe root.
- No other project files are written during execution. Preparation writes only the enumerated OpenSpec, probe, and packet files.

## Execution gate

The user has granted broad authorization for continued work. This packet does not itself authorize execution: the exact prereg command, source delta, output absence, budget, and write scope require main-thread freeze review first. No design or decoder execution is part of this preparation task.
