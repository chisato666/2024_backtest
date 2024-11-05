from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import requests

from binance.client import Client
from binance.enums import *
from myapp.include import config, function, oo_backtest, check_decrease_alert
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io, random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import time
import csv

client = Client(config.api_key, config.api_secret)

from myapp.models import PriceAlert


from django.conf import settings


def backtest_view(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        #df = pd.read_excel(file)
        df = csv.reader(file.read().decode('utf-8').splitlines())
        try:
            function.backtest_excel(df)
        except Exception as error:
            # handle the exception
            print("An save exception occurred: ", error)

        return render(request, 'result.html', {'result': df})

    return render(request, 'upload.html')

def plot_backtest(df_btc,buy_points,sell_points):
    plt.plot(df_btc.index, df_btc['Close'], label='BTC Price')
    plt.plot(df_btc.index, df_btc['EMA_short'], label='EMA Short')
    plt.plot(df_btc.index, df_btc['EMA_long'], label='EMA Long')

    plt.scatter(*zip(*buy_points), color='green', label='Buy')
    plt.scatter(*zip(*sell_points), color='red', label='Sell')
    plt.xlabel('Date/Time')
    plt.ylabel('BTC Price (USDT)')
    plt.title('BTC Price with Buy/Sell Points')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

def graph_view(request):
    # Generate some data for the graph
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]

    # Create the graph
    plt.plot(x, y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Sample Graph')

    # Save the graph to a temporary file
    graph_path = '/Users/apple/PycharmProjects/2024_backtest/myapp/static/graph/graph.png'
    plt.savefig(graph_path)
    plt.close()

    # Render the graph in the template
    return render(request, 'graph.html', {'graph_path': graph_path})



def show_alert(request):
    alert = PriceAlert(
        symbol='symbol',
        interval='17min',
        percentage_decrease=4,
        timestamp=datetime.now()
    )
    alert.save()
    alerts = PriceAlert.objects.all().order_by('-timestamp')
    context = {'alerts': alerts}
    return render(request, 'show_alert.html', context)

# Create your views here.

def check_alert(request):

    symbol_list = ["TARA_USDT", "ASTRA_USDT",'GFT_USDT','BTC_USDT','AUCTION_USDT','WEMIX_USDT','ARKM_USDT','CLORE_USDT']  # Add more symbols as needed
    check_decrease_alert.check_price_decrease(symbol_list)
    alerts = PriceAlert.objects.all().order_by('-timestamp')
    context = {'alerts': alerts}
    return render(request, 'show_alert.html', context)

def say_hello(request):
    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']
    context = { 'symbols': symbols }
    return render(request,'backtest.html',context)


def ajax(request):
    return render(request,'ajax.html')

def research(request):
    return render(request,'research.html')

def macd_report(request):
    #
    #     df['MACD'], df['Signal'] = calculate_macd(df)
    #symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'DOTUSDT', 'OPUSDT', 'AVAXUSDT', 'LINKUSDT', 'SANDUSDT', 'SUIUSDT']
    symbols = ['BTC_USDT',
                   'ETH_USDT',
                   'SOL_USDT',
                   'BIGTIME_USDT',
                   'MEME_USDT',
                   'LINK_USDT',
                   '1000BONK_USDT',
                   'TRB_USDT',
                   'TIA_USDT']
    start_date = '01-01-2024'
    end_date = '21-7-2024'
    periods = ['Week1','Day1']
    report_data = []
    sell_score=''
    sell_signals=''

    #     # time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1
    #symbols= function.get_symbol_list()
    for symbol in symbols:
        # df = pd.read_csv(f'{symbol}_historical_data.csv', parse_dates=['Date'])
        # df.set_index('Date', inplace=True)
        for period in periods:
        #df = function.getdata(symbol, start_date, end_date, periods)
            try:
                df = function.check_symbols_kline(symbol, period, 15)
                print(symbol,df)

                if (len(df) > 2):
                    sell_score, sell_signals = function.check_sell_signals(df)

                    df['MACD'], df['Signal'] = function.calculate_macd(df)
                    cross_up, cross_down = function.check_macd_crosses(df)
                    score, buy_signals = function.check_buy_signals(df)

                    report_data.append({
                        'Symbol': symbol,
                        'Score': score,
                        'Sell_Score': sell_score,
                        'Sell_Signals': sell_signals,
                        'Cross_Up': cross_up.index.tolist(),
                        'Cross_Down': cross_down.index.tolist(),
                        'Buy_Signals': buy_signals,
                        'Period': period
                    })

            except Exception as e:
                print('df error',e)

    report_data.sort(key=lambda x: x['Score'], reverse=True)

    return render(request, 'report/macd_report.html', {'report_data': report_data})

def submit_backtest(request):

    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']
    time_now= int(time.time())

    if request.method=="POST":
        print(request.POST.get('symbol'))
        buy_indicator=(request.POST.get('buy_indicator'))
        buy_operator=(request.POST.get('buy_operator'))
        buy_enter_value=(request.POST.get('buy_enter_value'))

        sell_indicator = (request.POST.get('sell_indicator'))
        sell_operator = (request.POST.get('sell_operator'))
        sell_enter_value = (request.POST.get('sell_enter_value'))

        rules=(request.POST.get('rules'))
        custom=(request.POST.get('custom'))
        moving_sl=(request.POST.get('moving_sl'))
        reverse_trade=(request.POST.get('reverse_trade'))

        in_diff=(request.POST.get('in_diff'))


        ema_short=(request.POST.get('ema_short'))
        ema_long=(request.POST.get('ema_long'))
        over_ema=(request.POST.get('over_ema'))

        sell_type=(request.POST.get('sell_type'))


        symbol = request.POST.get('symbol')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        period = request.POST.get('period')

        tp = request.POST.get('tp')
        sl = request.POST.get('sl')


        buy_value=[buy_indicator,buy_operator,buy_enter_value]
        sell_value=[sell_indicator,sell_operator,sell_enter_value]


        try:
            print(rules)
            profits=0
            pro_count=0
            buyarr=[]

            if (custom=='yes'):
               print('custom')
               instance = oo_backtest.Backtest(symbol, start_date, end_date, period, buy_value, sell_value)

               print(instance.buy_arr)
               print(instance.buy_arr.index)
               print(instance.sell_arr)
               print(instance.profit)

               buyarr = ((zip(instance.buy_arr.index, instance.buy_arr, instance.sell_arr.index, instance.sell_arr,instance.profit)))

               profits = (instance.cumul_profit) * 100
               pro_count = ((pd.Series(instance.profit) > 0).value_counts())

            else:

                if (rules == '1'):
                    df = function.getdata(symbol, start_date, end_date, period)
                    #print(df)
                    profits, pro_list, pro_count, buyarr, plt = function.get_rules1(df,in_diff,tp,sl)
                    profits = (profits - 1) * 100
                    # plot=get_plot(plt)
                    # plt.savefig(os.path.join('static', 'images', 'plot.png'))
                    print("rules 1")
                if (rules == '2'):
                    instance = oo_backtest.Backtest(symbol, start_date, end_date, period,buy_value,sell_value)

                    print(instance.buy_arr)
                    print(instance.buy_arr.index)
                    print(instance.sell_arr)
                    print(instance.profit)

                    buyarr = ((zip(instance.buy_arr.index, instance.buy_arr, instance.sell_arr.index, instance.sell_arr, instance.profit)))


                    profits = (instance.cumul_profit) * 100
                    pro_count = ((pd.Series(instance.profit) > 0).value_counts())

                    print("rules 2")


                if (rules == '3'):


                    # start_date = '01-01-2023'
                    # end_date = '12-05-2023'
                    # periods = ['1d']
                    sell_points = []
                    buy_points = []


                    df = function.getdata(symbol, start_date, end_date, period)

                    profits, pro_list, pro_count, buyarr, plt = function.get_rules3(df, float(tp), float(sl), moving_sl, sell_type, over_ema, int(ema_short),int(ema_long),reverse_trade)

                   # profits, sell_value, buy_value = function.get_rules3(df, float(tp), float(sl))
                    #print(symbol, period, str(int(total)))
                    #plot_backtest(df, buy_points, sell_points)


                # count_profits=((pd.Series(profits) > 0).value_counts())
                # print((pd.Series(profits) + 1).prod())
                # print((pd.Series(profits) + 1).cumprod())

                # print(rules, symbol, start_date, end_date, period)

        except Exception as e:
            return HttpResponse((e))


    data = {
        "profit": profits,
        "count": pro_count,
        "period": period,
        "symbol": symbol,
        "buy_value": buy_value,
        "sell_value": sell_value,
        "time_now": time_now

    }

    context = {"data": data, 'symbols': symbols , 'buyarr': buyarr}
    return render(request,'backtest.html',context)

def submit_research(request):

    if request.method=="POST":
        percent=(request.POST.get('enter_percent'))
        rules=(request.POST.get('rules'))
        period = request.POST.get('period')
        limit = request.POST.get('limit')
        ema_short = request.POST.get('ema_short')
        ema_long = request.POST.get('ema_long')
        cross_direction = request.POST.get('cross_direction')


        # symbol = request.POST.get('symbol')
        # start_date = request.POST.get('start_date')
        # end_date = request.POST.get('end_date')
        # period = request.POST.get('period')



        try:
            print(rules)
            if (rules == '1'):
                list = function.check_symbols_with_increased_5d(percent, period, limit)
                print('list',list)
                buyarr = pd.DataFrame(list)
                print('buyarr',buyarr)

                print("rules 1")
                
            elif (rules == '2'):
                crypto_list = function.get_symbol_list()
                print(crypto_list)
                # time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1

                interval = "Week1"  # 1-hour candlestick data


                interval = "Day1"  # 1-hour candlestick data
                count=0
                add_list=[]
                list=[]
                for symbol in crypto_list:
                    df = function.check_symbols_kline(symbol, period, int(ema_long) )
                    add_list=function.check_ema_cross(df, int(limit), symbol,int(ema_short),int(ema_long),cross_direction)
                    if add_list:
                        rank = function.get_market_cap_rank(symbol.split('_')[0])
                        add_list.append(rank)
                        list.append(add_list)

                list.sort(key=lambda x: x[2])
                # market_cap_rankings = {}
                #
                # for crypto in crypto_list:
                #     rank = get_market_cap_rank(crypto)
                #     if rank is not None:
                #         market_cap_rankings[crypto] = rank
                #
                # sorted_rankings = sorted(market_cap_rankings.items(), key=lambda x: x[1])




                buyarr = pd.DataFrame(list)
                print('buyarr',buyarr)

                print("rules 2")

            elif (rules == '3'):
                crypto_list = function.get_symbol_list()
                print(crypto_list)
                # time_step = 'Day1' # 合约的参数：间隔: Min1、Min5、Min15、Min30、Min60、Hour4、Hour8、Day1、Week1、Month1，不填时默认Min1

                interval = "Week1"  # 1-hour candlestick data

                interval = "Day1"  # 1-hour candlestick data
                count = 0
                symbol_list=[]
                add_list = []
                list = []

                for symbol in crypto_list:
                    print(symbol)
                    data = function.check_symbols_kline(symbol, period,  40)
                    if (len(data)>14):
                        scores = function.calculate_scores(data)
                        print( ' scores: ', len(scores), 'data:', len(data))
                        if scores[len(data)-1] > 1 and scores[len(data)-2] < 0:  # 評分從負數轉正數，買入
                            symbol_list.append(symbol)
                            line=('Symbol: ', symbol, ' 日期:', data.index[len(data)-2], '評分:', scores[len(data)-2])
                            list.append(line)
                            line2=('Symbol: ', symbol, ' 日期:', data.index[len(data)-1], '評分:', scores[len(data)-1])
                            list.append(line2)

                            print(line,line2)

            # count_profits=((pd.Series(profits) > 0).value_counts())
            # print((pd.Series(profits) + 1).prod())
            # print((pd.Series(profits) + 1).cumprod())

            # print(rules, symbol, start_date, end_date, period)

        except Exception as e:
            return HttpResponse((e))


    data = {
        "enter_percent": percent,
        "period": period,
        "limit": limit

    }

    context = {"in_value": data , 'buyarr': list}
    return render(request,'research.html',context)


def get_btcusdt_price(request):
    # Replace YOUR_API_KEY with your actual Binance API key
    # api_key = 'VLQd7y0l2OQhtWZz3TWCjSyV3m7Yuip095BbAjrEZuzcUGl3aSgqR5JkUTbblGrX'
    #
    # # Make a request to Binance API to get the ticker price
    # url = 'https://api.binance.com/api/v3/ticker/price'
    # params = {
    #     'symbol': 'BTCUSDT'
    # }
    # headers = {
    #     'X-MBX-APIKEY': api_key
    # }
    #
    # response = requests.get(url, params=params, headers=headers)
    # data = response.json()
    #btcusdt_price = data['price']


    rate = 0.05
    data = function.get_symbols_with_price_increase(rate)

    # for symbol in data:
    #     symbol_name=symbol[0]
    #     increase_percent=symbol[1]
    # # Extract the price from the response

    # Return the price as a JSON response
    return JsonResponse({'symbol_name': data})


def backtest_score(request):
    if request.method == 'POST':
        form = BacktestForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            score_threshold = form.cleaned_data['score_threshold']
            timeframe = form.cleaned_data['timeframe']

            tp_percent = form.cleaned_data['tp_percent'] / 100
            sl_percent = form.cleaned_data['sl_percent'] / 100
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Load your data (adjust the path as necessary)
            # df = pd.read_csv('your_data.csv', parse_dates=['Date'])
            # df.set_index('Date', inplace=True)

            df = function.check_symbols_kline(symbol, periods, 105)

            df = df[(df.index >= start_date) & (df.index <= end_date)]

            # Calculate scores and perform backtest
            scores = function.calculate_scores_over_intervals(df, interval_days=10)
            trades, total_profit = function.backtest_trading_strategy(df, scores, tp_percent, sl_percent)

            # Save the result (optional)
            BacktestResult.objects.create(
                symbol=symbol,
                score_threshold=score_threshold,
                tp_percent=tp_percent * 100,
                sl_percent=sl_percent * 100,
                start_date=start_date,
                end_date=end_date,
                total_profit=total_profit
            )

            return render(request, 'backtest_score/results.html', {'total_profit': total_profit, 'trades': trades})

    else:
        form = BacktestForm()

    return render(request, 'backtest_score/form.html', {'form': form})


def getProfiles(request):
    rate=0.05
    symbols =function.get_symbols_with_price_increase(rate)

    #print(symbols)
    return JsonResponse({'symbols': list(symbols)})


def list_symbol(request):
    rate=0.05
    symbols =function.get_symbols_with_price_increase(rate)

    #print(symbols)
    return JsonResponse({'symbols': list(symbols)})

# def list_symbol(request):
#     rate=0.05
#     symbols =function.get_symbols_with_price_increase(rate)
#
#     #print(symbols)
#     return render(request,'list_symbol.html',{'symbols': symbols})