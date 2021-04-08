# @Time    : 2021/4/8 11:10
# @Author  : GUO LULU

import datetime
import pandas as pd
import numpy as np
import rqdatac as rq
import calendarSpreadArbitrage.futureData
import matplotlib.pyplot as plt

"""
长周期跨期套利
1 根据各合约的年化贴水率确定开平仓条件；
2 尽量用近月/远季合约配对套利，但需同时关注各合约的贴水率，选择最优的合约配对。先用远季进行回测。
"""


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    startDate = '2021-03-22'
    endDate = '2021-04-02'
    orderBook = ['IC2104', 'IC2109']

    pass
