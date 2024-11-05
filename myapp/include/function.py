import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time,pytz
from datetime import datetime
import talib as ta
import csv
from binance.client import Client
client= Client()




def getdata(symbol,start_date,end_date,period):

    #interval = c("1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h",
    #             "1d", "3d", "1w", "1M"),

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
#   df['SMA200']=df.Close.rolling(200).mean()

    return df


def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    # Calculate the short-term and long-term EMA
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Calculate MACD line and Signal line
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    return macd, signal






# Function to calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_parabolic_sar(df, initial_af=0.02, max_af=0.2):
    # Initialize SAR and other variables
    sar = pd.Series(index=df.index, data=0.0)
    is_uptrend = True

    # Set initial values
    sar.iloc[0] = df['Low'].iloc[0]  # Starting SAR
    ep = df['High'].iloc[0]  # Extreme Point
    af = initial_af  # Acceleration Factor

    for i in range(1, len(df)):
        if is_uptrend:
            sar.iloc[i] = sar.iloc[i - 1] + af * (ep - sar.iloc[i - 1])
            # Adjust for new high
            if df['High'].iloc[i] > ep:
                ep = df['High'].iloc[i]
                af = min(af + initial_af, max_af)
            # Check for trend reversal
            if df['Low'].iloc[i] < sar.iloc[i]:
                is_uptrend = False
                sar.iloc[i] = ep  # Set SAR to EP on reversal
                ep = df['Low'].iloc[i]  # Reset EP to low
                af = initial_af  # Reset AF
        else:
            sar.iloc[i] = sar.iloc[i - 1] + af * (ep - sar.iloc[i - 1])
            # Adjust for new low
            if df['Low'].iloc[i] < ep:
                ep = df['Low'].iloc[i]
                af = min(af + initial_af, max_af)
            # Check for trend reversal
            if df['High'].iloc[i] > sar.iloc[i]:
                is_uptrend = True
                sar.iloc[i] = ep  # Set SAR to EP on reversal
                ep = df['High'].iloc[i]  # Reset EP to high
                af = initial_af  # Reset AF

    return sar



# Function to calculate EMA
def calculate_ema(data, span):
    return data['Close'].ewm(span=span, adjust=False).mean()


def calculate_dmi(data, period=14):
    high = data['High']
    low = data['Low']
    close = data['Close']

    # Calculate True Range (TR)
    data['High_Low'] = high - low
    data['High_Close'] = (high - close.shift(1)).fillna(0)
    data['Low_Close'] = (close.shift(1) - low).fillna(0)
    data['TR'] = data[['High_Low', 'High_Close', 'Low_Close']].max(axis=1)

    # Calculate +DM and -DM
    data['+DM'] = np.where(
        (high - high.shift(1) > low.shift(1) - low) & (high - high.shift(1) > 0),
        high - high.shift(1),
        0
    )
    data['-DM'] = np.where(
        (low.shift(1) - low > high - high.shift(1)) & (low.shift(1) - low > 0),
        low.shift(1) - low,
        0
    )

    # Calculate the smoothed TR, +DM, and -DM
    data['TR_smooth'] = data['TR'].rolling(window=period).mean()
    data['+DM_smooth'] = data['+DM'].rolling(window=period).mean()
    data['-DM_smooth'] = data['-DM'].rolling(window=period).mean()

    # Calculate +DI and -DI
    data['+DI'] = (data['+DM_smooth'] / data['TR_smooth']) * 100
    data['-DI'] = (data['-DM_smooth'] / data['TR_smooth']) * 100

    return data[['+DI', '-DI']]


# Function to calculate Bollinger Bands
# def calculate_bollinger_bands(data, window=20, num_std_dev=2):
#     rolling_mean = data['Close'].rolling(window=window).mean()
#     rolling_std = data['Close'].rolling(window=window).std()
#     data['Bollinger_Upper'] = rolling_mean + (rolling_std * num_std_dev)
#     data['Bollinger_Lower'] = rolling_mean - (rolling_std * num_std_dev)
#     return data[['Bollinger_Upper', 'Bollinger_Lower']]


def calculate_bollinger_bands(df, window=20, num_std=2):
    # Calculate the rolling mean and standard deviation
    rolling_mean = df['Close'].rolling(window=window).mean()
    rolling_std = df['Close'].rolling(window=window).std()

    # Calculate the upper and lower bands
    df['Bollinger_Upper'] = rolling_mean + (rolling_std * num_std)
    df['Bollinger_Lower'] = rolling_mean - (rolling_std * num_std)

    return df

# Function to calculate Stochastic Oscillator
def calculate_stochastic(data, k_window=14, d_window=3):
    min_low = data['Low'].rolling(window=k_window).min()
    max_high = data['High'].rolling(window=k_window).max()
    data['%K'] = 100 * ((data['Close'] - min_low) / (max_high - min_low))
    data['%D'] = data['%K'].rolling(window=d_window).mean()
    return data[['%K', '%D']]

