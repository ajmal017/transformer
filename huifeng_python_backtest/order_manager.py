"""订单管理"""

# cython模块
import py_c_api
from singleton import singleton


class EntrustOrder:
    def __init__(self):
        self.symbol = ""
        self.price = 0
        self.volume = 0
        # 订单ID，python端生成，类型字符串
        self.order_id = ""
        # 买=0 卖=1
        self.direction = 0
        # 订单超时时间
        self.time_out = 0
        # 下单时间
        self.market_time = 0
        self.dealt_volume = 0

@singleton
class OrderManager:
    def __init__(self, all_pos_dic):
        # todo: 定义其他订单管理数据
        self.pos_dic = all_pos_dic
        self.order_idx = 1

    def recv_order_deal(self, deal_info):
        """更新订单状态和股票关联的仓位"""
        # print("recv deal_info callback:", deal_info.symbol, deal_info.volume, deal_info.timestamp)
        stock_pos = self.pos_dic[deal_info.symbol]
        order = stock_pos.pending_orders[deal_info.order_id.decode()]
        if deal_info.volume > 0:  # fill
            order.dealt_volume = order.dealt_volume + deal_info.volume
            if order.dealt_volume >= order.volume:
                stock_pos.pending_orders.pop(order.order_id)
            if deal_info.direction == 0:
                stock_pos.filled_bid = stock_pos.filled_bid + deal_info.volume
                stock_pos.pending_bid = stock_pos.pending_bid - deal_info.volume
            else:
                stock_pos.filled_ask = stock_pos.filled_ask + deal_info.volume
                stock_pos.pending_ask = stock_pos.pending_ask - deal_info.volume
        else:  # canceled
            stock_pos.pending_orders.pop(order.order_id)
            if deal_info.direction == 0:
                stock_pos.pending_bid = stock_pos.pending_bid + deal_info.volume
            else:
                stock_pos.pending_ask = stock_pos.pending_ask + deal_info.volume
        # print(deal_info.symbol, stock_pos.filled_bid, stock_pos.filled_ask, stock_pos.pending_bid, stock_pos.pending_ask, len(stock_pos.pending_orders))

    def insert_order(self, entrust_order):
        """下单，调用C扩展API下单"""
        # todo: 记录订单
        entrust_order.order_id = entrust_order.symbol + '_' + str(self.order_idx)
        self.order_idx = self.order_idx + 1
        stock_pos = self.pos_dic[entrust_order.symbol]
        if entrust_order.direction == 0:
            stock_pos.pending_bid = stock_pos.pending_bid + entrust_order.volume
        else:
            stock_pos.pending_ask = stock_pos.pending_ask + entrust_order.volume
        # print(entrust_order.symbol, stock_pos.target_volume)

        stock_pos.pending_orders[entrust_order.order_id] = entrust_order
        # 下单
        py_c_api.entrust_order(entrust_order)

    def delete_order(self, entrust_order):
        """下单，调用C扩展API下单"""
        py_c_api.revoke_order(entrust_order)
