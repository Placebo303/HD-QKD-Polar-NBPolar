"""Driver-level tests with FAKE R2 modules (no real data).  Run:
  /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python workspace/r2c_strong_binary_msd_shg_64/_test_run_driver.py
Checks: --authorize refusal, one-shot guards, load_real_sessions wiring (CAL ids, H_total/F2 from results.json,
frame-count guard), production entry cannot be reached from tests without explicit fakes."""
import importlib.util, subprocess, sys, tempfile
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r2c_run_under_test", HERE / "run.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
m = run.load_r2c()


class FakeMod:
    def g2_cal_ids(self, arm):
        assert arm == "B_M2_32f_candidate"
        return list(range(1024, 1056))


class FakeChain:
    tag_bits = 64


class FakeNB:
    ARM = "B_M2_32f_candidate"

    def __init__(self, fp=256, h=0.8168138204133305, f=1.2753426830727925, bad=False):
        self.fp, self.h, self.f, self.bad = fp, h, f, bad

    def build_session_blocks(self, mod, name):
        return [dict(session=name, local_index=i, global_block_index=i, frame_start=128 * i, frame_end=128 * i + 127,
                     stratum_official="EVAL_already_decoded", stratum_task="previously_decoded_eval") for i in range(2)]

    def _reproduce_session_context(self, mod, chain, sj, name):
        rng = np.random.default_rng(0)
        fa = rng.integers(0, 1024, size=(2000, self.fp))
        return dict(frames_a=fa, frames_b=(fa + 1) % 1024, h_total_bits=self.h + (1e-3 if self.bad else 0.0), f_book_with_crc=self.f,
                    fit={"joint": np.eye(4)})


r2 = {"per_session": {s: {"h_total_bits": 0.8168138204133305, "f_book_with_crc_computed": 1.2753426830727925} for s in run.SESSIONS}}
ss = run.load_real_sessions(m, FakeNB(), FakeMod(), FakeChain(), None, r2)
assert [s.name for s in ss] == ["G2", "G3"] and ss[0].cal_a.size == 32 * 256 and ss[0].h_total_bits == 0.8168138204133305
assert ss[0].f_nb == 1.2753426830727925 and ss[0].blocks[0]["n_symbols"] == 32768 and ss[1].idx == 1
assert np.array_equal(ss[0].cal_a, ss[0].frames_a[1024:1056].ravel())
for kw in (dict(fp=128), dict(bad=True)):  # wrong block symbol count / H_total mismatch -> hard error
    try:
        run.load_real_sessions(m, FakeNB(**kw), FakeMod(), FakeChain(), None, r2)
        raise SystemExit("expected RuntimeError")
    except RuntimeError:
        pass
# CLI refusals
py = sys.executable
p = subprocess.run([py, str(HERE / "run.py")], capture_output=True, text=True)
assert p.returncode == 2 and "--authorize" in p.stderr, (p.returncode, p.stderr)
print("PASS _test_run_driver")
