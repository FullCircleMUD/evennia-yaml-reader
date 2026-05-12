# SPDX-License-Identifier: BSD-3-Clause
"""evennia-yaml-reader — source-agnostic YAML file reader.

Top-level package exports the `Reader` base, `ReaderResult`, the two concrete
implementations shipped today (`GitHubReader`, `LocalReader`), and the typed
exception hierarchy that every Reader's `read()` raises on failure.
"""

__version__ = "0.0.1"

from .base import Reader, ReaderResult
from .errors import (
    ReaderAuthError,
    ReaderError,
    ReaderNetworkError,
    ReaderNotFoundError,
    ReaderParseError,
)
from .github import GitHubReader
from .local import LocalReader

__all__ = [
    "GitHubReader",
    "LocalReader",
    "Reader",
    "ReaderAuthError",
    "ReaderError",
    "ReaderNetworkError",
    "ReaderNotFoundError",
    "ReaderParseError",
    "ReaderResult",
    "__version__",
]
