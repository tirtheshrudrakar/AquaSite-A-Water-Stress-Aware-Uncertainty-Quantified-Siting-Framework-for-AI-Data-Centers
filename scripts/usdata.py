import pandas as pd

df = pd.read_csv("data/raw/aqueduct/CVS/Aqueduct40_baseline_annual_y2023m07d05.csv")

us_df = df[df["name_0"] == "United States"]

# Your hotspot states from the earlier research (Ceres 2026 study)
hotspot_states = ["Virginia", "Arizona", "Georgia", "Texas", "California", "Illinois", "Ohio"]
us_hotspots = us_df[us_df["name_1"].isin(hotspot_states)]

print(us_hotspots.shape)
us_hotspots.to_csv("data/processed/aqueduct_us_hotspots_annual.csv", index=False)