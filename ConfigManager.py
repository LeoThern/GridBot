import configparser

class ConfigManager:
    def __init__(self, filename):
        self.filename = filename
        self.profile = 'Profile1'
        self.cp = configparser.ConfigParser()
        self.cp.read(self.filename)
        self._create_member_access()
        self.symbol_changed = False
        self.file_to_gui_fields = {'symbol':['s_symbol', 'symbol'],
                                   'tick_size':['s_tick_size',],
                                   'upper_bound':['s_upper_bound', 'upper_bound'],
                                   'lower_bound':['s_lower_bound', 'lower_bound'],
                                   'line_count':['s_line_count',],
                                   'base_volume_line':['s_base_volume_line',],
                                   'upper_sl': ['s_upper_sl',],
                                   }

    def _create_member_access(self):
        self.symbol = self.cp[self.profile]['symbol']
        self.upper_bound = float(self.cp[self.profile]['upper_bound'])
        self.lower_bound = float(self.cp[self.profile]['lower_bound'])
        self.line_count = int(self.cp[self.profile]['line_count'])
        self.base_volume_line = float(self.cp[self.profile]['base_volume_line'])
        self.tick_size = min(8, abs(int(self.cp[self.profile]['tick_size'])))
        self.upper_sl = float(self.cp[self.profile]['upper_sl'])

    def draw_to_window(self, window):
        for file_key, gui_keys in self.file_to_gui_fields.items():
            for gui_key in gui_keys:
                window[gui_key].update(self.cp[self.profile][file_key])

    def save(self, values):
        if self.symbol == values['s_symbol']:
            self.symbol_changed = False
        else:
            self.symbol_changed = True

        for file_key, gui_keys in self.file_to_gui_fields.items():
            self.cp[self.profile][file_key] = values[gui_keys[0]]

        with open(self.filename, 'w') as file:
            self.cp.write(file)
        self._create_member_access()