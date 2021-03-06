# @Time    : 2020/5/12 16:50
# @Author  : GUO LULU

import datetime
import pandas as pd
import interterporalArbitrage.futureData
import rqdatac as rq


"""
期货连续合约数据加载
"""


def continuous_future_data(underlying_symbol, start_date=None, end_date=None, rule=1, rank=1):
    contract_series = rq.futures.get_dominant(underlying_symbol, start_date, end_date, rule, rank)

    continuous_data = pd.DataFrame()
    for date_id in contract_series.index:
        contract_id = contract_series[date_id]
        contract_data = interterporalArbitrage.futureData.future_data_load(contract_id,
                                                                           start_date=date_id, end_date=date_id)
        continuous_data = pd.concat([continuous_data, contract_data[contract_id]], axis=0)

    return continuous_data


if __name__ == '__main__':
    rq.init("ricequant", "8ricequant8", ('10.29.135.119', 16010))

    startDate = '20200302'
    endDate = '20200409'
    underlyingSymbol = 'IF'

    contractSeries = continuous_future_data(underlyingSymbol, start_date=startDate, end_date=endDate, rule=1, rank=1)
