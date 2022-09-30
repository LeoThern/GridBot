from OrderManager import OrderManager

from time import sleep
import threading

class GridBot:
    def __init__(self, config, priceStream):
        self.config = config
        self.pS = priceStream
        self.OM = OrderManager(self.config.symbol)
        self.gridPrices = []
        self.gridPrices_lock = threading.Lock()
        self.gridOrders = {}
        self.pendingLine = 0.0
        self.window = None
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def subscribe_window(self, window):
        self.window = window

    def isActive(self):
        return bool(self.gridPrices)

    def place(self):
        self.gridPrices_lock.acquire()
        self.gridPrices = self._calculate_prices(self.config.upper_bound,
                                                 self.config.lower_bound,
                                                 self.config.line_count)
        for price in self.gridPrices:
            self._place_gridLine(price)
        self.gridPrices_lock.release()

    def cancel(self):
        self.gridPrices_lock.acquire()
        self.OM.cancelAll()
        self.gridPrices = []
        self.gridPrices_lock.release()

    def _update_loop(self):
        UPDATE_TIMEOUT = 2
        while True:
            sleep(UPDATE_TIMEOUT)
            self.gridPrices_lock.acquire()
            self._replace_orders()
            if self.window and self.pS.get() != 0:
                values = self._guiValues()
                self.window.write_event_value('UPDATE-VALUES', values)
            self.gridPrices_lock.release()

            if self.config.upper_sl > 0:
                if self.pS.get() > self.config.upper_sl:
                    self.cancel()
                    self.OM.limitBuy(self.config.base_volume_line * self.config.line_count,
                                     self.config.upper_sl)

    def _replace_orders(self):
        for price in self.gridPrices:
            if price == self.pendingLine:
                continue
            id = self.gridOrders[price]
            if self.OM.get_status(id) == 'filled':

                if self.pendingLine != 0.0:
                    self._place_gridLine(self.pendingLine)
                self.pendingLine = price

    def _place_gridLine(self, linePrice):
        side = 'buy' if linePrice < self.pS.get() else 'sell'
        volume = self.config.base_volume_line
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
        return [round(price, self.config.tick_size) for price in prices]

    def _guiValues(self):
        buy_count, sell_count = 0, 0
        base_volume, quote_volume = 0.0, 0.0
        current_price = self.pS.get()
        prices = self._calculate_prices(self.config.upper_bound,
                                        self.config.lower_bound,
                                        self.config.line_count)
        for price in prices:
            if price == self.pendingLine:
                continue

            side = 'buy' if price < current_price else 'sell'
            volume = self.config.base_volume_line
            if side == 'buy':
                buy_count += 1
                quote_volume += volume * price
            else:
                sell_count += 1
                base_volume += volume

        quote_volume = round(quote_volume, 2)
        return {'buy_count':buy_count,
                'sell_count':sell_count,
                'base_volume':base_volume,
                'quote_volume':quote_volume,}