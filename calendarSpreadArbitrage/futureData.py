# @Time    : 2021/3/6 13:44
# @Author  : GUO LULU

import datetime
import pandas as pd
import rqdatac as rq


"""
期货合约下载/tick数据加载
"""


def future_data_load(args, start_date, end_date):
    """
    期货tick数据
    :param args: 合约list
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return:
    """
    if args:
        data_dict = dict()
        date_list = rq.get_trading_dates(start_date=start_date, end_date=end_date)

        for contract_id in args:
            data = pd.DataFrame()

            for date_ind in date_list:
                try:
                    daily_data = get_tick(contract_id, date_ind, date_ind)
                except AttributeError:
                    print(contract_id)
                else:
                    # daily_data.drop_duplicates(keep='first', inplace=True)
                    daily_data = daily_data.loc[~daily_data.index.duplicated(keep='first')]
                    daily_data = data_resample(daily_data)
                    data = pd.concat([data, daily_data], axis=0)

            data_dict[contract_id] = data

        return data_dict


def data_resample(data, freq='500ms'):
    """
    数据填充补齐
    :param data: 原数据
    :param freq: 频率
    :return:
    """
    data = data.resample(freq).ffill()
    data = data.between_time('09:30:00', '14:59:00')
    # data = data.between_time('09:30:00', '15:00:00')

    return data.between_time('13:00:00', '11:30:00')


def get_tick(contract_id, start_date, end_date):
    """
    tick数据下载
    :param contract_id:
    :param start_date:
    :param end_date:
    :return:
    """
    df_tick = rq.get_price(contract_id, start_date=start_date, end_date=end_date, frequency='tick', fields=None)

    return df_tick.between_time('09:25:00', '15:10:00')


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    # trade_date = datetime.datetime.now().strftime('%Y%m%d')
    startDate = '2021-01-01'
    endDate = '2021-03-05'
    underlyingSymbol = 'IF'

    allInstruments = rq.all_instruments(type='Future')
    underlyingInstruments = allInstruments[allInstruments['underlying_symbol'] == underlyingSymbol]
    underlyingInstruments = underlyingInstruments[~(underlyingInstruments['listed_date'] == '0000-00-00')]
    underlyingInstruments = underlyingInstruments.sort_values(by='listed_date', ascending=True)

    dateList = rq.get_trading_dates(start_date=startDate, end_date=endDate)

    for dateInd in dateList:
        # dateInd = dateList[0]
        dateInd = dateInd.strftime('%Y-%m-%d')

        orderBookIndex = [((underlyingInstruments['listed_date'] <= dateInd)[ind] and
                           (underlyingInstruments['maturity_date'] >= dateInd)[ind])
                          for ind in (underlyingInstruments['listed_date'] >= dateInd).index]
        orderBookList = underlyingInstruments['order_book_id'][orderBookIndex].tolist()
        orderBookList.sort()

        dataLoad = future_data_load(orderBookList, start_date=dateInd, end_date=dateInd)
