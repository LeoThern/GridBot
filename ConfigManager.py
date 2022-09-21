import configparser

class ConfigManager:
    def __init__(self, filename):
        self.filename = filename
        self.cp = configparser.ConfigParser()
        self.cp.read(self.filename)
        self._create_member_access()
        self.symbol_changed = False
        #self.gui_settings_fields = {}

    def _create_member_access(self):
        self.symbol = self.cp['Profile1']['symbol']
        self.upper_bound = float(self.cp['Profile1']['upper_bound'])
        self.lower_bound = float(self.cp['Profile1']['lower_bound'])
        self.line_count = int(self.cp['Profile1']['line_count'])
        self.base_volume_line = float(self.cp['Profile1']['base_volume_line'])

    def draw_to_window(self, window):
        window['symbol'].update(self.cp['Profile1']['symbol'])
        window['upper_bound'].update(self.cp['Profile1']['upper_bound'])
        window['lower_bound'].update(self.cp['Profile1']['lower_bound'])
        window['s_symbol'].update(self.cp['Profile1']['symbol'])
        window['s_upper_bound'].update(self.cp['Profile1']['upper_bound'])
        window['s_lower_bound'].update(self.cp['Profile1']['lower_bound'])
        window['s_line_count'].update(self.cp['Profile1']['line_count'])
        window['s_base_volume_line'].update(self.cp['Profile1']['base_volume_line'])

    def save(self, values):
        if self.symbol == values['s_symbol']:
            self.symbol_changed = False
        else:
            self.symbol_changed = True
        self.cp['Profile1']['symbol'] = values['s_symbol']
        self.cp['Profile1']['upper_bound'] = values['s_upper_bound']
        self.cp['Profile1']['lower_bound'] = values['s_lower_bound']
        self.cp['Profile1']['line_count'] = values['s_line_count']
        self.cp['Profile1']['base_volume_line'] = values['s_base_volume_line']
        with open(self.filename, 'w') as file:
            self.cp.write(file)
        self._create_member_access()