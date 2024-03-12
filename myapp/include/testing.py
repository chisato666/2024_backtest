import requests

def get_market_cap_rank(crypto):
    api_key = '496c4b12-9483-415b-8701-edaddbd510c6'  # Replace with your CoinMarketCap API key
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=100&convert=USD"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if 'data' in data:
        for coin in data['data']:
            if coin['symbol'].lower() == crypto.lower():
                return coin['cmc_rank']
    return None

crypto_list = ['btc', 'eth']

market_cap_rankings = {}

for crypto in crypto_list:
    rank = get_market_cap_rank(crypto)
    if rank is not None:
        market_cap_rankings[crypto] = rank

sorted_rankings = sorted(market_cap_rankings.items(), key=lambda x: x[1])

for crypto, rank in sorted_rankings:
    print(f"{crypto}: Rank {rank}")