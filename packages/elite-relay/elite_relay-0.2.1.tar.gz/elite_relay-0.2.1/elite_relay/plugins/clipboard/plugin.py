import pyperclip
from pydantic import BaseModel

from elite_relay.plugins.base import BasePlugin


class ClipboardOptions(BaseModel):
    text: str
    strip: bool = True


class ClipboardPlugin(BasePlugin):
    def copy(self):
        options = ClipboardOptions.model_validate(self.config.options)
        value = self.format_string(options.text)
        if options.strip:
            value = value.strip()
        pyperclip.copy(value)
