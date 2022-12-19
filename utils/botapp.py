from lightbulb import BotApp

class BotApp(BotApp):
    def __init__(self, config, debug, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self._debug = debug

    def add_plugin(self, plugin, *args, **kwargs):
        plugin._config = self._config
        plugin._debug = self._debug
        super().add_plugin(plugin, *args, **kwargs)
