import pandas as pd
import talib
import ta

import ccxt
import time
import requests

from binance.client import Client
from datetime import datetime

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import config

import mysql.connector

database = "waishing_binance"
host = "hkwaishing.com"
user = "waishing_trendy"
passwd = "Socool666"

# Replace with your Binance API key


# Connect to PostgreSQL database
# mydb = mysql.connector.connect(
#     host=host,
#     user=user,
#     passwd=passwd,
#     database=database
# )

#db = mydb.cursor()

global last_email_time , last_alert_timestamps

last_alert_timestamps = {}

exchange = ccxt.binance()
api_key = config.api_key
api_secret = config.api_secret

# Create a Binance client object
client = Client(api_key, api_secret)
last_email_time = 0


def getdata(symbol,start_date,end_date,period):

    if (period !=""):
        df = pd.DataFrame(client.get_historical_klines(symbol,period,start_date,end_date))
    else:
        df = pd.DataFrame(client.get_historical_klines(symbol,start_date,end_date))
    df = df.iloc[:,:6]
    df.columns = ['Time','Open','High','Low','Close','Volume']
    df.set_index('Time',inplace=True)
    df.index = pd.to_datetime(df.index,unit='ms')
    df= df.astype(float)

    df['ret']= df.Close.pct_change()
    #df.ret.plot(kind='hist', bins=100)
    df['price']=df.Open.shift(-1)
    df['SMA200']=df.Close.rolling(200).mean()

    return df



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


def get_current_price(symbol):
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {'symbol': symbol}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data['price'])


def get_24hr_high(symbol):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {'symbol': symbol}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data['highPrice']), float(data['lowPrice'])

def get_24hr_high2(symbol):
    url = "https://contract.mexc.com/api/v1/contract/ticker/"
    params = {'symbol': symbol}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data['data']['high24Price']), float(data['data']['lower24Price'])


def check_percent_change(symbol, threshold):
    # Define the percentage increase threshold
    isAlert = False
    max_threshold = threshold
    min_threshold = -threshold
    # Get the current price of the cryptocurrency
    ticker = client.get_ticker(symbol=symbol)
    price = float(ticker['lastPrice'])
    dt = datetime.now()
    # Get the price 1 minute ago
    klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE)
    prev_price = float(klines[-2][4])

    # Calculate the percentage increase
    percent_increase = (price - prev_price) / prev_price * 100

    # print(dt, price, prev_price, percent_increase)
    # Check if the percentage increase is above the threshold
    if (percent_increase >= max_threshold):
        isAlert = True
        message = (f"ALERT: {symbol} price {price} increased by {percent_increase:.2f}% within 1 minute")
    elif (percent_increase <= min_threshold):
        isAlert = True
        message = (f"ALERT: {symbol} price {price} decreased by {percent_increase:.2f}% within 1 minute")
    else:
        message = ""
        isAlert = False

    return isAlert, message




def get_macd(symbol, interval):
    ohlcv = exchange.fetch_ohlcv(symbol, interval, limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    macd, signal, hist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return macd, signal, hist


def check_alert():
    df, ma = get_price_data()
    macd, signal, hist = get_macd()
    last_macd = macd.iloc[-1]
    last_signal = signal.iloc[-1]
    if df['close'][-1] > ma.iloc[-1] and last_macd > last_signal:
        print("Alert: BTC/USDT price is above the 100-day moving average and MACD has crossed")
        print(f"[ Close ] | {df['close'][-1]} | Ma  {ma.iloc[-1]}")
        print(f"[ last macd ] | {last_macd} | Last signal  {last_signal}")
        send_mail()
    else:
        print("No alert")

def calc_indicators(symbol, start_date, end_date, period):
    df = getdata(symbol, start_date, end_date, period)

    df['ma_20'] =  df.Close.rolling(20).mean()

    df['ma_50'] =  df.Close.rolling(50).mean()
    df['ma_100'] =  df.Close.rolling(100).mean()
    df['ma_150'] =  df.Close.rolling(150).mean()
    df['ma_200'] =  df.Close.rolling(200).mean()

    df['vol'] =  df.Close.rolling(20).std()
    df['upper_bb'] =  df.ma_20 + (2 *  df.vol)
    df['lower_bb'] =  df.ma_20 - (2 *  df.vol)
    df['ret'] =  df.Close.pct_change()
    df['sl'] =  df.Close * 0.98
    df['tp'] =  df.Close * 1.02

    df['price'] =  df.Open.shift(-1)

    df.dropna(inplace=True)

    return df

def check_cond(symbol,interval,period):

    message=f"Symbol: {symbol}, Interval: {interval}, Period: {period} \n"
    cond_count=0
    threshold=0.05
    # Get the Klines data for the last 2 hours
    klines = client.get_historical_klines(symbol, interval, period)
    #frame = pd.DataFrame(client.get_historical_klines(symbol,period,start,end))

    # Convert the Klines data to a pandas DataFrame
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

    # Convert the timestamp to a datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Set the timestamp column as the index
    df.set_index('timestamp', inplace=True)

    # Calculate the RSI using the ta library
    close=pd.to_numeric(df['close'],errors='coerce')

    rsi = ta.momentum.RSIIndicator(close, window=14)

    # Calculate the Bollinger Bands using the ta library
    bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)

    max_threshold = threshold
    min_threshold = -threshold
    # Get the current price of the cryptocurrency
    last_price = float(df['close'].iloc[-1])

    prev_price = float(df['close'].iloc[-2])
    ma_30 = float(df['close'].rolling(30).mean().iloc[-1])
    last_high = float(df['high'].max())
    last_low = float(df['low'].min())
    # Calculate the percentage increase
    percent_increase = (last_price - prev_price) / prev_price * 100

    percent_near_high=( last_high - last_price) / last_high * 100
    percent_near_low=(  last_price - last_low) / last_price * 100

    # Get the last RSI and Bollinger Band values
    last_rsi = rsi.rsi()[-1]
    last_bb_upper = bb.bollinger_hband()[-1]
    last_bb_lower = bb.bollinger_lband()[-1]

    # Get the last price from the Klines data

    data=getdata(symbol, "1d", "1 year ago UTC","")

    ma_100d =data.iloc[[-1]]['ma_100']

    ma_150d =data.iloc[[-1]]['ma_150']

    ma_200d =data.iloc[[-1]]['ma_200']

    # print(f"last_price {last_price} last_rsi {last_rsi} last_bb_upper {last_bb_upper} last_bb_lower {last_bb_lower}\n ma30 {ma_30} last_low {last_low} last_high {last_high}")
    # print(f"percent_increase {percent_increase} percent_near_high {percent_near_high} percent_near_low {percent_near_low}")
    #  Check if the conditions are met


    # if last_rsi > 70:
    #     message= message + "RSI is great than 70 \n"
    #     cond_count=cond_count+1
    # if last_rsi < 30:
    #     message = message + "RSI is less than 30 \n"
    #     cond_count=cond_count+1
    # if last_price < last_bb_lower:
    #     message = message + "Current price is less than the lower Bollinger Band. \n"
    #     cond_count=cond_count+1
    # if last_price > last_bb_upper:
    #     message = message + "Current price is greater than the upper Bollinger Band. \n"
    #     cond_count=cond_count+1

    if last_price > ma_30:
        message = message + "Current price is greater than ma30. \n"
        cond_count = cond_count + 1
    if percent_near_high < max_threshold:
        message = message + "Current price is near the highest price. \n"
        cond_count = cond_count + 1
    # if percent_near_low < max_threshold:
    #     message = message + "Current price is near the lowest price. \n"
    #     cond_count = cond_count + 1

    if  cond_count==0:
        message= message + "Conditions not met."

    return cond_count,message


