# Trace span analytics

> **Disclosed reconstruction prepared on 24 October 2026.** The recorded Git dates are synthetic, not dates of past development. See [HISTORY.md](HISTORY.md).

This is an incomplete stage in a tutorial reconstruction of an already-completed reference implementation. Source, fixtures, tests, command-line behavior and verification are introduced in later stages. Only the final branch tip contains the complete documented package.

## Intended scope of the final example

Validate nested trace spans and compute root latency percentiles, service error counts and exclusive durations without double-subtracting overlapping child spans.

All examples are synthetic and educational. This reconstruction does not establish historical employment, deployment, usage, or production benchmarks.
