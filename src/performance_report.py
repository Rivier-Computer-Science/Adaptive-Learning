from typing import Dict

class PerformanceReport:
    def __init__(self, student_id: str, accuracy: float, time_taken: float, improvement: float):
        self.student_id = student_id
        self.accuracy = accuracy
        self.time_taken = time_taken
        self.improvement = improvement
        # Assuming there might be a timestamp, but it's not provided here
        self.timestamp = "N/A"  # Default value or could be set when created

    def to_dict(self) -> Dict:
        return {
            'student_id': self.student_id,
            'accuracy': self.accuracy,
            'time_taken': self.time_taken,
            'improvement': self.improvement,
            'timestamp': self.timestamp
        }
