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
    Scan Sweep Time,Scan Number,102 (°C)- T_reg_in,106 (°C)- T_proc_in,117 (Vdc)- u_proc_out
    2026-06-01 12:00:00.000,1,22.5,26.1,2.5
    2026-06-01 12:02:00.000,2,22.7,26.0,2.6
    2026-06-01 12:04:00.000,3,-40.0,25.9,2.4
    """)


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_trace_number_parsing():
    assert ingest.trace_number("Trace 23.csv") == 23
    assert ingest.trace_number("trace 24.csv") == 24
    assert ingest.trace_number("something.csv") is None


def test_daq_loader_and_unconverted_voltage_warns(tmp_path):
    f = _write(tmp_path, "Trace 23.csv", DAQ_CSV)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        df = ingest.load_daq_trace(f)
    assert len(df) == 3
    assert "T_reg_in" in df.columns
    # trace 23 < cutoff and no coefficients → renamed, warned
    assert "u_proc_out_raw_V" in df.columns
    assert any("u_proc_out" in str(x.message) for x in w)


def test_daq_loader_post_cutoff_no_conversion(tmp_path):
    f = _write(tmp_path, "Trace 24.csv", DAQ_CSV)
    df = ingest.load_daq_trace(f)
    # logger already converted → column kept as-is
    assert "u_proc_out" in df.columns
    assert df["u_proc_out"].iloc[0] == pytest.approx(2.5)


def test_artefact_filter():
    idx = pd.date_range("2026-06-01", periods=3, freq="2min",
                        tz="Europe/Berlin")
    df = pd.DataFrame({"T_reg_in": [22.5, -40.0, 22.7],
                       "T_proc_in": [26.0, 26.0, 26.0],
                       "T_Kollektor": [55.0, 55.0, 55.0]}, index=idx)
    out, n = quality.filter_artefacts(df)
    assert n == 1
    assert np.isnan(out["T_proc_in"].iloc[1])       # DAQ row masked
    assert out["T_Kollektor"].iloc[1] == 55.0        # solar row kept


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
