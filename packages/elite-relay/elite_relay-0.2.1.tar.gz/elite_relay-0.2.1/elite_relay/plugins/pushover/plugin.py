import typing as t

import requests
from pydantic import BaseModel, HttpUrl, PositiveInt

from elite_relay.plugins.base import BasePlugin


class PushoverOptions(BaseModel):
    api_token: str
    user_key: str
    message: str
    title: str | None = None
    priority: int | None = None
    sound: str | None = None
    ttl: PositiveInt | None = None
    endpoint: HttpUrl = HttpUrl('https://api.pushover.net/1/messages.json')


class PushoverPlugin(BasePlugin):
    def notify(self):
        options = PushoverOptions.model_validate(self.config.options)
        payload: dict[str, t.Any] = {
            'token': options.api_token,
            'user': options.user_key,
            'message': self.format_string(options.message),
        }
        if options.title is not None:
            payload['title'] = self.format_string(options.title)
        if options.priority is not None:
            payload['priority'] = options.priority
        if options.sound is not None:
            payload['sound'] = options.sound
        if options.ttl is not None:
            payload['ttl'] = options.ttl
        requests.post(
            url=options.endpoint.encoded_string(),
            data=payload,
        ).raise_for_status()
