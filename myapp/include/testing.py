import pandas as pd
import function



def calculate_score(data):
    score = []

    # 計算移動平均線
    data['MA_short'] = data['close'].rolling(window=10).mean()
    data['MA_long'] = data['close'].rolling(window=50).mean()

    # 計算相對強弱指數 (RSI)
    delta = data['close'].diff()
    gain = delta.mask(delta < 0, 0)
    loss = -delta.mask(delta > 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi

    # 計算 MACD 指標
    data['MACD_line'] = data['close'].ewm(span=12).mean() - data['close'].ewm(span=26).mean()
    data['MACD_signal'] = data['MACD_line'].ewm(span=9).mean()

    # 計算布林帶
    data['MA'] = data['close'].rolling(window=20).mean()
    data['std'] = data['close'].rolling(window=20).std()
    data['upper_band'] = data['MA'] + (2 * data['std'])
    data['lower_band'] = data['MA'] - (2 * data['std'])

    # 計算評分
    for i in range(len(data)):
        daily_score = 0
        if data['MA_short'].iloc[i] > data['MA_long'].iloc[i] and data['MA_short'].iloc[i - 1] <= data['MA_long'].iloc[
            i - 1]:
            daily_score += 1
        if data['RSI'].iloc[i] > 30 and data['RSI'].iloc[i - 1] <= 30:
            daily_score += 1
        if data['MACD_line'].iloc[i] > data['MACD_signal'].iloc[i] and data['MACD_line'].iloc[i - 1] <= \
                data['MACD_signal'].iloc[i - 1]:
            daily_score += 1
        if data['close'].iloc[i] > data['upper_band'].iloc[i] and data['close'].iloc[i - 1] <= data['upper_band'].iloc[
            i - 1]:
            daily_score += 1

        if daily_score >= 2:
            score.append(daily_score)
        else:
            score.append(-daily_score)

    return score


# time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1

# 讀取股票價格數據（假設為CSV文件），並轉換為DataFrame
symbol='BTC_USDT'
period='Min60'
data = function.check_symbols_kline(symbol, period,  320)

# 假設只考慮最近三個月的K線資料
# start_date = pd.to_datetime('2024-02-01')
# end_date = pd.to_datetime('2024-04-30')
# data = data[(data['time'] >= start_date) & (data['time'] <= end_date)]

# 呼叫 calculate_score 函數計算每一日的評分
scores = calculate_score(data)

#print(data.index)

# 輸出每一日的評分
for i in range(len(data)):
    if scores[i]!=0:
        print('日期:', data.index[i], '評分:', scores[i])
# 讀取股票價格數據（假設為CSV文件），並轉換為DataFrame
#data = pd.read_csv('stock_data.csv')
#     # time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1

def backtest(data):
    positions = []  # 儲存每一天的持倉狀態（1表示買入，-1表示賣出，0表示觀望）
    buy_date = None  # 買入日期
    buy_price = None  # 買入價格
    total_profit = 0  # 總利潤

    # 根據評分變動計算持倉狀態
    for i in range(1, len(data)):
        if buy_price is None:  # 沒有持倉
            if data['Score'].iloc[i] > 0 and data['Score'].iloc[i - 1] < 0:  # 評分從負數轉正數，買入
                positions.append(1)
                buy_date = data['Date'].iloc[i]
                buy_price = data['Close'].iloc[i]
        else:  # 有持倉
            if data['Close'].iloc[i] >= buy_price * 1.1:  # 股價達到10%的利潤目標，賣出
                positions.append(-1)
                total_profit += buy_price * 0.1  # 計算利潤
                sell_date = data['Date'].iloc[i]
                print(f"賣出日期：{sell_date}，利潤：{buy_price * 0.1}")
                buy_date = None
                buy_price = None
            elif data['Close'].iloc[i] <= buy_price * 0.95:  # 股價跌破5%的停損閾值，賣出
                positions.append(-1)
                total_profit += buy_price * -0.05  # 計算利潤
                sell_date = data['Date'].iloc[i]
                print(f"賣出日期：{sell_date}，利潤：{buy_price * -0.05}")
                buy_date = None
                buy_price = None
            else:  # 股價未達到利潤目標或停損閾值，持續持倉
                positions.append(1)

    return total_profit


# 讀取股票價格數據（假設為CSV文件），並轉換為DataFrame
data = pd.read_csv('stock_data.csv')

# 假設只考慮最近三個月的K線資料
start_date = pd.to_datetime('2024-02-01')
end_date = pd.to_datetime('2024-04-30')
data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]

# 呼叫 backtest 函數進行回測
total_profit = backtest(data)

# 輸出總利潤
print('總利潤:', total_profit)
