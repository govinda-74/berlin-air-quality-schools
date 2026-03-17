import pandas as pd
from pathlib import Path


# PATH SETUP 
ROOT = Path(__file__).resolve().parents[2] 

INPUT_FILE = ROOT / "data_clean" / "pollution_clean_long.csv"
OUTPUT_FILE = ROOT / "data_clean" / "station_yearly_pollution.csv"


# LOAD CLEAN STANDARDISED DATA
df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

# EXTRACT YEAR
df["year"] = df["date"].dt.year


# YEARLY AGGREGATION (MEAN)
yearly = (
    df
    .groupby(
        ["station_id", "station_name", "pollutant", "year", "unit"],
        as_index=False
    )["value"]
    .mean()
    .rename(columns={"value": "mean_value"})
)


# SORT FOR CLEAR OUTPUT

yearly = yearly.sort_values(
    by=["year", "station_id", "pollutant"]
)


# SAVE RESULT
yearly.to_csv(OUTPUT_FILE, index=False)


# QUICK CHECK

print("Yearly aggregation completed")
print(yearly.head())
print("\nUnique pollutants:")
print(yearly["pollutant"].unique())
