# stations_from_blume_api_v2.py
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]   # BERLIN/
OUT = ROOT / "data" / "raw" / "stations"
OUT.mkdir(parents=True, exist_ok=True)

# API CONFIG
URL = "https://luftdaten.berlin.de/api/stations"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}

print("Fetching BLUME stations from API…")

# FETCH DATA
r = requests.get(URL, headers=HEADERS, timeout=60)
r.raise_for_status()
data = r.json()

df = pd.json_normalize(data)

# Use the actual field names you saw: code, name, lat, lng
need = ["code", "name", "lat", "lng", "active", "components"]
need = [c for c in need if c in df.columns]  # keep what's present
df = df[need].copy()

# Standardize column names
df = df.rename(columns={
    "code": "station_id",
    "name": "station_name",
    "lng": "lon"
})

# Ensure types
df["station_id"] = df["station_id"].astype(str)
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df = df.dropna(subset=["lat","lon"])

# Make GeoDataFrame (WGS84 → meters CRS for distance calcs)
gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df["lon"], df["lat"])],
    crs="EPSG:4326"
).to_crs(25833)

# Save
gdf.to_file(OUT / "blume_stations.geojson", driver="GeoJSON")
gdf.drop(columns="geometry").to_csv(OUT / "blume_stations.csv", index=False)

print(f"Saved {len(gdf)} stations to:")
print(f" - {OUT / 'blume_stations.geojson'}")
print(f" - {OUT / 'blume_stations.csv'}")
print("Columns:", list(gdf.columns))
print(gdf.head(3))
