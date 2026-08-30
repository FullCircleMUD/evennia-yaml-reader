# SPDX-License-Identifier: BSD-3-Clause
"""Tests for evennia-yaml-reader.

Verifies the package is importable, the Reader contract is honoured by
GitHubReader against a mocked urllib, and LocalReader operates against
real temp-directory fixtures. Pure stdlib unittest — no Django, no Evennia.
"""
import dataclasses
import email
import os
import tempfile
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from unittest.mock import MagicMock, patch

import evennia_yaml_reader
from evennia_yaml_reader import (
    GitHubReader,
    LocalReader,
    ReaderAuthError,
    ReaderError,
    ReaderNetworkError,
    ReaderNotFoundError,
    ReaderParseError,
    ReaderResult,
)

# Not decodable as UTF-8; PyYAML surfaces it as a yaml.reader.ReaderError.
UNDECODABLE_BYTES = b"key: caf\xe9\n"


class PackageSmokeTest(unittest.TestCase):
    """Sanity check that the package is importable and versioned."""

    def test_version_present(self):
        self.assertEqual(evennia_yaml_reader.__version__, "0.1.0")


class ReaderContractTest(unittest.TestCase):
    """Contract guarantees that hold across every Reader implementation."""

    def test_reader_result_is_frozen(self):
        result = ReaderResult(raw_bytes=b"k: v\n", parsed={"k": "v"})
        with self.assertRaises(dataclasses.FrozenInstanceError):
            result.parsed = {"k": "other"}

    def test_all_errors_subclass_reader_error(self):
        # A consumer catching the base must catch every reader failure.
        for error_type in (
            ReaderAuthError,
            ReaderNetworkError,
            ReaderNotFoundError,
            ReaderParseError,
        ):
            with self.subTest(error_type=error_type.__name__):
                self.assertTrue(issubclass(error_type, ReaderError))


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

    def _requested_url(self, mock_urlopen, path: str) -> urllib.parse.SplitResult:
        """Read the URL the reader actually built, split into its parts."""
        mock_urlopen.return_value = self._response_with_payload(b"x: 1\n")
        GitHubReader(**self.KWARGS).read(path)
        return urllib.parse.urlsplit(mock_urlopen.call_args[0][0].full_url)

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_url_delimiters_in_path_are_escaped(self, mock_urlopen):
        # Unescaped, everything after a "#" becomes a fragment and is never
        # sent — the ref goes with it and GitHub answers from the default
        # branch. A "?" corrupts the query the same way.
        for path, expected in (
            ("notes#1.yaml", "/repos/owner/repo/contents/notes%231.yaml"),
            ("notes?1.yaml", "/repos/owner/repo/contents/notes%3F1.yaml"),
        ):
            with self.subTest(path=path):
                split = self._requested_url(mock_urlopen, path)
                self.assertEqual(split.path, expected)
                self.assertEqual(split.query, "ref=main")
                self.assertEqual(split.fragment, "")

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_space_and_non_ascii_in_path_are_escaped(self, mock_urlopen):
        split = self._requested_url(mock_urlopen, "dark forest/café.yaml")
        self.assertEqual(
            split.path, "/repos/owner/repo/contents/dark%20forest/caf%C3%A9.yaml"
        )
        self.assertEqual(split.query, "ref=main")

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_path_separators_are_not_escaped(self, mock_urlopen):
        split = self._requested_url(mock_urlopen, "areas/town/rooms.yaml")
        self.assertEqual(split.path, "/repos/owner/repo/contents/areas/town/rooms.yaml")

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_ordinary_path_is_unchanged_by_escaping(self, mock_urlopen):
        # Escaping must be a no-op for every path that already worked.
        split = self._requested_url(mock_urlopen, "rooms/tavern.yaml")
        self.assertEqual(split.path, "/repos/owner/repo/contents/rooms/tavern.yaml")

    def _http_error(self, code: str, reason: str, headers: str = "") -> urllib.error.HTTPError:
        """Build an HTTPError whose .headers behave like a real response's."""
        return urllib.error.HTTPError(
            "url", code, reason, email.message_from_string(headers), None
        )

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_403_rate_limited_raises_network_error(self, mock_urlopen):
        # Quota exhausted — transient, so the consumer may retry.
        mock_urlopen.side_effect = self._http_error(
            403, "rate limit exceeded", "X-RateLimit-Remaining: 0\n"
        )
        with self.assertRaises(ReaderNetworkError):
            GitHubReader(**self.KWARGS).read(self.PATH)

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_403_with_quota_remaining_raises_auth_error(self, mock_urlopen):
        # Not rate-limited, so the PAT lacks scope — retrying cannot help.
        mock_urlopen.side_effect = self._http_error(
            403, "Forbidden", "X-RateLimit-Remaining: 4999\n"
        )
        with self.assertRaises(ReaderAuthError):
            GitHubReader(**self.KWARGS).read(self.PATH)

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_other_http_status_raises_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = self._http_error(500, "Internal Server Error")
        with self.assertRaises(ReaderNetworkError) as caught:
            GitHubReader(**self.KWARGS).read(self.PATH)
        self.assertIn("500", str(caught.exception))

    @patch("evennia_yaml_reader.github.urllib.request.urlopen")
    def test_undecodable_bytes_raise_parse_error(self, mock_urlopen):
        mock_urlopen.return_value = self._response_with_payload(UNDECODABLE_BYTES)
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

    def test_absolute_path_blocked(self):
        # root / "/abs" discards root in pathlib — a different escape route
        # to the "../" one, past the same guard.
        with self.assertRaises(ReaderNotFoundError):
            LocalReader(root=self.root).read("/etc/passwd")

    def test_symlink_escaping_root_blocked(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        secret = Path(outside.name) / "secret.yaml"
        secret.write_bytes(b"secret: true\n")
        (self.root / "link.yaml").symlink_to(secret)

        with self.assertRaises(ReaderNotFoundError):
            LocalReader(root=self.root).read("link.yaml")

    @unittest.skipIf(
        hasattr(os, "geteuid") and os.geteuid() == 0,
        "root bypasses filesystem permissions",
    )
    def test_permission_denied_raises_auth_error(self):
        target = self._write("locked.yaml", b"k: v\n")
        target.chmod(0o000)
        self.addCleanup(target.chmod, 0o600)
        with self.assertRaises(ReaderAuthError):
            LocalReader(root=self.root).read("locked.yaml")

    def test_directory_path_raises_network_error(self):
        (self.root / "subfolder").mkdir()
        with self.assertRaises(ReaderNetworkError) as caught:
            LocalReader(root=self.root).read("subfolder")
        # The OS's own wording carries the cause through to the consumer.
        self.assertIn("directory", str(caught.exception).lower())

    def test_undecodable_bytes_raise_parse_error(self):
        self._write("latin1.yaml", UNDECODABLE_BYTES)
        with self.assertRaises(ReaderParseError):
            LocalReader(root=self.root).read("latin1.yaml")

    def test_empty_document_reads_as_none(self):
        # Empty is a successful read, not a failure — whether it means
        # anything is the consumer's call.
        self._write("empty.yaml", b"")
        result = LocalReader(root=self.root).read("empty.yaml")
        self.assertEqual(result.raw_bytes, b"")
        self.assertIsNone(result.parsed)


if __name__ == "__main__":
    unittest.main()
