import tempfile
from pathlib import Path
import unittest

from dutpilot.config import VerifyConfig
from dutpilot.project import create_project


class ProjectTest(unittest.TestCase):
    def test_create_project_copies_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dut = root / "adder.v"
            tb = root / "tb_adder.v"
            dut.write_text("module adder; endmodule\n", encoding="utf-8")
            tb.write_text("module tb_adder; endmodule\n", encoding="utf-8")

            config = VerifyConfig(dut=dut, tb=tb, top="tb_adder", case="case1")
            layout = create_project(config, root / "runs")

            self.assertTrue((layout.src_dir / "adder.v").exists())
            self.assertTrue((layout.tb_dir / "tb_adder.v").exists())
            self.assertTrue(layout.build_dir.exists())
            self.assertTrue(layout.logs_dir.exists())
            self.assertTrue(layout.reports_dir.exists())
            self.assertTrue(layout.scripts_dir.exists())
            self.assertTrue(layout.waves_dir.exists())

    def test_rerun_clears_stale_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dut = root / "adder.v"
            tb = root / "tb_adder.v"
            dut.write_text("module adder; endmodule\n", encoding="utf-8")
            tb.write_text("module tb_adder; endmodule\n", encoding="utf-8")
            config = VerifyConfig(dut=dut, tb=tb, top="tb_adder", case="case1")

            first = create_project(config, root / "runs")
            (first.waves_dir / "wave.vcd").write_text("$date\n$end\n", encoding="utf-8")
            (first.src_dir / "stale_module.v").write_text("module stale; endmodule\n", encoding="utf-8")
            (first.reports_dir / "report.json").write_text("{}\n", encoding="utf-8")

            second = create_project(config, root / "runs")

            self.assertFalse((second.waves_dir / "wave.vcd").exists())
            self.assertFalse((second.src_dir / "stale_module.v").exists())
            self.assertFalse((second.reports_dir / "report.json").exists())
            self.assertTrue((second.src_dir / "adder.v").exists())
            self.assertTrue((second.tb_dir / "tb_adder.v").exists())


if __name__ == "__main__":
    unittest.main()
