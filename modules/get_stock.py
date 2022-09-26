import requests
import yfinance as yf
from tqdm import tqdm 
import pandas as pd

all_stock_info = pd.read_csv('../static/all_stock_info.csv')

for i in all_stock_info.index:

    # 抓取股票資料
    stock_id = all_stock_info.loc[i, '證券代號'] + '.TW'
    stock_name = all_stock_info.loc[i, '證券名稱']
    data = yf.download(stock_id, start='2012-01-01', end='2022-09-26')
    data.to_csv(f'../static/stocks/{stock_id}.csv')

    