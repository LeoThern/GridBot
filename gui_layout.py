import PySimpleGUI as sg

layoutMainTab = [[sg.Push(), sg.Text('Asset:'), sg.Text('', key='symbol'), sg.Push()],
                 [sg.Push(), sg.Text('BaseVolume:'), sg.Text('', key='base_volume'), sg.Push()],
                 [sg.Push(), sg.Text('QuoteVolume:'), sg.Text('', key='quote_volume'), sg.Push()],
                 [sg.Push(), sg.Frame('Grid', [[sg.Text('Upper Bound:'), sg.Push(), sg.Text('', key='upper_bound')],
                                                   [sg.Text('Sell\'s above:'), sg.Push(), sg.Text('', key='sell_count')],
                                                   [sg.Text('Price:'), sg.Push(), sg.Text('', key='price')],
                                                   [sg.Text('Buys\'s below:'), sg.Push(), sg.Text('', key='buy_count')],
                                                   [sg.Text('Lower Bound:'), sg.Push(), sg.Text('', key='lower_bound')],], title_location='n'), sg.Push()],
                 [sg.Push(), sg.Button('Place'), sg.Push()],
                 [sg.Push(), sg.Button('Cancel'), sg.Push()],
                 [sg.Push(), sg.Text('Move Grid:'), sg.Button('Off', button_color=('white', 'red'), key='move_grid'), sg.Push()],]

layoutSettingsTab = [[sg.Text('Symbol: '), sg.Push(), sg.InputText(key='s_symbol')],
                     [sg.Text('Nachkommastellen: '), sg.Push(), sg.InputText(key='s_tick_size')],
                     [sg.Text('Upper Bound: '), sg.Push(), sg.InputText(key='s_upper_bound')],
                     [sg.Text('Lower Bound: '), sg.Push(), sg.InputText(key='s_lower_bound')],
                     [sg.Text('Line Count: '), sg.Push(), sg.InputText(key='s_line_count')],
                     [sg.Text('Coin\'s per Line: '), sg.Push(), sg.InputText(key='s_base_volume_line')],
                     [sg.Push(), sg.Button('Save'), sg.Push()], ]

layoutStatsTab = [[sg.Push(), sg.Text('Buy\'s executed:'), sg.Text('', key='total_buys'), sg.Push()],
                  [sg.Push(), sg.Text('Sell\'s executed:'), sg.Text('', key='total_sells'), sg.Push()],
                  [sg.Push(), sg.Text('Base P/L:'), sg.Text('', key='base_pl'), sg.Push()],
                  [sg.Push(), sg.Text('Quote P/L:'), sg.Text('', key='quote_pl'), sg.Push()],]

layout = [[sg.TabGroup([[sg.Tab('Main', layoutMainTab),
                         sg.Tab('Settings', layoutSettingsTab),
                         sg.Tab('Stats', layoutStatsTab)]],
                         tab_location='centertop'), ]]


def load_demo_values(window):
    window['symbol'].update('APEBUSD')
    window['base_volume'].update(44.7)
    window['quote_volume'].update(133.9)
    window['upper_bound'].update(23.0)
    window['sell_count'].update(3)
    window['price'].update(15.354)
    window['buy_count'].update(2)
    window['lower_bound'].update(10.4)


def main():
    sg.theme('DarkGreen6')

    window = sg.Window(title='Binance GridBot', layout=layout, finalize=True)
    load_demo_values(window)
    move_grid = False

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == 'Place':
            print('Placing Grid...')
        if event == 'Cancel':
            print('Canceling all Orders...')
        if event == 'Save':
            print('Saving Settings...')
        if event == 'move_grid':
            move_grid = not move_grid
            window['move_grid'].update(('Off','On')[move_grid], button_color=(('white', ('red', 'green')[move_grid])))
    window.close()


if __name__ == "__main__":
    main()
