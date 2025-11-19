import time
import asyncio
import inspect
import functools
from typing import Any, Callable, Optional
from perf_sentinel.utils.json_logger import log_performance
from perf_sentinel.decorators.async_utils import detect_sync_blocking


def perf_timing(func: Optional[Callable] = None, *, name: Optional[str] = None, threshold_ms: Optional[float] = None):
    """
    Performance timing decorator for both sync and async functions.

    Features:
    - Records execution time
    - Detects yield/async yield usage
    - Detects blocking operations in async functions
    - Outputs structured JSON logs

    Args:
        func: Function to decorate
        name: Custom name for the operation
        threshold_ms: Log warning if execution exceeds this threshold
    """
    def decorator(f: Callable) -> Callable:
        operation_name = name or f.__qualname__

        if inspect.isasyncgenfunction(f):
            @functools.wraps(f)
            async def async_gen_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                has_yielded = False

                try:
                    async for item in f(*args, **kwargs):
                        has_yielded = True
                        yield item
                finally:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000

                    log_performance({
                        "operation": operation_name,
                        "type": "async_generator",
                        "elapsed_ms": round(elapsed_ms, 2),
                        "has_yield": has_yielded,
                        "threshold_exceeded": threshold_ms is not None and elapsed_ms > threshold_ms
                    })

            return async_gen_wrapper

        elif asyncio.iscoroutinefunction(f):
            has_blocking = detect_sync_blocking(f)

            @functools.wraps(f)
            async def async_wrapper(*args, **kwargs):
                start_time = time.perf_counter()

                try:
                    result = await f(*args, **kwargs)
                    return result
                finally:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000

                    log_performance({
                        "operation": operation_name,
                        "type": "async_function",
                        "elapsed_ms": round(elapsed_ms, 2),
                        "has_sync_blocking": has_blocking,
                        "threshold_exceeded": threshold_ms is not None and elapsed_ms > threshold_ms
                    })

            return async_wrapper

        elif inspect.isgeneratorfunction(f):
            @functools.wraps(f)
            def gen_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                has_yielded = False

                try:
                    for item in f(*args, **kwargs):
                        has_yielded = True
                        yield item
                finally:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000

                    log_performance({
                        "operation": operation_name,
                        "type": "generator",
                        "elapsed_ms": round(elapsed_ms, 2),
                        "has_yield": has_yielded,
                        "threshold_exceeded": threshold_ms is not None and elapsed_ms > threshold_ms
                    })

            return gen_wrapper

        else:
            @functools.wraps(f)
            def sync_wrapper(*args, **kwargs):
                start_time = time.perf_counter()

                try:
                    result = f(*args, **kwargs)
                    return result
                finally:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000

                    log_performance({
                        "operation": operation_name,
                        "type": "sync_function",
                        "elapsed_ms": round(elapsed_ms, 2),
                        "threshold_exceeded": threshold_ms is not None and elapsed_ms > threshold_ms
                    })

            return sync_wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)
