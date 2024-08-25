from src.performance_report import PerformanceReport
from src.report_generator import ReportGenerator
from src.performance_dashboard import PerformanceDashboard

def main():
    report_generator = ReportGenerator()
    dashboard = PerformanceDashboard(report_generator)
    
    performance_data = [
        PerformanceReport(student_id="12345", accuracy=95.0, time_taken=12.5, improvement=2.0),
        PerformanceReport(student_id="67890", accuracy=89.5, time_taken=15.0, improvement=1.5)
    ]
    
    dashboard.add_performance_data(performance_data)  # Ensure this method exists
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()
