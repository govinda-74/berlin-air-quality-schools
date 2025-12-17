import geopandas as gpd
import matplotlib.pyplot as plt

nearest = gpd.read_file(
    "D:/3rd_sem/urban-technology/project/berlin/data_clean/schools_nearest_station_pollution.geojson"
)
buffered = gpd.read_file(
    "D:/3rd_sem/urban-technology/project/berlin/data_clean/schools_within_200m_polluted_stations.geojson"
)

# Identify schools within 200 m
nearest["within_200m"] = nearest.geometry.to_wkt().isin(
    buffered.geometry.to_wkt()
)

inside = nearest[nearest["within_200m"]]["mean_value"]
outside = nearest[~nearest["within_200m"]]["mean_value"]

plt.figure(figsize=(6, 5))
plt.boxplot(
    [inside, outside],
    labels=["Within 200 m", "Beyond 200 m"]
)

plt.ylabel("Annual mean NO₂ (µg/m³)")
plt.title("School NO₂ Exposure by Proximity to Monitoring Stations")

plt.tight_layout()
plt.show()
