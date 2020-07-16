"""
回测的策略的基类
用户自定义子类，通过某种形式让StrategyFactory实例化用户自定义策略
"""


class IStrategy:
    def __init__(self):
        pass

    def do_strategy(self, position, order_manager, markets, quote_manager, strategy_param):
        """一只股票的策略函数"""
        pass
