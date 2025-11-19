import typing as t
import webbrowser

from pydantic import BaseModel, HttpUrl, computed_field

from elite_relay.plugins.base import BasePlugin

__all__ = ['BrowserPlugin']

OpenMethod = t.Literal['default', 'window', 'tab']
_open_method_map: dict[OpenMethod, int] = {
    'default': 0,
    'window': 1,
    'tab': 2,
}


class BrowserOptions(BaseModel):
    url: HttpUrl
    focus: bool = False
    open_method: OpenMethod = 'default'

    @computed_field
    @property
    def open_method_code(self) -> int:
        return _open_method_map[self.open_method]


class BrowserPlugin(BasePlugin):
    def open(self):
        options = BrowserOptions.model_validate(self.config.options)
        webbrowser.open(
            url=self.format_string(options.url),
            new=options.open_method_code,
            autoraise=options.focus,
        )
