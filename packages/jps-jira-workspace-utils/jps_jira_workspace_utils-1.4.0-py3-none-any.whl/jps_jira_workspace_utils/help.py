#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lists all available CLI tools in the jps-jira-workspace-utils package.

This script provides a unified help command for developers and release
managers to understand the purpose of each entrypoint utility included
in this package.

Usage:
    jps-jira-workspace-utils-help
"""

import textwrap

# ANSI colour codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def main() -> None:
    """Display help for all entrypoint scripts in this package."""
    help_text = textwrap.dedent(
        f"""
    Jira Workspace & Git Automation — Available Commands
    ====================================================

    {GREEN}create-jira-workspace{RESET}
        Create a standardized workspace for a Jira ticket under ~/jira/<JIRA-ID>.
        - Generates the directory tree if missing.
        - Seeds a templated README.md with placeholders for clone/branch steps.
        - Validates the ticket identifier (e.g. JPS-1234).

        Example:
            {YELLOW}create-jira-workspace -t JPS-1234{RESET}

    {GREEN}create-git-branch-for-jira-issue{RESET}
        Spin up a Git feature branch from a Jira issue.
        - Fetches the issue title via Jira REST API.
        - Builds a branch name: <type>/<JIRA-ID>-<sanitized-title>.
        - Clones the repo, checks out the source branch (default: development),
          creates and pushes the new branch.
        - Logs every Git command to a timestamped file.

        Example:
            {YELLOW}create-git-branch-for-jira-issue --jira-id JPS-1234 --codebase carrier-var --branch-type bugfix{RESET}  # noqa E501

    {GREEN}jps-jira-workspace-utils-help{RESET}
        Displays this overview of all available commands.

    ----------------------------------------------------
    Tip: Run each command with '--help' to see detailed options.
    """
    )

    print(help_text)


if __name__ == "__main__":
    main()
