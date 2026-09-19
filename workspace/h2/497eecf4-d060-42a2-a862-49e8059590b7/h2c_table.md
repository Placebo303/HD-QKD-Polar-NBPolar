# H2c concentration table (descriptive)

in-X overall: 35/38 = 0.9210526315789473; per-packet: P20N 12/14, P20O 11/11, P20Q 12/12, P20S 0/1.

New datum: {"arm": "B_spike_local_order", "first_error_coord": 0, "l2_fail_in_prefix": false, "l2_fail_in_prefix_u_domain": false, "note": "fail site outside disclosed prefix under both domain flags at boundary coord 0; out-of-X so excluded from the out-of-U-given-in-X conditioning"}

| packet | known | true | frac |
| --- | --- | --- | --- |
| P20N | 14 | 12 | 0.8571428571428571 |
| P20O | 11 | 11 | 1.0 |
| P20Q | 12 | 12 | 1.0 |
| P20S | 1 | 0 | 0.0 |

Out-of-U given in-X (u==False / u-known; P20S out-of-X fail excluded by conditioning):

| pool | u_known | outside_u | frac |
| --- | --- | --- | --- |
| P20O | 11 | 11 | 1.0 |
| P20Q | 12 | 12 | 1.0 |
| P20O_P20Q | 23 | 23 | 1.0 |

Coord distributions per (packet, arm/group):

| group | n | min | p50 | max | mean |
| --- | --- | --- | --- | --- | --- |
| P20N/A | 4 | 3 | 78.5 | 111 | 67.75 |
| P20N/B | 3 | 20 | 1009 | 5823 | 2284.0 |
| P20N/C | 4 | 3 | 78.5 | 111 | 67.75 |
| P20N/D | 3 | 20 | 1009 | 5823 | 2284.0 |
| P20N/operational | 7 | 3 | 81 | 5823 | 1017.5714285714286 |
| P20N/oracle | 7 | 3 | 81 | 5823 | 1017.5714285714286 |
| P20O/A | 3 | 14 | 45 | 153 | 70.66666666666667 |
| P20O/B | 1 | 35 | 35 | 35 | 35.0 |
| P20O/C | 5 | 14 | 78 | 274 | 112.8 |
| P20O/D | 2 | 35 | 78.0 | 121 | 78.0 |
| P20O/operational | 4 | 14 | 40.0 | 153 | 61.75 |
| P20O/oracle | 7 | 14 | 78 | 274 | 102.85714285714286 |
| P20Q/A | 5 | 163 | 411 | 1906 | 637.4 |
| P20Q/B | 1 | 5 | 5 | 5 | 5.0 |
| P20Q/C | 5 | 163 | 411 | 1906 | 637.4 |
| P20Q/D | 1 | 5 | 5 | 5 | 5.0 |
| P20Q/operational | 6 | 5 | 320.5 | 1906 | 532.0 |
| P20Q/oracle | 6 | 5 | 320.5 | 1906 | 532.0 |
| P20S/B | 1 | 0 | 0 | 0 | 0.0 |
| P20S/operational | 1 | 0 | 0 | 0 | 0.0 |

IR corroboration (stratified): IR-2 median P20Q-truncated=0.8830413818359375 (n=12), P20S full-block value=[0.432220458984375]; IR-4 pooled P20Q=66/320, P20S=0/48.
