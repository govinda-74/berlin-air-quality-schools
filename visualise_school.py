import geopandas as gpd
import folium

gdf = gpd.read_file("data/clean_data/berlin_schools_clean.geojson")

# Center map on Berlin
m = folium.Map(location=[52.52, 13.405], zoom_start=11)

# Add points
for _, row in gdf.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=3,
        color="blue",
        fill=True,
        fill_opacity=0.7,
        popup=row["schulname"]
    ).add_to(m)

# Save interactive map
m.save("berlin_schools_map.html")
print("Map saved as berlin_schools_map.html")
