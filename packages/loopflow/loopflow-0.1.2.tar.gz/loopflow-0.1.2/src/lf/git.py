"""Simple git operations using subprocess."""

import subprocess
from pathlib import Path
from typing import Optional


def find_root(path: Path) -> Optional[Path]:
    """
    Find the git repository root for the given path.

    Args:
        path: Starting path to search from

    Returns:
        Path to git root, or None if not in a git repository
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path if path.is_dir() else path.parent,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def fetch(repo_root: Path) -> bool:
    """
    Attempt to fetch from origin (best effort, doesn't fail if it errors).

    Args:
        repo_root: Path to git repository root

    Returns:
        True if fetch succeeded, False otherwise
    """
    try:
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=repo_root,
            capture_output=True,
            timeout=10,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def ref_exists(repo_root: Path, ref: str) -> bool:
    """
    Check if a git ref exists.

    Args:
        repo_root: Path to git repository root
        ref: Git reference (branch, tag, commit, etc.)

    Returns:
        True if ref exists, False otherwise
    """
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", ref],
            cwd=repo_root,
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def diff(repo_root: Path, base_ref: str) -> str:
    """
    Get git diff against a base reference.

    Args:
        repo_root: Path to git repository root
        base_ref: Git reference to diff against

    Returns:
        Diff output as string, empty string if error
    """
    try:
        result = subprocess.run(
            ["git", "diff", base_ref],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
