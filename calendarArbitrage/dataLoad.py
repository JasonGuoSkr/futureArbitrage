import datetime
import pandas as pd
import rqdatac as rq


"""
数据加载
"""


def data_load(args, start_date, end_date):
    """
    数据加载
    :param args: 合约list or 合约str
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return:
    """
    if type(args) is str:
        contract_id = args
        data_dict = {contract_id: pd.DataFrame()}
        try:
            contract_data = rq.get_price(contract_id, start_date=start_date, end_date=end_date,
                                         frequency='1d', fields=None)
        except AttributeError:
            print(contract_id)
            raise AttributeError
        data_dict[contract_id] = contract_data
    else:
        data_dict = dict()
        for contract_id in args:
            try:
                contract_data = rq.get_price(contract_id, start_date=start_date, end_date=end_date,
                                             frequency='1d', fields=None)
            except AttributeError:
                print(contract_id)
                raise AttributeError
            data_dict[contract_id] = contract_data

    return data_dict


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    startDate = '20200302'
    endDate = '20200409'

    contractList = ('000016.XSHG', '000300.XSHG','000905.XSHG', '000852.XSHG', '399006.XSHE')
    # contractList = ('IF2003', 'IF2004')
    # contractList = 'IF2003'

    Data = data_load(contractList, start_date=startDate, end_date=endDate)
