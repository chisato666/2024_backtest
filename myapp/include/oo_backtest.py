import yfinance as yf
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt

from binance.client import Client
client= Client()


class Backtest:
    def __init__(self, symbol, start_date, end_date, period,buy_value,sell_value):
        self.symbol = symbol
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
        self.buy_value = buy_value
        self.sell_value = sell_value

        #self.df = yf.download(self.symbol, start='2023-07-10',period = "1y",interval = "1h")
        self.getdata()


        if self.df.empty:
            print('No data pulled')
        else:
            self.calc_indicators()
            self.generate_signals()
            self.loop_it()
            self.profit = self.calc_profit()
            self.max_dd = self.profit.min()
            self.cumul_profit = (self.profit + 1).prod() - 1
       #     self.plot_chart()

    def getdata(self):

        self.df = pd.DataFrame(client.get_historical_klines(self.symbol,  self.period, self.start_date, self.end_date))
        self.df = self.df.iloc[:, :6]
        self.df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        self.df.set_index('Time', inplace=True)
        self.df.index = pd.to_datetime(self.df.index, unit='ms')
        self.df = self.df.astype(float)



    def calc_indicators(self):
        self.df['ma_20'] = self.df.Close.rolling(20).mean()
        self.df['vol'] = self.df.Close.rolling(20).std()
        self.df['upper_bb'] = self.df.ma_20 + (2 * self.df.vol)
        self.df['lower_bb'] = self.df.ma_20 - (2 * self.df.vol)
        self.df['ret'] = self.df.Close.pct_change()
        self.df['sl'] = self.df.Close * 0.98
        self.df['tp'] = self.df.Close * 1.02

        self.df['price'] = self.df.Open.shift(-1)

        self.df['rsi'] = ta.RSI(self.df.Close)
        self.df.dropna(inplace=True)

    def generate_signals(self):
        choices = ['Buy', 'Sell']

        program = 'conditions = [(self.df.rsi ' + self.buy_value[1] + ' ' + str( self.buy_value[2]) + ') , (self.df.rsi ' + self.sell_value[1] + ' ' + str( self.sell_value[2]) + ')]\nself.df[\'signal\'] = np.select(conditions, choices)'
        print('Generate ' , program)

        exec(program)
        #conditions = [(self.df.rsi < 30), (self.df.rsi > 70)]
        #conditions = [(self.df.rsi < 30) & (self.df.Close < self.df.lower_bb),
         #             (self.df.rsi > 70) & (self.df.Close > self.df.upper_bb)]

        conditions2 = [(self.df.ret > 0.01),
                      (self.df.High > self.df.tp) | (self.df.Low < self.df.sl)]

        self.df.signal = self.df.signal.shift()
        self.df.dropna(inplace=True)

    def loop_it(self):
        position = False
        buydates, selldates, all_arr = [], [],[]

        for index, row in self.df.iterrows():
            if not position and row['signal'] == 'Buy':
                position = True
                buydates.append(index)
            if position and row['signal'] == 'Sell':
                position = False
                selldates.append(index)

        self.buy_arr = self.df.loc[buydates].Open
        self.sell_arr = self.df.loc[selldates].Open

    def calc_profit(self):
        if self.buy_arr.index[-1] > self.sell_arr.index[-1]:
            self.buy_arr = self.buy_arr[:-1]
        return (self.sell_arr.values - self.buy_arr.values) / self.buy_arr.values

    # def plot_chart(self):
    #     plt.figure(figsize=(10, 5))
    #     plt.plot(self.df.Close)
    #     plt.scatter(self.buy_arr.index, self.buy_arr.values, marker='^', c='g')
    #     plt.scatter(self.sell_arr.index, self.sell_arr.values, marker='v', c='r')


symbol='ETHUSDT'
start_date='2023-06-10'
end_date='2023-08-02'
period='1h'
buy_value=['rsi','<',50]
sell_value=['rsi','>',70]

instance = Backtest(symbol,start_date,end_date,period,buy_value,sell_value)

print(instance.buy_arr)

print(instance.sell_arr)
#
print(instance.profit)
#
print(instance.cumul_profit)
pro_count = ((pd.Series(instance.profit) > 0).value_counts())
print(pro_count)
print(list(zip(instance.buy_arr.index,instance.buy_arr,instance.sell_arr,instance.profit)))

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 20)

# print(instance.df)

#instance.plot_chart()