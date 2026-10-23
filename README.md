# Trace span analytics

Inspect synthetic or exported nested trace spans without a telemetry backend. Computes root latency percentiles, error counts, service duration aggregates, and each span's exclusive time.

~~~sh
python3 main.py --input example.json
python3 -m unittest -v
~~~

Exclusive time subtracts the union of immediate-child intervals, so overlapping children are not subtracted twice. Traces require one root, unique span IDs, resolvable parents, no cycles, and child intervals contained in their parents. Cross-trace parent links and distributed clock skew are unsupported.

Percentiles use nearest rank. Service inclusive totals may double-count nested/parallel work and are not elapsed request latency or CPU utilization. No OpenTelemetry collector, tracing SDK, model call, or production latency benchmark is included.

## Scope

This is an educational implementation with synthetic fixtures. Run the tests and inspect the documented limits before adapting it.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
