import geopandas as gpd
import matplotlib.pyplot as plt

schools = gpd.read_file(
    "D:/3rd_sem/urban-technology/project/berlin/data_clean/schools_nearest_station_pollution.geojson"
)

plt.figure(figsize=(8, 5))
plt.hist(
    schools["distance_m"],
    bins=30
)

plt.xlabel("Distance to nearest station (meters)")
plt.ylabel("Number of schools")
plt.title("Distribution of School Distance to Nearest Pollution Monitoring Station")

plt.tight_layout()
plt.show()