def calculate_stochastic_oscillator(df, k_window=14, d_window=3):
    # Calculate the lowest low and highest high over the specified window
    low_min = df['Low'].rolling(window=k_window).min()
    high_max = df['High'].rolling(window=k_window).max()

    # Calculate %K
    df['%K'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    # Calculate %D
    df['%D'] = df['%K'].rolling(window=d_window).mean()

    return df
# Function to calculate Average True Range (ATR)
def calculate_atr(data, period=14):
    high = data['High']
    low = data['Low']
    close = data['Close']

    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calculate ATR
    atr = tr.rolling(window=period).mean()
    return atr


def check_sell_signals(df):
    score = 0
    sell_signals = {}

    # Calculate MACD
    df['MACD'], df['Signal'] = calculate_macd(df)
    cross_up_indices, cross_down_indices = check_macd_crosses(df)

    # Print debug information
    print("Cross Down Indices:", cross_down_indices)
    print("Type of Cross Down Indices:", type(cross_down_indices))

    if isinstance(cross_down_indices, list) and cross_down_indices:
        score += 1
        sell_signals['MACD Cross Down'] = cross_down_indices

    # RSI
    df['RSI'] = calculate_rsi(df)
    overbought_indices = df[df['RSI'] > 70].index.tolist()

    if overbought_indices:
        score += 1
        sell_signals['RSI Overbought'] = overbought_indices

    # Calculate Bollinger Bands
    df = calculate_bollinger_bands(df)

    if df['Close'].iloc[-1] > df['Bollinger_Upper'].iloc[-1]:
        score += 1
        sell_signals['Bollinger Band Sell Signal'] = [df.index[-1]]

    # Calculate Stochastic Oscillator
    df = calculate_stochastic_oscillator(df)  # Ensure this is called

    # Print columns for debugging
    print("DataFrame columns:", df.columns)

    # Check Stochastic Oscillator Sell Signal
    if '%K' in df.columns and '%D' in df.columns:
        if df['%K'].iloc[-1] < df['%D'].iloc[-1] and df['%K'].iloc[-1] > 80:
            score += 1
            sell_signals['Stochastic Sell Signal'] = [df.index[-1]]
    else:
        print("Stochastic Oscillator columns are missing.")

    # Parabolic SAR
    df['SAR'] = calculate_parabolic_sar(df)
    if df['Close'].iloc[-1] < df['SAR'].iloc[-1]:
        score += 1
        sell_signals['Parabolic SAR Sell Signal'] = [df.index[-1]]

    # EMA Crossover
    df['EMA_10'] = calculate_ema(df, 10)
    df['EMA_50'] = calculate_ema(df, 50)
    df['EMA_Cross_Down'] = (df['EMA_10'] < df['EMA_50'])
    df['Previous_EMA_Cross_Down'] = df['EMA_Cross_Down'].shift(1)
    ema_cross_down = df[(df['EMA_Cross_Down'] == True) & (df['Previous_EMA_Cross_Down'] == False)]

    if not ema_cross_down.empty:
        score += 1
        sell_signals['EMA Crossover Sell Signal'] = ema_cross_down.index.tolist()

    # DMI Sell Signal
    df[['+DI', '-DI']] = calculate_dmi(df)
    if df['-DI'].iloc[-1] > df['+DI'].iloc[-1]:
        score += 1
        sell_signals['DMI Sell Signal'] = [df.index[-1]]

    # ATR Spike
    df['ATR'] = calculate_atr(df)
    if df['ATR'].iloc[-1] > df['ATR'].rolling(window=14).mean().iloc[-1]:
        score += 1
        sell_signals['ATR Spike'] = [df.index[-1]]

    return score, sell_signals

def check_buy_signals(df):
    score = 0
    buy_signals = {}

    # Calculate Indicators
    df[['+DI', '-DI']] = calculate_dmi(df)
   # df[['Bollinger_Upper', 'Bollinger_Lower']] = calculate_bollinger_bands(df)
    df = calculate_bollinger_bands(df)
    #df = calculate_stochastic(df)

    df[['%K', '%D']] = calculate_stochastic(df)

    # MACD
    df['MACD'], df['Signal'] = calculate_macd(df)
    df['Cross_Up'] = (df['MACD'] > df['Signal'])
    df['Previous_Cross_Up'] = df['Cross_Up'].shift(1)
    macd_cross_up = df[(df['Cross_Up'] == True) & (df['Previous_Cross_Up'] == False)]

    if not macd_cross_up.empty:
        score += 1
        buy_signals['MACD Cross Up'] = macd_cross_up.index.tolist()

    # RSI
    df['RSI'] = calculate_rsi(df)
    df['RSI_Cross_Up'] = df['RSI'] > 30
    df['Previous_RSI_Cross_Up'] = df['RSI_Cross_Up'].shift(1)
    rsi_cross_up = df[(df['RSI_Cross_Up'] == True) & (df['Previous_RSI_Cross_Up'] == False)]

    if not rsi_cross_up.empty:
        score += 1
        buy_signals['RSI Cross Up'] = rsi_cross_up.index.tolist()

    # Parabolic SAR
    df['SAR'] = calculate_parabolic_sar(df)
    df['SAR_Buy_Signal'] = df['Close'] > df['SAR']
    if df['SAR_Buy_Signal'].iloc[-1]:  # Check the last value for recent signal
        score += 1
        buy_signals['Parabolic SAR Buy Signal'] = [df.index[-1]]

    # MACD Bottom Divergence
    df['MACD_Divergence'] = (df['MACD'] < df['MACD'].shift(1)) & (df['Close'] > df['Close'].shift(1))
    if df['MACD_Divergence'].any():
        score += 1
        buy_signals['MACD Bottom Divergence'] = df[df['MACD_Divergence']].index.tolist()

    # EMA Crossover
    df['EMA_10'] = calculate_ema(df, 10)
    df['EMA_50'] = calculate_ema(df, 50)
    df['EMA_Cross_Up'] = (df['EMA_10'] > df['EMA_50'])
    df['Previous_EMA_Cross_Up'] = df['EMA_Cross_Up'].shift(1)
    ema_cross_up = df[(df['EMA_Cross_Up'] == True) & (df['Previous_EMA_Cross_Up'] == False)]

    if not ema_cross_up.empty:
        score += 1
        buy_signals['EMA Crossover Buy Signal'] = ema_cross_up.index.tolist()

    # DMI Buy Signal
    df['DMI_Buy_Signal'] = (df['+DI'] > df['-DI'])
    if df['DMI_Buy_Signal'].iloc[-1]:  # Check last value
        score += 1
        buy_signals['DMI Buy Signal'] = [df.index[-1]]

    # Bollinger Band Buy Signal
    if df['Close'].iloc[-1] < df['Bollinger_Lower'].iloc[-1]:
        score += 1
        buy_signals['Bollinger Band Buy Signal'] = [df.index[-1]]

    # Stochastic Buy Signal
    if df['%K'].iloc[-1] > df['%D'].iloc[-1]:  # %K crosses above %D
        score += 1
        buy_signals['Stochastic Buy Signal'] = [df.index[-1]]

    return score, buy_signals

def check_macd_crosses(df):
    df['Cross_Up'] = (df['MACD'] > df['Signal'])
    df['Cross_Down'] = (df['MACD'] < df['Signal'])
    df['Previous_Cross_Up'] = df['Cross_Up'].shift(1)
    df['Previous_Cross_Down'] = df['Cross_Down'].shift(1)

    cross_up_points = df[(df['Cross_Up'] == True) & (df['Previous_Cross_Up'] == False)]
    cross_down_points = df[(df['Cross_Down'] == True) & (df['Previous_Cross_Down'] == False)]

    return cross_up_points, cross_down_points

# Check for weekly cross up
def check_macd_cross_up(df):
    df['Cross'] = df['MACD'] > df['Signal']
    df['Previous_Cross'] = df['Cross'].shift(1)

    # Identify cross up points
    cross_up_points = df[(df['Cross'] == True) & (df['Previous_Cross'] == False)]

    return cross_up_points


def check_macd_cross_down(df):
    df['Cross'] = df['MACD'] < df['Signal']
    df['Previous_Cross'] = df['Cross'].shift(1)

    # Identify cross up points
    cross_down_points = df[(df['Cross'] == True) & (df['Previous_Cross'] == False)]

    return cross_down_points

def backtest_excel(df):

    rows = [row for row in df]

    data = {
        "Rules": 'Rules',

        "Start Date": 'Start Date',
        "End Date": 'End Date',

        "Timeframe": "Timeframe",
        "Symbol": 'Symbol',

        "TP": 'TP',
        "SL": 'SL',
        "in_diff": 'in_diff',

        "Profit": 'Profit',
        "Profit Count": 'Profit Count'
    }
    df = pd.DataFrame(data, index=[0])

    rules=0
    start_date=1
    end_date=2
    symbol=3
    period=4
    tp=5
    sl=6
    in_diff=7

    for row in rows:

        if row[rules]=='1':

            df2 = getdata(row[symbol], row[start_date], row[end_date], row[period])
            print(df2,'df2')
            profits, pro_list, pro_count, buyarr, plt = get_rules1(df2, row[in_diff], row[tp], row[sl])
            profits = (profits - 1) * 100

            print(profits,'profits')
            print(pro_count,'pro_count')


            df = df.append({
                "Rules": row[rules],
                "Start Date": row[start_date],
                "End Date": row[end_date],
                "Timeframe": row[period],

                "Symbol": row[symbol],
                "TP": row[tp],

                "SL": row[sl],
                "in_diff": row[in_diff],

                "Profit": profits,
                "Profit Count": pro_count
            }, ignore_index=True)



    with open('/Users/apple/PycharmProjects/2024_backtest/static/csv/test.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for i in range(len(df)):
            writer.writerow(df.loc[i, :])

def get_rules1(df,in_diff,in_tp,in_sl):
    in_position=False
    profits=[]
    all_arr=[]
    buy_arr=[]
    sell_arr=[]
    signalBuy=[]
    buy_points=[]
    sell_points = []
    #and row.Close>row.SMA200


    for index, row in df.iterrows():
        if not in_position:
            if row.ret > float(in_diff):
                buyprice=row.price
                bought_at = index
                tp= buyprice * (1 + float(in_tp))
                sl= buyprice * (1 - float(in_sl))
                buy_points.append((index, buyprice))

                in_position=True
        if in_position and index > bought_at:
            if row.High > tp:
                profit = (tp -buyprice)/buyprice
                profits.append(profit)
                line=[index,buyprice,row.High,profit]
                buy_arr.append(line)
                all_arr.append(line)
                sell_points.append((index, row.High))

                signalBuy.append(buyprice)

                in_position = False
            if row.Low < sl:
                profit = (sl - buyprice)/buyprice
                line=[index,buyprice,row.Low,profit]
                all_arr.append(line)
                sell_arr.append(line)
                sell_points.append((index, row.Low))

                profits.append(profit)
                in_position=False

    # dd = pd.DataFrame(profit)
    #
    # monthly_profit = df.Close.resample('M').sum()
    #
    #print(pd.Series(monthly_profit))
    # print(pd.Series(buyprices))
    #print(profits)
    pro_count=((pd.Series(profits) > 0).value_counts())
    pro_list=((pd.Series(profits) + 1).cumprod())
   # total=((pd.Series(profits) + 1).cumprod())
    pro_total=(pd.Series(profits) +1).prod()

    #plt.show()
    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.max_columns', 10)

    df['signal']=pd.Series([signalBuy])

    print(buy_points)
    print(sell_points)

    plot_backtest(df, buy_points, sell_points)

    #plt.scatter(self.sell_arr.index, self.sell_arr.values, marker='v', c='r')
    return pro_total,pro_list,pro_count,all_arr,df


def get_rules3(df,tp_percentage,stop_loss_percentage,moving_sl,sell_type, over_ema=0, ema_short_period=5,ema_long_period=10,reverse_trade='No'):

    # Load the historical price data into a DataFrame
    df_btc = df
    profits=[]
    all_arr=[]

    # Define the strategy parameters
    # if ema_short > 0:
    # ema_short_period = 10
    # ema_long_period = 50
    # stop_loss_percentage = 0.1
    # tp_percentage=0.3

    rsi_period= 14


    # Calculate the EMA values
    df_btc['EMA_short'] = df_btc['Close'].ewm(span=ema_short_period, adjust=False).mean()
    df_btc['EMA_long'] = df_btc['Close'].ewm(span=ema_long_period, adjust=False).mean()
    df_btc['over_ema'] = df_btc['Close'].ewm(span=int(over_ema), adjust=False).mean()

    # Calculate the RSI values
    df_btc['RSI'] = ta.RSI(df_btc['Close'], timeperiod=rsi_period)

    # Initialize variables
    btc_position = False
    buy_amount=1000
    btc_buy_price = 0
    btc_sell_price = 0

    total_profit = 0
    buy_points=[]
    sell_points = []
#and df_btc['Close'][i] > over_ema
    # Backtest the strategy
    for i in range(1, len(df_btc)):
        # BTCUSDT
        if not btc_position and df_btc['EMA_short'][i] > df_btc['EMA_long'][i] and df_btc['EMA_short'][i - 1] < \
                df_btc['EMA_long'][i - 1] and (df_btc['Close'][i] > df_btc['over_ema'][i])  :
            btc_position = True
            btc_buy_price = df_btc['Close'][i]
            btc_stop_loss = btc_buy_price * (1 - stop_loss_percentage)
            tp= btc_buy_price * (1 + tp_percentage)
            buy_points.append((df_btc.index[i], df_btc['Close'][i]))

            if btc_sell_price > 0 and reverse_trade=='Yes':
                reverse_profit=btc_sell_price - btc_buy_price
                line = [df_btc.index[i], btc_buy_price, btc_sell_price, reverse_profit]
                all_arr.append(line)
                total_profit = total_profit + reverse_profit


        #Moving the SL is the current price increased
        elif moving_sl=='yes' and btc_position and df_btc['Close'][i] * (1 - stop_loss_percentage) > btc_stop_loss:
            tp = df_btc['Close'][i] * (1 + tp_percentage)
            btc_stop_loss = df_btc['Close'][i] * (1 - stop_loss_percentage)
        elif (sell_type=='TPSL' and btc_position and ((df_btc['Close'][i] <= btc_stop_loss) or (btc_position and df_btc['Close'][i] >=tp))):
            btc_position = False
            btc_sell_price = df_btc['Close'][i]
            btc_profit = round(((btc_sell_price - btc_buy_price) / btc_buy_price) * 100,2)
            profits.append(btc_profit)
            total_profit = total_profit + btc_profit
            sell_points.append((df_btc.index[i], df_btc['Close'][i]))
            line = [df_btc.index[i], btc_buy_price, btc_sell_price, btc_profit]
            all_arr.append(line)
        elif (sell_type=='cross_down' and btc_position and df_btc['EMA_short'][i] < df_btc['EMA_long'][i] and df_btc['EMA_short'][i - 1] > \
                df_btc['EMA_long'][i - 1]):
            btc_position = False
            btc_sell_price = df_btc['Close'][i]
            btc_profit = round(((btc_sell_price - btc_buy_price) / btc_buy_price) * 100, 2)
            profits.append(btc_profit)
            total_profit = total_profit + btc_profit
            sell_points.append((df_btc.index[i], df_btc['Close'][i]))
            line = [df_btc.index[i], btc_buy_price, btc_sell_price, btc_profit]
            all_arr.append(line)
                #print(f" Price {df_btc.index[i]} - Buy at {btc_buy_price:.2f}, Sell at {btc_sell_price:.2f}, Profit: {btc_profit:.2f} ,Total: {total_profit:.2f}")

    pro_count = ((pd.Series(profits) > 0).value_counts())
    pro_list = ((pd.Series(profits) ).cumprod())
    # total=((pd.Series(profits) + 1).cumprod())
    pro_total = (pd.Series(profits) ).prod()
    print("DF_BTC HERE",df_btc)
    plot_backtest(df_btc, buy_points, sell_points)

    return total_profit,pro_list,pro_count,all_arr,df




def plot_backtest(df_btc, buy_points, sell_points):
    plt.figure(figsize=(14, 8))

    plt.plot(df_btc.index, df_btc['Close'], label=' Price')

    if 'EMA_short' in df_btc:
        plt.plot(df_btc.index, df_btc['EMA_short'], label='EMA Short')

    if 'EMA_long' in df_btc:
        plt.plot(df_btc.index, df_btc['EMA_long'], label='EMA Long')

    if 'over_ema' in df_btc:
        plt.plot(df_btc.index, df_btc['over_ema'], label='Over EMA')

    plt.scatter(*zip(*buy_points), color='green', label='Buy')
    plt.scatter(*zip(*sell_points), color='red', label='Sell')

    plt.xlabel('Date/Time')
    plt.ylabel('Price (USDT)')
    plt.title('Price with Buy/Sell Points')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    graph_path = '/Users/apple/PycharmProjects/2024_backtest/myapp/static/graph/graph2.png'
    plt.savefig(graph_path)
    plt.close()
    # plt.show()

def check_symbols_with_increased_5d(percent, interval, limit):
    url = "https://contract.mexc.com/api/v1/contract/ticker"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        symbols = []

        x = 1
        for ticker in data['data']:
            x = x + 1
            # if (x > 30):
            #     break
            symbol = ticker['symbol']
            try:
                print(symbol,interval,limit,percent)

                df = check_symbols_kline(symbol, interval, limit)
                print(df)
                size = len(df)
                print('size',size)

                start_price = df['open'][0]
                end_price = df['close'][size - 1]


                price_change = (end_price - start_price) / start_price * 100
                print(start_price,end_price,price_change)

                # line = [symbol, round(price_change_percentage*100,2)]
                if (float(percent) >0) and (float(price_change) > float(percent)):
                    price_change=round(float(price_change),2)
                    line = [symbol, price_change]

                    symbols.append(line)
                    print('symbol added',symbol)
                if (float(percent) < 0) and (float(price_change) < float(percent)):
                    price_change = round(float(price_change), 2)
                    line = [symbol, price_change]

                    symbols.append(line)
                    print('symbol added', symbol)
            except Exception as error:
                print(symbol, error)

        symbols.sort(key=lambda element: element[1], reverse=True)

        return symbols
    else:
        print("Failed to retrieve data from MEXC API.")
        return None

def get_contract_info(symbol):
    url = "https://contract.mexc.com/api/v1/contract/ticker/"
    params = {'symbol': symbol}
    response = requests.get(url, params=params)
    data = response.json()
    return data['data']





# def check_symbols_kline(symbol, interval, limit):
#     url = f'https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval={interval}&limit={limit}'
#     # time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1
#
#     response = requests.get(url)
#     data = response.json()
#
#     df = pd.DataFrame(data['data'], columns=['time', 'open', 'low', 'high', 'close'])
#
#     df.index = pd.to_datetime(df.time, unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Hong_Kong'))
#
#     # df.index = pd.to_datetime(df.index, unit='s')
#
#     # df.set_index('time', inplace=True)
#
#     return df




def check_symbols_with_hr_24high(symbol,high24,low24):
    isHigh=False
    isLow=False

    url = f'https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval=Min60&limit=5'
    response = requests.get(url)
    data = response.json()
    highest_price = None

    try:
        for kline in data['data']['high']:
            if (kline>=high24):
                print(symbol,kline,high24)
                isHigh=True
                break
        for kline in data['data']['low']:
            if (kline<=low24):
                print(symbol,kline,low24)
                isLow=True
                break
    except:
        print(symbol, " 24 error")

    return isHigh, isLow



def check_symbols_with_high():
    url = "https://contract.mexc.com/api/v1/contract/ticker"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        symbols = []

        for ticker in data['data']:
            symbol = ticker['symbol']
            high24Price = float(ticker['high24Price'])

            if check_symbols_with_10hr_24high(symbol,high24Price):
                #line = [symbol, round(price_change_percentage*100,2)]
                symbols.append(symbol)

        symbols.sort(key=lambda element: element[0], reverse=False)

        return symbols
    else:
        print("Failed to retrieve data from MEXC API.")
        return None


def check_ema(symbol):
    # Logic to check if current price > 50EMA for the symbol
    # Replace this with your own implementation
    return True  # Placeholder value


# def calculate_rsi(df, period=14):
#     close_prices = df['close'].values
#     rsi = ta.momentum.RSIIndicator(close_prices, n=period)
#     rsi_values = rsi.rsi()
#     return rsi_values

def check_rsi(df):
    # Logic to check if RSI > 70 for the symbol
    df['rsi'] = ta.RSI((df['close']))
    return df  # Placeholder value

# def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
#
#
#     macd, signal, hist = ta.MACD(df['close'], fast_period=fast_period, slow_period=slow_period, signal_period=signal_period)
#
#     return macd, signal




def check_up_trend(symbol):

    return

def get_symbol_list():
    url = "https://contract.mexc.com/api/v1/contract/ticker"
    response = requests.get(url)
    symbols = []

    if response.status_code == 200:
        data = response.json()

    for ticker in data['data']:
        symbol = ticker['symbol']
        symbols.append(symbol)

    return symbols

def get_symbols_with_price_increase(rate):
    url = "https://contract.mexc.com/api/v1/contract/ticker"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        #symbol_list=['ING_USDT','YGG_USDT','SNX_USDT','FET_USDT','JASMY_USDT','XCN_USDT','BFC_USDT','MASK_USDT','C98_USDT','MC_USDT','ID_USDT','PYR_USDT','ACH_USDT','SSV_USDT','ARPA_USDT','RSS3_USDT','MXC_USDT','HIGH_USDT','BICO_USDT','APM_USDT','RACA_USDT','GOAL_USDT','MDT_USDT','SIS_USDT','QUICK_USDT','DREP_USDT','AUCTION_USDT','POND_USDT','BSW_USDT','DODO_USDT','BEL_USDT','CYBER_USDT','BRISE_USDT','FRONT_USDT']
        #symbol_list=['BTC_USDT','ETH_USDT','CLORE_USDT','ARKM_USDT','GFT_USDT','LUNANEW_USDT','TARA_USDT','ASTRA_USDT','AUCTION_USDT','BIGTIME_USDT', 'BNXNEW_USDT', 'LQTY_USDT', 'LOOM_USDT', 'TOMI_USDT']
        symbol_list=['BTC_USDT',
 'ETH_USDT',
 'SOL_USDT',
 'BIGTIME_USDT',
 'MEME_USDT',
 'LINK_USDT',
 '1000BONK_USDT',
 'TRB_USDT',
 'TIA_USDT']
        symbols = []
        current_trend = {symbol: None for symbol in symbol_list}

        for ticker in data['data']:
            message=''
            message_24high=''
            isHigh=''
            isLow=''
            up_trend=''
            up_count=0
            down_count=0
            symbol = ticker['symbol']
            lastPrice= ticker['lastPrice']
            fundingRate= ticker['fundingRate']
            price_change_percentage = float(ticker['riseFallRate'])
            high24Price= float(ticker['high24Price'])
            lower24Price= float(ticker['lower24Price'])
            #dt = datetime.now()
            dt = datetime.utcnow()  # utcnow class method
            dtobj3 = dt.replace(tzinfo=pytz.UTC)  # replace method

            dtobj_hongkong = dtobj3.astimezone(pytz.timezone("Asia/Hong_Kong"))  # astimezone method

            #dtobj_hongkong = dtobj3.astimezone(pytz.timezone("Asia/Hong_Kong"))  # astimezone method



            #isHigh, isLow= check_symbols_with_hr_24high(symbol, high24Price, lower24Price)

            dt = dtobj_hongkong.strftime("%Y-%m-%d %H:%M:%S")

            if lastPrice >= high24Price:
                message_24high = dt  + '<br> Up trend > 24high '

            #if fundingRate <= -0.001:
            if symbol in symbol_list:
                rsi_down = False
                ma20_down = False
                ma40_down = False
                macd_down = False

                rsi_up = False
                ma20_up = False
                ma40_up = False
                macd_up = False
                interval = "Min60"  # 1-hour candlestick data
                limit = 40

                kline = check_symbols_kline(symbol, interval, limit)
                df = pd.DataFrame(kline, columns=['time','open', 'low', 'high', 'close'])

                df.set_index('time', inplace=True)
                df.index = pd.to_datetime(df.index, unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Hong_Kong'))

                df['rsi'] = ta.RSI((df['close']))
                macd, signal, hist = ta.MACD((df['close']), fastperiod=12, slowperiod=26, signalperiod=9)

                df['ma20'] = df['close'].rolling(20).mean()
                df['ma40'] = df['close'].rolling(40).mean()
                df['ret'] = df['close'].pct_change()
                price_len=len(str(lastPrice))



                if (df["rsi"].iloc[-1] < 30):
                    down_count=down_count+1
                    rsi_down=True


                # if (lastPrice < df["ma20"].iloc[-1]):
                #     down_count = down_count + 1
                #     ma20_down=True


                if (lastPrice < df["ma40"].iloc[-1]):
                    down_count = down_count + 1
                    ma40_down=True


                if (macd.iloc[-1] < signal.iloc[-1]):
                    down_count = down_count + 1
                    macd_down=True




                if (df["rsi"].iloc[-1] > 70):
                    up_count = up_count + 1
                    rsi_up=True


                # if (lastPrice > df["ma20"].iloc[-1]):
                #     up_count = up_count + 1
                #     ma20_up=True


                if (lastPrice > df["ma40"].iloc[-1]):
                    up_count = up_count + 1
                    ma40_up=True

                if (macd.iloc[-1] > signal.iloc[-1]):
                    up_count = up_count + 1
                    macd_up=True

                print(symbol, " down - " , rsi_down,ma20_down,ma40_down,macd_down)
                print(symbol , " Up - " , rsi_up,ma20_up,ma40_up,macd_up)


                if up_count >= 2:
                    trend='Up'
                elif down_count >= 2:
                    trend='Down'
                else:
                    trend='Neutral'


                isHigh, isLow = check_symbols_with_hr_24high(symbol, high24Price, lower24Price)

                line = [symbol, round(price_change_percentage*100,2),lastPrice,round(fundingRate*100,3),high24Price,lower24Price,trend,message_24high,isHigh,isLow,round(df["rsi"].iloc[-1],2),up_count, down_count]
                symbols.append(line)

        symbols.sort(key=lambda element: element[1], reverse=True)
        print(symbols)
        return symbols
    else:
        print("Failed to retrieve data from MEXC API.")
        return None



def get_binance_historical_data(symbol, interval, start_date, end_date):
    # Convert dates to milliseconds
    start_timestamp = pd.Timestamp(start_date).timestamp() * 1000
    end_timestamp = pd.Timestamp(end_date).timestamp() * 1000

    # Binance API endpoint for historical klines data
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={int(start_timestamp)}&endTime={int(end_timestamp)}"

    # Send GET request to the API endpoint
    response = requests.get(url)

    # Parse the JSON response
    data = response.json()

    # Convert the data to a DataFrame
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])

    # Clean up the DataFrame
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df

def check_percent_change():
    # Specify the cryptocurrency symbol, interval, start date, and end date
    symbols = ['BTCUSDT','ETHUSDT','SOLUSDT','LINKUSDT','OPUSDT','AVAXUSDT','SANDUSDT']  # Example: Bitcoin/USDT
    interval = "1d"  # Example: daily interval
    start_date = "2023-01-31"
    end_date = "2024-01-31"


    for symbol in symbols:
        # Get the historical data from Binance
        data = get_binance_historical_data(symbol, interval, start_date, end_date)

        # Calculate the percentage change
        percentage_change = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0] * 100

        # Display the percentage change
        print(f"Percentage change for {symbol} from {start_date} to {end_date}: {percentage_change:.2f}%")

