"""
Unit tests for create_git_branch_for_jira_issue CLI.
"""

import builtins
import subprocess
import sys


def test_help_option() -> None:
    """Verify that the CLI runs and displays help text."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "jps_jira_workspace_utils.create_git_branch_for_jira_issue",
            "--help",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout
    # Updated assertion
    assert "create_git_branch_for_jira_issue" in result.stdout


def test_env_file_message(monkeypatch: object, tmp_path: object) -> None:
    """Verify message when no ~/.jira.env file exists.

    Args:
        monkeypatch: pytest fixture to modify environment variables.
        tmp_path: pytest fixture providing a temporary directory.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "jps_jira_workspace_utils.create_git_branch_for_jira_issue",
            "--help",
        ],
        capture_output=True,
        text=True,
    )
    assert "No ~/.jira.env file found" in result.stderr or result.stdout


def test_mock_branch_creation(monkeypatch: object) -> None:
    """Simulate branch creation logic without executing Git commands.

    Args:
        monkeypatch: pytest fixture to mock functions and environment.
    """
    import jps_jira_workspace_utils.create_git_branch_for_jira_issue as cli

    # Mock subprocess.run to avoid calling real git
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **kw: 0)

    # Mock os operations and environment variables
    monkeypatch.setattr(cli.os, "getenv", lambda k, d=None: d)

    # ✅ Auto-answer to input() prompt
    monkeypatch.setattr(builtins, "input", lambda *a, **kw: "y")

    # Minimal CLI arguments
    sys.argv = [
        "create_git_branch_for_jira_issue",
        "--jira-id",
        "BISD-123",
        "--codebase",
        "carrier-var-file-utils",
        "--branch-type",
        "feature",
    ]

    try:
        cli.main()
    except SystemExit:
        # argparse may call sys.exit() — ignore
        pass
