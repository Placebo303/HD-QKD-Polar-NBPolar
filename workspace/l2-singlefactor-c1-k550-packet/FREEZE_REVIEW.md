# C1 Tier-X main-thread freeze review — 2026-09-26

Decision: PASS for one synthetic execution of the exact `prereg.md` C command. The user's current-turn blanket authorization covers this scoped continuation. This review grants no real-data access or scientific promotion.

- Branch: `codex/nbpolar-phase0`. Existing unrelated worktree changes are preserved.
- Contract: C1 at `k2=550` only; F4@q1024, N=1024, k1=10, shared design MC, four new seeds ×16 paired blocks, design seed 2026092600, no fallback. `prereg.md` contains Q/P/C and the exact command.
- Code delta: compared mechanically with the k550 predecessor C body. The decoder, channel, paired sampling, budget, and stop logic are unchanged. C3-specific e2/h2 accumulation is removed; C1 uses stable ascending H2 selection with ascending-index ties. New IDs, seeds, output path, and in-root Numba cache are the other scoped changes.
- T0: operator reported syntax/import and tiny tie-order checks passed without calling design MC or decoder. The empty cache directory left by import is inside the declared root.
- Output: `workspace/probes/l2-singlefactor-c1-k550/results.json` is absent. Wall limit 200 s, RSS limit 1 GiB, one run, zero reruns; overlap >=495/550 or identical stops before measurement; `undetected` stops immediately and stays isolated.
- Runtime read dependency: inherited `qkd_recon.polar_core` import from `/mnt/d/Code/qkd-reconciliation-lab/src`; code only. No protected data, `results/`, or `outputs_comparison/` access.

The operator must record the exact invocation, exit code, start/end time, and result path on return. A failure consumes the one shot and must be reported without tuning or rerun. Tier-X results remain descriptive and require focused numerical review before main-thread adjudication.
