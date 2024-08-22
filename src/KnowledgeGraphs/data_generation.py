import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Parameters for synthetic data generation
num_students = 10000
num_activities = 200
activity_types = ['quiz', 'homework', 'lecture']
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 6, 30)

# Function to generate random dates
def random_date(start, end):
    return start + timedelta(seconds=np.random.randint(0, int((end - start).total_seconds())))

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
            'activity_type': activity_type,
            'outcome': 1 if score > 0.5 else 0,
            'time_spent': time_spent,
            'date': date
        })
        date += timedelta(days=np.random.randint(1, 5))

# Create a DataFrame
df = pd.DataFrame(data)
df.to_csv('data/synthetic_student_data.csv', index=False)
