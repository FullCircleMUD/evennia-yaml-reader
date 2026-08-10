# Progress

Running log of milestones with links to evidence. Reverse chronological — newest first.

## 2026-08-04 (latest)

- **Packaging metadata added ahead of the first PyPI release.** `pyproject.toml` gained classifiers, keywords, `[project.urls]` (Homepage/Repository/Issues), a `dev` optional-dependencies group (`build`, `twine`), and `package-data` so the co-located [base.md](../src/evennia_yaml_reader/base.md) ships inside the wheel. Version bumped `0.0.1` → `0.1.0` for the first public release, updated consistently across `pyproject.toml`, `__init__.py`, and the smoke test's version assertion. The `license = {text = "BSD-3-Clause"}` declaration was deliberately left as-is, matching sibling libraries' `pyproject.toml` shape.

- **README rewritten to render standalone on PyPI.** The Install section now leads with `pip install evennia-yaml-reader` rather than the git-install workaround. The "Is this for me?" section reframes the library as a plumbing dependency consumed by other Evennia-ecosystem libraries — [evennia-world-builder](https://github.com/FullCircleMUD/evennia-world-builder), [evennia-mob-spawner](https://github.com/FullCircleMUD/evennia-mob-spawner) — rather than something installed directly in a gamedir, with a fallback note pointing at each repo directly if it hasn't published yet either. Every README link was converted to an absolute `github.com` URL: PyPI embeds the README standalone with no surrounding repo file tree, so relative links that work fine on GitHub 404 there.

- **Build and TestPyPI rehearsal verified end-to-end.** `python -m build` + `twine check` pass on both the sdist and wheel. Uploaded to [TestPyPI](https://test.pypi.org/project/evennia-yaml-reader/0.1.0/) and reinstalled into a clean venv (`--index-url test.pypi.org` + `--extra-index-url pypi.org`, since `pyyaml` isn't mirrored on TestPyPI) — import, `__all__` exports, and both `LocalReader`/`GitHubReader` confirmed working from the installed package, not just the dev checkout.

## 2026-05-12

- **Readers ported from `evennia-world-builder`.** `Reader`, `ReaderResult`, `GitHubReader`, `LocalReader`, and the five-class typed exception hierarchy (`ReaderError`, `ReaderAuthError`, `ReaderNotFoundError`, `ReaderNetworkError`, `ReaderParseError`) are in place. Flat package layout — no `readers/` subfolder; the whole library is the Reader. Consumers import directly from `evennia_yaml_reader`. **15 tests green** (1 smoke + 7 `GitHubReader` + 7 `LocalReader`) via stdlib `unittest` through `runtests.py`.

  Substantive differences from world-builder's version: no settings-based dispatch (consumer concern), no `get_reader_class()` helper (consumer concern), `_USER_AGENT` in `GitHubReader` flipped to `"evennia-yaml-reader"`. Otherwise verbatim. Co-located [base.md](../src/evennia_yaml_reader/base.md) carried over as the reference doc for `Reader` and `ReaderResult`.

  Design captured in [reader-api.md](reader-api.md) — port of world-builder's equivalent doc with the consumer-concern bits stripped out and the provenance note added.

- **Repository bootstrapped.** LIBRARY_STANDARDS scaffold in place: `pyproject.toml`, `runtests.py`, `src/evennia_yaml_reader/__init__.py` (version 0.0.1), smoke test, `CLAUDE.md`, `README.md`, `docs/INDEX.md`, `docs/progress.md`, `docs/documentation-structure.md`, `docs/archive/`. The library is pure-Python (no Evennia / Django coupling) — a deliberate divergence from LIBRARY_STANDARDS captured in CLAUDE.md principle 5.

  Decision context: the extraction was discussed and agreed because more declarative-content libraries are planned (e.g. [evennia-mob-spawner](https://github.com/FullCircleMUD/evennia-mob-spawner)), each of which would otherwise duplicate the Reader. With three or more consumers anticipated, library overhead amortises and a single source-of-truth for the Reader pattern becomes the cheaper option.
