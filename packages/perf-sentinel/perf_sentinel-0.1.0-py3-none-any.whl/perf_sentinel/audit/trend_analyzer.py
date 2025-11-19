import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class TrendAnalyzer:
    """Analyze performance trends and detect regressions."""

    def __init__(self, data_dir: str = "./perf_reports"):
        self.data_dir = Path(data_dir)

    def load_historical_data(self, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load historical performance data.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary mapping operation names to their metrics over time
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        metrics_by_operation = defaultdict(list)

        json_files = sorted(self.data_dir.glob("perf_report_*.json"))

        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                    timestamp_str = data.get("generated_at", "")
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        continue

                    if timestamp < cutoff_date:
                        continue

                    for metric in data.get("metrics", []):
                        operation = metric.get("operation")
                        if operation:
                            metrics_by_operation[operation].append({
                                "timestamp": timestamp,
                                "elapsed_ms": metric.get("elapsed_ms", 0),
                                "type": metric.get("type"),
                                "has_sync_blocking": metric.get("has_sync_blocking", False)
                            })

            except (json.JSONDecodeError, IOError):
                continue

        return dict(metrics_by_operation)

    def calculate_baseline(
        self,
        operation: str,
        historical_data: Optional[Dict[str, List[Dict[str, Any]]]] = None
    ) -> Optional[float]:
        """
        Calculate baseline (median) performance for an operation.

        Args:
            operation: Operation name
            historical_data: Pre-loaded historical data (optional)

        Returns:
            Baseline time in milliseconds, or None if insufficient data
        """
        if historical_data is None:
            historical_data = self.load_historical_data()

        metrics = historical_data.get(operation, [])

        if len(metrics) < 3:
            return None

        times = sorted([m["elapsed_ms"] for m in metrics])
        median_idx = len(times) // 2

        return times[median_idx]

    def detect_regressions(
        self,
        threshold_percent: float = 10.0,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Detect performance regressions.

        Args:
            threshold_percent: Regression threshold as percentage
            days: Number of days to analyze

        Returns:
            List of detected regressions
        """
        historical_data = self.load_historical_data(days=days)
        regressions = []

        for operation, metrics in historical_data.items():
            if len(metrics) < 5:
                continue

            metrics_sorted = sorted(metrics, key=lambda x: x["timestamp"])

            baseline_metrics = metrics_sorted[:len(metrics_sorted) * 2 // 3]
            recent_metrics = metrics_sorted[len(metrics_sorted) * 2 // 3:]

            if not baseline_metrics or not recent_metrics:
                continue

            baseline_times = [m["elapsed_ms"] for m in baseline_metrics]
            recent_times = [m["elapsed_ms"] for m in recent_metrics]

            baseline_avg = sum(baseline_times) / len(baseline_times)
            recent_avg = sum(recent_times) / len(recent_times)

            if baseline_avg == 0:
                continue

            change_percent = ((recent_avg - baseline_avg) / baseline_avg) * 100

            if change_percent > threshold_percent:
                regressions.append({
                    "operation": operation,
                    "baseline_ms": round(baseline_avg, 2),
                    "recent_ms": round(recent_avg, 2),
                    "change_percent": round(change_percent, 2),
                    "sample_count": len(recent_metrics)
                })

        return sorted(regressions, key=lambda x: x["change_percent"], reverse=True)

    def generate_trend_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive trend analysis report.

        Args:
            days: Number of days to analyze

        Returns:
            Trend report dictionary
        """
        historical_data = self.load_historical_data(days=days)
        trends = {}

        for operation, metrics in historical_data.items():
            if len(metrics) < 2:
                continue

            times = [m["elapsed_ms"] for m in metrics]

            trends[operation] = {
                "count": len(metrics),
                "min_ms": round(min(times), 2),
                "max_ms": round(max(times), 2),
                "avg_ms": round(sum(times) / len(times), 2),
                "median_ms": round(sorted(times)[len(times) // 2], 2)
            }

        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "period_days": days,
            "operations_analyzed": len(trends),
            "trends": trends
        }
