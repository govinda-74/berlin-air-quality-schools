from pathlib import Path
import geopandas as gpd

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_CLEAN = BASE_DIR / "data_clean"

STATIONS_FILE = DATA_CLEAN / "stations_yearly_pollution.geojson"
SCHOOLS_FILE  = DATA_CLEAN / "berlin_schools_clean.geojson"

OUTPUT_FILE = DATA_CLEAN / "schools_within_200m_polluted_stations.geojson"

BUFFER_DISTANCE = 200  # meters

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
stations = gpd.read_file(STATIONS_FILE)
schools = gpd.read_file(SCHOOLS_FILE)

# --------------------------------------------------
# CRS
# --------------------------------------------------
stations = stations.to_crs(25833)
schools = schools.to_crs(25833)

# --------------------------------------------------
# SELECT POLLUTANT (recommended: NO2)
# --------------------------------------------------
stations_no2 = stations[stations["pollutant"] == "Stickstoffdioxid"].copy()

# --------------------------------------------------
# CREATE BUFFERS
# --------------------------------------------------
stations_no2["geometry"] = stations_no2.geometry.buffer(BUFFER_DISTANCE)

# --------------------------------------------------
# SPATIAL JOIN (INTERSECTS)
# --------------------------------------------------
schools_buffer = gpd.sjoin(
    schools,
    stations_no2,
    how="inner",
    predicate="intersects"
)

# --------------------------------------------------
# SAVE
# --------------------------------------------------
schools_buffer.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("✅ Step 3B completed")
print("📁 Output:", OUTPUT_FILE)
print("Schools within 200 m:", schools_buffer.shape[0])
