# SPDX-License-Identifier: BSD-3-Clause
"""GitHubReader — fetches a YAML file from a (private or public) GitHub repo.

Uses the GitHub Contents API with ``Accept: application/vnd.github.raw``
to get the raw file body in one hop. Authenticates via Bearer token
(works for both classic and fine-grained PATs).
"""
import urllib.error
import urllib.parse
import urllib.request

import yaml

from .base import Reader, ReaderResult
from .errors import (
    ReaderAuthError,
    ReaderNetworkError,
    ReaderNotFoundError,
    ReaderParseError,
)


_USER_AGENT = "evennia-yaml-reader"
_GITHUB_API_VERSION = "2022-11-28"
_REQUEST_TIMEOUT_SECONDS = 10


class GitHubReader(Reader):
    """Reader for the GitHub Contents API.

    Construction kwargs (all required, all keyword-only):
        repo: owner/name slug (e.g. ``"FullCircleMUD/fcm-world"``).
        ref:  branch, tag, or commit SHA.
        pat:  GitHub Personal Access Token with read access to the repo.

    The path within the repo is supplied per-read via ``read(path)``.

    Raises (from read()):
        ReaderAuthError:     HTTP 401 — PAT rejected; or HTTP 403 where the
                             rate limit is not exhausted (PAT scope).
        ReaderNotFoundError: HTTP 404 — repo, ref, or path not found.
        ReaderNetworkError:  HTTP 403 with the rate limit exhausted, any other
                             non-401/404 status, or a network failure.
        ReaderParseError:    YAML or UTF-8 decode failure.
    """

    required_kwargs = ("repo", "ref", "pat")

    def __init__(self, *, repo, ref, pat):
        self.repo = repo
        self.ref = ref
        self.pat = pat

    def read(self, path: str) -> ReaderResult:
        # `path` is a plain path, never pre-encoded — the same string is handed
        # to LocalReader, which opens it literally. Escaping is this reader's
        # job because it is the one building a URL. `/` stays safe so the
        # segment structure survives; without the escape a `#` or `?` in a
        # filename truncates the path and takes `ref` with it.
        quoted_path = urllib.parse.quote(path, safe="/")
        url = (
            f"https://api.github.com/repos/{self.repo}"
            f"/contents/{quoted_path}?ref={self.ref}"
        )
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self.pat}",
                "Accept": "application/vnd.github.raw",
                "X-GitHub-Api-Version": _GITHUB_API_VERSION,
                "User-Agent": _USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(
                request, timeout=_REQUEST_TIMEOUT_SECONDS
            ) as response:
                raw_bytes = response.read()
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise ReaderAuthError(
                    f"GitHub auth failed (401) for {self.repo}@{self.ref}:{path}"
                ) from e
            if e.code == 403:
                # GitHub returns 403 both for rate-limiting and for a PAT
                # lacking the required scope. Only the first is retryable, and
                # the remaining-quota header is what tells them apart — so the
                # two land in different exception types and the consumer can
                # dispatch on "can retrying help?" without matching strings.
                remaining = (e.headers or {}).get("x-ratelimit-remaining")
                if remaining == "0":
                    raise ReaderNetworkError(
                        f"GitHub rate limit exceeded (403) for "
                        f"{self.repo}@{self.ref}:{path}"
                    ) from e
                raise ReaderAuthError(
                    f"GitHub denied access (403) for {self.repo}@{self.ref}:{path}"
                    f" — check the PAT's scope for this repository"
                ) from e
            if e.code == 404:
                raise ReaderNotFoundError(
                    f"Not found (404) for {self.repo}@{self.ref}:{path}"
                ) from e
            raise ReaderNetworkError(f"HTTP {e.code}: {e.reason}") from e
        except urllib.error.URLError as e:
            raise ReaderNetworkError(f"Network error: {e.reason}") from e

        try:
            parsed = yaml.safe_load(raw_bytes)
        except yaml.YAMLError as e:
            raise ReaderParseError(str(e)) from e

        return ReaderResult(raw_bytes=raw_bytes, parsed=parsed)
