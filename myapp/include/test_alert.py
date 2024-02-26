import ccxt
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Configure email settings
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'chisato666@gmail.com'
SENDER_PASSWORD = 'socool'
RECIPIENT_EMAIL = 'chisato666@gmail.com'

# Connect to the exchange (Binance in this example)
exchange = ccxt.binance()

# Define the list of crypto pairs
crypto_pairs = ['BTC/USDT', 'ETH/USDT']

def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()

def check_ema_crossover(pair, timeframe):
    # Fetch historical OHLCV data
    now = datetime.now()
    start_time = now - timedelta(hours=10)  # Get data for the last 10 hours
    ohlcv = exchange.fetch_ohlcv(pair, timeframe=timeframe, since=int(start_time.timestamp()) * 1000)

    # Convert data to pandas DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # Calculate EMA
    df['ema_10'] = df['close'].ewm(span=10, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # Check EMA crossover
    if df['ema_10'].iloc[-2] < df['ema_50'].iloc[-2] and df['ema_10'].iloc[-1] > df['ema_50'].iloc[-1]:
        message = f"EMA 10 crossed above EMA 50 for {pair} on {timeframe} timeframe within the last 10 hours."
        send_email("EMA Crossover Alert", message)

# Check EMA crossover for each pair and timeframe
for pair in crypto_pairs:
    for timeframe in ['4h', '1d']:
        check_ema_crossover(pair, timeframe)