def check_all():
    global last_email_time
    email_interval = 60 * 60
    current_time = time.time()
    dt = datetime.now()
    print(dt)
    message=""
    isAlert = False
    symbols = ['ETHUSDT', 'BTCUSDT', 'SHIBUSDT', 'APEUSDT', 'THETAUSDT', 'MKRUSDT', 'LINKUSDT', 'ARKMUSDT', 'DOGEUSDT']
    symbol_last_sent_time = {symbol: None for symbol in symbols}

    for symbol in symbols:
        #isAlert, message = (check_percent_change(symbol, 1))
        count=0
        message = ""
        current_price = get_current_price(symbol)
        last_alert_time= last_alert_timestamps.get(symbol,0)
        hr_high, hr_low = get_24hr_high2(symbol)

        try:
            data = calc_indicators(symbol, "1d", "1 year ago UTC", "")

            ma_100d = data.iloc[[-1]]['ma_100']

            ma_150d = data.iloc[[-1]]['ma_150']

            ma_200d = data.iloc[[-1]]['ma_200']
            print(ma_100d, ma_150d, ma_200d)
            if current_price >= hr_high:
                isAlert = True
                count=count+1
                message = message + "\n" + symbol + " Current price " + str(current_price) + " > 24hr high " + str(hr_high)
            elif current_price <= hr_low:
                isAlert = True
                count=count+1

                message = message + "\n" + symbol + " Current price " + str(current_price) + " < 24hr low " + str(hr_low)

            if current_price <= float(ma_200d):
                isAlert = True
                count=count+1

                message = message + "\n" + symbol + " Current price " + str(current_price) + " <  ma_200d " + str(float(ma_200d))

            # if current_price <= float(ma_100d):
            #     isAlert = True
            #     count = count + 1
            #     message = message + "\n" + symbol + " Current price " + str(current_price) + " <  ma_100d " + str(float(ma_100d))

            # macd, signal, hist = get_macd(symbol, '4h')
            # last_macd = macd.iloc[-1]
            # last_signal = signal.iloc[-1]

            # if last_macd > last_signal:
            #     isAlert=True
            #     message = message + "\n" + symbol + " 4h MACD crossed "

            print(symbol, current_price, hr_high, hr_low)

            if count >1:
                print("isAert ", message)
                sent_symbol=symbol
                # db.execute("INSERT INTO ALERT_LOG (LOG) VALUES (%s)", (message))
                # mydb.commit()


                if  symbol_last_sent_time[symbol] is None or time.time() - symbol_last_sent_time[symbol] > 3600:
                    message = message + str(time.time())
                    send_mail(message)
                    symbol_last_sent_time[symbol] = time.time()

                # if current_time - last_alert_time > email_interval:
                #     message = message + str(last_alert_time) + str(current_time)
                #     #send_mail(message)
                #     print("email ",message)
                #
                #     last_alert_timestamps[symbol] = current_time
        except:
            print("data error")


        #count, message2 = check_cond(symbol, "1h", "50 hour ago UTC")
        #message = message + message2



#data=getdata(symbol, start_date, end_date, period)
# data=getdata('BTCUSDT', "1d", "1 year ago UTC","")
#
# print(data.iloc[-1:])


while True:
     check_all()
#
#     # check_alert()
     time.sleep(10)
# Note that this code will run indefinitely until you stop it manually. You can stop the program by pressing `Ctrl+C` in theterminal or console where it is running. Also, make sure you have the necessary API keys and permissions to access the Binance exchange before running this code.