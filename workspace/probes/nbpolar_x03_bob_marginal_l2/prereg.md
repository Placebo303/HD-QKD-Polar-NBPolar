# X03 preregistration — Tier-X non-claim probe (Bob-marginal L2 prior)

Status: FROZEN before any decoder call (all table and seed-derivation checks below
are decoder-free). This probe is Tier-X non-claim exploration under `AGENTS.md`
section 10.4. It writes exactly `prereg.md` and `results.json` under the probe
root, plus `/tmp` capture logs. No threshold verdict, candidate, accepted token,
attempt accounting, ledger update, commit or push.

## 1. Question

Does a truth-free Bob-marginal L2 prior reduce the accepted P5 hard-candidate P2
penalty at the frozen dependent point, and what fraction of the hard-to-oracle
exact gap does it close? The closure fraction is descriptive only: this probe
issues no pass/fail verdict and adds no threshold.

## 2. Parameters (frozen; must not change after this prereg)

- Point: GF32 polynomial basis, primitive polynomial 37, alpha 2, natural order,
  N=256; epsilon1=0.05; strong dependent-L2 profile
  `epsilon2(u1) = 0.02 + 0.36*u1/31` (mean 0.20); K1=45, K2=140.
- Injected `[Alice,Bob]` table:
  `penalty_gate.build_dependent_joint_table(profile="strong", epsilon1=0.05)`;
  columns must sum to 1 within 1e-12 (asserted, never renormalized).
- Sampler: `penalty_gate.sample_dependent_block(rng, n=256, epsilon1=0.05,
  profile="strong")` with one explicit `np.random.default_rng(seed)` per seed;
  frozen draw order (high uniform, low uniform, B_high erasure mask +
  replacements, B_low erasure mask with per-position `epsilon2(high)` +
  replacements).
- Seeds: 2026091490..2026091494 (five); 128 shared blocks per seed (one stream
  per seed; each block is used by all three arms); public tag master = seed+10000.
- Disclosures: D1 = sorted worst-first `analytic_order(0.05, 256)[:45]`,
  D2 = sorted worst-first `analytic_order(0.20, 256)[:140]` (accepted P5 rule via
  `two_layer.frozen_disclosure_sets`); actual GF32 values including zeros.
- Three arms per block, all sharing one L1 source-domain hard candidate:
  - operational (hard candidate): `P2_hard = gather_p2_metrics(bob, high_hat,
    P2_table)`, provenance CANDIDATE_CONDITIONED;
  - marginal: `P2_marginal[b,u2] = sum_u1 P1[u1,b]*P2[u1,b,u2]` (table gathered at
    bob), provenance PRIOR_ONLY; receives Bob only -- never candidate, truth,
    oracle or APP; independently compared against direct joint-table
    marginalization `sum_high f[32*high+u2,b] / sum_A f[A,b]`, max abs error
    recorded and required <= 1e-12;
  - oracle (true-L1): `P2_true = gather_p2_metrics(bob, high_true, P2_table)`,
    provenance ORACLE_CONDITIONED.
- L1: one shared `build_p1_metrics` + PRIOR_ONLY metric + one fresh `sc_decode`
  call with D1/U1[D1]; `high_hat = sc1.x_hat`.
- L2 per arm: one fresh `sc_decode` call on that arm's metric with D2/U2[D2];
  `low_hat_arm = sc2.x_hat`.
- FROZEN label assembly: all three arms use the shared L1 hard candidate for the
  high half, `label_arm = low_hat_arm + 32*high_hat`. The candidate never enters
  the marginal metric/decoder; it is used only for label assembly and scoring.
