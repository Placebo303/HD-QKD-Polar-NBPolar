# OPERATOR PROMPT — NBPOLAR-S11-SHG-TAIL-NATURE (copy-paste, self-contained)

You are the operator running a frozen Tier-X probe. Do NOT redesign. Do NOT guess.
If the packet is ambiguous, STOP and report (second return condition). Tier-X =
descriptive/non-claim: no claim, no token, no status change. Decoder-free: you
never call a decoder.

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD`. Else STOP.
- Venv: `/home/karel_303/.venvs/timetagger/bin/python` (TimeTagger 2.22.6 + Swabian
  shim per `docs/troubleshooting.md` — READ the import-namespace trap and the
  `.1`-segment double-count trap BEFORE touching any `.ttbin`).
- Packet: `.workbuddy/queue/NBPOLAR-S11-SHG-TAIL-NATURE/TASK_PACKET.md` (authoritative).
- ONLY write root: `workspace/probes/nbpolar_s11_shg_tail_nature/`. NEVER write
  anywhere else (packet STATUS.yaml excepted, counters/artifacts only). NEVER read
  SHG `_2`. NEVER modify `src/`/`experiments/`/`tools/`/`results/`/
  `comparison_bench/outputs_comparison/`/`formal_ir/` or any other packet dir.

## 1. Prereg FIRST (before any compute)

Write `workspace/probes/nbpolar_s11_shg_tail_nature/prereg.md` with the three-line
core (question; exact parameters incl. arms/offsets/windows/models/seeds=N-A/frozen
constants; exact command) verbatim from TASK_PACKET §Question/§Exact parameters,
plus the five preregistered readouts. No compute before this file exists.

## 2. Probe body (`body.py`, vendored, decoder-free)

Vendor the (N) narrow nearest-unique pairing literally from
`workspace/dual_rule_census_20260921.py` (read-only reference — copy the function,
do not import from workspace; frozen constants d=1024, bin 200 ps, period 204800 ps,
frame_pairs 256, gate 200 ps, threshold 40000 ps; symbol map `(b_A % 1024,
b_B % 1024)`, `b = t // 200`, `tA_aligned = tA_raw + offset`). Load SHG `_1` via
`FileReader` (auto-follow `.1`; never concatenate). Arms per TASK_PACKET: W-grid
{200,500,1000,2000} at offset +50; ANCHOR (w=500, skip-702, post-skip frames
1056–1837 = the G1 CHAR segment per the frozen SEG_RANGES — main-thread
correction 2026-09-21 replaced the contradictory "first 782 post-skip frames";
must reproduce p̂ = 0.0050202 EXACTLY, else STOP and record invalid);
offset scan {−50, 0, 25, 50, 75, 100} ps at w=500; far-offset baseline at
50 ± 409600 ps (w=500). Per arm: linear + circular δ-profiles {0,±1,±2..k}
(LINEAR_ONLY wrap semantics), p̂, q+1/q−1. Anchor additionally: per-frame tail
clustering (frames with ≥1 tail event vs Poisson(p̂×256); dispersion ratio).
No decoder, no prior fit, no model selection, no seeds (deterministic).

## 3. Results (ONE record)

`workspace/probes/nbpolar_s11_shg_tail_nature/results.json`: per-arm values
(deterministic — no seeds, so per-arm literals; mean/std/range N/A), the five
readouts with their arithmetic (ratios p̂_2000/p̂_200, offset-curve shape,
far-offset tail vs 99.7% and vs in-window tail, dispersion ratio), the anchor
reproduction check, wall/RSS, and the descriptive classification. Never a
pass/fail verdict, never a claim.

## 4. Verify + return (exactly two conditions)

Run log inside the probe root. Return:
1. All-complete: per-ID S11-P..S11-R PASS with evidence paths + results summary +
   wall/RSS + `git status --porcelain -- workspace/probes/nbpolar_s11_shg_tail_nature/`.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies +
   the SINGLE decision needed. "Still incomplete" is not a report.

Stop rules: anchor mismatch ⇒ STOP (invalid probe, record). Budget ≤ 300 s / 2 GiB
single-threaded; exceeded ⇒ STOP (no tuning). Any FORBIDDEN touch (SHG `_2`,
decoder, out-of-root write, post-prereg parameter change) ⇒ STOP + blocker.
No decision-log / memory / index updates (milestone batch after review).
