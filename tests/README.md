# tests/

Intentionally a placeholder. `evennia-yaml-reader` is a pure-Python library with no Evennia or Django
coupling — a deliberate divergence from the library standards (see `CLAUDE.md` principle 5). It therefore
does **not** use the Django test-runner infrastructure (`tests/test_settings.py`, `tests/urls.py`) that
the standard otherwise expects here.

Its tests live inside the package (`src/evennia_yaml_reader/tests.py`) and run via `runtests.py` with
stdlib `unittest`. This folder is kept so the repo's structure stays uniform with its sibling libraries.
