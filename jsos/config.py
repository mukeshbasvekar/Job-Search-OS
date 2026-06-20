"""Workspace-aware config loader.

Paths are resolved from the current working directory at call time,
not at import time — so the package works when installed globally via pipx.
"""
from pathlib import Path

import yaml


def _find_workspace_root() -> Path | None:
    candidate = Path.cwd()
    for _ in range(6):
        if (candidate / "config.yaml").exists():
            return candidate
        candidate = candidate.parent
    return None


def workspace_root() -> Path:
    root = _find_workspace_root()
    if root is None:
        import click
        raise click.ClickException(
            "No config.yaml found in this directory or any parent.\n\n"
            "  Set up a workspace first:\n"
            "    jsos init ~/my-job-search\n"
            "    cd ~/my-job-search\n"
        )
    return root


# These functions are called at command-run time, not at import time.
def get_data_dir() -> Path:
    return workspace_root() / "data"

def get_research_dir() -> Path:
    return workspace_root() / "4-Company-Research"

def get_tracker_csv() -> Path:
    return workspace_root() / "3-Outreach" / "outreach_tracker.csv"


def load() -> dict:
    with open(workspace_root() / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)
