import asyncio
from pathlib import Path
from typing import Optional, Callable, Any
import sys


class AioFlameProfiler:
    """Integration with aioflame for async flamegraph generation."""

    def __init__(self, output_dir: str = "./perf_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def profile_async(
        self,
        coro_func: Callable,
        *args,
        output_name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Profile an async function and generate flamegraph.

        Args:
            coro_func: Async function to profile
            *args: Positional arguments for the function
            output_name: Custom output filename
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the async function
        """
        try:
            import aioflame
        except ImportError:
            raise ImportError("aioflame is not installed. Install with: pip install aioflame")

        if output_name is None:
            output_name = f"aioflame_{coro_func.__name__}.svg"

        output_file = self.output_dir / output_name

        profiler = aioflame.Profile()
        profiler.start()

        try:
            result = await coro_func(*args, **kwargs)
        finally:
            profiler.stop()
            stats = profiler.stats()

            with open(output_file, 'w') as f:
                f.write(stats.render_svg())

        return result

    def profile_async_context(self, output_name: Optional[str] = None):
        """
        Context manager for profiling async code blocks.

        Usage:
            async with profiler.profile_async_context("my_profile.svg"):
                await some_async_operation()
        """
        try:
            import aioflame
        except ImportError:
            raise ImportError("aioflame is not installed. Install with: pip install aioflame")

        if output_name is None:
            output_name = "aioflame_context.svg"

        output_file = self.output_dir / output_name

        class ProfileContext:
            def __init__(self, output_path):
                self.output_path = output_path
                self.profiler = aioflame.Profile()

            async def __aenter__(self):
                self.profiler.start()
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.profiler.stop()
                stats = self.profiler.stats()

                with open(self.output_path, 'w') as f:
                    f.write(stats.render_svg())

        return ProfileContext(output_file)
