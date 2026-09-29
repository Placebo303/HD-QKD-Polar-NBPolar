"""Total-wall / two-pass unit test (Pre-EXECUTE round-2 F4 + D_BIN_TWO_PASS).
Fake monotonic clock, mocked block runners and construction (`prepare_fn`);
temp dir only; no real data, no decoder.

 W1 pass 1: clock advances during SC blocks; once elapsed > budget the remaining
    blocks are written status=not_started_total_wall_budget (no grid); the block
    already running finished; pass 2 then marks CA-SCL entries not started;
 W2 the check BEFORE a session's construction fires: the next session is not
    constructed (prepare_fn not called), its blocks recorded not_started;
 W3 already exceeded at the very start: no construction, no block at all;
 W4 dry-run: not_started record goes under dry_run/ only;
 W5 aggregate_results: block accounting 8 = contributing + error + not_started +
    resource_abort (+ no_grid_entries=0); not_started outside D; INSUFFICIENT;
 W6 (D_BIN_TWO_PASS) pass 2 truncated by the total wall: the SC primary arm has
    all 8 blocks, D unchanged with/without CA-SCL records, 4 CA-SCL blocks done,
    4 marked ca_scl_not_started_total_wall_budget, Table A untouched, Table B2
    covers only the finished blocks and says how many.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(THIS_DIR))

import run as drv  # noqa: E402


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t


def _blocks(session, offset):
    return [
        {"session": session, "global_block_index": offset + i, "local_index": i,
         "frame_start": 128 * i, "frame_end": 128 * i + 127,
         "stratum_official": "A1_CAL_characterization", "stratum_task": "never_decoded"}
        for i in range(4)
    ]


GP = {"sc_margin": 0.05, "kdb_sc": 8 * (4096 - 3000) + 64, "kdb_scl": 8 * (4096 - 3000) + 64 + 128,
      "f_book_sc": 1.2, "f_book_scl": 1.3, "_order": None,
      "layers": [{"layer_idx": 0, "ber": 0.01, "k": 3000}]}


def _setup(tmp, clock, *, budget=100.0, prepare_cost=10.0, sc_cost=35.0, scl_cost=1.0):
    drv.THIS_DIR = tmp
    drv.RESULTS_PATH = tmp / "results.json"
    drv.DRY_RUN_DIR = tmp / "dry_run"
    drv.DRY_RUN_DIR.mkdir(exist_ok=True)
    drv._CLOCK = clock
    drv.BUDGET_WALL_S_TOTAL = budget
    calls = {"prepare": [], "sc": [], "scl": []}

    def prepare(session):
        calls["prepare"].append(session)
        clock.t += prepare_cost
        return {"grid_points": [GP], "search_wall_s": prepare_cost}

    def fake_sc(block, grid_points, *, dry_run=False):
        calls["sc"].append((block["session"], block["global_block_index"]))
        clock.t += sc_cost
        rec = {"session": block["session"], "global_block_index": block["global_block_index"],
               "frame_start": block["frame_start"], "frame_end": block["frame_end"],
               "stratum_official": block["stratum_official"], "stratum_task": block["stratum_task"],
               "status": "ok", "dry_run": dry_run,
               "grid": [{"sc_margin": g["sc_margin"], "status": "ok", "exact": True, "verify_failed": False,
                         "decode_failed": False, "undetected": False} for g in grid_points]}
        drv._part_path(block["global_block_index"], block["session"], dry_run=dry_run).write_text(json.dumps(rec))

    def fake_scl(block, grid_points, *, dry_run=False):
        calls["scl"].append((block["session"], block["global_block_index"]))
        clock.t += scl_cost
        ents = [{"sc_margin": g["sc_margin"], "status": "ok",
                 "ca_scl_descriptive": {"n_codewords_applicable": 80, "n_codewords_msg_exact": 80,
                                        "msg_exact_rate": 1.0, "all_applicable_msg_exact": True}} for g in grid_points]
        drv._write_scl_part(block, ents, status="ok", dry_run=dry_run)

    drv._run_one_block_entry = fake_sc
    drv._run_scl_block_entry = fake_scl
    blocks_fn = lambda s: _blocks(s, 0 if s == "G2" else 32)  # noqa: E731
    return calls, prepare, blocks_fn


def _nb_parts_all_exact():
    return {
        (sess, off + i): {"status": "ok", "frame_start": 128 * i, "frame_end": 128 * i + 127,
                          "nb_sc_exact": True, "nb_scl_exact": True}
        for sess, off in (("G2", 0), ("G3", 32)) for i in range(4)
    }


def main() -> int:
    # ---- W1 + W5 ----
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        clock = FakeClock(0.0)
        calls, prepare, blocks_fn = _setup(tmp, clock)
        out = drv._run_sessions(("G2", "G3"), blocks_fn, prepare, 0.0)
        # both constructions first (t=20); SC blocks start at 20, 55, 90 (run, t->125); then not_started
        assert calls["prepare"] == ["G2", "G3"], calls["prepare"]
        assert calls["sc"] == [("G2", 0), ("G2", 1), ("G2", 2)], calls["sc"]
        rec3 = json.loads((tmp / "part_G2_03.json").read_text())
        assert rec3["status"] == drv.NOT_STARTED_STATUS and rec3["grid"] == [], rec3
        assert rec3["not_started_detail"]["checked_at"] == "before_block"
        for i in range(32, 36):
            r = json.loads((tmp / f"part_G3_{i:02d}.json").read_text())
            assert r["status"] == drv.NOT_STARTED_STATUS and r["not_started_detail"]["checked_at"] == "before_block", r
        assert len(out["not_started"]) == 5
        # pass 2: total wall already exceeded -> nothing run, the 3 SC blocks' CA-SCL entries marked not started
        assert calls["scl"] == [] and out["pass2_blocks_not_started"] == 3 and out["pass2_blocks_run"] == 0
        for i in range(3):
            r = json.loads((tmp / f"scl_part_G2_{i:02d}.json").read_text())
            assert r["status"] == drv.CA_SCL_NOT_STARTED and r["grid"][0]["status"] == drv.CA_SCL_NOT_STARTED, r
        print("[W1] pass 1: running block finished, later blocks not_started; pass 2 entries marked ca_scl_not_started: OK")

        recs = drv._load_all_part_records(tmp)
        assert len(recs) == 8
        scl_recs = drv._load_all_scl_records(tmp)
        assert len(scl_recs) == 3
        recs[0]["status"] = "error:RuntimeError"
        recs[1]["grid"] = [{"sc_margin": 0.05, "status": "resource_abort_rss_post_decode", "undetected": False}]
        agg = drv.aggregate_results(recs, out["grid_by_session"], expected_blocks=8, scl_records=scl_recs)
        acct = agg["block_accounting"]
        assert acct["n_blocks_contributing"] == 1, acct
        assert acct["n_error"] == 1 and acct["n_resource_abort"] == 1 and acct["n_not_started"] == 5, acct
        assert acct["n_no_grid_entries"] == 0
        assert acct["sum_of_categories"] == 8 == acct["expected_blocks"] and acct["consistent"] is True, acct
        assert len(agg["error_block_ids"]) == 1 and len(agg["not_started_block_ids"]) == 5
        m = agg["per_margin"][0]
        assert m["taxonomy_pooled"]["D_valid_denominator"] == 1
        assert m["insufficient"] is True and "INSUFFICIENT" in m["insufficient_note"]
        assert m["taxonomy_pooled"]["resource_abort"] == 1
        # the one contributing block's CA-SCL entry was not started -> reported as such, SC counts untouched
        ca = m["taxonomy_pooled"]["ca_scl_descriptive"]
        assert ca["n_sc_ok_entries"] == 1 and ca["n_ca_scl_not_started_entries"] == 1 and ca["coverage"] == 0.0, ca
        bad = drv.aggregate_results(recs[:-1], out["grid_by_session"], expected_blocks=8)
        assert bad["block_accounting"]["consistent"] is False
        print("[W5] 8 = 1 contributing + 1 error + 1 resource_abort + 5 not_started; D excludes not_started; INSUFFICIENT; drift flagged: OK")

    # ---- W2: pre-construction check fires ----
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        clock = FakeClock(0.0)
        calls, prepare, blocks_fn = _setup(tmp, clock, prepare_cost=110.0)
        out = drv._run_sessions(("G2", "G3"), blocks_fn, prepare, 0.0)
        assert calls["prepare"] == ["G2"], calls["prepare"]  # G3 never constructed
        for i in range(32, 36):
            r = json.loads((tmp / f"part_G3_{i:02d}.json").read_text())
            assert r["status"] == drv.NOT_STARTED_STATUS and r["not_started_detail"]["checked_at"] == "before_construction", r
        for i in range(4):  # G2 was constructed but budget already gone -> its blocks not started either
            r = json.loads((tmp / f"part_G2_{i:02d}.json").read_text())
            assert r["status"] == drv.NOT_STARTED_STATUS and r["not_started_detail"]["checked_at"] == "before_block", r
        assert calls["sc"] == [] and set(out["grid_by_session"]) == {"G2"} and len(out["not_started"]) == 8
        print("[W2] pre-construction check skipped G3 construction; all 8 blocks not_started: OK")

    # ---- W3: exceeded before anything starts ----
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        clock = FakeClock(500.0)
        calls, prepare, blocks_fn = _setup(tmp, clock)
        out = drv._run_sessions(("G2", "G3"), blocks_fn, prepare, 0.0)
        assert calls["prepare"] == [] and calls["sc"] == [] and calls["scl"] == []
        assert len(list(tmp.glob("part_*.json"))) == 8 and len(out["not_started"]) == 8
        assert not list(tmp.glob("scl_part_*.json")) and out["grid_by_session"] == {}
        print("[W3] exceeded at start: no construction, no block, 8 not_started: OK")

    # ---- W4: dry-run ----
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        clock = FakeClock(500.0)
        calls, prepare, blocks_fn = _setup(tmp, clock)
        out = drv._run_sessions(("G2", "G3"), blocks_fn, prepare, 0.0, dry_run=True)
        assert not list(tmp.glob("part_*.json")), "dry-run leaked to top level"
        assert len(list((tmp / "dry_run").glob("part_*.json"))) == 1 and len(out["not_started"]) == 1
        print("[W4] dry-run not_started record goes under dry_run/ only: OK")

    # ---- W6: pass 2 truncated (D_BIN_TWO_PASS) ----
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        clock = FakeClock(0.0)
        calls, prepare, blocks_fn = _setup(tmp, clock, budget=1000.0, prepare_cost=10.0, sc_cost=5.0, scl_cost=300.0)
        out = drv._run_sessions(("G2", "G3"), blocks_fn, prepare, 0.0)
        # pass 1: t = 20 (constructions) + 8*5 = 60, all 8 SC blocks ran
        assert len(calls["sc"]) == 8 and out["not_started"] == []
        # pass 2: blocks start at 60, 360, 660, 960 (<=1000 -> run, t->1260); remaining 4 not started
        assert len(calls["scl"]) == 4 == out["pass2_blocks_run"] and out["pass2_blocks_not_started"] == 4
        recs = drv._load_all_part_records(tmp)
        scl_recs = drv._load_all_scl_records(tmp)
        assert len(recs) == 8 and all(r["status"] == "ok" for r in recs)
        assert len(scl_recs) == 8
        n_ok = sum(1 for r in scl_recs if r["status"] == "ok")
        n_ns = sum(1 for r in scl_recs if r["status"] == drv.CA_SCL_NOT_STARTED)
        assert (n_ok, n_ns) == (4, 4), (n_ok, n_ns)
        for r in scl_recs:
            if r["status"] == drv.CA_SCL_NOT_STARTED:
                assert all(g["status"] == drv.CA_SCL_NOT_STARTED for g in r["grid"])
        agg_with = drv.aggregate_results(recs, out["grid_by_session"], expected_blocks=8, scl_records=scl_recs)
        agg_without = drv.aggregate_results(recs, out["grid_by_session"], expected_blocks=8, scl_records=[])
        pw, pwo = dict(agg_with["per_margin"][0]["taxonomy_pooled"]), dict(agg_without["per_margin"][0]["taxonomy_pooled"])
        ca_w = pw.pop("ca_scl_descriptive")
        pwo.pop("ca_scl_descriptive")
        assert pw == pwo and pw["D_valid_denominator"] == 8 and pw["exact"] == 8, (pw, pwo)  # SC primary arm complete, D unchanged
        assert agg_with["block_accounting"]["consistent"] and agg_with["n_blocks_contributing"] == 8
        assert ca_w["n_sc_ok_entries"] == 8 and ca_w["n_ca_scl_ok_entries"] == 4 and ca_w["n_ca_scl_not_started_entries"] == 4
        assert ca_w["coverage"] == 0.5, ca_w
        cross_with = drv.build_cross_comparison(recs, 0.05, _nb_parts_all_exact(), drv._scl_index(scl_recs))
        cross_without = drv.build_cross_comparison(recs, 0.05, _nb_parts_all_exact(), drv._scl_index([]))
        assert cross_with["table_A_nb_sc_vs_binary_sc"] == cross_without["table_A_nb_sc_vs_binary_sc"]
        assert cross_with["table_B1_nb_scl_vs_binary_sc"] == cross_without["table_B1_nb_scl_vs_binary_sc"]
        assert cross_with["table_A_nb_sc_vs_binary_sc"]["n"] == 8
        assert cross_with["table_B2_coverage"] == dict(cross_with["table_B2_coverage"], n_blocks_in_table_B2=4, n_blocks_matched_for_A_and_B1=8)
        assert cross_without["table_B2_coverage"]["n_blocks_in_table_B2"] == 0
        print("[W6] pass 2 truncated: SC 8/8 blocks, D=8 unchanged, 4 CA-SCL done / 4 marked ca_scl_not_started, Table A/B1 unchanged, B2 covers 4 of 8: OK")

    print("[test_total_wall] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
