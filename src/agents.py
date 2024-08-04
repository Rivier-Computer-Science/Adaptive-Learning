import autogen

class PerformanceReportAgent(autogen.Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_report(self, student_data):
        report = {
            'student_id': student_data['student_id'],
            'accuracy': student_data['accuracy'],
            'time_taken': student_data['time_taken'],
            'improvement': student_data['improvement'],
            'timestamp': student_data.get('timestamp', 'N/A')
        }
        return report
