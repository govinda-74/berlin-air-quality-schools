from pathlib import Path
import geopandas as gpd

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_CLEAN = BASE_DIR / "data_clean"

STATIONS_FILE = DATA_CLEAN / "stations_yearly_pollution.geojson"
SCHOOLS_FILE  = DATA_CLEAN / "berlin_schools_clean.geojson"

OUTPUT_FILE = DATA_CLEAN / "schools_nearest_station_pollution.geojson"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
stations = gpd.read_file(STATIONS_FILE)
schools = gpd.read_file(SCHOOLS_FILE)

# --------------------------------------------------
# CRS CHECK
# --------------------------------------------------
stations = stations.to_crs(25833)
schools = schools.to_crs(25833)

# --------------------------------------------------
# OPTIONAL: focus on key pollutant (recommended)
# --------------------------------------------------
stations_no2 = stations[stations["pollutant"] == "Stickstoffdioxid"].copy()

# --------------------------------------------------
# NEAREST SPATIAL JOIN
# --------------------------------------------------
schools_nearest = gpd.sjoin_nearest(
    schools,
    stations_no2,
    how="left",
    distance_col="distance_m"
)

# --------------------------------------------------
# SAVE
# --------------------------------------------------
schools_nearest.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("✅ Step 3A completed")
# --------------------------------------------------
# SAFE PRINT (NO ASSUMED COLUMN NAMES)
# --------------------------------------------------
print("Sample output columns:")
print(schools_nearest.columns)

print("\nSample rows:")
print(schools_nearest.head())
