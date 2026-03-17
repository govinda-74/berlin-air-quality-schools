import pandas as pd
from pathlib import Path

# PATH SETUP 
ROOT = Path(__file__).resolve().parents[2]  # BERLIN/
FILE_PATH = ROOT / "data_clean" / "pollution_clean_long.csv"

# LOAD CLEAN MERGED DATA
df = pd.read_csv(FILE_PATH, parse_dates=["date"])

#SHOW UNIQUE POLLUTANT NAMES
print("Unique pollutant names:")
print(df["pollutant"].unique())

# 2. COUNT RECORDS PER POLLUTANT
print("\nPollutant counts:")
print(df["pollutant"].value_counts())

# 3. STANDARDIZE POLLUTANT NAMES 
pollutant_map = {
    "Feinstaub (PM10)": "PM10",
    "Feinstaub (PM2.5)": "PM2.5",
    "Stickstoffdioxid": "NO2",
    "Stickstoffmonoxid": "NO",
    "Stickoxide": "NOx",
    "Ozon": "O3",
    "Kohlenmonoxid": "CO"
}

df["pollutant_clean"] = df["pollutant"].replace(pollutant_map)

print("\nUnique pollutant names after cleaning:")
print(df["pollutant_clean"].unique())
