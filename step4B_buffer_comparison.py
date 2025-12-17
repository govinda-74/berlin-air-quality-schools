import geopandas as gpd
import pandas as pd

nearest_fp = "D:/3rd_sem/urban-technology/project/berlin/data_clean/schools_nearest_station_pollution.geojson"
buffer_fp  = "D:/3rd_sem/urban-technology/project/berlin/data_clean/schools_within_200m_polluted_stations.geojson"

nearest = gpd.read_file(nearest_fp)
buffered = gpd.read_file(buffer_fp)

# Identify schools robustly
id_col = next((c for c in ["school_id", "id", "OBJECTID", "fid"] if c in nearest.columns), None)

if id_col and id_col in buffered.columns:
    nearest["within_200m"] = nearest[id_col].isin(buffered[id_col])
else:
    nearest["within_200m"] = nearest.geometry.to_wkt().isin(buffered.geometry.to_wkt())

summary = nearest.groupby("within_200m").agg(
    n_schools=("within_200m", "size"),
    mean_exposure=("mean_value", "mean"),
    median_exposure=("mean_value", "median"),
    mean_distance=("distance_m", "mean"),
    median_distance=("distance_m", "median"),
).reset_index()

OUT = "D:/3rd_sem/urban-technology/project/berlin/data_clean/summary_within200m_vs_not.csv"
summary.to_csv(OUT, index=False)

print("✅ Buffer comparison summary created")
print(summary)
