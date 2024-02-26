# Certainly! Here's a Python script that checks if the highest price of BTC/USDT in the last 24 hours occurred within the 1-hour candlesticks of the last 5 hours:
#
# ```python
import ccxt

# Initialize the exchange client (assuming Binance in this example)
exchange = ccxt.mexc()



# Fetch 1-hour candlestick data for BTC/USDT
symbols = ['ASTRA/USDT','LUNA/USDT']
timeframe = '1h'
limit = 5  # Number of candles to retrieve

for symbol in symbols:
    ohlcvs = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    closes = [candle[4] for candle in ohlcvs]  # Extract closing prices

    # Fetch 24-hour high price for BTC/USDT
    ticker = exchange.fetch_ticker(symbol)
    high_24h = ticker['high']

    # Check if highest price in the last 24 hours occurred within the last 5 hours
    if max(closes) == high_24h:
        print(f" {symbol} {high_24h} {max(closes)} The highest price in the last 24 hours occurred within the last 5 hours.")
    else:
        print(f" {symbol} {high_24h} {max(closes)} The highest price in the last 24 hours did not occur within the last 5 hours.")
# ```
#
# In this script, we use the CCXT library to fetch the 1-hour candlestick data for BTC/USDT from the Binance exchange. We extract the closing prices from the retrieved candlestick data and store them in the `closes` list.
#
# We then fetch the current ticker data for BTC/USDT to obtain the 24-hour high price. The `fetch_ticker` method retrieves the ticker information, and we extract the high price using the `'high'` key.
#
# Finally, we compare the 24-hour high price with the maximum value in the `closes` list. If they are equal, it means the highest price in the last 24 hours occurred within the last 5 hours.
#
# Please note that you'll need to have the CCXT library installed (`pip install ccxt`) and have valid API credentials for the Binance exchange to run this script.