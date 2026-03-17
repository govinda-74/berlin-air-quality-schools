from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --------------------------------------------------
# ROOT DETECTION
# --------------------------------------------------
THIS_FILE = Path(__file__).resolve()
ROOT = None
for p in THIS_FILE.parents:
    if (p / "data_clean").exists():
        ROOT = p
        break

if ROOT is None:
    raise FileNotFoundError("Project root not found.")

DATA_CLEAN   = ROOT / "data_clean"
DATA_DERIVED = ROOT / "data" / "derived"
FIG_DIR      = DATA_DERIVED / "figures"

DATA_DERIVED.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# INPUT FILES
# --------------------------------------------------
POLLUTION_FILE = DATA_CLEAN / "pollution_clean_long.csv"
SCHOOL_COUNT_FILE = DATA_DERIVED / "stations_school_1000m_counts.csv"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
pollution = pd.read_csv(POLLUTION_FILE, parse_dates=["date"])
schools = pd.read_csv(SCHOOL_COUNT_FILE)

# --------------------------------------------------
# STANDARDISE STATION IDs
# --------------------------------------------------
pollution["station_id"] = (
    pollution["station_id"]
    .astype(str)
    .str.replace("mc", "", regex=False)
    .str.zfill(3)
)

schools["station_id"] = (
    schools["station_id"]
    .astype(str)
    .str.replace("mc", "", regex=False)
    .str.zfill(3)
)

# --------------------------------------------------
# STANDARDISE POLLUTANT NAMES
# --------------------------------------------------
pollutant_map = {
    "Feinstaub (PM2,5)": "PM2.5",
    "Feinstaub (PM2.5)": "PM2.5",
    "Feinstaub (PM10)": "PM10",
    "Stickstoffdioxid": "NO2",
    "Ozon": "O3"
}
pollution["pollutant"] = pollution["pollutant"].replace(pollutant_map)

TARGETS = ["NO2", "PM10", "PM2.5", "O3"]
pollution = pollution[pollution["pollutant"].isin(TARGETS)].copy()

# --------------------------------------------------
# CLEAN VALUE COLUMN
# --------------------------------------------------
pollution["value"] = pd.to_numeric(pollution["value"], errors="coerce")
pollution = pollution.dropna(subset=["date", "value"])

# --------------------------------------------------
# DEFINE SEASONS
# Winter = DJF
# Summer = JJA
# Dec belongs to next winter year
# --------------------------------------------------
pollution["month"] = pollution["date"].dt.month
pollution["year"] = pollution["date"].dt.year

def assign_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return None

pollution["season"] = pollution["month"].apply(assign_season)
pollution = pollution[pollution["season"].notna()].copy()

pollution["season_year"] = pollution["year"]
pollution.loc[pollution["month"] == 12, "season_year"] = pollution["year"] + 1

# --------------------------------------------------
# KEEP ONLY COMPLETE SEASONS
# Require all 3 months for station-pollutant-season-year
# --------------------------------------------------
month_count = (
    pollution.groupby(["station_id", "pollutant", "season", "season_year"])["month"]
    .nunique()
    .reset_index(name="n_months")
)

complete = month_count[month_count["n_months"] == 3].copy()

pollution = pollution.merge(
    complete[["station_id", "pollutant", "season", "season_year"]],
    on=["station_id", "pollutant", "season", "season_year"],
    how="inner"
)

# --------------------------------------------------
# COMPUTE SEASONAL MEAN PER STATION
# --------------------------------------------------
seasonal = (
    pollution.groupby(
        ["station_id", "station_name", "pollutant", "season", "season_year"],
        as_index=False
    )["value"]
    .mean()
    .rename(columns={"value": "seasonal_mean"})
)

# --------------------------------------------------
# USE MOST RECENT COMPLETE WINTER AND SUMMER
# --------------------------------------------------
latest_winter = seasonal.loc[seasonal["season"] == "Winter", "season_year"].max()
latest_summer = seasonal.loc[seasonal["season"] == "Summer", "season_year"].max()

print("Latest complete Winter season year:", latest_winter)
print("Latest complete Summer season year:", latest_summer)

seasonal_compare = seasonal[
    ((seasonal["season"] == "Winter") & (seasonal["season_year"] == latest_winter)) |
    ((seasonal["season"] == "Summer") & (seasonal["season_year"] == latest_summer))
].copy()

# --------------------------------------------------
# MERGE SCHOOL COUNTS
# --------------------------------------------------
seasonal_compare = seasonal_compare.merge(
    schools[["station_id", "school_count"]],
    on="station_id",
    how="left"
)

seasonal_compare["school_count"] = seasonal_compare["school_count"].fillna(0)

# --------------------------------------------------
# EXPOSURE BURDEN INDEX
# --------------------------------------------------
seasonal_compare["exposure_burden"] = (
    seasonal_compare["seasonal_mean"] * seasonal_compare["school_count"]
)

# --------------------------------------------------
# SAVE SUMMARY TABLE
# --------------------------------------------------
OUT_CSV = DATA_DERIVED / "seasonal_school_exposure_summary_with_o3.csv"
seasonal_compare.to_csv(OUT_CSV, index=False)
print("Saved summary table:", OUT_CSV)

# --------------------------------------------------
# 4-PANEL FIGURE: WINTER VS SUMMER POLLUTION
# --------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharey=False)
axes = axes.flatten()

for ax, pol in zip(axes, TARGETS):
    sub = seasonal_compare[seasonal_compare["pollutant"] == pol].copy()

    if sub.empty:
        ax.set_visible(False)
        continue

    plot_df = (
        sub.groupby("season", as_index=False)["seasonal_mean"]
        .mean()
        .set_index("season")
        .reindex(["Winter", "Summer"])
        .reset_index()
    )

    ax.bar(plot_df["season"], plot_df["seasonal_mean"])
    ax.set_title(pol, fontsize=13, weight="bold")
    ax.set_ylabel("Mean Seasonal Concentration (µg/m³)")

fig.suptitle(
    "Winter vs Summer Mean Pollution Levels Near Schools",
    fontsize=16,
    weight="bold"
)

plt.tight_layout(rect=[0, 0, 1, 0.95])
OUT_POLLUTION = FIG_DIR / "seasonal_pollution_comparison_panel_with_o3.png"
plt.savefig(OUT_POLLUTION, dpi=300)
plt.close()
print("Saved seasonal pollution figure:", OUT_POLLUTION)

# --------------------------------------------------
# 4-PANEL FIGURE: WINTER VS SUMMER EXPOSURE BURDEN
# --------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharey=False)
axes = axes.flatten()

for ax, pol in zip(axes, TARGETS):
    sub = seasonal_compare[seasonal_compare["pollutant"] == pol].copy()

    if sub.empty:
        ax.set_visible(False)
        continue

    plot_df = (
        sub.groupby("season", as_index=False)["exposure_burden"]
        .mean()
        .set_index("season")
        .reindex(["Winter", "Summer"])
        .reset_index()
    )

    ax.bar(plot_df["season"], plot_df["exposure_burden"])
    ax.set_title(pol, fontsize=13, weight="bold")
    ax.set_ylabel("Mean Exposure Burden")

fig.suptitle(
    "Winter vs Summer Exposure Burden Near Schools",
    fontsize=16,
    weight="bold"
)

plt.tight_layout(rect=[0, 0, 1, 0.95])
OUT_BURDEN = FIG_DIR / "seasonal_exposure_burden_comparison_panel_with_o3.png"
plt.savefig(OUT_BURDEN, dpi=300)
plt.close()
print("Saved seasonal exposure burden figure:", OUT_BURDEN)