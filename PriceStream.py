from apiKeySecret import credentials

from binance import AsyncClient, BinanceSocketManager
import threading
import asyncio

class PriceStream:
    def __init__(self, symbol):
        self.symbol = symbol
        self.window = None
        self.price = 0.0
        self.update_thread = threading.Thread(target=asyncio.run, args=(self._async_update(),))
        self.update_thread.daemon = True
        self.update_thread.start()

    def get_price(self):
        return self.price

    def subscribe_window(self, window):
        self.window = window

    async def _async_update(self):
        async_client = await AsyncClient.create(credentials['key'], credentials['secret'])
        bm = BinanceSocketManager(async_client)
        async with bm.kline_socket(symbol=self.symbol) as stream:
            while True:
                data = await stream.recv()
                ohlc = data['k']
                close = float(ohlc['c'])
                self.price = close
                if self.window:
                    self.window.write_event_value('PRICE-STREAM', self.price)