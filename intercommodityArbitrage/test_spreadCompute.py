# @Time    : 2020/5/15 9:14
# @Author  : GUO LULU

import os
import time
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import intercommodityArbitrage.futureData
import statsmodels.api as sm
import rqdatac as rq


"""
期货价差计算分析
"""


def daily_compute(trade_date, contract_list):
    # 数据加载
    data_load = intercommodityArbitrage.futureData.future_data_load(contract_list, start_date=trade_date,
                                                                    end_date=trade_date)

    data_df = pd.DataFrame()
    for contract_id in contract_list:
        price_last = data_load[contract_id]['last']
        price_last.name = contract_id + '_last'
        data_df = pd.concat([data_df, price_last], axis=1)

    # 价差计算
    # data_log = np.log(data_df)
    #
    # ols_factor = sm.add_constant(data_log)
    #
    # result = sm.OLS(ols_factor.iloc[:, -1].astype(float), ols_factor.iloc[:, :-1].astype(float)).fit()
    # param_series = result.params
    # result.summary()
    #
    # data_log['spread_log'] = ols_factor.iloc[:, -1] - ols_factor.iloc[:, :-1] * param_series

    # 日内收益
    pct_in_day = data_df / data_df.iloc[0, :]
    pct_in_day['spread_pct'] = pct_in_day.iloc[:, 0] - pct_in_day.iloc[:, 1]
    # pct_in_day.index = pct_in_day.index.strftime('%Y-%m-%d %H:%m:%s:%f')

    point_in_day = data_df - data_df.iloc[0, :]
    point_in_day['spread_point'] = point_in_day.iloc[:, 0] - point_in_day.iloc[:, 1]

    # plt.plot(pct_in_day['spread_pct'])
    # plt.show()

    spread_data = pd.concat([data_df, pct_in_day['spread_pct'], point_in_day['spread_point']], axis=1)

    return spread_data


def spread_compute(start_date, end_date, contract_list):
    date_list = rq.get_trading_dates(start_date=start_date, end_date=end_date)
    data_final = pd.DataFrame()

    for date_ind in date_list:
        date_ind = date_ind.strftime('%Y%m%d')
        try:
            daily_data = daily_compute(date_ind, contract_list)
        except AttributeError:
            print(date_ind + '计算错误')
        else:
            data_final = pd.concat([data_final, daily_data], axis=0)

    return data_final


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 参数
    tradeDate = '20200416'

    startDate = '20200413'
    endDate = '20200417'

    contractList = ('IF2004', 'IH2004')
    # contractList = 'IF2003'

    # Data = futureData.future_data_load(contractList, start_date=startDate, end_date=endDate)
    Data = spread_compute(startDate, endDate, contractList)

    plt.plot(Data['spread_point'])
    plt.show()
