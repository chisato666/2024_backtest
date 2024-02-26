

import requests
from datetime import datetime, timedelta
import time
from plyer import notification

def check_price_decrease(symbol):
    url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}"
    interval = "Min60"
    candle_limit = 2
    seen_candles = set()
    params = {
        "interval": interval,
        "limit": candle_limit
    }

    response = requests.get(url, params=params)
    data = response.json()

    previous_close = float(data['data']['close'][0])
    current_close = float(data['data']['close'][1])

    print(data,previous_close,current_close)


def get_highest_price(symbol):
    url = f'https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval=Min60&limit=10'
    response = requests.get(url)
    data = response.json()
    highest_price = None
    for kline in data['data']['close']:
        print(str(kline))
        # timestamp = int(kline[0]) / 1000  # Convert milliseconds to seconds
        # kline_datetime = datetime.fromtimestamp(timestamp)
        # if kline_datetime >= datetime.now() - timedelta(hours=10):
        #     price = float(kline['close'])
        #     if highest_price is None or price > highest_price:
        #         highest_price = price_change_percentage
    return highest_price

# Example usage
# symbols = ['BTC_USDT', 'ETH_USDT']
# check_price_decrease("BTC_USDT")

dt = datetime.now()
dt = dt.strftime("%Y-%m-%d %H:%M:%S")
print(dt)
# for symbol in symbols:
#     highest_price = get_highest_price(symbol)
#     print(f"The highest price for symbol {symbol} in the past 10 hours is: ")



import pandas as pd
import matplotlib.pyplot as plt

# Load the historical price data into a DataFrame
df_btc = pd.read_csv('btcusdt.csv')

# Define the strategy parameters
ema_short_period = 10
ema_long_period = 30

# Calculate the EMA values
df_btc['EMA_short'] = df_btc['Close'].ewm(span=ema_short_period, adjust=False).mean()
df_btc['EMA_long'] = df_btc['Close'].ewm(span=ema_long_period, adjust=False).mean()

# Initialize variables
btc_position = False
buy_points = []
sell_points = []

# Backtest the strategy
for i in range(1, len(df_btc)):
    if not btc_position and df_btc['EMA_short'][i] > df_btc['EMA_long'][i] and df_btc['EMA_short'][i-1] < df_btc['EMA_long'][i-1]:
        btc_position = True
        buy_points.append((df_btc['Timestamp'][i], df_btc['Close'][i]))
    elif btc_position and df_btc['EMA_short'][i] < df_btc['EMA_long'][i] and df_btc['EMA_short'][i-1] > df_btc['EMA_long'][i-1]:
        btc_position = False
        sell_points.append((df_btc['Timestamp'][i], df_btc['Close'][i]))

# Plot the BTC price and buy/sell points
plt.plot(df_btc['Timestamp'], df_btc['Close'], label='BTC Price')
plt.scatter(*zip(*buy_points), color='green', label='Buy')
plt.scatter(*zip(*sell_points), color='red', label='Sell')
plt.xlabel('Date/Time')
plt.ylabel('BTC Price (USDT)')
plt.title('BTC Price with Buy/Sell Points')
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.show()


import pandas as pd

# Load the historical price data into a DataFrame
df_btc = pd.read_csv('btcusdt.csv')
df_eth = pd.read_csv('ethusdt.csv')

# Define the strategy parameters
ema_short_period = 10
ema_long_period = 30
stop_loss_percentage = 0.1

# Calculate the EMA values
df_btc['EMA_short'] = df_btc['Close'].ewm(span=ema_short_period, adjust=False).mean()
df_btc['EMA_long'] = df_btc['Close'].ewm(span=ema_long_period, adjust=False).mean()
df_eth['EMA_short'] = df_eth['Close'].ewm(span=ema_short_period, adjust=False).mean()
df_eth['EMA_long'] = df_eth['Close'].ewm(span=ema_long_period, adjust=False).mean()

# Initialize variables
btc_position = False
eth_position = False
btc_buy_price = 0
eth_buy_price = 0
btc_stop_loss = 0
eth_stop_loss = 0

