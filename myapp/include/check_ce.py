# Apologies for the oversight. You're right that the condition for entering a long position was incorrect. To avoid entering trades on every data point, we need to incorporate additional logic to track the current position and ensure that trades are only executed when the position changes. Here's an updated version of the code that addresses this issue:
#
# ```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import function


# Define Chandelier Exit strategy
def chandelier_exit(df, period=22, multiplier=3):
    high_max = df['high'].rolling(period).max()
    atr = df['high'].rolling(period).max() - df['low'].rolling(period).min()
    long_exit = high_max - multiplier * atr
    short_exit = df['low'].rolling(period).min() + multiplier * atr
    return long_exit, short_exit

# Define backtesting function
def backtest_chandelier_exit(df, period=22, multiplier=3):
    long_exit, short_exit = chandelier_exit(df, period, multiplier)
    trades = []
    position = None
    for i in range(len(df)):
        if position is None:
            if df['close'][i] > long_exit[i]:
                position = 'Long'
                entry_price = df['close'][i]
        elif position == 'Long':
            if df['close'][i] < short_exit[i]:
                exit_price = df['close'][i]
                profit = exit_price - entry_price
                trades.append(profit)
                position = None
    return trades

# Load BTCUSDT data (assuming you have a CSV file named 'btcusdt.csv' with columns 'Timestamp', 'Open', 'High', 'Low', 'Close')

symbol = "BTC_USDT"
interval = "Min60"  # 1-hour candlestick data
limit=40

data=function.check_symbols_kline(symbol,interval,limit)

df= pd.DataFrame(data)
df.set_index('time',inplace=True)
df.index = pd.to_datetime(df.index, unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Hong_Kong'))
df['time'] = pd.to_datetime(df.index, unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Hong_Kong'))

# Convert Timestamp to datetime
#df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

# Perform backtest
trades = backtest_chandelier_exit(df)

# Calculate total profit return
total_profit = np.sum(trades)

# Print results
print(f"Total trades: {len(trades)}")
print(f"Total profit return: {total_profit:.2f} USDT")
long_exit, short_exit=chandelier_exit(df)
# Plotting the Chandelier Exit and BTCUSDT Close price
plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['close'], label='BTCUSDT Close')
plt.plot(df['time'], long_exit, label='Long Exit')
plt.plot(df['time'], short_exit, label='Short Exit')
plt.title('Chandelier Exit Strategy - BTCUSDT')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()
# ```
#
# In this updated code, the condition for entering a long position has been modified. Now, it only triggers a trade if there is no existing position and the current close price is higher than the long exit level. This ensures that trades are only executed when the position changes from None to Long.
#
# Please note that this code assumes that you are trading only in one direction (long positions) and does not consider factors such as transaction fees, slippage, or position sizing. It provides a basic framework for backtesting the Chandelier Exit strategy, and you may need to customize it further based on your specific requirements.