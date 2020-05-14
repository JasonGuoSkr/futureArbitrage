# @Time    : 2020/5/11 18:20
# @Author  : GUO LULU

import os
import time
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import interterporalArbitrage.futureData
import rqdatac as rq


"""
期货价差计算
"""


def spread_compute(contract_list, start_date=None, end_date=None):
    """
    跨期期货价差计算
    :param contract_list:
    :param start_date:
    :param end_date:
    :return:
    """

    # 数据加载
    data_dict = interterporalArbitrage.futureData.future_data_load(contract_list, start_date, end_date)

    # 价差计算
    data_df = pd.DataFrame()
    for contract_id in contract_list:
        price_last = data_dict[contract_id]['close']
        price_last.name = contract_id
        data_df = pd.concat([data_df, price_last], axis=1)
    data_df['spread'] = data_df.iloc[:, 0] - data_df.iloc[:, 1]

    return data_df


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    startDate = '20190302'
    endDate = '20190508'

    contractList = ('IF1906', 'IF1909')

    Data = interterporalArbitrage.futureData.future_data_load(contractList, start_date=startDate, end_date=endDate)
    spreadData = spread_compute(contractList, start_date=startDate, end_date=endDate)
