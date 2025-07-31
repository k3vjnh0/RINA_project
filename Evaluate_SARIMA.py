import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from pmdarima import auto_arima
import numpy as np

df_day = pd.read_csv("Katherine_InputData_Time_Series.csv")
df_day.columns = df_day.columns.str.strip()
df_day['Date'] = pd.to_datetime(df_day['Date'], dayfirst=True, errors='coerce')
df_day = df_day.dropna(subset=['Date'])


def run_sarima_forecast(df_input, mode='monthly', seasonal_period=12):
    """
    Run SARIMA forecasting on soil temperature data in two modes:
    - 'monthly': Full year data
    - 'wet_season': Only wet season months (December, January, February)

    Parameters:
        df_input: pandas DataFrame with columns 'Date' and 'Soil_Temperature'
        mode: 'monthly' or 'wet_season'
        forecast_periods: Number of steps to forecast
        seasonal_period: Seasonal period (12 for monthly, 3 for wet season)
    """

    df = df_day.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    # Monthly average
    df_monthly = df.groupby(['Year', 'Month']).mean(numeric_only=True).reset_index()
    df_monthly = df_monthly.dropna(subset=['Soil_Temperature'])
    df_monthly['Date'] = pd.to_datetime(df_monthly[['Year', 'Month']].assign(DAY=1))
    df_monthly = df_monthly.sort_values('Date').set_index('Date')
    df_monthly = df_monthly[['Soil_Temperature']]

    if mode == 'wet_season':
        df_monthly['Month'] = df_monthly.index.month
        df_model = df_monthly[df_monthly['Month'].isin([12, 1, 2])]
        seasonal_period = 3  # override
    else:
        df_model = df_monthly.copy()

    #df_model.index.freq = 'MS'
    df_model = df_model[['Soil_Temperature']]

    print(f"\n--- Mode: {mode.upper()} | Data Points: {len(df_model)} ---")

    # Plot data
    plt.figure(figsize=(10, 4))
    plt.plot(df_model.index, df_model['Soil_Temperature'], marker='o')
    plt.title(f"Soil Temperature - {mode}")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Check stationarity
    adf_result = adfuller(df_model['Soil_Temperature'])
    print(f"ADF Statistic: {adf_result[0]:.3f}, p-value: {adf_result[1]:.3f} → {'Stationary' if adf_result[1] < 0.05 else 'Non-stationary'}")

    # ACF & PACF plots
    plot_acf(df_model['Soil_Temperature'])
    plot_pacf(df_model['Soil_Temperature'])
    plt.show()

    # Train/Test split
    split_index = int(len(df_model) * 0.7)
    train = df_model.iloc[:split_index]
    test = df_model.iloc[split_index:]

    # Auto ARIMA
    auto_model = auto_arima(
        train['Soil_Temperature'],
        seasonal=True,
        m=seasonal_period,
        start_p=0, start_q=0, max_p=3, max_q=3,
        start_P=0, start_Q=0, max_P=2, max_Q=2,
        d=None, D=None,
        trace=True,
        error_action='ignore',
        suppress_warnings=True,
        stepwise=True
    )
    print(auto_model.summary())

    # SARIMA model
    order = auto_model.order
    seasonal_order = auto_model.seasonal_order
    model = SARIMAX(train['Soil_Temperature'], order=order, seasonal_order=seasonal_order)
    results = model.fit()
    print(results.summary())

    # Forecast
    forecast = results.get_forecast(steps=len(test))
    forecast_mean = forecast.predicted_mean
    forecast_ci = forecast.conf_int()

    # Plot forecast
    plt.figure(figsize=(14, 6))
    plt.plot(train.index, train['Soil_Temperature'], label='Train')
    plt.plot(test.index, test['Soil_Temperature'], label='Actual', color='green')
    plt.plot(forecast_mean.index, forecast_mean, label='Forecast', color='red')
    plt.fill_between(forecast_ci.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color='pink', alpha=0.3)
    plt.title(f'SARIMA Forecast - {mode}')
    plt.xlabel('Date')
    plt.ylabel('Soil Temperature (°C)')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Evaluate
    mae = mean_absolute_error(df_model.iloc[split_index:], forecast_mean)
    mse = mean_squared_error(df_model.iloc[split_index:], forecast_mean)
    r2 = r2_score(df_model.iloc[split_index:], forecast_mean)
    print(f" Evaluation ({mode}):")
    print(f"MAE: {mae:.3f}")
    print(f"MSE: {mse:.3f}")
    print(f"R²: {r2:.3f}")

# Forecast for full year (monthly)
#run_sarima_forecast(df_day, mode='monthly', seasonal_period=12)
# Forecast for wet season only
run_sarima_forecast(df_day, mode='wet_season', seasonal_period=3)