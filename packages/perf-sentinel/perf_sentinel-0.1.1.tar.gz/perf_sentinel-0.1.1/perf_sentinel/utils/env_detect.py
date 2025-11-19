import os
from typing import Dict, Optional


def detect_ci_environment() -> Optional[str]:
    """
    Detect CI environment.

    Returns:
        CI platform name or None
    """
    if os.getenv("GITHUB_ACTIONS"):
        return "github_actions"
    elif os.getenv("GITLAB_CI"):
        return "gitlab_ci"
    elif os.getenv("CIRCLECI"):
        return "circle_ci"
    elif os.getenv("TRAVIS"):
        return "travis_ci"
    elif os.getenv("JENKINS_URL"):
        return "jenkins"
    return None


def get_ci_metadata() -> Dict[str, str]:
    """
    Get CI environment metadata.

    Returns:
        Dictionary with CI metadata
    """
    ci_platform = detect_ci_environment()

    if ci_platform == "github_actions":
        return {
            "platform": "github_actions",
            "repo": os.getenv("GITHUB_REPOSITORY", ""),
            "branch": os.getenv("GITHUB_REF", ""),
            "commit": os.getenv("GITHUB_SHA", ""),
            "run_id": os.getenv("GITHUB_RUN_ID", "")
        }
    elif ci_platform == "gitlab_ci":
        return {
            "platform": "gitlab_ci",
            "repo": os.getenv("CI_PROJECT_PATH", ""),
            "branch": os.getenv("CI_COMMIT_REF_NAME", ""),
            "commit": os.getenv("CI_COMMIT_SHA", ""),
            "pipeline_id": os.getenv("CI_PIPELINE_ID", "")
        }
    else:
        return {
            "platform": ci_platform or "local",
            "repo": "",
            "branch": "",
            "commit": "",
            "run_id": ""
        }
