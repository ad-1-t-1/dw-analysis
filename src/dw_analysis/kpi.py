"""
Key performance indicators — instantaneous and period-integrated.

Every KPI states its exact equation and literature source in the docstring.
Definitions vary between papers; the definition used HERE is fixed below and
mirrored in docs/KPI_DEFINITIONS.md.

Integration method: trapezoidal rule over the 2-minute grid. Gaps longer
than config.MAX_INTEGRATION_GAP are EXCLUDED (no interpolation across them);
each integral is reported together with its data coverage so a low-coverage
number is never mistaken for a full-period total.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

EPS = 1e-12


# ─────────────────────────────────────────────────────────────────────────────
# Instantaneous KPIs (added as columns)
# ─────────────────────────────────────────────────────────────────────────────
def instantaneous(df: pd.DataFrame) -> pd.DataFrame:
    """Add per-timestep KPI columns.

    eta_deh        Dehumidification effectiveness
                   η = (x_p,in − x_p,out) / x_p,in           [–]
                   Source: De Antonellis et al. (2015), Energy & Buildings
                   (also used by Comino et al. 2016, Eq. for ε_deh).
    epsilon_wheel  Wheel moisture effectiveness
                   ε = (x_p,in − x_p,out) / (x_p,in − x_r,in) [–]
                   Ideal wheel would dry process air to the regeneration
                   inlet humidity ratio. Source: Mandegari & Pahlavanzadeh
                   (2009), Energy 34, Eq. (12).
    COP_th         Thermal COP = Q̇_latent / Q̇_reg            [–]
                   Q̇_latent = ṁ_da·Δx·Δh_vap(0°C);
                   Q̇_reg = hydronic heat to the regeneration coil
                   (circuit III). Source: Angrisani et al. (2012),
                   Applied Energy 92 — their COP_el analogue, thermal form.
    SHR            Sensible heat ratio of the process stream.
    SMR_g_per_kJ   Specific moisture removal = MRR / Q̇_reg    [g/kJ]
                   (inverse of specific regeneration heat demand).
    """
    df = df.copy()

    if {"Delta_x_proc", "x_proc_in"} <= set(df.columns):
        df["eta_deh"] = df["Delta_x_proc"] / (df["x_proc_in"] + EPS)

    if {"x_proc_in", "x_proc_out", "x_reg_in"} <= set(df.columns):
        denom = df["x_proc_in"] - df["x_reg_in"]
        eps_w = (df["x_proc_in"] - df["x_proc_out"]) / denom
        # undefined when process and regen inlet humidity are nearly equal
        df["epsilon_wheel"] = eps_w.where(denom.abs() > 5e-4)

    if {"Q_latent_W", "Q_reg_W"} <= set(df.columns):
        df["COP_th"] = (df["Q_latent_W"]
                        / df["Q_reg_W"].where(df["Q_reg_W"] > 50.0))
        # Q_reg < 50 W → wheel not being regenerated; COP meaningless

    if {"Q_proc_enthalpy_W", "Q_latent_W"} <= set(df.columns):
        q_sens = df["Q_proc_enthalpy_W"] - (-df["Q_latent_W"])
        tot = df["Q_proc_enthalpy_W"].abs() + EPS
        df["SHR"] = (q_sens.abs() / tot).clip(0, 1)

    if {"MRR_gs", "Q_reg_W"} <= set(df.columns):
        df["SMR_g_per_kJ"] = (df["MRR_gs"]
                              / (df["Q_reg_W"].where(df["Q_reg_W"] > 50.0)
                                 / 1000.0))
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Time integration
# ─────────────────────────────────────────────────────────────────────────────
def integrate_rate(series: pd.Series,
                   max_gap: str | pd.Timedelta = config.MAX_INTEGRATION_GAP
                   ) -> tuple[float, float]:
    """Trapezoidal time integral of a rate series.

    Returns (integral in [unit·s], coverage 0–1).
    Segments where consecutive valid samples are further apart than
    `max_gap` contribute nothing (no interpolation across gaps).
    """
    s = series.dropna()
    if len(s) < 2:
        return 0.0, 0.0
    t = s.index.view("int64") / 1e9          # seconds
    dt = np.diff(t)
    max_gap_s = pd.Timedelta(max_gap).total_seconds()
    ok = dt <= max_gap_s
    integral = float(np.sum(0.5 * (s.values[1:] + s.values[:-1])[ok] * dt[ok]))
    span = (series.index[-1] - series.index[0]).total_seconds()
    coverage = float(np.sum(dt[ok]) / span) if span > 0 else 0.0
    return integral, coverage


def period_totals(df: pd.DataFrame) -> dict:
    """Season/period-integrated KPIs for the given (already sliced) frame.

    water_removed_kg   ∫ ṁ_da·Δx dt                     [kg]
    Q_reg_kWh          ∫ Q̇_reg dt                       [kWh] (hydronic)
    Q_latent_kWh       ∫ Q̇_latent dt                    [kWh]
    SRH_kWh_per_kg     Q_reg_kWh / water_removed_kg      [kWh/kg]
                       (specific regeneration heat demand — lower is better;
                        pure evaporation would need ≈ 0.69 kWh/kg)
    COP_th_integral    Q_latent_kWh / Q_reg_kWh          [–]
    E_el_kWh           ∫ P_el dt (pumps + controls)      [kWh]
    """
    out: dict = {}
    if "MRR_kgs" in df.columns:
        w, cov = integrate_rate(df["MRR_kgs"])
        out["water_removed_kg"] = w
        out["water_removed_coverage"] = cov
    if "Q_reg_W" in df.columns:
        q, cov = integrate_rate(df["Q_reg_W"].clip(lower=0))
        out["Q_reg_kWh"] = q / 3.6e6
        out["Q_reg_coverage"] = cov
        # net integral (negative dT periods NOT discarded) — if this differs
        # much from Q_reg_kWh, the positive-only number is inflated by noise
        q_net, _ = integrate_rate(df["Q_reg_W"])
        out["Q_reg_net_kWh"] = q_net / 3.6e6
    if "Q_latent_W" in df.columns:
        q, _ = integrate_rate(df["Q_latent_W"].clip(lower=0))
        out["Q_latent_kWh"] = q / 3.6e6
    if out.get("water_removed_kg", 0) > 0 and "Q_reg_kWh" in out:
        out["SRH_kWh_per_kg"] = out["Q_reg_kWh"] / out["water_removed_kg"]
    if out.get("Q_reg_kWh", 0) > 0 and "Q_latent_kWh" in out:
        out["COP_th_integral"] = out["Q_latent_kWh"] / out["Q_reg_kWh"]
    if "P_el" in df.columns:
        e, _ = integrate_rate(df["P_el"].clip(lower=0))
        out["E_el_kWh"] = e / 3.6e6
    return out


def solar_fraction(df: pd.DataFrame, Q_aux_col: str | None = None) -> dict:
    """Solar fraction of the regeneration heat.

    Definition (system boundary = regeneration heating coil):
        SF = 1 − Q_aux / Q_reg
    where Q_aux is heat supplied by any non-solar source within the period.

    PLANT STATUS: the regeneration coil is fed exclusively from the solar
    storage via circuit III; no auxiliary heater is metered (P_el covers
    pumps/controls only). Therefore SF = 1 by construction, and the more
    informative quantity is the storage/collector utilisation. Both are
    reported; if an auxiliary source is ever added, pass its power column
    as `Q_aux_col`.
    """
    out: dict = {}
    if "Q_reg_W" not in df.columns:
        return out
    q_reg, _ = integrate_rate(df["Q_reg_W"].clip(lower=0))
    if q_reg <= 0:
        return out
    if Q_aux_col and Q_aux_col in df.columns:
        q_aux, _ = integrate_rate(df[Q_aux_col].clip(lower=0))
        out["solar_fraction"] = 1.0 - q_aux / q_reg
        out["Q_aux_kWh"] = q_aux / 3.6e6
    else:
        out["solar_fraction"] = 1.0
        out["solar_fraction_note"] = ("no auxiliary heat source metered; all "
                                      "regeneration heat traced to solar "
                                      "storage (boundary: regeneration coil)")
    # share of time solar collection was active while the wheel ran
    if {"solar_active", "Betrieb_Entfeuchter"} <= set(df.columns):
        running = df["Betrieb_Entfeuchter"] > 0.5
        if running.any():
            out["solar_collection_share_while_running"] = float(
                df.loc[running, "solar_active"].mean())
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Binned + resampled summaries
# ─────────────────────────────────────────────────────────────────────────────
def kpis_by_temp_bin(df: pd.DataFrame,
                     bins: list[float] = config.T_REG_BINS) -> pd.DataFrame:
    """Period KPIs binned by effective regeneration temperature.

    Answers: 'how much water do we remove per kWh of heat at 45–50 °C vs
    55–60 °C?' — the core low-temperature-regeneration question.
    """
    if "T_reg_eff" not in df.columns:
        return pd.DataFrame()
    running = df
    if "Betrieb_Entfeuchter" in df.columns:
        running = df[df["Betrieb_Entfeuchter"] > 0.5]
    cats = pd.cut(running["T_reg_eff"], bins=bins)
    rows = []
    for interval, grp in running.groupby(cats, observed=True):
        if len(grp) < 5:
            continue
        row = {"T_reg_bin": str(interval), "hours": len(grp) *
               pd.Timedelta(config.RESAMPLE_RULE).total_seconds() / 3600.0,
               "Delta_x_mean_gkg": grp.get("Delta_x_proc_gkg",
                                           pd.Series(dtype=float)).mean(),
               "eta_deh_mean": grp.get("eta_deh",
                                       pd.Series(dtype=float)).mean()}
        row.update(period_totals(grp))
        rows.append(row)
    return pd.DataFrame(rows)


def resampled_summary(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """Daily/weekly table: integrated totals + mean operating conditions."""
    rows = []
    for ts, grp in df.groupby(pd.Grouper(freq=freq)):
        if grp.empty:
            continue
        row = {"period": ts}
        row.update(period_totals(grp))
        row.update(solar_fraction(grp))
        for col in ["T_proc_in", "Phi_proc_in", "T_reg_eff",
                    "Delta_x_proc_gkg", "T_AU", "T_SP_oben"]:
            if col in grp.columns:
                row[f"{col}_mean"] = grp[col].mean()
        if "Betrieb_Entfeuchter" in grp.columns:
            row["runtime_h"] = float((grp["Betrieb_Entfeuchter"] > 0.5).sum()
                    * pd.Timedelta(config.RESAMPLE_RULE).total_seconds()
                    / 3600.0)
        rows.append(row)
    return pd.DataFrame(rows).set_index("period") if rows else pd.DataFrame()


# ─────────────────────────────────────────────────────────────────────────────
# Energy-balance closure
# ─────────────────────────────────────────────────────────────────────────────
def energy_balance(df: pd.DataFrame) -> dict:
    """Compare hydronic heat input with regeneration-air enthalpy gain.

    Closure = Q_reg_air / Q_reg_hydronic  (expected < 1: HX and duct losses;
    values ≫ 1 or ≪ 0.5 indicate a sensor, unit, or flow-assumption error).
    Requires the regeneration air flow (ch 120) — reported as
    'not computable' until that channel is available/converted.
    """
    out: dict = {}
    if "Q_reg_W" in df.columns:
        q_hyd, _ = integrate_rate(df["Q_reg_W"].clip(lower=0))
        out["Q_reg_hydronic_kWh"] = q_hyd / 3.6e6
    if "Q_reg_air_W" in df.columns:
        # closure is only meaningful over the window where BOTH sides are
        # measured (air-side flow may cover a fraction of the season)
        both = df["Q_reg_W"].notna() & df["Q_reg_air_W"].notna()
        if both.any():
            q_air, _ = integrate_rate(df.loc[both, "Q_reg_air_W"].clip(lower=0))
            q_hyd_w, _ = integrate_rate(df.loc[both, "Q_reg_W"].clip(lower=0))
            out["Q_reg_air_kWh_window"] = q_air / 3.6e6
            out["Q_reg_hydronic_kWh_window"] = q_hyd_w / 3.6e6
            out["closure_window_hours"] = round(
                both.sum() * pd.Timedelta(config.RESAMPLE_RULE
                                          ).total_seconds() / 3600.0, 1)
            if q_hyd_w > 0:
                out["closure"] = q_air / q_hyd_w
    else:
        out["closure_note"] = ("regeneration air flow (ch 120) unavailable — "
                               "air-side balance not computable")
    # moisture balance: water picked up by regen air vs removed from process
    if {"m_dot_da_reg", "Delta_x_reg"} <= set(df.columns) and \
            "MRR_kgs" in df.columns:
        w_reg, _ = integrate_rate((df["m_dot_da_reg"]
                                   * df["Delta_x_reg"]).clip(lower=0))
        w_proc, _ = integrate_rate(df["MRR_kgs"].clip(lower=0))
        if w_proc > 0:
            out["moisture_closure"] = w_reg / w_proc
    return out
