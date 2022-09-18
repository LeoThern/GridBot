from OrderManager import OrderManager
from apiKeySecret import credentials

from binance import AsyncClient, BinanceSocketManager


class GridBot:
    def __init__(self, config, priceStream):
        self.config = config
        self.pS = priceStream
        self.OM = OrderManager(self.config.symbol)
        self.isActive = False
        self.current_price = None
        self.Grid = GridCalculator(self.config.upper_bound,
                                   self.config.lower_bound,
                                   self.config.line_count)
        self.Grid.set_baseVolumePerLine(self.config.base_volume_line)
        self.guiValues = None
        self.orderIds = {}
        self.window = None

    def subscribe_window(self, window):
        self.window = window

    async def async_update(self):
        async_client = await AsyncClient.create(credentials['key'], credentials['secret'])
        bm = BinanceSocketManager(async_client)
        async with bm.kline_socket(symbol=self.config.symbol) as stream:
            while True:
                data = await stream.recv()
                ohlc = data['k']
                close = float(ohlc['c'])
                self.current_price = close
                self.Grid.update_current_price(close)
                if not self.guiValues or self.Grid.orders_changed:
                    if self.isActive:
                        self._check_orders_match_grid()
                    values = self.Grid.get_guiValues()
                    self.guiValues = values
                else:
                    values = self.guiValues
                values['price'] = close
                self.window.write_event_value('UPDATE-PRICE', values)

    def _replace_if_filled(self):
        for i in range(self.config.line_count):
            if self.OM.get_status(self.orderIds[i]) == 'filled':
                self.OM.cancel(self.orderIds[i])
                self._place_order(i)


    def place(self):
        for i in range(self.config.line_count):
            self._place_order(i)
        self.isActive = True

    def cancel(self):
        self.OM.cancelAll()
        self.isActive = False

    def _place_order(self, index):
        side = self.Grid.get_side(index)
        price = self.Grid.get_price(index)

        if side == 'buy':
            volume = self.Grid.get_baseVolume(index)
            id = self.OM.limitBuy(volume, price)
        if side == 'sell':
            volume = self.Grid.get_quoteVolume(index)
            id = self.OM.limitSell(volume, price)
        self.orderIds[index] = id



class GridCalculator:
    def __init__(self, upper_bound, lower_bound, line_count):
        self.grid_range = upper_bound - lower_bound
        grid_line_height = self.grid_range / (line_count - 1)
        prices = [lower_bound + (grid_line_height * i) for i in range(line_count)]
        prices[-1] = upper_bound  # counter rounding error
        self.grid = []
        for price in prices:
            self.grid.append({'price':price,
                              'side':None,
                              'baseVolume':None,
                              'quoteVolume':None})
        self.current_price = None
        self.orders_changed = False

    def set_quoteVolumePerLine(self, quote_volume):
        for order in self.grid:
            order['quoteVolume'] = quote_volume
            order['baseVolume'] = quote_volume / order['price']

    def set_baseVolumePerLine(self, base_volume):
        for order in self.grid:
            order['baseVolume'] = base_volume
            order['quoteVolume'] = base_volume * order['price']

    def update_current_price(self, current_price):
        self.current_price = current_price
        self.orders_changed = False

        for order in self.grid:
            if order['price'] <= current_price:
                if order['side'] != 'buy':
                    order['side'] = 'buy'
                    self.orders_changed = True
            if order['price'] > current_price:
                if order['side'] != 'sell':
                    order['side'] = 'sell'
                    self.orders_changed = True

    def get_guiValues(self):
        assert self.current_price, 'cant get order data without price'
        sell_count, buy_count, base_volume, quote_volume = 0, 0, 0, 0
        for order in self.grid:
            if order['side'] == 'buy':
                buy_count += 1
                quote_volume += order['quoteVolume']
            if order['side'] == 'sell':
                sell_count += 1
                base_volume += order['baseVolume']

        return {'sell_count':sell_count,
                'buy_count':buy_count,
                'base_volume':base_volume,
                'quote_volume':quote_volume,}

    def get_price(self, index):
        return self.grid[index]['price']

    def get_side(self, index):
        return self.grid[index]['side']

    def get_quoteVolume(self, index):
        return self.grid[index]['quoteVolume']

    def get_baseVolume(self, index):
        return self.grid[index]['baseVolume']