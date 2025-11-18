#!/usr/bin/env python3
"""A utility to create a Jira ticket workspace.

A utility to create a Jira ticket workspace and seed a README.md.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

# ----------------------------- Logging setup ----------------------------- #


def configure_logging(verbosity: int) -> None:
    """Configure application logging.

    Args:
        verbosity: Verbosity level. 0=WARNING, 1=INFO, 2+=DEBUG.
    """
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ----------------------------- CLI parsing ----------------------------- #


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Create a Jira ticket workspace directory and seed a README.md."
    )
    parser.add_argument(
        "-t",
        "--ticket",
        dest="ticket",
        type=str,
        help="Jira ticket identifier (e.g., BISD-1050).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (use -v, -vv).",
    )
    return parser


# ----------------------------- Core logic ----------------------------- #

_JIRA_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]+-\d+$")


def is_valid_jira_id(jira_id: str) -> bool:
    """Validate a Jira ticket identifier.

    A valid identifier must be a string prefix followed by hyphen then an unsigned integer,
    e.g., 'BISD-1050'.

    Args:
        jira_id: Candidate Jira ticket identifier.

    Returns:
        True if valid, else False.
    """
    return bool(_JIRA_ID_PATTERN.match(jira_id.strip()))


def prompt_for_jira_id(max_additional_attempts: int = 3) -> Optional[str]:
    """Prompt the user for a Jira ticket identifier with limited attempts.

    Per SRS:
      - If not provided via CLI, prompt for the Jira ticket identifier.
      - If invalid, continue to prompt the user **3 more times**.
      - During the first prompt show an example (e.g., BISD-1050).

    Note on interpretation:
      The SRS also says "If after the third attempt the identifier is still invalid... stop."
      This conflicts with "prompt 3 more times." We interpret this as **4 total attempts**:
      the initial prompt + 3 additional attempts.

    Args:
        max_additional_attempts: Number of additional attempts after the first prompt.

    Returns:
        A valid Jira ID or None if attempts are exhausted.
    """
    example = "BISD-1050"
    attempts_remaining = 1 + max_additional_attempts  # total attempts

    prompt = f"Enter the Jira ticket identifier (e.g., {example}): "
    while attempts_remaining > 0:
        user_input = input(prompt).strip()
        logging.debug("User entered Jira ID candidate: %r", user_input)
        if is_valid_jira_id(user_input):
            return user_input
        attempts_remaining -= 1
        if attempts_remaining > 0:
            print(
                "Invalid Jira ID format. Expected like 'BISD-1050'. Please try again.",
                file=sys.stderr,
            )

        # After the first prompt, subsequent prompts can be shorter
        prompt = "Enter Jira ticket identifier: "
    return None


def ensure_workspace(jira_id: str) -> Tuple[Path, bool]:
    """Ensure the Jira workspace directory exists.

    Creates ~/jira/[Jira ID] if missing.

    Args:
        jira_id: Validated Jira ticket identifier.

    Returns:
        (workspace_path, created_flag) where created_flag is True if created, else False.
    """
    home = Path.home()
    workspace = home / "jira" / jira_id
    if workspace.exists():
        print(f"The directory {workspace} already existed.")
        logging.info("Workspace already existed at %s", workspace)
        created = False
    else:
        workspace.mkdir(parents=True, exist_ok=True)
        print(f"The directory {workspace} has been created.")
        logging.info("Workspace created at %s", workspace)
        created = True
    return workspace.resolve(), created


def write_readme(workspace: Path, jira_id: str) -> Path:
    """Create README.md in the workspace if it does not already exist.

    Args:
        workspace: Absolute path to the Jira workspace directory.
        jira_id: Jira ticket identifier.

    Returns:
        Absolute path to the README.md file.
    """
    readme = workspace / "README.md"
    if readme.exists():
        logging.info("README.md already exists at %s", readme)
        return readme.resolve()

    content = f"""# Jira: {jira_id}

keywords:

# Steps
## Step 1 - Create workspace

```bash
mkdir ~/jira/{jira_id}
cd ~/jira/{jira_id}
```

## Step 2 - Clone code base

```bash
```

## Step 3 - Create branch
```bash
```

# Contact
Jay Sundaram <jsundaram@baylorgenetics.com>

# References
"""
    readme.write_text(content, encoding="utf-8")
    logging.info("README.md created at %s", readme)
    return readme.resolve()


def resolve_jira_id(cli_ticket: Optional[str]) -> Optional[str]:
    """Resolve a (valid) Jira ID either from CLI or interactive prompts.

    Args:
        cli_ticket: Optional Jira ticket from CLI.

    Returns:
        Valid Jira ID or None if could not be obtained/validated.
    """
    if cli_ticket:
        logging.debug("CLI provided Jira ID: %s", cli_ticket)
        if is_valid_jira_id(cli_ticket):
            return cli_ticket
        print(
            "The provided Jira ticket identifier is invalid. Falling back to interactive prompt.",
            file=sys.stderr,
        )

    return prompt_for_jira_id(max_additional_attempts=3)


def main(argv: Optional[list[str]] = None) -> int:
    """Program entry point.

    Args:
        argv: Optional list of CLI arguments for testing.

    Returns:
        Process return code (0 on success, non-zero otherwise).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.verbose)
    logging.debug("Parsed arguments: %s", args)

    jira_id = resolve_jira_id(args.ticket)
    if not jira_id:
        logging.error("Failed to obtain a valid Jira ticket identifier after allowed attempts.")
        return 2

    workspace, created = ensure_workspace(jira_id)
    readme = write_readme(workspace, jira_id)

    # SRS: At end of execution, print absolute paths to workspace and README.md
    print(str(workspace))
    print(str(readme))

    # Note: The SRS mentions "print absolute path to the report file". No report file
    # is otherwise defined; we interpret the deliverable as README.md.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
