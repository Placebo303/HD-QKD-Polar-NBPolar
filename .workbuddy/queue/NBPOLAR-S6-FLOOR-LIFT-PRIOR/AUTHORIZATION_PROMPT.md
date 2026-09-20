# AUTHORIZATION_PROMPT — NBPOLAR-S6-FLOOR-LIFT-PRIOR (copy-pasteable)

Copy the block below verbatim into the user response to authorize S6 execution.
Links alone are insufficient per AGENTS.md §10.1.

---

I authorize Tier-X execution ONLY for `NBPOLAR-S6-FLOOR-LIFT-PRIOR`
(`nbpolar_s6_floor_lift_prior`) exactly as frozen in its `TASK_PACKET.md`
(§§2–10), `prereg.md` (3 lines), and `body.py` (unmodified).

This authorization permits: read-only opens of the 7 artifacts in
`TASK_PACKET.md` §3 (two raw-prior npz, two alt_l2_tables npz for
counts-equality identity ONLY, P16 construction_and_allocation.json for
order/K identity ONLY, two raw_prior_orders json for presence/identity ONLY)
plus the probe's own `prereg.md`/`body.py`; the SINGLE compile check
`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m py_compile
workspace/probes/nbpolar_s6_floor_lift_prior/body.py`; and ONE run of
`cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar &&
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python
workspace/probes/nbpolar_s6_floor_lift_prior/body.py` (sibling-checkout venv;
this checkout has no .venv), writing ONLY
`workspace/probes/nbpolar_s6_floor_lift_prior/results.json`.

This authorization explicitly forbids: any decoder run or import (sc.py,
formal_ir/nbpolar, comparison_bench method code); opening any protected
segment (pairs.parquet, channel_counts.npz, comparison_bench outputs,
results/, raw-data roots); any write outside
`workspace/probes/nbpolar_s6_floor_lift_prior/`; any edit to `body.py`,
`prereg.md`, or the packet; any `docs/`/`AGENT_PROJECT_MEMORY.md`/index
write; any `git commit`/`push`; any λ/Laplace/construction change; any second
run beyond one execution-error fix-run; any claim, verdict, threshold, or
candidate/accepted token. Parameters freeze at prereg: seed 20260920, rules
FLOOR_1e-6 / FLOOR_1e-9 / FLOOR_1e-15, fixed P16 construction
(K1=319/K2=6492). Target-output absence confirmed: `results.json` does not
exist at authorization time. This probe is Tier-X non-claim: it consumes no
attempt, changes no scientific status, and its ranking is a recommendation
input only.
