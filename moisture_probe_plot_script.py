import matplotlib.pyplot as plt
import pandas as pd

# Load the CSV
moisture_df = pd.read_csv("Moisture_Probe.csv")
moisture_df.columns = moisture_df.columns.str.strip()

# Parse datetime
moisture_df["Date Time"] = pd.to_datetime(moisture_df["Date Time"], dayfirst=True)
moisture_df["Month"] = moisture_df["Date Time"].dt.strftime("%b")

# Define columns
moisture_cols = ["A1(10)", "A2(20)", "A3(40)", "A4(60)", "A5(90)"]
temperature_col = "T1(10)"
humidity_col = "H1(10)"

# Group data
grouped = moisture_df.groupby("Month")

# Helper to order months
month_order = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

# Plot 1: Soil Water Content across depths
plt.figure(figsize=(10, 6))
for col in moisture_cols:
    grouped[col].mean().reindex(month_order).plot(label=col)
plt.title("Soil Water Content by Depth (Monthly Average)")
plt.xlabel("Month")
plt.ylabel("Water Content")
plt.legend(title="Depth")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot1_soil_water_content.png")
plt.show()

# Plot 2: Soil Temperature at 10cm
plt.figure(figsize=(8, 5))
grouped[temperature_col].mean().reindex(month_order).plot(color="orange")
plt.title("Soil Temperature at 10cm (Monthly Average)")
plt.xlabel("Month")
plt.ylabel("Temperature (°C)")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot2_soil_temperature.png")
plt.show()

# Plot 3: Soil Humidity at 10cm
plt.figure(figsize=(8, 5))
grouped[humidity_col].mean().reindex(month_order).plot(color="green")
plt.title("Soil Humidity at 10cm (Monthly Average)")
plt.xlabel("Month")
plt.ylabel("Humidity (%)")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot3_soil_humidity.png")
plt.show()

# Plot 4: Combined Water Content, Temperature, and Humidity
fig, ax = plt.subplots(figsize=(12, 6))
for col in moisture_cols:
    grouped[col].mean().reindex(month_order).plot(ax=ax, label=col)
grouped[temperature_col].mean().reindex(month_order).plot(
    ax=ax, linestyle="--", color="orange", label="T1(10)"
)
grouped[humidity_col].mean().reindex(month_order).plot(
    ax=ax, linestyle="--", color="green", label="H1(10)"
)
plt.title("Combined: Soil Water, Temp, and Humidity")
plt.xlabel("Month")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plot4_combined.png")
plt.show()