def check_symbols_kline(symbol, interval, limit):
    url = f'https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval={interval}&limit={limit}'
    #     # time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1

    response = requests.get(url)
    data = response.json()
    df=[]
    try:
        df = pd.DataFrame(data['data'], columns=['time', 'open', 'low', 'high', 'close'])
        df.columns = ['Time', 'Open', 'Low', 'High', 'Close']  # Rename columns

        df['ret'] = df.Close.pct_change()
        df.index = pd.to_datetime(df.Time, unit='s', utc=True).map(lambda x: x.tz_convert('Asia/Hong_Kong'))
    except Exception as error:
        print(symbol,'ERROR ', error)

    return df

def get_market_cap_rank(crypto):
    api_key = '496c4b12-9483-415b-8701-edaddbd510c6'  # Replace with your CoinMarketCap API key
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=800&convert=USD"
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
    return 999

def check_ema_cross(data,check_range,symbol,ema_short,ema_long,cross_direction):
    # end_date = pd.Timestamp.today()
    # start_date = end_date - pd.DateOffset(days=80)
    ema_list=''

    if len(data) >= ema_long :
        data['ema_short'] = data['close'].ewm(span=ema_short, adjust=False).mean()
        data['ema_long'] = data['close'].ewm(span=ema_long, adjust=False).mean()
        ma_short = data['close'].rolling(window=ema_short).mean()
        ma_long = data['close'].rolling(window=ema_long).mean()

        ema_short = data['close'].ewm(span=ema_short, adjust=False).mean()
        ema_long = data['close'].ewm(span=ema_long, adjust=False).mean()
        #data.dropna(inplace=True)

        print(ema_short)

        for i in range(len(data) - check_range,len(data)):
            #if (((cross_direction=='up' and ((ma_short[i] > ma_long[i]) and (ma_short[i-1] <= ma_long[i-1])))) or ((cross_direction=='down' and ((ma_short[i] < ma_long[i]) and (ma_short[i-1] >= ma_long[i-1]))))):
            if (((cross_direction=='up' and ((ema_short[i] > ema_long[i]) and (ema_short[i-1] <= ema_long[i-1])))) or ((cross_direction=='down' and ((ema_short[i] < ema_long[i]) and (ema_short[i-1] >= ema_long[i-1]))))):
                cross_date = data.index[i]
                print(f" {symbol} : i ={data['close'][i]} {ema_short[i-1]} | {ema_long[i-1]} EMA crossed {cross_direction} above {ema_short[i]} | {ema_long[i]} EMA on {cross_date}")
                url="https://futures.mexc.com/exchange/" + symbol + "?type=linear_swap"
                symbol_link=f'<a href="{url}" target="_blank">{symbol}</a>'
                ema_list=[symbol_link,cross_date]

    return ema_list


