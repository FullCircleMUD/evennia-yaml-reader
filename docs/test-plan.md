# Test plan

Every test case the library commits to covering, and the test function that covers it. The **Test
function** column is the auditable trail — it is filled in as each test is written, so an empty cell
means the case is agreed but not yet covered.

Case IDs are stable and referenceable. Do not renumber; retire an ID rather than reuse it.

All test functions live in `src/evennia_yaml_reader/tests.py` and run via `python runtests.py`
(pure stdlib `unittest` — see CLAUDE.md principle 5).

| Prefix | Covers |
|---|---|
| `PK` | Package surface — version, exports |
| `RD` | `Reader` / `ReaderResult` contract |
| `GH` | `GitHubReader` |
| `LR` | `LocalReader` |

## Fixtures

The suite needs no Evennia, no Django and no database. Remote reads are mocked at `urlopen`; local
reads run against a real temp directory.

| Fixture | Purpose |
|---|---|
| `GitHubReaderTest.KWARGS` / `.PATH` | Fixed construction kwargs (`owner/repo`, `main`, `ghp_test`) and read path, so URL and header assertions have known expected values |
| `_response_with_payload(bytes)` | `MagicMock` honouring the context-manager protocol that `urlopen()` is used under, returning a chosen payload from `.read()` |
| `urllib.error.HTTPError(...)` / `URLError(...)` | Raised as `urlopen` side effects to drive each error branch |
| `tempfile.TemporaryDirectory` (per-test, `addCleanup`) | Real filesystem root for `LocalReader` |
| `_write(path, content)` | Writes a fixture file under the temp root, creating parent directories |

## PK — package surface

| ID | Case | Test function |
|---|---|---|
| PK-01 | `__version__` is present and matches the released value | `PackageSmokeTest.test_version_present` |

## RD — `Reader` / `ReaderResult` contract

The base class carries no behaviour, so it has no direct tests — the contract is exercised only
through the concrete readers. `Reader.read()`'s `NotImplementedError` branch is deliberately untested;
asserting it would be a tautology. See [../src/evennia_yaml_reader/base.md](../src/evennia_yaml_reader/base.md).

| ID | Case | Test function |
|---|---|---|
| RD-01 | A successful read returns a `ReaderResult` carrying both `raw_bytes` and `parsed` | `GitHubReaderTest.test_happy_path_returns_raw_and_parsed`, `LocalReaderTest.test_happy_path_returns_raw_and_parsed` |
| RD-02 | Each concrete reader declares its own `required_kwargs`, overriding the empty base default | `GitHubReaderTest.test_required_kwargs_declared`, `LocalReaderTest.test_required_kwargs_declared` |
| RD-03 | An empty document is a successful read with `parsed is None` — not a failure. Whether empty content is meaningful is the consumer's judgement, not the reader's | `LocalReaderTest.test_empty_document_reads_as_none` |
| RD-04 | `ReaderResult` is frozen — assigning to a field after construction raises | `ReaderContractTest.test_reader_result_is_frozen` |
| RD-05 | All four typed errors subclass `ReaderError`, so a consumer catching the base catches every reader failure | `ReaderContractTest.test_all_errors_subclass_reader_error` |

## GH — `GitHubReader(repo, ref, pat).read(path)`

| ID | Case | Test function |
|---|---|---|
| GH-01 | `required_kwargs` is `("repo", "ref", "pat")` | `GitHubReaderTest.test_required_kwargs_declared` |
| GH-02 | Happy path returns the raw bytes and the parsed structure | `GitHubReaderTest.test_happy_path_returns_raw_and_parsed` |
| GH-03 | The request targets the Contents API path with `ref=`, and carries the Bearer token, raw `Accept`, API version and User-Agent headers | `GitHubReaderTest.test_request_url_and_headers` |
| GH-04 | HTTP 401 raises `ReaderAuthError` | `GitHubReaderTest.test_401_raises_auth_error` |
| GH-05 | HTTP 404 raises `ReaderNotFoundError` | `GitHubReaderTest.test_404_raises_not_found_error` |
| GH-06 | A `URLError` (DNS, refused, timeout) raises `ReaderNetworkError` | `GitHubReaderTest.test_url_error_raises_network_error` |
| GH-07 | Unparseable YAML raises `ReaderParseError` | `GitHubReaderTest.test_bad_yaml_raises_parse_error` |
| GH-08 | HTTP 403 with `x-ratelimit-remaining: 0` raises `ReaderNetworkError` — rate-limited, so retrying can help | `GitHubReaderTest.test_403_rate_limited_raises_network_error` |
| GH-09 | HTTP 403 with quota remaining raises `ReaderAuthError` — a PAT scope problem, so retrying cannot help | `GitHubReaderTest.test_403_with_quota_remaining_raises_auth_error` |
| GH-10 | Any other HTTP status (e.g. 500) raises `ReaderNetworkError` carrying the status | `GitHubReaderTest.test_other_http_status_raises_network_error` |
| GH-11 | Bytes that are not decodable as UTF-8 raise `ReaderParseError` | `GitHubReaderTest.test_undecodable_bytes_raise_parse_error` |
| GH-12 | A `#` or `?` in the path is escaped, so the path reaches GitHub intact and `ref` is not lost to a fragment or a junk query | `GitHubReaderTest.test_url_delimiters_in_path_are_escaped` |
| GH-13 | A space and non-ASCII characters are percent-encoded | `GitHubReaderTest.test_space_and_non_ascii_in_path_are_escaped` |
| GH-14 | `/` is not escaped — path segments survive as segments | `GitHubReaderTest.test_path_separators_are_not_escaped` |
| GH-15 | An ordinary ASCII path is unchanged by the escaping | `GitHubReaderTest.test_ordinary_path_is_unchanged_by_escaping` |

