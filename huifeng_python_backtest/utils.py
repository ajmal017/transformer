import os
from order_manager import EntrustOrder


def getOptionChainList(datestr, ticker):
    directory = os.environ['CFFEX_DATA_ROOT'] + '/' + datestr + '/'
    options = []
    for filename in os.listdir(directory):
        if filename.startswith(ticker.replace('IF', 'IO') + '-'):
            options.append(filename.split('_')[0])
    return options


def contructEntrustOrder(symbol, direction, price, volume, time, time_out=500):
    order = EntrustOrder()
    order.direction = direction
    order.symbol = symbol
    order.price = price
    order.volume = volume
    order.market_time = time
    order.time_out = time_out
    return order
