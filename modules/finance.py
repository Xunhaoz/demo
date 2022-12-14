# System import
import os
import pprint as pp
import json
import argparse
import logging

# Twisted import
import numpy as np
import pandas as pd
from argparse import RawTextHelpFormatter
from tqdm import tqdm
import pypfopt
from pypfopt import expected_returns, risk_models
import yfinance as yf

'''
This is a scrip which can help calculating better assets allocation from stocks history data. 
'''


class StockClass:
    """
        this is a stock class to read stocks individually.

        Inputs:
            dir_path: string
            csv_name: string

        Public methods:
            get_stock_name(): return string
            get_stock_dataframe(): return dataframe
            get_stock_period(): return dict{stock_data_len:int, start_time:str, end_time:str}
            get_stock_pct_change(mean: bool):   if mean is true, return mean_pct_change: int
                                                else return a dataframe
                                                !important in order to count pct_change we will lose the fist data
                                                so the length of return dataframe will minus one
            get_stock_performance(): return dict{expect_return:float, sharpe_ratio:float}
            get_all_stock_info(): return all above in a dic
    """

    def __init__(self, dir_path, csv_name):
        self.stock_dataframe = pd.read_csv(os.path.join(dir_path, csv_name))
        self.stock_name = csv_name[:-4]
        self.stock_data_len = len(self.stock_dataframe)
        self.pct_change = self.stock_dataframe['close'].pct_change().dropna()

    def get_stock_name(self):
        return self.stock_name

    def get_stock_dataframe(self):
        return self.stock_dataframe

    def get_stock_period(self):
        start_time = self.stock_dataframe['date'][0]
        end_time = self.stock_dataframe['date'][self.stock_data_len - 1]
        return {'stock_data_len': self.stock_data_len, 'start_time': start_time, 'end_time': end_time}

    # drop na would make the length minus one
    def get_stock_pct_change(self, mean=False):
        return self.pct_change.dropna().mean() if mean else self.pct_change.dropna()

    def get_stock_performance(self):
        expect_return = self.pct_change.mean() * 252
        sharpe_ratio = expect_return / (self.pct_change.std() * (252 ** 0.5))
        return {'expect_return': expect_return, 'sharpe_ratio': sharpe_ratio}

    def get_all_stock_info(self):
        info = {}
        info['name'] = self.stock_name
        info['mean_pct_change'] = self.get_stock_pct_change(mean=True)
        info['period'] = self.get_stock_period()
        info['performance'] = self.get_stock_performance()
        return info


def data_pre_treatment(stocks_class_list):
    """
    ???????????????
    ??????????????????tickit?????????dataframe???????????????
    ?????????????????????????????????????????????dataframe???
    """

    stock_df_result = stocks_class_list[0].get_stock_dataframe()['date']  # ???????????????
    for stock in stocks_class_list:  # ?????????????????????????????????
        print(stock)
        stock_df = stock.get_stock_dataframe()[['close', 'date']]
        stock_df = stock_df[~(stock_df['close'] == 0.0)]
        stock_df = stock_df.rename(columns={'close': stock.get_stock_name()})
        stock_df_result = pd.merge(stock_df_result, stock_df, on="date")
    # ??????????????????????????????????????????????????????????????????????????????
    data_for_pypfopt = stock_df_result.set_index('date')
    return data_for_pypfopt


def check_stock_info(stock_class_list, stock_name, save):
    """???????????????name, mean_pct_change, period, and performance"""
    result_dict = {}
    if stock_name == 'all':
        for index, stock in enumerate(stock_class_list):
            result_dict[index] = stock.get_all_stock_info()
    else:
        for stock in stock_class_list:
            if stock.get_stock_name() == stock_name:
                result_dict = stock.get_all_stock_info()
    if save:
        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)
    else:
        pp.pprint(result_dict)
    return result_dict


def save_result(weights, clean_weight, portfolio_performance, save):
    """
        ??????weights, clean_weight, portfolio_performance, and save
        ??? save??? True????????????.json??? ????????????????????????
    """
    result_dict = {'weights': weights, 'clean_weight': clean_weight, 'performance': {}}
    result_dict['performance']['expected_annual_return'] = portfolio_performance[0]
    result_dict['performance']['annual_volatility'] = portfolio_performance[1]
    result_dict['performance']['sharpe_ratio'] = portfolio_performance[2]
    # if save:
    #     with open('result.json', 'w', encoding='utf-8') as f:
    #         json.dump(result_dict, f, ensure_ascii=False, indent=4)
    # else:
    #     pp.pprint(result_dict)
    return result_dict


