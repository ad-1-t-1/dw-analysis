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
| Moisture removal rate | MRR | ṁ_da,p · (x_p,in − x_p,out) | kg/s | Angrisani et al. 2012, Appl. Energy 92 (their MRC) |
| Water removed (period) | m_w | ∫ MRR dt (trapezoid, gaps excluded) | kg | — |
| Dehumidification effectiveness | η_deh | (x_p,in − x_p,out)/x_p,in | – | De Antonellis et al. 2015, Energy Build.; Comino et al. 2016 |
| Wheel moisture effectiveness | ε_w | (x_p,in − x_p,out)/(x_p,in − x_r,in) | – | Mandegari & Pahlavanzadeh 2009, Energy 34, Eq. (12) |
| Regeneration heat input | Q̇_reg | ρ_w(T)·V̇_III·c_p,w(T)·(T_VL,III − T_RL,III) | W | hydronic heat balance; water props CoolProp IAPWS-97 |
| Regeneration heat (period) | Q_reg | ∫ Q̇_reg dt | kWh | — |
| Latent heat flow | Q̇_lat | MRR · Δh_vap(0 °C) = MRR · 2 501 kJ/kg | W | ASHRAE Fundamentals 2021 Ch. 1 reference state |
| Thermal COP (period) | COP_th | Q_lat / Q_reg | – | thermal analogue of Angrisani et al. 2012 |
| Specific regeneration heat demand | SRH | Q_reg / m_w | kWh/kg | inverse of "specific moisture removal"; cf. Comino et al. 2021 |
| Solar fraction | SF | 1 − Q_aux/Q_reg (boundary: regeneration coil) | – | Duffie & Beckman, Solar Eng. of Thermal Processes, Ch. 20 convention |
| Energy-balance closure | – | Q_reg,air / Q_reg,hydronic | – | internal consistency check |

## Deliberate choices (and why)

1. **T_reg,eff = `T_reg_nach_HX`** (solar Ana8, TIBT851), never the DAQ
   `T_reg_in`, which sits before the heating coil (reads near-ambient;
   correlation with Δx: r≈0.85 vs r≈0.44). `x_reg_in` from the pre-heater
   sensor *is* used — sensible heating conserves humidity ratio.
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
- Units of the regeneration flow channel (ch 120) are assumed m³/h — verify.
- RH-sensor uncertainty (typ. ±2–3 % RH) dominates the uncertainty of Δx and
  hence all moisture KPIs; a formal uncertainty propagation is on the
  roadmap (see README).
