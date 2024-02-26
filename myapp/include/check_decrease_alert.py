# To modify the code to check a list of symbols and send alerts only once per Kline (candlestick) using the MEXC exchange instead of Binance, you can update the `check_price_decrease()` function as follows:
#
# ```python
import requests
import time
from plyer import notification
from datetime import datetime
from django.utils import timezone
from myapp.models import PriceAlert


def check_price_decrease(symbol_list):
    intervals = ["Min15", "Min30", "Min60"]
    candle_limit = 2
    seen_candles = set()
    isAlert=False
    check_percent= 2

    while True:


        for symbol in symbol_list:
            url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}"

            for interval in intervals:
                params = {
                    "interval": interval,
                    "limit": candle_limit
                }

                response = requests.get(url, params=params)
                data = response.json()
                # Extract the close prices for the previous and current candles
                try:
                    previous_close = float(data['data']['close'][0])
                    current_close = float(data['data']['close'][1])
                    dt = datetime.now()
                    # Calculate the percentage decrease
                    percentage_decrease = (current_close - previous_close) / previous_close * 100
                    print(f" {dt} {symbol} | {percentage_decrease} | {interval}")

                    candle_id = f"{symbol}-{interval}-{data['data']['close'][0]}"  # Unique identifier for the candle

                    if candle_id not in seen_candles:
                        if percentage_decrease <= -check_percent:
                            isAlert=True
                            print("decreased found")
                            title = "Price Decrease Alert",
                            message = f"{dt} The {symbol} price has decreased by {round(percentage_decrease, 2)}% within the last {interval}.",

                        if percentage_decrease >= check_percent:
                            isAlert=True
                            print("increased found")
                            title = "Price Increase Alert",
                            message = f"{dt} The {symbol} price has increase by {round(percentage_decrease, 2)}% within the last {interval}.",

                        if isAlert:
                            print("IsAlert found")
                            alert = PriceAlert(
                                symbol=symbol,
                                interval=interval,
                                percentage_decrease=round(percentage_decrease, 2),
                                timestamp=dt
                            )
                            alert.save()
                            notification.notify(
                                title=title,
                                message=message,
                                timeout=10
                            )
                            seen_candles.add(candle_id)
                            isAlert=False




                except:
                    print(symbol," error")

        time.sleep(60)  # Sleep for 1 minute before checking again

# Define the symbols to monitor
# symbol_list = ["TARA_USDT", "ASTRA_USDT",'GFT_USDT','BTC_USDT','AUCTION_USDT','WEMIX_USDT','ARKM_USDT','CLORE_USDT']  # Add more symbols as needed
#
# # Start checking for price decreases
# check_price_decrease(symbol_list)



# ```
#
# In this updated code, we modified the URL to `https://www.mxc.com/open/api/v1/market/kline` to fetch the price data from the MEXC exchange. We also adjusted the response parsing to extract the close prices from the `data` dictionary.
#
# Additionally, we updated the symbol format to match the MEXC format. For example, "BTC_USDT" instead of "BTCUSDT". Make sure to provide the symbols in the correct format for monitoring.
#
# Again, make sure you have the `requests` and `plyer` libraries installed (`pip install requests plyer`) before running this updated code.