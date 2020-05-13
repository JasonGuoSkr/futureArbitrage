# @Time    : 2020/5/12 16:50
# @Author  : GUO LULU

import datetime
import pandas as pd
import rqdatac as rq


"""
期货连续合约数据加载
"""


def continuous_future_data(underlying_symbol, start_date=None, end_date=None, rule=1, rank=0):
    contract_series = rq.futures.get_dominant(underlying_symbol, start_date=None, end_date=None, rule=0)


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    startDate = '20200302'
    endDate = '20200409'
    underlyingSymbol = 'IF'

    contractSeries = rq.futures.get_dominant('IF', start_date='20200102', end_date='20200409', rule=0, rank=1)
