import argparse
import sys
from pathlib import Path
from typing import List
from perf_sentinel.reporter.report_builder import PerformanceReport
from perf_sentinel.reporter.pyspy_integration import PySpyProfiler
from perf_sentinel.audit.trend_analyzer import TrendAnalyzer


def run_command(args):
    """Execute performance test run."""
    print(f"Running performance tests: {args.test_path}")

    if args.profile:
        profiler = PySpyProfiler(output_dir=args.output_dir)
        try:
            profile_file = profiler.profile_script(
                script_path=args.test_path,
                duration=args.duration,
                format=args.profile_format
            )
            print(f"Profile generated: {profile_file}")
        except Exception as e:
            print(f"Error during profiling: {e}", file=sys.stderr)
            return 1

    if args.report_formats:
        report = PerformanceReport(output_dir=args.output_dir)

        json_files = list(Path(args.output_dir).glob("*.json"))
        for json_file in json_files:
            try:
                report.load_from_json(str(json_file))
            except Exception:
                pass

        for format_type in args.report_formats:
            try:
                if format_type == "html":
                    output = report.generate_html()
                    print(f"HTML report generated: {output}")
                elif format_type == "json":
                    output = report.generate_json()
                    print(f"JSON report generated: {output}")
                elif format_type == "markdown":
                    output = report.generate_markdown()
                    print(f"Markdown report generated: {output}")
            except Exception as e:
                print(f"Error generating {format_type} report: {e}", file=sys.stderr)

    return 0


def audit_command(args):
    """Execute performance audit."""
    print(f"Running performance audit (threshold: {args.threshold}%)")

    analyzer = TrendAnalyzer(data_dir=args.data_dir)

    try:
        regressions = analyzer.detect_regressions(threshold_percent=args.threshold)

        if regressions:
            print(f"\n  Found {len(regressions)} performance regressions:")
            for reg in regressions:
                print(f"  - {reg['operation']}: {reg['change_percent']:.1f}% slower")
            return 1
        else:
            print("\n No significant performance regressions detected")
            return 0

    except Exception as e:
        print(f"Error during audit: {e}", file=sys.stderr)
        return 1


def init_command(args):
    """Initialize PerfSentinel in a project."""
    print("Initializing PerfSentinel...")

    if args.ci == "github":
        from perf_sentinel.ci.github_actions import generate_github_actions
        workflow_file = generate_github_actions()
        print(f" GitHub Actions workflow created: {workflow_file}")

    elif args.ci == "gitlab":
        from perf_sentinel.ci.gitlab_ci import generate_gitlab_ci
        ci_file = generate_gitlab_ci()
        print(f" GitLab CI configuration created: {ci_file}")

    Path("perf_reports").mkdir(exist_ok=True)
    print(" Performance reports directory created")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="perf-sentinel",
        description="Performance testing and monitoring system"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run performance tests")
    run_parser.add_argument("test_path", help="Path to test script")
    run_parser.add_argument("--profile", action="store_true", help="Enable py-spy profiling")
    run_parser.add_argument("--duration", type=int, help="Profiling duration in seconds")
    run_parser.add_argument("--profile-format", default="speedscope", choices=["speedscope", "flamegraph", "raw"])
    run_parser.add_argument("--report-formats", nargs="+", choices=["html", "json", "markdown"], help="Report formats to generate")
    run_parser.add_argument("--output-dir", default="./perf_reports", help="Output directory for reports")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit performance trends")
    audit_parser.add_argument("--threshold", type=float, default=10.0, help="Regression threshold percentage")
    audit_parser.add_argument("--data-dir", default="./perf_reports", help="Directory with historical data")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize PerfSentinel in project")
    init_parser.add_argument("--ci", choices=["github", "gitlab"], help="Generate CI configuration")

    args = parser.parse_args()

    if args.command == "run":
        return run_command(args)
    elif args.command == "audit":
        return audit_command(args)
    elif args.command == "init":
        return init_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
