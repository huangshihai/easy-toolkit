import requests


class HttpClient:
    def __init__(self, proxy_pool, timeout=10):
        self.proxy_pool = proxy_pool
        self.timeout = timeout

    def _to_requests_proxy(self, proxy: str):
        return {"http": proxy, "https": proxy}

    def request(self, method, url, **kwargs):
        proxy_state = self.proxy_pool.acquire()
        proxies = self._to_requests_proxy(proxy_state.http_proxy()) if proxy_state else None

        try:
            resp = requests.request(
                method,
                url,
                proxies=proxies,
                timeout=self.timeout,
                **kwargs,
            )
            resp.raise_for_status()
            self.proxy_pool.report_success(proxy_state)
            return resp
        except Exception:
            self.proxy_pool.report_failure(proxy_state)
            raise

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)
