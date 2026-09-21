# OPERATOR PROMPT — NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION (copy-paste, self-contained)

You are the operator implementing a frozen Stage-1 packet. Do NOT redesign. Do NOT guess.
If the packet is ambiguous, STOP and report (second return condition). M2 is a CANDIDATE,
never the baseline. No production code exists yet for this packet — you write it to spec.

## 0. Setup (verify, do not change)

- Repo: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`
- Branch: `codex/nbpolar-phase0` — verify `cat .git/HEAD` shows
  `ref: refs/heads/codex/nbpolar-phase0`. Else STOP.
- Python: `.venv/bin/python` for EVERYTHING in Stage 1 (synthetic only; never import TimeTagger).
- Packet: `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION/TASK_PACKET.md`
  (authoritative; overrides this prompt on conflict).
- NEVER modify `sc.py`/`algebra.py`/`transform.py` or anything under `src/`/`experiments/`/`tools/`.
  NEVER open protected data or `.ttbin`. NEVER call a decoder. NEVER write outside `workspace/`.

## 1. Build (decoder-free; injected arrays + temp roots only)

1. `comparison_bench/src/comparison_bench/formal_ir/prior_m2.py` (NEW, beside — never inside —
   `formal_ir/nbpolar/`; numpy+stdlib only; ZERO imports from `nbpolar/`): `fit_m2_triple`,
   `build_m2_joint`, `build_m0_joint`, `build_prior(mode={"M2","M0"})`, vendored
   `split_symbol`/`combine_symbol`, `prob_rows_to_logp`. Per-session `(q0,q+1,q−1)` over
   δ∈{0,+1,−1}, rest→floor; `FLOOR=1e-15` literal; `MOD ∈ {LINEAR_ONLY,CIRCULAR}`,
   default `LINEAR_ONLY` (wrap cells `(0,1023)`/`(1023,0)` count as tail). M0 = raw-count MLE
   columns + 1e-15 PROBABILITY floor + renorm (P7 rule, never λ-formula). Layer factorization
   is caller-side via UNCHANGED frozen `derive_p1`/`derive_p2` (imported by caller/tests only).
2. `comparison_bench/tests/test_nbpolar_prior_m2.py` (NEW): tests T1–T11 per TASK_PACKET Spec 4
   (oracle ≤1e-12; M0 bit-exact `==0.0`; MOD 2-cell exact; logsumexp ≤1e-12; zero→`-inf` exact;
   packing exhaustive exact; equivariance ≤1e-12; decoder-free loopback; sc-frozen + no-import
   scans; synthetic K replay exact, H-proportional absent).
3. K re-split caller path via FROZEN `select_empirical_split` (imported, never reimplemented);
   `k_total` caller-supplied; fixed-K vs fixed-f DEFERRED; no real-data numbers.
4. `docs/SECURITY_MODEL.md` append per Spec 6 (CAL sacrificed; reveal diagnostic; no λ_prior;
   scope unchanged; M2 CANDIDATE label; 0-bit inventory skeleton, Release pattern).
5. `scripts/m2_prior_validation.py` (NEW) per Spec 5: `--freeze-config` (all 19 keys, null/absent
   ⇒ exit 2 listing keys) + `--stage-g1-nll`/`--stage-g2-decode` + `--authorized`
   (`action="store_true"`, absent ⇒ exit 2 reading nothing) + flag cross-check + 319/6492 pin +
   `workspace/`-confined `--out-root`; post-validation bodies exit 3 with zero data contact.

## 2. Verify (exact commands)

```
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
.venv/bin/python -m pytest comparison_bench/tests/test_nbpolar_prior_m2.py -p no:cacheprovider -q
.venv/bin/python scripts/m2_prior_validation.py --help
git diff --stat -- comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py comparison_bench/src/comparison_bench/formal_ir/nbpolar/algebra.py comparison_bench/src/comparison_bench/formal_ir/nbpolar/transform.py
grep -rE "from.*nbpolar|import.*nbpolar|from \. |import \." comparison_bench/src/comparison_bench/formal_ir/prior_m2.py
```

## 3. Return (exactly two conditions)

1. All-complete: S1-1..S1-8 PASS with evidence paths + pytest log + `git status` snippet.
2. Concrete blocker: failing command + exact error/traceback + attempted remedies + the SINGLE
   decision needed. "Still incomplete" is not a report.
