# @Time    : 2020/6/21 16:03
# @Author  : GUO LULU


import os
import time
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import intercommodityArbitrage.futureData
import intercommodityArbitrage.spreadAnalysis
import rqdatac as rq


"""
期货跨品种隔夜交易策略：
    隔夜价差过大时，下个交易日早盘做价差回归
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


def statistics(underlying_list, start_date, end_date, time_list):
    # 数据加载
    spread_data = intercommodityArbitrage.spreadAnalysis.spread_analysis(underlying_list, start_date, end_date)
    spread_data = spread_data.resample('1min', how='first', closed='left', label='left')

    date_list = rq.get_trading_dates(start_date, end_date)
    index_str = spread_data.index.strftime("%Y-%m-%d %H:%M:%S.%f")

    statistical_dict = {}

    for time_on in time_list:
        print(time_on)
        data_filter = pd.DataFrame(index=date_list[1:], columns=['spread_pre', 'spread_on'])
        statistical_details = pd.DataFrame(index=range(-10, 11),
                                           columns=['count_all', 'count_inverse', 'ratio_inverse', 'return_avg'])

        for date in date_list[1:]:
            # date = date_list[1]
            # print(date)
            time_pre = date_list[date_list.index(date)-1].strftime("%Y-%m-%d") + " 14:59:00.000000"
            time_str = date.strftime("%Y-%m-%d") + " " + time_on + ".000000"
            data_filter.loc[date, 'spread_pre'] = spread_data["spread_pct"][index_str == time_pre].values[0]
            data_filter.loc[date, 'spread_on'] = spread_data["spread_pct"][index_str == time_str].values[0]

        for order in range(-10, 11):
            if order < 0:
                statistical_details.loc[order, 'count_all'] = (data_filter['spread_pre'] < 0.001 * order).sum()
                statistical_details.loc[order, 'count_inverse'] = ((data_filter['spread_on'] > 0) &
                                                                   (data_filter['spread_pre'] < 0.001 * order)).sum()
                if (data_filter['spread_pre'] < 0.001 * order).sum():
                    statistical_details.loc[order, 'ratio_inverse'] = statistical_details.loc[order, 'count_inverse'] / \
                        statistical_details.loc[order, 'count_all']
                    statistical_details.loc[order, 'return_avg'] = data_filter['spread_on'][data_filter['spread_pre'] <
                                                                                            0.001 * order].mean()
            else:
                statistical_details.loc[order, 'count_all'] = (data_filter['spread_pre'] > 0.001 * order).sum()
                statistical_details.loc[order, 'count_inverse'] = ((data_filter['spread_on'] < 0) &
                                                                   (data_filter['spread_pre'] > 0.001 * order)).sum()
                if (data_filter['spread_pre'] > 0.001 * order).sum():
                    statistical_details.loc[order, 'ratio_inverse'] = statistical_details.loc[order, 'count_inverse'] / \
                        statistical_details.loc[order, 'count_all']
                    statistical_details.loc[order, 'return_avg'] = data_filter['spread_on'][data_filter['spread_pre'] >
                                                                                            0.001 * order].mean()
        statistical_dict[time_on] = statistical_details

    return statistical_dict


def strategy(underlying_list, start_date, end_date, quantile=0.03, stop=-0.003, close=0.003, close_len=7200):
    # 数据加载
    future_data = trading_data(underlying_list, start_date=start_date, end_date=end_date)
    spread_data = intercommodityArbitrage.spreadAnalysis.spread_analysis(underlying_list, start_date, end_date)

    # 逐tick回测，获取交易信号
    trade_details = pd.DataFrame(columns=['openTime', 'closeTime', 'tradeDirection',
                                          'openSpread', 'closeSpread', 'profitSpread', 'profitTrade'])
    count_num = -1

    date_list = rq.get_trading_dates(start_date, end_date)
    for date in date_list[60:]:
        # date = date_list[60]
        print(date)
        hold_par = False
        pos_par = 0
        stop_par = stop
        close_par = close
        open_spread = 0
        open_order = 0

        # 日内开平仓参数
        sample_spread = spread_data[future_data['trading_date'] < date]['spread_pct']
        up_par = sample_spread.quantile(1-quantile)
        down_par = sample_spread.quantile(quantile)

        daily_spread = spread_data[future_data['trading_date'] == date]

        for order in range(0, daily_spread.shape[0] - 1):
            # order = 0
            last_spread = daily_spread.iloc[order, 4]

            if not hold_par:
                if last_spread >= up_par:
                    open_spread = last_spread
                    open_order = order
                    pos_par = -1
                    hold_par = True
                    count_num += 1
                    trade_details.loc[count_num, 'openTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
                elif last_spread <= down_par:
                    open_spread = last_spread
                    open_order = order
                    pos_par = 1
                    hold_par = True
                    count_num += 1
                    trade_details.loc[count_num, 'openTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'tradeDirection'] = pos_par
                    trade_details.loc[count_num, 'openSpread'] = open_spread
            else:
                profit_spread = last_spread - open_spread
                if (profit_spread <= -close_par) and (pos_par == -1):
                    trade_details.loc[count_num, 'closeTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = -profit_spread
                    pos_par = 0
                    hold_par = False
                if (profit_spread >= -stop_par) and (pos_par == -1):
                    trade_details.loc[count_num, 'closeTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = -profit_spread
                    pos_par = 0
                    hold_par = False
                if (order - open_order > close_len) and (pos_par == -1):
                    trade_details.loc[count_num, 'closeTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = -profit_spread
                    pos_par = 0
                    hold_par = False
                if (profit_spread >= close_par) and (pos_par == 1):
                    trade_details.loc[count_num, 'closeTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = profit_spread
                    pos_par = 0
                    hold_par = False
                if (profit_spread <= stop_par) and (pos_par == 1):
                    trade_details.loc[count_num, 'closeTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = profit_spread
                    pos_par = 0
                    hold_par = False
                if (order - open_order > close_len) and (pos_par == 1):
                    trade_details.loc[count_num, 'closeTime'] = daily_spread.index[order]
                    trade_details.loc[count_num, 'closeSpread'] = last_spread
                    trade_details.loc[count_num, 'profitSpread'] = profit_spread
                    pos_par = 0
                    hold_par = False
        if pos_par == 1:
            last_spread = daily_spread.iloc[-1, 4]
            trade_details.loc[count_num, 'closeTime'] = daily_spread.index[-1]
            trade_details.loc[count_num, 'closeSpread'] = last_spread
            trade_details.loc[count_num, 'profitSpread'] = last_spread - open_spread
        elif pos_par == -1:
            last_spread = daily_spread.iloc[-1, 4]
            trade_details.loc[count_num, 'closeTime'] = daily_spread.index[-1]
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
    startDate = '20170101'
    endDate = '20200531'
    underlyingList = ('IF', 'IH')
    timeList = ["09:31:00", "09:35:00", "09:40:00", "09:45:00", "09:50:00", "09:55:00", "10:00:00"]
    # quantilePar = 0.04
    # stopPar = -0.003
    # closePar = 0.003
    # closeLen = 7200

    # tradeDetails = strategy(underlyingList, startDate, endDate, quantile=quantilePar,
    #                         stop=stopPar, close=closePar, close_len=closeLen)
    # tradeDetails['profitTrade'].mean()
    # tradeDetails.to_csv("E:/中泰证券/策略/期货套利/跨品种套利/rbreaker/tradeDetails.csv")
    underlying_list = underlyingList
    start_date = startDate
    end_date = endDate
    time_list = timeList
    # tradingData = trading_data(underlyingList, startDate, endDate)
    statisticalList = statistics(underlyingList, startDate, endDate, timeList)
    for timeOn in timeList:
        statisticalList[timeOn].to_csv("E:/中泰证券/策略/期货套利/跨品种套利/overnight/"
                                       + timeOn[0:2] + timeOn[3:5] + ".csv")
