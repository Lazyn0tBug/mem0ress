"""Substrate - physical storage layer.

Exports:
- SubstrateParser: Markdown frontmatter <-> Pydantic bidirectional conversion
- get_file_hash: SHA-256 hash of file contents
- safe_write: optimistic-lock write with hash verification
- ConflictError: raised when optimistic lock fails
"""

from mem0ress.substrate.fs import ConflictError, get_file_hash, safe_write
from mem0ress.substrate.parser import SubstrateParser

__all__ = ["SubstrateParser", "ConflictError", "get_file_hash", "safe_write"]
