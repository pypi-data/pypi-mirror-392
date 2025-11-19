from pathlib import Path


GITLAB_CI_TEMPLATE = """stages:
  - test
  - performance

performance-test:
  stage: performance
  image: python:3.11

  before_script:
    - pip install --upgrade pip
    - pip install perf-sentinel py-spy aioflame
    - if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

  script:
    - perf-sentinel run --profile --report-formats html json markdown
    - perf-sentinel audit --threshold 20

  artifacts:
    when: always
    paths:
      - perf_reports/
    expire_in: 30 days
    reports:
      performance: perf_reports/perf_report.json

  only:
    - main
    - develop
    - merge_requests

  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
      when: always
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: on_success
    - if: '$CI_MERGE_REQUEST_ID'
      when: on_success
"""


def generate_gitlab_ci(output_path: str = ".gitlab-ci.yml") -> str:
    """
    Generate GitLab CI configuration file for performance testing.

    Args:
        output_path: Path where CI file should be created

    Returns:
        Path to generated CI file
    """
    ci_path = Path(output_path)
    ci_path.parent.mkdir(parents=True, exist_ok=True)

    with open(ci_path, 'w') as f:
        f.write(GITLAB_CI_TEMPLATE)

    return str(ci_path)
