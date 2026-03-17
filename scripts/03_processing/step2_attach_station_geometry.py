from pathlib import Path
import pandas as pd
import geopandas as gpd

# PATH SETUP
ROOT = Path(__file__).resolve().parents[2]  

DATA_CLEAN = ROOT / "data_clean"
DATA_RAW   = ROOT / "data" / "raw"

POLLUTION_FILE = DATA_CLEAN / "station_yearly_pollution.csv"
STATIONS_FILE  = DATA_RAW / "stations" / "blume_stations_active.geojson"

OUTPUT_FILE = DATA_CLEAN / "stations_yearly_pollution.geojson"

# LOAD DATA
pollution = pd.read_csv(POLLUTION_FILE)
stations = gpd.read_file(STATIONS_FILE)

# STANDARDISE station_id IN STATION FILE
# mc010 -> 010
stations["station_id"] = (
    stations["station_id"]
    .astype(str)
    .str.replace("mc", "", regex=False)
    .str.zfill(3)
)

# ENSURE station_id IN POLLUTION FILE
pollution["station_id"] = (
    pollution["station_id"]
    .astype(str)
    .str.zfill(3)
)

# CRS FIX (Berlin standard)
if stations.crs is None or stations.crs.to_epsg() != 25833:
    stations = stations.to_crs(25833)

# FILTER ONLY ACTIVE STATIONS 
stations = stations[stations["active"] == True].copy()

# MERGE

stations_pollution = stations.merge(
    pollution,
    on="station_id",
    how="inner"
)

# SANITY CHECK
print("Merged rows:", len(stations_pollution))
print("Unique stations:", stations_pollution["station_id"].nunique())
print("Unique pollutants:", stations_pollution["pollutant"].unique())

# SAVE OUTPUT
stations_pollution.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("Step 2 completed successfully")
print("Output saved to:", OUTPUT_FILE)
