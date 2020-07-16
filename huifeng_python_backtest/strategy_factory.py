"""策略工厂，根绝配置文件或者运行参数初始化一只股票的策略"""

from singleton import singleton
from pc_parity_strategy import PcParityStrategy


@singleton
class StrategyFactory:
    def __init__(self):
        pass

    def create(self):
        """根据股票创建股票的策略"""
        return PcParityStrategy()
