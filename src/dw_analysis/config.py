"""
Central configuration for the Kassel solar-assisted desiccant wheel pilot plant.

Everything plant-specific lives here: column maps, sensor quirks, unit
assumptions. Analysis code imports from this module only — if sensor naming
or wiring changes, this is the single file to update.
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# General
# ─────────────────────────────────────────────────────────────────────────────
TZ = "Europe/Berlin"          # plant location; DST handled at tz-localize
P_ATM = 98_600.0              # Pa — mean site pressure, Kassel ≈ 230 m a.s.l.
                              # (barometric formula: 101325·(1−2.25577e-5·230)^5.2559)
                              # Was 101 325 until 2026-07-12; that biased all
                              # humidity ratios ~2.7 % low. Replace with the
                              # measured station value when available.
RESAMPLE_RULE = "2min"        # common time grid for merged dataset
MAX_INTEGRATION_GAP = "6min"  # gaps longer than this are excluded from
                              # time integrals instead of being interpolated

# Reference latent heat of vaporisation at 0 °C [J/kg]
# (ASHRAE Fundamentals 2021, Ch. 1, Eq. 30 basis)
DELTA_H_VAP_0C = 2_501_000.0

# ─────────────────────────────────────────────────────────────────────────────
# Plant geometry / flow assumptions  — VERIFY BEFORE TRUSTING FLOW-BASED KPIs
# ─────────────────────────────────────────────────────────────────────────────
# Duct cross-section at the process-air velocity sensor (ch 117).
# None → process air mass flow cannot be computed from u_proc_out and any
# flow-dependent KPI is marked "assumed-flow" (or NaN if no fallback given).
PROC_DUCT_AREA_M2: float | None = None

# Fallback volumetric flows [m³/s] used ONLY when measurement is unavailable.
# KPIs computed with these are flagged flow_source="assumed" in all outputs.
V_DOT_PROC_ASSUMED: float | None = None
V_DOT_REG_ASSUMED: float | None = None

# Units of the regeneration air volume-flow channel (ch 120).
# UNVERIFIED — confirm against sensor datasheet. Options: "m3/h", "m3/s", "L/s"
V_DOT_REG_UNITS = "m3/h"

# ─────────────────────────────────────────────────────────────────────────────
# Thermal storage (Speicher) — for the storage energy balance
# ─────────────────────────────────────────────────────────────────────────────
# Water volume of the stratified store [m³]. None → the stored-energy-change
# term (ΔU) of the storage balance is reported PER m³ only (the temperature
# signal is still usable); set the datasheet value to get absolute ΔU, standby
# losses and the charge/discharge closure.
STORAGE_VOLUME_M3: float | None = None

# Storage temperature layers, top → bottom. Their mean is the bulk store
# temperature T̄ used for ΔU = M·c_p,w·ΔT̄.
STORAGE_LAYER_COLS = ["T_SP_oben", "T_SP_mitte_ob",
                      "T_SP_mitte_unten", "T_SP_unten"]

# Solar charging circuit feeding the store (circuit II, collector side):
# Q̇_charge = ρ_w·V̇_II·c_p,w·(T_II_VL − T_II_RL).
# Units of its volume-flow channel (ch 122) — UNVERIFIED, confirm vs
# datasheet. Options: "L/h", "L/s", "m3/h", "m3/s". (ch 122 is also sparsely
# populated, so the charge side is often "not computable" until wired up.)
V_DOT_II_UNITS = "L/h"

# ─────────────────────────────────────────────────────────────────────────────
# DAQ973A trace-number dependent sensor conversions
# ─────────────────────────────────────────────────────────────────────────────
# Channels 117/118/120/122 were added as raw voltage (Vdc) channels.
# For trace files with number  < TRACE_CONVERSION_CUTOFF the logger stored raw
# volts and the conversion MUST be applied in software.
# From trace TRACE_CONVERSION_CUTOFF onwards the logger applies the conversion
# itself and applying it again would corrupt the data.
TRACE_CONVERSION_CUTOFF = 24

# Linear conversions  physical = scale * signal + offset, applied to the RAW
# column names as they appear in pre-cutoff Trace files.
# Source: merge.py (original merge script), verified against Trace 21 header.
# NOTE: ch 120/122 have DIFFERENT ranges in the logger from trace 24 onwards
# (120: 125*U − 50; 122: 62500*I − 250) — the logger applies those itself, so
# they never appear in this software-side table.
VOLTAGE_CONVERSIONS: dict[str, dict] = {
    # raw col      alias            physical = scale*signal + offset
    "117 (Vdc)": {"name": "u_proc_out", "scale": 1.0, "offset": 0.0,
                  "units": "m/s"},   # 0–10 V == 0–10 m/s (identity)
    "118 (Vdc)": {"name": "T_proc_out_Vol", "scale": 9.0, "offset": -20.0,
                  "units": "degC"},  # temperature inside velocity sensor
    "120 (Vdc)": {"name": "V_dot_reg", "scale": 500.0, "offset": -200.0,
                  "units": V_DOT_REG_UNITS},  # OLD range (pre-trace-24)
    "122 (Adc)": {"name": "V_dot_II", "scale": 187500.0, "offset": -750.0,
                  "units": "L/h?"},  # OLD range; units unverified
}

# ─────────────────────────────────────────────────────────────────────────────
# Sensor artefacts / plausibility limits
# ─────────────────────────────────────────────────────────────────────────────
# Disconnected thermocouple on the desiccant DAQ reads ≈ −40 °C
# (0 V × gain − offset). Rows with T_reg_in below this are artefacts.
T_ARTEFACT_THRESHOLD = -30.0

PLAUSIBILITY = {
    # column-name prefix → (min, max) physical limits; outside → NaN + logged
    "T_":   (-45.0, 130.0),   # °C
    "Phi_": (0.0, 102.0),     # % (2 % sensor overshoot tolerance)
    "V_dot": (0.0, None),     # flows non-negative
    "u_":   (0.0, 30.0),      # m/s
}

# ─────────────────────────────────────────────────────────────────────────────
# Regeneration temperature — sensor placement (verified 2026-07-06)
# ─────────────────────────────────────────────────────────────────────────────
# desiccant_T_reg_in sits BEFORE the regeneration heating coil (water-air HX)
# and reads near-ambient. The physically meaningful regeneration inlet
# temperature is solar_Ana8 "T_reg_nach_HX" (after the HX; TIBT851).
# Δx_proc correlates r≈0.85 with T_reg_nach_HX vs r≈0.44 with T_reg_in.
# x_reg_in measured pre-heater remains valid: sensible heating does not
# change the humidity ratio.
T_REG_EFFECTIVE_SOURCE = "T_reg_nach_HX"   # never use raw T_reg_in for KPIs

# Regeneration temperature bins for binned KPIs [°C]
T_REG_BINS = [30, 35, 40, 45, 50, 55, 60, 65, 70]

# ─────────────────────────────────────────────────────────────────────────────
# Column map: raw merged names → short aliases used everywhere in the code
# ─────────────────────────────────────────────────────────────────────────────
COLUMN_MAP = {
    # Desiccant / DAQ973A channels
    "desiccant_T_reg_in":     "T_reg_in",       # ch 102 [°C]  (PRE-heater!)
    "desiccant_Phi_reg_in":   "Phi_reg_in",     # ch 103 [%]
    "desiccant_T_RL_III":     "T_RL_III",       # ch 104 [°C]
    "desiccant_T_VL_III":     "T_VL_III",       # ch 105 [°C]
    "desiccant_T_proc_in":    "T_proc_in",      # ch 106 [°C]
    "desiccant_Phi_proc_in":  "Phi_proc_in",    # ch 107 [%]
    "desiccant_T_proc_out":   "T_proc_out",     # ch 108 [°C]
    "desiccant_Phi_proc_out": "Phi_proc_out",   # ch 109 [%]
    "desiccant_T_reg_out":    "T_reg_out",      # ch 112 [°C]
    "desiccant_Phi_reg_out":  "Phi_reg_out",    # ch 113 [%]
    "desiccant_V_dot_III":    "V_dot_III",      # ch 121 [L/s]
    "desiccant_u_proc_out":     "u_proc_out",       # ch 117 [m/s]
    "desiccant_T_proc_out_Vol": "T_proc_out_Vol",   # ch 118 [°C]
    "desiccant_V_dot_reg":      "V_dot_reg",        # ch 120 [V_DOT_REG_UNITS]
    "desiccant_V_dot_II":       "V_dot_II",         # ch 122

    # Solar / UVR channels
    "solar_Ana1_T_Kollektor":            "T_Kollektor",
    "solar_Ana2_T_I_VL":                 "T_I_VL",
    "solar_Ana3_T_I_RL":                 "T_I_RL",
    "solar_Ana4_T_II_VL":                "T_II_VL",
    "solar_Ana5_T_II_RL":                "T_II_RL",
    "solar_Ana6_T_SP_oben":              "T_SP_oben",
    "solar_Ana7_T_Anf_Entfeuchter":      "T_Anf_Entfeuchter",
    "solar_Ana8_T_reg_nach_HX_(TIBT851)": "T_reg_nach_HX",
    "solar_Ana9_T_SP_mitte_ob":          "T_SP_mitte_ob",
    "solar_Ana10_T_SP_mitte_unten":      "T_SP_mitte_unten",
    "solar_Ana11_T_SP_unten":            "T_SP_unten",
    "solar_Ana12_T_III_VL_1":            "T_III_VL_1",
    "solar_Ana13_T_AU":                  "T_AU",
    "solar_Ana14_Betrieb_Entfeuchter":   "Betrieb_Entfeuchter",
    "solar_Ana15_P_el":                  "P_el",
    "solar_Ana16_Störung_Entfeuchter":   "Stoerung",
    "solar_Ana17_PWM_Pumpe_I":           "PWM_Pumpe_I",
    "solar_Ana18_T_reg_(TICBT103)":      "T_reg_TICBT103",
    "solar_Dig1_Pumpe_I":                "Pumpe_I",
    "solar_Dig2_Pumpe_II":               "Pumpe_II",
    "solar_Dig3_Pumpe_III":              "Pumpe_III",
    "solar_Dig5_Anforderung_Entfeuchter": "Anforderung_DW",

    # names as they come out of ingest.load_solar_uvr on raw UVR exports
    # (label suffixes that differ from the plain aliases above)
    "solar_T_reg_nach_HX_(TIBT851)":     "T_reg_nach_HX",
    "solar_T_reg_(TICBT103)":            "T_reg_TICBT103",
    "solar_PWM Pumpe_I":                 "PWM_Pumpe_I",
    "solar_Anforderung_Entfeuchter":     "Anforderung_DW",
    "solar_Stoerung_Entfeuchter":        "Stoerung",
}
