# Data Sources
1) **Berlin School Locations — “Schulen Berlin” (ESRI DE content)**  
   - Portal: <https://opendata-esridech.hub.arcgis.com/maps/esri-de-content::schulen-berlin-1/about>  

2) **Air-Quality Monitoring Stations — BLUME (berlin.de)**  
   - Stations list API: <https://luftdaten.berlin.de/api/stations>  

3) **Air-Quality Time Series (1-year daily)** — BLUME CSV export (berlin.de)  
   - Portal: <https://luftdaten.berlin.de/>  
   - Method: CSV export per pollutant with `timespan=custom`, `start[date]/start[hour]`, `end[date]/end[hour]`, `period=24h`  
   - Example pattern (NO₂ daily):
     ```
     https://luftdaten.berlin.de/core/no2.csv?timespan=custom&
       start[date]=2024-12-01&start[hour]=00&

# Data Sources and collection
## 01_data_collection

This stage focuses on acquiring authoritative source data required for the analysis, without modifying.

 1. Air Quality Monitoring Stations (BLUME):
  
  Source:
  Berlin Senate – BLUME Air Quality Monitoring Network
  https://luftdaten.berlin.de/api/stations

  Script:
  scripts/01_data_collection/stations_from_blume_api_v2.py
  
  What this script does:
  Fetches official air-quality monitoring station metadata directly from the BLUME public API
  Extracts station identifiers, names, geographic coordinates, activity status, and measured components
  Saves the data in both spatial and non-spatial formats

  Outputs:
  data/raw/stations/blume_stations.geojson
  data/raw/stations/blume_stations.csv

 2. Raw Air Quality Measurements:
  Source: Portal: <https://luftdaten.berlin.de/>  
   
   Daily air-pollution measurements (e.g. PM10, PM2.5, NO₂, O₃) were downloaded separately for each monitoring station.
   Each station provides data as a German-formatted CSV file.
   Storage: data/raw/air_quality_data/

 3. School Location Data
 Source: <https://opendata-esridech.hub.arcgis.com/maps/esri-de-content::schulen-berlin-1/about>  

 Geographic locations of schools in Berlin provided as GeoJSON and CSV
 storage:
 data/raw/schools/Schulen.geojson
 data/raw/schools/Schulen.csv

# 02_data_cleaning
 This stage transforms raw, heterogeneous data into clean, consistent, and analysis-ready datasets.
 ## 1. Cleaning and Filtering Monitoring Stations
  Script: scripts/02_data_cleaning/filter_active_stations.py
  
  * Loads raw station metadata collected from the BLUME API

  * Filters out inactive stations and stations with invalid coordinates
   
   Outputs:

       - data/raw/stations/blume_stations_active.csv

       - data/raw/stations/blume_stations_active.geojson
[blume_stations_active.csv](data/raw/stations/blume_stations_active.csv)

  ## 2. Merging and Cleaning Air Quality Measurements
   Script: scripts/02_data_cleaning/merging_station.py
    
  * Iterates over all raw station-level pollution CSV files

  * Extracts station identifiers and names from file names

  * Merges all stations into a single, unified dataset

    Output: data_clean/pollution_clean_long.csv

  [pollution_clean_long.csv](data_clean/pollution_clean_long.csv)
  
  ## 3. Cleaning School Location Data
   Script: scripts/02_data_cleaning/school_cleaning.py
   
  * Loads raw school location data.
  * Extracts latitude and longitude from spatial geometry
  * Removes entries with missing or invalid locations
  * Eliminates duplicate school locations
  * Saves cleaned school data in both spatial and tabular formats
 
  output: 

  - data_clean/berlin_schools_clean.geojson
         
  - data_clean/berlin_schools_clean.csv

[berlin_schools_clean.geojson](data_clean/berlin_schools_clean.csv)

# 03_processing
 ## 1. final_station.py :
  * Pollutant labels were inspected and standardised to internationally recognised naming conventions (e.g., PM10, PM2.5, NO₂).
  * This ensured consistency across stations and facilitated aggregation and comparison across pollutant types.

 ## 2. step1_yearly_aggregation.py

  * Script: scripts/03_processing/step1_yearly_aggregation.py

  * Input: `data_clean/pollution_clean_long.csv` (daily pollution measurements for all stations)

  * Output: `data_clean/station_yearly_pollution.csv` (yearly mean pollution values per station)

  [station_yearly_pollution.csv](data_clean/station_yearly_pollution.csv)

  * Purpose: This script aggregates daily air-pollution measurements into yearly average values for each monitoring station and pollutant.

  * Method:
  - Extracts the calendar year from daily timestamps  
  - Groups pollution measurements by station, pollutant, and year  
  - Computes the mean pollution level for each group  
  - Produces a clean, compact dataset suitable for spatial analysis  

  * Why this step matters:  
  Daily pollution data are highly variable and unsuitable for long-term exposure assessment. Yearly averages provide a stable and interpretable representation of air quality that can be reliably linked to school locations in subsequent spatial analyses.

  ## 3. step2_attach_station_geometry.py
  * Attach Station Geometry to Yearly Pollution Data

  * Script: `scripts/03_processing/step2_attach_station_geometry.py`

  * Input:
    - `data_clean/station_yearly_pollution.csv` (yearly pollution per station)  
    - `data/raw/blume_stations_active.geojson` (active station locations)

 * Output:  `data_clean/stations_yearly_pollution.geojson` (spatial pollution dataset)

 * Purpose: This script combines yearly aggregated pollution data with the geographic locations of air-quality monitoring stations to create a spatially enabled pollution dataset.

 * Why this step matters:  
  Spatial exposure analysis requires pollution data to be linked to geographic locations. This step enables distance-based and buffer-based analyses by transforming tabular pollution data into a spatial dataset.

# 04_exposure_analysis
 ## stations_vs_schools_1000m.py
   
 - Calculates how many schools are located within a 1 km radius of each active BLUME air quality monitoring station in Berlin.

 - Method

   - Load cleaned school locations and active station data

   - Reproject to EPSG:25833 for accurate distance calculation

   - Create 1 km buffers around stations

   - Spatially join schools within buffers

   - Count schools per station
  

  - Outputs

    - data/derived/stations_school_1000m_counts.csv
    → School count per station
[stations_school_1000m_counts.csv](data/derived/stations_school_1000m_counts.csv)
   
    - data/derived/stations_school_1000m.geojson
    → Station geometries with school counts

    - data/derived/schools_per_station_1000m.png
    → Bar chart of schools per station
[schools_per_station_1000m.png](data/derived/schools_per_station_1000m.png)
    
    - data/derived/stations_school_1000m_map.html
    → Interactive map with 1 km buffers
[stations_school_1000m_map.html](data/derived/stations_school_1000m_map.html)  
  
  - Purpose
   - Why This Is Important

     - Which monitoring stations matter most for school exposure?
     - Are pollution hotspots near dense school clusters?
     - Where should policy focus?

   - Identifies monitoring stations that are most relevant from a school exposure perspective and supports further pollution–exposure analysis.

 ## mean_no2_per_station.py
  This script calculates the long-term average annual NO₂ concentration for each monitoring station in Berlin and compares it to the WHO annual guideline.
  It provides a station-level pollution ranking to identify persistent NO₂ hotspots.

   - Method

     - Load yearly aggregated pollution data (station_yearly_pollution.csv).
     - Standardise pollutant names.
     - Filter only NO₂ observations.
     - Compute the mean NO₂ concentration per station (averaged across available years).
     - Compare results against the WHO annual guideline (10 µg/m³).
     - Generate a bar chart visualisation.

   - Outputs

      - Saved in:

       data/derived/

        mean_no2_per_station.csv
       → Table containing mean NO₂ concentration per station

      - Saved in:

         data/derived/figures/

         mean_no2_per_station.png
         → Bar chart of station-wise NO₂ levels with WHO guideline reference line

 ## mean_pm10_per_station.py
  This script calculates the long-term average annual PM10 concentration for each air quality monitoring station in Berlin and compares it against the WHO annual air quality guideline.
  It provides a station-level ranking to identify persistent PM10 hotspots.
     
  - Method

      - Load yearly aggregated pollution data (station_yearly_pollution.csv).

      - Standardise pollutant names for consistency.

      - Filter only PM10 observations.

      - Compute the mean PM10 concentration per station (averaged across available years).

      - Compare results with the WHO annual guideline (15 µg/m³).

      - Generate a bar chart visualisation.


  - Outputs

      - Saved in:

        data/derived/

        mean_pm10_per_station.csv
        → Table containing mean PM10 concentration per station

      - Saved in:

        data/derived/figures/

        mean_pm10_per_station.png
        → Bar chart showing station-wise PM10 levels with WHO reference line

 ## mean_pm25_per_station.py
  This script calculates the long-term average annual PM2.5 concentration for each air quality monitoring station in Berlin and compares it to the WHO annual air quality guideline.
  It identifies stations with persistently high fine particulate pollution levels.

  - Method

      - Load yearly aggregated pollution data (station_yearly_pollution.csv).

      - Standardise pollutant names for consistency.

      - Filter only PM2.5 observations.

      - Compute the mean PM2.5 concentration per station (averaged across available years).

      - Compare results with the WHO annual guideline (5 µg/m³).

      - Generate a bar chart visualisation.
  
  - Outputs

      - Saved in:

      data/derived/

      mean_pm25_per_station.csv
      → Table containing mean PM2.5 concentration per station

      - Saved in:

      data/derived/figures/

      mean_pm25_per_station.png
      → Bar chart showing station-wise PM2.5 levels with WHO reference line
 ## exceedance-vs-school_exposure.py
  This script links annual air pollution levels at monitoring stations with school proximity to assess potential exposure relevance. It evaluates whether stations exceeding WHO air quality guidelines are located near a higher number of schools.

 - Method

   Load:
    - station_yearly_pollution.csv (annual mean concentrations per station)
    - stations_school_1000m_counts.csv (number of schools within 1 km)

   Standardise:

   - Station IDs (format alignment)
   - Pollutant names (PM2.5, PM10, NO2)

   Filter:

    - Use the most recent year available
    - Focus only on PM2.5, PM10, and NO2
   
   Apply WHO annual guidelines:

    - PM2.5 → 5 µg/m³
    - PM10 → 15 µg/m³
    - NO2 → 10 µg/m³
  
   Merge pollution data with school counts.

   Generate scatter plots for each pollutant showing:

   - X -axis: Number of schools within buffer

   - Y-axis: Annual mean concentration

   - Dashed line: WHO annual limit

   - Points classified as above or below WHO threshold


 - Outputs

    - Saved in:

    - data/derived/figures/

    - NO2_vs_school_exposure_WHO_<year>.png

    - PM10_vs_school_exposure_WHO_<year>.png

    - PM2.5_vs_school_exposure_WHO_<year>.png

 - Purpose

   - This analysis examines whether air pollution exceedance levels coincide with higher school density around monitoring stations,   supporting assessment of potential environmental health relevance in urban areas.
  
  
 ## Exposure Burden Index Analysis
   This script computes an Exposure Burden Index (EBI) for Berlin air-quality monitoring stations by combining:
  
  - Annual mean pollutant concentration

  - Number of schools located within a 1 km buffer

  The index is defined as:

  - Exposure Burden = Annual Mean Concentration × School Count

  This identifies locations where high pollution levels coincide with high school density.

  Research Objective:
   - Which monitoring stations represent the highest combined pollution intensity and potential school exposure burden in Berlin?

  
  Methodology

  - Load yearly aggregated station pollution data.
  - Standardise pollutant names and station IDs.
  - Merge with station-level school counts (1 km buffer).
  - Compute Exposure Burden Index per station
  - Rank stations in descending order.
  - Generate tables and visualisations.

Outputs

 - For each pollutant:
  - Tables 
   - data/derived/NO2_exposure_burden_<year>.csv
   - data/derived/PM10_exposure_burden_<year>.csv
   - data/derived/PM2.5_exposure_burden_<year>.csv

Figures
 - data/derived/figures/<pollutant>_exposure_burden_<year>.png
 - Bar charts ranking stations by exposure burden.

 
Interpretation

 A high Exposure Burden Index indicates:
 - Elevated pollutant concentration
    AND
 - A high number of nearby schools

 These stations represent priority areas for environmental health and urban planning interventions.

## Monitoring Adequacy & Health Risk Assessment

 Objective

   - This analysis evaluates whether Berlin schools that are exposed to elevated air pollution levels are also adequately covered by nearby monitoring stations.
   
 - The assessment combines:

   - WHO 2021 annual air quality guidelines

   - Spatial proximity to monitoring stations (1 km threshold)

   - School-level exposure context

  Methodology

 - For each pollutant (NO₂, PM10, PM2.5):

   - Latest yearly mean concentration per station was used.

 - WHO annual limits were applied:

    - NO₂: 10 µg/m³

    - PM10: 15 µg/m³

    - PM2.5: 5 µg/m³

  - Each school was classified based on:

    - Distance to nearest monitoring station (≤1 km = Covered)

    - Whether the nearest station exceeded WHO limits
  
 Outputs

  - The script generates:

   - 3-panel publication-style figure

   - Separate pollutant plots with WHO guideline lines

   - Exposure summary tables

   - Monitoring adequacy classification results

 Interpretation Scope

   - Results represent a distance-based monitoring adequacy assessment, not direct on-site pollution measurements at schools.

   - Findings should be interpreted within the defined assumptions:

   - 1 km spatial threshold

   - Nearest-station proxy

   - WHO 2021 annual guidelines  

## monitoring_adequacy_primary_secondary

Evaluates monitoring coverage and pollution risk separately for Primary and Secondary schools in Berlin using NO₂, PM10, and PM2.5.

 Method:

 - Classify schools → Primary (Grundschule), Secondary (Gymnasium, ISS, Privatschule)

 - Compute nearest station distance

 - Use latest yearly pollution data

 - Compare with WHO limits

 - Apply 1 km threshold to classify schools into:

   - Covered & Safe

   - Covered but High Risk

   - Under-monitored but Low Risk

   - Under-monitored & High Risk

 Outputs:
   - Tables:

     - rq4_monitoring_summary_primary_<year>.csv

     - rq4_monitoring_summary_secondary_<year>.csv

   - Figures:

     - RQ4_monitoring_adequacy_panel_primary_<year>.png

     - RQ4_monitoring_adequacy_panel_secondary_<year>.png
 
## rq5_school_category_exposure.py
  Analyzes how different school categories (Primary, Secondary, Vocational, Special/Other) are exposed to air pollution (NO₂, PM10, PM2.5) within a 1 km buffer of monitoring stations.

  
 Method

   - Classify schools using schulart

   - Create 1 km buffers around stations

   - Identify schools within buffers (spatial join)

   - Merge with latest yearly pollution data

   - Compare with WHO limits and flag exceedance

   - Aggregate exposure by school category and pollutant

 Outputs

   - Table:

     - school_category_pollution_exposure.csv

   - Figure:

     - school_category_exposure_panel_<year>.png

## seasonal_school_exposure_comparison.py
  Compares winter vs summer pollution and exposure for schools near monitoring stations, including NO₂, PM10, PM2.5, and O₃.

 Method
   - Use daily pollution data (pollution_clean_long.csv)

   - Define seasons: Winter (Dec–Feb), Summer (Jun–Aug)

   - Keep only complete seasons (3 months)

   - Compute seasonal mean per station

   - Merge with school counts (1 km buffer)

   - Calculate Exposure Burden = pollution × school_count

 Outputs

   - Table:

     - seasonal_school_exposure_summary_with_o3.csv

   Figures:

     - seasonal_pollution_comparison_panel_with_o3.png

     - seasonal_exposure_burden_comparison_panel_with_o3.png