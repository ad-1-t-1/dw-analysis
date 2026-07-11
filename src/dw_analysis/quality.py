"""
Data-quality checks: plausibility limits, sensor artefacts, gap detection.

Every pipeline run produces a per-period quality report so that KPI numbers
are always accompanied by a statement of how much data they rest on.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def apply_plausibility(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Set physically impossible values to NaN.

    Limits per column-name prefix are defined in config.PLAUSIBILITY.
    Returns (cleaned df, report DataFrame with counts of flagged values).
    """
    df = df.copy()
    rows = []
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        for prefix, (lo, hi) in config.PLAUSIBILITY.items():
            if col.startswith(prefix):
                bad = pd.Series(False, index=df.index)
                if lo is not None:
                    bad |= df[col] < lo
                if hi is not None:
                    bad |= df[col] > hi
                n = int(bad.sum())
                if n:
                    df.loc[bad, col] = np.nan
                    rows.append({"column": col, "flagged": n,
                                 "rule": f"[{lo}, {hi}]"})
                break
    report = pd.DataFrame(rows, columns=["column", "flagged", "rule"])
    return df, report


# Combined T/RH probes on the desiccant DAQ: when a probe is disconnected its
# temperature channel reads ≈ −40 °C (0 V × gain − offset) AND its RH channel
# reads 0.0 % — which would otherwise pass plausibility as "valid dry air"
# and corrupt humidity-based KPIs. Mask both channels of the affected probe.
_PROBE_PAIRS = {
    "T_reg_in": "Phi_reg_in",
    "T_reg_out": "Phi_reg_out",
    "T_proc_in": "Phi_proc_in",
    "T_proc_out": "Phi_proc_out",
}


def filter_artefacts(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Mask disconnected-probe artefacts PER SENSOR PAIR, not per row.

    Verified on the 2026-06 dataset: while the regeneration-air probes were
    disconnected (T = −40, RH = 0.0) for ~half the season, the process-air
    probes and the circuit-III water sensors (T_VL/T_RL/V_dot) recorded
    valid data throughout. Masking whole rows would silently discard >50 %
    of the regeneration-heat measurement — so only the channels that are
    provably bad are removed. Solar/UVR channels are never touched here.

    Returns (cleaned df, number of masked probe-samples).
    """
    df = df.copy()
    n = 0
    for T_col, Phi_col in _PROBE_PAIRS.items():
        if T_col not in df.columns:
            continue
        bad = df[T_col] <= config.T_ARTEFACT_THRESHOLD
        if bad.any():
            n += int(bad.sum())
            df.loc[bad, T_col] = np.nan
            if Phi_col in df.columns:
                df.loc[bad, Phi_col] = np.nan
    return df, n


def gap_report(df: pd.DataFrame, key_cols: list[str] | None = None
               ) -> pd.DataFrame:
    """Detect gaps in the time index and in key measurement columns.

    A gap = consecutive-timestamp spacing larger than 2× the resample grid.
    """
    grid = pd.Timedelta(config.RESAMPLE_RULE)
    rows = []
    dt = df.index.to_series().diff()
    idx_gaps = dt[dt > 2 * grid]
    for ts, d in idx_gaps.items():
        rows.append({"kind": "index", "column": "-", "gap_end": ts,
                     "duration": d})
    for col in (key_cols or ["T_proc_in", "T_reg_nach_HX", "V_dot_III"]):
        if col not in df.columns:
            continue
        miss = df[col].isna()
        # runs of consecutive NaNs
        run_id = (miss != miss.shift()).cumsum()
        for _, grp in df.index.to_series()[miss].groupby(run_id[miss]):
            dur = grp.iloc[-1] - grp.iloc[0] + grid
            if dur > 2 * grid:
                rows.append({"kind": "nan-run", "column": col,
                             "gap_end": grp.iloc[-1], "duration": dur})
    return pd.DataFrame(rows, columns=["kind", "column", "gap_end", "duration"])


def coverage(df: pd.DataFrame, col: str) -> float:
    """Fraction of the period for which `col` has data (0–1)."""
    if col not in df.columns or len(df) == 0:
        return 0.0
    return float(df[col].notna().mean())


def quality_summary(df: pd.DataFrame, plaus_report: pd.DataFrame,
                    n_artefacts: int) -> dict:
    """Assemble a dict for the markdown report."""
    return {
        "rows": len(df),
        "start": str(df.index[0]) if len(df) else "-",
        "end": str(df.index[-1]) if len(df) else "-",
        "artefact_rows_masked": n_artefacts,
        "plausibility_flags": int(plaus_report["flagged"].sum())
                              if len(plaus_report) else 0,
        "coverage_T_proc_in": round(coverage(df, "T_proc_in"), 3),
        "coverage_T_reg_nach_HX": round(coverage(df, "T_reg_nach_HX"), 3),
        "coverage_V_dot_III": round(coverage(df, "V_dot_III"), 3),
    }
