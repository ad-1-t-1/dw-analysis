"""
Raw data ingestion: DAQ973A "Trace" CSVs + UVR solar-controller CSVs.

Weekly workflow: drop raw files into  data/raw/<week-folder>/  (any folder
name; desiccant Trace CSVs and solar UVR CSVs may be mixed or in
subfolders). `build_merged()` loads everything, applies plant-specific
corrections, resamples both sources onto a common 2-minute grid
(Europe/Berlin, DST-aware) and returns one merged DataFrame with
'desiccant_' / 'solar_' column prefixes — the same layout as the historical
merged_solar_desiccant.pkl.

Raw files are never modified.
"""
from __future__ import annotations

import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from . import config


# ─────────────────────────────────────────────────────────────────────────────
# DAQ973A Trace CSVs (Keysight)
# ─────────────────────────────────────────────────────────────────────────────
def trace_number(filepath: str | Path) -> int | None:
    """Extract the trace number from a filename like 'Trace 23.csv'."""
    m = re.search(r"[Tt]race\s*(\d+)", Path(filepath).name)
    return int(m.group(1)) if m else None


def _apply_voltage_conversions(df: pd.DataFrame, n_trace: int | None,
                               fname: str) -> pd.DataFrame:
    """Convert raw V/A channels (ch 117/118/120/122) to physical units.

    Logger behaviour (from merge.py, verified against Trace 21 header):
      trace  < TRACE_CONVERSION_CUTOFF (24): logger stored raw signals in
        columns named '117 (Vdc)', '118 (Vdc)', '120 (Vdc)', '122 (Adc)'
        → convert here (physical = scale*signal + offset) and rename.
      trace >= cutoff: logger already converted (and with NEW ranges for
        ch 120/122) → columns arrive with alias names; do NOT touch them.
    Unknown trace number: warn; convert only if raw-named columns present
    (their presence itself indicates an unconverted file), so silent
    double-conversion is impossible.
    """
    raw_cols = [c for c in config.VOLTAGE_CONVERSIONS if c in df.columns]
    if n_trace is not None and n_trace >= config.TRACE_CONVERSION_CUTOFF:
        if raw_cols:
            warnings.warn(f"{fname}: trace {n_trace} >= cutoff but raw "
                          f"columns {raw_cols} present — check logger config.")
        return df
    if n_trace is None and raw_cols:
        warnings.warn(f"{fname}: no trace number in filename; raw columns "
                      f"{raw_cols} found → converting as pre-trace-24.")
    for raw_col in raw_cols:
        conv = config.VOLTAGE_CONVERSIONS[raw_col]
        df[conv["name"]] = conv["scale"] * df[raw_col] + conv["offset"]
        df = df.drop(columns=[raw_col])
    return df


def load_daq_trace(filepath: str | Path) -> pd.DataFrame:
    """Load one Keysight DAQ973A Trace CSV.

    Format: ~62-line metadata header, then a table whose header row starts
    with 'Scan Sweep Time'; column labels like '102 (°C)- T_reg_in'.
    Returns tz-naive datetime-indexed DataFrame with clean channel names,
    voltage conversions applied per trace number.
    """
    filepath = Path(filepath)
    header_row = None
    with open(filepath, encoding="utf-8-sig") as fh:
        for i, line in enumerate(fh):
            if line.startswith("Scan Sweep Time"):
                header_row = i
                break
    if header_row is None:
        raise ValueError(f"No 'Scan Sweep Time' header found in {filepath.name}")

    raw = pd.read_csv(filepath, skiprows=header_row, encoding="utf-8-sig",
                      low_memory=False)
    raw = raw.rename(columns={raw.columns[0]: "timestamp"})
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], errors="coerce")
    raw = raw.dropna(subset=["timestamp"]).set_index("timestamp")

    def clean(c: str) -> str:
        c = str(c).strip()
        return c.split("- ", 1)[-1].strip() if "- " in c else c

    raw.columns = [clean(c) for c in raw.columns]
    raw = raw.drop(columns=["Scan Number"], errors="ignore")
    raw = raw.dropna(axis=1, how="all").apply(pd.to_numeric, errors="coerce")
    raw = raw.sort_index()
    return _apply_voltage_conversions(raw, trace_number(filepath), filepath.name)


# ─────────────────────────────────────────────────────────────────────────────
# UVR solar-controller CSVs
# ─────────────────────────────────────────────────────────────────────────────
def load_solar_uvr(filepath: str | Path) -> pd.DataFrame:
    """Load one UVR CSV (semicolon-separated, German decimal commas,
    'Datum'+'Uhrzeit' timestamp columns, labels like 'Ana1 - 1: T_Kollektor')."""
    raw = pd.read_csv(filepath, sep=";", encoding="latin-1", decimal=",",
                      low_memory=False)
    raw["timestamp"] = pd.to_datetime(
        raw["Datum"].astype(str) + " " + raw["Uhrzeit"].astype(str),
        dayfirst=False, errors="coerce")
    raw = (raw.dropna(subset=["timestamp"]).set_index("timestamp")
              .drop(columns=["Datum", "Uhrzeit"], errors="ignore"))

    def clean(c: str) -> str:
        c = str(c).strip()
        if ": " in c:
            c = c.split(": ", 1)[-1]
        elif " - " in c:
            c = c.split(" - ", 1)[-1]
        return c.replace("Störung", "Stoerung").replace("St\xf6rung",
                                                        "Stoerung").strip()

    raw.columns = [clean(c) for c in raw.columns]
    if raw.columns.duplicated().any():
        dups = raw.columns[raw.columns.duplicated()].unique().tolist()
        warnings.warn(f"{Path(filepath).name}: duplicate column names after "
                      f"cleaning {dups} — keeping first occurrence.")
        raw = raw.loc[:, ~raw.columns.duplicated()]
    return raw.apply(pd.to_numeric, errors="coerce").sort_index()


