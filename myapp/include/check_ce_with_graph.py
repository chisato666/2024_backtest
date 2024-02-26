from datetime import datetime
import sys
import os
import math, requests
import numpy as np
import pandas as pd
import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
US_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import itertools
import matplotlib.dates as mpl_dates
import yfinance as yf
from finta import TA


def check_symbols_kline(symbol, interval, limit):
    url = f'https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval={interval}&limit={limit}'

    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data['data'], columns=['time', 'open', 'low', 'high', 'close'])

    df.index = pd.to_datetime(df.time, unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Hong_Kong'))

    # df.index = pd.to_datetime(df.index, unit='s')

    # df.set_index('time', inplace=True)

    return df

def load_historic_data(symbol, start_date_str, today_date_str, period, interval, prepost):
    try:
        df = yf.download(symbol, start=start_date_str, end=today_date_str, period=period, interval=interval, prepost=prepost)
        #  Add symbol
        df["Symbol"] = symbol
        df['high'] = df['High']
        df['low'] = df['Low']
        df['open'] = df['Open']
        df['close'] = df['Close']
        df = pd.DataFrame(df, columns = ['open','low', 'high','close'])
        #df.set_index('Time', inplace=True)
        #df.index = pd.to_datetime(df.index, unit='ms')

        return df
    except:
        print('Error loading stock data for ' + symbol)
        return None


def calculate_tis(df, atr_period):
    #  Calculate ATR
    atr = TA.ATR(df, period=atr_period)

    #  Calculate chandelier exits
    chandelier_info = TA.CHANDELIER(df, short_period=atr_period, long_period=atr_period, k=2)
    #  Add to price dataframe
    df = pd.concat([df, atr, chandelier_info], axis=1, ignore_index=False)
    return df


def calculate_signals(df):
    #  Long position
    df['enter_long'] = np.where((df['close'] > df['Short.']) & (df['close'].shift(1) <= df['Short.'].shift(1)), 1, 0)
    df['exit_long'] = np.where((df['close'] < df['Long.']) & (df['close'].shift(1) >= df['Long.'].shift(1)), 1, 0)

    #  Short position
    df['enter_short'] = np.where((df['close'] < df['Long.']) & (df['close'].shift(1) >= df['Long.'].shift(1)), 1, 0)
    df['exit_short'] = np.where((df['close'] > df['Short.']) & (df['close'].shift(1) <= df['Short.'].shift(1)), 1, 0)
    return df


def execute_strategy(df):
    close_prices = df['close'].to_numpy()
    enter_long = df['enter_long'].to_numpy()
    exit_long = df['exit_long'].to_numpy()
    enter_short = df['enter_short'].to_numpy()
    exit_short = df['exit_short'].to_numpy()

    last_long_entry_price = 0
    last_short_entry_price = 0
    long_entry_prices = []
    long_exit_prices = []
    short_entry_prices = []
    short_exit_prices = []
    hold_long = 0
    hold_short = 0
    for i in range(len(close_prices)):
        current_price = close_prices[i]

        #  Enter long
        if hold_long == 0 and enter_long[i] == 1:
            last_long_entry_price = current_price
            long_entry_prices.append(current_price)
            long_exit_prices.append(np.nan)
            hold_long = 1
        #  Exit long
        elif hold_long == 1 and exit_long[i] == 1:
            long_entry_prices.append(np.nan)
            long_exit_prices.append(current_price)
            hold_long = 0
        else:
            #  Neither entry nor exit
            long_entry_prices.append(np.nan)
            long_exit_prices.append(np.nan)
        #  Enter Short
        if hold_short == 0 and enter_short[i] == 1:
            last_short_entry_price = current_price
            short_entry_prices.append(current_price)
            short_exit_prices.append(np.nan)
            hold_short = 1
        #  Exit short
        elif hold_short == 1 and exit_short[i] == 1:
            short_entry_prices.append(np.nan)
            short_exit_prices.append(current_price)
            hold_short = 0
        else:
            #  Neither entry nor exit
            short_entry_prices.append(np.nan)
            short_exit_prices.append(np.nan)
    return long_entry_prices, long_exit_prices, short_entry_prices, short_exit_prices


def plot_graph(symbol, df, atr_period, long_entry_prices, long_exit_prices, short_entry_prices, short_exit_prices):
    fig = make_subplots(rows=2, cols=1, subplot_titles=['close', 'ATR'])
    #  Plot close price
    fig.add_trace(go.Line(x=df.index, y=df['close'], line=dict(color="blue", width=1), name="Close"), row=1, col=1)

    #  Chandelier lines
    fig.add_trace(go.Line(x=df.index, y=df['Long.'], line=dict(color="green", width=1), name="Chandelier Long"), row=1,
                  col=1)
    fig.add_trace(go.Line(x=df.index, y=df['Short.'], line=dict(color="red", width=1), name="Chandelier Short"), row=1,
                  col=1)

    #  Plot ATR
    fig.add_trace(go.Line(x=df.index, y=df[f"{atr_period} period ATR"], line=dict(color="blue", width=1), name="ATR"),
                  row=2, col=1)
    #  Long markers
    fig.add_trace(go.Scatter(x=df.index, y=long_entry_prices, marker_symbol="arrow-up", marker=dict(
        color='green', size=9
    ), mode='markers', name='Enter Long'))
    fig.add_trace(go.Scatter(x=df.index, y=long_exit_prices, marker_symbol="arrow-down", marker=dict(
        color='red', size=9
    ), mode='markers', name='Exit Long'))
    """ uncomment to see 
    #  Short markers
    fig.add_trace(go.Scatter(x=df.index + 8, y=short_entry_prices, marker_symbol="arrow-down", marker=dict(
        color='#8eb028',size=9
    ),mode='markers',name='Enter Short'))
    fig.add_trace(go.Scatter(x=df.index + 8, y=short_exit_prices, marker_symbol="arrow-up", marker=dict(
        color='#7b32a8', size=9
    ),mode='markers',name='Exit Short'))
    """

    fig.update_layout(
        title={'text': f"{symbol} with Chandelier Exits", 'x': 0.5},
        autosize=False,
        width=1000, height=800)
    fig.update_yaxes(range=[0, 1000000000], secondary_y=True)
    fig.update_yaxes(visible=False, secondary_y=True)  # hide range slider

    fig.show()
    fig.write_image('plot.png', format="png")


def calculate_profit(start_investment, long_entry_prices, long_exit_prices, short_entry_prices, short_exit_prices):
    hold_long, hold_short = 0, 0
    available_funds = start_investment
    cost_long, cost_short = 0, 0
    num_stocks_long, num_stocks_short = 0, 0
    proceeds_short = 0
    profit = 0
    for i in range(len(long_entry_prices)):
        #  Go long
        current_entry_price_long = long_entry_prices[i]
        current_exit_price_long = long_exit_prices[i]
        if not math.isnan(current_entry_price_long) and hold_long == 0:
            num_stocks_long = available_funds / current_entry_price_long
            cost_long = num_stocks_long * current_entry_price_long
            hold_long = 1
        elif hold_long == 1 and not math.isnan(current_exit_price_long):
            hold_long = 0
            proceeds = num_stocks_long * current_exit_price_long
            profit += proceeds - cost_long
        #  Go short
        current_entry_price_short = short_entry_prices[i]
        current_exit_price_short = short_exit_prices[i]
        if not math.isnan(current_entry_price_short) and hold_short == 0:
            num_stocks_short = available_funds / current_entry_price_short
            proceeds_short = num_stocks_short * current_entry_price_short
            hold_short = 1
        elif hold_short == 1 and not math.isnan(current_exit_price_short):
            hold_short = 0
            cost_short = num_stocks_short * current_exit_price_short
            profit += proceeds_short - cost_short
    return math.trunc(profit)


# MAIN
symbol = 'ETH-USD'
# Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
# Fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
period = '1mo'
interval = '1h'
atr_period = 1
prepost = True
today = datetime.date.today()
today_date_str = today.strftime("%Y-%m-%d")#  NOTE: 7 days is the max allowed
days = datetime.timedelta(7)
start_date = today - days
start_date_str = datetime.datetime.strftime(start_date, "%Y-%m-%d")#  Coins to download

df = load_historic_data(symbol, start_date_str, today_date_str, period, interval, prepost)

interval = "Min60"  # 1-hour candlestick data
limit = 400
symbol='TOMI_USDT'
df= check_symbols_kline(symbol, interval, limit)
start_investment = 100
df = df.tail(400)
#df.reset_index(inplace=True)
df = calculate_tis(df, atr_period)
df = calculate_signals(df)
df.to_csv('df.csv')
long_entry_prices, long_exit_prices, short_entry_prices, short_exit_prices = execute_strategy(df)
profit = calculate_profit(start_investment, long_entry_prices, long_exit_prices, short_entry_prices, short_exit_prices)
print(f"Total profit: {profit}")
plot_graph(symbol, df, atr_period, long_entry_prices, long_exit_prices, short_entry_prices, short_exit_prices)