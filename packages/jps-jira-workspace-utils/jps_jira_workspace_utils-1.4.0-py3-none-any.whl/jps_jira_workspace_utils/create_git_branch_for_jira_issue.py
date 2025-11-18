#!/usr/bin/env python3
"""Create a new Git branch for a Jira issue.

Features:
    1. Optional --jira-id argument (skip prompt if provided)
    2. Optional --codebase argument (skip prompt)
    3. Optional --source-branch argument (default: "development")
    4. Retrieves Jira issue title automatically via REST API
    5. Optional --branch-type argument (feature, bugfix, hotfix) or interactive menu
    6. Reads SSH URL from ~/.my_git_jira.conf ([codebases] section)
    7. Prompts to create ~/jira/[Jira-ID] workspace if missing
    8. Loads Jira environment variables from ~/.jira.env
    9. Uses Google docstring conventions throughout
    10. Logs all executed Git commands to the output log file

Environment Variables (from ~/.jira.env or shell):
    JIRA_BASE_URL   Jira Cloud base URL (e.g., https://example.atlassian.net)
    JIRA_EMAIL      Atlassian account email for API authentication
    JIRA_API_TOKEN  Jira API token generated from user profile
"""

import argparse
import configparser
import getpass
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# test

# ---------------------------------------------------------------------------- #
# Environment Handling
# ---------------------------------------------------------------------------- #


def load_env() -> None:
    """Load Jira environment variables from ~/.jira.env if present.

    The function loads variables using python-dotenv, enabling the user to
    avoid manually exporting credentials to their shell environment.
    """
    env_path = Path.home() / ".jira.env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print("No ~/.jira.env file found; relying on existing environment variables.")


# ---------------------------------------------------------------------------- #
# Utility Functions
# ---------------------------------------------------------------------------- #


def sanitize_title(title: str) -> str:
    """Sanitize Jira issue title for use in a Git branch name.

    Removes special characters and replaces spaces with hyphens.

    Args:
        title: Raw issue title string.

    Returns:
        Sanitized string safe for use in a branch name.
    """
    sanitized = re.sub(r"[^a-zA-Z0-9 ]", "", title)
    return sanitized.replace(" ", "-")


def log_command(log_file: Path, command: list[str]) -> None:
    """Append a command entry to a log file.

    Args:
        log_file: Path to the log file.
        command: List of strings representing the executed command.
    """
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(" ".join(command) + "\n")


def run_and_log(command: list[str], log_file: Path) -> None:
    """Run a shell command via subprocess and log it to the log file.

    Args:
        command: List representing the command to execute.
        log_file: Path to the log file.
    """
    log_command(log_file, command)
    subprocess.run(command, check=True)


def prompt_choice(prompt: str, choices: list[str]) -> str:
    """Prompt the user to select one of several allowed choices.

    Args:
        prompt: Descriptive text to display before the menu.
        choices: List of valid string options.

    Returns:
        The selected string value corresponding to a valid choice.
    """
    print(prompt)
    for i, c in enumerate(choices, start=1):
        print(f"{i}. {c}")
    while True:
        resp = input("Select number or type name: ").strip().lower()
        if resp.isdigit() and 1 <= int(resp) <= len(choices):
            return choices[int(resp) - 1]
        if resp in choices:
            return resp
        print("Invalid selection. Try again.")


# ---------------------------------------------------------------------------- #
# Jira Client
# ---------------------------------------------------------------------------- #


class JiraClient:
    """Lightweight Jira REST client to retrieve issue information."""

    def __init__(self, base_url: str, email: str, token: str) -> None:
        """Initialize a JiraClient session.

        Args:
            base_url: Jira Cloud base URL (no trailing slash).
            email: Jira account email for authentication.
            token: Jira API token.
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(email, token)
        self.session.headers.update({"Accept": "application/json"})

    def get_issue_summary(self, issue_id: str) -> Optional[str]:
        """Retrieve the summary (title) for a Jira issue.

        Args:
            issue_id: Issue key (e.g., "BISD-123").

        Returns:
            The issue summary string if found; otherwise None.
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_id}"
        resp = self.session.get(url)
        if not resp.ok:
            print(f"Error fetching Jira issue {issue_id}: {resp.status_code} {resp.text}")
            return None
        data = resp.json()

        if "fields" not in data or "summary" not in data["fields"]:
            return None
        return str(data.get("fields", {}).get("summary"))


# ---------------------------------------------------------------------------- #
# Configuration Handling
# ---------------------------------------------------------------------------- #


def get_ssh_url_from_config(codebase: str) -> Optional[str]:
    """Retrieve the SSH URL for a specified codebase from ~/.my_git_jira.conf.

    Args:
        codebase: Logical name of the repository (e.g., "carrier-var").

    Returns:
        SSH URL string if found; otherwise None.
    """
    cfg_path = Path.home() / ".my_git_jira.conf"
    if not cfg_path.exists():
        print(f"Config file not found: {cfg_path}")
        return None

    # Disable interpolation so %20 or similar characters don't break parsing.
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(cfg_path)

    if "codebases" not in parser:
        print(f"Missing [codebases] section in {cfg_path}")
        return None

    return parser["codebases"].get(codebase)


