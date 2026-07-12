# Solar-assisted desiccant wheel — season summary (2026-06-10 → 2026-07-02)

_Run: 2026-07-12 09:15 UTC · code+data revision `1d50ec418`. Every pipeline run rewrites this stamp, so a fresh commit here proves the analysis actually ran on your upload._

## Data quality

| Quantity | Value |
|---|---|
| rows | 15960 |
| start | 2026-06-10 11:20:00+02:00 |
| end | 2026-07-02 15:18:00+02:00 |
| artefact_rows_masked | 16411 |
| plausibility_flags | 15668 |
| coverage_T_proc_in | 0.605 |
| coverage_T_reg_nach_HX | 0.946 |
| coverage_V_dot_III | 0.569 |

## Measured-period totals

**Not full-season totals** — integrals cover only instrumented periods (see coverage figures); no extrapolation is applied.

| Quantity | Value |
|---|---|
| Q_reg_kWh | 660.185 |
| Q_reg_coverage | 0.572 |
| Q_reg_net_kWh | 660.182 |
| E_el_kWh | 0.000 |

_Air-flow sources: process = None, regeneration = measured (m3/h assumed)._

## Solar contribution

| Quantity | Value |
|---|---|
| solar_fraction | 1.000 |
| solar_fraction_note | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |
| solar_collection_share_while_running | 0.206 |

## Energy-balance closure

| Quantity | Value |
|---|---|
| Q_reg_hydronic_kWh | 660.185 |
| Q_reg_air_kWh_window | 1.249 |
| Q_reg_hydronic_kWh_window | 8.821 |
| closure_window_hours | 3.200 |
| closure | 0.142 |

## KPIs by regeneration temperature bin

| T_reg_bin   |   hours |   Delta_x_mean_gkg |   eta_deh_mean |   Q_reg_kWh |   Q_reg_coverage |   Q_reg_net_kWh |   E_el_kWh |
|:------------|--------:|-------------------:|---------------:|------------:|-----------------:|----------------:|-----------:|
| (30, 35]    |  32.300 |              0.855 |          0.132 |      22.475 |            0.027 |          22.475 |      0.000 |
| (35, 40]    |  81.133 |              1.004 |          0.166 |      79.431 |            0.080 |          79.431 |      0.000 |
| (40, 45]    |  94.000 |              1.347 |          0.222 |     155.991 |            0.222 |         155.991 |      0.000 |
| (45, 50]    |  82.167 |              1.462 |          0.239 |     184.711 |            0.239 |         184.711 |      0.000 |
| (50, 55]    |  39.867 |              1.614 |          0.266 |      95.270 |            0.174 |          95.270 |      0.000 |
| (55, 60]    |  20.500 |              1.836 |          0.303 |      50.331 |            0.261 |          50.331 |      0.000 |

## Daily summary