# Backtest the strategy
for i in range(1, max(len(df_btc), len(df_eth))):
    # BTCUSDT
    if i < len(df_btc):
        if not btc_position and df_btc['EMA_short'][i] > df_btc['EMA_long'][i] and df_btc['EMA_short'][i-1] < df_btc['EMA_long'][i-1]:
            btc_position = True
            btc_buy_price = df_btc['Close'][i]
            btc_stop_loss = btc_buy_price * (1 - stop_loss_percentage)
        elif btc_position and df_btc['Close'][i] > df_btc['Close'][i-1]:
            btc_stop_loss = df_btc['Close'][i] * (1 - stop_loss_percentage)
        elif btc_position and df_btc['Close'][i] <= btc_stop_loss:
            btc_position = False
            btc_sell_price = df_btc['Close'][i]
            btc_profit = btc_sell_price - btc_buy_price
            print(f"BTCUSDT - Buy at {btc_buy_price:.2f}, Sell at {btc_sell_price:.2f}, Profit: {btc_profit:.2f}")

    # ETHUSDT
    if i < len(df_eth):
        if not eth_position and df_eth['EMA_short'][i] > df_eth['EMA_long'][i] and df_eth['EMA_short'][i-1] < df_eth['EMA_long'][i-1]:
            eth_position = True
            eth_buy_price = df_eth['Close'][i]
            eth_stop_loss = eth_buy_price * (1 - stop_loss_percentage)
        elif eth_position and df_eth['Close'][i] > df_eth['Close'][i-1]:
            eth_stop_loss = df_eth['Close'][i] * (1 - stop_loss_percentage)
        elif eth_position and df_eth['Close'][i] <= eth_stop_loss:
            eth_position = False
            eth_sell_price = df_eth['Close'][i]
            eth_profit = eth_sell_price - eth_buy_price
            print(f"ETHUSDT - Buy at {eth_buy_price:.2f}, Sell at {eth_sell_price:.2f}, Profit: {eth_profit:.2f}")



import pandas as pd
import matplotlib.pyplot as plt
import talib

# Load the historical price data into a DataFrame
df_btc = pd.read_csv('btcusdt.csv')

# Define the strategy parameters
ema_short_period = 10
ema_long_period = 30
rsi_period = 14

# Calculate the EMA values
df_btc['EMA_short'] = df_btc['Close'].ewm(span=ema_short_period, adjust=False).mean()
df_btc['EMA_long'] = df_btc['Close'].ewm(span=ema_long_period, adjust=False).mean()

# Calculate the RSI values
df_btc['RSI'] = talib.RSI(df_btc['Close'], timeperiod=rsi_period)

# Initialize variables
btc_position = False
buy_points = []
sell_points = []

# Backtest the strategy
for i in range(1, len(df_btc)):
    if not btc_position and df_btc['EMA_short'][i] > df_btc['EMA_long'][i] and df_btc['EMA_short'][i-1] < df_btc['EMA_long'][i-1] and df_btc['RSI'][i] < 30:
        btc_position = True
        buy_points.append((df_btc['Timestamp'][i], df_btc['Close'][i]))
    elif btc_position and df_btc['EMA_short'][i] < df_btc['EMA_long'][i] and df_btc['EMA_short'][i-1] > df_btc['EMA_long'][i-1]:
        btc_position = False
        sell_points.append((df_btc['Timestamp'][i], df_btc['Close'][i]))

# Plot the BTC price and buy/sell points
plt.plot(df_btc['Timestamp'], df_btc['Close'], label='BTC Price')
plt.scatter(*zip(*buy_points), color='green', label='Buy')
plt.scatter(*zip(*sell_points), color='red', label='Sell')
plt.xlabel('Date/Time')
plt.ylabel('BTC Price (USDT)')
plt.title('BTC Price with Buy/Sell Points')
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

import pandas as pd
import ta

# Assuming you have historical price data in a DataFrame called 'df'

# Calculate Bollinger Bands
df['bb_upper'], df['bb_middle'], df['bb_lower'] = ta.volatility.bollinger_hband(df['close']), ta.volatility.bollinger_mavg(df['close']), ta.volatility.bollinger_lband(df['close'])

# Calculate Fibonacci retracement levels
high = df['high'].max()
low = df['low'].min()
fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
fib_values = [low + level * (high - low) for level in fib_levels]

# Calculate Stochastic Oscillator
df['stoch'] = ta.momentum.stoch(df['high'], df['low'], df['close'])

# Calculate Ichimoku Cloud
df['tenkan_sen'], df['kijun_sen'], span_a, span_b, df['cloud'] = ta.trend.ichimoku(df['High'], df['Low'])

# Define buy conditions
#buy_condition = (df['Close'] > df['bb_upper']) & (df['Close'] < fib_values[2]) & (df['stoch'] < 20) & (df['Close'] > df['tenkan_sen']) & (df['Close'] > df['kijun_sen']) & (df['Close'] > df['cloud'])

# Filter dataframe for buy signals
buy_signals = df[buy_condition]

# Analyze buy signals and make a decision based on your trading strategy