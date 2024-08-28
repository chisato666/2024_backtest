# Sure, let's modify the script to fetch the data from the MEXC API instead of CoinGecko. Here's the updated script:
#
# ```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import function


def compare_columns(df1, col_a, df2, col_b):
    """
    Compares two columns from different dataframes and returns the count of rows where col_a > col_b.

    Args:
        df1 (pandas.DataFrame): The first dataframe.
        col_a (str): The name of the column to compare from df1.
        df2 (pandas.DataFrame): The second dataframe.
        col_b (str): The name of the column to compare from df2.

    Returns:
        int: The count of rows where col_a > col_b.
    """
    # Create a new dataframe with the columns to be compared
    df = pd.DataFrame({col_a: df1[col_a], col_b: df2[col_b]})

    # Compare the columns and get the count
    df['comparison'] = 0
    df.loc[df[col_a] > df[col_b], 'comparison'] = 1
    df.loc[df[col_a] <= df[col_b], 'comparison'] = -1
    return df['comparison'].sum()


# Define the cryptocurrencies to plot
cryptos = ["BTC_USDT", "ETH_USDT", "SOL_USDT"]

# Define the time interval (daily, hourly, or 4-hourly)
time_interval = "Day1"  # can be "daily", "hourly", or "4hourly"
periods=['1h','4h','Day1']
#     # time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1
limit=60
# Get the current date and the start date for the past month
today = datetime.now()
if time_interval == "Day1":
    start_date = today - timedelta(days=30)
elif time_interval == "Min60":
    start_date = today - timedelta(hours=720)  # 30 days
else:
    start_date = today - timedelta(hours=2880)  # 120 days

# Fetch the price change percentages for each cryptocurrency
data = {}
# for crypto in cryptos:
#     prices = []
#     dates = []
#     # url = f'https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval={interval}&limit={limit}'
#     # #     # time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1
#     #
#     # response = requests.get(url)
#     # data = response.json()
#     # df = []
#     # try:
#     #     df = pd.DataFrame(data['data'], columns=['time', 'open', 'low', 'high', 'close'])
#     #     df['ret'] = df.close.pct_change()
#     #     df.index = pd.to_datetime(df.time, unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Hong_Kong'))
#     # except Exception as error:
#     #     print(symbol, 'error ', error)
#
#     df = function.check_symbols_kline(crypto, time_interval, limit)

crypto_list=function.get_symbol_list()
print(crypto_list)


# symbol='BTC_USDT'
# interval = "Day1"  # 1-hour candlestick data
# limit=80
# count=0
# ema_list=[]
# add_list=[]

for symbol in crypto_list:
    df = function.check_symbols_kline(symbol, time_interval, limit)
    print(symbol,df['ret'].sum())

df = function.check_symbols_kline('BTC_USDT', time_interval, limit)
# Create a pandas DataFrame from the data
#df = pd.DataFrame(data, index=dates)
plt.figure(figsize=(14, 8))

plt.plot(df.index, df['ret'], label='BTC Price %')

df2 = function.check_symbols_kline('ETH_USDT', time_interval, limit)
plt.plot(df2.index, df2['ret'], label='ETH Price %')


df3 = function.check_symbols_kline('SOL_USDT', time_interval, limit)
plt.plot(df3.index, df3['ret'], label='SOL Price %')

df4 = function.check_symbols_kline('RNDR_USDT', time_interval, limit)
plt.plot(df4.index, df4['ret'], label='RNDR Price %')

print((df['ret'].sum(),df2['ret'].sum(),df3['ret'].sum(),df4['ret'].sum()))



#total=df['ret'].prod()
#print(total)
# Plot the graph
#df.plot(figsize=(12, 6))


plt.title(f"Cryptocurrency Price Change Percentages ({time_interval.capitalize()})")
plt.xlabel("Date")
plt.ylabel("Percentage Change")
plt.grid(True)
plt.legend()
#plt.show()
# ```
#
# The main changes are:
#
# 1. Changed the cryptocurrency tickers to match the MEXC format (e.g., "BTC", "ETH", "SOL").
# 2. Updated the API endpoints to fetch the data from the MEXC API instead of CoinGecko.
# 3. Adjusted the API response parsing to extract the `changeRate` data from the MEXC API response.
#
# To use this script, you'll need to have the same dependencies as the previous version:
#
# - `requests`: For making HTTP requests to the MEXC API.
# - `pandas`: For working with tabular data.
# - `matplotlib`: For creating the line graph.
#
# You can install these libraries using pip:
#
# ```
# pip install requests pandas matplotlib
# ```
#
# Now, you can run the script with different values for the `time_interval` variable to see the price change percentages for daily, hourly, or 4-hourly intervals from the MEXC API.