- Tags: one 64-bit `toeplitz_tag` per arm per block from the accepted derivation
  `SHA-256('nbpolar-p4-toeplitz-seed:<master>:<arm>:<block>:<counter>')`,
  MSB-first, truncated to 10*256+63 = 2623 bits; per-arm namespaces
  ("operational", "marginal", "oracle"). Accepted
  `two_layer.block_toeplitz_seed_bits` is equality-checked for
  "operational"/"oracle"; the "marginal" namespace uses the identical local
  derivation because the accepted function is restricted to its two arms. Each
  tag consumes 2623 public control bits.
- Taxonomy per arm: exact (tag pass and label == true label), undetected (tag
  pass and not exact), verify_failed (tag mismatch), decode_failed (L1 or L2 SC
  exception / nonfinite marginals; no tag). If the shared L1 fails, all three
  arms are decode_failed for that block.
- Accounting per fully invoked arm: 5*(K1+K2)+64 = 989 key-dependent bits; 2623
  public control bits per tag invocation; a decode_failed arm counts only the
  disclosures it reached (5*K1 at L1 failure; 5*(K1+K2) at L2 failure).
- Four-cell tables (disjoint, exhaustive over planned blocks): hard-vs-marginal
  cells `both_exact/hard_only/marginal_only/neither`, and marginal-vs-oracle
  cells `both_exact/marginal_only/oracle_only/neither`; per seed and pooled.
- Gap closure: `(marginal_exact - hard_exact)/(oracle_exact - hard_exact)` per
  seed and pooled over the 640 blocks; null when the denominator is <= 0.
- Truth isolation: at least one block per seed (the first fully decoded block),
  after the marginal metric and all decisions exist, the truth arrays are
  adversarially mutated in place and the marginal metric (gathered probs and
  logp) plus decisions/disclosures must stay bitwise unchanged.
- Every execution attempt (including script-error reruns) is recorded in
  `results.json` commands with exit code, full command text, stdout/stderr tails
  and the script-only fix note; frozen parameters, models and seeds never change.

## 3. Command

The exact inline `python - <<'X03'` heredoc below is the frozen command. No probe
script file is written: the body is extracted byte-identically from this block
into `/tmp/x03_body.log` and executed via `python - < /tmp/x03_body.log`, and the
body asserts byte identity against this block (fail closed).

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - <<'X03'
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
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import penalty_gate as pg
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    Provenance,
    build_p1_metrics,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import sc_decode
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform
from comparison_bench.src.comparison_bench.formal_ir.shared import toeplitz_tag

ROOT = Path("workspace/probes/nbpolar_x03_bob_marginal_l2")
PREREG = ROOT / "prereg.md"
BODY_LOG = Path("/tmp/x03_body.log")
N = 256
Q = 32
K1 = 45
K2 = 140
EPS1 = 0.05
EPS2_MEAN = 0.20
PROFILE = "strong"
PROFILE_FORMULA = "0.02 + 0.36*u1/31"
SEEDS = (2026091490, 2026091491, 2026091492, 2026091493, 2026091494)
BLOCKS = 128
MASTER_OFFSET = 10000
TAG_BITS = 64
BITS_PER_COORD = 5
ALPHA = 2
ARMS = ("operational", "marginal", "oracle")
PROVENANCE = {
    "operational": Provenance.CANDIDATE_CONDITIONED,
    "marginal": Provenance.PRIOR_ONLY,
    "oracle": Provenance.ORACLE_CONDITIONED,
}
OUTCOMES = ("exact", "undetected", "verify_failed", "decode_failed")
STARTED_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
LOG = []
prereg_sha = None
command_text = ""
body_sha_match = None
prior = []
if (ROOT / "results.json").exists():
    try:
        prior = json.loads((ROOT / "results.json").read_text(encoding="utf-8")).get("commands", [])
    except Exception:
        prior = []


def log(message):
    LOG.append(str(message))
    print(message, flush=True)


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def arm_seed_bits(arm, block_index, master):
    length = tl.seed_bits_for(N)
    prefix = f"{tl.SEED_PREFIX}:{int(master)}:{arm}:{int(block_index)}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:length].astype(np.uint8)


