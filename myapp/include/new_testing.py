import yfinance as yf
import requests


def get_crypto_list():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)

    if response.status_code == 200:
        crypto_list = response.json()
        valid_crypto_list = []

        for crypto in crypto_list:
            symbol = crypto['symbol'].upper()
            try:
                data = yf.download(symbol + "-USD", period="1d")
                if len(data) > 0:
                    valid_crypto_list.append(symbol)
            except Exception:
                pass

        return valid_crypto_list
    else:
        print("Error retrieving crypto list. Status code:", response.status_code)
        return []


def check_ema_crossover(crypto_list, start_date, end_date):
    result = []

    for crypto in crypto_list:
        try:
            data = yf.download(crypto + "-USD", start=start_date, end=end_date)

            if len(data) >= 50:  # Ensure enough data points for calculations
                ema_10 = data['Close'].ewm(span=10, adjust=False).mean()
                ema_50 = data['Close'].ewm(span=50, adjust=False).mean()

                for i in range(1, len(data)):
                    if ema_10.iloc[i - 1] < ema_50.iloc[i - 1] and ema_10.iloc[i] > ema_50.iloc[i]:
                        result.append(crypto)
                        break
        except Exception:
            pass

    return result


# Example usage
all_crypto_list = get_crypto_list()
print(all_crypto_list)
# start_date = '2024-02-01'  # Start date of the period
# end_date = '2024-02-22'  # End date of the period
#
# crossed_cryptos = check_ema_crossover(all_crypto_list, start_date, end_date)
# print("Cryptocurrencies that crossed above the 50-day EMA:")
# print(crossed_cryptos)