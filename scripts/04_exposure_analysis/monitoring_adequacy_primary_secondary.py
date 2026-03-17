from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --------------------------------------------------
# ROOT DETECTION
# --------------------------------------------------
THIS_FILE = Path(__file__).resolve()
ROOT = None
for p in THIS_FILE.parents:
    if (p / "data_clean").exists():
        ROOT = p
        break

if ROOT is None:
    raise FileNotFoundError("Project root not found.")

DATA_CLEAN   = ROOT / "data_clean"
DATA_RAW     = ROOT / "data" / "raw"
DATA_DERIVED = ROOT / "data" / "derived"
FIG_DIR      = DATA_DERIVED / "figures"

DATA_DERIVED.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------
SCHOOLS_FP   = DATA_CLEAN / "berlin_schools_clean.geojson"
STATIONS_FP  = DATA_RAW / "stations" / "blume_stations_active.geojson"
POLLUTION_FP = DATA_CLEAN / "station_yearly_pollution.csv"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
schools  = gpd.read_file(SCHOOLS_FP).to_crs(25833)
stations = gpd.read_file(STATIONS_FP).to_crs(25833)
pollution = pd.read_csv(POLLUTION_FP)

# --------------------------------------------------
# CLASSIFY SCHOOL TYPES
# --------------------------------------------------
def classify_school_type(x):
    x = str(x)

    if x == "Grundschule":
        return "Primary"
    elif x in ["Gymnasium", "Integrierte Sekundarschule", "Privatschule"]:
        return "Secondary"
    else:
        return "Other"

schools["school_group"] = schools["schultyp"].apply(classify_school_type)

# Keep only Primary + Secondary
schools = schools[schools["school_group"].isin(["Primary", "Secondary"])].copy()

# --------------------------------------------------
# NEAREST STATION DISTANCE
# --------------------------------------------------
nearest = gpd.sjoin_nearest(
    schools,
    stations,
    how="left",
    distance_col="distance_m"
)

# --------------------------------------------------
# STANDARDISE POLLUTANT NAMES
# --------------------------------------------------
pollutant_map = {
    "Feinstaub (PM2,5)": "PM2.5",
    "Feinstaub (PM2.5)": "PM2.5",
    "Feinstaub (PM10)": "PM10",
    "Stickstoffdioxid": "NO2",
}
pollution["pollutant"] = pollution["pollutant"].replace(pollutant_map)

WHO_LIMITS = {"NO2": 10, "PM10": 15, "PM2.5": 5}
TARGETS = ["NO2", "PM10", "PM2.5"]

# Use latest year
latest_year = pollution["year"].max()
pollution = pollution[pollution["year"] == latest_year].copy()

pollution["who_limit"] = pollution["pollutant"].map(WHO_LIMITS)
pollution["exceeds_who"] = pollution["mean_value"] > pollution["who_limit"]

# Keep only relevant pollutants
pollution = pollution[pollution["pollutant"].isin(TARGETS)]

# Standardise station_id
pollution["station_id"] = pollution["station_id"].astype(str).str.replace("mc", "", regex=False).str.zfill(3)
nearest["station_id"] = nearest["station_id"].astype(str).str.replace("mc", "", regex=False).str.zfill(3)

# Pivot exceedance info
pollution_wide = pollution.pivot_table(
    index="station_id",
    columns="pollutant",
    values="exceeds_who"
).reset_index()

nearest = nearest.merge(pollution_wide, on="station_id", how="left")

# --------------------------------------------------
# CLASSIFICATION SETTINGS
# --------------------------------------------------
THRESHOLD = 1000  # 1 km

order = [
    "Covered & Safe",
    "Covered but High Risk",
    "Under-monitored but Low Risk",
    "Under-monitored & High Risk"
]

colors = {
    "Covered & Safe": "#4CAF50",
    "Covered but High Risk": "#FF9800",
    "Under-monitored but Low Risk": "#90A4AE",
    "Under-monitored & High Risk": "#D32F2F"
}

# --------------------------------------------------
# RUN FOR PRIMARY AND SECONDARY SEPARATELY
# --------------------------------------------------
for school_group in ["Primary", "Secondary"]:

    nearest_group = nearest[nearest["school_group"] == school_group].copy()

    summary_results = []

    for pol in TARGETS:

        if pol not in nearest_group.columns:
            continue

        temp = nearest_group.copy()
        temp["risk_category"] = "Covered & Safe"

        temp.loc[
            (temp["distance_m"] <= THRESHOLD) & (temp[pol] == True),
            "risk_category"
        ] = "Covered but High Risk"

        temp.loc[
            (temp["distance_m"] > THRESHOLD) & (temp[pol] == False),
            "risk_category"
        ] = "Under-monitored but Low Risk"

        temp.loc[
            (temp["distance_m"] > THRESHOLD) & (temp[pol] == True),
            "risk_category"
        ] = "Under-monitored & High Risk"

        counts = temp["risk_category"].value_counts().reset_index()
        counts.columns = ["category", "school_count"]
        counts["pollutant"] = pol
        counts["percentage"] = counts["school_count"] / len(temp) * 100

        summary_results.append(counts)

    final_summary = pd.concat(summary_results, ignore_index=True)

    # Save summary table
    out_csv = DATA_DERIVED / f"rq4_monitoring_summary_{school_group.lower()}_{latest_year}.csv"
    final_summary.to_csv(out_csv, index=False)

    print(f"Summary table saved for {school_group}:", out_csv)
    print(final_summary)

    # --------------------------------------------------
    # 3-PANEL FIGURE
    # --------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

    for ax, pol in zip(axes, TARGETS):
        sub = final_summary[final_summary["pollutant"] == pol].copy()

        if sub.empty:
            continue

        sub = sub.set_index("category").reindex(order).reset_index()

        bars = ax.bar(
            sub["category"],
            sub["school_count"],
            color=[colors[c] for c in sub["category"]],
            edgecolor="black",
            linewidth=0.5
        )

        ax.set_title(pol, fontsize=14, weight="bold")
        ax.set_xticks(range(len(sub["category"])))
        ax.set_xticklabels(sub["category"], rotation=30, ha="right", fontsize=10)

        for bar, pct in zip(bars, sub["percentage"]):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.5,
                f"{pct:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9
            )

    axes[0].set_ylabel("Number of Schools", fontsize=12)

    fig.suptitle(
        f"{school_group} Schools: Monitoring Adequacy & Health Risk Assessment ({latest_year})",
        fontsize=16,
        weight="bold"
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    out_png = FIG_DIR / f"RQ4_monitoring_adequacy_panel_{school_group.lower()}_{latest_year}.png"
    plt.savefig(out_png, dpi=300)
    plt.close()

    print(f"3-panel figure saved for {school_group}:", out_png)