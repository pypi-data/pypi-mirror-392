import requests
from pydantic import BaseModel, HttpUrl

from elite_relay.plugins.base import BasePlugin

__all__ = ['HttpPlugin']


class HttpOptions(BaseModel):
    url: HttpUrl
    headers: dict[str, str] = {}
    query: dict[str, str] = {}


class HttpPlugin(BasePlugin):
    def post(self):
        options = HttpOptions.model_validate(self.config.options)
        requests.post(
            url=options.url.encoded_string(),
            json=self.entry.model_dump(mode='json'),
            headers=options.headers,
            params=options.query,
        ).raise_for_status()
