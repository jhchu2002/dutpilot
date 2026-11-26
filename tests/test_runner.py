import unittest

from dutpilot.runner import _next_action_hint, _primary_error


class RunnerDecisionTest(unittest.TestCase):
    def test_failure_marker_wins_over_errors(self):
        primary = _primary_error(
            ["error: something broke"],
            {"pass": [], "fail": ["DUTPILOT_FAIL: expected 5, got 4"]},
            "fail",
        )
        self.assertEqual(primary, "DUTPILOT_FAIL: expected 5, got 4")

    def test_pass_has_no_primary_error(self):
        self.assertIsNone(_primary_error([], {"pass": ["DUTPILOT_PASS"], "fail": []}, "pass"))

    def test_fail_without_marker_or_error_still_reports_reason(self):
        primary = _primary_error([], {"pass": [], "fail": []}, "fail")
        self.assertIn("DUTPILOT_PASS", primary)

    def test_hint_points_at_compile_log_for_compile_failures(self):
        self.assertIn("compile.log", _next_action_hint("fail", "compile", "syntax error"))

    def test_hint_points_at_waveform_for_other_simulation_failures(self):
        self.assertIn("wave.vcd", _next_action_hint("fail", "simulate", "timeout"))


if __name__ == "__main__":
    unittest.main()
