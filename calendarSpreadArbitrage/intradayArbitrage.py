# @Time    : 2021/4/7 13:46
# @Author  : GUO LULU

import datetime
import pandas as pd
import numpy as np
import rqdatac as rq
import calendarSpreadArbitrage.futureData
import matplotlib.pyplot as plt


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    startDate = '2021-03-22'
    endDate = '2021-04-02'
    orderBook = ['IC2104', 'IC2105']

    futureData = calendarSpreadArbitrage.futureData.future_data_load(orderBook, start_date=startDate, end_date=endDate)



    pass
