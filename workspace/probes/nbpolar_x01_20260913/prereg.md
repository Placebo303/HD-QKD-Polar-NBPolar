# X01 preregistration — Tier-X non-claim probe

1. **Question.** Estimate seed-to-seed dispersion (mean / sample standard
   deviation / range over five seeds each) of the P5 K45, R1 three-arm, P4
   independent-layer and P4 dependent-L2 synthetic points at N=256, in order to
   size thresholds for the next Tier-Y decision gate. No claim, no pass/fail.

2. **Parameters (frozen; may not change after this prereg).** N=256.
   - **P5 family.** seeds 2026091400..2026091404, 300 blocks, K=45,
     epsilon=0.05, accepted `protocol.execute_blocks` semantics.
   - **R1 family.** seeds 2026091410..2026091414, 300 blocks, accepted three-arm
     semantics (static K45 / strict-stop / R1 advance, K=(29,33,37,41,45)).
   - **P4 independent family.** seeds 2026091420..2026091424, 96 blocks,
     epsilon1=0.05, epsilon2=0.20, K1=45, K2=110, accepted independent-layer
     injected table.
   - **P4 dependent family.** seeds 2026091430..2026091434, 96 blocks,
     epsilon1=0.05, `epsilon2(u1)=0.08+0.24*u1/31` (mean 0.20), K1=45, K2=110,
     injected joint table normalized to <=1e-12, and a pre-decode proof
     `max_{u1,u1',b,u2} |P2[u1,b,u2]-P2[u1',b,u2]| >= 0.10`; if the proof fails,
     that family is not decoded and the failure is recorded.
   - **Public tag master** = run_seed + 10000 for every family: P5/R1 masters are
     applied in-process via the module constant; P4 via its `toeplitz_master`
     parameter. Masters are probe-only.

