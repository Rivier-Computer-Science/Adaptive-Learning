import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load model and validation data
model = load_model('saved_model.h5')
df = pd.read_csv('data/synthetic_student_data.csv')

# Preprocess validation data (similar to train.py)
# ...

# Evaluate the model
y_pred = model.predict(X_val)
y_pred = (y_pred > 0.5).astype(int)

accuracy = accuracy_score(y_val, y_pred)
precision = precision_score(y_val, y_pred)
recall = recall_score(y_val, y_pred)
f1 = f1_score(y_val, y_pred)

print(f'Accuracy: {accuracy}')
print(f'Precision: {precision}')
print(f'Recall: {recall}')
print(f'F1 Score: {f1}')
