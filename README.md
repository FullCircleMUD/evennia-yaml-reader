# evennia-yaml-reader

A source-agnostic YAML file reader for declarative-content libraries in the [Evennia](https://www.evennia.com/) ecosystem.

The library abstracts *where the YAML lives* — local filesystem, GitHub repo, future sources — behind a uniform `Reader` interface. Consumers fetch a file by path, get back its raw bytes and parsed YAML, and dispatch on a small set of typed errors when something goes wrong.

## Status

**Foundational.** `Reader` contract + `GitHubReader` + `LocalReader` are in place, ported from [evennia-world-builder](https://github.com/FullCircleMUD/evennia-world-builder) where the pattern was first proven. 15 unit tests green. See [DESIGN/progress.md](DESIGN/progress.md) for the running milestone log.

## What's in the box

| Class | Source | Use case |
|---|---|---|
| `GitHubReader` | GitHub Contents API | Production fetch of content committed to a remote repo |
| `LocalReader` | Local filesystem tree | Dev iteration, CI / pre-commit validation, standalone tooling |

Both honour the same contract: `read(path)` returns a `ReaderResult` with `raw_bytes` and `parsed` YAML; failures raise one of `ReaderAuthError`, `ReaderNotFoundError`, `ReaderNetworkError`, or `ReaderParseError`.

```python
from evennia_yaml_reader import LocalReader

reader = LocalReader(root="/path/to/content")
result = reader.read("subfolder/file.yaml")
print(result.parsed)        # dict / list / scalar / None
print(result.raw_bytes)     # the bytes as they came back from the source
```

```python
from evennia_yaml_reader import GitHubReader

reader = GitHubReader(repo="owner/content-repo", ref="main", pat="ghp_…")
result = reader.read("subfolder/file.yaml")
```

The Reader instance is reusable — construct once per source, call `read(path)` as many times as you need.

## Is this for me?

This library is useful if you are building an Evennia-flavored library or consumer game that:

- Wants to keep YAML content in a separate repository (e.g. a content repo distinct from your gamedir).
- Wants to develop locally against a working copy of that repo and deploy from GitHub in production — without changing call sites.
- Wants typed errors (not `None` / empty defaults) when a file is missing, an auth call fails, the network blips, or the YAML is malformed.

If you only ever read YAML from one location with one auth model, `open(path) + yaml.safe_load(...)` is fine and you do not need this library.

## Install

The package is not on PyPI yet. Install directly from git:

```
pip install git+https://github.com/FullCircleMUD/evennia-yaml-reader.git@main
```

Editable install for development against a checkout:

```
git clone https://github.com/FullCircleMUD/evennia-yaml-reader.git
cd evennia-yaml-reader
python -m venv venv
# Activate the venv (platform-specific)
pip install -e .
python runtests.py
```

## Learn more

- **[CLAUDE.md](CLAUDE.md)** — load-bearing principles and orientation for working in the repository.
- **[DESIGN/INDEX.md](DESIGN/INDEX.md)** — index of design documents.
- **[DESIGN/reader-api.md](DESIGN/reader-api.md)** — the architectural decisions behind the `Reader` contract.
- **[src/evennia_yaml_reader/base.md](src/evennia_yaml_reader/base.md)** — `Reader` and `ReaderResult` reference, co-located with the code.

## License

BSD 3-Clause. See [LICENSE](LICENSE).
