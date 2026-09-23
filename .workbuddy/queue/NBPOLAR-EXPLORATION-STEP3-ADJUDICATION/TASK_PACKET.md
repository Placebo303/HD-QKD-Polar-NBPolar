# TASK PACKET — NBPOLAR-EXPLORATION-STEP3-ADJUDICATION (Tier-X, paper-only complexity adjudication)

**GATED PACKET.** Authorizes exactly ONE paper-only adjudication task and nothing else.
User authorization is recorded verbatim in `STATUS.yaml` as the 2026-09-23 instruction to
complete the full direction-exploration suite; scope is bound by this packet. No data
access of any kind, no code import from `formal_ir/`, no run of any decoder, no
frozen-constant change, no claim.

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; Branch (verify `.git/HEAD`):
  `codex/nbpolar-phase0` — DO NOT SWITCH.
- Packet dir: `.workbuddy/queue/NBPOLAR-EXPLORATION-STEP3-ADJUDICATION/`
- Output root (created by this task): `workspace/exploration/nbpolar-native-highdim/step3/`
  holding EXACTLY `prereg.md`, `results.json`, `notes.md`.
- Parent plan: `openspec/changes/nbpolar-native-highdim-exploration/` — proposal §Step 3,
  design §D5, `step3-complexity-adjudication-and-probe-envelope.md` (the accepted envelope;
  this packet freezes its assumptions and executes the one-page adjudication).
- Nature: **paper-only, tier-N/A** (see envelope §0): no probe run, no data, no decoder;
  arithmetic on cited formulas only; non-claim.

## Inputs (read-only; cited as-is, never re-derived)

- C1 RS-kernel scaling `O(q^l·l)` — Trifonov 2018 (as cited in proposal §Frozen facts).
- C2 SCL scaling `(q²+q)·L·n·log n/2` multiplications — Chen–Bai–Ma 2022,
  DOI 10.1016/j.jiixd.2022.10.002; cited q=1024 scale ≈ 1e6 multiplications/node.
- C3 frozen point: N = 32768 symbols/block, d = 1024 alphabet (frozen numbers verbatim).
- C4 per-decode budget ~20 s — **INFERRED ASSUMPTION** (G2/G3 wall telemetry
  ≈ 855–858 s over 3 arms × 14 blocks), never a frozen constant.

## Frozen assumptions (main-thread freeze 2026-09-23; all values fixed BEFORE any arithmetic)

| ID | Assumption | Frozen value |
|---|---|---|
| A1 | Rows | full-native: q=1024, n=32768; probe rows (pre-allowed set, CLOSED): GF(32)=32×32 baseline, GF(16)×GF(64), GF(8)×GF(128) (each product 1024; both factors ≤ 128; per OQ3) |
| A2 | Kernel/list params | SCL list L = 1 for probe rows and L = 8 for the full-native row; RS-kernel width l = 2; iterations N/A (SC/SCL non-iterative) |
| A3 | Block length | n = 32768 symbols per factor-stage per row (split rows process both factor fields over the same block; memory counts both) |
| A4 | Memory model | message storage = L · q · n float32 values per row (one q-vector per symbol per path; split rows sum over the two fields) |
| A5 | Budget | ~20 s per decode (C4, labeled inferred) + machine rate 1e9 float ops/s effective single-thread (stated assumption) |
| A6 | Reduction paths admitted | (i) L = 1 allowed on probe rows; (ii) no other reduction credited without a named mechanism in the artifact |
| A7 | Probe-cost bound | ≤ 4× the A5 decode budget (≤ ~80 s) |

## Task (exact)

1. P0 draft check: branch; packet files; output root absent.
2. P1: copy `prereg_frozen.md` → output root `prereg.md`; verify byte-identity.
3. P2: packet-local builder `s3_adjudicate.py` (stdlib only) computes, per row, the C1 and
   C2 estimates with the frozen A1–A7 values, converts to seconds at the A5 machine rate,
   compares each row against the A5 decode budget and the A7 probe bound, and records
   memory per the A4 model. NO other arithmetic; no tuning; every figure carries its
   formula + assumption refs. Write `results.json` (per-row table + verdict-relevant
   booleans + assumption echo) and `notes.md` (one-page human adjudication: inputs cited,
   assumptions, the numbers, and the single recorded verdict with its falsifier).
4. Verdict rule (from envelope §5, apply mechanically): SCALE iff the full-native row is
   within budget under the frozen assumptions; PROBE-ONLY iff the full-native row is NOT
   within budget AND at least one probe row is within the A7 bound; STOP iff no row
   (full-native or probe) is within budget. Record exactly one verdict with its stated
   falsifier; a verdict whose falsifier is met is not recorded.
5. P3: report per acceptance IDs.

## Output spec (results.json required keys)

`probe`, `tier` ("paper-only"), `question`, `inputs` (C1–C4 cited), `assumptions`
(A1–A7 echo), `rows` (per row: name, q, q-set/factorization, L, l, n, ops_c1, ops_c2,
seconds_c1, seconds_c2, memory_values, within_decode_budget, within_probe_bound),
`verdict` (exactly one of SCALE / PROBE-ONLY / STOP + its falsifier + the boolean
evidence), `attestation` (`no_fer_object: true`, `no_claim: true`), `counters`
(`s3_ops: 1`), `stop_rules_fired`.

## Budget & one-shot

wall ≤ 300 s (arithmetic only); single-threaded; `s3_ops: 1`, `reruns: 0`; one corrective
rebuild only after a zero-output crash, recorded.

## Write scope / stop rules

- Allowed: output root (3 files) + packet dir (`s3_adjudicate.py`, `s3_run_log.md`).
- Forbidden: any data path, any `formal_ir/` or `src/` import, any decoder execution,
  writes outside the two allowed roots, any claim language.
- Stop rules: missing input cited; output root pre-exists with content; any ambiguity in
  the verdict rule; any arithmetic not traceable to C1/C2 + A1–A7.

## Acceptance IDs

- **S3-P** draft check PASS (branch, packet files, output root absent).
- **S3-1** prereg byte-identical; run follows the frozen command.
- **S3-2** every row shows both C1 and C2 estimates with assumption refs; seconds at the
  A5 rate; memory per A4; no other arithmetic.
- **S3-3** exactly one verdict recorded, mechanically per the verdict rule, with falsifier.
- **S3-4** write scope exact (3 output files + packet-local files); no data/code touched.
- **S3-5** no-FER/no-claim attestation present; zero claim language; counters 1/0/0.

## Return (exactly two)

1. All-complete: per-ID PASS + the per-row seconds table + the verdict + falsifier.
2. Concrete blocker: failing command + exact error + attempted remedies + the single
   decision needed.
