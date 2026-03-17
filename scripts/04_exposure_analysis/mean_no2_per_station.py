from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# PATH SETUP

ROOT = Path(__file__).resolve().parents[2]  # BERLIN/

DATA_CLEAN   = ROOT / "data_clean"
DATA_DERIVED = ROOT / "data" / "derived"
FIG_DIR      = DATA_DERIVED / "figures"

FIG_DIR.mkdir(parents=True, exist_ok=True)

# INPUT FILE
POLLUTION_FILE = DATA_CLEAN / "station_yearly_pollution.csv"

# OUTPUT FILES
OUT_CSV = DATA_DERIVED / "mean_no2_per_station.csv"
OUT_PNG = FIG_DIR / "mean_no2_per_station.png"


# LOAD DATA

df = pd.read_csv(POLLUTION_FILE)


# STANDARDISE POLLUTANT NAMES

pollutant_map = {
    "Feinstaub (PM2,5)": "PM2.5",
    "Feinstaub (PM10)": "PM10",
    "Stickstoffdioxid": "NO2"
}

df["pollutant"] = df["pollutant"].replace(pollutant_map)


# FILTER NO2 ONLY

no2 = df[df["pollutant"] == "NO2"].copy()

if no2.empty:
    raise ValueError("No NO2 data found after standardisation.")

# COMPUTE MEAN NO2 PER STATION (ACROSS YEARS)

mean_no2 = (
    no2
    .groupby(["station_id", "station_name"], as_index=False)["mean_value"]
    .mean()
    .rename(columns={"mean_value": "mean_no2"})
    .sort_values("mean_no2", ascending=False)
)


# SAVE TABLE

mean_no2.to_csv(OUT_CSV, index=False)


# VISUALISATION (WITH WHO GUIDELINE)

WHO_NO2_LIMIT = 10  # µg/m³ (WHO annual guideline)

plt.figure(figsize=(14, 6))
plt.bar(mean_no2["station_name"], mean_no2["mean_no2"], color="#C44E52")

plt.axhline(
    y=WHO_NO2_LIMIT,
    color="black",
    linestyle="--",
    linewidth=2,
    label="WHO annual guideline (10 µg/m³)"
)

plt.xticks(rotation=90)
plt.xlabel("Monitoring Station")
plt.ylabel("Mean NO₂ concentration (µg/m³)")
plt.title("Mean NO₂ Levels by Monitoring Station (Berlin)")
plt.legend()
plt.tight_layout()

plt.savefig(OUT_PNG, dpi=300)
plt.close()


# CONSOLE OUTPUT

print(" Mean NO₂ per station calculated")
print("Saved:")
print(" -", OUT_CSV)
print(" -", OUT_PNG)
print("\nTop 5 stations by NO₂:")
print(mean_no2.head())
