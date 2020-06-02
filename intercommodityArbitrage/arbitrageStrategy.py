# @Time    : 2020/5/19 16:33
# @Author  : GUO LULU


import os
import time
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import intercommodityArbitrage.futureData
import intercommodityArbitrage.spreadCompute
import rqdatac as rq


"""
期货跨品种日内交易策略：
    短时间(dateLen)内价差(spread_pct)大幅波动，反向建仓，按一定比例止盈或止损，日内强制平仓
"""


def trading_data(contract_list, start_date, end_date):
    """
    获取期货合约的交易数据，包括日期、最新价、买一价、卖一价等(['trading_date', 'last', 'a1', 'b1'])
    :param contract_list: 合约列表
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: 合并数据
    """
    data_load = intercommodityArbitrage.futureData.future_data_load(contract_list, start_date=start_date,
                                                                    end_date=end_date)

    data_df = pd.DataFrame()
    data_df['trading_date'] = data_load[contract_list[0]]['trading_date']
    columns_list = ['last', 'a1', 'b1']
    for contract_id in contract_list:
        contract_data = data_load[contract_id][columns_list]
        contract_data.columns = [contract_id + '_' + columns_name for columns_name in columns_list]
        data_df = pd.concat([data_df, contract_data], axis=1)

    return data_df


def strategy(contract_list, start_date, end_date, date_len=1200, diff=0.0015, stop=-0.001, close=0.001):
    """
    策略回测，短时间(date_len)内价差(spread_pct)大幅波动(diff)，反向建仓，按一定比例止盈(close)或止损(stop)，日内强制平仓
    :param contract_list: 合约列表
    :param start_date: 开始日期
    :param end_date: 结束日期
    :param date_len: 考察时间长度
    :param diff: 波动阈值
    :param stop: 止损阈值
    :param close: 止盈阈值
    :return: 交易细节
    """
    # 数据加载
    future_data = trading_data(contract_list, start_date=start_date, end_date=end_date)
    spread_data = intercommodityArbitrage.spreadCompute.spread_compute(start_date, end_date, contract_list)

    # 逐tick回测，获取交易信号
    trade_details = pd.DataFrame(columns=['openTime', 'closeTime', 'tradeDirection',
                                          'openSpread', 'closeSpread', 'profitSpread'])
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

        daily_trading = future_data[future_data['trading_date'] == date]
        daily_spread = spread_data[future_data['trading_date'] == date]

        for order in range(1, daily_spread.shape[0] - 1):
            # order = date_len
            if order < date_len:
                data_series = daily_spread.iloc[0:order, 4]
            else:
                data_series = daily_spread.iloc[order - date_len:order, 4]

            last_spread = data_series.iloc[-1]
            max_id = np.max(data_series)
            min_id = np.min(data_series)

            if not hold_par:
                if (last_spread - min_id >= diff) and (max_id - last_spread >= diff):
                    open_spread = last_spread
                    hold_par = True
                    count_num += 1
                    if last_spread - data_series.iloc[0] >= 0:
                        pos_par = -1
                    else:
                        pos_par = 1
                    trade_details.loc[count_num, 'openTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
                elif (last_spread - min_id >= diff) and (max_id - last_spread < diff):
                    open_spread = last_spread
                    pos_par = -1
                    hold_par = True
                    count_num += 1
                    trade_details.loc[count_num, 'openTime'] = data_series.index[-1]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
                elif (last_spread - min_id < diff) and (max_id - last_spread >= diff):
                    open_spread = last_spread
                    pos_par = 1
                    hold_par = True
                    count_num += 1
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
        if pos_par == 1:
            data_series = daily_spread.iloc[-date_len:, 4]
            last_spread = data_series.iloc[-1]
            trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
            trade_details.loc[count_num, 'closeSpread'] = last_spread
            trade_details.loc[count_num, 'profitSpread'] = last_spread - open_spread
        elif pos_par == -1:
            data_series = daily_spread.iloc[-date_len:, 4]
            last_spread = data_series.iloc[-1]
            trade_details.loc[count_num, 'closeTime'] = data_series.index[-1]
            trade_details.loc[count_num, 'closeSpread'] = last_spread
            trade_details.loc[count_num, 'profitSpread'] = open_spread - last_spread

    # 收益计算
    trade_details = pd.DataFrame(columns=['openTime', 'closeTime', 'tradeDirection',
                                          'openSpread', 'closeSpread', 'profitSpread'])

    return trade_details


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 参数 回测区间及合约代码
    startDate = '20200511'
    endDate = '20200514'
    contractList = ('IF2005', 'IH2005')
    dateLen = 1200
    diffPar = 0.0015

    tradeDetails = strategy(contractList, startDate, endDate, date_len=dateLen, diff=diffPar, stop=-0.001, close=0.001)
