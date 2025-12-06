import geopandas as gpd

# Load your file (adjust name if needed)
gdf = gpd.read_file("D:\\3rd_sem\\urban-technology\\project\\berlin\\data\\Schulen.geojson")

print("Loaded entries:", len(gdf))
print("Columns:", gdf.columns.tolist())
print("\nCRS:", gdf.crs)
gdf.head()
