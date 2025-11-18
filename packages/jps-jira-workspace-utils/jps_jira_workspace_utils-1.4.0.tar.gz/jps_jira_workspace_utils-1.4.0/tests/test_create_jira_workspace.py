import subprocess
import sys


def test_help_option(tmp_path: object) -> None:
    """Verify that the CLI runs and displays help text.

    Args:
        tmp_path: pytest fixture providing a temporary directory.
    """
    result = subprocess.run(
        [sys.executable, "-m", "jps_jira_workspace_utils.create_jira_workspace", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Create a Jira ticket workspace" in result.stdout
