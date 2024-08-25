import json
from typing import List, Dict
from src.performance_report import PerformanceReport

class ReportGenerator:
    def __init__(self, report_file="data/performance_reports.json"):
        self.report_file = report_file

    def generate_report(self, performance_data: List[PerformanceReport]):
        report_data = [report.to_dict() for report in performance_data]
        with open(self.report_file, "w") as f:
            json.dump(report_data, f, indent=4)

    def load_report(self) -> List[Dict]:
        try:
            with open(self.report_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("No previous report found. Generating new report.")
            return []
