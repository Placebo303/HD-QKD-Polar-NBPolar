"""Phase 3-R1 one-shot synthetic EVAL entry point.

Frozen-argument CLI: every scientific parameter is an explicit required
flag, so the frozen command in ``EVAL_FREEZE_R1.md`` (literal full
256-permutation, seed, counts) is exactly replayable with no placeholder.
Fail-closed guards: predecessor seeds 2026091200-1203 are refused
(never rerun or reuse that stream), and an existing ``--out`` dir is
never overwritten (single-shot evidence; rerun = new dir + new freeze).

R1 streams (all differ from every predecessor seed):

```text
R1 unit/sanity = 2026091210
R1 TRAIN       = 2026091211
R1 DEV         = 2026091212
R1 EVAL        = 2026091213 (one future use after reviewer-go PASS only)
```

Field is the frozen MVP choice: GF32, primitive alpha 2. Output is one
compact JSON summary plus the literal disclosure order; nothing is
written under production roots (the frozen ``--out`` lives in the R1
packet dir). No I/O at import, no global RNG.
"""

from __future__ import annotations

import argparse
import json
import sys
from numbers import Integral
from pathlib import Path

import numpy as np

R1_UNIT_SEED = 2026091210
R1_TRAIN_SEED = 2026091211
R1_DEV_SEED = 2026091212
R1_EVAL_SEED = 2026091213

BANNED_SEEDS = frozenset({2026091200, 2026091201, 2026091202, 2026091203})


def parse_order(text: str) -> np.ndarray:
    """Parse a comma-separated U-coordinate order into int64 vector."""
    parts = [p.strip() for p in str(text).split(",")]
    if any(p == "" for p in parts):
        raise ValueError("order must be comma-separated integers with no gaps")
    try:
        vals = [int(p) for p in parts]
    except ValueError as exc:
        raise ValueError(f"order holds a non-integer entry ({exc})") from exc
    return np.asarray(vals, dtype=np.int64)


def run_r1_eval(*, q: int, n: int, channel: str, param: float, k: int,
                seed: int, order, n_blocks: int, out) -> dict:
    """Run one frozen R1 EVAL and persist its summary (single-shot)."""
    from .algebra import make_gf32
    from .construction import evaluate_blocks, failure_summary

    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise TypeError("seed must be an integer provenance label")
    seed = int(seed)
    if seed in BANNED_SEEDS:
        raise ValueError(f"seed {seed} is a banned predecessor stream: never rerun or reuse it")
    order = np.asarray(order, dtype=np.int64).ravel()
    if order.shape != (int(n),) or set(order.tolist()) != set(range(int(n))):
        raise ValueError("order must be a full permutation of 0..N-1")
    outp = Path(out)
    if outp.exists():
        raise FileExistsError(f"refuse to overwrite existing out dir: {outp}")
    if isinstance(n_blocks, bool) or not isinstance(n_blocks, Integral) or int(n_blocks) < 1:
        raise ValueError("n_blocks must be a positive integer")
    if int(q) != 32:
        raise ValueError("R1 EVAL entry pins q=32 (frozen MVP field)")
    field = make_gf32()  # GF32, pinned poly 37; alpha=2 primitive
    rng = np.random.default_rng(seed)  # fresh sequential stream, consumed once
    res = evaluate_blocks(rng, field=field, alpha=2, q=int(q), n=int(n),
                          channel=channel, param=float(param),
                          disclosure_order=order, k=int(k),
                          n_blocks=int(n_blocks))
    summ = failure_summary(res)
    payload = {
        "entry": "eval_r1",
        "q": int(q),
        "n": int(n),
        "alpha": 2,
        "field": "GF32/poly37",
        "channel": res.channel,
        "param": float(res.param),
        "k": int(res.k),
        "seed": seed,
        "n_blocks": summ["n_blocks"],
        "n_exact": summ["n_exact"],
        "n_failed_total": summ["n_failed_total"],
        "n_impossible": summ["n_impossible"],
        "n_other_failure": summ["n_other_failure"],
        "n_nan": summ["n_nan"],
        "n_initial_error": summ["n_initial_error"],
        "fail_indices": list(summ["fail_indices"]),
        "prereg": "impossible counts as failed decode/non-exact inside the "
                  "denominator and is reported as its own class",
    }
    outp.mkdir(parents=True, exist_ok=False)
    (outp / "eval_summary.json").write_text(json.dumps(payload, indent=2))
    (outp / "disclosure_order.txt").write_text(",".join(str(int(v)) for v in order))
    return payload


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Phase 3-R1 one-shot synthetic EVAL")
    ap.add_argument("--q", required=True, type=int)
    ap.add_argument("--n", required=True, type=int)
    ap.add_argument("--channel", required=True, choices=("erasure", "qsc"))
    ap.add_argument("--param", required=True, type=float)
    ap.add_argument("--k", required=True, type=int)
    ap.add_argument("--seed", required=True, type=int)
    ap.add_argument("--order", required=True, type=str,
                    help="literal comma-separated full N-permutation")
    ap.add_argument("--n-blocks", required=True, type=int)
    ap.add_argument("--out", required=True, type=str)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = run_r1_eval(q=args.q, n=args.n, channel=args.channel,
                              param=args.param, k=args.k, seed=args.seed,
                              order=parse_order(args.order),
                              n_blocks=args.n_blocks, out=args.out)
    except (ValueError, TypeError, FileExistsError) as exc:
        print(f"eval_r1 refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({k: payload[k] for k in (
        "q", "n", "channel", "param", "k", "seed", "n_blocks",
        "n_exact", "n_failed_total", "n_impossible", "n_other_failure",
        "n_nan", "n_initial_error", "fail_indices")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
