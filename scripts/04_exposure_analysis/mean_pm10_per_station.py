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
OUT_CSV = DATA_DERIVED / "mean_pm10_per_station.csv"
OUT_PNG = FIG_DIR / "mean_pm10_per_station.png"


# LOAD DATA

df = pd.read_csv(POLLUTION_FILE)


# STANDARDISE POLLUTANT NAMES

pollutant_map = {
    "Feinstaub (PM2,5)": "PM2.5",
    "Feinstaub (PM10)": "PM10",
    "Stickstoffdioxid": "NO2"
}

df["pollutant"] = df["pollutant"].replace(pollutant_map)


# FILTER PM10 ONLY

pm10 = df[df["pollutant"] == "PM10"].copy()

if pm10.empty:
    raise ValueError("No PM10 data found after standardisation.")


# COMPUTE MEAN PM10 PER STATION (ACROSS YEARS)

mean_pm10 = (
    pm10
    .groupby(["station_id", "station_name"], as_index=False)["mean_value"]
    .mean()
    .rename(columns={"mean_value": "mean_pm10"})
    .sort_values("mean_pm10", ascending=False)
)


# SAVE TABLE

mean_pm10.to_csv(OUT_CSV, index=False)


# VISUALISATION (WITH WHO GUIDELINE)

WHO_PM10_LIMIT = 15  # µg/m³ (WHO annual guideline)

plt.figure(figsize=(14, 6))
plt.bar(mean_pm10["station_name"], mean_pm10["mean_pm10"], color="#55A868")

plt.axhline(
    y=WHO_PM10_LIMIT,
    color="red",
    linestyle="--",
    linewidth=2,
    label="WHO annual guideline (15 µg/m³)"
)

plt.xticks(rotation=90)
plt.xlabel("Monitoring Station")
plt.ylabel("Mean PM10 concentration (µg/m³)")
plt.title("Mean PM10 Levels by Monitoring Station (Berlin)")
plt.legend()
plt.tight_layout()

plt.savefig(OUT_PNG, dpi=300)
plt.close()


# CONSOLE OUTPUT

print("Mean PM10 per station calculated")
print("Saved:")
print(" -", OUT_CSV)
print(" -", OUT_PNG)
print("\nTop 5 stations by PM10:")
print(mean_pm10.head())
