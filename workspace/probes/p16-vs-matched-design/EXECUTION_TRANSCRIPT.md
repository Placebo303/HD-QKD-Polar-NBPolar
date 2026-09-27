# EXECUTION_TRANSCRIPT — p16-vs-matched-design (Tier-X probe)

Operator: Tier-X probe operator (this session). Authorization: PI-authorized
Tier-X probe continuation per `AGENTS.md` Section 10.4 / `docs/nbpolar/PROBE_TIER.md`;
operator packet delivered inline by the coordinator (2026-09-28). Non-claim,
descriptive planning evidence only.

## Steps taken

1. Read `AGENTS.md` Section 10.4 and `docs/nbpolar/PROBE_TIER.md` (Tier-X
   template: 3-line prereg, one results.json, root discipline, focused
   review only, no candidate/accepted token).
2. Located the P16 frozen construction source (read-only, never re-derived):
   `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`,
   `cell.l1_order`/`cell.l2_order` (permutations of `range(32768)`),
   `cell.k1=319`, `cell.k2=6492`, `cell.freeze_sha256` matching the
   `g2_freeze.md`-pinned digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`.
   Confirmed via `comparison_bench/src/comparison_bench/formal_ir/nbpolar/operational_f13.py:777-778`
   that the frozen slicing rule is `l1_positions = l1_order[:k1]`,
   `l2_positions = l2_order[:k2]`. Confirmed via
   `operational_f13_gate/report.md` that P16 was constructed under an OLD
   `source/target: "1M"` prior model, NOT the G1R2-matched real-CAL32
   channel used in this probe. No raw real data file was opened at any
   point; the P16 file is a frozen, already-materialized JSON artifact of
   positions/metadata (train_seeds/dev_seeds are synthetic RNG seeds).
3. Read `workspace/probes/scl-gate-t3/run.py` and `prereg.md` for the
   channel-building convention (SAMPLING pmf vs floored DECODE-table pmf)
   and the genie-SC design procedure (`design_seed=2026093000`,
   `DESIGN_MC=64`), and `workspace/probes/op-n32k-matched/run.py` for the
   `matched_pmf`/`worst_k`/block-pairing conventions, both inherited
   unchanged into this probe's own self-contained script.
4. Wrote `prereg.md` (Q/P/C, 3 paragraphs) and `run.py` under
   `workspace/probes/p16-vs-matched-design/` (this probe's own root; no
   other file was written or modified outside this directory).
5. Pre-launch checks (recorded here):
   - `results.json` absent before launch: verified (`test -f results.json` -> absent).
   - AST/grep scan of `run.py` for legacy `%`-style format operators: 0 found
     (`grep -n "%[sd]" run.py` -> none; f-strings throughout).
   - `python -m py_compile run.py`: succeeded.
   - Aggregation-key uniqueness: trivial (single `json.dump` call, one
     result record; no multi-part merge in this probe).
   - Design-sanity gate `|H1.mean()+H2.mean()-H|<=0.01` implemented as a
     hard `assert` inside `run_design()` (verified by reading the code,
     not merely documented).
   - Quick WSL import check (`comparison_bench.formal_ir.nbpolar.{two_layer,sc,algebra,prior,transform}`):
     `IMPORTS_OK`, `FROZEN_TOEPLITZ_MASTER=2026091361`.
   - Quick WSL dry check of `load_p16()` + `build_tables()` (no design MC,
     no block loop): `d1 len 319 d2 len 6492`, `digest match True`,
     `H=0.8165136251536648`, `f_book=1.272821531730456` (matches the
     prereg's expected ~1.273).
6. Launched the one-shot run: foreground
   `wsl.exe -e bash -c "cd .../p16-vs-matched-design && PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=.../.numba_cache OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python run.py > run_stdout.log 2>&1; echo EXIT_CODE=$?"`
   wrapped in the Bash tool's `run_in_background` (single process, no
   `&`/`wait` parallelism -- deviation recorded in prereg's P paragraph,
   the estimated ~1500s total cost fit comfortably inside the single
   3600s process budget). Background job id `bstakuzr7`.
7. Job completed (exit code 0). `run_stdout.log`:
   `WROTE .../results.json status ok wall_s 2021.1 peak_rss_GiB 0.988`.
8. Read back `results.json`, confirmed `status=ok`, `within_budget=true`,
   design sanity pass (`abs_diff=3.28e-5 <= 0.01`), `p16_source.matches_g2_freeze_digest=true`.
9. Wrote this transcript and `STATUS.yaml`. No reruns (`reruns=0`).
   No code/config file outside `workspace/probes/p16-vs-matched-design/`
   was created, edited, or deleted. No git write operation was performed.

## Outcome (non-claim, descriptive; full numbers in results.json)

- f_book = 1.2728 (expected ~1.273).
- Jaccard(P16.d1, WK.d1) = 0.9275 (307/331); Jaccard(P16.d2, WK.d2) = 0.9721 (6400/6584).
- P16 operational exact = 30/32 (seed 2026092810: 16/16, seed 2026092811: 14/16).
- WK operational exact = 30/32 (seed 2026092810: 16/16, seed 2026092811: 14/16).
- Both arms' 2 failing blocks are `verify_failed` with `l1_exact=True` and
  `l2_pure_error=True` (pure-L2 failures, isolated per AGENTS.md's
  undetected/exact isolation rule -- here `undetected` was 0 in both arms).
- P16 failing blocks: (seed 2026092811, block 1), (seed 2026092811, block 3).
- WK failing blocks: (seed 2026092811, block 1), (seed 2026092811, block 4).
  One shared failing block (block 1); the other failing block differs.
- Oracle-arm exact counts are identical to operational-arm counts for both
  arms in this sample (30/32 each), consistent with all observed failures
  being pure-L2 (oracle discloses true L1, so an L1-caused failure would
  differ between operational and oracle; none did here).

This is Tier-X planning evidence only: no threshold, no pass/fail verdict,
no candidate/accepted token, no attempt accounting, no real/artifact data.
