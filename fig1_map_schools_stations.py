import geopandas as gpd
import matplotlib.pyplot as plt

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
stations = gpd.read_file(
    "D:/3rd_sem/urban-technology/project/berlin/data_clean/stations_yearly_pollution.geojson"
)
schools = gpd.read_file(
    "D:/3rd_sem/urban-technology/project/berlin/data_clean/schools_nearest_station_pollution.geojson"
)

# CRS
stations = stations.to_crs(25833)
schools = schools.to_crs(25833)

# Focus on NO2 (recommended)
stations_no2 = stations[stations["pollutant"] == "Stickstoffdioxid"]

# --------------------------------------------------
# PLOT
# --------------------------------------------------
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

stations_no2.plot(
    ax=ax,
    column="mean_value",
    cmap="Reds",
    legend=True,
    legend_kwds={"label": "Annual mean NO₂ (µg/m³)"},
    markersize=80,
    edgecolor="black"
)

schools.plot(
    ax=ax,
    color="blue",
    markersize=10,
    alpha=0.6,
    label="Schools"
)

ax.set_title("Berlin Schools and Air-Quality Monitoring Stations (NO₂)", fontsize=14)
ax.axis("off")
ax.legend()

plt.tight_layout()
plt.show()
