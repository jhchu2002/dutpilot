import unittest

from dutpilot.log_parser import parse_logs


class LogParserTest(unittest.TestCase):
    def test_pass_and_warning_markers(self):
        parsed = parse_logs("warning: minor\nDUTPILOT_PASS\n")
        self.assertEqual(parsed.markers["pass"], ["DUTPILOT_PASS"])
        self.assertEqual(parsed.markers["fail"], [])
        self.assertEqual(parsed.errors, [])
        self.assertEqual(parsed.warnings, ["warning: minor"])

    def test_fail_and_errors(self):
        parsed = parse_logs("DUTPILOT_FAIL: bad sum\nsyntax error\nFatal: stop\n")
        self.assertEqual(parsed.markers["fail"], ["DUTPILOT_FAIL: bad sum"])
        self.assertEqual(len(parsed.errors), 2)

    def test_zero_error_count_is_not_an_error(self):
        parsed = parse_logs("checks: 12, errors: 0\nDUTPILOT_PASS\n")
        self.assertEqual(parsed.errors, [])
        self.assertEqual(parsed.markers["pass"], ["DUTPILOT_PASS"])

    def test_zero_error_count_prefix_form(self):
        parsed = parse_logs("0 errors, 0 warnings\nDUTPILOT_PASS\n")
        self.assertEqual(parsed.errors, [])
        self.assertEqual(parsed.warnings, [])

    def test_no_warning_count_is_not_a_warning(self):
        parsed = parse_logs("warnings: 0\nDUTPILOT_PASS\n")
        self.assertEqual(parsed.warnings, [])

    def test_marker_lines_are_not_counted_as_diagnostics(self):
        parsed = parse_logs("DUTPILOT_FAIL: error while comparing sum\n")
        self.assertEqual(parsed.markers["fail"], ["DUTPILOT_FAIL: error while comparing sum"])
        self.assertEqual(parsed.errors, [])

    def test_real_error_after_marker_still_reported(self):
        parsed = parse_logs("DUTPILOT_PASS\nerror: wave.vcd could not be written\n")
        self.assertEqual(parsed.markers["pass"], ["DUTPILOT_PASS"])
        self.assertEqual(parsed.errors, ["error: wave.vcd could not be written"])


if __name__ == "__main__":
    unittest.main()
