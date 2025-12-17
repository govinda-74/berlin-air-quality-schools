import pandas as pd

# --------------------------------------------------
# LOAD CLEAN STANDARDISED DATA
# --------------------------------------------------
INPUT_FILE = "D:/3rd_sem/urban-technology/project/berlin/data_clean/pollution_clean_long.csv"
OUTPUT_FILE = "D:/3rd_sem/urban-technology/project/berlin/data_clean/station_yearly_pollution.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

# --------------------------------------------------
# EXTRACT YEAR
# --------------------------------------------------
df["year"] = df["date"].dt.year

# --------------------------------------------------
# YEARLY AGGREGATION (MEAN)
# --------------------------------------------------
yearly = (
    df
    .groupby(
        ["station_id", "station_name", "pollutant", "year", "unit"],
        as_index=False
    )["value"]
    .mean()
    .rename(columns={"value": "mean_value"})
)

# --------------------------------------------------
# SORT (NEAT OUTPUT)
# --------------------------------------------------
yearly = yearly.sort_values(
    by=["year", "station_id", "pollutant"]
)

# --------------------------------------------------
# SAVE RESULT
# --------------------------------------------------
yearly.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# QUICK CHECK
# --------------------------------------------------
print("✅ Yearly aggregation completed")
print(yearly.head())
print("\nUnique pollutants:")
print(yearly["pollutant"].unique())
