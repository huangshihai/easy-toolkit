import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..log.async_logging_context import trace_id_var


class ParallelProcessor:
    def __init__(self, max_workers=5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def submit(self, func, *args, **kwargs):
        trace_id = uuid.uuid4().hex
        logger = logging.getLogger()

        def wrapper():
            token = trace_id_var.set(trace_id)
            try:
                logger.info(f"任务开始：{func.__name__} args={args} kwargs={kwargs}")
                result = func(*args, **kwargs)
                logger.info(f"任务完成：{func.__name__} 返回值={result}")
                return result
            finally:
                trace_id_var.reset(token)

        self.futures.append(self.executor.submit(wrapper))

    def run(self):
        results = []
        for f in as_completed(self.futures):
            results.append(f.result())
        self.executor.shutdown(wait=True)
        return results
