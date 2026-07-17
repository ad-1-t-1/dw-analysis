"""
Psychrometric and energy enrichment of the merged dataset.

Adds, for each air stream (proc_in, proc_out, reg_in, reg_out):
    x_*        humidity ratio [kg/kg_da]         (CoolProp HAPropsSI 'W')
    h_*        specific enthalpy [J/kg_da]       ('H')
    T_dp_*     dew point [°C]                    ('D')
    v_da_*     mixture volume per kg dry air     ('Vda')

Cross-wheel differences, hydronic heat flow (circuit III = regeneration
heat), air mass flows and flow-dependent heat flows.

Flow-source bookkeeping: every run records whether air flows were measured
or assumed; downstream KPI tables carry this flag.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config, psychro

STREAMS = {
    "proc_in":  ("T_proc_in",  "Phi_proc_in"),
    "proc_out": ("T_proc_out", "Phi_proc_out"),
    "reg_in":   ("T_reg_in",   "Phi_reg_in"),   # pre-heater: T low, x valid
    "reg_out":  ("T_reg_out",  "Phi_reg_out"),
}


def enrich(df: pd.DataFrame, p_atm: float = config.P_ATM) -> tuple[pd.DataFrame, dict]:
    """Add derived columns. Returns (df, meta) where meta records flow sources.

    Note on the regeneration inlet state: T_reg_in/Phi_reg_in are measured
    BEFORE the heating coil. The humidity ratio x_reg_in is still the wheel
    inlet value (sensible heating conserves x), but the wheel-inlet
    TEMPERATURE is T_reg_nach_HX → stored as T_reg_eff.
    """
    df = df.copy()
    meta = {"flow_source_proc": None, "flow_source_reg": None}

    # ── psychrometrics per stream ────────────────────────────────────────
    for tag, (Tc, RHc) in STREAMS.items():
        if Tc not in df.columns or RHc not in df.columns:
            continue
        T, RH = df[Tc].values, df[RHc].values
        df[f"x_{tag}"] = psychro.humidity_ratio(T, RH, p_atm)
        df[f"x_{tag}_gkg"] = df[f"x_{tag}"] * 1000.0
        df[f"h_{tag}"] = psychro.enthalpy(T, RH, p_atm)
        df[f"T_dp_{tag}"] = psychro.dew_point(T, RH, p_atm)
        df[f"v_da_{tag}"] = psychro.specific_volume_da(T, RH, p_atm)

    # ── effective regeneration temperature (see config) ─────────────────
    src = config.T_REG_EFFECTIVE_SOURCE
    if src in df.columns:
        df["T_reg_eff"] = df[src]
    elif "T_reg_in" in df.columns:
        df["T_reg_eff"] = df["T_reg_in"]
        import warnings
        warnings.warn(f"{src} missing — falling back to PRE-heater T_reg_in; "
                      "regeneration-temperature KPIs will be wrong.")

    # ── cross-wheel differences ──────────────────────────────────────────
    if {"x_proc_in", "x_proc_out"} <= set(df.columns):
        df["Delta_x_proc"] = df["x_proc_in"] - df["x_proc_out"]
        df["Delta_x_proc_gkg"] = df["Delta_x_proc"] * 1000.0
    if {"x_reg_in", "x_reg_out"} <= set(df.columns):
        df["Delta_x_reg"] = df["x_reg_out"] - df["x_reg_in"]
    if {"h_proc_in", "h_proc_out"} <= set(df.columns):
        df["Delta_h_proc"] = df["h_proc_in"] - df["h_proc_out"]
    if {"T_reg_eff", "T_proc_in"} <= set(df.columns):
        df["dT_lift"] = df["T_reg_eff"] - df["T_proc_in"]
    if {"T_proc_out", "T_proc_in"} <= set(df.columns):
        df["dT_proc"] = df["T_proc_out"] - df["T_proc_in"]

    # ── regeneration heat: hydronic circuit III ─────────────────────────
    # Q̇_reg,w = ρ_w(T)·V̇·c_p,w(T)·(T_VL − T_RL)
    # Water properties from CoolProp (IAPWS-97) at the return-line
    # temperature (flow meter assumed in the return line — VERIFY).
    if {"T_VL_III", "T_RL_III"} <= set(df.columns):
        dT = df["T_VL_III"] - df["T_RL_III"]
        df["dT_water_III"] = dT
        if "V_dot_III" in df.columns:
            T_meter = df["T_RL_III"].values
            rho = psychro.water_rho(T_meter)
            cp = psychro.water_cp(np.nanmean(
                np.vstack([df["T_VL_III"].values, df["T_RL_III"].values]),
                axis=0))
            m_dot = df["V_dot_III"].clip(lower=0).values / 1000.0 * rho  # kg/s
            df["m_dot_water_III"] = m_dot
            df["Q_reg_W"] = m_dot * cp * dT.values          # [W]

    # ── air flows ────────────────────────────────────────────────────────
    # Process side: velocity sensor ch 117 × duct area (config) at outlet
    # state → dry-air mass flow m_dot_da = V̇ / v_da(outlet).
    if ("u_proc_out" in df.columns and config.PROC_DUCT_AREA_M2
            and "v_da_proc_out" in df.columns):
        V = df["u_proc_out"].clip(lower=0) * config.PROC_DUCT_AREA_M2
        df["m_dot_da_proc"] = V / df["v_da_proc_out"]
        meta["flow_source_proc"] = "measured"
    elif config.V_DOT_PROC_ASSUMED and "v_da_proc_in" in df.columns:
        df["m_dot_da_proc"] = config.V_DOT_PROC_ASSUMED / df["v_da_proc_in"]
        meta["flow_source_proc"] = "assumed"

    # Regeneration side: volumetric flow ch 120.
    if "V_dot_reg" in df.columns and "v_da_reg_in" in df.columns:
        factor = {"m3/h": 1 / 3600.0, "m3/s": 1.0, "L/s": 1e-3}[
            config.V_DOT_REG_UNITS]
        df["m_dot_da_reg"] = (df["V_dot_reg"].clip(lower=0) * factor
                              / df["v_da_reg_in"])
        meta["flow_source_reg"] = f"measured ({config.V_DOT_REG_UNITS} assumed)"
    elif config.V_DOT_REG_ASSUMED and "v_da_reg_in" in df.columns:
        df["m_dot_da_reg"] = config.V_DOT_REG_ASSUMED / df["v_da_reg_in"]
        meta["flow_source_reg"] = "assumed"

    # ── flow-dependent heat/moisture rates ───────────────────────────────
    if "m_dot_da_proc" in df.columns:
        if "Delta_x_proc" in df.columns:
            # moisture removal rate [kg/s] on dry-air basis
            df["MRR_kgs"] = df["m_dot_da_proc"] * df["Delta_x_proc"]
            df["MRR_gs"] = df["MRR_kgs"] * 1000.0
            # latent heat flow associated with removed moisture [W]
            df["Q_latent_W"] = df["MRR_kgs"] * config.DELTA_H_VAP_0C
        if "Delta_h_proc" in df.columns:
            df["Q_proc_enthalpy_W"] = df["m_dot_da_proc"] * df["Delta_h_proc"]

    # regeneration air enthalpy gain — used for energy-balance closure
    if ("m_dot_da_reg" in df.columns
            and {"h_reg_out", "x_reg_in", "Phi_reg_in"} <= set(df.columns)
            and "T_reg_eff" in df.columns):
        # wheel-inlet enthalpy at (T_reg_eff, x_reg_in): recompute h from
        # T_reg_eff and the pre-heater humidity ratio.  h ≈ f(T, x); we get
        # it via HAPropsSI with 'W' input.
        from CoolProp.HumidAirProp import HAPropsSI
        T = np.round(df["T_reg_eff"].values, 2)
        W = np.round(df["x_reg_in"].values, 6)
        h = np.full(len(df), np.nan)
        valid = np.isfinite(T) & np.isfinite(W)
        pairs = np.column_stack([T[valid], W[valid]])
        if len(pairs):
            uniq, inv = np.unique(pairs, axis=0, return_inverse=True)
            vals = np.empty(len(uniq))
            for i, (t, w) in enumerate(uniq):
                try:
                    vals[i] = HAPropsSI("H", "T", t + 273.15, "P", p_atm,
                                        "W", max(w, 0.0))
                except ValueError:
                    vals[i] = np.nan
            h[valid] = vals[inv]
        df["h_reg_wheel_in"] = h
        df["Q_reg_air_W"] = df["m_dot_da_reg"] * (df["h_reg_wheel_in"]
                                                  - df["h_reg_out"]) * -1.0
        # sign: positive = enthalpy picked up by regen air across heater+wheel

    # ── solar flags ──────────────────────────────────────────────────────
    if {"Pumpe_I", "T_Kollektor", "T_SP_oben"} <= set(df.columns):
        df["solar_active"] = ((df["Pumpe_I"] > 0.5)
                              & (df["T_Kollektor"] > df["T_SP_oben"] + 2.0)
                              ).astype(float)
    if {"T_I_VL", "T_I_RL"} <= set(df.columns):
        df["dT_solar_I"] = df["T_I_VL"] - df["T_I_RL"]

    # ── air-to-water HX (regeneration heating coil): air-side gain ───────
    # The coil heats the regeneration air from T_reg_in (pre-heater state)
    # to T_reg_eff (= T_reg_nach_HX) at CONSTANT humidity ratio (sensible
    # heating, no condensation), so the air-side heat picked up in the coil
    # is  Q̇_hx,air = ṁ_da,reg · [h(T_reg_eff, x_reg_in) − h(T_reg_in, x_reg_in)].
    #   h_reg_wheel_in = h(T_reg_eff, x_reg_in)  (built above)
    #   h_reg_in       = h(T_reg_in,  Φ_reg_in)  (built in the STREAMS loop;
    #                    same humidity ratio x_reg_in)
    # Water side of the same HX is Q_reg_W (circuit III). kpi.hx_energy_balance
    # compares the two.
    if {"m_dot_da_reg", "h_reg_wheel_in", "h_reg_in"} <= set(df.columns):
        df["Q_hx_air_W"] = df["m_dot_da_reg"] * (df["h_reg_wheel_in"]
                                                 - df["h_reg_in"])

    # ── thermal storage: charge / discharge / bulk temperature ──────────
    # Discharge to the regeneration coil is circuit III → equals Q_reg_W.
    if "Q_reg_W" in df.columns:
        df["Q_store_out_W"] = df["Q_reg_W"]

    # Charge from the collector side is circuit II:
    #   Q̇_charge = ρ_w(T_RL_II)·V̇_II·c_p,w·(T_II_VL − T_II_RL).
    # V̇_II units and coverage are UNVERIFIED (config.V_DOT_II_UNITS).
    if {"T_II_VL", "T_II_RL", "V_dot_II"} <= set(df.columns):
        dT_II = df["T_II_VL"] - df["T_II_RL"]
        rho_II = psychro.water_rho(df["T_II_RL"].values)
        cp_II = psychro.water_cp(np.nanmean(
            np.vstack([df["T_II_VL"].values, df["T_II_RL"].values]), axis=0))
        factor = {"L/h": 1 / 3.6e6, "L/s": 1e-3,
                  "m3/h": 1 / 3600.0, "m3/s": 1.0}[config.V_DOT_II_UNITS]
        m_dot_II = df["V_dot_II"].clip(lower=0).values * factor * rho_II
        df["m_dot_water_II"] = m_dot_II
        df["Q_store_in_W"] = m_dot_II * cp_II * dT_II.values

    # Bulk store temperature = mean of the stratification layers present.
    sp_cols = [c for c in config.STORAGE_LAYER_COLS if c in df.columns]
    if sp_cols:
        df["T_store_mean"] = df[sp_cols].mean(axis=1)

    return df, meta
