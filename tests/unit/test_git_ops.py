"""Tests for git_ops module."""

import os
import subprocess
from pathlib import Path

import pytest

# Set git test identity globally to avoid "please tell me who you are" errors
os.environ["GIT_AUTHOR_NAME"] = "Test User"
os.environ["GIT_AUTHOR_EMAIL"] = "test@test.com"
os.environ["GIT_COMMITTER_NAME"] = "Test User"
os.environ["GIT_COMMITTER_EMAIL"] = "test@test.com"


def _git_commit_empty(repo_path: Path) -> None:
    """Create an initial commit with a file (needed for git commit)."""
    subprocess.run(
        ["git", "-C", str(repo_path), "init"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_path), "config", "user.email", "test@test.com"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_path), "config", "user.name", "Test"],
        check=True, capture_output=True,
    )
    # Create a file so commit isn't empty
    (repo_path / "README.md").write_text("# test")
    subprocess.run(
        ["git", "-C", str(repo_path), "add", "."],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_path), "commit", "-m", "initial"],
        check=True, capture_output=True,
    )


class TestIsGitRepo:
    """Tests for is_git_repo()."""

    def test_returns_true_for_git_repo(self, tmp_path: Path) -> None:
        """Returns True when path is inside a git repository."""
        subprocess.run(["git", "-C", str(tmp_path), "init"], check=True, capture_output=True)

        from mem0ress.substrate.git_ops import is_git_repo

        assert is_git_repo(tmp_path) is True

    def test_returns_false_for_non_git_dir(self, tmp_path: Path) -> None:
        """Returns False when path is not a git repository."""
        from mem0ress.substrate.git_ops import is_git_repo

        assert is_git_repo(tmp_path) is False

    def test_returns_false_for_nonexistent_path(self) -> None:
        """Returns False for non-existent path."""
        from mem0ress.substrate.git_ops import is_git_repo

        assert is_git_repo(Path("/nonexistent/path")) is False


class TestGetRepoCommitId:
    """Tests for get_repo_commit_id()."""

    def test_returns_commit_hash(self, tmp_path: Path) -> None:
        """Returns short commit hash for a git repo."""
        _git_commit_empty(tmp_path)

        from mem0ress.substrate.git_ops import get_repo_commit_id

        commit_id = get_repo_commit_id(tmp_path)
        assert len(commit_id) == 7  # short hash
        assert commit_id.isalnum()

    def test_raises_for_non_git_repo(self, tmp_path: Path) -> None:
        """Raises GitError when path is not a git repository."""
        from mem0ress.substrate.git_ops import GitError, get_repo_commit_id

        with pytest.raises(GitError):
            get_repo_commit_id(tmp_path)


class TestIsRepoClean:
    """Tests for is_repo_clean()."""

    def test_returns_true_for_clean_repo(self, tmp_path: Path) -> None:
        """Returns True when repo has no uncommitted changes."""
        _git_commit_empty(tmp_path)

        from mem0ress.substrate.git_ops import is_repo_clean

        assert is_repo_clean(tmp_path) is True

    def test_returns_false_for_dirty_repo(self, tmp_path: Path) -> None:
        """Returns False when repo has uncommitted changes."""
        _git_commit_empty(tmp_path)
        # Create an uncommitted file
        (tmp_path / "uncommitted.txt").write_text("dirty state")

        from mem0ress.substrate.git_ops import is_repo_clean

        assert is_repo_clean(tmp_path) is False


class TestFindGitRepos:
    """Tests for find_git_repos()."""

    def test_finds_single_repo(self, tmp_path: Path) -> None:
        """Finds one repo at root."""
        subprocess.run(["git", "-C", str(tmp_path), "init"], check=True, capture_output=True)

        from mem0ress.substrate.git_ops import find_git_repos

        repos = find_git_repos(tmp_path)
        assert repos == [tmp_path]

    def test_finds_sibling_repos(self, tmp_path: Path) -> None:
        """Finds sibling repos at same depth level (not nested inside each other)."""
        # Create first repo at root
        _git_commit_empty(tmp_path)

        # Create a sibling repo at SAME level (parent of tmp_path)
        parent = tmp_path.parent / "sibling_repo"
        parent.mkdir(exist_ok=True)
        _git_commit_empty(parent)

        from mem0ress.substrate.git_ops import find_git_repos

        repos = find_git_repos(tmp_path.parent)
        assert tmp_path in repos
        assert parent in repos

    def test_excludes_nested_repo_inside_parent(self, tmp_path: Path) -> None:
        """Does not descend into a nested repo."""
        _git_commit_empty(tmp_path)

        # Child dir (not a repo) — should be scanned
        child_dir = tmp_path / "child_dir"
        child_dir.mkdir()

        from mem0ress.substrate.git_ops import find_git_repos

        repos = find_git_repos(tmp_path)
        assert repos == [tmp_path]

    def test_raises_for_nonexistent_root(self) -> None:
        """Raises GitError for non-existent root."""
        from mem0ress.substrate.git_ops import GitError, find_git_repos

        with pytest.raises(GitError):
            find_git_repos(Path("/nonexistent"))


class TestGetDataPlane:
    """Tests for get_data_plane()."""

    def test_returns_empty_dict_when_no_repos(self, tmp_path: Path) -> None:
        """Returns empty dict when no git repos found."""
        from mem0ress.substrate.git_ops import get_data_plane

        result = get_data_plane(tmp_path)
        assert result == {}

    def test_includes_clean_repo_commit_id(self, tmp_path: Path) -> None:
        """Includes commit ID for clean repos."""
        _git_commit_empty(tmp_path)

        from mem0ress.substrate.git_ops import get_data_plane

        result = get_data_plane(tmp_path)
        assert str(tmp_path) in result
        assert len(result[str(tmp_path)]) == 7

    def test_excludes_dirty_repo(self, tmp_path: Path) -> None:
        """Skips repos with uncommitted changes."""
        _git_commit_empty(tmp_path)
        # Make it dirty
        (tmp_path / "dirty.txt").write_text("uncommitted")

        from mem0ress.substrate.git_ops import get_data_plane

        result = get_data_plane(tmp_path)
        assert str(tmp_path) not in result


class TestGetRepoBranch:
    """Tests for get_repo_branch()."""

    def test_returns_branch_name(self, tmp_path: Path) -> None:
        """Returns current branch name."""
        _git_commit_empty(tmp_path)

        from mem0ress.substrate.git_ops import get_repo_branch

        branch = get_repo_branch(tmp_path)
        assert branch == "main"


class TestGetDirtyFiles:
    """Tests for get_dirty_files()."""

    def test_returns_empty_for_clean_repo(self, tmp_path: Path) -> None:
        """Returns empty list for clean repo."""
        _git_commit_empty(tmp_path)

        from mem0ress.substrate.git_ops import get_dirty_files

        assert get_dirty_files(tmp_path) == []

    def test_returns_modified_files(self, tmp_path: Path) -> None:
        """Returns list of dirty files."""
        _git_commit_empty(tmp_path)
        (tmp_path / "dirty.txt").write_text("uncommitted")

        from mem0ress.substrate.git_ops import get_dirty_files

        dirty = get_dirty_files(tmp_path)
        assert "dirty.txt" in dirty