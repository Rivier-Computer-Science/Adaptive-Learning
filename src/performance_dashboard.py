import matplotlib.pyplot as plt
from typing import List, Dict
from src.report_generator import ReportGenerator
from src.performance_report import PerformanceReport

class PerformanceDashboard:
    def __init__(self, report_generator: ReportGenerator):
        self.report_generator = report_generator
        self.reports = []

    def add_performance_data(self, reports: List[PerformanceReport]):
        self.reports.extend(reports)

    def display_dashboard(self):
        if not self.reports:
            print("No reports to display.")
            return
        
        print("Performance Reports Dashboard")
        for report in self.reports:
            # Access attributes using dot notation
            print(f"Student ID: {report.student_id}, Accuracy: {report.accuracy}, Time Taken: {report.time_taken}, Improvement: {report.improvement}, Timestamp: {report.timestamp}")
        
        self.generate_visualizations(self.reports)

    def generate_visualizations(self, reports: List[PerformanceReport]):
        student_ids = [report.student_id for report in reports]
        accuracies = [report.accuracy for report in reports]
        times_taken = [report.time_taken for report in reports]
        improvements = [report.improvement for report in reports]

        plt.figure(figsize=(12, 8))

        plt.subplot(3, 1, 1)
        plt.bar(student_ids, accuracies, color='blue')
        plt.xlabel('Student ID')
        plt.ylabel('Accuracy')
        plt.title('Accuracy per Student')

        plt.subplot(3, 1, 2)
        plt.bar(student_ids, times_taken, color='green')
        plt.xlabel('Student ID')
        plt.ylabel('Time Taken')
        plt.title('Time Taken per Student')

        plt.subplot(3, 1, 3)
        plt.bar(student_ids, improvements, color='red')
        plt.xlabel('Student ID')
        plt.ylabel('Improvement')
        plt.title('Improvement per Student')

        plt.tight_layout()
        plt.show()
