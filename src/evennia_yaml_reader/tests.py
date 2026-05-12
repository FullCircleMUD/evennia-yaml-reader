# SPDX-License-Identifier: BSD-3-Clause
"""Tests for evennia-yaml-reader.

Verifies the package is importable, the Reader contract is honoured by
GitHubReader against a mocked urllib, and LocalReader operates against
real temp-directory fixtures. Pure stdlib unittest — no Django, no Evennia.
"""
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import evennia_yaml_reader
from evennia_yaml_reader import (
    GitHubReader,
    LocalReader,
    ReaderAuthError,
    ReaderNetworkError,
    ReaderNotFoundError,
    ReaderParseError,
    ReaderResult,
)


class PackageSmokeTest(unittest.TestCase):
    """Sanity check that the package is importable and versioned."""

    def test_version_present(self):
        self.assertEqual(evennia_yaml_reader.__version__, "0.0.1")


class GitHubReaderTest(unittest.TestCase):
    """Verify GitHubReader.read() against a mocked urllib."""

    KWARGS = {
        "repo": "owner/repo",
        "ref": "main",
        "pat": "ghp_test",
    }
    PATH = "file.yaml"

    def _response_with_payload(self, payload: bytes) -> MagicMock:
        """Build a context-manager-protocol-supporting mock for urlopen()."""
        mock_response = MagicMock()
        mock_response.__enter__.return_value.read.return_value = payload
        return mock_response

    def test_required_kwargs_declared(self):
        self.assertEqual(GitHubReader.required_kwargs, ("repo", "ref", "pat"))

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_happy_path_returns_raw_and_parsed(self, mock_urlopen):
        mock_urlopen.return_value = self._response_with_payload(b"key: value\n")
        result = GitHubReader(**self.KWARGS).read(self.PATH)
        self.assertIsInstance(result, ReaderResult)
        self.assertEqual(result.raw_bytes, b"key: value\n")
        self.assertEqual(result.parsed, {"key": "value"})

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_request_url_and_headers(self, mock_urlopen):
        mock_urlopen.return_value = self._response_with_payload(b"x: 1\n")
        GitHubReader(**self.KWARGS).read(self.PATH)
        request = mock_urlopen.call_args[0][0]
        self.assertIn("/repos/owner/repo/contents/file.yaml", request.full_url)
        self.assertIn("ref=main", request.full_url)
        # urllib.request.Request normalises header keys via .capitalize();
        # compare via a lowercased view to stay robust against that.
        headers_lower = {k.lower(): v for k, v in request.header_items()}
        self.assertEqual(headers_lower["authorization"], "Bearer ghp_test")
        self.assertEqual(headers_lower["accept"], "application/vnd.github.raw")
        self.assertEqual(headers_lower["x-github-api-version"], "2022-11-28")
        self.assertEqual(headers_lower["user-agent"], "evennia-yaml-reader")

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_401_raises_auth_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "url", 401, "Unauthorized", {}, None
        )
        with self.assertRaises(ReaderAuthError):
            GitHubReader(**self.KWARGS).read(self.PATH)

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_404_raises_not_found_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "url", 404, "Not Found", {}, None
        )
        with self.assertRaises(ReaderNotFoundError):
            GitHubReader(**self.KWARGS).read(self.PATH)

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_url_error_raises_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("nodename nor servname")
        with self.assertRaises(ReaderNetworkError):
            GitHubReader(**self.KWARGS).read(self.PATH)

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_bad_yaml_raises_parse_error(self, mock_urlopen):
        mock_urlopen.return_value = self._response_with_payload(b":::not yaml\n: : :")
        with self.assertRaises(ReaderParseError):
            GitHubReader(**self.KWARGS).read(self.PATH)


class LocalReaderTest(unittest.TestCase):
    """Verify LocalReader.read() against real temp-directory fixtures."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _write(self, path: str, content: bytes) -> Path:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def test_required_kwargs_declared(self):
        self.assertEqual(LocalReader.required_kwargs, ("root",))

    def test_happy_path_returns_raw_and_parsed(self):
        self._write("hello.yaml", b"key: value\n")
        result = LocalReader(root=self.root).read("hello.yaml")
        self.assertIsInstance(result, ReaderResult)
        self.assertEqual(result.raw_bytes, b"key: value\n")
        self.assertEqual(result.parsed, {"key": "value"})

    def test_nested_path_resolves(self):
        self._write("subfolder/inner.yaml", b"name: B\nid: 1\n")
        result = LocalReader(root=self.root).read("subfolder/inner.yaml")
        self.assertEqual(result.parsed, {"name": "B", "id": 1})

    def test_missing_file_raises_not_found(self):
        with self.assertRaises(ReaderNotFoundError):
            LocalReader(root=self.root).read("ghost.yaml")

    def test_bad_yaml_raises_parse_error(self):
        self._write("bad.yaml", b":::not yaml\n: : :")
        with self.assertRaises(ReaderParseError):
            LocalReader(root=self.root).read("bad.yaml")

    def test_path_traversal_blocked(self):
        # An "escape" path resolves outside root and must be rejected
        # rather than reading whatever happens to be on disk above root.
        with self.assertRaises(ReaderNotFoundError):
            LocalReader(root=self.root).read("../../etc/passwd")

    def test_root_accepts_string_path(self):
        # Many consumers will pass a settings string, not a Path.
        self._write("hello.yaml", b"k: v\n")
        result = LocalReader(root=str(self.root)).read("hello.yaml")
        self.assertEqual(result.parsed, {"k": "v"})


if __name__ == "__main__":
    unittest.main()
