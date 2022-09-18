from ConfigManager import ConfigManager
from PriceStream import PriceStream
from gui_layout import layout
from GridBot import GridBot

from binance.exceptions import BinanceAPIException
import PySimpleGUI as sg
import datetime
import traceback
import sys


def main():
    sg.theme('DarkGreen6')
    window = sg.Window(title='Binance GridBot', layout=layout, finalize=True)
    config = ConfigManager('config.ini')
    config.draw_to_window(window)
    Price = PriceStream(config.symbol)
    Price.subscribe_window(window)
    Bot = GridBot(config, Price)
    Bot.subscribe_window(window)

    move_grid = False

    while True:
        event, values = window.read(timeout=20)

        if event == sg.WINDOW_CLOSED:
            sys.exit()

        if event == 'Place':
            if not Bot.isActive():
                Bot.place()

        if event == 'Cancel':
            if Bot.isActive():
                Bot.cancel()
        if event == 'Save':
            config.save(values)
            config.draw_to_window(window)
            if Bot.isActive():
                Bot.cancel()
                Bot = GridBot(config, Price)

        if event == 'move_grid':
            pass

        if event == 'UPDATE-VALUES':
            new_values = values['UPDATE-VALUES']
            for key in new_values:
                window[key].update(new_values[key])

        if event == 'PRICE-STREAM':
            window['price'].update(values['PRICE-STREAM'])


if __name__ == '__main__':
    try:
        main()
    except BinanceAPIException as e:
        sg.popup('- Error with Binance API -', e)
    except Exception:
        current_time = datetime.datetime.now().strftime("_%H_%M")
        with open(f"log{current_time}", 'w') as f:
            f.write(traceback.format_exc())
        sys.exit()
