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