def plot_crypto_price_with_ema(crypto_symbol, data):
    ema_10 = data['close'].ewm(span=10, adjust=False).mean()
    ema_50 = data['close'].ewm(span=50, adjust=False).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['close'], label=f"{crypto_symbol} Price")
    plt.plot(data.index, ema_10, label="10-day EMA")
    plt.plot(data.index, ema_50, label="50-day EMA")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(f"{crypto_symbol} Price with 10-day and 50-day EMA")
    plt.legend()
    plt.show()



def backtest_ema(df,tp_percentage,stop_loss_percentage):

    # Load the historical price data into a DataFrame
    df_btc = df

    # Define the strategy parameters
    ema_short_period = 10
    ema_long_period = 50
    # stop_loss_percentage = 0.1
    # tp_percentage=0.3

    rsi_period= 14


    # Calculate the EMA values
    df_btc['EMA_short'] = df_btc['Close'].ewm(span=ema_short_period, adjust=False).mean()
    df_btc['EMA_long'] = df_btc['Close'].ewm(span=ema_long_period, adjust=False).mean()

    # Calculate the RSI values
    df_btc['RSI'] = ta.RSI(df_btc['Close'], timeperiod=rsi_period)

    # Initialize variables
    btc_position = False
    buy_amount=1000
    btc_buy_price = 0
    total_profit = 0
    buy_points=[]
    sell_points = []

    # Backtest the strategy
    for i in range(1, len(df_btc) ):
        # BTCUSDT
        if i < len(df_btc):
            if not btc_position and df_btc['EMA_short'][i] > df_btc['EMA_long'][i] and df_btc['EMA_short'][i - 1] < \
                    df_btc['EMA_long'][i - 1] :
                btc_position = True
                btc_buy_price = df_btc['Close'][i]
                btc_stop_loss = btc_buy_price * (1 - stop_loss_percentage)
                tp= btc_buy_price * (1 + tp_percentage)
                buy_points.append((df_btc.index[i], df_btc['Close'][i]))

            elif btc_position and df_btc['Close'][i] * (1 - stop_loss_percentage) > btc_stop_loss:
                tp= df_btc['Close'][i] * (1 + tp_percentage)

                btc_stop_loss = df_btc['Close'][i] * (1 - stop_loss_percentage)
            elif (btc_position and df_btc['Close'][i] <= btc_stop_loss) or (btc_position and df_btc['Close'][i] >=tp):
                btc_position = False
                btc_sell_price = df_btc['Close'][i]
                btc_profit = ((btc_sell_price - btc_buy_price) / btc_buy_price) *100
                total_profit = total_profit + btc_profit
                sell_points.append((df_btc.index[i], df_btc['Close'][i]))

                #print(f" Price {df_btc.index[i]} - Buy at {btc_buy_price:.2f}, Sell at {btc_sell_price:.2f}, Profit: {btc_profit:.2f} ,Total: {total_profit:.2f}")



    return total_profit, buy_points, sell_points


