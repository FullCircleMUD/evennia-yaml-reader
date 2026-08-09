# Interoperability

This library against every sibling library in `libraries/`. It is the lowest layer of the five: a YAML
reading abstraction over a local checkout or a remote repo. It depends only on `pyyaml`, has no Evennia
dependency at all, touches no database, and dispatches nothing off the reactor thread. It is consumed
by siblings; it consumes none of them and has no knowledge that they exist.

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
