import pandas as pd

monthly = pd.read_csv("data/raw/aqueduct/CVS/Aqueduct40_baseline_monthly_y2023m07d05.csv")
annual = pd.read_csv(
    "data/raw/aqueduct/CVS/Aqueduct40_baseline_annual_y2023m07d05.csv",
    usecols=["pfaf_id", "name_0", "name_1"],
).drop_duplicates()

keep = ["pfaf_id"] + [c for c in monthly.columns if c.startswith(("bws_", "bwd_"))]
monthly = monthly[keep]

df = monthly.merge(annual, on="pfaf_id", how="inner")

us_df = df[df["name_0"] == "United States"]
hotspot_states = ["Virginia", "Arizona", "Georgia", "Texas", "California", "Illinois", "Ohio"]
us_hotspots = us_df[us_df["name_1"].isin(hotspot_states)]

print(us_hotspots.shape)
us_hotspots.to_csv("data/processed/aqueduct_us_hotspots_monthly.csv", index=False)