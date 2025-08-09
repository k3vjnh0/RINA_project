import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from pmdarima import auto_arima
import numpy as np

# Load data
df_day = pd.read_csv("Katherine_InputData_Time_Series.csv")
df_day.columns = df_day.columns.str.strip()
df_day['Date'] = pd.to_datetime(df_day['Date'], dayfirst=True, errors='coerce')
df_day = df_day.dropna(subset=['Date'])

def run_sarima_forecast(df_input, mode='monthly', seasonal_period=12, exog_vars=None):
    """
    Run SARIMA forecasting on soil temperature data with optional exogenous variables.

    Parameters:
        df_input: pandas DataFrame with at least 'Date' and 'Soil_Temperature'
        mode: 'monthly', 'wet_season', or 'daily_wet_season'
        seasonal_period: seasonal period (12 for monthly, 3 for wet season, etc.)
        exog_vars: list of column names to use as exogenous regressors
    """

    df = df_input.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    # Aggregate monthly averages
    df_monthly = df.groupby(['Year', 'Month']).mean(numeric_only=True).reset_index()
    df_monthly = df_monthly.dropna(subset=['Soil_Temperature'])
    df_monthly['Date'] = pd.to_datetime(df_monthly[['Year', 'Month']].assign(DAY=1))
    df_monthly = df_monthly.sort_values('Date').set_index('Date')

    if mode == 'wet_season':
        df_monthly['Month'] = df_monthly.index.month
        df_model = df_monthly[df_monthly['Month'].isin([12, 1, 2])]
        seasonal_period = 3
    elif mode == 'daily_wet_season':
        df_model = df[df['Month'].isin([12, 1, 2])].copy()
        df_model = df_model.set_index('Date')
        seasonal_period = 365
    else:
        df_model = df_monthly.copy()

    if exog_vars is None:
        exog_vars = []

    # Select Soil_Temperature and exogenous variables, drop rows with missing values
    columns_needed = ['Soil_Temperature'] + exog_vars
    df_model = df_model[columns_needed].dropna()

    print(f"\n--- Mode: {mode.upper()} | Data Points: {len(df_model)} ---")

    # Plot soil temperature
    plt.figure(figsize=(10, 4))
    plt.plot(df_model.index, df_model['Soil_Temperature'], marker='o')
    plt.title(f"Soil Temperature - {mode}")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Stationarity test
    adf_result = adfuller(df_model['Soil_Temperature'])
    print(f"ADF Statistic: {adf_result[0]:.3f}, p-value: {adf_result[1]:.3f} → {'Stationary' if adf_result[1] < 0.05 else 'Non-stationary'}")

    # Plot ACF and PACF
    plot_acf(df_model['Soil_Temperature'])
    plot_pacf(df_model['Soil_Temperature'])
    plt.show()

    # Train/test split
    split_index = int(len(df_model) * 0.6)
    train = df_model.iloc[:split_index]
    test = df_model.iloc[split_index:]

    train_endog = train['Soil_Temperature']
    test_endog = test['Soil_Temperature']

    if len(exog_vars) > 0:
        train_exog = train[exog_vars]
        test_exog = test[exog_vars]
    else:
        train_exog = None
        test_exog = None
    
    print("Train index:", train.index.min(), "→", train.index.max())
    print("Test index :", test.index.min(), "→", test.index.max())   


    # Auto ARIMA to find best SARIMA model with exogenous regressors
    auto_model = auto_arima(
        train_endog,
        exogenous=train_exog,
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

    order = auto_model.order
    seasonal_order = auto_model.seasonal_order

    # Fit SARIMAX with exogenous variables
    model = SARIMAX(train_endog, order=order, seasonal_order=seasonal_order, exog=train_exog)
    results = model.fit()
    print(results.summary())

    # Forecast with exogenous variables
    forecast = results.get_forecast(steps=len(test), exog=test_exog)
    forecast_mean = forecast.predicted_mean
    forecast_ci = forecast.conf_int()
    
    print("Actual (test_endog):")
    print(test_endog.head())

    print("Forecast (forecast_mean):")
    print(forecast_mean.head())

    # Plot forecast results
    plt.figure(figsize=(14, 6))
    plt.plot(train.index, train_endog, label='Train')
    plt.plot(test.index, test_endog, label='Actual', color='green')
    plt.plot(forecast_mean.index, forecast_mean, label='Forecast', color='red')
    plt.fill_between(forecast_ci.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color='pink', alpha=0.3)
    plt.title(f'SARIMA Forecast with Exogenous Variables - {mode}')
    plt.xlabel('Date')
    plt.ylabel('Soil Temperature (°C)')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Evaluation metrics
    mae = mean_absolute_error(test_endog, forecast_mean)
    mse = mean_squared_error(test_endog, forecast_mean)
    r2 = r2_score(test_endog, forecast_mean)
    print(f"Evaluation ({mode}):")
    print(f"MAE: {mae:.3f}")
    print(f"MSE: {mse:.3f}")
    print(f"R²: {r2:.3f}")

# Example exogenous variables available in your dataset:
exog_vars = ['T.Max', 'Radn','RHminT']

# Run forecasting in monthly mode with multiple exogenous variables
run_sarima_forecast(df_day, mode='monthly', seasonal_period=12, exog_vars=exog_vars)
