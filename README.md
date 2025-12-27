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

1. Core Research Question (Main Objective)

RQ1.
What is the spatial exposure of schools in Berlin to air pollution based on proximity to official air-quality monitoring stations?

2. Spatial Exposure Assessment Questions

RQ2.
Which schools are closest to air-quality monitoring stations, and what pollution levels are associated with those stations?

RQ3.
How far are schools located from their nearest active air-quality monitoring station across Berlin?

3. Proximity-Based Risk Questions (Buffer Analysis)

RQ4.
How many schools are located within 200 meters of air-pollution monitoring stations?

RQ5.
Do schools located within 200 meters of monitoring stations experience higher average pollution levels compared to schools located further away?

4. Pollutant-Specific Exposure Questions

RQ6.
How does school exposure differ across major regulated pollutants such as NO₂, PM₂.₅, and PM₁₀?

RQ7.
Which pollutant contributes most to potential exposure risk at school locations?

5. Inequality and Spatial Justice Questions

RQ8.
Is air-pollution exposure at schools evenly distributed across Berlin, or are there spatial patterns of inequality?

RQ9.
Are schools located in inner-city areas exposed to higher pollution levels than those in outer districts?

6. Distance–Exposure Relationship Questions

RQ10.
Is there a relationship between distance from pollution monitoring stations and estimated pollution exposure at schools?

RQ11.
Does pollution exposure decrease as distance from monitoring stations increases?

7. Temporal Analysis Questions (Optional Extension)

RQ12.
How does school pollution exposure vary across different seasons or months?

RQ13.
Are winter pollution levels at schools significantly higher than summer levels?

8. Multi-Pollutant Exposure Questions (Advanced)

RQ14.
Which schools experience the highest cumulative air-pollution burden when considering multiple pollutants simultaneously?

RQ15.
How does a combined pollution exposure index change the ranking of high-risk schools compared to single-pollutant analysis?

9. Policy and Planning Questions (Urban Technology Focus)

RQ16.
Which schools should be prioritized for mitigation measures based on their pollution exposure levels?

RQ17.
How can spatial exposure analysis inform future school-site planning and traffic-management strategies in Berlin?

10. Methodological Reflection Questions

RQ18.
How do nearest-station and buffer-based exposure assessment methods differ in identifying high-risk schools?

RQ19.
What are the limitations of using monitoring-station proximity as a proxy for school-level pollution exposure?

11. Future Research Questions (Beyond This Study)

RQ20.
How could machine-learning or spatial interpolation techniques improve pollution exposure estimation if denser data were available?