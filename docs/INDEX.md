# DESIGN Index

Map of all design documents in this directory, organised by category. Add new documents here when they land — un-indexed documents are invisible.

## Process and discipline

- **[documentation-structure.md](documentation-structure.md)** — what goes in CLAUDE.md vs README.md vs docs/, conventions for new design documents.
- **[progress.md](progress.md)** — running log of milestones with links to evidence.

## Architecture and design

- **[reader-api.md](reader-api.md)** — the load-bearing `Reader` contract: configured connection + per-read `path`, `ReaderResult` shape, typed exceptions, `required_kwargs` discoverability. Captures the decisions behind the contract and points at the co-located reference at [../src/evennia_yaml_reader/base.md](../src/evennia_yaml_reader/base.md).

## Co-located reference docs

These live alongside the source code rather than in `docs/`. They are detailed reference for the code they sit next to — kept co-located so the docs and code move together. Linked here for discoverability.

- **[../src/evennia_yaml_reader/base.md](../src/evennia_yaml_reader/base.md)** — `Reader` and `ReaderResult` reference: signatures, algorithm, class attributes, error contract, design notes per field.

## Archive

Historical context, not authoritative. Material in `archive/` is preserved per the "don't delete; supersede" principle.

*(The archive is currently empty. If substrate material later emerges — e.g. design notes carried over from the world-builder extraction, or brainstorming captured before a decision crystallised — it lands here.)*
