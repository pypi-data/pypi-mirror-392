# jps-jira-workspace-utils

![Test](https://github.com/jai-python3/jps-jira-workspace-utils/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/jai-python3/jps-jira-workspace-utils/actions/workflows/publish-to-pypi.yml/badge.svg)
[![codecov](https://codecov.io/gh/jai-python3/jps-pre-commit-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/jai-python3/jps-jira-workflow-utils)

Utilities for automating Jira-related workspace and branch management tasks.  
Includes CLI tools for creating Jira workspaces and Git branches that follow team conventions.

---

## 🧩 Installation

```bash
pip install jps-jira-workspace-utils
```

or install in editable mode for local development:

```bash
git clone git@github.com:jai-python3/jps-jira-workspace-utils.git  
cd jps-jira-workspace-utils  
pip install -e .
```

---

## 1. 🧩 create-jira-workspace

This utility initializes a Jira workspace with a standardized directory structure and a seeded `README.md` file.

### 1.1. Usage

```bash
create-jira-workspace --jira-id JPS-123 --project carrier-var
```

### 1.2. Options

| Option | Description | Default |
|---------|--------------|----------|
| `--jira-id` | Jira issue key (e.g., `JPS-123`) | *(required)* |
| `--project` | Project or codebase name | *(required)* |
| `--path` | Base path where workspace will be created | Current directory |
| `--open` | Open workspace in VSCode after creation | `False` |

### 1.3. Example

```bash
create-jira-workspace --jira-id JPS-123 --project carrier-var --open
```

This creates a directory like:

```bash
~/jira/JPS-123-carrier-var/
```

and seeds it with:

```bash
README.md  
```

---

## 2. 🧩 create-git-branch-for-jira-issue

This utility automates creating Git branches that follow the Jira naming convention.

### 2.1. Usage

```bash
create-git-branch-for-jira-issue --jira-id JPS-123 --codebase carrier-var --branch-type feature
```

### 2.2. Options

| Option | Description | Default |
|---------|--------------|----------|
| `--jira-id` | Jira issue key (e.g., `JPS-123`) | *(required)* |
| `--codebase` | Codebase name (e.g., `carrier-var`) | *(required)* |
| `--source-branch` | Source branch to base from | `development` |
| `--branch-type` | Branch type (`feature`, `bugfix`, `hotfix`) | `feature` |

### 2.3. Example

```bash
create-git-branch-for-jira-issue --jira-id JPS-321 --codebase carrier-var --branch-type bugfix
```

This creates a new branch named:

```bash
bugfix/JPS-321-carrier-var
```

If a `~/.jira.env` file exists, it will automatically load Jira-related environment variables (such as `JIRA_USER` and `JIRA_TOKEN`).  
If no `.jira.env` is found, it will rely on environment variables already defined in your shell.

## ⚙️ Required Configuration File (`~/.my_git_jira.conf`)

The `create-git-branch-for-jira-issue` utility uses an optional configuration file to locate Git repositories by their short **codebase identifiers**.

### 📄 Location

```bash
~/.my_git_jira.conf
```

### 🧩 Purpose

This configuration maps human-readable **codebase names** (like `project1`) to their **full Git repository URLs**.  
It allows you to specify a short `--codebase` name on the command line instead of typing a long Azure DevOps URL each time.

When a `--codebase` is provided, the utility looks up its corresponding URL from this configuration, navigates to the local
clone (if it exists), and creates the new branch from the appropriate source branch.

---

### 🧾 Example Configuration

```bash
[codebases]
project1 = git@ssh.dev.azure.com:v3/org1/Org1/project1
project2 = git@ssh.dev.azure.com:v3/org1/Org1/project2
```

---

### 🧠 Notes

- The `[codebases]` section is required; each key represents a **codebase short name**.  
- Values must be **valid SSH URLs** to Azure DevOps or GitHub repositories.  
- The CLI uses this mapping to locate the right Git repository automatically.  

---

### ✅ Example Workflow

```bash
create-git-branch-for-jira-issue --jira-id JPS-987 --codebase project1 --branch-type feature
```

This command will:

1️⃣ Read `~/.my_git_jira.conf`  
2️⃣ Find the SSH URL for `project1`  
3️⃣ Verify or locate the local Git repository  
4️⃣ Checkout the source branch (e.g., `development`)  
5️⃣ Create and switch to:

```bash
feature/JPS-987-project1
```

---

## 🧪 Development and Testing

Install dependencies for linting, formatting, and testing:

```bash
pip install -e '.[dev]'
```

Run all lint and test checks:

```bash
make lint  
make test
```

---

## 🧾 License

MIT License  
© 2025 Jaideep Sundaram
