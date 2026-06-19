# CLAUDE.md

> **Project-wide working rules and cross-repo context live in the FCM umbrella repo's `CLAUDE.md`**,
> loaded automatically when you work from the umbrella root. If you opened this repo directly instead
> of via the umbrella, relaunch from the umbrella root for the full context. This file holds only this
> repo's specific instructions.

Instructions for Claude (and other LLM agents) working in this repository.

## What this project is

`evennia-yaml-reader` is a library that provides a source-agnostic YAML file reader for declarative-content libraries in the [Evennia](https://www.evennia.com/) ecosystem. The `Reader` interface abstracts *where the YAML lives* — local filesystem, GitHub repo, future sources — so consuming libraries (and their consumer games) can swap backends via settings without touching call sites. Tagline: **"Source-agnostic YAML reader for the Evennia ecosystem."**

The library is Evennia-flavored by intended audience but is **not coupled to Evennia at runtime**: it has no Evennia or Django dependencies. It is a small, focused primitive that other Evennia-ecosystem libraries (e.g. [evennia-world-builder](https://github.com/FullCircleMUD/evennia-world-builder), [evennia-mob-spawner](https://github.com/FullCircleMUD/evennia-mob-spawner)) depend on.

For the big-picture overview, read [README.md](README.md).
For the design wiki, read [docs/INDEX.md](docs/INDEX.md).

## Project status

For the current state of the project — milestones reached, what's pending — see [docs/progress.md](docs/progress.md), the running log of milestones with links to evidence.

The library is being extracted from `evennia-world-builder`, where the Reader pattern was first proven. The original implementations live (today) at [src/evennia_world_builder/readers/](https://github.com/FullCircleMUD/evennia-world-builder/tree/main/src/evennia_world_builder/readers) and serve as the substrate for this library's initial code drop.

## Where to read first

For any non-trivial task, start by reading in this order:

1. [README.md](README.md) — what the project is, status, quick start.
2. [docs/INDEX.md](docs/INDEX.md) — map of all design docs.
## Load-bearing architectural principles

These are the principles every implementation decision must respect. Getting them wrong is expensive to undo.

1. **The library does not own game concepts.** Worlds, mobs, quests, rooms, NPCs — none of these belong to this library. The Reader reads YAML files. What's *in* the YAML, and what the consumer does with the parsed structure, is the consumer's concern. When tempted to interpret content, ask whether that interpretation actually belongs to the consuming library instead.
2. **No FCM-specific assumptions.** This library was extracted from infrastructure that originated in service of FullCircleMUD (FCM). Anything FCM-specific creeping into the library is a code smell. Repo paths, file-naming conventions, tag systems, identity schemes — all belong to whichever consuming library uses them. Default to "consumer concern" when uncertain.
3. **Source-agnostic core.** The base `Reader` interface is the contract. Adding a new backend implementation (S3, GitLab, an HTTP endpoint, a database, a packaged bundle) must not require changes to the interface, the consumer's call sites, or the settings-dispatch convention. The library is `Reader` plus a small set of concrete implementations that all honour the same contract.
4. **Typed errors, never silent defaults.** Every failure mode raises a specific exception (`ReaderNotFoundError`, `ReaderAuthError`, `ReaderNetworkError`, `ReaderParseError`). Consumers dispatch on type. The library never returns `None`, an empty string, or a sentinel object to indicate failure — those patterns hide bugs.
5. **No Evennia or Django coupling — deliberate divergence from the library standards.** This library is upstream of any Evennia integration. Pulling Evennia into the dependency graph here would slow tests, pull in a large transitive footprint, and make the library less reusable for non-Evennia contexts. Tests use pure stdlib `unittest` via `runtests.py`. The "evennia-" prefix is for ecosystem discoverability, not coupling.
6. **Synthetic content first.** Build the library against synthetic test fixtures the library owns (fixture YAML files in the test tree, fake HTTP responses, simulated filesystem layouts), exhaustively, before any consumer-library integration. Real consumer content surfaces edge cases synthetic fixtures didn't reach; when it does, pause integration, capture the case as a new synthetic fixture, fix against it, resume. Fixtures stay forever as regression coverage.

## Out of scope

Scope boundaries are decided as concrete questions arise, by applying the principles above. The library's surface area will be drawn deliberately as actual design needs surface, with each scope decision captured in docs/ when it is made.

Areas where scope questions are likely to need explicit decisions (TBD when they arrive):

- Whether the Reader returns bytes-and-parsed (today's shape) or only bytes (consumer parses) or only parsed (consumer never sees bytes). The current `ReaderResult(raw_bytes, parsed)` is a starting point inherited from world-builder.
- Caching semantics: per-Reader instance, per-process, none, configurable.
- Retry / backoff for transient network failures in remote Readers.
- Whether to ship additional Reader implementations beyond `LocalReader` and `GitHubReader` (S3, GitLab, gitea, …) or leave that to consumers.
- Async Reader variant (asyncio-friendly `aread()`) — out of scope until a real consumer needs it.

## Working conventions

- **Editing design docs.** Update or add design documents whenever an architectural decision is made or refined. Capture the *why*, not just the *what*. Index new docs in [docs/INDEX.md](docs/INDEX.md).
- **Don't put implementation detail in this file or README.** Link out to docs/ instead. Keep CLAUDE.md and README.md stable; let docs/ churn.
- **License.** BSD 3-Clause. Source files carry an SPDX header on the first line (`# SPDX-License-Identifier: BSD-3-Clause`).

## Documentation discipline (load-bearing)

Design documents in `docs/` must reflect decisions **actually discussed and agreed on with the project owner**. They are not a place to forward-design the system from first principles or extrapolate "reasonable defaults" from a starting point.

**Rules:**

1. **Only capture what was discussed and agreed.** If the conversation establishes a principle (e.g. "the Reader is source-agnostic"), do not extrapolate it into specifics that were not raised (e.g. a specific Reader implementation list, a chosen caching policy, retry semantics).
2. **Flag open questions explicitly.** Where a topic has been raised but not resolved, write `[TBD — needs discussion: <what is open>]` in the doc. Future sessions then pick the topic up deliberately rather than inheriting unagreed assumptions.
3. **Distinguish archived material from in-conversation decisions.** Material in `docs/archive/` is preserved historical context, not authoritative. Restating archived content in new docs is acceptable when it provides necessary context, but mark it as such rather than presenting it as a decision freshly made or as canonical project intent.
4. **Smaller is better.** A doc that captures three discussed points faithfully is more useful than one that captures three discussed points plus seven invented ones. Resist the urge to fill out sections "for completeness."

If a session catches itself writing content that goes beyond what was discussed, stop and either remove the extrapolation or convert it to a `[TBD]` marker. Documentation that puts unagreed decisions in the project's mouth is worse than documentation that has gaps.

## Repository layout

```
evennia-yaml-reader/
├── CLAUDE.md                  # this file
├── README.md
├── LICENSE                    # BSD 3-Clause
├── pyproject.toml
├── runtests.py                # standalone test runner (pure stdlib unittest)
├── .gitignore
├── docs/                    # technical wiki (humans + LLMs)
│   ├── INDEX.md
│   ├── progress.md
│   └── archive/               # historical context (currently empty)
└── src/
    └── evennia_yaml_reader/   # library code (src layout)
        ├── __init__.py
        └── tests.py           # unit tests, run via runtests.py
```

Note: no `tests/` infrastructure folder (no Django settings, no Evennia bootstrap) and no `examples/` (no demo gamedirs needed for a pure-Python primitive). These are deliberate divergences from the library standards, justified by the pure-Python framing — see principle 5.

## Tools and environment

- Python 3.10+ (pinned via `pyproject.toml`).
- Runtime dependencies: `pyyaml` only. **No Evennia, no Django** — see principle 5.
- **Tests use pure stdlib `unittest` via `runtests.py`** — deliberate divergence from sibling libraries that bootstrap Django for Evennia testing. The Reader has no Evennia dependency, so the Django bootstrap is unnecessary overhead.
- Dedicated venv at `evennia-yaml-reader/venv/` (gitignored). Development install via `pip install -e .`.

## Sibling libraries to reference

When in doubt about a convention not covered here, look at how a sibling library does it:

- **[../evennia-world-builder/](../evennia-world-builder/)** — the library this code is being extracted from. Reference for the Reader pattern's first proven implementation.- **[../evennia-shards/](../evennia-shards/)** — full Evennia-bootstrapped library with Django test settings. Reference for what *not* to do here (since this library doesn't need that machinery), but a useful sanity check against drifting too far from the standard.