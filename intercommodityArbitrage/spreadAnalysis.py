# @Time    : 2020/6/11 16:16
# @Author  : GUO LULU


import os
import time
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import intercommodityArbitrage.futureData
import rqdatac as rq


"""
期货价差统计分析
"""


def daily_compute(trade_date, contract_list):
    # 数据加载
    data_load = intercommodityArbitrage.futureData.future_data_load(contract_list, start_date=trade_date,
                                                                    end_date=trade_date)

    data_df = pd.DataFrame()
    for contract_id in contract_list:
        price_last = data_load[contract_id]['last']
        price_last.name = contract_id[:2] + '_last'
        data_df = pd.concat([data_df, price_last], axis=1)

    # 日内收益率差值
    pct_in_day = data_df / data_df.iloc[0, :]
    pct_in_day.columns = [contract_id[:2] + '_std' for contract_id in contract_list]
    pct_in_day['spread_pct'] = pct_in_day.iloc[:, 0] - pct_in_day.iloc[:, 1]

    # 日内点位差值
    point_in_day = data_df - data_df.iloc[0, :]
    point_in_day['spread_point'] = point_in_day.iloc[:, 0] - point_in_day.iloc[:, 1]

    spread_data = pd.concat([data_df, pct_in_day, point_in_day['spread_point']], axis=1)

    return spread_data


def spread_analysis(underlying_list, start_date, end_date):
    date_list = rq.get_trading_dates(start_date=start_date, end_date=end_date)
    spread_data = pd.DataFrame()
    describe_data = pd.DataFrame()

    for date_ind in date_list:
        contract_list = []
        for underlying in underlying_list:
            contract = rq.futures.get_dominant(underlying, start_date=date_ind, end_date=date_ind, rule=0)
            contract_list.append(contract[date_ind])
        # print(contract_list)

        try:
            daily_data = daily_compute(date_ind, contract_list)
        except AttributeError:
            print(date_ind + '计算错误')
        else:
            # print(date_ind)
            spread_data = pd.concat([spread_data, daily_data], axis=0)
            describe_data[date_ind] = daily_data['spread_pct'].describe()

    return spread_data


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 参数 回测区间及合约代码
    startDate = '20200203'
    endDate = '20200203'
    underlyingList = ('IF', 'IH')

    # start_date = startDate
    # end_date = endDate
    # underlying_list = ('IF', "IH")
    spreadData = spread_analysis(underlyingList, startDate, endDate)
    # spreadData['spread_pct'].describe()
    # spreadData['spread_pct'].quantile(0.05)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=spreadData.index.strftime("%Y-%m-%d %H:%M:%S.%f"),
                   y=spreadData[underlyingList[0] + '_std'], name=underlyingList[0]),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=spreadData.index.strftime("%Y-%m-%d %H:%M:%S.%f"),
                   y=spreadData[underlyingList[1] + '_std'], name=underlyingList[1]),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=spreadData.index.strftime("%Y-%m-%d %H:%M:%S.%f"), y=spreadData['spread_pct'], name='spread'),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="price_spread"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="datetime")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>price</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>spread</b>", secondary_y=True)
    fig.update_layout(xaxis_type="category")

    fig.show()
