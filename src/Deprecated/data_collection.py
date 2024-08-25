from src.agents import PerformanceReportAgent

class DataCollectionModule:
    def __init__(self):
        self.agent = PerformanceReportAgent()
        self.data = []

    def collect_data(self, student_id, accuracy, time_taken, improvement):
        student_data = {
            'student_id': student_id,
            'accuracy': accuracy,
            'time_taken': time_taken,
            'improvement': improvement
        }
        report = self.agent.generate_report(student_data)
        self.data.append(report)

    def get_reports(self):
        return self.data
