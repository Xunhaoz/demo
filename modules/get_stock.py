import requests
import yfinance as yf
from tqdm import tqdm 
import pandas as pd
import shutil
import os


def get_stock():
    link = 'https://quality.data.gov.tw/dq_download_json.php?nid=11549&md5_url=bb878d47ffbe7b83bfc1b41d0b24946e'
    r = requests.get(link)
    data = pd.DataFrame(r.json())
    data.to_csv('static/stocks/stock_id.csv', index=False, header = True)

    if os.path.exists('static/stocks/stocksSource'):
        shutil.rmtree('static/stocks/stocksSource')
    os.mkdir('static/stocks/stocksSource')


    for i in tqdm(data.index):
        # 抓取股票資料
        stock_id = data.loc[i, '證券代號'] + '.TW'
        stock_data = yf.Ticker(stock_id)
        df = stock_data.history(period="max")
        df.to_csv(f"static/stocks/stocksSource/{stock_id[:-3]}.csv")
        