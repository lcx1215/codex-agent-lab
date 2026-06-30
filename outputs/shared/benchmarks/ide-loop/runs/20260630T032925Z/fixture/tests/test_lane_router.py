import time
import unittest

from lane_router import parse_route_line, parse_routes, summarize_routes


class LaneRouterTest(unittest.TestCase):
    def test_groups_changed_route_and_keeps_highest_risk(self) -> None:
        records = parse_routes(
            [
                "waterflow.docs,P3,0,0.010,writer",
                "waterflow.docs,P1,1,0.020,auditor",
                "sandbox.skills,P2,0,0.030,auditor",
            ]
        )

        summaries = {summary.route: summary for summary in summarize_routes(records)}

        self.assertEqual(summaries["waterflow.docs"].total, 2)
        self.assertEqual(summaries["waterflow.docs"].changed, 1)
        self.assertEqual(summaries["waterflow.docs"].max_risk, "P1")
        self.assertEqual(summaries["waterflow.docs"].validation_mode, "boundary")
        self.assertEqual(summaries["waterflow.docs"].owners, ("auditor", "writer"))

    def test_low_risk_unchanged_route_stays_fast(self) -> None:
        records = parse_routes(
            [
                "readme,P3,0,0.010,writer",
                "readme,P3,false,0.011,writer",
            ]
        )

        summary = summarize_routes(records)[0]

        self.assertEqual(summary.max_risk, "P3")
        self.assertEqual(summary.changed, 0)
        self.assertEqual(summary.validation_mode, "fast")

    def test_large_unchanged_route_uses_sampled_mode_quickly(self) -> None:
        lines = [
            f"route-large,P3,0,0.001,worker-{index % 4}"
            for index in range(10000)
        ]

        started = time.perf_counter()
        summaries = summarize_routes(parse_routes(lines))
        elapsed = time.perf_counter() - started

        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0].total, 10000)
        self.assertEqual(summaries[0].validation_mode, "sampled")
        self.assertLess(elapsed, 1.0)

    def test_rejects_malformed_line(self) -> None:
        with self.assertRaises(ValueError):
            parse_route_line("missing,fields")


if __name__ == "__main__":
    unittest.main()
