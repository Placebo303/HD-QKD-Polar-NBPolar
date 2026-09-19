# H2b fail-site ratio table (descriptive, L2-fail rows only)

r_fail = fh/pm; r_nbhd = nm/pm; oracle arms separate from operational; O oracle has no fail row.

| split | n | min | p50 | max | mean |
| --- | --- | --- | --- | --- | --- |
| r_fail overall | 38 | 0.4712762603167972 | 2.2650675840331176 | 10.342065657551027 | 2.046216027828529 |
| r_nbhd overall | 38 | 0.6576695379102871 | 0.9500050964140138 | 1.7262965796433776 | 1.0056509293164801 |
| r_fail P20N | 14 | 0.5360591381629638 | 2.246075693397315 | 2.438126083905791 | 1.818024577202116 |
| r_fail P20O | 11 | 0.4712762603167972 | 2.22978624741752 | 10.342065657551027 | 2.3743470992439315 |
| r_fail P20Q | 12 | 0.5078126378967577 | 2.415602720269016 | 2.612721066327418 | 2.1333990434911683 |
| r_fail P20S | 1 | 0.5852583630772091 | 0.5852583630772091 | 0.5852583630772091 | 0.5852583630772091 |
| r_fail A | 12 | 0.4712762603167972 | 2.3066395412120473 | 2.612721066327418 | 1.9061979281661963 |
| r_fail B | 6 | 0.5136019241149791 | 1.43590097197188 | 2.565132245191564 | 1.4636450282874713 |
| r_fail C | 14 | 0.4712762603167972 | 2.3238151239118943 | 2.612721066327418 | 1.9686633061118766 |
| r_fail D | 6 | 0.5136019241149791 | 2.244659695848533 | 10.342065657551027 | 3.089779577366441 |
| r_fail O | 0 | None | None | None | None |

Strongest r_fail: {"packet": "P20O", "block_index": 0, "arm": "D_alt_L2_oracle", "fh": 9.179909090014934, "pm": 0.887628196724165, "r_fail": 10.342065657551027}

v1 continuity: v1 n=37 median=2.283522870993239 mean=2.0857013701191054 range=[0.4712762603167972, 10.342065657551027].

IR-2 corroboration, stratified by scope (no pooling): P20Q truncated n=12 median=0.8830413818359375; P20S full-block n=1 value=[0.432220458984375] (summary crosscheck diff=0.0).

P20R context (read-only, NOT joined): [{"arm": "A_frozen-order_operational", "rank_pct": 0.999664306640625}, {"arm": "B_new-order_operational", "rank_pct": 0.329193115234375}, {"arm": "C_frozen-order_oracle", "rank_pct": 0.999664306640625}, {"arm": "D_new-order_oracle", "rank_pct": 0.329193115234375}]