def calculate_scores(data):
    scores = []

    # 計算移動平均線
    data['MA'] = data['close'].rolling(window=10).mean()

    # 計算相對強弱指數 (RSI)
    data['RSI'] = ta.RSI(data['close'], timeperiod=14)

    # 計算布林帶
    upper_band, middle_band, lower_band = ta.BBANDS(data['close'], timeperiod=20, nbdevup=2, nbdevdn=2)
    data['Upper Band'] = upper_band
    data['Middle Band'] = middle_band
    data['Lower Band'] = lower_band

    # 計算MACD
    macd, macd_signal, _ = ta.MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    data['MACD'] = macd
    data['MACD Signal'] = macd_signal

    # 計算ATR
    data['ATR'] = ta.ATR(data['high'], data['low'], data['close'], timeperiod=14)

    # 計算評分
    for i in range(len(data)):
        daily_score = 0
        if data['MA'].iloc[i] > data['MA'].iloc[i - 1]:
            daily_score += 1
        elif data['MA'].iloc[i] < data['MA'].iloc[i - 1]:
            daily_score -= 1

        if data['RSI'].iloc[i] > 70:
            daily_score += 1
        elif data['RSI'].iloc[i] < 30:
            daily_score -= 1

        if data['close'].iloc[i] > data['Upper Band'].iloc[i]:
            daily_score -= 1
        elif data['close'].iloc[i] < data['Lower Band'].iloc[i]:
            daily_score += 1

        if data['MACD'].iloc[i] > data['MACD Signal'].iloc[i]:
            daily_score += 1
        elif data['MACD'].iloc[i] < data['MACD Signal'].iloc[i]:
            daily_score -= 1

        if data['ATR'].iloc[i] > data['close'].iloc[i] * 0.02:  # 假設閾值為收盤價的2%
            daily_score += 1

        scores.append(daily_score)

    return scores


