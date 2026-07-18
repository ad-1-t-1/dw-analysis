# KPI definitions — exact equations, units, sources

Different papers define the "same" KPI differently. The definitions used in
this repo are fixed here; tests in `tests/test_kpi.py` pin the numerics.

All psychrometric properties from CoolProp `HAPropsSI` (ASHRAE RP-1485
real-gas model; Herrmann, Kretzschmar & Gatley 2009). Humidity ratio *x* is
per kg **dry air**; all mass flows of air are **dry-air** mass flows
(m_dot_da = V_dot / v_da, `HAPropsSI('Vda', …)`), because dry-air mass is the
conserved quantity across the wheel.

| KPI | Symbol | Equation | Units | Source of definition |
|---|---|---|---|---|
| Moisture removal rate | MRR | ṁ_da,p · (x_p,in − x_p,out) | kg/s | Angrisani et al. 2012, Appl. Energy 92, Eq. (2) — VERIFIED against PDF (they use moist-air ρ₁V̇; repo uses dry-air ṁ_da, see intro note); same in Comino et al. 2020 ATE, Eq. MRC = ṁ·Δω — VERIFIED |
| Water removed (period) | m_w | ∫ MRR dt (trapezoid, gaps excluded) | kg | — |
| Dehumidification effectiveness | η_deh | (x_p,in − x_p,out)/x_p,in | – | Angrisani et al. 2012, Eq. (1) — VERIFIED against PDF; also used by De Antonellis et al. 2015 (paper not in library) |
| Wheel moisture effectiveness | ε_w | (x_p,in − x_p,out)/(x_p,in − x_r,in) | – | attributed to Mandegari & Pahlavanzadeh 2009, Energy 34 — CITATION UNVERIFIED (paper not in library; their headline metric is an *adiabatic* effectiveness). Obtain paper before citing in the thesis. |
| Regeneration heat input | Q̇_reg | ρ_w(T)·V̇_III·c_p,w(T)·(T_VL,III − T_RL,III) | W | hydronic heat balance; water props CoolProp IAPWS-97 |
| Regeneration heat (period) | Q_reg | ∫ Q̇_reg dt | kWh | — |
| Latent heat flow | Q̇_lat | MRR · Δh_vap(0 °C) = MRR · 2 501 kJ/kg | W | ASHRAE Fundamentals 2021 Ch. 1 reference state |
| Thermal COP (period) | COP_th | Q_lat / Q_reg,total  (Q_reg,total = hydronic + electric booster) | – | analogue of Angrisani et al. 2012 DCOP, Eq. (3) — VERIFIED: their denominator is air-side heat at the WHEEL INLET (t4−t1), i.e. all heat sources, supporting the Q_reg,total denominator; they use T-dependent Δh_vs, repo uses constant 2501 kJ/kg (choice 2) |
| Specific regeneration heat demand | SRH | Q_reg / m_w | kWh/kg | inverse of "specific moisture removal"; cf. Comino et al. 2021 |
| Booster heater duty | Q̇_aux | ṁ_da,reg·[h(T_wheel,in) − h(T_nach_HX)]; est. HX_EFF·Q̇_reg·ΔT_heater/ΔT_coil where flow unmetered | W | electric booster between coil and wheel (thermally inferred; P_el reads 0) |
| Solar fraction | SF | Q_solar / (Q_solar + Q_aux) | – | Duffie & Beckman, Solar Eng. of Thermal Processes, Ch. 20 convention |
| Energy-balance closure | – | Q_reg,air / Q_reg,total (air term = pre-coil state → wheel inlet) | – | internal consistency check; expected 0.9–1.0 |
| HX air-side heat | Q̇_hx,air | ṁ_da,reg · [h(T_nach_HX, x_reg,in) − h(T_reg,in, x_reg,in)] | W | coil-only balance (heater excluded), sensible (x conserved) |
| HX closure | – | Q_hx,air / Q_hx,water  (Q_hx,water = Q_reg) | – | air-to-water coil energy in vs out; expected ≈ 0.8–1.0 |
| Storage discharge | Q̇_store,out | Q̇_reg  (circuit III to the regeneration coil) | W | store energy out |
| Storage charge | Q̇_store,in | ρ_w·V̇_II·c_p,w·(T_II,VL − T_II,RL) | W | store energy in (circuit II); V̇_II units unverified |
| Stored-energy change | ΔU | M·c_p,w·(T̄_end − T̄_start), M = ρ_w·V_tank, T̄ = mean SP layers | kWh | store internal-energy change; V_tank = config.STORAGE_VOLUME_M3 |
| Storage standby loss | – | Q_store,in − Q_store,out − ΔU | kWh | first-law store balance (≥0 expected) |
| Storage closure | – | (Q_store,out + ΔU) / Q_store,in | – | store energy in vs out + accumulation |

