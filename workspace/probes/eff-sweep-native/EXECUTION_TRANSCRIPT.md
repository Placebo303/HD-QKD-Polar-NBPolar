# eff-sweep-native execution transcript (Tier X)
- 2026-09-29 11:02 prereg.md written; smoke (seed=1, non-protocol): L16 22.9 s/block, L32 40.8 s/block -> est ~2.1 h, kept 32 blocks/point (smoke_note.txt).
- Threads: scl_joint_native._default_threads patched in-process to 4 (L1 4 threads, each of 4 concurrent top_m L2 branches 1 thread); process pinned with taskset -c 4-7; single process. No repo files modified.
- Design: H/H1/H2 read from scl-gate-t3/design.json (identical seed/code); not recomputed.
- Command: taskset -c 4-7 env PYTHONDONTWRITEBYTECODE=1 python run.py run (reruns=0), started 11:04, results.json written ~13:30 (8784 s).
- Binary-baseline CPU checks: see cpu_check_log.txt (11:04 99.7%, 11:24 100%, 11:36 99.8%, 11:56 99.8%, 12:06 99.8%); binary process exited before 12:25 (NO_BINARY_PROCESS afterwards). Never below 80%; no pause needed.
- Note: total=round(f*H*N/5) uses no-CRC f; f_with_crc = (5*total+16)/HN also in results.json.
