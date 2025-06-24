import pandas as pd

# Load data
file_path = "./silo_data_cleaned.csv"
df = pd.read_csv(file_path)

# Ensure Date2 is string and filter rows that look like dates
df["Date2"] = df["Date2"].astype(str)

# Split by '-' and clean
split_date = df["Date2"].str.split("-", expand=True)

# Only keep rows where split worked
df = df[split_date.notnull().all(axis=1)]

# Convert to numeric safely
df["day"] = pd.to_numeric(split_date[0], errors="coerce")
df["month"] = pd.to_numeric(split_date[1], errors="coerce")
df["year"] = pd.to_numeric(split_date[2], errors="coerce")

# Drop bad rows
df = df.dropna(subset=["day", "month", "year"])
df["day"] = df["day"].astype(int)
df["month"] = df["month"].astype(int)
df["year"] = df["year"].astype(int)

# Convert PET + temperatures
df["Mpot"] = pd.to_numeric(df["Mpot"], errors="coerce")
df["T.Max"] = pd.to_numeric(df["T.Max"], errors="coerce")
df["T.Min"] = pd.to_numeric(df["T.Min"], errors="coerce")

# Compute Tmean
df["Tmean"] = (df["T.Max"] + df["T.Min"]) / 2

# Monthly summary
monthly_summary = (
    df.groupby(["year", "month"])
    .agg({"Mpot": "sum", "T.Max": "mean", "T.Min": "mean", "Tmean": "mean"})
    .reset_index()
)

monthly_summary.rename(columns={"Mpot": "PET"}, inplace=True)

# Show result
# print("\nMonthly PET + temperature summary (first 5 rows):")
# print(monthly_summary.head())

# Pivot tables
pet_df = monthly_summary.pivot(index="year", columns="month", values="PET")
tmax_df = monthly_summary.pivot(index="year", columns="month", values="T.Max")
tmin_df = monthly_summary.pivot(index="year", columns="month", values="T.Min")
tmean_df = monthly_summary.pivot(index="year", columns="month", values="Tmean")

# Sort the DataFrames by index in descending order
pet_df = pet_df.sort_index(ascending=False)
tmax_df = tmax_df.sort_index(ascending=False)
tmin_df = tmin_df.sort_index(ascending=False)
tmean_df = tmean_df.sort_index(ascending=False)

# Save to CSV files
pet_df.to_csv("pet_table.csv")
tmax_df.to_csv("tmax_table.csv")
tmin_df.to_csv("tmin_table.csv")
tmean_df.to_csv("tmean_table.csv")
