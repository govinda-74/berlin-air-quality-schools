from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATA_CLEAN = ROOT / "data_clean"
DATA_DERIVED = ROOT / "data" / "derived"
FIG_DIR = DATA_DERIVED / "figures"

DATA_DERIVED.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

SCHOOLS_FILE = DATA_CLEAN / "berlin_schools_clean.csv"
schools = pd.read_csv(SCHOOLS_FILE)

# --------------------------------------------------
# COUNT BY schulart
# --------------------------------------------------

schulart_count = (
    schools["schulart"]
    .value_counts()
    .reset_index()
)

schulart_count.columns = ["school_type", "count"]

# Save table
OUT_CSV = DATA_DERIVED / "school_count_by_schulart.csv"
schulart_count.to_csv(OUT_CSV, index=False)

print("School counts by schulart:")
print(schulart_count)

# --------------------------------------------------
# VISUALISATION
# --------------------------------------------------

plt.figure(figsize=(10,6))
plt.barh(schulart_count["school_type"], schulart_count["count"])

plt.xlabel("Number of Schools")
plt.ylabel("School Category")
plt.title("Distribution of School Types in Berlin")

plt.tight_layout()

OUT_PNG = FIG_DIR / "school_type_distribution.png"
plt.savefig(OUT_PNG, dpi=300)
plt.close()

print("Saved:")
print(OUT_CSV)
print(OUT_PNG)