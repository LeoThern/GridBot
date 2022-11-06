from apiKeySecret import credentials

from binance import Client
from binance import AsyncClient, BinanceSocketManager
import threading
import datetime
import asyncio
import time

def time_prefix():
    current_time = datetime.datetime.now().strftime("%H:%M")
    return f"[{current_time}]"

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
                    if data['i'] in self.orders:
                        self._update_order(data)

    def _update_order(self, report):
        status_conversion = {'NEW': 'open',
                             'FILLED': 'filled',
                             'PARTIALLY_FILLED': 'p_filled'}
        if not report['X'] in status_conversion:
            return
        status = status_conversion[report['X']]
        id = report['i']
        print(time_prefix(), f"[!] {report['S']} Order at {report['p']}: {status}")
        self.orders[id]['status'] = status

    def _reload_client(self):
        current_time = time.time()
        if current_time - self.client_creation_time > self.client_UPDATE_INTERVAL:
            self.client = Client(credentials['key'], credentials['secret'])
        self.client_creation_time = current_time

    def _get_quote_balance(self, symbol):
        self._reload_client()
        quoteAsset = self.client.get_symbol_info(symbol)['quoteAsset']
        data = self.client.get_asset_balance(quoteAsset)
        return float(data['free'])

    def limitBuy(self, volume, price):
        self._reload_client()
        print(time_prefix(), f"[+] Trying to place Limit Buy for {volume} at {price}")
        order = self.client.order_limit_buy(symbol=self.symbol,
                                            quantity=volume,
                                            price=price)
        if order['status'] == 'NEW':
            self._append_order(order)
            return order['orderId']
        else:
            time.sleep(2)
            return self.limitBuy(volume, price)

    def limitSell(self, volume, price):
        self._reload_client()
        print(time_prefix(), f"[+] Trying to place Limit Sell for {volume} at {price}")
        order = self.client.order_limit_sell(symbol=self.symbol,
                                             quantity=volume,
                                             price=price)
        if order['status'] == 'NEW':
            self._append_order(order)
            return order['orderId']
        else:
            time.sleep(2)
            return self.limitSell(volume, price)

    def _append_order(self, order):
        id = order['orderId']
        side = order['side'].lower()
        self.orders[id] = {'status':'open',
                            'side': side}

    def get_status(self, id):
        return self.orders[id]['status']

    def get_side(self, id):
        return self.orders[id]['side']

    def cancel(self, id):
        self._reload_client()
        self.client.cancel_order(symbol=self.symbol, orderId=id)

    def cancelAll(self):
        for id in self.orders:
            if self.get_status(id) == 'open':
                self.cancel(id)