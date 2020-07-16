"""定义c接口的回调"""

from strategy_manager import StrategyManager

# 全局变量manager
strategy_manager = StrategyManager()


def on_recv_market(m):
    """收到了行情数据
    m对象在cython模块定义"""
    strategy_manager.recv_market(m)


def on_recv_order_deal(deal):
    """收到了订单逐笔成交信息, deal对象在cython模块定义"""
    strategy_manager.recv_order_deal(deal)



