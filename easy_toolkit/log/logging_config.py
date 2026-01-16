import logging
from logging.handlers import RotatingFileHandler
import os

def init_logging(log_dir="logs", log_file="app.log"):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    fmt = "%(asctime)s - %(trace_id)s - %(levelname)s - %(message)s"
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # 控制台 Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # 文件 Handler（滚动）
    fh = RotatingFileHandler(
        filename=log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    fh.setFormatter(formatter)
    root.addHandler(fh)
