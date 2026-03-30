import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import datetime
import ta
from pages.utils.ploty_fig import plotly_table,candlestick,RSI,MACD,Moving_Average,close_chart

st.set_page_config(page_title="Stock Analysis", page_icon="page_with_curl", layout="centered")

st.markdown(
    """
    <style>
    .metric-card {border:1px solid rgba(255,255,255,0.18); border-radius:14px; padding:12px 14px; background: rgba(255,255,255,0.04); margin-bottom: 12px; max-width: 220px; min-width: 160px;}
    .metric-card .title {font-size:0.78rem; color: rgba(255,255,255,0.75); margin-bottom: 6px;}
    .metric-card .value {font-size:1.7rem; font-weight: 700; color: white; line-height:1.1; word-break: break-word;}
    .metric-card .subtitle {font-size:0.75rem; color: rgba(255,255,255,0.68); margin-top: 4px;}
    .metric-card strong {font-weight: 700;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Stock Analysis")
col1, col2, col3 = st.columns(3)

today = datetime.date.today()
with col1:
    ticker = st.text_input("Enter Stock Symbol", value="AAPL")
with col2:
    start_date = st.date_input("Start Date", value=today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("End Date",datetime.date(today.year, today.month, today.day))

st.subheader(ticker.upper())

stock = yf.Ticker(ticker)

data = yf.download(ticker, start=start_date, end=end_date)

st.write(stock.info['longBusinessSummary'])
st.write(f"**Sector:** {stock.info['sector']}")
st.write(f"**Industry:** {stock.info['industry']}")
st.write(f"**website:** {stock.info['website']}")

st.subheader("Key Metrics")

# --- Key metrics cards (styled) ---

def _format_metric(val, precision=2, suffix="", abbreviate=False):
    # Handle singleton Series/Index values (yfinance can sometimes return these)
    if isinstance(val, (pd.Series, pd.Index)) and len(val) == 1:
        val = val.iloc[0]

    if val is None or pd.isna(val):
        return "—"

    if abbreviate and isinstance(val, (int, float)):
        # Abbreviate large numbers for readability (e.g., 1.2B)
        abs_val = abs(val)
        for factor, suffix_label in [(1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")]:
            if abs_val >= factor:
                formatted = f"{val / factor:,.{precision}f}{suffix_label}"
                return formatted

    if isinstance(val, int):
        return f"{val:,}{suffix}"
    if isinstance(val, float):
        return f"{val:,.{precision}f}{suffix}"
    return str(val)


def _metric_card(title: str, value: str, subtitle: str | None = None) -> str:
    subtitle_html = f"<div class='subtitle'>{subtitle}</div>" if subtitle else ""
    return f"""
    <div class='metric-card'>
        <div class='title'>{title}</div>
        <div class='value'>{value}</div>
        {subtitle_html}
    </div>
    """


def _empty_card() -> str:
    # Used to keep alignment in grid rows when we have fewer than 4 cards.
    return """
    <div class='metric-card' style='visibility:hidden;'>
        <div class='title'>&nbsp;</div>
        <div class='value'>&nbsp;</div>
    </div>
    """

volume = data['Volume'].iloc[-1] if not data.empty else None

# Daily change metrics (absolute and percentage)
def _to_scalar(val):
    # yfinance may return a single-value Series/DataFrame; normalize to scalar
    if isinstance(val, (pd.Series, pd.Index)) and len(val) == 1:
        return val.iloc[0]
    if hasattr(val, 'item'):
        try:
            return val.item()
        except Exception:
            pass
    return val


daily_change = None
daily_change_pct = None
if not data.empty and len(data) > 1:
    close = _to_scalar(data['Close'].iloc[-1])
    prev_close = _to_scalar(data['Close'].iloc[-2])
    try:
        daily_change = close - prev_close
    except Exception:
        daily_change = None

    if prev_close not in (0, None) and not pd.isna(prev_close):
        try:
            daily_change_pct = (daily_change / prev_close) * 100
        except Exception:
            daily_change_pct = None

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(_metric_card("Market Cap", _format_metric(stock.info.get('marketCap'), abbreviate=True)), unsafe_allow_html=True)
with col2:
    st.markdown(_metric_card("P/E Ratio", _format_metric(stock.info.get('trailingPE'), precision=2)), unsafe_allow_html=True)
with col3:
    st.markdown(_metric_card("Beta", _format_metric(stock.info.get('beta'), precision=2)), unsafe_allow_html=True)
with col4:
    st.markdown(_metric_card("Volume", _format_metric(volume, abbreviate=True)), unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(_metric_card("52W High", _format_metric(stock.info.get('fiftyTwoWeekHigh'))), unsafe_allow_html=True)
with col2:
    st.markdown(_metric_card("52W Low", _format_metric(stock.info.get('fiftyTwoWeekLow'))), unsafe_allow_html=True)
with col3:
    div_yield = stock.info.get('dividendYield')
    div_yield_pct = div_yield * 100 if (div_yield is not None and not pd.isna(div_yield)) else None
    st.markdown(_metric_card("Div Yield", _format_metric(div_yield_pct, precision=2, suffix="%")), unsafe_allow_html=True)
with col4:
    st.markdown(_metric_card("Target Price", _format_metric(stock.info.get('targetMeanPrice'))), unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(_metric_card("Daily Change", _format_metric(daily_change)), unsafe_allow_html=True)
with col2:
    st.markdown(_metric_card("Daily Change %", _format_metric(daily_change_pct, precision=2, suffix="%")), unsafe_allow_html=True)

st.subheader("Financial Ratios")
# Financial ratios in 2 columns for compact display
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        _metric_card("Quick Ratio", _format_metric(stock.info.get('quickRatio'), precision=3)),
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        _metric_card("Revenue / Share", _format_metric(stock.info.get('revenuePerShare'), precision=3)),
        unsafe_allow_html=True,
    )

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        _metric_card("Profit Margin", _format_metric(stock.info.get('profitMargins'), precision=4)),
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        _metric_card("Debt to Equity", _format_metric(stock.info.get('debtToEquity'), precision=3)),
        unsafe_allow_html=True,
    )

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        _metric_card("Return on Equity", _format_metric(stock.info.get('returnOnEquity'), precision=4)),
        unsafe_allow_html=True,
    )

# col1, col2, col3 = st.columns(3)
# daily_change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
# col1.metric("Daily Change", str(round(data['Close'].iloc[-1], 2)), str(round(daily_change, 2)))
st.write("")
st.write("")
st.write("")
st.subheader("Recent Price Data")
last_10_df =data.tail(10).sort_index(ascending=False).round(2)
fig_df = plotly_table(last_10_df)
st.plotly_chart(fig_df, use_container_width=True)

st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.subheader("Price & Indicators")
col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1,1,1,1,1,1,1,1,1])
num_period = '6mo'
with col1:
    if st.button("5D"):
        num_period = '5d'
with col2:
    if st.button("1M"):
        num_period = '1mo'
with col3:
    if st.button("6M"):
        num_period = '6mo'
# with col4:
#     if st.button("YTD"):
#         num_period = 'ytd'
with col4:
    if st.button("1Y"):
        num_period = '1y'
with col5:
    if st.button("5Y"):
        num_period = '5y'
with col6:
    if st.button("MAX"):
        num_period = 'max'


col1, col2, col3 = st.columns(3)
with col1:
    chart_type = st.selectbox("Select Chart Type", ["Line", "Candlestick"])
with col2:
    if chart_type == "Candlestick":
        indicators = st.selectbox('', ('RSI', 'MACD'))
    else:
        indicators = st.selectbox('', ('RSI', 'Moving Average', 'MACD'))

ticker_ = yf.Ticker(ticker)

# Use selected period for history requests and avoid redundant calls
selected_period = num_period if num_period else '6mo'
try:
    data1 = ticker_.history(period=selected_period)
    if data1 is None or data1.empty:
        st.warning(f"No historical data available for '{ticker}' using period '{selected_period}'.")
        st.stop()
except Exception as exc:
    st.error(f"Failed to load historical data for '{ticker}': {exc}")
    st.stop()

new_df1 = data1.copy()

if chart_type == "Candlestick" and indicators == 'RSI':
    st.plotly_chart(candlestick(data1,num_period),use_container_width=True)
    st.plotly_chart(RSI(data1,num_period),use_container_width=True)

if chart_type == "Candlestick" and indicators == 'MACD':
    st.plotly_chart(candlestick(data1,num_period),use_container_width=True)
    st.plotly_chart(MACD(data1,num_period),use_container_width=True)
if chart_type == "Line" and indicators == 'RSI':
    st.plotly_chart(close_chart(new_df1,num_period),use_container_width=True)
    st.plotly_chart(RSI(new_df1,num_period),use_container_width=True)
if chart_type == "Line" and indicators == 'Moving Average':
    st.plotly_chart(close_chart(new_df1,num_period),use_container_width=True)
    st.plotly_chart(Moving_Average(new_df1,num_period),use_container_width=True)
if chart_type == "Line" and indicators == 'MACD':
    st.plotly_chart(close_chart(new_df1,num_period),use_container_width=True)
    st.plotly_chart(MACD(new_df1,num_period),use_container_width=True)