def check_boundary_exist(stock_boundary_path, stock_class_list):
    """
    ?????????????????????????????????????????????
    ??????????????? ????????????????????????????????????????????????None
    """
    if not os.path.exists(stock_boundary_path):
        stock_name_dict = {}
        for stock in stock_class_list:
            stock_name_dict[stock.stock_name] = {}
            stock_name_dict[stock.stock_name]['upper_bound'] = 0.0
            stock_name_dict[stock.stock_name]['lower_bound'] = 0.0
        with open(stock_boundary_path, 'w', encoding='utf-8') as f:
            json.dump(stock_name_dict, f, ensure_ascii=False, indent=4)
        logging.error('boundary.json doesn\'t exits')
        return
    else:
        with open(stock_boundary_path, 'r') as f:
            boundary_dict = json.load(f)

    upper_bound_array = []
    lower_bound_array = []
    has_return = False
    for stock in boundary_dict:
        has_return = True
        upper_bound_array.append(boundary_dict[stock]['upper_bound'])
        lower_bound_array.append(boundary_dict[stock]['lower_bound'])
    return upper_bound_array, lower_bound_array, has_return


def exec_general_efficient_frontier(stock_class_list, stocks_df, expected_returns, covariance_matrix, risk_free_rate,
                                    weight_bounds=None, stock_boundary_path=None, target_return=None,
                                    market_neutral=None, ):
    """?????????????????? ???????????????"""
    # ??????????????????
    ef = pypfopt.efficient_frontier.EfficientFrontier(expected_returns, covariance_matrix)

    # ??????????????????
    if stock_boundary_path is not None:
        if not check_boundary_exist(stock_boundary_path, stock_class_list):
            return
        upper_bound_array, lower_bound_array, has_return = check_boundary_exist(stock_boundary_path, stock_class_list)
        ef.add_constraint(lambda x: x <= np.array(upper_bound_array))
        ef.add_constraint(lambda x: x >= np.array(lower_bound_array))

    # ???????????????????????????
    if target_return is not None:
        # ??????????????????????????????????????????????????????
        weights = ef.efficient_return(target_return=target_return, market_neutral=market_neutral)
    else:
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)  # ??????????????????????????????????????????
    result_dict = save_result(weights, ef.clean_weights(), ef.portfolio_performance(risk_free_rate=risk_free_rate),
                              False)
    return result_dict


def exec_black_litterman(stock_class_list, stocks_df, covariance_matrix, vews_path,
                         weight_bounds, stock_boundary_path, target_return, market_neutral, risk_free_rate, save):
    """??? views, prior?????????????????????????????????????????????????????????"""
    # ??????????????????
    if not os.path.exists(vews_path):
        stock_name_dict = {}
        for stock in stock_class_list:
            stock_name_dict[stock.stock_name] = 0.0
        with open(vews_path, 'w', encoding='utf-8') as f:
            json.dump(stock_name_dict, f, ensure_ascii=False, indent=4)
        logging.error('vews.json doesn\'t exits')
        return
    else:
        with open(vews_path, 'r') as f:
            viewdict = json.load(f)

    # ?????????????????????
    mcaps = {}
    for stock in tqdm(stock_class_list):
        mcaps[stock.get_stock_name()] = yf.Ticker(stock.get_stock_name()).info["marketCap"]

    # ???????????????????????????????????????????????????
    delta = pypfopt.black_litterman.market_implied_risk_aversion(stocks_df)
    prior = pypfopt.black_litterman.market_implied_prior_returns(mcaps, delta, covariance_matrix)

    # ??????????????????????????????
    bl = pypfopt.BlackLittermanModel(S, pi=prior, absolute_views=viewdict, prior=prior)
    rets = bl.bl_returns()
    ef = pypfopt.efficient_frontier.EfficientFrontier(rets, S, weight_bounds=weight_bounds)
    if stock_boundary_path != 'None':
        if not check_boundary_exist(stock_boundary_path, stock_class_list):
            return
        upper_bound_array, lower_bound_array, has_return = check_boundary_exist(stock_boundary_path, stock_class_list)
        ef.add_constraint(lambda x: x <= np.array(upper_bound_array))
        ef.add_constraint(lambda x: x >= np.array(lower_bound_array))
    if target_return:
        weights = ef.efficient_return(target_return=target_return, market_neutral=market_neutral)
    else:
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
    result_dict = save_result(weights, ef.clean_weights(), ef.portfolio_performance(),
                              save)
    return result_dict


def exec_hierarchical_risky_party(stocks_df, covariance_matrix, risk_free_rate, frequency, save):
    """?????????pct_change, covariance_matrix, and ???????????? ?????? Hierarchical Risk Parity????????????"""
    returns = stocks_df.pct_change().dropna()
    HRP = pypfopt.hierarchical_portfolio.HRPOpt(returns=returns, cov_matrix=covariance_matrix)
    result_dict = save_result(HRP.optimize(), HRP.clean_weights(),
                              HRP.portfolio_performance(risk_free_rate=risk_free_rate, frequency=frequency), save)

    return result_dict


