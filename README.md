# dw-analysis — Solar-assisted desiccant wheel pilot plant (Univ. of Kassel)

Automated analysis of weekly measurement data from the pilot plant coupling
a solar thermal system (collector + stratified storage) with a desiccant
wheel for air dehumidification.

Current season results: **[results/SUMMARY.md](results/SUMMARY.md)** —
regenerated automatically on every data upload.

## Weekly workflow

1. Copy the week's raw files into a new folder, e.g.
   `data/raw/2026-W28/` — DAQ973A `Trace NN.csv` files and UVR solar
   controller CSVs can be mixed; subfolders are fine. Raw files are never
   modified.
2. Commit and push. GitHub Actions runs the test suite, then the full
   pipeline, and commits refreshed tables, figures and `results/SUMMARY.md`.
3. Or run locally: `python run_analysis.py`

The pipeline **rebuilds the whole season from scratch on every run**
(idempotent — re-uploading or correcting a week can never duplicate rows;
results always reflect current code + all data).

## Setup

```bash
git clone <this repo>
cd dw-analysis
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest                       # verify psychrometrics against ASHRAE tables
python run_analysis.py       # needs data in data/raw/ or data/legacy/
```

## What it computes

Instantaneous time series and season-integrated totals (defined precisely in
[docs/KPI_DEFINITIONS.md](docs/KPI_DEFINITIONS.md), each with equation,
units and literature source):

water removed [kg] for any period; regeneration heat input [kWh]; specific
regeneration heat demand [kWh per kg water] binned by effective regeneration
temperature (the low-temperature-regeneration performance map); thermal COP;
dehumidification and wheel effectiveness; solar fraction of the regeneration
heat (boundary: regeneration coil) plus solar-collection share; electrical
energy; energy- and moisture-balance closure checks; per-week data-quality
report (gaps, implausible values, sensor artefacts).

All moist-air properties come from **CoolProp `HAPropsSI`** (ASHRAE RP-1485
real-gas model) — no hand-rolled correlations. Liquid-water properties for
the hydronic circuits are temperature-dependent (IAPWS-97).

## Plant-specific handling built into the code

- `T_reg_in` (DAQ ch 102) sits **before** the regeneration heating coil and
  is never used as regeneration temperature; the effective value
  `T_reg_eff` comes from `T_reg_nach_HX` (solar Ana8, TIBT851).
- Channels 117/118/120/122 are raw volts in trace files < 24 and
  logger-converted from trace 24 on. Ingestion detects the trace number and
  branches; **conversion coefficients are still missing** (see below).
- Disconnected-thermocouple artefacts (≈ −40 °C) mask the whole DAQ scan row.
- Timestamps are timezone-aware (Europe/Berlin) with explicit DST handling;
  integrals never interpolate across data gaps.

## Open issues — input needed

| # | Issue | Impact until resolved |
|---|---|---|
| 1 | ~~Voltage→physical coefficients for ch 117/118/120/122~~ **resolved** — taken from `merge.py` (ch117 identity 0–10 V = 0–10 m/s; ch118 = 9·U − 20 °C; ch120 = 500·U − 200 old range; ch122 = 187500·I − 750 old range) | — |
| 2 | Duct area at velocity sensor ch 117 → `config.PROC_DUCT_AREA_M2` | process air mass flow, water removed, COP not computable from measurement |
| 3 | Units of ch 120 (assumed m³/h; measured values ≈ 75–83 in Trace 21 window) → `config.V_DOT_REG_UNITS` | air-side balance scales directly with this |
| 4 | Flow-meter position in circuit III (supply or return?) | ~1 % systematic on Q_reg |
| 5 | Site pressure (assumed 101.325 kPa; Kassel ≈ 98.6 kPa) → `config.P_ATM` | humidity ratios ~2.7 % systematic |
| 6 | Is there any non-solar heat source feeding the regeneration coil? | solar fraction currently 1.0 by system boundary |
| 7 | Energy-balance closure over the first air-flow window (3.2 h, Trace 21) is only **0.14** — air stream picks up ~14 % of the hydronic heat input. Candidates: ch 120 units/range, HX losses, wheel not rotating during that (overnight) window, or T_reg_nach_HX not representative at low flow | air-side balance untrustworthy until explained |
| 8 | `P_el` is 0.0 throughout the dataset — electrical power channel not delivering | E_el and electric COP unavailable |
| 9 | Channel `111 (Vdc)` appears in Trace files but has no known meaning/conversion | column kept raw, unused |

## Roadmap (effort → value)

1. **Low / high** — resolve open issues 1–3: unlocks measured-flow water
   totals and COP, the project's headline numbers.
2. **Medium / high** — uncertainty propagation (RH ±2 % RH dominates Δx);
   report KPI ± bands instead of bare numbers.
3. **Medium / high** — steady-state vs dynamic period detection (e.g.
   rolling variance on T_reg_eff and inlet humidity), so literature
   comparisons use steady windows and control studies use dynamic ones.
4. **Medium / medium** — performance map Δx = f(T_reg_eff, x_p,in, flow) fitted
   over the season; basis for a regeneration-temperature control strategy.
5. **Low / medium** — collector-circuit heat metering (needs circuit I flow)
   to close the solar loop balance and report collector efficiency.
6. **Low / medium** — Sankey energy-flow diagram per week once air-side
   balance closes.

## Repository layout

```
data/raw/        weekly raw CSV drops (immutable)
data/legacy/     pre-repo merged pickle (optional)
src/dw_analysis/ package: config, ingest, quality, psychro, enrich, kpi, plots, report, pipeline
results/         auto-generated: SUMMARY.md, tables/, figures/
tests/           pytest suite incl. ASHRAE validation of CoolProp
docs/            KPI definitions with equations and sources
```

## For the supervisor

Everything needed to judge the numbers is in two files:
[results/SUMMARY.md](results/SUMMARY.md) (current results incl. data
quality and balance-closure checks) and
[docs/KPI_DEFINITIONS.md](docs/KPI_DEFINITIONS.md) (exact equations,
sources, and known accuracy limits).
