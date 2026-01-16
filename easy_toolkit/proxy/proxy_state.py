import time
from dataclasses import dataclass

from .proxy_info import ProxyInfo


@dataclass
class ProxyState:
    proxy: ProxyInfo
    score: int = 100
    success: int = 0
    failure: int = 0
    cooldown_until: float = 0.0

    def available(self) -> bool:
        return self.score > 0 and time.time() >= self.cooldown_until

    def http_proxy(self) -> str:
        if self.proxy.username and self.proxy.password:
            return f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.ip}:{self.proxy.port}"
        else:
            return f"http://{self.proxy.ip}:{self.proxy.port}"

    def socks5_proxy(self) -> str:
        if self.proxy.username and self.proxy.password:
            return f"socks5://{self.proxy.username}:{self.proxy.password}@{self.proxy.ip}:{self.proxy.port}"
        else:
            return f"socks5://{self.proxy.ip}:{self.proxy.port}"

    def playwright_http_proxy(self) -> dict:
        return {
            "server": f"http://{self.proxy.ip}:{self.proxy.port}",
            "username": self.proxy.username if self.proxy.username else None,
            "password": self.proxy.password if self.proxy.password else None
        }

    def playwright_socks5_proxy(self) -> dict:
        return {
            "server": f"socks5://{self.proxy.ip}:{self.proxy.port}",
            "username": self.proxy.username if self.proxy.username else None,
            "password": self.proxy.password if self.proxy.password else None
        }
