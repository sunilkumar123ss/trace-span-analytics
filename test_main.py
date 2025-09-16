import unittest
from main import analyze, union_duration


def span(name, parent, start, end, **kwargs):
    return dict(trace_id="t", span_id=name, parent_id=parent, start_ms=start, end_ms=end, service="demo", **kwargs)


class TraceTests(unittest.TestCase):
    def test_overlapping_children_are_not_double_subtracted(self):
        result = analyze([span("root", None, 0, 100), span("a", "root", 10, 60),
                          span("b", "root", 40, 80, status="error")])
        self.assertEqual(result["spans"][0]["exclusive_ms"], 30)
        self.assertEqual(result["services"]["demo"]["errors"], 1)
        self.assertEqual(union_duration([(0, 2), (2, 3), (5, 6)]), 4)

    def test_zero_length_and_percentile(self):
        result = analyze([span("root", None, 0, 0)])
        self.assertEqual(result["root_latency_ms"]["p95_nearest_rank"], 0)

