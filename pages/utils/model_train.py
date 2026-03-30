import yfinance as yf
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

def get_data(ticker):
    stock = yf.download(ticker,start='2025-01-01')
    return stock['Close']

def stationary_check(close_price):
    adf_test = adfuller(close_price)
    p_value = round(adf_test[1], 3)
    return p_value

def get_rolling_mean(close_price):
    return close_price.rolling(window=5).mean().dropna()

def get_differencing_order(close_price):
    p_value = stationary_check(close_price)
    d = 0
    while p_value > 0.05 and d < 5:
        close_price = close_price.diff().dropna()
        p_value = stationary_check(close_price)
        d += 1
    return d

def fit_model(data, differencing_order):
    model = ARIMA(data, order=(5, differencing_order, 5))
    model_fit = model.fit()

    forecast_steps = 30
    forecast = model_fit.get_forecast(steps=forecast_steps)

    predictions = forecast.predicted_mean
    return predictions

def evaluate_model(original_price, differencing_order):
    train_data, test_data = original_price[:-30], original_price[-30:]
    predictions = fit_model(train_data, differencing_order)

    predictions = pd.Series(
        predictions.values[:len(test_data)],
        index=test_data.index
    )

    rmse = np.sqrt(mean_squared_error(test_data, predictions))

    # Use original scale for meaningful percentage error
    mape = mean_absolute_percentage_error(test_data, predictions) * 100
    accuracy_percent = max(0.0, round(100 - mape, 2))

    return round(rmse, 2), accuracy_percent

def scaling(close_price):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(np.array(close_price).reshape(-1, 1))
    return scaled_data, scaler

def get_forecast(original_price,differencing_order):
    predictions = fit_model(original_price, differencing_order)
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=29)).strftime("%Y-%m-%d")
    forcast_index = pd.date_range(start=start_date, end=end_date, freq='D')
    forecasst_df = pd.DataFrame(predictions, index=forcast_index, columns=['Close'])
    return forecasst_df

def inverse_scaling(scaled_data, scaler):
    return scaler.inverse_transform(np.array(scaled_data).reshape(-1, 1))
