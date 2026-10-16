#!/usr/bin/env python3
"""Summarize comparable loading metrics without adding overlapping phases."""
import argparse
import csv
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

PATTERNS = (
    ("engine-ready", re.compile(r"\[load-session\] engine ready scenario=([^:]+):\s*(\d+) ms")),
    ("startup-to-menu", re.compile(r"\[STARTUP\] total to main menu:\s*(\d+) ms")),
    ("filesystem-init", re.compile(r"Init FileSystem\s+(\d+(?:\.\d+)?) sec")),
    ("lua-startup", re.compile(r"\[LOADDIAG\] startup-total_ms=(\d+)")),
    ("legacy-partial-load", re.compile(r"total loading time\s*[:=]\s*(\d+)\s*ms", re.I)),
)


def samples(text):
    for line in text.splitlines():
        for metric, pattern in PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            if metric == "engine-ready":
                yield metric, match[1], float(match[2])
            else:
                value = float(match[1]) * (1000 if metric == "filesystem-init" else 1)
                yield metric, "unspecified", value
            break


def summarize(inputs):
    groups = defaultdict(list)
    for label, text in inputs:
        for metric, scenario, milliseconds in samples(text):
            groups[label, metric, scenario].append(milliseconds)
    return [
        (label, metric, scenario, len(values), statistics.median(values), min(values), max(values))
        for (label, metric, scenario), values in sorted(groups.items())
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", metavar="LABEL=LOG_PATH",
                        help="Use the same label for repeated runs of one build/setup.")
    args = parser.parse_args()
    inputs = []
    for item in args.logs:
        label, sep, path = item.partition("=")
        if not sep or not label or not path:
            parser.error("Each argument must be LABEL=LOG_PATH")
        try:
            inputs.append((label, Path(path).read_text(encoding="utf-8", errors="replace")))
        except OSError as error:
            parser.error(str(error))
    rows = summarize(inputs)
    if not rows:
        parser.exit(1, "No supported completed timing metrics found.\n")
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["build", "metric", "scenario", "samples", "median_ms", "min_ms", "max_ms"])
    for label, metric, scenario, count, median, low, high in rows:
        writer.writerow([label, metric, scenario, count, f"{median:.2f}", f"{low:.2f}", f"{high:.2f}"])


if __name__ == "__main__":
    main()
