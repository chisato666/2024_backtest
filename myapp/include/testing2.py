import pandas as pd
import talib
import function

import pandas as pd

def backtest(data,tp,sl):
    positions = []  # 儲存每一天的持倉狀態（1表示買入，-1表示賣出，0表示觀望）
    buy_date = None  # 買入日期
    buy_price = None  # 買入價格
    total_profit = 0  # 總利潤
    total_profit_per = 0  # 總利潤

    # 根據評分變動計算持倉狀態
    for i in range(1, len(data)):
        if buy_price is None:  # 沒有持倉
            if data['score'].iloc[i] > 1 and data['score'].iloc[i - 1] < 0:  # 評分從負數轉正數，買入
                positions.append(1)
                buy_date = data.index[i]
                buy_price = data['close'].iloc[i]
                print(f"買入日期：{buy_date}，價格：{buy_price}")

        else:  # 有持倉
            if data['close'].iloc[i] >= buy_price * (1 + tp):  # 股價達到10%的利潤目標，賣出
                positions.append(-1)
                total_profit += buy_price * tp  # 計算利潤
                sell_date = data.index[i]
                profit=  data['close'].iloc[i] - buy_price
                total_profit_per += (profit / buy_price) * 100

                print(f"賣出日期：{sell_date}，價格：{data['close'].iloc[i]}，利瀾：{profit} {(profit / buy_price) * 100 }%")
                buy_date = None
                buy_price = None
            elif data['close'].iloc[i] <= buy_price * (1- sl):  # 股價跌破5%的停損閾值，賣出
                positions.append(-1)
                total_profit += buy_price *  sl  # 計算利潤
                sell_date = data.index[i]

                profit =  data['close'].iloc[i] - buy_price
                total_profit_per += (profit / buy_price) * 100

                print(f"賣出日期：{sell_date}，價格：{data['close'].iloc[i]}，損失：{profit} {(profit / buy_price) * 100 }%")
                buy_date = None
                buy_price = None
            else:  # 股價未達到利潤目標或停損閾值，持續持倉
                positions.append(1)

    return total_profit, total_profit_per

# def backtest(data,tp,sl):
#     positions = []  # 儲存每一天的持倉狀態（1表示買入，-1表示賣出，0表示觀望）
#     buy_price = None  # 買入價格
#     total_profit = 0  # 總利潤
#
#     # 根據評分變動計算持倉狀態
#     for i in range(1, len(data)):
#         if buy_price is None:  # 沒有持倉
#             if data['score'].iloc[i] > 0 and data['score'].iloc[i - 1] < 0:  # 評分從負數轉正數，買入
#                 positions.append(1)
#                 buy_price = data['close'].iloc[i]
#                 print(f"date: {data.index[i]} buy price: {buy_price} ")
#             else:  # 評分未轉正，觀望
#                 positions.append(0)
#         else:  # 有持倉
#             if data['close'].iloc[i] >= buy_price * (1 + tp):  # 股價達到10%的利潤目標，賣出
#                 positions.append(-1)
#                 total_profit += buy_price * tp  # 計算利潤
#                 print(f" Sell price: {buy_price} ")
#
#                 buy_price = None
#             elif data['close'].iloc[i] <= buy_price * (1- sl):  # 股價跌破5%的停損閾值，賣出
#                 positions.append(-1)
#                 total_profit += buy_price * - sl  # 計算利潤
#                 buy_price = None
#             else:  # 股價未達到利潤目標或停損閾值，持續持倉
#                 positions.append(1)
#
#     return total_profit




def calculate_scores(data):
    scores = []

    # 計算移動平均線
    data['MA'] = data['close'].rolling(window=10).mean()

    # 計算相對強弱指數 (RSI)
    data['RSI'] = talib.RSI(data['close'], timeperiod=14)

    # 計算布林帶
    upper_band, middle_band, lower_band = talib.BBANDS(data['close'], timeperiod=20, nbdevup=2, nbdevdn=2)
    data['Upper Band'] = upper_band
    data['Middle Band'] = middle_band
    data['Lower Band'] = lower_band

    # 計算MACD
    macd, macd_signal, _ = talib.MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    data['MACD'] = macd
    data['MACD Signal'] = macd_signal

    # 計算ATR
    data['ATR'] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)

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


# 讀取股票價格數據（假設為CSV文件），並轉換為DataFrame
# data = pd.read_csv('stock_data.csv')
#
# # 假設只考慮最近三個月的K線資料
# start_date = pd.to_datetime('2024-02-01')
# end_date = pd.to_datetime('2024-04-30')
# data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
# time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1

crypto_list = function.get_symbol_list()

#symbol='BTC_USDT'
period = 'Hour4'
symbol_list=[]

for symbol in crypto_list:
    #print(symbol)
    data = function.check_symbols_kline(symbol, period,  40)
    if (len(data)>14):
        scores = calculate_scores(data)
        #print( ' scores: ', len(scores), 'data:', len(data))
        if scores[len(data)-1] > 1 and scores[len(data)-2] < 0:  # 評分從負數轉正數，買入
            symbol_list.append(symbol)
            print('Symbol: ', symbol, ' 日期:', data.index[len(data)-2], '評分:', scores[len(data)-2])

            print('Symbol: ', symbol, ' 日期:', data.index[len(data)-1], '評分:', scores[len(data)-1])




# 呼叫 calculate_scores 函數計算每一日的評分

# 呼叫 backtest 函數進行回測
# print(symbol_list)
# symbol_list=['ICP_USDT', 'MINA_USDT', 'ENJ_USDT', 'WOO_USDT', 'ANKR_USDT', 'BSV_USDT']
#
symbol_list=['GROK_USDT', 'TIA_USDT']

# for symbol in crypto_list:
#     data = function.check_symbols_kline(symbol, period,  640)
#     data['score'] = calculate_scores(data)
#     # 輸出總利潤
#     # 呼叫 backtest 函數進行回測，TP設定為10%，SL設定為5%
#     total_profit, total_profit_per = backtest(data, 0.2, 0.1)
#     print(symbol,period)
#     print('總利潤:', total_profit)  # 輸出持倉狀態、每一天的收益和總收益率
#     print('總利潤%:', total_profit_per)  # 輸出持倉狀態、每一天的收益和總收益率

# 輸出總利潤

#if scores[i] != 0:




# 判斷買入或賣出
# if total_score > 0:
#     action = '買入'
# elif total_score < 0:
#     action = '賣出'
# else:
#     action = '觀望'

# 輸出總評分和建議動作
# print('總評分:', total_score)
# print('建議動作:', action)