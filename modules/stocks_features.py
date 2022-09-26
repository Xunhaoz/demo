import logging
import os
import pandas as pd


def is_file_exist(file_name, path="static/stocks"):
    file_path = os.path.join(path, file_name + '.csv')
    if os.path.exists(file_path):
        return True
    return False


def cal_max_drawdown(path):
    df = pd.read_csv(path)
    max_price = df['close'].max(axis=0, skipna=True)
    min_price = df['close'].min(axis=0, skipna=True)
    max_drawdown = (min_price - max_price) / max_price
    logging.info(f"max_price: {max_price}, min_price: {min_price}, max_drawdown: {max_drawdown}")
    return max_price, min_price, max_drawdown


def cal_irr(path):
    df = pd.read_csv(path)['close']
    dr = df / df.shift(1)  # 取得損益百分比
    dr = dr.dropna()
    pr = dr.prod() ** (1 / len(dr))  # 幾何平均數
    apr = pr ** 252
    logging.info(f"apr: {apr}")
    return apr


def cal_volatility(path):
    df = pd.read_csv(path)['close']
    dr = df.pct_change().dropna()
    volatility = dr.std() * (252 ** 0.5)  # 年畫波動度
    logging.info(f"volatility: {volatility}")
    return volatility


def cal_skewness(path):
    df = pd.read_csv(path)['close']
    dr = df.pct_change().dropna()
    skewness = dr.skew()
    kurt = dr.kurt()
    logging.info(f"skewness: {skewness}, kurt: {kurt}")
    return skewness, kurt


def cal_sortino_ratio(path):
    df = pd.read_csv(path)
    df = df[~(df['Close'] == 0)]['Close']
    dr = df.pct_change().dropna()
    mean = dr.mean() * 252
    std_neg = dr[dr < 0].std() * (252 ** 0.5)
    sortino_ratio = mean / std_neg
    logging.info(f"sortino_ratio: {sortino_ratio}")
    return sortino_ratio
