from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATA_CLEAN = ROOT / "data_clean"
DATA_RAW = ROOT / "data" / "raw"
DATA_DERIVED = ROOT / "data" / "derived"
FIG_DIR = DATA_DERIVED / "figures"

DATA_DERIVED.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# FILES
SCHOOLS_FILE = DATA_CLEAN / "berlin_schools_clean.geojson"
STATIONS_FILE = DATA_RAW / "stations" / "blume_stations_active.geojson"
POLLUTION_FILE = DATA_CLEAN / "station_yearly_pollution.csv"

BUFFER_M = 1000

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

schools = gpd.read_file(SCHOOLS_FILE)
stations = gpd.read_file(STATIONS_FILE)
pollution = pd.read_csv(POLLUTION_FILE)

# --------------------------------------------------
# SCHOOL CATEGORY CLASSIFICATION
# --------------------------------------------------

def classify_school(row):

    t = str(row["schulart"])

    if "Grundschule" in t:
        return "Primary"

    elif "Gymnasium" in t or "Sekundarschule" in t or "Gemeinschaftsschule" in t:
        return "Secondary"

    elif "Beruf" in t or "Oberstufe" in t or "Fachschule" in t:
        return "Vocational"

    else:
        return "Special / Other"


schools["school_category"] = schools.apply(classify_school, axis=1)

# --------------------------------------------------
# CRS PROJECTION
# --------------------------------------------------

schools_m = schools.to_crs(25833)
stations_m = stations.to_crs(25833)

# --------------------------------------------------
# BUFFER AROUND STATIONS
# --------------------------------------------------

stations_buffer = stations_m.copy()
stations_buffer["geometry"] = stations_buffer.buffer(BUFFER_M)

# --------------------------------------------------
# SPATIAL JOIN
# --------------------------------------------------

hits = gpd.sjoin(
    schools_m,
    stations_buffer,
    predicate="within",
    how="inner"
)

# --------------------------------------------------
# STANDARDISE POLLUTANT NAMES
# --------------------------------------------------

pollutant_map = {
    "Feinstaub (PM2,5)": "PM2.5",
    "Feinstaub (PM10)": "PM10",
    "Stickstoffdioxid": "NO2"
}

pollution["pollutant"] = pollution["pollutant"].replace(pollutant_map)

# WHO LIMITS
WHO_LIMITS = {
    "PM2.5": 5,
    "PM10": 15,
    "NO2": 10
}

# LATEST YEAR
latest_year = pollution["year"].max()
pollution = pollution[pollution["year"] == latest_year]

# --------------------------------------------------
# MERGE POLLUTION WITH STATIONS
# --------------------------------------------------

# --------------------------------------------------
# STANDARDISE station_id TYPE
# --------------------------------------------------

hits["station_id"] = (
    hits["station_id"]
    .astype(str)
    .str.replace("mc","",regex=False)
    .str.zfill(3)
)

pollution["station_id"] = (
    pollution["station_id"]
    .astype(str)
    .str.replace("mc","",regex=False)
    .str.zfill(3)
)

df = hits.merge(
    pollution,
    on="station_id",
    how="left"
)

# --------------------------------------------------
# KEEP TARGET POLLUTANTS
# --------------------------------------------------

df = df[df["pollutant"].isin(WHO_LIMITS.keys())]

# FLAG WHO EXCEEDANCE
df["who_limit"] = df["pollutant"].map(WHO_LIMITS)
df["exceeds_who"] = df["mean_value"] > df["who_limit"]

# --------------------------------------------------
# EXPOSURE SUMMARY
# --------------------------------------------------

summary = (
    df.groupby(["pollutant","school_category","exceeds_who"])
    .size()
    .reset_index(name="schools_exposed")
)

OUT_CSV = DATA_DERIVED / "school_category_pollution_exposure.csv"
summary.to_csv(OUT_CSV, index=False)

print("Saved summary:", OUT_CSV)

# --------------------------------------------------
# 3-PANEL VISUALISATION
# --------------------------------------------------

pollutants = ["PM2.5", "PM10", "NO2"]

fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

for ax, pol in zip(axes, pollutants):

    sub = df[df["pollutant"] == pol].copy()

    plot_data = (
        sub.groupby("school_category")
        .size()
        .reset_index(name="schools")
        .sort_values("schools", ascending=False)
    )

    ax.bar(plot_data["school_category"], plot_data["schools"])

    ax.set_title(f"{pol}", fontsize=13, weight="bold")
    ax.set_xlabel("School Category")
    ax.tick_params(axis="x", rotation=30)

axes[0].set_ylabel("Number of Schools Exposed")

fig.suptitle(
    f"School Category Exposure by Pollutant (within {BUFFER_M/1000:.0f} km, {latest_year})",
    fontsize=15,
    weight="bold"
)

plt.tight_layout(rect=[0, 0, 1, 0.95])

OUT_PANEL = FIG_DIR / f"school_category_exposure_panel_{latest_year}.png"
plt.savefig(OUT_PANEL, dpi=300)
plt.close()

print("Saved 3-panel figure:", OUT_PANEL)