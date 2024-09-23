from binance.client import Client

# Replace with your own API key and secret
api_key = 'QsQNAgeZtTKkPNxEggcTloqiaQWCwbLUGUhMy4GvzbFb0GTLfKlnx0G7YIyhsvlT'
api_secret = '8rpoDvhzXjgvszHfDDTS2A4upThhI1mGrCWg1Tmcm6B9zJvnm3XXOgfy2pwJNVbl'

# Create a Binance client
client = Client(api_key, api_secret)

def get_asset_balance(symbol):
    """Get the free balance of a specific asset."""
    asset = symbol[:-4]  # Assuming the symbol is like 'BTCUSDT'
    account_info = client.get_account()
    for balance in account_info['balances']:
        if balance['asset'] == asset:
            return float(balance['free'])
    return 0.0

def calculate_valid_quantity(symbol, amount_to_sell):
    """Calculate the valid quantity for selling based on step size and minimum quantity."""
    symbol_info = client.get_symbol_info(symbol)
    step_size = float(next(filter(lambda x: x['filterType'] == 'LOT_SIZE', symbol_info['filters']))['stepSize'])
    min_qty = float(next(filter(lambda x: x['filterType'] == 'LOT_SIZE', symbol_info['filters']))['minQty'])

    # Round amount to sell based on step size
    rounded_amount = round(amount_to_sell / step_size) * step_size

    # Ensure the rounded amount meets the minimum quantity
    if rounded_amount < min_qty:
        raise ValueError(f"Quantity {rounded_amount} is less than minimum required {min_qty}.")

    return rounded_amount

def format_quantity(quantity, symbol):
    """Format the quantity to a string with the correct precision."""
    symbol_info = client.get_symbol_info(symbol)
    step_size = float(next(filter(lambda x: x['filterType'] == 'LOT_SIZE', symbol_info['filters']))['stepSize'])
    precision = len(str(step_size).split('.')[1]) if '.' in str(step_size) else 0
    return f"{quantity:.{precision}f}"

def place_market_order(symbol, usdt_amount):
    # Get the current price of the symbol
    ticker = client.get_symbol_ticker(symbol=symbol)
    current_price = float(ticker['price'])

    # Calculate the quantity of the asset to buy
    quantity = usdt_amount / current_price

    # Calculate valid quantity
    valid_quantity = calculate_valid_quantity(symbol, quantity)

    # Format quantity for API
    formatted_quantity = format_quantity(valid_quantity, symbol)

    # Place a market order
    try:
        order = client.order_market_buy(
            symbol=symbol,
            quantity=formatted_quantity
        )
        print("Market Order placed:")
        print(order)
    except Exception as e:
        print(f"An error occurred: {e} qty {quantity} vq {valid_quantity,formatted_quantity}")

def place_limit_order(symbol, usdt_amount, limit_price):
    # Get the current price of the symbol
    ticker = client.get_symbol_ticker(symbol=symbol)
    current_price = float(ticker['price'])

    # Calculate the quantity of the asset to buy
    quantity = usdt_amount / limit_price

    # Calculate valid quantity
    valid_quantity = calculate_valid_quantity(symbol, quantity)

    # Format quantity for API
    formatted_quantity = format_quantity(valid_quantity, symbol)

    # Place a limit order
    try:
        order = client.order_limit_buy(
            symbol=symbol,
            quantity=formatted_quantity,
            price=limit_price,
            timeInForce='GTC'  # Good till canceled
        )
        print("Limit Order placed:")
        print(order)
    except Exception as e:
        print(f"An error occurred: {e} qty {quantity} vq {valid_quantity,formatted_quantity}")

def sell_percentage(symbol, percentage, tp_price, sl_price):
    # Get the amount of the asset to sell
    asset_balance = get_asset_balance(symbol)
    amount_to_sell = asset_balance * (percentage / 100)

    # Calculate valid quantity
    valid_quantity = calculate_valid_quantity(symbol, amount_to_sell)

    # Format quantity for API
    formatted_quantity = format_quantity(valid_quantity, symbol)

    # Place a market sell order
    try:
        order = client.order_market_sell(
            symbol=symbol,
            quantity=formatted_quantity
        )
        print("Market Sell Order placed:")
        print(order)

        # Set Take Profit and Stop Loss
        if tp_price:
            client.create_order(
                symbol=symbol,
                side='SELL',
                type='LIMIT',
                quantity=formatted_quantity,
                price=tp_price,
                timeInForce='GTC'  # Good till canceled
            )
            print(f"Take Profit set at {tp_price}")

        if sl_price:
            client.create_order(
                symbol=symbol,
                side='SELL',
                type='STOP_MARKET',
                quantity=formatted_quantity,
                stopPrice=sl_price
            )
            print(f"Stop Loss set at {sl_price}")

    except Exception as e:
        print("An error occurred:", e)

# Example usage
place_market_order('BTCUSDT', 10)          # Market order for BTC
#place_limit_order('ETHUSDT', 20, 1500)     # Limit order for ETH at $1500
#sell_percentage('BTCUSDT', 25, 30000, 29000)  # Sell 25% of BTC with TP and SL