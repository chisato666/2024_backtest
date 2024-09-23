from binance.client import Client

# Replace with your own API key and secret
api_key = 'QsQNAgeZtTKkPNxEggcTloqiaQWCwbLUGUhMy4GvzbFb0GTLfKlnx0G7YIyhsvlT'
api_secret = '8rpoDvhzXjgvszHfDDTS2A4upThhI1mGrCWg1Tmcm6B9zJvnm3XXOgfy2pwJNVbl'



# Create a Binance client
client = Client(api_key, api_secret)


def get_asset_balance(symbol):
    """Get the free balance of a specific asset."""
    asset = symbol[:-4]
    account_info = client.get_account()
    for balance in account_info['balances']:
        if balance['asset'] == asset:
            return float(balance['free'])
    return 0.0


def get_symbol_info(symbol):
    """Get symbol information including step size and minimum quantity."""
    symbol_info = client.get_symbol_info(symbol)
    print(f"Symbol Info: {symbol_info}")  # Debug output
    return symbol_info


def calculate_valid_quantity(symbol, amount_to_sell):
    """Calculate the valid quantity for selling based on step size and minimum quantity."""
    symbol_info = get_symbol_info(symbol)
    step_size = float(next(filter(lambda x: x['filterType'] == 'LOT_SIZE', symbol_info['filters']))['stepSize'])
    min_qty = float(next(filter(lambda x: x['filterType'] == 'LOT_SIZE', symbol_info['filters']))['minQty'])

    # Round the amount to sell based on step size
    rounded_amount = round(amount_to_sell / step_size) * step_size

    print(f"Step Size: {step_size}, Min Qty: {min_qty}, Rounded Amount: {rounded_amount}")  # Debug output

    if rounded_amount < min_qty:
        raise ValueError(f"Quantity {rounded_amount} is less than minimum required {min_qty}.")

    return rounded_amount


def format_quantity(quantity, symbol):
    """Format the quantity to a string with the correct precision."""
    symbol_info = get_symbol_info(symbol)
    step_size = next(filter(lambda x: x['filterType'] == 'LOT_SIZE', symbol_info['filters']))['stepSize']

    # Calculate precision based on the step size
    if 'e' in step_size or 'E' in step_size:  # Check for scientific notation
        precision = abs(int(step_size.split('e')[-1]))
    else:
        precision = len(step_size.split('.')[1]) if '.' in step_size else 0

    print(f"Step Size: {step_size}, Precision: {precision}")  # Debug output

    if quantity < float(step_size):
        return f"{0:.{precision}f}"

    formatted_quantity = f"{quantity:.{precision}f}"
    print(f"Formatted quantity (before API call): {formatted_quantity}")  # Debug output
    return formatted_quantity


def place_market_order(symbol, usdt_amount):
    # Get the current price of the symbol
    ticker = client.get_symbol_ticker(symbol=symbol)
    current_price = float(ticker['price'])

    print(f"Current price for {symbol}: {current_price}")  # Debug output

    quantity = usdt_amount / current_price
    print(f"Calculated quantity (before validation): {quantity}")  # Debug output

    if quantity <= 0:
        print("Error: Calculated quantity is zero or negative.")
        return

    valid_quantity = calculate_valid_quantity(symbol, quantity)
    formatted_quantity = format_quantity(valid_quantity, symbol)

    print(f"Formatted quantity: {formatted_quantity}")  # Debug output

    try:
        order = client.order_market_buy(
            symbol=symbol,
            quantity=formatted_quantity
        )
        print("Market Order placed:")
        print(order)
    except Exception as e:
        print("An error occurred:", e)


# Example usage


symbol='BTCUSDT'
usdt_amount=20

ticker = client.get_symbol_ticker(symbol=symbol)
current_price = float(ticker['price'])

# Debug output for current price

# Calculate the quantity of the asset to buy
quantity = usdt_amount / current_price
valid_quantity = calculate_valid_quantity(symbol, quantity)

print(f"Current price for {symbol}: {current_price}  qty {quantity}  vq {valid_quantity}")

formatted_quantity = format_quantity(valid_quantity, symbol)

print(f" fq {formatted_quantity}")
# Example usage
place_market_order('BTCUSDT', 10)  # Market order for BTC
# place_limit_order('ETHUSDT', 20, 1500)  # Limit order for ETH at $1500
# sell_percentage('BTCUSDT', 25, 30000, 29000)  # Sell 25% of BTC with TP and SL