import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class PerformanceReport:
    """Build comprehensive performance reports in multiple formats."""

    def __init__(self, output_dir: str = "./perf_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics: List[Dict[str, Any]] = []

    def add_metric(self, metric: Dict[str, Any]) -> None:
        """Add a performance metric to the report."""
        self.metrics.append(metric)

    def load_from_json(self, json_path: str) -> None:
        """Load metrics from JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                self.metrics.extend(data)
            else:
                self.metrics.append(data)

    def generate_json(self, output_name: str = "perf_report.json") -> str:
        """Generate JSON report."""
        output_file = self.output_dir / output_name

        report = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_operations": len(self.metrics),
            "metrics": self.metrics,
            "summary": self._calculate_summary()
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        return str(output_file)

    def generate_html(self, output_name: str = "perf_report.html") -> str:
        """Generate HTML report."""
        output_file = self.output_dir / output_name

        summary = self._calculate_summary()

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Performance Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
        }}
        .summary-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .metrics-table {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
        }}
        td {{
            padding: 12px;
            border-top: 1px solid #e9ecef;
        }}
        .warning {{
            color: #ff6b6b;
            font-weight: bold;
        }}
        .success {{
            color: #51cf66;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Performance Report</h1>
        <p>Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
    </div>

    <div class="summary">
        <div class="summary-card">
            <h3>Total Operations</h3>
            <div class="value">{summary['total_operations']}</div>
        </div>
        <div class="summary-card">
            <h3>Average Time</h3>
            <div class="value">{summary['avg_time_ms']:.2f}ms</div>
        </div>
        <div class="summary-card">
            <h3>Max Time</h3>
            <div class="value">{summary['max_time_ms']:.2f}ms</div>
        </div>
        <div class="summary-card">
            <h3>Threshold Exceeded</h3>
            <div class="value {'warning' if summary['threshold_exceeded_count'] > 0 else 'success'}">
                {summary['threshold_exceeded_count']}
            </div>
        </div>
    </div>

    <div class="metrics-table">
        <table>
            <thead>
                <tr>
                    <th>Operation</th>
                    <th>Type</th>
                    <th>Time (ms)</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
"""

        for metric in self.metrics:
            warning_class = 'warning' if metric.get('threshold_exceeded', False) else ''
            details = []

            if metric.get('has_yield'):
                details.append('Has Yield')
            if metric.get('has_sync_blocking'):
                details.append('⚠ Sync Blocking')

            html_content += f"""
                <tr>
                    <td>{metric.get('operation', 'Unknown')}</td>
                    <td>{metric.get('type', 'Unknown')}</td>
                    <td class="{warning_class}">{metric.get('elapsed_ms', 0):.2f}</td>
                    <td>{', '.join(details) if details else '-'}</td>
                </tr>
"""

        html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_content)

        return str(output_file)

    def generate_markdown(self, output_name: str = "perf_report.md") -> str:
        """Generate Markdown report."""
        output_file = self.output_dir / output_name

        summary = self._calculate_summary()

        md_content = f"""# Performance Report

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

## Summary

- **Total Operations:** {summary['total_operations']}
- **Average Time:** {summary['avg_time_ms']:.2f}ms
- **Max Time:** {summary['max_time_ms']:.2f}ms
- **Threshold Exceeded:** {summary['threshold_exceeded_count']}

## Metrics

| Operation | Type | Time (ms) | Details |
|-----------|------|-----------|---------|
"""

        for metric in self.metrics:
            details = []
            if metric.get('has_yield'):
                details.append('Has Yield')
            if metric.get('has_sync_blocking'):
                details.append('⚠ Sync Blocking')
            if metric.get('threshold_exceeded'):
                details.append('⚠ Threshold Exceeded')

            md_content += f"| {metric.get('operation', 'Unknown')} | {metric.get('type', 'Unknown')} | {metric.get('elapsed_ms', 0):.2f} | {', '.join(details) if details else '-'} |\n"

        with open(output_file, 'w') as f:
            f.write(md_content)

        return str(output_file)

    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not self.metrics:
            return {
                "total_operations": 0,
                "avg_time_ms": 0.0,
                "max_time_ms": 0.0,
                "threshold_exceeded_count": 0
            }

        times = [m.get('elapsed_ms', 0) for m in self.metrics]
        threshold_exceeded = sum(1 for m in self.metrics if m.get('threshold_exceeded', False))

        return {
            "total_operations": len(self.metrics),
            "avg_time_ms": sum(times) / len(times),
            "max_time_ms": max(times),
            "threshold_exceeded_count": threshold_exceeded
        }
