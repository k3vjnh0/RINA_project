import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox
from datetime import datetime
from pmdarima import auto_arima
from statsmodels.tsa.statespace.sarimax import SARIMAX

# --- Load & preprocess data ---
df_day = pd.read_csv("Katherine_InputData_Time_Series.csv")
df_day.columns = df_day.columns.str.strip()
df_day['Date'] = pd.to_datetime(df_day['Date'], dayfirst=True, errors='coerce')
df_day = df_day.dropna(subset=['Date'])
df_day['Year'] = df_day['Date'].dt.year
df_day['Month'] = df_day['Date'].dt.month

df_monthly = df_day.groupby(['Year', 'Month']).mean(numeric_only=True).reset_index()
df_monthly = df_monthly.dropna(subset=['Soil_Temperature'])
df_monthly['Date'] = pd.to_datetime(df_monthly[['Year', 'Month']].assign(DAY=1))
df_monthly = df_monthly.sort_values('Date')
df_monthly.set_index('Date', inplace=True)
df_monthly = df_monthly[['Soil_Temperature']]

# --- Build SARIMA model ---
def build_model():
    global model_results, df_monthly
    auto_model = auto_arima(
        df_monthly['Soil_Temperature'],
        seasonal=True, m=12,
        start_p=0, start_q=0, max_p=3, max_q=3,
        start_P=0, start_Q=0, max_P=2, max_Q=2,
        d=None, D=None,
        trace=False,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True
    )
    order = auto_model.order
    seasonal_order = auto_model.seasonal_order
    model = SARIMAX(df_monthly['Soil_Temperature'], order=order, seasonal_order=seasonal_order)
    model_results = model.fit()

build_model()

# --- Forecast & Plot ---
def forecast_to_date():
    try:
        month = int(entry_month.get())
        year = int(entry_year.get())
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12.")

        last_date = df_monthly.index[-1]
        end_date = datetime(year, month, 1)
        if end_date <= last_date:
            messagebox.showerror("Error", "Target date must be in the future.")
            return

        months_diff = (end_date.year - last_date.year) * 12 + (end_date.month - last_date.month)

        forecast = model_results.get_forecast(steps=months_diff)
        forecast_mean = forecast.predicted_mean
        forecast_ci = forecast.conf_int()

        forecast_index = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=months_diff, freq='MS')
        forecast_mean.index = forecast_index
        forecast_ci.index = forecast_index

        forecast_df = pd.DataFrame({
            'Forecast': forecast_mean,
            'Lower CI': forecast_ci.iloc[:, 0],
            'Upper CI': forecast_ci.iloc[:, 1]
        })
        forecast_df.index.name = 'Date'

        # Save to Excel
        output_file = f"soil_temperature_forecast_until_{month}_{year}.xlsx"
        forecast_df.to_excel(output_file)

        messagebox.showinfo("Success", f"Forecast saved to:\n{output_file}")

        # Plotting
        plt.figure(figsize=(14, 6))
        plt.plot(df_monthly.index, df_monthly['Soil_Temperature'], label='Observed')
        plt.plot(forecast_mean.index, forecast_mean, label='Forecast', color='red')
        plt.fill_between(forecast_ci.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color='pink', alpha=0.3)
        plt.title(f"Soil Temperature Forecast until {month}/{year}")
        plt.xlabel("Date")
        plt.ylabel("Soil Temperature (°C)")
        plt.legend()
        plt.tight_layout()
        plt.show()
        
       
        # Plotting only forecast with month labels and temperature values
        plt.figure(figsize=(14, 6))
        plt.plot(forecast_mean.index, forecast_mean, label='Forecast', color='blue', marker='o')
        plt.fill_between(forecast_ci.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color='lightblue', alpha=0.3)

        # Display temperature values on each forecast point
        for date, temp in forecast_mean.items():
            plt.text(date, temp + 0.2, f"{temp:.1f}°C", ha='center', va='bottom', fontsize=9, rotation=0)

        plt.title(f"Forecast Only: Soil Temperature from {forecast_index[0].strftime('%b %Y')} to {forecast_index[-1].strftime('%b %Y')}")
        plt.xlabel("Month")
        plt.ylabel("Soil Temperature (°C)")

        # Format x-axis to show each month clearly
        plt.xticks(forecast_mean.index, [d.strftime('%b\n%Y') for d in forecast_mean.index], rotation=45)

        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.show()


    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{str(e)}")

# --- Tkinter GUI ---
root = Tk()
root.title("Soil Temperature Forecast")

Label(root, text="Forecast up to Month:").grid(row=0, column=0, padx=10, pady=5)
entry_month = Entry(root)
entry_month.grid(row=0, column=1, padx=10, pady=5)

Label(root, text="Forecast up to Year:").grid(row=1, column=0, padx=10, pady=5)
entry_year = Entry(root)
entry_year.grid(row=1, column=1, padx=10, pady=5)

Button(root, text="Run Forecast, Save Excel & Plot", command=forecast_to_date, bg='green', fg='white').grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()