def calculate_scores_over_intervals(df, interval_days=10):
    scores = []
    for i in range(0, len(df) - interval_days + 1):
        window_df = df.iloc[i:i + interval_days]
        score, _ = check_buy_signals(window_df)
        scores.append(score)
    return scores


def plot_prices_and_scores(df, scores):
    # Create a new DataFrame for plotting
    score_df = pd.DataFrame({'Score': scores}, index=df.index[:len(scores)])

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot the price
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price', color='tab:blue')
    ax1.plot(df.index, df['Close'], color='tab:blue', label='Price')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Create a second y-axis for the scores
    ax2 = ax1.twinx()
    ax2.set_ylabel('Buy Score', color='tab:orange')
    ax2.plot(score_df.index, score_df['Score'], color='tab:orange', label='Buy Score', linestyle='--')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    # Add titles and legends
    plt.title('Price and Buy Score Over Time')
    fig.tight_layout()
    plt.show()


def backtest_trading_strategy(df, scores, tp_percent=0.20, sl_percent=0.10):
    trades = []
    total_profit = 0
    position = None  # Track the current trade position

    for i in range(len(df)):
        score = scores[i] if i < len(scores) else 0

        # Check if we should enter a trade
        if score > 4 and position is None:
            entry_price = df['Close'].iloc[i]
            tp_price = entry_price * (1 + tp_percent)  # 20% TP
            sl_price = entry_price * (1 - sl_percent)  # 10% SL
            position = {
                'entry_price': entry_price,
                'tp_price': tp_price,
                'sl_price': sl_price,
                'entry_index': i
            }
            print(f"Entering trade at index {i}, price: {entry_price}")

        # Check if we need to exit the trade
        if position is not None:
            current_price = df['Close'].iloc[i]
            if current_price >= position['tp_price']:
                profit = current_price - position['entry_price']
                total_profit += profit
                trades.append({
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'entry_index': position['entry_index'],
                    'exit_index': i,
                    'profit': profit
                })
                print(f"Taking profit at index {i}, price: {current_price}, profit: {profit}")
                position = None  # Reset position after exit
            elif current_price <= position['sl_price']:
                loss = position['entry_price'] - current_price
                total_profit -= loss
                trades.append({
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'entry_index': position['entry_index'],
                    'exit_index': i,
                    'profit': -loss
                })
                print(f"Stopping loss at index {i}, price: {current_price}, loss: {loss}")
                position = None  # Reset position after exit

    return trades, total_profit

