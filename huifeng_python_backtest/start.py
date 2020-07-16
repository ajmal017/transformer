"""
回测启动文件
"""

from callback import on_recv_market
from callback import on_recv_order_deal
from callback import strategy_manager
# cython模块
import py_c_api
import market_data_loader
# import pandas as pd
# import numpy as np
import multiprocessing
# import math
# from optparse import OptionParser
from utils import getOptionChainList
# import json
import os
import sys

def init():
    """
    初始化回测数据
    1)注册C接口回调
    2)确定回测的日期
    """
    py_c_api.reg_market_callback(on_recv_market)
    py_c_api.reg_order_deal_callback(on_recv_order_deal)

    if not os.path.exists('output'):
        os.mkdir('output', 0o755)


def test_worker(data_path='', day_list=[], symbols=[]):
    for day in day_list:
        # TODO...
        # strategy_manager.set_target_volume({"300019.SZ".encode(): 10000, "002596.SZ".encode(): 10000})
        markets = market_data_loader.load(data_path, day, symbols)
        markets.sort_values(by=['updatetime'], ascending=True, inplace=True)
        py_c_api.py_onload_symbol(symbols)

        py_c_api.run(day, 100)
        py_c_api.py_onload_market(markets)
        strategy_manager.reset()

        # py_c_api.run(day + '_2')
        # py_c_api.py_onload_h5(market)
        # strategy_manager.reset()

    py_c_api.stop()


def split_day_list(day_list, process_num):
    result = []
    cnt = len(day_list)
    if cnt <= process_num:
        for i in range(cnt):
            result.append(day_list[i:i+1])
    else:
        left = 0
        right = math.ceil(cnt/process_num)
        for i in range(process_num):
            result.append(day_list[left:right])
            if i < process_num - 1:
                left = right
                right = right + math.ceil((cnt-right)/(process_num-i-1))

    return result


# 启动回测
if __name__ == '__main__':
    init()
    # parser = OptionParser()
    # parser.add_option("-b", "--begin", action="store_true",
    #                   dest="begin time",
    #                   default=20200319,
    #                   help="begin time , es: 20200319")

    data_dir = os.environ['CFFEX_DATA_ROOT']
    # user can put in arguments, for example:
    # python start.py 20200413 IF2004
    if len(sys.argv)==3 :
        datestr = sys.argv[1]
        ticker = sys.argv[2]
        symbols = getOptionChainList(datestr, ticker) + [ticker]
        raw_day_list = [datestr]
    else :
        raw_day_list = ['20200413']
        symbols = ['IO2004-P-3550', 'IO2004-C-3550', 'IF2004']

    process_day_list = split_day_list(raw_day_list, 4)
    process_list = []
    for day_list in process_day_list:
        p = multiprocessing.Process(target=test_worker, args=(data_dir, day_list, symbols))
        p.start()
        process_list.append(p)

    for p in process_list:
        p.join()
