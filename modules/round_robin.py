import os
from random import shuffle
import sqlite3
import pandas as pd
import shutil
import modules.kmeans_allocation as kmeans_allocation
import yfinance as yf
import datetime

def read_classification():
    conn = sqlite3.connect("database/finance_feature.db")
    sql = """
            SELECT * from classification
        """
    result = conn.execute(sql).fetchall()
    conn.close()
    return result


def select_data(stock_id):
    conn = sqlite3.connect('database/finance_feature.db')
    sql = "SELECT * FROM features WHERE stock_id = (?)"
    data = conn.execute(sql, (stock_id,)).fetchone()
    conn.close()
    return data

def round_robin():
    data = read_classification()
    classes = [[], [], [], [], [], []]
    represent_stocks = []

    for i in data:
        classes[int(i[2])].append(i)

    for i, j in enumerate(classes):
        classes[i].sort(key=lambda s:s[3], reverse=True)
    
    i = 0
    while len(represent_stocks) < 30 + 1:
        for j in classes:
            if i < len(j):
                represent_stocks.append(j[i])
        i += 1
    
    for i in range(1, 6):
        if os.path.exists(f'static/stocks/group{i}'):
            shutil.rmtree(f'static/stocks/group{i}')        

    shuffle(represent_stocks)
    
    dt = datetime.datetime.now()
    for k, i in enumerate(represent_stocks):
        k = k % 5 + 1
        if not os.path.exists(f'static/stocks/group{k}'):
            os.mkdir(f'static/stocks/group{k}')

        stock_data = yf.Ticker(i[1]+'.TW')
        df = yf.download(i[1]+'.TW', start='2012-01-01', end=f'{dt.year}-{dt.month}-{dt.day}')
        df = df.rename({'Open':'open','High':'max','Low':'min','Close':'close','Adj Close':'adj close' ,'Volume':'volumn'}, axis=1)
        df.index.name = 'date'
        df.to_csv(f"static/stocks/group{k}/{i[1]}.csv")    


if __name__ == "__main__":
    data = read_classification()
    classes = [[], [], [], [], [], []]
    represent_stocks = []

    for i in data:
        classes[int(i[2])].append(i)

    for i, j in enumerate(classes):
        classes[i].sort(key=lambda s:s[3], reverse=True)
    
    i = 0
    while len(represent_stocks) < 30 + 1:
        for j in classes:
            if i < len(j):
                represent_stocks.append(j[i])
        i += 1
    
    for i in range(1, 6):
        if os.path.exists(f'static/stocks/group{i}'):
            shutil.rmtree(f'static/stocks/group{i}')        

    shuffle(represent_stocks)
    
    dt = datetime.datetime.now()
    for k, i in enumerate(represent_stocks):
        k = k % 5 + 1
        if not os.path.exists(f'static/stocks/group{k}'):
            os.mkdir(f'static/stocks/group{k}')

        stock_data = yf.Ticker(i[1]+'.TW')
        df = yf.download(i[1]+'.TW', start='2012-01-01', end=f'{dt.year}-{dt.month}-{dt.day}')
        df = df.rename({'Open':'open','High':'max','Low':'min','Close':'close','Adj Close':'adj close' ,'Volume':'volumn'}, axis=1)
        df.index.name = 'date'
        df.to_csv(f"../static/stocks/group{k}/{i[1]}.csv")

    
    

    # for stock in data:
    #     classes[int(stock[2])].append((stock[1], stock[3]))
    #     data_id_sortinoRatio.append((stock[1], stock[3]))

    # for key, class_ in enumerate(classes):
    #     classes[key] = sorted(class_, key=lambda tup: tup[1], reverse=True)

    #     print(key)
    #     count = 0
    #     for class__ in classes[key]:
    #         df = pd.read_csv(f'../static/stocks/{class__[0]}.csv')
    #         if count < 5:
    #             print(class__[0])
    #             # print(select_data(class__[0]))
    #             count += 1
    #         else:
    #             break
