import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("summarize_loading", Path(__file__).parents[1] / "tools/summarize_loading.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LoadingMetricsTests(unittest.TestCase):
    def test_completed_loads_only_and_no_overlapping_phase_sums(self):
        text = """* [load-session] begin scenario=transition
* [load-session] cancelled scenario=transition after 400 ms (disconnect)
* [load-session] phases: teardown=20 ms, server/lua=50 ms
* [load-session] engine ready scenario=transition: 1200 ms
* [load-session] engine ready scenario=quickload: 700 ms
"""
        self.assertEqual(list(module.samples(text)), [
            ("engine-ready", "transition", 1200.0), ("engine-ready", "quickload", 700.0)])

    def test_medians_preserve_scenario_and_build(self):
        rows = module.summarize([
            ("baseline", "[load-session] engine ready scenario=quickload: 400 ms"),
            ("baseline", "[load-session] engine ready scenario=quickload: 100 ms"),
            ("baseline", "[load-session] engine ready scenario=quickload: 200 ms"),
            ("candidate", "[load-session] engine ready scenario=quickload: 50 ms"),
        ])
        self.assertEqual(rows[0], ("baseline", "engine-ready", "quickload", 3, 200.0, 100.0, 400.0))
        self.assertEqual(rows[1][0], "candidate")

    def test_units_and_partial_metrics_stay_separate(self):
        result = list(module.samples("""Init FileSystem 23.384899 sec
[STARTUP] total to main menu: 30000 ms
total loading time: 800 ms
[LOADDIAG] startup-total_ms=5000
[LOADDIAG] startup-total_ms=%u
"""))
        self.assertAlmostEqual(result[0][2], 23384.899)
        self.assertEqual([row[0] for row in result], [
            "filesystem-init", "startup-to-menu", "legacy-partial-load", "lua-startup"])


if __name__ == "__main__":
    unittest.main()