# ---------------------------------------------------------------------------- #
# Main Logic
# ---------------------------------------------------------------------------- #


def main() -> None:
    """Program entry point for creating a Git branch from a Jira issue.

    Prompts interactively for missing arguments and performs the following steps:
        1. Load Jira credentials from ~/.jira.env
        2. Retrieve Jira issue summary using REST API
        3. Determine repository SSH URL from ~/.my_git_jira.conf
        4. Create (if needed) the local workspace directory under ~/jira/[Jira-ID]
        5. Clone repository, checkout base branch, and create/push new branch
        6. Log all Git commands executed to the output log file
    """
    load_env()

    parser = argparse.ArgumentParser(description="Create a Git branch for a Jira issue.")
    parser.add_argument("--jira-id", help="Jira issue key (e.g. BISD-123)")
    parser.add_argument("--codebase", help="Codebase name (e.g. carrier-var)")
    parser.add_argument(
        "--source-branch",
        default="development",
        help="Source branch to base from (default: development)",
    )
    parser.add_argument(
        "--branch-type", choices=["feature", "bugfix", "hotfix"], help="Branch type"
    )
    args = parser.parse_args()

    # --- Step 1: Jira issue ID ------------------------------------------------
    issue_id = args.jira_id or input("Enter the Jira issue identifier: ").strip()

    # --- Step 2: Workspace directory -----------------------------------------
    jira_workspace = Path.home() / "jira" / issue_id
    if not jira_workspace.exists():
        resp = input(f"Create directory? {jira_workspace} [Y/n]: ").strip().lower()
        if resp in ("", "y", "yes"):
            jira_workspace.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {jira_workspace}")
        else:
            print("Aborting: workspace directory not created.")
            sys.exit(1)
    os.chdir(jira_workspace)

    # --- Step 3: Determine codebase and SSH URL -------------------------------
    codebase = args.codebase or input("Enter codebase name: ").strip()
    ssh_url = get_ssh_url_from_config(codebase)
    if not ssh_url:
        print(f"Could not find SSH URL for '{codebase}' in ~/.my_git_jira.conf")
        sys.exit(1)

    # --- Step 4: Load Jira credentials and retrieve title ---------------------
    base_url = os.environ.get("JIRA_BASE_URL", "").strip()
    email = os.environ.get("JIRA_EMAIL", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    if not all([base_url, email, token]):
        print("Missing Jira credentials (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN).")
        sys.exit(1)

    jira_client = JiraClient(base_url, email, token)
    issue_title = jira_client.get_issue_summary(issue_id)
    if not issue_title:
        print("Failed to retrieve Jira issue title.")
        sys.exit(1)

    print(f"Issue title: {issue_title}")

    # --- Step 5: Branch type --------------------------------------------------
    branch_type = args.branch_type or prompt_choice(
        "Select branch type:", ["feature", "bugfix", "hotfix"]
    )

    # --- Step 6: Branch creation ----------------------------------------------
    sanitized_title = sanitize_title(issue_title)
    branch_name = f"{branch_type}/{issue_id}-{sanitized_title}"
    repo_name = ssh_url.split("/")[-1].replace(".git", "")
    log_file_name = jira_workspace / f"{issue_id}-{repo_name}-{branch_type}-branch.txt"
    source_branch = args.source_branch

    log_command(log_file_name, ["## Create Git Issue Branch ###"])
    log_command(log_file_name, [f"## date-created: {datetime.today().strftime('%Y-%m-%d-%H%M%S')}"])
    log_command(log_file_name, [f"## created-by: {getpass.getuser()}"])
    log_command(log_file_name, [f"## jira-id: {issue_id}"])
    log_command(log_file_name, [f"## jira-title: {issue_title}"])
    log_command(log_file_name, [f"## codebase: {codebase}"])
    log_command(log_file_name, [f"## ssh-url: {ssh_url}"])
    log_command(log_file_name, [f"## branch-type: {branch_type}"])
    log_command(log_file_name, [f"## source-branch: {source_branch}"])

    try:
        # Log and execute all Git operations
        run_and_log(["git", "clone", ssh_url], log_file_name)
        os.chdir(repo_name)
        run_and_log(["git", "checkout", source_branch], log_file_name)
        run_and_log(["git", "checkout", "-b", branch_name], log_file_name)
        run_and_log(["git", "push", "-u", "origin", branch_name], log_file_name)

        print(f"Branch '{branch_name}' created and pushed successfully.")
        print(f"Log saved to {log_file_name}")

    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------- #

if __name__ == "__main__":
    main()
