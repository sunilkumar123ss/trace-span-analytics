"""Analyze nested spans, including overlap-aware exclusive duration."""
import argparse
import json
from pathlib import Path
import math
import sys


def union_duration(intervals):
    total, start, end = 0.0, None, None
    for left, right in sorted(intervals):
        if start is None:
            start, end = left, right
        elif left <= end:
            end = max(end, right)
        else:
            total += end - start
            start, end = left, right
    return total + (end - start if start is not None else 0)


def analyze(spans):
    if not isinstance(spans, list) or not spans:
        raise ValueError("spans must be a nonempty list")
    traces = {}
    for span in spans:
        for field in ("trace_id", "span_id", "service"):
            if not isinstance(span[field], str) or not span[field]:
                raise ValueError(f"{field} must be a nonempty string")
        if span.get("parent_id") is not None and (not isinstance(span["parent_id"], str) or not span["parent_id"]):
            raise ValueError("parent_id must be null or a nonempty string")
        if span.get("status", "ok") not in ("ok", "error"):
            raise ValueError("status must be ok or error")
        if any(type(span[key]) not in (int, float) or not math.isfinite(span[key]) for key in ("start_ms", "end_ms")):
            raise ValueError("span timestamps must be finite")
        if span["end_ms"] < span["start_ms"]:
            raise ValueError("negative span duration")
        trace = traces.setdefault(span["trace_id"], {})
        if span["span_id"] in trace:
            raise ValueError("duplicate span ID within a trace")
        trace[span["span_id"]] = span
    details, services, latencies = [], {}, []
    for trace_id, trace in traces.items():
        roots = [s for s in trace.values() if s.get("parent_id") is None]
        if len(roots) != 1:
            raise ValueError("each trace needs exactly one root")
        latencies.append(roots[0]["end_ms"] - roots[0]["start_ms"])
        children = {key: [] for key in trace}
        for span_id, span in trace.items():
            parent_id = span.get("parent_id")
            if parent_id is not None:
                if parent_id not in trace:
                    raise ValueError("missing parent span")
                parent = trace[parent_id]
                if span["start_ms"] < parent["start_ms"] or span["end_ms"] > parent["end_ms"]:
                    raise ValueError("child interval falls outside parent")
                children[parent_id].append((span["start_ms"], span["end_ms"]))
            visited, cursor = set(), span_id
            while cursor is not None:
                if cursor in visited:
                    raise ValueError("parent cycle")
                visited.add(cursor)
                if cursor not in trace:
                    raise ValueError("missing parent span")
                cursor = trace[cursor].get("parent_id")
        for span_id, span in trace.items():
            duration = span["end_ms"] - span["start_ms"]
            exclusive = duration - union_duration(children[span_id])
            details.append({"trace_id": trace_id, "span_id": span_id, "duration_ms": duration, "exclusive_ms": exclusive})
            summary = services.setdefault(span["service"], {"spans": 0, "errors": 0, "inclusive_ms": 0, "exclusive_ms": 0})
            summary["spans"] += 1
            summary["errors"] += span.get("status", "ok") == "error"
            summary["inclusive_ms"] += duration
            summary["exclusive_ms"] += exclusive
    ordered = sorted(latencies)
    return {"trace_count": len(traces), "root_latency_ms": {
        "p50_nearest_rank": ordered[math.ceil(0.5 * len(ordered)) - 1],
        "p95_nearest_rank": ordered[math.ceil(0.95 * len(ordered)) - 1]},
        "services": services, "spans": details}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        input_path = Path(args.input)
        if not input_path.is_absolute():
            input_path = Path(__file__).resolve().parent / input_path
        with input_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        print(json.dumps(analyze(data["spans"]), indent=2, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"Invalid trace data: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