## Deliberate choices (and why)

1. **T_reg,eff = `T_reg_TICBT103`** — the WHEEL-INLET temperature, after
   the electric booster heater (updated 2026-07-19; operator-confirmed
   layout: intake → solar coil → electric heater → wheel). Correlation with
   Δx: r = 0.957 vs 0.56 for the pre-heater `T_reg_nach_HX` and 0.44 for the
   pre-coil `T_reg_in`. `T_reg_nach_HX` (TIBT851) is kept as the SOLAR-side
   temperature; their difference is the booster lift (median ≈ 11 K, present
   98 % of runtime in 2026-06/07). `x_reg_in` from the pre-coil sensor *is*
   used — sensible heating conserves humidity ratio.
2. **Latent heat at 0 °C reference (2501 kJ/kg), constant.** Some papers use
   h_fg at the process temperature (~2440 kJ/kg at 30 °C, ≈2.4 % difference).
   Constant-reference is consistent with the enthalpy reference of
   `HAPropsSI` and keeps Q_lat/COP definitions reproducible. Stated here so
   comparisons with papers using the other convention can be corrected.
3. **ε_w is masked when x_p,in ≈ x_r,in** (denominator < 0.5 g/kg): the
   definition degenerates and produces unbounded noise, which clipping would
   disguise as data.
4. **COP is masked when Q̇_reg < 50 W**: without regeneration heat a COP is
   meaningless; including near-zero denominators inflates period means.
5. **Integrals exclude gaps > 6 min** rather than interpolating across them,
   and every integral carries a coverage figure. A season total with 60 %
   coverage is reported as such, not silently extrapolated.
6. **Idempotent rebuild instead of append** (see `pipeline.py` docstring).
7. **Water properties are temperature-dependent** (CoolProp IAPWS-97), not
   constants: between 20 and 60 °C, ρ_w drops ~1.7 % — a systematic error the
   old constant-1000 kg/m³ assumption embedded in every Q_reg value.

## Known accuracy limits (be honest with the supervisor)

- Site pressure is assumed 101 325 Pa; Kassel (~230 m a.s.l.) mean is
  ≈ 98.6 kPa → humidity ratios are systematically ~2.7 % low. Fix: set
  `config.P_ATM` from local barometer or station altitude. (Kept at standard
  pressure for now to stay comparable with the earlier analysis; flagged.)
- Flow-meter location in circuit III (supply vs return line) affects ρ_w by
  ~1 %; return line assumed — verify on the plant.
- Units of the regeneration flow channel (ch 120) are set to L/s, inferred
  from the regeneration-coil energy balance (closure 0.255 with m³/h vs
  ≈ 0.92 with L/s; see comment at `config.V_DOT_REG_UNITS`) — still confirm
  against the sensor datasheet.
- RH-sensor uncertainty (typ. ±2–3 % RH) dominates the uncertainty of Δx and
  hence all moisture KPIs; a formal uncertainty propagation is on the
  roadmap (see README).
