from pathlib import Path
import tempfile
import unittest
from aero_workflow.analysis import OperatingPoint, PolarPoint, analyze, grid_convergence_index, load_polar

class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.polar = [PolarPoint(0.0,0.0,0.02,-0.01), PolarPoint(5.0,0.5,0.03,-0.02), PolarPoint(10.0,1.0,0.06,-0.04)]
    def test_analysis_balances_lift_and_weight(self):
        report = analyze(OperatingPoint(25.0,0.3,8.0,0.8), self.polar)
        self.assertAlmostEqual(report["lift_balance_error_percent"],0.0,places=10)
        self.assertGreater(report["reynolds_number"],400_000)
    def test_rejects_operating_point_outside_polar(self):
        with self.assertRaisesRegex(ValueError,"outside polar range"):
            analyze(OperatingPoint(8.0,0.3,20.0,0.4), self.polar)
    def test_grid_convergence(self):
        result=grid_convergence_index(0.0392,0.0376,0.0372)
        self.assertAlmostEqual(result["observed_order"],2.0,places=8)
        self.assertLess(result["fine_gci_percent"],0.5)
    def test_polar_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"bad.csv"
            path.write_text("alpha_deg,cl,cd,cm\n0,0.2,-0.01,0\n2,0.4,0.02,0\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"CD"):
                load_polar(path)

if __name__ == "__main__": unittest.main()
