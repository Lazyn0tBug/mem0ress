"""Git operations for Data Plane - commit ID tracking for repositories.

Data Plane tracks the current commit ID of all relevant repositories,
enabling Agent to know "which version of code was last operated on".

The data_plane snapshot is stored in session.md's turn entries as:
    data_plane:
      /path/to/repo: abc1234

This module provides:
- Discovery: find all git repos under a directory
- Commit tracking: get current commit ID for each repo
- Clean state check: detect uncommitted changes (which affect snapshot reliability)
"""

import subprocess
from pathlib import Path


class GitError(Exception):
    """Raised when a git operation fails."""

    pass


def _run_git(repo_path: Path, *args: str) -> str:
    """Run a git command in the given repo directory.

    Args:
        repo_path: Path to the git repository
        *args: Git command arguments (e.g., "rev-parse", "HEAD")

    Returns:
        stdout from git command

    Raises:
        GitError: If git command fails
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {' '.join(args)}: {e.stderr}") from e
    except FileNotFoundError:
        raise GitError("git not found in PATH — ensure git is installed") from None


def is_git_repo(path: Path) -> bool:
    """Check if the given path is a git repository.

    Args:
        path: Path to check

    Returns:
        True if path is inside a git repository (has .git directory)
    """
    try:
        _run_git(path, "rev-parse", "--is-inside-work-tree")
        return True
    except GitError:
        return False


def get_repo_commit_id(repo_path: Path) -> str:
    """Get current commit ID (short hash) for a git repository.

    Args:
        repo_path: Path to the git repository

    Returns:
        Short commit hash (7 characters, matching git rev-parse --short HEAD)

    Raises:
        GitError: If not a git repo or git command fails
    """
    if not is_git_repo(repo_path):
        raise GitError(f"Path is not a git repository: {repo_path}")

    return _run_git(repo_path, "rev-parse", "--short", "HEAD")


def get_repo_branch(repo_path: Path) -> str:
    """Get current branch name for a git repository.

    Args:
        repo_path: Path to the git repository

    Returns:
        Current branch name

    Raises:
        GitError: If not a git repo or git command fails
    """
    if not is_git_repo(repo_path):
        raise GitError(f"Path is not a git repository: {repo_path}")

    return _run_git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")


def is_repo_clean(repo_path: Path) -> bool:
    """Check if the repository has uncommitted changes.

    A clean repo means the snapshot is reliable — what you see is what you get.
    A dirty repo means there are uncommitted changes that won't be captured
    in the commit ID snapshot.

    Args:
        repo_path: Path to the git repository

    Returns:
        True if repo is clean (no uncommitted changes), False otherwise

    Raises:
        GitError: If not a git repo or git command fails
    """
    if not is_git_repo(repo_path):
        raise GitError(f"Path is not a git repository: {repo_path}")

    # --porcelain gives machine-readable output
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    # Empty output means clean (no uncommitted changes)
    return result.stdout.strip() == ""


def get_dirty_files(repo_path: Path) -> list[str]:
    """Get list of uncommitted/dirty files in the repository.

    Args:
        repo_path: Path to the git repository

    Returns:
        List of file paths (relative to repo root) that have uncommitted changes

    Raises:
        GitError: If not a git repo or git command fails
    """
    if not is_git_repo(repo_path):
        raise GitError(f"Path is not a git repository: {repo_path}")

    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    files = []
    for line in result.stdout.strip().split("\n"):
        if line:
            # Format: XY filename, XY is status like " M" (modified in worktree)
            # We only need the filename (index 1 onwards), stripping status indicator
            parts = line[2:].strip()
            if parts:
                files.append(parts)
    return files


def find_git_repos(root: Path) -> list[Path]:
    """Find all git repositories under a directory tree.

    Performs a breadth-first search from root, stopping at the first
    .git directory found for each repo. Does not descend into nested repos.

    Args:
        root: Root directory to search from

    Returns:
        List of paths to discovered git repositories (directories with .git)

    Raises:
        GitError: If root directory does not exist
    """
    if not root.exists():
        raise GitError(f"Path does not exist: {root}")

    repos: list[Path] = []
    dirs_to_scan = [root]

    while dirs_to_scan:
        current = dirs_to_scan.pop(0)
        git_dir = current / ".git"

        if git_dir.exists() and git_dir.is_dir():
            # It's a repo — add to results
            repos.append(current)
            # Don't descend INTO this repo's subdirs (they're part of this repo)
            # but continue BFS to find sibling repos (other top-level dirs at current level)
        else:
            # Not a repo — scan children to find more dirs
            try:
                for child in sorted(current.iterdir()):
                    if child.is_dir() and child.name not in (".git", "node_modules", "__pycache__"):
                        dirs_to_scan.append(child)
            except PermissionError:
                continue

    return repos


def get_data_plane(root: Path) -> dict[str, str]:
    """Build a data plane snapshot — all repo commit IDs under a directory.

    Scans the directory tree for git repositories and records their current
    commit IDs. This enables the Agent to know "which version of code was
    last operated on" when resuming work.

    Args:
        root: Root directory to scan (e.g., task directory or workspace root)

    Returns:
        Dict mapping repo path string -> commit ID
        Only includes clean repos (uncommitted changes are excluded)
    """
    repos = find_git_repos(root)
    data_plane: dict[str, str] = {}

    for repo_path in repos:
        try:
            # Skip dirty repos — their state is not fully captured by commit ID
            if not is_repo_clean(repo_path):
                continue
            commit_id = get_repo_commit_id(repo_path)
            data_plane[str(repo_path)] = commit_id
        except GitError:
            # Skip repos we can't read — they're not our concern
            continue

    return data_plane


def snapshot_data_plane(
    task_id: str,
    substrate_root: Path,
    data_plane: dict[str, str] | None = None,
) -> None:
    """Snapshot the current data plane into the task's session.md.

    This is a thin wrapper around intercept.snapshot_session that ensures
    data_plane is captured. Call this at the end of each turn to record
    which code versions were operated on.

    Args:
        task_id: Task identifier
        substrate_root: Root directory (.cap)
        data_plane: Optional pre-built data plane dict. If None, auto-discovers
                    all repos under substrate_root.
    """
    from mem0ress.gateway.intercept import snapshot_session

    if data_plane is None:
        data_plane = get_data_plane(substrate_root)

    snapshot_session(
        task_id=task_id,
        substrate_root=substrate_root,
        code_progress="(data plane snapshot)",
        data_plane=data_plane,
        status="in-progress",
    )