| period                    |   Q_reg_kWh |   Q_reg_coverage |   Q_reg_net_kWh |   E_el_kWh |   T_proc_in_mean |   Phi_proc_in_mean |   T_reg_eff_mean |   Delta_x_proc_gkg_mean |   T_AU_mean |   T_SP_oben_mean |   runtime_h |   solar_fraction | solar_fraction_note                                                                                           |   solar_collection_share_while_running |
|:--------------------------|------------:|-----------------:|----------------:|-----------:|-----------------:|-------------------:|-----------------:|------------------------:|------------:|-----------------:|------------:|-----------------:|:--------------------------------------------------------------------------------------------------------------|---------------------------------------:|
| 2026-06-10 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           23.876 |                 nan     |      17.629 |           53.89  |       2.667 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-11 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           23.928 |                 nan     |      14.411 |           55.649 |       5.7   |              nan | nan                                                                                                           |                                nan     |
| 2026-06-12 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           23.273 |                 nan     |      15.311 |           53.643 |       6.633 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-13 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           23.396 |                 nan     |      17.585 |           48.614 |       7.267 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-14 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           21.525 |                 nan     |      15.032 |           51.668 |       4.533 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-15 00:00:00+02:00 |       5.592 |            0.103 |           5.59  |          0 |          nan     |            nan     |           21.707 |                 nan     |      14.449 |           49.733 |      13.733 |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0     |
| 2026-06-16 00:00:00+02:00 |      25.947 |            0.636 |          25.947 |          0 |           16.966 |             52.668 |           25.808 |                   0.399 |      17.111 |           42.031 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.103 |
| 2026-06-17 00:00:00+02:00 |      24.827 |            0.709 |          24.827 |          0 |           17.595 |             50.296 |           28.526 |                   0.646 |      19.734 |           39.35  |      17.1   |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.146 |
| 2026-06-18 00:00:00+02:00 |      25.255 |            0.588 |          25.255 |          0 |           20.02  |             39.994 |           42.734 |                   0.98  |      27.404 |           60.392 |       7     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0     |
| 2026-06-19 00:00:00+02:00 |      55.497 |            0.99  |          55.497 |          0 |           22.043 |             35.606 |           42.295 |                   1.105 |      26.075 |           58.031 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.247 |
| 2026-06-20 00:00:00+02:00 |      57.5   |            0.968 |          57.5   |          0 |           23.085 |             33.521 |           43.272 |                   1.118 |      26.426 |           60.922 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.174 |
| 2026-06-21 00:00:00+02:00 |      54.864 |            0.983 |          54.864 |          0 |           23.302 |             33.025 |           42.303 |                   1.258 |      25.205 |           56.326 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.208 |
| 2026-06-22 00:00:00+02:00 |      47.735 |            0.897 |          47.735 |          0 |           23.634 |             32.398 |           43.406 |                   1.296 |      25.631 |           57.259 |      22.133 |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.236 |
| 2026-06-23 00:00:00+02:00 |      53.673 |            0.964 |          53.673 |          0 |           23.892 |             31.893 |           44.355 |                   1.194 |      25.809 |           60.851 |      22.433 |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.25  |
| 2026-06-24 00:00:00+02:00 |      56.774 |            0.994 |          56.774 |          0 |           24.325 |             31.096 |           46.301 |                   1.226 |      27.308 |           62.528 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.296 |
| 2026-06-25 00:00:00+02:00 |      55.363 |            0.994 |          55.363 |          0 |           25.451 |             29.679 |           49.462 |                   1.671 |      28.789 |           69.068 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.267 |
| 2026-06-26 00:00:00+02:00 |      53.895 |            1     |          53.895 |          0 |           25.936 |             28.293 |           50.454 |                   1.496 |      29.692 |           78.493 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.349 |
| 2026-06-27 00:00:00+02:00 |      49.318 |            1     |          49.318 |          0 |           26.687 |             27.072 |           50     |                   1.623 |      31.677 |           71.409 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.221 |
| 2026-06-28 00:00:00+02:00 |      46.466 |            0.917 |          46.466 |          0 |           26.85  |             26.77  |           48.829 |                   1.519 |      30.095 |           67.69  |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.318 |
| 2026-06-29 00:00:00+02:00 |      32.682 |            0.68  |          32.682 |          0 |           25.884 |             28.484 |           41.931 |                   1.444 |      24.485 |           60.786 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.097 |
| 2026-06-30 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           37.83  |                 nan     |      23.738 |           51.226 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-07-01 00:00:00+02:00 |       6.891 |            0.118 |           6.891 |          0 |           23.743 |             32.405 |           36.903 |                   1.963 |      21.633 |           50.58  |      21     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.3   |
| 2026-07-02 00:00:00+02:00 |       6.727 |            0.198 |           6.727 |          0 |           22.814 |             33.855 |           28.811 |                   0.827 |      21.321 |           57.601 |       3.433 |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.301 |

## Figures

![overview](figures/overview.png)
![kpi_vs_treg](figures/kpi_vs_treg.png)
![psychrometric](figures/psychrometric.png)
![season_cumulative](figures/season_cumulative.png)

---
_Auto-generated by dw-analysis. KPI definitions and sources: see docs/KPI_DEFINITIONS.md._