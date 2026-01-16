import os
import random
import threading
import time

from .proxy_info import ProxyInfo
from .proxy_state import ProxyState


class ProxyPool:
    def __init__(self, proxy_dir: str, cooldown=60):
        self._lock = threading.Lock()
        self.proxy_dir = proxy_dir
        self.cooldown = cooldown
        self._proxies = [ProxyState(p) for p in self.init_proxies()]

    def init_proxies(self):
        result_list = []
        for filename in os.listdir(self.proxy_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.proxy_dir, filename)
                # 打开并读取文件
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        # 去除空行和首尾空白符
                        line = line.strip()
                        if not line:
                            continue  # 跳过空行
                        # 按 ":" 切分行
                        parts = line.split(":")
                        # 如果不是4个部分则跳过，确保每行有四个元素
                        if len(parts) != 4:
                            continue
                        # 构建字典对象
                        proxy_info = ProxyInfo(parts[0].strip(), str(parts[1].strip()), str(parts[2].strip()),
                                               str(parts[3].strip()))
                        # 将字典对象放入列表中
                        result_list.append(proxy_info)
        return result_list

    def acquire(self) -> ProxyState | None:
        with self._lock:
            candidates = [p for p in self._proxies if p.available()]
            return random.choice(candidates) if candidates else None

    def report_success(self, proxy: ProxyState | None):
        if not proxy:
            return
        with self._lock:
            proxy.success += 1
            proxy.score = min(proxy.score + 1, 100)

    def report_failure(self, proxy: ProxyState | None):
        if not proxy:
            return
        with self._lock:
            proxy.failure += 1
            proxy.score -= 10
            proxy.cooldown_until = time.time() + self.cooldown
