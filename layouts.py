import PySimpleGUI as sg

layoutMainTab = [[sg.Push(), sg.Text('Asset:'), sg.Text('', key='symbol'), sg.Push()],
                 [sg.Push(),
                  sg.Frame('Price', [[sg.Text('Current Price:'), sg.Push(), sg.Text('Loading..', key='current_price')],
                                     [sg.Text('Recent High:'), sg.Push(), sg.Text('Loading..', key='high')],
                                     [sg.Text('Recent Low:'), sg.Push(), sg.Text('Loading..', key='low')]]), sg.Push()],
                 [sg.Push()],
                 [sg.Push(), sg.Text('Mode:'), sg.Text('', key='mode'), sg.Push()],
                 [sg.Push(), sg.Frame('Position', [[sg.Text('Entry:'), sg.Push(), sg.Text('', key='position_entry')],
                                                   [sg.Text('Volume:'), sg.Push(), sg.Text('', key='position_volume')],
                                                   [sg.Text('Profit/Loss:'), sg.Push(), sg.Text('', key='position_pl')],
                                                   [sg.Text('Minimum Profit:'), sg.Push(),
                                                    sg.Text('', key='min_profit')], ]), sg.Push()],
                 [sg.Push(), sg.Text('Automatic Trades:'), sg.Button('On', button_color=('white', 'green'), key='automatic_trades'), sg.Push()],
                 [sg.Push(), sg.Text('Order Status:'), sg.Text('', key='order_status'), sg.Push()],
                 [sg.Push(), sg.Button('Buy Position'), sg.Push()],
                 [sg.Push(), sg.Button('Sell Position'), sg.Push()], ]

layoutSettingsTab = [[sg.Text('Symbol: '), sg.Push(), sg.InputText(key='symbol_settings')],
                     [sg.Text('Position Volume: '), sg.Push(), sg.InputText(key='volume')],
                     [sg.Text('Threshold-Buy (diff.): '), sg.Push(), sg.InputText(key='threshold-buy')],
                     [sg.Text('Threshold-Sell (diff.): '), sg.Push(), sg.InputText(key='threshold-sell')],
                     [sg.Push()],
                     [sg.Push()],
                     [sg.Push(), sg.Frame('OPTIONAL', [
                        [sg.Text('Minimal Profit (diff.): '), sg.Push(), sg.InputText(key='min-profit')],
                        [sg.Text('Upper Stop Loss (diff.): '), sg.Push(), sg.InputText(key='long-sl-diff')],
                        [sg.Text('Lower Stop Loss (diff.): '), sg.Push(), sg.InputText(key='short-sl-diff')],
                     ], title_location='n'), sg.Push()],
                     [sg.Push(), sg.Button('Save'), sg.Push()], ]

tabgroup = [[sg.TabGroup([[sg.Tab('Main', layoutMainTab),
                           sg.Tab('Settings', layoutSettingsTab)]],
                         tab_location='centertop'), ]]


def load_demo_values(window):
    window['symbol'].update('APEBUSD')
    window['mode'].update('waiting')
    window['order_status'].update('filled')
    price, high, low, sl = 4.55, 4.96, 4.36, 3.0
    window['current_price'].update(price)
    window['high'].update(high)
    window['low'].update(low)
    window['min_profit'].update(0.10)
    window['position_entry'].update(4.21)
    window['position_volume'].update(2300)
    window['position_pl'].update('+0.33')


def main():
    sg.theme('DarkGreen6')

    window = sg.Window(title='Binance Strategy', layout=tabgroup, finalize=True)
    load_demo_values(window)
    automatic_trades = False

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == 'Buy Position':
            print('Buying Position...')
        if event == 'Sell Position':
            print('Selling Position...')
        if event == 'Save':
            print('Saving Settings...')
        if event == 'automatic_trades':
            automatic_trades = not automatic_trades
            window['automatic_trades'].update(('Off','On')[automatic_trades], button_color=(('white', ('red', 'green')[automatic_trades])))

    window.close()


if __name__ == "__main__":
    main()
