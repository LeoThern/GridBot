from OrderManager import OrderManager

from time import sleep
import threading

class GridBot:
    def __init__(self, config, priceStream):
        self.config = config
        self.pS = priceStream
        self.OM = OrderManager(self.config.symbol)
        self.gridPrices = []
        self.gridOrders = {}
        self.window = None
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def subscribe_window(self, window):
        self.window = window

    def isActive(self):
        return bool(self.gridPrices)

    def place(self):
        self.gridPrices = self._calculate_prices(self.config.upper_bound,
                                                self.config.lower_bound,
                                                self.config.line_count)
        for price in self.gridPrices:
            self._place_gridLine(price)

    def cancel(self):
        self.gridPrices = []
        self.OM.cancelAll()

    def _update_loop(self):
        UPDATE_TIMEOUT = 2
        while True:
            sleep(UPDATE_TIMEOUT)
            self._replace_orders()
            if self.window:
                values = self._guiValues()
                self.window.write_event_value('UPDATE-VALUES', values)

    def _replace_orders(self):
        for price in self.gridPrices:
            id = self.gridOrders[price]
            if self.OM.get_status(id) == 'filled':
                self.OM.cancel(id)
                self._place_gridLine(price)

    def _place_gridLine(self, linePrice):
        side, volume = self._side_volume_of_line(linePrice)
        if side == 'buy':
            id = self.OM.limitBuy(volume, linePrice)
        else:
            id = self.OM.limitSell(volume, linePrice)
        self.gridOrders[linePrice] = id

    def _calculate_prices(self, upper_bound, lower_bound, line_count):
        grid_range = upper_bound - lower_bound
        grid_line_height = grid_range / (line_count - 1)
        prices = [lower_bound + (grid_line_height * i) for i in range(line_count)]
        prices[-1] = upper_bound  # counter rounding error
        return prices

    def _side_volume_of_line(self, linePrice):
        side = 'buy' if linePrice < self.pS.get() else 'sell'
        base_volume = self.config.base_volume_line
        quote_volume = base_volume * linePrice
        return side, quote_volume if side == 'buy' else base_volume

    def _guiValues(self):
        buy_count, sell_count = 0, 0
        base_volume, quote_volume = 0.0, 0.0
        prices = self._calculate_prices(self.config.upper_bound,
                                        self.config.lower_bound,
                                        self.config.line_count)
        for price in prices:
            side, volume = self._side_volume_of_line(price)
            if side == 'buy':
                buy_count += 1
                quote_volume += volume
            else:
                sell_count += 1
                base_volume += volume

        return {'buy_count':buy_count,
                'sell_count':sell_count,
                'base_volume':base_volume,
                'quote_volume':quote_volume,}