import os
import sqlite3
import pandas as pd


def init_db(path="database"):
    conn = sqlite3.connect(os.path.join(path, 'finance_feature.db'))
    sql = """
        CREATE TABLE features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id TEXT,
            mean REAL,
            variance REAL,
            skewness REAL, 
            kurt REAL
        );
    """
    conn.execute(sql)
    conn.commit()

    sql = """
            CREATE TABLE classification (
                `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                `stock_id` TEXT,
                `group` REAL,
                `sortino_ratio` REAL
            );"""
    conn.execute(sql)
    conn.commit()

    conn.close()


def create_feature(stock_id, mean, variance, skewness, kurt, path="database"):
    conn = sqlite3.connect(os.path.join(path, 'finance_feature.db'))
    sql = """
        INSERT INTO features (stock_id, mean, variance, skewness, kurt)
        VALUES (?, ?, ?, ?, ?);
    """
    conn.execute(sql, (stock_id, mean, variance, skewness, kurt))
    conn.commit()
    conn.close()


def main(path_to_stock="static/stocks"):
    # generate feature from stocks_info
    for (root, dirs, files) in os.walk(path_to_stock):
        for file in files:
            if file.endswith(".csv"):
                df = pd.read_csv(os.path.join(path_to_stock, file))
                stock_id = file[:-4]

                # 資料篩選
                df = df[~(df['Close'] == 0)]

                # 計算損益比率
                df = df['Close'].pct_change().dropna()

                # 取得損益比率平均
                df_mean = df.mean()
                # 取得損益比率標準差
                df_std = df.std()

                # 篩選超過兩個標準差的值
                df = df[df < (df_mean + 2 * df_std)]
                df = df[df > (df_mean - 2 * df_std)]

                # 取得平均、變異數、峰度、偏度
                mean = df.mean()
                var = df.var()
                skewness = df.skew()
                kurt = df.kurt()

                # 存進資料庫
                create_feature(stock_id, mean, var, skewness, kurt, path="../database")


if __name__ == "__main__":
    init_db('../database')
    main(path_to_stock='../static/stocks', )
