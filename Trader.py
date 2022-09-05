from apiKeySecret import credentials
import binanceOrders as bo

from binance import Client
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException
import datetime as dt
import asyncio


def time_prefix():
    current_time = dt.datetime.now().strftime("%H:%M")
    return f"[{current_time}]"


class Trader:
    def __init__(self, config, window, automaticTrades=False):
        self.config = config
        self.window = window
        self.automaticTrades = automaticTrades
        self.mode = 'waiting'
        self.price = {
            'current': 0.0,
            'high': None,
            'low': None,
        }
        self.position = {
            'entry_price': 0.0,
            'base_volume': 0.0,
            'quote_volume': 0.0,
        }
        self.limitOrder = None
        self.stopOrder = None

    async def async_price_update(self, lock):
        async_client = await AsyncClient.create(credentials['key'], credentials['secret'])
        bm = BinanceSocketManager(async_client)
        async with bm.kline_socket(symbol=self.config['Profile1']['symbol']) as stream:
            while True:
                data = await stream.recv()
                ohlc = data['k']
                open, high, low, close = float(ohlc['o']), float(ohlc['h']), float(ohlc['l']), float(ohlc['c'])

                lock.acquire()
                self.price['current'] = close

                if not self.price['high'] or high > self.price['high']:
                    self.price['high'] = high
                if not self.price['low'] or low < self.price['low']:
                    self.price['low'] = low

                if not self.lastOrder['filled'] and self.lastOrder['Id']:
                    self.check_if_last_order_filled()

                lock.release()
                self.window.write_event_value('UPDATE-VALUES', None)

    async def async_event_update(self, lock):
        async_client = await AsyncClient.create(credentials['key'], credentials['secret'])
        bm = BinanceSocketManager(async_client)
        async with bm.user_socket() as stream:
            while True:
                data = await stream.recv()
                print(data)

    def check_trade_conditions(self):
        if not self.automaticTrades or not self.limitOrder.is_filled():
            return

        if self.mode == 'waiting':
            if (self.price['current'] - self.price['low']) > float(self.config['Profile1']['threshold-buy']):
                if (self.position['entry_price'] - self.price['current']) > float(
                        self.config['Profile1']['min-profit']):
                    self.limit_buy()

        if self.mode == 'holding':
            if (self.price['high'] - self.price['current']) > float(self.config['Profile1']['threshold-sell']):
                if (self.price['current'] - self.position['entry_price']) > float(
                        self.config['Profile1']['min-profit']):
                    self.limit_sell()

    def catchApiError(func):
        def wrapper(self):
            try:
                func(self)
            except BinanceAPIException as e:
                self.window.write_event_value('BINANCE-ERROR', e)
        return wrapper

    @catchApiError
    def check_if_last_order_filled(self):
        last_order = self.client.get_order(symbol=self.config['Profile1']['symbol'],
                                           orderId=self.lastOrder['Id'])
        if last_order['status'] == Client.ORDER_STATUS_FILLED:
            print(time_prefix(), ' Order filled')
            self.position['entry_price'] = float(last_order['price'])
            self.lastOrder['filled'] = True
            self.lastOrder['open'] = False

            if self.mode == 'waiting':
                self.mode = 'holding'
                self.price['high'] = None
                self.position['base_volume'] = float(last_order['executedQty'])
                return
            if self.mode == 'holding':
                self.mode = 'waiting'
                self.price['low'] = None
                self.position['base_volume'] = 0.0
                self.position['quote_volume'] = float(last_order['cummulativeQuoteQty'])

    def _print_trade_log(self, direction):
        lines = [f"\tCurrent Price: {self.price['current']}",
                 f"\tHigh    Price: {self.price['high']}",
                 f"\tLow     Price: {self.price['low']}", ]

        price_info = str('\n'.join(lines))

        if self.automaticTrades:
            if direction == 'buy':
                print(time_prefix(), ' Buying Threshold and MinProfit reached', '\n', price_info)
            if direction == 'sell':
                print(time_prefix(), ' Selling Threshold and MinProfit reached', '\n', price_info)
        else:
            if direction == 'buy':
                print(time_prefix(), ' Manual Buy', '\n', price_info)
            if direction == 'sell':
                print(time_prefix(), ' Manual Sell', '\n', price_info)
