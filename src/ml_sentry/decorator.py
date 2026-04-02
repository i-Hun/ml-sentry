import inspect
import os
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import psutil

from .formatters import smart_format_args
from .logging_utils import log_metrics
from .memory import PyMemoryTracker
from .rss_sampler import RssPeakSampler

P = ParamSpec("P")
R = TypeVar("R")


def track(
    *,
    use_tracemalloc: bool = False,
    rss_interval: float = 0.01,
    log_args: bool = False,
    max_arg_length: int = 200,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Main profiling decorator."""

    process = psutil.Process(os.getpid())

    def decorator(func: Callable[P, R]) -> Callable[P, R]:

        def _run_sync(*args: P.args, **kwargs: P.kwargs) -> R:
            sampler = RssPeakSampler(process, rss_interval)
            sampler.start()

            py_tracker = PyMemoryTracker(use_tracemalloc)
            py_tracker.start()

            args_str = (
                smart_format_args(func, args, kwargs, max_length=max_arg_length)
                if log_args
                else None
            )

            start_time = time.perf_counter()
            start_rss = process.memory_info().rss

            try:
                return func(*args, **kwargs)
            finally:
                peak_rss = sampler.stop()
                peak_py = py_tracker.stop()

                log_metrics(
                    func.__name__,
                    start_time,
                    start_rss,
                    peak_rss,
                    py_tracker.start_mem,
                    peak_py,
                    args_str,
                )

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrap(*args: P.args, **kwargs: P.kwargs) -> R:
                sampler = RssPeakSampler(process, rss_interval)
                sampler.start()

                py_tracker = PyMemoryTracker(use_tracemalloc)
                py_tracker.start()

                args_str = (
                    smart_format_args(func, args, kwargs, max_length=max_arg_length)
                    if log_args
                    else None
                )

                start_time = time.perf_counter()
                start_rss = process.memory_info().rss

                try:
                    return await func(*args, **kwargs)
                finally:
                    peak_rss = sampler.stop()
                    peak_py = py_tracker.stop()

                    log_metrics(
                        func.__name__,
                        start_time,
                        start_rss,
                        peak_rss,
                        py_tracker.start_mem,
                        peak_py,
                        args_str,
                    )

            return async_wrap  # type: ignore

        return wraps(func)(_run_sync)

    return decorator
