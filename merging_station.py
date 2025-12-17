import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

INPUT_DIR = Path("D:/3rd_sem/urban-technology/project/berlin/data/air_quality_data")
OUTPUT_FILE = Path("D:/3rd_sem/urban-technology/project/berlin/data_clean/pollution_clean_long.csv")


# create output directory if needed
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

all_data = []

# --------------------------------------------------
# PROCESS EACH STATION FILE
# --------------------------------------------------
for fp in INPUT_DIR.glob("*.csv"):

    # ---- station info from filename ----s
    # example filename: 010_wedding.csv
    parts = fp.stem.split("_")
    station_id = parts[0]
    station_name = parts[1].title()

    # ---- read raw German CSV ----
    raw = pd.read_csv(fp, sep=";", header=None)

    # ---- extract metadata ----
    pollutants = raw.iloc[1, 1:].values        # row with pollutant names
    units = raw.iloc[2, 1:].values             # row with units

    # ---- extract actual data ----
    df = raw.iloc[4:].copy()
    df.columns = ["date"] + list(pollutants)

    # ---- clean date ----
    df["date"] = pd.to_datetime(
        df["date"],
        dayfirst=True,
        errors="coerce"
    )

    # ---- wide → long format ----
    df_long = df.melt(
        id_vars="date",
        var_name="pollutant",
        value_name="value"
    )

    # ---- add station info ----
    df_long["station_id"] = station_id
    df_long["station_name"] = station_name

    # ---- attach units ----
    unit_map = dict(zip(pollutants, units))
    df_long["unit"] = df_long["pollutant"].map(unit_map)

    # ---- keep ONLY important columns ----
    df_long = df_long[
        ["date", "station_id", "station_name", "pollutant", "value", "unit"]
    ]

    all_data.append(df_long)

# --------------------------------------------------
# MERGE ALL STATIONS
# --------------------------------------------------
pollution_clean = pd.concat(all_data, ignore_index=True)

# optional: remove missing values
pollution_clean = pollution_clean.dropna(subset=["date", "value"])

# save final clean dataset
pollution_clean.to_csv(OUTPUT_FILE, index=False)

print("✅ Pollution data merged successfully")
print(f"📁 Output saved to: {OUTPUT_FILE}")
print(pollution_clean.head())
