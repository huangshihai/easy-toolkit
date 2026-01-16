"""
语义正确的 retry 工具：
- retries = 失败后的额外重试次数
- 第一次执行不算 retry
- retry 时打印第几次重试
"""

import asyncio
import time
import logging
from typing import Callable, Type, Tuple

logger = logging.getLogger()


# ============================================================================
# 公共工具
# ============================================================================

def _should_retry(exc: Exception, retry_on: Tuple[Type[Exception], ...]) -> bool:
    return isinstance(exc, retry_on)


def _calc_delay(
    retry_index: int,
    base_delay: float,
    backoff: float,
    max_delay: float | None,
) -> float:
    """
    retry_index 从 1 开始
    """
    delay = base_delay * (backoff ** (retry_index - 1))
    if max_delay is not None:
        delay = min(delay, max_delay)
    return delay


# ============================================================================
# 同步 retry
# ============================================================================

def retry(
    *,
    retries: int = 3,
    base_delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float | None = None,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None,
):
    """
    同步 retry 装饰器

    retries:
        失败后重试次数（不包含第一次正常执行）
    on_retry(exc, retry_index):
        retry_index 从 1 开始
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 第一次正常执行
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                if not _should_retry(exc, retry_on) or retries <= 0:
                    raise

                last_exc = exc

            # 进入 retry 阶段
            for retry_index in range(1, retries + 1):
                if on_retry:
                    on_retry(last_exc, retry_index)

                delay = _calc_delay(retry_index, base_delay, backoff, max_delay)
                logger.info(f"[同步重试] 方法 {func.__name__} 第 {retry_index}/{retries} 次将在 {delay:.2f}s 后重试，异常信息 {last_exc}")
                time.sleep(delay)

                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if not _should_retry(exc, retry_on):
                        raise
                    last_exc = exc

            raise last_exc

        return wrapper

    return decorator


# ============================================================================
# 异步 retry
# ============================================================================

def async_retry(
    *,
    retries: int = 3,
    base_delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float | None = None,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None,
):
    """
    异步 retry 装饰器（async def）

    retry_index 从 1 开始
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 第一次正常执行
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                if not _should_retry(exc, retry_on) or retries <= 0:
                    raise
                last_exc = exc

            # retry 阶段
            for retry_index in range(1, retries + 1):
                if on_retry:
                    on_retry(last_exc, retry_index)

                delay = _calc_delay(retry_index, base_delay, backoff, max_delay)
                logger.info(f"[异步重试] 方法 {func.__name__} 第 {retry_index}/{retries} 次将在 {delay:.2f}s 后重试，异常信息 {last_exc}")
                await asyncio.sleep(delay)

                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    if not _should_retry(exc, retry_on):
                        raise
                    last_exc = exc

            raise last_exc

        return wrapper

    return decorator
