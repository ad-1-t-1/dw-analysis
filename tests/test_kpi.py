"""Hand-calculated expected values for KPI and integration functions."""
import numpy as np
import pandas as pd
import pytest

from dw_analysis import kpi


def _series(values, freq="2min", tz="Europe/Berlin"):
    idx = pd.date_range("2026-06-01 12:00", periods=len(values), freq=freq,
                        tz=tz)
    return pd.Series(values, index=idx)


def test_integrate_constant_rate():
    # 1 W for 1 h (31 samples at 2 min) → 3600 J
    s = _series([1.0] * 31)
    val, cov = kpi.integrate_rate(s)
    assert val == pytest.approx(3600.0, rel=1e-9)
    assert cov == pytest.approx(1.0)


def test_integrate_excludes_gaps():
    # 1 W, but a 30-min hole in the middle → only the two 20-min blocks count
    idx = (list(pd.date_range("2026-06-01 12:00", periods=11, freq="2min"))
           + list(pd.date_range("2026-06-01 12:50", periods=11, freq="2min")))
    s = pd.Series(1.0, index=pd.DatetimeIndex(idx).tz_localize("Europe/Berlin"))
    val, cov = kpi.integrate_rate(s, max_gap="6min")
    assert val == pytest.approx(2 * 20 * 60.0, rel=1e-9)   # 2400 J
    assert cov < 1.0


def test_water_removed_hand_calc():
    # m_dot_da = 0.05 kg/s, Δx = 0.002 kg/kg → MRR = 1e-4 kg/s
    # over 1 h → 0.36 kg water
    df = pd.DataFrame({"MRR_kgs": _series([1e-4] * 31)})
    tot = kpi.period_totals(df)
    assert tot["water_removed_kg"] == pytest.approx(0.36, rel=1e-9)


def test_specific_heat_demand():
    # Q_reg = 1 kW constant, MRR = 1 kg/h constant
    # → 1 kWh heat, 1 kg water → SRH = 1 kWh/kg
    df = pd.DataFrame({
        "MRR_kgs": _series([1.0 / 3600.0] * 31),
        "Q_reg_W": _series([1000.0] * 31),
    })
    tot = kpi.period_totals(df)
    assert tot["water_removed_kg"] == pytest.approx(1.0, rel=1e-9)
    assert tot["Q_reg_kWh"] == pytest.approx(1.0, rel=1e-9)
    assert tot["SRH_kWh_per_kg"] == pytest.approx(1.0, rel=1e-9)


def test_eta_deh_and_epsilon_wheel():
    df = pd.DataFrame({
        "x_proc_in": _series([0.010] * 3),
        "x_proc_out": _series([0.007] * 3),
        "x_reg_in": _series([0.004] * 3),
    })
    df["Delta_x_proc"] = df["x_proc_in"] - df["x_proc_out"]
    out = kpi.instantaneous(df)
    assert out["eta_deh"].iloc[0] == pytest.approx(0.3, rel=1e-6)
    # ε = (10−7)/(10−4) = 0.5
    assert out["epsilon_wheel"].iloc[0] == pytest.approx(0.5, rel=1e-6)


def test_epsilon_wheel_undefined_when_no_potential():
    df = pd.DataFrame({
        "x_proc_in": _series([0.0100] * 3),
        "x_proc_out": _series([0.0099] * 3),
        "x_reg_in": _series([0.0100] * 3),   # no drying potential
    })
    df["Delta_x_proc"] = df["x_proc_in"] - df["x_proc_out"]
    out = kpi.instantaneous(df)
    assert out["epsilon_wheel"].isna().all()


def test_solar_fraction_with_aux():
    df = pd.DataFrame({
        "Q_reg_W": _series([1000.0] * 31),
        "Q_aux_W": _series([250.0] * 31),
    })
    sf = kpi.solar_fraction(df, Q_aux_col="Q_aux_W")
    assert sf["solar_fraction"] == pytest.approx(0.75, rel=1e-9)
