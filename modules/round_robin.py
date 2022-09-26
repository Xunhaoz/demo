import os
import sqlite3
import pandas as pd
import kmeans_allocation as ka


def read_classification():
    conn = sqlite3.connect("../database/finance_feature.db")
    sql = """
            SELECT * from classification
        """
    result = conn.execute(sql).fetchall()
    conn.close()
    return result


def select_data(stock_id):
    conn = sqlite3.connect('../database/finance_feature.db')
    sql = "SELECT * FROM features WHERE stock_id = (?)"
    data = conn.execute(sql, (stock_id,)).fetchone()
    conn.close()
    return data


def download_from_finmind(stock_id):
    api = DataLoader()
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMi0wOS0xOSAwNzoyMDoxMSIsInVzZXJfaWQiOiJYdW5oYW96IiwiaXAiOiIxMTEuMjQxLjYyLjIyIn0.oHQQ78x6E7jS2zocX3zfRyur_R3gr7YhR9c465Y3pek"
    api.login_by_token(api_token=token)
    df = api.taiwan_stock_daily(
        stock_id=stock_id,
        start_date='2012-01-1',
        end_date='2022-09-19'
    )
    return df


if __name__ == "__main__":
    data = read_classification()
    classes = [[], [], [], [], [], []]
    data_id_sortinoRatio = []

    for stock in data:
        classes[int(stock[2])].append((stock[1], stock[3]))
        data_id_sortinoRatio.append((stock[1], stock[3]))

    for key, class_ in enumerate(classes):
        classes[key] = sorted(class_, key=lambda tup: tup[1], reverse=True)

        print(key)
        count = 0
        for class__ in classes[key]:
            df = pd.read_csv(f'../static/stocks/{class__[0]}.csv')
            if count < 5:
                print(class__[0])
                # print(select_data(class__[0]))
                count += 1
            else:
                break
