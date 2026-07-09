"""Standard figures for weekly reports and season tracking."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def _fmt(ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax.grid(True, alpha=0.3)


def plot_overview(df: pd.DataFrame, path: Path):
    """4-panel operational overview."""
    fig, axes = plt.subplots(4, 1, figsize=(14, 14), sharex=True)

    ax = axes[0]
    for col, lbl in [("T_Kollektor", "Collector"), ("T_SP_oben", "Storage top"),
                     ("T_SP_unten", "Storage bottom"), ("T_AU", "Outdoor")]:
        if col in df.columns:
            ax.plot(df.index, df[col], lw=0.8, label=lbl)
    ax.set_ylabel("T [°C]"); ax.legend(fontsize=8, ncol=4); _fmt(ax)
    ax.set_title("Solar system", fontsize=10, loc="left")

    ax = axes[1]
    for col, lbl in [("T_proc_in", "T proc in"), ("T_proc_out", "T proc out"),
                     ("T_reg_eff", "T reg eff (after HX)"),
                     ("T_reg_out", "T reg out")]:
        if col in df.columns:
            ax.plot(df.index, df[col], lw=0.8, label=lbl)
    ax.set_ylabel("T [°C]"); ax.legend(fontsize=8, ncol=4); _fmt(ax)
    ax.set_title("Air streams", fontsize=10, loc="left")

    ax = axes[2]
    for col, lbl in [("x_proc_in_gkg", "x proc in"),
                     ("x_proc_out_gkg", "x proc out"),
                     ("x_reg_out_gkg", "x reg out")]:
        if col in df.columns:
            ax.plot(df.index, df[col], lw=0.8, label=lbl)
    if "Delta_x_proc_gkg" in df.columns:
        ax.fill_between(df.index, df["Delta_x_proc_gkg"].clip(lower=0),
                        alpha=0.25, color="green", label="Δx removed")
    ax.set_ylabel("x [g/kg]"); ax.legend(fontsize=8, ncol=4); _fmt(ax)
    ax.set_title("Humidity ratios", fontsize=10, loc="left")

    ax = axes[3]
    if "Q_reg_W" in df.columns:
        ax.fill_between(df.index, df["Q_reg_W"].clip(lower=0) / 1000.0,
                        alpha=0.4, color="darkred", label="Q̇ reg [kW]")
    if "solar_active" in df.columns:
        ax.fill_between(df.index, df["solar_active"] * 0.5, alpha=0.3,
                        color="gold", label="solar active")
    ax.set_ylabel("kW / flag"); ax.legend(fontsize=8, ncol=2); _fmt(ax)
    ax.set_title("Regeneration heat & solar status", fontsize=10, loc="left")

    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_kpi_vs_treg(df: pd.DataFrame, path: Path):
    """Scatter of dehumidification vs effective regeneration temperature."""
    if not {"T_reg_eff", "Delta_x_proc_gkg"} <= set(df.columns):
        return
    d = df
    if "Betrieb_Entfeuchter" in df.columns:
        d = df[df["Betrieb_Entfeuchter"] > 0.5]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(d["T_reg_eff"], d["Delta_x_proc_gkg"], s=6, alpha=0.35)
    axes[0].set_xlabel("T_reg,eff [°C]")
    axes[0].set_ylabel("Δx process [g/kg]")
    axes[0].grid(alpha=0.3)
    if "eta_deh" in d.columns:
        axes[1].scatter(d["T_reg_eff"], d["eta_deh"], s=6, alpha=0.35,
                        color="darkorange")
        axes[1].set_xlabel("T_reg,eff [°C]")
        axes[1].set_ylabel("η_deh [–]")
        axes[1].set_ylim(0, 1)
        axes[1].grid(alpha=0.3)
    fig.suptitle("Dehumidification vs regeneration temperature")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_season_cumulative(daily: pd.DataFrame, path: Path):
    """Cumulative season totals: water removed + regeneration heat."""
    if daily.empty:
        return
    fig, ax1 = plt.subplots(figsize=(12, 5))
    if "water_removed_kg" in daily.columns:
        ax1.plot(daily.index, daily["water_removed_kg"].fillna(0).cumsum(),
                 color="steelblue", lw=2, label="Water removed [kg]")
        ax1.set_ylabel("Cumulative water removed [kg]", color="steelblue")
    ax2 = ax1.twinx()
    if "Q_reg_kWh" in daily.columns:
        ax2.plot(daily.index, daily["Q_reg_kWh"].fillna(0).cumsum(),
                 color="darkred", lw=2, label="Q reg [kWh]")
        ax2.set_ylabel("Cumulative regeneration heat [kWh]", color="darkred")
    ax1.grid(alpha=0.3)
    ax1.set_title("Season cumulative totals")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_psychrometric(df: pd.DataFrame, path: Path):
    """Process in/out states on a T–x chart (simple psychrometric view)."""
    need = {"T_proc_in", "x_proc_in_gkg", "T_proc_out", "x_proc_out_gkg"}
    if not need <= set(df.columns):
        return
    d = df
    if "Betrieb_Entfeuchter" in df.columns:
        d = df[df["Betrieb_Entfeuchter"] > 0.5]
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter(d["T_proc_in"], d["x_proc_in_gkg"], s=6, alpha=0.4,
               label="process in", color="steelblue")
    ax.scatter(d["T_proc_out"], d["x_proc_out_gkg"], s=6, alpha=0.4,
               label="process out", color="tomato")
    # saturation line via CoolProp
    import numpy as np
    from .psychro import humidity_ratio
    T = np.arange(0, 51, 1.0)
    ax.plot(T, humidity_ratio(T, np.full_like(T, 100.0)) * 1000.0,
            "k-", lw=1, label="saturation")
    ax.set_xlabel("Temperature [°C]")
    ax.set_ylabel("Humidity ratio [g/kg]")
    ax.legend(); ax.grid(alpha=0.3)
    ax.set_title("Process air states (wheel operating)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
