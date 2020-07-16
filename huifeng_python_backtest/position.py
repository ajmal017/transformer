"""仓位信息"""


class Position:
    def __init__(self):
        self.filled_bid = 0
        self.filled_ask = 0
        self.pending_bid = 0
        self.pending_ask = 0
        self.pending_orders = {}
        pass
