"""Storage layer with optimistic locking - ConflictError, get_file_hash, safe_write."""

import hashlib
import hmac
from pathlib import Path


class ConflictError(Exception):
    """Optimistic lock failure - file was modified since last read."""


def get_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file contents.

    Args:
        file_path: Path to file

    Returns:
        SHA-256 hex string of file contents
    """
    content = file_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def safe_write(file_path: Path, content: str, expected_hash: str) -> None:
    """Write file with optimistic lock check.

    If expected_hash is provided and file exists, verifies the current hash
    matches before writing. Uses constant-time comparison to prevent timing attacks.

    Args:
        file_path: Path to file to write
        content: Content to write
        expected_hash: Expected current hash (if file exists)

    Raises:
        ConflictError: If file exists and hash does not match expected_hash
        FileNotFoundError: If parent directory does not exist
    """
    # If file exists, check hash
    if file_path.exists():
        current_hash = get_file_hash(file_path)
        if not hmac.compare_digest(current_hash, expected_hash):
            raise ConflictError(
                f"409 Conflict: 文件已被修改\n"
                f"期望 Hash: {expected_hash}\n"
                f"实际 Hash: {current_hash}\n"
                f"请更新后重试！"
            )

    # Write content
    file_path.write_text(content, encoding="utf-8")