def direct_marginal_table(table):
    joint = table.reshape(Q, Q, table.shape[1])
    colsum = table.sum(axis=0)
    return (joint.sum(axis=0) / colsum[None, :]).T


def decode_layer(logp, positions, disclosed, field):
    result = sc_decode(logp, field=field, alpha=ALPHA, known_positions=positions, known_values=disclosed)
    if bool(np.isnan(result.decision_metrics).any()) or bool(np.isposinf(result.decision_metrics).any()):
        raise RuntimeError("numeric nonfinite failure: invalid decision marginals")
    return result


def cell4(first_exact, second_exact, first_key, second_key):
    if first_exact and second_exact:
        return "both_exact"
    if first_exact:
        return first_key
    if second_exact:
        return second_key
    return "neither"


def body_from_command(command):
    lines = command.splitlines()
    start = next(i for i, line in enumerate(lines) if line.rstrip().endswith("<<'X03'"))
    stop = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "X03")
    return "\n".join(lines[start + 1:stop]) + "\n"


def stage_prereg():
    global prereg_sha, command_text, body_sha_match
    text = PREREG.read_text(encoding="utf-8")
    prereg_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    match = re.search(r"```bash\n(.*?)\n```", text, re.S)
    if match is None:
        raise RuntimeError("prereg bash command block not found")
    command_text = match.group(1)
    executed = BODY_LOG.read_text(encoding="utf-8") if BODY_LOG.exists() else ""
    body_sha_match = hashlib.sha256(executed.encode("utf-8")).hexdigest() == hashlib.sha256(
        body_from_command(command_text).encode("utf-8")
    ).hexdigest()
    log(f"prereg_sha256={prereg_sha} body_sha_match={body_sha_match}")
    if not body_sha_match:
        raise RuntimeError("staged body is not byte-identical to the prereg heredoc body")


def aggregate(values):
    vals = [float(v) for v in values]
    return {
        "mean": statistics.mean(vals),
        "sample_std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        "range": [min(vals), max(vals)],
    }


