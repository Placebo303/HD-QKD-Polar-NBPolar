# X02 preregistration — Tier-X non-claim probe (dependent-L2 operating-point search)

Status: FROZEN before any decoder call. This probe is Tier-X non-claim exploration
under `AGENTS.md` section 10.4. It writes exactly `prereg.md` and `results.json`
under the probe root, plus `/tmp` capture logs. No threshold verdict, candidate,
accepted token, attempt accounting, ledger update, commit or push.

## 1. Question

Find whether any N=256 injected dependent-L2 point combines high oracle recovery
(oracle mean exact rate >= 0.90) with a measurable operational-vs-oracle paired
exact gap (gap mean >= 0.05), so that a later Tier-Y gate at that point would be
informative rather than trivially weak. The 0.90 / 0.05 region is a descriptive
screening label only; this probe issues no pass/fail verdict and never expands
the grid if the region is empty.

## 2. Parameters (frozen; must not change after this prereg)

- N = 256, epsilon1 = 0.05, mean epsilon2 = 0.20.
- Dependence profiles (epsilon2 as a function of the high-layer source symbol
  value u1 in 0..31; all three means equal 0.20):
  - weak: `epsilon2(u1) = 0.14 + 0.12*u1/31`
  - medium: `epsilon2(u1) = 0.08 + 0.24*u1/31`
  - strong: `epsilon2(u1) = 0.02 + 0.36*u1/31`
- K1 in {45, 64, 96, 128}; K2 in {110, 140, 170, 200, 230} → exactly
  3 x 4 x 5 = 60 configurations.
- Seeds 2026091450, 2026091451, 2026091452; 32 paired blocks per
  configuration per seed (operational + oracle arms on the same block).
- Public tag master = seed + 10000, passed as `toeplitz_master`.
- D1 = `sorted(analytic_order(0.05, 256)[:K1])` and
  D2 = `sorted(analytic_order(0.20, 256)[:K2])` for every profile.
- Accepted runner `comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer.run_two_layer_block`,
  in memory, called once per block with the per-profile injected joint table
  (`layer_metric_tables`). The table is built from `layer_observation_matrix`
  blocks (`ph[hi, bh] * pl[al, bl]`); each profile table must satisfy
  `max|column_sum - 1| <= 1e-12` (asserted before decoding).
- Pairing/reuse choice: one block stream per (profile, seed) is sampled once
  with `np.random.default_rng(seed)` using the frozen dependent draw order
  (high uniform, low uniform, B_high erasure mask + replacements with
  epsilon1=0.05, B_low erasure mask + replacements with epsilon2(high)) and is
  reused across all 20 (K1, K2) configurations of that (profile, seed). The
  operational and oracle arms share each block and its disclosures by
  construction; block index is 0..31 in every configuration.
- P2 cross-u1 maximum difference, computed on the profile table before any
  decode and reported per configuration:
  `max over (b, u2) of (max_u1 P2[u1,b,u2] - min_u1 P2[u1,b,u2])`, i.e. the
  exact cross-u1 all-pairs maximum absolute difference.
- Per configuration and seed collect: operational exact/failures/undetected,
  oracle exact/failures/undetected, paired exact gap
  `(oracle_exact - op_exact)/32`, key-dependent disclosure bits (sum over both
  arms and all 32 paired blocks), block count.
- Descriptive ordering for the ranking: oracle mean exact rate descending,
  then gap magnitude descending, then total disclosed bits ascending, then
  profile / K1 / K2.
- Screening region (label only): oracle mean exact rate >= 0.90 AND paired gap
  mean >= 0.05.
- Master verification: recompute >=1 tag seed per family-level point on an
  independent MSB-first SHA-256 path and require exact equality.
- Only synthetic in-memory blocks and tables; no artifact/real data, no old-root
  writes, no code/workflow edits, no commit/push.

## 3. Command

The exact inline `python - <<'X02'` heredoc below is the frozen command. No probe
script file is written: the body is extracted byte-identically from this block
into `/tmp/x02_body.log` and executed via `python - < /tmp/x02_body.log`, and the
body asserts byte equality against this block. The verbatim full command text
and every execution attempt are preserved in `results.json`.

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - <<'X02'
import hashlib
import json
import re
import statistics
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from comparison_bench.src.comparison_bench.formal_ir import nbpolar as nb
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as tl

