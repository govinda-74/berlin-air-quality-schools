# schools_vs_stations_200m.py
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster

DATA = Path("data")
SCHOOLS_FP  = DATA / "school_location/berlin_schools_clean.geojson"
STATIONS_FP = DATA / "blume_stations_active.geojson"
OUT_CSV     = DATA / "schools_station_200m_counts.csv"
OUT_GEOJSON = DATA / "schools_station_200m.geojson"
OUT_HTML    = DATA / "schools_station_200m_map.html"

# 1) Load
schools  = gpd.read_file(SCHOOLS_FP)
stations = gpd.read_file(STATIONS_FP)

# 2) Pick sensible identifiers (handle column name variations)
def pick(cols, candidates):
    for c in candidates:
        if c in cols: return c
    return None

school_id  = pick(schools.columns, ["OBJECTID","school_id","bsn","id"])
school_nm  = pick(schools.columns, ["schulname","name","school_name","schule","School","Schulname"])
if school_id is None:
    schools = schools.reset_index().rename(columns={"index":"school_id"})
    school_id = "school_id"
if school_nm is None:
    schools["schulname"] = schools[school_id].astype(str)
    school_nm = "schulname"

st_id  = pick(stations.columns, ["station_id","code","id"])
st_nm  = pick(stations.columns, ["station_name","name"])
if st_id is None:
    stations = stations.reset_index().rename(columns={"index":"station_id"})
    st_id = "station_id"
if st_nm is None:
    stations["station_name"] = stations[st_id].astype(str)
    st_nm = "station_name"

# 3) Project to meters (ETRS89 / UTM zone 33N) for accurate 200 m buffers
schools_m  = schools.to_crs(25833)
stations_m = stations.to_crs(25833)

# 4) Build 200 m buffers around schools and spatial join
schools_buf = schools_m[[school_id, school_nm, "geometry"]].copy()
schools_buf["geometry"] = schools_buf.buffer(200)  # 200 meters

hits = gpd.sjoin(
    stations_m[[st_id, st_nm, "geometry"]],
    schools_buf,
    predicate="within",
    how="left"
)

# 5) Aggregate counts + list of station ids per school
counts = (
    hits.dropna(subset=[school_id])
        .groupby(school_id)
        .agg(
            station_count=(st_id, "size"),
            station_ids=(st_id, lambda x: sorted(set(map(str, x))))
        )
        .reset_index()
)

# 6) Attach to original schools; fill 0 if none
schools_with = schools_m.merge(counts, on=school_id, how="left")
schools_with["station_count"] = schools_with["station_count"].fillna(0).astype(int)
schools_with["station_ids"]   = schools_with["station_ids"].apply(lambda v: v if isinstance(v, list) else [])

# 7) Save outputs
# 7a) CSV (attributes only)
cols_for_csv = [school_id, school_nm, "station_count", "station_ids"]
schools_with.to_crs(4326)  # (ensure geometry CRS for completeness, not needed for CSV)
pd.DataFrame(schools_with[cols_for_csv]).to_csv(OUT_CSV, index=False)

# 7b) GeoJSON with attributes for mapping (keep points, not buffers)
schools_geo = schools_with.to_crs(4326)
schools_geo.to_file(OUT_GEOJSON, driver="GeoJSON")

print(f"Saved:\n - {OUT_CSV}\n - {OUT_GEOJSON}")
print(f"Schools with ≥1 station in 200 m: {(schools_geo['station_count']>0).sum()} / {len(schools_geo)}")
print("Max stations around a school (200 m):", schools_geo["station_count"].max())

# 8) Interactive map (Folium)
#    Color by station_count: 0=gray, 1=green, 2+=red
def color_for(n):
    if n == 0: return "#9e9e9e"  # gray
    if n == 1: return "#2e7d32"  # green
    return "#c62828"             # red

center = schools_geo.geometry.unary_union.centroid
m = folium.Map(location=[center.y, center.x], zoom_start=11, tiles="CartoDB Positron")

# Add stations as small markers
st_w = stations_m.to_crs(4326)
st_layer = folium.FeatureGroup(name="Active BLUME stations", show=True)
for _, r in st_w.iterrows():
    folium.CircleMarker(
        location=[r.geometry.y, r.geometry.x],
        radius=4, weight=1, fill=True, fill_opacity=0.9, opacity=0.9,
        color="#0066cc", popup=f"{r.get(st_id)} — {r.get(st_nm)}"
    ).add_to(st_layer)
st_layer.add_to(m)

# Add schools with 200 m discs colored by count
sch_layer = folium.FeatureGroup(name="Schools (200 m zone)", show=True)
for _, r in schools_geo.iterrows():
    lat, lon = r.geometry.y, r.geometry.x
    cnt = int(r["station_count"])
    folium.Circle(
        location=[lat, lon],
        radius=200,  # meters
        color=color_for(cnt), fill=True, fill_opacity=0.15, weight=2,
        tooltip=f"{r.get(school_nm)} | stations≤200m: {cnt}\nIDs: {', '.join(r['station_ids']) if r['station_ids'] else '—'}"
    ).add_to(sch_layer)
sch_layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
m.save(str(OUT_HTML))
print(f"Saved interactive map: {OUT_HTML}")
