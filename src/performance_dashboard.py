import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict

class PerformanceDashboard:
    def __init__(self):
        self.reports = []

    def add_performance_data(self, reports: List[Dict]):
        self.reports.extend(reports)

    def generate_visualizations(self):
        student_ids = [report['student_id'] for report in self.reports]
        accuracies = [report['accuracy'] for report in self.reports]
        times_taken = [report['time_taken'] for report in self.reports]
        improvements = [report['improvement'] for report in self.reports]

        fig, axs = plt.subplots(3, 1, figsize=(10, 12))

        axs[0].bar(student_ids, accuracies, color='blue')
        axs[0].set_xlabel('Student ID')
        axs[0].set_ylabel('Accuracy')
        axs[0].set_title('Accuracy per Student')

        axs[1].bar(student_ids, times_taken, color='green')
        axs[1].set_xlabel('Student ID')
        axs[1].set_ylabel('Time Taken')
        axs[1].set_title('Time Taken per Student')

        axs[2].bar(student_ids, improvements, color='red')
        axs[2].set_xlabel('Student ID')
        axs[2].set_ylabel('Improvement')
        axs[2].set_title('Improvement per Student')

        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
