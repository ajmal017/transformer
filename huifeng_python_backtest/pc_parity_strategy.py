import math
from strategy import IStrategy
from utils import contructEntrustOrder
# import random

cumPNL = 0
cumVolume = 0
cumComboID = 0


class PcParityStrategy(IStrategy):
    def __init__(self):
        pass

    def do_strategy(self, position, order_manager, market, quote_manager):
        global cumPNL, cumVolume, cumComboID

        opt_symbol = market.symbol
        # we only tick on PUTs, so CALLs and FUT are all updated
        if '-P-' not in opt_symbol:
            return

        fut_symbol = opt_symbol.split('-')[0]
        fut_symbol = fut_symbol.replace('IO', 'IF')
        futQuote = quote_manager.get_quote(fut_symbol)
        if futQuote is None:
            print('can not find future in market data: ', fut_symbol, ' return')
            return

        parity_sym = opt_symbol.replace('-P-', '-C-')
        parityQuote = quote_manager.get_quote(parity_sym)
        if parityQuote is None:
            print('can not find parity call in market data: ', parity_sym, ' return')
            return

        strike = float(opt_symbol.split('-')[2])
        optQuote = quote_manager.get_quote(opt_symbol)
        
        opt_bid = optQuote.bid_price[0]
        opt_ask = optQuote.ask_price[0]
        bidSize = optQuote.bid_volume[0]
        askSize = optQuote.ask_volume[0]

        parity_bid = parityQuote.bid_price[0]
        parity_ask = parityQuote.ask_price[0]
        parity_bidSize = parityQuote.bid_volume[0]
        parity_askSize = parityQuote.ask_volume[0]
        synth_buy_price = parity_ask - opt_bid + strike
        synth_sell_price = parity_bid - opt_ask + strike

        fut_buy_price = futQuote.ask_price[0]
        fut_sell_price = futQuote.bid_price[0]
        fut_buy_volume = futQuote.ask_volume[0]
        fut_sell_volume = futQuote.bid_volume[0]

        # cross-market check:
        if (opt_bid >= opt_ask) | (parity_bid >= parity_ask) | (fut_sell_price >= fut_buy_price):
            print('bid equal or larger than offer happened at strike=', strike)
            print('p_bo=', opt_bid, ' ', opt_ask, 'c_bo=', parity_bid, ' ', parity_ask, 'fut_bo=', fut_sell_price, ' ', fut_buy_price)
            return

        if synth_buy_price < fut_sell_price:
            trading_volume = min(min(parity_askSize, bidSize), fut_sell_volume*3)
            if trading_volume <= 0:
                # strictly speaking this should not happen, but who knows....
                print('no volume at some of legs, skip')
                return
            # we are buying call, selling put, and selling future:
            order = contructEntrustOrder(opt_symbol, 1, opt_bid, trading_volume, market.market_time)
            # order_manager.insert_order(order)
            order = contructEntrustOrder(parity_sym, 0, parity_ask, trading_volume, market.market_time)
            # order_manager.insert_order(order)
            order = contructEntrustOrder(fut_symbol, 1, fut_sell_price, trading_volume, market.market_time)
            # order_manager.insert_order(order)
            arb = fut_sell_price - synth_buy_price
        elif synth_sell_price > fut_buy_price:
            trading_volume = min(min(parity_bidSize, askSize), fut_buy_volume*3)
            if trading_volume <= 0:
                print('no volume at some of legs, skip')
                return
            # we are selling call, buying put, and buying future:
            order = contructEntrustOrder(opt_symbol, 0, opt_ask, trading_volume, market.market_time)
            # order_manager.insert_order(order)
            order = contructEntrustOrder(parity_sym, 1, parity_bid, trading_volume, market.market_time)
            # order_manager.insert_order(order)
            order = contructEntrustOrder(fut_symbol, 0, fut_buy_price, trading_volume, market.market_time)
            # order_manager.insert_order(order)
            arb = synth_sell_price - fut_buy_price
        else:
            return
        
        if ((arb * 100) > 40) & (trading_volume >= 3 ):
            trdVolRounded = math.floor(trading_volume / 3) * 3
            cumPNL = cumPNL + trdVolRounded * (arb * 100 - 40)
            cumVolume = cumVolume + trdVolRounded
            cumComboID = cumComboID + 1
            print('K=', strike, ', arb=', int(arb * 100)/100, ', trdCount=', cumComboID, ', volume=', trdVolRounded, ', cumPNL=', cumPNL, ', cumVol=', cumVolume)
