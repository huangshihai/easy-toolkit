import contextvars
import logging

trace_id_var = contextvars.ContextVar("trace_id", default="N/A")

_orig_factory = logging.getLogRecordFactory()

def _record_factory(*args, **kwargs):
    record = _orig_factory(*args, **kwargs)
    record.trace_id = trace_id_var.get()
    return record

def init_async_logging_context():
    logging.setLogRecordFactory(_record_factory)
