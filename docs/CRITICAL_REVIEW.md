# Critical review of this repository and its results

Written deliberately as a hostile reviewer (2026-07-12). Items marked ✅ were
fixed in the same commit that added this file; the rest are open and ranked
by how much they threaten the credibility of the reported numbers.

## Verdict in one paragraph

The pipeline is methodologically sound (real-gas psychrometrics, gap-aware
integration, per-sensor artefact handling, pinned definitions with sources),
but the headline result — **660 kWh regeneration heat** — currently rests on
a single water-side measurement whose only independent cross-check (the
air-side balance) disagrees by a factor of ~7 over the one window where both
exist. Until that discrepancy is explained, treat Q_reg as *provisional*.
The project's actual target KPIs (water removed [kg], kWh per kg water, COP)
are still not computable from measurement because one geometry constant is
missing. The dataset covers 22 days at 57 % instrument coverage — too little
for seasonal claims.

## High severity — threatens the numbers

1. **Energy-balance closure = 0.14** (air side picks up 14 % of hydronic
   input, 3.2 h window, Trace 21). At least one of: ch 120 units/range
   wrong, regen air flow sensor faulty, wheel idle during window, or Q_reg
   overstated. Action: confirm ch 120 output unit with the colleague; log a
   window where the wheel is verifiably rotating with flow present.
2. **No uncertainty quantification.** RH sensors are typically ±2–3 % RH;
   at Δx ≈ 0.8 g/kg (the 30–35 °C bin) the moisture-removal signal is the
   same order as sensor uncertainty. The binned trend (0.83 → 1.79 g/kg) is
   probably real; individual bin values should not be quoted without bands.
3. **Solar fraction = 1.0 is a boundary assumption, not a measurement.**
   No heat metering on the solar circuits confirms the storage is charged
   only by the collector. As presented it invites over-interpretation:
   "100 % solar" is a definition, not a finding.
4. **T_reg bins are confounded.** Higher regeneration temperatures occur at
   specific times of day/weather; inlet humidity and flow are not controlled
   for. The Δx-vs-T_reg table is descriptive, not a performance map. A
   multivariate fit (Δx ~ T_reg + x_in + flow) is needed before control
   conclusions.

## Medium severity — fixed or fixable

5. ✅ **Site pressure** was 101.325 kPa; Kassel (~230 m) ≈ 98.6 kPa →
   all humidity ratios were ~2.7 % low. Fixed (config.P_ATM = 98 600 Pa);
   replace with measured station pressure when available.
6. ✅ **"Season totals" naming was misleading** at 57 % coverage. Renamed
   to "Measured-period totals" with an explicit no-extrapolation note.
7. ✅ **Positive-only integration bias.** Q_reg used clip(≥0); sensor noise
   around zero then only adds. The net integral is now reported alongside —
   if the two diverge, suspect the positive-only figure.
8. ✅ **CI observability.** A successful run with unchanged results was
   indistinguishable from a dead workflow. SUMMARY.md now embeds a run
   timestamp + commit SHA, so every pipeline run produces a visible commit.
9. **P_el is 0.0 for the entire dataset** — nobody has chased why. Without
   it there is no electrical COP and no parasitic-load accounting.
10. **Post-trace-24 ingestion is untested against a real file.** The
    cutoff logic is unit-tested with synthetic data, but no trace ≥ 24
    exists in the repo; the assumed column naming ("117 (Vdc)- u_proc_out")
    is a guess. First real file may break ingestion — upload one soon.

## Low severity — hygiene

11. Repo stores raw data in git (38 MB and growing weekly): fine for a
    season, will need git-LFS or external storage within a year.
12. Dependencies are lower-bounded but not upper-pinned; a pandas 3.x
    release could silently break CI.
13. No end-to-end integration test (tiny synthetic raw folder → SUMMARY).
14. Channel 111 (Vdc) remains unidentified.

## What would most improve the analysis, in order

1. The duct area at ch 117 (one number → unlocks water removed, kWh/kg, COP).
2. Resolve the closure discrepancy (ch 120 unit confirmation + one verified
   operating window).
3. Uncertainty propagation on Δx and all derived KPIs.
4. Steady-state detection so literature comparisons use steady windows only.
5. A multivariate performance map instead of 1-D temperature bins.
