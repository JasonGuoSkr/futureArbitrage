# @Time    : 2020/5/13 14:01
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

    # 参数
    dateLen = 10
    benchDate = '0430'
    contractList = ('000016.XSHG', '000300.XSHG','000905.XSHG', '000852.XSHG', '399006.XSHE')

    # 计算
    for year_id in range(2011, 2021):
        print(year_id)
        endDate = str(year_id) + benchDate
        endDate = rq.get_next_trading_date(rq.get_previous_trading_date(endDate))
        startDate = rq.get_previous_trading_date(endDate, n=dateLen)

        Data = calendarArbitrage.dataLoad.data_load(contractList, start_date=startDate, end_date=endDate)