GH-12 is the case with teeth: unescaped, everything after a `#` becomes a URL fragment and is never
sent, so the reader silently queries the repo's default branch instead of the configured `ref`.

GH-08 and GH-09 exist because GitHub returns 403 for both rate-limiting and an under-scoped PAT, and
the response header is the only thing that separates them. Splitting them across the two exception
types lets a consumer answer "can retrying help?" by type rather than by matching the message string.

## LR — `LocalReader(root).read(path)`

| ID | Case | Test function |
|---|---|---|
| LR-01 | `required_kwargs` is `("root",)` | `LocalReaderTest.test_required_kwargs_declared` |
| LR-02 | Happy path returns the raw bytes and the parsed structure | `LocalReaderTest.test_happy_path_returns_raw_and_parsed` |
| LR-03 | A nested path resolves relative to `root` | `LocalReaderTest.test_nested_path_resolves` |
| LR-04 | A missing file raises `ReaderNotFoundError` | `LocalReaderTest.test_missing_file_raises_not_found` |
| LR-05 | Unparseable YAML raises `ReaderParseError` | `LocalReaderTest.test_bad_yaml_raises_parse_error` |
| LR-06 | A `../` path resolving outside `root` raises `ReaderNotFoundError` rather than reading the file | `LocalReaderTest.test_path_traversal_blocked` |
| LR-07 | `root` accepts a string as well as a `Path` — consumers pass a settings value | `LocalReaderTest.test_root_accepts_string_path` |
| LR-08 | An absolute path raises `ReaderNotFoundError` — `root / "/abs"` discards the root in pathlib, so this escapes by a different mechanism to LR-06 | `LocalReaderTest.test_absolute_path_blocked` |
| LR-09 | A symlink inside `root` pointing outside it raises `ReaderNotFoundError` — `resolve()` follows the link before the guard runs | `LocalReaderTest.test_symlink_escaping_root_blocked` |
| LR-10 | A file the OS refuses to open raises `ReaderAuthError` | `LocalReaderTest.test_permission_denied_raises_auth_error` |
| LR-11 | A path naming a directory raises `ReaderNetworkError`, with the OS's own cause in the message | `LocalReaderTest.test_directory_path_raises_network_error` |
| LR-12 | Bytes that are not decodable as UTF-8 raise `ReaderParseError` | `LocalReaderTest.test_undecodable_bytes_raise_parse_error` |

LR-06, LR-08 and LR-09 are three routes past the same guard, kept as separate cases so removing the
guard cannot pass by satisfying one of them. LR-10 and LR-11 record that a file the reader cannot open
raises rather than returning empty — the reader has one job, and failing it is never a silent success.

## Settled

- **`path` is a plain path, never pre-encoded; each reader escapes for its own backend.** The same
  string must work against every reader, and `LocalReader` opens it literally — so the consumer cannot
  encode it. `GitHubReader` percent-encodes when it builds the URL (GH-12 … GH-15).
- **Typed errors carry the retry decision.** A consumer answers "can retrying help?" from the
  exception type, never by matching a message string — which is why a GitHub 403 splits across
  `ReaderNetworkError` and `ReaderAuthError` on the rate-limit header (GH-08, GH-09).
- **A read that cannot be completed raises; it never returns empty.** Missing, unreadable, blocked and
  unparseable all raise (LR-04, LR-06, LR-08 … LR-12). An empty *document*, by contrast, is a
  successful read (RD-03) — whether empty content means anything is the consumer's judgement.
