# Handover: Campaign Export Function

**Date:** November 28, 2025
**Branch:** `feature/export-function`
**Commit:** `109bbbd`

---

## Summary

Implemented the campaign export button that generates a downloadable zip file containing all campaign data (CSVs) and visualizations (PNGs).

---

## What Was Done

### 1. Export Utility Module

Created `src/ui/utils/export.py` with three main functions:

| Function | Purpose |
|----------|---------|
| `gather_campaign_data()` | Collects all campaign data from query functions into DataFrames |
| `create_charts()` | Generates Plotly charts as PNG images using kaleido |
| `create_export_zip()` | Packages everything into a downloadable zip file |

### 2. Data Exported (9 CSV files)

| File | Source Tab | Content |
|------|-----------|---------|
| `frame_audience_summary.csv` | Overview | Frame-level audience data with all demographics |
| `weekly_performance_individual.csv` | Weekly Reach | Individual week metrics (reach, impacts, GRP) |
| `weekly_performance_cumulative.csv` | Weekly Reach | Cumulative build data |
| `daily_impacts.csv` | Time Series | Daily impacts by demographic |
| `hourly_impacts.csv` | Time Series | Hourly impacts with day of week |
| `geographic_frame_data.csv` | Geographic | Frame locations with impacts |
| `regional_impacts.csv` | Geographic | TV region level aggregates |
| `environment_impacts.csv` | Geographic | Environment type breakdown |
| `frame_daily_impacts.csv` | Detailed Analysis | Frame × day level granular data |
| `frame_hourly_impacts.csv` | Detailed Analysis | Frame × hour level granular data |

### 3. Visualizations Exported (9 PNG charts)

| Chart | Source Tab | Description |
|-------|-----------|-------------|
| `weekly_reach_impacts.png` | Weekly Reach | Grouped bar chart of reach/impacts by week |
| `weekly_grp.png` | Weekly Reach | GRP bar chart by week |
| `cumulative_build.png` | Weekly Reach | Dual-axis line chart for cumulative metrics |
| `daily_impacts.png` | Time Series | Spline line chart of daily impacts |
| `day_of_week.png` | Time Series | Bar chart by day of week |
| `hourly_heatmap.png` | Time Series | 7×24 heatmap of hourly activity |
| `hourly_bar.png` | Time Series | Average impacts by hour bar chart |
| `regional_impacts.png` | Geographic | Top 12 regions bar chart |
| `environment_distribution.png` | Geographic | Donut chart of environments |

### 4. Additional Files in Zip

- `README.txt` - Export contents and campaign summary
- `campaign_summary.json` - Campaign metadata in JSON format

---

## UI Changes

Updated `src/ui/app_api_real.py`:

- Export button (line 529-556) now:
  1. First click: Generates export and stores in session state
  2. Reruns page to show download button
  3. Download button allows user to save the zip file
  4. Export data cleared when selecting new campaign

---

## Dependencies

**Added:** `kaleido` package for Plotly image export.

To install: `pip install kaleido`

---

## Files Changed

| File | Changes |
|------|---------|
| `src/ui/app_api_real.py` | Import export function, replace placeholder button |
| `src/ui/utils/__init__.py` | New - package init |
| `src/ui/utils/export.py` | New - export utility module (380 lines) |

---

## Testing

1. Start the Streamlit app
2. Select any campaign from the browser
3. Click "Export Data" button in the header
4. Wait for "Generating export..." spinner
5. Click "Download Export" when it appears
6. Verify zip contains:
   - `/data/` folder with 9+ CSV files
   - `/charts/` folder with 9 PNG images
   - `README.txt` with summary
   - `campaign_summary.json`

---

## Demo Mode

Export respects demo mode anonymisation:
- Brand names in CSVs are anonymised if `DEMO_MODE=true`
- README notes if running in demo mode

---

## Performance Notes

- Export generation takes 5-15 seconds depending on campaign size
- Chart generation is the slowest part (kaleido renders each chart)
- Data gathering is fast as it uses cached MVs

---

## Future Enhancements

- Add progress bar for export generation
- Add option to export specific tabs only
- Add Excel export option (xlsx with multiple sheets)
- Add PDF report generation

---

*Handover prepared by Claude Code*
