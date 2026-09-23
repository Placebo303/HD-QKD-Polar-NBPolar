# PREG (FROZEN) — NBPOLAR-EXPLORATION-STEP3-ADJUDICATION

> Copied verbatim into the output root BEFORE any computation. Parameters are frozen here.

- **Task:** one paper-only Step-3 complexity adjudication (proposal §Step 3; design §D5;
  envelope `step3-complexity-adjudication-and-probe-envelope.md`). Tier: paper-only,
  tier-N/A; non-claim.
- **Question:** even if Steps 0–2 look promising, does a native d=1024 decoder survive the
  complexity wall on paper (C1/C2 as cited), and is a split-dimension probe (GF(32)
  baseline; other factorizations pre-allowed per OQ3) the right bounded next object?
- **Cited inputs (as-is, never re-derived):** C1 RS-kernel `O(q^l·l)` (Trifonov 2018);
  C2 SCL `(q²+q)·L·n·log n/2` (Chen–Bai–Ma 2022); C3 frozen point N=32768, d=1024;
  C4 per-decode ~20 s INFERRED (G2/G3 wall telemetry), never frozen.
- **Frozen assumptions A1–A7 (verbatim from STATUS.yaml):** rows = full-native q=1024
  n=32768 + probe rows GF(32)=32×32 (baseline), GF(16)×GF(64), GF(8)×GF(128) (set CLOSED);
  L=8 full-native / L=1 probes; l=2; iterations N/A; n=32768 per factor-stage, split rows
  sum both fields; memory = L·q·n float32 (split rows sum fields); budget ~20 s/decode +
  1e9 float ops/s effective; reductions admitted: L=1 on probes only; probe bound ≤ 4×
  budget (~80 s).
- **Exact command:** `<interpreter> .workbuddy/queue/NBPOLAR-EXPLORATION-STEP3-ADJUDICATION/s3_adjudicate.py --out-root workspace/exploration/nbpolar-native-highdim/step3/`
  (interpreter per ordered policy: `.venv/bin/python` absent → timetagger venv → stdlib-only `python3` deviation, recorded; builder is stdlib-only so any works).
- **Verdict rule (mechanical):** SCALE iff full-native row within budget; else PROBE-ONLY
  iff ≥1 probe row within the A7 bound; else STOP. Exactly one verdict with its falsifier.
- **Write root:** `workspace/exploration/nbpolar-native-highdim/step3/` — exactly
  `prereg.md`, `results.json`, `notes.md`. Nothing else, anywhere.
- **Budget:** wall ≤ 300 s, single-threaded, one op (`s3_ops: 1`, `reruns: 0`; one
  corrective rebuild only after a zero-output crash, recorded).
- **Stop rules (packet §Stop rules, binding):** missing cited input; output root
  pre-exists; verdict-rule ambiguity; arithmetic not traceable to C1/C2+A1–A7; any data
  path / decoder execution / `formal_ir` import / out-of-scope write / claim object ⇒ STOP.
- **Non-claim:** no FER / efficiency / promotion / qualification statement of any kind.
