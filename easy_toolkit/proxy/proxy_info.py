from dataclasses import dataclass


@dataclass
class ProxyInfo:
    username: str
    password: str
    ip: str
    port: str
