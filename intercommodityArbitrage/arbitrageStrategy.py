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


def trading_data(trade_date, contract_list):
    # 数据加载
    data_load = intercommodityArbitrage.futureData.future_data_load(contract_list, start_date=trade_date,
                                                                    end_date=trade_date)



if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 参数 回测区间及合约代码
    startDate = '20200511'
    endDate = '20200514'
    contractList = ('IF2005', 'IH2005')

    # 数据加载
    futureData = intercommodityArbitrage.futureData.future_data_load(contractList, start_date=startDate,
                                                                     end_date=endDate)
    spreadData = intercommodityArbitrage.spreadCompute.spread_compute(startDate, endDate, contractList)

    #
    dateList = rq.get_trading_dates(startDate, endDate)

    for date in dateList:
        # date = dateList[0]
        for contractID in contractList:
            # contractID = contractList[0]
            contractData = futureData[contractID]
