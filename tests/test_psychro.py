"""Validate CoolProp HAPropsSI against ASHRAE Fundamentals (2021, Ch. 1)
psychrometric table values. Table values are defined at standard pressure
(101.325 kPa), so it is passed explicitly — config.P_ATM is the Kassel site
pressure and intentionally differs."""
import numpy as np
import pytest

from dw_analysis import psychro

P_STD = 101_325.0


def test_saturation_humidity_ratio_20C():
    # ASHRAE Fundamentals 2021, Table 2: Ws(20 °C) = 0.014758 kg/kg
    W = psychro.humidity_ratio(20.0, 100.0, p_atm=P_STD)
    assert W == pytest.approx(0.014758, rel=0.005)


def test_saturation_humidity_ratio_25C():
    # ASHRAE Fundamentals 2021, Table 2: Ws(25 °C) = 0.020170 kg/kg
    W = psychro.humidity_ratio(25.0, 100.0, p_atm=P_STD)
    assert W == pytest.approx(0.020170, rel=0.005)


def test_state_25C_50RH():
    # Classic check state 25 °C / 50 % RH:
    # W ≈ 0.00992 kg/kg, h ≈ 50.4 kJ/kg_da, Tdp ≈ 13.9 °C, Twb ≈ 17.9 °C
    assert psychro.humidity_ratio(25.0, 50.0, p_atm=P_STD) == pytest.approx(0.00992, rel=0.01)
    assert psychro.enthalpy(25.0, 50.0, p_atm=P_STD) / 1000 == pytest.approx(50.4, rel=0.01)
    assert psychro.dew_point(25.0, 50.0, p_atm=P_STD) == pytest.approx(13.9, abs=0.15)
    assert psychro.wet_bulb(25.0, 50.0, p_atm=P_STD) == pytest.approx(17.9, abs=0.15)


def test_specific_volume_dry_air_20C():
    # v_da at 20 °C, 0 % RH ≈ R_a·T/p = 287.042·293.15/101325 = 0.8304 m³/kg
    v = psychro.specific_volume_da(20.0, 0.0, p_atm=P_STD)
    assert v == pytest.approx(0.8304, rel=0.005)


def test_site_pressure_raises_humidity_ratio():
    # lower pressure → same RH holds MORE water per kg dry air (~2.7 % here);
    # guards against silently reverting P_ATM to standard pressure
    from dw_analysis.config import P_ATM
    assert P_ATM < P_STD
    w_site = psychro.humidity_ratio(25.0, 50.0)          # uses config.P_ATM
    w_std = psychro.humidity_ratio(25.0, 50.0, p_atm=P_STD)
    assert w_site > w_std * 1.015


def test_vectorized_and_nan_safe():
    T = np.array([20.0, np.nan, 25.0])
    RH = np.array([50.0, 50.0, np.nan])
    W = psychro.humidity_ratio(T, RH)
    assert np.isfinite(W[0]) and np.isnan(W[1]) and np.isnan(W[2])


def test_rh_above_100_clipped_not_crash():
    W = psychro.humidity_ratio(20.0, 101.5)   # sensor overshoot
    assert W == pytest.approx(psychro.humidity_ratio(20.0, 100.0), rel=1e-6)


def test_water_properties():
    # IAPWS: rho(40 °C) ≈ 992.2 kg/m³, cp(40 °C) ≈ 4179 J/(kg K)
    assert psychro.water_rho(np.array([40.0]))[0] == pytest.approx(992.2, rel=0.005)
    assert psychro.water_cp(np.array([40.0]))[0] == pytest.approx(4179.0, rel=0.005)
