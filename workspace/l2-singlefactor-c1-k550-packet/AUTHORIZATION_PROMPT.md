# AUTHORIZATION RECORD — C1 Tier-X synthetic probe

The user has already granted broad authorization to continue work and supplied any needed authorization in the main conversation. Do not ask for the same authorization again.

This packet is not executable yet. The next gate is main-thread freeze review of the exact command in `workspace/probes/l2-singlefactor-c1-k550/prereg.md`, the C1 runner delta, absence of the target result, 200-second / 1-GiB caps, paired seeds, design-stage overlap stop, and the single probe-root write scope. Until that review records `READY_FOR_EXECUTE`, do not invoke the command.

Runtime code dependency inherited from the predecessor: read-only import of `qkd_recon.polar_core` via `/mnt/d/Code/qkd-reconciliation-lab/src`; no data reads or writes to that path.

After the main-thread freeze review, the scoped action covered by the user's existing authorization is:

> Run the exact preregistered C1 synthetic Tier-X probe once, with `reruns=0`, writing its single result record only to `workspace/probes/l2-singlefactor-c1-k550/results.json` and any Numba cache only inside `workspace/probes/l2-singlefactor-c1-k550/`. Stop before measurement if the C1/BASE d2 sets are identical or overlap is at least 495/550. Stop on budget breach or any `undetected` event. Do not read real/protected data, write `results/` or `comparison_bench/outputs_comparison/`, tune, add samples, or continue to another candidate. Report descriptive results only, with no FER, efficiency, security, R2-sizing, or superiority claim.

This is an execution scope record, not an independent freeze review or a scientific acceptance. The main thread owns the freeze decision and later focused numerical review.
