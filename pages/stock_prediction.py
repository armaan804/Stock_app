import streamlit as st
from pages.utils.model_train import get_data, stationary_check, get_rolling_mean, get_differencing_order, fit_model, evaluate_model, scaling, get_forecast, inverse_scaling
from pages.utils.ploty_fig import plotly_table,Moving_average_forecast
import pandas as pd

st.set_page_config(page_title="Stock Prediction", page_icon="chart_with_upwards_trend", layout="wide")

st.title("Stock Price Prediction")

col1, col2,col3 = st.columns(3)
with col1:
    ticker = st.text_input("Enter Stock Symbol", value="AAPL")


accuracy_pct = 0.0
st.subheader('Predicting Next 30 Days Stock Price: ' + ticker)

close_price = get_data(ticker)
rollling_price = get_rolling_mean(close_price)
differencing_order = get_differencing_order(rollling_price)
scaled_data, scaler = scaling(rollling_price)
rmse, accuracy_pct = evaluate_model(rollling_price, differencing_order)
st.write(f"Model Accuracy: {accuracy_pct}%")

forecast = get_forecast(scaled_data, differencing_order)
forecast['Close'] = inverse_scaling(forecast['Close'], scaler)

st.write('Forecast Data (Next 30 days)')
fig_tail = plotly_table(forecast.sort_index(ascending=True).round(3))
fig_tail.update_layout(height=220)
st.plotly_chart(fig_tail, use_container_width=True)

forecast = pd.concat([rollling_price, forecast])

st.plotly_chart(Moving_average_forecast(forecast.iloc[150:],tic=ticker),use_container_width=True)
