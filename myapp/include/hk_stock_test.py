import yfinance as yf

# 定義港股代碼

# 使用 yfinance 庫獲取港股資料
#stock_data = yf.download(symbol, start='2021-01-01', end='2022-12-31')

# 定義港股代碼
symbol = '0005.HK'  # 以腾讯控股（0005.HK）為例

# 使用 yfinance 庫獲取港股資料
stock_data = yf.Ticker(symbol)
print(stock_data.info)
# 獲取港股的PE和ROE數據
# pe_ratio = stock_data.info['trailingPE']
# roe = stock_data.info['roe']
#
# # 輸出結果
# print("PE Ratio:", pe_ratio)
# print("ROE:", roe)
# # 檢視獲取的資料
# print(stock_data.head())