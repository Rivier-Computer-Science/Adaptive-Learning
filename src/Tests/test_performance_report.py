import unittest
from datetime import datetime
from src.performance_report import PerformanceReport

class TestPerformanceReport(unittest.TestCase):
    def test_to_dict(self):
        report = PerformanceReport("12345", 95.0, 12.5, 2.0)
        report_dict = report.to_dict()
        self.assertEqual(report_dict["student_id"], "12345")
        self.assertEqual(report_dict["accuracy"], 95.0)
        self.assertEqual(report_dict["time_taken"], 12.5)
        self.assertEqual(report_dict["improvement"], 2.0)
        self.assertTrue(isinstance(report_dict["timestamp"], str))

if __name__ == "__main__":
    unittest.main()
