import asyncio
import uuid
import logging

from playwright.async_api import async_playwright, Browser
from typing import Callable, Awaitable, Any, List
from ..log.async_logging_context import trace_id_var


class PlaywrightAsyncProcessor:
    def __init__(self, max_concurrency: int = 5, browser_type: str = "chromium", headless: bool = True, proxy_pool = None):
        self.max_concurrency = max_concurrency
        self.browser_type = browser_type
        self.headless = headless
        self.proxy_pool = proxy_pool

        self._tasks: List[Callable[[], Awaitable[Any]]] = []
        self._semaphore = asyncio.Semaphore(max_concurrency)

        self._playwright = None
        self._browser: Browser | None = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        browser_launcher = getattr(self._playwright, self.browser_type)
        launch_kwargs = {
            "headless": self.headless,
        }
        self._browser = await browser_launcher.launch(**launch_kwargs)
        return self

    async def __aexit__(self, *exc):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    def submit(self, task_func: Callable[..., Awaitable[Any]], *args, **kwargs):
        async def _runner():
            trace_id = uuid.uuid4().hex
            token = trace_id_var.set(trace_id)
            logger = logging.getLogger()
            proxy_state = self.proxy_pool.acquire()
            async with self._semaphore:
                proxy = proxy_state.playwright_http_proxy()
                context = await self._browser.new_context(
                    proxy=proxy if proxy else None
                )
                try:
                    logger.info(f"任务开始: {task_func.__name__}  args={args} kwargs={kwargs}")
                    result = await task_func(context, *args, **kwargs)
                    self.proxy_pool.report_success(proxy_state)
                    logger.info(f"任务完成: {task_func.__name__} 返回值={result}")
                    return result
                except Exception as e:
                    self.proxy_pool.report_failure(proxy_state)
                    logger.exception(f"任务异常: {task_func.__name__} 异常={e}")
                    raise
                finally:
                    await context.close()
                    trace_id_var.reset(token)

        self._tasks.append(_runner)

    async def run(self):
        results = []
        coros = [task() for task in self._tasks]

        for fut in asyncio.as_completed(coros):
            results.append(await fut)

        return results
