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


def statistics(underlying_list, start_date, end_date, time_yes, time_list):
    # 数据加载
    spread_data = intercommodityArbitrage.spreadAnalysis.spread_analysis(underlying_list, start_date, end_date)
    spread_data = spread_data.resample('1min', how='first', closed='left', label='left')

    date_list = rq.get_trading_dates(start_date, end_date)
    index_str = spread_data.index.strftime("%Y-%m-%d %H:%M:%S.%f")

    statistical_dict = {}

    for time_on in time_list:
        print(time_on)
        data_filter = pd.DataFrame(index=date_list[1:], columns=['spread_pre', 'spread_on'])
        statistical_details = pd.DataFrame(index=range(-20, 21),
                                           columns=['count_all', 'count_inverse', 'ratio_inverse', 'return_avg'])

        for date in date_list[1:]:
            # date = date_list[1]
            # print(date)
            time_pre = date_list[date_list.index(date)-1].strftime("%Y-%m-%d") + " " + time_yes + ".000000"
            time_str = date.strftime("%Y-%m-%d") + " " + time_on + ".000000"
            data_filter.loc[date, 'spread_pre'] = spread_data["spread_pct"][index_str == time_pre].values[0]
            data_filter.loc[date, 'spread_on'] = spread_data["spread_pct"][index_str == time_str].values[0]

        for order in range(-20, 21):
            if order < 0:
                statistical_details.loc[order, 'count_all'] = (data_filter['spread_pre'] < 0.001 * order).sum()
                statistical_details.loc[order, 'count_inverse'] = ((data_filter['spread_on'] > 0) &
                                                                   (data_filter['spread_pre'] < 0.001 * order)).sum()
                if (data_filter['spread_pre'] < 0.001 * order).sum():
                    statistical_details.loc[order, 'ratio_inverse'] = statistical_details.loc[order, 'count_inverse'] \
                                                                      / statistical_details.loc[order, 'count_all']
                    statistical_details.loc[order, 'return_avg'] = data_filter['spread_on'][data_filter['spread_pre'] <
                                                                                            0.001 * order].mean()
            elif order > 0:
                statistical_details.loc[order, 'count_all'] = (data_filter['spread_pre'] > 0.001 * order).sum()
                statistical_details.loc[order, 'count_inverse'] = ((data_filter['spread_on'] < 0) &
                                                                   (data_filter['spread_pre'] > 0.001 * order)).sum()
                if (data_filter['spread_pre'] > 0.001 * order).sum():
                    statistical_details.loc[order, 'ratio_inverse'] = statistical_details.loc[order, 'count_inverse'] \
                                                                      / statistical_details.loc[order, 'count_all']
                    statistical_details.loc[order, 'return_avg'] = data_filter['spread_on'][data_filter['spread_pre'] >
                                                                                            0.001 * order].mean()
        statistical_details.drop(index=[0], inplace=True)
        statistical_dict[time_on] = statistical_details

    return statistical_dict


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 参数 回测区间及合约代码
    startDate = '20170101'
    endDate = '20200531'
    underlyingList = ('IF', 'IH')
    timeYes = "14:59:00"
    timeList = ["09:31:00", "09:35:00", "09:40:00", "09:45:00", "09:50:00", "09:55:00", "10:00:00"]

    underlying_list = underlyingList
    start_date = startDate
    end_date = endDate
    time_list = timeList
    statisticalList = statistics(underlyingList, startDate, endDate, timeYes, timeList)
    for timeOn in timeList:
        statisticalList[timeOn].to_csv("E:/中泰证券/策略/期货套利/跨品种套利/overnight/"
                                       + underlyingList[0] + underlyingList[1] + "_" + timeYes[3:5]
                                       + "_" + timeOn[0:2] + timeOn[3:5] + ".csv")
