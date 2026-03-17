# stations_vs_schools_1000m.py
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import geopandas as gpd
import folium

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
BUFFER_M = 1000  # 1 km buffer

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]  # BERLIN/

DATA_RAW     = ROOT / "data" / "raw"
DATA_CLEAN   = ROOT / "data_clean"
DATA_DERIVED = ROOT / "data" / "derived"
DATA_DERIVED.mkdir(parents=True, exist_ok=True)

SCHOOLS_FP  = DATA_CLEAN / "berlin_schools_clean.geojson"
STATIONS_FP = DATA_RAW / "stations" / "blume_stations_active.geojson"

OUT_CSV     = DATA_DERIVED / "stations_school_1000m_counts.csv"
OUT_GEOJSON = DATA_DERIVED / "stations_school_1000m.geojson"
OUT_HTML    = DATA_DERIVED / "stations_school_1000m_map.html"

# LOAD DATA

schools  = gpd.read_file(SCHOOLS_FP)
stations = gpd.read_file(STATIONS_FP)


# PICK IDENTIFIERS

def pick(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    return None

school_id = pick(schools.columns, ["OBJECTID", "school_id", "bsn", "id"])
school_nm = pick(schools.columns, ["schulname", "school_name", "name", "Schulname"])

st_id = pick(stations.columns, ["station_id", "code", "id"])
st_nm = pick(stations.columns, ["station_name", "name"])


# PROJECT TO METERS

schools_m  = schools.to_crs(25833)
stations_m = stations.to_crs(25833)


# BUILD 1 km BUFFERS AROUND STATIONS

stations_buf = stations_m[[st_id, st_nm, "geometry"]].copy()
stations_buf["geometry"] = stations_buf.buffer(BUFFER_M)


# SPATIAL JOIN: SCHOOLS WITHIN STATION BUFFERS

hits = gpd.sjoin(
    schools_m[[school_id, school_nm, "geometry"]],
    stations_buf,
    predicate="within",
    how="left"
)


# AGGREGATE SCHOOL COUNTS

counts = (
    hits.dropna(subset=[st_id])
        .groupby(st_id)
        .agg(
            school_count=(school_id, "size"),
            school_ids=(school_id, lambda x: sorted(set(map(str, x))))
        )
        .reset_index()
)

stations_with = stations_m.merge(counts, on=st_id, how="left")
stations_with["school_count"] = stations_with["school_count"].fillna(0).astype(int)
stations_with["school_ids"] = stations_with["school_ids"].apply(
    lambda v: v if isinstance(v, list) else []
)


# VISUALISATION: NUMBER OF SCHOOLS PER STATION (1 km)


plot_df = (
    stations_with[[st_nm, "school_count"]]
    .sort_values("school_count", ascending=False)
)

plt.figure(figsize=(14, 6))
plt.bar(plot_df[st_nm], plot_df["school_count"])
plt.xticks(rotation=90)
plt.xlabel("Monitoring Station")
plt.ylabel("Number of Schools within 1 km")
plt.title("Number of Schools within 1 km of Each Monitoring Station (Berlin)")
plt.tight_layout()

FIG_PATH = DATA_DERIVED / "schools_per_station_1000m.png"
plt.savefig(FIG_PATH, dpi=300)
plt.close()

print("📊 Bar chart saved to:", FIG_PATH)




# SAVE OUTPUTS

stations_with.drop(columns="geometry").to_csv(OUT_CSV, index=False)

stations_geo = stations_with.to_crs(4326)
stations_geo.to_file(OUT_GEOJSON, driver="GeoJSON")

print(f"Stations with ≥1 school in {BUFFER_M} m:",
      (stations_geo["school_count"] > 0).sum(), "/", len(stations_geo))


# INTERACTIVE MAP

def color_for(n):
    if n == 0: return "#9e9e9e"
    if n <= 2: return "#2e7d32"
    return "#c62828"

center = stations_geo.geometry.unary_union.centroid
m = folium.Map(location=[center.y, center.x], zoom_start=11, tiles="CartoDB Positron")

# Schools
sch_w = schools_m.to_crs(4326)
for _, r in sch_w.iterrows():
    folium.CircleMarker(
        location=[r.geometry.y, r.geometry.x],
        radius=3, color="black",
        fill=True, fill_opacity=0.8
    ).add_to(m)

# Stations with 1 km circles
for _, r in stations_geo.iterrows():
    folium.Circle(
        location=[r.geometry.y, r.geometry.x],
        radius=BUFFER_M,
        color=color_for(int(r["school_count"])),
        fill=True, fill_opacity=0.15
    ).add_to(m)

m.save(str(OUT_HTML))
print("Map saved:", OUT_HTML)
