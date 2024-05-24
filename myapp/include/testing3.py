import time
import smtplib
from email.mime.text import MIMEText
import requests

# List of cryptocurrencies to monitor
crypto_list = ['BTC', 'ETH', 'LTC', 'XRP']

# Percentage change to trigger alert
percentage_change = 3

# Time period to monitor (in seconds)
time_period = 60  # 1 minute

# Email settings
sender_email = 'your_email@example.com'
recipient_email = 'recipient_email@example.com'
subject = 'Cryptocurrency Price Alert'
body = ''

def monitor_crypto():
    # Get initial prices
    initial_prices = {crypto: get_crypto_price(crypto) for crypto in crypto_list}

    while True:
        # Get current prices
        current_prices = {crypto: get_crypto_price(crypto) for crypto in crypto_list}

        # Check for price changes
        for crypto, initial_price in initial_prices.items():
            current_price = current_prices[crypto]
            percent_change = (current_price - initial_price) / initial_price * 100

            if abs(percent_change) >= percentage_change:
                direction = 'increased' if percent_change > 0 else 'decreased'
                body += f"{crypto} price has {direction} by {abs(percent_change):.2f}% in the last {time_period} seconds.\n"

        # Send email if there are any alerts
        if body:
            send_email(body)
            body = ''

        # Update initial prices
        initial_prices = current_prices

        # Wait for the next monitoring period
        time.sleep(time_period)

def get_crypto_price(crypto):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto.lower()}&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    return data[crypto.lower()]['usd']

def send_mail(msg):
    email_address = 'bitcontrol2018'
    email_password = 'xgvgtothglqfqhag'
    recipient_address = 'waishing1977@gmail.com'
    message = MIMEText('Increase 0.5%  on BTC/ETH')
    message['From'] = email_address
    message['To'] = recipient_address
    message['Subject'] = msg
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(email_address, email_password)
        smtp.send_message(message)

if __name__ == '__main__':
    #monitor_crypto()
    send_mail('this is testing')