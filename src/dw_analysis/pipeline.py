"""
End-to-end pipeline.

Design: IDEMPOTENT REBUILD, not append. Every run re-derives the season
tables from all available data. This is deliberate — appending to a season
CSV silently duplicates rows when a week is re-processed (re-uploaded file,
corrected sensor conversion, changed KPI definition). Rebuilding from raw
each time guarantees results always reflect the current code and full data,
at negligible cost for a single season of 2-minute data.
"""
from __future__ import annotations

import io
import warnings
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

from . import config, enrich, ingest, kpi, plots, quality, report


def run(raw_dir: str | Path | None = None,
        legacy_pkl: str | Path | None = None,
        out_dir: str | Path = "results") -> dict:
    """Run the full analysis.

    Data sources (both optional, concatenated when both given):
      raw_dir    : folder tree of weekly raw CSV drops (data/raw)
      legacy_pkl : historical merged pickle (data before the repo existed)
    """
    out = Path(out_dir)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(parents=True, exist_ok=True)

    # ── 1 load ───────────────────────────────────────────────────────────
    frames = []
    if legacy_pkl and Path(legacy_pkl).exists():
        frames.append(ingest.load_merged_pkl(legacy_pkl))
    if raw_dir and Path(raw_dir).exists():
        try:
            frames.append(ingest.build_merged(raw_dir))
        except FileNotFoundError:
            warnings.warn(f"No raw CSVs found under {raw_dir} yet.")
    if not frames:
        raise SystemExit("No data: provide data/raw CSVs or a legacy pickle.")
    df = pd.concat(frames).sort_index()
    df = df[~df.index.duplicated(keep="last")]
    df = ingest.apply_column_map(df)

    # ── 2 quality ────────────────────────────────────────────────────────
    df, plaus = quality.apply_plausibility(df)
    df, n_art = quality.filter_artefacts(df)
    gaps = quality.gap_report(df)
    qsum = quality.quality_summary(df, plaus, n_art)

    # ── 3 enrichment + KPIs ──────────────────────────────────────────────
    df, flow_meta = enrich.enrich(df)
    df = kpi.instantaneous(df)

    # ── 4 aggregation ────────────────────────────────────────────────────
    totals = kpi.period_totals(df)
    solar = kpi.solar_fraction(df)
    balance = kpi.energy_balance(df)
    daily = kpi.resampled_summary(df, "D")
    weekly = kpi.resampled_summary(df, "W-MON")
    binned = kpi.kpis_by_temp_bin(df)

    # ── 5 outputs ────────────────────────────────────────────────────────
    daily.to_csv(out / "tables" / "season_daily.csv")
    weekly.to_csv(out / "tables" / "season_weekly.csv")
    if not binned.empty:
        binned.to_csv(out / "tables" / "kpi_by_regen_temp_bin.csv",
                      index=False)
    if len(gaps):
        gaps.to_csv(out / "tables" / "data_gaps.csv", index=False)
    if len(plaus):
        plaus.to_csv(out / "tables" / "plausibility_flags.csv", index=False)
    df.to_parquet(out / "tables" / "enriched_full.parquet")

    figs = []
    for name, fn, arg in [
        ("overview.png", plots.plot_overview, df),
        ("kpi_vs_treg.png", plots.plot_kpi_vs_treg, df),
        ("psychrometric.png", plots.plot_psychrometric, df),
        ("season_cumulative.png", plots.plot_season_cumulative, daily),
    ]:
        p = out / "figures" / name
        fn(arg, p)
        if p.exists():
            figs.append(f"figures/{name}")

    report.write_report(
        out / "SUMMARY.md",
        title=(f"Solar-assisted desiccant wheel — season summary "
               f"({qsum['start'][:10]} → {qsum['end'][:10]})"),
        quality=qsum, totals=totals, solar=solar, balance=balance,
        flow_meta=flow_meta, binned=binned, daily=daily, figures=figs)

    return {"df": df, "daily": daily, "weekly": weekly, "totals": totals,
            "solar": solar, "balance": balance, "quality": qsum}
