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


def test_integrate_resolution_independent():
    # pandas 3.0 defaults new datetimes to microsecond resolution; the
    # integral must not change with the index unit (CI regression 2026-07-10:
    # ns-assuming code gave values exactly 1000× too small under µs indexes)
    s = _series([1.0] * 31)
    s_us = pd.Series(s.values, index=s.index.as_unit("us"))
    val, _ = kpi.integrate_rate(s_us)
    assert val == pytest.approx(3600.0, rel=1e-9)


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
    # Q_reg_W is the SOLAR (hydronic) heat, Q_aux the electric booster:
    # SF = Q_solar / (Q_solar + Q_aux) = 1000 / 1250
    assert sf["solar_fraction"] == pytest.approx(0.8, rel=1e-9)
    assert sf["Q_aux_kWh"] == pytest.approx(0.25 * 1000 / 1000, rel=1e-6)


# ── air-to-water HX balance ──────────────────────────────────────────────
def test_hx_energy_balance_closure():
    # water side 1000 W, air side 900 W, both measured for 1 h
    df = pd.DataFrame({
        "Q_reg_W": _series([1000.0] * 31),
        "Q_hx_air_W": _series([900.0] * 31),
    })
    hb = kpi.hx_energy_balance(df)
    assert hb["Q_hx_water_kWh"] == pytest.approx(1.0, rel=1e-9)
    assert hb["Q_hx_air_kWh_window"] == pytest.approx(0.9, rel=1e-9)
    assert hb["hx_closure"] == pytest.approx(0.9, rel=1e-9)


def test_hx_closure_only_over_common_window():
    # air side measured for only the first 11 of 31 samples (20 min);
    # water side runs the full hour. Closure must use the common window,
    # so water_window ≈ 20 min · 1000 W, not the full hour.
    air = [900.0] * 11 + [np.nan] * 20
    df = pd.DataFrame({
        "Q_reg_W": _series([1000.0] * 31),
        "Q_hx_air_W": _series(air),
    })
    hb = kpi.hx_energy_balance(df)
    assert hb["Q_hx_water_kWh"] == pytest.approx(1.0, rel=1e-9)          # full
    # 11 overlapping samples on the 2-min grid → ~0.37 h (rounds to 0.4);
    # the point is it is well below the full hour.
    assert hb["hx_window_hours"] < 0.5
    assert hb["hx_closure"] == pytest.approx(0.9, rel=1e-9)


def test_hx_note_when_no_air_side():
    df = pd.DataFrame({"Q_reg_W": _series([1000.0] * 31)})
    hb = kpi.hx_energy_balance(df)
    assert "hx_closure" not in hb
    assert "hx_note" in hb


# ── thermal-storage balance ──────────────────────────────────────────────
def test_storage_discharge_and_dU_per_m3():
    # discharge 1000 W for 1 h → 1 kWh out; store warms 50→54 °C → ΔU>0
    df = pd.DataFrame({
        "Q_store_out_W": _series([1000.0] * 31),
        "T_store_mean": _series(list(np.linspace(50.0, 54.0, 31))),
    })
    sb = kpi.storage_energy_balance(df)
    assert sb["Q_store_out_kWh"] == pytest.approx(1.0, rel=1e-9)
    assert sb["T_store_start_C"] == pytest.approx(50.0, abs=1e-6)
    assert sb["T_store_end_C"] == pytest.approx(54.0, abs=1e-6)
    assert sb["dU_store_kWh_per_m3"] > 0            # warming → energy stored
    assert "dU_store_kWh" not in sb                 # no volume set → per-m³ only


def test_storage_absolute_dU_with_volume(monkeypatch):
    from dw_analysis import config as cfg
    monkeypatch.setattr(cfg, "STORAGE_VOLUME_M3", 2.0)
    df = pd.DataFrame({
        "T_store_mean": _series(list(np.linspace(50.0, 54.0, 31))),
    })
    sb = kpi.storage_energy_balance(df)
    assert sb["dU_store_kWh"] == pytest.approx(
        sb["dU_store_kWh_per_m3"] * 2.0, rel=1e-9)


def test_storage_charge_note_when_no_flow():
    df = pd.DataFrame({"Q_store_out_W": _series([500.0] * 31)})
    sb = kpi.storage_energy_balance(df)
    assert "Q_store_in_kWh" not in sb
    assert "Q_store_in_note" in sb
