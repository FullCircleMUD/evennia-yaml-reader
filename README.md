# evennia-yaml-reader

A source-agnostic YAML file reader for declarative-content libraries in the [Evennia](https://www.evennia.com/) ecosystem.

The library abstracts *where the YAML lives* — local filesystem, GitHub repo, future sources — behind a uniform `Reader` interface. Consumers fetch a file by path, get back its raw bytes and parsed YAML, and dispatch on a small set of typed errors when something goes wrong.

## Status

**Pre-foundation.** Repository scaffold is in place; Reader implementations to be extracted from [evennia-world-builder](https://github.com/FullCircleMUD/evennia-world-builder), where the pattern was first proven. See [DESIGN/progress.md](DESIGN/progress.md) for the running milestone log.

## Is this for me?

This library is useful if you are building an Evennia-flavored library or consumer game that:

- Wants to keep YAML content in a separate repository (e.g. a content repo distinct from your gamedir).
- Wants to develop locally against a working-copy of that repo and deploy from GitHub in production.
- Wants typed errors (not None / empty defaults) when a file is missing, an auth call fails, the network blips, or the YAML is malformed.

If you only ever read YAML from one location with one auth model, `open(path) + yaml.safe_load(...)` is fine and you do not need this library.

## Install

The package is not on PyPI yet. Install directly from git:

```
pip install git+https://github.com/FullCircleMUD/evennia-yaml-reader.git@main
```

## Learn more

- **[CLAUDE.md](CLAUDE.md)** — load-bearing principles and orientation for working in the repository.
- **[DESIGN/INDEX.md](DESIGN/INDEX.md)** — index of design documents.

## License

BSD 3-Clause. See [LICENSE](LICENSE).
