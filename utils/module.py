from lightbulb import Plugin

from .config import Config

class Module(Plugin):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self._config_ = Config

    @property
    def _config(self):
        return self._config_
    
    @_config.setter
    def _config(self, config):
        self._config_ = config
