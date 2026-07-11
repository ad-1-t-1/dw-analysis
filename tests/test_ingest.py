"""Synthetic raw-file tests for ingestion, trace conversion, quality checks."""
import textwrap
import warnings

import numpy as np
import pandas as pd
import pytest

from dw_analysis import config, ingest, quality


DAQ_CSV = textwrap.dedent("""\
    metadata line 1
    metadata line 2
    Scan Sweep Time,Scan Number,102 (°C)- T_reg_in,106 (°C)- T_proc_in,117 (Vdc),118 (Vdc),120 (Vdc),122 (Adc)
    2026-06-01 12:00:00.000,1,22.5,26.1,2.5,5.0,1.0,0.008
    2026-06-01 12:02:00.000,2,22.7,26.0,2.6,5.1,1.1,0.008
    2026-06-01 12:04:00.000,3,-40.0,25.9,2.4,5.2,1.2,0.008
    """)

DAQ_CSV_POST24 = textwrap.dedent("""\
    metadata line 1
    metadata line 2
    Scan Sweep Time,Scan Number,102 (°C)- T_reg_in,117 (Vdc)- u_proc_out
    2026-06-01 12:00:00.000,1,22.5,2.5
    2026-06-01 12:02:00.000,2,22.7,2.6
    """)


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_trace_number_parsing():
    assert ingest.trace_number("Trace 23.csv") == 23
    assert ingest.trace_number("trace 24.csv") == 24
    assert ingest.trace_number("something.csv") is None


def test_pre_trace24_conversions_applied(tmp_path):
    # coefficients from merge.py:
    # ch117 identity; ch118 = 9U−20; ch120 = 500U−200; ch122 = 187500·I−750
    f = _write(tmp_path, "Trace 23.csv", DAQ_CSV)
    df = ingest.load_daq_trace(f)
    assert len(df) == 3
    assert df["u_proc_out"].iloc[0] == pytest.approx(2.5)          # 1·2.5
    assert df["T_proc_out_Vol"].iloc[0] == pytest.approx(25.0)     # 9·5−20
    assert df["V_dot_reg"].iloc[0] == pytest.approx(300.0)         # 500·1−200
    assert df["V_dot_II"].iloc[0] == pytest.approx(750.0)          # 187500·0.008−750
    assert "117 (Vdc)" not in df.columns                           # raw dropped


def test_post_cutoff_not_double_converted(tmp_path):
    f = _write(tmp_path, "Trace 24.csv", DAQ_CSV_POST24)
    df = ingest.load_daq_trace(f)
    # logger already converted → alias column arrives named, value untouched
    assert df["u_proc_out"].iloc[0] == pytest.approx(2.5)


def test_post_cutoff_with_raw_columns_warns(tmp_path):
    # a trace ≥ 24 should never contain raw '117 (Vdc)' columns; if it does,
    # warn loudly instead of silently guessing
    f = _write(tmp_path, "Trace 25.csv", DAQ_CSV)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ingest.load_daq_trace(f)
    assert any("check logger config" in str(x.message) for x in w)


def test_artefact_filter_masks_only_affected_probe():
    idx = pd.date_range("2026-06-01", periods=3, freq="2min",
                        tz="Europe/Berlin")
    df = pd.DataFrame({"T_reg_in": [22.5, -40.0, 22.7],
                       "Phi_reg_in": [40.0, 0.0, 41.0],   # RH=0 artefact
                       "T_proc_in": [26.0, 26.0, 26.0],   # valid probe
                       "T_VL_III": [55.0, 56.0, 55.5],    # valid water sensor
                       "T_Kollektor": [55.0, 55.0, 55.0]}, index=idx)
    out, n = quality.filter_artefacts(df)
    assert n == 1
    assert np.isnan(out["T_reg_in"].iloc[1])         # bad probe T masked
    assert np.isnan(out["Phi_reg_in"].iloc[1])       # paired RH masked too
    assert out["T_proc_in"].iloc[1] == 26.0          # other probe KEPT
    assert out["T_VL_III"].iloc[1] == 56.0           # water circuit KEPT
    assert out["T_Kollektor"].iloc[1] == 55.0        # solar KEPT


def test_plausibility():
    idx = pd.date_range("2026-06-01", periods=2, freq="2min",
                        tz="Europe/Berlin")
    df = pd.DataFrame({"Phi_proc_in": [50.0, 150.0],
                       "T_proc_in": [26.0, 300.0]}, index=idx)
    out, rep = quality.apply_plausibility(df)
    assert np.isnan(out["Phi_proc_in"].iloc[1])
    assert np.isnan(out["T_proc_in"].iloc[1])
    assert rep["flagged"].sum() == 2


def test_solar_uvr_loader(tmp_path):
    csv = ("Datum;Uhrzeit;Ana1 - 1: T_Kollektor;Dig1 - 1: Pumpe_I\n"
           "2026-06-01;12:00:00;55,3;1\n"
           "2026-06-01;12:02:00;56,1;1\n")
    f = _write(tmp_path, "solar_log.csv", csv)
    df = ingest.load_solar_uvr(f)
    assert df["T_Kollektor"].iloc[0] == pytest.approx(55.3)
    assert df["Pumpe_I"].iloc[1] == 1
