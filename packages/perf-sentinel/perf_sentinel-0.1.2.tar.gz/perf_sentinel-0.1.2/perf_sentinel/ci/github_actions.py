from pathlib import Path


GITHUB_ACTIONS_TEMPLATE = """name: Performance Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  performance-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install perf-sentinel py-spy aioflame
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Run performance tests
      run: |
        perf-sentinel run --profile --report-formats html json markdown

    - name: Upload performance reports
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: performance-reports
        path: perf_reports/
        retention-days: 30

    - name: Check performance regression
      run: |
        perf-sentinel audit --threshold 20  # 20% regression threshold
"""


def generate_github_actions(output_path: str = ".github/workflows/performance.yml") -> str:
    """
    Generate GitHub Actions workflow file for performance testing.

    Args:
        output_path: Path where workflow file should be created

    Returns:
        Path to generated workflow file
    """
    workflow_path = Path(output_path)
    workflow_path.parent.mkdir(parents=True, exist_ok=True)

    with open(workflow_path, 'w') as f:
        f.write(GITHUB_ACTIONS_TEMPLATE)

    return str(workflow_path)
