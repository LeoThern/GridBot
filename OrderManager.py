from apiKeySecret import credentials

from binance import Client
from binance import AsyncClient, BinanceSocketManager
import threading
import asyncio
import time

class OrderManager:
    def __init__(self, symbol):
        self.symbol = symbol
        self.orders = {}
        self.client = Client(credentials['key'], credentials['secret'])
        self.client_creation_time = time.time()
        self.client_UPDATE_INTERVAL = 60
        self.update_thread = threading.Thread(target=asyncio.run, args=(self._async_update(),))
        self.update_thread.daemon = True
        self.update_thread.start()

    async def _async_update(self):
        async_client = await AsyncClient.create(credentials['key'], credentials['secret'])
        bm = BinanceSocketManager(async_client)
        async with bm.user_socket() as stream:
            while True:
                data = await stream.recv()
                if data['e'] == 'executionReport':
                    self._update_order(data)

    def _update_order(self, report):
        status_conversion = {'NEW': 'open',
                             'FILLED': 'filled',
                             'PARTIALLY_FILLED': 'p_filled'}
        if not report['X'] in status_conversion:
            return
        status = status_conversion[report['X']]
        id = report['i']
        self.orders[id]['status'] = status

    def _reload_client(self):
        current_time = time.time()
        if current_time - self.client_creation_time > self.client_UPDATE_INTERVAL:
            self.client = Client(credentials['key'], credentials['secret'])
        self.client_creation_time = current_time

    def limitBuy(self, volume, price):
        self._reload_client()
        order = self.client.order_limit_buy(symbol=self.symbol,
                                            quantity=volume,
                                            price=price)
        self._append_order(order)
        return order['orderId']

    def limitSell(self, volume, price):
        self._reload_client()
        order = self.client.order_limit_sell(symbol=self.symbol,
                                             quantity=volume,
                                             price=price)
        self._append_order(order)
        return order['orderId']

    def _append_order(self, order):
        id = order['orderId']
        side = order['side'].lower()
        self.orders[id] = {'status':'open',
                           'side': side}

    def get_status(self, id):
        return self.orders[id]['status']

    def cancel(self, id):
        self._reload_client()
        self.client.cancel_order(symbol=self.symbol, orderId=id)
        del self.orders[id]

    def cancelAll(self):
        for id in self.orders:
            self.cancel(id)