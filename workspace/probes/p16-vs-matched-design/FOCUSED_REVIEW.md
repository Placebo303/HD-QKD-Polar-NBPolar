# FOCUSED_REVIEW — p16-vs-matched-design (Tier-X, reviewer-go)

Scope: AGENTS.md §10.4 focused Tier-X review (commands, completeness, arithmetic,
truth isolation, write-scope). Not Pre-EXECUTE/Pre-RESULT.

## Checks

(a) run.py vs base runners: `build_tables`/`sample_pmf`/`decode_pmf_floored`/`gen_block`/
`worst_k`/design loop are line-for-line inherited from `scl-gate-t3/run.py` (floor
convention, design_seed=2026093000, DESIGN_MC=64); block evaluation via
`two_layer.run_two_layer_block` and pairing rng=`default_rng([seed,block])` inherited
from `op-n32k-matched/run.py`. `table_decode = pmf_decode[(b-a)%Q]` confirmed
(delta = arange[None,:] - arange[:,None], row=a, col=b) — matches stated convention
with explicit 1e-15 floor. No unauthorized scope creep found.

(b) P16 read: `.workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE/g2_freeze.md` pins
freeze_sha256=`055c9064...a1b` with K1=319/K2=6492/N=32768 — matches
`construction_and_allocation.json`'s `cell.freeze_sha256`/k1/k2/n exactly (independently
recomputed: file bytes sha256 differs, as expected — g2_freeze.md calls the pinned
value the "inner P16 procedure digest", not the file hash). Slicing rule
`l1_positions=l1_order[:k1]`, `l2_positions=l2_order[:k2]` confirmed verbatim at
`operational_f13.py:777-778`.

(c) prereg vs run: prereg's "single sequential process" deviation is recorded in P
paragraph (1); `run_stdout.log` shows one `WROTE ... status ok` line from one process —
consistent, no hidden parallelism.

(d) Independent recompute from `results.json` records: per-arm operational/oracle exact
= 30/32 both arms (P16 and WK), undetected=0 in all 128 role-outcomes; all 4 failing
records (P16: seed 2026092811 blocks 1,3; WK: seed 2026092811 blocks 1,4) are
`verify_failed` with `l1_exact=True` and `l2_pure_error=True` — pure-L2, matches
STATUS.yaml. Jaccard recomputed from intersection/union/len_a/len_b:
L1 307/331=0.927492…, L2 6400/6584=0.972053… — both match reported values exactly.
`f_book = 5*6811/(H*N)` recomputed = 1.272821531730456 — matches reported and the
prereg's ~1.273 expectation.

(e) Truth isolation: `undetected` is a distinct outcome key, counted separately from
`exact`/`verify_failed` in both per-arm outcome totals and the record-level scan; 0
occurrences in this run, never merged into success counts.

(f) reruns=0 (STATUS.yaml, results.json). Budget: wall_s=2021.13 ≤ 3600, peak
RSS≈0.988 GiB ≤ 2 GiB, within_budget=true. Write scope: `git status` shows no changes
outside `workspace/probes/p16-vs-matched-design/`; that whole probe root is
git-ignored (`workspace/probes/*`) — no forbidden-path writes.

## Verdict

**PASS**
