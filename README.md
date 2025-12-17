## Data Sources
1) **Berlin School Locations — “Schulen Berlin” (ESRI DE content)**  
   - Portal: <https://opendata-esridech.hub.arcgis.com/maps/esri-de-content::schulen-berlin-1/about>  
   - File used: `data/berlin_schools_clean.geojson` (cleaned from source download)  
   - CRS: WGS84 (EPSG:4326) → reprojected to **ETRS89 / UTM 33N (EPSG:25833)** for distance/buffers  
   - Accessed: 2025-12-17

2) **Air-Quality Monitoring Stations — BLUME (berlin.de)**  
   - Stations list API: <https://luftdaten.berlin.de/api/stations>  
   - Script: `stations_from_blume_api_v2.py` → outputs `data/blume_stations.{csv,geojson}`  
   - Filter: `filter_active_stations.py` → `data/blume_stations_active.{csv,geojson}`  
   - CRS: WGS84 → EPSG:25833 for spatial ops  
   - Accessed: 2025-12-17

3) **Air-Quality Time Series (1-year daily)** — BLUME CSV export (berlin.de)  
   - Portal: <https://luftdaten.berlin.de/>  
   - Method: CSV export per pollutant with `timespan=custom`, `start[date]/start[hour]`, `end[date]/end[hour]`, `period=24h`  
   - Example pattern (NO₂ daily):
     ```
     https://luftdaten.berlin.de/core/no2.csv?timespan=custom&
       start[date]=2024-12-01&start[hour]=00&
       end[date]=2025-11-30&end[hour]=23&
       period=24h&stationgroup=all
     ```
