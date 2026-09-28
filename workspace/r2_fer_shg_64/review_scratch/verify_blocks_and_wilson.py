#!/usr/bin/env python3
"""Pre-EXECUTE reviewer scratch script: PURE ARITHMETIC ONLY.

Re-derives (independently of run.py, by re-typing the same frozen
constants from DATA_LEDGER.md / T6_PACKET_SKELETON_20260928.md) the
64-block layout and stratum_task split, and independently checks the
Wilson-interval arithmetic used in run.py::_wilson. Reads NO data files,
executes NO decoder, touches nothing outside this directory.
"""

BLOCK_FRAMES = 128
A1_CAL_FIRST = 0
A1_CAL_BLOCKS = 8
CHARHELD_FIRST = 1056
CHARHELD_BLOCKS = 10
HELDOUT_FIRST = 1838
EVAL_FIRST = 2398
EVAL_BLOCKS = 14


def band(first, n):
    return [(first + i * BLOCK_FRAMES, first + i * BLOCK_FRAMES + BLOCK_FRAMES - 1) for i in range(n)]


def build_one_session():
    out = []
    for (s, e) in band(A1_CAL_FIRST, A1_CAL_BLOCKS):
        out.append(("A1_CAL_characterization", "never_decoded", s, e))
    for (s, e) in band(CHARHELD_FIRST, CHARHELD_BLOCKS):
        task = "heldout_model_selection" if e >= HELDOUT_FIRST else "never_decoded"
        out.append(("HELDOUT_model_selection", task, s, e))
    for (s, e) in band(EVAL_FIRST, EVAL_BLOCKS):
        out.append(("EVAL_already_decoded", "previously_decoded_eval", s, e))
    return out


def main():
    session = build_one_session()
    assert len(session) == 32, len(session)
    # last CHARHELD block end must be 2335 (62-frame remainder 2336-2397 unused)
    charheld = [b for b in session if b[0] == "HELDOUT_model_selection"]
    assert charheld[-1][3] == 2335, charheld[-1]
    assert charheld[0][2] == 1056, charheld[0]
    never_in_charheld = sum(1 for b in charheld if b[1] == "never_decoded")
    held_in_charheld = sum(1 for b in charheld if b[1] == "heldout_model_selection")
    assert (never_in_charheld, held_in_charheld) == (6, 4), (never_in_charheld, held_in_charheld)
    # first heldout-labeled block must start at 1824 (contains frame 1838)
    first_held_block = next(b for b in charheld if b[1] == "heldout_model_selection")
    assert first_held_block[2] == 1824, first_held_block
    assert first_held_block[2] <= HELDOUT_FIRST <= first_held_block[3]
    # EVAL band
    ev = [b for b in session if b[0] == "EVAL_already_decoded"]
    assert ev[0][2] == 2398 and ev[-1][3] == 4189, (ev[0], ev[-1])
    assert len(ev) == 14

    n_never = sum(1 for b in session if b[1] == "never_decoded")
    n_held = sum(1 for b in session if b[1] == "heldout_model_selection")
    n_eval = sum(1 for b in session if b[1] == "previously_decoded_eval")
    assert (n_never, n_held, n_eval) == (14, 4, 14), (n_never, n_held, n_eval)

    total_pooled = 2 * len(session)
    assert total_pooled == 64

    print("[block layout] OK: 8 A1_CAL + (6 never_decoded + 4 heldout_model_selection "
          "from the 10-block CHAR/HELDOUT band) + 14 EVAL = 32/session, 64 pooled.")
    print(f"[block layout] stratum_task per session = (never_decoded={n_never}, "
          f"heldout_model_selection={n_held}, previously_decoded_eval={n_eval})")

    # --- Wilson interval re-derivation (independent formula, z=1.96) ---
    def wilson(k, n, z=1.96):
        if n <= 0:
            return None
        p = k / n
        denom = 1.0 + z * z / n
        center = (p + z * z / (2.0 * n)) / denom
        half = z * ((p * (1.0 - p) / n + z * z / (4.0 * n * n)) ** 0.5) / denom
        return p, max(0.0, center - half), min(1.0, center + half)

    # cross-check against run.py's own _wilson() output on a few sample points
    import importlib.util
    spec = importlib.util.spec_from_file_location("r2run", r"D:\Code\HD-QKD_Polar_Comparison-nbpolar\workspace\r2_fer_shg_64\run.py")
    # NOTE: cannot import run.py directly (top-level main() does I/O on import guard? No --
    # run.py only executes main() under __main__ guard, so importing the module object is
    # safe/pure: it only defines functions/constants at import time). We only call _wilson,
    # a pure function, never main().
    r2run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r2run)  # pure at import time: only def/constants, no I/O (module docstring + __main__ guard)

    samples = [(0, 64), (1, 64), (3, 28), (5, 56), (34135, 34135)]
    for k, n in samples:
        mine = wilson(k, n)
        theirs = r2run._wilson(k, n)
        assert abs(mine[0] - theirs["p_hat"]) < 1e-12
        assert abs(mine[1] - theirs["lower"]) < 1e-9
        assert abs(mine[2] - theirs["upper"]) < 1e-9
        print(f"[wilson] k={k} n={n}: p_hat={mine[0]:.6f} CI=[{mine[1]:.6f},{mine[2]:.6f}] "
              f"(matches run.py._wilson)")

    # --- kdb / f_book arithmetic re-check ---
    disclosed_bits_per_coordinate = 5
    K1, K2, TAG_BITS, CRC_BITS = 319, 6492, 64, 16
    kdb_no_crc = disclosed_bits_per_coordinate * (K1 + K2) + TAG_BITS
    kdb_with_crc = kdb_no_crc + CRC_BITS
    assert kdb_no_crc == 34119, kdb_no_crc
    assert kdb_with_crc == 34135, kdb_with_crc
    print(f"[kdb] kdb_no_crc={kdb_no_crc} kdb_with_crc={kdb_with_crc} (matches prereg.md / T6 / AUTHORIZATION_PROMPT.md)")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
