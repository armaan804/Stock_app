import plotly.graph_objects as go
import dateutil
import pandas as pd
import datetime

def plotly_table(df):
    # Table colors optimized for dark background
    header_color = 'rgba(255,255,255,0.14)'
    row_colors = ['rgba(255,255,255,0.04)', 'rgba(255,255,255,0.08)']

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Index</b>"] + [f"<b>{col}</b>" for col in df.columns],
            fill_color=header_color,
            align='center',
            font=dict(color='white', size=14),
            height=40,
            line_color='rgba(255,255,255,0.25)',
            line_width=1
        ),
        cells=dict(
            values=[df.index.tolist()] + [df[col].tolist() for col in df.columns],
            fill_color=[row_colors * (len(df) // 2 + 1)],
            align='left',
            font=dict(color='white', size=13),
            height=35,
            line_color='rgba(255,255,255,0.2)',
            line_width=1
        )
    )])

    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(255,255,255,0.04)',
        paper_bgcolor='rgba(255,255,255,0.04)',
        font=dict(color='white')
    )

    return fig

def filter_data(df, num_period):
    if(num_period == '5d'):
        data = df.index[-1] + dateutil.relativedelta.relativedelta(days=-5)
    elif(num_period == '1mo'):
        data = df.index[-1] + dateutil.relativedelta.relativedelta(months=-1)
    elif(num_period == '3mo'):
        data = df.index[-1] + dateutil.relativedelta.relativedelta(months=-3)
    elif(num_period == '6mo'):
        data = df.index[-1] + dateutil.relativedelta.relativedelta(months=-6)
    elif(num_period == '1y'):
        data = df.index[-1] + dateutil.relativedelta.relativedelta(years=-1)
    elif(num_period == '5y'):
        data = df.index[-1] + dateutil.relativedelta.relativedelta(years=-5)
    else:
        data = df.index[0]

    filtered_df = df.reset_index()[df.reset_index()['Date'] > data]
    return filtered_df

def close_chart(df, num_period=False):
    if num_period:
        df = filter_data(df, num_period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Open'], mode='lines', name='Open Price', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price', line=dict(color='#ff7f0e', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['High'], mode='lines', name='High Price', line=dict(color='#2ca02c', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Low'], mode='lines', name='Low Price', line=dict(color='#d62728', width=2)))

    # last close reference line
    fig.add_hline(
        y=df['Close'].iloc[-1],
        line_dash='dash',
        line_color='rgba(255,255,255,0.6)',
        annotation_text='Last Close',
        annotation_position='top right',
        annotation_font=dict(color='white')
    )

    fig.update_xaxes(rangeslider_visible=True)

    fig.update_layout(
        height=500,
        margin=dict(l=0, r=20, t=20, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(yanchor="top", xanchor="right", font=dict(color='white'), bgcolor='rgba(0,0,0,0)'),
        font=dict(color='white')
    )

    fig.update_xaxes(
        title_text="Date",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )
    fig.update_yaxes(
        title_text="Price",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )

    return fig

def candlestick(df, num_period):

    df = filter_data(df, num_period)
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'
    ))

    # last close reference line
    fig.add_hline(
        y=df['Close'].iloc[-1],
        line_dash='dash',
        line_color='rgba(255,255,255,0.6)',
        annotation_text='Last Close',
        annotation_position='top right',
        annotation_font=dict(color='white')
    )

    fig.update_layout(
        height=500,
        margin=dict(l=0, r=20, t=20, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(color='white')
    )

    fig.update_xaxes(
        title_text="Date",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )
    fig.update_yaxes(
        title_text="Price",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )

    return fig

def RSI(df, num_period):

    # df.index = pd.to_datetime(df.index)

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df = filter_data(df, num_period)
    # df = df.dropna()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI',marker_color='orange', line=dict(color='orange', width=2)))

    fig.add_trace(go.Scatter(x=df['Date'], y=[70]*len(df), name='Overbought', line=dict(width=2,color='red' ,dash='dash')))
    fig.add_trace(go.Scatter(x=df['Date'], y=[30]*len(df),fill = 'tonexty', name='Oversold',marker_color='green', line=dict(width=2,color='green' ,dash='dash')))

    fig.update_layout(
        yaxis_range=[0, 100],
        height=200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="right", x=1, font=dict(color='white'), bgcolor='rgba(0,0,0,0)')
    )

    fig.update_xaxes(
        title_text="Date",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )
    fig.update_yaxes(
        title_text="RSI",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )

    return fig

def Moving_Average(df, num_period):
    df = filter_data(df, num_period)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Open'], mode='lines', name='Open Price', line=dict(color='orange', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['High'], mode='lines', name='High Price', line=dict(color='green', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Low'], mode='lines', name='Low Price', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], mode='lines', name='20-Day MA', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], mode='lines', name='50-Day MA', line=dict(color='green', width=2)))

    fig.update_layout(
        showlegend=True,
        height=500,
        margin=dict(l=0, r=20, t=20, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(font=dict(color='white'), bgcolor='rgba(0,0,0,0)')
    )

    fig.update_xaxes(
        title_text="Date",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )
    fig.update_yaxes(
        title_text="Price",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )
    return fig

def MACD(df, num_period='1y'):
    df = filter_data(df, num_period)

    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], mode='lines', name='MACD', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Signal'], mode='lines', name='Signal Line', line=dict(color='orange', width=2)))

    c= ['green' if macd > signal else 'red' for macd, signal in zip(df['MACD'], df['Signal'])]

    fig.update_layout(
        showlegend=True,
        height=300,
        margin=dict(l=0, r=20, t=20, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(font=dict(color='white'), bgcolor='rgba(0,0,0,0)')
    )

    fig.update_xaxes(
        title_text="Date",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )
    fig.update_yaxes(
        title_text="MACD",
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        automargin=True,
        showgrid=True,
        gridcolor='rgba(255,255,255,0.12)',
        linecolor='rgba(255,255,255,0.5)',
        mirror=True
    )
    return fig


def Moving_average_forecast(forecast, tic, forecast_days=30):
    # Expect `forecast` to be a DataFrame with a datetime index and a column named 'Close'
    # The last `forecast_days` rows are treated as the forecasted values.
    hist = forecast.iloc[:-forecast_days]
    fut = forecast.iloc[-forecast_days:]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist[tic], mode='lines', name='Historical Close', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=fut.index, y=fut['Close'], mode='lines', name='Forecasted Close', line=dict(color='red', width=2)))

    fig.update_xaxes(rangeslider_visible=True)

    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), legend=dict(yanchor="top", xanchor="right", font=dict(color='white'), bgcolor='rgba(0,0,0,0)'))
    return fig