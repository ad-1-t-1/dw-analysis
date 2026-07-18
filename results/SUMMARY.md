# Solar-assisted desiccant wheel — season summary (2026-06-10 → 2026-07-15)

_Run: 2026-07-18 20:25 UTC · code+data revision `fea63189b`. Every pipeline run rewrites this stamp, so a fresh commit here proves the analysis actually ran on your upload._

## Data quality

| Quantity | Value |
|---|---|
| rows | 25220 |
| start | 2026-06-10 11:20:00+02:00 |
| end | 2026-07-15 11:58:00+02:00 |
| artefact_rows_masked | 16411 |
| plausibility_flags | 17580 |
| coverage_T_proc_in | 0.437 |
| coverage_T_reg_nach_HX | 0.966 |
| coverage_V_dot_III | 0.374 |

## Measured-period totals

**Not full-season totals** — integrals cover only instrumented periods (see coverage figures); no extrapolation is applied.

| Quantity | Value |
|---|---|
| Q_reg_kWh | 706.972 |
| Q_reg_coverage | 0.376 |
| Q_reg_net_kWh | 706.970 |
| E_el_kWh | 0.000 |

_Air-flow sources: process = None, regeneration = measured (L/s assumed)._

## Solar contribution

| Quantity | Value |
|---|---|
| solar_fraction | 0.615 |
| Q_aux_kWh | 428.757 |
| Q_solar_kWh | 684.684 |
| solar_fraction_note | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |
| solar_collection_share_while_running | 0.203 |

## Energy-balance closure

| Quantity | Value |
|---|---|
| Q_reg_hydronic_kWh | 706.972 |
| Q_reg_air_kWh_window | 71.182 |
| Q_reg_input_kWh_window | 76.557 |
| closure_window_hours | 14.700 |
| closure | 0.930 |

## Air-to-water HX balance (regeneration coil)

Boundary = regeneration heating coil. Water side (`Q_hx_water` = circuit-III heat given up) vs air side (`Q_hx_air` = regeneration-air sensible gain across the coil). `hx_closure = Q_hx_air / Q_hx_water` — expected ≈ 0.8–1.0; the air side needs the ch 120 regeneration air flow, so the closure covers only the window where both sides are measured.

| Quantity | Value |
|---|---|
| Q_hx_water_kWh | 706.972 |
| Q_hx_air_kWh_window | 49.788 |
| Q_hx_water_kWh_window | 54.552 |
| hx_window_hours | 14.700 |
| hx_closure | 0.913 |

## Thermal-storage balance (energy in vs out + ΔU)

Boundary = stratified store. Charge (`Q_store_in`, circuit II) vs discharge (`Q_store_out`, circuit III = regeneration heat) plus the stored-energy change ΔU from the SP layer temperatures. Absolute ΔU, standby loss and closure require the tank volume (`config.STORAGE_VOLUME_M3`); until then ΔU is reported per m³.

| Quantity | Value |
|---|---|
| Q_store_out_kWh | 706.972 |
| Q_store_out_coverage | 0.376 |
| Q_store_in_kWh | 40.611 |
| Q_store_in_coverage | 0.069 |
| T_store_start_C | 41.200 |
| T_store_end_C | 70.090 |
| dU_store_kWh_per_m3 | 33.074 |
| dU_store_note | set config.STORAGE_VOLUME_M3 for absolute ΔU, standby loss and closure |

## KPIs by regeneration temperature bin

| T_reg_bin   |   hours |   Delta_x_mean_gkg |   eta_deh_mean |   Q_reg_kWh |   Q_reg_coverage |   Q_reg_net_kWh |   E_el_kWh |
|:------------|--------:|-------------------:|---------------:|------------:|-----------------:|----------------:|-----------:|
| (30, 35]    |  25.300 |              0.307 |          0.049 |      23.171 |            0.018 |          23.171 |      0.000 |
| (35, 40]    |  21.100 |              0.524 |          0.085 |       9.392 |            0.007 |           9.392 |      0.000 |
| (40, 45]    |  28.800 |              0.708 |          0.115 |      25.457 |            0.014 |          25.457 |      0.000 |
| (45, 50]    |  51.033 |              0.876 |          0.144 |      75.906 |            0.040 |          75.906 |      0.000 |
| (50, 55]    |  65.700 |              1.087 |          0.179 |     111.732 |            0.059 |         111.732 |      0.000 |
| (55, 60]    |  74.233 |              1.322 |          0.218 |     133.508 |            0.069 |         133.508 |      0.000 |
| (60, 65]    |  55.200 |              1.560 |          0.257 |      91.722 |            0.047 |          91.722 |      0.000 |
| (65, 70]    |  40.267 |              1.856 |          0.302 |      53.907 |            0.027 |          53.907 |      0.000 |

