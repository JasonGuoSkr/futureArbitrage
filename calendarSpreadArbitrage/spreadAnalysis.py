# @Time    : 2021/4/7 15:24
# @Author  : GUO LULU

import datetime
import pandas as pd
import numpy as np
import rqdatac as rq
import calendarSpreadArbitrage.futureData
import plotly.graph_objs as go
from plotly.subplots import make_subplots


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # startDate = '2021-03-23'
    # endDate = '2021-04-02'
    # orderBook = ['IC2104', 'IC2105', 'IC2106', 'IC2109']
    #
    # futureData = calendarSpreadArbitrage.futureData.future_data_load(orderBook, start_date=startDate, end_date=endDate)
    #
    # spreadData = pd.DataFrame(columns=orderBook)
    # for orderID in orderBook:
    #     spreadData[orderID] = futureData[orderID]['a1'] - futureData[orderID]['b1']
    #
    # spreadData.mean()

    # fig = plt.figure(figsize=(15, 10))
    # plt.plot(spreadData[orderBook[0]])
    # plt.plot(spreadData[orderBook[1]])
    # plt.legend(['spread1', 'spread2'], loc='upper left')
    # plt.show()

    ####################################################################################################################
    startDate = '2020-01-01'
    endDate = '2021-03-31'
    underlyingSymbol = 'IC'

    allInstruments = rq.all_instruments(type='Future')
    underlyingInstruments = allInstruments[allInstruments['underlying_symbol'] == underlyingSymbol]
    underlyingInstruments = underlyingInstruments[~(underlyingInstruments['listed_date'] == '0000-00-00')]
    underlyingInstruments = underlyingInstruments.sort_values(by='maturity_date', ascending=True)

    indexCode = underlyingInstruments['underlying_order_book_id'].values[0]

    dateNow = datetime.datetime.now().strftime('%Y-%m-%d')
    dateList = underlyingInstruments['maturity_date'][underlyingInstruments['maturity_date'] <= dateNow]

    spreadData = pd.DataFrame(index=range(7000))
    for dateInd in dateList.values[:-15:-1]:
        # 交易合约
        # dateInd = dateList.values[-1]

        contractCodeIndex = [((underlyingInstruments['listed_date'] <= dateInd)[ind] and
                           (underlyingInstruments['maturity_date'] >= dateInd)[ind])
                          for ind in underlyingInstruments.index]
        contractCodeList = underlyingInstruments['order_book_id'][contractCodeIndex].tolist()
        contractCodeList.sort()

        spreadData[contractCodeList[0]] = None

        startDate = underlyingInstruments['listed_date'][underlyingInstruments['listed_date'] <= dateInd].sort_values(ascending = True).values[-1]
        endDate = dateInd

        price = rq.get_price(contractCodeList, start_date=startDate, end_date=endDate, frequency='1m', fields='close',
                             adjust_type='none', skip_suspended=False, market='cn', expect_df=False)
        price = price[contractCodeList]

        basisData = price.iloc[:, 0].sub(price.iloc[:, 1], axis=0)
        basisData = basisData.sort_index(ascending=False)
        spreadData[contractCodeList[0]][:len(basisData)] = round(basisData, 2)

        # spreadData.to_csv('E:/中泰证券/策略/期货套利/跨期套利/当月次月价差.csv')

    data = [go.Scatter(x=spreadData.index, y=spreadData.iloc[:, 0], name='spread1'),
            go.Scatter(x=spreadData.index, y=spreadData.iloc[:, 1], name='spread2')]
    layout = go.Layout(title='金融股价的变化趋势')
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(xaxis_type="category")
    fig.show()