def build_output():
    ROOT.mkdir(parents=True, exist_ok=True)
    stage_prereg()

    table = pg.build_dependent_joint_table(profile=PROFILE, epsilon1=EPS1)
    table_dev = float(np.abs(table.sum(axis=0) - 1.0).max())
    if table_dev > 1e-12:
        raise AssertionError(f"injected table column deviation {table_dev:.3e} > 1e-12")
    p1_table, p2_table = tl.layer_metric_tables(table)
    p2_marginal_table = np.einsum("vb,vbw->bw", p1_table, p2_table)
    direct = direct_marginal_table(table)
    formula_err = float(np.abs(p2_marginal_table - direct).max())
    formula_pass = bool(formula_err <= 1e-12)
    if not formula_pass:
        raise AssertionError(f"marginal formula max abs error {formula_err:.3e} > 1e-12")
    log(f"formula_max_abs_error={formula_err:.3e} pass={formula_pass} table_col_dev={table_dev:.3e}")

    d1, d2 = tl.frozen_disclosure_sets(n=N, k1=K1, k2=K2, epsilon1=EPS1, epsilon2=EPS2_MEAN)
    if d1.shape != (K1,) or d2.shape != (K2,):
        raise AssertionError(f"disclosure shapes D1={d1.shape} D2={d2.shape}")
    if any(s in pg.BANNED_SEEDS for s in SEEDS):
        raise AssertionError("a frozen seed is banned by the accepted modules")
    field = nb.make_gf32()

    seed_checks = 0
    for s in SEEDS:
        for arm in ("operational", "oracle"):
            got = arm_seed_bits(arm, 0, s + MASTER_OFFSET)
            ref = tl.block_toeplitz_seed_bits(arm, 0, master=s + MASTER_OFFSET, bit_length=tl.seed_bits_for(N))
            if not np.array_equal(got, ref):
                raise AssertionError(f"seed derivation mismatch seed={s} arm={arm}")
            seed_checks += 1
    log(f"seed convention checks={seed_checks}; marginal uses the same derivation with arm='marginal'")

    full_arm_bits = BITS_PER_COORD * (K1 + K2) + TAG_BITS
    seed_bits = tl.seed_bits_for(N)
    per_seed = []
    truth_isolation = {
        int(s): {
            "sentinel_run": False,
            "block_index": None,
            "protected_arrays": 0,
            "marginal_metric_bitwise_unchanged": False,
        }
        for s in SEEDS
    }
    pooled_arms = {arm: {name: 0 for name in OUTCOMES} for arm in ARMS}
    pooled_kdb = {arm: 0 for arm in ARMS}
    pooled_public = {arm: 0 for arm in ARMS}
    pooled_tags = {arm: 0 for arm in ARMS}
    pooled_hm = {"both_exact": 0, "hard_only": 0, "marginal_only": 0, "neither": 0}
    pooled_mo = {"both_exact": 0, "marginal_only": 0, "oracle_only": 0, "neither": 0}
    pooled_hard_exact = 0
    pooled_marg_exact = 0
    pooled_oracle_exact = 0
    l1_failure_total = 0

    for s in SEEDS:
        master = s + MASTER_OFFSET
        rng = np.random.default_rng(s)
        arm_stats = {arm: {name: 0 for name in OUTCOMES} for arm in ARMS}
        arm_kdb = {arm: 0 for arm in ARMS}
        arm_public = {arm: 0 for arm in ARMS}
        arm_tags = {arm: 0 for arm in ARMS}
        cells_hm = {"both_exact": 0, "hard_only": 0, "marginal_only": 0, "neither": 0}
        cells_mo = {"both_exact": 0, "marginal_only": 0, "oracle_only": 0, "neither": 0}
        sentinel_done = False
        l1_failures = 0

        for block_index in range(BLOCKS):
            block = pg.sample_dependent_block(rng, n=N, epsilon1=EPS1, profile=PROFILE)
            high, low, bob = block.high, block.low, block.bob
            u1_true = polar_transform(high, field=field, alpha=ALPHA)
            u2_true = polar_transform(low, field=field, alpha=ALPHA)
            u1_disclosed = np.array(u1_true[d1], copy=True)
            u2_disclosed = np.array(u2_true[d2], copy=True)
            labels_true = (low + 32 * high).astype(np.int64)
            labels_true_bits = tl.labels_to_bits(labels_true)

            high_hat = None
            try:
                p1_probs = build_p1_metrics(bob[None, :], p1_table)[0]
                p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)
                sc1 = decode_layer(p1_metric.logp, d1, u1_disclosed, field)
                high_hat = np.array(sc1.x_hat, copy=True)
            except Exception:
                l1_failures += 1

            outcomes = {}
            protected = []
            marginal_low_hat = None
            marginal_label_hat = None
            if high_hat is None:
                for arm in ARMS:
                    outcomes[arm] = "decode_failed"
                    arm_stats[arm]["decode_failed"] += 1
                    arm_kdb[arm] += BITS_PER_COORD * K1
            else:
                p2_operational = gather_p2_metrics(bob[None, :], high_hat[None, :], p2_table)[0]
                p2_marginal = p2_marginal_table[bob]
                p2_oracle = gather_p2_metrics(bob[None, :], high[None, :], p2_table)[0]
                p2_by_arm = {"operational": p2_operational, "marginal": p2_marginal, "oracle": p2_oracle}
                for arm in ARMS:
                    metric = probs_to_symbol_metric(p2_by_arm[arm], provenance=PROVENANCE[arm])
                    if arm == "marginal":
                        protected.extend([p2_marginal, metric.logp])
                    try:
                        sc2 = decode_layer(metric.logp, d2, u2_disclosed, field)
                        low_hat = np.array(sc2.x_hat, copy=True)
                        label_hat = (low_hat + 32 * high_hat).astype(np.int64)
                        label_match = bool(np.array_equal(label_hat, labels_true))
                        seed_vec = arm_seed_bits(arm, block_index, master)
                        tag_pass = toeplitz_tag(labels_true_bits, seed_vec, TAG_BITS) == toeplitz_tag(
                            tl.labels_to_bits(label_hat), seed_vec, TAG_BITS
                        )
                        if tag_pass and label_match:
                            outcomes[arm] = "exact"
                        elif tag_pass:
                            outcomes[arm] = "undetected"
                        else:
                            outcomes[arm] = "verify_failed"
                        arm_kdb[arm] += full_arm_bits
                        arm_public[arm] += seed_bits
                        arm_tags[arm] += 1
                        if arm == "marginal":
                            marginal_low_hat = low_hat
                            marginal_label_hat = label_hat
                    except Exception:
                        outcomes[arm] = "decode_failed"
                        arm_kdb[arm] += BITS_PER_COORD * (K1 + K2)
                    arm_stats[arm][outcomes[arm]] += 1

            hard_exact = outcomes["operational"] == "exact"
            marg_exact = outcomes["marginal"] == "exact"
            oracle_exact = outcomes["oracle"] == "exact"
            cells_hm[cell4(hard_exact, marg_exact, "hard_only", "marginal_only")] += 1
            cells_mo[cell4(marg_exact, oracle_exact, "marginal_only", "oracle_only")] += 1

            if (not sentinel_done) and high_hat is not None:
                protected.extend([high_hat, u1_disclosed, u2_disclosed])
                if marginal_low_hat is not None:
                    protected.extend([marginal_low_hat, marginal_label_hat])
                snapshots = [np.array(item, copy=True) for item in protected]
                for arr, modulus in ((high, Q), (low, Q), (u1_true, Q), (u2_true, Q), (labels_true, 1024)):
                    arr[...] = (arr + 1) % modulus
                unchanged = all(
                    np.array_equal(np.asarray(item), snap) for item, snap in zip(protected, snapshots)
                )
                truth_isolation[int(s)] = {
                    "sentinel_run": True,
                    "block_index": int(block_index),
                    "protected_arrays": len(protected),
                    "marginal_metric_bitwise_unchanged": bool(unchanged),
                }
                sentinel_done = True

        hard_exact_count = arm_stats["operational"]["exact"]
        marg_exact_count = arm_stats["marginal"]["exact"]
        oracle_exact_count = arm_stats["oracle"]["exact"]
        denominator = oracle_exact_count - hard_exact_count
        closure = None
        if denominator > 0:
            closure = (marg_exact_count - hard_exact_count) / float(denominator)

        per_seed.append({
            "seed": int(s),
            "master": int(master),
            "blocks": BLOCKS,
            "l1_shared_decode_failures": int(l1_failures),
            "arms": {
                arm: {
                    "outcome_counts": {name: int(arm_stats[arm][name]) for name in OUTCOMES},
                    "failures": int(arm_stats[arm]["verify_failed"] + arm_stats[arm]["decode_failed"]),
                    "key_dependent_bits": int(arm_kdb[arm]),
                    "public_control_bits": int(arm_public[arm]),
                    "tag_invocations": int(arm_tags[arm]),
                }
                for arm in ARMS
            },
            "four_cell_tables": {
                "hard_vs_marginal": dict(cells_hm),
                "marginal_vs_oracle": dict(cells_mo),
            },
            "exact_gaps": {
                "marginal_minus_hard": int(marg_exact_count - hard_exact_count),
                "oracle_minus_hard": int(denominator),
            },
            "gap_closure_fraction": closure,
            "truth_isolation": truth_isolation[int(s)],
        })

        for arm in ARMS:
            for name in OUTCOMES:
                pooled_arms[arm][name] += arm_stats[arm][name]
            pooled_kdb[arm] += arm_kdb[arm]
            pooled_public[arm] += arm_public[arm]
            pooled_tags[arm] += arm_tags[arm]
        for name in cells_hm:
            pooled_hm[name] += cells_hm[name]
        for name in cells_mo:
            pooled_mo[name] += cells_mo[name]
        pooled_hard_exact += hard_exact_count
        pooled_marg_exact += marg_exact_count
        pooled_oracle_exact += oracle_exact_count
        l1_failure_total += l1_failures
        log(
            f"seed {s}: hard={hard_exact_count}/{BLOCKS} marginal={marg_exact_count}/{BLOCKS} "
            f"oracle={oracle_exact_count}/{BLOCKS} closure={closure} l1_fail={l1_failures}"
        )

    pooled_denominator = pooled_oracle_exact - pooled_hard_exact
    pooled_closure = None
    if pooled_denominator > 0:
        pooled_closure = (pooled_marg_exact - pooled_hard_exact) / float(pooled_denominator)

    closure_seeds = [r["gap_closure_fraction"] for r in per_seed if r["gap_closure_fraction"] is not None]
    aggregate_block = {
        "per_arm": {
            arm: {
                name: aggregate([r["arms"][arm]["outcome_counts"][name] for r in per_seed])
                for name in OUTCOMES
            }
            for arm in ARMS
        },
        "per_arm_failures": {
            arm: aggregate([r["arms"][arm]["failures"] for r in per_seed]) for arm in ARMS
        },
        "per_arm_key_dependent_bits": {
            arm: aggregate([r["arms"][arm]["key_dependent_bits"] for r in per_seed]) for arm in ARMS
        },
        "per_arm_public_control_bits": {
            arm: aggregate([r["arms"][arm]["public_control_bits"] for r in per_seed]) for arm in ARMS
        },
        "per_arm_tag_invocations": {
            arm: aggregate([r["arms"][arm]["tag_invocations"] for r in per_seed]) for arm in ARMS
        },
        "marginal_minus_hard_exact": aggregate([r["exact_gaps"]["marginal_minus_hard"] for r in per_seed]),
        "oracle_minus_hard_exact": aggregate([r["exact_gaps"]["oracle_minus_hard"] for r in per_seed]),
        "gap_closure_fraction_defined_seeds": len(closure_seeds),
        "gap_closure_fraction": aggregate(closure_seeds) if closure_seeds else None,
        "pooled": {
            "hard_exact": int(pooled_hard_exact),
            "marginal_exact": int(pooled_marg_exact),
            "oracle_exact": int(pooled_oracle_exact),
            "blocks": int(BLOCKS * len(SEEDS)),
            "gap_closure_fraction": pooled_closure,
            "four_cell_tables": {
                "hard_vs_marginal": dict(pooled_hm),
                "marginal_vs_oracle": dict(pooled_mo),
            },
            "arms": {
                arm: {
                    "outcome_counts": {name: int(pooled_arms[arm][name]) for name in OUTCOMES},
                    "key_dependent_bits": int(pooled_kdb[arm]),
                    "public_control_bits": int(pooled_public[arm]),
                    "tag_invocations": int(pooled_tags[arm]),
                }
                for arm in ARMS
            },
        },
        "l1_shared_decode_failures": int(l1_failure_total),
    }

    accounting = {
        "fully_invoked_arm_bits": int(full_arm_bits),
        "l1_disclosure_bits": int(BITS_PER_COORD * K1),
        "l2_disclosure_bits": int(BITS_PER_COORD * K2),
        "tag_bits": TAG_BITS,
        "public_control_bits_per_tag": int(seed_bits),
        "per_arm": {
            arm: {
                "key_dependent_bits": int(pooled_kdb[arm]),
                "public_control_bits": int(pooled_public[arm]),
                "tag_invocations": int(pooled_tags[arm]),
            }
            for arm in ARMS
        },
        "grand_total_key_dependent_bits": int(sum(pooled_kdb.values())),
        "grand_total_public_control_bits": int(sum(pooled_public.values())),
        "grand_total_tag_invocations": int(sum(pooled_tags.values())),
        "expected_all_fully_invoked": {
            "per_arm_key_dependent_bits": int(BLOCKS * len(SEEDS) * full_arm_bits),
            "per_arm_public_control_bits": int(BLOCKS * len(SEEDS) * seed_bits),
            "per_arm_tag_invocations": int(BLOCKS * len(SEEDS)),
            "grand_total_key_dependent_bits": int(len(ARMS) * BLOCKS * len(SEEDS) * full_arm_bits),
            "grand_total_public_control_bits": int(len(ARMS) * BLOCKS * len(SEEDS) * seed_bits),
        },
        "observed_equals_full_invocation": bool(
            all(pooled_tags[arm] == BLOCKS * len(SEEDS) for arm in ARMS)
        ),
    }

    truth_all = all(
        truth_isolation[int(s)]["sentinel_run"]
        and truth_isolation[int(s)]["marginal_metric_bitwise_unchanged"]
        for s in SEEDS
    )

    failed_prior = any(entry.get("exit_code") not in (0, None) for entry in prior)
    execution_entry = {
        "n": len(prior) + 1,
        "kind": "frozen three-arm per-block execution (Tier-X, decoder calls)",
        "started_utc": STARTED_UTC,
        "ended_utc": utcnow(),
        "exit_code": 0,
        "command_full_text": command_text,
        "stdout_tail": "\n".join(LOG[-30:]),
        "stderr_tail": "",
        "error_fixed": (
            "script-only fix after a failed prior attempt; frozen parameters unchanged; see notes.deviation"
            if failed_prior else None
        ),
    }

    return {
        "probe_id": "nbpolar_x03_bob_marginal_l2",
        "tier": "X-non-claim",
        "created_utc": utcnow(),
        "prereg_sha256": prereg_sha,
        "body_sha_match": bool(body_sha_match),
        "interpreter": sys.executable,
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "config": {
            "q": Q,
            "n": N,
            "field": {
                "name": "GF32 polynomial basis",
                "primitive_polynomial": 37,
                "alpha": ALPHA,
                "index_order": "natural",
            },
            "epsilon1": EPS1,
            "profile": PROFILE,
            "epsilon2_formula": PROFILE_FORMULA,
            "epsilon2_mean": EPS2_MEAN,
            "profile_table_max_column_deviation": float(table_dev),
            "k1": K1,
            "k2": K2,
            "seeds": [int(s) for s in SEEDS],
            "masters": [int(s) + MASTER_OFFSET for s in SEEDS],
            "blocks_per_seed": BLOCKS,
            "arms": list(ARMS),
            "arm_seed_namespaces": list(ARMS),
            "provenance": {arm: PROVENANCE[arm].value for arm in ARMS},
            "p2_marginal_formula": "P2_marginal[b,u2] = sum_u1 P1[u1,b] * P2[u1,b,u2]",
            "p2_direct_marginal": "sum_high f[32*high+u2,b] / sum_A f[A,b]",
            "label_assembly": (
                "label_arm = low_hat_arm + 32*high_hat; the shared L1 hard candidate high_hat "
                "supplies the high half for all three arms"
            ),
            "d1": [int(v) for v in d1],
            "d2": [int(v) for v in d2],
            "tag_bits": TAG_BITS,
            "fully_invoked_arm_bits": int(full_arm_bits),
            "public_control_bits_per_tag": int(seed_bits),
            "sampler": (
                "penalty_gate.sample_dependent_block(profile='strong', epsilon1=0.05) with one "
                "np.random.default_rng(seed) per seed; 128 shared blocks per seed"
            ),
            "seed_convention": (
                "SHA-256('nbpolar-p4-toeplitz-seed:<master>:<arm>:<block>:<counter>') MSB-first, "
                "arm namespaces operational/marginal/oracle; accepted block_toeplitz_seed_bits "
                "covers operational/oracle and is equality-checked; the marginal namespace uses "
                "the identical local derivation because the accepted function is restricted to "
                "its two arms"
            ),
        },
        "formula_max_abs_error": formula_err,
        "formula_max_abs_error_pass": formula_pass,
        "seed_convention_checks": int(seed_checks),
        "per_seed": per_seed,
        "aggregate": aggregate_block,
        "accounting": accounting,
        "truth_isolation": {
            "per_seed": {str(s): truth_isolation[int(s)] for s in SEEDS},
            "all_seeds_marginal_metric_bitwise_unchanged": bool(truth_all),
            "violations": int(
                sum(1 for s in SEEDS if not truth_isolation[int(s)]["marginal_metric_bitwise_unchanged"])
            ),
        },
        "commands": prior + [execution_entry],
        "notes": {
            "label_assembly_convention": (
                "FROZEN: all three arms use the same shared L1 source-domain hard candidate "
                "high_hat for the high half; label_arm = low_hat_arm + 32*high_hat. The candidate "
                "enters only label assembly/scoring, never the marginal metric or its decoder; "
                "the marginal metric (PRIOR_ONLY) receives Bob only."
            ),
            "arm_metrics": {
                "operational": "P2_hard = gather_p2_metrics(bob, high_hat, p2_table), CANDIDATE_CONDITIONED",
                "marginal": "P2_marginal_table[b,u2] = sum_u1 P1[u1,b]*P2[u1,b,u2] gathered at bob, PRIOR_ONLY",
                "oracle": "P2_true = gather_p2_metrics(bob, high_true, p2_table), ORACLE_CONDITIONED",
            },
            "scope": (
                "Tier-X non-claim probe; descriptive numbers only, no threshold verdict, candidate, "
                "accepted token, attempt accounting, ledger update, commit or push"
            ),
            "writes": (
                "exactly workspace/probes/nbpolar_x03_bob_marginal_l2/{prereg.md,results.json} "
                "plus /tmp logs"
            ),
            "execution_staging": (
                "the executed decoder body is the byte-identical prereg heredoc body staged via "
                "/tmp/x03_body.log; body_sha_match=" + str(bool(body_sha_match))
            ),
            "deviation": (
                "none" if not failed_prior else
                "script-only fixes after failed attempts; frozen parameters unchanged"
            ),
        },
    }


try:
    output = build_output()
    (ROOT / "results.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {ROOT / 'results.json'}")
except BaseException:
    tb = traceback.format_exc()
    print(tb, file=sys.stderr, flush=True)
    try:
        ROOT.mkdir(parents=True, exist_ok=True)
        failure_entry = {
            "n": len(prior) + 1,
            "kind": "frozen three-arm per-block execution (Tier-X, decoder calls)",
            "started_utc": STARTED_UTC,
            "ended_utc": utcnow(),
            "exit_code": 1,
            "command_full_text": command_text,
            "stdout_tail": "\n".join(LOG[-30:]),
            "stderr_tail": "\n".join(tb.splitlines()[-30:]),
            "error_fixed": None,
        }
        partial = {
            "probe_id": "nbpolar_x03_bob_marginal_l2",
            "tier": "X-non-claim",
            "created_utc": utcnow(),
            "prereg_sha256": prereg_sha,
            "body_sha_match": body_sha_match,
            "status": "failed_attempt",
            "commands": prior + [failure_entry],
            "notes": {"failure": "see commands[-1].stderr_tail; frozen parameters unchanged"},
        }
        (ROOT / "results.json").write_text(
            json.dumps(partial, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except BaseException:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
    raise
X03
```