def for_demo(risk_free_rate):
    INPUT_PATH = 'static/stocks'
    STOCK_CLASS_LIST = []

    if risk_free_rate < 0.01:
        INPUT_PATH += '/group1'
    elif 0.01 < risk_free_rate < 0.02:
        INPUT_PATH += '/group2'
    elif 0.02 < risk_free_rate < 0.3:
        INPUT_PATH += '/group3'
    elif 0.03 < risk_free_rate < 0.04:
        INPUT_PATH += '/group4'
    else:
        INPUT_PATH += '/group5'

    for root, dirs, files in os.walk(INPUT_PATH):
        for file in files:
            if file.endswith('.csv'):
                stock_class = StockClass(INPUT_PATH, file)
                STOCK_CLASS_LIST.append(stock_class)

    # get every stocks' Close price and return a dataframe
    STOCKS_DF = data_pre_treatment(STOCK_CLASS_LIST)

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(STOCKS_DF)
    S = risk_models.CovarianceShrinkage(STOCKS_DF).ledoit_wolf()

    result = exec_general_efficient_frontier(STOCK_CLASS_LIST, STOCKS_DF, mu, S, risk_free_rate)

    stocksPctChange = STOCKS_DF.pct_change().dropna().sum(axis=1)
    pctPeriod = []
    pctChange = []
    for index, value in stocksPctChange.iteritems():
        if index > "2022-08-16":
            pctPeriod.append(index)
            pctChange.append(int(value * 100000) / 1000)

    result['pct_period'] = pctPeriod
    result['pct_change'] = pctChange
    return result


if __name__ == '__main__':
    # add argument
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('--mode', '-M', default=1, type=int, required=False, help='Choose optimization methods')
    parser.add_argument('--input_path', '-P', default='./source', type=str, required=False,
                        help='Path to data directory')
    parser.add_argument('--stock_name', '-SName', default='all', type=str, required=False,
                        help='The stock you want to check independently')
    parser.add_argument('--save', '-S', default='False', type=str, required=False,
                        help='save the result to ./result.csv')
    parser.add_argument('--weight_bounds', '-WB', default=[0, 1], nargs=2, type=int, required=False,
                        help='set weight_bounds, two nums are seperated with space')
    parser.add_argument('--market_neutral', '-MN', default='False', type=str, required=False,
                        help='set market_neutral')
    parser.add_argument('--vews_path', '-VP', default='vews.json', type=str, required=False,
                        help='the path to vews.json')
    parser.add_argument('--target_return', '-TR', default=0.0, type=float, required=False,
                        help='set target return')
    parser.add_argument('--risk_free_rate', '-RFR', default=0.02, type=float, required=False,
                        help='set risk free rate')
    parser.add_argument('--frequency', '-F', default=252, type=int, required=False,
                        help='number of time periods in a year, defaults to 252')
    parser.add_argument('--stocks_boundary_path', '-BP', default='None', type=str, required=False,
                        help='set stocks boundary')
    # read args
    args = parser.parse_args()
    MODE = args.mode
    INPUT_PATH = args.input_path
    STOCK_NAME = args.stock_name
    WEIGHT_BOUNDS = tuple(args.weight_bounds)
    MARKET_NATURAL = True if args.market_neutral == 'True' else False
    SAVE = True if args.save == 'True' else False
    VEWS_PATH = args.vews_path
    TARGET_RETURN = args.target_return
    RISK_FREE = args.risk_free_rate
    FREQUENCY = args.frequency
    STOCKS_BOUNDARY_PATH = args.stocks_boundary_path
    # read stock.csv in dir_path and create the stock object
    STOCK_CLASS_LIST = []
    for root, dirs, files in os.walk(INPUT_PATH):
        for file in files:
            if file.endswith('.csv'):
                stock_class = StockClass(INPUT_PATH, file)
                STOCK_CLASS_LIST.append(stock_class)
    STOCK_CLASS_LEN = len(STOCK_CLASS_LIST)

    # get every stocks' Close price and return a dataframe
    STOCKS_DF = data_pre_treatment(STOCK_CLASS_LIST)

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(STOCKS_DF)
    S = risk_models.CovarianceShrinkage(STOCKS_DF).ledoit_wolf()

    if MODE == 0:
        check_stock_info(STOCK_CLASS_LIST, STOCK_NAME, SAVE)
    elif MODE == 1:
        exec_general_efficient_frontier(STOCK_CLASS_LIST, STOCKS_DF, mu, S, WEIGHT_BOUNDS,
                                        STOCKS_BOUNDARY_PATH, TARGET_RETURN, MARKET_NATURAL,
                                        RISK_FREE)
    elif MODE == 2:
        exec_black_litterman(STOCK_CLASS_LIST, STOCKS_DF, S, VEWS_PATH, WEIGHT_BOUNDS,
                             STOCKS_BOUNDARY_PATH, TARGET_RETURN, MARKET_NATURAL,
                             RISK_FREE, SAVE)
    elif MODE == 3:
        exec_hierarchical_risky_party(STOCKS_DF, S, RISK_FREE, FREQUENCY, SAVE)
