import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Define parameters
num_students = 10000
num_activities = 200
activity_types = ['quiz', 'homework', 'lecture']
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 6, 30)

# Function to generate random dates
def random_date(start, end):
    return start + timedelta(
        seconds=np.random.randint(0, int((end - start).total_seconds())))

# Initialize student profiles
students = [{'student_id': i, 'initial_skill': np.random.uniform(0, 1)} for i in range(num_students)]

# Generate synthetic sequences
data = []
for student in students:
    current_skill = student['initial_skill']
    student_id = student['student_id']
    date = start_date
    while date < end_date:
        activity_type = np.random.choice(activity_types)
        score = np.clip(current_skill + np.random.normal(0, 0.1), 0, 1)
        time_spent = np.random.uniform(5, 60)
        data.append({
            'student_id': student_id,
            'timestamp': date,
            'activity_type': activity_type,
            'activity_id': np.random.randint(0, num_activities),
            'outcome': score if activity_type == 'quiz' else 'completed',
            'time_spent': time_spent
        })
        date = random_date(date, end_date)
        current_skill += np.random.normal(0, 0.01)  # Simulate learning over time

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('data/synthetic_student_data.csv', index=False)