ROOT = Path("workspace/probes/nbpolar_x02_dependent_l2_point_search")
PREREG = ROOT / "prereg.md"
BODY_LOG = Path("/tmp/x02_body.log")
N = 256
OFF = 10000
SEEDS = (2026091450, 2026091451, 2026091452)
K1S = (45, 64, 96, 128)
K2S = (110, 140, 170, 200, 230)
PROFILE_FORMULAS = {
    "weak": "0.14 + 0.12*u1/31",
    "medium": "0.08 + 0.24*u1/31",
    "strong": "0.02 + 0.36*u1/31",
}
BLOCKS = 32
STARTED_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
LOG = []
prereg_sha = None
command_text = ""
prior = []


def log(message):
    LOG.append(str(message))
    print(message, flush=True)


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def eps2_vector(profile):
    u1 = np.arange(32, dtype=np.float64)
    if profile == "weak":
        e2 = 0.14 + 0.12 * u1 / 31.0
    elif profile == "medium":
        e2 = 0.08 + 0.24 * u1 / 31.0
    elif profile == "strong":
        e2 = 0.02 + 0.36 * u1 / 31.0
    else:
        raise ValueError(f"unknown profile {profile}")
    if not np.isclose(float(e2.mean()), 0.20, atol=1e-12):
        raise AssertionError(f"profile {profile} mean epsilon2 != 0.20")
    return e2


def profile_table(profile):
    e2 = eps2_vector(profile)
    ph = tl.layer_observation_matrix(0.05)
    a = np.arange(1024)
    ah, al = a // 32, a % 32
    b = np.arange(1024)
    bh, bl = b // 32, b % 32
    table = np.zeros((1024, 1024), dtype=np.float64)
    for hi in range(32):
        pl = tl.layer_observation_matrix(float(e2[hi]))
        idx = np.where(ah == hi)[0]
        table[np.ix_(idx, b)] = ph[hi, bh][None, :] * pl[al[idx][:, None], bl[None, :]]
    deviation = float(np.abs(table.sum(axis=0) - 1.0).max())
    if deviation > 1e-12:
        raise AssertionError(f"profile {profile} joint table norm deviation {deviation:.3e}")
    return table, deviation


def p2_cross_u1_maxdiff(p2):
    return float((p2.max(axis=0) - p2.min(axis=0)).max())


def reference_seed_bits(master, arm, index, length):
    prefix = f"nbpolar-p4-toeplitz-seed:{master}:{arm}:{index}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest())
        counter += 1
    out = np.empty(len(buf) * 8, dtype=np.uint8)
    i = 0
    for byte in buf:
        for shift in range(7, -1, -1):
            out[i] = (byte >> shift) & 1
            i += 1
    return out[:length]


def sample_stream(profile, seed):
    e2 = eps2_vector(profile)
    rng = np.random.default_rng(seed)
    stream = []
    for _ in range(BLOCKS):
        high = rng.integers(0, 32, size=N).astype(np.int64)
        low = rng.integers(0, 32, size=N).astype(np.int64)
        b_high = high.copy()
        erased = rng.random(N) < 0.05
        if bool(erased.any()):
            idx = np.where(erased)[0]
            b_high[idx] = rng.integers(0, 32, size=idx.size)
        b_low = low.copy()
        erased2 = rng.random(N) < e2[high]
        if bool(erased2.any()):
            idx = np.where(erased2)[0]
            b_low[idx] = rng.integers(0, 32, size=idx.size)
        stream.append((high, low, (32 * b_high + b_low).astype(np.int64)))
    return stream


def arm_counts(results):
    exact = sum(1 for r in results if r.exact)
    failures = sum(1 for r in results if r.outcome in ("decode_failed", "verify_failed", "resource_abort"))
    undetected = sum(1 for r in results if r.outcome == "undetected")
    disclosure = int(sum(r.key_dependent_bits for r in results))
    return exact, failures, undetected, disclosure


def body_from_command(command):
    lines = command.splitlines()
    start = next(i for i, line in enumerate(lines) if line.rstrip().endswith("<<'X02'"))
    stop = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "X02")
    return "\n".join(lines[start + 1:stop]) + "\n"


