import json
import logging
import logging.config
import os
from collections.abc import Callable
from contextlib import contextmanager
from logging import Logger
from threading import local

from pydantic import BaseModel

from kong.common.json import JsonEncoder

_thread_local = local()


class LogConfig(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = False

    formatters: dict = {
        "default": {
            "format": '%(asctime)s,%(msecs)d | %(levelname)-5s | %(message)s process="%(processName)s" thread="%(threadName)s" module="%(filename)s:%(lineno)d"',  # noqa: E501
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }

    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }

    root: dict = {
        "handlers": ["default"],
        "level": os.environ.get("CP_LOG_LEVEL", "INFO"),
    }


def _get_thread_local_mdc():
    if not hasattr(_thread_local, "mdc"):
        _thread_local.mdc = {}
    return _thread_local.mdc


def _mdc_context(pairs):
    mdc = _get_thread_local_mdc()
    old_values = {k: mdc.get(k) for k in pairs}
    mdc.update(pairs)
    try:
        yield
    finally:
        for k, v in old_values.items():
            if v is None:
                mdc.pop(k, None)
            else:
                mdc[k] = v


class AppLogger:
    def __init__(self, logger: Logger):
        self.logger = logger

    @property
    def is_debug_enabled(self):
        return self.logger.isEnabledFor(logging.DEBUG)

    def shorten(self, msg: any, max_len: int = 140) -> str:
        if not isinstance(msg, str):
            try:
                msg = json.dumps(msg, cls=JsonEncoder)
            except Exception:
                msg = str(msg)

        if self.is_debug_enabled:
            return msg
        return msg[:max_len]

    @contextmanager
    def context(self, **pairs):
        return _mdc_context(pairs)

    def debug(self, msg, get_pairs=None):
        if self.is_debug_enabled:
            with self.context(**(get_pairs() if get_pairs else {})):
                self.logger.debug(self.format_message(msg, _get_thread_local_mdc()))
        else:
            self.logger.debug(msg)

    def info(self, msg, get_pairs=None):
        with self.context(**(get_pairs() if get_pairs else {})):
            self.logger.info(self.format_message(msg, _get_thread_local_mdc()))

    def warning(self, msg, get_pairs=None, error=None):
        with self.context(**(get_pairs() if get_pairs else {})):
            self.logger.warning(
                self.format_message(msg, _get_thread_local_mdc()), exc_info=error
            )

    def error(self, msg, get_pairs=None, error=None):
        with self.context(**(get_pairs() if get_pairs else {})):
            self.logger.error(
                self.format_message(msg, _get_thread_local_mdc()), exc_info=error
            )

    def exception(self, msg, *args, get_pairs=None, **kwargs):
        with self.context(**(get_pairs() if get_pairs else {})):
            self.logger.exception(
                self.format_message(msg, _get_thread_local_mdc()),
                *args,
                exc_info=True,
                **kwargs,
            )

    def format_message(self, msg, pairs):
        body = self.format_string(msg)
        context = " ".join(
            f"{self.format_string(k)}={self.format_string(v)}" for k, v in pairs.items()
        )
        return f"msg={body} {context}"

    @staticmethod
    def format_string(value):
        if value is None:
            return value
        text = str(value)
        need_quotes = False
        escaped = []
        for c in text:
            if c in ["\r", "\n", '"']:
                escaped.append({"\r": "", "\n": "\\n", '"': '\\"'}[c])
                need_quotes = True
            else:
                escaped.append(c)
                if not need_quotes:
                    need_quotes = c in [" ", "\t", "="]
        result = "".join(escaped)
        return f'"{result}"' if need_quotes else result


def __logger_factory() -> Callable[[str], AppLogger]:
    configured = False

    def init_logger(name: str) -> AppLogger:
        nonlocal configured

        if not configured:
            configured = True
            logging.config.dictConfig(LogConfig().model_dump())

        return AppLogger(logging.getLogger(name))

    return init_logger


app_logger = __logger_factory()
