# @Time    : 2020/6/2 17:16
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


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # 参数 回测区间及合约代码
    startDate = '20200511'
    endDate = '20200514'
    contractList = ('IF2005', 'IH2005')
    dateLen = 1200
    diffPar = 0.0015

    # 数据加载
    futureData = trading_data(contractList, start_date=startDate, end_date=endDate)
    spreadData = intercommodityArbitrage.spreadCompute.spread_compute(startDate, endDate, contractList)

    # 逐tick回测
    tradeDetails = pd.DataFrame(columns=['openTime', 'closeTime', 'tradeDirection',
                                         'openSpread', 'closeSpread', 'profitSpread'])
    countNum = -1

    dateList = rq.get_trading_dates(startDate, endDate)
    for date in dateList:
        # date = dateList[0]
        print(date)
        holdPar = False
        posPar = 0
        stopPar = -0.001
        closePar = 0.001
        openSpread = 0

        dailyTradingData = futureData[futureData['trading_date'] == date]
        dailySpreadData = spreadData[futureData['trading_date'] == date]
        # dailyParData = dailySpreadData[['spread_pct', 'spread_point']]
        # dailyParData.loc[:, 'position'] = np.zeros(dailySpreadData.shape[0])

        for order in range(1, dailySpreadData.shape[0]-1):
            # order = dateLen
            if order < dateLen:
                dataSeries = dailySpreadData.iloc[0:order, 4]
            else:
                dataSeries = dailySpreadData.iloc[order - dateLen:order, 4]

            # temp1 = np.maximum.accumulate(dataSeries)
            # temp2 = dataSeries.idxmax()
            # temp3 = dataSeries.idxmin()
            lastSpread = dataSeries.iloc[-1]
            maxID = np.max(dataSeries)
            minID = np.min(dataSeries)

            if not holdPar:
                if (lastSpread - minID >= diffPar) and (maxID - lastSpread >= diffPar):
                    openSpread = lastSpread
                    holdPar = True
                    countNum += 1
                    if lastSpread - dataSeries.iloc[0] >= 0:
                        posPar = -1
                    else:
                        posPar = 1
                    tradeDetails.loc[countNum, 'openTime'] = dataSeries.index[-1]
                    tradeDetails.loc[countNum, 'tradeDirection'] = posPar
                    tradeDetails.loc[countNum, 'openSpread'] = openSpread
                elif (lastSpread - minID >= diffPar) and (maxID - lastSpread < diffPar):
                    openSpread = lastSpread
                    posPar = -1
                    holdPar = True
                    countNum += 1
                    tradeDetails.loc[countNum, 'openTime'] = dataSeries.index[-1]
                    tradeDetails.loc[countNum, 'tradeDirection'] = posPar
                    tradeDetails.loc[countNum, 'openSpread'] = openSpread
                elif (lastSpread - minID < diffPar) and (maxID - lastSpread >= diffPar):
                    openSpread = lastSpread
                    posPar = 1
                    holdPar = True
                    countNum += 1
                    tradeDetails.loc[countNum, 'openTime'] = dataSeries.index[-1]
                    tradeDetails.loc[countNum, 'tradeDirection'] = posPar
                    tradeDetails.loc[countNum, 'openSpread'] = openSpread
            else:
                profitSpread = lastSpread - openSpread
                if (profitSpread <= -closePar) and (posPar == -1):
                    tradeDetails.loc[countNum, 'closeTime'] = dataSeries.index[-1]
                    tradeDetails.loc[countNum, 'closeSpread'] = lastSpread
                    tradeDetails.loc[countNum, 'profitSpread'] = -profitSpread
                    posPar = 0
                    holdPar = False
                if (profitSpread >= -stopPar) and (posPar == -1):
                    tradeDetails.loc[countNum, 'closeTime'] = dataSeries.index[-1]
                    tradeDetails.loc[countNum, 'closeSpread'] = lastSpread
                    tradeDetails.loc[countNum, 'profitSpread'] = -profitSpread
                    posPar = 0
                    holdPar = False
                if (profitSpread >= closePar) and (posPar == 1):
                    tradeDetails.loc[countNum, 'closeTime'] = dataSeries.index[-1]
                    tradeDetails.loc[countNum, 'closeSpread'] = lastSpread
                    tradeDetails.loc[countNum, 'profitSpread'] = profitSpread
                    posPar = 0
                    holdPar = False
                if (profitSpread <= stopPar) and (posPar == 1):
                    tradeDetails.loc[countNum, 'closeTime'] = dataSeries.index[-1]
                    tradeDetails.loc[countNum, 'closeSpread'] = lastSpread
                    tradeDetails.loc[countNum, 'profitSpread'] = profitSpread
                    posPar = 0
                    holdPar = False
        if posPar == 1:
            dataSeries = dailySpreadData.iloc[-dateLen:, 4]
            lastSpread = dataSeries.iloc[-1]
            tradeDetails.loc[countNum, 'closeTime'] = dataSeries.index[-1]
            tradeDetails.loc[countNum, 'closeSpread'] = lastSpread
            tradeDetails.loc[countNum, 'profitSpread'] = lastSpread - openSpread
            posPar = 0
            holdPar = False
        elif posPar == -1:
            dataSeries = dailySpreadData.iloc[-dateLen:, 4]
            lastSpread = dataSeries.iloc[-1]
            tradeDetails.loc[countNum, 'closeTime'] = dataSeries.index[-1]
            tradeDetails.loc[countNum, 'closeSpread'] = lastSpread
            tradeDetails.loc[countNum, 'profitSpread'] = openSpread - lastSpread
            posPar = 0
            holdPar = False
