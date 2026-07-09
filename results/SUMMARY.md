# Solar-assisted desiccant wheel — season summary (2026-06-10 → 2026-07-02)

## Data quality

| Quantity | Value |
|---|---|
| rows | 15960 |
| start | 2026-06-10 11:20:00+02:00 |
| end | 2026-07-02 15:18:00+02:00 |
| artefact_rows_masked | 8206 |
| plausibility_flags | 15489 |
| coverage_T_proc_in | 0.091 |
| coverage_T_reg_nach_HX | 0.946 |
| coverage_V_dot_III | 0.076 |

## Season / period totals

| Quantity | Value |
|---|---|
| Q_reg_kWh | 68.333 |
| Q_reg_coverage | 0.075 |
| E_el_kWh | 0.000 |

_Air-flow sources: process = None, regeneration = None._

## Solar contribution

| Quantity | Value |
|---|---|
| solar_fraction | 1.000 |
| solar_fraction_note | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |
| solar_collection_share_while_running | 0.206 |

## Energy-balance closure

| Quantity | Value |
|---|---|
| Q_reg_hydronic_kWh | 68.333 |
| closure_note | regeneration air flow (ch 120) unavailable — air-side balance not computable |

## KPIs by regeneration temperature bin

| T_reg_bin   |   hours |   Delta_x_mean_gkg |   eta_deh_mean |   Q_reg_kWh |   Q_reg_coverage |   E_el_kWh |
|:------------|--------:|-------------------:|---------------:|------------:|-----------------:|-----------:|
| (30, 35]    |  32.300 |              0.880 |          0.138 |      21.400 |            0.026 |      0.000 |
| (35, 40]    |  81.133 |              1.314 |          0.213 |       0.000 |            0.000 |      0.000 |
| (40, 45]    |  94.000 |              2.463 |          0.421 |       7.528 |            0.010 |      0.000 |
| (45, 50]    |  82.167 |              3.087 |          0.486 |       5.584 |            0.007 |      0.000 |
| (50, 55]    |  39.867 |            nan     |        nan     |       0.000 |            0.000 |      0.000 |
| (55, 60]    |  20.500 |            nan     |        nan     |       0.000 |            0.000 |      0.000 |

## Daily summary

| period                    |   Q_reg_kWh |   Q_reg_coverage |   E_el_kWh |   T_proc_in_mean |   Phi_proc_in_mean |   T_reg_eff_mean |   Delta_x_proc_gkg_mean |   T_AU_mean |   T_SP_oben_mean |   runtime_h |   solar_fraction | solar_fraction_note                                                                                           |   solar_collection_share_while_running |
|:--------------------------|------------:|-----------------:|-----------:|-----------------:|-------------------:|-----------------:|------------------------:|------------:|-----------------:|------------:|-----------------:|:--------------------------------------------------------------------------------------------------------------|---------------------------------------:|
| 2026-06-10 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           23.876 |                 nan     |      17.629 |           53.89  |       2.667 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-11 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           23.928 |                 nan     |      14.411 |           55.649 |       5.7   |              nan | nan                                                                                                           |                                nan     |
| 2026-06-12 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           23.273 |                 nan     |      15.311 |           53.643 |       6.633 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-13 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           23.396 |                 nan     |      17.585 |           48.614 |       7.267 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-14 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           21.525 |                 nan     |      15.032 |           51.668 |       4.533 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-15 00:00:00+02:00 |       5.592 |            0.103 |          0 |          nan     |            nan     |           21.707 |                 nan     |      14.449 |           49.733 |      13.733 |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0     |
| 2026-06-16 00:00:00+02:00 |      25.947 |            0.636 |          0 |           16.966 |             52.668 |           25.808 |                   0.388 |      17.111 |           42.031 |      24     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.103 |
| 2026-06-17 00:00:00+02:00 |      23.051 |            0.668 |          0 |           17.456 |             51.215 |           28.526 |                   0.631 |      19.734 |           39.35  |      17.1   |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.146 |
| 2026-06-18 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           42.734 |                 nan     |      27.404 |           60.392 |       7     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-19 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           42.295 |                 nan     |      26.075 |           58.031 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-20 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           43.272 |                 nan     |      26.426 |           60.922 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-21 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           42.303 |                 nan     |      25.205 |           56.326 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-22 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           43.406 |                 nan     |      25.631 |           57.259 |      22.133 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-23 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           44.355 |                 nan     |      25.809 |           60.851 |      22.433 |              nan | nan                                                                                                           |                                nan     |
| 2026-06-24 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           46.301 |                 nan     |      27.308 |           62.528 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-25 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           49.462 |                 nan     |      28.789 |           69.068 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-26 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           50.454 |                 nan     |      29.692 |           78.493 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-27 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           50     |                 nan     |      31.677 |           71.409 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-28 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           48.829 |                 nan     |      30.095 |           67.69  |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-29 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           41.931 |                 nan     |      24.485 |           60.786 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-06-30 00:00:00+02:00 |       0     |            0     |          0 |          nan     |            nan     |           37.83  |                 nan     |      23.738 |           51.226 |      24     |              nan | nan                                                                                                           |                                nan     |
| 2026-07-01 00:00:00+02:00 |       6.891 |            0.118 |          0 |           23.743 |             32.405 |           36.903 |                   1.909 |      21.633 |           50.58  |      21     |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.3   |
| 2026-07-02 00:00:00+02:00 |       6.727 |            0.198 |          0 |           22.814 |             33.855 |           28.811 |                   0.804 |      21.321 |           57.601 |       3.433 |                1 | no auxiliary heat source metered; all regeneration heat traced to solar storage (boundary: regeneration coil) |                                  0.301 |

## Figures

![overview](figures/overview.png)
![kpi_vs_treg](figures/kpi_vs_treg.png)
![psychrometric](figures/psychrometric.png)
![season_cumulative](figures/season_cumulative.png)

---
_Auto-generated by dw-analysis. KPI definitions and sources: see docs/KPI_DEFINITIONS.md._