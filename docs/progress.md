# Progress

Running log of milestones with links to evidence. Reverse chronological — newest first.

## 2026-05-12 (latest)

- **Readers ported from `evennia-world-builder`.** `Reader`, `ReaderResult`, `GitHubReader`, `LocalReader`, and the five-class typed exception hierarchy (`ReaderError`, `ReaderAuthError`, `ReaderNotFoundError`, `ReaderNetworkError`, `ReaderParseError`) are in place. Flat package layout — no `readers/` subfolder; the whole library is the Reader. Consumers import directly from `evennia_yaml_reader`. **15 tests green** (1 smoke + 7 `GitHubReader` + 7 `LocalReader`) via stdlib `unittest` through `runtests.py`.

  Substantive differences from world-builder's version: no settings-based dispatch (consumer concern), no `get_reader_class()` helper (consumer concern), `_USER_AGENT` in `GitHubReader` flipped to `"evennia-yaml-reader"`. Otherwise verbatim. Co-located [base.md](../src/evennia_yaml_reader/base.md) carried over as the reference doc for `Reader` and `ReaderResult`.

  Design captured in [reader-api.md](reader-api.md) — port of world-builder's equivalent doc with the consumer-concern bits stripped out and the provenance note added.

- **Repository bootstrapped.** LIBRARY_STANDARDS scaffold in place: `pyproject.toml`, `runtests.py`, `src/evennia_yaml_reader/__init__.py` (version 0.0.1), smoke test, `CLAUDE.md`, `README.md`, `docs/INDEX.md`, `docs/progress.md`, `docs/documentation-structure.md`, `docs/archive/`. The library is pure-Python (no Evennia / Django coupling) — a deliberate divergence from LIBRARY_STANDARDS captured in CLAUDE.md principle 5.

  Decision context: the extraction was discussed and agreed because more declarative-content libraries are planned (e.g. [evennia-mob-spawner](https://github.com/FullCircleMUD/evennia-mob-spawner)), each of which would otherwise duplicate the Reader. With three or more consumers anticipated, library overhead amortises and a single source-of-truth for the Reader pattern becomes the cheaper option.
