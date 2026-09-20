# SCOPING_NOTES.md — NBPOLAR-L2-REPRESENTATION-REDESIGN (no-contact statement)

- No-contact statement: this scoping performed NO implementation, NO execution, NO protected
  opens (V25 counts, parquet/pairs, 1M/1.5M/2M content, `raw_prior_*.npz`), NO decoder runs,
  NO data contact of any kind. All cited numbers are read from already-committed records
  (decision-log 2026-09-20 entries: X14→X17 closeout, H2-v2, G3 `SCLW_STOP_SANITY_HIGH`,
  Q1–Q4 queue, P20S/P20T/RN packets; `NBPOLAR-SCL-SYNTHETIC-GATE/FREEZE_DRAFT.md` §§1–3;
  X16 packet prereg; AGENT_PROJECT_MEMORY L2 evidence lines). Read-only inventory only.
- Route posture: Route B (user-decided 2026-09-20) scopes the L2 model/representation +
  disclosure-placement redesign as a new top-level OpenSpec change, as mandated by the
  X14→X17/G3 closeout consequence ("any future SCL work must change the operating point …
  and be separately gated"; H2-v2: "new top-level OpenSpec change"). This scoping authorizes
  NOTHING: no axis selection, no freeze, no implementation, no execution.
- SCL stays locked: the `scl-synthetic-list-gate` track is untouched; its G0–G6 gates remain
  NOT AUTHORIZED. This route may produce a working point that becomes a CANDIDATE input to a
  future SCL G1 freeze, but promotion is never automatic.
- Real-data gate NOT reopened: RN and all P20 packets stay closed; the 2M HOLD tail and all
  never-decoded remainders stay never-decoded; the real-data N ladder ended by population
  exhaustion (0 full N=32768 blocks). No real-data execution, no protected opens, no
  FER/reliability/efficiency claims.
- Strategy stop rule (why not add N): the Tier-X queue cap forced the exhaustion-route
  return; the user chose redesign. Adding N is barred because every tested scale hugs its own
  no-information ceiling (X14/X15 N=256, G3 N=16384, X16 N=32768) and channel sharpening
  alone moved mismatch ~0.0002 (X14→X15) — scale × current representation is not the binding
  constraint.
- Q5 activation note: Q5 (TRAIN counts structure probe, remaining queue item) becomes the
  FIRST Tier-X probe of route B IF axis (iii) (L2 channel/prior model change) is selected
  first at B2; otherwise Q5 stays retired-conditional (its own usefulness is gated on an L2
  redesign being chosen, per the queue record). Q5 activation still requires the B3 freeze +
  B4 authorization gates; the sketch below is NOT a frozen prereg.
- Q5 prereg sketch (one line, NOT frozen): Question — does the TRAIN counts structure
  (worktree-reused prior arrays only; zero counts-NPZ opens, zero protected opens) support a
  structured prior re-estimation for L2 at the frozen synthetic working point, measured
  decoder-free as descriptive per-seed + pooled scalars, SCL stays locked.
- Seed hygiene: band 2026092600..2026092619 is reserved-but-unactivated (planner grep clean
  2026-09-20, zero hits repo-wide for pattern `20260926`). Occupied bands 20260923xx..20260925xx
  (incl. the SCL gate's reserved 2026092500..2026092519) were avoided. Re-grep is required at
  any future freeze before activation; reservation alone authorizes nothing.
- Gate posture: proposal (B1) is this scoping. Axis selection (B2), freeze review (B3),
  implementation authorization (B4), focused tests (B5), execution (B6), focused review (B7),
  and acceptance (B8) are each NOT AUTHORIZED and need explicit future gates.
