from enum import Enum
import threading
from pathlib import Path
from datetime import datetime
import sys

LOG_DIR = "./logs"


class LogLevel(Enum):
    """log level"""
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'


class SimpleLogger:
    """logger"""
    _locks = {}
    _biz_type: str = "default"

    def __init__(self, biz_type: str, log_dir: Path = Path(LOG_DIR)):
        self._biz_type = biz_type
        log_dir.mkdir(exist_ok=True)
        file_name = f"{datetime.now().strftime('%Y%m%d_%H')}.log"
        self.file_path = log_dir / file_name
        self.lock = self._locks.setdefault(biz_type, threading.Lock())
        # with self.lock:
        # with self.file_path.open('a', encoding='utf-8') as f:
        # f.write(f"# {biz_type} write new log: {datetime.now()}\n")

    def log(self, level: LogLevel, message: str):
        now = datetime.now()
        ms = now.microsecond // 1000
        line = line = (f"{now.strftime('%Y-%m-%d %H:%M:%S')}.{ms:03d} | {level.name:>4} | "
                       f"{threading.current_thread().name:<12} | {self._biz_type} {message}\n")

        # 控制台（无颜色）
        sys.stdout.write(line)
        sys.stdout.flush()

        # append log to log file
        with self.lock:
            with self.file_path.open('a', encoding='utf-8') as f:
                f.write(line)

    def info(self, message: str):
        self.log(LogLevel.INFO, message)

    def warn(self, message: str):
        self.log(LogLevel.WARN, message)

    def error(self, message: str):
        self.log(LogLevel.ERROR, message)

    def debug(self, message: str):
        self.log(LogLevel.DEBUG, message)


_loggers: dict[str, SimpleLogger] = {}


def get_logger(biz_type: str) -> SimpleLogger:
    if biz_type not in _loggers:
        _loggers[biz_type] = SimpleLogger(biz_type)
    return _loggers[biz_type]


# log = _get_logger("default")
