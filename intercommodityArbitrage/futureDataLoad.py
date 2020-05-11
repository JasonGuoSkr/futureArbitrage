import os
import datetime
import rqdatac as rq


"""
期货tick数据下载，每日更新
"""


def future_data_load(data_dir, *args, start_date, end_date):
    """
    期货tick数据
    :param data_dir: 数据路径
    :param args: 合约list
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return:
    """
    if args:
        date_list = rq.get_trading_dates(start_date=start_date, end_date=end_date)
        for contract_id in args:
            for date_ind in date_list:
                date_ind = date_ind.strftime('%Y%m%d')
                try:
                    contract_data = get_tick(contract_id, date_ind, date_ind)
                except AttributeError:
                    print(contract_id)
                else:
                    contract_data.to_csv(data_dir + contract_id + '_' + date_ind + '.csv')


def get_tick(contract_id, start_date, end_date):
    """
    tick数据下载
    :param contract_id:
    :param start_date:
    :param end_date:
    :return:
    """
    df_tick = rq.get_price(contract_id, start_date=start_date, end_date=end_date, frequency='tick', fields=None)

    return df_tick.between_time('09:25:00', '15:01:00')


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    dataDir = "E:/中泰证券/策略/期权套利/期货tick数据/"
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)

    # trade_date = datetime.datetime.now().strftime('%Y%m%d')
    startDate = '20200302'
    endDate = '20200309'

    # contractList = ['IF2001', 'IH2001']
    contractList = ['IF2003']

    future_data_load(dataDir, *contractList, start_date=startDate, end_date=endDate)
