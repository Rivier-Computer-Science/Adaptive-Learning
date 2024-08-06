import matplotlib.pyplot as plt
import io
import base64
from typing import Dict

import random

class PerformanceReport:
    def __init__(self, data: Dict):
        self.data = data

    def generate_report(self):
        report = "Performance Report\n\n"
        report += f"Accuracy: {self.data.get('accuracy', 'N/A')}\n"
        report += f"Time Taken per Question: {self.data.get('time_taken', 'N/A')}\n"
        report += f"Improvement Over Time: {self.data.get('improvement', 'N/A')}\n"
        
        chart_url = self.create_chart()
        report += f"\n![Performance Chart]({chart_url})\n"

        return report

    def create_chart(self):
        plt.figure(figsize=(10, 5))
        x = [1, 2, 3, 4, 5]  # Example dynamic data
        y = [10, 20, 25, 30, 40]  # Example dynamic data
        
        plt.plot(x, y, marker='o')
        plt.title('Student Performance Over Time')
        plt.xlabel('Time/Question')
        plt.ylabel('Performance')
        
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png')
        plt.close()
        img_stream.seek(0)
        
        img_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"


def collect_performance_data(query: str = '') -> Dict:
    # Simulate dynamic data based on the query
    data = {
        'accuracy': f"{random.randint(70, 100)}%",
        'time_taken': f"{random.randint(30, 60)} seconds per question",
        'improvement': f"{random.randint(10, 30)}% improvement over the last month"
    }
    
    # Modify data based on query if needed
    if "accuracy" in query.lower():
        data['accuracy'] = f"{random.randint(70, 100)}%"
    
    if "time" in query.lower():
        data['time_taken'] = f"{random.randint(30, 60)} seconds per question"
    
    if "improvement" in query.lower():
        data['improvement'] = f"{random.randint(10, 30)}% improvement over the last month"
    
    return data


def generate_performance_report(query: str = ''):
    data = collect_performance_data(query)
    report = PerformanceReport(data)
    return report.generate_report()
