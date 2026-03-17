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
POLLUTION_FILE = DATA_CLEAN / "station_yearly_pollution.csv"
SCHOOL_COUNT_FILE = DATA_DERIVED / "stations_school_1000m_counts.csv"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
pollution = pd.read_csv(POLLUTION_FILE)
schools   = pd.read_csv(SCHOOL_COUNT_FILE)

# --------------------------------------------------
# STANDARDISE IDS
# --------------------------------------------------
pollution["station_id"] = pollution["station_id"].astype(str).str.replace("mc", "", regex=False).str.zfill(3)
schools["station_id"]   = schools["station_id"].astype(str).str.replace("mc", "", regex=False).str.zfill(3)

# --------------------------------------------------
# STANDARDISE POLLUTANT NAMES
# --------------------------------------------------
pollutant_map = {
    "Feinstaub (PM2,5)": "PM2.5",
    "Feinstaub (PM2.5)": "PM2.5",
    "Feinstaub (PM10)": "PM10",
    "Stickstoffdioxid": "NO2",
}
pollution["pollutant"] = pollution["pollutant"].replace(pollutant_map)

TARGETS = ["NO2", "PM10", "PM2.5"]

# --------------------------------------------------
# USE LATEST YEAR
# --------------------------------------------------
latest_year = pollution["year"].max()
pollution = pollution[pollution["year"] == latest_year].copy()

# --------------------------------------------------
# MERGE SCHOOL COUNTS
# --------------------------------------------------
df = pollution.merge(
    schools[["station_id", "school_count"]],
    on="station_id",
    how="left"
)

df["school_count"] = df["school_count"].fillna(0)

print("Using year:", latest_year)

# --------------------------------------------------
# LOOP THROUGH POLLUTANTS
# --------------------------------------------------
for pol in TARGETS:

    sub = df[df["pollutant"] == pol].copy()

    if sub.empty:
        print(f"No data for {pol}")
        continue

    # ----------------------------------------------
    # Exposure Burden Index
    # ----------------------------------------------
    sub["exposure_index"] = sub["mean_value"] * sub["school_count"]

    sub = sub.sort_values("exposure_index", ascending=False)

    # ----------------------------------------------
    # SAVE TABLE
    # ----------------------------------------------
    OUT_CSV = DATA_DERIVED / f"{pol}_exposure_burden_{latest_year}.csv"
    sub.to_csv(OUT_CSV, index=False)

    # ----------------------------------------------
    # PLOT
    # ----------------------------------------------
    plt.figure(figsize=(14, 6))
    plt.bar(sub["station_name"], sub["exposure_index"])

    plt.xticks(rotation=90)
    plt.xlabel("Monitoring Station")
    plt.ylabel("Exposure Burden Index (Pollution × School Count)")
    plt.title(f"{pol} Exposure Burden Index (Year {latest_year})")

    plt.tight_layout()

    OUT_PNG = FIG_DIR / f"{pol}_exposure_burden_{latest_year}.png"
    plt.savefig(OUT_PNG, dpi=300)
    plt.close()

    print(f"{pol} results saved:")
    print(" -", OUT_CSV)
    print(" -", OUT_PNG)
    print("Top 5 stations:")
    print(sub[["station_name", "exposure_index"]].head())
    print("-" * 40)

print("Exposure burden analysis completed.")