def plot_trades(df, trades):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], color='blue', label='Price', alpha=0.5)

    # Plot buy and sell points
    for trade in trades:
        entry_index = trade['entry_index']
        exit_index = trade['exit_index']
        plt.scatter(df.index[entry_index], trade['entry_price'], color='green', marker='^', label='Buy' if trade == trades[0] else "")
        plt.scatter(df.index[exit_index], trade['exit_price'], color='red', marker='v', label='Sell' if trade == trades[0] else "")

    plt.title('Price with Buy and Sell Points')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

# def plot_prices_and_scores(df, scores):
#     score_df = pd.DataFrame({'Score': scores}, index=df.index[:len(scores)])
#
#     # Create subplots
#     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
#
#     # Plot Price
#     ax1.plot(df.index, df['Close'], color='blue', label='Price')
#     ax1.set_title('Price Over Time')
#     ax1.set_ylabel('Price')
#     ax1.legend()
#     ax1.grid()
#
#     # Plot Scores
#     ax2.plot(score_df.index, score_df['Score'], color='orange', label='Buy Score', linestyle='--')
#     ax2.set_title('Buy Score Over Time')
#     ax2.set_ylabel('Buy Score')
#     ax2.legend()
#     ax2.grid()
#
#     # Set common x-axis label
#     ax2.set_xlabel('Date')
#
#     # Adjust layout
#     plt.tight_layout()
#     plt.show()

