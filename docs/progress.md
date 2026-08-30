# Progress

Running log of milestones with links to evidence. Reverse chronological — newest first.

## 2026-08-30 (latest)

- **[test-plan.md](test-plan.md) added — the library now meets the test-first standard.** Every case the suite commits to covering is listed with the test function covering it, across four prefixes: `PK` (package surface), `RD` (the `Reader`/`ReaderResult` contract), `GH` (`GitHubReader`) and `LR` (`LocalReader`). Written to the [evennia-targeting](../../evennia-targeting/docs/test-plan.md) reference shape, with the fixtures table and a **Settled** section recording this round's decisions. No open `[TBD]`. `library-standards-linter` validates the coverage trail in both directions and passes.

- **Recording the existing tests exposed the gaps; the gaps are now closed.** Cases added for undecodable bytes, empty documents, the absolute-path and symlink routes past `LocalReader`'s root guard, permission-denied and directory paths, `ReaderResult` immutability, and the error hierarchy. Most pinned behaviour that was already correct but unproven — in particular the root guard, which can no longer be removed without a test going red.

- **Two `GitHubReader` defects found and fixed** ([commit](https://github.com/FullCircleMUD/evennia-yaml-reader/commit/1ba4622)). HTTP 403 was classified as a network failure whether the cause was an exhausted rate limit or a PAT lacking scope; only the first is retryable, so the two now raise `ReaderNetworkError` and `ReaderAuthError` respectively, and a consumer answers "can retrying help?" from the exception type rather than by matching a message string. Separately, the path was interpolated into the request URL unescaped — a `#` in a filename turned the remainder into a URL fragment that is never sent, taking `ref=` with it, so the read silently answered from the repo's default branch. `path` is now percent-encoded with `/` left safe, and [base.md](../src/evennia_yaml_reader/base.md) records the contract: `path` is always a plain path, never pre-encoded, because the same string is handed to `LocalReader` and opened literally.

- **[interoperability.md](interoperability.md) completed across all nine libraries.** `ai-memory`, `llm-service` and `message-bus` had no section; `archive` carried a placeholder. The opening paragraph now carries the clearance in full — no models, no database, no registration at server start, no state between calls, no dispatch of its own — so a sibling has nothing to catch on. `ai-memory` and `llm-service` are stated as uncoupled today with the open question left where it is owned, both being `[TBD]` on their own side.

- **[CLAUDE.md](../CLAUDE.md) brought back in line with the repo.** Layout tree, project status, reading order, and the test-first working convention.

## 2026-08-04

- **Packaging metadata added ahead of the first PyPI release.** `pyproject.toml` gained classifiers, keywords, `[project.urls]` (Homepage/Repository/Issues), a `dev` optional-dependencies group (`build`, `twine`), and `package-data` so the co-located [base.md](../src/evennia_yaml_reader/base.md) ships inside the wheel. Version bumped `0.0.1` → `0.1.0` for the first public release, updated consistently across `pyproject.toml`, `__init__.py`, and the smoke test's version assertion. The `license = {text = "BSD-3-Clause"}` declaration was deliberately left as-is, matching sibling libraries' `pyproject.toml` shape.

- **README rewritten to render standalone on PyPI.** The Install section now leads with `pip install evennia-yaml-reader` rather than the git-install workaround. The "Is this for me?" section reframes the library as a plumbing dependency consumed by other Evennia-ecosystem libraries — [evennia-world-builder](https://github.com/FullCircleMUD/evennia-world-builder), [evennia-mob-spawner](https://github.com/FullCircleMUD/evennia-mob-spawner) — rather than something installed directly in a gamedir, with a fallback note pointing at each repo directly if it hasn't published yet either. Every README link was converted to an absolute `github.com` URL: PyPI embeds the README standalone with no surrounding repo file tree, so relative links that work fine on GitHub 404 there.

- **Build and TestPyPI rehearsal verified end-to-end.** `python -m build` + `twine check` pass on both the sdist and wheel. Uploaded to [TestPyPI](https://test.pypi.org/project/evennia-yaml-reader/0.1.0/) and reinstalled into a clean venv (`--index-url test.pypi.org` + `--extra-index-url pypi.org`, since `pyyaml` isn't mirrored on TestPyPI) — import, `__all__` exports, and both `LocalReader`/`GitHubReader` confirmed working from the installed package, not just the dev checkout.

## 2026-05-12

- **Readers ported from `evennia-world-builder`.** `Reader`, `ReaderResult`, `GitHubReader`, `LocalReader`, and the five-class typed exception hierarchy (`ReaderError`, `ReaderAuthError`, `ReaderNotFoundError`, `ReaderNetworkError`, `ReaderParseError`) are in place. Flat package layout — no `readers/` subfolder; the whole library is the Reader. Consumers import directly from `evennia_yaml_reader`. **15 tests green** (1 smoke + 7 `GitHubReader` + 7 `LocalReader`) via stdlib `unittest` through `runtests.py`.

  Substantive differences from world-builder's version: no settings-based dispatch (consumer concern), no `get_reader_class()` helper (consumer concern), `_USER_AGENT` in `GitHubReader` flipped to `"evennia-yaml-reader"`. Otherwise verbatim. Co-located [base.md](../src/evennia_yaml_reader/base.md) carried over as the reference doc for `Reader` and `ReaderResult`.

  Design captured in [reader-api.md](reader-api.md) — port of world-builder's equivalent doc with the consumer-concern bits stripped out and the provenance note added.

- **Repository bootstrapped.** LIBRARY_STANDARDS scaffold in place: `pyproject.toml`, `runtests.py`, `src/evennia_yaml_reader/__init__.py` (version 0.0.1), smoke test, `CLAUDE.md`, `README.md`, `docs/INDEX.md`, `docs/progress.md`, `docs/documentation-structure.md`, `docs/archive/`. The library is pure-Python (no Evennia / Django coupling) — a deliberate divergence from LIBRARY_STANDARDS captured in CLAUDE.md principle 5.

  Decision context: the extraction was discussed and agreed because more declarative-content libraries are planned (e.g. [evennia-mob-spawner](https://github.com/FullCircleMUD/evennia-mob-spawner)), each of which would otherwise duplicate the Reader. With three or more consumers anticipated, library overhead amortises and a single source-of-truth for the Reader pattern becomes the cheaper option.
