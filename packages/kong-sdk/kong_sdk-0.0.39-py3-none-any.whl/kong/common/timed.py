import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from prometheus_client import Histogram
from time import perf_counter

# preserving decorated function return type: https://github.com/python/mypy/issues/1927
_BaseDecoratedFunc = Callable[..., Any]
DecoratedFunc = TypeVar("DecoratedFunc", bound=_BaseDecoratedFunc)


# custom decorator since @time from prometheus_client.Histogram doesn't await
class Timed:
    __histograms = {}

    def __init__(
        self,
        value: str,
        extra_tags: list[str] = [],
        percentiles: tuple[float, ...] = Histogram.DEFAULT_BUCKETS,
    ):
        if not self.__histograms.get(value):
            label_names = extra_tags[::2]
            label_values = extra_tags[1::2]

            histogram = Histogram(
                name=value,
                documentation="method execution in seconds",
                unit="s",
                labelnames=label_names,
                buckets=percentiles,
            )
            histogram.labels(*label_values)
            self.__histograms[value] = (histogram, label_values)

        self.histogram = self.__histograms[value]

    def __call__(self, func) -> DecoratedFunc:
        @functools.wraps(func)
        def decorate(*args, **kwargs) -> Any:
            start_time = perf_counter()
            _result = func(*args, **kwargs)
            histogram, labels = self.histogram
            histogram.labels(*labels).observe(perf_counter() - start_time)
            return _result

        @functools.wraps(func)
        async def async_decorate(*args, **kwargs) -> Any:
            start_time = perf_counter()
            _result = await func(*args, **kwargs)
            histogram, labels = self.histogram
            histogram.labels(*labels).observe(perf_counter() - start_time)
            return _result

        return async_decorate if inspect.iscoroutinefunction(func) else decorate
