# TASK PACKET AMENDMENT 2 — NBPOLAR-EXPLORATION-STEP1-SCREENING (2026-09-23, main thread)

**Trigger:** P0 draft check FAIL — operator correctly STOPPED with zero writes (output root absent, no builder). The frozen interpreter (`/home/karel_303/.venvs/timetagger/bin/python`) has numpy but **no pandas**, and the `formal_ir` package chain (`formal_ir/__init__.py` → `shared.py`) imports pandas before reaching the (pandas-free) `nbpolar` submodules. The operator found and verified (read-only) an existing pandas-capable interpreter and refused to substitute unilaterally — correct discipline. No scientific-scope change; no new authorization needed (same verbatim instruction, recorded in STATUS.yaml).

## Amendment (binding)

**Interpreter policy (replaces the packet's ordered policy and prereg line):**

1. `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python` — **authorized primary**
   (existing user venv; numpy 2.4.4 + pandas 3.0.2; the frozen import chain
   `PYTHONPATH=comparison_bench/src … -c "from comparison_bench.formal_ir.nbpolar import
   algebra, transform, sc, oracle"` succeeds; pinned primitives verified to match F3
   exactly: GF(4)=0b111, GF(8)=0b1011, GF(16)=0b10011);
2. `.venv/bin/python` if it ever exists (absent in this checkout);
3. timetagger venv — demoted: usable ONLY for pandas-free operations (it cannot import
   the `formal_ir` package chain), never for this builder.
No interpreter is installed; nothing is modified under any venv.

**Exact command (re-frozen):**
```
PYTHONPATH=comparison_bench/src /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python .workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/s1_screen.py --probe-root workspace/exploration/nbpolar-native-highdim/step1/
```
(with the ordered-policy substitution rule above if the primary path is absent at run time, recorded in `notes.md`.)

**Follow-on noted for the main thread (not scope of this amendment):** the pandas-capable
interpreter likely also enables the deferred M6 occupancy Phase-A check of the Step-0
skeleton (`real_frame_batch.parquet`); that addendum probe is a separate future packet.

## Continuity

Everything else in `TASK_PACKET.md` holds verbatim: F1–F8 freeze, correctness gates,
budget, write scope, stop rules, acceptance IDs, return conditions. The failed P0
consumed nothing; the re-dispatched operator starts P0 from scratch.