3. **Command.** The exact inline command is the in-memory `python - <<'X01'`
   heredoc below (no probe-script file is written). Its verbatim full text and
   every execution/rerun are preserved in `results.json`. The probe writes ONLY
   `prereg.md` and `results.json`.

   ```bash
   cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
   /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - <<'X01'
   import json, statistics
   from pathlib import Path
   import numpy as np
   from comparison_bench.src.comparison_bench.formal_ir import nbpolar as nb

   ROOT = Path("workspace/probes/nbpolar_x01_20260913")
   N = 256
   OFF = 10000

   def agg(v):
       v = [float(x) for x in v]
       return {"per_seed": v, "mean": float(statistics.mean(v)),
               "sample_std": float(statistics.stdev(v)),
               "range": [float(min(v)), float(max(v))]}

   def counts(rs):
       return {
           "exact": sum(1 for r in rs if r.exact),
           "decode_failed": sum(1 for r in rs if r.outcome == "decode_failed"),
           "verify_failed": sum(1 for r in rs if r.outcome == "verify_failed"),
           "undetected": sum(1 for r in rs if r.outcome == "undetected"),
           "resource_abort": sum(1 for r in rs if r.outcome == "resource_abort"),
           "failure": sum(1 for r in rs if r.outcome in ("decode_failed", "verify_failed", "resource_abort")),
           "key_dependent_bits_total": int(sum(r.key_dependent_bits for r in rs)),
           "public_control_bits_total": int(sum(r.public_control_bits for r in rs)),
       }

   fam = {}

   # P5 K45 family (accepted protocol.execute_blocks semantics)
   fam["p5_k45"] = {}
   for s in range(2026091400, 2026091405):
       nb.protocol.TOEPLITZ_MASTER_SEED = s + OFF
       sm = nb.protocol.execute_blocks(run_seed=s, blocks=300, n=N, k=45).summary
       t = sm["outcome_totals"]
       fam["p5_k45"][s] = {
           "exact": t["exact"], "decode_failed": t["decode_failed"],
           "verify_failed": t["verify_failed"], "undetected": t["undetected"],
           "resource_abort": t["resource_abort"],
           "failure": t["decode_failed"] + t["verify_failed"] + t["resource_abort"],
           "key_dependent_bits_total": sm["key_dependent_bits_total"],
           "public_control_bits_total": sm["public_control_bits_total"],
       }

   # R1 three-arm family (static K45 / strict-stop / R1 advance)
   fam["r1_three_arm"] = {}
   for s in range(2026091410, 2026091415):
       nb.incremental.TOEPLITZ_MASTER_SEED = s + OFF
       field = nb.make_gf32()
       nested = nb.incremental.build_nested_schedule(n=N, epsilon=0.05, sizes=nb.incremental.FROZEN_K)
       rng = np.random.default_rng(s)
       arms = {"static": [], "strict_stop": [], "r1": []}
       for b in range(300):
           x, _y, logp = nb.generate_erasure_block(rng, 32, N, 0.05)
           three = nb.incremental.run_three_arm_block(b, x, logp, field=field, n=N,
                       sizes=nb.incremental.FROZEN_K, nested=nested)
           arms["static"].append(three["static_result"])
           arms["strict_stop"].append(three["strict_result"])
           arms["r1"].append(three["r1_result"])
       flat = {}
       for a, rs in arms.items():
           for k, val in counts(rs).items():
               flat[a + "_" + k] = val
       fam["r1_three_arm"][s] = flat

   # P4 injected-table families
   def eps2_u1():
       return 0.08 + 0.24 * np.arange(32) / 31.0

   def dependent_table():
       a = np.arange(1024); ah, al = a // 32, a % 32
       b = np.arange(1024); bh, bl = b // 32, b % 32
       ph = nb.two_layer.layer_observation_matrix(0.05)
       tbl = np.zeros((1024, 1024))
       e2 = eps2_u1()
       for hi in range(32):
           pl = nb.two_layer.layer_observation_matrix(float(e2[hi]))
           idx = np.where(ah == hi)[0]
           tbl[np.ix_(idx, b)] = ph[hi, bh][None, :] * pl[al[idx][:, None], bl[None, :]]
       return tbl

   def p2_gap(p2):
       return float(np.abs(p2 - p2[0:1]).max())

   def sample_dependent(rng):
       e2 = eps2_u1()
       high = rng.integers(0, 32, size=N).astype(np.int64)
       low = rng.integers(0, 32, size=N).astype(np.int64)
       b_high = high.copy(); er = rng.random(N) < 0.05
       if er.any():
           i = np.where(er)[0]; b_high[i] = rng.integers(0, 32, size=i.size)
       b_low = low.copy(); er2 = rng.random(N) < e2[high]
       if er2.any():
           i = np.where(er2)[0]; b_low[i] = rng.integers(0, 32, size=i.size)
       return high, low, (32 * b_high + b_low).astype(np.int64)

   def run_p4(name, seeds, table, dependent):
       p1, p2 = nb.two_layer.layer_metric_tables(table)
       gap = p2_gap(p2)
       fam[name] = {"p2_cross_u1_max_abs_diff": gap, "seeds": {}}
       if dependent and gap < 0.10:
           fam[name]["proof_failed"] = True
           return
       d1, d2 = nb.two_layer.frozen_disclosure_sets(n=N, k1=45, k2=110, epsilon1=0.05, epsilon2=0.20)
       field = nb.make_gf32()
       for s in seeds:
           rng = np.random.default_rng(s)
           op, orc = [], []
           for b in range(96):
               if dependent:
                   high, low, bob = sample_dependent(rng)
               else:
                   smp = nb.two_layer.sample_two_layer_block(rng, n=N, epsilon1=0.05, epsilon2=0.20)
                   high, low, bob = smp.high, smp.low, smp.bob
               r = nb.two_layer.run_two_layer_block(b, high, low, bob, field=field,
                       p1_table=p1, p2_table=p2, d1=d1, d2=d2, n=N, k1=45, k2=110,
                       toeplitz_master=s + OFF)
               op.append(r.operational); orc.append(r.oracle)
           flat = {}
           for a, rs in (("operational", op), ("oracle", orc)):
               for k, val in counts(rs).items():
                   flat[a + "_" + k] = val
           fam[name]["seeds"][s] = flat

   run_p4("p4_independent", range(2026091420, 2026091425),
          nb.two_layer.build_injected_joint_table(epsilon1=0.05, epsilon2=0.20), False)
   run_p4("p4_dependent_l2", range(2026091430, 2026091435), dependent_table(), True)

   agg_fam = {}
   for name, f in fam.items():
       if "seeds" in f:
           seeds = f["seeds"]
           entry = {"p2_cross_u1_max_abs_diff": f["p2_cross_u1_max_abs_diff"], "aggregate": {}}
           if seeds:
               entry["aggregate"] = {k: agg([seeds[s][k] for s in seeds])
                                     for k in sorted(next(iter(seeds.values())).keys())}
           if f.get("proof_failed"):
               entry["proof_failed"] = True
           agg_fam[name] = entry
       else:
           agg_fam[name] = {k: agg([f[s][k] for s in f]) for k in sorted(next(iter(f.values())).keys())}

   out = {"probe": "nbpolar_x01_20260913", "tier": "X-non-claim", "n": N,
          "master_offset": OFF, "per_seed": fam, "aggregate": agg_fam}
   ROOT.mkdir(parents=True, exist_ok=True)
   (ROOT / "results.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
   print("wrote", ROOT / "results.json")
   X01
   ```
