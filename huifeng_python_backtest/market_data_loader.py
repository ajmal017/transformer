import os
import time
import pandas as pd
import numpy as np
from six import iteritems


init_cols = [
                'askprice1', 'askprice2', 'askprice3', 'askprice4', 'askprice5',
                'askvolume1', 'askvolume2', 'askvolume3', 'askvolume4', 'askvolume5',
                'bidprice1', 'bidprice2', 'bidprice3', 'bidprice4', 'bidprice5',
                'bidvolume1', 'bidvolume2', 'bidvolume3', 'bidvolume4', 'bidvolume5',
                'volume', 'turnover', 'openinterest', 'presettleprice', 'preclose',
                'open', 'high', 'low', 'last', 'markettime', 'updatetime', 's_pos'
            ]


def to_timestamp(time_str):
    time_array = time.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    micro = int(time_str[-6:])
    ts = int(time.mktime(time_array)) * 1000000 + micro
    return ts


def to_timestamp_milli(time_str):
    time_array = time.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    milli = int(time_str[-3:])
    ts = int(time.mktime(time_array)) * 1000000 + milli*1000
    return ts


def load(base_path='', trading_day='', symbols=[]):

    dic = {}
    symbol_pos = 0
    # Generate file path
    day_path = os.path.join(base_path, trading_day)
    for symbol in symbols:
        file_name = symbol + '_' + trading_day + '.csv'
        csv_file_absolute_path = os.path.join(day_path, file_name)

        print('Start loading data:', csv_file_absolute_path)

        # Load csv file
        df = pd.read_csv(csv_file_absolute_path)
        if len(df) < 2:
            print('no market data:', csv_file_absolute_path)
            continue
        len_time = len(df['markettime'][0])
        if len_time == 23:
            df.loc[:, 'markettime'] = df['markettime'].apply(to_timestamp_milli)
        else:
            df.loc[:, 'markettime'] = df['markettime'].apply(to_timestamp)
        df.loc[:, 'updatetime'] = df['updatetime'].apply(to_timestamp)
        df['s_pos'] = symbol_pos
        dic[symbol] = df[init_cols]
        symbol_pos = symbol_pos + 1

    return pd.concat(dic.values())
