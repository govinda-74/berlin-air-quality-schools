# filter_active_stations.py
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

# INPUT / OUTPUT PATHS
IN_CSV = Path("data/blume_stations.csv")   # change if your file name/path differs
OUT_DIR = Path("data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Load ---
df = pd.read_csv(IN_CSV)

# --- Normalize 'active' to boolean (handles True/False or 'true'/'false' strings) ---
def to_bool(x):
    if isinstance(x, bool):
        return x
    if pd.isna(x):
        return False
    return str(x).strip().lower() in ("true", "1", "yes", "y", "t")

df["active"] = df["active"].apply(to_bool)

# --- Keep only active + valid coords ---
for c in ("lat", "lon"):
    df[c] = pd.to_numeric(df[c], errors="coerce")

active = df[df["active"]].dropna(subset=["lat", "lon"]).copy()

# --- Save CSV ---
csv_path = OUT_DIR / "blume_stations_active.csv"
active.to_csv(csv_path, index=False)

# --- Save GeoJSON (WGS84) ---
gdf = gpd.GeoDataFrame(
    active,
    geometry=[Point(xy) for xy in zip(active["lon"], active["lat"])],
    crs="EPSG:4326"
)
geojson_path = OUT_DIR / "blume_stations_active.geojson"
gdf.to_file(geojson_path, driver="GeoJSON")

print(f"Active stations: {len(gdf)}")
print("Wrote:", csv_path)
print("Wrote:", geojson_path)