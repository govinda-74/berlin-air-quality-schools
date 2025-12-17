import geopandas as gpd
import pandas as pd

FILE = "D:/3rd_sem/urban-technology/project/berlin/data_clean/schools_nearest_station_pollution.geojson"

gdf = gpd.read_file(FILE)

# Auto-detect school name column (robust)
school_name_col = next(
    (c for c in ["school_name", "name", "schule", "bezeichnung", "Schulname"] if c in gdf.columns),
    None
)

if school_name_col is None:
    print("⚠ No school name column found, using index as identifier.")
    gdf["school_name"] = gdf.index.astype(str)
    school_name_col = "school_name"

# Build report table
report = gdf[
    [school_name_col, "station_id", "mean_value", "distance_m"]
].rename(columns={school_name_col: "school_name"})

# Sort by exposure (highest first)
report = report.sort_values("mean_value", ascending=False)

# Save
OUT = "D:/3rd_sem/urban-technology/project/berlin/data_clean/school_exposure_rankings.csv"
report.to_csv(OUT, index=False)

print("✅ Exposure ranking table created")
print(report.head(10))
