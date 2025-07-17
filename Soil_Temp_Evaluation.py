import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tkinter as tk
from tkinter import filedialog

# Step 1: File input dialog
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Select Excel file",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)

if not file_path:
    print("No file selected. Exiting.")
    exit()

# Step 2: Read Excel
df = pd.read_excel(file_path)

# Step 3: Clean and convert columns
df.columns = [col.strip() for col in df.columns]  # Remove extra spaces
df["observed temperature"] = pd.to_numeric(df["observed temperature"], errors="coerce")
df["Formula"] = pd.to_numeric(df["Formula"], errors="coerce")
df = df.dropna(subset=["observed temperature", "Formula"])  # Drop invalid rows

# Step 4: Evaluation
observed = df["observed temperature"]
estimated = df["Formula"]

rmse = np.sqrt(mean_squared_error(observed, estimated))
mae = mean_absolute_error(observed, estimated)
r2 = r2_score(observed, estimated)

print("Model Evaluation Metrics:")
print(f"RMSE: {rmse:.2f} °C")
print(f"MAE: {mae:.2f} °C")
print(f"R²: {r2:.2f}")

# Step 5: Scatter Plot
plt.figure(figsize=(7, 7))
plt.scatter(observed, estimated, color='blue', label='Estimated vs Observed')
plt.plot([observed.min(), observed.max()],
         [observed.min(), observed.max()],
         'r--', label='1:1 Reference Line')
plt.xlabel("Observed Temperature (°C)")
plt.ylabel("Estimated Temperature (°C)")
plt.title("Observed vs Estimated Soil Temperature")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.tight_layout()
plt.show()

# Step 6: Time Series Plot
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")

    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["observed temperature"], marker='o', label='Observed', color='blue')
    plt.plot(df["Date"], df["Formula"], marker='s', label='Estimated', color='orange')
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.title("Observed vs Estimated Soil Temperature Over Time")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("'Date' column not found. Skipping time series plot.")
