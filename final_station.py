import pandas as pd

# --------------------------------------------------
# LOAD CLEAN MERGED DATA
# --------------------------------------------------
FILE_PATH = "D:/3rd_sem/urban-technology/project/berlin/data_clean/pollution_clean_long.csv"

df = pd.read_csv(FILE_PATH, parse_dates=["date"])

# --------------------------------------------------
# 1. SHOW UNIQUE POLLUTANT NAMES
# --------------------------------------------------
print("Unique pollutant names:")
print(df["pollutant"].unique())

# --------------------------------------------------
# 2. COUNT RECORDS PER POLLUTANT
# --------------------------------------------------
print("\nPollutant counts:")
print(df["pollutant"].value_counts())

# --------------------------------------------------
# 3. (OPTIONAL) STANDARDIZE POLLUTANT NAMES
# --------------------------------------------------
pollutant_map = {
    "Feinstaub (PM10)": "PM10",
    "Feinstaub (PM2.5)": "PM2.5",
    "Stickstoffdioxid": "NO2"
}

df["pollutant_clean"] = df["pollutant"].replace(pollutant_map)

print("\nUnique pollutant names after cleaning:")
print(df["pollutant_clean"].unique())
