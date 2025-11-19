"""PerfSentinel - Performance testing and monitoring system."""

__version__ = "0.1.2"

from perf_sentinel.decorators import perf_timing
from perf_sentinel.reporter import PySpyProfiler, AioFlameProfiler, PerformanceReport
from perf_sentinel.audit import PerformanceScheduler, TrendAnalyzer

__all__ = [
    'perf_timing',
    'PySpyProfiler',
    'AioFlameProfiler',
    'PerformanceReport',
    'PerformanceScheduler',
    'TrendAnalyzer',
]
