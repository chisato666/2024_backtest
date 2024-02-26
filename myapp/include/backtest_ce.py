

import pandas as pd
import ccxt
import talib

# Define the Chandelier Exit function
def chandelier_exit(high, low, close, period=1, multiplier=2):
    atr = talib.ATR(high, low, close, timeperiod=period)
    chandelier_long = high - multiplier * atr
    chandelier_short = low + multiplier * atr
    return chandelier_long, chandelier_short

# Initialize the exchange client (assuming Binance in this example)
exchange = ccxt.binance()

# Fetch historical data for BTC/USDT
symbol = 'BTC/USDT'
timeframe = '1d'  # Daily timeframe
limit = 100  # Number of candles to retrieve

ohlcvs = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
df = pd.DataFrame(ohlcvs, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Convert timestamp to datetime

# Calculate Chandelier Exit values
chandelier_long, chandelier_short = chandelier_exit(df['high'], df['low'], df['close'])

# Backtest the strategy
position = None
buy_price = 0
balance = 10000  # Initial balance in USDT
quantity = 0

for i in range(len(df)):
    close = df['close'][i]
    chandelier_long_value = chandelier_long[i]
    chandelier_short_value = chandelier_short[i]

    if position is None:
        if close > chandelier_long_value:
            position = 'LONG'
            buy_price = close
            quantity = balance / buy_price
            print(f"{i} Buy at {buy_price:.2f}  {df['timestamp'][i]}  {chandelier_long_value}")
    elif position == 'LONG':
        if close < chandelier_short_value:
            position = None
            sell_price = close
            balance = quantity * sell_price
            pnl = (sell_price - buy_price) / buy_price * 100
            print(f"Sell at {sell_price:.2f} | {df['timestamp'][i]} | PnL: {pnl:.2f}%  {chandelier_short_value}")

# Calculate overall PnL
initial_balance = 10000
final_balance = balance
pnl = (final_balance - initial_balance) / initial_balance * 100
print(f"Initial Balance: {initial_balance:.2f} USDT")
print(f"Final Balance: {final_balance:.2f} USDT")
print(f"Profit/Loss: {pnl:.2f}%")

# ```
#
# In this script, we define the `chandelier_exit` function that calculates the Chandelier Exit values based on the high, low, and close prices. We then fetch historical candlestick data for BTC/USDT from the Binance exchange, calculate the Chandelier Exit values using the `chandelier_exit` function, and proceed to backtest the strategy.
#
# During the backtest, we iterate through each candle and check if the current close price is above the Chandelier Long value. If it is, we enter a long position by buying BTC/USDT at the current price. If we are already in a long position and the close price falls below the Chandelier Short value, we exit the position by selling BTC/USDT at the current price.
#
# Finally, we calculate the overall profit/loss (PnL) by comparing the initial balance (assumed to be 10,000 USDT) with the final balance after the backtest.
#
# Please note that this is a simple example and does not include factors such as trading fees, slippage, or risk management. Additionally, it's important to thoroughly test and validate any trading strategy before using it with real funds.