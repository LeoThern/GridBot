from layouts import tabgroup
from Trader import Trader

import configparser as cp
import PySimpleGUI as sg
import datetime as dt
import threading
import traceback
import asyncio
import sys


def main():
    sg.theme('DarkGreen6')
    window = sg.Window(title='Binance Strategy', layout=tabgroup, finalize=True)
    config = cp.ConfigParser()
    config.read('config.ini')
    draw_settings(config, window)
    automatic_trades = True
    trader = Trader(config, window, automatic_trades)

    lock = threading.Lock()
    update_thread = threading.Thread(target=asyncio.run, args=(trader.async_price_update(lock),))
    update_thread.daemon = True
    update_thread.start()

    while True:
        event, values = window.read(timeout=20)

        if event == sg.WINDOW_CLOSED:
            sys.exit()

        if event == 'Buy Position':
            if not trader.limitOrder.status == 'open' and trader.mode == 'waiting':
                lock.acquire()
                trader.limit_buy()
                update_values(trader, window)
                lock.release()

        if event == 'Sell Position':
            if not trader.limitOrder.status == 'open' and trader.mode == 'holding':
                lock.acquire()
                trader.limit_sell()
                update_values(trader, window)
                lock.release()

        if event == 'Save':
            if trader.automaticTrades:
                sg.popup('Please turn off automatic trades to change settings!')
            if trader.mode == 'holding':
                sg.popup('Please sell your active position to change settings!')
            else:
                lock.acquire()
                save_settings(config, values)
                lock.release()
                if config['Profile1']['symbol'] != window['symbol'].DisplayText:
                    sg.popup('Please restart to change symbol!')
                draw_settings(config, window)

        if event == 'automatic_trades':
            automatic_trades = not automatic_trades
            trader.automaticTrades = automatic_trades
            window['automatic_trades'].update(('Off','On')[automatic_trades], button_color=(('white', ('red', 'green')[automatic_trades])))

        if event == 'UPDATE-VALUES':
            lock.acquire()
            update_values(trader, window)
            trader.check_trade_conditions()
            lock.release()

        if event == 'BINANCE-ERROR':
            sg.popup('- Error with Binance API -', values['BINANCE-ERROR'])
            window.close()
            sys.exit()

        if not update_thread.is_alive():
            window.close()
            sys.exit()


def save_settings(config, values):
    config['Profile1']['symbol'] = values['symbol_settings']
    config['Profile1']['threshold-buy'] = values['threshold-buy']
    config['Profile1']['threshold-sell'] = values['threshold-sell']
    config['Profile1']['min-profit'] = values['min-profit']
    config['Profile1']['short-sl-diff'] = values['short-sl-diff']
    config['Profile1']['long-sl-diff'] = values['long-sl-diff']
    config['Profile1']['volume'] = values['volume']
    with open('config.ini', 'w') as file:
        config.write(file)


def draw_settings(config, window):
    window['symbol'].update(config['Profile1']['symbol'])
    window['symbol_settings'].update(config['Profile1']['symbol'])
    window['threshold-buy'].update(config['Profile1']['threshold-buy'])
    window['threshold-sell'].update(config['Profile1']['threshold-sell'])
    window['short-sl-diff'].update(config['Profile1']['short-sl-diff'])
    window['long-sl-diff'].update(config['Profile1']['long-sl-diff'])
    window['min-profit'].update(config['Profile1']['min-profit'])
    window['min_profit'].update(config['Profile1']['min-profit'])
    window['volume'].update(config['Profile1']['volume'])


def update_values(trader, window):
    price = trader.price
    position = trader.position
    mode = trader.mode

    window['current_price'].update(price['current'])
    window['high'].update(price['high'])
    window['low'].update(price['low'])
    window['position_entry'].update(position['entry_price'])
    window['position_volume'].update(position['base_volume'])
    pl = float(position['base_volume']) * float(price['current']) - float(position['base_volume']) * float(
        position['entry_price'])
    window['position_pl'].update(f"{'+' if pl >= 0 else ''}{round(pl, 2)}")
    window['mode'].update(mode)

    if trader.limitOrder:
        window['order_status'].update(trader.limitOrder.status)
    else:
        window['order_status'].update('NO ORDER')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        current_time = dt.datetime.now().strftime("_%H_%M")
        with open(f"log{current_time}", 'w') as f:
            f.write(traceback.format_exc())
        sys.exit()