# ─────────────────────────────────────────────────────────────────────────────
# Folder-level loading and merging
# ─────────────────────────────────────────────────────────────────────────────
def _localize(df: pd.DataFrame) -> pd.DataFrame:
    """Attach Europe/Berlin timezone.

    Loggers record local wall-clock time. DST edge cases:
      - ambiguous times (autumn fold): first occurrence assumed (loggers run
        continuously, so 'infer' would also work but can fail on gaps)
      - nonexistent times (spring gap): dropped (NaT)
    Affected rows: at most 2 h per year — negligible for seasonal KPIs but
    logged in the data-quality report.
    """
    df = df[~df.index.duplicated(keep="last")]
    idx = df.index.tz_localize(config.TZ, ambiguous=True,
                               nonexistent="NaT")
    df = df.set_axis(idx)
    return df[df.index.notna()]


def _concat_folder(folder: Path, loader, pattern: str) -> pd.DataFrame | None:
    frames = []
    for f in sorted(folder.rglob(pattern)):
        try:
            frames.append(loader(f))
        except Exception as e:                      # noqa: BLE001
            warnings.warn(f"Skipping {f.name}: {e}")
    if not frames:
        return None
    df = pd.concat(frames)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def build_merged(raw_dir: str | Path) -> pd.DataFrame:
    """Load all raw files under `raw_dir` (recursively) and return the merged,
    prefixed, 2-minute-grid DataFrame (tz-aware Europe/Berlin).

    Resampling uses the mean within each 2-min bin (no forward-fill across
    gaps — missing stays missing so integrals can exclude it).
    """
    raw_dir = Path(raw_dir)
    daq = _concat_folder(raw_dir, load_daq_trace, "[Tt]race*.csv")
    # UVR files: any csv that is not a Trace file
    solar_frames = []
    for f in sorted(raw_dir.rglob("*.csv")):
        if re.search(r"[Tt]race\s*\d+", f.name):
            continue
        try:
            solar_frames.append(load_solar_uvr(f))
        except Exception as e:                      # noqa: BLE001
            warnings.warn(f"Skipping {f.name} (not a UVR file?): {e}")
    solar = None
    if solar_frames:
        solar = pd.concat(solar_frames)
        solar = solar[~solar.index.duplicated(keep="last")].sort_index()

    if daq is None and solar is None:
        raise FileNotFoundError(f"No usable CSV files found under {raw_dir}")

    parts = []
    if daq is not None:
        daq = _localize(daq).resample(config.RESAMPLE_RULE).mean()
        parts.append(daq.add_prefix("desiccant_"))
    if solar is not None:
        solar = _localize(solar).resample(config.RESAMPLE_RULE).mean()
        # replicate historical naming: solar_Ana1_T_Kollektor etc. is NOT
        # reproducible from cleaned names, so keep clean names prefixed —
        # config.COLUMN_MAP contains both variants via apply_column_map().
        parts.append(solar.add_prefix("solar_"))

    merged = pd.concat(parts, axis=1).sort_index()
    return merged


def apply_column_map(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw merged columns to short aliases (see config.COLUMN_MAP).

    Handles both historical names ('solar_Ana8_T_reg_nach_HX_(TIBT851)')
    and names produced by build_merged ('solar_T_reg_nach_HX',
    'desiccant_T_reg_in').
    """
    rename = {}
    for raw, alias in config.COLUMN_MAP.items():
        if raw in df.columns:
            rename[raw] = alias
    # fallback: prefix + alias directly
    for col in df.columns:
        if col in rename:
            continue
        for prefix in ("desiccant_", "solar_"):
            if col.startswith(prefix) and col[len(prefix):] in set(
                    config.COLUMN_MAP.values()):
                rename[col] = col[len(prefix):]
    df = df.rename(columns=rename)
    # legacy pickle and raw-built frames may map DIFFERENT raw names onto the
    # same alias (e.g. 'solar_Ana1_T_Kollektor' and 'solar_T_Kollektor') —
    # coalesce duplicates, first non-null value wins per timestamp
    if df.columns.duplicated().any():
        out = {}
        for name in dict.fromkeys(df.columns):
            sub = df.loc[:, df.columns == name]
            out[name] = (sub.iloc[:, 0] if sub.shape[1] == 1
                         else sub.bfill(axis=1).iloc[:, 0])
        df = pd.DataFrame(out, index=df.index)
    return df


def load_merged_pkl(pkl_path: str | Path) -> pd.DataFrame:
    """Load a historical merged pickle (e.g. merged_solar_desiccant.pkl)."""
    df = pd.read_pickle(pkl_path)
    df.index.name = "timestamp"
    if df.index.tz is None:
        df = _localize(df)
    else:
        # historical pickle stored a fixed UTC+02:00 offset; normalise to the
        # named zone so it concatenates cleanly with newly ingested data
        df.index = df.index.tz_convert(config.TZ)
    return df
