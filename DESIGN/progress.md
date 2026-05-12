# Progress

Running log of milestones with links to evidence. Reverse chronological — newest first.

## 2026-05-12 (latest)

- **Repository bootstrapped.** LIBRARY_STANDARDS scaffold in place: `pyproject.toml`, `runtests.py`, `src/evennia_yaml_reader/__init__.py` (version 0.0.1), smoke test, `CLAUDE.md`, `README.md`, `DESIGN/INDEX.md`, `DESIGN/progress.md`, `DESIGN/documentation-structure.md`, `DESIGN/archive/`. The library is pure-Python (no Evennia / Django coupling) — a deliberate divergence from LIBRARY_STANDARDS captured in CLAUDE.md principle 5.

  Substrate: the Reader pattern was first proven inside [evennia-world-builder](https://github.com/FullCircleMUD/evennia-world-builder), where it now ships as `src/evennia_world_builder/readers/` (191 lines across `base.py`, `local.py`, `github.py`, `__init__.py`). Extraction into this library is the next milestone.

  Decision context: the extraction was discussed and agreed because more declarative-content libraries are planned (e.g. [evennia-mob-spawner](https://github.com/FullCircleMUD/evennia-mob-spawner)), each of which would otherwise duplicate the Reader. With three or more consumers anticipated, library overhead amortises and a single source-of-truth for the Reader pattern becomes the cheaper option.
