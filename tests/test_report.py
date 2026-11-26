import tempfile
from pathlib import Path
import unittest
import json

from dutpilot.report import build_report, write_report, write_summary


class ReportTest(unittest.TestCase):
    def test_report_contains_required_fields(self):
        report = build_report(
            case="adder",
            simulator="icarus",
            status="pass",
            stage="simulate",
            top="tb_adder",
            commands={"compile": "iverilog", "simulate": "vvp"},
            artifacts={"report_json": "reports/report.json", "wave": "dutpilot_runs/adder/waves/wave.vcd"},
            markers={"pass": ["DUTPILOT_PASS"], "fail": []},
            errors=[],
            warnings=[],
            return_codes={"compile": 0, "simulate": 0},
        )
        for key in (
            "schema_version",
            "case",
            "simulator",
            "status",
            "stage",
            "primary_error",
            "next_action_hint",
            "top",
            "commands",
            "artifacts",
            "markers",
            "errors",
            "warnings",
            "return_codes",
        ):
            self.assertIn(key, report)

    def test_write_report_and_summary(self):
        report = build_report(
            case="adder",
            simulator="icarus",
            status="pass",
            stage="simulate",
            top="tb_adder",
            commands={"compile": "iverilog", "simulate": "vvp"},
            artifacts={"report_json": "reports/report.json", "wave": "dutpilot_runs/adder/waves/wave.vcd"},
            markers={"pass": ["DUTPILOT_PASS"], "fail": []},
            errors=[],
            warnings=[],
            return_codes={"compile": 0, "simulate": 0},
        )
        with tempfile.TemporaryDirectory() as tmp:
            reports_dir = Path(tmp)
            report_path = write_report(report, reports_dir)
            summary_path = write_summary(report, reports_dir)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "pass")
            self.assertIn("DUTPilot Summary", summary_path.read_text(encoding="utf-8"))


    def test_schema_version_matches_package_version(self):
        import dutpilot
        from dutpilot import report as report_module

        self.assertEqual(report_module.SCHEMA_VERSION, dutpilot.__version__)

    def test_summary_includes_primary_error_and_hint(self):
        report = build_report(
            case="adder",
            simulator="icarus",
            status="fail",
            stage="simulate",
            top="tb_adder",
            commands={"compile": "iverilog", "simulate": "vvp"},
            artifacts={"report_json": "reports/report.json"},
            markers={"pass": [], "fail": ["DUTPILOT_FAIL: expected 5, got 4"]},
            errors=[],
            warnings=[],
            return_codes={"compile": 0, "simulate": 0},
            primary_error="DUTPILOT_FAIL: expected 5, got 4",
            next_action_hint="Inspect the testbench failure marker.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            summary = write_summary(report, Path(tmp)).read_text(encoding="utf-8")
            self.assertIn("DUTPILOT_FAIL: expected 5, got 4", summary)
            self.assertIn("Inspect the testbench failure marker.", summary)


if __name__ == "__main__":
    unittest.main()
