# @Time    : 2020/5/13 16:57
# @Author  : GUO LULU

import os
import time
import numpy as np
import pandas as pd
import datetime
import calendarArbitrage.dataLoad
import rqdatac as rq

"""
日历效应
"""

if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 文件路径
    outputPath = "E:/中泰证券/策略/期货套利/日历效应/"
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    # 参数
    dateLen = 10
    startBenchDate = '0101'
    endBenchDate = '0331'
    contractList = ('000016.XSHG', '000300.XSHG', '000905.XSHG', '000852.XSHG', '399006.XSHE')

    # 计算
    pctChange = pd.DataFrame(index=range(2011, 2021), columns=contractList)

    for year_id in range(2011, 2021):
        # year_id = 2011
        print(year_id)
        endDate = str(year_id) + endBenchDate
        startDate = str(year_id) + startBenchDate
        dateSeries = pd.Series(rq.get_trading_dates(startDate, endDate))
        dateDelta = [0] + [delta.days for delta in dateSeries.diff()[1:].tolist()]
        dateDf = pd.DataFrame({'date': dateSeries, 'delta': dateDelta})
        dateDf = dateDf[dateDf['delta'] > 3]
        startDate = dateDf.iloc[0, 0]
        endDate = rq.get_next_trading_date(startDate, n=dateLen)
        print(startDate)

        Data = calendarArbitrage.dataLoad.data_load(contractList, start_date=startDate, end_date=endDate)

        dataDf = pd.DataFrame()
        for contract_id in contractList:
            dataClose = Data[contract_id]['close']
            dataDf = pd.concat([dataDf, dataClose], axis=1)
        dataDf.columns = contractList

        pctChangeDf = dataDf / dataDf.iloc[0, :]
        pctChange.loc[year_id] = pctChangeDf.iloc[-1, :] - 1

    pctChange.to_csv(outputPath + "春节指数收益.csv")
