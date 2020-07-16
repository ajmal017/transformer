"""股票的策略集合"""

from singleton import singleton
from strategy_factory import StrategyFactory
from order_manager import OrderManager
from position import Position
from quote_manager import QuoteManager

# import json
# from strategy import IStrategy


@singleton
class StrategyManager:
    def __init__(self):
        # 股票 -> 策略
        self.strategy_instance = StrategyFactory().create()
        # 股票 -> 仓位
        self.stock_position_dic = {}
        # 订单管理
        self.order_manager = OrderManager(self.stock_position_dic)

        self.quote_manager = QuoteManager()

        self.cumPNL = 0

    def recv_market(self, market_data):
        # print("recv_market callback:", market_data.symbol, 
        # market_data.market_time, market_data.high_price, 
        # market_data.pre_close_price, self.market_count)
        # 股票的策略不存在，初始化
        if market_data.symbol not in self.stock_position_dic:
            self.stock_position_dic[market_data.symbol] = Position()

        # 这只股票的仓位信息
        stock_position = self.stock_position_dic[market_data.symbol]
        # update market quotes
        self.quote_manager.update_table(market_data.symbol, market_data)
        # 运算策略
        self.strategy_instance.do_strategy(stock_position, self.order_manager, market_data, self.quote_manager)

    def recv_order_deal(self, deal_info):
        self.order_manager.recv_order_deal(deal_info)

    def reset(self):
        # 股票 -> 仓位
        self.stock_position_dic.clear()


    def addPNL(self, pnl):
        self.cumPNL + pnl
