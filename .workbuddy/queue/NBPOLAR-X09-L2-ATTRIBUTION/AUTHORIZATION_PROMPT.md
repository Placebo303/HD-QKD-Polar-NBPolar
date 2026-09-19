# AUTHORIZATION_PROMPT.md — NBPOLAR-X09-L2-ATTRIBUTION (copy-paste authorization)

Copy and paste the block below to authorize. Links alone are insufficient.

```
AUTHORIZATION — NBPOLAR-X09-L2-ATTRIBUTION (Tier-X probe, 2026-09-19)

Basis: main-thread (user) decision on 2026-09-19 to run the zero-cost L2
attribution diagnostic probe NBPOLAR-X09-L2-ATTRIBUTION.

Scope (only):
- One worktree-artifact read-only pass over the frozen inputs listed in
  TASK_PACKET.md section 2 (P20M records/priors/plan/identity/report,
  four in-sample predecessor record files, five runner .py files for field
  semantics). Each read declared with stat size/mtime_ns in results.json.
- Zero protected opens in every form (no parquet/pairs content; no
  DEV/VAL/HOLD/1M/V25-counts/2M open, stat, or listing). If any protected
  path would be needed, STOP instead.
- Writes ONLY under workspace/probes/nbpolar_x09_l2_attribution/
  (prereg.md, body.py, results.json; results.json is the ONLY file body.py
  writes) plus the packet docs beside this prompt. No other writes.
- No decoder calls, no RNG calls, no tag calls (all stay 0).
- No claims beyond descriptive support labels; no verdict about the next
  scientific factor; no commit/push.

Command (exactly once; a rerun solely to fix an execution error is allowed
and must be recorded in results.json notes):
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
MALLOC_ARENA_MAX=2 && timeout 120
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python
workspace/probes/nbpolar_x09_l2_attribution/body.py

Stop rules: missing/absent expected file, unreadable JSON/JSONL, key-set
surprise in the npz, or nonfinite result → STOP, write results.json with the
specific STOP status, return. No repair by editing inputs.

I authorize this scope. Execute.
```
