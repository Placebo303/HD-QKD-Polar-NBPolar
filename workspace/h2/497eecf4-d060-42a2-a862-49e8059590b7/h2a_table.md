# H2a pm-ordering table (descriptive, 59 rows)

Pooled: n_blocks=15 n_evaluable=9 n_gap_exceeds_eps=8 eps=1e-12
P20S arm mapping: A_anchor_frozen_order=A(operational), B_spike_local_order=B(operational), O_true_l1_oracle=O(oracle, diagnostic only).

| packet | block | n | exact | nonexact | evaluable | fail_min_pm | exact_max_pm | gap | gap>eps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P20N | 0 | 4 | 0 | 4 | False | None | None | None | False |
| P20N | 1 | 4 | 0 | 4 | False | None | None | None | False |
| P20N | 2 | 4 | 0 | 4 | False | None | None | None | False |
| P20N | 3 | 4 | 2 | 2 | True | 0.7954019295969416 | 0.8924603616627651 | 0.09705843206582354 | True |
| P20O | 0 | 4 | 0 | 4 | False | None | None | None | False |
| P20O | 1 | 4 | 2 | 2 | True | 0.8551898630718846 | 0.8855957136697814 | 0.0304058505978968 | True |
| P20O | 2 | 4 | 2 | 2 | True | 0.8507799362778862 | 0.8938879980233024 | 0.04310806174541626 | True |
| P20O | 3 | 4 | 0 | 4 | False | None | None | None | False |
| P20O | 4 | 4 | 1 | 3 | True | 0.8020323236246235 | 0.8704057305978118 | 0.06837340697318828 | True |
| P20Q | 0 | 4 | 2 | 2 | True | 0.8174777632576917 | 0.8786631755228653 | 0.0611854122651736 | True |
| P20Q | 1 | 4 | 2 | 2 | True | 0.843433382262791 | 0.8921689975200733 | 0.048735615257282316 | True |
| P20Q | 2 | 4 | 2 | 2 | True | 0.8162702812301864 | 0.8765952135597158 | 0.0603249323295294 | True |
| P20Q | 3 | 4 | 2 | 2 | True | 0.8409936190420514 | 0.8894356161876981 | 0.048441997145646676 | True |
| P20Q | 4 | 4 | 0 | 4 | False | None | None | None | False |
| P20S | 0 | 3 | 2 | 1 | True | 0.8768295338061611 | 0.8740592319509212 | -0.002770301855239965 | False |

P20S block operational-only (A/B, O excluded): n_exact=1 n_nonexact=1 gap=-0.002770301855239965 gap>eps=False (same outcome as all-arm row).

X10 continuity (P20N+P20O subset, diff vs v1 literals):

| packet | block | recomputed_gap | v1_gap | abs_diff |
| --- | --- | --- | --- | --- | --- |
| P20N | 3 | 0.09705843206582354 | 0.09705843206582354 | 0.0 |
| P20O | 1 | 0.0304058505978968 | 0.0304058505978968 | 0.0 |
| P20O | 2 | 0.04310806174541626 | 0.04310806174541626 | 0.0 |
| P20O | 4 | 0.06837340697318828 | 0.06837340697318828 | 0.0 |