# crypto_list=get_symbol_list()
# print(crypto_list)

#check_ema_cross(data,crypto_list)

# symbol='BTC_USDT'
# interval = "Day1"  # 1-hour candlestick data
# limit=80
# count=0
# ema_list=[]
# add_list=[]
# for symbol in crypto_list:
#     df = check_symbols_kline(symbol, interval, limit)
#     if check_ema_cross(df, 10, symbol):
#         add_list.append(symbol)
#
# print(add_list)

# symbols=['BTCUSDT','ETHUSDT','SOLUSDT','DOTUSDT','OPUSDT','AVAXUSDT','LINKUSDT','SANDUSDT','SUIUSDT']
#
start_date='01-01-2024'
end_date='21-10-2024'
periods='Day1'
sell_points=[]
buy_points=[]
symbol='BTC_USDT'
# df = check_symbols_kline(symbol, periods, 105)
# print(symbol, df)
# #
# scores = calculate_scores_over_intervals(df, interval_days=15)  # Get scores over 10-day intervals
#
# trades, total_profit = backtest_trading_strategy(df, scores, tp_percent=0.10, sl_percent=0.05)
#
# # Display total profit
# print(f"Total Profit: {total_profit}")
# plot_trades(df, trades)


#plot_prices_and_scores(df, scores)

#
# if (len(df) > 2):
#     #sell_score, sell_signals = check_sell_signals(df)
#     score, buy_signals = check_buy_signals(df)
#     print(score,buy_signals)

   # print(sell_score,sell_signals)
# for symbol in symbols:
#     df=getdata(symbol,start_date,end_date,periods)
#
#     df['MACD'], df['Signal'] = calculate_macd(df)
#     weekly_cross_up = check_macd_cross_up(df)
#     weekly_cross_down = check_macd_cross_down(df)
#
#     # Display results
#     if not weekly_cross_down.empty:
#         print(symbol, " Weekly MACD has crossed drown on the following dates:")
#         print(weekly_cross_down.index)
#
#     if not weekly_cross_up.empty:
#         print(symbol, " Weekly MACD has crossed up on the following dates:")
#         print(weekly_cross_up.index)
#     else:
#         print("No weekly MACD cross up detected.")
# total,sell_points,buy_points=backtest_ema(df,0.2,0.1)
# plot_backtest(df,buy_points, sell_points)


# for symbol in symbols:
#     for period in periods:
#         df=getdata(symbol,start_date,end_date,period)
#         total,sell_points,buy_points=backtest_ema(df,0.3,0.1)
#         print(symbol,period,str(int(total)))
        #plot_backtest(df,buy_points, sell_points)

# Fetch historical data using an API or from a CSV file
# Assuming you have OHLCV (Open, High, Low, Close, Volume) data
# stored in a pandas DataFrame named 'data'

# Assuming 'data' DataFrame has columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
#data = check_symbols_kline(symbol, interval,limit)  # Replace this with your own data fetching logic

# list=check_symbols_with_increased_5d(percent,interval,limit)
# print(list)
# data=get_contract_info('TARA_USDT')
# print(data['lastPrice'],data['symbol'])
#print(check_symbols_with_high())

# Example usage
# rate = 0.05
# symbol_list = get_symbols_with_price_increase(rate)
# print(symbol_list)
# list=[]
# if symbol_list:
#     print("Symbols with price increase over :" + str(rate * 100) + "%")
#     for symbol in symbol_list:
#         list.append(symbol[0])
#         #print(symbol[0])
#

#print(list)