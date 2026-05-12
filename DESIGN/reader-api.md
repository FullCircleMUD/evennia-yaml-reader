# Reader API

The library's load-bearing contract: a `Reader` is a configured connection to a content source (a GitHub repo, a local filesystem tree, future sources). Construction kwargs are reader-specific (auth, source identity); `path` is supplied per-read as the query against that source. `read(path)` returns a `ReaderResult` carrying both raw bytes and parsed YAML. Concrete subclasses determine the source.

This document captures the *why* behind the contract. The contract itself is specified at [../src/evennia_yaml_reader/base.md](../src/evennia_yaml_reader/base.md), co-located with [base.py](../src/evennia_yaml_reader/base.py).

## Shipped readers

| Class | Source | Construction kwargs | Use case |
|---|---|---|---|
| `GitHubReader` | GitHub Contents API | `repo`, `ref`, `pat` | Production fetch of content committed to a remote repo |
| `LocalReader` | Local filesystem tree | `root` | Dev iteration, CI / pre-commit validation, standalone tooling |

Both implementations use the same downstream-visible contract: `ReaderResult` shape, typed exceptions, `required_kwargs` advertisement. A consuming library iterates locally with `LocalReader` against a checkout; the same content goes through `GitHubReader` once committed. No code path changes in the consumer — only the configured reader.

## Decisions

- **Strategy pattern, not ABC.** `Reader` is a plain base class with `read()` raising `NotImplementedError`. Duck-typed; matches the convention used in `evennia-shards` and `evennia-world-builder`. ABCs add ceremony (`@abstractmethod`, the `abc` import, MRO subtleties) that buys nothing here — the contract is small, the failure mode is loud, and subclasses are easy to spot.
- **Kwargs are consumer-side.** The library does not dictate setting names or how the consumer wires construction. Each consuming library (or its consumer game) names its own settings keys and constructs the appropriate Reader with whatever kwargs that Reader's `required_kwargs` declares. Dispatch is a consumer concern, not a library concern.
- **`ReaderResult` dataclass holds both raw bytes and parsed value.** Preserves observability for diagnostics — change-detection hashes, "show me exactly what the server sent" debugging surfaces — without forcing every caller to choose ahead of fetch which form they want. Frozen, by convention; downstream code that needs to transform the parsed structure copies it.
- **Typed exceptions, never silent defaults.** `ReaderError` base + `ReaderAuthError` / `ReaderNotFoundError` / `ReaderNetworkError` / `ReaderParseError` subtypes. Consumers dispatch on type semantically rather than parsing error messages or checking sentinel return values. UTF-8 decode failures fold into `ReaderParseError` (degenerate parse case) — they look the same as bad YAML to the consumer, which is correct: both mean "the bytes arrived but cannot be interpreted as a YAML document."
- **No `get_reader(**kwargs)` helper, no settings dispatch.** Both belong to the consuming library. The library exposes Reader classes; the consumer is responsible for choosing one and constructing it. Adding dispatch here would couple this library to whichever settings convention a specific consumer uses, which is the opposite of source-agnostic.
- **Flat package layout.** `base.py`, `github.py`, `local.py`, `errors.py` all live at the package root. The whole library is the Reader; nesting them under a `readers/` subfolder would be over-organisation. Consumers import as `from evennia_yaml_reader import GitHubReader` — short and obvious.
- **Discoverability via `required_kwargs`.** Each Reader subclass declares a `required_kwargs` class attribute (a tuple of strings) listing the keyword arguments its `__init__` accepts. A consuming library can introspect `ReaderClass.required_kwargs` rather than reading docstrings, and can validate that its settings actually cover what the chosen Reader needs before any I/O fires. Default on the base `Reader` is `()`. `path` is deliberately **not** a construction kwarg — it is supplied per-read as the query.
- **`path` is per-read, not construction-time.** A Reader instance is reusable across many `read(path)` calls against the same source. This matters for any consumer that fetches multiple files (a manifest tree, a set of rule files, a definitions document plus its referenced content) — they configure one Reader once and reuse it.
- **No retry, caching, or close() in the contract.** Each is an orthogonal concern that belongs in a consumer-built wrapper or middleware, not in the base. A Reader that retries internally couples policy with mechanism in a way that's hard to override; a consumer that wants retry semantics implements them as a decorating Reader, leaving the underlying contract clean.
- **`path` is `str`, not `Path`.** The contract is platform-neutral and works against backends where filesystem paths aren't meaningful (HTTP URLs, S3 keys). A backend that wants `pathlib.Path` semantics converts at its own boundary (as `LocalReader` does internally).

## Provenance

This contract was first proven inside [evennia-world-builder](https://github.com/FullCircleMUD/evennia-world-builder), where the Reader pattern shipped as part of that library's pipeline. Extraction into a standalone library happened once a second consumer ([evennia-mob-spawner](https://github.com/FullCircleMUD/evennia-mob-spawner)) and the prospect of more declarative-content libraries (quests, recipes, …) made duplicating the Reader the worse trade-off than sharing it. See [progress.md](progress.md) for the milestone log.

The library/consumer boundary that the original spike left open ("who owns the credentials, dispatch, and settings naming?") resolves as:

- **This library owns:** fetch, parse, error mapping, the typed exception hierarchy, `required_kwargs` advertisement.
- **Consumer owns:** credential storage, Reader selection, construction kwargs, settings naming. Each consuming library defines its own dispatch convention (e.g. `WORLDBUILDER_READER` / `WORLDBUILDER_READER_KWARGS` in world-builder).

## Test approach

Unit tests in [../src/evennia_yaml_reader/tests.py](../src/evennia_yaml_reader/tests.py):

- **`GitHubReaderTest`** — mocks `urllib.request.urlopen` via `unittest.mock.patch`. Covers happy path (raw + parsed return, URL/header construction including `User-Agent`), four error paths (401, 404, network, bad YAML), and `required_kwargs` declaration.
- **`LocalReaderTest`** — uses `tempfile.TemporaryDirectory` for real-filesystem fixtures. Covers happy path (single + nested paths), missing-file + bad-YAML error paths, path-traversal guard (escape attempts via `..` resolve outside `root` and are rejected as not-found), and string-vs-`Path` root acceptance.
- **`PackageSmokeTest`** — minimal sanity that the package is importable and versioned.

Tests run via pure stdlib `unittest` through [../runtests.py](../runtests.py). No Django, no Evennia bootstrap — see CLAUDE.md principle 5 for the rationale.

## Future Readers

Out of scope for v0; captured here so a future contributor knows the boundary:

- **`S3Reader`** — Contents API equivalent for AWS S3 / S3-compatible stores. Construction kwargs likely `bucket`, `prefix`, `credentials_chain`.
- **`GitLabReader`** / **`GiteaReader`** — same shape as `GitHubReader` against alternative hosted-git platforms.
- **`HTTPReader`** — generic HTTPS endpoint for content served outside a git platform (a CDN, a static-site fileserver).
- **`PackageReader`** — read content shipped inside a Python package's `package_data`, useful for distributing example content with a consuming library.

Each is a straightforward addition: subclass `Reader`, declare `required_kwargs`, implement `read()`, translate backend errors to the typed hierarchy. None of these are committed; they are documented to make the boundary obvious — a Reader is whatever fetches bytes from a configured source.
