import geopandas as gpd

# Load your GeoJSON file from the data folder
gdf = gpd.read_file("data/Schulen.geojson")

print("Loaded entries:", len(gdf))
print("CRS:", gdf.crs)
print("Columns:", gdf.columns)

# Extract latitude and longitude
gdf["lon"] = gdf.geometry.x
gdf["lat"] = gdf.geometry.y

# Drop rows with missing geometry
gdf = gdf[gdf["lat"].notnull() & gdf["lon"].notnull()]

# Remove duplicates
gdf = gdf.drop_duplicates(subset=["lon", "lat"])

# Print summary
print("Cleaned entries:", len(gdf))
print(gdf.head())

# Save clean versions
gdf.to_file("data/clean_data/berlin_schools_clean.geojson", driver="GeoJSON")
gdf.drop(columns=["geometry"]).to_csv("data/clean_data/berlin_schools_clean.csv", index=False)

print("Saved berlin_schools_clean.geojson and berlin_schools_clean.csv")
