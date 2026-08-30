# Interoperability

This library against every sibling library in `libraries/`. It is the lowest layer: a YAML reading
abstraction over a local checkout or a remote repo. It depends only on `pyyaml`, has no Evennia
dependency at all, defines no models and touches no database, registers nothing at server start, holds
no state between calls, and runs wholly inline on whichever thread called it — it dispatches nothing of
its own. It is consumed by siblings; it consumes none of them and has no knowledge that they exist.

That is the whole clearance, and it is why the sections below are short. A sibling can only be
constrained by what a library *does* — a query it issues, a row it writes, a thread it dispatches to, a
hook it registers. This library does none of those things, so there is nothing for a sibling to catch
on and nothing it needs a sibling to do. The one consideration worth stating is about the *caller's*
thread rather than this library's work, and it is recorded under `evennia-shards` below.

Sections appear for every sibling, in alphabetical order, so this file can be read side by side with
the others and a missing consideration shows up as a gap.

## evennia-ai-memory

**No coupling today** — neither library imports the other. Whether that changes is ai-memory's
question, not this library's: it becomes a consumer if the lore YAML importer lands there, and stays
uncoupled if the importer sits in the lore content repo. The decision is owned and marked `[TBD]` in
[its `interoperability.md`](../../evennia-ai-memory/docs/interoperability.md).

Either outcome is free for this library. Being consumed imposes nothing beyond the API contract in
[reader-api.md](reader-api.md).

## evennia-archive

**No coupling.** Neither library imports the other. Archive's second database alias and its off-reactor
copy job cannot reach a library that issues no query, writes no row and dispatches nothing.

Archive states the same clearance from its side, in
[its `interoperability.md`](../../evennia-archive/docs/interoperability.md).

## evennia-llm-service

**No coupling today** — neither library imports the other. As with ai-memory, whether that changes is
llm-service's question: it depends on the format its prompt templates are loaded from, and is marked
`[TBD]` in [its `interoperability.md`](../../evennia-llm-service/docs/interoperability.md).

## evennia-message-bus

**No coupling.** Neither library imports the other. Message payloads are built by consumer code and
stored as structured data on a message row; nothing in message-bus parses YAML, and nothing here
touches its tables.

## evennia-mob-spawner

**Hard dependency, in the other direction.** mob-spawner imports this library unconditionally and is
the only side that knows about the relationship. This library imposes nothing on it beyond its own
API contract — see [reader-api.md](reader-api.md).

## evennia-shards

**No coupling.** Neither library imports the other. Because this library performs no database access
of any kind and requires no Evennia runtime, nothing it does is visible to the tenancy layer — there
is no query to scope and no row to stamp.

The one thing worth knowing is where its work happens: consumers typically call it from inside a worker
thread as part of a larger pipeline, and it is that consumer's dispatch site that must carry
shards' `preserve_tenant_context` wrap. The requirement belongs to whichever library owns the dispatch,
not to this one.

## evennia-targeting

**No coupling.** Neither library imports the other. Targeting reads no files and has no configuration
in YAML.

## evennia-world-builder

**Hard dependency, in the other direction.** world-builder imports this library unconditionally and is
the only side that knows about the relationship. This library imposes nothing on it beyond its own
API contract — see [reader-api.md](reader-api.md).

## evennia-yaml-reader

This library.
