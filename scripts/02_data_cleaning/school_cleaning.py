# school_cleaning.py

import geopandas as gpd
from pathlib import Path

# --------------------------------------------------
# PATH SETUP (SAFE & PORTABLE)
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]  # BERLIN/

INPUT_FILE = ROOT / "data" / "raw" / "schools" / "Schulen.geojson"
OUTPUT_DIR = ROOT / "data_clean"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# LOAD RAW SCHOOL DATA
# --------------------------------------------------
gdf = gpd.read_file(INPUT_FILE)

print("Loaded entries:", len(gdf))
print("CRS:", gdf.crs)
print("Columns:", gdf.columns)

# --------------------------------------------------
# EXTRACT LATITUDE & LONGITUDE FROM GEOMETRY
# --------------------------------------------------
gdf["lon"] = gdf.geometry.x
gdf["lat"] = gdf.geometry.y

# --------------------------------------------------
# DROP ROWS WITH MISSING GEOMETRY
# --------------------------------------------------
gdf = gdf[gdf["lat"].notnull() & gdf["lon"].notnull()]

# --------------------------------------------------
# REMOVE DUPLICATE LOCATIONS
# --------------------------------------------------
gdf = gdf.drop_duplicates(subset=["lon", "lat"])

print("Cleaned entries:", len(gdf))
print(gdf.head())

# --------------------------------------------------
# SAVE CLEAN DATASETS
# --------------------------------------------------
gdf.to_file(OUTPUT_DIR / "berlin_schools_clean.geojson", driver="GeoJSON")
gdf.drop(columns=["geometry"]).to_csv(
    OUTPUT_DIR / "berlin_schools_clean.csv",
    index=False
)

print("Saved berlin_schools_clean.geojson and berlin_schools_clean.csv")
