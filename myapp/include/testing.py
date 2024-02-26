import pandas as pd
import numpy as np
import ta
import function
# Calculate EMA



symbols=['BTCUSDT','ETHUSDT','SOLUSDT','DOTUSDT','OPUSDT','AVAXUSDT','LINKUSDT','SANDUSDT','SUIUSDT']
start_date='01-01-2023'
end_date='12-05-2023'
periods=['1h','4h','1d']
sell_points=[]
buy_points=[]

symbol='BTCUSDT'
period='1d'
df=function.getdata(symbol,start_date,end_date,period)


df['ema'] = ta.trend.ema_indicator(df['Close'], window=14)

# Calculate RSI
df['rsi'] = ta.momentum.rsi(df['Close'], window=14)

# Calculate MACD
df['macd'] = ta.trend.macd_diff(df['Close'], window_slow=26, window_fast=12, window_sign=9)
# Calculate Support and Resistance levels (example)
df['support'] = df['Low'].rolling(window=20).min()
df['resistance'] = df['High'].rolling(window=20).max()

# Example buy condition
buy_condition = (df['ema'] > df['ema'].shift()) & (df['rsi'] < 30) & (df['macd'] > df['macd'].shift()) & (df['Close'] > df['support'])

buy_signals = df[buy_condition]



# Assuming you have historical price data in a DataFrame called 'df'

# Calculate Bollinger Bands
df['bb_upper'], df['bb_middle'], df['bb_lower'] = ta.volatility.bollinger_hband(df['Close']), ta.volatility.bollinger_mavg(df['Close']), ta.volatility.bollinger_lband(df['Close'])

# Calculate Fibonacci retracement levels
high = df['High'].max()
low = df['Low'].min()
fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
fib_values = [low + level * (high - low) for level in fib_levels]

# Calculate Stochastic Oscillator
df['stoch'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])

ichimoku_data = ta.trend.ichimoku_a(df['High'], df['Low'])
# df['tenkan_sen'] = ichimoku_data['tenkan_sen']
# df['kijun_sen'] = ichimoku_data['kijun_sen']
# df['cloud'] = ichimoku_data['cloud']
#
#
# # Define buy conditions
# buy_condition = (df['Close'] > df['bb_upper']) & (df['Close'] < fib_values[2]) & (df['stoch'] < 20) & (df['Close'] > df['tenkan_sen']) & (df['Close'] > df['kijun_sen']) & (df['Close'] > df['cloud'])

# Filter dataframe for buy signals
buy_signals = df[buy_condition]

# Analyze buy signals and make a decision based on your trading strategy


#print(ichimoku_data)

print(df)

# for symbol in symbols:
#     for period in periods:
#         df=function.getdata(symbol,start_date,end_date,period)
#         total,sell_points,buy_points=backtest_ema(df)
#         print(symbol,period,str(int(total)))