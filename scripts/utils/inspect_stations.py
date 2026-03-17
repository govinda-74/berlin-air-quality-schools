import geopandas as gpd

stations = gpd.read_file(
    "D:/3rd_sem/urban-technology/project/berlin/data/blume_stations_active.geojson"
)

print("Columns in station file:")
print(stations.columns)

print("\nFirst 5 rows:")
print(stations.head())
