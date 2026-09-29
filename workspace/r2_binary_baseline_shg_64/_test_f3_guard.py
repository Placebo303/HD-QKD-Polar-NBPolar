"""F3 guard test (Pre-EXECUTE round 1). NO real data: every real-data loader
is mocked to raise a sentinel, and all file I/O happens in a fresh temp
directory (THIS_DIR/RESULTS_PATH/DRY_RUN_DIR are monkeypatched to it).

Checks:
 G1 a full run refuses to start (SystemExit 2) when a top-level part_*.json exists,
    BEFORE any real-data loader is touched;
 G2 same when results.json exists;
 G3 files under dry_run/ do NOT trigger the guard (execution proceeds to the
    mocked loader, proving the guard let it through);
 G4 no --authorize -> refused;
 G5 dry-run output paths (_part_path / _construction_path / _run_one_block_entry)
    land under dry_run/, never at the top level, and are stamped dry_run=True;
 G6 _load_all_part_records ignores dry_run/ and rejects a dry_run=True record
    found at top level.
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


class RealDataTouched(Exception):
    pass


def _mock_loader():
    raise RealDataTouched("real-data loader was called")


def main() -> int:
    drv._load_nb_packet_module = _mock_loader  # any real-data path starts here
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        drv.THIS_DIR = tmp
        drv.RESULTS_PATH = tmp / "results.json"
        drv.DRY_RUN_DIR = tmp / "dry_run"

        # G4: no --authorize
        try:
            drv.main([])
            raise AssertionError("G4: expected SystemExit")
        except SystemExit as e:
            assert e.code == 2, e.code
        print("[G4] no --authorize -> refused: OK")

        # G3 first (clean dir + a dry_run/ part file only): guard must let it through
        (tmp / "dry_run").mkdir()
        (tmp / "dry_run" / "part_G2_00.json").write_text(json.dumps({"dry_run": True}))
        try:
            drv.main(["--authorize"])
            raise AssertionError("G3: expected RealDataTouched")
        except RealDataTouched:
            pass
        print("[G3] dry_run/ part file does not trigger guard (reached mocked loader): OK")

        # G1: fake top-level part file
        fake_part = tmp / "part_G2_00.json"
        fake_part.write_text(json.dumps({"session": "G2", "global_block_index": 0}))
        try:
            drv.main(["--authorize"])
            raise AssertionError("G1: guard did not refuse")
        except SystemExit as e:
            assert e.code == 2, e.code
        except RealDataTouched:
            raise AssertionError("G1: real-data loader reached despite pre-existing part file")
        print("[G1] pre-existing top-level part_*.json -> SystemExit(2) before any loader: OK")
        fake_part.unlink()

        # G7 (D_BIN_TWO_PASS): a pre-existing top-level pass-2 file also blocks a full run
        fake_scl = tmp / "scl_part_G2_00.json"
        fake_scl.write_text(json.dumps({"session": "G2", "global_block_index": 0}))
        try:
            drv.main(["--authorize"])
            raise AssertionError("G7: guard did not refuse")
        except SystemExit as e:
            assert e.code == 2, e.code
        except RealDataTouched:
            raise AssertionError("G7: loader reached despite scl_part file")
        print("[G7] pre-existing top-level scl_part_*.json -> SystemExit(2): OK")
        fake_scl.unlink()

        # G2: results.json
        drv.RESULTS_PATH.write_text("{}")
        try:
            drv.main(["--authorize"])
            raise AssertionError("G2: guard did not refuse")
        except SystemExit as e:
            assert e.code == 2, e.code
        except RealDataTouched:
            raise AssertionError("G2: loader reached despite results.json")
        print("[G2] pre-existing results.json -> SystemExit(2): OK")
        drv.RESULTS_PATH.unlink()

        # G5: dry-run paths
        pp = drv._part_path(0, "G2", dry_run=True)
        cp = drv._construction_path("G2", dry_run=True)
        assert pp.parent == tmp / "dry_run" and cp.parent == tmp / "dry_run", (pp, cp)
        assert drv._part_path(0, "G2").parent == tmp
        assert drv._construction_path("G2").parent == tmp
        (tmp / "dry_run" / "part_G2_00.json").unlink()
        drv._CTX.clear()  # empty ctx -> KeyError caught inside; still writes the record
        blk = {"session": "G2", "global_block_index": 0, "frame_start": 0, "frame_end": 127,
               "stratum_official": "A1_CAL_characterization", "stratum_task": "never_decoded"}
        drv._run_one_block_entry(blk, [], dry_run=True)
        rec = json.loads((tmp / "dry_run" / "part_G2_00.json").read_text())
        assert rec["dry_run"] is True and "DRY-RUN" in rec["note"], rec
        assert not list(tmp.glob("part_*.json")), "dry-run leaked a top-level part file"
        print("[G5] dry-run writes only under dry_run/, stamped dry_run=True/note: OK")

        # G6: record loading
        assert drv._load_all_part_records(tmp) == []
        (tmp / "part_G2_01.json").write_text(json.dumps({"dry_run": True}))
        try:
            drv._load_all_part_records(tmp)
            raise AssertionError("G6: expected AssertionError")
        except AssertionError as e:
            assert "dry_run=True" in str(e), e
        print("[G6] dry_run/ ignored; dry_run=True at top level rejected: OK")

    print("[test_f3_guard] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