def build_output():
    global prereg_sha, command_text, prior
    ROOT.mkdir(parents=True, exist_ok=True)
    text = PREREG.read_text(encoding="utf-8")
    prereg_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    match = re.search(r"```bash\n(.*?)\n```", text, re.S)
    if match is None:
        raise RuntimeError("prereg bash command block not found")
    command_text = match.group(1)
    expected_body = body_from_command(command_text)
    executed_body = BODY_LOG.read_text(encoding="utf-8") if BODY_LOG.exists() else ""
    body_sha_match = hashlib.sha256(executed_body.encode("utf-8")).hexdigest() == hashlib.sha256(expected_body.encode("utf-8")).hexdigest()
    log(f"prereg_sha256={prereg_sha} body_sha_match={body_sha_match}")
    if (ROOT / "results.json").exists():
        try:
            prior = json.loads((ROOT / "results.json").read_text(encoding="utf-8")).get("commands", [])
        except Exception:
            prior = []

    profile_data = {}
    for profile in PROFILE_FORMULAS:
        table, deviation = profile_table(profile)
        p1, p2 = tl.layer_metric_tables(table)
        profile_data[profile] = {
            "p1": p1,
            "p2": p2,
            "norm_dev": deviation,
            "p2_maxdiff": p2_cross_u1_maxdiff(p2),
        }
        log(f"profile {profile}: p2_maxdiff={profile_data[profile]['p2_maxdiff']:.6f} norm_dev={deviation:.3e}")

    seed_bits = tl.seed_bits_for(N)
    master_points = [(profile, s) for profile in PROFILE_FORMULAS for s in SEEDS]
    master_checks = 0
    for profile, s in master_points:
        master = s + OFF
        for arm in ("operational", "oracle"):
            got = tl.block_toeplitz_seed_bits(arm, 0, master=master, bit_length=seed_bits)
            ref = reference_seed_bits(master, arm, 0, seed_bits)
            if not np.array_equal(got, ref):
                raise AssertionError(f"master tag-seed mismatch profile={profile} seed={s} arm={arm}")
            master_checks += 1
    masters = [s + OFF for _, s in master_points]
    if len(set(masters)) != len(masters):
        raise AssertionError("master = seed + 10000 is not injective")
    log(f"master check: {master_checks} tag seeds recomputed (independent MSB-first path), all match")

    streams = {}
    for profile in PROFILE_FORMULAS:
        for s in SEEDS:
            streams[(profile, s)] = sample_stream(profile, s)
    log(f"streams sampled: {len(streams)} streams x {BLOCKS} blocks")

    d1_sets = {k: tl.disclosure_coordinates(n=N, k=k, epsilon=0.05) for k in K1S}
    d2_sets = {k: tl.disclosure_coordinates(n=N, k=k, epsilon=0.20) for k in K2S}
    for k, d in d1_sets.items():
        if d.shape != (k,) or len(set(d.tolist())) != k:
            raise AssertionError(f"D1[{k}] contract violated")
    for k, d in d2_sets.items():
        if d.shape != (k,) or len(set(d.tolist())) != k:
            raise AssertionError(f"D2[{k}] contract violated")

    field = nb.make_gf32()
    configs = []
    leak_violations = 0
    nonfinite_arms = 0
    total_block_calls = 0
    for profile in PROFILE_FORMULAS:
        pd = profile_data[profile]
        for k1 in K1S:
            for k2 in K2S:
                seed_records = []
                for s in SEEDS:
                    op_results = []
                    oracle_results = []
                    for block_index, (high, low, bob) in enumerate(streams[(profile, s)]):
                        result = tl.run_two_layer_block(
                            block_index,
                            high,
                            low,
                            bob,
                            field=field,
                            p1_table=pd["p1"],
                            p2_table=pd["p2"],
                            d1=d1_sets[k1],
                            d2=d2_sets[k2],
                            n=N,
                            k1=k1,
                            k2=k2,
                            toeplitz_master=s + OFF,
                        )
                        op_results.append(result.operational)
                        oracle_results.append(result.oracle)
                        leak_violations += int(bool(result.operational.truth_leak_violation)) + int(bool(result.oracle.truth_leak_violation))
                        nonfinite_arms += int(bool(result.operational.nonfinite)) + int(bool(result.oracle.nonfinite))
                        total_block_calls += 1
                    op_exact, op_failures, op_undetected, op_disclosure = arm_counts(op_results)
                    or_exact, or_failures, or_undetected, or_disclosure = arm_counts(oracle_results)
                    seed_records.append({
                        "seed": s,
                        "op_exact": op_exact,
                        "op_failures": op_failures,
                        "op_undetected": op_undetected,
                        "oracle_exact": or_exact,
                        "oracle_failures": or_failures,
                        "oracle_undetected": or_undetected,
                        "paired_gap": (or_exact - op_exact) / float(BLOCKS),
                        "disclosure_bits": int(op_disclosure + or_disclosure),
                        "block_count": BLOCKS,
                    })
                op_rates = [r["op_exact"] / float(BLOCKS) for r in seed_records]
                or_rates = [r["oracle_exact"] / float(BLOCKS) for r in seed_records]
                gaps = [r["paired_gap"] for r in seed_records]
                disclosures = [float(r["disclosure_bits"]) for r in seed_records]
                configs.append({
                    "profile": profile,
                    "k1": k1,
                    "k2": k2,
                    "p2_maxdiff": pd["p2_maxdiff"],
                    "seeds": seed_records,
                    "mean": {
                        "op_exact_rate": float(statistics.mean(op_rates)),
                        "oracle_exact_rate": float(statistics.mean(or_rates)),
                        "gap": float(statistics.mean(gaps)),
                        "disclosure_bits": float(statistics.mean(disclosures)),
                    },
                    "sample_std": {
                        "op_exact_rate": float(statistics.stdev(op_rates)),
                        "oracle_exact_rate": float(statistics.stdev(or_rates)),
                        "gap": float(statistics.stdev(gaps)),
                        "disclosure_bits": float(statistics.stdev(disclosures)),
                    },
                    "range": {
                        "op_exact_rate": [float(min(op_rates)), float(max(op_rates))],
                        "oracle_exact_rate": [float(min(or_rates)), float(max(or_rates))],
                        "gap": [float(min(gaps)), float(max(gaps))],
                        "disclosure_bits": [float(min(disclosures)), float(max(disclosures))],
                    },
                })
                log(f"config {profile:6s} k1={k1:3d} k2={k2:3d}: oracle={statistics.mean(or_rates):.4f} op={statistics.mean(op_rates):.4f} gap={statistics.mean(gaps):+.4f}")

    if len(configs) != 60:
        raise AssertionError(f"expected 60 configurations, got {len(configs)}")
    if total_block_calls != 60 * len(SEEDS) * BLOCKS:
        raise AssertionError("paired block count mismatch")
    if leak_violations != 0:
        raise AssertionError(f"truth isolation violated in {leak_violations} arms")

    ranking = []
    for config in configs:
        ranking.append({
            "profile": config["profile"],
            "k1": config["k1"],
            "k2": config["k2"],
            "oracle_exact_rate_mean": config["mean"]["oracle_exact_rate"],
            "op_exact_rate_mean": config["mean"]["op_exact_rate"],
            "gap_mean": config["mean"]["gap"],
            "disclosure_bits_total": int(sum(r["disclosure_bits"] for r in config["seeds"])),
            "p2_maxdiff": config["p2_maxdiff"],
        })
    ranking.sort(key=lambda e: (
        -e["oracle_exact_rate_mean"],
        -abs(e["gap_mean"]),
        e["disclosure_bits_total"],
        e["profile"],
        e["k1"],
        e["k2"],
    ))
    for position, entry in enumerate(ranking, 1):
        entry["rank"] = position

    region = [
        c for c in configs
        if c["mean"]["oracle_exact_rate"] >= 0.90 and c["mean"]["gap"] >= 0.05
    ]
    screening_region = {
        "criterion": "oracle mean exact rate >= 0.90 AND paired gap mean >= 0.05",
        "label": "screening label only; not a pass/fail gate or verdict",
        "count": len(region),
        "found": bool(region),
        "configs": [
            {
                "profile": c["profile"],
                "k1": c["k1"],
                "k2": c["k2"],
                "oracle_exact_rate_mean": c["mean"]["oracle_exact_rate"],
                "op_exact_rate_mean": c["mean"]["op_exact_rate"],
                "gap_mean": c["mean"]["gap"],
                "p2_maxdiff": c["p2_maxdiff"],
            }
            for c in region
        ],
    }

    notes = {
        "pairing_choice": (
            "one block stream per (profile, seed) sampled once and reused across all 20 "
            "(K1, K2) configurations of that (profile, seed); operational and oracle arms "
            "share each block and its disclosures by construction"
        ),
        "sampling_order": (
            "per block: high uniform, low uniform, B_high erasure mask (epsilon1=0.05) plus "
            "replacements, B_low erasure mask (epsilon2(high)) plus replacements; explicit "
            "np.random.default_rng(seed) per (profile, seed), no global RNG"
        ),
        "p2_maxdiff_definition": (
            "max over (b, u2) of (max_u1 P2[u1,b,u2] - min_u1 P2[u1,b,u2]) computed on the "
            "injected profile joint table before any decode; equals the exact cross-u1 "
            "all-pairs maximum absolute difference"
        ),
        "table_normalization_max_col_deviation": {
            profile: profile_data[profile]["norm_dev"] for profile in PROFILE_FORMULAS
        },
        "disclosure_bits_definition": (
            "per seed, sum of key_dependent_bits over all 32 paired blocks and both arms "
            "(operational + oracle); each fully invoked arm discloses 5*(k1+k2)+64 bits"
        ),
        "master_verification": {
            "scheme": "public tag master = seed + 10000",
            "points_checked": len(master_points),
            "tag_seeds_recomputed": master_checks,
            "arms": ["operational", "oracle"],
            "block_index": 0,
            "independent_msb_first_sha256_match": True,
            "distinct_masters": len(set(masters)),
        },
        "sanity": {
            "paired_block_calls": total_block_calls,
            "truth_leak_violations": leak_violations,
            "nonfinite_arms": nonfinite_arms,
        },
        "execution_staging": (
            "the executed decoder body is the byte-identical prereg heredoc body staged via "
            "/tmp/x02_body.log; body_sha_match=" + str(body_sha_match)
        ),
        "scope": (
            "Tier-X non-claim probe; screening labels only, no threshold verdict, candidate, "
            "attempt accounting or scientific status"
        ),
    }

    failed_prior = any(entry.get("exit_code") not in (0, None) for entry in prior)
    execution_entry = {
        "n": len(prior) + 1,
        "kind": "frozen 60-config grid execution (Tier-X, decoder calls)",
        "started_utc": STARTED_UTC,
        "ended_utc": utcnow(),
        "exit_code": 0,
        "command_full_text": command_text,
        "stdout_tail": "\n".join(LOG[-30:]),
        "stderr_tail": "",
        "error_fixed": (
            "script-only fix applied after a failed prior attempt; see prior commands and notes"
            if failed_prior else None
        ),
    }

    return {
        "probe_id": "nbpolar_x02_dependent_l2_point_search",
        "tier": "X-non-claim",
        "created_utc": utcnow(),
        "prereg_sha256": prereg_sha,
        "interpreter": sys.executable,
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "n": N,
        "epsilon1": 0.05,
        "profile_epsilon2_formulas": PROFILE_FORMULAS,
        "k1_values": list(K1S),
        "k2_values": list(K2S),
        "seeds": list(SEEDS),
        "blocks_per_config_per_seed": BLOCKS,
        "configs": configs,
        "ranking": ranking,
        "screening_region": screening_region,
        "commands": prior + [execution_entry],
        "notes": notes,
    }


try:
    output = build_output()
    (ROOT / "results.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {ROOT / 'results.json'}")
except BaseException:
    tb = traceback.format_exc()
    print(tb, file=sys.stderr, flush=True)
    try:
        ROOT.mkdir(parents=True, exist_ok=True)
        failure_entry = {
            "n": len(prior) + 1,
            "kind": "frozen 60-config grid execution (Tier-X, decoder calls)",
            "started_utc": STARTED_UTC,
            "ended_utc": utcnow(),
            "exit_code": 1,
            "command_full_text": command_text,
            "stdout_tail": "\n".join(LOG[-30:]),
            "stderr_tail": "\n".join(tb.splitlines()[-30:]),
            "error_fixed": None,
        }
        partial = {
            "probe_id": "nbpolar_x02_dependent_l2_point_search",
            "tier": "X-non-claim",
            "created_utc": utcnow(),
            "prereg_sha256": prereg_sha,
            "status": "failed_attempt",
            "commands": prior + [failure_entry],
            "notes": {"failure": "see commands[-1].stderr_tail; frozen parameters unchanged"},
        }
        (ROOT / "results.json").write_text(json.dumps(partial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except BaseException:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
    raise
X02
```
