# @Time    : 2020/7/16 16:59
# @Author  : GUO LULU


import os
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import intercommodityArbitrage.futureData
import intercommodityArbitrage.spreadAnalysis
import rqdatac as rq

"""
期货跨品种日内交易策略：
    r-breaker策略
"""


def trading_data(underlying_list, start_date, end_date):
    date_list = rq.get_trading_dates(start_date=start_date, end_date=end_date)
    price_data = pd.DataFrame()

    for date_ind in date_list:
        print(date_ind)
        contract_list = []
        for underlying in underlying_list:
            contract = rq.futures.get_dominant(underlying, start_date=date_ind, end_date=date_ind, rule=0)
            contract_list.append(contract[date_ind])

        data_load = intercommodityArbitrage.futureData.future_data_load(contract_list, start_date=date_ind,
                                                                        end_date=date_ind)

        data_df = pd.DataFrame()
        data_df['trading_date'] = data_load[contract_list[0]]['trading_date']
        columns_list = ['last', 'a1', 'b1']
        for contract_id in contract_list:
            contract_data = data_load[contract_id][columns_list]
            contract_data.columns = [contract_id[:2] + '_' + columns_name for columns_name in columns_list]
            data_df = pd.concat([data_df, contract_data], axis=1)

        price_data = pd.concat([price_data, data_df], axis=0)

    return price_data


def strategy(underlying_list, start_date, end_date, quantile=0.03, close=0.003, stop=-0.003, close_len=7200):
    # 数据加载
    future_data = trading_data(underlying_list, start_date=start_date, end_date=end_date)
    spread_data = intercommodityArbitrage.spreadAnalysis.spread_analysis(underlying_list, start_date, end_date)

    # 逐tick回测，获取交易信号
    trade_details = pd.DataFrame(columns=['openTime', 'closeTime', 'tradeDirection',
                                          'openSpread', 'closeSpread', 'profitSpread', 'profitTrade'])
    count_num = -1

    date_list = rq.get_trading_dates(start_date, end_date)
    for date in date_list:
        # date = date_list[0]
        print(date)
        hold_par = False
        pos_par = 0
        open_spread = 0
        open_order = 0

        daily_spread = spread_data[future_data['trading_date'] == date]

        STOP_LOSS_PRICE = stopLossPrice
        bBreak = bBreak
        sSetup = sSetup
        sEnter = sEnter
        bEnter = bEnter
        bSetup = bSetup
        sBreak = sBreak

        for order in range(1, daily_spread.shape[0] - 1):
            # order = 0
            last_spread = daily_spread.iloc[order, 4]

            if not hold_par:
                if last_spread > bBreak:
                    open_spread = last_spread
                    open_order = order
                    pos_par = 1
                    hold_par = True
                    count_num += 1
                    trade_details.loc[count_num, 'tradeDate'] = date
                    trade_details.loc[count_num, 'openTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
                elif last_spread < sBreak:
                    open_spread = last_spread
                    open_order = order
                    pos_par = -1
                    hold_par = True
                    count_num += 1
                    trade_details.loc[count_num, 'tradeDate'] = date
                    trade_details.loc[count_num, 'openTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
            else:
                profit_spread = last_spread - open_spread
                if (profit_spread <= STOP_LOSS_PRICE) and (pos_par == 1):
                    trade_details.loc[count_num, 'closeTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = profit_spread
                    pos_par = 0
                    hold_par = False
                if (profit_spread >= -STOP_LOSS_PRICE) and (pos_par == -1):
                    trade_details.loc[count_num, 'closeTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = -profit_spread
                    pos_par = 0
                    hold_par = False






if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 参数 回测区间及合约代码
    startDate = '20200101'
    endDate = '20200531'
    underlyingList = ('IF', 'IH')
    diffPar = 0.004
    stopPar = -0.0025
    closePar = 0.005
    openLen = 1800
    closeLen = 7200

