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
期货跨品种日内交易策略
"""


def trading_data(contract_list, start_date, end_date):
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


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 参数 回测区间及合约代码
    startDate = '20200511'
    endDate = '20200514'
    contractList = ('IF2005', 'IH2005')
    dateLen = 600

    # 数据加载
    futureData = trading_data(contractList, start_date=startDate, end_date=endDate)
    spreadData = intercommodityArbitrage.spreadCompute.spread_compute(startDate, endDate, contractList)

    #
    dateList = rq.get_trading_dates(startDate, endDate)

    for date in dateList:
        # date = dateList[0]
        dailyTradingData = futureData[futureData['trading_date'] == date]
        dailySpreadData = spreadData[futureData['trading_date'] == date]

        for id in range(dateLen, dailySpreadData.shape[0]):
            print(id)
