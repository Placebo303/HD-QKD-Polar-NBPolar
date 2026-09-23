"""S3 paper-only complexity adjudication builder (stdlib only).

Implements EXACTLY the frozen packet
.workbuddy/queue/NBPOLAR-EXPLORATION-STEP3-ADJUDICATION/TASK_PACKET.md:

Per row, from the cited inputs C1/C2 under frozen assumptions A1-A7:
  ops_c1    = (q**l * l) * (n/2) per kernel-stage over the block;
              split rows sum over both factor fields (x2).
  ops_c2    = (q**2 + q) * L * n * log2(n) / 2 (multiplications);
              split rows sum over both factor fields (x2).
  seconds   = ops / 1e9 (A5 machine rate), per component.
  memory_values = L * q * n float32 values (split rows sum fields) (A4).
  within_decode_budget = (seconds_c1 <= 20 s AND seconds_c2 <= 20 s) (C4/A5).
  within_probe_bound   = (seconds_c1 <= 80 s AND seconds_c2 <= 80 s) (A7).

No other arithmetic; no tuning; no data; no decoder; no imports beyond stdlib.
Verdict rule (envelope S5, mechanical): SCALE iff full-native within decode
budget; else PROBE-ONLY iff >=1 probe row within the A7 bound; else STOP.
"""

import argparse
import json
import math
import os

RATE_OPS_PER_S = 1e9  # A5 machine rate
DECODE_BUDGET_S = 20.0  # C4/A5 inferred per-decode budget
PROBE_BOUND_S = 80.0  # A7 probe-cost bound (4x A5 budget)
N = 32768  # A3 block length per factor-stage
L_WIDTH = 2  # A2 RS-kernel width l

ROWS = [
    {"name": "full-native", "factors": [1024], "L": 8, "split": False,
     "factorization": "native, no split"},
    {"name": "probe-GF32-baseline", "factors": [32, 32], "L": 1,
     "split": True, "factorization": "GF(32)=32x32 baseline"},
    {"name": "probe-GF16xGF64", "factors": [16, 64], "L": 1, "split": True,
     "factorization": "GF(16)xGF(64)"},
    {"name": "probe-GF8xGF128", "factors": [8, 128], "L": 1, "split": True,
     "factorization": "GF(8)xGF(128)"},
]


