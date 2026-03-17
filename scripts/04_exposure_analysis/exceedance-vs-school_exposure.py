from pathlib import Path
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ROOT DETECTION

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
FIG_DIR.mkdir(parents=True, exist_ok=True)


# INPUT FILES
POLLUTION_FILE = DATA_CLEAN / "station_yearly_pollution.csv"
SCHOOL_COUNT_FILE = DATA_DERIVED / "stations_school_1000m_counts.csv"

# LOAD DATA
pollution = pd.read_csv(POLLUTION_FILE)
schools   = pd.read_csv(SCHOOL_COUNT_FILE)


# STANDARDISE IDS

pollution["station_id"] = pollution["station_id"].astype(str).str.replace("mc", "", regex=False).str.zfill(3)
schools["station_id"]   = schools["station_id"].astype(str).str.replace("mc", "", regex=False).str.zfill(3)


# STANDARDISE POLLUTANT NAMES

pollutant_map = {
    "Feinstaub (PM2,5)": "PM2.5",
    "Feinstaub (PM2.5)": "PM2.5",
    "Feinstaub (PM10)": "PM10",
    "Stickstoffdioxid": "NO2",
}
pollution["pollutant"] = pollution["pollutant"].replace(pollutant_map)


# WHO GUIDELINES (Annual)

WHO_LIMITS = {
    "PM2.5": 5,
    "PM10": 15,
    "NO2": 10
}

TARGETS = ["NO2", "PM10", "PM2.5"]


# USE LATEST YEAR

latest_year = pollution["year"].max()
pollution = pollution[pollution["year"] == latest_year].copy()


# MERGE SCHOOL COUNTS
df = pollution.merge(
    schools[["station_id", "school_count"]],
    on="station_id",
    how="left"
)
df["school_count"] = df["school_count"].fillna(0)

print("Using year:", latest_year)


# CREATE ONE PLOT PER POLLUTANT

for pol in TARGETS:

    sub = df[df["pollutant"] == pol].copy()

    if sub.empty:
        print(f"No data for {pol}")
        continue

    # Determine exceedance
    limit = WHO_LIMITS[pol]
    sub["exceed"] = sub["mean_value"] > limit

    plt.figure(figsize=(12, 8))

    # Below WHO
    below = sub[sub["exceed"] == False]
    plt.scatter(
        below["school_count"],
        below["mean_value"],
        alpha=0.7,
        label="Below WHO"
    )

    # Above WHO
    above = sub[sub["exceed"] == True]
    plt.scatter(
        above["school_count"],
        above["mean_value"],
        alpha=0.9,
        label="Above WHO"
    )

    # WHO limit line
    plt.axhline(
        limit,
        linestyle="--",
        linewidth=2,
        label=f"WHO Annual Limit ({limit} µg/m³)"
    )

    plt.xlabel("Number of Schools within buffer")
    plt.ylabel("Annual Mean Concentration (µg/m³)")
    plt.title(f"{pol}: Pollution vs School Exposure (Year {latest_year})")

    plt.legend()

    import numpy as np

    # -----------------------------
    # Regression Line
    # -----------------------------

    # X and Y values
    x = sub["school_count"].values
    y = sub["mean_value"].values

    # Fit linear regression (1st degree polynomial)
    slope, intercept = np.polyfit(x, y, 1)

    # Create regression line values
    x_line = np.linspace(min(x), max(x), 100)
    y_line = slope * x_line + intercept

    # Plot regression line
    plt.plot(
        x_line,
        y_line,
        color="black",
        linewidth=2,
        label=f"Regression line (slope = {slope:.2f})"
    )

    # Optional: Print regression info
    print(f"{pol} regression slope:", slope)
    print(f"{pol} intercept:", intercept)

    plt.tight_layout()

    OUT_PNG = FIG_DIR / f"{pol}_vs_school_exposure_WHO_{latest_year}.png"
    plt.savefig(OUT_PNG, dpi=300)
    plt.close()

    print(f"Saved: {OUT_PNG}")

print("All plots generated successfully.")