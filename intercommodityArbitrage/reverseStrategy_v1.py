# @Time    : 2020/6/7 16:28
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
    短时间(dateLen)内价差(spread_pct)大幅波动，反向建仓
    按一定比例止盈或止损/持仓超过一定时间平仓/日内强制平仓
修改内容：
    增加**************
    
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


def strategy(underlying_list, start_date, end_date, diff=0.0015, stop=-0.001, close=0.001,
             open_len=1200, close_len=7200):
    # 数据加载
    future_data = trading_data(underlying_list, start_date=start_date, end_date=end_date)
    spread_data = intercommodityArbitrage.spreadAnalysis.spread_analysis(underlying_list, start_date, end_date)

    # 逐tick回测，获取交易信号
    trade_details = pd.DataFrame(columns=['tradeDate', 'openTime', 'closeTime', 'tradeDirection',
                                          'openSpread', 'closeSpread', 'profitSpread', 'profitTrade'])
    count_num = -1

    date_list = rq.get_trading_dates(start_date, end_date)
    for date in date_list:
        # date = date_list[0]
        print(date)
        hold_par = False
        pos_par = 0
        stop_par = stop
        close_par = close
        open_spread = 0
        open_order = 0

        daily_spread = spread_data[future_data['trading_date'] == date]

        for order in range(1, daily_spread.shape[0] - 1):
            # order = open_len
            if order < open_len:
                data_series = daily_spread.iloc[0:order, 4]
            else:
                data_series = daily_spread.iloc[order - open_len:order, 4]

            last_spread = data_series.iloc[-1]
            max_id = np.max(data_series)
            min_id = np.min(data_series)

            if not hold_par:
                if (last_spread - min_id >= diff) and (max_id - last_spread >= diff):
                    open_spread = last_spread
                    open_order = order
                    hold_par = True
                    count_num += 1
                    if last_spread - data_series.iloc[0] >= 0:
                        pos_par = -1
                    else:
                        pos_par = 1
                    trade_details.loc[count_num, 'tradeDate'] = date
                    trade_details.loc[count_num, 'openTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
                elif (last_spread - min_id >= diff) and (max_id - last_spread < diff):
                    open_spread = last_spread
                    open_order = order
                    pos_par = -1
                    hold_par = True
                    count_num += 1
                    trade_details.loc[count_num, 'tradeDate'] = date
                    trade_details.loc[count_num, 'openTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
                elif (last_spread - min_id < diff) and (max_id - last_spread >= diff):
                    open_spread = last_spread
                    open_order = order
                    pos_par = 1
                    hold_par = True
                    count_num += 1
                    trade_details.loc[count_num, 'tradeDate'] = date
                    trade_details.loc[count_num, 'openTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
            else:
                profit_spread = last_spread - open_spread
                if (profit_spread <= -close_par) and (pos_par == -1):
                    trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = -profit_spread
                    pos_par = 0
                    hold_par = False
                if (profit_spread >= -stop_par) and (pos_par == -1):
                    trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = -profit_spread
                    pos_par = 0
                    hold_par = False
                if (order - open_order > close_len) and (pos_par == -1):
                    trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = -profit_spread
                    pos_par = 0
                    hold_par = False
                if (profit_spread >= close_par) and (pos_par == 1):
                    trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = profit_spread
                    pos_par = 0
                    hold_par = False
                if (profit_spread <= stop_par) and (pos_par == 1):
                    trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = profit_spread
                    pos_par = 0
                    hold_par = False
                if (order - open_order > close_len) and (pos_par == 1):
                    trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = profit_spread
                    pos_par = 0
                    hold_par = False
        if pos_par == 1:
            data_series = daily_spread.iloc[-open_len:, 4]
            last_spread = data_series.iloc[-1]
            trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
            trade_details.loc[count_num, 'closeSpread'] = last_spread
            trade_details.loc[count_num, 'profitSpread'] = last_spread - open_spread
        elif pos_par == -1:
            data_series = daily_spread.iloc[-open_len:, 4]
            last_spread = data_series.iloc[-1]
            trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
            trade_details.loc[count_num, 'closeSpread'] = last_spread
            trade_details.loc[count_num, 'profitSpread'] = open_spread - last_spread

    # 收益计算
    for order in trade_details.index:
        # order = trade_details.index[0]
        open_time = trade_details.loc[order, 'openTime']
        close_time = trade_details.loc[order, 'closeTime']
        contract_0 = underlying_list[0]
        contract_1 = underlying_list[1]
        if trade_details.loc[order, 'tradeDirection'] == 1:
            long_leg = (future_data.loc[close_time, contract_0 + '_b1'] -
                        future_data.loc[open_time, contract_0 + '_a1']) / \
                future_data.loc[open_time, contract_0 + '_a1']
            short_leg = -(future_data.loc[close_time, contract_1 + '_a1'] -
                          future_data.loc[open_time, contract_1 + '_b1']) / \
                future_data.loc[open_time, contract_1 + '_b1']
        else:
            long_leg = (future_data.loc[close_time, contract_1 + '_b1'] -
                        future_data.loc[open_time, contract_1 + '_a1']) / \
                future_data.loc[open_time, contract_1 + '_a1']
            short_leg = -(future_data.loc[close_time, contract_0 + '_a1'] -
                          future_data.loc[open_time, contract_0 + '_b1']) / \
                future_data.loc[open_time, contract_0 + '_b1']
        trade_details.loc[order, 'profitTrade'] = (long_leg + short_leg) / 2
        # trade_details['profitTrade'].mean()

    return trade_details


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

    underlying_list = underlyingList
    start_date = startDate
    end_date = endDate

    tradeDetails = strategy(underlyingList, startDate, endDate, diff=diffPar,
                            stop=stopPar, close=closePar, open_len=openLen, close_len=closeLen)
    tradeDetails = tradeDetails[tradeDetails['tradeDate'] != datetime.date(2020, 2, 3)]
    tradeDetails['profitTrade'].mean()