def adjudicate_row(name, factors, L, split, factorization):
    # C1: ops_c1 = (q**l * l) * (n/2); split rows sum both fields.
    ops_c1 = sum((q ** L_WIDTH) * L_WIDTH * (N / 2) for q in factors)
    # C2: ops_c2 = (q**2 + q) * L * n * log2(n) / 2; split rows sum fields.
    ops_c2 = sum(
        (q ** 2 + q) * L * N * math.log2(N) / 2 for q in factors
    )
    seconds_c1 = ops_c1 / RATE_OPS_PER_S  # A5 rate
    seconds_c2 = ops_c2 / RATE_OPS_PER_S  # A5 rate
    # A4: memory = L * q * n float32 values; split rows sum fields.
    memory_values = sum(L * q * N for q in factors)
    within_decode_budget = (
        seconds_c1 <= DECODE_BUDGET_S and seconds_c2 <= DECODE_BUDGET_S
    )
    within_probe_bound = (
        seconds_c1 <= PROBE_BOUND_S and seconds_c2 <= PROBE_BOUND_S
    )
    return {
        "name": name,
        "q": factors[0] if not split else None,
        "q_set_factorization": factorization,
        "factors": factors,
        "split": split,
        "L": L,
        "l": L_WIDTH,
        "n": N,
        "ops_c1": ops_c1,
        "ops_c1_formula": "ops_c1 = sum_fields (q**l * l) * (n/2) [C1 + A1-A3]",
        "ops_c2": ops_c2,
        "ops_c2_formula": "ops_c2 = sum_fields (q**2 + q) * L * n * log2(n) / 2 [C2 + A1-A3]",
        "seconds_c1": seconds_c1,
        "seconds_c2": seconds_c2,
        "seconds_formula": "seconds = ops / 1e9 [A5 machine rate]",
        "memory_values": memory_values,
        "memory_formula": "memory = sum_fields L * q * n float32 values [A4]",
        "within_decode_budget": within_decode_budget,
        "within_decode_budget_rule": "seconds_c1 <= 20 s AND seconds_c2 <= 20 s [C4/A5]",
        "within_probe_bound": within_probe_bound,
        "within_probe_bound_rule": "seconds_c1 <= 80 s AND seconds_c2 <= 80 s [A7]",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()

    rows = [adjudicate_row(**r) for r in ROWS]
    full = rows[0]
    probes = rows[1:]

    # Verdict rule (envelope S5), applied mechanically.
    if full["within_decode_budget"]:
        verdict = "SCALE"
        falsifier = (
            "ops/memory over budget by orders of magnitude with no credible "
            "reduction path (per the A6 paths admitted at freeze time) => "
            "SCALE is not recorded [envelope S5]."
        )
        evidence = {"full_native_within_decode_budget": True}
    elif any(p["within_probe_bound"] for p in probes):
        verdict = "PROBE-ONLY"
        falsifier = (
            "the probe cannot preserve the Step-1 separation signal at "
            "bounded cost => PROBE-ONLY is not recorded [envelope S5]."
        )
        evidence = {
            "full_native_within_decode_budget": False,
            "probe_rows_within_probe_bound": [
                p["name"] for p in probes if p["within_probe_bound"]
            ],
        }
    else:
        verdict = "STOP"
        falsifier = (
            "a credible reduction path exists (among the A6 paths admitted at "
            "freeze time) that keeps a configuration within budget => STOP is "
            "not recorded on complexity grounds alone [envelope S5]."
        )
        evidence = {
            "full_native_within_decode_budget": False,
            "probe_rows_within_probe_bound": [],
        }

    results = {
        "probe": "NBPOLAR-EXPLORATION-STEP3-ADJUDICATION",
        "tier": "paper-only",
        "question": (
            "Even if Steps 0-2 look promising, does a native d=1024 decoder "
            "survive the complexity wall on paper (C1/C2 as cited), and is a "
            "split-dimension probe the right bounded next object? "
            "[complexity reading only; non-claim]"
        ),
        "inputs": {
            "C1": "RS-kernel O(q^l·l) — Trifonov 2018 (per proposal S Frozen facts)",
            "C2": "SCL (q^2+q)·L·n·log n/2 — Chen–Bai–Ma 2022 DOI 10.1016/j.jiixd.2022.10.002; q=1024 => ~1e6 mult/node",
            "C3": "frozen point N=32768 symbols/block, d=1024 alphabet",
            "C4": "per-decode ~20 s — INFERRED (G2/G3 wall ~855-858 s over 3 arms x 14 blocks); never a frozen constant",
        },
        "assumptions": {
            "A1": "rows: full-native q=1024 n=32768; probe rows (CLOSED set): GF(32)=32x32 baseline, GF(16)xGF(64), GF(8)xGF(128)",
            "A2": "SCL list L=8 full-native / L=1 probe rows; RS-kernel width l=2; iterations N/A",
            "A3": "n=32768 symbols per factor-stage per row; split rows sum over both fields",
            "A4": "memory model: L·q·n float32 values per row (split rows sum fields)",
            "A5": "budget ~20 s/decode (C4 inferred) + machine rate 1e9 float ops/s effective single-thread",
            "A6": "reduction paths admitted: L=1 on probe rows only; nothing else credited",
            "A7": "probe-cost bound <= 4x A5 decode budget (<= ~80 s)",
        },
        "rows": rows,
        "verdict": {
            "value": verdict,
            "falsifier": falsifier,
            "evidence": evidence,
            "rule": "SCALE iff full-native within budget; else PROBE-ONLY iff >=1 probe row within A7 bound; else STOP [envelope S5]",
        },
        "attestation": {"no_fer_object": True, "no_claim": True},
        "counters": {"s3_ops": 1, "reruns": 0, "rebuilds": 0},
        "stop_rules_fired": [],
    }

    os.makedirs(args.out_root, exist_ok=True)
    with open(os.path.join(args.out_root, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
        f.write("\n")

    def fmt(x):
        return f"{x:.3f}"

    lines = [
        "# Step-3 paper-complexity adjudication (one page; non-claim)",
        "",
        "## Cited inputs (as-is, never re-derived)",
        "",
        "- C1 RS-kernel `O(q^l·l)` — Trifonov 2018 (proposal S Frozen facts).",
        "- C2 SCL `(q^2+q)·L·n·log n/2` multiplications — Chen–Bai–Ma 2022,",
        "  DOI 10.1016/j.jiixd.2022.10.002; cited q=1024 scale ~1e6 mult/node.",
        "- C3 frozen point N=32768 symbols/block, d=1024 alphabet.",
        "- C4 per-decode ~20 s — INFERRED (G2/G3 wall ~855–858 s over 3 arms x 14 blocks); never a frozen constant.",
        "",
        "## Frozen assumptions A1–A7",
        "",
        "- A1 rows: full-native q=1024 n=32768; probes (CLOSED): GF(32)=32x32 baseline, GF(16)xGF(64), GF(8)xGF(128).",
        "- A2 L=8 full-native / L=1 probes; l=2; iterations N/A.",
        "- A3 n=32768 per factor-stage; split rows sum both fields.",
        "- A4 memory = L·q·n float32 values (split rows sum fields).",
        "- A5 budget ~20 s/decode (C4 inferred) + 1e9 float ops/s effective single-thread.",
        "- A6 reductions admitted: L=1 on probe rows only; nothing else credited.",
        "- A7 probe-cost bound <= 4x A5 budget (<= ~80 s).",
        "",
        "## Numbers (every figure: formula + assumption refs)",
        "",
        "| Row | ops_c1 [C1+A1-A3] | s_c1 [A5] | ops_c2 [C2+A1-A3] | s_c2 [A5] | mem values [A4] | <=20 s? | <=80 s? |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['ops_c1']:.3e} | {fmt(r['seconds_c1'])} s "
            f"| {r['ops_c2']:.3e} | {fmt(r['seconds_c2'])} s "
            f"| {r['memory_values']} | {r['within_decode_budget']} | "
            f"{r['within_probe_bound']} |"
        )
    lines += [
        "",
        "Reading aid (not a claim): full-native C2 ~2.06e3 s exceeds the ~20 s",
        "inferred budget by ~100x; full-native C1 ~34.4 s alone exceeds it.",
        "All three probe rows sit within the ~80 s A7 bound on both components.",
        "",
        "## Verdict (exactly one; mechanical per envelope S5)",
        "",
        f"- **{verdict}**",
        f"- Falsifier: {falsifier}",
        f"- Boolean evidence: {json.dumps(evidence)}",
        "",
        "## Non-claim statement",
        "",
        "This verdict is a complexity reading under the frozen A1–A7 "
        "assumptions, not a performance claim. No FER, efficiency, promotion, "
        "qualification, or key-yield statement of any kind is made here.",
        "",
    ]
    with open(os.path.join(args.out_root, "notes.md"), "w") as f:
        f.write("\n".join(lines))

    for r in rows:
        print(
            f"{r['name']}: s_c1={r['seconds_c1']:.3f} s "
            f"s_c2={r['seconds_c2']:.3f} s mem={r['memory_values']} "
            f"decode20={r['within_decode_budget']} probe80={r['within_probe_bound']}"
        )
    print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
