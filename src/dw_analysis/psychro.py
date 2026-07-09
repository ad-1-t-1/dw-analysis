"""
Psychrometric properties via CoolProp HAPropsSI — no hand-rolled correlations.

CoolProp implements the ASHRAE RP-1485 real-gas moist-air model
(Herrmann, Kretzschmar & Gatley, 2009, HVAC&R Research 15(5)), which is the
basis of the ASHRAE Fundamentals psychrometric tables. Validated against
ASHRAE table values in tests/test_psychro.py.

HAPropsSI keys used (all SI: K, Pa, J/kg_dry_air, kg/kg_dry_air):
    inputs : 'T' [K], 'P' [Pa], 'R' relative humidity [0–1]
    outputs: 'W'   humidity ratio [kg_w/kg_da]
             'H'   mixture enthalpy per kg dry air [J/kg_da]
             'D'   dew-point temperature [K]
             'B'   wet-bulb temperature [K]
             'Vda' mixture volume per kg dry air [m³/kg_da]

All public functions accept °C and RH in %, return SI values (documented per
function). Vectorised over numpy arrays; invalid inputs yield NaN.

Performance: HAPropsSI is scalar. We evaluate only the unique (T, RH) pairs
after rounding T to 0.01 K and RH to 0.1 % (below sensor resolution of the
plant's hygrometers), then broadcast back — lossless in practice and ~100×
faster on 2-minute season data.
"""
from __future__ import annotations

import numpy as np
from CoolProp.HumidAirProp import HAPropsSI

from .config import P_ATM

_T_DECIMALS = 2   # round T [°C] to 0.01 K
_RH_DECIMALS = 1  # round RH [%] to 0.1 %


def _ha_vectorized(output: str, T_C, RH_pct, p_atm: float = P_ATM) -> np.ndarray:
    """Evaluate HAPropsSI(output) over arrays of T [°C] and RH [%].

    NaN-safe: any point where CoolProp fails (out-of-range input, NaN)
    returns NaN instead of raising.
    """
    T = np.asarray(T_C, dtype=float)
    RH = np.asarray(RH_pct, dtype=float)
    T, RH = np.broadcast_arrays(T, RH)
    shape = T.shape
    T = np.round(T.ravel(), _T_DECIMALS)
    # clip physically impossible RH (sensor noise) — >100 % clipped to 100
    RH = np.clip(np.round(RH.ravel(), _RH_DECIMALS), 0.0, 100.0)

    out = np.full(T.size, np.nan)
    valid = np.isfinite(T) & np.isfinite(RH)
    if valid.any():
        pairs = np.column_stack([T[valid], RH[valid]])
        uniq, inverse = np.unique(pairs, axis=0, return_inverse=True)
        vals = np.empty(len(uniq))
        for i, (t, rh) in enumerate(uniq):
            try:
                vals[i] = HAPropsSI(output, "T", t + 273.15, "P", p_atm,
                                    "R", rh / 100.0)
            except ValueError:
                vals[i] = np.nan
        out[valid] = vals[inverse]
    return out.reshape(shape)


def humidity_ratio(T_C, RH_pct, p_atm: float = P_ATM) -> np.ndarray:
    """Humidity ratio x [kg_water / kg_dry_air]."""
    return _ha_vectorized("W", T_C, RH_pct, p_atm)


def enthalpy(T_C, RH_pct, p_atm: float = P_ATM) -> np.ndarray:
    """Specific enthalpy of moist air [J / kg_dry_air], h=0 for dry air at 0 °C."""
    return _ha_vectorized("H", T_C, RH_pct, p_atm)


def dew_point(T_C, RH_pct, p_atm: float = P_ATM) -> np.ndarray:
    """Dew-point temperature [°C]."""
    return _ha_vectorized("D", T_C, RH_pct, p_atm) - 273.15


def wet_bulb(T_C, RH_pct, p_atm: float = P_ATM) -> np.ndarray:
    """Thermodynamic wet-bulb temperature [°C]."""
    return _ha_vectorized("B", T_C, RH_pct, p_atm) - 273.15


def specific_volume_da(T_C, RH_pct, p_atm: float = P_ATM) -> np.ndarray:
    """Mixture volume per kg DRY air v_da [m³/kg_da].

    Dry-air mass flow from a volumetric flow:  m_dot_da = V_dot / v_da.
    Using dry-air (not moist-air) mass flow is the correct basis for
    moisture balances, because the dry-air mass is conserved across the
    wheel while the moist-air mass is not.
    """
    return _ha_vectorized("Vda", T_C, RH_pct, p_atm)


def absolute_humidity(T_C, RH_pct, p_atm: float = P_ATM) -> np.ndarray:
    """Water-vapour density (absolute humidity) [kg/m³] = x / v_da."""
    return (_ha_vectorized("W", T_C, RH_pct, p_atm)
            / _ha_vectorized("Vda", T_C, RH_pct, p_atm))


# ── Liquid-water properties for the hydronic circuits ────────────────────────
from CoolProp.CoolProp import PropsSI

_P_WATER = 2.0e5  # Pa — circuit pressure assumption; cp/rho vary <0.1 %/bar


def water_cp(T_C) -> np.ndarray:
    """cp of liquid water [J/(kg·K)] at circuit temperature (CoolProp IAPWS-97)."""
    T = np.asarray(T_C, dtype=float)
    out = np.full(T.shape, np.nan)
    Tr = np.round(T, 1)
    uniq = np.unique(Tr[np.isfinite(Tr)])
    lut = {}
    for t in uniq:
        try:
            lut[t] = PropsSI("C", "T", t + 273.15, "P", _P_WATER, "Water")
        except ValueError:
            lut[t] = np.nan
    flat = out.ravel()
    trf = Tr.ravel()
    for i in range(flat.size):
        flat[i] = lut.get(trf[i], np.nan)
    return flat.reshape(T.shape)


def water_rho(T_C) -> np.ndarray:
    """Density of liquid water [kg/m³] at circuit temperature."""
    T = np.asarray(T_C, dtype=float)
    Tr = np.round(T, 1)
    uniq = np.unique(Tr[np.isfinite(Tr)])
    lut = {}
    for t in uniq:
        try:
            lut[t] = PropsSI("D", "T", t + 273.15, "P", _P_WATER, "Water")
        except ValueError:
            lut[t] = np.nan
    flat = np.full(T.size, np.nan)
    trf = Tr.ravel()
    for i in range(flat.size):
        flat[i] = lut.get(trf[i], np.nan)
    return flat.reshape(T.shape)
