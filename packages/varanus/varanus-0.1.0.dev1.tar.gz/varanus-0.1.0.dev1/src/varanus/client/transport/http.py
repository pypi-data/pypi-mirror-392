import platform
from typing import Any
from urllib.parse import SplitResult

import httpx
import msgspec

from varanus import events

from .base import BaseTransport


class HttpTransport(BaseTransport):
    def __init__(self, url: SplitResult, environment: str):
        path = url.path.rstrip("/")
        self.ping_url = f"{url.scheme}://{url.netloc}{path}/api/ping/"
        self.event_url = f"{url.scheme}://{url.netloc}{path}/api/ingest/"
        self.client = httpx.Client(
            headers={
                "X-Varanus-Key": url.username or "",
                "X-Varanus-Environment": environment or "",
                "X-Varanus-Node": platform.node(),
            },
            timeout=1.0,
        )

    def request(self, url: str, obj: Any):
        try:
            self.client.post(url, content=msgspec.json.encode(obj))
        except Exception as ex:
            print(f"error sending to {url}: {ex}")

    def ping(self, info: events.NodeInfo):
        self.request(self.ping_url, info)

    def send(self, event: events.Context):
        self.request(self.event_url, event)
