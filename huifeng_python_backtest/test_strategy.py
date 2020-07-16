from strategy import IStrategy
from order_manager import EntrustOrder
import random


class TestStrategy(IStrategy):
    def __init__(self):
        pass

    def do_strategy(self, position, order_manager, market, quote_manager):
        print(market.symbol, market.bid_price[0])
        # //if market.ask_volume[0] / market.bid_volume[0] > 30 and market.bid_volume[0] > 4:
        #     order = EntrustOrder()
        #     order.direction = 1
        #     order.symbol = market.symbol
        #     order.price = market.bid_price[0]
        #     order.volume = 10
        #     order.market_time = market.market_time
        #     order.time_out = 5000
        #     order_manager.insert_order(order)
