import typing as t

from elite_relay.plugins.base import BasePlugin


class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, t.Type[BasePlugin]] = {}

    def register(self, alias: str, plugin: t.Type[BasePlugin]):
        self._plugins[alias] = plugin

    def get(self, alias: str) -> t.Type[BasePlugin] | None:
        return self._plugins.get(alias)
