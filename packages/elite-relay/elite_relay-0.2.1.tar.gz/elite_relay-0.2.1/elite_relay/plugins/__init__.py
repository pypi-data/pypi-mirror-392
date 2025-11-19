from elite_relay.plugins.registry import PluginRegistry

from .browser import BrowserPlugin
from .clipboard import ClipboardPlugin
from .http import HttpPlugin
from .pushover import PushoverPlugin

registry = PluginRegistry()


# Register plugins below

registry.register('http', HttpPlugin)
registry.register('browser', BrowserPlugin)
registry.register('clipboard', ClipboardPlugin)
registry.register('pushover', PushoverPlugin)
