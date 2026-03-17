from pathlib import Path
import pandas as pd

# PATH
ROOT = Path(__file__).resolve().parents[2]
DATA_CLEAN = ROOT / "data_clean"

# LOAD DATA
schools = pd.read_csv(DATA_CLEAN / "berlin_schools_clean.csv")

# UNIQUE TYPES
unique_types = schools["schultyp"].unique()

print("Unique schultyp values:")
print(unique_types)

print("\nTotal unique types:", len(unique_types))