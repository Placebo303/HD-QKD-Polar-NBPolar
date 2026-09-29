# prereg — r2c-strong-binary-msd-shg-64 (Tier-Y, one-shot; frozen by the contract)

1. Question: on the same 64-block SHG `_1`/`_2` pool as R2/R2B, what is the block failure rate of hard-prefix conditional MSD + SCL (L=16, no CRC, DE construction, global-margin allocation) at f = F1 (1.20), F2 (NB f_book_with_crc per session), F3 (design-set FER≈0.03 point), F4 (F3+0.10)?
2. Parameters: contract `docs/nbpolar/R2C_STRONG_BINARY_MSD_CONTRACT_20260929.md` §3–§8 (N=32768/layer, 10 layers, DE M_root=4096/m=1024/seed 20260929, M_design=256, tag 64 bits, budget 6 h / 6 GiB), plus the operator-fixed constants listed in `TASK_PACKET.md` §1/`PROMPT.md` (F3 bracket [1.10,1.90] with 4 bisection steps; RNG seed bases 20260929).
3. Command: see `AUTHORIZATION_PROMPT.md` (execution command block). Allowed sentence pattern (contract §0): "在 SHG `_1`/`_2` 同一 64 块池上，硬前缀 MSD + SCL(L=16，无 CRC，DE 构造，全局 margin 码率分配)在 f=… 时块失败率为 …"; no optimality claim, no general "binary vs NB" statement.
