# @Time    : 2021/3/14 13:50
# @Author  : GUO LULU

import datetime
import pandas as pd
import rqdatac as rq


"""
合约贴水率分析
1 到期日前推，贴水率与期限的关系
2 不同年份同一月份合约的贴水率，主要考察季月合约贴水率的变化，观察离到期日较远时季月合约的贴水率变化
    观察9、12月合约的分红季的贴水
"""

if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # startDate = '2021-01-01'
    # endDate = '2021-03-12'
    underlyingSymbol = 'IC'

    allInstruments = rq.all_instruments(type='Future')
    underlyingInstruments = allInstruments[allInstruments['underlying_symbol'] == underlyingSymbol]
    underlyingInstruments = underlyingInstruments[~(underlyingInstruments['listed_date'] == '0000-00-00')]
    underlyingInstruments = underlyingInstruments.sort_values(by='listed_date', ascending=True)

    indexCode = underlyingInstruments['underlying_order_book_id'].values[0]

    # dateList = rq.get_trading_dates(start_date=startDate, end_date=endDate)
    #
    # contractData = pd.DataFrame(columns=['one', 'two', 'three', 'four'])
    # discountData = pd.DataFrame(columns=['one', 'two', 'three', 'four'])
    # for dateInd in dateList:
    #     # dateInd = dateList[0]
    #     dateInd = dateInd.strftime('%Y-%m-%d')
    #
    #     # 交易合约
    #     contractCodeIndex = [((underlyingInstruments['listed_date'] <= dateInd)[ind] and
    #                        (underlyingInstruments['maturity_date'] >= dateInd)[ind])
    #                       for ind in (underlyingInstruments['listed_date'] >= dateInd).index]
    #     contractCodeList = underlyingInstruments['order_book_id'][contractCodeIndex].tolist()
    #     contractCodeList.sort()
    #
    #     # 年化到期日
    #     deListedDate = underlyingInstruments['de_listed_date'][contractCodeIndex].tolist()
    #     deListedDate.sort()
    #
    #     deDateLen = [ind for ind in range(len(deListedDate))]
    #     for ind in range(len(deListedDate)):
    #         deDateLen[ind] = (datetime.datetime.strptime(deListedDate[ind], '%Y-%m-%d') -
    #                           datetime.datetime.strptime(dateInd, '%Y-%m-%d')).days
    #     deDateYearly = pd.Series([ind / 365 + 0.0001 for ind in deDateLen], index=contractCodeList)
    #
    #     orderList = contractCodeList.copy()
    #     orderList.append(indexCode)
    #
    #     price = rq.get_price(orderList, start_date=dateInd, end_date=dateInd, frequency='1d', fields='close',
    #                          adjust_type='none', skip_suspended=False, market='cn', expect_df=False)
    #     price = price[orderList]
    #
    #     discountAbsolute = (price / price.iloc[0, 4] - 1).iloc[0, 0:4]
    #     discountYearly = discountAbsolute / deDateYearly
    #
    #     contractData.loc[dateInd, :] = contractCodeList
    #     discountData.loc[dateInd, :] = discountYearly.values

    ####################################################################################################################
    # discountData = pd.DataFrame(index=range(300))
    #
    # for yearInd in range(17, 21):
    #     for monthInd in ['03', '06', '09', '12']:
    #         contractCode = underlyingSymbol + str(yearInd) + monthInd
    #         discountData[contractCode] = None
    #         print(contractCode)
    #
    #         # contractCode = 'IC2012'
    #         listedDate = underlyingInstruments['listed_date'][underlyingInstruments['trading_code'] == contractCode].values[0]
    #         deListedDate = underlyingInstruments['de_listed_date'][underlyingInstruments['trading_code'] == contractCode].values[0]
    #
    #         dateList = rq.get_trading_dates(start_date=listedDate, end_date=deListedDate)
    #         deDateLen = [(datetime.datetime.strptime(deListedDate, '%Y-%m-%d').date() - ind).days for ind in dateList]
    #         deDateYearly = pd.Series([ind / 365 + 0.0001 for ind in deDateLen], index=dateList)
    #
    #         orderList = [contractCode, indexCode]
    #
    #         price = rq.get_price(orderList, start_date=listedDate, end_date=deListedDate, frequency='1d', fields='close',
    #                              adjust_type='none', skip_suspended=False, market='cn', expect_df=False)
    #         price = price[orderList]
    #
    #         discountAbsolute = (price.iloc[:, 0] - price.iloc[:, 1]) / price.iloc[:, 1]
    #         discountYearly = discountAbsolute / deDateYearly
    #         discountYearly = discountYearly.sort_index(ascending = False)
    #
    #         discountData[contractCode][:len(discountYearly)] = discountYearly
    #
    # discountData.to_csv('E:/中泰证券/策略/期货套利/跨期套利/季月折溢价.csv')

    ####################################################################################################################
    underlyingInstruments = underlyingInstruments.sort_values(by='maturity_date', ascending=True)

    dateNow = datetime.datetime.now().strftime('%Y-%m-%d')
    dateList = underlyingInstruments['maturity_date'][underlyingInstruments['maturity_date'] <= dateNow]

    for dateInd in dateList:
        # 交易合约
        # dateInd = dateList.values[-1]

        contractCodeIndex = [((underlyingInstruments['listed_date'] <= dateInd)[ind] and
                           (underlyingInstruments['maturity_date'] >= dateInd)[ind])
                          for ind in (underlyingInstruments['listed_date'] >= dateInd).index]
        contractCodeList = underlyingInstruments['order_book_id'][contractCodeIndex].tolist()
        contractCodeList.sort()

        startDate = underlyingInstruments['listed_date'][underlyingInstruments['listed_date'] <= dateInd].sort_values(ascending = True).values[-1]
        endDate = dateInd

        orderList = contractCodeList.copy()
        orderList.append(indexCode)

        price = rq.get_price(orderList, start_date=startDate, end_date=endDate, frequency='1d', fields='close',
                             adjust_type='none', skip_suspended=False, market='cn', expect_df=False)
        price = price[orderList]

        dateList = rq.get_trading_dates(start_date=startDate, end_date=endDate)
        yearlyData = pd.DataFrame(index=dateList, columns=contractCodeList)

        for codeIndex in contractCodeList:
            deListedDate = underlyingInstruments['de_listed_date'][underlyingInstruments['trading_code'] == codeIndex].values[0]
            deDateLen = [(datetime.datetime.strptime(deListedDate, '%Y-%m-%d').date() - ind).days for ind in dateList]
            yearlyData[codeIndex] = pd.Series([ind / 365 + 0.0001 for ind in deDateLen], index=dateList)

        basisData = price.iloc[:, 0:4].sub(price.iloc[:, 4], axis=0)
        discountAbsolute = price.iloc[:, 0:4].div(price.iloc[:, 4], axis=0) - 1
        discountYearly = discountAbsolute.div(yearlyData, axis=0)

        discountYearly.to_csv('E:/中泰证券/策略/期货套利/跨期套利/' + dateInd + '年化折溢价.csv')
        basisData.to_csv('E:/中泰证券/策略/期货套利/跨期套利/' + dateInd + '基差.csv')

    pass
