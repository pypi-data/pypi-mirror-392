import schedule
import time
import subprocess
from datetime import datetime
from typing import Callable, Optional
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceScheduler:
    """Schedule periodic performance audits."""

    def __init__(self):
        self.jobs = []

    def add_daily_audit(
        self,
        test_script: str,
        time_str: str = "00:00",
        callback: Optional[Callable] = None
    ):
        """
        Schedule daily performance audit.

        Args:
            test_script: Path to performance test script
            time_str: Time in HH:MM format
            callback: Optional callback function
        """
        def job():
            logger.info(f"Running scheduled audit: {test_script}")
            try:
                result = subprocess.run(
                    ["perf-sentinel", "run", test_script, "--report-formats", "html", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info(f"Audit completed: {result.stdout}")

                if callback:
                    callback(result)

            except subprocess.CalledProcessError as e:
                logger.error(f"Audit failed: {e.stderr}")

        schedule.every().day.at(time_str).do(job)
        self.jobs.append(job)

    def add_weekly_audit(
        self,
        test_script: str,
        day: str = "monday",
        time_str: str = "00:00",
        callback: Optional[Callable] = None
    ):
        """
        Schedule weekly performance audit.

        Args:
            test_script: Path to performance test script
            day: Day of week (monday, tuesday, etc.)
            time_str: Time in HH:MM format
            callback: Optional callback function
        """
        def job():
            logger.info(f"Running scheduled weekly audit: {test_script}")
            try:
                result = subprocess.run(
                    ["perf-sentinel", "run", test_script, "--report-formats", "html", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info(f"Audit completed: {result.stdout}")

                if callback:
                    callback(result)

            except subprocess.CalledProcessError as e:
                logger.error(f"Audit failed: {e.stderr}")

        getattr(schedule.every(), day.lower()).at(time_str).do(job)
        self.jobs.append(job)

    def add_custom_interval(
        self,
        test_script: str,
        interval_minutes: int,
        callback: Optional[Callable] = None
    ):
        """
        Schedule audit at custom interval.

        Args:
            test_script: Path to performance test script
            interval_minutes: Interval in minutes
            callback: Optional callback function
        """
        def job():
            logger.info(f"Running scheduled audit: {test_script}")
            try:
                result = subprocess.run(
                    ["perf-sentinel", "run", test_script, "--report-formats", "html", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info(f"Audit completed: {result.stdout}")

                if callback:
                    callback(result)

            except subprocess.CalledProcessError as e:
                logger.error(f"Audit failed: {e.stderr}")

        schedule.every(interval_minutes).minutes.do(job)
        self.jobs.append(job)

    def run(self):
        """Run the scheduler (blocking)."""
        logger.info("Performance scheduler started")
        while True:
            schedule.run_pending()
            time.sleep(60)

    def run_once(self):
        """Run all pending jobs once."""
        schedule.run_pending()