## Daily summary

| period                    |   Q_reg_kWh |   Q_reg_coverage |   Q_reg_net_kWh |   E_el_kWh |   T_proc_in_mean |   Phi_proc_in_mean |   T_reg_eff_mean |   Delta_x_proc_gkg_mean |   T_AU_mean |   T_SP_oben_mean |   runtime_h |   solar_fraction |   Q_aux_kWh |   Q_solar_kWh | solar_fraction_note                                                                                                        |   solar_collection_share_while_running |
|:--------------------------|------------:|-----------------:|----------------:|-----------:|-----------------:|-------------------:|-----------------:|------------------------:|------------:|-----------------:|------------:|-----------------:|------------:|--------------:|:---------------------------------------------------------------------------------------------------------------------------|---------------------------------------:|
| 2026-06-10 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           28.894 |                 nan     |      17.629 |           53.89  |       2.667 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-06-11 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           30.208 |                 nan     |      14.411 |           55.649 |       5.7   |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-06-12 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           32.3   |                 nan     |      15.311 |           53.643 |       6.633 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-06-13 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           32.684 |                 nan     |      17.585 |           48.614 |       7.267 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-06-14 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           26.832 |                 nan     |      15.032 |           51.668 |       4.533 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-06-15 00:00:00+02:00 |       5.592 |            0.103 |           5.59  |          0 |          nan     |            nan     |           29.087 |                 nan     |      14.449 |           49.733 |      13.733 |            0.878 |       0.774 |         5.592 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0     |
| 2026-06-16 00:00:00+02:00 |      25.947 |            0.636 |          25.947 |          0 |           16.966 |             52.668 |           30.074 |                   0.399 |      17.111 |           42.031 |      24     |            0.74  |       9.101 |        25.947 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.103 |
| 2026-06-17 00:00:00+02:00 |      24.827 |            0.709 |          24.827 |          0 |           17.595 |             50.296 |           40.081 |                   0.646 |      19.734 |           39.35  |      17.1   |            0.496 |      23.332 |        22.99  | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.146 |
| 2026-06-18 00:00:00+02:00 |      25.255 |            0.588 |          25.255 |          0 |           20.02  |             39.994 |           57.406 |                   0.98  |      27.404 |           60.392 |       7     |            0.568 |       8.903 |        11.717 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0     |
| 2026-06-19 00:00:00+02:00 |      55.497 |            0.99  |          55.497 |          0 |           22.043 |             35.606 |           53.07  |                   1.105 |      26.075 |           58.031 |      24     |            0.619 |      34.186 |        55.497 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.247 |
| 2026-06-20 00:00:00+02:00 |      57.5   |            0.968 |          57.5   |          0 |           23.085 |             33.521 |           53.768 |                   1.118 |      26.426 |           60.922 |      24     |            0.638 |      32.625 |        57.5   | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.174 |
| 2026-06-21 00:00:00+02:00 |      54.864 |            0.983 |          54.864 |          0 |           23.302 |             33.025 |           57.198 |                   1.258 |      25.205 |           56.326 |      24     |            0.551 |      44.662 |        54.864 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.208 |
| 2026-06-22 00:00:00+02:00 |      47.735 |            0.897 |          47.735 |          0 |           23.634 |             32.398 |           57.255 |                   1.296 |      25.631 |           57.259 |      22.133 |            0.582 |      31.429 |        43.731 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.236 |
| 2026-06-23 00:00:00+02:00 |      53.673 |            0.964 |          53.673 |          0 |           23.892 |             31.893 |           54.915 |                   1.194 |      25.809 |           60.851 |      22.433 |            0.654 |      27.024 |        50.972 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.25  |
| 2026-06-24 00:00:00+02:00 |      56.774 |            0.994 |          56.774 |          0 |           24.325 |             31.096 |           55.39  |                   1.226 |      27.308 |           62.528 |      24     |            0.695 |      24.97  |        56.774 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.296 |
| 2026-06-25 00:00:00+02:00 |      55.363 |            0.994 |          55.363 |          0 |           25.451 |             29.679 |           64.368 |                   1.671 |      28.789 |           69.068 |      24     |            0.594 |      37.801 |        55.363 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.267 |
| 2026-06-26 00:00:00+02:00 |      53.895 |            1     |          53.895 |          0 |           25.936 |             28.293 |           62.085 |                   1.496 |      29.692 |           78.493 |      24     |            0.658 |      28.005 |        53.895 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.349 |
| 2026-06-27 00:00:00+02:00 |      49.318 |            1     |          49.318 |          0 |           26.687 |             27.072 |           65.322 |                   1.623 |      31.677 |           71.409 |      24     |            0.561 |      38.594 |        49.318 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.221 |
| 2026-06-28 00:00:00+02:00 |      46.466 |            0.917 |          46.466 |          0 |           26.85  |             26.77  |           62.352 |                   1.519 |      30.095 |           67.69  |      24     |            0.593 |      31.836 |        46.466 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.318 |
| 2026-06-29 00:00:00+02:00 |      32.682 |            0.68  |          32.682 |          0 |           25.884 |             28.484 |           57.81  |                   1.444 |      24.485 |           60.786 |      24     |            0.547 |      27.064 |        32.682 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.097 |
| 2026-06-30 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           50.743 |                 nan     |      23.738 |           51.226 |      24     |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-01 00:00:00+02:00 |       6.891 |            0.118 |           6.891 |          0 |           23.743 |             32.405 |           49.394 |                   1.963 |      21.633 |           50.58  |      21     |            0.488 |       7.217 |         6.891 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.3   |
| 2026-07-02 00:00:00+02:00 |       6.727 |            0.127 |           6.727 |          0 |           22.814 |             33.855 |           38.423 |                   0.827 |      21.333 |           60.77  |       7.567 |            0.448 |       8.288 |         6.727 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.145 |
| 2026-07-03 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           38.324 |                 nan     |      19.254 |           60.484 |       8.267 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-04 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           36.295 |                 nan     |      20.257 |           61.496 |       7.7   |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-05 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           41.365 |                 nan     |      20.134 |           55.708 |      10.667 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-06 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           35.896 |                 nan     |      20.392 |           46.373 |      10.267 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-07 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           32.878 |                 nan     |      22.334 |           48.691 |       6.733 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-08 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           34.262 |                 nan     |      20.12  |           52.427 |       7.167 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-09 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           31.805 |                 nan     |      19.649 |           52.071 |       7.9   |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-10 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           32.571 |                 nan     |      20.037 |           53.297 |       7.333 |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-11 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           30.229 |                 nan     |      22.832 |           68.237 |       5.4   |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-12 00:00:00+02:00 |       0     |            0     |           0     |          0 |          nan     |            nan     |           34.43  |                 nan     |      24.283 |           77.113 |       8.1   |          nan     |     nan     |       nan     | nan                                                                                                                        |                                nan     |
| 2026-07-13 00:00:00+02:00 |       7.587 |            0.083 |           7.587 |          0 |           24.647 |             33.958 |           34.366 |                   1.022 |      25.398 |           78.774 |       8.1   |            0.92  |       0.658 |         7.587 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.35  |
| 2026-07-14 00:00:00+02:00 |      28.68  |            0.307 |          28.68  |          0 |           24.072 |             35.078 |           39.115 |                   1.082 |      23     |           77.18  |       9.167 |            0.734 |      10.389 |        28.68  | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.298 |
| 2026-07-15 00:00:00+02:00 |      10.521 |            0.212 |          10.521 |          0 |           23.412 |             36.813 |           35.116 |                   0.609 |      20.996 |           73.507 |       4.033 |            0.862 |       1.683 |        10.521 | electric booster heater included (thermally inferred — not electrically metered); SF over timesteps where both sides known |                                  0.314 |

## Figures

![overview](figures/overview.png)
![kpi_vs_treg](figures/kpi_vs_treg.png)
![psychrometric](figures/psychrometric.png)
![season_cumulative](figures/season_cumulative.png)

---
_Auto-generated by dw-analysis. KPI definitions and sources: see docs/KPI_DEFINITIONS.md._